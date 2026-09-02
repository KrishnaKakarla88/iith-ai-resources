import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Why Chat History Isn't Memory Enough",
      ["Between API calls an LLM is stateless — a raw transcript is only one of four kinds of memory an agent actually needs."])

slide(p("slide-02.png"), 2, 6, "The CoALA Taxonomy", "Four Kinds Of Memory, Four Jobs",
      ["**Working**: what's in front of me right now — one turn, never persisted.",
       "**Episodic**: what happened, and when — a timestamped event.",
       "**Semantic**: what's stably true — no story, no date attached.",
       "**Procedural**: how do I do this task — a reusable recipe."])

slide(p("slide-03.png"), 3, 6, "The Discriminator", "Does It Have A Specific \"When\"?",
      ["**Example:** \"User booked flight AI-302 on 1 Aug\" has a when — episodic.",
       "\"User prefers aisle seats\" doesn't need one — semantic.",
       "\"Check the budget freeze, then use the corporate vendor\" is neither a moment nor a fact — it's a recipe — procedural."])

slide(p("slide-04.png"), 4, 6, "Core Mechanics", "One Write Call, Different Tags",
      ["The SDK call never changes — only the metadata tag decides which bucket a fact lands in."],
      code="def remember(mem, text, kind, **extra):\n    mem.add(content=text, container_tag=USER_ID,\n             metadata={\"type\": kind, **extra})\n\nremember(mem, \"Booked flight AI-302 on 1 Aug.\", kind=\"episodic\")\nremember(mem, \"Prefers aisle seats.\", kind=\"semantic\")")

slide(p("slide-05.png"), 5, 6, "Production Practice", "Who Decides What Gets Written?",
      ["The lab has application code pre-decide the type tag at write time.",
       "2026-era systems increasingly hand that judgment to the model itself — Anthropic's memory tool lets Claude read/write files under /memories with no vector DB required."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Chat Buffer Is Episodic Memory In Disguise",
      ["It has no durable facts extracted, no reusable procedures — and it's gone the moment the session ends unless something deliberately persists it."],
      closing_q="Next time an agent 're-asks' something — is that a memory bug, or a working-memory bug?")

print("done: 46")
