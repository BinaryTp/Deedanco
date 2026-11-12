import re


def split_into_clauses(text):
    """Split a block of text into clause-level chunks on sentence boundaries."""
    if not text or not text.strip():
        return []

    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    clauses = [s.strip() for s in sentences if s.strip()]
    return clauses


def chunk_document(document_result):
    """Takes load_document()'s output and returns flat, source-tagged chunks."""
    chunks = []
    doc_type = document_result["type"]
    content = document_result["content"]

    if doc_type == "pdf":
        for page in content:
            for clause in split_into_clauses(page["text"]):
                chunks.append({"text": clause, "source": f"page {page['page']}"})

    elif doc_type == "docx":
        for i, paragraph in enumerate(content):
            for clause in split_into_clauses(paragraph):
                chunks.append({"text": clause, "source": f"paragraph {i + 1}"})

    elif doc_type == "txt":
        for clause in split_into_clauses(content):
            chunks.append({"text": clause, "source": "txt file"})

    return chunks