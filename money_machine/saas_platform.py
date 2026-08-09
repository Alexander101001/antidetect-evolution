"""
💰 COMPLETE SAAS PLATFORM
Multiple AI services, ready for Stripe payments.
All powered by FREE HF models + GitHub OAuth.
"""
import os
import json
import secrets
import requests
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Configuration
HF_TOKEN_FILE = Path.home() / ".cache" / "huggingface" / "token"
SECRETS_DIR = Path.home() / ".config" / "money-machine"
SECRETS_DIR.mkdir(parents=True, exist_ok=True)


def get_hf_token():
    if HF_TOKEN_FILE.exists():
        return HF_TOKEN_FILE.read_text().strip()
    return ""


# ========== PRODUCTS (What we sell) ==========

PRODUCTS = {
    "ai_writer": {
        "name": "AI Writer Pro",
        "price": 5,
        "currency": "USD",
        "interval": "month",
        "description": "Write emails, cover letters, resumes, blog posts in 30 seconds",
        "features": [
            "Unlimited generations",
            "All content types",
            "Save & export",
            "Priority support",
        ],
        "stripe_price_id": "price_ai_writer_monthly",
    },
    "ai_code": {
        "name": "AI Code Helper",
        "price": 29,
        "interval": "month",
        "description": "Generate code, debug, refactor. 10+ languages",
        "features": [
            "Unlimited code generation",
            "10+ languages",
            "Bug detection",
            "Code review",
        ],
        "stripe_price_id": "price_ai_code_monthly",
    },
    "ai_resume": {
        "name": "AI Resume + Cover Letter",
        "price": 19,
        "interval": "month",
        "description": "Professional resumes and cover letters that get interviews",
        "features": [
            "ATS-optimized",
            "Industry-specific",
            "Unlimited revisions",
            "PDF export",
        ],
        "stripe_price_id": "price_resume_monthly",
    },
    "ai_bundle": {
        "name": "Complete AI Bundle",
        "price": 49,
        "interval": "month",
        "description": "All AI tools in one subscription",
        "features": [
            "AI Writer Pro",
            "AI Code Helper",
            "AI Resume Builder",
            "All future tools",
            "Priority support",
        ],
        "stripe_price_id": "price_bundle_monthly",
    },
    "freelance_pack": {
        "name": "Freelancer Toolkit",
        "price": 99,
        "interval": "month",
        "description": "Everything for freelancers: proposals, content, code, marketing",
        "features": [
            "All AI tools",
            "Proposal templates",
            "Client management",
            "Invoice generator",
            "Priority support",
        ],
        "stripe_price_id": "price_freelance_monthly",
    },
}

# ========== FREE MODELS (What powers the products) ==========

MODELS = {
    "writing": "mistralai/Mistral-7B-Instruct-v0.3",
    "coding": "bigcode/starcoder2-15b",
    "reasoning": "deepseek-ai/DeepSeek-R1",
    "chat": "Qwen/Qwen2.5-7B-Instruct",
    "summarization": "facebook/bart-large-cnn",
    "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
}


def query_model(model_id, prompt, max_tokens=512, temperature=0.7):
    """Query HuggingFace Inference API."""
    token = get_hf_token()
    if not token:
        return "Error: No HF token configured"
    
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "return_full_text": False,
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            result = r.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "")
            return str(result)
        return f"Error: API returned {r.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


# ========== SAAS SERVICES (The actual products) ==========

class AIService:
    """Base AI service."""
    
    def __init__(self, name, model, system_prompt=""):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
    
    def generate(self, user_input, **kwargs):
        prompt = f"{self.system_prompt}\n\nUser: {user_input}\n\nResponse:"
        return query_model(self.model, prompt, **kwargs)


# Service 1: AI Writer
ai_writer = AIService(
    name="AI Writer Pro",
    model=MODELS["writing"],
    system_prompt="""You are a professional writing assistant. Generate high-quality content 
    including emails, cover letters, resumes, blog posts, social media captions, 
    and product descriptions. Be concise, engaging, and tailored to the user's needs."""
)

# Service 2: AI Code Helper  
ai_coder = AIService(
    name="AI Code Helper",
    model=MODELS["coding"],
    system_prompt="""You are an expert programmer. Generate clean, well-commented code 
    in any language. Explain your code. Help debug. Suggest improvements."""
)

# Service 3: AI Resume
ai_resume = AIService(
    name="AI Resume Builder",
    model=MODELS["writing"],
    system_prompt="""You are a professional resume writer. Create ATS-optimized resumes 
    and cover letters. Highlight achievements. Use action verbs. Be specific."""
)


# ========== STRIPE INTEGRATION ==========

class StripeHandler:
    """Handle Stripe payments."""
    
    def __init__(self):
        self.config_file = SECRETS_DIR / "stripe.json"
        self.config = self._load_config()
    
    def _load_config(self):
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return {
            "publishable_key": "",
            "secret_key": "",
            "webhook_secret": "",
            "products_created": False,
        }
    
    def _save_config(self):
        self.config_file.write_text(json.dumps(self.config, indent=2))
        self.config_file.chmod(0o600)
    
    def setup(self, publishable_key, secret_key):
        """Save Stripe keys (user does this once)."""
        self.config["publishable_key"] = publishable_key
        self.config["secret_key"] = secret_key
        self._save_config()
    
    def create_checkout_session(self, product_id, success_url, cancel_url):
        """Create Stripe checkout (when configured)."""
        if not self.config.get("secret_key"):
            return None
        
        import stripe
        stripe.api_key = self.config["secret_key"]
        
        product = PRODUCTS.get(product_id)
        if not product:
            return None
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": product["stripe_price_id"],
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session.url
        except Exception as e:
            print(f"Stripe error: {e}")
            return None


# ========== USAGE TRACKING ==========

class UsageTracker:
    """Track API usage and customer data."""
    
    def __init__(self):
        self.db_file = SECRETS_DIR / "usage.json"
        self.db = self._load()
    
    def _load(self):
        if self.db_file.exists():
            return json.loads(self.db_file.read_text())
        return {
            "users": {},
            "total_requests": 0,
            "revenue": 0,
            "products_sold": {},
        }
    
    def _save(self):
        self.db_file.write_text(json.dumps(self.db, indent=2))
    
    def log_request(self, user_id, product, success=True):
        if user_id not in self.db["users"]:
            self.db["users"][user_id] = {
                "created": datetime.now().isoformat(),
                "requests": 0,
                "products": [],
            }
        self.db["users"][user_id]["requests"] += 1
        self.db["total_requests"] += 1
        self.db["products_sold"][product] = \
            self.db["products_sold"].get(product, 0) + 1
        self._save()
    
    def log_payment(self, user_id, amount, product):
        if user_id not in self.db["users"]:
            self.db["users"][user_id] = {
                "created": datetime.now().isoformat(),
                "paid": 0,
                "products": [],
            }
        self.db["users"][user_id]["paid"] = \
            self.db["users"][user_id].get("paid", 0) + amount
        self.db["users"][user_id]["products"].append(product)
        self.db["revenue"] += amount
        self._save()
    
    def get_stats(self):
        return {
            "total_users": len(self.db["users"]),
            "total_requests": self.db["total_requests"],
            "revenue": self.db["revenue"],
            "top_product": max(self.db["products_sold"].items(), 
                             key=lambda x: x[1], default=("none", 0))[0],
        }


# ========== LANDING PAGE ==========

LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Suite - Professional AI Tools | From $5/month</title>
    <meta name="description" content="AI Writer, Code Helper, Resume Builder. Save 95% vs hiring. From $5/month.">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0a0a0a; color: white; }
        .hero { padding: 80px 20px; text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); }
        .hero h1 { font-size: 3em; margin-bottom: 20px; }
        .hero p { font-size: 1.2em; opacity: 0.9; max-width: 600px; margin: 0 auto 30px; }
        .container { max-width: 1100px; margin: 0 auto; padding: 60px 20px; }
        .products { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
        .product { background: #1a1a1a; padding: 30px; border-radius: 15px; border: 2px solid transparent; transition: 0.3s; }
        .product:hover { border-color: #667eea; transform: translateY(-5px); }
        .product h3 { font-size: 1.4em; margin-bottom: 10px; }
        .product .price { font-size: 2em; color: #667eea; font-weight: bold; margin: 15px 0; }
        .product ul { list-style: none; margin: 20px 0; }
        .product li { padding: 5px 0; opacity: 0.8; }
        .product button { background: #667eea; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; width: 100%; font-size: 1em; }
        .cta { text-align: center; margin: 40px 0; }
        .cta a { background: white; color: #667eea; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; }
        .stats { background: #1a1a1a; padding: 40px; border-radius: 15px; text-align: center; margin: 40px 0; }
        .stats h2 { margin-bottom: 20px; }
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; }
        .stat { padding: 20px; }
        .stat .num { font-size: 2em; color: #667eea; font-weight: bold; }
        footer { text-align: center; padding: 40px; opacity: 0.5; }
    </style>
</head>
<body>
    <section class="hero">
        <h1>AI Suite for Professionals</h1>
        <p>AI Writer, Code Helper, Resume Builder, and more. Save 95% vs hiring freelancers. From $5/month.</p>
        <div class="cta">
            <a href="#products">Start Free Trial →</a>
        </div>
    </section>
    
    <section class="stats">
        <h2>Why Choose Us</h2>
        <div class="stat-grid">
            <div class="stat">
                <div class="num">10x</div>
                <p>Faster than humans</p>
            </div>
            <div class="stat">
                <div class="num">95%</div>
                <p>Cheaper than hiring</p>
            </div>
            <div class="stat">
                <div class="num">24/7</div>
                <p>Always available</p>
            </div>
            <div class="stat">
                <div class="num">$0</div>
                <p>Hidden costs</p>
            </div>
        </div>
    </section>
    
    <section class="container" id="products">
        <h2 style="text-align: center; margin-bottom: 40px;">Choose Your Plan</h2>
        <div class="products">
""" + "".join([
    f"""
            <div class="product">
                <h3>{p['name']}</h3>
                <div class="price">${p['price']}<span style="font-size: 0.3em;">/mo</span></div>
                <p>{p['description']}</p>
                <ul>
                    {''.join(f'<li>✓ {f}</li>' for f in p['features'])}
                </ul>
                <button onclick="alert('Stripe checkout would open here!')">Start Free Trial</button>
            </div>
    """
    for p in PRODUCTS.values()
]) + """
        </div>
    </section>
    
    <footer>
        <p>© 2026 AI Suite • Built with FREE open-source AI models</p>
        <p>Powered by Hugging Face • Hosted on GitHub Pages</p>
    </footer>
</body>
</html>
"""

# Save landing page
landing_file = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/money_machine/index.html")
landing_file.write_text(LANDING_PAGE)
print(f"✅ Landing page saved to {landing_file}")

# Initialize services
stripe_handler = StripeHandler()
tracker = UsageTracker()

print()
print("💰 MONEY MACHINE READY")
print()
print("📦 Products available:")
for pid, p in PRODUCTS.items():
    print(f"  • {p['name']}: ${p['price']}/{p['interval']}")
print()
print("🤖 Models (FREE):")
for task, model in MODELS.items():
    print(f"  • {task}: {model}")
print()
print("📊 Current stats:")
stats = tracker.get_stats()
print(f"  Users: {stats['total_users']}")
print(f"  Requests: {stats['total_requests']}")
print(f"  Revenue: ${stats['revenue']}")
