#!/usr/bin/env python3
"""
Site Difficulty Rating — knows which platforms are easy vs hard to automate.

Each site gets scored 0-100 based on:
- Anti-bot protection (Cloudflare, DataDome, etc.)
- CAPTCHA presence
- Phone verification requirement
- JS rendering needed
- 2FA requirement
- Rate limiting
- Account approval workflow

Outputs a difficulty rating and recommended strategy.
"""

import re
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import json
from pathlib import Path

from unified import SmartClient


@dataclass
class DifficultyRating:
    """How hard is this site to automate?"""
    url: str
    domain: str
    score: int  # 0=easy, 100=impossible
    tier: str  # easy, medium, hard, extreme
    factors: Dict[str, int]  # what makes it hard
    recommended_strategy: str
    estimated_success_rate: float  # 0.0-1.0
    requires_paid_services: bool


class DifficultyScorer:
    """Score how hard a site is to automate."""

    # Known hard sites (heuristic)
    KNOWN_HARD_DOMAINS = {
        'google.com': 95, 'youtube.com': 90, 'facebook.com': 90,
        'instagram.com': 95, 'twitter.com': 95, 'x.com': 95,
        'tiktok.com': 95, 'linkedin.com': 85, 'pinterest.com': 80,
        'reddit.com': 75, 'amazon.com': 70,
        'github.com': 60, 'gitlab.com': 55,
        'stackoverflow.com': 50,
    }

    # Known easy sites
    KNOWN_EASY_DOMAINS = {
        'the-internet.herokuapp.com': 5,
        'httpbin.org': 0,
        'automationexercise.com': 15,
        'demoqa.com': 15,
        'guerrillamail.com': 10,
    }

    ANTI_BOT_SIGNATURES = [
        ('cloudflare', 15),
        ('datadome', 25),
        ('distil', 20),
        ('imperva', 20),
        ('perimeterx', 20),
        ('f5', 15),
        ('akamai', 20),
        ('kasada', 25),
        ('shape', 20),
        ('humansecurity', 20),
        ('cloudflare-turnstile', 15),
        ('cf-ray', 10),
    ]

    CAPTCHA_SIGNATURES = [
        ('recaptcha', 10),
        ('hcaptcha', 10),
        ('turnstile', 10),
        ('funcaptcha', 15),
        ('captcha-delivery', 10),
    ]

    JS_FRAMEWORKS = [
        ('react', 5),
        ('vue', 5),
        ('angular', 5),
        ('svelte', 5),
        ('next.js', 5),
        ('nuxt', 5),
    ]

    def __init__(self):
        self.client = SmartClient()
        self.cache_path = Path("~/.pi/skills/antidetect-stack/data/difficulty_cache.json").expanduser()
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache: Dict = self._load_cache()

    def _load_cache(self) -> Dict:
        if self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text())
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        self.cache_path.write_text(json.dumps(self.cache, indent=2))

    def score(self, url: str, force_refresh: bool = False) -> DifficultyRating:
        """Get difficulty rating for a URL."""
        domain = urlparse(url).netloc.replace('www.', '')

        # Check known sites
        if domain in self.KNOWN_EASY_DOMAINS and not force_refresh:
            score = self.KNOWN_EASY_DOMAINS[domain]
            return self._build_rating(url, domain, score, source="known_easy")
        if domain in self.KNOWN_HARD_DOMAINS and not force_refresh:
            score = self.KNOWN_HARD_DOMAINS[domain]
            return self._build_rating(url, domain, score, source="known_hard")

        # Check cache
        if domain in self.cache and not force_refresh:
            cached = self.cache[domain]
            if time.time() - cached.get('timestamp', 0) < 86400:  # 24h cache
                return self._build_rating(url, domain, cached['score'], source="cache")

        # Analyze page
        try:
            result = self.client.get(url, method="cloudscraper")
            html = result.text
        except Exception:
            try:
                result = self.client.get(url, method="jina")
                html = result.text
            except Exception:
                return self._build_rating(url, domain, 80, source="error")

        score = 0
        factors = {}

        # 1. Anti-bot detection
        for sig, points in self.ANTI_BOT_SIGNATURES:
            if sig in html.lower():
                score += points
                factors[f"antibot_{sig}"] = points

        # 2. CAPTCHA detection
        for sig, points in self.CAPTCHA_SIGNATURES:
            if sig in html.lower():
                score += points
                factors[f"captcha_{sig}"] = points

        # 3. JS rendering needed
        js_score = 0
        for sig, points in self.JS_FRAMEWORKS:
            if sig in html.lower():
                js_score += points
        if js_score > 0:
            factors["js_heavy"] = js_score
        score += js_score

        # 4. Phone required
        if re.search(r'type=["\']tel["\']|name=["\']phone["\']', html, re.IGNORECASE):
            score += 20
            factors["phone_required"] = 20

        # 5. 2FA likely
        if re.search(r'two[- ]?factor|2fa|authenticator', html, re.IGNORECASE):
            score += 10
            factors["likely_2fa"] = 10

        # 6. Form complexity (lots of fields = harder)
        inputs = re.findall(r'<input[^>]*name=', html, re.IGNORECASE)
        if len(inputs) > 10:
            score += 5
            factors["complex_form"] = 5

        # 7. Email-only signup bonus (easier)
        if re.search(r'type=["\']email["\']', html, re.IGNORECASE) and not re.search(r'type=["\']tel["\']', html, re.IGNORECASE):
            score -= 10  # email-only is easier
            factors["email_only_bonus"] = -10

        # Clamp to 0-100
        score = max(0, min(100, score))

        # Cache
        self.cache[domain] = {"score": score, "factors": factors, "timestamp": time.time()}
        self._save_cache()

        return self._build_rating(url, domain, score, factors, source="analysis")

    def _build_rating(self, url: str, domain: str, score: int,
                      factors: Optional[Dict] = None,
                      source: str = "") -> DifficultyRating:
        """Build a rating object."""
        factors = factors or {}

        # Determine tier
        if score < 25:
            tier = "easy"
            success_rate = 0.95
            strategy = "Use cloudscraper + mechanicalsoup directly. Free SMS/email work."
        elif score < 50:
            tier = "medium"
            success_rate = 0.7
            strategy = "Use cloudscraper + Jina fallback. May need Firecrawl browser mode."
        elif score < 75:
            tier = "hard"
            success_rate = 0.4
            strategy = "Use Firecrawl browser mode + paid CAPTCHA solver. OAuth preferred."
        else:
            tier = "extreme"
            success_rate = 0.1
            strategy = "Manual signup recommended. Or use paid residential proxies + anti-detect browser."

        return DifficultyRating(
            url=url,
            domain=domain,
            score=score,
            tier=tier,
            factors=factors,
            recommended_strategy=strategy,
            estimated_success_rate=success_rate,
            requires_paid_services=score >= 50,
        )

    def compare(self, urls: List[str]) -> List[DifficultyRating]:
        """Compare difficulty of multiple sites."""
        return [self.score(url) for url in urls]


if __name__ == "__main__":
    ds = DifficultyScorer()
    print("🎯 Site Difficulty Scorer")
    print()

    sites = [
        "https://automationexercise.com/signup",
        "https://dev.to/enter?signup=true",
        "https://github.com/signup",
        "https://stackoverflow.com/users/signup",
        "https://twitter.com/i/flow/signup",
    ]

    for url in sites:
        rating = ds.score(url)
        print(f"\n{url}")
        print(f"  Score: {rating.score}/100 ({rating.tier})")
        print(f"  Success rate: {rating.estimated_success_rate:.0%}")
        print(f"  Strategy: {rating.recommended_strategy[:80]}")
        print(f"  Paid services needed: {rating.requires_paid_services}")
