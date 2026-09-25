export interface Env {
  SHADOW_FILES_MODE: string;
}

export default {
  async fetch(
    request: Request,
    env: Env,
  ): Promise<Response> {
    const url = new URL(request.url);

    if (request.method !== "GET") {
      return new Response(
        JSON.stringify({
          ok: false,
          error: "Method not allowed.",
        }),
        {
          status: 405,
          headers: {
            "content-type": "application/json",
          },
        },
      );
    }

    if (url.pathname === "/") {
      return new Response(
        JSON.stringify({
          ok: true,
          service: "Shadow Files Cloudflare Control",
          mode: env.SHADOW_FILES_MODE,
          status: "online",
        }),
        {
          status: 200,
          headers: {
            "content-type": "application/json",
          },
        },
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
          "content-type": "application/json",
        },
      },
    );
  },
};
