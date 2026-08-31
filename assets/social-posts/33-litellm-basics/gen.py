import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "One Function, Every Provider",
      ["litellm.completion() normalizes the call shape and the response shape across providers."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "The Model String Routes The Call",
      ["The provider prefix before the slash tells LiteLLM which SDK/API to actually call.",
       "Everything after — messages, response.choices[0].message.content — stays identical."],
      code='model="groq/llama-3.1-8b-instant"  # or "gpt-4o-mini", "anthropic/claude-sonnet-4-6"')

slide(p("slide-03.png"), 3, 6, "Core Mechanics", "The Generation Knobs",
      ["**temperature** controls randomness. **max_tokens** caps output length.",
       "**stop** ends generation early. **response_format** switches prose vs JSON mode."])

slide(p("slide-04.png"), 4, 6, "Core Mechanics", "top_p Is An Alternative, Not An Add-On",
      ["**top_p** (nucleus sampling) shapes randomness a different way than temperature.",
       "Provider guidance: tune one or the other — stacking both compounds in ways that are hard to reason about."],
      code="top_p=0.9  # instead of temperature, not alongside it")

slide(p("slide-05.png"), 5, 6, "Core Mechanics", "Token Counting Is Per-Model",
      ["token_counter takes a model= argument because different models tokenize the same string differently.",
       "A single global ratio would misreport cost and context usage."],
      code="litellm.token_counter(model=m, messages=[...])")

slide(p("slide-06.png"), 6, 6, "Takeaway", "temperature=0 Is Not A Guarantee",
      ["Near-deterministic in practice, not promised — same for seed.",
       "Providers make a \"best effort,\" not a hard contract."],
      closing_q="Do you rely on temperature=0 for reproducible outputs?")

print("done: 33")
