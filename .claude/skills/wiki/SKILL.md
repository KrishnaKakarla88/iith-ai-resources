---
name: wiki
description: Build, extend, and verify the /knowledge-base/ revision KB (topic-first MkDocs reference derived from lab-summaries/). Use when the user says "/wiki" or asks to scaffold, generate, cross-link, or verify knowledge-base content.
---

# /wiki — knowledge-base build operator

Executes the Build steps of the approved KB plan. Source of truth for *what* to build:
`plan.md` at the repo root (`d:\Krishna\OpenSource\AI\IITH-AI\milestones\plan.md`) — edit that file for
any future plan changes, not the original `~/.claude/plans/...` Plan Mode file.

Always read `plan.md` before doing anything below — it carries the manifest, rationale, and
"settled, not open for re-litigation" decisions inline (see its Context section). If it's
missing, stop and tell the user — do not improvise a replacement plan.

## Args

`/wiki <subcommand> [target]`

### `scaffold`
Create new headed-but-empty files (H1 + "what & why" line) for whatever's in `plan.md`'s
manifest but not yet on disk — the original one-time run built all 73 concept files, `index.md`,
`capstone-milestone-map.md`, and 10 `<stage>/_interview.md` stubs; a later run added the
`10-interview-preparation/` stage the same way. Skip any file that already exists (check before
writing). Do not touch files outside `knowledge-base/`.

### `generate <stage-or-file-list>`
Plan's Build step 4, run per batch. Before spawning anything:
1. Confirm the target files' headings already exist (run `scaffold` first if not).
2. Check `presentations/dayN.md` for the file matching the target stage, per `plan.md`'s
   Day → stage mapping. Where a match exists it's a real input to gather, not optional — the
   decks are co-primary for conceptual framing and anything lab-silent; labs/notebooks still win
   on code-level/API specifics on conflict. `01`/`02` have no matching day file (expected).
3. Gather that batch's `lab-summaries/*.md` + the matching notebook path(s) in `labs/`.

Spawn one `general-purpose` Agent per batch (roughly even file count, not strictly
one-agent-per-folder — split stage 07, merge thin stages like 01+02). Give each agent:
- the relevant `lab-summaries/*.md` + notebook path(s), and the matching `presentations/dayN.md`
  when one exists for that stage
- the full per-file template (plan's "Per-file template (revised)" section)
- 2-3 already-written pages as style reference (e.g. `chunking.md`, `tokens-and-tokenization.md`,
  `qdrant.md` — pick ones already in the target stage's neighborhood when possible)
- the full manifest (`mkdocs.yml`'s `nav:` section) as the **only** legal `[[wikilink]]` targets
- the Web-research rules (latest package version only, source tiering, alternatives-table rules,
  and the rule on citing unverifiable 2026-dated deck claims as "per course material")
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
- mechanically confirm every `[[wikilink]]` resolves to a real file in the manifest (script it —
  walk `knowledge-base/`, regex `\[\[([^\]|#]+)`, diff targets against filenames)
- separately grep for `` `\[\[ `` — a wikilink wrapped in backticks renders as literal inline code,
  not a link, even though the target is valid; this is a distinct failure mode from a broken
  target and the mechanical link-resolution check above won't catch it
- same failure mode, no brackets: grep for any backtick-wrapped `` `<name>.md` `` where `<name>`
  matches a real file under `knowledge-base/` (e.g. `` `capstone-milestone-map.md` ``) — a plain
  in-KB filename cited in backticks instead of as `[[name]]` also renders as dead inline code, not
  a link, and a bracket-only grep won't catch it either (found tree-wide across ~66 files this way
  once already — see `plan.md` Status)
- spot-check external URLs aren't dead
- open in Obsidian to confirm the graph clusters sensibly (ask the user to eyeball this — not
  automatable)
- read `index.md` → `capstone-milestone-map.md` → stage 00 → 01 → 02 cold, as a newcomer would
- spot-check 4-5 files against source notebooks, confirm no TA references leaked through
- confirm Alternatives tables cite sources actually fetched that session, not stale/hallucinated
- grep for banned strings: `Day 1`, `Session 2`, and any TA names found in `lab-summaries/` — but
  citing a real filename (`presentations/day1.md`, `lab-summaries/Day1-Session1-Foundations.md`)
  inside a Sources section is fine and expected; only narrative prose using day/session numbering
  is banned
- if `capstone-milestone-map.md` itself changed this run, re-grep the whole tree for
  `Milestone \d` — every page's own "How this shows up in the capstone" section names a specific
  milestone number, and fixing only the map without checking every page that cites a number
  against it leaves the two silently contradicting each other

### `pointers`
Plan's Build step 6, one-time, run only after `verify` passes: add one pointer line from
`lab-summaries/INDEX.md` to `knowledge-base/index.md`, and one from `CLAUDE.md`'s
"Reference before teaching" section to `knowledge-base/index.md`. No other changes to either file.

## Guardrails (apply to every subcommand)

- Never invent a `[[wikilink]]` target outside the manifest — cross-check `mkdocs.yml`'s `nav:`
  section as the authoritative, always-current list (it grows over time; don't hardcode a count).
- Never add day/session naming to a concept filename or to narrative prose — name the pattern,
  source the example. Citing a real filename inside a Sources section is fine (see `verify` above).
- Web-research rules (latest-version-only, source tiering, lab-vs-deck precedence) and the
  out-of-scope list (no GitHub remote/Pages, no `lab-summaries/*.md` edits beyond `pointers`, no
  `log.md` ledger) live once in `plan.md` — read them there, don't restate them here.
- `mkdocs-roamlinks-plugin` is the intentional choice despite its cosmetic deprecation warning at
  build time (unmaintained since 2023, but wikilinks resolve fine); its own fallback
  `mkdocs-ezlinks-plugin` is more stale, not less. Don't swap it over a warning — only if MkDocs
  actually breaks resolving `[[wikilinks]]`.
- After any subcommand that changes a structural decision (not just fills in content), add or
  update a note directly in `plan.md`'s Status section — that's the only place this reasoning
  needs to live; don't start a separate memory file for it.
