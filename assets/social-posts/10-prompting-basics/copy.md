--- LINKEDIN ---
Prompting is just a list of messages

Every LLM call is built from role-tagged messages, sent fresh every time. Three roles do almost all the work: system (standing instructions for the whole exchange — the cheapest lever to reshape behavior without touching code), user (what's being asked right now), and assistant (the model's own prior replies, replayed back as history).

Here's the part people miss: "memory" is an illusion your app maintains. A chatbot seems to remember what you said earlier because your code resends the entire message history, every call. Nothing about the model remembers a prior turn — a bug that drops history silently degrades every downstream reply, with no error to catch it.

The other basic axis: zero-shot gives the model an instruction and a task, no worked examples. Few-shot adds example input→output pairs first — "Shipping was fast, loved it." → positive / "Item arrived broken." → negative — then the real task, trading extra tokens for a clearer pattern to match.

A SessionStore — one message list per session_id — is what keeps concurrent users from cross-talking.

Full mechanics — the session code and the few-shot template — in the carousel.

Is your system prompt under version control, or a hotfix waiting to happen?

#AppliedAI #LLM #AIEngineering #PromptEngineering

--- INSTAGRAM ---
Prompting is just a list of messages 💬

system = standing instructions. user = the ask. assistant = replayed history.

"Memory" is an illusion your app maintains — the model remembers nothing between calls.

Zero-shot: no examples. Few-shot: a couple of input→output pairs first, then the real task.

Is your system prompt reviewable, or a hotfix waiting to happen?

#AppliedAI #LLM #AIEngineering #GenAI #PromptEngineering

--- VISUAL FORMAT ---
carousel — 6 slides
1. Title — "Prompting Is Just A List Of Messages"
2. Concept 1 — Three Roles Do Almost All The Work (code: messages.append(...))
3. Concept 2 — "Memory" Is An Illusion You Maintain
4. Concept 3 — Zero-Shot vs. Few-Shot
5. Concept 4 — One Session Per User (code: SessionStore)
6. Takeaway — closing question

--- SCHEDULE ---
Tue 9/8: IG 5pm · LinkedIn 11am
