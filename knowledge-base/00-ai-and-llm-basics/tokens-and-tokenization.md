---
stage: "00-ai-and-llm-basics"
tools: [tiktoken, litellm]
tags: [primer, tokens, pricing]
last_verified: 2026-08-19
verified_against: "litellm 1.96.x (this repo's pin)"
---

# Tokens and tokenization

A **token** is the unit an LLM actually reads and generates — not a word, not a character, but a chunk somewhere in between — and it's the unit both context-window limits and API pricing are measured in.

## Prerequisites
- [[what-is-an-llm]]

## In plain English

When you send text to an LLM, it doesn't see letters or whole words. A tokenizer first chops your text into smaller pieces called tokens — sometimes a whole word ("cat"), sometimes a word fragment ("token" → "tok" + "en"), sometimes a single punctuation mark. The model was trained on sequences of these token IDs, and it generates output the same way: one token at a time.

This matters for three practical reasons: (1) the context window (how much the model can "see" at once) is measured in tokens, not characters, (2) API pricing is per-token (input and output priced separately), and (3) some behavior that looks like a "word" problem is actually a token problem — e.g. asking a model to count letters in a word can fail because the model never saw individual letters, only the token(s) that word was split into.

## Core mechanics

Most current LLM tokenizers (OpenAI, and models compatible with the OpenAI tokenizer family) use **Byte Pair Encoding (BPE)**: start from individual bytes, and iteratively merge the most frequent adjacent pairs into new tokens, built from a training corpus. The result is a fixed vocabulary (tens of thousands of tokens) where common words get their own token and rarer words get split into 2+ subword pieces. This is why tokenization is called "subword" — it's a middle ground between character-level (too many tokens) and word-level (vocabulary explodes with every new word/misspelling).

Rough rule of thumb for English text: **~4 characters per token**, or **~0.75 tokens per word** (so 100 words ≈ 130-140 tokens). This is an approximation, not exact — code, non-English text, and text with lots of rare tokens (IDs, hashes, unusual names) tokenize less efficiently (more tokens per character).

| Concept | What it means |
|---|---|
| Vocabulary | Fixed set of token IDs the tokenizer/model was built with — different models can use different vocabularies |
| Encode | text → list of token IDs |
| Decode | list of token IDs → text |
| Input tokens | Everything sent to the model: system prompt + history + user message + tool schemas |
| Output tokens | Everything the model generates back |

## Sample code

Lab-sourced (Day 1 · Session 1 — `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`): counting tokens via LiteLLM, which delegates to `tiktoken` (or a model-specific tokenizer when one exists) rather than requiring you to call a tokenizer library directly:

```python
import litellm

input_tokens = litellm.token_counter(model="groq/llama-3.1-8b-instant", messages=messages)
output_tokens = litellm.token_counter(model="groq/llama-3.1-8b-instant", text=reply)
```

`token_counter` picks the right tokenizer per model where LiteLLM has one registered (OpenAI, Cohere, Anthropic, Llama family), falling back to `tiktoken`'s default encoding otherwise — useful for the cost/latency comparison table the lab builds across providers, since you don't need a different counting call per vendor.

## How this shows up in the capstone

Milestone 1 (provider-agnostic LLM client) logs input/output token counts per call as part of the cost/latency comparison — see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why can't an LLM reliably count the letters in a word?**
  A: It never sees individual letters — the word is tokenized into one or more subword tokens, and the model reasons over token IDs, not characters.
- **Q: Why does pricing differ between English prose and, say, JSON or code?**
  A: BPE vocabularies are built from natural-language-heavy training corpora, so structured/dense text (JSON keys, code, IDs) tends to tokenize less efficiently — more tokens per character than plain English.

## Production gotchas & best practices

- Lab gotcha: cost/latency comparisons must count tokens *per model*, not assume one global token-to-character ratio — different providers/models can tokenize the same string into different counts, which is why `litellm.token_counter(model=...)` takes a model argument rather than a fixed table.
- Production practice: track token usage per call (input/output separately) from day one if cost matters — bolting on cost accounting after the fact means guessing retroactively. Anthropic's [Claude tokenizer docs](https://platform.claude.com) and OpenAI's `tiktoken` both expose local, offline token counting so you can budget prompts before sending them, not just measure after the fact.

## Course vs. production

The lab counts tokens after the fact for a cost/latency comparison table. In production, token budgeting is often done *before* the call — trimming/summarizing context to fit a target token count — which is exactly the problem [[context-compression]] and [[context-rot-and-long-context-management]] address later in this KB.

## Related
- **Builds on** — [[what-is-an-llm]]
- **Feeds into** — [[context-windows-and-limits]], [[model-selection-cost-latency-tradeoffs]]

## Sources

**Lab sources**
- `lab-summaries/Day1-Session1-Foundations.md` (§ "Cost/latency/token comparison")
- `labs/Day1 Session 1 - Foundations of Reliable AI Agents.ipynb`

**Web sources**
- [tiktoken (GitHub, openai/tiktoken)](https://github.com/openai/tiktoken) — BPE algorithm, ~4 bytes/token average, accessed 2026-08-19
- [LiteLLM — Track Token & Response Usage](https://docs.litellm.ai/docs/completion/token_usage) — `token_counter` behavior, per-provider tokenizer fallback, accessed 2026-08-19
