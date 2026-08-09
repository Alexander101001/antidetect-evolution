"""
🕐 HUMAN TIMING ENGINE
Random, non-predictable delays to avoid detection patterns.
"""
import random
import time
import math
import hashlib
from datetime import datetime, timezone

# Per-account state to avoid same timing twice
_TIMING_STATE = {}

def get_human_delay(min_sec=2, max_sec=15, action_type="general", account_id="default"):
    """
    Get a delay that looks human.
    
    Humans don't wait exactly 5 seconds. They wait 4.7, 6.3, 8.1, 11.2, etc.
    We use multiple factors:
    - Time of day (humans are faster in morning, slower at night)
    - Day of week (slower on weekends)
    - Account history (different per account)
    - Action type (reading takes longer than clicking)
    - Gaussian distribution around expected value
    """
    key = f"{action_type}:{account_id}"
    if key not in _TIMING_STATE:
        _TIMING_STATE[key] = {
            "count": 0,
            "last_action": 0,
            "avg_delay": 0,
        }
    
    state = _TIMING_STATE[key]
    state["count"] += 1
    
    # Gaussian distribution around middle of range
    mean = (min_sec + max_sec) / 2
    std_dev = (max_sec - min_sec) / 4  # 95% within range
    
    delay = random.gauss(mean, std_dev)
    
    # Add timezone-based modulation
    now = datetime.now(timezone.utc)
    hour = now.hour
    
    # Humans slower late night, faster midday
    if 1 <= hour <= 6:  # Night (Iraq time roughly)
        delay *= random.uniform(1.3, 1.8)
    elif 12 <= hour <= 14:  # Lunch break
        delay *= random.uniform(1.1, 1.4)
    
    # Weekend effect
    if now.weekday() >= 5:  # Sat/Sun
        delay *= random.uniform(1.05, 1.25)
    
    # Add micro-variations (humans have non-uniform micro-delays)
    # Like reading text takes 200-500ms per word
    micro_jitter = random.uniform(0.85, 1.4)
    delay *= micro_jitter
    
    # Round to nearest 0.1 (humans don't measure exactly)
    delay = round(delay * 10) / 10
    
    # Clamp to valid range
    delay = max(min_sec * 0.7, min(max_sec * 1.5, delay))
    
    # Update running average (humans get slightly faster with practice)
    if state["avg_delay"] == 0:
        state["avg_delay"] = delay
    else:
        state["avg_delay"] = state["avg_delay"] * 0.9 + delay * 0.1
    
    state["last_action"] = time.time()
    return delay


def human_wait(delay):
    """Sleep for delay with realistic patterns (not perfectly linear)."""
    if delay <= 0.1:
        time.sleep(delay)
        return
    
    # Break delay into chunks with slight variation
    chunks = max(1, int(delay * 2))
    chunk_size = delay / chunks
    
    for i in range(chunks):
        # Each chunk has slight randomness
        chunk_variance = chunk_size * random.uniform(0.7, 1.3)
        time.sleep(chunk_variance)
        
        # Occasional "distraction" pause
        if random.random() < 0.05:  # 5% chance of micro-pause
            time.sleep(random.uniform(0.1, 0.5))


def schedule_next_action(account_id="default"):
    """
    Generate next action time - looks like a real person.
    Returns Unix timestamp when to act next.
    
    Patterns avoided:
    - No fixed intervals (not 30, 60, 90 mins)
    - Not exactly aligned to hour marks
    - Variable gaps throughout day
    """
    now = time.time()
    hour = datetime.now().hour
    
    # Base intervals (in minutes) - different per time of day
    if 0 <= hour < 6:  # Night - mostly inactive
        if random.random() < 0.7:  # 70% chance no action
            base_minutes = random.uniform(60, 240)  # 1-4 hours
        else:
            base_minutes = random.uniform(15, 45)
    elif 6 <= hour < 9:  # Morning - getting active
        base_minutes = random.uniform(10, 35)
    elif 9 <= hour < 12:  # Mid-morning - active
        base_minutes = random.uniform(5, 20)
    elif 12 <= hour < 14:  # Lunch - varies
        base_minutes = random.uniform(15, 45)
    elif 14 <= hour < 18:  # Afternoon - active
        base_minutes = random.uniform(8, 25)
    elif 18 <= hour < 22:  # Evening - moderate
        base_minutes = random.uniform(15, 60)
    else:  # Late evening - slowing down
        base_minutes = random.uniform(30, 120)
    
    # Special "human" patterns:
    # - Sometimes takes a long break
    # - Sometimes checks quickly
    r = random.random()
    if r < 0.1:  # 10% - quick check
        base_minutes *= random.uniform(0.2, 0.5)
    elif r > 0.9:  # 10% - long break (lunch, meeting, sleep)
        base_minutes *= random.uniform(2.0, 4.0)
    
    # Convert to seconds
    base_seconds = base_minutes * 60
    
    # Add jitter
    jitter = random.uniform(0.8, 1.3)
    final_seconds = base_seconds * jitter
    
    next_time = now + final_seconds
    return next_time, final_seconds / 60  # return minutes for display


# Specific action delays
def delay_before_click():
    """Time before clicking a button. ~500-2000ms"""
    delay = random.uniform(0.5, 2.0)
    # Most clicks are quick, occasional longer
    if random.random() < 0.15:
        delay += random.uniform(0.5, 2.0)
    human_wait(delay)
    return delay


def delay_before_type():
    """Time before starting to type. ~300-1500ms"""
    delay = random.uniform(0.3, 1.5)
    human_wait(delay)
    return delay


def delay_after_page_load():
    """Time after page loads before doing anything. ~1-4 seconds"""
    delay = random.uniform(1.0, 4.0)
    human_wait(delay)
    return delay


def delay_reading(text_length):
    """Reading time based on text length. ~250 words/minute average."""
    # Average reading speed: 250 wpm = 4.17 words/sec
    words = text_length / 5  # avg 5 chars per word
    base_seconds = words / random.uniform(3.5, 5.0)
    # Add "thinking" pauses
    pauses = random.randint(1, max(2, int(words / 30)))
    for _ in range(pauses):
        base_seconds += random.uniform(0.5, 2.0)
    return max(0.5, base_seconds)


def delay_form_filling(num_fields):
    """Time to fill out a form. ~5-15 sec per field."""
    base = num_fields * random.uniform(5, 15)
    return base


def delay_between_actions(action_type="general"):
    """Random delay between platform actions."""
    delays = {
        "registration": random.uniform(45, 180),  # 45s-3min between registrations
        "login": random.uniform(10, 30),
        "form_submit": random.uniform(2, 8),
        "navigation": random.uniform(1, 4),
        "email_check": random.uniform(20, 90),
        "general": random.uniform(2, 10),
        "aggressive": random.uniform(15, 45),
        "safe": random.uniform(60, 300),  # 1-5 minutes for safe mode
    }
    delay = delays.get(action_type, delays["general"])
    return delay


# Example usage:
if __name__ == "__main__":
    print("🕐 HUMAN TIMING ENGINE TEST")
    print("=" * 50)
    print("Random delays (no fixed patterns):")
    print()
    
    for i in range(10):
        d = get_human_delay(5, 15, "registration", "test_account")
        print(f"  Attempt {i+1}: {d:.1f}s")
    
    print()
    print("Next action times:")
    for i in range(5):
        next_t, minutes = schedule_next_action()
        time_str = datetime.fromtimestamp(next_t).strftime("%H:%M:%S")
        print(f"  #{i+1}: in {minutes:.1f} minutes (at {time_str})")
