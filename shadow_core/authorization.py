"""
Shadow Files authorization foundation.

Authorization is kept separate from the conversational layer so that
natural-language commands cannot bypass permission checks.
"""

from dataclasses import dataclass


class AuthorizationError(Exception):
    """Raised when an actor is not authorized for an action."""


@dataclass(frozen=True)
class Actor:
    """
    Identity and role of the person or system requesting an action.
    """

    actor_id: str
    role: str


def require_role(
    actor: Actor,
    *allowed_roles: str,
) -> None:
    """
    Require the actor to have one of the permitted roles.

    Raises AuthorizationError when access is not permitted.
    """

    if actor.role not in allowed_roles:
        raise AuthorizationError(
            f"Role '{actor.role}' is not authorized for this action."
        )
