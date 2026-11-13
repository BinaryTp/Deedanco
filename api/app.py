import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_document
from extraction.claim_extractor import extract_claims_from_chunks
from clustering.topic_clustering import cluster_claims
from detection.contradiction_detector import detect_contradictions_in_clusters
from reporting.report_generator import generate_contradiction_report, save_findings_to_db

app = Flask(__name__)
CORS(app)  # allows the React app (different port) to call this API

UPLOAD_DIR = "data/raw_docs/uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    files = request.files.getlist("documents")

    if not files:
        return jsonify({"error": "No files uploaded. Use field name 'documents'."}), 400

    all_chunks = []
    saved_filenames = []

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)
        saved_filenames.append(filename)

        try:
            result = load_document(file_path)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        chunks = chunk_document(result)
        for chunk in chunks:
            chunk["source"] = f"{filename} ({chunk['source']})"
        all_chunks.extend(chunks)

    claims = extract_claims_from_chunks(all_chunks)
    clusters = cluster_claims(claims)
    findings = detect_contradictions_in_clusters(clusters)

    report = generate_contradiction_report(findings)
    save_findings_to_db(findings)

    return jsonify({
        "files_processed": saved_filenames,
        "total_claims": len(claims),
        "total_contradictions": len(report),
        "contradictions": report
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)