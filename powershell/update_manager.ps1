<#
.SYNOPSIS
AutoPatch Guardian Update Management Script

.DESCRIPTION
Manages Windows Update operations including checking, installing, 
and rolling back updates for the AutoPatch Guardian toolkit.
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('CheckUpdates', 'InstallUpdates', 'RollbackUpdates')]
    [string]$Action = 'CheckUpdates',

    [Parameter(Mandatory=$false)]
    [string[]]$Updates = @(),

    [Parameter(Mandatory=$false)]
    [string]$UpdateID = $null
)

# Ensure script runs with administrative privileges
function Verify-AdminRights {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check for Pending Windows Updates
function Get-PendingUpdates {
    try {
        # Use Windows Update PowerShell module
        Import-Module PSWindowsUpdate -ErrorAction Stop

        # Get list of pending updates
        $pendingUpdates = Get-WindowsUpdate -NotInstalled -ErrorAction Stop

        # Output update names
        $pendingUpdates | ForEach-Object {
            Write-Output $_.Title
        }
    }
    catch {
        Write-Error "Error checking for updates: $_"
        return $null
    }
}

# Install Specified Windows Updates
function Install-SpecificUpdates {
    param([string[]]$UpdatesToInstall)

    try {
        Import-Module PSWindowsUpdate -ErrorAction Stop

        # If no specific updates provided, get all pending
        if ($UpdatesToInstall.Count -eq 0) {
            $UpdatesToInstall = (Get-WindowsUpdate -NotInstalled).KB
        }

        # Install updates
        $installResults = Install-WindowsUpdate -KBArticleID $UpdatesToInstall -AcceptAll -AutoReboot

        # Output installation results
        $installResults | ForEach-Object {
            Write-Output "Installed Update: $($_.KB) - Status: $($_.Status)"
        }
    }
    catch {
        Write-Error "Error installing updates: $_"
        return $null
    }
}

# Rollback Specific Update
function Rollback-Update {
    param([string]$UpdateToRollback)

    try {
        # Use DISM for update rollback
        if ($UpdateToRollback) {
            $result = DISM.exe /Online /Remove-Package /PackageName:$UpdateToRollback
            Write-Output $result
        }
        else {
            # Rollback most recent update if no specific update provided
            $result = WUSA.exe /Uninstall /KB:$((Get-HotFix | Sort-Object InstalledOn -Descending)[0].HotFixID)
            Write-Output $result
        }
    }
    catch {
        Write-Error "Error rolling back update: $_"
        return $null
    }
}

# Main Script Execution
if (-not (Verify-AdminRights)) {
    Write-Error "This script requires administrative privileges."
    exit 1
}

# Execute requested action
switch ($Action) {
    'CheckUpdates' {
        Get-PendingUpdates
    }
    'InstallUpdates' {
        Install-SpecificUpdates -UpdatesToInstall $Updates
    }
    'RollbackUpdates' {
        Rollback-Update -UpdateToRollback $UpdateID
    }
    default {
        Write-Error "Invalid action specified."
        exit 1
    }
}