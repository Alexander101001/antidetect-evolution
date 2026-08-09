#!/bin/bash
# 🔄 MASTER LOOP - Runs every 3 hours
# Monitors, improves, and grows the empire

set -e

cd /data/data/com.termux/files/home/.pi/skills/antidetect-stack/empire

echo "════════════════════════════════════════════════════════════"
echo "🔄 CYCLE START: $(date)"
echo "════════════════════════════════════════════════════════════"

# 1. Track analytics
echo ""
echo "📊 Step 1: Check analytics..."
python3 analytics_tracker.py

# 2. Find trending keywords
echo ""
echo "🔍 Step 2: Find new opportunities..."
python3 opportunity_finder.py

# 3. Generate new tools
echo ""
echo "🛠️ Step 3: Generate new tools..."
python3 tool_generator.py

# 4. Improve existing tools (based on data)
echo ""
echo "⚡ Step 4: Optimize tools..."
python3 optimizer.py

# 5. Submit to new directories
echo ""
echo "📢 Step 5: Submit to directories..."
python3 submit_to_dirs.py

# 6. Update affiliate links
echo ""
echo "💰 Step 6: Update affiliate links..."
python3 update_affiliates.py

# 7. Report
echo ""
echo "📱 Step 7: Send Telegram report..."
python3 send_report.py

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ CYCLE COMPLETE: $(date)"
echo "════════════════════════════════════════════════════════════"
