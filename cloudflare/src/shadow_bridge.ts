export interface ShadowBridgeEnv {
  SHADOW_SERVICE_URL: string;
  SHADOW_SERVICE_SECRET: string;
}

export interface ShadowRequest {
  conversationId: string;
  message: string;
  userId: string;
}

export interface ShadowResponse {
  ok: boolean;
  text?: string;
  action?: string;
  status?: string;
  error?: string;
}

export async function sendToShadow(
  env: ShadowBridgeEnv,
  request: ShadowRequest,
): Promise<ShadowResponse> {
  if (!env.SHADOW_SERVICE_URL) {
    throw new Error(
      "SHADOW_SERVICE_URL is not configured.",
    );
  }

  if (!env.SHADOW_SERVICE_SECRET) {
    throw new Error(
      "SHADOW_SERVICE_SECRET is not configured.",
    );
  }

  const response = await fetch(
    env.SHADOW_SERVICE_URL,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization:
          `Bearer ${env.SHADOW_SERVICE_SECRET}`,
      },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Shadow service request failed with status ${response.status}.`,
    );
  }

  return (await response.json()) as ShadowResponse;
    }
