from kit import *

G = "Functional Java & Standard Library"


@topic(G, "functional-interfaces", "Functional Interfaces", "function")
def _():
    yield lead("An interface with exactly one abstract method — the *target type* that every lambda and method reference is converted to.")
    yield define("Functional interface", "an interface with a **single abstract method** (SAM). `default`, `static` and `private` methods don't count, nor do methods that `Object` already provides (`equals`, `toString`). A lambda is just a compact implementation of that one method.")
    yield section("Declaring one", "code")
    yield snippet("java", r'''
        public class Main {
            @FunctionalInterface
            interface Calculator {
                int apply(int a, int b);                 // the single abstract method

                default Calculator twice() {             // defaults are allowed
                    return (a, b) -> apply(apply(a, b), b);
                }
            }

            public static void main(String[] args) {
                Calculator add = (a, b) -> a + b;
                Calculator mul = (a, b) -> a * b;
                System.out.println(add.apply(3, 4));
                System.out.println(mul.apply(3, 4));
                System.out.println(add.twice().apply(3, 4));   // (3 + 4) + 4
            }
        }
    ''', out='''
        7
        12
        11
    ''')
    yield note("`@FunctionalInterface` is optional but recommended: the compiler then *rejects* the interface if someone adds a second abstract method, protecting every lambda that depends on it.", "Annotation")
    yield snippet("java", r'''
        @FunctionalInterface
        interface Broken {
            void first();
            void second();      // error: Broken is not a functional interface
        }
    ''', fails=True)
    yield section("The `java.util.function` toolbox", "tools")
    yield p("You rarely need to declare your own — the JDK ships 43 standard shapes. Learn the six core ones; the rest are variations.")
    yield table(
        ["Interface", "Method", "Shape", "Typical use"],
        ["`Predicate<T>`", "`boolean test(T t)`", "T → boolean", "`filter`, `removeIf`"],
        ["`Function<T, R>`", "`R apply(T t)`", "T → R", "`map`, `computeIfAbsent`"],
        ["`Consumer<T>`", "`void accept(T t)`", "T → nothing", "`forEach`"],
        ["`Supplier<T>`", "`T get()`", "nothing → T", "lazy defaults, `orElseGet`, factories"],
        ["`UnaryOperator<T>`", "`T apply(T t)`", "T → T", "`replaceAll`, `Stream.iterate`"],
        ["`BinaryOperator<T>`", "`T apply(T a, T b)`", "(T, T) → T", "`reduce`, `merge`"],
        ["`BiFunction<T, U, R>`", "`R apply(T t, U u)`", "(T, U) → R", "`Map.compute`, `replaceAll` on maps"],
        ["`BiConsumer<T, U>` / `BiPredicate<T, U>`", "`accept` / `test`", "two inputs", "`Map.forEach`"],
    )
    yield p("**Primitive specializations** avoid boxing: `IntPredicate`, `IntFunction<R>`, `ToIntFunction<T>`, `IntUnaryOperator`, `IntBinaryOperator`, `IntSupplier`, `IntConsumer` (plus `Long*` / `Double*` versions, and `ObjIntConsumer<T>`).")
    yield snippet("java", r'''
        import java.util.function.*;

        public class Main {
            public static void main(String[] args) {
                Predicate<String> isEmpty = String::isEmpty;
                Function<String, Integer> length = String::length;
                Consumer<String> shout = s -> System.out.println(s.toUpperCase());
                Supplier<String> greeting = () -> "hello";
                UnaryOperator<Integer> square = x -> x * x;
                BinaryOperator<Integer> max = Math::max;
                IntBinaryOperator add = (a, b) -> a + b;      // no boxing

                System.out.println(isEmpty.test(""));
                System.out.println(length.apply("lambda"));
                shout.accept("java");
                System.out.println(greeting.get());
                System.out.println(square.apply(7) + " " + max.apply(3, 9) + " " + add.applyAsInt(2, 3));
            }
        }
    ''', out='''
        true
        6
        JAVA
        hello
        49 9 5
    ''')
    yield section("Composition", "link")
    yield p("The standard interfaces have `default` methods that build new functions out of old ones — no new classes needed.")
    yield table(
        ["Method", "On", "Meaning"],
        ["`f.andThen(g)`", "`Function`, `Consumer`", "run `f`, then `g` on the result: `g(f(x))`"],
        ["`f.compose(g)`", "`Function`", "run `g` first: `f(g(x))`"],
        ["`p.and(q)` / `p.or(q)` / `p.negate()`", "`Predicate`", "logical combination (short-circuits)"],
        ["`Predicate.not(p)`", "`Predicate` (static, 11+)", "negate a method ref: `filter(not(String::isBlank))`"],
        ["`Function.identity()`", "`Function` (static)", "`x -> x`"],
    )
    yield snippet("java", r'''
        import java.util.function.*;

        public class Main {
            public static void main(String[] args) {
                Function<Integer, Integer> plus2 = x -> x + 2;
                Function<Integer, Integer> times3 = x -> x * 3;
                System.out.println(plus2.andThen(times3).apply(1));   // (1 + 2) * 3
                System.out.println(plus2.compose(times3).apply(1));   // (1 * 3) + 2

                Predicate<String> longWord = s -> s.length() > 4;
                Predicate<String> startsJ = s -> s.startsWith("J");
                System.out.println(longWord.and(startsJ).test("Java"));
                System.out.println(longWord.or(startsJ).test("Java"));
                System.out.println(longWord.negate().test("Java"));
            }
        }
    ''', out='''
        9
        5
        false
        true
        true
    ''')
    yield warn("A lambda has no type of its own — `var f = x -> x;` does not compile. The compiler needs a target functional interface from the assignment, parameter or cast.")
    yield qa("What makes an interface functional?", "Exactly one abstract method. `default`/`static`/`private` methods and abstract methods that match public `Object` methods (like `boolean equals(Object)` in `Comparator`) don't count. `Comparator`, `Runnable`, `Callable` and everything in `java.util.function` are functional interfaces.")
    yield qa("Why do primitive specializations like IntPredicate exist?", "Generics only work with reference types, so `Predicate<Integer>` boxes every `int` into an `Integer`. `IntPredicate.test(int)` takes the primitive directly — no allocation, no unboxing — which matters in hot loops and streams (`IntStream`).")
    yield qa("Function vs UnaryOperator vs BinaryOperator?", "`UnaryOperator<T>` extends `Function<T, T>` (same input and output type); `BinaryOperator<T>` extends `BiFunction<T, T, T>`. Use the narrower one when types match — it documents intent and fits APIs like `List.replaceAll(UnaryOperator)` and `Stream.reduce(BinaryOperator)`.")


@topic(G, "lambdas-method-refs", "Lambdas & Method References", "lambda")
def _():
    yield lead("A lambda is an anonymous function you can pass around as a value; a method reference is a lambda that just calls an existing method.")
    yield define("Lambda expression", "`(parameters) -> body` — an instance of a functional interface, written inline. Introduced in Java 8, it replaced most anonymous inner classes.")
    yield section("Syntax forms", "code")
    yield table(
        ["Form", "Example"],
        ["No parameters", "`() -> 42`"],
        ["One parameter (parentheses optional)", "`s -> s.length()`"],
        ["Several parameters", "`(a, b) -> a + b`"],
        ["Explicit types", "`(String a, String b) -> a.compareTo(b)`"],
        ["`var` parameters (11+, allows annotations)", "`(var a, var b) -> a + b`"],
        ["Block body (needs `return`)", "`x -> { int y = x * 2; return y + 1; }`"],
    )
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> names = new ArrayList<>(List.of("Ravi", "Asha", "Zoe", "Mohan"));

                // Before Java 8: an anonymous class
                names.sort(new Comparator<String>() {
                    @Override
                    public int compare(String a, String b) {
                        return a.compareTo(b);
                    }
                });
                System.out.println(names);

                // Java 8+: a lambda
                names.sort((a, b) -> b.length() - a.length());
                System.out.println(names);

                names.removeIf(s -> s.length() < 4);
                names.forEach(s -> System.out.print(s + " "));
                System.out.println();
            }
        }
    ''', out='''
        [Asha, Mohan, Ravi, Zoe]
        [Mohan, Asha, Ravi, Zoe]
        Mohan Asha Ravi
    ''')
    yield section("Capturing variables: effectively final", "lock")
    yield p("A lambda can read local variables from the enclosing method only if they are **effectively final** — never reassigned after initialisation. The lambda captures the *value*, and Java forbids the variable changing underneath it.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                int count = 0;
                Runnable r = () -> count++;     // error: must be final or effectively final
                r.run();
            }
        }
    ''', fails=True)
    yield snippet("java", r'''
        import java.util.*;
        import java.util.concurrent.atomic.AtomicInteger;

        public class Main {
            public static void main(String[] args) {
                String prefix = "item-";                  // effectively final: OK to capture
                AtomicInteger counter = new AtomicInteger();  // the reference is final; its state can change
                List.of("a", "b", "c").forEach(s -> {
                    counter.incrementAndGet();
                    System.out.println(prefix + s);
                });
                System.out.println("count = " + counter.get());
            }
        }
    ''', out='''
        item-a
        item-b
        item-c
        count = 3
    ''')
    yield note("Fields (instance or `static`) are *not* restricted — a lambda reads them through `this` or the class. Only captured **local** variables must be effectively final.", "Fields are different")
    yield section("`this` in a lambda vs an anonymous class", "arrows-exchange")
    yield snippet("java", r'''
        public class Main {
            String name = "outer";

            void demo() {
                Runnable lambda = () -> System.out.println("lambda this: " + this.name);
                Runnable anon = new Runnable() {
                    String name = "anonymous";
                    @Override
                    public void run() {
                        System.out.println("anon this:   " + this.name);
                    }
                };
                lambda.run();
                anon.run();
            }

            public static void main(String[] args) {
                new Main().demo();
            }
        }
    ''', out='''
        lambda this: outer
        anon this:   anonymous
    ''')
    yield table(
        ["", "Lambda", "Anonymous class"],
        ["`this` refers to", "the **enclosing** instance", "the anonymous object itself"],
        ["New scope?", "No — can't redeclare an enclosing local name", "Yes — can shadow names"],
        ["Implements", "only functional interfaces", "any interface or class, many methods, can hold state"],
        ["Compiled to", "`invokedynamic` + a private method (no extra `.class` file)", "a separate `Outer$1.class`"],
    )
    yield section("Method references — four kinds", "link")
    yield p("When a lambda only forwards its arguments to one method, write `Class::method` instead.")
    yield table(
        ["Kind", "Syntax", "Equivalent lambda"],
        ["Static method", "`Integer::parseInt`", "`s -> Integer.parseInt(s)`"],
        ["Instance method of a **particular** object", "`System.out::println`", "`x -> System.out.println(x)`"],
        ["Instance method of an **arbitrary** object of a type", "`String::toUpperCase`", "`s -> s.toUpperCase()`"],
        ["Constructor", "`ArrayList::new`", "`() -> new ArrayList<>()`"],
    )
    yield snippet("java", r'''
        import java.util.*;
        import java.util.function.*;

        public class Main {
            public static void main(String[] args) {
                Function<String, Integer> parse = Integer::parseInt;         // static
                String greeting = "Hello";
                Predicate<String> startsWithIt = greeting::startsWith;       // particular object
                Function<String, String> upper = String::toUpperCase;        // arbitrary object
                BiFunction<String, String, Boolean> eq = String::equalsIgnoreCase; // first arg is the receiver
                Supplier<List<String>> newList = ArrayList::new;             // constructor
                Function<Integer, int[]> newArray = int[]::new;              // array constructor

                System.out.println(parse.apply("41") + 1);
                System.out.println(startsWithIt.test("Hell"));
                System.out.println(upper.apply("java"));
                System.out.println(eq.apply("JAVA", "java"));
                List<String> list = newList.get();
                list.add("x");
                System.out.println(list + " " + newArray.apply(3).length);
            }
        }
    ''', out='''
        42
        true
        JAVA
        true
        [x] 3
    ''')
    yield warn("`System.out::println` evaluates `System.out` *once*, when the reference is created — the lambda `x -> System.out.println(x)` looks it up on every call. Usually irrelevant, but a `null` receiver in `obj::method` throws `NullPointerException` immediately, not when called.")
    yield qa("Are lambdas just syntactic sugar for anonymous classes?", "No. They compile to an `invokedynamic` call site plus a private synthetic method; the JVM creates the implementation at run time (via `LambdaMetafactory`). No `.class` file per lambda, non-capturing lambdas are cached as singletons, and `this` means the enclosing instance rather than a new object.")
    yield qa("Why must captured local variables be effectively final?", "Locals live on the stack frame of the method, which may be gone by the time the lambda runs (e.g. on another thread). Java copies the value into the lambda; allowing later reassignment would make the copy silently stale and invite data races. Use a field, an array element or an `AtomicInteger` if you really need mutable state — or better, restructure with a stream reduction.")
    yield qa("What does String::compareTo mean when a Comparator<String> is expected?", "It's an *unbound* instance-method reference: the first parameter becomes the receiver. `(a, b) -> a.compareTo(b)`. That's why a two-argument functional interface can be satisfied by a one-argument instance method.")


@topic(G, "streams", "Streams API: Intermediate & Terminal Operations", "arrows-right")
def _():
    yield lead("A stream is a lazy pipeline of operations over a sequence of elements — declare *what* to compute, and the library does the looping.")
    yield define("Stream", "a sequence of elements supporting aggregate operations. It **stores nothing**, **doesn't modify its source**, is **lazy** (nothing runs until a terminal operation) and is **single-use**.")
    yield flow("Source (`list.stream()`)", "Intermediate ops (`filter`, `map`…) — lazy", "Terminal op (`collect`, `sum`…) — triggers work", "Result")
    yield section("A first pipeline", "code")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> words = List.of("stream", "java", "lambda", "api", "collector", "map");

                List<String> result = words.stream()
                        .filter(w -> w.length() > 3)      // keep long words
                        .map(String::toUpperCase)         // transform
                        .sorted()                         // natural order
                        .toList();                        // terminal (Java 16+)
                System.out.println(result);

                // the imperative equivalent
                List<String> loop = new ArrayList<>();
                for (String w : words) if (w.length() > 3) loop.add(w.toUpperCase());
                Collections.sort(loop);
                System.out.println(loop.equals(result));
            }
        }
    ''', out='''
        [COLLECTOR, JAVA, LAMBDA, STREAM]
        true
    ''')
    yield section("Creating streams", "plus")
    yield table(
        ["Source", "Example"],
        ["Collection", "`list.stream()`, `set.parallelStream()`"],
        ["Array", "`Arrays.stream(arr)`, `Stream.of(1, 2, 3)`"],
        ["Numeric range", "`IntStream.range(0, 5)` (end exclusive), `rangeClosed(1, 5)`"],
        ["Generated", "`Stream.iterate(1, x -> x * 2)`, `Stream.generate(supplier)` — infinite, use `limit`"],
        ["Bounded iterate (9+)", "`Stream.iterate(1, x -> x < 100, x -> x * 2)`"],
        ["Others", "`str.chars()`, `Files.lines(path)`, `map.entrySet().stream()`, `Stream.empty()`"],
    )
    yield section("Intermediate operations (lazy, return a Stream)", "filter")
    yield table(
        ["Operation", "What it does", "Stateful?"],
        ["`filter(pred)`", "keep elements matching", "No"],
        ["`map(fn)` / `mapToInt(fn)`", "transform each element (1 → 1)", "No"],
        ["`flatMap(fn)`", "each element → a stream, flattened (1 → many)", "No"],
        ["`peek(action)`", "look at elements as they pass (debugging)", "No"],
        ["`distinct()`", "drop duplicates (uses `equals`/`hashCode`)", "**Yes**"],
        ["`sorted()` / `sorted(cmp)`", "sort — must see *all* elements first", "**Yes**"],
        ["`limit(n)` / `skip(n)`", "first n / drop first n (short-circuit `limit`)", "Yes (count)"],
        ["`takeWhile` / `dropWhile` (9+)", "prefix while predicate holds", "No"],
    )
    yield snippet("java", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<List<Integer>> nested = List.of(List.of(1, 2), List.of(3, 4), List.of(4, 5));
                System.out.println(nested.stream().flatMap(List::stream).toList());
                System.out.println(nested.stream().flatMap(List::stream).distinct().skip(1).limit(3).toList());

                System.out.println(Stream.of("b", "a", "c").sorted(Comparator.reverseOrder()).toList());
                System.out.println(Stream.iterate(1, x -> x * 2).limit(6).toList());
                System.out.println(IntStream.rangeClosed(1, 10).takeWhile(i -> i < 5).boxed().toList());
                System.out.println("hello".chars().filter(c -> c == 'l').count());
            }
        }
    ''', out='''
        [1, 2, 3, 4, 4, 5]
        [2, 3, 4]
        [c, b, a]
        [1, 2, 4, 8, 16, 32]
        [1, 2, 3, 4]
        2
    ''')
    yield section("Laziness: nothing runs until the terminal op", "player-pause")
    yield snippet("java", r'''
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                Stream<Integer> pipeline = Stream.of(1, 2, 3, 4, 5, 6)
                        .peek(x -> System.out.println("saw " + x))
                        .filter(x -> x % 2 == 0)
                        .map(x -> x * 10);
                System.out.println("pipeline built, nothing printed yet");

                Integer first = pipeline.findFirst().orElseThrow();   // terminal op
                System.out.println("first = " + first);
            }
        }
    ''', out='''
        pipeline built, nothing printed yet
        saw 1
        saw 2
        first = 20
    ''')
    yield note("Elements flow through the pipeline **one at a time** (vertical processing), not stage by stage. With a short-circuiting terminal op like `findFirst`, `anyMatch` or `limit`, the stream stops as soon as it has its answer — here it never looked at 3–6.", "Vertical, short-circuiting")
    yield section("Terminal operations", "flag")
    yield table(
        ["Operation", "Returns", "Notes"],
        ["`forEach(action)`", "void", "order not guaranteed on parallel streams (`forEachOrdered`)"],
        ["`collect(collector)` / `toList()`", "a collection / value", "see Collectors topic"],
        ["`reduce(identity, op)`", "`T`", "fold into one value"],
        ["`count()`, `min(cmp)`, `max(cmp)`", "`long`, `Optional<T>`", "min/max are Optional — stream may be empty"],
        ["`sum()`, `average()`, `summaryStatistics()`", "number / `OptionalDouble`", "only on `IntStream`/`LongStream`/`DoubleStream`"],
        ["`anyMatch`, `allMatch`, `noneMatch`", "`boolean`", "short-circuit; `allMatch` on empty = `true`"],
        ["`findFirst()`, `findAny()`", "`Optional<T>`", "`findAny` is faster on parallel streams"],
        ["`toArray()`", "array", "`toArray(String[]::new)` for a typed array"],
    )
    yield snippet("java", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = List.of(4, 8, 15, 16, 23, 42);

                System.out.println(nums.stream().reduce(0, Integer::sum));
                System.out.println(nums.stream().reduce(Integer::max).get());
                System.out.println(nums.stream().mapToInt(Integer::intValue).sum());
                System.out.println(nums.stream().mapToInt(i -> i).average().getAsDouble());
                System.out.println(nums.stream().max(Comparator.naturalOrder()).get());
                System.out.println(nums.stream().filter(n -> n > 100).count());
                System.out.println(nums.stream().anyMatch(n -> n % 2 == 1) + " " + nums.stream().allMatch(n -> n > 0));
                IntSummaryStatistics st = nums.stream().mapToInt(i -> i).summaryStatistics();
                System.out.println(st.getMin() + ".." + st.getMax() + " avg " + st.getAverage());
                String[] arr = Stream.of("x", "y").toArray(String[]::new);
                System.out.println(Arrays.toString(arr));
            }
        }
    ''', out='''
        108
        42
        108
        18.0
        42
        0
        true true
        4..42 avg 18.0
        [x, y]
    ''')
    yield section("Primitive streams and boxing", "number")
    yield p("`IntStream`, `LongStream` and `DoubleStream` avoid boxing and add `sum`, `average`, `range`. Convert with `mapToInt` / `mapToObj` / `boxed()`.")
    yield snippet("java", r'''
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                System.out.println(IntStream.range(0, 5).sum());
                System.out.println(IntStream.range(0, 5).boxed().toList());
                System.out.println(IntStream.rangeClosed(1, 5).mapToObj(i -> "#" + i).collect(Collectors.joining(",")));
                System.out.println(IntStream.of(3, 1, 2).map(i -> i * i).sorted().boxed().toList());
            }
        }
    ''', out='''
        10
        [0, 1, 2, 3, 4]
        #1,#2,#3,#4,#5
        [1, 4, 9]
    ''')
    yield section("Streams are single-use", "ban")
    yield snippet("java", r'''
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                Stream<String> s = Stream.of("a", "b");
                System.out.println(s.count());
                try {
                    s.count();                        // reuse → exception
                } catch (IllegalStateException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out='''
        2
        stream has already been operated upon or closed
    ''')
    yield good("Need the data twice? Keep the *collection* and call `.stream()` again, or hold a `Supplier<Stream<T>>`.")
    yield section("Parallel streams — use with care", "arrows-split")
    yield ul(
        "`list.parallelStream()` or `.parallel()` splits the work across the common `ForkJoinPool` (cores − 1 threads).",
        "Worth it only for **large**, CPU-bound, easily splittable data (`ArrayList`, arrays, ranges) — not `LinkedList` or I/O.",
        "Lambdas must be **stateless and non-interfering**: never mutate a shared `ArrayList` from `forEach` — use `collect`.",
        "`reduce` needs an associative operation and a true identity (`0` for sum), or results change with the split.",
        "Order-dependent ops (`findFirst`, `limit`, `forEachOrdered`) cost extra in parallel; `findAny` / `unordered()` are cheaper.",
    )
    yield warn("Side effects in stream lambdas (`peek`, `map` that writes to an outer list) are a classic bug: behaviour can change with parallelism, and since Java 9 `count()` may even *skip* running `peek`/`map` when it can compute the size directly.")
    yield qa("Intermediate vs terminal operations?", "Intermediate ops (`filter`, `map`, `sorted`) return a new `Stream` and are lazy — they only describe the pipeline. A terminal op (`collect`, `forEach`, `reduce`, `count`) consumes the stream, triggers all the work and produces a result or side effect. Without a terminal op, nothing executes.")
    yield qa("map vs flatMap?", "`map` turns each element into exactly one element (`Stream<List<T>>` stays a stream of lists). `flatMap` turns each element into a *stream* and concatenates them — one-to-many, flattening `Stream<List<T>>` into `Stream<T>`.")
    yield qa("Stateless vs stateful intermediate operations?", "Stateless ops (`filter`, `map`, `flatMap`) handle each element independently. Stateful ops (`sorted`, `distinct`, `limit`, `skip`) must remember elements seen so far — `sorted` buffers the entire stream before emitting anything, which hurts on huge or infinite streams and in parallel.")
    yield qa("Can a stream be reused? Does it modify its source?", "No and no. A stream can be traversed once; a second terminal op throws `IllegalStateException`. It never changes the source collection — it produces new results. Modifying the source while the stream runs is interference and may throw `ConcurrentModificationException`.")


@topic(G, "collectors", "Collectors & groupingBy", "category")
def _():
    yield lead("`collect(...)` is the terminal operation that turns a stream into a collection, map, string or summary — and `Collectors` is the toolbox of recipes for it.")
    yield define("Collector", "a recipe of four functions — *supplier* (new container), *accumulator* (add an element), *combiner* (merge two containers, for parallel runs) and *finisher* — that `Stream.collect` uses to perform a mutable reduction.")
    yield section("Into lists and sets", "list")
    yield table(
        ["Call", "Result", "Mutable?", "Nulls?"],
        ["`stream.toList()` (16+)", "`List<T>`", "**No** — unmodifiable", "allowed"],
        ["`collect(Collectors.toList())`", "`List<T>` (an `ArrayList` in practice)", "yes (not guaranteed)", "allowed"],
        ["`collect(Collectors.toUnmodifiableList())` (10+)", "`List<T>`", "No", "**NPE**"],
        ["`collect(Collectors.toSet())`", "`Set<T>` (a `HashSet`)", "yes", "allowed"],
        ["`collect(Collectors.toCollection(TreeSet::new))`", "the exact type you choose", "yes", "depends"],
    )
    yield snippet("java", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<String> fixed = Stream.of("b", "a").toList();
                List<String> growable = Stream.of("b", "a").collect(Collectors.toList());
                growable.add("c");
                System.out.println(growable);
                try {
                    fixed.add("c");
                } catch (UnsupportedOperationException e) {
                    System.out.println("toList() result is unmodifiable");
                }
                TreeSet<String> sorted = Stream.of("pear", "apple", "fig", "apple")
                        .collect(Collectors.toCollection(TreeSet::new));
                System.out.println(sorted);
            }
        }
    ''', out='''
        [b, a, c]
        toList() result is unmodifiable
        [apple, fig, pear]
    ''')
    yield section("Into maps: `toMap`", "map")
    yield snippet("java", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<String> words = List.of("apple", "avocado", "banana", "cherry");

                Map<String, Integer> lengths = words.stream()
                        .collect(Collectors.toMap(w -> w, String::length, (a, b) -> a, TreeMap::new));
                System.out.println(lengths);

                try {
                    words.stream().collect(Collectors.toMap(w -> w.charAt(0), w -> w));   // 'a' twice
                } catch (IllegalStateException e) {
                    System.out.println(e.getMessage());
                }

                // merge function decides what to do with duplicate keys
                Map<Character, String> byLetter = words.stream()
                        .collect(Collectors.toMap(w -> w.charAt(0), w -> w, (a, b) -> a + "|" + b, TreeMap::new));
                System.out.println(byLetter);
            }
        }
    ''', out='''
        {apple=5, avocado=7, banana=6, cherry=6}
        Duplicate key a (attempted merging values apple and avocado)
        {a=apple|avocado, b=banana, c=cherry}
    ''')
    yield warn("`toMap(keyFn, valueFn)` throws `IllegalStateException: Duplicate key` on the first collision, and `NullPointerException` if a *value* is `null`. Pass a merge function whenever keys might repeat.")
    yield section("`groupingBy` — the SQL `GROUP BY` of Java", "table")
    yield p("`groupingBy(classifier)` builds a `Map<K, List<T>>`. The two optional arguments are the **map factory** and a **downstream collector** applied to each group.")
    yield snippet("java", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            record Emp(String name, String dept, int salary) {}

            public static void main(String[] args) {
                List<Emp> emps = List.of(
                        new Emp("Asha", "Eng", 120), new Emp("Ravi", "HR", 70),
                        new Emp("Zoe", "Eng", 100), new Emp("Mohan", "Sales", 80),
                        new Emp("Lena", "HR", 75));

                Map<String, List<String>> names = emps.stream().collect(Collectors.groupingBy(
                        Emp::dept, TreeMap::new, Collectors.mapping(Emp::name, Collectors.toList())));
                System.out.println(names);

                Map<String, Long> counts = emps.stream().collect(
                        Collectors.groupingBy(Emp::dept, TreeMap::new, Collectors.counting()));
                System.out.println(counts);

                Map<String, Integer> payroll = emps.stream().collect(
                        Collectors.groupingBy(Emp::dept, TreeMap::new, Collectors.summingInt(Emp::salary)));
                System.out.println(payroll);

                Map<String, Double> avg = emps.stream().collect(
                        Collectors.groupingBy(Emp::dept, TreeMap::new, Collectors.averagingInt(Emp::salary)));
                System.out.println(avg);

                Map<String, Optional<Emp>> top = emps.stream().collect(Collectors.groupingBy(
                        Emp::dept, TreeMap::new, Collectors.maxBy(Comparator.comparingInt(Emp::salary))));
                top.forEach((d, e) -> System.out.println(d + " -> " + e.get().name()));
            }
        }
    ''', out='''
        {Eng=[Asha, Zoe], HR=[Ravi, Lena], Sales=[Mohan]}
        {Eng=2, HR=2, Sales=1}
        {Eng=220, HR=145, Sales=80}
        {Eng=110.0, HR=72.5, Sales=80.0}
        Eng -> Asha
        HR -> Lena
        Sales -> Mohan
    ''')
    yield note("Plain `groupingBy(f)` returns a `HashMap`, so the key order you print is not something to rely on. Pass `TreeMap::new` (sorted) or `LinkedHashMap::new` (encounter order) when order matters.", "Deterministic order")
    yield table(
        ["Downstream collector", "Per group you get"],
        ["`counting()`", "`Long` count"],
        ["`summingInt(f)` / `averagingDouble(f)`", "sum / average"],
        ["`mapping(f, toList())`", "a list of a projected field"],
        ["`maxBy(cmp)` / `minBy(cmp)`", "`Optional<T>`"],
        ["`toSet()`, `joining(\", \")`", "set / concatenated string"],
        ["`collectingAndThen(c, fn)`", "post-process, e.g. unwrap the `Optional`"],
        ["`groupingBy(...)`", "nested (multi-level) grouping"],
    )
    yield section("`partitioningBy`, `joining` and friends", "arrows-split-2")
    yield snippet("java", r'''
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = List.of(1, 2, 3, 4, 5, 6, 7);

                Map<Boolean, List<Integer>> evenOdd = nums.stream()
                        .collect(Collectors.partitioningBy(n -> n % 2 == 0));
                System.out.println(evenOdd);

                System.out.println(Stream.of("a", "b", "c").collect(Collectors.joining(", ", "[", "]")));

                IntSummaryStatistics st = nums.stream().collect(Collectors.summarizingInt(n -> n));
                System.out.println(st);

                Map<Integer, Long> byLength = Stream.of("hi", "yo", "hey", "java", "sun")
                        .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));
                System.out.println(byLength);
            }
        }
    ''', out='''
        {false=[1, 3, 5, 7], true=[2, 4, 6]}
        [a, b, c]
        IntSummaryStatistics{count=7, sum=28, min=1, average=4.000000, max=7}
        {2=2, 3=2, 4=1}
    ''')
    yield p("`partitioningBy` always has exactly two keys, `false` and `true` — even if one group is empty — which makes it nicer than `groupingBy` with a boolean.")
    yield qa("Stream.toList() vs Collectors.toList()?", "`Stream.toList()` (Java 16) returns an **unmodifiable** list and accepts `null` elements. `Collectors.toList()` returns a list with no guarantees on type or mutability (an `ArrayList` in practice, so callers often mutate it). Prefer `toList()` for results you only read; use `toCollection(ArrayList::new)` when you need to mutate.")
    yield qa("How would you count word frequencies with streams?", "`words.stream().collect(Collectors.groupingBy(Function.identity(), Collectors.counting()))` → `Map<String, Long>`. Add `TreeMap::new` as the middle argument for sorted keys.")
    yield qa("What happens with duplicate keys in Collectors.toMap?", "Without a merge function it throws `IllegalStateException` (\"Duplicate key …\"). Supply the third argument, e.g. `(a, b) -> a` to keep the first or `Integer::sum` to add counts; a fourth argument chooses the map implementation.")


@topic(G, "optional", "Optional", "question-mark")
def _():
    yield lead("A container that holds either one value or nothing — a return type that forces callers to think about *absence* instead of forgetting a null check.")
    yield define("Optional<T>", "an immutable box that is either *present* (holds a non-null value) or *empty*. Introduced in Java 8, designed for **method return types** where \"no result\" is a normal outcome.")
    yield section("Creating", "plus")
    yield table(
        ["Factory", "When"],
        ["`Optional.of(v)`", "`v` is definitely non-null — throws `NullPointerException` otherwise"],
        ["`Optional.ofNullable(v)`", "`v` may be `null` → empty"],
        ["`Optional.empty()`", "explicitly no value"],
    )
    yield section("Using the value — don't just call `get()`", "code")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static Map<String, String> emails = Map.of("asha", "asha@mail.com");

            static Optional<String> findEmail(String user) {
                return Optional.ofNullable(emails.get(user));
            }

            public static void main(String[] args) {
                System.out.println(findEmail("asha"));
                System.out.println(findEmail("ravi"));

                System.out.println(findEmail("ravi").orElse("no-email"));
                System.out.println(findEmail("asha").map(String::toUpperCase).orElse("?"));
                System.out.println(findEmail("asha").filter(e -> e.endsWith(".org")).isPresent());
                findEmail("asha").ifPresent(e -> System.out.println("send to " + e));
                findEmail("ravi").ifPresentOrElse(
                        e -> System.out.println("send to " + e),
                        () -> System.out.println("nobody to email"));
                try {
                    findEmail("ravi").orElseThrow();
                } catch (NoSuchElementException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out='''
        Optional[asha@mail.com]
        Optional.empty
        no-email
        ASHA@MAIL.COM
        false
        send to asha@mail.com
        nobody to email
        No value present
    ''')
    yield table(
        ["Method", "Does"],
        ["`isPresent()` / `isEmpty()` (11+)", "test"],
        ["`get()` / `orElseThrow()` (10+)", "value or `NoSuchElementException` — prefer the clearer `orElseThrow()`"],
        ["`orElse(x)`", "value or `x` (x is **always evaluated**)"],
        ["`orElseGet(supplier)`", "value or `supplier.get()` (evaluated **only if empty**)"],
        ["`orElseThrow(() -> new MyEx())`", "value or your exception"],
        ["`map(f)` / `flatMap(f)`", "transform if present (`flatMap` when `f` already returns an `Optional`)"],
        ["`filter(pred)`", "empty unless the predicate holds"],
        ["`ifPresent(c)` / `ifPresentOrElse(c, r)` (9+)", "run code"],
        ["`or(supplier)` (9+)", "fall back to another `Optional`"],
        ["`stream()` (9+)", "0- or 1-element stream"],
    )
    yield section("The `orElse` vs `orElseGet` trap", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static String expensiveDefault() {
                System.out.println("  (computing default...)");
                return "default";
            }

            public static void main(String[] args) {
                Optional<String> name = Optional.of("Asha");
                System.out.println("orElse:");
                System.out.println(name.orElse(expensiveDefault()));      // default is computed anyway!
                System.out.println("orElseGet:");
                System.out.println(name.orElseGet(Main::expensiveDefault)); // lazy — not called
            }
        }
    ''', out='''
        orElse:
          (computing default...)
        Asha
        orElseGet:
        Asha
    ''')
    yield warn("`orElse(createUser())` runs `createUser()` even when the value is present — wasteful, or a real bug if it has side effects (a DB insert). Use `orElseGet` for anything non-trivial.")
    yield section("`map` vs `flatMap` — chaining without null checks", "link")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            record Address(String city) {}
            record User(String name, Optional<Address> address) {}

            public static void main(String[] args) {
                User withAddr = new User("Asha", Optional.of(new Address("Pune")));
                User without = new User("Ravi", Optional.empty());

                for (User u : List.of(withAddr, without)) {
                    String city = Optional.of(u)
                            .flatMap(User::address)          // already Optional → flatMap
                            .map(Address::city)              // plain value → map
                            .orElse("unknown");
                    System.out.println(u.name() + ": " + city);
                }
            }
        }
    ''', out='''
        Asha: Pune
        Ravi: unknown
    ''')
    yield note("The record above stores an `Optional` field only to demonstrate `flatMap`. In real code, keep the field nullable and expose `Optional<Address> address()` from a getter.", "Demo only")
    yield section("How *not* to use Optional", "ban")
    yield dodont(
        "Return `Optional<T>` from methods that may find nothing (`findById`, `max`). Chain with `map`/`filter`/`orElse`. Return empty collections, not `Optional<List<T>>`.",
        "Optional fields, method parameters or collection elements; `Optional.get()` without a check; `if (opt.isPresent()) opt.get()` (just a verbose null check); returning `null` from a method whose return type is `Optional`.",
    )
    yield p("`Optional` is not `Serializable`, adds an allocation, and a parameter of type `Optional` can itself be `null` — so it solves nothing there. Primitive versions `OptionalInt`, `OptionalLong`, `OptionalDouble` avoid boxing (returned by `IntStream.max()` etc.).")
    yield qa("Why was Optional added?", "To make \"no result\" explicit in an API's type. A method returning `Optional<User>` tells callers at compile time that the user may be missing, pushing them to handle it (`orElse`, `orElseThrow`) instead of risking a `NullPointerException`. It was designed primarily for stream results like `findFirst` and `max`.")
    yield qa("Difference between orElse and orElseGet?", "`orElse(value)` takes an already-computed value, so its argument is evaluated even when the Optional is present. `orElseGet(supplier)` takes a function that is called only when empty. Use `orElse` for constants, `orElseGet` for anything costly or with side effects.")
    yield qa("Should you use Optional as a field or method parameter?", "No. It's intended for return types. As a field it isn't serializable and adds overhead; as a parameter the caller could still pass `null`, and overloading or a nullable parameter is clearer.")


@topic(G, "java-time", "Date & Time API (java.time)", "calendar-time")
def _():
    yield lead("Java 8's `java.time` package replaced the broken `Date` and `Calendar` classes with immutable, thread-safe types that say exactly what they mean.")
    yield section("Why the old API was bad", "bug")
    yield cards(
        ("Mutable", "`Date` and `Calendar` have setters — sharing one between objects or threads leads to surprise changes.", "edit"),
        ("Confusing", "`Date` is really an instant; months in `Calendar` start at 0 (`Calendar.JANUARY == 0`); years in `Date` are offset by 1900.", "question-mark"),
        ("Not thread-safe", "`SimpleDateFormat` keeps internal state — sharing one across threads corrupts results.", "users"),
        ("One type for everything", "No separate concept of \"a date\", \"a time of day\" or \"a duration\".", "box"),
    )
    yield section("The main types", "calendar")
    yield table(
        ["Type", "Represents", "Example"],
        ["`LocalDate`", "a date without time or zone", "`2024-03-15` — birthdays, holidays"],
        ["`LocalTime`", "a time of day", "`09:30`"],
        ["`LocalDateTime`", "date + time, no zone", "`2024-03-15T09:30` — a meeting \"on the wall clock\""],
        ["`ZonedDateTime`", "date + time + zone rules (DST aware)", "`2024-03-15T09:30+05:30[Asia/Kolkata]`"],
        ["`Instant`", "a point on the UTC timeline (epoch nanos)", "`2024-03-15T04:00:00Z` — timestamps, logs"],
        ["`Duration`", "a time-based amount (seconds/nanos)", "`PT1H30M`"],
        ["`Period`", "a date-based amount (years/months/days)", "`P1Y2M3D`"],
        ["`DateTimeFormatter`", "immutable, thread-safe formatter/parser", "`ofPattern(\"dd/MM/yyyy\")`"],
    )
    yield section("Creating and manipulating (always returns a new object)", "code")
    yield snippet("java", r'''
        import java.time.*;
        import java.time.temporal.ChronoUnit;

        public class Main {
            public static void main(String[] args) {
                LocalDate d = LocalDate.of(2024, 1, 31);
                System.out.println(d);
                System.out.println(d.plusMonths(1));             // clamps to Feb 29 (leap year)
                System.out.println(d.plusDays(1).getDayOfWeek());
                System.out.println(d.isLeapYear() + " " + d.lengthOfMonth());

                d.plusYears(1);                                  // result ignored — d unchanged!
                System.out.println(d);

                LocalDateTime meeting = LocalDateTime.of(2024, 3, 15, 9, 30);
                System.out.println(meeting.plusHours(2).withMinute(0));

                LocalDate a = LocalDate.of(2024, 1, 1), b = LocalDate.of(2024, 12, 25);
                System.out.println(ChronoUnit.DAYS.between(a, b));
                System.out.println(Period.between(a, b));
                System.out.println(a.isBefore(b));
            }
        }
    ''', out='''
        2024-01-31
        2024-02-29
        THURSDAY
        true 31
        2024-01-31
        2024-03-15T11:00
        359
        P11M24D
        true
    ''')
    yield warn("Every `plus`/`with` method returns a *new* object. Writing `date.plusDays(1);` on its own line does nothing — assign the result.")
    yield section("Zones, instants and durations", "world")
    yield snippet("java", r'''
        import java.time.*;

        public class Main {
            public static void main(String[] args) {
                LocalDateTime local = LocalDateTime.of(2024, 3, 15, 9, 30);
                ZonedDateTime india = local.atZone(ZoneId.of("Asia/Kolkata"));
                ZonedDateTime ny = india.withZoneSameInstant(ZoneId.of("America/New_York"));
                System.out.println(india);
                System.out.println(ny);

                Instant instant = india.toInstant();
                System.out.println(instant);
                System.out.println(instant.getEpochSecond());
                System.out.println(Instant.ofEpochSecond(0));

                Duration flight = Duration.ofMinutes(135);
                System.out.println(flight + " = " + flight.toHours() + "h " + flight.toMinutesPart() + "m");
                System.out.println(Duration.between(LocalTime.of(9, 0), LocalTime.of(17, 45)));
            }
        }
    ''', out='''
        2024-03-15T09:30+05:30[Asia/Kolkata]
        2024-03-15T00:00-04:00[America/New_York]
        2024-03-15T04:00:00Z
        1710475200
        1970-01-01T00:00:00Z
        PT2H15M = 2h 15m
        PT8H45M
    ''')
    yield note("`Duration` measures machine time (exact seconds); `Period` measures calendar time. Adding `Period.ofDays(1)` across a DST change keeps the wall-clock time; adding `Duration.ofHours(24)` keeps the exact elapsed time.", "Duration vs Period")
    yield section("Formatting and parsing", "typography")
    yield snippet("java", r'''
        import java.time.*;
        import java.time.format.*;

        public class Main {
            public static void main(String[] args) {
                DateTimeFormatter f = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");
                LocalDateTime t = LocalDateTime.of(2024, 7, 4, 18, 5);
                System.out.println(t.format(f));
                System.out.println(LocalDateTime.parse("25/12/2024 08:00", f));
                System.out.println(LocalDate.parse("2024-02-29"));       // ISO format by default
                System.out.println(t.format(DateTimeFormatter.ISO_LOCAL_DATE));
                try {
                    LocalDate.parse("2023-02-29");
                } catch (DateTimeParseException e) {
                    System.out.println("invalid: " + e.getParsedString());
                }
            }
        }
    ''', out='''
        04/07/2024 18:05
        2024-12-25T08:00
        2024-02-29
        2024-07-04
        invalid: 2023-02-29
    ''')
    yield table(
        ["Pattern letter", "Meaning", "Trap"],
        ["`yyyy` / `uuuu`", "year", "`YYYY` is the *week-based* year — wrong around New Year"],
        ["`MM` / `mm`", "month / **minute**", "mixing them up is the #1 formatting bug"],
        ["`dd` / `DD`", "day of month / day of **year**", ""],
        ["`HH` / `hh` + `a`", "24-hour / 12-hour + AM/PM", ""],
    )
    yield good("Store and transmit `Instant` (UTC) or ISO-8601 strings; convert to `ZonedDateTime` only for display. Inject a `Clock` instead of calling `now()` directly so tests are deterministic: `LocalDate.now(clock)`.")
    yield qa("Why is java.time better than java.util.Date?", "Its types are immutable and thread-safe, months are 1-based, each concept has its own type (`LocalDate`, `Instant`, `Duration`, `Period`), time zones are handled explicitly via `ZoneId`, and `DateTimeFormatter` is thread-safe unlike `SimpleDateFormat`.")
    yield qa("LocalDateTime vs ZonedDateTime vs Instant?", "`LocalDateTime` is a wall-clock reading with no zone — it is not a point in time. `ZonedDateTime` adds a zone (with DST rules), making it an exact moment shown in local terms. `Instant` is the exact moment in UTC, ideal for timestamps and storage.")
    yield qa("How do you convert between old and new APIs?", "`date.toInstant()` / `Date.from(instant)`, `calendar.toInstant()`, `new java.sql.Date(...).toLocalDate()` / `java.sql.Date.valueOf(localDate)`, and `Timestamp.valueOf(localDateTime)`.")


@topic(G, "file-io", "File I/O with java.nio.file", "file-text")
def _():
    yield lead("Modern file handling uses `Path` and the static helpers in `Files` — one line for small files, buffered streams for large ones, try-with-resources for everything that must be closed.")
    yield section("The two generations", "history")
    yield table(
        ["", "`java.io` (1996)", "`java.nio.file` (Java 7, NIO.2)"],
        ["Path type", "`File`", "`Path` (`Path.of(\"a\", \"b.txt\")`)"],
        ["Errors", "many methods return `false` silently", "descriptive `IOException`s (`NoSuchFileException`…)"],
        ["Helpers", "streams and readers only", "`Files.readString`, `write`, `lines`, `walk`, `copy`, `move`…"],
        ["Extras", "—", "symbolic links, attributes, `WatchService`, file systems (zip)"],
    )
    yield p("Streams (`InputStream`/`OutputStream`) move **bytes**; readers/writers (`Reader`/`Writer`) move **characters** and need a charset. Always name it (`StandardCharsets.UTF_8`) — the `Files` methods default to UTF-8.")
    yield section("`Path` basics", "route")
    yield snippet("java", r'''
        import java.nio.file.*;

        public class Main {
            public static void main(String[] args) {
                Path p = Path.of("/home/asha/docs/../notes/report.txt");
                System.out.println(p.getFileName());
                System.out.println(p.getParent());
                System.out.println(p.normalize());
                System.out.println(p.getNameCount());
                System.out.println(Path.of("/data").resolve("logs/app.log"));
                System.out.println(Path.of("/a/b").relativize(Path.of("/a/c/d")));
                System.out.println(p.toString().endsWith(".txt"));
            }
        }
    ''', out='''
        report.txt
        /home/asha/docs/../notes
        /home/asha/notes/report.txt
        6
        /data/logs/app.log
        ../c/d
        true
    ''')
    yield section("Small files: one-liners", "file")
    yield snippet("java", r'''
        import java.io.IOException;
        import java.nio.file.*;
        import java.util.*;

        public class Main {
            public static void main(String[] args) throws IOException {
                Path file = Files.createTempFile("notes", ".txt");
                try {
                    Files.writeString(file, "line one\nline two\n");
                    Files.write(file, List.of("line three"), StandardOpenOption.APPEND);

                    System.out.print(Files.readString(file));
                    List<String> lines = Files.readAllLines(file);
                    System.out.println(lines.size() + " lines, last = " + lines.get(lines.size() - 1));
                    System.out.println(Files.exists(file) + " " + Files.size(file) + " bytes");
                } finally {
                    Files.deleteIfExists(file);
                }
                System.out.println("exists after delete: " + Files.exists(file));
            }
        }
    ''', out='''
        line one
        line two
        line three
        3 lines, last = line three
        true 29 bytes
        exists after delete: false
    ''')
    yield warn("`readString` / `readAllLines` load the **whole file** into memory — fine for configs, an `OutOfMemoryError` for a 5 GB log. Stream large files instead.")
    yield section("Large files: stream line by line", "arrows-down")
    yield snippet("java", r'''
        import java.io.*;
        import java.nio.charset.StandardCharsets;
        import java.nio.file.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) throws IOException {
                Path log = Files.createTempFile("app", ".log");
                try {
                    try (BufferedWriter w = Files.newBufferedWriter(log, StandardCharsets.UTF_8)) {
                        for (int i = 1; i <= 5; i++) {
                            w.write((i % 2 == 0 ? "ERROR " : "INFO ") + "event " + i);
                            w.newLine();
                        }
                    }                                           // closed (and flushed) here

                    try (BufferedReader r = Files.newBufferedReader(log)) {
                        String line;
                        while ((line = r.readLine()) != null) {
                            if (line.startsWith("ERROR")) System.out.println(line);
                        }
                    }

                    try (Stream<String> lines = Files.lines(log)) {   // lazy — must be closed
                        System.out.println(lines.filter(l -> l.startsWith("INFO")).count() + " info lines");
                    }
                } finally {
                    Files.delete(log);
                }
            }
        }
    ''', out='''
        ERROR event 2
        ERROR event 4
        3 info lines
    ''')
    yield note("`Files.lines`, `Files.list`, `Files.walk` and `Files.newBufferedReader` hold an open file handle. Wrap them in **try-with-resources**, or you leak file descriptors until the GC gets around to it.", "Close what you open")
    yield section("Directories: create, walk, copy, move", "folders")
    yield snippet("java", r'''
        import java.io.IOException;
        import java.nio.file.*;
        import java.util.*;
        import java.util.stream.*;

        public class Main {
            public static void main(String[] args) throws IOException {
                Path root = Files.createTempDirectory("demo");
                Files.createDirectories(root.resolve("src/main"));
                Files.writeString(root.resolve("src/main/App.java"), "class App {}");
                Files.writeString(root.resolve("README.md"), "# demo");
                Files.copy(root.resolve("README.md"), root.resolve("src/README.copy"));
                Files.move(root.resolve("README.md"), root.resolve("NOTES.md"));

                try (Stream<Path> all = Files.walk(root)) {
                    all.map(p -> root.relativize(p).toString().replace('\\', '/'))
                       .filter(s -> !s.isEmpty())
                       .sorted()
                       .forEach(System.out::println);
                }

                try (Stream<Path> all = Files.walk(root)) {       // delete children before parents
                    for (Path p : all.sorted(Comparator.reverseOrder()).toList()) Files.delete(p);
                }
                System.out.println(Files.exists(root));
            }
        }
    ''', out='''
        NOTES.md
        src
        src/README.copy
        src/main
        src/main/App.java
        false
    ''')
    yield table(
        ["Task", "Call"],
        ["Create dir (and parents)", "`Files.createDirectories(path)`"],
        ["List one level / whole tree", "`Files.list(dir)` / `Files.walk(dir)` / `Files.find(dir, depth, matcher)`"],
        ["Copy / move (overwrite)", "`Files.copy(a, b, StandardCopyOption.REPLACE_EXISTING)` / `Files.move(...)`"],
        ["Delete", "`Files.delete(p)` (throws if missing) / `Files.deleteIfExists(p)`"],
        ["Checks", "`Files.exists`, `isDirectory`, `isRegularFile`, `isReadable`, `size`, `getLastModifiedTime`"],
        ["Binary", "`Files.readAllBytes`, `Files.newInputStream` / `newOutputStream`"],
    )
    yield qa("Why wrap I/O in try-with-resources?", "Files, sockets and streams hold OS resources. try-with-resources calls `close()` automatically in reverse order, even when an exception is thrown, and records exceptions from `close()` as *suppressed* instead of losing the original one. Before Java 7 this took a verbose `finally` block that was easy to get wrong.")
    yield qa("Why use BufferedReader/BufferedWriter?", "Unbuffered streams make a system call for every read/write. Buffering batches data in an in-memory buffer (8 KB by default), cutting system calls dramatically; `BufferedReader` also adds `readLine()`. Remember that a `BufferedWriter` must be flushed/closed or the last chunk never reaches the file.")
    yield qa("Byte streams vs character streams?", "`InputStream`/`OutputStream` handle raw bytes — images, zip files, serialized objects. `Reader`/`Writer` handle text and decode/encode it with a charset. Bridge them with `InputStreamReader` / `OutputStreamWriter`, always passing an explicit charset.")


@topic(G, "serialization", "Serialization Basics", "file-export")
def _():
    yield lead("Java serialization turns an object graph into bytes (and back) — built into the language, but now considered a legacy mechanism with real security risks.")
    yield define("Serialization", "converting an object's state into a byte stream (`ObjectOutputStream.writeObject`) so it can be stored or sent; **deserialization** rebuilds the object from bytes (`ObjectInputStream.readObject`). A class opts in by implementing the *marker interface* `java.io.Serializable`.")
    yield section("A round trip in memory", "refresh")
    yield snippet("java", r'''
        import java.io.*;

        public class Main {
            static class User implements Serializable {
                private static final long serialVersionUID = 1L;
                String name;
                int age;
                transient String password;            // not written
                static String company = "Acme";       // static: belongs to the class, not written

                User(String name, int age, String password) {
                    this.name = name; this.age = age; this.password = password;
                }
            }

            public static void main(String[] args) throws Exception {
                User original = new User("Asha", 30, "s3cret");

                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                try (ObjectOutputStream out = new ObjectOutputStream(bytes)) {
                    out.writeObject(original);
                }

                User copy;
                try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(bytes.toByteArray()))) {
                    copy = (User) in.readObject();
                }
                System.out.println(copy.name + " " + copy.age + " " + copy.password);
                System.out.println(copy == original);
            }
        }
    ''', out='''
        Asha 30 null
        false
    ''')
    yield note("Deserialization does **not** call your class's constructor — fields are filled in directly. `transient` fields come back as their default (`null`, `0`, `false`), and field initialisers don't run for them.", "No constructor")
    yield section("The rules", "list-check")
    yield table(
        ["Rule", "Detail"],
        ["`implements Serializable`", "marker interface — no methods. Otherwise `NotSerializableException`."],
        ["Every field must be serializable", "or `transient`/`static`. One non-serializable field fails the whole graph."],
        ["`transient`", "skip this field (passwords, caches, `Thread`s, connections)."],
        ["`static` fields", "never serialized — they belong to the class."],
        ["Superclass", "if the parent isn't `Serializable`, it needs an accessible no-arg constructor, which runs on deserialization."],
        ["Object graph", "references are followed; shared objects and cycles are written once."],
        ["Custom format", "`private void writeObject(ObjectOutputStream)` / `readObject(ObjectInputStream)`, or `Externalizable`."],
    )
    yield snippet("java", r'''
        import java.io.*;

        public class Main {
            static class Connection {}                     // NOT Serializable

            static class Session implements Serializable {
                private static final long serialVersionUID = 1L;
                String user = "asha";
                Connection conn = new Connection();       // fix: mark it transient
            }

            public static void main(String[] args) throws IOException {
                try (ObjectOutputStream out = new ObjectOutputStream(new ByteArrayOutputStream())) {
                    out.writeObject(new Session());
                } catch (NotSerializableException e) {
                    System.out.println("NotSerializableException: " + e.getMessage());
                }
            }
        }
    ''', out='''
        NotSerializableException: Main$Connection
    ''')
    yield section("`serialVersionUID`", "id")
    yield p("A version number stored in the stream. On deserialization, the JVM compares it with the current class; if they differ you get `InvalidClassException`. If you don't declare one, the compiler computes it from the class's structure — so adding a method can break compatibility with previously saved data.")
    yield snippet("java", r'''
        import java.io.Serializable;

        class Order implements Serializable {
            private static final long serialVersionUID = 1L;   // declare it explicitly
            private final String id;
            private final int qty;

            Order(String id, int qty) { this.id = id; this.qty = qty; }
            String id() { return id; }
            int qty() { return qty; }
        }
    ''')
    yield good("Always declare `private static final long serialVersionUID` in a `Serializable` class; bump it only when a change is truly incompatible. (`javac -Xlint:serial` warns when it's missing.)")
    yield section("Security and modern alternatives", "shield")
    yield warn("**Never deserialize untrusted bytes.** `readObject` can instantiate any serializable class on the classpath and run its hooks — \"gadget chains\" in common libraries have produced remote-code-execution exploits. If you must, install an `ObjectInputFilter` (Java 9+) allow-list.", "Security")
    yield cards(
        ("JSON (Jackson, Gson)", "Human-readable, language-neutral, the default for REST APIs. Works well with records.", "braces"),
        ("Protocol Buffers / Avro", "Compact binary with an explicit schema and versioning rules — service-to-service and event streams.", "binary"),
        ("Records + serialization", "Serializable records are deserialized through their canonical constructor, so validation still runs — safer than classes.", "file-certificate"),
        ("Plain Java serialization", "OK for short-lived in-JVM caches or legacy protocols (RMI). Avoid for long-term storage or network input.", "archive"),
    )
    yield qa("What is the purpose of serialVersionUID?", "It versions the serialized form. When bytes are read back, the stored UID must equal the class's UID or `InvalidClassException` is thrown. Declaring it explicitly keeps compatible changes (adding a field) readable; relying on the computed default makes almost any change incompatible, and the value can differ between compilers.")
    yield qa("What does transient do? Are static fields serialized?", "`transient` excludes an instance field from serialization; after deserialization it holds its default value. Static fields are never serialized because they belong to the class, not the object — after deserialization they show whatever the class currently holds.")
    yield qa("Serializable vs Externalizable?", "`Serializable` is a marker; the JVM writes all non-transient fields automatically (customisable via `writeObject`/`readObject`). `Externalizable` makes you implement `writeExternal`/`readExternal` yourself — full control and potentially faster, but you must write every field and the class needs a public no-arg constructor.")
    yield qa("Why is Java serialization considered dangerous?", "Deserialization builds objects without constructors and can trigger methods (`readObject`, `readResolve`, `hashCode` in hash-based collections) on any class on the classpath. Attackers craft byte streams that chain these into arbitrary code execution. Mitigations: don't accept serialized data from untrusted sources, use `ObjectInputFilter`, prefer JSON/protobuf.")
