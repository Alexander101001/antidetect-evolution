#!/usr/bin/env python3
"""
Unified Anti-Detect Stack — pi skill
Combines 10 free Termux-compatible tools into one smart HTTP client.

Usage:
    from unified import SmartClient
    client = SmartClient()
    r = client.get("https://protected-site.com")
    print(r.text)
"""

import random
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Tool 1-2: HTTP clients
import httpx
import requests

# Tool 3: UA rotation
import fake_useragent

# Tool 4: Cloudflare bypass
import cloudscraper

# Tool 5: Form/cookie handling
import mechanicalsoup

# Tool 6: RSS/Atom feeds
import feedparser

# Tool 7: HTML→Markdown
import html2text

# Tool 8: Google search
try:
    from googlesearch import search as google_search
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


@dataclass
class FetchResult:
    url: str
    status: int
    text: str
    markdown: str
    method_used: str
    elapsed: float
    cookies: Dict[str, str]


class SmartClient:
    """
    Auto-picks the best tool for each request.
    Falls back through chains if one fails.
    """

    def __init__(self, stealth: bool = True):
        self.stealth = stealth
        self.ua_gen = fake_useragent.UserAgent()
        self.session_cookies = {}
        self.cf_scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'android', 'mobile': True}
        )

    def _random_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': self.ua_gen.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'zh-CN,zh;q=0.9',
                'en-GB,en;q=0.9',
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get(self, url: str, method: str = "auto", **kwargs) -> FetchResult:
        """Fetch URL with auto-fallback through tool chain."""
        start = time.time()
        methods_to_try = ["cloudscraper", "httpx", "requests", "jina"] if method == "auto" else [method]

        last_err = None
        for m in methods_to_try:
            try:
                if m == "cloudscraper":
                    r = self.cf_scraper.get(url, headers=self._random_headers(), timeout=30, **kwargs)
                    return self._make_result(url, r, "cloudscraper", start, dict(r.cookies))
                elif m == "httpx":
                    with httpx.Client(http2=True, headers=self._random_headers(), follow_redirects=True) as client:
                        r = client.get(url, timeout=30, **kwargs)
                        return self._make_result(url, r, "httpx[http2]", start, dict(r.cookies))
                elif m == "requests":
                    r = requests.get(url, headers=self._random_headers(), timeout=30, **kwargs)
                    return self._make_result(url, r, "requests", start, dict(r.cookies))
                elif m == "jina":
                    jina_url = f"https://r.jina.ai/{url}"
                    r = requests.get(jina_url, headers={"X-Return-Format": "markdown"}, timeout=30)
                    if r.status_code == 200:
                        return FetchResult(url=url, status=200, text=r.text, markdown=r.text, method_used="jina", elapsed=time.time()-start, cookies={})
                    else:
                        last_err = f"Jina returned {r.status_code}"
                        continue
            except Exception as e:
                last_err = e
                continue

        # Graceful failure — return empty result instead of raising
        return FetchResult(
            url=url,
            status=0,
            text=f"[Failed to fetch: {last_err}]",
            markdown=f"[Failed to fetch: {last_err}]",
            method_used="none",
            elapsed=time.time() - start,
            cookies={},
        )

    def _make_result(self, url, r, method, start, cookies) -> FetchResult:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        text = r.text if hasattr(r, 'text') else str(r.content)
        return FetchResult(
            url=url,
            status=r.status_code,
            text=text,
            markdown=h.handle(text),
            method_used=method,
            elapsed=time.time() - start,
            cookies=cookies,
        )

    def fill_form(self, url: str, submit_url: Optional[str] = None) -> mechanicalsoup.StatefulBrowser:
        """Open a page with form-filling capability."""
        browser = mechanicalsoup.StatefulBrowser(
            user_agent=self.ua_gen.random,
            soup_config={'features': 'lxml'}
        )
        browser.open(url)
        return browser

    def read_rss(self, feed_url: str):
        """Parse any RSS/Atom feed."""
        return feedparser.parse(feed_url)

    def google(self, query: str, num_results: int = 10):
        """Google search via googlesearch-python."""
        if not HAS_GOOGLE:
            raise RuntimeError("googlesearch-python not available")
        return list(google_search(query, num_results=num_results))

    def stealth_delay(self):
        """Human-like random delay."""
        time.sleep(random.uniform(0.5, 2.5))


# Quick CLI interface
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: unified.py <url> [method]")
        sys.exit(1)

    url = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "auto"

    client = SmartClient()
    result = client.get(url, method=method)
    print(f"✅ Fetched via {result.method_used} in {result.elapsed:.2f}s")
    print(f"   Status: {result.status}")
    print(f"   Size: {len(result.markdown)} chars markdown")
    print("---")
    print(result.markdown[:2000])
