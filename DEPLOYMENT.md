# Truth Ledger - Deployment Guide

Complete step-by-step instructions for deploying Truth Ledger.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Deployment Options](#deployment-options)
3. [VPS Deployment (Recommended)](#vps-deployment)
4. [Raspberry Pi Deployment](#raspberry-pi-deployment)
5. [Verification](#verification)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

**Minimum Requirements:**
- Ubuntu 22.04 / Debian 11+ / Raspberry Pi OS
- 1 GB RAM
- 10 GB storage
- Python 3.8+
- Internet connection

**Installation Time:** 5-10 minutes

---

## Deployment Options

### Option A: DigitalOcean VPS ($6/month)
- **Pros:** Reliable, easy setup, good uptime
- **Cons:** Monthly cost
- **Recommended for:** Production deployment

### Option B: Raspberry Pi ($35-50 one-time)
- **Pros:** One-time cost, low power usage
- **Cons:** Need to maintain hardware, home internet reliability
- **Recommended for:** Learning, testing, home deployment

### Option C: AWS/Azure/GCP Free Tier
- **Pros:** Free for 12 months
- **Cons:** More complex setup, requires credit card
- **Recommended for:** Temporary testing

---

## VPS Deployment (Recommended)

### Step 1: Create VPS

#### DigitalOcean (Easiest)

1. Go to [DigitalOcean](https://www.digitalocean.com)
2. Create account
3. Click "Create" → "Droplets"
4. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic - $6/month (1 GB RAM)
   - **Datacenter:** Closest to you
   - **Authentication:** SSH keys (generate if needed)
5. Click "Create Droplet"
6. Wait 1 minute for creation
7. Copy the IP address (e.g., `123.45.67.89`)

#### Alternative Providers

**Linode:** Similar to DigitalOcean, also $6/month  
**Vultr:** Same pricing, good performance  
**AWS Lightsail:** $5/month but more complex

### Step 2: Connect to VPS

```bash
# On your local machine (Mac/Linux)
ssh root@YOUR_VPS_IP

# On Windows, use PuTTY or Windows Terminal
```

### Step 3: Upload Truth Ledger Files

**Option A: Direct Upload (if you have files locally)**

```bash
# On your local machine
scp -r truth-ledger/ root@YOUR_VPS_IP:/root/
```

**Option B: Clone from GitHub (once you've pushed)**

```bash
# On VPS
git clone https://github.com/YOUR_USERNAME/truth-ledger.git
cd truth-ledger
```

**Option C: Manual Copy-Paste**

1. On VPS: `mkdir -p /root/truth-ledger && cd /root/truth-ledger`
2. For each file, run: `nano FILENAME` and paste content
3. Save with Ctrl+X, Y, Enter

### Step 4: Run Setup Script

```bash
cd /root/truth-ledger
chmod +x setup.sh
sudo ./setup.sh
```

The script will:
- Install Python and dependencies
- Create `truth-ledger` system user
- Set up virtual environment
- Install Python packages
- Create systemd service
- Set up cron jobs
- Start monitoring

**Expected output:**
```
==================================
Installation Complete!
==================================

Service Status:
● truth-ledger.service - Truth Ledger API Monitor
     Loaded: loaded (/etc/systemd/system/truth-ledger.service; enabled)
     Active: active (running) since...
```

### Step 5: Verify It's Working

```bash
# Check service status
systemctl status truth-ledger

# View live logs
journalctl -u truth-ledger -f

# Check database was created
ls -lh /opt/truth-ledger/truth_ledger.db

# View stats (wait 1 hour for first check)
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --stats
```

**Success indicators:**
- Service shows "active (running)"
- Logs show "✓ stripe: up (145ms, 200)"
- Database file exists and grows over time

---

## Raspberry Pi Deployment

### Step 1: Set Up Raspberry Pi

1. Flash Raspberry Pi OS (64-bit) to SD card
2. Enable SSH: Create empty file named `ssh` in boot partition
3. Insert SD card and power on
4. Find Pi's IP: `ping raspberrypi.local` or check router

### Step 2: Connect

```bash
ssh pi@raspberrypi.local
# Default password: raspberry (change this!)
```

### Step 3: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 4: Upload and Install

Same as VPS Step 3 and 4 above.

### Step 5: Configure Auto-Start

The setup script already configured systemd, so monitoring will survive reboots.

```bash
# Test reboot persistence
sudo reboot

# After reboot, SSH back in and check
systemctl status truth-ledger
```

---

## Verification

### Check System is Monitoring

```bash
# View recent checks
sudo -u truth-ledger sqlite3 /opt/truth-ledger/truth_ledger.db \
  "SELECT timestamp, api_name, status, response_time_ms FROM checks ORDER BY id DESC LIMIT 10;"
```

Expected output:
```
2026-01-11T12:00:00|stripe|up|145
2026-01-11T12:00:00|openai|up|523
2026-01-11T12:00:00|github|up|89
...
```

### Verify Hash Chain Integrity

```bash
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --verify
```

Expected: `✓ All hash chains verified successfully`

### Check Stats After 24 Hours

```bash
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --stats
```

Expected:
```
==================================
TRUTH LEDGER - MONITORING STATISTICS
==================================
Total Checks: 480
APIs Monitored: 20
Discrepancies Found: 0
Database Size: 2.3 MB

API Uptime (Last 24 Hours):
----------------------------------
✓ stripe           99.95% (  24 checks,    145ms avg)
✓ openai           99.90% (  24 checks,    523ms avg)
...
```

---

## Maintenance

### Daily Tasks (Automated)

These run automatically via cron:
- **3 AM:** Discrepancy check (generates report)
- **4 AM:** Database backup

### Weekly Tasks (Manual)

```bash
# Check service health
systemctl status truth-ledger

# Review logs
journalctl -u truth-ledger --since "1 week ago"

# Check disk space
df -h /opt/truth-ledger
```

### Monthly Tasks

```bash
# Review all discrepancies
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 reveal_truth.py

# Check backup size
du -sh /opt/truth-ledger/backups/

# Rotate old backups (keep last 30 days)
cd /opt/truth-ledger/backups
find . -name "*.db" -mtime +30 -delete
```

---

## Maintenance Commands

### View Logs

```bash
# Real-time logs
journalctl -u truth-ledger -f

# Last 100 lines
journalctl -u truth-ledger -n 100

# Logs from today
journalctl -u truth-ledger --since today

# Logs with errors only
journalctl -u truth-ledger -p err
```

### Database Operations

```bash
# Database size
ls -lh /opt/truth-ledger/truth_ledger.db

# Number of checks
sudo -u truth-ledger sqlite3 /opt/truth-ledger/truth_ledger.db \
  "SELECT COUNT(*) FROM checks;"

# Backup database
sudo -u truth-ledger cp /opt/truth-ledger/truth_ledger.db \
  /opt/truth-ledger/backups/manual_backup_$(date +%Y%m%d).db
```

### Service Management

```bash
# Restart service
systemctl restart truth-ledger

# Stop service
systemctl stop truth-ledger

# Start service
systemctl start truth-ledger

# Disable auto-start
systemctl disable truth-ledger

# Enable auto-start
systemctl enable truth-ledger
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
journalctl -u truth-ledger -n 50

# Test script manually
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --once

# Check Python dependencies
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/pip list
```

### No Checks Being Recorded

```bash
# Verify database exists
ls -l /opt/truth-ledger/truth_ledger.db

# Check permissions
ls -l /opt/truth-ledger/

# Run single check manually
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --once
```

### Network Errors

```bash
# Test internet connectivity
ping -c 3 8.8.8.8

# Test DNS
ping -c 3 google.com

# Test API endpoint manually
curl -I https://api.stripe.com/v1/charges
```

### Database Corrupted

```bash
# Verify integrity
cd /opt/truth-ledger
sudo -u truth-ledger sqlite3 truth_ledger.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
sudo systemctl stop truth-ledger
sudo -u truth-ledger cp /opt/truth-ledger/backups/truth_ledger_YYYYMMDD.db \
  /opt/truth-ledger/truth_ledger.db
sudo systemctl start truth-ledger
```

---

## Next Steps

After 24 hours of data collection:

1. **Run discrepancy check:**
   ```bash
   cd /opt/truth-ledger
   sudo -u truth-ledger ./venv/bin/python3 reveal_truth.py
   ```

2. **Review report:**
   ```bash
   cat /opt/truth-ledger/discrepancy_report.md
   ```

3. **Set up public dashboard:**
   - Upload `dashboard.html` to GitHub Pages
   - Or serve with nginx (see Advanced Setup)

4. **Configure GitHub backups:**
   - Create private GitHub repo
   - Add deploy key
   - Set up automated push

---

## Advanced Setup

### Serve Dashboard with Nginx

```bash
# Install nginx
sudo apt install nginx

# Copy dashboard
sudo cp /opt/truth-ledger/dashboard.html /var/www/html/index.html

# Access at http://YOUR_VPS_IP
```

### Set Up GitHub Automated Backups

```bash
# On VPS
cd /opt/truth-ledger
git init
git remote add origin git@github.com:YOUR_USERNAME/truth-ledger-data.git

# Add to crontab (sudo crontab -e -u truth-ledger)
0 5 * * * cd /opt/truth-ledger && git add truth_ledger.db && git commit -m "Backup $(date +\%Y-\%m-\%d)" && git push origin main
```

---

## Security Notes

1. **Change default passwords** (especially on Raspberry Pi)
2. **Set up firewall:**
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw enable
   ```
3. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
4. **Use SSH keys instead of passwords**
5. **Don't expose database publicly**

---

## Support

If you encounter issues:

1. Check logs: `journalctl -u truth-ledger -n 100`
2. Verify integrity: `python3 truth_ledger.py --verify`
3. Test manually: `python3 truth_ledger.py --once`
4. Check GitHub issues
5. Contact: your-email@example.com

---

**You're now running Truth Ledger!**

The silent observer is watching. The baseline is growing. The truth is being recorded.
