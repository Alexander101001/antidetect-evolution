#!/usr/bin/env python3
"""
Live Registrar — actually registers on platforms end-to-end.

Combines:
- universal_registrar (planning)
- submission_engine (form POST)
- email_service (temp email)
- verification_handler (auto-click links)
- session_manager (persist login)
- pattern_cache (learn from success/failure)

Use with caution — only on sites you're authorized to test.
"""

import sys
import time
from typing import Optional, Dict
from dataclasses import dataclass

sys.path.insert(0, str(__file__).replace("/live_registrar.py", ""))

from universal_registrar import UniversalRegistrar, RegistrationResult
from submission_engine import SubmissionEngine
from email_service import GuerrillaMail
from verification_handler import VerificationHandler
from session_manager import SessionManager
from pattern_cache import PatternCache
from stealth import HumanBehavior


@dataclass
class LiveRegistrationResult:
    """Full result of a live registration attempt."""
    success: bool
    platform: str
    signup_url: str
    final_url: str
    email_used: Optional[str] = None
    verification_completed: bool = False
    logged_in: bool = False
    session_saved: bool = False
    credentials: Optional[Dict] = None
    error: Optional[str] = None
    steps_completed: list = None
    next_steps: list = None


class LiveRegistrar:
    """Register for real, end-to-end."""

    def __init__(self):
        self.universal = UniversalRegistrar()
        self.submitter = SubmissionEngine()
        self.email = GuerrillaMail()
        self.verifier = VerificationHandler()
        self.sessions = SessionManager()
        self.cache = PatternCache()
        self.human = HumanBehavior()

    def register(self, signup_url: str, platform: Optional[str] = None,
                 custom_fields: Optional[Dict] = None,
                 auto_verify_email: bool = True,
                 require_oauth_fallback: bool = True,
                 dry_run: bool = False) -> LiveRegistrationResult:
        """
        Full live registration flow:
        1. Study platform
        2. Acquire temp email
        3. Fill + submit form
        4. Wait for verification email
        5. Click verification link
        6. Verify login works
        7. Save session
        8. Cache pattern
        """
        steps = []
        print(f"\n{'='*70}")
        print(f"🚀 LIVE REGISTRATION: {signup_url}")
        print(f"{'='*70}\n")

        # Step 1: Study
        print("Step 1: Studying platform...")
        try:
            study = self.universal.study(signup_url, platform)
            print(f"   ✅ Platform: {study['platform']}")
            print(f"   ✅ Forms: {study['forms_found']}")
            print(f"   ✅ Verifications: {study['verifications_needed']}")
            steps.append("studied")
        except Exception as e:
            return LiveRegistrationResult(
                success=False, platform="unknown", signup_url=signup_url,
                final_url="", error=f"Study failed: {e}", steps_completed=steps,
            )

        # Check for hard blockers
        if 'captcha' in study['verifications_needed']:
            print("   ⚠️  CAPTCHA detected — may fail without solver")
        if 'sms' in study['verifications_needed']:
            print("   ⚠️  SMS verification needed — free SMS may not work")

        # Prefer OAuth if available (much more reliable)
        if require_oauth_fallback and study['oauth_providers']:
            print(f"   ℹ️  OAuth available: {study['oauth_providers']}")
            print(f"   💡 Recommendation: Use OAuth via {study['oauth_providers'][0]}")

        # Step 2: Plan
        print("\nStep 2: Building registration plan...")
        try:
            plan = self.universal.plan_registration(
                signup_url, platform, custom_fields
            )
            print(f"   ✅ Form action: {plan.form_action}")
            print(f"   ✅ Fields: {list(plan.fields.keys())}")
            steps.append("planned")
        except Exception as e:
            return LiveRegistrationResult(
                success=False, platform=study['platform'], signup_url=signup_url,
                final_url="", error=f"Plan failed: {e}", steps_completed=steps,
            )

        # Step 3: Submit
        print("\nStep 3: Submitting registration form...")
        if dry_run:
            print("   ⚠️  DRY RUN — building plan only")
            return LiveRegistrationResult(
                success=True, platform=study['platform'], signup_url=signup_url,
                final_url=signup_url,
                email_used=self.email.inbox.address if self.email.inbox else None,
                verification_completed=False, logged_in=False, session_saved=False,
                credentials=plan.fields,
                steps_completed=["studied", "planned"],
                next_steps=["Set dry_run=False to actually submit"],
            )

        result = self.submitter.submit_with_requests(
            url=signup_url,
            form_action=plan.form_action,
            fields=plan.fields,
        )

        print(f"   Status: {result.status_code}")
        print(f"   Final URL: {result.final_url}")

        if not result.success:
            # Try with mechanicalsoup as fallback
            print("   ⚠️  First attempt may have failed, trying mechanicalsoup...")
            self.cache.record_failure(signup_url, "httpx submission")

            # Find form selector
            form_selector = "form"  # generic fallback
            mb_result = self.submitter.submit_form(
                page_url=signup_url,
                form_selector=form_selector,
                fields=plan.fields,
            )
            if mb_result.success:
                result = mb_result

        steps.append("submitted")

        # Step 4: Email verification
        verification_done = False
        if result.requires_email_verification and auto_verify_email and self.email.inbox:
            print("\nStep 4: Waiting for verification email...")
            self.human.delay(2, 5)  # give server time to send
            link = self.verifier.auto_verify_email(self.email, timeout=60)
            verification_done = link is not None
            steps.append("email_verified" if verification_done else "email_pending")

        # Step 5: Check login
        print("\nStep 5: Verifying login...")
        logged_in = False
        try:
            check = self.submitter.client.get(result.final_url)
            page_text = check.text.lower()
            logged_in = any(s in page_text for s in [
                'dashboard', 'profile', 'settings', 'logout', 'sign out',
                'my account', 'welcome'
            ])
            print(f"   {'✅' if logged_in else '⚠️ '} Login verified: {logged_in}")
        except Exception as e:
            print(f"   ⚠️  Could not verify: {e}")
        steps.append("login_checked")

        # Step 6: Save session
        session_saved = False
        if logged_in:
            print("\nStep 6: Saving session...")
            try:
                self.sessions.save_session(
                    url=result.final_url,
                    client=self.submitter.client.session if hasattr(self.submitter.client, 'session') else None,
                    username=plan.fields.get(plan.username_field),
                    notes=f"Registered via live_registrar",
                )
                session_saved = True
            except Exception as e:
                print(f"   ⚠️  Session save failed: {e}")
        steps.append("session_saved" if session_saved else "session_skipped")

        # Step 7: Cache pattern
        if result.success or logged_in:
            self.cache.record_success(signup_url, notes=f"Logged in: {logged_in}")

        # Build result
        next_steps = []
        if not result.success:
            next_steps.append("Check form fields manually — auto-fill may have missed some")
        if not verification_done and result.requires_email_verification:
            next_steps.append("Check temp email inbox manually for verification link")
        if not logged_in:
            next_steps.append("Visit site and try to login with the generated credentials")

        return LiveRegistrationResult(
            success=result.success or logged_in,
            platform=study['platform'],
            signup_url=signup_url,
            final_url=result.final_url,
            email_used=self.email.inbox.address if self.email.inbox else None,
            verification_completed=verification_done,
            logged_in=logged_in,
            session_saved=session_saved,
            credentials=plan.fields,
            error=result.error if not result.success else None,
            steps_completed=steps,
            next_steps=next_steps,
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: live_registrar.py <signup_url> [platform_name]")
        print("Example: live_registrar.py https://the-internet.herokuapp.com/register test")
        sys.exit(1)

    url = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else None

    registrar = LiveRegistrar()
    result = registrar.register(url, platform)

    print(f"\n{'='*70}")
    print("RESULT:")
    print(f"{'='*70}")
    print(f"Success: {result.success}")
    print(f"Platform: {result.platform}")
    print(f"Final URL: {result.final_url}")
    print(f"Email: {result.email_used}")
    print(f"Verification: {result.verification_completed}")
    print(f"Logged in: {result.logged_in}")
    print(f"Session saved: {result.session_saved}")
    print(f"Steps: {' → '.join(result.steps_completed or [])}")
    if result.error:
        print(f"Error: {result.error}")
    if result.next_steps:
        print("\nNext steps:")
        for s in result.next_steps:
            print(f"  - {s}")
