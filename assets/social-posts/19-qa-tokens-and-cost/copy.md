--- LINKEDIN ---
Tokens & cost: questions that actually get asked

"Your team estimated a chatbot's monthly bill using '1 token ≈ 1 word.' Production comes in 40% over budget. What went wrong?" The heuristic is a rough English-prose average, not a rule — subword tokenization splits rare words, punctuation, and non-English text into multiple tokens, and structured payloads (JSON, code, IDs) tokenize even less efficiently per character. The fix is to stop estimating and measure: run the real system prompt, few-shot examples, and a sample of real user turns through the actual tokenizer.

"Two models claim the same '128K context window.' Why might one cost noticeably more?" Window size and per-token price are independent axes — a bigger window changes what fits, not what it costs per token. A larger window also tempts you to stuff in more retrieved content or history by default, raising your realized token count before price differences even enter the picture.

"Why would you deliberately choose a model with a smaller context window?" It forces discipline — it caps how much can accumulate before you're forced to summarize, prune, or retrieve selectively, which caps both cost and the lost-in-the-middle degradation that comes with an overstuffed window. A huge window is a ceiling you can hit, not a reason to stop engineering what goes into the call.

#AppliedAI #LLM #AIEngineering

--- INSTAGRAM ---
Tokens & cost: questions that actually get asked 💸

"1 word ≈ 1 token" is an average, not a rule — measure with the real tokenizer.

Window size and per-token price are independent axes.

A smaller window forces discipline — caps cost and lost-in-the-middle risk.

Which of these have you actually been asked?

#AppliedAI #LLM #AIEngineering #GenAI

--- VISUAL FORMAT ---
carousel — 5 slides
1. Title — "Tokens & Cost: Questions That Actually Get Asked"
2. Question 1 — The 40% Over-Budget Estimate (code: litellm.token_counter(...))
3. Question 2 — Same 128K, Different Price
4. Question 3 — Why Pick A Smaller Window?
5. Takeaway — closing question

--- SCHEDULE ---
Mon 9/21: IG 7pm · LinkedIn 10am
