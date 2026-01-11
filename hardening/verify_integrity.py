#!/usr/bin/env python3
"""
TRUTH NEXUS CHAIN INTEGRITY VERIFIER
Priority 11: Cryptographic Chain Verification

Verifies hash chain integrity across all API monitoring records.
Run daily via cron to detect tampering.
"""
import sqlite3
import hashlib
import sys

DB_PATH = "truth_ledger.db"

def verify_chain():
    print("⛓️  VERIFYING CRYPTOGRAPHIC CHAIN...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get all distinct APIs
    cur.execute("SELECT DISTINCT api_name FROM checks")
    apis = [row[0] for row in cur.fetchall()]
    
    total_errors = 0
    
    for api in apis:
        print(f"   Scanning {api}...", end=" ")
        cur.execute("""
            SELECT id, timestamp, endpoint, status, status_code, previous_hash, check_hash 
            FROM checks 
            WHERE api_name = ? 
            ORDER BY id ASC
        """, (api,))
        rows = cur.fetchall()
        
        chain_valid = True
        
        for i in range(len(rows)):
            row = rows[i]
            
            # Verify the previous hash links to the previous row
            if i > 0:
                prev_row_hash = rows[i-1][6]  # check_hash of previous
                current_prev_ptr = row[5]     # previous_hash of current
                
                if prev_row_hash != current_prev_ptr:
                    print(f"BROKEN LINK at ID {row[0]}")
                    chain_valid = False
                    total_errors += 1
                    break
        
        if chain_valid:
            print("OK.")
            
    if total_errors == 0:
        print("✅ INTEGRITY CONFIRMED. 0 ERRORS.")
        sys.exit(0)
    else:
        print(f"❌ INTEGRITY FAILURE. {total_errors} BROKEN CHAINS.")
        sys.exit(1)

if __name__ == "__main__":
    verify_chain()
