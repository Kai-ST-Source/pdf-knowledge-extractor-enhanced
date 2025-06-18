"""
Logging configuration module.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(name: str = None, log_dir: Optional[Path] = None, 
                 log_level: str = "INFO", console_output: bool = True) -> logging.Logger:
    """Setup and configure logger.
    
    Args:
        name: Logger name (defaults to root logger)
        log_dir: Directory for log files
        log_level: Logging level
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Set level
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"pdf_extractor_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # Debug log handler for errors
    if log_dir:
        debug_log = log_dir / "debug.log"
        debug_handler = logging.FileHandler(debug_log, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        logger.addHandler(debug_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance by name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class ProgressLogger:
    """Logger for tracking progress of operations."""
    
    def __init__(self, logger: logging.Logger, total_items: int, 
                 description: str = "Processing"):
        """Initialize progress logger.
        
        Args:
            logger: Logger instance
            total_items: Total number of items to process
            description: Description of the operation
        """
        self.logger = logger
        self.total_items = total_items
        self.description = description
        self.current_item = 0
        self.start_time = datetime.now()
        
    def update(self, item_name: str = None):
        """Update progress.
        
        Args:
            item_name: Name of current item being processed
        """
        self.current_item += 1
        percentage = (self.current_item / self.total_items) * 100
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.current_item > 0:
            rate = elapsed / self.current_item
            eta = rate * (self.total_items - self.current_item)
            eta_str = f", ETA: {int(eta)}s"
        else:
            eta_str = ""
        
        msg = f"{self.description}: {self.current_item}/{self.total_items} ({percentage:.1f}%){eta_str}"
        if item_name:
            msg += f" - {item_name}"
            
        self.logger.info(msg)
        
    def complete(self):
        """Mark operation as complete."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(
            f"{self.description} completed: {self.total_items} items in {elapsed:.1f}s"
        )