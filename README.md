# OUACC website

This repository contains the public OUACC website and its editable source.

The generated website is published from the repository root for simple GitHub Pages use. The editable page content lives under `site_src/content`, shared templates live under `site_src/templates`, and `build.py` rebuilds the site.

For a future-proof workflow, GitHub Actions can rebuild and publish the root site whenever `site_src` changes. See `.github/workflows/build.yml`.

The public site is intended for public-facing material only. Do not add private committee documents, member lists, credentials or other confidential information.
