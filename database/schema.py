"""
Shadow Files database schema.

Phase 7 established the foundational schema.

Phase 11 extends the schema with persistent case/evidence memory
without removing or redesigning existing Phase 7 tables.
"""

import sqlite3


SCHEMA_VERSION = 2


def create_schema(
    connection: sqlite3.Connection,
) -> None:
    """Create the current Shadow Files database schema."""

    connection.executescript(
        """
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
            target TEXT,
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

        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            claim TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_url TEXT,
            evidence_type TEXT NOT NULL,
            status TEXT NOT NULL,
            retrieved_at TEXT NOT NULL,
            publication_date TEXT,
            reliability_assessment TEXT NOT NULL,
            notes TEXT NOT NULL,
            FOREIGN KEY (case_id)
                REFERENCES cases(case_id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_cases_state
            ON cases(state);

        CREATE INDEX IF NOT EXISTS idx_jobs_status
            ON jobs(status);

        CREATE INDEX IF NOT EXISTS idx_audit_timestamp
            ON audit_events(timestamp);

        CREATE INDEX IF NOT EXISTS idx_audit_job
            ON audit_events(job_id);

        CREATE INDEX IF NOT EXISTS idx_evidence_case
            ON evidence(case_id);

        CREATE INDEX IF NOT EXISTS idx_evidence_status
            ON evidence(status);

        CREATE INDEX IF NOT EXISTS idx_evidence_retrieved
            ON evidence(retrieved_at);
        """
    )

    connection.execute(
        """
        INSERT INTO schema_metadata (key, value)
        VALUES ('schema_version', ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
        """,
        (str(SCHEMA_VERSION),),
    )

    connection.commit()
