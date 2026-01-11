#!/bin/bash
# TRUTH NEXUS HARDENING PROTOCOL
# Priority 1 & 2: Firewall + User Isolation

set -e

echo "🛡️  INITIATING HARDENING SEQUENCE..."

# 1. CREATE DEDICATED USER
if id "truthledger" &>/dev/null; then
    echo "   [SKIP] User 'truthledger' exists."
else
    echo "   [USER] Creating 'truthledger' service user..."
    useradd -r -s /bin/false truthledger
    # Create isolated directory
    mkdir -p /opt/truth-nexus
    chown truthledger:truthledger /opt/truth-nexus
fi

# 2. FIREWALL (UFW)
echo "   [FIREWALL] Configuring UFW..."
# Default: Deny incoming, Allow outgoing
ufw default deny incoming
ufw default allow outgoing
# Allow SSH (Critical: Don't lock yourself out)
ufw allow ssh
# Allow HTTP/HTTPS (If serving public dashboard later)
ufw allow 80/tcp
ufw allow 443/tcp
# Enable
echo "   [FIREWALL] Enabling..."
echo "y" | ufw enable

# 3. SECURE SHARED MEMORY (Anti-exploit)
if ! grep -q "tmpfs /run/shm" /etc/fstab; then
    echo "   [KERNEL] Securing shared memory..."
    echo "tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0" >> /etc/fstab
fi

# 4. FAIL2BAN (Brute force protection)
if ! command -v fail2ban-client &> /dev/null; then
    echo "   [FAIL2BAN] Installing..."
    apt-get update -qq
    apt-get install -y fail2ban -qq
    systemctl enable fail2ban
    systemctl start fail2ban
fi

echo "✅ SYSTEM HARDENED."
echo "   - Firewall Active"
echo "   - Service User Created"
echo "   - Fail2Ban Active"
