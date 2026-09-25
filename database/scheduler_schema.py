"""
Shadow Files scheduler database schema.

Phase 14 stores production and publication schedule slots separately
from production records while maintaining a foreign-key relationship
to the production domain.
"""

import sqlite3


def create_scheduler_schema(
    connection: sqlite3.Connection,
) -> None:
    """
    Create the Phase 14 scheduler tables.

    The operation is idempotent and preserves existing scheduler data.
    """

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schedule_slots (
            schedule_id TEXT PRIMARY KEY,
            production_id TEXT NOT NULL,
            schedule_type TEXT NOT NULL,
            scheduled_for TEXT NOT NULL,
            status TEXT NOT NULL,
            deadline TEXT,
            timezone_name TEXT NOT NULL,
            notes TEXT NOT NULL,
            FOREIGN KEY (production_id)
                REFERENCES productions(production_id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS schedule_events (
            event_id TEXT PRIMARY KEY,
            schedule_id TEXT NOT NULL,
            from_status TEXT,
            to_status TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            reason TEXT NOT NULL,
            FOREIGN KEY (schedule_id)
                REFERENCES schedule_slots(schedule_id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_schedule_slots_production
            ON schedule_slots(production_id);

        CREATE INDEX IF NOT EXISTS idx_schedule_slots_type
            ON schedule_slots(schedule_type);

        CREATE INDEX IF NOT EXISTS idx_schedule_slots_status
            ON schedule_slots(status);

        CREATE INDEX IF NOT EXISTS idx_schedule_slots_scheduled
            ON schedule_slots(scheduled_for);

        CREATE INDEX IF NOT EXISTS idx_schedule_slots_deadline
            ON schedule_slots(deadline);

        CREATE INDEX IF NOT EXISTS idx_schedule_events_schedule
            ON schedule_events(schedule_id);

        CREATE INDEX IF NOT EXISTS idx_schedule_events_occurred
            ON schedule_events(occurred_at);
        """
    )

    connection.commit()
