--- LINKEDIN ---
print(x), x == y, len(x) — none of these have special-cased logic for every type in Python's interpreter. They all call a dunder method on x instead.

Dunder ("double underscore") methods are reserved names Python calls automatically in response to a language-level operation, not something you call directly. print(x) calls x.__repr__() (or __str__ if defined). x == y calls x.__eq__(y). len(x) calls x.__len__(). A class with none of these defined still works, but inherits defaults from object: printing shows <MyClass object at 0x...>, and == falls back to identity comparison (is).

Defining __init__, __repr__, and __eq__ on a plain class is what turns it into something that behaves like real data — printable, comparable by value, not just by memory address.

The gotcha worth remembering: overriding __eq__ to compare by value silently makes instances unhashable, unless __hash__ is also defined too. Python does this deliberately — two objects that compare equal but hash differently would break dict/set lookups.

Which dunder have you had to write by hand recently?

#AppliedAI #Python #LLM #AIEngineering

--- INSTAGRAM ---
Python never has special-cased logic for print(x), x == y, len(x) — it calls a dunder method on x instead. 🔧

__repr__ controls what print(x) shows.
__eq__ controls what x == y checks.
No dunders defined? You get <MyClass object at 0x...> and identity-only comparison.

The gotcha: override __eq__ without __hash__ and your objects silently become unhashable. Full mechanism in the carousel.

Which dunder have you written by hand?

#AppliedAI #Python #LLM #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Dunder Methods"
2. Concept — Python calls these for you (print/len/==)
3. The Big Three — __init__, __repr__, __eq__
4. Sample code — a Ticket class
5. Gotcha — __eq__ without __hash__ (code: re-inherit line)
6. Takeaway + closing question
