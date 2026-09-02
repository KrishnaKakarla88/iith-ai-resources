import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "\"Agent\" Isn't The Fancy Version Of \"Chain\"",
      ["Inside LangChain specifically, create_agent always runs a loop with tool-choice inside it — a chain never does, no matter how it's dressed up."])

slide(p("slide-02.png"), 2, 6, "Two Control Shapes", "Fixed Order vs. Model-Decided Order",
      ["**Chain**: prompt | model | parser always runs in that order, every time.",
       "**Agent**: call the model, let it choose a tool, run it, feed the result back, repeat until the model decides to stop."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "A Chain Wearing An LLM Call Isn't An Agent",
      ["If the steps are always the same and only the content is fuzzy, reach for with_structured_output inside a chain — not create_agent."],
      code="# CHAIN — fixed order\ninvoice = chat_model.with_structured_output(InvoiceSchema).invoke(raw_text)\nif not validate(invoice):\n    raise ValueError(...)\npost(invoice)  # both plain code, no model")

slide(p("slide-04.png"), 4, 6, "When It's Genuinely An Agent", "The Model Decides Which Tool + When To Stop",
      [],
      code="agent = create_agent(\n    model=\"groq:llama-3.1-8b-instant\",\n    tools=[lookup_supplier_risk, lookup_contract_terms],\n    system_prompt=\"Research supplier risk before recommending a decision.\",\n)")

slide(p("slide-05.png"), 5, 6, "The Rule That Applies To Both", "Let The Model Produce, Let Deterministic Code Decide",
      ["An agent's tool-call arguments come from the model and can't be blindly trusted — force-set authorization-critical fields like a customer id server-side, unconditionally overwriting whatever the model's argument contained."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Model Can Narrate An Outcome It Never Executed",
      ["\"Refund processed\" in the final text doesn't mean the tool was actually called — check for narrated-but-not-executed outcomes explicitly."],
      closing_q="Is any step in your \"agent\" actually fixed order wearing an LLM call?")

print("done: 64")
