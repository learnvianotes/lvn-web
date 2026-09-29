from kit import *

G = "Concurrency"


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
    yield section("Concurrency vs parallelism", "arrows-split")
    yield cards(
        ("Concurrency", "*Dealing* with many things at once: tasks make progress in overlapping time periods, possibly by taking turns on one core. Threads under the GIL and `asyncio` give you this.", "arrows-shuffle"),
        ("Parallelism", "*Doing* many things at once: tasks literally run at the same instant on different cores. In CPython that means processes (or a free-threaded build, or C extensions that release the GIL).", "layout-columns"),
    )
    yield section("The GIL in detail", "lock")
    yield ul(
        "**What it protects:** CPython's internals — above all the reference counts on every object. Without it, two threads doing `refcount += 1` could corrupt memory.",
        "**When it is released:** during blocking I/O (`socket.recv`, `file.read`, `time.sleep`), and inside many C extensions doing heavy work (NumPy, `hashlib`, `zlib`). The running thread is also forced to hand it over every few milliseconds (`sys.getswitchinterval()`, 5 ms by default).",
        "**What it does NOT do:** make *your* code thread-safe. `counter += 1` is several bytecodes, and a switch can happen between them — you still need locks.",
        "**Free-threaded build:** CPython 3.13 added an optional build without the GIL (`python3.13t`); in 3.14 it is officially supported (PEP 779) as `python3.14t`. Pure-Python threads then run truly in parallel, at a small single-thread cost.",
    )
    yield code('''
        import sys
        print(sys.getswitchinterval())                 # 0.005
        # Only exists on 3.13+; True on the normal build, False on a free-threaded one:
        gil = getattr(sys, "_is_gil_enabled", lambda: True)()
        print(isinstance(gil, bool))                   # True
    ''')
    yield section("Which tool? A decision flow", "route")
    yield steps(
        ("Is the work mostly waiting?", "Network calls, disk, databases, sleeping → it's **I/O-bound**."),
        ("I/O-bound, a handful to hundreds of tasks", "`ThreadPoolExecutor` — works with ordinary blocking libraries like `requests`."),
        ("I/O-bound, thousands of connections", "`asyncio` with async libraries (`aiohttp`, `httpx`, `asyncpg`) — one thread, tiny per-task cost."),
        ("Is it computing in Python?", "Loops, parsing, math → **CPU-bound**: `ProcessPoolExecutor` / `multiprocessing`, or vectorise with NumPy, or a free-threaded build."),
        ("Mixed?", "`asyncio` for the I/O, `loop.run_in_executor` / `asyncio.to_thread` or a process pool for the heavy bits."),
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
    yield note("Python 3.13 shipped an experimental *free-threaded* build (no GIL); 3.14 makes it officially supported but still optional — the default `python3` keeps the GIL. For interviews, explain the GIL as above and mention free-threading as the direction of travel.", "Recent change")
    yield qa("If Python has a GIL, why are threads useful at all?",
             "Because most real programs spend their time **waiting** — for the network, the disk or a database. A thread blocked on I/O releases the GIL, so other threads run meanwhile. Threads give concurrency for I/O-bound work; for CPU-bound pure-Python work use processes (or a free-threaded build).")
    yield qa("Does the GIL make my code thread-safe?",
             "No. It only protects the interpreter's internals. A compound operation like `counter += 1` or check-then-act (`if key not in d: d[key] = …`) can be interrupted between bytecodes, so shared mutable state still needs a `Lock`, a `queue.Queue`, or another synchronisation primitive.")


@topic(G, "threading-module", "Threading & Synchronisation", "arrows-shuffle")
def _():
    yield lead("`threading` runs functions in OS threads that share one memory space. Sharing is the superpower and the danger — the synchronisation primitives (`Lock`, `Event`, `Queue`, …) are how you stay correct.")
    yield define("Thread", "an independent flow of execution inside one process. All threads see the same globals and heap objects, so they can communicate cheaply — and corrupt each other's data if they write without coordination.")
    yield section("Creating, starting & joining threads", "player-play")
    yield p("Pass a `target` callable (plus `args`/`kwargs`), or subclass `Thread` and override `run()`. `start()` launches the thread; `join()` waits for it to finish.")
    yield code('''
        import threading

        results = {}

        def square(n):
            results[n] = n * n                    # each thread writes its own key

        threads = [threading.Thread(target=square, args=(i,), name=f"worker-{i}") for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()                              # wait for all of them
        print(sorted(results.items()))            # [(0, 0), (1, 1), (2, 4), (3, 9)]
        print(threads[0].name, threads[0].is_alive())   # worker-0 False

        class Downloader(threading.Thread):       # subclass style
            def __init__(self, url):
                super().__init__()
                self.url = url
                self.size = None
            def run(self):                        # called in the new thread by start()
                self.size = len(self.url)         # stands in for a real download

        d = Downloader("https://example.com")
        d.start(); d.join()
        print(d.size)                             # 19
    ''')
    yield warn("Call `start()`, not `run()`. `t.run()` just executes the function in the *current* thread — no concurrency at all, and no error to tell you.")
    yield table(
        ["Method / attribute", "Meaning"],
        ["`t.start()`", "Begin running `run()` in a new OS thread (once per thread object)"],
        ["`t.join(timeout=None)`", "Block until the thread ends (or the timeout passes)"],
        ["`t.is_alive()`", "Still running?"],
        ["`t.daemon`", "Daemon threads don't keep the program alive"],
        ["`threading.current_thread()`", "The `Thread` object running this code"],
        ["`threading.active_count()`", "Number of live threads"],
    )
    yield section("Daemon threads", "ghost")
    yield p("The interpreter exits when all **non-daemon** threads have finished. Daemon threads are killed abruptly at exit — fine for background heartbeats, dangerous for anything that writes files or commits transactions.")
    yield code('''
        import threading

        def heartbeat(stop):
            while not stop.is_set():
                stop.wait(0.01)                   # sleep, but wake up immediately when stopped

        stop = threading.Event()
        t = threading.Thread(target=heartbeat, args=(stop,), daemon=True)
        t.start()
        print(t.daemon, t.is_alive())             # True True
        stop.set(); t.join()                      # a clean shutdown is still better
        print(t.is_alive())                       # False
    ''')
    yield section("Race conditions: why `x += 1` isn't safe", "alert-triangle")
    yield p("A thread switch can happen **between any two bytecodes**. `counter += 1` is a read, an add and a write — three steps:")
    yield code('''
        import dis

        def increment():
            global counter
            counter += 1

        ops = [i.opname for i in dis.get_instructions(increment)]
        print([op for op in ops if op in ("LOAD_GLOBAL", "BINARY_OP", "STORE_GLOBAL")])
        # ['LOAD_GLOBAL', 'BINARY_OP', 'STORE_GLOBAL']
    ''', check=False)
    yield table(
        ["Step", "Thread A", "Thread B", "`counter`"],
        ["1", "reads 5", "", "5"],
        ["2", "", "reads 5", "5"],
        ["3", "computes 6, writes 6", "", "6"],
        ["4", "", "computes 6, writes 6", "6 — one increment **lost**"],
    )
    yield note("Races are non-deterministic: the code may pass a thousand runs and fail in production. The fix is to make the read-modify-write **atomic** with a lock.")
    yield section("Lock & RLock", "lock")
    yield code('''
        import threading

        class BankAccount:
            def __init__(self):
                self.balance = 0
                self._lock = threading.Lock()

            def deposit(self, amount):
                with self._lock:                  # acquire … release, even on exceptions
                    self.balance += amount

        acct = BankAccount()

        def worker():
            for _ in range(10_000):
                acct.deposit(1)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        print(acct.balance)                       # 50000

        lock = threading.Lock()
        lock.acquire()
        print(lock.acquire(timeout=0.01))         # False  ← a Lock is not re-entrant
        lock.release()
    ''')
    yield p("A plain `Lock` deadlocks if the **same** thread tries to take it twice. An `RLock` (re-entrant lock) counts acquisitions by its owner — handy when one locked method calls another.")
    yield code('''
        import threading

        class Inventory:
            def __init__(self):
                self._lock = threading.RLock()
                self.items = {}

            def add(self, name, qty=1):
                with self._lock:
                    self.items[name] = self.items.get(name, 0) + qty

            def add_many(self, names):
                with self._lock:                  # held here…
                    for n in names:
                        self.add(n)               # …and re-acquired inside add(): OK with RLock

        inv = Inventory()
        inv.add_many(["pen", "pen", "ink"])
        print(inv.items)                          # {'pen': 2, 'ink': 1}
    ''')
    yield section("Semaphore, Event & Condition", "traffic-lights")
    yield cards(
        ("`Semaphore(n)`", "A lock that up to `n` threads can hold at once — limit concurrent DB connections or API calls. `BoundedSemaphore` also errors if released too often.", "users-group"),
        ("`Event`", "A thread-safe boolean flag: `set()`, `clear()`, `wait()`. Great for “start now” and “please stop” signals.", "flag"),
        ("`Condition`", "A lock plus wait/notify: threads sleep until *some predicate* becomes true — the building block of queues.", "bell"),
        ("`Barrier(n)`", "`n` threads each call `wait()`; all are released together once the last one arrives.", "fence"),
    )
    yield code('''
        import threading, time

        sem = threading.Semaphore(2)              # at most 2 inside at a time
        active = peak = 0
        guard = threading.Lock()

        def task():
            global active, peak
            with sem:
                with guard:
                    active += 1
                    peak = max(peak, active)
                time.sleep(0.01)
                with guard:
                    active -= 1

        threads = [threading.Thread(target=task) for _ in range(6)]
        for t in threads: t.start()
        for t in threads: t.join()
        print(peak <= 2)                          # True

        ready = threading.Event()
        log = []

        def waiter():
            ready.wait()                          # blocks until set()
            log.append("go")

        w = threading.Thread(target=waiter); w.start()
        log.append("setting up")
        ready.set(); w.join()
        print(log)                                # ['setting up', 'go']

        cond = threading.Condition()
        items, got = [], []

        def consumer():
            with cond:
                cond.wait_for(lambda: len(items) >= 3)   # sleeps; re-checks after each notify
                got.extend(items)

        c = threading.Thread(target=consumer); c.start()
        for i in range(3):
            with cond:
                items.append(i)
                cond.notify()
        c.join()
        print(got)                                # [0, 1, 2]
    ''')
    yield section("Producer–consumer with `queue.Queue`", "stack-push")
    yield p("`queue.Queue` is already thread-safe and does all the locking for you. It's the cleanest way for threads to hand work to each other — prefer it to sharing lists and locks.")
    yield code('''
        import queue, threading

        q = queue.Queue(maxsize=5)                # put() blocks when full → back-pressure
        results = []
        STOP = object()                           # a unique sentinel

        def consumer():
            while True:
                n = q.get()
                if n is STOP:
                    q.task_done()
                    break
                results.append(n * n)             # list.append is safe; fancier updates need a lock
                q.task_done()

        workers = [threading.Thread(target=consumer) for _ in range(3)]
        for w in workers: w.start()
        for n in range(10):                       # the producer
            q.put(n)
        for _ in workers:
            q.put(STOP)                           # one sentinel per consumer
        q.join()                                  # wait until every item is task_done()
        for w in workers: w.join()
        print(sorted(results))                    # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    ''')
    yield table(
        ["Queue class", "Order"],
        ["`queue.Queue`", "FIFO"],
        ["`queue.LifoQueue`", "LIFO (a stack)"],
        ["`queue.PriorityQueue`", "Smallest item first — put `(priority, item)` tuples"],
        ["`queue.SimpleQueue`", "Unbounded FIFO without `task_done`/`join` — simpler, faster"],
    )
    yield note("Since 3.13, `Queue.shutdown()` wakes blocked `get()`/`put()` callers with `queue.ShutDown` — an alternative to sentinel values.", "3.13+")
    yield section("Per-thread data: `threading.local`", "user-circle")
    yield code('''
        import threading

        ctx = threading.local()                   # each thread sees its own attributes
        seen = {}

        def current_user_greeting():
            return f"hi {ctx.user}"               # no need to pass user down the call chain

        def handle(user):
            ctx.user = user
            seen[user] = current_user_greeting()

        threads = [threading.Thread(target=handle, args=(u,)) for u in ("asha", "ravi")]
        for t in threads: t.start()
        for t in threads: t.join()
        print(sorted(seen.values()))              # ['hi asha', 'hi ravi']
        print(hasattr(ctx, "user"))               # False  ← the main thread never set it
    ''')
    yield section("Deadlocks & lock ordering", "lock-x")
    yield p("Thread 1 holds lock A and waits for B; thread 2 holds B and waits for A — both wait forever. The standard cure is to **always acquire locks in one global order**.")
    yield code('''
        import threading

        class Account:
            def __init__(self, id, balance):
                self.id, self.balance = id, balance
                self.lock = threading.Lock()

        def transfer(src, dst, amount):
            first, second = sorted((src, dst), key=lambda a: a.id)   # fixed order, whatever the direction
            with first.lock, second.lock:
                src.balance -= amount
                dst.balance += amount

        a, b = Account(1, 100), Account(2, 100)
        t1 = threading.Thread(target=lambda: [transfer(a, b, 1) for _ in range(1000)])
        t2 = threading.Thread(target=lambda: [transfer(b, a, 1) for _ in range(1000)])
        t1.start(); t2.start(); t1.join(); t2.join()
        print(a.balance, b.balance)               # 100 100
    ''')
    yield ul(
        "Take locks in a consistent order (by id, by name, by address).",
        "Hold locks for as short a time as possible; never call unknown code (callbacks, I/O) while holding one.",
        "Use `lock.acquire(timeout=…)` to detect a stuck lock instead of hanging forever.",
        "Prefer message passing (`queue.Queue`) over many fine-grained locks.",
    )
    yield section("Timer", "alarm")
    yield code('''
        import threading

        fired = threading.Event()
        t = threading.Timer(0.01, fired.set)      # run fired.set() after 10 ms, in a new thread
        t.start()
        print(fired.wait(timeout=1))              # True

        never = threading.Timer(10, print, args=("never printed",))
        never.start()
        never.cancel(); never.join()              # cancel before it fires
        print(never.is_alive())                   # False
    ''')
    yield section("Which built-in operations are thread-safe?", "shield-check")
    yield table(
        ["Usually atomic (single operation on a built-in)", "NOT atomic — needs a lock"],
        ["`L.append(x)`, `L.pop()`, `L.extend(ys)`", "`x += 1`, `L[i] += 1`, `d[k] += 1`"],
        ["`d[k] = v`, `d.get(k)`, `d.pop(k, None)`", "`if k not in d: d[k] = v` (check-then-act)"],
        ["`x = L[i]`, `q.put(x)`, `q.get()`", "`d[k] = d.get(k, 0) + 1`"],
        ["`d.setdefault(k, v)`", "Any sequence of several operations that must stay consistent"],
    )
    yield warn("Atomicity of single built-in operations is a CPython implementation detail (the GIL on the default build, per-object locks on the free-threaded build). It's fine to rely on `queue.Queue`; for your own invariants, use a lock.")
    yield qa("What is a race condition and how do you prevent one?",
             "The result depends on the unpredictable interleaving of threads — typically two threads doing read-modify-write on shared data. Prevent it by making the critical section atomic with a `Lock`, by confining data to one thread (`queue.Queue`, `threading.local`), or by using immutable data.")
    yield qa("Lock vs RLock?",
             "A `Lock` can be acquired once; a second `acquire()` — even from the same thread — blocks. An `RLock` records its owner and a counter, so the owning thread can re-acquire it (it must release it the same number of times). Use `RLock` when locked methods call other locked methods.")
    yield qa("What is a deadlock and how do you avoid it?",
             "Two or more threads each wait for a lock held by another, so none can proceed. Avoid it with a global lock-ordering rule, minimal lock scope, timeouts on `acquire`, and message passing instead of shared locks.")


@topic(G, "multiprocessing-module", "Multiprocessing", "cpu")
def _():
    yield lead("`multiprocessing` runs code in separate processes — each with its own interpreter, memory and GIL — so CPU-bound Python work finally uses every core.")
    yield define("Process", "an independent program instance with its own address space. Processes share nothing by default; data moves between them by **pickling** it through pipes or queues.")
    yield section("Processes vs threads", "arrows-split")
    yield table(
        ["", "Threads", "Processes"],
        ["Memory", "Shared", "Separate (copy or explicit sharing)"],
        ["GIL", "One GIL for all threads", "One GIL **per process** → true parallelism"],
        ["Start-up cost", "~microseconds", "~milliseconds (a new interpreter)"],
        ["Communication", "Any object, directly", "Pickled messages: `Queue`, `Pipe`, shared memory"],
        ["A crash", "Can take down the whole program", "Isolated to that process"],
        ["Use for", "I/O-bound work", "CPU-bound work"],
    )
    yield section("`Process`: start, join, exit code", "player-play")
    yield code('''
        from multiprocessing import Process, current_process

        def work(n):
            print(f"{current_process().name}: {n * n}")

        if __name__ == "__main__":
            procs = [Process(target=work, args=(i,), name=f"P{i}") for i in range(3)]
            for p in procs:
                p.start()
            for p in procs:
                p.join()
            print("exit codes:", [p.exitcode for p in procs])
    ''', run=False)
    yield output('''
        P0: 0
        P1: 1
        P2: 4
        exit codes: [0, 0, 0]
    ''', "Output (the P lines can appear in any order)")
    yield warn("The `if __name__ == \"__main__\":` guard is **mandatory** with the `spawn` and `forkserver` start methods: each child re-imports your module, and without the guard it would start children of its own, recursively.", "Required")
    yield section("`Pool`: parallel map", "grid-dots")
    yield code('''
        from multiprocessing import Pool

        def square(x):
            return x * x

        def power(base, exp):
            return base ** exp

        if __name__ == "__main__":
            with Pool(processes=4) as pool:
                print(pool.map(square, range(6)))                 # [0, 1, 4, 9, 16, 25]
                print(list(pool.imap(square, range(3))))          # [0, 1, 4]  ← lazy, in order
                print(sorted(pool.imap_unordered(square, range(3))))   # [0, 1, 4]  ← as they finish
                print(pool.starmap(power, [(2, 3), (3, 2)]))      # [8, 9]  ← unpacks tuples
                r = pool.apply_async(square, (7,))
                print(r.get(timeout=5))                           # 49
    ''', run=False)
    yield table(
        ["Method", "Returns", "Use when"],
        ["`map(f, it, chunksize)`", "A list, in input order (blocks)", "All inputs known, results fit in memory"],
        ["`imap(f, it)`", "A lazy iterator, in order", "Large inputs; process results as a stream"],
        ["`imap_unordered(f, it)`", "A lazy iterator, completion order", "Order doesn't matter — fastest feedback"],
        ["`starmap(f, pairs)`", "A list; each tuple is unpacked into args", "Functions of several arguments"],
        ["`apply_async(f, args)`", "An `AsyncResult` (`.get()`)", "One-off background calls"],
    )
    yield note("For many tiny tasks, pass a larger `chunksize` to `map`/`imap` — sending each item separately costs more in pickling and IPC than the work itself.", "Performance")
    yield section("Start methods", "rocket")
    yield table(
        ["Method", "How the child starts", "Default on"],
        ["`spawn`", "A fresh interpreter imports your module, then runs the target. Safe, slower.", "Windows, **macOS** (since 3.8)"],
        ["`fork`", "The OS copies the parent process (memory included). Fast, but unsafe if the parent has threads.", "Linux before 3.14"],
        ["`forkserver`", "A clean server process is started once and forks children on request.", "**Linux since 3.14**"],
    )
    yield code('''
        import multiprocessing as mp

        print(mp.cpu_count() > 0)                                     # True
        print(mp.get_start_method() in {"fork", "spawn", "forkserver"})   # True
        print("spawn" in mp.get_all_start_methods())                  # True  ← available everywhere
    ''')
    yield p("Choose explicitly with `mp.set_start_method(\"spawn\")` once at start-up, or better, a context: `ctx = mp.get_context(\"spawn\"); ctx.Pool(...)`. Code that works under `spawn` works everywhere.")
    yield section("Everything crosses the boundary by pickling", "package")
    yield p("Arguments, return values and queue items are pickled in the parent and unpickled in the child. Functions are pickled **by name**, so the target must be importable: a module-level `def`, not a lambda, nested function or something defined in the REPL.")
    yield code('''
        import pickle

        def module_level(x):
            return x

        try:
            pickle.dumps(lambda x: x)
        except pickle.PicklingError:
            print("lambdas can't be sent to a worker")   # lambdas can't be sent to a worker
    ''')
    yield warn("Large arguments are copied for every task. Send small descriptions (file paths, index ranges) and let workers load the data, or use shared memory.")
    yield section("Communicating: Queue & Pipe", "arrows-exchange")
    yield code('''
        from multiprocessing import Process, Queue, Pipe

        def producer(q):
            for i in range(3):
                q.put(i * 10)
            q.put(None)                           # sentinel: "no more"

        def echo(conn):
            msg = conn.recv()
            conn.send(msg.upper())
            conn.close()

        if __name__ == "__main__":
            q = Queue()
            p = Process(target=producer, args=(q,)); p.start()
            items = []
            while (item := q.get()) is not None:
                items.append(item)
            p.join()
            print(items)                          # [0, 10, 20]

            parent, child = Pipe()                # two connected ends
            p = Process(target=echo, args=(child,)); p.start()
            parent.send("hello")
            print(parent.recv())                  # HELLO
            p.join()
    ''', run=False)
    yield section("Sharing state", "share")
    yield cards(
        ("`Value` / `Array`", "A single number or fixed array in shared memory, with an optional lock: `Value('i', 0)`, `Array('d', 10)`.", "number"),
        ("`shared_memory`", "A raw named block of bytes any process can attach to — zero-copy for NumPy arrays (3.8+).", "database"),
        ("`Manager()`", "A server process holding real `dict`/`list` objects; others use proxies. Flexible but slow (every access is IPC).", "server"),
    )
    yield code('''
        from multiprocessing import Process, Value, Manager

        def add(counter, n):
            for _ in range(n):
                with counter.get_lock():          # += on shared memory still needs the lock
                    counter.value += 1

        def record(d, key):
            d[key] = key * 2

        if __name__ == "__main__":
            counter = Value("i", 0)
            ps = [Process(target=add, args=(counter, 1000)) for _ in range(4)]
            for p in ps: p.start()
            for p in ps: p.join()
            print(counter.value)                  # 4000

            with Manager() as m:
                d = m.dict()
                ps = [Process(target=record, args=(d, k)) for k in range(3)]
                for p in ps: p.start()
                for p in ps: p.join()
                print(dict(sorted(d.items())))    # {0: 0, 1: 2, 2: 4}
    ''', run=False)
    yield p("`shared_memory` hands out a named buffer; another process attaches by name. Here both ends live in one process to show the API:")
    yield code('''
        from multiprocessing import shared_memory

        shm = shared_memory.SharedMemory(create=True, size=4)
        try:
            shm.buf[:4] = bytes([1, 2, 3, 4])
            other = shared_memory.SharedMemory(name=shm.name)   # normally done in another process
            print(list(other.buf[:4]))                          # [1, 2, 3, 4]
            other.close()
        finally:
            shm.close()
            shm.unlink()                          # free the block (only the creator does this)
    ''')
    yield dodont(
        "Use processes for CPU-heavy, independent chunks of work; keep messages small; prefer `ProcessPoolExecutor` or `Pool` over hand-managed `Process` objects.",
        "Spawning a process per tiny task, sharing huge objects through a `Manager`, or forgetting the `__main__` guard.",
    )
    yield qa("Why does multiprocessing need `if __name__ == \"__main__\"`?",
             "With `spawn`/`forkserver` the child process imports your main module to find the target function. Without the guard, that import would execute the process-creating code again — infinite recursion (Python raises a `RuntimeError` to stop it).")
    yield qa("How do processes share data?",
             "By default they don't — each has its own memory. You send pickled messages (`Queue`, `Pipe`, pool arguments/results), or share explicitly with `Value`/`Array`, `shared_memory`, or a `Manager` proxy.")
    yield qa("fork vs spawn?",
             "`fork` copies the running parent (fast, inherits everything — including held locks from other threads, which can deadlock). `spawn` starts a fresh interpreter (slower, but clean and portable). macOS and Windows default to `spawn`; Linux moved from `fork` to `forkserver` in 3.14.")


@topic(G, "concurrent-futures", "concurrent.futures", "stack-2")
def _():
    yield lead("One high-level API for both threads and processes: submit callables to an *executor* and get back *futures* — placeholders for results that will arrive later.")
    yield define("Future", "an object representing a pending result. You can ask whether it's `done()`, block on `result()`, fetch its `exception()`, `cancel()` it, or attach callbacks.")
    yield section("The Executor API", "api")
    yield table(
        ["Call", "Does"],
        ["`ex.submit(f, *args, **kw)`", "Schedule one call → returns a `Future` immediately"],
        ["`ex.map(f, *iterables, timeout=None)`", "Like built-in `map`, run in parallel; results in **input order**"],
        ["`ex.shutdown(wait=True, cancel_futures=False)`", "Stop accepting work; called automatically by `with`"],
        ["`as_completed(futures, timeout)`", "Yield futures as they **finish**"],
        ["`wait(futures, timeout, return_when)`", "Block until ALL_COMPLETED / FIRST_COMPLETED / FIRST_EXCEPTION"],
    )
    yield section("submit, result & map", "send")
    yield code('''
        from concurrent.futures import ThreadPoolExecutor

        def square(x):
            return x * x

        with ThreadPoolExecutor(max_workers=3) as ex:
            fut = ex.submit(square, 7)
            print(fut.result())                   # 49  ← blocks until ready
            print(fut.done())                     # True
            print(list(ex.map(square, [3, 1, 2])))   # [9, 1, 4]  ← input order, always
    ''')
    yield section("as_completed: handle results as they arrive", "list-check")
    yield code('''
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def job(name, delay):
            time.sleep(delay)                     # stands in for a network call
            return name

        with ThreadPoolExecutor() as ex:
            futures = {ex.submit(job, n, d): n for n, d in [("slow", 0.05), ("fast", 0.0), ("mid", 0.02)]}
            finished = [f.result() for f in as_completed(futures)]   # completion order
        print(sorted(finished))                   # ['fast', 'mid', 'slow']
        print(len(futures))                       # 3
    ''')
    yield note("Map each future back to its input with a dict (`{future: input}`), because `as_completed` yields them in whatever order they finish.")
    yield section("Exceptions travel through the future", "alert-octagon")
    yield p("An exception raised in a worker is stored in the future and **re-raised when you call `result()`** — nothing is printed if you never ask.")
    yield code('''
        from concurrent.futures import ThreadPoolExecutor

        def risky(x):
            if x == 2:
                raise ValueError("bad input 2")
            return x

        with ThreadPoolExecutor() as ex:
            futures = [ex.submit(risky, i) for i in range(4)]
            outcomes = []
            for f in futures:
                try:
                    outcomes.append(f.result())
                except ValueError as e:
                    outcomes.append(f"error: {e}")
        print(outcomes)                           # [0, 1, 'error: bad input 2', 3]
        print(type(futures[2].exception()).__name__)   # ValueError
    ''')
    yield warn("With `ex.map`, the first failing item raises when the iterator reaches it, and you lose the remaining results. Use `submit` + per-future `try` when some inputs may fail.")
    yield section("wait, cancel & timeouts", "clock-pause")
    yield code('''
        import threading
        from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

        gate = threading.Event()
        with ThreadPoolExecutor(max_workers=2) as ex:
            quick = ex.submit(lambda: "quick")
            blocked = ex.submit(gate.wait)        # can't finish until the gate opens
            done, pending = wait([quick, blocked], return_when=FIRST_COMPLETED)
            print([f.result() for f in done], len(pending))   # ['quick'] 1
            gate.set()
    ''')
    yield code('''
        import threading
        from concurrent.futures import ThreadPoolExecutor

        started, gate = threading.Event(), threading.Event()

        def blocker():
            started.set()
            gate.wait()
            return "finished"

        with ThreadPoolExecutor(max_workers=1) as ex:
            running = ex.submit(blocker)          # occupies the only worker
            queued = ex.submit(print, "never")    # waits in the queue
            started.wait()
            print(queued.cancel(), queued.cancelled())   # True True  ← not started yet
            print(running.cancel())               # False  ← already running: can't cancel
            try:
                running.result(timeout=0.01)
            except TimeoutError:
                print("timed out")                # timed out
            gate.set()
        print(running.result())                   # finished
    ''')
    yield note("A timeout on `result()` only stops *you* waiting — the task keeps running. Threads can't be killed; design long tasks to check a stop `Event`.")
    yield section("Callbacks", "phone-call")
    yield code('''
        from concurrent.futures import ThreadPoolExecutor

        log = []
        with ThreadPoolExecutor() as ex:
            f = ex.submit(sum, [1, 2, 3])
            f.add_done_callback(lambda fut: log.append(fut.result() * 10))
        print(log)                                # [60]
    ''')
    yield section("Processes & interpreters: same API", "cpu")
    yield code('''
        from concurrent.futures import ProcessPoolExecutor

        def count_primes(limit):
            return sum(all(n % d for d in range(2, int(n ** 0.5) + 1)) for n in range(2, limit))

        if __name__ == "__main__":
            with ProcessPoolExecutor() as ex:     # one worker per CPU core by default
                print(list(ex.map(count_primes, [10_000, 20_000], chunksize=1)))   # [1229, 2262]
    ''', run=False)
    yield table(
        ["Executor", "Parallel CPU?", "Default `max_workers`", "Notes"],
        ["`ThreadPoolExecutor`", "No (GIL)", "`min(32, cpu_count + 4)`", "I/O-bound; shares memory"],
        ["`ProcessPoolExecutor`", "Yes", "number of CPUs", "Arguments/results must pickle; needs `__main__` guard"],
        ["`InterpreterPoolExecutor` (3.14)", "Yes", "number of CPUs", "Sub-interpreters in one process, each with its own GIL"],
    )
    yield dodont(
        "Size thread pools for the I/O you're waiting on (tens of workers is fine); size process pools to the number of cores.",
        "Using a `ProcessPoolExecutor` for tiny tasks — pickling and IPC overhead will make it slower than a plain loop.",
    )
    yield qa("What's the difference between `ex.map` and `submit` + `as_completed`?",
             "`map` returns results in input order and raises the first exception when you reach it — simple and tidy. `submit` returns one `Future` per call; with `as_completed` you process each result as soon as it's ready and handle failures individually.")
    yield qa("How do you get an exception out of a worker thread?",
             "Call `future.result()` — it re-raises the worker's exception in the caller — or inspect `future.exception()`. With raw `threading.Thread`, exceptions are only reported by `threading.excepthook`, which is why executors are usually nicer.")


@topic(G, "asyncio-deep", "asyncio in Depth", "bolt")
def _():
    yield lead("`asyncio` runs thousands of I/O tasks on **one thread** by switching between them at every `await`. It's cooperative multitasking: fast and lock-free, as long as nobody blocks the loop.")
    yield define("Event loop", "a scheduler that runs ready tasks one at a time. A task runs until it `await`s something that isn't ready (a socket, a timer); the loop then parks it and runs another task, resuming it when its I/O completes.")
    yield section("Coroutines, tasks & futures", "components")
    yield table(
        ["Object", "What it is", "Created by"],
        ["Coroutine", "The paused computation returned by calling an `async def` function. Does **nothing** until awaited or wrapped in a task.", "`coro = fetch()`"],
        ["Task", "A coroutine scheduled on the loop — it runs concurrently with the code that created it.", "`asyncio.create_task(coro)`, `TaskGroup.create_task`"],
        ["Future", "A low-level placeholder for a result; tasks are futures. Rarely created by hand.", "`loop.create_future()`"],
    )
    yield code('''
        import asyncio

        async def greet(name):
            await asyncio.sleep(0)                # yield control to the loop once
            return f"hi {name}"

        coro = greet("asha")
        print(type(coro).__name__)                # coroutine  ← nothing has run yet
        print(asyncio.run(coro))                  # hi asha    ← run() starts a loop, runs it, closes it
    ''')
    yield section("Sequential awaits vs concurrent tasks", "arrows-split")
    yield code('''
        import asyncio

        async def job(name, delay, log):
            log.append(f"start {name}")
            await asyncio.sleep(delay)
            log.append(f"end {name}")

        async def sequential():
            log = []
            await job("a", 0.02, log)             # waits for a to finish…
            await job("b", 0.01, log)             # …before b even starts
            return log

        async def concurrent():
            log = []
            t1 = asyncio.create_task(job("a", 0.02, log))   # both scheduled now
            t2 = asyncio.create_task(job("b", 0.01, log))
            await t1
            await t2
            return log

        print(asyncio.run(sequential()))   # ['start a', 'end a', 'start b', 'end b']
        print(asyncio.run(concurrent()))   # ['start a', 'start b', 'end b', 'end a']
    ''')
    yield warn("`await coro()` one after another is **sequential**. Concurrency only happens when several tasks exist at once — via `create_task`, `gather` or a `TaskGroup`.")
    yield section("gather", "stack")
    yield code('''
        import asyncio

        async def fetch(i):
            await asyncio.sleep(0.01 * (3 - i))   # later items finish first…
            if i == 1:
                raise ValueError(f"item {i} failed")
            return i * 10

        async def main():
            results = await asyncio.gather(*(fetch(i) for i in range(3)), return_exceptions=True)
            print(results)                        # [0, ValueError('item 1 failed'), 20]  ← …but order = input order
            try:
                await asyncio.gather(fetch(0), fetch(1))
            except ValueError as e:
                print("first error:", e)          # first error: item 1 failed

        asyncio.run(main())
    ''')
    yield section("TaskGroup — structured concurrency (3.11+)", "sitemap")
    yield p("`async with asyncio.TaskGroup()` waits for every task created in it. If one fails, the others are **cancelled** and all errors are raised together as an `ExceptionGroup` — no orphaned tasks.")
    yield code('''
        import asyncio

        async def worker(n):
            await asyncio.sleep(0.01)
            if n == 2:
                raise KeyError(n)
            return n

        async def main():
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(worker(n)) for n in range(2)]
            print([t.result() for t in tasks])    # [0, 1]  ← all done when the block exits

            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(worker(2))
                    slow = tg.create_task(asyncio.sleep(10))
            except* KeyError as eg:
                print(type(eg).__name__, len(eg.exceptions))   # ExceptionGroup 1
            print(slow.cancelled())               # True  ← the sibling was cancelled

        asyncio.run(main())
    ''')
    yield note("Prefer `TaskGroup` over bare `create_task` + `gather` in new code. A bare task that nobody keeps a reference to can even be garbage-collected mid-flight — keep references or use a group.")
    yield section("Timeouts & cancellation", "clock-x")
    yield code('''
        import asyncio

        async def main():
            try:
                async with asyncio.timeout(0.01):          # 3.11+
                    await asyncio.sleep(1)
            except TimeoutError:
                print("timeout block")                     # timeout block

            try:
                await asyncio.wait_for(asyncio.sleep(1), timeout=0.01)
            except TimeoutError:
                print("wait_for")                          # wait_for

        asyncio.run(main())
    ''')
    yield code('''
        import asyncio

        async def worker(log):
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                log.append("cleaning up")
                raise                             # always re-raise CancelledError

        async def main():
            log = []
            t = asyncio.create_task(worker(log))
            await asyncio.sleep(0)                # let it start
            t.cancel()                            # throws CancelledError into it at its await
            try:
                await t
            except asyncio.CancelledError:
                log.append("cancelled")
            print(log, t.cancelled())             # ['cleaning up', 'cancelled'] True

        asyncio.run(main())
    ''')
    yield warn("Swallowing `CancelledError` (`except Exception` doesn't catch it, but a bare `except:` or `except BaseException` does) breaks timeouts and `TaskGroup` shutdown. Clean up, then re-raise.")
    yield section("Queues & semaphores", "stack-push")
    yield code('''
        import asyncio

        async def consumer(q, out):
            while True:
                item = await q.get()
                out.append(item * item)
                q.task_done()

        async def main():
            q = asyncio.Queue(maxsize=2)          # put() waits when full
            out = []
            workers = [asyncio.create_task(consumer(q, out)) for _ in range(2)]
            for i in range(5):                    # the producer
                await q.put(i)
            await q.join()                        # every item processed
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            print(sorted(out))                    # [0, 1, 4, 9, 16]

        asyncio.run(main())
    ''')
    yield code('''
        import asyncio

        async def main():
            sem = asyncio.Semaphore(3)            # at most 3 "requests" in flight
            active = peak = 0

            async def fetch(i):
                nonlocal active, peak
                async with sem:
                    active += 1
                    peak = max(peak, active)
                    await asyncio.sleep(0.01)
                    active -= 1
                    return i

            results = await asyncio.gather(*(fetch(i) for i in range(10)))
            print(results == list(range(10)), peak)   # True 3

        asyncio.run(main())
    ''')
    yield note("No lock is needed around `active += 1` here: with one thread, a task can only be interrupted at an `await`.")
    yield section("Blocking code: `asyncio.to_thread`", "arrow-bar-to-right")
    yield p("A blocking call (`time.sleep`, `requests.get`, heavy CPU) freezes the **whole loop** — every other task stops. Push it to a worker thread:")
    yield code('''
        import asyncio, time

        def blocking_io(x):
            time.sleep(0.01)                      # a blocking library call
            return x * 2

        async def main():
            results = await asyncio.gather(
                asyncio.to_thread(blocking_io, 1),   # runs in the default thread pool
                asyncio.to_thread(blocking_io, 2),
            )
            print(results)                        # [2, 4]

        asyncio.run(main())
    ''')
    yield section("Async iterators & context managers", "repeat")
    yield code('''
        import asyncio
        from contextlib import asynccontextmanager

        async def ticker(n):                      # async generator
            for i in range(n):
                await asyncio.sleep(0)
                yield i

        log = []

        @asynccontextmanager
        async def connection(name):               # async with → __aenter__ / __aexit__
            log.append(f"open {name}")
            try:
                yield name.upper()
            finally:
                log.append(f"close {name}")

        async def main():
            squares = [i * i async for i in ticker(4)]   # async comprehension
            print(squares)                        # [0, 1, 4, 9]
            async with connection("db") as conn:
                log.append(f"using {conn}")
            print(log)                            # ['open db', 'using DB', 'close db']

        asyncio.run(main())
    ''')
    yield section("Common mistakes", "alert-triangle")
    yield code('''
        import asyncio

        async def save():
            return "saved"

        async def main():
            result = save()                       # forgot await → just a coroutine object
            print(type(result).__name__)          # coroutine
            result.close()                        # (silences "coroutine was never awaited")
            print(await save())                   # saved

        asyncio.run(main())
    ''')
    yield table(
        ["Mistake", "Symptom", "Fix"],
        ["Forgetting `await`", "`RuntimeWarning: coroutine … was never awaited`; nothing happens", "`await` it or create a task"],
        ["`time.sleep()` / `requests` in a coroutine", "All tasks freeze", "`await asyncio.sleep()`, async libraries, or `asyncio.to_thread`"],
        ["CPU-heavy loop in a coroutine", "Latency spikes for every other task", "`loop.run_in_executor(ProcessPoolExecutor(), …)`"],
        ["Calling `asyncio.run` inside a running loop", "`RuntimeError`", "`await` the coroutine instead"],
        ["Fire-and-forget tasks without a reference", "Task silently disappears; errors never seen", "Keep references / use `TaskGroup`"],
    )
    yield section("Sync vs async at a glance", "arrows-exchange")
    yield table(
        ["Sync", "Async"],
        ["`def f():`", "`async def f():`"],
        ["`f()`", "`await f()`"],
        ["`time.sleep(1)`", "`await asyncio.sleep(1)`"],
        ["`for x in it:`", "`async for x in ait:`"],
        ["`with cm:`", "`async with cm:`"],
        ["`threading.Lock`", "`asyncio.Lock` (only across `await`s)"],
        ["`queue.Queue`", "`asyncio.Queue`"],
        ["`ThreadPoolExecutor.map`", "`asyncio.gather` / `TaskGroup`"],
    )
    yield qa("How is asyncio different from threading?",
             "asyncio uses one thread and **cooperative** switching: tasks yield only at `await`, so there are no surprise interleavings and tasks are very cheap (thousands are fine). Threads are **pre-emptive**: the OS can switch at any bytecode, so shared data needs locks, and each thread costs more memory. Neither gives CPU parallelism under the GIL.")
    yield qa("What happens if you call a blocking function inside a coroutine?",
             "It blocks the event loop thread, so every other task stalls until it returns. Use the async equivalent, or offload with `await asyncio.to_thread(func, …)` (or `run_in_executor` with a process pool for CPU work).")
    yield qa("gather vs TaskGroup?",
             "Both run awaitables concurrently. `gather` returns results in order and, by default, propagates the first exception while leaving the other tasks running (or collects errors with `return_exceptions=True`). `TaskGroup` (3.11+) guarantees structure: if any task fails, the rest are cancelled and all failures are raised as an `ExceptionGroup`.")
