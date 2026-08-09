"""
☁️ CLOUD CLIENT - Uses HF Space for AI inference
This works around the local network restriction.
"""
import requests
import json
from pathlib import Path

# HF Space URL (when deployed)
SPACE_URL = "https://AlexanderGreater90-ai-suite-inference.hf.space"


class CloudAIClient:
    """Connect to AI Suite via HF Space."""
    
    def __init__(self, space_url=SPACE_URL):
        self.space_url = space_url
        self.session = requests.Session()
    
    def _query(self, task, prompt, max_tokens=512):
        try:
            r = self.session.post(
                f"{self.space_url}/generate",
                json={
                    "task": task,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                },
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get("result", "")
            return f"Error: {r.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def write(self, prompt):
        return self._query("writing", prompt)
    
    def code(self, prompt):
        return self._query("coding", prompt, max_tokens=2048)
    
    def reason(self, prompt):
        return self._query("reasoning", prompt)
    
    def chat(self, prompt):
        return self._query("chat", prompt)


# Test
if __name__ == "__main__":
    client = CloudAIClient()
    print("☁️ Cloud AI Client")
    print(f"URL: {SPACE_URL}")
    print()
    print("Methods: write(), code(), reason(), chat()")
