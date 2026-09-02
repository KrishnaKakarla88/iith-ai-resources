import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Semantic Search Is Actually A Geometry Question",
      ["An embedding model turns text into a fixed-length vector — texts with similar meaning land close together in that space."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "Dimension, Distance, And One Fixed Rule",
      ["**Dimension**: length of the output vector — fixed per model, must match on write and read sides.",
       "**Distance metric**: cosine similarity is the default pairing with most modern embedding models.",
       "**MRL**: lets one model's output be truncated to a shorter, still-usable vector."])

slide(p("slide-03.png"), 3, 6, "Chat And Embeddings Don't Have To Match", "Different Vendor, Different Capability",
      ["**Example:** this stack generates text with Groq (llama-3.1-8b-instant) but embeds with Gemini.",
       "Embedding quality and chat quality are separate capabilities — nothing requires the same vendor for both."])

slide(p("slide-04.png"), 4, 6, "Sample Code", "Cache And Throttle, Or The Free Tier Kills You",
      ["Caching by a hash of the input text avoids re-embedding unchanged chunks on every pipeline re-run."],
      code="from langchain_google_genai import GoogleGenerativeAIEmbeddings\n\nembedder = GoogleGenerativeAIEmbeddings(model=\"gemini-embedding-001\")\n# disk cache: sha1(text) -> embedding, batches of 90, 60s pause")

slide(p("slide-05.png"), 5, 6, "The Gotcha", "Switching Embedding Models Isn't A Config Change",
      ["Every existing vector is in the old model's space — mixing old and new vectors makes distances meaningless.",
       "The whole corpus has to be re-embedded and the collection rebuilt at the new dimension, never appended to in place."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Pin The Exact Model Name And Dimension",
      ["Not just code that happens to work today — a silent provider-side upgrade can change output dimensions or the vector space entirely."],
      closing_q="Do you know exactly which embedding model and dimension your index was built with?")

print("done: 51")
