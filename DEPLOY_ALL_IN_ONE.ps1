# ============================================================================
# TRUTH LEDGER - ALL-IN-ONE DEPLOYMENT
# ============================================================================
# Purpose: Fully automated deployment with ZERO dependencies
# Usage: Right-click → Run with PowerShell (as Administrator)
# Time: 10 minutes (completely automated)
# ============================================================================

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

# Configuration
$InstallDir = "C:\TruthLedger"
$ServiceName = "TruthLedger"

# ============================================================================
# EMBEDDED TRUTH LEDGER CODE (NO GITHUB DEPENDENCY)
# ============================================================================

$TruthLedgerCode = @'
#!/usr/bin/env python3
"""
TRUTH LEDGER - API Monitoring with Cryptographic Verification
Embedded version - no external dependencies
"""
import sqlite3
import hashlib
import time
import json
from datetime import datetime
from typing import Dict, Optional
try:
    import urllib.request
    import urllib.error
except ImportError:
    print("ERROR: Python standard library not available")
    exit(1)

# Configuration
DB_PATH = "truth_ledger.db"
CHECK_INTERVAL = 3600  # 1 hour

# API endpoints to monitor
APIS = {
    "stripe": "https://status.stripe.com/api/v2/status.json",
    "openai": "https://status.openai.com/api/v2/status.json",
    "github": "https://www.githubstatus.com/api/v2/status.json",
    "cloudflare": "https://www.cloudflarestatus.com/api/v2/status.json",
    "aws": "https://status.aws.amazon.com/",
    "vercel": "https://www.vercel-status.com/api/v2/status.json",
    "netlify": "https://www.netlifystatus.com/api/v2/status.json",
    "mongodb": "https://status.mongodb.com/api/v2/status.json",
    "redis": "https://status.redis.com/api/v2/status.json",
    "datadog": "https://status.datadoghq.com/api/v2/status.json"
}

def init_database():
    """Initialize SQLite database with hash chain"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            api_name TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            status TEXT NOT NULL,
            status_code INTEGER,
            response_time_ms INTEGER,
            previous_hash TEXT,
            check_hash TEXT NOT NULL,
            raw_response TEXT
        )
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_timestamp 
        ON checks(api_name, timestamp)
    """)
    
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] Database initialized: {DB_PATH}")

def get_previous_hash(api_name: str) -> Optional[str]:
    """Get the last hash for this API"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT check_hash FROM checks 
        WHERE api_name = ? 
        ORDER BY id DESC LIMIT 1
    """, (api_name,))
    
    result = cur.fetchone()
    conn.close()
    
    return result[0] if result else "GENESIS"

def compute_hash(timestamp: float, api_name: str, endpoint: str, 
                status: str, status_code: int, previous_hash: str) -> str:
    """Compute SHA-256 hash for this check"""
    data = f"{timestamp}|{api_name}|{endpoint}|{status}|{status_code}|{previous_hash}"
    return hashlib.sha256(data.encode()).hexdigest()

def check_api(api_name: str, endpoint: str) -> Dict:
    """Check API status"""
    start_time = time.time()
    
    try:
        req = urllib.request.Request(
            endpoint,
            headers={'User-Agent': 'TruthLedger/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                'status': 'UP',
                'status_code': status_code,
                'response_time_ms': response_time_ms,
                'raw_response': response_body[:1000]
            }
            
    except urllib.error.HTTPError as e:
        return {
            'status': 'ERROR',
            'status_code': e.code,
            'response_time_ms': int((time.time() - start_time) * 1000),
            'raw_response': str(e)
        }
        
    except Exception as e:
        return {
            'status': 'DOWN',
            'status_code': 0,
            'response_time_ms': int((time.time() - start_time) * 1000),
            'raw_response': str(e)
        }

def save_check(api_name: str, endpoint: str, result: Dict):
    """Save check result with hash chain"""
    timestamp = time.time()
    previous_hash = get_previous_hash(api_name)
    
    check_hash = compute_hash(
        timestamp,
        api_name,
        endpoint,
        result['status'],
        result['status_code'],
        previous_hash
    )
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO checks (
            timestamp, api_name, endpoint, status, status_code,
            response_time_ms, previous_hash, check_hash, raw_response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        api_name,
        endpoint,
        result['status'],
        result['status_code'],
        result['response_time_ms'],
        previous_hash,
        check_hash,
        result['raw_response']
    ))
    
    conn.commit()
    conn.close()
    
    print(f"[{datetime.now()}] {api_name}: {result['status']} "
          f"({result['status_code']}) - {result['response_time_ms']}ms")

def run_monitoring_cycle():
    """Run one complete monitoring cycle"""
    print(f"\n{'='*80}")
    print(f"MONITORING CYCLE - {datetime.now()}")
    print(f"{'='*80}")
    
    for api_name, endpoint in APIS.items():
        try:
            result = check_api(api_name, endpoint)
            save_check(api_name, endpoint, result)
        except Exception as e:
            print(f"[{datetime.now()}] ERROR checking {api_name}: {e}")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM checks")
    total_checks = cur.fetchone()[0]
    conn.close()
    
    print(f"\nTotal checks in database: {total_checks}")
    print(f"Next check in {CHECK_INTERVAL} seconds")

def main():
    """Main monitoring loop"""
    print("="*80)
    print("TRUTH LEDGER STARTING")
    print("="*80)
    print(f"Database: {DB_PATH}")
    print(f"APIs monitored: {len(APIS)}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("="*80)
    
    init_database()
    
    while True:
        try:
            run_monitoring_cycle()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
'@

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Banner {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "$Type" -NoNewline -ForegroundColor $color
    Write-Host " - $Message"
}

function Install-Python {
    Write-Status "Checking for Python..." "INFO"
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)") {
            $minorVersion = [int]$matches[1]
            if ($minorVersion -ge 8) {
                Write-Status "Python $pythonVersion detected" "SUCCESS"
                return $true
            }
        }
    } catch {
        # Python not found
    }
    
    Write-Status "Python 3.8+ not found, installing..." "WARNING"
    
    # Download Python installer
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    Write-Status "Downloading Python 3.11.7..." "INFO"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
    
    Write-Status "Installing Python (this may take 2-3 minutes)..." "INFO"
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Verify installation
    Start-Sleep -Seconds 5
    try {
        $pythonVersion = python --version 2>&1
        Write-Status "Python installed: $pythonVersion" "SUCCESS"
        return $true
    } catch {
        Write-Status "Python installation failed" "ERROR"
        return $false
    }
}

function Install-NSSM {
    Write-Status "Installing NSSM (Service Manager)..." "INFO"
    
    $nssmPath = Join-Path $InstallDir "nssm.exe"
    
    if (Test-Path $nssmPath) {
        Write-Status "NSSM already installed" "SUCCESS"
        return $nssmPath
    }
    
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
    Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
    
    if ([Environment]::Is64BitOperatingSystem) {
        Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" $nssmPath
    } else {
        Copy-Item "$env:TEMP\nssm-2.24\win32\nssm.exe" $nssmPath
    }
    
    Remove-Item $nssmZip -Force
    Write-Status "NSSM installed" "SUCCESS"
    
    return $nssmPath
}

# ============================================================================
# MAIN DEPLOYMENT
# ============================================================================

Write-Banner "TRUTH LEDGER - ALL-IN-ONE DEPLOYMENT"

Write-Host "This script will:"
Write-Host "  1. Install Python (if needed)"
Write-Host "  2. Create Truth Ledger service"
Write-Host "  3. Start 24/7 monitoring"
Write-Host "  4. Begin data collection"
Write-Host ""
Write-Host "Installation directory: $InstallDir"
Write-Host "Estimated time: 5-10 minutes"
Write-Host ""

$response = Read-Host "Continue? (Y/N)"
if ($response -ne "Y" -and $response -ne "y") {
    Write-Host "Deployment cancelled"
    exit 0
}

Write-Banner "STEP 1: PREREQUISITES"

# Install Python if needed
if (-not (Install-Python)) {
    Write-Host ""
    Write-Host "ERROR: Python installation failed" -ForegroundColor Red
    Write-Host "Please install Python manually from: https://www.python.org/downloads/"
    exit 1
}

Write-Banner "STEP 2: CREATE INSTALLATION"

# Create installation directory
Write-Status "Creating installation directory..." "INFO"
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Write Truth Ledger code
$truthLedgerPath = Join-Path $InstallDir "truth_ledger.py"
Write-Status "Creating Truth Ledger script..." "INFO"
Set-Content -Path $truthLedgerPath -Value $TruthLedgerCode

# Install NSSM
$nssmPath = Install-NSSM

Write-Banner "STEP 3: CONFIGURE SERVICE"

# Stop existing service if running
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Status "Stopping existing service..." "WARNING"
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    & $nssmPath remove $ServiceName confirm 2>&1 | Out-Null
    Start-Sleep -Seconds 2
}

# Install service
Write-Status "Installing Windows Service..." "INFO"
$pythonExe = (Get-Command python).Source

& $nssmPath install $ServiceName $pythonExe $truthLedgerPath 2>&1 | Out-Null
& $nssmPath set $ServiceName AppDirectory $InstallDir 2>&1 | Out-Null
& $nssmPath set $ServiceName DisplayName "PHOENIX Truth Ledger Monitor" 2>&1 | Out-Null
& $nssmPath set $ServiceName Description "24/7 API monitoring with cryptographic verification" 2>&1 | Out-Null
& $nssmPath set $ServiceName Start SERVICE_AUTO_START 2>&1 | Out-Null
& $nssmPath set $ServiceName AppStdout "$InstallDir\stdout.log" 2>&1 | Out-Null
& $nssmPath set $ServiceName AppStderr "$InstallDir\stderr.log" 2>&1 | Out-Null
& $nssmPath set $ServiceName AppRotateFiles 1 2>&1 | Out-Null
& $nssmPath set $ServiceName AppRotateBytes 1048576 2>&1 | Out-Null

Write-Banner "STEP 4: START SERVICE"

Write-Status "Starting Truth Ledger service..." "INFO"
Start-Service -Name $ServiceName

# Wait for service to start
Start-Sleep -Seconds 5

# Verify service is running
$service = Get-Service -Name $ServiceName
if ($service.Status -eq "Running") {
    Write-Status "Service started successfully!" "SUCCESS"
} else {
    Write-Status "Service failed to start" "ERROR"
    Write-Host ""
    Write-Host "Check error logs at: $InstallDir\stderr.log"
    exit 1
}

# Wait for first check to complete
Write-Status "Waiting for first monitoring cycle (30 seconds)..." "INFO"
Start-Sleep -Seconds 30

Write-Banner "DEPLOYMENT COMPLETE"

Write-Host "✅ Truth Ledger is now running 24/7" -ForegroundColor Green
Write-Host ""
Write-Host "Installation Details:" -ForegroundColor Yellow
Write-Host "  Service Name: $ServiceName"
Write-Host "  Install Directory: $InstallDir"
Write-Host "  Database: $InstallDir\truth_ledger.db"
Write-Host "  Logs: $InstallDir\stdout.log"
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  View status:  Get-Service $ServiceName"
Write-Host "  Stop service: Stop-Service $ServiceName"
Write-Host "  Start service: Start-Service $ServiceName"
Write-Host "  View logs:    Get-Content $InstallDir\stdout.log -Tail 50 -Wait"
Write-Host ""
Write-Host "Verify Data Collection (run after 1 hour):" -ForegroundColor Yellow
Write-Host "  cd $InstallDir"
Write-Host '  python -c "import sqlite3; conn=sqlite3.connect(''truth_ledger.db''); print(f''Total checks: {conn.execute(''''SELECT COUNT(*) FROM checks'''').fetchone()[0]}''); conn.close()"'
Write-Host ""
Write-Host "🚀 Data collection has started!" -ForegroundColor Green
Write-Host "📊 Check back in 1 hour to see first results" -ForegroundColor Green
Write-Host "⏰ Full 7-day verification completes: " -NoNewline -ForegroundColor Green
Write-Host (Get-Date).AddDays(7).ToString("yyyy-MM-dd HH:mm") -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
