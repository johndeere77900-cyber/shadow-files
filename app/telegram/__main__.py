"""
Shadow Files Telegram runtime entry point.

This module starts the configured Telegram transport, authorizes
incoming messages, and passes authorized commands into the existing
Shadow Files command service.

Telegram remains an interface layer. Business execution stays inside
the application's controlled command pipeline.
"""

from app.application import build_command_service
from app.telegram.config import TelegramConfig
from app.telegram.messages import OutgoingMessage
from app.telegram.router import TelegramRouter
from app.telegram.transport import TelegramBotTransport
from shadow_core.authorization import Actor


def _response_text(response) -> str:
    """
    Convert a command-service response into a concise Telegram message.
    """

    if not response.success:
        return (
            f"Shadow Files command failed: "
            f"{response.message}"
        )

    result = response.result

    if result is None:
        return response.message

    lines = [
        response.message,
        f"Command: {result.command.command_type.value}",
    ]

    if result.dispatch is not None:
        data = result.dispatch.data

        if hasattr(data, "result_count"):
            lines.append(
                f"Research results: {data.result_count}"
            )

    return "\n".join(lines)


def main() -> None:
    """Start the Telegram interface."""

    config = TelegramConfig.from_env()

    if not config.enabled:
        print(
            "Shadow Files Telegram interface is disabled."
        )
        return

    if not config.bot_token:
        raise RuntimeError(
            "SHADOW_TELEGRAM_BOT_TOKEN is required "
            "when Telegram is enabled."
        )

    if not config.authorized_chat_id:
        raise RuntimeError(
            "SHADOW_TELEGRAM_AUTHORIZED_CHAT_ID is required "
            "when Telegram is enabled."
        )

    transport = TelegramBotTransport(
        bot_token=config.bot_token,
    )

    router = TelegramRouter(
        authorized_chat_id=config.authorized_chat_id,
    )

    command_service = build_command_service()

    messages = transport.receive()

    for message in messages:
        try:
            route = router.route(message)

            actor = Actor(
                actor_id=route.actor.user_id,
                role="operator",
            )

            response = command_service.execute(
                actor=actor,
                text=route.message.text,
            )

            transport.send(
                OutgoingMessage(
                    chat_id=route.message.chat_id,
                    text=_response_text(response),
                    reply_to_message_id=(
                        route.message.message_id
                    ),
                )
            )

        except Exception as exc:
            transport.send(
                OutgoingMessage(
                    chat_id=message.chat_id,
                    text=(
                        "Shadow Files could not process "
                        f"this request: {exc}"
                    ),
                    reply_to_message_id=message.message_id,
                )
            )


if __name__ == "__main__":
    main()
