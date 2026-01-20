# Headers

There are two way to create headings in Markdown using both ATX-style (`#`) and Setext-style (`=` and `-`) syntax, along with examples and explanations.

### **ATX-style headings using** `#`

ATX-style headings use one or more `#` symbols at the beginning of a line.
The number of `#` symbols determines the heading level.

```
Syntax

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

**Explanation**

- ``#`` creates a level-1 heading (largest).
- ``##`` creates a level-2 heading.
- This continues up to ###### for level-6 (smallest).
- ATX-style headings support six levels.
- A space after # is required.

### **Setext-style headings using** `=` and `-`

Setext-style headings are written by placing underline characters on the
line below the heading text.

```
Syntax

Alt- Heading 7
==============

Alt- Heading 8
--------------

Alt- Heading 9
==============
```
Alt- Heading 7
===
Alt- Heading 8
---
Alt- Heading 9
===
**Explanation**
  - `=`underlines create a level-1 heading (same as #).
  - underlines create a level-2 heading (same as ##).
  - Only two levels are supported in Setext-style.
  - The underline must be on the next line, starting at column 1.
  - This style does not support headings 3–6.
