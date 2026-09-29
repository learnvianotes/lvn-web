from kit import *

G = "Inheritance & Polymorphism"


@topic(G, "inheritance", "Inheritance", "hierarchy")
def _():
    yield lead("A subclass `extends` a superclass to inherit its fields and methods, adding or overriding behaviour — an *IS-A* relationship.")
    yield define("Inheritance", "the mechanism by which one class (subclass / child) acquires the non-private members of another (superclass / parent). Every class ultimately extends `java.lang.Object`.")
    yield section("Basic syntax", "code")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Dog d = new Dog("Rex");
                d.eat();          // inherited from Animal
                d.bark();         // Dog's own
                System.out.println(d.name + " is an Animal? " + (d instanceof Animal));
                System.out.println(d.getClass().getSuperclass().getSimpleName());
                System.out.println(Animal.class.getSuperclass().getName());
            }
        }

        class Animal {
            protected String name;
            Animal(String name) { this.name = name; }
            void eat() { System.out.println(name + " eats"); }
        }

        class Dog extends Animal {
            Dog(String name) { super(name); }
            void bark() { System.out.println(name + " barks"); }
        }
    ''', out='''
        Rex eats
        Rex barks
        Rex is an Animal? true
        Animal
        java.lang.Object
    ''')
    yield section("What is (and isn't) inherited", "list-check")
    yield table(
        ["Member", "Inherited?"],
        ["`public` / `protected` fields and methods", "Yes"],
        ["Package-private members", "Only if the subclass is in the same package"],
        ["`private` members", "No (they exist inside the object, but the subclass can't access them)"],
        ["Constructors", "No — they are called via `super(...)`"],
        ["Static members", "Accessible through the subclass, but *hidden* rather than overridden"],
    )
    yield section("Types of inheritance", "sitemap")
    yield table(
        ["Type", "Shape", "In Java?"],
        ["Single", "`B extends A`", "Yes"],
        ["Multilevel", "`C extends B`, `B extends A`", "Yes"],
        ["Hierarchical", "`B extends A`, `C extends A`", "Yes"],
        ["Multiple (classes)", "`C extends A, B`", "**No** — ambiguity (diamond problem)"],
        ["Multiple (interfaces)", "`C implements X, Y`", "Yes — interfaces carry no instance state"],
        ["Hybrid", "mix of the above", "Only via interfaces"],
    )
    yield section("Constructor chaining up the hierarchy", "arrow-up")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                new Puppy();
            }
        }

        class Animal { Animal() { System.out.println("Animal()"); } }
        class Dog extends Animal { Dog() { System.out.println("Dog()"); } }
        class Puppy extends Dog { Puppy() { System.out.println("Puppy()"); } }
    ''', out='''
        Animal()
        Dog()
        Puppy()
    ''')
    yield note("Each constructor implicitly starts with `super()`, so construction runs top-down: `Object` → `Animal` → `Dog` → `Puppy`. The parent part of the object is always ready before the child's constructor body runs.")
    yield section("No multiple inheritance of classes", "ban")
    yield snippet("java", r'''
        class A { }
        class B { }
        class C extends A, B { }
    ''', fails=True)
    yield output('''
        Main.java:3: error: '{' expected
        class C extends A, B { }
                         ^
    ''', "javac")
    yield section("IS-A vs HAS-A: prefer composition", "puzzle")
    yield cards(
        ("IS-A (inheritance)", "`Car extends Vehicle`. Tight coupling: the child depends on the parent's implementation details and is fixed at compile time.", "hierarchy"),
        ("HAS-A (composition)", "`Car` *has an* `Engine` field. Loose coupling: swap the part, test it alone, reuse it anywhere.", "puzzle"),
    )
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            public static void main(String[] args) {
                CountingBag viaInheritance = new CountingBag();
                viaInheritance.addAll(List.of("a", "b", "c"));
                System.out.println("inheritance count = " + viaInheritance.added);

                CountingWrapper viaComposition = new CountingWrapper();
                viaComposition.addAll(List.of("a", "b", "c"));
                System.out.println("composition count = " + viaComposition.added);
            }
        }

        class Bag {                                   // a parent you don't control
            private final List<String> items = new ArrayList<>();
            void add(String s) { items.add(s); }
            void addAll(List<String> c) { for (String s : c) add(s); }   // self-use: calls add()
        }

        class CountingBag extends Bag {               // IS-A: counts every item twice
            int added;
            @Override void add(String s) { added++; super.add(s); }
            @Override void addAll(List<String> c) { added += c.size(); super.addAll(c); }
        }

        class CountingWrapper {                       // HAS-A: forwards to a private Bag
            private final Bag bag = new Bag();
            int added;
            void add(String s) { added++; bag.add(s); }
            void addAll(List<String> c) { added += c.size(); bag.addAll(c); }
        }
    ''', out='''
        inheritance count = 6
        composition count = 3
    ''')
    yield warn("Extending a class you don't control ties you to its self-use patterns (the *fragile base class* problem). *Effective Java*: “Favor composition over inheritance” — inherit only when there is a true IS-A relationship and the parent was designed for extension.")
    yield qa("Why doesn't Java support multiple inheritance of classes?",
             "To avoid the diamond problem: if `C extends A, B` and both define `m()` or a field `x`, which one does `C` get? Java allows multiple *interface* inheritance instead, where conflicts must be resolved explicitly and there is no instance state to duplicate.")
    yield qa("Are private members inherited?",
             "They are part of the subclass object's memory, but not *inherited* as members: the subclass can't name or access them. It reaches them only through inherited non-private methods.")
    yield qa("What is the superclass of every class?",
             "`java.lang.Object`. A class with no `extends` clause implicitly extends `Object`, which provides `equals`, `hashCode`, `toString`, `getClass`, `wait`/`notify` and more.")


@topic(G, "overriding-vs-overloading", "Method Overriding vs Overloading", "arrows-exchange")
def _():
    yield lead("Overloading = same name, different parameters, chosen at compile time. Overriding = same signature in a subclass, chosen at runtime.")
    yield section("Side by side", "table")
    yield table(
        ["", "Overloading", "Overriding"],
        ["Where", "Same class (or inherited)", "Subclass redefines a superclass/interface method"],
        ["Signature", "Same name, **different parameter list**", "Same name **and** same parameters"],
        ["Return type", "Anything", "Same or a subtype (*covariant*)"],
        ["Access", "Anything", "Same or **wider**"],
        ["Checked exceptions", "Anything", "Same, narrower or none — never new/broader"],
        ["Resolved", "Compile time (static binding)", "Runtime (dynamic dispatch)"],
        ["`static` / `private` / `final`", "Can be overloaded", "Cannot be overridden"],
        ["Polymorphism kind", "Compile-time", "Runtime"],
    )
    yield section("Overloading", "copy")
    yield snippet("java", r'''
        public class Main {
            static String show(int x)          { return "int " + x; }
            static String show(long x)         { return "long " + x; }
            static String show(double x)       { return "double " + x; }
            static String show(Integer x)      { return "Integer " + x; }
            static String show(Object x)       { return "Object " + x; }
            static String show(int... xs)      { return "varargs " + xs.length; }

            public static void main(String[] args) {
                byte b = 5;
                System.out.println(show(7));        // exact match
                System.out.println(show(b));        // widening byte → int beats boxing
                System.out.println(show(7L));
                System.out.println(show(7.0f));     // float → double
                System.out.println(show("hi"));     // String → Object
                System.out.println(show());         // only varargs fits
            }
        }
    ''', out='''
        int 7
        int 5
        long 7
        double 7.0
        Object hi
        varargs 0
    ''')
    yield note("Overload resolution picks the most specific method in three phases: (1) exact/widening, (2) boxing/unboxing, (3) varargs. The return type alone never distinguishes overloads.")
    yield section("Overriding with `@Override`", "replace")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Shape s = new Circle(2);           // reference type Shape, object Circle
                System.out.println(s.name());      // runtime: Circle.name()
                Circle copy = new Circle(2).copy();   // covariant return: no cast needed
                System.out.printf("%.2f%n", copy.area());
            }
        }

        class Shape {
            protected String name() { return "shape"; }
            Shape copy() { return new Shape(); }
            double area() { return 0; }
        }

        class Circle extends Shape {
            private final double r;
            Circle(double r) { this.r = r; }

            @Override public String name() { return "circle"; }        // protected → public: widening OK
            @Override Circle copy() { return new Circle(r); }          // covariant return type
            @Override double area() { return Math.PI * r * r; }
        }
    ''', out='''
        circle
        12.57
    ''')
    yield warn("Always write `@Override`. Without it, a typo or wrong parameter type silently creates an *overload* instead — e.g. `public boolean equals(Point p)` does not override `equals(Object)`.")
    yield snippet("java", r'''
        class Point {
            int x;
            @Override
            public boolean equals(Point other) { return other.x == x; }   // wrong parameter type
        }
    ''', fails=True)
    yield output('''
        Main.java:3: error: method does not override or implement a method from a supertype
            @Override
            ^
    ''', "javac")
    yield section("Rules the compiler enforces", "gavel")
    yield snippet("java", r'''
        import java.io.IOException;

        class Parent {
            public void run() { }
            void load() throws IOException { }
        }

        class Child extends Parent {
            @Override protected void run() { }   // narrowing public → protected
        }
    ''', fails=True)
    yield output('''
        Main.java:9: error: run() in Child cannot override run() in Parent
            @Override protected void run() { }   // narrowing public → protected
                                     ^
          attempting to assign weaker access privileges; was public
    ''', "javac")
    yield ul(
        "An override **may** throw fewer or narrower checked exceptions (`FileNotFoundException` instead of `IOException`), or none; unchecked exceptions are unrestricted.",
        "`final` methods can't be overridden; `private` methods aren't inherited, so a same-named subclass method is just a new method.",
        "Call the parent version with `super.method()`.",
    )
    yield section("Static methods are hidden, not overridden", "eye-off")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Parent p = new Child();
                System.out.println(p.stat());      // static: chosen by reference type
                System.out.println(p.inst());      // instance: chosen by object type
                System.out.println(p.label);       // fields are hidden too
                System.out.println(((Child) p).label);
            }
        }

        class Parent {
            String label = "parent-field";
            static String stat() { return "Parent.stat"; }
            String inst() { return "Parent.inst"; }
        }

        class Child extends Parent {
            String label = "child-field";
            static String stat() { return "Child.stat"; }
            @Override String inst() { return "Child.inst"; }
        }
    ''', out='''
        Parent.stat
        Child.inst
        parent-field
        child-field
    ''')
    yield qa("Can we overload `main`?",
             "Yes — any number of `main` overloads may exist, but the JVM only launches `public static void main(String[] args)`.")
    yield qa("Can we override a static or private method?",
             "No. A static method with the same signature *hides* the parent's (resolved by reference type at compile time). A private method isn't visible to the subclass, so a same-named method is a brand-new method.")
    yield qa("Can two overloads differ only by return type?",
             "No. The call `f(1)` wouldn't tell the compiler which one you want, so it's a compile error (`method f(int) is already defined`).")
    yield qa("What is a covariant return type?",
             "An overriding method may return a *subtype* of the parent method's return type — e.g. `Circle copy()` overriding `Shape copy()` — so callers need no cast. `clone()` overrides commonly use it.")


@topic(G, "polymorphism", "Polymorphism & Dynamic Dispatch", "arrows-split")
def _():
    yield lead("One reference type, many behaviours: the JVM picks the overriding method of the *actual object* at runtime.")
    yield define("Polymorphism", "“many forms” — code written against a supertype works with any subtype. Java has **compile-time** polymorphism (overloading) and **runtime** polymorphism (overriding + dynamic dispatch).")
    yield section("Runtime polymorphism", "player-play")
    yield snippet("java", r'''
        import java.util.List;

        public class Main {
            public static void main(String[] args) {
                List<Payment> payments = List.of(new Card(100), new Upi(250), new Cash(40));
                double total = 0;
                for (Payment p : payments) {             // one loop, three behaviours
                    System.out.println(p.describe());
                    total += p.fee();
                }
                System.out.println("total fees = " + total);
            }
        }

        abstract class Payment {
            protected final double amount;
            Payment(double amount) { this.amount = amount; }
            abstract double fee();
            String describe() { return getClass().getSimpleName() + " " + amount + " fee " + fee(); }
        }

        class Card extends Payment { Card(double a) { super(a); } double fee() { return amount * 0.02; } }
        class Upi  extends Payment { Upi(double a)  { super(a); } double fee() { return 0; } }
        class Cash extends Payment { Cash(double a) { super(a); } double fee() { return 1; } }
    ''', out='''
        Card 100.0 fee 2.0
        Upi 250.0 fee 0.0
        Cash 40.0 fee 1.0
        total fees = 3.0
    ''')
    yield note("Adding a new payment type needs **no change** to the loop — that is the Open/Closed Principle in action, and why polymorphism beats `if (type == ...)` chains.")
    yield section("Static type vs runtime type", "code-dots")
    yield table(
        ["Question", "Decided by", "When"],
        ["Which methods may I *call*?", "Reference (static) type", "Compile time"],
        ["Which overload is chosen?", "Static types of the arguments", "Compile time"],
        ["Which override *runs*?", "Runtime class of the object", "Runtime (dynamic dispatch)"],
        ["Which field is read?", "Reference type — fields are not polymorphic", "Compile time"],
        ["Which static method runs?", "Reference type", "Compile time"],
    )
    yield section("How dynamic dispatch works", "cpu")
    yield steps(
        ("Compile", "`javac` checks the method exists on the static type and emits `invokevirtual Shape.area()` (or `invokeinterface`)."),
        ("Look up", "At runtime the JVM reads the object's actual class and finds `area` in its **method table** (vtable) — the most specific override."),
        ("Optimise", "The JIT often *inlines* the call when only one implementation has been seen (monomorphic call site), so polymorphism is usually free."),
    )
    yield section("Upcasting and downcasting", "arrows-up-down")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Animal a = new Dog();              // upcast: implicit, always safe
                a.speak();
                // a.fetch();                      // error: Animal has no fetch()

                if (a instanceof Dog d) {          // pattern matching (Java 16+): test + cast
                    d.fetch();
                }
                Dog d2 = (Dog) a;                  // explicit downcast: checked at runtime
                d2.fetch();

                Animal c = new Cat();
                try {
                    Dog wrong = (Dog) c;           // compiles, fails at runtime
                    wrong.fetch();
                } catch (ClassCastException e) {
                    System.out.println("ClassCastException");
                }
            }
        }

        class Animal { void speak() { System.out.println("..."); } }
        class Dog extends Animal {
            @Override void speak() { System.out.println("Woof"); }
            void fetch() { System.out.println("fetching"); }
        }
        class Cat extends Animal { @Override void speak() { System.out.println("Meow"); } }
    ''', out='''
        Woof
        fetching
        fetching
        ClassCastException
    ''')
    yield warn("A downcast is a promise to the compiler. If the object isn't really of that type you get `ClassCastException` at runtime — guard with `instanceof` (ideally the pattern form `if (x instanceof Dog d)`), or better, redesign so an overridden method does the work.")
    yield section("Overloading is decided at compile time", "alert-triangle")
    yield snippet("java", r'''
        public class Main {
            static String greet(Object o) { return "object"; }
            static String greet(String s) { return "string"; }

            public static void main(String[] args) {
                Object o = "hello";            // runtime type String, static type Object
                System.out.println(greet(o));  // overload chosen from the STATIC type
                System.out.println(greet("hello"));
                System.out.println(o.toString().length());   // override chosen at runtime
            }
        }
    ''', out='''
        object
        string
        5
    ''')
    yield qa("What is dynamic method dispatch?",
             "The mechanism by which a call to an overridden method through a superclass reference is resolved at runtime, using the actual object's class. It is how runtime polymorphism is implemented (via method tables).")
    yield qa("Are fields polymorphic?",
             "No. A field access is resolved from the reference's static type. If a subclass declares a field with the same name it *hides* the parent's; `parentRef.x` still reads the parent's field. Access state through methods instead.")
    yield qa("Can you achieve polymorphism without inheritance?",
             "Yes, via interfaces: unrelated classes implementing the same interface can be used interchangeably. Overloading and generics are other (compile-time) forms.")


@topic(G, "abstract-classes", "Abstract Classes", "shape")
def _():
    yield lead("An `abstract` class is a partial implementation: it can hold state, constructors and concrete methods, but leaves some methods for subclasses to fill in.")
    yield define("Abstract class", "a class declared `abstract` that **cannot be instantiated**. It may declare `abstract` methods (no body) that every concrete subclass must implement.")
    yield section("Rules", "gavel")
    yield ul(
        "A class with at least one abstract method **must** be declared `abstract` (an abstract class may also have none).",
        "It can have constructors (called via `super(...)`), instance fields, static members, `final` and `private` methods.",
        "A concrete subclass must implement *all* inherited abstract methods, or be `abstract` itself.",
        "`abstract` can't be combined with `final`, `static` or `private` on a method — those can't be overridden.",
    )
    yield snippet("java", r'''
        abstract class Shape {
            abstract double area();
        }

        public class Main {
            public static void main(String[] args) {
                Shape s = new Shape();
            }
        }
    ''', fails=True)
    yield output('''
        Main.java:7: error: Shape is abstract; cannot be instantiated
                Shape s = new Shape();
                          ^
    ''', "javac")
    yield section("Template method pattern", "template")
    yield p("The abstract class fixes the *algorithm skeleton* in a `final` method and lets subclasses supply the varying steps.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                new CsvReport().generate();
                new JsonReport().generate();
            }
        }

        abstract class Report {
            private final String title;
            protected Report(String title) { this.title = title; }   // abstract classes have constructors

            // template method: fixed order, cannot be overridden
            public final void generate() {
                System.out.println("== " + title + " ==");
                System.out.println(header());
                System.out.println(body());
                footer();
            }

            protected abstract String header();       // required steps
            protected abstract String body();
            protected void footer() { System.out.println("-- end --"); }   // optional hook
        }

        class CsvReport extends Report {
            CsvReport() { super("CSV"); }
            @Override protected String header() { return "name,score"; }
            @Override protected String body() { return "asha,91"; }
        }

        class JsonReport extends Report {
            JsonReport() { super("JSON"); }
            @Override protected String header() { return "{"; }
            @Override protected String body() { return "  \"asha\": 91\n}"; }
            @Override protected void footer() { }                             // override the hook
        }
    ''', out='''
        == CSV ==
        name,score
        asha,91
        -- end --
        == JSON ==
        {
          "asha": 91
        }
    ''')
    yield section("Anonymous subclass of an abstract class", "user-question")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Greeter g = new Greeter("Asha") {          // anonymous concrete subclass
                    @Override String greeting() { return "Namaste"; }
                };
                System.out.println(g.greet());
            }
        }

        abstract class Greeter {
            private final String name;
            Greeter(String name) { this.name = name; }
            abstract String greeting();
            String greet() { return greeting() + ", " + name + "!"; }
        }
    ''', out="Namaste, Asha!")
    yield section("When to choose an abstract class", "checklist")
    yield cards(
        ("Use an abstract class when…", "Subclasses are closely related and share **state** or constructor logic; you want `protected` helpers or a fixed template method.", "check"),
        ("Use an interface when…", "You define a *capability* unrelated classes can have (`Comparable`, `Runnable`), or need a type to have several such capabilities.", "plug"),
    )
    yield qa("Can an abstract class have a constructor? Why?",
             "Yes. It can't be called with `new` directly, but subclasses call it via `super(...)` to initialise the fields the abstract class declares.")
    yield qa("Can an abstract class have no abstract methods?",
             "Yes — marking it `abstract` simply prevents instantiation (e.g. `HttpServlet` had none historically). It signals *extend me, don't use me directly*.")
    yield qa("Can an abstract method be `private`, `static` or `final`?",
             "No. An abstract method must be overridden; `private` methods aren't inherited, `static` methods are hidden not overridden, and `final` forbids overriding.")


@topic(G, "interfaces", "Interfaces", "plug")
def _():
    yield lead("An interface is a contract of methods a class promises to provide. A class can implement many interfaces — Java's answer to multiple inheritance.")
    yield define("Interface", "a reference type declaring abstract methods (plus, since Java 8, `default` and `static` methods, and since Java 9, `private` methods). Fields are implicitly `public static final` constants.")
    yield section("What an interface can contain", "list-details")
    yield table(
        ["Member", "Implicit modifiers", "Since"],
        ["Abstract method", "`public abstract`", "1.0"],
        ["Constant field", "`public static final`", "1.0"],
        ["`default` method (has a body, inherited)", "`public`", "8"],
        ["`static` method (called on the interface only)", "`public`", "8"],
        ["`private` / `private static` helper method", "—", "9"],
        ["Nested types", "`public static`", "1.0"],
    )
    yield section("Implementing several interfaces", "code")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            public static void main(String[] args) {
                Duck duck = new Duck();
                List<Swimmer> swimmers = new ArrayList<>(List.of(duck, new Fish()));
                for (Swimmer s : swimmers) s.swim();
                Flyer f = duck;                     // a Duck is also a Flyer
                f.fly();
                System.out.println(Flyer.MAX_ALTITUDE);
                System.out.println(duck instanceof Swimmer && duck instanceof Flyer);
            }
        }

        interface Swimmer { void swim(); }
        interface Flyer {
            int MAX_ALTITUDE = 10_000;              // public static final
            void fly();
        }

        class Duck implements Swimmer, Flyer {
            public void swim() { System.out.println("duck paddles"); }   // must be public
            public void fly()  { System.out.println("duck flies"); }
        }

        class Fish implements Swimmer {
            public void swim() { System.out.println("fish swims"); }
        }
    ''', out='''
        duck paddles
        fish swims
        duck flies
        10000
        true
    ''')
    yield section("Default, static and private methods", "sparkles")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Greeter en = name -> "Hello, " + name;    // one abstract method → lambda works
                System.out.println(en.greet("Asha"));
                System.out.println(en.greetLoudly("Ravi"));      // default method
                System.out.println(Greeter.polite().greet("Meera"));   // static factory
            }
        }

        interface Greeter {
            String greet(String name);                  // abstract

            default String greetLoudly(String name) {   // inherited, can be overridden
                return shout(greet(name));
            }

            static Greeter polite() {                   // Greeter.polite(), not inherited by implementers
                return name -> "Good evening, " + name;
            }

            private String shout(String s) {            // helper shared by default methods
                return s.toUpperCase() + "!";
            }
        }
    ''', out='''
        Hello, Asha
        HELLO, RAVI!
        Good evening, Meera
    ''')
    yield note("Default methods exist so interfaces can **evolve**: Java 8 added `forEach`, `stream()`, `removeIf` to `Collection`/`Iterable` without breaking millions of existing implementations.")
    yield section("The diamond problem with default methods", "diamond")
    yield p("If a class inherits the same default method from two interfaces, it must override it and may pick one with `Interface.super.method()`. Rules: (1) a class method always wins over an interface default; (2) a more specific sub-interface wins; (3) otherwise you must resolve it yourself.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(new Phone().start());
            }
        }

        interface Camera { default String start() { return "camera on"; } }
        interface Radio  { default String start() { return "radio on"; } }

        class Phone implements Camera, Radio {
            @Override public String start() {           // required: otherwise compile error
                return Camera.super.start() + " + " + Radio.super.start();
            }
        }
    ''', out="camera on + radio on")
    yield snippet("java", r'''
        interface Camera { default String start() { return "camera on"; } }
        interface Radio  { default String start() { return "radio on"; } }
        class Phone implements Camera, Radio { }
    ''', fails=True)
    yield output('''
        Main.java:3: error: types Camera and Radio are incompatible;
        class Phone implements Camera, Radio { }
        ^
          class Phone inherits unrelated defaults for start() from types Camera and Radio
    ''', "javac")
    yield section("Abstract class vs interface", "arrows-diff")
    yield table(
        ["", "Abstract class", "Interface"],
        ["Instance state (fields)", "Yes", "No — only `public static final` constants"],
        ["Constructors", "Yes", "No"],
        ["Multiple inheritance", "No — `extends` one class", "Yes — `implements` many"],
        ["Method bodies", "Any", "`default`, `static`, `private` only"],
        ["Member access", "Any modifier", "`public` (or `private` helpers)"],
        ["Relationship", "IS-A (shared identity)", "CAN-DO (capability)"],
        ["Lambda target", "No", "Yes, if exactly one abstract method (functional interface)"],
    )
    yield section("Marker and functional interfaces", "tag")
    yield cards(
        ("Marker interface", "No methods at all; tags a class for special treatment: `Serializable`, `Cloneable`, `RandomAccess`. Modern code often uses annotations instead.", "bookmark"),
        ("Functional interface", "Exactly one abstract method, so a lambda or method reference can implement it: `Runnable`, `Comparator`, `Function`. Mark with `@FunctionalInterface`.", "lambda"),
    )
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.LinkedList;
        import java.util.List;
        import java.util.RandomAccess;

        public class Main {
            static String strategy(List<?> list) {
                return list instanceof RandomAccess ? "index loop" : "iterator";
            }

            public static void main(String[] args) {
                System.out.println(strategy(new ArrayList<>()));
                System.out.println(strategy(new LinkedList<>()));
            }
        }
    ''', out='''
        index loop
        iterator
    ''')
    yield qa("Why were default methods added in Java 8?",
             "For backward-compatible interface evolution: new methods (like `Collection.stream()`) could be added with a body so existing implementing classes kept compiling. They also let interfaces offer convenience methods (`Comparator.reversed()`).")
    yield qa("Can an interface have a constructor or instance fields?",
             "No. Interfaces carry no per-object state; any field is implicitly `public static final`. That is exactly why multiple interface inheritance is safe.")
    yield qa("Can an interface extend another interface? A class?",
             "An interface can `extend` any number of interfaces (`interface C extends A, B`). It can never extend a class.")
    yield qa("If a class and an interface both provide the same method, which wins?",
             "The class. “Class wins” — a concrete (or inherited superclass) method always takes precedence over an interface default method.")
