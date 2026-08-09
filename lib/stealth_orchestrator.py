"""
🎼 STEALTH ORCHESTRATOR
Coordinates all workers with human-like timing.
"""
import asyncio
import logging
import json
import time
import random
from datetime import datetime
from stealth_worker import StealthWorker
from human_timing import schedule_next_action, format_delay

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

# List of accounts to manage
ACCOUNTS = [
    "mra494956@gmail.com",
    "hasanaliabdalgeny@gmail.com",
]

# List of platforms to register on (existing NOT touched)
PLATFORMS = [
    "vercel.com",
    "render.com",
    "railway.app",
    "fly.io",
    "heroku.com",
    "netlify.com",
    "supabase.com",
    "planetscale.com",
    "neon.tech",
    "convex.dev",
]


async def stealth_main():
    """Main loop with variable timing."""
    log = logging.getLogger("stealth")
    log.info("🥷 STEALTH ORCHESTRATOR STARTED")
    
    workers = {}
    for account in ACCOUNTS:
        workers[account] = StealthWorker(account_id=account, mode="safe")
    
    cycle = 0
    while True:
        cycle += 1
        log.info(f"\n{'='*60}")
        log.info(f"🔄 Cycle {cycle}")
        log.info(f"{'='*60}")
        
        for account, worker in workers.items():
            try:
                # Get stats
                stats = worker.get_stats()
                log.info(f"📊 [{account}] {stats}")
                
                # Wait for next action (variable time)
                worker.wait_for_next_action()
                
                # Pick random platform
                platform = random.choice(PLATFORMS)
                log.info(f"🌐 Registering on {platform}...")
                
                # Simulate work
                success = random.random() > 0.15
                worker.report_action(success=success)
                
                if success:
                    log.info(f"✅ Success: {platform}")
                else:
                    log.warning(f"❌ Failed: {platform}")
                    if random.random() < 0.1:
                        # Occasionally rate limited
                        worker.report_rate_limit()
                        next_t, mins = schedule_next_action()
                        log.info(f"⏰ Next action in {mins:.1f} minutes")
                
            except Exception as e:
                log.error(f"💥 Error: {e}")
                # Variable backoff
                delay = random.uniform(60, 600)
                time.sleep(delay)
        
        # Inter-cycle delay (variable)
        delay = random.uniform(300, 1800)  # 5-30 minutes
        log.info(f"\n⏸️  Cycle complete. Next cycle in {format_delay(delay)}")
        time.sleep(delay)


if __name__ == "__main__":
    asyncio.run(stealth_main())
