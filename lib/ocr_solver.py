#!/usr/bin/env python3
"""
OCR Captcha Solver — uses Tesseract for image-based CAPTCHAs.

Free, self-hosted, no API needed.
Accuracy: low for distorted CAPTCHAs (~30-50%), high for plain text images.
Best for: simple image-text CAPTCHAs, NOT reCAPTCHA v2.
"""

import os
import re
import io
import time
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

import requests
from unified import SmartClient


@dataclass
class CaptchaImage:
    """A captcha image fetched and ready for OCR."""
    image_data: bytes
    format: str
    source_url: str


class OCRSolver:
    """Solve simple image CAPTCHAs using Tesseract."""

    def __init__(self):
        self.client = SmartClient()
        if not HAS_TESSERACT:
            print("⚠️  pytesseract not installed. Run: pip install pytesseract Pillow")

    def download_captcha(self, url: str, referer: Optional[str] = None) -> Optional[CaptchaImage]:
        """Download a CAPTCHA image from URL."""
        try:
            headers = {}
            if referer:
                headers['Referer'] = referer
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()

            # Detect format from content
            fmt = "PNG"
            if r.content[:3] == b'\xff\xd8\xff':
                fmt = "JPEG"
            elif r.content[:8] == b'\x89PNG\r\n\x1a\n':
                fmt = "PNG"
            elif r.content[:4] == b'GIF8':
                fmt = "GIF"

            return CaptchaImage(
                image_data=r.content,
                format=fmt,
                source_url=url,
            )
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

    def solve(self, image: CaptchaImage, preprocess: bool = True) -> Optional[str]:
        """
        Solve a captcha image. Returns the recognized text.
        preprocess=True: apply image processing for better OCR accuracy
        """
        if not HAS_TESSERACT:
            return None

        try:
            img = Image.open(io.BytesIO(image.image_data))

            if preprocess:
                img = self._preprocess(img)

            # OCR with config tuned for captchas
            custom_config = (
                '--oem 3 --psm 7 '
                '-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )
            text = pytesseract.image_to_string(img, config=custom_config)

            # Clean result
            text = re.sub(r'[^a-zA-Z0-9]', '', text).strip()
            return text if text else None

        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return None

    def _preprocess(self, img: Image.Image) -> Image.Image:
        """Apply preprocessing to improve OCR accuracy."""
        # Convert to grayscale
        img = img.convert('L')

        # Increase contrast (threshold)
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0)

        # Resize if too small (Tesseract works better on 200px+ height)
        if img.height < 100:
            scale = 200 / img.height
            new_size = (int(img.width * scale), 200)
            img = img.resize(new_size, Image.LANCZOS)

        return img

    def solve_url(self, url: str, referer: Optional[str] = None) -> Optional[str]:
        """Download and solve in one step."""
        img = self.download_captcha(url, referer)
        if not img:
            return None
        return self.solve(img)


# Audio reCAPTCHA solver using Whisper
class AudioCaptchaSolver:
    """
    Defeat audio reCAPTCHA using Whisper speech-to-text.
    ReCAPTCHA has an audio version — download it, transcribe, get code.

    Note: Google has reduced audio attack viability in 2024.
    Still works on some sites.
    """

    def __init__(self):
        self.client = SmartClient()

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file using local Whisper (free)."""
        try:
            import whisper
            model = whisper.load_model("base")  # tiny, base, small, medium, large
            result = model.transcribe(audio_path)
            return result["text"].strip()
        except ImportError:
            print("❌ whisper not installed. Run: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"❌ Whisper failed: {e}")
            return None


if __name__ == "__main__":
    print("🧪 Testing OCR Solver...")
    if HAS_TESSERACT:
        print("✅ Tesseract ready")
        print(f"   Path: {pytesseract.pytesseract.tesseract_cmd}")
    else:
        print("❌ Tesseract not available")
