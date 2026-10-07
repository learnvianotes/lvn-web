# Writing the DSA Basics / DSA Advanced notes

Read `content-src/authoring/README.md` (the kit) first. This file adds the rules specific to the two DSA
subjects, which are rebuilt from the learner's original scattered notes into proper study notes.

## What you are producing

One Python module per group of topics in `content-src/authoring/dsa-basics/` or `dsa-advanced/`.
Each topic is a generator function decorated with `@topic(GROUP, ID, TITLE, ICON)`.

**Non-negotiable**

- Topic **ids and titles are fixed** — use exactly the id/title you were given. Learner progress is
  keyed on the id; the title is what the learner already knows the topic as.
- Use the **group** string you were given (it becomes the sidebar heading).
- **Every algorithm / problem solution is written in all four languages** with `multi(...)`:
  Python, C++, Java, JavaScript. All four are executed at build time and must print the identical
  output, or the build fails. Brute-force versions that exist only to motivate the efficient one may
  be Python-only (`snippet("py", src, out=...)`) — but the solution the learner should remember is
  always in all four.
- **Keep every concept and problem of the original notes.** The source for each topic is
  `content-build/topics/<subject>/<id>.json` (field `html`): read it fully, then rewrite. Fix its
  typos (“Bineay”, “Reecursive”), wrong statements and broken code; add the fundamentals it skipped
  (definition, why it matters, complexity, pitfalls, interview Q&A). Do not drop a problem because it is
  tedious to port.
- ASCII drawings (trees, arrays, matrices) go in `diagram(text, caption)` — never in paragraphs.
- Numbered lines of the original (“1. Distinct elements”, “-> Adjacency Matrix”) become real `ul()`/
  `ol()` lists, `table()`s or `cards()` — never a run of one-line paragraphs.

## Helpers (dsakit, on top of kit)

```python
from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall
```

| Helper | Use |
|---|---|
| `multi(out, py=…, cpp=…, java=…, js=…)` | the same program in four tabs; `out` is the exact shared stdout, shown once below |
| `complexity("O(n)", "O(1)")` | chips under every solution (time, space) |
| `io("arr = [1,2,3]", "6", "arr = []", "0")` | an Example callout with Input/Output pairs — put one before every problem |
| `diagram(text, caption)` | monospaced drawing |
| `idea(text)` | the one-paragraph insight behind a solution |
| `pitfall(text)` | the classic mistake |

Everything else from the kit: `lead`, `define`, `section(title, icon)`, `p`, `ul`, `ol`, `table`,
`cards`, `steps`, `flow`, `note`, `warn`, `good`/`bad`, `example`, `formula`, `chips`, `qa`,
`snippet(lang, src, out=…)` (single language, also `"py"`), `output(text, caption)`.

## Shape of a topic

```
lead            one sentence: what it is and why it matters
define          the term
diagram         when a picture helps (tree, list, array with indices)
section …       concept sections: how it works, operations table with complexities, variants
section …       one section per problem/algorithm from the notes:
                  io() example → idea() → (steps()) → multi() → complexity() → pitfall()/note()
section "Interview Q&A"   3–6 qa() items at the end
```

Notes, not a textbook: short paragraphs, then a table / list / code. Explain *why* the algorithm works
in one or two sentences before the code. Comments inside the code mark the key lines.

## Code rules (the build enforces these)

- **Identical output in all four languages.** Print the same text. Avoid language-specific
  formatting: no Python list reprs (`[1, 2]`) unless you build the same string elsewhere; print
  space-separated values or `key: value` lines. Booleans: print `true`/`false` (or `Yes`/`No`) explicitly
  in every language — Python's `True` differs from Java's `true`. Floats: avoid, or format to fixed
  decimals in every language.
- **Python** runs as `python3 -I main.py`. Recursion limit is 1000 — keep inputs small.
- **C++** compiles with `clang++ -std=c++20 -Wall -Wextra -Werror` plus AddressSanitizer/UBSan.
  Signed/unsigned comparison is an error: write `int n = v.size();` and loop with `int`, or use
  `size_t` consistently. Every `new` needs a `delete` is **not** required (leak detection is off) but
  out-of-bounds and use-after-free fail the build. Add `#include`s explicitly (`<vector>`, `<string>`,
  `<algorithm>`, `<unordered_map>`, …). `using namespace std;` is fine.
- **Java** runs as a single file (`java -ea Main.java`): the **first top-level class must be
  `public class Main`** containing `main`; put helper classes as `static class` inside it or as
  non-public top-level classes after it. `-Xlint:all -Werror` is only used when there is no `main`.
- **JavaScript** runs on Node 24 as an ES module (`console.log`, `const`, classes; top-level `await` ok).
- One `multi()` = one self-contained program per language, each with its own driver (`main`) that
  prints the result for the example inputs. Keep programs under ~60 lines where possible.
- Use the example inputs from `io()` so the reader sees the same numbers in the example and the output.

## Text rules

- Inline markup in text arguments: `` `code` ``, `**bold**`, `*italic*`. Put all identifiers, operators
  and complexities in backticks: `` `O(n log n)` ``, `` `arr[i]` ``. Outside backticks, `*` is markup.
- Headings (`section()`) are the topic outline the learner sees and searches — make them the problem
  or concept name, not “Method 1” or “Idea”.
- Choose Tabler icon names for `@topic` and `section`: e.g. `list-numbers`, `binary-tree`, `hierarchy`,
  `git-branch`, `hash`, `search`, `arrows-sort`, `stack-2`, `list`, `math-function`, `repeat`, `brackets`,
  `table`, `grid-dots`, `route`, `topology-star`, `binary`, `bolt`, `brain`, `puzzle`, `coin`, `clock`,
  `arrows-shuffle`, `message-question`, `alert-triangle`, `bulb`, `apps`, `box`, `link`, `chart-bar`.

## Check your work

```
python3 content-src/authoring/check.py dsa-basics g6_stacks_queues        # one or more modules
```

It imports only your module(s), runs every snippet and prints failures with their source. Fix until it
prints `OK`. It also writes `content-src/authoring/.cache/preview-<subject>.html` for a quick look.
Do **not** run `build.py`, `npm run content:*`, the seeder or git — the integrator does that once all
modules exist. Do not edit `kit.py`, `dsakit.py` or other modules.

The reference implementation is `content-src/authoring/dsa-basics/g6_stacks_queues.py` (topic `stack`).
