# AI Agentic Learning: Context & Regeneration Spec

This file holds everything needed to understand the learning plan and regenerate the living doc "AI Agentic Learning: Daily Plan & Progress" from scratch.

Living doc (current version): https://claude.ai/code/artifact/05f439c5-a05c-4d47-ba44-061a40ee5262

---

## 1. Original requirement (verbatim)

> I'm a backend engineer (Node.js: streams, buffers, cluster/workers, IPC, Redis shared state, AsyncLocalStorage/request-id propagation) moving into agentic AI. Goal: get familiar with the daily work of agentic AI roles in 2–3 months, then prep for those roles, then gradually move toward core ML (inference/infra, then fine-tuning and training). Plan: Month 1 is raw LLM APIs, tool calling, structured outputs, streaming, and basic RAG. Month 2 is agent patterns, memory and state, observability, and evals. Month 3 is production concerns (cost, latency, caching, guardrails, MCP) plus one polished project. I also want to start getting comfortable in Python, and run a slow parallel track on math, PyTorch, and Karpathy's Zero to Hero from around month 3. I prefer one topic at a time, concepts first, with small hands-on builds where they matter.

---

## 2. Starting skills

Backend engineer with Node.js depth in:

- **Streams and buffers**: chunked data, backpressure, piping.
- **Cluster/workers and IPC**: multi-process concurrency and message passing.
- **Redis shared state**: state shared across processes and instances.
- **AsyncLocalStorage / request-id propagation**: carrying context through async call chains.

New territory: Python, LLM APIs, agent design, evaluation of probabilistic systems, and later ML math and PyTorch.

### How existing skills map to agentic AI

| Existing skill | Where it shows up in agentic AI |
| --- | --- |
| Streams, backpressure | Streaming LLM responses (SSE), proxying streams to clients, cancelling upstream calls on disconnect |
| Redis shared state | Agent memory, durable agent state, checkpoints, caching (exact and semantic) |
| AsyncLocalStorage, request ids | Tracing nested LLM and tool calls; Python's equivalent is `contextvars` |
| Cluster/workers, IPC | Queue-backed agent workers, concurrency limits, later inference serving and batching |

The genuinely new mental shift: outputs vary run to run, so testing becomes **evaluation** (datasets, graders, scores) rather than assertion.

---

## 3. Why it's sequenced this way

**Month 1: no frameworks.** Raw API calls first, so every later abstraction (LangGraph, agent SDKs) is understood as a wrapper over things already built by hand: the message array, the tool-call loop, the stream parser.

**Order within Month 1:**
1. Python on-ramp alongside first API calls. Most agentic AI tooling and job expectations are Python-first, and simple API builds are a low-stakes way to learn the language.
2. Streaming and structured outputs before tools, because tool calling depends on both (streamed tool calls, schema-valid arguments).
3. Resilience (retries, backoff, timeouts) early, since every later build depends on a reliable client.
4. Tool calling, then the agent loop written by hand.
5. Basic RAG last, since it combines embeddings, retrieval, and prompting, and introduces the first measurement habit (recall@k).

**Month 2: patterns, then state, then visibility, then measurement.**
- Agent patterns first (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, ReAct), based on Anthropic's "Building effective agents."
- Frameworks surveyed only after building from scratch, to compare against something understood.
- Memory and state next, where Redis experience applies directly.
- Observability before evals, because you diagnose failures from traces before you can design good eval cases.
- Evals close the month and become the tool for every Month 3 change.

**Month 3: production concerns, then ship.**
- Cost, latency, and caching first, measured with the Month 2 traces.
- Guardrails and security next, with attacks added to the eval set.
- MCP after the agent is solid, so it plugs tools into a working system.
- Final week polishes one project into a portfolio piece.

**Parallel track from Week 9, deliberately slow (about 3 hours/week).** Order is dependency-driven: linear algebra basics, then calculus (derivatives, chain rule) before micrograd, remaining linear algebra before makemore, probability/softmax/cross-entropy alongside PyTorch basics, then "Let's build GPT" after Week 12.

**Habit throughout:** ask "how would I know this works?" from the first RAG build, even though formal evals arrive in Month 2.

---

## 4. Finalized decisions

| Decision | Value |
| --- | --- |
| Start date | Monday, September 28, 2026; week dates reset on October 21, 2026 after Day 1 (Week 1 runs Oct 21 – Nov 1, Week 12 ends Jan 17, 2027; Weeks 9–10 cross the year-end holidays) |
| Length | 12 weeks: 60 weekday learning days plus weekend sessions |
| Weekday time | About 1 hour: finish the concept, start the task |
| Weekend time | One longer session, 3–4 hours, for builds, review, and catch-up |
| Sunday | Buffer |
| Unfinished weekday tasks | Roll into the weekend session |
| LLM provider for hands-on | Groq free tier, OpenAI-compatible API (OpenAI SDK with `base_url=https://api.groq.com/openai/v1`), model `openai/gpt-oss-20b` (a reasoning model: hidden reasoning tokens count toward `max_tokens`). No paid Claude API key, so Anthropic-format examples get adapted |
| Default build language | Python; a few builds in Node where existing depth clarifies the concept |
| Day format | One topic per day: concept first, then a small hands-on task |
| Suggested Month 3 project | Incident/ops copilot: RAG over runbooks, logs and metrics via MCP tools, next-step suggestions with approval gates (confirm or swap by end of Week 8) |
| After Week 12 | Role prep, then inference/infra, then fine-tuning, then training |

---

## 5. Canonical day-by-day plan

### Month 1: LLM APIs, tools, basic RAG

**Week 1 (Oct 21 – Nov 1): Python on-ramp and first API calls**
- Day 1: Tokens, context window, messages/roles, system prompt, temperature/top-p. Task: uv setup; same call via curl, raw httpx, SDK.
- Day 2: Python for Node devs (lists, dicts, comprehensions, f-strings, modules, type hints, pyproject). Task: port a small Node utility.
- Day 3: asyncio vs the Node event loop (await, gather, semaphores). Task: 10 concurrent calls, limit 3, timed.
- Day 4: Prompting basics (system prompts, few-shot, XML delimiters, prompts as versioned code). Task: CLI summarizer; compare 3 temperatures.
- Day 5: Multi-turn chat, statelessness, token counting, truncation. Task: CLI chat with history trimmed to a token budget.
- Weekend: Chat CLI v1 with config and per-call token/cost logging; 1 page of notes.

**Week 2 (Nov 2 – 8): Streaming and structured outputs**
- Day 6: SSE, event types, deltas, time-to-first-token. Task: parse SSE by hand, then with the SDK.
- Day 7: Streaming through a server, backpressure, disconnects. Task: Node proxy that aborts upstream when the client leaves.
- Day 8: JSON mode, schema-constrained output, why JSON breaks. Task: extract fields from 20 messy texts; count failures.
- Day 9: Pydantic (Zod as the Node twin), retry with error feedback. Task: validate-then-retry loop with logged failures.
- Day 10: 429s, overload, timeouts, backoff with jitter, idempotency. Task: resilient client wrapper with simulated failures.
- Weekend: Structured extractor service in FastAPI.

**Week 3 (Nov 9 – 15): Tool calling**
- Day 11: Tool schemas; model requests, code executes, results returned. Task: one calculator tool, full round trip, raw API.
- Day 12: The agent loop with a max-iteration cap. Task: loop with calculator, read file, HTTP GET.
- Day 13: Tool design (names, descriptions, schemas, actionable errors, parallel calls). Task: bad vs good descriptions on 10 prompts.
- Day 14: Tool safety (timeouts, allowlists, confirmation). Task: human-approval step and per-tool timeouts.
- Day 15: Streaming plus tools; cost accounting per loop. Task: live stream with per-run cost summary.
- Weekend: Mini ops assistant with tools over SQLite and Redis.

**Week 4 (Nov 16 – 22): Basic RAG**
- Day 16: Embeddings, cosine similarity, dimensions. Task: embed 50 sentences; numpy nearest-neighbor search.
- Day 17: Chunking (size, overlap, structure-aware, metadata). Task: ingest a markdown docs set.
- Day 18: Vector stores (pgvector, Chroma, Redis), HNSW concept. Task: store and query top-k.
- Day 19: RAG pipeline with citations and "I don't know." Task: Q&A CLI with sources.
- Day 20: Hybrid search, reranking, query rewriting, recall@k. Task: 15 Q&A pairs; recall@5 before/after hybrid.
- Weekend: RAG CLI repo with README; Month 1 summary.

### Month 2: Agent patterns, memory, observability, evals

**Week 5 (Nov 23 – 29): Agent patterns**
- Day 21: Workflows vs agents; the core patterns ("Building effective agents"). Task: notes mapping each to a backend analogy.
- Day 22: Prompt chaining and routing. Task: classifier-router to specialized prompts.
- Day 23: Parallelization and orchestrator-workers. Task: split, run concurrently, merge.
- Day 24: Evaluator-optimizer and reflection. Task: writer + critic loop with stopping rules.
- Day 25: ReAct, plan-and-execute, failure modes. Task: ReAct agent with scratchpad and loop detection.
- Weekend: Rebuild one agent in LangGraph and one agent SDK; compare to from-scratch.

**Week 6 (Nov 30 – Dec 6): Memory and state**
- Day 26: Memory types (context, scratchpad, episodic, semantic, summaries). Task: notes and sketch.
- Day 27: Sliding windows, rolling summaries, compaction. Task: rolling summarization in the chat agent.
- Day 28: Long-term memory, write policies, embedding retrieval. Task: memory store in Redis/pgvector via tools.
- Day 29: Durable state, checkpoints, resumability. Task: persist to Redis each step; kill and resume.
- Day 30: Session isolation, contextvars, locking. Task: FastAPI agent with per-session state and request ids.
- Weekend: Stateful research assistant with memory and crash recovery.

**Week 7 (Dec 7 – 13): Observability**
- Day 31: Nested spans for LLM and tool calls; OpenTelemetry GenAI conventions. Task: notes mapped to request-id propagation.
- Day 32: Manual instrumentation (model, tokens, latency, cost). Task: OpenTelemetry + Jaeger.
- Day 33: Langfuse, LangSmith, Arize Phoenix. Task: self-host Langfuse; send traces.
- Day 34: Safe prompt logging, PII redaction, debugging trajectories. Task: diagnose 3 failed runs from traces.
- Day 35: Tokens/request, cost/task, tool error rate, p50/p95, TTFT. Task: dashboard.
- Weekend: Write-up, "Tracing agents, explained for backend engineers."

**Week 8 (Dec 14 – 20): Evals**
- Day 36: Golden datasets, offline vs online. Task: 30-case eval set.
- Day 37: Programmatic graders, LLM-as-judge, pairwise, judge bias. Task: one of each grader.
- Day 38: Task success, tool-use correctness, steps, cost. Task: trajectory-scoring harness.
- Day 39: promptfoo, Braintrust, Inspect, Langfuse evals; CI. Task: evals in GitHub Actions on PRs.
- Day 40: Error analysis, regressions, comparisons. Task: 2 changes compared and written up.
- Weekend: Month 2 summary; pick the Month 3 project.

### Month 3: Production concerns, MCP, polished project

**Week 9 (Dec 21 – 27): Cost, latency, caching**
- Day 41: Token costs, model tiers, routing. Task: cost report; route easy requests to a small model.
- Day 42: TTFT vs total latency, parallel tools. Task: per-span latency breakdown; cut p95.
- Day 43: Provider prompt caching. Task: enable and measure.
- Day 44: Exact and semantic caching, invalidation. Task: semantic cache; hit rate and wrong-hit rate.
- Day 45: Batch APIs, queues, rate limiting. Task: queue-backed workers (BullMQ or Celery).
- Weekend: Scope the project; start the parallel track.

**Week 10 (Dec 28 – Jan 3): Guardrails and security**
- Day 46: Prompt injection, exfiltration, tool misuse, OWASP Top 10 for LLM apps. Task: attack own RAG with poisoned docs.
- Day 47: Input/output guardrails. Task: add checks to the agent.
- Day 48: Least privilege, human-in-the-loop, sandboxing. Task: Docker-sandboxed code tool.
- Day 49: Budget caps, fallbacks, graceful degradation. Task: budget cap and fallback model.
- Day 50: Red-teaming as evals, PII in logs. Task: add injection and PII cases to evals.
- Weekend: Project core loop and RAG.

**Week 11 (Jan 4 – 10): MCP**
- Day 51: Hosts, clients, servers; tools, resources, prompts; stdio vs streamable HTTP. Task: connect an existing server to Claude Desktop/Code.
- Day 52: Build an MCP server. Task: 2 backend tools; test with MCP Inspector.
- Day 53: MCP client side. Task: own agent uses own server.
- Day 54: Remote MCP, auth, third-party risk. Task: deploy behind auth.
- Day 55: Agent SDKs, computer use, agent-to-agent protocols. Task: wire MCP into the project.
- Weekend: Project evals and tracing.

**Week 12 (Jan 11 – 17): Polish and ship**
- Day 56: Architecture diagram and README.
- Day 57: Evals in CI with a pass threshold.
- Day 58: Observability dashboard and cost-per-task report.
- Day 59: Deploy; 3-minute demo.
- Day 60: Write-up; resume update; shortlist target roles.
- Weekend: Retro; plan phase 2 (role prep).

### Parallel track (weekend slot, about 3 hours/week)

| Week | Math | Zero to Hero / PyTorch |
| --- | --- | --- |
| 9 | 3Blue1Brown, Essence of Linear Algebra, episodes 1–5 | — |
| 10 | 3Blue1Brown, Essence of Calculus (derivatives, chain rule) | micrograd |
| 11 | Linear algebra, remaining core episodes (dot products, change of basis) | makemore part 1 (bigram) |
| 12 | Probability basics: distributions, expectation, softmax, cross-entropy | PyTorch "Learn the Basics"; makemore part 2 (MLP) |
| After 12 | As needed | Remaining makemore, "Let's build GPT," tokenizer video |

---

## 6. How the living-doc workflow runs

**Structure of the doc (in order):**
1. Title and byline (as-of date, author).
2. Overview: goal, phase table, starting strengths, learning style, time assumption.
3. How to use this doc.
4. Current status: next day, days completed out of 60, current build, carried-over items.
5. Month 1, Month 2, Month 3 sections: one-line outcome, then one table per week with columns Day | Concept | Hands-on task, plus a Weekend row.
6. Parallel track table.
7. Progress log: table with Date | Day(s) | What was done | Notes / carried over, newest first.

**Updating it:**
- The learner reports progress in chat in plain words (e.g. "did Day 3, skipped the semaphore part").
- Claude then updates three places: **Current status** (moves to the real position), the **day table** (marks the cell, e.g. "Day 3 (done Oct 1)" or "Day 3 (partial)"), and the **Progress log** (new row on top).
- Comments left in the doc can be sent to Claude; Claude makes the change and replies in that comment thread.
- The plan flexes: topics that take longer shift the rest; familiar ones get compressed.

**Across chats:**
- Each new chat starts fresh. Put the doc link in the Claude Project's custom instructions with a line like "Read and update this progress doc when I report what I've done," or paste the link at the start of a chat.
- Exported or copied versions (Google Docs, PDF, Markdown) are snapshots and don't receive later updates.

---

## 7. Regenerating the doc

To rebuild the doc, give Claude this file with a prompt like:

> Using this context file, create a living doc titled "AI Agentic Learning: Daily Plan & Progress" with the structure in section 6 and the day plan in section 5. Keep the finalized decisions in section 4. Set Current status from my latest progress, or "Not started" if none.

If progress already exists, include the latest Progress log rows so the rebuilt doc picks up where the old one left off.
