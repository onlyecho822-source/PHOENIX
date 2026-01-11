# ⚡ Truth Ledger

**Independent API Status Verification with Cryptographic Proof**

Truth Ledger is an immutable monitoring system that verifies API uptime claims by directly testing endpoints and comparing against official status pages. Every check is cryptographically hashed and chained, creating an irreversible record of truth.

## The Problem

- API providers claim "99.99% uptime" but measure selectively
- Official status pages show "all systems operational" during outages
- No independent verification of uptime claims
- Historical data can be rewritten
- Users have no proof when services fail

## The Solution

Truth Ledger creates an **immutable baseline** by:

1. **Direct Testing:** Checks 20 critical APIs every hour
2. **Cryptographic Hashing:** Each check is SHA-256 hashed and chained
3. **Multi-Source Verification:** Compares measurements vs. official claims
4. **Discrepancy Detection:** Flags variances >2% automatically
5. **Public Proof:** All data stored in immutable SQLite database

**Value Proposition:** "Anyone can write the code; nobody can buy last month's data if they didn't record it."

---

## Features

### ✓ Core Monitoring
- Monitors 20 critical APIs (Stripe, OpenAI, GitHub, AWS, etc.)
- Hourly checks with configurable intervals
- Response time measurement
- Status code tracking
- Timeout and error detection

### ✓ Immutable Ledger
- SQLite database with cryptographic hashing
- Blockchain-like chain of checks
- Each check links to previous via SHA-256
- Database cannot be modified retroactively
- Integrity verification built-in

### ✓ Discrepancy Detection
- Compares measurements vs. official status pages
- Flags variances >2%
- Severity classification (low, medium, high, critical)
- Automated daily reports
- Cryptographic proof of discrepancies

### ✓ Production Ready
- Systemd service for continuous operation
- Automated daily backups
- Comprehensive logging
- Error handling and retry logic
- Low resource usage (~50 MB RAM)

---

## Quick Start

### Prerequisites

- Ubuntu 22.04+ / Debian 11+ / Raspberry Pi OS
- Python 3.8+
- 1 GB RAM
- 10 GB storage

### Installation (5 minutes)

```bash
# 1. Upload files to your server
scp -r truth-ledger/ root@YOUR_SERVER:/root/

# 2. SSH to server
ssh root@YOUR_SERVER

# 3. Run setup script
cd /root/truth-ledger
chmod +x setup.sh
sudo ./setup.sh

# 4. Verify it's running
systemctl status truth-ledger
```

That's it! Truth Ledger is now monitoring 20 APIs every hour.

---

## Architecture

```
truth_ledger.py          → Main monitoring script
database.py              → Immutable SQLite operations
api_sources.py           → API configurations
reveal_truth.py          → Discrepancy detection
dashboard.html           → Public status page
setup.sh                 → Automated deployment
```

### Database Schema

```sql
checks (
    id, timestamp, api_name, endpoint, status,
    response_time_ms, status_code, source,
    check_hash, previous_hash  ← Blockchain-like chain
)

discrepancies (
    timestamp, api_name, claimed_status, actual_status,
    claimed_uptime, measured_uptime, variance_percent,
    proof_hashes, severity
)

sources (
    api_name, source_type, source_url,
    verification_method, reliability_score
)
```

### Cryptographic Verification

Each check is hashed using:
```python
SHA256(
    timestamp + api_name + endpoint + status +
    response_time + status_code + previous_hash
)
```

This creates a chain where modifying any historical check breaks all subsequent hashes.

---

## Usage

### Monitor APIs

```bash
# Continuous monitoring (default: every hour)
python3 truth_ledger.py

# Run once and exit
python3 truth_ledger.py --once

# Custom interval (30 minutes)
python3 truth_ledger.py --interval 1800

# View statistics
python3 truth_ledger.py --stats

# Verify chain integrity
python3 truth_ledger.py --verify
```

### Detect Discrepancies

```bash
# Check all APIs for discrepancies
python3 reveal_truth.py

# Check specific API
python3 reveal_truth.py --api stripe

# Analyze last 7 days
python3 reveal_truth.py --hours 168

# Generate report
python3 reveal_truth.py --report my_report.md
```

### Database Queries

```bash
# View recent checks
sqlite3 truth_ledger.db \
  "SELECT timestamp, api_name, status, response_time_ms 
   FROM checks ORDER BY id DESC LIMIT 10;"

# Get uptime for API
sqlite3 truth_ledger.db \
  "SELECT api_name, 
          COUNT(*) as total,
          SUM(CASE WHEN status='up' THEN 1 ELSE 0 END) as up,
          ROUND(100.0 * SUM(CASE WHEN status='up' THEN 1 ELSE 0 END) / COUNT(*), 2) as uptime
   FROM checks 
   WHERE api_name='stripe';"

# Find all discrepancies
sqlite3 truth_ledger.db \
  "SELECT * FROM discrepancies ORDER BY timestamp DESC;"
```

---

## Monitored APIs

| API | Endpoint | Frequency |
|-----|----------|-----------|
| Stripe | `api.stripe.com` | Every hour |
| OpenAI | `api.openai.com` | Every hour |
| GitHub | `api.github.com` | Every hour |
| AWS | `status.aws.amazon.com` | Every hour |
| Vercel | `api.vercel.com` | Every hour |
| Cloudflare | `api.cloudflare.com` | Every hour |
| Binance | `api.binance.com` | Every hour |
| CoinGecko | `api.coingecko.com` | Every hour |
| Alpha Vantage | `www.alphavantage.co` | Every hour |
| IEX Cloud | `cloud.iexapis.com` | Every hour |
| Finnhub | `finnhub.io` | Every hour |
| Twitter/X | `api.twitter.com` | Every hour |
| Reddit | `www.reddit.com` | Every hour |
| Google Cloud | `status.cloud.google.com` | Every hour |
| Azure | `status.azure.com` | Every hour |
| Heroku | `api.heroku.com` | Every hour |
| Railway | `backboard.railway.app` | Every hour |
| Render | `api.render.com` | Every hour |
| Supabase | `api.supabase.com` | Every hour |
| PlanetScale | `api.planetscale.com` | Every hour |

---

## Business Model

### Phase 1: Silent Observer (Days 1-30)
- Run monitoring system
- Collect baseline data
- Build irreplaceable historical record

### Phase 2: First Strike (First Major Outage)
- Publish report with cryptographic proof
- Demonstrate value: "We saw it when they said it didn't happen"
- Gain authority as independent witness

### Phase 3: Watchdog Brand (Months 3-6)
- Expand to verify AI wrappers, decentralized services
- **"Sponsor the Truth"** model: Companies pay $999/month to be monitored
- Status symbol for reliable companies

### Phase 4: Oracle Protocol (Year 1+)
- Move ledger to blockchain (Arweave/similar)
- Smart contracts trigger on your data
- Example: "If uptime < 99.9%, refund 10%"
- Your ledger becomes the judge

### Revenue Tiers

| Tier | Price | Features |
|------|-------|----------|
| Basic | $99/month | Access to ledger, email alerts |
| Premium | $499/month | Custom monitoring, API access |
| Enterprise | $2,999/month | Oracle integration, SLA enforcement |
| Sponsor | $999/month | Company added to monitoring, badge |

**Year 1 Projection:** $150,000 revenue

---

## Deployment Options

### VPS (Recommended)
- **DigitalOcean:** $6/month, 5-minute setup
- **Linode:** $6/month, similar performance
- **AWS Lightsail:** $5/month, more complex

### Raspberry Pi
- **Cost:** $35-50 one-time
- **Power:** 5W, ~$5/year electricity
- **Reliability:** Depends on home internet

### Cloud Free Tiers
- AWS, GCP, Azure free for 12 months
- Good for testing

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.**

---

## Maintenance

### Automated (via cron)
- **Daily 3 AM:** Discrepancy check
- **Daily 4 AM:** Database backup

### Manual
- **Weekly:** Review logs, check disk space
- **Monthly:** Run `reveal_truth.py`, rotate old backups

### Monitoring
```bash
# Check service status
systemctl status truth-ledger

# View live logs
journalctl -u truth-ledger -f

# Get statistics
python3 truth_ledger.py --stats
```

---

## Example Output

### Monitoring
```
2026-01-11 12:00:00 - INFO - Starting check of 20 APIs...
2026-01-11 12:00:01 - INFO - ✓ stripe: up (145ms, 200) hash=a7f3d2e1...
2026-01-11 12:00:02 - INFO - ✓ openai: up (523ms, 200) hash=b8e4c3f2...
2026-01-11 12:00:03 - INFO - ✓ github: up (89ms, 200) hash=c9f5d4e3...
...
2026-01-11 12:00:20 - INFO - Completed check of 20 APIs
```

### Statistics
```
==================================
TRUTH LEDGER - MONITORING STATISTICS
==================================
Total Checks: 43,284
APIs Monitored: 20
Discrepancies Found: 3
Database Size: 52.4 MB
Genesis: 2026-01-01T00:00:00
Last Backup: 2026-01-11T04:00:00

API Uptime (Last 24 Hours):
----------------------------------
✓ stripe            99.98% (  24 checks,    145ms avg)
✓ openai            99.95% (  24 checks,    523ms avg)
✓ github           100.00% (  24 checks,     89ms avg)
⚠ twitter           98.75% (  24 checks,    567ms avg)
==================================
```

### Discrepancy Report
```markdown
# TRUTH LEDGER - DISCREPANCY REPORT

**Generated:** 2026-01-11T03:00:00
**Discrepancies Found:** 1

---

## 🚨 TWITTER/X API

**Severity:** HIGH
**Variance:** 7.25%

### The Claim vs. The Truth
- **They Claimed:** All systems operational
- **We Measured:** 92.75% uptime
- **Based On:** 24 checks over 24 hours

### Cryptographic Proof
1. `a7f3d2e1b4c5f8a9...`
2. `b8e4c3f2a5d6e9b1...`
3. `c9f5d4e3b6a7f1c2...`
...

**Evidence:** [https://api.twitterstat.us](https://api.twitterstat.us)
```

---

## Technical Details

### Performance
- **Memory:** ~50 MB RAM
- **CPU:** <1% average
- **Disk:** ~50 MB/month database growth
- **Network:** ~100 KB/hour bandwidth

### Dependencies
```
requests==2.31.0        # HTTP client
beautifulsoup4==4.12.3  # HTML parsing
lxml==5.1.0             # XML/HTML parser
```

### Security
- Runs as non-root user `truth-ledger`
- No external dependencies in production
- Database stored locally only
- No credentials required for most APIs

---

## Roadmap

### Phase 1 ✓ (Complete)
- [x] Core monitoring system
- [x] Immutable database
- [x] 20 API integrations
- [x] Automated deployment
- [x] Documentation

### Phase 2 (Month 1)
- [ ] Public dashboard (GitHub Pages)
- [ ] Email alerts on discrepancies
- [ ] First discrepancy report published
- [ ] GitHub automated backups

### Phase 3 (Month 2-3)
- [ ] Business entity registration
- [ ] Landing page
- [ ] First 10 beta customers
- [ ] "Sponsor the Truth" launch

### Phase 4 (Month 6-12)
- [ ] Blockchain migration (Arweave)
- [ ] Smart contract integration
- [ ] Oracle protocol
- [ ] Enterprise features

---

## FAQ

**Q: How is this different from status.io or similar services?**  
A: We're independent and immutable. Status pages can be edited retroactively. Our database cannot.

**Q: Why blockchain-like hashing instead of actual blockchain?**  
A: Phase 1 uses SQLite for simplicity and speed. Phase 4 migrates to blockchain for full decentralization.

**Q: How do you verify official status pages?**  
A: We scrape status pages and compare text. Looking for "operational", "outage", "degraded" indicators.

**Q: What if an API blocks your monitoring?**  
A: We respect rate limits and use standard endpoints. We're checking, not attacking.

**Q: Can I add custom APIs?**  
A: Yes! Edit `api_sources.py` and add your configuration.

**Q: How much data will this generate?**  
A: ~50 MB/month with 20 APIs checked hourly. ~600 MB/year.

**Q: What happens if the VPS goes down?**  
A: You lose that time period's data. Solution: Multi-region deployment or local Raspberry Pi backup.

---

## Contributing

Truth Ledger is open source. Contributions welcome:

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

**Areas needing help:**
- Additional API integrations
- Dashboard improvements
- Blockchain migration
- Documentation

---

## License

MIT License - See LICENSE file

---

## Support

- **Documentation:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues:** GitHub Issues
- **Email:** your-email@example.com

---

## The Philosophy

> "Anyone can write the code; nobody can buy last month's data if they didn't record it."

Truth Ledger isn't about fancy features or dashboards. It's about:

1. **Starting today** - Every hour we delay is data lost
2. **The baseline** - Irreplaceable historical record
3. **Independence** - No one can rewrite what we've recorded
4. **Proof** - Cryptographic verification, not trust

**The silence is where the value grows.**

---

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** January 11, 2026

**Start monitoring: `./setup.sh`**
