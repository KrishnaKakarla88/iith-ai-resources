--- LINKEDIN ---
A retriever never searches whole documents — it searches chunks. Get the chunk size wrong and even a perfect retriever returns text that's too big to be relevant or too small to make sense on its own. A 5,000-word chunk covering ten subtopics dilutes the embedding — it won't strongly match a query about any one of them. A single sentence pulled from a legal clause loses the clause it belonged to.

One splitter doesn't fit every document. Recursive character splitting is the default for prose — it tries paragraph, then sentence, then word boundaries before falling back to a hard cut. A CSV row is already a complete, retrievable unit — don't split it further. Header-aware splitting carries the heading path into chunk metadata for structured Markdown/HTML.

from langchain_text_splitters import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)

Chunk overlap repeats a few characters at each boundary so a concept split across a cut isn't fully lost to either side.

Production practice: tune chunk size and overlap against your actual retrieval eval, not once and forget — a chunk size that works for a manual page won't necessarily work for a return-policy FAQ. One detail worth getting right early: the chunk id gets assigned at chunking time, not embedding time, because it doubles as the vector database's point id downstream.

Is your chunk size tuned against a retrieval eval, or just picked once and left?

#AppliedAI #RAG #LLM #AIEngineering

--- INSTAGRAM ---
Your retriever never sees the whole document. It sees chunks. 📄

Too big: dilutes the embedding, doesn't match any one subtopic. Too small: loses the context that made it meaningful.

Recursive splitting for prose. Row-atomic for CSVs. Header-aware for structured docs.

splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)

Full breakdown in the carousel.

#AppliedAI #RAG #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "A Retriever Never Searches Whole Documents"
2. Too big vs too small — chunking is a tradeoff
3. Match strategy to source — recursive/row-atomic/header-aware
4. Core mechanics — chunk size + overlap (code)
5. Production practice — tune against the eval
6. Takeaway — cid assigned at chunking time (closing question)
