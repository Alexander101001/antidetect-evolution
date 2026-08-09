"""
🤗 Better ranking than cross-encoder
Uses: BAAI/bge-reranker-v2-m3
"""
import json
import requests
from pathlib import Path


class BgeRerankerV2M3:
    """Wrapper for BAAI/bge-reranker-v2-m3"""
    
    MODEL_ID = "BAAI/bge-reranker-v2-m3"
    API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    
    def __init__(self, token=None):
        self.token = token or self._get_token()
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _get_token(self):
        token_file = Path.home() / ".cache/huggingface/token"
        if token_file.exists():
            return token_file.read_text().strip()
        return None
    
    def query(self, inputs, **kwargs):
        """Query the model."""
        try:
            r = requests.post(
                self.API_URL,
                headers=self.headers,
                json={"inputs": inputs, **kwargs},
                timeout=30
            )
            if r.status_code == 200:
                return {"success": True, "data": r.json()}
            return {"success": False, "error": r.text[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fallback(self, inputs):
        """Fallback when API unavailable."""
        return {"fallback": True, "input": str(inputs)[:100]}


if __name__ == "__main__":
    print(f"🤗 {__name__}")
    print(f"   Model: {self.MODEL_ID}")
    print(f"   Use: Better ranking than cross-encoder")
    print(f"   Importance: MEDIUM")
