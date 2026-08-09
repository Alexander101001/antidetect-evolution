"""
🎯 AFFILIATE SIGNUP AUTOMATOR
Registers on affiliate programs with high commissions.
"""
import asyncio
import json
import time
import random
from pathlib import Path

# High-commission affiliate programs (free to join)
AFFILIATE_PROGRAMS = [
    # Web hosting (highest commissions)
    {"name": "Bluehost", "url": "https://www.bluehost.com/affiliates", "commission": "$65-130/sale", "category": "hosting"},
    {"name": "Hostinger", "url": "https://www.hostinger.com/affiliates", "commission": "60% recurring", "category": "hosting"},
    {"name": "SiteGround", "url": "https://www.siteground.com/affiliates", "commission": "$50-100/sale", "category": "hosting"},
    {"name": "A2 Hosting", "url": "https://www.a2hosting.com/affiliates", "commission": "$55-125/sale", "category": "hosting"},
    {"name": "Cloudways", "url": "https://www.cloudways.com/affiliates", "commission": "$30-200/sale", "category": "hosting"},
    {"name": "WPEngine", "url": "https://wpengine.com/affiliates", "commission": "$200+/sale", "category": "hosting"},
    
    # VPN services
    {"name": "NordVPN", "url": "https://nordvpn.com/affiliates", "commission": "40-100% recurring", "category": "vpn"},
    {"name": "ExpressVPN", "url": "https://www.expressvpn.com/affiliates", "commission": "$13-36/sale", "category": "vpn"},
    {"name": "Surfshark", "url": "https://surfshark.com/affiliates", "commission": "40% recurring", "category": "vpn"},
    
    # Software
    {"name": "ClickBank", "url": "https://www.clickbank.com/", "commission": "varies (up to 75%)", "category": "digital"},
    {"name": "ShareASale", "url": "https://account.shareasale.com/", "commission": "varies", "category": "digital"},
    {"name": "CJ Affiliate", "url": "https://www.cj.com/", "commission": "varies", "category": "digital"},
    
    # Email marketing
    {"name": "ConvertKit", "url": "https://convertkit.com/affiliates", "commission": "30% recurring", "category": "saas"},
    {"name": "GetResponse", "url": "https://www.getresponse.com/affiliates", "commission": "33% recurring", "category": "saas"},
    {"name": "Mailchimp", "url": "https://mailchimp.com/affiliates", "commission": "varies", "category": "saas"},
    
    # AI tools
    {"name": "Jasper AI", "url": "https://jasper.ai/affiliates", "commission": "30% recurring", "category": "ai"},
    {"name": "Copy.ai", "url": "https://copy.ai/affiliates", "commission": "varies", "category": "ai"},
    {"name": "Midjourney", "url": "https://midjourney.com/", "commission": "varies", "category": "ai"},
    
    # E-commerce
    {"name": "Amazon Associates", "url": "https://affiliate-program.amazon.com/", "commission": "1-10%", "category": "ecom"},
    {"name": "eBay Partner", "url": "https://partnernetwork.ebay.com/", "commission": "1-4%", "category": "ecom"},
    
    # Education
    {"name": "Udemy", "url": "https://www.udemy.com/affiliates/", "commission": "varies", "category": "education"},
    {"name": "Coursera", "url": "https://www.coursera.org/", "commission": "varies", "category": "education"},
    
    # Crypto
    {"name": "Coinbase", "url": "https://coinbase.com/affiliates", "commission": "$10-50/signup", "category": "crypto"},
    {"name": "Binance", "url": "https://www.binance.com/", "commission": "varies", "category": "crypto"},
]


def generate_revenue_calculator():
    """Show revenue potential."""
    print("\n💰 REVENUE PROJECTIONS")
    print("=" * 60)
    
    # Conservative estimates
    visitors_per_day = 5000  # start small, grow
    rpm_low = 1.00  # $1 per 1000 visitors
    rpm_high = 5.00  # with affiliates + ads
    
    print(f"\nWith {visitors_per_day} visitors/day:")
    print(f"   Conservative (ads only):    ${visitors_per_day * rpm_low / 1000 * 30:.0f}/month")
    print(f"   Moderate (ads + affiliates): ${visitors_per_day * rpm_high / 1000 * 30:.0f}/month")
    
    visitors_per_day = 50000  # with growth
    print(f"\nWith {visitors_per_day} visitors/day:")
    print(f"   Conservative: ${visitors_per_day * rpm_low / 1000 * 30:.0f}/month")
    print(f"   Aggressive:   ${visitors_per_day * rpm_high / 1000 * 30:.0f}/month")
    
    visitors_per_day = 500000  # viral
    print(f"\nWith {visitors_per_day} visitors/day (viral):")
    print(f"   Conservative: ${visitors_per_day * rpm_low / 1000 * 30:.0f}/month")
    print(f"   Aggressive:   ${visitors_per_day * rpm_high / 1000 * 30:.0f}/month = ${visitors_per_day * rpm_high / 1000:.0f}/day")


if __name__ == "__main__":
    print(f"🎯 {len(AFFILIATE_PROGRAMS)} affiliate programs to register on")
    print()
    
    # Generate revenue calculator
    generate_revenue_calculator()
    
    # Save programs to JSON
    with open("affiliate_programs.json", "w") as f:
        json.dump(AFFILIATE_PROGRAMS, f, indent=2)
    print(f"\n💾 Saved to affiliate_programs.json")
