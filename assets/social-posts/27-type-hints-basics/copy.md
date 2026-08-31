--- LINKEDIN ---
Python never enforces type hints at runtime. Nothing stops add(1, "two") from running, even if add is defined as def add(a: int, b: int) -> int. CPython ignores the annotation entirely at execution time — it exists for humans reading the code, and for tools that read it and act on it.

That second part is why type hints matter for building with LLMs specifically. Pydantic turns a class's type-annotated fields into a runtime validator. FastMCP turns a function's type-annotated parameters into the JSON schema an LLM reads to decide how to call it. The annotation isn't decoration for these libraries — it is the contract.

Literal["tool", "retrieval", "direct"] is the clearest example of that contract mattering. A bare str field accepts any string — a hallucinated route like "unknown" would pass type-level scrutiny with no complaint. Literal narrows the type to an exact enumerated set, so Pydantic can reject any value outside it at validation time.

Do you run a static type checker in CI, or rely on hints alone?

#AppliedAI #Python #LLM #AIEngineering

--- INSTAGRAM ---
Python never checks your type hints. Pydantic and FastMCP do. 🏷️

def add(a: int, b: int) -> int: — CPython ignores this at runtime. add(1, "two") just runs.

But Pydantic reads that same annotation to validate data. FastMCP reads it to build the schema an LLM uses to call your function.

Literal["tool", "retrieval", "direct"] vs a bare str is the difference between rejecting a hallucinated value and silently accepting it.

Full mechanism in the carousel.

Static type checker in CI, or hints alone?

#AppliedAI #Python #LLM #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Type Hints Are The Contract"
2. Annotation, not enforcement (code: add(1,"two") runs)
3. Why it matters here — Pydantic + FastMCP read the annotation
4. Literal narrows what str allows (code: route: Literal[...])
5. The optional field pattern (code: str | None = None)
6. Takeaway — hints without a checker (closing question)
