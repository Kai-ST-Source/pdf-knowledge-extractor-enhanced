"""
Notification management module for macOS.
"""

import sys
import logging
import subprocess
from typing import Optional


class NotificationManager:
    """Manage system notifications."""
    
    def __init__(self):
        """Initialize notification manager."""
        self.logger = logging.getLogger(__name__)
        self.enabled = sys.platform == "darwin"  # Only enable on macOS
        
        # Try to import macOS notification libraries
        if self.enabled:
            try:
                from Foundation import NSUserNotification, NSUserNotificationCenter
                self.NSUserNotification = NSUserNotification
                self.NSUserNotificationCenter = NSUserNotificationCenter
                self.use_native = True
            except ImportError:
                self.logger.warning("Native macOS notification libraries not available")
                self.use_native = False
    
    def send(self, title: str, message: str, subtitle: Optional[str] = None):
        """Send a notification.
        
        Args:
            title: Notification title
            message: Notification message
            subtitle: Optional subtitle
        """
        if not self.enabled:
            self.logger.debug(f"Notifications disabled: {title} - {message}")
            return
            
        try:
            if self.use_native:
                self._send_native(title, message, subtitle)
            else:
                self._send_osascript(title, message, subtitle)
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    def _send_native(self, title: str, message: str, subtitle: Optional[str] = None):
        """Send notification using native macOS APIs."""
        notification = self.NSUserNotification.new()
        notification.setTitle_(title)
        notification.setInformativeText_(message)
        
        if subtitle:
            notification.setSubtitle_(subtitle)
            
        center = self.NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)
        
    def _send_osascript(self, title: str, message: str, subtitle: Optional[str] = None):
        """Send notification using osascript."""
        script = f'display notification "{message}" with title "{title}"'
        if subtitle:
            script += f' subtitle "{subtitle}"'
            
        subprocess.run(['osascript', '-e', script], capture_output=True)
    
    def send_progress(self, current: int, total: int, operation: str = "Processing"):
        """Send progress notification.
        
        Args:
            current: Current item number
            total: Total number of items
            operation: Operation description
        """
        percentage = (current / total) * 100 if total > 0 else 0
        self.send(
            "PDF Knowledge Extractor",
            f"{operation}: {current}/{total} ({percentage:.0f}%)",
            f"Processing {operation.lower()}"
        )
    
    def send_completion(self, success_count: int, total_count: int, 
                       operation: str = "Extraction"):
        """Send completion notification.
        
        Args:
            success_count: Number of successful items
            total_count: Total number of items
            operation: Operation description
        """
        if success_count == total_count:
            self.send(
                f"{operation} Complete",
                f"Successfully processed all {total_count} files",
                "All files processed successfully"
            )
        else:
            failed_count = total_count - success_count
            self.send(
                f"{operation} Complete with Errors",
                f"Processed {success_count}/{total_count} files ({failed_count} failed)",
                "Some files had errors"
            )
    
    def send_error(self, error_message: str, file_name: Optional[str] = None):
        """Send error notification.
        
        Args:
            error_message: Error message
            file_name: Optional file name that caused the error
        """
        title = "PDF Knowledge Extractor Error"
        if file_name:
            message = f"Error processing {file_name}: {error_message}"
        else:
            message = f"Error: {error_message}"
            
        self.send(title, message, "An error occurred")