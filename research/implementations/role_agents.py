"""👥 ROLE-BASED AGENTS - from CrewAI (57k stars)"""
from dataclasses import dataclass

@dataclass
class RoleAgent:
    role: str
    goal: str
    backstory: str
    tools: list = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
    
    def act(self, task):
        return f"[{self.role}] Working on: {task}. Goal: {self.goal}"


AGENT_ROLES = {
    "tool_generator": RoleAgent(
        role="Tool Creator",
        goal="Create useful monetizable web tools",
        backstory="Expert in HTML/CSS/JS, knows SEO, creates tools users love"
    ),
    "content_writer": RoleAgent(
        role="Content Writer",
        goal="Write engaging blog posts that rank on Google",
        backstory="SEO expert, understands audience intent"
    ),
    "seo_optimizer": RoleAgent(
        role="SEO Specialist",
        goal="Rank #1 on Google for target keywords",
        backstory="Knows every SEO trick, understands search algorithms"
    ),
    "ad_manager": RoleAgent(
        role="Ad Revenue Manager",
        goal="Maximize ad revenue per visitor",
        backstory="Expert in 10+ ad networks, A/B testing"
    ),
    "analytics_agent": RoleAgent(
        role="Data Analyst",
        goal="Find insights from data to improve performance",
        backstory="Stats expert, knows what numbers matter"
    ),
    "research_agent": RoleAgent(
        role="Market Researcher",
        goal="Find profitable opportunities",
        backstory="Knows markets, trends, competitors"
    ),
}


if __name__ == "__main__":
    print("👥 ROLE-BASED AGENTS")
    print()
    for name, agent in AGENT_ROLES.items():
        print(f"   {name}: {agent.role}")
        print(f"      → {agent.goal}")
