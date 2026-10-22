import json

NEEDED = {"ts", "level", "path", "ms", "status"}


def parse_line(line: str, line_num: int) -> dict | None:
    if not line.strip():
        return None
    try:
        single_record = json.loads(line)
    except json.JSONDecodeError as e:
        print("Bad JSON:", e)
        return None
    if not isinstance(single_record,dict) :
        return None
    if NEEDED - single_record.keys():
        print(f"missing keys {NEEDED - single_record.keys()} on line:{line_num}")
        return None

    return single_record


if __name__ == "__main__":
    records = list()
    bad_records = list()
    with open("sample.jsonl", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            record = parse_line(line, line_no)
            if record is None:
                bad_records.append(line_no)
            else:
                records.append(record)
    # print(records)
    # print(bad_records)
    print(f"{len(records)} ok, {len(bad_records)} skipped: {bad_records}")
