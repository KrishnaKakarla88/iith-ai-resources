import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Provider Swap Becomes A Config Value",
      ["The same function, unmodified, calling two different providers — that's the whole payoff."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "Zero Code Change Across Providers",
      ["litellm_chat(model, user_input) never branches on which provider it's talking to.",
       "Swap the model= string and get a different vendor, same function body."],
      code='litellm_chat("groq/llama-3.1-8b-instant", text)\nlitellm_chat("gpt-4o-mini", text)  # same function')

slide(p("slide-03.png"), 3, 6, "Two Modes", "Library Mode vs Proxy Mode",
      ["**Library mode**: litellm.completion() runs in-process, reads provider env vars directly.",
       "**Proxy mode**: a standalone server your app calls over HTTP — centralized routing and fallback."])

slide(p("slide-04.png"), 4, 6, "Gotcha", "A Proxy Creates Two Credentials",
      ["The provider key the proxy forwards upstream, and the key your app sends to the proxy itself.",
       "LiteLLM's default env-var resolution is built for library mode — it doesn't separate the two automatically."],
      code="LITELLM_MASTER_KEY  # app-to-proxy, separate from GROQ_API_KEY")

slide(p("slide-05.png"), 5, 6, "Why It Matters", "Model Rankings Change Monthly",
      ["Locked into one provider's SDK, \"let's just try the new model\" is a rewrite.",
       "Routed through LiteLLM, it's a one-line model= change instead."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A 401 Despite A Valid Key Isn't Always Auth",
      ["Once a proxy sits in front, a 401 usually means the app-to-proxy credential — not the upstream one.",
       "Two credentials, two places to check."],
      closing_q="Are you running LiteLLM in library mode or behind a proxy?")

print("done: 34")
