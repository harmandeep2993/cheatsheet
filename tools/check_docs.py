"""Structural checks for the pocket guide: links, numbering, anchors, required sections and ASCII.

Run locally with `python tools/check_docs.py`; CI runs it on every push and pull request.
Exits with status 1 and a list of problems if anything is wrong.
"""

import re
import sys
from pathlib import Path

from build_nav import GUIDES_DIR

ROOT = Path(__file__).resolve().parent.parent
GUIDE_RE = re.compile(r"^(\d\d)_[a-z0-9-]+\.md$")
LINK_RE = re.compile(
    r"\[([^\]]+)\]\(((?:\.\./)?(?:examples/[^)#\s]+|README\.md|(?:guides/)?\d\d_[a-z0-9-]+\.md))(#[^)]*)?\)"
)
HEADING_RE = re.compile(r"^## (\d+)\. (.+)$")
TOC_RE = re.compile(r"^\d+\. \[[^\]]+\]\(#([^)]+)\)$")
SECTION_REF_RE = re.compile(r"\]\((\d\d_[a-z0-9-]+\.md)\)(?:[^\n\[]{0,40}?)sections? (\d+)(?:-(\d+))?")
# Guides that are reference pages rather than tool guides, so they have no Introduction / docs table
REFERENCE_PAGES = {"00", "97", "98", "99"}
ASCII_GLOBS = [
    "*.md", "guides/*.md", "tools/*.md", "tools/*.py", "examples/**/*.py", "examples/**/*.md", ".github/workflows/*.yml",
    "templates/**/*.py", "templates/**/*.md", "templates/**/*.ts", "templates/**/*.tsx", "templates/**/*.css",
    "templates/**/*.yaml", "templates/**/*.conf", "templates/**/Dockerfile",
    "templates/**/*.jinja", "templates/**/*.yml",
]
# Installed packages and build output are not ours to check
SKIP_DIRS = {".venv", "node_modules", "_site_src", "_site", "__pycache__"}


def github_slug(heading: str) -> str:
    """Anchor GitHub generates for a heading: lowercase, drop punctuation except - and _, spaces to -."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def outside_code(lines: list[str]):
    """Yield (line_number, line) for lines outside fenced code blocks."""
    in_code = False
    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            yield number, line


def check_ascii(errors: list[str]) -> None:
    for pattern in ASCII_GLOBS:
        for path in ROOT.glob(pattern):
            if SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if any(ord(ch) > 127 for ch in line):
                    errors.append(f"{path.relative_to(ROOT)}:{number}: non-ASCII character")


def check_links(path: Path, errors: list[str]) -> None:
    """Relative links must point to existing files, and "NN - Title" link text must match the file number."""
    name = path.relative_to(ROOT).as_posix()
    for line_no, line in outside_code(path.read_text(encoding="utf-8").splitlines()):
        for m in LINK_RE.finditer(line):
            text_part, target = m.group(1), m.group(2)
            target_path = (path.parent / target).resolve()
            if not target_path.exists():
                errors.append(f"{name}:{line_no}: broken link to {target}")
                continue
            file_num = GUIDE_RE.match(Path(target).name)
            text_num = re.match(r"(\d\d)(?:\D|$)", text_part)
            if file_num and text_num and text_num.group(1) != file_num.group(1):
                errors.append(f"{name}:{line_no}: link text '{text_part}' does not match {target}")


def check_guide(path: Path, guides: dict[str, Path], errors: list[str]) -> None:
    name = path.name
    number = name[:2]
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = re.match(r"# (\d\d) - ", lines[0]) if lines else None
    if not title or title.group(1) != number:
        errors.append(f"{name}:1: title must start with '# {number} - '")

    if number not in REFERENCE_PAGES:
        for required in ("## Introduction", "### Official docs", "Last verified:"):
            if required not in text:
                errors.append(f"{name}: missing '{required}'")

    # Contents entries must match numbered headings, in order
    toc = [m.group(1) for _, line in outside_code(lines) if (m := TOC_RE.match(line))]
    headings = [github_slug(f"{m.group(1)}. {m.group(2)}")
                for _, line in outside_code(lines) if (m := HEADING_RE.match(line))]
    if toc and toc != headings:
        missing = [t for t in toc if t not in headings]
        extra = [h for h in headings if h not in toc]
        errors.append(f"{name}: Contents does not match headings (no heading for {missing}, not listed {extra})")

    check_links(path, errors)

    for m in SECTION_REF_RE.finditer(text):
        target = guides.get(m.group(1)[:2])
        if target is None:
            continue
        body = target.read_text(encoding="utf-8")
        for section in filter(None, (m.group(2), m.group(3))):
            if not re.search(rf"^## {section}\. ", body, re.M):
                errors.append(f"{name}: reference to {m.group(1)} section {section}, which does not exist")


def main() -> int:
    errors: list[str] = []
    guides = {p.name[:2]: p for p in GUIDES_DIR.glob("*.md") if GUIDE_RE.match(p.name)}
    numbers = sorted(guides)
    if len(numbers) != len(set(numbers)):
        errors.append("duplicate guide numbers")

    check_ascii(errors)
    for path in sorted(guides.values()):
        check_guide(path, guides, errors)
    readme = ROOT / "README.md"
    check_links(readme, errors)
    for number in numbers:
        if f"(guides/{guides[number].name})" not in readme.read_text(encoding="utf-8"):
            errors.append(f"README.md: guide {guides[number].name} is not listed")

    if errors:
        print(f"{len(errors)} problem(s) found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"OK: {len(guides)} guides checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
