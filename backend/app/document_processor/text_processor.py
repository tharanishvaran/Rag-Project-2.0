import logging
import re

logger = logging.getLogger(__name__)


class TextProcessor:
    """Extracts text from plain text (.txt) and Markdown (.md) documents."""
    
    @staticmethod
    def extract(file_path: str, is_markdown: bool = False) -> list[dict]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")
            
        content = content.strip()
        if not content:
            raise ValueError("File is empty.")
            
        sections = []
        
        if is_markdown:
            # Split markdown by top-level or sub headings (#, ##, ###)
            parts = re.split(r'\n(?=#{1,3}\s+)', content)
            for idx, part in enumerate(parts, start=1):
                clean_part = part.strip()
                if not clean_part:
                    continue
                match = re.match(r'^(#{1,3})\s+(.+)$', clean_part, re.MULTILINE)
                section_title = match.group(2).strip() if match else f"Section {idx}"
                sections.append({
                    'page_number': idx,
                    'section': section_title,
                    'text': clean_part,
                    'file_type': 'md'
                })
        else:
            # Plain text: group into logical blocks (~1000 characters)
            paragraphs = content.split('\n\n')
            current_block = []
            current_length = 0
            block_idx = 1
            
            for para in paragraphs:
                p_text = para.strip()
                if not p_text:
                    continue
                current_block.append(p_text)
                current_length += len(p_text)
                
                if current_length >= 1000:
                    sections.append({
                        'page_number': block_idx,
                        'section': f"Section {block_idx}",
                        'text': "\n\n".join(current_block),
                        'file_type': 'txt'
                    })
                    block_idx += 1
                    current_block = []
                    current_length = 0
                    
            if current_block:
                sections.append({
                    'page_number': block_idx,
                    'section': f"Section {block_idx}",
                    'text': "\n\n".join(current_block),
                    'file_type': 'txt'
                })
                
        if not sections:
            sections.append({
                'page_number': 1,
                'section': 'Content',
                'text': content,
                'file_type': 'md' if is_markdown else 'txt'
            })
            
        logger.info(f"Extracted {len(sections)} sections from text/markdown file {file_path}")
        return sections
