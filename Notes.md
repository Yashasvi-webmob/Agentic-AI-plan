# My notes

Things I actually found out while building, in plain words. Newest day first.

---
## Day 5 : Multi Turn Chat, Statelessness and model memory
    Model has no memory of its own, picks from whatever chat you pass to it. If i ask what is my name , and in the same prompt i haven't given my name anywhere, it won;t be able to go back to previous chats and pick that name, even if it was present there.
    Takes less token for refusal/forgot case.

### What I built
A chat CLI (`day05/main.py`). It keeps the whole conversation in a list and sends the list on every call. Before each call it estimates the token count with `tiktoken`, and if the list is over a token budget it drops the oldest question-and-answer pairs.

### Test 1: with history vs without

| | Full history | Only the system prompt and the last question |
|---|---|---|
| "What club am I a fan of?" | "You're a Barcelona fan." | "I'm sorry, but I can't help with that." |
| Prompt tokens | 272 | 157 |

- Same system prompt and same question. Only the history differed, so the history I send is the only place the model learns anything about me.
- The answer without history was a refusal, not "I don't know", because my system prompt says to answer football-coach questions only. A refusal and a "forgot" look the same, so I should say "couldn't answer".
- The history cost 115 tokens, and it is resent on every turn.

### A bug I found: the reply was added to the history twice
- My first 7-turn chat had `prompt_tokens` of 124, 344, 485, 821, 897, 1048, 1217. Each turn rose by about **double** what the new question and the last reply were worth (e.g. +220 when a plain count said about 100).
- Cause: two lines both appended the assistant reply, so every reply was in the history twice.
- After deleting one, the same kind of chat gave 131, 163, 187, 262, 301, 354, 401. Each rise is now about one reply plus one question plus roughly 10 tokens.
- So the first run's totals (4,936 input tokens against 1,081 output) were inflated by the bug. Lesson: when a token count looks too big, check what is really in the list.

### The token estimate: how wrong it was and how I fixed it
With `tiktoken` (`o200k_base`) and 4 tokens per message, my estimate was always too low:

| Turn | My estimate | Real prompt tokens | Gap |
|---|---|---|---|
| 1 | 65 | 131 | -66 |
| 2 | 95 | 163 | -68 |
| 3 | 117 | 187 | -70 |
| 4 | 190 | 262 | -72 |
| 5 | 227 | 301 | -74 |
| 6 | 278 | 354 | -76 |
| 7 | 323 | 401 | -78 |

- The gap was exactly `64 + number of messages`. So there is a **fixed 64 tokens** that the provider adds to every request (a hidden header), and the real cost per message is **5, not 4**.
- With `64 + 5 per message` the gap is **0** on every turn I checked: 127/127, 159/159, 183/183, and 133/133 after trimming.
- The 64 belongs to this provider and model. If I change either, I have to measure it again.
- Counting only the new question (what I tried first) tells me nothing. What matters is the whole list that is sent.

### Test 2: trimming to a budget, and forgetting
Budget: 300 tokens (the estimate includes the 64). The chat went: my name, "what's your name", "what's your career" (the model answered with a big table), then a question about Arsenal and Barcelona.

- Before that fourth question the code printed `Messages Deleted: 6`, and `prompt_tokens` went **down** from 183 to 133. Only the system prompt and my new question were left.
- Why all 6 and not just the oldest pair: the career table was about 270 tokens, almost the whole budget on its own. After the two name pairs were gone the list was still over budget, so the table's pair was removed too.
- Then "what is my name?" got "I don't have that information." That is forgetting working: the model knew my name while that pair was in the list.
- The Arsenal and Barcelona question got a confident "No, I didn't coach the same player at both", although the table that mentioned those clubs had just been deleted. It had no basis for the answer and invented one. For a fact about me it declined, for a fact about its made-up career it made something up.
- The system prompt survived the trim, and the persona stayed.

### What I learned
- The model has no memory. Whatever it "remembers" is the list I resend, and it costs tokens on every turn.
- Trimming by age keeps the size down, but it ignores importance. The oldest pair went first (my name), but so did the long answer the next question depended on.
- One long message can push out everything older. With a 300 budget, a single table cleared the whole history. Real budgets are bigger, but the effect is the same.
- The model builds on its own earlier statements, true or not. It invented a career, then agreed with my wrong claim about Conte and contradicted itself ("I stepped in after him"). Same pattern as Day 4: it fills gaps and goes along with the user.
- A failed reply (`finish_reason: length`) must not enter the history. I remove my question again so the list keeps alternating user and assistant.

### Decisions I made
- If one message alone is bigger than the whole budget, the trim stops at the system prompt plus that message and sends it anyway, with no warning.
- If a reply fails, my question is removed again, but pairs the trim already dropped for that turn stay dropped.

### Python things that bit me
- `json.load(f)` parses an open file. `json.loads(s)` parses a string. And `f["messages"]` on the file object does nothing, I have to parse first.
- `except A or B` catches only `A`. For several exceptions, use a tuple: `except (A, B):`. A list in `[ ]` there crashes only when an exception happens.
- `x is "exit"` compares identity. Use `==`. `input()` gives `""` for an empty line, never `None`, so test `if not value:`.
- `enc.encode(...)` returns a **list** of token ids, so the count is `len(...)`. It takes a string, not a dict.
- Braces, `&&` and `delete` are JS. In Python: a colon and indentation, `and`, and `del messages[1:3]` to remove items in place.
- `tiktoken.get_encoding("o200k_base")` takes an encoding name. `encoding_for_model` only knows OpenAI's own model names.

### Still to check
- [ ] Which file did the no-history run use? `msgs_forget.json` has one Q&A in it, so the 115 tokens may be 6 messages (about 19 each) and not 8.
- [ ] Does a `finish_reason: length` reply really leave the list clean? (Try `max_tokens` 50.)
- [ ] Would trimming by size (drop the biggest old reply first) or a summary keep more? Week 6 covers summaries.

## Day 4: prompt best scenarios and working
Setting reference of large text in a small prompt type template.

If the question does not have a proper reference from the text the model was asked to reference, it fills the gap, not necessarily accurately instead of saying that this question can't be answered based on reference text. This needs explicit direction.

The 1.5 temp run is the only one which gave a summary response, along with the 4 bullets, rest temp=0 and temp=0.7 scenario resulted in 4 bullets, with no summary.

### The three runs (v1 prompt, same article, one run each)

| Temp | Format (asked for exactly 4 bullets, 15 words max each) | Completion tokens | Reasoning tokens | Reasoning share |
|---|---|---|---|---|
| 0 | 4 bullets, all short | 468 | 406 | 87% |
| 0.7 | 4 bullets, all short | 712 | 639 | 90% |
| 1.5 | 4 bullets **plus** a bold heading and a 2-sentence paragraph | 1010 | 862 | 85% |

Every call used 1162 prompt tokens (the article is most of that) and ended with `finish_reason: stop`. The three calls together used about 5,700 tokens, so they fit under the 8,000 per minute limit.

- **85-90% of the output is hidden reasoning.** The visible answer is only about 60-150 tokens. I pay for the thinking, and I never see it.
- **Reasoning tokens went up with temperature (406, 639, 862),** but this is one run each. On Day 1 the count also moved around at temperature 0, so I can't call it a rule yet. To check: run each temperature 2-3 times.
- **High temperature broke the format rule.** "Answer in exactly 4 bullet points" did not stop the model adding a heading and a paragraph at 1.5. An instruction is a request, not a guarantee, and it holds less well the more random the sampling is.

### Mistakes the format check can't catch
The bullet count was fine at temp 0 and 0.7, but the meaning was wrong in places:
- **Meaning flipped (temp 0.7):** "Promoter selling signals undervaluation". The article says the opposite: promoters sell because they think the market is paying too much for their companies.
- **Cause and effect reversed (temp 0):** "Large-cap ownership hit 14-year low, prompting FII exit". In the article the low ownership is the result of the FIIs selling, not the reason for it.
- **The question and the article don't match (all three temps):** the article explains how the market absorbed the selling, and says the Finance Minister's remark doesn't explain why FIIs sell. All three answers still gave "easy liquidity" as the reason FIIs sell.

So temperature changed the style and the cost, but it did not cause or fix these errors. The prompt did. Checking the format is easy (count the bullets). Checking the facts means reading the article.

### Prompt-writing lessons so far
- Counting bullets is not the same as checking the answer. A summary can look perfect and be wrong.
- If the question presumes something the text doesn't say, the model fills the gap. It needs an explicit way out: "if the article doesn't say, answer that it doesn't".
- A format rule needs to say what **not** to add, e.g. "output only the 4 bullets, no heading, no extra text".
- Print labels matter: my `Response - content` label put a dash right next to the first bullet's dash, and I miscounted the bullets at first.

### v1 vs v2 (same article; v1 ran once per temperature, v2 ran three times; each run goes 0.7, 0, 1.5)

What changed in v2:
- System prompt got an exit: "if a question can't be answered from the context, say so".
- User prompt got "only the bullets, no heading, no tags", "use only facts from the article", and one worked example (made-up article, question, 4 bullets). The example includes a cause-and-effect sentence (effect written first) and a bullet that reads it in the right order, plus one "article doesn't mention this" bullet.

v2 token counts, three runs (completion / reasoning). v1 is one run.

| Temp | v1 | v2 run 1 | v2 run 2 | v2 run 3 |
|---|---|---|---|---|
| 0 | 468 / 406 | 601 / 547 | 604 / 550 | 604 / 550 |
| 0.7 | 712 / 639 | 726 / 651 | 496 / 438 | 653 / 590 |
| 1.5 | 1010 / 862 | 607 / 537 | 579 / 499 | 534 / 440 |

What the 9 v2 samples showed (3 per temperature):

| Check | 0.7 | 0 | 1.5 |
|---|---|---|---|
| Exactly 4 bullets, no extra text, 15 words or fewer | 3/3 | 3/3 | 3/3 |
| Cause and effect reversed | 2/3 | 0/3 | 0/3 |
| "Article doesn't say" exit used | 0/3 | 0/3 | 0/3 |
| Finance Minister's remark credited correctly | 0/3 | 0/3 | 1/3 |
| Promoter role misread (sellers "enable/ease" absorption) | 2/3 | 0/3 | 0/3 |

- **Cost of the example:** prompt tokens went from 1162 to 1515 (+353, about 30%), and that is paid on every call. Each run of three calls used about 6,200-6,500 tokens, close to the 8,000 per minute limit.
- **Format: fixed, as far as I can tell.** 9 of 9 gave exactly 4 bullets with no heading, paragraph or tags, including 3 of 3 at 1.5, where v1 broke. v1 only ran once per temperature, so I can say it holds reliably on this article, not what the real failure rate is.
- **Temperature 0 repeats the same answer, not a correct one.** All three runs gave the same visible bullets, and the reasoning tokens barely moved (547, 550, 550). So its weak points repeat every time: the minister's quote stated as fact, and "retail participation fuels FII exits" where the article says retail inflows allowed the selling. A stable answer can be consistently wrong.
- **Reasoning no longer rises with temperature.** Ranges in v2: 0 gave 547-550, 0.7 gave 438-651, 1.5 gave 440-537 (averages about 550, 560, 492). So v1's rising pattern (406, 639, 862) was one sample, not a rule. What temperature seems to change is the spread: temperature 0 is steady and 0.7 jumps around. Reasoning is 82-91% of the output.
- **Cause and effect: not fixed.** At 0.7 it came back in 2 of 3 runs ("ownership fell to a 14-year low, prompting FII divestments" and "...encouraging divestment"), even though the example showed the right order. It only appeared when the model joined two facts with a verb like "prompting". When the bullet just stated the fact ("hit a 14-year low"), there was no reversal. That is a guess from 3 samples, not proof.
- **The "article doesn't say" exit: never used (0 of 9).** The article opens with the Finance Minister's quote as the explanation and ends by saying it explains nothing, so the gap is not obvious. The exit worked in my example because the gap there was obvious.
- **Attribution goes wrong in a pattern.** Only 1 of 9 answers credits the Finance Minister. Four said "FIIs cite..." (wrong speaker) and four stated the remark as plain fact. The 15-word limit probably squeezes out "Finance Minister".
- **The undervaluation flip is gone, but by absence.** No run clearly says why promoters sell, so nothing was fixed, the bullets just went elsewhere.
- **New errors v1 did not have:** "Promoter sales enable/ease market absorption" (promoters are sellers, retail buyers absorb), "Promoters... encouraging FII exits" (the article never says this), and "NRI inflows" (the article never mentions NRIs).
- **Lesson:** a prompt controlled the shape of the answer reliably, and the facts only partly. Shorter bullets forced compression, and compression brought new mistakes. Only reading the article catches these. 9 samples cannot give failure rates, and real confidence needs dozens of runs with automatic scoring. That is the reason evals exist (Week 8).

Still to check:
- [x] Run v2 two more times: format held at 1.5 (3 of 3), the reversal came back at 0.7, the exit never appeared
- [ ] Optional: run v1 two or three more times at 1.5, so the v1 vs v2 format comparison is fair

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
