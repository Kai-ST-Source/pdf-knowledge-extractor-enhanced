"""
Main GUI window for PDF Knowledge Extractor.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from pathlib import Path
from typing import List, Optional

from gui.file_handler import FileHandler
from gui.progress_dialog import ProgressDialog
from utils.notifications import NotificationManager


class PDFExtractorGUI:
    """Main GUI window for PDF Knowledge Extractor."""
    
    def __init__(self, process_callback, output_dir: Path, 
                 formats: List[str], logger: Optional[logging.Logger] = None):
        """Initialize GUI.
        
        Args:
            process_callback: Callback function to process files
            output_dir: Output directory for results
            formats: List of output formats
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.process_callback = process_callback
        self.output_dir = output_dir
        self.formats = formats
        self.file_handler = FileHandler(self.logger)
        self.notifications = NotificationManager()
        
        # Check if running as frozen app on macOS
        self.is_frozen = getattr(sys, 'frozen', False)
        self.is_macos = sys.platform == "darwin"
        
        # Don't create GUI if frozen macOS app (use file dialog directly)
        if self.is_frozen and self.is_macos:
            self.logger.info("Running as frozen macOS app - using direct file dialog")
            self._run_direct_mode()
        else:
            self._create_gui()
    
    def _run_direct_mode(self):
        """Run in direct mode without GUI window."""
        # Select files immediately
        files = self.file_handler.select_files_dialog()
        
        if files:
            # Validate files
            valid_files = self.file_handler.validate_pdf_files(files)
            
            if valid_files:
                # Process files directly
                self.logger.info(f"Processing {len(valid_files)} files in direct mode")
                
                try:
                    # Call the process callback
                    results = self.process_callback(valid_files)
                    
                    # Send completion notification
                    self.notifications.send_completion(
                        len(results), 
                        len(valid_files),
                        "PDF Knowledge Extraction"
                    )
                except Exception as e:
                    self.logger.error(f"Error processing files: {e}")
                    self.notifications.send_error(str(e))
            else:
                self.logger.warning("No valid PDF files selected")
        else:
            self.logger.info("No files selected")
    
    def _create_gui(self):
        """Create the GUI window."""
        self.logger.info("Creating GUI window")
        
        try:
            self.root = tk.Tk()
            self.root.title("PDF Knowledge Extractor")
            self.root.geometry("500x400")
            
            # Configure window
            self.root.configure(bg="#f0f0f0")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Center window
            self._center_window()
            
            # Setup UI components
            self._setup_ui()
            
            # Make window visible
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.focus_force()
            
            # Remove topmost after brief delay
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            self.logger.info("GUI created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating GUI: {e}")
            raise
    
    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        
        window_width = 500
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _setup_ui(self):
        """Setup UI components."""
        # Title
        title_label = tk.Label(
            self.root, 
            text="PDF Knowledge Extractor",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=20)
        
        # File selection frame
        self.select_frame = tk.Frame(
            self.root,
            bg="#ffffff",
            relief=tk.RAISED,
            borderwidth=2,
            width=400,
            height=200
        )
        self.select_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        self.select_frame.pack_propagate(False)
        
        # File selection label
        self.select_label = tk.Label(
            self.select_frame,
            text="📄\n\nクリックしてPDFファイルを選択\n\n複数ファイル選択可能",
            font=("Arial", 14),
            bg="#ffffff",
            fg="#666666",
            justify=tk.CENTER,
            cursor="hand2"
        )
        self.select_label.pack(expand=True)
        
        # Select button
        self.select_button = tk.Button(
            self.root,
            text="📁 PDFファイルを選択",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.select_files
        )
        self.select_button.pack(pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="待機中...")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.status_label.pack(pady=5)
        
        # Output location label
        output_label = tk.Label(
            self.root,
            text=f"出力先: {self.output_dir}",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666666"
        )
        output_label.pack(pady=5)
        
        # Bind events
        self.select_frame.bind("<Button-1>", lambda e: self.select_files())
        self.select_label.bind("<Button-1>", lambda e: self.select_files())
        
        # Hover effects
        self.select_frame.bind("<Enter>", lambda e: self.select_frame.configure(bg="#f8f8f8"))
        self.select_frame.bind("<Leave>", lambda e: self.select_frame.configure(bg="#ffffff"))
    
    def select_files(self):
        """Handle file selection."""
        files = self.file_handler.select_files_dialog(self.root)
        
        if files:
            # Validate files
            valid_files = self.file_handler.validate_pdf_files(files)
            
            if valid_files:
                self.process_files(valid_files)
            else:
                messagebox.showwarning(
                    "Invalid Files",
                    "No valid PDF files were selected."
                )
    
    def process_files(self, files: List[Path]):
        """Process selected files.
        
        Args:
            files: List of file paths to process
        """
        # Create progress dialog
        progress = ProgressDialog(self.root, "Processing PDFs", len(files))
        
        def worker():
            try:
                results = []
                
                for i, file_path in enumerate(files):
                    if progress.is_cancelled():
                        break
                        
                    # Update progress
                    self.root.after(0, lambda i=i, f=file_path: progress.update(
                        i + 1, 
                        f"Processing {i+1}/{len(files)}",
                        f.name
                    ))
                    
                    # Process file
                    try:
                        result = self.process_callback([file_path])
                        results.extend(result)
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
                        self.root.after(0, lambda e=e: messagebox.showerror(
                            "Processing Error",
                            f"Error: {str(e)}"
                        ))
                
                # Complete
                if not progress.is_cancelled():
                    self.root.after(0, lambda: progress.complete("Processing complete!"))
                    self.root.after(0, lambda: self.notifications.send_completion(
                        len(results),
                        len(files),
                        "PDF Knowledge Extraction"
                    ))
                    
                    # Update status
                    self.root.after(0, lambda: self.status_var.set(
                        f"完了: {len(results)} ファイルを処理しました"
                    ))
                
            except Exception as e:
                self.logger.error(f"Error in processing thread: {e}")
                self.root.after(0, lambda: progress.error(str(e)))
                self.root.after(0, lambda: self.notifications.send_error(str(e)))
            finally:
                # Close progress dialog after delay
                self.root.after(2000, progress.close)
        
        # Start processing in background thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle window closing."""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI."""
        if hasattr(self, 'root'):
            self.root.mainloop()