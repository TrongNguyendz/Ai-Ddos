# app/services/packet_capture.py
import time
import pandas as pd
from collections import defaultdict
from datetime import datetime

try:
    from scapy.all import sniff, IP, IPv6, TCP, UDP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("⚠️ Chưa cài Scapy! Chạy: pip install scapy")


class PacketSnifferWindows:
    def __init__(self, target_port=8000):
        self.target_port = target_port
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0,
            'byte_count': 0,
            'start_time': None,
            'last_time': None,
            'first_timestamp': None,
        })
        self.sniffing = False

    def get_protocol_name(self, protocol_num):
        protocols = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        return protocols.get(protocol_num, f'Other({protocol_num})')

    def process_packet(self, packet):
        try:
            # === HỖ TRỢ CẢ IPv4 VÀ IPv6 ===
            if IP not in packet and IPv6 not in packet:
                return

            if IP in packet:
                ip_layer = packet[IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                protocol = ip_layer.proto
            else:  # IPv6
                ip_layer = packet[IPv6]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                protocol = ip_layer.nh  # Next Header

            packet_size = len(packet)

            # Lấy port từ TCP/UDP
            dport = sport = None
            if TCP in packet:
                dport = packet[TCP].dport
                sport = packet[TCP].sport
            elif UDP in packet:
                dport = packet[UDP].dport
                sport = packet[UDP].sport
            else:
                return

            if dport != self.target_port:
                return

            flow_key = f"{src_ip}:{sport}_{dst_ip}:{dport}_{protocol}"

            current_time = time.time()
            real_timestamp = datetime.now()

            flow = self.flow_stats[flow_key]
            if flow['start_time'] is None:
                flow['start_time'] = current_time
                flow['first_timestamp'] = real_timestamp

            flow['packet_count'] += 1
            flow['byte_count'] += packet_size
            flow['last_time'] = current_time

        except Exception:
            pass

    def calculate_features(self):
        # (Giữ nguyên như cũ, chỉ sửa nhỏ phần parse flow_key)
        features_list = []
        for flow_key, flow in self.flow_stats.items():
            try:
                # Parse flow_key an toàn hơn
                parts = flow_key.split('_')
                src_part = parts[0]
                dst_part = parts[1]
                proto_num = int(parts[2])

                src_ip = src_part.split(':')[0]
                dst_info = dst_part.split(':')
                dst_ip = dst_info[0]
                dport = int(dst_info[1]) if len(dst_info) > 1 else self.target_port

            except:
                continue

            duration = max(flow['last_time'] - flow['start_time'], 0.001) if flow['start_time'] else 0.001

            pktcount = flow['packet_count']
            bytecount = flow['byte_count']
            pktrate = pktcount / duration
            tot_kbps = (bytecount * 8) / (duration * 1000)

            features = {
                'Switch': 'API_Gateway',
                'Src IP': src_ip,
                'Dst IP': dst_ip,
                'Dst Port': dport,
                'Protocol': self.get_protocol_name(proto_num),
                'pktcount': pktcount,
                'byteperflow': round(bytecount, 2),
                'tot_kbps': round(tot_kbps, 4),
                'rx_kbps': round(tot_kbps, 4),
                'flows': 1,
                'bytecount': bytecount,
                'tot_dur': round(duration, 4),
                'pktrate': round(pktrate, 4),
                'Protocol_ICMP': 1 if proto_num == 1 else 0,
                'Protocol_TCP': 1 if proto_num == 6 else 0,
                'Protocol_UDP': 1 if proto_num == 17 else 0,
                'start_timestamp': flow['first_timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            }
            features_list.append(features)

        return features_list

    def start_sniffing(self, duration=10, interface=None):
        if not SCAPY_AVAILABLE:
            print("❌ Scapy chưa được cài!")
            return None

        print(f"🔄 Bắt đầu sniff port {self.target_port} trong {duration}s | Interface: {interface or 'default'}")

        def packet_handler(pkt):
            print(f"📦 [DEBUG] Bắt được packet | Len={len(pkt)} | Has IP={IP in pkt or IPv6 in pkt}")  # ← Debug quan trọng
            self.process_packet(pkt)

        try:
            sniff(
                prn=packet_handler,
                timeout=duration,
                store=False,
                iface=interface,
                filter=f"port {self.target_port}",
                promisc=True   # Bắt thêm promiscuous mode
            )
        except Exception as e:
            print(f"❌ Sniff ERROR: {e}")

        features_df = pd.DataFrame(self.calculate_features())
        print(f"✅ Kết thúc sniff - Tìm thấy {len(features_df)} flows")
        return features_df

    def clear_stats(self):
        self.flow_stats.clear()