--- LINKEDIN ---
Functions in Python are ordinary objects — they can be passed around and returned from other functions. A decorator takes advantage of that: it accepts a function and returns a new function wrapping it. @my_decorator above a function is shorthand for my_function = my_decorator(my_function) — this exact mechanism is how retry, circuit-breaker, and tracing get bolted onto agent functions without touching their own code.

A parameterized decorator (@retry_with_backoff(max_retries=3)) needs three nested function levels: the outer accepts the decorator's own arguments and returns the actual decorator, which returns wrapper — the function that runs at call time.

Skip @functools.wraps(fn) on wrapper and every decorated function's __name__ and docstring get replaced with the generic wrapper's — not cosmetic when FastMCP reads a tool's name/docstring to build its JSON schema.

Stacking order matters too: retry innermost, circuit breaker outermost, so a burst of retried-but-still-failing calls is what actually trips the breaker.

Which decorator order has surprised you the first time you saw it?

#AppliedAI #Python #LLM #AIEngineering

--- INSTAGRAM ---
Decorators wrap a function without touching its code. 🎁

@my_decorator above a function is shorthand for my_function = my_decorator(my_function) — same mechanism behind retry, circuit-breaker, and tracing on every agent function.

Skip @functools.wraps(fn) and FastMCP reads the wrong name/docstring for a tool's schema.

Stacking order even changes what a trace records — full breakdown in the carousel.

Which decorator order surprised you?

#AppliedAI #Python #LLM #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Decorators: Wrap Without Touching"
2. A function that wraps a function (code)
3. Three nested levels, one reason (code)
4. Gotcha — forgetting functools.wraps (code)
5. Production rule — stacking order changes the meaning (code)
6. Takeaway + closing question
