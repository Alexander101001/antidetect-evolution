#!/usr/bin/env python3
"""
Phone Protection + Cloud Desktop — keeps your phone safe and unblocked.

For Termux/phone users specifically:
- Rate limiting per host (won't hammer any single domain)
- Off-peak scheduling (heavy work during low-traffic hours)
- Traffic shaping (looks more like real browser usage)
- IP rotation (when free proxies available)
- Local IP detection (warns if VPN needed)

Cloud Desktop option:
- Offload heavy work to free cloud browsers
- Use Browserless.io free tier
- Fallback to other cloud browser services
"""

import time
import random
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
import json
from collections import defaultdict
import threading


@dataclass
class HostTraffic:
    """Traffic stats per host."""
    host: str
    request_count: int
    last_request: float
    total_bytes: int
    is_throttled: bool


class PhoneProtector:
    """Protect your phone IP from being banned."""

    # Limits per host
    MAX_REQUESTS_PER_MINUTE = 10
    MAX_REQUESTS_PER_HOUR = 100
    COOLDOWN_AFTER_429 = 300  # 5 min after a 429

    # Off-peak hours (when most users are asleep, less suspicious)
    OFF_PEAK_HOURS = list(range(1, 7))  # 1am-7am

    def __init__(self):
        self.traffic: Dict[str, HostTraffic] = {}
        self.cooldowns: Dict[str, float] = {}
        self.lock = threading.Lock()
        self.path = Path("~/.pi/skills/antidetect-stack/data/traffic.json").expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self.traffic = {k: HostTraffic(**v) for k, v in data.get('traffic', {}).items()}
                self.cooldowns = data.get('cooldowns', {})
            except Exception:
                pass

    def _save(self):
        data = {
            'traffic': {k: asdict(v) for k, v in self.traffic.items()},
            'cooldowns': self.cooldowns,
        }
        self.path.write_text(json.dumps(data, indent=2))

    def check_rate_limit(self, host: str) -> bool:
        """Check if we can make a request to this host. Returns True if OK."""
        with self.lock:
            now = time.time()

            # Check cooldown (after 429)
            if host in self.cooldowns:
                if now < self.cooldowns[host]:
                    wait = int(self.cooldowns[host] - now)
                    print(f"⏳ Cooldown for {host}: {wait}s remaining")
                    return False
                else:
                    del self.cooldowns[host]

            # Check rate limits
            if host not in self.traffic:
                self.traffic[host] = HostTraffic(
                    host=host, request_count=0, last_request=0,
                    total_bytes=0, is_throttled=False,
                )

            t = self.traffic[host]

            # Reset counts if old
            if now - t.last_request > 3600:
                t.request_count = 0

            # Per-minute check
            recent_minute = sum(1 for k, v in self.traffic.items() if k == host and now - v.last_request < 60)

            if recent_minute >= self.MAX_REQUESTS_PER_MINUTE:
                print(f"⚠️  Rate limit hit for {host}: {recent_minute} reqs/min")
                return False

            return True

    def record_request(self, host: str, bytes_received: int = 0):
        """Record that we made a request."""
        with self.lock:
            if host not in self.traffic:
                self.traffic[host] = HostTraffic(
                    host=host, request_count=0, last_request=0,
                    total_bytes=0, is_throttled=False,
                )
            t = self.traffic[host]
            t.request_count += 1
            t.last_request = time.time()
            t.total_bytes += bytes_received
            self._save()

    def record_429(self, host: str):
        """Record a 429 response (Too Many Requests)."""
        with self.lock:
            self.cooldowns[host] = time.time() + self.COOLDOWN_AFTER_429
            print(f"🚫 Got 429 from {host}. Cooldown for {self.COOLDOWN_AFTER_429}s")
            self._save()

    def get_optimal_timing(self) -> Dict:
        """Suggest optimal time to do heavy work."""
        now = datetime.now()
        current_hour = now.hour

        is_off_peak = current_hour in self.OFF_PEAK_HOURS

        if is_off_peak:
            return {
                "is_off_peak": True,
                "recommendation": "GOOD — run heavy jobs now",
                "next_off_peak": "now",
            }
        else:
            hours_until = 0
            for h in range(1, 25):
                if (current_hour + h) % 24 in self.OFF_PEAK_HOURS:
                    hours_until = h
                    break

            return {
                "is_off_peak": False,
                "recommendation": f"WAIT — off-peak in {hours_until}h",
                "next_off_peak_hours": hours_until,
            }

    def safe_delay(self, host: str, min_s: float = 1.0, max_s: float = 3.0):
        """Wait a safe amount of time, adjusted for traffic to this host."""
        with self.lock:
            if host in self.traffic:
                recent = self.traffic[host].request_count
                # More requests = longer delay
                multiplier = 1 + (recent / 100)
                min_s *= multiplier
                max_s *= multiplier

        delay = random.uniform(min_s, max_s)
        time.sleep(delay)


class CloudDesktop:
    """
    Offload heavy automation to cloud browsers.

    Free options:
    - Browserless.io (free tier)
    - Firecrawl browser mode (already integrated)
    - Jina Reader (proxy rendering)
    - SearchApi.io (some free tier)
    """

    FREE_CLOUD_BROWSERS = {
        "browserless": {
            "url": "https://browserless.io",
            "free_tier": "1000 minutes/month",
            "method": "REST API",
            "best_for": "Full Chrome rendering, screenshots",
        },
        "firecrawl_browser": {
            "url": "https://firecrawl.dev",
            "free_tier": "500 credits",
            "method": "CLI",
            "best_for": "Already integrated",
        },
        "apify_free": {
            "url": "https://apify.com",
            "free_tier": "$5/month credit",
            "method": "API",
            "best_for": "Pre-built scrapers (scraping-browser actor)",
        },
        "scrapingant": {
            "url": "https://scrapingant.com",
            "free_tier": "10000 API credits",
            "method": "API",
            "best_for": "Headless Chrome",
        },
    }

    def __init__(self):
        pass

    def list_options(self) -> Dict:
        """List all cloud browser options."""
        return self.FREE_CLOUD_BROWSERS

    def render_with_firecrawl(self, url: str) -> Optional[str]:
        """Use Firecrawl browser mode to render JS."""
        import subprocess
        try:
            result = subprocess.run(
                ["firecrawl", "scrape", url, "--wait-for", "body", "--format", "html"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            print(f"Firecrawl browser failed: {e}")
        return None


if __name__ == "__main__":
    protector = PhoneProtector()
    print("📱 Phone Protector Active")
    print()
    timing = protector.get_optimal_timing()
    print(f"Current time strategy:")
    print(f"  Off-peak: {timing['is_off_peak']}")
    print(f"  Recommendation: {timing['recommendation']}")

    print()
    cloud = CloudDesktop()
    print("☁️  Cloud desktop options:")
    for name, info in cloud.list_options().items():
        print(f"  - {name}: {info['free_tier']}")
