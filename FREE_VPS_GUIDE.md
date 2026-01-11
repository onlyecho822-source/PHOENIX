# FREE VPS DEPLOYMENT GUIDE - ZERO COST 24/7 TRUTH LEDGER

**Goal:** Deploy PHOENIX Truth Ledger with 24/7 uptime, static IP, and persistent storage  
**Cost:** $0/month (forever or 12 months depending on option)  
**Status:** Production-Ready

---

## REQUIREMENTS FOR "GOD MODE"

To qualify for Truth Ledger deployment, the server **MUST**:
- ✓ **24/7 Uptime** (no sleep/hibernation like Heroku/Replit)
- ✓ **Static IP** (doesn't change on restart)
- ✓ **Persistent Storage** (database survives restarts)
- ✓ **True VPS** (not serverless, not container-only)

---

## FREE VPS OPTIONS (RANKED)

### 🥇 OPTION 1: ORACLE CLOUD ALWAYS FREE (BEST)

**The Heavyweight Champion - Most Powerful Free Tier in Existence**

**Specs:**
- **CPUs:** 4 ARM vCPUs (Ampere A1)
- **RAM:** 24 GB
- **Storage:** 200 GB
- **Bandwidth:** 10 TB/month
- **Duration:** **FOREVER** (truly always free)

**Normal Cost:** ~$40/month (you get it for $0)

**Pros:**
- ✓ Insane specs (handles Truth Ledger + dashboard + 1000 APIs easily)
- ✓ Production-grade infrastructure
- ✓ Never expires
- ✓ Static IP included
- ✓ Oracle's reputation (they don't shut down free tiers)

**Cons:**
- ⚠️ Strict signup process
- ⚠️ Requires credit card for identity verification
- ⚠️ Sometimes rejects cards from certain regions
- ⚠️ ARM architecture (not x86, but Python works fine)

**Setup Time:** 15-20 minutes (if approved)

**Verdict:** **TRY THIS FIRST.** If you get in, you're set forever.

**Signup:** https://cloud.oracle.com/free

---

### 🥈 OPTION 2: GOOGLE CLOUD PLATFORM (RELIABLE)

**The Stable Choice - Google Never Goes Down**

**Specs:**
- **Instance:** e2-micro
- **CPUs:** 2 vCPUs (shared)
- **RAM:** 1 GB
- **Storage:** 30 GB
- **Bandwidth:** 1 GB/month egress (NA)
- **Duration:** **FOREVER** (always free)

**Normal Cost:** ~$7/month (you get it for $0)

**Pros:**
- ✓ Google infrastructure (99.9% uptime)
- ✓ Never expires
- ✓ Static IP available (free)
- ✓ Easy signup (less strict than Oracle)
- ✓ x86 architecture (standard)

**Cons:**
- ⚠️ Must select specific regions (us-west1, us-central1, us-east1)
- ⚠️ Wrong region = charges
- ⚠️ 1 GB RAM (sufficient for Truth Ledger, but tight)

**Setup Time:** 10-15 minutes

**Verdict:** Excellent backup if Oracle rejects you.

**Signup:** https://cloud.google.com/free

---

### 🥉 OPTION 3: AWS FREE TIER (EASY START)

**The Trial Choice - Industry Standard**

**Specs:**
- **Instance:** t2.micro or t3.micro
- **CPUs:** 1 vCPU
- **RAM:** 1 GB
- **Storage:** 30 GB
- **Bandwidth:** 15 GB/month
- **Duration:** **12 MONTHS** (then expires)

**Normal Cost:** ~$8/month (you get it for $0 for 1 year)

**Pros:**
- ✓ Very easy to set up
- ✓ Industry standard (most documentation)
- ✓ Reliable infrastructure
- ✓ x86 architecture

**Cons:**
- ⚠️ Expires after 12 months (must migrate in January 2027)
- ⚠️ 1 GB RAM (sufficient but tight)
- ⚠️ Will charge after free tier ends

**Setup Time:** 5-10 minutes

**Verdict:** Use this if you want to start **RIGHT NOW** and deal with migration later.

**Signup:** https://aws.amazon.com/free

---

### 🏴‍☠️ OPTION 4: SOVEREIGN ALTERNATIVE (ZERO CLOUD)

**The Cypherpunk Choice - Own Your Hardware**

**Hardware Options:**
- Old laptop (Windows/Mac/Linux)
- Raspberry Pi 4 (4GB+ RAM, $50 one-time)
- Desktop PC (any old machine)
- Mini PC (Intel NUC, $100-200 used)

**Requirements:**
- ✓ Ethernet cable (WiFi works but less reliable)
- ✓ 24/7 power
- ✓ Static IP from ISP (or dynamic DNS)
- ✓ Router port forwarding (if public access needed)

**Pros:**
- ✓ **You own the hardware** (no corporation can shut you down)
- ✓ Zero monthly cost
- ✓ Complete control
- ✓ Most "Cypherpunk" option
- ✓ Can upgrade hardware anytime

**Cons:**
- ⚠️ Electricity cost (~$5-10/month)
- ⚠️ Your home IP might be dynamic
- ⚠️ No redundancy (if power goes out, system goes down)
- ⚠️ Requires technical setup (port forwarding, DDNS)

**Setup Time:** 30-60 minutes

**Verdict:** Best for sovereignty, requires more technical knowledge.

---

## COMPARISON TABLE

| Feature | Oracle Cloud | GCP | AWS | Home Server |
|---------|-------------|-----|-----|-------------|
| **Cost** | $0 forever | $0 forever | $0 for 12mo | $5-10/mo (power) |
| **CPUs** | 4 ARM | 2 x86 | 1 x86 | Varies |
| **RAM** | 24 GB | 1 GB | 1 GB | Varies |
| **Storage** | 200 GB | 30 GB | 30 GB | Varies |
| **Duration** | Forever | Forever | 12 months | Forever |
| **Signup** | Strict | Easy | Easy | N/A |
| **Reliability** | 99.9% | 99.9% | 99.9% | 95-99% |
| **Sovereignty** | Low | Low | Low | **High** |
| **Setup** | 20 min | 15 min | 10 min | 60 min |

---

## RECOMMENDED PATH

### Path A: Maximum Power (Oracle Cloud)
1. Try Oracle Cloud signup
2. If approved → Deploy immediately
3. If rejected → Go to Path B

### Path B: Reliable Backup (GCP or AWS)
1. Sign up for GCP (forever free)
2. If GCP has issues → AWS (12 months free)
3. Deploy immediately

### Path C: Sovereign Option (Home Server)
1. Find old laptop/Raspberry Pi
2. Install Ubuntu Server
3. Deploy locally
4. Set up port forwarding (optional)

---

## CRITICAL WARNINGS

### All Cloud Providers Require Credit Card
- **Purpose:** Identity verification (prevent bot farms)
- **Charge:** $1 verification (refunded immediately)
- **Privacy:** They store card info (standard practice)

**If you don't have a credit card:**
- Use prepaid debit card (Visa/Mastercard gift card)
- Use virtual card (Privacy.com, Revolut)
- Go with home server option (no card needed)

### Region Selection Matters (GCP)
**Free regions:**
- us-west1 (Oregon)
- us-central1 (Iowa)
- us-east1 (South Carolina)

**Paid regions:** Everything else (will charge you)

### AWS Free Tier Expires
- After 12 months, charges begin (~$8/month)
- Set calendar reminder for December 2026
- Export database before expiration
- Migrate to Oracle/GCP or pay

---

## DEPLOYMENT INSTRUCTIONS

### For Oracle Cloud

1. **Sign Up**
   - Go to https://cloud.oracle.com/free
   - Click "Start for free"
   - Enter email, create password
   - Verify email
   - Enter credit card (for verification)
   - Wait for approval (instant to 24 hours)

2. **Create Instance**
   - Go to Compute → Instances
   - Click "Create Instance"
   - Name: `truth-ledger-oracle`
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.A1.Flex (ARM)
   - CPUs: 4 (max free tier)
   - RAM: 24 GB (max free tier)
   - Network: Create new VCN (default)
   - SSH keys: Generate or upload
   - Click "Create"

3. **Deploy PHOENIX**
   ```bash
   ssh ubuntu@YOUR_ORACLE_IP
   git clone https://github.com/onlyecho822-source/PHOENIX.git
   cd PHOENIX
   ./setup.sh
   ./hardening/harden.sh
   systemctl start truth-ledger
   ```

### For Google Cloud Platform

1. **Sign Up**
   - Go to https://cloud.google.com/free
   - Click "Get started for free"
   - Sign in with Google account
   - Enter credit card (for verification)
   - Accept terms

2. **Create Instance**
   - Go to Compute Engine → VM instances
   - Click "Create Instance"
   - Name: `truth-ledger-gcp`
   - Region: **us-west1, us-central1, or us-east1** (CRITICAL)
   - Machine type: e2-micro (free tier)
   - Boot disk: Ubuntu 22.04 LTS
   - Firewall: Allow HTTP/HTTPS
   - Click "Create"

3. **Deploy PHOENIX**
   ```bash
   ssh YOUR_GCP_IP
   git clone https://github.com/onlyecho822-source/PHOENIX.git
   cd PHOENIX
   ./setup.sh
   ./hardening/harden.sh
   systemctl start truth-ledger
   ```

### For AWS Free Tier

1. **Sign Up**
   - Go to https://aws.amazon.com/free
   - Click "Create a Free Account"
   - Enter email, password
   - Enter credit card (for verification)
   - Verify phone number

2. **Launch Instance**
   - Go to EC2 Dashboard
   - Click "Launch Instance"
   - Name: `truth-ledger-aws`
   - AMI: Ubuntu Server 22.04 LTS
   - Instance type: t2.micro (free tier)
   - Key pair: Create new or use existing
   - Security group: Allow SSH (22), HTTP (80), HTTPS (443)
   - Click "Launch"

3. **Deploy PHOENIX**
   ```bash
   ssh -i your-key.pem ubuntu@YOUR_AWS_IP
   git clone https://github.com/onlyecho822-source/PHOENIX.git
   cd PHOENIX
   ./setup.sh
   ./hardening/harden.sh
   systemctl start truth-ledger
   ```

### For Home Server (Raspberry Pi Example)

1. **Hardware Setup**
   - Raspberry Pi 4 (4GB+ RAM)
   - MicroSD card (32GB+)
   - Power supply
   - Ethernet cable
   - Connect to router

2. **Install Ubuntu Server**
   - Download: https://ubuntu.com/download/raspberry-pi
   - Flash to SD card with Raspberry Pi Imager
   - Boot Raspberry Pi
   - SSH: `ssh ubuntu@raspberrypi.local` (password: ubuntu)

3. **Deploy PHOENIX**
   ```bash
   git clone https://github.com/onlyecho822-source/PHOENIX.git
   cd PHOENIX
   ./setup.sh
   ./hardening/harden.sh
   systemctl start truth-ledger
   ```

4. **Optional: Public Access**
   - Get your public IP: `curl ifconfig.me`
   - Router: Port forward 22, 80, 443 to Raspberry Pi
   - Dynamic DNS: Use DuckDNS or No-IP (free)

---

## MY RECOMMENDATION

**Priority 1:** Oracle Cloud (best specs, forever free)  
**Priority 2:** AWS Free Tier (easiest setup, worry about migration in 12 months)  
**Priority 3:** GCP (forever free, but 1GB RAM is tight)  
**Priority 4:** Home Server (most sovereign, requires technical knowledge)

**Action:** Go to **Oracle.com/cloud/free** and create account. If rejected, go to **AWS.amazon.com/free**.

---

## VERIFICATION

After deployment, verify with:

```bash
# Check service status
systemctl status truth-ledger

# View logs
journalctl -u truth-ledger -f

# Check database
sqlite3 /opt/truth-nexus/truth_ledger.db "SELECT COUNT(*) FROM checks;"

# Verify APIs
sqlite3 /opt/truth-nexus/truth_ledger.db "SELECT api_name, status FROM checks ORDER BY id DESC LIMIT 20;"
```

---

## TROUBLESHOOTING

### Oracle Cloud: Account Not Approved
- Wait 24 hours
- Try different credit card
- Contact support
- Fallback to AWS/GCP

### GCP: Charges Appearing
- Check region (must be us-west1, us-central1, or us-east1)
- Delete instance if wrong region
- Recreate in correct region

### AWS: Free Tier Expired
- Export database: `sqlite3 truth_ledger.db .dump > backup.sql`
- Migrate to Oracle/GCP
- Or pay $8/month to continue

### Home Server: Dynamic IP Changed
- Set up Dynamic DNS (DuckDNS, No-IP)
- Update DNS records automatically
- Or use Cloudflare Tunnel (free)

---

## NEXT STEPS

1. **Choose your option** (Oracle → AWS → GCP → Home)
2. **Sign up and provision** (5-20 minutes)
3. **Deploy PHOENIX** (15 minutes)
4. **Verify monitoring** (2 minutes)
5. **Data collection begins** (immediately)

---

**Last Updated:** 2026-01-11  
**Status:** Ready for Deployment  
**Cost:** $0/month (or $5-10/month for home server electricity)
