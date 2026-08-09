"""
📚 WEEKLY AI RESEARCH
Every week: Find latest AI papers, techniques, models.
Apply findings to make system smarter.
"""
import json
import time
import requests
from pathlib import Path
from datetime import datetime

class WeeklyAIResearch:
    """
    Researches latest AI developments weekly.
    Sources:
    - arXiv papers
    - HF trending models
    - GitHub trending AI repos
    - AI news sites
    """
    
    SOURCES = {
        "arxiv_ai": "http://export.arxiv.org/api/query?searchQuery=cat:cs.AI&max_results=20&sortBy=submittedDate&sortOrder=descending",
        "arxiv_ml": "http://export.arxiv.org/api/query?searchQuery=cat:cs.LG&max_results=20&sortBy=submittedDate&sortOrder=descending",
        "arxiv_cl": "http://export.arxiv.org/api/query?searchQuery=cat:cs.CL&max_results=20&sortBy=submittedDate&sortOrder=descending",
        "github_trending": "https://api.github.com/search/repositories?q=ai+artificial+intelligence&sort=stars&order=desc&per_page=20",
        "hf_trending": "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=20",
    }
    
    RESEARCH_DIR = Path("../data/weekly_research")
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    
    def __init__(self):
        self.findings = []
        self.applications = []
    
    def research_arxiv(self, category="ai"):
        """Fetch latest papers from arXiv."""
        url = self.SOURCES.get(f"arxiv_{category}", self.SOURCES["arxiv_ai"])
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return self._parse_arxiv(response.text)
        except Exception as e:
            print(f"   ❌ arXiv error: {e}")
        
        return []
    
    def _parse_arxiv(self, xml_text):
        """Parse arXiv XML response."""
        import re
        papers = []
        
        # Extract titles and summaries
        entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
        
        for entry in entries[:20]:
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            
            if title_match and summary_match:
                papers.append({
                    "title": title_match.group(1).strip()[:200],
                    "summary": summary_match.group(1).strip()[:500],
                    "source": "arxiv"
                })
        
        return papers
    
    def research_github_ai(self):
        """Find trending AI repos."""
        try:
            response = requests.get(
                self.SOURCES["github_trending"],
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                data = response.json()
                repos = []
                for item in data.get("items", [])[:20]:
                    repos.append({
                        "name": item["full_name"],
                        "description": item.get("description", "")[:300],
                        "stars": item.get("stargazers_count", 0),
                        "url": item["html_url"],
                        "source": "github"
                    })
                return repos
        except Exception as e:
            print(f"   ❌ GitHub error: {e}")
        return []
    
    def research_hf_trending(self):
        """Find trending HF models."""
        try:
            response = requests.get(self.SOURCES["hf_trending"], timeout=30)
            if response.status_code == 200:
                models = response.json()
                return [
                    {
                        "name": m.get("modelId", m.get("id")),
                        "downloads": m.get("downloads", 0),
                        "likes": m.get("likes", 0),
                        "source": "huggingface"
                    }
                    for m in models[:20]
                ]
        except Exception as e:
            print(f"   ❌ HF error: {e}")
        return []
    
    def extract_techniques(self, papers):
        """
        Extract AI techniques from research papers.
        These are patterns we can apply to our system.
        """
        techniques = []
        
        # Common AI technique keywords
        technique_keywords = [
            "transformer", "attention mechanism", "self-attention",
            "fine-tuning", "transfer learning", "few-shot learning",
            "zero-shot", "in-context learning", "chain-of-thought",
            "rag", "retrieval augmented", "vector embeddings",
            "reinforcement learning", "rlhf", "reward modeling",
            "distillation", "quantization", "pruning",
            "mixture of experts", "moe", "sparse",
            "agent", "multi-agent", "tool use",
            "memory", "long context", "retrieval",
            "reasoning", "planning", "reflection",
            "constitutional ai", "self-correction",
            "tree of thought", "graph reasoning",
            "self-play", "curriculum learning",
            "meta-learning", "neural architecture search",
            "prompt engineering", "instruction tuning",
        ]
        
        for paper in papers:
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            for kw in technique_keywords:
                if kw in text:
                    techniques.append({
                        "technique": kw,
                        "paper": paper.get("title", "")[:100],
                        "url": paper.get("url", "")
                    })
        
        return techniques[:50]  # Top 50
    
    def apply_to_system(self, technique):
        """
        Apply an AI technique to our system.
        Returns concrete implementation ideas.
        """
        applications = {
            "chain-of-thought": "Add step-by-step reasoning to all agents",
            "rag": "Add retrieval from past actions for context",
            "self-correction": "Agents review and fix their own work",
            "tree of thought": "Explore multiple strategies before choosing",
            "reflection": "Daily self-review and improvement",
            "memory": "Long-term agent memory across sessions",
            "meta-learning": "Learn how to learn faster",
            "few-shot learning": "Show examples before asking for action",
            "multi-agent": "Agents collaborate on complex tasks",
            "tool use": "Agents use external tools automatically",
            "planning": "Multi-step planning before action",
            "curriculum learning": "Start easy, progress to hard tasks",
            "in-context learning": "Learn from current conversation",
            "constitutional ai": "Built-in safety principles",
            "retrieval augmented": "Pull info from knowledge base",
            "self-attention": "Focus on what matters in each task",
            "transfer learning": "Apply learnings across domains",
        }
        
        return applications.get(technique, f"Apply {technique} to relevant agents")
    
    def run_weekly_research(self):
        """Run the weekly research cycle."""
        print("📚 WEEKLY AI RESEARCH")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
        print()
        
        all_papers = []
        
        # 1. arXiv
        print("🔍 Fetching arXiv papers...")
        for cat in ["ai", "ml", "cl"]:
            papers = self.research_arxiv(cat)
            all_papers.extend(papers)
            print(f"   ✅ {cat}: {len(papers)} papers")
        
        # 2. GitHub
        print("\n🐙 Fetching GitHub trending AI...")
        repos = self.research_github_ai()
        print(f"   ✅ {len(repos)} repos")
        
        # 3. Hugging Face
        print("\n🤗 Fetching HF trending models...")
        models = self.research_hf_trending()
        print(f"   ✅ {len(models)} models")
        
        # 4. Extract techniques
        print("\n🧠 Extracting techniques...")
        techniques = self.extract_techniques(all_papers)
        print(f"   ✅ Found {len(techniques)} technique applications")
        
        # 5. Generate applications
        applications = []
        for t in techniques[:50]:
            app = self.apply_to_system(t["technique"])
            applications.append({
                "technique": t["technique"],
                "application": app,
                "paper": t["paper"]
            })
        
        # 6. Save
        report = {
            "date": datetime.now().isoformat(),
            "papers_found": len(all_papers),
            "repos_found": len(repos),
            "models_found": len(models),
            "techniques": techniques,
            "applications": applications,
        }
        
        report_file = self.RESEARCH_DIR / f"weekly_{datetime.now().strftime('%Y%m%d')}.json"
        report_file.write_text(json.dumps(report, indent=2))
        
        print(f"\n💾 Saved: {report_file}")
        
        # Print top applications
        print("\n🎯 TOP APPLICATIONS:")
        for i, app in enumerate(applications[:10], 1):
            print(f"   {i}. {app['technique']}")
            print(f"      → {app['application']}")
        
        return report


if __name__ == "__main__":
    researcher = WeeklyAIResearch()
    researcher.run_weekly_research()
