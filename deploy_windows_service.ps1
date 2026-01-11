# ============================================================================
# TRUTH LEDGER WINDOWS SERVICE INSTALLER
# ============================================================================
# Purpose: Deploy Truth Ledger as 24/7 Windows Service on your laptop
# Usage: Run as Administrator: .\deploy_windows_service.ps1
# Time: 10 minutes
# ============================================================================

#Requires -RunAsAdministrator

param(
    [string]$InstallDir = "C:\TruthLedger",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# Configuration
$ServiceName = "TruthLedger"
$ServiceDisplayName = "PHOENIX Truth Ledger Monitor"
$ServiceDescription = "24/7 API monitoring with cryptographic verification"

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "$Type" -NoNewline -ForegroundColor $color
    Write-Host " - $Message"
}

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)") {
            $minorVersion = [int]$matches[1]
            if ($minorVersion -ge 8) {
                Write-Status "Python $pythonVersion detected" "SUCCESS"
                return $true
            }
        }
        Write-Status "Python 3.8+ required" "ERROR"
        return $false
    } catch {
        Write-Status "Python not found" "ERROR"
        return $false
    }
}

function Install-TruthLedger {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "TRUTH LEDGER WINDOWS SERVICE INSTALLER" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check Python
    Write-Status "Checking prerequisites..." "INFO"
    if (-not (Test-PythonInstalled)) {
        Write-Host ""
        Write-Host "Please install Python 3.8+ from: https://www.python.org/downloads/"
        Write-Host "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }
    
    # Create installation directory
    Write-Status "Creating installation directory: $InstallDir" "INFO"
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
    
    # Clone repository
    Write-Status "Cloning PHOENIX repository..." "INFO"
    $repoPath = Join-Path $InstallDir "PHOENIX"
    if (Test-Path $repoPath) {
        Write-Status "Repository already exists, pulling latest..." "WARNING"
        Push-Location $repoPath
        git pull origin main 2>&1 | Out-Null
        Pop-Location
    } else {
        git clone https://github.com/onlyecho822-source/PHOENIX.git $repoPath 2>&1 | Out-Null
    }
    
    # Install Python dependencies
    Write-Status "Installing Python dependencies..." "INFO"
    Push-Location $repoPath
    python -m pip install --upgrade pip --quiet
    pip install requests schedule --quiet
    Pop-Location
    
    # Create Windows-compatible truth_ledger.py
    Write-Status "Creating Windows service wrapper..." "INFO"
    $servicePyPath = Join-Path $InstallDir "truth_ledger_service.py"
    
    $servicePyContent = @'
#!/usr/bin/env python3
"""
TRUTH LEDGER WINDOWS SERVICE
24/7 API monitoring with cryptographic verification
"""
import sys
import os
import time
import logging
from pathlib import Path

# Set up paths
INSTALL_DIR = Path(__file__).parent
PHOENIX_DIR = INSTALL_DIR / "PHOENIX"
sys.path.insert(0, str(PHOENIX_DIR))

# Configure logging
LOG_FILE = INSTALL_DIR / "truth_ledger.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def main():
    """Main service loop"""
    logging.info("=" * 80)
    logging.info("TRUTH LEDGER SERVICE STARTING")
    logging.info("=" * 80)
    logging.info(f"Install directory: {INSTALL_DIR}")
    logging.info(f"PHOENIX directory: {PHOENIX_DIR}")
    logging.info(f"Log file: {LOG_FILE}")
    
    # Change to PHOENIX directory
    os.chdir(PHOENIX_DIR)
    
    # Import and run truth_ledger
    try:
        # Import the main truth_ledger module
        import truth_ledger
        
        logging.info("Starting monitoring loop...")
        
        # Run the monitoring loop
        while True:
            try:
                truth_ledger.run_monitoring_cycle()
                time.sleep(3600)  # 1 hour between checks
            except KeyboardInterrupt:
                logging.info("Service stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retry
                
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'@
    
    Set-Content -Path $servicePyPath -Value $servicePyContent
    
    # Create NSSM service wrapper
    Write-Status "Installing NSSM (Non-Sucking Service Manager)..." "INFO"
    $nssmPath = Join-Path $InstallDir "nssm.exe"
    
    if (-not (Test-Path $nssmPath)) {
        # Download NSSM
        $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $nssmZip = Join-Path $env:TEMP "nssm.zip"
        
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
        Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
        
        # Copy appropriate version
        if ([Environment]::Is64BitOperatingSystem) {
            Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" $nssmPath
        } else {
            Copy-Item "$env:TEMP\nssm-2.24\win32\nssm.exe" $nssmPath
        }
        
        Remove-Item $nssmZip -Force
    }
    
    # Stop existing service if running
    $existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Status "Stopping existing service..." "WARNING"
        Stop-Service -Name $ServiceName -Force
        & $nssmPath remove $ServiceName confirm
        Start-Sleep -Seconds 2
    }
    
    # Install service
    Write-Status "Installing Windows Service..." "INFO"
    $pythonExe = (Get-Command python).Source
    
    & $nssmPath install $ServiceName $pythonExe $servicePyPath
    & $nssmPath set $ServiceName AppDirectory $InstallDir
    & $nssmPath set $ServiceName DisplayName $ServiceDisplayName
    & $nssmPath set $ServiceName Description $ServiceDescription
    & $nssmPath set $ServiceName Start SERVICE_AUTO_START
    & $nssmPath set $ServiceName AppStdout "$InstallDir\stdout.log"
    & $nssmPath set $ServiceName AppStderr "$InstallDir\stderr.log"
    & $nssmPath set $ServiceName AppRotateFiles 1
    & $nssmPath set $ServiceName AppRotateBytes 1048576
    
    # Start service
    Write-Status "Starting Truth Ledger service..." "INFO"
    Start-Service -Name $ServiceName
    
    # Wait for service to start
    Start-Sleep -Seconds 3
    
    # Verify service is running
    $service = Get-Service -Name $ServiceName
    if ($service.Status -eq "Running") {
        Write-Status "Service started successfully!" "SUCCESS"
    } else {
        Write-Status "Service failed to start" "ERROR"
        exit 1
    }
    
    # Show summary
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "INSTALLATION COMPLETE" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Service Name: $ServiceName" -ForegroundColor Gray
    Write-Host "Install Directory: $InstallDir" -ForegroundColor Gray
    Write-Host "Database: $InstallDir\PHOENIX\truth_ledger.db" -ForegroundColor Gray
    Write-Host "Logs: $InstallDir\truth_ledger.log" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Service Status: " -NoNewline -ForegroundColor Gray
    Write-Host "RUNNING" -ForegroundColor Green
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Yellow
    Write-Host "  View status:  Get-Service $ServiceName" -ForegroundColor Gray
    Write-Host "  Stop service: Stop-Service $ServiceName" -ForegroundColor Gray
    Write-Host "  Start service: Start-Service $ServiceName" -ForegroundColor Gray
    Write-Host "  View logs:    Get-Content $InstallDir\truth_ledger.log -Tail 50 -Wait" -ForegroundColor Gray
    Write-Host "  Check DB:     sqlite3 $InstallDir\PHOENIX\truth_ledger.db 'SELECT COUNT(*) FROM checks;'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Data collection has started!" -ForegroundColor Green
    Write-Host "Check back in 1 hour to see first results." -ForegroundColor Gray
    Write-Host ""
}

function Uninstall-TruthLedger {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "TRUTH LEDGER UNINSTALLER" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $nssmPath = Join-Path $InstallDir "nssm.exe"
    
    if (-not (Test-Path $nssmPath)) {
        Write-Status "NSSM not found, service may not be installed" "WARNING"
        return
    }
    
    # Stop and remove service
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Status "Stopping service..." "INFO"
        Stop-Service -Name $ServiceName -Force
        
        Write-Status "Removing service..." "INFO"
        & $nssmPath remove $ServiceName confirm
        
        Write-Status "Service removed" "SUCCESS"
    } else {
        Write-Status "Service not found" "WARNING"
    }
    
    # Ask about data deletion
    Write-Host ""
    $response = Read-Host "Delete installation directory ($InstallDir)? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Status "Deleting $InstallDir..." "INFO"
        Remove-Item -Path $InstallDir -Recurse -Force
        Write-Status "Uninstallation complete" "SUCCESS"
    } else {
        Write-Status "Installation directory preserved" "INFO"
    }
    
    Write-Host ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if ($Uninstall) {
    Uninstall-TruthLedger
} else {
    Install-TruthLedger
}
