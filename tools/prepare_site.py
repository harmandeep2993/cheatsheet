"""Copy the README and guides into one flat MkDocs source folder (the repo keeps guides in guides/)."""

import re
import shutil
from pathlib import Path

from build_nav import guides

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "_site_src"
NAV_START, NAV_END = "<!-- nav:start -->", "<!-- nav:end -->"
# On the site every page sits in one folder, so links that step out of or into guides/ lose that step
README_GUIDE_LINK_RE = re.compile(r"\]\(guides/")
# Folder READMEs are not website pages, so the home page links to them on GitHub instead
REPO_TREE_URL = "https://github.com/harmandeep2993/pocket-guide/tree/main/"
FOLDER_README_RE = re.compile(r"\]\((guides|templates|tools)/README\.md\)")
# Wrap each diagram in a box the stylesheet can scroll sideways, so phones do not shrink it unreadably small
MERMAID_BLOCK_RE = re.compile(r"^```mermaid\n.*?^```$", re.S | re.M)


def write_page(source: Path, target_name: str, replacements: list[tuple[str, str]]) -> None:
    """Copy one Markdown file into the site folder, rewriting links for the flat layout."""
    text = source.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    text = MERMAID_BLOCK_RE.sub(lambda m: f'<div class="pg-diagram" markdown="1">\n\n{m.group(0)}\n\n</div>', text)
    # Wrap Previous / Next links so the stylesheet can make them small and unobtrusive
    text = text.replace(NAV_START, '<div class="pg-nav" markdown="1">').replace(NAV_END, "</div>")
    (SITE_SRC / target_name).write_text(text, encoding="utf-8")


def main() -> None:
    """Rebuild _site_src/: README becomes the home page, every guide sits next to it."""
    if SITE_SRC.exists():
        shutil.rmtree(SITE_SRC)
    SITE_SRC.mkdir()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme = FOLDER_README_RE.sub(lambda m: f"]({REPO_TREE_URL}{m.group(1)})", readme)
    (SITE_SRC / "index.md").write_text(README_GUIDE_LINK_RE.sub("](", readme), encoding="utf-8")
    # Numbered guides only: guides/README.md describes the repo folder and has no place on the site
    for md in guides():
        write_page(md, md.name, [("](../README.md)", "](index.md)"), ("](../examples/", "](examples/")])
    shutil.copytree(ROOT / "site_assets", SITE_SRC, dirs_exist_ok=True)
    # The examples overview is linked from the guides; the code itself stays on GitHub
    (SITE_SRC / "examples").mkdir()
    examples_readme = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
    (SITE_SRC / "examples" / "README.md").write_text(examples_readme.replace("](../guides/", "](../"), encoding="utf-8")
    print(f"Copied {len(list(SITE_SRC.glob('*.md')))} pages to {SITE_SRC.name}/")


if __name__ == "__main__":
    main()
