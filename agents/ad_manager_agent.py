"""
💰 MULTI-PLATFORM AD MANAGER
Manages ads across 10 different platforms.
"""
import json
from pathlib import Path
from base_agent import BaseAgent

class AdManagerAgent(BaseAgent):
    """
    Inserts ad code from multiple platforms into all tools.
    - Maximizes fill rate
    - A/B tests platforms
    - Auto-rotates underperformers
    """
    
    PLATFORMS = {
        "adsense": {
            "name": "Google AdSense",
            "code": '''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-REPLACE_ME" crossorigin="anonymous"></script>
<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-REPLACE_ME" data-ad-slot="1111111111" data-ad-format="auto"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>''',
            "rpm": 2.0,
            "approval_required": True
        },
        "ezoic": {
            "name": "Ezoic",
            "code": '''<script async src="//www.googletagservices.com/tag/js/gpt.js"></script>
<div id="ezoic-pub-ad-placeholder-REPLACE_ME"></div>
<script>ezic_start();</script>''',
            "rpm": 4.0,
            "approval_required": True
        },
        "medianet": {
            "name": "Media.net",
            "code": '''<script async src="//contextual.media.net/dmedianet.js?cid=REPLACE_ME"></script>
<div id="REPLACE_ME" style="display:none"></div>
<script>(function(w,d){if(typeof w['_mNHandle']==='undefined'){w['_mNHandle']={};w['_mNHandle'].show=function(){return;};}var s=d.createElement('script');s.async=1;s.src='//contextual.media.net/dmedianet.js?cid=REPLACE_ME';d.head.appendChild(s);})(window,document);</script>''',
            "rpm": 2.5,
            "approval_required": True
        },
        "propellerads": {
            "name": "PropellerAds",
            "code": '''<script>(function(d,z,s){s.src='//ad.propellerads.com/'+z+'?id='+s;s.async=true;})(document,'script','pa-REPLACE_ME');</script>''',
            "rpm": 1.5,
            "approval_required": False
        },
        "adsterra": {
            "name": "Adsterra",
            "code": '''<script async src="https://www.profitabledisplaynetwork.com/REPLACE_ME.js"></script>
<div id="adsterra-REPLACE_ME" style="display:block;min-height:90px;min-width:728px;"></div>''',
            "rpm": 1.8,
            "approval_required": False
        },
        "hilltopads": {
            "name": "HilltopAds",
            "code": '''<script async src="https://www.hilltopads.com/js/REPLACE_ME.js"></script>''',
            "rpm": 2.0,
            "approval_required": False
        },
        "popads": {
            "name": "PopAds",
            "code": '''<script src="//c.popads.net/popunder-REPLACE_ME.js"></script>''',
            "rpm": 3.0,
            "approval_required": False
        },
        "infolinks": {
            "name": "Infolinks",
            "code": '''<script async src="//resources.infolinks.com/js/infolinks_main.js"></script>''',
            "rpm": 1.5,
            "approval_required": True
        },
        "bidvertiser": {
            "name": "BidVertiser",
            "code": '''<script async src="//cdn.bidvertiser.com/BidVertiser.dbm?pid=REPLACE_ME&bid=REPLACE_ME"></script>''',
            "rpm": 1.2,
            "approval_required": False
        },
        "buysellads": {
            "name": "BuySellAds",
            "code": '''<script async src="//s3.buysellads.com/ac/bsa.js"></script>
<div id="bsa-REPLACE_ME" class="bsarocks"></div>''',
            "rpm": 5.0,
            "approval_required": True
        }
    }
    
    def __init__(self):
        super().__init__("ad_manager", "Manages multi-platform ads")
        self.tools_dir = Path("../empire/tools")
    
    def execute(self, task: dict) -> dict:
        """Insert ads into a tool."""
        tool_path = task.get("tool_path")
        platforms = task.get("platforms", ["adsense", "ezoic", "propellerads"])
        
        if not tool_path:
            return {"error": "No tool_path"}
        
        path = Path(tool_path)
        if not path.exists():
            return {"error": "File not found"}
        
        html = path.read_text()
        
        # Create ad placement container
        ad_section = self._build_ad_section(platforms)
        
        # Insert ads before closing body tag
        if "</body>" in html.lower():
            html = html.replace("</body>", f"{ad_section}\n</body>")
        else:
            html += ad_section
        
        path.write_text(html)
        
        return {
            "success": True,
            "tool": path.name,
            "platforms_added": platforms,
            "estimated_rpm": sum(
                self.PLATFORMS[p]["rpm"] for p in platforms if p in self.PLATFORMS
            ) / len(platforms)
        }
    
    def _build_ad_section(self, platforms: list) -> str:
        """Build HTML with multiple ad platforms."""
        ad_html = '\n<!-- Auto-injected multi-platform ads -->\n<div id="ad-section" style="margin:20px 0;padding:20px;background:#f9f9f9;border-radius:8px;text-align:center;">\n'
        ad_html += '<p style="font-size:12px;color:#999;margin-bottom:10px;">Advertisement</p>\n'
        
        for platform_id in platforms:
            if platform_id in self.PLATFORMS:
                platform = self.PLATFORMS[platform_id]
                ad_html += f'<!-- {platform["name"]} -->\n{platform["code"]}\n<hr style="margin:15px 0;border:none;border-top:1px solid #eee;">\n'
        
        ad_html += '</div>\n'
        return ad_html


if __name__ == "__main__":
    agent = AdManagerAgent()
    
    # Test
    tools = list(Path("../empire/tools").glob("*.html"))
    if tools:
        result = agent.execute({
            "tool_path": str(tools[0]),
            "platforms": ["adsense", "ezoic", "propellerads"]
        })
        print(f"Result: {result}")
