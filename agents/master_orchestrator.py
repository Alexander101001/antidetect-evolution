"""
🎼 MASTER ORCHESTRATOR
Coordinates all agents to maximize revenue.
"""
import asyncio
import json
import time
import logging
from pathlib import Path
import sys

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from base_agent import AgentOrchestrator
from tool_agent import ToolGeneratorAgent
from seo_agent import SEOOptimizerAgent
from analytics_agent import AnalyticsAgent
from ad_manager_agent import AdManagerAgent
from github_agent import GitHubAgent
from content_agent import ContentWriterAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')
log = logging.getLogger("orchestrator")


class MasterOrchestrator:
    """
    Master orchestrator that runs all agents in coordinated cycles.
    """
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self._register_agents()
        self.cycle_count = 0
        self.total_revenue = 0
    
    def _register_agents(self):
        """Register all agents."""
        self.orchestrator.register(ToolGeneratorAgent())
        self.orchestrator.register(SEOOptimizerAgent())
        self.orchestrator.register(AnalyticsAgent())
        self.orchestrator.register(AdManagerAgent())
        self.orchestrator.register(GitHubAgent())
        self.orchestrator.register(ContentWriterAgent())
    
    async def run_revenue_cycle(self):
        """Run one full revenue-maximizing cycle."""
        self.cycle_count += 1
        log.info(f"\n{'='*60}\n🔄 CYCLE {self.cycle_count}\n{'='*60}")
        
        workflow = [
            # Step 1: Parallel - Generate new tools + write content
            [
                ("tool_generator", {"slug": f"ai-tool-{self.cycle_count}", "title": "AI Smart Tool", "description": "Powered by AI"}),
                ("content_writer", {"action": "write_blog", "topic": random.choice(["productivity", "developer tools", "calculators"])}),
            ],
            # Step 2: Optimize all tools (parallel)
            [
                ("seo_optimizer", {"tool_path": str(f)}) for f in Path("../empire/tools").glob("*.html")
            ][:5],  # Limit to 5 per cycle
            # Step 3: Add ads (parallel)
            [
                ("ad_manager", {"tool_path": str(f), "platforms": ["adsense", "ezoic", "propellerads"]}) 
                for f in Path("../empire/tools").glob("*.html")
            ][:5],
            # Step 4: Track analytics
            ("analytics", {"action": "report"}),
        ]
        
        results = await self.orchestrator.run_workflow(workflow)
        
        # Print summary
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        log.info(f"✅ Cycle {self.cycle_count} complete: {successful}/{len(results)} tasks successful")
        
        return results
    
    async def run_forever(self):
        """Run cycles forever (or until interrupted)."""
        log.info("🚀 Starting autonomous empire orchestrator")
        log.info("📊 Registered agents:")
        for name, agent in self.orchestrator.agents.items():
            log.info(f"   • {name}: {agent.role}")
        
        while True:
            try:
                await self.run_revenue_cycle()
                
                # Wait 3 hours between cycles (with variance)
                import random
                wait = random.uniform(10800, 14400)  # 3-4 hours
                log.info(f"⏸️  Next cycle in {wait/3600:.1f} hours")
                await asyncio.sleep(wait)
            
            except KeyboardInterrupt:
                log.info("⛔ Stopped by user")
                break
            except Exception as e:
                log.error(f"💥 Error: {e}")
                await asyncio.sleep(60)


if __name__ == "__main__":
    orchestrator = MasterOrchestrator()
    asyncio.run(orchestrator.run_forever())
