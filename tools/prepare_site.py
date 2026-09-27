"""Copy the guides into a MkDocs source folder so the repo root can stay flat for GitHub."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "_site_src"


def main() -> None:
    """Rebuild _site_src/ from the Markdown files in the repo root; README becomes the home page."""
    if SITE_SRC.exists():
        shutil.rmtree(SITE_SRC)
    SITE_SRC.mkdir()
    for md in sorted(ROOT.glob("*.md")):
        target = "index.md" if md.name == "README.md" else md.name
        # On the site the README is the home page, so "All guides" links must point to index.md
        text = md.read_text(encoding="utf-8").replace("](README.md)", "](index.md)")
        (SITE_SRC / target).write_text(text, encoding="utf-8")
    # The examples overview is linked from the guides; the code itself stays on GitHub
    (SITE_SRC / "examples").mkdir()
    shutil.copy2(ROOT / "examples" / "README.md", SITE_SRC / "examples" / "README.md")
    print(f"Copied {len(list(SITE_SRC.glob('*.md')))} pages to {SITE_SRC.name}/")


if __name__ == "__main__":
    main()
