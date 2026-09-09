# akabgani.github.io

Quarto source for Alireza Kabgani's academic and research portfolio website.

## What is automated

The website separates:

- **Published & Accepted**
- **Preprints**

All publications live in `data/publications.yml`. A paper appears only once. When a preprint is accepted, change:

```yaml
status: preprint
```

to:

```yaml
status: accepted
venue: SIAM Journal on Optimization
details: Accepted / forthcoming
```

When final publication details arrive, change it to `published` and add the DOI/details. Keep the `arxiv:` field so the arXiv button remains available.

News is maintained in `data/news.yml`.

The script `scripts/render_data.py` automatically builds the publication cards, featured homepage items, news list, and activities fragments before Quarto renders the site.

## First deployment

1. Create a **public** GitHub repository named exactly `akabgani.github.io`.
2. Upload/push all files in this repository.
3. On GitHub open **Settings → Pages**.
4. Under **Build and deployment → Source**, choose **GitHub Actions**.
5. Push to `main` or manually run the `Build and deploy Quarto site` workflow from the Actions tab.
6. The site will be available at `https://akabgani.github.io`.

## Local preview on Windows

Install Quarto once from https://quarto.org.

Then in PowerShell:

```powershell
.\preview.ps1
```

Or manually:

```powershell
python -m pip install -r requirements.txt
quarto preview
```

Quarto automatically runs `python scripts/render_data.py` before rendering.


## Faster update commands

### Import a new arXiv preprint

Instead of typing the full title and author list:

```powershell
python scripts/add_arxiv.py 2609.12345 --topic "High-order optimization"
```

The script queries the public arXiv API, imports the title/authors/year, and creates a `preprint` record automatically.

### Move a preprint to Accepted

```powershell
python scripts/promote_publication.py 2609.12345 `
  --status accepted `
  --venue "SIAM Journal on Optimization" `
  --year 2027
```

### Move it to Published

```powershell
python scripts/promote_publication.py 2609.12345 `
  --status published `
  --venue "SIAM Journal on Optimization" `
  --doi "10.xxxx/xxxxx" `
  --details "37(2), 123–150" `
  --year 2027
```

This edits the existing record, so the paper never appears twice. The arXiv link is retained.

### Add a news item

```powershell
python scripts/add_news.py "Our paper ... was accepted for publication in ..." `
  --type publication `
  --url "https://..."
```


## Add a publication manually

Edit `data/publications.yml` and append an entry:

```yaml
- id: short-unique-id
  title: "Paper title"
  authors:
    - Alireza Kabgani
    - Coauthor Name
  year: 2026
  status: preprint
  venue: arXiv
  arxiv: "2609.12345"
  topics:
    - High-order optimization
  featured: false
```

Commit and push. GitHub Actions rebuilds and publishes the site.

## Add news

Edit `data/news.yml`:

```yaml
- date: "2026-09-09"
  type: publication
  text: "Our paper ... was accepted for publication in ..."
  url: "https://..."
```

The latest five entries automatically appear on the homepage.

## Important checks before launch

- Confirm the homepage profile image.
- Add your Google Scholar profile link if you want it in the navbar.
- Put your latest PDF CV at `assets/Alireza_Kabgani_CV.pdf` and activate the download link in `cv.qmd`.
- Review publication metadata, especially accepted/forthcoming papers whose final volume/issue/DOI may not yet be public.

## Optional next automation

A later version can add a scheduled workflow that checks ORCID/Crossref/arXiv and opens a GitHub issue or pull request when a likely new publication is detected. Human approval is deliberately retained to avoid author-disambiguation errors.
