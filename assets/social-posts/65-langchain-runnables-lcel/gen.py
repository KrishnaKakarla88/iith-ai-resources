import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "The Pipe Operator Isn't String Concatenation",
      ["Every piece you'd chain in LangChain — a prompt, a model, a parser — implements the same Runnable interface. That's what makes prompt | model | parser actually build something."])

slide(p("slide-02.png"), 2, 6, "The Real Payoff", "Streaming And Batching, For Free",
      ["Once composed with |, every step supports invoke/stream/batch (and async forms) uniformly — you don't write separate streaming logic for a 3-step vs a 7-step chain."],
      code="chain = prompt | model | parser          # RunnableSequence\nsummary = chain.invoke({\"ticket_text\": raw_text})\nasync for token in chain.astream({\"ticket_text\": raw_text}):\n    print(token, end=\"\")")

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "Sequence, Parallel, Lambda, Passthrough",
      ["**RunnableSequence**: chained with |, runs steps in order.",
       "**RunnableParallel**: runs multiple Runnables concurrently on the same input.",
       "**RunnableLambda**: wraps a plain function so it fits inside a | chain."])

slide(p("slide-04.png"), 4, 6, "The Ceiling", "No Loop, No Persisted State, No Pause",
      ["LCEL is for straight-line or simply-branching pipelines.",
       "The moment a workflow needs conditional routing backward, a human pause, or crash-survivable state, you've outgrown a chain and want a graph."])

slide(p("slide-05.png"), 5, 6, "Production Gotcha", "A Chain Built Outside The Shared Wrapper Bypasses It Silently",
      ["A centralized LLM-call wrapper (tracing, retry, cost accounting) only covers call sites that go through it — a code path building its own chain and calling .invoke() directly skips it entirely."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Most Real Workflows Are A Mix",
      ["A handful of always-fixed steps (chains) embedded inside a larger stateful, branching workflow (a graph) — not one or the other for the whole system."],
      closing_q="Does every LCEL chain in your codebase actually go through your instrumentation wrapper?")

print("done: 65")
