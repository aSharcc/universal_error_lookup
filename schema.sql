DROP TABLE IF EXISTS searches;
DROP TABLE IF EXISTS solutions;

CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_code TEXT NOT NULL,
    solution TEXT NOT NULL,
    author TEXT NOT NULL,
    context TEXT NOT NULL DEFAULT '',
    votes INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_code TEXT NOT NULL,
    source_api TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    context TEXT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(error_code, context)
);

CREATE INDEX IF NOT EXISTS idx_searches_code ON searches(error_code);
CREATE INDEX IF NOT EXISTS idx_solutions_code ON solutions(error_code);