#!/usr/bin/env python3
"""
TELEGRAM NOTIFIER — Send reports to user via Telegram bot.

Used by all modules to report progress.
"""

import os
import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict


class TelegramNotifier:
    """Sends messages to Telegram bot."""

    def __init__(self):
        self.bot_token = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
        self.chat_id = "890601506"
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send a message."""
        try:
            # Telegram has 4096 char limit per message
            if len(message) > 4000:
                # Split into chunks
                chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
                for chunk in chunks:
                    self._send_chunk(chunk, parse_mode)
                    time.sleep(0.5)
            else:
                self._send_chunk(message, parse_mode)
            return True
        except Exception as e:
            print(f"Telegram send error: {e}")
            return False

    def _send_chunk(self, message: str, parse_mode: str = "HTML"):
        """Send a single message chunk."""
        url = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
        }
        try:
            response = requests.post(url, data=data, timeout=15)
            return response.json()
        except Exception as e:
            print(f"Send chunk error: {e}")
            return None

    def send_report(self, title: str, content: Dict, footer: str = ""):
        """Send a formatted report."""
        msg = f"<b>{title}</b>\n\n"
        for key, value in content.items():
            msg += f"<b>{key}:</b> {value}\n"
        if footer:
            msg += f"\n<i>{footer}</i>"
        return self.send(msg)

    def send_evolution_report(self, result: Dict):
        """Send evolution engine report."""
        msg = f"""🧬 <b>EVOLUTION ENGINE REPORT</b>

<b>Generation:</b> {result.get('generation', 'N/A')}
<b>Revenue:</b> ${result.get('total_revenue', 0):.2f}
<b>Scaling:</b> {result.get('scaling', 0)} strategies
<b>Archived:</b> {result.get('archived', 0)}
<b>Mutations:</b> {result.get('mutations', 0)}

⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}"""
        return self.send(msg)

    def send_account_report(self, accounts: list):
        """Send account registration report."""
        msg = f"""📁 <b>ACCOUNT REGISTRATION REPORT</b>

<b>Total accounts:</b> {len(accounts)}
"""
        for acc in accounts[:10]:  # First 10
            msg += f"\n• {acc.get('platform', 'Unknown')}"
            if acc.get('category'):
                msg += f" ({acc['category']})"
        if len(accounts) > 10:
            msg += f"\n... and {len(accounts) - 10} more"
        return self.send(msg)

    def send_error(self, error: str, context: str = ""):
        """Send error notification."""
        msg = f"""⚠️ <b>ERROR REPORT</b>

<b>Context:</b> {context}
<b>Error:</b> {error}

⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}"""
        return self.send(msg)


def main():
    """Test the notifier."""
    notifier = TelegramNotifier()
    notifier.send("🧪 Test message from Antidetect Worker — system check successful!")


if __name__ == "__main__":
    main()
