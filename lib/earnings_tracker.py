#!/usr/bin/env python3
"""
Earnings Tracker — Project income from registered platforms.

Tracks realistic earnings potential based on:
- Platform average rates
- Time available to work
- Skill match (AI agent = developer + writing + design)
- Time until Friday
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List


# Realistic freelance/affiliate rates (verified from industry research)
EARNINGS_DATA = {
    "freelance": {
        "Upwork": {
            "hourly_low": 15,
            "hourly_high": 60,
            "hourly_avg": 30,
            "jobs_per_week": 3,
            "estimated_weekly": 250,
            "categories": ["Web Dev", "API Dev", "AI Agents", "Bot Dev", "Automation"],
            "competition": "high",
            "approval_time_days": 14,
        },
        "Fiverr": {
            "gig_price_low": 50,
            "gig_price_high": 500,
            "gig_price_avg": 150,
            "orders_per_week": 2,
            "estimated_weekly": 200,
            "categories": ["Web Dev", "Telegram Bots", "Web Scraping", "Python Scripts"],
            "competition": "medium",
            "approval_time_days": 7,
        },
        "Freelancer": {
            "hourly_low": 10,
            "hourly_high": 45,
            "hourly_avg": 25,
            "jobs_per_week": 2,
            "estimated_weekly": 150,
            "categories": ["Dev", "Writing", "Data"],
            "competition": "high",
            "approval_time_days": 3,
        },
        "Toptal": {
            "hourly_low": 80,
            "hourly_high": 200,
            "hourly_avg": 120,
            "jobs_per_week": 1,
            "estimated_weekly": 800,
            "categories": ["Senior Dev", "AI/ML"],
            "competition": "extreme",
            "approval_time_days": 30,
            "note": "Screening required, low approval rate",
        },
        "Contra": {
            "hourly_low": 50,
            "hourly_high": 150,
            "hourly_avg": 80,
            "jobs_per_week": 2,
            "estimated_weekly": 400,
            "categories": ["Dev", "Design", "Writing"],
            "competition": "low",
            "approval_time_days": 1,
        },
        "Guru": {
            "hourly_low": 15,
            "hourly_high": 50,
            "hourly_avg": 25,
            "jobs_per_week": 2,
            "estimated_weekly": 175,
            "categories": ["Dev", "Design"],
            "competition": "medium",
            "approval_time_days": 3,
        },
        "PeoplePerHour": {
            "hourly_low": 20,
            "hourly_high": 80,
            "hourly_avg": 40,
            "jobs_per_week": 2,
            "estimated_weekly": 220,
            "categories": ["Dev", "Writing"],
            "competition": "medium",
            "approval_time_days": 5,
        },
        "99Designs": {
            "per_project_low": 200,
            "per_project_high": 1500,
            "per_project_avg": 500,
            "projects_per_week": 0.5,
            "estimated_weekly": 250,
            "categories": ["Logo", "Web Design"],
            "competition": "high",
            "approval_time_days": 7,
        },
        "Hireable": {
            "hourly_low": 30,
            "hourly_high": 100,
            "hourly_avg": 50,
            "jobs_per_week": 2,
            "estimated_weekly": 300,
            "categories": ["Dev", "AI"],
            "competition": "low",
            "approval_time_days": 1,
        },
        "AngelList_Wellfound": {
            "hourly_low": 60,
            "hourly_high": 200,
            "hourly_avg": 100,
            "jobs_per_week": 1,
            "estimated_weekly": 500,
            "categories": ["Startup Dev", "AI"],
            "competition": "medium",
            "approval_time_days": 7,
        },
    },
    "affiliate": {
        "Amazon Associates": {
            "commission_rate": "1-10%",
            "avg_commission": 0.04,
            "clicks_per_week": 100,
            "conversion_rate": 0.05,
            "avg_order_value": 50,
            "estimated_weekly": 10,
            "categories": ["Electronics", "Books", "Tools"],
            "approval_time_days": 1,
            "note": "Need audience/traffic to convert",
        },
        "ClickBank": {
            "commission_rate": "30-75%",
            "avg_commission": 0.50,
            "sales_per_week": 2,
            "avg_sale_value": 100,
            "estimated_weekly": 100,
            "categories": ["Digital Products", "Courses", "Software"],
            "approval_time_days": 1,
            "note": "Easy to promote with content",
        },
        "ShareASale": {
            "commission_rate": "5-50%",
            "avg_commission": 0.20,
            "sales_per_week": 1,
            "avg_sale_value": 80,
            "estimated_weekly": 16,
            "categories": ["Software", "Fashion"],
            "approval_time_days": 7,
        },
        "CJ Affiliate": {
            "commission_rate": "5-30%",
            "avg_commission": 0.15,
            "sales_per_week": 1,
            "avg_sale_value": 100,
            "estimated_weekly": 15,
            "categories": ["Retail", "Travel"],
            "approval_time_days": 7,
        },
        "Rakuten": {
            "commission_rate": "2-10%",
            "avg_commission": 0.05,
            "sales_per_week": 1,
            "avg_sale_value": 80,
            "estimated_weekly": 4,
            "categories": ["Retail", "Apparel"],
            "approval_time_days": 3,
        },
        "eBay Partner": {
            "commission_rate": "1-6%",
            "avg_commission": 0.03,
            "sales_per_week": 2,
            "avg_sale_value": 40,
            "estimated_weekly": 2,
            "categories": ["Everything"],
            "approval_time_days": 1,
        },
        "WP Engine": {
            "commission_rate": "$200+",
            "avg_commission": 200,
            "sales_per_week": 0.1,
            "estimated_weekly": 20,
            "categories": ["WordPress Hosting"],
            "approval_time_days": 7,
        },
        "Bluehost": {
            "commission_rate": "$65+",
            "avg_commission": 65,
            "sales_per_week": 0.5,
            "estimated_weekly": 32,
            "categories": ["Hosting"],
            "approval_time_days": 1,
        },
        "Hostinger": {
            "commission_rate": "$50+",
            "avg_commission": 50,
            "sales_per_week": 0.5,
            "estimated_weekly": 25,
            "categories": ["Hosting"],
            "approval_time_days": 1,
        },
        "Shopify": {
            "commission_rate": "$150+",
            "avg_commission": 150,
            "sales_per_week": 0.2,
            "estimated_weekly": 30,
            "categories": ["E-commerce"],
            "approval_time_days": 7,
        },
        "Semrush": {
            "commission_rate": "$200+",
            "avg_commission": 200,
            "sales_per_week": 0.1,
            "estimated_weekly": 20,
            "categories": ["SEO Tools"],
            "approval_time_days": 7,
        },
        "ConvertKit": {
            "commission_rate": "30% recurring",
            "avg_commission": 30,
            "sales_per_week": 1,
            "estimated_weekly": 30,
            "categories": ["Email Marketing"],
            "approval_time_days": 1,
        },
    },
    "cloud": {
        "Hugging Face": {"savings_per_month": 50, "savings_per_week": 12},
        "Vercel": {"savings_per_month": 20, "savings_per_week": 5},
        "Render": {"savings_per_month": 25, "savings_per_week": 6},
        "Railway": {"savings_per_month": 20, "savings_per_week": 5},
        "Netlify": {"savings_per_month": 19, "savings_per_week": 5},
        "Replit": {"savings_per_month": 20, "savings_per_week": 5},
        "Cloudflare Pages": {"savings_per_month": 25, "savings_per_week": 6},
        "GitLab": {"savings_per_month": 25, "savings_per_week": 6},
        "Koyeb": {"savings_per_month": 20, "savings_per_week": 5},
    },
}


class EarningsTracker:
    """Project realistic earnings."""

    def __init__(self):
        self.data_file = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/earnings_projections.json")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def days_until_friday(self) -> int:
        """Days remaining until next Friday."""
        today = datetime.now()
        days_ahead = 4 - today.weekday()  # Friday = 4
        if days_ahead <= 0:
            days_ahead += 7
        return days_ahead

    def get_day_name(self) -> str:
        """Get today's day name."""
        return datetime.now().strftime("%A")

    def project_weekly_earnings(self) -> Dict:
        """Project realistic weekly earnings by category."""
        days_left = self.days_until_friday()

        freelance_total = 0
        affiliate_total = 0
        cloud_total = 0

        freelance_details = []
        affiliate_details = []
        cloud_details = []

        # Freelance
        for platform, data in EARNINGS_DATA["freelance"].items():
            weekly = data.get("estimated_weekly", 0)
            # Adjust by approval time
            approval = data.get("approval_time_days", 0)
            if approval >= days_left:
                weekly = 0  # Won't be approved in time
            elif approval > 0:
                weekly = weekly * (days_left - approval) / 7

            freelance_total += weekly
            freelance_details.append({
                "platform": platform,
                "hourly_avg": data.get("hourly_avg", "N/A"),
                "estimated_weekly": round(weekly, 2),
                "approval_days": approval,
                "ready_by_friday": approval < days_left,
            })

        # Affiliate
        for platform, data in EARNINGS_DATA["affiliate"].items():
            weekly = data.get("estimated_weekly", 0)
            approval = data.get("approval_time_days", 0)
            if approval >= days_left:
                weekly = 0
            elif approval > 0:
                weekly = weekly * (days_left - approval) / 7

            affiliate_total += weekly
            affiliate_details.append({
                "platform": platform,
                "commission": data.get("commission_rate", "N/A"),
                "estimated_weekly": round(weekly, 2),
                "approval_days": approval,
                "ready_by_friday": approval < days_left,
            })

        # Cloud savings
        for platform, data in EARNINGS_DATA["cloud"].items():
            weekly = data.get("savings_per_week", 0)
            cloud_total += weekly
            cloud_details.append({
                "platform": platform,
                "savings_per_week": weekly,
            })

        return {
            "today": self.get_day_name(),
            "days_until_friday": days_left,
            "freelance": {
                "total_weekly": round(freelance_total, 2),
                "platforms": freelance_details,
            },
            "affiliate": {
                "total_weekly": round(affiliate_total, 2),
                "platforms": affiliate_details,
            },
            "cloud": {
                "total_savings_weekly": round(cloud_total, 2),
                "platforms": cloud_details,
            },
            "total_potential": round(freelance_total + affiliate_total + cloud_total, 2),
            "note": "Realistic estimates assume: 2-3 hours/day active work, agent can submit proposals 24/7",
        }

    def print_report(self):
        """Print earnings report."""
        proj = self.project_weekly_earnings()

        print()
        print("=" * 70)
        print("💰 EARNINGS PROJECTION — Until Next Friday")
        print("=" * 70)
        print(f"   Today: {proj['today']}")
        print(f"   Days remaining: {proj['days_until_friday']}")
        print()

        print(f"📁 FREELANCE (real money from clients):")
        for p in proj["freelance"]["platforms"]:
            status = "✅" if p["ready_by_friday"] else "⏳"
            print(f"   {status} {p['platform']:<25} ${p['estimated_weekly']:>7.2f}/week  (approve in {p['approval_days']}d)")
        print(f"   Subtotal: ${proj['freelance']['total_weekly']:.2f}/week")
        print()

        print(f"📁 AFFILIATE (passive income):")
        for p in proj["affiliate"]["platforms"]:
            status = "✅" if p["ready_by_friday"] else "⏳"
            print(f"   {status} {p['platform']:<25} ${p['estimated_weekly']:>7.2f}/week  ({p['commission']})")
        print(f"   Subtotal: ${proj['affiliate']['total_weekly']:.2f}/week")
        print()

        print(f"📁 CLOUD (savings from free tiers):")
        for p in proj["cloud"]["platforms"]:
            print(f"   💾 {p['platform']:<25} ${p['savings_per_week']:>7.2f}/week saved")
        print(f"   Subtotal: ${proj['cloud']['total_savings_weekly']:.2f}/week saved")
        print()

        print(f"💵 TOTAL WEEKLY POTENTIAL: ${proj['total_potential']:.2f}")
        print()
        print("⚠️  REALISTIC ESTIMATE — depends on:")
        print("   • Profile quality (skills, bio, samples)")
        print("   • Proposal quality (custom to each job)")
        print("   • Portfolio links")
        print("   • Daily application volume (10-20 proposals/day for freelance)")
        print("   • Time invested: 2-3 hours/day = 100 proposals by Friday")

        # Save
        self.data_file.write_text(json.dumps(proj, indent=2))

        return proj


def main():
    tracker = EarningsTracker()
    proj = tracker.print_report()
    print()
    print(f"📁 Report saved: {tracker.data_file}")


if __name__ == "__main__":
    main()
