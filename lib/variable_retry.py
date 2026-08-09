"""
🔄 VARIABLE RETRY SYSTEM
Never uses fixed timing.
"""
import random
import time
import logging
from datetime import datetime, timezone
from functools import wraps

_RETRY_STATE = {}

def variable_retry(max_attempts=10, base_delay=30, action_name="action"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{action_name}:{func.__name__}"
            if key not in _RETRY_STATE:
                _RETRY_STATE[key] = {"consecutive_failures": 0}
            
            state = _RETRY_STATE[key]
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    state["consecutive_failures"] = 0
                    return result
                except Exception as e:
                    state["consecutive_failures"] += 1
                    if attempt >= max_attempts:
                        raise
                    delay = calculate_retry_delay(attempt, state["consecutive_failures"], base_delay)
                    logging.warning(f"⚠️ {action_name} attempt {attempt}/{max_attempts} failed")
                    logging.info(f"⏳ Waiting {format_delay(delay)} before retry")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def calculate_retry_delay(attempt, consecutive_failures=0, base_delay=30):
    multiplier = min(2 ** (attempt - 1), 8)
    random_factor = random.uniform(0.5, 3.0)
    delay_seconds = base_delay * multiplier * random_factor
    
    prime_seconds = random.choice([0, 7, 11, 13, 17, 23, 29, 37, 41, 43, 47, 53])
    delay_seconds += prime_seconds
    
    hour = datetime.now(timezone.utc).hour
    if 1 <= hour <= 6:
        delay_seconds *= random.uniform(1.2, 2.0)
    elif 22 <= hour <= 24:
        delay_seconds *= random.uniform(1.1, 1.5)
    
    if consecutive_failures >= 3:
        delay_seconds *= random.uniform(1.5, 2.5)
    elif consecutive_failures >= 5 and random.random() < 0.3:
        delay_seconds *= random.uniform(3.0, 8.0)
    
    delay_seconds = round(delay_seconds / 30) * 30
    delay_seconds = max(10, min(4 * 3600, delay_seconds))
    return delay_seconds

def format_delay(seconds):
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.0f} min {seconds%60:.0f} sec"
    else:
        return f"{seconds/3600:.0f} hr {(seconds%3600)/60:.0f} min"
