#!/usr/bin/env python3
import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBS = ROOT / "data" / "publications.yml"

def main():
    parser = argparse.ArgumentParser(description="Move an existing arXiv record to accepted/published without duplicating it.")
    parser.add_argument("arxiv_id", help="Existing arXiv ID")
    parser.add_argument("--status", required=True, choices=["accepted", "published"])
    parser.add_argument("--venue", required=True)
    parser.add_argument("--doi")
    parser.add_argument("--details")
    parser.add_argument("--year", type=int)
    args = parser.parse_args()

    pubs = yaml.safe_load(PUBS.read_text(encoding="utf-8")) or []
    matches = [p for p in pubs if str(p.get("arxiv", "")) == args.arxiv_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one record with arXiv:{args.arxiv_id}; found {len(matches)}.")

    p = matches[0]
    p["status"] = args.status
    p["venue"] = args.venue
    if args.doi:
        p["doi"] = args.doi
    if args.details:
        p["details"] = args.details
    if args.year:
        p["year"] = args.year

    PUBS.write_text(
        yaml.safe_dump(pubs, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    print(f"Updated arXiv:{args.arxiv_id} → {args.status}: {args.venue}")
    print("The arXiv field was retained, so both journal and arXiv links will remain visible.")

if __name__ == "__main__":
    main()
