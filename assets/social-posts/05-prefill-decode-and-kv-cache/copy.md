--- LINKEDIN ---
Every LLM call runs through two very different phases

Prefill processes your whole prompt in one parallel pass — compute-bound, and it determines time-to-first-token: how long you wait before any reply appears.

Decode generates the reply one token at a time, each depending on the one before it. Every step reloads weights from GPU memory, so it's memory-bandwidth-bound instead — this determines inter-token latency, the speed after the first token lands.

Here's what connects them: a new token's attention needs the Key/Value vectors of every prior token, including the whole prompt. Recomputing that every decode step would redo prefill's work again and again. The KV cache stores those vectors once and reuses them — each step only computes Key/Value for the one new token.

The real cost: cache size scales with sequence length, layers, and attention heads. A ~7B model at a 100K-token context runs roughly 52GB for one request's cache alone — a bigger advertised context window is a real per-request memory bill, not just a bigger token limit.

Full mechanics — the sizing formula and worked example — in the carousel.

Does your serving setup account for KV cache memory, or just token limits?

#AppliedAI #LLM #AIEngineering

--- INSTAGRAM ---
Every LLM call has two very different phases ⚙️

Prefill: whole prompt, one parallel pass — sets time-to-first-token.

Decode: one token at a time — sets the speed after that.

The KV cache stores Key/Value vectors once so decode doesn't redo prefill's work every step. A ~7B model at 100K tokens: ~52GB of cache for one request.

Does your setup account for that memory, or just token limits?

#AppliedAI #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "The Two Phases Inside Every LLM Call"
2. Concept 1 — Prefill
3. Concept 2 — Decode
4. Concept 3 — The KV Cache
5. Concept 4 — Sizing The Cache (code: size = 2 * seq_len * n_layers * n_kv_heads * head_dim * bytes)
6. Takeaway — closing question

--- SCHEDULE ---
Tue 9/1: IG 5pm · LinkedIn 11am
