import argparse
import json
import os

from monitoring.drift import compute_drift_report
from monitoring.log_store import fetch_recent_logs, init_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM drift check against inference logs")
    parser.add_argument("--baseline-size", type=int, default=300)
    parser.add_argument("--current-size", type=int, default=100)
    parser.add_argument("--output", type=str, default="reports/drift/latest.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    logs = fetch_recent_logs(limit=max(5000, args.baseline_size + args.current_size))
    report = compute_drift_report(logs, baseline_size=args.baseline_size, current_size=args.current_size)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
