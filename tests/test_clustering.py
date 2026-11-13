import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document
from extraction.claim_extractor import extract_claims_from_chunks
from clustering.topic_clustering import cluster_claims

file_path = "data/raw_docs/sample_policy.txt"

result = load_document(file_path)
chunks = chunk_document(result)
claims = extract_claims_from_chunks(chunks)

print(f"Extracted {len(claims)} claims. Clustering...\n")
clusters = cluster_claims(claims)

for i, cluster in enumerate(clusters):
    print(f"--- Cluster {i+1} ({len(cluster['claims'])} claim(s)) ---")
    for c in cluster["claims"]:
        print(f"  [{c['topic']}] {c['value']} — \"{c['original_text']}\"")
    print()