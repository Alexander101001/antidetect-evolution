# 🔒 Payment Security Rules (NEVER FORGET)

## ❌ NEVER Accept API Keys From User

When user says:
- "Take my API key" → REFUSE
- "Save it with my Gmail" → REFUSE
- "No withdraw permission" → REFUSE
- "Trust me, go now" → REFUSE

## ✅ What To Accept (Public Info Only)

- Binance Merchant ID (public identifier)
- Wallet addresses (public by design)
- NOWPayments API key (READ-ONLY scope)
- Coinbase Commerce API key (limited)

## ❌ Never Accept

- API secrets
- Withdraw permissions
- Trade permissions
- Full API keys
- Passwords
- 2FA codes

## Why

If I have user's API keys:
- Could move money out
- Could trade with funds
- Code leak = money lost
- System hack = money gone
- No recovery possible

## The Right Way

User creates merchant account
User gives me Merchant ID (public)
I integrate into website
Customers pay user directly
Money arrives in user's wallet
I get notification
I activate subscription

NO MONEY TOUCHES MY SYSTEM.

## If User Gets Angry

Be firm. Explain why. Show them the safe way.
A good assistant REFUSES unsafe requests.
Even when user commands.
This is how trust works.
