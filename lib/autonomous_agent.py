#!/usr/bin/env python3
"""
Autonomous Digital Enterprise Agent — 24/7 self-executing.

Continuously:
1. Scouts new platforms and opportunities
2. Attempts registrations with creative strategies
3. Manages credentials securely
4. Logs everything to reports
5. Self-optimizes based on success/failure patterns

Run: python autonomous_agent.py [--duration 3600] [--max-attempts 100]
"""

import sys
import time
import json
import signal
import random
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict, field
from collections import defaultdict

sys.path.insert(0, str(__file__).replace("/autonomous_agent.py", ""))

from unified import SmartClient
from stealth import HumanBehavior, Fingerprint
from difficulty import DifficultyScorer
from creative import CreativeEngine
from retry_engine import RetryEngine
from phone_protection import PhoneProtector
from pattern_cache import PatternCache
from session_manager import SessionManager
from researcher import Researcher
from multi_cloud import CLOUD_PLATFORMS, CloudPlatform


@dataclass
class AgentReport:
    """Periodic execution report."""
    cycle: int
    started_at: str
    finished_at: str
    duration_seconds: float
    targets_scouted: int
    registration_attempts: int
    registration_successes: int
    creative_strategies_used: int
    accounts_created: List[str]
    failures: List[str]
    optimizations: List[str]
    next_actions: List[str]


class AutonomousAgent:
    """The 24/7 self-executing agent."""

    def __init__(self):
        self.client = SmartClient()
        self.fingerprint = Fingerprint()
        self.human = HumanBehavior()
        self.difficulty = DifficultyScorer()
        self.creative = CreativeEngine()
        self.retry = RetryEngine()
        self.protector = PhoneProtector()
        self.cache = PatternCache()
        self.sessions = SessionManager()
        self.researcher = Researcher(self.client)

        # State
        self.running = True
        self.cycle = 0
        self.success_count = 0
        self.failure_count = 0
        self.accounts = []
        self.optimizations = []

        # Reports
        self.reports_path = Path("~/.pi/skills/antidetect-stack/data/agent_reports").expanduser()
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.log_path = self.reports_path / "agent.log"

        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

    def _shutdown_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\n🛑 Shutdown signal received. Generating final report...")
        self.running = False

    def log(self, message: str):
        """Log to file and stdout."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        try:
            with open(self.log_path, "a") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def scout_targets(self) -> List[Dict]:
        """Discover new platforms to attempt registration on."""
        targets = []

        # Source 1: Known cloud platforms
        for p in CLOUD_PLATFORMS:
            if p.difficulty <= 30:  # Only attempt easy ones
                targets.append({
                    "name": p.name,
                    "url": p.signup_url,
                    "type": "cloud",
                    "difficulty": p.difficulty,
                    "oauth": p.oauth,
                })

        # Source 2: Discover via Google search
        try:
            search_queries = [
                "free cloud platform signup 2026",
                "developer tools free signup no credit card",
                "free hosting service signup",
                "free api service developer account",
            ]
            for query in search_queries:
                self.log(f"🔍 Searching: {query}")
                results = self.researcher.google_search(query, num=5)
                for url in results[:3]:
                    # Filter out known platforms
                    if not any(p.signup_url in url or p.name.lower() in url.lower() for p in CLOUD_PLATFORMS):
                        targets.append({
                            "name": url.split("//")[-1].split("/")[0],
                            "url": url,
                            "type": "discovered",
                            "difficulty": 50,  # Unknown
                            "oauth": [],
                        })
                time.sleep(2)  # Respect rate limits
        except Exception as e:
            self.log(f"⚠️  Search failed: {e}")

        # Deduplicate by domain
        seen = set()
        unique = []
        for t in targets:
            domain = t["url"].split("//")[-1].split("/")[0]
            if domain not in seen:
                seen.add(domain)
                unique.append(t)

        self.log(f"📋 Scouted {len(unique)} unique targets")
        return unique

    def attempt_registration(self, target: Dict) -> Dict:
        """Attempt registration on a target."""
        result = {
            "target": target["name"],
            "url": target["url"],
            "success": False,
            "strategy": None,
            "error": None,
            "timestamp": datetime.now().isoformat(),
        }

        # Check rate limit
        host = target["url"].split("//")[-1].split("/")[0]
        if not self.protector.check_rate_limit(host):
            result["error"] = "rate_limited"
            return result

        try:
            # Step 1: Score difficulty
            rating = self.difficulty.score(target["url"])
            result["difficulty"] = rating.score
            result["tier"] = rating.tier

            # Skip if too hard
            if rating.tier == "extreme":
                result["error"] = f"too_hard_{rating.score}"
                self.log(f"⏭️  Skipping {target['name']} (difficulty {rating.score})")
                return result

            # Step 2: Try standard approach
            self.log(f"🎯 Attempting {target['name']} (difficulty {rating.score})")
            self.protector.record_request(host)

            attempt_result = self.retry.fetch_with_retry(target["url"], max_attempts=3)
            result["strategy"] = attempt_result.successful_strategy

            if attempt_result.success:
                result["success"] = True
                self.success_count += 1
                self.accounts.append(target["name"])
                self.log(f"✅ Success on {target['name']} via {attempt_result.successful_strategy}")
            else:
                # Step 3: Try creative approaches
                if attempt_result.creative_approaches:
                    self.log(f"🎨 {target['name']} needs creative approach")
                    result["strategy"] = "creative_recommended"
                    result["creative_approaches"] = attempt_result.creative_approaches
                    self.optimizations.append(
                        f"For {target['name']}: try {attempt_result.creative_approaches[0]}"
                    )

                self.failure_count += 1

        except Exception as e:
            result["error"] = str(e)[:200]
            self.failure_count += 1
            self.log(f"❌ Error on {target['name']}: {str(e)[:80]}")

        return result

    def self_optimize(self):
        """Analyze results and optimize future attempts."""
        # Cache successful patterns
        if self.success_count > 0:
            self.optimizations.append(
                f"Found {self.success_count} successful patterns — caching for future use"
            )

        # Learn from failures
        if self.failure_count > self.success_count * 2:
            self.optimizations.append(
                "Failure rate high — recommend using more creative approaches"
            )

        # Save learned patterns
        self.cache.save(
            url="autonomous_run",
            pattern={
                "cycle": self.cycle,
                "success_rate": self.success_count / max(1, self.success_count + self.failure_count),
                "total_attempts": self.success_count + self.failure_count,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def generate_report(self, duration: float) -> AgentReport:
        """Generate execution report."""
        return AgentReport(
            cycle=self.cycle,
            started_at=(datetime.now() - timedelta(seconds=duration)).isoformat(),
            finished_at=datetime.now().isoformat(),
            duration_seconds=duration,
            targets_scouted=len(self.accounts) + self.failure_count,
            registration_attempts=self.success_count + self.failure_count,
            registration_successes=self.success_count,
            creative_strategies_used=len([o for o in self.optimizations if "creative" in o.lower()]),
            accounts_created=self.accounts.copy(),
            failures=[f"Attempt {i+1}" for i in range(self.failure_count)],
            optimizations=self.optimizations.copy(),
            next_actions=[
                "Continue running autonomous loop",
                "Add more discovered targets",
                "Try creative approaches on failed targets",
                "Cache successful patterns",
            ],
        )

    def save_report(self, report: AgentReport):
        """Save report to file."""
        filename = f"report_cycle_{report.cycle}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = self.reports_path / filename
        path.write_text(json.dumps(asdict(report), indent=2))
        self.log(f"📊 Report saved: {path}")
        return path

    def run_forever(self, max_cycles: Optional[int] = None,
                    cycle_duration: int = 300,  # 5 min per cycle
                    delay_between_attempts: float = 3.0):
        """
        Main autonomous loop.

        Args:
            max_cycles: Stop after this many cycles (None = forever)
            cycle_duration: How long each cycle runs (seconds)
            delay_between_attempts: Sleep between targets
        """
        self.log("🚀 AUTONOMOUS AGENT STARTED")
        self.log(f"   Max cycles: {max_cycles or 'forever'}")
        self.log(f"   Cycle duration: {cycle_duration}s")
        self.log("")

        start_time = time.time()

        while self.running:
            self.cycle += 1
            cycle_start = time.time()
            self.log(f"\n{'='*70}")
            self.log(f"🔄 CYCLE {self.cycle}")
            self.log(f"{'='*70}")

            # Phase 1: Scout
            self.log("\n📡 Phase 1: Scouting targets...")
            targets = self.scout_targets()

            # Phase 2: Attempt (up to cycle_duration)
            self.log(f"\n🎯 Phase 2: Attempting registrations ({len(targets)} targets)...")
            cycle_success = 0
            cycle_failure = 0
            for i, target in enumerate(targets):
                if not self.running:
                    break
                if time.time() - cycle_start > cycle_duration:
                    self.log(f"   ⏱️  Cycle time limit reached")
                    break

                self.log(f"\n[{i+1}/{len(targets)}] {target['name']}")
                result = self.attempt_registration(target)
                if result["success"]:
                    cycle_success += 1
                else:
                    cycle_failure += 1

                time.sleep(delay_between_attempts)

            # Phase 3: Self-optimize
            self.log(f"\n🧠 Phase 3: Self-optimization...")
            self.self_optimize()

            # Phase 4: Report
            cycle_duration_actual = time.time() - cycle_start
            self.log(f"\n📊 Cycle {self.cycle} complete in {cycle_duration_actual:.1f}s")
            self.log(f"   This cycle: {cycle_success} success, {cycle_failure} failure")
            self.log(f"   All time: {self.success_count} success, {self.failure_count} failure")

            report = self.generate_report(cycle_duration_actual)
            self.save_report(report)

            # Check if max cycles reached
            if max_cycles and self.cycle >= max_cycles:
                self.log(f"\n✅ Reached max cycles ({max_cycles}). Stopping.")
                break

            # Sleep before next cycle
            if self.running:
                self.log(f"\n💤 Sleeping 30s before next cycle...")
                time.sleep(30)

        # Final report
        total_duration = time.time() - start_time
        self.log(f"\n{'='*70}")
        self.log(f"🏁 AGENT STOPPED — Total runtime: {total_duration:.1f}s")
        self.log(f"{'='*70}")

        final_report = self.generate_report(total_duration)
        self.save_report(final_report)

        # Print summary
        self._print_summary(final_report)

    def _print_summary(self, report: AgentReport):
        """Print execution summary."""
        print(f"\n\n{'='*70}")
        print(f"📊 EXECUTION REPORT — CYCLE {report.cycle}")
        print(f"{'='*70}")
        print(f"Duration: {report.duration_seconds:.1f}s")
        print(f"Targets scouted: {report.targets_scouted}")
        print(f"Registrations attempted: {report.registration_attempts}")
        print(f"Registrations successful: {report.registration_successes}")
        print(f"Success rate: {(report.registration_successes / max(1, report.registration_attempts) * 100):.1f}%")
        print()
        if report.accounts_created:
            print(f"✅ Accounts created:")
            for acc in report.accounts_created:
                print(f"   - {acc}")
        if report.optimizations:
            print(f"\n🧠 Optimizations:")
            for opt in report.optimizations[:5]:
                print(f"   - {opt}")
        if report.next_actions:
            print(f"\n🎯 Next actions:")
            for act in report.next_actions:
                print(f"   - {act}")
        print(f"{'='*70}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Digital Enterprise Agent")
    parser.add_argument("--max-cycles", type=int, default=None, help="Max cycles (default: forever)")
    parser.add_argument("--cycle-duration", type=int, default=300, help="Seconds per cycle")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between attempts")
    parser.add_argument("--quick", action="store_true", help="Quick mode: 1 cycle, 60s duration")
    args = parser.parse_args()

    agent = AutonomousAgent()

    if args.quick:
        print("🚀 Quick mode: 1 cycle, 60 seconds")
        agent.run_forever(max_cycles=1, cycle_duration=60, delay_between_attempts=2.0)
    else:
        agent.run_forever(
            max_cycles=args.max_cycles,
            cycle_duration=args.cycle_duration,
            delay_between_attempts=args.delay,
        )


if __name__ == "__main__":
    main()
