#!/bin/bash

###############################################################################
# Truth Ledger - Automated Setup Script
# Supports: Ubuntu 22.04, Debian, Raspberry Pi OS
###############################################################################

set -e  # Exit on any error

echo "=================================="
echo "Truth Ledger - Setup Script"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (use sudo)"
   exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    echo "Detected OS: $OS"
else
    echo "Cannot detect OS"
    exit 1
fi

# Install Python 3 and pip if not present
echo ""
echo "Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git

# Create truth-ledger user (non-root for security)
if ! id -u truth-ledger > /dev/null 2>&1; then
    echo "Creating truth-ledger user..."
    useradd -r -m -d /opt/truth-ledger -s /bin/bash truth-ledger
fi

# Set up directory
INSTALL_DIR="/opt/truth-ledger"
echo "Installing to: $INSTALL_DIR"

# Copy files
mkdir -p $INSTALL_DIR
cp -r * $INSTALL_DIR/
chown -R truth-ledger:truth-ledger $INSTALL_DIR

# Create virtual environment
echo "Creating Python virtual environment..."
cd $INSTALL_DIR
sudo -u truth-ledger python3 -m venv venv
sudo -u truth-ledger $INSTALL_DIR/venv/bin/pip install --upgrade pip
sudo -u truth-ledger $INSTALL_DIR/venv/bin/pip install -r requirements.txt

# Make scripts executable
chmod +x $INSTALL_DIR/truth_ledger.py
chmod +x $INSTALL_DIR/reveal_truth.py

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/truth-ledger.service << 'EOF'
[Unit]
Description=Truth Ledger API Monitor
After=network.target

[Service]
Type=simple
User=truth-ledger
WorkingDirectory=/opt/truth-ledger
ExecStart=/opt/truth-ledger/venv/bin/python3 /opt/truth-ledger/truth_ledger.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create daily discrepancy check cron job
echo "Setting up cron jobs..."
cat > /etc/cron.d/truth-ledger << 'EOF'
# Truth Ledger - Daily discrepancy check at 3 AM
0 3 * * * truth-ledger /opt/truth-ledger/venv/bin/python3 /opt/truth-ledger/reveal_truth.py --report /opt/truth-ledger/discrepancy_report.md

# Backup database to /opt/truth-ledger/backups/ daily at 4 AM
0 4 * * * truth-ledger mkdir -p /opt/truth-ledger/backups && cp /opt/truth-ledger/truth_ledger.db /opt/truth-ledger/backups/truth_ledger_$(date +\%Y\%m\%d).db
EOF

# Create backup directory
mkdir -p $INSTALL_DIR/backups
chown truth-ledger:truth-ledger $INSTALL_DIR/backups

# Reload systemd
systemctl daemon-reload

# Enable and start service
echo ""
echo "Starting Truth Ledger service..."
systemctl enable truth-ledger.service
systemctl start truth-ledger.service

# Wait a moment
sleep 2

# Check status
echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Service Status:"
systemctl status truth-ledger.service --no-pager | head -20
echo ""
echo "Useful Commands:"
echo "  View logs:        journalctl -u truth-ledger -f"
echo "  Check status:     systemctl status truth-ledger"
echo "  Stop service:     systemctl stop truth-ledger"
echo "  Start service:    systemctl start truth-ledger"
echo "  Restart service:  systemctl restart truth-ledger"
echo "  View database:    sqlite3 $INSTALL_DIR/truth_ledger.db"
echo "  Check integrity:  cd $INSTALL_DIR && ./venv/bin/python3 truth_ledger.py --verify"
echo "  View stats:       cd $INSTALL_DIR && ./venv/bin/python3 truth_ledger.py --stats"
echo "  Run discrepancy:  cd $INSTALL_DIR && ./venv/bin/python3 reveal_truth.py"
echo ""
echo "Database location: $INSTALL_DIR/truth_ledger.db"
echo "Backups location:  $INSTALL_DIR/backups/"
echo "Logs location:     journalctl -u truth-ledger"
echo ""
echo "The service is now running and will:"
echo "  - Check all APIs every hour"
echo "  - Log to immutable database"
echo "  - Run discrepancy check daily at 3 AM"
echo "  - Backup database daily at 4 AM"
echo ""
echo "Next Steps:"
echo "1. Wait 24 hours to collect baseline data"
echo "2. Run: cd $INSTALL_DIR && ./venv/bin/python3 truth_ledger.py --stats"
echo "3. Check for discrepancies: cd $INSTALL_DIR && ./venv/bin/python3 reveal_truth.py"
echo ""
echo "=================================="
