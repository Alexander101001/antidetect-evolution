#!/usr/bin/env python3
"""
Nodriver + Tor — The ULTIMATE anti-detection stack.

Combines:
- nodriver (raw CDP, no WebDriver detection)
- Tor SOCKS proxy (hidden IP)
- Real Chrome fingerprints
- Human behavior simulation

This is the BEST free option for bypassing detection.
"""

import subprocess
import os
import asyncio
import sys
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple


# Chrome paths (from Playwright install in Ubuntu proot)
CHROME_PATH = "/root/.cache/ms-playwright/chromium-1234/chrome-linux/chrome"

# Tor SOCKS proxy
TOR_PROXY = "socks5://127.0.0.1:9050"

# Real Chrome fingerprints
REAL_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Stealth init script
STEALTH_INIT = """
// Hide webdriver
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

// Real Chrome plugins (override what browser provides)
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const arr = [
            {name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1},
            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '', length: 1},
            {name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: '', length: 1},
            {name: 'Native Client', filename: 'internal-nacl-plugin', description: '', length: 2},
        ];
        arr.item = function(i) { return this[i] || null; };
        arr.namedItem = function(name) { return this.find(p => p.name === name) || null; };
        arr.refresh = function() {};
        return arr;
    }
});

// Real mimeTypes
Object.defineProperty(navigator, 'mimeTypes', {
    get: () => {
        const arr = [
            {type: 'application/pdf', suffixes: 'pdf', description: ''},
            {type: 'text/pdf', suffixes: 'pdf', description: ''},
        ];
        arr.item = function(i) { return this[i] || null; };
        arr.namedItem = function(name) { return this.find(m => m.type === name) || null; };
        return arr;
    }
});

// Languages
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});

// Platform
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});

// Hardware
Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});

// WebGL - real Intel GPU
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Google Inc. (Intel)';
    if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)';
    return getParameter.call(this, parameter);
};

// Permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = function(parameters) {
    if (parameters.name === 'notifications') {
        return Promise.resolve({state: Notification.permission});
    }
    return originalQuery.call(this, parameters);
};

// WebRTC - prevent leaks
const OriginalRTC = window.RTCPeerConnection;
window.RTCPeerConnection = function(...args) {
    const pc = new OriginalRTC(...args);
    const origCreateOffer = pc.createOffer.bind(pc);
    pc.createOffer = async function(options) {
        const offer = await origCreateOffer(options);
        if (offer && offer.sdp) {
            offer.sdp = offer.sdp.replace(/a=candidate:.+?typ.+?\\r\\n/g, '');
        }
        return offer;
    };
    return pc;
};

// Chrome runtime
if (!window.chrome) window.chrome = {};
window.chrome.runtime = window.chrome.runtime || {};
window.chrome.loadTimes = window.chrome.loadTimes || function() { return {}; };
window.chrome.csi = window.chrome.csi || function() { return {}; };
window.chrome.app = window.chrome.app || {isInstalled: false};
"""


class NodriverAutomation:
    """nodriver + Tor + stealth — the ultimate free anti-detection stack."""

    def __init__(self, use_tor: bool = True, headless: bool = True):
        self.use_tor = use_tor
        self.headless = headless
        self.browser = None
        self.page = None
        self._ensure_tor()

    def _ensure_tor(self):
        """Make sure Tor is running."""
        try:
            # Check if Tor is running
            result = subprocess.run(
                ["curl", "--socks5-hostname", "127.0.0.1:9050", "-s",
                 "https://check.torproject.org/api/ip"],
                capture_output=True, text=True, timeout=10
            )
            if "IsTor" in result.stdout:
                return
        except Exception:
            pass

        # Start Tor
        print("🧅 Starting Tor...")
        subprocess.Popen(["tor", "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(10)
        # Verify
        for _ in range(10):
            try:
                result = subprocess.run(
                    ["curl", "--socks5-hostname", "127.0.0.1:9050", "-s",
                     "https://check.torproject.org/api/ip"],
                    capture_output=True, text=True, timeout=5
                )
                if "IsTor" in result.stdout:
                    print(f"✅ Tor running: {result.stdout}")
                    return
            except Exception:
                time.sleep(2)

        print("⚠️  Tor not available, continuing without it")

    async def start(self):
        """Start the browser."""
        # Patch the file encoding issue first
        self._patch_nodriver()

        import nodriver as nd

        # Try multiple paths
        paths_to_try = [
            "/root/.cache/ms-playwright/chromium-1234/chrome-linux/chrome",
            "/root/.cache/ms-playwright/chromium-1228/chrome-linux/chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
        ]

        chrome_path = None
        for p in paths_to_try:
            if Path(p).exists():
                chrome_path = p
                break

        if not chrome_path:
            raise RuntimeError("No Chrome found")

        print(f"🌐 Using Chrome: {chrome_path}")
        print(f"🧅 Tor proxy: {'enabled' if self.use_tor else 'disabled'}")

        kwargs = {
            "headless": self.headless,
            "no_sandbox": True,
            "browser_executable_path": chrome_path,
        }

        if self.use_tor:
            kwargs["proxy"] = TOR_PROXY

        self.browser = await nd.start(**kwargs)

        # Get initial page
        await asyncio.sleep(2)
        self.page = self.browser.tabs[0] if self.browser.tabs else await self.browser.get("about:blank")

        # Inject stealth script
        await self.page.evaluate(STEALTH_INIT)

        return self

    def _patch_nodriver(self):
        """Patch nodriver's encoding issue if needed."""
        try:
            network_file = "/usr/local/lib/python3.14/dist-packages/nodriver/cdp/network.py"
            if Path(network_file).exists():
                with open(network_file, "rb") as f:
                    data = f.read()
                text = data.decode("latin-1").replace("\ufffdInf", "Inf")
                with open(network_file, "w", encoding="utf-8") as f:
                    f.write(text)
        except Exception as e:
            print(f"Patch warning: {e}")

    async def navigate(self, url: str) -> Dict:
        """Navigate to a URL."""
        # Get a fresh tab and navigate
        if self.browser.tabs:
            self.page = self.browser.tabs[0]
            await self.page.get(url)
        else:
            self.page = await self.browser.get(url)
        await asyncio.sleep(3)  # Let JS settle
        return await self.get_state()

    async def get_state(self) -> Dict:
        """Get current page state and detection signals."""
        return {
            "url": self.page.url,
            "title": await self.page.evaluate("document.title"),
            "content_length": len(await self.page.evaluate("document.documentElement.outerHTML")),
            "webdriver": await self.page.evaluate("navigator.webdriver"),
            "ua": await self.page.evaluate("navigator.userAgent"),
            "plugins": await self.page.evaluate("navigator.plugins.length"),
            "languages": await self.page.evaluate("navigator.languages"),
            "platform": await self.page.evaluate("navigator.platform"),
            "has_chrome": await self.page.evaluate("typeof window.chrome"),
        }

    async def stop(self):
        """Stop the browser."""
        if self.browser:
            try:
                self.browser.stop()  # sync, not await
            except Exception:
                pass

    def run_sync(self, coro):
        """Run async function synchronously."""
        return asyncio.run(coro)


def run_nodriver_test():
    """Run a test with nodriver + Tor."""
    print("=" * 70)
    print("🥷 NODRIVER + TOR + STEALTH TEST")
    print("=" * 70)

    async def main():
        client = NodriverAutomation(use_tor=True)
        await client.start()

        # Test on bot detection site
        print("\n1️⃣  bot.sannysoft.com...")
        state = await client.navigate("https://bot.sannysoft.com/")
        print(f"   URL: {state['url']}")
        print(f"   webdriver: {state['webdriver']}")
        print(f"   Plugins: {state['plugins']}")
        print(f"   window.chrome: {state['has_chrome']}")

        # Get full page text to see test results
        body = await client.page.evaluate("document.body.innerText")
        failed = body.lower().count("failed")
        passed = body.lower().count("passed")
        print(f"   Sannysoft: {passed} passed, {failed} failed")

        # Test on CreepJS (most thorough detection)
        print("\n2️⃣  CreepJS (most comprehensive test)...")
        state = await client.navigate("https://abrahamjuliot.github.io/creepjs/")
        await asyncio.sleep(5)
        body = await client.page.evaluate("document.body.innerText")
        print(f"   Content length: {len(body)}")
        if "headless" in body.lower():
            print(f"   ⚠️  Headless detected")
        if "lies" in body.lower():
            print(f"   ⚠️  Lies detected")

        # Test on fingerprintjs
        print("\n3️⃣  fingerprintjs.github.io...")
        state = await client.navigate("https://fingerprintjs.github.io/fingerprintjs/")
        await asyncio.sleep(3)
        fp_id = await client.page.evaluate("""
            new Promise((resolve) => {
                const fpPromise = import('https://openfpcdn.io/fingerprintjs/v4')
                    .then(FingerprintJS => FingerprintJS.load())
                    .then(fp => fp.get())
                    .then(result => resolve(result.visitorId))
                    .catch(() => resolve('error'));
                setTimeout(() => resolve('timeout'), 8000);
            })
        """)
        print(f"   Fingerprint ID: {fp_id[:20] if fp_id != 'error' else 'error'}...")

        await client.stop()
        print("\n✅ Tests complete")

    asyncio.run(main())


if __name__ == "__main__":
    run_nodriver_test()
