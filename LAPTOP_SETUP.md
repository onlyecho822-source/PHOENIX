# PHOENIX LAPTOP SETUP - WINDOWS

**Purpose:** Sync all PHOENIX repositories to your Windows laptop automatically  
**Time:** 5 minutes setup, then automatic forever  
**Requirements:** Windows 10/11, Git for Windows

---

## QUICK START (5 MINUTES)

### Step 1: Install Git (if not already installed)

1. Download Git for Windows: https://git-scm.com/download/win
2. Run installer (use default settings)
3. Verify installation:
   ```powershell
   git --version
   ```

### Step 2: Set Your GitHub PAT

Open PowerShell and run:

```powershell
# Set your Personal Access Token (replace with your actual token)
$env:GITHUB_PAT = "ghp_your_token_here"

# Make it permanent (optional but recommended)
[System.Environment]::SetEnvironmentVariable("GITHUB_PAT", "ghp_your_token_here", "User")
```

**Don't have a PAT?** Create one at: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scopes: `repo`, `workflow`
- Copy the token (you won't see it again!)

### Step 3: Download and Run Sync Script

```powershell
# Navigate to your preferred directory
cd C:\Users\$env:USERNAME\Downloads

# Download sync script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/onlyecho822-source/PHOENIX/main/sync_laptop.ps1" -OutFile "sync_laptop.ps1"

# Run first-time setup
.\sync_laptop.ps1 -FirstRun
```

**That's it!** Your repositories are now synced to:
```
C:\Users\YourUsername\EchoUniverse\
  ├── PHOENIX\
  ├── Echo\
  └── Echo-AI-University\
```

---

## WHAT IT DOES

### Automatic Sync
- Clones all PHOENIX repositories on first run
- Pulls latest changes on subsequent runs
- Preserves your local changes (won't overwrite)
- Shows sync summary with stats

### Smart Features
- **PAT Authentication:** Uses your GitHub token (no password prompts)
- **Change Detection:** Skips pull if you have local modifications
- **Statistics:** Shows files, commits, size for each repo
- **Scheduled Task:** Optionally runs every 30 minutes automatically

---

## USAGE

### Manual Sync (anytime)
```powershell
cd C:\Users\$env:USERNAME\EchoUniverse
.\PHOENIX\sync_laptop.ps1
```

### First-Time Setup
```powershell
.\sync_laptop.ps1 -FirstRun
```
This will offer to create a scheduled task for automatic syncing.

### Custom Base Directory
```powershell
.\sync_laptop.ps1 -BaseDir "D:\MyProjects\Echo"
```

### Verbose Output
```powershell
.\sync_laptop.ps1 -Verbose
```

---

## SCHEDULED TASK (AUTOMATIC SYNC)

If you chose to create a scheduled task during first run, it will:
- Run every 30 minutes
- Sync all repositories automatically
- Run in background (no window popup)

### Manage Scheduled Task
1. Open Task Scheduler (`taskschd.msc`)
2. Find "PHOENIX-Laptop-Sync" in Task Scheduler Library
3. Right-click to:
   - Disable (pause automatic sync)
   - Edit (change frequency)
   - Delete (remove automation)

### Change Sync Frequency
In Task Scheduler:
1. Right-click "PHOENIX-Laptop-Sync" → Properties
2. Triggers tab → Edit
3. Change "Repeat task every" to your preference:
   - 15 minutes (aggressive)
   - 1 hour (balanced)
   - 4 hours (conservative)

---

## TROUBLESHOOTING

### "Git is not installed"
Install Git for Windows: https://git-scm.com/download/win

### "GitHub PAT not provided"
Set your token:
```powershell
$env:GITHUB_PAT = "ghp_your_token_here"
```

### "Authentication failed"
Your PAT might be expired or invalid:
1. Go to https://github.com/settings/tokens
2. Generate a new token
3. Update your environment variable

### "Local changes - skipping pull"
You have uncommitted changes in that repository. Either:
- Commit your changes: `git add . && git commit -m "Your message"`
- Stash your changes: `git stash`
- Or leave them (script won't overwrite)

### Script won't run (execution policy)
Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## WHAT GETS SYNCED

### PHOENIX Repository
- Truth Ledger system
- API monitoring code
- Hardening scripts
- Documentation

### Echo Repository
- Main Echo Universe codebase
- Agent implementations
- Constellation management

### Echo-AI-University Repository
- Training systems
- Test results
- Curriculum data
- Agent certifications

---

## ADVANCED FEATURES

### Add More Repositories

Edit `sync_laptop.ps1` and add to the `$Repositories` array:

```powershell
$Repositories = @(
    "PHOENIX",
    "Echo",
    "Echo-AI-University",
    "YourNewRepo"  # Add here
)
```

### Sync Specific Repos Only

```powershell
# Edit the script to comment out repos you don't want:
$Repositories = @(
    "PHOENIX",
    # "Echo",  # Commented out - won't sync
    "Echo-AI-University"
)
```

### Change GitHub Username

If syncing from a different account:

```powershell
# Edit sync_laptop.ps1
$GitHubUsername = "your-github-username"
```

---

## SECURITY NOTES

### PAT Storage
- Stored in Windows environment variables (encrypted by Windows)
- Only accessible to your user account
- Not visible in Task Manager or process lists

### Best Practices
- Use a PAT with minimal required scopes (`repo` only if possible)
- Regenerate PAT every 90 days
- Never commit PAT to repositories
- Don't share your PAT with anyone

### Revoke PAT
If compromised, immediately revoke at:
https://github.com/settings/tokens

---

## SYNC SUMMARY OUTPUT

After each sync, you'll see:

```
============================================================================
SYNC SUMMARY
============================================================================

  PHOENIX
    Files: 110
    Commits: 47
    Size: 0.52 MB

  Echo
    Files: 234
    Commits: 156
    Size: 1.23 MB

  Echo-AI-University
    Files: 89
    Commits: 92
    Size: 0.18 MB

============================================================================
SYNC COMPLETE
============================================================================

Base directory: C:\Users\YourName\EchoUniverse
Repositories synced: 3
```

---

## UNINSTALL

### Remove Scheduled Task
```powershell
Unregister-ScheduledTask -TaskName "PHOENIX-Laptop-Sync" -Confirm:$false
```

### Remove Environment Variable
```powershell
[System.Environment]::SetEnvironmentVariable("GITHUB_PAT", $null, "User")
```

### Delete Repositories
```powershell
Remove-Item -Recurse -Force C:\Users\$env:USERNAME\EchoUniverse
```

---

## SUPPORT

**Issues?** Check:
1. Git is installed: `git --version`
2. PAT is set: `$env:GITHUB_PAT` (should show your token)
3. Internet connection is active
4. GitHub is accessible: https://github.com

**Still stuck?** Open an issue at:
https://github.com/onlyecho822-source/PHOENIX/issues

---

## NEXT STEPS

After syncing, you can:

1. **Deploy Truth Ledger to VPS**
   ```powershell
   cd C:\Users\$env:USERNAME\EchoUniverse\PHOENIX
   # Follow QUICKSTART.md
   ```

2. **Run Hardening Scripts**
   ```powershell
   cd C:\Users\$env:USERNAME\EchoUniverse\PHOENIX\hardening
   # Review README.md
   ```

3. **Explore Echo Universe**
   ```powershell
   cd C:\Users\$env:USERNAME\EchoUniverse\Echo
   # Check documentation
   ```

---

**Last Updated:** 2026-01-11  
**Version:** 1.0.0  
**Status:** Production-Ready
