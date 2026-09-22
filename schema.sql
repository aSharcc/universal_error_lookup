DROP TABLE IF EXISTS searches;
DROP TABLE IF EXISTS solutions;

CREATE TABLE solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_code TEXT NOT NULL,
    solution TEXT NOT NULL,
    author TEXT NOT NULL,
    votes INTEGER DEFAULT 0
);

CREATE TABLE searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_code TEXT NOT NULL,
    source_api TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);