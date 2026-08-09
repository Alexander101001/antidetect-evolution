"""
🛠️ TOOL GENERATOR AGENT
Autonomously creates monetizable micro tools.
"""
import asyncio
import random
import json
from pathlib import Path
from base_agent import BaseAgent

class ToolGeneratorAgent(BaseAgent):
    """
    Generates new micro tools based on trending niches.
    """
    
    TOOL_TEMPLATES = {
        "calculator": {
            "html": """<!DOCTYPE html><html><head><title>{title}</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px;background:#f5f5f5;}}
.box{{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}}
input,select{{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;}}
button{{background:#4CAF50;color:white;padding:12px 24px;border:none;border-radius:5px;cursor:pointer;}}
button:hover{{background:#45a049;}}.result{{margin-top:20px;padding:15px;background:#e8f5e9;border-radius:5px;}}</style>
</head><body><div class="box"><h1>{title}</h1><p>{description}</p>
<input id="input1" placeholder="Enter value"><input id="input2" placeholder="Enter value">
<button onclick="calc()">Calculate</button>
<div class="result" id="result"></div></div>
<script>function calc(){{document.getElementById('result').innerText='Result: '+(parseFloat(document.getElementById('input1').value||0)*parseFloat(document.getElementById('input2').value||0));}}</script>
</body></html>""",
            "category": "calculator"
        },
        "converter": {
            "html": """<!DOCTYPE html><html><head><title>{title}</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px;}}
textarea{{width:100%;min-height:200px;padding:10px;border:1px solid #ddd;}}
button{{margin:10px 5px;padding:10px 20px;background:#2196F3;color:white;border:none;border-radius:5px;cursor:pointer;}}</style>
</head><body><h1>{title}</h1><p>{description}</p>
<textarea id="input" placeholder="Paste content here..."></textarea><br>
<button onclick="convert()">Convert</button><button onclick="copy()">Copy</button>
<div id="output" style="margin-top:20px;padding:15px;background:#f5f5f5;border-radius:5px;"></div>
<script>function convert(){{document.getElementById('output').innerText=document.getElementById('input').value.toUpperCase();}}
function copy(){{navigator.clipboard.writeText(document.getElementById('output').innerText);alert('Copied!');}}</script>
</body></html>""",
            "category": "converter"
        },
        "generator": {
            "html": """<!DOCTYPE html><html><head><title>{title}</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px;}}
.box{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;border-radius:10px;}}
button{{background:white;color:#667eea;padding:12px 24px;border:none;border-radius:5px;cursor:pointer;font-weight:bold;}}
.result{{margin-top:20px;padding:15px;background:rgba(255,255,255,0.2);border-radius:5px;word-break:break-all;}}</style>
</head><body><div class="box"><h1>{title}</h1><p>{description}</p>
<button onclick="generate()">Generate</button>
<div class="result" id="result"></div></div>
<script>function generate(){{
const chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
let result='';
for(let i=0;i<16;i++)result+=chars.charAt(Math.floor(Math.random()*chars.length));
document.getElementById('result').innerText=result;
}}</script>
</body></html>""",
            "category": "generator"
        }
    }
    
    def __init__(self):
        super().__init__("tool_generator", "Creates monetizable micro tools")
        self.output_dir = Path("../empire/tools")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, task: dict) -> dict:
        """Generate a new tool."""
        slug = task.get("slug", "new-tool")
        title = task.get("title", "New Tool")
        description = task.get("description", "A useful tool")
        template_type = task.get("template", random.choice(list(self.TOOL_TEMPLATES.keys())))
        
        template = self.TOOL_TEMPLATES[template_type]
        html = template["html"].format(title=title, description=description)
        
        output_path = self.output_dir / f"{slug}.html"
        output_path.write_text(html)
        
        return {
            "success": True,
            "tool": slug,
            "path": str(output_path),
            "template": template_type
        }


if __name__ == "__main__":
    agent = ToolGeneratorAgent()
    
    # Test
    result = agent.execute({
        "slug": "test-tool",
        "title": "Test Calculator",
        "description": "A test calculator",
        "template": "calculator"
    })
    print(f"Result: {result}")
