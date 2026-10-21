import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
resp = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    max_tokens=500,
    temperature=1,
    messages=[
        {"role": "system", "content": "You are a terse senior backend engineer."},
        {"role": "user", "content": "Explain backpressure in one sentence."},
    ],
)
print(resp.choices[0].message.content)
print(resp.choices[0].finish_reason)
print(resp.usage)   