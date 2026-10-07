# Authoring kit — writing verified study notes

Subjects written with this kit live in `content-src/authoring/<subject>/` (Python, C, C++, Java, JavaScript, SQL,
Artificial Intelligence, Machine Learning, Deep Learning, Data Science, DSA Basics, DSA Advanced):

```
content-src/authoring/<subject>/
  build.py          imports kit + the topic modules, calls kit.build(out, "Title")
  g1_<group>.py     one module per sidebar group; each topic is a generator function
  g2_<group>.py
```

`python3 content-src/authoring/<subject>/build.py` runs **every** code sample, fails on any error or
output mismatch, and writes `content-src/legacy-html/<subject_dir>/index.html`. That file then goes
through the normal pipeline (`npm run content:extract` → `npm run content:seed:check` → seed).
Never hand-edit the generated HTML.

## A topic

```python
from kit import *

G = "Pointers & Memory"          # sidebar group (topics are listed in module/definition order)

@topic(G, "pointers", "Pointers", "pointer")      # group, id (stable! learner progress is keyed on it), title, Tabler icon
def _():
    yield lead("One-sentence summary shown under the title.")
    yield define("Pointer", "a variable that stores the *address* of another object.")
    yield section("Declaring and dereferencing", "code")
    yield snippet("c", r'''
        #include <stdio.h>
        int main(void) {
            int x = 10;
            int *p = &x;
            *p = 20;
            printf("%d\n", x);
            return 0;
        }
    ''', out="20")
    yield warn("Dereferencing an uninitialised pointer is undefined behaviour.")
    yield qa("What is a dangling pointer?", "A pointer to memory that has been freed…")
```

Topic ids are permanent once published — renaming one resets learners' progress for it.

## Blocks

| Helper | Renders |
|---|---|
| `lead(text)` | subtitle under the title (one per topic, first) |
| `section(title, icon)` | an `h3` sub-heading — these become the topic outline and search keywords |
| `p(text)`, `ul(*items)`, `ol(*items)` | paragraph / lists |
| `define(term, body)` | definition callout |
| `note(body, label)` / `warn(body, label)` | key-point / pitfall callout |
| `good(body)` / `bad(body)` / `dodont(do, dont)` | do / avoid callouts (side by side) |
| `example(body, label)` | worked-example callout |
| `cards((title, body, icon), …, cols=2|3)` | card grid |
| `table(head, *rows)` | table |
| `steps((title, desc), …)` | numbered steps |
| `flow("A", "B", "C")` | A → B → C pipeline |
| `formula(text)` | centred formula line |
| `chips(*items)` | tag chips |
| `qa(question, *answer_parts)` | collapsible interview Q&A |
| `code(src)` | **Python**, executed; `print(x)  # expected` comments are checked |
| `snippet(lang, src, out=…)` | **C / C++ / Java / JavaScript / SQL / Python** (as a separate process), executed; `out` is checked and shown as an Output block |
| `multi(out, py=…, cpp=…, java=…, js=…)` | *(dsakit)* the same program in four language **tabs** with one shared Output block; every version is executed and must print `out` — see [DSA_GUIDE.md](DSA_GUIDE.md) |
| `output(text, caption)` | a plain console block (e.g. a compiler error message) — not executed |
| `shell(src)` | terminal commands — not executed |

Inline markup in every text argument: `` `code` ``, `**bold**`, `*italic*`. Put all code, identifiers,
operators and types in backticks (`int *p`, `char **argv`) — text outside backticks treats `*` as markup.
Text is HTML-escaped for you.

## `snippet(lang, src, out=None, caption=None, *, run=True, setup="", stdin="", args=(), fails=False, flags=())`

| lang | how it runs |
|---|---|
| `c` | `clang -std=c17 -Wall -Wextra -Werror` + AddressSanitizer/UBSan, then runs the binary |
| `cpp` | `clang++ -std=c++20 …` same flags |
| `java` | `java -ea File.java` (JDK 21 single-file launch; the first top-level class must hold `main`) |
| `js` | `node main.mjs` (Node 24, ES module — top-level `await` works) |
| `py` | `python3 -I main.py` in a separate process (use `code()` instead when `print(x)  # expected` comments are enough) |
| `sql` | SQLite 3.53 in memory; every result set is printed as an aligned table (below) |

- `out` — the exact stdout (trailing spaces/newlines ignored). Leave `None` only when the output is
  genuinely non-deterministic (addresses, timing, hash order); the sample still has to run cleanly.
- C/C++/Java sources **without `main`** are compile-checked only — fine for declarations/fragments.
- `fails=True` — the sample must be rejected (compile error, exception, sanitizer report, SQL error).
  Use it for "this is wrong" examples; pair with `output(...)` to show the message if useful.
- `setup` — SQL executed before `src` and not shown (sample tables). `stdin` / `args` — program input.
- `run=False` — not executed at all. Last resort for things that cannot stand alone.
- Results are cached in `content-src/authoring/.cache/` by content hash — rebuilds only run what changed.

SQL result format (produced by the kit, so `out` must match it exactly):

```
name | dept | salary
-----+------+-------
Asha | Eng  | 90000
Ravi | HR   | NULL
```

Several `SELECT`s in one sample print several tables separated by a blank line. Statements that
return no rows print nothing (a SELECT with zero rows still prints its header).

## Style — these are notes, not a textbook

- Scannable: short paragraphs, then a table / cards / code. Every topic has a clear takeaway.
- Show, then explain: a small runnable example with its real output beats a paragraph.
- Name the pitfalls (`warn`) and the interview angle (`qa`) where they matter.
- Consistent order inside a topic: lead → what/why → syntax & examples → pitfalls → Q&A.
