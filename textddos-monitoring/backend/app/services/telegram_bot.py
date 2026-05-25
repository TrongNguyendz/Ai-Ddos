import httpx
from dotenv import load_dotenv


load_dotenv()

# === SỬA Ở ĐÂY ===
TOKEN = "8546638271:AAH6qYLNQYdgMpO28YiKVaIyWqi80BDgiB4"
CHAT_ID = "7995482522"

if not TOKEN or not CHAT_ID:
    print("❌ LỖI: TELEGRAM_TOKEN hoặc TELEGRAM_CHAT_ID chưa được set trong .env")

async def send_telegram_alert(message: str, parse_mode="HTML"):
    if not TOKEN or not CHAT_ID:
        print("❌ Telegram config missing!")
        return False
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                print(f"❌ Telegram API error: {resp.status_code} - {resp.text}")
            return resp.status_code == 200
        except Exception as e:
            print(f"❌ Exception khi gửi Telegram: {e}")
            return False