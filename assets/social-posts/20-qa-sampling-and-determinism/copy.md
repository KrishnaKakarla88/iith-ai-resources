--- LINKEDIN ---
Sampling & determinism: questions that actually get asked

"A teammate sets temperature=0 and seed=42 and says the pipeline is now 'fully deterministic, safe to unit test on exact output.' Do you sign off?" No — both are best-effort, not a contract. Provider-side floating-point non-determinism, batching effects across concurrent requests, and silent backend model updates can all still change output at temperature=0. Test structure/behavior instead — does it call the right tool, does the JSON validate, does a keyword appear — not byte-for-byte equality.

"When would raising temperature actually hurt a task that 'needs creativity'?" Any task with a verifiable right answer buried in a creative-looking wrapper — a tool-call payload, a specific extracted field, code that must compile. Higher temperature increases the odds of a plausible-looking but wrong sequence exactly where correctness is the actual requirement. Creativity and correctness are different axes; raising temperature only ever costs you on the correctness one.

"Why does chain-of-thought sometimes make small, fast models worse, not better?" CoT works because earlier reasoning tokens become context for later ones — but only if the intermediate reasoning is itself likely to be correct. A smaller model's reasoning steps are less reliable, so a bad early step compounds into a worse final answer instead of self-correcting.

#AppliedAI #LLM #AIEngineering

--- INSTAGRAM ---
Sampling & determinism: questions that get asked 🎲

temp=0 + seed=42 is best-effort, not a guarantee — test structure, not exact bytes.

Higher temperature only ever hurts when correctness is the actual requirement.

CoT can hurt small models — a bad early step compounds.

Which of these have you actually been asked?

#AppliedAI #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
single image
- kicker: Interview Nugget
- headline: Sampling & Determinism: Questions That Get Asked
- 1. "temp=0 + seed=42 = deterministic?" — Both are best-effort. Test structure, not exact bytes.
- 2. Does temperature help creative tasks? — Only if correctness isn't buried in the wrapper.
- 3. Why does CoT hurt small models? — A bad early reasoning step compounds into a worse answer.
- footer code: assert response.tool_calls[0].name == "expected_tool"

--- SCHEDULE ---
Tue 9/22: IG 5pm · LinkedIn 11am
