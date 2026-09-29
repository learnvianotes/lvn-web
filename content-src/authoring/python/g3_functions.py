from kit import *

G = "Functions"


@topic(G, "functions", "Functions & Arguments", "function")
def _():
    yield lead("Functions are first-class objects: you can pass them around, return them, and store them — and Python's argument system is unusually flexible.")
    yield section("Defining & returning", "code")
    yield code('''
        def area(w: float, h: float = 1.0) -> float:
            """Return the area of a w × h rectangle."""
            return w * h

        def min_max(xs):
            return min(xs), max(xs)          # "multiple" return = one tuple

        lo, hi = min_max([4, 1, 9])
        print(area(3, 2), area(5), lo, hi)   # 6 5.0 1 9
        print(area.__doc__)                  # Return the area of a w × h rectangle.
    ''')
    yield note("A function with no `return` (or a bare `return`) returns `None`. Type hints are documentation — Python does not enforce them at runtime.")
    yield section("Kinds of parameters", "adjustments")
    yield table(
        ["Kind", "Syntax", "Call as"],
        ["Positional or keyword", "`def f(a, b)`", "`f(1, 2)` or `f(b=2, a=1)`"],
        ["Default value", "`def f(a, b=10)`", "`f(1)`"],
        ["Variadic positional", "`def f(*args)`", "`f(1, 2, 3)` → `args == (1, 2, 3)`"],
        ["Variadic keyword", "`def f(**kwargs)`", "`f(x=1)` → `kwargs == {'x': 1}`"],
        ["Keyword-only", "`def f(a, *, key)`", "`f(1, key=2)` — `key` must be named"],
        ["Positional-only", "`def f(a, /, b)`", "`f(1, 2)` — `a` can't be named"],
    )
    yield code('''
        def report(title, *items, sep=", ", **meta):
            line = f"{title}: {sep.join(items)}"
            if meta:
                line += f" {meta}"
            return line

        print(report("fruits", "apple", "kiwi"))             # fruits: apple, kiwi
        print(report("ids", "1", "2", sep="|", source="db"))  # ids: 1|2 {'source': 'db'}

        opts = {"sep": "-"}
        print(report("unpacked", *["a", "b"], **opts))       # unpacked: a-b
    ''')
    yield section("The mutable default trap", "alert-triangle")
    yield p("Default values are evaluated **once**, when `def` runs — not on each call. A mutable default is shared by every call.")
    yield code('''
        def add_bad(item, bucket=[]):
            bucket.append(item)
            return bucket

        print(add_bad(1), add_bad(2))     # [1, 2] [1, 2]

        def add_good(item, bucket=None):
            if bucket is None:
                bucket = []
            bucket.append(item)
            return bucket

        print(add_good(1), add_good(2))   # [1] [2]
    ''')
    yield warn("Use `None` as the default for lists, dicts and sets, and create the object inside the function.", "Rule")
    yield section("How arguments are passed", "arrow-right")
    yield define("Pass by object reference", "the function receives a reference to the *same object*. Mutating it is visible to the caller; rebinding the parameter name is not.")
    yield code('''
        def mutate(xs):
            xs.append(99)      # changes the caller's list

        def rebind(xs):
            xs = [0]           # only changes the local name

        data = [1]
        mutate(data); rebind(data)
        print(data)            # [1, 99]
    ''')
    yield section("Recursion", "refresh")
    yield code('''
        import sys

        def fact(n: int) -> int:
            return 1 if n <= 1 else n * fact(n - 1)

        print(fact(10), sys.getrecursionlimit())   # 3628800 1000
    ''')
    yield note("CPython has no tail-call optimisation and a default recursion limit of ~1000 frames. For deep recursion (DFS on 10⁵ nodes) use an explicit stack, or raise the limit with `sys.setrecursionlimit`.")


@topic(G, "scope-closures", "Scope & Closures", "brackets-contain")
def _():
    yield lead("Python resolves names with the LEGB rule, and inner functions can *close over* variables from the function that created them.")
    yield section("LEGB: where a name is looked up", "search")
    yield steps(
        ("Local", "Names assigned inside the current function."),
        ("Enclosing", "Locals of any enclosing (outer) functions."),
        ("Global", "Names at the top level of the module."),
        ("Built-in", "`len`, `print`, `range`, … from the `builtins` module."),
    )
    yield code('''
        x = "global"

        def outer():
            x = "enclosing"
            def inner():
                return x              # found in the enclosing scope
            return inner()

        print(outer(), x)             # enclosing global
    ''')
    yield section("`global` and `nonlocal`", "world")
    yield p("Assigning to a name makes it local to that function. To rebind an outer name, declare it first.")
    yield code('''
        count = 0

        def bump():
            global count
            count += 1

        def make_counter():
            n = 0
            def inc():
                nonlocal n            # rebinding the enclosing variable
                n += 1
                return n
            return inc

        bump(); bump()
        c = make_counter()
        c(); c()
        print(count, c())             # 2 3
    ''')
    yield warn("Without `nonlocal`, `n += 1` inside `inc` raises `UnboundLocalError`: the assignment makes `n` local, so reading it before assigning fails.")
    yield section("Closures", "lock-access")
    yield define("Closure", "a function object that remembers variables from the scope where it was defined, even after that scope has finished running.")
    yield code('''
        def multiplier(k):
            def times(x):
                return x * k          # k is captured
            return times

        double, triple = multiplier(2), multiplier(3)
        print(double(5), triple(5))                       # 10 15
        print(double.__closure__[0].cell_contents)        # 2
    ''')
    yield section("Late binding in loops", "clock")
    yield code('''
        # Every lambda sees the final value of i:
        fns = [lambda: i for i in range(3)]
        print([f() for f in fns])          # [2, 2, 2]

        # A default argument captures each value at definition time:
        fns = [lambda i=i: i for i in range(3)]
        print([f() for f in fns])          # [0, 1, 2]
    ''')
    yield note("Closures capture *variables*, not values. The value is read when the function is **called**.")


@topic(G, "functional", "Lambdas & Functional Tools", "lambda")
def _():
    yield lead("Small anonymous functions plus `map`, `filter`, `sorted(key=…)` and `functools` — Python's functional toolkit.")
    yield section("lambda", "lambda")
    yield p("`lambda args: expression` — a one-expression function with no name, no statements and no annotations. Best as a short `key=` or callback.")
    yield code('''
        add = lambda a, b: a + b
        print(add(2, 3))                                            # 5
        words = ["banana", "Apple", "cherry"]
        print(sorted(words, key=str.lower))                         # ['Apple', 'banana', 'cherry']
        print(sorted(words, key=lambda w: (len(w), w)))             # ['Apple', 'banana', 'cherry']
        print(max(["aa", "b", "cccc"], key=len))                    # cccc
    ''')
    yield section("map, filter, zip", "arrows-right-left")
    yield code('''
        nums = [1, 2, 3, 4]
        print(list(map(lambda x: x * 10, nums)))        # [10, 20, 30, 40]
        print(list(filter(lambda x: x % 2, nums)))      # [1, 3]
        print(list(map(int, "123")))                    # [1, 2, 3]
        print(list(map(pow, [2, 3], [3, 2])))           # [8, 9]
    ''')
    yield note("`map`, `filter` and `zip` return **lazy iterators**. Wrap them in `list()` to see the values — and remember they can be consumed only once.")
    yield section("functools", "tools")
    yield code('''
        from functools import reduce, partial, cache, lru_cache

        print(reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))   # 24

        base2 = partial(int, base=2)
        print(base2("1011"))                                      # 11

        @cache
        def fib(n):
            return n if n < 2 else fib(n - 1) + fib(n - 2)
        print(fib(80))                                            # 23416728348467685

        @lru_cache(maxsize=128)
        def slow_square(x):
            return x * x
        slow_square(4); slow_square(4)
        print(slow_square.cache_info().hits)                      # 1
    ''')
    yield cards(
        ("`@cache` / `@lru_cache`", "Memoize pure functions — the fastest way to turn a recursive solution into top-down DP.", "database"),
        ("`partial`", "Pre-fill some arguments to create a simpler function.", "puzzle"),
        ("`reduce`", "Fold a sequence into one value. Often `sum`, `max`, `math.prod` or a loop is clearer.", "arrows-minimize"),
        ("`operator` module", "`itemgetter(1)`, `attrgetter('age')` — faster, named alternatives to small lambdas.", "settings"),
    )
    yield code('''
        from operator import itemgetter
        rows = [("b", 2), ("a", 3), ("c", 1)]
        print(sorted(rows, key=itemgetter(1)))    # [('c', 1), ('b', 2), ('a', 3)]
    ''')
    yield dodont(
        "Prefer a comprehension over `map`/`filter` with a lambda — `[x * 2 for x in xs]` reads better than `list(map(lambda x: x * 2, xs))`.",
        "Assigning lambdas to names (`f = lambda x: …`) in real code — use `def` so the function has a name in tracebacks.",
    )


@topic(G, "decorators", "Decorators", "sparkles")
def _():
    yield lead("A decorator takes a function and returns a new function that wraps it — adding behaviour like timing, logging, caching or access checks without touching the original code.")
    yield define("`@decorator`", "syntax sugar: `@timer` above `def f` means `f = timer(f)`.")
    yield section("Writing one", "code")
    yield code('''
        import functools

        def shout(func):
            @functools.wraps(func)            # keep func's name and docstring
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result.upper()
            return wrapper

        @shout
        def greet(name):
            """Say hello."""
            return f"hello, {name}"

        print(greet("asha"))                     # HELLO, ASHA
        print(greet.__name__, greet.__doc__)     # greet Say hello.
    ''')
    yield warn("Without `functools.wraps`, the decorated function reports the name `wrapper` and loses its docstring — confusing in debugging and documentation.")
    yield section("Decorators with arguments", "adjustments")
    yield p("Add one more level: a function that takes the arguments and *returns* the decorator.")
    yield code('''
        import functools

        def retry(times):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    for attempt in range(1, times + 1):
                        try:
                            return func(*args, **kwargs)
                        except ValueError:
                            if attempt == times:
                                raise
                return wrapper
            return decorator

        calls = {"n": 0}

        @retry(times=3)
        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("not yet")
            return "ok"

        print(flaky(), calls["n"])   # ok 3
    ''')
    yield section("A timing decorator", "clock")
    yield code('''
        import functools, time

        def timed(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = time.perf_counter() - start
                    wrapper.last_ms = round(elapsed * 1000, 3)
            return wrapper

        @timed
        def work():
            return sum(range(100_000))

        print(work())                            # 4999950000
        print(isinstance(work.last_ms, float))   # True
    ''')
    yield section("Stacking & built-in decorators", "stack")
    yield p("Stacked decorators apply bottom-up: `@a` over `@b` over `def f` means `f = a(b(f))`.")
    yield table(
        ["Decorator", "Purpose"],
        ["`@property`", "Expose a method as a read-only (or validated) attribute"],
        ["`@classmethod` / `@staticmethod`", "Methods that receive the class / nothing instead of `self`"],
        ["`@functools.cache` / `lru_cache`", "Memoization"],
        ["`@dataclasses.dataclass`", "Generate `__init__`, `__repr__`, `__eq__` for a class"],
        ["`@contextlib.contextmanager`", "Turn a generator into a `with`-statement context manager"],
    )
