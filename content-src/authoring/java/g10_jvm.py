from kit import *

G = "JVM Internals & Memory"


@topic(G, "jvm-memory", "JVM Memory: Heap, Stack & Metaspace", "stack-2")
def _():
    yield lead("The JVM splits memory into areas with different lifetimes: *objects on the heap*, *method calls on per-thread stacks*, *class metadata in metaspace*.")
    yield define("Runtime data areas", "the regions of memory the JVM specification defines. Some are shared by all threads (heap, metaspace), others are private to each thread (stack, PC register).")
    yield section("The runtime data areas", "layout-grid")
    yield table(
        ["Area", "Shared?", "Holds", "Error when full"],
        ["**Heap** — young gen (Eden + 2 Survivor spaces)", "All threads", "Newly created objects and arrays", "`OutOfMemoryError: Java heap space`"],
        ["**Heap** — old (tenured) gen", "All threads", "Objects that survived several young GCs", "`OutOfMemoryError: Java heap space`"],
        ["**JVM stack** (one per thread)", "Per thread", "One *frame* per method call: local variables, operand stack, return address", "`StackOverflowError`"],
        ["**Metaspace** (native memory, Java 8+)", "All threads", "Class metadata: method bytecode, field layout, runtime constant pool", "`OutOfMemoryError: Metaspace`"],
        ["**PC register**", "Per thread", "Address of the bytecode instruction being executed", "—"],
        ["**Native method stack**", "Per thread", "Frames of native (C/C++) methods called through JNI", "`StackOverflowError`"],
        ["**Code cache**", "All threads", "Machine code produced by the JIT compiler", "JIT stops compiling (warning)"],
    )
    yield note("The **string pool** lives on the heap (moved out of PermGen in Java 7). **PermGen** itself was removed in Java 8 and replaced by **metaspace**, which grows in native memory instead of having a fixed size.", "History")
    yield section("What lives where", "map-pin")
    yield cards(
        ("Primitive locals", "`int x = 5;` inside a method — the value sits directly in the stack frame. Gone when the method returns.", "number"),
        ("References", "`Box b` is a local of reference type — the *reference* (a pointer-sized value) is on the stack…", "link"),
        ("Objects", "…and the `new Box()` it points to is on the heap, shared by every reference to it. Instance fields (primitive or not) live inside the object.", "box"),
        ("Static fields", "Belong to the class. Since Java 8 they are stored with the `Class` object on the heap; the class metadata is in metaspace.", "building"),
    )
    yield snippet("java", r'''
        public class Main {
            static class Box { int value; }

            public static void main(String[] args) {
                int a = 10;           // primitive local → in main's stack frame
                int b = a;            // copies the value
                b++;

                Box x = new Box();    // reference x on the stack, Box object on the heap
                Box y = x;            // copies the reference, not the object
                y.value = 42;

                System.out.println(a + " " + b);
                System.out.println(x.value + " " + (x == y));
            }
        }
    ''', out="""
        10 11
        42 true
    """)
    yield section("Stack frames and StackOverflowError", "stack")
    yield steps(
        ("Call", "Calling a method pushes a new frame onto the current thread's stack."),
        ("Execute", "The frame holds the method's parameters and locals, plus an operand stack the bytecode works on."),
        ("Return", "The frame is popped — its locals disappear instantly. No GC is needed for stack memory."),
    )
    yield snippet("java", r'''
        public class Main {
            static int depth = 0;

            static void recurse() {
                depth++;
                recurse();              // no base case → a new frame on every call
            }

            public static void main(String[] args) {
                try {
                    recurse();
                } catch (StackOverflowError e) {
                    System.out.println("StackOverflowError after more than 1000 frames: " + (depth > 1000));
                }
            }
        }
    ''', out="StackOverflowError after more than 1000 frames: true")
    yield section("OutOfMemoryError", "alert-octagon")
    yield p("Run with a deliberately tiny heap (`-Xmx64m`) and ask for a 400 MB array:")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                try {
                    int[] huge = new int[100_000_000];      // ~400 MB
                    System.out.println(huge.length);
                } catch (OutOfMemoryError e) {
                    System.out.println("OutOfMemoryError: " + e.getMessage());
                }
            }
        }
    ''', out="OutOfMemoryError: Java heap space", flags=("-Xmx64m",))
    yield table(
        ["", "`StackOverflowError`", "`OutOfMemoryError`"],
        ["Area", "A thread's stack", "Heap, metaspace, direct buffers, native threads…"],
        ["Typical cause", "Unbounded / too deep recursion", "Leak (objects stay reachable), or heap simply too small"],
        ["Fix", "Base case, iteration, or bigger `-Xss`", "Fix the leak (heap dump), then size `-Xmx`"],
        ["Type", "Both extend `Error` (via `VirtualMachineError`) — not meant to be caught in normal code", ""],
    )
    yield section("Sizing flags", "adjustments")
    yield table(
        ["Flag", "Meaning", "Example"],
        ["`-Xms`", "Initial heap size", "`-Xms512m`"],
        ["`-Xmx`", "Maximum heap size (default: 1/4 of physical RAM)", "`-Xmx2g`"],
        ["`-Xss`", "Stack size per thread", "`-Xss1m`"],
        ["`-XX:MaxMetaspaceSize`", "Cap metaspace (unbounded by default)", "`-XX:MaxMetaspaceSize=256m`"],
        ["`-XX:+HeapDumpOnOutOfMemoryError`", "Write a `.hprof` heap dump when OOM happens", "with `-XX:HeapDumpPath=/tmp`"],
    )
    yield shell('''
        $ java -Xms256m -Xmx1g -Xss512k -XX:+HeapDumpOnOutOfMemoryError App.java
        $ java -XX:+PrintFlagsFinal -version | grep -E "MaxHeapSize|ThreadStackSize"
    ''')
    yield section("Escape analysis", "run")
    yield p("The JIT checks whether an object *escapes* the method that creates it (returned, stored in a field, passed to another thread). If it doesn't, the JIT may **scalar-replace** it — keep its fields in registers/stack slots and never allocate it on the heap at all.")
    yield snippet("java", r'''
        public class Main {
            record Point(int x, int y) {}

            static int distanceSquared(int x, int y) {
                Point p = new Point(x, y);      // never escapes → candidate for scalar replacement
                return p.x() * p.x() + p.y() * p.y();
            }

            public static void main(String[] args) {
                long sum = 0;
                for (int i = 0; i < 1_000; i++) sum += distanceSquared(i, i);
                System.out.println(sum);
            }
        }
    ''', out="665667000")
    yield note("\"All objects live on the heap\" is the *language model*. Escape analysis is an invisible optimisation — your program behaves exactly the same either way.")
    yield qa("Where are local variables, objects and static variables stored?",
             "Local primitives and local references are in the thread's stack frame. Objects (including their instance fields) are on the heap. Static fields are stored with the class's `Class` object on the heap (Java 8+); the class metadata itself is in metaspace.")
    yield qa("What replaced PermGen and why?",
             "Metaspace (Java 8). PermGen had a fixed maximum size and caused `OutOfMemoryError: PermGen space` in apps that load many classes (app servers, dynamic proxies). Metaspace lives in native memory and grows on demand; cap it with `-XX:MaxMetaspaceSize`.")
    yield qa("Is the stack or the heap thread-safe?",
             "Each thread has its own stack, so locals are never shared — they are inherently thread-confined. The heap is shared by all threads, so objects reachable from more than one thread need synchronization.")


@topic(G, "garbage-collection", "Garbage Collection", "recycle")
def _():
    yield lead("The garbage collector frees heap objects that are no longer *reachable* — you never call `free`, but you still decide what stays reachable.")
    yield define("Garbage", "an object that cannot be reached by following references from any **GC root**. Reference counting is *not* used, so cycles of objects pointing at each other are still collected.")
    yield section("GC roots and reachability", "sitemap")
    yield ul(
        "Local variables and parameters in every live thread's stack frames.",
        "Static fields of loaded classes.",
        "Active threads themselves.",
        "JNI references held by native code, and objects used as monitors (`synchronized`).",
    )
    yield snippet("java", r'''
        public class Main {
            static class Node { Node next; }

            public static void main(String[] args) {
                Node a = new Node();
                Node b = new Node();
                a.next = b;
                b.next = a;          // a cycle: a → b → a

                a = null;
                b = null;            // no root reaches the cycle any more → both are garbage
                System.out.println("the cycle is unreachable and will be collected");
            }
        }
    ''', out="the cycle is unreachable and will be collected")
    yield section("Generational collection", "stairs")
    yield p("**Weak generational hypothesis**: most objects die young (temporary strings, iterators, DTOs). So the heap is split and the young part is collected often and cheaply.")
    yield steps(
        ("Allocate in Eden", "`new` bumps a pointer in a thread-local allocation buffer — allocation is extremely cheap."),
        ("Minor GC", "When Eden fills, live objects are copied to a Survivor space; everything left in Eden is reclaimed at once."),
        ("Age and promote", "Each survived minor GC increments an object's age; past a threshold it is *promoted* to the old generation."),
        ("Major / full GC", "When the old generation fills, it is collected too — more expensive, historically the source of long pauses."),
    )
    yield table(
        ["Phase / term", "Meaning"],
        ["**Mark**", "Trace from the roots and mark every reachable object."],
        ["**Sweep**", "Reclaim the memory of unmarked objects."],
        ["**Compact**", "Slide live objects together to remove fragmentation."],
        ["**Copying**", "Copy live objects to an empty space (used for the young gen: cost ∝ live objects, not heap size)."],
        ["**Stop-the-world (STW)**", "All application threads are paused while the GC works."],
        ["**Concurrent**", "GC work done while application threads keep running."],
    )
    yield section("The collectors", "list-details")
    yield table(
        ["Collector", "Flag", "Best for", "Notes"],
        ["Serial", "`-XX:+UseSerialGC`", "Tiny heaps, single-core containers", "One thread, stop-the-world"],
        ["Parallel", "`-XX:+UseParallelGC`", "Batch jobs — maximum throughput", "Many threads, still STW"],
        ["**G1** (default since 9)", "`-XX:+UseG1GC`", "General purpose, heaps of GBs", "Region-based; targets a pause goal (`-XX:MaxGCPauseMillis=200`)"],
        ["ZGC", "`-XX:+UseZGC` (generational in 21: `-XX:+ZGenerational`)", "Huge heaps, low latency", "Pauses under a millisecond, mostly concurrent"],
        ["Shenandoah", "`-XX:+UseShenandoahGC`", "Low latency", "Concurrent compaction (OpenJDK builds)"],
        ["CMS", "—", "—", "Deprecated in 9, **removed in 14**"],
    )
    yield shell('''
        $ java -XX:+UseZGC -Xmx4g -Xlog:gc App.java      # choose a collector, log each GC
        $ java -Xlog:gc*:file=gc.log App.java            # detailed GC log to a file
        $ jcmd <pid> GC.heap_info                        # inspect a running JVM
    ''')
    yield section("System.gc(), finalize() and cleanup", "trash")
    yield warn("`System.gc()` is only a **hint** — the JVM may ignore it (`-XX:+DisableExplicitGC`), and when honoured it usually triggers an expensive full GC. Never call it to “free memory”.")
    yield warn("`finalize()` is **deprecated for removal** (Java 9/18): it runs at an unpredictable time or never, slows GC, and can resurrect objects. Release resources with `try-with-resources`; for a safety net use `java.lang.ref.Cleaner`.", "finalize()")
    yield snippet("java", r'''
        import java.lang.ref.Cleaner;

        public class Main {
            static final Cleaner CLEANER = Cleaner.create();

            static class Resource implements AutoCloseable {
                private final Cleaner.Cleanable cleanable;

                Resource(String name) {
                    // the cleanup action must NOT capture `this`, or the object never becomes unreachable
                    cleanable = CLEANER.register(this, () -> System.out.println("released " + name));
                }

                @Override
                public void close() { cleanable.clean(); }   // runs the action at most once
            }

            public static void main(String[] args) {
                try (Resource r = new Resource("db-connection")) {
                    System.out.println("using the resource");
                }
                System.out.println("after try");
            }
        }
    ''', out="""
        using the resource
        released db-connection
        after try
    """)
    yield section("Tuning in practice", "adjustments")
    yield ol(
        "Measure first: GC logs (`-Xlog:gc`), JDK Flight Recorder (`-XX:StartFlightRecording`), `jstat -gc <pid>`.",
        "Size the heap: set `-Xms` = `-Xmx` for servers to avoid resizing.",
        "Pick the collector by goal: throughput → Parallel, balanced → G1, latency → ZGC.",
        "Reduce garbage: reuse builders, avoid needless boxing, stream large files instead of loading them.",
    )
    yield qa("Can an object be garbage collected while it still references other objects?",
             "Yes. Reachability is about incoming references *from roots*. An object that points to others — even a whole cycle — is garbage as soon as no root can reach it.")
    yield qa("What is a stop-the-world pause and how do modern collectors reduce it?",
             "A pause during which all application threads are stopped so the GC can work on a consistent heap. G1 limits pause length by collecting a subset of regions per cycle; ZGC and Shenandoah do marking *and* compaction concurrently, keeping pauses below ~1 ms regardless of heap size.")
    yield qa("Minor GC vs major GC?",
             "A minor GC collects only the young generation — frequent and fast because most young objects are dead. A major (old-gen) or full GC collects the old generation or the whole heap — rarer and much more expensive.")
    yield qa("Does calling System.gc() guarantee collection?",
             "No. It is a request the JVM may ignore. Code that depends on it for correctness is broken.")


@topic(G, "references-memory-leaks", "References & Memory Leaks", "link-off")
def _():
    yield lead("Java has garbage collection, not leak immunity: anything you keep *reachable by accident* is a leak.")
    yield define("Memory leak (Java)", "objects that are no longer needed but are still reachable from a GC root, so the collector can never reclaim them. The heap slowly fills until `OutOfMemoryError`.")
    yield section("Four reference strengths", "link")
    yield table(
        ["Type", "Collected when…", "`get()` after collection", "Typical use"],
        ["**Strong** (`Obj o = …`)", "Never, while reachable", "—", "Normal code"],
        ["**Soft** — `SoftReference`", "Only when memory is low (before OOM)", "`null`", "Memory-sensitive caches"],
        ["**Weak** — `WeakReference`", "At the next GC once only weakly reachable", "`null`", "`WeakHashMap`, canonicalising maps, listener registries"],
        ["**Phantom** — `PhantomReference`", "After finalisation; enqueued for cleanup", "always `null`", "Post-mortem cleanup (`Cleaner` is built on it)"],
    )
    yield snippet("java", r'''
        import java.lang.ref.WeakReference;

        public class Main {
            public static void main(String[] args) {
                StringBuilder data = new StringBuilder("payload");
                WeakReference<StringBuilder> weak = new WeakReference<>(data);

                System.out.println(weak.get());          // still strongly reachable via `data`
                data = null;                             // drop the only strong reference
                System.gc();                             // a hint — usually honoured in practice
                System.out.println(weak.get());
            }
        }
    ''', out=None)
    yield output('''
        payload
        null
    ''', "Typical output")
    yield note("Weak/soft clearing depends on when the GC actually runs, so never write logic that *needs* a reference to be cleared at a particular moment.")
    yield section("WeakHashMap", "map")
    yield p("Keys are held weakly: when a key has no strong references elsewhere, its entry disappears on a later GC. Useful for attaching metadata to objects you don't own.")
    yield warn("A `WeakHashMap` with `String` literal keys or boxed small integers never clears — those keys are strongly held by the string pool / `Integer` cache. And a value that refers back to its own key keeps the key alive.")
    yield section("The usual leak suspects", "bug")
    yield table(
        ["Leak", "Why it's reachable", "Fix"],
        ["Static collection used as a cache", "Static fields are GC roots — the map lives as long as the class", "Bounded cache (LRU via `LinkedHashMap.removeEldestEntry`, Caffeine), or eviction"],
        ["Listeners / callbacks never removed", "The subject's listener list points at every subscriber", "Unregister in a `close()`; or weak listeners"],
        ["Non-static inner class / lambda captures", "An inner instance holds `Outer.this`; lambdas hold captured variables", "Use `static` nested classes; capture only what you need"],
        ["`ThreadLocal` in thread pools", "Pool threads never die, so their thread-local values never go away", "`try { … } finally { tl.remove(); }`"],
        ["Unclosed resources", "Streams, connections, native buffers hold memory and file handles", "`try-with-resources`"],
        ["Wrong `equals`/`hashCode` as map key", "Duplicate keys pile up; mutated keys become unreachable-yet-present", "Immutable keys with a correct contract"],
    )
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static final List<Runnable> LISTENERS = new ArrayList<>();   // static → a GC root

            public static void main(String[] args) {
                for (int i = 0; i < 1_000; i++) {
                    byte[] buffer = new byte[10_000];
                    LISTENERS.add(() -> System.out.print(buffer.length));   // lambda captures buffer
                }
                // ~10 MB can never be freed: every buffer is reachable through LISTENERS
                System.out.println("listeners: " + LISTENERS.size());

                LISTENERS.clear();                 // unsubscribe → buffers become garbage
                System.out.println("listeners: " + LISTENERS.size());
            }
        }
    ''', out="""
        listeners: 1000
        listeners: 0
    """)
    yield snippet("java", r'''
        public class Main {
            private static final ThreadLocal<StringBuilder> BUFFER =
                    ThreadLocal.withInitial(StringBuilder::new);

            static String handle(String request) {
                try {
                    StringBuilder sb = BUFFER.get();
                    sb.setLength(0);
                    return sb.append("handled ").append(request).toString();
                } finally {
                    BUFFER.remove();          // pooled threads live forever — always clean up
                }
            }

            public static void main(String[] args) {
                System.out.println(handle("GET /"));
            }
        }
    ''', out="handled GET /")
    yield section("Finding a leak", "search")
    yield steps(
        ("Confirm", "Heap usage after each full GC keeps climbing (GC logs, JFR, VisualVM / JConsole graphs)."),
        ("Dump the heap", "`jcmd <pid> GC.heap_dump heap.hprof` (or `jmap -dump:live,format=b,file=heap.hprof <pid>`, or `-XX:+HeapDumpOnOutOfMemoryError`)."),
        ("Analyse", "Open it in Eclipse MAT or VisualVM: look at the dominator tree and the *path to GC roots* of the biggest retained sets."),
        ("Fix & verify", "Remove the unintended reference, then re-run and compare dumps."),
    )
    yield shell('''
        $ jcmd                                   # list running JVMs
        $ jcmd <pid> GC.class_histogram | head   # which classes use the most memory
        $ jcmd <pid> GC.heap_dump /tmp/heap.hprof
        $ jstat -gcutil <pid> 1000               # GC utilisation every second
    ''')
    yield qa("How can a garbage-collected language leak memory?",
             "The GC only frees *unreachable* objects. If a static map, a listener list, a thread-local in a pooled thread or a long-lived object keeps a reference to data you no longer need, that data is reachable and stays forever.")
    yield qa("SoftReference vs WeakReference?",
             "A weakly reachable object is cleared at the next GC. A softly reachable object is kept until the JVM is short of memory, which makes soft references suitable for simple memory-sensitive caches (though a proper bounded cache is usually better).")
    yield qa("Why can a non-static inner class cause a leak?",
             "Every instance of a non-static inner class holds a hidden reference to its enclosing instance (`Outer.this`). If the inner object outlives the outer one (e.g. registered as a callback), the whole outer object is retained. Make it a `static` nested class.")


@topic(G, "string-memory-traps", "String & Memory Interview Traps", "alert-triangle")
def _():
    yield lead("A collection of classic “what does this print?” questions about strings, the pool, boxing and constant folding — each verified.")
    yield section("== on strings", "equal")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String a = "java";
                String b = "java";                 // same pooled literal
                String c = new String("java");     // a new heap object
                String d = "ja" + "va";            // compile-time constant → folded to "java"
                String part = "ja";
                String e = part + "va";            // runtime concatenation → new object
                final String fpart = "ja";
                String f = fpart + "va";           // final + literal is a constant → folded

                System.out.println(a == b);
                System.out.println(a == c);
                System.out.println(a == d);
                System.out.println(a == e);
                System.out.println(a == f);
                System.out.println(a == e.intern());
                System.out.println(a.equals(c));
            }
        }
    ''', out="""
        true
        false
        true
        false
        true
        true
        true
    """)
    yield table(
        ["Expression", "Pooled?", "Why"],
        ["`\"java\"`", "Yes", "Every string literal is interned in the pool"],
        ["`new String(\"java\")`", "No", "`new` always creates a fresh heap object"],
        ["`\"ja\" + \"va\"`", "Yes", "Constant expression, folded by `javac`"],
        ["`part + \"va\"` (non-final `part`)", "No", "Computed at run time (`StringConcatFactory` / `StringBuilder`)"],
        ["`fpart + \"va\"` (`final` with constant initialiser)", "Yes", "`fpart` is a *constant variable*, so the whole expression is constant"],
        ["`s.intern()`", "Yes", "Returns the pooled instance, adding it if absent"],
    )
    yield note("Rule: compare strings with `equals` (or `Objects.equals` for null-safety). `==` only tells you whether two references point at the same object.")
    yield qa("How many objects does new String(\"hello\") create?",
             "Up to two: the literal `\"hello\"` is placed in the string pool when the class is loaded (if it isn't already there), and `new` creates one more `String` object on the heap. If the literal was already pooled, only one new object is created at run time.")
    yield section("Integer cache and boxing", "box")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Integer a = 127, b = 127;
                Integer c = 128, d = 128;
                System.out.println(a == b);          // cached: -128..127
                System.out.println(c == d);          // two different objects
                System.out.println(c.equals(d));

                Long big = 127L;
                System.out.println(big.equals(127));  // Integer vs Long → false
                System.out.println(big == 127);       // unboxed numeric comparison → true

                Integer missing = null;
                try {
                    int n = missing;                  // auto-unboxing null
                    System.out.println(n);
                } catch (NullPointerException ex) {
                    System.out.println("NPE on unboxing");
                }

                boolean flag = true;
                try {
                    int r = flag ? missing : 0;       // ternary unboxes `missing`
                    System.out.println(r);
                } catch (NullPointerException ex) {
                    System.out.println("NPE in ternary");
                }
            }
        }
    ''', out="""
        true
        false
        true
        false
        true
        NPE on unboxing
        NPE in ternary
    """)
    yield warn("The cache covers `Integer`, `Short`, `Long`, `Byte` in −128…127, `Character` up to 127 and both `Boolean` values. The upper bound for `Integer` can be raised with `-XX:AutoBoxCacheMax`, so `==` on boxed numbers is never reliable.")
    yield section("Concatenation and char arithmetic", "plus")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println("a" + 1 + 2);      // left to right: ("a" + 1) + 2
                System.out.println(1 + 2 + "a");      // (1 + 2) + "a"
                System.out.println('a' + 'b');        // char + char → int
                System.out.println("" + 'a' + 'b');
                System.out.println((char) ('a' + 1));
                System.out.println(Math.abs(Integer.MIN_VALUE));   // overflow: no positive counterpart
                System.out.println(0.1 + 0.2);
            }
        }
    ''', out="""
        a12
        3a
        195
        ab
        b
        -2147483648
        0.30000000000000004
    """)
    yield section("String + in a loop", "repeat")
    yield p("Each `s += x` creates a brand-new string and copies everything so far — O(n²) for n appends. Inside loops use a `StringBuilder` (single-expression concatenations are fine: the compiler optimises them).")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 5; i++) {
                    sb.append(i).append(',');
                }
                sb.setLength(sb.length() - 1);            // drop the trailing comma
                System.out.println(sb);

                System.out.println(String.join(",", "a", "b", "c"));   // often simplest
            }
        }
    ''', out="""
        0,1,2,3,4
        a,b,c
    """)
    yield section("Other traps", "list-check")
    yield cards(
        ("`substring` copies", "Before Java 7u6, `substring` shared the parent's `char[]` — a tiny substring could pin a huge string in memory. Now it copies, so no leak (but O(k) cost).", "scissors"),
        ("Passwords in `char[]`", "A `String` is immutable and may be pooled; it lingers in memory until GC and can show up in heap dumps. A `char[]` can be wiped with `Arrays.fill(pw, '\\0')` right after use — that's why `Console.readPassword()` returns `char[]`.", "lock"),
        ("Compact strings (9+)", "Strings that contain only Latin-1 characters store one byte per char instead of two (`byte[]` + a coder flag).", "file-zip"),
        ("Strings are immutable", "`s.toUpperCase()` returns a new string; calling it without assigning the result does nothing.", "lock-square"),
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String s = "hello";
                s.toUpperCase();                   // result discarded
                System.out.println(s);
                s = s.toUpperCase();
                System.out.println(s);
            }
        }
    ''', out="""
        hello
        HELLO
    """)
    yield section("switch on strings and null", "switch")
    yield p("A `switch` on a `String` compiles to a switch on `hashCode()` followed by `equals()`. A `null` selector throws `NullPointerException` — unless (Java 21) you add `case null`.")
    yield snippet("java", r'''
        public class Main {
            static String classic(String cmd) {
                switch (cmd) {
                    case "start": return "starting";
                    case "stop":  return "stopping";
                    default:      return "unknown";
                }
            }

            static String modern(String cmd) {
                return switch (cmd) {
                    case null -> "no command";            // Java 21
                    case "start" -> "starting";
                    default -> "unknown";
                };
            }

            public static void main(String[] args) {
                System.out.println(classic("stop"));
                try {
                    classic(null);
                } catch (NullPointerException e) {
                    System.out.println("NPE from classic switch");
                }
                System.out.println(modern(null));
            }
        }
    ''', out="""
        stopping
        NPE from classic switch
        no command
    """)
    yield qa("Why is String immutable in Java?",
             "(1) The string pool is only safe if pooled strings can't change. (2) Security: class names, file paths and URLs passed to APIs can't be altered after a check. (3) Thread safety for free. (4) The hash code can be cached, which makes strings fast `HashMap` keys.")
    yield qa("What does intern() do, and should you use it?",
             "It returns the canonical pooled copy of the string, adding it to the pool if needed, so equal interned strings are `==`. It can save memory for many duplicate strings, but the pool lookup has a cost — modern G1 also offers `-XX:+UseStringDeduplication`, which deduplicates backing arrays automatically.")
