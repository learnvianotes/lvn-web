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
    yield note("Argument kinds (`/`, `*`, `*args`, `**kwargs`) and recursion each have their own topic next — this one covers the essentials.", "Next")


@topic(G, "arguments", "Argument Kinds: *args, **kwargs, / and *", "adjustments")
def _():
    yield lead("A Python signature can say exactly how each parameter may be passed — by position, by name, or either — and can soak up any number of extras with `*args` and `**kwargs`.")
    yield section("The full signature, in order", "list-numbers")
    yield formula("`def f(pos_only, /, pos_or_kw, *args, kw_only, **kwargs)`")
    yield table(
        ["Part", "Syntax", "How callers pass it"],
        ["Positional-only", "before `/`", "Only by position: `f(1)` — `f(a=1)` is an error"],
        ["Positional-or-keyword", "between `/` and `*`", "Either: `f(1)` or `f(b=1)` — the default kind"],
        ["Variadic positional", "`*args`", "Extra positional values, collected into a **tuple**"],
        ["Keyword-only", "after `*` or `*args`", "Only by name: `f(key=1)`"],
        ["Variadic keyword", "`**kwargs`", "Extra named values, collected into a **dict** (must be last)"],
    )
    yield code('''
        def f(a, b=1, /, c=2, *args, d, e=5, **kwargs):
            return f"a={a} b={b} c={c} args={args} d={d} e={e} kwargs={kwargs}"

        print(f(10, d=4))
        # a=10 b=1 c=2 args=() d=4 e=5 kwargs={}
        print(f(10, 20, 30, 40, 50, d=4, z=9))
        # a=10 b=20 c=30 args=(40, 50) d=4 e=5 kwargs={'z': 9}
    ''', check=False)
    yield output('''
        a=10 b=1 c=2 args=() d=4 e=5 kwargs={}
        a=10 b=20 c=30 args=(40, 50) d=4 e=5 kwargs={'z': 9}
    ''')
    yield note("Once a parameter has a default, every later *positional* parameter needs one too. Keyword-only parameters are exempt — `d` above has no default even though `c` does.")
    yield section("Keyword-only parameters (`*`)", "key")
    yield p("A bare `*` ends the positional parameters. Everything after it must be named at the call site — ideal for flags and options that would be unreadable as bare `True`/`False`.")
    yield code('''
        def connect(host, port, *, timeout=10, retries=3):
            return f"{host}:{port} t={timeout} r={retries}"

        print(connect("db", 5432, timeout=2))     # db:5432 t=2 r=3
        try:
            connect("db", 5432, 2)                # which option is 2? Python refuses to guess
        except TypeError as e:
            print(e)   # connect() takes 2 positional arguments but 3 were given
    ''')
    yield dodont(
        "`sort(items, reverse=True)` — boolean and option parameters keyword-only, so call sites explain themselves.",
        "`process(data, True, False, 3)` — nobody can read that without opening the definition.",
    )
    yield section("Positional-only parameters (`/`, 3.8+)", "lock")
    yield p("Parameters before `/` can't be passed by name. Many built-ins work this way (`len(obj=…)` is an error). It lets a library rename parameters later without breaking callers, and frees the name for `**kwargs`.")
    yield code('''
        def distance(x, y, /):
            return (x * x + y * y) ** 0.5

        print(distance(3, 4))                  # 5.0
        try:
            distance(x=3, y=4)
        except TypeError as e:
            print(type(e).__name__)            # TypeError

        def format_row(name, /, **fields):     # 'name' can ALSO appear as a field
            return f"{name}: {fields}"

        print(format_row("user", name="asha"))  # user: {'name': 'asha'}
    ''')
    yield section("`*args` and `**kwargs`", "brackets")
    yield code('''
        def total(*nums):
            return sum(nums)

        def tag(name, **attrs):
            parts = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            return f"<{name} {parts}>"

        print(total(), total(1, 2, 3))                 # 0 6
        print(tag("a", href="/home", id="nav"))        # <a href="/home" id="nav">
    ''')
    yield note("The names `args` and `kwargs` are only convention — the `*` and `**` do the work. Use descriptive names when they help: `*paths`, `**options`.")
    yield section("Unpacking at the call site", "arrows-maximize")
    yield code('''
        def point(x, y, z=0):
            return (x, y, z)

        coords = [1, 2]
        opts = {"z": 9}
        print(point(*coords))                  # (1, 2, 0)
        print(point(*coords, **opts))          # (1, 2, 9)
        print(point(**{"x": 5, "y": 6}))       # (5, 6, 0)

        defaults = {"z": 1}
        overrides = {"z": 3}
        print(point(0, 0, **{**defaults, **overrides}))   # (0, 0, 3)   ← merge first, later wins
        print(max(*[4, 8, 2]), *"abc")         # 8 a b c
    ''')
    yield warn("Passing the same keyword twice is an error, even through unpacking: `point(1, 2, z=0, **{\"z\": 9})` raises `TypeError: got multiple values for keyword argument 'z'`. Merge the dicts first.")
    yield code('''
        def point(x, y, z=0):
            return (x, y, z)
        try:
            point(1, 2, z=0, **{"z": 9})
        except TypeError as e:
            print(type(e).__name__, "multiple values" in str(e))   # TypeError True
        try:
            point(1, x=1)
        except TypeError as e:
            print(e)   # point() got multiple values for argument 'x'
    ''')
    yield section("Forwarding arguments", "arrow-forward")
    yield p("`*args, **kwargs` in a wrapper accepts *anything* and passes it on unchanged — the core trick behind decorators, proxies and subclass constructors.")
    yield code('''
        import functools

        def logged(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                shown = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
                print(f"{func.__name__}({', '.join(shown)})")
                return func(*args, **kwargs)
            return wrapper

        @logged
        def power(base, exp=2):
            return base ** exp

        print(power(3, exp=3))
    ''', check=False)
    yield output('''
        power(3, exp=3)
        27
    ''')
    yield section("Inspecting a signature", "search")
    yield code('''
        import inspect

        def f(a, /, b, *args, c, d=1, **kw):
            pass

        sig = inspect.signature(f)
        print(str(sig))                  # (a, /, b, *args, c, d=1, **kw)
        print([p.kind.name for p in sig.parameters.values()])
        # ['POSITIONAL_ONLY', 'POSITIONAL_OR_KEYWORD', 'VAR_POSITIONAL', 'KEYWORD_ONLY', 'KEYWORD_ONLY', 'VAR_KEYWORD']
        bound = sig.bind(1, 2, 3, c=4)
        print(bound.arguments)           # {'a': 1, 'b': 2, 'args': (3,), 'c': 4}
    ''', check=False)
    yield output('''
        (a, /, b, *args, c, d=1, **kw)
        ['POSITIONAL_ONLY', 'POSITIONAL_OR_KEYWORD', 'VAR_POSITIONAL', 'KEYWORD_ONLY', 'KEYWORD_ONLY', 'VAR_KEYWORD']
        {'a': 1, 'b': 2, 'args': (3,), 'c': 4}
    ''')
    yield section("Defaults are evaluated once", "alert-triangle")
    yield code('''
        import time

        def stamp(when=time.time()):      # evaluated ONCE, at def time
            return when

        print(stamp() == stamp())         # True   ← same frozen value every call

        def stamp_ok(when=None):
            return time.time() if when is None else when
    ''')
    yield note("Same rule as the mutable-default trap: use `None` as a sentinel and compute the real default inside the function. If `None` is a valid value, use a private sentinel: `_MISSING = object()`.")
    yield qa("What are `*args` and `**kwargs`?",
             "In a definition, `*args` collects extra positional arguments into a tuple and `**kwargs` collects extra keyword arguments into a dict. In a call, `*seq` and `**mapping` do the reverse — unpack into separate arguments.")
    yield qa("What do `/` and `*` mean in a parameter list?",
             "Parameters before `/` are positional-only; parameters after `*` (or after `*args`) are keyword-only. So in `def f(a, /, b, *, c)`, `a` must be positional, `c` must be named, and `b` can be either.")
    yield qa("Why make parameters keyword-only?",
             "Readability and safety: `resize(img, 100, 200, True)` becomes `resize(img, width=100, height=200, keep_ratio=True)`, arguments can't be swapped by accident, and you can add or reorder options later without breaking callers.")


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


@topic(G, "recursion", "Recursion", "refresh")
def _():
    yield lead("A recursive function solves a problem by calling itself on a smaller piece of it. Natural for trees, divide-and-conquer and backtracking — but in Python, mind the stack depth.")
    yield define("Recursion", "a function that calls itself. It needs a **base case** that returns without recursing, and a **recursive case** that moves strictly closer to the base case.")
    yield section("Anatomy", "template")
    yield code('''
        def factorial(n: int) -> int:
            if n <= 1:                    # base case
                return 1
            return n * factorial(n - 1)   # recursive case: smaller input

        def digit_sum(n: int) -> int:
            return n if n < 10 else n % 10 + digit_sum(n // 10)

        print(factorial(5), factorial(20))   # 120 2432902008176640000
        print(digit_sum(98765))              # 35
    ''')
    yield steps(
        ("Define the base case", "The smallest input you can answer directly (`n <= 1`, empty list, `None` node)."),
        ("Trust the recursion", "Assume the call on the smaller input returns the right answer."),
        ("Combine", "Build this level's answer from the smaller result(s)."),
        ("Check progress", "Every call must shrink the input, or it never reaches the base case."),
    )
    yield section("The call stack", "stack-2")
    yield p("Each call gets its own **frame** (its local variables) pushed on the call stack; it is popped when the call returns. `factorial(4)` stacks four frames before any multiplication happens.")
    yield code('''
        def countdown(n, depth=0):
            print("  " * depth + f"enter {n}")
            if n > 0:
                countdown(n - 1, depth + 1)
            print("  " * depth + f"leave {n}")

        countdown(2)
    ''', check=False)
    yield output('''
        enter 2
          enter 1
            enter 0
            leave 0
          leave 1
        leave 2
    ''')
    yield section("Recursion limit & RecursionError", "alert-octagon")
    yield p("CPython caps the stack depth (default **1000** frames) to avoid crashing the interpreter. Exceeding it raises `RecursionError` — also what you get from a missing base case.")
    yield code('''
        import sys

        def no_base_case(n):
            return no_base_case(n + 1)

        try:
            no_base_case(0)
        except RecursionError as e:
            print(type(e).__name__, "-", e)   # RecursionError - maximum recursion depth exceeded
        print(sys.getrecursionlimit())        # 1000
    ''')
    yield table(
        ["Option", "When"],
        ["Rewrite iteratively (loop / explicit stack)", "Best fix for deep, linear recursion (linked lists, DFS on 10⁵ nodes)"],
        ["`sys.setrecursionlimit(10**5)`", "Quick fix in contests — the C stack may still overflow and crash"],
        ["Memoize (`@cache`)", "When the depth is fine but the *number* of calls explodes"],
    )
    yield warn("Python does **not** optimise tail calls. `return f(n - 1)` still consumes a frame per call, so tail-recursive style doesn't save you from `RecursionError` — Guido rejected TCO to keep full tracebacks.")
    yield section("Memoization: from exponential to linear", "database")
    yield code('''
        from functools import cache

        calls = 0
        def fib_slow(n):
            global calls
            calls += 1
            return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)

        fib_slow(20)
        print(calls)                 # 21891   ← O(2^n) calls

        @cache
        def fib(n):
            return n if n < 2 else fib(n - 1) + fib(n - 2)

        print(fib(90))               # 2880067194370816120
        print(fib.cache_info().misses)   # 91   ← each n computed once
    ''')
    yield section("Recursion → iteration with an explicit stack", "arrows-exchange")
    yield code('''
        tree = {"a": ["b", "c"], "b": ["d"], "c": [], "d": []}

        def dfs_recursive(node, out):
            out.append(node)
            for child in tree[node]:
                dfs_recursive(child, out)
            return out

        def dfs_iterative(root):
            out, stack = [], [root]
            while stack:
                node = stack.pop()
                out.append(node)
                stack.extend(reversed(tree[node]))   # reversed → same order as recursion
            return out

        print(dfs_recursive("a", []))   # ['a', 'b', 'd', 'c']
        print(dfs_iterative("a"))       # ['a', 'b', 'd', 'c']
    ''')
    yield note("Any recursion can be converted: the explicit stack holds what the call stack held. Heap memory is plentiful; the call stack is not.")
    yield section("Classic patterns", "star")
    yield code('''
        def binary_search(xs, target, lo=0, hi=None):
            hi = len(xs) - 1 if hi is None else hi
            if lo > hi:
                return -1
            mid = (lo + hi) // 2
            if xs[mid] == target:
                return mid
            if xs[mid] < target:
                return binary_search(xs, target, mid + 1, hi)
            return binary_search(xs, target, lo, mid - 1)

        def power(x, n):                       # fast exponentiation: O(log n) calls
            if n == 0:
                return 1
            half = power(x, n // 2)
            return half * half * (x if n % 2 else 1)

        def flatten(items):
            for it in items:
                if isinstance(it, list):
                    yield from flatten(it)     # recursive generator
                else:
                    yield it

        print(binary_search([1, 3, 5, 7, 9], 7))     # 3
        print(power(2, 30))                          # 1073741824
        print(list(flatten([1, [2, [3, [4]], 5]])))  # [1, 2, 3, 4, 5]
    ''')
    yield section("Backtracking: subsets & permutations", "git-branch")
    yield p("Backtracking explores a tree of choices: **choose**, **recurse**, **un-choose**. It powers subsets, permutations, N-Queens, Sudoku and word search.")
    yield code('''
        def subsets(nums):
            result, path = [], []
            def backtrack(i):
                if i == len(nums):
                    result.append(path[:])      # copy! path keeps changing
                    return
                path.append(nums[i])            # choose nums[i]
                backtrack(i + 1)
                path.pop()                      # un-choose
                backtrack(i + 1)                # skip nums[i]
            backtrack(0)
            return result

        def permutations(nums):
            if len(nums) <= 1:
                return [nums[:]]
            out = []
            for i, x in enumerate(nums):
                for rest in permutations(nums[:i] + nums[i + 1:]):
                    out.append([x] + rest)
            return out

        print(subsets([1, 2]))          # [[1, 2], [1], [2], []]
        print(permutations([1, 2, 3]))  # [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    ''')
    yield warn("Appending `path` instead of `path[:]` stores the *same* list object many times — at the end every entry is the final (empty) path.")
    yield section("Trees & mutual recursion", "binary-tree")
    yield code('''
        class Node:
            def __init__(self, val, left=None, right=None):
                self.val, self.left, self.right = val, left, right

        def height(node):
            if node is None:
                return 0
            return 1 + max(height(node.left), height(node.right))

        def inorder(node):
            return inorder(node.left) + [node.val] + inorder(node.right) if node else []

        root = Node(2, Node(1), Node(4, Node(3)))
        print(height(root), inorder(root))    # 3 [1, 2, 3, 4]

        def is_even(n):
            return True if n == 0 else is_odd(n - 1)

        def is_odd(n):
            return False if n == 0 else is_even(n - 1)

        print(is_even(10), is_odd(7))         # True True
    ''')
    yield table(
        ["Recursion shines", "Prefer iteration"],
        ["Trees, graphs (DFS), nested data", "Simple counting loops"],
        ["Divide and conquer (merge sort, quick sort)", "Linear chains deeper than ~1000"],
        ["Backtracking & top-down DP with `@cache`", "Hot loops where call overhead matters"],
    )
    yield qa("What is the default recursion limit in Python and how do you work around it?",
             "About 1000 frames (`sys.getrecursionlimit()`). Raise it with `sys.setrecursionlimit` (risky — the C stack can still overflow), or better, convert the recursion to a loop with an explicit stack.")
    yield qa("Does Python optimise tail recursion?",
             "No. Every call adds a frame, even `return f(n - 1)`. The design choice preserves full tracebacks. Convert tail recursion to a `while` loop instead.")
    yield qa("How do you speed up a recursive solution with overlapping subproblems?",
             "Memoize it — decorate with `@functools.cache` (or pass a `memo` dict). Fibonacci drops from O(2ⁿ) calls to O(n). That is top-down dynamic programming.")


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


@topic(G, "functools-module", "functools Deep Dive", "tools")
def _():
    yield lead("`functools` is the standard library's toolbox for working *with functions*: caching, pre-filling arguments, building decorators, generic dispatch and ordering.")
    yield section("At a glance", "list")
    yield table(
        ["Tool", "What it does"],
        ["`partial(f, *a, **kw)`", "New callable with some arguments pre-filled"],
        ["`partialmethod`", "`partial` for methods defined in a class body"],
        ["`reduce(f, it, init)`", "Fold an iterable into a single value"],
        ["`cache` / `lru_cache(maxsize)`", "Memoize results by arguments"],
        ["`cached_property`", "Compute an attribute once per instance, then store it"],
        ["`wraps` / `update_wrapper`", "Copy name, docstring, etc. onto a wrapper"],
        ["`total_ordering`", "Fill in `<=`, `>`, `>=` from `__eq__` + one comparison"],
        ["`singledispatch`", "Choose an implementation by the **type** of the first argument"],
        ["`cmp_to_key`", "Turn an old-style comparator into a `key=` function"],
    )
    yield section("partial & partialmethod", "puzzle")
    yield code('''
        from functools import partial, partialmethod

        def power(base, exp):
            return base ** exp

        square = partial(power, exp=2)
        cube = partial(power, exp=3)
        print(square(7), cube(2))                    # 49 8
        print(square.func.__name__, square.keywords) # power {'exp': 2}

        parse_hex = partial(int, base=16)
        print(list(map(parse_hex, ["ff", "10"])))    # [255, 16]

        class Light:
            def set(self, state):
                self.state = state
                return state
            on = partialmethod(set, "on")
            off = partialmethod(set, "off")

        print(Light().on())                          # on
    ''')
    yield note("`partial` beats a lambda when you want an inspectable, picklable callable (e.g. passing work to a process pool) — lambdas can't be pickled.")
    yield section("reduce", "arrows-minimize")
    yield code('''
        from functools import reduce
        import operator

        print(reduce(operator.add, [1, 2, 3, 4]))           # 10
        print(reduce(operator.mul, range(1, 6), 1))         # 120
        print(reduce(lambda acc, d: {**acc, **d}, [{"a": 1}, {"b": 2}, {"a": 3}], {}))   # {'a': 3, 'b': 2}
        print(reduce(max, [3, 9, 2]))                       # 9
    ''')
    yield warn("`reduce` on an empty iterable without an initial value raises `TypeError`. Prefer `sum`, `math.prod`, `max`, `any`/`all` or a loop when they express the intent better.")
    yield section("cache & lru_cache", "database")
    yield code('''
        from functools import lru_cache, cache

        @lru_cache(maxsize=2)
        def square(x):
            return x * x

        square(1); square(2); square(1)      # hit for 1
        square(3)                            # evicts 2 (least recently used)
        square(2)                            # miss again
        info = square.cache_info()
        print(info.hits, info.misses, info.currsize)   # 1 4 2
        square.cache_clear()
        print(square.cache_info().currsize)            # 0

        @lru_cache(typed=True)
        def kind(x):
            return type(x).__name__
        print(kind(1), kind(1.0))            # int float   ← typed: 1 and 1.0 cached separately

        @cache
        def total(xs):
            return sum(xs)
        try:
            total([1, 2])                    # arguments are dict keys → must be hashable
        except TypeError as e:
            print(e)                         # unhashable type: 'list'
        print(total((1, 2)))                 # 3
    ''')
    yield table(
        ["", "`@cache`", "`@lru_cache(maxsize=128)`"],
        ["Size", "Unbounded", "Bounded; evicts least-recently-used"],
        ["Speed", "Slightly faster (no bookkeeping)", "Small LRU overhead"],
        ["Use for", "Recursion / DP with a bounded input space", "Long-running services with unbounded inputs"],
    )
    yield warn("Decorating a **method** with `@cache` caches on `self` too: every instance stays alive as long as the cache does (a memory leak), and instances must be hashable. Prefer `cached_property`, a module-level cached function, or a per-instance dict.", "Method caching pitfall")
    yield section("cached_property", "clock")
    yield code('''
        from functools import cached_property

        class Report:
            def __init__(self, rows):
                self.rows = rows
                self.computed = 0

            @cached_property
            def total(self):
                self.computed += 1           # expensive work, done once
                return sum(self.rows)

        r = Report([5, 10, 20])
        print(r.total, r.total, r.computed)  # 35 35 1
        del r.total                          # invalidate: the next access recomputes
        print(r.total, r.computed)           # 35 2
    ''')
    yield note("`cached_property` stores the value in the instance `__dict__` under the same name, so later lookups never call the function. It needs a `__dict__` (not compatible with `__slots__` alone). Unlike `property`, it is writable.")
    yield section("wraps & update_wrapper", "gift")
    yield code('''
        from functools import wraps, update_wrapper

        def plain(f):
            def wrapper(*a, **kw):
                return f(*a, **kw)
            return wrapper

        def proper(f):
            @wraps(f)                         # = update_wrapper(wrapper, f)
            def wrapper(*a, **kw):
                return f(*a, **kw)
            return wrapper

        @plain
        def area(r):
            """Circle area."""
        @proper
        def volume(r):
            """Sphere volume."""

        print(area.__name__, area.__doc__)        # wrapper None
        print(volume.__name__, volume.__doc__)    # volume Sphere volume.
        print(volume.__wrapped__.__name__)        # volume   ← the original, for introspection
    ''')
    yield section("total_ordering", "arrows-sort")
    yield code('''
        from functools import total_ordering

        @total_ordering
        class Grade:
            order = "FDCBA"
            def __init__(self, letter):
                self.letter = letter
            def __eq__(self, other):
                return self.letter == other.letter
            def __lt__(self, other):
                return self.order.index(self.letter) < self.order.index(other.letter)
            def __repr__(self):
                return self.letter

        print(Grade("B") > Grade("C"), Grade("A") <= Grade("A"))   # True True
        print(sorted([Grade("C"), Grade("A"), Grade("F")]))        # [F, C, A]
    ''')
    yield section("singledispatch — overloading by type", "git-fork")
    yield code('''
        from functools import singledispatch, singledispatchmethod

        @singledispatch
        def to_json(value):
            raise TypeError(f"can't serialise {type(value).__name__}")

        @to_json.register
        def _(value: int):
            return str(value)

        @to_json.register
        def _(value: str):
            return f'"{value}"'

        @to_json.register(list)
        def _(value):
            return "[" + ", ".join(to_json(v) for v in value) + "]"

        print(to_json([1, "a", [2]]))       # [1, "a", [2]]
        print(to_json(True))                # True   ← bool is a subclass of int
        try:
            to_json(1.5)
        except TypeError as e:
            print(e)                        # can't serialise float

        class Area:
            @singledispatchmethod
            def of(self, shape):
                raise NotImplementedError
            @of.register
            def _(self, side: int):
                return side * side
            @of.register
            def _(self, dims: tuple):
                return dims[0] * dims[1]

        print(Area().of(3), Area().of((2, 5)))   # 9 10
    ''')
    yield note("Dispatch looks only at the **first** argument's type and follows the MRO, so a handler for `int` also handles `bool`. It's the standard-library answer to “function overloading”.")
    yield section("cmp_to_key & the operator module", "settings")
    yield code('''
        from functools import cmp_to_key
        from operator import itemgetter, attrgetter, methodcaller

        def by_length_then_reverse_alpha(a, b):
            if len(a) != len(b):
                return len(a) - len(b)
            return (a < b) - (a > b)          # reverse alphabetical

        words = ["bb", "a", "cc", "c"]
        print(sorted(words, key=cmp_to_key(by_length_then_reverse_alpha)))   # ['c', 'a', 'cc', 'bb']

        print(itemgetter(0, 2)("xyz"))                     # ('x', 'z')
        print(attrgetter("real")(3 + 4j))                  # 3.0
        print(list(map(methodcaller("upper"), ["a", "b"])))   # ['A', 'B']
    ''')
    yield cards(
        ("`operator.add`, `mul`, …", "Function versions of operators — pass to `reduce`, `map`, `accumulate`.", "plus"),
        ("`itemgetter(k)`", "`lambda x: x[k]` — faster, and accepts several keys.", "list-details"),
        ("`attrgetter('a.b')`", "`lambda x: x.a.b` — dotted paths allowed.", "dots"),
        ("`methodcaller('m', arg)`", "`lambda x: x.m(arg)`.", "phone-call"),
    )
    yield qa("How does `lru_cache` work?",
             "It stores results in a dict keyed by the call's arguments (so they must be hashable) and keeps a doubly linked list of recency. On a hit it returns the stored value and marks it recent; when the cache exceeds `maxsize`, it evicts the least recently used entry. `cache_info()` reports hits and misses.")
    yield qa("`partial` vs `lambda`?",
             "Both pre-fill arguments. `partial` is introspectable (`.func`, `.args`, `.keywords`), picklable when the wrapped function is, and binds values immediately — no late-binding surprise in loops. A lambda is more flexible (can reorder or transform arguments).")
    yield qa("How do you get function overloading in Python?",
             "Python has no signature-based overloading — a later `def` replaces the earlier one. Use default/keyword arguments, or `functools.singledispatch` to dispatch on the first argument's type (`singledispatchmethod` for methods).")


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


@topic(G, "advanced-decorators", "Advanced Decorators", "sparkles")
def _():
    yield lead("Beyond the basic wrapper: decorators with optional arguments, decorators that are classes, decorators *for* classes, registries, and the traps to avoid.")
    yield section("Recap: the three shapes", "template")
    yield table(
        ["Usage", "What Python calls", "Your decorator must be"],
        ["`@d`", "`f = d(f)`", "a callable taking the function"],
        ["`@d(3)`", "`f = d(3)(f)`", "a factory returning a decorator"],
        ["`@d` on a class", "`C = d(C)`", "a callable taking the class"],
    )
    yield section("Optional arguments: `@d` and `@d(…)`", "adjustments")
    yield p("Make the function the first, optional positional parameter and the options keyword-only. If a function arrives, decorate it now; otherwise return a decorator.")
    yield code('''
        import functools

        def repeat(func=None, *, times=2):
            def decorator(f):
                @functools.wraps(f)
                def wrapper(*args, **kwargs):
                    return [f(*args, **kwargs) for _ in range(times)]
                return wrapper
            if func is None:            # used as @repeat(times=3)
                return decorator
            return decorator(func)      # used as bare @repeat

        @repeat
        def hi():
            return "hi"

        @repeat(times=3)
        def yo():
            return "yo"

        print(hi(), yo())   # ['hi', 'hi'] ['yo', 'yo', 'yo']
    ''')
    yield section("Class-based decorators with state", "box")
    yield p("Any callable can be a decorator. A class whose `__init__` takes the function and whose `__call__` runs it keeps state naturally in attributes.")
    yield code('''
        import functools

        class CountCalls:
            def __init__(self, func):
                functools.update_wrapper(self, func)   # copy __name__, __doc__
                self.func = func
                self.calls = 0

            def __call__(self, *args, **kwargs):
                self.calls += 1
                return self.func(*args, **kwargs)

        @CountCalls
        def add(a, b):
            """Add two numbers."""
            return a + b

        add(1, 2); add(3, 4)
        print(add.calls, add.__name__, add(5, 5))   # 2 add 10
    ''')
    yield warn("A class-based decorator applied to a **method** breaks `self`: instances of `CountCalls` aren't descriptors, so `obj.method` doesn't bind. Add a `__get__` returning `functools.partial(self.__call__, obj)`, or use a function-based decorator for methods.")
    yield section("Decorating methods", "user")
    yield p("Function-based decorators work on methods unchanged — `self` simply arrives as the first element of `*args`.")
    yield code('''
        import functools

        def require_login(method):
            @functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                if not self.logged_in:
                    raise PermissionError(f"{method.__name__} needs login")
                return method(self, *args, **kwargs)
            return wrapper

        class Account:
            def __init__(self):
                self.logged_in = False
            @require_login
            def balance(self):
                return 100

        acc = Account()
        try:
            acc.balance()
        except PermissionError as e:
            print(e)                  # balance needs login
        acc.logged_in = True
        print(acc.balance())          # 100
    ''')
    yield section("Class decorators", "hierarchy")
    yield p("A class decorator receives the finished class and returns it (modified) or a replacement. `@dataclass` is the famous one — it reads the annotations and generates `__init__`, `__repr__` and `__eq__`.")
    yield code('''
        def add_repr(cls):
            def __repr__(self):
                fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
                return f"{cls.__name__}({fields})"
            cls.__repr__ = __repr__
            return cls

        def singleton(cls):
            instances = {}
            def get(*args, **kwargs):
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
                return instances[cls]
            return get

        @add_repr
        class User:
            def __init__(self, name, age):
                self.name, self.age = name, age

        @singleton
        class Config:
            pass

        print(User("asha", 30))           # User(name='asha', age=30)
        print(Config() is Config())       # True
    ''')
    yield warn("The `singleton` above replaces the class with a function, so `isinstance(x, Config)` no longer works. Decorators that *return the class* are safer than ones that replace it.")
    yield section("Registries & plugins", "plug")
    yield p("A decorator doesn't have to wrap anything — it can just **record** the function and return it unchanged. This is how Flask routes, pytest fixtures and CLI command groups work.")
    yield code('''
        HANDLERS = {}

        def on(event):
            def register(func):
                HANDLERS[event] = func
                return func               # unchanged
            return register

        @on("signup")
        def welcome(user):
            return f"welcome {user}"

        @on("delete")
        def goodbye(user):
            return f"bye {user}"

        def dispatch(event, user):
            return HANDLERS[event](user)

        print(sorted(HANDLERS))           # ['delete', 'signup']
        print(dispatch("signup", "asha")) # welcome asha
    ''')
    yield section("Stacking order", "stack")
    yield p("Decorators are **applied** bottom-up (closest to `def` first) but the wrappers **run** top-down, like layers of an onion.")
    yield code('''
        import functools

        def layer(name):
            def deco(f):
                print(f"apply {name}")
                @functools.wraps(f)
                def wrapper():
                    print(f"enter {name}")
                    result = f()
                    print(f"exit {name}")
                    return result
                return wrapper
            return deco

        @layer("outer")
        @layer("inner")
        def work():
            print("work")

        work()
    ''', check=False)
    yield output('''
        apply inner
        apply outer
        enter outer
        enter inner
        work
        exit inner
        exit outer
    ''')
    yield note("Order matters: `@app.route` above `@login_required` protects the route; the other way round registers the *unprotected* function. Similarly put `@cache` where you want the cache to sit relative to logging or timing.")
    yield section("Validation from type hints", "shield-check")
    yield code('''
        import functools, inspect

        def enforce_types(func):
            sig = inspect.signature(func)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                bound = sig.bind(*args, **kwargs)
                for name, value in bound.arguments.items():
                    expected = func.__annotations__.get(name)
                    if isinstance(expected, type) and not isinstance(value, expected):
                        raise TypeError(f"{name} must be {expected.__name__}")
                return func(*args, **kwargs)
            return wrapper

        @enforce_types
        def repeat_text(text: str, n: int) -> str:
            return text * n

        print(repeat_text("ab", 2))           # abab
        try:
            repeat_text("ab", "2")
        except TypeError as e:
            print(e)                          # n must be int
        print(inspect.signature(repeat_text)) # (text: str, n: int) -> str
    ''')
    yield note("`functools.wraps` sets `__wrapped__`, which `inspect.signature` follows — so the decorated function still shows its real signature in help, IDEs and docs.")
    yield section("Decorators that are also context managers", "door-exit")
    yield code('''
        from contextlib import ContextDecorator

        class traced(ContextDecorator):
            def __init__(self, label):
                self.label = label
            def __enter__(self):
                print(f"start {self.label}")
                return self
            def __exit__(self, *exc):
                print(f"end {self.label}")
                return False

        @traced("job")                    # as a decorator
        def job():
            print("working")

        job()
        with traced("block"):             # as a with-statement
            print("inline")
    ''', check=False)
    yield output('''
        start job
        working
        end job
        start block
        inline
        end block
    ''')
    yield section("Pitfalls", "alert-triangle")
    yield cards(
        ("Forgetting `wraps`", "Name, docstring and signature are lost — confusing tracebacks, broken introspection.", "tag-off"),
        ("Forgetting to return", "The wrapper must `return func(...)`, and the decorator must `return wrapper` — otherwise the function becomes `None`.", "arrow-back"),
        ("`@d` vs `@d()`", "A factory used without parentheses receives the function as its option argument — support both forms or be consistent.", "brackets"),
        ("Import-time side effects", "Decorator bodies run when the module is imported. Keep them cheap; do the work inside the wrapper.", "clock"),
    )
    yield qa("How do you write a decorator that accepts arguments?",
             "Add a level: an outer function takes the arguments and returns the actual decorator, which takes the function and returns the wrapper. `@retry(times=3)` means `f = retry(times=3)(f)`.")
    yield qa("What is a class decorator? Give an example.",
             "A callable that receives a class and returns a class (usually the same one, modified). `@dataclass` inspects the annotations and adds `__init__`, `__repr__` and `__eq__`; `@functools.total_ordering` adds comparison methods.")
    yield qa("In what order are stacked decorators applied?",
             "Bottom-up: `@a @b def f` is `f = a(b(f))`. At call time the outermost wrapper (`a`) runs first and calls into `b`'s wrapper, which calls `f`.")
