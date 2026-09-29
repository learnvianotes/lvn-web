from kit import *

G = "Concurrency"


@topic(G, "threads-basics", "Threads & Runnable", "arrows-split")
def _():
    yield lead("A thread is an independent path of execution inside one JVM process — create it with a `Runnable`, start it with `start()`, wait for it with `join()`.")
    yield define("Thread", "the smallest unit the OS schedules. All threads of a process share its heap (objects, static fields) but each has its *own stack* (local variables, call frames) and program counter.")
    yield section("Process vs thread", "layers-difference")
    yield table(
        ["", "Process", "Thread"],
        ["Memory", "Own address space", "Shares the process heap; own stack"],
        ["Creation cost", "Heavy (fork, new address space)", "Lighter (~1 MB stack reserved for a platform thread)"],
        ["Communication", "IPC: pipes, sockets, files", "Shared objects — fast, but needs synchronisation"],
        ["Crash impact", "Isolated", "An uncaught error kills only that thread, but corrupted shared state affects all"],
        ["In Java", "`ProcessBuilder`, one JVM = one process", "`Thread`, executors, virtual threads"],
    )
    yield section("Creating and joining threads", "code")
    yield p("Give each thread its own slice of the work, `start()` them, then `join()` before reading the results — `join()` both waits *and* guarantees you see everything the thread wrote.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                long[] sums = new long[2];
                Thread t1 = new Thread(() -> sums[0] = sum(1, 50), "worker-1");
                Thread t2 = new Thread(() -> sums[1] = sum(51, 100), "worker-2");
                t1.start();                 // both now run concurrently with main
                t2.start();
                t1.join();                  // wait for each to finish
                t2.join();
                System.out.println(t1.getName() + " -> " + sums[0]);
                System.out.println(t2.getName() + " -> " + sums[1]);
                System.out.println("total = " + (sums[0] + sums[1]));
            }

            static long sum(int from, int to) {
                long s = 0;
                for (int i = from; i <= to; i++) s += i;
                return s;
            }
        }
    ''', out="""
        worker-1 -> 1275
        worker-2 -> 3775
        total = 5050
    """)
    yield section("Three ways to define the task", "list")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Thread a = new Greeter();                       // 1. subclass Thread
                a.setName("greeter");
                a.start();
                a.join();

                Runnable task = new Runnable() {                // 2. implement Runnable
                    @Override public void run() {
                        System.out.println("2. Runnable on " + Thread.currentThread().getName());
                    }
                };
                Thread b = new Thread(task, "runner");
                b.start();
                b.join();

                Thread c = new Thread(                          // 3. lambda (Runnable is functional)
                    () -> System.out.println("3. lambda on " + Thread.currentThread().getName()), "lambda");
                c.start();
                c.join();
            }
        }

        class Greeter extends Thread {
            @Override public void run() {
                System.out.println("1. Thread subclass on " + getName());
            }
        }
    ''', out="""
        1. Thread subclass on greeter
        2. Runnable on runner
        3. lambda on lambda
    """)
    yield dodont("Implement `Runnable` (or `Callable`) and hand it to a thread or executor — the task stays independent of *how* it is run, and your class can still extend something else.",
                 "Extending `Thread` just to override `run()` — it burns your single superclass slot and couples the work to one thread.")
    yield section("`start()` vs `run()`", "player-play")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Runnable r = () -> System.out.println("running in " + Thread.currentThread().getName());
                Thread t = new Thread(r, "worker");
                t.run();     // an ordinary method call — runs on main, no new thread
                t.start();   // creates the new call stack and calls run() there
                t.join();
                try {
                    t.start();   // a Thread object can be started only once
                } catch (IllegalThreadStateException e) {
                    System.out.println("second start(): " + e.getClass().getSimpleName());
                }
            }
        }
    ''', out="""
        running in main
        running in worker
        second start(): IllegalThreadStateException
    """)
    yield section("Thread lifecycle", "refresh")
    yield flow("`NEW`", "`RUNNABLE`", "`BLOCKED` / `WAITING` / `TIMED_WAITING`", "`RUNNABLE`", "`TERMINATED`")
    yield table(
        ["`Thread.State`", "Meaning", "Entered by"],
        ["`NEW`", "Created, not yet started", "`new Thread(...)`"],
        ["`RUNNABLE`", "Running *or* ready to run (the JVM doesn't distinguish)", "`start()`; also while doing blocking I/O"],
        ["`BLOCKED`", "Waiting to acquire a monitor lock", "entering a `synchronized` block held by another thread"],
        ["`WAITING`", "Waiting indefinitely for another thread", "`wait()`, `join()`, `LockSupport.park()`"],
        ["`TIMED_WAITING`", "Waiting with a timeout", "`sleep(ms)`, `wait(ms)`, `join(ms)`"],
        ["`TERMINATED`", "`run()` returned or threw", "end of `run()`"],
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Object lock = new Object();
                Thread t = new Thread(() -> {
                    synchronized (lock) { System.out.println("worker got the lock"); }
                });
                System.out.println("before start: " + t.getState());
                synchronized (lock) {                      // main holds the lock...
                    t.start();
                    while (t.getState() != Thread.State.BLOCKED) Thread.onSpinWait();
                    System.out.println("waiting for lock: " + t.getState());
                }                                          // ...and releases it here
                t.join();
                System.out.println("after join: " + t.getState());
            }
        }
    ''', out="""
        before start: NEW
        waiting for lock: BLOCKED
        worker got the lock
        after join: TERMINATED
    """)
    yield section("`sleep`, interrupt and daemon threads", "hand-stop")
    yield p("Java has no safe way to *kill* a thread (`stop()` is deprecated and removed in practice). Instead you **interrupt** it — a polite request the thread must check for. Blocking calls (`sleep`, `wait`, `join`, `BlockingQueue.take`) respond by throwing `InterruptedException` and *clearing* the flag.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Thread sleeper = new Thread(() -> {
                    try {
                        Thread.sleep(10_000);
                        System.out.println("woke normally");
                    } catch (InterruptedException e) {
                        System.out.println("sleep interrupted, flag now " + Thread.currentThread().isInterrupted());
                    }
                });
                sleeper.start();
                sleeper.interrupt();
                sleeper.join();

                Thread spinner = new Thread(() -> {
                    long n = 0;
                    while (!Thread.currentThread().isInterrupted()) n++;   // cooperative check
                    System.out.println("spinner saw the interrupt and stopped");
                });
                spinner.start();
                spinner.interrupt();
                spinner.join();

                Thread daemon = new Thread(() -> {
                    while (true) {
                        try { Thread.sleep(1000); } catch (InterruptedException e) { return; }
                    }
                });
                daemon.setDaemon(true);          // must be set before start()
                daemon.start();
                System.out.println("daemon? " + daemon.isDaemon() + " - JVM exits without waiting for it");
            }
        }
    ''', out="""
        sleep interrupted, flag now false
        spinner saw the interrupt and stopped
        daemon? true - JVM exits without waiting for it
    """)
    yield table(
        ["Method", "What it does"],
        ["`Thread.sleep(ms)`", "Pause the *current* thread; keeps any locks it holds"],
        ["`t.join()` / `t.join(ms)`", "Wait until `t` terminates (happens-before: you see all its writes)"],
        ["`t.interrupt()`", "Set `t`'s interrupt flag; wakes it from `sleep`/`wait`/`join`"],
        ["`Thread.interrupted()`", "*Static*: test **and clear** the current thread's flag"],
        ["`t.isInterrupted()`", "Test the flag without clearing it"],
        ["`t.setDaemon(true)`", "Background thread — the JVM exits when only daemons remain"],
        ["`Thread.yield()`", "Hint to the scheduler; practically never needed"],
    )
    yield warn("Never swallow `InterruptedException` with an empty `catch`. Either propagate it, or restore the flag with `Thread.currentThread().interrupt()` so code higher up can see the request to stop.")
    yield qa("What is the difference between start() and run()?",
             "`start()` asks the JVM to create a new thread, which then calls `run()` on its own stack. Calling `run()` directly is just a normal method call on the *current* thread — no concurrency. `start()` may be called only once per `Thread` object (`IllegalThreadStateException` otherwise).")
    yield qa("Runnable vs Callable?",
             "`Runnable.run()` returns `void` and cannot throw checked exceptions. `Callable<V>.call()` returns a value and may throw `Exception`. Threads accept only `Runnable`; executors accept both and return a `Future` for either.")
    yield qa("How do you stop a thread?",
             "Cooperatively: call `interrupt()` (or set a `volatile` flag) and have the thread check `isInterrupted()` / catch `InterruptedException` and return. `Thread.stop()` is deprecated because it releases locks mid-update and leaves objects corrupted.")
    yield qa("Does sleep() release the lock?",
             "No. `sleep()` keeps every monitor the thread holds. `wait()` is the one that releases the monitor of the object it is called on while waiting.")


@topic(G, "synchronization", "synchronized, volatile & the Java Memory Model", "lock")
def _():
    yield lead("Shared mutable state + more than one thread = a race. `synchronized` gives *mutual exclusion and visibility*; `volatile` gives *visibility and ordering only*.")
    yield define("Race condition", "the result depends on the timing of threads. The classic case is `count++`, which is really three steps — *read*, *add 1*, *write* — so two threads can read the same old value and one increment is lost.")
    yield section("The lost-update problem", "bug")
    yield snippet("java", r'''
        public class Main {
            static int count = 0;

            public static void main(String[] args) throws InterruptedException {
                Runnable inc = () -> { for (int i = 0; i < 100_000; i++) count++; };
                Thread a = new Thread(inc), b = new Thread(inc);
                a.start(); b.start();
                a.join();  b.join();
                System.out.println("unsafe count = " + count + " (expected 200000)");
            }
        }
    ''')
    yield output("unsafe count = 104072 (expected 200000)", "Output (a typical run — different every time)")
    yield section("The fix: `synchronized`", "lock")
    yield snippet("java", r'''
        public class Main {
            private int count = 0;

            synchronized void increment() { count++; }     // lock = this
            synchronized int get() { return count; }

            public static void main(String[] args) throws InterruptedException {
                Main counter = new Main();
                Runnable inc = () -> { for (int i = 0; i < 100_000; i++) counter.increment(); };
                Thread a = new Thread(inc), b = new Thread(inc);
                a.start(); b.start();
                a.join();  b.join();
                System.out.println("safe count = " + counter.get());
                System.out.println("correct? " + (counter.get() == 200_000));
            }
        }
    ''', out="""
        safe count = 200000
        correct? true
    """)
    yield p("Every object has an **intrinsic lock** (monitor). Only one thread at a time can hold it; others trying to enter a `synchronized` region on the same object go `BLOCKED`.")
    yield table(
        ["Form", "Lock used", "Use when"],
        ["`synchronized void m()`", "`this`", "The whole method touches shared state"],
        ["`static synchronized void m()`", "the `Class` object (`Main.class`)", "Guarding static fields"],
        ["`synchronized (lock) { ... }`", "any object you choose", "Only a few lines need the lock — keep critical sections short"],
    )
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        class Inventory {
            private final Object lock = new Object();      // private lock: outsiders can't grab it
            private final List<String> items = new ArrayList<>();

            void add(String item) {
                String cleaned = item.trim().toLowerCase(); // no lock needed for local work
                synchronized (lock) {                       // lock only the shared mutation
                    items.add(cleaned);
                }
            }

            int size() {
                synchronized (lock) { return items.size(); }
            }
        }
    ''')
    yield warn("An instance lock and a static lock are *different* locks: a `synchronized` instance method and a `static synchronized` method can run at the same time. Also, locking on different objects protects nothing — every access to the shared field must use the *same* lock.")
    yield section("Reentrancy", "repeat")
    yield snippet("java", r'''
        public class Main {
            synchronized void outer() {
                System.out.println("outer holds lock: " + Thread.holdsLock(this));
                inner();              // same thread, same lock — no self-deadlock
            }

            synchronized void inner() {
                System.out.println("inner re-entered the same lock");
            }

            public static void main(String[] args) {
                new Main().outer();
            }
        }
    ''', out="""
        outer holds lock: true
        inner re-entered the same lock
    """)
    yield p("Intrinsic locks are **reentrant**: the JVM keeps a hold count per owning thread, so a synchronized method can call another synchronized method on the same object.")
    yield section("Visibility and the Java Memory Model", "eye")
    yield p("Without synchronisation, a thread may *never see* another thread's write: values can sit in CPU caches or registers, and the compiler/CPU may reorder instructions. The **Java Memory Model (JMM)** defines when a write is guaranteed visible through *happens-before* rules.")
    yield table(
        ["Happens-before rule", "Guarantee"],
        ["Program order", "Each action in a thread happens-before later actions in the same thread"],
        ["Monitor lock", "Unlocking a monitor happens-before every later lock of the *same* monitor"],
        ["`volatile`", "A write to a volatile field happens-before every later read of it"],
        ["Thread start", "`t.start()` happens-before anything `t` does"],
        ["Thread join", "Everything `t` does happens-before `t.join()` returns"],
        ["Transitivity", "A hb B and B hb C ⇒ A hb C"],
    )
    yield section("`volatile`", "bolt")
    yield snippet("java", r'''
        public class Main {
            static volatile boolean running = true;     // try removing volatile: the loop may never end

            public static void main(String[] args) throws InterruptedException {
                Thread worker = new Thread(() -> {
                    long spins = 0;
                    while (running) spins++;
                    System.out.println("worker saw running=false and exited");
                });
                worker.start();
                Thread.sleep(50);
                running = false;                        // visible to the worker immediately
                worker.join();
                System.out.println("done");
            }
        }
    ''', out="""
        worker saw running=false and exited
        done
    """)
    yield table(
        ["", "`volatile`", "`synchronized`"],
        ["Visibility", "Yes", "Yes"],
        ["Prevents reordering around it", "Yes", "Yes"],
        ["Atomic compound actions (`x++`, check-then-act)", "**No**", "Yes"],
        ["Blocks other threads", "Never", "Yes (mutual exclusion)"],
        ["Typical use", "Status flags, safe publication, DCL", "Invariants spanning several fields/steps"],
    )
    yield warn("`volatile int count; count++` is still a race — `volatile` makes each read and write visible but does not make read-modify-write atomic. Use `synchronized`, `AtomicInteger` or `LongAdder`.")
    yield section("Double-checked locking (lazy singleton)", "copy-check")
    yield snippet("java", r'''
        final class Config {
            private static volatile Config instance;    // volatile is essential here

            private Config() { }

            static Config getInstance() {
                Config local = instance;                // 1st check without locking (fast path)
                if (local == null) {
                    synchronized (Config.class) {
                        local = instance;               // 2nd check under the lock
                        if (local == null) {
                            instance = local = new Config();
                        }
                    }
                }
                return local;
            }
        }
    ''')
    yield p("Without `volatile`, the write of the reference could be reordered before the constructor finishes, so another thread might see a *partially constructed* object. Simpler alternatives: an `enum` singleton or the holder idiom (`private static class Holder { static final Config I = new Config(); }`) — class initialisation is already thread-safe and lazy.")
    yield qa("Is `count++` atomic in Java?",
             "No — it compiles to read, add, write (`getfield`, `iadd`, `putfield`). Two threads can interleave and lose updates, even if `count` is `volatile`. Use `synchronized`, `AtomicInteger.incrementAndGet()` or `LongAdder`.")
    yield qa("What does volatile guarantee?",
             "Visibility (a read sees the latest write by any thread) and ordering (no reordering across the volatile access; it creates a happens-before edge). It does *not* give atomicity or mutual exclusion.")
    yield qa("Synchronized method vs synchronized block?",
             "A synchronized method locks `this` (or the `Class` for static methods) for the whole method. A block lets you choose the lock object — often a private final field — and keep the critical section as small as possible, which improves throughput and prevents outside code from locking on your object.")
    yield qa("Why must the double-checked-locking field be volatile?",
             "`instance = new Config()` is allocate → construct → assign, and the JIT/CPU may publish the reference before construction completes. `volatile` forbids that reordering, so a thread that sees a non-null reference also sees a fully initialised object.")


@topic(G, "wait-notify", "wait/notify & Producer–Consumer", "arrows-exchange")
def _():
    yield lead("`wait()` and `notify()` let threads *coordinate* — sleep until a condition becomes true — instead of busy-spinning. In modern code a `BlockingQueue` usually does this for you.")
    yield define("Guarded wait", "a thread holding an object's monitor calls `wait()` in a `while (!condition)` loop: it releases the monitor and sleeps until another thread calls `notify()`/`notifyAll()` on the same object, then re-acquires the monitor and re-checks the condition.")
    yield section("The rules", "list-check")
    yield table(
        ["Method (on `Object`)", "Effect"],
        ["`wait()`", "Release this object's monitor and wait (state `WAITING`) until notified or interrupted"],
        ["`wait(ms)`", "Same, with a timeout (`TIMED_WAITING`)"],
        ["`notify()`", "Wake *one* arbitrary waiting thread"],
        ["`notifyAll()`", "Wake *all* waiting threads — they compete for the monitor and re-check their conditions"],
    )
    yield ul(
        "All three must be called while holding the object's monitor (inside `synchronized (obj)`), otherwise `IllegalMonitorStateException`.",
        "Always wait in a **`while`** loop, never `if`: threads can wake *spuriously*, and another thread may have consumed the condition first.",
        "Prefer `notifyAll()` unless all waiters are interchangeable and only one can proceed.",
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Object o = new Object();
                try {
                    o.wait();                           // not holding o's monitor!
                } catch (IllegalMonitorStateException | InterruptedException e) {
                    System.out.println(e.getClass().getSimpleName());
                }
            }
        }
    ''', out="IllegalMonitorStateException")
    yield section("A bounded buffer with wait/notifyAll", "stack-push")
    yield snippet("java", r'''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                BoundedBuffer buf = new BoundedBuffer(2);
                Thread producer = new Thread(() -> {
                    try {
                        for (int i = 1; i <= 5; i++) buf.put(i);
                        buf.put(-1);                              // poison pill: "no more items"
                    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                });
                Thread consumer = new Thread(() -> {
                    try {
                        int sum = 0;
                        for (int x; (x = buf.take()) != -1; ) {
                            System.out.println("consumed " + x);
                            sum += x;
                        }
                        System.out.println("sum = " + sum);
                    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                });
                producer.start(); consumer.start();
                producer.join();  consumer.join();
            }
        }

        class BoundedBuffer {
            private final Queue<Integer> items = new ArrayDeque<>();
            private final int capacity;

            BoundedBuffer(int capacity) { this.capacity = capacity; }

            synchronized void put(int x) throws InterruptedException {
                while (items.size() == capacity) wait();   // full: wait for space
                items.add(x);
                notifyAll();                               // wake consumers
            }

            synchronized int take() throws InterruptedException {
                while (items.isEmpty()) wait();            // empty: wait for data
                int x = items.remove();
                notifyAll();                               // wake producers
                return x;
            }
        }
    ''', out="""
        consumed 1
        consumed 2
        consumed 3
        consumed 4
        consumed 5
        sum = 15
    """)
    yield section("The modern way: `BlockingQueue`", "list-details")
    yield snippet("java", r'''
        import java.util.concurrent.ArrayBlockingQueue;
        import java.util.concurrent.BlockingQueue;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);
                Thread producer = new Thread(() -> {
                    try {
                        for (String job : new String[]{"resize", "upload", "notify"}) queue.put(job);
                        queue.put("DONE");
                    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                });
                producer.start();
                for (String job; !(job = queue.take()).equals("DONE"); ) {
                    System.out.println("processing " + job);
                }
                producer.join();
                System.out.println("queue empty: " + queue.isEmpty());
            }
        }
    ''', out="""
        processing resize
        processing upload
        processing notify
        queue empty: true
    """)
    yield table(
        ["`BlockingQueue` op", "Full / empty behaviour"],
        ["`put(e)` / `take()`", "Block until space / an element is available"],
        ["`offer(e)` / `poll()`", "Return `false` / `null` immediately"],
        ["`offer(e, t, unit)` / `poll(t, unit)`", "Block up to a timeout"],
        ["`add(e)` / `remove()`", "Throw an exception"],
    )
    yield p("Implementations: `ArrayBlockingQueue` (bounded, array), `LinkedBlockingQueue` (optionally bounded), `PriorityBlockingQueue`, `SynchronousQueue` (capacity 0 — a direct hand-off), `DelayQueue`.")
    yield section("Deadlock", "lock-off")
    yield define("Deadlock", "two or more threads each hold a lock the other needs, so all wait forever. It needs all four Coffman conditions: mutual exclusion, hold-and-wait, no preemption, circular wait.")
    yield p("Here T1 locks `a` then wants `b`, while T2 locks `b` then wants `a`. The latch makes the bad interleaving certain; the JVM's `ThreadMXBean` detects the cycle (the same thing `jstack` reports).")
    yield snippet("java", r'''
        import java.lang.management.ManagementFactory;
        import java.lang.management.ThreadMXBean;
        import java.util.concurrent.CountDownLatch;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Object a = new Object(), b = new Object();
                CountDownLatch bothHoldOne = new CountDownLatch(2);
                Thread t1 = worker("T1", a, b, bothHoldOne);
                Thread t2 = worker("T2", b, a, bothHoldOne);   // opposite order!
                t1.start(); t2.start();
                while (t1.getState() != Thread.State.BLOCKED || t2.getState() != Thread.State.BLOCKED) {
                    Thread.sleep(10);
                }
                ThreadMXBean mx = ManagementFactory.getThreadMXBean();
                System.out.println("deadlocked threads: " + mx.findDeadlockedThreads().length);
                System.out.println("T1 waits for a lock owned by " + mx.getThreadInfo(t1.threadId()).getLockOwnerName());
                System.out.println("T2 waits for a lock owned by " + mx.getThreadInfo(t2.threadId()).getLockOwnerName());
            }

            static Thread worker(String name, Object first, Object second, CountDownLatch latch) {
                Thread t = new Thread(() -> {
                    synchronized (first) {
                        latch.countDown();
                        try { latch.await(); } catch (InterruptedException e) { return; }
                        synchronized (second) { System.out.println(name + " finished"); }
                    }
                }, name);
                t.setDaemon(true);                 // lets the JVM exit despite the deadlock
                return t;
            }
        }
    ''', out="""
        deadlocked threads: 2
        T1 waits for a lock owned by T2
        T2 waits for a lock owned by T1
    """)
    yield section("Avoiding deadlock: a global lock order", "sort-ascending")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Account x = new Account(1, 1000), y = new Account(2, 1000);
                Thread t1 = new Thread(() -> { for (int i = 0; i < 1000; i++) transfer(x, y, 1); });
                Thread t2 = new Thread(() -> { for (int i = 0; i < 1000; i++) transfer(y, x, 2); });
                t1.start(); t2.start();
                t1.join();  t2.join();
                System.out.println("x = " + x.balance + ", y = " + y.balance + ", total = " + (x.balance + y.balance));
            }

            static void transfer(Account from, Account to, int amount) {
                Account first = from.id < to.id ? from : to;   // always lock the lower id first
                Account second = first == from ? to : from;
                synchronized (first) {
                    synchronized (second) {
                        from.balance -= amount;
                        to.balance += amount;
                    }
                }
            }
        }

        class Account {
            final int id;
            int balance;
            Account(int id, int balance) { this.id = id; this.balance = balance; }
        }
    ''', out="x = 2000, y = 0, total = 2000")
    yield cards(
        ("Lock ordering", "Acquire locks in one global order (by id, by `System.identityHashCode`) — breaks circular wait.", "sort-ascending"),
        ("Timeouts", "`ReentrantLock.tryLock(timeout)` — give up, release what you hold, retry.", "clock"),
        ("Fewer locks", "Hold one lock at a time; never call unknown (alien) code while holding a lock.", "lock-open"),
        ("Higher-level tools", "Concurrent collections, executors and immutable data remove most explicit locking.", "tools"),
    )
    yield warn("Other liveness failures: **livelock** (threads keep reacting to each other and make no progress), **starvation** (a thread never gets the lock/CPU — e.g. unfair locks under heavy contention).")
    yield qa("Why must wait() be called inside a while loop?",
             "Because waking up does not mean the condition is true: *spurious wakeups* are allowed, `notifyAll()` wakes threads whose condition may still be false, and another thread may grab the monitor and consume the item first. Re-checking in a `while` handles all three.")
    yield qa("wait() vs sleep()?",
             "`wait()` is an `Object` method, must hold that object's monitor, *releases* it and waits for a notify. `sleep()` is a static `Thread` method, needs no lock, and keeps all locks it holds. Both throw `InterruptedException`.")
    yield qa("Why are wait/notify defined on Object and not Thread?",
             "Because they operate on a *monitor*, and every object is a monitor. Threads wait on the condition guarded by a particular object's lock, so the methods belong to the lock object.")
    yield qa("How do you detect a deadlock in production?",
             "Take a thread dump (`jstack <pid>`, `jcmd <pid> Thread.print`, or VisualVM/JMC) — it prints \"Found one Java-level deadlock\" with the cycle. Programmatically, `ThreadMXBean.findDeadlockedThreads()`.")


@topic(G, "executors", "ExecutorService & Thread Pools", "server-2")
def _():
    yield lead("Don't create a thread per task — submit tasks to an `ExecutorService`, which reuses a pool of threads and gives you `Future`s for the results.")
    yield define("ExecutorService", "an `Executor` (runs `Runnable`s) that also manages its own lifecycle (`shutdown`) and returns a `Future` for each submitted `Runnable`/`Callable`.")
    yield section("Why a pool?", "bulb")
    yield cards(
        ("Reuse", "Creating a platform thread costs a syscall and ~1 MB of stack. A pool pays it once.", "recycle"),
        ("Bounded resources", "10 000 requests don't become 10 000 threads — the queue absorbs bursts.", "gauge"),
        ("Results & errors", "`Future.get()` returns the value or rethrows the task's exception.", "package"),
        ("Separation", "Business code submits tasks; the pool decides how and where they run.", "arrows-split-2"),
    )
    yield section("submit, Future and invokeAll", "code")
    yield snippet("java", r'''
        import java.util.List;
        import java.util.concurrent.*;

        public class Main {
            public static void main(String[] args) throws Exception {
                ExecutorService pool = Executors.newFixedThreadPool(3);
                try {
                    Future<Integer> f = pool.submit(() -> 6 * 7);          // Callable<Integer>
                    System.out.println("answer = " + f.get());            // blocks until done

                    List<Callable<String>> tasks = List.of(() -> "a".repeat(3), () -> "b".repeat(2), () -> "c");
                    for (Future<String> r : pool.invokeAll(tasks)) {       // results in task order
                        System.out.println(r.get());
                    }

                    Future<?> g = pool.submit(() -> { });                  // Runnable
                    System.out.println("runnable result = " + g.get());

                    Future<Integer> bad = pool.submit(() -> 1 / 0);
                    try {
                        bad.get();
                    } catch (ExecutionException e) {                        // the task's exception is wrapped
                        System.out.println("cause: " + e.getCause());
                    }
                } finally {
                    pool.shutdown();                                        // stop accepting, finish queued
                    System.out.println("terminated = " + pool.awaitTermination(1, TimeUnit.SECONDS));
                }
            }
        }
    ''', out="""
        answer = 42
        aaa
        bb
        c
        runnable result = null
        cause: java.lang.ArithmeticException: / by zero
        terminated = true
    """)
    yield table(
        ["`Future` method", "Purpose"],
        ["`get()` / `get(t, unit)`", "Wait for the result; throws `ExecutionException` (task failed), `TimeoutException`, `InterruptedException`"],
        ["`isDone()`", "Completed normally, exceptionally or cancelled"],
        ["`cancel(mayInterrupt)`", "Try to cancel; `true` interrupts a running task"],
        ["`resultNow()` / `state()`", "Java 19+: read a completed result without checked exceptions"],
    )
    yield section("Executors factory methods", "building-factory")
    yield table(
        ["Factory", "Pool", "Watch out"],
        ["`newFixedThreadPool(n)`", "`n` threads, unbounded `LinkedBlockingQueue`", "Queue can grow until `OutOfMemoryError`"],
        ["`newCachedThreadPool()`", "0…∞ threads, idle ones die after 60 s, `SynchronousQueue`", "Unbounded *threads* under load"],
        ["`newSingleThreadExecutor()`", "1 thread, tasks run sequentially in order", "Same unbounded queue"],
        ["`newScheduledThreadPool(n)`", "Delayed / periodic tasks (`schedule`, `scheduleAtFixedRate`)", "Replaces `java.util.Timer`"],
        ["`newWorkStealingPool()`", "`ForkJoinPool` with one queue per worker", "Good for many small CPU tasks"],
        ["`newVirtualThreadPerTaskExecutor()`", "Java 21: one virtual thread per task", "For blocking I/O workloads"],
    )
    yield section("Shutting down", "power")
    yield steps(
        ("`shutdown()`", "No new tasks accepted; already submitted ones still run."),
        ("`awaitTermination(t, unit)`", "Block until all tasks finish or the timeout elapses; returns `true` if terminated."),
        ("`shutdownNow()`", "Interrupt running tasks and return the ones never started (tasks must respond to interrupts)."),
    )
    yield p("Since Java 19 `ExecutorService` is `AutoCloseable`: `close()` calls `shutdown()` and waits for every task, so try-with-resources is the tidiest pattern.")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.concurrent.ExecutorService;
        import java.util.concurrent.Executors;
        import java.util.concurrent.Future;

        public class Main {
            public static void main(String[] args) throws Exception {
                List<Future<Integer>> squares = new ArrayList<>();
                try (ExecutorService pool = Executors.newFixedThreadPool(4)) {
                    for (int i = 1; i <= 5; i++) {
                        int n = i;
                        squares.add(pool.submit(() -> n * n));
                    }
                }                                   // close(): shutdown + wait for all tasks
                int total = 0;
                for (Future<Integer> f : squares) total += f.resultNow();
                System.out.println("sum of squares = " + total);
            }
        }
    ''', out="sum of squares = 55")
    yield warn("A pool that is never shut down keeps its non-daemon threads alive, so the JVM never exits. And a forgotten `Future` hides exceptions: `execute()` prints an uncaught task exception, but `submit()` stores it in the `Future` until someone calls `get()`.")
    yield section("ThreadPoolExecutor: the real knobs", "adjustments")
    yield table(
        ["Parameter", "Meaning"],
        ["`corePoolSize`", "Threads kept alive even when idle"],
        ["`maximumPoolSize`", "Upper bound — extra threads are created only when the queue is **full**"],
        ["`keepAliveTime`", "How long threads above core may stay idle"],
        ["`workQueue`", "Where waiting tasks go: bounded `ArrayBlockingQueue` recommended"],
        ["`threadFactory`", "Name threads (`order-worker-1`), set daemon/priority"],
        ["`handler`", "Rejection policy when both queue and max threads are full"],
    )
    yield flow("task arrives", "threads < core? new thread", "else queue it", "queue full? thread up to max", "else reject")
    yield snippet("java", r'''
        import java.util.concurrent.*;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                CountDownLatch gate = new CountDownLatch(1);
                ThreadPoolExecutor pool = new ThreadPoolExecutor(
                    1, 1, 0, TimeUnit.SECONDS,                 // exactly one thread
                    new ArrayBlockingQueue<>(1),               // room for one waiting task
                    new ThreadPoolExecutor.AbortPolicy());     // default: throw when full
                Runnable blocker = () -> {
                    try { gate.await(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                };
                pool.execute(blocker);                         // runs on the only thread
                pool.execute(blocker);                         // waits in the queue
                try {
                    pool.execute(blocker);                     // no thread, no queue space
                } catch (RejectedExecutionException e) {
                    System.out.println("3rd task rejected");
                }
                System.out.println("pool size = " + pool.getPoolSize() + ", queued = " + pool.getQueue().size());
                gate.countDown();
                pool.shutdown();
                pool.awaitTermination(1, TimeUnit.SECONDS);
                System.out.println("completed = " + pool.getCompletedTaskCount());
            }
        }
    ''', out="""
        3rd task rejected
        pool size = 1, queued = 1
        completed = 2
    """)
    yield table(
        ["Rejection policy", "Behaviour"],
        ["`AbortPolicy` (default)", "Throw `RejectedExecutionException`"],
        ["`CallerRunsPolicy`", "Run the task on the submitting thread — natural back-pressure"],
        ["`DiscardPolicy`", "Silently drop the new task"],
        ["`DiscardOldestPolicy`", "Drop the oldest queued task, retry the new one"],
    )
    yield section("How many threads?", "calculator")
    yield formula("`threads ≈ cores × (1 + wait time / compute time)`")
    yield ul(
        "**CPU-bound** (hashing, parsing, math): about `Runtime.getRuntime().availableProcessors()` threads — more only adds context switching.",
        "**I/O-bound** (HTTP calls, DB queries): many more, since threads mostly wait. On Java 21 prefer virtual threads here.",
        "Use separate pools for separate kinds of work, so a slow dependency can't starve everything (bulkheads).",
    )
    yield qa("submit() vs execute()?",
             "`execute(Runnable)` comes from `Executor`, returns nothing, and an exception goes to the thread's uncaught-exception handler. `submit()` accepts `Runnable` or `Callable`, returns a `Future`, and captures any exception inside it (rethrown as `ExecutionException` from `get()`).")
    yield qa("Why is Executors.newFixedThreadPool considered risky in production?",
             "Its `LinkedBlockingQueue` is unbounded: if producers outpace workers, tasks pile up until `OutOfMemoryError`. Construct a `ThreadPoolExecutor` with a bounded queue, named threads and an explicit rejection policy instead.")
    yield qa("When does a ThreadPoolExecutor create threads beyond corePoolSize?",
             "Only when the work queue is full. With an unbounded queue, `maximumPoolSize` is never reached — a common surprise.")
    yield qa("shutdown() vs shutdownNow()?",
             "`shutdown()` is graceful: no new tasks, queued and running tasks complete. `shutdownNow()` interrupts running tasks, drains the queue and returns the unstarted tasks. Follow either with `awaitTermination` to actually wait.")


@topic(G, "completablefuture", "CompletableFuture", "git-merge")
def _():
    yield lead("`CompletableFuture` composes asynchronous steps into a pipeline — transform, chain, combine and recover — without blocking a thread on each `get()`.")
    yield define("CompletableFuture<T>", "a `Future` you can complete explicitly *and* a `CompletionStage`: attach callbacks (`thenApply`, `thenCompose`, …) that run when the value is ready. Async methods run on `ForkJoinPool.commonPool()` unless you pass an `Executor`.")
    yield section("Transform and combine", "arrows-join")
    yield snippet("java", r'''
        import java.util.concurrent.CompletableFuture;

        public class Main {
            public static void main(String[] args) {
                CompletableFuture<Integer> price = CompletableFuture.supplyAsync(() -> 200);
                CompletableFuture<Double> discount = CompletableFuture.supplyAsync(() -> 0.9);

                double total = price
                    .thenCombine(discount, (p, d) -> p * d)   // wait for BOTH, merge
                    .thenApply(x -> x + 15)                   // transform the value (shipping)
                    .join();                                  // block for the final result
                System.out.println("total = " + total);

                CompletableFuture.supplyAsync(() -> "order-42")
                    .thenApply(String::toUpperCase)
                    .thenAccept(id -> System.out.println("placed " + id))   // consume, returns CF<Void>
                    .thenRun(() -> System.out.println("email queued"))      // no input, no output
                    .join();
            }
        }
    ''', out="""
        total = 195.0
        placed ORDER-42
        email queued
    """)
    yield section("thenApply vs thenCompose", "git-branch")
    yield p("`thenApply` is `map`: the function returns a plain value. `thenCompose` is `flatMap`: the function itself returns a `CompletableFuture`, and you want the inner result — not a nested `CompletableFuture<CompletableFuture<T>>`.")
    yield snippet("java", r'''
        import java.util.List;
        import java.util.concurrent.CompletableFuture;

        public class Main {
            static CompletableFuture<String> findUser(int id) {
                return CompletableFuture.supplyAsync(() -> "user" + id);
            }

            static CompletableFuture<List<String>> findOrders(String user) {
                return CompletableFuture.supplyAsync(() -> List.of(user + ":book", user + ":pen"));
            }

            public static void main(String[] args) {
                List<String> orders = findUser(7)
                    .thenCompose(Main::findOrders)        // async step depending on the previous one
                    .join();
                System.out.println(orders);
            }
        }
    ''', out="[user7:book, user7:pen]")
    yield table(
        ["Method", "Function shape", "Analogy"],
        ["`thenApply(f)`", "`T -> U`", "`map`"],
        ["`thenCompose(f)`", "`T -> CompletionStage<U>`", "`flatMap` — sequential async calls"],
        ["`thenCombine(other, f)`", "`(T, U) -> V`", "zip two independent futures"],
        ["`thenAccept(c)` / `thenRun(r)`", "`T -> void` / `() -> void`", "side effect at the end"],
        ["`allOf(cfs...)`", "→ `CompletableFuture<Void>`", "wait for all"],
        ["`anyOf(cfs...)`", "→ `CompletableFuture<Object>`", "first to finish wins"],
        ["`...Async` variants", "same, but callback runs on the pool", "don't hog the completing thread"],
    )
    yield section("Waiting for many: allOf", "stack-2")
    yield snippet("java", r'''
        import java.util.List;
        import java.util.concurrent.CompletableFuture;

        public class Main {
            public static void main(String[] args) {
                List<CompletableFuture<Integer>> calls = List.of("alpha", "beta", "gamma").stream()
                    .map(s -> CompletableFuture.supplyAsync(() -> s.length()))
                    .toList();

                CompletableFuture.allOf(calls.toArray(new CompletableFuture[0])).join();
                List<Integer> lengths = calls.stream().map(CompletableFuture::join).toList();  // all done: no waiting
                System.out.println(lengths + " sum=" + lengths.stream().mapToInt(Integer::intValue).sum());
            }
        }
    ''', out="[5, 4, 5] sum=14")
    yield section("Handling errors", "alert-triangle")
    yield snippet("java", r'''
        import java.util.concurrent.CompletableFuture;
        import java.util.concurrent.CompletionException;
        import java.util.concurrent.ExecutionException;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                CompletableFuture<Integer> failing = CompletableFuture.supplyAsync(() -> Integer.parseInt("x"));

                int recovered = failing.exceptionally(ex -> -1).join();          // fallback value
                System.out.println("exceptionally -> " + recovered);

                String handled = failing.handle((value, ex) ->                   // sees success OR failure
                    ex == null ? "ok " + value : "failed: " + ex.getCause().getClass().getSimpleName()).join();
                System.out.println("handle -> " + handled);

                try {
                    failing.join();                                              // unchecked wrapper
                } catch (CompletionException e) {
                    System.out.println("join threw CompletionException, cause " + e.getCause().getClass().getSimpleName());
                }
                try {
                    failing.get();                                               // checked wrapper
                } catch (ExecutionException e) {
                    System.out.println("get threw ExecutionException, cause " + e.getCause().getClass().getSimpleName());
                }
            }
        }
    ''', out="""
        exceptionally -> -1
        handle -> failed: NumberFormatException
        join threw CompletionException, cause NumberFormatException
        get threw ExecutionException, cause NumberFormatException
    """)
    yield table(
        ["Method", "Called on", "Can change result?"],
        ["`exceptionally(fn)`", "failure only", "Yes — supply a fallback"],
        ["`handle((v, ex) -> ...)`", "success and failure", "Yes — map either to a new value"],
        ["`whenComplete((v, ex) -> ...)`", "success and failure", "No — side effects (logging); original result passes through"],
        ["`orTimeout(t, unit)` / `completeOnTimeout(v, t, unit)`", "Java 9+", "Fail / default after a timeout"],
    )
    yield section("Use your own executor", "server")
    yield snippet("java", r'''
        import java.util.concurrent.CompletableFuture;
        import java.util.concurrent.ExecutorService;
        import java.util.concurrent.Executors;

        public class Main {
            public static void main(String[] args) {
                try (ExecutorService io = Executors.newFixedThreadPool(2, r -> new Thread(r, "io-worker"))) {
                    String where = CompletableFuture
                        .supplyAsync(() -> Thread.currentThread().getName(), io)   // runs on our pool
                        .join();
                    System.out.println("ran on " + where);
                }
            }
        }
    ''', out="ran on io-worker")
    yield warn("The common `ForkJoinPool` is sized for CPU work (cores − 1 threads) and shared by the whole JVM, including parallel streams. Blocking I/O in `supplyAsync(...)` without an executor can starve everything else — pass a dedicated executor (or virtual threads).")
    yield qa("join() vs get()?",
             "Both block for the result. `get()` throws checked `InterruptedException` and `ExecutionException`; `join()` throws unchecked `CompletionException`, which makes it usable inside lambdas and stream pipelines.")
    yield qa("thenApply vs thenCompose?",
             "`thenApply` maps the result with a function returning a value. `thenCompose` is for a function that returns another `CompletionStage` — it flattens, so dependent async calls chain as `CF<U>` instead of `CF<CF<U>>`.")
    yield qa("Future vs CompletableFuture?",
             "A plain `Future` only lets you poll or block with `get()`. `CompletableFuture` can be completed manually (`complete`, `completeExceptionally`), supports non-blocking callbacks, composition (`thenCompose`, `thenCombine`, `allOf`) and error recovery (`exceptionally`, `handle`).")


@topic(G, "concurrent-utilities", "ConcurrentHashMap, Atomics & Locks", "tools")
def _():
    yield lead("`java.util.concurrent` replaces most hand-written `synchronized`/`wait` code with tested building blocks: concurrent collections, atomic variables, explicit locks and synchronizers.")
    yield section("Thread-safe maps compared", "table")
    yield table(
        ["", "`Hashtable`", "`Collections.synchronizedMap`", "`ConcurrentHashMap`"],
        ["Locking", "Every method locks the whole table", "Every method locks one mutex", "CAS + per-bin locks; reads are lock-free"],
        ["Concurrent reads/writes", "No", "No", "Yes"],
        ["`null` keys/values", "Not allowed", "Allowed (if the backing map allows)", "**Not allowed**"],
        ["Iteration while modifying", "Fail-fast", "Must lock manually; else CME", "Weakly consistent, never throws CME"],
        ["Atomic compound ops", "No", "No", "`merge`, `compute`, `putIfAbsent`…"],
        ["Status", "Legacy", "Simple wrapper", "Default choice"],
    )
    yield snippet("java", r'''
        import java.util.List;
        import java.util.TreeMap;
        import java.util.concurrent.ConcurrentHashMap;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                ConcurrentHashMap<String, Integer> counts = new ConcurrentHashMap<>();
                List<String> words = List.of("a", "b", "a", "c", "a", "b");

                Runnable countAll = () -> { for (String w : words) counts.merge(w, 1, Integer::sum); };  // atomic
                Thread[] ts = new Thread[4];
                for (int i = 0; i < ts.length; i++) (ts[i] = new Thread(countAll)).start();
                for (Thread t : ts) t.join();

                System.out.println(new TreeMap<>(counts));     // sorted for display
                counts.computeIfAbsent("d", k -> 0);
                counts.compute("d", (k, v) -> v + 100);
                System.out.println("d = " + counts.get("d") + ", size = " + counts.size());
            }
        }
    ''', out="""
        {a=12, b=8, c=4}
        d = 100, size = 4
        """)
    yield warn("`if (!map.containsKey(k)) map.put(k, v);` is a check-then-act race even on a `ConcurrentHashMap` — each call is atomic, the pair is not. Use `putIfAbsent`, `computeIfAbsent` or `merge`.")
    yield section("Atomic variables and CAS", "atom")
    yield define("CAS (compare-and-swap)", "a single CPU instruction: *if the value is still `expected`, set it to `new`*. Atomic classes retry CAS in a loop, giving lock-free thread safety for single variables.")
    yield snippet("java", r'''
        import java.util.concurrent.atomic.AtomicInteger;
        import java.util.concurrent.atomic.LongAdder;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                AtomicInteger a = new AtomicInteger(5);
                System.out.println(a.compareAndSet(5, 10) + " " + a.get());   // expected 5: swap
                System.out.println(a.compareAndSet(5, 20) + " " + a.get());   // stale expectation: no swap
                System.out.println(a.updateAndGet(x -> x * 3));
                System.out.println(a.getAndIncrement() + " then " + a.get());

                AtomicInteger hits = new AtomicInteger();
                LongAdder adder = new LongAdder();
                Runnable work = () -> {
                    for (int i = 0; i < 10_000; i++) { hits.incrementAndGet(); adder.increment(); }
                };
                Thread[] ts = new Thread[4];
                for (int i = 0; i < ts.length; i++) (ts[i] = new Thread(work)).start();
                for (Thread t : ts) t.join();
                System.out.println("AtomicInteger = " + hits.get() + ", LongAdder = " + adder.sum());
            }
        }
    ''', out="""
        true 10
        false 10
        30
        30 then 31
        AtomicInteger = 40000, LongAdder = 40000
    """)
    yield table(
        ["Class", "Use"],
        ["`AtomicInteger` / `AtomicLong`", "Counters, sequence numbers, `compareAndSet` state machines"],
        ["`AtomicBoolean`", "Run-once flags (`if (started.compareAndSet(false, true))`)"],
        ["`AtomicReference<V>`", "Swap an immutable object atomically"],
        ["`LongAdder`", "Hot counters under heavy contention — cells per thread, summed on read"],
        ["`AtomicIntegerArray`", "Per-index atomic updates"],
    )
    yield note("ABA problem: CAS only checks the *value*, so A → B → A looks unchanged. When it matters (lock-free stacks), use `AtomicStampedReference`, which pairs the reference with a version stamp.")
    yield section("ReentrantLock and Condition", "lock-access")
    yield p("An explicit `Lock` does what `synchronized` does plus: try without blocking, time out, be interrupted while waiting, optional fairness, and several wait-sets (`Condition`s) per lock.")
    yield snippet("java", r'''
        import java.util.concurrent.locks.ReentrantLock;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                ReentrantLock lock = new ReentrantLock();
                lock.lock();                                   // main holds it
                try {
                    Thread t = new Thread(() -> System.out.println("worker tryLock: " + lock.tryLock()));
                    t.start();
                    t.join();
                } finally {
                    lock.unlock();                             // ALWAYS unlock in finally
                }
                Thread t2 = new Thread(() -> {
                    if (lock.tryLock()) {
                        try { System.out.println("worker tryLock after unlock: true"); }
                        finally { lock.unlock(); }
                    }
                });
                t2.start();
                t2.join();
                System.out.println("held now? " + lock.isLocked());
            }
        }
    ''', out="""
        worker tryLock: false
        worker tryLock after unlock: true
        held now? false
    """)
    yield snippet("java", r'''
        import java.util.ArrayDeque;
        import java.util.Deque;
        import java.util.concurrent.locks.Condition;
        import java.util.concurrent.locks.ReentrantLock;

        class LockBuffer<T> {
            private final Deque<T> items = new ArrayDeque<>();
            private final int capacity;
            private final ReentrantLock lock = new ReentrantLock();
            private final Condition notFull = lock.newCondition();    // two separate wait-sets
            private final Condition notEmpty = lock.newCondition();

            LockBuffer(int capacity) { this.capacity = capacity; }

            void put(T x) throws InterruptedException {
                lock.lock();
                try {
                    while (items.size() == capacity) notFull.await();
                    items.addLast(x);
                    notEmpty.signal();              // wake only a consumer
                } finally {
                    lock.unlock();
                }
            }

            T take() throws InterruptedException {
                lock.lock();
                try {
                    while (items.isEmpty()) notEmpty.await();
                    T x = items.removeFirst();
                    notFull.signal();               // wake only a producer
                    return x;
                } finally {
                    lock.unlock();
                }
            }
        }
    ''', caption="Java — Condition (compile-checked)")
    yield table(
        ["", "`synchronized`", "`ReentrantLock`"],
        ["Release", "Automatic at block end", "Manual `unlock()` in `finally`"],
        ["Try / timeout", "No", "`tryLock()`, `tryLock(t, unit)`"],
        ["Interruptible wait for lock", "No", "`lockInterruptibly()`"],
        ["Fairness", "No", "`new ReentrantLock(true)` (FIFO-ish, slower)"],
        ["Conditions", "One wait-set (`wait`/`notify`)", "Many (`newCondition()`)"],
        ["Reentrant", "Yes", "Yes"],
    )
    yield p("`ReentrantReadWriteLock` lets many readers in at once but writers alone — good for read-mostly data. `StampedLock` (Java 8) adds optimistic reads for even cheaper read paths.")
    yield section("Synchronizers", "users-group")
    yield table(
        ["Tool", "What it does", "Reusable?", "Typical use"],
        ["`CountDownLatch(n)`", "`await()` blocks until `countDown()` was called `n` times", "No", "Wait for N services to start / N tasks to finish"],
        ["`CyclicBarrier(n, action)`", "`n` threads wait for each other, then all continue", "Yes", "Phased parallel algorithms"],
        ["`Semaphore(permits)`", "`acquire()`/`release()` permits", "Yes", "Limit concurrency (max 10 DB connections)"],
        ["`Phaser`", "Flexible barrier with dynamic parties", "Yes", "Multi-phase work with join/leave"],
        ["`Exchanger`", "Two threads swap objects", "Yes", "Pipeline buffers"],
    )
    yield snippet("java", r'''
        import java.util.List;
        import java.util.concurrent.*;
        import java.util.concurrent.atomic.AtomicInteger;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                // CountDownLatch: wait for 3 workers
                CountDownLatch done = new CountDownLatch(3);
                List<String> results = new CopyOnWriteArrayList<>();
                for (String svc : List.of("db", "cache", "queue")) {
                    new Thread(() -> { results.add(svc + " ready"); done.countDown(); }).start();
                }
                done.await();
                System.out.println(results.stream().sorted().toList());

                // Semaphore: at most 2 tasks inside at once
                Semaphore permits = new Semaphore(2);
                AtomicInteger inside = new AtomicInteger(), maxInside = new AtomicInteger();
                try (ExecutorService pool = Executors.newFixedThreadPool(6)) {
                    for (int i = 0; i < 6; i++) {
                        pool.submit(() -> {
                            permits.acquire();
                            try {
                                maxInside.accumulateAndGet(inside.incrementAndGet(), Math::max);
                                Thread.sleep(20);
                                inside.decrementAndGet();
                            } finally {
                                permits.release();
                            }
                            return null;
                        });
                    }
                }
                System.out.println("max concurrent <= 2: " + (maxInside.get() <= 2));
            }
        }
    ''', out="""
        [cache ready, db ready, queue ready]
        max concurrent <= 2: true
    """)
    yield note("Other concurrent collections: `CopyOnWriteArrayList` (copy on every write — ideal for rarely-changed listener lists), `ConcurrentLinkedQueue` (lock-free queue), `ConcurrentSkipListMap`/`Set` (sorted, concurrent `TreeMap`/`TreeSet`).")
    yield qa("How does ConcurrentHashMap achieve thread safety (Java 8+)?",
             "The table is an array of bins. Inserting into an empty bin uses CAS; otherwise the thread locks only that bin's first node. Reads are lock-free via volatile reads. Long bins turn into red-black trees. Resizing is done cooperatively by several threads. (Java 7 used 16 lock *segments* instead.)")
    yield qa("Why doesn't ConcurrentHashMap allow null?",
             "Ambiguity: `get(k)` returning `null` could mean \"absent\" or \"mapped to null\", and unlike a single-threaded map you can't follow up with `containsKey` atomically — another thread may change the map in between.")
    yield qa("AtomicInteger vs LongAdder?",
             "`AtomicInteger` is one CAS'd variable — exact reads, but many threads hammering it retry a lot. `LongAdder` spreads increments over per-thread cells and sums on `sum()`, scaling far better for write-heavy counters, at the cost of a non-atomic snapshot read.")
    yield qa("CountDownLatch vs CyclicBarrier?",
             "A latch is one-shot: some threads count down, others await; it cannot be reset. A barrier makes a fixed group of threads wait for *each other*, can run a barrier action, and resets automatically for the next round.")


@topic(G, "virtual-threads", "Virtual Threads (Java 21)", "feather")
def _():
    yield lead("Virtual threads (JEP 444, final in Java 21) are lightweight threads managed by the JVM — you can have *millions*, so plain blocking code scales like async code.")
    yield define("Virtual thread", "a `java.lang.Thread` not tied to an OS thread. The JVM *mounts* it on a small pool of **carrier** (platform) threads; when it blocks on I/O, `sleep` or a lock, it *unmounts* and the carrier runs another virtual thread.")
    yield section("Platform vs virtual threads", "columns")
    yield table(
        ["", "Platform thread", "Virtual thread"],
        ["Backed by", "One OS thread for its whole life", "Any carrier thread, only while running"],
        ["Stack", "Fixed, ~1 MB reserved", "Heap-allocated, grows as needed (KBs)"],
        ["How many", "Thousands", "Millions"],
        ["Creation", "Expensive — pool them", "Cheap — create one per task, **never pool**"],
        ["Scheduler", "OS", "JVM (`ForkJoinPool` of carriers, ~one per core)"],
        ["Always daemon?", "Configurable", "Yes; priority fixed"],
        ["Best for", "CPU-bound work, long-lived threads", "High-concurrency blocking I/O (servers, clients)"],
    )
    yield section("Creating virtual threads", "code")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) throws InterruptedException {
                Thread v = Thread.ofVirtual().name("v-worker").start(() ->
                    System.out.println(Thread.currentThread().getName()
                        + " virtual=" + Thread.currentThread().isVirtual()
                        + " daemon=" + Thread.currentThread().isDaemon()));
                v.join();

                Thread quick = Thread.startVirtualThread(() -> System.out.println("started with startVirtualThread"));
                quick.join();

                Thread unstarted = Thread.ofVirtual().unstarted(() -> { });
                System.out.println("state = " + unstarted.getState());

                Thread p = Thread.ofPlatform().name("p-worker").start(() ->
                    System.out.println(Thread.currentThread().getName() + " virtual=" + Thread.currentThread().isVirtual()));
                p.join();
            }
        }
    ''', out="""
        v-worker virtual=true daemon=true
        started with startVirtualThread
        state = NEW
        p-worker virtual=false
    """)
    yield section("One virtual thread per task", "stack-3")
    yield p("10 000 tasks that each block for 10 ms. A pool of 100 platform threads would need ~1 s; with a thread per task the sleeps all overlap and the whole batch finishes in roughly the time of one.")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.concurrent.ExecutorService;
        import java.util.concurrent.Executors;
        import java.util.concurrent.Future;

        public class Main {
            public static void main(String[] args) throws Exception {
                List<Future<Integer>> results = new ArrayList<>();
                try (ExecutorService exec = Executors.newVirtualThreadPerTaskExecutor()) {
                    for (int i = 0; i < 10_000; i++) {
                        int n = i;
                        results.add(exec.submit(() -> {
                            Thread.sleep(10);          // blocking call: the virtual thread unmounts
                            return n;
                        }));
                    }
                }                                      // close() waits for all 10 000
                long sum = 0;
                for (Future<Integer> f : results) sum += f.resultNow();
                System.out.println(results.size() + " tasks, sum = " + sum);
            }
        }
    ''', out="10000 tasks, sum = 49995000")
    yield section("When they help — and when they don't", "scale")
    yield cards(
        ("Great for", "Thread-per-request servers, calling many HTTP/DB services, anything that spends most of its time **waiting**. Write simple blocking code; get async-level throughput.", "circle-check"),
        ("No gain for", "**CPU-bound** work — there are still only as many carriers as cores. Virtual threads increase *throughput* for waiting tasks, not the *speed* of a single task.", "circle-x"),
    )
    yield section("Pitfalls", "alert-triangle")
    yield table(
        ["Pitfall", "Why", "Instead"],
        ["Pooling virtual threads", "They are cheap; pooling just limits concurrency", "One per task; limit access to a scarce resource with a `Semaphore`"],
        ["**Pinning** (Java 21)", "Blocking inside `synchronized` (or a native call) keeps the carrier occupied", "Use `ReentrantLock` around blocking I/O; diagnose with `-Djdk.tracePinnedThreads=full` (fixed for `synchronized` in JDK 24, JEP 491)"],
        ["Heavy `ThreadLocal` caches", "A million threads × a cached object each = memory blow-up", "Pass context explicitly; scoped values (preview)"],
        ["Long CPU loops", "No time-slicing preemption between virtual threads", "Keep CPU-heavy work on a platform pool"],
    )
    yield warn("Virtual threads are always daemon threads: if `main` returns without joining them (or closing their executor), the JVM exits and their work is lost.")
    yield note("**Structured concurrency** (`StructuredTaskScope`, preview in Java 21, needs `--enable-preview`) treats a group of subtasks as one unit: fork them, `join()` the scope, and if one fails the others are cancelled — no leaked threads. **Scoped values** (also preview) are the virtual-thread-friendly replacement for `ThreadLocal`.", "Related previews")
    yield qa("Do virtual threads make code faster?",
             "Not individual tasks — a CPU-bound computation runs at the same speed. They raise *throughput* for I/O-bound workloads by letting you have one cheap thread per concurrent task, so waiting no longer ties up an expensive OS thread.")
    yield qa("What is a carrier thread? What is pinning?",
             "A carrier is the platform thread (from a `ForkJoinPool`) a virtual thread is mounted on while it runs. Pinning happens when a virtual thread blocks but can't unmount — in Java 21, while inside a `synchronized` block or a native method — so the carrier is blocked too, reducing scalability.")
    yield qa("Should you use a thread pool of virtual threads?",
             "No. Pools exist to amortise expensive thread creation and cap resource use; virtual threads are cheap, so create one per task (`newVirtualThreadPerTaskExecutor`). To cap access to a limited resource, use a `Semaphore` instead.")
