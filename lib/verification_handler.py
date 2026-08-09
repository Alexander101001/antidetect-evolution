#!/usr/bin/env python3
"""
Verification Handler — auto-complete email/SMS verification flows.

Many platforms send click-this-link emails (not codes).
This module reads the email, finds the link, and clicks it.
"""

import re
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
from urllib.parse import urlparse

from email_service import GuerrillaMail, EmailMessage
from unified import SmartClient


@dataclass
class VerificationLink:
    """A verification link found in email."""
    url: str
    domain: str
    link_type: str  # verify, confirm, activate, etc.


class VerificationHandler:
    """Handle email verification automatically."""

    VERIFICATION_PATTERNS = [
        r'href=["\']([^"\']*(?:verify|confirm|activate|validate|complete)[^"\']*)["\']',
        r'(https?://[^\s"\'<>]+(?:verify|confirm|activate|validate|complete)[^\s"\'<>]*)',
    ]

    def __init__(self):
        self.client = SmartClient()

    def find_verification_link(self, email_body: str) -> Optional[VerificationLink]:
        """Find verification link in email HTML body."""
        for pattern in self.VERIFICATION_PATTERNS:
            matches = re.findall(pattern, email_body, re.IGNORECASE)
            for match in matches:
                url = match if match.startswith('http') else match
                if not url.startswith('http'):
                    continue
                # Filter out obvious non-verification links
                if any(skip in url.lower() for skip in ['unsubscribe', 'privacy', 'twitter.com', 'facebook.com/share']):
                    continue
                domain = urlparse(url).netloc
                link_type = 'verify' if 'verify' in url.lower() else \
                           'confirm' if 'confirm' in url.lower() else \
                           'activate' if 'activate' in url.lower() else 'unknown'
                return VerificationLink(url=url, domain=domain, link_type=link_type)
        return None

    def click_verification_link(self, url: str) -> Dict:
        """Click a verification link and return the response."""
        print(f"🖱️  Clicking: {url[:80]}...")
        try:
            result = self.client.get(url, method="cloudscraper")
            print(f"   ✅ Status: {result.status}")
            print(f"   ✅ Final URL: {result.url if hasattr(result, 'url') else 'unknown'}")
            return {
                "success": True,
                "status": result.status,
                "text": result.text[:2000],
                "url": url,
            }
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return {"success": False, "error": str(e), "url": url}

    def auto_verify_email(self, email_client: GuerrillaMail,
                          timeout: int = 90) -> Optional[VerificationLink]:
        """
        Wait for verification email and auto-click the link.
        Returns the link that was clicked (or None).
        """
        print(f"📧 Waiting for verification email at {email_client.inbox.address}...")
        messages = email_client.check_inbox(timeout=timeout)

        if not messages:
            print("   ⚠️  No email received")
            return None

        msg = messages[0]
        print(f"   ✅ Got: {msg.subject[:60]}")

        # Try HTML body first (usually has clickable links)
        link = self.find_verification_link(msg.body)
        if not link:
            # Try plain text body fallback
            link = self.find_verification_link(msg.subject + " " + msg.body)

        if link:
            print(f"   🔗 Found link: {link.link_type} -> {link.domain}")
            self.click_verification_link(link.url)
            return link

        # Fall back to code extraction
        code = email_client.extract_verification_code(msg)
        if code:
            print(f"   🔢 Found code: {code} (would need to enter on site)")
            return None

        print("   ⚠️  No link or code found in email")
        return None


if __name__ == "__main__":
    print("Testing verification handler...")
    handler = VerificationHandler()

    # Test link extraction on sample email
    sample = '''
    <html><body>
    <p>Click to verify: <a href="https://example.com/verify?token=abc123">Verify Email</a></p>
    <p>Or copy: https://example.com/confirm/xyz</p>
    </body></html>
    '''
    link = handler.find_verification_link(sample)
    print(f"✅ Found: {link.url if link else 'None'}")
    print(f"   Type: {link.link_type if link else 'N/A'}")
