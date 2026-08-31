--- LINKEDIN ---
litellm_chat(model, user_input) never branches on which provider it's talking to. Swap the model= string and get a different vendor — same function, zero code change. That's the payoff of routing through LiteLLM: provider choice becomes a config value, not an architectural decision.

Model rankings and pricing change monthly. Locked into one provider's SDK, "let's just try the new model" is a rewrite. Routed through LiteLLM, it's a one-line model= change.

Two distinct modes: library mode runs in-process and reads provider env vars directly; proxy mode is a standalone server your app calls over HTTP for centralized routing and fallback. The moment a proxy sits in front, there are two credentials — the provider key the proxy forwards upstream, and the key your app sends to the proxy itself. LiteLLM's default resolution is built for library mode and doesn't separate the two automatically. A 401 despite a valid provider key usually means the app-to-proxy credential — not the upstream one.

Are you running LiteLLM in library mode, or behind a proxy?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Provider swap = config change, not a rewrite. 🔧

litellm_chat("groq/llama-3.1-8b-instant", text) and litellm_chat("gpt-4o-mini", text) — same function, zero code change.

Add a proxy in front and you get two credentials: the provider key forwarded upstream, and the key your app sends to the proxy.

A 401 with a valid key usually means the wrong one of those two.

Full breakdown in the carousel.

Library mode or proxy mode in your stack?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Provider Swap Becomes A Config Value"
2. Core mechanics — zero code change across providers (code)
3. Two modes — library vs proxy
4. Gotcha — a proxy creates two credentials (code)
5. Why it matters — model rankings change monthly
6. Takeaway — a 401 isn't always auth (closing question)
