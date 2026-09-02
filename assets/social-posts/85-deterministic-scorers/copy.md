--- LINKEDIN ---
Not every eval question needs a language model. "Did the agent call search_catalog with the right book_id?" is a string comparison — cheap, milliseconds, no rate limit, and perfectly reproducible.

def tool_match_score(item, trace):
    call = trace.get("tool_call") or {}
    if call.get("name") != item["expected_tool"]:
        return 0.0
    args_str = str(call.get("args", {})).lower()
    if not all(sub.lower() in args_str for sub in item["expected_args_contains"]):
        return 0.0
    return 1.0

The all-or-nothing vs. partial-credit choice is deliberate, not a default. A tool call with the wrong argument isn't 80% correct — it's the wrong call, full stop, so tool-match is binary. A written answer can legitimately cover most of the expected ground without every keyword present, so keyword-hit scoring gives partial credit.

The real value isn't replacing LLM judges — it's an independent signal for when they're wrong. LLM-judge scoring is noisy, and an eval harness relying only on judges has no way to notice a judge is systematically wrong. When a deterministic score and a judge score disagree, that disagreement is exactly the case worth reading by hand.

Production gotcha worth documenting: a metric's name doesn't guarantee its mechanism. A metric labeled expected_route was, in one real case, scored against answer content rather than structural routing state — because no golden case ever exercised the path that would have exposed the mismatch.

The trade-off is exactly what you'd expect: deterministic scorers can only check what you can express as code. They can't tell you if an answer is well-written or helpful in tone — that's where an LLM judge earns its cost.

Do your eval scores ever disagree with each other, or do you only run one kind?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
Not every eval question needs an LLM. 🎯

"Right tool, right args" is a string comparison. Cheap, reproducible, no rate limit.

def tool_match_score(item, trace):
    if call.get("name") != item["expected_tool"]: return 0.0

Binary for tool calls. Partial credit for keyword coverage. Different questions, different scoring.

The real value: an independent check on your LLM judges when they disagree.

Full breakdown in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Not Every Eval Question Needs A Language Model"
2. Sample code — one scorer per category, reading the same trace (code)
3. All-or-nothing vs partial credit — the choice is deliberate, not a default
4. The real value — an independent signal when judges are wrong
5. Production gotcha — a metric's name doesn't guarantee its mechanism
6. Takeaway — the trade-off is exactly what you'd expect (closing question)
