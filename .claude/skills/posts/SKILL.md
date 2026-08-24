---
name: posts
description: Draft LinkedIn + Instagram posts teaching Applied AI Engineering concepts — RAG, LangGraph, MCP, LLM tool-calling, LangFuse, LangChain, chunking, reranking, etc. — grounded in Krishna's course labs, capstone project, and production AI use cases. Teaching-first, caveman tone, no hype. Generates a matching carousel or single-image visual via a coded Pillow template (no AI-generated art). Use whenever Krishna wants to post about his AI engineering learning/build work.
---

# Applied AI Engineering Posts

Output LinkedIn + Instagram copy, plus a matching visual (carousel or single image), every time.

## Tone: Balanced Caveman — Short Lines, Not Cryptic Ones

Short sentences, no filler, no hype words. But every line has to stand on its own for someone refreshing the topic or meeting it for the first time — a term never gets dropped without the phrase that explains what it does or why it matters. Line-per-fact structure stays; each line carries one real explanatory clause, trimmed of secondary qualifiers, not a compressed label and not a full multi-clause sentence either.

- One line = one fact or one step: subject + what it does/means, in as few words as that still takes. Cut secondary qualifiers ("the one-time process of," "what happens every time you," "the already-") that don't change what the reader understands. Blank line between lines.
- Match the vocabulary the source wiki page itself uses — if the page calls something "parametric knowledge" or "autoregressive," use that term, then explain it in the same breath, don't invent a simpler synonym that drifts from the source.
- Each line should be dense (a real term, an import, a mechanism) — never vague filler stretched out to sound simple, and never so compressed that a newcomer has to fill in the connective logic themselves.
- Combine cause + scope + verdict only when they're truly one thought.
- Hook = the concept itself, a question, or a real tension. No "In this post I'll cover..."
- No client/company names. Course name OK (public cert).
- Never say "built in public" or similar framing — the work isn't pitched as a public-build narrative.
- Never ask the audience to pick what gets covered next (no "which should I do first?"). Krishna sets the roadmap; closing questions invite discussion of the concept itself, not content planning.

✓ "An LLM's knowledge lives in its weights — billions of parameters fixed after training." — short, but a newcomer doesn't need outside context to follow it.
✓ "SystemMessage sets behavior. Use SystemMessagePromptTemplate when it needs variables." — still fine when the line is already this tight at full length.
✗ "An LLM's knowledge lives entirely in its weights — billions of numeric parameters fixed once training ends." — correct content, but "entirely" and "numeric" and "once" are qualifiers that don't add anything a reader needs; trim them.
✗ "Weights: billions of frozen numbers, set once during training." — a label-fragment, not a sentence; reads as a flashcard, not teaching.
✗ "AI is transforming how we build apps!" — short but empty, this is hype, not teaching.

## Mode: Teaching-First (default, always)

Teach the concept plainly first — imports, syntax, how it fits, what it's for. Real lab/capstone/production experience is an **optional bonus**, added after the teaching only when a real moment exists (a bug, a ratio, an issue). Never invent or force one.

## Pillars (rotate)

1. **Concept teaching** (primary) — one concept, taught plainly, experience tacked on only if real.
2. **Production tradeoff** (occasional) — real capstone/production decision or bug. Problem → decision → result. Experience leads.
3. **Interview nugget** (occasional) — a real question actually faced + the real answer, in caveman form.

❌ Hype, unfinished thoughts, forced anchors, syllabus recaps with no teaching value.

## Platform & Hashtags

**LinkedIn:** ≤1200 chars, no emoji, ends on an engagement question, hashtags last line.
**Instagram:** 5-6 lines, 1-2 functional emoji max, hashtag block separate at end.

**Caption vs. visual — don't make the caption a transcript of the slides.** When there's a matching carousel, the caption's job is hook + the 2-3 highest-value points + the closing question, not a paragraph-per-slide restatement of every concept. The carousel is where the full granular teaching lives (one concept per slide, in depth); the caption should give someone enough to learn something real from the text alone while still giving a real reason to swipe (a line like "full breakdown in the carousel" or letting an unanswered thread pull them in) — not duplicate the carousel's content 1:1. For a single-image post, the caption and image content overlap more naturally since there's no multi-slide depth to point to.

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

**Slide count vs. item count:** one item per slide is not a rule — a single tool/term with only a line or two of content leaves a slide mostly blank. Group 2-3 related items onto one slide (stack them as sub-headlines or a labeled list in `body_lines`) instead of stretching thin content across too many slides. Keep one item per slide only when it genuinely needs its own code block or fuller explanation.

**Carousel hard cap: 7 slides total** (title + closing included, so ~5 content slides). This is a ceiling, not a target — group facts aggressively to fit under it rather than thinning content across more slides. Long lists (source page has more distinct facts than 5 content slides can each carry substantively) mean splitting into two posts, not stretching one carousel past 7.

**Code examples:** when the source material has a real code snippet, formula, or API call, render it as an actual code block (carousel) or footer code line (single image) — not a prose paraphrase. Skip only when the source genuinely has no such artifact; never fabricate one to fill a slide.

**Files (bundled):**
- `assets/fonts/` — Liberation Sans Bold, Regular, Mono (SIL Open Font License, bundled so this works on any machine without system font installs)
- `carousel_template.py` → `slide()` per slide: slide_no, total, kicker, headline, body_lines, optional code/closing_q. Title slide = no code. Content slide = kicker "Role N"/"Step N" + code. Closing slide = kicker "Takeaway" + closing question.
- `single_image_template.py` → `single_image()`: headline + list of (name, description) + footer code line.

Both scripts resolve fonts relative to their own file location (`assets/fonts/`) — no system font dependency, works wherever the skill folder is placed.

**Delivery:** default is Krishna uploads images to Buffer himself — after generating slides, give the local file path(s), and do not publish an Artifact preview by default (that's extra work he didn't ask for; only do it if he explicitly asks to preview/view them in-panel). If he instead asks to post directly via the Buffer MCP tools, follow the Buffer Delivery section below.

**Asset storage:** save generated visuals to `assets/social-posts/NN-slug/` at the repo root (numbered per post — carousel slides as `slide-01.png`, `slide-02.png`, ...; single image as `image.png`), not a scratch/temp path — keeps output traceable across posting waves.

Always generate via these scripts. Never hand-craft an AI image prompt for this niche.

## Buffer Delivery (when posting directly via the Buffer MCP tools)

- **Draft only, never live, unless explicitly told otherwise.** Every `create_post` call defaults to `saveToDraft: true`. Never queue, schedule, or publish a real post to a live channel without Krishna explicitly asking for that specific post.
- **`edit_post` does NOT preserve draft status by omission.** It re-validates the whole post from what you send, not a merge — leaving `saveToDraft` off an edit call flips the post from `draft` to `scheduled` (live-armed to auto-post at its `dueAt`), even if it was already a draft and you only meant to change the text or an asset URL. Pass `saveToDraft: true` explicitly on **every** `edit_post` call, every time, no exceptions. After any edit, check the returned `status` field is `"draft"` before moving on — if it isn't, immediately re-issue the edit with `saveToDraft: true` (and the full text/assets/metadata again, since a bare `saveToDraft`-only retry gets rejected as "Post must have either text or media").
- **Only these two channels are in scope**: LinkedIn ("Krishna Kakarla" profile) and Instagram ("krishnakakarla88" business). The connected YouTube channel is out of scope — never post or draft to it unless Krishna explicitly asks.
- **Images need a public URL** — Buffer's `assets` field takes a direct file URL, not a local path or upload. Since generated slides live in `assets/social-posts/NN-slug/` in this git repo (public GitHub remote), commit + push that post's folder first, then use the resulting `raw.githubusercontent.com/.../main/...` URLs as the asset sources. Confirm the push landed (or that the file already exists at that URL) before calling `create_post`.
- **LinkedIn requires `schedulingType: "automatic"`** — `"notification"` errors out on LinkedIn channels ("Notification scheduling is not supported for linkedin channels").
- **Instagram posts need `metadata.instagram: { type: "post", shouldShareToFeed: true }`** alongside the image assets.
- **Set a real `dueAt` on every draft, using this plan's schedule slot for that post** — pass `mode: "customScheduled"` with `dueAt` (ISO 8601, IST offset `+05:30`, built from that post's weekday/time in the schedule table) alongside `saveToDraft: true`. A draft created with no `dueAt` didn't reliably surface anywhere in Krishna's Buffer calendar/channel view even though it existed via the API — setting the actual scheduled date/time is what made it visible. Do this on `create_post` directly when possible; if scheduling isn't accepted at creation, follow up with `edit_post` the same way used to fix post #1 (carry `text`/`assets`/`metadata` forward from `get_post`, since `edit_post` re-validates the whole post rather than merging).
- After creating (or fixing) a draft, verify it with `get_post` (or `list_posts` filtered to `status: ["draft"]`) and report the post ID(s) and scheduled time back — Buffer's own UI can file drafts in ways that aren't obvious, so don't assume something's wrong (or right) without checking via the API first.
- Always tell Krishna which organization/channel names were used (per the Buffer MCP server's own instructions) — don't just cite IDs.

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
