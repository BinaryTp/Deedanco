import os
import pdfplumber
from docx import Document


def load_pdf(file_path):
    """Extract raw text from a PDF file, page by page."""
    text_by_page = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            text_by_page.append({
                "page": i + 1,
                "text": page_text
            })
    return text_by_page


def load_docx(file_path):
    """Extract raw text from a DOCX file, paragraph by paragraph."""
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return paragraphs


def load_txt(file_path):
    """Extract raw text from a plain TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_document(file_path):
    """Detect file type by extension and load accordingly."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return {"type": "pdf", "content": load_pdf(file_path)}
    elif ext == ".docx":
        return {"type": "docx", "content": load_docx(file_path)}
    elif ext == ".txt":
        return {"type": "txt", "content": load_txt(file_path)}
    else:
        raise ValueError(f"Unsupported file type: {ext}")