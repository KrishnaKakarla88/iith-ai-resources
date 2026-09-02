--- LINKEDIN ---
An LLM judge inherits every blind spot a model has. A documented failure mode: the judge rewards style — a long, fluent, well-formatted answer scores well even when it's factually wrong, because "confident and articulate" correlates with "correct" in the judge's training distribution far more than it should.

Three frameworks, cross-checked rather than trusted individually. Ragas's Faithfulness checks whether an answer is entailed by the context. DeepEval's GEval builds a custom rubric judge from plain-language criteria — no hand-written judge prompt needed. TruLens's feedback functions return chain-of-thought reasoning alongside every score. If all three independently agree an answer is faithful, that's stronger evidence than any single judge's opinion.

The fix for the style-rewarding blind spot isn't to distrust judges wholesale — it's to measure them. A worked example: 200 answers scored, 40 hand-labeled, 35/40 agreement — 87.5%. But all four disagreements were long, fluent, well-formatted answers that were factually wrong. The judge was rewarding style.

The direction that actually costs you: judge says PASS, human says FAIL. That's the judge certifying bad output as good — invisible unless you specifically go looking for it. Judge-FAIL/human-PASS just costs a false alarm you'll notice immediately.

Production gotcha: wrap each judge call in its own try/except inside the dispatch function. Python doesn't return partial results on an uncaught exception — one rate-limited judge silently erases every score already computed for that item, including the ones that already succeeded.

A judge audited against last quarter's model version is an audit of a judge that no longer exists. Recalibrate on every model swap, prompt change, or new domain.

Have you ever audited your LLM judge against a human label, or just trusted the score?

#AppliedAI #AIEngineering #LLM #RAG

--- INSTAGRAM ---
Your LLM judge might just reward confident writing. Not correctness. 🎭

87.5% agreement with human labels sounds good — until you check the direction. Judge-PASS/human-FAIL is invisible unless you audit for it.

Run three judges, cross-check them. One judge exhausting its retry budget shouldn't erase every score already computed.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #RAG #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "An LLM Judge Inherits Every Blind Spot A Model Has"
2. Three judges, cross-checked — agreement is stronger evidence than any one opinion
3. Auditing the judge — hand-label a sample, compute agreement (code)
4. The direction that costs you — judge says PASS, human says FAIL
5. Sample code — same trace, three independent calls (code)
6. Production gotcha — one judge's exception discards every score already computed
7. Takeaway — a judge audited against last quarter's model no longer exists (closing question)
