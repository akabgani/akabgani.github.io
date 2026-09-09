#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import html
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "generated"
OUT.mkdir(exist_ok=True)

def load_yaml(name):
    with (DATA / name).open(encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def esc(x):
    return html.escape(str(x), quote=True)

def author_html(authors):
    parts = []
    for a in authors:
        if a == "Alireza Kabgani":
            parts.append("<strong>Alireza Kabgani</strong>")
        else:
            parts.append(esc(a))
    return ", ".join(parts)

def button(label, url, kind="secondary"):
    if not url:
        return ""
    return f'<a class="pub-btn pub-btn-{kind}" href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'

def pub_card(p, compact=False):
    status = p.get("status", "preprint")
    title = esc(p["title"])
    authors = author_html(p.get("authors", []))
    year = esc(p.get("year", ""))
    venue = esc(p.get("venue", ""))
    details = esc(p.get("details", ""))
    arxiv = p.get("arxiv")
    doi = p.get("doi")
    url = p.get("url")
    code = p.get("code")
    topics = p.get("topics", [])
    primary_url = f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv}" if arxiv else url)
    status_label = {"published": "Published", "accepted": "Accepted", "preprint": "Preprint"}.get(status, status.title())
    chips = "".join(f'<span class="topic-chip">{esc(t)}</span>' for t in topics[:3])
    buttons = [
        button("Journal / DOI", f"https://doi.org/{doi}", "primary") if doi else "",
        button("arXiv", f"https://arxiv.org/abs/{arxiv}") if arxiv else "",
        button("Code", code) if code else "",
        button("Link", url) if url and not doi else "",
    ]
    buttons = "".join(b for b in buttons if b)
    meta = venue
    if details:
        meta += (", " if meta else "") + details
    if year:
        meta += (", " if meta else "") + year
    compact_class = " pub-card-compact" if compact else ""
    search_blob = " ".join([p["title"], " ".join(p.get("authors", [])), p.get("venue", ""), " ".join(topics)]).lower()
    title_html = f'<a href="{esc(primary_url)}" target="_blank" rel="noopener">{title}</a>' if primary_url else title
    return f'''
<article class="pub-card{compact_class}" data-status="{esc(status)}" data-year="{year}" data-search="{esc(search_blob)}">
  <div class="pub-card-topline"><span class="status-badge status-{esc(status)}">{status_label}</span><span class="pub-year">{year}</span></div>
  <h3 class="pub-title">{title_html}</h3>
  <div class="pub-authors">{authors}</div>
  <div class="pub-meta">{meta}</div>
  <div class="pub-topics">{chips}</div>
  <div class="pub-actions">{buttons}</div>
</article>
'''

def render_publications(pubs):
    published = sorted(
        [p for p in pubs if p.get("status") in ("published", "accepted")],
        key=lambda p: (p.get("year", 0), p.get("status") == "published"),
        reverse=True,
    )
    preprints = sorted(
        [p for p in pubs if p.get("status") == "preprint"],
        key=lambda p: p.get("year", 0),
        reverse=True,
    )
    controls = '''
<div class="pub-controls">
  <input id="pub-search" type="search" placeholder="Search title, author, venue, or topic…" aria-label="Search publications">
  <select id="pub-year" aria-label="Filter by year">
    <option value="all">All years</option>
  </select>
</div>
'''
    body = [
        controls,
        '<section id="published-section"><h2>Published & Accepted</h2><p class="section-note">Peer-reviewed publications and papers accepted for publication.</p><div class="pub-grid">',
    ]
    body += [pub_card(p) for p in published]
    body += [
        "</div></section>",
        '<section id="preprints-section"><h2>Preprints</h2><p class="section-note">arXiv manuscripts not yet listed above as accepted or published.</p><div class="pub-grid">',
    ]
    body += [pub_card(p) for p in preprints]
    body += [
        "</div></section>",
        '<p id="pub-empty" class="pub-empty" hidden>No publications match the current filter.</p>',
    ]
    (OUT / "publications.md").write_text("\n".join(body), encoding="utf-8")

def render_home(pubs, news):
    featured = [p for p in pubs if p.get("featured")]
    rank = {"published": 3, "accepted": 2, "preprint": 1}
    featured = sorted(
        featured,
        key=lambda p: (rank.get(p.get("status"), 0), p.get("year", 0)),
        reverse=True,
    )[:4]

    featured_items = ['<div class="featured-list">']
    for p in featured:
        status = p.get("status", "preprint")
        status_label = {"published": "Published", "accepted": "Accepted", "preprint": "Preprint"}.get(status, status.title())
        title = esc(p["title"])
        authors = author_html(p.get("authors", []))
        year = esc(p.get("year", ""))
        venue = esc(p.get("venue", ""))
        details = esc(p.get("details", ""))
        arxiv = p.get("arxiv")
        doi = p.get("doi")
        url = p.get("url")
        code = p.get("code")
        primary_url = f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv}" if arxiv else url)
        title_html = f'<a href="{esc(primary_url)}" target="_blank" rel="noopener">{title}</a>' if primary_url else title
        meta = venue
        if details:
            meta += (", " if meta else "") + details
        if year:
            meta += (", " if meta else "") + year
        links = []
        if doi:
            links.append(f'<a href="https://doi.org/{esc(doi)}" target="_blank" rel="noopener">DOI</a>')
        if arxiv:
            links.append(f'<a href="https://arxiv.org/abs/{esc(arxiv)}" target="_blank" rel="noopener">arXiv</a>')
        if code:
            links.append(f'<a href="{esc(code)}" target="_blank" rel="noopener">Code</a>')
        if url and not doi:
            links.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">Link</a>')
        featured_items.append(
            f'<article class="featured-paper">'
            f'<div class="featured-paper-year">{year}<span class="featured-paper-status">{status_label}</span></div>'
            f'<div><h3>{title_html}</h3>'
            f'<div class="featured-paper-authors">{authors}</div>'
            f'<div class="featured-paper-meta">{meta}</div>'
            f'<div class="featured-paper-links">{"".join(links)}</div></div>'
            f'</article>'
        )
    featured_items += ["</div>"]
    (OUT / "featured.md").write_text("\n".join(featured_items), encoding="utf-8")

    news_sorted = sorted(news, key=lambda n: n.get("date", ""), reverse=True)[:5]
    items = ['<div class="news-list">']
    for n in news_sorted:
        d = datetime.fromisoformat(n["date"]).strftime("%b %Y")
        text = esc(n["text"])
        typ = esc(n.get("type", "news").title())
        url = n.get("url")
        content = f'<a href="{esc(url)}" target="_blank" rel="noopener">{text}</a>' if url else text
        items.append(
            f'<div class="news-item"><div class="news-date">{d}</div><div><span class="news-type">{typ}</span>{content}</div></div>'
        )
    items += ["</div>"]
    (OUT / "news.md").write_text("\n".join(items), encoding="utf-8")

def render_activities(a):
    sections = []
    sections.append("## Research projects\n")
    for x in a.get("projects", []):
        sections.append(f"- **{x['period']}** · {x['text']}")
    sections.append("\n## Conference organization\n")
    for x in a.get("organization", []):
        sections.append(f"- **{x['year']}** · {x['text']}")
    sections.append("\n## Supervision\n")
    for x in a.get("supervisions", []):
        sections.append(f"- **{x['year']}** · {x['text']}")
    sections.append("\n## Editorial & reviewing activity\n")
    sections.append("- Editorial Board: **Control and Optimization in Applied Mathematics (COAM)**")
    sections.append("- Reviewer for: " + "; ".join(a.get("reviewing", [])) + ".")
    sections.append("\n## Honours & grants\n")
    for x in a.get("honours", []):
        sections.append(f"- **{x['year']}** · {x['text']}")
    (OUT / "activities.md").write_text("\n".join(sections), encoding="utf-8")

def validate(pubs):
    ids = set()
    errors = []
    for p in pubs:
        pid = p.get("id")
        if pid in ids:
            errors.append(f"Duplicate id: {pid}")
        ids.add(pid)
        if p.get("status") not in {"published", "accepted", "preprint"}:
            errors.append(f"Invalid status for {pid}: {p.get('status')}")
        if p.get("status") == "preprint" and not p.get("arxiv"):
            errors.append(f"Preprint without arXiv id: {pid}")
    if errors:
        raise SystemExit("\n".join(errors))

def main():
    pubs = load_yaml("publications.yml")
    news = load_yaml("news.yml")
    activities = load_yaml("activities.yml")
    validate(pubs)
    render_publications(pubs)
    render_home(pubs, news)
    render_activities(activities)
    print(f"Generated site fragments from {len(pubs)} publications and {len(news)} news items.")

if __name__ == "__main__":
    main()
