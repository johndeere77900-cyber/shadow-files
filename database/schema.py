"""
Shadow Files database schema.

This module defines the initial persistent database structure for:

- cases
- jobs
- audit events

The schema is intentionally small at this stage. Evidence, sources,
scripts, production records, QC, and publication records will be added
in their respective phases.
"""

import sqlite3


SCHEMA_VERSION = 1


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    intent TEXT NOT NULL,
    command TEXT NOT NULL,
    target TEXT NOT NULL,
    previous_state TEXT,
    new_state TEXT,
    result TEXT NOT NULL,
    error TEXT,
    provider TEXT,
    job_id TEXT,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_cases_state
    ON cases(state);

CREATE INDEX IF NOT EXISTS idx_jobs_status
    ON jobs(status);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp
    ON audit_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_job_id
    ON audit_events(job_id);
"""


def create_schema(connection: sqlite3.Connection) -> None:
    """
    Create all Phase 7 tables and indexes if they do not already exist.
    """

    connection.executescript(SCHEMA_SQL)

    connection.execute(
        """
        INSERT OR IGNORE INTO schema_metadata (
            key,
            value
        )
        VALUES (
            'schema_version',
            ?
        )
        """,
        (str(SCHEMA_VERSION),),
    )

    connection.commit()
