"""
Shadow Files database connection layer.

SQLite is the initial persistent database for Shadow Files.

This module owns database opening and initialization. Initialization
must leave the database ready for application use by applying the
current core and investigation schemas.
"""

import sqlite3
from pathlib import Path
from typing import Union

from database.migrations import migrate_investigation_schema


DatabasePath = Union[str, Path]


def get_connection(
    database_path: DatabasePath,
) -> sqlite3.Connection:
    """
    Open a connection to the Shadow Files SQLite database.

    The database file is created automatically when it does not exist.
    Foreign-key enforcement is enabled for every connection.
    """

    path = Path(database_path)

    if path.parent != Path("."):
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    connection = sqlite3.connect(
        str(path),
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def initialize_database(
    database_path: DatabasePath,
) -> sqlite3.Connection:
    """
    Open and initialize the Shadow Files database.

    The returned connection has the current core schema and
    investigation schema available.

    Existing records are preserved by the migration layer.
    """

    connection = get_connection(
        database_path
    )

    try:
        migrate_investigation_schema(
            connection
        )
    except Exception:
        connection.close()
        raise

    return connection
