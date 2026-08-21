THE FOUR-DAY ARC
Four Questions, One Progression
Each day answers one question — and its answer becomes the next day's starting point.
DAY 1 · 01 AUGUST 2026 · TODAY
1
Engineering Reliable Single-Agent Systems
How does an LLM become software?
DAY 2 · 02 AUGUST 2026
2
Knowledge, Memory and Retrieval
How does software become intelligent?
DAY 3 · 08 AUGUST 2026
3
Building Multi-Agent Systems
How does intelligence become autonomous?
DAY 4 · 09 AUGUST 2026
4
Production AI Engineering
How does autonomy become production-ready?

User Request
DAY 1 · 01 AUGUST 2026
Context Engineering
Engineering Reliable Single-Agent
Instruction Engineering
Systems
Memory Engineering
Knowledge Engineering
“How does an LLM become software?”
Reasoning Engine
Planning Engine
Tools
Agent Runtime
Evaluation
Observability
Production

Day 1 · 01 August 2026
SESSION 1
Understanding the Agent Runtime & Structured
Outputs
“Teach the AI to Speak Reliably”
11:30 – 13:30
Milestone 1 · Provider-agnostic LLM client + structured intake

Day 1 · Session 1
By the end of this session, three ideas will matter more than any
other
|     | 1   |     | 2   |     | 3   |
| --- | --- | --- | --- | --- | --- |
Every API call starts from zero — Prompt engineering became one  Fluent language isn't validated data
your application fakes memory by  room in a bigger house: context  — constrain the shape, then check
resending the whole history, every  engineering is deciding what goes  the values, before your code ever
| time. |     | into the window, on every call. |     | trusts a number. |     |
| ----- | --- | ------------------------------- | --- | ---------------- | --- |

Day 1 · Session 1 · Understanding the Agent Runtime & Structured Outputs
ACT 1
What the Model Actually Does
One token at a time · why fluent isn’t correct · why nothing persists between calls

ACT 1 · AT A GLANCE
How does one call to an LLM actually work?
It composes an answer one token at a time
...and doesn’t remember doing it a moment later
✓ Built one token at a time — each word is a
guess informed by everything before it, not a
lookup
✓ Fluent isn’t the same as correct — a confident,
well-formed answer can still be wrong
✓ Nothing persists between calls —
“conversation” is your app resending
everything, every time
Source: Stateless vs Stateful LLM Architectures -The Hidden Cost You're Ignoring

ACT 1 · QUESTION 1
What happens the instant you send Claude or GPT a
message?

ACT 1 · QUESTION 1 — THE RATIONALE
LLM API call (under the hood) What is Tokenization?
process of breaking raw data into tokens and vice versa
Tokenizer converts data into unique numerical IDs to represent
these tokens before training or generating responses
[Video] Let's build the GPT Tokenizer
Source: LLM Tokenizers Explained: BPE Encoding, WordPieceand SentencePiece
Source: What Actually Happens When You Press ‘Send’ to ChatGPT

ACT 1 · QUESTION 1 — THE RATIONALE
Transformer Explainerwalks a live GPT-2 call from embedding through self-attention to next-token probabilities. Look at the self-attention grid
(C2): every token is compared against every other token. Double the tokens in a request, and that grid roughly quadruples — the mechanical
reason a longer conversation costs more and takes longer, not just "more data."
Source: Transformer Explainer -Learning LLM Transformers with Interactive Visual Explanation and Experimentation

ACT 1 · QUESTION 1 — THE RATIONALE
What is Next-Token Prediction?
One token at a time Hedging is a byproduct No built-in type system
Each output token is sampled from a ‘Around,’ ‘approximately,’ ‘it seems’ are The model doesn't know 450 needs to be a
probability distribution over everything natural outputs of training on human text — float vs. a string —that contract is yours to
written before it —there's no separate not a flag your code can detect impose, downstream
‘extract the number’ step
Source: Reference explainer on autoregressive language modeling and transformer decoding

ACT 1 · QUESTION 1 — THE ANSWER
One Token, Informed by Everything Before It
One token at a time No separate "understanding" step Attention looks back at all of it
Each output token is sampled from a There's no hidden extraction phase —just “Conversation” is an illusion your application
probability distribution over everything the next most likely token, repeated maintains, not the API
written so far

ACT 1 · QUESTION 1 — REMEMBER IT THIS WAY
“
A brilliant consultant with total amnesia — reads the entire case file before every
sentence, then forgets it instantly.
Statelessness isn't a limitation to apologize for — it's what makes the API scale.

ACT 1 · QUESTION 2
The model just said 'the total is around $450' — is that a
number your code can trust?

ACT 1 · QUESTION 2 — SEE IT WORKING
What Your Code Actually Receives
Model's raw output
"Looking at the invoice, the total comes to around $450,
though the tax line is a bit unclear.“
Your code tries
total = float(response)
→ ValueError: could not convert string to float
What you need instead
{"total": 450.00, "currency": "USD", "confidence": "tax_unclear"}
The model isn't being difficult — it was trained to sound like this. Getting the second block is the whole job of Act 3, later today.

ACT 1 · QUESTION 2 — THE ANSWER
Fluent Language ≠ Validated Data
Trained for fluency “Around $450” isn't a float Downstream needs certainty
Not trained to produce parseable, typed data “Unclear” isn't a schema Databases and business logic need typed
data every time

ACT 1 · QUESTION 2 — REMEMBER IT THIS WAY
“
A brilliant essayist (language model) asked to fill out a tax form in prose — output
is fluent, persuasive, useless. Accounting needs a number in a cell, not a paragraph.
Two mechanisms close this gap: constrain the shape, then validate the values.

ACT 1 · QUESTION 3
If nothing about the model persists between calls, how
does a chatbot seem to remember what you said 10
messages ago?

ACT 1 · QUESTION 3 — SEE IT WORKING
The Array, Growing Turn by Turn
Turn 1 —2 messages sent (~40 tokens)
messages = [
{"role": "system", "content": "You are support for Acme Shipping."},
{"role": "user", "content": "My order hasn't arrived."}
]
Turn 2 —4 messages sent (~95 tokens) —everything above, resent
messages = [ ...same 2 messages as Turn 1...,
{"role": "assistant", "content": "Sorry to hear that — order number?"},
{"role": "user", "content": "It's #48213."}
]
Turn 3 —6 messages sent (~210 tokens) —everything above, resent again
messages = [ ...same 4 messages as Turn 2...,
{"role": "assistant", "content": "Thanks — shipped 2 days ago, in transit."},
{"role": "user", "content": "Exactly when will it arrive?"}
]
Nothing here is new for the model to "catch up" on —it's the same first messages, typed out again, on every single call.

ACT 1 · QUESTION 3 — THE ANSWER
Every Call Starts From Zero
| Stateless by design | History is replayed | Your app fakes it |
| ------------------- | ------------------- | ----------------- |
Each API call has zero knowledge of any call  The full message list is resent, from message  “Conversation” is an illusion your application
| before it | 1, every time | maintains, not the API |
| --------- | ------------- | ---------------------- |

ACT 1 · QUESTION 3 — REMEMBER IT THIS WAY
“
Meet your newest analyst: brilliant, and completely amnesiac — they reread the
entire case file before every sentence, then forget it instantly the moment they're
done.
Statelessness isn't a limitation to apologize for — it's what makes the API scale.

ACT 1 · Nothing Remembers — And That Changes Everything​
QUICK CHECK — NO PEEKING
Before we move past What the Model Actually Does:
Without looking back — does the model understand your sentence, or predict it one
1
token at a time?
Why can a fluent, confident answer still be wrong?
2

DAY 1 · SESSION 1
ACT 1 · DEEP DIVE
Nothing Remembers, And That Changes Everything
Statelessness · the message list as the entire conversation · why cost and latency compound
| START HERE — |                                           | 3 THINGS |
| ------------ | ----------------------------------------- | -------- |
| 1            | Vaswani et al., Attention Is All You Need |          |
arxiv.org/abs/1706.03762
The architectural reason statelessness exists.
| 2   | Atlan — | Why AI Agents Forget: The Stateless LLM Problem |
| --- | ------- | ----------------------------------------------- |
atlan.com/know/why-ai-agents-forget
The clearest single explanation of why continuity has to be engineered around the model rather than expected from it.
| 3   | ByteByteGo — | A Guide to Context Engineering for LLMs |
| --- | ------------ | --------------------------------------- |
blog.bytebytego.com/p/a-guide-to-context-engineering-for
Connects statelessness to the practical discipline that follows from it.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 20 resources in all, in the companion Deep Dive
Resources guide (Day 1, Act 1).

Day 1 · Session 1 · Understanding the Agent Runtime & Structured Outputs
ACT 2
What That Costs You
The context window · why longer conversations cost more · deciding what earns a seat in it

ACT 2 · AT A GLANCE
What enters the context window?
Context Window = Instructions + Conversation + Reasoning + External Knowledge & Tools

ACT 2 · AT A GLANCE
Why the context window matters?
The larger the context, the more the model can consider at once. But once
the window fills up, older or less relevant information may be pushed out.

ACT 2 · QUESTION 1
Why does a 50-turn conversation get slower and more
expensive than a 2-turn one?

ACT 2 · QUESTION 1 — THE RATIONALE
What happens when you increase Context Length of an LLM Model?
Source: What happens when you increase Context Length of an LLM Model?

ACT 2 · QUESTION 1 — SEE IT WORKING
Run the Numbers on Your Own Agent
The formula
tokens/day = (tokens/turn) x (turns/session) x (sessions/day)
cost/day = ( (tokens/day) / 1,000,000 ) x price per 1M tokens
Plugged in for one support flow
~200 (tokens/turn) x 20 (turns/session) = 4,000 tokens by the last turn
4,000 (tokens/session) x 500 (sessions/day) = 2,000,000 tokens/day
( (2,000,000 tokens/day) / 1,000,000 ) x $2.50 = $5/day — for ONE untrimmed flow
Change one number — turns per session, price per token, sessions per day — and rerun this. That's the exact arithmetic your Milestone 1 client
needs to survive a real conversation.

ACT 2 · QUESTION 1 — THE ANSWER
You're Paying for the Whole Transcript, Every Time
| The array grows | Cost scales with history | Latency compounds |
| --------------- | ------------------------ | ----------------- |
system → user → assistant → user… every  Every token in that array is billed and  More tokens in, more time to first response
| turn appended | processed again |     |
| ------------- | --------------- | --- |
A 6-token query can become a 40,000-token  100K tokens/request ×1,000 req/day =  1K → 128K tokens: time-to-first-token
request once tools + history attach $250/day —10x an untrimmed history jumps ~200x, past 30 seconds

ACT 2 · QUESTION 1 — REMEMBER IT THIS WAY
“
Every question means photocopying that same case file in full, from page one —
no wonder it gets slower and pricier as the file grows.
There's a hard resource this is competing for — how much can you send at once?

★ WHAT'S NEW · 2026
ACT 2 · QUESTION 2
The context window: what's the room you're actually
talking in?

ACT 2 · QUESTION 2 — THE RATIONALE
Should larger context windows be implemented in LLMs?
Source: Cutting Tokens by 40% to Lower LLM API Costs Using a Memory-Efficient Algorithm
Computational Cost Performance Issues
Larger context windows require significantly more Key information may be lost in long contexts, reducing
processing power, increasing operational costs. model effectiveness

ACT 2 · QUESTION 2 — THE RATIONALE
What is context rot?
LLM’s performance degradation during a long session
happens because noise—failed attempts and irrelevant
data—distracts the model, weakening its ability to find
and apply your core rules
Source: LLMs Get Lost In Multi-Turn Conversation
Source: Context Rot -Why Claude Code Sessions Decay, and How to Govern Them

ACT 2 · QUESTION 2 — THE RATIONALE
What to include in the context window?
|     | Does it use  |     | Does it become future  |     |     |
| --- | ------------ | --- | ---------------------- | --- | --- |
Item
context window? context?
| User prompt    |                    | Yes        |                           |        | Yes |
| -------------- | ------------------ | ---------- | ------------------------- | ------ | --- |
| System prompt  |                    | Yes        | Usually yes, while active |        |     |
| Uploaded file  |                    | Yes, when  | Sometimes, depending on   |        |     |
| content        | included/retrieved |            |                           | system |     |
Often yes, if included in
| Tool/RAG results |     | Yes |     |     |     |
| ---------------- | --- | --- | --- | --- | --- |
conversation state
| Internal reasoning |     | Yes |     | Usually no |     |
| ------------------ | --- | --- | --- | ---------- | --- |
| Final answer       |     | Yes |     |            | Yes |

ACT 2 · QUESTION 2 — SEE IT WORKING
Watch the Wheels Come Off
Turn 1
User: "Always confirm the customer's email before sharing account details.“
Turn ~15 (thousands of tokens of history later — several tool calls, a couple of failed attempts)
...ordinary back-and-forth continues; the Turn-1 rule is still technically in the window...
Turn ~36 (32,000+ tokens of history now)
Assistant shares account details without confirming the email first.
Nothing left the context window. The Turn-1 rule is still in there, mathematically. It just stopped being the loudest thing attention was listening
to, buried under 35 turns of noise.

ACT 2 · QUESTION 2 — THE ANSWER
A Room With a Fixed Number of Chairs
| Tokens, not words | Everything shares the room | Bigger ≠ solved |
| ----------------- | -------------------------- | --------------- |
~4 characters per token in English System + history + input + reserved output,  Kimi K3's 1M-token window moves the wall
|     | all counted together | —it doesn't remove it |
| --- | -------------------- | --------------------- |

ACT 2 · QUESTION 2 — REMEMBER IT THIS WAY
“
That case file has to fit in one physical binder — a fatter binder just moves the day
it stops closing, it doesn't remove the day.
A bigger window changes WHEN you hit the wall, not WHETHER you do.

★ WHAT'S NEW · 2026
ACT 2 · QUESTION 3
You can't send everything, and you can't send nothing —
whose job is it to decide what makes the cut?

ACT 2 · QUESTION 3 — THE RATIONALE
What are Prompts?
a means to interact with AI models
The goal is to provide the AI model with sufficient
context, information, and guidance to generate a
meaningful and accurate response
A prompt contains any of the following elements
✓ Instruction - a specific task or instruction you want
the model to perform
✓ Context - external information or additional context
that can steer the model to better responses
✓ Input Data - the input or question that we are
interested in finding a response for
✓ Output Indicator - the type or format of the output.
Source: The Importance of Prompt Engineering in Natural Language Systems Source: An Introduction to Large Language Models: Prompt Engineering and P-Tuning

ACT 2 · QUESTION 3 — SEE IT WORKING
Same Task, Two Very Different Calls
Prompt engineering only Context engineered
"You are a helpful assistant. System: "Acme Shipping support.
Answer the customer's question Be concise."
about their order as clearly and
+ Retrieved fact:
politely as possible, using good
"#48213 — shipped 2 days ago,
judgement, in the style of a
in transit, ETA Thursday"
professional support agent,
considering all relevant + Trimmed history: last 2 turns
company policies...“
+ Tool result: "Out for delivery"
(one long static instruction —no real data)
The left column is all wording. The right column is a decision, made fresh on every call, about what earns a seat in the window — that decision is context
engineering.

ACT 2 · QUESTION 3 — THE ANSWER
Prompting Became One Room in a Bigger House
Prompting = wording Context = everything The job title moved, not the work
One instruction, worded well —necessary, System prompt + history + retrieved facts + "Prompt engineer" postings quietly faded
not sufficient tools + memory, curated every call 2023-2025 —folded into a bigger “Context
Engineering”, still-growing discipline

ACT 1 · QUESTION 3 — REMEMBER IT THIS WAY
“
A theater director doesn't just write good lines — they control lighting, blocking, the
whole stage.
Every session this week is really asking: what goes into the window, and when?

Day 1 · Session 1
QUICK CHECK — NO PEEKING
Before we move past What That Costs You:
In one sentence, why does a 50-turn conversation cost more than a 2-turn one?
1
Does a one million-token window remove the context-ceiling problem?
2

DAY 1 · SESSION 1
ACT 2 · DEEP DIVE
Choosing What Goes In, and Who Answers
The context window as a hard ceiling · long-context evaluation · the 2026 model landscape
START HERE — 3 THINGS
1 Chroma — Context Rot: How Increasing Input Tokens Impacts LLM Performance
trychroma.com/research/context-rot​
The single most load-bearing reference on this day.
2 Kelly Hong (Chroma) — Context Rot: When Long Context Fails
maven.com/p/37bdf2/context-rot-when-long-context-fails​
The talk version of the paper, with a Q&A section on detecting context rot in your own application.
3 Hsieh et al., RULER: What’s the Real Context Size of Your Long-Context Language Models?
arxiv.org/abs/2404.06654​
Turns needle-in-a-haystack into a configurable suite covering retrieval, variable tracking and aggregation.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 19 resources in all, in the companion Deep Dive
Resources guide (Day 1, Act 2).

Day 1 · Session 1 · Understanding the Agent Runtime & Structured Outputs
ACT 3
Making It Speak Data, Not Prose
Why fluent text fails your code · shape-valid vs. value-valid · the repair loop

ACT 3 · QUESTION 1
The model just said something fluent — how do you get
an actual number or field out of it?

ACT 3 · QUESTION 1 — THE RATIONALE
What is Structured Output?
ensure model-generated responses follow
pre-defined formats, such as
✓ A known format, like JSON
✓ A schema, like JSON Schema or a typed class
✓ A constrained set of values, like enums
✓ A validation contract, enforced in code
We usually want all four
Source: Structured Outputs: Everything You Should Know
Teams pick formats based on where the data lands
✓ JSON for APIs, pipelines, and document stores
✓ JSONL for event streams and batch processing The MCP specification (November 2025) now requires that tool
✓ CSV for interoperability with legacy tools servers return structured results conforming to an output schema
✓ YAML for configuration-like artifacts
✓ XML in enterprise integration pockets
For LLMs, JSON wins most days.

ACT 3 · QUESTION 2
A JSON-mode response can be perfectly valid JSON —
and still be a wrong answer. How do you catch that?

ACT 3 · QUESTION 2 — SEE IT WORKING
Valid JSON, Wrong Answer
The schema
class Invoice(BaseModel):
total: float
currency: str
Provider's JSON-mode output (shape-perfect)
{"total": -450.00, "currency": "XYZ"}
Pydantic catches what JSON mode can't
@field_validator("total")
def check_total(cls, v):
if v < 0: raise ValueError("total cannot be negative")
JSON mode guarantees the shape. It never once checks whether -450 or "XYZ" make sense.

ACT 3 · QUESTION 2 — THE ANSWER
Right Shape Isn't the Same as Right Answer
JSON mode / function-calling Shape ≠ value Pydantic adds the 2nd layer
The provider constrains generation to match  A perfectly-shaped object can still hold a  Validates types, constraints, and business
| a schema | wrong number | rules |
| -------- | ------------ | ----- |

ACT 3 · QUESTION 2 — REMEMBER IT THIS WAY
“
Your analyst turns in a perfectly formatted invoice — with the wrong number typed
into every field.
You need a second layer that checks values, not just shape.

ACT 3 · QUESTION 3
What do you do the moment the model's output fails
validation?

ACT 3 · QUESTION 3 — THE RATIONALE
Challenges with Structured Output
| Use case                         |     |     |     | Structured output suitability |     |     |     |     |
| -------------------------------- | --- | --- | --- | ----------------------------- | --- | --- | --- | --- |
| Extracting invoice fields        |     |     |     | Excellent                     |     |     |     |     |
| Classifying support tickets      |     |     |     | Good, if ambiguity is allowed |     |     |     |     |
| Calling tools/functions          |     |     |     | Excellent                     |     |     |     |     |
| Returning database-ready records |     |     |     | Excellent                     |     |     |     |     |
| Producing UI components          |     |     |     | Good with validation          |     |     |     |     |
| Summarizing into fixed fields    |     |     |     | Good                          |     |     |     |     |
Risky unless schema includes
Solving hard reasoning problems
reasoning-support fields
|                   |           |                     |                            |                           |            |         |            |                       |
| ----------------- | --------- | ------------------- | -------------------------- | ------------------------- | ---------- | ------- | ---------- | --------------------- |
|                   |           |                     |                            |                           |            |         |            |                       |
|                   |           |                     |                            |                           |            |         |            |                       |
|                   |           |                     |                            |                           |            |         |            |                       |
|                   |           |                     |                            |                           |            |         |            |                       |
|                   |           |                     |                            |                           |            |         |            |                       |
|                   |           |                     |                            |                           |            |         |            |                       |
Source: Structured Outputs in LLMs: Reliable Data for Real Pipelines
Structured outputs improve reliability, not intelligence.
Recommendation: Use structured outputs in stages rather than forcing the
entire reasoning process into a rigid schema. Let it extract facts in structure,
Source: Let Me Speak Freely? A Study on the Impact of Format
reason with flexibility, and then return the final answer in a strict schema.
Restrictions on Performance of Large Language Models

ACT 3 · QUESTION 3 — THE RATIONALE
What is a Self-Repair Loop?
Don't discard, feed back The smallest agentic loop Cap it, then escalate
The validation error —which field, what rule, Generate → check → act on the check → 2–3 attempts is typical; on cap exhaustion,
what value —becomes new context for a re- repeat: the exact skeleton behind every fail loudly and route to a human —never let
call pattern this week bad data flow through silently
Source: Engineering references on self-correcting structured-extraction pipelines

ACT 3 · QUESTION 3 — SEE IT WORKING
The Full Repair, In Order
1. Model's first attempt
{"total": "around 450", "currency": "USD"}
2. Pydantic's ValidationError
total: Input should be a valid number, unable to parse string as a number
3. Re-prompt sent back
"Your last response failed validation: total — unable to parse as a number.
Return total as a plain number, e.g. 450.00, with no words.“
4. Model's corrected output
{"total": 450.00, "currency": "USD"}
Attempt 1 failed, attempt 2 succeeded — using the model's own mistake as the fix. Cap this at 2-3 tries; this is the loop Milestone 1 asks you to
build.

ACT 3 · QUESTION 3 — THE ANSWER
Feed the Error Back — Don't Just Ask Again
Generate → validate → fix Cap it at 2–3 tries This is a tiny agent
Send the actual ValidationError text back as  Can't self-correct in 3 tries? Flag for a human,  Generate, check, fix —the skeleton for
| new context | don't loop forever | everything this afternoon |
| ----------- | ------------------ | ------------------------- |

ACT 3 · QUESTION 3 — REMEMBER IT THIS WAY
“
Not a scolding, a correction: circle the exact error, hand it back, let the analyst
(language model) fix their own memo.
This loop is the smallest agent you'll build this week — this afternoon, much bigger ones.

Day 1 · Session 1
QUICK CHECK — NO PEEKING
Before we move past Making It Speak Data, Not Prose:
What gets sent back to the model when validation fails?
1
Is valid JSON the same thing as a correct answer?
2

DAY 1 · SESSION 1
ACT 3 · DEEP DIVE
Making It Speak Data, Not Prose
Structured output · constrained decoding · schema validity versus value correctness · repair loops
START HERE — 3 THINGS
1 Geng et al., JSONSchemaBench
arxiv.org/abs/2501.10868​
Ten thousand real-world JSON schemas across six constrained-decoding frameworks, scored on efficiency, coverage and quality.
2 Tam et al., Let Me Speak Freely? A Study on the Impact of Format Restrictions on LLM Performance
arxiv.org/abs/2408.02442​
Argues that JSON, XML and YAML constraints degrade reasoning ability.
3 dottxt — Say What You Mean: A Response to "Let Me Speak Freely"
blog.dottxt.ai/say-what-you-mean.html​
The rebuttal, from the team behind Outlines.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 24 resources in all, in the companion Deep Dive
Resources guide (Day 1, Act 3).

Day 1 · Session 1 · Understanding the Agent Runtime & Structured Outputs
ACT 4
One Trustworthy Answer Isn’t the Whole Job
Choosing a model · provider lock-in · why the right answer keeps changing

ACT 4 · QUESTION 1
If every provider does 'the same thing,' why can't you swap
for free?

| ACT 4 · QUESTION 1 — |     | THE RATIONALE |
| -------------------- | --- | ------------- |
What is inside an LLM API call?
Not just a prompt. Now an execution contract
LLM API calls are no longer just
prompt → completion
They are now
| instructions  | + context       | + reasoning policy+ output  |
| ------------- | --------------- | --------------------------- |
| schema+ tools | + state+ safety | + runtime controls          |
→ typed response stream
API compatibility means “your request
may parse.” It does not mean the same
parameter is supported, carries the same
meaning, produces the same behaviour, or
returns the same events.

ACT 4 · QUESTION 1 — THE RATIONALE
Why are provider APIs not freely interchangeable?

ACT 4 · QUESTION 1 — SEE IT WORKING
One Task, Three SDKs, Then One Wrapper
# OpenAI
client.chat.completions.create(model="gpt-4o", messages=[...])
# Anthropic
client.messages.create(model="claude-sonnet-4-6", messages=[...], max_tokens=1000)
# Google Gemini
client.models.generate_content(model="gemini-2.0-flash", contents=[...])
# One call, any provider (LiteLLM)
completion(model="anthropic/claude-sonnet-4-6", messages=[...])
completion(model="openai/gpt-4o", messages=[...])
Same shape, three different field names, three different response objects. Milestone 1 asks you to write the layer that hides this.

ACT 4 · QUESTION 1 — THE ANSWER
Same Idea, Different Dialects
Every SDK is different Hardcoding is a trap Two options exist
OpenAI, Anthropic, Google each speak their Every other week a cheaper or better model A client library maps one call shape onto
own dialect –different field names, schemas, ships every provider (LiteLLM/ LangChain); a
model behaviour, operational contracts, and hosted proxy also handles routing and billing
streaming formats (OpenRouter)

ACT 4 · QUESTION 1 — REMEMBER IT THIS WAY
“
Three branch offices, three different intake forms, for the exact same case — you
want one form that works everywhere.
This is exactly the gap a provider-abstraction layer exists to close.

★ WHAT'S NEW · 2026
ACT 4 · QUESTION 2
Which model should you actually use, and why is that
answer changing monthly?

ACT 4 · QUESTION 2 — THE RATIONALE
What does “best model” even mean?
Do not ask: “Which model is the smartest?”
There is no single best model. There is only the
best fit for a task, budget, risk level, latency  Ask: “Which model passes my evals at the
target, and deployment constraint. lowest acceptable cost, latency, and risk?”
| General Leaderboards |                     | Task & Domain Leaderboards |                          |
| -------------------- | ------------------- | -------------------------- | ------------------------ |
| LMArena              | (blind human votes) | SWE-bench                  | and BFCLfor coding/tool- |
use
| Artificial Analysis | (composite index +  | HealthBench        | for medicine |
| ------------------- | ------------------- | ------------------ | ------------ |
| cost/speed)         |                     | LegalBench         | for law and  |
|                     |                     | FinBen for finance |              |
| LiveBench           | and llm-stats       | Vals.ai            |              |
(contamination-resistant, aggregated)
Two failure modes to know
1. Contamination (the model memorized the test) and
| 2. saturation | (everyone's bunched near the ceiling) |     |     |
| ------------- | ------------------------------------- | --- | --- |
— triangulate, don't trust one number

ACT 4 · QUESTION 2 — THE RATIONALE
What are LLM Benchmarks and Leaderboards?
General leaderboards Task & domain leaderboards Two failure modes to know
LMArena (blind human votes), Artificial SWE-bench and BFCL for coding/tool-use; Contamination (the model memorized the
Analysis (composite index + cost/speed), HealthBench, LegalBench, and FinBen for test) and saturation (everyone's bunched
LiveBench and llm-stats (contamination- medicine, law, and finance near the ceiling) —triangulate, don't trust
resistant, aggregated) one number

ACT 4 · QUESTION 2 — SEE IT WORKING
Staffing an Actual Case
Scenario
Vernacular healthcare support bot, Hindi + Telugu, 50,000 req/day, data must stay in India, budget-sensitive.
Step 1 — Rule out
Top closed frontier models: fails on cost and data-residency, regardless of benchmark score.
Step 2 — Check the right leaderboard
Task/domain boards for agentic + multilingual performance — not a general "who's smartest" board.
Step 3 — Shortlist
Qwen3.6 (35B, 3B active) — strong agentic scores, low cost, self-hostable in-country.
Step 4 — Decide, then verify
Qwen3.6, self-hosted — passes budget + residency; re-benchmark before real traffic.
Different case, different numbers, same 4 steps — reuse them for your own project brief.

ACT 4 · QUESTION 2 — THE ANSWER ★ WHAT'S NEW · 2026
The Open-Weight Tier Got Serious
Kimi K3 — 2 weeks old Qwen3.6 — small & sharp A trade-off, not a ranking
2.8T params, 1M-token context, competitive 35B params (3B active), strong agentic Cost & data residency vs. bleeding-edge
benchmarks (Moonshot AI) performance, low cost capability & support

ACT 4 · QUESTION 2 — REMEMBER IT THIS WAY
“
Staffing the case isn't 'who has the fanciest résumé' — it's fit to this budget, this
deadline, this risk.
'Open-weight = worse' stopped being reliably true in 2026 — the decision is a trade-off, not a ranking.

SESSION 1 FINALE
What is an Agent?
a software entity that can autonomously perceive its
environment, make decisions, and take actions to achieve
its goals
✓ Humans set goals, but an AI agent independently
chooses the best actions to take to achieve those goals
Key Characteristics
✓ Autonomy: Agents operate independently without
human intervention.
✓ Perception: Agents gather data from their
environment (e.g., sensors, APIs).
✓ Reasoning: Agents use logic or learning to make
decisions based on the data.
✓ Action: Agents act to change or influence the
environment (e.g., send an alert, perform a task). Source: Intro of AI agent, & AI agent projects summary
✓ Learning: How agents adapt to new situations and
improve performance over time

Day 1 · Session 1
Same three ideas — now you’ve built them
1 2 3
Every API call starts from zero — You've made the context- You have a validated, self-repairing
you now have a client that manages engineering trade-off explicit: which structured-output parser — data
the message list and swaps model, why, and what goes in the your code can actually trust.
providers freely. window.
✓ Milestone 1 · Provider-agnostic LLM client + structured intake

Source: Effective context engineering for AI agents

Day 1 · 01 August 2026
SESSION 2
Tool Use and Agent Design Patterns
“Teach the AI to Act”
14:15 – 15:30
Milestone 2 · Tool-enabled single agent

Day 1 · Session 2
By the end of this session, three ideas will matter more than any
other
1 2 3
A tool is a function the model can Agent = model + harness + tools. Reason, act, observe, repeat —
ask your app to run — the model The harness — not just the model capped, and the exact same
requests, your code always decides. — is what makes it feel reliable. primitive that powers 300-agent
swarms.

Day 1 · Session 2 · Tool Use and Agent Design Patterns
ACT 1
Giving the Model Hands
Why tools exist · designing a safe schema · idempotency

ACT 1 · QUESTION 1
An LLM alone cannot tell you today's weather. Why not?

ACT 1 · QUESTION 1 — THE RATIONALE
What is a Training Cutoff?
the date when a model's learning phase stops,
fixing its knowledge base
Key Points
✓ Knowledge, frozen: Parametric knowledge is
whatever got compressed into the weights during
training — nothing live is wired in by default.
✓ Live facts aren't knowledge: Today's weather, today's
price, a row in your database — none of that is
something a model can ‘know’.
✓ No self-initiated action: The model can't execute code
or hit an API on its own — it can only produce text,
including text shaped like a function call.
Source: ChatGPT Knowledge Cutoff: Master Its Impact in 2026

ACT 1 · QUESTION 1 — SEE IT WORKING
Same Question, No Tool vs. a Tool
Without a tool
User: "What's the weather in Hyderabad right now?"
Model: "I don't have real-time data, but Hyderabad in late
July is typically warm and humid, often 28-32°C.“
(plausible-sounding — not actually current)
With a tool
Model → calls get_weather(city="Hyderabad")
Tool returns: {"temp_c": 31, "condition": "partly cloudy"}
Model: "It's 31°C and partly cloudy in Hyderabad right now.“
Same fluent voice both times. Only one of these is actually true right now.

ACT 1 · QUESTION 1 — THE ANSWER
No Eyes, No Hands, No Live Access
Frozen at training time No live-world access The fix: give it a tool
No knowledge past its cutoff Can't execute code, hit an API, or query a A function it can ask your app to run
database on its own

ACT 1 · QUESTION 1 — REMEMBER IT THIS WAY
“
A brilliant scholar in a sealed, windowless library with no phone to access latest
information.
That access is called a tool — let's build one properly.

ACT 1 · QUESTION 2
How do you give a model 'hands' without letting it break
things?

ACT 1 · QUESTION 2 — THE RATIONALE
What is a Tool Schema?
a structured JSON definitionthat tells a LLM about an available function or API

ACT 1 · QUESTION 2 — THE RATIONALE
Anatomy of a Tool Specification
Source: Understanding Tool Specifications and Descriptions

ACT 1 · QUESTION 2 — THE RATIONALE
What is a Tool Schema?
Name, description, parameters Requests, never executes Least privilege by design
The description is the highest-leverage, The model only ever produces ‘I'd like to call Expose the narrowest tool that does the job
most-neglected field —it's effectively a X with these arguments’ —your code —a confused model has less room to cause
prompt deciding when the tool gets called decides whether to comply damage
Source: Anthropic / OpenAI tool-use documentation
Source: JSON Schema specification (json-schema.org)

ACT 1 · QUESTION 2 — SEE IT WORKING
One Real Tool Schema, Fully Annotated
{
"name": "get_weather", ← unambiguous, verb-first
"description": "Get current weather for a named
city. Use for CURRENT conditions. Do NOT use
for forecasts >24h out." ← highest-leverage field
"parameters": {
"type": "object",
"properties": {
"city": {"type": "string"},
"units": {"type": "string",
"enum": ["celsius","fahrenheit"]} ← enum, not free text
},
"required": ["city"]
}
}
The description doubles as a prompt deciding when the tool gets called —it is the field most worth rewriting twice.

ACT 1 · QUESTION 2 — THE ANSWER
The Model Requests. Your Code Decides.
Name + description + params The model never executes Vague descriptions = wrong calls
The schema —description is a prompt in  It asks; your application decides whether to  The highest-leverage, least-taught lever in
| disguise | comply | tool design |
| -------- | ------ | ----------- |

ACT 1 · QUESTION 2 — REMEMBER IT THIS WAY
“
A capable intern who can draft the email — but doesn't have the send button.
Say it plainly: the model never executes anything. It requests.

ACT 1 · QUESTION 3
Should tools be safe to call more than once by accident?

ACT 1 · QUESTION 3 — THE RATIONALE
What is Idempotency?
ensures that executing an identical request multiple times produces the same server state and result as running it just once
Source: Idempotency -The Key to a Robust Distributed System

ACT 1 · QUESTION 3 — SEE IT WORKING
The Same Call, Twice, By Accident
Not idempotent
def book_room(date):
return db.insert(Booking(date=date))
# Called twice by accident → two bookings, same room, same day
Fixed with an idempotency key
def book_room(date, idempotency_key):
existing = db.find(Booking, key=idempotency_key)
if existing: return existing
return db.insert(Booking(date=date, key=idempotency_key))
# Called twice by accident → same booking returned both times
One line of extra state turns a dangerous retry into a safe one — the check Milestone 2 asks you to add before any tool runs in parallel.

ACT 1 · QUESTION 3 — THE ANSWER
Parallel Only Works If It's Safe to Repeat
Parallel tool calls exist Idempotency is the precondition A GET is safe; a charge isn't
Weather + currency + calendar, requested in Calling it twice by accident must cause no Design for safety before you design for speed
one turn harm

ACT 1 · QUESTION 3 — REMEMBER IT THIS WAY
“
An elevator button (press twice, nothing extra happens) vs. a payment form (press
twice, charged twice).
Design tools to be safe to retry before you make them parallel-callable.

Day 1 · Session 2
QUICK CHECK — NO PEEKING
Before we move past Giving the Model Hands:
In one sentence — who actually executes a tool call?
1
Name a tool that is NOT safe to call twice.
2

DAY 1 · SESSION 2
ACT 1 · DEEP DIVE
Giving the Model Hands
Tool use and function calling · schemas as safety boundaries · idempotency
START HERE — 3 THINGS
1 Schick et al., Toolformer: Language Models Can Teach Themselves to Use Tools
arxiv.org/abs/2302.04761​
The paper that established the shape of the problem.
2 Yao et al., τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains
arxiv.org/abs/2406.12045​
Evaluates whether an agent reaches the right end state in realistic multi-step customer-service tasks, rather than whether a single call was…
3 Berkeley Function Calling Leaderboard (BFCL)
gorilla.cs.berkeley.edu/leaderboard.html​
The function-calling primitive measured directly.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 19 resources in all, in the companion Deep Dive
Resources guide.

Day 1 · Session 2 · Tool Use and Agent Design Patterns
ACT 2
Making It Reliable, Making It Think
Retries and circuit breakers · the agent harness · the ReAct loop

ACT 2 · QUESTION 1
What happens when a tool call fails at 2am with nobody
watching?

ACT 2 · QUESTION 1 — THE RATIONALE
What are Retry-with-Backoff and Circuit Breakers?
Backoff assumes transient Circuit breaker assumes broken
Wait 1s, then 2s, then 4s, often with Closed → Open (stop calling after N
jitter —protects a struggling service failures) → Half-open (test one call
from a retry storm after cooldown)
Standard, not LLM-specific
Originates from Netflix's Hystrix; today
implemented via resilience4j and
equivalents for any service call
Source: Retry, Backoff, Circuit Breakers –
Making Systems Fail Gracefully
Source: Michael Nygard, Release It!
Source: Netflix Hystrix / resilience4j documentation

ACT 2 · QUESTION 1 — SEE IT WORKING
One Bad Minute, Handled
0.0s — Attempt 1 → tool times out
1.0s — wait, then Attempt 2 → fails again
3.0s — wait (2s), then Attempt 3 → succeeds ✓
...but if it keeps failing
5 failures in 60s → circuit OPENS → stop calling for 30s
30s later → ONE test call (HALF-OPEN) → success → circuit CLOSES
Retries assume "probably transient." A circuit breaker assumes "probably broken" — and stops hammering a service that's already
down.

ACT 2 · QUESTION 1 — THE ANSWER
Assume Failure. Design For It.
| Retry with backoff | Circuit breaker | Log everything |
| ------------------ | --------------- | -------------- |
Wait, then retry, waiting longer each time After N failures, stop and fail fast rather than  You cannot debug an agent you can't see
|     | retry forever | inside |
| --- | ------------- | ------ |

ACT 2 · QUESTION 1 — REMEMBER IT THIS WAY
“
A home circuit breaker — trips on a real fault instead of letting the wiring
overheat.
'Log every tool call and result' matters starting now, not just during deployment.

★ WHAT'S NEW · 2026
ACT 2 · QUESTION 2
Why does Claude Code feel like a coworker, not a chatbot?

ACT 2 · QUESTION 2 — THE RATIONALE
What is an Agent Harness?
Everything around the model Instructions as files Model ≠ product
The loop, tool executor, permissions, context CLAUDE.md / AGENTS.md / SKILL.md give The same model in two different harnesses
management, and UI — the model is one the harness durable, project-specific can feel completely different —the harness
replaceable piece inside it instructions without retraining anything does real work
Source: Anthropic engineering commentary on agent harness design

ACT 2 · QUESTION 2 — THE RATIONALE
Source: Instructions.md vs Skills.md vs Agent.md vs Agents.md

ACT 2 · QUESTION 2 — THE RATIONALE
Source: Agent Harness

ACT 2 · QUESTION 2 — SEE IT WORKING
What's Actually Inside a Harness
agent/
├── SYSTEM_PROMPT.md ← durable instructions, not retrained
├── tools/ ← schemas + the functions they call
├── executor.py ← runs tool calls, retry + circuit breaker
├── logger.py ← every call and result, logged
└── loop.py ← the ReAct/planning loop tying it together
The model is one line inside executor.py. Swap it, and everything else still stands.

ACT 2 · QUESTION 2 — THE ANSWER
Agent = Model + Harness
The harness, not just the model Claude Code, Codex CLI, OpenCode Instructions as files
The loop, executor, retries, permissions, All harnesses wrapped around a INSTRUCTIONS.md / AGENTS.md / SKILLS.md
context management (replaceable) model

ACT 2 · QUESTION 2 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
A great analyst alone isn't a reliable firm — it's the analyst plus the playbook, the
review process, the org chart around them.
Say it and mean it: model ≠ agent. Agent = model + harness.

ACT 2 · QUESTION 3
Given 5 tools, how does the model decide what to call, in
what order?

ACT 2 · QUESTION 3 — THE RATIONALE
What is the ReAct Pattern?
Source: 7 Must-Know Agentic AI Design Patterns

ACT 2 · QUESTION 3 — SEE IT WORKING
One Question, Traced Step by Step
User: "What's the weather in Hyderabad, in Fahrenheit?"
Thought: I need the current temperature in Hyderabad first.
Action: get_weather(city="Hyderabad")
Observation: {"temp_c": 31}
Thought: The user wants Fahrenheit, so I need to convert.
Action: convert(31, "C", "F")
Observation: {"result": 87.8}
Answer: "It's 87.8°F in Hyderabad right now.“
Five tools, capped iterations, this exact shape — that's today's lab, and the same primitive Act 3 scales to 300 agents.

| ACT 2 · QUESTION 3 — | THE ANSWER |               |     |     |
| -------------------- | ---------- | ------------- | --- | --- |
| Thought →            | Action →   | Observation → |     |     |
Repeat
|     | Thought |     | Action | Observation |
| --- | ------- | --- | ------ | ----------- |
The model reasons in text about what to do  It calls a tool The result comes back, and the loop
|     | next |     |     | continues |
| --- | ---- | --- | --- | --------- |

ACT 2 · QUESTION 3 — REMEMBER IT THIS WAY
“
Your analyst, narrating their own case notes out loud — check this, note that,
conclude — one step at a time.
Loops until the model decides it's done — but what stops it running forever?

Day 1 · Session 2
QUICK CHECK — NO PEEKING
Before we move past Making It Reliable, Making It Think:
Fill in the blank: Agent = ___ + ___ + ___.
1
What are the three steps of the ReAct loop?
2

DAY 1 · SESSION 2
ACT 2 · DEEP DIVE
Making It Reliable, Making It Think
The agent harness · retries and circuit breakers · the ReAct loop
START HERE — 3 THINGS
1 Yao et al., ReAct: Synergizing Reasoning and Acting in Language Models
arxiv.org/abs/2210.03629
The loop underneath almost everything else in this course.
2 Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning
arxiv.org/abs/2303.11366
Self-critique that persists across attempts.
3 Gabriel Anhaia — ReAct, Plan-and-Execute, or Reflection? (DEV, 2026)
dev.to/gabrielanhaia/react-plan-and-execute-or-reflection-the-three-agent-patterns-every-engineer-needs-in-2026-355p
Three patterns with a Python skeleton, a named failure mode for each, and how the spans look under OpenTelemetry GenAI semantic conventions.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 21 resources in all, in the companion Deep Dive
Resources guide (Day 1, Act 2).

Day 1 · Session 2 · Tool Use and Agent Design Patterns
ACT 3
Planning, Reflecting, Scaling
Planner-Executor · Reflection · patterns pushed to their limit

ACT 3 · QUESTION 1
Should one call plan the work and a different call execute
it?

ACT 3 · QUESTION 1 — THE RATIONALE
What is the Planner - Executor Pattern?
Source: 7 Must-Know Agentic AI Design Patterns

ACT 3 · QUESTION 1 — THE RATIONALE
First Plan → Then Execute
Plan, then execute A real trade-off Plans are structured data
A dedicated step decomposes the task into More structure and cost than ReAct's Everything already covered on structured
sub-goals; a separate call or loop works improvisation —worth it for tasks with real, outputs and validation applies directly to the
through each one nameable sub-goals plan itself
Source: Anthropic engineering write-up on multi-agent research system design

ACT 3 · QUESTION 1 — SEE IT WORKING
The Plan, as Actual Data
Task: "Research competitor pricing for our new plan tier.“
Planner's output
{"plan": [
{"step": 1, "action": "search_competitors", "args": {"category": "AI bootcamps"}},
{"step": 2, "action": "extract_prices", "args": {"source": "step_1_results"}},
{"step": 3, "action": "summarize", "args": {"format": "table"}}
]}
Executor: runs step 1, feeds its output into step 2's args, then step 3.
This is structured output again — the plan is just another schema your code validates before acting on it.

ACT 3 · QUESTION 1 — THE ANSWER
Separate the Thinking From the Doing
Planner breaks it into steps Executor runs each step More structure, more cost
One call, or a distinct planning phase A separate call or loop per step Worth it for tasks with real, nameable sub-
goals

ACT 3 · QUESTION 1 — REMEMBER IT THIS WAY
“
A senior partner plans the case strategy; associates execute each piece — versus
everyone improvising alone.
Neither ReAct nor Planner-Executor is strictly better — it's a fit-to-task decision.

ACT 3 · QUESTION 2
Can the model catch its own mistakes before you do?

ACT 3 · QUESTION 2 — THE RATIONALE
What is the Reflection Pattern?
Source: 7 Must-Know Agentic AI Design Patterns

ACT 3 · QUESTION 2 — THE RATIONALE
Reflect Before Answering
A second pass, on meaning Documented in research Same discipline, same limits
This morning's loop checked shape (valid Self-Refine (Madaan et al., 2023) and Cap the cycles —and remember a model
JSON); reflection checks whether the answer Reflexion (Shinn et al., 2023) both show critiquing its own work shares its own blind
actually satisfies the goal iterative self-critique improving quality spots
Source: Madaan et al., 2023, ‘Self-Refine: Iterative Refinement with Self-Feedback’
Source: Shinn et al., 2023, ‘Reflexion: Language Agents with Verbal Reinforcement Learning’

ACT 3 · QUESTION 2 — SEE IT WORKING
Catching It Before You Do
Task: "What's 20% of $75?“
Draft answer
"20% of $75 is $16."
Reflection pass
"Check: 75 x 0.20 = 15, not 16. Correcting: $15."
Corrected answer
"20% of $75 is $15."
Same self-check as this morning's repair loop, now applied to reasoning instead of JSON shape — and it just as easily finds nothing
wrong, which is fine too.

ACT 3 · QUESTION 2 — THE ANSWER
Reflection: The Same Loop, One Layer Up
Draft, then critique Loop back if it fails Checks reasoning, not shape
A second pass checks the answer against the  Capped, exactly like this morning's repair  This morning: valid JSON? Now: actually
| original goal | loop | right? |
| ------------- | ---- | ------ |

ACT 3 · QUESTION 2 — REMEMBER IT THIS WAY
“
Your analyst, rereading their own memo against the original brief — not spell-
checking it, actually checking whether it answers the question.
Generate, check, fix — the same skeleton from this morning, now applied to reasoning.

★ WHAT'S NEW · 2026
ACT 3 · QUESTION 3
What happens when these patterns are pushed to their
absolute limit?

ACT 3 · QUESTION 3 — THE RATIONALE
What is Multi-Agent Orchestration?
Source: 7 Must-Know Agentic AI Design Patterns

ACT 3 · QUESTION 3 — THE RATIONALE
What is Multi-Agent Orchestration?
Planner-Executor, at scale Coordination is the hard part Cost is real, not free
One orchestrator decomposes a task and With hundreds of concurrent agents, the Anthropic's own multi-agent research system
dispatches many sub-agents, each running its bottleneck shifts from reasoning quality to shows meaningfully better coverage at
own full ReAct loop conflicting writes and race conditions meaningfully higher token cost
Source: Anthropic engineering blog, ‘How we built our multi-agent research system’

ACT 3 · QUESTION 3 — SEE IT WORKING
What Goes Wrong Without Coordination (Small Scale First)
Sub-agent 7
writes its result to shared_notes.md
Sub-agent 12
writes to shared_notes.md at the same moment — silently overwrites #7's work
Sub-agent 19
calls search_competitors("AI bootcamps") — the same call sub-agent 3 already made, 4 minutes ago
At 5 sub-agents, you can spot this by reading the log. At 300, this is the entire failure mode — the exact problem idempotency warned
about this morning, now at 300x scale.

ACT 3 · QUESTION 3 — THE ANSWER ★ WHAT'S NEW · 2026
One Planner, 300 Executors, All at Once
Kimi K3 / K2.6 Agent Swarm Planner-Executor at scale Idempotency matters more, not less
Spawns up to 300 parallel sub-agents for one One parent, hundreds of concurrent ReAct 300 parallel writes need the same safety as 1
task loops

ACT 3 · QUESTION 3 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
300 analysts, all handed the same case file at once — with no partner
coordinating who touches what.
The 5-tool lab you're about to build is the exact same primitive, at a scale you can debug by hand.

Day 1 · Session 2
QUICK CHECK — NO PEEKING
Before we move past Planning, Reflecting, Scaling:
What's the trade-off Planner-Executor makes against ReAct?
1
How many sub-agents can Kimi's Agent Swarm spawn?
2

DAY 1 · SESSION 2
ACT 3 · DEEP DIVE
Planning, Reflecting, Scaling
Planner-executor separation · reflection · where each pattern breaks
START HERE — 3 THINGS
1 Wang et al., Plan-and-Solve Prompting
arxiv.org/abs/2305.04091
The formalisation behind the planner-executor split.
2 Yao et al., Tree of Thoughts
arxiv.org/abs/2305.10601
Deliberate search over reasoning paths rather than a single chain.
3 Shinn et al., Reflexion
arxiv.org/abs/2303.11366
The reflection pattern in its original form.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 19 resources in all, in the companion Deep Dive
Resources guide (Day 1, Act 3).

SESSION FINALE
Source: Choosing the Right Agentic Design Pattern -A Decision Tree Approach

Day 1 · Session 2
Same three ideas — now you’ve built them
|     | 1   |     | 2   |     | 3   |
| --- | --- | --- | --- | --- | --- |
You gave the model hands — real  You built a harness around it:  You gave it a reasoning loop —
tools, with a schema, and an  retries, a circuit breaker, and logging  ReAct, extended with planning or
idempotency check before anything  — the same shape as Claude Code,  reflection — the same primitive
| runs in parallel. |     | just smaller. |     | that scales to 300 agents. |     |
| ----------------- | --- | ------------- | --- | -------------------------- | --- |
✓ Milestone 2 · Tool-enabled single agent