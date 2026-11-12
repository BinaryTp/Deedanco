import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document
from extraction.claim_extractor import extract_claims_from_chunks

file_path = "data/raw_docs/sample_policy.txt"

result = load_document(file_path)
chunks = chunk_document(result)

print(f"Extracting claims from {len(chunks)} chunks...\n")
claims = extract_claims_from_chunks(chunks)

for i, claim in enumerate(claims):
    print(f"[{i+1}] {claim}")