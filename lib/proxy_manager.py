#!/usr/bin/env python3
"""
Proxy Manager — fetch free proxies and rotate them.

Free proxies are often slow and unreliable but can help with rate limits.
For serious use, paid residential proxies are needed.
"""

import requests
import time
import random
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class Proxy:
    """A proxy server."""
    ip: str
    port: int
    protocol: str  # http, https, socks5
    country: Optional[str] = None
    last_check: Optional[float] = None
    working: bool = False


class ProxyManager:
    """Manage a pool of free proxies."""

    FREE_PROXY_SOURCES = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    ]

    def __init__(self):
        self.proxies: List[Proxy] = []
        self.last_refresh = 0
        self.refresh_interval = 300  # 5 min

    def refresh(self) -> List[Proxy]:
        """Fetch fresh list of free proxies."""
        print("🔄 Fetching free proxy list...")
        new_proxies = []

        for source in self.FREE_PROXY_SOURCES:
            try:
                r = requests.get(source, timeout=10)
                for line in r.text.strip().split('\n'):
                    line = line.strip()
                    if ':' in line and not line.startswith('#'):
                        try:
                            ip, port = line.split(':')
                            new_proxies.append(Proxy(
                                ip=ip, port=int(port), protocol='http'
                            ))
                        except Exception:
                            continue
            except Exception as e:
                print(f"   ⚠️  {source}: {e}")

        self.proxies = new_proxies
        self.last_refresh = time.time()
        print(f"   ✅ Loaded {len(self.proxies)} proxies")
        return new_proxies

    def get_random(self, refresh_if_empty: bool = True) -> Optional[Proxy]:
        """Get a random proxy from the pool."""
        if not self.proxies and refresh_if_empty:
            self.refresh()
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def get_dict(self, proxy: Proxy) -> Dict:
        """Convert to requests/httpx proxy dict."""
        url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
        return {"http://": url, "https://": url}


if __name__ == "__main__":
    pm = ProxyManager()
    proxies = pm.refresh()
    if proxies:
        p = pm.get_random()
        print(f"Sample proxy: {p.ip}:{p.port}")
    else:
        print("No proxies fetched")
