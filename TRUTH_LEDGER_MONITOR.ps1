# ============================================================================
# TRUTH LEDGER - FULLY LOADED MONITORING & MANAGEMENT SCRIPT
# ============================================================================
# Purpose: Complete monitoring, verification, and management system
# Usage: .\TRUTH_LEDGER_MONITOR.ps1 [action]
# Actions: status, verify, analyze, export, fix, schedule
# ============================================================================

param(
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"

# Configuration
$InstallDir = "C:\TruthLedger"
$DBPath = "$InstallDir\truth_ledger.db"
$ServiceName = "TruthLedger"
$LogPath = "$InstallDir\monitor_log.txt"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Banner {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host $Text.PadLeft(($Text.Length + 80) / 2) -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    $output = "[$timestamp] $Type - $Message"
    Write-Host $output -ForegroundColor $color
    Add-Content -Path $LogPath -Value $output
}

function Get-DatabaseStats {
    $query = @"
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('$($DBPath.Replace('\', '\\'))')
cur = conn.cursor()

# Total checks
cur.execute('SELECT COUNT(*) FROM checks')
total = cur.fetchone()[0]

# Per-API breakdown
cur.execute('''
    SELECT 
        api_name,
        COUNT(*) as total,
        SUM(CASE WHEN status = "UP" THEN 1 ELSE 0 END) as up,
        AVG(response_time_ms) as avg_ms
    FROM checks
    GROUP BY api_name
    ORDER BY api_name
''')
apis = cur.fetchall()

# Time range
cur.execute('SELECT MIN(timestamp), MAX(timestamp) FROM checks')
min_ts, max_ts = cur.fetchone()

# Recent issues
cur.execute('''
    SELECT datetime(timestamp, "unixepoch"), api_name, status, status_code
    FROM checks
    WHERE status != "UP"
    ORDER BY timestamp DESC
    LIMIT 10
''')
issues = cur.fetchall()

result = {
    'total': total,
    'apis': [{'name': a[0], 'total': a[1], 'up': a[2], 'avg_ms': round(a[3], 2) if a[3] else 0} for a in apis],
    'first_check': datetime.fromtimestamp(min_ts).isoformat() if min_ts else None,
    'last_check': datetime.fromtimestamp(max_ts).isoformat() if max_ts else None,
    'issues': [{'time': i[0], 'api': i[1], 'status': i[2], 'code': i[3]} for i in issues]
}

print(json.dumps(result))
conn.close()
"@

    $result = python -c $query
    return $result | ConvertFrom-Json
}

function Test-ChainIntegrity {
    $query = @"
import sqlite3
import hashlib

conn = sqlite3.connect('$($DBPath.Replace('\', '\\'))')
cur = conn.cursor()

# Get all unique APIs
cur.execute('SELECT DISTINCT api_name FROM checks ORDER BY api_name')
apis = [row[0] for row in cur.fetchall()]

results = {}

for api in apis:
    cur.execute('''
        SELECT id, timestamp, api_name, endpoint, status, status_code, previous_hash, check_hash
        FROM checks
        WHERE api_name = ?
        ORDER BY id ASC
    ''', (api,))
    
    rows = cur.fetchall()
    
    if not rows:
        continue
    
    broken = 0
    total = len(rows)
    
    # Verify chain links
    for i in range(1, len(rows)):
        prev_check_hash = rows[i-1][7]  # check_hash of previous
        current_prev_hash = rows[i][6]  # previous_hash of current
        
        if prev_check_hash != current_prev_hash:
            broken += 1
    
    # Verify hash computation
    for row in rows:
        row_id, timestamp, api_name, endpoint, status, status_code, previous_hash, check_hash = row
        data = f"{timestamp}|{api_name}|{endpoint}|{status}|{status_code}|{previous_hash}"
        computed_hash = hashlib.sha256(data.encode()).hexdigest()
        
        if computed_hash != check_hash:
            broken += 1
    
    results[api] = {'total': total, 'broken': broken, 'valid': broken == 0}

conn.close()

import json
print(json.dumps(results))
"@

    $result = python -c $query
    return $result | ConvertFrom-Json
}

# ============================================================================
# ACTION FUNCTIONS
# ============================================================================

function Show-Status {
    Write-Banner "TRUTH LEDGER - STATUS REPORT"
    
    # Service status
    Write-Host "SERVICE STATUS" -ForegroundColor Yellow
    Write-Host ("-" * 80)
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        $statusColor = if ($service.Status -eq "Running") { "Green" } else { "Red" }
        Write-Host "Service: " -NoNewline
        Write-Host $service.Status -ForegroundColor $statusColor
        Write-Host "Display Name: $($service.DisplayName)"
        Write-Host "Start Type: $($service.StartType)"
    } else {
        Write-Host "Service not found!" -ForegroundColor Red
        return
    }
    
    # Database stats
    Write-Host "`nDATABASE STATISTICS" -ForegroundColor Yellow
    Write-Host ("-" * 80)
    
    if (-not (Test-Path $DBPath)) {
        Write-Host "Database not found at: $DBPath" -ForegroundColor Red
        return
    }
    
    $stats = Get-DatabaseStats
    
    Write-Host "Total Checks: " -NoNewline
    Write-Host $stats.total -ForegroundColor Green
    
    if ($stats.first_check) {
        $firstCheck = [DateTime]::Parse($stats.first_check)
        $lastCheck = [DateTime]::Parse($stats.last_check)
        $duration = $lastCheck - $firstCheck
        
        Write-Host "First Check: $($firstCheck.ToString('yyyy-MM-dd HH:mm:ss'))"
        Write-Host "Last Check: $($lastCheck.ToString('yyyy-MM-dd HH:mm:ss'))"
        Write-Host "Duration: $($duration.Days) days, $($duration.Hours) hours, $($duration.Minutes) minutes"
        
        # Calculate progress
        $daysElapsed = $duration.TotalDays
        $daysRemaining = 7 - $daysElapsed
        $progressPct = ($daysElapsed / 7) * 100
        
        Write-Host "`n7-DAY VERIFICATION PROGRESS" -ForegroundColor Yellow
        Write-Host ("-" * 80)
        Write-Host "Days Elapsed: " -NoNewline
        Write-Host ("{0:F2}" -f $daysElapsed) -ForegroundColor Cyan
        Write-Host "Days Remaining: " -NoNewline
        $remainingColor = if ($daysRemaining -le 0) { "Green" } else { "Yellow" }
        Write-Host ("{0:F2}" -f $daysRemaining) -ForegroundColor $remainingColor
        Write-Host "Progress: " -NoNewline
        Write-Host ("{0:F1}%" -f $progressPct) -ForegroundColor Cyan
        
        if ($daysRemaining -le 0) {
            Write-Host "`n✅ 7-DAY VERIFICATION COMPLETE!" -ForegroundColor Green
            Write-Host "Ready for technical partnership activation." -ForegroundColor Green
        } else {
            $completionDate = $lastCheck.AddDays($daysRemaining)
            Write-Host "Estimated Completion: $($completionDate.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        }
    }
    
    # Per-API breakdown
    Write-Host "`nAPI BREAKDOWN" -ForegroundColor Yellow
    Write-Host ("-" * 80)
    Write-Host ("{0,-15} {1,10} {2,10} {3,12} {4,10}" -f "API", "Checks", "UP", "Avg RT (ms)", "Uptime %")
    Write-Host ("-" * 80)
    
    foreach ($api in $stats.apis) {
        $uptimePct = if ($api.total -gt 0) { ($api.up / $api.total) * 100 } else { 0 }
        $uptimeColor = if ($uptimePct -ge 99) { "Green" } elseif ($uptimePct -ge 95) { "Yellow" } else { "Red" }
        
        Write-Host ("{0,-15}" -f $api.name) -NoNewline
        Write-Host ("{0,10}" -f $api.total) -NoNewline
        Write-Host ("{0,10}" -f $api.up) -NoNewline
        Write-Host ("{0,12:F0}" -f $api.avg_ms) -NoNewline
        Write-Host ("{0,9:F2}%" -f $uptimePct) -ForegroundColor $uptimeColor
    }
    
    # Recent issues
    if ($stats.issues.Count -gt 0) {
        Write-Host "`nRECENT ISSUES" -ForegroundColor Yellow
        Write-Host ("-" * 80)
        Write-Host ("{0,-20} {1,-15} {2,-10} {3,-10}" -f "Time", "API", "Status", "Code")
        Write-Host ("-" * 80)
        
        foreach ($issue in $stats.issues) {
            Write-Host ("{0,-20} {1,-15} {2,-10} {3,-10}" -f $issue.time, $issue.api, $issue.status, $issue.code) -ForegroundColor Red
        }
    } else {
        Write-Host "`n✅ No issues detected!" -ForegroundColor Green
    }
    
    Write-Host ""
}

function Verify-Integrity {
    Write-Banner "TRUTH LEDGER - CHAIN INTEGRITY VERIFICATION"
    
    Write-Host "Verifying cryptographic hash chains..." -ForegroundColor Cyan
    Write-Host ""
    
    $results = Test-ChainIntegrity
    
    Write-Host ("{0,-15} {1,10} {2,10} {3,-10}" -f "API", "Links", "Broken", "Status")
    Write-Host ("-" * 80)
    
    $allValid = $true
    
    foreach ($api in $results.PSObject.Properties) {
        $data = $api.Value
        $statusText = if ($data.valid) { "✅ VALID" } else { "❌ BROKEN" }
        $statusColor = if ($data.valid) { "Green" } else { "Red" }
        
        Write-Host ("{0,-15}" -f $api.Name) -NoNewline
        Write-Host ("{0,10}" -f $data.total) -NoNewline
        Write-Host ("{0,10}" -f $data.broken) -NoNewline
        Write-Host ("{0,-10}" -f $statusText) -ForegroundColor $statusColor
        
        if (-not $data.valid) {
            $allValid = $false
        }
    }
    
    Write-Host ""
    if ($allValid) {
        Write-Host "✅ ALL CHAINS VERIFIED - DATA INTEGRITY CONFIRMED" -ForegroundColor Green
    } else {
        Write-Host "❌ CHAIN INTEGRITY COMPROMISED - INVESTIGATION REQUIRED" -ForegroundColor Red
    }
    Write-Host ""
}

function Export-Data {
    Write-Banner "TRUTH LEDGER - DATA EXPORT"
    
    $exportDir = "$InstallDir\exports"
    if (-not (Test-Path $exportDir)) {
        New-Item -ItemType Directory -Path $exportDir | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    # Export database
    $dbBackup = "$exportDir\truth_ledger_$timestamp.db"
    Copy-Item -Path $DBPath -Destination $dbBackup
    Write-Status "Database exported: $dbBackup" "SUCCESS"
    
    # Export CSV
    $csvPath = "$exportDir\truth_ledger_$timestamp.csv"
    $query = @"
import sqlite3
import csv

conn = sqlite3.connect('$($DBPath.Replace('\', '\\'))')
cur = conn.cursor()

cur.execute('SELECT * FROM checks ORDER BY timestamp')
rows = cur.fetchall()

with open('$($csvPath.Replace('\', '\\'))', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'timestamp', 'api_name', 'endpoint', 'status', 'status_code', 'response_time_ms', 'previous_hash', 'check_hash', 'raw_response'])
    writer.writerows(rows)

conn.close()
print('Exported')
"@
    
    python -c $query | Out-Null
    Write-Status "CSV exported: $csvPath" "SUCCESS"
    
    # Export JSON summary
    $jsonPath = "$exportDir\summary_$timestamp.json"
    $stats = Get-DatabaseStats
    $stats | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8
    Write-Status "Summary exported: $jsonPath" "SUCCESS"
    
    Write-Host "`nExport complete!" -ForegroundColor Green
    Write-Host "Location: $exportDir" -ForegroundColor Gray
    Write-Host ""
}

function Fix-Service {
    Write-Banner "TRUTH LEDGER - SERVICE REPAIR"
    
    Write-Host "Attempting to fix service issues..." -ForegroundColor Cyan
    Write-Host ""
    
    # Check if service exists
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Status "Service not found. Reinstalling..." "WARNING"
        Write-Host "Run deployment script again: irm https://raw.githubusercontent.com/onlyecho822-source/PHOENIX/main/DEPLOY_ALL_IN_ONE.ps1 | iex" -ForegroundColor Yellow
        return
    }
    
    # Stop service
    if ($service.Status -eq "Running") {
        Write-Status "Stopping service..." "INFO"
        Stop-Service -Name $ServiceName -Force
        Start-Sleep -Seconds 2
    }
    
    # Start service
    Write-Status "Starting service..." "INFO"
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 3
    
    # Verify
    $service = Get-Service -Name $ServiceName
    if ($service.Status -eq "Running") {
        Write-Status "Service repaired successfully!" "SUCCESS"
    } else {
        Write-Status "Service failed to start. Check logs: $InstallDir\stderr.log" "ERROR"
    }
    
    Write-Host ""
}

function Set-DailySchedule {
    Write-Banner "TRUTH LEDGER - SCHEDULE DAILY MONITORING"
    
    Write-Host "Creating scheduled task for daily monitoring..." -ForegroundColor Cyan
    Write-Host ""
    
    $taskName = "TruthLedger-DailyMonitor"
    $scriptPath = $MyInvocation.MyCommand.Path
    
    # Remove existing task
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    # Create new task
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" status"
    $trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Daily Truth Ledger monitoring and verification" | Out-Null
    
    Write-Status "Scheduled task created: $taskName" "SUCCESS"
    Write-Host "Daily monitoring will run at 9:00 AM" -ForegroundColor Green
    Write-Host ""
}

function Show-Help {
    Write-Banner "TRUTH LEDGER - HELP"
    
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\TRUTH_LEDGER_MONITOR.ps1 [action]"
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor Yellow
    Write-Host "  status    - Show complete status report (default)"
    Write-Host "  verify    - Verify cryptographic chain integrity"
    Write-Host "  analyze   - Detailed data analysis"
    Write-Host "  export    - Export database and reports"
    Write-Host "  fix       - Repair service issues"
    Write-Host "  schedule  - Set up daily automated monitoring"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\TRUTH_LEDGER_MONITOR.ps1"
    Write-Host "  .\TRUTH_LEDGER_MONITOR.ps1 status"
    Write-Host "  .\TRUTH_LEDGER_MONITOR.ps1 verify"
    Write-Host "  .\TRUTH_LEDGER_MONITOR.ps1 export"
    Write-Host ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

switch ($Action.ToLower()) {
    "status" { Show-Status }
    "verify" { Verify-Integrity }
    "analyze" { Show-Status; Verify-Integrity }
    "export" { Export-Data }
    "fix" { Fix-Service }
    "schedule" { Set-DailySchedule }
    "help" { Show-Help }
    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Write-Host "Run '.\TRUTH_LEDGER_MONITOR.ps1 help' for usage information" -ForegroundColor Yellow
    }
}
