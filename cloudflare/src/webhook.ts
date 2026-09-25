import {
  parseTelegramUpdate,
  TelegramUpdate,
} from "./telegram";
import { sendTelegramMessage } from "./telegram_api";

export interface WebhookEnv {
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_AUTHORIZED_CHAT_ID: string;
}

export async function handleTelegramWebhook(
  request: Request,
  env: WebhookEnv,
): Promise<Response> {
  if (request.method !== "POST") {
    return new Response("Method not allowed.", {
      status: 405,
    });
  }

  let update: TelegramUpdate;

  try {
    update = (await request.json()) as TelegramUpdate;
  } catch {
    return new Response("Invalid JSON.", {
      status: 400,
    });
  }

  const message = parseTelegramUpdate(update);

  if (!message) {
    return new Response(
      JSON.stringify({ ok: true, ignored: true }),
      {
        status: 200,
        headers: {
          "content-type": "application/json",
        },
      },
    );
  }

  if (
    !env.TELEGRAM_AUTHORIZED_CHAT_ID ||
    message.chatId !== env.TELEGRAM_AUTHORIZED_CHAT_ID
  ) {
    return new Response(
      JSON.stringify({ ok: true, ignored: true }),
      {
        status: 200,
        headers: {
          "content-type": "application/json",
        },
      },
    );
  }

  await sendTelegramMessage(
    env,
    message.chatId,
    `Shadow Files received: ${message.text}`,
  );

  return new Response(
    JSON.stringify({ ok: true }),
    {
      status: 200,
      headers: {
        "content-type": "application/json",
      },
    },
  );
}
