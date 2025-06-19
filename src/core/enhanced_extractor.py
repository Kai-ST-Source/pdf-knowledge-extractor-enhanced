"""
Enhanced PDF extraction module with OCR, structured text, and comprehensive analysis.
"""

import logging
import re
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

import fitz  # PyMuPDF
from PIL import Image

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("pytesseract not available. OCR features will be disabled.")


class EnhancedPDFExtractor:
    """Enhanced PDF extractor with OCR and structured text analysis."""
    
    def __init__(self, temp_dir: Path = None, tesseract_lang: str = 'jpn+eng'):
        """Initialize enhanced PDF extractor.
        
        Args:
            temp_dir: Temporary directory for storing extracted images
            tesseract_lang: Tesseract language setting (default: Japanese + English)
        """
        self.temp_dir = temp_dir or Path(tempfile.mkdtemp(prefix="pdf_extractor_"))
        self.tesseract_lang = tesseract_lang
        self.logger = logging.getLogger(__name__)
        
        # Font size thresholds for header detection
        self.header_font_sizes = {
            'h1': 16,  # Level 1 headers
            'h2': 14,  # Level 2 headers  
            'h3': 12,  # Level 3 headers
        }
        
    def extract_comprehensive(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract comprehensive information from PDF including OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing all extracted information
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Initialize result structure
            result = {
                'metadata': self._extract_pdf_metadata(doc, pdf_path),
                'pages': [],
                'headers': [],
                'tables': [],
                'images_with_text': [],
                'footnotes': [],
                'page_headers': [],
                'page_footers': [],
                'structured_content': [],
                'markdown_content': '',
                'extraction_summary': {
                    'total_pages': len(doc),
                    'total_text_blocks': 0,
                    'total_images': 0,
                    'total_tables': 0,
                    'ocr_processed_images': 0,
                    'extraction_time': datetime.now().isoformat()
                }
            }
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_info = self._extract_page_comprehensive(page, page_num)
                result['pages'].append(page_info)
                
                # Aggregate data
                result['headers'].extend(page_info['headers'])
                result['tables'].extend(page_info['tables'])
                result['images_with_text'].extend(page_info['images_with_text'])
                result['footnotes'].extend(page_info['footnotes'])
                result['page_headers'].extend(page_info['page_headers'])
                result['page_footers'].extend(page_info['page_footers'])
                result['structured_content'].extend(page_info['structured_content'])
                
                # Update summary
                result['extraction_summary']['total_text_blocks'] += len(page_info['text_blocks'])
                result['extraction_summary']['total_images'] += len(page_info['images'])
                result['extraction_summary']['total_tables'] += len(page_info['tables'])
                result['extraction_summary']['ocr_processed_images'] += len(page_info['images_with_text'])
            
            # Generate structured markdown
            result['markdown_content'] = self._generate_markdown(result)
            
            doc.close()
            self.logger.info(f"Enhanced extraction completed for {pdf_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in enhanced extraction from {pdf_path}: {e}")
            raise
    
    def _extract_pdf_metadata(self, doc: fitz.Document, pdf_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = doc.metadata
        file_stats = pdf_path.stat()
        
        return {
            'file_name': pdf_path.name,
            'file_size': file_stats.st_size,
            'file_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'keywords': metadata.get('keywords', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'total_pages': len(doc),
            'extraction_timestamp': datetime.now().isoformat()
        }
    
    def _extract_page_comprehensive(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """Extract comprehensive information from a single page."""
        page_info = {
            'page_number': page_num + 1,
            'text_blocks': [],
            'headers': [],
            'tables': [],
            'images': [],
            'images_with_text': [],
            'footnotes': [],
            'page_headers': [],
            'page_footers': [],
            'structured_content': [],
            'raw_text': ''
        }
        
        # Get page dimensions
        page_rect = page.rect
        page_height = page_rect.height
        page_width = page_rect.width
        
        # Extract text blocks with detailed information
        blocks = page.get_text("dict")
        
        for block in blocks['blocks']:
            if 'lines' in block:  # Text block
                block_info = self._process_text_block(block, page_num, page_height, page_width)
                if block_info['text'].strip():  # Only add non-empty blocks
                    page_info['text_blocks'].append(block_info)
                    page_info['raw_text'] += block_info['text'] + '\n'
                    
                    # Classify content
                    if block_info['is_header']:
                        page_info['headers'].append(block_info)
                    elif block_info['is_footer']:
                        page_info['page_footers'].append(block_info)
                    elif block_info['is_page_header']:
                        page_info['page_headers'].append(block_info)
                    elif block_info['is_footnote']:
                        page_info['footnotes'].append(block_info)
                    
                    page_info['structured_content'].append(block_info)
        
        # Also try alternative text extraction methods to ensure we get all text
        try:
            # Get all text as a fallback to ensure we don't miss anything
            fallback_text = page.get_text()
            if len(fallback_text.strip()) > len(page_info['raw_text'].strip()):
                # If fallback method got more text, add the difference
                self.logger.debug(f"Fallback text extraction added more content on page {page_num + 1}")
                # Add as a general text block
                fallback_block = {
                    'text': fallback_text,
                    'page_number': page_num + 1,
                    'bbox': [0, 0, page_width, page_height],
                    'font_size': 12,  # Default
                    'is_bold': False,
                    'is_italic': False,
                    'is_header': False,
                    'header_level': 0,
                    'is_footer': False,
                    'is_page_header': False,
                    'is_footnote': False,
                    'y_position': 0
                }
                page_info['text_blocks'].append(fallback_block)
                page_info['structured_content'].append(fallback_block)
        except Exception as e:
            self.logger.warning(f"Fallback text extraction failed for page {page_num + 1}: {e}")
        
        # Extract tables
        page_info['tables'] = self._extract_tables(page, page_num)
        
        # Extract and process images
        page_info['images'] = self._extract_page_images(page, page_num)
        
        # OCR processing for images
        if OCR_AVAILABLE:
            page_info['images_with_text'] = self._process_images_with_ocr(page_info['images'], page_num)
        
        return page_info
    
    def _process_text_block(self, block: Dict, page_num: int, page_height: float, page_width: float) -> Dict[str, Any]:
        """Process a text block and extract detailed information."""
        text_content = ""
        font_sizes = []
        font_flags = []
        
        for line in block['lines']:
            line_text = ""
            for span in line['spans']:
                span_text = span['text']
                line_text += span_text
                font_sizes.append(span['size'])
                font_flags.append(span['flags'])
            # Add line break between lines to preserve text structure
            if line_text.strip():  # Only add non-empty lines
                text_content += line_text
                if not text_content.endswith('\n'):
                    text_content += '\n'
        
        # Analyze text properties
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
        is_bold = any(flag & 2**4 for flag in font_flags)  # Bold flag
        is_italic = any(flag & 2**1 for flag in font_flags)  # Italic flag
        
        # Position analysis
        bbox = block['bbox']
        y_position = bbox[1]  # Top y coordinate
        
        # Classification
        is_header = avg_font_size >= self.header_font_sizes['h3'] and (is_bold or avg_font_size >= self.header_font_sizes['h1'])
        is_footer = y_position > page_height * 0.9  # Bottom 10% of page
        is_page_header = y_position < page_height * 0.1  # Top 10% of page
        is_footnote = y_position > page_height * 0.8 and avg_font_size < 10
        
        # Determine header level
        header_level = 0
        if is_header:
            if avg_font_size >= self.header_font_sizes['h1']:
                header_level = 1
            elif avg_font_size >= self.header_font_sizes['h2']:
                header_level = 2
            else:
                header_level = 3
        
        return {
            'text': text_content.strip(),
            'page_number': page_num + 1,
            'bbox': bbox,
            'font_size': avg_font_size,
            'is_bold': is_bold,
            'is_italic': is_italic,
            'is_header': is_header,
            'header_level': header_level,
            'is_footer': is_footer,
            'is_page_header': is_page_header,
            'is_footnote': is_footnote,
            'y_position': y_position
        }
    
    def _extract_tables(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract table data from page."""
        tables = []
        
        try:
            # Try to find tables using PyMuPDF's table detection
            page_tables = page.find_tables()
            
            for i, table in enumerate(page_tables):
                table_data = table.extract()
                if table_data:
                    markdown_table = self._convert_table_to_markdown(table_data)
                    tables.append({
                        'table_number': i + 1,
                        'page_number': page_num + 1,
                        'data': table_data,
                        'markdown': markdown_table,
                        'bbox': table.bbox
                    })
        except Exception as e:
            self.logger.debug(f"PyMuPDF table detection failed for page {page_num + 1}: {e}")
            # Try alternative table detection method using text blocks
            try:
                alt_tables = self._extract_tables_alternative(page, page_num)
                tables.extend(alt_tables)
            except Exception as e2:
                self.logger.warning(f"Alternative table extraction also failed for page {page_num + 1}: {e2}")
        
        return tables
    
    def _extract_tables_alternative(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Alternative table extraction using text block analysis."""
        tables = []
        
        # Get text blocks with position info
        text_dict = page.get_text("dict")
        
        # Look for tabular patterns in text blocks
        potential_table_rows = []
        
        for block in text_dict['blocks']:
            if 'lines' in block:
                for line in block['lines']:
                    line_text = ""
                    for span in line['spans']:
                        line_text += span['text']
                    
                    # Check if line looks like table data (contains multiple separated values)
                    line_text = line_text.strip()
                    if line_text and ('  ' in line_text or '\t' in line_text):
                        # Split on multiple spaces or tabs
                        cells = [cell.strip() for cell in re.split(r'\s{2,}|\t', line_text) if cell.strip()]
                        if len(cells) >= 2:  # At least 2 columns
                            potential_table_rows.append(cells)
        
        # If we found potential table rows, create a table
        if len(potential_table_rows) >= 2:  # At least 2 rows
            markdown_table = self._convert_table_to_markdown(potential_table_rows)
            tables.append({
                'table_number': 1,
                'page_number': page_num + 1,
                'data': potential_table_rows,
                'markdown': markdown_table,
                'bbox': [0, 0, page.rect.width, page.rect.height]  # Approximate bbox
            })
        
        return tables
    
    def _convert_table_to_markdown(self, table_data: List[List[str]]) -> str:
        """Convert table data to Markdown format."""
        if not table_data:
            return ""
        
        markdown_lines = []
        
        # Header row
        if table_data:
            header = table_data[0]
            markdown_lines.append("| " + " | ".join(str(cell or "") for cell in header) + " |")
            markdown_lines.append("| " + " | ".join("---" for _ in header) + " |")
            
            # Data rows
            for row in table_data[1:]:
                markdown_lines.append("| " + " | ".join(str(cell or "") for cell in row) + " |")
        
        return "\n".join(markdown_lines)
    
    def _extract_page_images(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from page."""
        images = []
        image_list = page.get_images()
        
        for i, img in enumerate(image_list):
            try:
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_filename = f"page_{page_num + 1}_image_{i + 1}.png"
                    img_path = self.temp_dir / img_filename
                    pix.save(str(img_path))
                    
                    images.append({
                        'image_number': i + 1,
                        'page_number': page_num + 1,
                        'filename': img_filename,
                        'path': str(img_path),
                        'width': pix.width,
                        'height': pix.height
                    })
                
                pix = None  # Free memory
                
            except Exception as e:
                self.logger.warning(f"Failed to extract image {i + 1} from page {page_num + 1}: {e}")
        
        return images
    
    def _process_images_with_ocr(self, images: List[Dict[str, Any]], page_num: int) -> List[Dict[str, Any]]:
        """Process images with OCR to extract text."""
        ocr_results = []
        
        if not OCR_AVAILABLE:
            return ocr_results
        
        for img_info in images:
            try:
                # Load image
                img_path = img_info['path']
                
                # Perform OCR
                text = pytesseract.image_to_string(
                    Image.open(img_path),
                    lang=self.tesseract_lang,
                    config='--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
                )
                
                if text.strip():
                    ocr_results.append({
                        'image_number': img_info['image_number'],
                        'page_number': page_num + 1,
                        'filename': img_info['filename'],
                        'extracted_text': text.strip(),
                        'image_info': img_info
                    })
                    
            except Exception as e:
                self.logger.warning(f"OCR failed for image {img_info['filename']}: {e}")
        
        return ocr_results
    
    def _generate_markdown(self, result: Dict[str, Any]) -> str:
        """Generate structured Markdown content according to specifications."""
        markdown_lines = []
        
        # Title from metadata or filename
        title = result['metadata'].get('title', '').strip()
        if not title:
            title = result['metadata']['file_name'].replace('.pdf', '')
        markdown_lines.append(f"# {title}")
        markdown_lines.append("")
        
        # Document metadata section
        markdown_lines.append("## Document Information")
        markdown_lines.append("")
        metadata = result['metadata']
        
        markdown_lines.append(f"- **File:** {metadata['file_name']}")
        markdown_lines.append(f"- **Pages:** {metadata['total_pages']}")
        markdown_lines.append(f"- **File Size:** {metadata['file_size']:,} bytes")
        
        if metadata.get('author'):
            markdown_lines.append(f"- **Author:** {metadata['author']}")
        if metadata.get('creator'):
            markdown_lines.append(f"- **Creator:** {metadata['creator']}")
        if metadata.get('producer'):
            markdown_lines.append(f"- **Producer:** {metadata['producer']}")
        if metadata.get('creation_date'):
            markdown_lines.append(f"- **Created:** {metadata['creation_date']}")
        if metadata.get('modification_date'):
            markdown_lines.append(f"- **Modified:** {metadata['modification_date']}")
        if metadata.get('subject'):
            markdown_lines.append(f"- **Subject:** {metadata['subject']}")
        if metadata.get('keywords'):
            markdown_lines.append(f"- **Keywords:** {metadata['keywords']}")
        
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")
        
        # Process content by pages with improved structure
        for page_info in result['pages']:
            # Skip page headers if they contain repetitive information
            main_content_blocks = []
            headers_processed = []
            
            # Separate content types
            headers = [block for block in page_info['structured_content'] if block['is_header']]
            regular_content = [block for block in page_info['structured_content'] 
                             if not block['is_header'] and not block['is_footer'] 
                             and not block['is_page_header'] and not block['is_footnote']
                             and block['text'].strip()]
            
            # Add page header only if there's substantial content
            if headers or regular_content or page_info['tables'] or page_info['images_with_text']:
                markdown_lines.append(f"## Page {page_info['page_number']}")
                markdown_lines.append("")
            
            # Process headers with proper hierarchy
            for header in headers:
                if header['text'].strip():
                    level = min(header['header_level'], 3)  # Limit to h3
                    prefix = "#" * (level + 2)  # +2 because we start from h3 (page is h2)
                    markdown_lines.append(f"{prefix} {header['text'].strip()}")
                    markdown_lines.append("")
                    headers_processed.append(header['text'])
            
            # Add regular content paragraphs
            if regular_content:
                for block in regular_content:
                    text = block['text'].strip()
                    if text and len(text) > 10:  # Skip very short text blocks
                        # Clean up text formatting
                        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                        markdown_lines.append(text)
                        markdown_lines.append("")
            
            # Add tables with better formatting
            for i, table in enumerate(page_info['tables']):
                if table['markdown'].strip():
                    markdown_lines.append(f"### Table {table['table_number']}")
                    markdown_lines.append("")
                    markdown_lines.append(table['markdown'])
                    markdown_lines.append("")
            
            # Add images with OCR text in specified format
            for img_ocr in page_info['images_with_text']:
                if img_ocr['extracted_text'].strip():
                    clean_text = img_ocr['extracted_text'].strip()
                    markdown_lines.append(f"### [Figure {img_ocr['image_number']}: Extracted Text]")
                    markdown_lines.append("")
                    markdown_lines.append(clean_text)
                    markdown_lines.append("")
            
            # Add footnotes if present
            if page_info['footnotes']:
                markdown_lines.append("### Footnotes")
                markdown_lines.append("")
                for footnote in page_info['footnotes']:
                    if footnote['text'].strip():
                        markdown_lines.append(f"- {footnote['text'].strip()}")
                markdown_lines.append("")
            
            # Add page headers and footers if they contain useful information
            useful_headers = [h for h in page_info['page_headers'] 
                            if h['text'].strip() and len(h['text'].strip()) > 5]
            useful_footers = [f for f in page_info['page_footers'] 
                            if f['text'].strip() and len(f['text'].strip()) > 5]
            
            if useful_headers:
                markdown_lines.append("### Page Header")
                markdown_lines.append("")
                for header in useful_headers:
                    markdown_lines.append(header['text'].strip())
                markdown_lines.append("")
            
            if useful_footers:
                markdown_lines.append("### Page Footer")
                markdown_lines.append("")
                for footer in useful_footers:
                    markdown_lines.append(footer['text'].strip())
                markdown_lines.append("")
        
        # Clean up final output
        final_content = []
        for line in markdown_lines:
            final_content.append(line)
        
        # Remove excessive empty lines
        result_lines = []
        prev_empty = False
        for line in final_content:
            if line.strip() == "":
                if not prev_empty:
                    result_lines.append(line)
                prev_empty = True
            else:
                result_lines.append(line)
                prev_empty = False
        
        return "\n".join(result_lines)