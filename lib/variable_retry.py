"""
🔄 VARIABLE RETRY SYSTEM
Never uses fixed timing. Looks like a real person who sometimes forgets,
sometimes is patient, sometimes is quick. Avoids detection patterns.
"""
import random
import time
import logging
from datetime import datetime, timezone
from functools import wraps

# Persistent state across calls
_RETRY_STATE = {}


def variable_retry(max_attempts=10, base_delay=30, action_name="action"):
    """
    Decorator that retries a function with human-like variable delays.
    
    Delays are:
    - Never fixed (random between min and max)
    - Don't follow patterns (43min, 27min, 53min etc.)
    - Account for time of day
    - Account for past attempts
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{action_name}:{func.__name__}"
            if key not in _RETRY_STATE:
                _RETRY_STATE[key] = {
                    "attempts": 0,
                    "last_success": 0,
                    "last_failure": 0,
                    "consecutive_failures": 0,
                }
            
            state = _RETRY_STATE[key]
            
            for attempt in range(1, max_attempts + 1):
                state["attempts"] += 1
                
                try:
                    result = func(*args, **kwargs)
                    state["last_success"] = time.time()
                    state["consecutive_failures"] = 0
                    if attempt > 1:
                        logging.info(f"✅ {action_name} succeeded on attempt {attempt}")
                    return result
                
                except Exception as e:
                    state["last_failure"] = time.time()
                    state["consecutive_failures"] += 1
                    
                    if attempt >= max_attempts:
                        logging.error(f"❌ {action_name} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    # Calculate variable delay (NEVER fixed)
                    delay = calculate_retry_delay(
                        attempt=attempt,
                        consecutive_failures=state["consecutive_failures"],
                        base_delay=base_delay,
                        action_name=action_name
                    )
                    
                    logging.warning(
                        f"⚠️  {action_name} attempt {attempt}/{max_attempts} failed: {str(e)[:100]}"
                    )
                    logging.info(f"⏳ Waiting {delay/60:.1f} minutes before retry...")
                    
                    # Sleep in chunks (looks more human than single long sleep)
                    chunks = max(1, int(delay / 30))
                    chunk_size = delay / chunks
                    for i in range(chunks):
                        time.sleep(chunk_size)
                        # Sometimes add micro-break (like checking phone)
                        if random.random() < 0.1:
                            time.sleep(random.uniform(5, 30))
            
            return None
        return wrapper
    return decorator


def calculate_retry_delay(attempt, consecutive_failures, base_delay=30, action_name="action"):
    """
    Calculate next retry delay. Always different, always human-like.
    
    Examples of what it generates:
    - 27 min 14 sec
    - 43 min 51 sec  
    - 8 min 33 sec
    - 1 hr 17 min
    - 19 min 06 sec
    """
    # Base grows exponentially with attempts (humans get frustrated)
    multiplier = min(2 ** (attempt - 1), 8)  # cap at 8x
    
    # But random within that range
    base_with_multiplier = base_delay * multiplier
    
    # Random factor 0.5x to 3x of base (huge variance)
    random_factor = random.uniform(0.5, 3.0)
    
    delay_seconds = base_with_multiplier * random_factor
    
    # Add prime-number seconds (looks more random)
    prime_seconds = random.choice([0, 7, 11, 13, 17, 23, 29, 37, 41, 43, 47, 53])
    delay_seconds += prime_seconds
    
    # Time of day consideration
    hour = datetime.now(timezone.utc).hour
    if 1 <= hour <= 6:  # Night - longer delays (humans sleeping)
        delay_seconds *= random.uniform(1.2, 2.0)
    elif 22 <= hour <= 24:  # Late evening
        delay_seconds *= random.uniform(1.1, 1.5)
    
    # Consecutive failures add longer delays (humans give up faster)
    if consecutive_failures >= 3:
        delay_seconds *= random.uniform(1.5, 2.5)
    elif consecutive_failures >= 5:
        # After many failures, sometimes take very long break
        if random.random() < 0.3:
            delay_seconds *= random.uniform(3.0, 8.0)
    
    # Round to nearest 30 seconds (humans don't count exactly)
    delay_seconds = round(delay_seconds / 30) * 30
    
    # Minimum 10 seconds
    delay_seconds = max(10, delay_seconds)
    
    # Maximum 4 hours (humans go to sleep)
    delay_seconds = min(4 * 3600, delay_seconds)
    
    return delay_seconds


def format_delay(seconds):
    """Convert seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        secs = seconds % 60
        return f"{minutes:.0f} min {secs:.0f} sec"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{hours:.0f} hr {minutes:.0f} min"


# Test
if __name__ == "__main__":
    print("🔄 VARIABLE RETRY SYSTEM TEST")
    print("=" * 50)
    print()
    print("Simulating 10 retries of same action:")
    print()
    
    for attempt in range(1, 11):
        delay = calculate_retry_delay(
            attempt=attempt,
            consecutive_failures=attempt - 1,
            base_delay=30,
            action_name="test_action"
        )
        formatted = format_delay(delay)
        print(f"   Attempt {attempt}: {formatted} ({delay:.0f}s)")
