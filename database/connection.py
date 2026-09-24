"""
Shadow Files database connection layer.

Phase 7 uses SQLite as the initial persistent database.
The connection layer is isolated so the storage engine can be
changed later without redesigning the rest of Shadow Files.
"""

import sqlite3
from pathlib import Path
from typing import Union


DatabasePath = Union[str, Path]


def get_connection(database_path: DatabasePath) -> sqlite3.Connection:
    """
    Open a connection to the Shadow Files SQLite database.

    The database file is created automatically when it does not exist.
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
    Open a database connection and enable foreign-key enforcement.

    Schema creation is handled separately by database.schema.
    """

    return get_connection(database_path)
