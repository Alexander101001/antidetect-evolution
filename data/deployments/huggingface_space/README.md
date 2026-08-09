---
title: Evolution Worker
emoji: 🧬
colorFrom: green
colorTo: purple
sdk: docker
pinned: false
---

# Evolution Worker

Self-evolving autonomous enterprise worker. Runs evolution cycles
continuously and reports results back to the central orchestrator.

## Configuration

Set these secrets in your Space:
- `TELEGRAM_BOT_TOKEN` - For reporting
- `TELEGRAM_CHAT_ID` - Where to send reports
- `CENTRAL_ORCHESTRATOR_URL` - Optional: report to central system
