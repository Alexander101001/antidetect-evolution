
import json
import sys
import re
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from patchright.sync_api import sync_playwright

result = {'success': False, 'error': None, 'data': None}

# Stealth patches
INIT_SCRIPT = '''
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
        {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''},
    ],
});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);

const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
};
'''

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            chromium_sandbox=False,
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            device_scale_factor=1,
        )

        context.add_init_script(INIT_SCRIPT)
        page = context.new_page()

        # Visit the test URL
        page.goto('https://abrahamjuliot.github.io/creepjs/', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(5000)  # Let JS settle

        # Get page text and HTML
        title = page.title()
        html = page.content()
        text = page.inner_text('body')

        # Run special checks per test
        test_data = {}

        # Check navigator.webdriver
        test_data['webdriver'] = page.evaluate('navigator.webdriver')
        test_data['userAgent'] = page.evaluate('navigator.userAgent')
        test_data['platform'] = page.evaluate('navigator.platform')
        test_data['languages'] = page.evaluate('navigator.languages')
        test_data['hardwareConcurrency'] = page.evaluate('navigator.hardwareConcurrency')
        test_data['deviceMemory'] = page.evaluate('navigator.deviceMemory')

        # WebGL
        try:
            test_data['webglVendor'] = page.evaluate('''() => {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (!gl) return null;
                const ext = gl.getExtension('WEBGL_debug_renderer_info');
                return {
                    vendor: ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
                    renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
                };
            }''')
        except Exception as e:
            test_data['webglError'] = str(e)

        # Canvas fingerprint
        try:
            test_data['canvasHash'] = page.evaluate('''() => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillStyle = '#f60';
                ctx.fillRect(125, 1, 62, 20);
                ctx.fillStyle = '#069';
                ctx.fillText('Hello, world!', 2, 15);
                return canvas.toDataURL().slice(-50);
            }''')
        except Exception as e:
            test_data['canvasError'] = str(e)

        # Chrome object
        test_data['hasChrome'] = page.evaluate('typeof window.chrome')
        test_data['hasChromeRuntime'] = page.evaluate('typeof (window.chrome && window.chrome.runtime)')

        # Plugins count
        test_data['pluginCount'] = page.evaluate('navigator.plugins.length')

        result['success'] = True
        result['data'] = {
            'title': title,
            'url': page.url,
            'text_length': len(text),
            'text': text,
            'test_data': test_data,
            'content_length': len(html),
        }

        browser.close()
except Exception as e:
    result['error'] = str(e)
    result['traceback'] = __import__('traceback').format_exc()

with open('/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/score_result.json', 'w') as f:
    json.dump(result, f, default=str)
