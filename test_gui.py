#!/usr/bin/env python3
"""Test GUI to debug the white screen issue."""

import sys
import tkinter as tk
from tkinter import ttk
sys.path.insert(0, '/Users/hideki/pdf_knowledge_extractor_mac/src')

try:
    print("Starting test GUI...")
    
    # Create simple test window
    root = tk.Tk()
    root.title("Test GUI")
    root.geometry("400x300")
    
    # Add some widgets
    label = ttk.Label(root, text="Test Label", font=("Arial", 14))
    label.pack(pady=20)
    
    button = ttk.Button(root, text="Test Button", command=lambda: print("Button clicked!"))
    button.pack(pady=10)
    
    print("GUI created successfully")
    root.mainloop()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()