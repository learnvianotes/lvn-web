from kit import *

G = "Data Structures"


@topic(G, "lists-tuples", "Lists & Tuples", "list")
def _():
    yield lead("`list` is a mutable, ordered, dynamic array. `tuple` is its immutable sibling — lighter, hashable, and used for fixed records.")
    yield define("list", "a dynamic array of *references* to objects. Indexing is O(1); appending is amortised O(1) because Python over-allocates capacity.")
    yield section("Core operations & complexity", "clock")
    yield table(
        ["Operation", "Example", "Time"],
        ["Index / assign", "`xs[i]`, `xs[i] = v`", "O(1)"],
        ["Append / pop from end", "`xs.append(v)`, `xs.pop()`", "O(1) amortised"],
        ["Insert / pop at front", "`xs.insert(0, v)`, `xs.pop(0)`", "**O(n)** — use `deque`"],
        ["Search", "`v in xs`, `xs.index(v)`", "O(n)"],
        ["Slice", "`xs[a:b]`", "O(b − a)"],
        ["Sort", "`xs.sort()`, `sorted(xs)`", "O(n log n) — Timsort, stable"],
        ["Extend", "`xs.extend(ys)`, `xs + ys`", "O(len(ys))"],
    )
    yield code('''
        xs = [5, 2, 9]
        xs.append(1)
        xs.extend([7, 3])
        xs.insert(1, 4)
        print(xs)                       # [5, 4, 2, 9, 1, 7, 3]
        print(xs.pop(), xs.pop(0))      # 3 5
        xs.remove(9)                    # removes the first 9 (ValueError if absent)
        print(sorted(xs), xs[::-1])     # [1, 2, 4, 7] [7, 1, 2, 4]
    ''')
    yield section("`sort()` vs `sorted()`", "sort-ascending")
    yield cards(
        ("`xs.sort()`", "Sorts **in place** and returns `None`. Only for lists.", "arrows-sort"),
        ("`sorted(it)`", "Returns a **new** list from any iterable. The original is untouched.", "copy"),
    )
    yield code('''
        people = [("Ravi", 30), ("Asha", 25), ("Kiran", 30)]
        print(sorted(people, key=lambda p: p[1]))
        # [('Asha', 25), ('Ravi', 30), ('Kiran', 30)]   ← stable: Ravi stays before Kiran
        print(sorted(people, key=lambda p: (-p[1], p[0])))
        # [('Kiran', 30), ('Ravi', 30), ('Asha', 25)]   ← age desc, then name asc
    ''', check=False)
    yield section("Copies: aliasing, shallow, deep", "copy")
    yield code('''
        import copy
        grid = [[0, 0], [0, 0]]
        alias = grid                 # same list
        shallow = grid[:]            # new outer list, same inner lists
        deep = copy.deepcopy(grid)   # everything copied
        grid[0][0] = 9
        print(alias[0][0], shallow[0][0], deep[0][0])   # 9 9 0
    ''')
    yield warn("`[[0] * 3] * 3` creates **three references to the same inner list** — changing one row changes all. Build 2-D lists with a comprehension: `[[0] * 3 for _ in range(3)]`.", "Classic bug")
    yield code('''
        bad = [[0] * 3] * 3
        bad[0][0] = 1
        print(bad)                              # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]
        good = [[0] * 3 for _ in range(3)]
        good[0][0] = 1
        print(good)                             # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    ''')
    yield section("Tuples, packing & unpacking", "brackets")
    yield code('''
        point = (3, 4)
        x, y = point                    # unpacking
        a, b = 1, 2
        a, b = b, a                     # swap without a temp variable
        first, *middle, last = [1, 2, 3, 4, 5]
        print(x, y, a, b)               # 3 4 2 1
        print(first, middle, last)      # 1 [2, 3, 4] 5
        single = (42,)                  # the comma makes the tuple, not the parentheses
        print(type(single).__name__)    # tuple
    ''')
    yield table(
        ["", "`list`", "`tuple`"],
        ["Mutable", "Yes", "No"],
        ["Hashable (dict key / set item)", "No", "Yes, if its items are hashable"],
        ["Memory / speed", "Slightly larger", "Smaller, slightly faster to create"],
        ["Use for", "Collections that grow and change", "Fixed records: coordinates, DB rows, dict keys"],
    )
    yield section("Named tuples", "tag")
    yield code('''
        from collections import namedtuple
        Point = namedtuple("Point", ["x", "y"])
        p = Point(3, 4)
        print(p.x + p.y, p)          # 7 Point(x=3, y=4)
    ''')


@topic(G, "dictionaries", "Dictionaries", "book-2")
def _():
    yield lead("`dict` maps hashable keys to values with average O(1) lookup, insert and delete — the workhorse of Python.")
    yield define("Hash table", "each key's `hash()` picks a slot; collisions are resolved by open addressing. Since Python 3.7, dicts **preserve insertion order**.")
    yield section("Create, read, update", "pencil")
    yield code('''
        ages = {"asha": 25, "ravi": 30}
        ages["kiran"] = 28                    # insert / update
        print(ages["asha"])                   # 25
        print(ages.get("zoe"), ages.get("zoe", 0))   # None 0
        print("ravi" in ages, len(ages))      # True 3
        del ages["ravi"]
        print(ages.pop("kiran"), ages)        # 28 {'asha': 25}
    ''')
    yield warn("`d[key]` raises `KeyError` for a missing key. Use `d.get(key, default)`, `key in d`, `setdefault`, or a `defaultdict`.")
    yield section("Iterating", "repeat")
    yield code('''
        scores = {"math": 90, "cs": 95}
        for subject, score in scores.items():
            print(subject, score, end="; ")   # math 90; cs 95;
        print()
        print(list(scores), list(scores.values()))   # ['math', 'cs'] [90, 95]
    ''', check=False)
    yield note("Don't add or remove keys while iterating over a dict (`RuntimeError`). Iterate over `list(d)` if you must modify it.")
    yield section("Useful methods", "tools")
    yield table(
        ["Method", "Does"],
        ["`d.get(k, default)`", "Value or default — never raises"],
        ["`d.setdefault(k, v)`", "Insert `v` if `k` is missing, then return `d[k]`"],
        ["`d.update(other)` / `d | other`", "Merge (the right-hand side wins); `|` returns a new dict (3.9+)"],
        ["`d.pop(k, default)`", "Remove and return"],
        ["`d.items()` / `keys()` / `values()`", "Live *views* that reflect later changes"],
        ["`dict.fromkeys(keys, v)`", "New dict with every key set to `v`"],
    )
    yield code('''
        base = {"theme": "light", "font": 14}
        user = {"theme": "dark"}
        print(base | user)                        # {'theme': 'dark', 'font': 14}
        counts = {}
        for ch in "banana":
            counts[ch] = counts.get(ch, 0) + 1
        print(counts)                             # {'b': 1, 'a': 3, 'n': 2}
        print(max(counts, key=counts.get))        # a
    ''')
    yield section("What can be a key?", "key")
    yield p("Keys must be **hashable**: their hash never changes during their lifetime. Immutable built-ins (`int`, `str`, `tuple` of hashables, `frozenset`) are hashable; `list`, `dict` and `set` are not.")
    yield code('''
        grid = {(0, 0): "start", (2, 3): "goal"}     # tuples make great coordinate keys
        print(grid[(2, 3)])                          # goal
        try:
            {[1, 2]: "x"}                            # lists are unhashable
        except TypeError as e:
            print(type(e).__name__)                  # TypeError
    ''')
    yield section("Dictionary patterns", "puzzle")
    yield cards(
        ("Frequency count", "`Counter(items)` or `d[x] = d.get(x, 0) + 1`.", "chart-bar"),
        ("Grouping", "`defaultdict(list)` then `groups[key].append(item)`.", "folders"),
        ("Two-sum lookup", "Store `value → index` while scanning; check `target - x in seen`.", "search"),
        ("Memoization", "Cache results: `memo[args] = result` — or use `functools.cache`.", "database"),
    )
    yield code('''
        def two_sum(nums, target):
            seen = {}                      # value → index
            for i, x in enumerate(nums):
                if target - x in seen:
                    return [seen[target - x], i]
                seen[x] = i
            return []

        print(two_sum([2, 7, 11, 15], 9))   # [0, 1]
    ''')


@topic(G, "sets", "Sets", "circles-relation")
def _():
    yield lead("A `set` is an unordered collection of unique, hashable items with O(1) membership tests — and real set algebra.")
    yield code('''
        a = {1, 2, 3, 4}
        b = {3, 4, 5}
        print(a | b)          # {1, 2, 3, 4, 5}
        print(a & b)          # {3, 4}
        print(a - b)          # {1, 2}
        print(a ^ b)          # {1, 2, 5}
        print({1, 2} <= a)    # True
    ''')
    yield table(
        ["Operator", "Method", "Meaning"],
        ["`a | b`", "`a.union(b)`", "In either"],
        ["`a & b`", "`a.intersection(b)`", "In both"],
        ["`a - b`", "`a.difference(b)`", "In `a` but not `b`"],
        ["`a ^ b`", "`a.symmetric_difference(b)`", "In exactly one"],
        ["`a <= b`", "`a.issubset(b)`", "Every item of `a` is in `b`"],
    )
    yield section("Adding & removing", "plus")
    yield code('''
        s = set()                  # {} would be an empty *dict*
        s.add(3); s.add(3); s.add(1)
        s.discard(99)              # no error if missing
        print(sorted(s), len(s))   # [1, 3] 2
    ''')
    yield warn("`remove(x)` raises `KeyError` if `x` is missing; `discard(x)` doesn't. And `{}` is an empty **dict** — write `set()`.")
    yield section("When to reach for a set", "bulb")
    yield cards(
        ("De-duplicate", "`list(set(xs))` — order is lost; use `list(dict.fromkeys(xs))` to keep first-seen order.", "filter"),
        ("Fast membership", "`x in big_set` is O(1) vs O(n) for a list — the difference between TLE and AC.", "bolt"),
        ("Visited nodes", "BFS / DFS keep a `visited` set of states or coordinates.", "route"),
        ("frozenset", "An immutable, hashable set — usable as a dict key or inside another set.", "snowflake"),
    )
    yield code('''
        xs = [3, 1, 3, 2, 1]
        print(list(dict.fromkeys(xs)))                   # [3, 1, 2]
        def has_duplicate(nums):
            return len(set(nums)) != len(nums)
        print(has_duplicate(xs), has_duplicate([1, 2]))  # True False
    ''')


@topic(G, "comprehensions", "Comprehensions", "filter")
def _():
    yield lead("Comprehensions build lists, dicts and sets in one readable expression: *what* to produce, *from where*, and *which* items.")
    yield section("The shape", "template")
    yield code('''
        squares = [x * x for x in range(6)]
        evens = [x for x in range(10) if x % 2 == 0]
        labels = ["even" if x % 2 == 0 else "odd" for x in range(4)]
        print(squares)    # [0, 1, 4, 9, 16, 25]
        print(evens)      # [0, 2, 4, 6, 8]
        print(labels)     # ['even', 'odd', 'even', 'odd']
    ''')
    yield note("A filter `if` goes **after** the `for`. A conditional *value* (`a if c else b`) goes **before** it.")
    yield section("Dict & set comprehensions", "braces")
    yield code('''
        words = ["apple", "bat", "cherry"]
        lengths = {w: len(w) for w in words}
        inverted = {v: k for k, v in lengths.items()}
        first_letters = {w[0] for w in words}
        print(lengths)            # {'apple': 5, 'bat': 3, 'cherry': 6}
        print(inverted[3])        # bat
        print(sorted(first_letters))   # ['a', 'b', 'c']
    ''')
    yield section("Nested loops & flattening", "stack-2")
    yield code('''
        matrix = [[1, 2, 3], [4, 5, 6]]
        flat = [x for row in matrix for x in row]          # outer loop first
        transposed = [list(col) for col in zip(*matrix)]
        pairs = [(i, j) for i in range(3) for j in range(i + 1, 3)]
        print(flat)          # [1, 2, 3, 4, 5, 6]
        print(transposed)    # [[1, 4], [2, 5], [3, 6]]
        print(pairs)         # [(0, 1), (0, 2), (1, 2)]
    ''')
    yield section("Generator expressions", "bolt")
    yield p("Swap `[]` for `()` and nothing is built up front — values are produced lazily, one at a time. Ideal when you only aggregate.")
    yield code('''
        total = sum(x * x for x in range(1_000_000))   # no million-item list in memory
        print(total)                                    # 333332833333500000
        print(any(n > 10 for n in [3, 12, 5]))          # True
    ''')
    yield dodont(
        "Use comprehensions for simple map/filter transformations that fit on one or two lines.",
        "Nesting three levels deep or adding side effects (`[print(x) for x in xs]`) — write a normal loop instead.",
    )


@topic(G, "object-model", "Identity, Mutability & Copying", "fingerprint")
def _():
    yield lead("Every Python value is an object with an **identity**, a **type** and a **value**. Knowing which objects are shared, which can change, and how copies work explains most “spooky action at a distance” bugs.")
    yield define("Object", "a chunk of memory with an identity (`id(x)` — fixed for its lifetime), a type (`type(x)` — decides what it can do) and a value (which may or may not be allowed to change).")
    yield section("Identity, type, value", "id")
    yield code('''
        a = [1, 2, 3]
        b = a                      # a second name for the SAME object
        c = [1, 2, 3]              # a different object with an equal value

        print(a == c, a is c)      # True False
        print(a is b, id(a) == id(b))   # True True
        print(type(a) is list)     # True
    ''')
    yield table(
        ["Question", "Operator / function", "Calls"],
        ["Same value?", "`a == b`", "`a.__eq__(b)` — can be customised"],
        ["Same object?", "`a is b`", "compares identities — can't be overridden"],
        ["Which object?", "`id(a)`", "an integer unique among *live* objects (the address in CPython)"],
        ["What kind?", "`type(a)`, `isinstance(a, T)`", "`isinstance` also accepts subclasses"],
    )
    yield note("Use `is` only for singletons: `x is None`, `x is True`, sentinel objects. For everything else, compare values with `==`.")
    yield section("Small-int cache & string interning", "database")
    yield p("CPython pre-creates the integers −5…256 and reuses (*interns*) many identifier-like strings, so equal values may *happen* to be the same object. That is an implementation detail — never write code whose result depends on it.")
    yield code('''
        import sys

        x = 256
        y = int("256")             # built at run time, still the cached object
        print(x is y)              # True

        big1 = int("1000")
        big2 = int("1000")
        print(big1 == big2, big1 is big2)   # True False

        s1 = "".join(["hello", " ", "world"])     # built at run time: not interned
        s2 = sys.intern("hello world")
        s3 = sys.intern(s1)                       # returns the canonical copy
        print(s1 == s2, s3 is s2)                 # True True
    ''')
    yield warn("`if name is \"admin\":` may work in a REPL test and fail in production. Python 3.8+ even emits a `SyntaxWarning` for `is` with a literal.", "Classic bug")
    yield section("Mutable vs immutable", "lock-open")
    yield table(
        ["Immutable — value can never change", "Mutable — can change in place"],
        ["`int`, `float`, `complex`, `bool`, `str`, `bytes`", "`list`, `dict`, `set`, `bytearray`"],
        ["`tuple`, `frozenset`, `range`, `None`", "most user-defined class instances"],
    )
    yield p("“Changing” an immutable object really creates a **new** object and rebinds the name. Mutating a mutable object is visible through **every** name that refers to it.")
    yield code('''
        s = "hi"
        before = id(s)
        s += "!"                        # new str object, name rebound
        print(id(s) == before)          # False

        nums = [1]
        before = id(nums)
        nums += [2]                     # list.__iadd__ mutates in place
        print(id(nums) == before)       # True
    ''')
    yield note("Hashability follows immutability: `dict` keys and `set` items must be hashable, and a hash is only safe if the value can't change. That's why `tuple` and `frozenset` can be keys but `list` and `set` can't.")
    yield section("Aliasing through function calls", "arrow-right")
    yield code('''
        def add_tax(prices):
            for i in range(len(prices)):
                prices[i] = round(prices[i] * 1.18, 2)     # mutates the caller's list!

        cart = [100, 50]
        add_tax(cart)
        print(cart)                     # [118.0, 59.0]

        def add_tax_safe(prices):
            return [round(p * 1.18, 2) for p in prices]   # new list, input untouched

        cart = [100, 50]
        print(add_tax_safe(cart), cart) # [118.0, 59.0] [100, 50]
    ''')
    yield dodont(
        "Return a new object from functions by default; if you must mutate an argument, say so in the name/docstring (`sort_in_place`) and return `None` like `list.sort`.",
        "Silently mutating arguments the caller still uses — or storing a caller's list inside an object without copying it.",
    )
    yield section("Shallow vs deep copy", "copy")
    yield table(
        ["Way", "Result"],
        ["`b = a`", "No copy — just another name"],
        ["`a[:]`, `list(a)`, `a.copy()`, `dict(d)`, `d.copy()`, `set(s)`", "**Shallow**: new outer container, same inner objects"],
        ["`copy.copy(x)`", "Shallow copy of any object"],
        ["`copy.deepcopy(x)`", "**Deep**: recursively copies everything reachable"],
    )
    yield code('''
        import copy

        config = {"name": "app", "ports": [80, 443]}
        shallow = config.copy()
        deep = copy.deepcopy(config)

        config["name"] = "renamed"          # rebinding a key: only config changes
        config["ports"].append(8080)        # mutating a shared inner list

        print(shallow["name"], shallow["ports"])   # app [80, 443, 8080]
        print(deep["name"], deep["ports"])         # app [80, 443]
    ''')
    yield note("Immutable leaves (`int`, `str`, `tuple` of immutables) are never really copied — sharing them is safe, so `deepcopy` reuses them.")
    yield section("deepcopy handles cycles; `__copy__` / `__deepcopy__`", "recycle")
    yield p("`deepcopy` keeps a *memo* dict of objects already copied, so shared references stay shared and cycles don't recurse forever. Classes can customise copying with `__copy__` and `__deepcopy__(self, memo)`.")
    yield code('''
        import copy

        node = {"name": "a"}
        node["self"] = node                 # a cycle
        clone = copy.deepcopy(node)
        print(clone["self"] is clone, clone is node)   # True False

        shared = [0]
        pair = [shared, shared]
        pair_copy = copy.deepcopy(pair)
        print(pair_copy[0] is pair_copy[1])            # True   ← sharing preserved

        class Session:
            def __init__(self, user, cache):
                self.user, self.cache = user, cache
            def __deepcopy__(self, memo):
                # copy the user data, but share the (expensive) cache
                return Session(copy.deepcopy(self.user, memo), self.cache)

        s = Session({"id": 1}, cache={"big": "data"})
        t = copy.deepcopy(s)
        print(t.user == s.user, t.user is s.user, t.cache is s.cache)   # True False True
    ''')
    yield section("Puzzle: a tuple that changes", "puzzle")
    yield code('''
        t = ([1, 2], "x")
        try:
            t[0] += [3]                    # list.__iadd__ runs, THEN tuple item assignment fails
        except TypeError as e:
            print(type(e).__name__)        # TypeError
        print(t)                           # ([1, 2, 3], 'x')
    ''')
    yield p("`t[0] += [3]` is `t[0] = t[0].__iadd__([3])`: the list is extended in place first, then storing it back into the tuple raises. The error is real — and so is the mutation.")
    yield qa("What is the difference between `is` and `==`?",
             "`==` asks whether two objects have equal **values** (it calls `__eq__`). `is` asks whether two names refer to the **same object** (identical `id`). Use `is` for `None` and other singletons, `==` for everything else.")
    yield qa("Why does `a is b` return True for 256 but False for 1000?",
             "CPython caches small integers from −5 to 256, so every 256 is the same object. Larger ints created at run time are separate objects. It's an implementation detail — compare numbers with `==`.")
    yield qa("When do you need a deep copy?",
             "When the object contains **mutable** inner objects (lists of lists, dicts of lists, objects holding lists) and you want the copy to be fully independent. A shallow copy is enough for a flat list of immutable values.")


@topic(G, "sorting", "Sorting & Custom Ordering", "sort-ascending")
def _():
    yield lead("Python's sort is fast (Timsort), **stable**, and customised with a `key` function — rarely with a comparator. Master `key=` and most ordering problems become one line.")
    yield section("`sorted()` vs `list.sort()`", "arrows-sort")
    yield code('''
        nums = [5, 2, 9, 1]
        print(sorted(nums), nums)          # [1, 2, 5, 9] [5, 2, 9, 1]
        result = nums.sort(reverse=True)   # in place
        print(result, nums)                # None [9, 5, 2, 1]
        print(sorted("hello"))             # ['e', 'h', 'l', 'l', 'o']
        print(sorted({"b": 1, "a": 2}))    # ['a', 'b']   ← iterating a dict gives keys
    ''')
    yield table(
        ["", "`sorted(iterable)`", "`lst.sort()`"],
        ["Works on", "Any iterable (str, dict, set, generator…)", "Lists only"],
        ["Returns", "A **new** list", "`None` — sorts in place"],
        ["Memory", "Copies the data", "No extra list"],
        ["Options", "`key=`, `reverse=`", "`key=`, `reverse=`"],
    )
    yield warn("`xs = xs.sort()` sets `xs` to `None`. Either `xs.sort()` or `xs = sorted(xs)`.")
    yield section("The `key` function", "key")
    yield p("`key` is called **once per item**; items are ordered by those computed keys. Any callable works: a built-in, a method, a lambda, an `operator` helper.")
    yield code('''
        words = ["banana", "Apple", "fig", "cherry"]
        print(sorted(words))                           # ['Apple', 'banana', 'cherry', 'fig']
        print(sorted(words, key=str.lower))            # ['Apple', 'banana', 'cherry', 'fig']
        print(sorted(words, key=len))                  # ['fig', 'Apple', 'banana', 'cherry']
        print(sorted(words, key=lambda w: w[-1]))      # ['banana', 'Apple', 'fig', 'cherry']
        print(sorted([-4, 1, -2, 3], key=abs))         # [1, -2, 3, -4]
    ''')
    yield note("Uppercase letters sort before lowercase (`'Z' < 'a'`) because strings compare by code point. Use `key=str.lower` (or `str.casefold` for full Unicode) for human order.")
    yield section("Multi-level ordering", "list-numbers")
    yield p("Return a **tuple** from the key: ties on the first element fall through to the second. Negate numbers to flip one level to descending.")
    yield code('''
        students = [("asha", 90, 21), ("ravi", 85, 22), ("kiran", 90, 20), ("meera", 85, 20)]

        # marks descending, then name ascending
        print([s[0] for s in sorted(students, key=lambda s: (-s[1], s[0]))])
        # ['asha', 'kiran', 'meera', 'ravi']
    ''', check=False)
    yield output("['asha', 'kiran', 'meera', 'ravi']")
    yield p("Can't negate a string? Use **stability**: sort by the secondary key first, then by the primary key. Each pass keeps the previous order among ties.")
    yield code('''
        people = [("asha", "dev"), ("ravi", "ops"), ("kiran", "dev"), ("meera", "ops")]
        by_name_desc = sorted(people, key=lambda p: p[0], reverse=True)   # secondary first
        result = sorted(by_name_desc, key=lambda p: p[1])                 # then primary
        print(result)   # [('kiran', 'dev'), ('asha', 'dev'), ('ravi', 'ops'), ('meera', 'ops')]
    ''')
    yield define("Stable sort", "items with equal keys keep their original relative order. Python's sort is guaranteed stable, which makes multi-pass sorting correct.")
    yield section("`operator.itemgetter` & `attrgetter`", "settings")
    yield code('''
        from operator import itemgetter, attrgetter
        from dataclasses import dataclass

        rows = [{"name": "ravi", "age": 30}, {"name": "asha", "age": 25}]
        print([r["name"] for r in sorted(rows, key=itemgetter("age"))])   # ['asha', 'ravi']

        pairs = [(2, "b"), (1, "z"), (2, "a")]
        print(sorted(pairs, key=itemgetter(0, 1)))    # [(1, 'z'), (2, 'a'), (2, 'b')]

        @dataclass
        class Emp:
            name: str
            salary: int

        staff = [Emp("a", 50), Emp("b", 70), Emp("c", 60)]
        print([e.name for e in sorted(staff, key=attrgetter("salary"), reverse=True)])   # ['b', 'c', 'a']
    ''')
    yield section("Sorting dict items", "book-2")
    yield code('''
        scores = {"asha": 91, "ravi": 78, "kiran": 91, "zoe": 85}

        top = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        print(top[:3])                        # [('asha', 91), ('kiran', 91), ('zoe', 85)]
        print(dict(sorted(scores.items())))   # {'asha': 91, 'kiran': 91, 'ravi': 78, 'zoe': 85}
        print(max(scores, key=scores.get))    # asha   ← first max wins
    ''')
    yield section("Comparators with `cmp_to_key`", "arrows-exchange")
    yield p("When the order can't be expressed as a key — it depends on *both* items together — write a comparator returning negative / zero / positive and wrap it with `functools.cmp_to_key`.")
    yield code('''
        from functools import cmp_to_key

        def largest_number(nums):
            """Arrange numbers to form the largest possible number."""
            strs = [str(n) for n in nums]
            def cmp(a, b):
                if a + b > b + a:
                    return -1          # a goes first
                if a + b < b + a:
                    return 1
                return 0
            strs.sort(key=cmp_to_key(cmp))
            result = "".join(strs)
            return "0" if result[0] == "0" else result

        print(largest_number([3, 30, 34, 5, 9]))   # 9534330
        print(largest_number([0, 0]))              # 0
    ''')
    yield section("Natural sort & custom objects", "abc")
    yield code('''
        import re

        files = ["file10.txt", "file2.txt", "file1.txt"]
        print(sorted(files))     # ['file1.txt', 'file10.txt', 'file2.txt']

        def natural_key(s):
            return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\\d+)", s)]

        print(sorted(files, key=natural_key))   # ['file1.txt', 'file2.txt', 'file10.txt']

        class Task:
            def __init__(self, pri, name):
                self.pri, self.name = pri, name
            def __lt__(self, other):             # sort() only needs <
                return self.pri < other.pri
            def __repr__(self):
                return self.name

        print(sorted([Task(3, "c"), Task(1, "a"), Task(2, "b")]))   # [a, b, c]
    ''')
    yield section("min, max, heapq & bisect take a key too", "binary")
    yield code('''
        import heapq, bisect

        words = ["kiwi", "banana", "fig", "apple"]
        print(min(words, key=len), max(words, key=len))       # fig banana
        print(heapq.nsmallest(2, words, key=len))             # ['fig', 'kiwi']
        print(max([], default="empty"))                       # empty

        records = [(1, "a"), (4, "b"), (9, "c")]              # sorted by first field
        print(bisect.bisect_left(records, 5, key=lambda r: r[0]))   # 2   ← key= needs 3.10+
    ''')
    yield table(
        ["Need", "Best tool", "Cost"],
        ["Full order", "`sorted` / `.sort`", "O(n log n)"],
        ["Just the min or max", "`min` / `max`", "O(n)"],
        ["Top k (k small)", "`heapq.nsmallest` / `nlargest`", "O(n log k)"],
        ["Keep a list sorted while inserting", "`bisect.insort`", "O(log n) search + O(n) insert"],
    )
    yield section("Timsort facts & pitfalls", "info-circle")
    yield cards(
        ("Timsort", "Hybrid merge + insertion sort. O(n log n) worst case, **O(n)** on already-sorted or reversed data — it detects natural runs.", "bolt"),
        ("Stable", "Guaranteed. Equal keys keep their input order.", "anchor"),
        ("Mixed types", "`sorted([1, 'a'])` raises `TypeError` — Python 3 won't compare unrelated types.", "alert-triangle"),
        ("Key once", "Keys are computed once per item (decorate-sort-undecorate), so an expensive key is still only n calls.", "clock"),
    )
    yield code('''
        try:
            sorted([3, "a", 1])
        except TypeError as e:
            print(e)   # '<' not supported between instances of 'str' and 'int'
        print(sorted([3, None, 1], key=lambda x: (x is None, x or 0)))   # [1, 3, None]
    ''')
    yield qa("How do you sort by one field descending and another ascending?",
             "Use a tuple key and negate the numeric field: `key=lambda r: (-r.score, r.name)`. If the descending field isn't numeric, rely on stability: sort by the secondary key first, then by the primary key with `reverse=True`.")
    yield qa("Is Python's sort stable, and why does it matter?",
             "Yes — Timsort is stable. Equal elements keep their relative order, which lets you sort in multiple passes (secondary key first) and get a correct multi-key ordering.")
    yield qa("When would you use `cmp_to_key`?",
             "When ordering depends on comparing two items together and can't be turned into a per-item key — e.g. \"largest number\" (compare `a+b` with `b+a`). Otherwise a key function is simpler and faster.")


@topic(G, "stdlib-ds", "collections, heapq & bisect", "stack-3")
def _():
    yield lead("The standard-library data structures that turn O(n) interview solutions into O(1) or O(log n) ones.")
    yield section("deque — double-ended queue", "arrows-horizontal")
    yield p("O(1) appends and pops at **both** ends. Use it for queues (BFS) and sliding windows; a list's `pop(0)` is O(n).")
    yield code('''
        from collections import deque
        q = deque([1, 2, 3])
        q.appendleft(0); q.append(4)
        print(q.popleft(), q.pop(), list(q))    # 0 4 [1, 2, 3]
        window = deque(maxlen=3)                # keeps only the last 3 items
        for x in range(6):
            window.append(x)
        print(list(window))                     # [3, 4, 5]
    ''')
    yield section("Counter & defaultdict", "chart-bar")
    yield code('''
        from collections import Counter, defaultdict
        c = Counter("mississippi")
        print(c.most_common(2))                  # [('i', 4), ('s', 4)]
        # Missing keys count as zero instead of raising KeyError:
        print(c["z"])                            # 0

        graph = defaultdict(list)                # missing key → new empty list
        for u, v in [("a", "b"), ("a", "c"), ("b", "c")]:
            graph[u].append(v)
        print(dict(graph))                       # {'a': ['b', 'c'], 'b': ['c']}

        groups = defaultdict(list)
        for w in ["eat", "tea", "tan", "ate"]:
            groups["".join(sorted(w))].append(w)
        print(list(groups.values()))             # [['eat', 'tea', 'ate'], ['tan']]
    ''')
    yield section("heapq — priority queue", "stack-pop")
    yield p("A **min-heap** stored in a plain list: `heappush` / `heappop` are O(log n), `heap[0]` is the minimum in O(1).")
    yield code('''
        import heapq
        nums = [5, 1, 8, 3, 2]
        heapq.heapify(nums)                       # O(n)
        heapq.heappush(nums, 0)
        print(heapq.heappop(nums), nums[0])       # 0 1
        print(heapq.nlargest(2, [5, 1, 8, 3]))    # [8, 5]

        max_heap = []                             # no max-heap: store negatives
        for x in [5, 1, 8]:
            heapq.heappush(max_heap, -x)
        print(-heapq.heappop(max_heap))           # 8

        tasks = [(2, "write"), (1, "plan"), (3, "ship")]
        heapq.heapify(tasks)                      # tuples compare by first item
        print(heapq.heappop(tasks))               # (1, 'plan')
    ''')
    yield warn("If priorities tie, tuples fall back to comparing the next item — which may not be comparable. Add a counter: `(priority, count, item)`.")
    yield section("bisect — binary search on sorted lists", "binary")
    yield code('''
        import bisect
        xs = [1, 3, 3, 5, 8]
        print(bisect.bisect_left(xs, 3), bisect.bisect_right(xs, 3))   # 1 3
        bisect.insort(xs, 4)                                          # insert, keep sorted
        print(xs)                                                     # [1, 3, 3, 4, 5, 8]
    ''')
    yield table(
        ["Need", "Use", "Key operations"],
        ["FIFO queue / BFS", "`deque`", "`append`, `popleft` — O(1)"],
        ["Counting", "`Counter`", "`most_common(k)`, arithmetic between counters"],
        ["Grouping / adjacency list", "`defaultdict(list)`", "auto-creates missing keys"],
        ["k smallest / Dijkstra / scheduling", "`heapq`", "`heappush`, `heappop` — O(log n)"],
        ["Search in sorted data", "`bisect`", "`bisect_left` — O(log n)"],
        ["LRU-style ordering", "`OrderedDict`", "`move_to_end`, `popitem(last=False)`"],
    )


@topic(G, "collections-more", "More collections: namedtuple, OrderedDict, ChainMap", "box-multiple")
def _():
    yield lead("The rest of the `collections` toolbox — lightweight records, counting arithmetic, order-aware dicts, layered lookups — plus when to use each.")
    yield section("namedtuple — a tuple with field names", "tag")
    yield code('''
        from collections import namedtuple

        Point = namedtuple("Point", ["x", "y"])
        p = Point(3, 4)
        x, y = p                             # still a tuple: unpacking, indexing, hashing
        print(p.x, p[1], x + y)              # 3 4 7
        print(p._replace(x=10), p)           # Point(x=10, y=4) Point(x=3, y=4)
        print(p._asdict())                   # {'x': 3, 'y': 4}
        print(Point._fields)                 # ('x', 'y')
        print(Point._make([5, 6]))           # Point(x=5, y=6)

        Conn = namedtuple("Conn", "host port timeout", defaults=[30])
        print(Conn("db", 5432))              # Conn(host='db', port=5432, timeout=30)
    ''')
    yield p("`typing.NamedTuple` is the class-syntax version — same runtime behaviour, but with type hints, docstrings and methods.")
    yield code('''
        from typing import NamedTuple

        class Employee(NamedTuple):
            name: str
            dept: str = "eng"

            def badge(self) -> str:
                return f"{self.name}@{self.dept}"

        e = Employee("asha")
        print(e, e.badge())          # Employee(name='asha', dept='eng') asha@eng
        try:
            e.name = "ravi"
        except AttributeError:
            print("immutable")       # immutable
    ''')
    yield table(
        ["", "`namedtuple` / `NamedTuple`", "`@dataclass`", "`dict`"],
        ["Mutable", "No", "Yes (or `frozen=True`)", "Yes"],
        ["Access", "`p.x` and `p[0]`", "`p.x`", "`p['x']`"],
        ["Hashable", "Yes", "Only if frozen", "No"],
        ["Best for", "Small immutable records, returning several values", "Rich objects with defaults & methods", "Dynamic / JSON-like data"],
    )
    yield section("Counter — counting with arithmetic", "chart-bar")
    yield code('''
        from collections import Counter

        inventory = Counter(apple=3, pear=1)
        inventory.update(["apple", "kiwi"])          # add counts
        print(inventory)                             # Counter({'apple': 4, 'pear': 1, 'kiwi': 1})
        inventory.subtract({"pear": 2})              # can go negative
        print(inventory["pear"], inventory.total())  # -1 4

        a, b = Counter("aabbc"), Counter("abd")
        print(a + b)          # Counter({'a': 3, 'b': 3, 'c': 1, 'd': 1})
        print(a - b)          # Counter({'a': 1, 'b': 1, 'c': 1})   ← drops counts <= 0
        print(a & b)          # Counter({'a': 1, 'b': 1})           ← min of each
        print(sorted(Counter(x=2, y=1).elements()))   # ['x', 'x', 'y']
    ''')
    yield note("A `Counter` is a `dict` subclass: missing keys read as `0`, and `+`, `-`, `&`, `|` combine counters. `most_common(k)` gives the top k.")
    yield section("defaultdict variations", "folders")
    yield code('''
        from collections import defaultdict

        seen_first = defaultdict(lambda: "unknown")     # any zero-arg callable
        print(seen_first["x"])                          # unknown

        def tree():
            return defaultdict(tree)                    # infinitely nested dict
        t = tree()
        t["india"]["ts"]["hyd"] = 1
        print(t["india"]["ts"]["hyd"], "ap" in t["india"])   # 1 False

        totals = defaultdict(int)
        for dept, amount in [("eng", 5), ("ops", 2), ("eng", 3)]:
            totals[dept] += amount
        print(dict(totals))                              # {'eng': 8, 'ops': 2}
    ''')
    yield warn("Merely *reading* `d[missing]` on a `defaultdict` inserts the key. Use `key in d` or `d.get(key)` when you only want to check.")
    yield section("OrderedDict — order you can manipulate", "arrows-sort")
    yield p("Plain dicts keep insertion order since 3.7, so `OrderedDict` is now for its extras: `move_to_end`, `popitem(last=False)`, and order-sensitive equality.")
    yield code('''
        from collections import OrderedDict

        a = OrderedDict(x=1, y=2)
        b = OrderedDict(y=2, x=1)
        print(a == b, dict(a) == dict(b))     # False True   ← OrderedDict compares order

        a.move_to_end("x")                    # x becomes the newest
        print(list(a))                        # ['y', 'x']
        print(a.popitem(last=False))          # ('y', 2)   ← FIFO pop of the oldest
    ''')
    yield code('''
        from collections import OrderedDict

        class LRUCache:
            def __init__(self, capacity):
                self.capacity = capacity
                self.data = OrderedDict()

            def get(self, key):
                if key not in self.data:
                    return -1
                self.data.move_to_end(key)            # mark as recently used
                return self.data[key]

            def put(self, key, value):
                self.data[key] = value
                self.data.move_to_end(key)
                if len(self.data) > self.capacity:
                    self.data.popitem(last=False)     # evict least recently used

        cache = LRUCache(2)
        cache.put(1, "a"); cache.put(2, "b")
        cache.get(1)                                  # 1 is now most recent
        cache.put(3, "c")                             # evicts 2
        print(list(cache.data), cache.get(2))         # [1, 3] -1
    ''', caption="Python — LRU cache (a classic interview question)")
    yield section("ChainMap — layered lookups", "stack-2")
    yield p("`ChainMap(a, b, c)` searches several dicts in order **without copying** them. Writes go to the first map. Perfect for defaults → config file → environment → command-line layering, or nested scopes.")
    yield code('''
        from collections import ChainMap

        defaults = {"theme": "light", "lang": "en", "debug": False}
        user = {"theme": "dark"}
        cli = {"debug": True}

        settings = ChainMap(cli, user, defaults)
        print(settings["theme"], settings["lang"], settings["debug"])   # dark en True

        settings["lang"] = "te"                  # written to the first map (cli)
        print(cli, defaults["lang"])             # {'debug': True, 'lang': 'te'} en

        scope = ChainMap({"x": 1})
        inner = scope.new_child({"x": 2})        # push a new scope
        print(inner["x"], inner.parents["x"])    # 2 1
    ''')
    yield section("UserDict & UserList — safe subclassing", "user-cog")
    yield p("Subclassing `dict` directly is tricky: `update()` and the constructor bypass your overridden `__setitem__`. `UserDict` stores the data in `self.data` and routes every write through your methods.")
    yield code('''
        from collections import UserDict

        class LowerDict(dict):
            def __setitem__(self, k, v):
                super().__setitem__(k.lower(), v)

        class LowerUserDict(UserDict):
            def __setitem__(self, k, v):
                super().__setitem__(k.lower(), v)

        print(LowerDict({"A": 1}))                    # {'A': 1}   ← override bypassed!
        print(LowerUserDict({"A": 1}).data)           # {'a': 1}
    ''')
    yield section("Two more handy containers", "package")
    yield code('''
        from array import array
        from types import SimpleNamespace

        nums = array("i", [1, 2, 3])        # compact typed array of C ints
        nums.append(4)
        print(nums.tolist(), nums.itemsize) # [1, 2, 3, 4] 4

        cfg = SimpleNamespace(host="localhost", port=8000)   # attribute bag
        cfg.debug = True
        print(cfg.port, cfg)   # 8000 namespace(host='localhost', port=8000, debug=True)
    ''')
    yield section("Choosing the right container", "checklist")
    yield table(
        ["Need", "Use"],
        ["Immutable record with named fields", "`namedtuple` / `typing.NamedTuple`"],
        ["Count things, combine counts", "`Counter`"],
        ["Group values / auto-create missing entries", "`defaultdict`"],
        ["Reorder keys, LRU cache, FIFO dict", "`OrderedDict`"],
        ["Look up through several dicts in priority order", "`ChainMap`"],
        ["Queue / sliding window", "`deque`"],
        ["Custom dict/list behaviour", "`UserDict` / `UserList`"],
        ["Millions of numbers, low memory", "`array` (or NumPy)"],
        ["Quick attribute bag", "`types.SimpleNamespace`"],
    )
    yield qa("Why use `OrderedDict` now that `dict` preserves insertion order?",
             "For its extra behaviour: `move_to_end`, `popitem(last=False)` (FIFO) and equality that takes order into account. It's the idiomatic base for an LRU cache.")
    yield qa("Implement an LRU cache in O(1) per operation.",
             "Use an `OrderedDict`: on `get`, `move_to_end(key)`; on `put`, insert, `move_to_end`, and if over capacity `popitem(last=False)`. Under the hood this is a hash map plus a doubly linked list — the same design you'd write by hand in Java or C++. For caching function results, `functools.lru_cache` does it for you.")
    yield qa("namedtuple or dataclass?",
             "`namedtuple` for small, immutable, tuple-compatible records (unpacking, hashing, low memory). `dataclass` when you need mutability, default factories, validation in `__post_init__` or many methods.")
