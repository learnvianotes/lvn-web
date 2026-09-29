from kit import *

G = "Exceptions & Generics"


@topic(G, "exceptions", "Exceptions: Checked vs Unchecked", "alert-triangle")
def _():
    yield lead("An exception is an object that signals something went wrong. Java splits them into **checked** exceptions the compiler forces you to handle, and **unchecked** ones it doesn't.")
    yield define("Exception", "an instance of `Throwable` that is *thrown* to abort normal flow. The runtime unwinds the call stack until a matching `catch` is found; if none is, the thread dies and the stack trace is printed.")
    yield section("The hierarchy", "sitemap")
    yield flow("`Throwable`", "`Error` | `Exception`", "`RuntimeException` (under `Exception`)")
    yield table(
        ["Type", "Checked?", "Meaning", "Examples"],
        ["`Error`", "Unchecked", "Serious JVM/environment problems — don't catch", "`OutOfMemoryError`, `StackOverflowError`, `NoClassDefFoundError`"],
        ["`Exception` (not Runtime)", "**Checked**", "Recoverable, expected conditions outside your control", "`IOException`, `FileNotFoundException`, `SQLException`, `InterruptedException`"],
        ["`RuntimeException`", "Unchecked", "Programming bugs / violated preconditions", "`NullPointerException`, `IllegalArgumentException`, `IndexOutOfBoundsException`, `ClassCastException`, `ArithmeticException`"],
    )
    yield note("**Checked** = `Exception` and its subclasses *except* `RuntimeException` subclasses. The compiler requires them to be caught or declared with `throws`. Everything else (`RuntimeException`, `Error`) is unchecked.")
    yield section("throw vs throws", "arrow-bar-up")
    yield table(
        ["", "`throw`", "`throws`"],
        ["What", "A statement that throws one exception object", "Part of a method signature listing exceptions it may throw"],
        ["Where", "Method body: `throw new IllegalStateException(\"closed\");`", "Declaration: `void read() throws IOException`"],
        ["Needed for", "Any exception", "**Checked** exceptions (optional for unchecked)"],
    )
    yield snippet("java", r'''
        import java.io.IOException;

        public class Main {
            static int parseAge(String s) {                        // unchecked: no throws needed
                int age = Integer.parseInt(s);                     // may throw NumberFormatException
                if (age < 0) throw new IllegalArgumentException("negative age: " + age);
                return age;
            }

            static String load(String name) throws IOException {  // checked: must be declared
                if (name.isEmpty()) throw new IOException("no file name");
                return "data of " + name;
            }

            public static void main(String[] args) {
                for (String s : new String[] {"42", "-1", "abc"}) {
                    try {
                        System.out.println(parseAge(s));
                    } catch (IllegalArgumentException e) {         // NumberFormatException is a subclass
                        System.out.println(e.getClass().getSimpleName() + ": " + e.getMessage());
                    }
                }
                try {
                    System.out.println(load("a.txt"));
                    System.out.println(load(""));
                } catch (IOException e) {
                    System.out.println("IO problem: " + e.getMessage());
                }
            }
        }
    ''', out="""
        42
        IllegalArgumentException: negative age: -1
        NumberFormatException: For input string: "abc"
        data of a.txt
        IO problem: no file name
    """)
    yield section("Handle or declare", "gavel")
    yield p("Calling a method that throws a checked exception without catching or declaring it doesn't compile:")
    yield snippet("java", r'''
        import java.nio.file.*;

        public class Main {
            public static void main(String[] args) {
                String text = Files.readString(Path.of("notes.txt"));
                System.out.println(text);
            }
        }
    ''', fails=True)
    yield output("""
        Main.java:5: error: unreported exception IOException; must be caught or declared to be thrown
                String text = Files.readString(Path.of("notes.txt"));
                                              ^
    """, "Compiler error")
    yield section("Stack unwinding", "stack-2")
    yield snippet("java", r'''
        public class Main {
            static void c() { System.out.println("c throws"); throw new IllegalStateException("boom"); }
            static void b() { System.out.println("b calls c"); c(); System.out.println("b after c"); }  // never printed
            static void a() {
                try {
                    b();
                } catch (IllegalStateException e) {
                    System.out.println("a caught " + e.getMessage());
                    StackTraceElement top = e.getStackTrace()[0];
                    System.out.println("thrown in " + top.getMethodName() + "()");
                }
            }

            public static void main(String[] args) {
                a();
                System.out.println("program continues");
            }
        }
    ''', out="""
        b calls c
        c throws
        a caught boom
        thrown in c()
        program continues
    """)
    yield p("The exception travels up from `c` through `b` (whose remaining code is skipped) until `a`'s `catch` matches. An uncaught exception in `main` terminates the thread and prints `Exception in thread \"main\" …` with the stack trace to **stderr**.")
    yield section("Common exceptions to recognise", "list")
    yield table(
        ["Exception", "Typical cause"],
        ["`NullPointerException`", "Calling a method / accessing a field on `null` (Java 14+ says *which* reference was null)"],
        ["`ArrayIndexOutOfBoundsException`", "`arr[arr.length]`, negative index"],
        ["`ArithmeticException`", "Integer division by zero (`5 / 0`); `5.0 / 0` is `Infinity`, no exception"],
        ["`ClassCastException`", "`(String) someInteger` at runtime"],
        ["`NumberFormatException`", "`Integer.parseInt(\"12a\")`"],
        ["`ConcurrentModificationException`", "Modifying a collection while iterating it with for-each"],
        ["`UnsupportedOperationException`", "Adding to `List.of(…)` or `Arrays.asList(…)`"],
        ["`IllegalStateException`", "Method called at the wrong time (iterator `remove` twice, closed resource)"],
        ["`StackOverflowError`", "Infinite / too-deep recursion"],
        ["`OutOfMemoryError`", "Heap (or metaspace) exhausted"],
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Runnable[] bugs = {
                    () -> System.out.println(10 / Integer.parseInt("0")),
                    () -> java.util.List.of(1).add(2),
                    () -> { Object o = "text"; Integer i = (Integer) o; System.out.println(i); },
                    () -> { String s = null; System.out.println(s.length()); },
                };
                for (Runnable bug : bugs) {
                    try {
                        bug.run();
                    } catch (RuntimeException e) {
                        System.out.println(e.getClass().getSimpleName());
                    }
                }
                try {
                    int[] a = new int[3];
                    a[3] = 1;
                } catch (ArrayIndexOutOfBoundsException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out="""
        ArithmeticException
        UnsupportedOperationException
        ClassCastException
        NullPointerException
        Index 3 out of bounds for length 3
    """)
    yield warn("Never catch `Throwable` or `Error` just to keep going — an `OutOfMemoryError` or `StackOverflowError` leaves the JVM in a doubtful state. Catch the most specific exception you can actually handle.")
    yield qa("Checked vs unchecked exceptions?",
             "Checked exceptions (`Exception` subclasses other than `RuntimeException`) must be caught or declared with `throws` — they model recoverable conditions like I/O failures. Unchecked (`RuntimeException`, `Error`) need not be declared — they usually indicate bugs (null, bad index, bad argument) or JVM failures.")
    yield qa("Error vs Exception?",
             "`Error` signals serious problems the application generally can't recover from (`OutOfMemoryError`, `StackOverflowError`). `Exception` signals conditions a program might reasonably catch and handle.")
    yield qa("Is NullPointerException checked?",
             "No — it extends `RuntimeException`. The compiler can't force you to handle it; prevent it with null checks, `Objects.requireNonNull`, `Optional` return types and not returning `null` from methods.")


@topic(G, "try-catch-finally", "try/catch/finally & try-with-resources", "shield")
def _():
    yield lead("`try` marks code that may fail, `catch` handles specific exceptions, `finally` always runs — and try-with-resources closes resources automatically, in reverse order, without losing exceptions.")
    yield section("Anatomy", "code")
    yield snippet("java", r'''
        public class Main {
            static void run(String input) {
                try {
                    System.out.println("parsing " + input);
                    int n = Integer.parseInt(input);
                    System.out.println("100 / n = " + 100 / n);
                } catch (NumberFormatException | ArithmeticException e) {   // multi-catch
                    System.out.println("bad input: " + e.getClass().getSimpleName());
                } finally {
                    System.out.println("finally");                          // always
                }
            }

            public static void main(String[] args) {
                run("4");
                run("0");
                run("x");
            }
        }
    ''', out="""
        parsing 4
        100 / n = 25
        finally
        parsing 0
        bad input: ArithmeticException
        finally
        parsing x
        bad input: NumberFormatException
        finally
    """)
    yield ul(
        "Catch blocks are tried **top to bottom**; the first matching type wins.",
        "A subclass catch must come **before** its superclass — `catch (Exception e)` then `catch (IOException e)` doesn't compile (unreachable).",
        "In a multi-catch `A | B`, the types can't be related by inheritance and `e` is implicitly `final`.",
        "`try` needs at least one `catch` or a `finally` (or resources).",
    )
    yield section("finally always runs — even after return", "clock")
    yield snippet("java", r'''
        public class Main {
            static int value() {
                try {
                    return 1;
                } finally {
                    System.out.println("finally runs before the method returns");
                }
            }

            @SuppressWarnings("finally")
            static int overridden() {
                try {
                    throw new RuntimeException("lost!");
                } finally {
                    return 2;              // discards the exception AND any earlier return
                }
            }

            static int snapshot() {
                int x = 10;
                try {
                    return x;              // return value (10) is saved here
                } finally {
                    x = 99;                // changing x doesn't affect it
                }
            }

            public static void main(String[] args) {
                System.out.println(value());
                System.out.println(overridden());
                System.out.println(snapshot());
            }
        }
    ''', out="""
        finally runs before the method returns
        1
        2
        10
    """)
    yield warn("Never `return` (or `throw`) from a `finally` block: it silently replaces the method's result and **swallows** any exception in flight. The only ways `finally` doesn't run are `System.exit()`, the JVM crashing, or the thread being killed.", "Trap")
    yield section("try-with-resources", "recycle")
    yield p("Any object implementing `AutoCloseable` (or `Closeable`) declared in the `try (…)` header is closed automatically when the block ends — normally or by exception. Resources close in **reverse** order of declaration.")
    yield snippet("java", r'''
        public class Main {
            record Res(String name) implements AutoCloseable {
                Res { System.out.println("open " + name); }
                @Override public void close() { System.out.println("close " + name); }
            }

            public static void main(String[] args) {
                try (Res db = new Res("db"); Res file = new Res("file")) {
                    System.out.println("working with " + db.name() + " and " + file.name());
                    throw new IllegalStateException("failure");
                } catch (IllegalStateException e) {
                    System.out.println("caught " + e.getMessage() + " (resources already closed)");
                } finally {
                    System.out.println("finally");
                }
            }
        }
    ''', out="""
        open db
        open file
        working with db and file
        close file
        close db
        caught failure (resources already closed)
        finally
    """)
    yield section("Suppressed exceptions", "stack-pop")
    yield p("If the body throws *and* `close()` throws, the body's exception is the one propagated; the close exception is attached to it as **suppressed** instead of replacing it (which is what a hand-written `finally { close(); }` would do).")
    yield snippet("java", r'''
        public class Main {
            static class Conn implements AutoCloseable {
                @Override public void close() { throw new IllegalStateException("close failed"); }
            }

            public static void main(String[] args) {
                try (Conn c = new Conn()) {
                    throw new RuntimeException("query failed");
                } catch (RuntimeException e) {
                    System.out.println("primary: " + e.getMessage());
                    for (Throwable s : e.getSuppressed())
                        System.out.println("suppressed: " + s.getMessage());
                }
            }
        }
    ''', out="""
        primary: query failed
        suppressed: close failed
    """)
    yield section("Before and after", "arrows-diff")
    yield dodont(
        "`try (var in = Files.newBufferedReader(path)) { … }` — closed on every path, exceptions preserved. Java 9+ also accepts an existing effectively-final variable: `try (in) { … }`.",
        "Manual `finally { if (in != null) in.close(); }` — verbose, `close()` needs its own try/catch, and an exception from `close()` hides the real one.",
    )
    yield qa("Does finally run if there's a return in try?",
             "Yes. The return value is computed and saved, `finally` runs, then the method returns. If `finally` itself returns, that value wins and any pending exception is discarded — so never return from `finally`.")
    yield qa("When does finally NOT execute?",
             "When the JVM stops: `System.exit()`, a crash / `kill -9`, or power loss. (Also if the `try` never completes, e.g. an infinite loop, or a daemon thread killed at JVM exit.)")
    yield qa("What are suppressed exceptions?",
             "In try-with-resources, if the body throws and then `close()` also throws, the close exception is added to the primary one via `addSuppressed` and can be read with `getSuppressed()`, so no failure is lost.")
    yield qa("In what order are resources closed?",
             "Reverse order of declaration — the last opened is closed first, like a stack — and before any `catch` or `finally` block of that statement runs.")


@topic(G, "custom-exceptions", "Custom Exceptions & Best Practices", "bug")
def _():
    yield lead("Define your own exception types when callers need to react to a specific failure — and always keep the original cause attached.")
    yield section("Defining one", "code")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Account acc = new Account(100);
                try {
                    acc.withdraw(30);
                    acc.withdraw(500);
                } catch (InsufficientFundsException e) {
                    System.out.println(e.getMessage());
                    System.out.println("short by " + e.shortfall());
                }
            }
        }

        // Checked: the caller can reasonably recover (show a message, offer a smaller amount)
        class InsufficientFundsException extends Exception {
            private final long shortfall;
            InsufficientFundsException(long balance, long requested) {
                super("balance " + balance + " < requested " + requested);
                this.shortfall = requested - balance;
            }
            long shortfall() { return shortfall; }
        }

        class Account {
            private long balance;
            Account(long balance) { this.balance = balance; }
            void withdraw(long amount) throws InsufficientFundsException {
                if (amount <= 0) throw new IllegalArgumentException("amount must be positive");  // bug → unchecked
                if (amount > balance) throw new InsufficientFundsException(balance, amount);
                balance -= amount;
            }
        }
    ''', out="""
        balance 70 < requested 500
        short by 430
    """)
    yield section("Checked or unchecked?", "arrows-split")
    yield table(
        ["Choose", "When", "Extend"],
        ["**Checked**", "The caller can and should recover: file missing, payment declined, validation of external input", "`Exception`"],
        ["**Unchecked**", "Programming errors / violated preconditions, or failures nobody nearby can handle", "`RuntimeException`"],
    )
    yield p("Modern code (Spring, most libraries, lambdas and streams) leans unchecked: checked exceptions don't compose with functional interfaces like `Function`, and they leak implementation details up the call chain.")
    yield section("Exception chaining: keep the cause", "link")
    yield snippet("java", r'''
        public class Main {
            static class ConfigException extends RuntimeException {
                ConfigException(String msg, Throwable cause) { super(msg, cause); }
            }

            static int loadPort(String raw) {
                try {
                    return Integer.parseInt(raw);
                } catch (NumberFormatException e) {
                    throw new ConfigException("invalid port in config: " + raw, e);   // wrap, keep cause
                }
            }

            public static void main(String[] args) {
                try {
                    loadPort("80a");
                } catch (ConfigException e) {
                    System.out.println(e.getMessage());
                    System.out.println("caused by " + e.getCause().getClass().getSimpleName()
                                       + ": " + e.getCause().getMessage());
                }
            }
        }
    ''', out="""
        invalid port in config: 80a
        caused by NumberFormatException: For input string: "80a"
    """)
    yield p("Translate low-level exceptions into ones that match your layer's abstraction (a repository throws `DataAccessException`, not `SQLException`) — but pass the original as the **cause** so the stack trace still shows the root problem (`Caused by: …`).")
    yield section("Anti-patterns", "ban")
    yield table(
        ["Anti-pattern", "Why it hurts", "Instead"],
        ["`catch (Exception e) {}`", "Swallows the failure — the bug disappears silently", "Handle it, or let it propagate"],
        ["`e.printStackTrace()` and continue", "Output goes to stderr, program runs on with bad state", "Log with a logger and rethrow/handle"],
        ["`throw new RuntimeException(e.getMessage())`", "Loses the original type and stack trace", "`throw new XException(\"context\", e)`"],
        ["Catch-log-rethrow at every layer", "The same error is logged five times", "Log once, where it's handled"],
        ["Exceptions for control flow", "Slow (stack trace capture) and hides intent", "Use `if`, `Optional`, return values"],
        ["`throws Exception` on every method", "Callers can't tell what can go wrong", "Declare specific types"],
        ["Catching `NullPointerException`", "Masks a bug", "Fix the null source / validate early"],
    )
    yield section("Best practices", "checklist")
    yield ul(
        "**Fail fast**: validate arguments at the start of a method (`Objects.requireNonNull`, `IllegalArgumentException`).",
        "Use **standard exceptions** when they fit: `IllegalArgumentException`, `IllegalStateException`, `UnsupportedOperationException`, `NoSuchElementException`.",
        "Put useful context in the message: the bad value, the id, the expected range.",
        "Name custom types `…Exception` and provide `(String message)` and `(String message, Throwable cause)` constructors.",
        "Restore the interrupt flag if you catch `InterruptedException` and can't rethrow it: `Thread.currentThread().interrupt();`.",
        "Clean up with try-with-resources, not `finally` blocks.",
    )
    yield qa("How do you create a custom exception?",
             "Extend `Exception` (checked) or `RuntimeException` (unchecked), add constructors that call `super(message)` and `super(message, cause)`, and optionally add fields carrying extra context (an error code, the invalid value).")
    yield qa("What is exception chaining and why use it?",
             "Wrapping a caught exception as the *cause* of a new, higher-level one (`new ServiceException(\"…\", e)`). The API stays at the right abstraction level while the full root cause remains available via `getCause()` and in the `Caused by:` part of the stack trace.")
    yield qa("Why are exceptions expensive?",
             "Creating one captures the whole stack trace (`fillInStackTrace`), which walks the stack. That's fine for exceptional cases but wasteful as normal control flow in a hot loop.")


@topic(G, "generics", "Generics: Classes, Methods & Bounded Types", "brackets-angle")
def _():
    yield lead("Generics let a class or method work with *any* type while the compiler still checks types — no casts, and type errors show up at compile time instead of as `ClassCastException` at runtime.")
    yield define("Type parameter", "a placeholder type such as `T` in `class Box<T>`. Using the class with a concrete type argument, `Box<String>`, makes every `T` mean `String` for the compiler.")
    yield section("Why generics?", "bulb")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            @SuppressWarnings({"rawtypes", "unchecked"})
            public static void main(String[] args) {
                List raw = new ArrayList();            // pre-Java-5 style: a list of Object
                raw.add("hello");
                raw.add(42);                           // compiler can't stop this
                try {
                    for (Object o : raw) {
                        String s = (String) o;         // manual cast, fails at runtime
                        System.out.println(s.toUpperCase());
                    }
                } catch (ClassCastException e) {
                    System.out.println("ClassCastException at runtime");
                }

                List<String> typed = new ArrayList<>();
                typed.add("hello");
                // typed.add(42);                      // compile error instead
                String s = typed.get(0);               // no cast needed
                System.out.println(s.length());
            }
        }
    ''', out="""
        HELLO
        ClassCastException at runtime
        5
    """)
    yield section("Generic classes", "box")
    yield snippet("java", r'''
        public class Main {
            static class Box<T> {
                private T value;
                Box(T value) { this.value = value; }
                T get() { return value; }
                <R> Box<R> map(java.util.function.Function<T, R> f) { return new Box<>(f.apply(value)); }
            }

            record Pair<A, B>(A first, B second) {
                Pair<B, A> swap() { return new Pair<>(second, first); }
            }

            public static void main(String[] args) {
                Box<String> name = new Box<>("generics");      // diamond: type inferred
                Box<Integer> len = name.map(String::length);
                System.out.println(name.get() + " " + len.get());

                Pair<String, Integer> p = new Pair<>("age", 30);
                System.out.println(p.swap());
                var q = new Pair<>(1.5, true);                  // Pair<Double, Boolean>
                System.out.println(q.first() + " " + q.second());
            }
        }
    ''', out="""
        generics 8
        Pair[first=30, second=age]
        1.5 true
    """)
    yield table(
        ["Convention", "Stands for"],
        ["`T`, `U`, `V`", "Type (first, second, third)"],
        ["`E`", "Element (collections)"],
        ["`K`, `V`", "Key, Value (maps)"],
        ["`R`", "Return / result type"],
        ["`N`", "Number"],
    )
    yield section("Generic methods", "function")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static <T> T firstOr(List<T> list, T fallback) {       // <T> before the return type
                return list.isEmpty() ? fallback : list.get(0);
            }

            static <K, V> Map<V, K> invert(Map<K, V> map) {
                Map<V, K> out = new TreeMap<>();
                map.forEach((k, v) -> out.put(v, k));
                return out;
            }

            public static void main(String[] args) {
                System.out.println(firstOr(List.of("a", "b"), "none"));
                System.out.println(firstOr(List.<Integer>of(), -1));     // explicit type witness
                System.out.println(invert(Map.of("one", 1, "two", 2)));
            }
        }
    ''', out="""
        a
        -1
        {1=one, 2=two}
    """)
    yield section("Bounded type parameters", "arrow-bar-to-up")
    yield p("`<T extends Bound>` restricts `T` to `Bound` or its subtypes — and in return lets you call `Bound`'s methods on a `T`. (`extends` is used for both classes and interfaces; multiple bounds: `<T extends Number & Comparable<T>>`, class first.)")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static <T extends Comparable<T>> T max(List<T> items) {
                T best = items.get(0);
                for (T item : items)
                    if (item.compareTo(best) > 0) best = item;   // compareTo allowed thanks to the bound
                return best;
            }

            static <N extends Number> double sum(List<N> nums) {
                double total = 0;
                for (N n : nums) total += n.doubleValue();       // Number's method
                return total;
            }

            public static void main(String[] args) {
                System.out.println(max(List.of(3, 9, 4)));
                System.out.println(max(List.of("pear", "apple", "zucchini")));
                System.out.println(sum(List.of(1, 2.5, 3L)));
            }
        }
    ''', out="""
        9
        zucchini
        6.5
    """)
    yield section("Primitives and restrictions", "alert-circle")
    yield ul(
        "Type arguments must be reference types: `List<int>` is illegal — use `List<Integer>` (autoboxing does the conversion).",
        "A static field or static method can't use the class's `T` (there's one static copy for all `Box<X>`), though a static method can declare its own `<T>`.",
        "You can't create `new T()`, `new T[n]`, or `new List<String>[n]` — see type erasure in the next topic.",
    )
    yield warn("**Raw types** (`List` instead of `List<String>`) exist only for pre-Java-5 compatibility. They switch off generic type checking for that variable and produce `rawtypes`/`unchecked` warnings. Never use them in new code; use `List<?>` if you really mean \"a list of unknown type\".", "Raw types")
    yield qa("What are generics and why use them?",
             "Parameterised types that let one class/method work with many types while keeping compile-time type safety. Benefits: errors caught at compile time, no explicit casts, and reusable, self-documenting APIs (`Map<String, List<Order>>`).")
    yield qa("What does <T extends Comparable<T>> mean?",
             "`T` can be any type that is comparable to itself, so the method may call `a.compareTo(b)` on two `T`s. The fully flexible version used by the JDK is `<T extends Comparable<? super T>>`, which also accepts types whose `compareTo` is inherited from a supertype.")
    yield qa("What is the diamond operator?",
             "`<>` in `new ArrayList<>()` (Java 7+): the compiler infers the type arguments from the context, so you don't repeat `ArrayList<String>`.")


@topic(G, "generics-wildcards", "Wildcards, PECS & Type Erasure", "asterisk")
def _():
    yield lead("`List<Integer>` is **not** a `List<Number>`. Wildcards (`?`, `? extends`, `? super`) restore flexibility, PECS tells you which to use, and type erasure explains generics' odd limitations.")
    yield section("Generics are invariant", "arrows-exchange")
    yield p("Even though `Integer` is a `Number`, `List<Integer>` is not a subtype of `List<Number>`. If it were, you could add a `Double` to a list of integers through the `List<Number>` reference.")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> ints = new ArrayList<>();
                List<Number> nums = ints;          // not allowed
                nums.add(3.14);
            }
        }
    ''', fails=True)
    yield output("""
        Main.java:6: error: incompatible types: List<Integer> cannot be converted to List<Number>
                List<Number> nums = ints;          // not allowed
                                    ^
    """, "Compiler error")
    yield p("Arrays are **covariant** (`Integer[]` *is* an `Object[]`), so the same mistake compiles and only fails at runtime:")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Object[] objs = new Integer[2];      // compiles: arrays are covariant
                objs[0] = 1;
                try {
                    objs[1] = "text";                // runtime type check
                } catch (ArrayStoreException e) {
                    System.out.println("ArrayStoreException: " + e.getMessage());
                }
            }
        }
    ''', out="ArrayStoreException: java.lang.String")
    yield section("The three wildcards", "asterisk")
    yield table(
        ["Wildcard", "Accepts", "Read as", "Can add?"],
        ["`List<?>`", "A list of *any* type", "`Object`", "Only `null`"],
        ["`List<? extends Number>`", "`List<Number>`, `List<Integer>`, `List<Double>`…", "`Number`", "No (except `null`)"],
        ["`List<? super Integer>`", "`List<Integer>`, `List<Number>`, `List<Object>`", "`Object`", "**Yes**, `Integer`s"],
    )
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static double sum(List<? extends Number> nums) {    // producer: we only read
                double s = 0;
                for (Number n : nums) s += n.doubleValue();
                return s;
            }

            static void fill(List<? super Integer> sink, int n) { // consumer: we only write
                for (int i = 1; i <= n; i++) sink.add(i);
            }

            static int count(Collection<?> anything) { return anything.size(); }

            public static void main(String[] args) {
                System.out.println(sum(List.of(1, 2, 3)));         // List<Integer>
                System.out.println(sum(List.of(1.5, 2.5)));        // List<Double>

                List<Number> numbers = new ArrayList<>();
                List<Object> objects = new ArrayList<>();
                fill(numbers, 3);
                fill(objects, 2);
                System.out.println(numbers + " " + objects);
                System.out.println(count(Set.of("a", "b")));
            }
        }
    ''', out="""
        6.0
        4.0
        [1, 2, 3] [1, 2]
        2
    """)
    yield section("PECS: Producer Extends, Consumer Super", "arrows-right-left")
    yield formula("If a parameter **produces** `T`s for you → `? extends T`.  If it **consumes** `T`s → `? super T`.  Both → plain `T`.")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            // src produces T (extends), dest consumes T (super) — same shape as Collections.copy
            static <T> void copy(List<? super T> dest, List<? extends T> src) {
                for (T item : src) dest.add(item);
            }

            public static void main(String[] args) {
                List<Integer> ints = List.of(1, 2);
                List<Double> doubles = List.of(3.5);
                List<Number> all = new ArrayList<>();
                copy(all, ints);                      // T = Integer, Number is a super of it
                copy(all, doubles);                   // T = Double
                System.out.println(all);

                List<Object> objs = new ArrayList<>(List.of("x"));
                Main.<Integer>copy(objs, ints);
                System.out.println(objs);
            }
        }
    ''', out="""
        [1, 2, 3.5]
        [x, 1, 2]
    """)
    yield p("JDK examples: `Collections.copy(List<? super T> dest, List<? extends T> src)`, `addAll(Collection<? extends E>)`, `sort(Comparator<? super E>)` — a `Comparator<Object>` can sort a list of strings.")
    yield section("Type erasure", "eraser")
    yield define("Type erasure", "generics exist only at compile time. The compiler checks types, inserts casts, then replaces each type parameter with its bound (`Object` if unbounded). At runtime, `List<String>` and `List<Integer>` are the same class, `ArrayList`.")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> a = new ArrayList<>();
                List<Integer> b = new ArrayList<>();
                System.out.println(a.getClass() == b.getClass());
                System.out.println(a.getClass().getName());
                Object o = a;
                System.out.println(o instanceof List<?>);      // OK: unbounded wildcard
                // o instanceof List<String>                   // error: can't check a type argument at runtime
            }
        }
    ''', out="""
        true
        java.util.ArrayList
        true
    """)
    yield table(
        ["You can't…", "Because at runtime `T` is erased", "Workaround"],
        ["`new T()`", "The JVM doesn't know what `T` is", "Pass a `Supplier<T>` or `Class<T>`"],
        ["`new T[n]`, `new List<String>[n]`", "Arrays need their exact element type at runtime", "Use a `List<T>`, or `(T[]) new Object[n]` with care"],
        ["`x instanceof List<String>`", "Type arguments aren't stored", "`instanceof List<?>`"],
        ["Overload `f(List<String>)` and `f(List<Integer>)`", "Both erase to `f(List)` — same signature", "Use different method names"],
        ["`catch (T e)` / generic exception classes", "Catch needs a runtime type", "—"],
        ["Use primitives as type arguments", "Erasure turns `T` into `Object`", "Boxed types, or specialised streams (`IntStream`)"],
    )
    yield snippet("java", r'''
        import java.util.*;
        import java.util.function.Supplier;

        public class Main {
            static <T> List<T> nCopies(int n, Supplier<T> factory) {    // instead of new T()
                List<T> out = new ArrayList<>();
                for (int i = 0; i < n; i++) out.add(factory.get());
                return out;
            }

            static <T> T create(Class<T> type) throws ReflectiveOperationException {
                return type.getDeclaredConstructor().newInstance();
            }

            public static void main(String[] args) throws Exception {
                System.out.println(nCopies(3, StringBuilder::new).size());
                System.out.println(create(ArrayList.class).isEmpty());
            }
        }
    ''', out="""
        3
        true
    """)
    yield section("Bridge methods and heap pollution", "bridge")
    yield p("When a class implements `Comparable<Money>`, its `compareTo(Money)` erases differently from the interface's `compareTo(Object)`. The compiler generates a synthetic **bridge method** `compareTo(Object)` that casts and delegates, so polymorphism still works after erasure.")
    yield snippet("java", r'''
        import java.lang.reflect.Method;

        public class Main {
            record Money(long cents) implements Comparable<Money> {
                public int compareTo(Money o) { return Long.compare(cents, o.cents); }
            }

            public static void main(String[] args) {
                java.util.List<String> found = new java.util.ArrayList<>();
                for (Method m : Money.class.getDeclaredMethods())
                    if (m.getName().equals("compareTo"))
                        found.add("compareTo(" + m.getParameterTypes()[0].getSimpleName() + ")"
                                  + (m.isBridge() ? " <- bridge" : ""));
                java.util.Collections.sort(found);
                found.forEach(System.out::println);
            }
        }
    ''', out="""
        compareTo(Money)
        compareTo(Object) <- bridge
    """)
    yield p("**Heap pollution** happens when a variable of a parameterised type refers to an object that isn't of that type — typically through raw types, unchecked casts or generic varargs (`T...` creates a `T[]`). The compiler warns (`unchecked`); `@SafeVarargs` marks a varargs method that doesn't misuse its array.")
    yield warn("An `unchecked` warning means the compiler can no longer guarantee type safety: a `ClassCastException` may appear later, far from the real bug, at a cast the compiler inserted. Don't suppress it unless you can prove the cast is safe.")
    yield qa("What is PECS?",
             "*Producer Extends, Consumer Super*: use `? extends T` for a parameter you read `T`s from, `? super T` for one you write `T`s into. E.g. `copy(List<? super T> dest, List<? extends T> src)`.")
    yield qa("Why is List<Integer> not a subtype of List<Number>?",
             "Generics are invariant for type safety: if it were, you could write `List<Number> n = ints; n.add(2.5);` and corrupt a list of integers. Use `List<? extends Number>` when you only need to read.")
    yield qa("What is type erasure and what are its consequences?",
             "The compiler removes type arguments after checking them, replacing type variables with their bounds and inserting casts. So generic type info isn't available at runtime: no `new T()`, no generic arrays, no `instanceof List<String>`, and methods differing only by type argument clash.")
    yield qa("List<?> vs List<Object>?",
             "`List<Object>` is a list you may add *any* object to, and only a `List<Object>` can be passed. `List<?>` accepts a list of *any* element type, but you can only read `Object`s from it and add nothing but `null`.")
