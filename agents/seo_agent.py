"""
🔍 SEO OPTIMIZER AGENT
Analyzes and improves SEO for all tools.
"""
import re
import json
from pathlib import Path
from base_agent import BaseAgent

class SEOOptimizerAgent(BaseAgent):
    """
    Optimizes tools for search engines.
    - Adds meta tags
    - Improves titles
    - Adds structured data
    - Creates sitemaps
    """
    
    def __init__(self):
        super().__init__("seo_optimizer", "Optimizes tools for search engines")
        self.tools_dir = Path("../empire/tools")
    
    def execute(self, task: dict) -> dict:
        """Optimize a tool for SEO."""
        tool_path = task.get("tool_path")
        if not tool_path:
            return {"error": "No tool_path provided"}
        
        path = Path(tool_path)
        if not path.exists():
            return {"error": f"File not found: {tool_path}"}
        
        html = path.read_text()
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        title = title_match.group(1) if title_match else path.stem
        
        # Add SEO meta tags if missing
        if 'name="description"' not in html.lower():
            description = f"Free online {title}. Fast, easy, no signup required."
            html = html.replace(
                '<head>',
                f'<head>\n<meta name="description" content="{description}">\n<meta name="keywords" content="{title.lower()}, free tool, online tool">'
            )
        
        # Add Open Graph tags
        if 'property="og:' not in html.lower():
            og_tags = f'''
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://alexander101001.github.io/tools-empire/{path.name}">
'''
            html = html.replace('<head>', f'<head>{og_tags}')
        
        # Add JSON-LD structured data
        if 'application/ld+json' not in html.lower():
            structured_data = f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "{title}",
  "description": "{description}",
  "url": "https://alexander101001.github.io/tools-empire/{path.name}",
  "applicationCategory": "UtilityApplication",
  "operatingSystem": "Any",
  "offers": {{
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }}
}}
</script>'''
            html = html.replace('</head>', f'{structured_data}\n</head>')
        
        path.write_text(html)
        
        return {
            "success": True,
            "tool": path.name,
            "optimizations": ["meta_description", "open_graph", "structured_data"]
        }


if __name__ == "__main__":
    agent = SEOOptimizerAgent()
    
    # Test on a tool
    tools = list(Path("../empire/tools").glob("*.html"))
    if tools:
        result = agent.execute({"tool_path": str(tools[0])})
        print(f"Result: {result}")
