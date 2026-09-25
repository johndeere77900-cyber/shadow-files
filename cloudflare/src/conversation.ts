export interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
}

const MAX_TURNS = 20;

const conversations = new Map<
  string,
  ConversationTurn[]
>();

export function getConversation(
  conversationId: string,
): ConversationTurn[] {
  return conversations.get(conversationId) ?? [];
}

export function addConversationTurn(
  conversationId: string,
  turn: ConversationTurn,
): ConversationTurn[] {
  const history = getConversation(conversationId);

  history.push(turn);

  if (history.length > MAX_TURNS) {
    history.splice(
      0,
      history.length - MAX_TURNS,
    );
  }

  conversations.set(
    conversationId,
    history,
  );

  return history;
}

export function clearConversation(
  conversationId: string,
): void {
  conversations.delete(conversationId);
}
