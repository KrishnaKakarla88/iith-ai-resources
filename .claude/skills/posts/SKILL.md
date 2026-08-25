---
name: posts
description: Draft LinkedIn + Instagram posts teaching Applied AI Engineering concepts — RAG, LangGraph, MCP, LLM tool-calling, LangFuse, LangChain, chunking, reranking, etc. — grounded in Krishna's course labs, capstone project, and production AI use cases. Teaching-first, caveman tone, no hype. Generates a matching carousel or single-image visual via a coded Pillow template (no AI-generated art). Use whenever Krishna wants to post about his AI engineering learning/build work.
---

# Applied AI Engineering Posts

Output LinkedIn + Instagram copy, plus a matching visual (carousel or single image), every time.

## Tone: Balanced Caveman — Short Lines, Not Cryptic Ones

Short sentences, no filler, no hype words. But every line has to stand on its own for someone refreshing the topic or meeting it for the first time — a term never gets dropped without the phrase that explains what it does or why it matters. Line-per-fact structure stays; each line carries one real explanatory clause, trimmed of secondary qualifiers, not a compressed label and not a full multi-clause sentence either.

- One line = one fact or one step: subject + what it does/means, dense (a real term, an import, a mechanism) but stripped of qualifiers ("the one-time process of," "what happens every time you") that don't change what the reader understands. Blank line between lines.
- Match the vocabulary the source wiki page itself uses — if it calls something "parametric knowledge" or "autoregressive," use that term and explain it in the same breath, don't invent a simpler synonym that drifts from the source.
- Hook = the concept itself, a question, or a real tension. No "In this post I'll cover..."
- No client/company names. Course name OK (public cert). Never "built in public" framing.
- Never ask the audience to pick what gets covered next (no "which should I do first?"). Krishna sets the roadmap; closing questions invite discussion of the concept, not content planning.

✓ "An LLM's knowledge lives in its weights — billions of parameters fixed after training." — short, but a newcomer doesn't need outside context to follow it.
✗ "An LLM's knowledge lives entirely in its weights — billions of numeric parameters fixed once training ends." — "entirely," "numeric," "once" are qualifiers that add nothing; trim them. ("Weights: billions of frozen numbers, set once." is the same fault taken further — a flashcard fragment, not a taught sentence.)
✗ "AI is transforming how we build apps!" — short but empty, this is hype, not teaching.

## Ground Abstract Concepts With A Real Example

An abstract mechanism (tokenization, an attention head, a decode step) reads as pure theory until it's tied to a concrete instance — a real word, a real number, a real snippet. Wherever a concept is genuinely abstract (not already concrete, like a code import), work in a short, real example rather than leaving the definition to stand alone. Pull it from the source wiki page when it has one; invent a small, obviously-correct one when it doesn't — never a vague placeholder like "some word." Check every concept slide against this before finalizing a carousel — a plugged-in instance, or only the mechanism stated in the abstract? Common miss, not an edge case.

✓ "A tokenizer splits words into pieces. **Example:** **\"tokenization\"** splits into **\"token\"** + **\"ization\"**." — concrete instead of asserted, and the label is bolded so it scans like the term labels around it.
✗ "A tokenizer splits words into subword pieces based on frequency." — technically correct, but a first-time reader has nothing to picture.

## Bold The Term Being Defined

When a line defines or names something ("X is Y," "X: Y," a term-then-explanation pattern — including anything that started life as a wiki table row, e.g. Query/Key/Value or Prefill/Decode) or labels a worked instance (`**Example:**`, `**Worked example:**`), wrap the term/label in `**double asterisks**` in `body_lines` so it renders bold against the regular-weight explanation — `slide()`/`draw_rich_line()` parse `**bold**` spans inline; `single_image_template.py`'s `items` already bolds each row's `name`, no markup needed there. Don't bold whole sentences or every noun — only what a reader should be able to scan for.

✓ "**Query** is what a token looks for. **Key** is what it offers others." — a reader scanning the slide can immediately find each term.
✗ "Query is what a token looks for. Key is what it offers others." — same content, but nothing helps the eye separate the terms from the prose.

## Mode: Teaching-First (default, always)

Teach the concept plainly first — imports, syntax, how it fits, what it's for. Real lab/capstone/production experience is an **optional bonus**, added after the teaching only when a real moment exists (a bug, a ratio, an issue). Never invent or force one.

## Pillars (rotate)

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

## Schedule (IST) — include only if a weekday is specified

Mon: IG 7pm / LI 10am · Tue: IG 5pm / LI 11am · Wed: IG 6pm / LI 4pm · Thu: IG 9am / LI 1pm · Fri: IG 12pm / LI 4pm

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

**Code examples:** when the source material has a real code snippet, formula, or API call, render it as an actual code block (carousel) or footer code line (single image) — not a prose paraphrase. Skip only when the source genuinely has no such artifact; never fabricate one to fill a slide.

**Files (bundled):**
- `assets/fonts/` — Liberation Sans Bold, Regular, Mono (SIL Open Font License, bundled so this works on any machine without system font installs)
- `carousel_template.py` → `slide()` per slide: slide_no, total, kicker, headline, body_lines, optional code/closing_q/diagram. Title slide = no code. Content slide = kicker "Role N"/"Step N" + code (or diagram, see above). Closing slide = kicker "Takeaway" + closing question.
- `single_image_template.py` → `single_image()`: headline + list of (name, description) + footer code line. Keep each item's `description` to roughly one line (~50-55 chars) — the template wraps and vertically centers automatically, but with 4-5 items a description that wraps to 2+ lines can still push past the footer code block. If a description needs more than one line to say something real, that item belongs in a carousel slide instead, not squeezed into a single-image row.

Both scripts resolve fonts relative to their own file location (`assets/fonts/`) — no system font dependency, works wherever the skill folder is placed.

**Delivery:** default is Krishna uploads images to Buffer himself — after generating slides, give the local file path(s), and do not publish an Artifact preview by default (that's extra work he didn't ask for; only do it if he explicitly asks to preview/view them in-panel). If he instead asks to post directly via the Buffer MCP tools, follow the Buffer Delivery section below.

**Asset storage:** save generated visuals to `assets/social-posts/NN-slug/` at the repo root (numbered per post — carousel slides as `slide-01.png`, `slide-02.png`, ...; single image as `image.png`), not a scratch/temp path — keeps output traceable across posting waves.

Always generate via these scripts. Never hand-craft an AI image prompt for this niche.

## Buffer Delivery (when posting directly via the Buffer MCP tools)

- **Default is `scheduled` (live-armed), not draft.** Every `create_post` sets `saveToDraft: false` (or omits it) alongside `mode: "customScheduled"` and a real `dueAt` — it auto-publishes at that time, no further review step, per Krishna's confirmed workflow. Use `saveToDraft: true` only if he explicitly asks for a draft.
- **`edit_post` re-validates the whole post, not a merge.** Whatever you pass (or omit) for `saveToDraft` is exactly what the post ends up as. Always pass it explicitly, with the full `text`/`assets`/`metadata` again — a bare status-only retry is rejected. Check the returned `status` matches what you intended.
- **Only two channels in scope**: LinkedIn ("Krishna Kakarla") and Instagram ("krishnakakarla88"). YouTube is connected but out of scope unless Krishna explicitly asks.
- **Images need a public URL**, not a local path — commit + push the post's folder to this repo's public GitHub remote first, then use the resulting `raw.githubusercontent.com/.../main/...` URL. Confirm the push landed before calling `create_post`.
- **LinkedIn requires `schedulingType: "automatic"`** — `"notification"` errors out on LinkedIn channels.
- **Instagram needs `metadata.instagram: { type: "post", shouldShareToFeed: true }`** alongside the image assets.
- **Every scheduled post needs a real `dueAt`** (ISO 8601, IST offset `+05:30`, from that post's schedule slot) — one created with no `dueAt` didn't reliably surface in Krishna's Buffer calendar even though it existed via the API. Set it on `create_post` directly; if rejected there, follow up with `edit_post` (carrying `text`/`assets`/`metadata` forward from `get_post`).
- **The org plan caps scheduled posts per channel** (currently 10) — a `create_post` past the cap errors with "Scheduled posts limit reached." Slots free up as earlier posts publish; report the block to Krishna rather than silently stopping partway.
- After creating or fixing a post, verify with `get_post` and report the ID(s) and scheduled time back — don't assume something's wrong (or right) without checking the API.
- Always tell Krishna which organization/channel names were used — don't just cite IDs.

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
[day]: IG [time] · LinkedIn [time]
```
