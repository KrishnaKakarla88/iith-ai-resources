--- LINKEDIN ---
litellm.completion(model=..., messages=...) normalizes both the call shape and the response shape across providers. The provider prefix before the slash — "groq/llama-3.1-8b-instant" vs "gpt-4o-mini" — is what routes the call. Everything else, including response.choices[0].message.content, stays identical no matter which provider actually answered.

The other half of completion() is the generation knobs: temperature controls randomness, max_tokens caps length, stop ends generation early, response_format switches prose vs JSON mode. Not LiteLLM inventions — the OpenAI-style set most providers converged on — but LiteLLM validates and forwards them per-provider.

One knob pairing worth knowing: top_p (nucleus sampling) shapes randomness a different way than temperature. Provider guidance: tune one or the other, not both together.

And temperature=0 is not a guarantee of identical output. Near-deterministic in practice, not promised — same for seed. Providers make a "best effort," not a hard contract.

Do you rely on temperature=0 for reproducible outputs?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
One function call. Any provider. 🔀

litellm.completion(model="groq/llama-3.1-8b-instant", messages=...) — swap the model string, everything else stays the same.

top_p and temperature both shape randomness — tune one or the other, not both together.

temperature=0 is near-deterministic, not guaranteed. Providers make a "best effort," not a promise.

Full breakdown in the carousel.

Do you rely on temperature=0 for reproducible outputs?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "One Function, Every Provider"
2. Core mechanics — the model string routes the call (code)
3. Core mechanics — the generation knobs
4. Core mechanics — top_p is an alternative, not an add-on (code)
5. Core mechanics — token counting is per-model (code)
6. Takeaway — temperature=0 is not a guarantee (closing question)
