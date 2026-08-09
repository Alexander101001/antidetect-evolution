"""Stripe integration for AI Writer Pro."""
import os
import stripe

# When you set up Stripe, replace these
STRIPE_PUBLISHABLE_KEY = "pk_live_YOUR_KEY_HERE"  # Public, OK to share
STRIPE_SECRET_KEY = "sk_live_YOUR_KEY_HERE"      # PRIVATE, never share

stripe.api_key = STRIPE_SECRET_KEY

PRICES = {
    "pro": "price_YOUR_PRO_PRICE_ID",
    "business": "price_YOUR_BUSINESS_PRICE_ID",
}

def create_checkout_session(plan="pro", success_url=None, cancel_url=None):
    """Create a Stripe checkout session."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": PRICES.get(plan, PRICES["pro"]),
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url or "https://yourdomain.com/success",
            cancel_url=cancel_url or "https://yourdomain.com/cancel",
        )
        return session.url
    except Exception as e:
        return None

# Setup instructions:
SETUP_STEPS = """
🚀 STRIPE SETUP (10 minutes):

1. Go to stripe.com → Sign up (free)
2. Verify email + phone
3. Go to Developers → API Keys
4. Copy your keys:
   - Publishable key (pk_live_...) → Frontend
   - Secret key (sk_live_...) → Backend (NEVER share!)
5. Create Products:
   - Pro plan ($5/mo recurring)
   - Business plan ($29/mo recurring)
6. Copy Price IDs → Put in PRICES dict above
7. Deploy this code to Render/Railway
8. Add checkout button to your landing page

DONE. Money flows directly to your Stripe → your bank.
"""
print(SETUP_STEPS)
