#!/usr/bin/env python3
"""
TRUTH NEXUS WATCHDOG
Priority 6: Health Monitoring

Monitors database writes and restarts service if stalled.
"""
import time
import os
import subprocess
import logging
from datetime import datetime

# CONFIGURATION
DB_PATH = "/opt/truth-nexus/truth_ledger.db"
SERVICE_NAME = "truth-ledger"
CHECK_INTERVAL = 300  # 5 minutes
THRESHOLD_SECONDS = 3600  # Alert if no data for 1 hour

logging.basicConfig(level=logging.INFO, format='%(asctime)s - WATCHDOG - %(message)s')

def get_file_mtime(path):
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return 0

def restart_service():
    logging.warning(f"⚠️  Restarting {SERVICE_NAME}...")
    subprocess.run(["systemctl", "restart", SERVICE_NAME])

def run_watchdog():
    logging.info("🐶 Watchdog active. Monitoring Ledger heartbeat...")
    
    while True:
        last_modified = get_file_mtime(DB_PATH)
        time_since_write = time.time() - last_modified
        
        if time_since_write > THRESHOLD_SECONDS:
            logging.error(f"🚨 CRITICAL: No data written for {int(time_since_write)}s!")
            restart_service()
            # TODO: Add SMS/Email alert logic here
        else:
            logging.info(f"✅ Pulse check: OK (Last write {int(time_since_write)}s ago)")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_watchdog()
