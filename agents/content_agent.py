"""
✍️ CONTENT WRITER AGENT
Generates blog posts, descriptions, social media content.
"""
import json
import random
from pathlib import Path
from base_agent import BaseAgent

class ContentWriterAgent(BaseAgent):
    """
    Writes content for tools to drive traffic.
    """
    
    BLOG_TEMPLATES = [
        {
            "title_pattern": "10 Best {topic} Tools in 2026",
            "structure": ["intro", "list of tools", "comparison", "recommendation", "conclusion"]
        },
        {
            "title_pattern": "How to Use {topic} Like a Pro",
            "structure": ["intro", "basics", "advanced tips", "common mistakes", "conclusion"]
        },
        {
            "title_pattern": "{topic}: Complete Guide for Beginners",
            "structure": ["what is", "why use", "how to", "examples", "conclusion"]
        }
    ]
    
    def __init__(self):
        super().__init__("content_writer", "Generates SEO content")
        self.output_dir = Path("../empire/content")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, task: dict) -> dict:
        action = task.get("action", "write_blog")
        
        if action == "write_blog":
            return self._write_blog(task)
        elif action == "write_description":
            return self._write_description(task)
        elif action == "write_social":
            return self._write_social_post(task)
        
        return {"error": f"Unknown action: {action}"}
    
    def _write_blog(self, task: dict) -> dict:
        """Generate a blog post."""
        topic = task.get("topic", "productivity")
        
        template = random.choice(self.BLOG_TEMPLATES)
        title = template["title_pattern"].format(topic=topic.title())
        
        blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | ToolMaster Blog</title>
    <meta name="description" content="Complete guide to {topic}. Free tools, tips, and tricks for 2026.">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; font-size: 2.5em; margin-bottom: 20px; }}
        h2 {{ color: #667eea; margin-top: 30px; }}
        p {{ margin-bottom: 15px; }}
        .tool-link {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0; display: block; text-decoration: none; color: #333; }}
        .tool-link:hover {{ background: #e8e8e8; }}
        .cta {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; margin: 30px 0; }}
        .cta a {{ color: white; background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 10px; }}
    </style>
</head>
<body>
    <article>
        <h1>{title}</h1>
        
        <p>Welcome to our comprehensive guide on <strong>{topic}</strong>. Whether you're a beginner or experienced user, this article will help you master {topic} tools in 2026.</p>
        
        <h2>Why {topic.title()} Matters</h2>
        <p>In today's fast-paced world, having the right {topic} tools can save you hours of work. From free online tools to advanced software, we've compiled the best options for you.</p>
        
        <h2>Top Tools We Recommend</h2>
        
        <a href="https://alexander101001.github.io/tools-empire/" class="tool-link">
            <strong>🛠️ ToolMaster Network</strong> - 100+ free online tools for everything
        </a>
        
        <a href="https://alexander101001.github.io/tools-empire/word-counter.html" class="tool-link">
            <strong>📝 Word Counter</strong> - Free online word counter tool
        </a>
        
        <a href="https://alexander101001.github.io/tools-empire/json-formatter.html" class="tool-link">
            <strong>📋 JSON Formatter</strong> - Format and validate JSON data
        </a>
        
        <h2>How to Choose the Right Tool</h2>
        <p>When selecting a {topic} tool, consider these factors:</p>
        <ul>
            <li>Ease of use</li>
            <li>Features available</li>
            <li>Price (free vs paid)</li>
            <li>Privacy and data handling</li>
            <li>Mobile compatibility</li>
        </ul>
        
        <div class="cta">
            <h3 style="color:white;margin:0;">Try Our Free Tools Now</h3>
            <p style="color:white;">100+ tools, no signup required</p>
            <a href="https://alexander101001.github.io/tools-empire/">Browse All Tools →</a>
        </div>
        
        <h2>Pro Tips</h2>
        <p>Here are some expert tips for getting the most out of {topic} tools:</p>
        <ul>
            <li>Always backup your data before using new tools</li>
            <li>Test tools with sample data first</li>
            <li>Read user reviews and ratings</li>
            <li>Check for regular updates</li>
        </ul>
        
        <h2>Conclusion</h2>
        <p>{topic.title()} tools have come a long way. With the options we've listed, you're well-equipped to handle any task. Start with our free ToolMaster network and explore from there.</p>
        
        <p><em>Last updated: 2026 - All tools tested and verified working.</em></p>
    </article>
</body>
</html>'''
        
        filename = f"blog-{topic.replace(' ', '-').lower()}.html"
        filepath = self.output_dir / filename
        filepath.write_text(blog_html)
        
        return {
            "success": True,
            "file": filename,
            "title": title,
            "word_count": len(blog_html.split())
        }
    
    def _write_description(self, task: dict) -> dict:
        """Write a meta description."""
        tool = task.get("tool", "this tool")
        desc = f"Free online {tool}. Fast, easy, no signup required. Works on all devices. 100% free forever."
        return {"description": desc}
    
    def _write_social_post(self, task: dict) -> dict:
        """Write a social media post."""
        tool = task.get("tool", "our tool")
        posts = [
            f"🚀 Just launched: {tool}! Free, fast, no signup. Check it out: https://alexander101001.github.io/tools-empire/",
            f"💡 Need a {tool}? We built a free one for you: https://alexander101001.github.io/tools-empire/",
            f"🛠️ Free online {tool} - no ads, no limits: https://alexander101001.github.io/tools-empire/",
        ]
        return {"post": random.choice(posts)}


if __name__ == "__main__":
    agent = ContentWriterAgent()
    result = agent.execute({"action": "write_blog", "topic": "productivity"})
    print(f"Result: {result}")
