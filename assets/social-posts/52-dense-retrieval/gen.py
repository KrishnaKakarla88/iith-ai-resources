import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "Good At Meaning, Blind To Exact Tokens",
      ["Dense retrieval ranks documents by embedding-vector similarity to a query — but an exact SKU or case number often isn't meaningfully different from a similar-looking one in vector space."])

slide(p("slide-02.png"), 2, 6, "The Strength", "No Shared Words Required",
      ["**Example:** a query for \"can I return a laptop late?\" retrieves a chunk saying \"electronics must be returned within 14 days\" — zero shared exact words, same meaning."])

slide(p("slide-03.png"), 3, 6, "The Blind Spot", "Exact Identifiers Are Probabilistic, Not Guaranteed",
      ["Whether dense search finds the exact right record for an exact id depends on embedder quality and how distinct that identifier is from its neighbors.",
       "Not a guarantee the way BM25's exact-term match is."])

slide(p("slide-04.png"), 4, 6, "Sample Code", "Metadata Filters Are Exact, Query Text Isn't",
      ["A Filter restricts search to a structural condition. Embedding \"only CSV files\" into the query text is just another signal competing with the rest of the meaning — not a guarantee."],
      code="hits = client.query_points(\n    collection_name=COLLECTION,\n    query=query_vector,\n    limit=k,\n    query_filter=Filter(must=[FieldCondition(\n        key=\"doc_type\", match=MatchValue(value=doc_type))]))")

slide(p("slide-05.png"), 5, 6, "Production Practice", "Fetching More Isn't Automatically Safer",
      ["Every extra chunk in the generation context competes for the model's attention and adds cost/latency.",
       "Over-fetch into a pool only when a reranking stage follows — dense search's job in a two-stage pipeline is recall, not final precision."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "A recall@k of 1.0 On A Clean Corpus Is A Best Case",
      ["Not a guarantee — production corpora are larger, noisier, and more likely to have near-duplicate identifiers."],
      closing_q="Would your retriever survive two SKUs that differ by one digit?")

print("done: 52")
