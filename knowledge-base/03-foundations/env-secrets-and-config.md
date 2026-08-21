---
stage: "03-foundations"
tools: [python-dotenv]
tags: [config, secrets, env-vars]
last_verified: 2026-08-20
verified_against: "python-dotenv 1.2.2"
---

# Env, secrets, and config

Loading API keys and settings from a `.env` file instead of hardcoding them, and validating they're actually present before your app tries to use them — not when Python happens to import the module that needs them.

## Prerequisites
- [[what-is-an-llm]]

## In plain English

Every agent in this stack needs credentials — a Groq API key, a Qdrant URL, a Supermemory token — and none of those belong typed directly into your source files. A `.env` file is a plain-text list of `KEY=value` pairs that lives next to your code but stays out of version control; `python-dotenv` reads that file at startup and copies its contents into `os.environ`, so the rest of your code just calls `os.getenv("GROQ_API_KEY")` like it would for any environment variable, whether that variable came from the `.env` file, a CI secret, or a real shell export.

The subtler design decision is *when* you check that a required key actually exists. It's tempting to check at import time — the moment `config.py` runs, fail loudly if `GROQ_API_KEY` is missing. That feels safe, but it silently breaks anything that imports your module transitively without needing to make a live call — most importantly, your test suite. A unit test for a Pydantic model or a prompt template shouldn't need a real API key just because it imported a file that, three imports down, imports something that imports `config.py`. The fix is to validate required env vars at your actual entry points (`main()`, the FastAPI startup hook, the CLI's first line) — not at module import.

## Core mechanics

| Concept | What it does |
|---|---|
| `.env` file | Plain `KEY=value` lines, one per secret/setting, kept out of git via `.gitignore` |
| `load_dotenv()` | Reads `.env`, writes each key into `os.environ` if not already set there |
| `os.getenv(key, default)` | Standard library read — works the same regardless of where the value came from |
| Fail-fast validation | A function called at entry points that raises/exits if a required key is missing, run once, deliberately not at import |
| Defensive parsing | Env vars are always strings — a malformed inline comment (`PORT=8000 # http port`) breaks a naive `int(os.getenv("PORT"))`; regex out the leading integer and fall back to a default instead of trusting the raw string |

`load_dotenv()` **does not overwrite** existing environment variables by default — a real shell/CI export always wins over a stale `.env` value, which is the behavior you want.

## Sample code

```python
# config.py
import os, re
from dotenv import load_dotenv

load_dotenv()  # populates os.environ from .env, doesn't overwrite real env vars

def _int_env(key: str, default: int) -> int:
    """Defensive int parsing — malformed .env inline comments break naive int(getenv())."""
    raw = os.getenv(key)
    if raw is None:
        return default
    match = re.match(r"\s*(\d+)", raw)
    return int(match.group(1)) if match else default

REQUIRED_KEYS = ["GROQ_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]

def validate_required_env() -> None:
    """Call this at entry points (main(), FastAPI startup) — never at import time,
    so tests can import this module without live keys present."""
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {missing}")
```

```python
# main.py — the one place validate_required_env() actually runs
from config import validate_required_env

def main():
    validate_required_env()
    ...

if __name__ == "__main__":
    main()
```

Version note: `python-dotenv` versions before 1.2.2 carry a path-traversal vulnerability (CVE-2026-28684) via symlinked `.env` files — this repo's `>=1.2.2` pin is a security floor, not just a feature bar.[^dotenv-cve]

## Alternatives

| Approach | Where it lives | Boring/simple alternative to python-dotenv? |
|---|---|---|
| `python-dotenv` | Standalone package, `theskumar/python-dotenv` | — |
| `pydantic-settings` | Pydantic ecosystem, `BaseSettings` class | No — strictly more: adds type validation and clear per-field error messages on top of what dotenv loads, at the cost of a schema class to maintain[^pydantic-settings] |
| Cloud secret manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault) | Managed service | No — heavier, but the actual production answer once a leaked env var is a real incident, not a toy risk: centralized rotation, access control, and audit trails a flat file can't give you[^secrets-2026] |
| Doppler / Infisical | Secrets-as-a-service, syncs to env at runtime | No — same tier as a cloud secret manager, positioned as the more dev-friendly drop-in replacement for team `.env` sharing |
| Plain `os.environ` + a shell-level `.env` loader (`set -a; source .env; set +a`) | No Python dependency | **Yes** — the boring option; works fine for a single script, loses dotenv's `.env`-file-format parsing (quoting, comments, multiline values) and Windows portability |

## How this shows up in the capstone

Milestone 1 (provider-agnostic LLM client + structured intake) can't make its first Groq call without a validated `GROQ_API_KEY` — this is the first thing that has to work, before any agent code runs; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why validate required env vars at the entry point instead of at import time?**
  A: Import-time validation breaks anything that imports the module transitively without needing a live call — most commonly your test suite, which shouldn't need a real API key just to import a Pydantic model three files away.
- **Q: Does `load_dotenv()` overwrite a real environment variable with the same key from `.env`?**
  A: No — by default it only sets variables not already present in `os.environ`, so a real shell/CI export takes precedence over a stale `.env` file.

## Production gotchas & best practices

- Lab/production gotcha: malformed `.env` inline comments (`TIMEOUT=30 # seconds`) broke a naive `int(os.getenv("TIMEOUT"))` call — regex-extract the leading integer and fall back to a default rather than trusting the raw string.
- Production practice: central fail-fast validation (`validate_required_env()`), called at entry points only, never at import — tests import modules transitively without live keys present, and import-time validation breaks that.
- Production practice (2026 guidance): `.env` files are convenient but not a control — a leaked env var can surface through process dumps, debug output, misconfigured build logs, or an inherited shell session. If an env var is the only surviving copy of a production secret, that's accepted risk, not a solved problem — production credentials belong in a secrets manager with rotation and audit trails, with env vars used only as the runtime delivery mechanism.[^secrets-2026]

## Course vs. production

The lab/course setup uses a single `.env` file per developer machine — adequate for a capstone with one Groq key and one Qdrant instance. In production, non-sensitive config (timeouts, feature flags) still lives in environment variables, but secrets are resolved from a secrets manager at runtime and injected into the process environment at deploy time, not committed to a file anywhere, even a gitignored one.

## Related
- **Feeds into** — [[raw-llm-clients]], [[litellm-basics]]
- **Paired with** — [[rate-limits-quotas-and-caching]] (both are "the operational reality before your first real call")

## Sources

**Lab sources**
- `labs/production-notes.md` (§ "Schema Validation" — defensive env-var parsing; § "Error Handling" — central fail-fast validation at entry points only)

**Web sources**
- [python-dotenv best practices, CVE-2026-28684](https://coderivers.org/blog/install-dotenv-python/) — accessed 2026-08-20
- [Pydantic Settings docs](https://docs.pydantic.dev/1.10/usage/settings/) — type-safe env var validation comparison, accessed 2026-08-20
- [Production Secrets Management: From .env Files to HashiCorp Vault (2026 Guide)](https://dev.to/young_gao/production-secrets-management-from-env-files-to-vault-and-beyond-cp1) — accessed 2026-08-20

[^dotenv-cve]: python-dotenv path-traversal CVE-2026-28684, fixed in 1.2.2 — see coderivers.org source above.
[^pydantic-settings]: docs.pydantic.dev — pydantic-settings loads `.env` directly and adds type validation on top.
[^secrets-2026]: dev.to/young_gao — 2026 guide on env-var vs secrets-manager tradeoffs in production.
