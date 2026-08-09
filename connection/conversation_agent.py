"""
💬 CONVERSATION AGENT
"""
import json
import time
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("conversation_history.json")

class ConversationAgent:
    def __init__(self):
        self.history = self._load()
        self.patterns = {}
        self.preferences = {}
        self.learnings = []
    
    def _load(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except:
                pass
        return {
            "conversations": [],
            "patterns_learned": {},
            "user_preferences": {},
            "improvements_made": []
        }
    
    def _save(self):
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2))
    
    def record_conversation(self, user_msg, ai_response):
        entry = {
            "timestamp": time.time(),
            "date": datetime.now().isoformat(),
            "user": user_msg,
            "ai": ai_response[:500] if isinstance(ai_response, str) else str(ai_response)[:500]
        }
        self.history["conversations"].append(entry)
        self._extract_patterns(user_msg)
        self._save()
    
    def _extract_patterns(self, user_msg):
        msg = user_msg.lower()
        if "make" in msg and "money" in msg:
            self.preferences["primary_goal"] = "make_money"
        if "autonomous" in msg or "automatic" in msg:
            self.preferences["style"] = "autonomous"
        if "smart" in msg or "creative" in msg:
            self.preferences["quality"] = "high"
        if "free" in msg:
            self.preferences["cost"] = "free_only"
        if "safe" in msg:
            self.preferences["risk"] = "low"
        self.history["user_preferences"] = self.preferences
    
    def add_learning(self, learning):
        self.learnings.append({"timestamp": time.time(), "learning": learning})
        self.history["improvements_made"].append({"timestamp": time.time(), "improvement": learning})
        self._save()
    
    def get_summary(self):
        return {
            "total_conversations": len(self.history["conversations"]),
            "preferences": self.preferences,
            "improvements_count": len(self.history["improvements_made"])
        }


if __name__ == "__main__":
    agent = ConversationAgent()
    agent.record_conversation("make money", "ok")
    print(json.dumps(agent.get_summary(), indent=2))
