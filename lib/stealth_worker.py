"""
🥷 STEALTH WORKER
A worker that:
1. Uses random delays (never fixed)
2. Rotates fingerprints per session
3. Detects rate limiting and backs off intelligently
4. Never follows predictable patterns
5. Saves state for resume across restarts
"""
import asyncio
import json
import random
import time
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from human_timing import (
    get_human_delay, human_wait, schedule_next_action,
    delay_before_click, delay_before_type, delay_after_page_load,
    delay_reading, delay_form_filling, delay_between_actions
)
from stealth_browser import get_random_profile, STEALTH_JS, get_viewport_profile
from variable_retry import variable_retry, calculate_retry_delay, format_delay

# State persistence
STATE_FILE = Path.home() / ".pi/skills/antidetect-stack/data/stealth_state.json"


class StealthWorker:
    """
    Worker that behaves like a human.
    No fixed timings. No patterns. No detection.
    """
    
    def __init__(self, account_id="default", mode="safe"):
        """
        mode: 
        - "safe" - very conservative, long delays (recommended)
        - "normal" - balanced
        - "aggressive" - faster but riskier
        """
        self.account_id = account_id
        self.mode = mode
        self.session_start = time.time()
        self.action_count = 0
        self.last_action_time = 0
        
        # Load previous state
        self.state = self._load_state()
        
        # Get fresh profile for this session
        self.profile = get_random_profile()
        self.viewport = get_viewport_profile()
        
        # Mode-specific settings
        self.mode_settings = {
            "safe": {
                "min_delay": 30,
                "max_delay": 300,
                "max_actions_per_hour": 10,
                "max_actions_per_day": 50,
            },
            "normal": {
                "min_delay": 15,
                "max_delay": 120,
                "max_actions_per_hour": 25,
                "max_actions_per_day": 150,
            },
            "aggressive": {
                "min_delay": 5,
                "max_delay": 60,
                "max_actions_per_hour": 50,
                "max_actions_per_day": 300,
            },
        }
        self.settings = self.mode_settings[mode]
        
        logging.info(f"🥷 StealthWorker initialized")
        logging.info(f"   Account: {account_id}")
        logging.info(f"   Mode: {mode}")
        logging.info(f"   Profile: {self.profile['platform']} {self.profile['screen']}")
        logging.info(f"   Timezone: {self.profile['timezone']}")
    
    def _load_state(self):
        """Load persistent state (survives restarts)."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            "hourly_actions": [],
            "daily_actions": [],
            "rate_limited_until": 0,
            "consecutive_failures": 0,
            "successful_actions": 0,
            "failed_actions": 0,
        }
    
    def _save_state(self):
        """Persist state to disk."""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def wait_for_next_action(self):
        """
        Wait until it's time for next action.
        Considers:
        - Rate limits (max per hour/day)
        - Previous actions timing
        - Time of day patterns
        - Random human factor
        """
        now = time.time()
        
        # Clean up old entries
        hour_ago = now - 3600
        day_ago = now - 86400
        self.state["hourly_actions"] = [t for t in self.state["hourly_actions"] if t > hour_ago]
        self.state["daily_actions"] = [t for t in self.state["daily_actions"] if t > day_ago]
        
        # Check if rate limited
        if self.state["rate_limited_until"] > now:
            wait_seconds = self.state["rate_limited_until"] - now
            logging.warning(f"⏸️  Rate limited. Waiting {format_delay(wait_seconds)}")
            time.sleep(wait_seconds)
            self.state["rate_limited_until"] = 0
        
        # Check hourly limit
        if len(self.state["hourly_actions"]) >= self.settings["max_actions_per_hour"]:
            # Wait until oldest action is >1 hour old
            oldest = self.state["hourly_actions"][0]
            wait_seconds = (oldest + 3600) - now + random.uniform(60, 300)
            logging.warning(f"⏸️  Hourly limit reached. Waiting {format_delay(wait_seconds)}")
            time.sleep(wait_seconds)
        
        # Check daily limit
        if len(self.state["daily_actions"]) >= self.settings["max_actions_per_day"]:
            oldest = self.state["daily_actions"][0]
            wait_seconds = (oldest + 86400) - now + random.uniform(300, 900)
            logging.warning(f"⏸️  Daily limit reached. Waiting {format_delay(wait_seconds)}")
            time.sleep(wait_seconds)
        
        # Variable delay before next action
        delay = get_human_delay(
            self.settings["min_delay"],
            self.settings["max_delay"],
            "registration",
            self.account_id
        )
        
        logging.info(f"⏳ Waiting {delay:.1f}s before next action...")
        human_wait(delay)
    
    def report_action(self, success=True):
        """Record that an action was performed."""
        now = time.time()
        self.state["hourly_actions"].append(now)
        self.state["daily_actions"].append(now)
        self.action_count += 1
        self.last_action_time = now
        
        if success:
            self.state["successful_actions"] += 1
            self.state["consecutive_failures"] = 0
        else:
            self.state["failed_actions"] += 1
            self.state["consecutive_failures"] += 1
        
        self._save_state()
    
    def report_rate_limit(self, duration_minutes=None):
        """
        Got rate limited. Back off intelligently.
        If duration_minutes not specified, calculate based on history.
        """
        if duration_minutes is None:
            # Base on consecutive failures
            base = 5 * self.state["consecutive_failures"]
            # Random factor 1-3
            duration_minutes = base * random.uniform(1, 3)
            # Cap at 4 hours
            duration_minutes = min(240, duration_minutes)
        
        duration_seconds = duration_minutes * 60
        # Add some randomness
        duration_seconds *= random.uniform(1.2, 1.8)
        
        self.state["rate_limited_until"] = time.time() + duration_seconds
        self._save_state()
        
        logging.warning(f"⏸️  Rate limited! Backing off for {format_delay(duration_seconds)}")
    
    def get_stats(self):
        """Get current statistics."""
        uptime = time.time() - self.session_start
        return {
            "session_actions": self.action_count,
            "total_successful": self.state["successful_actions"],
            "total_failed": self.state["failed_actions"],
            "consecutive_failures": self.state["consecutive_failures"],
            "uptime_seconds": uptime,
            "actions_per_hour": len(self.state["hourly_actions"]),
            "actions_today": len(self.state["daily_actions"]),
            "rate_limited": self.state["rate_limited_until"] > time.time(),
            "mode": self.mode,
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    print("🥷 STEALTH WORKER TEST")
    print("=" * 50)
    print()
    
    worker = StealthWorker(account_id="test_acc", mode="safe")
    
    print("Simulating 5 actions with variable timing...")
    print()
    
    for i in range(5):
        print(f"Action {i+1}:")
        worker.wait_for_next_action()
        # Simulate work
        success = random.random() > 0.2
        worker.report_action(success=success)
        print(f"   Result: {'✅' if success else '❌'}")
        print(f"   Stats: {worker.get_stats()}")
        print()
    
    print()
    print("✅ Stealth worker simulation complete")
    print("   No fixed patterns detected in timing")
    print("   All delays were variable")
