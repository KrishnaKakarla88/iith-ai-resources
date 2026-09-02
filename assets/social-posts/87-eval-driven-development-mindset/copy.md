--- LINKEDIN ---
A demo proves an agent can work — once, on the input you happened to type, on a day the model happened to behave. It proves nothing about the input you didn't try, or what happens after next week's prompt change.

This is a distinct concern from unit testing. A unit test asks: does this function do what the code says it should, with the LLM call mocked out — deterministic, code-correctness. Eval asks: is the agent's actual behavior good enough to ship — probabilistic, and the LLM call is exactly the thing being measured. A node can pass every unit test and still route every query to the wrong tool.

The core idea: grade every layer, not just the final answer. Tool use (right tool, right arguments), retrieval (right documents came back), planning/routing (right sub-task chosen), final answer (correct, grounded, well-formed — the only layer a demo actually shows you).

Why that matters: a system with a 100% final-answer score can still be broken. Two wrong steps underneath can coincidentally land on a correct-looking answer, and you won't find out until the layers diverge on a case that doesn't get lucky. Grading only the final answer is grading a group project by the final presentation alone.

trace = {
    "query": query,
    "route": route,           # "tool" | "retrieval" | "direct"
    "tool_call": tool_call,
    "retrieved_docs": retrieved_docs,
    "final_answer": final_answer,
}

One trace shape, every scorer — deterministic and judge alike — reads from it, so component boundaries stay clean and comparable release over release.

The other half of the discipline: a golden set, not live traffic. Fixed inputs, re-run every time something changes — the prompt, the model, the retrieval corpus, a dependency version. Live traffic isn't controlled enough to tell you anything about one specific change.

Could you point to which layer of your agent broke, or only whether the final answer was right?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
A demo proves your agent can work. Once. 📊

Unit tests check code correctness with the LLM mocked out. Eval checks actual behavior quality — the LLM call is the thing being tested.

Grade every layer: tool use, retrieval, routing, final answer. A 100% final-answer score can still hide two wrong steps underneath.

Fixed golden set, re-run on every change — not live traffic.

Full breakdown in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A Demo Proves An Agent Can Work. Once."
2. Not the same as a unit test — code correctness vs behavior quality
3. The core idea — grade every layer, not just the final answer
4. Why that matters — a 100% final-answer score can still be broken
5. Sample code — one trace, every scorer reads the same shape (code)
6. Takeaway — fixed inputs, re-run every time something changes (closing question)
