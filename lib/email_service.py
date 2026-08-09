#!/usr/bin/env python3
"""
Email service — automatic temp email creation + inbox reading.
Uses GuerrillaMail (has working API, no registration needed).
Also supports fallback to manual URLs for other services.
"""

import requests
import time
import re
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """One email in the inbox."""
    from_addr: str
    subject: str
    body: str
    received_at: str
    mail_id: str


@dataclass
class EmailInbox:
    """Active temp email session."""
    address: str
    sid_token: str
    service: str
    created_at: float


class GuerrillaMail:
    """
    GuerrillaMail API client.
    Free, no signup, ~60min lifetime, has full API.
    Docs: https://www.guerrillamail.com/GuerrillaMailAPI.html
    """

    BASE = "https://api.guerrillamail.com/ajax.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.inbox: Optional[EmailInbox] = None

    def _post(self, **params) -> Dict:
        """POST to GuerrillaMail API."""
        params.setdefault("lang", "en")
        r = self.session.post(self.BASE, data=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def create(self, email_alias: Optional[str] = None) -> EmailInbox:
        """Create a new temp email address."""
        params = {"f": "get_email_address"}
        if email_alias:
            params["email_alias"] = email_alias
        data = self._post(**params)

        self.inbox = EmailInbox(
            address=data["email_addr"],
            sid_token=data["sid_token"],
            service="guerrillamail",
            created_at=time.time(),
        )
        return self.inbox

    def check_inbox(self, since_id: int = 0, timeout: int = 60) -> List[EmailMessage]:
        """
        Check inbox for new messages. Polls until found or timeout.
        Returns list of messages with id > since_id.
        """
        if not self.inbox:
            # Auto-create if no inbox exists
            print("   ⚠️  No inbox yet, creating one...")
            self.create()

        start = time.time()
        while time.time() - start < timeout:
            data = self._post(
                f="get_email_list",
                sid_token=self.inbox.sid_token,
                offset=0,
            )

            messages = []
            for m in data.get("mail_list", []):
                if int(m.get("mail_id", 0)) > since_id:
                    # Fetch full body
                    full = self._post(
                        f="fetch_email",
                        sid_token=self.inbox.sid_token,
                        email_id=m["mail_id"],
                    )
                    messages.append(EmailMessage(
                        from_addr=full.get("mail_from", ""),
                        subject=full.get("mail_subject", ""),
                        body=full.get("mail_body", ""),
                        received_at=full.get("mail_date", ""),
                        mail_id=str(m["mail_id"]),
                    ))

            if messages:
                return messages

            time.sleep(3)

        return []

    def extract_verification_code(self, message: EmailMessage) -> Optional[str]:
        """Extract verification code from email body. Looks for 4-8 digit codes."""
        patterns = [
            r'\b(\d{6})\b',                          # 6-digit code
            r'\b(\d{4})\b',                          # 4-digit code
            r'code[:\s]+([A-Z0-9]{6,})',             # "code: ABC123"
            r'verify.*?([A-Z0-9]{6,})',              # "verify ... ABC123"
            r'([A-Z0-9]{8})',                        # 8-char alphanumeric
        ]
        for pattern in patterns:
            match = re.search(pattern, message.body, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def get_address(self) -> str:
        """Get current email address (must call create() first)."""
        if not self.inbox:
            self.create()
        return self.inbox.address

    def wait_for_verification(self, timeout: int = 90) -> Optional[str]:
        """Wait for verification email and extract code."""
        print(f"📧 Waiting for verification email at {self.inbox.address}...")
        messages = self.check_inbox(timeout=timeout)
        if not messages:
            print("   ⚠️  No email received within timeout")
            return None

        msg = messages[0]
        print(f"   ✅ Got email from: {msg.from_addr}")
        print(f"   Subject: {msg.subject}")

        code = self.extract_verification_code(msg)
        if code:
            print(f"   ✅ Verification code: {code}")
        return code


# Fallback: Open web-based inboxes in a way that can be checked
class WebInboxFallback:
    """
    For services without APIs, opens the public inbox page.
    User must read codes themselves OR I can scrape if simple HTML.
    """

    SERVICES = {
        "temp-mail.org": {
            "url": "https://temp-mail.org",
            "type": "html_scrape",
            "note": "Uses JS to load emails — hard to scrape directly",
        },
        "yopmail.com": {
            "url": "https://yopmail.com/en/",
            "type": "html_scrape",
            "note": "Inbox at /en/inbox/[username]",
        },
        "10minutemail.com": {
            "url": "https://10minutemail.com",
            "type": "html_scrape",
            "note": "Auto-generates address, ~10 min lifetime",
        },
    }

    @staticmethod
    def list_services() -> List[str]:
        return list(WebInboxFallback.SERVICES.keys())


if __name__ == "__main__":
    # Quick test
    gm = GuerrillaMail()
    inbox = gm.create()
    print(f"✅ Created temp email: {inbox.address}")
    print(f"   Session token: {inbox.sid_token[:20]}...")
    print(f"   Check via API: {GuerrillaMail.BASE}?f=get_email_list&sid_token=...")
