--- LINKEDIN ---
A LangGraph node does not return the whole state — it returns a partial update, just the keys it touched. The engine merges that partial dict into the running state using a per-key reducer. The default reducer, if you don't specify one, is "last write wins" — exactly right for a routing decision, exactly wrong for a running list of messages.

class ApprovalState(TypedDict):
    draft: str                            # overwrite
    issues: list[str]                     # overwrite — control field
    issue_log: Annotated[list[str], add]  # accumulate — audit trail
    revision_count: int                   # overwrite

The design pattern that follows directly from this: control fields vs. audit fields. A field a conditional edge reads to decide what happens next has to stay overwrite-only, or it never becomes empty again once anything has ever failed — the router would loop forever reading stale history. A separate accumulate field preserves the full history for debugging without corrupting the field the router actually depends on.

The crash guard worth knowing about: if two nodes write the same key in the same superstep and it has no reducer, LangGraph raises InvalidUpdateError — the engine refuses to silently pick a winner between two conflicting writes.

Production gotcha: a TypedDict isn't runtime-validated. A misspelled key in a node's return value silently creates a dead channel nothing ever reads, rather than raising an error. Print or inspect state after every node during development — that's what actually catches it.

Facts the graph acts on are control fields. Everything the graph remembers for a human or a trace is an audit field. Mixing the two is the most common state-design bug.

Does your router read a field that also silently accumulates history?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
A node never returns the whole state. Just what it touched. 🧩

Default reducer: last write wins. Fine for a routing decision. Wrong for a message list.

class ApprovalState(TypedDict):
    issues: list[str]                     # overwrite, control field
    issue_log: Annotated[list[str], add]  # accumulate, audit trail

Mix the two and your router loops forever reading stale history.

Full breakdown in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A Node Returns A Partial Update, Never The Whole State"
2. Core mechanics — default reducer is last write wins (code)
3. The design pattern — control fields vs audit fields
4. The crash guard — two nodes, same key, no reducer
5. Production gotcha — a TypedDict is not runtime-validated
6. Takeaway — facts the graph acts on are control fields (closing question)
