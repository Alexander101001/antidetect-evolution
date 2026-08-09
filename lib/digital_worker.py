#!/usr/bin/env python3
"""
Digital Worker — Complete autonomous freelancer/affiliate/cloud registration system.

Registers on:
1. Freelancing platforms (Upwork, Fiverr, Freelancer, etc.)
2. Affiliate marketing programs (Amazon, ClickBank, etc.)
3. Cloud platforms (HuggingFace, Vercel, etc.)
4. Development platforms (GitHub, GitLab, etc.)

Uses:
- nodriver (raw CDP, 100% human score)
- Tor (hidden IP)
- Mail.tm (persistent email)
- Free SMS services
- Human behavior simulation
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field

sys.path.insert(0, str(__file__).replace("/digital_worker.py", ""))

from nodriver_automation import NodriverAutomation, STEALTH_INIT
from mail_tm import MailTm
from email_service import GuerrillaMail
from stealth import HumanBehavior


# ════════════════════════════════════════════════════════════════════
# COMPREHENSIVE PLATFORM DATABASE
# ════════════════════════════════════════════════════════════════════

FREELANCING_PLATFORMS = [
    {"name": "Upwork", "url": "https://www.upwork.com/signup", "oauth": ["google", "apple"], "difficulty": "high", "category": "freelance"},
    {"name": "Fiverr", "url": "https://www.fiverr.com/join", "oauth": ["google", "facebook", "apple"], "difficulty": "high", "category": "freelance"},
    {"name": "Freelancer", "url": "https://www.freelancer.com/signup", "oauth": ["google", "facebook"], "difficulty": "medium", "category": "freelance"},
    {"name": "Toptal", "url": "https://www.toptal.com/signup", "oauth": [], "difficulty": "extreme", "category": "freelance_vetted"},
    {"name": "Guru", "url": "https://www.guru.com/signup", "oauth": ["google", "facebook"], "difficulty": "medium", "category": "freelance"},
    {"name": "PeoplePerHour", "url": "https://www.peopleperhour.com/signup", "oauth": ["google", "facebook"], "difficulty": "medium", "category": "freelance"},
    {"name": "99Designs", "url": "https://99designs.com/signup", "oauth": ["google", "facebook"], "difficulty": "medium", "category": "freelance_design"},
    {"name": "Contra", "url": "https://contra.com/signup", "oauth": ["google"], "difficulty": "low", "category": "freelance"},
    {"name": "LinkedIn Services", "url": "https://www.linkedin.com/signup", "oauth": ["google"], "difficulty": "high", "category": "freelance"},
    {"name": "Hireable", "url": "https://hireable.io/signup", "oauth": ["github", "linkedin"], "difficulty": "low", "category": "freelance"},
    {"name": "Remotive", "url": "https://remotive.com/signup", "oauth": ["google"], "difficulty": "medium", "category": "freelance_remote"},
    {"name": "Workana", "url": "https://www.workana.com/signup", "oauth": ["google", "facebook"], "difficulty": "medium", "category": "freelance"},
    {"name": "Crunchboard", "url": "https://www.crunchboard.com/signup", "oauth": ["linkedin"], "difficulty": "low", "category": "freelance"},
    {"name": "AngelList", "url": "https://wellfound.com/signup", "oauth": ["google", "github"], "difficulty": "medium", "category": "freelance_startup"},
    {"name": "Crew", "url": "https://crew.co/signup", "oauth": ["google"], "difficulty": "low", "category": "freelance"},
    {"name": "Dribbble", "url": "https://dribbble.com/signup", "oauth": ["google", "twitter"], "difficulty": "medium", "category": "freelance_design"},
    {"name": "Behance", "url": "https://www.behance.net/signup", "oauth": ["google", "apple", "facebook"], "difficulty": "medium", "category": "freelance_design"},
    {"name": "GitHub Jobs", "url": "https://github.com/join", "oauth": ["google", "apple"], "difficulty": "medium", "category": "freelance_dev"},
]

AFFILIATE_PROGRAMS = [
    {"name": "Amazon Associates", "url": "https://affiliate-program.amazon.com/", "oauth": ["google"], "difficulty": "medium", "category": "affiliate"},
    {"name": "ClickBank", "url": "https://accounts.clickbank.com/master/signup.htm", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "ShareASale", "url": "https://account.shareasale.com/merchant/signup/", "oauth": [], "difficulty": "medium", "category": "affiliate"},
    {"name": "CJ Affiliate", "url": "https://signup.cj.com/member/signup", "oauth": [], "difficulty": "medium", "category": "affiliate"},
    {"name": "Rakuten", "url": "https://signup.rakuten.com/", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Awin", "url": "https://www.awin.com/", "oauth": [], "difficulty": "medium", "category": "affiliate"},
    {"name": "Impact", "url": "https://impact.com/", "oauth": [], "difficulty": "medium", "category": "affiliate"},
    {"name": "PartnerStack", "url": "https://partnerstack.com/", "oauth": [], "difficulty": "medium", "category": "affiliate"},
    {"name": "eBay Partner", "url": "https://partnernetwork.ebay.com/", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Etsy Affiliate", "url": "https://www.etsy.com/affiliates", "oauth": [], "difficulty": "medium", "category": "affiliate"},
    {"name": "WP Engine", "url": "https://wpengine.com/affiliates/", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Bluehost", "url": "https://www.bluehost.com/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Hostinger", "url": "https://www.hostinger.com/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Shopify", "url": "https://www.shopify.com/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Semrush", "url": "https://www.semrush.com/lp/affiliate-program/", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "HubSpot", "url": "https://www.hubspot.com/partners/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "ConvertKit", "url": "https://convertkit.com/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Teachable", "url": "https://teachable.com/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "Thinkific", "url": "https://www.thinkific.com/affiliates", "oauth": [], "difficulty": "low", "category": "affiliate"},
    {"name": "GetResponse", "url": "https://www.getresponse.com/affiliates.html", "oauth": [], "difficulty": "low", "category": "affiliate"},
]

CLOUD_PLATFORMS = [
    {"name": "Hugging Face", "url": "https://huggingface.co/join", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "Vercel", "url": "https://vercel.com/signup", "oauth": ["github"], "difficulty": "easy", "category": "cloud"},
    {"name": "Render", "url": "https://render.com/register", "oauth": ["github", "gitlab"], "difficulty": "easy", "category": "cloud"},
    {"name": "Railway", "url": "https://railway.app/login", "oauth": ["github"], "difficulty": "easy", "category": "cloud"},
    {"name": "Netlify", "url": "https://app.netlify.com/signup", "oauth": ["github"], "difficulty": "easy", "category": "cloud"},
    {"name": "Replit", "url": "https://replit.com/signup", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "Cloudflare Pages", "url": "https://pages.cloudflare.com/sign-up", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "Glitch", "url": "https://glitch.com/signup", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "GitLab.com", "url": "https://gitlab.com/users/sign_up", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "Koyeb", "url": "https://app.koyeb.com/auth/signup", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "Cyclic.sh", "url": "https://www.cyclic.sh/", "oauth": ["github"], "difficulty": "easy", "category": "cloud"},
    {"name": "Adaptable.io", "url": "https://adaptable.io/register", "oauth": ["github"], "difficulty": "easy", "category": "cloud"},
    {"name": "GitHub Codespaces", "url": "https://github.com/features/codespaces", "oauth": ["github"], "difficulty": "easy", "category": "cloud"},
    {"name": "StackBlitz", "url": "https://stackblitz.com/signup", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
    {"name": "CodeSandbox", "url": "https://codesandbox.io/signup", "oauth": ["github", "google"], "difficulty": "easy", "category": "cloud"},
]

DEV_PLATFORMS = [
    {"name": "GitHub", "url": "https://github.com/signup", "oauth": ["google", "apple"], "difficulty": "hard", "category": "dev"},
    {"name": "GitLab", "url": "https://gitlab.com/users/sign_up", "oauth": ["github", "google"], "difficulty": "medium", "category": "dev"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/account/signup/", "oauth": ["google"], "difficulty": "medium", "category": "dev"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/signup", "oauth": ["google", "github"], "difficulty": "easy", "category": "dev"},
    {"name": "npm", "url": "https://www.npmjs.com/signup", "oauth": ["github"], "difficulty": "easy", "category": "dev"},
    {"name": "PyPI", "url": "https://pypi.org/account/register/", "oauth": ["google", "github"], "difficulty": "easy", "category": "dev"},
    {"name": "Hashnode", "url": "https://hashnode.com/onboard", "oauth": ["github", "google"], "difficulty": "easy", "category": "dev"},
    {"name": "Dev.to", "url": "https://dev.to/enter?signup=true", "oauth": ["github", "twitter"], "difficulty": "easy", "category": "dev"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com/users/signup", "oauth": ["google", "github"], "difficulty": "medium", "category": "dev"},
]


@dataclass
class RegistrationAttempt:
    """One platform registration attempt."""
    platform: str
    category: str
    url: str
    success: bool
    method: str  # 'oauth_github', 'email', 'google', 'github_login_required'
    email_used: Optional[str]
    error: Optional[str]
    duration: float
    needs_manual: bool
    screenshots: List[str] = field(default_factory=list)


class DigitalWorker:
    """The autonomous digital entrepreneur."""

    def __init__(self):
        self.human = HumanBehavior()
        self.email = MailTm()
        self.attempts: List[RegistrationAttempt] = []
        self.reports_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/worker_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.browser = None

    async def start(self):
        """Start the browser."""
        self.browser = NodriverAutomation(use_tor=True)
        await self.browser.start()
        # Create persistent email
        self.email.create()
        print(f"📧 Email ready: {self.email.address}")

    async def stop(self):
        """Stop the browser."""
        if self.browser:
            await self.browser.stop()

    async def register_oauth(self, platform: Dict) -> RegistrationAttempt:
        """Register via OAuth (clicks the OAuth button)."""
        start = time.time()
        result = RegistrationAttempt(
            platform=platform['name'],
            category=platform['category'],
            url=platform['url'],
            success=False,
            method='oauth_clicked',
            email_used=self.email.address,
            error=None,
            duration=0,
            needs_manual=True,
        )

        try:
            print(f"\n📝 {platform['name']} ({platform['category']})")

            # Navigate to signup
            await self.browser.navigate(platform['url'])
            await asyncio.sleep(3)

            # Take initial screenshot
            screenshot_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot = str(screenshot_dir / f"{platform['name']}_step1.png")
            try:
                await self.browser.page.screenshot(path=screenshot)
                result.screenshots.append(screenshot)
            except Exception:
                pass

            # Try to find and click OAuth button
            oauth_providers = platform.get('oauth', [])
            if not oauth_providers:
                result.method = 'email_required'
                result.error = "No OAuth available, email signup needed"
                result.duration = time.time() - start
                return result

            # Look for OAuth buttons
            clicked = False
            for provider in oauth_providers:
                try:
                    # Try clicking OAuth button
                    js = f"""
                        const buttons = document.querySelectorAll('a, button');
                        for (const btn of buttons) {{
                            const text = (btn.textContent || '').toLowerCase();
                            const href = (btn.href || '').toLowerCase();
                            if (text.includes('{provider}') || href.includes('{provider}')) {{
                                btn.click();
                                return true;
                            }}
                        }}
                        return false;
                    """
                    found = await self.browser.page.evaluate(js)
                    if found:
                        print(f"   ✅ Clicked {provider} button")
                        result.method = f'oauth_{provider}'
                        clicked = True
                        await asyncio.sleep(3)
                        break
                except Exception as e:
                    print(f"   ⚠️  Could not click {provider}: {str(e)[:50]}")

            if not clicked:
                # Take screenshot of page state
                screenshot2 = str(screenshot_dir / f"{platform['name']}_no_oauth.png")
                try:
                    await self.browser.page.screenshot(path=screenshot2)
                    result.screenshots.append(screenshot2)
                except Exception:
                    pass

                result.method = 'no_oauth_found'
                result.error = f"OAuth buttons not found for: {oauth_providers}"
                result.duration = time.time() - start
                return result

            # Wait for redirect
            await asyncio.sleep(5)

            # Check current URL
            current_url = self.browser.page.url
            result.duration = time.time() - start

            # If we ended up at OAuth provider, we need manual authorization
            if any(provider in current_url.lower() for provider in oauth_providers):
                result.success = True
                result.needs_manual = True
                result.method = f"oauth_{oauth_providers[0]}_waiting_auth"
                print(f"   🔐 At OAuth provider — manual auth required")
                print(f"   URL: {current_url[:80]}")
            else:
                # We stayed on the same site, OAuth may have completed or failed
                body_text = await self.browser.page.evaluate("document.body.innerText") or ""
                if any(kw in body_text.lower() for kw in ['dashboard', 'welcome', 'logged in', 'verify your email']):
                    result.success = True
                    result.needs_manual = False
                    print(f"   ✅ Account created!")
                else:
                    result.success = False
                    result.error = "OAuth flow unclear"
                    print(f"   ⚠️  OAuth flow unclear")

        except Exception as e:
            result.error = str(e)[:200]
            print(f"   ❌ Error: {result.error[:100]}")

        result.duration = time.time() - start
        return result

    async def register_email(self, platform: Dict) -> RegistrationAttempt:
        """Register via email form."""
        start = time.time()
        result = RegistrationAttempt(
            platform=platform['name'],
            category=platform['category'],
            url=platform['url'],
            success=False,
            method='email_form',
            email_used=self.email.address,
            error=None,
            duration=0,
            needs_manual=False,
        )

        try:
            print(f"\n📝 {platform['name']} (email signup)")
            await self.browser.navigate(platform['url'])
            await asyncio.sleep(3)

            # Try to fill email field
            js = f"""
                // Find email input
                const emailInput = document.querySelector('input[type=\"email\"], input[name*=\"email\"], input[id*=\"email\"]');
                if (emailInput) {{
                    emailInput.focus();
                    // Human-like typing
                    const email = '{self.email.address}';
                    emailInput.value = '';
                    for (let i = 0; i < email.length; i++) {{
                        setTimeout(() => {{
                            emailInput.value += email[i];
                            emailInput.dispatchEvent(new Event('input', {{bubbles: true}}));
                        }}, i * 100);
                    }}
                    return true;
                }}
                return false;
            """
            found = await self.browser.page.evaluate(js)
            if found:
                await asyncio.sleep(2)
                print(f"   ✅ Email field filled: {self.email.address}")
                result.method = 'email_form_filled'

                # Try to submit
                submit_js = """
                    const submit = document.querySelector('button[type=\"submit\"], input[type=\"submit\"]');
                    if (submit) {
                        submit.click();
                        return true;
                    }
                    return false;
                """
                submitted = await self.browser.page.evaluate(submit_js)
                if submitted:
                    await asyncio.sleep(5)
                    print(f"   ✅ Form submitted")
                    result.success = True
                    result.needs_manual = True  # Usually needs email verification
            else:
                result.error = "Email input not found"

        except Exception as e:
            result.error = str(e)[:200]

        result.duration = time.time() - start
        return result

    async def register_all_in_category(self, category: str, max_attempts: int = 5) -> List[RegistrationAttempt]:
        """Register on all platforms in a category."""
        all_platforms = {
            'freelance': FREELANCING_PLATFORMS,
            'affiliate': AFFILIATE_PROGRAMS,
            'cloud': CLOUD_PLATFORMS,
            'dev': DEV_PLATFORMS,
        }

        platforms = all_platforms.get(category, [])[:max_attempts]
        results = []

        for platform in platforms:
            try:
                if platform.get('oauth'):
                    result = await self.register_oauth(platform)
                else:
                    result = await self.register_email(platform)

                results.append(result)
                self.attempts.append(result)

                # Wait between platforms
                await asyncio.sleep(2)

            except Exception as e:
                print(f"   ❌ Failed {platform['name']}: {str(e)[:80]}")

        return results

    def generate_report(self) -> Dict:
        """Generate final work report."""
        by_category = {}
        for attempt in self.attempts:
            cat = attempt.category
            if cat not in by_category:
                by_category[cat] = {"total": 0, "success": 0, "needs_manual": 0, "failed": 0, "platforms": []}
            by_category[cat]["total"] += 1
            if attempt.success and not attempt.needs_manual:
                by_category[cat]["success"] += 1
            elif attempt.needs_manual:
                by_category[cat]["needs_manual"] += 1
            else:
                by_category[cat]["failed"] += 1
            by_category[cat]["platforms"].append(attempt.platform)

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_attempts": len(self.attempts),
            "by_category": by_category,
            "details": [asdict(a) for a in self.attempts],
        }

    def save_report(self, report: Dict):
        """Save report to file."""
        filename = f"worker_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        path = self.reports_dir / filename
        path.write_text(json.dumps(report, indent=2, default=str))
        print(f"\n📁 Report saved: {path}")

    def print_summary(self, report: Dict):
        """Print work summary."""
        print(f"\n{'='*70}")
        print(f"📊 DIGITAL WORKER REPORT")
        print(f"{'='*70}")
        print(f"Total platforms attempted: {report['total_attempts']}")
        print()
        for cat, stats in report["by_category"].items():
            print(f"📁 {cat.upper()}:")
            print(f"   Total: {stats['total']}")
            print(f"   ✅ Success: {stats['success']}")
            print(f"   🔐 Needs manual: {stats['needs_manual']}")
            print(f"   ❌ Failed: {stats['failed']}")
            print(f"   Platforms: {', '.join(stats['platforms'])}")
            print()


async def main():
    """Main worker flow."""
    print("=" * 70)
    print("🤖 DIGITAL WORKER — Autonomous Registration System")
    print("=" * 70)
    print()
    print("Will register on:")
    print("  - Freelancing platforms (Upwork, Fiverr, etc.)")
    print("  - Affiliate programs (Amazon, ClickBank, etc.)")
    print("  - Cloud platforms (Vercel, Render, etc.)")
    print("  - Dev platforms (GitHub, GitLab, etc.)")
    print()

    worker = DigitalWorker()
    await worker.start()

    # Run registration on each category
    for category in ['cloud', 'dev', 'freelance', 'affiliate']:
        print(f"\n{'='*70}")
        print(f"📁 CATEGORY: {category.upper()}")
        print(f"{'='*70}")
        await worker.register_all_in_category(category, max_attempts=3)
        await asyncio.sleep(3)

    await worker.stop()

    # Generate and save report
    report = worker.generate_report()
    worker.save_report(report)
    worker.print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())
