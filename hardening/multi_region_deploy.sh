#!/bin/bash
# TRUTH NEXUS MULTI-REGION DEPLOYMENT
# Priority 4: Geographic Redundancy

set -e

echo "🌍 MULTI-REGION DEPLOYMENT INITIATING..."

# Configuration
REGIONS=("nyc" "lon" "sgp")
VPS_IPS=("$NYC_IP" "$LON_IP" "$SGP_IP")

# Verify IPs are set
if [ -z "$NYC_IP" ] || [ -z "$LON_IP" ] || [ -z "$SGP_IP" ]; then
    echo "❌ ERROR: Set environment variables: NYC_IP, LON_IP, SGP_IP"
    exit 1
fi

echo "Target VPS:"
echo "  NYC: $NYC_IP"
echo "  LON: $LON_IP"
echo "  SGP: $SGP_IP"

# Deploy to each region
for i in "${!REGIONS[@]}"; do
    REGION="${REGIONS[$i]}"
    IP="${VPS_IPS[$i]}"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "DEPLOYING TO: $REGION ($IP)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 1. Clone repository
    echo "[1/5] Cloning PHOENIX repository..."
    ssh root@$IP "cd /root && git clone https://github.com/onlyecho822-source/PHOENIX.git || (cd PHOENIX && git pull)"
    
    # 2. Run setup
    echo "[2/5] Running setup.sh..."
    ssh root@$IP "cd /root/PHOENIX && chmod +x setup.sh && ./setup.sh"
    
    # 3. Harden system
    echo "[3/5] Running hardening..."
    ssh root@$IP "cd /root/PHOENIX/hardening && chmod +x harden.sh && ./harden.sh"
    
    # 4. Start service
    echo "[4/5] Starting truth-ledger service..."
    ssh root@$IP "systemctl enable truth-ledger && systemctl start truth-ledger"
    
    # 5. Verify
    echo "[5/5] Verifying deployment..."
    ssh root@$IP "systemctl status truth-ledger --no-pager"
    
    echo "✅ $REGION DEPLOYED"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ MULTI-REGION DEPLOYMENT COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Active regions: ${#REGIONS[@]}"
echo "Geographic redundancy: ENABLED"
echo "Consensus verification: READY"
