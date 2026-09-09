Academic homepage redesign patch

Replace these files in the root of your local akabgani-site repository:
  index.qmd
  styles.css
  _quarto.yml
  scripts/render_data.py

Then run:
  python scripts/render_data.py
  git diff

If the diff looks correct:
  git add index.qmd styles.css _quarto.yml scripts/render_data.py generated/featured.md generated/news.md
  git commit -m "Redesign homepage for academic profile"
  git push

The GitHub Actions workflow will rebuild and deploy the site automatically.
