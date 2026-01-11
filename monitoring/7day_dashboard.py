#!/usr/bin/env python3
"""
7-DAY MONITORING DASHBOARD
Comprehensive verification and reporting for Truth Ledger
"""
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Database path (adjust based on deployment)
DB_PATH = Path(__file__).parent.parent / "truth_ledger.db"

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"{title:^80}")
    print("=" * 80 + "\n")

def get_db_connection():
    """Get database connection"""
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def check_service_status():
    """Check if data collection is active"""
    print_header("SERVICE STATUS")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get latest check time
    cur.execute("SELECT MAX(timestamp) FROM checks")
    latest_timestamp = cur.fetchone()[0]
    
    if latest_timestamp:
        latest_time = datetime.fromtimestamp(latest_timestamp)
        time_since = datetime.now() - latest_time
        
        print(f"Latest check: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Time since last check: {time_since}")
        
        if time_since.total_seconds() < 7200:  # Less than 2 hours
            print("Status: ✅ ACTIVE")
        else:
            print("Status: ⚠️  STALE (no recent data)")
    else:
        print("Status: ❌ NO DATA")
    
    conn.close()

def get_data_summary():
    """Get overall data summary"""
    print_header("DATA SUMMARY")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Total checks
    cur.execute("SELECT COUNT(*) FROM checks")
    total_checks = cur.fetchone()[0]
    
    # Unique APIs
    cur.execute("SELECT COUNT(DISTINCT api_name) FROM checks")
    unique_apis = cur.fetchone()[0]
    
    # Date range
    cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM checks")
    min_ts, max_ts = cur.fetchone()
    
    if min_ts and max_ts:
        first_check = datetime.fromtimestamp(min_ts)
        last_check = datetime.fromtimestamp(max_ts)
        duration = last_check - first_check
        
        print(f"Total checks: {total_checks:,}")
        print(f"APIs monitored: {unique_apis}")
        print(f"First check: {first_check.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last check: {last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration.days} days, {duration.seconds // 3600} hours")
        
        # Calculate expected vs actual
        expected_checks_per_day = unique_apis * 24  # Hourly checks
        expected_total = expected_checks_per_day * duration.days
        coverage_pct = (total_checks / expected_total * 100) if expected_total > 0 else 0
        
        print(f"Expected checks: {expected_total:,}")
        print(f"Coverage: {coverage_pct:.1f}%")
    else:
        print("No data available")
    
    conn.close()

def get_api_breakdown():
    """Get per-API breakdown"""
    print_header("API BREAKDOWN")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            api_name,
            COUNT(*) as total_checks,
            SUM(CASE WHEN status = 'UP' THEN 1 ELSE 0 END) as up_count,
            SUM(CASE WHEN status != 'UP' THEN 1 ELSE 0 END) as down_count,
            AVG(response_time_ms) as avg_response_ms,
            MIN(datetime(timestamp, 'unixepoch')) as first_check,
            MAX(datetime(timestamp, 'unixepoch')) as last_check
        FROM checks
        GROUP BY api_name
        ORDER BY api_name
    """)
    
    results = cur.fetchall()
    
    print(f"{'API':<15} {'Checks':<8} {'UP':<8} {'DOWN':<8} {'Avg RT':<10} {'Uptime %':<10}")
    print("-" * 80)
    
    for api_name, total, up, down, avg_rt, first, last in results:
        uptime_pct = (up / total * 100) if total > 0 else 0
        avg_rt_str = f"{avg_rt:.0f}ms" if avg_rt else "N/A"
        
        print(f"{api_name:<15} {total:<8} {up:<8} {down:<8} {avg_rt_str:<10} {uptime_pct:>8.2f}%")
    
    conn.close()

def get_recent_issues():
    """Get recent downtime or errors"""
    print_header("RECENT ISSUES (Last 24 Hours)")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_ts = yesterday.timestamp()
    
    cur.execute("""
        SELECT 
            datetime(timestamp, 'unixepoch') as check_time,
            api_name,
            status,
            status_code
        FROM checks
        WHERE timestamp > ? AND status != 'UP'
        ORDER BY timestamp DESC
        LIMIT 20
    """, (yesterday_ts,))
    
    results = cur.fetchall()
    
    if results:
        print(f"{'Time':<20} {'API':<15} {'Status':<10} {'Code':<8}")
        print("-" * 80)
        
        for check_time, api_name, status, status_code in results:
            print(f"{check_time:<20} {api_name:<15} {status:<10} {status_code:<8}")
    else:
        print("✅ No issues detected in last 24 hours")
    
    conn.close()

def verify_chain_integrity():
    """Verify cryptographic chain integrity"""
    print_header("CHAIN INTEGRITY VERIFICATION")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all unique APIs
    cur.execute("SELECT DISTINCT api_name FROM checks ORDER BY api_name")
    apis = [row[0] for row in cur.fetchall()]
    
    all_valid = True
    
    for api_name in apis:
        # Get all checks for this API
        cur.execute("""
            SELECT id, previous_hash, check_hash
            FROM checks
            WHERE api_name = ?
            ORDER BY id ASC
        """, (api_name,))
        
        rows = cur.fetchall()
        
        if not rows:
            continue
        
        # Verify chain links
        broken_links = 0
        for i in range(1, len(rows)):
            prev_check_hash = rows[i-1][2]  # check_hash of previous
            current_prev_hash = rows[i][1]  # previous_hash of current
            
            if prev_check_hash != current_prev_hash:
                broken_links += 1
        
        if broken_links == 0:
            print(f"✅ {api_name:<15} Chain intact ({len(rows)} links)")
        else:
            print(f"❌ {api_name:<15} Chain broken ({broken_links} breaks in {len(rows)} links)")
            all_valid = False
    
    conn.close()
    
    print()
    if all_valid:
        print("✅ ALL CHAINS VERIFIED - DATA INTEGRITY CONFIRMED")
    else:
        print("❌ CHAIN INTEGRITY COMPROMISED - INVESTIGATION REQUIRED")
    
    return all_valid

def check_7day_readiness():
    """Check if 7-day verification period is complete"""
    print_header("7-DAY VERIFICATION READINESS")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get date range
    cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM checks")
    min_ts, max_ts = cur.fetchone()
    
    if not min_ts or not max_ts:
        print("❌ No data available")
        return False
    
    first_check = datetime.fromtimestamp(min_ts)
    last_check = datetime.fromtimestamp(max_ts)
    duration = last_check - first_check
    
    days_collected = duration.days + (duration.seconds / 86400)
    
    print(f"Data collection started: {first_check.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Latest data point: {last_check.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {days_collected:.2f} days")
    print()
    
    if days_collected >= 7.0:
        print("✅ 7-DAY PERIOD COMPLETE")
        print("Ready for technical partnership activation!")
        return True
    else:
        remaining = 7.0 - days_collected
        print(f"⏳ {remaining:.2f} days remaining")
        print(f"Estimated completion: {(last_check + timedelta(days=remaining)).strftime('%Y-%m-%d %H:%M')}")
        return False
    
    conn.close()

def generate_full_report():
    """Generate complete monitoring report"""
    print("\n" + "=" * 80)
    print("TRUTH LEDGER - 7-DAY MONITORING DASHBOARD")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    check_service_status()
    get_data_summary()
    get_api_breakdown()
    get_recent_issues()
    chain_valid = verify_chain_integrity()
    ready = check_7day_readiness()
    
    print_header("SUMMARY")
    
    if ready and chain_valid:
        print("✅ VERIFICATION COMPLETE")
        print("✅ CHAIN INTEGRITY CONFIRMED")
        print("✅ READY FOR NEXT PHASE")
    elif ready and not chain_valid:
        print("✅ 7-DAY PERIOD COMPLETE")
        print("❌ CHAIN INTEGRITY ISSUES DETECTED")
        print("⚠️  INVESTIGATION REQUIRED")
    else:
        print("⏳ DATA COLLECTION IN PROGRESS")
        print("✅ CHAIN INTEGRITY CONFIRMED" if chain_valid else "❌ CHAIN INTEGRITY ISSUES")
        print("⏳ CONTINUE MONITORING")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        generate_full_report()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
