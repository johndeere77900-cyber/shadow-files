"""
Shadow Files case and evidence model tests.

Phase 11 verifies validation and immutability of the application-level
case, identity, evidence, source, claim, and claim-evidence models.
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from app.cases.identity import (
    CaseIdentityError,
    create_case_identity,
)
from app.cases.models import Case
from app.evidence.claims import (
    Claim,
    ClaimStatus,
)
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


class CaseEvidenceModelTests(unittest.TestCase):
    """Verify Phase 11 case and evidence models."""

    def setUp(self) -> None:
        self.now = datetime.now(timezone.utc)

    def test_case_requires_id(self) -> None:
        with self.assertRaises(ValueError):
            Case(
                case_id="",
                title="Test Case",
                state="IDEA",
                created_at=self.now,
                updated_at=self.now,
            )

    def test_case_requires_title(self) -> None:
        with self.assertRaises(ValueError):
            Case(
                case_id="CASE-001",
                title="",
                state="IDEA",
                created_at=self.now,
                updated_at=self.now,
            )

    def test_case_rejects_naive_timestamp(self) -> None:
        naive = datetime.now()

        with self.assertRaises(ValueError):
            Case(
                case_id="CASE-001",
                title="Test Case",
                state="IDEA",
                created_at=naive,
                updated_at=naive,
            )

    def test_case_rejects_invalid_timestamp_order(self) -> None:
        earlier = datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        )
        later = datetime(
            2026,
            1,
            2,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(ValueError):
            Case(
                case_id="CASE-001",
                title="Test Case",
                state="IDEA",
                created_at=later,
                updated_at=earlier,
            )

    def test_case_is_immutable(self) -> None:
        case = Case(
            case_id="CASE-001",
            title="Test Case",
            state="IDEA",
            created_at=self.now,
            updated_at=self.now,
        )

        with self.assertRaises(FrozenInstanceError):
            case.title = "Changed"

    def test_case_identity_normalizes_title(self) -> None:
        identity = create_case_identity(
            " CASE-001 ",
            "  Test   Case   Title ",
        )

        self.assertEqual(
            identity.case_id,
            "CASE-001",
        )
        self.assertEqual(
            identity.canonical_title,
            "Test Case Title",
        )

    def test_case_identity_requires_title(self) -> None:
        with self.assertRaises(CaseIdentityError):
            create_case_identity(
                "CASE-001",
                "",
            )

    def test_evidence_requires_claim(self) -> None:
        with self.assertRaises(ValueError):
            Evidence(
                evidence_id="EVIDENCE-001",
                case_id="CASE-001",
                claim="",
                source_name="Test Source",
                source_url=None,
                evidence_type=EvidenceType.OTHER,
                status=EvidenceStatus.UNREVIEWED,
                retrieved_at=self.now,
            )

    def test_evidence_requires_timezone_aware_retrieval(self) -> None:
        with self.assertRaises(ValueError):
            Evidence(
                evidence_id="EVIDENCE-001",
                case_id="CASE-001",
                claim="Test claim",
                source_name="Test Source",
                source_url=None,
                evidence_type=EvidenceType.OTHER,
                status=EvidenceStatus.UNREVIEWED,
                retrieved_at=datetime.now(),
            )

    def test_evidence_is_immutable(self) -> None:
        evidence = Evidence(
            evidence_id="EVIDENCE-001",
            case_id="CASE-001",
            claim="Test claim",
            source_name="Test Source",
            source_url=None,
            evidence_type=EvidenceType.OTHER,
            status=EvidenceStatus.UNREVIEWED,
            retrieved_at=self.now,
        )

        with self.assertRaises(FrozenInstanceError):
            evidence.status = EvidenceStatus.VERIFIED

    def test_source_requires_id(self) -> None:
        with self.assertRaises(ValueError):
            EvidenceSource(
                source_id="",
                name="Test Source",
                url=None,
                publisher=None,
                publication_date=None,
                retrieved_at=self.now,
            )

    def test_source_is_immutable(self) -> None:
        source = EvidenceSource(
            source_id="SOURCE-001",
            name="Test Source",
            url="https://example.com",
            publisher="Test Publisher",
            publication_date=None,
            retrieved_at=self.now,
        )

        with self.assertRaises(FrozenInstanceError):
            source.name = "Changed"

    def test_claim_requires_statement(self) -> None:
        with self.assertRaises(ValueError):
            Claim(
                claim_id="CLAIM-001",
                case_id="CASE-001",
                statement="",
                status=ClaimStatus.UNREVIEWED,
                created_at=self.now,
            )

    def test_claim_is_immutable(self) -> None:
        claim = Claim(
            claim_id="CLAIM-001",
            case_id="CASE-001",
            statement="Test factual statement.",
            status=ClaimStatus.UNREVIEWED,
            created_at=self.now,
        )

        with self.assertRaises(FrozenInstanceError):
            claim.status = ClaimStatus.SUPPORTED

    def test_claim_evidence_link_requires_claim(self) -> None:
        with self.assertRaises(ValueError):
            ClaimEvidenceLink(
                link_id="LINK-001",
                claim_id="",
                evidence_id="EVIDENCE-001",
                relation=EvidenceRelation.SUPPORTS,
            )

    def test_claim_evidence_link_is_immutable(self) -> None:
        link = ClaimEvidenceLink(
            link_id="LINK-001",
            claim_id="CLAIM-001",
            evidence_id="EVIDENCE-001",
            relation=EvidenceRelation.SUPPORTS,
        )

        with self.assertRaises(FrozenInstanceError):
            link.relation = EvidenceRelation.DISPUTES


if __name__ == "__main__":
    unittest.main()
