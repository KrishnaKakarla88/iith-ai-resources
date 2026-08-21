# 00-ai-and-llm-basics — interview fire round

### what-is-an-llm

- **Q: Does an LLM "understand" your question, or predict it?**
  A: Neither in a human sense — it samples the next token from a learned probability distribution, repeated one token at a time, informed by everything before it in the input. There's no separate comprehension step.
- **Q: Why can't an LLM tell you today's weather?**
  A: Its knowledge is frozen at a training cutoff and lives entirely in its weights — there's no live connection to the outside world. It needs a tool call to fetch anything current.

### tokens-and-tokenization

- **Q: Why can't an LLM reliably count the letters in a word?**
  A: It never sees individual letters — the word is tokenized into one or more subword tokens, and the model reasons over token IDs, not characters.
- **Q: Why does pricing differ between English prose and, say, JSON or code?**
  A: BPE vocabularies are built from natural-language-heavy training corpora, so structured/dense text (JSON keys, code, IDs) tends to tokenize less efficiently — more tokens per character than plain English.

### how-llms-generate-text

- **Q: Why does the same prompt sometimes produce a different answer on two separate calls, even at `temperature=0`?**
  A: `temperature=0` is near-deterministic, not guaranteed — floating-point non-determinism, batching effects on the provider's infrastructure, or minor backend changes can still produce slightly different output.
- **Q: What's the practical difference between `temperature` and `top_p`?**
  A: Temperature reshapes the whole probability distribution (flatter or peakier); `top_p` instead truncates the distribution to its most-probable cumulative mass before sampling. They're two different levers on the same step — the lab's guidance is to tune one, not stack both.

### context-windows-and-limits

- **Q: Does a 1M-token context window mean you never have to think about context limits again?**
  A: No — it moves the ceiling further away, it doesn't remove it. A big-enough conversation with tools and retrieved content still fills it, and (per [[context-rot-and-long-context-management]]) quality can degrade well before the hard limit is reached.
- **Q: Why does a 50-turn conversation cost noticeably more than a 2-turn one, given the same model?**
  A: Every turn resends the full history from turn 1 onward — there's no incremental "just the new part" billing. All of it is tokenized and billed again, every single call.

### prompting-basics

- **Q: If the model has no memory between calls, how does a chatbot seem to remember what you said earlier?**
  A: Your application resends the entire message history — system, user, and assistant turns — on every single call. The illusion of memory lives in your code's growing list, not in the model.
- **Q: When would you reach for few-shot over zero-shot?**
  A: When the expected output format or style is easier to demonstrate than to describe in words — a few worked examples often pin down a pattern more reliably than a longer written instruction, at the cost of extra tokens on every call.

### prompt-engineering-techniques

- **Q: Does asking a model to "return valid JSON" guarantee it will?**
  A: No — the request itself is just wording. Reliability comes from pairing it with an actual enforcement mechanism (JSON mode, schema-constrained decoding) and a validation layer on top, not from the phrasing alone.
- **Q: Why does chain-of-thought prompting tend to help on multi-step reasoning tasks specifically?**
  A: Generation is sequential and autoregressive — a model that writes out intermediate reasoning has that reasoning available as context for the tokens that follow, including the final answer, rather than having to arrive at the answer in one uninterrupted step.

### context-engineering

- **Q: How is context engineering different from prompt engineering?**
  A: Prompt engineering is about wording a single instruction well. Context engineering is the broader, per-call decision about everything that enters the window — history, retrieved facts, tool results, memory — of which the instruction's wording is only one part.
- **Q: Why can two calls with an identically-worded system prompt still produce very different quality of answers?**
  A: Because the rest of the window — what history, retrieved content, and memory got included — differs call to call. Good wording on a bad selection of context still produces a bad answer.

### context-rot-and-long-context-management

- **Q: If a fact is still technically inside the context window, is it safe to assume the model will use it correctly?**
  A: No — context rot means presence in the window doesn't guarantee it's weighted correctly, especially once it's buried in the middle of a long, noisy history. "In the window" and "effectively attended to" are different claims.
- **Q: Does upgrading to a model with a 1M-token context window solve this?**
  A: No — it moves the point at which you hit the hard ceiling further out, but doesn't change the fact that a window stuffed with irrelevant content degrades quality well before that ceiling, at any window size.
- **Q: Why does doubling the tokens in a request roughly quadruple the self-attention computation?**
  A: Self-attention compares every token against every other token — an all-pairs comparison — so the comparison grid scales roughly with the square of the sequence length, not linearly.

### model-selection-cost-latency-tradeoffs

- **Q: Why can a "worse" model on a general leaderboard still be the right production choice?**
  A: General leaderboards measure broad capability, not fit — cost, latency, data residency, and task-specific performance (a domain leaderboard, not a general one) can all rule out a top-ranked model regardless of its score.
- **Q: Why does a 50-turn conversation cost meaningfully more than a 2-turn one, beyond "more messages"?**
  A: The entire message history is resent and reprocessed on every single call (see [[what-is-an-llm]], [[prompting-basics]]) — cost and latency both scale with the full accumulated transcript, not just the newest turn.

### fine-tuning-vs-rag

- **Q: A team wants to "fine-tune the model on our latest pricing" so it always has current prices. Good idea?**
  A: No — pricing changes are exactly the "facts that change" case RAG is built for. Fine-tuning on today's prices bakes in information that goes stale the moment prices change again, requiring another retraining pass; retrieval keeps that current without touching the model at all.
- **Q: When does fine-tuning actually make sense over RAG?**
  A: When the problem is consistent *behavior* — format, tone, a checklist reliably followed — not missing or changing facts, and prompting/context engineering alone haven't made that behavior reliable enough.
- **Q: What changed about this trade-off in 2026, per course material?**
  A: Cheaper, capable open-weight models with more accessible adapter-based fine-tuning shifted the cost side of the calculation — fine-tuning a stable-behavior need became more affordable to test, not that the underlying facts-vs-behavior distinction changed.

### architecture-of-an-agentic-system

- **Q: What's the difference between a model and an agent?**
  A: A model is one replaceable component. An agent is the model plus a harness around it — the loop, the tool executor, retries, permissions, context management — and it's the harness, not the model alone, that determines whether the system feels reliable.
- **Q: Why do most real systems use several narrow agents instead of one agent with every tool?**
  A: Coordination and reliability — a single agent with dozens of tools and unbounded scope is harder to reason about, harder to bound, and harder to recover from a bad decision in. Several bounded agents, each owning a narrow decision, coordinated by an orchestration layer, keeps each piece testable and each failure contained.
- **Q: Where do guardrails and tracing fit relative to the agent loop itself?**
  A: Around it, not inside it — tracing wraps every hop as an observable span, guardrails check the final output independent of the reasoning that produced it, and retries/circuit-breakers wrap every dependency call the loop makes. None of them change what the loop itself does.

## Harder / real-interview-style

These go beyond the per-page fire round above — scenario-based questions an interviewer would actually push on, not textbook restatements. Grounded in current (2025-2026) LLM-fundamentals interview practice ([InterviewBit](https://www.interviewbit.com/llm-interview-questions-answers/), [DataCamp](https://www.datacamp.com/blog/llm-interview-questions), [MyEngineeringPath](https://myengineeringpath.dev/genai-engineer/llm-interview-questions/)) and this repo's own stack (Groq + Gemini via LiteLLM).

#### Tokens, cost, and tokenization

- **Q: Your team estimated a chatbot's monthly bill using "1 token ≈ 1 word." Production comes in 40% over budget. What went wrong, and how would you re-estimate?**
  A: The 1-word-per-token heuristic is a rough English-prose average, not a rule — subword BPE tokenization splits rare words, punctuation, and non-English text into multiple tokens, and structured payloads (JSON, code, IDs) tokenize even less efficiently per character (see [[tokens-and-tokenization]]). The fix is to stop estimating and measure: run the actual system prompt, few-shot examples, and a sample of real user turns through the provider's own tokenizer (or `litellm.token_counter(model=..., messages=...)`) rather than eyeballing word counts, because the ratio is model- and content-dependent, not a constant.
- **Q: Two models claim the same "128K context window." Why might one cost noticeably more to run the same workload?**
  A: Context window size and pricing are independent axes — a bigger window changes what *fits*, not what it *costs per token*. Two providers can size windows identically while pricing input/output tokens completely differently, and a model with a larger window also tempts you to stuff in more retrieved content or history by default, which raises your realized token count even before per-token price differences are considered (see [[model-selection-cost-latency-tradeoffs]]).
- **Q: Why would you deliberately choose a model with a *smaller* context window for a production agent?**
  A: A smaller window forces discipline — it caps how much can accumulate before you're forced to summarize, prune, or retrieve selectively, which caps both cost and the lost-in-the-middle degradation that comes with an overstuffed window (see [[context-rot-and-long-context-management]]). A huge window is a ceiling you *can* hit, not a reason to stop engineering what actually goes into the call.

#### Sampling, determinism, and generation

- **Q: A teammate sets `temperature=0` and `seed=42` and says the pipeline is now "fully deterministic, safe to unit test on exact output." Do you sign off?**
  A: No — both are "best effort," not a contract. Provider-side floating-point non-determinism, batching effects across concurrent requests on shared inference hardware, and silent backend model updates can all still change output at `temperature=0`. The right test strategy asserts on structure/behavior (does it call the right tool, does the JSON validate, does a keyword/entity appear) rather than byte-for-byte output equality.
- **Q: When would raising `temperature` actually hurt a task that "needs creativity," rather than help it?**
  A: Any task with a verifiable right answer buried in a superficially "creative" wrapper — e.g. generating a valid tool-call payload, extracting a specific field, or writing code that must compile. Higher temperature increases the odds of a plausible-looking but wrong or malformed token sequence exactly where correctness, not variety, is the actual requirement. Creativity and correctness are different axes; raising temperature only ever costs you on the correctness one.
- **Q: Why does chain-of-thought prompting sometimes make small/fast models (like an 8B model) *worse*, not better?**
  A: CoT works because generation is autoregressive — earlier reasoning tokens become context for later ones — but that only helps if the intermediate reasoning is itself likely to be correct. A smaller model's reasoning steps are less reliable, so a bad early step compounds into a worse final answer instead of the self-correction a stronger model can sometimes achieve; forcing verbose CoT on a small fast model can also just burn latency/tokens for no accuracy gain, which is one reason this stack pairs Groq's small fast model with tight, structured prompts rather than long free-form reasoning chains.

#### Context management and prompting strategy

- **Q: A RAG-backed agent's answers get *worse* after you increase `top_k` from 3 to 15 retrieved chunks. Why, and what would you check first?**
  A: This is the lost-in-the-middle / context-rot effect — more retrieved chunks means more content the model has to weigh, and relevant facts placed mid-context get attended to less reliably than facts near the start or end, even though they're technically "in the window" (see [[context-rot-and-long-context-management]]). Before assuming you need a bigger window or a better model, check retrieval precision (are the top 3 already the right chunks, and 4-15 are noise?) and whether reranking or a smaller, higher-precision `top_k` fixes it — often the fix is retrieving *less*, not stuffing in more.
- **Q: What's the practical difference between "prompt engineering" and "context engineering," and why does an interviewer care which term you use?**
  A: Prompt engineering is wording one instruction well; context engineering is the superset decision, per call, over everything that enters the window — system prompt, retrieved chunks, memory, tool results, and history (see [[context-engineering]]). An interviewer asking this is usually checking whether you think about failure as "the prompt was worded wrong" (a small, local fix) versus "the wrong things were in context" (a systems problem spanning retrieval, memory, and history management) — the second framing is what production debugging actually looks like.
- **Q: A stakeholder asks "why don't we just fine-tune the model on our FAQ and skip the RAG pipeline?" How do you push back?**
  A: FAQ content changes — new products, updated policies, corrected answers — and fine-tuning bakes a snapshot of "today's FAQ" into frozen weights that goes stale the moment content changes, requiring a full retraining/redeployment cycle to fix even one wrong fact. RAG keeps the same model and swaps the underlying documents, so a content update is a re-index, not a retrain (see [[fine-tuning-vs-rag]]). Fine-tuning earns its keep for consistent *behavior* (tone, format, a checklist reliably followed) — not for facts that will keep changing.
- **Q: Why is "the model has a 1M-token window now" not actually good news for someone maintaining a support-bot's memory strategy?**
  A: It removes the hard-limit failure mode but not the quality-degradation one — a much larger window still costs more per call the fuller it gets, still suffers attention dilution over a long noisy history, and now tempts a team to skip building real memory/compression (summarization, selective retrieval) because "it fits." The maintenance burden shifts from "we hit the ceiling" to "we're silently paying more and getting subtly worse answers well before the ceiling," which is a harder problem to notice and debug (see [[context-rot-and-long-context-management]], [[context-compression]]).
