"""
Shadow Files production database schema.

Phase 13 stores production records separately from investigation data
while maintaining references to the originating case and investigation.
"""

import sqlite3


def create_production_schema(
    connection: sqlite3.Connection,
) -> None:
    """
    Create the Phase 13 production tables.

    The operation is idempotent and does not delete or replace existing
    production records.
    """

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS productions (
            production_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            investigation_id TEXT NOT NULL,
            status TEXT NOT NULL,
            title TEXT,
            content_type TEXT,
            notes TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (case_id)
                REFERENCES cases(case_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS production_assets (
            asset_id TEXT PRIMARY KEY,
            production_id TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            status TEXT NOT NULL,
            name TEXT NOT NULL,
            location TEXT,
            source_id TEXT,
            checksum TEXT,
            mime_type TEXT,
            duration_seconds REAL,
            notes TEXT NOT NULL,
            FOREIGN KEY (production_id)
                REFERENCES productions(production_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS production_events (
            event_id TEXT PRIMARY KEY,
            production_id TEXT NOT NULL,
            from_status TEXT,
            to_status TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            reason TEXT NOT NULL,
            FOREIGN KEY (production_id)
                REFERENCES productions(production_id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_productions_case
            ON productions(case_id);

        CREATE INDEX IF NOT EXISTS idx_productions_investigation
            ON productions(investigation_id);

        CREATE INDEX IF NOT EXISTS idx_productions_status
            ON productions(status);

        CREATE INDEX IF NOT EXISTS idx_productions_created
            ON productions(created_at);

        CREATE INDEX IF NOT EXISTS idx_production_assets_production
            ON production_assets(production_id);

        CREATE INDEX IF NOT EXISTS idx_production_assets_status
            ON production_assets(status);

        CREATE INDEX IF NOT EXISTS idx_production_events_production
            ON production_events(production_id);

        CREATE INDEX IF NOT EXISTS idx_production_events_occurred
            ON production_events(occurred_at);
        """
    )

    connection.commit()
