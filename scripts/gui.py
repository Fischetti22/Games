import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading
from datetime import datetime, timedelta
import numpy as np
import sys
import os

# Import from our modules
from wifi_monitor import SpeedCalculator, validate_interface
from data_manager import DataManager

class WiFiMonitorGUI:
    def __init__(self, interface='wlo1'):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("WiFi Traffic Monitor")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize data
        self.interface = interface
        self.running = False
        self.monitoring_thread = None
        self.show_mbps = False  # Default to MB/s
        
        try:
            # Validate interface
            if not validate_interface(self.interface):
                messagebox.showerror("Error", f"Interface {self.interface} not found or not active")
                self.root.destroy()
                return
                
            # Initialize core components
            self.speed_calculator = SpeedCalculator(self.interface)
            self.data_manager = DataManager()
            
            # Create GUI elements
            self.create_widgets()
            
            # Set up plotting
            self.setup_plot()
            
            # Initialize timestamps and data
            self.timestamps = []
            self.download_speeds = []
            self.upload_speeds = []
            
            # Update interval (ms)
            self.update_interval = 1000
            
            # Initial plot update
            self.update_plot()
            
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.root.destroy()
    
    def create_widgets(self):
        # Create frame for stats display
        stats_frame = ttk.LabelFrame(self.root, text="Real-time Network Statistics")
        stats_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Upload stats
        ttk.Label(stats_frame, text="Upload:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.upload_label = ttk.Label(stats_frame, text="0.00 MB/s (0.00 Mbps)")
        self.upload_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Download stats
        ttk.Label(stats_frame, text="Download:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.download_label = ttk.Label(stats_frame, text="0.00 MB/s (0.00 Mbps)")
        self.download_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Create frame for buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Start/Stop button
        self.start_stop_button = ttk.Button(button_frame, text="Start", command=self.toggle_monitoring)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # Unit toggle button
        self.unit_button = ttk.Button(button_frame, text="Switch to Mbps", command=self.toggle_unit)
        self.unit_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_button = ttk.Button(button_frame, text="Save Data", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_plot(self):
        # Create a frame for the plot
        self.plot_frame = ttk.LabelFrame(self.root, text="Network Traffic (30-second window)")
        self.plot_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create figure and subplot
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Add a second y-axis
        self.ax2 = self.ax.twinx()
        
        # Set up the plot
        self.download_line, = self.ax.plot([], [], 'b-', label='Download')
        self.upload_line, = self.ax2.plot([], [], 'r-', label='Upload')
        
        # Add labels and legend
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Download Speed', color='blue')
        self.ax2.set_ylabel('Upload Speed', color='red')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add legend
        lines = [self.download_line, self.upload_line]
        labels = [line.get_label() for line in lines]
        self.ax.legend(lines, labels, loc='upper left')
        
        # Initial grid
        self.ax.grid(True)
        
        # Initialize time window (30 seconds)
        now = time.time()
        self.ax.set_xlim(now - 30, now)
        
        # Set y-axis limits
        self.ax.set_ylim(0, 1)  # Will be auto-adjusted later
        self.ax2.set_ylim(0, 1)  # Will be auto-adjusted later
    
    def update_plot(self):
        if not self.running:
            # If not running, just update the canvas and reschedule
            self.canvas.draw_idle()
            self.root.after(self.update_interval, self.update_plot)
            return
            
        try:
            # Get current time
            current_time = time.time()
            
            # Set x-axis limits to show last 30 seconds
            self.ax.set_xlim(current_time - 30, current_time)
            
            # Update line data
            self.download_line.set_data(self.timestamps, self.download_speeds)
            self.upload_line.set_data(self.timestamps, self.upload_speeds)
            
            # Adjust y-axis limits if needed
            if self.download_speeds:
                max_download = max(self.download_speeds) * 1.1
                self.ax.set_ylim(0, max(max_download, 0.1))  # Ensure min scale
                
            if self.upload_speeds:
                max_upload = max(self.upload_speeds) * 1.1
                self.ax2.set_ylim(0, max(max_upload, 0.1))  # Ensure min scale
            
            # Update the canvas
            self.canvas.draw_idle()
        except Exception as e:
            self.status_bar.config(text=f"Error updating plot: {str(e)}")
        
        # Schedule next update
        self.root.after(self.update_interval, self.update_plot)
    
    def toggle_monitoring(self):
        if not self.running:
            # Start monitoring
            self.running = True
            self.start_stop_button.config(text="Stop")
            self.status_bar.config(text=f"Monitoring {self.interface}...")
            
            # Start monitoring in a separate thread
            self.monitoring_thread = threading.Thread(target=self.monitor_network, daemon=True)
            self.monitoring_thread.start()
        else:
            # Stop monitoring
            self.running = False
            self.start_stop_button.config(text="Start")
            self.status_bar.config(text="Monitoring stopped")
    
    def monitor_network(self):
        """Monitor network traffic in a separate thread"""
        while self.running:
            try:
                # Get current speeds
                download_speed, upload_speed = self.speed_calculator.get_speeds()
                
                # Update data lists
                current_time = time.time()
                self.timestamps.append(current_time)
                
                # Store speeds in the selected unit
                if self.show_mbps:
                    self.download_speeds.append(self.speed_calculator.mb_to_mbps(download_speed))
                    self.upload_speeds.append(self.speed_calculator.mb_to_mbps(upload_speed))
                else:
                    self.download_speeds.append(download_speed)
                    self.upload_speeds.append(upload_speed)
                
                # Only keep data for the last 30 seconds
                cutoff_time = current_time - 30
                while self.timestamps and self.timestamps[0] < cutoff_time:
                    self.timestamps.pop(0)
                    self.download_speeds.pop(0)
                    self.upload_speeds.pop(0)
                
                # Update the labels
                self.update_labels(download_speed, upload_speed)
                
                # Update data manager
                # Update data manager
                self.data_manager.add_data_point(
                    datetime.now(),  # datetime.datetime
                    upload_speed,    # float
                    download_speed   # float
                )
                # Sleep for 1 second
                time.sleep(1)
                
            except Exception as e:
                # Update status with the error
                self.root.after(0, lambda: self.status_bar.config(text=f"Error: {str(e)}"))
                time.sleep(1)
    
    def update_labels(self, download_speed, upload_speed):
        """Update the speed labels with current values"""
        # Calculate Mbps equivalents
        download_mbps = self.speed_calculator.mb_to_mbps(download_speed)
        upload_mbps = self.speed_calculator.mb_to_mbps(upload_speed)
        
        # Format strings based on current unit display setting
        if self.show_mbps:
            download_text = f"{download_mbps:.2f} Mbps ({download_speed:.2f} MB/s)"
            upload_text = f"{upload_mbps:.2f} Mbps ({upload_speed:.2f} MB/s)"
        else:
            download_text = f"{download_speed:.2f} MB/s ({download_mbps:.2f} Mbps)"
            upload_text = f"{upload_mbps:.2f} MB/s ({upload_mbps:.2f} Mbps)"
        
        # Update labels in the main thread
        self.root.after(0, lambda: self.download_label.config(text=download_text))
        self.root.after(0, lambda: self.upload_label.config(text=upload_text))
    
    def toggle_unit(self):
        """Toggle between MB/s and Mbps as the primary display unit"""
        self.show_mbps = not self.show_mbps
        
        # Clear and rebuild data with new units
        if self.show_mbps:
            self.unit_button.config(text="Switch to MB/s")
            self.ax.set_ylabel('Download Speed (Mbps)', color='blue')
            self.ax2.set_ylabel('Upload Speed (Mbps)', color='red')
        else:
            self.unit_button.config(text="Switch to Mbps")
            self.ax.set_ylabel('Download Speed (MB/s)', color='blue')
            self.ax2.set_ylabel('Upload Speed (MB/s)', color='red')
        
        # Refresh plot
        self.canvas.draw_idle()
    
    def clear_data(self):
        """Clear all collected data"""
        # Clear data lists
        self.timestamps = []
        self.download_speeds = []
        self.upload_speeds = []
        
        # Clear data manager
        # Clear data manager
        self.data_manager.clear_history()
        
        self.status_bar.config(text="Data cleared")
        
        # Update plot
        self.update_plot()
    
    def save_data(self):
        """Save current session data to CSV"""
        try:
            filename = self.data_manager.save_to_csv()
            self.status_bar.config(text=f"Data saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
    
    def on_closing(self):
        """Handle window closing event"""
        # Stop monitoring if running
        if self.running:
            self.running = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=1.0)
        
        # Save data before closing
        try:
            self.data_manager.save_to_csv()
        except Exception as e:
            print(f"Error saving data: {e}")
        
        # Destroy root window
        self.root.destroy()
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

# Entry point
if __name__ == "__main__":
    try:
        app = WiFiMonitorGUI()
        app.run()
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)

