---
stage: "01-python-refresher"
tools: []
tags: [primer, python, collections]
last_verified: 2026-08-20
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13)"
---

# Lists, tuples, sets, dicts

Python's four built-in collection types — each optimized for a different question ("in what order", "can this change", "is this unique", "how do I look this up by name") — and picking the wrong one is the most common source of avoidable bugs and slow code in everyday scripts.

## Prerequisites
- [[python-data-types-and-mutability]]

## In plain English

A single scalar value (a number, a string) can't represent "a customer's order history" or "a set of allowed tool names" — you need a collection. Python gives you four built-in ones, and the choice between them isn't cosmetic:

- **List** — an ordered, changeable sequence. Use it when you have a bunch of things, order matters (or might later), and you'll add/remove/reorder over time. This is the default "just give me a bag of things" collection.
- **Tuple** — an ordered, unchangeable sequence. Use it when the collection represents a fixed, small structure that shouldn't change after creation — a coordinate pair, a function returning multiple values, a dict key made of several parts (tuples are hashable, lists aren't).
- **Set** — an unordered collection of unique values, with fast membership testing. Use it when you care about "is X in here" and "no duplicates," not about order.
- **Dict** — a mapping from keys to values, with fast lookup by key. Use it when you need to look something up by name/id rather than by position — the workhorse for structured data (a parsed JSON object, a row of fields, a lookup table).

## Core mechanics

| Type | Ordered | Mutable | Duplicates | Typical use |
|---|---|---|---|---|
| `list` | Yes | Yes | Allowed | Sequences you'll grow/shrink/reorder |
| `tuple` | Yes | No | Allowed | Fixed-shape records, dict keys, multiple return values |
| `set` | No | Yes | Not allowed (auto-deduped) | Membership tests, deduplication, set algebra |
| `dict` | Insertion order preserved | Yes | Keys unique, values may repeat | Lookup by key, structured records |

Membership testing (`x in collection`) is where the choice matters most for performance: it's O(1) average for `set` and `dict` (hash lookup) but O(n) for `list`/`tuple` (linear scan) — checking membership against a large list repeatedly in a loop is a common accidental-slowness bug; a `set` fixes it with no other code change.

Comprehensions build all four concisely:

```python
squares = [n * n for n in range(5)]                 # list
unique_lengths = {len(w) for w in words}             # set
word_lengths = {w: len(w) for w in words}            # dict
```

## Sample code

```python
# list — ordered, mutable
tool_names = ["search_catalog", "check_fine_policy"]
tool_names.append("write_note")

# tuple — ordered, fixed; common as a function's multi-value return
def min_max(values: list[float]) -> tuple[float, float]:
    return min(values), max(values)

low, high = min_max([3.0, 1.0, 4.0])   # unpacking

# set — unique, fast membership
allowed_routes = {"tool", "retrieval", "direct"}
if requested_route in allowed_routes:   # O(1) average
    ...

# dict — lookup by key
tool_args = {"city": "Chennai", "units": "metric"}
city = tool_args.get("city", "unknown")   # .get() avoids a KeyError on a missing key
```

`.get(key, default)` vs `collection[key]`: indexing raises `KeyError` on a missing key, `.get()` returns a fallback — prefer `.get()` for optional fields (e.g. reading a possibly-absent field from a parsed tool-call argument dict) and indexing only when the key's presence is already guaranteed.

## How this shows up in the capstone

Dicts are the default shape for parsed tool-call arguments and LLM JSON output before validation; sets show up as whitelists (e.g. legal next-agent routes, allowed tool names) that a router's output is checked against rather than trusted outright.

## Production gotchas & best practices

- A `list` used purely for membership testing in a hot loop is a common accidental-performance bug — swap to `set` when order doesn't matter and duplicates aren't meaningful; the fix is usually a one-line type change ([Python docs — Time Complexity](https://wiki.python.org/moin/TimeComplexity), accessed 2026-08-20 — community wiki, not primary docs, but the complexity table matches CPython's documented implementation).
- Dict insertion order is preserved and guaranteed as of Python 3.7+ (a language guarantee, not an implementation detail to rely on informally) — code can depend on iteration order matching insertion order ([Python docs — dict](https://docs.python.org/3/library/stdtypes.html#dict), accessed 2026-08-20).
- Tuples as dict keys only work because tuples are hashable — a tuple containing a list is not hashable and raises `TypeError`, since hashability requires every element to be immutable too.

## Course vs. production

Not applicable — this page is language fundamentals, not a course-vs-production tool comparison.

## Related

- **Builds on** — [[python-data-types-and-mutability]]
- **Prerequisite for** — [[functions-args-kwargs]], [[type-hints-basics]]

## Sources

**Lab sources**

None — this page has no matching lab or notebook; see task framing (01-python-refresher is lab/notebook-silent by design).

**Web sources**
- [Python 3 tutorial — Data Structures](https://docs.python.org/3/tutorial/datastructures.html) — list/tuple/set/dict operations and comprehensions, accessed 2026-08-20
- [Python 3 library reference — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — dict ordering guarantee, set/frozenset semantics, accessed 2026-08-20
