"""
Progress dialog for displaying processing status.
"""

import tkinter as tk
from tkinter import ttk
import threading
import logging
from typing import Optional, Callable


class ProgressDialog:
    """Progress dialog for long-running operations."""
    
    def __init__(self, parent: Optional[tk.Tk] = None, title: str = "Processing",
                 total_items: int = 0):
        """Initialize progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            total_items: Total number of items to process
        """
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.total_items = total_items
        self.current_item = 0
        self.cancelled = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(parent)
        if parent:
            self.dialog.grab_set()
            
        self._setup_ui()
        self._center_window()
        
    def _setup_ui(self):
        """Setup the dialog UI."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame, 
            text="Preparing...",
            font=('System', 12)
        )
        self.status_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=350
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Detail label
        self.detail_label = ttk.Label(
            main_frame,
            text="",
            font=('System', 10)
        )
        self.detail_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            main_frame,
            text="Cancel",
            command=self._on_cancel
        )
        self.cancel_button.grid(row=3, column=0, columnspan=2)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
    def _center_window(self):
        """Center the dialog on screen or parent."""
        self.dialog.update_idletasks()
        
        if self.parent:
            # Center on parent
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()
            
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
        else:
            # Center on screen
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
            
        self.dialog.geometry(f"+{x}+{y}")
        
    def update(self, current: int, status: str = "", detail: str = ""):
        """Update progress.
        
        Args:
            current: Current item number
            status: Status message
            detail: Detail message
        """
        self.current_item = current
        
        if self.total_items > 0:
            progress = (current / self.total_items) * 100
            self.progress_var.set(progress)
            
            if not status:
                status = f"Processing {current}/{self.total_items}..."
        else:
            # Indeterminate progress
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start(10)
            
        if status:
            self.status_label.configure(text=status)
        if detail:
            self.detail_label.configure(text=detail)
            
        self.dialog.update()
        
    def set_indeterminate(self, status: str = "Processing..."):
        """Set progress to indeterminate mode.
        
        Args:
            status: Status message
        """
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start(10)
        self.status_label.configure(text=status)
        self.dialog.update()
        
    def complete(self, message: str = "Complete!"):
        """Mark operation as complete.
        
        Args:
            message: Completion message
        """
        self.progress_var.set(100)
        self.status_label.configure(text=message)
        self.detail_label.configure(text="")
        self.cancel_button.configure(text="Close")
        self.dialog.update()
        
    def error(self, message: str):
        """Show error state.
        
        Args:
            message: Error message
        """
        self.status_label.configure(text="Error occurred")
        self.detail_label.configure(text=message)
        self.cancel_button.configure(text="Close")
        self.dialog.update()
        
    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.close()
        
    def close(self):
        """Close the dialog."""
        try:
            if self.progress_bar.cget('mode') == 'indeterminate':
                self.progress_bar.stop()
            self.dialog.destroy()
        except:
            pass
            
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled.
        
        Returns:
            True if cancelled
        """
        return self.cancelled