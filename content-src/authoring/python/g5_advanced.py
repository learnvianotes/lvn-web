from kit import *

G = "Advanced Python"


@topic(G, "iterators-generators", "Iterators & Generators", "repeat")
def _():
    yield lead("Iteration is a protocol: an *iterable* gives you an *iterator*, and an iterator hands out items with `next()` until it raises `StopIteration`. Generators make writing iterators trivial.")
    yield section("The iterator protocol", "arrows-right")
    yield code('''
        nums = [10, 20]
        it = iter(nums)               # calls nums.__iter__()
        print(next(it), next(it))     # 10 20
        try:
            next(it)
        except StopIteration:
            print("exhausted")        # exhausted
    ''')
    yield cards(
        ("Iterable", "Anything with `__iter__` (lists, strings, dicts, files). Can be looped over many times.", "list"),
        ("Iterator", "Has `__next__` and remembers its position. Single-use: once exhausted, it stays empty.", "arrow-right"),
    )
    yield section("Generators with `yield`", "bolt")
    yield p("A function containing `yield` returns a **generator**. Each `next()` runs the body until the next `yield`, then pauses with all local state intact.")
    yield code('''
        def countdown(n):
            while n > 0:
                yield n
                n -= 1

        gen = countdown(3)
        print(next(gen), list(gen))          # 3 [2, 1]

        def fib():
            a, b = 0, 1
            while True:                      # infinite, but lazy
                yield a
                a, b = b, a + b

        from itertools import islice
        print(list(islice(fib(), 10)))       # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    ''')
    yield note("Generators use O(1) memory regardless of how many items they produce — the key to processing huge files or infinite streams.")
    yield section("Pipelines & `yield from`", "git-commit")
    yield code('''
        def read_lines(text):
            yield from text.splitlines()        # delegate to another iterable

        def non_empty(lines):
            return (l.strip() for l in lines if l.strip())

        def numbers(lines):
            for l in lines:
                if l.isdigit():
                    yield int(l)

        data = "10\\n\\n  7 \\nabc\\n3"
        print(sum(numbers(non_empty(read_lines(data)))))   # 20
    ''')
    yield section("itertools essentials", "tools")
    yield code('''
        from itertools import accumulate, chain, combinations, groupby, permutations, product, count

        print(list(accumulate([1, 2, 3, 4])))                 # [1, 3, 6, 10]
        print(list(chain([1, 2], (3,), "ab")))                # [1, 2, 3, 'a', 'b']
        print(list(combinations("abc", 2)))                   # [('a', 'b'), ('a', 'c'), ('b', 'c')]
        print(len(list(permutations(range(4)))))              # 24
        print(list(product([0, 1], repeat=2)))                # [(0, 0), (0, 1), (1, 0), (1, 1)]
        print([(k, len(list(g))) for k, g in groupby("aaabcc")])   # [('a', 3), ('b', 1), ('c', 2)]
        print(next(x for x in count(1) if x * x > 50))        # 8
    ''')
    yield warn("`groupby` only groups **consecutive** equal keys — sort by the same key first if the data isn't already grouped.")


@topic(G, "exceptions", "Exceptions & Context Managers", "alert-octagon")
def _():
    yield lead("Errors are objects that propagate up the call stack until something handles them. `with` guarantees cleanup no matter how a block exits.")
    yield section("try / except / else / finally", "shield")
    yield code('''
        def parse(value):
            try:
                n = int(value)
            except ValueError as e:
                return f"bad input: {e}"
            else:
                return n * 2            # runs only if no exception
            finally:
                pass                    # always runs: close files, release locks

        print(parse("21"))              # 42
        print(parse("x"))               # bad input: invalid literal for int() with base 10: 'x'
    ''')
    yield table(
        ["Block", "Runs when"],
        ["`try`", "Always — the code that might fail"],
        ["`except E`", "An exception of type `E` (or a subclass) was raised"],
        ["`else`", "The `try` block finished **without** an exception"],
        ["`finally`", "Always, even after `return`, `break` or an unhandled error"],
    )
    yield section("Raising & custom exceptions", "flame")
    yield code('''
        class InsufficientFunds(Exception):
            def __init__(self, needed):
                super().__init__(f"need {needed} more")
                self.needed = needed

        def withdraw(balance, amount):
            if amount > balance:
                raise InsufficientFunds(amount - balance)
            return balance - amount

        try:
            withdraw(100, 150)
        except InsufficientFunds as e:
            print(e, e.needed)          # need 50 more 50

        try:
            try:
                {}["k"]
            except KeyError as e:
                raise LookupError("config missing") from e    # keep the original cause
        except LookupError as e:
            print(repr(e.__cause__))    # KeyError('k')
    ''')
    yield dodont(
        "Catch the most specific exception you can handle, keep `try` blocks small, and re-raise with `raise` (no argument) to preserve the traceback.",
        "Bare `except:` or `except Exception: pass` — it hides bugs, and a bare `except` even swallows `KeyboardInterrupt`.",
    )
    yield section("Exception hierarchy (the useful part)", "hierarchy-3")
    yield table(
        ["Exception", "Typical cause"],
        ["`ValueError`", "Right type, wrong value: `int('x')`"],
        ["`TypeError`", "Wrong type: `'a' + 1`"],
        ["`KeyError` / `IndexError`", "Missing dict key / list index out of range (both are `LookupError`s)"],
        ["`AttributeError`", "Object has no such attribute"],
        ["`ZeroDivisionError`", "Division by zero (an `ArithmeticError`)"],
        ["`FileNotFoundError`", "Missing file (an `OSError`)"],
        ["`StopIteration`", "Iterator is exhausted"],
    )
    yield section("Context managers: `with`", "door-exit")
    yield p("`with` calls `__enter__` at the start and `__exit__` at the end — even if the block raises. Files, locks, DB transactions and timers all use it.")
    yield code('''
        from contextlib import contextmanager, suppress

        @contextmanager
        def tag(name):
            print(f"<{name}>")           # setup
            try:
                yield name               # the with-block runs here
            finally:
                print(f"</{name}>")      # teardown, always

        with tag("b") as t:
            print(t.upper())

        with suppress(FileNotFoundError):     # ignore one specific error
            open("definitely-missing.txt")
        print("still running")
    ''', check=False)
    yield shell('''
        <b>
        B
        </b>
        still running
    ''', caption="Output")


@topic(G, "memory-model", "Memory, Mutability & Garbage Collection", "cpu-2")
def _():
    yield lead("Variables are references, objects live on the heap, and CPython frees them with reference counting plus a cycle collector. Mutability explains most “weird” Python bugs.")
    yield section("Names point to objects", "link")
    yield code('''
        a = [1, 2]
        b = a                    # b refers to the SAME list
        b.append(3)
        print(a, a is b)         # [1, 2, 3] True

        x = 5
        y = x
        y += 1                   # ints are immutable: y now points to a new object
        print(x, y)              # 5 6
    ''')
    yield table(
        ["Immutable (can't change in place)", "Mutable (can change in place)"],
        ["`int`, `float`, `bool`, `str`, `bytes`", "`list`, `dict`, `set`, `bytearray`"],
        ["`tuple`, `frozenset`, `None`", "Most user-defined objects"],
    )
    yield note("A tuple is immutable, but if it *contains* a list, that list can still change: `t = ([1],); t[0].append(2)` works.")
    yield section("`+=` differs for mutable and immutable types", "plus")
    yield code('''
        nums = [1]
        alias = nums
        nums += [2]              # list: extends in place
        print(alias)             # [1, 2]

        s = "a"
        alias_s = s
        s += "b"                 # str: builds a new object
        print(alias_s, s)        # a ab
    ''')
    yield section("Reference counting & the cycle collector", "recycle")
    yield steps(
        ("Reference counting", "Every object tracks how many references point to it. When the count hits 0, it is freed immediately."),
        ("Cycle detection", "Objects that reference each other (a ↔ b) never reach 0. The `gc` module periodically finds and frees such unreachable cycles."),
        ("Generations", "New objects are checked often; objects that survive are promoted and checked less — most objects die young."),
    )
    yield code('''
        import sys, gc

        data = []
        # getrefcount's own argument adds a temporary reference:
        print(sys.getrefcount(data) >= 2)   # True

        class Node:
            def __init__(self):
                self.other = None
        a, b = Node(), Node()
        a.other, b.other = b, a             # a reference cycle
        del a, b
        print(gc.collect() >= 2)            # True
    ''')
    yield section("Memory tips", "bulb")
    yield cards(
        ("Generators over lists", "Stream data instead of materialising it: `sum(x for x in …)`.", "bolt"),
        ("`__slots__`", "Drop per-instance `__dict__`s when creating millions of objects.", "database"),
        ("`sys.getsizeof`", "Shallow size of one object in bytes — it doesn't include what it references.", "ruler"),
        ("Interning", "Short identifier-like strings and small ints are reused. Never depend on it; compare with `==`.", "fingerprint"),
    )


@topic(G, "concurrency", "Concurrency: Threads, Processes & asyncio", "arrows-split-2")
def _():
    yield lead("Three tools for doing many things at once. Which one to pick depends on whether your program waits on I/O or burns CPU — because of the GIL.")
    yield define("GIL (Global Interpreter Lock)", "a mutex in CPython that lets only **one thread execute Python bytecode at a time**. Threads still help while waiting on I/O (the GIL is released), but they don't speed up CPU-bound Python code.")
    yield table(
        ["", "`threading`", "`multiprocessing`", "`asyncio`"],
        ["Model", "OS threads, shared memory", "Separate processes, separate memory", "One thread, cooperative tasks"],
        ["Best for", "I/O-bound (network, disk)", "**CPU-bound** (math, image processing)", "Many concurrent I/O waits (thousands of sockets)"],
        ["GIL", "Limits CPU parallelism", "Bypassed — each process has its own", "Not relevant — single thread"],
        ["Cost", "Light; needs locks for shared data", "Heavy start-up; data must be pickled", "Very light; code must be `async`"],
    )
    yield section("Threads for I/O", "arrows-shuffle")
    yield code('''
        from concurrent.futures import ThreadPoolExecutor
        import time

        def fetch(i):
            time.sleep(0.2)              # stands in for a network call (releases the GIL)
            return i * i

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(fetch, range(5)))
        elapsed = time.perf_counter() - start
        print(results, elapsed < 0.5)    # [0, 1, 4, 9, 16] True
    ''')
    yield section("Processes for CPU", "cpu")
    yield code('''
        from concurrent.futures import ProcessPoolExecutor

        def heavy(n):
            return sum(i * i for i in range(n))

        if __name__ == "__main__":       # required: child processes re-import this module
            with ProcessPoolExecutor() as pool:
                print(list(pool.map(heavy, [10**6] * 4)))
    ''', run=False)
    yield section("asyncio for massive I/O concurrency", "bolt")
    yield code('''
        import asyncio

        async def download(name, delay):
            await asyncio.sleep(delay)   # yields control while "waiting"
            return f"{name} done"

        async def main():
            results = await asyncio.gather(download("a", 0.1), download("b", 0.1))
            print(results)               # ['a done', 'b done']

        asyncio.run(main())
    ''')
    yield section("Shared state needs a lock", "lock")
    yield code('''
        import threading

        counter = 0
        lock = threading.Lock()

        def work():
            global counter
            for _ in range(100_000):
                with lock:               # without the lock, updates can be lost
                    counter += 1

        threads = [threading.Thread(target=work) for _ in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        print(counter)                   # 400000
    ''')
    yield note("`counter += 1` is several bytecode steps (load, add, store), so a thread switch in between loses updates. Protect shared mutable state with a `Lock` or use a `queue.Queue`.")
    yield note("Python 3.13+ ships an optional *free-threaded* build (no GIL). It's still experimental — for interviews, explain the GIL as above.", "Recent change")


@topic(G, "modules-packages", "Modules, Packages & Environments", "package")
def _():
    yield lead("A module is a `.py` file; a package is a folder of modules. `import` finds, runs and caches them — and virtual environments keep each project's dependencies separate.")
    yield section("Importing", "download")
    yield code('''
        import math                          # whole module
        from collections import Counter      # one name
        import datetime as dt                # alias
        print(math.sqrt(16), Counter("aab")["a"], dt.date(2026, 1, 1).year)   # 4.0 2 2026
    ''')
    yield steps(
        ("Find", "Python searches `sys.path`: the script's folder, `PYTHONPATH`, the standard library, then `site-packages`."),
        ("Execute once", "The module's top-level code runs the first time it is imported."),
        ("Cache", "The module object is stored in `sys.modules`; later imports reuse it."),
    )
    yield section("`if __name__ == \"__main__\":`", "player-play")
    yield code('''
        # utils.py
        def add(a, b):
            return a + b

        if __name__ == "__main__":    # True only when run directly: python utils.py
            print(add(2, 3))          # 5
    ''')
    yield note("When the file is imported, `__name__` is `\"utils\"`, so the demo code doesn't run. Use this guard for scripts, tests and anything with side effects.")
    yield section("Packages", "folders")
    yield shell('''
        shop/
        ├── __init__.py        # marks a regular package; runs on "import shop"
        ├── cart.py
        └── payments/
            ├── __init__.py
            └── upi.py

        from shop.cart import Cart            # absolute import
        from .cart import Cart                # relative import (inside the package)
    ''', caption="Layout")
    yield section("Virtual environments & pip", "box-multiple")
    yield shell('''
        $ python3 -m venv .venv               # create
        $ source .venv/bin/activate           # activate (Windows: .venv\\Scripts\\activate)
        (.venv) $ pip install requests        # install into this project only
        (.venv) $ pip freeze > requirements.txt
        (.venv) $ pip install -r requirements.txt
        (.venv) $ deactivate
    ''')
    yield cards(
        ("Why venvs", "Each project gets its own package versions — no conflicts, reproducible installs.", "shield"),
        ("`pyproject.toml`", "The modern single file for project metadata and dependencies (used by pip, uv, Poetry).", "file-settings"),
    )


@topic(G, "files-io", "Files, JSON & pathlib", "file-text")
def _():
    yield lead("Reading and writing files safely with `with`, the common formats (text, CSV, JSON), and `pathlib` for paths.")
    yield section("Text files", "file")
    yield code('''
        import os, tempfile
        path = os.path.join(tempfile.mkdtemp(), "notes.txt")

        with open(path, "w", encoding="utf-8") as f:     # "w" truncates, "a" appends
            f.write("line one\\nline two\\n")

        with open(path, encoding="utf-8") as f:           # default mode "r"
            for line in f:                                # streams line by line
                print(line.rstrip())
    ''', check=False)
    yield table(
        ["Mode", "Meaning"],
        ["`'r'`", "Read (default) — error if missing"],
        ["`'w'`", "Write — creates or **truncates**"],
        ["`'a'`", "Append to the end"],
        ["`'x'`", "Create — error if it exists"],
        ["`'b'`", "Binary, e.g. `'rb'` for images"],
        ["`'+'`", "Read and write"],
    )
    yield warn("Always pass `encoding=\"utf-8\"` for text — the platform default differs between Windows and macOS/Linux.")
    yield section("JSON", "braces")
    yield code('''
        import json
        user = {"name": "Asha", "skills": ["python", "sql"], "active": True, "manager": None}
        text = json.dumps(user)
        print(text)                            # {"name": "Asha", "skills": ["python", "sql"], "active": true, "manager": null}
        print(json.loads(text)["skills"][0])   # python
    ''')
    yield note("`dumps`/`loads` work with strings; `dump`/`load` with open files. JSON has no tuples, sets or dates — convert them first.")
    yield section("CSV", "table")
    yield code('''
        import csv, io
        raw = "name,score\\nasha,91\\nravi,84\\n"
        rows = list(csv.DictReader(io.StringIO(raw)))
        print(rows[0])                                       # {'name': 'asha', 'score': '91'}
        print(sum(int(r["score"]) for r in rows) / len(rows))   # 87.5
    ''')
    yield section("pathlib", "folder")
    yield code('''
        from pathlib import Path
        import tempfile

        root = Path(tempfile.mkdtemp())
        report = root / "reports" / "2026.txt"      # "/" joins paths
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("ok", encoding="utf-8")

        print(report.name, report.stem, report.suffix)   # 2026.txt 2026 .txt
        print(report.read_text(encoding="utf-8"))         # ok
        print([p.name for p in root.rglob("*.txt")])      # ['2026.txt']
    ''')
