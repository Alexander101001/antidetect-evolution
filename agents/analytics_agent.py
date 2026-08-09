"""
📊 ANALYTICS AGENT
Tracks performance of all tools.
"""
import json
import time
from pathlib import Path
from base_agent import BaseAgent

class AnalyticsAgent(BaseAgent):
    """
    Tracks and reports on tool performance.
    """
    
    def __init__(self):
        super().__init__("analytics", "Tracks performance metrics")
        self.analytics_file = Path("../empire/analytics.json")
    
    def execute(self, task: dict) -> dict:
        """Run analytics task."""
        action = task.get("action", "report")
        
        if action == "report":
            return self._generate_report()
        elif action == "track_visit":
            return self._track_visit(task.get("tool"), task.get("source"))
        elif action == "track_conversion":
            return self._track_conversion(task.get("tool"), task.get("amount"))
        
        return {"error": f"Unknown action: {action}"}
    
    def _load_data(self):
        if self.analytics_file.exists():
            try:
                return json.loads(self.analytics_file.read_text())
            except:
                pass
        return {
            "visits": {},
            "conversions": [],
            "revenue": 0,
            "tools_count": 0
        }
    
    def _save_data(self, data):
        self.analytics_file.write_text(json.dumps(data, indent=2))
    
    def _generate_report(self):
        data = self._load_data()
        
        total_visits = sum(data["visits"].values())
        total_revenue = data["revenue"]
        
        report = {
            "total_visits": total_visits,
            "total_revenue": total_revenue,
            "tools_count": data["tools_count"],
            "rpm": (total_revenue / total_visits * 1000) if total_visits > 0 else 0,
            "top_tools": sorted(
                data["visits"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        return report
    
    def _track_visit(self, tool: str, source: str = "direct"):
        data = self._load_data()
        if tool not in data["visits"]:
            data["visits"][tool] = 0
        data["visits"][tool] += 1
        self._save_data(data)
        return {"tracked": True, "tool": tool, "total_visits": data["visits"][tool]}
    
    def _track_conversion(self, tool: str, amount: float):
        data = self._load_data()
        data["conversions"].append({
            "tool": tool,
            "amount": amount,
            "timestamp": time.time()
        })
        data["revenue"] += amount
        self._save_data(data)
        return {"tracked": True, "amount": amount, "total_revenue": data["revenue"]}


if __name__ == "__main__":
    agent = AnalyticsAgent()
    print(agent.execute({"action": "report"}))
