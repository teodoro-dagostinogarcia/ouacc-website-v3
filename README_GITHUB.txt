OUACC GitHub Pages setup

Upload the whole repository to GitHub. The editable website content is under site_src/content. Shared templates are under site_src/templates. Do not edit the generated files by hand.

For automatic publication, open Settings > Pages and select GitHub Actions as the build source. The included workflow rebuilds the site, audits it, and deploys the generated dist folder whenever main changes.

The dist folder is included as a verified build snapshot for reference.

To edit a page in GitHub web, open the corresponding Markdown file under site_src/content, edit the text, and commit to main. The workflow will rebuild and republish the site.
