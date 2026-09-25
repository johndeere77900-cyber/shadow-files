import {
  parseTelegramUpdate,
  TelegramUpdate,
} from "./telegram";
import { sendTelegramMessage } from "./telegram_api";
import {
  getConversation,
  addConversationTurn,
} from "./conversation";
import {
  generateIntelligentResponse,
} from "./intelligence";
import {
  SHADOW_FILES_SYSTEM_PROMPT,
} from "./intelligence_policy";

export interface WebhookEnv {
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_AUTHORIZED_CHAT_ID: string;
  AI_API_URL: string;
  AI_API_KEY: string;
  AI_MODEL: string;
}

function jsonResponse(
  body: unknown,
  status = 200,
): Response {
  return new Response(
    JSON.stringify(body),
    {
      status,
      headers: {
        "content-type": "application/json",
      },
    },
  );
}

export async function handleTelegramWebhook(
  request: Request,
  env: WebhookEnv,
): Promise<Response> {
  if (request.method !== "POST") {
    return new Response(
      "Method not allowed.",
      { status: 405 },
    );
  }

  let update: TelegramUpdate;

  try {
    update =
      (await request.json()) as TelegramUpdate;
  } catch {
    return new Response(
      "Invalid JSON.",
      { status: 400 },
    );
  }

  const message =
    parseTelegramUpdate(update);

  if (!message) {
    return jsonResponse({
      ok: true,
      ignored: true,
    });
  }

  if (
    !env.TELEGRAM_AUTHORIZED_CHAT_ID ||
    message.chatId !==
      env.TELEGRAM_AUTHORIZED_CHAT_ID
  ) {
    return jsonResponse({
      ok: true,
      ignored: true,
    });
  }

  const conversationId =
    message.chatId;

  addConversationTurn(
    conversationId,
    {
      role: "user",
      content: message.text,
    },
  );

  const history =
    getConversation(conversationId);

  const conversation = [
    {
      role: "system" as const,
      content:
        SHADOW_FILES_SYSTEM_PROMPT,
    },
    ...history,
  ];

  try {
    const result =
      await generateIntelligentResponse(
        env,
        { conversation },
      );

    addConversationTurn(
      conversationId,
      {
        role: "assistant",
        content: result.text,
      },
    );

    await sendTelegramMessage(
      env,
      message.chatId,
      result.text,
    );

    return jsonResponse({
      ok: true,
      responded: true,
    });
  } catch (error) {
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Unknown intelligence error.";

    return jsonResponse(
      {
        ok: false,
        error: errorMessage,
      },
      500,
    );
  }
      }
