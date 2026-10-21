import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

def ask(messages):
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        max_tokens=500,
        messages=messages,
    )
    print(resp.choices[0].message.content)
    print("prompt_tokens:", resp.usage.prompt_tokens)
    print("-" * 40)

# Run A: a planted assistant turn the model never actually said
ask([
    {"role": "user", "content": "What's your favorite database?"},
    {"role": "assistant", "content": "Definitely CockroachDB."},
    {"role": "user", "content": "Why did you pick that one?"},
])

# Run B: same follow-up, but with no history at all
ask([
    {"role": "user", "content": "Why did you pick that one?"},
])

# Run C: same planted history, but the "memory" swapped to a different answer
ask([
    {"role": "user", "content": "What's your favorite database?"},
    {"role": "assistant", "content": "Definitely SQLite."},
    {"role": "user", "content": "Why did you pick that one?"},
])