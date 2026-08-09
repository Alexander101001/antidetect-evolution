"""
🥷 STEALTH WORKER
"""
import json
import time
import random
import logging
from pathlib import Path

STATE_FILE = Path.home() / ".pi/skills/antidetect-stack/data/stealth_state.json"

class StealthWorker:
    def __init__(self, account_id="default", mode="safe"):
        self.account_id = account_id
        self.mode = mode
        self.state = self._load_state()
        from stealth_browser import get_random_profile
        self.profile = get_random_profile()
        self.settings = {
            "safe": {"min_delay": 30, "max_delay": 300, "max_per_hour": 10},
            "normal": {"min_delay": 15, "max_delay": 120, "max_per_hour": 25},
            "aggressive": {"min_delay": 5, "max_delay": 60, "max_per_hour": 50},
        }.get(mode, {"min_delay": 30, "max_delay": 300, "max_per_hour": 10})
    
    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except:
                pass
        return {"hourly_actions": [], "daily_actions": [], "rate_limited_until": 0}
    
    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state, indent=2))
    
    def wait_for_next_action(self):
        from human_timing import get_human_delay, human_wait
        delay = get_human_delay(self.settings["min_delay"], self.settings["max_delay"], "registration", self.account_id)
        logging.info(f"⏳ Waiting {delay:.1f}s...")
        human_wait(delay)
    
    def report_action(self, success=True):
        now = time.time()
        self.state["hourly_actions"] = [t for t in self.state["hourly_actions"] if t > now - 3600]
        self.state["hourly_actions"].append(now)
        self._save_state()
    
    def get_stats(self):
        return {
            "actions_last_hour": len(self.state["hourly_actions"]),
            "rate_limited": self.state["rate_limited_until"] > time.time(),
        }
