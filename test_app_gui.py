#!/usr/bin/env python3
"""Test the app.py GUI directly"""

import sys
sys.path.insert(0, '/Users/hideki/pdf_knowledge_extractor_mac/src')

from app import PDFKnowledgeExtractorApp

try:
    print("Initializing PDFKnowledgeExtractorApp...")
    app = PDFKnowledgeExtractorApp()
    
    print("Running GUI...")
    app.run_gui()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()