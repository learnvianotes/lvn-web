from kit import *

G = "Language Basics"


@topic(G, "types-variables", "Fundamental Types & Variables", "variable")
def _():
    yield lead("Every variable has a fixed type chosen at compile time. The type decides its size, its range and which operations are legal.")
    yield section("Built-in types", "box")
    yield table(
        ["Type", "Typical size (64-bit)", "Notes"],
        ["`bool`", "1 byte", "`true` / `false`"],
        ["`char`", "1 byte", "A character *and* a small integer; signedness is platform-defined"],
        ["`short`", "2 bytes", "At least 16 bits"],
        ["`int`", "4 bytes", "At least 16 bits — in practice 32"],
        ["`long`", "8 bytes (Linux/macOS), 4 (Windows)", "At least 32 bits"],
        ["`long long`", "8 bytes", "At least 64 bits — use for big sums"],
        ["`float`", "4 bytes", "~7 significant digits"],
        ["`double`", "8 bytes", "~15–16 significant digits — the default for decimals"],
        ["`long double`", "8–16 bytes", "Extended precision where supported"],
        ["`std::size_t`", "8 bytes", "Unsigned; the type of `sizeof` and container sizes"],
    )
    yield snippet("cpp", r'''
        #include <climits>
        #include <cstdint>
        #include <iostream>
        #include <limits>

        int main() {
            std::cout << sizeof(int) << ' ' << sizeof(long long) << ' ' << sizeof(double) << '\n';
            std::cout << INT_MAX << ' ' << std::numeric_limits<int>::min() << '\n';
            std::cout << std::numeric_limits<long long>::max() << '\n';
            std::int32_t a = 1;          // exact-width types from <cstdint>
            std::uint64_t b = 1;
            std::cout << sizeof(a) << ' ' << sizeof(b) << '\n';
        }
    ''', out='''
        4 8 8
        2147483647 -2147483648
        9223372036854775807
        4 8
    ''')
    yield note("Sizes of `int`, `long` and friends are only *minimums* in the standard. When the exact width matters (file formats, hashing, bit tricks), use `std::int32_t`, `std::uint64_t`, … from `<cstdint>`.")
    yield section("Ways to initialise", "equal")
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            int a = 5;        // copy initialisation
            int b(5);         // direct initialisation
            int c{5};         // brace (uniform) initialisation — C++11
            int d{};          // value-initialised → 0
            int e = {5};      // copy-list initialisation
            std::cout << a << b << c << d << e << '\n';
        }
    ''', out="55505")
    yield p("Brace initialisation **refuses narrowing conversions** — a lossy conversion becomes a compile error instead of a silent bug:")
    yield snippet("cpp", r'''
        int main() {
            double price = 9.99;
            int cents{price};     // error: narrowing conversion from double to int
            return cents;
        }
    ''', fails=True)
    yield output('''
        error: type 'double' cannot be narrowed to 'int' in initializer list [-Wc++11-narrowing]
    ''', caption="Compiler error")
    yield warn("A local variable of built-in type that is not initialised holds an *indeterminate* value — reading it is undefined behaviour. Always initialise: `int count = 0;` or `int count{};`.")
    yield section("Integer overflow & unsigned wrap-around", "alert-triangle")
    yield snippet("cpp", r'''
        #include <climits>
        #include <iostream>
        int main() {
            unsigned int u = 0;
            u = u - 1;                        // unsigned arithmetic wraps modulo 2^32
            std::cout << u << '\n';
            long long big = 1LL * INT_MAX * 2; // widen *before* multiplying
            std::cout << big << '\n';
            int s = -1;
            unsigned int one = 1;
            std::cout << (s < static_cast<int>(one)) << '\n';   // compare as signed
        }
    ''', out='''
        4294967295
        4294967294
        1
    ''')
    yield snippet("cpp", r'''
        #include <climits>
        #include <iostream>
        int main() {
            int x = INT_MAX;
            x = x + 1;                // signed overflow: undefined behaviour
            std::cout << x << '\n';
        }
    ''', fails=True, caption="C++ — signed overflow (UBSan aborts)")
    yield output('''
        runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
    ''', caption="UBSan")
    yield warn("*Unsigned* overflow is well-defined (wraps). *Signed* overflow is **undefined behaviour** — the optimiser may assume it never happens. Compute `a * b` in `long long` when it can exceed ~2·10⁹.")
    yield section("Literals", "number")
    yield table(
        ["Literal", "Type / meaning"],
        ["`42`, `42u`, `42L`, `42LL`, `42ULL`", "`int`, `unsigned`, `long`, `long long`, `unsigned long long`"],
        ["`0x2A`, `052`, `0b101010`", "Hex, octal, binary (C++14) — all 42"],
        ["`1'000'000`", "Digit separators (C++14)"],
        ["`3.14`, `3.14f`, `1e9`", "`double`, `float`, `double`"],
        ["`'a'`, `\"abc\"`", "`char`, `const char[4]` (array incl. `'\\0'`)"],
        ["`\"abc\"s`, `\"abc\"sv`", "`std::string`, `std::string_view` (with `using namespace std::literals`)"],
        ["`nullptr`", "The null pointer literal (type `std::nullptr_t`)"],
    )
    yield section("Floating point is approximate", "decimal")
    yield snippet("cpp", r'''
        #include <cmath>
        #include <iostream>
        int main() {
            double a = 0.1 + 0.2;
            std::cout << (a == 0.3) << '\n';                   // 0: not exactly equal
            std::cout << (std::fabs(a - 0.3) < 1e-9) << '\n';  // 1: compare with a tolerance
            std::cout << 7 / 2 << ' ' << 7 / 2.0 << '\n';      // integer vs floating division
        }
    ''', out='''
        0
        1
        3 3.5
    ''')
    yield qa("What is the difference between int x; and int x{}; inside a function?",
             "`int x;` leaves `x` uninitialised — reading it is undefined behaviour. `int x{};` *value-initialises* it to `0`. For class types with a default constructor both call that constructor.")
    yield qa("Why prefer brace initialisation?",
             "It works the same way for every type (built-ins, aggregates, classes, containers), it rejects narrowing conversions, and it avoids the *most vexing parse* (`Widget w();` declares a function, `Widget w{};` creates an object). The one gotcha: for types with an `initializer_list` constructor, `std::vector<int> v{3, 0}` means the elements `{3, 0}`, not “3 zeros”.")


@topic(G, "auto-const-constexpr", "auto, const & constexpr", "lock")
def _():
    yield lead("`auto` lets the compiler deduce a type; `const` promises a value won't change; `constexpr` asks for it to be computed at compile time.")
    yield section("`auto` type deduction", "wand")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <string>
        #include <vector>

        int main() {
            auto n = 42;              // int
            auto pi = 3.14;           // double
            auto s = std::string("hi");
            std::map<std::string, std::vector<int>> index{{"a", {1, 2}}};
            for (const auto& [key, list] : index)   // instead of spelling out the pair type
                std::cout << key << ": " << list.size() << '\n';
            std::cout << n << ' ' << pi << ' ' << s << '\n';
        }
    ''', out='''
        a: 2
        42 3.14 hi
    ''')
    yield table(
        ["You write", "Deduced as", "Why"],
        ["`auto x = ci;` (where `const int ci`)", "`int`", "Top-level `const` and references are dropped — you get a copy"],
        ["`auto& r = ci;`", "`const int&`", "A reference keeps `const`"],
        ["`const auto& r = expr;`", "`const T&`", "Read-only view, no copy — the default in range-`for`"],
        ["`auto* p = &x;`", "`int*`", "Documents that it's a pointer"],
        ["`auto&& r = expr;`", "`T&` or `T&&`", "Forwarding reference — binds to anything"],
        ["`auto v = {1, 2};`", "`std::initializer_list<int>`", "Surprise! Braces with `=` deduce an initializer list"],
    )
    yield warn("`for (auto x : bigStrings)` copies every element. Use `const auto&` to read and `auto&` to modify.")
    yield section("`const`", "lock")
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            const int maxUsers = 100;       // must be initialised; can't be changed later
            int value = 5;
            const int* p1 = &value;         // pointer to const int: *p1 is read-only
            int* const p2 = &value;         // const pointer: p2 can't be re-seated
            *p2 = 6;                        // OK — the int itself isn't const
            p1 = &maxUsers;                 // OK — p1 itself isn't const
            std::cout << *p1 << ' ' << value << '\n';
        }
    ''', out="100 6")
    yield note("Read pointer declarations **right to left**: `const int* p` → “p is a pointer to an int that is const”; `int* const p` → “p is a const pointer to int”. `const int* const p` → both.", "Reading trick")
    yield snippet("cpp", r'''
        int main() {
            const int limit = 10;
            limit = 20;           // error: cannot assign to a const variable
            return limit;
        }
    ''', fails=True)
    yield section("`constexpr` — compile-time values & functions", "cpu")
    yield snippet("cpp", r'''
        #include <array>
        #include <iostream>

        constexpr long long factorial(int n) {       // may run at compile time
            return n <= 1 ? 1 : n * factorial(n - 1);
        }

        int main() {
            constexpr auto f10 = factorial(10);      // computed by the compiler
            static_assert(factorial(5) == 120);      // checked at compile time
            std::array<int, factorial(4)> arr{};     // usable as an array size
            int n = 6;
            std::cout << f10 << ' ' << arr.size() << ' ' << factorial(n) << '\n';   // also callable at run time
        }
    ''', out="3628800 24 720")
    yield table(
        ["Keyword", "Meaning"],
        ["`const`", "Can't be modified after initialisation. Value may be known only at run time."],
        ["`constexpr` variable", "Must be a compile-time constant (implies `const`)."],
        ["`constexpr` function", "*Can* be evaluated at compile time if its arguments are constants; otherwise runs normally."],
        ["`consteval` function (C++20)", "*Must* be evaluated at compile time (an “immediate function”)."],
        ["`constinit` (C++20)", "A static variable must be initialised at compile time, but can change later."],
    )
    yield snippet("cpp", r'''
        #include <iostream>
        consteval int square(int x) { return x * x; }
        int main() {
            constexpr int s = square(9);   // fine: argument is a constant
            std::cout << s << '\n';
            // int n = 3; square(n);       // error: n is not a constant expression
        }
    ''', out="81")
    yield section("`const` everywhere it applies", "shield-check")
    yield dodont("Make variables, parameters (`const std::string&`) and member functions `const` whenever they don't mutate — the compiler then enforces your intent.", "Using `#define MAX 100` for constants — macros ignore scope and types; use `constexpr int kMax = 100;`")
    yield qa("What's the difference between const and constexpr?",
             "`const` means *read-only after initialisation*; the initial value may come from run-time input. `constexpr` means the value is a *compile-time constant* (or, for functions, that they can be evaluated at compile time). Every `constexpr` variable is `const`, but not the other way round.")
    yield qa("Does auto make C++ dynamically typed?",
             "No. The type is deduced once, at compile time, from the initialiser, and never changes. `auto x = 1; x = \"hi\";` is a compile error.")


@topic(G, "operators-conversions", "Operators & Type Conversions", "math-symbols")
def _():
    yield lead("C++ operators behave like C's, with a few traps: integer division, precedence of bitwise ops, and implicit conversions between signed/unsigned and int/double.")
    yield section("Operator overview", "list")
    yield table(
        ["Kind", "Operators", "Notes"],
        ["Arithmetic", "`+ - * / %`", "`int / int` truncates toward zero; `%` takes the sign of the left operand"],
        ["Increment", "`++x`, `x++`", "Prefix returns the new value (by reference); postfix returns a copy of the old one"],
        ["Comparison", "`== != < <= > >=`, `<=>` (C++20)", "`<=>` (spaceship) returns an ordering"],
        ["Logical", "`&& || !`", "Short-circuit evaluation"],
        ["Bitwise", "`& | ^ ~ << >>`", "Lower precedence than `==` — parenthesise!"],
        ["Assignment", "`= += -= *= /= %= &= |= ^= <<= >>=`", "Return a reference to the left side"],
        ["Other", "`?:`, `,`, `sizeof`, `::`, `.`, `->`, `.*`, `->*`", "`::` is scope resolution"],
    )
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            std::cout << 7 / 2 << ' ' << -7 / 2 << ' ' << 7 % 3 << ' ' << -7 % 3 << '\n';
            int i = 5;
            int a = i++;          // a = 5, i = 6
            int b = ++i;          // i = 7, b = 7
            std::cout << a << ' ' << b << ' ' << i << '\n';
            int flags = 0b0110;
            std::cout << ((flags & 0b0100) != 0) << ' ' << (flags | 1) << ' ' << (flags ^ 0b1111) << ' ' << (1 << 10) << '\n';
            int x = 0;
            bool ok = (x != 0) && (10 / x > 1);   // short-circuit: division never runs
            std::cout << std::boolalpha << ok << '\n';
        }
    ''', out='''
        3 -3 1 -1
        5 7 7
        1 7 9 1024
        false
    ''')
    yield warn("`if (flags & MASK == 0)` parses as `flags & (MASK == 0)` because `==` binds tighter than `&`. Always write `(flags & MASK) == 0`.")
    yield section("Implicit conversions", "transform")
    yield ul(
        "**Integral promotion:** `char`, `short`, `bool` are promoted to `int` in arithmetic.",
        "**Usual arithmetic conversions:** in `int + double` the `int` becomes `double`; in `int + unsigned` the `int` becomes **unsigned**.",
        "**Narrowing:** `double → int` truncates, `long long → int` may lose bits — allowed with `=`, rejected with `{}`.",
    )
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            char c = 'A';
            std::cout << c + 1 << ' ' << static_cast<char>(c + 1) << '\n';   // promoted to int
            double d = 9.99;
            int t = static_cast<int>(d);                                     // truncates toward zero
            std::cout << t << ' ' << static_cast<int>(-9.99) << '\n';
            std::vector<int> v;                                              // v.size() is unsigned
            std::cout << v.size() - 1 << '\n';                               // wraps: not -1!
            std::cout << static_cast<long long>(v.size()) - 1 << '\n';
        }
    ''', out='''
        66 B
        9 -9
        18446744073709551615
        -1
    ''')
    yield warn("`for (int i = 0; i < v.size() - 1; ++i)` on an empty vector loops ~2⁶⁴ times: `v.size() - 1` wraps to a huge unsigned value. Use `i + 1 < v.size()` or `std::ssize(v)` (C++20, signed).")
    yield section("Explicit casts", "arrows-exchange")
    yield table(
        ["Cast", "Use for"],
        ["`static_cast<T>(x)`", "Ordinary, checked-at-compile-time conversions (numeric, up/down a class hierarchy without check)"],
        ["`dynamic_cast<T>(x)`", "Safe down-casting of polymorphic types, checked at run time"],
        ["`const_cast<T>(x)`", "Add/remove `const` (rarely legitimate)"],
        ["`reinterpret_cast<T>(x)`", "Reinterpret bits/pointers (low-level, unsafe)"],
        ["`(T)x` / `T(x)`", "C-style cast: tries all of the above — avoid, it hides intent"],
    )
    yield p("See **Casts & RTTI** for the full story on the four named casts.")
    yield section("Evaluation order", "sort-ascending")
    yield warn("Precedence says how an expression is *grouped*, not in which order operands are *evaluated*. `f() + g()` may call `g` first, and `i = i++ + 1`-style expressions that modify a variable twice without sequencing are undefined (or unspecified) — split them into separate statements.")
    yield qa("What is the difference between ++i and i++?",
             "`++i` increments and returns the variable itself (an lvalue). `i++` makes a copy of the old value, increments, and returns the copy. For `int` the compiler optimises both identically, but for iterators and class types `++it` avoids a copy — prefer it when you don't need the old value.")


@topic(G, "control-flow", "Control Flow", "arrows-split")
def _():
    yield lead("`if`, `switch`, `for`, `while`, `do-while` — plus the modern additions: range-based `for`, `if`/`switch` with an initializer, and `[[fallthrough]]`.")
    yield section("`if` / `else` and the ternary", "git-branch")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <string>

        int main() {
            int score = 72;
            if (score >= 90)      std::cout << "A\n";
            else if (score >= 70) std::cout << "B\n";
            else                  std::cout << "C\n";

            std::string parity = (score % 2 == 0) ? "even" : "odd";
            std::cout << parity << '\n';

            std::map<std::string, int> stock{{"apple", 3}};
            if (auto it = stock.find("apple"); it != stock.end())   // C++17: init; condition
                std::cout << "apples: " << it->second << '\n';      // `it` is scoped to the if/else
        }
    ''', out='''
        B
        even
        apples: 3
    ''')
    yield section("`switch`", "switch")
    yield snippet("cpp", r'''
        #include <iostream>
        void describe(char op) {
            switch (op) {
                case '+':
                case '-':
                    std::cout << op << " is additive\n";
                    break;
                case '*':
                    std::cout << "* is multiplicative\n";
                    [[fallthrough]];              // intentional: silences the warning
                case '/':
                    std::cout << "  (binary operator)\n";
                    break;
                default:
                    std::cout << op << " unknown\n";
            }
        }
        int main() { describe('-'); describe('*'); describe('?'); }
    ''', out='''
        - is additive
        * is multiplicative
          (binary operator)
        ? unknown
    ''')
    yield warn("`switch` works only on integral and enum types (not `std::string`), and a missing `break` falls through into the next case. You can't declare an initialised variable across case labels without braces: `case 1: { int x = 5; … } break;`.")
    yield section("Loops", "repeat")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v{3, 1, 4, 1, 5};
            for (std::size_t i = 0; i < v.size(); ++i) std::cout << v[i];   // classic index loop
            std::cout << '\n';
            for (int x : v) std::cout << x * 2 << ' ';                       // range-based for
            std::cout << '\n';
            for (int& x : v) x += 10;                                        // reference: modify in place
            std::cout << v.front() << '\n';

            int n = 1;
            while (n < 100) n *= 3;
            std::cout << n << '\n';

            int tries = 0;
            do { ++tries; } while (tries < 0);   // body runs at least once
            std::cout << tries << '\n';
        }
    ''', out='''
        31415
        6 2 8 2 10
        13
        243
        1
    ''')
    yield section("`break`, `continue` and nested loops", "player-skip-forward")
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            for (int i = 1; i <= 10; ++i) {
                if (i % 2 == 0) continue;   // skip evens
                if (i > 7) break;           // stop the loop
                std::cout << i << ' ';
            }
            std::cout << '\n';

            bool found = false;              // leaving nested loops: use a flag (or a function + return)
            for (int r = 0; r < 3 && !found; ++r)
                for (int c = 0; c < 3; ++c)
                    if (r * c == 2) { std::cout << r << ',' << c << '\n'; found = true; break; }
        }
    ''', out='''
        1 3 5 7
        1,2
    ''')
    yield table(
        ["Loop", "Use when"],
        ["`for (init; cond; step)`", "You need the index or a custom step"],
        ["`for (auto& x : range)`", "Visit every element — the default choice"],
        ["`while (cond)`", "Number of iterations isn't known up front"],
        ["`do { } while (cond);`", "Body must run at least once (e.g. menu loops)"],
    )
    yield qa("How does the range-based for loop work under the hood?",
             "`for (auto x : r) body` is rewritten to roughly `auto&& __r = r; for (auto it = begin(__r), e = end(__r); it != e; ++it) { auto x = *it; body }`. So it works for any type with `begin()`/`end()` — arrays, all STL containers, `std::string`, ranges and your own classes.")


@topic(G, "enums", "enum & enum class", "list-numbers")
def _():
    yield lead("Enumerations give names to a fixed set of integral values. Prefer the scoped `enum class` (C++11): its names don't leak and it doesn't convert to `int` silently.")
    yield section("Unscoped `enum` (C-style)", "list")
    yield snippet("cpp", r'''
        #include <iostream>
        enum Color { Red, Green, Blue };          // Red=0, Green=1, Blue=2
        enum Status { Ok = 200, NotFound = 404 };  // explicit values

        int main() {
            Color c = Green;
            int n = c;                    // implicit conversion to int
            std::cout << n << ' ' << Blue + 1 << ' ' << NotFound << '\n';
        }
    ''', out="1 3 404")
    yield warn("Unscoped enumerators are injected into the surrounding scope — two enums can't both have a `None` — and they compare/convert freely with integers and each other.")
    yield section("Scoped `enum class`", "lock")
    yield snippet("cpp", r'''
        #include <cstdint>
        #include <iostream>
        #include <string_view>

        enum class Direction : std::uint8_t { North, East, South, West };   // underlying type: 1 byte

        std::string_view name(Direction d) {
            switch (d) {
                case Direction::North: return "North";
                case Direction::East:  return "East";
                case Direction::South: return "South";
                case Direction::West:  return "West";
            }
            return "?";
        }

        Direction turnRight(Direction d) {
            return static_cast<Direction>((static_cast<int>(d) + 1) % 4);   // explicit conversions
        }

        int main() {
            Direction d = Direction::West;
            std::cout << name(d) << " -> " << name(turnRight(d)) << '\n';
            std::cout << sizeof(Direction) << ' ' << static_cast<int>(Direction::South) << '\n';
        }
    ''', out='''
        West -> North
        1 2
    ''')
    yield snippet("cpp", r'''
        enum class Fruit { Apple, Pear };
        int main() {
            int x = Fruit::Apple;      // error: no implicit conversion to int
            return x;
        }
    ''', fails=True)
    yield table(
        ["", "`enum`", "`enum class`"],
        ["Names scoped?", "No — `Red`", "Yes — `Color::Red`"],
        ["Implicit → `int`?", "Yes", "No — needs `static_cast`"],
        ["Underlying type", "Implementation-chosen (can be fixed)", "`int` by default, can be fixed (`: std::uint8_t`)"],
        ["Forward-declarable", "Only with fixed underlying type", "Yes"],
    )
    yield note("With `-Wall`, a `switch` over an enum that misses an enumerator (and has no `default`) triggers a warning — a free exhaustiveness check. C++20 also allows `using enum Direction;` inside a scope to drop the prefix.")
    yield qa("Why prefer enum class over plain enum?",
             "Scoping (no name clashes), strong typing (no accidental comparison with `int` or with another enum), and a guaranteed underlying type that allows forward declaration. You opt into conversions explicitly with `static_cast`.")


@topic(G, "namespaces", "Namespaces", "folders")
def _():
    yield lead("A namespace is a named scope that groups related declarations and prevents name clashes between libraries.")
    yield section("Declaring and using", "code")
    yield snippet("cpp", r'''
        #include <iostream>

        namespace geometry {
            constexpr double pi = 3.14159;
            double circleArea(double r) { return pi * r * r; }

            namespace units {                      // nested namespace
                double toCm(double inches) { return inches * 2.54; }
            }
        }

        namespace app::config {                     // C++17 nested-namespace shorthand
            int retries = 3;
        }

        int main() {
            std::cout << geometry::circleArea(1.0) << '\n';
            std::cout << geometry::units::toCm(10) << '\n';
            namespace gu = geometry::units;         // namespace alias
            std::cout << gu::toCm(1) << ' ' << app::config::retries << '\n';
            using geometry::pi;                     // using-declaration: one name
            std::cout << pi << '\n';
        }
    ''', out='''
        3.14159
        25.4
        2.54 3
        3.14159
    ''')
    yield section("Anonymous namespaces & `::`", "eye-off")
    yield snippet("cpp", r'''
        #include <iostream>

        namespace {                    // anonymous: visible only in this .cpp (internal linkage)
            int helperCalls = 0;
            void helper() { ++helperCalls; }
        }

        int value = 1;                 // global

        int main() {
            int value = 2;             // local shadows the global
            helper();
            helper();
            std::cout << value << ' ' << ::value << ' ' << helperCalls << '\n';   // ::value = global scope
        }
    ''', out="2 1 2")
    yield table(
        ["Construct", "Effect"],
        ["`ns::name`", "Qualified access"],
        ["`using ns::name;`", "Using-declaration: brings one name into scope"],
        ["`using namespace ns;`", "Using-directive: makes *all* names visible (risk of ambiguity)"],
        ["`namespace a = long::name;`", "Alias"],
        ["`namespace { … }`", "Anonymous — replaces `static` for file-local functions/variables"],
        ["`inline namespace v2 { … }`", "Members are also visible in the enclosing namespace (library versioning)"],
    )
    yield section("Argument-dependent lookup (ADL)", "search")
    yield p("When you call an unqualified function, C++ also searches the namespaces of the argument types. That's why `std::cout << x` finds `std::operator<<` and `swap(a, b)` can find a custom `swap` next to your type.")
    yield snippet("cpp", r'''
        #include <iostream>
        namespace shop {
            struct Item { int price; };
            void print(const Item& i) { std::cout << "Item $" << i.price << '\n'; }
        }
        int main() {
            shop::Item it{5};
            print(it);        // no `shop::` needed — found by ADL via the argument's type
        }
    ''', out="Item $5")
    yield dodont("Put your project's code in its own namespace; in `.cpp` files, `using` specific names is fine.", "`using namespace` at global scope in a header")
    yield qa("What is the difference between an anonymous namespace and static at file scope?",
             "Both give *internal linkage* (the name is private to the translation unit). The anonymous namespace is the modern, more general choice: it also works for types (classes, enums), whereas `static` applies only to functions and variables.")


@topic(G, "structured-bindings", "Structured Bindings", "brackets-contain")
def _():
    yield lead("C++17 `auto [a, b] = expr;` unpacks a pair, tuple, array or plain struct into named variables in one line.")
    yield section("What can be unpacked", "package")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <string>
        #include <tuple>

        struct Point { int x; int y; };

        std::tuple<int, double, std::string> record() { return {7, 9.5, "ok"}; }

        int main() {
            auto [x, y] = Point{3, 4};                  // aggregate struct: by member order
            std::cout << x + y << '\n';

            int arr[3] = {10, 20, 30};
            auto [a, b, c] = arr;                        // C array
            std::cout << a << b << c << '\n';

            auto [id, score, status] = record();         // tuple
            std::cout << id << ' ' << score << ' ' << status << '\n';

            std::map<std::string, int> ages{{"ada", 36}, {"bob", 25}};
            for (const auto& [name, age] : ages)         // pairs in a map
                std::cout << name << '=' << age << ' ';
            std::cout << '\n';

            if (auto [it, inserted] = ages.insert({"ada", 99}); !inserted)
                std::cout << "ada already " << it->second << '\n';
        }
    ''', out='''
        7
        102030
        7 9.5 ok
        ada=36 bob=25
        ada already 36
    ''')
    yield section("Copy or reference?", "link")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <utility>
        int main() {
            std::pair<int, int> p{1, 2};
            auto [a, b] = p;      // binds to a hidden *copy* of p
            a = 100;
            auto& [c, d] = p;     // binds to p itself
            c = 50;
            std::cout << p.first << ' ' << p.second << '\n';
        }
    ''', out="50 2")
    yield ul(
        "`auto [..]` — copy of the whole object; `auto& [..]` — refer to the original; `const auto& [..]` — read-only view.",
        "The number of names must match exactly; you can't skip one (use a dummy name like `_` or `[[maybe_unused]]`).",
        "For your own classes with private members, enable it by specialising `std::tuple_size`/`std::tuple_element` and providing `get<N>` (advanced).",
    )
    yield qa("How would you swap-return two values from a function in modern C++?",
             "Return a `std::pair`/`std::tuple` or, better, a small named `struct`, and unpack at the call site with structured bindings: `auto [quotient, remainder] = divide(17, 5);`.")


@topic(G, "preprocessor-macros", "Preprocessor & Macros", "hash")
def _():
    yield lead("Before compilation, the preprocessor rewrites the source text: it pastes headers, expands macros and keeps or drops code with `#if`. It knows nothing about types or scopes.")
    yield section("Directives", "list")
    yield table(
        ["Directive", "Does"],
        ["`#include <x>` / `#include \"x\"`", "Paste a header (system paths / project paths first)"],
        ["`#define NAME value`", "Object-like macro: textual replacement"],
        ["`#define F(a, b) (…)`", "Function-like macro"],
        ["`#undef NAME`", "Remove a macro"],
        ["`#if` / `#ifdef` / `#ifndef` / `#elif` / `#else` / `#endif`", "Conditional compilation"],
        ["`#pragma once`", "Include guard (non-standard but universal)"],
        ["`#error msg`", "Stop compilation with a message"],
    )
    yield section("Macros and their traps", "alert-triangle")
    yield snippet("cpp", r'''
        #include <iostream>

        #define SQUARE_BAD(x) x * x
        #define SQUARE(x) ((x) * (x))
        #define MAX(a, b) ((a) > (b) ? (a) : (b))

        constexpr int square(int x) { return x * x; }       // the C++ way: typed, scoped, evaluated once

        int main() {
            std::cout << SQUARE_BAD(2 + 3) << ' ' << SQUARE(2 + 3) << ' ' << square(2 + 3) << '\n';   // 2 + 3 * 2 + 3
            int i = 5;
            int m = MAX(i++, 0);                             // i++ is evaluated TWICE
            std::cout << m << ' ' << i << '\n';
        }
    ''', out='''
        11 25 25
        6 7
    ''')
    yield warn("Macros ignore scope and types, evaluate arguments multiple times and are invisible to the debugger. Use `constexpr` variables, `inline`/`constexpr` functions, templates and `enum class` instead.")
    yield section("Where macros are still useful", "tool")
    yield snippet("cpp", r'''
        #include <iostream>

        #define STRINGIFY(x) #x                         // # turns an argument into a string literal
        #define CONCAT(a, b) a##b                       // ## pastes tokens
        #define LOG_VAR(v) std::cout << #v << " = " << (v) << '\n'

        #ifndef NDEBUG
        #define DEBUG_ONLY(code) code
        #else
        #define DEBUG_ONLY(code)
        #endif

        int main() {
            int CONCAT(user, Count) = 3;                 // declares userCount
            LOG_VAR(userCount * 2);
            std::cout << STRINGIFY(hello world) << '\n';
            std::cout << __LINE__ << ' ' << (__cplusplus >= 202002L) << '\n';   // predefined macros
            DEBUG_ONLY(std::cout << "debug build\n";)
        }
    ''', out='''
        userCount * 2 = 6
        hello world
        17 1
        debug build
    ''')
    yield table(
        ["Predefined macro", "Value"],
        ["`__FILE__`, `__LINE__`", "Current file name and line (C++20: prefer `std::source_location`)"],
        ["`__cplusplus`", "Standard version, e.g. `202002L` for C++20"],
        ["`NDEBUG`", "Defined in release builds (`-DNDEBUG`) — disables `assert`"],
        ["`_WIN32`, `__linux__`, `__APPLE__`", "Target platform"],
        ["`__GNUC__`, `__clang__`, `_MSC_VER`", "Compiler"],
    )
    yield section("`assert`", "circle-check")
    yield snippet("cpp", r'''
        #include <cassert>
        #include <iostream>
        int divide(int a, int b) {
            assert(b != 0 && "divisor must be non-zero");   // checked only when NDEBUG is not defined
            return a / b;
        }
        int main() { std::cout << divide(10, 2) << '\n'; }
    ''', out="5")
    yield qa("Why prefer constexpr over #define for constants?",
             "A `constexpr` constant has a type (so the compiler checks its uses), respects namespaces and scopes, shows up in the debugger, and can't be silently redefined elsewhere. A `#define` is blind text replacement that can clash with any identifier of the same name in any header included later.")
