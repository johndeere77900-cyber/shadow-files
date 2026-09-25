"""
Shadow Files database schema.

Phase 7 established the original persistent database tables.

Phase 11 extends the schema with the complete case/evidence memory
model:

- cases
- evidence
- claims
- evidence_sources
- claim_evidence_links
- jobs
- audit_events
- schema_metadata

The schema is intentionally explicit and uses foreign keys so that
case memory cannot become disconnected from its supporting records.
"""

import sqlite3


SCHEMA_VERSION = 2


def create_schema(
    connection: sqlite3.Connection,
) -> None:
    """
    Create the complete current Shadow Files database schema.

    Schema creation is idempotent. Existing tables and indexes are
    preserved and are not deleted or recreated destructively.
    """

    connection.executescript(
        """
        PRAGMA foreign_keys = ON;

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

        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            statement TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            reviewed_at TEXT,
            notes TEXT NOT NULL,
            FOREIGN KEY (case_id)
                REFERENCES cases(case_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS evidence_sources (
            source_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT,
            publisher TEXT,
            publication_date TEXT,
            retrieved_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS claim_evidence_links (
            link_id TEXT PRIMARY KEY,
            claim_id TEXT NOT NULL,
            evidence_id TEXT NOT NULL,
            relation TEXT NOT NULL,
            notes TEXT NOT NULL,
            FOREIGN KEY (claim_id)
                REFERENCES claims(claim_id)
                ON DELETE CASCADE,
            FOREIGN KEY (evidence_id)
                REFERENCES evidence(evidence_id)
                ON DELETE CASCADE,
            UNIQUE (
                claim_id,
                evidence_id,
                relation
            )
        );

        CREATE INDEX IF NOT EXISTS idx_cases_state
            ON cases(state);

        CREATE INDEX IF NOT EXISTS idx_jobs_status
            ON jobs(status);

        CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp
            ON audit_events(timestamp);

        CREATE INDEX IF NOT EXISTS idx_audit_events_job_id
            ON audit_events(job_id);

        CREATE INDEX IF NOT EXISTS idx_evidence_case
            ON evidence(case_id);

        CREATE INDEX IF NOT EXISTS idx_evidence_status
            ON evidence(status);

        CREATE INDEX IF NOT EXISTS idx_evidence_retrieved
            ON evidence(retrieved_at);

        CREATE INDEX IF NOT EXISTS idx_claims_case
            ON claims(case_id);

        CREATE INDEX IF NOT EXISTS idx_claims_status
            ON claims(status);

        CREATE INDEX IF NOT EXISTS idx_claims_created
            ON claims(created_at);

        CREATE INDEX IF NOT EXISTS idx_evidence_sources_publisher
            ON evidence_sources(publisher);

        CREATE INDEX IF NOT EXISTS idx_evidence_sources_retrieved
            ON evidence_sources(retrieved_at);

        CREATE INDEX IF NOT EXISTS idx_claim_evidence_claim
            ON claim_evidence_links(claim_id);

        CREATE INDEX IF NOT EXISTS idx_claim_evidence_evidence
            ON claim_evidence_links(evidence_id);
        """
    )

    connection.execute(
        """
        INSERT INTO schema_metadata (
            key,
            value
        )
        VALUES (
            'schema_version',
            ?
        )
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
        """,
        (str(SCHEMA_VERSION),),
    )

    connection.commit()
