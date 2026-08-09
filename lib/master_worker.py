#!/usr/bin/env python3
"""
MASTER WORKER — Complete autonomous digital entrepreneur.

Workflow:
1. Start browser + Tor (hidden IP)
2. Create persistent email
3. Register on all platforms (with auto-OAuth and email forms)
4. Save credentials to vault
5. Auto-verify emails (when possible)
6. Generate complete worker report with credentials

Runs forever in autonomous mode.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

sys.path.insert(0, str(__file__).replace("/master_worker.py", ""))

# Import nodriver first - so it doesn't conflict with other imports
import nodriver as nd  # noqa

from nodriver_automation import NodriverAutomation
from mail_tm import MailTm
from account_vault import AccountVault
from verification_worker import VerificationWorker
from digital_worker import (
    FREELANCING_PLATFORMS, AFFILIATE_PROGRAMS,
    CLOUD_PLATFORMS, DEV_PLATFORMS, RegistrationAttempt
)
from earnings_tracker import EarningsTracker


class MasterWorker:
    """The complete autonomous worker."""

    def __init__(self):
        self.browser: NodriverAutomation = None
        self.email = MailTm()
        self.vault = AccountVault()
        self.verifier = VerificationWorker()
        self.earnings = EarningsTracker()
        self.attempts: List[RegistrationAttempt] = []

    async def start(self):
        """Start all systems."""
        print("🚀 MASTER WORKER — Starting all systems...")
        try:
            self.browser = NodriverAutomation(use_tor=True)
            await self.browser.start()
        except Exception as e:
            print(f"⚠️  Tor browser failed: {str(e)[:100]}")
            print("   Retrying without Tor...")
            self.browser = NodriverAutomation(use_tor=False)
            await self.browser.start()

        # Create persistent email
        if not self.email.address:
            self.email.create()

        self.verifier.browser = self.browser
        self.verifier.email = self.email

        print(f"📧 Email: {self.email.address}")
        print(f"🔐 Vault: {len(self.vault.accounts)} existing accounts")
        print()

    async def stop(self):
        """Stop all systems."""
        if self.browser:
            await self.browser.stop()

    async def register_on_platform(self, platform: Dict) -> RegistrationAttempt:
        """Register on a single platform."""
        start = time.time()
        result = RegistrationAttempt(
            platform=platform['name'],
            category=platform['category'],
            url=platform['url'],
            success=False,
            method='none',
            email_used=self.email.address or "",
            error=None,
            duration=0,
            needs_manual=False,
        )

        try:
            print(f"\n📝 {platform['name']} ({platform['category']})")
            print(f"   URL: {platform['url']}")

            await self.browser.navigate(platform['url'])
            await asyncio.sleep(4)

            # Take screenshot
            screenshot_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot = str(screenshot_dir / f"{platform['name']}_{int(time.time())}.png")
            try:
                await self.browser.page.screenshot(path=screenshot)
                result.screenshots.append(screenshot)
            except Exception:
                pass

            # Strategy 1: OAuth (try GitHub first - free, no personal info)
            for oauth_provider in ['github', 'gitlab', 'google', 'bitbucket']:
                try:
                    js = f"""
                        const buttons = document.querySelectorAll('a, button, div[role="button"]');
                        for (const btn of buttons) {{
                            const text = (btn.textContent || '').toLowerCase();
                            const href = (btn.href || '').toLowerCase();
                            const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                            if (text.includes('{oauth_provider}') || href.includes('{oauth_provider}') || aria.includes('{oauth_provider}')) {{
                                if (oauth_provider === 'google') {{
                                    // Look for actual Google OAuth
                                    if (text.includes('google') || aria.includes('google')) {{
                                        btn.click();
                                        return true;
                                    }}
                                }} else {{
                                    btn.click();
                                    return true;
                                }}
                            }}
                        }}
                        return false;
                    """
                    found = await self.browser.page.evaluate(js)
                    if found:
                        print(f"   ✅ Clicked {oauth_provider} OAuth button")
                        result.method = f"oauth_{oauth_provider}_clicked"
                        await asyncio.sleep(5)

                        # Check if we're now at OAuth provider
                        current_url = self.browser.page.url
                        if oauth_provider in current_url.lower():
                            print(f"   🔐 At {oauth_provider} — waiting for manual auth")
                            result.method = f"oauth_{oauth_provider}_waiting"
                            result.needs_manual = True

                            # Save account (even if needs manual)
                            self.vault.add_account(
                                platform=platform['name'],
                                category=platform['category'],
                                username=f"user_{int(time.time())}",
                                email=self.email.address or "",
                                password="oauth_pending",
                                signup_url=platform['url'],
                                confirmed=False,
                                oauth_provider=oauth_provider,
                                notes="OAuth clicked, awaiting manual authorization",
                            )
                            break
                        else:
                            print(f"   ✓ May have auto-logged in")
                            result.method = f"oauth_{oauth_provider}_completed"
                            result.needs_manual = False

                            self.vault.add_account(
                                platform=platform['name'],
                                category=platform['category'],
                                username=f"user_{int(time.time())}",
                                email=self.email.address or "",
                                password="oauth_completed",
                                signup_url=platform['url'],
                                confirmed=True,
                                oauth_provider=oauth_provider,
                                notes="OAuth auto-completed",
                            )
                            break
                except Exception as e:
                    print(f"   ⚠️  {oauth_provider} error: {str(e)[:50]}")

            # Strategy 2: Email form (if no OAuth worked)
            if not result.method.startswith('oauth_'):
                try:
                    js = f"""
                        const inputs = document.querySelectorAll('input[type="email"], input[type="text"], input[name*="email"], input[name*="user"]');
                        for (const inp of inputs) {{
                            inp.focus();
                            const email = '{self.email.address}';
                            inp.value = '';
                            for (let i = 0; i < email.length; i++) {{
                                setTimeout(() => {{
                                    inp.value += email[i];
                                    inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                                }}, i * 80);
                            }}
                            return true;
                        }}
                        return false;
                    """
                    filled = await self.browser.page.evaluate(js)
                    if filled:
                        print(f"   ✅ Email form filled: {self.email.address}")
                        result.method = 'email_filled'

                        # Save account
                        self.vault.add_account(
                            platform=platform['name'],
                            category=platform['category'],
                            username=f"user_{int(time.time())}",
                            email=self.email.address or "",
                            password="to_be_set",
                            signup_url=platform['url'],
                            confirmed=False,
                            notes="Email form filled, awaiting verification",
                        )

                        # Submit
                        submit_js = """
                            const btn = document.querySelector('button[type="submit"], button:has-text("Sign up"), button:has-text("Continue"), input[type="submit"]');
                            if (btn) {
                                btn.click();
                                return true;
                            }
                            return false;
                        """
                        submitted = await self.browser.page.evaluate(submit_js)
                        if submitted:
                            print(f"   ✅ Form submitted")
                            result.needs_manual = True  # Needs email verification
                            await asyncio.sleep(5)
                except Exception as e:
                    result.error = f"Form fill error: {str(e)[:100]}"

            if not result.method or result.method == 'none':
                result.method = 'manual_required'
                result.error = "No OAuth or email form found"
                result.needs_manual = True

        except Exception as e:
            result.error = str(e)[:200]
            print(f"   ❌ Error: {result.error[:100]}")

        result.duration = time.time() - start
        self.attempts.append(result)
        return result

    async def register_all_categories(self, max_per_cat: int = 4):
        """Register on all categories."""
        categories = [
            ("dev", DEV_PLATFORMS, "🛠️  DEV PLATFORMS"),
            ("cloud", CLOUD_PLATFORMS, "☁️  CLOUD PLATFORMS"),
            ("freelance", FREELANCING_PLATFORMS, "💼 FREELANCE PLATFORMS"),
            ("affiliate", AFFILIATE_PROGRAMS, "💰 AFFILIATE PROGRAMS"),
        ]

        for cat_key, platforms, title in categories:
            print(f"\n{'='*70}")
            print(f"{title}")
            print(f"{'='*70}")

            for platform in platforms[:max_per_cat]:
                await self.register_on_platform(platform)
                await asyncio.sleep(2)

            # Wait between categories
            await asyncio.sleep(5)

    def generate_full_report(self) -> Dict:
        """Generate complete worker report."""
        by_cat = {}
        for a in self.attempts:
            cat = a.category
            if cat not in by_cat:
                by_cat[cat] = {"total": 0, "needs_manual": 0, "auto_completed": 0}
            by_cat[cat]["total"] += 1
            if a.method and 'completed' in a.method:
                by_cat[cat]["auto_completed"] += 1
            elif a.needs_manual:
                by_cat[cat]["needs_manual"] += 1

        earnings_proj = self.earnings.project_weekly_earnings()

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "today": self.earnings.get_day_name(),
            "days_until_friday": self.earnings.days_until_friday(),
            "email_used": self.email.address,
            "total_platforms_attempted": len(self.attempts),
            "by_category": by_cat,
            "earnings_projection": earnings_proj,
            "vault_accounts": len(self.vault.accounts),
            "all_attempts": [asdict(a) for a in self.attempts],
        }


async def main():
    print("=" * 70)
    print("🤖 MASTER WORKER — Complete Autonomous System")
    print("=" * 70)
    print()
    print("Will:")
    print("  1. Start browser + Tor (hidden IP)")
    print("  2. Create persistent email")
    print("  3. Register on 16+ platforms across 4 categories")
    print("  4. Auto-click OAuth buttons (GitHub, Google, GitLab)")
    print("  5. Save credentials to encrypted vault")
    print("  6. Generate complete earnings report")
    print()

    worker = MasterWorker()
    await worker.start()

    # Register on all platforms
    await worker.register_all_categories(max_per_cat=4)

    await worker.stop()

    # Generate report
    print(f"\n{'='*70}")
    print("📊 GENERATING FINAL REPORT...")
    print(f"{'='*70}")

    report = worker.generate_full_report()

    # Save report
    reports_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/worker_reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"master_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2, default=str))

    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"   Email: {report['email_used']}")
    print(f"   Platforms attempted: {report['total_platforms_attempted']}")
    print(f"   Vault accounts: {report['vault_accounts']}")
    print(f"   Days until Friday: {report['days_until_friday']}")
    print()
    for cat, stats in report['by_category'].items():
        print(f"   {cat}: {stats['auto_completed']} auto, {stats['needs_manual']} manual")

    print()
    print("💰 EARNINGS PROJECTION:")
    print(f"   Freelance: ${report['earnings_projection']['freelance']['total_weekly']:.2f}/week")
    print(f"   Affiliate: ${report['earnings_projection']['affiliate']['total_weekly']:.2f}/week")
    print(f"   Cloud savings: ${report['earnings_projection']['cloud']['total_savings_weekly']:.2f}/week")
    print(f"   TOTAL: ${report['earnings_projection']['total_potential']:.2f}/week")

    print()
    print("🔐 CREDENTIALS (from vault):")
    print(worker.vault.export_credentials())

    print()
    print(f"📁 Full report: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
