from kit import *

G = "Core Language: Strings, Arrays & Methods"


@topic(G, "strings-immutability", "Strings, Immutability & the String Pool", "letter-case")
def _():
    yield lead("`String` is an immutable object, not a primitive. Literals are interned in the *string pool*, so `==` sometimes “works” — and that is exactly the trap.")
    yield define("String", "a final class holding an immutable sequence of UTF-16 characters (since Java 9 stored compactly as `byte[]` + a coder flag: Latin-1 or UTF-16). Every “modifying” method returns a *new* `String`.")
    yield section("Creating strings", "plus")
    yield table(
        ["Form", "Where it lives", "Notes"],
        ["`String a = \"hi\";`", "String pool (interned)", "Identical literals in the whole JVM share one object"],
        ["`String b = new String(\"hi\");`", "A new heap object", "Always a distinct object — almost never what you want"],
        ["`\"h\" + \"i\"`", "Pool", "Constant expression — folded to `\"hi\"` by the compiler"],
        ["`s1 + s2` (non-final variables)", "New heap object", "Built at runtime (via `StringConcatFactory` since Java 9)"],
        ["`b.intern()`", "Pool", "Returns the pooled copy (adds it if missing)"],
    )
    yield section("`==` vs `equals()`", "equal")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String a = "java";
                String b = "java";
                String c = new String("java");
                String d = "ja" + "va";          // compile-time constant → pooled
                String part = "ja";
                String e = part + "va";          // runtime concatenation → new object

                System.out.println(a == b);          // same pooled object
                System.out.println(a == c);          // different objects
                System.out.println(a.equals(c));     // same characters
                System.out.println(a == d);
                System.out.println(a == e);
                System.out.println(a == e.intern());
            }
        }
    ''', out='''
        true
        false
        true
        true
        false
        true
    ''')
    yield warn("Always compare string *contents* with `equals()` (or `equalsIgnoreCase()`). `==` compares references and only looks right when both sides happen to be pooled.")
    yield good("Write `\"yes\".equals(input)` — the literal on the left can never throw `NullPointerException` when `input` is `null`. Or use `Objects.equals(a, b)`.")
    yield section("Immutability in action", "lock")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String s = "hello";
                s.toUpperCase();                 // result discarded — s is unchanged
                System.out.println(s);
                s = s.toUpperCase();             // rebind the variable to the new object
                System.out.println(s);

                String t = s;
                s = s + "!";                     // creates a new String; t still points at the old one
                System.out.println(t + " " + s);
            }
        }
    ''', out='''
        hello
        HELLO
        HELLO HELLO!
    ''')
    yield section("Why is String immutable?", "shield")
    yield cards(
        ("String pool", "Sharing one object between many references is only safe if nobody can change it.", "database"),
        ("Security", "Class names, file paths, URLs and DB credentials passed as strings can't be altered after validation.", "shield-lock"),
        ("Hash caching", "`hashCode()` is computed once and cached — perfect for `HashMap` keys.", "hash"),
        ("Thread safety", "Immutable objects can be shared across threads with no synchronization.", "arrows-split"),
    )
    yield section("Concatenation in loops", "repeat")
    yield p("Each `+=` on a `String` allocates a new object and copies all characters so far — O(n²) for a loop of n appends. Use `StringBuilder` (next topics) or `String.join` / `Collectors.joining`.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String slow = "";
                for (int i = 0; i < 5; i++) slow += i;      // 5 new String objects

                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 5; i++) sb.append(i);   // one growing buffer
                System.out.println(slow + " " + sb);
                System.out.println(String.join("-", "a", "b", "c"));
            }
        }
    ''', out='''
        01234 01234
        a-b-c
    ''')
    yield qa("How many objects does `new String(\"abc\")` create?",
             "Up to **two**: the literal `\"abc\"` is placed in the string pool when the class is loaded (if not already there), and `new` always creates one more `String` object on the heap. If the literal is already pooled, only one new object is created.")
    yield qa("Where is the string pool located?",
             "Since Java 7 it is part of the regular **heap** (it used to be in PermGen), so pooled strings can be garbage-collected when unreferenced.")
    yield qa("Why is `char[]` preferred over `String` for passwords?",
             "A `String` is immutable and may sit in memory (or the pool) until GC; you cannot wipe it. A `char[]` can be overwritten with zeros right after use, and it doesn't show up by accident in logs via `toString()`.")


@topic(G, "string-methods", "Common String Methods & Text Blocks", "text-recognition")
def _():
    yield lead("The `String` API you use daily — searching, slicing, splitting, formatting — plus Java 15 text blocks for multi-line literals.")
    yield section("Method cheat sheet", "list-details")
    yield table(
        ["Method", "Returns", "Example → result"],
        ["`length()`", "int", "`\"hello\".length()` → `5`"],
        ["`charAt(i)`", "char", "`\"hello\".charAt(1)` → `'e'`"],
        ["`substring(b, e)`", "String", "`\"hello\".substring(1, 3)` → `\"el\"` (end exclusive)"],
        ["`indexOf(x)` / `lastIndexOf(x)`", "int", "`-1` when not found"],
        ["`contains`, `startsWith`, `endsWith`", "boolean", "`\"hello\".startsWith(\"he\")` → `true`"],
        ["`toUpperCase()` / `toLowerCase()`", "String", "new string"],
        ["`trim()` / `strip()`", "String", "`strip()` (Java 11) is Unicode-aware"],
        ["`isEmpty()` / `isBlank()`", "boolean", "`\"  \".isBlank()` → `true` (Java 11)"],
        ["`replace(a, b)`", "String", "literal replace of all occurrences"],
        ["`replaceAll(regex, b)`", "String", "regex-based"],
        ["`split(regex)`", "String[]", "trailing empty strings removed"],
        ["`toCharArray()` / `chars()`", "char[] / IntStream", "iterate characters"],
        ["`compareTo(s)`", "int", "lexicographic: negative / 0 / positive"],
        ["`repeat(n)`", "String", "`\"ab\".repeat(3)` → `\"ababab\"` (Java 11)"],
        ["`String.valueOf(x)`", "String", "any type → string (`\"null\"` for null objects)"],
        ["`String.format` / `formatted`", "String", "printf-style formatting"],
    )
    yield section("Searching & slicing", "search")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String s = "Hello, World";
                System.out.println(s.length() + " " + s.charAt(7));
                System.out.println(s.substring(7) + "|" + s.substring(0, 5));
                System.out.println(s.indexOf('o') + " " + s.lastIndexOf('o') + " " + s.indexOf("xyz"));
                System.out.println(s.contains("World") + " " + s.startsWith("Hell"));
                System.out.println(s.toLowerCase().replace('l', 'L'));
                System.out.println("  padded  ".strip() + "|" + "   ".isBlank() + "|" + "".isEmpty());
                System.out.println("apple".compareTo("banana") + " " + "b".compareTo("a"));
                System.out.println("Java".equalsIgnoreCase("JAVA"));
            }
        }
    ''', out='''
        12 W
        World|Hello
        4 8 -1
        true true
        heLLo, worLd
        padded|true|true
        -1 1
        true
    ''')
    yield section("Splitting & joining", "cut")
    yield snippet("java", r'''
        import java.util.Arrays;

        public class Main {
            public static void main(String[] args) {
                System.out.println(Arrays.toString("a,b,,c,,".split(",")));      // trailing empties dropped
                System.out.println(Arrays.toString("a,b,,c,,".split(",", -1)));  // keep them
                System.out.println(Arrays.toString("1.2.3".split("\\.")));       // "." is a regex!
                System.out.println(Arrays.toString("  one   two three ".trim().split("\\s+")));
                System.out.println(String.join(" | ", Arrays.asList("x", "y", "z")));
            }
        }
    ''', out='''
        [a, b, , c]
        [a, b, , c, , ]
        [1, 2, 3]
        [one, two, three]
        x | y | z
    ''')
    yield warn("`split` takes a **regex**: `split(\".\")` returns an empty array because `.` matches every character. Escape metacharacters: `\"\\\\.\"`, `\"\\\\|\"`, or use `Pattern.quote(\".\")`.")
    yield section("Characters", "abc")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String word = "Level42";
                int letters = 0, digits = 0;
                for (char c : word.toCharArray()) {
                    if (Character.isLetter(c)) letters++;
                    else if (Character.isDigit(c)) digits++;
                }
                System.out.println(letters + " letters, " + digits + " digits");
                System.out.println((int) 'a' + " " + (char) ('a' + 2) + " " + ('7' - '0'));
                System.out.println(new StringBuilder(word).reverse());
                System.out.println(word.chars().filter(Character::isUpperCase).count());
            }
        }
    ''', out='''
        5 letters, 2 digits
        97 c 7
        24leveL
        1
    ''')
    yield section("Formatting", "typography")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                System.out.println(String.format("%-6s|%5d|%.2f|%05d", "id", 42, 3.14159, 7));
                System.out.println("%s is %d years".formatted("Asha", 30));    // Java 15
                System.out.printf("%x %o %e %b%n", 255, 8, 12345.678, true);
                System.out.println(String.format("%,d", 1234567));
            }
        }
    ''', out='''
        id    |   42|3.14|00007
        Asha is 30 years
        ff 10 1.234568e+04 true
        1,234,567
    ''')
    yield section("Text blocks (Java 15)", "file-text")
    yield p("A text block starts with `\"\"\"` followed by a newline. Incidental indentation (the common leading whitespace) is stripped, and line endings are normalised to `\\n` — ideal for JSON, SQL and HTML.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                String json = """
                    {
                      "name": "Asha",
                      "age": 30
                    }
                    """;
                System.out.print(json);
                String oneLine = """
                    SELECT * \
                    FROM users""";                  // \ joins lines
                System.out.println(oneLine);
                System.out.println("""
                    Hi %s!""".formatted("Ravi"));
            }
        }
    ''', out='''
        {
          "name": "Asha",
          "age": 30
        }
        SELECT * FROM users
        Hi Ravi!
    ''')
    yield note("The position of the closing `\"\"\"` controls indentation: put it on its own line to get a trailing newline; put it after the last text to avoid one.", "Text blocks")
    yield qa("What is the difference between `trim()` and `strip()`?",
             "`trim()` removes characters with code point ≤ `U+0020` (ASCII spaces and control chars). `strip()` (Java 11) uses `Character.isWhitespace`, so it also removes Unicode whitespace such as `U+2000`. `stripLeading()` / `stripTrailing()` do one side.")
    yield qa("What is the difference between `replace` and `replaceAll`?",
             "Both replace *all* occurrences. `replace(CharSequence, CharSequence)` treats the target literally; `replaceAll(String regex, String replacement)` interprets a regular expression (and `$` / `\\` in the replacement).")
    yield qa("How do you check if a string is a palindrome?",
             "Compare `s` with `new StringBuilder(s).reverse().toString()` using `equals`, or use two indices moving towards the middle — the latter is O(1) extra space.")


@topic(G, "stringbuilder", "StringBuilder & StringBuffer", "writing")
def _():
    yield lead("A *mutable* character buffer. Use `StringBuilder` whenever you build a string piece by piece — especially in loops.")
    yield table(
        ["", "`String`", "`StringBuilder`", "`StringBuffer`"],
        ["Mutable?", "No", "Yes", "Yes"],
        ["Thread-safe?", "Yes (immutable)", "No", "Yes (`synchronized` methods)"],
        ["Speed", "Slow for repeated edits", "**Fastest**", "Slower (locking)"],
        ["Since", "1.0", "1.5", "1.0"],
        ["Use when", "Values that don't change", "Building strings in one thread (almost always)", "Legacy code; shared buffer across threads (rare)"],
    )
    yield section("Core operations", "tool")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder("Java");
                sb.append(' ').append(21).append("!");     // chaining — each call returns this
                System.out.println(sb);
                sb.insert(0, ">> ");
                System.out.println(sb);
                sb.replace(3, 7, "JAVA");
                System.out.println(sb);
                sb.deleteCharAt(sb.length() - 1).delete(0, 3);
                System.out.println(sb);
                sb.setCharAt(0, 'j');
                System.out.println(sb.reverse());
                System.out.println(sb.length() + " " + sb.indexOf("AV") + " " + sb.charAt(0));
                String result = sb.toString();              // freeze into an immutable String
                System.out.println(result);
            }
        }
    ''', out='''
        Java 21!
        >> Java 21!
        >> JAVA 21!
        JAVA 21
        12 AVAj
        7 3 1
        12 AVAj
    ''')
    yield section("Capacity", "box")
    yield p("A `StringBuilder` has a *capacity* (default 16). When full, it grows to roughly `(old * 2) + 2` and copies — amortised O(1) per append. Pre-size with `new StringBuilder(expectedLength)` when you know it.")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder();
                System.out.println(sb.capacity());
                sb.append("12345678901234567");            // 17 chars > 16
                System.out.println(sb.capacity());
                System.out.println(new StringBuilder("abc").capacity());   // 16 + 3
            }
        }
    ''', out='''
        16
        34
        19
    ''')
    yield section("Pitfalls", "alert-triangle")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                StringBuilder a = new StringBuilder("x");
                StringBuilder b = new StringBuilder("x");
                System.out.println(a.equals(b));                          // identity! not overridden
                System.out.println(a.toString().equals(b.toString()));
                System.out.println(a.compareTo(b) == 0);                  // Java 11+: content compare

                StringBuilder c = new StringBuilder('A');                  // char → int capacity 65!
                System.out.println("[" + c + "] " + c.capacity());
            }
        }
    ''', out='''
        false
        true
        true
        [] 65
    ''')
    yield warn("`StringBuilder` does **not** override `equals`/`hashCode` — compare `toString()` values (or use `compareTo`, Java 11+). And `new StringBuilder('A')` silently calls the `int capacity` constructor.")
    yield note("The compiler already turns `a + b + c` in a *single expression* into efficient code. The problem is `+=` inside a loop: each iteration creates a new `String`.", "When does + matter?")
    yield qa("Why is StringBuilder faster than String concatenation in a loop?",
             "`String` is immutable, so each `s += x` allocates a new string and copies all previous characters: O(n²) total. `StringBuilder` appends into one resizable array: O(n) amortised.")
    yield qa("StringBuilder vs StringBuffer?",
             "Same API. `StringBuffer` methods are `synchronized` (thread-safe, slower); `StringBuilder` is not synchronized and is the default choice. Sharing a builder between threads is a design smell anyway.")


@topic(G, "control-flow", "Conditionals & Loops", "arrows-split-2")
def _():
    yield lead("`if`/`else`, the ternary operator and four loop forms — plus labeled `break`/`continue` for nested loops.")
    yield section("if / else if / else", "git-branch")
    yield snippet("java", r'''
        public class Main {
            static String grade(int score) {
                if (score >= 90) return "A";
                else if (score >= 75) return "B";
                else if (score >= 50) return "C";
                else return "F";
            }

            public static void main(String[] args) {
                System.out.println(grade(95) + grade(80) + grade(60) + grade(10));
                int n = 7;
                String parity = (n % 2 == 0) ? "even" : "odd";     // ternary: an expression
                System.out.println(n + " is " + parity);
            }
        }
    ''', out='''
        ABCF
        7 is odd
    ''')
    yield warn("Conditions must be `boolean` — `if (x = 5)` or `if (n)` do not compile in Java (unlike C). The one sneaky exception: `if (flag = true)` compiles for a `boolean flag` and is always true.")
    yield section("Loops at a glance", "repeat")
    yield table(
        ["Loop", "Syntax", "Use when"],
        ["`for`", "`for (int i = 0; i < n; i++)`", "You need the index or a counted range"],
        ["enhanced `for`", "`for (T x : arrayOrIterable)`", "Visiting every element, read-only"],
        ["`while`", "`while (cond) { … }`", "Unknown number of iterations; may run 0 times"],
        ["`do-while`", "`do { … } while (cond);`", "Body must run **at least once** (menus, retries)"],
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                for (int i = 0, j = 10; i < j; i += 3, j -= 3)       // several variables
                    System.out.print(i + ":" + j + " ");
                System.out.println();

                int[] nums = {3, 1, 4};
                int sum = 0;
                for (int x : nums) sum += x;
                System.out.println("sum=" + sum);

                int n = 1234, digits = 0;
                while (n > 0) { n /= 10; digits++; }
                System.out.println("digits=" + digits);

                int k = 100;
                do { System.out.println("runs once, k=" + k); } while (k < 10);
            }
        }
    ''', out='''
        0:10 3:7
        sum=8
        digits=4
        runs once, k=100
    ''')
    yield section("break, continue & labels", "player-skip-forward")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                for (int i = 1; i <= 10; i++) {
                    if (i % 2 == 0) continue;      // skip evens
                    if (i > 7) break;              // stop the loop
                    System.out.print(i + " ");
                }
                System.out.println();

                int[][] grid = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
                outer:
                for (int r = 0; r < grid.length; r++) {
                    for (int c = 0; c < grid[r].length; c++) {
                        if (grid[r][c] == 5) {
                            System.out.println("found at " + r + "," + c);
                            break outer;           // leaves BOTH loops
                        }
                    }
                }
            }
        }
    ''', out='''
        1 3 5 7
        found at 1,1
    ''')
    yield section("Common mistakes", "bug")
    yield ul(
        "Off-by-one: `i <= arr.length` → `ArrayIndexOutOfBoundsException`. Use `i < arr.length`.",
        "Modifying the loop variable inside an enhanced `for` does nothing to the array — `x` is a copy.",
        "Removing from a `List` inside a for-each throws `ConcurrentModificationException` — use an `Iterator` or `removeIf`.",
        "A stray `;` — `for (…);` or `while (…);` makes an empty body.",
        "Floating-point loop counters (`for (double d = 0; d != 1; d += 0.1)`) may never terminate.",
    )
    yield qa("What is the difference between `while` and `do-while`?",
             "`while` checks the condition first, so the body may run zero times. `do-while` checks after the body, so it always runs at least once.")
    yield qa("How do you break out of nested loops?",
             "Put a label on the outer loop (`outer:`) and use `break outer;` (or `continue outer;`). Alternatives: move the loops into a method and `return`, or use a flag variable.")
    yield qa("Can the ternary operator replace every if/else?",
             "No — it is an *expression* that must produce a value of a common type; it can't contain statements. Use it for simple value choices; nested ternaries hurt readability.")


@topic(G, "switch-pattern-matching", "Switch Expressions & Pattern Matching", "switch-horizontal")
def _():
    yield lead("Modern `switch` (Java 14) is an expression with arrow labels and no fall-through; Java 16–21 add pattern matching for `instanceof`, type patterns in `switch`, guards and record patterns.")
    yield section("Classic switch statement (fall-through)", "arrow-down")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                int day = 2;
                switch (day) {
                    case 1:
                        System.out.println("Mon");
                    case 2:
                        System.out.println("Tue");      // matches here...
                    case 3:
                        System.out.println("Wed");      // ...and falls through (no break!)
                        break;
                    default:
                        System.out.println("Other");
                }
            }
        }
    ''', out='''
        Tue
        Wed
    ''')
    yield p("Old-style `switch` works on `int`-like types (`byte`, `short`, `char`, `int` and their wrappers), `String` (Java 7) and `enum` — never on `long`, `float`, `double` or `boolean`.")
    yield section("Switch expressions (Java 14)", "arrow-right")
    yield snippet("java", r'''
        public class Main {
            enum Day { MON, TUE, WED, THU, FRI, SAT, SUN }

            static int letters(Day d) {
                return switch (d) {                     // an expression — yields a value
                    case MON, FRI, SUN -> 6;            // several labels, no fall-through
                    case TUE -> 7;
                    case THU, SAT -> 8;
                    case WED -> {
                        int n = "Wednesday".length();
                        yield n;                        // yield returns from a block
                    }
                };                                      // exhaustive over the enum: no default needed
            }

            public static void main(String[] args) {
                System.out.println(letters(Day.MON) + " " + letters(Day.WED));
                String cmd = "stop";
                String msg = switch (cmd) {
                    case "go" -> "moving";
                    case "stop" -> "halted";
                    default -> "unknown";
                };
                System.out.println(msg);
            }
        }
    ''', out='''
        6 9
        halted
    ''')
    yield table(
        ["", "`case X:` (colon)", "`case X ->` (arrow)"],
        ["Fall-through", "Yes, until `break`", "Never"],
        ["As an expression", "Yes, with `yield`", "Yes"],
        ["Multiple labels", "`case 1: case 2:`", "`case 1, 2 ->`"],
        ["Exhaustiveness", "Only required for switch *expressions*", "Same"],
    )
    yield section("Pattern matching for `instanceof` (Java 16)", "search")
    yield snippet("java", r'''
        public class Main {
            static String describe(Object o) {
                if (o instanceof String s && !s.isEmpty())   // test + cast + bind in one step
                    return "String of length " + s.length();
                if (o instanceof Integer i)
                    return "Integer doubled " + (i * 2);
                return "something else";
            }

            public static void main(String[] args) {
                System.out.println(describe("hello"));
                System.out.println(describe(21));
                System.out.println(describe(3.5));
            }
        }
    ''', out='''
        String of length 5
        Integer doubled 42
        something else
    ''')
    yield section("Type patterns, guards & null in switch (Java 21)", "filter")
    yield snippet("java", r'''
        public class Main {
            static String classify(Object o) {
                return switch (o) {
                    case null -> "null!";                          // otherwise NPE
                    case Integer i when i < 0 -> "negative int";   // guard with `when`
                    case Integer i -> "int " + i;
                    case String s when s.isBlank() -> "blank string";
                    case String s -> "string '" + s + "'";
                    case int[] arr -> "int array of " + arr.length;
                    default -> "other: " + o.getClass().getSimpleName();
                };
            }

            public static void main(String[] args) {
                Object[] inputs = {-5, 7, " ", "hi", new int[3], 2.5, null};
                for (Object o : inputs) System.out.println(classify(o));
            }
        }
    ''', out='''
        negative int
        int 7
        blank string
        string 'hi'
        int array of 3
        other: Double
        null!
    ''')
    yield warn("Order matters: a more general pattern before a specific one (`case Integer i` before `case Integer i when i < 0`) is a *dominance* compile error. Without `case null`, a `null` selector throws `NullPointerException`.")
    yield section("Record patterns & sealed hierarchies (Java 21)", "brackets")
    yield snippet("java", r'''
        public class Main {
            sealed interface Shape permits Circle, Rect, Square {}
            record Circle(double r) implements Shape {}
            record Rect(double w, double h) implements Shape {}
            record Square(double side) implements Shape {}

            static double area(Shape s) {
                return switch (s) {                        // exhaustive: compiler knows all subtypes
                    case Circle(double r) -> Math.PI * r * r;
                    case Rect(double w, double h) -> w * h;     // deconstruct the record
                    case Square(var side) -> side * side;
                };
            }

            record Point(int x, int y) {}
            record Line(Point from, Point to) {}

            public static void main(String[] args) {
                System.out.printf("%.2f %.1f %.1f%n", area(new Circle(1)), area(new Rect(2, 3)), area(new Square(4)));
                Object o = new Line(new Point(0, 0), new Point(3, 4));
                if (o instanceof Line(Point(var x1, var y1), Point(var x2, var y2)))   // nested patterns
                    System.out.println("dx=" + (x2 - x1) + " dy=" + (y2 - y1));
            }
        }
    ''', out='''
        3.14 6.0 16.0
        dx=3 dy=4
    ''')
    yield note("Sealed interface + records + pattern `switch` = algebraic data types in Java. Add a new subtype and every non-exhaustive `switch` fails to compile — the compiler finds the code you forgot.", "Why it matters")
    yield qa("What does `yield` do in a switch expression?",
             "It returns a value from a block-bodied `case` (`case X -> { …; yield v; }`) or from a colon-style case in a switch *expression*. `return` would try to leave the enclosing method instead.")
    yield qa("Is a `default` needed in a switch expression?",
             "The switch expression must be **exhaustive**. For an `enum` or a `sealed` type covering every constant/subtype, no `default` is needed; for `int`, `String` or `Object` you need `default` (or an unconditional pattern).")
    yield qa("What happens if the selector of a switch is null?",
             "Traditionally a `NullPointerException`. From Java 21 you can add `case null` (or `case null, default ->`) to handle it explicitly.")


@topic(G, "arrays", "Arrays", "layout-grid")
def _():
    yield lead("A fixed-size, zero-indexed, contiguous container of one element type. Arrays are objects: they live on the heap and know their `length`.")
    yield define("Array", "an object holding `length` elements of the same type, accessed by index `0 … length-1` in O(1). Its size is fixed at creation; bounds are checked at runtime.")
    yield section("Declaring and creating", "plus")
    yield snippet("java", r'''
        import java.util.Arrays;

        public class Main {
            public static void main(String[] args) {
                int[] a = new int[4];                  // all zeros
                int[] b = {5, 3, 9};                   // array initializer
                String[] names = new String[2];        // all null
                boolean[] flags = new boolean[2];      // all false
                double[] d = new double[]{1.5, 2.5};

                a[0] = 42;
                System.out.println(Arrays.toString(a) + " len=" + a.length);
                System.out.println(Arrays.toString(b) + " " + Arrays.toString(names) + " " + Arrays.toString(flags) + " " + Arrays.toString(d));
                System.out.println(b);                 // prints type@hash — not the contents!
            }
        }
    ''', out=None)
    yield p("The last line prints something like `[I@1b6d3586` — `[I` means “array of int”. Always print arrays with `Arrays.toString` (or `Arrays.deepToString` for nested arrays).")
    yield table(
        ["Element type", "Default value"],
        ["`byte`, `short`, `int`, `long`", "`0`"],
        ["`float`, `double`", "`0.0`"],
        ["`char`", "`'\\u0000'`"],
        ["`boolean`", "`false`"],
        ["Any reference type", "`null`"],
    )
    yield section("2D and jagged arrays", "table")
    yield snippet("java", r'''
        import java.util.Arrays;

        public class Main {
            public static void main(String[] args) {
                int[][] grid = new int[2][3];          // 2 rows × 3 columns
                grid[1][2] = 7;
                System.out.println(Arrays.deepToString(grid));

                int[][] jagged = new int[3][];         // rows created separately
                for (int i = 0; i < jagged.length; i++) {
                    jagged[i] = new int[i + 1];
                    Arrays.fill(jagged[i], i);
                }
                System.out.println(Arrays.deepToString(jagged));

                int[][] m = {{1, 2}, {3, 4}};
                int total = 0;
                for (int[] row : m) for (int x : row) total += x;
                System.out.println("total=" + total + " rows=" + m.length + " cols=" + m[0].length);
            }
        }
    ''', out='''
        [[0, 0, 0], [0, 0, 7]]
        [[0], [1, 1], [2, 2, 2]]
        total=10 rows=2 cols=2
    ''')
    yield section("The `java.util.Arrays` toolbox", "tool")
    yield snippet("java", r'''
        import java.util.Arrays;

        public class Main {
            public static void main(String[] args) {
                int[] a = {5, 2, 8, 1, 9};
                Arrays.sort(a);                                        // dual-pivot quicksort for primitives
                System.out.println(Arrays.toString(a));
                System.out.println(Arrays.binarySearch(a, 8));         // array must be sorted
                int[] bigger = Arrays.copyOf(a, 7);                    // pads with zeros
                int[] mid = Arrays.copyOfRange(a, 1, 3);
                System.out.println(Arrays.toString(bigger) + " " + Arrays.toString(mid));

                int[] x = {1, 2}, y = {1, 2};
                System.out.println((x == y) + " " + x.equals(y) + " " + Arrays.equals(x, y));

                Integer[] boxed = {3, 1, 2};
                Arrays.sort(boxed, (p, q) -> q - p);                   // comparator needs objects
                System.out.println(Arrays.toString(boxed));
                System.out.println(Arrays.stream(a).sum() + " " + Arrays.stream(a).max().getAsInt());
            }
        }
    ''', out='''
        [1, 2, 5, 8, 9]
        3
        [1, 2, 5, 8, 9, 0, 0] [2, 5]
        false false true
        [3, 2, 1]
        25 9
    ''')
    yield warn("`array.equals(other)` is inherited from `Object` — it compares references. Use `Arrays.equals` (or `Arrays.deepEquals` for 2D).")
    yield section("`Arrays.asList` pitfalls", "alert-triangle")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                String[] arr = {"a", "b", "c"};
                List<String> view = Arrays.asList(arr);     // fixed-size view backed by arr
                view.set(0, "z");
                System.out.println(arr[0]);                  // the array changed too
                try {
                    view.add("d");
                } catch (UnsupportedOperationException e) {
                    System.out.println("cannot add: " + e.getClass().getSimpleName());
                }

                int[] prim = {1, 2, 3};
                System.out.println(Arrays.asList(prim).size());   // List<int[]> with ONE element
                List<String> copy = new ArrayList<>(Arrays.asList(arr));   // real, growable list
                copy.add("d");
                System.out.println(copy);
            }
        }
    ''', out='''
        z
        cannot add: UnsupportedOperationException
        1
        [z, b, c, d]
    ''')
    yield section("Arrays are covariant (a design flaw)", "arrows-exchange")
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                Object[] objs = new String[2];      // compiles: String[] is an Object[]
                objs[0] = "fine";
                try {
                    objs[1] = 42;                   // runtime check fails
                } catch (ArrayStoreException e) {
                    System.out.println("ArrayStoreException: " + e.getMessage());
                }
            }
        }
    ''', out='''
        ArrayStoreException: java.lang.Integer
    ''')
    yield qa("What is the difference between `length`, `length()` and `size()`?",
             "`array.length` is a field of arrays; `string.length()` is a method on `String`; `collection.size()` is a method on collections.")
    yield qa("Can an array's size change?",
             "No. To grow, allocate a bigger array and copy (`Arrays.copyOf`, `System.arraycopy`) — which is exactly what `ArrayList` does internally.")
    yield qa("Why can't you create a generic array like `new T[n]`?",
             "Arrays check element types at runtime (they are *reified*), but generic types are erased. The JVM wouldn't know what `T` is, so `new T[]` and `new List<String>[]` are compile errors. Use `List<T>` or `(T[]) new Object[n]` with care.")


@topic(G, "methods-pass-by-value", "Methods & Pass-by-Value", "function")
def _():
    yield lead("Java is **always pass-by-value**. For objects, the value passed is a copy of the *reference* — so you can mutate the object, but never reseat the caller's variable.")
    yield section("Anatomy of a method", "code")
    yield snippet("java", r'''
        public class Main {
            //  modifiers   return type  name   parameters        throws clause
            public static   int          add(   int a, int b)    /* throws … */ {
                return a + b;
            }

            static void greet(String name) {           // void: returns nothing
                if (name == null) return;              // early return
                System.out.println("Hi " + name);
            }

            public static void main(String[] args) {
                System.out.println(add(2, 3));
                greet("Asha");
                greet(null);
            }
        }
    ''', out='''
        5
        Hi Asha
    ''')
    yield table(
        ["Part", "Meaning"],
        ["**Signature**", "Name + parameter *types* (e.g. `add(int, int)`). Return type and parameter names are **not** part of it."],
        ["Access modifier", "`public`, `protected`, package-private (none), `private`"],
        ["`static`", "Belongs to the class — call as `Main.add(…)` without an object"],
        ["Return type", "Any type or `void`; every path of a non-void method must `return` or throw"],
        ["Parameters", "Local variables initialized with copies of the arguments"],
    )
    yield section("Pass-by-value, demonstrated", "arrows-exchange")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static void bump(int x) { x++; }                          // changes the copy only

            static void mutate(List<String> list) { list.add("added"); }   // same object → visible

            static void reassign(List<String> list) {
                list = new ArrayList<>();                             // local copy now points elsewhere
                list.add("lost");
            }

            static void swap(Integer a, Integer b) { Integer t = a; a = b; b = t; }

            public static void main(String[] args) {
                int n = 5;
                bump(n);
                System.out.println(n);

                List<String> items = new ArrayList<>(List.of("x"));
                mutate(items);
                reassign(items);
                System.out.println(items);

                Integer p = 1, q = 2;
                swap(p, q);
                System.out.println(p + " " + q);                      // swap is impossible this way
            }
        }
    ''', out='''
        5
        [x, added]
        1 2
    ''')
    yield flow("caller: `items` → [list object]", "call copies the reference", "param `list` → same [list object]", "`list = new …` rebinds only the param")
    yield warn("“Objects are passed by reference” is a common but wrong interview answer. The *reference* is passed by value: the method gets its own copy of the pointer.")
    yield section("Return values & multiple results", "arrow-back-up")
    yield snippet("java", r'''
        public class Main {
            record MinMax(int min, int max) {}                 // return several values via a record

            static MinMax range(int... xs) {
                int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE;
                for (int x : xs) { lo = Math.min(lo, x); hi = Math.max(hi, x); }
                return new MinMax(lo, hi);
            }

            public static void main(String[] args) {
                MinMax r = range(4, -2, 9, 0);
                System.out.println(r + " -> " + r.min() + ".." + r.max());
            }
        }
    ''', out='''
        MinMax[min=-2, max=9] -> -2..9
    ''')
    yield section("Local variables & scope", "brackets")
    yield ul(
        "Local variables have **no default value** — using one before assignment is a compile error (fields do get defaults).",
        "A variable's scope is its enclosing block `{ … }`; you can't redeclare a name that is already in scope in the same method.",
        "`var` (Java 10) infers a local's type: `var list = new ArrayList<String>();` — locals only, must be initialized.",
        "Parameters can be `final` to document that they're not reassigned.",
    )
    yield snippet("java", r'''
        public class Main {
            public static void main(String[] args) {
                int x;
                System.out.println(x);       // error: variable x might not have been initialized
            }
        }
    ''', fails=True)
    yield qa("Is Java pass-by-value or pass-by-reference?",
             "Strictly pass-by-value. Primitives: the value is copied. Objects: the reference is copied — the method can mutate the shared object but reassigning the parameter never affects the caller's variable. That's why a `swap(a, b)` method can't work.")
    yield qa("Can two methods differ only by return type?",
             "No. The signature is name + parameter types; `int f()` and `long f()` in the same class is a compile error because a call `f()` would be ambiguous.")
    yield qa("What does `static` mean for a method?",
             "It belongs to the class, not an instance: no `this`, can't access instance fields directly, and it is resolved at compile time (not overridden — only hidden).")


@topic(G, "varargs-overloading", "Varargs & Method Overloading", "adjustments-horizontal")
def _():
    yield lead("Overloading = same name, different parameter lists, chosen at *compile time*. Varargs (`T...`) lets a method accept zero or more arguments as an array.")
    yield section("Overloading", "copy")
    yield snippet("java", r'''
        public class Main {
            static int area(int side) { return side * side; }
            static int area(int w, int h) { return w * h; }
            static double area(double r) { return Math.PI * r * r; }

            public static void main(String[] args) {
                System.out.println(area(3));
                System.out.println(area(2, 5));
                System.out.printf("%.2f%n", area(1.0));
            }
        }
    ''', out='''
        9
        10
        3.14
    ''')
    yield p("Overloads must differ in the **number, types or order** of parameters. Different return types, parameter names, or exceptions alone are not enough.")
    yield section("Varargs", "dots")
    yield snippet("java", r'''
        import java.util.Arrays;

        public class Main {
            static int sum(int... nums) {                   // nums is an int[]
                int total = 0;
                for (int n : nums) total += n;
                return total;
            }

            static String tag(String name, Object... attrs) {   // varargs must be LAST
                return name + Arrays.toString(attrs);
            }

            public static void main(String[] args) {
                System.out.println(sum() + " " + sum(1) + " " + sum(1, 2, 3));
                System.out.println(sum(new int[]{4, 5}));       // can pass an array directly
                System.out.println(tag("div", "id", 7, true));
                System.out.println(String.format("%s-%s", "a", "b"));   // printf/format use varargs
            }
        }
    ''', out='''
        0 1 6
        9
        div[id, 7, true]
        a-b
    ''')
    yield ul(
        "Only **one** varargs parameter per method, and it must be the **last** one.",
        "Inside the method it is an ordinary array (possibly empty, never `null` unless the caller passes `null`).",
        "Each call allocates a new array — hot paths often add fixed-arity overloads (like `List.of(e1, e2, …)`).",
    )
    yield section("Overload resolution: which method wins?", "list-numbers")
    yield steps(
        ("Phase 1 — exact / widening", "Match without boxing or varargs; primitive widening allowed (`int` → `long` → `float` → `double`)."),
        ("Phase 2 — boxing / unboxing", "Allow `int` ↔ `Integer`, then widening of references (`Integer` → `Number` → `Object`)."),
        ("Phase 3 — varargs", "Only if nothing matched in phases 1–2."),
        ("Most specific", "If several match in the same phase, the most specific wins; if none is more specific → *ambiguous* compile error."),
    )
    yield snippet("java", r'''
        public class Main {
            static void f(long x)    { System.out.println("long (widening)"); }
            static void f(Integer x) { System.out.println("Integer (boxing)"); }
            static void f(int... x)  { System.out.println("int... (varargs)"); }

            static void g(Object o)  { System.out.println("g(Object)"); }
            static void g(String s)  { System.out.println("g(String)"); }

            static void h(double d)  { System.out.println("h(double)"); }
            static void h(Object o)  { System.out.println("h(Object)"); }

            public static void main(String[] args) {
                f(5);              // widening beats boxing beats varargs
                f(Integer.valueOf(5));
                f();
                g(null);           // String is more specific than Object
                g((Object) "hi");  // static (compile-time) type decides
                h('A');            // char → double widening wins over boxing to Character
            }
        }
    ''', out='''
        long (widening)
        Integer (boxing)
        int... (varargs)
        g(String)
        g(Object)
        h(double)
    ''')
    yield warn("Overloads are chosen from the **compile-time (static) types** of the arguments, not the runtime objects. `Object o = \"hi\"; g(o);` calls `g(Object)`. Contrast with overriding, which is chosen at runtime.")
    yield snippet("java", r'''
        public class Main {
            static void k(Integer a, long b) {}
            static void k(long a, Integer b) {}

            public static void main(String[] args) {
                k(1, 2);          // error: reference to k is ambiguous
            }
        }
    ''', fails=True)
    yield section("A classic trap: `List.remove`", "trash")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                List<Integer> list = new ArrayList<>(List.of(10, 20, 30, 1));
                list.remove(1);                       // remove(int index) → removes 20
                System.out.println(list);
                list.remove(Integer.valueOf(1));      // remove(Object) → removes the value 1
                System.out.println(list);
            }
        }
    ''', out='''
        [10, 30, 1]
        [10, 30]
    ''')
    yield qa("Can we overload `main`?",
             "Yes — you can declare other `main` methods with different parameters, but the JVM only starts the program with `public static void main(String[] args)` (or `String...`).")
    yield qa("What is the priority order in overload resolution?",
             "Exact match / primitive widening first, then boxing/unboxing, then varargs. Within a phase the most specific method is chosen; if none is most specific the call is ambiguous and won't compile.")
    yield qa("Is `void f(int[] a)` vs `void f(int... a)` a valid overload?",
             "No — varargs compiles to an array parameter, so both have the same signature `f(int[])`: a *duplicate method* compile error.")


@topic(G, "recursion", "Recursion", "recycle")
def _():
    yield lead("A method that calls itself on a smaller input. Every recursion needs a **base case**; each call pushes a stack frame, so depth is limited.")
    yield define("Recursion", "solving a problem by reducing it to smaller instances of the same problem, until a *base case* can be answered directly.")
    yield section("The two parts", "stairs")
    yield snippet("java", r'''
        public class Main {
            static long factorial(int n) {
                if (n <= 1) return 1;                 // base case
                return n * factorial(n - 1);          // recursive case: smaller input
            }

            static int sumDigits(int n) {
                return n < 10 ? n : n % 10 + sumDigits(n / 10);
            }

            static String reverse(String s) {
                return s.isEmpty() ? "" : reverse(s.substring(1)) + s.charAt(0);
            }

            public static void main(String[] args) {
                System.out.println(factorial(5) + " " + factorial(20));
                System.out.println(sumDigits(9875));
                System.out.println(reverse("stack"));
            }
        }
    ''', out='''
        120 2432902008176640000
        29
        kcats
    ''')
    yield section("The call stack", "stack-2")
    yield steps(
        ("`factorial(3)` called", "Frame pushed: `n=3`, waiting on `factorial(2)`."),
        ("`factorial(2)`", "Frame pushed: `n=2`, waiting on `factorial(1)`."),
        ("`factorial(1)` — base case", "Returns `1`; frame popped."),
        ("Unwinding", "`2 * 1 = 2` returned, then `3 * 2 = 6`. Each frame pops as it returns."),
    )
    yield snippet("java", r'''
        public class Main {
            static int depth = 0;

            static void dive() {
                depth++;
                dive();                               // no base case
            }

            public static void main(String[] args) {
                try {
                    dive();
                } catch (StackOverflowError e) {      // an Error, not an Exception
                    System.out.println("StackOverflowError after " + (depth > 1000 ? "thousands of" : "few") + " calls");
                }
            }
        }
    ''', out='''
        StackOverflowError after thousands of calls
    ''')
    yield warn("The JVM does **not** perform tail-call optimization. Even a tail-recursive method uses one frame per call, so deep recursion (e.g. 100 000 levels) overflows the default ~512 KB–1 MB thread stack. Convert to a loop, or run in a thread with a bigger stack.")
    yield section("Memoization: from exponential to linear", "bolt")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static int calls = 0;

            static long fibNaive(int n) {
                calls++;
                return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2);    // O(2^n)
            }

            static Map<Integer, Long> memo = new HashMap<>();
            static long fibMemo(int n) {
                if (n < 2) return n;
                Long cached = memo.get(n);
                if (cached != null) return cached;
                long v = fibMemo(n - 1) + fibMemo(n - 2);                // O(n)
                memo.put(n, v);
                return v;
            }

            static long fibIter(int n) {                                 // O(n) time, O(1) space
                long a = 0, b = 1;
                for (int i = 0; i < n; i++) { long t = a + b; a = b; b = t; }
                return a;
            }

            public static void main(String[] args) {
                System.out.println(fibNaive(25) + " in " + calls + " calls");
                System.out.println(fibMemo(90) + " " + fibIter(90));
            }
        }
    ''', out='''
        75025 in 242785 calls
        2880067194370816120 2880067194370816120
    ''')
    yield note("Don't use `memo.computeIfAbsent(n, k -> fib(k-1) + fib(k-2))` for recursive memoization on a `HashMap` — modifying the map inside its own `computeIfAbsent` throws `ConcurrentModificationException` (Java 9+).", "Gotcha")
    yield section("Classic recursive patterns", "binary-tree")
    yield snippet("java", r'''
        import java.util.*;

        public class Main {
            static int binarySearch(int[] a, int target, int lo, int hi) {
                if (lo > hi) return -1;
                int mid = (lo + hi) >>> 1;
                if (a[mid] == target) return mid;
                return a[mid] < target ? binarySearch(a, target, mid + 1, hi)
                                       : binarySearch(a, target, lo, mid - 1);
            }

            static void subsets(int[] nums, int i, Deque<Integer> cur, List<String> out) {
                if (i == nums.length) { out.add(cur.toString()); return; }
                subsets(nums, i + 1, cur, out);            // exclude nums[i]
                cur.addLast(nums[i]);
                subsets(nums, i + 1, cur, out);            // include nums[i]
                cur.removeLast();                          // backtrack
            }

            static void hanoi(int n, char from, char to, char via, List<String> moves) {
                if (n == 0) return;
                hanoi(n - 1, from, via, to, moves);
                moves.add(from + ">" + to);
                hanoi(n - 1, via, to, from, moves);
            }

            public static void main(String[] args) {
                System.out.println(binarySearch(new int[]{1, 3, 5, 7, 9}, 7, 0, 4));
                List<String> out = new ArrayList<>();
                subsets(new int[]{1, 2, 3}, 0, new ArrayDeque<>(), out);
                System.out.println(out);
                List<String> moves = new ArrayList<>();
                hanoi(3, 'A', 'C', 'B', moves);
                System.out.println(moves.size() + " moves: " + moves);
            }
        }
    ''', out='''
        3
        [[], [3], [2], [2, 3], [1], [1, 3], [1, 2], [1, 2, 3]]
        7 moves: [A>C, A>B, C>B, A>C, B>A, B>C, A>C]
    ''')
    yield table(
        ["Recursion", "Iteration"],
        ["Natural for trees, graphs, divide & conquer, backtracking", "Natural for linear scans"],
        ["O(depth) stack space", "O(1) extra space usually"],
        ["Risk of `StackOverflowError`", "No stack risk"],
        ["Method-call overhead per step", "Faster in the JVM"],
    )
    yield qa("What happens if a recursive method has no base case?",
             "It recurses until the thread's stack is exhausted and the JVM throws `StackOverflowError` (a subclass of `VirtualMachineError`, i.e. an `Error`).")
    yield qa("Does Java optimize tail recursion?",
             "No. The JVM spec has no tail-call elimination (partly to keep stack traces and security checks intact), so rewrite deep tail recursion as a loop.")
    yield qa("How do you find the time complexity of a recursive function?",
             "Write the recurrence: e.g. naive Fibonacci `T(n) = T(n-1) + T(n-2) + O(1)` → O(2ⁿ) (tighter: φⁿ); binary search `T(n) = T(n/2) + O(1)` → O(log n); merge sort `T(n) = 2T(n/2) + O(n)` → O(n log n) (Master theorem).")
