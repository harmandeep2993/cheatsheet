# 10 - Python Basics

<!-- nav:start -->
**Previous:** [09 - HTTP and APIs](09_http-apis.md) | **Index:** [All guides](../README.md) | **Next:** [11 - Python Virtual Environment](11_python-virtual-environment.md)
<!-- nav:end -->

Quick reference for core Python syntax (Python 3.10+).

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Python?

Python is a general-purpose programming language known for readable, almost English-like code. It is **interpreted** (you run the code directly, no compile step) and **dynamically typed** (you do not declare types). A huge ecosystem of free libraries makes it the leading language for data analysis, machine learning, automation, web APIs and scripting.

### Why use it?

- **Easy to read and learn**: less syntax noise, indentation instead of braces.
- **Libraries for everything**: NumPy, pandas, scikit-learn, FastAPI, requests, and 500,000+ more on PyPI.
- **Data and AI standard**: most data science and ML work is done in Python.
- **Automation**: scripts to rename files, call APIs, process spreadsheets.
- **Runs everywhere**: Windows, macOS, Linux, servers, notebooks.

### Key terms

| Term | Meaning |
|---|---|
| Interpreter | The program that runs Python code (`python`) |
| Script | A `.py` file you run |
| Module / package | A `.py` file / a folder of modules you can import |
| Library | A package made by others (pandas, requests) |
| PyPI | The Python Package Index where libraries are published |
| pip / uv | Tools to install packages |
| Indentation | Spaces at the start of a line that define code blocks |

**Where it fits:** the base for [11 - venv](11_python-virtual-environment.md), [17 - NumPy](17_numpy.md), [18 - Pandas](18_pandas.md), [23 - Scikit-learn](23_scikit-learn.md) and [40 - FastAPI](40_fastapi.md). Next steps: [13 - Pydantic](13_pydantic.md), [14 - Async](14_async-python.md), [15 - pytest](15_pytest.md); for AI work see [26 - LLM Fundamentals](26_llm-fundamentals.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Python documentation | https://docs.python.org/3/ |
| Official Python tutorial | https://docs.python.org/3/tutorial/ |
| Standard library reference | https://docs.python.org/3/library/ |
| PEP 8 style guide | https://peps.python.org/pep-0008/ |

---

## Contents

1. [Run Python](#1-run-python)
2. [Variables and Data Types](#2-variables-and-data-types)
3. [Numbers and Operators](#3-numbers-and-operators)
4. [Strings](#4-strings)
5. [f-Strings and Formatting](#5-f-strings-and-formatting)
6. [Lists](#6-lists)
7. [Tuples](#7-tuples)
8. [Dictionaries](#8-dictionaries)
9. [Sets](#9-sets)
10. [Conditions](#10-conditions)
11. [Loops](#11-loops)
12. [Comprehensions](#12-comprehensions)
13. [Functions](#13-functions)
14. [Lambda, map, filter, sorted](#14-lambda-map-filter-sorted)
15. [Error Handling](#15-error-handling)
16. [Files](#16-files)
17. [Paths (pathlib)](#17-paths-pathlib)
18. [JSON and CSV](#18-json-and-csv)
19. [Modules and Imports](#19-modules-and-imports)
20. [Classes](#20-classes)
21. [Dataclasses](#21-dataclasses)
22. [Type Hints](#22-type-hints)
23. [Useful Built-ins](#23-useful-built-ins)
24. [Dates and Times](#24-dates-and-times)
25. [Logging](#25-logging)
26. [Script Entry Point and Arguments](#26-script-entry-point-and-arguments)
27. [Common Errors](#27-common-errors)
28. [Try It](#28-try-it)

---

## 1. Run Python

> Ways to start Python code. Interactive shell for experiments, `python file.py` for scripts, `-m` for modules.
>
> Use it for quick test in the shell; real work in files.

```powershell
python                          # interactive shell (exit() or Ctrl+Z Enter to leave)
python script.py                # run a file
python -m module_name           # run a module (python -m pip, python -m venv)
python -c "print(1 + 1)"        # run one line
```

## 2. Variables and Data Types

> Names that hold values, and the basic value types. Assign with `=`; Python figures out the type (str, int, float, bool, None).
>
> Use it everywhere; know the types to avoid errors like adding text to a number.

```python
name = "Harman"                 # str
age = 30                        # int
price = 9.99                    # float
active = True                   # bool (True / False)
nothing = None                  # no value

type(age)                       # <class 'int'>
isinstance(age, int)            # True

int("5") ; float("2.5") ; str(10) ; bool(0)   # conversion
a, b = 1, 2                     # multiple assignment
a, b = b, a                     # swap
```

Falsy values: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`. Everything else is truthy.

## 3. Numbers and Operators

> Arithmetic and comparison. Operators `+ - * / // % **`, comparisons return True / False.
>
> Use it for calculations, conditions, loop counters.

```python
7 + 2 ; 7 - 2 ; 7 * 2           # 9, 5, 14
7 / 2                           # 3.5   (always float)
7 // 2                          # 3     (floor division)
7 % 2                           # 1     (remainder)
2 ** 3                          # 8     (power)
abs(-5) ; round(3.14159, 2)     # 5, 3.14
min(3, 1, 2) ; max(3, 1, 2)     # 1, 3
x += 1                          # x = x + 1 (also -=, *=, /=)
1_000_000                       # underscores for readability
```

Comparison: `==  !=  >  <  >=  <=`. Logic: `and  or  not`. Identity: `is`, `is not` (use for `None`).

## 4. Strings

> Working with text. Strings are sequences: index / slice them and use methods like `split`, `replace`, `strip`.
>
> Use it for cleaning input, parsing file names, building messages.

```python
s = "Hello World"
len(s)                          # 11
s[0] ; s[-1]                    # 'H', 'd'
s[0:5]                          # 'Hello'   (end excluded)
s[::-1]                         # reversed

s.lower() ; s.upper() ; s.title()
s.strip()                       # remove spaces at both ends
s.replace("World", "There")
s.split(" ")                    # ['Hello', 'World']
" ".join(["a", "b"])            # 'a b'
s.startswith("He") ; s.endswith("ld")
s.find("o")                     # 4 (index, -1 if missing)
s.count("o")                    # 2
"World" in s                    # True
s.isdigit() ; s.isalpha()
"ab" * 3                        # 'ababab'

multi = """Line 1
Line 2"""
path = r"C:\new\folder"         # raw string: backslashes kept
```

## 5. f-Strings and Formatting

> Putting values into text with formatting. Prefix with `f` and put expressions in `{}`; add `:` format codes.
>
> Use it for printing results, log messages, reports (decimals, percent, thousands separators).

```python
name, score = "Ana", 0.8765
f"Hello {name}"                 # 'Hello Ana'
f"{score:.2f}"                  # '0.88'      2 decimals
f"{score:.1%}"                  # '87.7%'     percent
f"{1234567:,}"                  # '1,234,567' thousands separator
f"{42:05d}"                     # '00042'     pad with zeros
f"{name:<10}|"                  # left align in 10 chars (> right, ^ center)
f"{score=}"                     # 'score=0.8765' (debug)
f"{2 + 3}"                      # expressions allowed
```

## 6. Lists

> Ordered, changeable collections. `[a, b, c]`; add with `append`, remove with `remove` / `pop`, access by index.
>
> Use it in any sequence of items: rows, file names, results you collect in a loop.

Ordered, changeable, allows duplicates.

```python
nums = [3, 1, 2]
nums[0] ; nums[-1] ; nums[1:3]  # index, last, slice
nums.append(4)                  # add to end
nums.insert(0, 10)              # add at position
nums.extend([5, 6])             # add several
nums.remove(10)                 # remove first matching value
nums.pop()                      # remove and return last
nums.pop(0)                     # remove and return at index
del nums[0]
nums.sort()                     # sort in place
nums.sort(reverse=True)
sorted(nums)                    # sorted copy
nums.reverse()
nums.index(2)                   # position of value
nums.count(2)                   # occurrences
len(nums) ; sum(nums) ; min(nums) ; max(nums)
2 in nums                       # membership
copy = nums.copy()              # copy (b = a would share the same list)
list(range(5))                  # [0, 1, 2, 3, 4]
first, *rest = [1, 2, 3]        # unpacking: first=1, rest=[2, 3]
```

## 7. Tuples

> Ordered collections that cannot change. `(a, b)`; often unpacked into variables.
>
> Use it for fixed groups like coordinates, or returning several values from a function.

Ordered, **unchangeable**.

```python
point = (3, 4)
x, y = point                    # unpack
single = (5,)                   # one-element tuple needs a comma
```

## 8. Dictionaries

> Key-value lookup tables. `{"key": value}`; access by key, `.get()` for a safe default.
>
> Use it for config settings, JSON data, counting items, mapping codes to names.

Key-value pairs.

```python
person = {"name": "Ana", "age": 30}
person["name"]                  # 'Ana' (KeyError if missing)
person.get("city")              # None if missing
person.get("city", "unknown")   # default value
person["city"] = "Berlin"       # add / update
person.update({"age": 31, "job": "dev"})
del person["job"]
person.pop("age")               # remove and return
"name" in person                # key exists?
person.keys() ; person.values() ; person.items()

for key, value in person.items():
    print(key, value)

merged = {**a, **b}             # merge (or a | b in 3.9+)
counts = {}
counts[word] = counts.get(word, 0) + 1   # counting pattern
```

## 9. Sets

> Collections of unique values. `{a, b}` or `set(list)`; supports union, intersection, difference.
>
> Use it for removing duplicates, fast "is x in here?" checks, comparing two lists.

Unordered, unique values.

```python
s = {1, 2, 3}
s.add(4) ; s.remove(1) ; s.discard(99)   # discard: no error if missing
set([1, 1, 2])                  # {1, 2}   remove duplicates
a | b                           # union
a & b                           # intersection
a - b                           # difference
empty = set()                   # {} is an empty dict, not a set
```

## 10. Conditions

> Running code only when a condition is true. `if` / `elif` / `else`; `match` for many fixed cases.
>
> Use it for validating input, choosing behaviour based on a value.

```python
if age >= 18:
    print("adult")
elif age >= 13:
    print("teen")
else:
    print("child")

status = "adult" if age >= 18 else "minor"      # one-line if / else

if 0 < x < 10: ...                              # chained comparison
if value is None: ...
if not items: ...                               # empty list check

match command:                                  # Python 3.10+
    case "start":
        run()
    case "stop" | "quit":
        stop()
    case _:
        print("unknown")
```

## 11. Loops

> Repeating code. `for` over any collection; `while` until a condition changes; `break` / `continue` to control it.
>
> Use it for processing each file, row or item; retrying until something succeeds.

```python
for item in ["a", "b", "c"]:
    print(item)

range(5)                        # 0 to 4
range(1, 10, 2)                 # 1, 3, 5, 7, 9

for i, item in enumerate(items):          # index + value
    print(i, item)

for name, score in zip(names, scores):    # two lists together
    print(name, score)

count = 0
while count < 5:
    count += 1

for x in nums:
    if x < 0:
        continue                # skip to next iteration
    if x > 100:
        break                   # exit loop
    print(x)
```

## 12. Comprehensions

> One-line way to build lists, dicts and sets. `[expression for item in items if condition]`.
>
> Use it for transforming or filtering a collection; replaces a 3-line loop with `append`.

```python
[x * 2 for x in nums]                       # list
[x for x in nums if x > 0]                  # with filter
["pos" if x > 0 else "neg" for x in nums]   # with if / else
{x: x ** 2 for x in range(5)}               # dict
{x % 3 for x in nums}                       # set
sum(x * x for x in nums)                    # generator (no list created)
[[r * c for c in range(3)] for r in range(3)]   # nested
```

## 13. Functions

> Reusable, named blocks of code. `def name(params):` with `return`; defaults, `*args` and `**kwargs` for flexible input.
>
> Use it whenever you repeat code or a block does one clear job.

```python
def greet(name, greeting="Hello"):
    """Return a greeting for name."""
    return f"{greeting}, {name}!"

greet("Ana")                        # 'Hello, Ana!'
greet("Ana", greeting="Hi")         # keyword argument

def total(*args):                   # any number of positional args (tuple)
    return sum(args)

def show(**kwargs):                 # any number of keyword args (dict)
    for k, v in kwargs.items():
        print(k, v)

def stats(nums):
    return min(nums), max(nums)     # return several values (tuple)

low, high = stats([3, 1, 2])
```

Never use a mutable default: `def f(items=[])` is shared between calls. Use `items=None` and create the list inside.

## 14. Lambda, map, filter, sorted

> Small anonymous functions and functional helpers. `lambda x: ...` passed to `sorted`, `map`, `filter`, `max`.
>
> Use it for sort by a field, pick the max by a key; short one-off logic.

```python
square = lambda x: x ** 2
list(map(str.upper, ["a", "b"]))                # ['A', 'B']
list(filter(lambda x: x > 0, nums))             # keep positives
sorted(people, key=lambda p: p["age"])          # sort dicts by field
sorted(words, key=len, reverse=True)            # longest first
max(people, key=lambda p: p["age"])             # oldest
any(x > 10 for x in nums) ; all(x > 0 for x in nums)
```

## 15. Error Handling

> Handling errors without crashing. `try` risky code, `except` specific errors, `finally` for cleanup; `raise` your own.
>
> Use it for reading files, parsing user input, calling APIs: things that can fail at runtime.

```python
try:
    value = int(text)
except ValueError:
    value = 0
except (TypeError, KeyError) as e:
    print(f"Error: {e}")
else:
    print("no error")           # runs if no exception
finally:
    print("always runs")        # cleanup

raise ValueError("age must be positive")

class InvalidInputError(Exception):
    """Raised when user input fails validation."""
```

Always catch a specific exception type, never a bare `except:`.

## 16. Files

> Reading and writing text files. `with open(...) as f:` closes the file automatically.
>
> Use it for reading config / data files, writing results or logs.

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    text = f.read()             # whole file as string
    # f.readlines()             # list of lines

with open("notes.txt", encoding="utf-8") as f:
    for line in f:              # line by line (memory friendly)
        print(line.strip())

with open("out.txt", "w", encoding="utf-8") as f:   # "w" overwrite, "a" append
    f.write("Hello\n")
```

`with` closes the file automatically. Modes: `r` read, `w` write, `a` append, `rb` / `wb` binary.

## 17. Paths (pathlib)

> Working with file paths in a way that works on Windows and Linux. `Path` objects joined with `/`; methods to read, write, list and check files.
>
> Use it in any file handling; avoids hard-coded `\` vs `/` problems.

```python
from pathlib import Path

p = Path("data") / "sales.csv"          # join paths (works on all OS)
p.exists() ; p.is_file() ; p.is_dir()
p.name ; p.stem ; p.suffix ; p.parent   # 'sales.csv', 'sales', '.csv', 'data'
p.read_text(encoding="utf-8")
p.write_text("hi", encoding="utf-8")
Path("out").mkdir(parents=True, exist_ok=True)
list(Path("data").glob("*.csv"))        # files matching pattern
list(Path(".").rglob("*.py"))           # recursive
Path.cwd() ; Path.home()
Path(__file__).parent                   # folder of the current script
```

## 18. JSON and CSV

> Reading and writing JSON and CSV with the standard library. `json.load` / `json.dump`; `csv.DictReader` for rows as dicts.
>
> Use it for API responses and config (JSON), small tabular files when pandas is not needed (CSV).

```python
import json
import csv

data = json.loads('{"a": 1}')                   # string -> dict
text = json.dumps(data, indent=2)               # dict -> string
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)                         # file -> dict
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)                # dict -> file

with open("data.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):               # each row as dict
        print(row["name"])
```

For real data work, use pandas (see [18 - Pandas](18_pandas.md)).

## 19. Modules and Imports

> Using code from other files and libraries. `import module` or `from module import name`; folders with `__init__.py` are packages.
>
> Use it for splitting a project into files, using libraries like pandas.

```python
import math
from math import sqrt, pi
import numpy as np                      # alias
from mypackage.utils import helper      # own module (folder with .py files)
```

Import order: standard library, third-party, local (blank line between groups). Keep imports at the top of the file.

```text
project/
  app.py
  utils/
    __init__.py         # makes the folder a package
    helpers.py          # from utils.helpers import clean
```

## 20. Classes

> Custom types that bundle data and behaviour. `class` with `__init__` for data and methods for behaviour; inheritance to extend.
>
> Use it for modelling things with state and actions (an account, an API client, a game object).

```python
class Account:
    """Bank account with a balance."""

    interest = 0.02                         # class attribute (shared)

    def __init__(self, owner, balance=0):
        self.owner = owner                  # instance attribute
        self.balance = balance

    def deposit(self, amount):
        """Add amount to the balance."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def __repr__(self):
        return f"Account({self.owner!r}, {self.balance})"


class SavingsAccount(Account):              # inheritance
    """Account that earns extra interest."""

    def __init__(self, owner, balance=0, rate=0.05):
        super().__init__(owner, balance)
        self.rate = rate


acc = Account("Ana", 100)
acc.deposit(50)
print(acc)                                  # Account('Ana', 150)
```

## 21. Dataclasses

> Classes for holding data with almost no boilerplate. `@dataclass` generates `__init__`, `__repr__` and comparison from type-annotated fields.
>
> Use it for records like a product, config or API result where you mainly store fields.

Less boilerplate for classes that mainly hold data.

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name: str
    price: float
    tags: list[str] = field(default_factory=list)

p = Product("Pen", 1.5)
p                               # Product(name='Pen', price=1.5, tags=[])
```

## 22. Type Hints

> Declaring expected types for variables and functions. `name: type` and `-> return_type`; checked by editors and mypy, not at runtime.
>
> Use it in any code you will maintain; catches bugs early and improves autocomplete.

```python
def average(values: list[float]) -> float:
    return sum(values) / len(values)

name: str = "Ana"
scores: dict[str, int] = {}
maybe: int | None = None        # Python 3.10+ (older: Optional[int])
```

Hints are not enforced at runtime; tools like VS Code (Pylance) and mypy use them to catch bugs.

## 23. Useful Built-ins

> Functions available without importing, plus a few standard helpers. Built-ins like `len`, `zip`, `enumerate`; `Counter` / `defaultdict` from collections.
>
> Use it for counting, pairing lists, looping with an index.

```python
len() ; sum() ; min() ; max() ; abs() ; round()
range() ; enumerate() ; zip() ; sorted() ; reversed()
any() ; all() ; map() ; filter()
input("Your name: ")            # read from keyboard (returns str)
print("a", "b", sep=", ", end="\n")
help(str.split) ; dir(obj)      # documentation, attributes

from collections import Counter, defaultdict
Counter(["a", "b", "a"]).most_common(1)   # [('a', 2)]
groups = defaultdict(list)                # missing key -> empty list
```

## 24. Dates and Times

> Dates, times and time differences. `datetime` objects; `strftime` to text, `strptime` from text, `timedelta` for arithmetic.
>
> Use it for timestamps in logs, date filters, "days until" calculations.

```python
from datetime import datetime, date, timedelta

now = datetime.now()
today = date.today()
now.strftime("%Y-%m-%d %H:%M")                  # datetime -> string
datetime.strptime("2026-09-27", "%Y-%m-%d")     # string -> datetime
tomorrow = today + timedelta(days=1)
(date(2026, 12, 25) - today).days               # days between
```

Format codes: `%Y` year, `%m` month, `%d` day, `%H` hour, `%M` minute, `%S` second, `%A` weekday name.

## 25. Logging

> Recording what a program does, with levels and timestamps. `logging.getLogger(__name__)`, then `.info()`, `.warning()`, `.error()`.
>
> Use it in any script or app beyond a quick test, instead of `print()`.

Use logging instead of `print()` in real programs.

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

logger.debug("details")
logger.info("started")
logger.warning("disk almost full")
logger.error("failed to load %s", filename)
logger.exception("crash")       # inside except: includes traceback
```

## 26. Script Entry Point and Arguments

> Making a file runnable as a script with command-line options. `if __name__ == "__main__":` runs only when executed directly; `argparse` reads options.
>
> Use it for tools you run with different inputs (`python clean.py data.csv --limit 5`).

```python
import argparse


def main():
    """Parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="Process a file.")
    parser.add_argument("path")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print(args.path, args.limit)


if __name__ == "__main__":      # only runs when executed directly, not when imported
    main()
```

```powershell
python script.py data.csv --limit 5
```

## 27. Common Errors

| Error | Meaning / Fix |
|---|---|
| `IndentationError` | Mixed or wrong indentation; use 4 spaces |
| `SyntaxError` | Missing `:`, bracket or quote |
| `NameError: name 'x' is not defined` | Typo, or variable used before assignment |
| `TypeError: can only concatenate str (not "int")` | Convert: `"Age: " + str(age)` or use f-string |
| `TypeError: 'NoneType' object is not subscriptable` | A function returned `None` (missing `return`, or used `list.sort()` result) |
| `IndexError: list index out of range` | Index >= `len(list)` |
| `KeyError: 'x'` | Key missing; use `d.get("x")` |
| `AttributeError: 'list' object has no attribute 'x'` | Wrong type or method name; check `type(obj)` |
| `ValueError: invalid literal for int()` | Converting text that is not a number |
| `ModuleNotFoundError` | Not installed, or wrong venv active (see [11 - Python Virtual Environment](11_python-virtual-environment.md)) |
| `ZeroDivisionError` | Check the divisor before dividing |
| `UnicodeDecodeError` | Open with `encoding="utf-8"` |
| `RecursionError` | Function calls itself without an end condition |

## 28. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Word counts

Print the 3 most common words in a text (case-insensitive).

<details markdown="1">
<summary>Solution</summary>

```python
from collections import Counter

words = text.lower().split()
Counter(words).most_common(3)
```

</details>

### Exercise 2: Filter CSV rows

Write a typed, documented function that returns rows of a CSV whose `amount` is above a threshold.

<details markdown="1">
<summary>Solution</summary>

```python
import csv
from pathlib import Path


def rows_above(path: Path, threshold: float) -> list[dict]:
    """Return CSV rows whose 'amount' column is greater than threshold."""
    with path.open(newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if float(row["amount"]) > threshold]
```

</details>

### Exercise 3: Dict comprehension

From `names = ["Ana", "Bo", "Carla", "Dmitri"]` build `{name: length}` for names longer than 3 characters.

<details markdown="1">
<summary>Solution</summary>

```python
{name: len(name) for name in names if len(name) > 3}     # {'Carla': 5, 'Dmitri': 6}
```

</details>

---

<!-- nav:start -->
**Previous:** [09 - HTTP and APIs](09_http-apis.md) | **Index:** [All guides](../README.md) | **Next:** [11 - Python Virtual Environment](11_python-virtual-environment.md)
<!-- nav:end -->
