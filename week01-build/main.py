import os
from openai import OpenAI, APIError
from dotenv import load_dotenv
import json
import tiktoken
import pathlib
import time
import sys

config_path = pathlib.Path(__file__).parent / "config.json"

REQUIRED_KEYS = {
    "encoding",
    "model",
    "max_tokens",
    "budget_tokens",
    "starting_overhead",
    "per_message_overhead",
    "temperature",
    "log_file",
    "input_price_per_million",
    "output_price_per_million",
    "system_prompt",
}

def load_config(path):
    try:
        with open(path, encoding="utf8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"Config is not valid JSON: {e}")
    missing = REQUIRED_KEYS - cfg.keys()
    if missing:
        sys.exit(f"Config is missing keys: {sorted(missing)}")
    return cfg

config = load_config(config_path)

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


def calc_tokens_cost(completion_tokens, prompt_tokens):
    return (
        prompt_tokens * config["input_price_per_million"]
        + completion_tokens * config["output_price_per_million"]
    ) / 1000000


def trim_based_on_estimate(encoding, messages):
    messages_deleted = 0
    while True:
        estimate = estimate_message_tokens(encoding, messages)
        if estimate > BUDGET_TOKENS and len(messages) > 3:
            del messages[1:3]
            messages_deleted = messages_deleted + 2
        else:
            break
    # if messages_deleted > 0:
    #     print(f"Messages Deleted: {messages_deleted}")
    return messages_deleted


def main():
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    enc = tiktoken.get_encoding(config["encoding"])
    messages = [config["system_prompt"]]
    turn = 0
    session_id = str(time.time())
    calls = 0
    failed_calls = 0
    total_prompt = 0
    total_completion = 0
    total_reasoning = 0
    total_cost = 0.0
    total_gap = 0
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
        messages_deleted = trim_based_on_estimate(enc, messages)
        estimated_tokens = estimate_message_tokens(enc, messages)
        turn = turn + 1
        start = time.perf_counter()
        try:
            result = call_model(client, config["temperature"], messages)
        except APIError as e:
            elapsed = time.perf_counter() - start
            print(f"API call failed: {type(e).__name__}")
            write_log(
                {
                    "session_id": session_id,
                    "timestamp": time.time(),
                    "turn": turn,
                    "finish_reason": "error",
                    "error": type(e).__name__,
                    "latency": elapsed,
                    "messages_deleted": messages_deleted,
                }
            )
            failed_calls += 1
            messages.pop()
            continue
        elapsed = time.perf_counter() - start

        print(f"Latency For Model Call: {elapsed}")
        # turn = turn + 1
        cost = calc_tokens_cost(
            result["usage"].completion_tokens, result["usage"].prompt_tokens
        )
        new_record = {
            "session_id": session_id,
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
            "latency": elapsed,
            "tokens_cost": cost,
            "messages_deleted": messages_deleted,
        }
        write_log(new_record)

        calls += 1
        total_prompt += new_record["prompt_tokens"]
        total_completion += new_record["completion_tokens"]
        total_reasoning += new_record["reasoning_tokens"]
        total_cost += new_record["tokens_cost"]
        total_gap += new_record["gap"]
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
    print("\n--- Session summary ---")
    print(f"Calls: {calls} (failed: {failed_calls})")
    print(f"Input tokens: {total_prompt}")
    print(f"Output tokens: {total_completion} (reasoning: {total_reasoning})")
    print(f"Estimated cost: ${total_cost:.6f}")
    print(f"Average gap: {total_gap / calls if calls else 0}")


if __name__ == "__main__":
    main()
