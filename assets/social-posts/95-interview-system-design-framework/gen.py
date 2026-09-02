import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Interview Nugget", "There's No Correct Answer In A System-Design Round. Only A Defensible One.",
      ["Roughly 75% of technical-round time in 2026 AI-engineer loops goes to RAG architecture, evals, and multi-agent design specifically — a repeatable framework matters more than any one memorized design."])

slide(p("slide-02.png"), 2, 6, "The Framework", "Five Steps, In Order",
      ["Clarify actual requirements and constraints before designing anything.",
       "Sketch the end-to-end shape at a high level.",
       "Go one level deeper on the 1-2 components that are actually hard here.",
       "Name the failure modes and how the system degrades under each.",
       "State what you'd measure to know it's working."])

slide(p("slide-03.png"), 3, 6, "The Tell", "Jumping Straight To Step 3 Without 1-2",
      ["Interviewers notice candidates who jump straight to \"I'd use a vector database\" without first asking how often the data changes, how large the corpus is, or what a wrong answer actually costs."])

slide(p("slide-04.png"), 4, 6, "A Concrete Number Worth Having Ready", "Multi-Agent Isn't Free, Even When It's Right",
      ["Per 2026 industry estimates, independent multi-agent setups run roughly 58% more tokens than a single agent doing the same work — centralized coordination overhead can run substantially higher still."])

slide(p("slide-05.png"), 5, 6, "Justify Before You Design", "The Question Most Candidates Skip",
      ["Before sketching a multi-agent system, justify the decision to split at all — a single agent with three tools isn't automatically worse than three specialist agents. Naming the reason is what separates knowing the mechanics from knowing when to reach for them."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Rehearse Out Loud Before Reading Any Answer Sketch",
      ["Talk through your own answer for 3-5 minutes first — the framework is a habit to practice, not a script to recite."],
      closing_q="Next system-design prompt you get — do you know your first three clarifying questions?")

print("done: 95")
