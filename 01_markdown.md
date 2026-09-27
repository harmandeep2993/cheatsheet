# 01 - Markdown

Quick reference for writing Markdown (README files, notes, GitHub docs).

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

---

## 1. Headings

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

```markdown
First paragraph.

Second paragraph (separated by a blank line).

Line one<br>
Line two (forced line break)
```

A single newline without a blank line does NOT start a new line. Use a blank line, `<br>`, or two trailing spaces.

## 3. Text Formatting

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

```markdown
[Link text](https://example.com)
[Link with hover title](https://example.com "Title")
[Link to another file](06_python-virtual-environment.md)
[Link to a heading](#5-links)
<https://example.com>                   <!-- auto link -->
```

## 6. Images

```markdown
![Alt text](path/to/image.png)
![Alt text](https://example.com/image.png "Title")
```

Resize (HTML):

```html
<img src="image.png" width="300">
```

## 7. Code

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

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| a    |   b    |     c |
| d    |   e    |     f |
```

- `:---` left align, `:---:` center, `---:` right.
- The columns do not need to line up in the source.

## 10. Horizontal Rule

```markdown
---
```

Put a blank line above it, otherwise the text above becomes an H2 (Setext style).

## 11. Task Lists

```markdown
- [x] Done
- [ ] Not done
```

## 12. Escaping Characters

Put a backslash before a special character to show it literally:

```markdown
\*not italic\*
\# not a heading
```

Characters that can be escaped: `` \ ` * _ { } [ ] ( ) # + - . ! | ``

## 13. Table of Contents (Anchor Links)

Heading anchors are built from the heading text: lowercase, spaces become `-`, punctuation is removed.

```markdown
## 3. Data Manipulation      ->  #3-data-manipulation

- [Data Manipulation](#3-data-manipulation)
```

## 14. Collapsible Section (GitHub)

```html
<details>
<summary>Click to expand</summary>

Hidden content here (leave a blank line after summary).

</details>
```
