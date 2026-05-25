# app/services/packet_sniffer.py
import time
import asyncio
import threading
import pandas as pd
from datetime import datetime, timezone, timedelta
from loguru import logger
import pandas as pd
import random
from app.services.telegram_bot import send_telegram_alert
from datetime import datetime
from app.schemas.flow import FlowCreate
from app.core.database import get_flows_collection   # ← Import trực tiếp
from app.services.inference import predict_flow      
from .packet_capture import PacketSnifferWindows
from app.services.websocket_manager import websocket_manager
# from app.services.rule_engine_cloud_flare import rule_engine
from app.services.rule_engine import rule_engine
from app.core.config import settings
VN_TZ = timezone(timedelta(hours=7))
# Global event loop từ FastAPI
main_event_loop = None
class ContinuousPacketSniffer:
    def __init__(self, target_port=8000, interface=None):
        self.target_port = target_port
        self.interface = interface
        self.sniffer = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        
        # Lưu main event loop trước khi start thread
        try:
            global main_event_loop
            main_event_loop = asyncio.get_running_loop()
            logger.info("✅ Main event loop captured for background thread")
        except RuntimeError:
            logger.warning("⚠️ Cannot get running loop, will use fallback method")

        self.thread = threading.Thread(target=self._run_sniffer, daemon=True)
        self.thread.start()
        logger.info(f"🚀 Packet Sniffer started on port {self.target_port}")

    def stop(self):
        self.running = False
        logger.info("⛔ Packet Sniffer stopped")

    def _create_dummy_flow(self):
        now = datetime.now()

        # ================== HÀM TẠO IP THẬT ==================
        def random_public_ip():
            # Các dải IP public phổ biến
            first_octets = [
                1, 8, 23, 31, 45, 49,
                58, 59, 61, 66, 80,
                91, 101, 103, 112,
                113, 115, 118, 123,
                171, 172, 175, 183,
                185, 192, 203
            ]

            first = random.choice(first_octets)

            return (
                f"{first}."
                f"{random.randint(1,255)}."
                f"{random.randint(1,255)}."
                f"{random.randint(1,254)}"
            )

        def random_private_ip():
            private_type = random.choice(["192", "10", "172"])

            if private_type == "192":
                return (
                    f"192.168."
                    f"{random.randint(0,255)}."
                    f"{random.randint(1,254)}"
                )

            elif private_type == "10":
                return (
                    f"10."
                    f"{random.randint(0,255)}."
                    f"{random.randint(0,255)}."
                    f"{random.randint(1,254)}"
                )

            else:
                return (
                    f"172."
                    f"{random.randint(16,31)}."
                    f"{random.randint(0,255)}."
                    f"{random.randint(1,254)}"
                )

        def generate_realistic_ip():
            # 75% public IP, 25% private IP
            if random.random() < 0.75:
                return random_public_ip()
            return random_private_ip()

        # ================== QUYẾT ĐỊNH BENIGN HAY MALICIOUS ==================
        is_malicious = random.random() < 0.4

        # ================== TẠO DỮ LIỆU ==================
        if is_malicious:
            pktcount = random.randint(45, 650)
            byteperflow = random.uniform(6500, 48000)
            tot_kbps = random.uniform(110, 920)
            tot_dur = random.uniform(0.3, 9.5)
            pktrate = random.uniform(18, 220)
            flows = random.randint(2, 18)

            label = "🚨 MALICIOUS"
            color = "\033[91m"

            # Attack traffic thường scan port
            dst_port = random.choice([
                21, 22, 23, 25, 53,
                80, 110, 135, 139,
                443, 445, 3306,
                3389, 5432, 8080
            ])

        else:
            pktcount = random.randint(3, 28)
            byteperflow = random.uniform(650, 5800)
            tot_kbps = random.uniform(8, 98)
            tot_dur = random.uniform(4, 38)
            pktrate = random.uniform(0.15, 5.2)
            flows = 1

            label = "✅ BENIGN"
            color = "\033[92m"

            # User traffic bình thường
            dst_port = random.choice([
                80, 443, 53, 123,
                8080, 8443
            ])

        # ================== CHỌN PROTOCOL ==================
        protocol = random.choice(['TCP', 'UDP', 'ICMP'])

        # ================== TẠO FLOW ==================
        dummy_data = [{
            'Switch': random.choice([
                'API_Gateway',
                'Switch1',
                'Switch2',
                'Firewall',
                'CoreRouter',
                'EdgeRouter'
            ]),

            'Src IP': generate_realistic_ip(),

            'Dst IP': generate_realistic_ip(),

            'Dst Port': (
                self.target_port
                if hasattr(self, 'target_port')
                else dst_port
            ),

            'Protocol': protocol,

            'pktcount': pktcount,

            'byteperflow': round(byteperflow, 2),

            'tot_kbps': round(tot_kbps, 2),

            'rx_kbps': round(
                tot_kbps * random.uniform(0.7, 1.0),
                2
            ),

            'flows': flows,

            'bytecount': int(byteperflow),

            'tot_dur': round(tot_dur, 2),

            'pktrate': round(pktrate, 4),

            'Protocol_ICMP': 1 if protocol == 'ICMP' else 0,

            'Protocol_TCP': 1 if protocol == 'TCP' else 0,

            'Protocol_UDP': 1 if protocol == 'UDP' else 0,

            'start_timestamp': now.strftime(
                '%Y-%m-%d %H:%M:%S.%f'
            )[:-3]
        }]

        df = pd.DataFrame(dummy_data)

        # ================== IN RA CONSOLE ==================
        print(f"\n{'='*70}")
        print(f"{color}{label} - Random Flow Generated\033[0m")
        print(f"{'='*70}")
        print(df.to_string(index=False))
        print(f"{'='*70}\n")

        return df

    async def _save_one_flow(self, row):
        try:
            flows_collection = await get_flows_collection()

            # Tạo input cho model
            flow_input = {
                "switch": str(row.get("Switch", "API_Gateway")),
                "src_ip": str(row.get("Src IP", row.get("src_ip", "0.0.0.0"))),
                "dst_ip": str(row.get("Dst IP", row.get("dst_ip", "0.0.0.0"))),
                "dst_port": int(row.get("Dst Port", getattr(self, 'target_port', 8000))),
                "protocol": str(row.get("Protocol", "TCP")),
                "pktcount": int(row.get("pktcount", 5)),
                "byteperflow": float(row.get("byteperflow", 0.0)),
                "tot_kbps": float(row.get("tot_kbps", 0.0)),
                "rx_kbps": float(row.get("rx_kbps", 0.0)),
                "flows": int(row.get("flows", 1)),
                "bytecount": int(row.get("bytecount", 0)),
                "tot_dur": float(row.get("tot_dur", 0.0)),
                "pktrate": float(row.get("pktrate", 0.0)),
                "protocol_icmp": int(row.get("Protocol_ICMP", 0)),
                "protocol_tcp": int(row.get("Protocol_TCP", 0)),
                "protocol_udp": int(row.get("Protocol_UDP", 0)),
            }

            prediction = predict_flow(flow_input)

            flow_data = {
                **flow_input,
                "timestamp": datetime.now(VN_TZ),
                "label": prediction.get("label", 0),
                "confidence": prediction.get("confidence", 0.95)
            }

            # Lưu vào database
            result = await flows_collection.insert_one(flow_data)
            logger.success(f"✅ Lưu thành công vào MongoDB | ID: {result.inserted_id} | IP: {flow_data['src_ip']}")
            # ==================== BLOCK CLOUD FLARE ====================
            # if prediction.get("label") == 1 and flow_data.get("confidence", 0) > 0.75:
            #     src_ip = flow_data["src_ip"]
                
            #     # Bỏ qua Private IP (192.168., 10., 172.16-31.)
            #     if self._is_private_ip(src_ip):
            #         logger.info(f"⚠️ Private IP detected ({src_ip}), skip Cloudflare block")
            #     else:
            #         threat_score = int(flow_data.get("confidence", 0) * 100)
                    
            #         await rule_engine.process_flow({
            #             "ip": src_ip,
            #             "threat_score": threat_score,
            #             "reason": f"AI Model Detected - Confidence {threat_score}%",
            #             "pktcount": flow_data.get("pktcount"),
            #             "pktrate": flow_data.get("pktrate")
            #         })
            # ================== 3. RULE ENGINE KIỂM TRA & THỰC HIỆN ACTION ==================
            await rule_engine.process_flow(flow_data)
            # Gửi Telegram Alert
            if prediction.get("label") == 1:
                alert_message = f"""
                🔐 <b>Security Alert | DDoS Attack Detected</b>

                ├─ <b>Source IP:</b> <code>{flow_data['src_ip']}</code>
                ├─ <b>Confidence:</b> <code>{flow_data['confidence']*100:.2f}%</code>
                ├─ <b>Pkt Rate:</b> <code>{flow_data.get('pktrate', 0):.2f}</code>
                └─ <b>Timestamp:</b> <i>{flow_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</i>
                """
                await send_telegram_alert(alert_message)

            # Broadcast WebSocket
            await websocket_manager.broadcast_flow(flow_data)

            logger.success(f"💾 Saved flow | Label: {flow_data['label']} | Src: {flow_data['src_ip']}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save flow: {e}")
            logger.error(f"❌ Failed to save flow from IP {row.get('Src IP')}: {type(e).__name__} - {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _is_private_ip(self, ip: str) -> bool:
        """Kiểm tra IP private"""
        if not ip or not isinstance(ip, str):
            return True
        return (
            ip.startswith("192.168.") or 
            ip.startswith("10.") or 
            ip.startswith("172.16.") or ip.startswith("172.17.") or 
            ip.startswith("172.18.") or ip.startswith("172.19.") or 
            ip.startswith("172.2") or ip.startswith("172.30.") or ip.startswith("172.31.")
        )
        
    def _run_sniffer(self):
        # Khởi tạo sniffer, bắt lỗi nếu Scapy không tương thích/không có quyền
        try:
            self.sniffer = PacketSnifferWindows(target_port=self.target_port)
            logger.info(f"✅ PacketSnifferWindows initialized on port {self.target_port}")
        except Exception as e:
            self.sniffer = None
            logger.warning(f"⚠️ PacketSnifferWindows initialization failed: {e}. Running in Simulation mode if enabled.")

        while self.running:
            df = None
            if self.sniffer:
                try:
                    df = self.sniffer.start_sniffing(duration=10, interface=self.interface)
                except Exception as e:
                    logger.error(f"❌ Error sniffing: {e}")
                    df = None

            if df is None or df.empty:
                if settings.ENABLE_SIMULATION:
                    logger.info("⚠️ Không bắt được gói tin thật → Tạo flow giả lập (Simulation Mode)")
                    # df = self._create_dummy_flow()
                else:
                    logger.warning("⚠️ Không bắt được gói tin thật trong 10s và Simulation Mode tắt, bỏ qua lượt này")
                    time.sleep(10)
                    continue
            else:
                logger.success(f"📡 Bắt được {len(df)} flow thật từ network! IP đầu tiên: {df.iloc[0].get('Src IP') if not df.empty else 'N/A'}")

            logger.info(f"📊 Processing {len(df)} flows...")

            for _, row in df.iterrows():
                if main_event_loop and not main_event_loop.is_closed():
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            self._save_one_flow(row), 
                            main_event_loop
                        )
                    except Exception as e:
                        logger.error(f"Failed to schedule _save_one_flow: {e}")
                else:
                    logger.error("Main event loop not available!")

            if self.sniffer:
                self.sniffer.clear_stats()
            
            time.sleep(3)