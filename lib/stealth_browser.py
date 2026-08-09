"""
🥷 STEALTH BROWSER - Anti-detection
"""
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

SCREEN_RESOLUTIONS = [(1920, 1080), (2560, 1440), (1366, 768), (1536, 864), (1440, 900)]
TIMEZONES = ["Asia/Baghdad", "Asia/Riyadh", "Europe/Istanbul", "Asia/Dubai"]
LANGUAGES = ["en-US,en;q=0.9", "ar,en;q=0.8", "en-GB,en;q=0.9"]

def get_random_profile():
    return {
        "user_agent": random.choice(USER_AGENTS),
        "screen": random.choice(SCREEN_RESOLUTIONS),
        "timezone": random.choice(TIMEZONES),
        "language": random.choice(LANGUAGES),
        "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
        "hardware_concurrency": random.choice([4, 8, 12, 16]),
        "device_memory": random.choice([4, 8, 16, 32]),
    }

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true});
delete navigator.__proto__.webdriver;
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {name: 'Chrome PDF Plugin'},
        {name: 'Chrome PDF Viewer'},
        {name: 'Native Client'}
    ]
});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
window.chrome = {runtime: {}};
console.log('Stealth: active');
"""

def bezier_mouse_path(start_x, start_y, end_x, end_y, steps=20):
    cp1_x = start_x + (end_x - start_x) * random.uniform(0.2, 0.5) + random.uniform(-50, 50)
    cp1_y = start_y + (end_y - start_y) * random.uniform(0.1, 0.4) + random.uniform(-50, 50)
    cp2_x = start_x + (end_x - start_x) * random.uniform(0.5, 0.8) + random.uniform(-30, 30)
    cp2_y = start_y + (end_y - start_y) * random.uniform(0.6, 0.9) + random.uniform(-30, 30)
    path = []
    for i in range(steps + 1):
        t = i / steps
        x = ((1-t)**3 * start_x + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end_x)
        y = ((1-t)**3 * start_y + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end_y)
        path.append((x + random.uniform(-1.5, 1.5), y + random.uniform(-1.5, 1.5)))
    return path
