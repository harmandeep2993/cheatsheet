# 06 - Regex

<!-- nav:start -->
**Previous:** [05 - VS Code](05_vscode.md) | **Index:** [All guides](README.md) | **Next:** [07 - YAML, JSON, TOML and .env](07_yaml-json.md)
<!-- nav:end -->

Quick reference for regular expressions (patterns that match text) in Python, pandas, grep, PowerShell, VS Code and SQL.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Regex?

A **regular expression** (regex) is a pattern that describes text. Instead of searching for one exact word, you describe a shape: "four digits, a dash, two digits" (`\d{4}-\d{2}`) or "anything that looks like an email". A regex engine then finds, checks, extracts or replaces every piece of text that matches. The same pattern language works (with small differences) in Python, pandas, SQL, grep, PowerShell, VS Code and most programming languages.

### Why use it?

- **Validate input**: check that an email, postcode or date has the right format.
- **Extract data**: pull numbers, IDs, dates or URLs out of messy text and logs.
- **Clean data**: remove extra spaces, strip symbols from phone numbers, normalise formats.
- **Powerful find-and-replace**: reorder `27/09/2026` into `2026-09-27` across 100 files at once.
- **Search logs**: find every ERROR or WARNING line with one pattern.

### Key terms

| Term | Meaning |
|---|---|
| Pattern | The regex itself, e.g. `\d+` |
| Match | A piece of text the pattern fits |
| Metacharacter | A symbol with special meaning (`. * + ? ^ $`) |
| Character class | A set of allowed characters, e.g. `[a-z]` or `\d` |
| Quantifier | How many times something repeats (`+`, `{3}`) |
| Group | Part of a pattern in `( )` you can extract separately |
| Flag | Option that changes matching, e.g. ignore case |

**Where it fits:** used inside [09 - Python](09_python-basics.md), [17 - Pandas](17_pandas.md), [19 - SQL](19_sql.md), [03 - Linux](03_linux.md) (grep) and [05 - VS Code](05_vscode.md) (search).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Python re module | https://docs.python.org/3/library/re.html |
| Python Regular Expression HOWTO | https://docs.python.org/3/howto/regex.html |
| regex101 (test and explain patterns) | https://regex101.com/ |
| Regular-Expressions.info (tutorial) | https://www.regular-expressions.info/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [What Regex Is](#1-what-regex-is)
2. [Literal Characters and Escaping](#2-literal-characters-and-escaping)
3. [Character Classes](#3-character-classes)
4. [Shorthand Classes](#4-shorthand-classes)
5. [Anchors and Boundaries](#5-anchors-and-boundaries)
6. [Quantifiers](#6-quantifiers)
7. [Greedy vs Lazy](#7-greedy-vs-lazy)
8. [Groups and Alternation](#8-groups-and-alternation)
9. [Named Groups and Backreferences](#9-named-groups-and-backreferences)
10. [Lookahead and Lookbehind](#10-lookahead-and-lookbehind)
11. [Common Patterns](#11-common-patterns)
12. [Python re Module](#12-python-re-module)
13. [Regex in Pandas](#13-regex-in-pandas)
14. [Regex in grep, sed, PowerShell, VS Code](#14-regex-in-grep-sed-powershell-vs-code)
15. [Regex in SQL](#15-regex-in-sql)
16. [Build and Test a Pattern](#16-build-and-test-a-pattern)
17. [Troubleshooting](#17-troubleshooting)
18. [Try It](#18-try-it)

---

## 0. Flags and Parameters

> Options that change how a pattern matches (ignore case, multi-line, ...). Passed as `flags=` in Python, as options in tools, or inline as `(?i)` at the start of a pattern. Use this when your pattern is right but case, line breaks or whitespace stop it from matching.

```text
re.findall(r"\d{4}-\d{2}", text, flags=re.I)
|  |       ||              |     |
|  |       ||              |     +-- flag: ignore case
|  |       ||              +-------- the text to search
|  |       |+----------------------- the pattern
|  |       +------------------------ r"..." raw string: backslashes are kept as-is
|  +-------------------------------- function: return all matches as a list
+----------------------------------- Python regex module
```

| Python flag | Inline | Meaning |
|---|---|---|
| `re.I` / `re.IGNORECASE` | `(?i)` | Ignore upper / lower case |
| `re.M` / `re.MULTILINE` | `(?m)` | `^` and `$` match at every line, not only start / end of text |
| `re.S` / `re.DOTALL` | `(?s)` | `.` also matches newline |
| `re.X` / `re.VERBOSE` | `(?x)` | Allow spaces and `#` comments inside the pattern |
| combine | | `flags=re.I \| re.M` |

| Tool | Option | Meaning |
|---|---|---|
| `grep` | `-E` | Extended regex (`+`, `?`, `\|`, `()` without backslashes) |
| `grep` | `-P` | Perl / Python style regex (`\d`, lookarounds) |
| `grep` | `-o` | Print only the matched part |
| `grep` | `-i` / `-v` | Ignore case / invert match |
| `sed` | `-E` | Extended regex |
| pandas `.str` methods | `regex=True/False` | Treat pattern as regex or as plain text |
| pandas `.str` methods | `case=False` | Ignore case |
| `Select-String` | `-CaseSensitive` | Match case (PowerShell ignores case by default) |
| `Select-String` | `-SimpleMatch` | Plain text, not regex |

---

## 1. What Regex Is

> A mini-language for describing text patterns. A pattern like `\d{3}` is compared against text; the engine reports where it matches. Use it for validating input (emails, dates), extracting parts of text, find-and-replace with rules.

```text
Pattern:  \d{4}-\d{2}-\d{2}
Text:     Order placed on 2026-09-27 and shipped 2026-09-29
Matches:  2026-09-27, 2026-09-29
```

Use regex when simple methods (`in`, `startswith`, `split`) are not enough. For HTML / JSON use a real parser instead.

## 2. Literal Characters and Escaping

> Most characters match themselves; some have special meaning and must be escaped. Put `\` before a special character to match it literally. Use it for matching dots in file names or IPs, brackets, `$` in prices, etc.

Special characters: `. ^ $ * + ? { } [ ] \ | ( )`

| Pattern | Matches |
|---|---|
| `cat` | the text "cat" |
| `3.14` | "3.14" but also "3x14" (`.` = any character) |
| `3\.14` | only "3.14" |
| `\$100` | "$100" |
| `\(note\)` | "(note)" |
| `C:\\Users` | "C:\Users" |

Python: always write patterns as raw strings `r"..."` so `\d` is not changed by Python first. `re.escape(text)` escapes a whole string for you.

## 3. Character Classes

> A set of characters, any ONE of which can match at that position. List characters in `[ ]`; use `-` for ranges and `^` at the start for "not". Use it to answer questions like "a vowel", "a digit or dash", "anything except a comma".

| Pattern | Matches one character that is |
|---|---|
| `[aeiou]` | a vowel |
| `[a-z]` | a lowercase letter |
| `[A-Za-z]` | any letter |
| `[0-9]` | a digit |
| `[a-zA-Z0-9_]` | letter, digit or underscore |
| `[^0-9]` | NOT a digit |
| `[^,]` | anything except a comma |
| `[.-]` | a dot or a dash (inside `[ ]` most specials are literal; put `-` first or last) |

## 4. Shorthand Classes

> Short names for common character classes. A backslash plus a letter; uppercase means "not". Use it in almost every pattern: digits, words and whitespace.

| Pattern | Means | Opposite |
|---|---|---|
| `.` | any character except newline | |
| `\d` | digit `[0-9]` | `\D` not a digit |
| `\w` | word character `[A-Za-z0-9_]` | `\W` not a word character |
| `\s` | whitespace (space, tab, newline) | `\S` not whitespace |
| `\t` / `\n` | tab / newline | |

## 5. Anchors and Boundaries

> Positions, not characters: start, end, word edges. `^` start, `$` end, `\b` edge between a word character and a non-word character. Use it for validating a whole string (`^...$`) or matching whole words only (`\bcat\b` not "category").

| Pattern | Matches |
|---|---|
| `^Hello` | "Hello" at the start |
| `world$` | "world" at the end |
| `^\d+$` | the whole string is digits |
| `\bcat\b` | "cat" as a whole word (not "concat") |
| `\Bcat` | "cat" inside a word |

With `re.M`, `^` and `$` work per line.

## 6. Quantifiers

> How many times the previous item may repeat. Put the quantifier right after a character, class or group. Use it to answer questions like "one or more digits", "optional s", "exactly 5 characters".

| Pattern | Means | Example | Matches |
|---|---|---|---|
| `*` | 0 or more | `ab*` | "a", "ab", "abbb" |
| `+` | 1 or more | `\d+` | "7", "2026" |
| `?` | 0 or 1 (optional) | `colou?r` | "color", "colour" |
| `{3}` | exactly 3 | `\d{3}` | "123" |
| `{2,4}` | 2 to 4 | `\d{2,4}` | "12", "1234" |
| `{2,}` | 2 or more | `\w{2,}` | words with 2+ characters |

## 7. Greedy vs Lazy

> Whether a quantifier takes as much or as little text as possible. Quantifiers are greedy by default; add `?` after them to make them lazy. Use it for extracting text between delimiters (tags, quotes) where greedy grabs too much.

```text
Text:     <b>one</b> and <b>two</b>
<.*>      -> <b>one</b> and <b>two</b>     greedy: longest possible
<.*?>     -> <b>  </b>  <b>  </b>           lazy: shortest possible
```

Lazy forms: `*?`, `+?`, `??`, `{2,5}?`. Often clearer: use a negated class `<[^>]*>`.

## 8. Groups and Alternation

> Treat part of a pattern as a unit, capture it, or offer alternatives. `( )` groups and captures, `(?: )` groups without capturing, `|` means "or". Use it for extracting parts (year, month, day), repeating a group, matching one of several words.

| Pattern | Means |
|---|---|
| `(ab)+` | "ab" repeated: "ab", "abab" |
| `cat\|dog` | "cat" or "dog" |
| `(jpg\|png)$` | ends with jpg or png |
| `(\d{4})-(\d{2})` | captures year as group 1, month as group 2 |
| `(?:Mr\|Ms)\. \w+` | group for `\|` without capturing it |

```python
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Due 2026-09-27")
m.group(0)      # '2026-09-27'  whole match
m.group(1)      # '2026'
m.groups()      # ('2026', '09', '27')
```

## 9. Named Groups and Backreferences

> Groups with names, and patterns that refer to an earlier captured group. `(?P<name>...)` names a group in Python; `\1` or `(?P=name)` repeats what group 1 matched. Use it for readable extraction code; finding repeated words; reordering in replacements.

```python
m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})", "2026-09")
m["year"] ; m.groupdict()               # '2026', {'year': '2026', 'month': '09'}

re.findall(r"\b(\w+) \1\b", "this is is a test test")   # ['is', 'test']  repeated words
re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1", "27/09/2026")   # '2026-09-27'
```

In replacements: Python uses `\1` or `\g<name>`; VS Code and JavaScript use `$1`.

## 10. Lookahead and Lookbehind

> Conditions on what comes before or after, without including it in the match. `(?=...)` followed by, `(?!...)` not followed by, `(?<=...)` preceded by, `(?<!...)` not preceded by. Use it to answer questions like "Number followed by EUR", "price after $", password rules.

| Pattern | Matches |
|---|---|
| `\d+(?= EUR)` | "100" in "100 EUR" (not the " EUR") |
| `(?<=\$)\d+` | "50" in "$50" |
| `\b(?!un)\w+` | words that do NOT start with "un" |
| `\d+(?! EUR)\b` | numbers NOT followed by " EUR" |
| `^(?=.*\d)(?=.*[A-Z]).{8,}$` | at least 8 chars with a digit and an uppercase letter |

Lookbehind in Python must have a fixed length (`(?<=\$)` ok, `(?<=\$+)` not).

## 11. Common Patterns

> Ready-made patterns for everyday data. Copy, then test on your own examples; real-world formats vary. Use this when cleaning and validating data; these are practical, not perfect, validators.

| Data | Pattern |
|---|---|
| Integer | `^-?\d+$` |
| Decimal number | `^-?\d+(\.\d+)?$` |
| Email (practical) | `^[\w.+-]+@[\w-]+\.[\w.-]+$` |
| Date YYYY-MM-DD | `^\d{4}-(0[1-9]\|1[0-2])-(0[1-9]\|[12]\d\|3[01])$` |
| Time HH:MM (24h) | `^([01]\d\|2[0-3]):[0-5]\d$` |
| IPv4 (shape only) | `^(\d{1,3}\.){3}\d{1,3}$` |
| URL | `https?://[^\s]+` |
| German postcode | `^\d{5}$` |
| Phone (digits, spaces, +, -) | `^\+?[\d\s-]{7,15}$` |
| Hex colour | `^#([0-9a-fA-F]{3}){1,2}$` |
| Hashtag | `#\w+` |
| Extra whitespace | `\s{2,}` (replace with one space) |
| Leading / trailing spaces | `^\s+\|\s+$` |
| File extension | `\.([a-zA-Z0-9]+)$` |
| Python log line | `^(\S+ \S+) (INFO\|WARNING\|ERROR) (.*)$` |

## 12. Python re Module

> Python's built-in regex functions. `import re`; choose the function by what you want back (first match, all matches, replaced text). Use it in any regex work in plain Python scripts.

```python
import re

text = "Orders: A-102 (12 EUR), B-7 (5 EUR)"

re.search(r"\d+", text)             # first match anywhere -> Match object or None
re.match(r"Orders", text)           # match only at the START
re.fullmatch(r"\d+", "2026")        # the WHOLE string must match (validation)
re.findall(r"\d+ EUR", text)        # all matches -> ['12 EUR', '5 EUR']
re.findall(r"([A-Z])-(\d+)", text)  # with groups -> [('A', '102'), ('B', '7')]
re.finditer(r"\d+", text)           # iterator of Match objects (positions too)
re.sub(r"\s+", " ", text)           # replace -> new string
re.sub(r"\d+", lambda m: str(int(m[0]) * 2), text)   # replace with a function
re.split(r"[,;]\s*", "a, b;c")      # split -> ['a', 'b', 'c']

pattern = re.compile(r"\b[A-Z]-\d+\b")   # compile once, reuse many times
pattern.findall(text)

m = re.search(r"(\d+) EUR", text)
if m:                                     # always check for None
    m.group(1) ; m.start() ; m.end() ; m.span()
```

| Function | Returns | Use for |
|---|---|---|
| `search` | first Match or None | "is it anywhere?" + extract |
| `match` | Match at start or None | prefix check |
| `fullmatch` | Match of whole string or None | validation |
| `findall` | list of strings / tuples | extract all |
| `finditer` | iterator of Match | extract all with positions |
| `sub` | new string | replace |
| `split` | list | split by pattern |

## 13. Regex in Pandas

> Regex on a whole text column at once. `.str` methods accept regex patterns; `extract` turns groups into new columns. Use it for cleaning messy text columns, extracting codes / numbers, filtering rows by pattern.

```python
df[df["email"].str.contains(r"@gmail\.com$", regex=True)]           # filter rows
df["email"].str.match(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")                # True / False per row
df["phone"] = df["phone"].str.replace(r"[^\d+]", "", regex=True)    # keep digits and +
df[["year", "month"]] = df["date"].str.extract(r"(\d{4})-(\d{2})")  # groups -> columns
df["code"].str.extract(r"(?P<letter>[A-Z])-(?P<num>\d+)")           # named groups = column names
df["tags"].str.findall(r"#\w+")                                     # list of matches per row
df["text"].str.count(r"\d")                                         # count matches
df.filter(regex=r"^sales_")                                         # select columns by name
df.replace(r"^\s*$", np.nan, regex=True)                            # empty strings -> NaN
```

See [17 - Pandas](17_pandas.md).

## 14. Regex in grep, sed, PowerShell, VS Code

> Using patterns in command-line tools and the editor. Each tool has a regex mode; syntax differs slightly (basic vs extended vs Perl style). Use it for searching logs, bulk renames, find-and-replace across a project.

```bash
grep -E "ERROR|WARN" app.log                    # lines with ERROR or WARN
grep -oE "[0-9]{1,3}(\.[0-9]{1,3}){3}" access.log | sort | uniq -c   # count IPs
grep -P "\d{4}-\d{2}-\d{2}" file.txt            # Perl style: \d works
sed -E 's/([0-9]{2})\/([0-9]{2})\/([0-9]{4})/\3-\2-\1/g' dates.txt   # reorder dates
```

```powershell
Select-String -Path *.log -Pattern "ERROR|WARN"
"2026-09-27" -match "(\d{4})-(\d{2})"; $Matches[1]      # '2026'
"a  b   c" -replace "\s+", " "                          # 'a b c'
"a,b;c" -split "[,;]"
```

VS Code: `Ctrl+H`, turn on regex (`Alt+R`), use `$1` in the replacement. See [05 - VS Code](05_vscode.md).

Basic `grep` / `sed` (without `-E`) need `\+`, `\?`, `\|`, `\(\)`; use `-E` to avoid that.

## 15. Regex in SQL

> Pattern matching inside database queries. Each database has its own operator or function. Use it when `LIKE` with `%` and `_` is not flexible enough.

```sql
-- PostgreSQL
SELECT * FROM users WHERE email ~ '@gmail\.com$';        -- match (case-sensitive)
SELECT * FROM users WHERE email ~* '@GMAIL\.com$';       -- ignore case
SELECT * FROM users WHERE email !~ '@';                  -- does not match
SELECT REGEXP_REPLACE(phone, '[^0-9]', '', 'g') FROM users;
SELECT SUBSTRING(code FROM '[0-9]+') FROM items;

-- MySQL 8
SELECT * FROM users WHERE email REGEXP '@gmail\\.com$';
SELECT REGEXP_REPLACE(phone, '[^0-9]', '') FROM users;

-- SQLite: no built-in REGEXP function; use LIKE / GLOB or do it in Python / pandas
```

See [19 - SQL](19_sql.md).

## 16. Build and Test a Pattern

> A reliable way to write patterns without guessing. Start small, test on real examples (matches AND non-matches), add pieces one at a time. Use it in every non-trivial pattern.

1. Collect 5 to 10 real examples, including ones that should NOT match.
2. Test at **regex101.com** (choose the Python flavor); it explains every token.
3. Start with the fixed part, then add classes and quantifiers.
4. Add `^...$` if the whole string must match.
5. Use `re.VERBOSE` for long patterns:

```python
DATE = re.compile(r"""
    (?P<year>\d{4})  -     # year
    (?P<month>\d{2}) -     # month
    (?P<day>\d{2})         # day
""", re.VERBOSE)
```

## 17. Troubleshooting

| Problem | Fix |
|---|---|
| `\d` does not work in Python | Use a raw string: `r"\d+"` |
| `re.match` finds nothing but the text is there | `match` only checks the start; use `re.search` |
| Pattern matches too much | Greedy quantifier; use `.*?` or a negated class `[^"]*` |
| `.` matched a real dot and something else | Escape it: `\.` |
| `AttributeError: 'NoneType' object has no attribute 'group'` | No match; check `if m:` before `m.group()` |
| `findall` returns tuples instead of strings | Pattern has groups; use `(?:...)` for groups you do not want back |
| `^` / `$` only match once in multi-line text | Add `re.M` |
| `.` does not cross line breaks | Add `re.S` |
| pandas `FutureWarning` about `regex` | Pass `regex=True` or `regex=False` explicitly |
| grep ignores `\d` or `+` | Use `grep -E` (and `[0-9]` instead of `\d`) or `grep -P` |
| `look-behind requires fixed-width pattern` | Python lookbehind cannot use `*`, `+`; restructure or use the `regex` package |

## 18. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Reformat dates

Convert all dates written `DD.MM.YYYY` in a text to `YYYY-MM-DD`.

<details markdown="1">
<summary>Solution</summary>

```python
import re
re.sub(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", r"\3-\2-\1", "Due 27.09.2026 and 01.10.2026")
# 'Due 2026-09-27 and 2026-10-01'
```

</details>

### Exercise 2: Hashtags

Extract all hashtags from `"Loving #python and #AI-tools today"`.

<details markdown="1">
<summary>Solution</summary>

```python
re.findall(r"#\w+", "Loving #python and #AI-tools today")     # ['#python', '#AI']
re.findall(r"#[\w-]+", "Loving #python and #AI-tools today")  # ['#python', '#AI-tools']
```

</details>

### Exercise 3: Order IDs in pandas

A column `note` contains text like `refund for A-1042 please`. Put the order ID into a new column.

<details markdown="1">
<summary>Solution</summary>

```python
df["order_id"] = df["note"].str.extract(r"\b([A-Z]-\d{4})\b", expand=False)
```

</details>

### Exercise 4: Whole-string validation

Check that a string is exactly a 5-digit German postcode.

<details markdown="1">
<summary>Solution</summary>

```python
bool(re.fullmatch(r"\d{5}", "10115"))     # True
bool(re.fullmatch(r"\d{5}", "10115 X"))   # False  (fullmatch = whole string)
```

</details>

---

<!-- nav:start -->
**Previous:** [05 - VS Code](05_vscode.md) | **Index:** [All guides](README.md) | **Next:** [07 - YAML, JSON, TOML and .env](07_yaml-json.md)
<!-- nav:end -->
