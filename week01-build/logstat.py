import argparse
import json
import math
import pathlib
import sys
from collections import Counter

DEFAULT_LOG = pathlib.Path(__file__).parent / "per_call_log.jsonl"


def parse_line(line: str, line_num: int) -> dict | None:
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Line {line_num}: bad JSON, skipped ({e})", file=sys.stderr)
        return None


def load_records(path) -> tuple[list[dict], int]:
    records, bad = [], 0
    try:
        with open(path, encoding="utf8") as f:
            for line_num, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                record = parse_line(line, line_num)
                if record is None:
                    bad += 1
                else:
                    records.append(record)
    except FileNotFoundError:
        sys.exit(f"Log file not found: {path}")
    return records, bad


def select_records(records, session=None, show_all=False):
    if show_all:
        return records
    if session is None:
        session = records[-1]["session_id"]  # append-only log: last line = latest session
    return [r for r in records if r.get("session_id") == session]


def percentile(values, p):
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[math.ceil(p / 100 * len(ordered)) - 1]


def summarize(records: list[dict]) -> dict:
    failed = [r for r in records if r["finish_reason"] == "error"]
    ok = [r for r in records if r["finish_reason"] != "error"]
    completion = sum(r["completion_tokens"] for r in ok)
    reasoning = sum(r["reasoning_tokens"] for r in ok)
    latencies = [r["latency"] for r in ok]
    gaps = [abs(r["gap"]) for r in ok]
    return {
        "calls": len(ok),
        "failed": len(failed),
        "by_finish_reason": dict(Counter(r["finish_reason"] for r in ok)),
        "prompt_tokens": sum(r["prompt_tokens"] for r in ok),
        "completion_tokens": completion,
        "reasoning_tokens": reasoning,
        "reasoning_pct": reasoning / completion * 100 if completion else 0.0,
        "cost": sum(r["tokens_cost"] for r in ok),
        "avg_latency": sum(latencies) / len(latencies) if latencies else 0.0,
        "p50_latency": percentile(latencies, 50),
        "p95_latency": percentile(latencies, 95),
        "max_abs_gap": max(gaps) if gaps else 0,
        "trimmed_turns": sum(1 for r in ok if r["messages_deleted"] > 0),
        "messages_dropped": sum(r["messages_deleted"] for r in ok),
    }


def print_report(s: dict, bad_lines: int) -> None:
    print(f"Calls: {s['calls']} (failed: {s['failed']})")
    print(f"Finish reasons: {s['by_finish_reason']}")
    print(f"Input tokens: {s['prompt_tokens']}")
    print(
        f"Output tokens: {s['completion_tokens']} "
        f"(reasoning: {s['reasoning_tokens']}, {s['reasoning_pct']:.0f}% of output)"
    )
    print(f"Estimated cost: ${s['cost']:.6f}")
    print(
        f"Latency: avg {s['avg_latency']:.3f}s, "
        f"p50 {s['p50_latency']:.3f}s, p95 {s['p95_latency']:.3f}s"
    )
    print(f"Largest estimate gap: {s['max_abs_gap']}")
    print(f"Trimmed turns: {s['trimmed_turns']} ({s['messages_dropped']} messages dropped)")
    if bad_lines:
        print(f"Warning: {bad_lines} bad line(s) skipped")


def main():
    parser = argparse.ArgumentParser(description="Summarize per_call_log.jsonl")
    parser.add_argument("--log", default=DEFAULT_LOG, help="path to the log file")
    parser.add_argument("--session", help="session_id to report on (default: latest)")
    parser.add_argument("--all", action="store_true", help="report on every session")
    args = parser.parse_args()

    records, bad = load_records(args.log)
    if not records:
        sys.exit("No records in the log.")
    selected = select_records(records, args.session, args.all)
    if not selected:
        sys.exit(f"No records for session {args.session}.")
    print_report(summarize(selected), bad)


if __name__ == "__main__":
    main()