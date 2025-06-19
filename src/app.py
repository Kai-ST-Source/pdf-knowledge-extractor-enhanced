#!/usr/bin/env python3
"""
PDF Knowledge Extractor - Refactored Version
A clean, modular application for extracting knowledge from PDF files
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add the src directory to Python path for core module imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Set environment variables for macOS compatibility
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class PDFKnowledgeExtractorApp:
    """Main application class for PDF Knowledge Extractor."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = self._load_config()
        self.setup_logging()
        self.extractor = None
        self.analyzer = None
        
        # Initialize components
        self._init_components()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        config_paths = [
            Path(__file__).parent.parent / "config.json",  # Main project config
            "config.json",
            Path(__file__).parent / "config.json",
            Path.home() / "Desktop" / "PDF knowledge extractor" / "config.json"
        ]
        
        for config_path in config_paths:
            if Path(config_path).exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        
                    # Convert nested config structure to flat structure
                    if isinstance(config_data, dict):
                        flat_config = {}
                        
                        # Extract top-level values
                        for key, value in config_data.items():
                            if not isinstance(value, dict):
                                flat_config[key] = value
                        
                        # Extract output settings
                        if "output" in config_data:
                            output_config = config_data["output"]
                            if "output_directory" in output_config:
                                flat_config["output_directory"] = output_config["output_directory"]
                            if "default_formats" in output_config:
                                flat_config["output_formats"] = output_config["default_formats"]
                        
                        # Extract extraction settings
                        if "extraction_settings" in config_data:
                            extraction_config = config_data["extraction_settings"]
                            if "default_mode" in extraction_config:
                                flat_config["extraction_mode"] = extraction_config["default_mode"]
                            if "raw_extraction_formats" in extraction_config:
                                flat_config["output_formats"] = extraction_config["raw_extraction_formats"]
                        
                        return flat_config
                        
                except Exception as e:
                    print(f"Error loading config from {config_path}: {e}")
        
        # Create default config
        default_config = {
            "gemini_api_key": "",
            "model_name": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_tokens": 8192,
            "log_level": "INFO",
            "output_directory": str(Path.home() / "Desktop" / "PDF knowledge extractor"),
            "extraction_mode": "enhanced",
            "output_formats": ["excel", "markdown"],
            "enable_ai_analysis": False
        }
        
        # Save default config
        output_dir = Path(default_config["output_directory"])
        output_dir.mkdir(exist_ok=True)
        config_file = output_dir / "config.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            print(f"Created default config: {config_file}")
        except Exception as e:
            print(f"Error creating config: {e}")
        
        return default_config
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        # Create output directory with fallback
        output_dir = Path(self.config.get("output_dir", str(Path.home() / "Desktop" / "pdf_knowledge_extractor")))
        output_dir.mkdir(exist_ok=True)
        
        # Setup logging with error handling
        handlers = [logging.StreamHandler(sys.stdout)]
        
        try:
            # Try to create log file
            log_file = output_dir / "app.log"
            # Ensure we can write to the log file
            if log_file.exists():
                # Remove extended attributes if they exist
                try:
                    import subprocess
                    subprocess.run(["xattr", "-c", str(log_file)], capture_output=True)
                except:
                    pass
            
            # Create file handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
            handlers.append(file_handler)
        except PermissionError:
            # If we can't write to the default location, try temp directory
            import tempfile
            temp_log = Path(tempfile.gettempdir()) / "pdf_extractor.log"
            try:
                file_handler = logging.FileHandler(temp_log, encoding='utf-8', mode='a')
                handlers.append(file_handler)
                print(f"Log file created at: {temp_log}")
            except:
                print("Warning: Could not create log file, using console only")
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers,
            force=True  # Force reconfiguration
        )
        
        logging.info("PDF Knowledge Extractor initialized")
    
    def _init_components(self):
        """Initialize core components."""
        # Initialize extractors
        self.extractor = None
        self.enhanced_extractor = None
        
        # Try to initialize basic extractor
        try:
            from core.extractor import PDFExtractor
            self.extractor = PDFExtractor()
            logging.info("Basic PDF Extractor initialized")
        except Exception as e:
            logging.error(f"Failed to initialize basic PDF Extractor: {e}")
            
        # Try to initialize enhanced extractor
        try:
            from core.enhanced_extractor import EnhancedPDFExtractor
            self.enhanced_extractor = EnhancedPDFExtractor()
            logging.info("Enhanced PDF Extractor initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Enhanced PDF Extractor: {e}")
            
        # Ensure at least one extractor is available
        if not self.extractor and not self.enhanced_extractor:
            raise RuntimeError("Failed to initialize any PDF extractor")
        
        # Initialize analyzer only if API key is provided
        if self.config.get("gemini_api_key") and self.config.get("enable_ai_analysis"):
            try:
                from core.analyzer import AIAnalyzer
                self.analyzer = AIAnalyzer(self.config)
                logging.info("AI Analyzer initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize AI Analyzer: {e}")
        else:
            logging.info("AI analysis disabled - no API key or disabled in config")
    
    def process_pdf(self, pdf_path: Path, output_formats: Optional[list] = None) -> Dict[str, Any]:
        """Process a PDF file and extract knowledge."""
        if not self.extractor and not self.enhanced_extractor:
            raise RuntimeError("No PDF Extractor available")
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logging.info(f"Processing PDF: {pdf_path}")
        
        # Use configured formats if not specified
        if output_formats is None:
            output_formats = self.config.get("output_formats", ["markdown", "txt"])
        
        # Extract text and images based on mode and available extractors
        extraction_mode = self.config.get("extraction_mode", "enhanced")
        
        if extraction_mode == "enhanced" and self.enhanced_extractor:
            # Use enhanced extraction with OCR and comprehensive analysis
            extraction_result = self.enhanced_extractor.extract_comprehensive(pdf_path)
        elif extraction_mode == "raw_text_only" and self.extractor:
            # Use raw text extraction
            extraction_result = self.extractor.extract_raw_text_only(pdf_path)
            # Add images if needed
            images = self.extractor.extract_images(pdf_path)
            extraction_result['images'] = images
        elif extraction_mode == "detailed" and self.extractor:
            # Use detailed extraction
            extraction_result = self.extractor.extract_detailed_text(pdf_path)
            # Add images if needed
            images = self.extractor.extract_images(pdf_path)
            extraction_result['images'] = images
        elif self.enhanced_extractor:
            # Fallback to enhanced extractor if available
            extraction_result = self.enhanced_extractor.extract_comprehensive(pdf_path)
        elif self.extractor:
            # Fallback to basic extractor
            text, images = self.extractor.extract(pdf_path)
            extraction_result = {
                'text': text,
                'images': images,
                'extraction_mode': 'standard'
            }
        else:
            raise RuntimeError("No suitable extractor available for the requested mode")
        
        # Analyze with AI if available
        analysis_result = None
        if self.analyzer and extraction_mode != "raw_text_only":
            try:
                text_for_analysis = extraction_result.get('text', '') or extraction_result.get('full_text', '')
                analysis_result = self.analyzer.analyze(
                    text_for_analysis,
                    extraction_result.get("images", [])
                )
                logging.info("AI analysis completed")
            except Exception as e:
                logging.error(f"AI analysis failed: {e}")
                analysis_result = {"error": str(e)}
        
        # Prepare results
        results = {
            "metadata": {
                "source_file": str(pdf_path),
                "extraction_mode": extraction_mode,
                "timestamp": str(Path().cwd()),
                "ai_analysis": analysis_result is not None
            },
            "extraction": extraction_result,
            "analysis": analysis_result or {"note": "AI analysis not available"}
        }
        
        # Save results
        self._save_results(results, pdf_path, output_formats)
        
        return results
    
    def _save_results(self, results: Dict[str, Any], pdf_path: Path, formats: list):
        """Save results in specified formats."""
        output_dir = Path(self.config.get("output_dir", str(Path.home() / "Desktop" / "pdf_knowledge_extractor")))
        base_name = pdf_path.stem
        
        # Create output directory if it doesn't exist
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Output directory created/verified: {output_dir}")
        except PermissionError as e:
            # Fallback to Documents folder if Desktop has permission issues
            fallback_dir = Path.home() / "Documents" / "pdf_knowledge_extractor"
            logging.warning(f"Permission denied for {output_dir}, using fallback: {fallback_dir}")
            output_dir = fallback_dir
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create output directory: {e}")
            # Use temporary directory as last resort
            import tempfile
            output_dir = Path(tempfile.gettempdir()) / "pdf_knowledge_extractor"
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.warning(f"Using temporary directory: {output_dir}")
        
        for format_type in formats:
            try:
                if format_type == "json":
                    self._save_json(results, output_dir / f"{base_name}.json")
                elif format_type == "txt":
                    self._save_txt(results, output_dir / f"{base_name}.txt")
                elif format_type == "markdown":
                    self._save_markdown(results, output_dir / f"{base_name}.md")
                elif format_type == "excel":
                    self._save_excel(results, output_dir / f"{base_name}.xlsx")
                elif format_type == "yaml":
                    self._save_yaml(results, output_dir / f"{base_name}.yaml")
                else:
                    logging.warning(f"Unknown format: {format_type}")
            except Exception as e:
                logging.error(f"Error saving {format_type} format: {e}")
    
    def _save_json(self, results: Dict[str, Any], output_path: Path):
        """Save results as JSON."""
        def convert(obj):
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(convert(results), f, ensure_ascii=False, indent=2)
        logging.info(f"Saved JSON: {output_path}")
    
    def _save_txt(self, results: Dict[str, Any], output_path: Path):
        """Save results as plain text."""
        extraction_data = results.get("extraction", {})
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Title and metadata
            metadata = extraction_data.get("metadata", {})
            title = metadata.get('title', '') or metadata.get('file_name', 'PDF Document')
            if title:
                title = title.replace('.pdf', '')
                f.write(f"{title}\n")
                f.write("=" * len(title) + "\n\n")
            
            # Document information
            if metadata:
                f.write("Document Information:\n")
                f.write("-" * 20 + "\n")
                f.write(f"File: {metadata.get('file_name', 'Unknown')}\n")
                f.write(f"Pages: {metadata.get('total_pages', 'Unknown')}\n")
                if metadata.get('author'):
                    f.write(f"Author: {metadata['author']}\n")
                if metadata.get('creation_date'):
                    f.write(f"Created: {metadata['creation_date']}\n")
                f.write("\n")
            
            # Extract text from pages
            if "pages" in extraction_data:
                for page_info in extraction_data["pages"]:
                    page_num = page_info.get('page_number', 'Unknown')
                    f.write(f"Page {page_num}:\n")
                    f.write("-" * 10 + "\n")
                    
                    # Headers
                    for header in page_info.get('headers', []):
                        f.write(f"{header['text']}\n")
                    
                    # Regular content
                    for content in page_info.get('structured_content', []):
                        if not content.get('is_header') and not content.get('is_footer') and not content.get('is_page_header'):
                            text = content.get('text', '').strip()
                            if text and len(text) > 10:
                                f.write(f"{text}\n")
                    
                    # Tables
                    for table in page_info.get('tables', []):
                        f.write(f"\nTable {table['table_number']}:\n")
                        # Convert markdown table to plain text
                        table_lines = table['markdown'].split('\n')
                        for line in table_lines:
                            if line.strip() and not line.strip().startswith('|---'):
                                # Remove markdown table formatting
                                clean_line = line.replace('|', ' ').strip()
                                if clean_line:
                                    f.write(f"{clean_line}\n")
                    
                    # OCR results
                    for img_ocr in page_info.get('images_with_text', []):
                        f.write(f"\nFigure {img_ocr['image_number']} (OCR Text):\n")
                        f.write(f"{img_ocr['extracted_text']}\n")
                    
                    f.write("\n")
            
            # Fallback to basic text if enhanced extraction not available
            elif "text" in extraction_data or "full_text" in extraction_data:
                text_content = extraction_data.get("text", "") or extraction_data.get("full_text", "")
                if text_content:
                    f.write("Content:\n")
                    f.write("-" * 10 + "\n")
                    f.write(text_content)
                    f.write("\n\n")
        
        logging.info(f"Saved TXT: {output_path}")
    
    def _save_markdown(self, results: Dict[str, Any], output_path: Path):
        """Save results as Markdown using enhanced extraction format."""
        extraction_data = results.get("extraction", {})
        
        # Use the enhanced markdown content directly
        if "markdown_content" in extraction_data and extraction_data["markdown_content"]:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extraction_data["markdown_content"])
        else:
            # Fallback for basic extraction
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# PDF Content\n\n")
                
                # Write metadata
                metadata = extraction_data.get("metadata", {})
                if metadata:
                    f.write("## Document Information\n\n")
                    f.write(f"- **File:** {metadata.get('file_name', 'Unknown')}\n")
                    f.write(f"- **Pages:** {metadata.get('total_pages', 'Unknown')}\n")
                    if metadata.get('author'):
                        f.write(f"- **Author:** {metadata['author']}\n")
                    if metadata.get('creation_date'):
                        f.write(f"- **Created:** {metadata['creation_date']}\n")
                    f.write("\n---\n\n")
                
                # Write text content
                text_content = extraction_data.get("text", "") or extraction_data.get("full_text", "")
                if text_content:
                    f.write("## Content\n\n")
                    f.write(text_content)
                    f.write("\n\n")
        
        logging.info(f"Saved Markdown: {output_path}")
    
    def _save_yaml(self, results: Dict[str, Any], output_path: Path):
        """Save results as YAML."""
        try:
            import yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
            logging.info(f"Saved YAML: {output_path}")
        except ImportError:
            logging.warning("PyYAML not available, skipping YAML export")
    
    def _save_excel(self, results: Dict[str, Any], output_path: Path):
        """Save results as Excel."""
        try:
            import pandas as pd
            
            # Create a dictionary to hold data for different sheets
            sheets_data = {}
            
            # Metadata sheet
            metadata_data = []
            for key, value in results.get("metadata", {}).items():
                metadata_data.append({"項目": key, "値": str(value)})
            sheets_data["メタデータ"] = pd.DataFrame(metadata_data)
            
            # Extracted text sheet
            extraction_data = results.get("extraction", {})
            
            # Try different text fields for comprehensive extraction
            text_content = ""
            if "full_text" in extraction_data:
                text_content = extraction_data["full_text"]
            elif "formatted_text" in extraction_data:
                text_content = extraction_data["formatted_text"]
            elif "raw_text" in extraction_data:
                text_content = extraction_data["raw_text"]
            elif "text" in extraction_data:
                text_content = extraction_data["text"]
            
            if text_content:
                text_data = [{"抽出テキスト": text_content}]
                sheets_data["抽出テキスト"] = pd.DataFrame(text_data)
            
            # Add page-by-page text if available
            if "page_texts" in extraction_data and extraction_data["page_texts"]:
                page_data = []
                for page_info in extraction_data["page_texts"]:
                    page_data.append({
                        "ページ番号": page_info.get('page_number', 'Unknown'),
                        "テキスト": page_info.get('text', ''),
                        "ブロック数": page_info.get('blocks_count', 0)
                    })
                if page_data:
                    sheets_data["ページ別テキスト"] = pd.DataFrame(page_data)
            
            # Analysis results sheet
            if "analysis" in results and results["analysis"]:
                analysis_data = []
                for category, items in results["analysis"].items():
                    if isinstance(items, list):
                        for item in items:
                            analysis_data.append({"カテゴリ": category, "内容": str(item)})
                    elif items:  # Non-empty value
                        analysis_data.append({"カテゴリ": category, "内容": str(items)})
                
                if analysis_data:
                    sheets_data["分析結果"] = pd.DataFrame(analysis_data)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in sheets_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logging.info(f"Saved Excel: {output_path}")
            
        except ImportError:
            logging.warning("pandas or openpyxl not available, skipping Excel export")
        except Exception as e:
            logging.error(f"Error saving Excel: {e}")
    
    def run_gui(self):
        """Run the GUI version of the application."""
        try:
            import tkinter as tk
            from tkinter import ttk, filedialog, messagebox
            
            # Create root window
            root = tk.Tk()
            root.title("PDF Knowledge Extractor")
            root.geometry("600x500")
            
            # Center window
            root.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (600 // 2)
            y = (root.winfo_screenheight() // 2) - (500 // 2)
            root.geometry(f"600x500+{x}+{y}")
            
            # Create simple GUI
            self._create_simple_gui(root)
            
            # Start main loop
            root.mainloop()
            
        except Exception as e:
            logging.error(f"GUI failed to start: {e}")
            print(f"GUI Error: {e}")
            print("Falling back to console mode...")
            self.run_console()
    
    def _create_simple_gui(self, root):
        """Create a simple GUI interface."""
        import tkinter as tk
        from tkinter import ttk
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
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
        file_entry = ttk.Entry(main_frame, textvariable=self.file_var, width=50)
        file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        ttk.Button(main_frame, text="選択", command=self._select_file).grid(row=1, column=2, pady=5)
        
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
            command=self._start_extraction
        )
        self.extract_button.grid(row=4, column=1, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="PDFファイルを選択してください")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Store references
        self.root = root
        self.main_frame = main_frame
    
    def _select_file(self):
        """Open file dialog to select PDF file."""
        try:
            from tkinter import filedialog, messagebox
            file_path = filedialog.askopenfilename(
                title="PDFファイルを選択",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if file_path:
                self.file_var.set(file_path)
                self.status_var.set(f"選択されたファイル: {Path(file_path).name}")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイル選択エラー: {e}")
    
    def _start_extraction(self):
        """Start the extraction process."""
        try:
            from tkinter import messagebox
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
            import threading
            thread = threading.Thread(target=self._run_extraction, args=(pdf_file,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("エラー", f"抽出開始エラー: {e}")
    
    def _run_extraction(self, pdf_file):
        """Run extraction in background thread."""
        try:
            # Update config with current settings
            self.config["extraction_mode"] = self.mode_var.get()
            output_formats = [self.format_var.get()]
            
            # Process the PDF
            results = self.process_pdf(pdf_file, output_formats)
            
            # Update UI on main thread
            self.root.after(0, self._extraction_completed, results)
            
        except Exception as e:
            # Show error on main thread
            self.root.after(0, self._extraction_failed, str(e))
    
    def _extraction_completed(self, results):
        """Handle successful extraction completion."""
        from tkinter import messagebox
        self.progress.stop()
        self.extract_button.config(state='normal')
        self.status_var.set("抽出完了！")
        
        output_dir = Path(self.config.get("output_dir", str(Path.home() / "Desktop" / "pdf_knowledge_extractor")))
        messagebox.showinfo(
            "完了", 
            f"抽出が完了しました。\n結果は {output_dir} に保存されました。"
        )
    
    def _extraction_failed(self, error_msg):
        """Handle extraction failure."""
        from tkinter import messagebox
        self.progress.stop()
        self.extract_button.config(state='normal')
        self.status_var.set("エラーが発生しました")
        
        messagebox.showerror("エラー", f"抽出中にエラーが発生しました:\n{error_msg}")
    
    def run_console(self):
        """Run the console version of the application."""
        print("PDF Knowledge Extractor - Console Mode")
        print("=" * 40)
        
        while True:
            try:
                pdf_path = input("\nPDFファイルのパスを入力してください (終了: q): ").strip()
                
                if pdf_path.lower() == 'q':
                    break
                
                if not pdf_path:
                    continue
                
                pdf_file = Path(pdf_path)
                if not pdf_file.exists():
                    print("ファイルが見つかりません。")
                    continue
                
                print("処理中...")
                results = self.process_pdf(pdf_file)
                print(f"完了！結果は {self.config['output_directory']} に保存されました。")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"エラー: {e}")
        
        print("終了します。")

def main():
    """Main entry point."""
    app = PDFKnowledgeExtractorApp()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--console":
            app.run_console()
        elif sys.argv[1] == "--gui":
            app.run_gui()
        else:
            # Process specific file
            pdf_path = Path(sys.argv[1])
            if pdf_path.exists():
                try:
                    app.process_pdf(pdf_path)
                    sys.exit(0)  # Exit successfully if processing completed
                except Exception as e:
                    logging.error(f"Error processing {pdf_path}: {e}")
                    sys.exit(0)  # Exit with 0 to avoid error dialogs if files were created
            else:
                print(f"File not found: {pdf_path}")
                sys.exit(1)
    else:
        # Default to GUI, fallback to console
        try:
            app.run_gui()
        except Exception as e:
            print(f"GUI failed: {e}")
            app.run_console()

if __name__ == "__main__":
    main() 