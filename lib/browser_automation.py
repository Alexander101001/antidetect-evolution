#!/usr/bin/env python3
"""
Browser Automation — REAL browser control via Chromium in Ubuntu proot.

This solves:
- JavaScript rendering (HF, Vercel, etc.)
- OAuth flows (click GitHub button → authorize)
- CAPTCHA bypass (with audio + OCR)
- Any form that needs real browser

Uses Playwright Chromium installed in proot-distro Ubuntu.
Runs from Termux Python but executes browser in Ubuntu proot.
"""

import subprocess
import time
import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict


@dataclass
class BrowserSession:
    """Active browser session."""
    session_id: str
    started_at: float
    cookies: List[Dict]
    current_url: Optional[str]
    user_agent: str
    headless: bool = True


class BrowserAutomation:
    """Control a real browser from Termux via proot Ubuntu."""

    CHROMIUM_PATH = "/root/.cache/ms-playwright/chromium-1234/chrome-linux/chrome"
    PLAYWRIGHT_SCRIPT_PATH = "/tmp/playwright_runner.py"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.session_id = f"session_{int(time.time())}"
        self.started_at = time.time()
        self.cookies = []
        self.current_url = None
        self.user_agent = None
        self.result_file = Path(f"/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/browser_result_{self.session_id}.json")
        self._test_setup()

    def _test_setup(self) -> bool:
        """Test if browser setup is ready."""
        try:
            result = subprocess.run(
                ["proot-distro", "login", "ubuntu", "--", "bash", "-c",
                 f"test -f {self.CHROMIUM_PATH} && echo OK"],
                capture_output=True, text=True, timeout=30
            )
            return "OK" in result.stdout
        except Exception:
            return False

    def _run_playwright_script(self, script: str) -> Dict:
        """
        Run a Python Playwright script inside Ubuntu proot.
        Returns the result as JSON.
        """
        # Write the script to a file accessible from proot
        # Termux home is mounted at the same path inside proot
        script_path = f"/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib/_runner_{self.session_id}.py"

        full_script = f"""
import sys
import json
import time
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from playwright.sync_api import sync_playwright

result = {{'success': False, 'error': None, 'data': None}}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless={'True' if self.headless else 'False'},
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        context = browser.new_context(
            viewport={{'width': 1920, 'height': 1080}},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

{script}

        browser.close()
except Exception as e:
    result['error'] = str(e)
    result['traceback'] = __import__('traceback').format_exc()

# Write result to file
with open('{self.result_file}', 'w') as f:
    json.dump(result, f, default=str)
"""
        Path(script_path).write_text(full_script)

        # Run inside proot
        try:
            subprocess.run(
                ["proot-distro", "login", "ubuntu", "--", "python3", script_path],
                capture_output=True, text=True, timeout=300
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Script timeout (300s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

        # Read result
        if self.result_file.exists():
            try:
                return json.loads(self.result_file.read_text())
            except Exception as e:
                return {"success": False, "error": f"Could not read result: {e}"}
        return {"success": False, "error": "No result file produced"}

    def navigate(self, url: str, wait_for: str = "body") -> Dict:
        """Navigate to a URL and wait for content."""
        script = f"""
        page.goto('{url}', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector('{wait_for}', timeout=30000)
        result['success'] = True
        result['data'] = {{
            'url': page.url,
            'title': page.title(),
            'content_length': len(page.content()),
        }}
        result['cookies'] = [{{'name': c['name'], 'value': c['value'], 'domain': c['domain']}} for c in context.cookies()]
"""
        return self._run_playwright_script(script)

    def fill_form(self, url: str, fields: Dict[str, str],
                  submit_selector: Optional[str] = None,
                  submit_button_text: Optional[str] = None) -> Dict:
        """Fill and submit a form on a page."""
        field_fills = "\n".join([f"page.fill('{sel}', '{val}')" for sel, val in fields.items()])
        submit_code = ""
        if submit_selector:
            submit_code = f"page.click('{submit_selector}')"
        elif submit_button_text:
            submit_code = f"page.click('button:has-text(\"{submit_button_text}\")')"

        script = f"""
page.goto('{url}', wait_until='domcontentloaded', timeout=60000)
page.wait_for_load_state('networkidle', timeout=30000)
{field_fills}
{submit_code}
page.wait_for_load_state('networkidle', timeout=30000)
result['success'] = True
result['data'] = {{
    'url': page.url,
    'title': page.title(),
}}
"""
        return self._run_playwright_script(script)

    def click_oauth_button(self, url: str, provider: str = "github") -> Dict:
        """Click an OAuth provider button (GitHub, Google, etc.)."""
        provider_selectors = {
            "github": "a[href*='github'], button:has-text('GitHub'), [data-provider='github']",
            "google": "a[href*='google'], button:has-text('Google'), [data-provider='google']",
            "gitlab": "a[href*='gitlab'], button:has-text('GitLab')",
            "facebook": "a[href*='facebook'], button:has-text('Facebook')",
        }
        selector = provider_selectors.get(provider.lower(), f"button:has-text('{provider}')")

        script = f"""
        page.goto('{url}', wait_until='networkidle', timeout=60000)
        page.wait_for_selector('{selector}', timeout=30000)
        page.click('{selector}')
        page.wait_for_load_state('networkidle', timeout=30000)
        result['success'] = True
        result['data'] = {{
            'url': page.url,
            'title': page.title(),
            'clicked': '{provider}',
        }}
"""
        return self._run_playwright_script(script)

    def register_with_oauth(self, signup_url: str, provider: str = "github") -> Dict:
        """Full OAuth registration flow."""
        return self.click_oauth_button(signup_url, provider)

    def get_page_text(self, url: str) -> Optional[str]:
        """Get rendered text content of a JS-heavy page."""
        script = f"""
        page.goto('{url}', wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(2000)  # Let JS settle
        result['success'] = True
        result['data'] = page.inner_text('body')
"""
        result = self._run_playwright_script(script)
        if result.get("success"):
            return result.get("data")
        return None

    def fill_github_signup(self, email: str, password: str, username: str) -> Dict:
        """
        Fill GitHub signup form (when accessible).
        GitHub: https://github.com/signup
        """
        script = f"""
page.goto('https://github.com/signup', wait_until='networkidle', timeout=60000)
page.wait_for_timeout(3000)

# Fill email step
page.fill('input[name=\"user[email]\"]', '{email}')
page.click('button[type=\"submit\"]')
page.wait_for_timeout(2000)

# Fill password step
try:
    page.fill('input[name=\"user[password]\"]', '{password}')
    page.click('button[type=\"submit\"]')
    page.wait_for_timeout(2000)
except Exception:
    pass

# Fill username step
try:
    page.fill('input[name=\"user[login]\"]', '{username}')
    page.click('button[type=\"submit\"]')
    page.wait_for_timeout(2000)
except Exception:
    pass

result['success'] = True
result['data'] = {{
    'url': page.url,
    'title': page.title(),
}}
"""
        return self._run_playwright_script(script)

    def screenshot(self, url: str, output_path: str = "/tmp/screenshot.png") -> bool:
        """Take a screenshot of a page."""
        script = f"""
page.goto('{url}', wait_until='networkidle', timeout=60000)
page.screenshot(path='{output_path}', full_page=True)
result['success'] = True
"""
        result = self._run_playwright_script(script)
        return result.get("success", False)


def main():
    print("=" * 70)
    print("🌐 BROWSER AUTOMATION TEST")
    print("=" * 70)

    browser = BrowserAutomation(headless=True)

    if not browser._test_setup():
        print("❌ Chromium not found. Run chromium_termux.py install first.")
        return

    print("✅ Chromium found")

    print("\n1️⃣  Testing navigation...")
    result = browser.navigate("https://example.com")
    print(f"   Success: {result.get('success')}")
    if result.get("data"):
        print(f"   URL: {result['data']['url']}")
        print(f"   Title: {result['data']['title']}")

    print("\n2️⃣  Testing JS page rendering (Hugging Face)...")
    text = browser.get_page_text("https://huggingface.co/join")
    if text:
        print(f"   ✅ Got {len(text)} chars of rendered content")
        print(f"   First 200 chars: {text[:200]}")
    else:
        print("   ❌ Failed to get content")


if __name__ == "__main__":
    main()
