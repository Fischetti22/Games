#!/usr/bin/env python3
"""
WiFi Traffic Monitor - Network Monitoring Module

This module provides functionality to monitor network interface traffic,
calculate upload and download speeds, and validate network interfaces.
"""

import psutil
import time
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wifi_monitor')

class InterfaceNotFoundError(Exception):
    """Exception raised when the specified network interface is not found."""
    pass

def validate_interface(interface_name):
    """
    Validates if a network interface exists and is up.
    
    Args:
        interface_name (str): Name of the network interface to validate
        
    Returns:
        bool: True if interface exists and is up
        
    Raises:
        InterfaceNotFoundError: If the interface does not exist
    """
    net_stats = psutil.net_if_stats()
    
    if interface_name not in net_stats:
        raise InterfaceNotFoundError(f"Interface '{interface_name}' not found")
    
    return net_stats[interface_name].isup

class SpeedCalculator:
    """
    Class for calculating network upload and download speeds for a specified interface.
    """
    
    def __init__(self, interface_name, history_size=60):
        """
        Initialize the SpeedCalculator with a network interface.
        
        Args:
            interface_name (str): Name of the network interface to monitor
            history_size (int): Number of historical data points to keep
        
        Raises:
            InterfaceNotFoundError: If the interface does not exist
        """
        self.interface_name = interface_name
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
        
        # Validate that the interface exists
        if not validate_interface(interface_name):
            logger.warning(f"Interface {interface_name} is down")
        
        # Get initial counter values
        try:
            counters = psutil.net_io_counters(pernic=True)
            if self.interface_name not in counters:
                raise InterfaceNotFoundError(f"Interface '{interface_name}' not found")
                
            self.last_bytes_sent = counters[self.interface_name].bytes_sent
            self.last_bytes_recv = counters[self.interface_name].bytes_recv
        except (KeyError, AttributeError) as e:
            logger.error(f"Error initializing counters: {e}")
            raise InterfaceNotFoundError(f"Error accessing interface '{interface_name}'")
        
        # Initialize history storage
        self.history = deque(maxlen=history_size)
    
    @staticmethod
    def bytes_to_mb(bytes_count):
        """
        Convert bytes to megabytes.
        
        Args:
            bytes_count (int): Number of bytes
            
        Returns:
            float: Equivalent value in megabytes
        """
        return bytes_count / (1024 * 1024)
    
    @staticmethod
    def bytes_to_mbits(bytes_count):
        """
        Convert bytes to megabits.
        
        Args:
            bytes_count (int): Number of bytes
            
        Returns:
            float: Equivalent value in megabits
        """
        return bytes_count * 8 / (1024 * 1024)
    
    def get_speeds(self):
        """
        Calculate current upload and download speeds.
        
        Returns:
            tuple: (upload_speed_mb, download_speed_mb, upload_speed_mbits, 
                   download_speed_mbits, elapsed_time)
            
        Raises:
            InterfaceNotFoundError: If the interface is no longer available
            ValueError: If there's an issue calculating speeds
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        
        try:
            counters = psutil.net_io_counters(pernic=True)
            
            if self.interface_name not in counters:
                raise InterfaceNotFoundError(f"Interface '{self.interface_name}' not found or disconnected")
            
            current_bytes_sent = counters[self.interface_name].bytes_sent
            current_bytes_recv = counters[self.interface_name].bytes_recv
            
            # Avoid division by zero or negative time intervals
            if elapsed_time <= 0:
                elapsed_time = 0.001
            
            # Calculate bytes transferred during interval
            bytes_sent_diff = current_bytes_sent - self.last_bytes_sent
            bytes_recv_diff = current_bytes_recv - self.last_bytes_recv
            
            # Calculate speeds in MB/s
            upload_speed_mb = self.bytes_to_mb(bytes_sent_diff) / elapsed_time
            download_speed_mb = self.bytes_to_mb(bytes_recv_diff) / elapsed_time
            
            # Calculate speeds in Mbps (megabits per second)
            upload_speed_mbits = self.bytes_to_mbits(bytes_sent_diff) / elapsed_time
            download_speed_mbits = self.bytes_to_mbits(bytes_recv_diff) / elapsed_time
            
            # Update last values for next calculation
            self.last_bytes_sent = current_bytes_sent
            self.last_bytes_recv = current_bytes_recv
            self.last_time = current_time
            
            # Add to history
            timestamp = time.time()
            self.history.append((timestamp, upload_speed_mb, download_speed_mb))
            
            return (upload_speed_mb, download_speed_mb, upload_speed_mbits, 
                    download_speed_mbits, elapsed_time)
            
        except (KeyError, AttributeError) as e:
            logger.error(f"Error calculating speeds: {e}")
            raise ValueError(f"Failed to calculate network speeds: {e}")
    
    def get_history(self):
        """
        Get the history of speed measurements.
        
        Returns:
            deque: Collection of (timestamp, upload_speed_mb, download_speed_mb) tuples
        """
        return self.history


if __name__ == "__main__":
    # Simple test to demonstrate usage
    try:
        # Replace 'wlo1' with your actual WiFi interface name
        interface_name = 'wlo1'
        
        print(f"Validating interface {interface_name}...")
        is_up = validate_interface(interface_name)
        print(f"Interface {interface_name} is {'up' if is_up else 'down'}")
        
        print(f"Starting speed monitoring on {interface_name}...")
        calculator = SpeedCalculator(interface_name)
        
        # Monitor for 5 seconds
        for _ in range(5):
            speeds = calculator.get_speeds()
            print(f"Upload: {speeds[0]:.2f} MB/s ({speeds[2]:.2f} Mbps)")
            print(f"Download: {speeds[1]:.2f} MB/s ({speeds[3]:.2f} Mbps)")
            print("-" * 50)
            time.sleep(1)
        
    except InterfaceNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

