"""
Shadow Files claim-evidence link repository.

Phase 11 provides persistent storage for the explicit relationship
between claims and evidence.

A link records whether a piece of evidence supports, disputes, or
contextualizes a claim.
"""

import sqlite3

from app.evidence.links import (
    ClaimEvidenceLink,
    EvidenceRelation,
)


class LinkRepositoryError(Exception):
    """Raised when a claim-evidence link operation fails."""


class LinkRepository:
    """Persist and retrieve claim-evidence relationships."""

    def __init__(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
        self,
        link: ClaimEvidenceLink,
    ) -> None:
        """Create a claim-evidence relationship."""

        try:
            self._connection.execute(
                """
                INSERT INTO claim_evidence_links (
                    link_id,
                    claim_id,
                    evidence_id,
                    relation,
                    notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    link.link_id,
                    link.claim_id,
                    link.evidence_id,
                    link.relation.value,
                    link.notes,
                ),
            )
            self._connection.commit()

        except sqlite3.IntegrityError as exc:
            raise LinkRepositoryError(
                f"Link '{link.link_id}' could not be created."
            ) from exc

    def get(
        self,
        link_id: str,
    ) -> ClaimEvidenceLink | None:
        """Retrieve a claim-evidence link by ID."""

        row = self._connection.execute(
            """
            SELECT
                link_id,
                claim_id,
                evidence_id,
                relation,
                notes
            FROM claim_evidence_links
            WHERE link_id = ?
            """,
            (link_id,),
        ).fetchone()

        if row is None:
            return None

        return ClaimEvidenceLink(
            link_id=row["link_id"],
            claim_id=row["claim_id"],
            evidence_id=row["evidence_id"],
            relation=EvidenceRelation(
                row["relation"]
            ),
            notes=row["notes"],
        )

    def list_for_claim(
        self,
        claim_id: str,
    ) -> list[ClaimEvidenceLink]:
        """Return all evidence relationships for a claim."""

        rows = self._connection.execute(
            """
            SELECT
                link_id,
                claim_id,
                evidence_id,
                relation,
                notes
            FROM claim_evidence_links
            WHERE claim_id = ?
            ORDER BY link_id ASC
            """,
            (claim_id,),
        ).fetchall()

        return [
            ClaimEvidenceLink(
                link_id=row["link_id"],
                claim_id=row["claim_id"],
                evidence_id=row["evidence_id"],
                relation=EvidenceRelation(
                    row["relation"]
                ),
                notes=row["notes"],
            )
            for row in rows
        ]

    def list_for_evidence(
        self,
        evidence_id: str,
    ) -> list[ClaimEvidenceLink]:
        """Return all claim relationships for evidence."""

        rows = self._connection.execute(
            """
            SELECT
                link_id,
                claim_id,
                evidence_id,
                relation,
                notes
            FROM claim_evidence_links
            WHERE evidence_id = ?
            ORDER BY link_id ASC
            """,
            (evidence_id,),
        ).fetchall()

        return [
            ClaimEvidenceLink(
                link_id=row["link_id"],
                claim_id=row["claim_id"],
                evidence_id=row["evidence_id"],
                relation=EvidenceRelation(
                    row["relation"]
                ),
                notes=row["notes"],
            )
            for row in rows
              ]
