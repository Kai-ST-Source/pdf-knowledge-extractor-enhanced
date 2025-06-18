# PDF Knowledge Extractor

A powerful tool for extracting structured knowledge from PDF documents using Google Gemini AI.

## Features

- **AI-Powered Analysis**: Uses Google Gemini to extract meaningful insights from PDFs
- **Dual Extraction Modes**: Standard and detailed extraction for different granularity needs
- **Structured Output**: Organizes extracted knowledge into predefined categories
- **Multiple Formats**: Supports JSON, Excel, YAML, PowerPoint, and Markdown output
- **macOS Integration**: Native notifications and app bundle support
- **Batch Processing**: Process multiple PDFs simultaneously

## Extraction Modes

### Standard Extraction
- Basic text extraction from PDF pages
- Suitable for simple documents with clear text structure
- Faster processing time

### Detailed Extraction (Recommended)
- **Enhanced Text Analysis**: Extracts text with preserved formatting and structure
- **Header Detection**: Automatically identifies and categorizes headers and titles
- **Table Extraction**: Extracts and analyzes table contents
- **Footnote Recognition**: Captures footnotes and supplementary information
- **Position-Aware Processing**: Uses text position and formatting for better categorization
- **Page Number Tracking**: Associates extracted information with specific pages

## Knowledge Categories

1. **概念・理論** (Concepts & Theory)
2. **方法論・手順** (Methodology & Procedures)
3. **事例・ケーススタディ** (Case Studies & Examples)
4. **データ・数値** (Data & Numbers)
5. **注意点・リスク** (Cautions & Risks)
6. **ベストプラクティス** (Best Practices)
7. **詳細情報** (Detailed Information) - Only in detailed mode

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key
- macOS (for app bundle)

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your API key in `config.json`

### Basic Usage

```bash
# Process a single PDF with detailed extraction (default)
python src/pdf_knowledge_extractor.py document.pdf

# Process with standard extraction
python src/pdf_knowledge_extractor.py document.pdf --mode standard

# Process with custom output directory
python src/pdf_knowledge_extractor.py document.pdf -o results/

# Specify output formats
python src/pdf_knowledge_extractor.py document.pdf -f json excel powerpoint markdown

# Process all PDFs in a directory
python src/pdf_knowledge_extractor.py /path/to/pdfs/
```

### macOS App

Build the macOS app bundle:
```bash
./scripts/build.sh
```

The app will be created in `dist/PDF Knowledge Extractor.app`

## Configuration

Edit `config.json` to customize:

### Basic Settings
- **gemini_api_key**: Your Google Gemini API key
- **model_name**: Gemini model to use (default: gemini-1.5-flash)
- **temperature**: AI creativity level (0.0-1.0)
- **max_tokens**: Maximum response length
- **log_level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Extraction Settings
- **default_mode**: Default extraction mode ("detailed" or "standard")
- **header_font_size_threshold**: Font size threshold for header detection (default: 14)
- **footnote_position_threshold**: Y-position threshold for footnote detection (default: 700)
- **table_extraction_enabled**: Enable/disable table extraction (default: true)
- **formatting_preservation**: Preserve text formatting (default: true)

### Analysis Prompts
Customize AI prompts for both standard and detailed analysis modes.

## Output Formats

### JSON
Structured data for programmatic use:
```json
{
  "概念・理論": ["concept 1", "concept 2"],
  "方法論・手順": ["method 1", "method 2"],
  "詳細情報": ["見出し: Title (ページ1)", "表の内容: data (ページ2)"],
  "metadata": {
    "extraction_method": "detailed",
    "pages_processed": 5,
    "headers_found": 3,
    "tables_found": 2
  }
}
```

### Excel
Spreadsheet with categories and extracted items, with separate sheets for each category

### YAML
Human-readable structured format

### PowerPoint
Presentation with one slide per category

### Markdown
Formatted markdown document with metadata and categorized content

## Detailed Extraction Features

### Header Detection
- **Font Size Analysis**: Identifies headers based on larger font sizes
- **Formatting Detection**: Recognizes bold, italic, and other formatting
- **Pattern Matching**: Detects common header patterns (numbered lists, chapter titles)
- **Position Analysis**: Considers text position on the page

### Table Extraction
- **Automatic Detection**: Finds tables using PyMuPDF's table detection
- **Data Preservation**: Extracts table content with structure intact
- **Page Association**: Links tables to their source pages
- **Error Handling**: Graceful handling of complex table layouts

### Footnote Processing
- **Position-Based Detection**: Identifies footnotes at page bottom
- **Pattern Recognition**: Detects footnote markers and numbering
- **Content Extraction**: Captures complete footnote text
- **Page Tracking**: Associates footnotes with correct pages

### Enhanced Metadata
Detailed extraction provides comprehensive metadata:
- Processing method used
- Number of pages processed
- Count of headers, tables, and footnotes found
- Processing timestamp
- File information

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify your Gemini API key in config.json
   - Check API quotas and billing

2. **PDF Processing Error**
   - Ensure PDF is not password-protected
   - Check file permissions
   - Try standard extraction mode for problematic files

3. **Memory Issues**
   - Large PDFs may require more RAM
   - Try processing fewer pages at once
   - Use standard extraction for very large documents

4. **Detailed Extraction Issues**
   - Some PDFs may not have clear structure
   - Try standard extraction as fallback
   - Check extraction settings in config.json

### Logs

Check `extraction.log` for detailed error information.

## Development

### Project Structure

```
pdf_knowledge_extractor_mac/
├── src/
│   ├── pdf_knowledge_extractor.py  # Main application
│   ├── core/
│   │   ├── extractor.py            # PDF extraction logic
│   │   ├── analyzer.py             # AI analysis logic
│   │   └── exporter.py             # Output formatting
│   ├── gui/                        # GUI components
│   └── config.json                 # Configuration
├── scripts/
│   └── build.sh                    # Build script
├── docs/                           # Documentation
├── tests/                          # Test files
├── dist/                           # Built applications
├── venv/                           # Virtual environment
└── requirements.txt                # Dependencies
```

### Testing

Run tests with:
```bash
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please check the troubleshooting section above or create an issue in the repository.