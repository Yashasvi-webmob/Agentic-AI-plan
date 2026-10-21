# Agentic AI learning repo

I'm Yashasvi, a backend engineer (Node.js: streams, buffers, cluster/workers, IPC, Redis shared state, AsyncLocalStorage) working through a 12-week plan to move into agentic AI roles, then toward core ML.

Full context, rationale, finalized decisions, and the canonical day-by-day plan:
@agentic-ai-learning-context.md

## How to help me

- One topic per day: explain the concept first, then the small hands-on task. Relate new ideas to my backend experience where it genuinely helps.
- Builds default to Python (managed with `uv`); Node only where my existing depth makes the concept clearer.
- Time budget: about 1 hour on weekdays, one 3–4 hour weekend session. Unfinished weekday tasks roll into the weekend.
- LLM provider: Groq free tier via the OpenAI SDK (`base_url="https://api.groq.com/openai/v1"`, key in `.env` as `GROQ_API_KEY`), model `openai/gpt-oss-20b`. It's a reasoning model, so leave room in `max_tokens` for hidden reasoning tokens. I don't have a paid Claude API key, so adapt Anthropic-format examples to the OpenAI-compatible format.
- In every script that calls a model, print `finish_reason` and `usage`.
- Don’t write the full code for me; give hints and review what I   write.
## Repo layout

- One folder per day: `day01/`, `day02/`, ... Weekend builds get their own folder (e.g. `week01-build/`).
- `.env` holds `GROQ_API_KEY` and is never committed.

## Progress tracking

The source of truth is the living doc "AI Agentic Learning: Daily Plan & Progress":
https://claude.ai/artifact/1jeJSL6LVrPWyQB8pJnnHw (doc ID `05f439c5-a05c-4d47-ba44-061a40ee5262`)

When I report finished work:
1. If Claude Docs tools are available in this session, update the doc directly: mark the day in its week table (e.g. "Day 2 (done Oct 22)"), update the Current status section, and add a row at the top of the Progress log (Date | Day(s) | What was done | Notes / carried over).
2. If they aren't available, add the same row to `PROGRESS.md` in the repo root (create it if missing, newest first) and remind me that the doc needs syncing.

## Current status (as of Oct 21, 2026)

- Day 1 done: API basics via raw httpx and the OpenAI SDK against Groq; truncation, system prompt, statelessness, and temperature experiments.
- Next: Week 1, Day 2 (Python for Node devs).
- Week dates were reset on Oct 21: Week 1 runs Oct 21 – Nov 1, Week 12 ends Jan 17, 2027.


