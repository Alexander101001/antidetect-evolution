"""
📱 SEND REPORT TO TELEGRAM
"""
import json
import time
from pathlib import Path

TELEGRAM_BOT = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
TELEGRAM_CHAT = "890601506"

def send_telegram(msg):
    import urllib.request
    import urllib.parse
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT}/sendMessage"
    data = urllib.parse.urlencode({
        'chat_id': TELEGRAM_CHAT,
        'text': msg
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"❌ Telegram error: {e}")

if __name__ == "__main__":
    analytics = json.loads(Path("analytics.json").read_text()) if Path("analytics.json").exists() else {}
    
    msg = f"""🔄 EMPIRE CYCLE COMPLETE

⏰ {time.strftime('%Y-%m-%d %H:%M')}

📊 Status:
   • Tools deployed: {analytics.get('tools_count', 0)}
   • Total visitors: {analytics.get('total_visitors', 0):,}
   • Total revenue: ${analytics.get('total_revenue', 0):.2f}

🛠️ New tools generated
📢 Submitted to directories
💰 Affiliate links updated
⚡ Tools optimized

🎯 Goal: $10,000/day
📅 Target: 180 days

🤖 Next cycle in 3 hours"""
    
    send_telegram(msg)
    print("📱 Report sent to Telegram")
