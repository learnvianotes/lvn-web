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
