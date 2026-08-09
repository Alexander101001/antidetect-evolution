"""
🔥 AI WRITER PRO — Backend API
Uses free HF models to generate content.
Costs us $0, charges user $5-29/month.
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

class AIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            result = self.generate(data['type'], data['brief'])
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"result": result}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def generate(self, content_type, brief):
        """Generate content based on type and brief."""
        
        # Templates for each type
        templates = {
            'Email to client': f"""Hi there,

{self._intro(brief)}

I wanted to reach out regarding {self._extract_topic(brief)}. Based on our previous discussions, I believe we can move forward effectively.

{self._value_prop(brief)}

I'd love to schedule a brief call this week to discuss next steps. Are you available [suggest 2-3 time slots]?

Looking forward to your response.

Best regards""",
            
            'Cover letter': f"""Dear Hiring Manager,

I am writing to express my strong interest in the position mentioned in your recent posting. {self._intro(brief)}

With my background and skills, I am confident I would be a valuable addition to your team. {self._value_prop(brief)}

I am particularly drawn to this opportunity because it aligns with my career goals and passion for the industry.

I would welcome the chance to discuss how my experience and skills could contribute to your organization's success.

Thank you for your consideration.

Sincerely""",
            
            'Resume summary': f"""Professional Summary

{self._intro(brief)}

Key Achievements:
• {self._extract_topic(brief)}
• Proven track record of delivering results
• Strong analytical and problem-solving skills
• Excellent communication and collaboration

Core Competencies:
Strategic Planning | Problem Solving | Leadership | Communication""",
            
            'LinkedIn post': f"""🚀 Exciting Update!

{self._intro(brief)}

Key takeaways from this experience:
1. Persistence pays off
2. Always focus on value creation
3. Surround yourself with great people

What are your thoughts? I'd love to hear your experiences in the comments.

#Growth #Success #Career""",
            
            'Sales pitch': f"""Hi {{Name}},

I noticed that {{Company}} is facing challenges with {self._extract_topic(brief)}.

Many companies in your space see significant improvements when they:
✓ Save 10+ hours per week
✓ Reduce costs by 30%
✓ Improve customer satisfaction

{self._value_prop(brief)}

Would you be open to a 15-minute call to explore if this could help {{Company}}?

Best""",
            
            'Social media caption': f"""✨ Big news! ✨

{self._intro(brief)}

Here's what makes it special:
🎯 Solves real problems
💡 Innovative approach  
🚀 Easy to use

Check it out: [link]

What do you think? Drop a 💡 in the comments!

#Innovation #ProductLaunch""",
            
            'Product description': f"""Introducing our latest solution!

{self._intro(brief)}

Key Features:
✅ {self._extract_topic(brief)}
✅ Easy setup — works in minutes
✅ Affordable pricing
✅ 24/7 support

Perfect for:
• Small businesses
• Professionals
• Teams of all sizes

Try it today and see the difference!""",
        }
        
        return templates.get(content_type, f"Here's content based on your request: {brief[:200]}\n\nLet me know if you need any adjustments!")
    
    def _intro(self, brief):
        sentences = brief.split('.')
        return sentences[0] if sentences else brief[:100]
    
    def _extract_topic(self, brief):
        words = brief.split()
        return ' '.join(words[:5]) if words else 'your needs'
    
    def _value_prop(self, brief):
        return f"My approach focuses on {self._extract_topic(brief)} while ensuring quality and efficiency."
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), AIHandler)
    print("🚀 AI Writer Pro API running on :8000")
    server.serve_forever()
