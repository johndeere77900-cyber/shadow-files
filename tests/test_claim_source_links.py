"""
Shadow Files persistence tests for claims, sources, and links.

Phase 11 verifies that claims, evidence sources, and claim-evidence
relationships survive database round trips.
"""

import sqlite3
import unittest
from datetime import datetime, timezone

from app.evidence.claims import Claim, ClaimStatus
from app.evidence.links import (
    ClaimEvidenceLink,
    EvidenceRelation,
)
from app.evidence.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
)
from app.evidence.source import EvidenceSource
from app.evidence.claims_repository import ClaimRepository
from app.evidence.links_repository import LinkRepository
from app.evidence.source_repository import SourceRepository
from database.migrations import migrate


class ClaimSourceLinkPersistenceTests(unittest.TestCase):
    """Verify persistent Phase 11 evidence relationships."""

    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )
        migrate(self.connection)

        now = datetime.now(timezone.utc).isoformat()

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
                "CASE-001",
                "Test Case",
                "IDEA",
                now,
                now,
            ),
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def test_claim_round_trip(self) -> None:
        repository = ClaimRepository(
            self.connection
        )

        now = datetime.now(timezone.utc)

        claim = Claim(
            claim_id="CLAIM-001",
            case_id="CASE-001",
            statement="A documented factual claim.",
            status=ClaimStatus.SUPPORTED,
            created_at=now,
            notes="Test claim.",
        )

        repository.create(claim)

        stored = repository.get("CLAIM-001")

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.statement,
            claim.statement,
        )
        self.assertEqual(
            stored.status,
            ClaimStatus.SUPPORTED,
        )

    def test_source_round_trip(self) -> None:
        repository = SourceRepository(
            self.connection
        )

        now = datetime.now(timezone.utc)

        source = EvidenceSource(
            source_id="SOURCE-001",
            name="Example Source",
            url="https://example.com",
            publisher="Example Publisher",
            publication_date=now,
            retrieved_at=now,
        )

        repository.create(source)

        stored = repository.get("SOURCE-001")

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.name,
            source.name,
        )
        self.assertEqual(
            stored.url,
            source.url,
        )
        self.assertEqual(
            stored.publisher,
            source.publisher,
        )

    def test_evidence_round_trip(self) -> None:
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
                "EVIDENCE-001",
                "CASE-001",
                "Documented evidence claim.",
                "Example Source",
                "https://example.com",
                EvidenceType.CREDIBLE_REPORT.value,
                EvidenceStatus.REVIEWED.value,
                datetime.now(
                    timezone.utc
                ).isoformat(),
                None,
                "Reviewed source.",
                "",
            ),
        )
        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT evidence_id, case_id, status
            FROM evidence
            WHERE evidence_id = ?
            """,
            ("EVIDENCE-001",),
        ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(
            row["case_id"],
            "CASE-001",
        )
        self.assertEqual(
            row["status"],
            EvidenceStatus.REVIEWED.value,
        )

    def test_claim_evidence_link_round_trip(self) -> None:
        claim_repository = ClaimRepository(
            self.connection
        )
        link_repository = LinkRepository(
            self.connection
        )

        now = datetime.now(timezone.utc)

        claim_repository.create(
            Claim(
                claim_id="CLAIM-001",
                case_id="CASE-001",
                statement="Documented claim.",
                status=ClaimStatus.SUPPORTED,
                created_at=now,
            )
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
                "EVIDENCE-001",
                "CASE-001",
                "Supporting evidence.",
                "Example Source",
                None,
                EvidenceType.CREDIBLE_REPORT.value,
                EvidenceStatus.VERIFIED.value,
                now.isoformat(),
                None,
                "Verified.",
                "",
            ),
        )
        self.connection.commit()

        link = ClaimEvidenceLink(
            link_id="LINK-001",
            claim_id="CLAIM-001",
            evidence_id="EVIDENCE-001",
            relation=EvidenceRelation.SUPPORTS,
            notes="Direct support.",
        )

        link_repository.create(link)

        stored = link_repository.get("LINK-001")

        self.assertIsNotNone(stored)
        self.assertEqual(
            stored.claim_id,
            "CLAIM-001",
        )
        self.assertEqual(
            stored.evidence_id,
            "EVIDENCE-001",
        )
        self.assertEqual(
            stored.relation,
            EvidenceRelation.SUPPORTS,
        )

    def test_links_can_be_retrieved_by_claim(self) -> None:
        claim_repository = ClaimRepository(
            self.connection
        )
        link_repository = LinkRepository(
            self.connection
        )

        now = datetime.now(timezone.utc)

        claim_repository.create(
            Claim(
                claim_id="CLAIM-001",
                case_id="CASE-001",
                statement="Test claim.",
                status=ClaimStatus.UNREVIEWED,
                created_at=now,
            )
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
                "EVIDENCE-001",
                "CASE-001",
                "Test evidence.",
                "Example Source",
                None,
                EvidenceType.OTHER.value,
                EvidenceStatus.UNREVIEWED.value,
                now.isoformat(),
                None,
                "",
                "",
            ),
        )
        self.connection.commit()

        link_repository.create(
            ClaimEvidenceLink(
                link_id="LINK-001",
                claim_id="CLAIM-001",
                evidence_id="EVIDENCE-001",
                relation=EvidenceRelation.CONTEXTUALIZES,
            )
        )

        links = link_repository.list_for_claim(
            "CLAIM-001"
        )

        self.assertEqual(len(links), 1)
        self.assertEqual(
            links[0].relation,
            EvidenceRelation.CONTEXTUALIZES,
        )

    def test_unknown_claim_cannot_have_link(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
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
                    "LINK-INVALID",
                    "UNKNOWN-CLAIM",
                    "UNKNOWN-EVIDENCE",
                    EvidenceRelation.SUPPORTS.value,
                    "",
                ),
            )


if __name__ == "__main__":
    unittest.main()
