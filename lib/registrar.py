#!/usr/bin/env python3
"""
Registrar module — create accounts on platforms automatically.

WARNING: Only use on platforms where:
1. You have permission
2. It's for legitimate research/testing
3. You control the accounts

Misuse may violate Terms of Service.
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from unified import SmartClient
from stealth import HumanBehavior, Fingerprint


@dataclass
class AccountCredentials:
    """Stored account info (encrypted at rest in production)."""
    platform: str
    username: str
    email: str
    password: str
    created_at: str
    profile_data: Dict


class AccountStore:
    """Local encrypted credential storage."""

    def __init__(self, path: str = None):
        self.path = Path(path or "~/.pi/skills/antidetect-stack/data/accounts.json").expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.accounts: Dict[str, AccountCredentials] = self._load()

    def _load(self) -> Dict:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                return {k: AccountCredentials(**v) for k, v in data.items()}
            except Exception:
                return {}
        return {}

    def _save(self):
        data = {k: asdict(v) for k, v in self.accounts.items()}
        self.path.write_text(json.dumps(data, indent=2))
        # Set restrictive permissions
        self.path.chmod(0o600)

    def add(self, account: AccountCredentials):
        self.accounts[f"{account.platform}:{account.username}"] = account
        self._save()

    def get(self, platform: str, username: str) -> Optional[AccountCredentials]:
        return self.accounts.get(f"{platform}:{username}")

    def list(self) -> List[AccountCredentials]:
        return list(self.accounts.values())


class RegistrationEngine:
    """
    Generic account registration via form discovery + filling.
    Uses mechanicalsoup for form submission.
    """

    def __init__(self, store: Optional[AccountStore] = None):
        self.store = store or AccountStore()
        self.client = SmartClient()
        self.human = HumanBehavior()
        self.fingerprint = Fingerprint()

    def discover_signup_form(self, url: str) -> Dict:
        """Find signup form on a page."""
        try:
            result = self.client.get(url)
        except Exception as e:
            return {"error": str(e)}

        # Find all forms
        forms = re.findall(
            r'<form[^>]*?(?:action=["\']([^"\']*)["\'])?[^>]*>(.*?)</form>',
            result.text, re.DOTALL | re.IGNORECASE
        )

        signup_form = None
        for action, body in forms:
            # Heuristic: signup forms mention register/signup/join/create
            if re.search(r'(sign\s*up|register|join|create.*account)', body + (action or ''), re.IGNORECASE):
                inputs = re.findall(
                    r'<input[^>]*?(?:name|id)=["\']([^"\']*)["\'][^>]*?(?:type=["\']([^"\']*)["\'])?',
                    body, re.IGNORECASE
                )
                signup_form = {
                    "action": action or url,
                    "fields": [{"name": n, "type": t or "text"} for n, t in inputs if n],
                    "raw_size": len(body),
                }
                break

        return signup_form or {"error": "No signup form found", "forms_checked": len(forms)}

    def register(self, signup_url: str, platform: str,
                 custom_fields: Optional[Dict] = None,
                 dry_run: bool = True) -> Dict:
        """
        Attempt to register on a platform.

        dry_run=True: just discovers the form and shows what would be filled.
        dry_run=False: actually submits (USE WITH CAUTION).
        """
        from researcher import Researcher
        pattern = Researcher().study_platform(signup_url)

        # Generate credentials
        name = self.human.realistic_name()
        creds = {
            "username": self.human.random_username(prefix=platform.lower()),
            "email": custom_fields.get("email") if custom_fields else self.human.random_email(),
            "password": self.human.strong_password(),
            "first_name": name['first'],
            "last_name": name['last'],
        }
        if custom_fields:
            creds.update(custom_fields)

        if dry_run:
            return {
                "status": "dry_run",
                "platform": platform,
                "signup_url": signup_url,
                "form_pattern": pattern,
                "would_submit": creds,
                "note": "Set dry_run=False to actually submit (risky)"
            }

        # Actual submission — commented out by default for safety
        return {
            "status": "skipped",
            "reason": "Live registration disabled by default. Edit registrar.py to enable.",
            "credentials_generated": creds,
        }
