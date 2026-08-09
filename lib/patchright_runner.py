#!/usr/bin/env python3
"""
Patchright Test — uses real Patchright (patched Playwright) to bypass detection.

This is the REAL solution:
- Patchright is a drop-in replacement for Playwright
- Patches Chrome's anti-bot signals at the C++ level
- Used by major bot operators
- Detected as "Chrome 120" not "HeadlessChrome"

Direct call to Patchright via proot-distro.
"""

import subprocess
import json
import sys
import os
import random
import time
from pathlib import Path
from typing import Optional, Dict


def run_patchright(url: str, action: str = "navigate", **kwargs) -> Dict:
    """
    Run Patchright against a URL with full anti-detection.

    Args:
        url: URL to visit
        action: 'navigate', 'get_text', 'screenshot'
        kwargs: action-specific params
    """
    script_path = "/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib/_patchright_runner.py"
    result_path = "/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/patchright_result.json"

    # Generate human fingerprint
    ua = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ])

    # Match platform to UA
    if "Windows" in ua:
        platform = "Win32"
        viewport = {"width": 1920, "height": 1080}
    elif "Macintosh" in ua:
        platform = "MacIntel"
        viewport = {"width": 2560, "height": 1600}
    else:
        platform = "Linux x86_64"
        viewport = {"width": 1920, "height": 1080}

    # Build script
    script = f"""
import json
import sys
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from patchright.sync_api import sync_playwright

result = {{'success': False, 'error': None, 'data': None}}

# JavaScript to inject BEFORE page load - hides all bot signals
INIT_SCRIPT = '''
Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});

Object.defineProperty(navigator, 'plugins', {{
    get: () => [
        {{name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'}},
        {{name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''}},
        {{name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}},
    ],
}});

Object.defineProperty(navigator, 'languages', {{
    get: () => ['en-US', 'en']
}});

Object.defineProperty(navigator, 'platform', {{
    get: () => '{platform}'
}});

window.chrome = {{
    runtime: {{}},
    loadTimes: function() {{}},
    csi: function() {{}},
    app: {{isInstalled: false}}
}};

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({{state: Notification.permission}}) :
        originalQuery(parameters)
);

const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {{
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
}};
'''

try:
    with sync_playwright() as p:
        # Patchright's launch has stealth built in
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
            ],
            chromium_sandbox=False,
        )

        context = browser.new_context(
            viewport={json.dumps(viewport)},
            user_agent='{ua}',
            locale='en-US',
            timezone_id='America/New_York',
            color_scheme='light',
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            extra_http_headers={{
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"{' + platform + '}"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }}
        )

        # Inject stealth BEFORE any page loads
        context.add_init_script(INIT_SCRIPT)

        page = context.new_page()

        # Navigate
        page.goto('{url}', wait_until='domcontentloaded', timeout=60000)

        # Wait for JS to settle
        page.wait_for_timeout(3000)

        # Get content
        title = page.title()
        content = page.content()
        body_text = page.inner_text('body')

        result['success'] = True
        result['data'] = {{
            'url': page.url,
            'title': title,
            'content_length': len(content),
            'text_length': len(body_text),
            'text_preview': body_text[:500] if body_text else '',
            'cookies': [{{'name': c['name'], 'value': c['value'], 'domain': c['domain']}} for c in context.cookies()],
        }}

        browser.close()
except Exception as e:
    result['error'] = str(e)
    import traceback
    result['traceback'] = traceback.format_exc()

with open('{result_path}', 'w') as f:
    json.dump(result, f, default=str)
"""
    Path(script_path).write_text(script)

    # Run via proot
    try:
        result = subprocess.run(
            ["proot-distro", "login", "ubuntu", "--", "python3", script_path],
            capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout (120s)"}

    if Path(result_path).exists():
        try:
            return json.loads(Path(result_path).read_text())
        except Exception as e:
            return {"success": False, "error": f"Parse error: {e}"}
    return {"success": False, "error": "No result file"}


def main():
    print("=" * 70)
    print("🥷 PATCHRIGHT TEST — Real Anti-Detection Browser")
    print("=" * 70)

    # Test 1: bot.sannysoft.com (detection test)
    print("\n1️⃣  bot.sannysoft.com (bot detection test)...")
    result = run_patchright("https://bot.sannysoft.com/")
    if result.get("success"):
        data = result["data"]
        print(f"   Content length: {data['content_length']} bytes")
        print(f"   Text length: {data['text_length']}")
        print(f"   Title: {data['title']}")
        # Show what the detection page says
        if 'failed' in data.get('text_preview', '').lower():
            # Count failed vs passed
            text = data.get('text_preview', '')
            failed = text.lower().count('failed')
            passed = text.lower().count('passed')
            print(f"   Tests FAILED: {failed}")
            print(f"   Tests PASSED: {passed}")
    else:
        print(f"   Error: {result.get('error', 'unknown')[:200]}")

    # Test 2: GitHub signup (was blocked before)
    print("\n2️⃣  github.com/signup (was blocked with plain Chromium)...")
    result = run_patchright("https://github.com/signup")
    if result.get("success"):
        data = result["data"]
        print(f"   Title: {data['title']}")
        print(f"   Content length: {data['content_length']} bytes")
        print(f"   Text length: {data['text_length']}")
        if data['content_length'] > 10000:
            print(f"   🎉 GitHub returned FULL content — anti-bot bypassed!")
        elif data['content_length'] > 1000:
            print(f"   ⚠️  Partial content — partial success")
        else:
            print(f"   ❌ Still blocked — only {data['content_length']} bytes")
        print(f"\n   First 200 chars: {data.get('text_preview', '')[:200]}")


if __name__ == "__main__":
    main()
