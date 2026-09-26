"""
Shadow Files conversational intent parser.

This is the deterministic foundation for natural-language commands.
It identifies clearly recognized requests without executing them.

Research requests preserve the user's research instruction and may
carry an explicitly supplied case_id into the controlled command layer.
Case identity is never inferred or invented.
"""

import re

from app.conversation.intents import (
    Intent,
    IntentType,
)


class IntentParser:
    """Convert supported natural-language requests into intents."""

    def parse(self, text: str) -> Intent:
        """Parse a user message into a structured intent."""

        normalized = text.strip().lower()

        if not normalized:
            return Intent(
                intent_type=IntentType.UNKNOWN,
                raw_text=text,
                confidence=0.0,
            )

        if self._matches(
            normalized,
            r"\bhow\s+are\s+we\s+doing\b",
        ):
            return Intent(
                intent_type=IntentType.STATUS,
                raw_text=text,
            )

        if self._matches(
            normalized,
            r"\bwhat(?:'s| is)\s+holding\s+up\b",
        ):
            return Intent(
                intent_type=IntentType.CASE_STATUS,
                raw_text=text,
            )

        if self._matches(
            normalized,
            r"\bcontinue\b.*\bcase\b",
        ):
            return Intent(
                intent_type=IntentType.CONTINUE_CASE,
                raw_text=text,
            )

        if self._matches(
            normalized,
            r"\bmove\b.*\b(?:next|this)\s+(?:tuesday|week)\b",
        ):
            return Intent(
                intent_type=IntentType.SCHEDULE_CHANGE,
                raw_text=text,
            )

        research_match = re.search(
            r"\bresearch\b(?P<target>.*)",
            normalized,
            flags=re.IGNORECASE,
        )

        if research_match:
            target = (
                research_match.group("target")
                .strip(" \t\n:,-")
            )

            case_id = None

            case_match = re.search(
                r"\bcase_id\s*=\s*([A-Za-z0-9._:-]+)\b",
                target,
                flags=re.IGNORECASE,
            )

            if case_match:
                case_id = case_match.group(1).strip()

                target = (
                    target[:case_match.start()]
                    + target[case_match.end():]
                ).strip(" \t\n:,-")

            if re.fullmatch(
                r"(?:this|the)\s+case\.?",
                target,
                flags=re.IGNORECASE,
            ):
                target = ""

            parameters = ()

            if case_id:
                parameters = (
                    ("case_id", case_id),
                )

            return Intent(
                intent_type=IntentType.RESEARCH,
                raw_text=text,
                target=target or None,
                parameters=parameters,
            )

        if self._matches(
            normalized,
            r"\banalyze\b",
        ):
            return Intent(
                intent_type=IntentType.ANALYZE,
                raw_text=text,
            )

        if self._matches(
            normalized,
            r"\bshow\b.*\bschedule\b",
        ):
            return Intent(
                intent_type=IntentType.SHOW_SCHEDULE,
                raw_text=text,
            )

        if self._matches(
            normalized,
            r"\bhelp\b",
        ):
            return Intent(
                intent_type=IntentType.HELP,
                raw_text=text,
            )

        return Intent(
            intent_type=IntentType.UNKNOWN,
            raw_text=text,
            confidence=0.0,
        )

    @staticmethod
    def _matches(
        text: str,
        pattern: str,
    ) -> bool:
        return re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ) is not None
