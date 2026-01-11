# TRUTH NEXUS HARDENING KIT

**Status:** Production-Ready  
**Method:** AC/DC (Audit → Construct → Deploy → Chain)

---

## OVERVIEW

This directory contains security hardening and operational scripts for the PHOENIX Truth Ledger system. These scripts implement Priorities 1-11 from the Hardening Roadmap.

---

## SCRIPTS

### 1. `harden.sh` - Security Automation
**Priority:** 1-2 (HIGH)  
**Purpose:** System hardening (firewall, user isolation, fail2ban)

**Features:**
- Creates dedicated `truthledger` service user
- Configures UFW firewall (SSH, HTTP, HTTPS only)
- Secures shared memory
- Installs and enables fail2ban

**Usage:**
```bash
chmod +x harden.sh
sudo ./harden.sh
```

**Time:** 2-3 minutes  
**Requires:** Root access

---

### 2. `watchdog.py` - Health Monitoring
**Priority:** 6 (MEDIUM)  
**Purpose:** Monitor database writes and restart service if stalled

**Features:**
- Checks database modification time every 5 minutes
- Restarts service if no writes for 1 hour
- Logs all health checks

**Usage:**
```bash
# Run in background
nohup python3 watchdog.py > watchdog.log 2>&1 &

# Or as systemd service (recommended)
sudo cp watchdog.service /etc/systemd/system/
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

**Configuration:**
- `DB_PATH`: Path to truth_ledger.db
- `CHECK_INTERVAL`: Seconds between checks (default: 300)
- `THRESHOLD_SECONDS`: Alert threshold (default: 3600)

---

### 3. `verify_integrity.py` - Chain Verification
**Priority:** 11 (HIGH)  
**Purpose:** Verify cryptographic hash chain integrity

**Features:**
- Scans all API chains for broken links
- Detects tampering attempts
- Exit code 0 = valid, 1 = compromised

**Usage:**
```bash
# Manual verification
python3 verify_integrity.py

# Daily cron job (recommended)
# Add to crontab: 0 3 * * * /usr/bin/python3 /opt/truth-nexus/verify_integrity.py
```

**Time:** 1-2 seconds per 1000 records

---

### 4. `multi_region_deploy.sh` - Geographic Redundancy
**Priority:** 4 (HIGH)  
**Purpose:** Deploy to 3 VPS in different regions

**Features:**
- Automated deployment to NYC, London, Singapore
- Clones repository, runs setup, hardens system
- Verifies each deployment

**Usage:**
```bash
# Set VPS IP addresses
export NYC_IP="64.23.xxx.xxx"
export LON_IP="159.89.xxx.xxx"
export SGP_IP="128.199.xxx.xxx"

# Deploy
chmod +x multi_region_deploy.sh
./multi_region_deploy.sh
```

**Requirements:**
- SSH access to all 3 VPS
- SSH keys configured (no password prompts)

**Time:** 10-15 minutes total

---

## EXECUTION ORDER

### Phase 1: Single VPS (15 minutes)
1. Deploy Truth Ledger to primary VPS
2. Run `harden.sh` for security
3. Start `watchdog.py` for monitoring
4. Schedule `verify_integrity.py` daily

### Phase 2: Multi-Region (60 minutes)
1. Provision 2 additional VPS (London, Singapore)
2. Run `multi_region_deploy.sh`
3. Verify all 3 regions operational

### Phase 3: Database Replication (30 minutes)
1. Set up rsync between regions (every 5 min)
2. Configure S3 backup (daily)
3. Test restore procedure

---

## SECURITY FEATURES

### Firewall (UFW)
- Default: Deny all incoming
- Allow: SSH (22), HTTP (80), HTTPS (443)
- Rate limiting on SSH

### User Isolation
- Dedicated `truthledger` user (no shell)
- Restricted permissions
- Isolated directory `/opt/truth-nexus`

### Fail2Ban
- Brute force protection
- Automatic IP banning
- SSH attack prevention

### Chain Integrity
- Cryptographic verification
- Tamper detection
- Daily automated checks

---

## MONITORING

### Health Checks
- Database write monitoring (every 5 min)
- Service restart on failure
- Log all events

### Integrity Checks
- Hash chain verification (daily)
- Broken link detection
- Alert on tampering

### Multi-Region Consensus
- 3 independent VPS
- Geographic redundancy
- Cross-verification capability

---

## COST BREAKDOWN

**Infrastructure:**
- Primary VPS: $6/month (DigitalOcean)
- 2 Backup VPS: $12/month
- S3 Storage: $1/month
- **Total: $19/month**

**One-time:**
- Security audit: $5,000-15,000 (optional)
- Business setup: $1,500-3,000 (optional)

---

## TROUBLESHOOTING

### Firewall locked me out
```bash
# From VPS console (not SSH):
sudo ufw disable
sudo ufw allow ssh
sudo ufw enable
```

### Service won't start
```bash
# Check logs
journalctl -u truth-ledger -n 50

# Check permissions
ls -la /opt/truth-nexus

# Restart
sudo systemctl restart truth-ledger
```

### Chain verification failed
```bash
# Check database
sqlite3 /opt/truth-nexus/truth_ledger.db "SELECT COUNT(*) FROM checks;"

# Manual verification
python3 verify_integrity.py

# If compromised, restore from backup
```

---

## NEXT STEPS

1. **Deploy to VPS** - Run setup.sh on primary VPS
2. **Harden System** - Run harden.sh
3. **Start Monitoring** - Run watchdog.py
4. **Multi-Region** - Deploy to 3 regions
5. **Database Replication** - Set up rsync + S3

---

**Last Updated:** 2026-01-11  
**Version:** 1.0.0  
**Status:** Production-Ready
