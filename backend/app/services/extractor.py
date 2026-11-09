import os
from typing import List, Dict, Any, Optional
import pymupdf  # PyMuPDF
from docx import Document as DocxDocument

class DocumentExtractionError(Exception):
    pass

def extract_pdf_passages(file_path: str) -> List[Dict[str, Any]]:
    passages = []
    try:
        doc = pymupdf.open(file_path)
    except Exception as e:
        raise DocumentExtractionError(f"Corrupted or invalid PDF file: {str(e)}")

    if doc.page_count == 0:
        raise DocumentExtractionError("PDF file contains no pages")

    passage_idx = 1
    total_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text").strip()
        if not page_text:
            continue

        # Split into meaningful paragraph blocks
        blocks = [b.strip() for b in page_text.split("\n\n") if b.strip()]
        for block in blocks:
            # Skip very short noise
            if len(block) < 15:
                continue
            char_start = len(total_text)
            total_text += block + "\n\n"
            char_end = len(total_text)

            # Try to identify heading / section title if first line is short
            lines = block.split("\n")
            section_title = None
            if len(lines) > 1 and len(lines[0]) < 80:
                section_title = lines[0].strip()

            passages.append({
                "passage_number": passage_idx,
                "page_number": page_num + 1,
                "section_title": section_title,
                "content": block,
                "char_start": char_start,
                "char_end": char_end
            })
            passage_idx += 1

    doc.close()
    if not passages and not total_text.strip():
        raise DocumentExtractionError("Document is empty or contains no extractable text")
    return passages

def extract_docx_passages(file_path: str) -> List[Dict[str, Any]]:
    try:
        doc = DocxDocument(file_path)
    except Exception as e:
        raise DocumentExtractionError(f"Corrupted or invalid DOCX file: {str(e)}")

    passages = []
    passage_idx = 1
    current_section = "General"
    total_text = ""

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Check if heading
        if para.style.name.startswith("Heading"):
            current_section = text
            continue

        if len(text) < 15:
            continue

        char_start = len(total_text)
        total_text += text + "\n\n"
        char_end = len(total_text)

        passages.append({
            "passage_number": passage_idx,
            "page_number": 1,  # DOCX doesn't have fixed pagination without rendering
            "section_title": current_section,
            "content": text,
            "char_start": char_start,
            "char_end": char_end
        })
        passage_idx += 1

    # Also extract tables from docx
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if len(row_text) > 15:
                char_start = len(total_text)
                total_text += row_text + "\n\n"
                char_end = len(total_text)
                passages.append({
                    "passage_number": passage_idx,
                    "page_number": 1,
                    "section_title": f"{current_section} (Table Data)",
                    "content": row_text,
                    "char_start": char_start,
                    "char_end": char_end
                })
                passage_idx += 1

    if not passages:
        raise DocumentExtractionError("Document is empty or contains no extractable text")
    return passages

def extract_txt_passages(file_path: str) -> List[Dict[str, Any]]:
    encodings = ["utf-8", "latin-1", "cp1252"]
    content = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise DocumentExtractionError("Failed to decode text file with standard encodings")

    if not content.strip():
        raise DocumentExtractionError("Document is empty")

    passages = []
    passage_idx = 1
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    total_text = ""

    current_section = "General Notes"
    for p in paragraphs:
        # Check if single line header
        lines = p.split("\n")
        if len(lines) == 1 and (p.startswith("#") or (p.isupper() and len(p) < 60) or (p.endswith(":") and len(p) < 30 and not any(p.lower().startswith(x) for x in ["task:", "note:", "status:"]))):
            current_section = p.lstrip("#").strip()
            continue

        char_start = len(total_text)
        total_text += p + "\n\n"
        char_end = len(total_text)

        passages.append({
            "passage_number": passage_idx,
            "page_number": 1,
            "section_title": current_section,
            "content": p,
            "char_start": char_start,
            "char_end": char_end
        })
        passage_idx += 1

    if not passages:
        raise DocumentExtractionError("Document is empty or contains no extractable paragraphs")
    return passages

def extract_document(file_path: str, filename: str) -> List[Dict[str, Any]]:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_pdf_passages(file_path)
    elif ext == ".docx":
        return extract_docx_passages(file_path)
    elif ext in (".txt", ".md"):
        return extract_txt_passages(file_path)
    else:
        raise DocumentExtractionError(f"Unsupported file format '{ext}'. Supported formats: PDF, DOCX, TXT")
