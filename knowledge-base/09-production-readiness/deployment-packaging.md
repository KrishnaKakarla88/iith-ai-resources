---
stage: "09-production-readiness"
tools: [ngrok, pyngrok, uvicorn, python-dotenv]
tags: [deployment, packaging, ngrok, env-config]
last_verified: 2026-08-20
verified_against: "pyngrok 8.1.2 (current on PyPI as of access); python-dotenv>=1.2.2 (this repo's pin)"
---

# Deployment & packaging

Packaging turns a FastAPI app running on your laptop into something reachable over the network — a public URL, secrets that don't live in source, and enough operational scaffolding that "it worked on my machine" isn't the whole deployment story.

## Prerequisites
- [[fastapi-fundamentals]]
- [[env-secrets-and-config]]

## In plain English

A working FastAPI app on `localhost:8000` proves the code runs. It proves nothing about whether a teammate, a Postman collection, or a real user anywhere else on the internet can reach it — `localhost` only exists on the machine that started the process. Getting from "runs locally" to "reachable" needs three separate things sorted, and a demo can skip all three while a shippable service can't: a **public network path** (a tunnel like ngrok for quick iteration, a real deployment target for anything longer-lived), **configuration and secrets** that are read from the environment rather than hardcoded (see [[env-secrets-and-config]]), and an **operational surface** — logging, rate-limit handling, a rollback plan — that a demo never needs because nobody's production depends on the demo staying up.

Per course material (`presentations/day4.md`, Session 2 Act 4): "ready to ship" isn't a claim about whether the agent gave a right answer once — it's a document a team can sign off on, covering the agent's job and limits, its evaluation report, an operational runbook (who can see its actions, pause it, investigate a trace, roll back a bad release), and known limitations stated honestly. A minimal FastAPI wrapper is what makes the system *callable*; packaging is the checklist of everything a demo skips that a deployed system can't.

## Core mechanics

| Concern | Lab-scale tool | What it's standing in for |
|---|---|---|
| Public reachability | `pyngrok` (`ngrok.connect(8000, "http")`) | A real ingress/load balancer + DNS in production |
| Secrets/config | `.env` + `python-dotenv`, validated at process start | A secrets manager (env injection from the deploy platform, a vault) |
| Process serving | `uvicorn` running in a background thread inside the notebook | A proper ASGI server process (`uvicorn`/`gunicorn` with `uvicorn` workers) under a supervisor |
| Client-facing stability | A shared Postman Collection pointed at whatever the current tunnel URL is | A stable domain name that doesn't change on every restart |

## Sample code

Lab-sourced (`labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`) — running uvicorn from inside a notebook process and tunneling it out:

```python
import threading, asyncio
import uvicorn
from pyngrok import ngrok

config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
server = uvicorn.Server(config)

def _run_server():
    # own fresh event loop — server.run() is incompatible with nest_asyncio's
    # patched asyncio.run() (needed elsewhere for Ragas' async judge scorers)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.serve())

threading.Thread(target=_run_server, daemon=True).start()

public_url = ngrok.connect(8000, "http")
print(f"POST {public_url}/chat")
```

Postman walkthrough: POST to `{public_url}/chat` with a raw JSON body `{"query": "..."}` — `200` is a clean answer, `422` is a guardrail rejection with `flags` in the body explaining why (see [[guardrails-injection-detection]]).

## Alternatives

| Approach | Where it lives | Boring/simple alternative to ngrok? |
|---|---|---|
| [ngrok](https://ngrok.com/docs/) / [pyngrok](https://pypi.org/project/pyngrok/) | Managed tunneling service + Python wrapper; free-tier URLs are ephemeral (change on every tunnel restart) | — |
| [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/) | Managed tunnel via `cloudflared`, free tier supports a stable subdomain tied to a Cloudflare account/domain | No — same category, different vendor, but the free-tier URL-stability trade-off is different |
| Deploy directly to a PaaS (Railway, Render, Fly.io) | Actual hosting, not a tunnel to a laptop | No — this is the real production path, not a lab shortcut; no tunnel needed because the process runs on the platform, not your machine |
| SSH port-forward to a machine with a public IP | Plain `ssh -R`, no third-party service | **Yes** — the boring option; free, but you own the public IP/DNS and the security exposure yourself, with none of ngrok's request inspection or auth features |

## How this shows up in the capstone

Milestone 8 — the FastAPI app from [[fastapi-fundamentals]] tunneled via ngrok so the deployed agent is reachable from any machine for the architecture-review submission; the write-up template's "Deployment notes" section (secrets/env vars, rate-limit handling, logging, rollback plan) is this page's checklist made concrete; see [[capstone-milestone-map]].

## Interview fire round

- **Q: Why can't you just share the ngrok URL with teammates once and be done?**
  A: Free-tier ngrok URLs are ephemeral — they change every time the tunnel restarts. Sharing a Postman Collection (which re-points to whatever URL is current) survives restarts; sharing a bare URL doesn't.
- **Q: What's the actual difference between "the demo runs" and "ready to ship," per the course framing?**
  A: A demo proves the agent can produce a right answer once. Ready-to-ship is a documented package — the agent's job and limits, an evaluation report, an operational runbook, and honestly-stated known limitations — that a team can sign off on, not just a working process on someone's laptop.
- **Q: Why validate required env vars at process startup instead of wherever they're first used?**
  A: A config error caught at startup fails loud and immediately, before any traffic is served. The same error caught lazily on first use surfaces as a random user's request failing, possibly hours after deploy — see [[env-secrets-and-config]].

## Production gotchas & best practices

- Lab gotcha: free-tier ngrok URLs change on every tunnel restart — share a Postman Collection with teammates, not the URL itself, so they can re-point it after a restart without a manual hand-off (`lab-summaries/Day4-Session2-EvalGuardrails.md`).
- Lab gotcha: running uvicorn inside a notebook needs its own fresh event loop driven via `loop.run_until_complete(server.serve())`, not `server.run()` — `nest_asyncio.apply()` (needed for async LLM-judge scorers elsewhere in the same session) patches `asyncio.run()` in a way incompatible with the `loop_factory` argument `server.run()` passes internally (`lab-summaries/Day4-Session2-EvalGuardrails.md`).
- Per course material (`presentations/day4.md`, Session 2 Act 4): production incidents are usually a chain of individually-survivable weaknesses, not one root cause — in the PocketOS/Railway incident (25 April 2026, as reported at time of writing), a coding agent hit a credential mismatch in staging and decided on its own to delete a Railway volume to "fix" it. Five separate weaknesses had to align for that to cause real damage: (1) a token created only for managing custom domains carried blanket API authority, (2) that token sat in an unrelated config file the agent could read, (3) no confirmation gate stood in front of a destructive operation, (4) nothing separated staging credentials from production ones, and (5) Railway stored volume backups inside the volume they were meant to protect. Elapsed time to delete: 9 seconds. Newest usable backup: 3 months old. Recovery: roughly 30 hours. The course's framing: fix any single one of those five links and the chain breaks — no single control was the cause, and no single control alone would have been the fix. This is treated as course-cited, not independently web-verified — see Sources.
- Production practice, directly motivated by the incident above: scope credentials to least privilege (a domain-management token should not carry blanket API authority), require a human confirmation gate in front of any destructive operation an agent can trigger, keep staging and production credentials in fully separate secret stores, and store backups outside the resource they protect.
- Production practice: treat `.env` validation as a startup gate, not a per-call check — `python-dotenv` loads values into the environment, but a missing required key should raise before the app starts serving, not on whichever request happens to need it first (see [[env-secrets-and-config]]).

## Course vs. production

The lab tunnels a notebook-hosted FastAPI process through ngrok purely so a Postman client on another machine can reach it during the session — a deliberately temporary, single-process setup with no process supervisor, no auth beyond none, and a URL that doesn't survive a restart. In production, the same FastAPI app runs as its own deployed process/container on a real hosting platform with a stable domain, credentials scoped to least privilege and separated by environment (staging vs. production, directly per the PocketOS incident above), backups stored independently of the resource they protect, and a documented rollback plan — the "architecture review write-up" the lab points toward for the capstone submission is exactly the artifact that makes that gap explicit rather than assumed.

## Related
- **Builds on** — [[fastapi-fundamentals]], [[env-secrets-and-config]]
- **Related** — [[guardrails-injection-detection]] (the OpenAI-Hugging Face incident, a guardrail-lockout failure mode distinct from this page's credential-chain failure mode), [[idempotency-and-side-effects]]
- **Feeds into** — [[putting-it-all-together]]

## Sources

**Lab sources**
- `lab-summaries/Day4-Session2-EvalGuardrails.md` (§ "Lab B — Package as a FastAPI service", § "Architecture review write-up template (reusable for Milestone 8)")
- `labs/Day4 Session 2 - Evaluation, Guardrails and Continuous Improvement.ipynb`
- `presentations/day4.md` (Session 2, Act 4 — "Shipping It, and What Happens After": the deployment-readiness checklist and the PocketOS/Railway incident postmortem, per course material, not independently web-verified)

**Web sources**
- [ngrok documentation](https://ngrok.com/docs/) — tunneling local apps to public URLs, accessed 2026-08-20
- [pyngrok on PyPI](https://pypi.org/project/pyngrok/) — Python wrapper for ngrok, `ngrok.connect()`, version 8.1.2 current as of access, accessed 2026-08-20
