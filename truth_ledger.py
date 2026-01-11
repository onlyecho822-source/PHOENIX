#!/usr/bin/env python3
"""
Truth Ledger - Main Monitoring Script
Checks API status every hour and logs to immutable database
"""

import requests
import time
from datetime import datetime
from typing import Dict, Optional
import logging
import sys
from pathlib import Path

from database import TruthLedgerDB
from api_sources import get_api_config, get_all_apis, get_priority_apis


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('truth_ledger.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class APIMonitor:
    """Monitors APIs and logs results to truth ledger"""
    
    def __init__(self, db_path: str = "truth_ledger.db"):
        self.db = TruthLedgerDB(db_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TruthLedger/1.0 (API Monitoring)'
        })
    
    def check_api(self, api_name: str) -> Dict:
        """
        Check if an API is up
        Returns status, response time, and status code
        """
        config = get_api_config(api_name)
        
        if not config:
            logger.error(f"No configuration found for API: {api_name}")
            return None
        
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Prepare request
            method = config.get("method", "GET").upper()
            url = config["endpoint"]
            headers = config.get("headers", {})
            timeout = config.get("timeout", 10)
            
            # Make request
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=timeout)
            elif method == "HEAD":
                response = self.session.head(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = self.session.post(url, headers=headers, timeout=timeout)
            else:
                logger.error(f"Unsupported method: {method}")
                return None
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Check if status code indicates API is up
            success_codes = config.get("success_codes", [200])
            is_up = response.status_code in success_codes
            
            check_data = {
                "timestamp": timestamp,
                "api_name": api_name,
                "endpoint": url,
                "status": "up" if is_up else "down",
                "response_time_ms": response_time_ms,
                "status_code": response.status_code,
                "source": "direct_check",
                "raw_response": ""  # Don't store full response to save space
            }
            
            # Insert into database
            check_hash = self.db.insert_check(check_data)
            
            logger.info(
                f"✓ {api_name}: {check_data['status']} "
                f"({response_time_ms}ms, {response.status_code}) "
                f"hash={check_hash[:8]}..."
            )
            
            return check_data
            
        except requests.exceptions.Timeout:
            logger.warning(f"✗ {api_name}: TIMEOUT")
            check_data = {
                "timestamp": timestamp,
                "api_name": api_name,
                "endpoint": config["endpoint"],
                "status": "timeout",
                "response_time_ms": config.get("timeout", 10) * 1000,
                "status_code": 0,
                "source": "direct_check",
                "raw_response": "timeout"
            }
            self.db.insert_check(check_data)
            return check_data
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"✗ {api_name}: CONNECTION ERROR")
            check_data = {
                "timestamp": timestamp,
                "api_name": api_name,
                "endpoint": config["endpoint"],
                "status": "down",
                "response_time_ms": 0,
                "status_code": 0,
                "source": "direct_check",
                "raw_response": "connection_error"
            }
            self.db.insert_check(check_data)
            return check_data
            
        except Exception as e:
            logger.error(f"✗ {api_name}: ERROR - {str(e)}")
            check_data = {
                "timestamp": timestamp,
                "api_name": api_name,
                "endpoint": config["endpoint"],
                "status": "error",
                "response_time_ms": 0,
                "status_code": 0,
                "source": "direct_check",
                "raw_response": str(e)
            }
            self.db.insert_check(check_data)
            return check_data
    
    def check_all_apis(self):
        """Check all configured APIs"""
        apis = get_all_apis()
        logger.info(f"Starting check of {len(apis)} APIs...")
        
        results = {}
        for api_name in apis:
            result = self.check_api(api_name)
            if result:
                results[api_name] = result
            time.sleep(1)  # Rate limiting
        
        logger.info(f"Completed check of {len(results)} APIs")
        return results
    
    def verify_integrity(self):
        """Verify hash chain integrity for all APIs"""
        apis = get_all_apis()
        all_valid = True
        
        for api_name in apis:
            is_valid, errors = self.db.verify_chain_integrity(api_name)
            if not is_valid:
                logger.error(f"Chain integrity failure for {api_name}:")
                for error in errors:
                    logger.error(f"  {error}")
                all_valid = False
        
        if all_valid:
            logger.info("✓ All hash chains verified successfully")
        else:
            logger.error("✗ Hash chain verification failed")
        
        return all_valid
    
    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        stats = self.db.get_database_stats()
        
        # Add per-API uptime
        apis = get_all_apis()
        api_uptimes = {}
        
        for api_name in apis:
            uptime_data = self.db.get_api_uptime(api_name, hours=24)
            if uptime_data['total_checks'] > 0:
                api_uptimes[api_name] = uptime_data
        
        stats['api_uptimes'] = api_uptimes
        return stats
    
    def print_stats(self):
        """Print current statistics"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("TRUTH LEDGER - MONITORING STATISTICS")
        print("="*60)
        print(f"Total Checks: {stats['total_checks']}")
        print(f"APIs Monitored: {stats['apis_monitored']}")
        print(f"Discrepancies Found: {stats['total_discrepancies']}")
        print(f"Database Size: {stats['database_size_mb']} MB")
        print(f"Genesis: {stats['genesis_timestamp']}")
        print(f"Last Backup: {stats['last_backup']}")
        print("\nAPI Uptime (Last 24 Hours):")
        print("-"*60)
        
        for api_name, uptime_data in stats['api_uptimes'].items():
            uptime = uptime_data['uptime']
            checks = uptime_data['total_checks']
            avg_time = uptime_data['avg_response_time_ms']
            
            # Color coding
            if uptime >= 99.9:
                status = "✓"
            elif uptime >= 99.0:
                status = "⚠"
            else:
                status = "✗"
            
            print(
                f"{status} {api_name:20s} {uptime:6.2f}% "
                f"({checks:4d} checks, {avg_time:6.0f}ms avg)"
            )
        
        print("="*60 + "\n")
    
    def close(self):
        """Close connections"""
        self.db.close()
        self.session.close()


def main():
    """Main monitoring loop"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Truth Ledger API Monitor')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (default: continuous)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='Check interval in seconds (default: 3600 = 1 hour)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Print statistics and exit'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify chain integrity and exit'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='truth_ledger.db',
        help='Database path (default: truth_ledger.db)'
    )
    
    args = parser.parse_args()
    
    monitor = APIMonitor(args.db)
    
    try:
        if args.stats:
            monitor.print_stats()
            return
        
        if args.verify:
            monitor.verify_integrity()
            return
        
        if args.once:
            logger.info("Running single check...")
            monitor.check_all_apis()
            monitor.print_stats()
        else:
            logger.info(f"Starting continuous monitoring (interval: {args.interval}s)...")
            logger.info("Press Ctrl+C to stop")
            
            iteration = 0
            while True:
                iteration += 1
                logger.info(f"\n--- Iteration {iteration} ---")
                
                monitor.check_all_apis()
                
                if iteration % 24 == 0:  # Print stats every 24 hours
                    monitor.print_stats()
                
                logger.info(f"Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)
    
    except KeyboardInterrupt:
        logger.info("\nStopping monitor...")
    finally:
        monitor.close()
        logger.info("Monitor stopped")


if __name__ == "__main__":
    main()
