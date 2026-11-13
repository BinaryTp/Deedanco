import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document
from extraction.claim_extractor import extract_claims_from_chunks
from clustering.topic_clustering import cluster_claims
from detection.contradiction_detector import detect_contradictions_in_clusters

FILES = [
    "data/raw_docs/policy_2024.txt",
    "data/raw_docs/policy_2026_circular.txt",
]

all_chunks = []
for file_path in FILES:
    result = load_document(file_path)
    chunks = chunk_document(result)
    filename = os.path.basename(file_path)
    for chunk in chunks:
        chunk["source"] = f"{filename} ({chunk['source']})"
    all_chunks.extend(chunks)

print(f"Loaded {len(all_chunks)} chunks from {len(FILES)} documents.\n")

claims = extract_claims_from_chunks(all_chunks)
clusters = cluster_claims(claims)

print(f"Formed {len(clusters)} clusters.\n")
for i, cluster in enumerate(clusters):
    print(f"Cluster {i}: {len(cluster['claims'])} claim(s)")
    for c in cluster["claims"]:
        print(f"   [{c['topic']} | {c['entity']}] {c['value']} (cond: {c['condition']}) — {c['source']}")
print()

findings = detect_contradictions_in_clusters(clusters)

print(f"\n=== {len(findings)} comparison(s) made ===\n")
for f in findings:
    print(f"{f['relationship'].upper()} (confidence: {f['confidence']}, method: {f['method']})")
    print(f"  A [{f['claim_a']['source']}]: \"{f['claim_a']['original_text']}\"")
    print(f"  B [{f['claim_b']['source']}]: \"{f['claim_b']['original_text']}\"")
    print(f"  Explanation: {f['explanation']}\n")