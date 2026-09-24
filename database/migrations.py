"""
Shadow Files database migration layer.

Phase 7 starts with schema version 1.

Migrations are kept separate from schema creation so future database
changes can be applied in a controlled and traceable manner without
silently destroying existing data.
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
    """
    Return the currently recorded database schema version.

    A database without metadata is treated as version 0.
    """

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

    Phase 7 currently has only schema version 1.
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

    raise MigrationError(
        f"No migration path exists from version "
        f"{current_version} to {SCHEMA_VERSION}."
  )
