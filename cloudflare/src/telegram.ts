export interface TelegramMessage {
  message_id: number;
  chat: {
    id: number;
  };
  from?: {
    id: number;
  };
  text?: string;
}

export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
}

export interface NormalizedTelegramMessage {
  messageId: string;
  chatId: string;
  userId: string;
  text: string;
}

export function parseTelegramUpdate(
  update: TelegramUpdate,
): NormalizedTelegramMessage | null {
  const message = update.message;

  if (!message) {
    return null;
  }

  if (!message.text) {
    return null;
  }

  return {
    messageId: String(message.message_id),
    chatId: String(message.chat.id),
    userId: String(message.from?.id ?? message.chat.id),
    text: message.text,
  };
}
