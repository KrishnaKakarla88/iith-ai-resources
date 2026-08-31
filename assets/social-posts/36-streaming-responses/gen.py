import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Streaming Doesn't Make Generation Faster",
      ["Total generation time is roughly unchanged. What changes is what the user actually perceives."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "Chunks Instead Of One Response",
      ["stream=True returns an iterable of small chunks instead of blocking until the full reply is done.",
       "Each chunk carries a fragment, delivered as soon as the model produces it."],
      code='for chunk in litellm.completion(model=m, messages=msgs, stream=True):\n    piece = chunk.choices[0].delta.content or ""')

slide(p("slide-03.png"), 3, 6, "Gotcha", "Guard The Empty Chunk",
      ["chunk.choices[0].delta.content can be empty or None for metadata-only chunks — like the final chunk carrying finish_reason.",
       "Guard with \"or \\\"\\\"\" before appending."],
      code='piece = chunk.choices[0].delta.content or ""')

slide(p("slide-04.png"), 4, 6, "What Actually Improves", "Time-To-First-Token",
      ["How long before anything shows up is what a user feels as \"fast.\"",
       "That's the whole mechanism behind the typewriter effect in every modern chat UI."])

slide(p("slide-05.png"), 5, 6, "Production Note", "Prefer SSE For A Browser Endpoint",
      ["Server-Sent Events give built-in reconnection and a clean client-side EventSource API.",
       "Disable reverse-proxy buffering explicitly, or an intermediary can re-batch your stream back into one blocking response."],
      code="X-Accel-Buffering: no")

slide(p("slide-06.png"), 6, 6, "Takeaway", "A Long Reply Still Takes About As Long",
      ["The perceived win from streaming is naturally smaller relative to a long response's total duration.",
       "It's a UX fix, not a throughput fix."],
      closing_q="Is your chat endpoint streaming, or blocking until the full reply is ready?")

print("done: 36")
