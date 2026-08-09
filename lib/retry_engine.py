#!/usr/bin/env python3
"""
Retry Engine — tries multiple strategies before giving up.

When a single approach fails, automatically tries:
1. Different HTTP methods (cloudscraper → httpx → jina → firecrawl)
2. Different fingerprint (rotating UA/headers)
3. Different timing (varying delays)
4. Different submission approach (requests vs mechanicalsoup)
5. Different proxy (when available)

This is what makes the skill "creative" — it doesn't give up after one failure.
"""

import time
import random
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass

from unified import SmartClient
from stealth import HumanBehavior, Fingerprint
from creative import CreativeEngine


@dataclass
class RetryAttempt:
    """One retry attempt."""
    strategy: str
    success: bool
    error: Optional[str]
    elapsed: float
    response_size: int = 0


@dataclass
class RetryResult:
    """Final retry result."""
    success: bool
    total_attempts: int
    successful_strategy: Optional[str]
    final_response: Optional[object]
    attempts: List[RetryAttempt]
    creative_approaches: List[str]


class RetryEngine:
    """Try multiple strategies with exponential backoff."""

    def __init__(self):
        self.client = SmartClient()
        self.human = HumanBehavior()
        self.creative = CreativeEngine()

    def fetch_with_retry(self, url: str, max_attempts: int = 5) -> RetryResult:
        """
        Try multiple strategies to fetch a URL.
        """
        attempts = []

        strategies = [
            ("cloudscraper", lambda: self.client.get(url, method="cloudscraper")),
            ("httpx", lambda: self.client.get(url, method="httpx")),
            ("requests", lambda: self.client.get(url, method="requests")),
            ("jina", lambda: self.client.get(url, method="jina")),
            ("wayback", lambda: self._wayback_fetch(url)),
        ]

        for i, (name, fn) in enumerate(strategies[:max_attempts]):
            start = time.time()
            try:
                response = fn()
                elapsed = time.time() - start
                success = response.status == 200 and len(response.text) > 100

                attempts.append(RetryAttempt(
                    strategy=name,
                    success=success,
                    error=None if success else f"Status {response.status}, size {len(response.text)}",
                    elapsed=elapsed,
                    response_size=len(response.text),
                ))

                if success:
                    return RetryResult(
                        success=True,
                        total_attempts=i + 1,
                        successful_strategy=name,
                        final_response=response,
                        attempts=attempts,
                        creative_approaches=[],
                    )
            except Exception as e:
                elapsed = time.time() - start
                attempts.append(RetryAttempt(
                    strategy=name,
                    success=False,
                    error=str(e)[:200],
                    elapsed=elapsed,
                ))

            # Backoff between attempts
            if i < max_attempts - 1:
                backoff = random.uniform(1.0, 3.0) * (i + 1)
                time.sleep(backoff)

        # All failed — get creative approaches
        last_error = attempts[-1].error if attempts else "unknown"
        creative = self.creative.analyze_failure(url, last_error)

        return RetryResult(
            success=False,
            total_attempts=len(attempts),
            successful_strategy=None,
            final_response=None,
            attempts=attempts,
            creative_approaches=[a.name for a in creative],
        )

    def _wayback_fetch(self, url: str):
        """Try Wayback Machine for blocked content."""
        from unified import FetchResult
        try:
            r = self.client.session.get(
                f"https://web.archive.org/web/2024/{url}",
                timeout=20,
            )
            if r.status_code == 200:
                return FetchResult(
                    url=url,
                    status=r.status_code,
                    text=r.text,
                    markdown=r.text,
                    method_used="wayback",
                    elapsed=0,
                    cookies={},
                )
            # Return empty result instead of raising
            return FetchResult(
                url=url,
                status=r.status_code,
                text=f"[Wayback returned {r.status_code}]",
                markdown=f"[Wayback returned {r.status_code}]",
                method_used="wayback_failed",
                elapsed=0,
                cookies={},
            )
        except Exception as e:
            return FetchResult(
                url=url,
                status=0,
                text=f"[Wayback failed: {e}]",
                markdown=f"[Wayback failed: {e}]",
                method_used="wayback_error",
                elapsed=0,
                cookies={},
            )


if __name__ == "__main__":
    re_eng = RetryEngine()

    print("=" * 70)
    print("TEST: Retry engine on a hard site (GitHub)")
    print("=" * 70)

    result = re_eng.fetch_with_retry("https://github.com/signup", max_attempts=4)

    print(f"\nResult: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"Total attempts: {result.total_attempts}")
    if result.successful_strategy:
        print(f"Winning strategy: {result.successful_strategy}")
    print(f"\nAttempt log:")
    for a in result.attempts:
        status = "✅" if a.success else "❌"
        print(f"  {status} {a.strategy}: {a.elapsed:.2f}s, {a.response_size} bytes")
        if a.error:
            print(f"      Error: {a.error[:80]}")

    if result.creative_approaches:
        print(f"\nCreative approaches to try next:")
        for ca in result.creative_approaches:
            print(f"  💡 {ca}")
