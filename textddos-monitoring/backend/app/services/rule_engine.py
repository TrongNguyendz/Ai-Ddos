from typing import Dict, Any
from loguru import logger
from datetime import datetime
from bson import ObjectId

from app.core.database import get_rules_collection, get_alerts_collection, get_rule_history_collection
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
                await self._update_trigger_count(rule["_id"])

        # Nếu AI detect malicious + không rule nào trigger → vẫn block theo AI
        if flow_data.get("label") == 1 and not triggered_any:
            await self._execute_default_action(flow_data)

    def _rule_matches(self, rule: Dict, flow_data: Dict) -> bool:
        """Kiểm tra rule có khớp với flow không"""
        conditions = rule.get("conditions", {})
        if not conditions:
            return False

        try:
            pktrate = flow_data.get("pktrate", 0)
            
            if "pktrate_threshold" in conditions:
                threshold = conditions["pktrate_threshold"]
                if pktrate <= threshold:
                    return False
            elif "pktrate" in conditions and isinstance(conditions["pktrate"], dict):
                pktrate_cond = conditions["pktrate"]
                if "gt" in pktrate_cond and pktrate <= pktrate_cond["gt"]:
                    return False

            if "protocol" in conditions and conditions["protocol"]:
                if flow_data.get("protocol") != conditions["protocol"]:
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking rule {rule.get('name')}: {e}")
            return False

    async def _execute_rule_action(self, rule: Dict, flow_data: Dict):
        """Thực hiện action theo rule + Lưu lịch sử"""
        actions = rule.get("actions", ["alert"])
        if isinstance(actions, str):
            actions = [actions]

        rule_name = rule.get("name", "Unknown Rule")
        rule_id = str(rule["_id"])

        for action in actions:
            if action == "block":
                src_ip = flow_data.get("src_ip")
                if src_ip:
                    success = ip_blocker.block_ip(src_ip, reason=f"Rule: {rule_name}")
                    if success:
                        logger.warning(f"🚫 BLOCKED by Rule '{rule_name}': {src_ip}")
                        await self._save_history(rule_id, rule_name, flow_data, "block")

            elif action == "alert":
                await self._create_alert(rule, flow_data)
                await self._save_history(rule_id, rule_name, flow_data, "alert")

            elif action == "log":
                logger.info(f"📝 LOG by Rule '{rule_name}': {flow_data.get('src_ip')}")
                await self._save_history(rule_id, rule_name, flow_data, "log")

    async def _execute_default_action(self, flow_data: Dict):
        """Action mặc định khi AI detect malicious"""
        src_ip = flow_data.get("src_ip")
        confidence = flow_data.get("confidence", 0)

        if not src_ip or confidence <= 0.5:
            return

        blocked_success = False

        try:
            # Thử block IP
            blocked_success = ip_blocker.block_ip(src_ip, reason="AI Model Detection")
        except Exception as e:
            logger.error(f"Lỗi block IP {src_ip}: {e}")

        try:
            # Luôn lưu alert và history dù block thất bại
            await self._create_alert(None, flow_data, is_ai=True)
            await self._save_history(None, "AI Detection", flow_data, "block_ai")
            
            if blocked_success:
                logger.warning(f"🚫 BLOCKED by AI Detection: {src_ip} | Confidence: {confidence}")
            else:
                logger.warning(f"🚫 AI DETECTED (không block được): {src_ip} | Confidence: {confidence} | Cần chạy Admin")
                
        except Exception as e:
            logger.error(f"Lỗi lưu alert/history cho AI Detection {src_ip}: {e}")

    async def _save_history(self, rule_id: str, rule_name: str, flow_data: Dict, action: str):
        """Lưu lịch sử kích hoạt rule"""
        try:
            history_collection = await get_rule_history_collection()
            
            history_entry = {
                "timestamp": datetime.utcnow(),
                "rule_id": rule_id,
                "rule_name": rule_name,
                "src_ip": flow_data.get("src_ip"),
                "pktrate": flow_data.get("pktrate"),
                "action": action,
                "confidence": flow_data.get("confidence"),
                "flow_details": {
                    "protocol": flow_data.get("protocol"),
                    "dst_ip": flow_data.get("dst_ip"),
                    "pktcount": flow_data.get("pktcount"),
                    "bytecount": flow_data.get("bytecount"),
                }
            }

            await history_collection.insert_one(history_entry)
            
        except Exception as e:
            logger.error(f"Failed to save rule history: {e}")

    async def _create_alert(self, rule, flow_data, is_ai=False):
        """Tạo alert, an toàn hơn khi rule là None"""
        try:
            if rule:
                title = f"Rule Triggered: {rule.get('name', 'Unknown')}"
                description = rule.get("description") or "Rule was triggered"
                rule_id = str(rule.get("_id"))
            else:
                title = "AI Detection Alert"
                description = "AI Model detected suspicious traffic"
                rule_id = None

            alert = {
                "title": title,
                "description": description,
                "severity": "high",
                "src_ip": flow_data.get("src_ip"),
                "pktrate": flow_data.get("pktrate"),
                "confidence": flow_data.get("confidence"),
                "timestamp": datetime.utcnow(),
                "rule_id": rule_id,
                "is_ai": is_ai ,
                "is_blocked": True if is_ai else False,  # AI alert mặc định là blocked (dù có block được hay không)
            }

            alerts_collection = await get_alerts_collection()
            result = await alerts_collection.insert_one(alert)
            
            logger.info(f"✅ Alert created successfully | ID: {result.inserted_id} | IP: {flow_data.get('src_ip')}")

            # Broadcast websocket (nếu lỗi thì catch riêng)
            try:
                await websocket_manager.broadcast_alert(alert)
            except Exception as ws_err:
                logger.warning(f"⚠️ WebSocket broadcast failed: {ws_err}")

            return alert

        except Exception as e:
            logger.error(f"Lỗi tạo Alert cho IP {flow_data.get('src_ip')}: {e}")
            # Log chi tiết hơn để debug
            logger.error(f"Alert data: rule={rule is not None}, flow_data keys={list(flow_data.keys())}")

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