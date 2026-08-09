#!/usr/bin/env python3
"""
MORE PLATFORMS — Additional platforms I haven't registered on yet.

Categories:
- Survey sites (paid opinions)
- Micro-task platforms (small $)
- Sell digital products (Gumroad)
- Print on demand (Redbubble, TeePublic)
- Stock photography (Shutterstock, Adobe Stock)
- Video platforms (YouTube monetization)
- Podcast platforms (Spotify, Anchor)
- Writing platforms (Medium, Substack)
- Music platforms (DistroKid)
- Course platforms (Udemy, Skillshare)
"""

# Full platform database
ALL_PLATFORMS = {
    # ════ MORE FREELANCE ════
    "freelance": [
        {"name": "Mochi", "url": "https://mochi.com/signup", "method": "email", "category": "design"},
        {"name": "SolidGigs", "url": "https://solidgigs.com/", "method": "email", "category": "curated_freelance"},
        {"name": "CloudPeeps", "url": "https://cloudpeeps.io/", "method": "email", "category": "vetted_freelance"},
        {"name": "Growers", "url": "https://growers.io/", "method": "email", "category": "tech_freelance"},
        {"name": "Codementor", "url": "https://www.codementor.io/login", "method": "oauth_github", "category": "tech_mentorship"},
        {"name": "Lemon.io", "url": "https://lemon.io/", "method": "email", "category": "dev_freelance"},
        {"name": "Turing", "url": "https://www.turing.com/signup", "method": "email", "category": "dev_freelance"},
        {"name": "Arc.dev", "url": "https://arc.dev/", "method": "email", "category": "vetted_freelance"},
        {"name": "Pesto", "url": "https://www.pesto.tech/", "method": "email", "category": "dev_freelance"},
        {"name": "A.Team", "url": "https://www.a.team/", "method": "email", "category": "vetted_freelance"},
        {"name": "Crewfire", "url": "https://crewfire.com/", "method": "email", "category": "influencer_marketing"},
    ],

    # ════ SELL DIGITAL PRODUCTS ════
    "digital_products": [
        {"name": "Gumroad", "url": "https://gumroad.com/signup", "method": "oauth_github", "category": "sell_digital"},
        {"name": "Lemonsqueezy", "url": "https://app.lemonsqueezy.com/register", "method": "email", "category": "sell_digital"},
        {"name": "Paddle", "url": "https://paddle.com/signup", "method": "email", "category": "sell_saas"},
        {"name": "FastSpring", "url": "https://fastspring.com/", "method": "email", "category": "sell_saas"},
        {"name": "Stripe Atlas", "url": "https://stripe.com/atlas", "method": "email", "category": "sell_saas"},
        {"name": "Payhip", "url": "https://payhip.com/", "method": "email", "category": "sell_digital"},
        {"name": "Podia", "url": "https://www.podia.com/signup", "method": "email", "category": "sell_courses"},
        {"name": "Teachable", "url": "https://teachable.com/", "method": "oauth_google", "category": "sell_courses"},
        {"name": "Thinkific", "url": "https://www.thinkific.com/signup", "method": "email", "category": "sell_courses"},
        {"name": "Kajabi", "url": "https://kajabi.com/signup", "method": "email", "category": "sell_courses"},
        {"name": "Etsy", "url": "https://www.etsy.com/join", "method": "oauth_google", "category": "sell_handmade"},
        {"name": "Creative Market", "url": "https://creativemarket.com/", "method": "email", "category": "sell_design"},
    ],

    # ════ PRINT ON DEMAND ════
    "print_on_demand": [
        {"name": "Redbubble", "url": "https://www.redbubble.com/auth/signup", "method": "oauth_google", "category": "print_art"},
        {"name": "TeePublic", "url": "https://www.teepublic.com/", "method": "oauth_google", "category": "print_apparel"},
        {"name": "Society6", "url": "https://society6.com/", "method": "oauth_google", "category": "print_art"},
        {"name": "Spreadshirt", "url": "https://www.spreadshirt.com/", "method": "oauth_google", "category": "print_apparel"},
        {"name": "Zazzle", "url": "https://www.zazzle.com/", "method": "oauth_google", "category": "print_custom"},
        {"name": "Printful", "url": "https://www.printful.com/", "method": "email", "category": "print_fulfillment"},
        {"name": "Printify", "url": "https://printify.com/", "method": "email", "category": "print_fulfillment"},
        {"name": "Spring (Teespring)", "url": "https://spring.io/", "method": "email", "category": "print_apparel"},
    ],

    # ════ STOCK PHOTO / VIDEO / MUSIC ════
    "stock_content": [
        {"name": "Shutterstock", "url": "https://www.shutterstock.com/contributor", "method": "email", "category": "stock_photo"},
        {"name": "Adobe Stock", "url": "https://stock.adobe.com/contributor", "method": "oauth_google", "category": "stock_photo"},
        {"name": "iStock/Getty", "url": "https://www.istockphoto.com/", "method": "email", "category": "stock_photo"},
        {"name": "Pond5", "url": "https://www.pond5.com/", "method": "email", "category": "stock_video"},
        {"name": "Foap", "url": "https://www.foap.com/", "method": "oauth_facebook", "category": "stock_photo"},
        {"name": "EyeEm", "url": "https://www.eyeem.com/", "method": "oauth_facebook", "category": "stock_photo"},
        {"name": "500px", "url": "https://500px.com/", "method": "email", "category": "stock_photo"},
        {"name": "Alamy", "url": "https://www.alamy.com/", "method": "email", "category": "stock_photo"},
        {"name": "Freepik Contributor", "url": "https://www.freepik.com/contributor", "method": "email", "category": "stock_vector"},
        {"name": "Vecteezy", "url": "https://www.vecteezy.com/", "method": "email", "category": "stock_vector"},
        {"name": "AudioJungle", "url": "https://audiojungle.net/", "method": "email", "category": "stock_audio"},
        {"name": "Pond5 Music", "url": "https://www.pond5.com/", "method": "email", "category": "stock_audio"},
    ],

    # ════ SURVEYS & MICRO-TASKS ════
    "micro_tasks": [
        {"name": "Amazon Mechanical Turk", "url": "https://www.mturk.com/", "method": "amazon", "category": "micro_task"},
        {"name": "Clickworker", "url": "https://www.clickworker.com/", "method": "email", "category": "micro_task"},
        {"name": "Appen", "url": "https://appen.com/", "method": "email", "category": "ai_training"},
        {"name": "Telus International (Lionbridge)", "url": "https://www.telusinternational.com/", "method": "email", "category": "ai_training"},
        {"name": "Remotasks", "url": "https://www.remotasks.com/", "method": "email", "category": "ai_training"},
        {"name": "Scale AI", "url": "https://scale.com/", "method": "email", "category": "ai_training"},
        {"name": "Defined.ai", "url": "https://www.defined.ai/", "method": "email", "category": "ai_training"},
        {"name": "Spare5 (Defined)", "url": "https://www.spare5.com/", "method": "email", "category": "micro_task"},
        {"name": "Picoworkers", "url": "https://picoworkers.com/", "method": "email", "category": "micro_task"},
        {"name": "Microworkers", "url": "https://microworkers.com/", "method": "email", "category": "micro_task"},
        {"name": "Swagbucks", "url": "https://www.swagbucks.com/", "method": "email", "category": "surveys"},
        {"name": "Survey Junkie", "url": "https://www.surveyjunkie.com/", "method": "email", "category": "surveys"},
        {"name": "Prolific", "url": "https://www.prolific.com/", "method": "email", "category": "surveys_academic"},
        {"name": "Respondent.io", "url": "https://respondent.io/", "method": "email", "category": "research_surveys"},
        {"name": "UserTesting", "url": "https://www.usertesting.com/", "method": "email", "category": "usability_test"},
        {"name": "Testbirds", "url": "https://www.testbirds.com/", "method": "email", "category": "usability_test"},
        {"name": "TryMyUI", "url": "https://www.trymyui.com/", "method": "email", "category": "usability_test"},
        {"name": "Userlytics", "url": "https://www.userlytics.com/", "method": "email", "category": "usability_test"},
    ],

    # ════ WRITING / BLOGGING ════
    "writing": [
        {"name": "Medium Partner Program", "url": "https://medium.com/m/signin", "method": "oauth_google", "category": "writing_paid"},
        {"name": "Substack", "url": "https://substack.com/signup", "method": "email", "category": "newsletter"},
        {"name": "Ghost", "url": "https://ghost.org/", "method": "email", "category": "newsletter"},
        {"name": "Hashnode", "url": "https://hashnode.com/onboard", "method": "oauth_github", "category": "dev_blog"},
        {"name": "Dev.to", "url": "https://dev.to/enter?signup=true", "method": "oauth_github", "category": "dev_blog"},
        {"name": "Blogger", "url": "https://www.blogger.com/", "method": "oauth_google", "category": "blog"},
        {"name": "WordPress.com", "url": "https://wordpress.com/start/", "method": "email", "category": "blog"},
        {"name": "Wix", "url": "https://www.wix.com/", "method": "email", "category": "blog"},
        {"name": "Squarespace", "url": "https://www.squarespace.com/", "method": "email", "category": "blog"},
    ],

    # ════ VIDEO / STREAMING ════
    "video_content": [
        {"name": "YouTube Partner", "url": "https://studio.youtube.com/", "method": "oauth_google", "category": "video_ads"},
        {"name": "Twitch Affiliate", "url": "https://www.twitch.tv/signup", "method": "email", "category": "streaming"},
        {"name": "TikTok Creator Fund", "url": "https://www.tiktok.com/", "method": "email", "category": "video_ads"},
        {"name": "Instagram Creator", "url": "https://www.instagram.com/accounts/emailsignup/", "method": "email", "category": "video_ads"},
        {"name": "Facebook Creator", "url": "https://www.facebook.com/", "method": "email", "category": "video_ads"},
    ],

    # ════ MORE CLOUD / DEVELOPER ════
    "more_cloud": [
        {"name": "GitHub Sponsors", "url": "https://github.com/sponsors", "method": "oauth_github", "category": "sponsorship"},
        {"name": "Patreon", "url": "https://www.patreon.com/signup", "method": "email", "category": "sponsorship"},
        {"name": "Buy Me a Coffee", "url": "https://www.buymeacoffee.com/signup", "method": "email", "category": "sponsorship"},
        {"name": "Ko-fi", "url": "https://ko-fi.com/account/register", "method": "email", "category": "sponsorship"},
        {"name": "Open Collective", "url": "https://opencollective.com/", "method": "email", "category": "sponsorship"},
        {"name": "Gumroad Creator", "url": "https://gumroad.com/signup", "method": "oauth_twitter", "category": "sell_tips"},
        {"name": "Flattr", "url": "https://flattr.com/", "method": "email", "category": "sponsorship"},
        {"name": "Liberapay", "url": "https://liberapay.com/", "method": "email", "category": "sponsorship"},
        {"name": "Memberful", "url": "https://memberful.com/", "method": "email", "category": "membership"},
    ],

    # ════ AFFILIATE EXPANDED ════
    "affiliate_more": [
        {"name": "Fiverr Affiliates", "url": "https://affiliates.fiverr.com/", "method": "email", "category": "affiliate"},
        {"name": "Upwork Affiliates", "url": "https://www.upwork.com/affiliates", "method": "email", "category": "affiliate"},
        {"name": "ShareASale", "url": "https://account.shareasale.com/merchant/signup/", "method": "email", "category": "affiliate"},
        {"name": "CJ Affiliate", "url": "https://signup.cj.com/member/signup", "method": "email", "category": "affiliate"},
        {"name": "Rakuten", "url": "https://signup.rakuten.com/", "method": "email", "category": "affiliate"},
        {"name": "Awin", "url": "https://www.awin.com/", "method": "email", "category": "affiliate"},
        {"name": "Impact", "url": "https://impact.com/", "method": "email", "category": "affiliate"},
        {"name": "PartnerStack", "url": "https://partnerstack.com/", "method": "email", "category": "affiliate"},
        {"name": "eBay Partner", "url": "https://partnernetwork.ebay.com/", "method": "email", "category": "affiliate"},
        {"name": "Etsy Affiliate", "url": "https://www.etsy.com/affiliates", "method": "email", "category": "affiliate"},
        {"name": "WP Engine", "url": "https://wpengine.com/affiliates/", "method": "email", "category": "affiliate"},
        {"name": "HubSpot", "url": "https://www.hubspot.com/partners/affiliates", "method": "email", "category": "affiliate"},
        {"name": "Teachable Affiliate", "url": "https://teachable.com/affiliates", "method": "email", "category": "affiliate"},
        {"name": "GetResponse", "url": "https://www.getresponse.com/affiliates.html", "method": "email", "category": "affiliate"},
        {"name": "Canva Affiliate", "url": "https://www.canva.com/affiliates/", "method": "email", "category": "affiliate"},
        {"name": "Figma Affiliate", "url": "https://www.figma.com/affiliates", "method": "email", "category": "affiliate"},
        {"name": "Notion Affiliate", "url": "https://affiliate.notion.so/", "method": "email", "category": "affiliate"},
        {"name": "Airtable Affiliate", "url": "https://airtable.com/affiliates", "method": "email", "category": "affiliate"},
        {"name": "Zapier Affiliate", "url": "https://zapier.com/affiliates", "method": "email", "category": "affiliate"},
    ],

    # ════ SELL SERVICES MARKETPLACE ════
    "services_marketplace": [
        {"name": "Fiverr Pro", "url": "https://www.fiverr.com/pro", "method": "email", "category": "premium_gigs"},
        {"name": "TaskRabbit", "url": "https://www.taskrabbit.com/", "method": "email", "category": "local_services"},
        {"name": "Thumbtack", "url": "https://www.thumbtack.com/pro", "method": "email", "category": "local_services"},
        {"name": "Etsy Services", "url": "https://www.etsy.com/services", "method": "email", "category": "services"},
    ],
}


def get_total_count() -> int:
    """Total number of platforms."""
    return sum(len(p) for p in ALL_PLATFORMS.values())


def main():
    print("=" * 70)
    print(f"📊 EXPANDED PLATFORM LIST: {get_total_count()} platforms")
    print("=" * 70)
    print()
    for cat, platforms in ALL_PLATFORMS.items():
        print(f"📁 {cat.upper()} ({len(platforms)} platforms):")
        for p in platforms[:5]:
            print(f"   • {p['name']:<30} [{p['method']}]")
        if len(platforms) > 5:
            print(f"   ... and {len(platforms) - 5} more")
        print()


if __name__ == "__main__":
    main()
