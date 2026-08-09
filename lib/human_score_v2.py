"""Human Score Test v2 — uses nodriver + Tor for max stealth."""
import asyncio
import json
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib')
from nodriver_automation import NodriverAutomation, STEALTH_INIT


DETECTION_SITES = [
    ("Sannysoft", "https://bot.sannysoft.com/"),
    ("CreepJS", "https://abrahamjuliot.github.io/creepjs/"),
    ("BrowserLeaks Canvas", "https://browserleaks.com/canvas"),
    ("BrowserLeaks WebGL", "https://browserleaks.com/webgl"),
    ("BrowserLeaks JS", "https://browserleaks.com/javascript"),
    ("Pixelscan", "https://pixelscan.net/"),
]


async def test_all():
    print("=" * 70)
    print("🥷 NODRIVER + TOR — Full Human Score Test")
    print("=" * 70)
    
    client = NodriverAutomation(use_tor=True)
    await client.start()
    
    total_score = 0
    results = []
    
    for name, url in DETECTION_SITES:
        print(f"\n🔍 {name}...")
        try:
            state = await client.navigate(url)
            await asyncio.sleep(4)
            
            body = await client.page.evaluate("document.body.innerText")
            content_len = len(body) if body else 0
            
            # Get detection data
            test_data = await client.page.evaluate("""
                ({
                    webdriver: navigator.webdriver,
                    plugins: navigator.plugins.length,
                    languages: navigator.languages,
                    hardwareConcurrency: navigator.hardwareConcurrency,
                    deviceMemory: navigator.deviceMemory,
                    hasChrome: typeof window.chrome,
                    hasChromeRuntime: typeof (window.chrome && window.chrome.runtime),
                    hasChromeApp: typeof (window.chrome && window.chrome.app),
                })
            """)
            
            failed = body.lower().count("failed") if body else 0
            passed = body.lower().count("passed") if body else 0
            
            # Score
            score = 100
            issues = []
            
            if test_data.get('webdriver') is not None and test_data.get('webdriver') != False:
                score -= 20
                issues.append(f"webdriver detected")
            
            if test_data.get('plugins', 0) < 3:
                score -= 15
                issues.append(f"only {test_data.get('plugins')} plugins")
            
            if test_data.get('hasChrome') != 'object':
                score -= 10
                issues.append("chrome object missing")
            
            if test_data.get('hasChromeRuntime') != 'object':
                score -= 5
                issues.append("chrome.runtime missing")
            
            score -= min(40, failed * 10)  # Each failed test costs 10 points
            
            if failed == 0 and passed > 0:
                print(f"   ✅ {passed} passed, {failed} failed — Score: {score}%")
            elif content_len > 1000:
                print(f"   ⚠️  Content OK ({content_len} bytes), {passed} passed, {failed} failed — Score: {score}%")
            else:
                print(f"   ❌ Blocked (content: {content_len} bytes) — Score: {score}%")
            
            if issues:
                for issue in issues:
                    print(f"      - {issue}")
            
            total_score += score
            results.append({
                "name": name,
                "score": score,
                "passed": passed,
                "failed": failed,
                "content_length": content_len,
            })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            results.append({"name": name, "score": 0, "error": str(e)[:100]})
    
    await client.stop()
    
    # Summary
    avg = total_score / len(DETECTION_SITES)
    print(f"\n{'='*70}")
    print(f"📊 FINAL SCORE: {avg:.1f}%")
    print(f"{'='*70}")
    
    if avg >= 90:
        print("🎉 EXCELLENT — Indistinguishable from human!")
    elif avg >= 75:
        print("✅ GOOD — Most detection bypassed")
    elif avg >= 50:
        print("⚠️  MODERATE — Some sites may block")
    else:
        print("❌ POOR — Many detections trigger")
    
    return avg


if __name__ == "__main__":
    asyncio.run(test_all())
