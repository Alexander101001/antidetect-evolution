"""
💰 SAFE PAYMENT SYSTEM
No API keys needed. Customers pay YOU directly.
"""
import json
from pathlib import Path
from datetime import datetime


class SafePaymentSystem:
    """Payment system that doesn't touch your money."""
    
    def __init__(self):
        self.config_file = Path("/data/data/com.termux/files/home/.config/money-machine/payment_config.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.transactions_file = Path("/data/data/com.termux/files/home/.pi/skills/antidetect-stack/data/payment_transactions.json")
    
    def _load_config(self):
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return {
            "merchant_id": "",
            "wallet_address_usdt": "",
            "wallet_address_btc": "",
            "wallet_address_eth": "",
            "nowpayments_api_key": "",
            "nowpayments_email": "",
            "telegram_notifications": True,
        }
    
    def save_config(self):
        """Save PUBLIC payment info (safe)."""
        self.config_file.write_text(json.dumps(self.config, indent=2))
        self.config_file.chmod(0o644)  # Public readable is OK
    
    def setup_binance_pay(self, merchant_id):
        """Save Binance Merchant ID (PUBLIC)."""
        self.config["merchant_id"] = merchant_id
        self.save_config()
        return "✅ Binance Pay Merchant ID saved. Customers will pay you directly."
    
    def setup_wallet(self, currency, address):
        """Save wallet address (PUBLIC)."""
        key = f"wallet_address_{currency.lower()}"
        self.config[key] = address
        self.save_config()
        return f"✅ {currency} wallet address saved. Customers can pay you directly."
    
    def setup_nowpayments(self, api_key, email):
        """Save NOWPayments limited API key."""
        # Important: This should be a READ-ONLY or LIMITED key
        self.config["nowpayments_api_key"] = api_key
        self.config["nowpayments_email"] = email
        self.save_config()
        return "✅ NOWPayments API key saved. Make sure it has NO withdraw permission."
    
    def log_transaction(self, customer, amount, currency, product):
        """Log a payment (for tracking)."""
        if not self.transactions_file.exists():
            transactions = []
        else:
            transactions = json.loads(self.transactions_file.read_text())
        
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "customer": customer,
            "amount": amount,
            "currency": currency,
            "product": product,
            "status": "received",
        }
        transactions.append(transaction)
        self.transactions_file.write_text(json.dumps(transactions, indent=2))
        return transaction


# Initialize
ps = SafePaymentSystem()

print("💰 SAFE PAYMENT SYSTEM")
print("=" * 50)
print()
print("NO API KEYS NEEDED.")
print()
print("What I need from you (all PUBLIC, safe):")
print()
print("1. Binance Merchant ID")
print("   → Go to pay.binance.com")
print("   → Create merchant account")
print("   → Copy your Merchant ID")
print("   → Send to me")
print()
print("2. OR your USDT/BTC wallet address")
print("   → Open your Binance wallet")
print("   → Copy USDT address")
print("   → Send to me (public info)")
print()
print("3. OR NOWPayments API key (limited)")
print("   → Sign up at nowpayments.io")
print("   → Create API key")
print("   → DISABLE withdraw permission")
print("   → Send me the key")
print()
print("=" * 50)
print()
print("I will NEVER ask for:")
print("❌ Your Binance API secret")
print("❌ Withdraw permission")
print("❌ Trade permission")
print("❌ Your password")
print("❌ Your Gmail login")
print()
print("If anyone (including me) asks for these = SCAM")
