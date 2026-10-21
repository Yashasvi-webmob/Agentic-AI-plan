import os, httpx
from dotenv import load_dotenv
load_dotenv()

resp = httpx.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
    json={
        "model": "openai/gpt-oss-20b",
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": "You are a terse senior backend engineer."},
            {"role": "user", "content": "Explain backpressure in one sentence."},
        ],
    },
    timeout=30,
)
data = resp.json()
print(data["choices"][0]["message"]["content"])
print(data["choices"][0]["finish_reason"], data["usage"])
