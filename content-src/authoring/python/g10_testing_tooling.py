from kit import *

G = "Testing & Tooling"


@topic(G, "testing", "Testing: unittest & pytest", "test-pipe")
def _():
    yield lead("Automated tests prove your code works today and keep it working tomorrow. Python ships `unittest` and `doctest`; most projects use `pytest` for its plain `assert`s and fixtures.")
    yield section("Why and what to test", "target-arrow")
    yield cards(
        ("Unit tests", "One function or class in isolation. Fast (milliseconds) — the bulk of your suite.", "cube"),
        ("Integration tests", "Several parts together: your code + a real database, file system or HTTP layer.", "plug-connected"),
        ("End-to-end tests", "The whole system as a user sees it. Slow and brittle — keep few of them.", "world"),
        ("Regression tests", "Every fixed bug gets a test that failed before the fix, so it can't come back.", "bug-off"),
    )
    yield p("A good test follows **Arrange → Act → Assert**: set up inputs, call the code once, check the result.")
    yield section("assert — the building block", "check")
    yield code('''
        def slugify(title: str) -> str:
            return "-".join(title.lower().split())

        # Arrange, Act, Assert — a test is just code that raises if something is wrong
        assert slugify("Hello World") == "hello-world"
        assert slugify("  Python   Notes ") == "python-notes"
        try:
            assert slugify("A B") == "a_b", "separator should be a hyphen"
        except AssertionError as e:
            print("failed:", e)             # failed: separator should be a hyphen
    ''')
    yield warn("`assert` statements are removed when Python runs with `-O`. Use them in tests and for internal sanity checks — never to validate user input in production code.")
    yield section("unittest — the built-in framework", "list-check")
    yield code('''
        import io, unittest

        class Stack:
            def __init__(self):
                self._items = []
            def push(self, x):
                self._items.append(x)
            def pop(self):
                if not self._items:
                    raise IndexError("pop from empty stack")
                return self._items.pop()

        class StackTest(unittest.TestCase):
            def setUp(self):                         # runs before EACH test method
                self.s = Stack()

            def test_push_then_pop(self):
                self.s.push(1)
                self.s.push(2)
                self.assertEqual(self.s.pop(), 2)

            def test_pop_empty_raises(self):
                with self.assertRaises(IndexError):
                    self.s.pop()

            def test_many_values(self):
                for value in [0, "x", None]:
                    with self.subTest(value=value):  # each case reported separately
                        self.s.push(value)
                        self.assertIs(self.s.pop(), value)

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(StackTest)
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        print(result.testsRun, len(result.failures), len(result.errors))   # 3 0 0
        print(result.wasSuccessful())                                        # True
    ''')
    yield table(
        ["Assertion", "Checks"],
        ["`assertEqual(a, b)` / `assertNotEqual`", "`a == b`"],
        ["`assertTrue(x)` / `assertFalse(x)`", "Truthiness"],
        ["`assertIs(a, b)` / `assertIsNone(x)`", "Identity"],
        ["`assertIn(a, b)`", "Membership"],
        ["`assertRaises(E)`", "The block raises `E` (use as a context manager)"],
        ["`assertAlmostEqual(a, b, places=7)`", "Floats close enough"],
        ["`assertCountEqual(a, b)`", "Same items, any order"],
    )
    yield note("`setUp`/`tearDown` run around every test; `setUpClass`/`tearDownClass` once per class. Test methods must start with `test`. Run everything with `python -m unittest discover`.")
    yield section("pytest — less boilerplate", "flask")
    yield code('''
        # test_cart.py
        import pytest
        from shop.cart import Cart

        @pytest.fixture
        def cart():                                   # fresh object for every test that asks for it
            c = Cart()
            c.add("pen", price=10, qty=2)
            return c

        def test_total(cart):
            assert cart.total() == 20                 # plain assert — pytest shows both sides on failure

        @pytest.mark.parametrize("qty, expected", [(1, 10), (3, 30), (0, 0)])
        def test_line_total(qty, expected):
            c = Cart()
            c.add("pen", price=10, qty=qty)
            assert c.total() == expected

        def test_negative_qty_rejected():
            with pytest.raises(ValueError, match="qty"):
                Cart().add("pen", price=10, qty=-1)

        def test_export(cart, tmp_path):              # built-in fixture: a fresh temp directory
            path = tmp_path / "cart.json"
            cart.save(path)
            assert path.exists()
    ''', run=False)
    yield shell('''
        $ pip install pytest
        $ pytest                       # finds test_*.py files and test_* functions
        $ pytest -q -k "total"         # quiet, only tests whose name matches
        $ pytest -x --lf               # stop at first failure; rerun last failures
        $ pytest --cov=shop            # coverage report (pytest-cov plugin)
    ''')
    yield output('''
        ============================= test session starts ==============================
        collected 6 items

        test_cart.py ......                                                      [100%]

        ============================== 6 passed in 0.02s ===============================
    ''', caption="pytest output")
    yield table(
        ["", "`unittest`", "`pytest`"],
        ["Install", "Built in", "`pip install pytest`"],
        ["Style", "Classes + `self.assertX` methods", "Plain functions + `assert`"],
        ["Setup", "`setUp` / `tearDown`", "Fixtures, injected by name, with scopes"],
        ["Parametrise", "`subTest`", "`@pytest.mark.parametrize`"],
        ["Runs the other's tests?", "No", "Yes — pytest runs unittest suites too"],
    )
    yield section("doctest — examples that are tests", "file-text")
    yield code('''
        import doctest, io

        def median(xs):
            """Return the median of a non-empty list.

            >>> median([3, 1, 2])
            2
            >>> median([4, 1, 3, 2])
            2.5
            """
            s = sorted(xs)
            mid = len(s) // 2
            return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

        runner = doctest.DocTestRunner()
        for test in doctest.DocTestFinder().find(median, globs={"median": median}):
            runner.run(test, out=io.StringIO().write)
        print(runner.tries, runner.failures)       # 2 0
    ''')
    yield shell('''
        $ python -m doctest -v stats.py     # run every docstring example in a module
        $ pytest --doctest-modules          # or let pytest collect them
    ''')
    yield section("Coverage & the TDD loop", "refresh")
    yield steps(
        ("Red", "Write a small failing test for the next bit of behaviour."),
        ("Green", "Write the simplest code that makes it pass."),
        ("Refactor", "Clean up with the tests as a safety net; rerun them."),
    )
    yield note("Coverage (`coverage run -m pytest && coverage report`) shows which lines never ran. High coverage doesn't prove correctness, but **uncovered code is definitely untested**.")
    yield dodont(
        "Keep tests fast, independent and deterministic; one behaviour per test; descriptive names like `test_pop_empty_raises`.",
        "Tests that depend on each other's order, the current time, the network or random data without a fixed seed.",
    )
    yield qa("What is a fixture in pytest?",
             "A function decorated with `@pytest.fixture` that prepares something a test needs (an object, a temp directory, a DB connection). Tests receive it by naming it as a parameter. Fixtures can `yield` to run teardown and have scopes (`function`, `module`, `session`).")
    yield qa("unittest or pytest?",
             "pytest for most projects: less boilerplate, better failure output, fixtures and a large plugin ecosystem — and it runs existing unittest tests. unittest when you can't add dependencies.")
    yield qa("How do you test code that raises an exception?",
             "`with pytest.raises(ValueError, match=\"...\"):` or `with self.assertRaises(ValueError):` around the call. The test fails if the exception is *not* raised.")


@topic(G, "mocking", "Mocking & Test Doubles", "masks-theater")
def _():
    yield lead("A test double stands in for a slow, flaky or external dependency — an API, the clock, the database — so a unit test checks only *your* code. `unittest.mock` is the standard toolkit.")
    yield section("Kinds of test doubles", "category")
    yield table(
        ["Double", "What it does", "Example"],
        ["Stub", "Returns canned answers", "`get_rate()` always returns `83.0`"],
        ["Mock", "Records calls so you can assert on them", "“`send_email` was called once with this address”"],
        ["Fake", "A working lightweight implementation", "An in-memory dict instead of a real database"],
        ["Spy", "Wraps the real object and records calls", "`Mock(wraps=real_func)`"],
    )
    yield section("Mock basics", "masks-theater")
    yield code('''
        from unittest.mock import Mock

        api = Mock()
        api.get_user.return_value = {"id": 7, "name": "Asha"}   # stub a method

        print(api.get_user(7)["name"])                    # Asha
        print(api.get_user.call_count)                    # 1
        print(api.get_user.call_args)                     # call(7)
        api.get_user.assert_called_once_with(7)           # passes silently

        print(type(api.anything.you.like).__name__)       # Mock   ← attributes are created on demand
    ''')
    yield section("side_effect: exceptions and sequences", "arrows-shuffle")
    yield code('''
        from unittest.mock import Mock

        def fetch_with_retry(client, attempts=3):
            for i in range(attempts):
                try:
                    return client.fetch()
                except ConnectionError:
                    if i == attempts - 1:
                        raise

        client = Mock()
        client.fetch.side_effect = [ConnectionError(), ConnectionError(), "data"]   # fail, fail, succeed
        print(fetch_with_retry(client), client.fetch.call_count)   # data 3

        client.fetch.side_effect = ConnectionError("down")          # always fail
        try:
            fetch_with_retry(client)
        except ConnectionError as e:
            print("gave up:", e)                                     # gave up: down

        double = Mock(side_effect=lambda x: x * 2)                   # compute the return value
        print(double(21))                                            # 42
    ''')
    yield section("patch: replace a name during a test", "replace")
    yield p("`patch` swaps an attribute for a mock and restores it afterwards. Patch **where the name is looked up**, not where it was defined: if `app.py` does `from time import time`, patch `app.time`, not `time.time`.")
    yield code('''
        import time
        from unittest.mock import patch

        class Greeter:
            def greeting(self):
                hour = time.localtime().tm_hour
                return "Good morning" if hour < 12 else "Good afternoon"

        fake = time.struct_time((2026, 9, 29, 9, 0, 0, 1, 272, 0))
        with patch.object(time, "localtime", return_value=fake):      # context-manager form
            print(Greeter().greeting())                                # Good morning

        @patch.object(Greeter, "greeting", return_value="Hi")          # decorator form
        def check(mock_greeting):
            result = Greeter().greeting()
            mock_greeting.assert_called_once()
            return result

        print(check())                                                 # Hi
        print(time.localtime is not None)                              # True   ← original restored
    ''')
    yield code('''
        import os
        from unittest.mock import patch, mock_open

        with patch.dict(os.environ, {"FEATURE_X": "on"}):     # temporary environment
            print(os.environ["FEATURE_X"])                    # on
        print("FEATURE_X" in os.environ)                      # False

        with patch("builtins.open", mock_open(read_data="line1\\nline2")):
            with open("any/path.txt") as f:                   # no real file touched
                print(f.read().splitlines())                  # ['line1', 'line2']
    ''')
    yield section("spec & autospec: mocks that fail like the real thing", "shield-check")
    yield code('''
        from unittest.mock import create_autospec

        class PaymentGateway:
            def charge(self, amount: int, currency: str) -> str:
                raise NotImplementedError

        gateway = create_autospec(PaymentGateway, instance=True)
        gateway.charge.return_value = "txn-1"
        print(gateway.charge(500, "INR"))                     # txn-1

        try:
            gateway.charge(500)                               # wrong signature → error, like the real method
        except TypeError:
            print("signature checked")                        # signature checked
        try:
            gateway.refund(1)                                 # no such method on the real class
        except AttributeError:
            print("unknown method rejected")                  # unknown method rejected
    ''')
    yield warn("A plain `Mock()` accepts any call and any attribute, so a typo like `mock.assert_caled_once()` or a renamed method can make a broken test pass. Use `spec=`/`autospec` (and Python rejects `assert_*` typos since 3.12).")
    yield section("pytest's monkeypatch", "flask")
    yield code('''
        def test_uses_api_key(monkeypatch):
            monkeypatch.setenv("API_KEY", "test-key")
            monkeypatch.setattr("shop.payments.charge", lambda amount: "ok")
            assert checkout(100) == "ok"          # undone automatically after the test
    ''', run=False)
    yield dodont(
        "Mock at the boundaries: network, time, randomness, file system, third-party services.",
        "Mocking your own internal functions everywhere — tests then mirror the implementation and break on every refactor while missing real bugs.",
    )
    yield qa("Why do you patch where an object is used, not where it's defined?",
             "`from module import name` copies the reference into the importing module's namespace. Patching the original module doesn't change that copy, so the code under test still calls the real function. Patch `consumer_module.name`.")
    yield qa("Mock vs MagicMock?",
             "`MagicMock` is a `Mock` that also pre-configures magic methods (`__len__`, `__iter__`, `__enter__`, …), so it can stand in for containers or context managers. `patch` uses `MagicMock` by default.")
    yield qa("What is `side_effect` used for?",
             "To make a mock raise an exception, return successive values from an iterable, or compute its result with a function — for testing error handling and retries.")


@topic(G, "debugging-profiling", "Debugging & Profiling", "bug")
def _():
    yield lead("Debugging finds *why* code is wrong; profiling finds *where* it is slow or hungry. Both start with reading carefully and measuring, not guessing.")
    yield section("Reading a traceback", "file-alert")
    yield output('''
        Traceback (most recent call last):
          File "report.py", line 12, in <module>
            print(average(scores))
                  ~~~~~~~^^^^^^^^
          File "report.py", line 4, in average
            return sum(xs) / len(xs)
                   ~~~~~~~~^~~~~~~~~
        ZeroDivisionError: division by zero
    ''', caption="Traceback")
    yield steps(
        ("Read the last line first", "The exception type and message: *what* went wrong."),
        ("Walk up the stack", "Frames are listed oldest → newest; the last frame is where it was raised."),
        ("Find your code", "Skip library frames; the lowest frame in *your* file is usually the place to fix."),
        ("Use the markers", "Since 3.11 `~~~^^^` points at the exact sub-expression that failed."),
    )
    yield section("print, logging and assertions", "message-dots")
    yield code('''
        items = [3, 5]
        total = sum(items)
        print(f"{items=} {total=}")          # items=[3, 5] total=8   ← the "=" specifier labels values
        print(f"{total / len(items)=:.2f}")  # total / len(items)=4.00
    ''')
    yield section("pdb — the built-in debugger", "player-pause")
    yield p("Put `breakpoint()` where you want to stop (3.7+). The program pauses there with an interactive `(Pdb)` prompt; you can inspect variables, step line by line and continue.")
    yield code('''
        def apply_discount(price, pct):
            breakpoint()              # execution pauses here
            return price - price * pct / 100
    ''', run=False)
    yield shell('''
        > shop.py(3)apply_discount()
        -> return price - price * pct / 100
        (Pdb) p price, pct
        (200, 15)
        (Pdb) n
        --Return--
        (Pdb) c
    ''', caption="pdb session")
    yield table(
        ["Command", "Does"],
        ["`p expr` / `pp expr`", "Print / pretty-print an expression"],
        ["`n` (next)", "Run the current line, stepping *over* calls"],
        ["`s` (step)", "Step *into* a function call"],
        ["`c` (continue)", "Run until the next breakpoint"],
        ["`r` (return)", "Run until the current function returns"],
        ["`l` / `ll`", "List source around the current line / the whole function"],
        ["`w` (where)", "Show the call stack"],
        ["`u` / `d`", "Move up / down the stack to inspect callers"],
        ["`b file:line` / `b func`", "Set a breakpoint"],
        ["`q`", "Quit"],
    )
    yield shell('''
        $ python -m pdb script.py                 # start under the debugger
        $ python -m pdb -c continue script.py     # run; drop into pdb post-mortem on a crash
        $ PYTHONBREAKPOINT=0 python script.py     # disable every breakpoint() call
    ''')
    yield note("IDE debuggers (VS Code, PyCharm) do the same with clicks: breakpoints, conditional breakpoints, watch expressions. `faulthandler` (`python -X faulthandler`) dumps tracebacks even on hard crashes and hangs.")
    yield section("timeit — micro-benchmarks", "clock")
    yield code('''
        import timeit

        setup = "data = list(range(10_000)); s = set(data)"
        list_time = timeit.timeit("9_999 in data", setup=setup, number=1_000)
        set_time = timeit.timeit("9_999 in s", setup=setup, number=1_000)
        print(set_time < list_time)          # True   ← O(1) hash lookup beats an O(n) scan
    ''')
    yield shell('''
        $ python -m timeit -s "xs = list(range(1000))" "sum(xs)"
        20000 loops, best of 5: 11.2 usec per loop
    ''')
    yield section("cProfile — where does the time go?", "chart-bar")
    yield code('''
        import cProfile, pstats, io

        def slow_square(n):
            return sum(i * i for i in range(n))

        def work():
            return [slow_square(20_000) for _ in range(20)]

        profiler = cProfile.Profile()
        profiler.enable()
        work()
        profiler.disable()

        out = io.StringIO()
        stats = pstats.Stats(profiler, stream=out).sort_stats("cumulative")
        stats.print_stats(5)
        print("slow_square" in out.getvalue())     # True
    ''')
    yield output('''
                 400063 function calls in 0.041 seconds

           Ordered by: cumulative time

           ncalls  tottime  percall  cumtime  percall filename:lineno(function)
                1    0.000    0.000    0.041    0.041 app.py:6(work)
               20    0.000    0.000    0.041    0.002 app.py:3(slow_square)
               20    0.019    0.001    0.041    0.002 {built-in method builtins.sum}
           400020    0.022    0.000    0.022    0.000 app.py:4(<genexpr>)
    ''', caption="Typical report (timings vary)")
    yield table(
        ["Column", "Meaning"],
        ["`ncalls`", "How many times the function was called"],
        ["`tottime`", "Time spent in the function itself, excluding sub-calls"],
        ["`cumtime`", "Time including everything it called — sort by this to find hot paths"],
    )
    yield shell('''
        $ python -m cProfile -s cumtime app.py      # profile a whole script
        $ python -m cProfile -o out.prof app.py && snakeviz out.prof   # visualise
    ''')
    yield section("tracemalloc — where does the memory go?", "database")
    yield code('''
        import tracemalloc

        tracemalloc.start()
        big = [str(i) * 10 for i in range(50_000)]
        current, peak = tracemalloc.get_traced_memory()
        top = tracemalloc.take_snapshot().statistics("lineno")[0]
        tracemalloc.stop()
        print(peak > 1_000_000, top.size > 1_000_000)   # True True
    ''')
    yield table(
        ["Tool", "Kind", "Good for"],
        ["`cProfile`", "Deterministic, built in", "Which functions take the time"],
        ["`py-spy`", "Sampling, attaches to a running process", "Production processes, no code changes"],
        ["`line_profiler`", "Line by line", "The slow line inside a known-slow function"],
        ["`scalene`", "CPU + memory + GPU sampling", "An all-in-one view"],
        ["`memray` / `tracemalloc`", "Memory allocations", "Leaks and peak usage"],
    )
    yield qa("How would you find why a Python program is slow?",
             "Reproduce with a realistic input, profile with `cProfile` (or `py-spy` on a live process), sort by cumulative time, then zoom in with `line_profiler` or `timeit`. Fix the biggest hotspot — usually an algorithm or data-structure issue — and measure again.")
    yield qa("What does `breakpoint()` do?",
             "It calls `sys.breakpointhook()`, which starts `pdb` at that line by default. The `PYTHONBREAKPOINT` environment variable can switch to another debugger or disable it (`=0`).")


@topic(G, "performance", "Performance Tips", "rocket")
def _():
    yield lead("Fast Python comes from choosing the right algorithm and data structure, then letting C-implemented built-ins do the looping. Measure before and after every change.")
    yield note("“Premature optimisation is the root of all evil.” Write clear code first, profile (*Debugging & Profiling*), then optimise the hotspot the profiler shows you.", "Rule zero")
    yield section("1. Algorithms and data structures first", "binary-tree")
    yield code('''
        emails = [f"user{i}@x.com" for i in range(5_000)]
        blocked = [f"user{i}@x.com" for i in range(0, 5_000, 7)]

        # O(n·m): "in list" scans the whole list every time
        slow = [e for e in emails if e not in blocked]

        # O(n + m): build a set once, then O(1) lookups
        blocked_set = set(blocked)
        fast = [e for e in emails if e not in blocked_set]

        print(slow == fast, len(fast))       # True 4285
    ''')
    yield table(
        ["Instead of", "Use", "Why"],
        ["`x in list` inside a loop", "`x in set` / `dict`", "O(n) → O(1)"],
        ["`list.pop(0)` / `insert(0, x)`", "`collections.deque`", "O(n) → O(1) at both ends"],
        ["Repeated `min()` of a changing list", "`heapq`", "O(n) → O(log n)"],
        ["Linear search in sorted data", "`bisect`", "O(n) → O(log n)"],
        ["Recomputing the same results", "`functools.cache`", "Exponential → linear for DP-style recursion"],
        ["Counting with a manual dict", "`collections.Counter`", "Written in C, clearer"],
    )
    yield section("2. Let built-ins do the looping", "bolt")
    yield code('''
        nums = list(range(1, 100_001))

        total = 0
        for n in nums:                        # interpreted, one bytecode loop per item
            total += n * n

        fast_total = sum(n * n for n in nums)   # sum() runs in C
        print(total == fast_total)              # True

        words = ["b", "a", "c"] * 3
        print("".join(sorted(set(words))))      # abc   ← set, sorted, join: all C
        print(max(nums), any(n > 99_999 for n in nums))   # 100000 True
    ''')
    yield cards(
        ("Comprehensions", "Faster than `for` + `append` — the loop runs with less bytecode overhead.", "filter"),
        ("`str.join`", "Build strings from a list of parts; `+=` in a loop can copy repeatedly.", "link"),
        ("`map` with built-ins", "`list(map(int, parts))` avoids a Python-level lambda call per item.", "arrows-right"),
        ("Batch operations", "`list.extend`, `dict.update`, `set.update` instead of item-by-item loops.", "stack-2"),
    )
    yield section("3. Reduce work inside hot loops", "flame")
    yield code('''
        import math

        def distances_slow(points):
            result = []
            for x, y in points:
                result.append(math.sqrt(x * x + y * y))    # attribute lookups every iteration
            return result

        def distances_fast(points):
            hypot = math.hypot                               # hoist the lookup into a local
            return [hypot(x, y) for x, y in points]          # comprehension + a specialised C function

        pts = [(3, 4), (6, 8), (5, 12)]
        print(distances_slow(pts) == distances_fast(pts), distances_fast(pts))   # True [5.0, 10.0, 13.0]
    ''')
    yield ul(
        "Local variables are faster than globals and attribute lookups (`self.x`, `module.func`) — hoist them out of tight loops.",
        "Move invariant work (compiling a regex, building a set) outside the loop.",
        "Avoid exceptions for normal control flow inside very hot loops — but `try` itself is free when nothing is raised (3.11+).",
        "Use generators to stream large data instead of building huge lists: less memory means fewer cache misses and GC pauses.",
    )
    yield section("4. Memory: slots, generators, arrays", "database")
    yield code('''
        import sys
        from array import array

        class PointDict:
            def __init__(self, x, y):
                self.x, self.y = x, y

        class PointSlots:
            __slots__ = ("x", "y")
            def __init__(self, x, y):
                self.x, self.y = x, y

        a, b = PointDict(1, 2), PointSlots(1, 2)
        print(hasattr(a, "__dict__"), hasattr(b, "__dict__"))   # True False

        as_list = list(range(100_000))
        as_array = array("i", range(100_000))                    # packed 4-byte C ints
        print(sys.getsizeof(as_array) < sys.getsizeof(as_list))  # True
    ''')
    yield section("5. Cache and precompute", "archive")
    yield code('''
        from functools import cache

        @cache
        def ways(n):                  # count paths — exponential without the cache
            return 1 if n < 2 else ways(n - 1) + ways(n - 2)

        print(ways(200))              # 453973694165307953197296969697410619233826
        print(ways.cache_info().hits > 0)   # True
    ''')
    yield section("6. When pure Python isn't enough", "rocket")
    yield table(
        ["Tool", "How it helps", "Best for"],
        ["NumPy / pandas", "Vectorised operations run in C over whole arrays", "Numeric and tabular data"],
        ["`multiprocessing` / `ProcessPoolExecutor`", "Use every CPU core", "CPU-bound, parallelisable work"],
        ["`asyncio` / threads", "Overlap waiting time", "I/O-bound work"],
        ["PyPy", "A JIT-compiled Python implementation", "Long-running pure-Python code"],
        ["Cython / mypyc", "Compile (typed) Python to C extensions", "Hot inner loops in libraries"],
        ["Numba", "JIT-compile numeric functions with a decorator", "Loops over NumPy arrays"],
        ["Rust / C extensions (PyO3)", "Write the hot core natively", "Maximum speed, bigger effort"],
    )
    yield note("Upgrading Python is the cheapest optimisation: 3.11 was 10–60% faster than 3.10, and later releases continue the work (an experimental JIT arrived in 3.13).", "Free speed")
    yield dodont(
        "Profile, fix the top hotspot, re-measure, and keep a benchmark or test that proves the result is still correct.",
        "Micro-optimising code that runs once, or sacrificing readability for a 2% gain the profiler never pointed at.",
    )
    yield qa("Why is a list comprehension usually faster than a for loop with append?",
             "The comprehension is compiled into a specialised loop that appends via a dedicated bytecode instead of looking up and calling the `append` method on each iteration, so there's less interpreter overhead per item.")
    yield qa("How do you speed up CPU-bound Python code?",
             "Better algorithm first; then vectorise with NumPy or move hot loops into C (built-ins, Cython, Numba); then parallelise across cores with `multiprocessing`, since threads don't run Python bytecode in parallel under the GIL.")


@topic(G, "code-quality", "PEP 8, Linters & Formatters", "checklist")
def _():
    yield lead("Consistent style makes code easier to read and review. PEP 8 defines the conventions; formatters and linters apply and enforce them automatically so humans can review logic instead of whitespace.")
    yield section("PEP 8 essentials", "writing")
    yield table(
        ["Topic", "Convention"],
        ["Indentation", "4 spaces, never tabs"],
        ["Line length", "79 in PEP 8; most teams use 88 (Black/Ruff) or 100"],
        ["Functions, variables, modules", "`snake_case`"],
        ["Classes, exceptions, type variables", "`PascalCase` (`HttpError`, `UserProfile`)"],
        ["Constants", "`UPPER_SNAKE_CASE` at module level"],
        ["Internal names", "`_leading_underscore`"],
        ["Blank lines", "2 around top-level functions/classes, 1 between methods"],
        ["Imports", "One per line, at the top: standard library → third-party → local, each group separated"],
        ["Whitespace", "`x = f(a, b)`, `items[1:2]`, no spaces inside brackets, `def f(x=1)` without spaces around `=`"],
        ["Comparisons", "`is None`, `if not items:`, `isinstance(x, int)` instead of `type(x) == int`"],
    )
    yield code('''
        import os                                  # 1. standard library
        from collections import Counter

        # import requests                          # 2. third-party
        # from .models import User                 # 3. local package

        MAX_RETRIES = 3


        class RetryPolicy:
            """Decide whether a failed request should be retried."""

            def __init__(self, max_retries: int = MAX_RETRIES) -> None:
                self.max_retries = max_retries

            def should_retry(self, attempt: int, status: int) -> bool:
                return attempt < self.max_retries and status >= 500


        policy = RetryPolicy()
        print(policy.should_retry(1, 503), policy.should_retry(3, 503))   # True False
    ''')
    yield section("Docstrings (PEP 257)", "file-description")
    yield code('''
        def transfer(src: str, dst: str, amount: float) -> str:
            """Move money between two accounts.

            Args:
                src: Account id to debit.
                dst: Account id to credit.
                amount: Positive amount in rupees.

            Returns:
                The transaction id.

            Raises:
                ValueError: If amount is not positive.
            """
            if amount <= 0:
                raise ValueError("amount must be positive")
            return f"txn:{src}->{dst}:{amount}"

        print(transfer.__doc__.splitlines()[0])      # Move money between two accounts.
        print(transfer("a1", "b2", 50))              # txn:a1->b2:50
    ''')
    yield note("A one-line summary in the imperative mood, a blank line, then details. Google style (above) and NumPy style are both common — pick one per project. Tools like Sphinx and mkdocstrings turn them into documentation.")
    yield section("The tools", "tools")
    yield table(
        ["Tool", "Role", "Notes"],
        ["**Ruff**", "Linter + formatter", "Written in Rust, very fast; replaces Flake8, isort, pyupgrade and most plugins"],
        ["**Black**", "Formatter", "“Uncompromising” — one style, no debates; Ruff's formatter is compatible"],
        ["isort", "Import sorter", "Built into Ruff (`I` rules)"],
        ["Flake8 / Pylint", "Linters", "Older; Pylint is slower but checks more design issues"],
        ["**mypy** / pyright", "Type checkers", "Catch type errors statically — see *Type Hints & mypy*"],
        ["**pre-commit**", "Git hook runner", "Runs the tools on every commit"],
        ["Bandit", "Security linter", "Flags `eval`, `shell=True`, weak hashes…"],
    )
    yield shell('''
        $ pip install ruff
        $ ruff check .              # lint
        $ ruff check . --fix        # auto-fix what's safe (unused imports, sorting…)
        $ ruff format .             # format (Black-compatible)
    ''')
    yield output('''
        app.py:1:8: F401 [*] `os` imported but unused
        app.py:14:5: E722 Do not use bare `except`
        app.py:20:15: B006 Do not use mutable data structures for argument defaults
        Found 3 errors.
        [*] 1 fixable with the `--fix` option.
    ''', caption="ruff check output")
    yield section("Configuration in pyproject.toml", "file-settings")
    yield shell('''
        [tool.ruff]
        line-length = 88
        target-version = "py312"

        [tool.ruff.lint]
        select = ["E", "F", "I", "B", "UP", "SIM"]   # pycodestyle, pyflakes, isort, bugbear, pyupgrade, simplify

        [tool.mypy]
        strict = true
    ''', caption="pyproject.toml")
    yield shell('''
        # .pre-commit-config.yaml
        repos:
          - repo: https://github.com/astral-sh/ruff-pre-commit
            rev: v0.6.9
            hooks:
              - id: ruff
                args: [--fix]
              - id: ruff-format

        $ pip install pre-commit && pre-commit install   # now runs on every git commit
    ''', caption="pre-commit")
    yield section("The Zen of Python", "yin-yang")
    yield code('''
        import codecs, contextlib, io

        with contextlib.redirect_stdout(io.StringIO()):
            import this                           # "import this" prints the poem on first import
        zen = codecs.decode(this.s, "rot13").splitlines()
        print(zen[2])                             # Beautiful is better than ugly.
        print(zen[3])                             # Explicit is better than implicit.
        print(zen[8])                             # Readability counts.
    ''')
    yield section("Code-review checklist", "list-check")
    yield ul(
        "Names say what things are; no single letters except loop indices and math.",
        "Functions do one thing, are short, and return early instead of nesting deeply.",
        "No bare `except:`, no mutable default arguments, no unused imports or variables.",
        "Public functions have type hints and a docstring.",
        "Resources are opened with `with`; no secrets in code or logs.",
        "New behaviour has tests; the formatter, linter and type checker pass in CI.",
    )
    yield qa("What is PEP 8?",
             "The official style guide for Python code: naming, indentation, line length, whitespace, imports and comments. Its goal is readability and consistency; it explicitly says consistency within a project matters more than following it to the letter.")
    yield qa("Linter vs formatter?",
             "A formatter rewrites layout (spacing, line breaks, quotes) without changing meaning — Black, `ruff format`. A linter analyses code for likely bugs and style violations (unused imports, bare except, mutable defaults) and reports or fixes them — Ruff, Flake8, Pylint.")
