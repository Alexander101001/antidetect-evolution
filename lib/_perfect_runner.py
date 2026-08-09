
import json
import sys
sys.path.insert(0, '/usr/local/lib/python3.14/dist-packages')

from patchright.sync_api import sync_playwright

result = {'success': False, 'error': None, 'data': None}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process,AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=site-per-process',
                '--start-maximized',
            ],
            chromium_sandbox=False,
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            device_scale_factor=1,
            color_scheme='light',
            is_mobile=False,
            has_touch=False,
            extra_http_headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
        )

        # Inject stealth script BEFORE any page loads
        context.add_init_script("\n(function() {\n    'use strict';\n\n    // 1. Hide webdriver flag (most important)\n    Object.defineProperty(navigator, 'webdriver', {\n        get: () => undefined,\n        configurable: true\n    });\n\n    // 2. Real Chrome plugins (this was missing)\n    const realPlugins = [\n        {name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1},\n        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '', length: 1},\n        {name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: '', length: 1},\n        {name: 'Microsoft Edge PDF Viewer', filename: 'internal-pdf-viewer', description: '', length: 1},\n        {name: 'WebKit built-in PDF', filename: 'internal-pdf-viewer', description: '', length: 1},\n        {name: 'Native Client', filename: 'internal-nacl-plugin', description: '', length: 2},\n    ];\n\n    Object.defineProperty(navigator, 'plugins', {\n        get: () => {\n            const arr = realPlugins;\n            arr.item = function(i) { return this[i] || null; };\n            arr.namedItem = function(name) { return this.find(p => p.name === name) || null; };\n            arr.refresh = function() {};\n            return arr;\n        },\n        configurable: true\n    });\n\n    // 3. Real mimeTypes (paired with plugins)\n    const realMimeTypes = [\n        {type: 'application/pdf', suffixes: 'pdf', description: '', enabledPlugin: realPlugins[0]},\n        {type: 'text/pdf', suffixes: 'pdf', description: '', enabledPlugin: realPlugins[0]},\n    ];\n\n    Object.defineProperty(navigator, 'mimeTypes', {\n        get: () => {\n            const arr = realMimeTypes;\n            arr.item = function(i) { return this[i] || null; };\n            arr.namedItem = function(name) { return this.find(m => m.type === name) || null; };\n            return arr;\n        },\n        configurable: true\n    });\n\n    // 4. Languages\n    Object.defineProperty(navigator, 'languages', {\n        get: () => ['en-US', 'en'],\n        configurable: true\n    });\n\n    // 5. Platform\n    Object.defineProperty(navigator, 'platform', {\n        get: () => 'Win32',\n        configurable: true\n    });\n\n    // 6. Hardware concurrency (real Chrome reports actual cores)\n    Object.defineProperty(navigator, 'hardwareConcurrency', {\n        get: () => 8,\n        configurable: true\n    });\n\n    // 7. Device memory\n    Object.defineProperty(navigator, 'deviceMemory', {\n        get: () => 8,\n        configurable: true\n    });\n\n    // 8. Connection (real Chrome has this)\n    if (!navigator.connection) {\n        Object.defineProperty(navigator, 'connection', {\n            get: () => ({\n                effectiveType: '4g',\n                rtt: 50,\n                downlink: 10,\n                saveData: false,\n            }),\n            configurable: true\n        });\n    }\n\n    // 9. Chrome object with all expected methods\n    window.chrome = {\n        app: {\n            isInstalled: false,\n            InstallState: {DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed'},\n            RunningState: {CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running'},\n            getDetails: function() { return null; },\n            getIsInstalled: function() { return false; },\n            installState: function() { return 'not_installed'; },\n            runningState: function() { return 'cannot_run'; },\n        },\n        runtime: {\n            OnInstalledReason: {CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update'},\n            PlatformArch: {ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64'},\n            PlatformNaclArch: {ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64'},\n            PlatformOs: {ANDROID: 'android', CROS: 'cros', FUCHSIA: 'fuchsia', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win'},\n            RequestUpdateCheckStatus: {NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available'},\n            connect: function() {},\n            sendMessage: function() {},\n        },\n        loadTimes: function() {\n            return {\n                requestTime: Date.now() / 1000,\n                startLoadTime: Date.now() / 1000,\n                commitLoadTime: Date.now() / 1000,\n                finishDocumentLoadTime: Date.now() / 1000,\n                finishLoadTime: Date.now() / 1000,\n                firstPaintTime: Date.now() / 1000,\n                firstPaintAfterLoadTime: 0,\n                navigationType: 'Other',\n                wasFetchedViaSpdy: false,\n                wasNpnNegotiated: true,\n                npnNegotiatedProtocol: 'h2',\n                wasAlternateProtocolAvailable: false,\n                connectionInfo: 'h2',\n            };\n        },\n        csi: function() { return {startE: Date.now(), onloadT: Date.now()}; },\n        webstore: {},\n    };\n\n    // 10. Permissions API fix\n    const originalQuery = window.navigator.permissions.query;\n    window.navigator.permissions.query = function(parameters) {\n        if (parameters.name === 'notifications') {\n            return Promise.resolve({state: Notification.permission});\n        }\n        return originalQuery.call(this, parameters);\n    };\n\n    // 11. WebGL vendor/renderer (real Intel GPU, not SwiftShader)\n    const getParameter = WebGLRenderingContext.prototype.getParameter;\n    WebGLRenderingContext.prototype.getParameter = function(parameter) {\n        if (parameter === 37445) return 'Google Inc. (Intel)';  // UNMASKED_VENDOR_WEBGL\n        if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)';  // UNMASKED_RENDERER_WEBGL\n        return getParameter.call(this, parameter);\n    };\n\n    // Also patch WebGL2\n    if (typeof WebGL2RenderingContext !== 'undefined') {\n        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;\n        WebGL2RenderingContext.prototype.getParameter = function(parameter) {\n            if (parameter === 37445) return 'Google Inc. (Intel)';\n            if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)';\n            return getParameter2.call(this, parameter);\n        };\n    }\n\n    // 12. WebGL parameter extensions\n    const getExtension = WebGLRenderingContext.prototype.getExtension;\n    WebGLRenderingContext.prototype.getExtension = function(name) {\n        const ext = getExtension.call(this, name);\n        if (name === 'WEBGL_debug_renderer_info') {\n            // Patch the extension to return real values\n            if (ext) {\n                return new Proxy(ext, {\n                    get: function(target, prop) {\n                        if (prop === 'UNMASKED_VENDOR_WEBGL') return 37445;\n                        if (prop === 'UNMASKED_RENDERER_WEBGL') return 37446;\n                        return target[prop];\n                    }\n                });\n            }\n        }\n        return ext;\n    };\n\n    // 13. Notification permission (real browsers show 'default')\n    if (typeof Notification !== 'undefined') {\n        Object.defineProperty(Notification, 'permission', {\n            get: () => 'default',\n            configurable: true\n        });\n    }\n\n    // 14. PluginArray methods (needed for old API)\n    if (navigator.plugins) {\n        const origItem = navigator.plugins.item;\n        if (!origItem) {\n            navigator.plugins.item = function(i) { return this[i] || null; };\n        }\n        const origNamedItem = navigator.plugins.namedItem;\n        if (!origNamedItem) {\n            navigator.plugins.namedItem = function(name) {\n                return Array.from(this).find(p => p.name === name) || null;\n            };\n        }\n    }\n\n    // 15. WebRTC - prevent IP leaks (but make it look real)\n    const OriginalRTCPeerConnection = window.RTCPeerConnection;\n    window.RTCPeerConnection = function(...args) {\n        const pc = new OriginalRTCPeerConnection(...args);\n        const origCreateOffer = pc.createOffer.bind(pc);\n        pc.createOffer = async function(options) {\n            const offer = await origCreateOffer(options);\n            // Remove mDNS/candidate IP leakage but keep sdp\n            if (offer && offer.sdp) {\n                offer.sdp = offer.sdp.replace(/a=candidate:.+?typ.+?\\r\\n/g, '');\n            }\n            return offer;\n        };\n        return pc;\n    };\n\n    // 16. Battery API (some sites check this)\n    if (navigator.getBattery) {\n        const origGetBattery = navigator.getBattery.bind(navigator);\n        navigator.getBattery = async function() {\n            return {\n                charging: true,\n                chargingTime: 0,\n                dischargingTime: Infinity,\n                level: 0.87,\n                addEventListener: function() {},\n                removeEventListener: function() {},\n            };\n        };\n    }\n\n    // 17. Notification + Push APIs consistency\n    if (typeof PushManager === 'undefined') {\n        window.PushManager = function() {};\n    }\n\n    // 18. Permissions API (more comprehensive)\n    if (window.navigator.permissions && window.navigator.permissions.query) {\n        const origQuery2 = window.navigator.permissions.query;\n        window.navigator.permissions.query = function(params) {\n            return origQuery2.call(this, params).catch(() => {\n                return Promise.resolve({state: 'prompt', onchange: null});\n            });\n        };\n    }\n\n    // 19. Touch events (make it look like desktop)\n    window.ontouchstart = null;\n    window.ontouchend = null;\n    window.ontouchmove = null;\n\n    // 20. CDP / DevTools detection prevention\n    const elementDescriptor = Object.getOwnPropertyDescriptor(Element.prototype, 'innerText') || {};\n    Object.defineProperty(HTMLElement.prototype, 'innerText', {\n        get: function() {\n            return elementDescriptor.get ? elementDescriptor.get.call(this) : this.textContent;\n        }\n    });\n\n    console.log('[Stealth] All patches applied');\n})();\n")

        page = context.new_page()
        page.set_default_timeout(60000)

        page.goto('https://bot.sannysoft.com/', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(4000)

        title = page.title()
        html = page.content()
        text = page.inner_text('body')

        # Get all the detection indicators
        test_data = {}

        test_data['webdriver'] = page.evaluate('navigator.webdriver')
        test_data['userAgent'] = page.evaluate('navigator.userAgent')
        test_data['platform'] = page.evaluate('navigator.platform')
        test_data['languages'] = page.evaluate('navigator.languages')
        test_data['hardwareConcurrency'] = page.evaluate('navigator.hardwareConcurrency')
        test_data['deviceMemory'] = page.evaluate('navigator.deviceMemory')
        test_data['pluginCount'] = page.evaluate('navigator.plugins.length')
        test_data['pluginNames'] = page.evaluate('Array.from(navigator.plugins).map(p => p.name)')
        test_data['hasChrome'] = page.evaluate('typeof window.chrome')
        test_data['hasChromeRuntime'] = page.evaluate('typeof (window.chrome && window.chrome.runtime)')
        test_data['hasChromeLoadTimes'] = page.evaluate('typeof (window.chrome && window.chrome.loadTimes)')

        # WebGL
        try:
            test_data['webgl'] = page.evaluate('''() => {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                if (!gl) return null;
                const dbg = gl.getExtension('WEBGL_debug_renderer_info');
                return {
                    vendor: dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
                    renderer: dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
                };
            }''')
        except Exception as e:
            test_data['webglError'] = str(e)

        # Canvas
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
                ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
                ctx.fillText('Hello, world!', 4, 17);
                return canvas.toDataURL();
            }''')
        except Exception as e:
            test_data['canvasError'] = str(e)

        result['success'] = True
        result['data'] = {
            'url': page.url,
            'title': title,
            'content_length': len(html),
            'text_length': len(text),
            'text': text,
            'test_data': test_data,
        }

        browser.close()
except Exception as e:
    result['error'] = str(e)
    import traceback
    result['traceback'] = traceback.format_exc()

with open('/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/perfect_result.json', 'w') as f:
    json.dump(result, f, default=str)
