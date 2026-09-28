"""Add Previous / Index / Next links to the top and bottom of every numbered guide.

The order is the file order (00, 01 ... 48, 97, 98, 99), so renumbering never needs manual edits.

Usage:
    python tools/build_nav.py          # (re)write the navigation in every guide
    python tools/build_nav.py --check  # exit 1 if any navigation is missing or out of date (used in CI)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Guides live in their own folder so the repository front page shows the README without scrolling
GUIDES_DIR = ROOT / "guides"
GUIDE_RE = re.compile(r"^\d\d_[a-z0-9-]+\.md$")
START, END = "<!-- nav:start -->", "<!-- nav:end -->"
NAV_BLOCK_RE = re.compile(rf"\n*{re.escape(START)}.*?{re.escape(END)}\n*", re.S)


def title(path: Path) -> str:
    return path.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")


def nav_line(prev: Path | None, nxt: Path | None) -> str:
    """One line of navigation links; missing neighbours are simply left out."""
    parts = []
    if prev:
        parts.append(f"**Previous:** [{title(prev)}]({prev.name})")
    parts.append("**Index:** [All guides](../README.md)")
    if nxt:
        parts.append(f"**Next:** [{title(nxt)}]({nxt.name})")
    return f"{START}\n{' | '.join(parts)}\n{END}"


def with_nav(text: str, nav: str) -> str:
    """Remove any old navigation, then put it under the title and at the very end."""
    text = NAV_BLOCK_RE.sub("\n\n", text).strip("\n")
    title_line, rest = text.split("\n", 1)
    body = rest.strip("\n")
    if body.endswith("\n---") or body.endswith("---"):
        body = body.rstrip("-").rstrip()
    return f"{title_line}\n\n{nav}\n\n{body}\n\n---\n\n{nav}\n"


def guides() -> list[Path]:
    """All numbered guides in reading order."""
    return sorted(p for p in GUIDES_DIR.glob("*.md") if GUIDE_RE.match(p.name))


def nav_for(path: Path) -> str:
    """Navigation block for one guide, based on its neighbours in file order."""
    ordered = [g.name for g in guides()]
    i = ordered.index(path.name)
    prev = GUIDES_DIR / ordered[i - 1] if i > 0 else None
    nxt = GUIDES_DIR / ordered[i + 1] if i + 1 < len(ordered) else None
    return nav_line(prev, nxt)


def build() -> dict[Path, str]:
    """Every guide's text with fresh navigation."""
    return {path: with_nav(path.read_text(encoding="utf-8").replace("\r\n", "\n"), nav_for(path))
            for path in guides()}


def main() -> int:
    updated = build()
    if "--check" in sys.argv:
        stale = [p.name for p, text in updated.items()
                 if p.read_text(encoding="utf-8").replace("\r\n", "\n") != text]
        if stale:
            print(f"Navigation out of date in {len(stale)} file(s): run python tools/build_nav.py")
            return 1
        print("Navigation is up to date")
        return 0
    for path, text in updated.items():
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Navigation written to {len(updated)} guides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
