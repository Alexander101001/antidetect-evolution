
import json
import sys
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from patchright.sync_api import sync_playwright

result = {'success': False, 'error': None, 'data': None}

# JavaScript to inject BEFORE page load - hides all bot signals
INIT_SCRIPT = '''
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
        {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''},
    ],
});

Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

Object.defineProperty(navigator, 'platform', {
    get: () => 'Win32'
});

window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {isInstalled: false}
};

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
        # Patchright's launch has stealth built in
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
            ],
            chromium_sandbox=False,
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            color_scheme='light',
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            extra_http_headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '" + platform + "',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
        )

        # Inject stealth BEFORE any page loads
        context.add_init_script(INIT_SCRIPT)

        page = context.new_page()

        # Navigate
        page.goto('https://github.com/signup', wait_until='domcontentloaded', timeout=60000)

        # Wait for JS to settle
        page.wait_for_timeout(3000)

        # Get content
        title = page.title()
        content = page.content()
        body_text = page.inner_text('body')

        result['success'] = True
        result['data'] = {
            'url': page.url,
            'title': title,
            'content_length': len(content),
            'text_length': len(body_text),
            'text_preview': body_text[:500] if body_text else '',
            'cookies': [{'name': c['name'], 'value': c['value'], 'domain': c['domain']} for c in context.cookies()],
        }

        browser.close()
except Exception as e:
    result['error'] = str(e)
    import traceback
    result['traceback'] = traceback.format_exc()

with open('/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/patchright_result.json', 'w') as f:
    json.dump(result, f, default=str)
