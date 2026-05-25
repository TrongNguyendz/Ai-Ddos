from typing import Dict, Any
from loguru import logger
from datetime import datetime
from bson import ObjectId

from app.core.database import get_rules_collection, get_alerts_collection
from app.services.ip_blocker import IPBlocker
from app.services.websocket_manager import websocket_manager

ip_blocker = IPBlocker()

class RuleEngine:
    def __init__(self):
        self.blocked_ips = set()

    async def process_flow(self, flow_data: Dict[str, Any]):
        """Xử lý flow: Kiểm tra rules và thực hiện action"""
        src_ip = flow_data.get("src_ip")
        if not src_ip:
            return

        # Lấy tất cả rules đang bật
        rules_collection = await get_rules_collection()
        rules = await rules_collection.find({"enabled": True}).to_list(length=None)

        triggered_any = False

        for rule in rules:
            if self._rule_matches(rule, flow_data):
                triggered_any = True
                await self._execute_rule_action(rule, flow_data)
                # Cập nhật số lần trigger
                await self._update_trigger_count(rule["_id"])

        # Nếu AI detect malicious + không rule nào trigger → vẫn block theo AI
        if flow_data.get("label") == 1 and not triggered_any:
            await self._execute_default_action(flow_data)

    def _rule_matches(self, rule: Dict, flow_data: Dict) -> bool:
        """Kiểm tra rule có khớp với flow không - Đã sửa theo cấu trúc thực tế"""
        conditions = rule.get("conditions", {})
        if not conditions:
            return False

        try:
            # ================== KIỂM TRA PKTRATE ==================
            # Hỗ trợ cả 2 cách: pktrate_threshold hoặc pktrate
            pktrate = flow_data.get("pktrate", 0)
            
            if "pktrate_threshold" in conditions:
                threshold = conditions["pktrate_threshold"]
                if pktrate <= threshold:
                    return False
            elif "pktrate" in conditions and isinstance(conditions["pktrate"], dict):
                pktrate_cond = conditions["pktrate"]
                if "gt" in pktrate_cond and pktrate <= pktrate_cond["gt"]:
                    return False

            # ================== KIỂM TRA PROTOCOL ==================
            if "protocol" in conditions and conditions["protocol"]:
                if flow_data.get("protocol") != conditions["protocol"]:
                    return False

            # ================== CÓ THỂ MỞ RỘNG SAU ==================
            return True

        except Exception as e:
            logger.error(f"Error checking rule {rule.get('name')}: {e}")
            return False

    async def _execute_rule_action(self, rule: Dict, flow_data: Dict):
        """Thực hiện action theo rule"""
        actions = rule.get("actions", ["alert"])
        if isinstance(actions, str):
            actions = [actions]

        rule_name = rule.get("name", "Unknown Rule")

        for action in actions:
            if action == "block":
                src_ip = flow_data.get("src_ip")
                if src_ip:
                    success = ip_blocker.block_ip(src_ip, reason=f"Rule: {rule_name}")
                    if success:
                        logger.warning(f"🚫 BLOCKED by Rule '{rule_name}': {src_ip}")

            elif action == "alert":
                await self._create_alert(rule, flow_data)

            elif action == "log":
                logger.info(f"📝 LOG by Rule '{rule_name}': {flow_data.get('src_ip')}")

    async def _execute_default_action(self, flow_data: Dict):
        """Action mặc định khi AI detect malicious"""
        src_ip = flow_data.get("src_ip")
        if src_ip and flow_data.get("confidence", 0) > 0.7:
            ip_blocker.block_ip(src_ip, reason="AI Model Detection")
            # await self._create_alert(None, flow_data, is_ai=True)
            logger.warning(f"🚫 BLOCKED by AI Detection: {src_ip} | Confidence: {flow_data.get('confidence')}")

    async def _create_alert(self, rule, flow_data, is_ai=False):
        alert = {
            "title": f"Rule Triggered: {rule.get('name')}" if rule else "AI Detection Alert",
            "description": rule.get("description") if rule else "AI Model detected suspicious traffic",
            "severity": "high",
            "src_ip": flow_data.get("src_ip"),
            "pktrate": flow_data.get("pktrate"),
            "confidence": flow_data.get("confidence"),
            "timestamp": datetime.utcnow(),
            "rule_id": str(rule["_id"]) if rule else None
        }

        await get_alerts_collection().insert_one(alert)
        await websocket_manager.broadcast_alert(alert)

    async def _update_trigger_count(self, rule_id):
        rules_collection = await get_rules_collection()
        await rules_collection.update_one(
            {"_id": ObjectId(rule_id)},
            {
                "$inc": {"triggered_count": 1},
                "$set": {"last_triggered": datetime.utcnow()}
            }
        )


# Global instance
rule_engine = RuleEngine()