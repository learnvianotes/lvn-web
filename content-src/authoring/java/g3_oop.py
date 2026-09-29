from kit import *

G = "OOP Fundamentals"


@topic(G, "classes-objects", "Classes & Objects", "box")
def _():
    yield lead("A *class* is a blueprint that bundles state (fields) and behaviour (methods); an *object* is one instance of it living on the heap.")
    yield define("Class", "a user-defined type that declares **fields** (what each object knows) and **methods** (what each object can do).")
    yield define("Object", "a concrete instance created with `new`. It has its own copy of every instance field and lives on the heap until no reference points to it.")
    yield section("The four pillars of OOP", "building")
    yield cards(
        ("Encapsulation", "Hide state behind methods; the class controls how its data changes.", "lock"),
        ("Abstraction", "Expose *what* an object does, not *how* — abstract classes and interfaces.", "eye-off"),
        ("Inheritance", "A subclass reuses and extends a superclass (`extends`).", "hierarchy"),
        ("Polymorphism", "One reference type, many runtime behaviours — overriding + dynamic dispatch.", "arrows-split"),
    )
    yield section("Declaring a class and creating objects", "code")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                BankAccount a = new BankAccount("Asha", 500);
                BankAccount b = new BankAccount("Ravi", 100);
                a.deposit(250);
                b.withdraw(30);
                System.out.println(a.describe());
                System.out.println(b.describe());
                System.out.println("accounts opened: " + BankAccount.count);
            }
        }

        class BankAccount {
            String owner;          // instance field: one copy per object
            double balance;
            static int count = 0;  // static field: one copy per class

            BankAccount(String owner, double balance) {   // constructor
                this.owner = owner;
                this.balance = balance;
                count++;
            }

            void deposit(double amount) { balance += amount; }
            void withdraw(double amount) { balance -= amount; }
            String describe() { return owner + " has " + balance; }
        }
    ''', out='''
        Asha has 750.0
        Ravi has 70.0
        accounts opened: 2
    ''')
    yield section("What `new` does", "sparkles")
    yield steps(
        ("Load the class", "If `BankAccount` isn't loaded yet, the class loader loads, links and initialises it (static fields/blocks run once)."),
        ("Allocate", "Memory for the object is reserved on the heap; every field gets its default value (`0`, `false`, `null`)."),
        ("Initialise", "Field initialisers and instance initializer blocks run, then the constructor body."),
        ("Return a reference", "`new` evaluates to a reference (think: a safe pointer) that is stored in the variable."),
    )
    yield section("References, not objects, live in variables", "link")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Point p1 = new Point();
                p1.x = 1;
                Point p2 = p1;          // copies the reference, not the object
                p2.x = 99;
                System.out.println(p1.x);        // same object
                System.out.println(p1 == p2);    // same reference?

                Point p3 = new Point();
                p3.x = 99;
                System.out.println(p1 == p3);    // different objects

                Point nothing = null;
                System.out.println(nothing == null);
            }
        }

        class Point { int x, y; }
    ''', out='''
        99
        true
        false
        true
    ''')
    yield section("Default values of fields", "list")
    yield table(
        ["Field type", "Default"],
        ["`byte`, `short`, `int`, `long`", "`0`"],
        ["`float`, `double`", "`0.0`"],
        ["`char`", "`'\\u0000'`"],
        ["`boolean`", "`false`"],
        ["Any reference (`String`, arrays, objects)", "`null`"],
    )
    yield warn("Only **fields** get defaults. Local variables have none — using one before assigning it is a compile error (`variable x might not have been initialized`).")
    yield section("Instance vs class members", "table")
    yield table(
        ["", "Instance member", "Static (class) member"],
        ["Belongs to", "each object", "the class itself"],
        ["Copies", "one per object", "exactly one"],
        ["Accessed via", "`obj.field`", "`ClassName.field`"],
        ["Can use `this`?", "Yes", "No"],
    )
    yield qa("What is the difference between a class and an object?",
             "A class is a compile-time blueprint (a type); an object is a runtime instance of that type on the heap. One class, many objects — each with its own instance fields.")
    yield qa("Is `p2 = p1` a copy of the object?",
             "No. It copies the *reference*. Both variables point to the same object, so a change through one is visible through the other. To copy, write a copy constructor or factory (`new Point(p1)`).")
    yield qa("Where do objects and references live?",
             "Objects live on the heap. A local reference variable lives in the method's stack frame; a reference stored in a field lives inside its owning object on the heap.")


@topic(G, "constructors", "Constructors & Initialization Order", "hammer")
def _():
    yield lead("A constructor initialises a new object. Java runs static setup once per class and then a fixed sequence for every `new`.")
    yield define("Constructor", "a special member with the class's name and **no return type** that runs when `new` creates an object. It is not inherited and cannot be `static`, `final` or `abstract`.")
    yield section("Kinds of constructors", "list-details")
    yield table(
        ["Kind", "What it is"],
        ["**Default**", "Added by the compiler *only if you write no constructor at all*: no args, calls `super()`."],
        ["**No-arg**", "One you write yourself with no parameters."],
        ["**Parameterized**", "Takes arguments to set up state."],
        ["**Copy**", "Takes another instance of the same class: `Point(Point other)` (Java has no built-in copy constructor)."],
        ["**Private**", "Prevents outside `new` — singletons, factories, utility classes."],
    )
    yield section("Overloading and chaining with `this(...)`", "link")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(new Pizza());
                System.out.println(new Pizza("large"));
                System.out.println(new Pizza("small", 3));
            }
        }

        class Pizza {
            private final String size;
            private final int toppings;

            Pizza() { this("medium"); }                 // delegates
            Pizza(String size) { this(size, 1); }       // delegates
            Pizza(String size, int toppings) {          // the one "real" constructor
                this.size = size;
                this.toppings = toppings;
            }

            @Override public String toString() { return size + " pizza, " + toppings + " topping(s)"; }
        }
    ''', out='''
        medium pizza, 1 topping(s)
        large pizza, 1 topping(s)
        small pizza, 3 topping(s)
    ''')
    yield note("`this(...)` or `super(...)` must be the **first statement** of a constructor, and you can use only one of them. If you write neither, the compiler inserts `super()`.")
    yield warn("Writing *any* constructor removes the free default one. `class A { A(int x) {} }` means `new A()` no longer compiles — a common surprise with frameworks (JPA, Jackson) that need a no-arg constructor.")
    yield section("Initializer blocks", "brackets")
    yield cards(
        ("Static initializer `static { … }`", "Runs **once**, when the class is initialised (first active use). For complex static setup.", "bolt"),
        ("Instance initializer `{ … }`", "Runs on **every** `new`, before the constructor body — the compiler copies it into each constructor after `super()`.", "refresh"),
    )
    yield section("The full initialization order", "sort-ascending")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println("-- first new Child()");
                new Child();
                System.out.println("-- second new Child()");
                new Child();
            }
        }

        class Parent {
            static { System.out.println("1. Parent static block"); }
            { System.out.println("3. Parent instance block"); }
            Parent() { System.out.println("4. Parent constructor"); }
        }

        class Child extends Parent {
            static { System.out.println("2. Child static block"); }
            private String name = init();
            { System.out.println("6. Child instance block"); }
            Child() { System.out.println("7. Child constructor"); }

            private String init() { System.out.println("5. Child field initializer"); return "child"; }
        }
    ''', out='''
        -- first new Child()
        1. Parent static block
        2. Child static block
        3. Parent instance block
        4. Parent constructor
        5. Child field initializer
        6. Child instance block
        7. Child constructor
        -- second new Child()
        3. Parent instance block
        4. Parent constructor
        5. Child field initializer
        6. Child instance block
        7. Child constructor
    ''')
    yield steps(
        ("Static, parent first", "Superclass static fields/blocks, then subclass static fields/blocks — once per class, in textual order."),
        ("Parent instance part", "`super(...)` runs first: parent field initialisers + instance blocks (textual order), then parent constructor body."),
        ("Child instance part", "Child field initialisers + instance blocks in textual order, then the child constructor body."),
    )
    yield section("Pitfall: calling an overridable method from a constructor", "alert-triangle")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                new Sub();
            }
        }

        class Base {
            Base() { describe(); }            // dynamic dispatch — calls Sub.describe()
            void describe() { System.out.println("Base"); }
        }

        class Sub extends Base {
            private String label = "ready";
            @Override void describe() { System.out.println("Sub label = " + label); }
        }
    ''', out="Sub label = null")
    yield warn("The subclass override runs *before* the subclass's fields are initialised, so it sees `null`/`0`. Never call overridable methods from a constructor — make them `private` or `final`.")
    yield qa("Can a constructor be private? Why would you do that?",
             "Yes. It stops other classes from calling `new` — used for singletons, static factory methods (`List.of`), and utility classes like `Math` or `Collections`.")
    yield qa("Is a constructor inherited? Can it be overridden?",
             "Neither. Constructors are not members that are inherited, so they cannot be overridden. A subclass must call a superclass constructor (implicitly `super()` or explicitly `super(args)`).")
    yield qa("Can a constructor return a value or be `final`/`static`?",
             "No return type at all (writing `void` turns it into an ordinary method with the class's name!). It cannot be `static`, `final`, `abstract` or `synchronized`.")
    yield qa("In what order do static blocks, instance blocks and constructors run?",
             "Static blocks: once per class, parent before child. Then for each `new`: parent instance initialisers → parent constructor → child instance initialisers (fields and blocks in source order) → child constructor.")


@topic(G, "this-super", "this & super", "arrow-up")
def _():
    yield lead("`this` refers to the current object; `super` refers to the superclass part of the current object.")
    yield section("Uses of `this`", "pointer")
    yield table(
        ["Use", "Example", "Why"],
        ["Disambiguate a field from a parameter", "`this.name = name;`", "Parameter shadows the field"],
        ["Call another constructor", "`this(name, 0);`", "Constructor chaining — first statement only"],
        ["Pass the current object", "`registry.add(this);`", "Callbacks, listeners"],
        ["Return the current object", "`return this;`", "Fluent / builder APIs"],
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Counter c = new Counter().add(5).add(10).add(-3);   // chaining via return this
                System.out.println(c.total);
            }
        }

        class Counter {
            int total;
            Counter add(int total) {
                this.total += total;   // this.total = field, total = parameter
                return this;
            }
        }
    ''', out="12")
    yield section("Uses of `super`", "arrow-big-up")
    yield table(
        ["Use", "Example"],
        ["Call a superclass constructor", "`super(name);` — first statement of the constructor"],
        ["Call the overridden superclass method", "`super.describe()`"],
        ["Access a hidden superclass field", "`super.name` (when the subclass declares a field with the same name)"],
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Manager m = new Manager("Asha", 3);
                System.out.println(m.describe());
                m.showNames();
            }
        }

        class Employee {
            protected String name;
            String kind = "employee";
            Employee(String name) { this.name = name; }
            String describe() { return name + " (" + kind + ")"; }
        }

        class Manager extends Employee {
            private final int reports;
            String kind = "manager";                   // hides Employee.kind

            Manager(String name, int reports) {
                super(name);                           // must come first
                this.reports = reports;
            }

            @Override String describe() {
                return super.describe() + " manages " + reports;   // reuse parent logic
            }

            void showNames() {
                System.out.println(this.kind + " / " + super.kind);
            }
        }
    ''', out='''
        Asha (employee) manages 3
        manager / employee
    ''')
    yield note("`Employee.describe()` prints *employee* — fields are **not** polymorphic, so inside `Employee` the name `kind` always means `Employee.kind`. Avoid hiding fields; it is confusing.")
    yield section("Rules", "gavel")
    yield ul(
        "`this` and `super` cannot be used in a `static` context — there is no current object.",
        "A constructor can start with `this(...)` **or** `super(...)`, never both.",
        "`super.super.method()` is not allowed — you can only reach one level up.",
        "If the superclass has no no-arg constructor, every subclass constructor must call `super(args)` explicitly.",
    )
    yield snippet("java", r'''
        class Animal {
            Animal(String name) { }
        }

        class Dog extends Animal {
            Dog() { }   // implicit super() — but Animal has no no-arg constructor
        }
    ''', fails=True)
    yield output('''
        Main.java:6: error: constructor Animal in class Animal cannot be applied to given types;
            Dog() { }   // implicit super() — but Animal has no no-arg constructor
                  ^
          required: String
          found:    no arguments
          reason: actual and formal argument lists differ in length
    ''', "javac")
    yield qa("Why can't `this` be used inside a static method?",
             "A static method belongs to the class and runs without any instance, so there is no current object for `this` (or `super`) to refer to.")
    yield qa("What happens if you don't call `super(...)` in a constructor?",
             "The compiler inserts `super()` as the first statement. If the parent has no accessible no-arg constructor, compilation fails.")


@topic(G, "static-keyword", "The static Keyword", "bolt")
def _():
    yield lead("`static` members belong to the class, not to any object: one copy, shared by all instances, usable without `new`.")
    yield section("Where `static` can appear", "list")
    yield table(
        ["On", "Meaning", "Typical use"],
        ["Field", "One copy per class (in the class's data, not in each object)", "Counters, constants (`static final`), caches"],
        ["Method", "Called on the class; no `this`", "Utilities (`Math.max`), factories (`List.of`)"],
        ["Block `static { }`", "Runs once when the class is initialised", "Complex static setup"],
        ["Nested class", "A class inside a class that needs no outer instance", "Builders, helper types, `Map.Entry`"],
        ["Import", "`import static java.lang.Math.*;`", "Use `sqrt(x)` without the class name"],
    )
    yield section("Static field vs instance field", "code")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                User a = new User("asha");
                User b = new User("ravi");
                User c = new User("meera");
                System.out.println(a.id + " " + b.id + " " + c.id);
                System.out.println("users created: " + User.created);
                System.out.println(User.isValidName("x"));   // static method: no object needed
            }
        }

        class User {
            static int created = 0;   // shared by all Users
            final int id;             // each User has its own
            final String name;

            User(String name) {
                this.name = name;
                this.id = ++created;
            }

            static boolean isValidName(String s) {
                // return name.length() > 1;   // would not compile: no 'this' in a static method
                return s.length() > 1;
            }
        }
    ''', out='''
        1 2 3
        users created: 3
        false
    ''')
    yield section("What a static method can and cannot touch", "lock")
    yield cards(
        ("Can", "Other static fields and methods directly; instance members *through an object reference* (`u.name`).", "check"),
        ("Cannot", "Instance fields/methods directly, `this`, `super`. Static methods are also not polymorphic — they are *hidden*, not overridden.", "x"),
    )
    yield section("Static blocks and lazy initialisation", "bolt")
    yield snippet("java", r'''
        import java.util.Map;

        public class Main {
            public static void main(String[] args) {
                System.out.println("main starts");
                System.out.println(Codes.lookup("IN"));
                System.out.println(Codes.lookup("JP"));
            }
        }

        class Codes {
            private static final Map<String, String> NAMES;
            static {
                System.out.println("Codes initialised");   // runs on first use, once
                NAMES = Map.of("IN", "India", "JP", "Japan");
            }
            static String lookup(String code) { return NAMES.get(code); }
        }
    ''', out='''
        main starts
        Codes initialised
        India
        Japan
    ''')
    yield note("A class is initialised lazily, on its **first active use** (creating an instance, calling a static method, reading a non-constant static field). That is what makes the *holder idiom* singleton lazy and thread-safe.")
    yield section("Why is `main` static?", "help")
    yield p("The JVM must call `main` before any object of your class exists. Making it `static` lets the launcher invoke `Main.main(args)` directly on the class without having to choose a constructor.")
    yield section("Static nested class", "stack")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Order.Line line = new Order.Line("pen", 3);   // no Order instance needed
                System.out.println(line.item() + " x" + line.qty());
            }
        }

        class Order {
            record Line(String item, int qty) { }   // nested records/enums/interfaces are implicitly static
        }
    ''', out="pen x3")
    yield warn("Mutable `static` state is global state: it is shared across all threads and tests and never garbage-collected while the class is loaded. Prefer `static final` constants and stateless static helpers.")
    yield qa("Can we override a static method?",
             "No. A static method with the same signature in a subclass *hides* the parent's one. Which version runs is chosen at compile time from the reference type, not the object.")
    yield qa("Can a static method access instance variables?",
             "Not directly — there is no `this`. It can only reach them through an explicit object reference passed in or created inside it.")
    yield qa("When is a static block executed?",
             "Once, when the class is initialised — at its first active use — after the class is loaded and linked. Multiple static blocks run in source order.")


@topic(G, "final-keyword", "The final Keyword", "lock")
def _():
    yield lead("`final` means *cannot be changed after it is set*: a variable can't be reassigned, a method can't be overridden, a class can't be extended.")
    yield section("`final` in three places", "list")
    yield table(
        ["Applied to", "Effect", "Example"],
        ["Variable (local, field, parameter)", "Assigned exactly once", "`final int max = 10;`"],
        ["Method", "Cannot be overridden by subclasses", "`final void audit()`"],
        ["Class", "Cannot be extended", "`String`, `Integer`, all records"],
    )
    yield section("Final variables", "variable")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static final double TAX_RATE = 0.18;         // constant: static final, UPPER_CASE

            public static void main(String[] args) {
                final List<String> names = new ArrayList<>();
                names.add("Asha");                        // OK: the object is mutable
                names.add("Ravi");
                // names = new ArrayList<>();             // error: cannot assign a value to final variable names
                System.out.println(names);

                final int limit;                          // "blank final": assigned once, later
                limit = args.length > 0 ? 5 : 10;
                System.out.println(limit + " " + TAX_RATE);
            }
        }
    ''', out='''
        [Asha, Ravi]
        10 0.18
    ''')
    yield warn("`final` freezes the **reference**, not the object. A `final List` can still be modified; for a truly unchangeable list use `List.of(...)` or `Collections.unmodifiableList(...)`.")
    yield section("Blank finals must be assigned in every constructor", "hammer")
    yield snippet("java", r'''
        class Account {
            private final String id;
            Account(String id) { this.id = id; }
            Account() { }   // forgot to assign id
        }
    ''', fails=True)
    yield output('''
        Main.java:4: error: variable id might not have been initialized
            Account() { }   // forgot to assign id
                        ^
    ''', "javac")
    yield section("Effectively final", "lambda")
    yield p("A local variable that is never reassigned is *effectively final* even without the keyword. Lambdas and anonymous/local classes may only capture effectively final locals.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                int base = 100;                       // never reassigned → effectively final
                Runnable r = () -> System.out.println(base + 1);
                r.run();
            }
        }
    ''', out="101")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                int count = 0;
                Runnable r = () -> System.out.println(count);
                count++;   // makes count NOT effectively final
                r.run();
            }
        }
    ''', fails=True)
    yield output('''
        Main.java:4: error: local variables referenced from a lambda expression must be final or effectively final
                Runnable r = () -> System.out.println(count);
                                                      ^
    ''', "javac")
    yield section("Final methods and classes", "shield-lock")
    yield ul(
        "A `final` method keeps its behaviour fixed in every subclass — good for security-sensitive or template-method steps.",
        "A `final` class cannot be subclassed: `String`, the wrapper classes, `LocalDate`, every `record` and `enum` (without bodies).",
        "`private` methods are implicitly final (they aren't inherited, so nothing can override them).",
        "`abstract` and `final` together are illegal: one demands a subclass, the other forbids it.",
    )
    yield section("final vs finally vs finalize", "arrows-diff")
    yield table(
        ["Keyword", "What it is"],
        ["`final`", "Modifier: no reassignment / overriding / extending."],
        ["`finally`", "Block after `try`/`catch` that always runs (cleanup)."],
        ["`finalize()`", "`Object` method once called by the GC before reclaiming an object — **deprecated for removal** since Java 18; use `try-with-resources` or `Cleaner`."],
    )
    yield qa("Does `final` make an object immutable?",
             "No. It only stops the variable from being reassigned. Immutability needs a design: `final` class, `private final` fields, no setters, defensive copies of mutable parts.")
    yield qa("Why is `String` final?",
             "So no subclass can break its immutability — which the string pool, `hashCode` caching, security checks (file paths, class names) and thread safety all rely on.")
    yield qa("Can a `final` variable be initialised later?",
             "Yes — a *blank final*. A local must be assigned before use; an instance field in every constructor (or an initializer block); a static final in a static block. Exactly once.")


@topic(G, "access-packages", "Access Modifiers & Packages", "shield")
def _():
    yield lead("Packages group related classes into namespaces; access modifiers decide who may see each class and member.")
    yield section("The four access levels", "table")
    yield table(
        ["Modifier", "Same class", "Same package", "Subclass (other package)", "Everywhere"],
        ["`private`", "Yes", "No", "No", "No"],
        ["*(default / package-private)*", "Yes", "Yes", "No", "No"],
        ["`protected`", "Yes", "Yes", "Yes (through inheritance)", "No"],
        ["`public`", "Yes", "Yes", "Yes", "Yes"],
    )
    yield note("Order from most to least restrictive: `private` → default → `protected` → `public`. Start with `private` and widen only when needed.")
    yield section("Where each modifier is allowed", "list")
    yield ul(
        "**Top-level classes**: only `public` or default. A source file may contain at most one `public` top-level class, and the file must be named after it.",
        "**Members** (fields, methods, constructors, nested types): all four.",
        "**Local variables**: no access modifiers at all (only `final`).",
        "**Interface members**: `public` by default; methods may also be `private` (Java 9+).",
    )
    yield section("`private` is per class, not per object", "lock")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Money a = new Money(500);
                Money b = new Money(300);
                System.out.println(a.isMoreThan(b));
                // System.out.println(a.cents);   // error: cents has private access in Money
            }
        }

        class Money {
            private final long cents;
            Money(long cents) { this.cents = cents; }

            boolean isMoreThan(Money other) {
                return this.cents > other.cents;   // OK: other object, same class
            }
        }
    ''', out="true")
    yield section("Packages", "folders")
    yield define("Package", "a namespace that groups related types and maps to a directory: `package com.shop.billing;` lives in `com/shop/billing/`. The fully qualified name is `com.shop.billing.Invoice`.")
    yield shell('''
        src/com/shop/billing/Invoice.java     # package com.shop.billing;
        src/com/shop/app/Main.java            # package com.shop.app;  import com.shop.billing.Invoice;

        $ javac -d out $(find src -name '*.java')
        $ java -cp out com.shop.app.Main
    ''')
    yield ul(
        "Naming: reversed domain, all lowercase — `com.google.common.collect`.",
        "`java.lang` is imported automatically (`String`, `Math`, `Integer`, `System`…).",
        "Sub-packages are **not** related for access: `com.shop` cannot see package-private members of `com.shop.billing`.",
        "Classes without a `package` line are in the *unnamed package* — fine for scripts, never for real projects.",
    )
    yield section("Imports", "file-import")
    yield snippet("java", r'''
        import java.util.*;                        // on-demand: every public type in java.util
        import java.time.LocalDate;                // single-type import (preferred)
        import static java.lang.Math.max;          // static import of one member
        import static java.lang.Math.PI;

        public class Main {
            public static void main(String[] args) {
                List<Integer> nums = new ArrayList<>(List.of(3, 9, 4));
                System.out.println(max(nums.get(0), nums.get(1)));
                System.out.printf("%.2f%n", PI);
                System.out.println(LocalDate.of(2024, 2, 29).plusDays(1));
                java.util.Date legacy = null;      // fully qualified name, no import needed
                System.out.println(legacy);
            }
        }
    ''', out='''
        9
        3.14
        2024-03-01
        null
    ''')
    yield warn("An import is only a compile-time shortcut for names — it loads nothing and has no runtime cost. `import java.util.*` does **not** import sub-packages like `java.util.function`.")
    yield section("`protected` in practice", "shield-half")
    yield p("`protected` members are visible to the whole package *plus* subclasses elsewhere — but a subclass in another package can only use them through its own type (`this` or a subclass reference), not through an arbitrary parent-class object.")
    yield qa("Can a top-level class be `private` or `protected`?",
             "No — only `public` or package-private. Nested classes can use all four modifiers.")
    yield qa("What is the default access level?",
             "Package-private: visible to every class in the same package and nowhere else — not even to subclasses in other packages.")
    yield qa("Can an overriding method reduce visibility?",
             "No. An override may keep or widen access (`protected` → `public`) but never narrow it, otherwise code written against the parent type would break.")


@topic(G, "encapsulation", "Encapsulation", "lock-square")
def _():
    yield lead("Keep fields `private` and expose behaviour through methods, so the class alone guarantees that its state is always valid.")
    yield define("Encapsulation", "bundling data with the methods that operate on it, and **hiding the data** so outside code can change it only through a controlled interface.")
    yield section("Why it matters", "bulb")
    yield cards(
        ("Invariants", "The class validates every change, so an object can never be in an illegal state (negative balance, empty name).", "shield-check"),
        ("Freedom to change", "Internal representation can change (cents instead of double) without breaking callers.", "refresh"),
        ("Easier debugging", "Every mutation passes through a few methods — one place for a breakpoint or log.", "bug"),
        ("Thread safety", "Controlled access is where you add synchronisation or make the class immutable.", "lock"),
    )
    yield section("Getters, setters and validation", "code")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Account acc = new Account("Asha", 1000);
                acc.withdraw(300);
                System.out.println(acc.getOwner() + ": " + acc.getBalance());
                try {
                    acc.withdraw(5000);
                } catch (IllegalArgumentException e) {
                    System.out.println("rejected: " + e.getMessage());
                }
                System.out.println("balance still " + acc.getBalance());
            }
        }

        class Account {
            private final String owner;
            private long balance;                  // hidden: no one can set it to -1

            Account(String owner, long opening) {
                if (owner == null || owner.isBlank()) throw new IllegalArgumentException("owner required");
                this.owner = owner;
                this.balance = opening;
            }

            String getOwner() { return owner; }
            long getBalance() { return balance; }  // read-only: no setBalance()

            void withdraw(long amount) {
                if (amount <= 0 || amount > balance)
                    throw new IllegalArgumentException("invalid amount " + amount);
                balance -= amount;
            }
        }
    ''', out='''
        Asha: 700
        rejected: invalid amount 5000
        balance still 700
    ''')
    yield note("Don't generate a setter for every field. Expose *operations* (`withdraw`, `rename`) that express intent and enforce rules — a public getter + setter pair on every field is barely better than a public field.")
    yield section("Leaking mutable state — and defensive copies", "copy")
    yield snippet("java", r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            public static void main(String[] args) {
                List<String> input = new ArrayList<>(List.of("math", "physics"));
                Leaky leaky = new Leaky(input);
                Safe safe = new Safe(input);

                input.add("hacked");                 // caller mutates its own list
                leaky.getSubjects().clear();         // caller mutates via the getter

                System.out.println("leaky: " + leaky.getSubjects());
                System.out.println("safe:  " + safe.getSubjects());
                try {
                    safe.getSubjects().add("x");
                } catch (UnsupportedOperationException e) {
                    System.out.println("safe getter is read-only");
                }
            }
        }

        class Leaky {
            private final List<String> subjects;
            Leaky(List<String> subjects) { this.subjects = subjects; }   // stores caller's list
            List<String> getSubjects() { return subjects; }              // hands out internals
        }

        class Safe {
            private final List<String> subjects;
            Safe(List<String> subjects) { this.subjects = List.copyOf(subjects); }   // copy in
            List<String> getSubjects() { return subjects; }                          // already unmodifiable
        }
    ''', out='''
        leaky: []
        safe:  [math, physics]
        safe getter is read-only
    ''')
    yield dodont(
        "Copy mutable arguments on the way in and return copies or unmodifiable views on the way out (`List.copyOf`, `new Date(d.getTime())`).",
        "Returning a reference to an internal array, list or `Date` — callers can then change your object's state behind its back.",
    )
    yield section("Encapsulation vs abstraction", "arrows-diff")
    yield table(
        ["", "Encapsulation", "Abstraction"],
        ["Focus", "*How* data is protected", "*What* is exposed"],
        ["Mechanism", "`private` fields, accessors, validation", "Interfaces, abstract classes, simple method names"],
        ["Level", "Implementation", "Design"],
    )
    yield qa("How do you achieve encapsulation in Java?",
             "Make fields `private`, provide methods (getters, intention-revealing operations) that validate changes, and avoid leaking references to mutable internals — use defensive copies.")
    yield qa("Is a class with private fields and public getters/setters for all of them encapsulated?",
             "Only nominally. If every setter accepts anything, the class can't protect its invariants. Real encapsulation exposes behaviour and validates every state change.")
    yield qa("What is a JavaBean?",
             "A convention: public no-arg constructor, private fields, `getX`/`setX` (`isX` for booleans) accessors, and usually `Serializable`. Frameworks use reflection on these names.")
