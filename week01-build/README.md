# Week 1 build
Terminal chat, tracking token behavior, cost and prompt behaviour determined by budget and config variables.

* Setup: uv sync, ,env with GROQ_API_KEY=...
* Running: uv run main.py
* Config: a dict holding values for the variables 
* Log: A .jsonl file holding each prompt token and other details, differentiated by session_id
* Stats script: Check logstat.py, run by uv run logstat.py --<all> or --<session_id>
* Known limits, budget is set, so trimming of messages done according to its value. 