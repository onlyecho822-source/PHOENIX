# ============================================================================
# PHOENIX LAPTOP SYNC - COMPREHENSIVE AUTOMATION
# ============================================================================
# Purpose: Sync all GitHub repositories to Windows laptop with PAT authentication
# Usage: .\sync_laptop.ps1
# Requirements: Git for Windows, PowerShell 5.1+
# ============================================================================

param(
    [string]$PAT = $env:GITHUB_PAT,
    [string]$BaseDir = "C:\Users\$env:USERNAME\EchoUniverse",
    [switch]$FirstRun,
    [switch]$Verbose
)

# Configuration
$ErrorActionPreference = "Stop"
$GitHubUsername = "onlyecho822-source"

# Repositories to sync
$Repositories = @(
    "PHOENIX",
    "Echo",
    "Echo-AI-University"
)

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

function Test-GitInstalled {
    try {
        $null = git --version
        return $true
    } catch {
        return $false
    }
}

function Initialize-GitConfig {
    Write-Status "Configuring Git..." "INFO"
    
    # Set user info (if not already set)
    $gitUser = git config --global user.name
    if (-not $gitUser) {
        git config --global user.name "Echo Universe"
        Write-Status "Set Git user.name" "SUCCESS"
    }
    
    $gitEmail = git config --global user.email
    if (-not $gitEmail) {
        git config --global user.email "npoinsette@gmail.com"
        Write-Status "Set Git user.email" "SUCCESS"
    }
    
    # Configure credential helper for Windows
    git config --global credential.helper wincred
    
    # Configure line endings for Windows
    git config --global core.autocrlf true
    
    Write-Status "Git configuration complete" "SUCCESS"
}

function Clone-Repository {
    param(
        [string]$RepoName,
        [string]$TargetDir,
        [string]$Token
    )
    
    $repoUrl = "https://${Token}@github.com/${GitHubUsername}/${RepoName}.git"
    
    Write-Status "Cloning $RepoName..." "INFO"
    
    try {
        git clone $repoUrl $TargetDir 2>&1 | Out-Null
        Write-Status "Cloned $RepoName successfully" "SUCCESS"
        return $true
    } catch {
        Write-Status "Failed to clone $RepoName : $_" "ERROR"
        return $false
    }
}

function Update-Repository {
    param(
        [string]$RepoPath,
        [string]$RepoName
    )
    
    Write-Status "Updating $RepoName..." "INFO"
    
    Push-Location $RepoPath
    
    try {
        # Fetch latest changes
        git fetch origin 2>&1 | Out-Null
        
        # Check if there are changes
        $status = git status --porcelain
        
        if ($status) {
            Write-Status "$RepoName has local changes - skipping pull" "WARNING"
            Write-Host "  Local changes:"
            git status --short
        } else {
            # Pull latest changes
            git pull origin main 2>&1 | Out-Null
            Write-Status "Updated $RepoName successfully" "SUCCESS"
        }
        
        # Show latest commit
        $latestCommit = git log -1 --oneline
        Write-Host "  Latest: $latestCommit" -ForegroundColor Gray
        
    } catch {
        Write-Status "Failed to update $RepoName : $_" "ERROR"
    } finally {
        Pop-Location
    }
}

function Get-RepositoryStats {
    param([string]$RepoPath)
    
    Push-Location $RepoPath
    
    try {
        $files = (git ls-files | Measure-Object).Count
        $commits = (git rev-list --count HEAD)
        $branches = (git branch -a | Measure-Object).Count
        $size = (Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
        
        return @{
            Files = $files
            Commits = $commits
            Branches = $branches
            SizeMB = [math]::Round($size, 2)
        }
    } finally {
        Pop-Location
    }
}

function Show-SyncSummary {
    param([hashtable]$Results)
    
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "SYNC SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($repo in $Results.Keys) {
        $stats = $Results[$repo]
        Write-Host "  $repo" -ForegroundColor Yellow
        Write-Host "    Files: $($stats.Files)" -ForegroundColor Gray
        Write-Host "    Commits: $($stats.Commits)" -ForegroundColor Gray
        Write-Host "    Size: $($stats.SizeMB) MB" -ForegroundColor Gray
        Write-Host ""
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "PHOENIX LAPTOP SYNC - COMPREHENSIVE AUTOMATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Status "Checking prerequisites..." "INFO"

if (-not (Test-GitInstalled)) {
    Write-Status "Git is not installed!" "ERROR"
    Write-Host ""
    Write-Host "Please install Git for Windows from: https://git-scm.com/download/win"
    exit 1
}

# Check PAT
if (-not $PAT) {
    Write-Status "GitHub PAT not provided!" "ERROR"
    Write-Host ""
    Write-Host "Please provide your GitHub Personal Access Token:"
    Write-Host "  Method 1: Set environment variable: `$env:GITHUB_PAT = 'your_token'"
    Write-Host "  Method 2: Run with parameter: .\sync_laptop.ps1 -PAT 'your_token'"
    Write-Host ""
    Write-Host "Create PAT at: https://github.com/settings/tokens"
    Write-Host "Required scopes: repo, workflow"
    exit 1
}

Write-Status "Prerequisites OK" "SUCCESS"

# Initialize Git configuration
Initialize-GitConfig

# Create base directory
if (-not (Test-Path $BaseDir)) {
    Write-Status "Creating base directory: $BaseDir" "INFO"
    New-Item -ItemType Directory -Path $BaseDir -Force | Out-Null
}

# Sync repositories
$syncResults = @{}

foreach ($repo in $Repositories) {
    $repoPath = Join-Path $BaseDir $repo
    
    Write-Host ""
    Write-Host "------------------------------------------------------------------------" -ForegroundColor Gray
    
    if (Test-Path $repoPath) {
        # Repository exists - update it
        Update-Repository -RepoPath $repoPath -RepoName $repo
    } else {
        # Repository doesn't exist - clone it
        Clone-Repository -RepoName $repo -TargetDir $repoPath -Token $PAT
    }
    
    # Get repository statistics
    if (Test-Path $repoPath) {
        $stats = Get-RepositoryStats -RepoPath $repoPath
        $syncResults[$repo] = $stats
    }
}

# Show summary
Show-SyncSummary -Results $syncResults

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "SYNC COMPLETE" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Base directory: $BaseDir" -ForegroundColor Gray
Write-Host "Repositories synced: $($Repositories.Count)" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# OPTIONAL: CREATE SCHEDULED TASK
# ============================================================================

if ($FirstRun) {
    Write-Host ""
    Write-Status "First run detected - setting up automation..." "INFO"
    
    $taskName = "PHOENIX-Laptop-Sync"
    $scriptPath = $MyInvocation.MyCommand.Path
    
    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($existingTask) {
        Write-Status "Scheduled task already exists" "WARNING"
    } else {
        Write-Host ""
        Write-Host "Do you want to create a scheduled task to run this sync automatically?"
        Write-Host "  Frequency: Every 30 minutes"
        Write-Host "  (You can modify this later in Task Scheduler)"
        Write-Host ""
        $response = Read-Host "Create scheduled task? (Y/N)"
        
        if ($response -eq "Y" -or $response -eq "y") {
            try {
                # Create action
                $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
                    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
                
                # Create trigger (every 30 minutes)
                $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)
                
                # Create principal (run as current user)
                $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
                
                # Register task
                Register-ScheduledTask -TaskName $taskName `
                    -Action $action `
                    -Trigger $trigger `
                    -Principal $principal `
                    -Description "Automatically sync PHOENIX repositories from GitHub"
                
                Write-Status "Scheduled task created successfully" "SUCCESS"
                Write-Host "  Task name: $taskName"
                Write-Host "  Frequency: Every 30 minutes"
                Write-Host "  Manage at: Task Scheduler > Task Scheduler Library"
            } catch {
                Write-Status "Failed to create scheduled task: $_" "ERROR"
            }
        }
    }
}

Write-Host ""
Write-Status "All operations complete" "SUCCESS"
Write-Host ""
