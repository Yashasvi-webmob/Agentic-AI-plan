# My notes

Things I actually found out while building, in plain words. Newest day first.

---

## Day 3: asyncio, a concurrency limit, and Groq's rate limit

What I built: 10 LLM calls, run three ways (one at a time, 3 at once, 10 at once), timed each.

| Limit | Time | Speed-up vs one at a time |
|---|---|---|
| 1 (one at a time) | 9.06 s | 1x |
| 3 | 2.28 s | 4.0x |
| 10 | 1.16 s | 7.8x |

(Best run. An earlier run gave 8.75 s / 2.63 s / 3.83 s, see below.)

- **The semaphore speeds things up as expected.** With 3 slots, 10 calls take about a third of the time (slots free up one by one, so it is not strict waves). Same idea as a worker pool in Node. At limit 10 the whole batch took about as long as the slowest single call (1.16 s).
- **The 4.0x is probably flattered by a cold start.** Limit 1 always runs first, so it pays for opening the connection (DNS, TCP, TLS), and the later batches reuse it. Simple concurrency should give about 3.3x at most. To check: make one throwaway call before the loop, or run the limits in the order 10, 3, 1.
- **One earlier run had limit 10 slower than limit 3 (3.83 s vs 2.63 s).** I guessed Groq was queuing the burst, but `usage.queue_time` says no: it was 0.05-0.54 s per call at every limit, with no increase at limit 10. So that run was most likely a one-off (variance or a hidden retry). Lesson: repeat a timing before believing it.
- **`queue_time` is only the wait inside Groq,** before the model starts. It does not include my own semaphore wait.
- **The free tier limits tokens, not just requests.** `openai/gpt-oss-20b` allows 8,000 tokens per minute (TPM). Each call also reserves its `max_tokens` up front (about 500), so a burst can get rejected even when the answers themselves are short. My first full run hit a 429 on the third batch: 7,971 already used, 501 requested.
- **The SDK retries 429s by itself, twice.** After that it gives up and raises `RateLimitError`. So a slow call can hide a retry. Turn on `OPENAI_LOG=info` to see `retries_taken`.
- **`gather` throws away the good results when one call fails.** It raises the first error and the other 9 answers are lost (and their tokens are already spent). `return_exceptions=True` keeps them.
- **`finish_reason: length` can happen on a trivial prompt.** With `max_tokens=500` and the longer prompt, two of ten calls were cut off at exactly 591 tokens (91 prompt + 500 output). The hidden reasoning tokens eat into the budget. Asking for "one short sentence" fixed it and cut tokens per call from about 350-550 down to about 150-250.

### Python things that bit me today
- Forgetting `await` doesn't run anything: the call just gives back a coroutine object. In Node the work would have started anyway.
- `finish_reason` is on `resp.choices[0]`, not on `resp`.
- `{a, b}` is a set, `{"a": a, "b": b}` is a dict. Same braces, very different thing.
- A dict uses `d["key"]`, never `d.key` or `d.["key"]`.
- `await` only works inside `async def`, and `asyncio.run(main())` starts the loop for you. Node starts it automatically.

### Still to check
- [x] `queue_time` per call at limit 10 vs limit 3: no difference, Groq was not queuing
- [x] Repeat limit 10: 1.16 s this time, so the 3.83 s run was a one-off
- [ ] Is the 4.0x partly a cold start? (warm-up call first, or run in the order 10, 3, 1)
- [ ] Why was that one run slow? A hidden retry would show up with `OPENAI_LOG=info`

---

## Day 2: Python for Node devs (the logstat CLI)

- A Python **dict** is not a JS object. A missing key raises `KeyError` instead of giving `undefined`. Use `d.get("k", default)` when the key may be absent.
- **Empty things are falsy** in Python (`[]`, `{}`, `""`, `0`, `None`), unlike JS where `[]` and `{}` are truthy. `if not records:` means "the list is empty".
- **`x is None` vs `if x:`** are different questions: "is there a value?" vs "is it non-empty?". An empty set is not `None`, which cost me a bug.
- **Sets have maths operators.** `NEEDED - record.keys()` gives the missing keys. An empty result means nothing is missing.
- **Keep the `try` small.** Only wrap the line that can raise, and name the exception you expect (`except FileNotFoundError`, never a bare `except`).
- **Exit codes matter.** `sys.exit(1)` and an error message on `stderr` for failures. `return` from `main()` exits with 0, which looks like success.
- **Layering:** `parser.py` turns one line into one record, `stats.py` turns a list of records into numbers (no files, no printing), `cli.py` glues them and prints. Validate at the edge (the parser) and trust the data after that.
