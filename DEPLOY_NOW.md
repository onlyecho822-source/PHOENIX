# DEPLOY NOW - IMMEDIATE DEPLOYMENT GUIDE

**Goal:** Start collecting Truth Ledger data TODAY  
**Time:** 10-15 minutes  
**Cost:** $0

---

## TWO DEPLOYMENT OPTIONS

### OPTION 1: LAPTOP DEPLOYMENT (TODAY - 10 MINUTES)
**Deploy on your Windows laptop as a 24/7 background service**

### OPTION 2: CLOUD VPS (WHEN READY - 5 MINUTES)
**Zero-touch deployment to Oracle Cloud, AWS, GCP, or DigitalOcean**

---

## OPTION 1: LAPTOP DEPLOYMENT

### Requirements
- Windows 10/11
- Python 3.8+ installed
- Administrator access
- 500 MB free disk space

### Step 1: Install Python (if not already installed)
1. Download: https://www.python.org/downloads/
2. Run installer
3. **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify: Open PowerShell and run `python --version`

### Step 2: Download Deployment Script
Open PowerShell and run:
```powershell
# Navigate to Downloads
cd $env:USERPROFILE\Downloads

# Download deployment script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/onlyecho822-source/PHOENIX/main/deploy_windows_service.ps1" -OutFile "deploy_windows_service.ps1"
```

### Step 3: Deploy as Windows Service
Run PowerShell **as Administrator**:
```powershell
# Navigate to Downloads
cd $env:USERPROFILE\Downloads

# Run deployment
.\deploy_windows_service.ps1
```

**What happens:**
1. Creates `C:\TruthLedger` directory
2. Clones PHOENIX repository
3. Installs Python dependencies
4. Creates Windows Service
5. Starts monitoring automatically

**Time:** 5-10 minutes

### Step 4: Verify Deployment
```powershell
# Check service status
Get-Service TruthLedger

# View logs
Get-Content C:\TruthLedger\truth_ledger.log -Tail 20 -Wait

# Check database (after 1 hour)
cd C:\TruthLedger\PHOENIX
python -c "import sqlite3; conn=sqlite3.connect('truth_ledger.db'); print(f'Total checks: {conn.execute(\"SELECT COUNT(*) FROM checks\").fetchone()[0]}'); conn.close()"
```

### Laptop Service Management
```powershell
# Stop service
Stop-Service TruthLedger

# Start service
Start-Service TruthLedger

# View status
Get-Service TruthLedger

# Uninstall (if needed)
.\deploy_windows_service.ps1 -Uninstall
```

---

## OPTION 2: CLOUD VPS DEPLOYMENT

### Requirements
- VPS account (Oracle Cloud, AWS, GCP, or DigitalOcean)
- 5 minutes

### Supported Providers
- ✅ Oracle Cloud (4 CPUs, 24 GB RAM - FREE FOREVER)
- ✅ AWS EC2 (1 CPU, 1 GB RAM - FREE 12 MONTHS)
- ✅ Google Cloud (2 CPUs, 1 GB RAM - FREE FOREVER)
- ✅ DigitalOcean (1 CPU, 1 GB RAM - $6/month)
- ✅ Vultr, Linode, Hetzner (all compatible)

### Step 1: Get Cloud-Init Script
The script is in your PHOENIX repository:
```
PHOENIX/cloud-init.yaml
```

Or download directly:
```bash
curl -O https://raw.githubusercontent.com/onlyecho822-source/PHOENIX/main/cloud-init.yaml
```

### Step 2: Create VPS with Cloud-Init

#### Oracle Cloud
1. Go to https://cloud.oracle.com
2. Compute → Instances → Create Instance
3. Name: `truth-ledger`
4. Image: Ubuntu 22.04
5. Shape: VM.Standard.A1.Flex (4 CPUs, 24 GB RAM)
6. **Advanced Options → Management**
7. **Paste entire cloud-init.yaml contents**
8. Create Instance
9. Wait 10 minutes
10. SSH in: `ssh ubuntu@YOUR_IP`
11. Verify: `/root/verify.sh`

#### AWS EC2
1. Go to AWS Console → EC2
2. Launch Instance
3. Name: `truth-ledger`
4. AMI: Ubuntu Server 22.04 LTS
5. Instance type: t2.micro (free tier)
6. **Advanced Details → User Data**
7. **Paste entire cloud-init.yaml contents**
8. Launch
9. Wait 10 minutes
10. SSH in: `ssh -i your-key.pem ubuntu@YOUR_IP`
11. Verify: `sudo /root/verify.sh`

#### Google Cloud Platform
1. Go to GCP Console → Compute Engine
2. Create Instance
3. Name: `truth-ledger`
4. Region: **us-west1, us-central1, or us-east1** (FREE TIER)
5. Machine type: e2-micro
6. Boot disk: Ubuntu 22.04 LTS
7. **Management → Automation**
8. **Paste entire cloud-init.yaml contents**
9. Create
10. Wait 10 minutes
11. SSH in: `ssh YOUR_IP`
12. Verify: `sudo /root/verify.sh`

#### DigitalOcean
1. Go to DigitalOcean → Droplets
2. Create Droplet
3. Image: Ubuntu 22.04 LTS
4. Plan: Basic ($6/month)
5. **Advanced Options → User Data**
6. **Paste entire cloud-init.yaml contents**
7. Create Droplet
8. Wait 10 minutes
9. SSH in: `ssh root@YOUR_IP`
10. Verify: `/root/verify.sh`

### Step 3: Verify Deployment
After 10 minutes, SSH into your VPS and run:
```bash
# Check service status
systemctl status truth-ledger

# View logs
journalctl -u truth-ledger -f

# Run verification script
/root/verify.sh
```

**Expected output:**
```
=== TRUTH LEDGER STATUS ===
● truth-ledger.service - PHOENIX Truth Ledger Monitor
   Active: active (running)

=== DATABASE STATS ===
total_checks
10

=== RECENT CHECKS ===
2026-01-11 08:00:00|stripe|UP|200
2026-01-11 08:00:05|openai|UP|200
...
```

---

## MONITORING YOUR DEPLOYMENT

### Daily Checks (Both Options)

#### Windows Laptop
```powershell
# View logs
Get-Content C:\TruthLedger\truth_ledger.log -Tail 50

# Check database
cd C:\TruthLedger\PHOENIX
python monitoring\7day_dashboard.py
```

#### Cloud VPS
```bash
# View logs
journalctl -u truth-ledger -n 50

# Check database
cd /opt/truth-nexus
python3 /root/PHOENIX/monitoring/7day_dashboard.py
```

### 7-Day Dashboard
After deployment, run the monitoring dashboard daily:

**Windows:**
```powershell
cd C:\TruthLedger\PHOENIX
python monitoring\7day_dashboard.py
```

**Linux:**
```bash
cd /opt/truth-nexus
python3 /root/PHOENIX/monitoring/7day_dashboard.py
```

**Output:**
- Service status
- Data summary
- API breakdown
- Recent issues
- Chain integrity verification
- 7-day readiness check

---

## TROUBLESHOOTING

### Laptop Deployment

**"Python not found"**
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH"

**"Service won't start"**
- Check logs: `Get-Content C:\TruthLedger\stderr.log`
- Verify Python: `python --version`
- Reinstall: `.\deploy_windows_service.ps1 -Uninstall` then redeploy

**"Access denied"**
- Run PowerShell as Administrator
- Right-click PowerShell → "Run as administrator"

### Cloud VPS Deployment

**"Service not running after 10 minutes"**
```bash
# Check cloud-init logs
cat /var/log/cloud-init-output.log

# Check service logs
journalctl -u truth-ledger -n 100

# Restart service
systemctl restart truth-ledger
```

**"Database empty after 1 hour"**
```bash
# Check if service is running
systemctl status truth-ledger

# Check logs for errors
journalctl -u truth-ledger -n 50

# Verify network connectivity
curl -I https://status.stripe.com/api/v2/status.json
```

---

## NEXT STEPS

### After 24 Hours
1. Run monitoring dashboard
2. Verify data collection (should have ~240 checks)
3. Check chain integrity

### After 7 Days
1. Run full verification: `python monitoring/7day_dashboard.py`
2. Should have ~10,080 data points
3. Chain integrity verified
4. Ready for technical partnership activation

### Migration (Laptop → Cloud)
When you're ready to move from laptop to cloud:

1. **Export database:**
   ```powershell
   # Windows
   cd C:\TruthLedger\PHOENIX
   sqlite3 truth_ledger.db .dump > backup.sql
   ```

2. **Deploy to cloud** (Option 2)

3. **Import database:**
   ```bash
   # Linux
   cd /opt/truth-nexus
   sqlite3 truth_ledger.db < backup.sql
   ```

4. **Stop laptop service:**
   ```powershell
   Stop-Service TruthLedger
   ```

---

## SUMMARY

**Laptop Deployment:**
- Time: 10 minutes
- Cost: $0
- Pros: Immediate, no credit card, sovereign
- Cons: Requires laptop to stay on

**Cloud Deployment:**
- Time: 5 minutes (after VPS provisioning)
- Cost: $0-6/month
- Pros: 24/7 uptime, redundant, professional
- Cons: Requires VPS account

**Recommendation:**
1. Deploy on laptop TODAY (10 min)
2. Deploy to cloud TOMORROW (when you have VPS)
3. Migrate data (5 min)
4. Keep laptop as backup

---

**Every hour delayed = 20 lost data points that can never be recovered.**

**Deploy now. Start collecting truth.**
