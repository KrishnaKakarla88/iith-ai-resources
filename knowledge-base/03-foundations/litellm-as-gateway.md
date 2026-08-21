---
stage: "03-foundations"
tools: [litellm]
tags: [litellm, gateway, provider-agnostic]
last_verified: 2026-08-20
verified_against: "litellm>=1.96.2"
---

# LiteLLM as a gateway

Using LiteLLM as the seam between your agent code and *any* provider — swap the `model=` string, get a different vendor, with zero other code changes.

## Prerequisites
- [[litellm-basics]]

## In plain English

[[litellm-basics]] covered the `completion()` call shape. The gateway framing is the payoff of that shape: because every provider's response gets normalized into the same OpenAI-style object, your application code never branches on "which provider am I talking to." A function written against `litellm.completion(model=m, messages=msgs)` works identically whether `m` is `"groq/llama-3.1-8b-instant"` or `"gpt-4o-mini"` — the lab proves this directly by running the exact same `litellm_chat()` function across both without touching a single line of its body. That's the core value proposition: provider choice becomes a config value, not an architectural decision baked into your call sites.

This matters in production for a mundane but real reason — model rankings and pricing change monthly, and being locked into one provider's SDK means a "let's just try the new model" experiment is a rewrite, not a config change. LiteLLM (used as a library, or run standalone as a **proxy** server) is one of several tools built specifically to make that swap cheap.

## Core mechanics

| Concept | What it means |
|---|---|
| Model string as router | `"groq/llama-3.1-8b-instant"`, `"openai/gpt-4o"`, `"anthropic/claude-sonnet-4-6"` — the prefix before `/` tells LiteLLM which provider's SDK/API to call |
| Library mode | `import litellm; litellm.completion(...)` — runs in-process, resolves API keys from env vars per-provider |
| Proxy mode | `litellm --config config.yaml` — a standalone server your app calls over HTTP, useful for centralized routing/fallback/cost-accounting across multiple apps |
| Fallback/routing (proxy) | Config-driven: try model A, fall back to model B on failure — orchestration [[retry-fallback-patterns]] would otherwise hand-roll |
| Credential resolution | Library mode reads provider env vars (`GROQ_API_KEY`, `OPENAI_API_KEY`) directly; proxy mode has its **own** separate credential layer |

## Sample code

Lab-sourced (Day 1 · Session 1) — the same function, unmodified, across two providers:

```python
import litellm

def litellm_chat(model: str, user_input: str) -> str:
    response = litellm.completion(
        model=model,
        messages=[{"role": "system", "content": "You are a support assistant."},
                  {"role": "user", "content": user_input}],
    )
    return response.choices[0].message.content

# identical call, different provider — zero code change
litellm_chat("groq/llama-3.1-8b-instant", "What's your return policy?")
litellm_chat("gpt-4o-mini", "What's your return policy?")
```

Proxy mode (`docs.litellm.ai`), for when routing/fallback needs to live outside your application process:

```yaml
# config.yaml
model_list:
  - model_name: groq-llama
    litellm_params:
      model: groq/llama-3.1-8b-instant
      api_key: os.environ/GROQ_API_KEY
  - model_name: gpt-4o-mini
    litellm_params:
      model: gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
```
```bash
litellm --config config.yaml   # your app now calls this proxy over HTTP
```

**Credential-resolution gotcha:** LiteLLM's default per-provider env-var resolution (`GROQ_API_KEY`, etc.) is designed for **library mode**. The moment you put a LiteLLM **proxy** in front of your app, there are now two different credentials in play — the provider key the proxy forwards upstream, and the key your app must send *to the proxy itself* (`LITELLM_MASTER_KEY` / a per-client virtual key). Reusing the provider-key resolution logic against a proxy layer sends the wrong token where it's not expected; this has to be explicitly branched, not assumed to "just work" the same way library mode does.

## Alternatives

| Approach | Where it lives | Boring/simple alternative to LiteLLM-as-gateway? |
|---|---|---|
| LiteLLM (library or self-hosted proxy) | `litellm` package / `BerriAI/litellm` | — |
| OpenRouter | Hosted gateway, single OpenAI-compatible endpoint, 300+ models | No — widest hosted catalog with least setup, but adds a credit markup (~5.5%) and a third-party hop you don't control[^gateway-compare] |
| Portkey | Hosted/self-hostable gateway focused on production observability | No — richer built-in routing/logs/guardrails/budgets than LiteLLM's proxy out of the box, at a cost/vendor-dependency tradeoff[^gateway-compare] |
| Vercel AI Gateway / Cloudflare AI Gateway | Platform-native hosted gateways | No — convenient if you're already on that platform, less portable elsewhere |
| Provider SDKs + your own if/else router | Plain Python | **Yes** — the boring option; fine for 2-3 providers you rarely swap between, becomes unmaintainable fast past that as each provider's SDK drifts independently |

## How this shows up in the capstone

Milestone 1 (provider-agnostic LLM client + structured intake) — every ShopSense agent calls through `litellm.completion()` so the model backing any given agent is a config change, not a code change; see [[capstone-milestone-map]].

## Interview fire round

- **Q: What actually changes when you swap `model="groq/llama-3.1-8b-instant"` for `model="gpt-4o-mini"` in a LiteLLM call?**
  A: Nothing in your code — LiteLLM parses the provider prefix, dispatches to that provider's SDK/API, and normalizes the response back into the same shape your code already expects.
- **Q: Why does adding a LiteLLM proxy in front of your app introduce a new credential-resolution bug class?**
  A: Because there are now two credentials — the provider key the proxy forwards upstream, and the key your app sends to authenticate to the proxy — and LiteLLM's default env-var resolution logic (built for library mode) doesn't automatically distinguish them.

## Production gotchas & best practices

- Production gotcha (from `labs/production-notes.md`): explicitly branch credential resolution once a proxy layer is introduced — LiteLLM's default per-provider env-var resolution sends the wrong token to the proxy layer otherwise.
- Production gotcha (web-verified): a common real-world symptom of this is the proxy running in an environment (Docker, systemd, CI) that doesn't inherit the host shell's env vars at all — worth confirming the variable is actually present in the *proxy's* process context, not just your terminal, before assuming the credential-branching logic is the bug.[^litellm-auth]
- Production practice (from `labs/production-notes.md`): match provider errors by message-substring, not exception class, when routing through LiteLLM — exception types for the same underlying failure (e.g. a malformed tool call) aren't standardized across the providers LiteLLM fronts.
- Production practice (from `labs/production-notes.md`): pay LiteLLM's slow first-import cost at process startup (eager, best-effort warm-up), not on the first live request — otherwise it shows up as unattributed latency on whichever request happens to trigger the import.

## Course vs. production

The lab uses LiteLLM purely as a library, in-process, with per-provider env vars — no proxy, no routing config. Production deployments that need centralized fallback, per-team budget limits, or unified cost/observability across multiple applications typically graduate to the standalone LiteLLM proxy (or a hosted equivalent like Portkey) — at which point the credential-resolution split above becomes a real, not theoretical, concern.

## Related
- **Builds on** — [[litellm-basics]]
- **Related** — [[retry-fallback-patterns]] (proxy-level fallback overlaps this), [[model-selection-cost-latency-tradeoffs]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "`litellm_chat(model, user_input)`")
- `labs/production-notes.md` (§ "Auth / Permissions" — proxy credential branching; § "Technology-Specific Learnings — LiteLLM")

**Web sources**
- [LiteLLM — Groq provider docs](https://docs.litellm.ai/docs/providers/groq) — model prefix + proxy config.yaml shape, accessed 2026-08-20
- [LiteLLM Authentication Failed: Root Cause + Fix](https://markaicode.com/errors/litellm-authentication-failed-fix/) — master-key vs provider-key credential confusion, accessed 2026-08-20
- [OpenRouter Alternatives 2026: LiteLLM, Portkey, Unify & More](https://www.layer3labs.io/comparisons/openrouter-alternatives) — gateway comparison, accessed 2026-08-20

[^gateway-compare]: layer3labs.io — OpenRouter/Portkey/LiteLLM tradeoffs, 2026.
[^litellm-auth]: markaicode.com — common LiteLLM proxy auth-failure root causes, 2026.
