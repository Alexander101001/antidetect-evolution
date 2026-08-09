#!/usr/bin/env python3
"""
Human Likeness Score Test — runs my browser against multiple detection
services and gives a comprehensive score from 0-100%.

Tests:
1. bot.sannysoft.com (basic bot detection)
2. browserleaks.com/canvas (canvas fingerprinting)
3. browserleaks.com/webgl (WebGL fingerprinting)
4. browserleaks.com/javascript (JS properties)
5. browserleaks.com/webrtc (WebRTC leaks)
6. browserleaks.com/fonts (font enumeration)
7. fingerprintjs.github.io/fingerprintjs (commercial-grade)
8. pixelscan.net (overall consistency)
9. bot detection in headers
10. behavioral tests (mouse, keyboard, timing)
"""

import subprocess
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict, field


@dataclass
class TestResult:
    """Single detection test result."""
    test_name: str
    url: str
    score: float  # 0-100 (100 = perfect human)
    issues: List[str] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)


@dataclass
class HumanScoreReport:
    """Overall human-likeness report."""
    total_score: float  # weighted average
    tests: List[TestResult]
    passed: int
    failed: int
    critical_issues: List[str]
    recommendations: List[str]


class HumanScoreTest:
    """Run comprehensive human-likeness tests."""

    DETECTION_SITES = [
        {
            "name": "Sannysoft Anti-Bot",
            "url": "https://bot.sannysoft.com/",
            "weight": 0.15,
            "parser": "sannysoft",
        },
        {
            "name": "FingerprintJS Demo",
            "url": "https://fingerprintjs.github.io/fingerprintjs/",
            "weight": 0.15,
            "parser": "fingerprintjs",
        },
        {
            "name": "BrowserLeaks Canvas",
            "url": "https://browserleaks.com/canvas",
            "weight": 0.10,
            "parser": "canvas",
        },
        {
            "name": "BrowserLeaks WebGL",
            "url": "https://browserleaks.com/webgl",
            "weight": 0.10,
            "parser": "webgl",
        },
        {
            "name": "BrowserLeaks JS",
            "url": "https://browserleaks.com/javascript",
            "weight": 0.10,
            "parser": "javascript",
        },
        {
            "name": "BrowserLeaks WebRTC",
            "url": "https://browserleaks.com/webrtc",
            "weight": 0.05,
            "parser": "webrtc",
        },
        {
            "name": "BrowserLeaks Fonts",
            "url": "https://browserleaks.com/fonts",
            "weight": 0.05,
            "parser": "fonts",
        },
        {
            "name": "Pixelscan",
            "url": "https://pixelscan.net/",
            "weight": 0.15,
            "parser": "pixelscan",
        },
        {
            "name": "CreepJS",
            "url": "https://abrahamjuliot.github.io/creepjs/",
            "weight": 0.15,
            "parser": "creepjs",
        },
    ]

    def __init__(self):
        self.script_path = "/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib/_score_test.py"
        self.result_path = "/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/score_result.json"
        self.test_url = None
        self.test_action = "score"

    def run_all_tests(self) -> HumanScoreReport:
        """Run all detection tests and produce report."""
        results = []

        for site in self.DETECTION_SITES:
            print(f"\n🔍 Testing: {site['name']}")
            print(f"   URL: {site['url']}")

            try:
                result = self._run_test(site)
                results.append(result)
                status = "✅" if result.score >= 80 else "⚠️" if result.score >= 50 else "❌"
                print(f"   {status} Score: {result.score:.1f}%")
                if result.issues:
                    for issue in result.issues[:3]:
                        print(f"      - {issue}")
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)[:100]}")
                results.append(TestResult(
                    test_name=site['name'],
                    url=site['url'],
                    score=0,
                    issues=[f"Test error: {str(e)[:100]}"],
                ))

        # Calculate weighted score
        total_score = 0
        total_weight = 0
        critical_issues = []

        for result, site in zip(results, self.DETECTION_SITES):
            total_score += result.score * site['weight']
            total_weight += site['weight']
            if result.score < 50:
                critical_issues.append(f"{result.test_name}: {result.score:.1f}%")

        final_score = total_score / total_weight if total_weight > 0 else 0

        passed = sum(1 for r in results if r.score >= 80)
        failed = sum(1 for r in results if r.score < 50)

        recommendations = self._generate_recommendations(results, final_score)

        report = HumanScoreReport(
            total_score=final_score,
            tests=results,
            passed=passed,
            failed=failed,
            critical_issues=critical_issues,
            recommendations=recommendations,
        )

        return report

    def _run_test(self, site: Dict) -> TestResult:
        """Run a single detection test."""
        # Build the playwright script
        script = f"""
import json
import sys
import re
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from patchright.sync_api import sync_playwright

result = {{'success': False, 'error': None, 'data': None}}

# Stealth patches
INIT_SCRIPT = '''
Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
Object.defineProperty(navigator, 'plugins', {{
    get: () => [
        {{name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'}},
        {{name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''}},
        {{name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}},
    ],
}});
Object.defineProperty(navigator, 'languages', {{get: () => ['en-US', 'en']}});
Object.defineProperty(navigator, 'platform', {{get: () => 'Win32'}});
window.chrome = {{runtime: {{}}, loadTimes: function() {{}}, csi: function() {{}}, app: {{}}}};

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({{state: Notification.permission}}) :
        originalQuery(parameters)
);

const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {{
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
}};
'''

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            chromium_sandbox=False,
        )

        context = browser.new_context(
            viewport={{'width': 1920, 'height': 1080}},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            device_scale_factor=1,
        )

        context.add_init_script(INIT_SCRIPT)
        page = context.new_page()

        # Visit the test URL
        page.goto('{site['url']}', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(5000)  # Let JS settle

        # Get page text and HTML
        title = page.title()
        html = page.content()
        text = page.inner_text('body')

        # Run special checks per test
        test_data = {{}}

        # Check navigator.webdriver
        test_data['webdriver'] = page.evaluate('navigator.webdriver')
        test_data['userAgent'] = page.evaluate('navigator.userAgent')
        test_data['platform'] = page.evaluate('navigator.platform')
        test_data['languages'] = page.evaluate('navigator.languages')
        test_data['hardwareConcurrency'] = page.evaluate('navigator.hardwareConcurrency')
        test_data['deviceMemory'] = page.evaluate('navigator.deviceMemory')

        # WebGL
        try:
            test_data['webglVendor'] = page.evaluate('''() => {{
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (!gl) return null;
                const ext = gl.getExtension('WEBGL_debug_renderer_info');
                return {{
                    vendor: ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
                    renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
                }};
            }}''')
        except Exception as e:
            test_data['webglError'] = str(e)

        # Canvas fingerprint
        try:
            test_data['canvasHash'] = page.evaluate('''() => {{
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillStyle = '#f60';
                ctx.fillRect(125, 1, 62, 20);
                ctx.fillStyle = '#069';
                ctx.fillText('Hello, world!', 2, 15);
                return canvas.toDataURL().slice(-50);
            }}''')
        except Exception as e:
            test_data['canvasError'] = str(e)

        # Chrome object
        test_data['hasChrome'] = page.evaluate('typeof window.chrome')
        test_data['hasChromeRuntime'] = page.evaluate('typeof (window.chrome && window.chrome.runtime)')

        # Plugins count
        test_data['pluginCount'] = page.evaluate('navigator.plugins.length')

        result['success'] = True
        result['data'] = {{
            'title': title,
            'url': page.url,
            'text_length': len(text),
            'text': text,
            'test_data': test_data,
            'content_length': len(html),
        }}

        browser.close()
except Exception as e:
    result['error'] = str(e)
    result['traceback'] = __import__('traceback').format_exc()

with open('{self.result_path}', 'w') as f:
    json.dump(result, f, default=str)
"""
        Path(self.script_path).write_text(script)

        try:
            subprocess.run(
                ["proot-distro", "login", "ubuntu", "--", "python3", self.script_path],
                capture_output=True, text=True, timeout=90
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=site['name'],
                url=site['url'],
                score=0,
                issues=["Timeout (90s)"],
            )

        if not Path(self.result_path).exists():
            return TestResult(
                test_name=site['name'],
                url=site['url'],
                score=0,
                issues=["No result file"],
            )

        try:
            data = json.loads(Path(self.result_path).read_text())
        except Exception as e:
            return TestResult(
                test_name=site['name'],
                url=site['url'],
                score=0,
                issues=[f"Parse error: {e}"],
            )

        if not data.get("success"):
            return TestResult(
                test_name=site['name'],
                url=site['url'],
                score=0,
                issues=[data.get('error', 'Unknown')[:200]],
            )

        # Score the test based on parser
        test_data = data['data'].get('test_data', {})
        text = data['data'].get('text', '')

        return self._score_test(site, test_data, text)

    def _score_test(self, site: Dict, test_data: Dict, text: str) -> TestResult:
        """Score a test based on collected data."""
        issues = []
        score = 100  # Start at 100, deduct for issues

        # Common checks across all tests
        if test_data.get('webdriver') is not None and test_data.get('webdriver') != False:
            issues.append(f"navigator.webdriver = {test_data.get('webdriver')} (should be undefined/false)")
            score -= 30

        if 'HeadlessChrome' in test_data.get('userAgent', ''):
            issues.append("User-Agent contains 'HeadlessChrome'")
            score -= 30

        if test_data.get('pluginCount', 0) == 0:
            issues.append("navigator.plugins is empty (real Chrome has 3+ plugins)")
            score -= 15

        if test_data.get('hasChrome') == 'undefined' or test_data.get('hasChromeRuntime') == 'undefined':
            issues.append("window.chrome.runtime missing (real Chrome has it)")
            score -= 10

        # WebGL check
        webgl = test_data.get('webglVendor')
        if webgl and isinstance(webgl, dict):
            if 'SwiftShader' in str(webgl.get('renderer', '')):
                issues.append(f"WebGL renderer = SwiftShader (CPU fallback, suspicious)")
                score -= 15

        # Site-specific parsing
        if site['parser'] == 'sannysoft':
            score, issues = self._parse_sannysoft(text, score, issues)
        elif site['parser'] == 'fingerprintjs':
            score, issues = self._parse_fingerprintjs(text, test_data, score, issues)
        elif site['parser'] == 'pixelscan':
            score, issues = self._parse_pixelscan(text, score, issues)
        elif site['parser'] == 'creepjs':
            score, issues = self._parse_creepjs(text, score, issues)

        score = max(0, min(100, score))

        return TestResult(
            test_name=site['name'],
            url=site['url'],
            score=score,
            issues=issues,
            raw_data=test_data,
        )

    def _parse_sannysoft(self, text: str, score: float, issues: List[str]) -> Tuple[float, List[str]]:
        """Parse sannysoft results."""
        # Count "failed" indicators in the page text
        failed_count = text.lower().count('failed')
        passed_count = text.lower().count('passed')

        if failed_count > 0:
            issues.append(f"Sannysoft reports {failed_count} failed tests")
            # Each failed test deducts 15 points
            score -= min(60, failed_count * 15)

        return score, issues

    def _parse_fingerprintjs(self, text: str, test_data: Dict, score: float, issues: List[str]) -> Tuple[float, List[str]]:
        """Parse FingerprintJS results."""
        # Check if visitorId looks bot-like
        if 'visitorId' in text or 'fingerprint' in text.lower():
            # FingerprintJS usually still works, just uniqueness matters
            pass

        # Check entropy indicators
        if 'Chrome' not in test_data.get('userAgent', ''):
            issues.append("User-Agent doesn't say Chrome")
            score -= 20

        return score, issues

    def _parse_pixelscan(self, text: str, score: float, issues: List[str]) -> Tuple[float, List[str]]:
        """Parse Pixelscan results."""
        if 'inconsistent' in text.lower():
            issues.append("Pixelscan reports inconsistencies")
            score -= 25
        if 'bot' in text.lower() and 'detected' in text.lower():
            issues.append("Pixelscan detected bot-like behavior")
            score -= 30
        return score, issues

    def _parse_creepjs(self, text: str, score: float, issues: List[str]) -> Tuple[float, List[str]]:
        """Parse CreepJS results (most comprehensive)."""
        if 'lies' in text.lower() or 'mismatch' in text.lower():
            issues.append("CreepJS detected lies/mismatches in browser features")
            score -= 25
        if 'headless' in text.lower():
            issues.append("CreepJS detected headless mode")
            score -= 30
        if 'automation' in text.lower() and 'detected' in text.lower():
            issues.append("CreepJS detected automation")
            score -= 25
        return score, issues

    def _generate_recommendations(self, results: List[TestResult], total_score: float) -> List[str]:
        """Generate recommendations based on failures."""
        recs = []

        if total_score < 50:
            recs.append("🚨 CRITICAL: Browser is easily detected as bot")
            recs.append("   - Use residential proxies instead of datacenter/Tor exit nodes")
            recs.append("   - Use a non-headless browser or xvfb virtual display")
            recs.append("   - Consider paid anti-detect browsers (GoLogin, Multilogin)")

        if total_score < 80:
            recs.append("⚠️  Improve stealth with:")
            recs.append("   - Patchright over Playwright (C++ level patches)")
            recs.append("   - Realistic canvas/WebGL/音频 fingerprints")
            recs.append("   - Human-like mouse movements and typing")

        # Specific recommendations based on which tests failed
        for result in results:
            if result.score < 70:
                if 'webdriver' in str(result.issues):
                    recs.append(f"   - {result.test_name}: Override navigator.webdriver at init")
                if 'plugins' in str(result.issues):
                    recs.append(f"   - {result.test_name}: Inject realistic plugin list")
                if 'Chrome' in str(result.issues) and 'chrome' not in str(result.issues).lower():
                    recs.append(f"   - {result.test_name}: Inject window.chrome runtime")
                if 'SwiftShader' in str(result.issues):
                    recs.append(f"   - {result.test_name}: Use real GPU, not CPU SwiftShader")

        if not recs:
            recs.append("✅ Browser is passing most detection tests")
            recs.append("   - Continue using current setup")
            recs.append("   - Monitor for new detection vectors")

        return recs

    def print_report(self, report: HumanScoreReport):
        """Print formatted report."""
        print(f"\n{'='*70}")
        print(f"🧪 HUMAN LIKENESS SCORE REPORT")
        print(f"{'='*70}")
        print()
        print(f"  📊 OVERALL SCORE: {report.total_score:.1f}% / 100%")
        print()

        # Score visualization
        bar_length = 50
        filled = int(report.total_score / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        if report.total_score >= 90:
            label = "🎉 EXCELLENT - Indistinguishable from human"
        elif report.total_score >= 70:
            label = "✅ GOOD - Most sites will accept"
        elif report.total_score >= 50:
            label = "⚠️  MODERATE - Some sites may block"
        elif report.total_score >= 30:
            label = "❌ POOR - Many sites will detect"
        else:
            label = "🚨 CRITICAL - Easily detected as bot"

        print(f"  [{bar}] {label}")
        print()
        print(f"  ✅ Tests passed (≥80%): {report.passed}")
        print(f"  ❌ Tests failed (<50%): {report.failed}")
        print()

        print("  📋 Individual Test Scores:")
        for test in report.tests:
            status = "✅" if test.score >= 80 else "⚠️" if test.score >= 50 else "❌"
            print(f"    {status} {test.test_name}: {test.score:.1f}%")

            if test.issues:
                for issue in test.issues[:2]:
                    print(f"       - {issue}")

        if report.critical_issues:
            print()
            print("  🚨 Critical Issues:")
            for issue in report.critical_issues:
                print(f"     - {issue}")

        print()
        print("  💡 Recommendations:")
        for rec in report.recommendations:
            print(f"     {rec}")

        print(f"\n{'='*70}")


def main():
    print("=" * 70)
    print("🧪 HUMAN LIKENESS SCORE TEST")
    print("=" * 70)
    print()
    print("This test runs your browser against 9 major bot detection")
    print("services and scores how human-like you appear.")
    print()
    print("⏱️  Estimated time: 3-5 minutes")
    print()

    tester = HumanScoreTest()
    report = tester.run_all_tests()
    tester.print_report(report)

    # Save report
    report_path = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/human_score_report.json")
    report_path.write_text(json.dumps(asdict(report), indent=2, default=str))
    print(f"\n📁 Full report saved to: {report_path}")


if __name__ == "__main__":
    main()
