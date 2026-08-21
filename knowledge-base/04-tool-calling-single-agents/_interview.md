# 04-tool-calling-single-agents — interview fire round

### workflow-vs-agent-autonomy-spectrum

- **Q: When should you use a workflow instead of an agent?**
  A: When the steps and their order are knowable in advance — a workflow gets the same outcome with less cost, lower latency, and a fully enumerable set of execution paths to test.
- **Q: Is an agent always "better" because it's more flexible?**
  A: No — flexibility is a cost (unpredictable paths, harder to bound, more tokens/latency), justified only when the task's steps genuinely can't be fixed ahead of time.
- **Q: What's the actual signal that a task needs agent autonomy?**
  A: The next step depends on something discovered mid-task (an unexpected tool result, a failure requiring a different approach) — not "this task involves an LLM" or "this feels complex."

### agentic-loop-fundamentals

- **Q: What are the four steps of the agentic loop?**
  A: Perceive, plan, act, observe — repeated until the model signals it's done or an iteration cap is hit.
- **Q: What makes a loop "agentic" rather than just a `while` loop with an LLM call in it?**
  A: The plan step is delegated to the model — your code doesn't decide what happens next, the model's output does; your code only executes what's requested.
- **Q: Why is the structured-output repair loop from stage 03 not usually called "agentic"?**
  A: It has no tool/action step and its "plan" (retry with the error fed back) is fixed by your code, not chosen by the model — it's closer to a workflow than an agent, per [[workflow-vs-agent-autonomy-spectrum]].

### tool-calling-fundamentals

- **Q: Who actually executes a tool call — the model or your code?**
  A: Your code, always. The model only ever produces a request (name + arguments); your application decides whether to comply and runs the function.
- **Q: Why is the tool's description field described as "the highest-leverage, most-neglected field"?**
  A: It's effectively a prompt the model reads to decide *when* to reach for the tool at all — a vague description causes the model to call the wrong tool, or the right tool at the wrong time, regardless of how correct the parameter schema is.
- **Q: What's wrong with implementing a calculator tool as `eval(expr)`?**
  A: Arbitrary code execution — `eval` runs anything Python can parse as an expression, including attribute access and calls into other code. Parse with `ast.parse` and walk the tree evaluating only a whitelisted operator set instead.

### react-pattern

- **Q: What does the `stop=["Observation:"]` argument actually prevent?**
  A: Without it, the model can generate its own fake `Observation:` text and reason off invented results instead of waiting for your code to inject the real tool output — a real bug class, not a lab-only concern.
- **Q: Why does the system prompt tell the model to treat Observation content as untrusted?**
  A: Observations can contain adversarial or scraped content (e.g. a search result with embedded instructions) — without that framing, the model might follow instructions hidden inside tool output instead of just reasoning about it, a prompt-injection risk.
- **Q: What are the three steps of the ReAct loop?**
  A: Thought (reason about what to do next) → Action (request a tool call) → Observation (the result, fed back in) — repeated until a Final Answer is produced or the iteration cap is hit.

### reflection-pattern

- **Q: What does reflection check that the stage-03 structured-output repair loop doesn't?**
  A: Repair checks shape (valid JSON, right types); reflection checks whether the answer actually satisfies the goal given the evidence gathered — a shape-valid answer can still be substantively wrong.
- **Q: Why cap reflection at exactly one revision cycle instead of looping until `APPROVED`?**
  A: Same reasoning as capping ReAct's iterations — bounded cost and risk. Additional critique rounds have diminishing accuracy payoff and the same runaway-loop risk as any uncapped agentic loop.
- **Q: What should happen if the reflection pass itself can't run (no key, outage)?**
  A: Fail open — skip the critique and return the original draft with a plain `"SKIPPED"` label, rather than fabricating a fake `APPROVED` or blocking the whole pipeline on a broken quality-improvement step.

## Harder / real-interview-style

Scenario-based questions on autonomy, the agentic loop, tool schemas, ReAct, and reflection — the kind that probe whether you can justify a design choice under pushback, not just define a pattern. Grounded in current (2025-2026) agentic-AI interview practice ([Interview Coder — Agentic AI](https://www.interviewcoder.co/blog/agentic-ai-interview-questions), [dev.to ReAct/Plan-Execute/Reflection](https://dev.to/gabrielanhaia/react-plan-and-execute-or-reflection-the-three-agent-patterns-every-engineer-needs-in-2026-355p), [dev.to 7 agentic design patterns](https://dev.to/emperorakashi20/the-7-agentic-ai-design-patterns-every-developer-should-know-react-reflection-tool-use-and-more-3bba)) and this repo's own [[workflow-vs-agent-autonomy-spectrum]], [[agentic-loop-fundamentals]], [[tool-calling-fundamentals]], [[react-pattern]], [[reflection-pattern]].

#### Workflow vs. agent: justifying the autonomy call

- **Q: A product manager insists "make it an agent, agents are more impressive to demo." The task is "refund an order if it's within 30 days and under $50, else escalate." How do you push back, concretely?**
  A: This task's steps and their order are fully knowable ahead of time — check date, check amount, branch two ways — which is the textbook signature of a workflow, not an agent (see [[workflow-vs-agent-autonomy-spectrum]]). Building it as an agent means paying agent costs (unpredictable execution paths, more tokens/latency per decision, a much larger test surface since the model chooses the path rather than your code) for zero benefit, because there's no discovery-dependent branching for autonomy to actually earn its keep on. The concrete pushback: name the exact steps and their fixed order back to the PM, and ask them to name a realistic case where the *next* step isn't already determined by the first two checks — if they can't, it's a workflow.
- **Q: Give a realistic example where a task that looks like "just conditionals" is actually a legitimate case for agent autonomy.**
  A: A refund-eligibility check that also has to interpret a *freeform customer complaint* to decide whether it's actually a shipping-damage claim (different policy path), a duplicate charge (different tool), or a change-of-mind return (the "simple" path) — the next step here depends on something only discoverable by reading and classifying unstructured text mid-task, which a fixed workflow can't branch on without effectively re-implementing an LLM classifier inline. That's the actual signal: not "this involves an LLM" or "this feels complex," but "the next action depends on a mid-task discovery a human would have to read to make."
- **Q: Why might an experienced engineer deliberately build something *as* an agent even when the steps are mostly fixed, accepting the extra cost?**
  A: When the fixed-step assumption is fragile — policy/business rules change often enough that hardcoding the branch logic into workflow code means a code deploy every time a rule changes, whereas an agent reading current policy (via RAG) and reasoning about the branch adapts without a redeploy. This is a real tradeoff, not a free win: you're trading workflow's cheaper/more-testable execution for the agent's adaptability to a fast-changing rule set — worth stating explicitly rather than treating "agent" as strictly the more advanced/better choice.

#### The agentic loop and tool-calling mechanics

- **Q: An agent's loop has no iteration cap. Under what realistic condition does it actually run away, and what's the cheapest fix that doesn't just lower a hardcoded number?**
  A: It runs away when a tool consistently returns a result the model interprets as "not yet done" — e.g. a search tool returning irrelevant results the model keeps re-querying, or a flaky tool returning transient errors the model keeps retrying itself instead of surfacing. A hardcoded max-iteration cap stops the bleeding but doesn't fix the cause; a better layered fix combines a hard cap (safety net) with detecting *repeated identical or near-identical tool calls* within the loop (a real signal of "the model is stuck," not just "the task needs many steps") and forcing an early exit/escalation when that pattern appears.
- **Q: Who validates a tool call's arguments before execution — is Pydantic schema validation on the tool call sufficient?**
  A: Schema validation (right types, required fields present) is necessary but not sufficient — it catches a malformed call, not a *dangerous* or *out-of-scope* one, e.g. a syntactically valid `refund_amount: 50000.0` that's absurd for a $30 order. Your application code, not the model and not the schema layer alone, is responsible for a second business-rule check before actually executing a consequential tool call — this is the same "structural vs. semantic validation" gap that shows up in stage 03's repair loops, applied to tool execution instead of output parsing.
- **Q: A tool's JSON schema is airtight (correct types, tight enums, required fields) but the agent still calls the wrong tool at the wrong time. What's actually broken, and why does fixing the schema not fix it?**
  A: The schema constrains *arguments once a tool is chosen* — it says nothing about *when* to choose it. The model decides which tool to reach for based on the tool's `description` field (and the surrounding system prompt), so a vague or overlapping description is a much more common root cause of wrong-tool-at-wrong-time than a schema defect — this is the "description is the highest-leverage, most-neglected field" problem, and no amount of schema tightening fixes a decision-time mistake the model makes before argument-filling even happens.

#### ReAct and reflection in production

- **Q: A ReAct agent's `stop=["Observation:"]` sequence is accidentally removed during a refactor. What specific failure mode should you expect to see in production, and how would you notice it from logs alone?**
  A: Without that stop sequence, nothing prevents the model from generating its own fake `Observation:` text and continuing to reason off an invented result instead of waiting for your code to inject the real tool output — the model essentially hallucinates the outcome of an action it never actually took. In logs, this shows up as a single completion containing a full Thought → Action → *and* Observation in one generation (instead of the loop properly stopping after Action, executing the tool, and feeding a real observation back in on the next call) — a suspiciously "complete-looking" single-shot response is the tell.
- **Q: Why would you frame tool/observation output as "untrusted" in a ReAct agent's system prompt even when your own tools are fully trusted and controlled?**
  A: The risk isn't your tool's code — it's the *content* a trusted tool can return, e.g. a search tool returning a scraped web page, or a policy-RAG tool returning a document, either of which could contain adversarial text engineered to look like an instruction ("ignore previous instructions and...") embedded in otherwise-legitimate content. Framing observations as untrusted data to reason *about*, not instructions to *follow*, is a prompt-injection defense that matters regardless of how trustworthy the tool's code itself is, because the vulnerability is in what the tool's data source can contain, not in the tool call mechanism.
- **Q: A reflection pass is added after a ReAct loop's final answer. What specific failure class does it catch that a well-tuned ReAct loop with a good stop condition doesn't already prevent?**
  A: ReAct's loop termination (stop condition, iteration cap) only checks *whether the model believes it's done* — it says nothing about whether the final answer is actually correct given the evidence gathered along the way. A reflection pass adds an explicit second look asking "does this answer actually follow from the observations collected," catching a confidently-stated but unsupported or logically inconsistent conclusion that a shape-valid, schema-valid, loop-terminated response would otherwise ship as-is — this is the same "shape-valid isn't goal-valid" gap that separates structured-output repair (stage 03) from semantic correctness.
- **Q: Reflection adds a second LLM call (and doubles latency/cost) for every response. How would you decide whether that's worth it for a given agent, rather than applying it uniformly?**
  A: Apply it where the cost of a wrong answer materially exceeds the cost of one extra call — high-stakes or hard-to-reverse actions (a refund decision, an escalation classification, a policy-sensitive response) — and skip it for low-stakes, easily-corrected, or already-well-validated outputs (a simple FAQ lookup already grounded in retrieved text). This is the same class of reasoning as the workflow-vs-agent autonomy call above: reflection is a cost you deliberately pay where the risk profile justifies it, not a default you bolt onto every agent regardless of what's actually at stake in a wrong answer.
