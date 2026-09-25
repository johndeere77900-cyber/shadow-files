export interface IntelligenceEnv {
  AI_API_URL: string;
  AI_API_KEY: string;
  AI_MODEL: string;
}

export interface IntelligenceRequest {
  conversation: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
}

export interface IntelligenceResponse {
  text: string;
}

export async function generateIntelligentResponse(
  env: IntelligenceEnv,
  request: IntelligenceRequest,
): Promise<IntelligenceResponse> {
  if (!env.AI_API_URL) {
    throw new Error("AI_API_URL is not configured.");
  }

  if (!env.AI_API_KEY) {
    throw new Error("AI_API_KEY is not configured.");
  }

  if (!env.AI_MODEL) {
    throw new Error("AI_MODEL is not configured.");
  }

  const response = await fetch(env.AI_API_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${env.AI_API_KEY}`,
    },
    body: JSON.stringify({
      model: env.AI_MODEL,
      messages: request.conversation.map(
        (message) => ({
          role: message.role,
          content: message.content,
        }),
      ),
    }),
  });

  if (!response.ok) {
    throw new Error(
      `AI provider request failed with status ${response.status}.`,
    );
  }

  const data = (await response.json()) as {
    choices?: Array<{
      message?: {
        content?: string;
      };
    }>;
  };

  const text = data.choices?.[0]?.message?.content;

  if (!text) {
    throw new Error(
      "AI provider returned no response text.",
    );
  }

  return {
    text,
  };
                         }
