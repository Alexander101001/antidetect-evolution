#!/usr/bin/env python3
"""
Stealth module — human-behavior simulation
Makes automation look like a real person browsing.
"""

import random
import time
import string
from typing import Optional


class HumanBehavior:
    """Simulate realistic human browsing patterns."""

    @staticmethod
    def delay(min_s: float = 0.5, max_s: float = 2.5):
        """Random delay like a human reading/thinking."""
        time.sleep(random.uniform(min_s, max_s))

    @staticmethod
    def short_delay():
        """Short delay between rapid actions."""
        time.sleep(random.uniform(0.1, 0.4))

    @staticmethod
    def long_delay():
        """Long delay like reading content."""
        time.sleep(random.uniform(2.0, 6.0))

    @staticmethod
    def type_delay(text: str) -> float:
        """Simulate typing speed (~40 wpm average)."""
        per_char = random.uniform(0.05, 0.18)
        time.sleep(per_char * len(text))
        return per_char * len(text)

    @staticmethod
    def random_username(prefix: str = "user", length: int = 8) -> str:
        """Generate a believable username."""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"{prefix}_{suffix}"

    @staticmethod
    def random_email(domain: Optional[str] = None) -> str:
        """Generate a believable email."""
        first = random.choice(['alex', 'sam', 'jordan', 'taylor', 'casey', 'morgan', 'riley', 'jamie'])
        last = random.choice(['smith', 'jones', 'lee', 'patel', 'wang', 'garcia', 'kim'])
        year = random.randint(1985, 2005)
        domains = domain and [domain] or ['gmail.com', 'outlook.com', 'proton.me', 'yahoo.com']
        return f"{first}.{last}{year}@{random.choice(domains)}"

    @staticmethod
    def strong_password(length: int = 16) -> str:
        """Generate a strong password meeting most policy requirements."""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        # Ensure at least one of each category
        pwd = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*"),
        ]
        pwd += random.choices(chars, k=length - 4)
        random.shuffle(pwd)
        return ''.join(pwd)

    @staticmethod
    def realistic_name() -> dict:
        """Generate a believable full name."""
        firsts = ['Alex', 'Sam', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Jamie',
                  'Avery', 'Quinn', 'Drew', 'Reese', 'Skyler', 'Hayden']
        lasts = ['Smith', 'Jones', 'Lee', 'Patel', 'Wang', 'Garcia', 'Kim', 'Brown',
                 'Davis', 'Miller', 'Wilson', 'Anderson', 'Thomas']
        return {
            'first': random.choice(firsts),
            'last': random.choice(lasts),
            'full': f"{random.choice(firsts)} {random.choice(lasts)}",
        }


class Fingerprint:
    """Browser fingerprint consistency (kept across session)."""

    def __init__(self):
        self.user_agent = self._random_ua()
        self.accept_lang = random.choice([
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'zh-CN,zh;q=0.9,en;q=0.8',
            'en-US,en;q=0.9,fr;q=0.8',
        ])
        self.platform = random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"'])
        self.viewport = random.choice([
            (1920, 1080), (1366, 768), (1536, 864),
            (1440, 900), (390, 844),  # mobile
        ])
        self.timezone = random.choice([
            'America/New_York', 'Europe/London', 'Asia/Shanghai',
            'Asia/Tokyo', 'Europe/Berlin', 'America/Los_Angeles',
        ])

    def _random_ua(self) -> str:
        """Realistic Chrome/Firefox/Safari UA."""
        chrome_v = random.randint(120, 140)
        return (
            f"Mozilla/5.0 ({random.choice(['Windows NT 10.0; Win64; x64', 'Macintosh; Intel Mac OS X 10_15_7', 'X11; Linux x86_64'])}) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_v}.0.0.0 Safari/537.36"
        )

    def headers(self) -> dict:
        """Build consistent header set."""
        return {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': self.accept_lang,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-CH-UA': f'"Chromium";v="{chrome_v}", "Not(A:Brand";v="24", "Google Chrome";v="{chrome_v}"' if False else f'"Chromium";v="{random.randint(120,140)}"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': self.platform,
        }
