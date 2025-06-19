#!/usr/bin/env python3
"""
Simple GUI for PDF Knowledge Extractor
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import logging

class MainWindow:
    """Main GUI window for PDF Knowledge Extractor."""
    
    def __init__(self, root, app):
        """Initialize the main window."""
        self.root = root
        self.app = app
        
        logging.info("Initializing MainWindow")
        
        # Configure window
        self.root.title("PDF Knowledge Extractor")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Create UI
        logging.info("Creating widgets...")
        self.create_widgets()
        logging.info("Widgets created successfully")
        
        # Setup event handlers
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
    
    def create_widgets(self):
        """Create and arrange widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="PDF Knowledge Extractor",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="PDFファイル:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(main_frame, textvariable=self.file_var, width=50)
        self.file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        ttk.Button(main_frame, text="選択", command=self.select_file).grid(row=1, column=2, pady=5)
        
        # Extraction mode
        ttk.Label(main_frame, text="抽出モード:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.mode_var = tk.StringVar(value="raw_text_only")
        mode_combo = ttk.Combobox(main_frame, textvariable=self.mode_var, state="readonly", width=20)
        mode_combo['values'] = [
            "raw_text_only",
            "standard", 
            "detailed"
        ]
        mode_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 5), pady=5)
        
        # Output formats
        ttk.Label(main_frame, text="出力形式:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var, state="readonly", width=20)
        format_combo['values'] = ["json", "txt", "markdown", "yaml"]
        format_combo.grid(row=3, column=1, sticky=tk.W, padx=(5, 5), pady=5)
        
        # Extract button
        self.extract_button = ttk.Button(
            main_frame, 
            text="抽出開始", 
            command=self.start_extraction
        )
        self.extract_button.grid(row=4, column=1, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="PDFファイルを選択してください")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Log text area
        ttk.Label(main_frame, text="ログ:").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        # Create frame for log area
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget and scrollbar
        self.log_text = tk.Text(log_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame grid weights for log area
        main_frame.rowconfigure(8, weight=1)
        
        # Setup logging to GUI
        self.setup_gui_logging()
    
    def setup_gui_logging(self):
        """Setup logging to display in GUI."""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                # Avoid recursive logging
                if record.name == __name__:
                    return
                    
                msg = self.format(record)
                # Use after to avoid blocking
                self.text_widget.after(0, lambda: self._insert_text(msg))
            
            def _insert_text(self, msg):
                try:
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                except:
                    pass  # Ignore errors in GUI logging
        
        # Add GUI handler to root logger
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        gui_handler.setLevel(logging.INFO)  # Only show INFO and above
        logging.getLogger().addHandler(gui_handler)
    
    def select_file(self):
        """Open file dialog to select PDF file."""
        file_path = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_var.set(file_path)
            self.status_var.set(f"選択されたファイル: {Path(file_path).name}")
    
    def start_extraction(self):
        """Start the extraction process."""
        pdf_path = self.file_var.get().strip()
        
        if not pdf_path:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            messagebox.showerror("エラー", "選択されたファイルが見つかりません。")
            return
        
        # Disable button and show progress
        self.extract_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("処理中...")
        
        # Run extraction in separate thread
        thread = threading.Thread(target=self.run_extraction, args=(pdf_file,))
        thread.daemon = True
        thread.start()
    
    def run_extraction(self, pdf_file):
        """Run extraction in background thread."""
        try:
            # Update config with current settings
            if "extraction_settings" not in self.app.config:
                self.app.config["extraction_settings"] = {}
            self.app.config["extraction_settings"]["default_mode"] = self.mode_var.get()
            self.app.config["extraction_mode"] = self.mode_var.get()
            output_formats = [self.format_var.get()]
            
            # Process the PDF
            results = self.app.process_pdf(pdf_file, output_formats=output_formats)
            
            # Update UI on main thread
            self.root.after(0, self.extraction_completed, results)
            
        except Exception as e:
            # Show error on main thread
            self.root.after(0, self.extraction_failed, str(e))
    
    def extraction_completed(self, results):
        """Handle successful extraction completion."""
        self.progress.stop()
        self.extract_button.config(state='normal')
        self.status_var.set("抽出完了！")
        
        output_dir = Path(self.app.config.get("output", {}).get("output_directory", "~/Desktop/PDF knowledge extractor")).expanduser()
        messagebox.showinfo(
            "完了", 
            f"抽出が完了しました。\n結果は {output_dir} に保存されました。"
        )
    
    def extraction_failed(self, error_msg):
        """Handle extraction failure."""
        self.progress.stop()
        self.extract_button.config(state='normal')
        self.status_var.set("エラーが発生しました")
        
        messagebox.showerror("エラー", f"抽出中にエラーが発生しました:\n{error_msg}")
    
    def on_closing(self):
        """Handle window closing."""
        self.root.quit()
        self.root.destroy()