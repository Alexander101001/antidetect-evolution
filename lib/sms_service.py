#!/usr/bin/env python3
"""
SMS service — automatic phone number retrieval + SMS inbox checking.
Supports multiple free public SMS services.

IMPORTANT: These are PUBLIC inboxes. Anyone can see the SMS codes.
Use ONLY for non-critical accounts. Production use needs paid services.
"""

import requests
import time
import re
from typing import List, Optional, Dict
from dataclasses import dataclass
from unified import SmartClient


@dataclass
class SMSMessage:
    """One SMS in the inbox."""
    sender: str
    body: str
    received_at: str
    number: str


@dataclass
class PhoneNumber:
    """A phone number with its inbox."""
    number: str
    country: str
    service: str
    inbox_url: str
    extra: Dict = None


class SMSService:
    """
    Multi-service SMS inbox checker.
    Each service has different scraping strategy.
    """

    def __init__(self):
        self.client = SmartClient()
        self.current: Optional[PhoneNumber] = None

    def get_number(self, service: str = "receive-smss.com", country: str = "USA") -> PhoneNumber:
        """Get an available phone number from a service."""
        if service == "receive-smss.com":
            return self._receive_smss(country)
        elif service == "receivesms.co":
            return self._receivesms(country)
        elif service == "quackr.io":
            return self._quackr(country)
        elif service == "smscodeonline.com":
            return self._smscodeonline(country)
        elif service == "anonymsms.com":
            return self._anonymsms(country)
        else:
            raise ValueError(f"Unknown service: {service}")

    def _receive_smss(self, country: str) -> PhoneNumber:
        """Get number from receive-smss.com."""
        url = f"https://receive-smss.com"
        result = self.client.get(url, method="jina")

        # Parse the page for numbers
        # Pattern: phone numbers usually appear as +[country_code][number]
        numbers = re.findall(r'\+\d{10,15}', result.text)
        if numbers:
            number = numbers[0]
            self.current = PhoneNumber(
                number=number,
                country=country,
                service="receive-smss.com",
                inbox_url=url,
            )
            return self.current
        raise RuntimeError(f"No numbers found on receive-smss.com")

    def _receivesms(self, country: str) -> PhoneNumber:
        """Get number from receivesms.co."""
        url = "https://receivesms.co"
        result = self.client.get(url, method="jina")

        numbers = re.findall(r'\+\d{10,15}', result.text)
        if numbers:
            number = numbers[0]
            self.current = PhoneNumber(
                number=number,
                country=country,
                service="receivesms.co",
                inbox_url=url,
            )
            return self.current
        raise RuntimeError(f"No numbers found on receivesms.co")

    def _quackr(self, country: str) -> PhoneNumber:
        """Get number from quackr.io."""
        url = "https://quackr.io"
        result = self.client.get(url, method="jina")

        numbers = re.findall(r'\+\d{10,15}', result.text)
        if numbers:
            number = numbers[0]
            self.current = PhoneNumber(
                number=number,
                country=country,
                service="quackr.io",
                inbox_url=url,
            )
            return self.current
        raise RuntimeError(f"No numbers found on quackr.io")

    def _smscodeonline(self, country: str) -> PhoneNumber:
        """Get number from smscodeonline.com."""
        url = "https://smscodeonline.com"
        result = self.client.get(url, method="jina")
        numbers = re.findall(r'\+\d{10,15}', result.text)
        if numbers:
            self.current = PhoneNumber(
                number=numbers[0],
                country=country,
                service="smscodeonline.com",
                inbox_url=url,
            )
            return self.current
        raise RuntimeError("No numbers found")

    def _anonymsms(self, country: str) -> PhoneNumber:
        """Get number from anonymsms.com."""
        url = "https://anonymsms.com"
        result = self.client.get(url, method="jina")
        numbers = re.findall(r'\+\d{10,15}', result.text)
        if numbers:
            self.current = PhoneNumber(
                number=numbers[0],
                country=country,
                service="anonymsms.com",
                inbox_url=url,
            )
            return self.current
        raise RuntimeError("No numbers found")

    def check_inbox(self, timeout: int = 90) -> List[SMSMessage]:
        """
        Check current phone number's inbox for new SMS.
        Returns list of new messages.
        """
        if not self.current:
            raise RuntimeError("Call get_number() first")

        print(f"📱 Waiting for SMS at {self.current.number}...")
        print(f"   Inbox: {self.current.inbox_url}")

        start = time.time()
        # Snapshot the initial page content
        initial = self.client.get(self.current.inbox_url, method="jina").text

        while time.time() - start < timeout:
            time.sleep(5)
            current_text = self.client.get(self.current.inbox_url, method="jina").text

            # Find new content
            if current_text != initial:
                # Look for SMS messages (usually 4-8 digit codes)
                codes = re.findall(r'\b\d{4,8}\b', current_text)
                messages = []
                for code in codes[:5]:
                    messages.append(SMSMessage(
                        sender="unknown",
                        body=f"Verification code: {code}",
                        received_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                        number=self.current.number,
                    ))
                if messages:
                    print(f"   ✅ Got {len(messages)} potential codes")
                    return messages

        print("   ⚠️  No SMS within timeout")
        return []

    def extract_code(self, message: SMSMessage) -> Optional[str]:
        """Extract verification code from SMS body."""
        patterns = [
            r'\b(\d{6})\b',  # 6-digit
            r'\b(\d{4})\b',  # 4-digit
            r'code[:\s]+(\d+)',  # "code: 123456"
            r'(\d{5,8})',   # 5-8 digit
        ]
        for p in patterns:
            m = re.search(p, message.body)
            if m:
                return m.group(1)
        return None

    def wait_for_code(self, timeout: int = 90) -> Optional[str]:
        """Wait for SMS and return first verification code found."""
        messages = self.check_inbox(timeout=timeout)
        for msg in messages:
            code = self.extract_code(msg)
            if code:
                return code
        return None


# Premium services (paid, more reliable, can be added later)
PREMIUM_SMS_SERVICES = {
    "sms-activate.org": "API key needed, $0.50+/number",
    "5sim.net": "API key needed, ~$0.10/number",
    "twilio.com": "Official, $1+/number, most reliable",
}


if __name__ == "__main__":
    print("Testing SMS service discovery...")
    svc = SMSService()
    try:
        num = svc.get_number("receive-smss.com", "USA")
        print(f"✅ Got number: {num.number}")
        print(f"   Country: {num.country}")
        print(f"   Service: {num.service}")
        print(f"   Inbox: {num.inbox_url}")
    except Exception as e:
        print(f"❌ Failed: {e}")
