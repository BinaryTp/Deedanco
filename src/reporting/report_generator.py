import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "db/contradictions.db"
SCHEMA_PATH = "db/schema.sql"


def init_db(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    """Create the database and table if they don't already exist."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def save_findings_to_db(findings, db_path=DB_PATH):
    """Persist only genuine contradictions into SQLite. Returns how many were saved."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    saved = 0
    for f in findings:
        if f["relationship"] != "contradiction":
            continue

        cursor.execute("""
            INSERT INTO contradictions
            (topic, relationship, confidence, method, explanation,
             claim_a_text, claim_a_source, claim_b_text, claim_b_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f["claim_a"].get("topic"),
            f["relationship"],
            f["confidence"],
            f["method"],
            f["explanation"],
            f["claim_a"]["original_text"],
            f["claim_a"]["source"],
            f["claim_b"]["original_text"],
            f["claim_b"]["source"],
        ))
        saved += 1

    conn.commit()
    conn.close()
    return saved


def generate_contradiction_report(findings):
    """
    Build a clean, structured report (list of dicts) containing only
    genuine contradictions, ready for display or export.
    """
    report = []
    for i, f in enumerate(findings):
        if f["relationship"] != "contradiction":
            continue

        report.append({
            "id": i + 1,
            "topic": f["claim_a"].get("topic"),
            "confidence": f["confidence"],
            "detection_method": f["method"],
            "explanation": f["explanation"],
            "statement_1": {
                "text": f["claim_a"]["original_text"],
                "source": f["claim_a"]["source"],
            },
            "statement_2": {
                "text": f["claim_b"]["original_text"],
                "source": f["claim_b"]["source"],
            },
        })

    return report


def export_report_json(report, output_path="data/processed/contradiction_report.json"):
    """Save the report as a JSON file (useful for the frontend to consume later)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_contradictions": len(report),
            "contradictions": report
        }, f, indent=2)
    return output_path


def print_report(report):
    """Human-readable console version of the report."""
    print(f"\n{'='*60}")
    print(f"CONTRADICTION REPORT — {len(report)} issue(s) found")
    print(f"{'='*60}\n")

    for item in report:
        print(f"[{item['id']}] Topic: {item['topic']}  (confidence: {item['confidence']}, method: {item['detection_method']})")
        print(f"    Statement 1 ({item['statement_1']['source']}):")
        print(f"       \"{item['statement_1']['text']}\"")
        print(f"    Statement 2 ({item['statement_2']['source']}):")
        print(f"       \"{item['statement_2']['text']}\"")
        print(f"    Why: {item['explanation']}\n")