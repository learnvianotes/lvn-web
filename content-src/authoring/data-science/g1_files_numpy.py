from kit import *

G = "Working with Files"


@topic(G, "files", "Reading & Writing Files", "file-text")
def _():
    yield lead("Most data science starts with a file. Python's built-in `open()` reads and writes text files — and a few string methods already give you basic text statistics.")
    yield define("File object", "what `open(path, mode)` returns: a handle with `read`, `readline`, `readlines`, `write` and `seek`. Always close it — or better, use `with`, which closes it for you.")
    yield section("Modes", "adjustments")
    yield table(
        ["Mode", "Meaning", "If the file exists", "If it doesn't"],
        ["`'r'`", "Read (default)", "Reads from the start", "`FileNotFoundError`"],
        ["`'w'`", "Write", "**Erases** it first", "Creates it"],
        ["`'a'`", "Append", "Writes at the end", "Creates it"],
        ["`'r+'`", "Read and write", "Starts at the beginning", "`FileNotFoundError`"],
        ["`'x'`", "Create only", "`FileExistsError`", "Creates it"],
    )
    yield section("Writing: write vs writelines", "pencil")
    yield code('''
        lines = ["This is Delhi \\n", "This is Paris \\n", "This is London \\n"]
        with open("myfile.txt", "w", encoding="utf-8") as f:
            f.write("Hello \\n")          # one string
            f.writelines(lines)          # an iterable of strings (no newlines are added for you)

        with open("myfile.txt", encoding="utf-8") as f:
            print(f.read())
    ''', check=False)
    yield shell('''
        Hello
        This is Delhi
        This is Paris
        This is London
    ''', caption="Output")
    yield section("Reading: read, readline, readlines, seek", "book")
    yield code('''
        with open("myfile.txt", encoding="utf-8") as f:
            print(repr(f.read(9)))       # 'Hello \\nTh'   ← 9 characters, across lines
            f.seek(0)                    # jump back to the start
            print(repr(f.readline()))    # 'Hello \\n'     ← up to and including the newline
            f.seek(0)
            print(f.readlines())         # ['Hello \\n', 'This is Delhi \\n', 'This is Paris \\n', 'This is London \\n']
    ''', check=False)
    yield table(
        ["Method", "Returns"],
        ["`f.read()` / `f.read(n)`", "The whole file / the next `n` characters, as one string"],
        ["`f.readline()`", "The next line, including its `\\n`"],
        ["`f.readlines()`", "A list of all remaining lines"],
        ["`for line in f:`", "Lines one at a time — memory-friendly for big files"],
        ["`f.seek(n)`", "Moves the position to byte `n` (0 = start)"],
    )
    yield section("Append vs write", "file-plus")
    yield code('''
        with open("notes.txt", "w") as f:
            f.write("Today \\n")
        with open("notes.txt", "a") as f:        # append keeps what was there
            f.write("Tomorrow \\n")
        with open("notes.txt") as f:
            print(f.readlines())                  # ['Today \\n', 'Tomorrow \\n']

        with open("notes.txt", "w") as f:        # write erases it first
            f.write("Only this \\n")
        with open("notes.txt") as f:
            print(f.readlines())                  # ['Only this \\n']
    ''')
    yield warn("Opening with `'w'` silently wipes the file. Use `'a'` to add to it, or `'x'` to refuse overwriting.")
    yield section("Quick text statistics", "chart-bar")
    yield code('''
        text = """Data science turns raw data into insight. It mixes statistics and programming.

        Python is the most popular language for it."""

        paragraphs = [p for p in text.split("\\n\\n") if p.strip()]
        sentences = [s for s in text.replace("\\n", " ").split(".") if s.strip()]
        words = text.split()                     # split() with no argument handles any whitespace

        print(len(paragraphs), len(sentences), len(words))   # 2 3 20
    ''')
    yield note("`split(\" \")` counts empty strings between double spaces and keeps newlines inside words — `split()` with no argument is almost always what you want for words.")
    yield section("Cleaning unwanted characters", "eraser")
    yield code('''
        raw = "Hello!! World@ #2026 [7] [12]"
        for ref in [f"[{i}]" for i in range(1, 20)]:     # remove citation markers like [7]
            raw = raw.replace(ref, "")
        for ch in "!@#":                                 # remove unwanted symbols
            raw = raw.replace(ch, "")
        print(" ".join(raw.split()))                     # Hello World 2026
    ''')
    yield note("For anything more than a few characters, a regular expression is cleaner: `re.sub(r\"\\[\\d+\\]|[!@#]\", \"\", raw)` — see *Regular Expressions*.")


@topic(G, "os-module", "Files & Folders with os", "folders")
def _():
    yield lead("The `os` module talks to the operating system: where you are, what's in a folder, and creating, renaming or removing directories — the plumbing behind organising datasets.")
    yield section("Where am I?", "map-pin")
    yield code('''
        import os
        start = os.getcwd()              # current working directory
        os.mkdir("project")              # create one folder
        os.chdir("project")              # move into it
        print(os.path.basename(os.getcwd()))   # project
        os.chdir("..")                   # back to the parent
        print(os.getcwd() == start)      # True
    ''')
    yield table(
        ["Function", "Does"],
        ["`os.getcwd()`", "Current working directory"],
        ["`os.chdir(path)`", "Change directory (`..` = parent)"],
        ["`os.listdir(path='.')`", "Names of files and folders in a directory"],
        ["`os.mkdir(path)`", "Create **one** folder (parent must exist)"],
        ["`os.makedirs(path, exist_ok=True)`", "Create a whole chain of folders"],
        ["`os.rmdir(path)`", "Remove an **empty** folder"],
        ["`os.rename(old, new)`", "Rename or move"],
        ["`os.remove(path)`", "Delete a file"],
        ["`os.path.join(a, b)`", "Build a path with the right separator"],
        ["`os.path.exists(p)` / `isdir` / `isfile`", "Check what's there"],
    )
    yield section("Nested folders", "folder")
    yield code('''
        import os
        os.makedirs("data/raw/2026", exist_ok=True)     # creates data, data/raw and data/raw/2026
        os.rmdir("data/raw/2026")                       # only works because it's empty
        os.rename("data", "dataset")
        print(sorted(os.listdir("dataset")))            # ['raw']
    ''')
    yield warn("`os.rmdir` refuses non-empty folders. To delete a whole tree use `shutil.rmtree(path)` — carefully: there's no recycle bin.")
    yield section("Creating folders in bulk", "copy")
    yield code('''
        import os
        master = "KT"
        n, m = 5, 5
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                os.makedirs(os.path.join(master, f"{master} {i}", f"{master} {i}.{j}"), exist_ok=True)

        total = sum(len(dirs) for _, dirs, _ in os.walk(master)) + 1   # + the master folder itself
        print(total)                                                    # 31
    ''')
    yield note("That's the notebook's `n*m + n + 1` = 5×5 + 5 + 1 folders. `os.walk(top)` yields `(folder, subfolders, files)` for every folder under `top`.")
    yield section("Reading many text files", "files")
    yield code('''
        import os
        os.makedirs("Files", exist_ok=True)
        for name, text in [("a.txt", "first"), ("b.txt", "second"), (".DS_Store", "junk")]:
            with open(os.path.join("Files", name), "w") as f:
                f.write(text)

        contents = []
        for name in sorted(os.listdir("Files")):
            if name.startswith("."):                    # skip hidden files like .DS_Store
                continue
            with open(os.path.join("Files", name)) as f:
                contents.append(f.read())
        print(contents)                                 # ['first', 'second']
    ''')
    yield note("Modern alternative: `pathlib` — `[p.read_text() for p in Path(\"Files\").glob(\"*.txt\")]` does the same in one line.", "Tip")


G = "NumPy"


@topic(G, "numpy-arrays", "NumPy Arrays", "grid-dots")
def _():
    yield lead("NumPy's `ndarray` stores numbers in one contiguous block of memory with a single type — which makes maths on millions of values fast and concise.")
    yield define("ndarray", "an N-dimensional array of values that all share one `dtype`. Operations apply to every element at once (*vectorisation*), running in C instead of a Python loop.")
    yield section("List vs array", "arrows-exchange")
    yield code('''
        import numpy as np
        l = [2, 3, 4, 5]
        arr = np.array(l)
        print(l, type(l).__name__)            # [2, 3, 4, 5] list
        print(arr, type(arr).__name__)        # [2 3 4 5] ndarray
        print(l * 2)                          # [2, 3, 4, 5, 2, 3, 4, 5]
        print(arr * 2)                        # [ 4  6  8 10]
    ''')
    yield note("`list * 2` repeats the list; `array * 2` multiplies every element. That difference is the whole point of NumPy.")
    yield section("Shape, size and type", "ruler")
    yield code('''
        import numpy as np
        a = np.array([2, 3, 4, 5])
        b = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        print(a.ndim, b.ndim)           # 1 2
        print(b.shape, b.size)          # (2, 4) 8
        print(b.dtype)                  # int64
    ''')
    yield table(
        ["Attribute", "Meaning", "For `b` above"],
        ["`ndim`", "Number of dimensions (axes)", "`2`"],
        ["`shape`", "Length along each axis — (rows, columns)", "`(2, 4)`"],
        ["`size`", "Total number of elements", "`8`"],
        ["`dtype`", "Element type", "`int64`"],
    )
    yield section("Creating arrays", "plus")
    yield code('''
        import numpy as np
        print(np.zeros(3, dtype=int))                # [0 0 0]
        print(np.ones((2, 2), dtype=int))            # [[1 1]
                                                     #  [1 1]]
        print(np.arange(4, 20, 3))                   # [ 4  7 10 13 16 19]
        print(np.linspace(2.0, 3.0, num=5))          # [2.   2.25 2.5  2.75 3.  ]
        print(np.full(3, 7))                         # [7 7 7]
        print(np.eye(2, dtype=int))                  # [[1 0]
                                                     #  [0 1]]
    ''', check=False)
    yield table(
        ["Function", "Gives", "Note"],
        ["`np.zeros(shape)` / `np.ones(shape)`", "All 0s / all 1s", "Float by default — pass `dtype=int` for ints"],
        ["`np.arange(start, stop, step)`", "Evenly spaced by **step**", "Like `range`; `stop` excluded"],
        ["`np.linspace(start, stop, num)`", "Exactly **num** points", "`stop` included by default"],
        ["`np.full(shape, v)`", "All `v`", ""],
        ["`np.eye(n)`", "Identity matrix", ""],
    )
    yield section("Random numbers", "dice")
    yield code('''
        import numpy as np
        rng = np.random.default_rng(seed=42)       # the modern API; a seed makes results repeatable
        print(rng.random(3).round(3))              # [0.774 0.439 0.859]
        print(rng.integers(1, 7, size=5))          # [1 5 2 1 4]
        print(rng.normal(0, 1, size=2).round(3))   # [ 0.128 -0.316]
    ''')
    yield note("The notebook uses `np.random.random(3)` — the older API. Both work; `default_rng` is recommended, and **seeding** matters whenever results must be reproducible (experiments, tests).")
    yield section("reshape", "transform")
    yield code('''
        import numpy as np
        arr = np.arange(10)
        print(arr.reshape(2, 5))        # [[0 1 2 3 4]
                                        #  [5 6 7 8 9]]
        print(arr.reshape(5, -1).shape) # (5, 2)   ← -1 means "work it out"
        print(np.arange(16).reshape(2, 8, 1).shape)   # (2, 8, 1)
    ''', check=False)
    yield warn("The new shape must hold exactly the same number of elements: `np.arange(10).reshape(3, 3)` raises `ValueError`.")


@topic(G, "numpy-operations", "Array Operations", "math")
def _():
    yield lead("Arithmetic, aggregation, sorting, joining, splitting and filtering — all without writing a loop.")
    yield section("Element-wise arithmetic", "math-symbols")
    yield code('''
        import numpy as np
        a = np.array([1, 2, 3, 4])
        b = np.array([5, 6, 7, 8])
        print(a + 2, a * 2, a / 2)        # [3 4 5 6] [2 4 6 8] [0.5 1.  1.5 2. ]
        print(a + b, b - a)               # [ 6  8 10 12] [4 4 4 4]
        print(np.add(1, b), np.multiply(a, b))   # [6 7 8 9] [ 5 12 21 32]
    ''')
    yield note("Combining an array with a single number (or arrays of compatible shapes) is called **broadcasting** — the number is applied to every element.")
    yield section("Aggregations and axes", "sum")
    yield code('''
        import numpy as np
        m = np.array([[1, 4, 2],
                      [3, 4, 6]])
        print(m.max(), m.min(), m.sum())      # 6 1 20
        print(m.max(axis=0))                  # [3 4 6]   ← down each column
        print(m.max(axis=1))                  # [4 6]     ← across each row
        print(m.mean(axis=1))                 # [2.33333333 4.33333333]
    ''')
    yield cards(
        ("`axis=0`", "Collapse the rows — one result **per column**.", "arrow-down"),
        ("`axis=1`", "Collapse the columns — one result **per row**.", "arrow-right"),
    )
    yield section("Sorting", "sort-ascending")
    yield code('''
        import numpy as np
        arr = np.array([[1, 4, 2], [3, 4, 6], [0, -1, 5]])
        print(np.sort(arr))                   # sorts each row (axis=-1 by default)
        print(np.sort(arr, axis=0))           # sorts each column
    ''', check=False)
    yield shell('''
        [[ 1  2  4]
         [ 3  4  6]
         [-1  0  5]]
        [[ 0 -1  2]
         [ 1  4  5]
         [ 3  4  6]]
    ''', caption="Output")
    yield note("`kind=\"quicksort\" | \"mergesort\" | \"stable\"` picks the algorithm; the result is the same, only speed and stability (order of equal elements) differ.")
    yield section("Joining and splitting", "arrows-join")
    yield code('''
        import numpy as np
        a = np.array([1, 2, 3, 4])
        b = np.array([5, 6, 7, 8])
        print(np.vstack((a, b)).shape)        # (2, 4)   ← stacked as rows
        print(np.hstack((a, b)))              # [1 2 3 4 5 6 7 8]
        m = np.array([[1, 2], [3, 4]])
        print(np.concatenate((m, m), axis=0).shape)   # (4, 2)
        top, bottom = np.vsplit(np.vstack((a, b)), 2)
        left, right = np.hsplit(np.vstack((a, b)), 2)
        print(top, right[1])                  # [[1 2 3 4]] [7 8]
    ''')
    yield section("Slicing and boolean filtering", "cut")
    yield code('''
        import numpy as np
        arr = np.array([1, 2, 3, 4, 5, 6, 7])
        print(arr[1:5], arr[1:5:2], arr[-3:-1], arr[::2])   # [2 3 4 5] [2 4] [5 6] [1 3 5 7]

        nums = np.arange(1, 40)
        print(nums[nums > 35])                  # [36 37 38 39]
        print(nums[(nums % 10 == 0)])           # [10 20 30]
        m = np.arange(12).reshape(3, 4)
        print(m[1], m[:, 2], m[1:, :2].tolist())   # [4 5 6 7] [ 2  6 10] [[4, 5], [8, 9]]
    ''')
    yield note("The notebook labels slicing “DAP (Distributed Array Protocol)” — that's unrelated. Slicing is plain `start:stop:step` indexing, per axis, separated by commas.", "Correction")
    yield warn("A slice of a NumPy array is a **view** — changing it changes the original. Use `.copy()` when you need an independent array. (List slices, by contrast, are copies.)")
    yield dodont(
        "Replace Python loops over numbers with vectorised expressions: `arr[arr > 2]`, `arr * 2`, `arr.sum()`.",
        "Building NumPy arrays by appending in a loop — collect into a list first, then call `np.array(list)` once.",
    )
