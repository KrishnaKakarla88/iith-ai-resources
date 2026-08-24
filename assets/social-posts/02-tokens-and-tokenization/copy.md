--- LINKEDIN ---
Tokens: the real unit an LLM reads

Not a word. Not a character. A chunk somewhere in between — and it's the unit both context limits and API pricing are measured in.

Most tokenizers use Byte Pair Encoding: start from bytes, merge frequent pairs into a fixed vocabulary. Common words get one token; rarer words split into two or more subword pieces. Rough rule for English: ~4 characters per token, or ~0.75 tokens per word — code, IDs, and non-English text tokenize less efficiently.

The one that trips people up: a model can't reliably count letters in a word. It never sees individual letters — only the token IDs that word got split into. Not a reasoning bug, a visibility bug.

Full mechanics — BPE, the ratio, and the token_counter code — in the carousel.

Where in your pipeline are you still estimating tokens instead of counting them?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Tokens: the real unit an LLM reads 🔢

Not a word, not a character — a chunk in between. Context limits and pricing are both measured here.

~4 characters per token for English. Code and IDs tokenize worse.

It can't count letters in a word because it never saw the letters — only the tokens.

Where are you still estimating tokens instead of counting them?

#AppliedAI #LLM #AIEngineering #GenAI #PromptEngineering

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Tokens: The Real Unit An LLM Reads"
2. Concept 1 — What A Token Actually Is
3. Concept 2 — The Rough Ratio
4. Concept 3 — What Tokens Actually Control (code: litellm.token_counter(...))
5. Concept 4 — Why It Can't Count Letters
6. Takeaway — closing question

--- SCHEDULE ---
Thu 8/27: IG 9am · LinkedIn 1pm
