#!/usr/bin/env python3
import argparse
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "data" / "news.yml"

def main():
    parser = argparse.ArgumentParser(description="Add one news item.")
    parser.add_argument("text")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--type", default="news", choices=["news", "publication", "talk", "service", "award"])
    parser.add_argument("--url")
    args = parser.parse_args()

    items = yaml.safe_load(NEWS.read_text(encoding="utf-8")) or []
    item = {"date": args.date, "type": args.type, "text": args.text}
    if args.url:
        item["url"] = args.url
    items.append(item)
    NEWS.write_text(
        yaml.safe_dump(items, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    print(f"Added {args.type} item dated {args.date}.")

if __name__ == "__main__":
    main()
