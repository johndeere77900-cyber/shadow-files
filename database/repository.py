"""
Shadow Files repository layer.

This module provides controlled persistence operations for cases, jobs,
and audit events. Higher-level Shadow Files components should use this
repository instead of writing SQL directly.
"""

import sqlite3
from typing import List, Optional

from database.models import (
    AuditEventRecord,
    CaseRecord,
    JobRecord,
)


class DatabaseRepository:
    """Persistent repository for Shadow Files foundation records."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    # ------------------------------------------------------------------
    # CASES
    # ------------------------------------------------------------------

    def create_case(
        self,
        case: CaseRecord,
    ) -> None:
        """Create a new case."""

        self.connection.execute(
            """
            INSERT INTO cases (
                case_id,
                title,
                state,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                case.case_id,
                case.title,
                case.state,
                case.created_at,
                case.updated_at,
            ),
        )

        self.connection.commit()

    def get_case(
        self,
        case_id: str,
    ) -> Optional[CaseRecord]:
        """Retrieve a case by ID."""

        row = self.connection.execute(
            """
            SELECT
                case_id,
                title,
                state,
                created_at,
                updated_at
            FROM cases
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()

        if row is None:
            return None

        return CaseRecord(
            case_id=row["case_id"],
            title=row["title"],
            state=row["state"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update_case_state(
        self,
        case_id: str,
        state: str,
        updated_at: str,
    ) -> None:
        """Update the current state of a case."""

        cursor = self.connection.execute(
            """
            UPDATE cases
            SET
                state = ?,
                updated_at = ?
            WHERE case_id = ?
            """,
            (
                state,
                updated_at,
                case_id,
            ),
        )

        if cursor.rowcount == 0:
            raise KeyError(
                f"Case not found: {case_id}"
            )

        self.connection.commit()

    # ------------------------------------------------------------------
    # JOBS
    # ------------------------------------------------------------------

    def create_job(
        self,
        job: JobRecord,
    ) -> None:
        """Create a new job."""

        self.connection.execute(
            """
            INSERT INTO jobs (
                job_id,
                operation,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                job.job_id,
                job.operation,
                job.status,
                job.created_at,
            ),
        )

        self.connection.commit()

    def get_job(
        self,
        job_id: str,
    ) -> Optional[JobRecord]:
        """Retrieve a job by ID."""

        row = self.connection.execute(
            """
            SELECT
                job_id,
                operation,
                status,
                created_at
            FROM jobs
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()

        if row is None:
            return None

        return JobRecord(
            job_id=row["job_id"],
            operation=row["operation"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def update_job_status(
        self,
        job_id: str,
        status: str,
    ) -> None:
        """Update the status of a job."""

        cursor = self.connection.execute(
            """
            UPDATE jobs
            SET status = ?
            WHERE job_id = ?
            """,
            (
                status,
                job_id,
            ),
        )

        if cursor.rowcount == 0:
            raise KeyError(
                f"Job not found: {job_id}"
            )

        self.connection.commit()

    # ------------------------------------------------------------------
    # AUDIT EVENTS
    # ------------------------------------------------------------------

    def create_audit_event(
        self,
        event: AuditEventRecord,
    ) -> None:
        """Persist an audit event."""

        self.connection.execute(
            """
            INSERT INTO audit_events (
                event_id,
                timestamp,
                actor,
                intent,
                command,
                target,
                previous_state,
                new_state,
                result,
                error,
                provider,
                job_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.timestamp,
                event.actor,
                event.intent,
                event.command,
                event.target,
                event.previous_state,
                event.new_state,
                event.result,
                event.error,
                event.provider,
                event.job_id,
            ),
        )

        self.connection.commit()

    def get_audit_event(
        self,
        event_id: str,
    ) -> Optional[AuditEventRecord]:
        """Retrieve an audit event by ID."""

        row = self.connection.execute(
            """
            SELECT
                event_id,
                timestamp,
                actor,
                intent,
                command,
                target,
                previous_state,
                new_state,
                result,
                error,
                provider,
                job_id
            FROM audit_events
            WHERE event_id = ?
            """,
            (event_id,),
        ).fetchone()

        if row is None:
            return None

        return AuditEventRecord(
            event_id=row["event_id"],
            timestamp=row["timestamp"],
            actor=row["actor"],
            intent=row["intent"],
            command=row["command"],
            target=row["target"],
            previous_state=row["previous_state"],
            new_state=row["new_state"],
            result=row["result"],
            error=row["error"],
            provider=row["provider"],
            job_id=row["job_id"],
        )

    def list_audit_events(
        self,
        job_id: Optional[str] = None,
    ) -> List[AuditEventRecord]:
        """Return audit events, optionally filtered by job ID."""

        if job_id is None:
            rows = self.connection.execute(
                """
                SELECT
                    event_id,
                    timestamp,
                    actor,
                    intent,
                    command,
                    target,
                    previous_state,
                    new_state,
                    result,
                    error,
                    provider,
                    job_id
                FROM audit_events
                ORDER BY timestamp ASC
                """
            ).fetchall()
        else:
            rows = self.connection.execute(
                """
                SELECT
                    event_id,
                    timestamp,
                    actor,
                    intent,
                    command,
                    target,
                    previous_state,
                    new_state,
                    result,
                    error,
                    provider,
                    job_id
                FROM audit_events
                WHERE job_id = ?
                ORDER BY timestamp ASC
                """,
                (job_id,),
            ).fetchall()

        return [
            AuditEventRecord(
                event_id=row["event_id"],
                timestamp=row["timestamp"],
                actor=row["actor"],
                intent=row["intent"],
                command=row["command"],
                target=row["target"],
                previous_state=row["previous_state"],
                new_state=row["new_state"],
                result=row["result"],
                error=row["error"],
                provider=row["provider"],
                job_id=row["job_id"],
            )
            for row in rows
      ]
