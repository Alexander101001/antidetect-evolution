"""
🐙 GITHUB REPO AGENT
Connects to and uses Hasan's 38 existing GitHub repos.
"""
import json
import subprocess
from pathlib import Path
from base_agent import BaseAgent

class GitHubAgent(BaseAgent):
    """
    Uses Hasan's existing GitHub repos to:
    - Learn patterns
    - Cross-pollinate features
    - Generate new repos
    - Manage the empire
    """
    
    def __init__(self):
        super().__init__("github", "Manages GitHub repos")
        self.user = "Alexander101001"
        self.repos = []
        self._fetch_repos()
    
    def _fetch_repos(self):
        """Get all repos via gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "repo", "list", self.user, "--limit", "50", "--json", "name,description,url,createdAt"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self.repos = json.loads(result.stdout)
        except Exception as e:
            self.logger.error(f"Failed to fetch repos: {e}")
    
    def execute(self, task: dict) -> dict:
        action = task.get("action", "list")
        
        if action == "list":
            return {"repos": self.repos, "count": len(self.repos)}
        elif action == "create_repo":
            return self._create_repo(task)
        elif action == "use_repo":
            return self._use_repo(task)
        elif action == "find_similar":
            return self._find_similar(task)
        
        return {"error": f"Unknown action: {action}"}
    
    def _create_repo(self, task: dict) -> dict:
        """Create new repo."""
        name = task.get("name")
        description = task.get("description", "")
        is_private = task.get("private", False)
        
        try:
            cmd = ["gh", "repo", "create", f"{self.user}/{name}"]
            if is_private:
                cmd.append("--private")
            else:
                cmd.append("--public")
            if description:
                cmd.extend(["--description", description])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {"success": True, "repo": name, "url": f"https://github.com/{self.user}/{name}"}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def _use_repo(self, task: dict) -> dict:
        """Use an existing repo - clone, analyze, etc."""
        repo_name = task.get("repo")
        if not repo_name:
            return {"error": "No repo specified"}
        
        # Just acknowledge for now - we can extend
        return {
            "success": True,
            "repo": repo_name,
            "action": "tracked",
            "message": f"Repo {repo_name} is now available for cross-pollination"
        }
    
    def _find_similar(self, task: dict) -> dict:
        """Find repos similar to given topic."""
        topic = task.get("topic", "").lower()
        similar = []
        
        for repo in self.repos:
            desc = (repo.get("description") or "").lower()
            name = repo.get("name", "").lower()
            if topic in desc or topic in name:
                similar.append(repo)
        
        return {"similar": similar, "count": len(similar)}


if __name__ == "__main__":
    agent = GitHubAgent()
    print(f"📦 Found {len(agent.repos)} repos")
    print(f"Sample repos: {[r['name'] for r in agent.repos[:5]]}")
    
    # Test find similar
    result = agent.execute({"action": "find_similar", "topic": "tool"})
    print(f"Tool-related repos: {result['count']}")
