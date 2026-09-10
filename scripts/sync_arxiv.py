#!/usr/bin/env python3
"""Discover new arXiv papers by Alireza Kabgani and add them to the site data.

The script is deliberately conservative:
- it searches arXiv by author;
- it requires the exact normalized author name to be present in the returned author list;
- it deduplicates by base arXiv id and normalized title;
- it never changes an existing paper's accepted/published status;
- newly discovered papers are added as preprints and are not featured automatically.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBS = ROOT / "data" / "publications.yml"
NEWS = ROOT / "data" / "news.yml"

ATOM = {"a": "http://www.w3.org/2005/Atom"}
ARXIV = {"arxiv": "http://arxiv.org/schemas/atom"}
API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "akabgani-academic-site/1.0 (https://akabgani.github.io/)"


def normalize_arxiv_id(value: str) -> str:
    value = str(value or "").strip()
    value = re.sub(r"^https?://(?:export\.)?arxiv\.org/(?:abs|pdf)/", "", value)
    value = value.removesuffix(".pdf")
    return re.sub(r"v\d+$", "", value)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-z0-9]+", " ", value.casefold())
    return " ".join(value.split())


def clean_text(value: str) -> str:
    return " ".join((value or "").split())


def fetch_author_entries(author: str, max_results: int = 50) -> list[dict]:
    params = urlencode(
        {
            "search_query": f'au:"{author}"',
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    request = Request(
        f"{API_URL}?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    with urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    entries: list[dict] = []
    for entry in root.findall("a:entry", ATOM):
        entry_url = entry.findtext("a:id", default="", namespaces=ATOM)
        arxiv_id = normalize_arxiv_id(entry_url.rsplit("/", 1)[-1])
        title = clean_text(entry.findtext("a:title", default="", namespaces=ATOM))
        authors = [
            clean_text(a.findtext("a:name", default="", namespaces=ATOM))
            for a in entry.findall("a:author", ATOM)
        ]
        published = entry.findtext("a:published", default="", namespaces=ATOM)
        updated = entry.findtext("a:updated", default="", namespaces=ATOM)
        primary = entry.find("arxiv:primary_category", ARXIV)
        category = primary.attrib.get("term", "") if primary is not None else ""

        if not arxiv_id or not title:
            continue

        entries.append(
            {
                "arxiv": arxiv_id,
                "title": title,
                "authors": authors,
                "published": published,
                "updated": updated,
                "category": category,
            }
        )
    return entries


def make_id(year: int, title: str, existing_ids: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:58]
    candidate = f"{year}-{slug}"
    if candidate not in existing_ids:
        return candidate
    i = 2
    while f"{candidate}-{i}" in existing_ids:
        i += 1
    return f"{candidate}-{i}"


def entry_year(entry: dict) -> int:
    published = entry.get("published", "")
    if len(published) >= 4 and published[:4].isdigit():
        return int(published[:4])
    arxiv_id = entry["arxiv"]
    if re.match(r"^\d{4}\.\d+$", arxiv_id):
        return 2000 + int(arxiv_id[:2])
    return date.today().year


def entry_date(entry: dict) -> str:
    published = entry.get("published", "")
    if len(published) >= 10:
        return published[:10]
    return date.today().isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find new arXiv papers by an author and add them to publications.yml."
    )
    parser.add_argument("--author", default="Alireza Kabgani")
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument(
        "--no-news",
        action="store_true",
        help="Do not add a Latest news item for newly discovered preprints.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report discoveries without modifying any files.",
    )
    args = parser.parse_args()

    pubs = yaml.safe_load(PUBS.read_text(encoding="utf-8")) or []
    news = yaml.safe_load(NEWS.read_text(encoding="utf-8")) or []

    target_author = normalize_text(args.author)
    existing_arxiv = {
        normalize_arxiv_id(p.get("arxiv", ""))
        for p in pubs
        if p.get("arxiv")
    }
    title_to_index = {
        normalize_text(p.get("title", "")): i
        for i, p in enumerate(pubs)
        if p.get("title")
    }
    existing_ids = {str(p.get("id", "")) for p in pubs}
    existing_news_urls = {str(n.get("url", "")) for n in news if n.get("url")}

    entries = fetch_author_entries(args.author, max_results=args.max_results)
    changed = False
    new_count = 0
    linked_count = 0

    # Process old-to-new so multiple new records are appended chronologically.
    for entry in reversed(entries):
        normalized_authors = {normalize_text(a) for a in entry["authors"]}
        if target_author not in normalized_authors:
            continue

        arxiv_id = entry["arxiv"]
        if arxiv_id in existing_arxiv:
            continue

        normalized_title = normalize_text(entry["title"])
        if normalized_title in title_to_index:
            # If a paper already exists under the same title, attach the arXiv id
            # rather than creating a duplicate. Never downgrade its status.
            idx = title_to_index[normalized_title]
            if not pubs[idx].get("arxiv"):
                print(f"Link existing record to arXiv:{arxiv_id}: {entry['title']}")
                if not args.dry_run:
                    pubs[idx]["arxiv"] = arxiv_id
                existing_arxiv.add(arxiv_id)
                linked_count += 1
                changed = True
            continue

        year = entry_year(entry)
        record_id = make_id(year, entry["title"], existing_ids)
        record = {
            "id": record_id,
            "title": entry["title"],
            "authors": entry["authors"],
            "year": year,
            "status": "preprint",
            "venue": "arXiv",
            "arxiv": arxiv_id,
            "topics": [],
            "featured": False,
        }

        print(f"New arXiv paper: arXiv:{arxiv_id} — {entry['title']}")
        if not args.dry_run:
            pubs.append(record)

            if not args.no_news:
                url = f"https://arxiv.org/abs/{arxiv_id}"
                if url not in existing_news_urls:
                    news.append(
                        {
                            "date": entry_date(entry),
                            "type": "publication",
                            "text": f"New preprint on arXiv: “{entry['title']}”.",
                            "url": url,
                        }
                    )
                    existing_news_urls.add(url)

        existing_arxiv.add(arxiv_id)
        existing_ids.add(record_id)
        title_to_index[normalized_title] = len(pubs) - 1 if not args.dry_run else -1
        new_count += 1
        changed = True

    if args.dry_run:
        print(f"Dry run complete: {new_count} new paper(s), {linked_count} existing record(s) linkable.")
        return

    if changed:
        PUBS.write_text(
            yaml.safe_dump(pubs, sort_keys=False, allow_unicode=True, width=120),
            encoding="utf-8",
        )
        NEWS.write_text(
            yaml.safe_dump(news, sort_keys=False, allow_unicode=True, width=120),
            encoding="utf-8",
        )
        print(f"Updated site data: {new_count} new paper(s), {linked_count} existing record(s) linked.")
    else:
        print("No new arXiv papers found.")


if __name__ == "__main__":
    main()
