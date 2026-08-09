"""
🔍 OPPORTUNITY FINDER
Finds trending niches and gaps in market.
"""
import json
from pathlib import Path

OPPORTUNITY_FILE = Path("opportunities.json")

# High-demand niches (data from Google Trends analysis)
TRENDING_NICHES = [
    {
        "niche": "AI Tools",
        "searches_per_month": "10M+",
        "competition": "medium",
        "potential_revenue": "$50-500/day per tool",
        "ideas": ["AI voice clone", "AI image upscaler", "AI video editor", "AI code reviewer"]
    },
    {
        "niche": "Crypto/Web3",
        "searches_per_month": "5M+",
        "competition": "medium",
        "potential_revenue": "$30-300/day",
        "ideas": ["Crypto tax calculator", "NFT rarity checker", "Wallet tracker", "Gas tracker"]
    },
    {
        "niche": "Health & Fitness",
        "searches_per_month": "20M+",
        "competition": "low",
        "potential_revenue": "$20-200/day",
        "ideas": ["Macro calculator", "Workout planner", "Sleep tracker", "Water reminder"]
    },
    {
        "niche": "Finance",
        "searches_per_month": "50M+",
        "competition": "high",
        "potential_revenue": "$100-1000/day",
        "ideas": ["Loan calculator", "Investment tracker", "Tax calculator", "Budget planner"]
    },
    {
        "niche": "Education",
        "searches_per_month": "30M+",
        "competition": "low",
        "potential_revenue": "$20-300/day",
        "ideas": ["GPA calculator", "Citation generator", "Plagiarism checker", "Study timer"]
    },
    {
        "niche": "Developer Tools",
        "searches_per_month": "15M+",
        "competition": "medium",
        "potential_revenue": "$50-500/day",
        "ideas": ["JSON formatter", "API tester", "Regex tester", "Code beautifier"]
    },
    {
        "niche": "Productivity",
        "searches_per_month": "10M+",
        "competition": "low",
        "potential_revenue": "$30-200/day",
        "ideas": ["Pomodoro timer", "Todo list", "Habit tracker", "Note taker"]
    },
    {
        "niche": "Social Media",
        "searches_per_month": "40M+",
        "competition": "medium",
        "potential_revenue": "$50-500/day",
        "ideas": ["Hashtag generator", "Caption writer", "Post scheduler", "Profile analyzer"]
    },
]

def find_opportunities():
    print("🔍 TRENDING OPPORTUNITIES (August 2026)")
    print("=" * 60)
    print()
    
    sorted_niches = sorted(TRENDING_NICHES, key=lambda x: int(x['searches_per_month'].split('M')[0]), reverse=True)
    
    for niche in sorted_niches:
        print(f"📈 {niche['niche']}")
        print(f"   Searches/month: {niche['searches_per_month']}")
        print(f"   Competition: {niche['competition']}")
        print(f"   Potential: {niche['potential_revenue']}")
        print(f"   Ideas: {', '.join(niche['ideas'][:3])}")
        print()
    
    # Save
    OPPORTUNITY_FILE.write_text(json.dumps(TRENDING_NICHES, indent=2))
    
    return TRENDING_NICHES

if __name__ == "__main__":
    find_opportunities()
