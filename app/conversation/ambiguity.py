"""
Shadow Files ambiguity handling.

Natural-language requests can be understandable but still lack enough
information for safe execution.

This module identifies intents that require clarification before the
command layer is allowed to act.
"""

from dataclasses import dataclass

from app.conversation.intents import (
    Intent,
    IntentType,
)


@dataclass(frozen=True)
class AmbiguityResult:
    """Result of checking an intent for execution ambiguity."""

    ambiguous: bool
    intent: Intent
    question: str = ""


class AmbiguityChecker:
    """Check whether a valid intent needs clarification."""

    def check(
        self,
        intent: Intent,
    ) -> AmbiguityResult:
        """Return whether the intent requires clarification."""

        if intent.intent_type == IntentType.UNKNOWN:
            return AmbiguityResult(
                ambiguous=True,
                intent=intent,
                question="What would you like Shadow Files to do?",
            )

        if intent.intent_type == IntentType.CONTINUE_CASE:
            if not intent.target:
                return AmbiguityResult(
                    ambiguous=True,
                    intent=intent,
                    question=(
                        "Which case would you like me to continue?"
                    ),
                )

        if intent.intent_type == IntentType.SCHEDULE_CHANGE:
            if not intent.parameters:
                return AmbiguityResult(
                    ambiguous=True,
                    intent=intent,
                    question=(
                        "Which video should be moved, and to "
                        "what date and time?"
                    ),
                )

        return AmbiguityResult(
            ambiguous=False,
            intent=intent,
                )
