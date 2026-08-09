#!/usr/bin/env python3
"""
Researcher module — search, read, learn from platforms.
This is how the agent 'studies' how each platform works.
"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from unified import SmartClient, FetchResult
from stealth import HumanBehavior


@dataclass
class Article:
    """A research article/page discovered."""
    url: str
    title: str
    excerpt: str
    platform: str
    tags: List[str]
    author: Optional[str] = None
    published: Optional[str] = None
    read_time_min: Optional[float] = None


class Researcher:
    """Search and read articles across multiple platforms."""

    def __init__(self, client: Optional[SmartClient] = None):
        self.client = client or SmartClient()
        self.human = HumanBehavior()
        self.learned_patterns = {}  # platform -> form schema

    def google_search(self, query: str, num: int = 10) -> List[str]:
        """Search Google for a topic."""
        try:
            return list(self.client.google(query, num_results=num))
        except Exception:
            return []

    def fetch_article(self, url: str) -> Optional[Article]:
        """Fetch and parse a single article."""
        try:
            result = self.client.get(url)
            article = self._parse_article(result.text, url)
            return article
        except Exception as e:
            print(f"[!] Failed to fetch {url}: {e}")
            return None

    def _parse_article(self, html: str, url: str) -> Article:
        """Extract title/excerpt/tags from raw HTML."""
        # Title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else url
        title = re.sub(r'\s+', ' ', title)[:200]

        # Meta description
        desc_match = re.search(
            r'<meta\s+(?:name|property)=["\'](?:description|og:description)["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        excerpt = desc_match.group(1) if desc_match else ""

        # Tags from keywords meta
        tags_match = re.search(
            r'<meta\s+name=["\']keywords["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []

        # Author
        author_match = re.search(
            r'<meta\s+(?:name|property)=["\']author["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        author = author_match.group(1) if author_match else None

        # Platform detection
        platform = self._detect_platform(url)

        return Article(
            url=url, title=title, excerpt=excerpt,
            platform=platform, tags=tags, author=author
        )

    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL."""
        domains = {
            'medium.com': 'Medium',
            'dev.to': 'Dev.to',
            'reddit.com': 'Reddit',
            'news.ycombinator.com': 'Hacker News',
            'github.com': 'GitHub',
            'huggingface.co': 'Hugging Face',
            'arxiv.org': 'arXiv',
            'stackoverflow.com': 'Stack Overflow',
            'substack.com': 'Substack',
            'hashnode.com': 'Hashnode',
            'hackernoon.com': 'HackerNoon',
        }
        for d, name in domains.items():
            if d in url:
                return name
        return "Web"

    def study_platform(self, url: str) -> Dict:
        """
        Learn how a platform works by analyzing its signup/login page.
        This is the 'learning' feature — we discover the form structure.
        """
        try:
            result = self.client.get(url)
        except Exception as e:
            return {"error": str(e), "url": url}

        # Find all forms
        forms = re.findall(
            r'<form[^>]*>(.*?)</form>',
            result.text,
            re.DOTALL | re.IGNORECASE
        )

        # Find all input fields
        inputs = re.findall(
            r'<input[^>]*(?:name|id|type|placeholder|required)=["\']([^"\']*)["\']',
            result.text,
            re.IGNORECASE
        )

        # Find CSRF tokens
        csrf = re.findall(
            r'<input[^>]*name=["\'](?:csrf[_\-]?token|_token|authenticity_token)["\'][^>]*value=["\']([^"\']*)["\']',
            result.text,
            re.IGNORECASE
        )

        platform = self._detect_platform(url)

        pattern = {
            "platform": platform,
            "url": url,
            "forms_count": len(forms),
            "input_fields": inputs,
            "csrf_tokens": csrf,
            "has_captcha": bool(re.search(r'captcha|hcaptcha|recaptcha|turnstile', result.text, re.IGNORECASE)),
            "has_email_signup": bool(re.search(r'type=["\']email["\']', result.text, re.IGNORECASE)),
            "has_oauth": bool(re.search(r'oauth|google.*sign|sign.*with.*google|github.*sign', result.text, re.IGNORECASE)),
        }

        # Cache learned pattern
        self.learned_patterns[platform] = pattern
        return pattern

    def research_topic(self, topic: str, max_articles: int = 5) -> List[Article]:
        """Research a topic: search → fetch top results → summarize."""
        print(f"[research] Searching for: {topic}")
        urls = self.google_search(topic, num=max_articles * 2)
        articles = []
        for url in urls[:max_articles]:
            self.human.delay(1, 3)  # human-like pause
            art = self.fetch_article(url)
            if art:
                articles.append(art)
        return articles

    def export_knowledge(self) -> str:
        """Export learned platform patterns as JSON."""
        return json.dumps(self.learned_patterns, indent=2, default=str)
