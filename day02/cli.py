import argparse
from parser import parse_line
from stats import summarize
import sys


def main() -> None:
    ap = argparse.ArgumentParser(description="Parsing File Args")
    ap.add_argument("path")
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()
    bad_records = []
    records = []
    try:
        with open(args.path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                record = parse_line(line, line_no)
                if record is None:
                    bad_records.append(line_no)
                else:
                    records.append(record)
    except FileNotFoundError:
        print(f"File not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    summarized_result = summarize(records, args.top)
    if summarized_result is None:
        print(f"Summarized Result is empty, no valid records in : {args.path}", file=sys.stderr)
        sys.exit(1)
    print(f"Filename: {args.path}")
    print(f"Records: {len(records)}, Bad Records: {len(bad_records)} {bad_records}")
    for path,count in summarized_result["top_paths"].items():
        print(f"{path:<20} {count:>4}")
    print(f"levels: {summarized_result['by_level']}")
    print(f"status:{summarized_result['by_status']}")
    print(
        f"p95: {summarized_result['p95_ms']:.1f}ms; Avg Time: {summarized_result['avg_ms']:.1f}ms"
    )


if __name__ == "__main__":
    main()
