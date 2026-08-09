"""🕸️ KNOWLEDGE GRAPH - from GraphRAG (35k stars)"""
import json
from pathlib import Path
from collections import defaultdict

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
    
    def add_node(self, name, properties=None):
        self.nodes[name] = properties or {}
    
    def add_edge(self, source, target, relation="related"):
        self.edges[source].append({"target": target, "relation": relation})
    
    def get_neighbors(self, node):
        return self.edges.get(node, [])
    
    def find_path(self, start, end):
        if start == end:
            return [start]
        visited = {start}
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            for edge in self.get_neighbors(path[-1]):
                target = edge["target"]
                if target == end:
                    return path + [target]
                if target not in visited:
                    visited.add(target)
                    queue.append(path + [target])
        return None


if __name__ == "__main__":
    g = KnowledgeGraph()
    agents = ["research_agent", "tool_generator", "content_writer", "seo_optimizer", "ad_manager", "analytics_agent"]
    for a in agents:
        g.add_node(a)
    
    g.add_edge("research_agent", "tool_generator", "finds_for")
    g.add_edge("tool_generator", "content_writer", "needs")
    g.add_edge("content_writer", "seo_optimizer", "uses")
    g.add_edge("seo_optimizer", "ad_manager", "drives_to")
    g.add_edge("ad_manager", "analytics_agent", "sends_to")
    
    print("🕸️ AGENT GRAPH")
    path = g.find_path("research_agent", "ad_manager")
    print(f"   Path: {' → '.join(path) if path else 'none'}")
