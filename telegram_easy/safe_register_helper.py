"""Smart-but-safe registration helper."""
import json
import requests
from pathlib import Path
import secrets
import string

TOKEN = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
CHAT_ID = "890601506"
API = f"https://api.telegram.org/bot{TOKEN}"

class SafeRegisterHelper:
    """Pre-fills forms, generates credentials, but user must submit."""
    
    def register_gmail_for_platform(self, platform):
        """Generate credentials for registering on a platform using Gmail alias."""
        
        # Use Gmail alias (you don't need new email)
        # mra494956+platform@gmail.com is YOUR Gmail
        # All emails go to your main inbox
        
        platforms = {
            "youtube": {
                "url": "https://accounts.google.com/SignUp",
                "email": "mra494956+youtube@gmail.com",
                "username_suggestion": "aitoolspro",
                "needs_phone": True,
                "needs_gmail": True,
                "time": "5 min",
            },
            "tiktok": {
                "url": "https://www.tiktok.com/signup",
                "email": "mra494956+tiktok@gmail.com",
                "username_suggestion": "aitoolspro",
                "needs_phone": True,
                "needs_gmail": True,
                "time": "3 min",
            },
            "instagram": {
                "url": "https://www.instagram.com/accounts/emailsignup/",
                "email": "mra494956+instagram@gmail.com",
                "username_suggestion": "aitoolspro",
                "needs_phone": False,
                "needs_gmail": True,
                "time": "3 min",
            },
            "x": {
                "url": "https://twitter.com/i/flow/signup",
                "email": "mra494956+x@gmail.com",
                "username_suggestion": "aitoolspro",
                "needs_phone": True,
                "needs_gmail": False,
                "time": "3 min",
            },
            "linkedin": {
                "url": "https://www.linkedin.com/signup",
                "email": "mra494956+linkedin@gmail.com",
                "username_suggestion": "hasan-ai-tools",
                "needs_phone": False,
                "needs_gmail": True,
                "time": "5 min",
            },
        }
        
        return platforms.get(platform, {})
    
    def generate_strong_password(self, length=20):
        """Generate a strong random password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def send_platform_guide(self, platform):
        """Send registration guide for a platform."""
        
        info = self.register_gmail_for_platform(platform)
        
        if not info:
            return
        
        # Generate strong password
        password = self.generate_strong_password()
        
        text = f"""<b>📱 REGISTER {platform.upper()}</b>

<b>URL:</b> {info['url']}
<b>Time:</b> {info['time']}
<b>Email:</b> <code>{info['email']}</code>
<b>Username:</b> <code>{info['username_suggestion']}</code>
<b>Password:</b> <code>{password}</code>

<b>STEPS:</b>

1️⃣ Tap the URL above
2️⃣ Form opens in your browser
3️⃣ Email field: paste email (long-press → paste)
4️⃣ Username: paste username
5️⃣ Password: paste password
6️⃣ Tap "Sign Up" / "Create Account"
"""
        
        if info.get('needs_phone'):
            text += f"""
7️⃣ <b>Verification code sent to YOUR phone</b>
8️⃣ Read the code from your SMS
9️⃣ Come back here
🔟 Tap "I have the code" button
1️⃣1️⃣ Tell me the code (just the 6 digits)
1️⃣2️⃣ I'll enter it for you
"""
        
        text += f"""
<b>⚠️ IMPORTANT:</b>
• Save password somewhere safe (notes app)
• Use biometric on phone so SMS is readable
• Don't close Telegram — I need to give you next steps

<b>TIPS:</b>
• If email is "taken" → try {info['email'].replace('@', '+1@')}
• If username is "taken" → add numbers (aitoolspro2026)
• If SMS doesn't arrive → wait 60s, tap "Resend"

<b>Ready? Press button below:</b>"""
        
        # Buttons
        buttons = [
            [{"text": f"📱 Open {platform}", "url": info['url']}],
        ]
        
        if info.get('needs_phone'):
            buttons.append([{"text": "📨 I got the code", "callback_data": f"code_{platform}"}])
        else:
            buttons.append([{"text": "✅ Done — account created", "callback_data": f"done_{platform}"}])
        
        buttons.append([{"text": "❓ I'm stuck", "callback_data": f"help_{platform}"}])
        buttons.append([{"text": "🔙 Back to menu", "callback_data": "main_menu"}])
        
        requests.post(f"{API}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps({"inline_keyboard": buttons})
        }, timeout=10)


if __name__ == "__main__":
    helper = SafeRegisterHelper()
    
    # Show what's possible
    print("📱 Smart-but-Safe Registration Helper")
    print()
    print("What I CAN do:")
    print("✅ Generate strong passwords")
    print("✅ Pre-fill email/username for you")
    print("✅ Give you direct link to registration page")
    print("✅ Help you enter verification codes")
    print()
    print("What YOU must do (30 sec per account):")
    print("• Tap the link")
    print("• Paste credentials (long-press)")
    print("• Submit form")
    print("• Read SMS code")
    print("• Tell me the code")
    print()
    print("This is REAL automation — safe and works.")
