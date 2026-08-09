# 🤗 Hugging Face Space Guide

## Live URL
https://huggingface.co/spaces/AlexanderGreater90/evolution-engine

## What's Deployed
- Streamlit dashboard
- Stealth system monitor
- Evolution engine metrics
- Real-time stats

## How to View
1. Open the URL in any browser
2. First visit: 30-60 second cold start
3. After: instant load

## What It Shows
- 🛡️ Stealth protection status
- 📊 Action counter
- 💰 Revenue projections (after data)
- 🔧 Tool network status

## Free Tier Limits
- 16 GB RAM
- Shared CPU
- Sleeps after 48h inactivity
- Cold starts take 30-60s

## To Keep It Active
- Visit at least every 2 days
- Or upgrade to paid tier

## To Update
Run from Termux:
```bash
cd ~/.pi/skills/antidetect-stack
python3 -c "from huggingface_hub import HfApi; api=HfApi(); api.upload_file('deploy/hf-space/app.py','app.py',repo_id='AlexanderGreater90/evolution-engine',repo_type='space')"
```
