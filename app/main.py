"""
Shadow Files application entry point.

This module provides the top-level executable entry point for running
a controlled Shadow Files command.

Execution path:

CLI input
    -> application composition
    -> CommandService
    -> CommandPipeline
    -> conversation parsing
    -> command validation
    -> authorization
    -> command dispatch
    -> registered business handler
"""

import argparse
import sys

from app.application import build_command_service
from shadow_core.authorization import Actor


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="shadow-files",
        description="Run a controlled Shadow Files command.",
    )

    parser.add_argument(
        "--actor-id",
        required=True,
        help="Identity of the person or system issuing the command.",
    )

    parser.add_argument(
        "--role",
        required=True,
        help="Authorization role of the actor.",
    )

    parser.add_argument(
        "command",
        nargs="+",
        help="Natural-language Shadow Files command to execute.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Execute one Shadow Files command through the configured application.

    Returns:
        0 = successful execution
        1 = command rejected or failed
    """

    parser = build_parser()
    args = parser.parse_args(argv)

    actor = Actor(
        actor_id=args.actor_id,
        role=args.role,
    )

    command_text = " ".join(args.command)

    service = build_command_service()

    response = service.execute(
        actor,
        command_text,
    )

    if response.success:
        print(response.message)

        if response.result is not None:
            print(
                f"Command: "
                f"{response.result.command.command_type.value}"
            )

            if response.result.dispatch is not None:
                data = response.result.dispatch.data

                if hasattr(data, "result_count"):
                    print(
                        f"Research results: "
                        f"{data.result_count}"
                    )

        return 0

    print(
        f"Shadow Files command failed: {response.message}",
        file=sys.stderr,
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
