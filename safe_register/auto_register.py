"""
🤖 AUTO-REGISTRATION ATTEMPT
Tries to register accounts using browser automation.
Uses Stealth techniques to avoid detection.
"""
import asyncio
import json
import secrets
import string
import requests
from datetime import datetime
from pathlib import Path

TOKEN = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
CHAT_ID = "890601506"
API = f"https://api.telegram.org/bot{TOKEN}"


def notify(msg):
    """Send progress to Telegram."""
    try:
        requests.post(f"{API}/sendMessage", 
                     data={"chat_id": CHAT_ID, "text": msg},
                     timeout=10)
    except: pass


async def register_medium():
    """Try to register Medium account using browser."""
    notify("🤖 Attempting Medium registration...")
    
    try:
        # Use nodriver for stealth
        import nodriver as uc
        
        browser = await uc.start(headless=True)
        tab = await browser.get("https://medium.com/m/signin")
        
        notify("✅ Browser opened Medium signup page")
        
        # Generate credentials
        email = f"mra494956+medium{secrets.randbelow(99)}@gmail.com"
        password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$") for _ in range(18))
        
        # Wait for page to load
        await asyncio.sleep(3)
        
        notify(f"📧 Email ready: {email}\n🔑 Password ready\n\n📱 Trying to fill form...")
        
        # Try to find email field
        try:
            # Look for email input
            email_input = await tab.find("input[type='email']", timeout=10)
            if email_input:
                await email_input.send_keys(email)
                notify("✅ Email filled")
        except Exception as e:
            notify(f"⚠️ Couldn't find email field: {e}")
        
        await asyncio.sleep(2)
        
        # Find password
        try:
            password_input = await tab.find("input[type='password']", timeout=10)
            if password_input:
                await password_input.send_keys(password)
                notify("✅ Password filled")
        except Exception as e:
            notify(f"⚠️ Couldn't find password field: {e}")
        
        await asyncio.sleep(2)
        
        # Try to submit
        try:
            submit = await tab.find("button[type='submit']", timeout=10)
            if submit:
                await submit.click()
                notify("✅ Form submitted!")
        except Exception as e:
            notify(f"⚠️ Couldn't submit: {e}")
        
        await asyncio.sleep(5)
        
        # Check if we're in
        url = tab.url
        if "medium.com" in url and "signin" not in url:
            notify("🎉 MEDIUM ACCOUNT CREATED!")
            return {"success": True, "email": email, "password": password, "url": url}
        else:
            notify(f"⚠️ Still on signup page: {url}")
            return {"success": False, "email": email, "password": password}
        
        await browser.stop()
        
    except Exception as e:
        notify(f"❌ Browser automation failed: {e}")
        return {"success": False, "error": str(e)}


async def register_all():
    """Try to register all 10 accounts."""
    results = []
    platforms = ["medium", "threads", "pinterest", "reddit", "instagram",
                 "youtube", "linkedin", "tiktok", "twitter", "facebook"]
    
    for i, platform in enumerate(platforms, 1):
        notify(f"📱 [{i}/10] Registering {platform}...")
        
        if platform == "medium":
            result = await register_medium()
            results.append(result)
        else:
            notify(f"⏭️ {platform} - will try after Medium works")
            results.append({"platform": platform, "status": "pending"})
        
        await asyncio.sleep(10)  # Wait between attempts
    
    # Summary
    notify(f"📊 REGISTRATION ATTEMPT COMPLETE\n\n{json.dumps(results, indent=2)}")


if __name__ == "__main__":
    notify("🤖 STARTING AUTOMATIC REGISTRATION\n\nI'll try to do everything using browser automation.\n\nIf something fails, I'll tell you what to do manually.")
    
    asyncio.run(register_all())
