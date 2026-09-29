from kit import *

G = "Strings & Numbers"


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
    yield note("This page is the overview. The next topics go deeper: *String Methods Deep Dive*, *String Formatting & f-strings*, *Unicode, Bytes & Encodings* and *Regular Expressions*.", "Go deeper")
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


@topic(G, "string-methods", "String Methods Deep Dive", "letter-case-toggle")
def _():
    yield lead("`str` has ~47 methods. Knowing the right one — `partition` instead of a regex, `casefold` instead of `lower`, `removeprefix` instead of `strip` — makes text code shorter and correct.")
    yield note("Every method returns a **new** string (or a list / bool / int). Nothing modifies the original — strings are immutable.", "Remember")
    yield section("Case conversion", "letter-case")
    yield table(
        ["Method", "Does", "Example → result"],
        ["`lower()` / `upper()`", "All lower / upper case", "`'PyThon'.lower()` → `'python'`"],
        ["`casefold()`", "Aggressive lower-casing for **caseless comparison**", "`'Straße'.casefold()` → `'strasse'`"],
        ["`title()`", "First letter of every word upper", "`'hello world'.title()` → `'Hello World'`"],
        ["`capitalize()`", "First character upper, **rest lower**", "`'hELLO'.capitalize()` → `'Hello'`"],
        ["`swapcase()`", "Invert each letter's case", "`'Ab'.swapcase()` → `'aB'`"],
    )
    yield code('''
        print("Straße".lower(), "Straße".casefold())          # straße strasse
        print("STRASSE".casefold() == "Straße".casefold())    # True
        print("STRASSE".lower() == "Straße".lower())          # False
        print("they're bill's".title())                      # They'Re Bill'S
        print(" ".join(w.capitalize() for w in "they're bill's".split()))   # They're Bill's
    ''')
    yield warn("`title()` treats every non-letter as a word boundary, so apostrophes break it (`They'Re`). Use `capitalize()` per word, or `string.capwords(s)`.")
    yield section("Searching", "search")
    yield table(
        ["Method", "Returns", "If not found"],
        ["`s.find(sub[, start[, end]])`", "Lowest index", "`-1`"],
        ["`s.rfind(sub)`", "Highest index", "`-1`"],
        ["`s.index(sub)` / `s.rindex(sub)`", "Like `find` / `rfind`", "raises `ValueError`"],
        ["`s.count(sub)`", "Number of **non-overlapping** occurrences", "`0`"],
        ["`s.startswith(p)` / `s.endswith(p)`", "`bool` — `p` may be a **tuple** of options", "`False`"],
        ["`sub in s`", "`bool` — the most readable test", "`False`"],
    )
    yield code('''
        path = "reports/2026/q1.final.csv"
        print(path.find("/"), path.rfind("/"), path.find("zip"))   # 7 12 -1
        print(path[path.rfind(".") + 1:])                         # csv
        print(path.endswith((".csv", ".tsv")))                    # True
        print("aaaa".count("aa"), "2026" in path)                 # 2 True
        print("banana".find("a", 2), "banana".find("a", 2, 3))    # 3 -1
    ''')
    yield note("Use `find` when \"not found\" is a normal outcome (check for `-1`); use `index` when absence is a bug and an exception is what you want. For a plain yes/no, `in` beats both.")
    yield section("Splitting family", "arrows-split")
    yield table(
        ["Method", "Behaviour"],
        ["`s.split()`", "Split on **runs of any whitespace**, dropping empty strings and leading/trailing space"],
        ["`s.split(sep)`", "Split on an exact separator — keeps empty strings between adjacent separators"],
        ["`s.split(sep, maxsplit)`", "At most `maxsplit` splits, from the left"],
        ["`s.rsplit(sep, maxsplit)`", "At most `maxsplit` splits, from the **right**"],
        ["`s.splitlines()`", "Split on `\\n`, `\\r\\n`, `\\r`… without a trailing empty item"],
        ["`s.partition(sep)`", "Always a 3-tuple `(before, sep, after)` — at the **first** `sep`"],
        ["`s.rpartition(sep)`", "Same, at the **last** `sep`"],
    )
    yield code('''
        print("  a   b  c ".split())               # ['a', 'b', 'c']
        print("a,,b,".split(","))                  # ['a', '', 'b', '']
        print("k=v=w".split("=", 1))               # ['k', 'v=w']
        print("a.b.c.txt".rsplit(".", 1))          # ['a.b.c', 'txt']
        print("one\\ntwo\\r\\nthree\\n".splitlines())  # ['one', 'two', 'three']
        print("one\\ntwo\\n".split("\\n"))            # ['one', 'two', '']
        print("user@example.com".partition("@"))   # ('user', '@', 'example.com')
        print("no-at-sign".partition("@"))         # ('no-at-sign', '', '')
        key, _, value = "timeout=30".partition("=")
        print(key, value)                          # timeout 30
    ''')
    yield note("`partition` never raises and always returns three parts — perfect for `key, _, value = line.partition('=')` parsing without an `if`.")
    yield section("Trimming & prefixes", "cut")
    yield code('''
        print("  hi  ".strip() + "|")               # hi|
        print("xxhixyx".strip("xy"))                # hi   ← a SET of characters, not a substring
        print("www.python.org".lstrip("w."))        # python.org
        print("test_login.py".removesuffix(".py"))  # test_login
        print("mississippi".rstrip("ip"))           # mississ
        print("mississippi".removesuffix("ippi"))   # mississ
        print("reader.txt".rstrip(".txt"))          # reader   ← looks right…
        print("rat.txt".rstrip(".txt"))             # ra       ← …but eats the 't' of 'rat'
        print("rat.txt".removesuffix(".txt"))       # rat
    ''')
    yield warn("`strip`/`lstrip`/`rstrip(chars)` remove **any combination of those characters**, not a prefix/suffix string. To remove an exact prefix or suffix use `removeprefix` / `removesuffix` (3.9+).", "Classic bug")
    yield section("Padding & alignment", "align-center")
    yield code('''
        print("[" + "hi".center(8, "*") + "]")      # [***hi***]
        print("[" + "hi".ljust(6) + "]")            # [hi    ]
        print("[" + "hi".rjust(6, ".") + "]")       # [....hi]
        print("42".zfill(5), "-42".zfill(5))        # 00042 -0042
        print("a\\tbc\\td".expandtabs(4))             # a   bc  d
        print("-" * 10)                             # ----------
    ''')
    yield note("For tables and reports, f-string alignment (`f'{x:>8}'`) does the same job inline — see *String Formatting*.")
    yield section("Replacing & translating", "replace")
    yield code('''
        s = "a-b-c-d"
        print(s.replace("-", "+"))                  # a+b+c+d
        print(s.replace("-", "", 2))                # abc-d   ← only the first 2
        table = str.maketrans({"a": "4", "e": "3", "o": "0"})
        print("hello world".translate(table))       # h3ll0 w0rld
        strip_vowels = str.maketrans("", "", "aeiou")   # 3rd arg: characters to delete
        print("programming".translate(strip_vowels))    # prgrmmng
        print("abc".translate(str.maketrans("abc", "xyz")))   # xyz
    ''')
    yield p("`translate` does many single-character replacements (and deletions) in **one pass** — much faster than chaining `replace` calls.")
    yield section("Character-class predicates", "checkbox")
    yield table(
        ["Method", "True when every character is…", "`'²'`", "`'½'`", "`'٣'` (Arabic 3)"],
        ["`isdecimal()`", "a decimal digit usable by `int()`", "False", "False", "True"],
        ["`isdigit()`", "a digit, including superscripts", "True", "False", "True"],
        ["`isnumeric()`", "any numeric character, incl. fractions", "True", "True", "True"],
    )
    yield code('''
        for s in ["123", "²", "½", "٣", "-5", "3.5", ""]:
            print(repr(s), s.isdecimal(), s.isdigit(), s.isnumeric())
    ''', check=False)
    yield output('''
        '123' True True True
        '²' False True True
        '½' False False True
        '٣' True True True
        '-5' False False False
        '3.5' False False False
        '' False False False
    ''')
    yield code('''
        print("abc123".isalnum(), "abc".isalpha(), "ABC".isupper())    # True True True
        print(" \\t\\n".isspace(), "".isspace())                          # True False
        print("my_var".isidentifier(), "2fast".isidentifier())          # True False
        print(int("٣") + 1)                                             # 4
    ''')
    yield warn("None of the digit predicates accept `'-5'` or `'3.5'`. To check \"is this a number?\", just try `int(s)` / `float(s)` and catch `ValueError` (EAFP). Also note all predicates return `False` for the empty string.")
    yield section("Comparison, repetition & membership", "equal")
    yield code('''
        print("apple" < "banana", "Zebra" < "apple")     # True True   ← 'Z' (90) < 'a' (97)
        print(sorted(["b", "C", "a"]))                   # ['C', 'a', 'b']
        print(sorted(["b", "C", "a"], key=str.casefold)) # ['a', 'b', 'C']
        print("10" < "9", int("10") < int("9"))          # True False
        print("ab" * 3, "-" * 0 == "")                   # ababab True
        print("ell" in "hello", "" in "hello")           # True True
    ''')
    yield warn("String comparison is **lexicographic by code point**: uppercase sorts before lowercase and `'10' < '9'`. Sort with `key=str.casefold` for human order and convert numeric strings before comparing.")
    yield section("Building strings efficiently", "bolt")
    yield dodont(
        "Collect pieces in a list and call `''.join(parts)` once — O(total length). `join` needs strings: `', '.join(map(str, nums))`.",
        "`s += piece` inside a big loop — each `+=` may copy the whole string (O(n²) worst case). CPython sometimes optimises it, but don't rely on it.",
    )
    yield code('''
        nums = [3, 1, 4]
        print(", ".join(map(str, nums)))      # 3, 1, 4
        print("".join(reversed("stressed")))  # desserts
        try:
            ", ".join(nums)
        except TypeError as e:
            print(type(e).__name__)           # TypeError
    ''')
    yield section("Interview questions", "message-question")
    yield qa("What's the difference between `find` and `index`?",
             "Both return the lowest index of a substring. `find` returns `-1` when it's missing; `index` raises `ValueError`. Lists only have `index`.")
    yield qa("Why does `'rat.txt'.rstrip('.txt')` return `'ra'`?",
             "`rstrip` takes a *set of characters* and strips any of them from the end — `t`, `x`, `.` — until it hits a character not in the set. Use `removesuffix('.txt')` to remove an exact suffix.")
    yield qa("`lower()` vs `casefold()`?",
             "`casefold()` is a stronger normalisation meant for caseless matching: it also maps characters like `ß` → `ss`. Use `casefold()` when comparing user text case-insensitively; `lower()` for display.")
    yield qa("How do you reverse the words of a sentence?",
             code('''
                 s = "  the sky  is blue "
                 print(" ".join(reversed(s.split())))   # blue is sky the
             '''),
             "`split()` with no arguments discards extra whitespace, so the result has single spaces.")


@topic(G, "string-formatting", "String Formatting & f-strings", "braces")
def _():
    yield lead("f-strings are the modern way to build text: any expression inside `{}`, plus a compact *format spec* after `:` that controls width, alignment, precision, signs and number bases.")
    yield section("f-string basics", "braces")
    yield code('''
        name, items, price = "Asha", 3, 49.5
        print(f"{name} bought {items} items")            # Asha bought 3 items
        print(f"total = {items * price}")                # total = 148.5
        print(f"{name.upper()} {len(name)} {'yes' if items > 2 else 'no'}")   # ASHA 4 yes
        print(f"{{literal braces}} {items}")             # {literal braces} 3
        data = {"k": [10, 20]}
        print(f"{data['k'][1]}")                         # 20
    ''')
    yield table(
        ["Part", "Syntax", "Example"],
        ["Expression", "`{expr}`", "`f'{a + b}'`"],
        ["Conversion", "`{expr!r}` / `!s` / `!a`", "`repr()`, `str()`, `ascii()` of the value"],
        ["Format spec", "`{expr:spec}`", "`f'{pi:.3f}'`"],
        ["Self-documenting", "`{expr=}`", "`f'{x=}'` → `x=5` (3.8+)"],
        ["Nested spec", "`{expr:{width}.{prec}f}`", "Width/precision from variables"],
        ["Literal brace", "`{{` and `}}`", "`f'{{x}}'` → `{x}`"],
    )
    yield section("Debugging with `=` and conversions", "bug")
    yield code('''
        x, word = 42, "café"
        print(f"{x=}")                  # x=42
        print(f"{x * 2 = }")            # x * 2 = 84
        print(f"{word=}")               # word='café'   ← = uses repr() by default
        print(f"{word!s}", f"{word!r}", f"{word!a}")   # café 'café' 'caf\\xe9'
        print(f"{x = :>6}|")            # x =     42|
    ''')
    yield note("`{x=}` prints the expression text, then the value's `repr()` — the quickest print-debugging tool in Python.", "Tip")
    yield section("The format-spec mini-language", "adjustments")
    yield formula("`[[fill]align][sign][z][#][0][width][grouping][.precision][type]`")
    yield table(
        ["Field", "Options", "Meaning"],
        ["fill", "any character", "Pad character (needs an align after it)"],
        ["align", "`<` `>` `^` `=`", "Left / right / centre / pad after the sign"],
        ["sign", "`+` `-` space", "Always show sign / only negatives (default) / space for positives"],
        ["`#`", "", "Alternate form: `0b`, `0o`, `0x` prefixes"],
        ["`0`", "", "Zero-pad numbers (sign-aware)"],
        ["width", "integer", "Minimum field width"],
        ["grouping", "`,` or `_`", "Thousands separator"],
        [".precision", "integer", "Digits after the point (`f`, `%`), significant digits (`g`), or max chars for strings"],
        ["type", "`d b o x X e f g % n s c`", "Presentation: decimal, binary, octal, hex, exponent, fixed, general, percent…"],
    )
    yield section("Alignment & padding", "align-left")
    yield code('''
        s = "py"
        print(f"[{s:<6}] [{s:>6}] [{s:^6}]")      # [py    ] [    py] [  py  ]
        print(f"[{s:*^8}] [{s:->5}]")             # [***py***] [---py]
        print(f"[{42:5}] [{'ab':5}]")             # [   42] [ab   ]   ← numbers right, strings left by default
        print(f"[{-42:=+7}] [{-42:07}]")          # [-    42] [-000042]
        print(f"[{'truncate me':.5}]")            # [trunc]
    ''')
    yield section("Numbers: precision, signs, grouping", "number")
    yield code('''
        pi, big, ratio = 3.14159265, 1234567.891, 0.4567
        print(f"{pi:.2f} {pi:.4f} {pi:8.3f}|")    # 3.14 3.1416    3.142|
        print(f"{big:,.2f} {big:_.1f}")           # 1,234,567.89 1_234_567.9
        print(f"{ratio:.1%} {ratio:%}")           # 45.7% 45.670000%
        print(f"{big:e} {big:.2e}")               # 1.234568e+06 1.23e+06
        print(f"{pi:g} {big:g} {0.00001234:g}")   # 3.14159 1.23457e+06 1.234e-05
        print(f"{5:+d} {-5:+d} {5: d}")           # +5 -5  5
        print(f"{1_000_000:,}")                   # 1,000,000
    ''')
    yield section("Integers in other bases", "binary")
    yield code('''
        n = 255
        print(f"{n:b} {n:o} {n:x} {n:X}")         # 11111111 377 ff FF
        print(f"{n:#b} {n:#o} {n:#x}")            # 0b11111111 0o377 0xff
        print(f"{5:08b}")                         # 00000101
        print(f"{n:#06x}")                        # 0x00ff   ← width counts the prefix
        print(f"{65:c}")                          # A
        print(format(n, "x"), int("ff", 16))      # ff 255
    ''')
    yield section("Nested & dynamic specs", "stack")
    yield code('''
        rows = [("apple", 1.5), ("kiwi", 12.25)]
        w = max(len(name) for name, _ in rows)
        for name, cost in rows:
            print(f"{name:<{w}} | {cost:>{8}.{2}f}")
    ''', check=False)
    yield output('''
        apple |     1.50
        kiwi  |    12.25
    ''')
    yield section("Dates in f-strings", "calendar")
    yield code('''
        from datetime import datetime
        d = datetime(2026, 9, 29, 14, 5)
        print(f"{d:%Y-%m-%d %H:%M}")        # 2026-09-29 14:05
        print(f"{d:%d %b %Y, %A}")          # 29 Sep 2026, Tuesday
        print(f"{d:%I:%M %p}")              # 02:05 PM
    ''')
    yield note("A format spec is passed to the object's `__format__` method — that is why `datetime` understands `strftime` codes after the colon.")
    yield section("`__format__` for your own classes", "wand")
    yield code('''
        class Money:
            def __init__(self, amount):
                self.amount = amount
            def __format__(self, spec):
                if spec == "inr":
                    return f"₹{self.amount:,.2f}"
                return format(self.amount, spec)     # fall back to float formatting

        m = Money(1234.5)
        print(f"{m:inr}")              # ₹1,234.50
        print(f"{m:>10.1f}|")          #     1234.5|
        print(format(m, "inr"))        # ₹1,234.50
    ''')
    yield section("Older styles: `str.format`, `%` and `Template`", "history")
    yield code('''
        print("{} + {} = {}".format(1, 2, 3))              # 1 + 2 = 3
        print("{0}{1}{0}".format("ab", "-"))               # ab-ab
        print("{name} is {age}".format(name="Ravi", age=30))   # Ravi is 30
        point = {"x": 3, "y": 4}
        print("({p[x]}, {p[y]})".format(p=point))          # (3, 4)
        print("{:>6.2f}|".format(3.14159))                 #   3.14|

        print("%s has %d items (%.1f%%)" % ("cart", 3, 42.456))   # cart has 3 items (42.5%)
        print("%(who)s says hi" % {"who": "Asha"})         # Asha says hi

        from string import Template
        t = Template("Hello $name, you owe $$${amount}")
        print(t.substitute(name="Kiran", amount=20))       # Hello Kiran, you owe $20
        print(t.safe_substitute(name="Kiran"))             # Hello Kiran, you owe $${amount}
    ''')
    yield table(
        ["Style", "Use it for"],
        ["f-strings", "**Default choice** — fastest and most readable (3.6+)"],
        ["`str.format`", "Templates stored separately from the values, e.g. `FMT.format(**row)`"],
        ["`%` formatting", "Legacy code and `logging` calls (`log.info('%s', x)` formats lazily)"],
        ["`string.Template`", "Templates written by **users** — `$name` only, no expressions, so it's safe"],
    )
    yield warn("Never call `.format()` or build f-strings from untrusted template text — `'{0.__class__}'.format(obj)` can read attributes. Use `string.Template` for user-supplied templates.", "Security")
    yield section("Python 3.12+: f-strings grew up", "sparkles")
    yield code('''
        songs = ["a", "b"]
        print(f"{", ".join(songs)}")          # a, b     ← same quotes inside (3.12+)
        print(f"{'\\n'.join(songs)!r}")        # 'a\\nb'   ← backslashes allowed in expressions
        total = f"{
            sum([1, 2, 3])                   # comments and line breaks inside {} are fine
        }"
        print(total)                          # 6
    ''')
    yield note("PEP 701 (3.12) made f-strings part of the real grammar: reuse the outer quote type, write backslashes and comments inside the braces, and nest arbitrarily. Python 3.14 adds **t-strings** (`t'…'`) that produce a `Template` object for safe, deferred processing (e.g. SQL/HTML escaping).", "Version")
    yield section("Pitfalls", "alert-triangle")
    yield ul(
        "`f'{x:.2f}'` on a string raises `ValueError: Unknown format code 'f'` — convert first.",
        "`round(x, 2)` changes the value; `f'{x:.2f}'` only changes how it is *displayed*. For money use `Decimal`.",
        "`=` in `{x=}` uses `repr`, so strings appear quoted — add `!s` for the plain form.",
        "Forgetting the `f` prefix silently prints the braces: `'{name}'`.",
    )
    yield qa("How do you print a float with 2 decimals and thousands separators, right-aligned in 12 characters?",
             code('''
                 print(f"{1234567.891:>12,.2f}|")   # 1,234,567.89|
             '''),
             "Spec parts in order: align `>`, width `12`, grouping `,`, precision `.2`, type `f`.")
    yield qa("Which string formatting method is fastest?",
             "f-strings — they compile to direct bytecode (`FORMAT_VALUE` / `BUILD_STRING`) with no method lookup or argument parsing, so they beat `str.format` and `%`.")


@topic(G, "unicode-bytes", "Unicode, Bytes & Encodings", "language")
def _():
    yield lead("A `str` is a sequence of Unicode **code points**; `bytes` is a sequence of raw 8-bit values. An *encoding* such as UTF-8 is the bridge — and most text bugs come from crossing that bridge carelessly.")
    yield define("Code point", "a number that identifies one Unicode character, written `U+0041` for `A`. `ord()` gives it, `chr()` goes back. Python strings index and measure in code points.")
    yield flow("`str` (text)", "`.encode('utf-8')`", "`bytes` (disk / network)", "`.decode('utf-8')`", "`str`")
    yield section("Code points & escapes", "hash")
    yield code('''
        print(ord("A"), hex(ord("€")), chr(0x1F600))       # 65 0x20ac 😀
        print("\\u00e9", "\\U0001F40D", "\\N{GREEK SMALL LETTER PI}")   # é 🐍 π
        import unicodedata
        print(unicodedata.name("€"))                       # EURO SIGN
        print(unicodedata.category("A"), unicodedata.category("5"))   # Lu Nd
    ''')
    yield table(
        ["Escape", "Meaning", "Example"],
        ["`\\xhh`", "Code point with 2 hex digits", "`'\\xe9'` → `é`"],
        ["`\\uhhhh`", "4 hex digits (BMP)", "`'\\u20ac'` → `€`"],
        ["`\\Uhhhhhhhh`", "8 hex digits (any code point)", "`'\\U0001F600'` → 😀"],
        ["`\\N{name}`", "By official Unicode name", "`'\\N{SNOWMAN}'` → ☃"],
    )
    yield section("UTF-8: variable-length encoding", "ruler")
    yield code('''
        for ch in ["A", "é", "€", "😀"]:
            b = ch.encode("utf-8")
            print(ch, len(b), b)
    ''', check=False)
    yield output('''
        A 1 b'A'
        é 2 b'\\xc3\\xa9'
        € 3 b'\\xe2\\x82\\xac'
        😀 4 b'\\xf0\\x9f\\x98\\x80'
    ''')
    yield code('''
        s = "naïve café"
        print(len(s), len(s.encode("utf-8")), len(s.encode("utf-16")))   # 10 12 22
        print(s.encode("utf-8")[:3])                                    # b'na\\xc3'
    ''')
    yield cards(
        ("UTF-8", "1–4 bytes per code point, ASCII-compatible, no byte-order issues. **The default everywhere** — web, Linux, Python source files.", "world"),
        ("UTF-16 / UTF-32", "2–4 / always 4 bytes. Used internally by Windows, Java and JavaScript. Need a byte-order mark (BOM).", "binary"),
        ("Latin-1 (ISO-8859-1)", "One byte per character, only 256 characters. Decoding **never fails** — every byte maps to something (often wrong).", "alphabet-latin"),
        ("ASCII", "7-bit, 128 characters. Any non-English text raises `UnicodeEncodeError`.", "abc"),
    )
    yield section("Encoding errors and `errors=`", "alert-triangle")
    yield code('''
        data = "café".encode("utf-8")
        print(data.decode("utf-8"))                        # café
        print(data.decode("latin-1"))                      # cafÃ©   ← mojibake: wrong codec
        try:
            data.decode("ascii")
        except UnicodeDecodeError as e:
            print(e.reason, e.start)                       # ordinal not in range(128) 3
        print(data.decode("ascii", errors="replace"))      # caf��
        print(data.decode("ascii", errors="ignore"))       # caf
        print("café".encode("ascii", errors="xmlcharrefreplace"))   # b'caf&#233;'
        print("café".encode("ascii", errors="backslashreplace"))    # b'caf\\\\xe9'
    ''')
    yield table(
        ["`errors=`", "On bad data"],
        ["`'strict'` (default)", "Raise `UnicodeEncodeError` / `UnicodeDecodeError`"],
        ["`'replace'`", "Substitute `?` (encode) or `U+FFFD` � (decode)"],
        ["`'ignore'`", "Silently drop — loses data"],
        ["`'backslashreplace'`", "Write escapes like `\\xe9`"],
        ["`'surrogateescape'`", "Round-trip undecodable bytes (used for OS file names)"],
    )
    yield warn("*Mojibake* (`cafÃ©`) means text was encoded with one codec and decoded with another. Fix it at the boundary — always state the encoding when you read or write.")
    yield section("`bytes`, `bytearray` & `memoryview`", "binary")
    yield code('''
        b = b"hi\\x00\\xff"
        print(b[0], b[-1], list(b))            # 104 255 [104, 105, 0, 255]
        print(b[:2], type(b[:2]).__name__)     # b'hi' bytes
        print(b.hex(), bytes.fromhex("48 69"))  # 686900ff b'Hi'
        print(bytes([72, 105]), bytes(3))      # b'Hi' b'\\x00\\x00\\x00'

        buf = bytearray(b"hello")              # mutable
        buf[0] = ord("J")
        buf.extend(b"!")
        print(buf, bytes(buf))                 # bytearray(b'Jello!') b'Jello!'

        view = memoryview(buf)[1:4]            # zero-copy slice
        view[0] = ord("E")
        print(buf)                             # bytearray(b'JEllo!')
    ''')
    yield table(
        ["Type", "Mutable", "Indexing gives", "Use for"],
        ["`str`", "No", "a 1-char `str`", "Human text"],
        ["`bytes`", "No", "an `int` 0–255", "Binary data, network payloads, hashes"],
        ["`bytearray`", "Yes", "an `int` 0–255", "Building/patching binary buffers"],
        ["`memoryview`", "Follows the buffer", "an `int`", "Zero-copy slices of large buffers"],
    )
    yield warn("You can't mix them: `'a' + b'b'` raises `TypeError`. Decode bytes to text as early as possible and encode as late as possible (the *Unicode sandwich*).")
    yield section("Normalization: same text, different code points", "equal-not")
    yield code('''
        import unicodedata
        a = "café"                        # é as one code point U+00E9
        b = "cafe\\u0301"                  # e + COMBINING ACUTE ACCENT
        print(a == b)                     # False   ← both render as "café"
        print(len(a), len(b))             # 4 5
        nfc = lambda s: unicodedata.normalize("NFC", s)
        print(nfc(a) == nfc(b))           # True
        print(len(unicodedata.normalize("NFD", a)))   # 5
        print(unicodedata.normalize("NFKC", "ﬁ①"))   # fi1
    ''')
    yield table(
        ["Form", "Does", "Use"],
        ["NFC", "Compose into single code points where possible", "Storing and comparing text (the web default)"],
        ["NFD", "Decompose into base + combining marks", "Stripping accents"],
        ["NFKC / NFKD", "Also fold *compatibility* forms: `ﬁ` → `fi`, `①` → `1`", "Search, identifiers, user names"],
    )
    yield code('''
        import unicodedata
        def strip_accents(s):
            decomposed = unicodedata.normalize("NFD", s)
            return "".join(c for c in decomposed if not unicodedata.combining(c))

        print(strip_accents("Crème brûlée à São Paulo"))   # Creme brulee a Sao Paulo
        def same_text(x, y):
            norm = lambda s: unicodedata.normalize("NFC", s).casefold()
            return norm(x) == norm(y)
        print(same_text("STRASSE", "straße"))             # True
    ''')
    yield section("Length isn't what users see", "mood-smile")
    yield code('''
        thumbs = "👍🏽"                        # thumbs up + skin-tone modifier
        family = "👨\\u200d👩\\u200d👧"           # joined with ZERO WIDTH JOINERs
        flag = "🇮🇳"                           # two regional-indicator letters
        print(len(thumbs), len(family), len(flag))   # 2 5 2
        print(thumbs[::-1] == thumbs)              # False   ← reversing splits the emoji
    ''')
    yield note("A user-perceived character (a *grapheme cluster*) can be several code points. `len`, slicing and `[::-1]` work on code points, so they can cut emoji or accented letters in half. For true grapheme handling use the third-party `grapheme` or `regex` (`\\X`) modules.")
    yield section("Files & encodings", "file-text")
    yield code('''
        import tempfile, os
        path = os.path.join(tempfile.mkdtemp(), "bom.csv")
        with open(path, "w", encoding="utf-8-sig") as f:     # writes a BOM (Excel likes it)
            f.write("name\\nAsha\\n")
        with open(path, "rb") as f:
            print(f.read(3))                                  # b'\\xef\\xbb\\xbf'
        with open(path, encoding="utf-8") as f:
            print(repr(f.readline()))                         # '\\ufeffname\\n'
        with open(path, encoding="utf-8-sig") as f:           # strips the BOM
            print(repr(f.readline()))                         # 'name\\n'
    ''')
    yield ul(
        "Always pass `encoding='utf-8'` to `open()` in text mode — the default depends on the OS locale (Python 3.15 makes UTF-8 the default).",
        "Open binary files (`'rb'`, `'wb'`) for images, zips and anything you'll hash — you get `bytes`, no decoding.",
        "`utf-8-sig` reads files with or without a BOM; use it for CSVs from Excel.",
        "`sys.getdefaultencoding()` is always `'utf-8'`; `locale.getpreferredencoding()` is what `open()` uses by default.",
    )
    yield section("Interview questions", "message-question")
    yield qa("What is the difference between `str` and `bytes`?",
             "`str` is text: a sequence of Unicode code points. `bytes` is binary data: a sequence of integers 0–255. You convert with `str.encode(encoding)` and `bytes.decode(encoding)`; you can't concatenate them directly.")
    yield qa("Why is `len('é')` sometimes 1 and sometimes 2?",
             "`é` can be one precomposed code point (U+00E9) or `e` plus a combining accent (U+0301). Both render the same. Normalize with `unicodedata.normalize('NFC', s)` before comparing or measuring.")
    yield qa("What is UTF-8 and why is it the default?",
             "A variable-length encoding of Unicode using 1–4 bytes per code point. It is backward-compatible with ASCII, has no byte-order issues, is compact for English text, and can encode every character — so it became the standard for files, the web and Python source code.")


@topic(G, "numbers", "Numbers: int, float, Decimal & Fraction", "number")
def _():
    yield lead("Python has unlimited-size integers, IEEE-754 binary floats, exact `Decimal` and `Fraction` types and a rich `math` module. Picking the right one avoids rounding bugs and overflow.")
    yield table(
        ["Type", "Precision", "Speed", "Use for"],
        ["`int`", "Exact, **unlimited** size", "Fast", "Counting, indices, IDs, big-number math"],
        ["`float`", "~15–17 significant digits (64-bit binary)", "Fastest (hardware)", "Science, measurements, ML — where tiny errors are fine"],
        ["`decimal.Decimal`", "Exact decimal, configurable precision", "Slower", "**Money**, financial rounding rules"],
        ["`fractions.Fraction`", "Exact rational `p/q`", "Slowest", "Exact ratios, probability, teaching"],
        ["`complex`", "Pair of floats", "Fast", "Signal processing, maths (`2 + 3j`)"],
    )
    yield section("Integers: unlimited & many literals", "number")
    yield code('''
        print(2 ** 100)                               # 1267650600228229401496703205376
        print(0b1010, 0o17, 0xFF, 1_000_000)          # 10 15 255 1000000
        print(int("1010", 2), int("z", 36), int(" 42 "))   # 10 35 42
        n = 37
        print(n.bit_length(), n.bit_count(), bin(n))  # 6 3 0b100101
        print(7 // 2, -7 // 2, -7 % 3, int(-3.9))     # 3 -4 2 -3
        print(divmod(17, 5), divmod(-17, 5))          # (3, 2) (-4, 3)
    ''')
    yield note("`//` and `%` round toward **negative infinity**, so `-7 // 2 == -4` and `-7 % 3 == 2` (the result has the sign of the divisor). C and Java truncate toward zero. `int()` truncates toward zero.")
    yield code('''
        print(pow(2, 10), pow(2, 10, 1000))    # 1024 24     ← fast modular exponentiation
        print(pow(3, -1, 7))                   # 5           ← modular inverse: 3 * 5 % 7 == 1
        print(True + True, isinstance(True, int))   # 2 True
        print((255).to_bytes(2, "big"), int.from_bytes(b"\\x01\\x00", "big"))   # b'\\x00\\xff' 256
    ''')
    yield warn("Converting a huge `int` to/from `str` is limited to 4300 digits by default (a DoS protection since 3.11): `str(10**5000)` raises `ValueError`. Raise it with `sys.set_int_max_str_digits(n)` if you really need to.")
    yield section("Floats are binary approximations", "alert-triangle")
    yield code('''
        print(0.1 + 0.2)                        # 0.30000000000000004
        print(0.1 + 0.2 == 0.3)                 # False
        import math
        print(math.isclose(0.1 + 0.2, 0.3))     # True
        print((0.1).as_integer_ratio())         # (3602879701896397, 36028797018963968)
        print(f"{0.1:.20f}")                    # 0.10000000000000000555
        total = 0.0
        for _ in range(10):
            total += 0.1                        # error accumulates step by step
        print(total, math.fsum([0.1] * 10))     # 0.9999999999999999 1.0
        print(sum([0.1] * 10))                  # 1.0   ← sum() of floats is compensated since 3.12
        print(2 ** 53 + 1.0 == 2 ** 53)         # True   ← integers above 2**53 lose precision
    ''')
    yield define("IEEE 754 double", "64 bits: 1 sign bit, 11 exponent bits, 52 fraction bits. Only numbers of the form *m × 2ᵉ* are exact, so decimal fractions like 0.1 are stored as the nearest binary value.")
    yield dodont(
        "Compare floats with `math.isclose(a, b, rel_tol=1e-9, abs_tol=…)`; sum many floats with `math.fsum`; keep money in integer cents or `Decimal`.",
        "`if total == 0.3:` or storing prices as floats — errors accumulate and comparisons fail.",
    )
    yield section("inf, nan & float limits", "infinity")
    yield code('''
        import math, sys
        inf, nan = float("inf"), float("nan")
        print(inf > 10**308, -inf < 0, inf - inf)     # True True nan
        print(nan == nan, math.isnan(nan))            # False True
        print(1e308 * 10, 2.0 ** -1075)               # inf 0.0
        print(sys.float_info.max, sys.float_info.epsilon)   # 1.7976931348623157e+308 2.220446049250313e-16
        print(sorted([3, nan, 1]))                    # [3, nan, 1]   ← nan breaks sorting
    ''')
    yield warn("`nan` is not equal to anything, including itself, so `x in list`, `sort`, `max` and dict lookups behave strangely with it. Filter with `math.isnan` first. Also `1 / 0` raises `ZeroDivisionError` — Python does not return `inf` for division.")
    yield section("Rounding", "arrows-up-down")
    yield code('''
        import math
        print(round(2.5), round(3.5), round(-2.5))       # 2 4 -2   ← banker's rounding
        print(round(2.675, 2))                           # 2.67     ← 2.675 is really 2.67499999…
        print(round(1234.5678, -2))                      # 1200.0
        print(math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5))   # -3 -2 -2
        print(int(2.99), math.floor(2.99))               # 2 2
    ''')
    yield table(
        ["Function", "Rounds", "`2.5`", "`-2.5`"],
        ["`round(x)`", "To nearest, ties to **even**", "`2`", "`-2`"],
        ["`math.floor(x)`", "Down (toward −∞)", "`2`", "`-3`"],
        ["`math.ceil(x)`", "Up (toward +∞)", "`3`", "`-2`"],
        ["`math.trunc(x)` / `int(x)`", "Toward zero", "`2`", "`-2`"],
        ["`Decimal.quantize(…, ROUND_HALF_UP)`", "Ties away from zero (school rounding)", "`3`", "`-3`"],
    )
    yield section("Decimal: exact decimal arithmetic", "coin-rupee")
    yield code('''
        from decimal import Decimal, ROUND_HALF_UP, getcontext, localcontext
        print(Decimal("0.1") + Decimal("0.2"))               # 0.3
        print(Decimal(0.1))                                  # 0.1000000000000000055511151231257827021181583404541015625
        price = Decimal("19.99")
        total = price * 3
        print(total, total * Decimal("1.18"))                # 59.97 70.7646
        tax = (total * Decimal("0.18")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        print(tax)                                           # 10.79
        print(Decimal("2.5").quantize(Decimal("1"), rounding=ROUND_HALF_UP))   # 3
        print(getcontext().prec)                             # 28
        with localcontext() as ctx:
            ctx.prec = 5
            print(Decimal(1) / Decimal(7))                   # 0.14286
    ''')
    yield warn("Build `Decimal` from **strings** (`Decimal('0.1')`), never from floats — `Decimal(0.1)` faithfully copies the float's binary error. Also don't mix `Decimal` and `float` in arithmetic: it raises `TypeError`.")
    yield section("Fraction & complex", "divide")
    yield code('''
        from fractions import Fraction
        f = Fraction(1, 3) + Fraction(1, 6)
        print(f, f.numerator, f.denominator)            # 1/2 1 2
        print(Fraction("0.75"), Fraction(0.1).limit_denominator(100))   # 3/4 1/10
        print(float(Fraction(22, 7)))                   # 3.142857142857143

        z = 3 + 4j
        print(z.real, z.imag, abs(z), z.conjugate())    # 3.0 4.0 5.0 (3-4j)
        import cmath
        print(cmath.sqrt(-1))                           # 1j
    ''')
    yield section("The `math` module", "math-function")
    yield table(
        ["Function", "Does", "Example"],
        ["`sqrt`, `isqrt`", "Float root / exact integer floor root", "`math.isqrt(17)` → `4`"],
        ["`gcd`, `lcm`", "Greatest common divisor / least common multiple (any number of args)", "`math.lcm(4, 6)` → `12`"],
        ["`comb`, `perm`, `factorial`", "nCr, nPr, n!", "`math.comb(5, 2)` → `10`"],
        ["`prod`, `fsum`", "Product / precise float sum", "`math.prod([2, 3, 4])` → `24`"],
        ["`log`, `log2`, `log10`, `exp`", "Logarithms (`log(x, base)`)", "`math.log2(1024)` → `10.0`"],
        ["`hypot`, `dist`", "Euclidean length / distance between points", "`math.dist((0, 0), (3, 4))` → `5.0`"],
        ["`floor`, `ceil`, `trunc`", "Rounding to int", "`math.ceil(2.1)` → `3`"],
        ["`pi`, `e`, `tau`, `inf`, `nan`", "Constants", "`math.tau == 2 * math.pi`"],
        ["`isclose`, `isfinite`, `isnan`", "Float checks", "`math.isclose(0.1 + 0.2, 0.3)`"],
    )
    yield code('''
        import math
        print(math.isqrt(10**20), math.sqrt(2))        # 10000000000 1.4142135623730951
        print(math.gcd(12, 18, 30), math.lcm(4, 6))    # 6 12
        print(math.comb(52, 5), math.perm(5, 2), math.factorial(10))   # 2598960 20 3628800
        print(math.prod(range(1, 6)), math.log2(1024), math.log(8, 2))  # 120 10.0 3.0
        print(math.hypot(3, 4), math.dist((1, 1), (4, 5)))   # 5.0 5.0
        print(math.degrees(math.pi), round(math.sin(math.pi / 6), 3))   # 180.0 0.5
    ''')
    yield note("Use `math.isqrt(n)` — not `int(math.sqrt(n))` — for perfect-square checks on big integers: the float version is wrong once `n` exceeds 2⁵³.")
    yield section("Interview questions", "message-question")
    yield qa("Why is `0.1 + 0.2 != 0.3`?",
             "Floats are binary (IEEE 754). 0.1, 0.2 and 0.3 have no exact binary representation, so each is stored as the nearest double; the rounding errors don't cancel. Compare with `math.isclose`, or use `Decimal` / integer cents when exactness matters.")
    yield qa("Can Python integers overflow?",
             "No. `int` is arbitrary precision — it grows to use as much memory as needed (slower as it grows). Floats can overflow to `inf`, and `numpy` fixed-width integers *do* wrap around.")
    yield qa("What does `round(2.5)` return and why?",
             "`2`. Python 3 uses round-half-to-even (banker's rounding), which avoids a systematic upward bias when rounding many values. Use `Decimal.quantize(..., rounding=ROUND_HALF_UP)` for school-style rounding.")
    yield qa("How would you check whether a large number is a perfect square?",
             code('''
                 import math
                 def is_square(n):
                     return n >= 0 and math.isqrt(n) ** 2 == n
                 print(is_square(10**30), is_square(10**30 + 1))   # True False
             '''))


@topic(G, "regex", "Regular Expressions (re)", "regex")
def _():
    yield lead("A regular expression is a tiny pattern language for matching text. Python's `re` module finds, extracts, validates, splits and rewrites strings with it.")
    yield note("Always write patterns as **raw strings** — `r'\\d+'` — so Python doesn't interpret the backslashes before `re` sees them.", "Rule #1")
    yield section("The five ways to match", "search")
    yield table(
        ["Function", "Returns", "Matches where?"],
        ["`re.match(p, s)`", "`Match` or `None`", "Only at the **start** of `s`"],
        ["`re.search(p, s)`", "`Match` or `None`", "The **first** place anywhere in `s`"],
        ["`re.fullmatch(p, s)`", "`Match` or `None`", "The **whole** string — best for validation"],
        ["`re.findall(p, s)`", "`list` of strings (or tuples of groups)", "Every non-overlapping match"],
        ["`re.finditer(p, s)`", "Iterator of `Match` objects", "Every match, lazily, with positions"],
    )
    yield code(r'''
        import re
        s = "Order 66 shipped on 2026-09-29"
        print(re.match(r"\d+", s))                    # None   ← s doesn't start with a digit
        m = re.search(r"\d+", s)
        print(m.group(), m.start(), m.end(), m.span())   # 66 6 8 (6, 8)
        print(re.findall(r"\d+", s))                  # ['66', '2026', '09', '29']
        print(bool(re.fullmatch(r"\d{4}", "2026")), bool(re.fullmatch(r"\d{4}", "20261")))   # True False
        print([m.start() for m in re.finditer(r"\d+", s)])   # [6, 20, 25, 28]
    ''')
    yield warn("`re.match` only anchors at the start, not the end: `re.match(r'\\d+', '12abc')` succeeds. For validation use `re.fullmatch` (or `^…$` with `search`).")
    yield section("Pattern syntax cheat sheet", "list-details")
    yield table(
        ["Pattern", "Matches"],
        ["`.`", "Any character except newline (any at all with `re.DOTALL`)"],
        ["`\\d` / `\\D`", "Digit / non-digit (Unicode digits by default)"],
        ["`\\w` / `\\W`", "Word char `[A-Za-z0-9_]` + Unicode letters / anything else"],
        ["`\\s` / `\\S`", "Whitespace / non-whitespace"],
        ["`[abc]`, `[a-z]`, `[^0-9]`", "Character class, range, negated class"],
        ["`^` / `$`", "Start / end of string (of each line with `re.MULTILINE`)"],
        ["`\\A` / `\\Z`", "Start / end of string, always"],
        ["`\\b` / `\\B`", "Word boundary / not a boundary"],
        ["`a|b`", "Alternation: `a` or `b`"],
        ["`\\.`, `\\*`, `\\(`", "Escaped literal metacharacters (or use `re.escape(text)`)"],
    )
    yield table(
        ["Quantifier", "Means", "Lazy version"],
        ["`*`", "0 or more", "`*?`"],
        ["`+`", "1 or more", "`+?`"],
        ["`?`", "0 or 1 (optional)", "`??`"],
        ["`{n}`", "Exactly n", "—"],
        ["`{n,m}`", "Between n and m", "`{n,m}?`"],
        ["`{n,}`", "n or more", "`{n,}?`"],
    )
    yield code(r'''
        import re
        text = "cat catalog concat Cat"
        print(re.findall(r"cat", text))              # ['cat', 'cat', 'cat']
        print(re.findall(r"\bcat\b", text))          # ['cat']
        print(re.findall(r"\bcat\b", text, re.I))    # ['cat', 'Cat']
        print(re.findall(r"colou?r", "color colour"))    # ['color', 'colour']
        print(re.findall(r"[A-Z][a-z]+", "Asha met Ravi in Pune"))   # ['Asha', 'Ravi', 'Pune']
        print(re.findall(r"\d{2,3}", "1 12 123 1234"))  # ['12', '123', '123']
        print(re.escape("1+1=2?"))                   # 1\+1=2\?
    ''')
    yield section("Groups: capture, name, skip", "brackets")
    yield code(r'''
        import re
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "due 2026-09-29!")
        print(m.group(0), m.group(1), m.groups())    # 2026-09-29 2026 ('2026', '09', '29')

        m = re.search(r"(?P<user>[\w.]+)@(?P<domain>[\w.]+)", "mail asha.k@lvn.io now")
        print(m["user"], m.group("domain"))          # asha.k lvn.io
        print(m.groupdict())                         # {'user': 'asha.k', 'domain': 'lvn.io'}

        print(re.findall(r"(\w+)=(\d+)", "a=1, b=22"))       # [('a', '1'), ('b', '22')]
        print(re.findall(r"(?:ab)+", "ababab xab"))          # ['ababab', 'ab']
        print(re.findall(r"(ab)+", "ababab xab"))            # ['ab', 'ab']   ← only the last repetition
    ''')
    yield table(
        ["Syntax", "Meaning"],
        ["`(…)`", "Capturing group — `m.group(1)`"],
        ["`(?P<name>…)`", "Named group — `m['name']`, `m.groupdict()`"],
        ["`(?:…)`", "Non-capturing group — groups for `|` or quantifiers without capturing"],
        ["`\\1`, `(?P=name)`", "Backreference to what a group matched"],
    )
    yield warn("With groups in the pattern, `findall` returns the **groups**, not the whole match. Use `(?:…)` for grouping you don't want captured, or `finditer` + `m.group(0)`.")
    yield section("Backreferences", "arrow-back")
    yield code(r'''
        import re
        print(re.findall(r"\b(\w+) \1\b", "this is is a test test"))   # ['is', 'test']
        print(bool(re.fullmatch(r"(['\"]).*\1", "'quoted'")))           # True
        print(re.sub(r"\b(\w+) \1\b", r"\1", "the the cat sat sat"))    # the cat sat
    ''')
    yield section("Substitute & split", "replace")
    yield code(r'''
        import re
        print(re.sub(r"\s+", " ", "too    many\n spaces"))                 # too many spaces
        print(re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2026-09-29"))   # 29/09/2026
        print(re.sub(r"(?P<y>\d{4})", r"<\g<y>>", "in 2026"))                # in <2026>
        print(re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "3 apples, 10 pears"))   # 6 apples, 20 pears
        print(re.subn(r"a", "4", "banana"))                                  # ('b4n4n4', 3)
        print(re.split(r"[,;]\s*", "a, b;c;  d"))                           # ['a', 'b', 'c', 'd']
        print(re.split(r"([,;])", "a,b;c"))                                  # ['a', ',', 'b', ';', 'c']
    ''')
    yield note("`re.sub` accepts a **function** as the replacement: it receives each `Match` and returns the new text — perfect for computed replacements.")
    yield section("Flags", "flag")
    yield table(
        ["Flag", "Inline", "Effect"],
        ["`re.IGNORECASE` / `re.I`", "`(?i)`", "Case-insensitive"],
        ["`re.MULTILINE` / `re.M`", "`(?m)`", "`^` and `$` match at each line"],
        ["`re.DOTALL` / `re.S`", "`(?s)`", "`.` also matches newline"],
        ["`re.VERBOSE` / `re.X`", "`(?x)`", "Ignore whitespace, allow `#` comments in the pattern"],
        ["`re.ASCII` / `re.A`", "`(?a)`", "`\\w`, `\\d`, `\\s` match ASCII only"],
    )
    yield code(r'''
        import re
        log = "ERROR disk\nINFO ok\nERROR net"
        print(re.findall(r"^ERROR (\w+)", log))                 # ['disk']
        print(re.findall(r"^ERROR (\w+)", log, re.M))           # ['disk', 'net']
        print(re.search(r"disk.INFO", log))                     # None
        print(re.search(r"disk.INFO", log, re.S).group() == "disk\nINFO")   # True
        phone = re.compile(r"""
            (\d{3})     # area code
            [-.\s]?     # optional separator
            (\d{4})     # number
        """, re.VERBOSE)
        print(phone.search("call 080-4455").groups())           # ('080', '4455')
    ''')
    yield section("Greedy vs lazy", "arrows-maximize")
    yield code(r'''
        import re
        html = "<b>bold</b> and <i>italic</i>"
        print(re.findall(r"<.+>", html))     # ['<b>bold</b> and <i>italic</i>']   ← greedy: as much as possible
        print(re.findall(r"<.+?>", html))    # ['<b>', '</b>', '<i>', '</i>']     ← lazy: as little as possible
        print(re.findall(r"<[^>]+>", html))  # ['<b>', '</b>', '<i>', '</i>']     ← negated class: fastest & clearest
    ''')
    yield section("Lookahead & lookbehind", "eye")
    yield p("Lookarounds check what is next to the current position **without consuming it** — they are zero-width, so they don't appear in the match.")
    yield table(
        ["Syntax", "Name", "Asserts that…"],
        ["`X(?=Y)`", "Positive lookahead", "`Y` follows"],
        ["`X(?!Y)`", "Negative lookahead", "`Y` does not follow"],
        ["`(?<=Y)X`", "Positive lookbehind", "`Y` precedes (fixed width)"],
        ["`(?<!Y)X`", "Negative lookbehind", "`Y` does not precede"],
    )
    yield code(r'''
        import re
        print(re.findall(r"\d+(?=%)", "5% of 200 is 10"))        # ['5']
        print(re.findall(r"(?<=₹)\d+", "₹250 or $30"))           # ['250']
        print(re.findall(r"\b\d+\b(?!%)", "5% of 200 is 10"))    # ['200', '10']
        print(re.sub(r"\B(?=(\d{3})+(?!\d))", ",", "1234567"))   # 1,234,567

        strong = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}")
        print(bool(strong.fullmatch("Passw0rdX")), bool(strong.fullmatch("password1")))   # True False
    ''')
    yield section("Compile & reuse", "bolt")
    yield code(r'''
        import re
        DATE = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})")
        rows = ["2026-01-05 login", "bad row", "2026-02-11 logout"]
        dates = [m["m"] for r in rows if (m := DATE.search(r))]
        print(dates)                                  # ['01', '02']
        print(DATE.pattern[:6], DATE.groups)          # (?P<y> 3
    ''')
    yield note("`re` caches recently used patterns, so `re.compile` is mostly about **readability and reuse** — a named, documented constant at module level.")
    yield section("Practical recipes", "tools")
    yield code(r'''
        import re
        EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")   # good enough for forms, not RFC 5322
        print(bool(EMAIL.fullmatch("a.b+tag@mail.co.in")), bool(EMAIL.fullmatch("a@b")))   # True False

        tokens = re.findall(r"\d+\.?\d*|[-+*/()]", "3.5*(2+10)/4")
        print(tokens)          # ['3.5', '*', '(', '2', '+', '10', ')', '/', '4']

        def snake(name):
            return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        print(snake("parseHTTPResponseCode"))       # parse_h_t_t_p_response_code
        print(re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", "userIdCount").lower())   # user_id_count

        print(re.findall(r"#(\w+)", "loving #python and #regex!"))   # ['python', 'regex']
    ''')
    yield section("Performance & when not to use regex", "alert-triangle")
    yield warn("Nested quantifiers like `(a+)+$` or `(\\w+\\s?)*$` can cause **catastrophic backtracking**: on a near-miss input the engine tries exponentially many paths and hangs (a ReDoS vulnerability). Avoid ambiguous nested repetition; prefer specific classes like `[^,]*`. Python 3.11+ also supports atomic groups `(?>…)` and possessive quantifiers `*+` to prevent backtracking.", "ReDoS")
    yield dodont(
        "Use plain string methods when they suffice: `in`, `startswith`, `split`, `partition`, `str.isdigit` are faster and clearer.",
        "Parsing HTML, JSON, CSV or email addresses fully with regex — use `html.parser`/BeautifulSoup, `json`, `csv`, `email.utils`.",
    )
    yield section("Interview questions", "message-question")
    yield qa("`re.match` vs `re.search` vs `re.fullmatch`?",
             "`match` tries only at position 0; `search` scans for the first match anywhere; `fullmatch` requires the pattern to match the entire string. Use `fullmatch` for validation.")
    yield qa("What's the difference between greedy and lazy quantifiers?",
             "Greedy (`*`, `+`, `{n,m}`) consume as much as possible and backtrack; lazy (`*?`, `+?`) consume as little as possible. `<.+>` over `<b>x</b>` matches the whole thing, `<.+?>` matches `<b>`.")
    yield qa("Why use raw strings for regex?",
             "In a normal string `'\\b'` is a backspace character and `'\\1'` is chr(1); Python would process the escapes before `re` sees them. `r'\\b'` passes the backslash through literally.")
    yield qa("Extract all numbers (including decimals and negatives) from a string.",
             code(r'''
                 import re
                 print(re.findall(r"-?\d+(?:\.\d+)?", "t=-3.5, x=42, y=0.25"))   # ['-3.5', '42', '0.25']
             '''),
             "The non-capturing group keeps `findall` returning whole matches.")
