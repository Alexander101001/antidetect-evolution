#!/usr/bin/env python3
"""
Universal Registrar — register on ANY platform given a URL.

Workflow:
1. Study platform (analyze form structure)
2. Generate realistic credentials
3. Detect what verifications are needed (email/SMS/captcha)
4. Acquire temp email/SMS if needed
5. Fill and submit form
6. Handle verification codes automatically
7. Store credentials securely

This is the main tool you'll use to register accounts.
"""

import sys
import re
import time
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(__file__).replace("/universal_registrar.py", ""))

from unified import SmartClient
from stealth import HumanBehavior, Fingerprint
from email_service import GuerrillaMail
from sms_service import SMSService
from captcha_solver import CaptchaDetector, CaptchaSolver
from researcher import Researcher


class VerificationType(Enum):
    NONE = "none"
    EMAIL = "email"
    SMS = "sms"
    CAPTCHA = "captcha"
    OAUTH_ONLY = "oauth"


@dataclass
class RegistrationPlan:
    """Everything needed to register on a platform."""
    url: str
    platform: str
    form_action: str
    fields: Dict[str, str]  # name -> value
    verifications: List[VerificationType]
    captcha_challenge: Optional[Dict] = None
    oauth_providers: List[str] = field(default_factory=list)
    password_field: Optional[str] = None
    username_field: Optional[str] = None
    email_field: Optional[str] = None


@dataclass
class RegistrationResult:
    """Result of a registration attempt."""
    success: bool
    platform: str
    credentials: Dict
    email_used: Optional[str] = None
    sms_number_used: Optional[str] = None
    verification_code: Optional[str] = None
    captcha_solved: bool = False
    error: Optional[str] = None
    next_steps: List[str] = field(default_factory=list)


class UniversalRegistrar:
    """
    Register on ANY platform.

    Usage:
        reg = UniversalRegistrar()
        result = reg.register("https://dev.to/enter?signup=true", platform="dev_to")
        print(result)
    """

    def __init__(self, email_provider=None, sms_provider=None):
        self.client = SmartClient()
        self.fingerprint = Fingerprint()
        self.human = HumanBehavior()
        self.email = email_provider or GuerrillaMail()
        self.sms = sms_provider or SMSService()
        self.captcha_detector = CaptchaDetector()
        self.captcha_solver = CaptchaSolver()
        self.researcher = Researcher(self.client)

    def study(self, url: str, platform: Optional[str] = None) -> Dict:
        """
        Learn everything about a platform's signup page.
        Returns detailed form analysis.
        """
        result = self.client.get(url)
        html = result.text

        # Detect forms
        forms = re.findall(
            r'<form[^>]*?(?:action=["\']([^"\']*)["\'])?[^>]*>(.*?)</form>',
            html, re.DOTALL | re.IGNORECASE
        )

        # Analyze each form
        form_analysis = []
        for action, body in forms:
            # Find inputs
            inputs = re.findall(
                r'<input[^>]*?(?:name|id)=["\']([^"\']*)["\'][^>]*?(?:type=["\']([^"\']*)["\'])?[^>]*?(?:placeholder=["\']([^"\']*)["\'])?',
                body, re.IGNORECASE
            )
            fields = [{"name": n, "type": t or "text", "placeholder": p} for n, t, p in inputs if n]

            # Find selects (dropdowns)
            selects = re.findall(
                r'<select[^>]*name=["\']([^"\']*)["\']',
                body, re.IGNORECASE
            )

            # Find textareas
            textareas = re.findall(
                r'<textarea[^>]*name=["\']([^"\']*)["\']',
                body, re.IGNORECASE
            )

            is_signup = bool(re.search(
                r'(sign\s*up|register|create\s*account|join|new\s*account)',
                (action or "") + body, re.IGNORECASE
            ))

            if is_signup or 'email' in str(fields).lower():
                form_analysis.append({
                    "action": action or url,
                    "method": "POST",  # default
                    "fields": fields,
                    "selects": selects,
                    "textareas": textareas,
                    "is_signup_form": is_signup,
                })

        # Detect verifications
        verifications = []
        if self.captcha_detector.has_captcha(html):
            verifications.append(VerificationType.CAPTCHA)

        # Check for OAuth buttons
        oauth = []
        for provider in ['google', 'github', 'facebook', 'apple', 'twitter', 'microsoft']:
            if re.search(rf'{provider}|sign[_-]in[_-]with[_-]{provider}', html, re.IGNORECASE):
                oauth.append(provider)
        if oauth:
            verifications.append(VerificationType.OAUTH_ONLY)

        # Check for email field
        has_email = bool(re.search(r'type=["\']email["\']|name=["\'](?:email|e-?mail)', html, re.IGNORECASE))
        if has_email:
            verifications.append(VerificationType.EMAIL)

        # Check for phone/SMS
        has_phone = bool(re.search(r'type=["\']tel["\']|name=["\'](?:phone|mobile|tel)', html, re.IGNORECASE))
        if has_phone:
            verifications.append(VerificationType.SMS)

        return {
            "url": url,
            "platform": platform or self._detect_platform_name(url),
            "forms_found": len(forms),
            "signup_forms": form_analysis,
            "verifications_needed": [v.value for v in verifications],
            "oauth_providers": oauth,
            "html_size": len(html),
        }

    def _detect_platform_name(self, url: str) -> str:
        """Detect platform name from URL."""
        domains = {
            'dev.to': 'dev_to', 'medium.com': 'medium', 'reddit.com': 'reddit',
            'hashnode.com': 'hashnode', 'substack.com': 'substack',
            'news.ycombinator.com': 'hacker_news', 'stackoverflow.com': 'stackoverflow',
            'huggingface.co': 'huggingface', 'github.com': 'github',
            'twitter.com': 'twitter', 'x.com': 'twitter',
        }
        for d, name in domains.items():
            if d in url:
                return name
        # Extract from URL
        m = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if m:
            return m.group(1).replace('.', '_')
        return "unknown"

    def plan_registration(self, url: str, platform: Optional[str] = None,
                          custom_fields: Optional[Dict] = None) -> RegistrationPlan:
        """
        Build a complete registration plan for a platform.
        """
        study = self.study(url, platform)
        verifications = [VerificationType(v) for v in study["verifications_needed"]]

        # Pick the first signup form
        signup_form = None
        for f in study["signup_forms"]:
            if f["is_signup_form"]:
                signup_form = f
                break
        if not signup_form and study["signup_forms"]:
            signup_form = study["signup_forms"][0]

        if not signup_form:
            # Return an empty plan instead of raising
            return RegistrationPlan(
                url=url,
                platform=study["platform"],
                form_action=url,
                fields={},
                verifications=[],
                password_field=None,
                username_field=None,
                email_field=None,
            )

        # Identify key fields
        password_field = None
        username_field = None
        email_field = None
        name_field = None

        for field_info in signup_form["fields"]:
            name = field_info["name"].lower()
            ftype = field_info["type"].lower()
            if ftype == "password" or "password" in name:
                password_field = field_info["name"]
            elif ftype == "email" or "email" in name:
                email_field = field_info["name"]
            elif "username" in name or "user" == name:
                username_field = field_info["name"]
            elif "name" in name and not name_field:
                name_field = field_info["name"]

        # Generate credentials
        name = self.human.realistic_name()
        email_addr = self.email.get_address() if VerificationType.EMAIL in verifications else None
        username = self.human.random_username(prefix=(platform or "user").lower())
        password = self.human.strong_password()

        # Build field map
        fields = {}
        if email_field:
            fields[email_field] = email_addr or self.human.random_email()
        if username_field:
            fields[username_field] = username
        if password_field:
            fields[password_field] = password
        if name_field:
            fields[name_field] = name["full"]
        # First/last name if separate
        for field_info in signup_form["fields"]:
            fname = field_info["name"].lower()
            if "first" in fname and "name" in fname:
                fields[field_info["name"]] = name["first"]
            elif "last" in fname and "name" in fname:
                fields[field_info["name"]] = name["last"]

        # Apply custom fields
        if custom_fields:
            fields.update(custom_fields)

        return RegistrationPlan(
            url=url,
            platform=study["platform"],
            form_action=signup_form["action"],
            fields=fields,
            verifications=verifications,
            oauth_providers=study["oauth_providers"],
            password_field=password_field,
            username_field=username_field,
            email_field=email_field,
        )

    def register(self, url: str, platform: Optional[str] = None,
                 custom_fields: Optional[Dict] = None,
                 auto_verify: bool = True,
                 dry_run: bool = True) -> RegistrationResult:
        """
        Register on a platform.

        dry_run=True: just builds plan and shows what would happen
        dry_run=False: actually attempts registration

        auto_verify=True: automatically handle email/SMS verification codes
        """
        print(f"\n{'='*70}")
        print(f"📝 REGISTERING ON: {url}")
        print(f"{'='*70}\n")

        # Step 1: Study
        print("Step 1: Studying platform...")
        plan = self.plan_registration(url, platform, custom_fields)
        print(f"   ✅ Platform: {plan.platform}")
        print(f"   ✅ Form action: {plan.form_action}")
        print(f"   ✅ Verifications needed: {[v.value for v in plan.verifications]}")
        if plan.oauth_providers:
            print(f"   ℹ️  OAuth available: {plan.oauth_providers}")

        # Step 2: Generate credentials
        print("\nStep 2: Credentials generated...")
        for k, v in plan.fields.items():
            display = v if k != plan.password_field else "•" * 12
            print(f"   {k}: {display}")

        # Step 3: Acquire email/SMS
        email_used = None
        sms_used = None
        if VerificationType.EMAIL in plan.verifications and auto_verify:
            print("\nStep 3: Acquiring temp email...")
            email_used = self.email.get_address()
            print(f"   ✅ Email: {email_used}")
            # Update email field with new addr
            if plan.email_field:
                plan.fields[plan.email_field] = email_used

        if VerificationType.SMS in plan.verifications and auto_verify:
            print("\nStep 3: Acquiring SMS number...")
            try:
                num = self.sms.get_number("receive-smss.com")
                sms_used = num.number
                print(f"   ✅ Phone: {sms_used}")
            except Exception as e:
                print(f"   ⚠️  SMS failed: {e}")

        # Step 4: CAPTCHA
        captcha_solved = False
        if VerificationType.CAPTCHA in plan.verifications:
            print("\nStep 4: CAPTCHA detected...")
            challenge = self.captcha_detector.detect(url)
            if challenge:
                print(f"   Type: {challenge.type}")
                if self.captcha_solver.has_api_key("2captcha"):
                    print("   Solving via 2captcha...")
                    token = self.captcha_solver.solve_2captcha(challenge)
                    if token:
                        plan.fields["g-recaptcha-response"] = token
                        plan.fields["h-captcha-response"] = token
                        captcha_solved = True
                else:
                    print("   ⚠️  No API key. Get one at 2captcha.com (~$3/1000)")

        # Step 5: Submit
        print("\nStep 5: Submitting form...")
        if dry_run:
            print("   ⚠️  DRY RUN — not actually submitting")
            print(f"   Would POST to: {plan.form_action}")
            print(f"   With fields: {list(plan.fields.keys())}")
        else:
            # Actual submission would go here
            print("   ⚠️  Live submission not yet implemented in this version")

        # Step 6: Verification
        verification_code = None
        if auto_verify and not dry_run and VerificationType.EMAIL in plan.verifications:
            print("\nStep 6: Waiting for email verification...")
            verification_code = self.email.wait_for_verification(timeout=60)

        # Build result
        next_steps = []
        if dry_run:
            next_steps.append("Set dry_run=False to actually submit")
        if VerificationType.CAPTCHA in plan.verifications and not captcha_solved:
            next_steps.append("Set CAPTCHA_2CAPTCHA_KEY env var to solve CAPTCHAs")
        if plan.oauth_providers:
            next_steps.append(f"Consider using OAuth: {plan.oauth_providers[0]} (often easier)")

        return RegistrationResult(
            success=dry_run,  # dry runs always "succeed" in planning
            platform=plan.platform,
            credentials=plan.fields,
            email_used=email_used,
            sms_number_used=sms_used,
            verification_code=verification_code,
            captcha_solved=captcha_solved,
            error=None if dry_run else "Live submission not enabled",
            next_steps=next_steps,
        )


# Quick CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: universal_registrar.py <signup_url> [platform_name]")
        print("Example: universal_registrar.py https://dev.to/enter?signup=true dev_to")
        sys.exit(1)

    url = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else None

    reg = UniversalRegistrar()
    result = reg.register(url, platform, dry_run=True)

    print(f"\n{'='*70}")
    print("RESULT:")
    print(f"{'='*70}")
    print(f"Platform: {result.platform}")
    print(f"Success: {result.success}")
    print(f"Email: {result.email_used or 'N/A'}")
    print(f"SMS: {result.sms_number_used or 'N/A'}")
    print(f"Captcha solved: {result.captcha_solved}")
    if result.next_steps:
        print("\nNext steps:")
        for step in result.next_steps:
            print(f"  - {step}")
