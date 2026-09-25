export interface TelegramApiEnv {
  TELEGRAM_BOT_TOKEN: string;
}

interface TelegramApiResponse {
  ok: boolean;
  description?: string;
}

export async function sendTelegramMessage(
  env: TelegramApiEnv,
  chatId: string,
  text: string,
): Promise<void> {
  if (!env.TELEGRAM_BOT_TOKEN) {
    throw new Error("TELEGRAM_BOT_TOKEN is not configured.");
  }

  const response = await fetch(
    `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        chat_id: chatId,
        text,
      }),
    },
  );

  const result =
    (await response.json()) as TelegramApiResponse;

  if (!response.ok || !result.ok) {
    throw new Error(
      result.description ??
        `Telegram API request failed with status ${response.status}.`,
    );
  }
      }
