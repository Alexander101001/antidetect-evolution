#!/usr/bin/env python3
"""
JOB SCANNER — Find real freelance jobs you can actually do.

Searches for jobs in categories you can deliver with this stack:
- Web scraping (Python + stealth)
- Bot development (Telegram, Discord)
- Automation scripts
- AI agent development
- API integration

Outputs jobs with:
- Title
- Budget
- Description
- Match score (how well you can do it)
- Draft proposal text
- Apply link
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict


@dataclass
class Job:
    """A real freelance job opportunity."""
    title: str
    budget: str
    platform: str
    url: str
    description: str
    skills_required: List[str]
    match_score: int  # 0-100
    draft_proposal: str
    difficulty: str  # easy/medium/hard
    delivery_time_days: int


class JobScanner:
    """Scan for real jobs that match our skills."""

    def __init__(self):
        self.skills = [
            "python", "web scraping", "automation", "bot",
            "telegram", "discord", "api", "selenium",
            "playwright", "anti-detection", "browser automation",
            "data extraction", "ai agent", "anti-bot bypass",
            "scraping", "crawler", "stealth", "nodriver",
        ]
        self.report_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/jobs")
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def search_jobs(self, query: str, limit: int = 10) -> List[Job]:
        """Search for jobs using firecrawl."""
        print(f"🔍 Searching: {query}")

        cmd = ["firecrawl", "search", query, "--limit", str(limit), "--scrape", "--scrape-formats", "markdown"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            print(f"⚠️  Search failed: {result.stderr[:100]}")
            return []

        # Parse results from output (each result has URL + content)
        return self._parse_results(result.stdout, query)

    def _parse_results(self, raw: str, query: str) -> List[Job]:
        """Parse firecrawl output into Job objects."""
        jobs = []

        # Split by URL markers
        lines = raw.split("\n")
        current_url = None
        current_title = None
        current_content = []

        for line in lines:
            if line.strip().startswith("URL:"):
                if current_url and current_content:
                    job = self._make_job(current_url, current_title, "\n".join(current_content), query)
                    if job:
                        jobs.append(job)
                current_url = line.replace("URL:", "").strip()
                current_content = []
            elif line.strip().startswith("Title:"):
                current_title = line.replace("Title:", "").strip()
            elif current_url:
                current_content.append(line)

        # Don't forget last one
        if current_url and current_content:
            job = self._make_job(current_url, current_title, "\n".join(current_content), query)
            if job:
                jobs.append(job)

        return jobs

    def _make_job(self, url: str, title: str, content: str, query: str) -> Job:
        """Create a Job from parsed data."""
        # Extract budget
        budget = "Unknown"
        import re
        budget_match = re.search(r'(\$[\d,]+(?:\s*USD)?|\d+\s*USD)', content, re.IGNORECASE)
        if budget_match:
            budget = budget_match.group(1)

        # Extract skills from content
        content_lower = content.lower()
        found_skills = []
        for skill in self.skills:
            if skill in content_lower:
                found_skills.append(skill)

        # Calculate match score
        match_score = 0
        for skill in found_skills:
            match_score += 15
        match_score = min(match_score, 100)

        # Determine difficulty
        if match_score >= 60:
            difficulty = "easy"
            delivery = 3
        elif match_score >= 40:
            difficulty = "medium"
            delivery = 7
        else:
            difficulty = "hard"
            delivery = 14

        # Generate draft proposal
        proposal = self._generate_proposal(title or "Project", found_skills, budget, content[:300])

        return Job(
            title=title or query,
            budget=budget,
            platform=self._get_platform(url),
            url=url,
            description=content[:500],
            skills_required=found_skills,
            match_score=match_score,
            draft_proposal=proposal,
            difficulty=difficulty,
            delivery_time_days=delivery,
        )

    def _get_platform(self, url: str) -> str:
        """Extract platform name from URL."""
        if "upwork" in url:
            return "Upwork"
        elif "fiverr" in url:
            return "Fiverr"
        elif "freelancer" in url:
            return "Freelancer"
        elif "contra" in url:
            return "Contra"
        elif "vollna" in url:
            return "Vollna"
        elif "reddit" in url:
            return "Reddit"
        elif "github" in url:
            return "GitHub"
        else:
            return "Other"

    def _generate_proposal(self, title: str, skills: List[str], budget: str, description: str) -> str:
        """Generate a draft proposal."""
        skills_text = ", ".join(skills[:5]) if skills else "Python, automation"

        return f"""Hi there,

I can help with this {title}. I have direct experience in:
{skills_text}

My approach:
1. Understand your exact requirements
2. Build a working prototype within 48 hours
3. Iterate based on your feedback
4. Deliver production-ready code with documentation

I've built similar projects before and can deliver within your budget of {budget}.

Recent work:
- Built scrapers handling 10K+ requests/day with anti-detection
- Telegram/Discord bots with multi-user support
- AI agent frameworks using LLM APIs
- Browser automation with 100% bypass rate

Available to start immediately. Would you like to schedule a quick call to discuss details?

Best regards"""


def main():
    """Run job scanner."""
    print("=" * 70)
    print("💼 JOB SCANNER — Find real freelance work you can do")
    print("=" * 70)
    print()

    scanner = JobScanner()

    # Search queries targeting YOUR skills (this stack's skills)
    queries = [
        "python web scraping freelancer job",
        "telegram bot developer job",
        "automation script freelance",
        "AI agent python developer",
    ]

    all_jobs = []
    for q in queries:
        jobs = scanner.search_jobs(q, limit=5)
        all_jobs.extend(jobs)
        time.sleep(2)

    # Sort by match score
    all_jobs.sort(key=lambda j: j.match_score, reverse=True)

    # Display top jobs
    print()
    print("=" * 70)
    print(f"📊 Found {len(all_jobs)} jobs (showing top 10)")
    print("=" * 70)

    for i, job in enumerate(all_jobs[:10], 1):
        print(f"\n--- Job {i} ---")
        print(f"📌 {job.title[:80]}")
        print(f"💰 Budget: {job.budget}")
        print(f"🌐 Platform: {job.platform}")
        print(f"⭐ Match: {job.match_score}% ({job.difficulty})")
        print(f"🔗 URL: {job.url[:80]}")
        print(f"📋 Skills needed: {', '.join(job.skills_required[:5])}")
        print(f"⏰ Estimated delivery: {job.delivery_time_days} days")
        print(f"\n💬 Draft proposal:")
        print(job.draft_proposal[:300] + "...")
        print("-" * 50)

    # Save report
    report_file = scanner.report_dir / f"jobs_{time.strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps([asdict(j) for j in all_jobs], indent=2))
    print(f"\n📁 Full report: {report_file}")

    # Print summary
    easy_jobs = [j for j in all_jobs if j.difficulty == "easy"]
    print(f"\n💡 RECOMMENDATION:")
    print(f"   - {len(easy_jobs)} EASY jobs (you can start immediately)")
    print(f"   - Focus on these first — match score >60%")
    print(f"   - Apply to 10-20/day for best results")


if __name__ == "__main__":
    main()
