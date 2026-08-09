"""
🕐 HUMAN TIMING ENGINE
Random, non-predictable delays to avoid detection.
"""
import random
import time
from datetime import datetime, timezone

_TIMING_STATE = {}

def get_human_delay(min_sec=2, max_sec=15, action_type="general", account_id="default"):
    """Get a delay that looks human (Gaussian + time-of-day modulation)."""
    key = f"{action_type}:{account_id}"
    if key not in _TIMING_STATE:
        _TIMING_STATE[key] = {"count": 0, "avg_delay": 0}
    
    state = _TIMING_STATE[key]
    state["count"] += 1
    
    mean = (min_sec + max_sec) / 2
    std_dev = (max_sec - min_sec) / 4
    delay = random.gauss(mean, std_dev)
    
    # Time of day effect
    hour = datetime.now(timezone.utc).hour
    if 1 <= hour <= 6:
        delay *= random.uniform(1.3, 1.8)
    elif 12 <= hour <= 14:
        delay *= random.uniform(1.1, 1.4)
    
    # Weekend effect
    if datetime.now(timezone.utc).weekday() >= 5:
        delay *= random.uniform(1.05, 1.25)
    
    # Micro-jitter
    delay *= random.uniform(0.85, 1.4)
    delay = round(delay * 10) / 10
    
    delay = max(min_sec * 0.7, min(max_sec * 1.5, delay))
    
    if state["avg_delay"] == 0:
        state["avg_delay"] = delay
    else:
        state["avg_delay"] = state["avg_delay"] * 0.9 + delay * 0.1
    
    return delay

def human_wait(delay):
    """Sleep with realistic variation (not perfectly linear)."""
    if delay <= 0.1:
        time.sleep(delay)
        return
    chunks = max(1, int(delay * 2))
    chunk_size = delay / chunks
    for _ in range(chunks):
        chunk_variance = chunk_size * random.uniform(0.7, 1.3)
        time.sleep(chunk_variance)
        if random.random() < 0.05:
            time.sleep(random.uniform(0.1, 0.5))

def schedule_next_action(account_id="default"):
    """Generate next action time that looks human."""
    now = time.time()
    hour = datetime.now().hour
    
    if 0 <= hour < 6:
        base_minutes = random.uniform(60, 240) if random.random() < 0.7 else random.uniform(15, 45)
    elif 6 <= hour < 9:
        base_minutes = random.uniform(10, 35)
    elif 9 <= hour < 12:
        base_minutes = random.uniform(5, 20)
    elif 12 <= hour < 14:
        base_minutes = random.uniform(15, 45)
    elif 14 <= hour < 18:
        base_minutes = random.uniform(8, 25)
    elif 18 <= hour < 22:
        base_minutes = random.uniform(15, 60)
    else:
        base_minutes = random.uniform(30, 120)
    
    r = random.random()
    if r < 0.1:
        base_minutes *= random.uniform(0.2, 0.5)
    elif r > 0.9:
        base_minutes *= random.uniform(2.0, 4.0)
    
    return now + base_minutes * 60, base_minutes

def delay_before_click():
    return random.uniform(0.5, 2.0)

def delay_before_type():
    return random.uniform(0.3, 1.5)

def delay_after_page_load():
    return random.uniform(1.0, 4.0)

def delay_reading(text_length):
    words = text_length / 5
    return max(0.5, words / random.uniform(3.5, 5.0) + random.uniform(0.5, 2.0))

def delay_form_filling(num_fields):
    return num_fields * random.uniform(5, 15)

def delay_between_actions(action_type="general"):
    delays = {
        "registration": random.uniform(45, 180),
        "login": random.uniform(10, 30),
        "navigation": random.uniform(1, 4),
        "general": random.uniform(2, 10),
        "safe": random.uniform(60, 300),
    }
    return delays.get(action_type, delays["general"])
