from kit import *

G = "Getting Started"


@topic(G, "intro", "Introduction to Python", "brand-python")
def _():
    yield lead("A high-level, interpreted, dynamically typed language that favours readability — the most common language for interviews, scripting, data and AI.")
    yield define("Python", "a general-purpose language where *code is compiled to bytecode and run by a virtual machine* (CPython). You write less code per idea than in C++ or Java, at the cost of raw speed.")
    yield section("Why Python?", "bulb")
    yield cards(
        ("Readable", "Indentation is syntax, so code looks like pseudocode. Ideal for interviews — the interviewer reads your logic, not boilerplate.", "eye"),
        ("Batteries included", "A huge standard library: `collections`, `itertools`, `heapq`, `bisect`, `functools`, `json`, `re`, `pathlib`…", "package"),
        ("Dynamic typing", "Types belong to *values*, not variables. A name can point to an `int` now and a `str` later.", "arrows-shuffle"),
        ("Everywhere", "Web back ends (Django, FastAPI), automation, data science (pandas, NumPy), ML (PyTorch), scripting.", "world"),
    )
    yield section("How Python runs your code", "cpu")
    yield steps(
        ("Source", "You write `app.py` — plain text."),
        ("Compile to bytecode", "CPython parses it and compiles it to bytecode (cached as `__pycache__/*.pyc`)."),
        ("Run on the PVM", "The Python Virtual Machine executes the bytecode instruction by instruction — that is the “interpreted” part."),
    )
    yield table(
        ["Implementation", "What it is"],
        ["**CPython**", "The reference implementation, written in C. What you get from python.org. Has the GIL."],
        ["**PyPy**", "JIT-compiled — often several times faster for long-running pure-Python code."],
        ["**Jython / IronPython**", "Python on the JVM / .NET (rarely used today)."],
    )
    yield section("Your first program", "code")
    yield code('''
        name = "Python"
        version = 3
        print(f"Hello, {name} {version}!")   # Hello, Python 3!
        print(type(name), type(version))    # <class 'str'> <class 'int'>
    ''')
    yield shell('''
        $ python3 --version          # check the installed version
        $ python3 app.py             # run a file
        $ python3                    # interactive REPL (exit with Ctrl-D)
        $ python3 -m venv .venv      # create an isolated environment
    ''')
    yield section("Style: PEP 8 and the Zen", "writing")
    yield ul(
        "4 spaces per indent level, never tabs.",
        "`snake_case` for variables and functions, `PascalCase` for classes, `UPPER_CASE` for constants.",
        "Lines around 79–99 characters; one statement per line.",
        "Run `import this` to read *The Zen of Python* — “Readability counts.”, “Explicit is better than implicit.”",
    )
    yield note("Python 2 reached end-of-life in 2020. Everything in these notes is Python 3 (3.10+ for `match`).", "Version")


@topic(G, "variables-types", "Variables, Types & Operators", "variable")
def _():
    yield lead("A variable is a *name bound to an object*. Every object has an identity, a type and a value.")
    yield define("Name binding", "`x = 10` creates an `int` object and binds the name `x` to it. Assignment never copies — it only attaches another name to the same object.")
    yield section("Built-in types", "box")
    yield table(
        ["Type", "Example", "Mutable?"],
        ["`int`", "`42`, `-7`, `10**100` (unlimited size)", "No"],
        ["`float`", "`3.14`, `1e-9` (64-bit IEEE 754)", "No"],
        ["`complex`", "`2 + 3j`", "No"],
        ["`bool`", "`True`, `False` (a subclass of `int`)", "No"],
        ["`str`", "`'hi'`, `\"hi\"`, `'''multi'''`", "No"],
        ["`NoneType`", "`None` — the single “no value” object", "No"],
        ["`list` / `dict` / `set`", "`[1, 2]`, `{'a': 1}`, `{1, 2}`", "**Yes**"],
        ["`tuple` / `frozenset`", "`(1, 2)`, `frozenset({1})`", "No"],
    )
    yield code('''
        x = 10
        print(type(x))                    # <class 'int'>
        x = "now a string"                # same name, different object and type
        print(isinstance(x, str))         # True
        print(True + True)                # 2
    ''')
    yield section("Operators", "math-symbols")
    yield table(
        ["Kind", "Operators", "Notes"],
        ["Arithmetic", "`+ - * / // % **`", "`/` always returns a float; `//` floors; `**` is power"],
        ["Comparison", "`== != < <= > >=`", "Chainable: `0 < x < 10`"],
        ["Logical", "`and or not`", "Short-circuit and return an *operand*, not just `True`/`False`"],
        ["Identity", "`is`, `is not`", "Same object? Use for `None`: `x is None`"],
        ["Membership", "`in`, `not in`", "O(1) for `set`/`dict`, O(n) for `list`"],
        ["Bitwise", "`& | ^ ~ << >>`", "Also set union / intersection on `set`s"],
        ["Assignment expression", "`:=` (walrus)", "Assign inside an expression (3.8+)"],
    )
    yield code('''
        print(7 / 2, 7 // 2, 7 % 2, -7 // 2)   # 3.5 3 1 -4
        print(2 ** 10, divmod(17, 5))          # 1024 (3, 2)
        print(0 < 5 < 10)                      # True
        print("" or "default", 0 and 99)       # default 0
        if (n := len("hello")) > 3:
            print(n)                           # 5
    ''')
    yield section("`==` vs `is`", "equal")
    yield cards(
        ("`==` — equality", "Calls `__eq__`: do the two objects have the *same value*?", "equal"),
        ("`is` — identity", "Are they the *same object* in memory (same `id`)? Use only for singletons: `None`, `True`, `False`.", "fingerprint"),
    )
    yield code('''
        a = [1, 2, 3]
        b = [1, 2, 3]
        c = a
        print(a == b, a is b, a is c)   # True False True
    ''')
    yield warn("CPython caches small integers (−5…256) and some strings, so `a is b` may be `True` for them by accident. Never rely on it — compare values with `==`.")
    yield section("Truthiness", "toggle-left")
    yield p("In a condition, every object is truthy except these **falsy** values:")
    yield chips("`False`", "`None`", "`0`, `0.0`, `0j`", "`''`", "`[]`", "`()`", "`{}`", "`set()`", "`range(0)`")
    yield code('''
        items = []
        if not items:              # idiomatic emptiness check
            print("empty")         # empty
        print(bool("0"), bool(0))  # True False
    ''')
    yield section("Type conversion", "transform")
    yield code('''
        print(int("42") + 1, float("2.5"), str(99) + "!")   # 43 2.5 99!
        print(int(3.99), round(2.5), round(3.5))            # 3 2 4
        print(int("ff", 16), bin(10), hex(255))             # 255 0b1010 0xff
    ''')
    yield note("`round()` uses *banker's rounding*: halves go to the nearest even number, so `round(2.5) == 2`.")


@topic(G, "strings", "Strings", "letter-case")
def _():
    yield lead("`str` is an immutable sequence of Unicode characters — indexing, slicing and methods all return *new* strings.")
    yield section("Indexing & slicing", "cut")
    yield p("`s[start:stop:step]` — `start` is included, `stop` is excluded, negative indices count from the end.")
    yield code('''
        s = "interview"
        print(s[0], s[-1], len(s))      # i w 9
        print(s[0:5], s[5:], s[-4:])    # inter view view
        print(s[::-1], s[::2])          # weivretni itriw
    ''')
    yield section("Immutability", "lock")
    yield code('''
        s = "cat"
        try:
            s[0] = "b"
        except TypeError as e:
            print("TypeError:", e)       # TypeError: 'str' object does not support item assignment
        s = "b" + s[1:]                  # build a new string instead
        print(s)                         # bat
    ''')
    yield warn("Building a string with `+=` in a loop can be O(n²). Collect pieces in a list and call `''.join(parts)` once — O(n).", "Performance")
    yield section("Essential methods", "list")
    yield table(
        ["Method", "Does", "Example → result"],
        ["`split(sep)` / `join(it)`", "String ↔ list", "`'a,b'.split(',')` → `['a', 'b']`"],
        ["`strip()` / `lstrip()` / `rstrip()`", "Trim whitespace (or given chars)", "`'  hi '.strip()` → `'hi'`"],
        ["`lower()` / `upper()` / `title()`", "Change case", "`'Py'.lower()` → `'py'`"],
        ["`find(x)` / `index(x)`", "Position or −1 / raises", "`'abc'.find('z')` → `-1`"],
        ["`replace(a, b)`", "Replace all occurrences", "`'aa'.replace('a','b')` → `'bb'`"],
        ["`startswith` / `endswith`", "Prefix / suffix test", "`'file.py'.endswith('.py')` → `True`"],
        ["`isdigit` / `isalpha` / `isalnum`", "Character classes", "`'123'.isdigit()` → `True`"],
        ["`count(x)`", "Non-overlapping occurrences", "`'banana'.count('a')` → `3`"],
    )
    yield code('''
        words = "  the quick  brown fox ".split()   # split() with no args handles runs of spaces
        print(words)                                 # ['the', 'quick', 'brown', 'fox']
        print("-".join(words))                       # the-quick-brown-fox
        print(" ".join(w.capitalize() for w in words))   # The Quick Brown Fox
    ''')
    yield section("f-strings & formatting", "braces")
    yield code('''
        name, score, ratio = "Asha", 93, 0.8567
        print(f"{name} scored {score}")          # Asha scored 93
        print(f"{ratio:.2%} | {score:05d}")      # 85.67% | 00093
        print(f"{name!r:>8}|{score:<5}|")        #   'Asha'|93   |
        print(f"{score=}")                       # score=93
        print(f"{1_000_000:,}")                  # 1,000,000
    ''')
    yield section("Characters, Unicode & bytes", "language")
    yield code('''
        print(ord("A"), chr(97))                 # 65 a
        print(len("naïve"), len("naïve".encode("utf-8")))   # 5 6
        print("é".encode(), b"\\xc3\\xa9".decode())          # b'\\xc3\\xa9' é
    ''')
    yield cards(
        ("`str`", "Text — a sequence of Unicode code points.", "letter-case"),
        ("`bytes`", "Raw 8-bit data — files, network, hashing. Convert with `encode()` / `decode()`.", "binary"),
    )
    yield section("Interview favourites", "star")
    yield code('''
        def is_palindrome(s: str) -> bool:
            cleaned = [c.lower() for c in s if c.isalnum()]
            return cleaned == cleaned[::-1]

        def is_anagram(a: str, b: str) -> bool:
            from collections import Counter
            return Counter(a) == Counter(b)

        print(is_palindrome("A man, a plan, a canal: Panama"))   # True
        print(is_anagram("listen", "silent"))                    # True
    ''')


@topic(G, "control-flow", "Control Flow", "arrows-split")
def _():
    yield lead("`if`/`elif`/`else`, `for`, `while`, `match` — plus a few Python-only twists like `for … else`.")
    yield section("Conditionals", "git-branch")
    yield code('''
        def grade(score):
            if score >= 90:
                return "A"
            elif score >= 75:
                return "B"
            else:
                return "C"

        print(grade(95), grade(80), grade(40))       # A B C
        status = "adult" if 20 >= 18 else "minor"     # conditional expression
        print(status)                                  # adult
    ''')
    yield section("Loops", "repeat")
    yield p("`for` iterates over *any iterable* (lists, strings, dicts, files, generators). `while` repeats while a condition is truthy.")
    yield code('''
        for i in range(2, 10, 3):          # start, stop (exclusive), step
            print(i, end=" ")               # 2 5 8
        print()
        for i, ch in enumerate("abc", start=1):
            print(i, ch, end=" | ")         # 1 a | 2 b | 3 c |
        print()
        for name, age in zip(["a", "b"], [20, 30]):
            print(name, age, end="; ")      # a 20; b 30;
    ''', check=False)
    yield table(
        ["Helper", "Gives you", "Instead of"],
        ["`enumerate(it)`", "`(index, item)` pairs", "`for i in range(len(xs))`"],
        ["`zip(a, b)`", "Items side by side (stops at the shortest)", "Manual index juggling"],
        ["`reversed(seq)`", "Items back to front, lazily", "`seq[::-1]` (copies)"],
        ["`sorted(it, key=…)`", "A new sorted list", "Sorting then copying"],
    )
    yield section("`break`, `continue` and loop `else`", "player-skip-forward")
    yield p("A loop's `else` block runs only if the loop finished **without** `break` — perfect for search loops.")
    yield code('''
        def find_first_negative(nums):
            for i, n in enumerate(nums):
                if n < 0:
                    break
            else:
                return None          # no break → nothing found
            return i

        print(find_first_negative([3, 1, -2, 5]))   # 2
        print(find_first_negative([1, 2]))          # None
    ''')
    yield section("`match` — structural pattern matching (3.10+)", "binary-tree")
    yield code('''
        def describe(cmd):
            match cmd:
                case ["go", direction]:
                    return f"moving {direction}"
                case ["pick", *items] if items:
                    return f"picking {len(items)} items"
                case {"action": "quit"}:
                    return "bye"
                case int() | float() as n:
                    return f"number {n}"
                case _:
                    return "unknown"

        print(describe(["go", "north"]))       # moving north
        print(describe(["pick", "a", "b"]))    # picking 2 items
        print(describe({"action": "quit"}))    # bye
        print(describe(3.5))                   # number 3.5
    ''')
    yield note("`match` is not a C `switch`: it destructures sequences, mappings and objects, binds names, and supports guards (`if`).")
    yield section("No `do … while`, no `++`", "alert-triangle")
    yield dodont(
        "Use `while True:` with a `break` at the end for do-while logic, and `i += 1` to increment.",
        "Writing `i++` (a syntax error) or `++i` (parsed as `+(+i)` — silently does nothing).",
    )
