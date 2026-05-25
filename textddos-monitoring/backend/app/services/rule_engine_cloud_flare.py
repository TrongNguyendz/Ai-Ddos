from typing import Dict, Any, List
import asyncio
from loguru import logger

from app.core.database import get_rules_collection, get_alerts_collection
from app.services.inference import predict_flow
from app.services.websocket_manager import websocket_manager

class RuleEngine:
    def __init__(self):
        self.rules_cache = []
        self._load_rules()

    def _load_rules(self):
        """Load rules from database (this would be async in real implementation)"""
        # This is a simplified version. In production, this should be async
        pass

    async def evaluate_rules(self, rules: List[Dict[str, Any]], flow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate rules against flow data
        Returns list of triggered alerts
        """
        triggered_alerts = []

        for rule in rules:
            if not rule.get("enabled", True):
                continue

            if self._check_conditions(rule["conditions"], flow_data):
                alert = await self._create_alert_from_rule(rule, flow_data)
                triggered_alerts.append(alert)

                # Update rule trigger count
                await self._update_rule_trigger_count(rule["_id"])

        return triggered_alerts

    def _check_conditions(self, conditions: Dict[str, Any], flow_data: Dict[str, Any]) -> bool:
        """Check if flow data matches rule conditions"""
        try:
            for field, condition in conditions.items():
                if field not in flow_data:
                    return False

                value = flow_data[field]

                if isinstance(condition, dict):
                    # Complex condition (gt, lt, eq, etc.)
                    if "gt" in condition and value <= condition["gt"]:
                        return False
                    if "lt" in condition and value >= condition["lt"]:
                        return False
                    if "eq" in condition and value != condition["eq"]:
                        return False
                    if "ne" in condition and value == condition["ne"]:
                        return False
                    if "in" in condition and value not in condition["in"]:
                        return False
                else:
                    # Simple equality check
                    if value != condition:
                        return False

            return True

        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {e}")
            return False

    async def _create_alert_from_rule(self, rule: Dict[str, Any], flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert from a triggered rule"""
        alert = {
            "title": f"Rule Triggered: {rule['name']}",
            "description": rule.get("description", "Rule conditions met"),
            "severity": self._calculate_severity(rule, flow_data),
            "src_ip": flow_data.get("src_ip"),
            "dst_ip": flow_data.get("dst_ip"),
            "protocol": flow_data.get("protocol"),
            "pktrate": flow_data.get("pktrate", 0),
            "confidence": flow_data.get("confidence", 0),
            "rule_triggered": str(rule["_id"]),
            "status": "new"
        }

        # Insert alert into database
        alerts_collection = await get_alerts_collection()
        result = await alerts_collection.insert_one(alert)
        alert["_id"] = result.inserted_id

        # Broadcast alert
        await websocket_manager.broadcast_alert(alert)

        return alert

    def _calculate_severity(self, rule: Dict[str, Any], flow_data: Dict[str, Any]) -> str:
        """Calculate alert severity based on rule and flow data"""
        pktrate = flow_data.get("pktrate", 0)
        confidence = flow_data.get("confidence", 0)

        if pktrate > 10000 or confidence > 0.95:
            return "critical"
        elif pktrate > 5000 or confidence > 0.85:
            return "high"
        elif pktrate > 1000 or confidence > 0.7:
            return "medium"
        else:
            return "low"

    async def _update_rule_trigger_count(self, rule_id):
        """Update the trigger count for a rule"""
        rules_collection = await get_rules_collection()
        from bson import ObjectId
        from datetime import datetime

        await rules_collection.update_one(
            {"_id": ObjectId(rule_id)},
            {
                "$inc": {"triggered_count": 1},
                "$set": {"last_triggered": datetime.utcnow()}
            }
        )

    async def process_flow(self, flow_data: Dict[str, Any]):
        """Process a flow through the rule engine"""
        # Get enabled rules
        rules_collection = await get_rules_collection()
        rules = await rules_collection.find({"enabled": True}).to_list(length=None)

        # Evaluate rules
        triggered_alerts = await self.evaluate_rules(rules, flow_data)

        return {
            "flow_processed": True,
            "alerts_triggered": len(triggered_alerts),
            "alerts": triggered_alerts
        }

# Global rule engine instance
rule_engine = RuleEngine()

async def evaluate_rules(rules: List[Dict[str, Any]], flow_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Convenience function to evaluate rules"""
    if flow_data:
        return await rule_engine.evaluate_rules(rules, flow_data)
    else:
        # Evaluate all rules (for manual testing)
        rules_collection = await get_rules_collection()
        all_rules = await rules_collection.find({"enabled": True}).to_list(length=None)
        return all_rules  # Return rules instead of evaluating without flow data

from app.services.cloudflare_service import cloudflare_service

class RuleEngine:
    def __init__(self):
        self.blocked_ips = set()

    async def process_flow(self, flow_data: dict):
        """
        Xử lý logic rule từ packet_sniffer hoặc inference
        """
        ip = flow_data.get("src_ip") or flow_data.get("ip")
        reason = flow_data.get("reason", "Suspicious activity")

        if not ip:
            return

        # === Logic detect của bạn ===
        if self.should_block(flow_data):
            await self.block_ip(ip, reason)

    def should_block(self, flow_data: dict) -> bool:
        # Viết rule của bạn ở đây
        # Ví dụ: brute force, nhiều SYN packet, scanning, etc.
        score = flow_data.get("threat_score", 0)
        return score >= 70   # ngưỡng tùy bạn

    async def block_ip(self, ip: str, reason: str = "Suspicious"):
        if ip in self.blocked_ips:
            return

        rule_id = await cloudflare_service.block_ip(
            ip=ip,
            duration_days=3,
            reason=reason,
            mode="managed_challenge"   # Khuyến nghị dùng managed_challenge trước
        )
        
        if rule_id:
            self.blocked_ips.add(ip)

# Singleton
rule_engine = RuleEngine()