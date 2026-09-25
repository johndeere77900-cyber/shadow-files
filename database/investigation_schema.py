"""
Shadow Files investigation database schema.

Phase 12 adds persistent investigation records without modifying the
existing Phase 11 case/evidence tables.

Investigation records belong to cases. Research sources, research
items, and timeline events belong to investigations.
"""

import sqlite3


INVESTIGATION_SCHEMA_VERSION = 1


def create_investigation_schema(
    connection: sqlite3.Connection,
) -> None:
    """Create the Phase 12 investigation tables."""

    connection.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS investigations (
            investigation_id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            notes TEXT NOT NULL,
            FOREIGN KEY (case_id)
                REFERENCES cases(case_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS research_sources (
            source_id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            publisher TEXT,
            discovered_at TEXT NOT NULL,
            FOREIGN KEY (investigation_id)
                REFERENCES investigations(investigation_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS research_items (
            item_id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            statement TEXT NOT NULL,
            discovered_at TEXT NOT NULL,
            source_id TEXT,
            notes TEXT NOT NULL,
            FOREIGN KEY (investigation_id)
                REFERENCES investigations(investigation_id)
                ON DELETE CASCADE,
            FOREIGN KEY (source_id)
                REFERENCES research_sources(source_id)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS investigation_timeline (
            event_id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL,
            event_date TEXT NOT NULL,
            description TEXT NOT NULL,
            source_id TEXT,
            certainty TEXT NOT NULL,
            notes TEXT NOT NULL,
            FOREIGN KEY (investigation_id)
                REFERENCES investigations(investigation_id)
                ON DELETE CASCADE,
            FOREIGN KEY (source_id)
                REFERENCES research_sources(source_id)
                ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_investigations_case
            ON investigations(case_id);

        CREATE INDEX IF NOT EXISTS idx_investigations_status
            ON investigations(status);

        CREATE INDEX IF NOT EXISTS idx_research_sources_investigation
            ON research_sources(investigation_id);

        CREATE INDEX IF NOT EXISTS idx_research_items_investigation
            ON research_items(investigation_id);

        CREATE INDEX IF NOT EXISTS idx_research_items_source
            ON research_items(source_id);

        CREATE INDEX IF NOT EXISTS idx_investigation_timeline_investigation
            ON investigation_timeline(investigation_id);

        CREATE INDEX IF NOT EXISTS idx_investigation_timeline_date
            ON investigation_timeline(event_date);
        """
    )

    connection.commit()
