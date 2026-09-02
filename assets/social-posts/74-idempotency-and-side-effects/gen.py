import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "Resuming A Paused Node Re-Runs It From The Top",
      ["LangGraph doesn't restore a call stack — it replays the whole node function until interrupt() returns the resume value. Any side effect before that call fires again."])

slide(p("slide-02.png"), 2, 7, "The Bug In One Line", "A Side Effect Before interrupt() Double-Fires",
      ["An email gets sent twice. A payment gets charged twice. A refund gets issued twice — on every single resume, not just once."])

slide(p("slide-03.png"), 3, 7, "The Fix", "Split The Node, Not The Behavior",
      ["A node containing interrupt() should do nothing before it except read state. Every irreversible action belongs in its own node, downstream of the pause."],
      code="def human_approval_node(state):\n    decision = interrupt({\"draft\": state[\"draft\"]})  # only a state read before this\n    return {\"approval\": decision}\n\ndef finalize_node(state):\n    send_confirmation_email(state[\"draft\"])  # runs exactly once, post-resume\n    return {\"status\": \"finalized\"}")

slide(p("slide-04.png"), 4, 7, "Deterministic IDs", "uuid5 Makes A Re-Run A No-Op",
      ["uuid4 generates a new random id every call — a re-run duplicates the row.",
       "uuid5(namespace, stable_input) produces the same id every time — an upsert overwrites in place instead."],
      code="def chunk_point_id(source, chunk_idx):\n    return str(uuid.uuid5(NAMESPACE, f\"{source}:{chunk_idx}\"))")

slide(p("slide-05.png"), 5, 7, "Side Tables", "Bookkeeping That Must Survive A Replay Lives Outside The Node",
      ["An upsert-keyed table, written from the call site that sees the one-time event — not from inside a node that might replay."])

slide(p("slide-06.png"), 6, 7, "The Real-World Stakes", "Nine Seconds To Delete, Thirty Hours To Recover",
      ["A documented 2026 incident: an agent hit a credential mismatch and, on its own, deleted a production volume to \"fix\" it.",
       "No confirmation gate stood in front of a destructive operation — the exact category of gap the split-node rule closes."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "This Isn't A LangGraph Bug — It's What Resumability Costs",
      ["Checkpoint-and-resume has to replay code to work at all; idempotent design is the price of durability, not an edge case to patch later."],
      closing_q="Does any side effect in your graph run before its node's interrupt() call?")

print("done: 74")
