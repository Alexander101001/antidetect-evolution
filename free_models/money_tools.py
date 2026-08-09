"""
💰 MONEY TOOLS USING FREE MODELS
Build real money-making tools using free HF models.
"""
import requests
import json
import os
from pathlib import Path

TOKEN = "8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
CHAT_ID = "890601506"
HF_TOKEN_FILE = Path.home() / ".cache" / "huggingface" / "token"


def get_hf_token():
    if HF_TOKEN_FILE.exists():
        return HF_TOKEN_FILE.read_text().strip()
    return os.environ.get("HF_TOKEN", "")


def query_hf(model, payload, timeout=30):
    """Query HF Inference API."""
    token = get_hf_token()
    if not token:
        return {"error": "No HF token"}
    
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        return r.json() if r.status_code == 200 else {"error": r.status_code}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# TOOL 1: AI Content Generator ($5-29/month SaaS)
# ============================================================

def ai_content_generator():
    """Generate any content using free models."""
    
    PROMPT = f"""Generate a {input('Content type: ')} for {input('Topic: ')}.
    Tone: {input('Tone (formal/casual): ')}
    Length: {input('Length (short/medium/long): ')}
    """
    
    print("\n🤖 Generating content...")
    result = query_hf(
        "mistralai/Mistral-7B-Instruct-v0.3",
        {"inputs": PROMPT, "parameters": {"max_new_tokens": 1024}}
    )
    
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "")
    return "Error generating content"


# ============================================================
# TOOL 2: AI Code Helper ($30-100/hour freelance)
# ============================================================

def ai_code_helper():
    """Generate code using free models."""
    
    PROMPT = f"""Write {input('Language: ')} code for: {input('Task: ')}.
    Requirements: {input('Requirements: ')}
    """
    
    print("\n💻 Generating code...")
    result = query_hf(
        "bigcode/starcoder2-15b",
        {"inputs": PROMPT, "parameters": {"max_new_tokens": 2048}}
    )
    
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "")
    return "Error generating code"


# ============================================================
# TOOL 3: AI Email Writer ($10-50 per email freelance)
# ============================================================

def ai_email_writer():
    """Write emails using free models."""
    
    PROMPT = f"""Write a {input('Email type (sales/follow-up/cold): ')} email.
    To: {input('Recipient: ')}
    About: {input('Subject/topic: ')}
    Tone: {input('Tone: ')}
    """
    
    print("\n📧 Writing email...")
    result = query_hf(
        "mistralai/Mistral-7B-Instruct-v0.3",
        {"inputs": PROMPT, "parameters": {"max_new_tokens": 512}}
    )
    
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "")
    return "Error writing email"


# ============================================================
# TOOL 4: AI Resume/CV Writer ($50-200 freelance)
# ============================================================

def ai_resume_writer():
    """Generate resume content."""
    
    PROMPT = f"""Write a professional resume for: {input('Job title: ')}.
    Experience: {input('Years of experience: ')}
    Skills: {input('Key skills: ')}
    """
    
    print("\n📄 Writing resume...")
    result = query_hf(
        "mistralai/Mistral-7B-Instruct-v0.3",
        {"inputs": PROMPT, "parameters": {"max_new_tokens": 1024}}
    )
    
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "")
    return "Error writing resume"


if __name__ == "__main__":
    print("💰 MONEY TOOLS (Using FREE HF Models)")
    print()
    print("Available tools:")
    print("  1. AI Content Generator ($5-29/mo SaaS)")
    print("  2. AI Code Helper ($30-100/hr freelance)")
    print("  3. AI Email Writer ($10-50 freelance)")
    print("  4. AI Resume Writer ($50-200 freelance)")
    print()
    print("All powered by FREE HuggingFace models!")
