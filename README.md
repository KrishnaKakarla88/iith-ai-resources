# ShopSense — IITH Applied AI Capstone

Multi-agent customer care/ops system for a fictional marketplace ("Kartway"), built module-by-module (single agent → resilience → tracing → multi-agent orchestration → MCP → FastAPI + guardrails).

## Repo map

| Path | What it is |
|---|---|
| `/labs` | Course notebooks — fixed, never edited |
| `/lab-summaries` | Condensed per-notebook reference generated from `/labs`, indexed at `INDEX.md` |
| `/presentations` | Converted course slide decks, one file per day |
| `/data` | Datasets the labs/capstone consume |
| `/knowledge-base` | Topic-first revision/interview-prep reference — see below |
| `CLAUDE.md` | Instructor-mode instructions for Claude Code: build order, stack, teaching loop |
| `plan.md` | Source of truth for the `/knowledge-base` build (manifest + rationale) |

See [CLAUDE.md](CLAUDE.md) for the full build order, stack, and repo layout detail.

## Knowledge base (revision / interview prep)

`/knowledge-base/` is a topic-first, MkDocs-rendered reference derived from `/lab-summaries/` — a guided path (numbered stages, prerequisites) plus a `[[wikilink]]`-connected reference graph, viewable both as a rendered site and directly in Obsidian.

### Viewing it locally

```bash
uv run mkdocs serve
```

Then open **http://127.0.0.1:8000/** in a browser.

Don't open `site/index.html` directly by double-clicking it (`file://...`) — the site uses clean directory-style URLs (e.g. `/06-rag/chunking/`), which only resolve over a real HTTP server. `mkdocs serve` gives you that, plus live-reload on save. `uv run mkdocs build` still works for producing a static `site/` folder, but it's meant to be *served*, not opened as local files.

Alternatively, open the `knowledge-base/` folder directly as an Obsidian vault — the same `[[wikilink]]` syntax works natively there, no server needed.

### Deploying

Live at **https://krishnakakarla88.github.io/iith-ai-resources/**, published via `uv run mkdocs gh-deploy` (builds the site and pushes it to the `gh-pages` branch). Re-run that command to publish any future content changes — nothing auto-deploys on push.
