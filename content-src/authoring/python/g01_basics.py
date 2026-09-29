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


@topic(G, "syntax-basics", "Syntax, Comments & Keywords", "code")
def _():
    yield lead("The rules of how Python code is *written*: indentation instead of braces, comments and docstrings, how lines continue, what you may name things, and the reserved keywords.")
    yield section("Indentation is the block structure", "indent-increase")
    yield p("Where C and Java use `{ }`, Python uses a colon `:` followed by an **indented block**. Every line in a block must use the same indentation — the convention is **4 spaces**.")
    yield code('''
        def classify(n):
            if n < 0:
                return "negative"        # inside the if-block
            elif n == 0:
                return "zero"
            return "positive"            # back at the function-block level

        print(classify(-3), classify(0), classify(7))   # negative zero positive
    ''')
    yield code('''
        src = "def f():\\nreturn 1\\n"          # body not indented
        try:
            compile(src, "<demo>", "exec")
        except IndentationError as e:
            print(type(e).__name__, "-", e.msg)   # IndentationError - expected an indented block after function definition on line 1
    ''')
    yield warn("Mixing tabs and spaces raises `TabError` in Python 3. Configure your editor to insert 4 spaces when you press Tab.", "Tabs vs spaces")
    yield section("Comments & docstrings", "message")
    yield cards(
        ("`# comment`", "Ignored by the interpreter. Explains *why* the code does something — the code already says *what*.", "hash"),
        ("Docstring", "A string literal as the **first statement** of a module, class or function. Stored in `__doc__`, shown by `help()` and IDEs.", "file-description"),
    )
    yield code('''
        def area(r):
            """Return the area of a circle of radius r.

            Uses 3.14159 for pi; pass a float or int.
            """
            # the formula is pi * r squared
            return 3.14159 * r * r

        print(area.__doc__.splitlines()[0])   # Return the area of a circle of radius r.
        print(round(area(2), 2))              # 12.57
    ''')
    yield note("Python has no block-comment syntax. Use several `#` lines. A bare triple-quoted string in the middle of code is *evaluated and thrown away* — it works as a comment but is not one.")
    yield section("Statements vs expressions", "code-dots")
    yield define("Expression", "anything that produces a value: `2 + 3`, `len(xs)`, `x if c else y`, `lambda n: n * 2`. Expressions can appear inside other expressions.")
    yield define("Statement", "an instruction that does something: `x = 5`, `if`, `for`, `def`, `import`, `return`. A statement cannot be used where a value is expected.")
    yield code('''
        x = 5                                   # assignment statement
        y = (x * 2) + 1                         # the right side is an expression
        print(y, (z := x + 1), z)               # 11 6 6   ← := is an assignment *expression*
        print(eval("x * 10"))                   # 50       ← eval evaluates one expression
        exec("w = x + 100")                     # exec runs statements
        print(w)                                # 105
    ''')
    yield note("That's why `lambda` bodies must be a single expression (no `=`, no `for`), and why `if x = 5:` is a syntax error — assignment is a statement.")
    yield section("Long lines & multiple statements", "separator")
    yield code('''
        total = (1 + 2 +
                 3 + 4)                # implicit continuation inside ( ) [ ] { }
        fruits = [
            "apple",
            "banana",                  # a trailing comma is allowed — cleaner diffs
        ]
        legacy = 1 + \\
                 2                     # explicit backslash continuation (avoid)
        a = 1; b = 2                   # ; separates statements (discouraged)
        print(total, len(fruits), legacy, a + b)   # 10 2 3 3
    ''')
    yield dodont(
        "Wrap long expressions in parentheses and break after an operator or comma.",
        "Backslash continuations — a single trailing space after `\\` becomes a syntax error.",
    )
    yield section("Names (identifiers)", "id")
    yield table(
        ["Rule / convention", "Example"],
        ["Letters, digits, `_`; can't start with a digit", "`total_2` ✓ · `2total` ✗"],
        ["Case-sensitive", "`count`, `Count` and `COUNT` are three names"],
        ["Can't be a keyword", "`class = 1` ✗ → `class_ = 1` ✓"],
        ["Unicode letters allowed", "`π = 3.14159` works (but stick to ASCII in shared code)"],
        ["`snake_case`", "variables, functions, modules"],
        ["`PascalCase`", "classes"],
        ["`UPPER_CASE`", "constants (by convention only — nothing stops reassignment)"],
        ["`_leading`", "internal / private by convention"],
        ["`__dunder__`", "reserved for Python's special names"],
        ["`_`", "a throwaway value: `for _ in range(3)`; in the REPL it's the last result"],
    )
    yield code('''
        print("my_var".isidentifier(), "2cool".isidentifier())   # True False
        π = 3.14159
        print(round(2 * π, 2))                                    # 6.28
    ''')
    yield warn("Don't shadow built-ins: `list = [1, 2]` or `id = 5` hides the built-in `list()` / `id()` for the rest of the scope, leading to confusing `TypeError: 'list' object is not callable`.")
    yield section("Keywords & soft keywords", "key")
    yield p("Keywords are reserved words you can't use as names. **Soft keywords** (`match`, `case`, `type`, `_`) are keywords only in specific positions, so old code using `match` as a variable still works.")
    yield code('''
        import keyword
        print(len(keyword.kwlist))                                     # 35
        print(keyword.iskeyword("class"), keyword.iskeyword("match"))  # True False
        print(keyword.softkwlist)                                      # ['_', 'case', 'match', 'type']
        match = "still a valid variable name"
        print(match.split()[0])                                        # still
    ''')
    yield table(
        ["Purpose", "Keywords"],
        ["Values", "`True` `False` `None`"],
        ["Logic & tests", "`and` `or` `not` `in` `is`"],
        ["Branching", "`if` `elif` `else`"],
        ["Loops", "`for` `while` `break` `continue`"],
        ["Functions", "`def` `return` `lambda` `yield` `global` `nonlocal`"],
        ["Classes & modules", "`class` `import` `from` `as`"],
        ["Errors & resources", "`try` `except` `finally` `raise` `assert` `with`"],
        ["Async", "`async` `await`"],
        ["Misc", "`pass` `del`"],
    )
    yield section("Placeholders: `pass` and `...`", "dots")
    yield code('''
        def todo():
            pass                  # a statement that does nothing

        class Config: ...         # Ellipsis — a common "fill in later" body

        print(todo(), Config.__name__, ...)   # None Config Ellipsis
    ''')
    yield section("Exploring from the REPL: `help`, `dir`, `type`", "help")
    yield code('''
        print(type(3.0).__name__)                             # float
        print([n for n in dir(str) if n.startswith("st")])    # ['startswith', 'strip']
        print(len.__doc__.splitlines()[0])                    # Return the number of items in a container.
    ''')
    yield shell('''
        >>> help(str.split)       # full documentation (q to quit)
        >>> dir([])               # every attribute/method of a list
        >>> 2 + 3
        5
        >>> _ * 10                # _ holds the last REPL result
        50
    ''', caption="REPL")
    yield qa("Why does Python use indentation instead of braces?",
             "To make the visual structure *be* the actual structure — code that looks nested is nested. It removes a whole class of bugs (misleading indentation) and style debates, and keeps code readable.")
    yield qa("What is the difference between a comment and a docstring?",
             "A comment (`#`) is discarded by the parser. A docstring is a real string object stored in the `__doc__` attribute of a module, class or function, so `help()`, IDEs and documentation tools can read it at runtime.")
    yield qa("Is `match` a keyword?",
             "It's a **soft keyword**: it acts as a keyword only at the start of a `match` statement, so `match = 5` is still a legal assignment. The same applies to `case`, `type` and `_`.")


@topic(G, "variables-types","Variables, Types & Operators", "variable")
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
    yield section("Operators at a glance", "math-symbols")
    yield p("Arithmetic `+ - * / // % **`, comparison `== != < <= > >=` (chainable), logical `and or not`, identity `is`, membership `in`, bitwise `& | ^ ~ << >>` and the walrus `:=`. The next topic, **Operators & Precedence**, covers each one in depth.")
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


@topic(G, "operators", "Operators & Precedence", "math-symbols")
def _():
    yield lead("Every operator Python has, how tightly each one binds, and the surprising corners — floor division with negatives, `and`/`or` returning operands, chained comparisons and bit tricks.")
    yield section("Precedence table (highest first)", "list-numbers")
    yield table(
        ["Level", "Operators", "Notes"],
        ["1", "`(…)` `[…]` `{…}`, `x[i]`, `x(…)`, `x.attr`", "Grouping, subscription, calls, attribute access"],
        ["2", "`await x`", "Inside `async def`"],
        ["3", "`**`", "Power — **right**-associative; binds tighter than a unary minus on its left"],
        ["4", "`+x` `-x` `~x`", "Unary plus, minus, bitwise NOT"],
        ["5", "`*` `@` `/` `//` `%`", "Multiplicative (`@` is matrix multiplication)"],
        ["6", "`+` `-`", "Additive"],
        ["7", "`<<` `>>`", "Shifts"],
        ["8", "`&`", "Bitwise AND"],
        ["9", "`^`", "Bitwise XOR"],
        ["10", "`|`", "Bitwise OR"],
        ["11", "`in` `not in` `is` `is not` `<` `<=` `>` `>=` `!=` `==`", "All comparisons share one level and **chain**"],
        ["12", "`not x`", "Boolean NOT"],
        ["13", "`and`", "Short-circuit AND"],
        ["14", "`or`", "Short-circuit OR"],
        ["15", "`x if c else y`", "Conditional expression"],
        ["16", "`lambda`", "Anonymous function"],
        ["17", "`:=`", "Assignment expression (walrus) — lowest"],
    )
    yield note("Everything is left-to-right associative except `**` (right-to-left) and comparisons (which chain). When in doubt, add parentheses — they cost nothing and help the reader.")
    yield section("Arithmetic", "calculator")
    yield code('''
        print(7 / 2, 7 // 2, 7 % 2)           # 3.5 3 1
        print(-7 // 2, -7 % 2)                # -4 1
        print(7 // -2, 7 % -2)                # -4 -1
        print(divmod(-7, 2))                  # (-4, 1)
        print(7.5 // 2, 7.5 % 2)              # 3.0 1.5
        print(2 ** 3 ** 2, (2 ** 3) ** 2)     # 512 64
        print(-2 ** 2, (-2) ** 2)             # -4 4
        print(2 ** -1, 10 ** 20)              # 0.5 100000000000000000000
    ''')
    yield table(
        ["Operator", "Meaning", "Watch out"],
        ["`/`", "True division", "Always returns a `float`: `4 / 2 == 2.0`"],
        ["`//`", "Floor division", "Rounds toward **−∞**, not toward 0: `-7 // 2 == -4` (C/Java give `-3`)"],
        ["`%`", "Modulo", "Result has the sign of the **divisor**: `-7 % 2 == 1`; always `(a // b) * b + a % b == a`"],
        ["`**`", "Power", "Right-associative; `pow(a, b, m)` does fast modular exponentiation"],
        ["`divmod(a, b)`", "`(a // b, a % b)` at once", "Handy for digit extraction and time conversions"],
    )
    yield note("Python's `%` makes wrap-around indexing easy: `(i - 1) % n` is always a valid index, even when `i == 0`. For C-style truncation use `int(a / b)` or `math.fmod`.")
    yield section("Comparisons chain", "equal")
    yield code('''
        x = 5
        print(1 < x < 10, 10 > x >= 5)        # True True
        print(1 < 2 == 2)                     # True   ← means (1 < 2) and (2 == 2)
        print((1 < 2) == 2)                   # False  ← True == 2 is False
        print(False == False in [False])      # True   ← (False == False) and (False in [False])
        print("apple" < "banana" < "cherry")  # True   ← strings compare lexicographically
        print([1, 2] < [1, 3], (2, 0) > (1, 9))   # True True
    ''')
    yield p("`a < b < c` evaluates `b` only once and means `a < b and b < c`. Sequences compare element by element, which is why tuples make great multi-key sort keys.")
    yield section("`and`, `or`, `not` — short-circuit and return operands", "logic-and")
    yield code('''
        print(0 or "default", "x" or "default")   # default x
        print(0 and 1 / 0, 3 and 4)               # 0 4   ← 1 / 0 is never evaluated
        print([] or None or 0)                    # 0     ← every operand falsy → the last one
        print(not "", not "hi")                   # True False

        name = ""
        print(name or "Anonymous")                # Anonymous
    ''')
    yield table(
        ["Expression", "Returns"],
        ["`a or b`", "`a` if `a` is truthy, otherwise `b`"],
        ["`a and b`", "`a` if `a` is falsy, otherwise `b`"],
        ["`not a`", "Always a real `bool`"],
    )
    yield warn("`count = user_count or 10` replaces a legitimate `0` with `10`. When `0`, `''` or `[]` are valid values, test explicitly: `10 if user_count is None else user_count`.")
    yield section("Bitwise operators & tricks", "binary")
    yield code('''
        a, b = 0b1100, 0b1010                 # 12, 10
        print(a & b, a | b, a ^ b)            # 8 14 6
        print(bin(a & b), ~a)                 # 0b1000 -13   ← ~x == -x - 1
        print(1 << 4, 100 >> 2)               # 16 25        ← x << k == x * 2**k
    ''')
    yield code('''
        def is_power_of_two(x):
            return x > 0 and x & (x - 1) == 0     # clears the lowest set bit

        print(is_power_of_two(64), is_power_of_two(96))   # True False
        print(40 & -40)                         # 8      ← lowest set bit of 0b101000
        print((13 >> 2) & 1)                    # 1      ← bit 2 of 0b1101
        print((255).bit_count(), (255).bit_length())   # 8 8

        READ, WRITE, EXEC = 1, 2, 4             # flags packed in one int
        perms = READ | WRITE
        perms &= ~WRITE                         # clear a flag
        perms |= EXEC                           # set a flag
        print(perms, bool(perms & READ), bool(perms & WRITE))   # 5 True False

        nums = [4, 1, 2, 1, 2]
        single = 0
        for n in nums:
            single ^= n                         # x ^ x == 0, so pairs cancel out
        print(single)                           # 4
    ''')
    yield note("Unlike C, bitwise operators bind **tighter** than comparisons in Python: `n & 1 == 0` means `(n & 1) == 0`. Python ints are unbounded, so `~` and negative numbers behave as if they had infinitely many leading 1 bits.")
    yield section("Augmented assignment", "plus")
    yield p("`x += 1`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`, `&=`, `|=`, `^=`, `<<=`, `>>=`, `@=`. For mutable objects they modify **in place** (`__iadd__`); for immutable ones they build a new object and rebind the name.")
    yield code('''
        a = [1]
        b = a
        a += [2]              # list.__iadd__ → extends the same list
        print(b)              # [1, 2]
        a = a + [3]           # + builds a NEW list; b still sees the old one
        print(a, b)           # [1, 2, 3] [1, 2]
    ''')
    yield warn("There is no `++` or `--`. `i++` is a syntax error and `++i` quietly means `+(+i)` — it does nothing.")
    yield section("Conditional expression & walrus", "arrows-split")
    yield code('''
        age = 20
        print("adult" if age >= 18 else "minor")          # adult

        data = [4, 9, 1, 7]
        if (n := len(data)) > 3:                          # assign and test in one step
            print(f"{n} items")                           # 4 items
        big_squares = [y for x in data if (y := x * x) > 10]
        print(big_squares)                                # [16, 81, 49]
    ''')
    yield section("Membership, identity & overloading", "fingerprint")
    yield code('''
        print("ell" in "hello", 3 in {1, 2, 3}, "a" in {"a": 1})   # True True True
        a, b = [], []
        print(a == b, a is b, a is not b)                         # True False True
        print("ab" * 3, [0] * 3, [1] + [2])                       # ababab [0, 0, 0] [1, 2]

        import operator
        print(operator.add(2, 3), operator.mul("ha", 2))          # 5 haha
    ''')
    yield p("Operators are method calls in disguise: `a + b` → `a.__add__(b)`, `a < b` → `a.__lt__(b)`, `x in c` → `c.__contains__(x)`. That's how `str`, `list` and your own classes give `+` and `*` their own meaning (see **Magic (Dunder) Methods**). The `operator` module exposes each one as a function for `sorted(key=…)`, `reduce` and `map`.")
    yield section("Common pitfalls", "alert-triangle")
    yield code('''
        x = 5
        print(x == 1 or 2)            # 2      ← parsed as (x == 1) or 2 → always truthy!
        print(x in (1, 2))            # False  ← what was meant
        print(not x == 5, x != 5)     # False False   ← not binds looser than ==
        print(-3 ** 2)                # -9     ← -(3 ** 2)
        print(0.1 + 0.2 == 0.3)       # False  ← floats; compare with math.isclose
        print(1 + 2 * 3, (1 + 2) * 3) # 7 9
    ''')
    yield qa("What do `and` and `or` return?",
             "They return one of their **operands**, not necessarily a `bool`. `a or b` returns `a` if it's truthy, else `b`; `a and b` returns `a` if it's falsy, else `b`. Evaluation stops as soon as the result is known (short-circuit), so the right side may never run.")
    yield qa("Why is `-7 // 2` equal to `-4` in Python?",
             "`//` is **floor** division: it rounds toward negative infinity. −3.5 floors to −4. Correspondingly `-7 % 2 == 1`, keeping the identity `(a // b) * b + a % b == a`. C and Java truncate toward zero instead (−3 and −1).")
    yield qa("How do you check whether a number is a power of two?",
             "`n > 0 and n & (n - 1) == 0`. Subtracting 1 flips the lowest set bit and everything below it, so ANDing clears that bit — the result is 0 only if there was exactly one set bit.")
    yield qa("What does `1 < 2 == 2` evaluate to?",
             "`True`. Comparisons chain: it means `1 < 2 and 2 == 2`. It is *not* `(1 < 2) == 2`, which would be `True == 2` → `False`.")


@topic(G, "input-output", "Input & Output", "terminal-2")
def _():
    yield lead("Talking to the console: everything `print()` can do, reading typed input with `input()`, and the fast `sys.stdin` patterns used in coding rounds.")
    yield section("`print()` in full", "printer")
    yield p("Signature: `print(*objects, sep=' ', end='\\n', file=sys.stdout, flush=False)`. Each object is converted with `str()`, joined by `sep`, followed by `end`.")
    yield code('''
        print("a", "b", "c")                      # a b c
        print("a", "b", "c", sep="-")             # a-b-c
        print(2026, 9, 29, sep="/")               # 2026/9/29
        print("Loading", end=""); print("...done")   # Loading...done
        print(*[1, 2, 3], sep=", ")               # 1, 2, 3
        print("tab\\tseparated", repr("hi"))      # tab	separated 'hi'
    ''')
    yield table(
        ["Parameter", "Default", "Use it for"],
        ["`sep`", "`' '`", "What goes *between* the objects"],
        ["`end`", "`'\\n'`", "What goes *after* the last object — `end=''` keeps the cursor on the line"],
        ["`file`", "`sys.stdout`", "Any object with `.write()`: `sys.stderr`, an open file, an `io.StringIO`"],
        ["`flush`", "`False`", "Force the output out immediately (progress bars, logs piped to another program)"],
    )
    yield code('''
        import io
        buf = io.StringIO()
        # file= sends the text to buf instead of the screen:
        print("to a buffer", 42, file=buf)
        print(repr(buf.getvalue()))           # 'to a buffer 42\\n'
        result = print("shown", end=" ")
        print(result)                         # shown None
    ''')
    yield note("`print` returns `None` — it only has a side effect. Errors and diagnostics belong on `sys.stderr` (`print(msg, file=sys.stderr)`) so they don't mix with the program's real output.")
    yield section("`input()` — reading a line", "keyboard")
    yield p("`input(prompt)` shows the prompt, waits for the user to press Enter and returns the line **as a `str`, without the newline**. Convert it yourself.")
    yield shell('''
        name = input("Your name? ")
        age = int(input("Your age? "))
        print(f"Hi {name}, next year you'll be {age + 1}")

        $ python3 greet.py
        Your name? Asha
        Your age? 24
        Hi Asha, next year you'll be 25
    ''', caption="greet.py")
    yield p("Below, `sys.stdin` is swapped for an in-memory stream so the example runs without a keyboard — exactly how tests feed input to a program.")
    yield code(r'''
        import io, sys
        fake = io.StringIO("Asha\n3 1 4 1 5\n42\n")
        old, sys.stdin = sys.stdin, fake          # pretend the user typed three lines
        try:
            name = input()                        # 'Asha' — always a str
            nums = list(map(int, input().split()))
            n = int(input())
            try:
                input()                           # nothing left to read
            except EOFError:
                eof = True
        finally:
            sys.stdin = old                       # always restore the real stdin
        print(name, nums, n + 1, eof)             # Asha [3, 1, 4, 1, 5] 43 True
    ''')
    yield warn("`input()` never returns a number: `input() + 1` is a `TypeError`. And at end of input (Ctrl-D, or a judge's file running out) it raises `EOFError`.")
    yield section("Parsing patterns", "list-details")
    yield table(
        ["Input shape", "Code"],
        ["One integer", "`n = int(input())`"],
        ["Two integers on a line", "`a, b = map(int, input().split())`"],
        ["A list of integers", "`nums = list(map(int, input().split()))`"],
        ["`n` lines of text", "`lines = [input() for _ in range(n)]`"],
        ["A grid of characters", "`grid = [list(input()) for _ in range(rows)]`"],
        ["Comma-separated", "`parts = input().split(',')`"],
        ["Everything at once", "`tokens = sys.stdin.read().split()`"],
    )
    yield section("Fast input for coding rounds", "bolt")
    yield p("`input()` is slow for 10⁵+ lines. `sys.stdin.readline` is much faster, but it **keeps the trailing `\\n`** — strip it (or let `int()` / `split()` ignore it).")
    yield code(r'''
        import io
        data = io.StringIO("3\n10 20\n30 40\n50 60\n")
        readline = data.readline                  # real code: import sys; readline = sys.stdin.readline
        n = int(readline())                       # int() ignores the trailing newline
        pairs = [tuple(map(int, readline().split())) for _ in range(n)]
        print(pairs)                              # [(10, 20), (30, 40), (50, 60)]
        print(repr(io.StringIO("hi\n").readline()))   # 'hi\n'

        tokens = iter(io.StringIO("2\n5 7\n").read().split())   # read everything, walk token by token
        count = int(next(tokens))
        print(sum(int(next(tokens)) for _ in range(count)))    # 12
    ''')
    yield section("Fast output", "arrow-bar-right")
    yield code('''
        import sys
        written = sys.stdout.write("written ")    # no automatic newline; returns chars written
        print(written)                            # written 8

        results = [3, 1, 4]
        print(" ".join(map(str, results)))        # 3 1 4
    ''')
    yield dodont(
        "Collect answers in a list and print once with `'\\n'.join(map(str, answers))`.",
        "Calling `print` a million times in a loop — each call has overhead (and may flush).",
    )
    yield section("Pretty-printing nested data", "brackets")
    yield code('''
        from pprint import pprint
        data = {"name": "Asha", "skills": ["python", "sql", "dsa"],
                "address": {"city": "Pune", "pin": 411001}}
        pprint(data, width=40)
    ''', check=False)
    yield output('''
        {'address': {'city': 'Pune',
                     'pin': 411001},
         'name': 'Asha',
         'skills': ['python', 'sql', 'dsa']}
    ''')
    yield note("`pprint` wraps long structures and sorts dict keys (pass `sort_dicts=False` to keep insertion order). `pprint.pformat` returns the text instead of printing it.")
    yield section("Formatting output", "braces")
    yield code('''
        price, qty, item = 49.5, 3, "pen"
        print(f"{item:<6}|{qty:>3}|{price * qty:8.2f}|")   # pen   |  3|  148.50|
        print(f"{0.4567:.1%}  {1234567:,}  {7:03d}")       # 45.7%  1,234,567  007
    ''')
    yield p("f-strings and the format-spec mini-language (`:<6`, `.2f`, `,`, `%`) are covered in depth in **String Formatting** under *Strings & Numbers*.")
    yield qa("What type does `input()` return?",
             "Always `str` (without the trailing newline), even if the user types digits. Convert explicitly: `int(input())`, `float(input())`, or `map(int, input().split())` for several numbers.")
    yield qa("Why use `sys.stdin.readline` instead of `input()`?",
             "It avoids `input()`'s per-call overhead (prompt handling, newline stripping), which matters with hundreds of thousands of lines. Remember it keeps the `\\n`, and returns `''` (not `EOFError`) at end of input.")
    yield qa("What is the difference between `print` and `sys.stdout.write`?",
             "`print` accepts any objects, converts them with `str()`, adds separators and a newline, and returns `None`. `sys.stdout.write` accepts one string, adds nothing, and returns the number of characters written.")


@topic(G, "control-flow","Control Flow", "arrows-split")
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
    yield note("More patterns — `while … else`, breaking out of nested loops, sentinel loops, modifying while iterating — are in **Loops & Iteration Patterns**.")
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
    yield note("`match` is not a C `switch`: it destructures sequences, mappings and objects, binds names, and supports guards (`if`). See **Pattern Matching (match)** for every pattern kind and its pitfalls.")
    yield section("No `do … while`, no `++`", "alert-triangle")
    yield dodont(
        "Use `while True:` with a `break` at the end for do-while logic, and `i += 1` to increment.",
        "Writing `i++` (a syntax error) or `++i` (parsed as `+(+i)` — silently does nothing).",
    )


@topic(G, "loops", "Loops & Iteration Patterns", "repeat")
def _():
    yield lead("Python's `for` walks over *any iterable* — there is no C-style `for (i = 0; …)`. This topic collects the loop patterns, helpers and pitfalls you meet every day.")
    yield section("`range` in detail", "numbers")
    yield code('''
        print(list(range(5)))                 # [0, 1, 2, 3, 4]
        print(list(range(2, 12, 3)))          # [2, 5, 8, 11]
        print(list(range(5, 0, -1)))          # [5, 4, 3, 2, 1]
        print(list(range(3, 0)))              # []   ← empty: a negative step is needed to count down
        r = range(0, 10**12, 2)               # no list is built — O(1) memory
        print(len(r), r[10], r[-1])           # 500000000000 20 999999999998
        print(999_999 in r, 1_000 in r)       # False True   ← O(1) arithmetic check
    ''')
    yield table(
        ["Goal", "Loop header"],
        ["0 … n−1", "`for i in range(n)`"],
        ["1 … n inclusive", "`for i in range(1, n + 1)`"],
        ["n−1 down to 0", "`for i in range(n - 1, -1, -1)` or `reversed(range(n))`"],
        ["Every other index", "`for i in range(0, n, 2)`"],
        ["Items and their index", "`for i, x in enumerate(xs)`"],
        ["Two lists in step", "`for a, b in zip(xs, ys)`"],
        ["Neighbouring pairs", "`for a, b in zip(xs, xs[1:])` or `itertools.pairwise(xs)`"],
    )
    yield section("`while` loops and `while … else`", "rotate-clockwise")
    yield p("Use `while` when you don't know the number of iterations in advance. Like `for`, it takes an `else` that runs only if the loop ended **without** `break`.")
    yield code('''
        n, steps = 27, 0
        while n != 1:                         # Collatz sequence
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            steps += 1
        print(steps)                          # 111

        def is_prime(n):
            if n < 2:
                return False
            d = 2
            while d * d <= n:
                if n % d == 0:
                    break                     # found a divisor
                d += 1
            else:
                return True                   # no break → no divisor found
            return False

        print([k for k in range(20) if is_prime(k)])   # [2, 3, 5, 7, 11, 13, 17, 19]
    ''')
    yield code('''
        attempts = 0
        while True:                           # the do-while idiom: body runs at least once
            attempts += 1
            if attempts * attempts > 20:
                break
        print(attempts)                       # 5
    ''')
    yield section("Breaking out of nested loops", "door-exit")
    yield p("`break` only leaves the innermost loop. Three ways out of two:")
    yield code('''
        grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        # 1. A flag checked by the outer loop
        found = None
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                if val == 5:
                    found = (r, c)
                    break
            if found:
                break
        print(found)                          # (1, 1)

        # 2. Put the loops in a function and return (usually the cleanest)
        def find(grid, target):
            for r, row in enumerate(grid):
                for c, val in enumerate(row):
                    if val == target:
                        return r, c
            return None
        print(find(grid, 8), find(grid, 0))   # (2, 1) None

        # 3. One flat loop over all coordinates
        from itertools import product
        hit = next(((r, c) for r, c in product(range(3), range(3)) if grid[r][c] == 9), None)
        print(hit)                            # (2, 2)
    ''')
    yield section("Iterating dicts, in order, in reverse, in parallel", "arrows-right-left")
    yield code('''
        prices = {"tea": 20, "coffee": 35, "juice": 50}
        print([k for k in prices])                        # ['tea', 'coffee', 'juice']
        print([f"{k}={v}" for k, v in prices.items()])    # ['tea=20', 'coffee=35', 'juice=50']
        print(sorted(prices, key=prices.get, reverse=True))   # ['juice', 'coffee', 'tea']

        names = ["asha", "ravi", "kiran"]
        scores = [91, 84, 77]
        print(list(enumerate(names, start=1)))    # [(1, 'asha'), (2, 'ravi'), (3, 'kiran')]
        print(dict(zip(names, scores)))           # {'asha': 91, 'ravi': 84, 'kiran': 77}
        print(list(zip(names, [1, 2])))           # [('asha', 1), ('ravi', 2)]   ← stops at the shortest
        try:
            list(zip(names, [1, 2], strict=True)) # 3.10+: insist on equal lengths
        except ValueError as e:
            print(e)                              # zip() argument 2 is shorter than argument 1
        print(list(reversed(names)))              # ['kiran', 'ravi', 'asha']

        pairs = [("a", 1), ("b", 2)]
        letters, numbers = zip(*pairs)            # "unzip"
        print(letters, numbers)                   # ('a', 'b') (1, 2)
    ''')
    yield section("Don't modify a collection while looping over it", "alert-triangle")
    yield code('''
        nums = [1, 2, 2, 3, 4]
        for x in nums:
            if x % 2 == 0:
                nums.remove(x)        # shifts later items left → the loop skips one
        print(nums)                   # [1, 2, 3]   ← a 2 survived!

        nums = [1, 2, 2, 3, 4]
        print([x for x in nums if x % 2])       # [1, 3]   ← build a new list instead

        d = {"a": 1, "b": 2}
        try:
            for k in d:
                if d[k] == 1:
                    del d[k]
        except RuntimeError as e:
            print(e)                  # dictionary changed size during iteration
        d = {k: v for k, v in d.items() if v != 1}
        print(d)                      # {'b': 2}
    ''')
    yield cards(
        ("Build a new collection", "A comprehension that keeps what you want — the idiomatic fix.", "filter"),
        ("Loop over a copy", "`for x in nums[:]:` or `for k in list(d):` — then mutating the original is safe.", "copy"),
        ("Loop backwards by index", "`for i in range(len(xs) - 1, -1, -1): del xs[i]` — deletions don't shift unvisited items.", "arrow-back"),
    )
    yield section("Sentinel loops & `iter(callable, sentinel)`", "flag")
    yield code(r'''
        import io
        from functools import partial

        stream = io.StringIO("alpha\nbeta\n\ngamma\n")
        lines = []
        while (line := stream.readline().rstrip("\n")):   # stop at the first empty line
            lines.append(line)
        print(lines)                                      # ['alpha', 'beta']

        f = io.StringIO("abcdefgh")
        chunks = list(iter(partial(f.read, 3), ""))       # call f.read(3) until it returns ""
        print(chunks)                                     # ['abc', 'def', 'gh']
    ''')
    yield note("The two-argument `iter(func, sentinel)` calls `func()` repeatedly and stops when it returns `sentinel` — perfect for reading fixed-size blocks from files and sockets.")
    yield section("Loop variables & scope", "variable")
    yield code('''
        for i in range(3):
            pass
        print(i)                      # 2   ← the loop variable survives the loop

        squares = [j * j for j in range(3)]
        print("j" in dir())           # False   ← comprehension variables don't leak
    ''')
    yield warn("If the loop body never runs (empty iterable), the loop variable is never assigned — using it afterwards raises `NameError`.")
    yield section("Faster loops", "bolt")
    yield table(
        ["Slower", "Faster", "Why"],
        ["`total = 0` + `for x in xs: total += x`", "`sum(xs)`", "Built-ins loop in C"],
        ["Loop + `append`", "List comprehension", "No repeated `.append` lookup and call"],
        ["`if x in big_list` inside a loop", "Convert to a `set` once", "O(1) instead of O(n) per check"],
        ["`for i in range(len(xs)): xs[i]`", "`for x in xs`", "No indexing per step"],
        ["`s += piece` in a loop", "`''.join(pieces)`", "Avoids O(n²) copying"],
        ["`obj.method` looked up each time", "`m = obj.method` before the loop", "One attribute lookup instead of n"],
    )
    yield qa("When would you use `for … else`?",
             "For searches: the `else` runs only when the loop completed without `break`, i.e. when nothing was found. It replaces a separate `found = False` flag.")
    yield qa("How do you iterate over two lists at the same time?",
             "`for a, b in zip(xs, ys)`. `zip` stops at the shortest input; use `zip(..., strict=True)` (3.10+) to raise on a length mismatch, or `itertools.zip_longest` to pad the shorter one.")
    yield qa("Why is removing items from a list while iterating over it a bug?",
             "The list iterator walks by index. Removing an item shifts the rest left, so the item right after the removed one is skipped. Iterate over a copy, iterate backwards, or build a new list with a comprehension.")


@topic(G, "pattern-matching", "Pattern Matching (match)", "binary-tree")
def _():
    yield lead("`match` (Python 3.10+) compares a value against a series of *patterns* — shapes, not just values — and binds the pieces it finds to names.")
    yield define("Structural pattern matching", "`match subject:` followed by `case pattern:` blocks. Cases are tried top to bottom; the **first** one that matches runs, and there is no fall-through.")
    yield section("Literals, OR-patterns, `as` and the wildcard", "equal")
    yield code('''
        def http_status(code):
            match code:
                case 200 | 201 | 204:            # OR-pattern
                    return "success"
                case 301 | 302 as r:             # bind the matched value with as
                    return f"redirect {r}"
                case 404:
                    return "not found"
                case _:                          # wildcard: matches anything, binds nothing
                    return "other"

        print(http_status(201), http_status(302))   # success redirect 302
        print(http_status(404), http_status(500))   # not found other
    ''')
    yield section("Sequence patterns", "brackets")
    yield code('''
        def summarize(seq):
            match seq:
                case []:
                    return "empty"
                case [x]:
                    return f"one item: {x}"
                case [x, y]:
                    return f"pair: {x}, {y}"
                case [first, *rest]:             # star captures the remainder as a list
                    return f"{first} and {len(rest)} more"

        print(summarize([]))              # empty
        print(summarize([7]))             # one item: 7
        print(summarize((1, 2)))          # pair: 1, 2   ← tuples match list patterns too
        print(summarize([1, 2, 3, 4]))    # 1 and 3 more
        print(summarize("ab"))            # None   ← str is NOT treated as a sequence here
    ''')
    yield code('''
        def fizzbuzz(n):
            match (n % 3, n % 5):                # match a tuple built on the spot
                case (0, 0): return "FizzBuzz"
                case (0, _): return "Fizz"
                case (_, 0): return "Buzz"
                case _: return str(n)

        print(" ".join(fizzbuzz(i) for i in range(1, 16)))   # 1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz
    ''')
    yield section("Mapping patterns", "braces")
    yield code('''
        def handle(event):
            match event:
                case {"type": "click", "x": x, "y": y}:
                    return f"click at ({x}, {y})"
                case {"type": "key", "key": str(k)} if len(k) == 1:
                    return f"key {k!r}"
                case {"type": "resize", **rest}:
                    return f"resize {rest}"
                case {"type": t}:
                    return f"unhandled {t}"

        print(handle({"type": "click", "x": 3, "y": 4, "ts": 99}))   # click at (3, 4)   ← extra keys are ignored
        print(handle({"type": "key", "key": "q"}))                  # key 'q'
        print(handle({"type": "resize", "w": 800, "h": 600}))       # resize {'w': 800, 'h': 600}
        print(handle({"type": "scroll"}))                           # unhandled scroll
    ''')
    yield note("Mapping patterns match if the listed keys are present — other keys are allowed. Sequence patterns are the opposite: the length must match exactly unless you use `*rest`.")
    yield section("Class patterns", "box")
    yield code('''
        from dataclasses import dataclass

        @dataclass
        class Point:
            x: int
            y: int

        @dataclass
        class Circle:
            center: Point
            r: float

        def where(shape):
            match shape:
                case Point(x=0, y=0):
                    return "origin"
                case Point(0, y):                # positional → uses Point.__match_args__
                    return f"on the y-axis at {y}"
                case Point(x, y) if x == y:      # guard
                    return "on the diagonal"
                case Circle(Point(0, 0), r):     # patterns nest
                    return f"circle of radius {r} at the origin"
                case Point() | Circle():         # just an isinstance check
                    return "somewhere else"
                case _:
                    return "not a shape"

        print(where(Point(0, 0)), "|", where(Point(0, 5)))        # origin | on the y-axis at 5
        print(where(Point(3, 3)), "|", where(Circle(Point(0, 0), 2)))   # on the diagonal | circle of radius 2 at the origin
        print(where(Point(1, 2)), "|", where("hi"))               # somewhere else | not a shape
        print(Point.__match_args__)                               # ('x', 'y')
    ''')
    yield code('''
        def kind(value):
            match value:
                case bool():                     # check bool before int — bool is a subclass of int
                    return "bool"
                case int(n) if n < 0:            # built-ins match the whole value positionally
                    return "negative int"
                case int() | float():
                    return "number"
                case str() as s:
                    return f"string of {len(s)}"
                case _:
                    return type(value).__name__

        print(kind(True), kind(-4), kind(2.5), kind("abc"), kind(None))   # bool negative int number string of 3 NoneType
    ''')
    yield p("A class pattern `Cls(...)` first checks `isinstance(subject, Cls)`, then matches attributes: keyword sub-patterns by name, positional ones via the class's `__match_args__` tuple (generated automatically by `@dataclass` and `namedtuple`).")
    yield section("Guards", "shield-check")
    yield p("`case pattern if condition:` — the pattern must match **and** the condition must be truthy. Names bound by the pattern are available in the guard.")
    yield code('''
        def classify(pair):
            match pair:
                case (a, b) if a == b:
                    return "equal"
                case (a, b) if a > b:
                    return "descending"
                case (_, _):
                    return "ascending"

        print(classify((2, 2)), classify((5, 1)), classify((1, 5)))   # equal descending ascending
    ''')
    yield section("The capture-pattern trap", "alert-triangle")
    yield p("A **bare name** in a pattern is a *capture*: it matches anything and assigns to that name. To compare against a constant, use a **dotted name** (a value pattern) such as `Color.RED` or `http.HTTPStatus.OK`.")
    yield code('''
        RED = "red"

        def is_red(color):
            match color:
                case RED:                        # captures! binds a local RED = color
                    return True
            return False

        print(is_red("blue"))                    # True   ← oops

        from enum import Enum
        class Color(Enum):
            RED = "red"
            BLUE = "blue"

        def is_red_fixed(color):
            match color:
                case Color.RED:                  # dotted name → compared with ==
                    return True
                case _:
                    return False

        print(is_red_fixed(Color.BLUE), is_red_fixed(Color.RED))   # False True
    ''')
    yield code('''
        src = "match x:\\n    case y:\\n        pass\\n    case 1:\\n        pass\\n"
        try:
            compile(src, "<demo>", "exec")
        except SyntaxError as e:
            print(e.msg)          # name capture 'y' makes remaining patterns unreachable
    ''')
    yield section("Pattern kinds cheat sheet", "list")
    yield table(
        ["Pattern", "Example", "Matches"],
        ["Literal", "`case 0:` `case \"quit\":` `case None:`", "Equal value (`None`/`True`/`False` compared with `is`)"],
        ["Capture", "`case x:`", "Anything; binds `x`"],
        ["Wildcard", "`case _:`", "Anything; binds nothing"],
        ["Value", "`case Color.RED:`", "Equal to a dotted constant"],
        ["OR", "`case 1 | 2 | 3:`", "Any alternative"],
        ["AS", "`case [x, y] as pair:`", "The inner pattern; binds the whole subject too"],
        ["Sequence", "`case [x, *rest]:`", "Lists/tuples (not `str`/`bytes`) of the right length"],
        ["Mapping", "`case {\"id\": i}:`", "Dicts containing those keys; `**rest` collects the others"],
        ["Class", "`case Point(x, y=0):`", "`isinstance` + attribute patterns"],
    )
    yield section("When to use `match`", "bulb")
    yield dodont(
        "Use `match` to branch on the **shape** of data: parsed commands, JSON events, AST nodes, tuples of states.",
        "Using it as a glorified `switch` for simple value → value mapping — a `dict` lookup is shorter and faster.",
    )
    yield qa("How is `match` different from a C/Java `switch`?",
             "`switch` compares one value against constants. `match` tests *structure*: it can destructure lists, dicts and objects, bind variables, combine alternatives with `|`, and filter with guards. There is no fall-through and no `break` — the first matching case runs and the statement ends.")
    yield qa("Why does `case RED:` match every value?",
             "A bare name is a capture pattern: it always matches and binds the subject to `RED`. Constants must be referenced with a dotted name (`Color.RED`, `module.RED`) so Python treats them as value patterns compared with `==`.")
    yield qa("How do positional class patterns like `Point(0, y)` work?",
             "Python checks `isinstance(subject, Point)`, then maps positional sub-patterns to attribute names using `Point.__match_args__` — here `('x', 'y')` — and matches `subject.x` against `0` and binds `subject.y` to `y`. Dataclasses and named tuples define `__match_args__` automatically.")
