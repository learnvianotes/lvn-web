from kit import *

G = "Getting Started"


@topic(G, "c-intro", "Introduction to C", "letter-c")
def _():
    yield lead("A small, fast, portable systems language — the language of operating systems, embedded devices, databases and the runtimes of most other languages.")
    yield define("C", "a statically typed, compiled, *procedural* language that gives you direct access to memory through pointers and maps closely to what the hardware actually does. It trusts the programmer: there is no garbage collector, no bounds checking and no exceptions.")
    yield section("A short history", "history")
    yield table(
        ["Year", "Milestone"],
        ["1972", "Dennis Ritchie creates C at Bell Labs (successor of B) to rewrite **UNIX**."],
        ["1978", "*The C Programming Language* (K&R) by Kernighan & Ritchie — the de-facto standard, “K&R C”."],
        ["1989 / 1990", "**C89 / C90** — the first ANSI / ISO standard (“ANSI C”). Function prototypes, `void`, `const`."],
        ["1999", "**C99** — `//` comments, `long long`, `<stdint.h>`, `bool`, VLAs, designated initializers, `inline`, mixed declarations."],
        ["2011", "**C11** — `_Generic`, `_Static_assert`, anonymous structs/unions, `<threads.h>`, `<stdatomic.h>`, `_Alignas`; `gets` removed."],
        ["2018", "**C17** (C18) — bug-fix release of C11, no new features. The default standard for these notes."],
        ["2024", "**C23** — `bool`/`true`/`false` as keywords, `nullptr`, `constexpr`, `typeof`, `#embed`, binary literals `0b1010`, `[[attributes]]`."],
    )
    yield section("Why learn C?", "bulb")
    yield cards(
        ("Close to the machine", "You see memory, addresses and bytes. Understanding C explains how every higher-level language works underneath.", "cpu"),
        ("Everywhere", "Linux, Windows and macOS kernels, embedded firmware, SQLite, Redis, Git, CPython, the JVM, Nginx — all C.", "world"),
        ("Fast & small", "No runtime or VM; a C binary is just machine code. Predictable performance and tiny footprint.", "bolt"),
        ("Portable", "A C compiler exists for practically every CPU ever made. The standard library is small and everywhere.", "arrows-exchange"),
    )
    yield section("The trade-off", "scale")
    yield table(
        ["C gives you", "C does NOT give you"],
        ["Raw pointers and manual memory control", "Garbage collection, bounds checks, null safety"],
        ["Structs, unions, functions", "Classes, inheritance, templates, exceptions"],
        ["A tiny standard library", "Built-in strings, lists, maps, networking"],
        ["Speed and control", "Protection from **undefined behaviour** — mistakes compile and silently misbehave"],
    )
    yield section("Hello, world", "code")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            printf("Hello, world!\n");
            return 0;
        }
    ''', out="Hello, world!")
    yield shell('''
        $ gcc hello.c -o hello        # compile (or: clang hello.c -o hello)
        $ ./hello                     # run
        Hello, world!
        $ echo $?                     # exit status returned by main
        0
    ''')
    yield note("C is case-sensitive, every statement ends with `;`, and blocks are delimited by `{ }`. Whitespace and indentation don’t matter to the compiler.", "Syntax basics")
    yield qa("Is C a high-level or low-level language?",
             "It is usually called a *middle-level* language: it has high-level constructs (functions, loops, structs, types) but also low-level access (pointers, bit manipulation, manual memory) that maps almost one-to-one onto machine instructions.")
    yield qa("What is the difference between C and C++?",
             "C++ started as “C with classes” and is (almost) a superset of C. It adds classes, templates, references, RAII, exceptions, namespaces and a large standard library (STL). C stays small and procedural. Some valid C is not valid C++ (e.g. implicit `void *` conversion from `malloc`, designated-initializer order, `int new;`).")


@topic(G, "compilation", "The Compilation Model", "settings-automation")
def _():
    yield lead("Turning `main.c` into an executable is four separate stages: preprocess → compile → assemble → link. Knowing them makes compiler and linker errors easy to read.")
    yield flow("`main.c`", "Preprocessor → `main.i`", "Compiler → `main.s`", "Assembler → `main.o`", "Linker → `a.out`")
    yield section("The four stages", "list-numbers")
    yield steps(
        ("Preprocessing (`cpp`)", "Text substitution: expands `#include` (pastes header files in), `#define` macros, `#if` conditionals, strips comments. Output: one big *translation unit* (`-E`)."),
        ("Compilation (`cc1`)", "Parses the C, type-checks it, optimises it and emits **assembly** for the target CPU (`-S`). Syntax and type errors happen here."),
        ("Assembly (`as`)", "Converts assembly into machine code in an **object file** (`.o`) with a symbol table — unresolved references to functions defined elsewhere are left as holes (`-c`)."),
        ("Linking (`ld`)", "Combines object files and libraries (`libc`, `-lm`…), resolves every symbol to an address, and writes the executable. “undefined reference” errors happen here."),
    )
    yield shell('''
        $ gcc -E main.c -o main.i      # stop after preprocessing
        $ gcc -S main.c -o main.s      # stop after compiling (assembly)
        $ gcc -c main.c -o main.o      # stop after assembling (object file)
        $ gcc main.o util.o -o app     # link object files into an executable
        $ gcc -save-temps main.c       # keep main.i, main.s, main.o all at once
        $ nm main.o                    # list symbols (U = undefined, T = defined text)
    ''')
    yield section("Essential gcc / clang flags", "flag")
    yield table(
        ["Flag", "Meaning"],
        ["`-o name`", "Name of the output file (default `a.out`)."],
        ["`-std=c17`", "Language standard (`c89`, `c99`, `c11`, `c17`, `c2x`/`c23`, or `gnu17` with extensions)."],
        ["`-Wall -Wextra`", "Turn on the important warnings. **Always use them.**"],
        ["`-Werror`", "Treat warnings as errors (good in CI)."],
        ["`-pedantic`", "Warn about non-standard extensions."],
        ["`-g`", "Include debug info (for `gdb` / `lldb`)."],
        ["`-O0 -O1 -O2 -O3 -Os`", "Optimisation level (none → aggressive; `-Os` for size)."],
        ["`-I dir` / `-L dir` / `-lname`", "Add a header search path / library search path / link `libname`."],
        ["`-D NAME=val`", "Define a macro from the command line (like `#define NAME val`)."],
        ["`-fsanitize=address,undefined`", "Runtime checks for memory errors and undefined behaviour (ASan / UBSan)."],
    )
    yield section("Warnings are free bug reports", "alert-triangle")
    yield p("Every sample in these notes is compiled with `-Wall -Wextra -Werror`. This one is rejected at compile time because the format string does not match the argument:")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            double price = 9.99;
            printf("%d\n", price);   /* %d expects int, got double */
            return 0;
        }
    ''', fails=True)
    yield output('''
        main.c:5:20: error: format specifies type 'int' but the argument has type 'double' [-Werror,-Wformat]
            5 |     printf("%d\\n", price);   /* %d expects int, got double */
              |             ~~     ^~~~~
              |             %f
    ''', "Compiler")
    yield section("Compile-time vs link-time errors", "bug")
    yield table(
        ["Error", "Stage", "Typical cause"],
        ["`expected ';'`", "Compile", "Syntax error"],
        ["`implicit declaration of function`", "Compile", "Missing `#include` or prototype"],
        ["`undefined reference to 'foo'`", "Link", "Function declared but never defined / `.o` or `-l` library not linked"],
        ["`multiple definition of 'x'`", "Link", "Global *defined* in a header included by two `.c` files"],
        ["`undefined reference to 'sqrt'`", "Link", "Forgot `-lm` (math library) on some Linux toolchains"],
    )
    yield qa("What is a translation unit?",
             "One `.c` file after preprocessing — the source plus every header it includes, with macros expanded. The compiler works on one translation unit at a time; the linker joins them.")
    yield qa("What is the difference between a compiler error and a linker error?",
             "A compiler error means a single file is not valid C (syntax, types, undeclared names). A linker error means every file compiled fine, but a symbol that was *declared* and used was never *defined* in any object file or library (or was defined twice).")
    yield qa("Static vs dynamic linking?",
             "Static linking copies library code into the executable (`.a` archives) — bigger binary, no runtime dependency. Dynamic linking (`.so` / `.dylib` / `.dll`) records a reference that the loader resolves when the program starts — smaller binaries, shared updates, but the library must be present.")


@topic(G, "program-structure", "Program Structure & main", "file-code")
def _():
    yield lead("A C program is a set of declarations and function definitions; execution starts at `main`, and its return value becomes the process exit status.")
    yield section("Anatomy of a program", "layout-list")
    yield snippet("c", r'''
        /* 1. Preprocessor directives */
        #include <stdio.h>
        #define GREETING "Hi"

        /* 2. Global declarations */
        static int counter = 0;

        /* 3. Function prototype (declaration) */
        int square(int x);

        /* 4. main: the entry point */
        int main(void) {
            counter++;
            printf("%s! square(7) = %d, counter = %d\n", GREETING, square(7), counter);
            return 0;                /* 0 = success */
        }

        /* 5. Function definitions */
        int square(int x) {
            return x * x;
        }
    ''', out="Hi! square(7) = 49, counter = 1")
    yield section("Valid signatures of main", "signature")
    yield table(
        ["Signature", "Use"],
        ["`int main(void)`", "No command-line arguments."],
        ["`int main(int argc, char *argv[])`", "With arguments (`char **argv` is identical)."],
        ["`void main()`", "**Not standard C.** Some compilers accept it; never write it."],
    )
    yield ul(
        "`return 0;` or `return EXIT_SUCCESS;` means success; `EXIT_FAILURE` (from `<stdlib.h>`) means failure.",
        "Reaching the closing `}` of `main` without `return` is treated as `return 0;` (C99+) — but only for `main`.",
        "`int main()` with empty parentheses means *unspecified arguments* in C17; prefer `(void)`.",
    )
    yield section("Comments", "message")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            /* block comment — can span
               several lines, but cannot be nested */
            int x = 5;   // line comment (C99+)
            printf("%d\n", x);
            return 0;
        }
    ''', out="5")
    yield section("Declarations vs definitions", "list-details")
    yield cards(
        ("Declaration", "Introduces a name and its type: `int square(int x);`, `extern int count;`. Can appear many times.", "eye"),
        ("Definition", "Declaration that also allocates storage or provides the body: `int count = 0;`, `int square(int x) { … }`. Exactly **one** per program (the *one-definition rule*).", "hammer"),
    )
    yield warn("Calling a function before any declaration of it is an error since C99 (“implicit declaration”). Put prototypes at the top or in a header.")
    yield qa("What happens before main runs?",
             "The C runtime startup code (`crt0`/`_start`) sets up the stack, initialises `.data` and zeroes `.bss`, sets up `stdin`/`stdout`/`stderr`, builds `argc`/`argv`, then calls `main`. When `main` returns, `exit()` is called with its return value, which flushes buffers and runs `atexit` handlers.")
    yield qa("What does the return value of main mean?",
             "It is the process exit status passed to the operating system (`$?` in a shell). By convention `0` means success and non-zero means an error; only the low 8 bits are visible on POSIX systems.")


@topic(G, "input-output", "Input & Output: printf and scanf", "terminal-2")
def _():
    yield lead("`printf` formats values into text on `stdout`; `scanf` parses text from `stdin` into variables. Both are driven by *format specifiers* that must match the argument types exactly.")
    yield section("Format specifiers", "list")
    yield table(
        ["Specifier", "Type (printf)", "Type (scanf)", "Example output"],
        ["`%d` / `%i`", "`int`", "`int *`", "`-42`"],
        ["`%u`", "`unsigned int`", "`unsigned *`", "`42`"],
        ["`%ld` / `%lld`", "`long` / `long long`", "pointer to same", "`9000000000`"],
        ["`%zu`", "`size_t`", "`size_t *`", "`8`"],
        ["`%f`", "`double` (and `float`, promoted)", "`float *`", "`3.140000`"],
        ["`%lf`", "`double`", "`double *` (**required**)", "`3.140000`"],
        ["`%e` / `%g`", "`double` scientific / shortest", "same as `%f`", "`3.14e+00` / `3.14`"],
        ["`%c`", "`int` (a char)", "`char *`", "`A`"],
        ["`%s`", "`char *` (NUL-terminated)", "`char *` (array)", "`hello`"],
        ["`%x` / `%X` / `%o`", "`unsigned` hex / HEX / octal", "`unsigned *`", "`ff` / `FF` / `377`"],
        ["`%p`", "`void *`", "`void **`", "`0x16d…`"],
        ["`%%`", "a literal `%`", "—", "`%`"],
    )
    yield section("Width, precision and flags", "adjustments")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int n = 42;
            double pi = 3.14159265;
            printf("[%d] [%5d] [%-5d] [%05d] [%+d]\n", n, n, n, n, n);
            printf("[%f] [%.2f] [%8.3f] [%e] [%g]\n", pi, pi, pi, pi, pi);
            printf("[%x] [%X] [%#x] [%o] [%#o]\n", 255, 255, 255, 8, 8);
            printf("[%s] [%10s] [%-10s] [%.3s]\n", "hello", "hi", "hi", "truncate");
            printf("[%*d] [%.*f]\n", 6, n, 1, pi);    /* width / precision from args */
            printf("100%% done, char %c, code %d\n", 'A', 'A');
            return 0;
        }
    ''', out='''
        [42] [   42] [42   ] [00042] [+42]
        [3.141593] [3.14] [   3.142] [3.141593e+00] [3.14159]
        [ff] [FF] [0xff] [10] [010]
        [hello] [        hi] [hi        ] [tru]
        [    42] [3.1]
        100% done, char A, code 65
    ''')
    yield note("Format: `%[flags][width][.precision][length]specifier`. Flags: `-` left-align, `+` show sign, `0` zero-pad, `#` alternate form (`0x`), space = space for positive numbers.")
    yield section("Reading input with scanf", "keyboard")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int age;
            double height;
            char name[20];

            /* scanf needs ADDRESSES: &age, &height — but an array name already is one */
            int got = scanf("%19s %d %lf", name, &age, &height);
            printf("read %d items: %s is %d years, %.2f m\n", got, name, age, height);
            return 0;
        }
    ''', stdin="Asha 21 1.68\n", out="read 3 items: Asha is 21 years, 1.68 m")
    yield p("`scanf` returns the number of items successfully converted (or `EOF`). Always check it — on bad input the variables are left untouched:")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int x = -1;
            if (scanf("%d", &x) != 1) {
                printf("not a number, x still %d\n", x);
            } else {
                printf("x = %d\n", x);
            }
            return 0;
        }
    ''', stdin="abc\n", out="not a number, x still -1")
    yield section("Reading a whole line: fgets", "text-wrap")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char line[64];
            while (fgets(line, sizeof line, stdin) != NULL) {
                line[strcspn(line, "\n")] = '\0';   /* strip the trailing newline */
                printf("got \"%s\" (%zu chars)\n", line, strlen(line));
            }
            return 0;
        }
    ''', stdin="hello world\nsecond line\n", out='''
        got "hello world" (11 chars)
        got "second line" (11 chars)
    ''')
    yield section("Character I/O", "abc")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <ctype.h>

        int main(void) {
            int c;                         /* int, not char: must hold EOF (-1) too */
            while ((c = getchar()) != EOF) {
                putchar(toupper(c));
            }
            return 0;
        }
    ''', stdin="shout this\n", out="SHOUT THIS")
    yield section("Pitfalls", "alert-triangle")
    yield table(
        ["Mistake", "Consequence", "Fix"],
        ["`scanf(\"%d\", x)` — missing `&`", "Writes to a garbage address → crash", "`scanf(\"%d\", &x)`"],
        ["`scanf(\"%s\", buf)` with no width", "Buffer overflow on long input", "`scanf(\"%19s\", buf)` for `char buf[20]`"],
        ["`%f` to read a `double`", "Writes only 4 bytes → wrong value", "Use `%lf` in `scanf`"],
        ["`gets(buf)`", "Unbounded — removed in C11", "`fgets(buf, sizeof buf, stdin)`"],
        ["`scanf(\"%d\")` then `fgets`", "`fgets` reads the leftover `\\n` → empty line", "Consume the rest of the line first"],
        ["`printf(user_input)`", "Format-string vulnerability", "`printf(\"%s\", user_input)`"],
    )
    yield warn("`stdout` is *line-buffered* on a terminal but *fully buffered* when redirected to a file or pipe. Output may appear later than you expect — use `fflush(stdout)` or print to `stderr` (unbuffered) for diagnostics.")
    yield qa("Why is getchar's result stored in an int?",
             "`getchar` returns every possible `unsigned char` value (0–255) *plus* `EOF` (a negative value, usually −1). A `char` cannot represent all 257 values, so `EOF` would be confused with a real character (or never detected if `char` is unsigned).")
    yield qa("Why does printf use %f for both float and double, but scanf needs %lf for double?",
             "Arguments to variadic functions undergo *default argument promotions*: a `float` passed to `printf` is converted to `double`, so `%f` always receives a `double`. `scanf` receives *pointers*, which are not promoted — it must know whether to write 4 bytes (`float *`, `%f`) or 8 bytes (`double *`, `%lf`).")
