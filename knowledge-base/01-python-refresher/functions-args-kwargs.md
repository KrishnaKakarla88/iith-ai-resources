---
stage: "01-python-refresher"
tools: []
tags: [primer, python, functions]
last_verified: 2026-08-20
verified_against: "Python 3.13 (this repo's pin: requires-python >=3.13)"
---

# Functions, args, kwargs

Positional and keyword arguments, `*args`/`**kwargs`, and default parameters — the vocabulary needed to read any tool or agent function signature in this stack without guessing.

## Prerequisites
- [[python-data-types-and-mutability]]
- [[lists-tuples-sets-dicts]]

## In plain English

A function call passes arguments to a function's parameters, and Python gives you two ways to do that: by position (`f(1, 2)` — first value goes to the first parameter, second to the second) or by keyword (`f(a=1, b=2)` — explicitly named, order doesn't matter). Keyword arguments exist because position alone gets unreadable and error-prone once a function has more than two or three parameters — `create_agent(model, tools, None, True, False)` tells you nothing about what `None`/`True`/`False` mean at the call site; `create_agent(model=llm, tools=TOOLS, memory=None, verbose=True, streaming=False)` does.

Default parameter values (`def f(x, y=10)`) let a caller omit an argument and get a sensible fallback — this is what makes a function usable with a short call in the common case and a fully-specified call in the uncommon one.

`*args` and `**kwargs` exist for a different reason: writing a function that accepts an *arbitrary* number of arguments it doesn't know the shape of ahead of time — a logging wrapper, a decorator, a dispatcher that forwards whatever it received to another function.

## Core mechanics

| Syntax | Meaning | In the call site |
|---|---|---|
| `def f(a, b)` | positional-or-keyword parameters | `f(1, 2)` or `f(a=1, b=2)` |
| `def f(a, b=5)` | `b` optional, defaults to `5` | `f(1)` or `f(1, b=9)` |
| `def f(*args)` | collects extra positional args into a tuple named `args` | `f(1, 2, 3)` → `args == (1, 2, 3)` |
| `def f(**kwargs)` | collects extra keyword args into a dict named `kwargs` | `f(x=1, y=2)` → `kwargs == {"x": 1, "y": 2}` |
| `def f(a, *, b)` | everything after the bare `*` is keyword-only | `f(1, b=2)` works, `f(1, 2)` raises `TypeError` |
| `f(*a_list)` | unpacks a list/tuple into positional args at a **call** site | `f(*[1, 2])` same as `f(1, 2)` |
| `f(**a_dict)` | unpacks a dict into keyword args at a **call** site | `f(**{"a": 1})` same as `f(a=1)` |

Parameter order in a definition is fixed: positional-only, then positional-or-keyword, then `*args`, then keyword-only, then `**kwargs`. `*args`/`**kwargs` are only names by convention — `*items`/`**fields` work identically — but `args`/`kwargs` are the near-universal convention and worth reading as fixed vocabulary.

## Sample code

A decorator is the canonical reason to reach for both `*args` and `**kwargs` together — it has to forward *any* call shape through to the wrapped function without knowing what that shape is ahead of time:

```python
def log_call(fn):
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__} with {args=} {kwargs=}")
        return fn(*args, **kwargs)   # forwards whatever was received, unchanged
    return wrapper

@log_call
def get_weather(city: str, units: str = "metric") -> dict:
    ...

get_weather("Chennai")                  # args=('Chennai',) kwargs={}
get_weather(city="Chennai", units="imperial")  # args=() kwargs={'city': 'Chennai', 'units': 'imperial'}
```

Without `*args, **kwargs` in `wrapper`, `log_call` would only work on functions matching one exact fixed signature — the whole point of a general-purpose decorator is that it doesn't need to know the signature in advance.

## How this shows up in the capstone

Every tool function this stack wraps in retry/circuit-breaker/tracing decorators (see [[decorators-and-wrappers]]) is forwarded through exactly this `*args, **kwargs` pattern — the wrapper never needs to know a tool's actual parameter list.

## Production gotchas & best practices

- Keyword-only parameters (`def f(a, *, b)`) are the current recommended way to force callers to name a parameter explicitly when its meaning isn't obvious from a bare value at the call site (e.g. a boolean flag) — the language reference documents `*` as marking "the following are keyword-only" ([Python 3 tutorial — Special parameters](https://docs.python.org/3/tutorial/controlflow.html#special-parameters), accessed 2026-08-20).
- A parameter's default value is bound once, at function-definition time, not per call — the mutable-default-argument trap covered on [[python-data-types-and-mutability]] is really a consequence of this rule applied to `*args`/`**kwargs`-adjacent function signatures too.

## Course vs. production

Not applicable — this page is language fundamentals, not a course-vs-production tool comparison.

## Related

- **Builds on** — [[lists-tuples-sets-dicts]]
- **Prerequisite for** — [[type-hints-basics]], [[decorators-and-wrappers]]

## Sources

**Lab sources**

None — this page has no matching lab or notebook; see task framing (01-python-refresher is lab/notebook-silent by design).

**Web sources**
- [Python 3 tutorial — More Control Flow Tools: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) — args/kwargs, default values, accessed 2026-08-20
- [Python 3 tutorial — Special parameters](https://docs.python.org/3/tutorial/controlflow.html#special-parameters) — positional-only/keyword-only parameter syntax, accessed 2026-08-20
