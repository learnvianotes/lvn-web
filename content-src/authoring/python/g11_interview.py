from kit import *

G = "Interview Prep"


@topic(G, "python-for-dsa", "Python for DSA & Coding Rounds", "code-dots")
def _():
    yield lead("The complexities, templates and tricks that make Python the fastest language to *write* correct interview solutions in.")
    yield section("Complexity cheat sheet", "clock")
    yield table(
        ["Operation", "list", "dict / set", "deque", "heapq"],
        ["Access by index / key", "O(1)", "O(1) avg", "O(n) in the middle", "—"],
        ["Search `x in …`", "O(n)", "**O(1)** avg", "O(n)", "O(n)"],
        ["Append / add at end", "O(1)*", "O(1) avg", "O(1)", "push O(log n)"],
        ["Remove at front", "**O(n)**", "—", "**O(1)**", "pop min O(log n)"],
        ["Insert / delete in middle", "O(n)", "O(1) avg (by key)", "O(n)", "—"],
        ["Min / max", "O(n)", "O(n)", "O(n)", "**O(1)** peek"],
        ["Sort", "O(n log n)", "—", "—", "—"],
    )
    yield p("* amortised. Strings are immutable: slicing and `+` copy — O(k).")
    yield section("Templates", "template")
    yield code('''
        from collections import deque

        def bfs(graph, start):
            """Shortest path (edges) from start in an unweighted graph."""
            dist = {start: 0}
            q = deque([start])
            while q:
                node = q.popleft()
                for nxt in graph[node]:
                    if nxt not in dist:
                        dist[nxt] = dist[node] + 1
                        q.append(nxt)
            return dist

        graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
        print(bfs(graph, "a"))          # {'a': 0, 'b': 1, 'c': 1, 'd': 2}
    ''', caption="Python — BFS")
    yield code('''
        def lower_bound(nums, target):
            """First index with nums[i] >= target (len(nums) if none)."""
            lo, hi = 0, len(nums)
            while lo < hi:
                mid = (lo + hi) // 2
                if nums[mid] < target:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        print(lower_bound([1, 3, 5, 7], 5), lower_bound([1, 3], 9))   # 2 2
    ''', caption="Python — binary search")
    yield code('''
        def longest_unique_substring(s):
            seen, left, best = {}, 0, 0
            for right, ch in enumerate(s):
                if seen.get(ch, -1) >= left:
                    left = seen[ch] + 1          # shrink past the duplicate
                seen[ch] = right
                best = max(best, right - left + 1)
            return best

        print(longest_unique_substring("abcabcbb"))   # 3
    ''', caption="Python — sliding window")
    yield code('''
        import heapq

        def dijkstra(adj, src):
            dist = {src: 0}
            heap = [(0, src)]
            while heap:
                d, u = heapq.heappop(heap)
                if d > dist.get(u, float("inf")):
                    continue                      # stale entry
                for v, w in adj.get(u, []):
                    nd = d + w
                    if nd < dist.get(v, float("inf")):
                        dist[v] = nd
                        heapq.heappush(heap, (nd, v))
            return dist

        adj = {"a": [("b", 4), ("c", 1)], "c": [("b", 2)]}
        print(dijkstra(adj, "a"))                 # {'a': 0, 'b': 3, 'c': 1}
    ''', caption="Python — Dijkstra")
    yield section("Tricks that save time", "bolt")
    yield cards(
        ("Infinity", "`float('inf')` and `-float('inf')` for initial min/max; `math.inf` works too.", "infinity"),
        ("Big integers", "`int` never overflows — factorials and large sums need no special handling.", "number"),
        ("Fast input", "`import sys; input = sys.stdin.readline` for large competitive-programming inputs.", "keyboard"),
        ("Deep recursion", "`sys.setrecursionlimit(10**6)` — or better, rewrite DFS with an explicit stack.", "stack-2"),
        ("Memoize", "`@functools.cache` on a recursive function = instant top-down DP.", "database"),
        ("Grids", "Direction list `[(0,1),(1,0),(0,-1),(-1,0)]` and a bounds check `0 <= r < R`.", "grid-dots"),
    )
    yield code('''
        from functools import cache

        @cache
        def climb(n):                 # ways to climb n stairs taking 1 or 2 steps
            return 1 if n <= 1 else climb(n - 1) + climb(n - 2)

        print(climb(50))              # 20365011074
    ''')
    yield warn("Plain Python is roughly 10–100× slower than C++ for tight loops. Pick the right algorithm first; then lean on built-ins (`sum`, `sorted`, `set`), which run in C.")


@topic(G, "pythonic", "Pythonic Code & Idioms", "sparkles")
def _():
    yield lead("“Pythonic” code uses the language's features the way they were intended — shorter, clearer and usually faster. Interviewers notice.")
    yield section("Before → after", "arrows-exchange")
    yield table(
        ["Instead of", "Write"],
        ["`for i in range(len(xs)): print(xs[i])`", "`for x in xs: print(x)`"],
        ["`i = 0` … `i += 1` inside a loop", "`for i, x in enumerate(xs)`"],
        ["`if len(xs) == 0:`", "`if not xs:`"],
        ["`if x == True:` / `if x == None:`", "`if x:` / `if x is None:`"],
        ["`tmp = a; a = b; b = tmp`", "`a, b = b, a`"],
        ["`result = []` + loop + `append`", "a list comprehension"],
        ["`d[k] = d[k] + 1 if k in d else 1`", "`d[k] = d.get(k, 0) + 1` or `Counter`"],
        ["`s = ''` + `s += piece` in a loop", "`''.join(pieces)`"],
        ["`open` … `close()`", "`with open(…) as f:`"],
        ["`x > 0 and x < 10`", "`0 < x < 10`"],
    )
    yield section("EAFP vs LBYL", "scale")
    yield cards(
        ("LBYL — Look Before You Leap", "Check first: `if key in d: value = d[key]`. Common in C/Java.", "eye"),
        ("EAFP — Easier to Ask Forgiveness than Permission", "Just try it and handle the failure: `try: value = d[key] except KeyError: …`. Idiomatic Python, and avoids race conditions.", "shield-check"),
    )
    yield section("Idioms worth knowing", "star")
    yield code('''
        nums = [4, 8, 15, 16, 23, 42]

        print(sum(1 for n in nums if n % 2 == 0))         # 4
        print(all(n > 0 for n in nums), any(n > 40 for n in nums))   # True True
        print(max(enumerate(nums), key=lambda p: p[1]))    # (5, 42)

        first, *rest = nums
        print(first, len(rest))                            # 4 5

        pairs = list(zip(nums, nums[1:]))                  # neighbouring pairs
        print(pairs[:2])                                   # [(4, 8), (8, 15)]

        counts = {}
        for word in "to be or not to be".split():
            counts[word] = counts.get(word, 0) + 1
        print(sorted(counts.items(), key=lambda kv: -kv[1])[:2])   # [('to', 2), ('be', 2)]
    ''')
    yield section("Readable over clever", "writing")
    yield dodont(
        "Name things well, keep functions short, return early, and add type hints on public functions.",
        "One-liners that need a comment to explain — clever is the enemy of correct in an interview.",
    )


@topic(G, "python-versions", "What's New: Python 3.8 → 3.14", "news")
def _():
    yield lead("The features added in each recent release — what interviewers mean by “modern Python”, and what you'll see in current codebases.")
    yield note("A new Python 3.x ships every October and gets ~5 years of support. At the time of writing 3.14 is current and 3.9 and older are end-of-life. Check yours with `python3 --version` or `sys.version_info`.", "Release cadence")
    yield section("At a glance", "list-details")
    yield table(
        ["Version", "Headline features"],
        ["**3.8** (2019)", "Walrus `:=`, positional-only params `/`, `f\"{x=}\"`, `functools.cached_property`, `math.prod` / `isqrt`"],
        ["**3.9** (2020)", "Dict merge `|` / `|=`, `str.removeprefix` / `removesuffix`, `list[int]` generics without `typing`, `zoneinfo`"],
        ["**3.10** (2021)", "`match` statement, `X | Y` union types, `zip(strict=True)`, parenthesised `with`, much better error messages"],
        ["**3.11** (2022)", "10–60% faster CPython, `ExceptionGroup` / `except*`, `add_note`, `tomllib`, `asyncio.TaskGroup`, `typing.Self`, error locations with `^^^`"],
        ["**3.12** (2023)", "Type-parameter syntax `def f[T]`, `type` alias statement, f-strings may reuse quotes and nest freely, `itertools.batched`, `@override`"],
        ["**3.13** (2024)", "New colourful REPL, experimental free-threaded build (no GIL) and JIT, `copy.replace`, removed old “dead battery” modules"],
        ["**3.14** (2025)", "Deferred evaluation of annotations, template strings `t\"…\"`, free-threading officially supported, `except A, B` without brackets, `concurrent.interpreters`, `compression.zstd`"],
    )
    yield section("3.8 – 3.9: walrus, `/`, `=` debugging, dict union", "number-8")
    yield code('''
        import re

        # Walrus: assign inside an expression — avoids calling twice
        if (m := re.search(r"\\d+", "order 66 shipped")):
            print(m.group())                         # 66

        # Positional-only (/) and keyword-only (*) parameters
        def clamp(x, /, lo=0, *, hi=10):
            return max(lo, min(x, hi))
        print(clamp(15), clamp(-3, lo=-1))           # 10 -1

        # Self-documenting f-strings
        width = 42
        print(f"{width=}, {width * 2 = }")           # width=42, width * 2 = 84

        # 3.9: dict merge and prefix removal
        defaults, user = {"theme": "light", "size": 12}, {"size": 14}
        print(defaults | user)                       # {'theme': 'light', 'size': 14}
        print("test_login".removeprefix("test_"))    # login
    ''')
    yield section("3.10: `match`, `X | Y`, strict `zip`", "number-10-small")
    yield code('''
        def http_status(code: int | None) -> str:        # union without typing.Union
            match code:
                case 200 | 201:
                    return "ok"
                case 404:
                    return "not found"
                case int(n) if n >= 500:
                    return "server error"
                case None:
                    return "no response"
                case _:
                    return "other"

        print(http_status(201), http_status(503), http_status(None))   # ok server error no response

        try:
            list(zip([1, 2, 3], ["a", "b"], strict=True))              # catch length bugs early
        except ValueError as e:
            print(e)                  # zip() argument 2 is shorter than argument 1
    ''')
    yield section("3.11: speed, exception groups, notes", "number-11-small")
    yield p("3.11 was the first release of the *Faster CPython* project — an adaptive, specialising interpreter that made typical code 10–60% faster with no changes. It also made concurrent failures first-class.")
    yield code('''
        def validate(user):
            errors = []
            if not user.get("name"):
                errors.append(ValueError("name is required"))
            if user.get("age", 0) < 0:
                errors.append(ValueError("age must be >= 0"))
            if errors:
                raise ExceptionGroup("invalid user", errors)

        try:
            validate({"age": -1})
        except* ValueError as eg:                           # handles every ValueError in the group
            print(len(eg.exceptions), eg.exceptions[0])     # 2 name is required

        try:
            int("x")
        except ValueError as e:
            e.add_note("while parsing the 'qty' column")    # extra context in the traceback
            print(e.__notes__)                              # ["while parsing the 'qty' column"]
    ''')
    yield code('''
        import tomllib                                     # read TOML config (stdlib since 3.11)
        cfg = tomllib.loads("""
        [tool.app]
        debug = true
        workers = 4
        """)
        print(cfg["tool"]["app"])                          # {'debug': True, 'workers': 4}
    ''')
    yield section("3.12: generics syntax & f-string freedom", "number-12-small")
    yield code('''
        from itertools import batched

        def first[T](items: list[T]) -> T:          # no TypeVar boilerplate
            return items[0]

        class Stack[T]:
            def __init__(self) -> None:
                self._items: list[T] = []
            def push(self, item: T) -> None:
                self._items.append(item)
            def pop(self) -> T:
                return self._items.pop()

        type Pair[T] = tuple[T, T]                  # lazily evaluated type alias

        s = Stack[int]()
        s.push(first([7, 8]))
        print(s.pop(), Pair.__value__)              # 7 tuple[T, T]

        names = ["asha", "ravi"]
        print(f"{", ".join(names)}")                # asha, ravi   ← same quotes inside, 3.12+
        print(list(batched("abcdefg", 3)))          # [('a', 'b', 'c'), ('d', 'e', 'f'), ('g',)]
    ''')
    yield section("3.13: new REPL, free-threading, JIT", "number-13-small")
    yield cards(
        ("New interactive shell", "Colour, multi-line editing, history browsing, and `exit` / `help` work without parentheses.", "terminal-2"),
        ("Free-threaded build", "An optional `python3.13t` build without the GIL, so threads can run Python code on several cores. Experimental in 3.13.", "arrows-split-2"),
        ("Experimental JIT", "A copy-and-patch JIT compiler, off by default — groundwork for future speed-ups.", "rocket"),
        ("`copy.replace()`", "One function to make a modified copy of dataclasses, named tuples, `datetime`s and more.", "copy"),
    )
    yield code('''
        import copy
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class Point:
            x: int
            y: int

        p = Point(1, 2)
        print(copy.replace(p, y=5))          # Point(x=1, y=5)
    ''')
    yield section("3.14: t-strings, lazy annotations, `except A, B`", "number-14-small")
    yield p("**Template strings** look like f-strings but produce a `Template` object instead of a `str`, so a library can see the static text and the interpolated values separately — the safe way to build SQL, HTML or shell commands.")
    yield code('''
        from string.templatelib import Template, Interpolation

        def safe_html(tpl: Template) -> str:
            out = []
            for part in tpl:                              # static strings and Interpolations, in order
                if isinstance(part, Interpolation):
                    out.append(str(part.value).replace("<", "&lt;").replace(">", "&gt;"))
                else:
                    out.append(part)
            return "".join(out)

        user = "<script>"
        tpl = t"<p>Hello {user}</p>"
        print(type(tpl).__name__, tpl.values)             # Template ('<script>',)
        print(safe_html(tpl))                             # <p>Hello &lt;script&gt;</p>
    ''')
    yield code('''
        # Annotations are evaluated lazily (only when asked for), so forward references just work:
        def make_node() -> Node:          # Node isn't defined yet — fine in 3.14
            return Node()

        class Node:
            pass

        print(type(make_node()).__name__)                 # Node

        # Several exception types without brackets (when there's no "as"):
        try:
            int(None)
        except ValueError, TypeError:
            print("bad input")                            # bad input
    ''')
    yield table(
        ["Also in 3.14", "What it gives you"],
        ["Free-threaded build supported", "`python3.14t` is no longer experimental (still optional; the default build keeps the GIL)"],
        ["`concurrent.interpreters`", "Several isolated interpreters in one process — parallelism without separate processes"],
        ["`compression.zstd`", "Zstandard compression in the standard library"],
        ["`finally` warnings", "`return` / `break` / `continue` inside `finally` now warns — it silently swallows exceptions"],
        ["Better errors", "Suggestions for mistyped keywords (`whille` → `while`?)"],
    )
    yield warn("When a job description or codebase pins an older version, avoid the newer syntax: `match` needs 3.10, `except*` 3.11, `def f[T]` 3.12, t-strings 3.14. Check `requires-python` in `pyproject.toml`.")
    yield qa("Name three features added to Python in the last few versions.",
             "For example: structural pattern matching (`match`, 3.10), exception groups with `except*` and the big interpreter speed-up (3.11), the `def f[T]` generics syntax (3.12), the optional no-GIL free-threaded build (3.13, supported in 3.14), and template strings `t\"…\"` (3.14).")
    yield qa("What is the difference between an f-string and a t-string?",
             "An f-string is evaluated immediately into a `str`. A t-string (3.14) evaluates the expressions but returns a `Template` holding the literal parts and the values separately, so code can escape or transform the values before producing the final string — useful for preventing injection in SQL, HTML and shell commands.")


@topic(G, "interview-questions", "Interview Questions", "message-question")
def _():
    yield lead("The Python questions that come up again and again — with short, precise answers you can say out loud.")
    yield section("Core language", "brand-python")
    yield qa("What is the difference between a list and a tuple?",
             "A list is **mutable** (append, remove, assign by index); a tuple is **immutable**. Tuples are hashable (if their items are), so they can be dict keys or set items, and they're slightly smaller and faster. Use tuples for fixed records and lists for collections that change.")
    yield qa("How is a Python dict implemented, and why are lookups O(1)?",
             "It's a hash table. The key's `hash()` picks a slot; collisions are resolved with open addressing (probing). Average lookup, insert and delete are O(1); the worst case is O(n) with many collisions. Since 3.7 dicts preserve insertion order.")
    yield qa("What is the GIL?",
             "The Global Interpreter Lock in CPython lets only one thread run Python bytecode at a time. Threads still help for **I/O-bound** work (the lock is released while waiting), but for **CPU-bound** work you use `multiprocessing` (separate processes, each with its own GIL) or native extensions.")
    yield qa("`is` vs `==`?",
             "`==` compares **values** (calls `__eq__`); `is` compares **identity** (same object in memory). Use `is` only for singletons such as `None`.")
    yield qa("What happens with a mutable default argument?",
             "Defaults are evaluated once, when the function is defined, so `def f(x, items=[])` shares one list across calls. Use `items=None` and create the list inside the function.")
    yield qa("Shallow copy vs deep copy?",
             "A shallow copy (`xs[:]`, `copy.copy`, `list(xs)`) creates a new container holding **the same** inner objects. A deep copy (`copy.deepcopy`) recursively copies the inner objects too, so nested changes don't leak between them.")
    yield section("Functions & objects", "function")
    yield qa("What are `*args` and `**kwargs`?",
             "`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict. At the call site, `*` and `**` unpack a sequence or mapping into arguments.")
    yield qa("What is a decorator?",
             "A callable that takes a function and returns a new one wrapping it. `@d` above `def f` means `f = d(f)`. Used for logging, timing, caching (`@cache`), access checks and registering routes. Use `functools.wraps` to keep the original name and docstring.")
    yield qa("Generator vs list — when would you use each?",
             "A list stores every item in memory and can be iterated many times. A generator produces items lazily on demand, uses O(1) memory and can be iterated **once**. Use generators for large or infinite streams and pipelines; lists when you need indexing, `len` or repeated passes.")
    yield section("Runtime, memory & concurrency", "cpu")
    yield qa("How does Python manage memory?",
             "Objects live on a private heap. CPython frees an object as soon as its **reference count** drops to zero, and a generational **garbage collector** (`gc`) cleans up reference cycles that refcounting can't.")
    yield qa("What are `@staticmethod` and `@classmethod`?",
             "An instance method receives `self`. A `@classmethod` receives the class (`cls`) — typically used for alternative constructors like `from_json`. A `@staticmethod` receives neither; it's a plain function grouped inside the class.")
    yield qa("Explain the MRO and `super()`.",
             "The Method Resolution Order is the sequence Python searches for attributes in a class hierarchy, computed by C3 linearization (`Class.__mro__`). `super()` delegates to the **next** class in that order, not necessarily the direct parent — enabling cooperative multiple inheritance.")
    yield qa("What does `if __name__ == \"__main__\":` do?",
             "`__name__` is `\"__main__\"` only when the file is run directly. Code under the guard runs for `python file.py` but not when the module is imported — keeping imports free of side effects.")
    yield qa("How do you handle exceptions properly?",
             "Catch specific exceptions, keep `try` blocks small, use `else` for code that should run only on success and `finally` (or `with`) for cleanup. Chain with `raise NewError(...) from e` to keep the cause, and never silence errors with a bare `except:`.")
    yield section("Predict the output", "question-mark")
    yield qa("What is the output? (lists vs tuples with +=)",
             code('''
                 x = [1, 2, 3]
                 y = x
                 y += [4]
                 print(x)          # [1, 2, 3, 4]
                 a = (1, 2)
                 b = a
                 b += (3,)
                 print(a, b)       # (1, 2) (1, 2, 3)
             '''),
             "Lists are mutable, so `+=` extends the shared list in place. Tuples are immutable, so `+=` builds a new tuple and rebinds only `b`.")
    yield qa("What is the output? (lambdas in a loop)",
             code('''
                 funcs = [lambda: i * 10 for i in range(3)]
                 print([f() for f in funcs])     # [20, 20, 20]
             '''),
             "Closures look up `i` when called, after the loop ended with `i == 2`. Capture the current value with a default argument: `lambda i=i: i * 10`.")
    yield section("Quick-fire checklist", "checklist")
    yield chips(
        "Mutable vs immutable", "List vs tuple vs set vs dict", "Hashing & dict keys", "Comprehensions",
        "Generators & `yield`", "Decorators", "Closures & LEGB", "`*args` / `**kwargs`",
        "Shallow vs deep copy", "GIL & concurrency", "MRO & `super()`", "Dunder methods",
        "Exceptions & `with`", "`@dataclass`", "Big-O of built-ins",
        "Descriptors & `property`", "`__new__` vs `__init__`", "Metaclasses", "Iterator protocol",
        "`asyncio` vs threads", "Type hints", "`functools.cache`", "Testing & mocking",
    )
    yield note("Go deeper with *Advanced Interview Questions* and test yourself with *Predict the Output*.", "Next")


@topic(G, "interview-advanced", "Advanced Interview Questions", "message-question")
def _():
    yield lead("The deeper questions asked for mid/senior Python roles — internals, the object model, concurrency and design — with answers you can say in under a minute.")
    yield section("Object model & internals", "cpu-2")
    yield qa("What is the difference between `__new__` and `__init__`?",
             "`__new__` is a static method that **creates** and returns the instance (it receives the class). `__init__` **initialises** the already-created instance and returns `None`. You override `__new__` only for immutable types (subclassing `int`, `str`, `tuple`), singletons or caching instances.")
    yield qa("How does attribute lookup work for `obj.x`?",
             "`type(obj).__getattribute__` runs: first a **data descriptor** (defines `__set__`, e.g. a `property`) found on the class MRO wins; otherwise the instance `__dict__`; otherwise a non-data descriptor or plain class attribute (functions become bound methods here); finally `__getattr__` if defined, else `AttributeError`.")
    yield qa("What is a descriptor? Where does Python use them?",
             "An object on a class that defines `__get__` (and optionally `__set__` / `__delete__`) to control attribute access. `property`, `classmethod`, `staticmethod`, `functools.cached_property`, `__slots__` members and even ordinary methods (functions are descriptors that bind `self`) are all descriptors.")
    yield qa("What is a metaclass? When would you use one?",
             "The class of a class — `type` by default. It controls class *creation* (`__new__` / `__init__` of the metaclass run when a `class` statement executes). Frameworks use them for ORMs and registries, but `__init_subclass__`, class decorators or descriptors solve most of those problems more simply.")
    yield qa("Why can't a list be a dict key, and what makes an object hashable?",
             "Dict lookups rely on a key's hash never changing. A list is mutable, so its hash would change as it changes — Python makes it unhashable. An object is hashable if it has `__hash__` and equal objects hash equally (`a == b` ⇒ `hash(a) == hash(b)`). Defining `__eq__` without `__hash__` sets `__hash__` to `None`.")
    yield qa("What does `__slots__` do and what are the trade-offs?",
             "It replaces the per-instance `__dict__` with fixed slots, saving memory and making attribute access slightly faster. Trade-offs: you can't add new attributes, every class in the hierarchy must declare slots to get the saving, and weak references need `__weakref__` in the slots.")
    yield section("Functions, generators & scope", "function")
    yield qa("How are closures implemented?",
             "Variables captured by an inner function are stored in **cell** objects shared by the outer and inner function. The function's `__closure__` tuple holds these cells, which is why the inner function sees the variable's *current* value when called (late binding).")
    yield qa("How does a generator work under the hood?",
             "Calling a generator function creates a generator object with a suspended frame. Each `next()` resumes the frame until the next `yield`, which returns a value and suspends again, keeping locals and the instruction pointer. When the function returns, `StopIteration` is raised (carrying the return value). `send()` resumes it with a value that becomes the result of the `yield` expression.")
    yield qa("Explain `yield from`.",
             "It delegates to a sub-iterator: every value is yielded straight through, `send()` and `throw()` are forwarded, and the sub-generator's `return` value becomes the value of the `yield from` expression. It was the foundation of generator-based coroutines before `async` / `await`.")
    yield qa("What's the difference between an iterable and an iterator?",
             "An iterable has `__iter__` returning a fresh iterator (lists, dicts, files) and can be looped many times. An iterator has `__next__` (and `__iter__` returning itself), keeps position, and is exhausted after one pass.")
    yield section("Concurrency & performance", "arrows-split-2")
    yield qa("If the GIL exists, why do we still need locks?",
             "The GIL only guarantees that one bytecode instruction runs at a time — it doesn't make *your* operations atomic. `counter += 1` is a load, an add and a store; a thread switch between them loses updates. Locks protect multi-step invariants. (And free-threaded builds have no GIL at all.)")
    yield qa("When would you choose asyncio over threads?",
             "When you have many (hundreds to thousands) concurrent I/O waits — sockets, HTTP calls — and your libraries are async-aware. Tasks are far cheaper than threads and switch only at `await`, so there are fewer race conditions. Threads are simpler for a handful of blocking calls or for libraries without async support; neither helps CPU-bound work — use processes.")
    yield qa("How would you speed up a slow Python program?",
             "Measure first (`cProfile`, `py-spy`). Then: a better algorithm or data structure (set instead of list lookups), push loops into C (built-ins, comprehensions, NumPy), cache repeated work (`functools.cache`), avoid repeated attribute lookups in hot loops, use `multiprocessing` for CPU-bound work and async/threads for I/O, and consider PyPy, Cython or Numba for hot numerical code.")
    yield qa("What is the difference between `deepcopy` and pickling for copying?",
             "`copy.deepcopy` walks the object graph in memory, honours `__deepcopy__` and handles cycles with a memo dict. `pickle` serialises to bytes and back — slower, needs picklable objects, and is really for storage or sending between processes, not copying.")
    yield section("Design & practice", "puzzle")
    yield qa("How do you implement a singleton in Python?",
             "The Pythonic answer: a **module** is already a singleton — put the shared state or instance at module level. Other options: override `__new__` to return a cached instance, a class decorator that caches the instance, or a metaclass. Mention that singletons make testing harder, so dependency injection is often better.")
    yield qa("How do you make a class iterable, comparable and usable with `with`?",
             "Iterable: `__iter__` (often a generator method). Comparable: `__eq__` plus `__lt__` with `@functools.total_ordering`, or `@dataclass(order=True)`. Context manager: `__enter__` / `__exit__`, or a generator with `@contextlib.contextmanager`.")
    yield qa("What are `*` and `/` in a function signature?",
             "Parameters before `/` are positional-only (callers can't name them, so you can rename them freely). Parameters after `*` (or `*args`) are keyword-only, forcing readable calls like `sort(key=…, reverse=True)`.")
    yield qa("How do you manage dependencies and environments for a project?",
             "One virtual environment per project (`python -m venv .venv` or `uv venv`), dependencies declared in `pyproject.toml`, exact versions pinned in a lock file (`uv.lock`, `poetry.lock`, or `pip freeze > requirements.txt`) for reproducible installs, and CI that installs from the lock file.")
    yield section("Code you should be able to write on a whiteboard", "code")
    yield code('''
        from collections import OrderedDict

        class LRUCache:
            """O(1) get/put: OrderedDict remembers recency order."""
            def __init__(self, capacity: int):
                self.capacity = capacity
                self.data = OrderedDict()

            def get(self, key):
                if key not in self.data:
                    return -1
                self.data.move_to_end(key)            # mark as most recently used
                return self.data[key]

            def put(self, key, value):
                self.data[key] = value
                self.data.move_to_end(key)
                if len(self.data) > self.capacity:
                    self.data.popitem(last=False)     # evict least recently used

        c = LRUCache(2)
        c.put("a", 1); c.put("b", 2); c.get("a"); c.put("c", 3)
        print(list(c.data), c.get("b"))               # ['a', 'c'] -1
    ''', caption="Python — LRU cache")
    yield code('''
        import functools, time

        def rate_limited(max_calls, per_seconds, clock=time.monotonic):
            """Allow at most max_calls in any per_seconds window."""
            def decorator(func):
                calls = []
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    now = clock()
                    while calls and now - calls[0] >= per_seconds:
                        calls.pop(0)
                    if len(calls) >= max_calls:
                        raise RuntimeError("rate limit exceeded")
                    calls.append(now)
                    return func(*args, **kwargs)
                return wrapper
            return decorator

        fake_now = [0.0]
        @rate_limited(2, 1.0, clock=lambda: fake_now[0])
        def ping():
            return "pong"

        print(ping(), ping())             # pong pong
        try:
            ping()
        except RuntimeError as e:
            print(e)                      # rate limit exceeded
        fake_now[0] = 1.5                 # time passes
        print(ping())                     # pong
    ''', caption="Python — decorator with state")
    yield code('''
        def flatten(nested):
            """Flatten arbitrarily nested lists/tuples lazily."""
            for item in nested:
                if isinstance(item, (list, tuple)):
                    yield from flatten(item)
                else:
                    yield item

        print(list(flatten([1, [2, (3, [4])], 5])))   # [1, 2, 3, 4, 5]
    ''', caption="Python — recursive generator")


@topic(G, "output-puzzles", "Predict the Output", "question-mark")
def _():
    yield lead("Short snippets interviewers love because the obvious answer is wrong. Predict first, then read the explanation — every output below was produced by running the code.")
    yield note("Each puzzle tests one rule. When you get one wrong, go back to the topic it names — the rule matters more than the trivia.", "How to use this page")
    yield section("Mutability & names", "link")
    yield qa("Default argument shared between calls",
             code('''
                 def append_to(x, target=[]):
                     target.append(x)
                     return target

                 print(append_to(1))        # [1]
                 print(append_to(2))        # [1, 2]
                 print(append_to(3, []))    # [3]
             '''),
             "The default list is created **once** when `def` runs and reused by every call that doesn't pass `target`. → *Functions & Arguments*.")
    yield qa("Multiplying a nested list",
             code('''
                 board = [[" "] * 2] * 2
                 board[0][0] = "X"
                 print(board)               # [['X', ' '], ['X', ' ']]
             '''),
             "`* 2` copies the *reference* to the inner list, so both rows are the same object. Use `[[\" \"] * 2 for _ in range(2)]`. → *Lists & Tuples*.")
    yield qa("Augmented assignment on a tuple item",
             code('''
                 t = ([1], 2)
                 try:
                     t[0] += [3]
                 except TypeError as e:
                     print(type(e).__name__)   # TypeError
                 print(t)                      # ([1, 3], 2)
             '''),
             "`t[0] += [3]` first extends the list in place (succeeds), then tries to store it back into the tuple (fails). The error is raised **after** the mutation. → *Identity, Mutability & Copying*.")
    yield qa("Rebinding vs mutating a parameter",
             code('''
                 def f(xs):
                     xs.append(1)
                     xs = [99]
                     xs.append(2)

                 data = []
                 f(data)
                 print(data)                # [1]
             '''),
             "The first `append` mutates the caller's list. `xs = [99]` rebinds only the local name, so later changes don't reach the caller.")
    yield section("Scope & closures", "brackets-contain")
    yield qa("UnboundLocalError",
             code('''
                 count = 10
                 def bump():
                     try:
                         count += 1
                     except UnboundLocalError:
                         return "unbound"
                 print(bump())              # unbound
             '''),
             "Assigning to `count` anywhere in the function makes it local for the **whole** function, so reading it first fails. Use `global count` (or better, return the new value). → *Scope & Closures*.")
    yield qa("Closures in a loop",
             code('''
                 adders = [lambda x: x + i for i in range(3)]
                 print([f(10) for f in adders])   # [12, 12, 12]
             '''),
             "All lambdas share the same `i`, read when they are called — after the loop left it at 2. Bind it early: `lambda x, i=i: x + i`.")
    yield qa("Class variable vs instance variable",
             code('''
                 class Dog:
                     tricks = []
                     def add(self, t):
                         self.tricks.append(t)

                 a, b = Dog(), Dog()
                 a.add("roll")
                 print(b.tricks)            # ['roll']
             '''),
             "`tricks` lives on the class and is shared by every instance. Create it in `__init__` instead. → *Classes & Objects*.")
    yield section("Operators & values", "math-symbols")
    yield qa("Chained comparisons and precedence",
             code('''
                 print(1 < 2 == 2)          # True
                 print((1 < 2) == 2)        # False
                 print(-2 ** 2)             # -4
                 print(not 1 == 2)          # True
             '''),
             "`1 < 2 == 2` means `1 < 2 and 2 == 2`. `True == 2` is `False` because `True` is `1`. `**` binds tighter than unary minus. `not` has lower precedence than `==`. → *Operators & Precedence*.")
    yield qa("Floats and rounding",
             code('''
                 print(0.1 + 0.2 == 0.3)       # False
                 print(round(0.5), round(1.5), round(2.5))   # 0 2 2
                 print(-7 // 2, -7 % 2)        # -4 1
             '''),
             "Binary floats can't represent 0.1 exactly — compare with `math.isclose`. `round` uses banker's rounding (halves to even). `//` floors toward negative infinity and `%` takes the sign of the divisor. → *Numbers*.")
    yield qa("`and` / `or` return operands",
             code('''
                 print(0 or [] or "x")      # x
                 print(3 and 0 and 5)       # 0
                 print(None or 0)           # 0
             '''),
             "`or` returns the first truthy operand (or the last one); `and` returns the first falsy operand (or the last one). They return objects, not booleans.")
    yield qa("`True` is an `int`",
             code('''
                 d = {1: "int", True: "bool", 1.0: "float"}
                 print(d)                   # {1: 'float'}
                 print(sum([True, True, False]))   # 2
             '''),
             "`1 == True == 1.0` and they hash equally, so they are the **same key**: the first key object is kept and the value is overwritten twice.")
    yield section("Iteration & generators", "repeat")
    yield qa("Exhausted iterators",
             code('''
                 nums = map(lambda n: n * 2, [1, 2, 3])
                 print(list(nums))          # [2, 4, 6]
                 print(list(nums))          # []
                 z = zip("ab", [1, 2])
                 print(dict(z), dict(z))    # {'a': 1, 'b': 2} {}
             '''),
             "`map`, `filter`, `zip` and generators are one-shot iterators. Convert to a list once if you need several passes. → *Iterators & Generators*.")
    yield qa("Modifying a list while iterating",
             code('''
                 nums = [1, 2, 2, 3]
                 for n in nums:
                     if n == 2:
                         nums.remove(n)
                 print(nums)                # [1, 2, 3]
             '''),
             "Removing shifts later items left, so the loop's index skips the second `2`. Build a new list instead: `[n for n in nums if n != 2]`.")
    yield qa("Generator expression evaluation time",
             code('''
                 xs = [1, 2, 3]
                 gen = (x * 10 for x in xs)
                 xs = [7, 8]
                 print(list(gen))           # [10, 20, 30]
             '''),
             "The first `for` source of a generator expression is evaluated **immediately**; everything else is lazy. Rebinding `xs` afterwards doesn't affect it.")
    yield section("Exceptions & finally", "alert-octagon")
    yield qa("`finally` runs even after `return`",
             code('''
                 def f():
                     try:
                         return "try"
                     finally:
                         print("finally")   # finally

                 print(f())                 # try
             '''),
             "`finally` runs on the way out, before the caller receives the return value. (A `return` *inside* `finally` would override it and swallow exceptions — Python 3.14 warns about that.)")
    yield qa("The `else` clause of a loop",
             code('''
                 for n in range(3):
                     if n == 5:
                         break
                 else:
                     print("no break")      # no break
             '''),
             "A loop's `else` runs when the loop ends **without** `break` — think “no-break”, not “otherwise”.")
    yield qa("Which `except` catches it?",
             code('''
                 try:
                     {}["missing"]
                 except LookupError:
                     print("LookupError")   # LookupError
                 except KeyError:
                     print("KeyError")
             '''),
             "`except` clauses are tried top to bottom and match subclasses. `KeyError` is a subclass of `LookupError`, so the first clause wins — put specific exceptions first.")
    yield section("Classes", "box")
    yield qa("MRO in diamond inheritance",
             code('''
                 class A:
                     def who(self): return "A"
                 class B(A):
                     def who(self): return "B" + super().who()
                 class C(A):
                     def who(self): return "C" + super().who()
                 class D(B, C):
                     pass
                 print(D().who())           # BCA
             '''),
             "`super()` follows the MRO `D → B → C → A`, so `B`'s `super()` calls `C`, not `A`. → *Inheritance, MRO & super()*.")
    yield qa("`__eq__` without `__hash__`",
             code('''
                 class P:
                     def __init__(self, x): self.x = x
                     def __eq__(self, o): return self.x == o.x
                 print(P.__hash__)          # None
                 try:
                     {P(1)}
                 except TypeError as e:
                     print(type(e).__name__)   # TypeError
             '''),
             "Defining `__eq__` sets `__hash__` to `None`. Add a `__hash__` based on the same fields (and keep them immutable), or use `@dataclass(frozen=True)`.")
