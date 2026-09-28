# Tools

Small Python scripts (standard library only) that keep the guides consistent and build the website. Run them from the repository root; CI runs the same commands on every push.

| Script | What it does | Command |
|---|---|---|
| `check_docs.py` | Checks every guide: title format, required sections, Contents list matches headings, links point to existing files, link numbers match file numbers, "section N" references exist, the README lists every guide, and all source files are plain ASCII | `python tools/check_docs.py` |
| `build_nav.py` | Writes the Previous / Index / Next links at the top and bottom of every guide, in file-number order | `python tools/build_nav.py` (`--check` only reports) |
| `build_glossary.py` | Collects every "Key terms" table into `guides/98_glossary.md`, sorted A to Z with links | `python tools/build_glossary.py` (`--check` only reports) |
| `prepare_site.py` | Copies the README (as the home page), all guides and the examples overview into `_site_src/`, rewriting links for the website's flat layout | `python tools/prepare_site.py` |

## Build the website locally

```bash
pip install -r requirements-docs.txt
python tools/prepare_site.py
mkdocs serve          # http://127.0.0.1:8000, reloads on changes to _site_src/
mkdocs build --strict # what CI runs: any warning fails the build
```

`_site_src/` and `_site/` are generated and git-ignored.

## Where CI uses them

| Workflow (`.github/workflows/`) | Runs |
|---|---|
| `docs-checks.yml` | `check_docs.py`, `build_nav.py --check`, `build_glossary.py --check`, markdownlint, strict site build |
| `docs-site.yml` | `prepare_site.py`, then builds and deploys the website to GitHub Pages |
| `link-check.yml` | lychee on all Markdown files (also weekly, opening an issue when links break) |
| `examples.yml` | Lint, tests and evals for `examples/` |
| `templates.yml` | Lint, tests, frontend build, generated-service test and full Docker Compose smoke test for `templates/` |
