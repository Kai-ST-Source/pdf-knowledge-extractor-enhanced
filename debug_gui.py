#!/usr/bin/env python3
"""Debug GUI issues"""

import tkinter as tk
from tkinter import ttk
import sys
import platform

def test_gui():
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"macOS version: {platform.mac_ver()}")
    
    root = tk.Tk()
    root.title("Debug Test")
    
    # Set background color to make sure window is visible
    root.configure(bg='lightblue')
    
    # Get window info
    print(f"Window geometry: {root.geometry()}")
    print(f"Window state: {root.state()}")
    
    # Create a simple label with background
    label = tk.Label(root, text="TEST LABEL", bg='red', fg='white', font=("Arial", 24))
    label.pack(pady=50, padx=50)
    
    # Force update and print widget info
    root.update_idletasks()
    print(f"Label winfo: {label.winfo_geometry()}")
    print(f"Label visible: {label.winfo_viewable()}")
    
    # Add button
    button = tk.Button(root, text="CLICK ME", bg='green', fg='white', 
                      command=lambda: print("Button clicked!"))
    button.pack(pady=20)
    
    # Force another update
    root.update()
    
    # Check if widgets are mapped
    print(f"Label mapped: {label.winfo_ismapped()}")
    print(f"Button mapped: {button.winfo_ismapped()}")
    
    # Lift window to front
    root.lift()
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    
    print("Starting mainloop...")
    root.mainloop()

if __name__ == "__main__":
    test_gui()