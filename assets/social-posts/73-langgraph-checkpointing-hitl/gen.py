import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "A Crash At Minute Forty Shouldn't Mean Starting Over",
      ["A checkpointer snapshots graph state after every superstep — a crashed or paused run picks up exactly where it left off, instead of restarting."])

slide(p("slide-02.png"), 2, 7, "The Same Mechanism Enables HITL", "Pause Mid-Node, Wait, Resume With Human Input",
      ["A graph can pause for seconds or for days and resume later with a human's input folded into the resumed state — both capabilities depend on the same primitive, a checkpointer wired in first."])

slide(p("slide-03.png"), 3, 7, "Two Interrupt Mechanisms", "Only One Carries A Payload",
      ["interrupt(payload): called inside a node, carries an arbitrary JSON payload — the real production approval mechanism.",
       "interrupt_before/interrupt_after: unconditional, payload-less breakpoints set at compile time — debugging tools, not approval flows."])

slide(p("slide-04.png"), 4, 7, "Sample Code", "Three Response Shapes, One Primitive",
      ["Approve, reject, or edit-then-approve — all handled by the same Command(resume=...) call."],
      code="decision = interrupt({\"draft\": state[\"draft\"], \"prompt\": \"Approve, reject, or edit?\"})\nreturn {\"approval\": decision}\n\n# later, possibly after a real restart, same thread_id:\ngraph.invoke(Command(resume={\"action\": \"approved\"}), config=config)")

slide(p("slide-05.png"), 5, 7, "What interrupt() Doesn't Give You", "No Authorization Recorded By Default",
      ["It only pauses and resumes. Who approved and under what authority has to be written into state or an audit log explicitly, by your own code."])

slide(p("slide-06.png"), 6, 7, "Production Gotcha", "Don't Over-Interrupt",
      ["Pausing on every model call trains reviewers to rubber-stamp. Reserve interrupt() for irreversible, high-blast-radius, or regulated actions."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "A Checkpointer Persists State, Never Code",
      ["After a restart, node functions and graph wiring have to be rebuilt before a paused thread can resume — nothing about the state itself is lost."],
      closing_q="Would your paused threads survive a real process restart, not just a notebook re-run?")

print("done: 73")
