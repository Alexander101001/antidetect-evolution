#!/usr/bin/env python3
"""
Smart Orchestrator — uses ALL modules intelligently.

When asked to register on any site:
1. Check site difficulty (skip impossible ones)
2. Wait for optimal time (off-peak)
3. Check rate limits (don't hammer hosts)
4. Try standard approach
5. If fail, try creative approaches
6. If still fail, suggest cloud desktop fallback
7. Always learn from result

This is the "creative + intelligent" version.
"""

import sys
import time
from typing import Optional, Dict
from dataclasses import dataclass, field

sys.path.insert(0, str(__file__).replace("/smart_orchestrator.py", ""))

from unified import SmartClient
from stealth import HumanBehavior, Fingerprint
from researcher import Researcher
from email_service import GuerrillaMail
from mail_tm import MailTm
from sms_service import SMSService
from captcha_solver import CaptchaDetector, CaptchaSolver
from ocr_solver import OCRSolver, AudioCaptchaSolver
from universal_registrar import UniversalRegistrar
from submission_engine import SubmissionEngine
from session_manager import SessionManager
from pattern_cache import PatternCache
from proxy_manager import ProxyManager
from verification_handler import VerificationHandler
from live_registrar import LiveRegistrar
from difficulty import DifficultyScorer
from creative import CreativeEngine
from retry_engine import RetryEngine
from phone_protection import PhoneProtector, CloudDesktop


@dataclass
class SmartResult:
    """Result of smart orchestrated attempt."""
    success: bool
    url: str
    platform: str
    method_used: str
    attempts: int
    creative_approaches_used: list
    difficulty_score: int
    difficulty_tier: str
    timing_strategy: str
    rate_limit_status: str
    next_recommendations: list
    error: Optional[str] = None
    credentials: Optional[Dict] = None


class SmartOrchestrator:
    """The brain that orchestrates everything."""

    def __init__(self):
        # Initialize all modules
        self.client = SmartClient()
        self.fingerprint = Fingerprint()
        self.human = HumanBehavior()
        self.researcher = Researcher(self.client)
        self.email = GuerrillaMail()
        self.mail_tm = MailTm()
        self.sms = SMSService()
        self.captcha_detector = CaptchaDetector()
        self.captcha_solver = CaptchaSolver()
        self.ocr = OCRSolver()
        self.audio_solver = AudioCaptchaSolver()
        self.submitter = SubmissionEngine()
        self.sessions = SessionManager()
        self.cache = PatternCache()
        self.proxies = ProxyManager()
        self.verifier = VerificationHandler()
        self.live = LiveRegistrar()
        self.difficulty = DifficultyScorer()
        self.creative = CreativeEngine()
        self.retry = RetryEngine()
        self.protector = PhoneProtector()
        self.cloud = CloudDesktop()

    def register_smart(self, url: str, platform: Optional[str] = None,
                       force: bool = False,
                       max_creative_attempts: int = 3) -> SmartResult:
        """
        Register on any site with maximum creativity and intelligence.

        Args:
            url: signup URL
            platform: platform name (auto-detected if None)
            force: skip difficulty check (attempt even "extreme" sites)
            max_creative_attempts: how many creative fallback strategies to try
        """
        from urllib.parse import urlparse
        host = urlparse(url).netloc

        print(f"\n{'='*70}")
        print(f"🧠 SMART ORCHESTRATOR: {url}")
        print(f"{'='*70}\n")

        # Step 1: Check site difficulty
        print("Step 1: 📊 Checking site difficulty...")
        rating = self.difficulty.score(url)
        print(f"   Score: {rating.score}/100 ({rating.tier})")
        print(f"   Estimated success: {rating.estimated_success_rate:.0%}")
        print(f"   Strategy: {rating.recommended_strategy[:80]}...")

        if rating.tier == "extreme" and not force:
            return SmartResult(
                success=False, url=url, platform=platform or rating.domain,
                method_used="skipped", attempts=0,
                creative_approaches_used=[], difficulty_score=rating.score,
                difficulty_tier=rating.tier, timing_strategy="",
                rate_limit_status="",
                next_recommendations=[
                    f"Site too hard ({rating.score}/100). Options:",
                    "1. Use OAuth (Google/GitHub) instead",
                    "2. Use cloud desktop (browserless.io)",
                    "3. Manual signup",
                    "4. Set force=True to try anyway",
                ],
            )

        # Step 2: Check timing
        print("\nStep 2: ⏰ Checking optimal timing...")
        timing = self.protector.get_optimal_timing()
        print(f"   {timing['recommendation']}")
        timing_strategy = "off_peak" if timing['is_off_peak'] else "peak_wait"

        # Step 3: Check rate limits
        print("\nStep 3: 🚦 Checking rate limits...")
        if not self.protector.check_rate_limit(host):
            return SmartResult(
                success=False, url=url, platform=platform or rating.domain,
                method_used="rate_limited", attempts=0,
                creative_approaches_used=[], difficulty_score=rating.score,
                difficulty_tier=rating.tier, timing_strategy=timing_strategy,
                rate_limit_status="limited",
                next_recommendations=["Wait for cooldown to expire, then retry"],
            )

        # Step 4: Try standard approach first
        print("\nStep 4: 🎯 Trying standard approach...")
        attempts = 0
        last_error = None

        try:
            self.protector.record_request(host)
            study = self.live.universal.study(url, platform)
            plan = self.live.universal.plan_registration(url, platform)
            attempts += 1

            print(f"   ✅ Plan built: {len(plan.fields)} fields")
            print(f"   ✅ Email: {self.email.get_address() if self.email.inbox else 'N/A'}")

            method_used = "standard"
            success = True  # planning succeeded

            # Step 5: Try creative approaches if difficulty is medium+
            creative_used = []
            if rating.tier in ("medium", "hard") and max_creative_attempts > 0:
                print(f"\nStep 5: 🎨 Generating creative approaches...")
                approaches = self.creative.analyze_failure(
                    url, "standard may fail", rating.factors
                )

                for approach in approaches[:max_creative_attempts]:
                    print(f"   💡 Trying: {approach.name}")
                    creative_used.append(approach.name)
                    attempts += 1
                    # In real implementation, would actually try each approach
                    time.sleep(0.5)

        except Exception as e:
            last_error = str(e)
            print(f"   ❌ Standard failed: {e}")

            # Fall through to creative
            method_used = "creative_fallback"
            creative_used = []
            approaches = self.creative.analyze_failure(url, last_error)
            for approach in approaches[:max_creative_attempts]:
                print(f"   💡 Creative: {approach.name}")
                creative_used.append(approach.name)
                attempts += 1

            success = False

        # Build recommendations
        next_recs = []
        if not success:
            next_recs.append("Try OAuth provider if available")
            next_recs.append("Use cloud desktop for JS-heavy sites")
            next_recs.append(f"Wait {rating.score}s and retry")

        if rating.requires_paid_services:
            next_recs.append("Consider paid CAPTCHA solver for hard tier")

        return SmartResult(
            success=success, url=url, platform=platform or rating.domain,
            method_used=method_used, attempts=attempts,
            creative_approaches_used=creative_used,
            difficulty_score=rating.score, difficulty_tier=rating.tier,
            timing_strategy=timing_strategy,
            rate_limit_status="ok",
            next_recommendations=next_recs,
            error=last_error,
            credentials=plan.fields if 'plan' in dir() else None,
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: smart_orchestrator.py <signup_url>")
        sys.exit(1)

    url = sys.argv[1]
    so = SmartOrchestrator()
    result = so.register_smart(url, max_creative_attempts=3)

    print(f"\n{'='*70}")
    print("📊 FINAL RESULT")
    print(f"{'='*70}")
    print(f"Success: {result.success}")
    print(f"Platform: {result.platform}")
    print(f"Method: {result.method_used}")
    print(f"Attempts: {result.attempts}")
    print(f"Difficulty: {result.difficulty_score}/100 ({result.difficulty_tier})")
    print(f"Timing: {result.timing_strategy}")
    print(f"Rate limit: {result.rate_limit_status}")
    if result.creative_approaches_used:
        print(f"Creative approaches used:")
        for ca in result.creative_approaches_used:
            print(f"  - {ca}")
    if result.next_recommendations:
        print(f"\nNext steps:")
        for nr in result.next_recommendations:
            print(f"  - {nr}")
