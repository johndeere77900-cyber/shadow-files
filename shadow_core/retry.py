"""
Shadow Files retry foundation.

Retries are controlled explicitly so failed external operations do not
run indefinitely or silently duplicate work.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """
    Defines how many attempts an operation may make.
    """

    max_attempts: int = 3
    base_delay_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        if self.base_delay_seconds < 0:
            raise ValueError(
                "base_delay_seconds cannot be negative."
            )


def should_retry(
    attempt: int,
    policy: RetryPolicy,
) -> bool:
    """
    Return True when another attempt is permitted.

    Attempt numbers are zero-based:
        0 = first attempt
        1 = second attempt
        2 = third attempt
    """

    if attempt < 0:
        raise ValueError("attempt cannot be negative.")

    return attempt < policy.max_attempts
