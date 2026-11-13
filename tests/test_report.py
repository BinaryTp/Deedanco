import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document
from extraction.claim_extractor import extract_claims_from_chunks
from clustering.topic_clustering import cluster_claims
from detection.contradiction_detector import detect_contradictions_in_clusters
from reporting.report_generator import (
    generate_contradiction_report,
    print_report,
    export_report_json,
    save_findings_to_db,
)

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

claims = extract_claims_from_chunks(all_chunks)
clusters = cluster_claims(claims)
findings = detect_contradictions_in_clusters(clusters)

report = generate_contradiction_report(findings)
print_report(report)

json_path = export_report_json(report)
print(f"Report exported to: {json_path}")

saved_count = save_findings_to_db(findings)
print(f"Saved {saved_count} contradiction(s) to database: db/contradictions.db")