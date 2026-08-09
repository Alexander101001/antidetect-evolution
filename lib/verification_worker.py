#!/usr/bin/env python3
"""
Verification Worker — Auto-completes email/SMS verification flows.

Fully autonomous:
- Polls email inbox for verification emails
- Extracts verification links and codes
- Auto-clicks links using nodriver (100% human)
- Enters codes in forms with human-like timing
- Handles 2FA when possible
- Logs everything
"""

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

import sys
sys.path.insert(0, str(__file__).replace("/verification_worker.py", ""))

from nodriver_automation import NodriverAutomation
from mail_tm import MailTm


@dataclass
class VerificationResult:
    """Result of verification attempt."""
    platform: str
    email: str
    verification_type: str  # 'link', 'code', '2fa', 'none'
    found: bool
    action: str  # 'clicked_link', 'entered_code', 'no_action', 'failed'
    url_clicked: Optional[str] = None
    code_used: Optional[str] = None
    account_confirmed: bool = False
    error: Optional[str] = None


class VerificationWorker:
    """Auto-handle all verification flows."""

    def __init__(self):
        self.browser: Optional[NodriverAutomation] = None
        self.email = MailTm()
        self.history: List[VerificationResult] = []
        self.reports_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/verification_log")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def start(self):
        """Start browser."""
        self.browser = NodriverAutomation(use_tor=True)
        await self.browser.start()

    async def stop(self):
        """Stop browser."""
        if self.browser:
            await self.browser.stop()

    async def wait_for_verification_email(self, timeout: int = 120) -> Optional[Dict]:
        """
        Wait for verification email with link or code.
        Returns dict with type and value.
        """
        if not self.email.address:
            return None

        print(f"   📧 Waiting for email at {self.email.address}...")
        start = time.time()

        while time.time() - start < timeout:
            try:
                msg = self.email.wait_for_message(timeout=10)
                if msg:
                    print(f"   ✅ Got email: {msg.subject[:60]}")

                    # Extract link
                    link = self._extract_link(msg.body + " " + msg.subject)
                    if link:
                        return {"type": "link", "value": link, "subject": msg.subject, "body": msg.body[:500]}

                    # Extract code
                    code = self._extract_code(msg.body)
                    if code:
                        return {"type": "code", "value": code, "subject": msg.subject, "body": msg.body[:500]}

                    return {"type": "unknown", "value": None, "subject": msg.subject, "body": msg.body[:500]}
            except Exception as e:
                print(f"   ⚠️  Email check error: {str(e)[:50]}")

            await asyncio.sleep(3)

        return None

    def _extract_link(self, text: str) -> Optional[str]:
        """Extract verification link from email body."""
        patterns = [
            # Direct verification URLs
            r"""href=["'](https?://[^"']*(?:verify|confirm|activate|validate|complete|signup|register|welcome)[^"']*)["']""",
            r"""(https?://[^\s<>"']*(?:verify|confirm|activate|validate|complete|signup|register|welcome)[^\s<>"']*)""",
            # Any URL that looks like a verification link
            r"""href=["'](https?://[^"']+)["']""",
            r"""(https?://[^\s<>"']+)""",
        ]

        skip_keywords = ['unsubscribe', 'preferences', 'privacy', 'twitter.com/share', 'facebook.com/share', 'logo', 'help']

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match.strip()
                if not url.startswith('http'):
                    continue
                if any(skip in url.lower() for skip in skip_keywords):
                    continue
                # Prefer verify-like URLs
                if any(kw in url.lower() for kw in ['verify', 'confirm', 'activate', 'welcome', 'signup', 'register']):
                    return url

        # If no verification-like URL, return first URL
        for pattern in patterns[:2]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match.strip()
                if url.startswith('http') and not any(skip in url.lower() for skip in skip_keywords):
                    return url

        return None

    def _extract_code(self, text: str) -> Optional[str]:
        """Extract verification code from email body."""
        patterns = [
            r'\b(\d{6})\b',                                    # 6-digit code
            r'\b(\d{4})\b',                                    # 4-digit code
            r'code[:\s]+([A-Z0-9]{6,8})',                      # "code: ABC123"
            r'verification code[:\s]+([A-Z0-9]{4,8})',         # "verification code: XYZ"
            r'one-time code[:\s]+([A-Z0-9]{4,8})',             # "one-time code: ABC"
            r'([A-Z0-9]{8})',                                  # 8-char alphanumeric
            r'\b(\d{5})\b',                                    # 5-digit code
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.isdigit() or (match.isalnum() and match.isupper()):
                    return match

        return None

    async def click_verification_link(self, url: str) -> bool:
        """Click verification link with human-like behavior."""
        try:
            print(f"   🔗 Clicking verification link...")
            await self.browser.navigate(url)
            await asyncio.sleep(3)

            # Check if we're on a "verified" or "success" page
            body = await self.browser.page.evaluate("document.body.innerText") or ""

            success_indicators = ['verified', 'confirmed', 'success', 'welcome', 'activated', 'complete']
            if any(kw in body.lower() for kw in success_indicators):
                print(f"   ✅ Verification successful!")
                return True
            else:
                print(f"   ⚠️  Link clicked but confirmation unclear")
                return False
        except Exception as e:
            print(f"   ❌ Link click failed: {str(e)[:80]}")
            return False

    async def enter_verification_code(self, url: str, code: str) -> bool:
        """Navigate to URL and enter verification code."""
        try:
            print(f"   🔢 Entering code: {code}")
            await self.browser.navigate(url)
            await asyncio.sleep(3)

            # Try to find code input field
            js = """
                const inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[name*="code"], input[name*="otp"]');
                for (const inp of inputs) {
                    inp.focus();
                    return inp.name || inp.id || 'found';
                }
                return null;
            """
            field_name = await self.browser.page.evaluate(js)

            if field_name:
                # Type code with human-like delays
                type_js = f"""
                    const inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[name*="code"], input[name*="otp"]');
                    const input = inputs[0];
                    input.value = '';
                    const code = '{code}';
                    for (let i = 0; i < code.length; i++) {{
                        setTimeout(() => {{
                            input.value += code[i];
                            input.dispatchEvent(new Event('input', {{bubbles: true}}));
                        }}, i * 80);
                    }}
                    setTimeout(() => {{
                        const submit = document.querySelector('button[type="submit"], button:has-text("Verify"), button:has-text("Confirm")');
                        if (submit) submit.click();
                    }}, code.length * 80 + 500);
                """
                await self.browser.page.evaluate(type_js)
                await asyncio.sleep(3)

                body = await self.browser.page.evaluate("document.body.innerText") or ""
                if any(kw in body.lower() for kw in ['verified', 'confirmed', 'success', 'welcome']):
                    print(f"   ✅ Code accepted!")
                    return True

            return False
        except Exception as e:
            print(f"   ❌ Code entry failed: {str(e)[:80]}")
            return False

    async def complete_verification(self, platform: str, signup_url: str) -> VerificationResult:
        """Complete verification flow for a platform."""
        result = VerificationResult(
            platform=platform,
            email=self.email.address or "",
            verification_type='none',
            found=False,
            action='no_action',
        )

        try:
            print(f"\n{'='*60}")
            print(f"🔐 VERIFICATION: {platform}")
            print(f"{'='*60}")

            verification = await self.wait_for_verification_email(timeout=90)

            if not verification:
                print(f"   ⚠️  No verification email received")
                result.action = 'timeout'
                self.history.append(result)
                return result

            result.found = True
            result.verification_type = verification['type']

            if verification['type'] == 'link' and verification['value']:
                result.url_clicked = verification['value']
                success = await self.click_verification_link(verification['value'])
                result.account_confirmed = success
                result.action = 'clicked_link' if success else 'click_failed'
            elif verification['type'] == 'code' and verification['value']:
                result.code_used = verification['value']
                success = await self.enter_verification_code(signup_url, verification['value'])
                result.account_confirmed = success
                result.action = 'entered_code' if success else 'code_failed'

        except Exception as e:
            result.error = str(e)[:200]
            result.action = 'error'

        self.history.append(result)

        # Save log
        log_path = self.reports_dir / f"verify_{platform}_{int(time.time())}.json"
        log_path.write_text(json.dumps(asdict(result), indent=2))

        return result


async def main():
    """Run verification handler on test scenarios."""
    print("=" * 70)
    print("🔐 VERIFICATION WORKER — Auto-complete email verifications")
    print("=" * 70)

    worker = VerificationWorker()
    await worker.start()

    # Show what email we have
    print(f"\n📧 Email ready: {worker.email.address}")

    # Demo: extract patterns from sample emails
    print("\n🔍 Pattern detection test:")
    sample_emails = [
        "Click to verify: https://example.com/verify?token=abc123",
        "Your code is: 482931",
        "Confirm your email: https://platform.com/confirm?id=xyz",
        "Welcome! Activate: https://app.io/activate/u/123",
    ]

    for email in sample_emails:
        link = worker._extract_link(email)
        code = worker._extract_code(email)
        print(f"\n   Text: {email[:50]}...")
        print(f"   Link: {link[:60] if link else 'None'}")
        print(f"   Code: {code if code else 'None'}")

    await worker.stop()
    print("\n✅ Verification worker ready for use")


if __name__ == "__main__":
    asyncio.run(main())
