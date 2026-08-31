--- LINKEDIN ---
Tool calling has the model decide which tool to call silently, inside its forward pass. ReAct makes that reasoning explicit — a fixed pattern before acting: Thought, Action, Observation, repeated, then a Final Answer. The visible Thought line lets the model change its mind mid-task, reacting to an unexpected observation instead of blindly continuing a plan made before any evidence came in.

Two mechanics here are load-bearing. First: litellm.completion(..., stop=["Observation:"]) on every call. Without it, the model can generate its own fake Observation: line and reason off invented results — a real production bug class. Second: the system prompt frames Observation content as untrusted data. A search result can contain adversarial text — "ignore previous instructions and..." — embedded in legitimate content. The model reasons about it, never obeys it.

Mechanically this is the exact same loop as structured tool calling — perceive, plan, act, observe, capped. The only difference is where the plan lives: a structured tool_calls field versus a regex-parsed line of text.

Have you shipped a ReAct loop that forgot the stop sequence?

#AppliedAI #LLM #AIEngineering #LangGraph

--- INSTAGRAM ---
Making the model's reasoning visible. 💭

Thought → Action → Observation → Final Answer.

stop=["Observation:"] is load-bearing — without it, the model hallucinates its own fake result.

Observation content is untrusted data. The model reasons about it, never obeys embedded instructions.

Full breakdown in the carousel.

Shipped a ReAct loop that forgot the stop sequence?

#AppliedAI #LLM #AIEngineering #GenAI #Developer

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Making The Model's Reasoning Visible"
2. The loop — thought, action, observation (diagram)
3. Load-bearing gotcha — without stop=["Observation:"], it hallucinates one (code)
4. Security discipline — observations are untrusted data
5. Sample code — regex-parsing the action line (code)
6. Takeaway — same loop as tool calling, different plan format (closing question)
