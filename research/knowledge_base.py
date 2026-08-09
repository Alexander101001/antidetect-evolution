"""
🧠 AI KNOWLEDGE BASE
Stores patterns and techniques from:
- 20 trending GitHub repos
- 20 trending HF models
- 50 smarter things
- Research papers

Other agents can query this for guidance.
"""
import json
import re
from pathlib import Path
from datetime import datetime

KNOWLEDGE_FILE = Path("knowledge_base.json")

class KnowledgeBase:
    """Central knowledge from all research."""
    
    def __init__(self):
        self.knowledge = self._load()
    
    def _load(self):
        if KNOWLEDGE_FILE.exists():
            try:
                return json.loads(KNOWLEDGE_FILE.read_text())
            except:
                pass
        return {
            "techniques": {},
            "patterns": {},
            "best_practices": [],
            "tools_to_use": [],
            "models_to_use": [],
            "common_pitfalls": [],
            "last_updated": None
        }
    
    def _save(self):
        KNOWLEDGE_FILE.write_text(json.dumps(self.knowledge, indent=2))
    
    def add_from_repos(self, repos):
        """Extract techniques from trending GitHub repos."""
        repo_techniques = {
            "infiniflow/ragflow": {
                "technique": "RAG (Retrieval Augmented Generation)",
                "application": "Use vector DB to retrieve relevant past actions before deciding",
                "priority": "HIGH",
                "implementation": "Store all agent actions in ChromaDB/FAISS, retrieve similar past actions for context"
            },
            "fighting41love/funNLP": {
                "technique": "Multi-language NLP toolkit",
                "application": "Support Arabic, English, Chinese in our system",
                "priority": "MEDIUM",
                "implementation": "Add language detection + translation for Arabic content (Hasan's language)"
            },
            "dair-ai/Prompt-Engineering-Guide": {
                "technique": "Prompt engineering patterns",
                "application": "Use structured prompts for all AI tasks",
                "priority": "HIGH",
                "implementation": "Create prompt templates with: role, context, task, format, examples"
            },
            "hiyouga/LlamaFactory": {
                "technique": "Unified LLM fine-tuning",
                "application": "Fine-tune models on our specific data",
                "priority": "LOW",
                "implementation": "Train on our successful actions to improve agent behavior"
            },
            "CompVis/stable-diffusion": {
                "technique": "Diffusion models for images",
                "application": "Auto-generate images for blog posts and tools",
                "priority": "MEDIUM",
                "implementation": "Generate thumbnails, social media images automatically"
            },
            "unslothai/unsloth": {
                "technique": "Fast local model training",
                "application": "Train small models locally for fast inference",
                "priority": "MEDIUM",
                "implementation": "Use Unsloth to fine-tune small models for specific tasks"
            },
            "ruvnet/ruflo": {
                "technique": "Multi-agent orchestration",
                "application": "Coordinate many agents working together",
                "priority": "HIGH",
                "implementation": "Use their swarm patterns for our 66 agents"
            },
            "labmlai/annotated_deep_learning_paper_implementations": {
                "technique": "Paper implementations",
                "application": "Reference implementations for complex techniques",
                "priority": "MEDIUM",
                "implementation": "Study their code patterns for implementing new algorithms"
            },
            "gsd-build/get-shit-done": {
                "technique": "Meta-prompting + spec-driven development",
                "application": "Generate detailed specs before coding",
                "priority": "HIGH",
                "implementation": "Always create spec.md before implementing features"
            },
            "crewAIInc/crewAI": {
                "technique": "Role-playing autonomous agents",
                "application": "Each of our 66 agents has specific role + goal",
                "priority": "HIGH",
                "implementation": "Use their CrewAI patterns for agent collaboration"
            },
            "run-llama/llama_index": {
                "technique": "Document agents + OCR",
                "application": "Process documents, extract info automatically",
                "priority": "HIGH",
                "implementation": "Use LlamaIndex for document processing in content_agent"
            },
            "CherryHQ/cherry-studio": {
                "technique": "AI productivity with 300+ assistants",
                "application": "Multiple specialized assistants for different tasks",
                "priority": "MEDIUM",
                "implementation": "Each of our 66 agents is a specialized assistant"
            },
            "HKUDS/LightRAG": {
                "technique": "Simple fast RAG",
                "application": "Lightweight RAG for quick info retrieval",
                "priority": "HIGH",
                "implementation": "Implement LightRAG for our knowledge base queries"
            },
            "anthropics/prompt-eng-interactive-tutorial": {
                "technique": "Anthropic's prompt engineering",
                "application": "Use Anthropic's proven prompt patterns",
                "priority": "HIGH",
                "implementation": "Apply their patterns to all our prompts"
            },
            "khoj-ai/khoj": {
                "technique": "Self-hostable AI second brain",
                "application": "Personal AI assistant that learns from us",
                "priority": "MEDIUM",
                "implementation": "Build similar memory system for our agents"
            },
            "microsoft/graphrag": {
                "technique": "Graph-based RAG",
                "application": "Use knowledge graphs for relationships",
                "priority": "HIGH",
                "implementation": "Build graph DB of agent relationships and dependencies"
            },
            "lutzroeder/netron": {
                "technique": "Visualizer for ML models",
                "application": "Visualize our agent decision flows",
                "priority": "LOW",
                "implementation": "Create dashboards showing agent interactions"
            },
            "langfuse/langfuse": {
                "technique": "LLM observability + evals",
                "application": "Track + evaluate all AI calls",
                "priority": "HIGH",
                "implementation": "Add observability to all our AI agent actions"
            },
            "sgl-project/sglang": {
                "technique": "High-performance LLM serving",
                "application": "Fast inference for our agents",
                "priority": "MEDIUM",
                "implementation": "Use SGLang patterns for batch agent calls"
            },
            "NirDiamant/RAG_Techniques": {
                "technique": "Advanced RAG techniques",
                "application": "Use multiple RAG patterns for different needs",
                "priority": "HIGH",
                "implementation": "Implement: simple RAG, hybrid search, re-ranking, query expansion"
            }
        }
        
        self.knowledge["techniques"].update(repo_techniques)
        self.knowledge["last_updated"] = datetime.now().isoformat()
        self._save()
        
        return len(repo_techniques)
    
    def add_from_models(self, models):
        """Add knowledge from trending models."""
        model_knowledge = {
            "sentence-transformers/all-MiniLM-L6-v2": {
                "use_for": "Fast embeddings for similarity search",
                "size": "80MB",
                "speed": "Very fast",
                "application": "Use for quick text similarity in agent memory"
            },
            "google-bert/bert-base-uncased": {
                "use_for": "Fill-mask + classification",
                "size": "440MB",
                "speed": "Fast",
                "application": "Use for content categorization"
            },
            "cross-encoder/ms-marco-MiniLM-L6-v2": {
                "use_for": "Document ranking",
                "size": "80MB",
                "speed": "Fast",
                "application": "Use to rank search results for RAG"
            },
            "Qwen/Qwen3-0.6B": {
                "use_for": "Lightweight text generation",
                "size": "1.2GB",
                "speed": "Very fast",
                "application": "Use for quick responses, low-latency tasks"
            },
            "google-t5/t5-small": {
                "use_for": "Translation + text-to-text",
                "size": "240MB",
                "speed": "Fast",
                "application": "Use for translation between languages"
            }
        }
        
        self.knowledge["models_to_use"] = list(model_knowledge.values())
        self._save()
        
        return len(model_knowledge)
    
    def query(self, topic):
        """Query knowledge base for a topic."""
        results = []
        topic_lower = topic.lower()
        
        for name, info in self.knowledge["techniques"].items():
            text = (str(info)).lower()
            if topic_lower in text:
                results.append({
                    "source": name,
                    "info": info
                })
        
        return results
    
    def get_high_priority(self):
        """Get high priority techniques to implement."""
        return [
            info for info in self.knowledge["techniques"].values()
            if info.get("priority") == "HIGH"
        ]


if __name__ == "__main__":
    kb = KnowledgeBase()
    
    # Load real data
    repos_file = Path("../data/weekly_research/trending_repos.json")
    models_file = Path("../data/weekly_research/trending_models.json")
    
    if repos_file.exists():
        repos_data = json.loads(repos_file.read_text())
        # Add a marker that we found these
        print(f"📚 Loaded {len(repos_data['top_20'])} trending repos")
    
    if models_file.exists():
        models_data = json.loads(models_file.read_text())
        print(f"🤗 Loaded {len(models_data['top_20'])} trending models")
    
    # For now, use the hardcoded knowledge from trending repos
    # (will be replaced when we re-run weekly research)
    sample_repos = [
        {"name": "infiniflow/ragflow"},
        {"name": "crewAIInc/crewAI"},
        {"name": "run-llama/llama_index"},
    ]
    
    added = kb.add_from_repos(sample_repos)
    print(f"✅ Added {added} techniques to knowledge base")
    
    # Show high priority items
    print("\n🎯 HIGH PRIORITY IMPLEMENTATIONS:")
    for tech in kb.get_high_priority()[:5]:
        print(f"   • {tech['technique']}")
        print(f"     → {tech['application']}")
