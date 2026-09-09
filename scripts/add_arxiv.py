#!/usr/bin/env python3
import argparse
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBS = ROOT / "data" / "publications.yml"
ATOM = {"a": "http://www.w3.org/2005/Atom"}

def normalize_id(value):
    value = value.strip()
    value = re.sub(r"^https?://arxiv\.org/(abs|pdf)/", "", value)
    value = value.removesuffix(".pdf")
    return value.split("v")[0]

def fetch_arxiv(arxiv_id):
    query = urlencode({"id_list": arxiv_id})
    req = Request(
        "https://export.arxiv.org/api/query?" + query,
        headers={"User-Agent": "akabgani-academic-site/1.0"},
    )
    with urlopen(req, timeout=20) as response:
        root = ET.fromstring(response.read())
    entry = root.find("a:entry", ATOM)
    if entry is None:
        raise SystemExit(f"No arXiv entry found for {arxiv_id}")
    title = " ".join((entry.findtext("a:title", default="", namespaces=ATOM)).split())
    authors = [
        a.findtext("a:name", default="", namespaces=ATOM).strip()
        for a in entry.findall("a:author", ATOM)
    ]
    published = entry.findtext("a:published", default="", namespaces=ATOM)
    year = int(published[:4]) if published[:4].isdigit() else 2000 + int(arxiv_id[:2])
    return title, authors, year

def main():
    parser = argparse.ArgumentParser(description="Import one arXiv paper into data/publications.yml.")
    parser.add_argument("arxiv_id", help="arXiv ID or arXiv URL")
    parser.add_argument("--topic", action="append", default=[], help="Topic tag; repeat as needed")
    parser.add_argument("--featured", action="store_true", help="Feature the paper on the homepage")
    args = parser.parse_args()

    arxiv_id = normalize_id(args.arxiv_id)
    pubs = yaml.safe_load(PUBS.read_text(encoding="utf-8")) or []
    if any(str(p.get("arxiv", "")) == arxiv_id for p in pubs):
        raise SystemExit(f"arXiv:{arxiv_id} is already in publications.yml")

    title, authors, year = fetch_arxiv(arxiv_id)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:55]
    record = {
        "id": f"{year}-{slug}",
        "title": title,
        "authors": authors,
        "year": year,
        "status": "preprint",
        "venue": "arXiv",
        "arxiv": arxiv_id,
        "topics": args.topic,
        "featured": args.featured,
    }
    pubs.append(record)
    PUBS.write_text(
        yaml.safe_dump(pubs, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    print(f"Added arXiv:{arxiv_id}: {title}")
    print("Run `quarto preview` locally or commit/push to rebuild the website.")

if __name__ == "__main__":
    main()
