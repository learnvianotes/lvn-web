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
    )
