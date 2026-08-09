"""
✍️ CONTENT GENERATOR
Creates content for each platform automatically.
"""
import json
import random
from datetime import datetime
from platforms_database import TRENDING_NICHES_2026

class ContentGenerator:
    """Generate platform-specific content."""
    
    TEMPLATES = {
        "youtube_shorts": [
            "🔥 {niche} hack: {tip}\n\nThis will save you hours!\n\n{niche} #shorts #viral",
            "❌ Stop doing {niche} the WRONG way!\n\n✅ Do this instead: {tip}\n\n#fyp #viral",
            "🤯 {niche} secret they don't want you to know:\n\n{tip}\n\n#trending #viral",
        ],
        "tiktok": [
            "POV: You discovered {niche} hack\n\n{tip}\n\n#fyp #foryou #viral",
            "{niche} hack that will change your life:\n\n{tip}\n\n#trending #tiktok",
            "Tell me you're into {niche} without telling me:\n\n{tip}",
        ],
        "instagram_reels": [
            "📱 Save this {niche} tip!\n\n{tip}\n\nFollow for more! 💜",
            "{niche} hack most people miss:\n\n{tip}\n\nDouble tap if useful! ❤️",
            "Day {n} of {niche} tips:\n\n{tip}\n\nShare with a friend who needs this! 📲",
        ],
        "x_twitter": [
            "{niche} tip that will save you hours:\n\n{tip}\n\nBookmark this. 🔖",
            "I spent {time} learning {niche} so you don't have to.\n\nHere's what works: {tip}",
            "Hot take on {niche}:\n\n{tip}",
        ],
        "linkedin": [
            "After 5 years in {niche}, here's what I learned:\n\n{tip}\n\nThoughts?",
            "{niche} insight: {tip}\n\nThis changed how I approach my work.",
            "I analyzed 100 {niche} strategies.\n\nThe top 1% do this: {tip}",
        ],
        "facebook": [
            "💡 {niche} tip that changed everything for me:\n\n{tip}\n\nShare if helpful!",
            "Anyone else struggle with {niche}?\n\nI found this: {tip}",
        ],
    }
    
    TIPS = {
        "AI Tools & Prompts": [
            "Use this prompt: 'Act as expert X, give me 5 actionable insights about Y'",
            "Try the new AI image generator - results are insane",
            "Use AI to write your emails in 30 seconds",
            "Stop prompting, start conversing - AI is smarter than you think",
            "Free AI tools that beat paid ones",
        ],
        "Personal Finance & Side Hustles": [
            "Save 50% of any raise, invest the rest",
            "Side hustle: sell templates on Gumroad",
            "Compound interest = money makes money",
            "Track every dollar for 30 days = clarity",
            "Emergency fund = 3-6 months expenses",
        ],
        "Health & Longevity": [
            "Walk 10k steps daily = longevity boost",
            "Cold showers activate brown fat",
            "Sleep 7-9 hours = better everything",
            "Drink water before meals = eat less",
            "Vegetables first, then protein, then carbs",
        ],
    }
    
    def generate_post(self, platform, niche=None):
        """Generate a post for a platform."""
        if niche is None:
            niche = random.choice(TRENDING_NICHES_2026)
        
        if niche not in self.TIPS:
            niche = "AI Tools & Prompts"
        
        template = random.choice(self.TEMPLATES.get(platform, self.TEMPLATES["x_twitter"]))
        tip = random.choice(self.TIPS[niche])
        time_spent = random.choice(["6 months", "1 year", "2 years", "3 months"])
        
        post = template.format(
            niche=niche,
            tip=tip,
            time=time_spent,
            n=random.randint(1, 30)
        )
        
        return {
            "platform": platform,
            "niche": niche,
            "content": post,
            "hashtags": self._get_hashtags(platform, niche),
            "created_at": datetime.now().isoformat(),
        }
    
    def _get_hashtags(self, platform, niche):
        """Get platform-specific hashtags."""
        base_tags = ["#viral", "#trending", f"#{niche.lower().replace(' ', '').replace('&', '')}"]
        
        platform_tags = {
            "tiktok": ["#fyp", "#foryou", "#foryoupage"],
            "instagram_reels": ["#reels", "#explore", "#instagood"],
            "youtube_shorts": ["#shorts", "#youtubeshorts"],
            "x_twitter": ["#twitter"],
            "linkedin": ["#career", "#professional"],
        }
        
        return base_tags + platform_tags.get(platform, [])
    
    def daily_content_plan(self):
        """Generate a day's worth of content."""
        platforms = ["youtube_shorts", "tiktok", "instagram_reels", "x_twitter", "linkedin", "facebook"]
        plan = []
        
        for platform in platforms:
            # 1-2 posts per platform per day
            for _ in range(2):
                post = self.generate_post(platform)
                plan.append(post)
        
        return plan


if __name__ == "__main__":
    gen = ContentGenerator()
    
    print("✍️ CONTENT GENERATOR TEST")
    print("=" * 50)
    print()
    
    plan = gen.daily_content_plan()
    print(f"📅 Daily plan: {len(plan)} posts")
    print()
    
    for i, post in enumerate(plan[:3], 1):
        print(f"--- Post {i} ({post['platform']}) ---")
        print(f"Niche: {post['niche']}")
        print(f"Content: {post['content'][:150]}...")
        print(f"Hashtags: {' '.join(post['hashtags'][:5])}")
        print()
