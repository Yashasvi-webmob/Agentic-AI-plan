import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import tiktoken

load_dotenv()
STARTING_OVERHEAD = 64
PER_MESSAGE_ADJUST_OVERHEAD = 5
BUDGET_TOKENS = 300


def call_model(client: OpenAI, temp: float, prompt: list[dict]):
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        max_tokens=900,
        temperature=temp,
        messages=prompt,
    )
    return {
        "usage": resp.usage,
        "finish_reason": resp.choices[0].finish_reason,
        "content": resp.choices[0].message.content,
    }


def read_json():
    with open("msgs_just_sys_prompt.json", encoding="utf-8") as f:
        data = json.load(f)
        messages = data["messages"]
        return messages


def estimate_message_tokens(enc, messages: []):
    totalTokens = STARTING_OVERHEAD
    for message in messages:
        estimate = enc.encode(message["content"])
        totalTokens = totalTokens + len(estimate) + PER_MESSAGE_ADJUST_OVERHEAD
    return totalTokens


def trim_based_on_estimate(encoding, messages):
    messages_deleted= 0
    while True:
        estimate = estimate_message_tokens(encoding, messages)
        if estimate > BUDGET_TOKENS and len(messages) > 3:
            del messages[1:3]
            messages_deleted = messages_deleted + 2
        else:
            break
    if messages_deleted>0:
        print(f"Messages Deleted: {messages_deleted}")

def main():
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    enc = tiktoken.get_encoding("o200k_base")
    messages = read_json()

    while True:
        try:
            input_text = input("Ask here :>")
        except (json.JSONDecodeError, EOFError, KeyboardInterrupt) as e:
            print("Goodbye:", e)
            return
        input_value = input_text.strip()
        if input_value == "exit":
            break
        if not input_value:
            continue
        messages.append({"role": "user", "content": input_value})
        trim_based_on_estimate(enc, messages)
        estimated_tokens = estimate_message_tokens(enc, messages)
        result = call_model(client, 0.8, messages)
        print(f"finish_reason:{result['finish_reason']}")
        print(f"usage: {result['usage']}")
        if result["finish_reason"] == "length" or not result["content"]:
            print("Warning: reply cut off, try again")
            messages.pop()
            continue
        print("Response:")
        print(result["content"])
        print(
            f"Estimated tokens: {estimated_tokens}, Actual Tokens:{result['usage'].prompt_tokens}, Gap: {estimated_tokens - result['usage'].prompt_tokens}"
        )
        messages.append({"role": "assistant", "content": result["content"]})
        


if __name__ == "__main__":
    main()
