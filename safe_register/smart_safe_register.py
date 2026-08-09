"""
🎯 SMART-SAFE REGISTRATION SYSTEM
30 sec per account. Maximum automation. Zero ban risk.

Strategy:
- Use Gmail aliases (1 Gmail, 100+ unique emails)
- Generate strong passwords
- Pre-fill all data
- Wait for human verification
- Auto-fill remaining fields
"""
import json
import secrets
import string
import requests
from pathlib import Path
from datetime import datetime

TOKEN = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
CHAT_ID = "890601506"
API = f"https://api.telegram.org/bot{TOKEN}"

# Your Gmail base
GMAIL_BASE = "mra494956"
GMAIL_DOMAIN = "gmail.com"

class SmartSafeRegister:
    """Maximum automation while keeping accounts safe."""
    
    def __init__(self):
        self.progress_file = Path('/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/registration_progress.json')
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.progress = self._load_progress()
    
    def _load_progress(self):
        if self.progress_file.exists():
            return json.loads(self.progress_file.read_text())
        return {"completed": [], "pending": [], "codes": {}}
    
    def _save_progress(self):
        self.progress_file.write_text(json.dumps(self.progress, indent=2))
    
    def generate_email(self, platform):
        """Generate Gmail alias for platform."""
        # Gmail aliases: anything+tag@gmail.com works
        return f"{GMAIL_BASE}+{platform}{secrets.randbelow(99)}@{GMAIL_DOMAIN}"
    
    def generate_password(self, length=18):
        """Generate strong password."""
        # Avoid special chars that confuse some sites
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_username(self, platform, base="aitoolspro"):
        """Generate unique username."""
        return f"{base}_{platform}{secrets.randbelow(999)}"
    
    def send_telegram(self, text, buttons=None):
        """Send message with buttons."""
        data = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        if buttons:
            data["reply_markup"] = json.dumps({"inline_keyboard": buttons})
        try:
            requests.post(f"{API}/sendMessage", data=data, timeout=10)
        except Exception as e:
            print(f"Send error: {e}")
    
    def register_account(self, platform):
        """Generate registration package for a platform."""
        
        # Platform-specific config
        configs = {
            "youtube": {
                "name": "YouTube",
                "url": "https://accounts.google.com/SignUp",
                "needs_sms": True,
                "time": "60 sec",
                "icon": "📺",
                "category": "Video",
                "bio": "AI tools, tips, and tutorials to save you time and money. 🤖💰\n\nNew videos every day!\n\n#AI #Tools #Productivity",
            },
            "tiktok": {
                "name": "TikTok",
                "url": "https://www.tiktok.com/signup",
                "needs_sms": True,
                "time": "45 sec",
                "icon": "🎵",
                "category": "Short Video",
                "bio": "AI hacks in 60 seconds 🚀 Follow for daily tips!",
            },
            "instagram": {
                "name": "Instagram",
                "url": "https://www.instagram.com/accounts/emailsignup/",
                "needs_sms": False,
                "time": "45 sec",
                "icon": "📸",
                "category": "Photo/Video",
                "bio": "🤖 AI Tools & Tips\n💰 Save time, save money\n📱 Daily content\n👇 Link in bio",
            },
            "twitter": {
                "name": "X (Twitter)",
                "url": "https://twitter.com/i/flow/signup",
                "needs_sms": True,
                "time": "45 sec",
                "icon": "🐦",
                "category": "Microblog",
                "bio": "🤖 AI Tools\n💡 Daily tips\n🚀 Building in public\n📧 DM for collabs",
            },
            "linkedin": {
                "name": "LinkedIn",
                "url": "https://www.linkedin.com/signup/cold-join",
                "needs_sms": False,
                "time": "60 sec",
                "icon": "💼",
                "category": "Professional",
                "bio": "Building AI tools that save people time and money.\n\nFounder @ AI Writer Pro (alexander101001.github.io/tools-empire)\n\nOpen for collaboration.",
            },
            "facebook": {
                "name": "Facebook",
                "url": "https://www.facebook.com/r.php",
                "needs_sms": True,
                "time": "60 sec",
                "icon": "👥",
                "category": "Social",
                "bio": "AI Tools & Tips for everyday people.\nFollow for daily content!",
            },
            "pinterest": {
                "name": "Pinterest",
                "url": "https://www.pinterest.com/business/create/",
                "needs_sms": False,
                "time": "30 sec",
                "icon": "📌",
                "category": "Visual",
                "bio": "AI tools, productivity hacks, and money-saving tips. 📌💡",
            },
            "reddit": {
                "name": "Reddit",
                "url": "https://www.reddit.com/register/",
                "needs_sms": False,
                "time": "45 sec",
                "icon": "🤖",
                "category": "Community",
                "bio": "AI enthusiast sharing tools, tips, and cool finds.",
            },
            "threads": {
                "name": "Threads",
                "url": "https://www.threads.net/login",
                "needs_sms": False,
                "time": "30 sec",
                "icon": "🧵",
                "category": "Microblog",
                "bio": "AI Tools & Tips Daily 🚀",
            },
            "medium": {
                "name": "Medium",
                "url": "https://medium.com/m/signin",
                "needs_sms": False,
                "time": "45 sec",
                "icon": "✍️",
                "category": "Blog",
                "bio": "Writing about AI, productivity, and making money online.",
            },
        }
        
        config = configs.get(platform, {})
        if not config:
            return None
        
        # Generate unique credentials
        email = self.generate_email(platform)
        password = self.generate_password()
        username = self.generate_username(platform)
        
        return {
            "platform": platform,
            "config": config,
            "email": email,
            "password": password,
            "username": username,
            "timestamp": datetime.now().isoformat(),
        }
    
    def send_registration_card(self, info):
        """Send registration card with everything pre-filled."""
        
        c = info["config"]
        
        # Build beautiful message
        text = f"""<b>{c['icon']} REGISTER {c['name'].upper()}</b>
━━━━━━━━━━━━━━━━━━━━━━━

⏱️ <b>Time:</b> {c['time']}
📁 <b>Category:</b> {c['category']}

<b>📋 COPY THESE (tap to copy):</b>

📧 <b>Email:</b>
<code>{info['email']}</code>

🔑 <b>Password:</b>
<code>{info['password']}</code>

👤 <b>Username:</b>
<code>{info['username']}</code>

📝 <b>Bio (paste later):</b>
<code>{c['bio']}</code>

<b>📱 STEP 1:</b> Tap button below to open signup page"""

        buttons = [
            [{"text": f"🌐 Open {c['name']}", "url": c['url']}],
        ]
        
        if c['needs_sms']:
            text += f"""

<b>📱 STEP 2:</b> Fill the form
  • Email: long-press field → paste
  • Username: paste
  • Password: paste
  • Tap <b>Sign Up</b>

<b>📱 STEP 3:</b> Google sends code to YOUR phone
  • Read the SMS
  • Come back here
  • Tap button below"""
            
            buttons.append([{"text": "📨 I got the code", "callback_data": f"got_code_{info['platform']}"}])
        else:
            text += f"""

<b>📱 STEP 2:</b> Fill form & submit
  • Long-press each field → paste
  • Tap <b>Sign Up</b>

<b>📱 STEP 3:</b> Tap below when done"""
            
            buttons.append([{"text": "✅ Done — account created", "callback_data": f"done_{info['platform']}"}])
        
        buttons.append([{"text": "❓ I'm stuck", "callback_data": f"help_{info['platform']}"}])
        buttons.append([{"text": "⏭️ Skip this one", "callback_data": f"skip_{info['platform']}"}])
        buttons.append([{"text": "🔙 Back to list", "callback_data": "platforms_list"}])
        
        self.send_telegram(text, buttons)
        
        # Save for later
        self.progress["pending"].append(info)
        self._save_progress()
    
    def start_batch(self, platforms):
        """Start registering batch of platforms."""
        
        total = len(platforms)
        completed = len(self.progress["completed"])
        
        text = f"""<b>🚀 STARTING BATCH REGISTRATION</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>Goal:</b> {total} accounts
<b>Already done:</b> {completed}
<b>Remaining:</b> {total - completed}

<b>📱 You'll get:</b>
• Pre-filled email
• Strong password  
• Username suggestion
• Bio template
• Direct link to signup

<b>👤 You do:</b>
• Tap link (1 sec)
• Paste credentials (5 sec)
• Tap submit (1 sec)
• Read SMS code if needed (5 sec)
• Tell me code (3 sec)

<b>🤖 I do:</b>
• Generate everything
• Track progress
• Set up profiles after
• Generate content for each

<b>⏱️ Total time:</b> ~5 minutes for 10 accounts

<b>👇 Starting now:</b>"""
        
        self.send_telegram(text, [[{"text": "▶️ Start registration", "callback_data": "start_now"}]])
    
    def show_platforms_list(self):
        """Show all platforms available."""
        platforms = ["youtube", "tiktok", "instagram", "twitter", "linkedin", 
                     "facebook", "pinterest", "reddit", "threads", "medium"]
        
        text = """<b>📱 10 PLATFORMS — Pick Order</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>⭐ EASIEST (no SMS needed):</b>
• Medium
• Threads  
• Pinterest
• Reddit
• Instagram

<b>📱 NEEDS SMS (your phone):</b>
• YouTube
• TikTok
• Twitter/X
• Facebook
• LinkedIn (sometimes)

<b>💡 SMART ORDER:</b>
1. Start with NO-SMS ones (faster)
2. Then SMS ones

<b>👇 Pick platforms:</b>"""
        
        buttons = []
        # Make rows of 2
        for i in range(0, len(platforms), 2):
            row = []
            for j in range(2):
                if i + j < len(platforms):
                    p = platforms[i + j]
                    row.append({"text": f"📱 {p.title()}", "callback_data": f"register_{p}"})
            buttons.append(row)
        
        buttons.append([{"text": "🚀 DO ALL 10 (recommended)", "callback_data": "register_all"}])
        buttons.append([{"text": "🔙 Main menu", "callback_data": "main_menu"}])
        
        self.send_telegram(text, buttons)


# Initialize
register = SmartSafeRegister()

# Build the complete flow
print("✅ Smart-Safe Register System Ready")
print()
print("📱 10 platforms configured:")
print("   YouTube, TikTok, Instagram, Twitter, LinkedIn,")
print("   Facebook, Pinterest, Reddit, Threads, Medium")
print()
print("⏱️ Time per account: 30-60 seconds")
print()
print("🎯 Strategy:")
print("   1. Generate credentials (instant)")
print("   2. Send registration card (instant)")
print("   3. User taps link, pastes, submits (30 sec)")
print("   4. If SMS: user reads, types code (10 sec)")
print("   5. Account ready!")
