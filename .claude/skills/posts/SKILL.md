---
name: posts
description: Draft LinkedIn + Instagram posts teaching Applied AI Engineering concepts — RAG, LangGraph, MCP, LLM tool-calling, LangFuse, LangChain, chunking, reranking, etc. — grounded in Krishna's course labs, capstone project, and production AI use cases. Teaching-first, caveman tone, no hype. Generates a matching carousel or single-image visual via a coded Pillow template (no AI-generated art). Use whenever Krishna wants to post about his AI engineering learning/build work.
---

# Applied AI Engineering Posts

Output LinkedIn + Instagram copy, plus a matching visual (carousel or single image), every time.

## Writing Style

**Balanced caveman — short lines, not cryptic ones.** No filler, no hype words, but every line stands alone for a first-time reader: a term never appears without the phrase explaining what it does or why it matters. One line = one fact/step, dense (a real term, import, mechanism) but stripped of qualifiers ("the one-time process of") that add nothing. Blank line between lines. Match the source wiki's own vocabulary ("parametric knowledge," "autoregressive") rather than inventing simpler synonyms. Hook = the concept, a question, or a real tension — never "In this post I'll cover...". No client/company names (course name OK, public cert). Never ask the audience to pick what's next — Krishna sets the roadmap; closing questions invite discussion of the concept, not content planning.
✓ "An LLM's knowledge lives in its weights — billions of parameters fixed after training."
✗ "An LLM's knowledge lives entirely in its weights — billions of numeric parameters fixed once training ends." (qualifiers add nothing; trim them) · ✗ "AI is transforming how we build apps!" (hype, not teaching)

**Ground abstract concepts with a real example.** An abstract mechanism (tokenization, an attention head, a decode step) reads as pure theory until tied to a concrete instance — a real word, number, or snippet. Pull it from the source wiki when it has one; invent a small, obviously-correct one when it doesn't (never a vague placeholder like "some word"). Check every concept slide before finalizing a carousel: a plugged-in instance, or just the mechanism stated in the abstract? Common miss.
✓ "A tokenizer splits words into pieces. **Example:** **\"tokenization\"** splits into **\"token\"** + **\"ization\"**."
✗ "A tokenizer splits words into subword pieces based on frequency." (correct, but nothing to picture)

**Bold the term being defined.** When a line defines/names something ("X is Y," "X: Y," a term-then-explanation pattern — including former wiki table rows like Query/Key/Value or Prefill/Decode) or labels a worked instance (`**Example:**`), wrap the term/label in `**double asterisks**` in `body_lines` — `slide()`/`draw_rich_line()` parse `**bold**` inline (`single_image_template.py`'s `items` already bolds each row's `name`, no markup needed there). Don't bold whole sentences or every noun, only what a reader should scan for.
✓ "**Query** is what a token looks for. **Key** is what it offers others."
✗ "Query is what a token looks for. Key is what it offers others." (nothing helps the eye separate terms from prose)

**Never write a literal double-asterisk in `body_lines` prose** (`**kwargs`, `Invoice(**data)`) — the parser treats any `**` as a bold toggle with no awareness it's Python syntax, so an unpaired one silently bolds everything after it to the end of that line, with no error and nothing visible in the source text. Refer to the bare name instead (`kwargs`, not `**kwargs`) and put the real double-star syntax only inside a `code=`/footer-code string, which is drawn raw and never parsed for bold.

## Content Approach

**Teaching-first, always:** teach the concept plainly first — imports, syntax, how it fits, what it's for. Real lab/capstone/production experience is an **optional bonus**, added after the teaching only when a real moment exists (a bug, a ratio, an issue). Never invent or force one.

**Pillars (rotate):**
1. **Concept teaching** (primary) — one concept, taught plainly, experience tacked on only if real.
2. **Production tradeoff** (occasional) — real capstone/production decision or bug. Problem → decision → result. Experience leads.
3. **Interview nugget** (occasional) — a real question actually faced + the real answer, in caveman form. Must trace to an actual `_interview.md` entry (fire-round or "Harder" section) — never invent a question. If the wiki's real answer is multi-sentence/scenario-based, default to a short carousel (one question, full answer, per slide) instead of a single-image; reserve single-image for answers that are genuinely one line in the source.

❌ Hype, unfinished thoughts, forced anchors, syllabus recaps with no teaching value.

## Platform & Hashtags

**LinkedIn:** ≤1200 chars, no emoji, ends on an engagement question, hashtags last line.
**Instagram:** 5-6 lines, 1-2 functional emoji max, hashtag block separate at end.

**Caption vs. visual — don't make the caption a transcript of the slides.** When there's a matching carousel, the caption's job is hook + the 2-3 highest-value points + the closing question, not a paragraph-per-slide restatement. The carousel carries the full granular teaching (one concept per slide, in depth); the caption should teach something real on its own while still giving a reason to swipe ("full breakdown in the carousel," or an unanswered thread) — not duplicate the carousel 1:1. A single-image post's caption and image naturally overlap more, since there's no multi-slide depth to point to.

LinkedIn (3-5): `#AppliedAI #RAG #LLM #AIEngineering` — swap in `#LangGraph` `#MCP` `#LangChain` `#PromptEngineering` `#VectorSearch` per topic. Never `#MachineLearning`.
Instagram (max 5 — Buffer enforces this): pick the 5 most topic-relevant tags from the LinkedIn pool plus `#GenAI` `#AI` `#Developer`, don't just append every tag from the LinkedIn line. Never generic tags (`#BuildInPublic` etc) or `#MachineLearning`.

**Series numbering:** only for pre-planned serials on consecutive days — `[Series] — Part X/Y` before hashtags.

## Schedule (IST) — 2-3 posts/day, all 7 days incl. Sat/Sun

Pace goal: 2-3 topics/day to clear the course backlog fast. 3 fixed slots/day (each = one topic on both platforms); use slots 1+3 for a 2-post day, add slot 2 for 3-post. Weekends use the same slots — real weekend engagement is lower, but the daily-cadence goal overrides; cut slot 2 first if a day needs trimming.

| Slot | Instagram | LinkedIn |
|---|---|---|
| 1 — morning | 9:00am | 10:00am |
| 2 — midday | 12:00pm | 1:00pm |
| 3 — evening | 6:00pm | 4:00pm |

Sourced from Buffer's 2026 engagement data: IG peaks Wed 12pm/6pm + Thu 9am, evenings strong all week; LinkedIn peaks shifted later (Wed/Fri 3-4pm > old 8-11am mornings).

**Buffer free-plan cap: 10 scheduled posts/channel** (`get_account` → `limits.scheduledPosts`). At 2-3 slots/day that's only ~3-5 days queueable ahead per channel — schedule in batches, don't try to fill further; see Buffer Delivery below.

## Visuals — Coded Template, No AI-Generated Art

Abstract AI art reads as slop and teaches nothing. Use the bundled Pillow templates instead — same fonts/colors/grid every time, which is what makes a coded template *not* look AI-generated.

**Default: carousel.** Multi-slide teaching content out-saves single images — saves are the strongest ranking signal for reference-style posts. Use **single image** only for compact lists (≤4-5 items) or quick tradeoff/interview posts.

**Brand kit (locked):** Navy `#1A2B4A` text/lines · Amber `#C27803` accent · code block `#182030` bg / `#E2E8F0` text · white background. Liberation Sans Bold (headline/kicker), Regular (body), Mono (code). 1080×1080px per slide.

**Layout:** amber top bar → series label + slide counter → divider → kicker (topic-specific, never generic) → bold headline → amber underline → body → optional code block or bold closing question → navy bottom bar.

**Slide count vs. item count:** one item per slide is not a rule — a single tool/term with only a line or two leaves a slide mostly blank. Group 2-3 related items onto one slide (sub-headlines or a labeled list in `body_lines`) instead of stretching thin content across more slides. One item per slide only when it genuinely needs its own code block, diagram, or fuller explanation.

**Diagram over prose for spatial concepts.** When a concept is a pipeline (A happens, then B), a loop (perceive → decide → act → repeat), a layered stack (this sits on top of that), or a segmented budget (one fixed total split into named parts), draw it instead of describing it in a paragraph — reserve prose for genuinely non-spatial concepts (a definition, a tradeoff, a rule), and don't also cram the full prose paragraph onto a diagram slide — the diagram plus one short line is the content. `carousel_template.py` provides three helpers, each reserving a fixed height in the slide (no layout math needed), passed via `slide(..., diagram=(kind, payload))`:
- `flow_diagram` / `("flow", [labels])` — boxes connected by arrows. Prefill→Decode, the agent loop, paging into blocks.
- `stack_diagram` / `("stack", [labels])` — vertical stacked boxes, top to bottom. A layer stack (e.g. the agentic system stack).
- `bar_diagram` / `("bar", (segments, dip_label))` — one bar split into proportional labeled segments; `dip_label` (or `None`) shades a callout band across the middle third. The context window's token budget; a "lost in the middle" callout.

**Carousel hard cap: 7 slides total** (title + closing included, so ~5 content slides). This is a ceiling, not a target — group facts aggressively to fit under it rather than thinning content across more slides. Long lists (source page has more distinct facts than 5 content slides can each carry substantively) mean splitting into two posts, not stretching one carousel past 7.

**Code examples:** when the source material has a real code snippet, formula, or API call, render it as an actual code block (carousel) or footer code line (single image) — not a prose paraphrase. Skip only when the source genuinely has no such artifact; never fabricate one to fill a slide. `code=` in `slide()` also accepts a `"\n"`-joined multi-line string when a real snippet needs more than one line (e.g. the nested-decorator shape) — the block grows to fit; a single-line string keeps the original fixed-height block.

**Files (bundled):**
- `assets/fonts/` — Liberation Sans Bold, Regular, Mono (SIL Open Font License, bundled so this works on any machine without system font installs)
- `carousel_template.py` → `slide()` per slide: slide_no, total, kicker, headline, body_lines, optional code/closing_q/diagram. Title slide = no code. Content slide = kicker "Role N"/"Step N" + code (or diagram, see above). Closing slide = kicker "Takeaway" + closing question. Each `body_lines` entry renders as its own paragraph with a gap after it — never split one continuous sentence across two entries (it reads as two disconnected fragments with an odd gap mid-thought); either let one long entry word-wrap on its own, or make the split a real sentence boundary.
- `single_image_template.py` → `single_image()`: headline + list of (name, description) + footer code line. Keep each item's `description` to roughly one line (~50-55 chars) — the template wraps and vertically centers automatically, but with 4-5 items a description that wraps to 2+ lines can still push past the footer code block. If a description needs more than one line to say something real, that item belongs in a carousel slide instead, not squeezed into a single-image row.

Both scripts resolve fonts relative to their own file location (`assets/fonts/`) — no system font dependency, works wherever the skill folder is placed. Always generate via these scripts; never hand-craft an AI image prompt for this niche.

**Delivery & storage:** save visuals to `assets/social-posts/NN-slug/` at the repo root (`slide-01.png`, `slide-02.png`, ... or `image.png`), not a scratch/temp path — keeps output traceable across posting waves. Default is Krishna uploads to Buffer himself — give the local file path(s), no Artifact preview unless he asks to view them in-panel. If he asks to post directly via Buffer MCP tools, follow Buffer Delivery below.

## Critique & Auto-Approval Gate

After drafting (copy + visual, before Buffer Delivery), **open and actually look at every rendered slide/image** — the checklist below scores `copy.md` content and structural rules, but rendering bugs (a sentence split across two `body_lines` leaving an odd gap mid-thought, a stray literal `**` in body prose silently bolding the rest of the line, text overflowing a code block or wrapping awkwardly) are only visible in the PNG itself and are invisible in the source text. Score pass/fail, score = passed / 16 × 100:

*Writing Style:* (1) no hype/filler/forced hooks, (2) every term explained inline on first use, (3) defined terms bolded per the convention, (4) each abstract concept has a concrete, plugged-in example.
*Content Approach:* (5) concept taught before any experience anecdote, (6) no invented/forced anecdote, (7) if Interview-nugget pillar, traces to a real `_interview.md` entry.
*Platform & Hashtags:* (8) LinkedIn ≤1200 chars/no emoji/ends on question/hashtags last line/3-5 tags from the pool, (9) Instagram 5-6 lines/≤2 emoji/≤5 tags from the pool/no generic tags, (10) carousel captions aren't a slide-by-slide transcript.
*Visuals:* (11) template choice (carousel vs single) matches the item-count rule, (12) carousel ≤7 slides, (13) diagram used for spatial concepts / code rendered as a real block where the source has one, (16) every rendered slide/image was actually viewed and shows no split-sentence gaps, no accidental bolding from a stray `**`, and no wrapping/overflow artifacts.
*Accuracy:* (14) source page re-read fresh this session, (15) any external-sourced/uncertain claim was web-searched and confirmed or softened.

**Threshold: 80%** (13/16).
- **≥80%:** auto-approved — proceed straight to Buffer Delivery (or hand off local files) without waiting on Krishna.
- **<80%:** attempt one auto-fix pass — address each failing item per its rule above, regenerate copy/visual as needed, then re-score once.
  - Fixed to ≥80%: auto-approved, but tell Krishna what was fixed and the before/after score.
  - Still <80%: hold — do not schedule to Buffer. Report the score, the specific failing items, and what the auto-fix pass already tried, and wait for Krishna's review.

## Buffer Delivery (when posting directly via the Buffer MCP tools)

- **Default is `scheduled` (live-armed), not draft.** Every `create_post` sets `saveToDraft: false` (or omits it) alongside `mode: "customScheduled"` and a real `dueAt` (ISO 8601, IST `+05:30`, from the post's schedule slot) — it auto-publishes at that time, no further review step. Use `saveToDraft: true` only if Krishna explicitly asks for a draft. A `dueAt`-less post didn't reliably surface in Krishna's Buffer calendar — always set one.
- **`edit_post` re-validates the whole post, not a merge** — pass `text`/`assets`/`metadata` in full every time (fetch via `get_post` first), even for a pure reschedule. A bare status-only retry is rejected. Check the returned `status`/`dueAt` match what you intended.
- **Only two channels in scope**: LinkedIn ("Krishna Kakarla") and Instagram ("krishnakakarla88"). YouTube is connected but out of scope unless Krishna explicitly asks.
- **Images need a public URL**, not a local path — commit + push the post's folder to this repo's public GitHub remote first, then use the resulting `raw.githubusercontent.com/.../main/...` URL. Confirm the push landed before calling `create_post`.
- **LinkedIn requires `schedulingType: "automatic"`** — `"notification"` errors out on LinkedIn channels. **Instagram needs `metadata.instagram: { type: "post", shouldShareToFeed: true }`** alongside the image assets.
- **10-scheduled-posts/channel cap** (see Schedule section) — a `create_post` past it errors "Scheduled posts limit reached." Queue in batches; report the block to Krishna rather than silently stopping partway.
- After creating or fixing a post, verify with `get_post` and report the ID(s) and scheduled time back. Always tell Krishna which organization/channel names were used — don't just cite IDs.

## Accuracy — Always Re-Read the Live Source, Never Post From Memory

When a post is grounded in a knowledge-base page (or any repo doc), re-read that page fresh at copy-drafting time — don't rely on an earlier summary or a prior conversation's notes, the source may have been edited since. If the source page itself flags a claim as external-sourced, not independently verified, or otherwise uncertain, run a web search on that specific claim before stating it as fact in copy — confirm it still holds, or soften the phrasing if search turns up something contradicting or more current. This applies to every post, not just first-time topics.

## Video — Rare Add-on

~1 in 5-7 posts, only when the concept is genuinely motion-friendly (transformation/flow/before-after). AI-generated only, one continuous 15-20s motion, no beat structure. Default is always image.

## Output Format

```
--- LINKEDIN ---
[post]

--- INSTAGRAM ---
[post]

--- VISUAL FORMAT ---
[single | carousel — X slides]
[per-slide: kicker / headline / body / code]

--- SCHEDULE --- (only if weekday given)
[day] slot [1|2|3]: IG [time] · LinkedIn [time]
```
