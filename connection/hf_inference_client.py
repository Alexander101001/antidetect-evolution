"""
🤗 HF INFERENCE CLIENT
Connects to Hugging Face Inference API for real AI.
Uses FREE models.
"""
import json
import time
import requests
import os
from pathlib import Path

class HFInferenceClient:
    """
    Use Hugging Face Inference API for FREE AI.
    No API key needed for some models.
    """
    
    # Models with FREE inference
    FREE_MODELS = {
        "chat": "mistralai/Mistral-7B-Instruct-v0.2",
        "code": "bigcode/starcoder2-3b",
        "summarize": "sshleifer/distilbart-cnn-12-6",
        "translate": "Helsinki-NLP/opus-mt-en-ar",
        "classify": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "embed": "sentence-transformers/all-MiniLM-L6-v2",
        "answer": "deepset/roberta-base-squad2",
    }
    
    API_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(self, token=None):
        self.token = token or os.environ.get("HF_TOKEN") or self._get_token()
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _get_token(self):
        # Try cached token
        token_file = Path.home() / ".cache/huggingface/token"
        if token_file.exists():
            return token_file.read_text().strip()
        return None
    
    def query(self, model_name, inputs, **kwargs):
        """
        Query a model.
        Returns dict with response or error.
        """
        model = self.FREE_MODELS.get(model_name, model_name)
        url = f"{self.API_URL}/{model}"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"inputs": inputs, **kwargs},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "status": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_strategy(self, topic):
        """Generate a money-making strategy using AI."""
        prompt = f"""Generate a specific, actionable money-making strategy for: {topic}

Include:
1. Target audience
2. Monetization method
3. Initial investment
4. Time to first dollar
5. Scaling potential

Be specific and practical."""
        
        return self.query("chat", prompt, max_new_tokens=500)
    
    def research_market(self, niche):
        """Research a market niche."""
        prompt = f"""Analyze the market for: {niche}

Provide:
- Market size estimate
- Top 5 competitors
- Entry barriers
- Profit potential
- Recommended starting strategy"""
        
        return self.query("chat", prompt, max_new_tokens=400)
    
    def improve_code(self, code):
        """Get AI suggestions to improve code."""
        prompt = f"""Improve this Python code for performance, readability, and best practices:

{code}

Provide the improved version with comments explaining changes."""
        
        return self.query("code", prompt, max_new_tokens=800)
    
    def write_content(self, topic, style="blog"):
        """Write SEO-optimized content."""
        prompt = f"""Write a {style} about: {topic}

Include:
- SEO-friendly title
- Meta description
- 500+ words
- Subheadings
- Call to action
- Keywords naturally integrated"""
        
        return self.query("chat", prompt, max_new_tokens=1500)


if __name__ == "__main__":
    client = HFInferenceClient()
    
    # Test if API works
    print("🤗 Testing HF Inference API...")
    print()
    
    # Note: Real API calls would need to handle rate limits
    print("Models available:")
    for name, model in client.FREE_MODELS.items():
        print(f"   • {name}: {model}")
