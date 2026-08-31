import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "The Baseline Before Any Wrapper",
      ["Calling a provider's SDK directly, before LiteLLM or any gateway sits in front of it — every later abstraction gets judged against this."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "The Same Shape, Any Provider",
      ["**client.chat.completions.create(...)** is the call shape both the Groq SDK and OpenAI SDK share.",
       "**response.choices[0].message.content** is where the reply text lives, either way."],
      code="response.choices[0].message.content")

slide(p("slide-03.png"), 3, 6, "Why It Works", "Groq Speaks OpenAI's Dialect",
      ["Groq exposes an **OpenAI-compatible endpoint** — same request/response JSON shape as OpenAI's own API.",
       "Point the OpenAI SDK at Groq's base_url and it works unmodified."],
      code='OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")')

slide(p("slide-04.png"), 4, 6, "Why It Matters", "Only The Client Object Changes",
      ["Same messages list, same response shape either way — the only difference is which client you instantiate and which base_url it points at.",
       "That's the exact seam LiteLLM later automates away entirely."])

slide(p("slide-05.png"), 5, 6, "Real Bug Class", "One Shared List Leaks Between Users",
      ["A single messages list reused across concurrent users cross-talks their conversations.",
       "**SessionStore** maps session_id to its own isolated messages list — not a nice-to-have."],
      code="self._sessions[session_id] = [{'role': 'system', 'content': '...'}]")

slide(p("slide-06.png"), 6, 6, "Takeaway", "Statelessness Is The Baseline",
      ["Every later abstraction — LiteLLM, LangChain, an agent framework — is built to hide this fact, not to change it."],
      closing_q="Have you called a provider's raw SDK directly, or gone straight to a wrapper?")

print("done: 32")
