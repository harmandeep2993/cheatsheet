# 01 - Markdown

<!-- nav:start -->
**Previous:** [00 - Big Picture: How Everything Connects](00_big-picture.md) | **Index:** [All guides](README.md) | **Next:** [02 - Terminal and PowerShell](02_terminal-powershell.md)
<!-- nav:end -->

Quick reference for writing Markdown (README files, notes, GitHub docs).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Markdown?

Markdown is a simple way to format plain text using a few symbols. You write `# Title`, `**bold**` or `- item` in any text editor, and tools like GitHub, VS Code, Jupyter and many note apps turn it into nicely formatted headings, bold text and lists. The file stays readable even without rendering, which is why it is the standard for documentation.

### Why use it?

- **Readable everywhere**: the raw `.md` file is plain text; no special program needed to open it.
- **Standard on GitHub**: every `README.md`, issue, pull request and wiki uses it.
- **Works with Git**: plain text means clean diffs and history (Word files do not).
- **Fast to write**: no mouse, no menus; formatting while you type.
- **Used in many tools**: Jupyter Markdown cells, VS Code previews, documentation sites (MkDocs), chat apps.

### Key terms

| Term | Meaning |
|---|---|
| Render | Turning Markdown symbols into formatted output |
| GFM | GitHub Flavored Markdown: standard Markdown plus tables, task lists, alerts |
| Anchor | Link target created from a heading (`#1-headings`) |
| Code fence | Three backticks that start / end a code block |

**Where it fits:** every guide in this repo is Markdown. Preview it in VS Code with `Ctrl+Shift+V` ([05 - VS Code](05_vscode.md)).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Markdown Guide (basic + extended syntax) | https://www.markdownguide.org/ |
| GitHub: writing on GitHub | https://docs.github.com/en/get-started/writing-on-github |
| GitHub Flavored Markdown spec | https://github.github.com/gfm/ |

---

## Contents

1. [Headings](#1-headings)
2. [Paragraphs and Line Breaks](#2-paragraphs-and-line-breaks)
3. [Text Formatting](#3-text-formatting)
4. [Lists](#4-lists)
5. [Links](#5-links)
6. [Images](#6-images)
7. [Code](#7-code)
8. [Blockquotes](#8-blockquotes)
9. [Tables](#9-tables)
10. [Horizontal Rule](#10-horizontal-rule)
11. [Task Lists](#11-task-lists)
12. [Escaping Characters](#12-escaping-characters)
13. [Table of Contents (Anchor Links)](#13-table-of-contents-anchor-links)
14. [Collapsible Section (GitHub)](#14-collapsible-section-github)
15. [Try It](#15-try-it)

---

## 1. Headings

> Titles that structure a document into levels, from H1 (page title) to H6. Start a line with 1 to 6 `#` characters followed by a space. Use it in every README or note: one H1 for the title, H2 for main sections, H3 for sub-sections.

### ATX style (`#`) - recommended

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

- The number of `#` sets the level (1 = largest, 6 = smallest).
- A space after `#` is required.

### Setext style (underline) - only H1 and H2

```markdown
Heading 1
=========

Heading 2
---------
```

- `=` underline = level 1, `-` underline = level 2.
- The underline must be on the line directly below the text.
- Levels 3 to 6 are not supported.

## 2. Paragraphs and Line Breaks

> Blocks of text and how Markdown decides where a new line starts. Separate paragraphs with an empty line; force a line break inside a paragraph with `<br>`. Use this when your text shows up as one long line on GitHub even though you pressed Enter.

```markdown
First paragraph.

Second paragraph (separated by a blank line).

Line one<br>
Line two (forced line break)
```

A single newline without a blank line does NOT start a new line. Use a blank line, `<br>`, or two trailing spaces.

## 3. Text Formatting

> Inline styles such as bold, italic, strikethrough and inline code. Wrap words in `**`, `*`, `~~` or backticks. Use it for highlight a key word, a warning, or a command name inside a sentence.

| Result | Syntax |
|---|---|
| **Bold** | `**Bold**` |
| *Italic* | `*Italic*` |
| ***Bold and italic*** | `***Bold and italic***` |
| ~~Strikethrough~~ | `~~Strikethrough~~` |
| `Inline code` | `` `Inline code` `` |
| <sub>Subscript</sub> | `<sub>Subscript</sub>` |
| <sup>Superscript</sup> | `<sup>Superscript</sup>` |

## 4. Lists

> Bullet lists and numbered lists, optionally nested. Start lines with `-` (bullets) or `1.` (numbers); indent to nest. Use it for steps to follow (numbered) or a set of features / requirements (bullets).

### Unordered

```markdown
- Item
- Item
  - Nested item (indent 2 spaces)
```

### Ordered

```markdown
1. First
2. Second
   1. Nested (indent 3 spaces)
```

`-`, `*` and `+` all work for unordered lists. Pick one and stay consistent.

## 5. Links

> Clickable references to websites, other files or headings in the same file. `[text](target)` where target is a URL, a relative file path or `#heading-anchor`. Use it for point to official docs, link between your guides, or build a contents list.

```markdown
[Link text](https://example.com)
[Link with hover title](https://example.com "Title")
[Link to another file](10_python-virtual-environment.md)
[Link to a heading](#5-links)
<https://example.com>                   <!-- auto link -->
```

## 6. Images

> Pictures shown inside the document. Same as a link with `!` in front: `![alt](path)`; use HTML `<img>` to resize. Use it for screenshots in a README, architecture diagrams, chart results.

```markdown
![Alt text](path/to/image.png)
![Alt text](https://example.com/image.png "Title")
```

Resize (HTML):

```html
<img src="image.png" width="300">
```

## 7. Code

> Text shown in a monospace font without formatting, with syntax highlighting. Single backticks for inline code; triple backticks plus a language name for blocks. Use it in any command, file name or code snippet someone might copy.

### Inline

```markdown
Use `pip install pandas` to install.
```

### Code block

Wrap with three backticks and add the language name for syntax highlighting:

````markdown
```python
print("Hello")
```
````

Common language names: `python`, `bash`, `powershell`, `json`, `sql`, `html`, `css`, `javascript`, `markdown`.

## 8. Blockquotes

> Indented quote block, plus GitHub coloured alert boxes. Start lines with `>`; add `[!NOTE]`, `[!WARNING]` etc. on the first line for alerts. Use it for quoting someone, or making an important note / warning stand out.

```markdown
> This is a quote.
>
> > Nested quote.
```

GitHub alert boxes:

```markdown
> [!NOTE]
> Useful information.

> [!WARNING]
> Something to be careful about.
```

Other types: `[!TIP]`, `[!IMPORTANT]`, `[!CAUTION]`.

## 9. Tables

> Rows and columns of data. Separate cells with `|` and put a `|---|` line under the header row. Use it for comparisons, option lists, command-vs-meaning references (like this guide).

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| a    |   b    |     c |
| d    |   e    |     f |
```

- `:---` left align, `:---:` center, `---:` right.
- The columns do not need to line up in the source.

## 10. Horizontal Rule

> A horizontal divider line. Three dashes `---` on their own line with a blank line above. Use it for visually separate the contents list from the body, or big parts of a document.

```markdown
---
```

Put a blank line above it, otherwise the text above becomes an H2 (Setext style).

## 11. Task Lists

> Checkboxes that render as ticked / unticked on GitHub. `- [ ]` for open, `- [x]` for done. Use it for to-do lists in a README, PR description or issue.

```markdown
- [x] Done
- [ ] Not done
```

## 12. Escaping Characters

> Showing a Markdown symbol literally instead of it formatting text. Put a backslash `\` before the symbol. Use this when you need a literal `*`, `#` or `_` (for example in a file name) and it keeps turning into formatting.

Put a backslash before a special character to show it literally:

```markdown
\*not italic\*
\# not a heading
```

Characters that can be escaped: `` \ ` * _ { } [ ] ( ) # + - . ! | ``

## 13. Table of Contents (Anchor Links)

> Links that jump to a heading in the same document. GitHub creates an anchor from each heading: lowercase, spaces to `-`, punctuation removed. Use it for long documents: a clickable contents list at the top (every guide here uses one).

Heading anchors are built from the heading text: lowercase, spaces become `-`, punctuation is removed.

```markdown
## 3. Data Manipulation      ->  #3-data-manipulation

- [Data Manipulation](#3-data-manipulation)
```

## 14. Collapsible Section (GitHub)

> A section that is hidden until the reader clicks it. HTML `<details>` with a `<summary>` title; leave a blank line before the content. Use it for long logs, optional details, or FAQ answers that would clutter the page.

```html
<details>
<summary>Click to expand</summary>

Hidden content here (leave a blank line after summary).

</details>
```

## 15. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Setup section

Write a README section with an H2 heading `Setup`, a numbered list of three steps, and a code block containing `uv sync`.

<details markdown="1">
<summary>Solution</summary>

````markdown
## Setup

1. Install uv.
2. Clone the repository.
3. Install dependencies:

```bash
uv sync
```
````

</details>

### Exercise 2: Table

Create a table of three tools with the columns Tool and Purpose, with the Purpose column centred.

<details markdown="1">
<summary>Solution</summary>

```markdown
| Tool | Purpose |
|---|:---:|
| Git | Version control |
| uv | Environments and packages |
| Docker | Containers |
```

</details>

### Exercise 3: Links

Link to the heading `## 4. Lists` in the same file, and to the file `02_terminal-powershell.md`.

<details markdown="1">
<summary>Solution</summary>

```markdown
[Lists](#4-lists)
[Terminal guide](02_terminal-powershell.md)
```

Anchors: lowercase, spaces become `-`, punctuation removed.

</details>

---

<!-- nav:start -->
**Previous:** [00 - Big Picture: How Everything Connects](00_big-picture.md) | **Index:** [All guides](README.md) | **Next:** [02 - Terminal and PowerShell](02_terminal-powershell.md)
<!-- nav:end -->
