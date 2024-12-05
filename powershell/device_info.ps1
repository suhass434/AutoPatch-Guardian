<#
.SYNOPSIS
AutoPatch Guardian Device Information Script

.DESCRIPTION
Retrieves system health metrics and device configuration details
for the AutoPatch Guardian toolkit.
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('GetSystemHealth', 'GetDeviceConfig')]
    [string]$Action = 'GetSystemHealth'
)

# Get System Health Metrics
function Get-SystemHealth {
    try {
        # CPU Usage
        $cpuUsage = (Get-WmiObject Win32_Processor).LoadPercentage

        # Memory Usage
        $memoryMetrics = Get-WmiObject Win32_OperatingSystem
        $totalMemory = $memoryMetrics.TotalVisibleMemorySize
        $freeMemory = $memoryMetrics.FreePhysicalMemory
        $memoryUsagePercent = [math]::Round((($totalMemory - $freeMemory) / $totalMemory) * 100, 2)

        # Disk Health (Simple check)
        $diskCheck = Get-WmiObject Win32_LogicalDisk | 
            Where-Object { $_.DeviceID -eq $env:SystemDrive } | 
            Select-Object @{
                Name='DiskHealth';
                Expression={
                    if ($_.Size -gt 0) {
                        $freeSpacePercent = [math]::Round(($_.FreeSpace / $_.Size) * 100, 2)
                        if ($freeSpacePercent -lt 10) { "LOW" }
                        elseif ($freeSpacePercent -lt 20) { "MEDIUM" }
                        else { "GOOD" }
                    }
                    else { "UNKNOWN" }
                }
            }

        # Output as pipe-separated values
        Write-Output "$cpuUsage|$memoryUsagePercent|$($diskCheck.DiskHealth)"
    }
    catch {
        Write-Error "Error collecting system health: $_"
        return $null
    }
}

# Get Comprehensive Device Configuration
function Get-DeviceConfiguration {
    try {
        # Total Physical Memory
        $memoryInfo = (Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB

        # Storage Information
        $storageInfo = Get-WmiObject Win32_LogicalDisk | 
            Where-Object { $_.DeviceID -eq $env:SystemDrive } | 
            Select-Object @{
                Name='StorageInfo';
                Expression={
                    "$([math]::Round($_.Size / 1GB, 2)) GB Total, " +
                    "$([math]::Round($_.FreeSpace / 1GB, 2)) GB Free"
                }
            }

        # Output as pipe-separated values
        Write-Output "$([math]::Round($memoryInfo, 2)) GB|$($storageInfo.StorageInfo)"
    }
    catch {
        Write-Error "Error collecting device configuration: $_"
        return $null
    }
}

# Main Script Execution
switch ($Action) {
    'GetSystemHealth' {
        Get-SystemHealth
    }
    'GetDeviceConfig' {
        Get-DeviceConfiguration
    }
    default {
        Write-Error "Invalid action specified."
        exit 1
    }
}