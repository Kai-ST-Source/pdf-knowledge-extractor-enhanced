"""
PDF text and image extraction module.
"""

import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
import fitz  # PyMuPDF
import tempfile
import re
from datetime import datetime


class PDFExtractor:
    """Extract text and images from PDF documents."""
    
    def __init__(self, temp_dir: Path = None):
        """Initialize PDF extractor.
        
        Args:
            temp_dir: Temporary directory for storing extracted images
        """
        self.temp_dir = temp_dir or Path(tempfile.mkdtemp(prefix="pdf_extractor_"))
        self.logger = logging.getLogger(__name__)
        
    def extract(self, pdf_path: Path) -> Tuple[str, List[Path]]:
        """Extract text and images from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, list_of_image_paths)
        """
        text = self.extract_text(pdf_path)
        images = self.extract_images(pdf_path)
        return text, images
    
    def extract_detailed_text(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract detailed text information from PDF with structure preservation.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing detailed text information
        """
        try:
            doc = fitz.open(pdf_path)
            detailed_info = {
                'pages': [],
                'tables': [],
                'headers': [],
                'footnotes': [],
                'raw_text': '',
                'structured_text': [],
                'all_text_blocks': [],
                'page_texts': [],
                'formatted_text': '',
                'metadata': {
                    'total_pages': len(doc),
                    'extraction_timestamp': datetime.now().isoformat(),
                    'file_name': pdf_path.name,
                    'file_size': pdf_path.stat().st_size
                }
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_info = self._extract_page_details(page, page_num)
                detailed_info['pages'].append(page_info)
                detailed_info['raw_text'] += page_info['text'] + '\n'
                detailed_info['page_texts'].append({
                    'page_number': page_num + 1,
                    'text': page_info['text'],
                    'blocks_count': len(page_info['blocks'])
                })
                
                # Extract structured information
                detailed_info['headers'].extend(page_info['headers'])
                detailed_info['tables'].extend(page_info['tables'])
                detailed_info['footnotes'].extend(page_info['footnotes'])
                detailed_info['structured_text'].extend(page_info['structured_text'])
                detailed_info['all_text_blocks'].extend(page_info['blocks'])
            
            # Create formatted text with structure
            detailed_info['formatted_text'] = self._create_formatted_text(detailed_info)
            
            doc.close()
            self.logger.info(f"Extracted detailed text from {pdf_path}: {len(detailed_info['pages'])} pages, {len(detailed_info['all_text_blocks'])} text blocks")
            return detailed_info
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed text from {pdf_path}: {e}")
            raise
    
    def _create_formatted_text(self, detailed_info: Dict[str, Any]) -> str:
        """Create formatted text with structure information."""
        formatted_parts = []
        
        # Add document metadata
        formatted_parts.append(f"=== PDF Document: {detailed_info['metadata']['file_name']} ===")
        formatted_parts.append(f"Total Pages: {detailed_info['metadata']['total_pages']}")
        formatted_parts.append(f"Extraction Time: {detailed_info['metadata']['extraction_timestamp']}")
        formatted_parts.append("")
        
        # Add headers section
        if detailed_info['headers']:
            formatted_parts.append("=== HEADERS AND TITLES ===")
            for header in detailed_info['headers']:
                formatted_parts.append(f"Page {header['page_number']}: {header['text']}")
            formatted_parts.append("")
        
        # Add page-by-page content
        for page_info in detailed_info['pages']:
            formatted_parts.append(f"=== PAGE {page_info['page_number']} ===")
            
            # Add headers from this page
            page_headers = [h for h in detailed_info['headers'] if h['page_number'] == page_info['page_number']]
            if page_headers:
                formatted_parts.append("Headers:")
                for header in page_headers:
                    formatted_parts.append(f"  - {header['text']}")
                formatted_parts.append("")
            
            # Add structured text blocks
            if page_info['structured_text']:
                formatted_parts.append("Content:")
                for block in page_info['structured_text']:
                    formatted_parts.append(f"  {block['text']}")
                formatted_parts.append("")
            
            # Add tables from this page
            page_tables = [t for t in detailed_info['tables'] if t['page_number'] == page_info['page_number']]
            if page_tables:
                formatted_parts.append("Tables:")
                for table in page_tables:
                    if table.get('data'):
                        for row in table['data']:
                            formatted_parts.append(f"  | {' | '.join(str(cell) for cell in row)} |")
                formatted_parts.append("")
            
            # Add footnotes from this page
            page_footnotes = [f for f in detailed_info['footnotes'] if f['page_number'] == page_info['page_number']]
            if page_footnotes:
                formatted_parts.append("Footnotes:")
                for footnote in page_footnotes:
                    formatted_parts.append(f"  - {footnote['text']}")
                formatted_parts.append("")
            
            formatted_parts.append("")
        
        # Add summary statistics
        formatted_parts.append("=== EXTRACTION SUMMARY ===")
        formatted_parts.append(f"Total Headers Found: {len(detailed_info['headers'])}")
        formatted_parts.append(f"Total Tables Found: {len(detailed_info['tables'])}")
        formatted_parts.append(f"Total Footnotes Found: {len(detailed_info['footnotes'])}")
        formatted_parts.append(f"Total Text Blocks: {len(detailed_info['all_text_blocks'])}")
        formatted_parts.append(f"Total Characters: {len(detailed_info['raw_text'])}")
        
        return "\n".join(formatted_parts)
    
    def extract_raw_text_only(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract raw text without AI analysis - just pure text extraction.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing raw text data
        """
        try:
            doc = fitz.open(pdf_path)
            raw_data = {
                'file_name': pdf_path.name,
                'file_path': str(pdf_path),
                'total_pages': len(doc),
                'pages': [],
                'full_text': '',
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get raw text
                raw_text = page.get_text()
                
                # Get text with formatting
                formatted_text = page.get_text("dict")
                
                page_data = {
                    'page_number': page_num + 1,
                    'raw_text': raw_text,
                    'text_length': len(raw_text),
                    'blocks': []
                }
                
                # Extract text blocks with formatting
                for block in formatted_text.get("blocks", []):
                    if "lines" in block:
                        block_text = ""
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                block_text += span.get("text", "")
                        if block_text.strip():
                            page_data['blocks'].append({
                                'text': block_text.strip(),
                                'bbox': block.get("bbox", []),
                                'font_info': self._extract_font_info(block)
                            })
                
                raw_data['pages'].append(page_data)
                raw_data['full_text'] += raw_text + '\n'
            
            doc.close()
            self.logger.info(f"Extracted raw text from {pdf_path}: {len(raw_data['pages'])} pages, {len(raw_data['full_text'])} characters")
            return raw_data
            
        except Exception as e:
            self.logger.error(f"Error extracting raw text from {pdf_path}: {e}")
            raise
    
    def _extract_font_info(self, block: Dict) -> Dict[str, Any]:
        """Extract font information from a text block."""
        font_info = {
            'fonts': set(),
            'sizes': set(),
            'is_bold': False,
            'is_italic': False
        }
        
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                font_info['fonts'].add(span.get("font", ""))
                font_info['sizes'].add(span.get("size", 0))
                flags = span.get("flags", 0)
                if flags & 2**4:  # Bold flag
                    font_info['is_bold'] = True
                if flags & 2**1:  # Italic flag
                    font_info['is_italic'] = True
        
        # Convert sets to lists for JSON serialization
        font_info['fonts'] = list(font_info['fonts'])
        font_info['sizes'] = list(font_info['sizes'])
        
        return font_info
    
    def _extract_page_details(self, page, page_num: int) -> Dict[str, Any]:
        """Extract detailed information from a single page."""
        page_info = {
            'page_number': page_num + 1,
            'text': '',
            'headers': [],
            'tables': [],
            'footnotes': [],
            'structured_text': [],
            'blocks': []
        }
        
        # Get text blocks with position information
        blocks = page.get_text("dict")
        
        for block in blocks.get("blocks", []):
            if "lines" in block:  # Text block
                block_info = self._process_text_block(block, page_num)
                page_info['blocks'].append(block_info)
                page_info['text'] += block_info['text'] + '\n'
                
                # Categorize content
                if block_info['is_header']:
                    page_info['headers'].append(block_info)
                elif block_info['is_footnote']:
                    page_info['footnotes'].append(block_info)
                else:
                    page_info['structured_text'].append(block_info)
        
        # Extract tables
        tables = page.find_tables()
        for table in tables:
            table_info = self._extract_table_info(table, page_num)
            page_info['tables'].append(table_info)
        
        return page_info
    
    def _process_text_block(self, block: Dict, page_num: int) -> Dict[str, Any]:
        """Process a text block and extract detailed information."""
        block_text = ""
        lines_info = []
        
        for line in block.get("lines", []):
            line_text = ""
            spans_info = []
            
            for span in line.get("spans", []):
                span_text = span.get("text", "")
                line_text += span_text
                
                span_info = {
                    'text': span_text,
                    'font': span.get("font", ""),
                    'size': span.get("size", 0),
                    'flags': span.get("flags", 0),  # Bold, italic, etc.
                    'bbox': span.get("bbox", []),
                    'color': span.get("color", 0)
                }
                spans_info.append(span_info)
            
            block_text += line_text + '\n'
            
            line_info = {
                'text': line_text,
                'bbox': line.get("bbox", []),
                'spans': spans_info
            }
            lines_info.append(line_info)
        
        # Determine content type based on font size and position
        is_header = self._is_header(block, lines_info)
        is_footnote = self._is_footnote(block, lines_info)
        
        return {
            'text': block_text.strip(),
            'bbox': block.get("bbox", []),
            'lines': lines_info,
            'is_header': is_header,
            'is_footnote': is_footnote,
            'page_number': page_num + 1
        }
    
    def _is_header(self, block: Dict, lines_info: List[Dict]) -> bool:
        """Determine if a block is a header based on font size and formatting."""
        if not lines_info:
            return False
        
        # Check for large font size
        max_size = max(span['size'] for line in lines_info for span in line['spans'])
        if max_size > 14:  # Assuming headers are larger than 14pt
            return True
        
        # Check for bold formatting
        for line in lines_info:
            for span in line['spans']:
                if span['flags'] & 2**4:  # Bold flag
                    return True
        
        # Check for common header patterns
        text = ''.join(line['text'] for line in lines_info).strip()
        header_patterns = [
            r'^第\d+章',
            r'^\d+\.\s+',
            r'^[A-Z][A-Z\s]+$',
            r'^[一二三四五六七八九十]+、',
            r'^[①②③④⑤⑥⑦⑧⑨⑩]'
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _is_footnote(self, block: Dict, lines_info: List[Dict]) -> bool:
        """Determine if a block is a footnote based on position and formatting."""
        if not lines_info:
            return False
        
        # Check if text is at bottom of page
        bbox = block.get("bbox", [])
        if len(bbox) >= 4:
            y_position = bbox[1]  # Y coordinate
            # If text is in bottom 20% of page, likely a footnote
            if y_position > 700:  # Approximate bottom area
                return True
        
        # Check for footnote patterns
        text = ''.join(line['text'] for line in lines_info).strip()
        footnote_patterns = [
            r'^\d+\)',
            r'^\*+',
            r'^注\d+',
            r'^脚注\d+'
        ]
        
        for pattern in footnote_patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def _extract_table_info(self, table, page_num: int) -> Dict[str, Any]:
        """Extract information from a table."""
        try:
            table_data = table.extract()
            return {
                'page_number': page_num + 1,
                'data': table_data,
                'bbox': table.bbox,
                'rows': len(table_data),
                'columns': len(table_data[0]) if table_data else 0
            }
        except Exception as e:
            self.logger.warning(f"Error extracting table on page {page_num + 1}: {e}")
            return {
                'page_number': page_num + 1,
                'data': [],
                'bbox': [],
                'rows': 0,
                'columns': 0,
                'error': str(e)
            }
        
    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                
            doc.close()
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    def extract_text_with_formatting(self, pdf_path: Path) -> str:
        """Extract text with basic formatting preserved.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Formatted text as string
        """
        try:
            doc = fitz.open(pdf_path)
            formatted_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = ""
                
                # Get text blocks with formatting
                blocks = page.get_text("dict")
                
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block.get("lines", []):
                            line_text = ""
                            for span in line.get("spans", []):
                                text = span.get("text", "")
                                flags = span.get("flags", 0)
                                
                                # Apply formatting
                                if flags & 2**4:  # Bold
                                    text = f"**{text}**"
                                if flags & 2**1:  # Italic
                                    text = f"*{text}*"
                                
                                line_text += text
                            
                            page_text += line_text + "\n"
                        page_text += "\n"  # Add space between blocks
                
                formatted_text += f"=== Page {page_num + 1} ===\n{page_text}\n"
            
            doc.close()
            return formatted_text
            
        except Exception as e:
            self.logger.error(f"Error extracting formatted text from {pdf_path}: {e}")
            raise
    
    def extract_images(self, pdf_path: Path, dpi: int = 200, max_images: int = 10) -> List[Path]:
        """Convert PDF pages to images using PyMuPDF.
        
        Args:
            pdf_path: Path to PDF file
            dpi: DPI for image conversion
            max_images: Maximum number of images to extract
            
        Returns:
            List of paths to extracted images
        """
        try:
            # Use PyMuPDF instead of pdf2image to avoid poppler dependency
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(min(len(doc), max_images)):
                page = doc[page_num]
                
                # Render page to pixmap
                mat = fitz.Matrix(dpi/72, dpi/72)  # scaling factor for DPI
                pix = page.get_pixmap(matrix=mat)
                
                # Save as PNG
                image_path = self.temp_dir / f"{pdf_path.stem}_page_{page_num+1}.png"
                pix.save(str(image_path))
                image_paths.append(image_path)
                
            doc.close()
            self.logger.info(f"Extracted {len(image_paths)} images from {pdf_path}")
            return image_paths
            
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {e}")
            # Return empty list instead of raising to allow text-only processing
            return []
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Error cleaning up temporary files: {e}")