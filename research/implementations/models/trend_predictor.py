"""
🤗 Predict trends/revenue
Uses: amazon/chronos-2
"""
import json
import requests
from pathlib import Path


class Chronos2:
    """Wrapper for amazon/chronos-2"""
    
    MODEL_ID = "amazon/chronos-2"
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
    print(f"   Use: Predict trends/revenue")
    print(f"   Importance: HIGH - Predict our earnings!")
