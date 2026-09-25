"""
Shadow Files database migration layer.

The migration system upgrades the persistent database without
destructively replacing existing case, evidence, claim, source,
or audit records.

Phase 12 adds investigation and research-memory tables.
"""

import sqlite3

from database.investigation_schema import (
    create_investigation_schema,
)
from database.schema import (
    SCHEMA_VERSION,
    create_schema,
)


class MigrationError(Exception):
    """Raised when a database migration cannot be completed."""


def get_schema_version(
    connection: sqlite3.Connection,
) -> int:
    """Return the currently recorded database schema version."""

    try:
        row = connection.execute(
            """
            SELECT value
            FROM schema_metadata
            WHERE key = 'schema_version'
            """
        ).fetchone()
    except sqlite3.OperationalError:
        return 0

    if row is None:
        return 0

    return int(row["value"])


def migrate(
    connection: sqlite3.Connection,
) -> int:
    """
    Bring the database to the current Phase 7/11 schema.

    Phase 12 investigation tables are intentionally created separately
    by create_investigation_schema() so the core schema version remains
    compatible with the existing Phase 11 database contract.
    """

    current_version = get_schema_version(connection)

    if current_version > SCHEMA_VERSION:
        raise MigrationError(
            "Database schema version is newer than this application."
        )

    if current_version == SCHEMA_VERSION:
        return current_version

    if current_version == 0:
        create_schema(connection)
        return SCHEMA_VERSION

    if current_version == 1:
        connection.executescript(
            """
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
            UPDATE schema_metadata
            SET value = ?
            WHERE key = 'schema_version'
            """,
            (str(SCHEMA_VERSION),),
        )

        connection.commit()
        return SCHEMA_VERSION

    raise MigrationError(
        f"No migration path exists from version "
        f"{current_version} to {SCHEMA_VERSION}."
    )


def migrate_investigation_schema(
    connection: sqlite3.Connection,
) -> None:
    """
    Create the Phase 12 investigation schema.

    This operation is idempotent and preserves all existing records.
    """

    migrate(connection)
    create_investigation_schema(connection)
