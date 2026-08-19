import docx
import logging

logger = logging.getLogger(__name__)


class DOCXProcessor:
    """Extracts text from Word documents (.docx) into structured sections."""
    
    @staticmethod
    def extract(file_path: str) -> list[dict]:
        try:
            doc = docx.Document(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read Word document (.docx): {str(e)}")
        
        sections = []
        current_heading = "Document Content"
        current_block = []
        current_length = 0
        section_idx = 1

        def flush_block(heading_name):
            nonlocal current_block, current_length, section_idx
            if current_block:
                body = "\n".join(current_block).strip()
                if body:
                    sections.append({
                        'page_number': section_idx,
                        'section': heading_name,
                        'text': body,
                        'file_type': 'docx'
                    })
                    section_idx += 1
                current_block = []
                current_length = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # Check for Heading style or bold standalone title
            is_heading = para.style and para.style.name.startswith('Heading')
            
            if is_heading:
                flush_block(current_heading)
                current_heading = text
            else:
                current_block.append(text)
                current_length += len(text)
                # Flush block if length exceeds 1000 chars to ensure good vector chunking
                if current_length >= 1000:
                    flush_block(current_heading)

        # Include tables text
        for table in doc.tables:
            table_rows = []
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_text:
                    table_rows.append(row_text)
            if table_rows:
                current_block.append("\n".join(table_rows))
                current_length += sum(len(r) for r in table_rows)
                if current_length >= 1000:
                    flush_block(f"{current_heading} (Table Data)")

        flush_block(current_heading)

        if not sections:
            # Fallback if docx has text in shapes/textboxes or unrecognized elements
            full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
            if full_text.strip():
                sections.append({
                    'page_number': 1,
                    'section': 'Full Document Text',
                    'text': full_text.strip(),
                    'file_type': 'docx'
                })
            else:
                raise ValueError("No extractable text found in Word document.")
            
        logger.info(f"Extracted {len(sections)} sections from Word document {file_path}")
        return sections
