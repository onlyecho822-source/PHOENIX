"""
Truth Ledger Database Module
Immutable logging with cryptographic verification
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class TruthLedgerDB:
    """Immutable database for API truth verification"""
    
    def __init__(self, db_path: str = "truth_ledger.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database schema with immutability constraints"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Main checks table - immutable by design
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api_name TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time_ms INTEGER,
                status_code INTEGER,
                source TEXT NOT NULL,
                raw_response TEXT,
                check_hash TEXT NOT NULL UNIQUE,
                previous_hash TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_checks_api_timestamp 
            ON checks(api_name, timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_checks_hash 
            ON checks(check_hash)
        """)
        
        # Discrepancies table - when official status != our measurements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discrepancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api_name TEXT NOT NULL,
                claimed_status TEXT NOT NULL,
                actual_status TEXT NOT NULL,
                claimed_uptime REAL,
                measured_uptime REAL,
                variance_percent REAL NOT NULL,
                proof_hashes TEXT NOT NULL,
                evidence_url TEXT,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sources table - where we verify from
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_url TEXT NOT NULL,
                verification_method TEXT NOT NULL,
                reliability_score REAL DEFAULT 1.0,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(api_name, source_url)
            )
        """)
        
        # Metadata table - system state and chain integrity
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        
        # Initialize metadata if empty
        cursor.execute("SELECT COUNT(*) FROM metadata")
        if cursor.fetchone()[0] == 0:
            self._initialize_metadata()
    
    def _initialize_metadata(self):
        """Set initial metadata values"""
        cursor = self.conn.cursor()
        metadata = {
            "genesis_timestamp": datetime.utcnow().isoformat(),
            "last_backup": "never",
            "total_checks": "0",
            "chain_integrity": "valid",
            "version": "1.0.0"
        }
        for key, value in metadata.items():
            cursor.execute(
                "INSERT INTO metadata (key, value) VALUES (?, ?)",
                (key, value)
            )
        self.conn.commit()
    
    def compute_check_hash(self, check_data: Dict, previous_hash: str = "") -> str:
        """
        Compute cryptographic hash for check
        Creates blockchain-like chain of hashes
        """
        # Canonical representation for hashing
        canonical = json.dumps({
            "timestamp": check_data["timestamp"],
            "api_name": check_data["api_name"],
            "endpoint": check_data["endpoint"],
            "status": check_data["status"],
            "response_time_ms": check_data.get("response_time_ms"),
            "status_code": check_data.get("status_code"),
            "source": check_data["source"],
            "previous_hash": previous_hash
        }, sort_keys=True)
        
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def get_last_hash(self, api_name: str) -> Optional[str]:
        """Get the last check hash for an API to maintain chain"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT check_hash FROM checks 
            WHERE api_name = ? 
            ORDER BY id DESC LIMIT 1
        """, (api_name,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def insert_check(self, check_data: Dict) -> str:
        """
        Insert immutable check record
        Returns the computed hash
        """
        # Get previous hash for chain
        previous_hash = self.get_last_hash(check_data["api_name"]) or ""
        
        # Compute hash
        check_hash = self.compute_check_hash(check_data, previous_hash)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO checks (
                timestamp, api_name, endpoint, status, response_time_ms,
                status_code, source, raw_response, check_hash, previous_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            check_data["timestamp"],
            check_data["api_name"],
            check_data["endpoint"],
            check_data["status"],
            check_data.get("response_time_ms"),
            check_data.get("status_code"),
            check_data["source"],
            check_data.get("raw_response", ""),
            check_hash,
            previous_hash
        ))
        
        self.conn.commit()
        
        # Update metadata
        self._update_metadata("total_checks", str(self.get_total_checks()))
        
        return check_hash
    
    def insert_discrepancy(self, discrepancy_data: Dict) -> int:
        """Record a discrepancy between claimed and actual status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO discrepancies (
                timestamp, api_name, claimed_status, actual_status,
                claimed_uptime, measured_uptime, variance_percent,
                proof_hashes, evidence_url, severity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            discrepancy_data["timestamp"],
            discrepancy_data["api_name"],
            discrepancy_data["claimed_status"],
            discrepancy_data["actual_status"],
            discrepancy_data.get("claimed_uptime"),
            discrepancy_data.get("measured_uptime"),
            discrepancy_data["variance_percent"],
            json.dumps(discrepancy_data.get("proof_hashes", [])),
            discrepancy_data.get("evidence_url", ""),
            discrepancy_data["severity"]
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_source(self, source_data: Dict) -> bool:
        """Add a verification source for an API"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sources (
                    api_name, source_type, source_url, 
                    verification_method, reliability_score
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                source_data["api_name"],
                source_data["source_type"],
                source_data["source_url"],
                source_data["verification_method"],
                source_data.get("reliability_score", 1.0)
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Source already exists
            return False
    
    def get_api_uptime(self, api_name: str, hours: int = 24) -> Dict:
        """Calculate uptime statistics for an API"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'up' THEN 1 ELSE 0 END) as successful_checks,
                AVG(response_time_ms) as avg_response_time,
                MIN(timestamp) as first_check,
                MAX(timestamp) as last_check
            FROM checks
            WHERE api_name = ?
            AND datetime(timestamp) >= datetime('now', '-' || ? || ' hours')
        """, (api_name, hours))
        
        row = cursor.fetchone()
        
        if row["total_checks"] == 0:
            return {"uptime": 0, "checks": 0}
        
        uptime = (row["successful_checks"] / row["total_checks"]) * 100
        
        return {
            "uptime": round(uptime, 4),
            "total_checks": row["total_checks"],
            "successful_checks": row["successful_checks"],
            "avg_response_time_ms": round(row["avg_response_time"] or 0, 2),
            "first_check": row["first_check"],
            "last_check": row["last_check"]
        }
    
    def verify_chain_integrity(self, api_name: str) -> Tuple[bool, List[str]]:
        """
        Verify the hash chain is intact
        Returns (is_valid, list_of_errors)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, api_name, endpoint, status, 
                   response_time_ms, status_code, source, 
                   check_hash, previous_hash
            FROM checks
            WHERE api_name = ?
            ORDER BY id ASC
        """, (api_name,))
        
        rows = cursor.fetchall()
        errors = []
        previous_hash = ""
        
        for row in rows:
            # Reconstruct check data
            check_data = {
                "timestamp": row["timestamp"],
                "api_name": row["api_name"],
                "endpoint": row["endpoint"],
                "status": row["status"],
                "response_time_ms": row["response_time_ms"],
                "status_code": row["status_code"],
                "source": row["source"]
            }
            
            # Compute what hash should be
            expected_hash = self.compute_check_hash(check_data, previous_hash)
            
            # Verify previous_hash matches
            if row["previous_hash"] != previous_hash:
                errors.append(
                    f"Check {row['id']}: previous_hash mismatch. "
                    f"Expected: {previous_hash}, Got: {row['previous_hash']}"
                )
            
            # Verify current hash
            if row["check_hash"] != expected_hash:
                errors.append(
                    f"Check {row['id']}: check_hash mismatch. "
                    f"Expected: {expected_hash}, Got: {row['check_hash']}"
                )
            
            previous_hash = row["check_hash"]
        
        return (len(errors) == 0, errors)
    
    def get_recent_checks(self, api_name: str, limit: int = 100) -> List[Dict]:
        """Get recent checks for an API"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM checks
            WHERE api_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (api_name, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_discrepancies(self, severity: Optional[str] = None) -> List[Dict]:
        """Get all discrepancies, optionally filtered by severity"""
        cursor = self.conn.cursor()
        
        if severity:
            cursor.execute("""
                SELECT * FROM discrepancies
                WHERE severity = ?
                ORDER BY timestamp DESC
            """, (severity,))
        else:
            cursor.execute("""
                SELECT * FROM discrepancies
                ORDER BY timestamp DESC
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_total_checks(self) -> int:
        """Get total number of checks ever performed"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM checks")
        return cursor.fetchone()[0]
    
    def _update_metadata(self, key: str, value: str):
        """Update metadata value"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.utcnow().isoformat()))
        self.conn.commit()
    
    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata value"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        cursor = self.conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM checks")
        total_checks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM discrepancies")
        total_discrepancies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT api_name) FROM checks")
        apis_monitored = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sources WHERE active = 1")
        active_sources = cursor.fetchone()[0]
        
        # Get size
        import os
        db_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
        
        return {
            "total_checks": total_checks,
            "total_discrepancies": total_discrepancies,
            "apis_monitored": apis_monitored,
            "active_sources": active_sources,
            "database_size_mb": round(db_size_mb, 2),
            "genesis_timestamp": self.get_metadata("genesis_timestamp"),
            "last_backup": self.get_metadata("last_backup")
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
