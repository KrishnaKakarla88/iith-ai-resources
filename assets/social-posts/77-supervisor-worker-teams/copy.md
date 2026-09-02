--- LINKEDIN ---
A team of five specialists sharing one state dict looks harmless until a specialist reads a field it was never meant to see, or writes over a field another specialist depends on. Read scoping and write scoping are the two mechanisms that turn "shared state" into "state each agent has a contract with."

Read scoping is the one that actually earns multi-agent's cost. Each agent gets only its own state slice, not the whole dict — not an optimization, but what makes specialization real. A Fact-Checker that can read the Writer's brief can be talked into rationalizing a citation it would otherwise reject; one that only ever sees {draft, findings} has no brief to be persuaded by.

WRITE_SCOPES = {
    "fact_checker": {"fact_check", "log"},
    "reviewer": {"review", "log"},
    "writer": {"draft", "fact_check", "review", "log"},
}

def _check(role, update):
    illegal = set(update) - WRITE_SCOPES[role]
    if illegal: raise PermissionError(f"{role} wrote out-of-scope keys: {illegal}")

A decorator checks a node's returned keys against a per-role allowlist and raises before the update ever reaches the graph's reducer. The Writer's own entry looks like a violation of least privilege — until you notice fact_check and review deliberately have no reducer. They're control fields the Writer must reset to {} on every revision, because a rewrite voids prior approval; a field that only accumulates can't represent "not yet re-approved."

Why two critics instead of one stronger one: a Fact-Checker runs a deterministic regex check over citation tags — the code check is the verdict. A Reviewer requires an objective structural floor AND LLM-judge agreement, never OR — a judge alone can be argued around, a structural check alone can't catch a plausible-sounding fabrication.

Production gotcha: a @scoped decorator that doesn't branch on inspect.iscoroutinefunction silently stops enforcing scope the moment a node becomes async.

Proven directly in the lab: swapping in a hallucinating writer that plants a fake citation shows the read-scope boundary working — the Fact-Checker, never having seen the brief, can't be talked round.

Could any specialist in your team see a field that lets it rationalize a bad answer?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
Your Fact-Checker can see the Writer's brief. That's the bug. 🔍

Read scoping: each agent sees only its own state slice. A Fact-Checker with no brief has nothing to rationalize a fake citation against.

WRITE_SCOPES = {"fact_checker": {"fact_check", "log"}, ...}

Two critics, not one — a deterministic check AND an LLM judge, never OR.

Full mechanics in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "A Fact-Checker That Can See The Brief Can Be Talked Round"
2. Read scoping — the mechanism that actually earns multi-agent's cost
3. Sample code — write-scopes enforced before the reducer (code)
4. The deliberate exception — control fields need no reducer, on purpose
5. Why two critics, not one
6. Production gotcha — an async node silently bypasses a sync-only guard
7. Takeaway — proven directly: a hallucinating writer plants a fake citation (closing question)
