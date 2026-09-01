# OUACC deployment guide

## GitHub preview

Upload the contents of this repository to `ouacc-website-v3`.

In GitHub, open Settings, Pages, and set the source to `GitHub Actions`. The included workflow builds the preview site from `site_src`, audits it, and publishes it.

## Editing

Edit pages in `site_src/content`. Each page has a metadata block followed by Markdown. Shared navigation, footer, page shell and components live in `site_src/templates`. Shared CSS, JavaScript, the crest, favicon and public assets live in `site_src/static`.

The generated `public` and `production` directories are deliberately not committed. This keeps the repository smaller and avoids treating generated files as source material.

## Oxford production site

When the redesign is approved, the University-hosting version should be generated with:

`python tools/build.py --target production`

The resulting `production` directory contains the files for the existing Oxford server. The site pages use `.shtml`, preserving the historic URL convention. The new `search.html` page remains `.html`.

The `production-package.yml` GitHub Action can build this package from the repository and save it as a downloadable GitHub Actions artifact. For the eventual live deployment, keep the existing server backup and URL structure until redirects have been checked.
