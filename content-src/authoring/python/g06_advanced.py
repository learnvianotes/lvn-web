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


@topic(G, "generators-advanced", "Generators: send, yield from & Coroutines", "bolt")
def _():
    yield lead("Generators are more than lazy lists: they can receive values, be told to stop, return a result and delegate to each other — the machinery that `async`/`await` grew out of.")
    yield section("Iterator class vs generator", "code")
    yield p("Both objects below behave identically in a `for` loop. The generator version gets `__iter__`, `__next__` and `StopIteration` for free.")
    yield code('''
        class Countdown:                       # hand-written iterator
            def __init__(self, start):
                self.n = start
            def __iter__(self):
                return self
            def __next__(self):
                if self.n <= 0:
                    raise StopIteration
                self.n -= 1
                return self.n + 1

        def countdown(start):                  # the same thing as a generator
            while start > 0:
                yield start
                start -= 1

        print(list(Countdown(3)), list(countdown(3)))   # [3, 2, 1] [3, 2, 1]
    ''')
    yield section("Generator states", "traffic-lights")
    yield code('''
        from inspect import getgeneratorstate

        def gen():
            yield 1
            yield 2

        g = gen()
        print(getgeneratorstate(g))      # GEN_CREATED
        next(g)
        print(getgeneratorstate(g))      # GEN_SUSPENDED
        list(g)
        print(getgeneratorstate(g))      # GEN_CLOSED
    ''')
    yield table(
        ["State", "Meaning"],
        ["`GEN_CREATED`", "Created, body hasn't started — the first `next()` runs up to the first `yield`"],
        ["`GEN_RUNNING`", "Currently executing (only visible from inside)"],
        ["`GEN_SUSPENDED`", "Paused at a `yield`, locals preserved"],
        ["`GEN_CLOSED`", "Finished, closed, or raised — further `next()` raises `StopIteration`"],
    )
    yield section("`send()`: values flow *into* the generator", "send")
    yield p("`x = yield value` hands `value` out and pauses; when resumed with `g.send(v)`, the `yield` expression evaluates to `v`. `next(g)` is the same as `g.send(None)`. The first call must be `next()` (or `send(None)`) to *prime* the generator.")
    yield code('''
        def running_average():
            total, count, avg = 0, 0, None
            while True:
                value = yield avg           # hand out avg, wait for the next value
                total += value
                count += 1
                avg = total / count

        avg = running_average()
        next(avg)                           # prime: run to the first yield
        print(avg.send(10))                 # 10.0
        print(avg.send(20))                 # 15.0
        print(avg.send(60))                 # 30.0
    ''')
    yield section("`throw()`, `close()` and `GeneratorExit`", "hand-stop")
    yield code('''
        def worker():
            try:
                while True:
                    try:
                        job = yield
                        print("did", job)
                    except ValueError as e:
                        print("recovered from", e)      # the error is raised AT the paused yield
            finally:
                print("cleanup")                         # runs on close() — GeneratorExit

        w = worker()
        next(w)
        w.send("a")                                      # did a
        w.throw(ValueError("bad job"))                   # recovered from bad job
        w.close()                                        # cleanup
    ''', check=False)
    yield output('''
        did a
        recovered from bad job
        cleanup
    ''')
    yield warn("Never swallow `GeneratorExit` and keep yielding — `close()` then raises `RuntimeError: generator ignored GeneratorExit`. Do cleanup in `finally` and let it propagate.")
    yield section("Return values & `yield from`", "arrow-forward")
    yield p("A generator's `return x` becomes `StopIteration(x).value`. `yield from sub` re-yields everything `sub` produces, forwards `send`/`throw` to it, and evaluates to its return value.")
    yield code('''
        def read_block(lines):
            count = 0
            for line in lines:
                if line == "END":
                    return count                 # becomes the value of "yield from"
                yield line.upper()
                count += 1

        def document(lines):
            it = iter(lines)
            n1 = yield from read_block(it)
            n2 = yield from read_block(it)
            yield f"blocks had {n1} and {n2} lines"

        print(list(document(["a", "b", "END", "c", "END"])))
        # ['A', 'B', 'C', 'blocks had 2 and 1 lines']
    ''', check=False)
    yield output("['A', 'B', 'C', 'blocks had 2 and 1 lines']")
    yield code('''
        def tree(node):                          # recursive delegation: walk a nested structure
            name, children = node
            yield name
            for child in children:
                yield from tree(child)

        t = ("root", [("a", [("a1", [])]), ("b", [])])
        print(list(tree(t)))                     # ['root', 'a', 'a1', 'b']
    ''')
    yield section("Pipelines", "git-commit")
    yield code('''
        def parse(lines):
            for line in lines:
                name, amount = line.split(",")
                yield name, float(amount)

        def only_large(rows, limit):
            return ((n, a) for n, a in rows if a >= limit)

        def total(rows):
            return sum(a for _, a in rows)

        log = ["tea,40", "laptop,55000", "phone,18000", "pen,10"]
        print(total(only_large(parse(log), 1000)))    # 73000.0
    ''')
    yield note("Each stage pulls one item at a time from the previous one, so the whole pipeline runs in constant memory — whether the input is 4 lines or a 40 GB log file.")
    yield section("From generators to `async`/`await`", "bolt")
    yield steps(
        ("2001 — generators (PEP 255)", "`yield` makes pausable functions."),
        ("2005 — `send`/`throw`/`close` (PEP 342)", "Generators become coroutines that can receive values."),
        ("2012 — `yield from` (PEP 380)", "Delegation lets coroutines call sub-coroutines; asyncio was first built on it."),
        ("2015 — `async def` / `await` (PEP 492)", "Native coroutine syntax, separate from generators, with the same suspend/resume idea."),
    )
    yield warn("A generator can be consumed **once**. Passing the same generator to two functions gives the second one nothing — materialise it with `list()` or use `itertools.tee`.", "One-shot")
    yield qa("What does `send()` do, and why must you call `next()` first?",
             "`send(v)` resumes a paused generator and makes the pending `yield` expression evaluate to `v`. A freshly created generator isn't paused at a `yield` yet, so the first resume must be `next(g)` (or `send(None)`) — sending a non-`None` value raises `TypeError`.")
    yield qa("How do you get a generator's return value?",
             "With `yield from` (the expression's value), or by catching `StopIteration` and reading `.value`. A plain `for` loop discards it.")
    yield qa("Generator vs coroutine in modern Python?",
             "A generator (`def` + `yield`) produces a stream of values. A native coroutine (`async def`) is awaited and scheduled by an event loop; it can't be iterated with `for`. Both suspend and resume a frame, but they are different types with different protocols.")


@topic(G, "itertools-module", "itertools Deep Dive", "tools")
def _():
    yield lead("`itertools` is a toolkit of fast, memory-efficient iterator building blocks written in C. Combine them to express loops as pipelines.")
    yield section("Infinite iterators", "infinity")
    yield code('''
        from itertools import count, cycle, repeat, islice

        print(list(islice(count(10, 5), 4)))          # [10, 15, 20, 25]
        print(list(islice(cycle("AB"), 5)))           # ['A', 'B', 'A', 'B', 'A']
        print(list(repeat("x", 3)))                   # ['x', 'x', 'x']
        print(list(map(pow, [2, 3, 4], repeat(2))))   # [4, 9, 16]
    ''')
    yield warn("`count()` and `cycle()` never stop — always bound them with `islice`, `zip`, `takewhile` or a `break`.")
    yield section("Slicing & filtering", "filter")
    yield code('''
        from itertools import islice, takewhile, dropwhile, filterfalse, compress

        nums = [1, 4, 6, 3, 8, 2]
        print(list(islice(nums, 1, 5, 2)))                  # [4, 3]
        print(list(takewhile(lambda n: n < 5, nums)))       # [1, 4]
        print(list(dropwhile(lambda n: n < 5, nums)))       # [6, 3, 8, 2]
        print(list(filterfalse(lambda n: n % 2, nums)))     # [4, 6, 8, 2]
        print(list(compress("abcdef", [1, 0, 1, 0, 0, 1]))) # ['a', 'c', 'f']
    ''')
    yield section("Combining & reshaping", "arrows-join")
    yield code('''
        from itertools import chain, zip_longest, pairwise, batched, starmap, accumulate
        import operator

        print(list(chain.from_iterable([[1, 2], [3], []])))       # [1, 2, 3]
        print(list(zip_longest("abc", [1], fillvalue=0)))          # [('a', 1), ('b', 0), ('c', 0)]
        print(list(pairwise([1, 4, 9, 16])))                       # [(1, 4), (4, 9), (9, 16)]
        print(list(batched(range(7), 3)))                          # [(0, 1, 2), (3, 4, 5), (6,)]
        print(list(starmap(operator.mul, [(2, 3), (4, 5)])))       # [6, 20]
        print(list(accumulate([3, 1, 4, 1, 5], max)))              # [3, 3, 4, 4, 5]
        print(list(accumulate([1, 2, 3], initial=100)))            # [100, 101, 103, 106]
    ''')
    yield table(
        ["Function", "Since", "Use it for"],
        ["`chain.from_iterable(xss)`", "—", "Flatten one level lazily"],
        ["`zip_longest(a, b, fillvalue=…)`", "—", "Zip without truncating to the shortest"],
        ["`pairwise(it)`", "3.10", "Consecutive pairs — differences, gaps, edges of a path"],
        ["`batched(it, n)`", "3.12", "Fixed-size chunks (`strict=True` in 3.13 demands full batches)"],
        ["`accumulate(it, func)`", "—", "Running totals / max / products (prefix sums)"],
        ["`starmap(f, pairs)`", "—", "`f(*args)` for each tuple of args"],
        ["`tee(it, n)`", "—", "Split one iterator into `n` independent ones (buffers items)"],
    )
    yield section("Combinatorics", "atom-2")
    yield code('''
        from itertools import product, permutations, combinations, combinations_with_replacement
        from math import comb, perm

        print(list(product("ab", repeat=2)))               # [('a', 'a'), ('a', 'b'), ('b', 'a'), ('b', 'b')]
        print(list(permutations("abc", 2)))                # [('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]
        print(list(combinations([1, 2, 3], 2)))            # [(1, 2), (1, 3), (2, 3)]
        print(list(combinations_with_replacement("ab", 2)))  # [('a', 'a'), ('a', 'b'), ('b', 'b')]
        print(len(list(permutations(range(5), 3))), perm(5, 3), comb(5, 3))   # 60 60 10
    ''')
    yield table(
        ["Function", "Order matters?", "Repeats?", "Count for n items, size r"],
        ["`product(xs, repeat=r)`", "Yes", "Yes", "nʳ"],
        ["`permutations(xs, r)`", "Yes", "No", "n! / (n−r)!"],
        ["`combinations(xs, r)`", "No", "No", "n! / (r!(n−r)!)"],
        ["`combinations_with_replacement(xs, r)`", "No", "Yes", "(n+r−1)! / (r!(n−1)!)"],
    )
    yield section("groupby — done right", "category")
    yield code('''
        from itertools import groupby
        from operator import itemgetter

        sales = [("fruit", "apple"), ("veg", "kale"), ("fruit", "kiwi"), ("veg", "leek")]
        print([k for k, _ in groupby(sales, key=itemgetter(0))])   # ['fruit', 'veg', 'fruit', 'veg']

        sales.sort(key=itemgetter(0))                               # sort by the SAME key first
        grouped = {k: [name for _, name in g] for k, g in groupby(sales, key=itemgetter(0))}
        print(grouped)                                              # {'fruit': ['apple', 'kiwi'], 'veg': ['kale', 'leek']}

        # Run-length encoding: the classic groupby interview question
        print("".join(f"{ch}{len(list(g))}" for ch, g in groupby("aaabccdd")))   # a3b1c2d2
    ''')
    yield warn("Each group is an iterator tied to the parent `groupby`. Advancing to the next group invalidates the previous one — consume (e.g. `list(g)`) before moving on.")
    yield section("Recipes", "chef-hat")
    yield code('''
        from itertools import islice, chain, cycle
        from collections import deque

        def sliding_window(it, n):
            it = iter(it)
            window = deque(islice(it, n - 1), maxlen=n)
            for x in it:
                window.append(x)
                yield tuple(window)

        def unique_everseen(it):
            seen = set()
            for x in it:
                if x not in seen:
                    seen.add(x)
                    yield x

        def roundrobin(*its):
            iterators = cycle(iter(i) for i in its)
            pending = len(its)
            while pending:
                try:
                    yield next(next(iterators))
                except StopIteration:
                    pending -= 1
                    iterators = cycle(list(islice(iterators, pending)))

        print(list(sliding_window([1, 2, 3, 4, 5], 3)))   # [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
        print(list(unique_everseen("abracadabra")))       # ['a', 'b', 'r', 'c', 'd']
        print(list(roundrobin("ABC", "D", "EF")))         # ['A', 'D', 'E', 'B', 'F', 'C']
    ''')
    yield note("The official docs end with an *Itertools Recipes* section; the third-party `more-itertools` package ships all of them (and many more) ready to import.")
    yield qa("How would you generate all subsets of a list?",
             "`chain.from_iterable(combinations(xs, r) for r in range(len(xs) + 1))` — 2ⁿ subsets, produced lazily. Alternatively, loop a bitmask from `0` to `2**n - 1`.")
    yield qa("Why does `groupby` return the same key more than once?",
             "It only groups **consecutive** items with equal keys, like the Unix `uniq` command. Sort by the same key first, or use a `defaultdict(list)` if order doesn't matter.")
    yield qa("What is the benefit of itertools over writing loops?",
             "They are implemented in C and lazy: less memory (items are produced on demand), often faster, composable into pipelines, and they express intent (`pairwise`, `batched`) instead of index arithmetic.")


@topic(G, "context-managers", "Context Managers & contextlib", "door-exit")
def _():
    yield lead("A context manager pairs setup with guaranteed teardown. `with` runs the teardown however the block exits — normally, by `return`, or by an exception.")
    yield section("The protocol", "plug-connected")
    yield code('''
        class Resource:
            def __init__(self, name):
                self.name = name
            def __enter__(self):
                print(f"open {self.name}")
                return self                          # bound to the "as" target
            def __exit__(self, exc_type, exc, tb):
                print(f"close {self.name} (error: {exc_type.__name__ if exc_type else None})")
                return False                         # False/None → let the exception propagate

        with Resource("db") as r:
            print("using", r.name)

        try:
            with Resource("file"):
                raise KeyError("boom")
        except KeyError:
            print("caught outside")
    ''', check=False)
    yield output('''
        open db
        using db
        close db (error: None)
        open file
        close file (error: KeyError)
        caught outside
    ''')
    yield steps(
        ("Evaluate", "The expression after `with` produces the manager."),
        ("Enter", "`__enter__()` runs; its return value is bound to the `as` name."),
        ("Body", "The indented block runs."),
        ("Exit", "`__exit__(exc_type, exc, tb)` always runs — all three are `None` if there was no exception."),
        ("Suppress?", "If `__exit__` returns a truthy value, the exception is swallowed. Almost always return `False`."),
    )
    yield section("A reusable class-based manager", "clock")
    yield code('''
        import time

        class Timer:
            def __enter__(self):
                self.start = time.perf_counter()
                return self
            def __exit__(self, *exc):
                self.elapsed = time.perf_counter() - self.start
                return False

        with Timer() as t:
            sum(range(100_000))
        print(t.elapsed > 0)          # True
    ''')
    yield section("`@contextmanager`: a generator becomes a manager", "wand")
    yield p("Everything before `yield` is `__enter__`, the yielded value is the `as` target, everything after is `__exit__`. Wrap the `yield` in `try`/`finally` or the cleanup is skipped when the body raises.")
    yield code('''
        from contextlib import contextmanager

        @contextmanager
        def temporary_setting(config, key, value):
            old = config[key]
            config[key] = value
            try:
                yield config
            finally:
                config[key] = old             # restored even if the body raises

        cfg = {"debug": False}
        with temporary_setting(cfg, "debug", True):
            print(cfg["debug"])               # True
        print(cfg["debug"])                   # False
    ''')
    yield section("contextlib helpers", "tools")
    yield code('''
        import io
        from contextlib import suppress, redirect_stdout, nullcontext, closing

        with suppress(KeyError):                  # ignore one specific exception
            {}["missing"]

        buf = io.StringIO()
        with redirect_stdout(buf):                # capture print output
            print("hidden")
        print(buf.getvalue().strip())             # hidden

        def process(lock=None):
            with lock or nullcontext():           # "maybe a lock" without an if/else
                return "processed"
        print(process())                          # processed

        class Conn:
            def close(self):
                self.closed = True
        with closing(Conn()) as c:                # calls c.close() on exit
            pass
        print(c.closed)                           # True
    ''')
    yield table(
        ["Helper", "Purpose"],
        ["`suppress(*excs)`", "Ignore the listed exceptions inside the block"],
        ["`redirect_stdout(f)` / `redirect_stderr(f)`", "Temporarily send prints somewhere else"],
        ["`closing(obj)`", "Call `obj.close()` on exit, for objects without `__exit__`"],
        ["`nullcontext(value)`", "A do-nothing manager — for optional context"],
        ["`ExitStack()`", "Enter a *dynamic* number of managers; unwinds them in reverse"],
        ["`chdir(path)`", "Temporarily change the working directory (3.11+)"],
        ["`ContextDecorator`", "A manager that can also be used as `@decorator`"],
        ["`asynccontextmanager`", "The `async with` version of `@contextmanager`"],
    )
    yield section("ExitStack: many resources at once", "stack-2")
    yield code('''
        import tempfile
        from pathlib import Path
        from contextlib import ExitStack

        folder = Path(tempfile.mkdtemp())
        names = ["a.txt", "b.txt", "c.txt"]
        with ExitStack() as stack:
            files = [stack.enter_context(open(folder / n, "w", encoding="utf-8")) for n in names]
            for i, f in enumerate(files):
                f.write(str(i))
        # every file is closed here, even if one open() had failed half-way
        print(all(f.closed for f in files), (folder / "c.txt").read_text())   # True 2
    ''')
    yield section("Several managers in one `with`", "brackets")
    yield code('''
        import io

        src, dst = io.StringIO("copy me"), io.StringIO()
        with (
            src as reader,          # parenthesised form (3.10+) allows one per line
            dst as writer,
        ):
            writer.write(reader.read())
            copied = writer.getvalue()
        print(copied, src.closed, dst.closed)   # copy me True True
    ''')
    yield section("Async context managers", "bolt")
    yield code('''
        import asyncio
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def session(name):
            await asyncio.sleep(0)          # e.g. open a network connection
            try:
                yield f"session:{name}"
            finally:
                await asyncio.sleep(0)      # e.g. close it

        async def main():
            async with session("api") as s:
                return s

        print(asyncio.run(main()))          # session:api
    ''')
    yield dodont(
        "Use `with` for anything that must be released: files, locks, DB transactions, network connections, temporary state.",
        "Returning `True` from `__exit__` \"just in case\" — it silently swallows every exception raised in the block.",
    )
    yield qa("What happens if an exception occurs inside a `with` block?",
             "`__exit__` is called with the exception type, value and traceback. If it returns a falsy value the exception continues propagating after cleanup; if it returns `True` the exception is suppressed and execution continues after the `with`.")
    yield qa("How do you write a context manager without a class?",
             "Decorate a generator with `contextlib.contextmanager`: setup, `yield` the resource inside `try`, clean up in `finally`.")
    yield qa("When would you use ExitStack?",
             "When the number of resources is only known at runtime (open N files), or when you need to conditionally enter managers or register arbitrary cleanup callbacks with `stack.callback(func)`.")


@topic(G, "type-hints", "Type Hints & mypy", "tag")
def _():
    yield lead("Type hints describe what a function expects and returns. Python ignores them at runtime; static checkers (mypy, pyright) and IDEs use them to catch bugs before the code runs.")
    yield define("Gradual typing", "you can add hints a little at a time. Unannotated code is treated as `Any` (anything goes), so a codebase can move from untyped to fully typed one module at a time.")
    yield section("Annotation basics", "code")
    yield code('''
        def greet(name: str, times: int = 1) -> str:
            return ", ".join([f"hi {name}"] * times)

        count: int = 0
        scores: dict[str, list[float]] = {"asha": [9.5, 8.0]}
        point: tuple[int, int] = (3, 4)
        ids: tuple[int, ...] = (1, 2, 3)      # variable-length tuple

        print(greet("ravi", 2))               # hi ravi, hi ravi
        print(greet.__annotations__)          # {'name': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
        print(greet(42))                      # hi 42   ← runs fine: hints are NOT enforced at runtime
    ''')
    yield section("The vocabulary", "list-details")
    yield table(
        ["Hint", "Meaning"],
        ["`list[int]`, `dict[str, int]`, `set[str]`", "Built-in generics (3.9+) — no `typing.List` needed"],
        ["`int | None` / `Optional[int]`", "May be `None` (the `|` form is 3.10+)"],
        ["`int | str` / `Union[int, str]`", "One of several types"],
        ["`Any`", "Opt out of checking for this value"],
        ["`object`", "Any value, but you may only use what every object supports — safer than `Any`"],
        ["`Callable[[int, str], bool]`", "A function taking `(int, str)` and returning `bool`"],
        ["`Iterable[T]`, `Sequence[T]`, `Mapping[K, V]`", "Accept the *abstract* type (from `collections.abc`) in parameters"],
        ["`Literal[\"r\", \"w\"]`", "Only these exact values"],
        ["`Final`", "Must not be reassigned"],
        ["`ClassVar[int]`", "A class-level attribute, not an instance field"],
        ["`Self`", "The type of the current class — for fluent methods (3.11+)"],
        ["`Never` / `NoReturn`", "Function never returns normally (always raises)"],
    )
    yield code('''
        from collections.abc import Iterable, Callable
        from typing import Literal

        def total(xs: Iterable[float]) -> float:              # accepts list, tuple, generator…
            return sum(xs)

        def apply(f: Callable[[int], int], x: int) -> int:
            return f(x)

        def open_mode(mode: Literal["r", "w"]) -> str:
            return f"mode={mode}"

        print(total([1.5, 2.5]), total(x / 2 for x in range(3)))   # 4.0 1.5
        print(apply(lambda n: n * n, 7), open_mode("w"))           # 49 mode=w
    ''')
    yield note("Be liberal in what you accept, specific in what you return: take `Iterable[str]` or `Mapping[str, int]` as parameters, return concrete `list[str]` / `dict[str, int]`.")
    yield section("Structured data: TypedDict, NamedTuple, Protocol", "braces")
    yield code('''
        from typing import TypedDict, NotRequired, NamedTuple, Protocol

        class Movie(TypedDict):
            title: str
            year: int
            rating: NotRequired[float]      # key may be absent

        class Point(NamedTuple):
            x: float
            y: float

        class SupportsClose(Protocol):      # structural: anything with close() matches
            def close(self) -> None: ...

        def shutdown(things: list[SupportsClose]) -> int:
            for t in things:
                t.close()
            return len(things)

        class Socket:
            def close(self) -> None:
                pass

        m: Movie = {"title": "Dune", "year": 2021}
        print(m["title"], Point(1, 2).x, shutdown([Socket(), Socket()]))   # Dune 1 2
    ''')
    yield section("Generics: TypeVar and the 3.12 syntax", "brackets-angle")
    yield code('''
        from typing import TypeVar

        T = TypeVar("T")                          # pre-3.12 style
        def first_old(xs: list[T]) -> T:
            return xs[0]

        def first[T](xs: list[T]) -> T:           # 3.12+ style: same meaning
            return xs[0]

        def largest[N: (int, float)](a: N, b: N) -> N:   # constrained type parameter
            return a if a > b else b

        class Box[T]:
            def __init__(self, item: T) -> None:
                self.item = item
            def get(self) -> T:
                return self.item

        type Matrix = list[list[float]]           # type alias statement (3.12+)

        print(first_old(["a"]), first([1, 2]), largest(2.5, 1.0), Box("x").get())   # a 1 2.5 x
        print(Matrix.__value__)                    # list[list[float]]
    ''')
    yield section("Overloads, `Self`, `cast` and `TYPE_CHECKING`", "adjustments")
    yield code('''
        from typing import overload, Self, cast, TYPE_CHECKING

        if TYPE_CHECKING:                   # only True for the type checker — avoids import cycles
            from decimal import Decimal

        @overload
        def parse(x: str) -> int: ...
        @overload
        def parse(x: bytes) -> str: ...
        def parse(x):                       # the one real implementation
            return int(x) if isinstance(x, str) else x.decode()

        class Query:
            def __init__(self) -> None:
                self.parts: list[str] = []
            def where(self, cond: str) -> Self:   # subclasses get their own type back
                self.parts.append(cond)
                return self

        def to_money(x: object) -> "Decimal":
            return cast("Decimal", x)       # tells the checker "trust me" — no runtime effect

        print(parse("42"), parse(b"hi"), Query().where("a").where("b").parts)   # 42 hi ['a', 'b']
    ''')
    yield section("Running a type checker", "shield-check")
    yield shell('''
        $ pip install mypy
        $ mypy app.py                     # or: pyright app.py
        $ mypy --strict src/              # require annotations everywhere
    ''')
    yield code('''
        # app.py
        def average(xs: list[float]) -> float:
            return sum(xs) / len(xs)

        average(["1", "2"])            # a bug mypy finds without running anything
    ''', run=False)
    yield output('''
        app.py:5: error: List item 0 has incompatible type "str"; expected "float"  [list-item]
        app.py:5: error: List item 1 has incompatible type "str"; expected "float"  [list-item]
        Found 2 errors in 1 file (checked 1 source file)
    ''', caption="mypy output")
    yield section("Annotations at runtime", "clock")
    yield code('''
        import typing

        def make() -> Widget:          # Widget doesn't exist yet
            return Widget()

        class Widget:
            size: int = 3

        print(typing.get_type_hints(make))            # {'return': <class '__main__.Widget'>}
        print(typing.get_type_hints(Widget))          # {'size': <class 'int'>}
    ''')
    yield note("Since **3.14** annotations are evaluated lazily (PEP 649), so forward references like `-> Widget` work without quotes or `from __future__ import annotations`. On 3.13 and older, write `-> \"Widget\"` or add the `__future__` import.", "Version")
    yield cards(
        ("Runtime validation", "Hints aren't enforced. Libraries like **pydantic** and **beartype** read them to validate data at runtime.", "shield"),
        ("Stubs", "`.pyi` files give types to untyped libraries; many live in `types-*` packages (`pip install types-requests`).", "file-code"),
        ("`py.typed`", "An empty marker file that tells checkers your package ships inline types.", "package"),
        ("Gradual rollout", "Start with public function signatures, run mypy in CI, then tighten with `--strict` module by module.", "stairs-up"),
    )
    yield warn("`list[int]` as a parameter type is *invariant*: a `list[bool]` is not accepted even though `bool` is a subclass of `int`, because the function could append a plain `int`. Accept `Sequence[int]` (read-only, covariant) instead.")
    yield qa("Does Python enforce type hints?",
             "No. The interpreter stores them in `__annotations__` and otherwise ignores them. Static checkers (mypy, pyright), IDEs and runtime libraries such as pydantic are what give them teeth.")
    yield qa("`Optional[int]` vs a default of `None`?",
             "`Optional[int]` (or `int | None`) says the *value* may be `None`. It does not make the parameter optional — that's what a default value does. `def f(x: int | None)` still requires an argument.")
    yield qa("What is a Protocol and how does it differ from an ABC?",
             "A `Protocol` describes required methods and is matched **structurally** — any class with those methods qualifies, without inheriting. An ABC is **nominal**: a class must inherit from it (or be registered). Protocols suit duck typing; ABCs suit shared implementation and runtime `isinstance` checks.")


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
