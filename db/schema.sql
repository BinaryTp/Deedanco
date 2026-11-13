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