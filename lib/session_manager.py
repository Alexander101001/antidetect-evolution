#!/usr/bin/env python3
"""
Session Manager — persistent logins across requests.

Stores cookies in JSON files keyed by domain.
Lets the agent "stay logged in" to a site after login.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urlparse
from dataclasses import dataclass, asdict

import httpx


@dataclass
class StoredSession:
    """A saved login session."""
    domain: str
    cookies: Dict[str, str]
    headers: Dict[str, str]
    created_at: float
    last_used: float
    username: Optional[str] = None
    notes: str = ""


class SessionManager:
    """Manage persistent login sessions."""

    def __init__(self, storage_path: str = None):
        self.path = Path(storage_path or "~/.pi/skills/antidetect-stack/data/sessions.json").expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, StoredSession] = self._load()
        self.active: Dict[str, httpx.Client] = {}

    def _load(self) -> Dict:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                return {k: StoredSession(**v) for k, v in data.items()}
            except Exception:
                return {}
        return {}

    def _save(self):
        data = {k: asdict(v) for k, v in self.sessions.items()}
        self.path.write_text(json.dumps(data, indent=2))
        self.path.chmod(0o600)

    @staticmethod
    def _domain(url: str) -> str:
        return urlparse(url).netloc

    def save_session(self, url: str, client: httpx.Client,
                     username: Optional[str] = None, notes: str = "") -> str:
        """Save a logged-in session for later reuse."""
        domain = self._domain(url)
        cookies = dict(client.cookies)
        headers = dict(client.headers)

        self.sessions[domain] = StoredSession(
            domain=domain,
            cookies=cookies,
            headers={k: v for k, v in headers.items()
                    if k.lower() in ['user-agent', 'authorization', 'x-csrf-token']},
            created_at=time.time(),
            last_used=time.time(),
            username=username,
            notes=notes,
        )
        self._save()
        return domain

    def get_client(self, url: str) -> httpx.Client:
        """Get an HTTP client with saved session cookies (if any)."""
        domain = self._domain(url)

        # Check active clients first
        if domain in self.active:
            return self.active[domain]

        # Create new client
        client = httpx.Client(http2=True, follow_redirects=True)

        # Restore session if exists
        if domain in self.sessions:
            stored = self.sessions[domain]
            for k, v in stored.cookies.items():
                client.cookies.set(k, v)
            for k, v in stored.headers.items():
                client.headers[k] = v
            stored.last_used = time.time()
            self._save()

        self.active[domain] = client
        return client

    def close_session(self, url: str):
        """Close active client for a domain."""
        domain = self._domain(url)
        if domain in self.active:
            self.active[domain].close()
            del self.active[domain]

    def delete_session(self, url: str) -> bool:
        """Delete a stored session."""
        domain = self._domain(url)
        if domain in self.sessions:
            del self.sessions[domain]
            self._save()
            self.close_session(url)
            return True
        return False

    def list_sessions(self) -> List[StoredSession]:
        return list(self.sessions.values())


if __name__ == "__main__":
    sm = SessionManager()
    print(f"📂 Stored sessions: {len(sm.list_sessions())}")
    for s in sm.list_sessions():
        print(f"   - {s.domain} (user: {s.username}, age: {int(time.time() - s.created_at)}s)")
