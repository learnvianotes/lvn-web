from kit import *

G = "Advanced Types"


@topic(G, "nested-classes", "Inner, Nested, Local & Anonymous Classes", "box-multiple")
def _():
    yield lead("A class can be declared *inside* another class, method or expression. The four kinds differ in one key way: whether they hold a hidden reference to an enclosing instance.")
    yield define("Nested class", "any class declared inside another class. A **static nested** class is just a namespaced top-level class; a non-static one is an **inner** class and is tied to an instance of the outer class.")
    yield section("The four kinds at a glance", "list-details")
    yield table(
        ["Kind", "Declared", "Outer instance?", "Typical use"],
        ["**Static nested**", "`static class Node` inside a class", "No", "Helpers that belong with the outer class: `Map.Entry`, `Builder`, linked-list `Node`"],
        ["**Inner (member)**", "`class Itr` inside a class", "**Yes** — `Outer.this`", "Iterators and views that need the outer object's fields"],
        ["**Local**", "`class X` inside a method body", "Yes, if in an instance method", "A one-method helper type with a name"],
        ["**Anonymous**", "`new Interface() { … }` expression", "Yes, if in an instance context", "One-off implementation; mostly replaced by lambdas"],
    )
    yield section("Static nested vs inner", "sitemap")
    yield snippet("java", r'''
        public class Main {
            private int size = 3;
            private static String kind = "outer";

            static class StaticNested {            // no outer instance
                String describe() { return "nested sees " + kind; }   // only static members
            }

            class Inner {                          // bound to a Main instance
                int size = 10;
                String describe() {
                    return "inner " + size + ", outer " + Main.this.size;
                }
            }

            public static void main(String[] args) {
                StaticNested n = new StaticNested();          // no Main needed
                System.out.println(n.describe());

                Main outer = new Main();
                Main.Inner in = outer.new Inner();            // needs an outer instance
                System.out.println(in.describe());
            }
        }
    ''', out="""
        nested sees outer
        inner 10, outer 3
    """)
    yield note("Inside an inner class, `this` is the inner object and `Main.this` is the enclosing one. Use the qualified form when a field name is shadowed.")
    yield section("Local and anonymous classes", "code")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            interface Greeter { String greet(String name); }

            public static void main(String[] args) {
                String greeting = "Hello";                  // effectively final → can be captured

                class Polite implements Greeter {           // local class: has a name, lives in this method
                    public String greet(String name) { return greeting + ", " + name + "!"; }
                }

                Greeter shout = new Greeter() {             // anonymous class: no name, one instance
                    @Override
                    public String greet(String name) { return greeting.toUpperCase() + " " + name; }
                };

                Greeter lambda = name -> greeting + " " + name;   // same thing, as a lambda

                System.out.println(new Polite().greet("Asha"));
                System.out.println(shout.greet("Ravi"));
                System.out.println(lambda.greet("Mei"));

                List<String> names = new ArrayList<>(List.of("bob", "Al", "carol"));
                names.sort(new Comparator<String>() {       // classic pre-Java-8 style
                    public int compare(String a, String b) { return a.length() - b.length(); }
                });
                System.out.println(names);
            }
        }
    ''', out="""
        Hello, Asha!
        HELLO Ravi
        Hello Mei
        [Al, bob, carol]
    """)
    yield section("Capturing variables: effectively final", "lock")
    yield p("Local, anonymous classes and lambdas can read local variables of the enclosing method only if they are **final or effectively final** (never reassigned). The value is *copied* into the object, so allowing later changes would make the copy and the variable disagree.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                int count = 0;
                Runnable r = () -> System.out.println(count);
                count++;                 // makes count not effectively final
                r.run();
            }
        }
    ''', fails=True)
    yield output("""
        Main.java:4: error: local variables referenced from a lambda expression must be final or effectively final
                Runnable r = () -> System.out.println(count);
                                                      ^
    """, "Compiler error")
    yield good("Need a mutable counter inside a lambda? Use an `AtomicInteger`, a one-element array, or — better — restructure with a stream.")
    yield section("Anonymous class vs lambda", "arrows-diff")
    yield table(
        ["", "Anonymous class", "Lambda"],
        ["Implements", "Any interface or abstract/concrete class, many methods", "Only a **functional interface** (one abstract method)"],
        ["`this` means", "The anonymous object itself", "The **enclosing** instance"],
        ["State", "Can have fields", "No fields of its own"],
        ["Compiled to", "A separate `Main$1.class` file", "`invokedynamic` — no extra class file"],
    )
    yield warn("Every inner/anonymous class created in an instance method keeps a hidden reference to `Outer.this`. If it outlives the outer object (a listener, a cached task, a `Runnable` handed to a thread) it keeps the whole outer object alive — a classic **memory leak** (e.g. Android Activities). Prefer `static` nested classes unless you really need the outer instance.", "Memory leak")
    yield qa("Static nested vs inner class — when to use which?",
             "Default to **static nested**: it's cheaper (no hidden outer reference), can be created without an outer instance, and can't leak the outer object. Use an **inner** class only when it must read or write the outer instance's state, like an iterator over the outer collection.")
    yield qa("Why must captured local variables be effectively final?",
             "The lambda/anonymous object gets a *copy* of the value (locals live on the stack and may be gone when the object runs). If the variable could change afterwards, the copy would silently be stale, so Java forbids it at compile time.")
    yield qa("What does `this` refer to inside a lambda vs an anonymous class?",
             "In an anonymous class, `this` is the anonymous object. A lambda has no identity of its own, so `this` is the enclosing class instance.")


@topic(G, "object-methods", "The Object Class: equals, hashCode & toString", "equal")
def _():
    yield lead("Every class extends `java.lang.Object`. Its `equals`, `hashCode` and `toString` defaults are almost never what a value class wants — and `equals` and `hashCode` must be overridden **together**.")
    yield section("What Object gives every class", "list")
    yield table(
        ["Method", "Default behaviour", "Override?"],
        ["`boolean equals(Object o)`", "Identity: `this == o`", "Yes, for value classes"],
        ["`int hashCode()`", "Identity-based number", "**Always together with `equals`**"],
        ["`String toString()`", "`ClassName@1b6d3586` (class + hex hash)", "Yes — for logs and debugging"],
        ["`Class<?> getClass()`", "Runtime class", "Final — cannot"],
        ["`Object clone()`", "Shallow field copy (needs `Cloneable`)", "Rarely — prefer copy constructors"],
        ["`wait / notify / notifyAll`", "Monitor-based thread coordination", "Final — cannot"],
        ["`finalize()`", "Deprecated for removal (Java 9+)", "Never"],
    )
    yield section("The equals / hashCode contract", "file-certificate")
    yield ul(
        "**Reflexive**: `x.equals(x)` is `true`.",
        "**Symmetric**: `x.equals(y)` ⇔ `y.equals(x)`.",
        "**Transitive**: `x.equals(y)` and `y.equals(z)` ⇒ `x.equals(z)`.",
        "**Consistent**: repeated calls give the same answer while the objects don't change.",
        "`x.equals(null)` is `false`.",
        "**Equal objects must have equal hash codes.** (Unequal objects *may* share a hash code — that's a collision, which is legal.)",
    )
    yield section("A correct implementation", "check")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Point a = new Point(1, 2), b = new Point(1, 2);
                System.out.println(a == b);          // different objects
                System.out.println(a.equals(b));     // same value
                System.out.println(a.hashCode() == b.hashCode());
                System.out.println(a);               // our toString

                Set<Point> set = new HashSet<>(List.of(a));
                System.out.println(set.contains(b));
            }
        }

        final class Point {
            private final int x, y;
            Point(int x, int y) { this.x = x; this.y = y; }

            @Override
            public boolean equals(Object o) {
                if (this == o) return true;                    // fast path
                if (!(o instanceof Point p)) return false;     // also handles null
                return x == p.x && y == p.y;
            }

            @Override
            public int hashCode() { return Objects.hash(x, y); }

            @Override
            public String toString() { return "Point[x=" + x + ", y=" + y + "]"; }
        }
    ''', out="""
        false
        true
        true
        Point[x=1, y=2]
        true
    """)
    yield note("`@Override` makes the compiler check that you really override. A classic bug is `public boolean equals(Point p)` — that *overloads* `equals(Object)`, so `HashSet` and `List.contains` never call it.")
    yield section("What breaks when hashCode is missing", "bug")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                Set<Key> set = new HashSet<>();
                set.add(new Key("id-7"));
                System.out.println(new Key("id-7").equals(new Key("id-7")));
                System.out.println(set.contains(new Key("id-7")));   // looks in the wrong bucket
            }
        }

        class Key {
            final String id;
            Key(String id) { this.id = id; }
            @Override public boolean equals(Object o) {
                return o instanceof Key k && id.equals(k.id);
            }
            // hashCode NOT overridden → identity hash, different for each object
        }
    ''', out="""
        true
        false
    """)
    yield p("`HashSet`/`HashMap` first use `hashCode()` to pick a bucket and only then call `equals` on the entries in that bucket. Two \"equal\" keys with different hash codes land in different buckets and are never compared.")
    yield warn("Never use a **mutable** field in `hashCode` for an object stored in a hash collection. Change the field after inserting and the object is stranded in the old bucket: `contains` returns `false` and `remove` fails.", "Mutable keys")
    yield section("`getClass()` vs `instanceof` in equals", "arrows-split")
    yield table(
        ["Check", "Subclass instances", "Trade-off"],
        ["`o instanceof Point p`", "Can be equal to a `Point`", "Liskov-friendly, but symmetry breaks if a subclass adds fields and overrides `equals`"],
        ["`getClass() != o.getClass()`", "Never equal to a `Point`", "Strictly symmetric, but a harmless subclass (or proxy) is never equal"],
    )
    yield p("Common guidance: make value classes `final` (or use a **record**) and use `instanceof` — then the question doesn't arise.")
    yield section("Helpers in `java.util.Objects`", "tool")
    yield snippet("java", r'''
        import java.util.Objects;

        public class Main {
            public static void main(String[] args) {
                String a = null, b = "x";
                System.out.println(Objects.equals(a, b));          // null-safe, no NPE
                System.out.println(Objects.equals(null, null));
                System.out.println(Objects.hash(1, "a") == Objects.hash(1, "a"));
                System.out.println(Objects.hashCode(null));        // 0 for null
                System.out.println(Objects.toString(a, "n/a"));    // default for null
                System.out.println(Objects.requireNonNullElse(a, "fallback"));
                try {
                    Objects.requireNonNull(a, "name must not be null");
                } catch (NullPointerException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out="""
        false
        true
        true
        0
        n/a
        fallback
        name must not be null
    """)
    yield section("clone() — briefly", "copy")
    yield p("`Object.clone()` makes a **shallow** copy and only works if the class implements the marker interface `Cloneable` (otherwise it throws `CloneNotSupportedException`). It bypasses constructors and is awkward with `final` fields. Arrays are the one place it's pleasant: `int[] copy = arr.clone();`.")
    yield good("Prefer a copy constructor `new Point(other)` or a static factory `Point.copyOf(other)` over `clone()`.")
    yield qa("Why must you override hashCode when you override equals?",
             "Hash-based collections look up the bucket by `hashCode()` before calling `equals`. If two equal objects return different hash codes, `HashMap.get`/`HashSet.contains` look in the wrong bucket and fail — the contract *equal ⇒ same hash* is broken.")
    yield qa("Can two unequal objects have the same hashCode?",
             "Yes — that's a collision and it's allowed; the map then falls back to `equals` inside the bucket. Only the reverse is forbidden. Many collisions just make lookups slower.")
    yield qa("What does the default toString print?",
             "`getClass().getName() + \"@\" + Integer.toHexString(hashCode())` — e.g. `Point@1b6d3586`. It is not a memory address, just the identity hash code in hex.")
    yield qa("What is wrong with `public boolean equals(Point other)`?",
             "It overloads instead of overriding `equals(Object)`. Collections call `equals(Object)`, which is still the identity version. Always declare the parameter as `Object` and add `@Override`.")


@topic(G, "records", "Records", "id")
def _():
    yield lead("A `record` (Java 16+) is a concise, immutable data carrier: declare the components and the compiler writes the constructor, accessors, `equals`, `hashCode` and `toString`.")
    yield define("Record", "a final class whose state is exactly its **components**: `record Point(int x, int y) {}` gets `private final` fields, a canonical constructor, accessors `x()` / `y()`, and value-based `equals`/`hashCode`/`toString`.")
    yield section("What you get for free", "gift")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            record Point(int x, int y) {}

            public static void main(String[] args) {
                Point p = new Point(3, 4);
                System.out.println(p);                     // generated toString
                System.out.println(p.x() + p.y());         // accessors: x(), not getX()
                System.out.println(p.equals(new Point(3, 4)));
                System.out.println(new HashSet<>(List.of(p)).contains(new Point(3, 4)));
            }
        }
    ''', out="""
        Point[x=3, y=4]
        7
        true
        true
    """)
    yield table(
        ["Generated member", "For `record Point(int x, int y)`"],
        ["Fields", "`private final int x; private final int y;`"],
        ["Canonical constructor", "`Point(int x, int y)`"],
        ["Accessors", "`int x()`, `int y()`"],
        ["`equals` / `hashCode`", "Compare / hash all components"],
        ["`toString`", "`Point[x=3, y=4]`"],
    )
    yield section("Compact constructor: validate and normalise", "shield-check")
    yield snippet("java", r'''
        public class Main {
            record Range(int lo, int hi) {
                Range {                                    // compact canonical constructor: no parameter list
                    if (lo > hi) throw new IllegalArgumentException("lo > hi: " + lo + " > " + hi);
                }
                int length() { return hi - lo; }           // extra methods are fine
                static Range of(int a, int b) {            // static factory
                    return new Range(Math.min(a, b), Math.max(a, b));
                }
            }

            record Email(String value) {
                Email {
                    value = value.trim().toLowerCase();     // reassign the parameter, not this.value
                }
            }

            public static void main(String[] args) {
                System.out.println(new Range(2, 9).length());
                System.out.println(Range.of(9, 2));
                System.out.println(new Email("  Asha@Mail.COM "));
                try {
                    new Range(5, 1);
                } catch (IllegalArgumentException e) {
                    System.out.println("rejected: " + e.getMessage());
                }
            }
        }
    ''', out="""
        7
        Range[lo=2, hi=9]
        Email[value=asha@mail.com]
        rejected: lo > hi: 5 > 1
    """)
    yield note("In a compact constructor the fields are assigned **after** your code runs, from the (possibly reassigned) parameters. You cannot write `this.lo = …` there.")
    yield section("Records and shallow immutability", "lock-open")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            record Team(String name, List<String> members) {
                Team {
                    members = List.copyOf(members);        // defensive, unmodifiable copy
                }
            }

            public static void main(String[] args) {
                List<String> list = new ArrayList<>(List.of("Asha"));
                Team t = new Team("core", list);
                list.add("Ravi");                          // doesn't leak into the record
                System.out.println(t.members());
                try {
                    t.members().add("Mei");
                } catch (UnsupportedOperationException e) {
                    System.out.println("members are read-only");
                }
            }
        }
    ''', out="""
        [Asha]
        members are read-only
    """)
    yield warn("A record's fields are `final`, but the objects they point to are not magically immutable. A `List` component is still mutable unless you copy it with `List.copyOf` in the compact constructor.")
    yield section("Rules and limitations", "ruler")
    yield table(
        ["Allowed", "Not allowed"],
        ["Static fields and methods, instance methods", "Extra **instance** fields"],
        ["Implementing interfaces", "Extending a class (records implicitly extend `java.lang.Record`)"],
        ["Nested records, generic records `record Pair<A, B>(A a, B b)`", "Being extended — records are implicitly `final`"],
        ["Overriding accessors / `toString` / `equals`", "Mutating components (fields are `final`)"],
        ["Annotations on components", "Non-canonical constructors that don't delegate to `this(…)`"],
    )
    yield cards(
        ("Great for", "DTOs, API responses, map keys, tuples returned from methods, events, sealed-hierarchy cases with pattern matching.", "thumb-up"),
        ("Not for", "JPA entities (need mutability and a no-arg constructor), classes with hidden or derived mutable state.", "thumb-down"),
    )
    yield qa("Record vs Lombok @Data vs a hand-written class?",
             "A record is a language feature: immutable, transparent, no library needed, and it works with record patterns in `switch`. Lombok `@Data` generates *mutable* getters/setters. Write a normal class when you need mutability, inheritance or encapsulated state.")
    yield qa("Are records immutable?",
             "Shallowly. The component fields are `private final` and there are no setters, but a mutable component (a `List`, an array) can still be changed through its reference unless you defensively copy it.")
    yield qa("Can a record have a no-arg constructor?",
             "Only as a non-canonical constructor that delegates: `Point() { this(0, 0); }`. Every constructor must end up calling the canonical one.")


@topic(G, "enums", "Enums", "list-numbers")
def _():
    yield lead("An `enum` is a class with a fixed, named set of instances. It's type-safe, can carry fields and behaviour, and works in `switch`, `EnumMap` and `EnumSet`.")
    yield define("Enum", "a special class whose instances are exactly the listed constants, created once when the class loads. Each constant is a `public static final` instance; every enum implicitly extends `java.lang.Enum`.")
    yield section("Built-in methods", "list")
    yield snippet("java", r'''
        public class Main {
            enum Day { MON, TUE, WED, THU, FRI, SAT, SUN }

            public static void main(String[] args) {
                Day d = Day.WED;
                System.out.println(d + " " + d.name() + " " + d.ordinal());
                System.out.println(Day.valueOf("FRI").compareTo(Day.MON));  // by ordinal
                System.out.println(Day.values().length);
                System.out.println(d == Day.WED);          // safe: constants are singletons
                try {
                    Day.valueOf("Funday");
                } catch (IllegalArgumentException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out="""
        WED WED 2
        4
        7
        true
        No enum constant Main.Day.Funday
    """)
    yield table(
        ["Member", "Meaning"],
        ["`values()`", "Array of all constants in declaration order (a fresh copy each call)"],
        ["`valueOf(String)`", "Constant by exact name, else `IllegalArgumentException`"],
        ["`name()` / `toString()`", "Declared name (`toString` can be overridden, `name` cannot)"],
        ["`ordinal()`", "0-based position — don't persist it; reordering constants changes it"],
        ["`compareTo`", "Compares by ordinal; enums are `Comparable`"],
    )
    yield section("Fields, constructors and methods", "settings")
    yield snippet("java", r'''
        public class Main {
            enum Planet {
                MERCURY(3.303e+23, 2.4397e6),
                EARTH(5.976e+24, 6.37814e6);

                private final double mass, radius;            // per-constant data
                Planet(double mass, double radius) {          // constructor is implicitly private
                    this.mass = mass;
                    this.radius = radius;
                }
                double surfaceGravity() {
                    return 6.67300E-11 * mass / (radius * radius);
                }
            }

            public static void main(String[] args) {
                for (Planet p : Planet.values())
                    System.out.printf("%s %.2f%n", p, p.surfaceGravity());
            }
        }
    ''', out="""
        MERCURY 3.70
        EARTH 9.80
    """)
    yield section("Constant-specific bodies", "puzzle")
    yield snippet("java", r'''
        public class Main {
            enum Op {
                ADD("+") { int apply(int a, int b) { return a + b; } },
                MUL("*") { int apply(int a, int b) { return a * b; } };

                final String symbol;
                Op(String symbol) { this.symbol = symbol; }
                abstract int apply(int a, int b);            // each constant must implement it
            }

            public static void main(String[] args) {
                for (Op op : Op.values())
                    System.out.println("6 " + op.symbol + " 7 = " + op.apply(6, 7));
            }
        }
    ''', out="""
        6 + 7 = 13
        6 * 7 = 42
    """)
    yield section("Switch over an enum", "switch-horizontal")
    yield snippet("java", r'''
        public class Main {
            enum Level { LOW, MEDIUM, HIGH }

            static String action(Level l) {
                return switch (l) {             // exhaustive: no default needed
                    case LOW -> "ignore";
                    case MEDIUM -> "log";
                    case HIGH -> "page on-call";
                };
            }

            public static void main(String[] args) {
                for (Level l : Level.values()) System.out.println(l + " -> " + action(l));
            }
        }
    ''', out="""
        LOW -> ignore
        MEDIUM -> log
        HIGH -> page on-call
    """)
    yield note("In a `case` label you write the bare constant `LOW`, not `Level.LOW` (qualified names in case labels are only allowed from Java 21). A switch *expression* over an enum must cover every constant or have a `default`.")
    yield section("EnumSet and EnumMap", "table")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            enum Day { MON, TUE, WED, THU, FRI, SAT, SUN }

            public static void main(String[] args) {
                EnumSet<Day> weekend = EnumSet.of(Day.SAT, Day.SUN);          // a bit vector inside
                EnumSet<Day> weekdays = EnumSet.complementOf(weekend);
                System.out.println(weekdays);
                System.out.println(EnumSet.range(Day.TUE, Day.THU));

                Map<Day, Integer> hours = new EnumMap<>(Day.class);          // array indexed by ordinal
                hours.put(Day.FRI, 6);
                hours.put(Day.MON, 8);
                System.out.println(hours);                                   // always in declaration order
            }
        }
    ''', out="""
        [MON, TUE, WED, THU, FRI]
        [TUE, WED, THU]
        {MON=8, FRI=6}
    """)
    yield good("Use `EnumSet` instead of bit flags and `EnumMap` instead of `HashMap` with enum keys — both are faster, compact, and iterate in declaration order.")
    yield section("The enum singleton", "user")
    yield snippet("java", r'''
        public class Main {
            enum Registry {
                INSTANCE;
                private int count;
                int next() { return ++count; }
            }

            public static void main(String[] args) {
                Registry.INSTANCE.next();
                System.out.println(Registry.INSTANCE.next());
            }
        }
    ''', out="2")
    yield p("*Effective Java* calls a single-element enum the best singleton: the JVM guarantees one instance, it is thread-safe to initialise, and it is safe against reflection and serialization attacks that break classic singletons.")
    yield warn("Don't store or persist `ordinal()` (e.g. in a database). Adding or reordering a constant silently changes every ordinal. Persist `name()` or an explicit code field instead.")
    yield qa("Can an enum extend a class? Implement an interface?",
             "It cannot extend anything — it already extends `java.lang.Enum`. It *can* implement interfaces, which is a common way to make several enums interchangeable.")
    yield qa("Why is comparing enums with == safe?",
             "Each constant is created exactly once per class loader and can't be instantiated again (constructors are private; reflection and deserialization are blocked). So identity equals equality, and `==` is also null-safe.")
    yield qa("Why can't an enum constructor be public?",
             "The set of instances is fixed at compile time. Allowing `new` would break that guarantee, so enum constructors are implicitly `private`.")


@topic(G, "sealed-classes", "Sealed Classes & Interfaces", "lock-square")
def _():
    yield lead("A `sealed` type (Java 17) lists exactly which classes may extend it. The compiler then knows the full set of subtypes — which makes `switch` over them exhaustive.")
    yield define("Sealed", "`sealed interface Shape permits Circle, Square` — only the named types may directly implement `Shape`. Each permitted subtype must itself be `final`, `sealed` or `non-sealed`.")
    yield section("Why seal a hierarchy?", "bulb")
    yield cards(
        ("Closed set of cases", "Model \"one of these and nothing else\": a `Result` is `Ok` or `Err`; a JSON value is one of six kinds.", "list-check"),
        ("Exhaustive switch", "`switch` over a sealed type needs no `default` — and adding a new subtype makes every non-exhaustive switch a **compile error**.", "checks"),
        ("Controlled extension", "Public enough to use, not open for arbitrary subclassing — stronger than package-private, weaker than `final`.", "shield"),
    )
    yield section("Subtype modifiers", "adjustments")
    yield table(
        ["Permitted subtype is…", "Meaning"],
        ["`final`", "No further subclasses (records and enums are implicitly final)"],
        ["`sealed … permits …`", "Continues the restriction one level down"],
        ["`non-sealed`", "Re-opens that branch — anyone may extend it"],
    )
    yield section("Sealed interface + records + pattern switch", "code")
    yield snippet("java", r'''
        public class Main {
            sealed interface Shape permits Circle, Square, Rect {}
            record Circle(double r) implements Shape {}
            record Square(double side) implements Shape {}
            record Rect(double w, double h) implements Shape {}

            static double area(Shape s) {
                return switch (s) {                    // exhaustive: no default
                    case Circle c -> Math.PI * c.r() * c.r();
                    case Square sq -> sq.side() * sq.side();
                    case Rect(double w, double h) -> w * h;     // record pattern (Java 21)
                };
            }

            public static void main(String[] args) {
                Shape[] shapes = { new Circle(1), new Square(2), new Rect(2, 3) };
                for (Shape s : shapes) System.out.printf("%s -> %.2f%n", s, area(s));
            }
        }
    ''', out="""
        Circle[r=1.0] -> 3.14
        Square[side=2.0] -> 4.00
        Rect[w=2.0, h=3.0] -> 6.00
    """)
    yield note("This is Java's version of *algebraic data types*: the sealed interface is the \"sum\", each record is a \"product\". Together with pattern matching it replaces many uses of the Visitor pattern.")
    yield section("Sealed classes with final / non-sealed", "sitemap")
    yield snippet("java", r'''
        public class Main {
            static abstract sealed class Vehicle permits Car, Truck {}
            static final class Car extends Vehicle {}
            static non-sealed class Truck extends Vehicle {}      // open again
            static class Pickup extends Truck {}                  // allowed: Truck is non-sealed

            static String describe(Vehicle v) {
                return switch (v) {
                    case Car c -> "car";
                    case Truck t -> "truck (" + t.getClass().getSimpleName() + ")";
                };
            }

            public static void main(String[] args) {
                System.out.println(describe(new Car()));
                System.out.println(describe(new Pickup()));
            }
        }
    ''', out="""
        car
        truck (Pickup)
    """)
    yield section("Trying to extend a sealed type", "ban")
    yield snippet("java", r'''
        public class Main {
            sealed interface Shape permits Circle {}
            record Circle(double r) implements Shape {}
            record Triangle(double b, double h) implements Shape {}   // not in permits

            public static void main(String[] args) {}
        }
    ''', fails=True)
    yield output("""
        Main.java:4: error: class is not allowed to extend sealed class: Shape (as it is not listed in its 'permits' clause)
            record Triangle(double b, double h) implements Shape {}   // not in permits
            ^
    """, "Compiler error")
    yield ul(
        "Permitted subclasses must be in the same **module** (or the same **package** in the unnamed module).",
        "If all subtypes are in the same source file, the `permits` clause can be omitted — the compiler infers it.",
        "Every permitted subtype must directly extend/implement the sealed type.",
    )
    yield qa("Sealed class vs final class vs enum?",
             "`final` allows no subclasses; an `enum` has a fixed set of *instances* of one type; a `sealed` type has a fixed set of *subtypes*, each of which can carry different data (e.g. `Circle(r)` vs `Rect(w, h)`).")
    yield qa("What does sealing buy you in a switch?",
             "Exhaustiveness checking: the compiler knows every possible subtype, so a pattern `switch` needs no `default`, and adding a new permitted subtype turns every switch that forgot it into a compile error instead of a runtime surprise.")


@topic(G, "immutability", "Immutable Classes", "lock")
def _():
    yield lead("An immutable object's state can't change after construction. It is automatically thread-safe, safe to share and cache, and safe as a `HashMap` key — `String`, `Integer` and `LocalDate` are all immutable.")
    yield section("The recipe", "list-check")
    yield steps(
        ("Make the class `final`", "(or make constructors private with static factories) so no subclass can add mutable state."),
        ("Make every field `private final`", "assigned once, in the constructor."),
        ("No setters", "no method that changes a field. \"Withers\" return a *new* object: `withPrice(…)`."),
        ("Defensive copy mutable inputs", "copy lists/arrays/dates passed to the constructor, so the caller can't change them later."),
        ("Never expose mutable internals", "return copies or unmodifiable views from getters."),
    )
    yield section("A broken \"immutable\" class", "bug")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> tags = new ArrayList<>(List.of("java"));
                Article a = new Article("Intro", tags);
                tags.add("hacked");                 // caller still holds the same list
                a.tags().clear();                   // getter hands out the internal list
                a.tags().add("oops");
                System.out.println(a.tags());
            }
        }

        final class Article {
            private final String title;
            private final List<String> tags;        // final reference, mutable list
            Article(String title, List<String> tags) { this.title = title; this.tags = tags; }
            List<String> tags() { return tags; }
        }
    ''', out="[oops]")
    yield warn("`final` makes the *reference* unchangeable, not the object it points to. A `final List` can still be cleared.")
    yield section("Fixed with defensive copies", "shield-check")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<String> tags = new ArrayList<>(List.of("java"));
                Article a = new Article("Intro", tags);
                tags.add("hacked");                           // no effect on a
                try {
                    a.tags().add("oops");
                } catch (UnsupportedOperationException e) {
                    System.out.println("read-only");
                }
                Article b = a.withTitle("Basics");            // "modify" = new object
                System.out.println(a.title() + " " + a.tags());
                System.out.println(b.title() + " " + b.tags());
            }
        }

        final class Article {
            private final String title;
            private final List<String> tags;
            Article(String title, List<String> tags) {
                this.title = Objects.requireNonNull(title);
                this.tags = List.copyOf(tags);                // copy in (and unmodifiable)
            }
            String title() { return title; }
            List<String> tags() { return tags; }              // safe: already unmodifiable
            Article withTitle(String t) { return new Article(t, tags); }
        }
    ''', out="""
        read-only
        Intro [java]
        Basics [java]
    """)
    yield section("Unmodifiable view vs immutable copy", "eye")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> src = new ArrayList<>(List.of(1, 2));
                List<Integer> view = Collections.unmodifiableList(src);   // a read-only window
                List<Integer> copy = List.copyOf(src);                    // an independent snapshot
                src.add(3);
                System.out.println(view);    // sees the change!
                System.out.println(copy);    // doesn't
                try {
                    List.of(1, null);
                } catch (NullPointerException e) {
                    System.out.println("List.of rejects nulls");
                }
            }
        }
    ''', out="""
        [1, 2, 3]
        [1, 2]
        List.of rejects nulls
    """)
    yield table(
        ["API", "Can you modify it?", "Reflects source changes?", "Nulls"],
        ["`Collections.unmodifiableList(src)`", "No (`UnsupportedOperationException`)", "**Yes** — it's a view", "Allowed"],
        ["`List.copyOf(src)` / `Set.copyOf` / `Map.copyOf`", "No", "No — snapshot", "Rejected"],
        ["`List.of(…)` / `Set.of` / `Map.of`", "No", "—", "Rejected"],
        ["`stream().toList()` (16+)", "No", "No", "Allowed"],
        ["`Collectors.toList()`", "Yes (currently an `ArrayList`)", "No", "Allowed"],
    )
    yield section("Why bother?", "bulb")
    yield cards(
        ("Thread-safe for free", "No state changes → no races, no locks. Can be shared across threads freely.", "users"),
        ("Safe keys & set members", "Hash code never changes, so the object never gets lost in a `HashMap`.", "key"),
        ("Cacheable & shareable", "`Integer.valueOf` cache, the string pool and `BigInteger.ZERO` all rely on immutability.", "database"),
        ("Easier reasoning", "Validate once in the constructor; the invariant holds forever. No defensive copies needed by callers.", "brain"),
    )
    yield p("The cost is allocating a new object for every change. For heavy step-by-step construction, pair the immutable class with a mutable builder (like `String` + `StringBuilder`).")
    yield qa("How do you make a class immutable?",
             "`final` class, `private final` fields, no setters, validate in the constructor, defensively copy mutable arguments in, and never hand out references to mutable internals (return copies or unmodifiable collections). Records do most of this for you, except the deep copying.")
    yield qa("Why is String immutable?",
             "So it can be pooled and shared (string literals), cache its hash code (fast `HashMap` keys), be used safely for security-sensitive values (class names, file paths, URLs) and be shared across threads without synchronization.")
    yield qa("Collections.unmodifiableList vs List.copyOf?",
             "`unmodifiableList` is a read-only *view*: you can't modify through it, but changes to the underlying list show through. `List.copyOf` makes an independent immutable snapshot (and rejects nulls).")
