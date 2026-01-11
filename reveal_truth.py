#!/usr/bin/env python3
"""
Reveal Truth - Discrepancy Detection Script
Compares official status claims vs our measured reality
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sys

from database import TruthLedgerDB
from api_sources import get_api_config, get_all_apis


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class DiscrepancyDetector:
    """Detects discrepancies between claimed and actual API status"""
    
    def __init__(self, db_path: str = "truth_ledger.db"):
        self.db = TruthLedgerDB(db_path)
        self.session = requests.Session()
    
    def scrape_official_status(self, api_name: str) -> Optional[Dict]:
        """
        Scrape official status page
        Returns claimed uptime and status
        """
        config = get_api_config(api_name)
        verification_sources = config.get("verification_sources", [])
        
        if not verification_sources:
            logger.info(f"No verification sources for {api_name}")
            return None
        
        # Use first official source
        for source in verification_sources:
            if source["type"] == "official_status":
                try:
                    response = self.session.get(source["url"], timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for common status indicators
                    # Most status pages use "operational", "up", "all systems operational"
                    text = soup.get_text().lower()
                    
                    if "operational" in text or "all systems" in text:
                        claimed_status = "up"
                    elif "outage" in text or "down" in text:
                        claimed_status = "down"
                    elif "degraded" in text or "issues" in text:
                        claimed_status = "degraded"
                    else:
                        claimed_status = "unknown"
                    
                    # Try to find uptime percentage if present
                    claimed_uptime = self._extract_uptime(text)
                    
                    return {
                        "claimed_status": claimed_status,
                        "claimed_uptime": claimed_uptime,
                        "source_url": source["url"]
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to scrape {source['url']}: {e}")
                    continue
        
        return None
    
    def _extract_uptime(self, text: str) -> Optional[float]:
        """Extract uptime percentage from text"""
        import re
        
        # Look for patterns like "99.9%", "99.95% uptime"
        patterns = [
            r'(\d+\.\d+)%\s*uptime',
            r'uptime.*?(\d+\.\d+)%',
            r'(\d+\.\d+)%.*?availability'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return None
    
    def compare_status(self, api_name: str, hours: int = 24) -> Optional[Dict]:
        """
        Compare official claimed status vs our measurements
        Returns discrepancy data if variance > 2%
        """
        # Get our measured uptime
        measured = self.db.get_api_uptime(api_name, hours=hours)
        
        if measured['total_checks'] == 0:
            logger.info(f"No data for {api_name}")
            return None
        
        # Get official claimed status
        official = self.scrape_official_status(api_name)
        
        if not official:
            logger.info(f"Could not get official status for {api_name}")
            return None
        
        # Compare
        measured_uptime = measured['uptime']
        claimed_uptime = official.get('claimed_uptime')
        
        # If we can't extract claimed uptime percentage, use status comparison
        if claimed_uptime is None:
            # Simple status comparison
            claimed_status = official['claimed_status']
            
            # If they claim "up" but we measure < 95%, that's a discrepancy
            if claimed_status == "up" and measured_uptime < 95.0:
                variance = 100.0 - measured_uptime
                severity = self._calculate_severity(variance)
                
                return {
                    "api_name": api_name,
                    "claimed_status": claimed_status,
                    "actual_status": f"{measured_uptime:.2f}% uptime",
                    "claimed_uptime": None,
                    "measured_uptime": measured_uptime,
                    "variance_percent": variance,
                    "severity": severity,
                    "evidence_url": official['source_url'],
                    "checks_count": measured['total_checks']
                }
        else:
            # Percentage comparison
            variance = abs(claimed_uptime - measured_uptime)
            
            if variance > 2.0:  # More than 2% difference
                severity = self._calculate_severity(variance)
                
                return {
                    "api_name": api_name,
                    "claimed_status": f"{claimed_uptime}% uptime",
                    "actual_status": f"{measured_uptime:.2f}% uptime",
                    "claimed_uptime": claimed_uptime,
                    "measured_uptime": measured_uptime,
                    "variance_percent": variance,
                    "severity": severity,
                    "evidence_url": official['source_url'],
                    "checks_count": measured['total_checks']
                }
        
        return None
    
    def _calculate_severity(self, variance: float) -> str:
        """Calculate severity based on variance"""
        if variance >= 10.0:
            return "critical"
        elif variance >= 5.0:
            return "high"
        elif variance >= 2.0:
            return "medium"
        else:
            return "low"
    
    def detect_all_discrepancies(self, hours: int = 24) -> List[Dict]:
        """Check all APIs for discrepancies"""
        apis = get_all_apis()
        discrepancies = []
        
        logger.info(f"Checking {len(apis)} APIs for discrepancies...")
        
        for api_name in apis:
            logger.info(f"Checking {api_name}...")
            discrepancy = self.compare_status(api_name, hours=hours)
            
            if discrepancy:
                # Get proof hashes
                recent_checks = self.db.get_recent_checks(api_name, limit=100)
                proof_hashes = [check['check_hash'] for check in recent_checks[:10]]
                
                discrepancy['proof_hashes'] = proof_hashes
                discrepancy['timestamp'] = datetime.utcnow().isoformat()
                
                # Store in database
                self.db.insert_discrepancy(discrepancy)
                
                discrepancies.append(discrepancy)
                
                logger.warning(
                    f"⚠ DISCREPANCY FOUND: {api_name} - "
                    f"Claimed: {discrepancy['claimed_status']}, "
                    f"Actual: {discrepancy['actual_status']}, "
                    f"Variance: {discrepancy['variance_percent']:.2f}%"
                )
        
        return discrepancies
    
    def generate_report(self, discrepancies: List[Dict], output_file: str = "discrepancy_report.md"):
        """Generate markdown report of discrepancies"""
        if not discrepancies:
            logger.info("No discrepancies found - all APIs match their claims")
            return
        
        report = []
        report.append("# TRUTH LEDGER - DISCREPANCY REPORT\n")
        report.append(f"**Generated:** {datetime.utcnow().isoformat()}\n")
        report.append(f"**Discrepancies Found:** {len(discrepancies)}\n")
        report.append("\n---\n")
        
        for disc in sorted(discrepancies, key=lambda x: x['variance_percent'], reverse=True):
            severity_emoji = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "⚡",
                "low": "ℹ️"
            }
            
            report.append(f"\n## {severity_emoji.get(disc['severity'], '⚠️')} {disc['api_name'].upper()}\n")
            report.append(f"**Severity:** {disc['severity'].upper()}\n")
            report.append(f"**Variance:** {disc['variance_percent']:.2f}%\n\n")
            
            report.append("### The Claim vs. The Truth\n")
            report.append(f"- **They Claimed:** {disc['claimed_status']}\n")
            report.append(f"- **We Measured:** {disc['actual_status']}\n")
            report.append(f"- **Based On:** {disc['checks_count']} checks over 24 hours\n\n")
            
            report.append("### Cryptographic Proof\n")
            report.append("Proof hashes (first 10 checks):\n")
            for i, hash_val in enumerate(disc['proof_hashes'][:10], 1):
                report.append(f"{i}. `{hash_val}`\n")
            
            report.append(f"\n**Evidence:** [{disc['evidence_url']}]({disc['evidence_url']})\n")
            report.append("\n---\n")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(''.join(report))
        
        logger.info(f"Report written to {output_file}")
        
        # Also print summary
        print("\n" + "="*60)
        print("DISCREPANCY REPORT SUMMARY")
        print("="*60)
        for disc in discrepancies:
            print(
                f"{disc['api_name']:20s} | "
                f"Variance: {disc['variance_percent']:6.2f}% | "
                f"Severity: {disc['severity']:8s}"
            )
        print("="*60 + "\n")
    
    def close(self):
        """Close connections"""
        self.db.close()
        self.session.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Truth Ledger Discrepancy Detector')
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours of data to analyze (default: 24)'
    )
    parser.add_argument(
        '--api',
        type=str,
        help='Check specific API only'
    )
    parser.add_argument(
        '--report',
        type=str,
        default='discrepancy_report.md',
        help='Output report file (default: discrepancy_report.md)'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='truth_ledger.db',
        help='Database path (default: truth_ledger.db)'
    )
    
    args = parser.parse_args()
    
    detector = DiscrepancyDetector(args.db)
    
    try:
        if args.api:
            logger.info(f"Checking {args.api}...")
            discrepancy = detector.compare_status(args.api, hours=args.hours)
            if discrepancy:
                discrepancies = [discrepancy]
            else:
                discrepancies = []
                logger.info(f"No discrepancy found for {args.api}")
        else:
            discrepancies = detector.detect_all_discrepancies(hours=args.hours)
        
        if discrepancies:
            detector.generate_report(discrepancies, output_file=args.report)
        else:
            logger.info("✓ All APIs match their official status claims")
    
    finally:
        detector.close()


if __name__ == "__main__":
    main()
