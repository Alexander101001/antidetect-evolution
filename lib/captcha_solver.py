#!/usr/bin/env python3
"""
CAPTCHA solver module.

For testing purposes only. CAPTCHA solving services are paid.
This module is a framework — without an API key, it cannot actually solve.

Approach priority:
1. Avoid CAPTCHA — use stealth to never trigger it
2. Use 2captcha API (paid, ~$3/1000 reCAPTCHA v2)
3. Use anti-captcha API (paid, similar)
4. Audio fallback (free, manual)

For legitimate testing on dev sites, CAPTCHAs are rare.
"""

import os
import re
import time
from typing import Optional, Dict
from dataclasses import dataclass
from unified import SmartClient


@dataclass
class CaptchaChallenge:
    """Detected CAPTCHA challenge."""
    type: str  # recaptcha_v2, hcaptcha, turnstile, image
    site_key: Optional[str]
    page_url: str
    detected_at: float


class CaptchaDetector:
    """Detect what type of CAPTCHA is on a page."""

    TYPES = {
        "recaptcha_v2": r'(?:data-sitekey|grecaptcha)[^>]*?["\']([A-Za-z0-9_-]{40})["\']',
        "hcaptcha": r'hcaptcha[^>]*?data-sitekey=["\']([A-Za-z0-9_-]{36})["\']',
        "turnstile": r'cf-turnstile[^>]*?data-sitekey=["\']([A-Za-z0-9_-]{36})["\']',
        "funcaptcha": r'arkose[^>]*?data-sitekey=["\']([A-Za-z0-9_-]{36})["\']',
    }

    def __init__(self):
        self.client = SmartClient()

    def detect(self, url: str) -> Optional[CaptchaChallenge]:
        """Detect CAPTCHA on a URL."""
        result = self.client.get(url)
        html = result.text

        for ctype, pattern in self.TYPES.items():
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return CaptchaChallenge(
                    type=ctype,
                    site_key=match.group(1),
                    page_url=url,
                    detected_at=time.time(),
                )
        return None

    def has_captcha(self, html: str) -> bool:
        """Quick check if HTML contains any captcha."""
        return any(re.search(p, html, re.IGNORECASE) for p in self.TYPES.values())


class CaptchaSolver:
    """
    Framework for solving CAPTCHAs.

    Without an API key in environment variables, this will:
    - Try to bypass via stealth (browser fingerprint, headers)
    - Use audio fallback if available
    - Return None if cannot solve (caller should retry or use captcha-free path)
    """

    PROVIDERS = {
        "2captcha": {
            "url": "https://2captcha.com",
            "env_key": "CAPTCHA_2CAPTCHA_KEY",
            "cost": "$2.99/1000 reCAPTCHA v2",
            "speed": "~30 seconds",
        },
        "anticaptcha": {
            "url": "https://anti-captcha.com",
            "env_key": "CAPTCHA_ANTICAPTCHA_KEY",
            "cost": "$2.00/1000 reCAPTCHA v2",
            "speed": "~30 seconds",
        },
        "capsolver": {
            "url": "https://capsolver.com",
            "env_key": "CAPTCHA_CAPSOLVER_KEY",
            "cost": "$0.80/1000 reCAPTCHA v2",
            "speed": "~10 seconds",
        },
    }

    def __init__(self):
        self.client = SmartClient()

    def has_api_key(self, provider: str = "2captcha") -> bool:
        """Check if a paid API key is configured."""
        env_key = self.PROVIDERS[provider]["env_key"]
        return bool(os.environ.get(env_key))

    def solve_2captcha(self, challenge: CaptchaChallenge) -> Optional[str]:
        """
        Solve via 2captcha API. Requires CAPTCHA_2CAPTCHA_KEY env var.
        Docs: https://2captcha.com/2captcha-api
        """
        api_key = os.environ.get("CAPTCHA_2CAPTCHA_KEY")
        if not api_key:
            print("❌ No 2captcha key. Set CAPTCHA_2CAPTCHA_KEY env var.")
            return None

        # Submit
        submit = self.client.session.post("https://2captcha.com/in.php", data={
            "key": api_key,
            "method": "userrecaptcha",
            "googlekey": challenge.site_key,
            "pageurl": challenge.page_url,
            "json": 1,
        }).json()

        if submit.get("status") != 1:
            print(f"❌ Submit failed: {submit}")
            return None

        captcha_id = submit["request"]
        print(f"📤 Submitted {challenge.type}, id: {captcha_id}")

        # Poll for solution
        for _ in range(60):
            time.sleep(5)
            result = self.client.session.get(
                f"https://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1"
            ).json()
            if result.get("status") == 1:
                print(f"✅ Solved!")
                return result["request"]
            elif result.get("error_text"):
                print(f"❌ Error: {result['error_text']}")
                return None

        print("⚠️  Timeout waiting for solution")
        return None

    def bypass_stealth(self, url: str) -> bool:
        """
        Try to bypass CAPTCHA using stealth techniques alone (free).
        Returns True if bypassed (page loaded without captcha challenge).
        """
        # 1. Use cloudscraper (handles Cloudflare's IUAM challenge)
        try:
            result = self.client.get(url, method="cloudscraper")
            if not self.client.client.has_captcha(result.text):
                print("✅ Bypassed via cloudscraper (Cloudflare)")
                return True
        except Exception:
            pass

        # 2. Try with different UA + headers
        try:
            result = self.client.get(url, method="jina")
            if not self.client.client.has_captcha(result.text):
                print("✅ Bypassed via Jina proxy")
                return True
        except Exception:
            pass

        print("❌ Cannot bypass stealth alone")
        return False


# Audio fallback (free, manual)
class AudioCaptchaHelper:
    """
    For image CAPTCHAs that have audio versions.
    Requires manual intervention OR speech-to-text API.
    """

    @staticmethod
    def has_audio(page_html: str) -> bool:
        return bool(re.search(r'audio["\s]*challenge|type["\s]*=["\']audio', page_html, re.IGNORECASE))


if __name__ == "__main__":
    print("🔍 Testing CAPTCHA detection...")
    detector = CaptchaDetector()
    test_urls = [
        "https://the-internet.herokuapp.com/login",  # no captcha
        "https://www.google.com/recaptcha/api2/demo",  # has recaptcha
    ]
    for url in test_urls:
        try:
            challenge = detector.detect(url)
            if challenge:
                print(f"✅ {url}: {challenge.type}, key={challenge.site_key[:20]}...")
            else:
                print(f"✅ {url}: no CAPTCHA detected")
        except Exception as e:
            print(f"❌ {url}: {e}")
