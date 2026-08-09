# Create Oracle VM - Step by Step

## Option 1: Web Console (EASIEST)
1. Go to: https://cloud.oracle.com/compute/instances/create?region=eu-frankfurt-1
2. Login with mra494956@gmail.com
3. Click "Create Instance"
4. Name: hasan-worker-vm
5. Image: Ubuntu 22.04 (or latest LTS)
6. Shape: VM.Standard.A1.Flex
7. OCPUs: 4
8. Memory: 24 GB
9. Networking: Create new VCN + subnet (default)
10. Assign public IP: YES
11. SSH key: Paste contents of ~/.ssh/id_ed25519.pub
12. Click "Create"

## Option 2: Fix OCI SDK
The crc32c module fails to compile on Termux ARM.
Workaround: Run on Ubuntu proot (where it works).

## Option 3: Use REST API
Once VM is created, I can manage it via SSH.

## After VM is created:
I will:
1. SSH into the VM
2. Install Docker + Python
3. Deploy evolution engine
4. Set up cron jobs
5. Start 24/7 autonomous work

VM specs:
- 4 OCPUs (ARM Ampere)
- 24 GB RAM
- 200 GB storage
- 10 TB bandwidth/month
- COST: $0/month (free forever)
