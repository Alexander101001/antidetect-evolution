"""📊 OBSERVABILITY - from Langfuse (33k stars)"""
import json
import time
from pathlib import Path
from datetime import datetime

TRACE_FILE = Path("agent_traces.jsonl")

class AgentTracer:
    def __init__(self):
        TRACE_FILE.touch(exist_ok=True)
    
    def trace(self, agent_name, action, inputs=None, output=None, duration_ms=0, error=None):
        entry = {
            "timestamp": time.time(),
            "agent": agent_name,
            "action": action,
            "duration_ms": duration_ms,
            "error": error
        }
        with TRACE_FILE.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def stats(self):
        lines = TRACE_FILE.read_text().strip().split("\n")
        if not lines or lines == [""]:
            return {"total": 0}
        return {"total": len(lines), "last": lines[-1][:100]}


tracer = AgentTracer()


def traced(agent_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = (time.time() - start) * 1000
                tracer.trace(agent_name, func.__name__, duration_ms=duration)
        return wrapper
    return decorator


if __name__ == "__main__":
    @traced("test_agent")
    def my_function(x):
        return x * 2
    
    my_function(5)
    print(f"📊 Stats: {tracer.stats()}")
