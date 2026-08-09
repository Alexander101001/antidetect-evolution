"""
🤖 BASE AI AGENT
Foundation for all sub-agents.
"""
import json
import time
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s'
)

class BaseAgent(ABC):
    """
    Abstract base for all AI agents.
    Each agent:
    - Has a specific role
    - Can communicate with other agents
    - Logs its actions
    - Persists state
    """
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(name)
        self.state_file = Path(f"state/{name}.json")
        self.state_file.parent.mkdir(exist_ok=True)
        self.state = self._load_state()
        self.created_at = time.time()
        self.actions_taken = 0
    
    def _load_state(self):
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        return {"status": "idle", "results": [], "errors": []}
    
    def _save_state(self):
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    @abstractmethod
    def execute(self, task: dict) -> dict:
        """Execute a task and return result."""
        pass
    
    def log_action(self, action: str, result: dict = None):
        """Log an action with timestamp."""
        self.actions_taken += 1
        entry = {
            "timestamp": time.time(),
            "action": action,
            "result": result
        }
        if "actions" not in self.state:
            self.state["actions"] = []
        self.state["actions"].append(entry)
        # Keep last 100 actions
        self.state["actions"] = self.state["actions"][-100:]
        self._save_state()
        self.logger.info(f"📝 {action}")
    
    def get_stats(self):
        return {
            "name": self.name,
            "role": self.role,
            "actions_taken": self.actions_taken,
            "uptime_hours": (time.time() - self.created_at) / 3600,
            "status": self.state.get("status", "idle")
        }


class AgentOrchestrator:
    """
    Orchestrates multiple agents working together.
    Like a manager coordinating workers.
    """
    
    def __init__(self):
        self.agents = {}
        self.message_queue = asyncio.Queue()
        self.results = {}
    
    def register(self, agent: BaseAgent):
        """Register an agent."""
        self.agents[agent.name] = agent
        print(f"✅ Registered: {agent.name} ({agent.role})")
    
    async def run_agent_task(self, agent_name: str, task: dict):
        """Run a task on a specific agent."""
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}
        
        agent = self.agents[agent_name]
        try:
            result = await asyncio.to_thread(agent.execute, task)
            agent.log_action(task.get("type", "unknown"), result)
            return result
        except Exception as e:
            agent.log_action(task.get("type", "unknown"), {"error": str(e)})
            return {"error": str(e)}
    
    async def run_workflow(self, workflow: list):
        """
        Run a workflow (list of agent tasks).
        Tasks can be parallel or sequential.
        """
        results = []
        
        # Group by parallelism
        # Sequential tasks: [agent, task]
        # Parallel tasks: [[agent1, task1], [agent2, task2]]
        
        for step in workflow:
            if isinstance(step, tuple):
                # Sequential
                agent_name, task = step
                result = await self.run_agent_task(agent_name, task)
                results.append(result)
            elif isinstance(step, list):
                # Parallel
                tasks = [
                    self.run_agent_task(agent_name, task)
                    for agent_name, task in step
                ]
                step_results = await asyncio.gather(*tasks)
                results.extend(step_results)
        
        return results
    
    def get_all_stats(self):
        return {name: agent.get_stats() for name, agent in self.agents.items()}
