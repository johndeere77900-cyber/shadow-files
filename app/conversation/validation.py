"""
Shadow Files intent validation.

Parsing identifies what a message appears to mean.
Validation determines whether the interpreted intent contains enough
information to be safely passed to the command layer.

Validation does not execute the requested operation.
"""

from dataclasses import dataclass

from app.conversation.intents import (
    Intent,
    IntentType,
)


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a parsed intent."""

    valid: bool
    intent: Intent
    reason: str = ""


class IntentValidator:
    """Validate parsed intents before command execution."""

    def validate(
        self,
        intent: Intent,
    ) -> ValidationResult:
        """Validate an intent without executing it."""

        if intent.intent_type == IntentType.UNKNOWN:
            return ValidationResult(
                valid=False,
                intent=intent,
                reason="The request could not be understood.",
            )

        if not intent.raw_text.strip():
            return ValidationResult(
                valid=False,
                intent=intent,
                reason="The request is empty.",
            )

        if not isinstance(
            intent.intent_type,
            IntentType,
        ):
            return ValidationResult(
                valid=False,
                intent=intent,
                reason="The intent type is invalid.",
            )

        if not 0.0 <= intent.confidence <= 1.0:
            return ValidationResult(
                valid=False,
                intent=intent,
                reason="Intent confidence must be between 0 and 1.",
            )

        return ValidationResult(
            valid=True,
            intent=intent,
          )
