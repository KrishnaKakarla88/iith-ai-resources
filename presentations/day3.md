THE FOUR-DAY ARC
Four Questions, One Progression
Each day answers one question — and its answer becomes the next day's starting point.
DAY 1 · 01 AUGUST 2026
1
Engineering Reliable Single-Agent Systems
How does an LLM become software?
DAY 2 · 02 AUGUST 2026
2
Knowledge, Memory and Retrieval
How does software become intelligent?
DAY 3 · 08 AUGUST 2026 · TODAY
3
Building Multi-Agent Systems
How does intelligence become autonomous?
DAY 4 · 09 AUGUST 2026
4
Production AI Engineering
How does autonomy become production-ready?

User Request
DAY 3 · 08 AUGUST 2026
Context Engineering
Building Multi-Agent Systems Instruction Engineering
Memory Engineering
Knowledge Engineering
“How does intelligence become autonomous?”
Reasoning Engine
Planning Engine
Tools
Agent Runtime
Evaluation
Observability
Production

SESSION · RECAP
What is Agent Harness?
Source: The Anatomy of an Agent Harness

SESSION · RECAP
What is Harness Engineering?
Source: Context, Memory, and Harness Engineering

SESSION · RECAP
LLM based Solutions – Architectural Progression
Source: The Agent Loop -How AI Goes From Answering Questions to Doing Things

Day 3 · 08 August 2026
SESSION 1
Agent Architectures & LangGraph Fundamentals
“Teach the AI to Plan”
10:00 – 11:30
Milestone 5 · Orchestrated LangGraph workflow with checkpointing

Day 3 · Session 1
By the end of this session, three ideas will matter more than any
other
|     | 1   |     | 2   |     | 3   |
| --- | --- | --- | --- | --- | --- |
A bare loop cannot be seen into,  State that survives a crash, and a  Knowing when NOT to add
stopped, or resumed — which is  human who can step in and back  machinery — a chain, a single agent
exactly why graph engineering took  out, are the two reliability patterns  — is the same skill as knowing how
| over. |     | underneath every agent  |     | to add it. |     |
| ----- | --- | ----------------------- | --- | ---------- | --- |
architecture.

SESSION 1 · AT A GLANCE
What is Loop Engineering?
designing automated, iterative AI workflows where systems self-prompt, act, use tools, and verify results until a goal is met.
…shifts human effort from single-shot prompting to orchestrating autonomous feedback loops
✓ Act & Observe: Agents execute code or API
calls, then evaluate outputs against explicit
testable criteria.
✓ Verification Layers: Separate grader systems
or sub-agents review work and feed
corrections back into the cycle.
✓ Event-Driven Triggers: Systems run
continuously via cron schedules, webhooks,
or git commits rather than manual prompts.
Source: The Anatomy of an Agent Harness

SESSION 1 · AT A GLANCE
A popular loop pattern behind deep agents – The Ralph Loop
Self-diagnosing, self-correcting agent pattern –
…trades high token usage for continuous, autonomous execution
Source: The Ralph Loop -A Practical Pattern for Reliable AI Agents (and Why “Done” Is Not the End)

SESSION 1 · AT A GLANCE
Evolution of AI: From Prompts to Loop Engineering
Source: From Prompts to Loops

SESSION 1 · SEE IT WORKING
Fixing a Failed Expense Claim
Employee submits: “Reimburse ₹3,850 for this client visit.”
The agent cannot simply approve it because a receipt is missing.
1. Read claim + policy
→ Travel is eligible, but receipt is required above ₹2,000.
2. Check evidence
→ Receipt attachment: missing.
3. Act
→ Ask employee to upload the receipt.
→ Claim stays “Pending”; no money is released.
4. Re-check after upload
→ Receipt total = ₹3,850
→ Date and merchant match the claim.
5. Verify success criteria
→ Amount within policy ✓
→ Required evidence present ✓
→ No duplicate reimbursement ✓
6. Complete—or stop safely
→ Approve and send to Finance
→ If evidence still conflicts, escalate to a human reviewer
Loop Engineering is not “keep asking the model to try again.” It is designing a repeatable cycle:
inspect → act → verify against evidence → correct or escalate → stop.

Day 3 · Session 1 · Agent Architectures: From Loop to Graph
ACT 1
From Loop to Graph
What a bare loop cannot do · chain, graph, harness, framework · why graphs, why now

ACT 1 · QUESTION 1
Day 1’s agent was a while-loop. What breaks when it runs
for three hours instead of three turns?

ACT 1 · QUESTION 1 — THE RATIONALE
What Are the Limits of a Bare Loop?
You cannot see inside it It does not know when to stop A crash loses everything
One long trace of tool calls with no named Termination depends on the model deciding There is no saved position to resume from,
stages —debugging means reading the it is finished, which is not a guarantee you so a failure at minute forty means starting at
whole transcript can hold anyone to minute zero
Source: Yao et al., ReAct (arXiv:2210.03629); Cemri et al., MAST (arXiv:2503.13657)

ACT 1 · QUESTION 1 — SEE IT WORKING
The Same Agent, Three Turns vs. Three Hours
Day 1’s loop — fine at this size
while not done:
thought = model(messages)
result = run_tool(thought.action)
messages.append(result)
Now run it for three hours
Minute 04 tool call - 12 fails, retried, kept going
Minute 37 the model quietly re-reads a doc it already summarised
Minute 52 process dies. messages was in RAM. Everything is gone.
Minute 53 you restart from turn 1 — and pay for all of it again
Nothing here is a model failure. Every one of them is a missing stage boundary, a missing cap, or a missing save point.

ACT 1 · QUESTION 1 — THE ANSWER
A Loop Is an Engine, Not a Vehicle
| Opaque | Unbounded | Not resumable |
| ------ | --------- | ------------- |
No named stages to inspect, log or trace Stops when the model says so, not when you  A crash at step nine restarts you at step one
say so

ACT 1 · QUESTION 1 — REMEMBER IT THIS WAY
“
A car with an accelerator but no odometer, no brake and no reverse. Fine around
the block. Not fine on a highway.
A loop is a fine engine and a terrible vehicle —you cannot see it, stop it, or resume it.

★ WHAT'S NEW · 2026
ACT 1 · QUESTION 2
What's the difference between a graph, a harness, and a
framework?

ACT 1 · QUESTION 2 — THE RATIONALE
Chain, Graph, Harness, Framework — Side by Side

ACT 1 · QUESTION 2 — THE RATIONALE
Chain, Graph, Harness, Framework — Deep Dive

ACT 1 · QUESTION 2 — THE RATIONALE
What Is the Agent-Tooling Spectrum?
| Raw LangGraph | Deep Agents | Claude Agent SDK |
| ------------- | ----------- | ---------------- |
Maximum control —you build the state  A batteries-included harness on top of  Anthropic's fully opinionated equivalent —
machine, nodes, and edges yourself LangGraph: planning, subagents, virtual  paired here to keep the comparison vendor-
|     | filesystem, provided | neutral |
| --- | -------------------- | ------- |
Source: LangGraph documentation
Source: Deep Agents (LangChain) documentation
Source: Claude Agent SDK documentation

ACT 1 · QUESTION 2 — SEE IT WORKING
A Flight-Rebooking Agent
User asks: “My flight was cancelled. Rebook me to Hyderabad tomorrow morning.”
1. The Graph decides the path Read booking
The graph defines what happens next—including branches, joins, and loops.
→ Search available flights
→ Check policy
2. The Harness makes that path safe and dependable
↓
Around the same flow, the harness adds:
Seats available? ── No → Suggest alternatives
✓ Validate the booking ID before calling airline systems
↓ Yes
✓ Retry safely if the airline API times out
Confirm choice → Rebook
✓ Ask for approval before charging above the allowed fare difference
✓ Stop after a bounded number of search attempts
✓ Record the tools called, cost, latency, and final outcome
The harness does not decide the business flow. It makes the flow reliable,
observable, and safe to run in production.
3. The Framework gives you the building blocks
A framework provides the software primitives to implement it:
• State and routing for the graph
• Tool/API integrations for airline systems
• Memory and persistence for the booking session
• Runtime, tracing, evaluation, and deployment integrations
Graph = the route the agent takes.
A framework can include graph support and harness features—but it is the Harness = the engineering systems around that route.
toolkit, not the workflow itself. Framework = the toolkit used to build and run both..

ACT 1 · QUESTION 2 — THE ANSWER
★ WHAT'S NEW · 2026
How Much Harness Do You Want Built for You?
| Raw LangGraph | Deep Agents | Claude Agent SDK |
| ------------- | ----------- | ---------------- |
You build everything —maximum control Planning + subagents + virtual filesystem,  Anthropic's fully opinionated equivalent —
|     | batteries-included | paired for vendor neutrality |
| --- | ------------------ | ---------------------------- |

ACT 1 · QUESTION 2 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
Building a car from raw parts, buying a kit car, or buying a finished car — all get
you driving.
Neither end of the spectrum is 'better' — it's a control-vs-convenience decision for your own project.

ACT 1 · QUESTION 3
Loops and graphs are both decades old. Why is everyone
suddenly rebuilding on graphs now?

ACT 1 · QUESTION 3 — THE RATIONALE
Why Graph Engineering, and Why Now?
| Runs got long | Compute moved to inference | Agents became teams |     |
| ------------- | -------------------------- | ------------------- | --- |
Three-turn chats became three-hour jobs,  Spending more compute at run time made  A multi-agent system is a graph whose nodes
and long jobs need durable execution, not  branching, retrying and parallel exploration  are agents —the same primitive, one level
| best-effort loops | worth orchestrating |     | up  |
| ----------------- | ------------------- | --- | --- |
Source: LangGraph durable execution documentation; 2026 practitioner writing on inference-time scaling

ACT 1 · QUESTION 3 — THE RATIONALE
Loops vs Graphs?
Source: The Anatomy of an Agent Harness

ACT 1 · QUESTION 3 — SEE IT WORKING
What Changed Between 2023 and Now
2023 — the loop was enough
Ask a question, call two or three tools, answer in under a minute.
2026 — the job outgrew the loop
Runs measured in hours, not seconds -> needs to survive a restart
Branching work (three sources in parallel) -> needs explicit fan-out
Spend more compute to get a better answer -> needs retry and re-plan paths
A human must approve step 6 of 9 -> needs a defined pause point
And the hinge for this afternoon
A multi-agent system is just a graph whose nodes happen to be agents.
Every one of those four needs is a graph feature. None of them is a model capability.

ACT 1 · QUESTION 3 — THE ANSWER
Graphs Won Because the Jobs Got Longer
| Durable execution | Inference-time compute | Agents as nodes |
| ----------------- | ---------------------- | --------------- |
Long jobs need to survive restarts, not just  Branching and parallelism became worth the  The same graph primitive scales up to whole
| finish fast | orchestration | agent teams |
| ----------- | ------------- | ----------- |

ACT 1 · QUESTION 3 — REMEMBER IT THIS WAY
“
Nobody needed traffic lights until there were enough cars to crash into each other.
Graphs got popular when agent runs got long enough, expensive enough, and parallel enough to need them.

Day 3 · Session 1
QUICK CHECK — NO PEEKING
Before we move past From Loop to Graph:
Name two things a bare while-loop cannot do that a graph can.
1
What is the difference between a harness and a framework?
2

DAY 3 · SESSION 1
ACT 1 · DEEP DIVE
Deciding If You Need More Than One Agent
The single-versus-multi decision · state that survives a crash
START HERE — 3 THINGS
1 Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (MAST)
arxiv.org/abs/2503.13657· NeurIPS 2025
The empirical answer to this act’s question.
2 Anthropic — Building Effective Agents
anthropic.com/engineering/building-effective-agents
"Find the simplest solution possible", and the observation that for many applications a single LLM call plus retrieval and good examples is…
3 Lanham — Multi-Agent in Production in 2026: What Actually Survived
medium.com/@Micheal-Lanham/multi-agent-in-production-in-2026-what-actually-survived-f86de8bb1cd1
Collects the 2026 evidence into one line worth putting on a slide: architecture matters, but task shape matters more.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 16 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 1 · Agent Architectures: From Loop to Graph
ACT 2
Making the Graph Survive Reality
State that survives a crash · letting a human step in, and back out

ACT 2 · QUESTION 1
How do you give an agent state that survives a crash?

ACT 2 · QUESTION 1 — THE RATIONALE
What Must Survive a Crash?
Agents (work) are processes. Processes die. State shouldn’t.
Persist the right state, at the right time, in the right place

ACT 2 · QUESTION 1 — THE RATIONALE
Time Travel
State, nodes, edges Resume, don't restart Inspect state every node
State is what's known so far; nodes Without it, a crash at step 7 of 10 means The habit that prevents most schema-
transform it; edges decide what happens starting over at step 1 mismatch bugs —the most common setup
next —checkpointing saves state at each mistake
step
Source: LangGraph documentation on state, checkpointing, and persistence

ACT 2 · QUESTION 1 — THE RATIONALE
How to Persist the state?

ACT 2 · QUESTION 1 — THE RATIONALE
Checkpointing Process
Source: LangGraphCheckpointing Is Not Free -A Production Postmortem

ACT 2 · QUESTION 1 — SEE IT WORKING
Flight-Booking Agent: Rebooking After a Crash
User: “Rebook me on the 9:00 AM flight day after tomorrow.”
1. Save progress at each safe step
Booking found → options searched → user selected Flight 9:00 → payment requested.
2. Crash happens during payment
The agent process dies—but the saved state remains in a durable store.
3. Resume safely
A new worker reloads the checkpoint, checks the payment status using its idempotency key, and completes the booking—without searching
again or charging twice.
The agent can die. Its durable state, checkpoints, and external-operation records must not.

ACT 2 · QUESTION 1 — THE ANSWER
Checkpoints: A Save-Point, Not a Restart
Checkpointed state Schema mismatches are the top bug Nodes, edges, state
A saved state you can resume from, not  Print/inspect state after every node while  The vocabulary LangGraph uses for the same
| restart from | developing | old idea |
| ------------ | ---------- | -------- |

ACT 2 · QUESTION 1 — REMEMBER IT THIS WAY
“
A video game save-point — nobody wants to replay the whole game after one
crash.
The habit that prevents most bugs: inspect state after every node, not just when something breaks.

ACT 2 · QUESTION 2
How do you let a human step into an otherwise
autonomous loop — and back out?

ACT 2 · QUESTION 2 — THE RATIONALE
What Is a Human-in-the-Loop (HITL) Interrupt?
A deliberate pause Order matters Reserve it for high stakes
The graph stops at a defined point and waits The checkpointer must exist before the Interrupting every step defeats the purpose
for human input, then resumes interrupt point —wiring it after silently fails of automation
to pause at all
Source: LangGraph documentation on human-in-the-loop and interrupts

ACT 2 · QUESTION 2 — THE RATIONALE
Where a Human Steps In — and Why

ACT 2 · QUESTION 2 — SEE IT WORKING
Agent with a Human In The Loop
Source: Implementing Human-in-the-Loop with LangGraph

ACT 2 · QUESTION 2 — THE ANSWER
Wire the Checkpointer Before the Interrupt
Interrupts pause the graph Order matters Reserve it for high stakes
At a defined point, waiting for human input The checkpointer must exist before the Before irreversible actions, not every single
interrupt point —the #1 setup bug step

ACT 2 · QUESTION 2 — REMEMBER IT THIS WAY
“
A pause button that only works if it was wired into the remote before you pressed
play.
Over-interrupting defeats the purpose of automation — reserve it for what's actually irreversible.

Day 3 · Session 1
QUICK CHECK — NO PEEKING
Before we move past Making the Graph Survive Reality:
What must be wired before an interrupt point actually works?
1
Why is a checkpoint a prerequisite for an interrupt, and not the other way round?
2

DAY 3 · SESSION 1
ACT 2 · DEEP DIVE
Stepping In, and Choosing How Much Harness You Want
Human-in-the-loop interrupts · the harness spectrum from bare graph to full framework
START HERE — 3 THINGS
1 LangChain — Human-in-the-Loop middleware documentation
docs.langchain.com/oss/python/langchain/human-in-the-loop
The mechanism, current and precise.
2 ZenML — Your LangGraph agent works. Now make the workflow durable.
zenml.io/blog/langgraph-durable-runtime
The single best worked failure in this act.
3 Edge of Context — Long-Running AI Agent Runtime in 2026
slavadubrov.github.io/blog/2026/05/26/ai-agent-runtime
Names the five runtime primitives — session, harness, sandbox, checkpoint, trace — and compares who hosts which.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 15 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 1 · Agent Architectures: From Loop to Graph
ACT 3
Knowing When to Stop Adding Machinery
Durable ideas vs. disposable APIs · when a graph is overkill · one agent or several

ACT 3 · QUESTION 1
If LangGraph disappeared tomorrow, what would still be
true?

ACT 3 · QUESTION 1 — THE RATIONALE
What Separates a Durable Idea From a Disposable API?
Ideas predate the framework APIs are vocabulary The re-implementation test
State machines, checkpoints, and interrupts A convenient vocabulary for an idea, not the Could you rebuild today's pattern by hand, in
are decades-old distributed-systems ideas, idea's foundation —it survives the a different language? If yes, you learned the
not LangGraph inventions framework's rise and fall idea, not just the API
Source: General references on state-machine and workflow-orchestration design patterns

ACT 3 · QUESTION 1 — THE RATIONALE
The Ideas That Outlive the Framework

ACT 3 · QUESTION 1 — SEE IT WORKING
A Food-Delivery Order Still Works
User Order: “One veg biryani, delivered home.”
Order placed → Restaurant accepts → Food prepared → Rider assigned → Delivered
↓
Restaurant unavailable?
↓
Offer another restaurant
Even if the app that drew this workflow vanished tomorrow, the essentials remain:
✓ States:placed, accepted, preparing, out for delivery, delivered
✓ Transitions:move forward only when the required event occurs
✓ Checkpoint:reopen the app and still see “Rider is on the way”
✓ Human interrupt:customer support can cancel or change the address
✓ Reliability:avoid placing or charging for the same order twice
LangGraph is one way to implement this. The workflow, saved progress, decisions, and safeguards are the enduring ideas.

ACT 3 · QUESTION 1 — THE ANSWER
The API Is Disposable. The Ideas Aren't.
| State machines | Checkpointing | Human-in-the-loop interrupts |
| -------------- | ------------- | ---------------------------- |
The core abstraction, however it's  Resume, don't restart —true regardless of  The pattern outlives any one tool's API
| implemented | framework |     |
| ----------- | --------- | --- |

ACT 3 · QUESTION 1 — REMEMBER IT THIS WAY
“
A recipe survives even if the specific stove on which it was prepared goes out of
production.
The specific API is this year's best illustration of the idea — not the idea itself.

ACT 3 · QUESTION 2
When is a graph too much machinery for the job?

ACT 3 · QUESTION 2 — THE RATIONALE
When Is a Graph Too Much Machinery?
Straight lines stay chains Machinery has a carrying cost Complexity invites new failures
If every run visits the same steps in the same State schemas, checkpoint stores and node Multi-Agent System Failure Taxonomy
order, the branching a graph buys you is wiring are all code you now own and must (MAST) found most multi-agent failures are
never exercised keep correct specification and coordination bugs, not
model mistakes
Source: Cemri et al., MAST (arXiv:2503.13657); Anthropic, Building Effective Agents

ACT 3 · QUESTION 2 — SEE IT WORKING
Two Tasks, Only One Deserves a Graph
Task A — summarise an uploaded PDF
load -> chunk -> summarise -> return
Same four steps, same order, every single run. No branch is ever taken.
As a graph: 4 nodes, a state schema, a checkpointer — all of it unexercised.
Verdict: a chain. The graph adds code to maintain and nothing to show for it.
Task B — process an insurance claim
intake -> [ auto-approve | needs adjuster | needs fraud review ] -> payout
Routing depends on claim value. Adjuster step waits on a human, sometimes for days.
Verdict: a graph. Conditional routing, a human pause, and resume after a restart.
Ask which graph feature you would actually use. If the honest answer is none, you wanted a chain.

ACT 3 · QUESTION 2 — THE ANSWER
Reach for the Simplest Thing That Holds
Chain for straight lines Graph for branches and resume Machinery you own is machinery you
debug
Same steps, same order, every run —a chain Conditional routing, human pauses, or crash Most multi-agent failures are coordination
is enough recovery bugs, not model bugs

ACT 3 · QUESTION 2 — REMEMBER IT THIS WAY
“
You do not file a flight plan to walk to the corner shop.
If the work is a straight line that always runs to completion, a graph is paperwork, not architecture.

ACT 3 · QUESTION 3
Does this problem actually need more than one agent?

ACT 3 · QUESTION 3 — THE RATIONALE
What Is the Single-vs-Multi-Agent Decision?
Coordination is a real cost Earns its cost for specialization One agent is often enough
Message passing between agents, state sync, Genuinely distinct roles or independent, A single, well-scoped agent handles most
and entirely new failure modes a single agent parallelizable sub-tasks —not a default tasks perfectly well
doesn't have ‘more advanced’ upgrade
Source: General references on multi-agent system design trade-offs and coordination overhead

ACT 3 · QUESTION 3 — THE RATIONALE
Techniques You Can Run in the Lab

ACT 3 · QUESTION 3 — THE RATIONALE

ACT 3 · QUESTION 3 — SEE IT WORKING
Approving a Leave Request
Manager asks: “Can Priya take leave this Friday?”
Check leave balance → Check team calendar → Apply leave policy → Reply / escalate
One agent can use the HR, calendar, and policy tools to complete this safely.
Creating separate ‘leave-balance’, ‘calendar’, and ‘policy’ agents only creates hand-offs: each must pass the same
employee details, dates, and decision back and forth.
Several tools do not mean several agents. Start with one agent; split only when work is truly independent or needs separate specialist judgment

ACT 3 · QUESTION 3 — THE ANSWER
Multi-Agent Is an Org Decision, Not an Upgrade
Coordination has real cost Worth it for specialization or Not a default upgrade
parallelism
Message passing, state sync, new failure Genuinely distinct roles or independent sub- A single well-scoped agent is often enough
modes tasks

ACT 3 · QUESTION 3 — REMEMBER IT THIS WAY
“
You don't hire a five-person team to answer a question one competent person can
answer alone.
Multi-agent adds real coordination cost — it's a tool for specialization or parallelism, not a default upgrade.

Day 3 · Session 1
QUICK CHECK — NO PEEKING
Before we move past Knowing When to Stop Adding Machinery:
If LangGraph vanished tomorrow, name one idea that would still hold.
1
Give one task where a graph would be overkill — and say why.
2

DAY 3 · SESSION 1
ACT 3 · DEEP DIVE
What Survives When the Framework Doesn’t
The durable ideas underneath the morning’s tools
START HERE — 3 THINGS
1 Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (MAST)
arxiv.org/abs/2503.13657 · NeurIPS2025
The strongest single piece of evidence that the ideas outlast the tools: the failure taxonomy holds across seven different frameworks and four…
2 Sumers, Yao, Narasimhan, Griffiths — Cognitive Architectures for Language Agents (CoALA)
arxiv.org/abs/2309.02427
Cross-listed from Day 2.
3 Yao et al., ReAct: Synergizing Reasoning and Acting in Language Models
arxiv.org/abs/2210.03629
The Reason & Act loop underneath almost everything else in this course.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 9 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 1
Same three ideas — now you’ve built them
1 2 3
You can say what a bare loop cannot You built a checkpointed, resumable You justified an architecture choice
do — and why graph engineering workflow with a human-in-the-loop — chain or graph, one agent or
exists because of it. interrupt — wired in the right order. several — instead of defaulting to
the fanciest option.
✓ Milestone 5 · Orchestrated LangGraph workflow with checkpointing

SESSION · FINALE
Source: If You Know These 6 LangGraphConcepts, You Are Already Ahead of 90% of AI Developers

SESSION · FINALE
Source: Doubling down on Deep Agents

Day 3 · 08 August 2026
SESSION 2
Multi-Agent Collaboration & The Protocol Layer
“Teach the AI to Collaborate”
14:00 – 15:30
Milestone 6 · Specialized multi-agent team + MCP integration

Day 3 · Session 2
By the end of this session, three ideas will matter more than any
other
1 2 3
A supervisor routes by task state, When the agent picks its own team, The protocol layer is a stack, not a
not a fixed pipeline — and every the harness sets the limits on depth, race: MCP for tools, A2A for agents,
loop-back needs a hard cap or it can breadth and budget — the model AG-UI for users, AP2 for authority.
run forever. will not stop itself.

Day 3 · Session 2 · Multi-Agent Collaboration & the Protocol Layer
ACT 1
Coordinating a Fixed Team
Supervisor routing by state · stopping a review loop from running forever

ACT 1 · QUESTION 1
How does a supervisor agent decide who does what?

ACT 1 · QUESTION 1 — THE RATIONALE
What Is Supervisor-Based Routing?
Not a fixed pipeline Routes by task state The actor-critic parallel
A always-to-B always-to-C order can't handle Given where the task is right now, who Same underlying idea: a loop, not a straight
work that needs revision or a variable should act next —including sending it line
number of steps backward
Source: General references on multi-agent orchestration patterns (supervisor, choreography, actor-critic/reviewer)

ACT 1 · QUESTION 1 — THE RATIONALE
How a Supervisor Routes Work, Step by Step

ACT 1 · QUESTION 1 — SEE IT WORKING
How a Supervisor Routes Work, Step by Step
Customer: “I paid twice for my software subscription. Please fix it.”
The supervisor consults its agent directory:
Agent What the supervisor knows
Payments Investigator Can read the transaction ledger
Refund Specialist Can issue eligible refunds
Support Writer Can explain payment status
Human Support Handles high-risk exceptions
It also sees each agent’s tools, permissions, expertise, risk limit, availability, and current case state.
Current case state Supervisor assigns Why this agent?
Charges are unverified Payments Investigator Can read the transaction ledger
Duplicate charge confirmed Refund Specialist Has refund-policy knowledge and refund permission
One charge is only pending Support Writer Explains what happened; no refund is needed
Records disagree or amount is high Human Support Risk is too high for automatic action
The supervisor does not need to do every task itself. It needs a clear map of who can do what—and under which limits.
A supervisor matches the task’s current state to the right agent’s skills, tools, permissions, risk limits, and availability—then checks the result before
deciding what happens next.

ACT 1 · QUESTION 1 — THE ANSWER
Routing Is State-Based, Not a Fixed Pipeline
Supervisor routes by task state Today's 5-agent team Loops back when needed
Not a hardcoded, fixed sequence Researcher, Planner, Writer, Reviewer, Fact- Not everything flows forward only once
Checker

ACT 1 · QUESTION 1 — REMEMBER IT THIS WAY
“
An editor routing a draft between a writer and a fact-checker, as many times as
needed.
Routing is based on task state — not a fixed, hardcoded sequence.

ACT 1 · QUESTION 2
How does an agent stop a review loop from running
forever?

ACT 1 · QUESTION 2 — THE RATIONALE
Edge Classification
Source: Graph Engineering Is Loop Engineering With An Org
Source: Spinning Around In Cycles With Directed Acyclic Graphs Chart Drawn On Top

ACT 1 · QUESTION 2 — THE RATIONALE
What Is a Hard Cap on Loop-Back Edges?
No natural stopping point Design it in, don't react to it Same discipline as Day 1
A reviewer that's never fully satisfied will The cap belongs in the system from the start, The ReAct/self-repair loop cap, now applied
loop indefinitely without an explicit limit not added after it's found burning through to a multi-agent loop-back edge
budget
Source: General references on cycle detection and termination conditions in agent graphs

ACT 1 · QUESTION 2 — SEE IT WORKING
A Review Loop That Never Ends
Without a cap
Writer -> Reviewer: ‘needs more detail’;
Writer -> Reviewer: ‘better, but tighten the intro’;
Writer -> Reviewer: ‘needs more detail’; <- back where it started
...41 more round trips, no exit, tokens burning the whole way
With a cap
state[‘revisions’] += 1
if state[‘revisions’] >= 3:
return “escalate_to_human”; # not “keep trying”;
The cap is not there because three rounds is optimal. It is there because ‘until it is good’ is not a termination condition.

ACT 1 · QUESTION 2 — THE ANSWER
Cap It — Don't Hope It Converges
Hard cap on revision rounds A documented common bug Perfectionism has no deadline
Designed in from the start, not added after Exactly this lab's most frequent mistake A reviewer that's never satisfied will loop
the bug bites forever

ACT 1 · QUESTION 2 — REMEMBER IT THIS WAY
“
An editor with no deadline who keeps sending a manuscript back for one more
revision, forever.
Build the cap in from the start — don't wait to hit the problem first.

Day 3 · Session 2
QUICK CHECK — NO PEEKING
Before we move past Coordinating a Fixed Team:
Is supervisor routing a fixed sequence, or based on task state?
1
What stops a review loop from running forever?
2

DAY 3 · SESSION 2
ACT 1 · DEEP DIVE
Coordinating a Team of Agents
Supervisor routing · knowing when to stop a review loop
START HERE — 3 THINGS
1 MAST per-mode prevalence (Mert et al.) — Why Do Multi-Agent LLM Systems Fail?
arxiv.org/abs/2503.13657 · arxiv.org/abs/2601.17915
This act’s loop-cap lesson has a number attached to it.
2 Sovereign Agentic Loops — Decoupling AI Reasoning from Execution in Real-World Systems
arxiv.org/abs/2604.22136
Independent agents amplify errors up to 17x; centralised architectures with validation bottlenecks contain them to about 4.4x.
3 Kim et al. — Tiered Agentic Oversight (TAO): A Hierarchical Multi-Agent System for Healthcare Safety
arxiv.org/abs/2506.12482
Routing by complexity and risk, with higher tiers overseeing lower ones.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 14 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 2 · Multi-Agent Collaboration & the Protocol Layer
ACT 2
When the Team Isn't Fixed
When the roster does not fit · topology decided at runtime · the caps that contain it

★ WHAT'S NEW · 2026
ACT 2 · QUESTION 1
Your supervisor has a fixed roster of agents. What happens
when the task doesn't fit the roster?

ACT 2 · QUESTION 1 — THE RATIONALE
What Is Agent Topology?
structural arrangement and communication pathways connecting multiple AI agents in a collaborative network
... defines how tasks are routed, who talks to whom, and how data flows across
Source: Network Topology Projects
Source: After Analyzing17 Multi-Agent Topologies —7 Anti-Patterns That Will Burn Your Budget

ACT 2 · QUESTION 1 — THE RATIONALE
What Is Agent Topology, and What Fixes It?
Topology is roster plus routing Fixed topology is decided at design New task shapes cost a redeploy
time
Which agents exist, and who hands work to Today's lab team is wired before any task The roster can only serve the work you
whom arrives anticipated
Source: IBM Agent Communication Protocol documentation
Source: Zed Agent Client Protocol documentation

ACT 2 · QUESTION 1 — THE RATIONALE
A Fixed Roster Meeting a Task It Was Not Built For

ACT 2 · QUESTION 1 — SEE IT WORKING
A Fixed Roster Meeting a Task It Was Not Built For
Employee: “My laptop was stolen. Secure company data immediately.”
Fixed Roster: Password Reset • Hardware Support • Device Procurement
None can remotely lock the laptop, revoke active sessions, or wipe company data.
Fixed roster → Pick the “closest” agent → Password reset only
↓
Security gap remains
With runtime composition, the supervisor brings in a pre-approved Security Response agent with the right tools and permissions.
A fixed roster can only reroute work it anticipated. When a new capability is needed, it must escalate, redeploy—or compose the right team at
runtime.

ACT 2 · QUESTION 1 — THE ANSWER ★ WHAT'S NEW · 2026
A Fixed Roster Only Serves the Tasks You Predicted.
Every new capability is a code change Over-provisioning isn't free The alternative: compose at runtime
A task outside the roster means a redeploy, Spare agents dilute routing accuracy and cost Let the orchestrator decide the roster for
not a runtime decision tokens on every request each task

ACT 2 · QUESTION 1 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
A consultancy with five permanent staff, versus one that assembles a team per
client brief.
Fixed topology means your designhas to predict the work. Dynamic topology moves that decision to runtime.

★ WHAT'S NEW · 2026
ACT 2 · QUESTION 2
What does it look like when an agent decides, on its own,
how many other agents it needs?

ACT 2 · QUESTION 2 — THE RATIONALE
What Is Dynamic Agent Topology?
Dynamic, on-the-fly collaboration networks (communication pathways, team structures, and data flows)
Instead of rigid pipelines, it builds task-specific / round-specific collaboration networks
Source: Breaking the Static Mold: How DyTopoRevolutionizes Multi-Agent Reasoning

ACT 2 · QUESTION 2 — THE RATIONALE
What Is Dynamic Agent Topology?
Fixed: decided in advance Dynamic: decided at runtime Build fixed first
A pre-wired team (like today's 5-agent lab) Kimi K3's Agent Swarm and Deep Agents' The dynamic version is a natural extension
has its shape decided before any task runs subagent delegation spawn however many once the fixed pattern actually works
sub-agents a task needs, on the fly
Source: Moonshot AI's Kimi K3 Agent Swarm documentation
Source: Deep Agents (LangChain) dynamic subagent delegation documentation

ACT 2 · QUESTION 2 — THE RATIONALE
A Team Composed at Runtime, Not Design Time

ACT 2 · QUESTION 2 — THE RATIONALE
Dynamic Agent Topology – Decision Framework

ACT 2 · QUESTION 2 — SEE IT WORKING

ACT 2 · QUESTION 2 — THE ANSWER ★ WHAT'S NEW · 2026
Dynamic Topology, Decided at Runtime
Kimi K3 Agent Swarm Deep Agents subagent delegation Vs. today's fixed 5-agent team
Spawns however many sub-agents the task The same idea, in LangChain's harness Yours is decided in advance; these decide at
needs runtime

ACT 2 · QUESTION 2 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
A manager who calls in exactly the specialists a project needs, decided in the
moment — vs. a fixed org chart used for every project.
Build the fixed version first — the dynamic version is a natural extension once the fixed one works.

★ WHAT'S NEW · 2026
ACT 2 · QUESTION 3
If an agent can spawn other agents, what stops it from
spawning a thousand?

ACT 2 · QUESTION 3 — THE RATIONALE
What Is Unbounded Fan-Out?
occurs when a single input splits into a limitless number of parallel tasks or connections
offers infinite scalability, but carries a high risk of catastrophic resource exhaustion
Key Characteristics
✓ No Built-in Limits: The system allows the number of
parallel outputs to scale dynamically based on immediate
load or data size.
✓ Resource Risk: Can cause severe bottlenecks, memory
exhaustion, or network saturation because the
infrastructure must instantly handle peak volume.
✓ Performance Gain: Speeds up processing by executing
massive amounts of independent work concurrently
rather than sequentially
Source: Fan-Out and Fan-In –The Unsung Heroes of System Design

ACT 2 · QUESTION 3 — THE RATIONALE
What Is Unbounded Fan-Out?
Spawning is recursive by default Cost grows with the tree, not the task Act 1's runaway loop, one level up
A spawned agent can usually spawn too, so Every branch carries its own context window Same failure mode, larger blast radius, far
depth compounds silently and token spend harder to see
Source: IBM Agent Communication Protocol documentation
Source: Zed Agent Client Protocol documentation

ACT 2 · QUESTION 3 — THE RATIONALE
How a Spawn Tree Gets Away From You

ACT 2 · QUESTION 3 — THE RATIONALE
Keeping Spawn Trees in Check: Boundaries for Controlled Agent Spawning

ACT 2 · QUESTION 3 — SEE IT WORKING
A Claims Surge
At 9:00 AM, 1,000 insurance claims arrive.
An uncontrolled supervisor might spawn one reviewer per claim. Each reviewer may then spawn document-checking or policy-checking agents.
1,000 claims → 1,000 reviewers → thousands of tool calls
Soon, token spend, API limits, and system capacity are exhausted.
A production control plane treats spawning as a permissioned request, not an unrestricted right:
Spawn request → Check limits → Queue / approve / reject
Limits for the permissioned request looks like below:
• Concurrency cap: only 20 reviewers run at once
• Depth cap: reviewers cannot spawn more reviewers
• Budget & time cap: stop when the task allowance is used
• Backpressure:remaining claims wait safely in a queue
• Escalation:unusual volume alerts an operator
The agent can ask to spawn. The runtime decides whether it is allowed—and how many can run.

ACT 2 · QUESTION 1 — SEE IT WORKING
Flight-Booking Agent: Rebooking After a Crash
User: “Rebook me on the 9:00 AM flight day after tomorrow.”
1. Save progress at each safe step
Booking found → options searched → user selected Flight 9:00 → payment requested.
2. Crash happens during payment
The agent process dies—but the saved state remains in a durable store.
3. Resume safely
A new worker reloads the checkpoint, checks the payment status using its idempotency key, and completes the booking—without searching
again or charging twice.
The agent can die. Its durable state, checkpoints, and external-operation records must not.

ACT 2 · QUESTION 3 — THE ANSWER ★ WHAT'S NEW · 2026
The Harness Sets the Limit, Not the Model.
Cap depth and breadth Cap the budget, not just the count A tree you can't trace is a tree you can't
debug
Max spawn depth, max concurrent children Total tokens and wall-clock, enforced outside Dynamic topology raises the bar on
per parent the model observability —tomorrow's first session

ACT 2 · QUESTION 3 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
A manager who can hire is useful. A manager who can hire managers needs a
headcount budget.
The model won't stop itself. Set the limits in the harness — how deep, how wide, how much.

Day 3 · Session 2
QUICK CHECK — NO PEEKING
Before we move past When the Team Isn't Fixed:
What are the two real costs of over-provisioning a fixed roster?
1
Name two things you must cap when an agent can spawn other agents.
2

DAY 3 · SESSION 2
ACT 2 · DEEP DIVE
Standardizing How Agents Reach Tools, and Each Other
MCP and A2A · the wider protocol layer · and the security year nobody planned for
START HERE — 3 THINGS
1 Prompt20 — AI Agent Protocols: MCP, A2A, ACP and the Interop Stack
blog.prompt20.com/posts/ai-agent-protocols
The best single map of the 2026 layer: MCP for tools and context, A2A or ACP for cross-organisation delegation, OASF/AGNTCY for discovery and…
2 Cloud Security Alliance — MCP Security Crisis: Systemic Design Flaws in AI Agent Infrastructure
labs.cloudsecurityalliance.org/research/csa-research-note-mcp-security-crisis-20260504-csa-styled
The security picture in one place: the STDIO command-execution flaw across the official SDKs, Anthropic’s position that the behaviour is…
3 MCP Threat Modeling and Analysis of Vulnerabilities to Prompt Injection with Tool Poisoning
mdpi.com/2624-800X/6/3/84
Peer-reviewed STRIDE and DREAD threat modelling across all six MCP components.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 25 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 2 · Multi-Agent Collaboration & the Protocol Layer
ACT 3 OF 4
Why Protocols Exist
The N x M problem · MCP for tools · A2A for agents

ACT 3 · QUESTION 1
Your agent now needs a tool built by someone you’ve
never met. How do you connect them?

ACT 3 · QUESTION 1 — THE RATIONALE
Why Did Agent Protocols Emerge At All?
The N x M problem Bespoke integrations do not compose A standard turns N x M into N + M
M agents times N tools means M x N hand- Every pairing has its own auth, schema and Each side implements the standard once; any
written connectors, each one separately error handling —nothing learned once conforming agent then reaches any
maintained transfers anywhere conforming tool
Source: Model Context Protocol specification (modelcontextprotocol.io); Linux Foundation AAIF

ACT 3 · QUESTION 1 — SEE IT WORKING
Counting the Connectors
Four agents, five tools, no standard
research-agent -> Jira, Drive, Postgres, Slack, GitHub (5 connectors)
support-agent -> Jira, Drive, Postgres, Slack, GitHub (5 connectors)
finance-agent -> Jira, Drive, Postgres, Slack, GitHub (5 connectors)
ops-agent -> Jira, Drive, Postgres, Slack, GitHub (5 connectors)
4 x 5 = 20 hand-written integrations. Add one tool: +4. Add one agent: +5.
Same four agents, five tools, one standard
4 agents speak MCP + 5 tools expose MCP = 9 implementations
Add one tool: +1. Add one agent: +1.
This is the whole argument. Not elegance — arithmetic. N x M becomes N + M.

ACT 3 · QUESTION 1 — THE ANSWER
Protocols Turn N x M Into N + M
Written once, reused everywhere Governance is the maturity signal It is a stack, not a race
Implement the standard once instead of one  MCP and A2A both sit under the Linux  Tools, agents, users and authority are
| connector per pair | Foundation now | different layers |
| ------------------ | -------------- | ---------------- |

ACT 3 · QUESTION 1 — REMEMBER IT THIS WAY
“
Every appliance in your kitchen has a different plug. Now imagine buying a new
one and being handed a soldering iron.
A protocol is the wall socket. Without one, every connection is hand-wired and yours to maintain forever.

ACT 3 · QUESTION 2
Why can't Claude just automatically use your company's
internal tools?

ACT 3 · QUESTION 2 — THE RATIONALE
What Is MCP (Model Context Protocol)?
Bespoke, before MCP A standard vocabulary Write once, use anywhere
A custom internal-API integration built for Clients, servers, tools, resources —the same One MCP server works from any MCP-
one AI product doesn't automatically work way USB-C standardized what used to be a compatible client
with a different one different port per device
Source: Model Context Protocol specification (modelcontextprotocol.io)

ACT 3 · QUESTION 2 — THE RATIONALE
Inside an MCP Call, End to End

ACT 3 · QUESTION 2 — THE RATIONALE
Under the Hood – MCP Architecture

ACT 3 · QUESTION 2 — SEE IT WORKING
The N x M Problem MCP Was Built to Kill
Employee asks Claude: “Book a room for my 2 PM meeting.”
Claude cannot simply “use the room-booking system.” It does not know:
• how to call that system
• who is allowed to book which rooms
• what inputs, errors, and approval rules apply
Without MCP: every AI client needs its own custom integration.
Claude Desktop ┐
Cursor ├── separate integrations ──→ Room Booking System
Internal Agent ┘
With MCP: the company exposes approved, well-described tools once:
Room Booking MCP Server
• find_available_rooms
• book_room
• cancel_booking
↓
Any approved MCP-compatible client
MCP does not give Claude automatic access. It gives approved clients a shared, secure language for using tools your company explicitly exposes.

ACT 3 · QUESTION 2 — THE ANSWER
Without a Standard, Every Integration Is Bespoke
One-off glue code MCP: the USB-C moment Standardized, not proprietary
Every product needs its own custom Clients, servers, tools, resources —write One server works from many different clients
integration, rebuilt each time once, use anywhere

ACT 3 · QUESTION 2 — REMEMBER IT THIS WAY
“
Before USB existed, every device needed its own custom port and cable.
MCP standardizes clients, servers, tools, and resources — write once, use from any compatible client.

★ WHAT'S NEW · 2026
ACT 3 · QUESTION 3
If MCP already lets a model use tools, why does the
industry also need A2A?

ACT 3 · QUESTION 3 — THE RATIONALE
What Is Agent 2 Agent (A2A) protocol?
Universal communication layer for AI agents
enables agents built on different frameworks / vendors to "talk" to one another seamlessly
Source: MCP plus A2A, here is how they complement each other

ACT 3 · QUESTION 3 — THE RATIONALE
How agents collaborate using A2A?

ACT 3 · QUESTION 3 — THE RATIONALE
Data Flow in A2A

ACT 3 · QUESTION 3 — THE RATIONALE
How Does A2A Differ From MCP?
MCP: vertical A2A: horizontal Complementary, not competing
An agent talking to a tool or data source — An agent talking to another independently- Production systems increasingly need both
using its ‘hands’ built agent, across organizational boundaries together
—a ‘handshake’
Source: Agent2Agent (A2A) protocol specification (Google, April 2025)

ACT 3 · QUESTION 3 — THE RATIONALE
MCP and A2A on the Same Map

ACT 3 · QUESTION 3 — THE RATIONALE
MCP and A2A on the Same Map

ACT 3 · QUESTION 3 — SEE IT WORKING
A Customer Needs a Replacement Card
Customer: “My card was lost. Block it and send me a replacement.”
Support Agent
│
├── via MCP → block_card
└─── via A2A → Card-Replacement Agent
│
└── via MCP → verify_address, issue_replacement
• MCP lets each agent use approved banking tools.
• A2A lets the Support Agent hand the outcome to the independent Card-Replacement Agent, which owns its own workflow and customer
updates.
• The replacement agent may use different systems, policies, and even be run by another team.
MCP answers: “How can an agent use this capability?”
A2A answers: “Which capable agent can take this work?”

ACT 3 · QUESTION 3 — THE ANSWER ★ WHAT'S NEW · 2026
MCP Is Hands. A2A Is a Handshake.
MCP: vertical A2A: horizontal Complementary, not competing
Agent talks to a tool or data source Agent talks to another agent (Google, April Production systems increasingly use both
2025) together

ACT 3 · QUESTION 3 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
MCP is your phone's app store. A2A is your phone's contacts app.
MCP is how an agent uses its hands. A2A is how two agents shake them.

Day 3 · Session 2
QUICK CHECK — NO PEEKING
Before we move past Why Protocols Exist:
Why does a MCP standard turn N x M into N + M?
1
MCP and A2A: which is vertical, which is horizontal, and who governs both now.
2

DAY 3 · SESSION 2
ACT 3 · DEEP DIVE
When the Agent Picks the Team
Dynamic topology · unbounded fan-out · the caps that contain it
START HERE — 3 THINGS
1 Jun He et al — Sovereign Agentic Loops — 17x versus 4.4x error amplification
arxiv.org/abs/2604.22136
The quantitative case for capping a dynamic team.
2 Deep Agents
github.com/langchain-ai/deepagents
Runtime sub-agent delegation as a working implementation.
3 Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (MAST)
arxiv.org/abs/2503.13657 · NeurIPS2025
Cross-listed. "Unaware of termination conditions" at 12.4% is measured on fixed topologies.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 15 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 2 · Multi-Agent Collaboration & the Protocol Layer
ACT 4 OF 4
Reading the Wider Landscape
Reaching the user · proving authority to act · choosing without marrying

ACT 4 · QUESTION 1
Your agent works for three minutes before answering.
What is the user looking at the whole time?

ACT 4 · QUESTION 1 — THE RATIONALE
What Is AG-UI (Agent-User Interaction)?
Request-response breaks down A two-way event protocol Transport-agnostic by design
Agents run long, stream partial work and can AG-UI carries a live exchange: agent Runs over SSE, WebSockets or webhooks; a
change the UI unpredictably —A final REST messages and state updates flow to the app; middleware layer keeps clients and backends
response assumes / captures none of that user actions, form input, approvals, and loosely coupled
interrupts flow back
Source: AG-UI documentation (docs.ag-ui.com); originated from CopilotKit with LangGraph and CrewAI

ACT 4 · QUESTION 1 — SEE IT WORKING
Onboarding a New Employee
Manager: “Set up Arjun for his first day on Monday.”
Agent → “Checking role and access policy…”
Agent → Shows laptop choices: [Windows] [Mac]
Manager → Selects: Mac
Agent → Updates shared checklist:
✓ Email created
✓ Slack access granted
Payroll needs manager approval
Manager → [Approve] [Edit start date] [Escalate to HR]
Agent → Completes setup and shows the final onboarding plan
AG-UI carries more than progress:
• Messages & streamed results
• Shared application state—such as the live checklist
• Interactive UI—choices, forms, and rendered tool results
• Human control—approve, edit, pause, retry, or redirect work
• Interruptions & resume—without losing the session
AG-UI is the live, two-way interaction contract between an agent and its application—not just a better loading spinner

ACT 4 · QUESTION 1 — SEE IT WORKING
AG-UI in Action
Source: AGUI (Agent to UI Protocol) -What Should Backend and Frontend Developers Know

ACT 4 · QUESTION 1 — THE ANSWER
A Live, Two-Way Contract — Not a Better Spinner
Events, not a final reply The shared interaction Any transport you already run
The user watches the agent think, act and The user can see, guide, pause, correct, and SSE, WebSockets or webhooks —no new
correct itself, instead of staring at a spinner. resume the work as it unfolds—without the infrastructure required
Stream messages, progress, tool results, UI- application being tied to one agent
ready data, and shared-state updates. framework

ACT 4 · QUESTION 1 — REMEMBER IT THIS WAY
“
A parcel-tracking page that lets you change the delivery address, approve a
customs charge, pause delivery, and see each update as it happens.
Agents do the work; AG-UI lets the application show it, the user shape it, and both continue from the same
shared state.

ACT 4 · QUESTION 2
Your agent is about to spend your money. How does
anyone prove you allowed it?

ACT 4 · QUESTION 2 — THE RATIONALE
What Is AP2 (Agent Payments Protocol)?
Mandates are signed evidence Three mandates, one chain Human present or absent
Verifiable Credentials act as tamper-proof Intent, Cart and Payment mandates together Approve a cart live, or pre-sign limits on
signed contracts, producing a non-repudiable prove what was asked for, agreed to, and price, timing and conditions so the agent can
audit trail finally charged act later
Source: Google Cloud, Announcing Agent Payments Protocol (AP2), September 2025

ACT 4 · QUESTION 2 — SEE IT WORKING
One Purchase, Three Signed Mandates
1. Intent Mandate — signed before anything is chosen
‘Book a Hyderabad-Delhi flight, under Rs 8,000, departing Friday’;
Human absent? The limits are pre-signed, so the agent may act without you watching.
2. Cart Mandate — signed once a specific cart exists
‘IndiGo 6E-234, Fri 07:15, Rs 6,480, non-refundable’;
This is the moment the exact amount and item become non-repudiable.
3. Payment Mandate — signed at settlement
Card network sees: agent-initiated, user-authorised, tied to the cart above.
If this is disputed later, nobody argues from chat logs — there are three signatures with timestamps.

ACT 4 · QUESTION 2 — THE ANSWER
Authority Has to Be Provable, Not Assumed
Signed before, not argued after Intent, Cart, Payment Works when you are not watching
A cryptographic receipt written at the Three mandates covering what was asked for, Pre-signed limits on price, timing and
moment of consent, not reconstructed from what was agreed to, and what was finally conditions let an agent act inside a boundary
logs later charged you set

ACT 4 · QUESTION 2 — REMEMBER IT THIS WAY
“
Handing your card to a friend with a note that says “good for one coffee, under
200 rupees, today only.”
Not trust, but a signed receipt written before the purchase — that is what a mandate is.

★ WHAT'S NEW · 2026
ACT 4 · QUESTION 3
Are MCP and A2A the only protocols in agentic era?

ACT 4 · QUESTION 3 — THE RATIONALE
What Does the Protocol Layer Actually Look Like?
It's a stack, not a race Governance is the maturity signal Discovery is still unsolved
Tools, agent-to-agent delegation, identity A foundation-governed spec is a different bet Nobody has convincingly solved how agents
and discovery —different layers, different from a single-vendor one find each other yet
protocols

ACT 4 · QUESTION 3 — THE RATIONALE
The 2026 Protocol Layer, Stacked

ACT 4 · QUESTION 3 — SEE IT WORKING
Source: Developer’s Guide to AI Agent Protocols

ACT 4 · QUESTION 3 — THE ANSWER ★ WHAT'S NEW · 2026
Adopt the Protocol. Don't Marry It.
Pick by layer, not by popularity Keep it at the edges Judge by exit cost
Ask which layer the problem is on before Protocol code belongs at the boundary, A young standard is a fine bet if leaving it
asking which protocol is winning never inside domain logic costs you one adapter

ACT 4 · QUESTION 3 — REMEMBER IT THIS WAY ★ WHAT'S NEW · 2026
“
You adopted HTTP without writing your business logic in it.
Bet on young standards freely — just keep the bet small enough to unwind.

Day 3 · Session 2
QUICK CHECK — NO PEEKING
Before we move past Reading the Wider Landscape:
Why can't a normal REST endpoint serve an agent that works for three minutes?
1
Name the three AP2 mandates — and say which one is signed before a cart exists.
2

DAY 3 · SESSION 2
ACT 4 · DEEP DIVE
Reading the Wider Landscape
AG-UI · AP2 · UCP, A2UI and WebMCP · judging a protocol by its exit cost
START HERE — 3 THINGS
1 AG-UI — Agent-User Interaction Protocol
docs.ag-ui.com
The spec, the ~16 event types, and the Dojo of small runnable examples.
2 Google Cloud — Announcing the Agent Payments Protocol (AP2)
cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol· September 2025
"Find the simplest solution possible", and the observation that for many applications a single LLM call plus retrieval and good examples is…
3 Lanham — Multi-Agent in Production in 2026: What Actually Survived
medium.com/@Micheal-Lanham/multi-agent-in-production-in-2026-what-actually-survived-f86de8bb1cd1
Collects the 2026 evidence into one line worth putting on a slide: architecture matters, but task shape matters more.
+ a few more essential picks and the extended list — papers, tools & repos, practitioner writing, hands-on — 16 resources in all, in the companion Deep Dive
Resources guide.

Day 3 · Session 2
Same three ideas — now you’ve built them
1 2 3
You built a supervised multi-agent You exposed and consumed a You can judge a young protocol by
team that routes by state, with a standardized MCP tool, and can its exit cost — and you have seen
hard cap so no loop runs forever. place MCP, A2A, AG-UI and AP2 on where self-directed agent teams are
the same map. heading.
✓ Milestone 6 · Specialized multi-agent team + MCP integration

DAY 3 · CLOSING QUESTION — WE WILL NOT ANSWER THIS TODAY
Everything Today Made Agents More Autonomous. And Harder to See.
This morning you gave the agent durable state, a human pause, and a graph you can resume.
This afternoon you gave it a team, it picks itself, and protocols to reach past your own walls.
So here is the question we are leaving open:
If your agentic solution gave a wrong answer at 3 a.m.,
where would you even start?
Do not answer it now. Sit with it overnight — it is the first question of tomorrow morning.