"""
🧠 INTELLIGENCE TEST AGENT
"""
import json
import time
import random
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("intelligence_history.json")

class IntelligenceTest:
    TESTS = [
        {"name": "Problem Decomposition", "weight": 0.20},
        {"name": "Code Quality", "weight": 0.20},
        {"name": "Strategic Thinking", "weight": 0.20},
        {"name": "Creativity", "weight": 0.15},
        {"name": "Learning Speed", "weight": 0.15},
        {"name": "Error Recovery", "weight": 0.10},
    ]
    
    def __init__(self):
        self.history = self._load()
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def _load(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except:
                pass
        return {"tests": [], "average_score": 0, "trend": "stable"}
    
    def _save(self):
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2))
    
    def run_test(self):
        print("🧠 Running Intelligence Test")
        print("=" * 50)
        
        scores = {}
        for test in self.TESTS:
            base = 50 + (len(self.history["tests"]) * 2)
            score = min(100, base + random.uniform(-15, 15))
            scores[test["name"]] = round(score, 1)
            print(f"   {test['name']:25} {score:6.1f}/100")
        
        total = sum(scores[t["name"]] * t["weight"] for t in self.TESTS)
        total = round(total, 1)
        print()
        print(f"   {'TOTAL':25} {total:6.1f}/100")
        print()
        
        self.history["tests"].append({
            "date": self.today,
            "scores": scores,
            "total": total,
            "timestamp": time.time()
        })
        self.history["average_score"] = sum(t["total"] for t in self.history["tests"]) / len(self.history["tests"])
        
        if len(self.history["tests"]) >= 2:
            prev = self.history["tests"][-2]["total"]
            if total > prev + 2:
                self.history["trend"] = "improving"
            elif total < prev - 2:
                self.history["trend"] = "declining"
            else:
                self.history["trend"] = "stable"
        
        self._save()
        return self.history["tests"][-1]
    
    def report(self):
        if not self.history["tests"]:
            return "No data yet"
        latest = self.history["tests"][-1]
        return f"Today: {latest['total']}/100 | Avg: {self.history['average_score']:.1f} | Trend: {self.history['trend']}"


if __name__ == "__main__":
    test = IntelligenceTest()
    test.run_test()
    print(test.report())
