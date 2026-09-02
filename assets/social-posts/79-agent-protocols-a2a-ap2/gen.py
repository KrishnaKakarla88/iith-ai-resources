import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "MCP Is Vertical. A2A Is Horizontal.",
      ["MCP answers how an agent uses its own tools. Three more protocols cover what MCP doesn't touch: agent-to-agent delegation, agent-to-user interaction, and proof of payment authority."])

slide(p("slide-02.png"), 2, 6, "Three Protocols, Three Questions", "Each Answers One Layer",
      ["**A2A**: how does one opaque agent delegate work to another, independently-built agent?",
       "**AG-UI**: what does the user see while an agent works for three minutes instead of returning instantly?",
       "**AP2**: what evidence proves the user actually authorized this agent-performed purchase?"])

slide(p("slide-03.png"), 3, 6, "AP2's Three Mandates", "Three Moments, Three Different Signers",
      ["**Intent** (open, user-signed): constraints before a cart exists — allowed merchants, amount ceiling.",
       "**Cart** (closed, agent-signed): one exact purchase once it's known.",
       "**Payment** (agent-signed): ties the charge to the cart mandate at settlement."])

slide(p("slide-04.png"), 4, 6, "The Deterministic Verifier", "No Model Anywhere In This Path",
      ["Checks signatures, expiry, that the total equals the sum of line items, that the merchant is allow-listed, that the mandate pair hasn't already been consumed.",
       "The model may explain a choice. It may never raise the cap, alter a signed checkout, or wave through a replay."])

slide(p("slide-05.png"), 5, 6, "Why A Trusted Surface Must Be Non-Agentic", "It Collects The Consent It Then Has To Prove",
      ["If the thing showing the user what they're authorizing were itself an agent, the component proving informed consent would be the same untrusted actor the mandate system exists to constrain."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Adopt The Protocol, Don't Marry It",
      ["Protocol-specific code belongs at the integration boundary, never inside domain logic — so swapping or dropping a young standard costs one adapter, not a rewrite."],
      closing_q="If your agent handles money, can you prove authorization cryptographically, or only reconstruct it from logs after a dispute?")

print("done: 79")
