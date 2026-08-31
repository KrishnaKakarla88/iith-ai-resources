--- LINKEDIN ---
An LLM's training cutoff freezes its knowledge — it can't check today's weather or a row in your database. A tool fixes this by letting the model ask your application to do something and hand the result back. The critical thing: the model never executes anything. It produces a request — name and arguments. Your code decides whether to comply and runs it.

A tool has three parts the model sees: name (an unambiguous, verb-first identifier), parameters (a JSON Schema constraining argument shape), and description — the highest-leverage, most-neglected field. A vague description causes the wrong tool call, or the right tool at the wrong time.

The canonical safe-tool example is a calculator: never eval(expr) — arbitrary code execution. Parse with ast.parse and walk the tree, evaluating only a whitelisted operator set.

Watch for a model narrating a tool call it didn't make — "I checked the weather and it's 31°C" with no tool_calls entry. Always drive execution off the structured tool_calls field, never off prose.

When did a vague tool description cause a wrong-tool call for you?

#AppliedAI #LLM #AIEngineering #LangGraph

--- INSTAGRAM ---
The model never executes anything. 🛠️

It requests a call — name, arguments. Your code decides whether to run it.

Never eval(expr) for a calculator tool — parse with ast.parse and whitelist the operators instead.

description is the highest-leverage field: it decides WHEN the model reaches for a tool, not just how.

Full breakdown in the carousel.

When did a vague description cause a wrong-tool call?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "The Model Never Executes Anything"
2. Core mechanics — three parts the model sees
3. Safety first — never eval() a calculator tool (code)
4. Sample code — the bind-execute-feedback loop (code)
5. Gotcha — narrated isn't executed
6. Production practice — don't trust the model with exact numbers
7. Takeaway — the description is your prompt you forgot you wrote (closing question)
