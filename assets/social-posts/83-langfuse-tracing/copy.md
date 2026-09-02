--- LINKEDIN ---
"The agent gave a wrong answer, 14 seconds, no error" isn't debuggable on its own. Without tracing, a multi-agent run only shows the final state — you can't tell which agent produced the bad value or which step ate the latency. A trace is one end-to-end run as a tree of spans, and opening a span inside code already running inside another span nests it automatically — Langfuse follows the Python call stack, you never pass a span object by hand.

def traced(role):
    def decorator(fn):
        def wrapper(state):
            with langfuse.start_as_current_observation(as_type="span", name=f"agent:{role}") as span:
                result = fn(state)
                span.update(input=state.get("plan"), output=sorted(result))
                return result
        return wrapper
    return decorator

Cost only exists once real tokens are spent. A deterministic node with no LLM call legitimately has no cost figure — it should read as absent, not zero. A generation span specifically needs model and usage_details wired from the actual response object, because the SDK's built-in price table can't reliably resolve every provider-prefixed model name.

Production gotcha: the SDK fails silently by design if LANGFUSE_PUBLIC_KEY/SECRET_KEY are missing — check auth_check() first, rather than assuming a config problem elsewhere.

The real incident worth internalizing: a blanket "wrap the whole function" tracing decorator that repr()s its arguments put the customer's raw chat message onto every node's span, every single turn. It was initially missed because the decorator had been applied as a plain call rather than @traced_node, so a grep for decorator syntax found nothing. The fix was an explicit redact-keys allowlist that blanks free-text fields before the repr runs, while routing/audit fields stay visible.

Any tracing layer that captures "whatever's in scope" rather than named, reviewed fields is a PII leak waiting on the next field someone adds to shared state.

Does your tracing decorator capture named fields, or whatever happens to be in scope?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
"Wrong answer, 14 seconds, no error" isn't debuggable. Tracing fixes that. 🌳

Spans nest automatically by following the Python call stack — no manual span-passing.

Cost only exists once real tokens are spent. A pure-code node should show no cost, not zero.

Real incident: a blanket repr() decorator leaked raw customer chat text onto every span, every turn.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "\"Wrong Answer, 14 Seconds, No Error\" Isn't Debuggable"
2. The fix — a tree of timed, inspectable spans (diagram)
3. Sample code — a span that survives failure (code)
4. Cost accounting — cost only exists once real tokens are spent
5. Production gotcha — fails silently by design on a missing key
6. The real incident — a repr() decorator leaked raw chat text onto every span
7. Takeaway — redact named fields, never capture "whatever's in scope" (closing question)
