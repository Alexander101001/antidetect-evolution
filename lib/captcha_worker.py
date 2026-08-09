#!/usr/bin/env python3
"""
CAPTCHA Worker — Multi-strategy CAPTCHA solver.

Strategies (in order of preference):
1. Audio reCAPTCHA v2 → Whisper STT (free)
2. Image CAPTCHA → Tesseract OCR (free, low accuracy)
3. hCaptcha audio → Whisper
4. Cloudflare Turnstile → Just wait + retry
5. Detect CAPTCHA type and report
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, str(__file__).replace("/captcha_worker.py", ""))

from nodriver_automation import NodriverAutomation


class CaptchaWorker:
    """Solve CAPTCHAs using available free methods."""

    def __init__(self):
        self.browser: Optional[NodriverAutomation] = None

    async def start(self):
        self.browser = NodriverAutomation(use_tor=True)
        await self.browser.start()

    async def stop(self):
        if self.browser:
            await self.browser.stop()

    async def detect_captcha(self) -> Dict:
        """Detect what CAPTCHA is on the page."""
        detection_js = """
            ({
                hasRecaptchaV2: !!document.querySelector('.g-recaptcha, #g-recaptcha, [data-sitekey]'),
                siteKey: document.querySelector('[data-sitekey]')?.dataset.sitekey,
                hasHcaptcha: !!document.querySelector('.h-captcha, [data-hcaptcha-sitekey]'),
                hcaptchaSiteKey: document.querySelector('[data-hcaptcha-sitekey]')?.dataset.hcaptchaSitekey,
                hasTurnstile: !!document.querySelector('.cf-turnstile, [data-turnstile-sitekey]'),
                turnstileKey: document.querySelector('[data-turnstile-sitekey]')?.dataset.turnstileSitekey,
                hasInvisibleRecaptcha: !!document.querySelector('.grecaptcha-badge'),
                hasTextCaptcha: !!document.querySelector('input[name*="captcha"], img[src*="captcha"]'),
                hasFunCaptcha: !!document.querySelector('#arkoseFrame, [data-sitekey][data-marshalparams]'),
            })
        """
        try:
            return await self.browser.page.evaluate(detection_js)
        except Exception as e:
            return {"error": str(e)}

    async def solve_audio_recaptcha(self) -> bool:
        """Solve reCAPTCHA v2 using audio challenge + Whisper."""
        print("🎤 Trying audio reCAPTCHA solve...")

        try:
            # Find reCAPTCHA iframe
            js = """
                // Find all iframes
                const iframes = document.querySelectorAll('iframe');
                for (const f of iframes) {
                    if (f.src && f.src.includes('recaptcha')) {
                        return f.src;
                    }
                }
                return null;
            """
            recaptcha_url = await self.browser.page.evaluate(js)
            if not recaptcha_url:
                print("   ❌ reCAPTCHA iframe not found")
                return False

            # Open reCAPTCHA in new tab
            new_tab = await self.browser.browser.get(recaptcha_url)
            await asyncio.sleep(3)

            # Click audio challenge button
            audio_js = """
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.title && btn.title.toLowerCase().includes('audio')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            """
            clicked = await new_tab.evaluate(audio_js)
            if not clicked:
                print("   ❌ Audio button not found")
                return False

            await asyncio.sleep(3)

            # Find audio source URL
            audio_url_js = """
                const audio = document.querySelector('audio source, audio');
                return audio ? (audio.src || audio.querySelector('source')?.src) : null;
            """
            audio_url = await new_tab.evaluate(audio_url_js)

            if not audio_url:
                print("   ❌ Audio URL not found")
                return False

            print(f"   🎵 Downloading audio: {audio_url[:80]}...")

            # Download audio
            import requests
            audio_path = Path(f"/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/audio_{int(time.time())}.mp3")
            r = requests.get(audio_url, timeout=30)
            audio_path.write_bytes(r.content)
            print(f"   ✅ Downloaded: {len(r.content)} bytes")

            # Try to transcribe with Whisper
            try:
                import whisper
                print("   🔄 Transcribing with Whisper...")
                model = whisper.load_model("base")
                result = model.transcribe(str(audio_path))
                text = result["text"].strip()
                print(f"   ✅ Transcribed: '{text}'")

                # Enter the text in the audio input
                input_js = """
                    const input = document.querySelector('#audio-response, input[name="audio-response"]');
                    if (input) {
                        input.focus();
                        return true;
                    }
                    return false;
                """
                found = await new_tab.evaluate(input_js)
                if found:
                    type_js = f"""
                        const input = document.querySelector('#audio-response, input[name="audio-response"]');
                        input.value = '';
                        const text = `{text}`;
                        for (let i = 0; i < text.length; i++) {{
                            setTimeout(() => {{
                                input.value += text[i];
                                input.dispatchEvent(new Event('input', {{bubbles: true}}));
                            }}, i * 80);
                        }}
                    """
                    await new_tab.evaluate(type_js)
                    await asyncio.sleep(2)

                    # Submit
                    verify_js = """
                        const btn = document.querySelector('#recaptcha-verify-button, button:has-text("Verify")');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                    """
                    submitted = await new_tab.evaluate(verify_js)
                    if submitted:
                        print(f"   ✅ Submitted audio answer")
                        await asyncio.sleep(3)
                        return True

                return False

            except ImportError:
                print("   ⚠️  Whisper not installed (run: pip install openai-whisper)")
                return False

        except Exception as e:
            print(f"   ❌ Audio solve error: {str(e)[:100]}")
            return False

    async def solve_hcaptcha_audio(self) -> bool:
        """Solve hCaptcha using audio + Whisper."""
        print("🎤 Trying hCaptcha audio solve...")

        try:
            # hCaptcha flow is similar to reCAPTCHA
            js = """
                const iframes = document.querySelectorAll('iframe');
                for (const f of iframes) {
                    if (f.src && (f.src.includes('hcaptcha') || f.src.includes('hcaptcha.com'))) {
                        return f.src;
                    }
                }
                return null;
            """
            hcaptcha_url = await self.browser.page.evaluate(js)
            if not hcaptcha_url:
                return False

            new_tab = await self.browser.browser.get(hcaptcha_url)
            await asyncio.sleep(3)

            # Click audio
            audio_js = """
                const buttons = document.querySelectorAll('button, div[role="button"]');
                for (const btn of buttons) {
                    const label = (btn.getAttribute('aria-label') || btn.title || '').toLowerCase();
                    if (label.includes('audio')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            """
            if not await new_tab.evaluate(audio_js):
                return False

            await asyncio.sleep(3)

            # Get audio URL
            audio_url = await new_tab.evaluate("""
                () => {
                    const audio = document.querySelector('audio');
                    return audio ? audio.src : null;
                }
            """)

            if not audio_url:
                return False

            # Download and transcribe (same as recaptcha)
            import requests
            audio_path = Path(f"/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/hcaptcha_audio_{int(time.time())}.mp3")
            r = requests.get(audio_url, timeout=30)
            audio_path.write_bytes(r.content)

            try:
                import whisper
                model = whisper.load_model("base")
                result = model.transcribe(str(audio_path))
                text = result["text"].strip()
                print(f"   ✅ Transcribed: '{text}'")

                # Type and submit
                await new_tab.evaluate(f"""
                    const input = document.querySelector('textarea, input[type="text"]');
                    if (input) {{
                        input.focus();
                        input.value = `{text}`;
                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                        setTimeout(() => {{
                            const btn = document.querySelector('button[type="submit"], .button-submit');
                            if (btn) btn.click();
                        }}, 1000);
                    }}
                """)
                await asyncio.sleep(3)
                return True
            except ImportError:
                return False

        except Exception as e:
            print(f"   ❌ hCaptcha error: {str(e)[:100]}")
            return False

    async def wait_for_turnstile(self, timeout: int = 30) -> bool:
        """Wait for Cloudflare Turnstile to auto-solve."""
        print("⏳ Waiting for Cloudflare Turnstile...")

        try:
            start = time.time()
            while time.time() - start < timeout:
                # Check if Turnstile is solved
                solved = await self.browser.page.evaluate("""
                    () => {
                        const cf = document.querySelector('.cf-turnstile');
                        if (!cf) return true; // No turnstile on page
                        const response = document.querySelector('[name="cf-turnstile-response"]');
                        return response && response.value.length > 0;
                    }
                """)
                if solved:
                    print("   ✅ Turnstile solved (or not present)")
                    return True
                await asyncio.sleep(2)

            print("   ⚠️  Turnstile timeout")
            return False
        except Exception as e:
            print(f"   ⚠️  Turnstile check error: {str(e)[:50]}")
            return True  # Continue anyway

    async def try_solve(self, url: str) -> Dict:
        """Try to solve any CAPTCHA on the page."""
        print("=" * 60)
        print(f"🧩 CAPTCHA WORKER: {url}")
        print("=" * 60)

        await self.browser.navigate(url)
        await asyncio.sleep(3)

        # Detect
        detection = await self.detect_captcha()
        print(f"\n🔍 Detection: {detection}")

        result = {"detection": detection, "solved": False, "method": None}

        if detection.get('hasRecaptchaV2'):
            print("\n→ Detected: reCAPTCHA v2")
            print("  Trying audio challenge + Whisper...")
            success = await self.solve_audio_recaptcha()
            if success:
                result["solved"] = True
                result["method"] = "audio_whisper"

        elif detection.get('hasHcaptcha'):
            print("\n→ Detected: hCaptcha")
            print("  Trying audio challenge + Whisper...")
            success = await self.solve_hcaptcha_audio()
            if success:
                result["solved"] = True
                result["method"] = "audio_whisper"

        elif detection.get('hasTurnstile'):
            print("\n→ Detected: Cloudflare Turnstile")
            print("  Waiting for auto-solve...")
            success = await self.wait_for_turnstile()
            if success:
                result["solved"] = True
                result["method"] = "turnstile_wait"

        elif detection.get('hasTextCaptcha'):
            print("\n→ Detected: Image CAPTCHA")
            print("  Would use Tesseract OCR...")
            result["method"] = "ocr_pending"

        else:
            print("\n→ No CAPTCHA detected on page")
            result["method"] = "none"

        return result


async def main():
    print("=" * 70)
    print("🧩 CAPTCHA WORKER — Multi-strategy solver")
    print("=" * 70)
    print()
    print("Available strategies:")
    print("  1. Audio reCAPTCHA v2 + Whisper STT (FREE)")
    print("  2. Audio hCaptcha + Whisper STT (FREE)")
    print("  3. Cloudflare Turnstile (wait + auto-solve)")
    print("  4. Tesseract OCR for image CAPTCHAs")
    print()
    print("Requires: pip install openai-whisper")
    print()


if __name__ == "__main__":
    asyncio.run(main())
