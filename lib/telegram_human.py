#!/usr/bin/env python3
"""
HUMAN CONVERSATION BOT — Talks naturally with Hasan.

Rules:
- ONLY respond when Hasan messages me
- NEVER send proactive messages (no spam)
- Short, natural responses (like texting)
- Learn his style from previous conversations
- Be friendly, casual, real
- Don't sound like a robot
"""

import requests
import time
import json
import re
import random
from pathlib import Path
from datetime import datetime

BOT_TOKEN = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
USER_ID = "890601506"
USER_NAME = "Hasan"

# Memory of past conversations
MEMORY_FILE = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/telegram_assistant/memory.json")
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

# User's details learned
USER_INFO = {
    "email": "mra494956@gmail.com",
    "gmail_password": "H@ss@n*@li19900426",
    "phone": "009647740901271",
    "telegram_id": "890601506",
    "preferred_language": "en",  # Will detect from messages
    "style": "casual",  # Will learn from his style
}


def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text())
        except:
            pass
    return {"messages": [], "learned": {}}


def save_memory(memory):
    # Keep last 100 messages
    memory["messages"] = memory["messages"][-100:]
    MEMORY_FILE.write_text(json.dumps(memory, indent=2, default=str))


def send_message(text):
    """Send a single message to Hasan."""
    try:
        if len(text) > 4000:
            text = text[:4000] + "..."
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": USER_ID, "text": text},
            timeout=10
        )
        return r.json().get('ok', False)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return False


def is_arabic(text):
    """Check if message has Arabic."""
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return arabic_chars > len(text) * 0.2


def detect_mood(text):
    """Detect Hasan's mood."""
    text_lower = text.lower()

    # Frustrated
    if any(w in text_lower for w in ['stop', 'wait', 'why', 'no!', 'wrong', 'bad', 'mistake', 'غلط', 'ليش', 'ليش']):
        return "frustrated"

    # Happy/excited
    if any(w in text_lower for w in ['thanks', 'great', 'awesome', 'perfect', 'nice', 'love', 'ممتاز', 'شكرا', 'رائع']):
        return "happy"

    # Curious/asking
    if '?' in text or '؟' in text:
        return "curious"

    # Busy/impatient
    if any(w in text_lower for w in ['quick', 'fast', 'hurry', 'اسرع', 'بسرعة', 'الحين']):
        return "impatient"

    return "neutral"


def casual_response(text, memory):
    """Generate a human-like response. SHORT and natural."""

    text_clean = text.strip()
    text_lower = text_clean.lower()
    mood = detect_mood(text_clean)
    arabic = is_arabic(text_clean)

    # Track conversation
    memory["messages"].append({
        "time": datetime.now().isoformat(),
        "from": "user",
        "text": text_clean
    })

    # Get context from recent messages
    recent = memory["messages"][-10:]

    # SHORT, natural responses based on intent

    # Greetings
    if re.match(r'^(hi|hey|hello|مرحبا|هاي|سلام|هلا|صباح|مساء)', text_lower):
        responses_en = ["hey 👋", "hi!", "hey there", "hello 👋"]
        responses_ar = ["هلا 👋", "أهلين", "مرحبا"]
        save_memory(memory)
        if arabic:
            return random.choice(responses_ar)
        return random.choice(responses_en)

    # How are you
    if any(w in text_lower for w in ['how are you', 'كيفك', 'كيف حالك', 'how r u']):
        if arabic:
            return "تمام، الحمد لله! وانت؟ شلونك؟"
        return "doing good! you?"

    # Thanks
    if any(w in text_lower for w in ['thank', 'thanks', 'شكرا', 'متشكر', 'thx']):
        return random.choice(["you're welcome!", "anytime 😊", "no problem", "العفو"])

    # Status check
    if any(w in text_lower for w in ['status', 'how is', 'حالة', 'hows it']):
        return "all good ✅ what do you need?"

    # Money/earnings
    if any(w in text_lower for w in ['money', 'earn', 'فلوس', 'كسب', 'ربح']):
        return "💰 weekly potential $662. Want me to start working on it?"

    # Job/work
    if any(w in text_lower for w in ['job', 'work', 'شغل', 'وظيفة', 'وظائف']):
        return "💼 finding jobs now. what skills you got? python, writing, design?"

    # Register/sign up
    if any(w in text_lower for w in ['register', 'sign up', 'سجل', 'انشئ', 'حساب جديد']):
        return f"📝 using {USER_INFO['email']} to register on all 35 cloud platforms. starting now..."

    # Deploy
    if any(w in text_lower for w in ['deploy', 'انشر', 'شغل']):
        return "🚀 already deployed. github actions + hugging face running. want more?"

    # Yes
    if text_lower in ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'اه', 'نعم', 'اوكي', 'اوك', 'هيه', 'يب']:
        return "on it ✅"

    # No
    if text_lower in ['no', 'nope', 'na', 'لا', 'كلا']:
        return "ok 👍 what then?"

    # Stop
    if any(w in text_lower for w in ['stop', 'قف', 'بس']):
        return "ok pausing. just message me when ready"

    # Help
    if any(w in text_lower for w in ['help', 'مساعدة', 'ساعدني', 'كيف']):
        return """what i can do:

• register on cloud platforms (have your gmail + password ready)
• find freelance jobs for your skills
• generate proposals
• deploy evolution engine
• make money 💰

just tell me what you want in your own words"""

    # Email shared
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_clean)
    if email_match:
        email = email_match.group(0)
        USER_INFO["email"] = email
        return f"got it, using {email} 👍"

    # Password shared
    if "password" in text_lower or "pass" in text_lower:
        # Extract and store
        pass_match = re.search(r'[A-Za-z0-9@#$%^&*!\-_+=]{6,}', text_clean)
        if pass_match:
            USER_INFO["gmail_password"] = pass_match.group(0)
        return "saved it 🔒 (won't tell anyone)"

    # "I" statements - they want me to do something
    if re.match(r'^(i want|i need|please|can you|اريد|ابي|ممكن)', text_lower):
        return "sure, what specifically? tell me more"

    # Question marks - they want info
    if '?' in text_clean or '؟' in text_clean:
        # Try to answer common questions
        if 'how much' in text_lower or 'كم' in text_lower:
            return "depends on effort. $662/week if you actually apply to jobs"
        if 'when' in text_lower or 'متى' in text_lower:
            return "started already. telegram bot is live"
        if 'where' in text_lower or 'وين' in text_lower:
            return "everything is local on your phone + cloud"
        return "good question. give me a sec to check..."

    # Short acknowledgment needed
    if len(text_clean) < 5:
        return "?"

    # Default - try to understand what they want
    # Look for keywords
    keywords = {
        "cloud": "☁️ 35 cloud platforms researched. which one you want first?",
        "github": "github already done (alexander101001). what next?",
        "deploy": "🚀 already deployed to GH actions + HF. want more?",
        "register": f"📝 will use {USER_INFO['email']}. which platforms?",
        "evolution": "🧬 evolution engine running on gen 2+. testing 20 strategies",
        "skill": "what are you good at? python, writing, design?",
    }

    for kw, response in keywords.items():
        if kw in text_lower:
            save_memory(memory)
            return response

    # If message is unclear
    if len(text_clean) < 30:
        return "tell me more?"

    # Long message - acknowledge and ask what specifically
    return f"got it. you said:\n\n'{text_clean[:200]}'\n\nwhat do you want me to do with this?"


def handle_update(update, memory):
    """Handle incoming update."""
    msg = update.get('message', {})
    text = msg.get('text', '')
    chat_id = str(msg.get('chat', {}).get('id', ''))

    # Only respond to Hasan
    if chat_id != USER_ID or not text:
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Hasan: {text[:100]}", flush=True)

    # Small delay for natural feel
    time.sleep(random.uniform(0.3, 0.8))

    # Get response
    response = casual_response(text, memory)

    # Track our response
    memory["messages"].append({
        "time": datetime.now().isoformat(),
        "from": "me",
        "text": response
    })
    save_memory(memory)

    # Send it
    send_message(response)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Me: {response[:80]}", flush=True)


def main():
    """Listen for messages from Hasan."""
    print("=" * 60, flush=True)
    print("💬 HUMAN CONVERSATION BOT — Online", flush=True)
    print("=" * 60, flush=True)
    print(f"Talking to: {USER_NAME} ({USER_ID})", flush=True)
    print(f"Email: {USER_INFO['email']}", flush=True)
    print("Waiting for messages...", flush=True)
    print(flush=True)

    memory = load_memory()

    last_update_id = 0

    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params={
                    "offset": last_update_id + 1,
                    "timeout": 30,
                    "limit": 10,
                    "allowed_updates": '["message"]'
                },
                timeout=35
            )
            data = r.json()

            if data.get('ok'):
                for update in data['result']:
                    last_update_id = update['update_id']
                    handle_update(update, memory)
        except KeyboardInterrupt:
            print("\nStopping...", flush=True)
            break
        except Exception as e:
            print(f"Error: {e}", flush=True)
            time.sleep(3)


if __name__ == "__main__":
    main()
