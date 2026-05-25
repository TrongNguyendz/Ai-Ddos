import os
from datetime import datetime, timedelta
from typing import Optional
import httpx
from cloudflare import Cloudflare  # pip install cloudflare
from app.core.config import settings   # ← Import settings
class CloudflareService:
    def __init__(self):
        self.client = Cloudflare(api_token=settings.CLOUDFLARE_API_TOKEN)
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.zone_id = settings.CLOUDFLARE_ZONE_ID   # Optional nếu dùng account-level
        print(f"CloudflareService initialized with Account ID: {self.account_id}")
        # Cache rule_id để dễ quản lý (có thể dùng Redis sau)
        self.active_blocks = {}  

    async def block_ip(self, ip: str, duration_days: int = 3, reason: str = "Auto detected", mode: str = "managed_challenge"):
        try:
            notes = f"{reason} | Auto | {datetime.utcnow().isoformat()}"
            
            # Dùng httpx để async (tốt hơn)
            headers = {
                "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "configuration": {"target": "ip", "value": ip},
                "mode": mode,
                "notes": notes
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/firewall/access_rules/rules",
                    json=payload,
                    headers=headers
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    rule_id = data["result"]["id"]
                    self.active_blocks[ip] = rule_id
                    print(f"✅ Blocked {ip} | Mode: {mode}")
                    return rule_id
                else:
                    print(f"❌ API Error: {resp.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Block error: {e}")
            return None

        except Exception as e:
            print(f"❌ Cloudflare block error for {ip}: {e}")
            return None

    async def unblock_ip(self, ip: str) -> bool:
        """Gỡ block theo IP"""
        rule_id = self.active_blocks.get(ip)
        if not rule_id:
            return False

        try:
            self.client.firewall.access_rules.rules.delete(
                account_id=self.account_id,
                rule_id=rule_id
            )
            self.active_blocks.pop(ip, None)
            print(f"✅ Unblocked: {ip}")
            return True
        except Exception as e:
            print(f"❌ Unblock error: {e}")
            return False

    def list_blocks(self):
        """Liệt kê các rule đang có"""
        try:
            rules = self.client.firewall.access_rules.rules.list(account_id=self.account_id)
            return rules.result
        except Exception as e:
            print(e)
            return []

# Khởi tạo singleton
cloudflare_service = CloudflareService()