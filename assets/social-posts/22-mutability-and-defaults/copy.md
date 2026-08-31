--- LINKEDIN ---
Python's mutable-default-argument bug is a common interview trap for a reason — it doesn't fail loudly.

A default argument value is evaluated once, at function-definition time, not on every call. A function like log_event(event, history=[]) looks like it hands back a fresh empty list per call. It doesn't — every call that skips the history argument shares the exact same list object.

log_event("a") returns ['a']. log_event("b") returns ['a', 'b'] — the previous call's data leaked in, with no exception raised anywhere.

The fix: default to None, then build the real list inside the function body on every call.

The mechanism behind why this happens — and why is and == give different answers for two lists that look identical — is in the carousel.

Any list, dict, or set sitting as a default argument value is worth a second look.

Have you hit this bug in production, or only in an interview?

#AppliedAI #Python #LLM #AIEngineering

--- INSTAGRAM ---
Python's sneakiest bug hides in a function signature.

A default like history=[] looks like a fresh empty list every call. It isn't — that list gets created once, not per call, so every call sharing it mutates the same object. 🐍

Fix: default to None, build the real list inside the function body.

Full breakdown + the is vs == mechanism behind it, in the carousel.

Where has this bitten you?

#AppliedAI #Python #LLM #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Mutability In Python" (concept framing)
2. Concept — Mutable vs Immutable definitions
3. Mechanism — is vs == (code: a==b True, a is b False)
4. The Bug — shared default list (code: leaked list)
5. The Fix — default to None (code: the fix line)
6. Takeaway + closing question
