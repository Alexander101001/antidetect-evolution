"""Human Score Test v3 — uses nodriver + Tor for max stealth."""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, '/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib')
from nodriver_automation import NodriverAutomation, STEALTH_INIT


DETECTION_SITES = [
    ("Sannysoft", "https://bot.sannysoft.com/"),
    ("CreepJS", "https://abrahamjuliot.github.io/creepjs/"),
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
            
            failed = body.lower().count("failed") if body else 0
            passed = body.lower().count("passed") if body else 0
            
            # Score based on detection page results
            score = 100
            issues = []
            
            if failed > 0:
                score -= min(50, failed * 15)
                issues.append(f"{failed} failed tests on {name}")
            
            if content_len < 1000:
                score -= 30
                issues.append(f"low content ({content_len} bytes)")
            
            if score >= 80:
                print(f"   ✅ {passed} passed, {failed} failed — Score: {score}%")
            elif content_len > 500:
                print(f"   ⚠️  {passed} passed, {failed} failed — Score: {score}%")
            else:
                print(f"   ❌ Blocked — Score: {score}%")
            
            if issues:
                for issue in issues:
                    print(f"      - {issue}")
            
            total_score += score
            results.append({"name": name, "score": score, "passed": passed, "failed": failed})
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")
            results.append({"name": name, "score": 0})
    
    await client.stop()
    
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
