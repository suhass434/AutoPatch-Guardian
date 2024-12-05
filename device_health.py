import subprocess
import os
import platform
from typing import Dict, Any

class DeviceHealthMonitor:
    """
    Monitors and retrieves system health metrics and device configuration.
    Integrates with PowerShell for comprehensive system information gathering.
    """
    def __init__(self, powershell_script_path: str = None):
        """
        Initialize Device Health Monitor.
        
        :param powershell_script_path: Path to PowerShell device info script
        """
        # Default script path if not provided
        if not powershell_script_path:
            powershell_script_path = os.path.join(
                os.path.dirname(__file__), 
                'powershell', 
                'device_info.ps1'
            )
        
        self.script_path = powershell_script_path
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Collect system health metrics.
        
        :return: Dictionary of system health information
        """
        try:
            # Execute PowerShell script to get system health
            result = subprocess.run(
                ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', self.script_path, 
                 '-Action', 'GetSystemHealth'],
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                # Parse system health metrics
                # This is a simplified mock implementation
                return {
                    'cpu_usage': float(result.stdout.split('|')[0] or 0),
                    'memory_usage': float(result.stdout.split('|')[1] or 0),
                    'disk_health': result.stdout.split('|')[2] or 'Unknown',
                    'status': 'OK' if float(result.stdout.split('|')[0] or 0) < 80 else 'WARNING'
                }
            else:
                return {
                    'status': 'error',
                    'message': result.stderr
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_device_configuration(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive device configuration details.
        
        :return: Dictionary of device configuration information
        """
        try:
            # Execute PowerShell script to get device configuration
            result = subprocess.run(
                ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', self.script_path, 
                 '-Action', 'GetDeviceConfig'],
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                # Parse device configuration
                # This is a simplified mock implementation
                config_data = result.stdout.split('|')
                return {
                    'os_version': platform.version(),
                    'os_name': platform.system(),
                    'hostname': platform.node(),
                    'processor': platform.processor(),
                    'total_memory': config_data[0] if config_data else 'Unknown',
                    'storage_info': config_data[1] if len(config_data) > 1 else 'Unknown'
                }
            else:
                return {
                    'status': 'error',
                    'message': result.stderr
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# Singleton instance for global access
device_health_monitor = DeviceHealthMonitor()