-- Separate from the core four tables: stores "chunk data" (useless/discarded data).
CREATE TABLE IF NOT EXISTS chunk_data (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    content        TEXT NOT NULL,        -- short summary or snippet, not whole documents
    reason_useless TEXT NOT NULL,        -- why it was judged useless
    source         TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_chunk_reason ON chunk_data(reason_useless);