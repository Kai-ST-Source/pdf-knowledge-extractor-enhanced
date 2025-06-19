#!/usr/bin/env python3
"""
Cleanup script for icon generation temporary files
"""

import os
import shutil
import glob

def cleanup_temp_files():
    """Clean up temporary files and directories"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to keep
    keep_files = ['create_icon.py', 'cleanup.py', 'app_icon.icns']
    
    # Get all files in directory
    all_files = os.listdir(current_dir)
    
    files_removed = 0
    
    for file in all_files:
        file_path = os.path.join(current_dir, file)
        
        if file not in keep_files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed file: {file}")
                    files_removed += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Removed directory: {file}")
                    files_removed += 1
            except Exception as e:
                print(f"Error removing {file}: {e}")
    
    print(f"\nCleanup complete. Removed {files_removed} items.")
    print(f"Kept essential files: {', '.join(keep_files)}")

if __name__ == '__main__':
    cleanup_temp_files()