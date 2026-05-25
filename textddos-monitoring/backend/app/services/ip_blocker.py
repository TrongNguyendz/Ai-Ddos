# app/services/ip_blocker.py
import subprocess
from loguru import logger
from typing import Set, List, Optional

class IPBlocker:
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.rule_name_prefix = "DDoS_Block_"

    def block_ip(self, ip: str, reason: str = "DDoS detection", rule_name: str = None) -> bool:
        """Chặn IP bằng Windows Firewall - Đã cải tiến"""
        if ip in self.blocked_ips or ip in ["127.0.0.1", "::1", "localhost"]:
            return False

        # Bỏ qua Private IP (rất quan trọng)
        if self._is_private_ip(ip):
            logger.info(f"⚠️ Private IP detected ({ip}), skip blocking")
            return False

        try:
            rule_name_suffix = (rule_name or "Manual").replace(" ", "_")[:30]
            full_rule_name = f"{self.rule_name_prefix}{rule_name_suffix}_{ip.replace('.', '_')}"

            # Block Inbound
            cmd_in = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={full_rule_name}_IN",
                "dir=in", "action=block", f"remoteip={ip}",
                "protocol=any", "enable=yes"
            ]
            
            # Block Outbound
            cmd_out = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={full_rule_name}_OUT",
                "dir=out", "action=block", f"remoteip={ip}",
                "protocol=any", "enable=yes"
            ]

            # Thực thi và log chi tiết
            result_in = subprocess.run(cmd_in, capture_output=True, text=True, check=False)
            result_out = subprocess.run(cmd_out, capture_output=True, text=True, check=False)

            if result_in.returncode == 0 or result_out.returncode == 0:
                self.blocked_ips.add(ip)
                logger.warning(f"🚫 ĐÃ CHẶN IP: {ip} | Lý do: {reason}")
                return True
            else:
                logger.error(f"Lỗi chặn IP {ip}:")
                logger.error(f"IN: {result_in.stderr.strip() or result_in.stdout.strip()}")
                logger.error(f"OUT: {result_out.stderr.strip() or result_out.stdout.strip()}")
                return False

        except Exception as e:
            logger.error(f"Lỗi không xác định khi chặn IP {ip}: {e}")
            return False
        
    def _is_private_ip(self, ip: str) -> bool:
        """Kiểm tra IP private"""
        if not ip or not isinstance(ip, str):
            return True
        return (
            # ip.startswith("192.168.") or 
            ip.startswith("10.") or 
            ip.startswith("172.16.") or ip.startswith("172.17.") or 
            ip.startswith("172.18.") or ip.startswith("172.19.") or 
            ip.startswith("172.2") or ip.startswith("172.30.") or ip.startswith("172.31.")
        )

    def unblock_ip(self, ip: str) -> bool:
        """Bỏ chặn IP"""
        try:
            # Tìm và xóa tất cả rule liên quan đến IP này
            subprocess.run(
                f'netsh advfirewall firewall delete rule name=all remoteip={ip}',
                shell=True, capture_output=True
            )
            
            self.blocked_ips.discard(ip)
            logger.info(f"✅ ĐÃ BỎ CHẶN IP: {ip}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi bỏ chặn {ip}: {e}")
            return False

    def get_blocked_ips(self) -> List[str]:
        return list(self.blocked_ips)