import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import argparse
import sys

load_dotenv()


def run_file_prompt(client: OpenAI, temp: float, prompt: list[dict]) -> dict:
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        max_tokens=2000,
        temperature=temp,
        messages=prompt,
    )
    return {
        "usage": resp.usage,
        "finish_reason": resp.choices[0].finish_reason,
        "content": resp.choices[0].message.content,
    }


def form_prompt(article_path: str, prompt_version: str) -> list[dict]:
    if prompt_version == "v1":
        p1 = Path("prompts/summarize_sys_prompt_v1.txt")
        p2 = Path("prompts/summarize_usr_prompt_v1.txt")
    elif prompt_version == "v2":
        p1 = Path("prompts/summarize_sys_prompt_v2.txt")
        p2 = Path("prompts/summarize_usr_prompt_v2.txt")
    p3 = Path(article_path)
    sys_text = p1.read_text(encoding="utf-8")
    usr_prompt = p2.read_text(encoding="utf-8")
    article_text = p3.read_text(encoding="utf-8")
    usr_text = usr_prompt.replace("{{ARTICLE}}", article_text)
    return [
        {"role": "system", "content": sys_text},
        {"role": "user", "content": usr_text},
    ]


def main():
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    ap = argparse.ArgumentParser(description="Parsing Prompt files")
    ap.add_argument("path")
    ap.add_argument("--prompt", default="v1", choices=["v1", "v2"])
    args = ap.parse_args()
    prompt_version = args.prompt
    prompt = form_prompt(args.path, prompt_version)

    # print(f"prompt:{prompt}")
    summary_records = []
    for temp in [0.7, 0, 1.5]:
        resp = run_file_prompt(client, temp=temp, prompt=prompt)
        print("Response:")
        print(f"{resp['content']}")
        print(f"finish_reason:{resp['finish_reason']}")
        print(f"usage: {resp['usage']}")
        summary_records.append(
            {
                "temp": temp,
                "completion_tokens": resp["usage"].completion_tokens,
                "reasoning_tokens": resp[
                    "usage"
                ].completion_tokens_details.reasoning_tokens,
            }
        )
    for record in summary_records:
        print(f"For temp: {record['temp']}- {record}")


if __name__ == "__main__":
    main()
