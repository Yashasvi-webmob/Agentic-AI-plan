# MATCH_FIELDS = {"level", "status", "ts", "ms", "path"}
from collections import Counter
import math


def summarize(records: list[dict], top:int = 5) -> dict | None:

    if not records:
        return None
    levels = [r["level"] for r in records]
    statuses = [r["status"] for r in records]
    code_statuses = [f"{s // 100}xx" for s in statuses]
    ms_list = [r["ms"] for r in records]
    paths = [r["path"] for r in records]

    avg_ms = sum(ms_list) / len(ms_list)
    sorted_ms = sorted(ms_list)
    index_95 = math.ceil(0.95 * len(ms_list)) - 1
    result = {
        "by_level": dict(Counter(levels)),
        "by_status": dict(Counter(code_statuses)),
        "avg_ms": avg_ms,
        "p95_ms": sorted_ms[index_95],
        "top_paths": dict(Counter(paths).most_common(top)),
    }
    return result


if __name__ == "__main__":
    test_list = list(
        [
            {
                "ts": "2026-10-21T10:01:23Z",
                "level": "info",
                "path": "/api/cart",
                "status": 201,
                "ms": 205,
            },
            {
                "ts": "2026-10-22T10:01:23Z",
                "level": "info",
                "path": "/api/cart",
                "status": 200,
                "ms": 300,
            },
            {
                "ts": "2026-10-22T10:02:00Z",
                "level": "error",
                "path": "/api/orders",
                "status": 503,
                "ms": 2000,
            },
        ]
    )

    # test_list = list(dict_1)
    print(summarize(test_list))
