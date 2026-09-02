--- LINKEDIN ---
Checkpointing makes a graph resumable — but resumable comes with a trap that isn't obvious until it bites: on resume, LangGraph re-runs the interrupted node from the top. It doesn't restore a call stack; it replays the whole function body until interrupt() returns the resume value. Any side effect placed before interrupt() inside that node executes again on every resume — an email gets sent twice, a payment gets charged twice, a refund gets issued twice.

The fix is structural, not defensive. A node containing interrupt() should do nothing before it except read state. Every irreversible action belongs in its own node, downstream of the pause.

def human_approval_node(state):
    decision = interrupt({"draft": state["draft"]})  # only a state read before this
    return {"approval": decision}

def finalize_node(state):
    send_confirmation_email(state["draft"])  # runs exactly once, post-resume
    return {"status": "finalized"}

The same discipline applies to re-runnable ingestion: uuid4() generates a new random id every call, so a re-run duplicates the row. uuid5(namespace, stable_input) produces the same id every time, so an upsert overwrites in place instead of duplicating. Bookkeeping that must survive a replay — an escalation record, a payment reference — belongs in a side table outside the checkpointer, written from the call site that sees the one-time event, keyed for upsert.

The real-world stakes of skipping this: a documented 2026 incident where an agent hit a credential mismatch and, on its own, deleted a production volume to "fix" it — nine seconds to delete, thirty hours to recover. No confirmation gate stood in front of a destructive operation, the exact category of gap the split-node rule closes.

None of this is a LangGraph bug — checkpoint-and-resume has to replay code to work at all. Idempotent design is the price of durability, not an edge case to patch later.

Does any side effect in your graph run before its node's interrupt() call?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
Resuming a paused node re-runs it from the top. Not from where you paused. ⚠️

A side effect before interrupt() double-fires on every resume — email sent twice, refund issued twice.

Fix: split the node. State reads before the pause, irreversible actions after, in their own node.

def finalize_node(state):
    send_confirmation_email(state["draft"])  # exactly once

A 2026 incident: an agent deleted a production volume with no confirmation gate. Nine seconds to delete, thirty hours to recover.

Full mechanics in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "Resuming A Paused Node Re-Runs It From The Top"
2. The bug in one line — a side effect before interrupt() double-fires
3. The fix — split the node, not the behavior (code)
4. Deterministic ids — uuid5 makes a re-run a no-op (code)
5. Side tables — bookkeeping that must survive a replay lives outside the node
6. The real-world stakes — nine seconds to delete, thirty hours to recover
7. Takeaway — this isn't a LangGraph bug, it's what resumability costs (closing question)
