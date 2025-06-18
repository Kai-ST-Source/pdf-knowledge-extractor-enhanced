"""
Unit tests for AI analyzer module.
"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.analyzer import AIAnalyzer


class TestAIAnalyzer(unittest.TestCase):
    """Test cases for AIAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "fake_api_key"
        
    @patch('core.analyzer.genai')
    def test_init_success(self, mock_genai):
        """Test successful analyzer initialization."""
        # Mock Gemini configuration
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        analyzer = AIAnalyzer(self.api_key)
        
        # Assertions
        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        self.assertEqual(analyzer.model, mock_model)
        
    @patch('core.analyzer.genai')
    def test_analyze_success(self, mock_genai):
        """Test successful document analysis."""
        # Mock Gemini model
        mock_response = MagicMock()
        mock_response.text = """
1. 概念・理論
- 概念1: 説明1
- 概念2: 説明2

2. 方法論・手順
- 手順1: 説明1

3. 事例・ケーススタディ
- 事例1: 説明1

4. データ・数値
- データ1: 説明1

5. 注意点・リスク
- リスク1: 説明1

6. ベストプラクティス
- プラクティス1: 説明1
"""
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        analyzer = AIAnalyzer(self.api_key)
        result = analyzer.analyze("Sample text", [])
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("概念・理論", result)
        self.assertIn("方法論・手順", result)
        self.assertEqual(len(result["概念・理論"]), 2)
        self.assertEqual(result["概念・理論"][0], "概念1: 説明1")
        
    @patch('core.analyzer.genai')
    @patch('core.analyzer.Image')
    def test_analyze_with_images(self, mock_image_class, mock_genai):
        """Test analysis with images."""
        # Mock image loading
        mock_image = MagicMock()
        mock_image_class.open.return_value = mock_image
        
        # Mock Gemini model
        mock_response = MagicMock()
        mock_response.text = "1. 概念・理論\n- 概念1: 説明1"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        analyzer = AIAnalyzer(self.api_key)
        image_path = Path("/fake/image.png")
        
        # Mock image path existence
        with patch.object(Path, 'exists', return_value=True):
            result = analyzer.analyze("Sample text", [image_path])
        
        # Assertions
        mock_image_class.open.assert_called_once_with(image_path)
        mock_model.generate_content.assert_called_once()
        
    @patch('core.analyzer.genai')
    def test_parse_response_all_categories(self, mock_genai):
        """Test response parsing with all categories."""
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        analyzer = AIAnalyzer(self.api_key)
        
        response_text = """
1. 概念・理論
- 概念A: 詳細A
- 概念B: 詳細B

2. 方法論・手順
- 手順1: 手順詳細

3. 事例・ケーススタディ
- 事例A: 事例詳細

4. データ・数値
- データ1: 数値詳細

5. 注意点・リスク
- リスク1: リスク詳細

6. ベストプラクティス
- 推奨1: 推奨詳細
"""
        
        result = analyzer._parse_response(response_text)
        
        # Assertions
        self.assertEqual(len(result), 6)
        for category in analyzer.categories:
            self.assertIn(category, result)
            self.assertGreater(len(result[category]), 0)
            
    @patch('core.analyzer.genai')
    def test_parse_response_empty_categories(self, mock_genai):
        """Test response parsing with missing categories."""
        mock_genai.GenerativeModel.return_value = MagicMock()
        
        analyzer = AIAnalyzer(self.api_key)
        
        # Response with only one category
        response_text = """
1. 概念・理論
- 概念A: 詳細A
"""
        
        result = analyzer._parse_response(response_text)
        
        # Assertions
        self.assertEqual(len(result), 6)
        self.assertGreater(len(result["概念・理論"]), 0)
        
        # Check that empty categories have default messages
        for category in ["方法論・手順", "事例・ケーススタディ", "データ・数値", "注意点・リスク", "ベストプラクティス"]:
            self.assertEqual(len(result[category]), 1)
            self.assertIn("この文書からは", result[category][0])
            self.assertIn("に関する明確な情報を特定できませんでした", result[category][0])
            
    @patch('core.analyzer.genai')
    def test_analyze_error_handling(self, mock_genai):
        """Test error handling in analyze method."""
        # Mock Gemini model to raise exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        analyzer = AIAnalyzer(self.api_key)
        
        with self.assertRaises(Exception) as context:
            analyzer.analyze("Sample text", [])
        
        self.assertIn("API Error", str(context.exception))


if __name__ == '__main__':
    unittest.main()