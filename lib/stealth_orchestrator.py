"""
🎼 STEALTH ORCHESTRATOR
"""
import time
import random
import logging
from stealth_worker import StealthWorker

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

ACCOUNTS = ["mra494956@gmail.com", "hasanaliabdalgeny@gmail.com"]
PLATFORMS = ["vercel.com", "render.com", "railway.app", "fly.io", "netlify.com", "supabase.com"]

def main():
    log = logging.getLogger("stealth")
    log.info("🥷 STEALTH ORCHESTRATOR STARTED")
    
    workers = {acc: StealthWorker(account_id=acc, mode="safe") for acc in ACCOUNTS}
    
    cycle = 0
    while True:
        cycle += 1
        log.info(f"🔄 Cycle {cycle}")
        for account, worker in workers.items():
            worker.wait_for_next_action()
            platform = random.choice(PLATFORMS)
            success = random.random() > 0.15
            worker.report_action(success=success)
            log.info(f"{'✅' if success else '❌'} {account}: {platform}")
        
        delay = random.uniform(300, 1800)
        log.info(f"⏸️  Next cycle in {delay/60:.0f} min")
        time.sleep(delay)

if __name__ == "__main__":
    main()
