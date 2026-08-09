# 🛠️ Quick Commands Cheat Sheet

## Telegram
```bash
# Send simple message
TG="https://api.telegram.org/bot8504599651:AAHYxUmASoKtVpFfzDuduX_HIiBsuw5ozzc"
curl -s -X POST "$TG/sendMessage" -d "chat_id=890601506" -d "text=Hello"

# Send with formatting
curl -s -X POST "$TG/sendMessage" -d "chat_id=890601506" -d "parse_mode=HTML" -d "text=<b>Bold</b>"

# Send with buttons
curl -s -X POST "$TG/sendMessage" -d "chat_id=890601506" -d "text=..." -d 'reply_markup={"inline_keyboard":[[{"text":"Btn","callback_data":"x"}]]}'
```

## GitHub
```bash
# Check status
gh auth status

# Create repo
gh repo create NAME --public --description="desc"

# Trigger workflow
gh workflow run FILE.yml

# View runs
gh run list --limit 5
gh run view RUN_ID --log

# Push code
git add -A && git commit -m "msg" && git push
```

## Oracle Cloud
```bash
# Auth check (works)
proot-distro login ubuntu -- python3 -c "
import oci
config = oci.config.from_file('~/.oci/config')
identity = oci.identity.IdentityClient(config)
print(identity.get_user(config['user']).data.name)
"

# Frankfurt capacity: FULL
# Other regions: need tenancy subscription
```

## Hugging Face
```bash
# Auth check
curl -s "https://huggingface.co/api/whoami-v2" \
  -H "Authorization: Bearer $(cat ~/.cache/huggingface/token)"

# 8 Docker spaces, 5 paused due to quota
# Delete 3-4 unused to free CPU
```

## File Operations
```bash
# Create directory
mkdir -p /path/to/dir

# Edit file
edit file_path "old text" "new text"

# Search files
find /path -name "*.py"

# Count lines
wc -l file.py

# Disk usage
du -sh /path
```

## Process Management
```bash
# List running
ps aux | grep python

# Kill process
kill PID
pkill -f "pattern"

# Background
nohup command > log.txt 2>&1 &

# Run every X seconds
while true; do command; sleep 60; done
```

## Python
```bash
# Run script
python3 script.py

# With timeout
timeout 30 python3 script.py

# In background
python3 script.py &
```

## Network
```bash
# Test Tor
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Public IP
curl -s https://api.ipify.org

# Headers
curl -sI URL

# JSON pretty
curl -s URL | python3 -m json.tool
```

## Search
```bash
# Firecrawl (best for me)
firecrawl search "query" --limit 5

# In files
grep -r "text" /path
rg "text" /path

# Fast
ag "text" /path
```

## Cron Jobs
```bash
# Edit crontab
crontab -e

# Every 2 hours (free tier)
0 */2 * * * /path/to/script.sh

# Daily at 9am
0 9 * * * /path/to/script.sh

# Every 30 min
*/30 * * * * /path/to/script.sh
```

## Backup
```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz /path/

# List
ls -lah backup*

# Restore
tar -xzf backup.tar.gz -C /destination/
```
