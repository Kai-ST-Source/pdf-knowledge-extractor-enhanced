#!/usr/bin/env python3
"""Fixed GUI for PDF Knowledge Extractor"""

import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class FixedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Knowledge Extractor")
        self.root.geometry("600x500")
        
        # Force window to be visible
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # Set background color to ensure visibility
        self.root.configure(bg='white')
        
        # Create widgets with explicit backgrounds
        self.create_widgets()
        
        # Force update
        self.root.update()
        
    def create_widgets(self):
        # Use Frame instead of ttk.Frame for better control
        main_frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with explicit styling
        title_label = tk.Label(
            main_frame, 
            text="PDF Knowledge Extractor",
            font=("Arial", 18, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = tk.Frame(main_frame, bg='white')
        file_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(file_frame, text="PDFファイル:", bg='white').pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_var, width=40)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(file_frame, text="選択", command=self.select_file).pack(side=tk.LEFT)
        
        # Extraction mode frame
        mode_frame = tk.Frame(main_frame, bg='white')
        mode_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(mode_frame, text="抽出モード:", bg='white').pack(side=tk.LEFT, padx=(0, 10))
        
        self.mode_var = tk.StringVar(value="raw_text_only")
        modes = ["raw_text_only", "standard", "detailed"]
        mode_menu = tk.OptionMenu(mode_frame, self.mode_var, *modes)
        mode_menu.pack(side=tk.LEFT)
        
        # Output format frame
        format_frame = tk.Frame(main_frame, bg='white')
        format_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(format_frame, text="出力形式:", bg='white').pack(side=tk.LEFT, padx=(0, 10))
        
        self.format_var = tk.StringVar(value="json")
        formats = ["json", "txt", "markdown", "yaml"]
        format_menu = tk.OptionMenu(format_frame, self.format_var, *formats)
        format_menu.pack(side=tk.LEFT)
        
        # Extract button
        self.extract_button = tk.Button(
            main_frame, 
            text="抽出開始", 
            command=self.start_extraction,
            bg='#007AFF',
            fg='white',
            font=("Arial", 14, "bold"),
            padx=20,
            pady=10
        )
        self.extract_button.pack(pady=20)
        
        # Status label
        self.status_var = tk.StringVar(value="PDFファイルを選択してください")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, bg='white', fg='gray')
        self.status_label.pack(pady=10)
        
        # Log text area
        log_frame = tk.Frame(main_frame, bg='white')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(log_frame, text="ログ:", bg='white').pack(anchor=tk.W)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(text_frame, height=10, width=70, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_var.set(file_path)
            self.status_var.set(f"選択されたファイル: {Path(file_path).name}")
            self.log(f"ファイルを選択しました: {file_path}")
    
    def start_extraction(self):
        pdf_path = self.file_var.get().strip()
        
        if not pdf_path:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        self.log(f"抽出を開始します...")
        self.log(f"モード: {self.mode_var.get()}")
        self.log(f"出力形式: {self.format_var.get()}")
        
        # Import app module
        try:
            from app import PDFKnowledgeExtractorApp
            app = PDFKnowledgeExtractorApp()
            
            # Process PDF
            results = app.process_pdf(Path(pdf_path), [self.format_var.get()])
            
            self.status_var.set("抽出完了！")
            self.log("抽出が完了しました。")
            
            output_dir = Path(app.config.get("output_directory", "~/Desktop/PDF knowledge extractor")).expanduser()
            messagebox.showinfo(
                "完了", 
                f"抽出が完了しました。\n結果は {output_dir} に保存されました。"
            )
            
        except Exception as e:
            self.status_var.set("エラーが発生しました")
            self.log(f"エラー: {str(e)}")
            messagebox.showerror("エラー", f"抽出中にエラーが発生しました:\n{str(e)}")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = FixedGUI()
    gui.run()