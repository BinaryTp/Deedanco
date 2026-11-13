import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document
from extraction.claim_extractor import extract_claims_from_chunks
from clustering.topic_clustering import cluster_claims
from detection.contradiction_detector import detect_contradictions_in_clusters

file_path = "data/raw_docs/sample_policy.txt"

result = load_document(file_path)
chunks = chunk_document(result)
claims = extract_claims_from_chunks(chunks)
clusters = cluster_claims(claims)

print(f"Checking {len(clusters)} clusters for contradictions...\n")
findings = detect_contradictions_in_clusters(clusters)

if not findings:
    print("No clusters had 2+ claims to compare.")

for f in findings:
    print(f"Cluster {f['cluster_index']} — {f['relationship'].upper()} (confidence: {f['confidence']}, method: {f['method']})")
    print(f"  A: \"{f['claim_a']['original_text']}\"")
    print(f"  B: \"{f['claim_b']['original_text']}\"")
    print(f"  Explanation: {f['explanation']}\n")