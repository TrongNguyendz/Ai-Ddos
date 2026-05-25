from typing import Dict, Any, Optional
from datetime import datetime
import re
from loguru import logger

def validate_ip(ip: str) -> bool:
    """Validate IP address format"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False

    # Check each octet
    octets = ip.split('.')
    for octet in octets:
        if not 0 <= int(octet) <= 255:
            return False

    return True

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for API responses"""
    return timestamp.isoformat() + 'Z'

def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def sanitize_string(text: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>]', '', text)
    return sanitized[:max_length]

def parse_protocol(protocol: str) -> str:
    """Normalize protocol names"""
    protocol = protocol.upper().strip()
    valid_protocols = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "FTP", "SSH"]

    if protocol in valid_protocols:
        return protocol
    elif "TCP" in protocol:
        return "TCP"
    elif "UDP" in protocol:
        return "UDP"
    elif "ICMP" in protocol:
        return "ICMP"
    else:
        return "UNKNOWN"

def generate_flow_id(switch: str, src_ip: str, dst_ip: str, timestamp: datetime) -> str:
    """Generate a unique flow identifier"""
    import hashlib
    data = f"{switch}:{src_ip}:{dst_ip}:{timestamp.isoformat()}"
    return hashlib.md5(data.encode()).hexdigest()[:16]

def is_attack_flow(label: int, confidence: float, threshold: float = 0.8) -> bool:
    """Determine if a flow should be considered an attack"""
    return label == 1 and confidence >= threshold

def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        "critical": "#ef4444",
        "high": "#f59e0b",
        "medium": "#eab308",
        "low": "#10b981",
        "info": "#3b82f6"
    }
    return colors.get(severity.lower(), "#6b7280")

def paginate_data(data: list, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
    """Paginate data list"""
    total = len(data)
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "data": data[start:end],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }

def filter_flows_by_time(flows: list, hours: int = 1) -> list:
    """Filter flows by time window"""
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return [f for f in flows if f.get("timestamp", datetime.min) >= cutoff]

def aggregate_flow_stats(flows: list) -> Dict[str, Any]:
    """Aggregate statistics from flow data"""
    if not flows:
        return {
            "total_flows": 0,
            "attack_flows": 0,
            "normal_flows": 0,
            "attack_percentage": 0.0,
            "avg_pktrate": 0.0,
            "avg_kbps": 0.0
        }

    total_flows = len(flows)
    attack_flows = len([f for f in flows if f.get("label") == 1])
    normal_flows = total_flows - attack_flows

    avg_pktrate = sum(f.get("pktrate", 0) for f in flows) / total_flows
    avg_kbps = sum(f.get("tot_kbps", 0) for f in flows) / total_flows

    return {
        "total_flows": total_flows,
        "attack_flows": attack_flows,
        "normal_flows": normal_flows,
        "attack_percentage": calculate_percentage(attack_flows, total_flows),
        "avg_pktrate": round(avg_pktrate, 2),
        "avg_kbps": round(avg_kbps, 2)
    }
