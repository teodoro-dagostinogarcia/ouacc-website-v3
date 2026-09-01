# OUACC website v3

This repository is the development source for the Oxford University Association Croquet Club website. GitHub is used as a review and collaboration environment. It is not the intended permanent host.

The website is generated from `site_src` using `tools/build.py`.

GitHub Pages uses the included workflow to build the `public` preview site automatically. The workflow also builds and audits the Oxford production package on every deployment, although the production files are not committed to the repository.

The eventual University-hosted website is generated with `python tools/build.py --target production`. That package uses `.shtml` for site pages so the historic OUACC URL convention can be retained, while the development preview uses `.html` for GitHub Pages.

Do not edit generated output by hand. Edit `site_src/content` for page content, `site_src/templates` for shared page structure, and `site_src/static` for CSS, JavaScript, images and public documents.
