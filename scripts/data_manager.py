import os
import csv
import logging
from datetime import datetime
from collections import deque
from typing import List, Tuple, Optional, Deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataManager")

class DataManager:
    """
    Manages data storage, retrieval, and persistence for WiFi monitoring sessions.
    
    This class handles:
    - Circular buffer for real-time historical data
    - CSV file operations for data backup and restoration
    - Session data management with timestamp tracking
    """
    
    def __init__(self, buffer_size: int = 60, data_dir: str = "data"):
        """
        Initialize the DataManager with specified buffer size and data directory.
        
        Args:
            buffer_size: Maximum number of data points to keep in memory (default: 60)
            data_dir: Directory to store CSV data files (default: "data")
        """
        self.buffer_size = buffer_size
        self.data_dir = data_dir
        self.history: Deque[Tuple[datetime, float, float]] = deque(maxlen=buffer_size)
        self.session_start_time = datetime.now()
        
        # Ensure data directory exists
        try:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"Created data directory: {data_dir}")
        except Exception as e:
            logger.error(f"Failed to create data directory: {e}")
            
    def add_data_point(self, upload_speed: float, download_speed: float) -> None:
        """
        Add a new data point to the history buffer.
        
        Args:
            upload_speed: Upload speed in MB/s
            download_speed: Download speed in MB/s
        """
        timestamp = datetime.now()
        self.history.append((timestamp, upload_speed, download_speed))
        
    def get_history(self) -> List[Tuple[datetime, float, float]]:
        """
        Get all historical data points currently in the buffer.
        
        Returns:
            List of tuples containing (timestamp, upload_speed, download_speed)
        """
        return list(self.history)
    
    def clear_history(self) -> None:
        """Clear all historical data points from the buffer."""
        try:
            self.history.clear()
            logger.info("Historical data cleared")
        except Exception as e:
            logger.error(f"Failed to clear historical data: {e}")
    
    def save_to_csv(self, filename: Optional[str] = None) -> bool:
        """
        Save current session data to a CSV file.
        
        Args:
            filename: Name of the CSV file (default: auto-generated based on timestamp)
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not filename:
            # Generate filename based on session start time
            timestamp = self.format_timestamp_for_filename(self.session_start_time)
            filename = f"wifi_session_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                csv_writer.writerow(['Timestamp', 'Upload Speed (MB/s)', 'Download Speed (MB/s)'])
                
                # Write data
                for timestamp, upload, download in self.history:
                    formatted_timestamp = self.format_timestamp(timestamp)
                    csv_writer.writerow([formatted_timestamp, upload, download])
            
            logger.info(f"Session data saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session data to CSV: {e}")
            return False
    
    def load_from_csv(self, filename: str) -> bool:
        """
        Load session data from a CSV file into the history buffer.
        
        Args:
            filename: Name of the CSV file to load from
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return False
        
        try:
            # Clear existing history
            self.clear_history()
            
            with open(filepath, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader)  # Skip header row
                
                for row in csv_reader:
                    if len(row) >= 3:
                        try:
                            timestamp = self.parse_timestamp(row[0])
                            upload = float(row[1])
                            download = float(row[2])
                            self.history.append((timestamp, upload, download))
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Skipping malformed row in CSV: {e}")
            
            logger.info(f"Loaded {len(self.history)} data points from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load data from CSV: {e}")
            return False
    
    def list_available_sessions(self) -> List[str]:
        """
        List all available session CSV files in the data directory.
        
        Returns:
            List of filenames of available session data files
        """
        try:
            if not os.path.exists(self.data_dir):
                return []
                
            files = [f for f in os.listdir(self.data_dir) 
                    if f.startswith('wifi_session_') and f.endswith('.csv')]
            return sorted(files)
        except Exception as e:
            logger.error(f"Failed to list available sessions: {e}")
            return []
    
    def delete_session_file(self, filename: str) -> bool:
        """
        Delete a session data file.
        
        Args:
            filename: Name of the CSV file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return False
            
        try:
            os.remove(filepath)
            logger.info(f"Deleted session file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session file: {e}")
            return False
    
    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """
        Format a timestamp for display.
        
        Args:
            timestamp: Datetime object to format
            
        Returns:
            Formatted timestamp string (YYYY-MM-DD HH:MM:SS)
        """
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_timestamp_for_filename(timestamp: datetime) -> str:
        """
        Format a timestamp for use in filenames.
        
        Args:
            timestamp: Datetime object to format
            
        Returns:
            Formatted timestamp string (YYYYMMDD_HHMMSS)
        """
        return timestamp.strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> datetime:
        """
        Parse a timestamp string back into a datetime object.
        
        Args:
            timestamp_str: Timestamp string to parse (YYYY-MM-DD HH:MM:SS)
            
        Returns:
            Datetime object
        """
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")


# Simple test if the file is run directly
if __name__ == "__main__":
    # Create data manager
    dm = DataManager()
    
    # Add some test data
    for i in range(10):
        dm.add_data_point(i * 0.1, i * 0.2)
    
    # Display current history
    print(f"Current history ({len(dm.get_history())} points):")
    for point in dm.get_history():
        print(f"  {dm.format_timestamp(point[0])}: Up: {point[1]:.2f} MB/s, Down: {point[2]:.2f} MB/s")
    
    # Save to CSV
    dm.save_to_csv("test_session.csv")
    
    # Clear history
    dm.clear_history()
    print(f"After clearing: {len(dm.get_history())} points")
    
    # Load from CSV
    dm.load_from_csv("test_session.csv")
    print(f"After loading: {len(dm.get_history())} points")
    
    # List available sessions
    print(f"Available sessions: {dm.list_available_sessions()}")

