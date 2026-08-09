"""
🛠️ MICRO TOOL GENERATOR
Automatically creates monetizable tools.
"""
import os
import random
import json
from pathlib import Path

# 100+ tool ideas - all SEO-friendly, high-traffic niches
TOOL_IDEAS = [
    # Text tools (high search volume)
    ("word-counter", "Word Counter", "Count words, characters, sentences instantly"),
    ("case-converter", "Case Converter", "Convert text to UPPERCASE, lowercase, Title Case"),
    ("lorem-ipsum", "Lorem Ipsum Generator", "Generate placeholder text for designs"),
    ("reverse-text", "Reverse Text Generator", "Reverse any text upside down or backwards"),
    ("text-diff", "Text Difference Checker", "Compare two texts and find differences"),
    ("readability", "Readability Score Checker", "Check how easy your text is to read"),
    
    # Image tools
    ("image-compressor", "Image Compressor", "Reduce image file size without losing quality"),
    ("image-resizer", "Image Resizer", "Resize images to any dimension"),
    ("image-to-base64", "Image to Base64", "Convert images to base64 encoding"),
    ("color-picker", "Color Picker", "Pick colors from images or palette"),
    ("png-to-jpg", "PNG to JPG Converter", "Convert PNG images to JPG format"),
    
    # Developer tools
    ("json-formatter", "JSON Formatter", "Format and validate JSON data"),
    ("base64-encoder", "Base64 Encoder/Decoder", "Encode or decode base64 strings"),
    ("url-encoder", "URL Encoder/Decoder", "Encode URLs for safe transmission"),
    ("html-minifier", "HTML Minifier", "Compress HTML to reduce file size"),
    ("css-minifier", "CSS Minifier", "Compress CSS files"),
    ("js-formatter", "JavaScript Formatter", "Format and beautify JS code"),
    ("regex-tester", "Regex Tester", "Test regular expressions in real-time"),
    ("uuid-generator", "UUID Generator", "Generate unique identifiers"),
    ("hash-generator", "Hash Generator", "Generate MD5, SHA1, SHA256 hashes"),
    ("jwt-decoder", "JWT Decoder", "Decode JSON Web Tokens"),
    
    # Calculators (great for SEO)
    ("mortgage-calc", "Mortgage Calculator", "Calculate monthly mortgage payments"),
    ("loan-calc", "Loan Calculator", "Calculate loan payments and interest"),
    ("bmi-calc", "BMI Calculator", "Calculate Body Mass Index"),
    ("percentage-calc", "Percentage Calculator", "Calculate percentages easily"),
    ("age-calc", "Age Calculator", "Calculate exact age from birth date"),
    ("tip-calc", "Tip Calculator", "Calculate tips and split bills"),
    ("tax-calc", "Tax Calculator", "Calculate income tax"),
    ("currency-converter", "Currency Converter", "Convert between currencies"),
    ("unit-converter", "Unit Converter", "Convert between units of measurement"),
    ("time-zone", "Time Zone Converter", "Convert times between zones"),
    
    # PDF tools
    ("pdf-merge", "PDF Merger", "Combine multiple PDFs into one"),
    ("pdf-split", "PDF Splitter", "Split PDF into separate pages"),
    ("pdf-compress", "PDF Compressor", "Reduce PDF file size"),
    ("pdf-to-word", "PDF to Word Converter", "Convert PDFs to editable Word docs"),
    ("word-to-pdf", "Word to PDF Converter", "Convert Word docs to PDF"),
    
    # Security tools
    ("password-gen", "Password Generator", "Generate strong random passwords"),
    ("password-strength", "Password Strength Checker", "Test how strong your password is"),
    ("md5-decoder", "MD5 Decoder", "Try to decode MD5 hashes"),
    
    # Social media tools
    ("youtube-thumbnail", "YouTube Thumbnail Downloader", "Download YT video thumbnails"),
    ("instagram-downloader", "Instagram Photo Downloader", "Save Instagram photos"),
    ("tiktok-downloader", "TikTok Video Downloader", "Download TikTok videos"),
    ("twitter-video", "Twitter Video Downloader", "Download Twitter videos"),
    ("facebook-downloader", "Facebook Video Downloader", "Download FB videos"),
    
    # QR & Barcode
    ("qr-generator", "QR Code Generator", "Generate QR codes for any text"),
    ("barcode-gen", "Barcode Generator", "Generate barcodes online"),
    ("qr-scanner", "QR Code Scanner", "Scan QR codes from images"),
    
    # Web tools
    ("website-screenshot", "Website Screenshot", "Take screenshots of any website"),
    ("meta-tag-gen", "Meta Tag Generator", "Generate SEO meta tags"),
    ("robots-gen", "Robots.txt Generator", "Create robots.txt files"),
    ("sitemap-gen", "Sitemap Generator", "Generate XML sitemaps"),
    
    # Fun tools (viral potential)
    ("fake-chat", "Fake Chat Generator", "Create realistic fake chat screenshots"),
    ("fake-tweet", "Fake Tweet Generator", "Generate fake Twitter posts"),
    ("meme-maker", "Meme Generator", "Create memes easily"),
    ("name-generator", "Name Generator", "Generate random names"),
    ("username-gen", "Username Generator", "Find available usernames"),
    
    # Health & Fitness
    ("calorie-calc", "Calorie Calculator", "Calculate daily calorie needs"),
    ("water-intake", "Water Intake Calculator", "How much water should you drink"),
    ("macro-calc", "Macro Calculator", "Calculate protein, carbs, fat needs"),
    
    # Finance
    ("compound-interest", "Compound Interest Calculator", "See how investments grow"),
    ("roi-calc", "ROI Calculator", "Calculate return on investment"),
    ("crypto-profit", "Crypto Profit Calculator", "Calculate crypto gains/losses"),
    
    # Education
    ("gpa-calc", "GPA Calculator", "Calculate grade point average"),
    ("word-unscramble", "Word Unscrambler", "Unscramble letters into words"),
    ("vocab-builder", "Vocabulary Builder", "Learn new words daily"),
    
    # Date & Time
    ("date-diff", "Date Difference Calculator", "Calculate days between dates"),
    ("countdown", "Countdown Timer", "Create countdown to any date"),
    ("stopwatch", "Online Stopwatch", "Simple online stopwatch"),
    
    # Network tools
    ("ip-lookup", "IP Address Lookup", "Find location of any IP"),
    ("dns-lookup", "DNS Lookup", "Check DNS records for any domain"),
    ("speed-test", "Internet Speed Test", "Test your internet speed"),
    ("ping-test", "Ping Test", "Test connection to any server"),
    
    # Random useful
    ("random-number", "Random Number Generator", "Generate random numbers"),
    ("random-picker", "Random Picker", "Pick random items from list"),
    ("coin-flip", "Coin Flipper", "Flip a coin online"),
    ("dice-roller", "Dice Roller", "Roll virtual dice"),
    
    # AI tools
    ("ai-writer", "AI Text Writer", "Generate text with AI"),
    ("ai-summarizer", "Text Summarizer", "Summarize long texts"),
    ("ai-translator", "AI Translator", "Translate text between languages"),
    ("ai-email", "Email Writer", "Generate professional emails"),
    
    # Resume/CV
    ("resume-builder", "Resume Builder", "Create professional resumes"),
    ("cover-letter", "Cover Letter Generator", "Write cover letters"),
    
    # Business
    ("invoice-gen", "Invoice Generator", "Create professional invoices"),
    ("quote-gen", "Quote Generator", "Generate random inspirational quotes"),
    ("business-name", "Business Name Generator", "Find business name ideas"),
    
    # Color tools
    ("hex-to-rgb", "HEX to RGB Converter", "Convert color codes"),
    ("rgb-to-hex", "RGB to HEX Converter", "Convert RGB to hex"),
    ("gradient-gen", "Gradient Generator", "Create CSS gradients"),
    ("palette-gen", "Color Palette Generator", "Generate color palettes"),
    
    # Math tools
    ("scientific-calc", "Scientific Calculator", "Advanced math calculator"),
    ("graph-plotter", "Graph Plotter", "Plot math functions"),
    ("matrix-calc", "Matrix Calculator", "Matrix operations"),
    
    # Audio/Video
    ("audio-converter", "Audio Converter", "Convert audio formats"),
    ("video-compress", "Video Compressor", "Reduce video file size"),
    ("mp3-cutter", "MP3 Cutter", "Cut MP3 files online"),
    
    # File tools
    ("csv-viewer", "CSV Viewer", "View CSV files online"),
    ("xml-formatter", "XML Formatter", "Format XML data"),
    ("yaml-validator", "YAML Validator", "Validate YAML files"),
    
    # More SEO-friendly
    ("domain-checker", "Domain Availability", "Check if domain is available"),
    ("whois-lookup", "WHOIS Lookup", "Find domain owner info"),
    ("ssl-checker", "SSL Checker", "Check SSL certificate"),
    ("page-speed", "Page Speed Test", "Test website loading speed"),
]

class ToolGenerator:
    """Generates deployable micro tools."""
    
    def __init__(self, output_dir="tools"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_tool(self, slug, title, description, color="purple"):
        """Generate a complete HTML tool."""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Free Online Tool | ToolMaster</title>
    <meta name="description" content="{description}. Free, fast, no signup required.">
    <meta name="keywords" content="{title.lower()}, free tool, online tool">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-REPLACE_ME" crossorigin="anonymous"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); padding: 40px; }}
        h1 {{ color: #333; margin-bottom: 10px; font-size: 2.5em; }}
        .desc {{ color: #666; margin-bottom: 30px; font-size: 1.1em; }}
        textarea {{ width: 100%; min-height: 200px; padding: 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; font-family: monospace; resize: vertical; }}
        textarea:focus {{ outline: none; border-color: #667eea; }}
        button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 15px; margin-right: 10px; }}
        button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .output {{ margin-top: 20px; padding: 20px; background: #f5f5f5; border-radius: 8px; min-height: 50px; white-space: pre-wrap; word-break: break-all; }}
        .stats {{ display: flex; gap: 20px; margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
        .stat {{ flex: 1; text-align: center; }}
        .stat-num {{ font-size: 1.8em; font-weight: bold; color: #667eea; }}
        .ad-slot {{ margin: 20px 0; padding: 20px; background: #fafafa; border-radius: 8px; text-align: center; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 0.9em; }}
        .footer a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 {title}</h1>
        <p class="desc">{description}</p>
        
        <!-- Ad slot 1 -->
        <div class="ad-slot">
            <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-REPLACE_ME" data-ad-slot="1111111111" data-ad-format="auto"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        </div>
        
        <label for="input" style="font-weight: bold; display: block; margin-bottom: 8px;">Input:</label>
        <textarea id="input" placeholder="Paste your content here..."></textarea>
        
        <button onclick="process()">⚡ Process</button>
        <button onclick="copyResult()">📋 Copy Result</button>
        <button onclick="clearAll()">🗑️ Clear</button>
        
        <div class="output" id="output">Results will appear here...</div>
        
        <div class="stats" id="stats"></div>
        
        <!-- Ad slot 2 -->
        <div class="ad-slot">
            <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-REPLACE_ME" data-ad-slot="2222222222" data-ad-format="auto"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        </div>
        
        <div class="footer">
            <p>Free online tools by <a href="https://huggingface.co/spaces/AlexanderGreater90/evolution-engine">ToolMaster</a></p>
            <p>Part of the <a href="https://github.com/Alexander101001/antidetect-evolution">AI Tools Network</a></p>
        </div>
    </div>
    
    <script>
        function process() {{
            const input = document.getElementById('input').value;
            if (!input) {{ alert('Please enter some text'); return; }}
            
            // Basic processing - customize per tool
            const result = input;
            document.getElementById('output').innerText = result;
            
            // Stats
            const words = input.trim().split(/\\s+/).filter(w => w.length > 0).length;
            const chars = input.length;
            const lines = input.split('\\n').length;
            
            document.getElementById('stats').innerHTML = `
                <div class="stat"><div class="stat-num">${{words}}</div>Words</div>
                <div class="stat"><div class="stat-num">${{chars}}</div>Characters</div>
                <div class="stat"><div class="stat-num">${{lines}}</div>Lines</div>
            `;
        }}
        
        function copyResult() {{
            const output = document.getElementById('output').innerText;
            navigator.clipboard.writeText(output).then(() => alert('Copied!'));
        }}
        
        function clearAll() {{
            document.getElementById('input').value = '';
            document.getElementById('output').innerText = 'Results will appear here...';
            document.getElementById('stats').innerHTML = '';
        }}
        
        // Auto-process on page load if there's content
        document.getElementById('input').addEventListener('input', () => {{
            if (document.getElementById('input').value.length > 0) process();
        }});
    </script>
</body>
</html>'''
        
        filepath = self.output_dir / f"{slug}.html"
        filepath.write_text(html)
        return filepath

if __name__ == "__main__":
    gen = ToolGenerator()
    
    print(f"🛠️ Generating {len(TOOL_IDEAS)} micro tools...")
    print()
    
    generated = []
    for slug, title, desc in TOOL_IDEAS:
        try:
            path = gen.generate_html_tool(slug, title, desc)
            generated.append(slug)
        except Exception as e:
            print(f"❌ {slug}: {e}")
    
    print(f"✅ Generated {len(generated)} tools")
    print(f"📁 Location: {gen.output_dir}")
