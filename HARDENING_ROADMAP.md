# HARDENING ROADMAP - TRUTH NEXUS FORTRESS

**Date:** January 11, 2026  
**Status:** ACTIVE  
**Method:** AC/DC (Audit → Construct → Deploy → Chain)

---

## AC/DC METHOD STATUS

### A - AUDIT (Strategic Pivot)
**Principle:** From extraction to verification  
**Implementation:** ✓ Monitoring public endpoints (not scraping)  
**Status:** **COMPLETE**

### C - CONSTRUCT (Enterprise Architecture)
**Principle:** Enterprise-grade code quality  
**Implementation:** ✓ Dataclasses, nanoseconds, separation of concerns  
**Status:** **COMPLETE**

### D - DEPLOY (Autonomous Persistence)
**Principle:** Self-healing infrastructure  
**Implementation:** ✓ Systemd service, auto-restart, journald logging  
**Status:** **READY** (awaiting VPS)

### C - CHAIN (Cryptographic Integrity)
**Principle:** Immutable proof  
**Implementation:** ✓ SHA-256 hash chains, append-only ledger  
**Status:** **COMPLETE**

---

## HARDENING GAPS IDENTIFIED

**Total Gaps:** 15  
**Critical (High Risk):** 5  
**Important (Medium Risk):** 5  
**Enhancement (Low Risk):** 5

### PRIORITY 1: SECURITY - Firewall Configuration
**Risk:** HIGH  
**Gap:** No firewall rules configured  
**Solution:** UFW firewall (SSH only, block all else)  
**Time:** 10 minutes  
**Cost:** $0

### PRIORITY 2: SECURITY - Root User Deployment
**Risk:** MEDIUM  
**Gap:** Running as root user  
**Solution:** Create dedicated 'truthledger' user with limited permissions  
**Time:** 15 minutes  
**Cost:** $0

### PRIORITY 3: SECURITY - Rate Limiting
**Risk:** LOW  
**Gap:** No rate limiting on API calls  
**Solution:** Implement exponential backoff for failed APIs  
**Time:** 30 minutes  
**Cost:** $0

### PRIORITY 4: RELIABILITY - Single Point of Failure
**Risk:** HIGH  
**Gap:** One VPS only  
**Solution:** Multi-region deployment (3 VPS: NYC, London, Singapore)  
**Time:** 60 minutes  
**Cost:** $18/month (3 × $6)

### PRIORITY 5: RELIABILITY - Database Replication
**Risk:** HIGH  
**Gap:** No database backups  
**Solution:** Real-time database sync to backup VPS + S3  
**Time:** 45 minutes  
**Cost:** $1/month (S3 storage)

### PRIORITY 6: RELIABILITY - Health Monitoring
**Risk:** MEDIUM  
**Gap:** No watchdog service  
**Solution:** Watchdog that monitors main service and alerts on failure  
**Time:** 30 minutes  
**Cost:** $0

### PRIORITY 7: OBSERVABILITY - Metrics Dashboard
**Risk:** LOW  
**Gap:** No real-time metrics  
**Solution:** Prometheus + Grafana for visualization  
**Time:** 90 minutes  
**Cost:** $0 (same VPS)

### PRIORITY 8: OBSERVABILITY - Alerting System
**Risk:** MEDIUM  
**Gap:** No automated alerts  
**Solution:** Email/SMS/Slack alerts for discrepancies >5%  
**Time:** 45 minutes  
**Cost:** $0 (email), $10/month (SMS via Twilio)

### PRIORITY 9: OBSERVABILITY - Public Status Page
**Risk:** LOW  
**Gap:** Dashboard not publicly accessible  
**Solution:** Deploy dashboard.html to public URL with nginx  
**Time:** 20 minutes  
**Cost:** $0

### PRIORITY 10: VERIFICATION - External Verification API
**Risk:** MEDIUM  
**Gap:** No third-party verification  
**Solution:** Public REST API for hash chain verification  
**Time:** 60 minutes  
**Cost:** $0

### PRIORITY 11: VERIFICATION - Chain Integrity Checker
**Risk:** HIGH  
**Gap:** No automated chain verification  
**Solution:** Script that verifies entire chain every 6 hours  
**Time:** 45 minutes  
**Cost:** $0

### PRIORITY 12: SCALABILITY - Dynamic API Configuration
**Risk:** LOW  
**Gap:** 20 APIs hardcoded  
**Solution:** JSON config file for add/remove without restart  
**Time:** 30 minutes  
**Cost:** $0

### PRIORITY 13: SCALABILITY - Parallel API Checks
**Risk:** MEDIUM  
**Gap:** Sequential checks (slow)  
**Solution:** Async/parallel checks with asyncio (20x faster)  
**Time:** 60 minutes  
**Cost:** $0

### PRIORITY 14: LEGAL - Terms of Service
**Risk:** MEDIUM  
**Gap:** No TOS for public data  
**Solution:** Create TOS document  
**Time:** 30 minutes  
**Cost:** $0 (or $500 for lawyer review)

### PRIORITY 15: LEGAL - Privacy Policy
**Risk:** LOW  
**Gap:** No privacy policy  
**Solution:** Create privacy policy (we don't collect user data)  
**Time:** 20 minutes  
**Cost:** $0

---

## HARDENING ROADMAP

### PHASE 1: IMMEDIATE (DEPLOY + HARDEN - 24 HOURS)

#### TRACK A: DEPLOYMENT (Priority 1)
- [ ] Deploy to VPS (DigitalOcean $6/month)
- [ ] Verify 20 APIs monitoring
- [ ] Confirm database creation
- [ ] Check hash chain integrity

**Owner:** YOU + MANUS  
**Time:** 15 minutes  
**Cost:** $6/month

#### TRACK B: SECURITY HARDENING (Priority 1-3)
- [ ] Configure UFW firewall (SSH only)
- [ ] Create dedicated 'truthledger' user
- [ ] Implement rate limiting with exponential backoff
- [ ] Disable root SSH login
- [ ] Set up fail2ban for brute force protection

**Owner:** MANUS (scripts) + YOU (execution)  
**Time:** 60 minutes  
**Cost:** $0

#### TRACK C: RELIABILITY (Priority 4-6)
- [ ] Deploy to 2 additional VPS (multi-region)
- [ ] Set up database replication (rsync every 5 min)
- [ ] Create watchdog service (monitors main service)
- [ ] S3 backup automation (daily)

**Owner:** MANUS + YOU  
**Time:** 120 minutes  
**Cost:** $19/month ($18 VPS + $1 S3)

#### TRACK D: VERIFICATION (Priority 10-11)
- [ ] Build chain integrity checker
- [ ] Schedule integrity checks (every 6 hours)
- [ ] Create public verification API
- [ ] Generate verification reports

**Owner:** MANUS  
**Time:** 105 minutes  
**Cost:** $0

---

### PHASE 2: WEEK 1 (OBSERVABILITY + SCALABILITY)

#### TRACK A: OBSERVABILITY (Priority 7-9)
- [ ] Deploy Prometheus metrics exporter
- [ ] Set up Grafana dashboard
- [ ] Configure email alerts (discrepancies >5%)
- [ ] Configure SMS alerts (critical failures)
- [ ] Deploy public status page with nginx

**Owner:** MANUS  
**Time:** 155 minutes  
**Cost:** $10/month (SMS via Twilio)

#### TRACK B: SCALABILITY (Priority 12-13)
- [ ] Implement dynamic API configuration (JSON)
- [ ] Convert to async/parallel checks (asyncio)
- [ ] Add 80 more APIs (20 → 100)
- [ ] Implement priority tiers (5min/1hr/6hr)

**Owner:** MANUS  
**Time:** 180 minutes  
**Cost:** $0

#### TRACK C: LEGAL (Priority 14-15)
- [ ] Write Terms of Service
- [ ] Write Privacy Policy
- [ ] Add LICENSE file (MIT or Apache 2.0)
- [ ] Create CONTRIBUTING.md

**Owner:** MANUS  
**Time:** 50 minutes  
**Cost:** $0 (or $500 for lawyer review)

---

### PHASE 3: MONTH 1 (INSTITUTIONAL GRADE)

#### TRACK A: AUDIT READINESS
- [ ] External security audit (penetration testing)
- [ ] Code review by third party
- [ ] Compliance documentation (SOC 2 prep)
- [ ] Incident response plan

**Owner:** YOU + External Auditors  
**Time:** 40 hours  
**Cost:** $5,000-15,000

#### TRACK B: BUSINESS HARDENING
- [ ] Register business entity (LLC)
- [ ] Set up business bank account
- [ ] Professional liability insurance
- [ ] Legal review of TOS/Privacy

**Owner:** YOU  
**Time:** 8 hours  
**Cost:** $1,500-3,000

#### TRACK C: TECHNICAL EXCELLENCE
- [ ] 99.9% uptime SLA
- [ ] <100ms API response time
- [ ] Zero data loss guarantee
- [ ] Public transparency reports

**Owner:** MANUS  
**Time:** 80 hours  
**Cost:** $0 (optimization)

---

## IMMEDIATE NEXT STEPS (PRIORITIZED)

### STEP 1: DEPLOY TO VPS (15 MINUTES)
**Action:** Provision DigitalOcean droplet + run deployment script  
**Owner:** YOU (human) + MANUS (guidance)  
**Blocker:** None (ready to execute)  
**Value:** Data collection begins immediately

### STEP 2: SECURITY HARDENING (30 MINUTES)
**Action:** Configure firewall, create dedicated user, disable root SSH  
**Owner:** MANUS (scripts) + YOU (execution)  
**Blocker:** VPS must be deployed first  
**Value:** Prevent unauthorized access

### STEP 3: CHAIN INTEGRITY CHECKER (45 MINUTES)
**Action:** Build verification script that checks entire hash chain  
**Owner:** MANUS (code generation)  
**Blocker:** None (can build now)  
**Value:** Cryptographic proof of data integrity

### STEP 4: MULTI-REGION DEPLOYMENT (60 MINUTES)
**Action:** Deploy to 2 more VPS (NYC, London, Singapore)  
**Owner:** YOU (provision) + MANUS (automation)  
**Blocker:** Primary VPS must be stable  
**Value:** Geographic redundancy + consensus verification

### STEP 5: DATABASE REPLICATION (30 MINUTES)
**Action:** Set up rsync between 3 VPS + S3 backup  
**Owner:** MANUS (scripts) + YOU (S3 credentials)  
**Blocker:** Multi-region deployment complete  
**Value:** Zero data loss guarantee

---

## DECISION POINT

### OPTION A: DEPLOY NOW, HARDEN LATER
**Approach:** Deploy to VPS immediately, add security incrementally  
**Risk:** Vulnerable during Phase 1  
**Reward:** Data collection starts NOW  
**Time to Production:** 15 minutes

### OPTION B: HARDEN FIRST, DEPLOY SECURE
**Approach:** Build all security features first, deploy fully hardened  
**Risk:** Delay data collection 2-4 hours  
**Reward:** Production-grade from day 1  
**Time to Production:** 4 hours

### OPTION C: PARALLEL EXECUTION (RECOMMENDED)
**Approach:** Deploy minimal viable system NOW, build hardening simultaneously  
**Risk:** Complexity in coordination  
**Reward:** Best of both worlds  
**Time to Production:** 15 minutes (data collection), 2 hours (fully hardened)

---

## RECOMMENDED EXECUTION PLAN

**CHOICE: OPTION C (PARALLEL EXECUTION)**

**Reason:** Data collection is time-sensitive. Security is important but can be added incrementally. Deploy minimal system now, harden as we go.

### Timeline

**T+0 (Now):**
- YOU: Provision VPS (5 min)
- MANUS: Prepare deployment scripts

**T+5:**
- MANUS: Deploy Truth Ledger (10 min)
- **DATA COLLECTION BEGINS**

**T+15:**
- MANUS: Build security hardening scripts (30 min)
- Truth Ledger collecting data in background

**T+45:**
- YOU: Execute hardening scripts (15 min)
- MANUS: Build multi-region deployment (45 min)

**T+60:**
- YOU: Provision 2 more VPS (10 min)

**T+70:**
- MANUS: Deploy to all 3 regions (15 min)

**T+85:**
- MANUS: Set up database replication (30 min)

**T+115:**
- MANUS: Build chain integrity checker (45 min)

**T+160 (2 hours 40 minutes):**
- **FULLY HARDENED SYSTEM OPERATIONAL**
- 3 VPS in different regions
- Database replication active
- Security hardened
- Chain integrity verified
- **Data loss: 0 hours** (collection started at T+15)

---

## COST BREAKDOWN

### Phase 1 (Immediate - 24 Hours)
- Primary VPS: $6/month
- 2 Backup VPS: $12/month
- S3 Storage: $1/month
- **Total: $19/month**

### Phase 2 (Week 1)
- SMS Alerts (Twilio): $10/month
- **Total: $29/month**

### Phase 3 (Month 1)
- Security Audit: $5,000-15,000 (one-time)
- Business Setup: $1,500-3,000 (one-time)
- **Ongoing: $29/month**

### Annual Cost
- Infrastructure: $348/year
- One-time Setup: $6,500-18,000
- **Total Year 1: $6,848-18,348**

---

## SUCCESS METRICS

### Phase 1 (24 Hours)
- ✓ 480+ data points collected (20 APIs × 24 hours)
- ✓ Zero downtime
- ✓ Hash chain integrity verified
- ✓ Security hardened

### Phase 2 (Week 1)
- ✓ 3,360+ data points collected
- ✓ 100 APIs monitored
- ✓ Public dashboard live
- ✓ Alerting operational

### Phase 3 (Month 1)
- ✓ 14,400+ data points collected
- ✓ 99.9% uptime achieved
- ✓ External audit passed
- ✓ First paying customers

---

**END OF HARDENING ROADMAP**

*Last Updated: 2026-01-11 07:45 UTC*  
*Next Review: After VPS deployment*
