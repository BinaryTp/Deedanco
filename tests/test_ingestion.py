import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document

file_path = "data/raw_docs/sample_policy.txt"

result = load_document(file_path)
print("File type:", result["type"])

chunks = chunk_document(result)
print(f"\nTotal chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks[:10]):
    print(f"[{i+1}] ({chunk['source']}): {chunk['text']}")