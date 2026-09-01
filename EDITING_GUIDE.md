# Editing the OUACC website

Edit page copy in `site_src/content`. Each Markdown file maps to one public page. Shared layout, navigation, search, footer and responsive behaviour are controlled centrally in `site_src/templates`, `site_src/static/ouacc-modern.css` and `site_src/static/ouacc.js`.

Do not edit the generated HTML files by hand. They are a build output. The GitHub Actions workflow rebuilds the site from the source when changes are pushed to `main`.

The archive flag in `site_src/data/pages.json` gives historical pages a distinct archive treatment without rewriting the underlying historical record.
