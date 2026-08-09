
#!/usr/bin/env python3
import os
import time
import sys
sys.path.insert(0, '.')

from evolution_engine import EvolutionEngine

def main():
    print("🤗 Hugging Face Space — Evolution Worker")
    engine = EvolutionEngine()

    while True:
        try:
            result = engine.run_evolution_cycle()
            print(f"Cycle complete: {result}")

            # Send to Telegram if configured
            tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            tg_chat = os.environ.get("TELEGRAM_CHAT_ID")
            if tg_token and tg_chat:
                import requests
                requests.post(
                    f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    data={"chat_id": tg_chat, "text": f"🧬 HF Worker cycle: ${result.get('total_revenue', 0):.2f}"},
                    timeout=10,
                )
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1800)  # 30 min

if __name__ == "__main__":
    main()
