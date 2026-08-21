---
stage: "01-python-refresher"
tools: []
tags: [primer, python, mutability]
last_verified: 2026-08-20
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13)"
---

# Python data types and mutability

The built-in scalar types (`int`, `float`, `str`, `bool`) and the mutable-vs-immutable split that decides whether changing a value in one place silently changes it everywhere else it's referenced.

## Prerequisites

None — this is the starting page.

## In plain English

Every value in Python is an object, and every object belongs to a type. The everyday scalar types are `int` (whole numbers), `float` (decimals), `str` (text), and `bool` (`True`/`False`, which is actually a subtype of `int` — `True == 1` and `False == 0` both hold). None of these can be changed in place: `x = 5; x = x + 1` doesn't modify the object `5`, it points the name `x` at a new object `6`. That's what "immutable" means — the object itself can never change after it's created, only which object a name points to can change.

Collections split the other way. A `list` can be modified in place (`my_list.append(3)` changes the same object every name pointing at it sees), while a `tuple` cannot. This distinction — immutable scalars/tuples vs. mutable lists/dicts/sets — is not a style preference, it's a real behavioral difference: two names pointing at the same mutable object are aliases, and a change through one is visible through the other. Two names pointing at the same immutable object never need to worry about that, because neither can change it.

## Core mechanics

| Type | Mutable? | Notes |
|---|---|---|
| `int` | No | Arbitrary precision, no overflow |
| `float` | No | IEEE-754 double precision — exact decimal comparisons are unreliable (`0.1 + 0.2 != 0.3`) |
| `bool` | No | Subtype of `int`; `isinstance(True, int)` is `True` |
| `str` | No | Any "modification" (`s.upper()`, `s + "x"`) returns a new string object |
| `tuple` | No | Fixed-length, ordered — immutable even though it can hold mutable elements |
| `list` | Yes | Ordered, in-place `.append()`/`.pop()`/item assignment |
| `dict` | Yes | Key→value mapping, in-place `[key] = value` |
| `set` | Yes | Unordered, in-place `.add()`/`.remove()` |

Two operators make the mutable/immutable distinction concrete:

- `is` checks object identity (same object in memory) — `id(a) == id(b)`.
- `==` checks value equality (do they represent the same value).

`a = [1, 2]; b = a` makes `b` an alias for the same list object — `a is b` is `True`, and `a.append(3)` changes what `b` sees too. `a = [1, 2]; b = a.copy()` (or `list(a)`) makes an independent list — `a is b` is `False`.

## Sample code

Adapted from the Python tutorial's own worked example of the classic bug — a mutable default argument (Python docs, *Common Gotchas*/*Defining Functions*, accessed 2026-08-20):

```python
# BUG: the default list is created once, at function-definition time,
# not once per call — every call without an explicit `history` argument
# shares and mutates the *same* list object.
def log_event(event: str, history: list = []) -> list:
    history.append(event)
    return history

log_event("a")           # ['a']
log_event("b")           # ['a', 'b']  <- unexpected, leaked from the previous call

# FIX: default to None (immutable, safe to share), create a fresh list inside
def log_event(event: str, history: list | None = None) -> list:
    if history is None:
        history = []
    history.append(event)
    return history
```

This works because `None` is immutable — sharing the same `None` default across every call is harmless, since no call can ever mutate it. The fresh `[]` created inside the function body runs on every call, not once at definition time.

## How this shows up in the capstone

Every agent function signature in this stack takes default arguments — a shared mutable default here silently leaks state between unrelated calls (e.g. two different customers' tool-call logs bleeding into each other) in exactly the way M2's tool-enabled agent tools do.

## Production gotchas & best practices

- The mutable-default-argument bug is Python's most commonly cited gotcha precisely because it doesn't fail loudly — it accumulates state across calls silently, and shows up as "weird" behavior on the second or third call, not the first ([Python docs — Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values), accessed 2026-08-20).
- Current best practice (still the documented fix as of Python 3.13/3.14): default mutable arguments to `None`, then construct the real mutable object on the first line of the function body ([Python docs — Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values), accessed 2026-08-20).
- `is` vs `==`: use `is` only for identity checks that are meant to be identity checks — `is None`, `is True` — never for value comparison; `==` on two large equal-valued but distinct list/dict objects is `True` while `is` is `False`, and mixing the two up is a recurring source of confusing bugs.

## Course vs. production

Not applicable — this page is language fundamentals, not a course-vs-production tool comparison.

## Related

- **Prerequisite for** — [[lists-tuples-sets-dicts]], [[functions-args-kwargs]]

## Sources

**Lab sources**

None — this page has no matching lab or notebook; see task framing (01-python-refresher is lab/notebook-silent by design).

**Web sources**
- [Python 3 tutorial — More Control Flow Tools: Default Argument Values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values) — official documentation of the mutable-default-argument evaluation-once behavior, accessed 2026-08-20
- [Python 3 data model — Objects, values and types](https://docs.python.org/3/reference/datamodel.html) — identity vs. value, mutability defined at the object-model level, accessed 2026-08-20
