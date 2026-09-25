"""
Shadow Files database migration layer.

Phase 7 established schema version 1.

Phase 11 adds schema version 2 for persistent evidence records.
Migrations remain explicit so existing databases are upgraded without
silently destroying data.
"""

import sqlite3

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
    Bring the database to the current schema version.

    Version 1 is upgraded to version 2 by adding the Phase 11
    evidence table and indexes.
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
