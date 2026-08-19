# ShopSense — IITH Applied AI Capstone

Multi-agent customer care/ops system for a fictional marketplace ("Kartway"), built module-by-module (single agent → resilience → tracing → multi-agent orchestration → MCP → FastAPI + guardrails). See [CLAUDE.md](CLAUDE.md) for the full build order and stack.

## Knowledge base (revision / interview prep)

`/knowledge-base/` is a topic-first, MkDocs-rendered reference derived from `/lab-summaries/` — a guided path (numbered stages, prerequisites) plus a `[[wikilink]]`-connected reference graph, viewable both as a rendered site and directly in Obsidian.

### Viewing it locally

```bash
uv run mkdocs serve
```

Then open **http://127.0.0.1:8000/** in a browser.

Don't open `site/index.html` directly by double-clicking it (`file://...`) — the site uses clean directory-style URLs (e.g. `/06-rag/chunking/`), which only resolve over a real HTTP server. `mkdocs serve` gives you that, plus live-reload on save. `uv run mkdocs build` still works for producing a static `site/` folder, but it's meant to be *served*, not opened as local files.

Alternatively, open the `knowledge-base/` folder directly as an Obsidian vault — the same `[[wikilink]]` syntax works natively there, no server needed.

### Deploying (not done yet, but works as configured)

Since MkDocs' clean URLs are just plain HTTP paths, any static host serving over HTTP — GitHub Pages, Netlify, Vercel — renders and links correctly with no config changes. GitHub Pages specifically would need either `mkdocs gh-deploy` (pushes the built `site/` to a `gh-pages` branch) or a GitHub Action that runs `mkdocs build` and publishes the output; this repo doesn't have either wired up yet by design (local-only for now, per the KB build plan).
