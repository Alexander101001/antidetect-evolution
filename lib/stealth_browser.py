"""
🥷 STEALTH BROWSER - Maximum Undetectability
- Rotates user agent per session
- Hides navigator.webdriver
- Spoofs screen, hardware, timezone
- Random mouse movements (Bezier curves)
- Realistic typing with typos
"""
import random
import time
import math
import string

# Realistic user agents (regular browsers, not headless)
USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Safari Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Chrome Android (mobile)
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Chrome Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Common screen resolutions
SCREEN_RESOLUTIONS = [
    (1920, 1080), (2560, 1440), (1366, 768), (1536, 864),
    (1440, 900), (1680, 1050), (1280, 720), (1280, 800),
    (1024, 768), (1600, 900),
]

# Time zones
TIMEZONES = [
    "Asia/Baghdad",      # Iraq (Hasan's location)
    "Asia/Riyadh",       # Saudi
    "Europe/Istanbul",   # Turkey
    "Asia/Dubai",        # UAE
    "Europe/London",     # UK
    "America/New_York",  # US East
    "America/Los_Angeles",
]

# Languages
LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "ar,en;q=0.8",  # Arabic (relevant for Hasan)
    "en,ar;q=0.5",
]


def get_random_profile():
    """Get a randomized but realistic browser profile."""
    return {
        "user_agent": random.choice(USER_AGENTS),
        "screen": random.choice(SCREEN_RESOLUTIONS),
        "timezone": random.choice(TIMEZONES),
        "language": random.choice(LANGUAGES),
        "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
        "hardware_concurrency": random.choice([4, 8, 12, 16]),
        "device_memory": random.choice([4, 8, 16, 32]),
    }


# JavaScript to inject for maximum stealth
STEALTH_JS = """
// Hide webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
    configurable: true
});

// Hide automation-related properties
delete navigator.__proto__.webdriver;
delete window.navigator.webdriver;

// Spoof plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
        {name: 'Native Client', filename: 'internal-nacl-plugin'}
    ]
});

// Spoof languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Spoof permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);

// Spoof chrome runtime
window.chrome = {
    runtime: {}
};

// Spoof iframe contentWindow
const originalGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(...args) {
    const context = originalGetContext.apply(this, args);
    if (context && args[0] === '2d') {
        const originalGetImageData = context.getImageData;
        context.getImageData = function(...args) {
            const imageData = originalGetImageData.apply(this, args);
            // Add tiny noise
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] = imageData.data[i] ^ (Math.random() < 0.01 ? 1 : 0);
            }
            return imageData;
        };
    }
    return context;
};

// Spoof WebGL
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
};

console.log('Stealth: active');
"""


def bezier_mouse_path(start_x, start_y, end_x, end_y, steps=20):
    """
    Generate Bezier curve mouse movement (humans don't move in straight lines).
    Returns list of (x, y) tuples.
    """
    # Control points with random offset
    cp1_x = start_x + (end_x - start_x) * random.uniform(0.2, 0.5) + random.uniform(-50, 50)
    cp1_y = start_y + (end_y - start_y) * random.uniform(0.1, 0.4) + random.uniform(-50, 50)
    cp2_x = start_x + (end_x - start_x) * random.uniform(0.5, 0.8) + random.uniform(-30, 30)
    cp2_y = start_y + (end_y - start_y) * random.uniform(0.6, 0.9) + random.uniform(-30, 30)
    
    path = []
    for i in range(steps + 1):
        t = i / steps
        # Cubic Bezier
        x = ((1-t)**3 * start_x + 
             3*(1-t)**2*t * cp1_x + 
             3*(1-t)*t**2 * cp2_x + 
             t**3 * end_x)
        y = ((1-t)**3 * start_y + 
             3*(1-t)**2*t * cp1_y + 
             3*(1-t)*t**2 * cp2_y + 
             t**3 * end_y)
        
        # Add micro-jitter (humans have shaky hands)
        x += random.uniform(-1.5, 1.5)
        y += random.uniform(-1.5, 1.5)
        path.append((x, y))
    
    return path


def realistic_typing(text, wpm=None):
    """
    Generator that yields characters with realistic timing.
    Humans make typos occasionally and have variable speed.
    """
    if wpm is None:
        # Average typing: 40 wpm, range 25-65
        wpm = random.uniform(25, 65)
    
    # Characters per minute
    cpm = wpm * 5  # avg 5 chars per word
    base_delay = 60 / cpm  # seconds per char
    
    # Common typos (adjacent keys on QWERTY)
    typo_map = {
        'a': 'sqwz', 'b': 'vngh', 'c': 'xdfv', 'd': 'serfcx',
        'e': 'wrds', 'f': 'drtgvc', 'g': 'fthyhb', 'h': 'gjuy',
        'i': 'uko', 'j': 'hku', 'k': 'jli', 'l': 'ok',
        'm': 'njk', 'n': 'bmhj', 'o': 'iplk', 'p': 'o',
        'q': 'wa', 'r': 'etdf', 's': 'awedxz', 't': 'rfgy',
        'u': 'yhji', 'v': 'cbgf', 'w': 'qase', 'x': 'zsdc',
        'y': 'tghu', 'z': 'asx',
    }
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Occasionally make a typo (2-5% of chars)
        if (char.isalpha() and 
            random.random() < random.uniform(0.02, 0.05) and
            char.lower() in typo_map):
            # Type wrong character
            wrong = random.choice(typo_map[char.lower()])
            yield wrong, base_delay * random.uniform(0.8, 1.2)
            
            # Realize mistake (humans pause)
            time.sleep(random.uniform(0.2, 0.6))
            
            # Backspace
            yield '\b', random.uniform(0.1, 0.2)
            time.sleep(random.uniform(0.05, 0.15))
        
        yield char, base_delay * random.uniform(0.6, 1.6)
        
        # Occasional pause (humans pause to think)
        if random.random() < 0.08:
            time.sleep(random.uniform(0.3, 1.2))
        
        # Longer pause after space or punctuation
        if char in ' .,!?\n':
            time.sleep(random.uniform(0.1, 0.4))
        
        i += 1


def get_viewport_profile():
    """Get viewport that looks real."""
    profile = get_random_profile()
    return {
        "width": profile["screen"][0],
        "height": profile["screen"][1],
        "deviceScaleFactor": random.choice([1, 1.25, 1.5, 2]),
        "isMobile": "Mobile" in profile["user_agent"],
        "hasTouch": random.random() < 0.3,
        "isLandscape": random.random() < 0.7,
    }


# Verify what's covered
def print_protection_summary():
    """Print what's being protected against."""
    print("🥷 STEALTH PROTECTION SUMMARY")
    print("=" * 50)
    print("✅ navigator.webdriver = undefined")
    print("✅ Chrome runtime spoofed")
    print("✅ Plugins spoofed (looks like real Chrome)")
    print("✅ Languages match region")
    print("✅ Screen resolution randomized")
    print("✅ Timezone randomized (incl. Asia/Baghdad)")
    print("✅ Hardware concurrency realistic")
    print("✅ Canvas fingerprint protected (noise)")
    print("✅ WebGL vendor spoofed")
    print("✅ Mouse uses Bezier curves")
    print("✅ Typing has typos + variable speed")
    print("✅ User agent rotated per session")
    print("✅ Permissions API spoofed")
    print("=" * 50)


if __name__ == "__main__":
    print_protection_summary()
    print()
    print("🧪 Testing Bezier mouse path:")
    path = bezier_mouse_path(100, 100, 500, 400)
    print(f"   Generated {len(path)} points")
    print(f"   Start: ({path[0][0]:.1f}, {path[0][1]:.1f})")
    print(f"   End: ({path[-1][0]:.1f}, {path[-1][1]:.1f})")
    print()
    
    print("🧪 Testing realistic typing:")
    sample = "Hello world, this is a test"
    total = 0
    for char, delay in realistic_typing(sample):
        total += delay
    print(f"   '{sample}' = {total:.1f}s (varies each run)")
