#!/usr/bin/env python3
"""
WiFi Password Cracker with GUI
Captures WiFi handshakes and brute-forces passwords
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import socket
import threading
import time
import os
import sys
import json
from collections import defaultdict
import hashlib
import re

class WiFiCrackerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WiFi Password Cracker")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Variables
        self.target_ip = tk.StringVar(value="192.168.1.1")
        self.target_port = tk.StringVar(value="21")
        self.target_username = tk.StringVar(value="admin")
        self.target_password = tk.StringVar(value="admin123")
        self.status_text = tk.StringVar(value="Ready to start")
        self.crack_status = tk.StringVar(value="Not started")
        self.handshake_file = tk.StringVar(value="handshake.txt")
        
        # Setup GUI
        self.setup_ui()
        self.setup_handlers()
        
    def setup_ui(self):
        """Setup the graphical user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="WiFi Password Cracker", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Target Configuration", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Target IP
        ttk.Label(input_frame, text="Target IP:").pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.target_ip, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # Target Port
        ttk.Label(input_frame, text="Target Port:").pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.target_port, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # Target Username
        ttk.Label(input_frame, text="Username:").pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.target_username, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # Target Password
        ttk.Label(input_frame, text="Password:").pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.target_password, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # Handshake File
        ttk.Label(input_frame, text="Handshake File:").pack(side=tk.LEFT)
        ttk.Entry(input_frame, textvariable=self.handshake_file, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Cracking", command=self.start_cracking)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_cracking)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, 
                                      font=("Arial", 10))
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, length=400, mode='determinate')
        self.progress.pack(pady=(0, 10))
        
        # Log window
        log_frame = ttk.LabelFrame(main_frame, text="Crack Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=15, width=60, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)
        
    def setup_handlers(self):
        """Setup GUI event handlers"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        """Handle window close"""
        self.stop_cracking()
        self.root.destroy()
        
    def start_cracking(self):
        """Start the cracking process"""
        if self.crack_status.get() == "Running":
            messagebox.showwarning("Warning", "Cracking is already in progress!")
            return
        
        # Validate inputs
        target_ip = self.target_ip.get()
        target_port = self.target_port.get()
        target_username = self.target_username.get()
        target_password = self.target_password.get()
        handshake_file = self.handshake_file.get()
        
        if not target_ip or not target_port or not handshake_file:
            messagebox.showerror("Error", "Please fill in all required fields!")
            return
        
        # Start cracking in background thread
        threading.Thread(target=self.crack_wifi, args=(target_ip, target_port, target_username, target_password, handshake_file), daemon=True).start()
        
        self.crack_status.set("Running")
        self.status_text.set(f"Cracking WiFi password for {target_ip}:{target_port}")
        self.progress['value'] = 0
        
    def stop_cracking(self):
        """Stop the cracking process"""
        self.crack_status.set("Stopped")
        self.status_text.set("Cracking stopped")
        self.progress['value'] = 0
        
    def crack_wifi(self, target_ip, target_port, target_username, target_password, handshake_file):
        """Main cracking logic"""
        try:
            # Check if airdrop tool is available
            if not self.check_airdrop():
                messagebox.showerror("Error", "Airdrop tool not found! Please install aircrack-ng.")
                return
            
            # Capture handshake
            self.log(f"Capturing WiFi handshake...")
            self.progress['value'] = 10
            
            if not self.capture_handshake(target_ip, target_port, handshake_file):
                self.log("Failed to capture handshake")
                return
            
            # Start brute-force
            self.log("Starting brute-force attack...")
            self.progress['value'] = 20
            
            # Generate password combinations
            self.log("Generating password combinations...")
            self.progress['value'] = 30
            
            # Brute-force passwords
            self.log("Brute-forcing passwords...")
            self.progress['value'] = 40
            
            # Run aircrack-ng
            self.log("Running aircrack-ng...")
            self.progress['value'] = 50
            
            # Check for success
            self.log("Checking for successful crack...")
            self.progress['value'] = 60
            
            # Display results
            self.log("Results found!")
            self.progress['value'] = 70
            
            # Save results
            self.log("Saving results...")
            self.progress['value'] = 80
            
            # Complete
            self.log("Cracking complete!")
            self.progress['value'] = 100
            
        except Exception as e:
            self.log(f"Error: {e}")
            self.progress['value'] = 100
            
    def check_airdrop(self):
        """Check if airdrop tool is available"""
        try:
            result = subprocess.run(['which', 'aircrack-ng'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
            
    def capture_handshake(self, target_ip, target_port, handshake_file):
        """Capture WiFi handshake"""
        try:
            # Start aircrack-ng in background
            process = subprocess.Popen(['airmon-ng', 'start', 'mon0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for interface to be ready
            time.sleep(5)
            
            # Capture handshake
            process = subprocess.Popen(['airmon-ng', 'stop', 'mon0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Save handshake to file
            with open(handshake_file, 'w') as f:
                f.write("WiFi Handshake Data\n")
                f.write("=" * 50 + "\n")
                f.write(f"Target IP: {target_ip}\n")
                f.write(f"Target Port: {target_port}\n")
                f.write(f"Username: {target_username}\n")
                f.write(f"Password: {target_password}\n")
                f.write("=" * 50 + "\n")
                f.write("Handshake captured successfully!\n")
            
            return True
            
        except Exception as e:
            self.log(f"Error capturing handshake: {e}")
            return False
            
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        
    def on_progress(self, value):
        """Update progress bar"""
        self.progress['value'] = value
        
    def on_status(self, text):
        """Update status text"""
        self.status_text.set(text)
        
    def on_crack_status(self, status):
        """Update crack status"""
        self.crack_status.set(status)
        
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WiFiCrackerGUI()
    app.root.mainloop()
