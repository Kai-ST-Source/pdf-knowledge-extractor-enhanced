"""
AI analysis module using Google Gemini.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from PIL import Image


class AIAnalyzer:
    """Analyze documents using Google Gemini AI."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the analyzer with configuration."""
        self.config = config
        self.api_key = config.get("gemini_api_key")
        
        # Initialize Gemini client only if API key is provided
        self.gemini_client = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_client = genai.GenerativeModel(
                    model_name=config.get("model_name", "gemini-1.5-flash"),
                    generation_config=genai.types.GenerationConfig(
                        temperature=config.get("temperature", 0.3),
                        max_output_tokens=config.get("max_tokens", 8192)
                    )
                )
                logging.info("Gemini client initialized successfully in analyzer")
            except Exception as e:
                logging.warning(f"Failed to initialize Gemini client in analyzer: {e}")
        else:
            logging.info("No API key provided - AI analysis disabled in analyzer")
        
        # Load categories from config or use defaults
        if config.get('analysis_prompt', {}).get('default_categories'):
            self.categories = {k: [] for k in config.get('analysis_prompt', {}).get('default_categories', {}).keys()}
        else:
            self.categories = {
                "概念・理論": [],
                "方法論・手順": [],
                "事例・ケーススタディ": [],
                "データ・数値": [],
                "注意点・リスク": [],
                "ベストプラクティス": []
            }
        
    def analyze(self, text: str, images: List[Path]) -> Dict[str, Any]:
        """Analyze document with AI.
        
        Args:
            text: Extracted text from document
            images: List of image paths from document
            
        Returns:
            Dictionary of categorized knowledge
        """
        try:
            prompt = self._build_analysis_prompt()
            
            # Prepare content for Gemini
            content = [prompt]
            
            # Add text if available
            if text.strip():
                content.append(f"Document Text:\n{text}")
                logging.debug(f"Added text content: {len(text)} characters")
            else:
                logging.warning("No text content available for analysis")
            
            # Add images (limit to prevent token overflow)
            image_count = 0
            for image_path in images[:10]:
                if image_path.exists():
                    try:
                        content.append(Image.open(image_path))
                        image_count += 1
                        logging.debug(f"Added image: {image_path}")
                    except Exception as e:
                        logging.warning(f"Failed to load image {image_path}: {e}")
            
            logging.info(f"Sending to Gemini: {len(content)} content items ({image_count} images)")
            
            response = self.gemini_client.generate_content(content)
            
            if not response or not response.text:
                logging.error("Empty response from Gemini")
                raise ValueError("Empty response from Gemini")
            
            logging.debug(f"Gemini response length: {len(response.text)} characters")
            return self._parse_response(response.text)
            
        except Exception as e:
            logging.error(f"Error analyzing with Gemini: {e}")
            raise
    
    def analyze_detailed(self, detailed_text_info: Dict[str, Any], images: List[Path]) -> Dict[str, Any]:
        """Analyze document with detailed text information for finer granularity.
        
        Args:
            detailed_text_info: Detailed text information from extractor
            images: List of image paths from document
            
        Returns:
            Dictionary of categorized knowledge with enhanced detail
        """
        try:
            prompt = self._build_detailed_analysis_prompt()
            
            # Prepare content for Gemini
            content = [prompt]
            
            # Build structured text content
            structured_content = self._build_structured_content(detailed_text_info)
            if structured_content:
                content.append(f"Structured Document Content:\n{structured_content}")
                logging.debug(f"Added structured content: {len(structured_content)} characters")
            
            # Add raw text as fallback
            if detailed_text_info.get('raw_text', '').strip():
                content.append(f"Raw Document Text:\n{detailed_text_info['raw_text']}")
                logging.debug(f"Added raw text: {len(detailed_text_info['raw_text'])} characters")
            
            # Add images
            image_count = 0
            for image_path in images[:10]:
                if image_path.exists():
                    try:
                        content.append(Image.open(image_path))
                        image_count += 1
                        logging.debug(f"Added image: {image_path}")
                    except Exception as e:
                        logging.warning(f"Failed to load image {image_path}: {e}")
            
            logging.info(f"Sending detailed analysis to Gemini: {len(content)} content items ({image_count} images)")
            
            response = self.gemini_client.generate_content(content)
            
            if not response or not response.text:
                logging.error("Empty response from Gemini")
                raise ValueError("Empty response from Gemini")
            
            logging.debug(f"Gemini detailed response length: {len(response.text)} characters")
            return self._parse_detailed_response(response.text, detailed_text_info)
            
        except Exception as e:
            logging.error(f"Error analyzing with detailed information: {e}")
            raise
    
    def _build_structured_content(self, detailed_text_info: Dict[str, Any]) -> str:
        """Build structured content from detailed text information."""
        content_parts = []
        
        # Add headers with page numbers
        if detailed_text_info.get('headers'):
            content_parts.append("=== 見出し・タイトル ===")
            for header in detailed_text_info['headers']:
                content_parts.append(f"ページ{header['page_number']}: {header['text']}")
            content_parts.append("")
        
        # Add structured text blocks
        if detailed_text_info.get('structured_text'):
            content_parts.append("=== 本文内容 ===")
            for block in detailed_text_info['structured_text']:
                content_parts.append(f"ページ{block['page_number']}: {block['text']}")
            content_parts.append("")
        
        # Add tables
        if detailed_text_info.get('tables'):
            content_parts.append("=== 表・データ ===")
            for table in detailed_text_info['tables']:
                content_parts.append(f"ページ{table['page_number']}:")
                if table.get('data'):
                    for row in table['data']:
                        content_parts.append(" | ".join(str(cell) for cell in row))
                content_parts.append("")
        
        # Add footnotes
        if detailed_text_info.get('footnotes'):
            content_parts.append("=== 脚注・補足情報 ===")
            for footnote in detailed_text_info['footnotes']:
                content_parts.append(f"ページ{footnote['page_number']}: {footnote['text']}")
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _build_detailed_analysis_prompt(self) -> str:
        """Build detailed analysis prompt for fine-grained extraction."""
        # Check for custom prompt in config
        if (self.config and 
            self.config.get('detailed_analysis_prompt', {}).get('custom_prompt')):
            return self.config.get('detailed_analysis_prompt', {}).get('custom_prompt')
        
        # Build default detailed prompt
        categories_section = ""
        format_section = ""
        
        if self.config and self.config.get('detailed_analysis_prompt', {}).get('default_categories'):
            categories_config = self.config.get('detailed_analysis_prompt', {}).get('default_categories', {})
            
            # Build categories section
            for i, (category, description) in enumerate(categories_config.items(), 1):
                categories_section += f"**{i}. {category}**\n- {description}\n\n"
            
            # Build format section
            for i, category in enumerate(categories_config.keys(), 1):
                format_section += f"{i}. {category}\n- [詳細な内容]: [具体的な説明とページ番号]\n\n"
        else:
            # Enhanced categories for detailed analysis
            categories_section = """**1. 概念・理論**
- ビジネス概念、戦略理論、フレームワーク、基本原理、定義など

**2. 方法論・手順**  
- 実施方法、プロセス、ステップ、手順、やり方、具体的な手順など

**3. 事例・ケーススタディ**
- 具体例、成功事例、失敗事例、実際の取り組み、企業事例、実例など

**4. データ・数値**
- 統計数値、売上データ、市場規模、パーセンテージ、年度、金額、具体的な数値など

**5. 注意点・リスク**
- 注意すべき点、課題、問題点、リスク要因、障害、制約など

**6. ベストプラクティス**
- 推奨事項、成功のコツ、効果的な方法、改善案、最適解など

**7. 詳細情報**
- 見出し、タイトル、表の内容、脚注、補足情報など

"""
            format_section = """1. 概念・理論
- [詳細な概念]: [具体的な説明とページ番号]

2. 方法論・手順
- [詳細な方法]: [具体的な手順とページ番号]

3. 事例・ケーススタディ
- [詳細な事例]: [具体的な内容とページ番号]

4. データ・数値
- [詳細なデータ]: [具体的な数値とページ番号]

5. 注意点・リスク
- [詳細な注意点]: [具体的な内容とページ番号]

6. ベストプラクティス
- [詳細な推奨事項]: [具体的な内容とページ番号]

7. 詳細情報
- [見出し・タイトル]: [ページ番号]
- [表の内容]: [具体的なデータとページ番号]
- [脚注・補足]: [具体的な内容とページ番号]

"""
        
        # Get detailed extraction instructions from config
        extraction_instructions = ""
        if self.config and self.config.get('detailed_analysis_prompt', {}).get('extraction_instructions'):
            extraction_instructions = self.config.get('detailed_analysis_prompt', {}).get('extraction_instructions')
        else:
            extraction_instructions = "文書の構造化された情報（見出し、本文、表、脚注など）を活用して、できるだけ詳細で具体的な内容を抽出してください。各項目にはページ番号も含めてください。"
        
        return f"""あなたは優秀な文書分析AIアシスタントです。与えられたビジネス文書の構造化された情報を分析し、重要な知見を以下のカテゴリーに分類して詳細に抽出してください。

**【重要】{extraction_instructions}**

## 抽出カテゴリー：

{categories_section}

## 回答フォーマット：

{format_section}

**分析のポイント：**
- 見出し、タイトル、本文、表、脚注をすべて活用する
- 各項目にページ番号を含める
- 具体的で詳細な内容を抽出する
- 表の内容も詳細に分析する
- 脚注や補足情報も見逃さない
- 各カテゴリーで3-10項目を目標に抽出
- 日本語で明確かつ詳細に記述

それでは、提供された文書を詳細に分析してください：
"""
    
    def _parse_detailed_response(self, response_text: str, detailed_text_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse detailed AI response into structured data."""
        categories = self.categories.copy()
        categories["詳細情報"] = []  # Add detailed information category
        
        current_category = None
        lines = response_text.split('\n')
        
        # Debug: Log the response for troubleshooting
        logging.debug(f"Detailed AI Response:\n{response_text}")
        
        # First pass: Look for category headers
        category_patterns = {}
        for category in categories.keys():
            # Try multiple patterns for category detection
            patterns = [
                f"{i}. {category}" for i in range(1, 8)
            ] + [
                f"**{i}. {category}**" for i in range(1, 8)
            ] + [
                f"## {i}. {category}" for i in range(1, 8)
            ] + [
                f"### {category}",
                f"## {category}",
                f"# {category}",
                category,
                f"【{category}】",
                f"**{category}**",
                f"*{category}*"
            ]
            category_patterns[category] = patterns
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for category headers
            for category, patterns in category_patterns.items():
                if any(pattern in line for pattern in patterns):
                    current_category = category
                    logging.debug(f"Found category '{category}' at line {i}: {line}")
                    break
            
            # Extract items with enhanced detection
            if current_category:
                item = None
                
                # Handle bullet points
                if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                    for bullet in ['- ', '• ', '* ']:
                        if line.startswith(bullet):
                            item = line[len(bullet):].strip()
                            break
                
                # Handle numbered items
                elif line.startswith(tuple(f"{i}. " for i in range(1, 10))):
                    item = line.split('. ', 1)[1].strip() if '. ' in line else None
                
                # Handle items that start with category name followed by colon
                elif current_category in line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        item = parts[1].strip()
                
                # Add item if substantial
                if item and len(item) > 5 and not item.startswith('情報は見つかりません'):
                    categories[current_category].append(item)
                    logging.debug(f"Added detailed item to {current_category}: {item[:60]}...")
        
        # Second pass: Extract additional information from structured data
        self._extract_from_structured_data(categories, detailed_text_info)
        
        # Only add default message if truly no items were found after all attempts
        for category, items in categories.items():
            if not items:
                categories[category] = [f"この文書からは{category}に関する明確な情報を特定できませんでした。"]
                
        # Log final results
        total_items = sum(len(items) for items in categories.values())
        meaningful_items = sum(1 for items in categories.values() for item in items 
                             if not item.startswith('この文書からは'))
        logging.info(f"Detailed extraction results: {total_items} total items ({meaningful_items} meaningful)")
        
        return categories
    
    def _extract_from_structured_data(self, categories: Dict[str, List[str]], detailed_text_info: Dict[str, Any]):
        """Extract additional information from structured data."""
        # Extract from headers
        for header in detailed_text_info.get('headers', []):
            header_text = header['text'].strip()
            if len(header_text) > 3:
                categories["詳細情報"].append(f"見出し: {header_text} (ページ{header['page_number']})")
        
        # Extract from tables
        for table in detailed_text_info.get('tables', []):
            if table.get('data'):
                table_content = []
                for row in table['data']:
                    row_text = " | ".join(str(cell) for cell in row if str(cell).strip())
                    if row_text:
                        table_content.append(row_text)
                
                if table_content:
                    table_summary = f"表の内容: {'; '.join(table_content[:3])} (ページ{table['page_number']})"
                    categories["詳細情報"].append(table_summary)
        
        # Extract from footnotes
        for footnote in detailed_text_info.get('footnotes', []):
            footnote_text = footnote['text'].strip()
            if len(footnote_text) > 5:
                categories["詳細情報"].append(f"脚注: {footnote_text} (ページ{footnote['page_number']})")
    
    def _build_analysis_prompt(self) -> str:
        """Build the analysis prompt for AI."""
        # Check for custom prompt in config
        if (self.config and 
            self.config.get('analysis_prompt', {}).get('custom_prompt')):
            return self.config.get('analysis_prompt', {}).get('custom_prompt')
        
        # Build default prompt using config categories
        categories_section = ""
        format_section = ""
        
        if self.config and self.config.get('analysis_prompt', {}).get('default_categories'):
            categories_config = self.config.get('analysis_prompt', {}).get('default_categories', {})
            
            # Build categories section
            for i, (category, description) in enumerate(categories_config.items(), 1):
                categories_section += f"**{i}. {category}**\n- {description}\n\n"
            
            # Build format section
            for i, category in enumerate(categories_config.keys(), 1):
                format_section += f"{i}. {category}\n- [文書から抽出した内容]: [簡潔な説明]\n\n"
        else:
            # Fallback to hardcoded categories
            categories_section = """**1. 概念・理論**
- ビジネス概念、戦略理論、フレームワーク、基本原理など

**2. 方法論・手順**  
- 実施方法、プロセス、ステップ、手順、やり方など

**3. 事例・ケーススタディ**
- 具体例、成功事例、失敗事例、実際の取り組み、企業事例など

**4. データ・数値**
- 統計数値、売上データ、市場規模、パーセンテージ、年度、金額など

**5. 注意点・リスク**
- 注意すべき点、課題、問題点、リスク要因、障害など

**6. ベストプラクティス**
- 推奨事項、成功のコツ、効果的な方法、改善案など

"""
            format_section = """1. 概念・理論
- [文書から抽出した概念]: [簡潔な説明]

2. 方法論・手順
- [文書から抽出した方法]: [簡潔な説明]

3. 事例・ケーススタディ
- [文書から抽出した事例]: [簡潔な説明]

4. データ・数値
- [文書から抽出したデータ]: [数値と説明]

5. 注意点・リスク
- [文書から抽出した注意点]: [簡潔な説明]

6. ベストプラクティス
- [文書から抽出した推奨事項]: [簡潔な説明]

"""
        
        # Get extraction instructions from config
        extraction_instructions = ""
        if self.config and self.config.get('analysis_prompt', {}).get('extraction_instructions'):
            extraction_instructions = self.config.get('analysis_prompt', {}).get('extraction_instructions')
        else:
            extraction_instructions = "文書から読み取れる内容を積極的に抽出し、各カテゴリーに分類してください。「情報が見つかりません」ではなく、具体的な内容を記述してください。"
        
        return f"""あなたは優秀な文書分析AIアシスタントです。与えられたビジネス文書やプレゼンテーション資料を分析し、重要な知見を以下のカテゴリーに分類して抽出してください。

**【重要】{extraction_instructions}**

## 抽出カテゴリー：

{categories_section}

## 回答フォーマット：

{format_section}

**分析のポイント：**
- 文書のタイトル、見出し、本文を詳しく読み込む
- 営業、マーケティング、ビジネス戦略の内容を重視
- 具体的なアドバイスや提案があれば積極的に抽出
- 各カテゴリーで1-5項目を目標に抽出
- 日本語で明確かつ簡潔に記述

それでは、提供された文書を分析してください：
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        categories = self.categories.copy()
        
        current_category = None
        lines = response_text.split('\n')
        
        # Debug: Log the response for troubleshooting
        logging.debug(f"AI Response:\n{response_text}")
        
        # First pass: Look for category headers
        category_patterns = {}
        for category in categories.keys():
            # Try multiple patterns for category detection
            patterns = [
                f"{i}. {category}" for i in range(1, 7)
            ] + [
                f"**{i}. {category}**" for i in range(1, 7)
            ] + [
                f"## {i}. {category}" for i in range(1, 7)
            ] + [
                f"### {category}",
                f"## {category}",
                f"# {category}",
                category,
                f"【{category}】",
                f"**{category}**",
                f"*{category}*"
            ]
            category_patterns[category] = patterns
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for category headers
            for category, patterns in category_patterns.items():
                if any(pattern in line for pattern in patterns):
                    current_category = category
                    logging.debug(f"Found category '{category}' at line {i}: {line}")
                    break
            
            # Extract items - more flexible detection
            if current_category:
                item = None
                
                # Handle bullet points
                if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                    for bullet in ['- ', '• ', '* ']:
                        if line.startswith(bullet):
                            item = line[len(bullet):].strip()
                            break
                
                # Handle numbered items
                elif line.startswith(tuple(f"{i}. " for i in range(1, 10))):
                    item = line.split('. ', 1)[1].strip() if '. ' in line else None
                
                # Handle items that start with category name followed by colon
                elif current_category in line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        item = parts[1].strip()
                
                # Add item if substantial
                if item and len(item) > 5 and not item.startswith('情報は見つかりません'):
                    categories[current_category].append(item)
                    logging.debug(f"Added item to {current_category}: {item[:60]}...")
        
        # Second pass: If no structured format found, try to extract any meaningful content
        if all(not items for items in categories.values()):
            logging.warning("No structured items found, attempting content extraction")
            
            # Look for any meaningful sentences that could be knowledge
            for line in lines:
                line = line.strip()
                if (len(line) > 20 and 
                    not line.startswith(('**', '##', '#', '```')) and
                    not line.lower().startswith(('document', 'text:', 'それでは')) and
                    ('営業' in line or 'ビジネス' in line or '戦略' in line or '方法' in line or 
                     '事例' in line or 'データ' in line or '注意' in line or 'リスク' in line or
                     'ベスト' in line or '推奨' in line)):
                    
                    # Try to categorize based on keywords
                    if any(word in line for word in ['理論', '概念', 'フレームワーク', '基本']):
                        categories["概念・理論"].append(line)
                    elif any(word in line for word in ['方法', '手順', 'プロセス', 'ステップ']):
                        categories["方法論・手順"].append(line)
                    elif any(word in line for word in ['事例', 'ケース', '実例', '例']):
                        categories["事例・ケーススタディ"].append(line)
                    elif any(word in line for word in ['データ', '数値', '%', '円', '年']):
                        categories["データ・数値"].append(line)
                    elif any(word in line for word in ['注意', 'リスク', '課題', '問題']):
                        categories["注意点・リスク"].append(line)
                    elif any(word in line for word in ['ベスト', '推奨', '効果的', 'コツ']):
                        categories["ベストプラクティス"].append(line)
        
        # Only add default message if truly no items were found after all attempts
        for category, items in categories.items():
            if not items:
                categories[category] = [f"この文書からは{category}に関する明確な情報を特定できませんでした。"]
                
        # Log final results
        total_items = sum(len(items) for items in categories.values())
        meaningful_items = sum(1 for items in categories.values() for item in items 
                             if not item.startswith('この文書からは'))
        logging.info(f"Extraction results: {total_items} total items ({meaningful_items} meaningful)")
        
        return categories