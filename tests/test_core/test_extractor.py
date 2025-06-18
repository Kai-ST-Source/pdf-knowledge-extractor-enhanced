"""
Unit tests for PDF extractor module.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.extractor import PDFExtractor


class TestPDFExtractor(unittest.TestCase):
    """Test cases for PDFExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.extractor = PDFExtractor(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.extractor.cleanup()
        
    @patch('core.extractor.fitz')
    def test_extract_text_success(self, mock_fitz):
        """Test successful text extraction."""
        # Mock PyMuPDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF text"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc
        
        # Test
        pdf_path = Path("/fake/path/test.pdf")
        result = self.extractor.extract_text(pdf_path)
        
        # Assertions
        self.assertEqual(result, "Sample PDF text")
        mock_fitz.open.assert_called_once_with(pdf_path)
        mock_doc.close.assert_called_once()
        
    @patch('core.extractor.fitz')
    def test_extract_text_error(self, mock_fitz):
        """Test text extraction error handling."""
        # Mock exception
        mock_fitz.open.side_effect = Exception("PDF error")
        
        # Test
        pdf_path = Path("/fake/path/test.pdf")
        
        with self.assertRaises(Exception) as context:
            self.extractor.extract_text(pdf_path)
        
        self.assertIn("PDF error", str(context.exception))
        
    @patch('core.extractor.fitz')
    def test_extract_images_success(self, mock_fitz):
        """Test successful image extraction."""
        # Mock PyMuPDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_pix = MagicMock()
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc
        
        # Test
        pdf_path = Path("/fake/path/test.pdf")
        result = self.extractor.extract_images(pdf_path, max_images=2)
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(p, Path) for p in result))
        mock_fitz.open.assert_called_once_with(pdf_path)
        
    @patch('core.extractor.fitz')
    def test_extract_images_max_limit(self, mock_fitz):
        """Test image extraction respects max_images limit."""
        # Mock PyMuPDF with more pages than limit
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_pix = MagicMock()
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.__len__.return_value = 5
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc
        
        # Test
        pdf_path = Path("/fake/path/test.pdf")
        result = self.extractor.extract_images(pdf_path, max_images=3)
        
        # Assertions
        self.assertEqual(len(result), 3)
        
    @patch('core.extractor.fitz')
    def test_extract_combined(self, mock_fitz):
        """Test combined text and image extraction."""
        # Mock PyMuPDF for both text and image extraction
        mock_doc_text = MagicMock()
        mock_page_text = MagicMock()
        mock_page_text.get_text.return_value = "Sample text"
        mock_doc_text.__len__.return_value = 1
        mock_doc_text.__getitem__.return_value = mock_page_text
        
        mock_doc_images = MagicMock()
        mock_page_images = MagicMock()
        mock_pix = MagicMock()
        mock_page_images.get_pixmap.return_value = mock_pix
        mock_doc_images.__len__.return_value = 1
        mock_doc_images.__getitem__.return_value = mock_page_images
        
        # Return different mock docs for different calls
        mock_fitz.open.side_effect = [mock_doc_text, mock_doc_images]
        
        # Test
        pdf_path = Path("/fake/path/test.pdf")
        text, images = self.extractor.extract(pdf_path)
        
        # Assertions
        self.assertEqual(text, "Sample text")
        self.assertEqual(len(images), 1)
        
    def test_cleanup(self):
        """Test cleanup functionality."""
        # Create a test file in temp directory
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test")
        
        # Verify file exists
        self.assertTrue(test_file.exists())
        
        # Test cleanup
        self.extractor.cleanup()
        
        # Verify directory is removed
        self.assertFalse(self.temp_dir.exists())


if __name__ == '__main__':
    unittest.main()