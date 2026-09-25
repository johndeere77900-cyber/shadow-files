import {
  handleTelegramWebhook,
} from "./webhook";

export interface Env {
  SHADOW_FILES_MODE: string;

  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_AUTHORIZED_CHAT_ID: string;

  AI_API_URL: string;
  AI_API_KEY: string;
  AI_MODEL: string;
}

export default {
  async fetch(
    request: Request,
    env: Env,
  ): Promise<Response> {
    const url = new URL(request.url);

    if (
      request.method === "GET" &&
      url.pathname === "/"
    ) {
      return new Response(
        JSON.stringify({
          ok: true,
          service:
            "Shadow Files Cloudflare Control",
          mode: env.SHADOW_FILES_MODE,
          status: "online",
        }),
        {
          status: 200,
          headers: {
            "content-type":
              "application/json",
          },
        },
      );
    }

    if (
      url.pathname ===
      "/telegram/webhook"
    ) {
      return handleTelegramWebhook(
        request,
        env,
      );
    }

    return new Response(
      JSON.stringify({
        ok: false,
        error: "Not found.",
      }),
      {
        status: 404,
        headers: {
          "content-type":
            "application/json",
        },
      },
    );
  },
};
