#!/usr/bin/env python3
"""
Creative Module — generates novel approaches when standard ones fail.

When conventional automation hits a wall, this module:
- Detects unusual form structures (drag-drop, canvas, file upload)
- Generates alternative field detection strategies
- Creates fallback forms (use OAuth when direct signup fails)
- Adapts based on platform (social, dev, e-commerce have different patterns)
- Finds hidden entry points (API endpoints, RSS, sitemap)

Think of it as "thinking outside the box" for the agent.
"""

import re
import json
import random
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin

import requests
from unified import SmartClient


@dataclass
class CreativeApproach:
    """A non-standard approach to try."""
    name: str
    description: str
    confidence: float  # 0.0-1.0
    steps: List[str]
    expected_outcome: str


class CreativeEngine:
    """Generate creative approaches for hard-to-automate platforms."""

    def __init__(self):
        self.client = SmartClient()

    def analyze_failure(self, url: str, error: str, page_html: str = "") -> List[CreativeApproach]:
        """Given a failed attempt, generate alternative approaches."""
        approaches = []

        # Detect why it failed
        page_text = page_html.lower() if page_html else ""
        error_lower = error.lower() if error else ""

        # 1. JS-rendered form?
        if 'react' in page_text or 'vue' in page_text or 'angular' in page_text:
            approaches.append(CreativeApproach(
                name="Jina Reader JS rendering",
                description="Use Jina Reader proxy which renders JavaScript",
                confidence=0.7,
                steps=[
                    f"Fetch via r.jina.ai proxy",
                    "Parse rendered HTML for inputs",
                    "Re-identify form fields",
                ],
                expected_outcome="Get the actual rendered form with all fields",
            ))

            approaches.append(CreativeApproach(
                name="Firecrawl browser mode",
                description="Use Firecrawl's cloud browser for full JS execution",
                confidence=0.85,
                steps=[
                    "firecrawl scrape URL --wait-for body --format html",
                    "Parse the rendered output",
                    "Find form fields and CSRF tokens",
                ],
                expected_outcome="Get fully rendered page with hidden fields",
            ))

        # 2. Anti-bot detected?
        if any(kw in page_text for kw in ['cloudflare', 'datadome', 'captcha', 'challenge']):
            approaches.append(CreativeApproach(
                name="Multi-layered stealth rotation",
                description="Rotate User-Agents + add realistic headers + delay",
                confidence=0.5,
                steps=[
                    "Generate fresh Fingerprint (UA, viewport, timezone)",
                    "Add Sec-CH-UA headers for Chrome 120+",
                    "Insert 3-7 second delay before request",
                    "Retry with stealth headers",
                ],
                expected_outcome="Pass basic bot detection",
            ))

            approaches.append(CreativeApproach(
                name="Google cache bypass",
                description="Use Google cache or Wayback Machine as proxy",
                confidence=0.6,
                steps=[
                    f"Try https://webcache.googleusercontent.com/search?q=cache:{url}",
                    f"Try https://web.archive.org/web/*/{url}",
                    "Parse cached version",
                ],
                expected_outcome="Get page content without triggering anti-bot",
            ))

        # 3. Phone-only verification?
        if any(kw in error_lower for kw in ['phone', 'sms', 'mobile']):
            approaches.append(CreativeApproach(
                name="OAuth fallback to email-only flow",
                description="Find OAuth provider that allows email signup",
                confidence=0.6,
                steps=[
                    "Detect OAuth providers (Google/GitHub/Facebook)",
                    "Use GitHub OAuth (often allows email-only)",
                    "Link OAuth to a freshly created GitHub account",
                ],
                expected_outcome="Bypass phone requirement via OAuth",
            ))

            approaches.append(CreativeApproach(
                name="Multiple free SMS numbers rotation",
                description="Try 5 different free SMS services in sequence",
                confidence=0.4,
                steps=[
                    "Try receive-smss.com first",
                    "Fallback to receivesms.co, quackr.io, etc.",
                    "Wait 30s between each for SMS delivery",
                ],
                expected_outcome="Get a number that accepts SMS for this platform",
            ))

        # 4. CAPTCHA blocker?
        if 'captcha' in page_text or 'captcha' in error_lower:
            approaches.append(CreativeApproach(
                name="Audio reCAPTCHA defeat with Whisper",
                description="If reCAPTCHA v2 with audio option, use Whisper STT",
                confidence=0.5,
                steps=[
                    "Find reCAPTCHA iframe",
                    "Switch to audio challenge",
                    "Download audio file",
                    "Transcribe with Whisper (local, free)",
                    "Submit transcribed text",
                ],
                expected_outcome="Solve reCAPTCHA v2 audio challenge for free",
            ))

            approaches.append(CreativeApproach(
                name="OCR image captcha with Tesseract",
                description="Use local Tesseract OCR for simple image CAPTCHAs",
                confidence=0.3,
                steps=[
                    "Download captcha image",
                    "Preprocess (grayscale + threshold)",
                    "Run Tesseract with character whitelist",
                    "Submit result (may need retries)",
                ],
                expected_outcome="Solve simple text-based CAPTCHAs",
            ))

            approaches.append(CreativeApproach(
                name="Find alternate non-captcha path",
                description="Look for hidden API endpoints or mobile app flows",
                confidence=0.5,
                steps=[
                    "Check robots.txt and sitemap.xml",
                    "Look for /api/, /v1/, /graphql endpoints",
                    "Try mobile app API (often less protected)",
                    "Check OAuth signup (no captcha usually)",
                ],
                expected_outcome="Find a less-protected path to register",
            ))

        # 5. Email blocked?
        if 'email' in error_lower and 'used' in error_lower:
            approaches.append(CreativeApproach(
                name="Email rotation across multiple services",
                description="Cycle through Mail.tm, GuerrillaMail, OpenInbox",
                confidence=0.7,
                steps=[
                    "Try Mail.tm first (persistent)",
                    "Fallback to GuerrillaMail",
                    "Try OpenInbox.io",
                    "Use disposable domain variations",
                ],
                expected_outcome="Get fresh email that platform accepts",
            ))

        # 6. 2FA / Phone required for verification?
        if '2fa' in page_text or 'two-factor' in page_text:
            approaches.append(CreativeApproach(
                name="Disable 2FA if optional during signup",
                description="Look for 'skip for now' or 'later' links",
                confidence=0.4,
                steps=[
                    "Look for skip/continue without 2FA option",
                    "Sometimes 2FA is set after first login",
                    "Check if OAuth providers bypass 2FA setup",
                ],
                expected_outcome="Register without immediate 2FA requirement",
            ))

        # 7. Always include: archive.org fallback
        approaches.append(CreativeApproach(
            name="Wayback Machine historical snapshot",
            description="Access cached/older version of the page",
            confidence=0.5,
            steps=[
                f"Fetch https://web.archive.org/web/2024*/url",
                "Try snapshots from different dates",
                "Older versions may have simpler forms",
            ],
            expected_outcome="Get a less-protected version of the page",
        ))

        # Sort by confidence
        approaches.sort(key=lambda a: a.confidence, reverse=True)
        return approaches

    def find_alternate_entry(self, url: str) -> Dict:
        """Find alternative ways to register/access a platform."""
        result = {"alternates": []}

        # Try /api, /v1, /signup.json
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        candidates = [
            f"{base}/api/signup",
            f"{base}/api/v1/register",
            f"{base}/api/users",
            f"{base}/auth/register",
            f"{base}/users/sign_up",
            f"{base}/v1/auth/register",
            f"{base}/.well-known/openid-configuration",  # OAuth discovery
        ]

        for endpoint in candidates:
            try:
                r = requests.get(endpoint, timeout=10)
                if r.status_code in [200, 405]:  # 405 = method not allowed = endpoint exists
                    result["alternates"].append({
                        "url": endpoint,
                        "status": r.status_code,
                        "hint": "Possible API endpoint",
                    })
            except Exception:
                continue

        # Check OAuth provider
        try:
            r = requests.get(url, timeout=10)
            oauth = re.findall(r'(?:sign[_-]in[_-]with|oauth[_-]?provider)[\s"]*?(\w+)', r.text, re.IGNORECASE)
            result["oauth_hints"] = list(set(oauth))
        except Exception:
            pass

        return result

    def generate_randomized_strategy(self) -> Dict:
        """Generate a randomized strategy that combines multiple approaches."""
        strategies = [
            "user_agent_rotation",
            "header_randomization",
            "timing_jitter",
            "request_order_shuffle",
            "field_name_variants",
        ]
        selected = random.sample(strategies, k=3)
        return {
            "selected": selected,
            "delay_range": (random.uniform(0.5, 3.0), random.uniform(3.0, 8.0)),
            "retry_count": random.randint(2, 5),
            "fallback_method": random.choice(["jina", "firecrawl", "cloudscraper", "wayback"]),
        }


if __name__ == "__main__":
    ce = CreativeEngine()
    print("🧠 Creative Engine ready")
    # Demo
    approaches = ce.analyze_failure(
        "https://github.com/signup",
        "403 Forbidden - anti-bot detected",
        "<html>Cloudflare challenge page</html>"
    )
    print(f"\nGenerated {len(approaches)} creative approaches for GitHub:")
    for a in approaches[:5]:
        print(f"  - [{a.confidence:.0%}] {a.name}")
        print(f"    {a.description}")
