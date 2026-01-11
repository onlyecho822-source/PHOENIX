# TRUTH LEDGER - QUICK START GUIDE

**Time to Deploy:** 10 minutes  
**Cost:** $6/month (DigitalOcean) or $35-50 one-time (Raspberry Pi)

---

## CRITICAL: WHY START NOW

Every hour you wait = 20 lost data points  
After 24 hours delay = 480 irreplaceable checks lost  
**The baseline is time-sensitive. Start today.**

---

## OPTION A: DIGITALOCEAN VPS (RECOMMENDED)

### Step 1: Create Droplet (2 minutes)

1. Go to https://www.digitalocean.com
2. Create account (if new, get $200 credit)
3. Click "Create" → "Droplets"
4. Settings:
   - Image: **Ubuntu 22.04 LTS**
   - Plan: **Basic - $6/month** (1 GB RAM)
   - Datacenter: Closest to you
   - Authentication: **Password** (easier) or SSH keys
   - Hostname: `truth-ledger`
5. Click "Create Droplet"
6. Copy the IP address (e.g., `123.45.67.89`)

### Step 2: Upload Files (3 minutes)

**Download all files above** from this chat to a folder called `truth-ledger/`

Then on your local machine:

```bash
# Mac/Linux
scp -r truth-ledger/ root@YOUR_VPS_IP:/root/

# Windows (use WinSCP or similar)
# Or manually: connect with PuTTY, then create files
```

### Step 3: Deploy (2 minutes)

```bash
# SSH to your VPS
ssh root@YOUR_VPS_IP

# Navigate to folder
cd /root/truth-ledger

# Run setup
chmod +x setup.sh
./setup.sh
```

### Step 4: Verify (1 minute)

```bash
# Check it's running
systemctl status truth-ledger

# Should show: "active (running)"
```

**DONE! System is now monitoring 20 APIs every hour.**

---

## OPTION B: RASPBERRY PI (ONE-TIME $35-50)

### Step 1: Flash SD Card

1. Download Raspberry Pi Imager
2. Choose: Raspberry Pi OS (64-bit)
3. Flash to SD card (16 GB minimum)
4. Before ejecting: Create empty file named `ssh` in boot partition

### Step 2: Boot and Connect

1. Insert SD card, connect ethernet, power on
2. Find IP: `ping raspberrypi.local` or check router
3. SSH: `ssh pi@raspberrypi.local` (password: `raspberry`)
4. Change password: `passwd`

### Step 3: Upload and Deploy

Same as DigitalOcean steps 2 & 3 above.

---

## WHAT HAPPENS NEXT

### Immediately
- Service starts monitoring 20 APIs
- Checks run every hour
- Results logged to SQLite database
- Each check cryptographically hashed

### After 1 Hour
You can check stats:
```bash
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --stats
```

### After 24 Hours
Run discrepancy check:
```bash
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 reveal_truth.py
```

### After 30 Days
You have **irreplaceable baseline data**:
- 14,400 API checks
- 720 checks per API
- Cryptographic proof chain
- Historical record no one else has

---

## VERIFICATION CHECKLIST

After deployment, verify these:

✓ Service is running:
```bash
systemctl status truth-ledger
# Should show "active (running)"
```

✓ Database exists:
```bash
ls -lh /opt/truth-ledger/truth_ledger.db
# Should show file size > 0
```

✓ Logs show checks:
```bash
journalctl -u truth-ledger -n 20
# Should show "✓ stripe: up (145ms, 200)"
```

✓ Chain integrity verified:
```bash
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --verify
# Should show "✓ All hash chains verified successfully"
```

---

## TROUBLESHOOTING

### Problem: Service won't start

```bash
# Check logs for error
journalctl -u truth-ledger -n 50

# Try manual run
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --once
```

### Problem: "Permission denied"

```bash
# Fix ownership
sudo chown -R truth-ledger:truth-ledger /opt/truth-ledger

# Restart service
sudo systemctl restart truth-ledger
```

### Problem: No checks being recorded

```bash
# Verify internet connectivity
ping -c 3 google.com

# Check if database is writable
cd /opt/truth-ledger
sudo -u truth-ledger touch test.txt
rm test.txt
```

---

## USEFUL COMMANDS

```bash
# View real-time logs
journalctl -u truth-ledger -f

# Restart service
systemctl restart truth-ledger

# Check stats
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --stats

# Run discrepancy check
cd /opt/truth-ledger
sudo -u truth-ledger ./venv/bin/python3 reveal_truth.py

# Backup database manually
sudo -u truth-ledger cp /opt/truth-ledger/truth_ledger.db ~/truth_ledger_backup.db
```

---

## WHAT TO DO IN 24 HOURS

1. **Check stats:**
   ```bash
   cd /opt/truth-ledger
   sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --stats
   ```
   
   Expected: 480+ checks, all APIs with 20-24 checks each

2. **Run discrepancy check:**
   ```bash
   sudo -u truth-ledger ./venv/bin/python3 reveal_truth.py
   ```
   
   Expected: Report generated (hopefully no discrepancies yet)

3. **Verify chain integrity:**
   ```bash
   sudo -u truth-ledger ./venv/bin/python3 truth_ledger.py --verify
   ```
   
   Expected: "✓ All hash chains verified successfully"

4. **Set up GitHub backups** (optional):
   - Create private GitHub repo
   - Add automated daily backup script

---

## NEXT STEPS (WEEK 1)

- [ ] Deploy dashboard.html to GitHub Pages
- [ ] Set up email alerts for discrepancies
- [ ] Document your deployment process
- [ ] Join Discord/community (once created)
- [ ] Share your first week stats

---

## COST BREAKDOWN

### VPS Option
- DigitalOcean: $6/month = $72/year
- Alternative: Linode, Vultr, AWS Lightsail ($5-6/month)

### Raspberry Pi Option
- Hardware: $35-50 one-time
- SD Card: $10
- Power: ~$5/year electricity
- **Total Year 1:** ~$50-65

### Free Option (Temporary)
- AWS/GCP/Azure free tier (12 months)
- After 12 months: switch to paid or Raspberry Pi

---

## SUPPORT

If stuck:
1. Check DEPLOYMENT.md for detailed instructions
2. View logs: `journalctl -u truth-ledger -n 100`
3. Open GitHub issue (once repo public)

---

## REMEMBER

**The value isn't in the code. The value is in the data you're collecting RIGHT NOW.**

Every hour you delay = 20 lost data points you can never get back.

**Start today. Review while it runs.**

---

**Status:** Ready to Deploy  
**Time Required:** 10 minutes  
**Urgency:** Critical (baseline is time-sensitive)

**Deploy command:** `./setup.sh`
