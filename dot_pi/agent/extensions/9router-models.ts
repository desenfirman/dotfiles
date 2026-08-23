import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

type RouterModel = {
  id: string;
  name?: string;
};

type ModelsResponse = {
  data?: RouterModel[];
};

const BASE_URL = process.env.NINE_ROUTER_BASE_URL ?? "http://127.0.0.1:20128/v1";
const API_KEY = process.env.NINE_ROUTER_API_KEY;

export default function (pi: ExtensionAPI) {
  pi.registerProvider("9router", {
    name: "9Router",
    baseUrl: BASE_URL,
    api: "openai-completions",
    apiKey: "$NINE_ROUTER_API_KEY",

    async refreshModels({ signal }) {
      const response = await fetch(`${BASE_URL}/models`, {
        signal,
        headers: API_KEY
          ? { Authorization: `Bearer ${API_KEY}` }
          : undefined,
      });

      if (!response.ok) {
        throw new Error(`9Router model discovery failed: HTTP ${response.status}`);
      }

      const payload = (await response.json()) as ModelsResponse;
      if (!Array.isArray(payload.data)) {
        throw new Error("9Router model discovery returned an invalid response");
      }

      return payload.data
        .filter((model): model is RouterModel => typeof model?.id === "string")
        .map((model) => ({
          id: model.id,
          name: model.name ?? model.id,
          reasoning: false,
          input: ["text"],
          cost: {
            input: 0,
            output: 0,
            cacheRead: 0,
            cacheWrite: 0,
          },
          contextWindow: 200000,
          maxTokens: 16384,
        }));
    },
  });
}
