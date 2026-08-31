# Knowledge-base for revision / interview prep / teaching others

## Context
`lab-summaries/` maps 1:1 to notebooks by day/session — fine for Claude's teaching reference, useless for topic-first revision. `/knowledge-base/` exists to serve **a newcomer who knows basic Python but nothing about this stack**, read top-to-bottom without jumping around, while also working as a fast-lookup reference and interview-prep tool:

1. **Guided path** — numbered stages, prerequisites per page (Diátaxis "tutorial" mode).
2. **Reference graph** — `[[wikilinks]]` + a Tools & Libraries index (Diátaxis "reference" mode). No separate flat "category catalog" — the MkDocs sidebar / Obsidian file explorer already give that, in sync, for free (see "`index.md` — two sections" below).
3. **AI/LLM primer first** (stage 00) — tokens, generation, context windows, prompting — before any tooling, for a reader who's never touched an LLM API.
4. **Python split from AI-agent patterns** — `01-python-refresher` (everyday Python) stays separate from `02-python-for-ai-agents` (type hints, Pydantic, decorators, async), because the stack leans on the latter and a "basic Python" reader hasn't necessarily met them yet.
5. **Vendor neutrality** — every tool page lists real alternatives, web-researched, not just "what the course used."
6. **Market-relevant, not classroom-scoped** — code prefers the labs where clean, falls back to official docs when clearer; gotchas pull technical substance from the labs (never TA/course-logistics) plus web-researched production practice.

Fixed constraints from earlier scoping: no day/session naming anywhere in filenames or narrative prose (citing a real filename in a Sources section is fine — see `SKILL.md`'s `verify`); split by module, not high-level topic; real blank-line paragraph breaks; MkDocs Material for local rendering; no GitHub Pages this round.

**Naming convention**: files are named by pattern/concept, never by a lab's example project — e.g. the "travel assistant"/"research agent" labs feed `tool-calling-fundamentals.md`, `react-pattern.md`, `reflection-pattern.md`, never `travel-assistant.md`. Applies across all stages.

**Settled, not open for re-litigation** (each was deliberate against an earlier suggestion to change it): `01-python-refresher/` stays split into 3 files, not merged to 1; `05-memory` stays ordered before `06-rag`; the overlapping pattern pages in 07/08 (`agentic-loop-fundamentals` / `agent-topologies` / `graph-engineering-mindset` / `langgraph-agentic-patterns` / `supervisor-worker-teams`) stay separate, not merged.

### Course slide material (`presentations/day1.md` … `day4.md`)
One fully-scripted teaching deck per day (both sessions merged, not per-session files) — rationale, worked examples, analogies, and a dated reading list per act. For several topics these decks are the **only source in this repo** — the labs don't cover them at all: MCP/A2A/AG-UI/AP2 protocol layer, dynamic agent topology + fan-out caps, chaos engineering/seeded fault injection, prompt-cache-hit-rate as a reliability signal, context-rot-as-reliability, silent-failure detection, component-level eval, LLM-judge auditing, Reflexion-as-production-pattern, the fine-tune-vs-RAG 2026 decision framework, and two named incident postmortems. Lab/notebook still wins on code-level/API specifics where both exist; the decks are co-primary (not fallback) for conceptual framing and lab-silent topics. Sourcing rule for their 2026-dated/near-future claims: see Web-research rules below (same rule, stated once).

**Day → stage mapping** (for `generate` batch assignments — the deck is a real input to gather for every stage listed, not optional):
- `day1.md` → `00-ai-and-llm-basics` (tokens/context/prompting/model-selection) + `03-foundations` (`structured-output-repair-loops.md`) + `04-tool-calling-single-agents` (all 5 files)
- `day2.md` → `05-memory` (all 3 files) + `06-rag` (all 10 files)
- `day3.md` → `07-orchestration` (`graph-engineering-mindset`, `langgraph-checkpointing-hitl`, `idempotency-and-side-effects`, `agent-topologies`, `langchain-vs-langgraph`) + `08-multi-agent-systems` (all 4 files)
- `day4.md` → `09-production-readiness` (all 12 files) + `fine-tuning-vs-rag.md` (00 — Act 3's source, filed by topic under stage 00 instead)
- `01-python-refresher` / `02-python-for-ai-agents` have no matching day file (expected, decks don't teach Python fundamentals) — labs/web-research only.

**Placement decisions already applied** (deck content that didn't map 1:1 to an existing file — kept here since these choices aren't visible from the manifest alone): `fine-tuning-vs-rag.md` got its own stage-00 page rather than folding into `model-selection-cost-latency-tradeoffs.md` (recurring interview topic in its own right) — cross-linked both ways, not duplicated. Reliability-signal material (cache-hit-rate, context-rot, cost-anomaly triage, canary queries, fault injection) folded into `langfuse-tracing.md` / `retry-fallback-patterns.md` / `circuit-breaker-pattern.md`'s gotcha sections rather than a standalone page. The two named incident postmortems are cited as gotcha evidence across `idempotency-and-side-effects.md`, `auth-and-multi-tenancy.md`, `guardrails-injection-detection.md`, `deployment-packaging.md`, each tagged "per course material."

## File manifest

The authoritative, always-current file list is `mkdocs.yml`'s `nav:` section — don't re-list it here, it drifts. As of 2026-08-24: 77 concept files (stages 00-09, each with one `_interview.md`) + 6 interview-prep files (stage 10) + `index.md` + `capstone-milestone-map.md` + `changelog.md` = 85 files, the full legal set of `[[wikilink]]` targets.

Two things about the tree that aren't obvious from `mkdocs.yml` alone:
- `07-orchestration/langchain/` and `07-orchestration/langgraph/` are the only subfolders — every other stage is flat.
- Ownership on the acknowledged-overlap pages (each written once, not duplicated): `langgraph-agentic-patterns.md` gets the full supervisor-worker mechanics; `supervisor-worker-teams.md` covers only write-scopes/dual critics and links back to it.

## Stage 10 — Interview Preparation (added 2026-08-21)

A deliberate exception to the "concept-first, no day/session naming" stage pattern above: this stage's whole purpose is interview readiness, so it's organized by *interview-round shape* (how a real interview for this kind of role actually unfolds), not by the 00-09 topic order. Two additive changes that rode along with adding this stage:

1. Per-page "Interview fire round" sections (2-3 Q&A, stages 00-09) stay exactly as they were.
2. Each stage's `_interview.md` got a `### Harder / real-interview-style` sub-section appended — new, web-researched, harder questions beyond the page-sourced Q&A already assembled there.

Stage 10 itself has no `_interview.md` (it *is* the interview material) and is exempt from the standard 12-section template below — no Prerequisites/Alternatives scaffolding. Each round file carries as many well-organized, sub-sectioned questions as the topic supports, each with a full worked-answer sketch, so a candidate never needs to leave this KB to prep. `[[wikilink]]` back into the relevant 00-09 concept pages liberally; Sources can be a brief one-line note ("grounded in `lab-summaries/`, `presentations/day1-4.md`, and general LLM/agent-engineering interview practice as of 2026-08") rather than the full per-claim citation rigor of the concept-page template.

## Stage 00 expansion — inference internals & neural-net/transformer fundamentals (added 2026-08-24)

A gap-check against stage 00 found prefill, decode, KV cache, PagedAttention, and neural-network/transformer fundamentals entirely missing (self-attention had only a one-line O(n²) aside in `context-rot-and-long-context-management.md`). Four new pages were added to `00-ai-and-llm-basics/`, inserted between `tokens-and-tokenization.md` and `how-llms-generate-text.md`/`context-windows-and-limits.md` in this order: `neural-network-basics.md`, `transformer-architecture-and-attention.md`, `prefill-decode-and-kv-cache.md`, `paged-attention-and-efficient-serving.md`.

Two deliberate departures from the rest of the KB, both scoped to just these 4 pages:

- **First externally-sourced-only content.** None of these topics are covered in `labs/` or `presentations/dayN.md` — confirmed by an Explore pass and consistent with the Day → stage mapping above (nothing in day1-4 decks maps to inference-serving internals or neural-net basics). Every other page in this KB is grounded primarily in a lab/deck with web sources as backup; these 4 pages are grounded *only* in external references (Vaswani et al., Jay Alammar's Illustrated Transformer, Kwon et al.'s PagedAttention/vLLM paper, 3Blue1Brown). Their "Sample code" section says so explicitly, the same way `context-rot-and-long-context-management.md` already flags "no lab cell demonstrates this."
- **First Mermaid diagrams in the KB.** `mkdocs.yml` gained a `mermaid` custom fence under the existing `pymdownx.superfences` config (mkdocs-material renders it natively, no new plugin dependency). Each of the 4 new pages carries one diagram. This is now the KB's image/diagram convention — prefer a Mermaid fence over adding a binary-asset folder for any future page needing a visual.

`context-windows-and-limits.md` also gained a new "What actually fits in a 1M-token window" section (concrete, provider-neutral scale examples — word/page/codebase equivalents — explicitly not Claude Code product-feature framing), and its existing self-attention aside in `context-rot-and-long-context-management.md` now wikilinks into the new `transformer-architecture-and-attention.md` page instead of standing alone.

## `changelog.md` — ongoing, dated build log (added 2026-08-24)

A new top-level nav entry (`changelog.md`, placed after stage 10, outside the numbered stage sequence since it's meta/site-level, not a learning topic) tracks future changes to the KB going forward: one dated entry per change, listing what changed, which files, and the git commit hash once committed. Starts fresh from 2026-08-24 (this stage-00 expansion is its first entry) — no backfill of the KB's pre-changelog git history. Exempt from the standard 12-section template, same as stage 10.

## Per-file template (revised)

Optional frontmatter: `stage`, `tools`, `tags`, `last_verified` (date), `verified_against` (package version(s) checked against) — makes the Obsidian graph/Tools index groupable and staleness greppable later.

1. **H1 + one-line "what & why"**
2. **Prerequisites** — 0-4 `[[wikilinks]]` to pages a newcomer should read first (some pages, e.g. `hybrid-retrieval-rrf.md`, legitimately need more than 2)
3. **In plain English** — written for someone who knows basic Python, nothing else here; no unexplained jargon
4. **Core mechanics** — key APIs/classes/params as a table *when there's an actual API surface*; concept/mindset pages (00, 01, `graph-engineering-mindset`, `eval-driven-development-mindset`, etc.) get a plain mechanism walkthrough instead of a forced table
5. **Sample code** — prefer a lab-sourced snippet when clean; pull/adapt from official docs when clearer, and say which source it came from; version-pin inline (e.g. "LangGraph 1.2.x") against this repo's `pyproject.toml`/`uv.lock`
6. **Alternatives** *(tool/framework pages, plus `llm-judges-eval.md`)* — table of real competitors, capped at 4-5 rows, every row backed by a URL fetched that session (listed in Sources), differentiators limited to slow-changing structural facts (not pricing/benchmarks/superlatives), always including the "boring" alternative (Qdrant → pgvector, Langfuse → OpenTelemetry/structured logs, Supermemory → a Postgres table + your own summarizer, LangGraph → a `while` loop and a dict)
7. **How this shows up in the capstone** — one line linking the concept to its ShopSense/Kartway milestone, `[[capstone-milestone-map]]`
8. **Interview fire round** — 2-3 rapid Q&A local to this page (consolidated `_interview.md` per stage is the actual revision artifact; drop this section entirely on 01-python-refresher pages)
9. **Production gotchas & best practices** — technical lessons from lab-summary "Gotchas"/`labs/production-notes.md` (TA/course-logistics stripped, technical substance only) plus web-researched current production practice for that tool/pattern
10. **Course vs. production** — where the lab's approach and current production practice diverge (e.g. lab uses in-memory mocks, production needs persistence) — what makes gotchas market-scoped rather than classroom-scoped
11. **Related** — plain prose bullets with `[[wikilinks]]`, e.g. `- **Builds on** — [[langgraph-state]]` (not Dataview `field::` syntax — renders as literal text on MkDocs)
12. **Sources** — **Lab sources** (`lab-summaries/*.md`, notebook path) and **Web sources** (title + URL + accessed date, tiered per Web-research rules); every claim in sections 4-6 and 9-10 that could be wrong (pricing, licensing, dimension counts, rate limits, "X supports Y") gets an inline citation where it's made, not just a bare link at the bottom.

One consolidated `_interview.md` per stage folder (00-09), sequencing that stage's page-level questions into a single revision pass.

## `index.md` — two sections

1. **Start Here** — numbered stage path (00 → 09, plus a pointer to stage 10), 1-2 sentences per stage, links in reading order.
2. **Tools & Libraries quick index** — alphabetical, cuts across stages.

A third section (a flat one-line-per-page "Reference catalog" mirroring the folder tree) was tried and deliberately dropped — pure duplication of what the MkDocs sidebar nav and Obsidian's file explorer already give for free, and unlike them it doesn't stay in sync when pages are added/renamed/moved. Don't re-add it.

## Wikilinks: dual compatibility (Obsidian graph + MkDocs site)
- `[[filename]]` syntax (Obsidian-native — free graph view, zero tooling).
- `mkdocs-roamlinks-plugin` in `mkdocs.yml` resolves the same links on the rendered site.
- Filenames stay globally unique across the whole tree — wikilinks resolve by basename, not path.
- Stage numbers live only in folder names, never in filenames or as relative-path links — keeps links stable if a stage gets renumbered later.

## Web-research rules (for every agent generating content)

- **Always the latest package version, never stale examples** — cross-check against this repo's `pyproject.toml`/`uv.lock` pins; discard blog posts/tutorials that predate the pinned major version. Matters most for **LangGraph** (pre-1.0 vs 1.x, e.g. `interrupt()`/`Command(resume=)` replaced `interrupt_before`), **Langfuse** (repo uses SDK v4 — `get_client()`, `start_as_current_observation` — most web content is v2/v3), and **FastMCP** (repo pins standalone `fastmcp` v3.x at `gofastmcp.com`, not the MCP SDK's bundled v1 variant).
- **Source tiering**: (1) official docs + the tool's own GitHub repo (2) primary specs/papers (MCP spec, Anthropic's "Building effective agents", BM25/RRF/ReAct/Reflexion/lost-in-the-middle) (3) independent benchmarks, dated. Avoid vendor "X vs Y" pages (treat as marketing) and SEO listicles.
- **Alternatives tables**: every row needs a URL fetched that session, cap at 4-5 rows, no superlatives/rankings, always include the "boring" alternative.
- **Lab vs. web disagreement**: lab is truth for "what this course did," web is truth for "what production does now" — show both (template section 10). If plan's own inline description conflicts with a lab summary, the lab/notebook wins and the discrepancy gets a note.
- If nothing current/trustworthy turns up, say so on the page rather than filling the gap from memory.
- **2026-dated claims from `presentations/dayN.md`** that can't be independently web-verified (near-future model names, the two named incident postmortems) get cited as "per course material (`presentations/dayN.md`)," not presented as independently confirmed.

## Build steps

Full operational detail for each step lives in `.claude/skills/wiki/SKILL.md` (its `scaffold`/`generate`/`crosslink`/`verify`/`pointers` subcommands map to steps 1/4/5/7/6 below) — this is just the order and intent:

1. Scaffold the tree — `index.md`, `capstone-milestone-map.md`, headed-but-empty concept files, empty `_interview.md` stubs.
2. `mkdocs.yml` + wikilink plugin, smoke-tested on a throwaway page before any real content is generated.
3. Hand-write 2-3 exemplar pages first (style reference for every generation agent).
4. Generate remaining content in batches.
5. Cross-link pass — backfill `[[wikilinks]]`/Prerequisites across batches, assemble each `_interview.md`.
6. Add the two `pointers` lines (`lab-summaries/INDEX.md`, `CLAUDE.md`) to `knowledge-base/index.md`.
7. Verify (see `SKILL.md`'s `verify` checklist).

## Out of scope

No GitHub repo/remote, no GitHub Pages/Actions — local rendering only. No changes to `lab-summaries/*.md` beyond the one `pointers` line. No `log.md` ingest ledger — this KB is generated from fixed lab content, not continuously fed new sources. (Same list as `SKILL.md`'s guardrails — stated once here, referenced there.)

## Status (last touch: 2026-08-24)

All 7 Build steps complete across all 85 files (73 original + the 6-file `10-interview-preparation/` stage + the 4-file stage-00 inference-internals expansion + `changelog.md`, both added post-generation). `uv run mkdocs build --strict` is clean; 0 broken wikilinks; 0 backtick-wrapped wikilinks or backtick-wrapped in-KB filenames (see `SKILL.md`'s `verify` section for both failure modes); no banned day/session strings outside legitimate Sources citations.

Notable fixes along the way:
- `capstone-milestone-map.md`'s M1-M8 numbering was corrected to match each `lab-summaries/*.md`'s own "Capstone tie-in: Milestone N" line (the authoritative source, not `CLAUDE.md`'s build-order description) — every page's own "How this shows up in the capstone" section was reconciled against the corrected map in the same pass.
- Every page's capstone section (and 2 Sources-section entries, ~67 files total) cited `` `capstone-milestone-map.md` `` backtick-wrapped instead of `[[capstone-milestone-map]]`, so it rendered as dead inline code — fixed tree-wide; confirmed no other in-KB filename has the same bare-backtick pattern.
- `index.md`'s "Reference catalog by category" section was dropped (see the two-section note above) as pure duplication of the sidebar nav / file explorer.
- The standalone `knowledge-base-plan-decisions` memory file was removed — this file + `SKILL.md` are now the only two homes for build rationale.

Open, deliberately unfixed: `CLAUDE.md`'s Stack section says `groq/llama-3.1-8b-instant`, but the Day1·Session2 tool-calling lab's `LAB_MODEL` is actually `gemini/gemini-flash-lite-latest` (noted as a real lab detail on `model-selection-cost-latency-tradeoffs.md`). Editing `CLAUDE.md`'s Stack section is outside this skill's scope — an editorial call for the user to make, not this skill to touch.
