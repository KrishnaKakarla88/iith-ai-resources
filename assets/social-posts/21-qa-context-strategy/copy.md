--- LINKEDIN ---
Context strategy: questions that actually get asked

"A RAG agent's answers get worse after you increase top_k from 3 to 15 retrieved chunks. Why, and what would you check first?" Lost-in-the-middle: more chunks means more content to weigh, and relevant facts placed mid-context get attended to less reliably than facts near the start or end — even though they're technically in the window. Check retrieval precision first: are the top 3 already right, and 4-15 just noise? Often the fix is retrieving less, not more.

"What's the practical difference between prompt engineering and context engineering, and why does an interviewer care which term you use?" Prompt engineering is wording one instruction well. Context engineering is the superset decision, per call, over everything that enters the window. An interviewer asking this is checking whether you think about failure as "the prompt was worded wrong" versus "the wrong things were in context" — the second framing is what production debugging actually looks like.

"A stakeholder asks: why don't we just fine-tune the model on our FAQ and skip the RAG pipeline?" FAQ content changes — new products, updated policies, corrected answers. Fine-tuning bakes a snapshot of today's FAQ into frozen weights that goes stale the moment content changes, requiring a full retrain to fix even one wrong fact. RAG swaps the underlying documents — a content update is a re-index, not a retrain.

"Why isn't 'the model has a 1M-token window now' actually good news for someone maintaining a support-bot's memory strategy?" It removes the hard-limit failure mode but not the quality-degradation one — a bigger window still costs more the fuller it gets, still suffers attention dilution, and now tempts a team to skip building real memory/compression because "it fits."

#AppliedAI #LLM #AIEngineering #RAG

--- INSTAGRAM ---
Context strategy: questions that get asked 🧩

top_k 3→15 made answers worse? Lost-in-the-middle — check retrieval precision first.

Prompt vs. context engineering — wording vs. everything in the window.

"Just fine-tune the FAQ?" FAQs change; fine-tuning bakes in a stale snapshot.

1M window removes the hard limit, not the quality problem.

#AppliedAI #LLM #AIEngineering #RAG #GenAI

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Context Strategy: Questions That Actually Get Asked"
2. Question 1 — top_k 3→15 Made Answers Worse (code: top_k = 3  # fewer, higher-precision chunks beat more, noisier ones)
3. Question 2 — Prompt vs. Context Engineering
4. Question 3 — "Just Fine-Tune The FAQ?"
5. Question 4 — Why A 1M Window Isn't Good News
6. Takeaway — closing question

--- SCHEDULE ---
Wed 9/23: IG 6pm · LinkedIn 4pm
