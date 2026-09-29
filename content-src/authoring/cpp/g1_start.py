from kit import *

G = "Getting Started"


@topic(G, "intro-cpp", "Introduction to C++", "brand-cpp")
def _():
    yield lead("A compiled, statically typed, multi-paradigm language that gives you C-level control of memory with high-level abstractions that cost nothing at run time.")
    yield define("C++", "a general-purpose language created by Bjarne Stroustrup (1979, “C with Classes”). Source is compiled *ahead of time* to native machine code — no virtual machine, no garbage collector.")
    yield section("Why C++?", "bulb")
    yield cards(
        ("Performance", "Compiles to native code; you decide where every object lives (stack, heap, static). Used where latency matters: games, trading, browsers, databases.", "rocket"),
        ("Zero-overhead abstractions", "“What you don't use, you don't pay for; what you do use, you couldn't hand-code better.” Templates and inlining make `std::sort` as fast as hand-written C.", "adjustments"),
        ("Multi-paradigm", "Procedural (like C), object-oriented (classes, virtual functions), generic (templates) and functional (lambdas, ranges) — mix as needed.", "puzzle"),
        ("Deterministic cleanup", "Destructors run at a known point (end of scope) — the basis of **RAII**, C++'s answer to resource management.", "recycle"),
    )
    yield section("C vs C++", "git-compare")
    yield table(
        ["Feature", "C", "C++"],
        ["Paradigm", "Procedural", "Procedural + OOP + generic + functional"],
        ["Structs", "Data only", "`class`/`struct` with methods, access control, inheritance"],
        ["Memory", "`malloc` / `free`", "`new` / `delete`, but prefer containers & smart pointers"],
        ["Strings", "`char*` + `<string.h>`", "`std::string`, `std::string_view`"],
        ["Pass by", "Value or pointer", "Value, pointer **or reference** (`int&`)"],
        ["Overloading", "No", "Function & operator overloading"],
        ["Generic code", "Macros / `void*`", "Templates, concepts"],
        ["Errors", "Return codes, `errno`", "Exceptions (plus return codes, `std::optional`)"],
        ["Namespaces", "No (one global scope)", "`namespace`"],
        ["Standard library", "Small (`stdio`, `stdlib`…)", "STL: containers, algorithms, threads, chrono, …"],
    )
    yield note("C++ is *almost* a superset of C — most C compiles as C++, but not all (e.g. `int *p = malloc(4);` needs a cast in C++, and `class`/`new` are keywords).", "Compatibility")
    yield section("Your first program", "code")
    yield snippet("cpp", r'''
        #include <iostream>

        int main() {
            std::cout << "Hello, C++!\n";
            int year = 2020;
            std::cout << "Standard: C++" << year % 100 << '\n';
            return 0;   // optional in main: falling off the end returns 0
        }
    ''', out='''
        Hello, C++!
        Standard: C++20
    ''')
    yield section("The standards", "calendar")
    yield table(
        ["Standard", "Headline features"],
        ["**C++98/03**", "STL, templates, exceptions, `std::string`"],
        ["**C++11**", "The “modern C++” reset: `auto`, lambdas, move semantics, `nullptr`, smart pointers, range-`for`, `constexpr`, threads"],
        ["**C++14**", "Generic lambdas, `make_unique`, relaxed `constexpr`"],
        ["**C++17**", "Structured bindings, `optional`/`variant`/`any`, `string_view`, `if constexpr`, filesystem"],
        ["**C++20**", "Concepts, ranges, coroutines, modules, `<=>`, `std::format`, `std::span`"],
        ["**C++23**", "`std::print`, `std::expected`, `ranges::to`, deducing `this`"],
    )
    yield note("These notes use **C++20** (every example is compiled with `clang++ -std=c++20`). C++23 features are mentioned where relevant.", "Version")
    yield qa("Is C++ an object-oriented language?",
             "It *supports* OOP but doesn't force it. It's multi-paradigm: you can write procedural code, generic code with templates, or functional-style code with lambdas and ranges. A C++ program doesn't need a single class.")
    yield qa("Why is C++ faster than Java or Python?",
             "It compiles straight to native code with aggressive optimisation (inlining, templates specialised per type), has no garbage-collector pauses and no interpreter/JIT warm-up, and lets you control memory layout (contiguous `std::vector`, objects on the stack). The trade-off is that memory safety is your responsibility.")


@topic(G, "compilation-toolchain", "Compilation & Toolchain", "tool")
def _():
    yield lead("Turning `.cpp` files into an executable takes four stages — knowing them explains most “undefined reference” and “multiple definition” errors.")
    yield section("The build pipeline", "arrows-right")
    yield flow("`main.cpp`", "Preprocessor", "Compiler", "Assembler", "Linker", "`./app`")
    yield steps(
        ("Preprocess", "Handles `#include` (pastes the header text in), `#define` macros and `#if` conditionals. Output: one big *translation unit*."),
        ("Compile", "Parses and type-checks the translation unit, instantiates templates, optimises, and emits assembly."),
        ("Assemble", "Turns assembly into an **object file** (`main.o`) — machine code with unresolved symbol references."),
        ("Link", "Combines object files and libraries, resolving every symbol to exactly one definition. Output: the executable."),
    )
    yield shell('''
        $ clang++ -std=c++20 -Wall -Wextra -O2 main.cpp -o app   # all four stages in one go
        $ ./app

        $ clang++ -E main.cpp -o main.ii       # stop after preprocessing
        $ clang++ -S main.cpp -o main.s        # stop after compiling (assembly)
        $ clang++ -c main.cpp -o main.o        # stop after assembling (object file)
        $ clang++ main.o util.o -o app         # link object files
    ''')
    yield section("Useful compiler flags", "flag")
    yield table(
        ["Flag", "Meaning"],
        ["`-std=c++20`", "Pick the language standard (`c++17`, `c++23`, …)"],
        ["`-Wall -Wextra -Wpedantic`", "Turn on warnings — always use them"],
        ["`-Werror`", "Treat warnings as errors"],
        ["`-O0` / `-O2` / `-O3`", "Optimisation level (debug → release)"],
        ["`-g`", "Include debug info (for `gdb`/`lldb`)"],
        ["`-fsanitize=address,undefined`", "Catch memory errors and UB at run time (ASan/UBSan)"],
        ["`-I dir` / `-L dir` / `-lname`", "Header search path / library path / link a library"],
        ["`-D NAME=val`", "Define a macro (like `#define`)"],
    )
    yield section("Headers vs source files", "files")
    yield p("A **declaration** says a name exists; a **definition** creates it. Headers hold declarations so every `.cpp` can use them; exactly one `.cpp` holds each definition.")
    yield snippet("cpp", r'''
        // math_utils.h — the interface
        #pragma once              // include guard: paste this header at most once per TU

        int square(int x);        // declaration only
        inline int cube(int x) {  // `inline` lets a definition live in a header
            return x * x * x;
        }
    ''', caption="C++ — header", flags=("-Wno-pragma-once-outside-header",))
    yield snippet("cpp", r'''
        #include <iostream>
        // In a real project: #include "math_utils.h" and square() lives in math_utils.cpp.
        int square(int x);                    // what the header provides
        int main() { std::cout << square(7) << '\n'; }
        int square(int x) { return x * x; }   // what math_utils.cpp provides
    ''', out="49")
    yield cards(
        ("Undefined reference", "*Linker* error: something was declared and used but never defined (or the `.cpp` defining it wasn't linked).", "link-off"),
        ("Multiple definition", "*Linker* error: two translation units both define the same non-`inline` function/variable — e.g. a function body in a header included twice.", "copy"),
    )
    yield define("One Definition Rule (ODR)", "every function or variable may be *declared* many times but *defined* exactly once in the program — except `inline` functions/variables, templates and classes, which may be defined in every TU as long as all definitions are identical.")
    yield section("Include guards", "shield")
    yield snippet("cpp", r'''
        #ifndef POINT_H           // classic guard — works everywhere
        #define POINT_H
        struct Point { int x, y; };
        #endif
    ''', caption="C++ — classic guard")
    yield section("Build systems", "building-factory")
    yield p("Real projects don't type compiler commands — **CMake** generates the build (Make/Ninja/Xcode) from a `CMakeLists.txt`:")
    yield shell('''
        # CMakeLists.txt
        cmake_minimum_required(VERSION 3.20)
        project(app CXX)
        set(CMAKE_CXX_STANDARD 20)
        add_executable(app main.cpp math_utils.cpp)

        $ cmake -S . -B build && cmake --build build
    ''')
    yield qa("What's the difference between a compile error and a linker error?",
             "A compile error is found while checking a single translation unit (syntax, types, undeclared names). A linker error happens after every file compiled fine, when symbols are stitched together: a missing definition (*undefined reference*) or two definitions (*multiple definition*).")
    yield qa("Why do templates usually live entirely in headers?",
             "The compiler generates code for a template only when it sees it used with concrete types, and it needs the full definition at that point. If the definition were in a `.cpp`, other translation units couldn't instantiate it and you'd get undefined-reference errors.")


@topic(G, "program-structure-io", "Program Structure & I/O Streams", "terminal-2")
def _():
    yield lead("`main` is the entry point; `std::cin` and `std::cout` read and write through type-safe *streams* with `>>` and `<<`.")
    yield section("Anatomy of a program", "list-details")
    yield snippet("cpp", r'''
        #include <iostream>     // std::cin, std::cout, std::cerr
        #include <string>       // std::string

        int main() {
            std::string name;
            int age;
            std::cin >> name >> age;             // whitespace-separated tokens
            std::cout << "Hi " << name << ", next year you'll be " << age + 1 << ".\n";
        }
    ''', stdin="Asha 24\n", out="Hi Asha, next year you'll be 25.")
    yield table(
        ["Stream", "Purpose", "Buffered?"],
        ["`std::cout`", "Standard output", "Yes"],
        ["`std::cin`", "Standard input", "Yes"],
        ["`std::cerr`", "Error output (unbuffered — shows up immediately)", "No"],
        ["`std::clog`", "Log output to stderr", "Yes"],
    )
    yield section("`main` signatures", "door-enter")
    yield snippet("cpp", r'''
        #include <iostream>
        int main(int argc, char* argv[]) {       // argc = number of args, argv[0] = program name
            std::cout << "args: " << argc - 1 << '\n';
            for (int i = 1; i < argc; ++i) std::cout << i << ": " << argv[i] << '\n';
            return 0;                            // 0 = success; non-zero = failure
        }
    ''', args=("build", "--fast"), out='''
        args: 2
        1: build
        2: --fast
    ''')
    yield section("Reading lines with `getline`", "text-wrap")
    yield p("`>>` stops at whitespace. To read a whole line use `std::getline`. After a `>>`, the newline is still in the buffer — skip it with `std::ws` (or `cin.ignore()`) first.")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        int main() {
            int id;
            std::string fullName;
            std::cin >> id;
            std::getline(std::cin >> std::ws, fullName);   // std::ws eats the leftover '\n'
            std::cout << id << " -> [" << fullName << "]\n";
        }
    ''', stdin="7\nAda Lovelace\n", out="7 -> [Ada Lovelace]")
    yield warn("Without `std::ws`, `getline` right after `cin >> id` reads the *empty rest of the line* and `fullName` ends up `\"\"`. This is the #1 beginner I/O bug.")
    yield section("Reading until end of input", "repeat")
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            long long sum = 0;
            int x;
            while (std::cin >> x) sum += x;   // the stream converts to false at EOF or bad input
            std::cout << "sum = " << sum << '\n';
        }
    ''', stdin="3 4 5\n10\n", out="sum = 22")
    yield section("`\\n` vs `std::endl`", "corner-down-left")
    yield cards(
        ("`'\\n'`", "Just a newline character. Output stays buffered — fast.", "bolt"),
        ("`std::endl`", "Newline **plus a flush** of the buffer. Flushing on every line can make output-heavy programs many times slower.", "hourglass"),
    )
    yield note("Use `'\\n'` by default; flush explicitly (`std::flush` or `std::endl`) only when output must appear *now* (e.g. before a long computation or a crash).")
    yield section("`using namespace std;`", "world")
    yield p("Everything in the standard library lives in namespace `std`. Writing `using namespace std;` saves typing in small programs and contest code, but in headers or large code bases it pulls hundreds of names into scope and causes clashes (`std::count`, `std::distance`, `std::size`…).")
    yield dodont("Qualify names (`std::cout`) or import just what you need: `using std::cout;`", "`using namespace std;` in a header file — it leaks into every file that includes it")
    yield qa("What does std::cin >> x return, and why can it be used in a while condition?",
             "It returns the stream itself (`std::istream&`), which allows chaining (`cin >> a >> b`). A stream is contextually convertible to `bool`: it's `false` once a read failed (EOF or input that can't be parsed as the target type), so `while (cin >> x)` reads until input runs out.")


@topic(G, "formatting-output", "Formatting Output", "typography")
def _():
    yield lead("Two tools: stream *manipulators* from `<iomanip>` (classic, sticky state) and C++20's `std::format` (Python-style format strings, type-safe).")
    yield section("`std::format` (C++20)", "braces")
    yield snippet("cpp", r'''
        #include <format>
        #include <iostream>
        #include <numbers>

        int main() {
            std::cout << std::format("{} + {} = {}\n", 2, 3, 2 + 3);
            std::cout << std::format("[{:>6}] [{:<6}] [{:^6}]\n", "r", "l", "c");  // align in width 6
            std::cout << std::format("{:.3f} {:e}\n", std::numbers::pi, 12345.678);
            std::cout << std::format("{:05d} {:+d} {:#x} {:#b}\n", 42, 7, 255, 5);
            std::cout << std::format("{1} {0} {1}\n", "a", "b");                  // positional
            std::cout << std::format("{:*^11}\n", " hi ");                          // custom fill
        }
    ''', out='''
        2 + 3 = 5
        [     r] [l     ] [  c   ]
        3.142 1.234568e+04
        00042 +7 0xff 0b101
        b a b
        *** hi ****
    ''')
    yield table(
        ["Spec", "Meaning", "Example → result"],
        ["`{:>8}` `{:<8}` `{:^8}`", "Right / left / centre in width 8", "`{:>4}`, `7` → `   7`"],
        ["`{:*^8}`", "Centre with fill character `*`", "`{:*^5}`, `\"a\"` → `**a**`"],
        ["`{:.2f}`", "Fixed, 2 decimals", "`3.14159` → `3.14`"],
        ["`{:e}` / `{:g}`", "Scientific / shortest", "`1500.0` → `1.500000e+03` / `1500`"],
        ["`{:05d}`", "Zero-pad to width 5", "`42` → `00042`"],
        ["`{:x}` `{:#x}` `{:b}` `{:o}`", "Hex, hex with `0x`, binary, octal", "`255` → `ff`, `0xff`"],
        ["`{:+}`", "Always show sign", "`7` → `+7`"],
    )
    yield note("C++23 adds `std::print(\"{}\\n\", x)` / `std::println`, which format *and* write in one call. Until then, `std::cout << std::format(...)`.", "C++23")
    yield section("Stream manipulators (`<iomanip>`)", "adjustments-horizontal")
    yield snippet("cpp", r'''
        #include <iomanip>
        #include <iostream>

        int main() {
            double price = 3.14159;
            std::cout << std::fixed << std::setprecision(2) << price << '\n';
            std::cout << price * 2 << '\n';                 // precision is *sticky*
            std::cout << std::setw(6) << 42 << '|' << 42 << '|' << '\n';   // setw applies to next item only
            std::cout << std::setfill('0') << std::setw(4) << 7 << '\n';
            std::cout << std::left << std::setfill('.') << std::setw(8) << "name" << "Ada\n";
            std::cout << std::hex << 255 << ' ' << std::dec << 255 << '\n';
            std::cout << std::boolalpha << true << ' ' << std::noboolalpha << true << '\n';
        }
    ''', out='''
        3.14
        6.28
            42|42|
        0007
        name....Ada
        ff 255
        true 1
    ''')
    yield table(
        ["Manipulator", "Effect", "Sticky?"],
        ["`std::setw(n)`", "Minimum width of the next field", "No — next output only"],
        ["`std::setprecision(n)`", "Significant digits (or decimals with `fixed`)", "Yes"],
        ["`std::fixed` / `std::scientific`", "Floating-point notation", "Yes"],
        ["`std::setfill(c)`", "Padding character", "Yes"],
        ["`std::left` / `std::right`", "Alignment inside the width", "Yes"],
        ["`std::hex` / `std::oct` / `std::dec`", "Integer base", "Yes"],
        ["`std::boolalpha`", "Print `true`/`false` instead of `1`/`0`", "Yes"],
    )
    yield warn("Manipulators (except `setw`) change the stream's state *permanently*. A `std::hex` left on `std::cout` makes every later integer print in hex — reset with `std::dec`.")
    yield dodont("Prefer `std::format` in new code — the format is visible in one string and nothing leaks into later output.", "Mixing `printf` and `std::cout` on the same output without care — their buffers are synchronised only while `sync_with_stdio(true)` (the default).")
    yield qa("What does std::setprecision(3) do without std::fixed?",
             "It sets the number of *significant digits*: `std::cout << std::setprecision(3) << 3.14159` prints `3.14`, and `1234.5` prints `1.23e+03`. With `std::fixed` it means digits *after the decimal point*.")
