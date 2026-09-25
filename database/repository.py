"""
Shadow Files database repository.

Phase 7 established persistence for cases, jobs, and audit events.

Phase 11 keeps that repository compatible while allowing case creation
through explicit case fields used by the existing regression suite.
"""

import sqlite3
from datetime import datetime
from typing import Optional

from database.models import (
    AuditEventRecord,
    CaseRecord,
    JobRecord,
)


class DatabaseRepository:
    """Persistence boundary for core Shadow Files records."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    # ------------------------------------------------------------------
    # Cases
    # ------------------------------------------------------------------

    def create_case(
        self,
        case_id: str,
        title: str,
        state: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> CaseRecord:
        """Create and return a case record."""

        record = CaseRecord(
            case_id=case_id,
            title=title,
            state=state,
            created_at=created_at,
            updated_at=updated_at,
        )

        self._connection.execute(
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
                record.case_id,
                record.title,
                record.state,
                record.created_at.isoformat(),
                record.updated_at.isoformat(),
            ),
        )

        self._connection.commit()
        return record

    def get_case(
        self,
        case_id: str,
    ) -> Optional[CaseRecord]:
        """Retrieve a case by ID."""

        row = self._connection.execute(
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
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=datetime.fromisoformat(
                row["updated_at"]
            ),
        )

    def update_case_state(
        self,
        case_id: str,
        state: str,
        updated_at: datetime,
    ) -> CaseRecord:
        """Update a case state and return the updated record."""

        existing = self.get_case(case_id)

        if existing is None:
            raise KeyError(
                f"Case '{case_id}' does not exist."
            )

        self._connection.execute(
            """
            UPDATE cases
            SET
                state = ?,
                updated_at = ?
            WHERE case_id = ?
            """,
            (
                state,
                updated_at.isoformat(),
                case_id,
            ),
        )

        self._connection.commit()

        return CaseRecord(
            case_id=existing.case_id,
            title=existing.title,
            state=state,
            created_at=existing.created_at,
            updated_at=updated_at,
        )

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    def create_job(
        self,
        job_id: str,
        operation: str,
        status: str,
        created_at: datetime,
    ) -> JobRecord:
        """Create and return a job record."""

        record = JobRecord(
            job_id=job_id,
            operation=operation,
            status=status,
            created_at=created_at,
        )

        self._connection.execute(
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
                record.job_id,
                record.operation,
                record.status,
                record.created_at.isoformat(),
            ),
        )

        self._connection.commit()
        return record

    def get_job(
        self,
        job_id: str,
    ) -> Optional[JobRecord]:
        """Retrieve a job by ID."""

        row = self._connection.execute(
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
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
        )

    def update_job_status(
        self,
        job_id: str,
        status: str,
    ) -> JobRecord:
        """Update a job status and return the updated record."""

        existing = self.get_job(job_id)

        if existing is None:
            raise KeyError(
                f"Job '{job_id}' does not exist."
            )

        self._connection.execute(
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

        self._connection.commit()

        return JobRecord(
            job_id=existing.job_id,
            operation=existing.operation,
            status=status,
            created_at=existing.created_at,
        )

    # ------------------------------------------------------------------
    # Audit events
    # ------------------------------------------------------------------

    def create_audit_event(
        self,
        event: AuditEventRecord,
    ) -> AuditEventRecord:
        """Persist and return an audit event."""

        self._connection.execute(
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
                event.timestamp.isoformat(),
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

        self._connection.commit()
        return event

    def get_audit_event(
        self,
        event_id: str,
    ) -> Optional[AuditEventRecord]:
        """Retrieve an audit event by ID."""

        row = self._connection.execute(
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
            timestamp=datetime.fromisoformat(
                row["timestamp"]
            ),
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
    ) -> list[AuditEventRecord]:
        """Return audit events, optionally filtered by job ID."""

        if job_id is None:
            rows = self._connection.execute(
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
            rows = self._connection.execute(
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
                timestamp=datetime.fromisoformat(
                    row["timestamp"]
                ),
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
