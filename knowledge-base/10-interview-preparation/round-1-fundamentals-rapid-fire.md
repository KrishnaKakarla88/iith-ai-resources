# Round 1: Fundamentals rapid-fire

This round covers stages [[what-is-an-llm|00]]-[[workflow-vs-agent-autonomy-spectrum|04]]: LLM basics, tokens, prompting, context, Python-for-agents patterns, tool calling, ReAct/reflection. These are the questions a real interviewer asks in the first 15-20 minutes to establish whether you actually have the vocabulary — answered wrong or vaguely here, everything after gets discounted. Answer out loud, in one or two sentences, before reading the given answer.

Each question below is written the way it actually gets asked — comparative, adversarial, or "why would this fail" — not as a bare definition. Sub-sectioned by topic; work top to bottom once, then jump straight to whichever sub-section exposed a gap.

## LLM basics and generation

**Q1. What's actually different between a "model" and an "agent"? Interviewers ask this to see if you're using the words precisely.**
A model is a next-token predictor — stateless, no memory, no ability to act. An agent is that model wrapped in a harness: a loop that decides when to call the model again, a bounded set of tools it can request, retries, permission checks, and context management around every call. Swap the harness under the same model and the product can feel completely different; swap the model inside a fixed harness and the system's shape barely changes. See [[architecture-of-an-agentic-system]], [[what-is-an-llm]].

**Q2. If you set `temperature=0`, are you guaranteed the same output for the same input every time?**
No — near-deterministic, not guaranteed. Floating-point non-determinism, provider-side batching, and backend changes can still produce slightly different output even at `temperature=0`. Never build a test or a business-critical check that assumes bit-for-bit reproducibility from temperature alone. See [[how-llms-generate-text]].

**Q3. What's the practical difference between `temperature` and `top_p`, and why would you tune one instead of stacking both?**
Temperature reshapes the entire probability distribution (flatter or more peaked); `top_p` truncates the distribution to the smallest set of tokens whose cumulative probability reaches `p`, before sampling. They're two different levers on the same step, and stacking both makes the actual sampling behavior hard to reason about — tune one deliberately, leave the other at its default.

**Q4. A pipeline checks `response.choices[0].content` and moves on. What's it not checking, and how could that silently corrupt downstream data?**
It's not checking `finish_reason`. If generation stopped because it hit `max_tokens` (`finish_reason == "length"`) rather than a natural stop, the content is truncated mid-thought — and if that content feeds a JSON parser or a structured-output pipeline, you get a plausible-looking but incomplete result instead of a clean error. Always branch on `finish_reason` before trusting a response is complete, especially anything downstream code parses. See [[how-llms-generate-text]], [[structured-output-repair-loops]].

**Q5. Why can't an LLM reliably count the number of "r"s in "strawberry"?**
It never sees individual characters. The word is split into one or more subword tokens by BPE tokenization, and the model reasons over token IDs, not letters — a "word-shaped" problem is often actually a token-shaped problem in disguise. See [[tokens-and-tokenization]].

**Q6. Why does the same string cost more tokens as JSON or code than as plain English?**
BPE vocabularies are built from natural-language-heavy training corpora — common English words and word-fragments get compact, high-frequency token slots. Structured text (JSON keys, punctuation-dense code, IDs, hashes) hits rarer token combinations, so it tokenizes less efficiently: more tokens per character. This is a real cost lever, not trivia — a system that logs structured tool-call payloads verbatim into every turn's context is paying a token tax most teams don't measure. See [[tokens-and-tokenization]].

## Context, prompting, and context engineering

**Q7. Your context window is 128K tokens and your conversation is only 40K tokens in. Can quality still degrade?**
Yes — this is context rot, and it's distinct from hitting the hard ceiling. Performance can degrade well before the window is full, because self-attention's effective use of a long input isn't uniform: content buried in the middle of a long context gets attended to less reliably than content near the start or end ("lost in the middle"). A bigger window changes *when* you hit the wall, not whether stuffing it with irrelevant content costs you something before then. See [[context-rot-and-long-context-management]], [[context-windows-and-limits]].

**Q8. "Just use a 1M-token context window and stop worrying about retrieval." Push back on this.**
A bigger window doesn't eliminate the need for retrieval, pruning, or compression — it just moves the point where the hard ceiling shows up. Self-attention's comparison surface grows roughly with the square of sequence length (doubling tokens roughly quadruples the attention computation), so more content in the window is never free, even below the ceiling. Retrieval exists to keep what's *actually relevant* small, which is a quality lever independent of how big the window technically is. See [[context-rot-and-long-context-management]], [[hybrid-retrieval-rrf]].

**Q9. How is context engineering different from prompt engineering — and why would an interviewer care about the distinction?**
Prompt engineering is wording a single instruction well. Context engineering is the broader, per-call decision about *everything* that earns a seat in the window — system prompt, retrieved chunks, memory, tool results, trimmed history — of which prompt wording is only one input. An interviewer asking this is checking whether you think about a request holistically (what data should even be here?) or only about phrasing, which is a much smaller lever in a production system with retrieval and memory attached. See [[context-engineering]].

**Q10. Two calls use the identically-worded system prompt and still produce very different quality answers. What's the first thing you'd check?**
What differs in the rest of the window — retrieved content, conversation history, memory recall — not the prompt wording. A well-worded instruction sitting on top of a bad selection of context still produces a bad answer; the instruction and the context compete for the same fixed token budget and both matter. See [[context-engineering]].

**Q11. What's the difference between zero-shot and few-shot prompting, and when would few-shot actually hurt rather than help?**
Zero-shot gives the model only the instruction; few-shot adds worked examples in the prompt so the model can pattern-match the expected shape of a good answer. Few-shot can hurt when the examples are unrepresentative or too narrow — the model can overfit to superficial patterns in the examples (a specific phrasing, an incidental format quirk) rather than the actual task, or the extra tokens simply crowd out budget better spent on real retrieved context. See [[prompting-basics]], [[prompt-engineering-techniques]].

## Tool calling, ReAct, and reflection

**Q12. "The model called the tool and it returned 31°C" appears in the model's response text, but your logs show no corresponding tool call. What happened, and why does it matter?**
The model narrated a tool call it never actually made — a real failure mode, not a hypothetical. The fix is structural: never drive downstream logic or trust off the model's prose describing what it did; always branch off the structured `tool_calls` field the API actually returned. This is exactly why "the model never executes anything — your code decides and executes" is the load-bearing sentence of tool calling. See [[tool-calling-fundamentals]].

**Q13. Why is a tool's `description` field called the highest-leverage part of a tool schema — more than the parameter types?**
The description is effectively a prompt the model reads to decide *when* to reach for this tool at all. A vague description causes the model to call the wrong tool, or the right tool at the wrong moment, regardless of how tightly the parameter JSON Schema is typed — the schema constrains the shape of a call the model already decided to make; the description decides whether it makes that call. See [[tool-calling-fundamentals]].

**Q14. Why would you implement a calculator tool by parsing with `ast` and walking a whitelisted operator set instead of just calling `eval(expr)`?**
`eval()` executes arbitrary Python — anything parseable as an expression, including attribute access and calls into other code — so a model-supplied string reaching `eval()` is a direct code-execution vulnerability, not a hypothetical one. Parsing to an AST and evaluating only a small whitelisted set of node types (`ast.Add`, `ast.Mult`, etc.) bounds what can actually run. See [[tool-calling-fundamentals]].

**Q15. What does `stop=["Observation:"]` actually prevent in a ReAct loop, and what happens if you forget it?**
Without it, nothing stops the model from generating its own fake `Observation:` line and reasoning off an invented result instead of waiting for your code to inject the real tool output — the model has no way of knowing it's supposed to stop and wait. This is a real production bug class (hallucinated tool results silently feeding downstream reasoning), not a lab nicety. See [[react-pattern]].

**Q16. Why does the ReAct system prompt explicitly tell the model to treat `Observation:` content as untrusted data?**
Because observations can carry adversarial content — a search result or scraped page with embedded instructions ("ignore previous instructions and..."). Without that explicit framing, the model may follow instructions hidden inside tool output instead of just reasoning about it as data — the same "external content is untrusted" discipline that applies at the RAG boundary, applied one stage earlier to tool observations. See [[react-pattern]], [[grounded-answers-injection-defense]].

**Q17. What does the reflection pattern check that a stage-03 structured-output repair loop doesn't, and why would you want both?**
A repair loop checks *shape* — valid JSON, right types, passes a schema validator. Reflection checks whether the answer actually *satisfies the goal* given the evidence the agent gathered — a shape-valid answer can still be substantively wrong (bad arithmetic, an unsupported claim). You want both because they catch different failure classes at different points in the pipeline. See [[reflection-pattern]], [[structured-output-repair-loops]].

**Q18. Why cap reflection at exactly one revision cycle instead of looping "critique, revise, critique again" until the model says `APPROVED`?**
Same reasoning as capping a ReAct loop's iterations — bounded cost, bounded risk. Additional critique rounds have diminishing accuracy payoff and the same runaway-loop risk as any uncapped agentic loop; a model critiquing its own output can also loop indefinitely without ever fully satisfying itself. See [[reflection-pattern]].

**Q19. Reflection's revision pass just failed because the API key expired mid-run. What should happen to the pipeline?**
Fail open: skip the critique, return the original draft, and report the reflection status honestly (e.g. `"SKIPPED"`) rather than fabricating a fake `APPROVED` verdict or blocking the whole pipeline on a broken *quality-improvement* step. An optional quality pass being unavailable should degrade the quality bar visibly, not the availability of the system. See [[reflection-pattern]].

**Q20. When would you reach for a fixed workflow instead of an agentic loop, even though an agent is "more capable"?**
When the task's steps are actually fixed and enumerable in advance — validate input, look something up, format an answer. A workflow gets the same outcome with lower cost, lower latency, and a fully testable set of paths, because your code decided the order, not the model. Autonomy is a cost you pay for genuine unpredictability in the task (the next step depends on something discovered mid-task), not a feature you reach for because it sounds more sophisticated. See [[workflow-vs-agent-autonomy-spectrum]].

## Python-for-agents patterns

**Q21. What actually happens if you call an `async def` function without `await`ing it?**
You get back a coroutine object, not a result — the function body hasn't executed yet. Python usually warns ("coroutine was never awaited") but doesn't raise, so the bug can silently propagate until the missing result causes a failure somewhere downstream. See [[async-await-for-llm-apps]].

**Q22. Why does async concurrency help an LLM/tool-calling pipeline but do nothing for a CPU-heavy loop?**
Async works by yielding control at `await` points while waiting on I/O — an LLM API call or an MCP subprocess call spends nearly all its wall-clock time waiting on a response, so the event loop can usefully run other coroutines during that wait. A CPU-bound loop never hits an `await` point to yield at — async buys it nothing; that needs real parallelism (multiprocessing), not concurrency. See [[async-await-for-llm-apps]].

**Q23. A decorator you wrote works fine on sync functions but silently breaks the moment a function becomes `async def`. What's the bug?**
The decorator's `wrapper` isn't branching on `inspect.iscoroutinefunction(fn)` — a plain sync wrapper applied to an async function just wraps the coroutine *object* without awaiting it, so it silently returns an un-awaited coroutine instead of the actual result, without raising. A decorator meant to support both needs a sync and an async wrapper, chosen based on that check. See [[decorators-and-wrappers]].

**Q24. What actually breaks if you forget `@functools.wraps(fn)` inside a decorator — and is it just cosmetic?**
Not just cosmetic in this stack: every decorated function's `__name__`/`__doc__` get replaced by the wrapper's own, which breaks anything that introspects a function's identity for real behavior — help(), some test frameworks, and specifically FastMCP, which reads a tool function's name and docstring to build its JSON schema. An unwrapped decorator on a tool function silently produces a broken or generic schema, not just an ugly `repr`. See [[decorators-and-wrappers]].

**Q25. Why does decorator *order* matter when stacking retry and a circuit breaker around the same function?**
Whichever decorator is applied innermost (closest to the function) runs its logic per individual call attempt; the outer one sees the aggregate. Retry innermost + circuit breaker outermost means a burst of retried-but-still-failing calls is what trips the breaker — swap the order and "one failure" means something different to the breaker (it would trip on the very first failed attempt, before retry even got a chance). See [[decorators-and-wrappers]], [[circuit-breaker-pattern]].

---

*Grounded in `lab-summaries/`, `presentations/day1.md`, this knowledge base's stage 00-04 pages, and general LLM/agent-engineering interview practice as of 2026-08.*
