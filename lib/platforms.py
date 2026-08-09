#!/usr/bin/env python3
"""
Platforms module — known recipes for popular platforms.
Each platform has: signup URL, required fields, login URL, content search URL.
"""

PLATFORMS = {
    "medium": {
        "name": "Medium",
        "signup_url": "https://medium.com/m/signin?operation=register",
        "login_url": "https://medium.com/m/signin",
        "search_url": "https://medium.com/search?q={query}",
        "feed_url": "https://medium.com/feed/tag/{tag}",
        "required_fields": ["email", "password", "name"],
        "oauth": ["google", "facebook", "apple"],
        "notes": "Email signup requires email verification. Google OAuth is fastest.",
    },
    "dev_to": {
        "name": "DEV.to",
        "signup_url": "https://dev.to/enter?signup=true",
        "login_url": "https://dev.to/enter",
        "search_url": "https://dev.to/search?q={query}",
        "feed_url": "https://dev.to/feed",
        "api_url": "https://dev.to/api/",
        "required_fields": ["email", "password", "name", "username"],
        "oauth": ["github", "twitter", "apple"],
        "notes": "GitHub OAuth is the easiest. API is well-documented and open.",
    },
    "reddit": {
        "name": "Reddit",
        "signup_url": "https://www.reddit.com/register/",
        "login_url": "https://www.reddit.com/login/",
        "search_url": "https://www.reddit.com/search/?q={query}",
        "feed_url": "https://www.reddit.com/.rss",
        "required_fields": ["email", "username", "password"],
        "oauth": ["google", "apple"],
        "notes": "Heavy anti-bot. Use existing agent-reach skill instead.",
    },
    "hashnode": {
        "name": "Hashnode",
        "signup_url": "https://hashnode.com/onboard",
        "login_url": "https://hashnode.com/login",
        "search_url": "https://hashnode.com/search?q={query}",
        "api_url": "https://api.hashnode.com/",
        "required_fields": ["email", "password", "username"],
        "oauth": ["github", "google"],
        "notes": "GitHub OAuth recommended. Has a GraphQL API.",
    },
    "substack": {
        "name": "Substack",
        "signup_url": "https://substack.com/sign-up",
        "login_url": "https://substack.com/sign-in",
        "search_url": None,  # no global search
        "required_fields": ["email", "password"],
        "oauth": ["google"],
        "notes": "Per-publisher RSS is the best way to follow.",
    },
    "hacker_news": {
        "name": "Hacker News",
        "signup_url": "https://news.ycombinator.com/login",
        "login_url": "https://news.ycombinator.com/login",
        "search_url": "https://hn.algolia.com/api/v1/search?query={query}",
        "feed_url": "https://hnrss.org/frontpage",
        "api_url": "https://hacker-news.firebaseio.com/v0/",
        "required_fields": ["username", "password"],
        "notes": "No OAuth. Use Algolia search API for queries. Easy signup.",
    },
    "stackoverflow": {
        "name": "Stack Overflow",
        "signup_url": "https://stackoverflow.com/users/signup",
        "login_url": "https://stackoverflow.com/users/login",
        "search_url": "https://stackoverflow.com/search?q={query}",
        "api_url": "https://api.stackexchange.com/2.3/",
        "oauth": ["google", "github", "facebook"],
        "required_fields": ["email", "password", "display_name"],
        "notes": "Stack Exchange API is free with key. OAuth recommended.",
    },
    "huggingface": {
        "name": "Hugging Face",
        "signup_url": "https://huggingface.co/join",
        "login_url": "https://huggingface.co/login",
        "search_url": "https://huggingface.co/models?search={query}",
        "api_url": "https://huggingface.co/api/",
        "required_fields": ["email", "password", "username"],
        "oauth": ["github", "google"],
        "notes": "GitHub OAuth. Has comprehensive API for models/datasets/spaces.",
    },
    "github": {
        "name": "GitHub",
        "signup_url": "https://github.com/signup",
        "login_url": "https://github.com/login",
        "search_url": "https://github.com/search?q={query}&type={type}",
        "api_url": "https://api.github.com/",
        "required_fields": ["email", "password", "username"],
        "oauth": ["google", "apple"],
        "notes": "Best to use gh CLI. 2FA usually required.",
    },
    "arxiv": {
        "name": "arXiv",
        "signup_url": None,  # no signup, free papers
        "search_url": "http://export.arxiv.org/api/query?search_query={query}",
        "notes": "Open access. No registration needed.",
    },
}


def get_platform(name: str) -> dict:
    """Get a platform config by key."""
    return PLATFORMS.get(name.lower())


def list_platforms() -> list:
    """List all supported platforms."""
    return list(PLATFORMS.keys())


def search_url_for(platform: str, query: str) -> str:
    """Build a search URL for a platform."""
    cfg = PLATFORMS.get(platform.lower())
    if not cfg or not cfg.get("search_url"):
        return None
    return cfg["search_url"].format(query=query.replace(" ", "+"))
