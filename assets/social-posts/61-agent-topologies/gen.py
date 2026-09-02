import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "More Agents Is Not A Maturity Upgrade",
      ["A topology is the shape of a multi-agent system — the roster of agents plus who hands work to whom. Splitting into more agents only pays off when there's a reason you can name."])

slide(p("slide-02.png"), 2, 6, "Three Shapes", "Ordered By Coordination Cost",
      ["**Sequential**: A → B → C, fixed order — each stage's output is exactly what the next needs.",
       "**Parallel**: split into N independent workers, merge — genuinely independent sub-tasks.",
       "**Hierarchical**: one supervisor routes repeatedly to N specialists — which one is needed depends on the task."])

slide(p("slide-03.png"), 3, 6, "Sequential And Parallel Are Still Workflows", "Only Hierarchical Needs Real Agent Autonomy",
      ["A fixed A→B→C pipeline doesn't need an LLM deciding who talks to whom, only content at each step.",
       "A supervisor topology exists precisely because which specialist runs next depends on data the designer can't enumerate ahead of time."],
      diagram=("flow", ["Supervisor", "Route", "Specialist", "Report back"]))

slide(p("slide-04.png"), 4, 6, "The Real Cost", "Coordination Isn't Free",
      ["Message passing, state synchronization, lossy re-serialization at every handoff — a worker sees a summary, not the supervisor's full context.",
       "Most measured multi-agent failures are coordination/specification bugs, not model mistakes."])

slide(p("slide-05.png"), 5, 6, "Production Practice", "The Decision Tree Defaults To No",
      ["Split into a second agent only for a reason you can name — genuine expertise separation, real parallelism, or a critic that must not share the generator's blind spots.",
       "\"It feels more sophisticated\" is not a reason."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Topology Is Usually Fixed At Design Time",
      ["A fixed roster can only reroute work it anticipated — a task needing a capability outside the roster means an escalation, not a runtime decision."],
      closing_q="Could you name the exact reason your system needs a second agent?")

print("done: 61")
