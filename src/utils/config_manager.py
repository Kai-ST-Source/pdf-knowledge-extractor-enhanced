"""
Configuration management module.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import os
import sys


class ConfigManager:
    """Manage application configuration."""
    
    DEFAULT_CONFIG = {
        "gemini_api_key": "",
        "model_name": "gemini-1.5-flash",
        "temperature": 0.3,
        "max_tokens": 8192,
        "output_dir": "~/Desktop/PDF knowledge extractor",
        "supported_formats": ["excel", "markdown"],
        "log_level": "DEBUG",
        "max_images_per_pdf": 10,
        "image_dpi": 200,
        "concurrent_processing": True,
        "max_workers": 4
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = self._determine_config_path(config_path)
        self.config = self._load_config()
        
    def _determine_config_path(self, config_path: Optional[Path]) -> Path:
        """Determine the configuration file path."""
        if config_path:
            return Path(config_path)
            
        # Check if running as frozen app
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                base_path = Path(sys._MEIPASS)
            else:
                # Other freezers
                base_path = Path(sys.executable).parent
        else:
            # Running as script
            base_path = Path(__file__).parent.parent
            
        return base_path / "config.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            self.logger.warning(f"Config file not found at {self.config_path}, using defaults")
            return self.DEFAULT_CONFIG.copy()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Merge with defaults
            config = self.DEFAULT_CONFIG.copy()
            config.update(user_config)
            
            # Expand paths
            if 'output_dir' in config:
                config['output_dir'] = str(Path(config['output_dir']).expanduser())
                
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self.DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            
    def validate(self) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        # Check required fields
        if not self.config.get('gemini_api_key'):
            self.logger.error("Gemini API key is required")
            return False
            
        # Check output directory
        output_dir = Path(self.config.get('output_dir', ''))
        if not output_dir.parent.exists():
            self.logger.error(f"Output directory parent does not exist: {output_dir.parent}")
            return False
            
        return True