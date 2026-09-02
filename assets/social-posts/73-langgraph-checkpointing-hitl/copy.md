--- LINKEDIN ---
A bare while loop that dies mid-run loses everything — no saved position to resume from, so a crash at minute forty means starting over at minute zero. A checkpointer fixes this by snapshotting graph state after every superstep, so a crashed or paused run can pick up exactly where it left off.

That same save-point mechanism is what makes human-in-the-loop possible: a graph can pause mid-node, wait for seconds or for days, and resume later with a human's input folded into the resumed state. Both capabilities depend on the same primitive — nothing about pausing or resuming works without a checkpointer wired in first.

Two interrupt mechanisms exist, and they aren't interchangeable. interrupt(payload), called inside a node, carries an arbitrary JSON payload — the real production approval mechanism. interrupt_before/interrupt_after, passed to compile(), are unconditional, payload-less breakpoints — debugging tools, not approval flows.

decision = interrupt({"draft": state["draft"], "prompt": "Approve, reject, or edit?"})
return {"approval": decision}

# later, possibly after a real restart, same thread_id:
graph.invoke(Command(resume={"action": "approved"}), config=config)

Three response shapes — approve, reject, edit-then-approve — are all handled by that same Command(resume=...) call. What interrupt() doesn't give you: authorization tracking. It only pauses and resumes; who approved and under what authority has to be written into state or an audit log explicitly, by your own code.

Production practice: don't over-interrupt. Pausing on every model call trains reviewers to rubber-stamp — reserve interrupt() for irreversible, high-blast-radius, or regulated actions. And remember a checkpointer persists state, never code: after a restart, node functions and graph wiring have to be rebuilt before a paused thread can resume.

Would your paused threads survive a real process restart, not just a notebook re-run?

#AppliedAI #LangGraph #AIEngineering #LLM

--- INSTAGRAM ---
A crash at minute forty shouldn't mean starting over. ⏸️

A checkpointer snapshots state after every step — that's what lets a graph pause, wait days, and resume with a human's input folded in.

decision = interrupt({"draft": state["draft"]})
graph.invoke(Command(resume={"action": "approved"}), config=config)

Reserve it for irreversible actions — over-interrupting trains reviewers to rubber-stamp.

Full mechanics in the carousel.

#AppliedAI #LangGraph #AIEngineering #LLM #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "A Crash At Minute Forty Shouldn't Mean Starting Over"
2. The same mechanism enables HITL
3. Two interrupt mechanisms — only one carries a payload
4. Sample code — three response shapes, one primitive (code)
5. What interrupt() doesn't give you — no authorization recorded
6. Production gotcha — don't over-interrupt
7. Takeaway — a checkpointer persists state, never code (closing question)
