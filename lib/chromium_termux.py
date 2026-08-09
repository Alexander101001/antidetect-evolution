#!/usr/bin/env python3
"""
Chromium on Termux — install full browser via proot-distro Ubuntu.

This solves the JS-rendering problem and enables:
- OAuth automation (GitHub, Google buttons)
- CAPTCHAs solving via browser automation
- Full JavaScript execution
- Headless browser control

Free, self-hosted, no paid services.
"""

import subprocess
import time
import os
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class BrowserInstall:
    """Browser installation status."""
    method: str  # proot-distro, termux-direct, fallback
    installed: bool
    path: Optional[str]
    version: Optional[str]
    can_automate: bool


class ChromiumOnTermux:
    """Install and use Chromium on Termux."""

    PROOT_INSTALL_SCRIPT = """
# Install full Ubuntu via proot-distro
pkg update -y
pkg install -y proot-distro
proot-distro install ubuntu
echo "✅ Ubuntu installed"
"""

    UBUNTU_CHROMIUM_INSTALL = """
# Inside Ubuntu proot environment
apt update -y
apt install -y chromium-browser python3-pip

# Install Python automation libraries
pip3 install playwright
python3 -m playwright install chromium
python3 -m playwright install-deps

# Or install Selenium
pip3 install selenium

echo "✅ Chromium + automation libraries installed"
"""

    def __init__(self):
        self.install_log = Path("~/.pi/skills/antidetect-stack/data/chromium_install.log").expanduser()
        self.install_log.parent.mkdir(parents=True, exist_ok=True)

    def check_proot_available(self) -> bool:
        """Check if proot-distro is available."""
        try:
            result = subprocess.run(
                ["which", "proot-distro"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_chromium_available(self) -> Optional[BrowserInstall]:
        """Check if Chromium is installed anywhere."""
        paths_to_check = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/data/data/com.termux/files/usr/bin/chromium",
        ]

        for path in paths_to_check:
            try:
                result = subprocess.run(
                    ["which", path.split("/")[-1]],
                    capture_output=True, text=True, timeout=3
                )
                if result.returncode == 0:
                    return BrowserInstall(
                        method="system",
                        installed=True,
                        path=result.stdout.strip(),
                        version=self._get_browser_version(result.stdout.strip()),
                        can_automate=True,
                    )
            except Exception:
                continue

        return BrowserInstall(
            method="none",
            installed=False,
            path=None,
            version=None,
            can_automate=False,
        )

    def _get_browser_version(self, path: str) -> Optional[str]:
        """Get browser version."""
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def install_chromium_via_proot(self) -> Dict:
        """
        Install Chromium via proot-distro Ubuntu.

        This is the FULL solution for Termux browser automation.
        Takes 5-10 minutes depending on internet speed.
        """
        log = []
        log.append("=" * 70)
        log.append("🚀 INSTALLING CHROMIUM VIA PROOT-DISTRO UBUNTU")
        log.append("=" * 70)

        # Step 1: Check if proot-distro exists
        log.append("\nStep 1: Checking proot-distro...")
        if not self.check_proot_available():
            log.append("   Installing proot-distro...")
            result = subprocess.run(
                ["pkg", "install", "-y", "proot-distro"],
                capture_output=True, text=True, timeout=120
            )
            log.append(f"   Result: {result.returncode}")
            if result.returncode != 0:
                log.append(f"   Error: {result.stderr}")
                return {"success": False, "log": "\n".join(log)}
        else:
            log.append("   ✅ proot-distro already installed")

        # Step 2: Install Ubuntu
        log.append("\nStep 2: Installing Ubuntu (this takes 2-5 minutes)...")
        log.append("   Running: proot-distro install ubuntu")
        result = subprocess.run(
            ["proot-distro", "install", "ubuntu"],
            capture_output=True, text=True, timeout=600
        )
        log.append(f"   Result: {result.returncode}")
        if result.returncode != 0:
            log.append(f"   Error: {result.stderr[:200]}")

        # Step 3: Install Chromium inside Ubuntu
        log.append("\nStep 3: Installing Chromium inside Ubuntu...")
        install_cmd = """
proot-distro login ubuntu -- bash -c '
apt update -y && \
apt install -y chromium-browser python3-pip 2>&1 | tail -5
'
"""
        result = subprocess.run(
            install_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=900  # 15 minutes
        )
        log.append(f"   Result: {result.returncode}")
        if result.stdout:
            log.append(f"   Output: {result.stdout[:500]}")

        # Save log
        self.install_log.write_text("\n".join(log))

        return {
            "success": result.returncode == 0,
            "log": "\n".join(log),
            "method": "proot-distro",
        }

    def install_lightweight_alternative(self) -> Dict:
        """
        Install lighter alternatives that work directly on Termux.

        Faster than full Chromium, fewer features but enables automation.
        """
        log = []
        log.append("=" * 70)
        log.append("⚡ INSTALLING LIGHTWEIGHT BROWSER ALTERNATIVES")
        log.append("=" * 70)

        # Option 1: Install lynx (text-based, won't help with JS)
        # Option 2: Install Firefox via Termux (might work)
        # Option 3: Use Node.js + Puppeteer with Chrome binary

        # Try Firefox first
        log.append("\n1️⃣  Trying Firefox...")
        result = subprocess.run(
            ["pkg", "install", "-y", "firefox"],
            capture_output=True, text=True, timeout=300
        )
        log.append(f"   Firefox: {result.returncode}")
        if result.returncode == 0:
            log.append("   ✅ Firefox installed")
            return {"success": True, "browser": "firefox", "log": "\n".join(log)}

        # Try chromium via Termux directly (limited)
        log.append("\n2️⃣  Trying Chromium directly...")
        result = subprocess.run(
            ["pkg", "install", "-y", "chromium"],
            capture_output=True, text=True, timeout=300
        )
        log.append(f"   Chromium: {result.returncode}")

        self.install_log.write_text("\n".join(log))

        return {
            "success": result.returncode == 0,
            "browser": "chromium" if result.returncode == 0 else None,
            "log": "\n".join(log),
        }

    def get_status(self) -> Dict:
        """Get current browser installation status."""
        status = {
            "proot_available": self.check_proot_available(),
            "chromium_installed": False,
            "firefox_installed": False,
            "automation_ready": False,
            "recommendations": [],
        }

        # Check chromium
        browser = self.check_chromium_available()
        if browser.installed:
            status["chromium_installed"] = True
            status["chromium_path"] = browser.path
            status["chromium_version"] = browser.version
            status["automation_ready"] = True

        # Check firefox
        try:
            result = subprocess.run(
                ["which", "firefox"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                status["firefox_installed"] = True
        except Exception:
            pass

        # Add recommendations
        if not status["proot_available"]:
            status["recommendations"].append(
                "Install proot-distro: pkg install proot-distro"
            )

        if not status["chromium_installed"] and not status["firefox_installed"]:
            status["recommendations"].append(
                "Run install_chromium_via_proot() for full browser automation"
            )

        if not status["automation_ready"]:
            status["recommendations"].append(
                "Use Firecrawl browser mode (cloud) for immediate automation"
            )

        return status


def main():
    print("=" * 70)
    print("🌐 CHROMIUM ON TERMUX — STATUS & INSTALL")
    print("=" * 70)

    ct = ChromiumOnTermux()
    status = ct.get_status()

    print(f"\n📊 Current Status:")
    print(f"   proot-distro available: {status['proot_available']}")
    print(f"   Chromium installed: {status['chromium_installed']}")
    print(f"   Firefox installed: {status['firefox_installed']}")
    print(f"   Automation ready: {status['automation_ready']}")

    if status.get("chromium_version"):
        print(f"   Chromium version: {status['chromium_version']}")

    if status["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in status["recommendations"]:
            print(f"   - {rec}")

    # Ask if user wants to install
    print()
    choice = input("Install Chromium via proot? (yes/no): ").strip().lower()
    if choice in ("yes", "y"):
        print("\nThis will take 5-15 minutes...")
        result = ct.install_chromium_via_proot()
        print(f"\n{'='*70}")
        print(f"Result: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"{'='*70}")
        print(result["log"][-2000:])  # Last 2000 chars of log


if __name__ == "__main__":
    main()
