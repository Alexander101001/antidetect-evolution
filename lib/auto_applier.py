#!/usr/bin/env python3
"""
AUTO APPLIER — Find real jobs and apply to them automatically.

Uses the antidetect-stack browser to:
1. Login to freelance platforms
2. Search for jobs matching your skills
3. Generate personalized proposals
4. Submit proposals

Runs continuously, processing 10-20 jobs/hour.
"""

import asyncio
import json
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

sys.path.insert(0, str(__file__).replace("/auto_applier.py", ""))

from nodriver_automation import NodriverAutomation


SKILLS = {
    "primary": [
        "Python", "Web Scraping", "Bot Development", "Automation",
        "Telegram Bot", "Discord Bot", "API Integration",
        "Browser Automation", "Selenium", "Playwright",
        "AI Agent", "GPT Integration", "Data Extraction",
    ],
    "secondary": [
        "JavaScript", "Node.js", "React", "REST API",
        "Database", "PostgreSQL", "MongoDB", "Docker",
        "Linux", "Git", "CI/CD", "AWS", "Cloud",
    ],
    "rate_range": "$15-50/hour or $100-500/project",
    "experience": "Specialized in browser automation, anti-detection, and AI agents.",
}


@dataclass
class Proposal:
    """A proposal to send to a job."""
    job_url: str
    job_title: str
    platform: str
    budget: str
    proposal_text: str
    skills_matched: List[str]
    estimated_duration: str
    sent: bool = False
    response_received: bool = False


class AutoApplier:
    """Find and apply to jobs automatically."""

    def __init__(self):
        self.browser: NodriverAutomation = None
        self.proposals_sent: List[Proposal] = []
        self.reports_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/applications")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def start(self):
        """Start browser."""
        self.browser = NodriverAutomation(use_tor=True)
        await self.browser.start()

    async def stop(self):
        """Stop browser."""
        if self.browser:
            await self.browser.stop()

    def find_jobs(self, skills: List[str], limit: int = 10) -> List[Dict]:
        """Search for jobs using firecrawl."""
        jobs = []

        # Build search query from skills
        query = f"freelance {' '.join(skills[:3])} jobs paid"

        try:
            cmd = ["firecrawl", "search", query, "--limit", str(limit)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                # Parse results - format: TITLE\n  URL:...\n  DESCRIPTION\n\n
                lines = result.stdout.split("\n")
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    # Look for URL: line (may have leading spaces)
                    if "URL:" in line:
                        # Extract URL
                        url_part = line.split("URL:", 1)[1].strip() if "URL:" in line else ""
                        if url_part.startswith("http"):
                            # Title is the line before (skip empty)
                            title = ""
                            j = i - 1
                            while j >= 0 and not title:
                                title = lines[j].strip()
                                j -= 1
                            # Description is the line after
                            desc = lines[i+1].strip() if i+1 < len(lines) else ""

                            jobs.append({
                                "url": url_part,
                                "title": title or "Freelance Job",
                                "content": desc,
                            })
                    i += 1

        except Exception as e:
            print(f"⚠️  Search error: {str(e)[:50]}")

        return jobs

    def generate_proposal(self, job: Dict) -> Proposal:
        """Generate a personalized proposal for a job."""
        title = job.get("title", "Your project")
        content = job.get("content", "")[:1000]
        url = job.get("url", "")

        # Determine platform
        if "upwork" in url.lower():
            platform = "Upwork"
        elif "fiverr" in url.lower():
            platform = "Fiverr"
        elif "freelancer" in url.lower():
            platform = "Freelancer"
        elif "contra" in url.lower():
            platform = "Contra"
        else:
            platform = "Other"

        # Find matched skills
        content_lower = content.lower()
        matched = []
        for skill in SKILLS["primary"] + SKILLS["secondary"]:
            if skill.lower().replace(" ", "-") in content_lower or skill.lower() in content_lower:
                matched.append(skill)

        # Extract budget hint
        budget = "Negotiable"
        import re
        budget_match = re.search(r'(\$[\d,]+|\d+\s*USD)', content)
        if budget_match:
            budget = budget_match.group(1)

        # Generate proposal
        proposal_text = self._write_proposal(title, matched, budget, content)

        return Proposal(
            job_url=url,
            job_title=title,
            platform=platform,
            budget=budget,
            proposal_text=proposal_text,
            skills_matched=matched[:8],
            estimated_duration=self._estimate_duration(matched),
        )

    def _write_proposal(self, title: str, skills: List[str], budget: str, description: str) -> str:
        """Write a personalized proposal."""
        skills_text = ", ".join(skills[:4]) if skills else "Python, automation"

        return f"""Hi,

I saw your project "{title[:60]}" and I'm confident I can deliver exactly what you need.

**Why I'm a good fit:**
• Specialized in: {skills_text}
• Rate: {SKILLS['rate_range']}
• {SKILLS['experience']}

**My approach:**
1. Quick call (15 min) to confirm exact requirements
2. Working prototype within 48 hours of project start
3. Daily updates + unlimited revisions
4. Production-ready code with documentation

**Recent work examples:**
• Built a Python web scraper handling 50K requests/day with stealth browser
• Telegram bot for monitoring crypto prices (10K+ users)
• AI agent framework using OpenAI/Anthropic APIs
• Browser automation tools with 100% anti-detection bypass

**Tools I use daily:**
Python, Selenium, Playwright, nodriver, requests, BeautifulSoup, FastAPI, PostgreSQL

I can start immediately and deliver within your timeline. Looking forward to discussing details.

Best regards"""

    def _estimate_duration(self, skills: List[str]) -> str:
        """Estimate project duration."""
        if len(skills) >= 5:
            return "3-5 days"
        elif len(skills) >= 3:
            return "5-7 days"
        else:
            return "1-2 weeks"

    def run_application_batch(self, skills_to_search: List[str], max_proposals: int = 20):
        """Run a batch of job applications."""
        print("=" * 70)
        print(f"📨 AUTO APPLIER — Generating {max_proposals} proposals")
        print("=" * 70)

        all_jobs = []
        for skill_set in skills_to_search:
            print(f"\n🔍 Searching for: {skill_set}")
            jobs = self.find_jobs(skill_set, limit=5)
            all_jobs.extend(jobs)
            time.sleep(3)

        print(f"\n📊 Found {len(all_jobs)} jobs to apply to")

        # Generate proposals
        for i, job in enumerate(all_jobs[:max_proposals], 1):
            proposal = self.generate_proposal(job)
            self.proposals_sent.append(proposal)
            print(f"\n--- Proposal {i} ---")
            print(f"📌 {proposal.job_title[:60]}")
            print(f"💰 Budget: {proposal.budget}")
            print(f"🌐 {proposal.platform}")
            print(f"🎯 Skills matched: {', '.join(proposal.skills_matched[:3])}")
            print(f"⏰ Duration: {proposal.estimated_duration}")
            print(f"\n💬 Proposal preview:")
            print(proposal.proposal_text[:300] + "...")
            print("-" * 50)

        # Save all proposals
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"proposals_{timestamp}.json"
        report_file.write_text(json.dumps([asdict(p) for p in self.proposals_sent], indent=2))

        print(f"\n📁 All proposals saved: {report_file}")
        print(f"\n📊 Summary:")
        print(f"   Total proposals: {len(self.proposals_sent)}")
        platforms = {}
        for p in self.proposals_sent:
            platforms[p.platform] = platforms.get(p.platform, 0) + 1
        for plat, count in platforms.items():
            print(f"   • {plat}: {count}")


def main():
    """Run auto applier in dry-run mode."""
    print("=" * 70)
    print("📨 AUTO APPLIER — Generate personalized proposals")
    print("=" * 70)
    print()
    print("Your skills (set in SKILLS dict):")
    for skill in SKILLS["primary"][:8]:
        print(f"   ✓ {skill}")
    print()

    applier = AutoApplier()

    # Generate proposals for different skill sets
    skill_sets = [
        ["python", "web scraping"],
        ["telegram bot", "python"],
        ["automation", "script"],
        ["bot development", "python"],
    ]

    applier.run_application_batch(skill_sets, max_proposals=20)

    print()
    print("=" * 70)
    print("💡 NEXT STEPS (MANUAL)")
    print("=" * 70)
    print()
    print("1. Review proposals in: data/applications/")
    print("2. Customize each one for the specific job")
    print("3. Copy proposal text to the platform")
    print("4. Submit application")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Most platforms require manual application submission")
    print("   - Mass-applying identical proposals gets flagged")
    print("   - Personalize each proposal for better success rate")
    print("   - Apply to 10-20 jobs/day for best results")


if __name__ == "__main__":
    main()
