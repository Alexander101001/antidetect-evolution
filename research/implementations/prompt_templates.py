"""📝 PROMPT TEMPLATES - from Anthropic (37k stars)"""
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    role: str
    context: str
    task: str
    format: str
    examples: str = ""
    
    def render(self):
        parts = [f"# Role\n{self.role}", f"# Context\n{self.context}", f"# Task\n{self.task}", f"# Format\n{self.format}"]
        if self.examples:
            parts.append(f"# Examples\n{self.examples}")
        return "\n\n".join(parts)


TEMPLATES = {
    "code_generation": PromptTemplate(
        role="You are an expert Python developer.",
        context="Building autonomous AI agents.",
        task="Write code for the requested feature.",
        format="Code + explanation + dependencies"
    ),
    "research": PromptTemplate(
        role="You are a market researcher.",
        context="Finding profitable niches.",
        task="Research the topic.",
        format="Market size + opportunities + steps + revenue"
    ),
    "content": PromptTemplate(
        role="You are an SEO writer.",
        context="Writing for tool websites.",
        task="Write a blog post.",
        format="Title + meta + 500 words + subheadings + CTA"
    ),
}


if __name__ == "__main__":
    print("📝 PROMPT TEMPLATES (Anthropic Pattern)")
    print(f"   {len(TEMPLATES)} templates ready")
