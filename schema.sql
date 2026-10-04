PRAGMA foreign_keys = ON;

-- A. Knowledge: information Rabbit discovers
CREATE TABLE IF NOT EXISTS knowledge (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    topic         TEXT NOT NULL,
    claim         TEXT NOT NULL,
    source        TEXT,
    confidence    REAL NOT NULL DEFAULT 0.5 CHECK (confidence BETWEEN 0.0 AND 1.0),
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    last_verified TEXT
);

-- B. Experiences: attempts and their outcomes (failures are kept too)
CREATE TABLE IF NOT EXISTS experiences (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task       TEXT NOT NULL,
    action     TEXT NOT NULL,
    result     TEXT,
    success    INTEGER NOT NULL DEFAULT 0 CHECK (success IN (0, 1)),
    reason     TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- C. Capabilities: what Rabbit discovers about applications and tools
CREATE TABLE IF NOT EXISTS capabilities (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    application_name TEXT NOT NULL,
    capability_name  TEXT NOT NULL,
    interface_type   TEXT NOT NULL,          -- CLI, API, GUI, accessibility, etc.
    instructions     TEXT,
    evidence         TEXT,
    confidence       REAL NOT NULL DEFAULT 0.5 CHECK (confidence BETWEEN 0.0 AND 1.0),
    last_verified    TEXT
);

-- D. Lessons: reusable lessons from successful and failed attempts
CREATE TABLE IF NOT EXISTS lessons (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type            TEXT NOT NULL,
    lesson               TEXT NOT NULL,
    conditions           TEXT,
    source_experience_id INTEGER,
    created_at           TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_experience_id) REFERENCES experiences(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_knowledge_topic   ON knowledge(topic);
CREATE INDEX IF NOT EXISTS idx_experiences_task  ON experiences(task);
CREATE INDEX IF NOT EXISTS idx_capabilities_app  ON capabilities(application_name);
CREATE INDEX IF NOT EXISTS idx_lessons_type      ON lessons(task_type);