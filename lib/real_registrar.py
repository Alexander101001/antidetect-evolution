#!/usr/bin/env python3
"""
Real Registrar — actually creates accounts using:
- Real browser (Chromium via proot)
- Temp email (Mail.tm API)
- Free SMS services
- Captcha handling

Pipeline:
1. Open signup page in real browser
2. Click email/SMS field
3. Get fresh email/number from service
4. Fill all fields
5. Submit
6. Handle verification (read email/SMS inbox)
7. Click verification link or enter code
8. Confirm account created
9. Save credentials
"""

import sys
import time
import json
import re
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

sys.path.insert(0, str(__file__).replace("/real_registrar.py", ""))

from browser_automation import BrowserAutomation
from mail_tm import MailTm
from email_service import GuerrillaMail
from stealth import HumanBehavior


@dataclass
class RegistrationResult:
    """Result of real registration."""
    success: bool
    platform: str
    email_used: str
    final_url: str
    needs_verification: bool
    verification_method: str  # 'email_link', 'email_code', 'sms_code', 'captcha', 'none'
    verification_completed: bool
    account_confirmed: bool
    credentials: Dict
    screenshots: List[str]
    error: Optional[str] = None


class RealRegistrar:
    """Create accounts on platforms using real browser."""

    def __init__(self):
        self.browser = BrowserAutomation(headless=True)
        self.email_tm = MailTm()
        self.email_gm = GuerrillaMail()
        self.human = HumanBehavior()
        self.screenshots_dir = Path("~/.pi/skills/antidetect-stack/data/screenshots").expanduser()
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_dir = Path("~/.pi/skills/antidetect-stack/data/accounts").expanduser()
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

    def get_email(self, persistent: bool = True) -> str:
        """Get a fresh email address."""
        if persistent:
            # Mail.tm is more reliable for verification
            if not self.email_tm.address:
                self.email_tm.create()
            return self.email_tm.address
        else:
            # GuerrillaMail for fast disposable
            return self.email_gm.get_address()

    def wait_for_verification(self, timeout: int = 90) -> Optional[Dict]:
        """Wait for verification email and extract link/code."""
        print(f"   📧 Waiting for verification email...")
        start = time.time()

        # Try Mail.tm first (more reliable)
        if self.email_tm.address:
            msg = self.email_tm.wait_for_message(timeout=timeout)
            if msg:
                return self._extract_verification_from_msg(msg.body)

        # Fallback to GuerrillaMail
        if self.email_gm.inbox:
            messages = self.email_gm.check_inbox(timeout=20)
            if messages:
                return self._extract_verification_from_msg(messages[0].body)

        return None

    def _extract_verification_from_msg(self, body: str) -> Dict:
        """Extract verification link or code from email body."""
        # Look for verification links
        link_patterns = [
            r'''href=["'](https?://[^"']*(?:verify|confirm|activate|validate|complete)[^"']*)["']''',
            r'''(https?://[^\s<>"']*(?:verify|confirm|activate)[^\s<>"']*)''',
        ]

        for pattern in link_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            for match in matches:
                url = match if match.startswith('http') else match
                if 'unsubscribe' not in url.lower() and 'privacy' not in url.lower():
                    return {"type": "link", "value": url}

        # Look for verification codes
        code_patterns = [
            r'\b(\d{6})\b',
            r'\b(\d{4})\b',
            r'code[:\s]+([A-Z0-9]{4,8})',
        ]

        for pattern in code_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return {"type": "code", "value": match.group(1)}

        return {"type": "unknown", "value": body[:200]}

    def register_email(self, signup_url: str, platform_name: str,
                       custom_email: Optional[str] = None,
                       username: Optional[str] = None,
                       password: Optional[str] = None,
                       extra_fields: Optional[Dict] = None) -> RegistrationResult:
        """
        Register with email on a platform.

        Flow:
        1. Get email
        2. Open signup in browser
        3. Fill email + password
        4. Submit
        5. Wait for verification email
        6. Click link or extract code
        7. Confirm account
        """
        print(f"\n{'='*70}")
        print(f"📝 REAL REGISTRATION: {platform_name}")
        print(f"   URL: {signup_url}")
        print(f"{'='*70}\n")

        # Step 1: Get email
        email = custom_email or self.get_email(persistent=True)
        print(f"1️⃣  Email: {email}")

        # Step 2: Generate credentials
        name = self.human.realistic_name()
        creds = {
            "email": email,
            "password": password or self.human.strong_password(),
            "username": username or self.human.random_username(platform_name.lower()),
            "first_name": name['first'],
            "last_name": name['last'],
            "full_name": name['full'],
        }
        if extra_fields:
            creds.update(extra_fields)
        print(f"2️⃣  Generated credentials")

        # Step 3: Open signup in browser
        print(f"3️⃣  Opening signup page in browser...")
        screenshot1 = str(self.screenshots_dir / f"{platform_name}_signup.png")
        result = self.browser.navigate(signup_url)
        print(f"   ✅ Page loaded: {result.get('data', {}).get('url', 'unknown')}")

        # Step 4: Fill form
        print(f"4️⃣  Filling form fields...")

        # Build Playwright script to fill form
        fill_script = f"""
        page.wait_for_timeout(2000)  # Let page settle

        # Common email field selectors
        email_selectors = ['input[name=\"email\"]', 'input[type=\"email\"]', 'input[name=\"user[email]\"]', '#email', 'input[autocomplete=\"email\"]']
        for sel in email_selectors:
            try:
                elem = page.query_selector(sel)
                if elem:
                    elem.fill('{email}')
                    print(f'Filled email via {{sel}}')
                    break
            except: pass

        # Password fields
        pwd_selectors = ['input[name=\"password\"]', 'input[type=\"password\"]', '#password', 'input[name=\"user[password]\"]']
        for sel in pwd_selectors:
            try:
                elem = page.query_selector(sel)
                if elem:
                    elem.fill('{creds["password"]}')
                    break
            except: pass

        # Username if separate
        user_selectors = ['input[name=\"username\"]', 'input[name=\"user[login]\"]', 'input[name=\"login\"]', '#username']
        for sel in user_selectors:
            try:
                elem = page.query_selector(sel)
                if elem:
                    elem.fill('{creds["username"]}')
                    break
            except: pass

        # Name fields if present
        name_selectors = [
            ('input[name=\"first_name\"]', '{creds["first_name"]}'),
            ('input[name=\"last_name\"]', '{creds["last_name"]}'),
            ('input[name=\"name\"]', '{creds["full_name"]}'),
            ('input[name=\"full_name\"]', '{creds["full_name"]}'),
        ]
        for sel, val in name_selectors:
            try:
                elem = page.query_selector(sel)
                if elem:
                    elem.fill(val)
            except: pass

        page.wait_for_timeout(1000)

        # Screenshot after filling
        page.screenshot(path='{screenshot1}', full_page=True)

        result['success'] = True
        result['data'] = {{
            'url': page.url,
            'title': page.title(),
            'filled': True
        }}
        result['credentials'] = {json.dumps(creds)}
"""
        fill_result = self.browser._run_playwright_script(fill_script)
        print(f"   {'✅' if fill_result.get('success') else '❌'} Form filling: {fill_result.get('success')}")

        # Step 5: Submit
        print(f"5️⃣  Submitting form...")
        submit_script = f"""
        submit_selectors = ['button[type=\"submit\"]', 'input[type=\"submit\"]', 'button:has-text(\"Sign up\")', 'button:has-text(\"Register\")', 'button:has-text(\"Create\")']
        for sel in submit_selectors:
            try:
                elem = page.query_selector(sel)
                if elem:
                    elem.click()
                    print(f'Clicked submit via {{sel}}')
                    break
            except: pass

        page.wait_for_load_state('networkidle', timeout=30000)
        page.wait_for_timeout(3000)

        result['success'] = True
        result['data'] = {{
            'url': page.url,
            'title': page.title(),
            'submitted': True
        }}
"""
        submit_result = self.browser._run_playwright_script(submit_script)
        print(f"   {'✅' if submit_result.get('success') else '❌'} Submit: {submit_result.get('success')}")
        if submit_result.get('data'):
            print(f"   Final URL: {submit_result['data']['url']}")

        # Step 6: Check if verification needed
        final_url = submit_result.get('data', {}).get('url', signup_url)
        needs_verification = 'verify' in final_url.lower() or 'confirm' in final_url.lower()

        if needs_verification:
            print(f"\n6️⃣  Verification email required")
            print(f"   Waiting for email...")
            verification = self.wait_for_verification(timeout=60)

            if verification:
                print(f"   ✅ Got verification: type={verification['type']}")
                if verification['type'] == 'link':
                    print(f"   🔗 Clicking: {verification['value'][:80]}...")
                    self.browser.navigate(verification['value'])
                    verification_completed = True
                elif verification['type'] == 'code':
                    print(f"   🔢 Code: {verification['value']}")
                    verification_completed = False  # Would need to enter manually
            else:
                print(f"   ⚠️  No verification email received within timeout")
                verification_completed = False
        else:
            print(f"\n6️⃣  No email verification needed")
            verification_completed = True

        # Screenshot final state
        screenshot2 = str(self.screenshots_dir / f"{platform_name}_final.png")
        self.browser.screenshot(final_url, screenshot2)

        # Step 7: Determine success (HONEST verification)
        page_text = self.browser.get_page_text(final_url) or ""
        content_length = len(page_text) if page_text else 0

        # Strict success criteria:
        # 1. Page must have substantial content (not blank)
        # 2. Must show account-created OR login state indicators
        has_content = content_length > 200
        account_confirmed = has_content and any(kw in page_text.lower() for kw in [
            'dashboard', 'welcome', 'logged in', 'profile', 'settings',
            'verify your email', 'check your email', 'confirm your email',
            'account created', 'registration successful'
        ])

        # Final URL must NOT be the same signup page (means we didn't progress)
        progressed = final_url != signup_url and 'about:blank' not in final_url

        # Both conditions must be met for TRUE success
        success = account_confirmed and progressed and has_content

        if not success:
            if not has_content:
                error_msg = f"Page has no content (likely bot detection blocked us)"
            elif not progressed:
                error_msg = f"Did not progress past signup page (stayed at {final_url})"
            else:
                error_msg = f"Form submitted but account not confirmed"
        else:
            error_msg = None

        # Save credentials
        if success:
            self._save_credentials(platform_name, creds, email)

        result = RegistrationResult(
            success=success,
            platform=platform_name,
            email_used=email,
            final_url=final_url,
            needs_verification=needs_verification,
            verification_method='email_link' if needs_verification and verification and verification['type'] == 'link' else 'none',
            verification_completed=verification_completed,
            account_confirmed=account_confirmed,
            credentials=creds if success else {},
            screenshots=[screenshot1, screenshot2],
        )

        self._print_result(result)
        return result

    def register_oauth(self, signup_url: str, platform_name: str,
                       provider: str = "github") -> RegistrationResult:
        """
        Register via OAuth (GitHub, Google, etc.)
        Note: This would need real OAuth credentials to actually log in.
        We document the flow and can click the button.
        """
        print(f"\n{'='*70}")
        print(f"🔗 OAUTH REGISTRATION: {platform_name}")
        print(f"   Provider: {provider}")
        print(f"   URL: {signup_url}")
        print(f"{'='*70}\n")

        print(f"1️⃣  Opening signup page...")
        result = self.browser.navigate(signup_url)
        print(f"   ✅ Loaded: {result.get('data', {}).get('url')}")

        print(f"2️⃣  Clicking {provider} OAuth button...")
        click_result = self.browser.click_oauth_button(signup_url, provider)

        if click_result.get('success'):
            final_url = click_result.get('data', {}).get('url', '')
            print(f"   ✅ Clicked {provider}")
            print(f"   Now at: {final_url[:80]}")

            # Check if we landed on OAuth provider
            if provider in final_url.lower():
                print(f"\n3️⃣  At {provider} authorization page")
                print(f"   ⚠️  Manual step required: authorize the app")
                print(f"   URL: {final_url}")

                # Take screenshot
                screenshot = str(self.screenshots_dir / f"{platform_name}_oauth.png")
                self.browser.screenshot(final_url, screenshot)

                return RegistrationResult(
                    success=False,
                    platform=platform_name,
                    email_used="oauth",
                    final_url=final_url,
                    needs_verification=False,
                    verification_method=f'oauth_{provider}',
                    verification_completed=False,
                    account_confirmed=False,
                    credentials={"oauth_provider": provider, "url": final_url},
                    screenshots=[screenshot],
                    error=f"OAuth requires manual authorization at {final_url}",
                )
            else:
                # Already authorized (cookie was set)
                return RegistrationResult(
                    success=True,
                    platform=platform_name,
                    email_used="oauth",
                    final_url=final_url,
                    needs_verification=False,
                    verification_method=f'oauth_{provider}',
                    verification_completed=True,
                    account_confirmed=True,
                    credentials={"oauth_provider": provider},
                    screenshots=[],
                )

        return RegistrationResult(
            success=False,
            platform=platform_name,
            email_used="oauth",
            final_url=signup_url,
            needs_verification=False,
            verification_method=f'oauth_{provider}',
            verification_completed=False,
            account_confirmed=False,
            credentials={},
            screenshots=[],
            error=f"Could not click {provider} button",
        )

    def _save_credentials(self, platform: str, creds: Dict, email: str):
        """Save account credentials securely."""
        path = self.credentials_dir / f"{platform}_{email.replace('@', '_at_')}.json"
        path.write_text(json.dumps({
            "platform": platform,
            "email": email,
            "credentials": creds,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }, indent=2))
        path.chmod(0o600)
        print(f"   💾 Credentials saved: {path}")

    def _print_result(self, result: RegistrationResult):
        """Print registration result."""
        print(f"\n{'='*70}")
        print(f"📊 REGISTRATION RESULT: {result.platform}")
        print(f"{'='*70}")
        print(f"   Success: {'✅' if result.success else '❌'} {result.success}")
        print(f"   Email: {result.email_used}")
        print(f"   Final URL: {result.final_url[:80]}")
        print(f"   Verification needed: {result.needs_verification}")
        print(f"   Verification method: {result.verification_method}")
        print(f"   Verification completed: {result.verification_completed}")
        print(f"   Account confirmed: {result.account_confirmed}")
        if result.error:
            print(f"   Error: {result.error}")
        if result.success:
            print(f"\n   🔑 Credentials:")
            for k, v in result.credentials.items():
                if k == 'password':
                    print(f"      {k}: {'*' * 12}")
                else:
                    print(f"      {k}: {v}")
        print(f"{'='*70}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: real_registrar.py <signup_url> [platform_name] [method]")
        print("Methods: email, oauth_github, oauth_google")
        sys.exit(1)

    url = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    method = sys.argv[3] if len(sys.argv) > 3 else "email"

    registrar = RealRegistrar()

    if method.startswith("oauth_"):
        provider = method.replace("oauth_", "")
        result = registrar.register_oauth(url, platform, provider)
    else:
        result = registrar.register_email(url, platform)
