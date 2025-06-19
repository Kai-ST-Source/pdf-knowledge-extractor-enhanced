#!/usr/bin/env python3
"""
Debug script to check PDF extraction in detail
"""

import fitz
from pathlib import Path

def debug_pdf_extraction(pdf_path):
    """Debug PDF extraction to identify issues"""
    
    print(f"Debugging PDF: {pdf_path}")
    print("=" * 50)
    
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")
    print(f"PDF metadata: {doc.metadata}")
    print()
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"=== PAGE {page_num + 1} ===")
        
        # Basic text extraction
        text = page.get_text()
        print(f"Raw text length: {len(text)} characters")
        
        # Text blocks analysis
        text_dict = page.get_text("dict")
        print(f"Number of blocks: {len(text_dict['blocks'])}")
        
        # Block analysis
        text_blocks = 0
        image_blocks = 0
        total_chars = 0
        
        for block in text_dict['blocks']:
            if 'lines' in block:  # Text block
                text_blocks += 1
                for line in block['lines']:
                    for span in line['spans']:
                        total_chars += len(span['text'])
            else:  # Image block
                image_blocks += 1
        
        print(f"Text blocks: {text_blocks}")
        print(f"Image blocks: {image_blocks}")
        print(f"Total characters in spans: {total_chars}")
        
        # Show first few text blocks
        text_block_count = 0
        for block in text_dict['blocks']:
            if 'lines' in block and text_block_count < 3:
                text_content = ""
                for line in block['lines']:
                    for span in line['spans']:
                        text_content += span['text']
                if text_content.strip():
                    print(f"Block {text_block_count + 1}: {text_content.strip()[:100]}...")
                    text_block_count += 1
        
        # Table detection
        try:
            tables = page.find_tables()
            print(f"Tables found: {len(tables)}")
        except:
            print("Table detection failed")
        
        # Image extraction
        images = page.get_images()
        print(f"Images found: {len(images)}")
        
        print()
    
    doc.close()

if __name__ == "__main__":
    # Check for the 44-page PDF file
    import sys
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        # Try to find recently modified PDF files
        import glob
        import os
        
        pdf_candidates = []
        search_paths = [
            "/Users/hideki/Desktop/*.pdf",
            "/Users/hideki/Downloads/*.pdf",
            "/Users/hideki/Documents/*.pdf"
        ]
        
        for pattern in search_paths:
            for file in glob.glob(pattern):
                stat = os.stat(file)
                pdf_candidates.append((file, stat.st_mtime))
        
        # Sort by modification time (newest first)
        pdf_candidates.sort(key=lambda x: x[1], reverse=True)
        
        print("Recent PDF files found:")
        for i, (file, mtime) in enumerate(pdf_candidates[:5]):
            print(f"{i+1}. {file}")
            # Quick check of page count
            try:
                doc = fitz.open(file)
                print(f"   Pages: {len(doc)}")
                doc.close()
            except:
                print("   Could not open")
        
        if pdf_candidates:
            pdf_file = pdf_candidates[0][0]
            print(f"\nAnalyzing most recent PDF: {pdf_file}")
        else:
            print("No PDF files found")
            exit(1)
    
    if Path(pdf_file).exists():
        debug_pdf_extraction(pdf_file)
    else:
        print(f"PDF file not found: {pdf_file}")