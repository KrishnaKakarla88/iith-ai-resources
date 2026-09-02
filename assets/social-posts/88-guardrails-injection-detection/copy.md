--- LINKEDIN ---
An eval score tells you whether an agent's answer is right. A guardrail tells you whether it's safe to return at all — a different question, checked separately, because the two can diverge in both directions: a correct, well-written answer can still leak data it shouldn't, and a guardrail can block a perfectly good answer for being phrased suspiciously.

class AgentResponse(BaseModel):
    route: Literal["tool", "retrieval", "direct"]
    final_answer: str = Field(min_length=1, max_length=2000)

    @field_validator("final_answer")
    def reject_placeholder(cls, v):
        if v.strip().lower() in _PLACEHOLDER_ANSWERS:
            raise ValueError("placeholder, not a real response")

A hallucinated route or a placeholder answer both pass a naive schema check without this.

A guardrail fails in two directions, and only one ever generates a support ticket. False approval: something bad gets through, a user complains, you find out. False rejection: a good answer gets blocked — nobody files a ticket for the answer they never received. It just quietly erodes trust.

A worked example on tuning: threshold 0.5 caught 18/20 bad cases but blocked 41/180 good ones. Threshold 0.9 caught 11/20 bad cases but blocked only 3/180. Neither is "correct" — an internal tool can lean permissive, medical or financial advice should lean strict. That's a business decision, not a library default.

Scan retrieved content for injection too, not just the user's query — anything the agent treats as trusted context is a vector for an attacker who got content into the corpus.

The real-world stakes of getting this wrong in both directions: a documented 2026 incident where hosted safety filters blocked incident responders trying to forensically analyze a live exploit, because the filter couldn't distinguish a forensic prompt full of real exploit payloads from an actual attack. They ran the analysis on a self-hosted model instead — vetted before the incident, not shopped for during one.

Tune every threshold against the same golden set used for eval, scoring false-approval and false-rejection rates separately.

Do you know your guardrail's false-rejection rate, or only whether it blocks the obvious attacks?

#AppliedAI #AIEngineering #LLM #RAG

--- INSTAGRAM ---
"Right" and "safe to return" are different questions. 🛡️

A guardrail fails in two directions — only one ever generates a support ticket. False rejections quietly erode trust with zero complaints.

Threshold 0.5: catches 18/20 attacks, blocks 41/180 good answers. Threshold 0.9: catches 11/20, blocks only 3/180. Neither is "correct" — it's a business call.

Scan retrieved docs for injection too, not just the query.

Full breakdown in the carousel.

#AppliedAI #AIEngineering #LLM #RAG #GenAI

--- VISUAL FORMAT ---
carousel — 7 slides
1. Title — "\"Right\" And \"Safe To Return\" Are Different Questions"
2. Sample code — a hallucinated route passes a naive schema check (code)
3. Two failure directions — only one ever generates a support ticket
4. The actual tuning data — neither threshold is "correct"
5. Scan retrieved content too — not just the user's query
6. The real-world stakes — the same filter that stops an attacker can stop the clean-up crew
7. Takeaway — tune every threshold against the same golden set used for eval (closing question)
