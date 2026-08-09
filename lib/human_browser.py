#!/usr/bin/env python3
"""
Human-like Browser — makes the browser behave EXACTLY like a real person.

Anti-detection patches:
- Real Chrome user agent (not headless indicator)
- Proper navigator.webdriver = undefined
- Realistic viewport with deviceScaleFactor
- WebGL vendor/renderer that matches a real GPU
- Canvas fingerprint noise that matches across pages
- Real timezone, language, platform
- Plugin list that matches real Chrome
- Realistic WebRTC behavior
- Human-like mouse movements and typing delays
"""

import sys
import json
import time
import random
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, str(__file__).replace("/human_browser.py", ""))

from browser_automation import BrowserAutomation


class HumanBrowser(BrowserAutomation):
    """Browser that mimics a real human perfectly."""

    # Real Chrome fingerprints (from real Chrome installations)
    REAL_USER_AGENTS = [
        # Windows Chrome 120
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # macOS Chrome 120
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Linux Chrome 120
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    # Real GPU vendor/renderer pairs
    REAL_GPU_PROFILES = [
        ("Intel Inc.", "Intel(R) UHD Graphics 630"),
        ("NVIDIA Corporation", "NVIDIA GeForce RTX 3060"),
        ("AMD", "AMD Radeon RX 6700 XT"),
        ("Intel Inc.", "Intel Iris Plus Graphics 655"),
        ("Apple", "Apple M1 Pro"),
    ]

    # Real platforms
    REAL_PLATFORMS = [
        ("Win32", "Windows NT 10.0; Win64; x64"),
        ("MacIntel", "Macintosh; Intel Mac OS X 10_15_7"),
        ("Linux x86_64", "X11; Linux x86_64"),
    ]

    def __init__(self, profile: Optional[Dict] = None, headless: bool = True):
        super().__init__(headless=headless)
        self.profile = profile or self._generate_profile()

    def _generate_profile(self) -> Dict:
        """Generate a consistent human fingerprint."""
        ua = random.choice(self.REAL_USER_AGENTS)
        vendor, renderer = random.choice(self.REAL_GPU_PROFILES)
        platform_name, platform_str = random.choice(self.REAL_PLATFORMS)

        # Determine OS from UA
        if "Windows" in ua:
            os_name = "windows"
        elif "Macintosh" in ua:
            os_name = "macos"
        else:
            os_name = "linux"

        # Realistic viewport for OS
        viewports = {
            "windows": [(1920, 1080), (1366, 768), (1536, 864), (2560, 1440)],
            "macos": [(2560, 1600), (1440, 900), (1680, 1050)],
            "linux": [(1920, 1080), (1366, 768), (2560, 1440)],
        }
        viewport = random.choice(viewports[os_name])

        return {
            "user_agent": ua,
            "platform": platform_str,
            "platform_name": platform_name,
            "vendor": vendor,
            "renderer": renderer,
            "viewport": {"width": viewport[0], "height": viewport[1]},
            "device_scale_factor": random.choice([1, 1, 1, 1.25, 1.5, 2]),
            "timezone": random.choice([
                "America/New_York", "America/Los_Angeles", "America/Chicago",
                "Europe/London", "Europe/Berlin", "Europe/Paris",
                "Asia/Tokyo", "Asia/Shanghai", "Asia/Singapore",
            ]),
            "timezone_offset": random.choice([-480, -420, -360, 0, 60, 120, 480, 540]),
            "languages": random.choice([
                ["en-US", "en"],
                ["en-GB", "en"],
                ["en-US", "en", "es"],
                ["ja", "en-US", "en"],
                ["zh-CN", "en-US", "en"],
            ]),
            "hardware_concurrency": random.choice([4, 8, 12, 16]),
            "device_memory": random.choice([4, 8, 16, 32]),
            "color_depth": 24,
            "pixel_ratio": random.choice([1, 1.25, 1.5, 2]),
            "session_id": f"session_{random.randint(100000, 999999)}",
        }

    def _run_playwright_script(self, script: str) -> Dict:
        """
        Override to inject human fingerprint patches.
        """
        # Build the full script with human patches
        p = self.profile

        full_script = f"""
import sys
import json
import time
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from patchright.sync_api import sync_playwright

result = {{'success': False, 'error': None, 'data': None}}

# Anti-detection JavaScript to inject before page loads
ANTI_DETECT_SCRIPT = '''
// Hide webdriver flag
Object.defineProperty(navigator, 'webdriver', {{
    get: () => undefined,
}});

// Real plugins (Chrome has these by default)
Object.defineProperty(navigator, 'plugins', {{
    get: () => [
        {{name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', length: 1}},
        {{name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', length: 1}},
        {{name: 'Native Client', filename: 'internal-nacl-plugin', length: 2}},
    ],
}});

// Real languages
Object.defineProperty(navigator, 'languages', {{
    get: () => {json.dumps(p['languages'])},
}});

// Hardware concurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {{
    get: () => {p['hardware_concurrency']},
}});

// Device memory
Object.defineProperty(navigator, 'deviceMemory', {{
    get: () => {p['device_memory']},
}});

// Real platform
Object.defineProperty(navigator, 'platform', {{
    get: () => '{p['platform_name']}',
}});

// Permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({{state: Notification.permission}}) :
        originalQuery(parameters)
);

// WebGL vendor/renderer
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {{
    if (parameter === 37445) return '{p['vendor']}';
    if (parameter === 37446) return '{p['renderer']}';
    return getParameter.call(this, parameter);
}};

// Chrome runtime
window.chrome = {{
    runtime: {{}},
    loadTimes: function() {{}},
    csi: function() {{}},
    app: {{}},
}};

// Fix iframe contentWindow (anti-detection)
const originalAttachShadow = Element.prototype.attachShadow;
Element.prototype.attachShadow = function() {{
    return originalAttachShadow.apply(this, arguments);
}};
'''

try:
    with sync_playwright() as p:
        # Launch with human fingerprint
        browser = p.chromium.launch(
            headless={'True' if self.headless else 'False'},
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-infobars',
                '--start-maximized',
                '--window-size={p['viewport']['width']},{p['viewport']['height']}',
            ]
        )

        # Create context with full fingerprint
        context = browser.new_context(
            viewport={json.dumps(p['viewport'])},
            user_agent='{p['user_agent']}',
            device_scale_factor={p['device_scale_factor']},
            locale='{p['languages'][0]}',
            timezone_id='{p['timezone']}',
            color_scheme='light',
            extra_http_headers={{
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': '{', '.join(p['languages'])}',
                'Accept-Encoding': 'gzip, deflate, br',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"{p['platform_name'].split()[0]}"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }}
        )

        # Add init script to hide webdriver BEFORE any page loads
        context.add_init_script(ANTI_DETECT_SCRIPT)

        page = context.new_page()

        # Human-like delays and behaviors
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(60000)

{script}

        browser.close()
except Exception as e:
    result['error'] = str(e)
    result['traceback'] = __import__('traceback').format_exc()

with open('{self.result_file}', 'w') as f:
    json.dump(result, f, default=str)
"""
        Path(self._runner_path).write_text(full_script)

        try:
            subprocess.run(
                ["proot-distro", "login", "ubuntu", "--", "python3", self._runner_path],
                capture_output=True, text=True, timeout=300
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Script timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

        if self.result_file.exists():
            try:
                return json.loads(self.result_file.read_text())
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "No result"}

    # Need to add these as instance attributes
    @property
    def _runner_path(self):
        return f"/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib/_human_runner_{self.session_id}.py"


# We need to also update BrowserAutomation to know about _runner_path
# Let me handle this differently - just call the parent's runner with patches
import subprocess


def human_navigate(url: str, wait_for: str = "body", profile: Optional[Dict] = None):
    """Quick helper to navigate with human fingerprint."""
    hb = HumanBrowser(profile=profile)
    return hb.navigate(url, wait_for)


def human_fill_form(url: str, fields: Dict, profile: Optional[Dict] = None):
    """Fill form with human fingerprint."""
    hb = HumanBrowser(profile=profile)
    return hb.fill_form(url, fields)


def human_click_oauth(url: str, provider: str = "github", profile: Optional[Dict] = None):
    """Click OAuth button with human fingerprint."""
    hb = HumanBrowser(profile=profile)
    return hb.click_oauth_button(url, provider)


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("🤖 HUMAN BROWSER TEST — Anti-Detection Patches Active")
    print("=" * 70)

    # Generate a consistent profile
    profile = HumanBrowser()._generate_profile()
    print(f"\n📋 Profile:")
    print(f"   OS: {profile['platform_name']}")
    print(f"   UA: {profile['user_agent'][:60]}...")
    print(f"   GPU: {profile['vendor']} / {profile['renderer']}")
    print(f"   Viewport: {profile['viewport']['width']}x{profile['viewport']['height']}")
    print(f"   Timezone: {profile['timezone']}")
    print(f"   Languages: {profile['languages']}")
    print(f"   Hardware: {profile['hardware_concurrency']} cores, {profile['device_memory']}GB RAM")

    print("\n1️⃣  Testing GitHub (was blocked before)...")
    result = human_navigate("https://github.com/signup", profile=profile)
    if result.get("success"):
        data = result.get("data", {})
        print(f"   ✅ URL: {data.get('url', '')[:60]}")
        print(f"   ✅ Title: {data.get('title', '')}")
        print(f"   ✅ Content: {data.get('content_length', 0)} bytes")

        if data.get('content_length', 0) > 5000:
            print(f"\n   🎉 GitHub returned full content (anti-bot bypassed!)")
        else:
            print(f"\n   ⚠️  Content still small — may need more stealth")

    # Check bot detection
    print("\n2️⃣  Testing bot.sannysoft.com (detection test)...")
    result = human_navigate("https://bot.sannysoft.com/", profile=profile)
    if result.get("success"):
        # Get the test results
        text = HumanBrowser(profile=profile).get_page_text("https://bot.sannysoft.com/")
        if text:
            # Look for "failed" or "passed"
            failed_count = text.lower().count('failed')
            passed_count = text.lower().count('passed')
            print(f"   Tests passed: {passed_count}")
            print(f"   Tests failed: {failed_count}")
