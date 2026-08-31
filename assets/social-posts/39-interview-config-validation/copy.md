--- LINKEDIN ---
Real interview scenario: your test suite imports a module that defines a Pydantic settings model requiring GROQ_API_KEY. CI has no real key configured, and it starts failing to even import that module. What's the root mistake?

Validating required config at import time means anything that transitively imports the module is forced to have a real key — including a test that only needs the type, not a live call. The check ran at the wrong point in the lifecycle: import, not entry.

The fix is moving that check to the actual entry point — app startup, or lazily on first real use — not module import. Importing for tests, tooling, or docs generation shouldn't require secrets a live call would need.

Same discipline that keeps a unit test from needing a real GROQ_API_KEY just to load a Pydantic model three files away.

Has an import-time check ever broken your CI unexpectedly?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Real interview scenario. 🔍

Your test suite imports a module needing GROQ_API_KEY. CI has no key. Import itself fails.

The mistake: validation ran at import, not at the entry point — so anything that transitively imports the module gets forced to carry a real key.

Fix: move the check to main() or app startup.

Full scenario + answer in the carousel.

Has an import-time check ever broken your CI?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 5 slides
1. Title — "Why Did CI Suddenly Need An API Key?"
2. The question — import-time validation bit back (code)
3. The answer — the check ran at import, not entry
4. The fix — move the check to the entry point (code)
5. Takeaway — import should never cost a secret (closing question)
