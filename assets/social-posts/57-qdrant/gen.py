import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "skills", "posts"))
from carousel_template import slide

OUT = os.path.dirname(__file__)


def p(name):
    return os.path.join(OUT, name)


slide(p("slide-01.png"), 1, 6, "Concept", "A B-Tree Can't Answer \"Nearest In 3072 Dimensions\"",
      ["Qdrant is a vector database purpose-built for that exact question — store vectors plus metadata, then query by similarity."])

slide(p("slide-02.png"), 2, 6, "Core Mechanics", "Collection, Point, Payload",
      ["**Collection**: a named set of points sharing one vector dimension and distance metric, created once.",
       "**Point**: one record — id, vector, payload.",
       "**Payload index**: required before filtering on a field — Qdrant Cloud's strict mode rejects unindexed filters outright."])

slide(p("slide-03.png"), 3, 6, "Sample Code", "The Index Has To Exist First",
      ["Filtering on doc_type before creating its payload index is rejected outright, not degraded gracefully."],
      code="client.create_collection(collection_name=COLLECTION,\n    vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE))\n\nclient.create_payload_index(collection_name=COLLECTION,\n    field_name=\"doc_type\", field_schema=PayloadSchemaType.KEYWORD)")

slide(p("slide-04.png"), 4, 6, "The Gotcha", "Random IDs Silently Duplicate Every Re-Ingest",
      ["**Example:** uuid4() generates a new random id for the same content on every run — a re-run upserts duplicates instead of overwriting.",
       "uuid5(namespace, f\"{source}:{chunk_idx}\") makes re-ingestion idempotent instead."])

slide(p("slide-05.png"), 5, 6, "Don't Touch This Once Set", "Changing The Namespace Orphans Everything",
      ["Every id derived from that namespace constant changes with it — nothing matches existing points anymore, and prior data is effectively lost."])

slide(p("slide-06.png"), 6, 6, "Takeaway", "Build The Payload Index Before Ingestion, Not After",
      ["Adding one retroactively forces a full HNSW index rebuild instead of incrementally optimizing."],
      closing_q="Are your point ids deterministic, or does every re-ingest quietly duplicate your collection?")

print("done: 57")
