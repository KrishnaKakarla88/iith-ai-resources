--- LINKEDIN ---
"This answer looks better" is not evidence. Two retrieval pipelines can both produce fluent, confident answers, and only one of them is actually right. The fix is a golden set: a fixed collection of real questions where you already know the correct answer and which source chunk(s) support it.

Precision@k: of the top k retrieved, how many are actually relevant? Recall@k: of all relevant chunks that exist, how many did the top k retrieve? MRR: how high up did the first relevant result land, averaged across the whole golden set?

def precision_at_k(retrieved, gold, k):
    return sum(1 for c in retrieved[:k] if c in gold) / k

def mrr(retrieved, gold):
    for i, cid in enumerate(retrieved, start=1):
        if cid in gold:
            return 1.0 / i
    return 0.0

Precision and recall can move in opposite directions — fetching 50 candidates can hit high recall (the right chunk is probably in there) while scoring low precision at k=50 (most of those 50 aren't relevant).

The reason to measure retrieval separately from generation: a pipeline can retrieve the right chunk and still generate a bad answer (a generation problem), or generate a fluent answer that's ungrounded because retrieval never found the right chunk in the first place (a retrieval problem dressed up as "hallucination"). Measuring retrieval separately tells you which one you're actually looking at.

A golden set catches regressions nobody reported. A handful of spot-checked examples can look convincing by chance in either direction — a fixed, scored set turns "this seems worse" into a number that moves.

Is a hallucinated-looking answer on your system actually a retrieval problem in disguise?

#AppliedAI #RAG #LLM #AIEngineering

--- INSTAGRAM ---
"Looks better" isn't a metric. 📊

Precision@k, recall@k, MRR — measured against a golden set with known-correct chunks, not vibes.

def mrr(retrieved, gold):
    for i, cid in enumerate(retrieved, start=1):
        if cid in gold: return 1.0 / i

Most "hallucinations" are actually retrieval never finding the right chunk — not the model reasoning poorly.

Full breakdown in the carousel.

#AppliedAI #RAG #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "\"This Looks Better\" Is Not Evidence"
2. Three metrics — precision, recall, MRR
3. Sample code — formulas that work on any chunk ids (code)
4. Why measure the retriever separately
5. Precision and recall disagree
6. Takeaway — a golden set catches regressions nobody reported (closing question)
