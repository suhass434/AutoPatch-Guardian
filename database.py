import sqlite3
import os
from typing import List, Dict, Any

class DatabaseManager:
    """
    Manages SQLite database operations for AutoPatch Guardian.
    Handles device health, update logs, and compliance reporting.
    """
    def __init__(self, db_path: str = 'autopatch_guardian.db'):
        """
        Initialize database connection and create necessary tables.
        
        :param db_path: Path to the SQLite database file
        """
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        
        # Establish database connection
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self._create_tables()
    
    def _create_tables(self):
        """Create essential tables for tracking updates and device health."""
        # Device health tracking table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_health TEXT,
                status TEXT
            )
        ''')
        
        # Windows update logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                update_name TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # Commit changes
        self.conn.commit()
    
    def log_device_health(self, health_data: Dict[str, Any]):
        """
        Log device health metrics to the database.
        
        :param health_data: Dictionary containing device health information
        """
        try:
            self.cursor.execute('''
                INSERT INTO device_health 
                (cpu_usage, memory_usage, disk_health, status) 
                VALUES (?, ?, ?, ?)
            ''', (
                health_data.get('cpu_usage', 0),
                health_data.get('memory_usage', 0),
                health_data.get('disk_health', 'Unknown'),
                health_data.get('status', 'OK')
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error when logging device health: {e}")
    
    def log_update(self, update_name: str, status: str, details: str = ''):
        """
        Log Windows update information.
        
        :param update_name: Name of the update
        :param status: Update installation status
        :param details: Additional update details
        """
        try:
            self.cursor.execute('''
                INSERT INTO update_logs 
                (update_name, status, details) 
                VALUES (?, ?, ?)
            ''', (update_name, status, details))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error when logging update: {e}")
    
    def get_recent_device_health(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent device health records.
        
        :param limit: Number of recent records to fetch
        :return: List of device health records
        """
        try:
            self.cursor.execute('''
                SELECT * FROM device_health 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error when fetching device health: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        self.conn.close()

# Ensure proper database closure
import atexit

db_manager = DatabaseManager()
atexit.register(db_manager.close)