# Editing the OUACC website

The website is now source-driven. Edit pages in `site_src/content`, not in `public` or `production`.

Each page is a Markdown file with a short block of metadata at the top. The normal content can be edited as ordinary text. Headings beginning with `##` become section headings and are automatically added to the page contents panel. Tables and more specialised HTML can remain as raw HTML inside a Markdown page where necessary.

Shared website elements live in `site_src/templates`. The navigation, header, footer, sponsor area and page shell should normally be changed there rather than page by page.

`site_src/static` contains the shared stylesheet, JavaScript, crest, favicon and images.

Run the build to regenerate both `public` and `production`. `public` is the temporary review site for GitHub Pages. `production` is the Oxford-hosting version and includes `.shtml` mirrors to preserve the historic URL convention.

For normal editorial work, ask for changes in plain English if you prefer. The intended workflow is that source content changes first, then the generated website is rebuilt and checked.
