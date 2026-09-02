--- LINKEDIN ---
Real interview scenario: your agent's per-call cost dashboard shows a sudden 40% jump with no corresponding traffic increase. Walk through how you'd diagnose it using tracing data alone.

Start from the generation spans specifically, since only those carry usage_details and model. A cost anomaly usually traces to one of three causes: a model routing change (calls silently falling back to a pricier model), a prompt-length regression (context growing per call — a broken compression step, say), or a retry storm (failed calls retried more than expected, multiplying billed tokens per logical request).

Comparing token counts and model names per trace, before and after the jump, is what actually localizes which of the three it is — the aggregate dollar figure alone can't distinguish "more expensive calls" from "more calls."

A cost dashboard alone is a symptom, not a diagnosis. The generation span's usage_details and model fields are what turn that symptom into a specific, fixable cause.

If your cost jumped 40% tomorrow, could you localize the cause from tracing data alone?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
Cost jumps 40%. Traffic didn't move. Now what? 💸

Start from generation spans — only those carry usage_details and model.

Three usual suspects: silent fallback to a pricier model, a prompt-length regression, or a retry storm.

The aggregate dollar figure can't tell "more expensive calls" from "more calls" apart. Per-trace comparison can.

Full scenario + answer in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 5 slides
1. Title — "Cost Jumps 40%. Traffic Didn't Move."
2. The question — no corresponding traffic increase
3. The answer — start from generation spans specifically (code)
4. Why this works — the aggregate dollar figure can't tell you which one
5. Takeaway — a cost dashboard alone is a symptom, not a diagnosis (closing question)
