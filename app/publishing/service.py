"""
Publication service for Shadow Files.

This service coordinates validation, approval, state transitions,
event recording, and optional automated YouTube publishing.

It does not silently publish content. Explicit approval is required
before any external publishing operation.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .approval import create_approval_record, require_approved_publication
from .errors import (
    PublicationApprovalError,
    PublicationValidationError,
    UploadError,
)
from .events import PublicationEventRepository
from .models import (
    Publication,
    PublicationMode,
    PublicationPackage,
)
from .package import require_valid_publication_package
from .repository import PublicationRepository
from .status import PublicationStatus
from .youtube import (
    YouTubePublisher,
    YouTubeUploadRequest,
)


class PublicationService:
    """Application service for controlled publication workflows."""

    def __init__(
        self,
        repository: PublicationRepository,
        event_repository: PublicationEventRepository,
        youtube_publisher: Optional[YouTubePublisher] = None,
    ) -> None:
        self.repository = repository
        self.event_repository = event_repository
        self.youtube_publisher = youtube_publisher

    def create_publication(
        self,
        *,
        production_id: str,
        package: PublicationPackage,
        mode: PublicationMode = PublicationMode.HUMAN,
    ) -> Publication:
        """
        Create a publication in NOT_STARTED state.

        The package must contain the complete required metadata.
        File existence is checked at this stage because a publication
        package should not enter the workflow with missing assets.
        """

        require_valid_publication_package(
            package,
            check_files=True,
        )

        now = datetime.now(timezone.utc)

        publication = Publication(
            publication_id=str(uuid4()),
            production_id=production_id,
            mode=mode,
            status=PublicationStatus.NOT_STARTED,
            package=package,
            created_at=now,
            updated_at=now,
        )

        self.repository.create(publication)

        self.event_repository.record(
            publication_id=publication.publication_id,
            event_type="PUBLICATION_CREATED",
            status=publication.status.value,
            actor="system",
        )

        return publication

    def prepare_package(
        self,
        publication_id: str,
    ) -> Publication:
        """
        Validate a publication package and move it to PACKAGE_READY.
        """

        publication = self._require_publication(publication_id)

        require_valid_publication_package(
            publication.package,
            check_files=True,
        )

        updated = self._transition(
            publication_id,
            PublicationStatus.PACKAGE_READY,
            actor="system",
            event_type="PACKAGE_READY",
        )

        return updated

    def request_approval(
        self,
        publication_id: str,
        *,
        actor: str = "system",
    ) -> Publication:
        """
        Move a prepared publication into approval review.
        """

        publication = self._require_publication(publication_id)

        if publication.status != PublicationStatus.PACKAGE_READY:
            raise PublicationApprovalError(
                "Only a PACKAGE_READY publication can request approval."
            )

        return self._transition(
            publication_id,
            PublicationStatus.PENDING_APPROVAL,
            actor=actor,
            event_type="APPROVAL_REQUESTED",
        )

    def approve(
        self,
        publication_id: str,
        *,
        approved_by: str,
        note: Optional[str] = None,
    ) -> Publication:
        """
        Explicitly approve a publication.

        Approval is a deliberate human decision and is recorded as
        an audit event.
        """

        publication = self._require_publication(publication_id)

        approval = create_approval_record(
            publication,
            approved_by=approved_by,
            note=note,
        )

        updated = self._transition(
            publication_id,
            PublicationStatus.APPROVED,
            actor=approved_by,
            event_type="PUBLICATION_APPROVED",
            details=note,
        )

        self.repository.update_metadata(
            publication_id,
            approved_at=approval.approved_at,
            updated_at=approval.approved_at,
        )

        self.event_repository.record(
            publication_id=publication_id,
            event_type="APPROVAL_RECORDED",
            status=PublicationStatus.APPROVED.value,
            actor=approved_by,
            details=note,
            created_at=approval.approved_at,
        )

        return self._require_publication(publication_id)

    def begin_upload(
        self,
        publication_id: str,
        *,
        actor: str = "system",
    ) -> Publication:
        """
        Move an approved publication into UPLOADING.

        This does not perform the upload itself.
        """

        publication = self._require_publication(publication_id)

        require_approved_publication(publication)

        return self._transition(
            publication_id,
            PublicationStatus.UPLOADING,
            actor=actor,
            event_type="UPLOAD_STARTED",
        )

    def upload(
        self,
        publication_id: str,
        *,
        actor: str = "system",
    ) -> Publication:
        """
        Upload an approved publication through the configured
        YouTube provider.

        Human-mode publications intentionally do not perform an
        automated upload.
        """

        publication = self._require_publication(publication_id)

        require_approved_publication(publication)

        if publication.mode == PublicationMode.HUMAN:
            raise PublicationValidationError(
                "Human publication mode requires manual YouTube "
                "publication; automated upload was not requested."
            )

        if self.youtube_publisher is None:
            raise UploadError(
                "No automated YouTube publisher is configured."
            )

        if publication.status != PublicationStatus.APPROVED:
            raise PublicationApprovalError(
                "Publication must be APPROVED before upload."
            )

        self.begin_upload(
            publication_id,
            actor=actor,
        )

        try:
            result = self.youtube_publisher.upload(
                YouTubeUploadRequest(
                    video_location=publication.package.video_location,
                    title=publication.package.title,
                    description=publication.package.description,
                    tags=publication.package.tags,
                    category_id=publication.package.category_id,
                    thumbnail_location=(
                        publication.package.thumbnail_location
                    ),
                )
            )
        except Exception as exc:
            now = datetime.now(timezone.utc)

            self.repository.update_metadata(
                publication_id,
                error_message=str(exc),
                updated_at=now,
            )

            self._transition(
                publication_id,
                PublicationStatus.FAILED,
                actor=actor,
                event_type="UPLOAD_FAILED",
                details=str(exc),
            )

            raise UploadError(
                f"YouTube upload failed: {exc}"
            ) from exc

        if not result.success or not result.video_id:
            message = (
                result.error_message
                or "YouTube publisher returned an unsuccessful result."
            )

            now = datetime.now(timezone.utc)

            self.repository.update_metadata(
                publication_id,
                error_message=message,
                updated_at=now,
            )

            self._transition(
                publication_id,
                PublicationStatus.FAILED,
                actor=actor,
                event_type="UPLOAD_FAILED",
                details=message,
            )

            raise UploadError(message)

        uploaded_at = (
            result.uploaded_at
            or datetime.now(timezone.utc)
        )

        self.repository.update_metadata(
            publication_id,
            uploaded_at=uploaded_at,
            youtube_video_id=result.video_id,
            youtube_url=result.video_url,
            error_message=None,
            updated_at=uploaded_at,
        )

        updated = self._transition(
            publication_id,
            PublicationStatus.UPLOADED,
            actor=actor,
            event_type="UPLOAD_COMPLETED",
        )

        return updated

    def mark_human_uploaded(
        self,
        publication_id: str,
        *,
        youtube_video_id: Optional[str] = None,
        youtube_url: Optional[str] = None,
        actor: str = "human",
    ) -> Publication:
        """
        Record that a human completed the YouTube upload.

        This is the manual-publication path and does not require the
        YouTube API provider.
        """

        publication = self._require_publication(publication_id)

        require_approved_publication(publication)

        if publication.mode != PublicationMode.HUMAN:
            raise PublicationValidationError(
                "mark_human_uploaded is only valid for HUMAN mode."
            )

        now = datetime.now(timezone.utc)

        self._transition(
            publication_id,
            PublicationStatus.UPLOADING,
            actor=actor,
            event_type="HUMAN_UPLOAD_STARTED",
            details=None,
        )

        self.repository.update_metadata(
            publication_id,
            uploaded_at=now,
            youtube_video_id=youtube_video_id,
            youtube_url=youtube_url,
            updated_at=now,
        )

        return self._transition(
            publication_id,
            PublicationStatus.UPLOADED,
            actor=actor,
            event_type="HUMAN_UPLOAD_RECORDED",
        )

    def mark_scheduled(
        self,
        publication_id: str,
        *,
        scheduled_at: datetime,
        actor: str = "system",
    ) -> Publication:
        """Record a scheduled YouTube publication."""

        if scheduled_at.tzinfo is None:
            raise ValueError(
                "scheduled_at must be timezone-aware"
            )

        publication = self._require_publication(publication_id)

        if publication.status != PublicationStatus.UPLOADED:
            raise PublicationValidationError(
                "Only an UPLOADED publication can be scheduled."
            )

        now = datetime.now(timezone.utc)

        self.repository.update_metadata(
            publication_id,
            scheduled_at=scheduled_at,
            updated_at=now,
        )

        return self._transition(
            publication_id,
            PublicationStatus.SCHEDULED,
            actor=actor,
            event_type="PUBLICATION_SCHEDULED",
            details=scheduled_at.isoformat(),
        )

    def mark_published(
        self,
        publication_id: str,
        *,
        actor: str = "system",
    ) -> Publication:
        """Record that the episode has become publicly available."""

        publication = self._require_publication(publication_id)

        if publication.status not in {
            PublicationStatus.UPLOADED,
            PublicationStatus.SCHEDULED,
        }:
            raise PublicationValidationError(
                "Only an UPLOADED or SCHEDULED publication can "
                "be marked PUBLISHED."
            )

        now = datetime.now(timezone.utc)

        self.repository.update_metadata(
            publication_id,
            published_at=now,
            updated_at=now,
        )

        return self._transition(
            publication_id,
            PublicationStatus.PUBLISHED,
            actor=actor,
            event_type="PUBLICATION_COMPLETED",
        )

    def get(
        self,
        publication_id: str,
    ) -> Optional[Publication]:
        """Return a publication by ID."""

        return self.repository.get(publication_id)

    def _require_publication(
        self,
        publication_id: str,
    ) -> Publication:
        publication = self.repository.get(publication_id)

        if publication is None:
            raise ValueError(
                f"Publication not found: {publication_id}"
            )

        return publication

    def _transition(
        self,
        publication_id: str,
        target_status: PublicationStatus,
        *,
        actor: str,
        event_type: str,
        details: Optional[str] = None,
    ) -> Publication:
        now = datetime.now(timezone.utc)

        updated = self.repository.update_status(
            publication_id,
            target_status,
            now,
        )

        self.event_repository.record(
            publication_id=publication_id,
            event_type=event_type,
            status=target_status.value,
            actor=actor,
            details=details,
            created_at=now,
        )

        return updated
