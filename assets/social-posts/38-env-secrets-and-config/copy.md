--- LINKEDIN ---
Every agent needs credentials — a Groq API key, a Qdrant URL — and none of it belongs typed directly into source files. A .env file plus python-dotenv is the baseline: load_dotenv() reads the file and copies KEY=value pairs into os.environ, so the rest of your code just calls os.getenv() like any environment variable. It never overwrites a real export by default.

The subtler decision is when you check a required key actually exists. Tempting to check at import time — the moment config.py runs, fail loudly if missing. That feels safe, but it silently breaks anything that imports the module transitively without a live call — most commonly your test suite, which shouldn't need a real key just to import a model three files away. The fix: validate at your actual entry points (main(), a FastAPI startup hook) — never at import.

One more gotcha: env vars are always strings. A malformed inline comment like "PORT=8000 # http port" breaks a naive int(os.getenv("PORT")). Regex out the leading integer and fall back to a default.

Do you validate required env vars at import time, or at the entry point?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Secrets don't belong in source files. 🔐

load_dotenv() fills os.environ — then os.getenv("GROQ_API_KEY") like any env var. Never overwrites a real shell export.

The real design call: validate required keys at your entry point, not at import — or your test suite needs a live key just to load a model file.

Env vars are always strings — regex out malformed values instead of trusting them raw.

Full breakdown in the carousel.

Import time, or entry point?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Secrets Don't Belong In Source Files"
2. Core mechanics — load_dotenv() fills os.environ (code)
3. Gotcha — it never overwrites a real export
4. The real design call — validate at the entry point, not import (code)
5. Defensive parsing — env vars are always strings (code)
6. Takeaway — a .env file is convenience, not a control (closing question)
