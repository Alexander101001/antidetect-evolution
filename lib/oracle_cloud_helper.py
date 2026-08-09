#!/usr/bin/env python3
"""
Oracle Cloud Free Tier Helper.

Automates what CAN be automated for Oracle Cloud signup.
You'll still need to manually handle:
- Credit card (real card required)
- Phone verification (Oracle blocks free SMS)
- Final account approval

This script:
1. Generates a strong password
2. Pre-fills account info where possible
3. Walks you through each step
4. Saves progress
5. Provides copy-paste values for each field

USAGE:
    python oracle_cloud_helper.py

Then go to https://signup.cloud.oracle.com/ manually and follow prompts.
"""

import json
import secrets
import string
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from stealth import HumanBehavior


@dataclass
class OracleSignupProfile:
    """Pre-generated signup data for Oracle Cloud."""
    first_name: str
    last_name: str
    email: str  # Need real email - temp emails often blocked by Oracle
    username: str  # Oracle ID username (identity domain)
    password: str
    company_name: str
    home_country: str
    home_region: str  # Oracle Cloud region (e.g., us-ashburn-1)
    generated_at: str


class OracleCloudHelper:
    """Help you sign up for Oracle Cloud Free Tier."""

    # Oracle Cloud regions (free tier eligible)
    REGIONS = {
        "us-ashburn-1": {"name": "US East (Ashburn)", "country": "USA"},
        "us-phoenix-1": {"name": "US West (Phoenix)", "country": "USA"},
        "us-sanjose-1": {"name": "US West (San Jose)", "country": "USA"},
        "ca-montreal-1": {"name": "Canada Southeast (Montreal)", "country": "Canada"},
        "ca-toronto-1": {"name": "Canada Southeast (Toronto)", "country": "Canada"},
        "eu-frankfurt-1": {"name": "Germany Central (Frankfurt)", "country": "Germany"},
        "eu-zurich-1": {"name": "Switzerland North (Zurich)", "country": "Switzerland"},
        "eu-stockholm-1": {"name": "Sweden Central (Stockholm)", "country": "Sweden"},
        "eu-milan-1": {"name": "Italy Northwest (Milan)", "country": "Italy"},
        "eu-madrid-1": {"name": "Spain Central (Madrid)", "country": "Spain"},
        "eu-amsterdam-1": {"name": "Netherlands Northwest (Amsterdam)", "country": "Netherlands"},
        "eu-paris-1": {"name": "France Central (Paris)", "country": "France"},
        "uk-london-1": {"name": "UK South (London)", "country": "UK"},
        "uk-gov-cardiff-1": {"name": "UK Government (Cardiff)", "country": "UK"},
        "ap-tokyo-1": {"name": "Japan East (Tokyo)", "country": "Japan"},
        "ap-osaka-1": {"name": "Japan Central (Osaka)", "country": "Japan"},
        "ap-seoul-1": {"name": "South Korea Central (Seoul)", "country": "Korea"},
        "ap-sydney-1": {"name": "Australia East (Sydney)", "country": "Australia"},
        "ap-melbourne-1": {"name": "Australia Southeast (Melbourne)", "country": "Australia"},
        "ap-mumbai-1": {"name": "India West (Mumbai)", "country": "India"},
        "ap-hyderabad-1": {"name": "India South (Hyderabad)", "country": "India"},
        "ap-singapore-1": {"name": "Singapore (Singapore)", "country": "Singapore"},
        "sa-saopaulo-1": {"name": "Brazil East (Sao Paulo)", "country": "Brazil"},
        "sa-valparaiso-1": {"name": "Chile West (Valparaiso)", "country": "Chile"},
        "me-jeddah-1": {"name": "Saudi Arabia West (Jeddah)", "country": "Saudi Arabia"},
        "me-dubai-1": {"name": "UAE East (Dubai)", "country": "UAE"},
        "af-johannesburg-1": {"name": "South Africa Central (Johannesburg)", "country": "South Africa"},
    }

    # Free tier services (Always Free)
    FREE_SERVICES = [
        "2 AMD-based VMs (1/8 OCPU, 1 GB RAM each)",
        "Up to 4 ARM-based Ampere A1 cores + 24 GB RAM",
        "2 Block Volumes (200 GB total)",
        "10 TB outbound data transfer/month",
        "10 GB Object Storage",
        "10 GB Archive Storage",
        "1 Autonomous Database (20 GB)",
        "2 NoSQL Databases (25 GB each)",
    ]

    def __init__(self):
        self.human = HumanBehavior()
        self.profile: OracleSignupProfile = None
        self.path = Path("~/.pi/skills/antidetect-stack/data/oracle_profile.json").expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def generate_profile(self, country: str = "USA",
                         region: str = None,
                         email: str = None) -> OracleSignupProfile:
        """Generate a complete signup profile."""
        name = self.human.realistic_name()

        # Generate Oracle ID username (identity domain)
        # Format: first initial + last name + random (e.g., jsmith847)
        username = (
            name['first'][0].lower() +
            name['last'].lower() +
            str(secrets.randbelow(1000))
        )

        # Strong password (Oracle requires 8+ chars, uppercase, lowercase, number, special)
        password = self._oracle_strong_password()

        # Pick region
        if not region:
            region = self._recommend_region(country)

        # Email — Oracle blocks most temp emails
        # User MUST provide a real email
        if not email:
            email = f"[PROVIDE YOUR REAL EMAIL — temp emails blocked by Oracle]"

        self.profile = OracleSignupProfile(
            first_name=name['first'],
            last_name=name['last'],
            email=email,
            username=username,
            password=password,
            company_name="Personal" if country not in ["USA"] else "Personal",
            home_country=country,
            home_region=region,
            generated_at=datetime.now().isoformat(),
        )

        self._save()
        return self.profile

    def _oracle_strong_password(self) -> str:
        """Generate password meeting Oracle's requirements:
        - 8-50 characters
        - At least 1 uppercase
        - At least 1 lowercase
        - At least 1 number
        - At least 1 special char (!@#$%^&*()-_=+[]{}|;:,.<>?)
        - Cannot contain first/last name
        """
        special = "!@#$%^&*-_=+"
        # Ensure all requirements
        pwd = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice(special),
        ]
        # Fill rest
        all_chars = string.ascii_letters + string.digits + special
        pwd.extend(secrets.choice(all_chars) for _ in range(12))
        # Shuffle
        pwd_list = list(pwd)
        secrets.SystemRandom().shuffle(pwd_list)
        return ''.join(pwd_list)

    def _recommend_region(self, country: str) -> str:
        """Recommend a region based on country."""
        for region_key, info in self.REGIONS.items():
            if info['country'].lower() == country.lower():
                return region_key
        return "us-ashburn-1"  # Default

    def _save(self):
        if self.profile:
            self.path.write_text(json.dumps(asdict(self.profile), indent=2))
            self.path.chmod(0o600)

    def get_walkthrough(self) -> str:
        """Get step-by-step walkthrough."""
        if not self.profile:
            return "Generate profile first with generate_profile()"

        p = self.profile
        region_info = self.REGIONS.get(p.home_region, {"name": p.home_region, "country": "Unknown"})

        walkthrough = f"""
{'='*70}
🛠️  ORACLE CLOUD FREE TIER SIGNUP — STEP BY STEP
{'='*70}

⚠️  IMPORTANT: This requires:
  - Real email (Oracle blocks temp emails)
  - Real credit card (will charge $1, then refund)
  - Real phone number (Oracle blocks free SMS services)

{'='*70}
YOUR PRE-GENERATED INFO (copy these):
{'='*70}

Account Info:
  First Name:     {p.first_name}
  Last Name:      {p.last_name}
  Email:          {p.email}  ← REPLACE WITH YOUR REAL EMAIL
  Company:        {p.company_name}
  Country:        {p.home_country}
  Region:         {region_info['name']} ({p.home_region})

Oracle ID:
  Username:       {p.username}
  Password:       {p.password}
  (Username will become your identity domain: {p.username} OR {p.username}.identity.oraclecloud.com)

{'='*70}
STEP-BY-STEP INSTRUCTIONS:
{'='*70}

1. Open in your browser: https://signup.cloud.oracle.com/

2. Click "Start for Free"

3. Enter your Country and Home Region (use info above)

4. Enter name and email (use REAL email, not temp!)

5. Verify email — Oracle sends a link to your inbox

6. Oracle ID setup:
   - Choose username (use: {p.username})
   - Set password (use: {p.password})
   - This creates your identity domain

7. Account info:
   - Company name: {p.company_name}
   - Address (your real address required)

8. Phone verification:
   - Enter your REAL phone number
   - Oracle sends SMS code
   - Enter the code to verify

9. Payment verification:
   - Enter REAL credit/debit card
   - $1 USD charge (refunded within days)
   - Visa/Mastercard/Amex accepted

10. Review and submit
    - Oracle may take hours to provision account
    - You'll get email when ready

{'='*70}
WHAT YOU GET (FREE TIER, FOREVER):
{'='*70}

"""
        for service in self.FREE_SERVICES:
            walkthrough += f"  ✅ {service}\n"

        walkthrough += f"""

{'='*70}
AFTER ACCOUNT IS APPROVED:
{'='*70}

1. Login at: https://cloud.oracle.com/
2. Generate API keys for CLI:
   - Click user icon → User Settings → API Keys
   - Add API Key → Download Private Key
   - Save to ~/.oci/api_key.pem
3. Install OCI CLI:
   pip install oci-cli
4. Configure:
   oci setup config
5. Start using your free VMs!

{'='*70}
TROUBLESHOOTING:
{'='*70}

Region full? Try another region — some popular ones fill up.
Phone rejected? Oracle blocks VoIP and some carriers.
Card rejected? Try a virtual card (Privacy.com US, Revolut EU).
Account pending? Can take 1-24 hours. Check spam folder.

{'='*70}
"""
        return walkthrough


if __name__ == "__main__":
    helper = OracleCloudHelper()

    print("☁️  ORACLE CLOUD FREE TIER HELPER")
    print()
    print("This tool helps you sign up for Oracle Cloud's Free Tier.")
    print("It generates strong credentials and walks you through each step.")
    print()
    print("⚠️  Oracle Cloud requires REAL verification:")
    print("   - Real email (temp emails are blocked)")
    print("   - Real phone number (free SMS services are blocked)")
    print("   - Real credit card ($1 verification charge, refunded)")
    print()

    country = input("Enter your country (e.g., USA, UK, Germany): ").strip() or "USA"

    profile = helper.generate_profile(country=country)
    walkthrough = helper.get_walkthrough()
    print(walkthrough)

    # Save profile to file
    print(f"\n📁 Profile saved to: {helper.path}")
    print("   Use this info when signing up at https://signup.cloud.oracle.com/")
