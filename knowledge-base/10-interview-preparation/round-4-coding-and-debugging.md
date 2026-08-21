# Round 4 — Coding & Debugging

This round is code review, not trivia — read each snippet the way you'd read a teammate's PR, spot the one deliberate bug or missing edge case, then explain the fix and *why* it matters, not just what line to change. Each snippet is grounded in a real pattern from this stack; several are lightly fictionalized versions of documented bugs from `labs/production-notes.md`. Try to spot the bug yourself before reading the answer.

---

## Exercise 1 — The retry wrapper that "fixes" the wrong thing

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.5, max=8))
def search_kb(topic: str) -> list[dict]:
    """Query the policy knowledge base. May raise or return malformed records."""
    response = flaky_kb_client.query(topic)
    return response.records
```

**What's wrong?**

`@retry` here catches *every* exception by default (no `retry=retry_if_exception_type(...)` filter), so it will retry a `ValueError` from a malformed query just as eagerly as a `ConnectionError` from a dropped socket — burning the retry budget on a bug that will produce the exact same wrong result four times in a row. Worse: it doesn't handle the case where `flaky_kb_client.query()` succeeds (no exception) but returns records missing required fields — that's not caught by any exception-based retry at all, since nothing raised.

**What would you change?**

Two separate fixes for two separate failure classes: `retry_if_exception_type((ConnectionError, TimeoutError))` so only genuinely transient failures get retried and everything else re-raises immediately (add `reraise=True` too — tenacity's own `RetryError` wrapper otherwise hides the original exception type from the caller). Then add a *separate* validation step after the call succeeds — `if not all("text" in r for r in records): return fallback` — because malformed-but-successful data is a different failure mode that retrying does nothing for; it needs a fallback path, not another attempt.

**Follow-up interviewers ask**: "Would jittered backoff matter here?" — yes, if this function is called from many concurrent requests, `wait_exponential` without jitter can synchronize many clients into retrying at the same moment (a thundering herd against a struggling dependency); `wait_random_exponential` (Full Jitter) randomizes the wait within the widening window instead.

**Related**: [[retry-fallback-patterns]]

---

## Exercise 2 — The LangGraph node that double-charges

```python
def process_refund_node(state: RefundState) -> dict:
    issue_refund(state["order_id"], state["amount"])   # calls the payment provider

    decision = interrupt({
        "order_id": state["order_id"],
        "amount": state["amount"],
        "prompt": "Confirm this refund was issued correctly?",
    })

    return {"refund_confirmed": decision["confirmed"], "status": "done"}
```

**What's wrong?**

`interrupt()` pauses the graph and, on resume, LangGraph does not restore an in-flight call stack — it **re-runs the entire node function body from the top** until `interrupt()` returns the resume value. `issue_refund(...)` sits *before* the `interrupt()` call, so it executes once on the original run and executes **again** on every resume. A human reviewing and confirming this refund causes the actual refund API to be called a second time — a real, billable double-fire, not a hypothetical one.

**What would you change?**

Split the node in two: the node that calls `interrupt()` should do nothing but read state and pause; the actual irreversible action (`issue_refund`) belongs in a separate, downstream node that only runs *after* the interrupt resolves:

```python
def confirm_refund_node(state: RefundState) -> dict:
    decision = interrupt({"order_id": state["order_id"], "amount": state["amount"]})
    return {"approval": decision}

def issue_refund_node(state: RefundState) -> dict:
    issue_refund(state["order_id"], state["amount"])   # runs exactly once, only post-resume
    return {"status": "done"}

builder.add_edge("confirm_refund", "issue_refund")
```

**Follow-up interviewers ask**: "How would you make `issue_refund` itself safe even if this bug somehow still happened?" — a deterministic idempotency key derived from stable inputs (`uuid5(NAMESPACE, f"{order_id}:{amount}:{approval_timestamp}")`) passed to the payment provider, so a second call with the same key is a no-op rather than a second charge — defense in depth on top of, not instead of, the node split.

**Related**: [[idempotency-and-side-effects]], [[langgraph-checkpointing-hitl]]

---

## Exercise 3 — The tool-calling loop that trusts the wrong thing

```python
def run_agent(messages: list, max_iterations: int = 6) -> str:
    tool_by_name = {t.name: t for t in TOOLS}
    for _ in range(max_iterations):
        response = model.invoke(messages)
        messages.append(response)

        if "I called" in response.content or "I checked" in response.content:
            return response.content   # model says it already did the work

        for tc in response.tool_calls:
            result = tool_by_name[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    return "Sorry, I couldn't complete that request."
```

**What's wrong?**

The early-return check (`"I called" in response.content`) drives control flow off the model's *prose*, not off the structured `tool_calls` field. A model can narrate "I checked the weather and it's 31°C" without any corresponding entry in `response.tool_calls` — a real, documented failure mode where the model describes an action it never actually took. This code would return that narrated-but-unexecuted answer as if it were grounded, with no tool ever having run. There's a second bug too: if `response.tool_calls` is empty and the narration check doesn't match, the `for tc in response.tool_calls` loop silently does nothing and the loop just spins to the next iteration with no new information added to `messages` — no guaranteed forward progress.

**What would you change?**

Drive every branch off the structured field, never the text: `if not response.tool_calls: return response.content` (this is the correct, and only, way to detect "the model gave a final answer with no more tool calls needed"). Delete the prose-matching branch entirely — it's not a valid signal for anything.

```python
def run_agent(messages: list, max_iterations: int = 6) -> str:
    tool_by_name = {t.name: t for t in TOOLS}
    for _ in range(max_iterations):
        response = model.invoke(messages)
        if not response.tool_calls:
            return response.content
        messages.append(response)
        for tc in response.tool_calls:
            result = tool_by_name[tc["name"]].invoke(tc["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    raise RuntimeError("max_iterations exceeded without a final answer")
```

Note the other fix riding along: exhausting `max_iterations` now raises instead of returning a silent, unlogged apology string — a caller (or a golden-set eval run) needs to be able to tell "the agent answered" apart from "the agent gave up," and a friendly string in both cases erases that distinction.

**Related**: [[tool-calling-fundamentals]], [[agentic-loop-fundamentals]]

---

## Exercise 4 — The eval harness that loses everything on one bad call

```python
def component_scorer(item: dict, trace: dict) -> dict:
    scores = {}
    scores["tool_match"] = tool_match_score(item, trace)
    scores["retrieval"] = retrieval_score(item, trace)
    scores["faithfulness"] = ragas_faithfulness_judge(item, trace)   # network call, rate-limited
    scores["guardrail"] = guardrail_check(trace)
    return scores
```

**What's wrong?**

Under sustained rate limiting, `ragas_faithfulness_judge` (a real network call to a judge model) can exhaust its own retry budget and raise. Because there's no isolation around it, that single exception propagates out of `component_scorer` and discards every score already computed for this item — `tool_match`, `retrieval`, and critically `guardrail` are all lost, because Python doesn't return partial results from a function that raised partway through. For a batch eval run over an entire golden set, one rate-limited judge call silently drops the *safety* check for that item too, not just the quality score — and if the caller doesn't re-raise loudly, that item just quietly has no row in the results table at all.

**What would you change?**

Isolate every scorer that can independently fail — especially anything making a network call — behind its own `try/except`, so one scorer's failure degrades to a `None`/error marker for that metric alone, without discarding the others:

```python
def component_scorer(item: dict, trace: dict) -> dict:
    scores = {}
    scores["tool_match"] = tool_match_score(item, trace)
    scores["retrieval"] = retrieval_score(item, trace)
    try:
        scores["faithfulness"] = ragas_faithfulness_judge(item, trace)
    except Exception as e:
        scores["faithfulness"] = None
        scores["faithfulness_error"] = str(e)   # visible in the results table, not silently dropped
    scores["guardrail"] = guardrail_check(trace)   # always runs — safety isn't quality-conditional
    return scores
```

**Follow-up interviewers ask**: "Why does the guardrail check need to run regardless of what happened above it?" — because safety isn't quality-conditional: a judge call failing for rate-limit reasons has nothing to do with whether this response was safe to have returned, and an eval harness that lets an unrelated exception silently skip the guardrail check is a coverage gap in exactly the check you can least afford to lose.

**Related**: [[eval-driven-development-mindset]], [[llm-judges-eval]], [[guardrails-injection-detection]]

---

## Exercise 5 — The circuit breaker that never really opens

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.state = "closed"
        self.opened_at = None

    def call(self, fn, *args, **kwargs):
        if self.state == "open":
            if time.monotonic() - self.opened_at >= self.reset_timeout:
                self.state = "half_open"
            else:
                raise CircuitOpenError("circuit open")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "open"
                self.opened_at = time.monotonic()
            raise
        else:
            self.failures = 0
            self.state = "closed"
            return result
```

**What's wrong?**

Look at the `except` branch: it only opens the circuit when `self.failures >= self.failure_threshold`. But once the breaker has already tripped to `half_open` and lets exactly one trial call through, a *single* failure on that trial call should immediately re-open the circuit — the whole point of `half_open` is that one failure proves the dependency is still down. Here, if `self.failures` was reset to some value below `failure_threshold` on an earlier partial recovery, a single failed trial call in `half_open` just increments the counter and falls through to `closed` behavior (or stays open only if the running total happens to cross the threshold again) — it can take several more failed trial calls before the breaker re-opens, during which every one of those trial calls is a real, un-short-circuited hit against a dependency that's already been proven still-down by the very first trial failure.

**What would you change?**

Any failure while `half_open` must re-open immediately, unconditionally — it's not "one more failure toward the threshold," it's proof positive the trial failed:

```python
        except Exception:
            self.failures += 1
            if self.state == "half_open" or self.failures >= self.failure_threshold:
                self.state = "open"
                self.opened_at = time.monotonic()
            raise
```

**Follow-up interviewers ask**: "What's the risk of testing this bug in review versus catching it live?" — this is exactly the kind of bug that looks fine in a demo (a clean binary "up" or "down" dependency) and only shows its teeth against a *partially* recovering dependency that flaps between working and failing — precisely the shape real outages take, which is why seeded fault injection at a realistic (not 0%-or-100%) failure rate is worth pushing for in code review, not just a full-outage smoke test.

**Related**: [[circuit-breaker-pattern]]

---

## Exercise 6 — The guardrail that only catches half the placeholder answers

```python
from pydantic import BaseModel, Field, field_validator

class AgentResponse(BaseModel):
    route: str
    final_answer: str = Field(min_length=1, max_length=2000)

    @field_validator("final_answer")
    @classmethod
    def reject_placeholder(cls, v: str) -> str:
        if v in {"", "n/a", "todo", "..."}:
            raise ValueError("final_answer is a placeholder")
        return v
```

**What's wrong?**

Two independent gaps. First, `route: str` has no constraint at all — any string the model produces passes, including a hallucinated value like `"escalate_to_manager"` that no downstream code branch actually handles; a schema is supposed to be a guardrail here, and an unconstrained `str` field isn't one. Second, the placeholder check does an exact-match comparison against a fixed set (`v in {"", "n/a", ...}`) with no normalization — `"N/A"`, `" n/a "` (trailing whitespace), or `"N/A."` all sail through as if they were real answers, because the model doesn't reliably produce placeholder text in exactly the lowercase, untrimmed form the set expects.

**What would you change?**

Constrain `route` to the actual fixed set of valid values with `Literal[...]`, and normalize before comparing the placeholder set:

```python
from typing import Literal

class AgentResponse(BaseModel):
    route: Literal["tool", "retrieval", "direct"]
    final_answer: str = Field(min_length=1, max_length=2000)

    @field_validator("final_answer")
    @classmethod
    def reject_placeholder(cls, v: str) -> str:
        if v.strip().lower() in {"", "n/a", "todo", "..."}:
            raise ValueError("final_answer is a placeholder, not a real response")
        return v
```

**Follow-up interviewers ask**: "Where would you *also* enforce the valid-route set, besides this Pydantic model?" — the strong answer names defense in depth: a graph-layer check on the router's actual structural output, mirroring this schema-layer check, so a single missed enforcement point doesn't let a bad route slip all the way to a user-facing branch — the lab's own production notes cite a case where exactly this kind of duplicated check (not a single point of enforcement) is what actually caught a real incident.

**Related**: [[guardrails-injection-detection]]

---

## Exercise 7 — The auth check that trusts the wrong input

```python
def handle_order_lookup(session, user_message: str) -> dict:
    match = re.search(r"order[:\s#]*(\d+)", user_message, re.IGNORECASE)
    if not match:
        return {"error": "Please provide an order number."}
    order_id = match.group(1)
    order = orders_db.get(order_id)
    if order is None:
        return {"error": "Order not found."}
    return {"order": order.to_dict()}
```

**What's wrong?**

There's no ownership check at all — `order_id` is extracted straight from free text the *user* typed, and whatever order that ID belongs to is returned, regardless of whether the session's authenticated customer actually owns it. A user (malicious or just fat-fingering) who types `"what's the status of order 4471"` gets order 4471's full details back even if 4471 belongs to a different customer entirely. This is exactly the failure mode of deriving identity/authorization from message text: the text is attacker-controlled input, not proof of ownership.

**What would you change?**

Resolve the acting customer from the authenticated session (never from the message), and check ownership before returning anything:

```python
def handle_order_lookup(session, user_message: str) -> dict:
    if not session.is_authenticated:
        raise AuthError("no authenticated session")
    customer_ref = session.customer_ref          # from the session, never parsed from text

    match = re.search(r"order[:\s#]*(\d+)", user_message, re.IGNORECASE)
    if not match:
        return {"error": "Please provide an order number."}
    order_id = match.group(1)

    order = orders_db.get(order_id)
    if order is None or order.owner_ref != customer_ref:
        # same generic message either way — don't leak whether the order exists at all
        return {"error": "This order isn't associated with your account."}
    return {"order": order.to_dict()}
```

**Follow-up interviewers ask**: "Why return the same error message for 'order doesn't exist' and 'order exists but isn't yours'?" — a distinguishable message (or even a distinguishable status code) leaks information to someone probing IDs: if "not found" and "not yours" read differently, an attacker can enumerate valid order IDs belonging to other customers just by watching which response they get, without ever seeing the order's actual contents.

**Related**: [[auth-and-multi-tenancy]]

---

## Exercise 8 — The tracing decorator that leaks the whole conversation

```python
import functools

def traced_node(name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(state):
            span.update(input=repr(state), output=None)
            result = fn(state)
            span.update(output=repr(result))
            return result
        return wrapper
    return decorator

traced_check_document = traced_node("check_document")(check_document)
```

**What's wrong?**

`repr(state)` captures *everything* currently in the state dict, unconditionally — including whatever free-text fields happen to be there, like the customer's raw chat message or draft response text. Every node wrapped this way puts the full, unredacted conversation onto every span, every turn. It's also applied as a plain call (`traced_node(name)(fn)`, not `@traced_node`) — worth noticing because a grep for `@traced_node` decorator syntax across the codebase would find nothing, even though the wrapping is very much happening; a reviewer scanning for "which functions have tracing applied" using decorator syntax alone would miss this call site entirely.

**What would you change?**

Redact known free-text fields *before* the repr runs, using an explicit allowlist-of-what's-blocked (or better, an allowlist-of-what's-safe) rather than capturing the state dict wholesale:

```python
REDACT_KEYS = {"customer_message", "raw_chat_history", "draft"}

def safe_repr(state: dict) -> dict:
    return {k: ("[REDACTED]" if k in REDACT_KEYS else v) for k, v in state.items()}

def traced_node(name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(state):
            span.update(input=safe_repr(state))
            result = fn(state)
            span.update(output=safe_repr(result))
            return result
        return wrapper
    return decorator
```

**Follow-up interviewers ask**: "Is a denylist (`REDACT_KEYS`) actually the safer choice here, or would an allowlist be better?" — a strong answer flags the denylist's own weakness even in the fix: it only catches fields someone remembered to add to the set; a newly added free-text field leaks by default until someone notices and adds it. An allowlist (`SAFE_KEYS`, everything else redacted) inverts that failure mode — new fields are blocked by default until explicitly marked safe — and is the more defensible design for a state dict that keeps growing as the agent gets more capable.

**Related**: [[privacy-and-pii-handling]], [[langfuse-tracing]]

---

## Sourcing

Snippets are original, written to exercise real bug patterns documented in `labs/production-notes.md` and this KB's `09-production-readiness`/`08-multi-agent-systems`/`07-orchestration` pages (retry/circuit-breaker composition, LangGraph re-run-from-top on resume, narrated-vs-executed tool calls, eval-harness partial-failure isolation, guardrail schema gaps, auth/identity-from-text, and the tracing-decorator PII leak) — cross-checked against current library APIs (tenacity 9.x, LangGraph 1.2.x `interrupt()`/`Command(resume=...)`, pydantic v2) per this repo's pins, plus general 2025-2026 practice on agentic-AI code-review/debugging interview formats.
