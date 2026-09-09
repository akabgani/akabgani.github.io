# Migration notes

This repository was seeded from the existing Google Site and then normalized for a data-driven Quarto workflow.

## Verified recent publication status

- **On Fundamental Properties of High-Order Forward-Backward Envelope**  
  Published in *Journal of Optimization Theory and Applications* (2026), volume 210(1), Article 14.  
  DOI: `10.1007/s10957-026-03047-6`

- **Minimizing Smooth Kurdyka-Łojasiewicz Functions via Generalized Descent Methods: Convergence Rate and Complexity**  
  Published in *Journal of Optimization Theory and Applications* (2026), volume 210(1), Article 13.  
  DOI: `10.1007/s10957-026-03034-x`

- **ItsOPT: An Inexact Two-Level Smoothing Framework for Nonconvex Optimization via High-Order Moreau Envelope**  
  Seeded as **accepted / forthcoming** in *SIAM Journal on Optimization* based on the current Google Site. Final DOI/volume details are not yet included in this starter package.

- **Asymptotic Convergence Analysis of High-Order Proximal-Point Methods Beyond Sublinear Rates**  
  Seeded as **accepted / forthcoming** in *SIAM Journal on Optimization* based on the current Google Site. Final DOI/volume details are not yet included in this starter package.

## Deliberate design decisions

- One paper = one record.
- Published and accepted papers are grouped together.
- arXiv-only manuscripts are shown in a separate Preprints section.
- When a preprint is published, it is promoted rather than duplicated.
- arXiv links remain visible after publication.
- The homepage shows only selected featured papers and five latest news items.
- Full publication data lives in `data/publications.yml`.
- Full news data lives in `data/news.yml`.
- Activities data lives in `data/activities.yml`.

## Before public launch

1. Review all legacy bibliographic metadata migrated from the Google Site.
2. Add the latest PDF CV.
3. Confirm the preferred profile photo.
4. Add a direct Google Scholar profile URL if desired.
5. Once SIAM publishes final metadata for the two accepted papers, update their DOI/details.
