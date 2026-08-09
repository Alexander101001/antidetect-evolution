"""
🤖 SMART MODEL ROUTER
Routes tasks to best FREE model based on capability.
Uses HuggingFace Inference API (free tier).
"""
import os
import requests
import json
from pathlib import Path

# Free HF models for different tasks
MODELS = {
    "reasoning": {
        "best_free": "deepseek-ai/DeepSeek-R1",
        "alternative": "Qwen/Qwen2.5-72B-Instruct",
        "use_for": "Complex problems, math, logic",
    },
    "writing": {
        "best_free": "mistralai/Mistral-7B-Instruct-v0.3",
        "alternative": "meta-llama/Llama-3.1-8B-Instruct",
        "use_for": "Content, articles, emails",
    },
    "coding": {
        "best_free": "bigcode/starcoder2-15b",
        "alternative": "deepseek-ai/deepseek-coder-33b-instruct",
        "use_for": "Code generation, debugging",
    },
    "chat": {
        "best_free": "Qwen/Qwen2.5-7B-Instruct",
        "alternative": "microsoft/Phi-3.5-mini-instruct",
        "use_for": "Conversation, Q&A",
    },
    "embeddings": {
        "best_free": "sentence-transformers/all-MiniLM-L6-v2",
        "alternative": "BAAI/bge-large-en-v1.5",
        "use_for": "Search, similarity, RAG",
    },
    "summarization": {
        "best_free": "facebook/bart-large-cnn",
        "alternative": "philschmid/bart-large-cnn-samsum",
        "use_for": "Text summarization",
    },
}


class ModelRouter:
    """Route tasks to best free model."""
    
    def __init__(self):
        self.hf_token = os.environ.get("HF_TOKEN", "")
        if not self.hf_token:
            try:
                token_file = Path.home() / ".cache" / "huggingface" / "token"
                if token_file.exists():
                    self.hf_token = token_file.read_text().strip()
            except: pass
    
    def query(self, model_id, payload, timeout=30):
        """Query HuggingFace Inference API."""
        url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            else:
                return {"error": f"Status {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"error": str(e)}
    
    def reason(self, prompt):
        """Complex reasoning task."""
        model = MODELS["reasoning"]["best_free"]
        return self.query(model, {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.3}
        })
    
    def write(self, prompt):
        """Writing task."""
        model = MODELS["writing"]["best_free"]
        return self.query(model, {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 1024, "temperature": 0.7}
        })
    
    def code(self, prompt):
        """Code generation."""
        model = MODELS["coding"]["best_free"]
        return self.query(model, {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 2048, "temperature": 0.2}
        })
    
    def chat(self, message):
        """Chat/Q&A."""
        model = MODELS["chat"]["best_free"]
        return self.query(model, {
            "inputs": message,
            "parameters": {"max_new_tokens": 512, "temperature": 0.7}
        })
    
    def embed(self, text):
        """Get embeddings."""
        model = MODELS["embeddings"]["best_free"]
        return self.query(model, {"inputs": text})
    
    def summarize(self, text):
        """Summarize text."""
        model = MODELS["summarization"]["best_free"]
        return self.query(model, {
            "inputs": text,
            "parameters": {"max_length": 150, "min_length": 30}
        })


# Test
if __name__ == "__main__":
    router = ModelRouter()
    print("🤖 Model Router Ready")
    print()
    print("📋 Available models:")
    for task, info in MODELS.items():
        print(f"  {task}: {info['best_free']}")
    print()
    print("🚀 Use: router.write('your prompt'), router.code('...'), etc.")
