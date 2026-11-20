import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import tiktoken
import pathlib
import time

config_path = pathlib.Path(__file__).parent / "config.json"

with open(config_path, encoding="utf8") as f:
    config = json.load(f)

load_dotenv()
STARTING_OVERHEAD = config["starting_overhead"]
PER_MESSAGE_ADJUST_OVERHEAD = config["per_message_overhead"]
BUDGET_TOKENS = config["budget_tokens"]


def write_log(log: dict):
    with open(config["log_file"], mode="a", encoding="utf8") as f:
        f.write(json.dumps(log) + "\n")


def call_model(client: OpenAI, temp: float, prompt: list[dict]):
    resp = client.chat.completions.create(
        model=config["model"],
        max_tokens=config["max_tokens"],
        temperature=temp,
        messages=prompt,
    )
    return {
        "usage": resp.usage,
        "finish_reason": resp.choices[0].finish_reason,
        "content": resp.choices[0].message.content,
    }


# def read_json():
#     with open(config["system_prompt"], encoding="utf-8") as f:
#         data = json.load(f)
#         messages = data["messages"]
#         return messages


def estimate_message_tokens(enc, messages: []):
    totalTokens = STARTING_OVERHEAD
    for message in messages:
        estimate = enc.encode(message["content"])
        totalTokens = totalTokens + len(estimate) + PER_MESSAGE_ADJUST_OVERHEAD
    return totalTokens


def trim_based_on_estimate(encoding, messages):
    messages_deleted = 0
    while True:
        estimate = estimate_message_tokens(encoding, messages)
        if estimate > BUDGET_TOKENS and len(messages) > 3:
            del messages[1:3]
            messages_deleted = messages_deleted + 2
        else:
            break
    if messages_deleted > 0:
        print(f"Messages Deleted: {messages_deleted}")


def main():
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    enc = tiktoken.get_encoding(config["encoding"])
    messages = [config["system_prompt"]]
    turn = 0
    while True:
        try:
            input_text = input("Ask here :>")
        except (json.JSONDecodeError, EOFError, KeyboardInterrupt) as e:
            print("Goodbye:", e)
            break
        input_value = input_text.strip()
        if input_value == "exit":
            break
        if not input_value:
            continue
        messages.append({"role": "user", "content": input_value})
        trim_based_on_estimate(enc, messages)
        estimated_tokens = estimate_message_tokens(enc, messages)
        start = time.perf_counter()
        result = call_model(client, config["temperature"], messages)
        elapsed = time.perf_counter() - start

        print(f"Latency For Model Call: {elapsed}")
        turn = turn + 1
        new_record = {
            "session_id":time.time() + "_"+ turn,
            "timestamp": time.time(),
            "turn": turn,
            "finish_reason": result["finish_reason"],
            "prompt_tokens": result["usage"].prompt_tokens,
            "completion_tokens": result["usage"].completion_tokens,
            "reasoning_tokens": result[
                "usage"
            ].completion_tokens_details.reasoning_tokens
            or 0,
            "total_tokens": result["usage"].prompt_tokens
            + result["usage"].completion_tokens,
            "estimated_tokens": estimated_tokens,
            "gap": estimated_tokens - result["usage"].prompt_tokens,
            "latency":elapsed,
        }
        write_log(new_record)

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
