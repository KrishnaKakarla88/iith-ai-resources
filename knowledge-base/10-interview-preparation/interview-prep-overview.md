# Interview prep overview

This stage is different from every stage before it. Stages 00-09 taught the stack, concept by concept, so you could hold the whole territory in your head. This stage assumes you already did that reading and asks a harder question: can you perform under interview conditions — time pressure, a stranger pushing back on your answer, no notebook open next to you?

Nothing here repeats a concept page's "Interview fire round" section. Those are 2-3 quick per-page Q&A meant for a fast per-topic refresh. This stage is denser, harder, and organized by *interview-round shape* instead of by topic — because that's how the interview itself will actually come at you.

## How a real AI/LLM agent-engineer interview is structured

Research into 2026 hiring loops for "AI engineer," "LLM engineer," and "applied AI / agent engineer" roles at companies actually shipping agentic products converges on a fairly consistent shape, even though titles and company sizes vary:

| Round | What it tests | Typical weight | Roughly maps to |
|---|---|---|---|
| **Recruiter / phone screen** | Baseline fit, communication, whether your resume claims hold up under two follow-up questions | Pass/fail gate, not scored | — |
| **Fundamentals / rapid-fire** | Do you actually know what a token is, why RAG beats fine-tuning for facts that change, what ReAct is — the vocabulary you'll be assumed to already have in every later round | Filtering round; weak answers here rarely get a second chance | [[round-1-fundamentals-rapid-fire]] |
| **System design** | Can you architect a RAG pipeline, a multi-agent system, a memory layer — from a vague one-line prompt, out loud, defending tradeoffs as an interviewer pushes | Often the single highest-weighted technical round — one search found 2026 GenAI loops spending roughly 75% of technical rounds on RAG architecture, evals, and multi-agent design | [[round-2-system-design]] |
| **Production / reliability** | Observability, evals, guardrails, incident response — "what happens when this breaks in production," not just "does it work in the demo" | Growing in weight as agentic systems ship to real users; increasingly its own dedicated round rather than a subsection of system design | [[round-3-production-reliability]] |
| **Coding / live debugging** | Read and fix real code — a broken LangGraph node, a retry loop with no backoff, a tool schema that silently drops a field | Standard technical-round weight; less about DSA/LeetCode-style algorithms than about reading agent/LLM code specifically | [[round-4-coding-and-debugging]] |
| **Behavioral / tradeoffs** | How you reason about a decision out loud (RAG vs. fine-tune, framework choice, "tell me about a production issue"), and standard behavioral fit | Reported at nearly half the overall evaluation weight in some 2026 ML/LLM loops — behavioral is not a formality | [[round-5-behavioral-and-tradeoffs]] |

The exact number and order of rounds varies by company and level — a startup might compress fundamentals and coding into one round; a larger org might run system design twice (once narrow, once open-ended). What's consistent is that **system design and behavioral/tradeoff reasoning now carry as much or more weight than raw coding** for this kind of role, which is a real shift from a classic backend-engineer loop. An interviewer who spends 45 minutes on "design a policy-RAG support agent" is testing the same judgment a classic system-design round tests (scale, failure modes, tradeoffs) but through this stack's specific vocabulary: chunking, hybrid retrieval, agent topologies, checkpointing, guardrails.

## What "harder than the per-page fire rounds" means here

The per-page "Interview fire round" sections in stages 00-09 are definitional — good for confirming you remember what a term means. The questions in this stage are written the way a real interviewer actually asks them: comparative ("what's the difference between X and Y, and when would you pick each"), adversarial ("why would Z fail in production"), and open-ended ("design a system that..." with no single correct answer, only a defensible one). Several are drawn from, or modeled closely on, real 2026 interview questions and prep guidance gathered via web research for this stage — see each round file's sourcing note.

## How to use the five round files

- **Work them in order once, then drill weak spots.** Round 1 assumes stages 00-04; round 2 assumes you can already answer round 1 cold — a shaky system-design answer is very often a fundamentals gap wearing a design-round costume.
- **Round 2 (system design) is the one to rehearse out loud, not just read.** Cover the strong-answer sketch, talk through your own answer to the prompt for 3-5 minutes as if an interviewer were listening, then compare. Reading a strong answer silently and rehearsing one out loud are different skills, and the interview only tests the second one.
- **Use the wikilinks as your rescue rope, not your primary study path.** Every round file links back into the relevant 00-09 concept page for the full mechanics — if a question exposes a real gap, go read that page in full before moving on, then come back and re-answer the question from memory.
- **Round 3-5 lean on rounds 1-2 rather than repeating them.** Production/reliability assumes you already have the system-design shape in hand and asks "now it's live — what breaks and how do you know." Behavioral assumes you can already argue a tradeoff technically and asks you to also narrate *how* you'd make that call under real constraints (time, cost, a stakeholder who disagrees).
- **Ground every answer in this repo's actual stack where you can.** ShopSense/Kartway (Triage → Policy RAG → Order-Actions → Escalation Reviewer via LangGraph, Groq + Gemini via LiteLLM, Qdrant, Supermemory, Langfuse, FastMCP, FastAPI) is a real, defensible worked example — see [[capstone-milestone-map]] and [[architecture-of-an-agentic-system]]. An interviewer who hears "here's how I actually built this" is more convinced than one who hears only textbook definitions.

A candidate who works through all five files honestly — answering before reading the sketch, not after — should be able to walk into any round of this kind of interview without needing to open anything else.

---

*Grounded in `lab-summaries/`, `presentations/day1-4.md`, this knowledge base's own stage 00-09 pages, and general LLM/agent-engineering interview practice and web-researched 2026 interview questions as of 2026-08-21.*
