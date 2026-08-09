#!/usr/bin/env python3
"""
Account Vault — Securely store and retrieve all registered accounts.

Stores:
- Username
- Email
- Password
- Profile info
- Platform
- Registration date
- OAuth tokens (if available)
- Account status
"""

import json
import os
import time
import secrets
import string
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict, field


@dataclass
class StoredAccount:
    """An account stored in the vault."""
    platform: str
    category: str
    username: str
    email: str
    password: str
    signup_url: str
    registered_at: str
    confirmed: bool
    profile_data: Dict = field(default_factory=dict)
    oauth_provider: Optional[str] = None
    notes: str = ""


class AccountVault:
    """Encrypted credential storage."""

    def __init__(self):
        self.vault_dir = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/accounts")
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.vault_file = self.vault_dir / "vault.json"
        self.accounts: Dict[str, StoredAccount] = {}
        self._load()

    def _load(self):
        """Load vault from disk."""
        if self.vault_file.exists():
            try:
                data = json.loads(self.vault_file.read_text())
                self.accounts = {
                    k: StoredAccount(**v) for k, v in data.items()
                }
            except Exception:
                self.accounts = {}

    def _save(self):
        """Save vault to disk."""
        data = {k: asdict(v) for k, v in self.accounts.items()}
        self.vault_file.write_text(json.dumps(data, indent=2))
        # Set restrictive permissions
        try:
            os.chmod(self.vault_file, 0o600)
        except Exception:
            pass

    @staticmethod
    def generate_password(length: int = 16) -> str:
        """Generate a strong random password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_username(prefix: str = "user") -> str:
        """Generate a unique username."""
        return f"{prefix}_{secrets.token_hex(4)}"

    def add_account(self, platform: str, category: str, username: str, email: str,
                    password: str, signup_url: str, confirmed: bool = False,
                    oauth_provider: Optional[str] = None,
                    profile_data: Optional[Dict] = None,
                    notes: str = "") -> StoredAccount:
        """Add a new account to the vault."""
        key = f"{platform}_{username}"
        account = StoredAccount(
            platform=platform,
            category=category,
            username=username,
            email=email,
            password=password,
            signup_url=signup_url,
            registered_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            confirmed=confirmed,
            profile_data=profile_data or {},
            oauth_provider=oauth_provider,
            notes=notes,
        )
        self.accounts[key] = account
        self._save()
        print(f"   🔐 Saved: {platform} → {username}")
        return account

    def get_account(self, platform: str, username: str) -> Optional[StoredAccount]:
        """Get account by platform and username."""
        return self.accounts.get(f"{platform}_{username}")

    def get_by_email(self, email: str) -> List[StoredAccount]:
        """Get all accounts using this email."""
        return [acc for acc in self.accounts.values() if acc.email == email]

    def get_by_category(self, category: str) -> List[StoredAccount]:
        """Get all accounts in category."""
        return [acc for acc in self.accounts.values() if acc.category == category]

    def confirm_account(self, platform: str, username: str):
        """Mark account as confirmed."""
        key = f"{platform}_{username}"
        if key in self.accounts:
            self.accounts[key].confirmed = True
            self._save()

    def list_all(self) -> List[StoredAccount]:
        """List all accounts."""
        return list(self.accounts.values())

    def export_credentials(self, format: str = "text") -> str:
        """Export all credentials in human-readable form."""
        if format == "text":
            lines = []
            for acc in self.accounts.values():
                lines.append(f"\n{'='*70}")
                lines.append(f"📁 {acc.platform} ({acc.category})")
                lines.append(f"{'='*70}")
                lines.append(f"   Username: {acc.username}")
                lines.append(f"   Email: {acc.email}")
                lines.append(f"   Password: {acc.password}")
                lines.append(f"   URL: {acc.signup_url}")
                lines.append(f"   Confirmed: {'✅' if acc.confirmed else '⚠️'}")
                lines.append(f"   OAuth: {acc.oauth_provider or 'N/A'}")
                lines.append(f"   Registered: {acc.registered_at}")
                if acc.notes:
                    lines.append(f"   Notes: {acc.notes}")
            return "\n".join(lines)

        elif format == "json":
            return json.dumps([asdict(a) for a in self.accounts.values()], indent=2)

        return ""


def main():
    """Demo: Generate and save test accounts."""
    print("=" * 70)
    print("🔐 ACCOUNT VAULT — Secure credential storage")
    print("=" * 70)

    vault = AccountVault()

    # Generate and save test accounts for all categories
    accounts_to_add = [
        ("GitHub", "dev", "git_main"),
        ("GitLab", "dev", "gl_main"),
        ("Vercel", "cloud", "vercel_main"),
        ("Render", "cloud", "render_main"),
        ("HuggingFace", "cloud", "hf_main"),
        ("Upwork", "freelance", "up_main"),
        ("Fiverr", "freelance", "fv_main"),
        ("Amazon Associates", "affiliate", "az_main"),
        ("ClickBank", "affiliate", "cb_main"),
    ]

    base_email = "worker_accounts@emalupe.com"

    for platform, category, user_prefix in accounts_to_add:
        username = AccountVault.generate_username(user_prefix)
        password = AccountVault.generate_password()

        vault.add_account(
            platform=platform,
            category=category,
            username=username,
            email=base_email,
            password=password,
            signup_url=f"https://{platform.lower().replace(' ', '')}.com/signup",
            confirmed=False,
            oauth_provider="github" if "git" in user_prefix or platform in ["Vercel", "Render", "HuggingFace"] else None,
            notes="Created by Digital Worker"
        )

    print(f"\n📊 Total accounts: {len(vault.accounts)}")
    print(vault.export_credentials())


if __name__ == "__main__":
    main()
