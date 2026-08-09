# Oracle VM Options (Free Tier)

## Available Right Now:
✅ VM.Standard.A1.Flex (ARM Ampere) - Always Free

## Total Free Resources:
- 4 OCPUs
- 24 GB RAM
- 200 GB storage
- 10 TB bandwidth/month

## Best VM Configurations:

### Option 1: ONE BIG MACHINE
- 1 VM: 4 OCPU + 24 GB RAM
- Best for: Evolution engine, heavy compute, ML
- Use: Database, big processing jobs

### Option 2: TWO BALANCED
- VM1: 2 OCPU + 12 GB (main worker)
- VM2: 2 OCPU + 12 GB (backup/redundancy)
- Best for: Always-on + failover

### Option 3: FOUR SMALL
- VM1: 1 OCPU + 6 GB (jobs scraping)
- VM2: 1 OCPU + 6 GB (job applying)
- VM3: 1 OCPU + 6 GB (affiliate content)
- VM4: 1 OCPU + 6 GB (evolution engine)
- Best for: Parallel work, separation

### Option 4: HYBRID
- VM1: 2 OCPU + 12 GB (main - evolution)
- VM2: 1 OCPU + 6 GB (jobs scraper)
- VM3: 1 OCPU + 6 GB (backup)

## Recommendation:
**Option 1** (1 VM with all 24 GB) for now
- Simplest to manage
- Most flexibility
- Can split later if needed
