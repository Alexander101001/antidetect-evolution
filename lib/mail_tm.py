#!/usr/bin/env python3
"""
Mail.tm API client — persistent free temp email with full API.

Better than GuerrillaMail for some use cases:
- Persistent inboxes (don't expire in 60min)
- Full REST API
- Free, no signup

API docs: https://docs.mail.tm
"""

import requests
import time
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class MailTmMessage:
    """Email from mail.tm inbox."""
    id: str
    from_addr: str
    subject: str
    body: str
    received_at: str
    seen: bool


class MailTm:
    """Mail.tm email service client."""

    BASE = "https://api.mail.tm"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.token: Optional[str] = None
        self.account_id: Optional[str] = None
        self.address: Optional[str] = None

    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """Make API request."""
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        r = self.session.request(method, f"{self.BASE}{path}", timeout=30, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

    def get_domains(self) -> List[Dict]:
        """Get available email domains."""
        data = self._request("GET", "/domains")
        # API returns either list directly or {"hydra:member": [...]}
        if isinstance(data, list):
            return data
        return data.get("hydra:member", [])

    def create_account(self, address: str, password: str) -> Dict:
        """Create a new mail.tm account."""
        data = self._request("POST", "/accounts", json={
            "address": address,
            "password": password,
        })
        self.account_id = data.get("id")
        return data

    def login(self, address: str, password: str) -> str:
        """Login and get token."""
        data = self._request("POST", "/token", json={
            "address": address,
            "password": password,
        })
        self.token = data.get("token")
        return self.token

    def create(self, password: Optional[str] = None) -> str:
        """Create a new random email account. Returns the email address."""
        import random
        import string

        # Get a domain
        domains = self.get_domains()
        if not domains:
            # Fallback to known domains
            print("   ⚠️  Could not fetch domains, using fallback")
            domain = "tm.zain.id"  # known public domain
        else:
            domain = domains[0]["domain"]

        # Generate random username
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.address = f"{username}@{domain}"

        # Password
        if not password:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # Create + login
        self.create_account(self.address, password)
        self.login(self.address, password)

        return self.address

    def get_messages(self) -> List[MailTmMessage]:
        """Get all messages in inbox."""
        data = self._request("GET", "/messages")
        if isinstance(data, dict):
            items = data.get("hydra:member", [])
        else:
            items = data
        messages = []
        for m in items:
            messages.append(MailTmMessage(
                id=m.get("id", ""),
                from_addr=m.get("from", {}).get("address", ""),
                subject=m.get("subject", ""),
                body="",  # need separate fetch for body
                received_at=m.get("createdAt", ""),
                seen=m.get("seen", False),
            ))
        return messages

    def get_message_body(self, message_id: str) -> str:
        """Fetch full body of a message."""
        data = self._request("GET", f"/messages/{message_id}")
        # Body could be in different fields
        return data.get("text", "") or data.get("html", "") or ""

    def wait_for_message(self, timeout: int = 60) -> Optional[MailTmMessage]:
        """Poll inbox until message arrives."""
        start = time.time()
        seen_ids = set()
        while time.time() - start < timeout:
            msgs = self.get_messages()
            for msg in msgs:
                if msg.id not in seen_ids:
                    seen_ids.add(msg.id)
                    msg.body = self.get_message_body(msg.id)
                    return msg
            time.sleep(3)
        return None

    def get_address(self) -> str:
        if not self.address:
            self.create()
        return self.address


if __name__ == "__main__":
    print("Testing Mail.tm...")
    try:
        mt = MailTm()
        domains = mt.get_domains()
        print(f"✅ Available domains: {[d['domain'] for d in domains[:3]]}")
        addr = mt.create()
        print(f"✅ Created: {addr}")
    except Exception as e:
        print(f"❌ Failed: {e}")
