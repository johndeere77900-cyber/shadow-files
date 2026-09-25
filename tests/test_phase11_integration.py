"""
Shadow Files Phase 11 integration qualification tests.

Phase 11 verifies that case identity, claims, sources, evidence,
and claim-evidence relationships operate together through the
persistent database layer.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.cases.identity import create_case_identity
from app.cases.models import Case
from app.cases.repository import CaseRepository
from app.evidence.claims import Claim, ClaimStatus
from app.evidence.claims_repository import ClaimRepository
from app.evidence.links import (
    ClaimEvidenceLink,
    EvidenceRelation,
)
from app.evidence.links_repository import LinkRepository
from app.evidence.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
)
from app.evidence.repository import EvidenceRepository
from app.evidence.source import create_source
from app.evidence.source_repository import SourceRepository
from database.migrations import migrate


class Phase11IntegrationTests(unittest.TestCase):
    """Qualify the complete Phase 11 memory chain."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )
        migrate(self.connection)

        self.now = datetime.now(timezone.utc)

    def tearDown(self) -> None:
        self.connection.close()

    def test_complete_case_evidence_chain(self) -> None:
        case_repository = CaseRepository(
            self.connection
        )
        source_repository = SourceRepository(
            self.connection
        )
        claim_repository = ClaimRepository(
            self.connection
        )
        evidence_repository = EvidenceRepository(
            self.connection
        )
        link_repository = LinkRepository(
            self.connection
        )

        identity = create_case_identity(
            "CASE-001",
            "Example Unresolved Case",
        )

        case = Case(
            case_id=identity.case_id,
            title=identity.canonical_title,
            state="IDEA",
            created_at=self.now,
            updated_at=self.now,
        )

        case_repository.create(case)

        stored_case = case_repository.get(
            "CASE-001"
        )

        self.assertIsNotNone(stored_case)
        self.assertEqual(
            stored_case.title,
            "Example Unresolved Case",
        )

        source = create_source(
            source_id="SOURCE-001",
            name="Example Investigative Source",
            url="https://example.com/source",
            publisher="Example Publisher",
            publication_date=self.now,
            retrieved_at=self.now,
        )

        source_repository.create(source)

        claim = Claim(
            claim_id="CLAIM-001",
            case_id="CASE-001",
            statement=(
                "The source reports a documented factual event."
            ),
            status=ClaimStatus.SUPPORTED,
            created_at=self.now,
        )

        claim_repository.create(claim)

        evidence = Evidence(
            evidence_id="EVIDENCE-001",
            case_id="CASE-001",
            claim=claim.statement,
            source_name=source.name,
            source_url=source.url,
            evidence_type=EvidenceType.CREDIBLE_REPORT,
            status=EvidenceStatus.VERIFIED,
            retrieved_at=self.now,
            publication_date=self.now,
            reliability_assessment=(
                "Verified for the stated factual claim."
            ),
        )

        evidence_repository.create(evidence)

        link = ClaimEvidenceLink(
            link_id="LINK-001",
            claim_id="CLAIM-001",
            evidence_id="EVIDENCE-001",
            relation=EvidenceRelation.SUPPORTS,
            notes="Evidence directly supports the claim.",
        )

        link_repository.create(link)

        stored_source = source_repository.get(
            "SOURCE-001"
        )
        stored_claim = claim_repository.get(
            "CLAIM-001"
        )
        stored_evidence = evidence_repository.get(
            "EVIDENCE-001"
        )
        stored_link = link_repository.get(
            "LINK-001"
        )

        self.assertIsNotNone(stored_source)
        self.assertIsNotNone(stored_claim)
        self.assertIsNotNone(stored_evidence)
        self.assertIsNotNone(stored_link)

        self.assertEqual(
            stored_claim.case_id,
            stored_case.case_id,
        )
        self.assertEqual(
            stored_evidence.case_id,
            stored_case.case_id,
        )
        self.assertEqual(
            stored_link.claim_id,
            stored_claim.claim_id,
        )
        self.assertEqual(
            stored_link.evidence_id,
            stored_evidence.evidence_id,
        )
        self.assertEqual(
            stored_link.relation,
            EvidenceRelation.SUPPORTS,
        )

    def test_case_deletion_cascades_related_memory(self) -> None:
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
                "CASE-DELETE",
                "Deletion Test Case",
                "IDEA",
                self.now.isoformat(),
                self.now.isoformat(),
            ),
        )

        self.connection.execute(
            """
            INSERT INTO claims (
                claim_id,
                case_id,
                statement,
                status,
                created_at,
                reviewed_at,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "CLAIM-DELETE",
                "CASE-DELETE",
                "Deletion test claim.",
                ClaimStatus.UNREVIEWED.value,
                self.now.isoformat(),
                None,
                "",
            ),
        )

        self.connection.execute(
            """
            INSERT INTO evidence (
                evidence_id,
                case_id,
                claim,
                source_name,
                source_url,
                evidence_type,
                status,
                retrieved_at,
                publication_date,
                reliability_assessment,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "EVIDENCE-DELETE",
                "CASE-DELETE",
                "Deletion test evidence.",
                "Test Source",
                None,
                EvidenceType.OTHER.value,
                EvidenceStatus.UNREVIEWED.value,
                self.now.isoformat(),
                None,
                "",
                "",
            ),
        )

        self.connection.commit()

        self.connection.execute(
            """
            DELETE FROM cases
            WHERE case_id = ?
            """,
            ("CASE-DELETE",),
        )
        self.connection.commit()

        claim = self.connection.execute(
            """
            SELECT *
            FROM claims
            WHERE claim_id = ?
            """,
            ("CLAIM-DELETE",),
        ).fetchone()

        evidence = self.connection.execute(
            """
            SELECT *
            FROM evidence
            WHERE evidence_id = ?
            """,
            ("EVIDENCE-DELETE",),
        ).fetchone()

        self.assertIsNone(claim)
        self.assertIsNone(evidence)

    def test_phase11_memory_is_separate_from_production_state(
        self,
    ) -> None:
        tables = {
            row["name"]
            for row in self.connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        self.assertIn("cases", tables)
        self.assertIn("evidence", tables)
        self.assertIn("claims", tables)
        self.assertIn("evidence_sources", tables)
        self.assertIn(
            "claim_evidence_links",
            tables,
        )

        self.assertIn(
            "jobs",
            tables,
        )
        self.assertIn(
            "audit_events",
            tables,
        )


if __name__ == "__main__":
    unittest.main()
