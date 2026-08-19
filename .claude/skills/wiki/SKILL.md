---
name: wiki
description: Build, extend, and verify the /knowledge-base/ revision KB (topic-first MkDocs reference derived from lab-summaries/). Use when the user says "/wiki" or asks to scaffold, generate, cross-link, or verify knowledge-base content.
---

# /wiki — knowledge-base build operator

Executes the Build steps of the approved KB plan. Source of truth for *what* to build:
`C:\Users\ina974nagkaka\.claude\plans\from-lab-summaries-i-am-greedy-turtle.md`

Source of truth for *why* structural calls were made (don't re-litigate these — apply them):
memory file `knowledge-base-plan-decisions` (topic-first naming, stage order, wikilink plugin choice,
`source-material/` as optional supplementary input, web-research latest-version rule, etc).

Always read both before doing anything below. If either is missing, stop and tell the user —
do not improvise a replacement plan.

## Args

`/wiki <subcommand> [target]`

### `scaffold`
One-time. Plan's Build step 1: create the full `knowledge-base/` tree — all 72 concept files
(headed but empty per the template's H1 + "what & why" line), `index.md`,
`capstone-milestone-map.md`, and 10 empty `<stage>/_interview.md` stubs. Skip any file that
already exists (check before writing — this repo already has a validation slice: `mkdocs.yml`,
`tokens-and-tokenization.md`, `chunking.md`, `_smoketest/`). Do not touch files outside
`knowledge-base/`.

### `generate <stage-or-file-list>`
Plan's Build step 4, run per batch. Before spawning anything:
1. Confirm the target files' headings already exist (run `scaffold` first if not).
2. Check `source-material/` for a same-day/session file matching the target stage — optional,
   supplementary only, labs/notebooks still win on conflict.
3. Gather that batch's `lab-summaries/*.md` + the matching notebook path(s) in `labs/`.

Spawn one `general-purpose` Agent per batch (roughly even file count, not strictly
one-agent-per-folder — split stage 07, merge thin stages like 01+02 or 05). Give each agent:
- the relevant `lab-summaries/*.md` + notebook path(s), and the `source-material/` file if present
- the full per-file template (plan's "Per-file template (revised)" section)
- the 3 exemplar pages as style reference: `qdrant.md`, `chunking.md`, `tokens-and-tokenization.md`
- the full 72-file manifest as the **only** legal `[[wikilink]]` targets
- the Web-research rules (latest package version only, source tiering, alternatives-table rules)
- explicit instruction: strip any TA/course-logistics references from lab-sourced gotchas
- the "reader knows basic Python, nothing about this stack" framing

Write stages 00-02 (the primers) **last** — only once downstream pages that assume their content
exist have been written, so primers can be scoped to what's actually assumed.

Respect the pre-assigned ownership on overlap pages: `langgraph-agentic-patterns.md` gets full
supervisor-worker mechanics; `supervisor-worker-teams.md` covers only write-scopes/dual critics
and links back — don't let a generation agent duplicate both.

### `crosslink`
Plan's Build step 5. Backfill `[[wikilinks]]` + Prerequisites between files written in different
batches. Assemble each stage's `_interview.md` from its pages' "Interview fire round" sections.

### `verify`
Plan's Build step 7:
- `uv run mkdocs serve` (or `build --strict`) — nav follows stage order, wikilinks resolve, no
  mangled paragraph breaks (check raw markdown, not just rendered HTML)
- mechanically confirm every `[[wikilink]]` resolves to a real file in the 72-file manifest
- spot-check external URLs aren't dead
- open in Obsidian to confirm the graph clusters sensibly (ask the user to eyeball this — not
  automatable)
- read `index.md` → `capstone-milestone-map.md` → stage 00 → 01 → 02 cold, as a newcomer would
- spot-check 4-5 files against source notebooks, confirm no TA references leaked through
- confirm Alternatives tables cite sources actually fetched that session, not stale/hallucinated
- grep for banned strings: `Day 1`, `Session 2`, and any TA names found in `lab-summaries/`

### `pointers`
Plan's Build step 6, one-time, run only after `verify` passes: add one pointer line from
`lab-summaries/INDEX.md` to `knowledge-base/index.md`, and one from `CLAUDE.md`'s
"Reference before teaching" section to `knowledge-base/index.md`. No other changes to either file.

## Guardrails (apply to every subcommand)

- Never invent a `[[wikilink]]` target outside the 72-file manifest.
- Never add day/session naming to a concept filename — name the pattern, source the example
  (see memory: `knowledge-base-plan-decisions`).
- Lab/notebook content always wins over `source-material/` (slides) on conflict.
- Web research must target the latest package version against this repo's `pyproject.toml`/
  `uv.lock` pins — explicitly discard docs/blog content that predates the pinned major version
  (LangGraph pre-1.0 vs 1.x, Langfuse v2/v3 vs the repo's v4, FastMCP v1-bundled vs standalone v3.x).
- Out of scope for this skill: GitHub repo/remote, GitHub Pages/Actions, edits to
  `lab-summaries/*.md` beyond the one `pointers` line, any `log.md` ingest ledger.
- After any subcommand that changes a structural decision (not just fills in content), append a
  bullet to the `knowledge-base-plan-decisions` memory file and refresh its
  "Status as of last touch" line — that memory is the only place this reasoning survives a fresh
  session.
