"""
File handling module for GUI operations.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Optional
import tkinter as tk
from tkinter import filedialog


class FileHandler:
    """Handle file selection and drag-and-drop operations."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize file handler.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.is_frozen = getattr(sys, 'frozen', False)
        self.is_macos = sys.platform == "darwin"
        
    def select_files_dialog(self, parent: Optional[tk.Tk] = None) -> List[Path]:
        """Show file selection dialog.
        
        Args:
            parent: Parent window for dialog
            
        Returns:
            List of selected file paths
        """
        # Use native macOS dialog if frozen app
        if self.is_frozen and self.is_macos:
            return self._select_files_osascript()
        else:
            return self._select_files_tkinter(parent)
    
    def _select_files_tkinter(self, parent: Optional[tk.Tk] = None) -> List[Path]:
        """Select files using tkinter dialog.
        
        Args:
            parent: Parent window for dialog
            
        Returns:
            List of selected file paths
        """
        try:
            file_paths = filedialog.askopenfilenames(
                parent=parent,
                title="Select PDF Files",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                multiple=True
            )
            
            if file_paths:
                self.logger.info(f"Selected {len(file_paths)} files via tkinter dialog")
                return [Path(fp) for fp in file_paths]
            else:
                self.logger.info("File selection cancelled")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in tkinter file dialog: {e}")
            return []
    
    def _select_files_osascript(self) -> List[Path]:
        """Select files using macOS native dialog via osascript.
        
        Returns:
            List of selected file paths
        """
        try:
            # AppleScript for multiple file selection
            script = '''
            set theFiles to choose file with prompt "Select PDF files to process:" ¬
                of type {"pdf"} ¬
                with multiple selections allowed
            
            set filePaths to {}
            repeat with aFile in theFiles
                set end of filePaths to POSIX path of aFile
            end repeat
            
            set AppleScript's text item delimiters to "|"
            return filePaths as string
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Split the pipe-delimited paths
                file_paths = [Path(p.strip()) for p in result.stdout.strip().split('|')]
                self.logger.info(f"Selected {len(file_paths)} files via osascript")
                return file_paths
            else:
                self.logger.info("File selection cancelled or no files selected")
                return []
                
        except subprocess.TimeoutExpired:
            self.logger.error("File dialog timed out")
            return []
        except Exception as e:
            self.logger.error(f"Error in osascript file dialog: {e}")
            # Fallback to tkinter if osascript fails
            return self._select_files_tkinter()
    
    def validate_pdf_files(self, file_paths: List[Path]) -> List[Path]:
        """Validate that files are PDFs and exist.
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            List of valid PDF file paths
        """
        valid_files = []
        
        for file_path in file_paths:
            if not file_path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                continue
                
            if not file_path.is_file():
                self.logger.warning(f"Not a file: {file_path}")
                continue
                
            if file_path.suffix.lower() != '.pdf':
                self.logger.warning(f"Not a PDF file: {file_path}")
                continue
                
            valid_files.append(file_path)
            
        self.logger.info(f"Validated {len(valid_files)}/{len(file_paths)} files")
        return valid_files
    
    def setup_drag_drop(self, widget: tk.Widget, callback):
        """Setup drag and drop for a widget.
        
        Args:
            widget: tkinter widget to enable drag-drop on
            callback: Function to call with dropped files
        """
        # macOS drag-drop setup would go here
        # This is complex and requires platform-specific code
        # For now, we'll use the file dialog approach
        self.logger.info("Drag-drop setup requested (not implemented in frozen app)")
        
    def get_output_filename(self, input_file: Path, output_dir: Path, 
                          suffix: str = "") -> Path:
        """Generate output filename based on input file.
        
        Args:
            input_file: Input file path
            output_dir: Output directory
            suffix: Optional suffix to add to filename
            
        Returns:
            Output file path
        """
        base_name = input_file.stem
        if suffix:
            base_name = f"{base_name}_{suffix}"
            
        output_path = output_dir / base_name
        return output_path