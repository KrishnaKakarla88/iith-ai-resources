--- LINKEDIN ---
A customer saying "my order number is 4471" is not proof they own order 4471 — it's a string in a prompt, and an LLM that trusts it is trusting attacker-controlled input to authorize an action. A single-tenant agent can get away with sloppy identity handling because there's nowhere for a leak to go. A multi-tenant agent — one deployment, many customers sharing the same memory store and vector index — doesn't have that luxury.

Rule one: identity comes from the session, never the message.
def resolve_customer(session) -> str:
    if not session.is_authenticated:
        raise AuthError("no authenticated session")
    return session.customer_ref  # not: re.search(order_ref_pattern, user_message)

Rule two: re-verify at the point of mutation, not just at login. A login check proves who's talking then — it doesn't prove the specific write three tool calls later is still scoped to that same customer.
def order_service_authorize(customer_ref, order_id):
    order = orders_db.get(order_id)
    if order is None or order.owner_ref != customer_ref:
        raise PermissionError("not authorized for this order")

A cheap win: embed the owner in the resource id itself. A missed check on a namespaced id fails loudly — a lookup for the wrong prefix returns nothing, instead of silently returning someone else's data.

The error-masking rule matters more than it looks: the difference between "not found" and "not yours" leaks information an attacker can probe with. Convert a cross-tenant PermissionError into one generic denial before it reaches the caller.

Production practice: model three identity layers, not one — who triggered the request, what credential is executing it, and what tenant boundary it must stay inside. Modeling only one of these tends to surface access-control bugs silently, months later.

Is there even one call site in your system where identity comes from message text?

#AppliedAI #AIEngineering #LLM #LangGraph

--- INSTAGRAM ---
"My order number is 4471" proves nothing. 🔐

Identity comes from the session, never the message. Re-verify at every mutation, not just login.

def resolve_customer(session):
    return session.customer_ref  # never parsed from user text

Embed the owner in the resource id — a missed check then fails loudly, not silently.

Never confirm a resource exists in an error message.

Full mechanics in the carousel.

#AppliedAI #AIEngineering #LLM #LangGraph #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "\"My Order Number Is 4471\" Is Not Proof Of Ownership"
2. Rule one — identity comes from the session, never the message (code)
3. Rule two — re-verify at the point of mutation, not just at login (code)
4. Cheap ownership checks — embed the owner in the resource id itself (code)
5. The error-masking rule — never confirm a resource exists
6. Production practice — three identity layers, not one
7. Takeaway — a single missed namespace call site is a real leak (closing question)
