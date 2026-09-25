"""
Shadow Files production service.

Coordinates production lifecycle operations while enforcing explicit
status transitions and keeping external providers behind interfaces.
"""

from datetime import datetime, timezone
from typing import Optional

from app.production.models import (
    ContentType,
    Production,
    ProductionStatus,
)
from app.production.repository import ProductionRepository
from app.production.status import validate_transition


class ProductionService:
    """Application service for controlled production workflows."""

    def __init__(
        self,
        repository: ProductionRepository,
    ) -> None:
        self.repository = repository

    def create_production(
        self,
        production_id: str,
        case_id: str,
        investigation_id: str,
        title: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        notes: str = "",
    ) -> Production:
        """Create a new production in NOT_STARTED state."""

        now = datetime.now(timezone.utc)

        production = Production(
            production_id=production_id,
            case_id=case_id,
            investigation_id=investigation_id,
            status=ProductionStatus.NOT_STARTED,
            created_at=now,
            updated_at=now,
            title=title,
            content_type=content_type,
            notes=notes,
        )

        self.repository.create(production)

        return production

    def get_production(
        self,
        production_id: str,
    ) -> Optional[Production]:
        """Retrieve a production by ID."""

        return self.repository.get(production_id)

    def transition(
        self,
        production_id: str,
        target_status: ProductionStatus,
    ) -> Production:
        """
        Move a production to an explicitly permitted next state.
        """

        production = self.repository.get(production_id)

        if production is None:
            raise KeyError(
                f"Production not found: {production_id}"
            )

        validate_transition(
            production.status,
            target_status,
        )

        return self.repository.update_status(
            production_id=production_id,
            status=target_status,
            updated_at=datetime.now(timezone.utc),
        )

    def start_story_planning(
        self,
        production_id: str,
    ) -> Production:
        """Begin story planning."""

        return self.transition(
            production_id,
            ProductionStatus.STORY_PLANNING,
        )

    def start_script_draft(
        self,
        production_id: str,
    ) -> Production:
        """Move an approved story into script drafting."""

        return self.transition(
            production_id,
            ProductionStatus.SCRIPT_DRAFT,
        )

    def submit_script_for_review(
        self,
        production_id: str,
    ) -> Production:
        """Submit a script for review."""

        return self.transition(
            production_id,
            ProductionStatus.SCRIPT_REVIEW,
        )

    def approve_script(
        self,
        production_id: str,
    ) -> Production:
        """Approve the current script."""

        return self.transition(
            production_id,
            ProductionStatus.SCRIPT_APPROVED,
        )

    def start_scene_planning(
        self,
        production_id: str,
    ) -> Production:
        """Begin scene planning."""

        return self.transition(
            production_id,
            ProductionStatus.SCENE_PLANNING,
        )

    def start_production(
        self,
        production_id: str,
    ) -> Production:
        """Begin media/render production."""

        return self.transition(
            production_id,
            ProductionStatus.PRODUCTION,
        )

    def submit_for_qc(
        self,
        production_id: str,
    ) -> Production:
        """Submit the production for quality control."""

        return self.transition(
            production_id,
            ProductionStatus.QC,
        )

    def submit_for_human_approval(
        self,
        production_id: str,
    ) -> Production:
        """Submit a QC-passed production for human approval."""

        return self.transition(
            production_id,
            ProductionStatus.HUMAN_APPROVAL,
        )

    def mark_ready(
        self,
        production_id: str,
    ) -> Production:
        """Mark a human-approved production as ready."""

        return self.transition(
            production_id,
            ProductionStatus.READY,
        )

    def block(
        self,
        production_id: str,
    ) -> Production:
        """Block a production requiring intervention."""

        return self.transition(
            production_id,
            ProductionStatus.BLOCKED,
        )

    def pause(
        self,
        production_id: str,
    ) -> Production:
        """Pause a production."""

        return self.transition(
            production_id,
            ProductionStatus.PAUSED,
        )

    def cancel(
        self,
        production_id: str,
    ) -> Production:
        """Cancel a production."""

        return self.transition(
            production_id,
            ProductionStatus.CANCELLED,
      )
