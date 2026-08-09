#!/usr/bin/env python3
"""
Pattern Cache — remember successful registration strategies per platform.

Once we register on a site successfully, cache:
- Form field names
- Required fields and types
- Verification flow (email vs SMS)
- Optimal delays

Next time we visit the same platform, we know exactly what to do.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urlparse


class PatternCache:
    """Cache learned platform patterns."""

    def __init__(self, storage_path: str = None):
        self.path = Path(storage_path or "~/.pi/skills/antidetect-stack/data/patterns.json").expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.patterns = self._load()

    def _load(self) -> Dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                return {}
        return {}

    def _save(self):
        self.path.write_text(json.dumps(self.patterns, indent=2, default=str))

    @staticmethod
    def _key(url: str) -> str:
        """Key patterns by domain."""
        domain = urlparse(url).netloc
        # Strip www.
        return domain.replace('www.', '')

    def get(self, url: str) -> Optional[Dict]:
        """Get cached pattern for a URL."""
        key = self._key(url)
        return self.patterns.get(key)

    def save(self, url: str, pattern: Dict):
        """Save a pattern for future use."""
        key = self._key(url)
        pattern['last_used'] = time.time()
        pattern['use_count'] = self.patterns.get(key, {}).get('use_count', 0) + 1
        self.patterns[key] = pattern
        self._save()

    def record_success(self, url: str, notes: str = ""):
        """Record a successful registration."""
        key = self._key(url)
        if key in self.patterns:
            self.patterns[key]['success_count'] = self.patterns[key].get('success_count', 0) + 1
            self.patterns[key]['last_success'] = time.time()
            if notes:
                self.patterns[key]['success_notes'] = notes
            self._save()

    def record_failure(self, url: str, error: str):
        """Record a failure for learning."""
        key = self._key(url)
        if key in self.patterns:
            self.patterns[key]['failure_count'] = self.patterns[key].get('failure_count', 0) + 1
            self.patterns[key]['last_failure'] = time.time()
            self.patterns[key]['last_error'] = error[:200]
            self._save()

    def list_known(self) -> List[str]:
        return list(self.patterns.keys())


if __name__ == "__main__":
    pc = PatternCache()
    print(f"📚 Known patterns: {len(pc.list_known())}")
    for k in pc.list_known():
        p = pc.patterns[k]
        success = p.get('success_count', 0)
        fail = p.get('failure_count', 0)
        print(f"   - {k}: {success} success, {fail} fail")
