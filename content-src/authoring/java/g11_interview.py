from kit import *

G = "Design, Modern Java & Interview Prep"


@topic(G, "design-patterns-creational", "Design Patterns: Singleton, Builder & Factory", "building-factory-2")
def _():
    yield lead("Creational patterns control *how objects get made*: exactly one (Singleton), step by step (Builder), or without the caller naming the concrete class (Factory).")
    yield section("Singleton", "square-rounded-number-1")
    yield define("Singleton", "a class with exactly one instance and a global access point to it. Private constructor + a static way to get the instance.")
    yield table(
        ["Variant", "Lazy?", "Thread-safe?", "Notes"],
        ["Eager `static final` field", "No — created at class init", "Yes (class init is thread-safe)", "Simplest; fine when creation is cheap"],
        ["`synchronized getInstance()`", "Yes", "Yes", "Lock on every call — slow"],
        ["Double-checked locking", "Yes", "Yes **only with `volatile`**", "Verbose; easy to get wrong"],
        ["Holder idiom (static nested class)", "Yes", "Yes", "JVM class-loading guarantees; no locks"],
        ["`enum` with one constant", "At enum init", "Yes", "**Recommended** (Effective Java): also safe against reflection and serialization"],
    )
    yield snippet("java", r'''
        public class Main {
            // 1. Eager
            static final class Eager {
                private static final Eager INSTANCE = new Eager();
                private Eager() {}
                static Eager getInstance() { return INSTANCE; }
            }

            // 2. Double-checked locking — volatile prevents seeing a half-constructed object
            static final class Dcl {
                private static volatile Dcl instance;
                private Dcl() {}
                static Dcl getInstance() {
                    Dcl local = instance;
                    if (local == null) {                       // 1st check, no lock
                        synchronized (Dcl.class) {
                            local = instance;
                            if (local == null) {               // 2nd check, with lock
                                instance = local = new Dcl();
                            }
                        }
                    }
                    return local;
                }
            }

            // 3. Holder idiom — Holder is initialised on first getInstance() call
            static final class Lazy {
                private Lazy() { System.out.println("Lazy created"); }
                private static final class Holder { static final Lazy INSTANCE = new Lazy(); }
                static Lazy getInstance() { return Holder.INSTANCE; }
            }

            // 4. Enum
            enum Config {
                INSTANCE;
                private int timeout = 30;
                int timeout() { return timeout; }
            }

            public static void main(String[] args) {
                System.out.println(Eager.getInstance() == Eager.getInstance());
                System.out.println(Dcl.getInstance() == Dcl.getInstance());
                System.out.println("before first use");
                System.out.println(Lazy.getInstance() == Lazy.getInstance());
                System.out.println(Config.INSTANCE.timeout());
            }
        }
    ''', out="""
        true
        true
        before first use
        Lazy created
        true
        30
    """)
    yield warn("Without `volatile`, double-checked locking is broken: the write of the reference can be reordered before the constructor's field writes, so another thread may see a non-null but not fully initialised object.", "Double-checked locking")
    yield section("Breaking a singleton — and the enum defence", "hammer")
    yield snippet("java", r'''
        import java.lang.reflect.Constructor;

        public class Main {
            static final class Classic {
                static final Classic INSTANCE = new Classic();
                private Classic() {}
            }

            enum Single { INSTANCE }

            public static void main(String[] args) throws Exception {
                Constructor<Classic> c = Classic.class.getDeclaredConstructor();
                c.setAccessible(true);                       // bypass `private`
                Classic second = c.newInstance();
                System.out.println("classic still single? " + (second == Classic.INSTANCE));

                Constructor<Single> e = Single.class.getDeclaredConstructor(String.class, int.class);
                e.setAccessible(true);
                try {
                    e.newInstance("INSTANCE", 0);
                } catch (IllegalArgumentException ex) {
                    System.out.println(ex.getMessage());
                }
            }
        }
    ''', out="""
        classic still single? false
        Cannot reflectively create enum objects
    """)
    yield snippet("java", r'''
        import java.io.*;

        public class Main {
            static final class Settings implements Serializable {
                private static final long serialVersionUID = 1L;
                static final Settings INSTANCE = new Settings();
                private Settings() {}

                private Object readResolve() {       // deserialization returns this instead
                    return INSTANCE;
                }
            }

            public static void main(String[] args) throws Exception {
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                try (ObjectOutputStream out = new ObjectOutputStream(bytes)) {
                    out.writeObject(Settings.INSTANCE);
                }
                try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(bytes.toByteArray()))) {
                    Object copy = in.readObject();
                    System.out.println(copy == Settings.INSTANCE);   // false without readResolve
                }
            }
        }
    ''', out="true")
    yield note("Singletons are global state: they hide dependencies and make unit tests hard. In application code prefer *one instance created at startup and passed in* (dependency injection — what Spring beans are by default).")
    yield section("Builder", "hammer")
    yield p("For classes with many parameters, especially optional ones. Replaces *telescoping constructors* and avoids the half-built objects of the JavaBeans setter style.")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static final class Pizza {
                private final String size;              // required
                private final boolean extraCheese;      // optional
                private final List<String> toppings;    // optional

                private Pizza(Builder b) {
                    this.size = b.size;
                    this.extraCheese = b.extraCheese;
                    this.toppings = List.copyOf(b.toppings);
                }

                static Builder builder(String size) { return new Builder(size); }

                @Override
                public String toString() {
                    return size + " pizza, cheese=" + extraCheese + ", toppings=" + toppings;
                }

                static final class Builder {
                    private final String size;
                    private boolean extraCheese;
                    private final List<String> toppings = new ArrayList<>();

                    private Builder(String size) { this.size = size; }

                    Builder extraCheese() { this.extraCheese = true; return this; }
                    Builder topping(String t) { toppings.add(t); return this; }

                    Pizza build() {
                        if (toppings.size() > 5) throw new IllegalStateException("too many toppings");
                        return new Pizza(this);
                    }
                }
            }

            public static void main(String[] args) {
                Pizza p = Pizza.builder("large")
                        .topping("olives")
                        .topping("basil")
                        .extraCheese()
                        .build();
                System.out.println(p);
            }
        }
    ''', out="large pizza, cheese=true, toppings=[olives, basil]")
    yield chips("`StringBuilder`", "`HttpRequest.newBuilder()`", "`Stream.builder()`", "`Locale.Builder`", "Lombok `@Builder`")
    yield section("Factories", "building-factory")
    yield cards(
        ("Static factory method", "A `static` method that returns an instance: `List.of`, `Integer.valueOf`, `Optional.empty`. Has a *name*, can cache (`valueOf`), can return a subtype.", "function"),
        ("Simple factory", "One method picks the concrete class from a parameter — callers depend only on the interface.", "switch"),
        ("Factory Method (GoF)", "A superclass defines an abstract `createX()` and subclasses decide which class to instantiate.", "hierarchy"),
        ("Abstract Factory", "An interface for creating *families* of related objects (e.g. a UI kit: `createButton`, `createCheckbox`).", "stack-2"),
    )
    yield snippet("java", r'''
        public class Main {
            sealed interface Shape permits Circle, Square {
                double area();

                static Shape of(String kind, double size) {        // simple / static factory
                    return switch (kind) {
                        case "circle" -> new Circle(size);
                        case "square" -> new Square(size);
                        default -> throw new IllegalArgumentException("unknown shape: " + kind);
                    };
                }
            }

            record Circle(double r) implements Shape {
                public double area() { return Math.PI * r * r; }
            }

            record Square(double side) implements Shape {
                public double area() { return side * side; }
            }

            public static void main(String[] args) {
                Shape s = Shape.of("square", 3);
                System.out.println(s + " area=" + s.area());
                System.out.printf("%.2f%n", Shape.of("circle", 1).area());
                System.out.println(Integer.valueOf(100) == Integer.valueOf(100));   // valueOf caches
            }
        }
    ''', out="""
        Square[side=3.0] area=9.0
        3.14
        true
    """)
    yield qa("Which singleton implementation would you use and why?",
             "An `enum` with a single constant: it is thread-safe by class initialisation, serialization returns the same constant automatically, and reflection cannot create a second instance. If laziness matters and the class must extend something, use the holder idiom.")
    yield qa("Why must the instance field be volatile in double-checked locking?",
             "`instance = new X()` is allocate → initialise → publish; without `volatile` the publish can be reordered before initialisation, so a thread that skips the lock could see a non-null reference to an object whose fields are still defaults. `volatile` adds the happens-before edge that forbids this.")
    yield qa("When would you choose a builder over constructors?",
             "When there are more than a handful of parameters, several are optional, or several have the same type (easy to swap by mistake). The builder gives named, readable calls and still produces an immutable object validated in one place (`build()`).")


@topic(G, "design-patterns-behavioral", "Design Patterns: Strategy, Observer & More", "topology-star-3")
def _():
    yield lead("Behavioural and structural patterns in modern Java — most of them are a lambda or a small interface away.")
    yield section("Strategy", "route")
    yield define("Strategy", "define a family of interchangeable algorithms behind one interface and choose one at run time. With functional interfaces, each strategy is just a lambda.")
    yield snippet("java", r'''
        import java.util.Map;
        import java.util.function.DoubleUnaryOperator;

        public class Main {
            static final Map<String, DoubleUnaryOperator> DISCOUNTS = Map.of(
                    "none", price -> price,
                    "festive", price -> price * 0.8,
                    "flat50", price -> Math.max(0, price - 50));

            static double checkout(double price, String code) {
                return DISCOUNTS.getOrDefault(code, DISCOUNTS.get("none")).applyAsDouble(price);
            }

            public static void main(String[] args) {
                System.out.println(checkout(200, "festive"));
                System.out.println(checkout(200, "flat50"));
                System.out.println(checkout(200, "bogus"));
            }
        }
    ''', out="""
        160.0
        150.0
        200.0
    """)
    yield p("`Comparator` is the JDK's best-known strategy: `list.sort(Comparator.comparing(Person::age))` plugs a comparison algorithm into a sort.")
    yield section("Observer", "eye")
    yield define("Observer", "a subject keeps a list of listeners and notifies them of events; listeners don't know about each other. The basis of event buses, GUI listeners and reactive streams.")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.function.Consumer;

        public class Main {
            static final class StockTicker {
                private final List<Consumer<Double>> listeners = new ArrayList<>();

                Runnable subscribe(Consumer<Double> l) {
                    listeners.add(l);
                    return () -> listeners.remove(l);          // handle to unsubscribe
                }

                void publish(double price) {
                    listeners.forEach(l -> l.accept(price));
                }
            }

            public static void main(String[] args) {
                StockTicker ticker = new StockTicker();
                ticker.subscribe(p -> System.out.println("display: " + p));
                Runnable cancel = ticker.subscribe(p -> {
                    if (p > 100) System.out.println("alert: above 100");
                });

                ticker.publish(99.5);
                ticker.publish(101.0);
                cancel.run();                                  // stop the alerts
                ticker.publish(120.0);
            }
        }
    ''', out="""
        display: 99.5
        display: 101.0
        alert: above 100
        display: 120.0
    """)
    yield warn("Forgotten subscriptions are a classic memory leak — always give listeners a way to unsubscribe. `java.util.Observable` is deprecated (Java 9); use your own listener list, `PropertyChangeSupport` or `java.util.concurrent.Flow`.")
    yield section("Decorator", "layers-subtract")
    yield p("Wrap an object in another object with the *same interface* to add behaviour. `java.io` is built this way: each stream adds one feature (buffering, decoding, line reading).")
    yield snippet("java", r'''
        import java.io.BufferedReader;
        import java.io.IOException;
        import java.io.StringReader;

        public class Main {
            interface Coffee { double cost(); String describe(); }

            record Espresso() implements Coffee {
                public double cost() { return 2.0; }
                public String describe() { return "espresso"; }
            }

            record WithMilk(Coffee inner) implements Coffee {
                public double cost() { return inner.cost() + 0.5; }
                public String describe() { return inner.describe() + " + milk"; }
            }

            record WithSyrup(Coffee inner) implements Coffee {
                public double cost() { return inner.cost() + 0.75; }
                public String describe() { return inner.describe() + " + syrup"; }
            }

            public static void main(String[] args) throws IOException {
                Coffee order = new WithSyrup(new WithMilk(new Espresso()));
                System.out.println(order.describe() + " = " + order.cost());

                // the JDK version: a Reader decorated with buffering and readLine()
                try (BufferedReader r = new BufferedReader(new StringReader("line 1\nline 2"))) {
                    System.out.println(r.readLine());
                }
            }
        }
    ''', out="""
        espresso + milk + syrup = 3.25
        line 1
    """)
    yield section("Template method", "template")
    yield p("An abstract class fixes the *skeleton* of an algorithm in a `final` method and lets subclasses fill in the steps.")
    yield snippet("java", r'''
        public class Main {
            static abstract class Report {
                final String render() {                      // the template — not overridable
                    return header() + "\n" + body() + "\n-- end --";
                }
                String header() { return "REPORT"; }         // hook with a default
                abstract String body();                      // step subclasses must supply
            }

            static final class SalesReport extends Report {
                @Override String body() { return "sales: 42 units"; }
            }

            public static void main(String[] args) {
                System.out.println(new SalesReport().render());
            }
        }
    ''', out="""
        REPORT
        sales: 42 units
        -- end --
    """)
    yield section("Adapter", "plug-connected")
    yield p("Convert one interface into another that a client expects. `Arrays.asList` adapts an array to `List`; `InputStreamReader` adapts a byte stream to a character `Reader`.")
    yield snippet("java", r'''
        import java.util.function.Supplier;

        public class Main {
            static final class LegacyThermometer {                  // can't change this class
                double readFahrenheit() { return 98.6; }
            }

            interface CelsiusSensor { double celsius(); }

            static CelsiusSensor adapt(LegacyThermometer t) {     // the adapter
                return () -> (t.readFahrenheit() - 32) * 5 / 9;
            }

            public static void main(String[] args) {
                CelsiusSensor s = adapt(new LegacyThermometer());
                Supplier<String> fmt = () -> String.format("%.1f C", s.celsius());
                System.out.println(fmt.get());
            }
        }
    ''', out="37.0 C")
    yield section("Where the JDK uses them", "books")
    yield table(
        ["Pattern", "Kind", "In the JDK"],
        ["Strategy", "Behavioural", "`Comparator`, `ThreadPoolExecutor`'s `RejectedExecutionHandler`"],
        ["Observer", "Behavioural", "`PropertyChangeListener`, Swing listeners, `Flow.Subscriber`"],
        ["Iterator", "Behavioural", "`Iterator` / `Iterable` behind every for-each loop"],
        ["Template method", "Behavioural", "`AbstractList` (`get` + `size` → everything else), `InputStream.read(byte[])`"],
        ["Command", "Behavioural", "`Runnable`, `Callable` submitted to executors"],
        ["Decorator", "Structural", "`BufferedInputStream`, `Collections.unmodifiableList`, `synchronizedMap`"],
        ["Adapter", "Structural", "`Arrays.asList`, `InputStreamReader`, `OutputStreamWriter`"],
        ["Proxy", "Structural", "`java.lang.reflect.Proxy` (Spring AOP, mocks)"],
        ["Factory / static factory", "Creational", "`List.of`, `Calendar.getInstance`, `NumberFormat.getInstance`"],
        ["Builder", "Creational", "`StringBuilder`, `HttpClient.newBuilder()`"],
        ["Singleton", "Creational", "`Runtime.getRuntime()`"],
    )
    yield qa("Strategy vs template method?",
             "Both vary part of an algorithm. Template method uses *inheritance* — subclasses override steps of a fixed skeleton. Strategy uses *composition* — the varying algorithm is an object (often a lambda) passed in, so it can change at run time and needs no subclass.")
    yield qa("Decorator vs inheritance for adding behaviour?",
             "Inheritance fixes the combination at compile time and explodes into subclasses for every combination (MilkSyrupCoffee…). Decorators compose at run time: wrap in any order and any number, each class adding one responsibility.")


@topic(G, "modern-java", "Modern Java: 8 → 21 Feature Tour", "rocket")
def _():
    yield lead("What changed from Java 8 to Java 21 — the features interviewers expect you to know and modern codebases actually use.")
    yield note("Long-term-support releases: **8, 11, 17, 21** (and 25). Since Java 10 a feature release ships every six months; preview features need `--enable-preview`.", "LTS")
    yield section("Feature timeline", "timeline")
    yield table(
        ["Version", "Headline features"],
        ["**8** (2014, LTS)", "Lambdas, method references, Streams, `Optional`, `java.time`, default & static interface methods, `CompletableFuture`"],
        ["9", "Module system (JPMS), `List.of` / `Set.of` / `Map.of`, JShell, private interface methods, `Stream.takeWhile`, compact strings"],
        ["10", "`var` for local variables, `List.copyOf`, `Collectors.toUnmodifiableList`"],
        ["**11** (LTS)", "`String.isBlank/strip/repeat/lines`, `Files.readString/writeString`, standard `HttpClient`, single-file launch `java App.java`, `var` in lambda params"],
        ["12–13", "`Collectors.teeing`, `String.indent/transform`; switch expressions & text blocks in preview"],
        ["14", "**Switch expressions** (`->`, `yield`), helpful `NullPointerException` messages"],
        ["15", "**Text blocks** `\"\"\"`, `String.formatted`, ZGC production-ready"],
        ["16", "**Records**, **pattern matching for `instanceof`**, `Stream.toList()`"],
        ["**17** (LTS)", "**Sealed classes**, strong encapsulation of JDK internals, `RandomGenerator`"],
        ["18–20", "UTF-8 by default, simple web server `jwebserver`; previews of virtual threads, record patterns"],
        ["**21** (LTS)", "**Virtual threads**, **pattern matching for `switch`**, **record patterns**, **sequenced collections** (`getFirst`, `reversed`), generational ZGC"],
    )
    yield section("Many features, one program", "code")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            sealed interface Shape permits Circle, Rect {}             // 17: sealed
            record Circle(double r) implements Shape {}                 // 16: records
            record Rect(double w, double h) implements Shape {}

            static String describe(Object o) {
                return switch (o) {                                     // 21: pattern switch
                    case Circle(double r) when r > 10 -> "big circle";  // 21: record pattern + guard
                    case Circle c -> "circle r=" + c.r();
                    case Rect(double w, double h) -> "rect " + (w * h);
                    case String s -> "text of length " + s.length();
                    case null -> "null!";
                    default -> "something else";
                };
            }

            public static void main(String[] args) {
                var shapes = List.of(new Circle(2), new Rect(3, 4), new Circle(20));   // 10: var, 9: List.of
                shapes.forEach(s -> System.out.println(describe(s)));                 // 8: lambdas
                System.out.println(describe("hi") + ", " + describe(null));

                Object o = shapes.get(1);
                if (o instanceof Rect r && r.w() < r.h()) {                             // 16: instanceof pattern
                    System.out.println("tall " + r);
                }

                String json = """
                        {"name": "%s", "ok": %b}""".formatted("java", true);          // 15: text block + formatted
                System.out.println(json);

                System.out.println("  hi  ".strip() + "|" + "ab".repeat(3) + "|" + "   ".isBlank());   // 11

                var names = new ArrayList<>(List.of("a", "b", "c"));
                System.out.println(names.getFirst() + names.getLast() + " " + names.reversed());    // 21: sequenced

                List<String> kinds = shapes.stream().map(s -> s.getClass().getSimpleName()).toList();   // 16: toList()
                System.out.println(kinds);
            }
        }
    ''', out="""
        circle r=2.0
        rect 12.0
        big circle
        text of length 2, null!
        tall Rect[w=3.0, h=4.0]
        {"name": "java", "ok": true}
        hi|ababab|true
        ac [c, b, a]
        [Circle, Rect, Circle]
    """)
    yield section("Helpful NullPointerExceptions (14+)", "bug")
    yield snippet("java", r'''
        public class Main {
            record Address(String city) {}
            record User(Address address) {}

            public static void main(String[] args) {
                User u = new User(null);
                try {
                    System.out.println(u.address().city().length());
                } catch (NullPointerException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out='Cannot invoke "Main$Address.city()" because the return value of "Main$User.address()" is null')
    yield section("Virtual threads (21)", "brand-threads")
    yield snippet("java", r'''
        import java.util.concurrent.Executors;
        import java.util.concurrent.atomic.AtomicInteger;

        public class Main {
            public static void main(String[] args) {
                AtomicInteger done = new AtomicInteger();
                try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                    for (int i = 0; i < 10_000; i++) {
                        executor.submit(() -> {
                            Thread.sleep(10);                 // blocking is cheap on a virtual thread
                            return done.incrementAndGet();
                        });
                    }
                }                                             // close() waits for all tasks
                System.out.println("completed: " + done.get());
            }
        }
    ''', out="completed: 10000")
    yield qa("Which Java version would you pick for a new project and why?",
             "The latest LTS (21, or 25 if the stack supports it): records, sealed types, pattern matching and virtual threads are all final, and it gets long-term security updates. Frameworks like Spring Boot 3 require at least 17.")
    yield qa("What are the headline features of Java 8?",
             "Lambda expressions and functional interfaces, method references, the Streams API, `Optional`, the `java.time` API, default and static methods in interfaces, and `CompletableFuture`.")
    yield qa("What is pattern matching in Java 21?",
             "`switch` can test the *type* of the selector (`case String s ->`), deconstruct records (`case Point(int x, int y) ->`), add guards (`when x > 0`) and handle `case null`. With sealed hierarchies, the compiler checks exhaustiveness so no `default` is needed.")


@topic(G, "best-practices", "Java Best Practices", "checklist")
def _():
    yield lead("The habits that separate working Java from *good* Java — mostly from Joshua Bloch's *Effective Java*.")
    yield section("Naming conventions", "abc")
    yield table(
        ["Element", "Convention", "Example"],
        ["Class, interface, record, enum", "`PascalCase`, nouns", "`OrderService`, `Comparable`"],
        ["Method", "`camelCase`, verbs", "`calculateTotal()`, `isEmpty()`"],
        ["Variable / parameter", "`camelCase`", "`itemCount`"],
        ["Constant (`static final`)", "`UPPER_SNAKE_CASE`", "`MAX_RETRIES`"],
        ["Package", "lowercase, reversed domain", "`com.example.billing`"],
        ["Type parameter", "single capital letter", "`T`, `E`, `K`, `V`, `R`"],
        ["Enum constant", "`UPPER_SNAKE_CASE`", "`Status.IN_PROGRESS`"],
    )
    yield section("Effective Java highlights", "star")
    yield cards(
        ("Static factories", "Consider `of`/`valueOf`/`from` methods instead of constructors — named, cacheable, can return subtypes.", "function"),
        ("Builders", "Use a builder when a constructor would have many (optional) parameters.", "hammer"),
        ("Minimise mutability", "`final` fields, no setters, defensive copies (`List.copyOf`). Records make this the default.", "lock"),
        ("Composition over inheritance", "Extend only classes designed for it; otherwise wrap and forward.", "puzzle"),
        ("Program to interfaces", "Declare `List<String> names = new ArrayList<>()` — easy to switch implementation.", "plug"),
        ("`equals` ⇒ `hashCode`", "Always override both, or hash-based collections break.", "equal"),
        ("Empty, not `null`", "Return `List.of()` / `Optional.empty()` rather than `null`.", "circle-dashed"),
        ("Enums, not int constants", "Type-safe, printable, switchable, can carry data and behaviour.", "list"),
        ("`try-with-resources`", "Never close resources by hand in `finally`.", "file"),
        ("Don't ignore exceptions", "An empty `catch` hides bugs. Handle, wrap with a cause, or rethrow.", "alert-circle"),
    )
    yield section("Composition over inheritance — the classic bug", "puzzle")
    yield p("Subclassing `HashSet` to count insertions double-counts, because `HashSet.addAll` internally calls the overridden `add`. You depended on an implementation detail of the superclass.")
    yield snippet("java", r'''
        import java.util.Collection;
        import java.util.HashSet;
        import java.util.List;

        public class Main {
            static class CountingSet<E> extends HashSet<E> {
                int added = 0;

                @Override public boolean add(E e) { added++; return super.add(e); }

                @Override public boolean addAll(Collection<? extends E> c) {
                    added += c.size();
                    return super.addAll(c);        // calls our add() again for every element!
                }
            }

            public static void main(String[] args) {
                CountingSet<String> s = new CountingSet<>();
                s.addAll(List.of("a", "b", "c"));
                System.out.println(s.added);       // expected 3
            }
        }
    ''', out="6")
    yield good("Wrap instead: a `ForwardingSet` that *holds* a `Set` and delegates to it — its behaviour can't be broken by changes in `HashSet`'s internals.")
    yield section("equals without hashCode", "equal-not")
    yield snippet("java", r'''
        import java.util.HashSet;
        import java.util.Objects;
        import java.util.Set;

        public class Main {
            static final class Bad {
                final int id;
                Bad(int id) { this.id = id; }
                @Override public boolean equals(Object o) { return o instanceof Bad b && b.id == id; }
                // hashCode NOT overridden → identity hash codes differ
            }

            static final class Good {
                final int id;
                Good(int id) { this.id = id; }
                @Override public boolean equals(Object o) { return o instanceof Good g && g.id == id; }
                @Override public int hashCode() { return Objects.hash(id); }
            }

            public static void main(String[] args) {
                Set<Bad> bad = new HashSet<>();
                bad.add(new Bad(1));
                System.out.println(bad.contains(new Bad(1)));

                Set<Good> good = new HashSet<>();
                good.add(new Good(1));
                System.out.println(good.contains(new Good(1)));
            }
        }
    ''', out="""
        false
        true
    """)
    yield section("Return empty, not null", "circle-dashed")
    yield snippet("java", r'''
        import java.util.List;
        import java.util.Map;
        import java.util.Optional;

        public class Main {
            static final Map<String, List<String>> ORDERS = Map.of("asha", List.of("book", "pen"));

            static List<String> ordersOf(String user) {
                return ORDERS.getOrDefault(user, List.of());     // never null
            }

            static Optional<String> firstOrder(String user) {
                return ordersOf(user).stream().findFirst();
            }

            public static void main(String[] args) {
                for (String item : ordersOf("ravi")) System.out.println(item);   // simply loops 0 times
                System.out.println(ordersOf("ravi").size());
                System.out.println(firstOrder("asha").orElse("none"));
                System.out.println(firstOrder("ravi").orElse("none"));
            }
        }
    ''', out="""
        0
        book
        none
    """)
    yield section("Code hygiene checklist", "list-check")
    yield dodont(
        "Use `final` for fields that never change; keep variables in the narrowest scope; validate arguments early (`Objects.requireNonNull`); prefer `for-each` and streams where clearer; log with a logger (SLF4J), not `System.out`; write unit tests (JUnit 5).",
        "Raw types (`List` instead of `List<String>`); `catch (Exception e) {}`; `==` on strings; public mutable fields; huge god classes; premature optimisation; returning `null` for \"no results\"; exposing internal mutable collections.",
    )
    yield table(
        ["Instead of…", "Prefer…"],
        ["`new Integer(5)` (deprecated)", "`Integer.valueOf(5)` or autoboxing"],
        ["`Vector`, `Hashtable`, `Stack`", "`ArrayList`, `HashMap` / `ConcurrentHashMap`, `ArrayDeque`"],
        ["`Date`, `Calendar`, `SimpleDateFormat`", "`LocalDate`, `Instant`, `DateTimeFormatter`"],
        ["`int` status codes", "an `enum`"],
        ["Manual `close()` in `finally`", "`try-with-resources`"],
        ["`if (x != null) x.foo()` chains", "`Optional` for return values, or `Objects.requireNonNullElse`"],
    )
    yield qa("Why prefer composition over inheritance?",
             "Inheritance breaks encapsulation: the subclass depends on how the superclass implements its methods (the `addAll` → `add` double count), and superclass changes can silently break it. Composition depends only on the public interface, can be swapped at run time, and doesn't inherit an API you don't want.")
    yield qa("Why return an empty collection instead of null?",
             "Callers can iterate, stream or call `size()` without a null check, so there are no `NullPointerException`s and no duplicated `if (list != null)` code. Immutable empties like `List.of()` cost nothing to create.")


@topic(G, "competitive-io", "Competitive Programming I/O in Java", "trophy")
def _():
    yield lead("Java is fast enough for contests *if* you avoid slow input, per-line output and a few well-known traps.")
    yield section("Scanner is slow", "hourglass")
    yield p("`Scanner` uses regular expressions for every token — fine for 10³ numbers, too slow for 10⁶. Read lines with `BufferedReader` and split them with `StringTokenizer`; buffer the output with `PrintWriter`.")
    yield table(
        ["Tool", "Speed", "Use"],
        ["`Scanner(System.in)`", "Slow (regex per token)", "Small inputs, quick scripts"],
        ["`BufferedReader` + `StringTokenizer`", "Fast", "The standard contest template"],
        ["`DataInputStream` custom byte reader", "Fastest", "Huge inputs (10⁷ numbers)"],
        ["`System.out.println` in a loop", "Slow (flushes / locks)", "Avoid for many lines"],
        ["`PrintWriter` / `StringBuilder`", "Fast", "Build output, flush once"],
    )
    yield section("The standard template", "template")
    yield snippet("java", r'''
        import java.io.*;
        import java.util.*;

        public class Main {
            public static void main(String[] args) throws IOException {
                BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
                PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));

                int t = Integer.parseInt(br.readLine().trim());          // number of test cases
                while (t-- > 0) {
                    int n = Integer.parseInt(br.readLine().trim());
                    StringTokenizer st = new StringTokenizer(br.readLine());
                    long sum = 0;                                        // long: sums overflow int
                    int max = Integer.MIN_VALUE;
                    for (int i = 0; i < n; i++) {
                        int x = Integer.parseInt(st.nextToken());
                        sum += x;
                        max = Math.max(max, x);
                    }
                    out.println(sum + " " + max);
                }
                out.flush();                                             // forget this → no output!
            }
        }
    ''', out="""
        6 3
        3000000000 1000000000
    """, stdin="2\n3\n1 2 3\n3\n1000000000 1000000000 1000000000\n")
    yield output('''
        2
        3
        1 2 3
        3
        1000000000 1000000000 1000000000
    ''', "Input (stdin)")
    yield section("A reusable FastReader", "bolt")
    yield snippet("java", r'''
        import java.io.*;
        import java.util.*;

        public class Main {
            static final class FastReader {
                private final BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
                private StringTokenizer st;

                String next() throws IOException {
                    while (st == null || !st.hasMoreTokens()) {
                        st = new StringTokenizer(br.readLine());   // tokens may span lines
                    }
                    return st.nextToken();
                }
                int nextInt() throws IOException { return Integer.parseInt(next()); }
                long nextLong() throws IOException { return Long.parseLong(next()); }
            }

            public static void main(String[] args) throws IOException {
                FastReader in = new FastReader();
                int n = in.nextInt();
                int[] a = new int[n];
                for (int i = 0; i < n; i++) a[i] = in.nextInt();

                StringBuilder sb = new StringBuilder();
                for (int i = n - 1; i >= 0; i--) sb.append(a[i]).append(i > 0 ? ' ' : '\n');
                System.out.print(sb);                                   // one write
            }
        }
    ''', out="5 4 3 2 1", stdin="5\n1 2\n3 4 5\n")
    yield section("Overflow: when to use long", "alert-triangle")
    yield snippet("java", r'''
        public class Main {
            static final int MOD = 1_000_000_007;

            static long power(long base, long exp, long mod) {      // fast exponentiation, O(log exp)
                long result = 1;
                base %= mod;
                while (exp > 0) {
                    if ((exp & 1) == 1) result = result * base % mod;
                    base = base * base % mod;
                    exp >>= 1;
                }
                return result;
            }

            public static void main(String[] args) {
                int a = 1_000_000;
                System.out.println(a * a);              // int overflow, silently wraps
                System.out.println((long) a * a);       // widen BEFORE multiplying
                System.out.println((long) (a * a));     // too late: already overflowed
                System.out.println(power(2, 1_000_000_000L, MOD));
                System.out.println(Math.floorMod(-7, 3) + " " + (-7 % 3));   // % keeps the sign
            }
        }
    ''', out="""
        -727379968
        1000000000000
        -727379968
        140625001
        2 -1
    """)
    yield section("The Arrays.sort(int[]) trap", "sort-ascending")
    yield warn("`Arrays.sort(int[])` uses dual-pivot quicksort: O(n log n) on average but **O(n²) on adversarial input**, and contest “anti-Java” tests exploit that. `Arrays.sort(Object[])` (e.g. `Integer[]`) uses TimSort, which is always O(n log n).", "Hackable sort")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static void safeSort(int[] a) {
                Random rnd = new Random(42);
                for (int i = a.length - 1; i > 0; i--) {       // shuffle first → no adversarial order
                    int j = rnd.nextInt(i + 1);
                    int tmp = a[i]; a[i] = a[j]; a[j] = tmp;
                }
                Arrays.sort(a);
            }

            public static void main(String[] args) {
                int[] a = {5, 1, 4, 2, 3};
                safeSort(a);
                System.out.println(Arrays.toString(a));

                Integer[] boxed = {5, 1, 4, 2, 3};             // alternative: object sort = TimSort
                Arrays.sort(boxed, Collections.reverseOrder());
                System.out.println(Arrays.toString(boxed));
            }
        }
    ''', out="""
        [1, 2, 3, 4, 5]
        [5, 4, 3, 2, 1]
    """)
    yield section("Contest checklist", "checklist")
    yield ul(
        "Class name: most judges require `public class Main` (Codeforces accepts any; check the rules).",
        "Use `long` for sums, products and anything that can exceed ~2.1 × 10⁹.",
        "Recursion depth > ~10⁴ may overflow the default stack — iterate, or run the solver in `new Thread(null, task, \"\", 1 << 26)`.",
        "`ArrayDeque` over `Stack`/`LinkedList`; `int[]` over `List<Integer>` in hot loops (boxing is slow).",
        "Compare boxed values with `equals` — `Integer == Integer` fails above 127.",
        "Flush `PrintWriter` at the end (or use `try-with-resources`).",
    )
    yield qa("Why is BufferedReader faster than Scanner?",
             "`BufferedReader` reads large chunks and hands back raw lines; `StringTokenizer` splits on whitespace with a simple loop. `Scanner` has a smaller buffer and parses every token with regular expressions and locale-aware number parsing, which is several times slower on large inputs.")


@topic(G, "java-dsa-cheatsheet", "Java for DSA: Collections Cheat Sheet", "binary-tree")
def _():
    yield lead("The complexities, idioms and templates you reach for in every coding interview, in Java.")
    yield section("Complexity cheat sheet", "clock")
    yield table(
        ["Structure", "Access", "Search", "Insert", "Delete", "Notes"],
        ["`int[]` / array", "O(1)", "O(n)", "—", "—", "Fixed size"],
        ["`ArrayList`", "O(1)", "O(n)", "O(1) amortised at end", "O(n) (shift)", "Default list"],
        ["`LinkedList`", "O(n)", "O(n)", "O(1) at ends", "O(1) at ends", "Rarely the best choice"],
        ["`ArrayDeque`", "—", "O(n)", "O(1) both ends", "O(1) both ends", "Stack **and** queue"],
        ["`HashMap` / `HashSet`", "—", "O(1) avg", "O(1) avg", "O(1) avg", "Worst case O(log n) with treeified bins"],
        ["`TreeMap` / `TreeSet`", "—", "O(log n)", "O(log n)", "O(log n)", "Sorted; floor/ceiling queries"],
        ["`PriorityQueue`", "peek O(1)", "O(n)", "O(log n)", "poll O(log n)", "Binary min-heap"],
    )
    yield section("Maps: counting and grouping", "hash")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Map<Character, Integer> freq = new TreeMap<>();          // sorted keys for display
                for (char c : "banana".toCharArray()) {
                    freq.merge(c, 1, Integer::sum);                       // add 1 or start at 1
                }
                System.out.println(freq);

                int[] counts = new int[26];                                // faster for lowercase letters
                for (char c : "banana".toCharArray()) counts[c - 'a']++;
                System.out.println(counts['a' - 'a'] + " " + counts['n' - 'a']);

                Map<Integer, List<String>> byLength = new TreeMap<>();
                for (String w : List.of("hi", "cat", "go", "dog")) {
                    byLength.computeIfAbsent(w.length(), k -> new ArrayList<>()).add(w);
                }
                System.out.println(byLength);
                System.out.println(freq.getOrDefault('z', 0));
            }
        }
    ''', out="""
        {a=3, b=1, n=2}
        3 2
        {2=[hi, go], 3=[cat, dog]}
        0
    """)
    yield section("Stack, queue and heap", "stack-push")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Deque<Integer> stack = new ArrayDeque<>();
                stack.push(1); stack.push(2); stack.push(3);
                System.out.println(stack.pop() + " " + stack.peek());      // LIFO

                Deque<Integer> queue = new ArrayDeque<>();
                queue.offer(1); queue.offer(2); queue.offer(3);
                System.out.println(queue.poll() + " " + queue.peek());     // FIFO

                PriorityQueue<Integer> minHeap = new PriorityQueue<>(List.of(5, 1, 4));
                PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
                maxHeap.addAll(List.of(5, 1, 4));
                System.out.println(minHeap.poll() + " " + maxHeap.poll());

                // heap of int[] pairs ordered by the second value
                PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> Integer.compare(x[1], y[1]));
                pq.add(new int[]{7, 30}); pq.add(new int[]{8, 10}); pq.add(new int[]{9, 20});
                System.out.println(pq.poll()[0]);
            }
        }
    ''', out="""
        3 2
        1 2
        1 5
        8
    """)
    yield section("TreeMap: ordered queries", "sort-ascending-numbers")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                TreeMap<Integer, String> tm = new TreeMap<>(Map.of(10, "a", 20, "b", 30, "c"));
                System.out.println(tm.floorKey(25) + " " + tm.ceilingKey(25));    // ≤ 25, ≥ 25
                System.out.println(tm.lowerKey(10) + " " + tm.higherKey(30));     // strict: none → null
                System.out.println(tm.firstKey() + " " + tm.lastEntry());
                System.out.println(tm.headMap(20) + " " + tm.tailMap(20, true));
            }
        }
    ''', out="""
        20 30
        null null
        10 30=c
        {10=a} {20=b, 30=c}
    """)
    yield section("Templates", "template")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static int lowerBound(int[] a, int target) {        // first index with a[i] >= target
                int lo = 0, hi = a.length;
                while (lo < hi) {
                    int mid = lo + (hi - lo) / 2;                // not (lo + hi) / 2 — may overflow
                    if (a[mid] < target) lo = mid + 1; else hi = mid;
                }
                return lo;
            }

            static int shortestPath(char[][] grid) {            // BFS on a grid, '#' = wall
                int rows = grid.length, cols = grid[0].length;
                int[][] dist = new int[rows][cols];
                for (int[] row : dist) Arrays.fill(row, -1);
                Deque<int[]> q = new ArrayDeque<>();
                q.offer(new int[]{0, 0});
                dist[0][0] = 0;
                int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
                while (!q.isEmpty()) {
                    int[] cur = q.poll();
                    for (int[] d : dirs) {
                        int r = cur[0] + d[0], c = cur[1] + d[1];
                        if (r >= 0 && r < rows && c >= 0 && c < cols && grid[r][c] != '#' && dist[r][c] == -1) {
                            dist[r][c] = dist[cur[0]][cur[1]] + 1;
                            q.offer(new int[]{r, c});
                        }
                    }
                }
                return dist[rows - 1][cols - 1];
            }

            public static void main(String[] args) {
                int[] a = {1, 3, 5, 7};
                System.out.println(lowerBound(a, 5) + " " + lowerBound(a, 9));
                System.out.println(Arrays.binarySearch(a, 7) + " " + Arrays.binarySearch(a, 4));  // -(insertion)-1

                char[][] grid = {
                    "..#".toCharArray(),
                    ".##".toCharArray(),
                    "...".toCharArray(),
                };
                System.out.println(shortestPath(grid));
            }
        }
    ''', out="""
        2 4
        3 -3
        4
    """)
    yield section("Sorting idioms and the subtraction trap", "arrows-sort")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                int[][] intervals = {{5, 6}, {1, 3}, {2, 4}};
                Arrays.sort(intervals, (x, y) -> Integer.compare(x[0], y[0]));
                System.out.println(Arrays.deepToString(intervals));

                List<String> words = new ArrayList<>(List.of("pear", "fig", "apple", "kiwi"));
                words.sort(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()));
                System.out.println(words);

                List<Integer> nums = new ArrayList<>(List.of(1, Integer.MIN_VALUE, 5));
                nums.sort((x, y) -> x - y);                  // BROKEN: x - y overflows
                System.out.println(nums);
                nums.sort(Integer::compare);                 // correct
                System.out.println(nums);
            }
        }
    ''', out="""
        [[1, 3], [2, 4], [5, 6]]
        [fig, kiwi, pear, apple]
        [1, 5, -2147483648]
        [-2147483648, 1, 5]
    """)
    yield section("Handy one-liners", "bolt")
    yield table(
        ["Task", "Java"],
        ["Char ↔ index", "`c - 'a'`, `(char) ('a' + i)`"],
        ["Digit char → int", "`c - '0'` or `Character.getNumericValue(c)`"],
        ["Fill / copy arrays", "`Arrays.fill(a, -1)`, `Arrays.copyOfRange(a, l, r)`"],
        ["Sum / max of `int[]`", "`Arrays.stream(a).sum()`, `.max().getAsInt()`"],
        ["`List<Integer>` → `int[]`", "`list.stream().mapToInt(Integer::intValue).toArray()`"],
        ["Reverse a string", "`new StringBuilder(s).reverse().toString()`"],
        ["Infinity sentinels", "`Integer.MAX_VALUE`, `Long.MAX_VALUE` (beware of `+ 1`)"],
        ["Bit tricks", "`Integer.bitCount(x)`, `x & (x - 1)`, `1 << k`, `x >>> 1`"],
    )
    yield qa("Why ArrayDeque instead of Stack or LinkedList?",
             "`Stack` extends the synchronized `Vector` (needless locking, and it exposes index access). `LinkedList` allocates a node per element and has poor cache locality. `ArrayDeque` is a resizable circular array: O(1) at both ends, fast and memory-compact — the Javadoc itself recommends it for stacks and queues. (It rejects `null` elements.)")
    yield qa("Why is (a, b) -> a - b a bad comparator?",
             "The subtraction can overflow for large values of opposite sign (e.g. `1 - Integer.MIN_VALUE`), producing the wrong sign and an inconsistent ordering. Use `Integer.compare(a, b)` or `Comparator.comparingInt`.")


@topic(G, "interview-qa", "Java Interview Q&A", "messages")
def _():
    yield lead("The most frequently asked Java interview questions with crisp answers — a final revision sheet.")
    yield section("Platform and basics", "cpu")
    yield qa("What are the JDK, JRE and JVM?",
             "The **JVM** executes bytecode (interpreter + JIT + GC). The **JRE** is the JVM plus the standard class libraries — enough to *run* programs. The **JDK** is the JRE plus development tools (`javac`, `jar`, `jshell`, `jcmd`…) — needed to *build* them. Since Java 11 there's no separate JRE download; `jlink` builds custom runtimes.")
    yield qa("Why is Java platform independent?",
             "`javac` compiles source to platform-neutral **bytecode** (`.class` files). Each OS has its own JVM that runs that same bytecode. “Write once, run anywhere” — the JVM is platform-specific, the bytecode isn't.")
    yield qa("Is Java pass-by-value or pass-by-reference?",
             "Always pass-by-value. For objects, the value copied is the *reference*: the method can mutate the object it points to, but reassigning the parameter never affects the caller's variable.")
    yield snippet("java", r'''
        public class Main {
            static void reassign(StringBuilder sb) { sb = new StringBuilder("new"); }
            static void mutate(StringBuilder sb) { sb.append("!"); }

            public static void main(String[] args) {
                StringBuilder s = new StringBuilder("old");
                reassign(s);
                mutate(s);
                System.out.println(s);
            }
        }
    ''', out="old!")
    yield qa("What is the difference between == and equals()?",
             "`==` compares primitive values, or for references whether both point to the *same object*. `equals()` compares logical equality as defined by the class (`String`, `Integer`, records…); the default `Object.equals` is identity.")
    yield qa("What is the contract between equals() and hashCode()?",
             "Equal objects must have equal hash codes. Unequal objects may collide. If you override `equals` without `hashCode`, equal objects land in different buckets and `HashMap`/`HashSet` lookups fail.")
    yield qa("Why is String immutable? StringBuilder vs StringBuffer?",
             "Immutability makes the string pool safe, allows caching the hash code, gives thread safety and security (values can't change after validation). `StringBuilder` is a mutable, unsynchronized buffer — use it in single-threaded code; `StringBuffer` is the older synchronized version, rarely needed.")
    yield qa("final vs finally vs finalize?",
             "`final`: a variable can't be reassigned, a method can't be overridden, a class can't be extended. `finally`: a block that always runs after `try`/`catch`. `finalize()`: a deprecated `Object` method the GC might call before reclaiming an object — don't use it; use `try-with-resources` or `Cleaner`.")
    yield snippet("java", r'''
        public class Main {
            @SuppressWarnings("finally")
            static int tricky() {
                try {
                    return 1;
                } finally {
                    return 2;          // overrides the try's return (and would swallow exceptions)
                }
            }

            static int counter() {
                int x = 10;
                try {
                    return x;          // value 10 is saved now
                } finally {
                    x = 20;            // changing x does not change the saved return value
                }
            }

            public static void main(String[] args) {
                System.out.println(tricky() + " " + counter());
            }
        }
    ''', out="2 10")
    yield section("OOP", "hierarchy")
    yield qa("Overloading vs overriding?",
             "**Overloading**: same name, different parameter lists, in the same class — resolved at *compile time* by the static types of the arguments. **Overriding**: a subclass redefines an inherited instance method with the same signature — resolved at *run time* by the object's actual class (dynamic dispatch). Static methods can't be overridden, only *hidden*.")
    yield snippet("java", r'''
        public class Main {
            static class Animal {
                static String kind() { return "animal"; }
                String sound() { return "..."; }
            }
            static class Dog extends Animal {
                static String kind() { return "dog"; }          // hides, doesn't override
                @Override String sound() { return "woof"; }
            }

            static void print(Object o) { System.out.println("object"); }
            static void print(String s) { System.out.println("string"); }

            public static void main(String[] args) {
                Animal a = new Dog();
                System.out.println(a.sound());     // runtime type decides
                System.out.println(Animal.kind() + " " + Dog.kind());
                Object o = "text";
                print(o);                          // compile-time type decides
                print("text");
            }
        }
    ''', out="""
        woof
        animal dog
        object
        string
    """)
    yield qa("Abstract class vs interface?",
             "An abstract class can have state (instance fields), constructors and any access level; a class can extend only one. An interface has no instance state, only constants, abstract, `default`, `static` and `private` methods; a class can implement many. Use an interface for a capability/contract (“can be compared”), an abstract class for sharing code and state among closely related classes.")
    yield qa("What are the four pillars of OOP in Java?",
             "**Encapsulation** (private state behind methods), **Inheritance** (`extends`, code reuse and is-a), **Polymorphism** (one interface, many implementations — overriding and dynamic dispatch), **Abstraction** (expose what, hide how — interfaces and abstract classes).")
    yield qa("Static vs instance members?",
             "Static members belong to the class — one copy, accessed via the class name, loaded when the class initialises. Instance members belong to each object. Static methods have no `this`, so they can't access instance members directly.")
    yield qa("Records vs regular classes?",
             "A record is a transparent, shallowly immutable data carrier: the compiler generates the canonical constructor, accessors, `equals`, `hashCode` and `toString`. Records are implicitly `final`, can't extend another class and can't declare instance fields beyond their components — but can implement interfaces and add methods and validation.")
    yield qa("What are sealed classes for?",
             "`sealed ... permits A, B` restricts which classes may extend or implement a type. The hierarchy becomes closed and known to the compiler, so a pattern-matching `switch` over it can be checked for exhaustiveness without a `default`.")
    yield section("Exceptions", "alert-circle")
    yield qa("Checked vs unchecked exceptions?",
             "Checked exceptions (subclasses of `Exception` but not `RuntimeException`, e.g. `IOException`) must be caught or declared with `throws` — for recoverable conditions outside the program's control. Unchecked exceptions (`RuntimeException` and subclasses, e.g. `NullPointerException`, `IllegalArgumentException`) signal programming errors and need not be declared. `Error`s (`OutOfMemoryError`) are serious JVM problems you normally don't catch.")
    yield qa("What does try-with-resources do?",
             "It closes every resource declared in the header (anything `AutoCloseable`) automatically, in reverse order, even when an exception occurs. If both the body and `close()` throw, the close exception is attached to the primary one as a *suppressed* exception instead of replacing it.")
    yield section("Collections", "list")
    yield qa("How does HashMap work internally?",
             "An array of buckets. `put` computes `hashCode()`, spreads it (`h ^ (h >>> 16)`), and picks bucket `hash & (n - 1)`. Collisions are chained in a linked list; a bucket with more than 8 entries (when the table has at least 64 buckets) becomes a red-black tree, so worst-case lookup is O(log n). When size exceeds capacity × load factor (0.75), the table doubles and entries are redistributed. `get` finds the bucket, then compares with `hashCode` and `equals`.")
    yield qa("HashMap vs Hashtable vs ConcurrentHashMap?",
             "`HashMap`: not thread-safe, allows one `null` key and `null` values. `Hashtable`: legacy, every method synchronized on one lock, no nulls. `ConcurrentHashMap`: thread-safe with fine-grained locking (CAS + per-bin locks), lock-free reads, atomic `compute`/`merge`, no nulls, weakly consistent iterators — the one to use for concurrency.")
    yield qa("Fail-fast vs fail-safe iterators?",
             "Fail-fast iterators (`ArrayList`, `HashMap`) track a `modCount` and throw `ConcurrentModificationException` if the collection is structurally modified during iteration other than through the iterator. Fail-safe / weakly consistent iterators (`CopyOnWriteArrayList`, `ConcurrentHashMap`) iterate over a snapshot or tolerate concurrent changes and never throw it.")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = new ArrayList<>(List.of(1, 2, 3, 4));
                try {
                    for (Integer n : nums) {
                        if (n % 2 == 0) nums.remove(n);      // structural change during for-each
                    }
                } catch (ConcurrentModificationException e) {
                    System.out.println("ConcurrentModificationException");
                }
                nums = new ArrayList<>(List.of(1, 2, 3, 4));
                nums.removeIf(n -> n % 2 == 0);              // the safe way
                System.out.println(nums);
            }
        }
    ''', out="""
        ConcurrentModificationException
        [1, 3]
    """)
    yield qa("Comparable vs Comparator?",
             "`Comparable<T>` is implemented by the class itself (`compareTo`) and defines its single *natural ordering* (`String`, `Integer`). `Comparator<T>` is a separate object (`compare`) defining any number of *external* orderings, and composes: `Comparator.comparing(Person::age).thenComparing(Person::name).reversed()`.")
    yield qa("ArrayList vs LinkedList?",
             "`ArrayList` is a resizable array: O(1) random access, amortised O(1) append, O(n) insert/remove in the middle, cache-friendly. `LinkedList` is a doubly linked list: O(1) at the ends (or at an iterator position), O(n) access by index, high memory overhead per node. In practice `ArrayList` (or `ArrayDeque` for queues) wins almost always.")
    yield section("Concurrency", "arrows-split")
    yield qa("volatile vs synchronized vs atomic classes?",
             "`volatile` guarantees *visibility* and ordering of a single variable's reads/writes, but not atomicity of compound actions like `count++`. `synchronized` gives mutual exclusion *and* visibility for a whole block. `AtomicInteger` & co. make single-variable read-modify-write operations atomic with lock-free CAS — ideal for counters.")
    yield qa("wait() vs sleep()?",
             "`wait()` is an `Object` method, must be called while holding that object's monitor, *releases* the lock and waits for `notify`/`notifyAll` (or a timeout). `Thread.sleep()` is static, needs no lock and *keeps* any locks it holds while pausing for a fixed time.")
    yield qa("Runnable vs Callable?",
             "`Runnable.run()` returns nothing and can't throw checked exceptions. `Callable<V>.call()` returns a value and may throw `Exception`; submitting it to an `ExecutorService` gives a `Future<V>` to fetch the result.")
    yield qa("What are virtual threads?",
             "Lightweight threads (Java 21) scheduled by the JVM onto a few platform (OS) threads. When a virtual thread blocks on I/O it unmounts, freeing the carrier thread, so you can run millions of blocking tasks with simple thread-per-request code. Great for I/O-bound work; no gain for CPU-bound work. Don't pool them.")
    yield qa("What is a deadlock and how do you prevent it?",
             "Two or more threads each hold a lock the other needs, so all wait forever. Prevent it by acquiring locks in a single global order, holding locks briefly, using `tryLock` with timeouts, or avoiding shared mutable state (immutable objects, concurrent collections).")
    yield section("JVM and memory", "database")
    yield qa("What are the JVM memory areas?",
             "Heap (objects; young + old generations), per-thread stacks (frames with locals), metaspace (class metadata, native memory), PC registers, native method stacks and the code cache (JIT output).")
    yield qa("How does garbage collection decide what to free?",
             "It traces from GC roots (thread stacks, static fields, JNI refs) and marks every reachable object; everything else is garbage, cycles included. Collection is generational: frequent cheap minor GCs for the young generation, rarer old-generation collections. G1 is the default collector; ZGC offers sub-millisecond pauses.")
    yield qa("What is the difference between a ClassNotFoundException and a NoClassDefFoundError?",
             "`ClassNotFoundException` is a checked exception when code loads a class *by name* at run time (`Class.forName`) and it isn't on the classpath. `NoClassDefFoundError` is an `Error` when a class that was present at *compile time* can't be found or failed to initialise when the JVM links it at run time.")
    yield section("Functional Java", "lambda")
    yield qa("What is a functional interface?",
             "An interface with exactly one abstract method (it may have default/static methods), e.g. `Runnable`, `Comparator`, `Function<T,R>`, `Predicate<T>`. Lambdas and method references are instances of functional interfaces; `@FunctionalInterface` makes the compiler enforce the rule.")
    yield qa("Why are streams called lazy?",
             "Intermediate operations (`filter`, `map`, `sorted`) only build a pipeline; nothing runs until a terminal operation (`collect`, `forEach`, `count`). Elements then flow one at a time through the whole pipeline, and short-circuiting operations (`findFirst`, `limit`, `anyMatch`) stop early.")
    yield snippet("java", r'''
        import java.util.stream.Stream;

        public class Main {
            public static void main(String[] args) {
                Stream<Integer> pipeline = Stream.of(1, 2, 3, 4, 5)
                        .filter(n -> { System.out.println("filter " + n); return n % 2 == 0; })
                        .map(n -> { System.out.println("map " + n); return n * 10; });
                System.out.println("nothing has run yet");
                System.out.println("first = " + pipeline.findFirst().get());
            }
        }
    ''', out="""
        nothing has run yet
        filter 1
        filter 2
        map 2
        first = 20
    """)
    yield qa("How should Optional be used?",
             "As a *return type* for methods that may have no result, forcing callers to handle absence: `findUser(id).map(User::name).orElse(\"guest\")`. Don't use it for fields, parameters or collections, and avoid bare `get()` — prefer `orElse`, `orElseGet`, `orElseThrow`, `map`, `ifPresent`.")
    yield qa("map() vs flatMap() in streams?",
             "`map` transforms each element into exactly one element. `flatMap` transforms each element into a *stream* and flattens those streams into one — e.g. a list of sentences into a stream of words.")
    yield section("Rapid-fire tricks", "bolt")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(10 / 3 + " " + 10 % 3 + " " + 10 / 3.0);
                System.out.println((byte) 200);                 // narrowing wraps
                char c = 'A';
                c += 1;                                         // compound assignment casts implicitly
                System.out.println(c);
                int i = 5;
                i = i++ + ++i;                                  // 5 + 7
                System.out.println(i);
                System.out.println(Integer.MAX_VALUE + 1);
                System.out.println(1.0 / 0 + " " + (0.0 / 0 == 0.0 / 0));
                String s = null;
                System.out.println(s + "x");                    // concatenation turns null into "null"
            }
        }
    ''', out="""
        3 1 3.3333333333333335
        -56
        B
        12
        -2147483648
        Infinity false
        nullx
    """)
