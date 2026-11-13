# Architecture — AI Agent for Contradiction Detection in Company Documents

## 1. Overview

This system ingests multiple company policy/rule documents (PDF, DOCX, TXT), extracts atomic
rule statements using an LLM, groups related statements by topic using sentence embeddings,
detects contradictions between related statements using a rule-based + LLM hybrid approach,
and presents the findings through a web interface.

## 2. Tech stack

| Layer                  | Technology                                   | Purpose                                      |
|------------------------|-----------------------------------------------|-----------------------------------------------|
| Frontend               | React + Tailwind CSS (Vite)                  | Upload UI, contradiction report display       |
| App server             | Node.js + Express                            | Proxies requests from React to the Flask API  |
| ML / API service       | Python + Flask                               | Exposes the pipeline as a REST API            |
| Document parsing       | pdfplumber, python-docx                      | Extract text from PDF/DOCX/TXT                |
| Claim extraction       | Groq API (openai/gpt-oss-20b)                | LLM-based rule extraction (few-shot prompting)|
| Embeddings             | sentence-transformers (all-MiniLM-L6-v2)     | Semantic vector representation of claims      |
| Similarity search      | FAISS (IndexFlatL2)                          | Nearest-neighbor vector search                |
| Contradiction reasoning| Rule-based checks + Groq LLM                 | Hybrid NLI-style contradiction classification |
| Database               | SQLite                                       | Persists detected contradictions              |
| Version control        | Git + GitHub                                 | Team collaboration                            |

## 3. High-level data flow

```
 Browser (React)
      │  multipart/form-data (files)
      ▼
 Express (Node.js, :3001)
      │  forwards files
      ▼
 Flask API (Python, :5000) ── POST /api/analyze
      │
      ▼
 ┌─────────────────────────────────────────────────────────┐
 │                  ML Pipeline (src/)                      │
 │                                                           │
 │  1. ingestion/document_loader.py   → raw text per file   │
 │  2. ingestion/chunker.py           → clause-level chunks │
 │  3. extraction/claim_extractor.py  → structured claims   │
 │        (topic, entity, value, condition) via LLM         │
 │  4. clustering/topic_clustering.py → groups claims by    │
 │        topic using embeddings (src/embedding/)           │
 │  5. detection/contradiction_detector.py → compares       │
 │        claims within each cluster (rule-based first,     │
 │        LLM reasoning as fallback)                         │
 │  6. reporting/report_generator.py  → structured report,  │
 │        JSON export, SQLite persistence                   │
 └─────────────────────────────────────────────────────────┘
      │
      ▼
 JSON response (contradictions list)
      │
      ▼
 Express → Browser (React renders the report)
```

## 4. Module responsibilities

### `src/ingestion/`
- `document_loader.py` — detects file type by extension, extracts raw text (per page for PDF,
  per paragraph for DOCX, whole file for TXT).
- `chunker.py` — splits raw text into clause-level chunks using sentence-boundary regex,
  tagging each chunk with its source location (page/paragraph/file).

### `src/extraction/`
- `claim_extractor.py` — sends each chunk to the LLM (Groq, `openai/gpt-oss-20b`) with a
  few-shot prompt, returns structured JSON: `{topic, entity, value, condition}`.

### `src/embedding/`
- `embedding.py` — wraps `sentence-transformers` (`all-MiniLM-L6-v2`) to generate normalized
  384-dimension embeddings for a given text.
- `embedding_store.py` — standalone CLI tool to add text embeddings to a persistent FAISS
  index (`vector_store/storage.index`) with metadata (`vector_store/metadata.json`).
- `search.py` — standalone CLI tool to query the FAISS index for nearest neighbors to a
  given query string.

### `src/clustering/`
- `topic_clustering.py` — reuses `embedding.py`'s `generate_embedding()` to embed each
  claim's extracted topic, then greedily groups claims into clusters using cosine similarity
  (threshold-based, single-linkage style). Claims above the similarity threshold join the
  same cluster; otherwise a new cluster is started.

### `src/detection/`
- `contradiction_detector.py` — for every pair of claims within a cluster:
  1. **Rule-based layer** — handles clear cases deterministically: same topic + same entity
     + differing numeric values → `contradiction`; matching entity-subgroup relationships
     (e.g. "employees" vs "senior management employees") → `agreement`.
  2. **LLM layer** — fallback for anything the rules can't resolve confidently (non-numeric
     values, genuinely ambiguous entities, conditional exceptions). Classifies the pair as
     `contradiction`, `agreement`, or `unrelated` with an explanation and confidence score.

### `src/reporting/`
- `report_generator.py` — filters findings down to genuine contradictions, builds a
  structured report, exports it as JSON (for the frontend), and persists it to SQLite
  (`db/contradictions.db`) for historical record-keeping.

### `api/`
- `app.py` — Flask application exposing:
  - `GET /api/health` — liveness check.
  - `POST /api/analyze` — accepts multipart file uploads (`documents` field, multiple
    files), runs the full pipeline, returns the JSON report.

### `web/`
- `server.js` — Express server exposing the same two routes to the frontend, forwarding
  uploaded files to the Flask API via `axios` + `form-data`, so the frontend never talks to
  Flask directly (keeps Python internal to the backend, matches the required Node.js layer).

### `frontend/`
- React (Vite) + Tailwind CSS single-page app: file upload control, "Analyze Documents"
  button, and a card-based results view rendering each contradiction with both conflicting
  statements, their sources, and the explanation.

## 5. Database schema (`db/schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS contradictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    relationship TEXT NOT NULL,
    confidence REAL,
    method TEXT,
    explanation TEXT,
    claim_a_text TEXT,
    claim_a_source TEXT,
    claim_b_text TEXT,
    claim_b_source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 6. API contract

**`POST /api/analyze`**

Request: `multipart/form-data`, field name `documents` (repeatable, accepts `.pdf`, `.docx`, `.txt`)

Response:
```json
{
  "files_processed": ["policy_2024.txt", "policy_2026_circular.txt"],
  "total_claims": 8,
  "total_contradictions": 4,
  "contradictions": [
    {
      "id": 2,
      "topic": "casual leave",
      "confidence": 0.95,
      "detection_method": "llm",
      "explanation": "...",
      "statement_1": { "text": "...", "source": "policy_2024.txt (txt file)" },
      "statement_2": { "text": "...", "source": "policy_2026_circular.txt (txt file)" }
    }
  ]
}
```

## 7. Running the project locally

Three servers run concurrently, each in its own terminal:

```bash
# Terminal 1 — Flask API
python api/app.py

# Terminal 2 — Express server
cd web && node server.js

# Terminal 3 — React frontend
cd frontend && npm run dev
```

Then open `http://localhost:5173`.

## 8. Known limitations / future work

- Entity-subgroup detection uses substring matching (e.g. "senior management employees"
  contains "employees"); a proper organizational role hierarchy would be more robust.
- The clustering similarity threshold (0.80) is a fixed constant; could be tuned per
  document domain.
- FAISS index in `src/embedding/vector_store/` is currently a separate utility from the
  live clustering pipeline — a future iteration could unify them so clustering queries the
  persistent index instead of re-embedding claims per request.
- Free-tier LLM API (Groq) has rate limits; a production deployment would need a paid tier
  or request queuing.
