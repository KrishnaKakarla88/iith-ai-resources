---
stage: "01-python-refresher"
tools: []
tags: [primer, python, dunder-methods, oop]
last_verified: 2026-08-21
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13)"
---

# Dunder methods (magic methods)

The double-underscore methods (`__init__`, `__repr__`, `__eq__`, `__len__`, ...) that let a plain class plug into Python's own syntax — `print(x)`, `x == y`, `len(x)`, `for item in x` — instead of needing bespoke method calls for every operation.

## Prerequisites
- [[python-data-types-and-mutability]]
- [[lists-tuples-sets-dicts]]

## In plain English

"Dunder" is short for **d**ouble **under**score — `__init__` is pronounced "dunder init." These are methods with a fixed, reserved name that Python's interpreter calls automatically in response to a language-level operation, rather than a name you call directly. When you write `len(my_list)`, Python doesn't have special-cased logic for every type that could appear there — it calls `my_list.__len__()` and returns whatever that returns. `x == y` calls `x.__eq__(y)`. `for item in x:` repeatedly calls `x.__next__()` (after getting an iterator via `x.__iter__()`). `MyClass(a, b)` calls `MyClass.__init__(self, a, b)` after the object itself is allocated.

The point of this design: any class you write can opt into that same syntax by defining the matching dunder, instead of the language needing built-in special cases for user-defined types. A class with no dunders defined still gets default behavior inherited from `object` — printing it shows `<MyClass object at 0x...>`, and `==` falls back to identity comparison (`is`) — which is usually not what you want once a class represents actual data.

## Core mechanics

| Dunder | Called by | Default (inherited from `object`) if not defined |
|---|---|---|
| `__init__(self, ...)` | `MyClass(...)` | no-op — just sets whatever `__new__` already allocated |
| `__repr__(self)` | `repr(x)`, the interactive shell, inside `[x]`/dict display | `<MyClass object at 0x...>` |
| `__str__(self)` | `str(x)`, `print(x)`, `f"{x}"` | falls back to `__repr__` if not defined |
| `__eq__(self, other)` | `x == y` | falls back to `is` (identity) |
| `__hash__(self)` | `hash(x)`, using `x` as a dict key / set member | identity-based hash — **but** defining `__eq__` without `__hash__` sets this to `None`, making the object unhashable |
| `__len__(self)` | `len(x)` | not defined — raises `TypeError` |
| `__iter__(self)` | `for item in x:`, `list(x)` | not defined — raises `TypeError` |
| `__getitem__(self, key)` | `x[key]` | not defined — raises `TypeError` |
| `__call__(self, ...)` | `x(...)` — makes an *instance* callable like a function | not defined — raises `TypeError` |
| `__enter__(self)` / `__exit__(self, exc_type, exc_val, tb)` | `with x as ...:` | not defined — raises `TypeError` (not a context manager) |

`__eq__`/`__hash__` are worth double-checking together: overriding `__eq__` to compare by value (the usual reason to override it) silently makes instances unhashable unless `__hash__` is also defined — Python does this deliberately, because two objects that compare equal but hash differently would break dict/set lookups.

## Sample code

A minimal value-object class showing the three dunders every data-carrying class typically wants — `__init__`, `__repr__`, `__eq__` — and what breaks without them:

```python
class Ticket:
    def __init__(self, ticket_id: str, status: str):
        self.ticket_id = ticket_id
        self.status = status

    def __repr__(self) -> str:
        return f"Ticket(ticket_id={self.ticket_id!r}, status={self.status!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Ticket):
            return NotImplemented
        return self.ticket_id == other.ticket_id and self.status == other.status

t1 = Ticket("T-100", "open")
t2 = Ticket("T-100", "open")

print(t1)          # Ticket(ticket_id='T-100', status='open') — thanks to __repr__
t1 == t2            # True — field-by-field, thanks to __eq__
t1 is t2             # False — still two distinct objects in memory
```

Without `__repr__`, `print(t1)` would show `<__main__.Ticket object at 0x7f...>` — useless in a test failure message or a log line. Without `__eq__`, `t1 == t2` would fall back to `is` and return `False`, because they're two separate objects even though every field matches — the exact check a golden-eval test comparing "actual result == expected result" depends on.

## How this shows up in the capstone

A golden-eval test that asserts `actual_response == expected_response` on a structured object only works if that object's class defines `__eq__` by value — this is precisely what [[pydantic-basics]]'s `BaseModel` gives every model for free, and is why comparing two parsed Pydantic objects with `==` "just works" without writing `__eq__` yourself. Resource-holding objects in this stack (an HTTP client, a Qdrant connection) are also commonly used as context managers (`with client: ...`), which is `__enter__`/`__exit__` under the hood — the same mechanism guaranteeing cleanup runs even if the block raises.

## Production gotchas & best practices

- Overriding `__eq__` without `__hash__` doesn't leave the old identity-based hash in place — Python sets `__hash__` to `None` on any class that defines `__eq__` but not `__hash__`, so instances silently become unusable as dict keys or set members until `__hash__` is defined too (or explicitly re-inherited: `__hash__ = object.__hash__`) ([Python data model — object.\_\_hash\_\_](https://docs.python.org/3/reference/datamodel.html#object.__hash__), accessed 2026-08-21).
- `__repr__` is meant for developers (unambiguous, ideally something that could recreate the object) and `__str__` is meant for end users (readable); defining only `__repr__` is the common shortcut, since `str()`/`print()` fall back to it when `__str__` is absent — but the reverse isn't true, so a class that needs a friendly `str()` distinct from a debug `repr()` must define both explicitly ([Python data model — object.\_\_repr\_\_](https://docs.python.org/3/reference/datamodel.html#object.__repr__), accessed 2026-08-21).
- Returning `NotImplemented` (not `False`) from `__eq__` when `other` is an incompatible type lets Python fall back to trying `other.__eq__(self)` before giving up — returning a bare `False` forecloses that fallback and can produce wrong answers when comparing against an unrelated type.

## Course vs. production

Hand-writing `__init__`/`__repr__`/`__eq__` (as above) is worth doing once to see the mechanism, but production code rarely writes them by hand for plain data-holding classes: the standard library's `@dataclass` decorator generates `__init__`, `__repr__`, and `__eq__` from type-annotated fields automatically, and [[pydantic-basics]]'s `BaseModel` goes further — generating the same dunders *and* runtime validation. This stack uses `BaseModel` specifically because validation is needed on top of the dunders; a plain `@dataclass` would give the dunders without the validation.

## Related

- **Builds on** — [[lists-tuples-sets-dicts]]
- **Prerequisite for** — [[pydantic-basics]]

## Sources

**Lab sources**

None — this page has no matching lab or notebook; see task framing (01-python-refresher is lab/notebook-silent by design).

**Web sources**
- [Python 3 data model — Basic customization](https://docs.python.org/3/reference/datamodel.html#basic-customization) — `__init__`, `__repr__`, `__str__`, `__eq__`, `__hash__` reference semantics, accessed 2026-08-21
- [Python 3 data model — Emulating container types](https://docs.python.org/3/reference/datamodel.html#emulating-container-types) — `__len__`, `__getitem__`, `__iter__`, accessed 2026-08-21
- [Real Python — Python's Magic Methods](https://realpython.com/python-magic-methods/) — worked examples across the common dunder groups, accessed 2026-08-21
</content>
