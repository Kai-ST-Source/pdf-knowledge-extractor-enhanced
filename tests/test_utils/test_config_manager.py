"""
Unit tests for configuration manager.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "config.json"
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_load_default_config(self):
        """Test loading default configuration when file doesn't exist."""
        # Use non-existent config file
        config_manager = ConfigManager(Path("/non/existent/config.json"))
        
        # Should load defaults
        self.assertEqual(
            config_manager.get("model_name"), 
            ConfigManager.DEFAULT_CONFIG["model_name"]
        )
        self.assertEqual(
            config_manager.get("temperature"),
            ConfigManager.DEFAULT_CONFIG["temperature"]
        )
        
    def test_load_valid_config(self):
        """Test loading valid configuration file."""
        # Create test config
        test_config = {
            "gemini_api_key": "test_key",
            "model_name": "test_model",
            "temperature": 0.5
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
            
        # Load config
        config_manager = ConfigManager(self.config_file)
        
        # Check values
        self.assertEqual(config_manager.get("gemini_api_key"), "test_key")
        self.assertEqual(config_manager.get("model_name"), "test_model")
        self.assertEqual(config_manager.get("temperature"), 0.5)
        
        # Check that defaults are merged
        self.assertEqual(
            config_manager.get("max_tokens"),
            ConfigManager.DEFAULT_CONFIG["max_tokens"]
        )
        
    def test_load_invalid_json(self):
        """Test handling of invalid JSON configuration."""
        # Create invalid JSON file
        with open(self.config_file, 'w') as f:
            f.write("{ invalid json }")
            
        # Should fall back to defaults
        config_manager = ConfigManager(self.config_file)
        
        self.assertEqual(
            config_manager.get("model_name"),
            ConfigManager.DEFAULT_CONFIG["model_name"]
        )
        
    def test_get_set_operations(self):
        """Test get and set operations."""
        config_manager = ConfigManager(self.config_file)
        
        # Test get with default
        self.assertEqual(config_manager.get("non_existent", "default"), "default")
        
        # Test set
        config_manager.set("test_key", "test_value")
        self.assertEqual(config_manager.get("test_key"), "test_value")
        
    def test_save_config(self):
        """Test saving configuration to file."""
        config_manager = ConfigManager(self.config_file)
        
        # Modify config
        config_manager.set("test_key", "test_value")
        
        # Save
        config_manager.save()
        
        # Verify file was created and contains correct data
        self.assertTrue(self.config_file.exists())
        
        with open(self.config_file, 'r') as f:
            saved_config = json.load(f)
            
        self.assertEqual(saved_config["test_key"], "test_value")
        
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        # Create valid config
        test_config = {
            "gemini_api_key": "valid_key",
            "output_dir": str(self.temp_dir)
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
            
        config_manager = ConfigManager(self.config_file)
        
        # Should be valid
        self.assertTrue(config_manager.validate())
        
    def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        # Create config without API key
        test_config = {
            "output_dir": str(self.temp_dir)
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
            
        config_manager = ConfigManager(self.config_file)
        
        # Should be invalid
        self.assertFalse(config_manager.validate())
        
    def test_validate_invalid_output_dir(self):
        """Test validation with invalid output directory."""
        # Create config with invalid output directory
        test_config = {
            "gemini_api_key": "valid_key",
            "output_dir": "/non/existent/parent/directory"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
            
        config_manager = ConfigManager(self.config_file)
        
        # Should be invalid
        self.assertFalse(config_manager.validate())
        
    @patch('sys.frozen', True, create=True)
    @patch('sys._MEIPASS', "/fake/meipass", create=True)
    def test_determine_config_path_frozen(self):
        """Test config path determination for frozen application."""
        config_manager = ConfigManager()
        
        # Should use _MEIPASS when frozen
        expected_path = Path("/fake/meipass") / "config.json"
        self.assertEqual(config_manager.config_path, expected_path)
        
    def test_path_expansion(self):
        """Test path expansion in configuration."""
        # Create config with path that needs expansion
        test_config = {
            "gemini_api_key": "test_key",
            "output_dir": "~/test_output"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
            
        config_manager = ConfigManager(self.config_file)
        
        # Should expand the path
        output_dir = config_manager.get("output_dir")
        self.assertFalse(output_dir.startswith("~"))
        self.assertTrue(Path(output_dir).is_absolute())


if __name__ == '__main__':
    unittest.main()