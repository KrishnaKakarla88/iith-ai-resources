from litellm import completion
import os, json, time
from uuid import uuid4
from pydantic import BaseModel, ValidationError, Field
from dotenv import load_dotenv, find_dotenv

from models import Sentiment, IssueType, Urgency, SupportTicket

_ = load_dotenv(find_dotenv())  # read local .env file

EXTRACTION_PROMPT = """Extract support tickets data from the text below into JSON with exactly these fields:
issue_type (string), sentiment (string), urgency (string), order_id(str or null)

Allowed values:
- issue_type: {issue_types}
- sentiment: {sentiments}
- urgency: {urgencies}

Rules:
- Use only allowed enum values.
- Do not invent new values.
- Extract order_id exactly from text.
- Use null when order_id is unavailable.
- Return ONLY valid JSON.
- no markdown fences, no commentary

Text:
{text}"""

REPAIR_PROMPT = """The following JSON failed validation with error: {e}

Original text:
{text}

Previous JSON attempt:
{raw}

Return corrected JSON with EXACTLY these fields: issue_type (string), sentiment (string), urgency (string), order_id(str or null).
Allowed values:
- issue_type: {issue_types}
- sentiment: {sentiments}
- urgency: {urgencies}

Rules:
- Use only allowed enum values.
- Do not invent new values.
- Extract order_id exactly from text.
- Use null when order_id is unavailable.
- Return ONLY valid JSON.
- no markdown fences, no commentary"""

def extract_raw(
    systemPrompt: str,
    text: str,
    raw: str | None = None,
    error: str | None = None,
) -> str:
    prompt = systemPrompt.format(
        text=text,
        issue_types=", ".join(x.value for x in IssueType),
        sentiments=", ".join(x.value for x in Sentiment),
        urgencies=", ".join(x.value for x in Urgency),
        e=error,
        raw=raw
    )

    resp = completion(
        model=os.environ["GROQ_MODEL"],
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
        seed=42
    )
    return resp.choices[0].message.content

def validate_ticket(raw: str) -> tuple[SupportTicket | None, str | None]:
    # Parse raw as JSON, construct an SupportTicket, and return (SupportTicket, None) on success
    # or (None, str(e)) on failure ===
    try:
        data = json.loads(raw)
        ticket = SupportTicket(**data)
        return ticket, None
    except (json.JSONDecodeError, ValidationError) as e:
        return None, str(e)

def parse_ticket(text: str, max_retries: int = 2) -> tuple[SupportTicket | None, list[str]]:
    """Returns (parsed SupportTicket or None, list of attempt errors)."""
    errors = []
    raw = extract_raw(EXTRACTION_PROMPT, text)
    for attempt in range(max_retries + 1):
        try:
            # json.loads the raw string, validate/construct an SupportTicket, return (SupportTicket, errors)
            data = json.loads(raw)
            ticket = SupportTicket(**data)
            return ticket, errors

        except (json.JSONDecodeError, ValidationError) as e:
            # Record the error; return (None, errors) on last attempt; otherwise repair and retry
            errors.append(str(e))
            if attempt == max_retries:
                return None, errors
            raw = extract_raw(REPAIR_PROMPT, text, raw, str(e))
    return None, errors

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "shopsense" / "intake"
with open(DATA_DIR / "records.jsonl", 'r', encoding='utf-8') as f:
    tickets = [json.loads(line) for line in f]
print(f"Loaded {len(tickets)} tickets.")

# raw = extract_raw(EXTRACTION_PROMPT, tickets[0]["raw_text"])
# print(raw)

# ticket, error = validate_ticket(raw)
# print(ticket if ticket else error)

results = []
for record in tickets:
    ticket, errs = parse_ticket(record["raw_text"])
    results.append({"id": str(uuid4().hex), "ticket": ticket, "errors": errs})
    time.sleep(2)  # stay under Groq's free-tier tokens-per-minute limit

success = sum(1 for r in results if r["ticket"] is not None)
print(f"Parsed {success}/{len(results)} records successfully.")