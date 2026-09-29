from kit import *

G = "Getting Started"


@topic(G, "java-intro", "Introduction to Java", "coffee")
def _():
    yield lead("A statically typed, object-oriented, garbage-collected language that compiles to *bytecode* and runs on any machine with a JVM — “write once, run anywhere”.")
    yield define("Java", "a general-purpose language (Sun Microsystems, 1995; now Oracle + the OpenJDK community) whose source is compiled to platform-neutral **bytecode** and executed by the **Java Virtual Machine**, which interprets it and JIT-compiles hot code to native machine code.")
    yield section("Why Java?", "bulb")
    yield cards(
        ("Platform independent", "The same `.class` files run on Windows, Linux and macOS — only the JVM is platform-specific.", "world"),
        ("Statically typed", "Types are checked at compile time, so whole classes of bugs never reach production. Great IDE support and refactoring.", "shield-check"),
        ("Automatic memory", "No `free`/`delete`: the garbage collector reclaims unreachable objects. No dangling pointers, no pointer arithmetic.", "recycle"),
        ("Huge ecosystem", "Spring, Hibernate, Android, Kafka, Hadoop/Spark, Elasticsearch, Minecraft… plus Maven Central with millions of libraries.", "packages"),
        ("Fast", "The JIT (HotSpot C1/C2) optimises the code that actually runs hot, often reaching C++-like throughput for long-running servers.", "rocket"),
        ("Backward compatible", "Code written for Java 1.4 still compiles today. A new version ships every 6 months; an **LTS** every 2 years (8, 11, 17, 21, 25).", "history"),
    )
    yield section("Key features (the classic “buzzwords”)", "list-check")
    yield table(
        ["Feature", "What it means in practice"],
        ["Object-oriented", "Everything lives inside a class; encapsulation, inheritance, polymorphism, abstraction."],
        ["Simple", "No pointers, no operator overloading, no multiple class inheritance, no header files."],
        ["Robust", "Strong typing, exceptions, bounds-checked arrays, GC."],
        ["Secure", "Bytecode verification, no raw memory access, sandboxable class loaders."],
        ["Multithreaded", "Threads, locks and concurrent collections built into the language and library."],
        ["Architecture-neutral", "Fixed sizes for primitives: an `int` is 32 bits everywhere."],
    )
    yield section("Hello, World", "code")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println("Hello, Java!");
                System.out.println("Running on Java " + Runtime.version().feature());
            }
        }
    ''', out='''
        Hello, Java!
        Running on Java 21
    ''')
    yield shell('''
        $ javac Main.java        # compile → Main.class (bytecode)
        $ java Main              # run the class on the JVM
        $ java Main.java         # Java 11+: compile in memory and run in one step
        $ jshell                 # Java 9+: interactive REPL
    ''')
    yield section("Where Java is used", "building-factory")
    yield chips("Enterprise back ends (Spring Boot)", "Android (with Kotlin)", "Big data (Hadoop, Spark, Kafka)", "Banking & trading systems", "Search (Elasticsearch, Solr)", "Build tools (Maven, Gradle)", "Games (Minecraft)")
    yield note("Java ≠ JavaScript. The names are a 1995 marketing coincidence; the languages are unrelated.", "Common confusion")
    yield qa("Why is Java called platform independent?",
             "Because `javac` produces **bytecode**, not machine code. Any OS that has a JVM can run that bytecode unchanged. The JVM itself *is* platform dependent — there is a different JVM build for each OS/CPU.")
    yield qa("Is Java a purely object-oriented language?",
             "No. It has **primitive types** (`int`, `double`, `boolean`…) that are not objects, and `static` members that belong to no object. Wrapper classes (`Integer`…) bridge primitives into the object world.")
    yield qa("Is Java compiled or interpreted?",
             "Both. Source is *compiled* to bytecode by `javac`; the JVM then *interprets* bytecode and *JIT-compiles* frequently executed methods to native code at run time.")


@topic(G, "jdk-jre-jvm", "JDK, JRE & JVM", "stack-2")
def _():
    yield lead("Three nested boxes: the **JDK** (tools to build) contains the **JRE** (what's needed to run) which contains the **JVM** (the engine that executes bytecode).")
    yield formula("JDK = JRE + development tools (javac, jar, javadoc, jdb, jshell…)")
    yield formula("JRE = JVM + class libraries (java.lang, java.util, …)")
    yield section("What each one is", "box")
    yield cards(
        ("JVM — Java Virtual Machine", "An abstract machine that loads, verifies and executes bytecode. Provides memory management (GC), threads and the JIT compiler. *Specification* + *implementation* (HotSpot, OpenJ9, GraalVM).", "cpu"),
        ("JRE — Java Runtime Environment", "The JVM plus the standard library (`rt.jar` before Java 9, modules since). Enough to *run* programs, not compile them.", "player-play"),
        ("JDK — Java Development Kit", "The JRE plus developer tools: `javac`, `java`, `jar`, `javadoc`, `jdb`, `jshell`, `jcmd`, `jlink`… What developers install.", "tools"),
    )
    yield table(
        ["", "JDK", "JRE", "JVM"],
        ["Purpose", "Develop + run", "Run", "Execute bytecode"],
        ["Contains `javac`?", "Yes", "No", "No"],
        ["Contains class library?", "Yes", "Yes", "No"],
        ["Platform dependent?", "Yes", "Yes", "Yes"],
    )
    yield note("Since Java 11, Oracle no longer ships a separate JRE download. You install a JDK (e.g. Eclipse Temurin, Amazon Corretto, Oracle JDK) and, for deployment, build a trimmed runtime with `jlink`.", "Modern reality")
    yield section("Inside the JVM", "settings")
    yield steps(
        ("Class loader subsystem", "Finds `.class` files, loads them, links (verify → prepare → resolve) and initialises them."),
        ("Runtime data areas", "Heap (objects), Method Area / Metaspace (class metadata), one Stack per thread (frames with local variables), PC registers, native method stacks."),
        ("Execution engine", "Interpreter + JIT compiler (C1 quick, C2 optimising) + Garbage Collector."),
        ("JNI / native libraries", "Bridge to C/C++ code (`native` methods)."),
    )
    yield section("Checking what you have", "terminal")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println("feature version: " + Runtime.version().feature());
                System.out.println("spec version:    " + System.getProperty("java.specification.version"));
                System.out.println("class file ok:   " + (Main.class.getName().equals("Main")));
            }
        }
    ''', out='''
        feature version: 21
        spec version:    21
        class file ok:   true
    ''')
    yield shell('''
        $ java -version          # runtime version
        $ javac -version         # compiler version (only in a JDK)
        $ echo $JAVA_HOME        # where the JDK is installed
    ''')
    yield section("OpenJDK distributions", "brand-open-source")
    yield p("All major builds come from the same OpenJDK source; they differ in licensing, support length and extras.")
    yield chips("Eclipse Temurin", "Amazon Corretto", "Oracle JDK / Oracle OpenJDK", "Azul Zulu", "Microsoft Build of OpenJDK", "GraalVM")
    yield qa("What is the difference between JDK, JRE and JVM?",
             "The **JVM** executes bytecode. The **JRE** = JVM + standard libraries — enough to run Java apps. The **JDK** = JRE + development tools like `javac`, `jar`, `javadoc` — needed to write and compile Java.")
    yield qa("Is the JVM platform independent?",
             "No — the JVM is written for a specific OS and CPU. *Bytecode* is platform independent precisely because every platform has its own JVM.")
    yield qa("What is the JIT compiler?",
             "The Just-In-Time compiler inside the JVM. It profiles running code and compiles *hot* methods (called often, loops) from bytecode to optimised native machine code, with tricks like inlining and escape analysis. That's why Java programs “warm up”.")


@topic(G, "compilation-classloading", "Compilation, Bytecode & Class Loading", "file-code")
def _():
    yield lead("`javac` turns each class into a `.class` file of bytecode; the JVM loads classes *lazily*, on first use, through a chain of class loaders.")
    yield flow("`Main.java`", "`javac`", "`Main.class` (bytecode)", "Class loader", "Bytecode verifier", "Interpreter / JIT", "Native CPU")
    yield section("Bytecode", "binary")
    yield define("Bytecode", "the instruction set of the JVM — a compact, stack-based code stored in `.class` files. Each class (including nested and anonymous classes) gets its own `.class` file, e.g. `Outer$Inner.class`.")
    yield p("You can read the bytecode with `javap -c`:")
    yield shell('''
        $ cat Add.java
        class Add { static int add(int a, int b) { return a + b; } }
        $ javac Add.java && javap -c Add
          static int add(int, int);
            Code:
               0: iload_0        // push local 0 (a)
               1: iload_1        // push local 1 (b)
               2: iadd           // pop two ints, push their sum
               3: ireturn
    ''')
    yield section("Class loading: load → link → initialise", "loader")
    yield steps(
        ("Loading", "A class loader finds the bytes (from the module image, a JAR, the file system, the network…) and creates a `Class` object."),
        ("Linking — verify", "The bytecode verifier checks the code is type-safe and can't corrupt the stack or memory."),
        ("Linking — prepare", "Static fields are allocated and set to *default* values (`0`, `null`, `false`)."),
        ("Linking — resolve", "Symbolic references (names of other classes, methods) become direct references (may be lazy)."),
        ("Initialisation", "Static initialisers and static field assignments run, top to bottom — exactly once, on first *active use*."),
    )
    yield section("The class loader hierarchy", "hierarchy")
    yield table(
        ["Loader", "Loads", "Notes"],
        ["Bootstrap", "Core modules: `java.base` (`java.lang`, `java.util`…)", "Written in native code; appears as `null` from Java"],
        ["Platform (was Extension)", "Other Java SE / JDK modules (`java.sql`…)", "Parent is bootstrap"],
        ["Application (System)", "Your classes from the class path / module path", "Parent is platform"],
        ["Custom", "Anything you want (plugins, hot reload, app servers)", "Extend `ClassLoader`"],
    )
    yield note("**Parent delegation model:** a loader first asks its parent to load a class, and only loads it itself if the parent can't. So nobody can replace `java.lang.String` with their own version.")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println(String.class.getClassLoader());              // bootstrap → null
                System.out.println(java.sql.Date.class.getClassLoader().getName());
                ClassLoader app = ClassLoader.getSystemClassLoader();
                System.out.println(app.getName() + " -> parent " + app.getParent().getName());
            }
        }
    ''', out='''
        null
        platform
        app -> parent platform
    ''')
    yield section("Lazy initialisation — classes load on first use", "clock-play")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println("main starts");
                System.out.println(Config.NAME);     // compile-time constant: inlined, no init!
                System.out.println(Config.port);     // first active use → static block runs
                System.out.println(Config.port);     // already initialised
            }
        }

        class Config {
            static final String NAME = "app";       // constant — copied into the caller
            static int port = 8080;
            static { System.out.println("Config initialised"); }
        }
    ''', out='''
        main starts
        app
        Config initialised
        8080
        8080
    ''')
    yield warn("`static final` fields initialised with a compile-time constant (`\"app\"`, `42`) are copied into the calling class at compile time. Reading them does **not** initialise the declaring class — and changing the constant requires recompiling the callers.")
    yield qa("What triggers class initialisation?",
             "An *active use*: creating an instance (`new`), calling a static method, reading/writing a non-constant static field, reflection like `Class.forName(\"X\")`, initialising a subclass (parent first), or it being the main class. Merely declaring a variable of that type or reading a compile-time constant does not.")
    yield qa("What is the parent delegation model and why does it exist?",
             "Each class loader delegates a load request to its parent first. It guarantees core classes are always loaded by the bootstrap loader (security — you can't shadow `java.lang.Object`) and that a class is loaded only once per hierarchy.")
    yield qa("ClassNotFoundException vs NoClassDefFoundError?",
             "`ClassNotFoundException` is a *checked exception* when code explicitly loads a class by name (`Class.forName`, `loadClass`) and it isn't found. `NoClassDefFoundError` is an *error* when a class that was present at compile time is missing (or failed static initialisation) at run time.")


@topic(G, "program-structure", "Program Structure & main()", "layout-list")
def _():
    yield lead("A Java program is a set of classes; execution starts at `public static void main(String[] args)` of the class you launch.")
    yield section("Anatomy of a source file", "file")
    yield snippet("java", '''
        package com.example.app;           // 1. optional package (must be first)

        import java.util.List;             // 2. imports

        public class Main {                // 3. at most ONE public top-level class, named like the file
            static final int LIMIT = 3;    //    fields

            public static void main(String[] args) {   // entry point
                List<String> names = List.of("Ada", "Linus", "Grace");
                for (int i = 0; i < LIMIT; i++) {
                    greet(names.get(i));
                }
            }

            static void greet(String name) {            // methods
                System.out.println("Hi, " + name);
            }
        }
    ''', out='''
        Hi, Ada
        Hi, Linus
        Hi, Grace
    ''')
    yield section("Dissecting `main`", "search")
    yield table(
        ["Part", "Why"],
        ["`public`", "The JVM calls it from outside the class."],
        ["`static`", "No object exists yet — the JVM calls it on the class itself."],
        ["`void`", "Returns nothing; use `System.exit(code)` to set an exit status."],
        ["`main`", "The name the launcher looks for."],
        ["`String[] args`", "Command-line arguments (also `String... args`). Never `null`; empty if none."],
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println("count = " + args.length);
                for (String a : args) System.out.println("arg: " + a);
            }
        }
    ''', out='''
        count = 2
        arg: hello
        arg: 42
    ''', args=("hello", "42"), caption="Java — java Main.java hello 42")
    yield note("Java 21 previews *unnamed classes and instance main methods* (`void main() { … }`), finalised later as “compact source files” in Java 25. For interviews and production, the classic `public static void main(String[] args)` is the one to know.", "Newer Java")
    yield section("Rules and conventions", "ruler")
    yield ul(
        "One `public` top-level class per file, and the file must be named after it: `Main` → `Main.java`.",
        "Every statement ends with `;`; blocks use `{ }`. Java is case-sensitive (`Main` ≠ `main`).",
        "Naming: `PascalCase` classes/interfaces, `camelCase` methods/variables, `UPPER_SNAKE_CASE` constants, `lowercase.dotted` packages (reversed domain: `com.example.app`).",
        "Comments: `// line`, `/* block */`, `/** Javadoc */` (turned into HTML API docs by `javadoc`).",
        "`java.lang` (`String`, `Math`, `System`, `Integer`…) is imported automatically.",
    )
    yield section("Console output & input", "terminal-2")
    yield snippet("java", '''
        import java.util.Scanner;

        public class Main {
            public static void main(String[] args) {
                Scanner in = new Scanner(System.in);
                String name = in.next();
                int age = in.nextInt();
                System.out.print("No newline, ");
                System.out.println("then newline");
                System.out.printf("%s is %d years old (%.2f decades)%n", name, age, age / 10.0);
                System.out.println(String.format("[%5d] [%-5s] [%05d]", 42, "ab", 42));
            }
        }
    ''', out='''
        No newline, then newline
        Ravi is 27 years old (2.70 decades)
        [   42] [ab   ] [00042]
    ''', stdin="Ravi 27\n")
    yield table(
        ["Format", "Meaning"],
        ["`%d` / `%s` / `%c` / `%b`", "integer / string / char / boolean"],
        ["`%f`, `%.2f`, `%e`", "floating point, 2 decimals, scientific"],
        ["`%5d`, `%-5s`, `%05d`", "width 5 right-aligned, left-aligned, zero-padded"],
        ["`%x`, `%o`", "hexadecimal, octal"],
        ["`%n`", "platform line separator (prefer over `\\n` in `printf`)"],
    )
    yield qa("Can we overload main? Can main be private or non-static?",
             "You can overload `main` (e.g. `main(int x)`), but the JVM only calls `public static void main(String[])`. If it's `private` or non-static, the class compiles but the classic launcher reports that no valid main method was found.")
    yield qa("Why is main static?",
             "So the JVM can call it without creating an instance first — at start-up there is no object to call it on, and the JVM wouldn't know which constructor to use.")
    yield qa("Can a source file have no public class?",
             "Yes. Then the file can have any name, and all its top-level classes are package-private.")


@topic(G, "primitive-types", "Primitive Types & Variables", "variable")
def _():
    yield lead("Java has exactly **8 primitive types** with fixed sizes on every platform; everything else is a *reference* to an object.")
    yield section("The 8 primitives", "table")
    yield table(
        ["Type", "Size", "Range / values", "Default", "Literal"],
        ["`byte`", "8 bit", "−128 … 127", "`0`", "`(byte) 10`"],
        ["`short`", "16 bit", "−32,768 … 32,767", "`0`", "`(short) 10`"],
        ["`int`", "32 bit", "−2³¹ … 2³¹−1 (≈ ±2.1 billion)", "`0`", "`42`, `0x2A`, `0b101010`, `1_000_000`"],
        ["`long`", "64 bit", "−2⁶³ … 2⁶³−1 (≈ ±9.2 × 10¹⁸)", "`0L`", "`42L`"],
        ["`float`", "32 bit", "IEEE 754, ~7 significant digits", "`0.0f`", "`3.14f`"],
        ["`double`", "64 bit", "IEEE 754, ~15–16 significant digits", "`0.0d`", "`3.14`, `1e-9`"],
        ["`char`", "16 bit", "UTF-16 code unit `'\\u0000'` … `'\\uffff'` (unsigned)", "`'\\u0000'`", "`'A'`, `'\\n'`, `'\\u0041'`"],
        ["`boolean`", "JVM-dependent", "`true` / `false` (not 0/1!)", "`false`", "`true`"],
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println(Byte.MIN_VALUE + " " + Byte.MAX_VALUE);
                System.out.println(Integer.MAX_VALUE + " " + Long.MAX_VALUE);
                System.out.println((int) Character.MAX_VALUE + " " + Character.SIZE + " bits");
                int million = 1_000_000;                   // underscores for readability
                System.out.println(million + " " + 0xFF + " " + 0b1010 + " " + 017);
                char c = 'A';
                System.out.println(c + 1);                 // char promoted to int
                System.out.println((char) (c + 1));
            }
        }
    ''', out='''
        -128 127
        2147483647 9223372036854775807
        65535 16 bits
        1000000 255 10 15
        66
        B
    ''')
    yield warn("A leading `0` makes an *octal* literal: `017` is 15, and `09` doesn't compile.")
    yield section("Variables: local, instance, static", "variable-plus")
    yield table(
        ["Kind", "Declared", "Lives in", "Default value?"],
        ["Local", "Inside a method/block", "Stack frame", "**No** — must be assigned before use (compile error otherwise)"],
        ["Instance (field)", "In the class, no `static`", "Inside each object on the heap", "Yes (`0`, `false`, `null`)"],
        ["Static (class variable)", "`static` in the class", "Once per class", "Yes"],
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                int x;
                System.out.println(x);   // local variable never assigned
            }
        }
    ''', fails=True)
    yield output('''
        Main.java:4: error: variable x might not have been initialized
                System.out.println(x);   // local variable never assigned
                                   ^
        1 error
    ''', "Compiler error")
    yield section("`var` — local type inference (Java 10+)", "wand")
    yield snippet("java", '''
        import java.util.ArrayList;

        public class Main {
            public static void main(String[] args) {
                var count = 10;                       // int
                var price = 9.99;                     // double
                var names = new ArrayList<String>();  // ArrayList<String>
                names.add("Ada");
                for (var n : names) System.out.println(n + " " + count + " " + price);
            }
        }
    ''', out="Ada 10 9.99")
    yield ul(
        "Still **static typing** — the compiler infers the type once; it can't change later.",
        "Only for local variables with an initialiser (and loop variables). Not for fields, parameters or return types.",
        "`var x = null;` and `var a = {1, 2};` don't compile — there's nothing to infer from.",
    )
    yield section("Integer overflow & floating-point surprises", "alert-triangle")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                int big = Integer.MAX_VALUE;
                System.out.println(big + 1);                   // wraps around silently
                long ok = big + 1L;                            // do the math in long
                System.out.println(ok);
                System.out.println(1_000_000 * 1_000_000);     // int * int overflows
                System.out.println(1_000_000L * 1_000_000);
                try {
                    Math.addExact(big, 1);
                } catch (ArithmeticException e) {
                    System.out.println("addExact: " + e.getMessage());
                }
                System.out.println(0.1 + 0.2);
                System.out.println(0.1f + 0.2f);
                System.out.println(1.0 / 0 + " " + -1.0 / 0 + " " + 0.0 / 0);
            }
        }
    ''', out='''
        -2147483648
        2147483648
        -727379968
        1000000000000
        addExact: integer overflow
        0.30000000000000004
        0.3
        Infinity -Infinity NaN
    ''')
    yield warn("Integer overflow is **silent** in Java. Use `long`, `Math.addExact`/`multiplyExact` (which throw), or `BigInteger`. For money, never use `double` — use `BigDecimal` or integer cents.")
    yield snippet("java", '''
        import java.math.BigDecimal;
        import java.math.BigInteger;

        public class Main {
            public static void main(String[] args) {
                System.out.println(new BigDecimal("0.1").add(new BigDecimal("0.2")));
                System.out.println(new BigDecimal(0.1));    // the double's exact binary value!
                BigInteger f = BigInteger.ONE;
                for (int i = 2; i <= 25; i++) f = f.multiply(BigInteger.valueOf(i));
                System.out.println("25! = " + f);
            }
        }
    ''', out='''
        0.3
        0.1000000000000000055511151231257827021181583404541015625
        25! = 15511210043330985984000000
    ''')
    yield qa("Why is `char` 16 bits in Java?",
             "Java was designed around Unicode, and in 1995 Unicode fit in 16 bits. A `char` is a UTF-16 *code unit*; characters outside the Basic Multilingual Plane (e.g. many emoji) need two `char`s (a surrogate pair).")
    yield qa("What are default values, and do local variables get them?",
             "Fields and array elements get defaults (`0`, `0.0`, `false`, `'\\u0000'`, `null`). Local variables do **not** — the compiler rejects reading one before it's definitely assigned.")
    yield qa("Does `var` make Java dynamically typed?",
             "No. `var` is compile-time inference only; the variable has one fixed static type, exactly as if you had written it out.")


@topic(G, "wrappers-autoboxing", "Wrapper Classes, Autoboxing & the Integer Cache", "box")
def _():
    yield lead("Each primitive has an immutable wrapper class so it can live where objects are required (collections, generics, `null`). The compiler converts between them automatically — sometimes with surprising results.")
    yield table(
        ["Primitive", "Wrapper", "Cache (`valueOf`)"],
        ["`byte`", "`Byte`", "all values"],
        ["`short`", "`Short`", "−128 … 127"],
        ["`int`", "`Integer`", "−128 … 127 (upper bound tunable)"],
        ["`long`", "`Long`", "−128 … 127"],
        ["`char`", "`Character`", "0 … 127"],
        ["`boolean`", "`Boolean`", "`TRUE` / `FALSE`"],
        ["`float` / `double`", "`Float` / `Double`", "none"],
    )
    yield define("Autoboxing / unboxing", "the compiler's automatic conversion `int` → `Integer` (it inserts `Integer.valueOf(x)`) and `Integer` → `int` (it inserts `x.intValue()`).")
    yield snippet("java", '''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            public static void main(String[] args) {
                List<Integer> list = new ArrayList<>();
                list.add(5);                  // autoboxing: Integer.valueOf(5)
                int first = list.get(0);      // unboxing: list.get(0).intValue()
                Integer total = 0;
                for (int i = 1; i <= 3; i++) total += i;   // unbox, add, box again each time
                System.out.println(first + " " + total);
                System.out.println(Integer.parseInt("123") + 1);       // String → int
                System.out.println(Integer.valueOf("123").getClass().getSimpleName());
                System.out.println(Integer.toBinaryString(10) + " " + Integer.toHexString(255));
                System.out.println(Character.isDigit('7') + " " + Character.toUpperCase('q'));
            }
        }
    ''', out='''
        5 6
        124
        Integer
        1010 ff
        true Q
    ''')
    yield section("The Integer cache trap", "alert-triangle")
    yield p("`Integer.valueOf` returns *cached* objects for −128…127. `==` on wrappers compares **references**, so it “works” for small numbers and breaks for bigger ones.")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                Integer a = 127, b = 127;
                Integer c = 128, d = 128;
                System.out.println(a == b);          // same cached object
                System.out.println(c == d);          // two different objects
                System.out.println(c.equals(d));     // compare values
                System.out.println(c.intValue() == d);  // one side primitive → unboxes → value compare
            }
        }
    ''', out='''
        true
        false
        true
        true
    ''')
    yield warn("Never compare wrapper objects with `==`. Use `equals`, or unbox first. (`new Integer(5)` is deprecated for removal precisely because it bypasses the cache.)")
    yield section("NullPointerException from unboxing", "bug")
    yield snippet("java", '''
        import java.util.HashMap;
        import java.util.Map;

        public class Main {
            public static void main(String[] args) {
                Map<String, Integer> stock = new HashMap<>();
                stock.put("apple", 3);
                try {
                    int bananas = stock.get("banana");   // get → null → null.intValue()
                    System.out.println(bananas);
                } catch (NullPointerException e) {
                    System.out.println("NPE while unboxing");
                }
                int safe = stock.getOrDefault("banana", 0);
                System.out.println(safe);
            }
        }
    ''', out='''
        NPE while unboxing
        0
    ''')
    yield section("Performance cost", "gauge")
    yield ul(
        "Each boxed value is a separate heap object (~16 bytes vs 4 for an `int`), plus the reference.",
        "Summing into a `Long` inside a loop creates millions of garbage objects — use a primitive `long`.",
        "Prefer `int[]` over `List<Integer>` and `IntStream` over `Stream<Integer>` for heavy numeric work.",
    )
    yield qa("What does `Integer a = 1000, b = 1000; a == b` print, and why?",
             "`false` (by default). Autoboxing calls `Integer.valueOf`, which only caches −128…127, so 1000 creates two distinct objects and `==` compares references. With `127` it prints `true`.")
    yield qa("Why do we need wrapper classes?",
             "Generics and collections work only with objects (`List<int>` is illegal), wrappers can be `null` (\"no value\"), and they carry utility methods (`parseInt`, `MAX_VALUE`, `compare`, `toBinaryString`).")
    yield qa("Can the Integer cache range be changed?",
             "The upper bound can be raised with the JVM flag `-XX:AutoBoxCacheMax=<n>` (or `java.lang.Integer.IntegerCache.high`). The lower bound is fixed at −128.")


@topic(G, "type-casting", "Type Conversion & Casting", "transform")
def _():
    yield lead("Widening conversions happen automatically; narrowing ones need an explicit cast and may silently lose information.")
    yield section("Widening (implicit) vs narrowing (explicit)", "arrows-diff")
    yield formula("byte → short → int → long → float → double      (char → int)")
    yield table(
        ["", "Widening", "Narrowing"],
        ["Direction", "Smaller → larger type", "Larger → smaller type"],
        ["Syntax", "Automatic: `long l = i;`", "Cast required: `int i = (int) l;`"],
        ["Data loss?", "No (except precision: `long`/`int` → `float`/`double`)", "Possibly: high bits dropped, fraction truncated"],
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                int i = 100;
                long l = i;              // widening
                double d = l;            // widening
                System.out.println(l + " " + d);

                double price = 9.99;
                int whole = (int) price;         // truncates toward zero, not rounds
                System.out.println(whole + " " + (int) -9.99 + " " + Math.round(9.5));

                int big = 300;
                byte b = (byte) big;             // keeps only the low 8 bits: 300 - 256
                System.out.println(b);
                System.out.println((int) 3_000_000_000L);   // high 32 bits dropped
                System.out.println((int) 1e20);             // double → int saturates
                System.out.println((char) 97 + " " + (int) 'a');

                long precise = 123_456_789_123L;
                float f = precise;                          // widening but loses precision
                System.out.println((long) f);
            }
        }
    ''', out='''
        100 100.0
        9 -9 10
        44
        -1294967296
        2147483647
        a 97
        123456790528
    ''')
    yield section("Numeric promotion in expressions", "math")
    yield ul(
        "In arithmetic, `byte`, `short` and `char` are first promoted to `int`.",
        "If either operand is `long` → `long`; `float` → `float`; `double` → `double`.",
        "So `byte + byte` is an `int` and must be cast back — but compound assignments (`+=`) cast implicitly.",
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                byte a = 10, b = 20;
                // byte c = a + b;          // compile error: int cannot be converted to byte
                byte c = (byte) (a + b);
                a += 5;                     // OK: means a = (byte) (a + 5)
                byte x = 120;
                x += 10;                    // silently overflows!
                System.out.println(c + " " + a + " " + x);
                System.out.println(5 / 2 + " " + 5 / 2.0 + " " + (double) 5 / 2 + " " + (double) (5 / 2));
                System.out.println('a' + 'b' + " vs " + "" + 'a' + 'b');
            }
        }
    ''', out='''
        30 15 -126
        2 2.5 2.5 2.0
        195 vs ab
    ''')
    yield warn("`(double) (5 / 2)` is `2.0` — the integer division happens *before* the cast. Cast an operand, not the result.")
    yield section("Converting to and from String", "letter-case")
    yield table(
        ["Conversion", "How"],
        ["`String` → `int` / `double`", "`Integer.parseInt(s)`, `Double.parseDouble(s)` (throw `NumberFormatException`)"],
        ["`String` → wrapper", "`Integer.valueOf(s)`"],
        ["anything → `String`", "`String.valueOf(x)`, `Integer.toString(n)`, `\"\" + x`"],
        ["`char` ↔ digit", "`c - '0'`, `(char) ('0' + d)`, `Character.getNumericValue(c)`"],
        ["radix", "`Integer.parseInt(\"ff\", 16)`, `Integer.toString(255, 2)`"],
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println(Integer.parseInt("42") * 2);
                System.out.println(String.valueOf(3.5) + "!");
                System.out.println('7' - '0' + 1);
                System.out.println(Integer.parseInt("ff", 16) + " " + Integer.toString(10, 2));
                try {
                    Integer.parseInt("4 2");
                } catch (NumberFormatException e) {
                    System.out.println(e.getMessage());
                }
            }
        }
    ''', out='''
        84
        3.5!
        8
        255 1010
        For input string: "4 2"
    ''')
    yield section("Reference casting (preview)", "arrows-up-down")
    yield p("Objects are cast along the inheritance tree: **upcasting** (`Object o = \"hi\";`) is implicit and always safe; **downcasting** (`String s = (String) o;`) is checked at run time and throws `ClassCastException` if wrong. Use `instanceof` pattern matching — see *Polymorphism*.")
    yield qa("What is the result of `(byte) 200`?",
             "`-56`. Only the low 8 bits are kept: 200 is `11001000` in binary, which as a signed two's-complement byte is 200 − 256 = −56.")
    yield qa("Why does `short s = 1; s = s + 1;` fail but `s += 1;` compile?",
             "`s + 1` is promoted to `int`, and assigning an `int` to a `short` needs an explicit cast. Compound assignment operators include an implicit cast back to the left-hand type.")
    yield qa("Is converting `long` to `float` widening? Can it lose data?",
             "Yes, it's a widening conversion (allowed implicitly), but `float` has only 24 bits of mantissa, so large `long` values lose precision.")


@topic(G, "operators", "Operators & Precedence", "math-symbols")
def _():
    yield lead("Java's operators are C-like, with a few Java-specific twists: `>>>`, string `+`, `instanceof`, and strict `boolean` conditions.")
    yield table(
        ["Kind", "Operators", "Notes"],
        ["Arithmetic", "`+ - * / %`", "Integer `/` truncates toward zero; `%` takes the sign of the dividend"],
        ["Unary", "`+ - ++ -- !`, `~`", "Prefix `++i` increments then yields; postfix `i++` yields then increments"],
        ["Relational", "`== != < <= > >=`", "`==` on objects compares references"],
        ["Logical", "`&& || !`", "Short-circuit; operands must be `boolean`"],
        ["Bitwise", "`& | ^ ~`", "On `boolean` operands `&`/`|` evaluate *both* sides"],
        ["Shift", "`<< >> >>>`", "`>>` keeps the sign, `>>>` fills with zeros"],
        ["Assignment", "`= += -= *= /= %= &= |= ^= <<= >>= >>>=`", "Compound forms cast implicitly"],
        ["Ternary", "`cond ? a : b`", "An expression — yields a value"],
        ["Type", "`instanceof`", "`obj instanceof String s` binds a variable (Java 16+)"],
    )
    yield section("Arithmetic details", "math")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println(7 / 2 + " " + -7 / 2 + " " + 7 % 3 + " " + -7 % 3);
                System.out.println(Math.floorDiv(-7, 2) + " " + Math.floorMod(-7, 3));
                System.out.println(5.5 % 2);
                int i = 5;
                int a = i++;          // a = 5, then i = 6
                int b = ++i;          // i = 7, then b = 7
                System.out.println(a + " " + b + " " + i);
                String s = "Sum: " + 1 + 2;        // left to right: string concat
                String t = 1 + 2 + " is the sum";  // 3 first, then concat
                System.out.println(s + " | " + t);
            }
        }
    ''', out='''
        3 -3 1 -1
        -4 2
        1.5
        5 7 7
        Sum: 12 | 3 is the sum
    ''')
    yield warn("`i = i++;` leaves `i` unchanged: the old value is saved, `i` is incremented, then the saved old value is assigned back. A classic trick question — never write it.")
    yield section("Short-circuit evaluation", "bolt")
    yield snippet("java", '''
        public class Main {
            static boolean check(String label, boolean value) {
                System.out.println("evaluating " + label);
                return value;
            }

            public static void main(String[] args) {
                String s = null;
                if (s != null && s.length() > 3) System.out.println("long");   // safe: right side skipped
                System.out.println(check("A", false) && check("B", true));
                System.out.println(check("C", false) & check("D", true));       // non-short-circuit
            }
        }
    ''', out='''
        evaluating A
        false
        evaluating C
        evaluating D
        false
    ''')
    yield section("Bitwise & shift operators", "binary")
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                int a = 0b1100, b = 0b1010;
                System.out.println((a & b) + " " + (a | b) + " " + (a ^ b) + " " + ~a);
                System.out.println((1 << 10) + " " + (-16 >> 2) + " " + (-16 >>> 28));
                int n = 12;
                System.out.println("even? " + ((n & 1) == 0));
                System.out.println("power of two? " + (n > 0 && (n & (n - 1)) == 0));
                System.out.println("set bits: " + Integer.bitCount(n));
                int x = 3, y = 9;
                x ^= y; y ^= x; x ^= y;                  // XOR swap
                System.out.println(x + " " + y);
            }
        }
    ''', out='''
        8 14 6 -13
        1024 -4 15
        even? true
        power of two? false
        set bits: 2
        9 3
    ''')
    yield section("Precedence (high → low)", "sort-descending")
    yield table(
        ["Level", "Operators"],
        ["Postfix", "`expr++ expr--`"],
        ["Unary", "`++expr --expr + - ~ !` and casts"],
        ["Multiplicative", "`* / %`"],
        ["Additive", "`+ -`"],
        ["Shift", "`<< >> >>>`"],
        ["Relational", "`< > <= >= instanceof`"],
        ["Equality", "`== !=`"],
        ["Bitwise", "`&` then `^` then `|`"],
        ["Logical", "`&&` then `||`"],
        ["Ternary", "`? :`"],
        ["Assignment", "`= += -= …` (right-associative)"],
    )
    yield snippet("java", '''
        public class Main {
            public static void main(String[] args) {
                System.out.println(2 + 3 * 4);
                System.out.println((2 + 3) * 4);
                System.out.println(1 + 2 << 1);           // + binds tighter than <<
                System.out.println(true || false && false);   // && before ||
                int score = 72;
                String grade = score >= 90 ? "A" : score >= 70 ? "B" : "C";
                System.out.println(grade);
            }
        }
    ''', out='''
        14
        20
        6
        true
        B
    ''')
    yield note("When in doubt, add parentheses. Readers shouldn't need the precedence table.", "Tip")
    yield qa("What's the difference between `&` and `&&`?",
             "`&&` is logical AND with short-circuiting — the right side isn't evaluated if the left is `false`. `&` on booleans evaluates both sides; on integers it is bitwise AND.")
    yield qa("What is `>>>`?",
             "The unsigned right shift: it shifts in zeros from the left, regardless of sign. `>>` is the arithmetic shift, which copies the sign bit. For negative numbers they differ: `-16 >> 2` is `-4`, `-16 >>> 28` is `15`.")
    yield qa("What does `System.out.println(1 + 2 + \"3\" + 4 + 5)` print?",
             "`3345`. Evaluation is left to right: `1 + 2` = `3`, then `3 + \"3\"` = `\"33\"`, and from then on every `+` is string concatenation.")
