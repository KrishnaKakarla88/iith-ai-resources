--- LINKEDIN ---
JSON mode guarantees a response parses as JSON. Pydantic catches whether the values inside are sane. Both already do their job correctly on their own — the harder question is what happens the moment one of them actually fails.

The naive move is asking again and hoping. The better move is the repair loop: hand the model its own mistake. The repair prompt carries the actual ValidationError text — which field, what rule, what value — plus the original input and the model's previous failed attempt. That's the smallest possible agentic loop: generate, validate, observe the failure, act, repeat.

Cap it at 2-3 attempts — cost, and some inputs are legitimately unparseable no matter how many tries. Hit the cap and fail loudly to a human, rather than letting unvalidated data flow through silently.

A refund tool call can be syntactically perfect JSON with an amount of -9999999. Shape and value checks alone buy nothing once execution is the next step without a repair layer behind them.

Do you cap repair retries, or loop until it succeeds?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Detecting a bad value isn't the hard part. 📋

JSON mode + Pydantic already catch shape and value. The real question: what happens the moment one fails?

The repair loop hands the model its own mistake back — the error, the input, the failed attempt. Not just "try again."

Capped at 2-3 attempts, then escalate. Never let unvalidated data flow through silently.

Full mechanism in the carousel.

Do you cap repair retries, or loop until success?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "JSON Mode Isn't Validation"
2. Building on — detecting a bad value isn't the hard part
3. Core mechanics — the repair loop (diagram)
4. What gets sent back — the error, not another guess (code)
5. Discipline — cap the retries, escalate on exhaustion
6. Takeaway — checking values is a separate job (closing question)
