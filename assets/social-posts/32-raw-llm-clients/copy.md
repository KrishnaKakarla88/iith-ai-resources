--- LINKEDIN ---
Calling a provider's SDK directly, before any gateway abstraction sits in front of it, is the baseline every later wrapper gets judged against. It exposes the fact every wrapper is built to hide: an LLM completion call is stateless — no continuity carries over unless your code resends the growing history itself.

Groq's own SDK and the OpenAI SDK pointed at Groq's base_url use the identical call shape — client.chat.completions.create(...), reply at response.choices[0].message.content either way. That works because Groq exposes an OpenAI-compatible endpoint, same request/response JSON shape as OpenAI's own API. Calling both back to back makes the point concrete: the only thing that changes is which client object you instantiate and which base_url it points at — the exact seam LiteLLM later automates away.

Not hypothetical either: a single shared messages list reused across concurrent users leaks one customer's conversation into another's. A SessionStore mapping session_id to its own isolated list prevents that cross-talk.

Have you called a provider's raw SDK directly, or gone straight to a wrapper?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
The baseline before any wrapper. 🧩

client.chat.completions.create(...) — same shape for Groq's SDK and the OpenAI SDK pointed at Groq's base_url.

Only the client object and base_url change. That's the exact seam LiteLLM later automates away.

Miss this and a shared messages list across users leaks one customer's conversation into another's.

Full mechanism in the carousel.

Raw SDK, or straight to a wrapper?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "The Baseline Before Any Wrapper"
2. Core mechanics — same call shape across providers (code)
3. Why it works — Groq's OpenAI-compatible endpoint (code)
4. Why it matters — only the client object changes
5. Real bug class — SessionStore per-session isolation (code)
6. Takeaway — statelessness is the baseline (closing question)
