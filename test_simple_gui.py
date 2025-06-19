#!/usr/bin/env python3
"""Very simple GUI test to isolate the issue."""

import tkinter as tk
from tkinter import ttk

def main():
    print("Creating window...")
    root = tk.Tk()
    root.title("Simple Test")
    root.geometry("400x300")
    
    # Force update
    root.update()
    
    print("Creating frame...")
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    print("Creating label...")
    label = ttk.Label(frame, text="Test GUI", font=("Arial", 24))
    label.pack(pady=20)
    
    print("Creating button...")
    button = ttk.Button(frame, text="Click Me", command=lambda: print("Button clicked!"))
    button.pack()
    
    # Force another update
    root.update()
    
    print("Starting mainloop...")
    root.mainloop()

if __name__ == "__main__":
    main()