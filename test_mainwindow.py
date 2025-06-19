#!/usr/bin/env python3
"""Test MainWindow directly."""

import sys
import tkinter as tk
sys.path.insert(0, '/Users/hideki/pdf_knowledge_extractor_mac/src')

from gui import MainWindow

# Create mock app object
class MockApp:
    def __init__(self):
        self.config = {
            "output_dir": "/Users/hideki/Desktop/PDF knowledge extractor",
            "extraction_mode": "raw_text_only",
            "extraction_settings": {
                "default_mode": "raw_text_only"
            }
        }
    
    def process_pdf(self, pdf_path, output_formats=None):
        print(f"Mock process_pdf called with: {pdf_path}, formats: {output_formats}")
        return {"status": "success", "message": "Mock processing completed"}

try:
    print("Creating test MainWindow...")
    
    root = tk.Tk()
    app = MockApp()
    
    # Create MainWindow
    window = MainWindow(root, app)
    
    print("MainWindow created successfully")
    print("Starting mainloop...")
    
    root.mainloop()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()