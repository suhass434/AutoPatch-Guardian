import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHBoxLayout, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# Import custom modules
from database import db_manager
from update_tracker import update_tracker
from device_health import device_health_monitor

class AutoPatchGuardianApp(QMainWindow):
    """
    Main application window for AutoPatch Guardian.
    Provides dashboard and management interfaces for system updates and health.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoPatch Guardian - Windows Update Management")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create main tab widget
        self.main_tabs = QTabWidget()
        self.setCentralWidget(self.main_tabs)
        
        # Create tabs
        self.create_update_tab()
        self.create_device_health_tab()
        self.create_logs_tab()
        
        # Setup periodic refresh
        self.setup_periodic_refresh()
    
    def create_update_tab(self):
        """Create tab for update management and tracking."""
        update_tab = QWidget()
        update_layout = QVBoxLayout()
        
        # Pending Updates Section
        pending_updates_label = QLabel("Pending Windows Updates:")
        pending_updates_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        self.pending_updates_table = QTableWidget()
        self.pending_updates_table.setColumnCount(2)
        self.pending_updates_table.setHorizontalHeaderLabels(["Update Name", "Status"])
        
        # Update Actions
        update_actions_layout = QHBoxLayout()
        check_updates_btn = QPushButton("Check for Updates")
        check_updates_btn.clicked.connect(self.refresh_pending_updates)
        install_updates_btn = QPushButton("Install Selected Updates")
        install_updates_btn.clicked.connect(self.install_selected_updates)
        rollback_updates_btn = QPushButton("Rollback Last Update")
        rollback_updates_btn.clicked.connect(self.rollback_updates)
        
        update_actions_layout.addWidget(check_updates_btn)
        update_actions_layout.addWidget(install_updates_btn)
        update_actions_layout.addWidget(rollback_updates_btn)
        
        # Add widgets to layout
        update_layout.addWidget(pending_updates_label)
        update_layout.addWidget(self.pending_updates_table)
        update_layout.addLayout(update_actions_layout)
        
        update_tab.setLayout(update_layout)
        self.main_tabs.addTab(update_tab, "Update Management")
    
    def create_device_health_tab(self):
        """Create tab for monitoring device health and configuration."""
        device_health_tab = QWidget()
        device_health_layout = QVBoxLayout()
        
        # System Health Section
        system_health_label = QLabel("System Health Overview:")
        system_health_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        self.system_health_text = QTextEdit()
        self.system_health_text.setReadOnly(True)
        
        # Device Configuration Section
        device_config_label = QLabel("Device Configuration:")
        device_config_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        self.device_config_text = QTextEdit()
        self.device_config_text.setReadOnly(True)
        
        # Refresh Button
        refresh_health_btn = QPushButton("Refresh Device Health")
        refresh_health_btn.clicked.connect(self.refresh_device_health)
        
        # Add widgets to layout
        device_health_layout.addWidget(system_health_label)
        device_health_layout.addWidget(self.system_health_text)
        device_health_layout.addWidget(device_config_label)
        device_health_layout.addWidget(self.device_config_text)
        device_health_layout.addWidget(refresh_health_btn)
        
        device_health_tab.setLayout(device_health_layout)
        self.main_tabs.addTab(device_health_tab, "Device Health")
    
    def create_logs_tab(self):
        """Create tab for displaying system logs."""
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        
        # Update Logs Section
        update_logs_label = QLabel("Update Logs:")
        update_logs_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        self.update_logs_table = QTableWidget()
        self.update_logs_table.setColumnCount(4)
        self.update_logs_table.setHorizontalHeaderLabels(["Timestamp", "Update Name", "Status", "Details"])
        
        # Add widgets to layout
        logs_layout.addWidget(update_logs_label)
        logs_layout.addWidget(self.update_logs_table)
        
        logs_tab.setLayout(logs_layout)
        self.main_tabs.addTab(logs_tab, "System Logs")
    
    def setup_periodic_refresh(self):
        """Setup periodic refresh for various system components."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.periodic_refresh)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes
    
    def periodic_refresh(self):
        """Perform periodic refresh of system components."""
        self.refresh_pending_updates()
        self.refresh_device_health()
        self.refresh_update_logs()
    
    def refresh_pending_updates(self):
        """Refresh pending Windows updates."""
        try:
            # Clear existing table
            self.pending_updates_table.setRowCount(0)
            
            # Check for updates
            updates_info = update_tracker.check_pending_updates()
            
            if updates_info['status'] == 'success':
                pending_updates = updates_info.get('pending_updates', [])
                
                # Populate table
                self.pending_updates_table.setRowCount(len(pending_updates))
                for row, update in enumerate(pending_updates):
                    self.pending_updates_table.setItem(row, 0, QTableWidgetItem(str(update)))
                    self.pending_updates_table.setItem(row, 1, QTableWidgetItem("Pending"))
            else:
                QMessageBox.warning(self, "Update Check Error", 
                                    f"Failed to check updates: {updates_info.get('message', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
    
    def install_selected_updates(self):
        """Install selected Windows updates."""
        try:
            # Get selected updates
            selected_rows = self.pending_updates_table.selectionModel().selectedRows()
            updates_to_install = []
            
            for row in selected_rows:
                update_name = self.pending_updates_table.item(row.row(), 0).text()
                updates_to_install.append(update_name)
            
            # Install updates
            result = update_tracker.install_updates(updates_to_install)
            
            if result['status'] == 'success':
                QMessageBox.information(self, "Update Installation", 
                                        f"Updates installed successfully: {result.get('output', '')}")
            else:
                QMessageBox.warning(self, "Update Installation Error", 
                                    f"Failed to install updates: {result.get('error', 'Unknown error')}")
            
            # Refresh updates list
            self.refresh_pending_updates()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
    
    def rollback_updates(self):
        """Rollback recent Windows updates."""
        try:
            result = update_tracker.rollback_updates()
            
            if result['status'] == 'success':
                QMessageBox.information(self, "Update Rollback", 
                                        f"Updates rolled back successfully: {result.get('output', '')}")
            else:
                QMessageBox.warning(self, "Update Rollback Error", 
                                    f"Failed to rollback updates: {result.get('error', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
    
    def refresh_device_health(self):
        """Refresh device health and configuration information."""
        try:
            # Get system health
            health_info = device_health_monitor.get_system_health()
            
            # Display system health
            health_text = f"""
            CPU Usage: {health_info.get('cpu_usage', 'N/A')}%
            Memory Usage: {health_info.get('memory_usage', 'N/A')}%
            Disk Health: {health_info.get('disk_health', 'N/A')}
            Overall Status: {health_info.get('status', 'Unknown')}
            """
            self.system_health_text.setText(health_text)
            
            # Log device health to database
            db_manager.log_device_health(health_info)
            
            # Get device configuration
            config_info = device_health_monitor.get_device_configuration()
            
            # Display device configuration
            config_text = f"""
            OS Version: {config_info.get('os_version', 'N/A')}
            OS Name: {config_info.get('os_name', 'N/A')}
            Hostname: {config_info.get('hostname', 'N/A')}
            Processor: {config_info.get('processor', 'N/A')}
            Total Memory: {config_info.get('total_memory', 'N/A')}
            Storage Info: {config_info.get('storage_info', 'N/A')}
            """
            self.device_config_text.setText(config_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh device health: {str(e)}")
    
    def refresh_update_logs(self):
        """Refresh update logs from the database."""
        try:
            # Fetch recent device health logs
            health_logs = db_manager.get_recent_device_health(10)
            
            # Clear existing table
            self.update_logs_table.setRowCount(0)
            
            # Populate logs table
            for row, log in enumerate(health_logs):
                self.update_logs_table.insertRow(row)
                self.update_logs_table.setItem(row, 0, QTableWidgetItem(str(log.get('timestamp', 'N/A'))))
                self.update_logs_table.setItem(row, 1, QTableWidgetItem('System Health Check'))
                self.update_logs_table.setItem(row, 2, QTableWidgetItem(str(log.get('status', 'N/A'))))
                
                # Combine health details
                details = (f"CPU: {log.get('cpu_usage', 'N/A')}%, "
                           f"Memory: {log.get('memory_usage', 'N/A')}%, "
                           f"Disk: {log.get('disk_health', 'N/A')}")
                self.update_logs_table.setItem(row, 3, QTableWidgetItem(details))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh update logs: {str(e)}")

def main():
    """
    Main entry point for the AutoPatch Guardian application.
    Initializes and runs the PyQt5 application.
    """
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle('Fusion')
    
    # Create and show main window
    main_window = AutoPatchGuardianApp()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()