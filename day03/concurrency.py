import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import asyncio
import time

load_dotenv()


async def concurrent_calls(alphabet: str, sem: asyncio.Semaphore, client: AsyncOpenAI) -> dict:
    async with sem:
        resp = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=500,
            temperature=1,
            messages=[
                {"role": "system", "content": "You are a junior high teacher."},
                {
                    "role": "user",
                    "content": f"Name a historical event starting with the letter {alphabet}.No description needed.",
                },
            ],
        )
        return {
            "letter": alphabet,
            "usage": resp.usage,
            "reason": resp.choices[0].finish_reason,
            "content": resp.choices[0].message.content,
        }


async def run_batch(letters, client, num_semp):
    sem = asyncio.Semaphore(num_semp)  # 1. built once, shared by everyone
    coros = [concurrent_calls(i, sem, client) for i in letters]  # 2. 10 coroutines
    start = time.perf_counter()
    results = await asyncio.gather(*coros)  # 3. run them all
    elapsed = time.perf_counter() - start
    return results, elapsed


async def main():
    client = AsyncOpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    letters = "abcdefghij"
    records = []
    for conc_calls in [1, 3, 10]:
        results, elapsed = await run_batch(letters, client, conc_calls)
        records.append({"conc_calls": conc_calls, "elapsed": elapsed})
        for r in results:
            print(
                f"alphabet: {r['letter']}, content:{r['content'][:40]}, finish_reason:{r['reason']}, token_usage:{r['usage'].total_tokens}, queue_time:{r['usage'].queue_time:.2f}"
            )
        print(f"Time Elapsed:{elapsed:.2f}s")
    for record in records:
        print(
            f"Concurrent Calls: {record['conc_calls']}, Time elapsed: {record['elapsed']:.2f}s"
        )


if __name__ == "__main__":
    asyncio.run(main())
