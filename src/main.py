#!/usr/bin/env python3
"""
PDF Knowledge Extractor - Main Entry Point

A modular tool for extracting structured knowledge from PDF documents using AI.
"""

import os
import sys
import argparse
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core import PDFExtractor, AIAnalyzer, DataExporter
from gui import PDFExtractorGUI
from utils import ConfigManager, setup_logger, NotificationManager


class PDFKnowledgeExtractorApp:
    """Main application class for PDF Knowledge Extractor."""
    
    def __init__(self, config_path: str = None):
        """Initialize the application.
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_path)
        
        # Setup logging
        output_dir = Path(self.config_manager.get('output_dir')).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = setup_logger(
            "pdf_extractor",
            log_dir=output_dir,
            log_level=self.config_manager.get('log_level', 'INFO')
        )
        
        # Log startup information
        self._log_startup_info()
        
        # Validate configuration
        if not self.config_manager.validate():
            self.logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Initialize components
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pdf_extractor_"))
        self.pdf_extractor = PDFExtractor(self.temp_dir)
        
        self.ai_analyzer = AIAnalyzer(
            api_key=self.config_manager.get('gemini_api_key'),
            model_name=self.config_manager.get('model_name'),
            temperature=self.config_manager.get('temperature'),
            max_tokens=self.config_manager.get('max_tokens'),
            config_manager=self.config_manager
        )
        
        self.data_exporter = DataExporter()
        self.notifications = NotificationManager()
        
        self.logger.info("Application initialized successfully")
    
    def _log_startup_info(self):
        """Log startup information for debugging."""
        self.logger.info("=== PDF Knowledge Extractor Started ===")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {sys.platform}")
        self.logger.info(f"Working directory: {os.getcwd()}")
        self.logger.info(f"Is frozen: {getattr(sys, 'frozen', False)}")
        self.logger.info(f"Command line args: {sys.argv}")
    
    def process_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Process PDF files and extract knowledge.
        
        Args:
            file_paths: List of PDF file paths to process
            
        Returns:
            List of extraction results
        """
        results = []
        output_dir = Path(self.config_manager.get('output_dir')).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        formats = self.config_manager.get('supported_formats', ['excel', 'markdown'])
        
        for i, file_path in enumerate(file_paths):
            try:
                self.logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
                
                # Send progress notification
                self.notifications.send_progress(i + 1, len(file_paths), "PDF Analysis")
                
                # Extract text and images
                text, images = self.pdf_extractor.extract(file_path)
                
                # Analyze with AI
                analysis_result = self.ai_analyzer.analyze(text, images)
                
                # Prepare metadata
                metadata = {
                    'source_file': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'processed_date': datetime.now().isoformat(),
                    'text_length': len(text),
                    'image_count': len(images)
                }
                
                # Export results
                output_path = output_dir / file_path.stem
                self.data_exporter.export(
                    analysis_result,
                    output_path,
                    formats,
                    metadata
                )
                
                result = {
                    'file_path': str(file_path),
                    'status': 'success',
                    'output_files': [
                        str(output_path.with_suffix(f'.{fmt}'))
                        for fmt in formats
                    ],
                    'metadata': metadata
                }
                
                results.append(result)
                self.logger.info(f"Successfully processed: {file_path}")
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                
                result = {
                    'file_path': str(file_path),
                    'status': 'error',
                    'error': str(e)
                }
                results.append(result)
                
                # Send error notification
                self.notifications.send_error(str(e), file_path.name)
        
        # Send completion notification
        success_count = sum(1 for r in results if r['status'] == 'success')
        self.notifications.send_completion(success_count, len(file_paths))
        
        return results
    
    def run_gui(self):
        """Run the application with GUI."""
        self.logger.info("Starting GUI mode")
        
        output_dir = Path(self.config_manager.get('output_dir')).expanduser()
        formats = self.config_manager.get('supported_formats', ['excel', 'markdown'])
        
        gui = PDFExtractorGUI(
            process_callback=self.process_files,
            output_dir=output_dir,
            formats=formats,
            logger=self.logger
        )
        
        if hasattr(gui, 'run'):
            gui.run()
    
    def run_cli(self, input_files: List[str]):
        """Run the application in CLI mode.
        
        Args:
            input_files: List of input file paths
        """
        self.logger.info(f"Starting CLI mode with {len(input_files)} files")
        
        # Convert to Path objects and validate
        file_paths = []
        for file_str in input_files:
            file_path = Path(file_str)
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                continue
            if not file_path.suffix.lower() == '.pdf':
                self.logger.warning(f"Not a PDF file: {file_path}")
                continue
            file_paths.append(file_path)
        
        if not file_paths:
            self.logger.error("No valid PDF files found")
            return
        
        # Process files
        results = self.process_files(file_paths)
        
        # Print summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        self.logger.info(f"Processing complete: {success_count}/{len(results)} files successful")
    
    def cleanup(self):
        """Clean up temporary resources."""
        try:
            self.pdf_extractor.cleanup()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PDF Knowledge Extractor - Extract structured knowledge from PDFs using AI"
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='PDF files to process (if none provided, GUI mode is used)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['excel', 'markdown'],
        help='Output formats'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    try:
        # Initialize application
        app = PDFKnowledgeExtractorApp(args.config)
        
        # Override config with command line arguments
        if args.output_dir:
            app.config_manager.set('output_dir', args.output_dir)
        if args.formats:
            app.config_manager.set('supported_formats', args.formats)
        if args.log_level:
            app.config_manager.set('log_level', args.log_level)
        
        # Run in appropriate mode
        if args.files:
            # CLI mode
            app.run_cli(args.files)
        else:
            # GUI mode
            app.run_gui()
            
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
    except Exception as e:
        logging.error(f"Application error: {e}")
        raise
    finally:
        # Cleanup
        if 'app' in locals():
            app.cleanup()


if __name__ == "__main__":
    main()