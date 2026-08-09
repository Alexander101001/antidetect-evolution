import asyncio
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/.pi/skills/antidetect-stack/lib')
from nodriver_automation import NodriverAutomation

async def main():
    client = NodriverAutomation(use_tor=True)
    await client.start()
    
    print("\n1️⃣  bot.sannysoft.com...")
    state = await client.navigate("https://bot.sannysoft.com/")
    print(f"   URL: {state['url']}")
    print(f"   webdriver: {state['webdriver']}")
    print(f"   Plugins: {state['plugins']}")
    print(f"   chrome: {state['has_chrome']}")
    
    body = await client.page.evaluate("document.body.innerText")
    failed = body.lower().count("failed")
    passed = body.lower().count("passed")
    print(f"   Sannysoft: {passed} passed, {failed} failed")
    
    print("\n2️⃣  CreepJS (comprehensive test)...")
    state = await client.navigate("https://abrahamjuliot.github.io/creepjs/")
    await asyncio.sleep(5)
    body = await client.page.evaluate("document.body.innerText")
    print(f"   Content length: {len(body)}")
    
    await client.stop()
    print("\n✅ Done")

asyncio.run(main())
