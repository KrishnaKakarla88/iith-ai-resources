import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 7, "Concept", "\"My Order Number Is 4471\" Is Not Proof Of Ownership",
      ["A customer saying it is a string in a prompt — an LLM that trusts it is trusting attacker-controlled input to authorize an action."])

slide(p("slide-02.png"), 2, 7, "Rule One", "Identity Comes From The Session, Never The Message",
      ["An authenticated session, a signed token, a request header set by your own auth layer before the agent ever runs — never parsed out of the conversation."],
      code="def resolve_customer(session) -> str:\n    if not session.is_authenticated:\n        raise AuthError(\"no authenticated session\")\n    return session.customer_ref  # not: re.search(order_ref_pattern, user_message)")

slide(p("slide-03.png"), 3, 7, "Rule Two", "Re-Verify At The Point Of Mutation, Not Just At Login",
      ["A login check proves who's talking then. It doesn't prove the specific write three tool calls later is still scoped to that same customer — those are two different checks."],
      code="def order_service_authorize(customer_ref, order_id):\n    order = orders_db.get(order_id)\n    if order is None or order.owner_ref != customer_ref:\n        raise PermissionError(\"not authorized for this order\")")

slide(p("slide-04.png"), 4, 7, "Cheap Ownership Checks", "Embed The Owner In The Resource Id Itself",
      ["A missed check on a namespaced id fails loudly — a lookup for the wrong prefix returns nothing, instead of silently returning someone else's data."],
      code="def thread_id_for(customer_ref, conversation_id):\n    return f\"{customer_ref}:{conversation_id}\"")

slide(p("slide-05.png"), 5, 7, "The Error-Masking Rule", "Never Confirm A Resource Exists",
      ["The difference between \"not found\" and \"not yours\" leaks information an attacker can probe with. Convert a cross-tenant PermissionError into one generic denial before it reaches the caller."])

slide(p("slide-06.png"), 6, 7, "Production Practice", "Three Identity Layers, Not One",
      ["Who triggered the request, what credential is executing it, and what tenant boundary it must stay inside — modeling only one of these surfaces access-control bugs silently, months later."])

slide(p("slide-07.png"), 7, 7, "Takeaway", "A Single Missed Namespace Call Site Is A Real Leak",
      ["Not a hypothetical — every read/write to shared memory or a vector index has to go through the scoping helper, with no code path that bypasses it."],
      closing_q="Is there even one call site in your system where identity comes from message text?")

print("done: 78")
