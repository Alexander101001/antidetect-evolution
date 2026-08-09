"""
📤 AUTO-POSTER
Schedules and queues posts.
⚠️ ACTUAL POSTING NEEDS YOUR LOGIN (each platform requires 2FA)
"""
import json
import time
import random
from datetime import datetime
from pathlib import Path
from content_generator import ContentGenerator
from trend_researcher import TrendResearcher

class AutoPoster:
    """
    Generates content queue for posting.
    Note: Actual posting requires your login.
    """
    
    def __init__(self):
        self.queue_file = Path("data/post_queue.json")
        self.queue_file.parent.mkdir(exist_ok=True)
        self.queue = self._load_queue()
        self.content_gen = ContentGenerator()
        self.trend = TrendResearcher()
    
    def _load_queue(self):
        if self.queue_file.exists():
            try:
                return json.loads(self.queue_file.read_text())
            except:
                pass
        return {"posts": [], "posted": [], "stats": {}}
    
    def _save_queue(self):
        self.queue_file.write_text(json.dumps(self.queue, indent=2))
    
    def generate_day_queue(self):
        """Generate today's post queue."""
        print("📝 Generating today's content queue...")
        print()
        
        # Get trends
        trends = self.trend.daily_report()
        hot_niches = trends.get("niches", [])
        
        # Generate posts
        platforms = [
            ("youtube_shorts", "12pm", "video"),
            ("tiktok", "2pm", "video"),
            ("instagram_reels", "4pm", "video"),
            ("x_twitter", "6pm", "text"),
            ("linkedin", "8pm", "text"),
            ("facebook", "10pm", "text"),
        ]
        
        today = []
        for platform, time, content_type in platforms:
            # 2 posts per platform
            for i in range(2):
                niche = random.choice(hot_niches + ["AI Tools & Prompts"])
                post = self.content_gen.generate_post(platform, niche)
                post["scheduled_time"] = f"{time}+{i*30}min"
                post["status"] = "ready_to_post"
                today.append(post)
                self.queue["posts"].append(post)
        
        self._save_queue()
        
        print(f"✅ Generated {len(today)} posts for today")
        return today
    
    def show_queue(self):
        """Display the post queue."""
        print("📤 POST QUEUE")
        print("=" * 50)
        print()
        
        if not self.queue["posts"]:
            print("Queue is empty. Run generate_day_queue() first.")
            return
        
        # Group by platform
        by_platform = {}
        for post in self.queue["posts"][-12:]:  # last 12
            plat = post["platform"]
            by_platform.setdefault(plat, []).append(post)
        
        for platform, posts in by_platform.items():
            print(f"\n📱 {platform.upper()} ({len(posts)} posts):")
            for post in posts:
                print(f"   ⏰ {post.get('scheduled_time', '?')}")
                print(f"   📝 {post['content'][:100]}...")
                print(f"   🏷️  {' '.join(post['hashtags'][:3])}")
                print()


if __name__ == "__main__":
    poster = AutoPoster()
    
    # Generate today's queue
    today_posts = poster.generate_day_queue()
    print()
    
    # Show queue
    poster.show_queue()
