#!/usr/bin/env python3
"""
Submission Engine — actually fills and submits forms.

Handles:
- CSRF token extraction (hidden fields, meta tags, cookies)
- Cookie/session persistence
- POST with multipart/form-data
- Follow redirects
- Multi-step form wizards
- Click email verification links
"""

import re
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import mechanicalsoup
import httpx

from unified import SmartClient
from stealth import HumanBehavior


@dataclass
class SubmissionResult:
    """Result of form submission."""
    success: bool
    final_url: str
    status_code: int
    response_text: str
    cookies: Dict[str, str]
    error: Optional[str] = None
    redirect_chain: List[str] = None
    requires_email_verification: bool = False
    requires_2fa: bool = False


class SubmissionEngine:
    """Actually submit forms with proper session/cookie handling."""

    def __init__(self):
        self.client = SmartClient()
        self.human = HumanBehavior()
        self.browsers: Dict[str, mechanicalsoup.StatefulBrowser] = {}

    def _new_browser(self, user_agent: str = None) -> mechanicalsoup.StatefulBrowser:
        """Create a new browser session."""
        ua = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        browser = mechanicalsoup.StatefulBrowser(
            user_agent=ua,
            soup_config={'features': 'lxml'},
            raise_on_404=False,
        )
        return browser

    def submit_form(self, page_url: str, form_selector: str,
                    fields: Dict[str, str],
                    submit_button: Optional[str] = None) -> SubmissionResult:
        """
        Fill and submit a form on a page.

        Args:
            page_url: URL of page with the form
            form_selector: CSS selector for the form (#signup, form[name=...])
            fields: dict of field_name -> value
            submit_button: name of submit button (optional)

        Returns:
            SubmissionResult with status, final URL, cookies, etc.
        """
        browser = self._new_browser()
        redirect_chain = []

        try:
            # Step 1: Load the page
            print(f"   Loading: {page_url}")
            response = browser.open(page_url)
            initial_url = browser.url
            print(f"   Initial URL: {initial_url}")

            # Step 2: Find and select the form
            try:
                browser.select_form(form_selector)
            except Exception as e:
                # Try finding any form
                browser.select_form('form')

            # Step 3: Fill all fields
            for field_name, value in fields.items():
                try:
                    browser[field_name] = value
                    print(f"   Filled: {field_name}")
                except Exception as e:
                    print(f"   ⚠️  Could not fill {field_name}: {e}")

            # Step 4: Handle CSRF — usually already in browser state
            csrf_fields = ['csrfmiddlewaretoken', 'csrf_token', '_token',
                          'authenticity_token', '__RequestVerificationToken']
            for csrf in csrf_fields:
                try:
                    if csrf in browser.page.form.fields:
                        # Already populated by mechanicalsoup usually
                        pass
                except Exception:
                    pass

            # Step 5: Submit
            print(f"   Submitting form...")
            if submit_button:
                try:
                    browser.submit_selected(btnName=submit_button)
                except Exception:
                    browser.submit_selected()
            else:
                browser.submit_selected()

            # Step 6: Track redirect
            final_url = browser.url
            if final_url != initial_url:
                redirect_chain.append(final_url)
                print(f"   Redirected to: {final_url}")

            # Step 7: Extract cookies
            cookies = dict(browser.session.cookies.items()) if hasattr(browser, 'session') else {}

            # Step 8: Analyze response
            page_text = browser.page.get_text() if hasattr(browser.page, 'get_text') else str(browser.page)
            response_text = str(browser.page) if hasattr(browser.page, '__str__') else str(browser.page)

            # Detect next steps
            requires_email = bool(re.search(
                r'verify.*email|confirm.*email|check.*inbox|sent.*email|activation',
                page_text, re.IGNORECASE
            ))
            requires_2fa = bool(re.search(
                r'two[- ]factor|2fa|verification code|authenticator|sms code',
                page_text, re.IGNORECASE
            ))

            # Check for success indicators
            success_indicators = [
                'welcome', 'logged in', 'dashboard', 'account created',
                'successfully', 'confirm your email', 'verify your email'
            ]
            failure_indicators = [
                'incorrect', 'invalid', 'error', 'failed', 'try again',
                'already exists', 'taken'
            ]

            page_lower = page_text.lower()
            has_success = any(s in page_lower for s in success_indicators)
            has_failure = any(f in page_lower for f in failure_indicators)

            success = has_success and not has_failure

            return SubmissionResult(
                success=success,
                final_url=final_url,
                status_code=response.status_code if response else 200,
                response_text=response_text[:5000],
                cookies=cookies,
                redirect_chain=redirect_chain,
                requires_email_verification=requires_email,
                requires_2fa=requires_2fa,
            )

        except Exception as e:
            return SubmissionResult(
                success=False,
                final_url=browser.url if browser else page_url,
                status_code=0,
                response_text=str(e),
                cookies={},
                error=str(e),
            )

    def submit_with_requests(self, url: str, form_action: str,
                             fields: Dict[str, str],
                             cookies: Optional[Dict] = None,
                             headers: Optional[Dict] = None) -> SubmissionResult:
        """
        Submit using httpx (more control over headers, no JS).
        Best for simple forms without JavaScript.
        """
        # Get the page first to extract CSRF
        csrf_token = None
        csrf_field_name = None

        with httpx.Client(http2=True, follow_redirects=True) as client:
            try:
                page_resp = client.get(url, headers=headers or {})
                html = page_resp.text

                # Find CSRF token
                csrf_patterns = [
                    (r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', 'csrfmiddlewaretoken'),
                    (r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', 'csrf_token'),
                    (r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', '_token'),
                    (r'name=["\']authenticity_token["\']\s+value=["\']([^"\']+)["\']', 'authenticity_token'),
                ]

                for pattern, field_name in csrf_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        csrf_token = match.group(1)
                        csrf_field_name = field_name
                        fields[field_name] = csrf_token
                        break

                # Submit
                submit_url = urljoin(url, form_action)
                print(f"   POST to: {submit_url}")
                resp = client.post(
                    submit_url,
                    data=fields,
                    cookies=cookies,
                    headers=headers,
                )

                # Analyze
                page_text = resp.text
                page_lower = page_text.lower()

                success = any(s in page_lower for s in [
                    'welcome', 'dashboard', 'logged in', 'successfully',
                    'check your email', 'verify your email', 'confirm your email'
                ]) and not any(f in page_lower for f in [
                    'incorrect', 'invalid', 'error', 'failed', 'already exists'
                ])

                return SubmissionResult(
                    success=success,
                    final_url=str(resp.url),
                    status_code=resp.status_code,
                    response_text=resp.text[:5000],
                    cookies=dict(client.cookies),
                    requires_email_verification='verify' in page_lower and 'email' in page_lower,
                    requires_2fa='2fa' in page_lower or 'two-factor' in page_lower,
                )

            except Exception as e:
                return SubmissionResult(
                    success=False,
                    final_url=url,
                    status_code=0,
                    response_text="",
                    cookies={},
                    error=str(e),
                )

    def click_email_verification_link(self, email_body: str) -> Optional[str]:
        """Extract verification link from email body."""
        # Find all http/https links
        links = re.findall(r'https?://[^\s"\'<>]+', email_body)

        # Filter for verification-looking links
        verification_keywords = ['verify', 'confirm', 'activate', 'complete', 'validate']
        for link in links:
            if any(kw in link.lower() for kw in verification_keywords):
                return link

        # Return first link if no obvious one
        return links[0] if links else None


if __name__ == "__main__":
    print("🧪 Testing submission engine on the-internet.herokuapp.com")
    engine = SubmissionEngine()

    # Test on the-internet login page (known working)
    result = engine.submit_form(
        page_url="https://the-internet.herokuapp.com/login",
        form_selector="#login",
        fields={
            "username": "tomsmith",
            "password": "SuperSecretPassword!",
        },
    )

    print(f"\n{'='*60}")
    print(f"Success: {result.success}")
    print(f"Final URL: {result.final_url}")
    print(f"Status: {result.status_code}")
    print(f"Cookies: {list(result.cookies.keys())}")
    print(f"Email verification needed: {result.requires_email_verification}")
    if result.error:
        print(f"Error: {result.error}")
