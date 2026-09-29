from kit import *

G = "Files, Preprocessor & Program Organisation"


@topic(G, "file-io", "File I/O", "file-text")
def _():
    yield lead("`<stdio.h>` works with *streams* (`FILE *`): open with `fopen`, read/write with the same family of functions you use for the console, and always `fclose`.")
    yield section("Open modes", "lock-open")
    yield table(
        ["Mode", "Meaning", "If file exists", "If missing"],
        ["`\"r\"`", "Read", "Read from start", "Fails (`NULL`)"],
        ["`\"w\"`", "Write", "**Truncated to 0**", "Created"],
        ["`\"a\"`", "Append", "Writes go to the end", "Created"],
        ["`\"r+\"`", "Read + write", "Kept", "Fails"],
        ["`\"w+\"`", "Read + write", "Truncated", "Created"],
        ["`\"a+\"`", "Read + append", "Kept, writes at end", "Created"],
        ["`\"…b\"`", "Binary (`\"rb\"`, `\"wb\"`)", "No newline translation (matters on Windows)", ""],
        ["`\"wx\"` (C11)", "Exclusive create", "Fails", "Created"],
    )
    yield section("Writing and reading text", "pencil")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            FILE *f = fopen("scores.txt", "w");
            if (f == NULL) { perror("fopen"); return 1; }
            fprintf(f, "asha 91\nravi 78\nmeera 85\n");
            fclose(f);

            f = fopen("scores.txt", "r");
            if (!f) { perror("fopen"); return 1; }
            char name[32];
            int score, total = 0, count = 0;
            while (fscanf(f, "%31s %d", name, &score) == 2) {   /* loop on the read, not on feof */
                printf("%-6s %d\n", name, score);
                total += score;
                count++;
            }
            fclose(f);
            printf("average %.1f\n", (double)total / count);
            return 0;
        }
    ''', out='''
        asha   91
        ravi   78
        meera  85
        average 84.7
    ''')
    yield section("Line by line with fgets, appending", "text-wrap")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            FILE *f = fopen("log.txt", "w");
            if (!f) return 1;
            fputs("first\n", f);
            fclose(f);

            f = fopen("log.txt", "a");             /* keep existing content */
            if (!f) return 1;
            fputs("second\n", f);
            fputs("third\n", f);
            fclose(f);

            f = fopen("log.txt", "r");
            if (!f) return 1;
            char line[128];
            int n = 0;
            while (fgets(line, sizeof line, f)) {
                line[strcspn(line, "\n")] = '\0';
                printf("%d: %s\n", ++n, line);
            }
            fclose(f);
            return 0;
        }
    ''', out='''
        1: first
        2: second
        3: third
    ''')
    yield section("Binary files: fwrite / fread / fseek", "binary")
    yield snippet("c", r'''
        #include <stdio.h>

        typedef struct { int id; double price; } Item;

        int main(void) {
            Item items[3] = {{1, 9.5}, {2, 20.0}, {3, 4.25}};
            FILE *f = fopen("items.bin", "wb");
            if (!f) return 1;
            size_t written = fwrite(items, sizeof items[0], 3, f);
            fclose(f);

            f = fopen("items.bin", "rb");
            if (!f) return 1;
            fseek(f, 0, SEEK_END);
            long size = ftell(f);                          /* file size in bytes */
            printf("wrote %zu records, file is %ld bytes\n", written, size);

            Item it;
            fseek(f, 2 * (long)sizeof(Item), SEEK_SET);   /* random access: jump to record #2 */
            if (fread(&it, sizeof it, 1, f) == 1) printf("record 2: id=%d price=%.2f\n", it.id, it.price);
            rewind(f);
            if (fread(&it, sizeof it, 1, f) == 1) printf("record 0: id=%d\n", it.id);
            fclose(f);
            remove("items.bin");
            return 0;
        }
    ''', out='''
        wrote 3 records, file is 48 bytes
        record 2: id=3 price=4.25
        record 0: id=1
    ''')
    yield warn("Raw `fwrite` of structs is not portable between machines: padding, endianness and type sizes differ. For interchange formats write fields explicitly in a fixed byte order.")
    yield section("Character-level copy", "copy")
    yield snippet("c", r'''
        #include <stdio.h>

        int copy_file(const char *src, const char *dst) {
            FILE *in = fopen(src, "rb");
            if (!in) return -1;
            FILE *out = fopen(dst, "wb");
            if (!out) { fclose(in); return -1; }
            int c;
            long bytes = 0;
            while ((c = fgetc(in)) != EOF) { fputc(c, out); bytes++; }
            int err = ferror(in) || ferror(out);
            fclose(in);
            fclose(out);
            return err ? -1 : (int)bytes;
        }

        int main(void) {
            FILE *f = fopen("a.txt", "w");
            if (!f) return 1;
            fputs("copy me\n", f);
            fclose(f);
            printf("copied %d bytes\n", copy_file("a.txt", "b.txt"));
            printf("missing source -> %d\n", copy_file("nope.txt", "c.txt"));
            return 0;
        }
    ''', out='''
        copied 8 bytes
        missing source -> -1
    ''')
    yield table(
        ["Function", "Purpose"],
        ["`fgetc` / `fputc`", "One character"],
        ["`fgets` / `fputs`", "One line / string"],
        ["`fscanf` / `fprintf`", "Formatted text"],
        ["`fread` / `fwrite`", "Blocks of bytes (binary)"],
        ["`fseek` / `ftell` / `rewind`", "Move / query the file position"],
        ["`feof` / `ferror` / `clearerr`", "Why did the last read stop?"],
        ["`fflush`", "Push buffered output to the OS"],
        ["`remove` / `rename` / `tmpfile`", "File-system helpers"],
    )
    yield warn("`while (!feof(f)) { fgets(…); … }` processes the last line twice: `feof` only becomes true *after* a read has failed. Loop on the return value of the read function instead.")
    yield qa("What is the difference between text and binary mode?",
             "On POSIX there is none. On Windows, text mode translates `\\n` to `\\r\\n` on write (and back on read) and may treat Ctrl-Z as end-of-file; binary mode passes bytes through unchanged. Always use `\"rb\"`/`\"wb\"` for non-text data.")
    yield qa("Why must you call fclose?",
             "It flushes buffered data to the file (without it, the last writes may be lost if the program crashes or calls `_exit`), releases the file descriptor (processes have a limited number) and frees the `FILE` structure. `exit` and returning from `main` close open streams, but relying on that hides bugs.")


@topic(G, "command-line-args", "Command-Line Arguments", "terminal")
def _():
    yield lead("`main(int argc, char *argv[])` receives the words typed after the program name: `argc` counts them, `argv` holds them as strings, and `argv[argc]` is always `NULL`.")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(int argc, char *argv[]) {
            printf("argc = %d\n", argc);
            for (int i = 0; i < argc; i++)
                printf("argv[%d] = \"%s\"\n", i, argv[i]);
            printf("argv[argc] is %s\n", argv[argc] == NULL ? "NULL" : "not NULL");
            return 0;
        }
    ''', args=("input.txt", "--verbose", "42"), out='''
        argc = 4
        argv[0] = "./prog"
        argv[1] = "input.txt"
        argv[2] = "--verbose"
        argv[3] = "42"
        argv[argc] is NULL
    ''', caption="C — run as: ./prog input.txt --verbose 42")
    yield section("Converting and validating", "checks")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <errno.h>

        int parse_int(const char *s, long *out) {
            char *end;
            errno = 0;
            long v = strtol(s, &end, 10);
            if (end == s || *end != '\0' || errno == ERANGE) return -1;
            *out = v;
            return 0;
        }

        int main(int argc, char *argv[]) {
            if (argc < 2) {
                fprintf(stderr, "usage: %s NUM...\n", argv[0]);
                return EXIT_FAILURE;
            }
            long sum = 0;
            for (int i = 1; i < argc; i++) {
                long v;
                if (parse_int(argv[i], &v) != 0) { printf("skipping '%s'\n", argv[i]); continue; }
                sum += v;
            }
            printf("sum = %ld\n", sum);
            return EXIT_SUCCESS;
        }
    ''', args=("10", "20", "x7", "-5"), out='''
        skipping 'x7'
        sum = 25
    ''', caption="C — run as: ./prog 10 20 x7 -5")
    yield section("Parsing options", "adjustments-horizontal")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        int main(int argc, char **argv) {
            int verbose = 0, count = 1;
            const char *name = "world";
            for (int i = 1; i < argc; i++) {
                if (strcmp(argv[i], "-v") == 0) verbose = 1;
                else if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) count = atoi(argv[++i]);
                else name = argv[i];
            }
            for (int i = 0; i < count; i++) printf("hello, %s\n", name);
            if (verbose) printf("(printed %d times)\n", count);
            return 0;
        }
    ''', args=("-n", "2", "-v", "C"), out='''
        hello, C
        hello, C
        (printed 2 times)
    ''', caption="C — run as: ./prog -n 2 -v C")
    yield note("On POSIX systems, `getopt()` (`<unistd.h>`) and GNU `getopt_long()` handle combined flags (`-vn 2`), `--` and error messages for you.")
    yield ul(
        "`argv[0]` is the program name *as invoked* — it may be a path, or anything the parent process chose.",
        "The shell does quoting and globbing: `./prog \"a b\" *.c` passes `a b` as one argument and expands `*.c` before your program starts.",
        "The strings in `argv` are modifiable and live until the program ends.",
        "Environment variables: `getenv(\"HOME\")` from `<stdlib.h>`.",
    )
    yield qa("What is argv[argc]?",
             "Always a null pointer — the standard guarantees it. You can loop with `for (char **p = argv; *p; p++)` instead of counting.")
    yield qa("Why is argv declared as char *argv[] and char **argv interchangeably?",
             "Because an array parameter is adjusted to a pointer: `char *argv[]` in a parameter list *is* `char **argv`. It points to the first element of an array of `char *`, each pointing to a NUL-terminated argument string.")


@topic(G, "preprocessor", "Preprocessor & Macros", "hash")
def _():
    yield lead("Before compilation, the preprocessor rewrites the source text: it pastes in headers, expands macros and keeps or drops code with conditionals. It knows nothing about C types or scope.")
    yield table(
        ["Directive", "Purpose"],
        ["`#include <x.h>` / `\"x.h\"`", "Paste a file (angle brackets: system paths; quotes: current dir first)"],
        ["`#define NAME value`", "Object-like macro"],
        ["`#define F(a, b) (…)`", "Function-like macro"],
        ["`#undef NAME`", "Remove a definition"],
        ["`#if` / `#elif` / `#else` / `#endif`", "Conditional compilation on constant expressions"],
        ["`#ifdef` / `#ifndef` / `defined(X)`", "Is a macro defined?"],
        ["`#error \"msg\"`", "Stop compilation with a message"],
        ["`#pragma`", "Implementation-specific (`#pragma once`, `#pragma pack`)"],
        ["`#line`", "Change reported line numbers (used by code generators)"],
    )
    yield section("Macros and their pitfalls", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>

        #define SQUARE_BAD(x) x * x
        #define SQUARE(x) ((x) * (x))            /* parenthesise every argument AND the whole body */
        #define MAX(a, b) ((a) > (b) ? (a) : (b))

        int main(void) {
            printf("%d\n", SQUARE_BAD(2 + 3));   /* 2 + 3 * 2 + 3 = 11 */
            printf("%d\n", SQUARE(2 + 3));       /* 25 */
            printf("%d\n", 100 / SQUARE(5));     /* 4 — without outer parens: 100 / 5 * 5 = 100 */

            int i = 5, j = 3;
            int m = MAX(i++, j);                 /* i++ is evaluated TWICE */
            printf("m = %d, i = %d\n", m, i);
            return 0;
        }
    ''', out='''
        11
        25
        4
        m = 6, i = 7
    ''')
    yield warn("Function-like macros evaluate arguments as many times as they appear. Never pass expressions with side effects (`i++`, function calls). Prefer `static inline` functions — they are type-checked and evaluate arguments once.")
    yield section("Multi-statement macros: do { } while (0)", "brackets")
    yield snippet("c", r'''
        #include <stdio.h>

        #define SWAP(a, b) do { int tmp_ = (a); (a) = (b); (b) = tmp_; } while (0)

        int main(void) {
            int x = 1, y = 2;
            if (x < y)
                SWAP(x, y);        /* expands to ONE statement, so the else still pairs correctly */
            else
                printf("no swap\n");
            printf("%d %d\n", x, y);
            return 0;
        }
    ''', out="2 1")
    yield section("Stringising #, token pasting ##, predefined macros", "text-plus")
    yield snippet("c", r'''
        #include <stdio.h>

        #define STR(x) #x
        #define XSTR(x) STR(x)                    /* expand first, then stringise */
        #define VERSION 3
        #define DEBUG_PRINT(var) printf(#var " = %d\n", var)
        #define MAKE_GETTER(field) int get_##field(void) { return field; }

        int width = 80;
        MAKE_GETTER(width)                        /* defines int get_width(void) */

        int main(void) {
            int count = 42;
            DEBUG_PRINT(count);
            printf("%s %s\n", STR(VERSION), XSTR(VERSION));
            printf("%d\n", get_width());
            printf("line %d of %s, C standard %ld\n", __LINE__, __func__, __STDC_VERSION__);
            return 0;
        }
    ''', out='''
        count = 42
        VERSION 3
        80
        line 17 of main, C standard 201710
    ''')
    yield table(
        ["Macro", "Value"],
        ["`__FILE__`, `__LINE__`", "Current file name and line"],
        ["`__func__`", "Current function name (a predefined identifier, not a macro)"],
        ["`__DATE__`, `__TIME__`", "Compilation date and time"],
        ["`__STDC_VERSION__`", "`199901L` (C99), `201112L` (C11), `201710L` (C17), `202311L` (C23)"],
        ["`__GNUC__`, `__clang__`, `_WIN32`, `__linux__`, `__APPLE__`", "Compiler / platform detection"],
    )
    yield section("Conditional compilation", "git-branch")
    yield snippet("c", r'''
        #include <stdio.h>

        #define LOG_LEVEL 2

        #ifndef BUFFER_SIZE
        #define BUFFER_SIZE 256                   /* default unless -DBUFFER_SIZE=... is passed */
        #endif

        #if LOG_LEVEL >= 2
        #define LOG(msg) printf("[debug] %s\n", msg)
        #else
        #define LOG(msg) ((void)0)
        #endif

        int main(void) {
            LOG("starting");
        #if defined(__APPLE__)
            printf("macOS build, buffer %d\n", BUFFER_SIZE);
        #elif defined(__linux__)
            printf("Linux build, buffer %d\n", BUFFER_SIZE);
        #else
            printf("other build, buffer %d\n", BUFFER_SIZE);
        #endif
            return 0;
        }
    ''', out='''
        [debug] starting
        macOS build, buffer 1024
    ''', flags=("-DBUFFER_SIZE=1024",), caption="C — compiled on macOS with -DBUFFER_SIZE=1024")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <assert.h>

        int main(void) {
            int balance = 10;
            assert(balance >= 0);           /* active unless NDEBUG is defined */
            balance -= 25;
            assert(balance >= 0 && "balance went negative");
            printf("unreachable\n");
            return 0;
        }
    ''', fails=True, caption="C — assert aborts the program when the condition is false")
    yield output("Assertion failed: (balance >= 0 && \"balance went negative\"), function main, file main.c, line 8.", "stderr")
    yield qa("What is the difference between a macro and an inline function?",
             "A macro is textual substitution before compilation: no type checking, arguments may be evaluated several times, no scope, hard to debug. An `inline` function is a real function the compiler may expand in place: arguments are evaluated once and type-checked, and it follows normal scope rules. Macros are still needed for stringising, token pasting, conditional compilation and type-generic tricks.")
    yield qa("Why wrap a multi-statement macro in do { ... } while (0)?",
             "It turns the macro into a single statement that requires a trailing semicolon, so it works correctly as the body of an unbraced `if`/`else`. A bare `{ … }` block followed by `;` would break an `if … else`.")
    yield qa("What does #include <file> vs #include \"file\" do?",
             "Both paste the file’s contents. `\"file\"` searches the directory of the current file first, then the system paths; `<file>` searches only the system/`-I` paths. Use quotes for your own headers.")


@topic(G, "multi-file-programs", "Header Files & Multi-File Programs", "files")
def _():
    yield lead("Real programs split into modules: a **header** (`.h`) declares the interface, a **source** file (`.c`) implements it, and the linker joins the compiled objects.")
    yield section("A module: header + implementation", "file-code")
    yield snippet("c", r'''
        /* ---------- mathx.h ---------- */
        #ifndef MATHX_H              /* include guard: safe to include twice */
        #define MATHX_H

        #include <stddef.h>

        #define MATHX_PI 3.14159265358979

        extern int mathx_calls;                           /* declaration only */

        int    mathx_gcd(int a, int b);                   /* prototypes */
        double mathx_mean(const double *v, size_t n);

        static inline int mathx_sq(int x) { return x * x; }   /* small helpers may live in the header */

        #endif /* MATHX_H */
    ''', flags=("-Wno-unused-function",), caption="C — mathx.h (compile-checked)")
    yield snippet("c", r'''
        /* ---------- mathx.c ---------- */
        #include <stddef.h>
        /* #include "mathx.h"  — always include your own header to check the prototypes match */
        extern int mathx_calls;
        int mathx_gcd(int a, int b);
        double mathx_mean(const double *v, size_t n);

        int mathx_calls = 0;                              /* the one definition */

        static int abs_int(int x) { return x < 0 ? -x : x; }   /* private helper */

        int mathx_gcd(int a, int b) {
            mathx_calls++;
            a = abs_int(a); b = abs_int(b);
            while (b) { int t = a % b; a = b; b = t; }
            return a;
        }

        double mathx_mean(const double *v, size_t n) {
            mathx_calls++;
            double s = 0;
            for (size_t i = 0; i < n; i++) s += v[i];
            return n ? s / n : 0.0;
        }
    ''', caption="C — mathx.c (compile-checked)")
    yield snippet("c", r'''
        /* ---------- main.c ---------- */
        #include <stdio.h>
        /* #include "mathx.h" */
        #include <stddef.h>
        extern int mathx_calls;
        int mathx_gcd(int a, int b);
        double mathx_mean(const double *v, size_t n);
        static inline int mathx_sq(int x) { return x * x; }

        int main(void) {
            double v[] = {2, 4, 9};
            printf("gcd=%d mean=%.1f sq=%d calls=%d\n",
                   mathx_gcd(-48, 18), mathx_mean(v, 3), mathx_sq(7), mathx_calls);
            return 0;
        }

        /* (the definitions from mathx.c, pasted here so this sample runs as one file) */
        int mathx_calls = 0;
        int mathx_gcd(int a, int b) {
            mathx_calls++;
            a = a < 0 ? -a : a; b = b < 0 ? -b : b;
            while (b) { int t = a % b; a = b; b = t; }
            return a;
        }
        double mathx_mean(const double *v, size_t n) {
            mathx_calls++;
            double s = 0;
            for (size_t i = 0; i < n; i++) s += v[i];
            return n ? s / n : 0.0;
        }
    ''', out="gcd=6 mean=5.0 sq=49 calls=2", caption="C — main.c (run as one file)")
    yield shell('''
        $ gcc -c mathx.c -o mathx.o                 # compile each module separately
        $ gcc -c main.c  -o main.o
        $ gcc main.o mathx.o -o app                 # link them
        $ ./app
        gcd=6 mean=5.0 sq=49 calls=2

        # or in one step
        $ gcc -Wall -Wextra main.c mathx.c -o app

        # build a static library and link against it
        $ ar rcs libmathx.a mathx.o
        $ gcc main.c -L. -lmathx -o app
    ''')
    yield section("What goes where", "layout-2")
    yield table(
        ["In the header (`.h`)", "In the source (`.c`)"],
        ["Function prototypes", "Function definitions"],
        ["`extern` variable declarations", "The one definition of each global"],
        ["Type definitions (`struct`, `enum`, `typedef`)", "`static` helper functions and file-private globals"],
        ["Macros and `static inline` helpers", "`#include` of its own header first"],
        ["Include guard / `#pragma once`", "—"],
    )
    yield warn("Never *define* a non-`static` variable or function in a header (`int count = 0;`). Every `.c` file that includes it gets its own definition, and the linker fails with “duplicate symbol” / “multiple definition”.")
    yield section("A minimal Makefile", "hammer")
    yield shell('''
        CC      = gcc
        CFLAGS  = -std=c17 -Wall -Wextra -O2
        OBJS    = main.o mathx.o

        app: $(OBJS)
        	$(CC) $(CFLAGS) $(OBJS) -o $@

        %.o: %.c mathx.h
        	$(CC) $(CFLAGS) -c $< -o $@

        clean:
        	rm -f $(OBJS) app
    ''', "Makefile")
    yield note("Make recompiles only the files whose sources (or headers) changed. Larger projects use CMake or Meson to generate the build.")
    yield qa("What is an include guard and why is it needed?",
             "`#ifndef X_H / #define X_H / … / #endif` around a header’s content. If the header is included twice in one translation unit (directly or via other headers), the second copy expands to nothing, avoiding redefinition errors for types and macros. `#pragma once` does the same and is supported by all major compilers, though non-standard.")
    yield qa("Why separate declarations and definitions into .h and .c files?",
             "It gives each module a public interface and a private implementation, allows separate compilation (only changed files are recompiled), lets many files share one set of declarations so the compiler checks every call, and keeps exactly one definition of each symbol for the linker.")


@topic(G, "variadic-functions", "Variadic Functions", "dots")
def _():
    yield lead("Functions like `printf` take a variable number of arguments. `<stdarg.h>` lets you write your own: `va_start`, `va_arg`, `va_end` walk the extra arguments — with no type safety at all.")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdarg.h>

        /* the count is passed explicitly: the callee can't know how many arguments there are */
        int sum(int count, ...) {
            va_list ap;
            va_start(ap, count);                 /* start after the last named parameter */
            int total = 0;
            for (int i = 0; i < count; i++)
                total += va_arg(ap, int);        /* you must know each argument's type */
            va_end(ap);
            return total;
        }

        /* a sentinel (negative number) marks the end instead */
        double average(double first, ...) {
            va_list ap;
            va_start(ap, first);
            double s = 0;
            int n = 0;
            for (double x = first; x >= 0; x = va_arg(ap, double)) { s += x; n++; }
            va_end(ap);
            return n ? s / n : 0;
        }

        int main(void) {
            printf("%d %d\n", sum(3, 10, 20, 30), sum(0));
            printf("%.2f\n", average(1.0, 2.0, 4.5, -1.0));
            return 0;
        }
    ''', out='''
        60 0
        2.50
    ''')
    yield section("Forwarding to vprintf: a logging function", "file-text")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdarg.h>

        /* the format attribute makes the compiler check calls like printf */
        __attribute__((format(printf, 2, 3)))
        void log_msg(const char *level, const char *fmt, ...) {
            va_list ap;
            va_start(ap, fmt);
            printf("[%s] ", level);
            vprintf(fmt, ap);                    /* the v- variants take a va_list */
            printf("\n");
            va_end(ap);
        }

        int main(void) {
            log_msg("INFO", "server started on port %d", 8080);
            log_msg("WARN", "%s is %.1f%% full", "disk", 91.5);
            return 0;
        }
    ''', out='''
        [INFO] server started on port 8080
        [WARN] disk is 91.5% full
    ''')
    yield section("Rules", "list-check")
    yield ul(
        "At least one named parameter is required before `...` (until C23).",
        "*Default argument promotions* apply to the variadic part: `char`/`short` arrive as `int`, `float` as `double`. So `va_arg(ap, float)` or `va_arg(ap, char)` is wrong.",
        "The callee must learn the number and types of the arguments some other way: a count, a sentinel, or a format string.",
        "Reading more arguments than were passed, or with the wrong type, is undefined behaviour.",
        "Every `va_start` (and `va_copy`) needs a matching `va_end`.",
    )
    yield qa("How does printf know how many arguments it received?",
             "It doesn’t — it trusts the format string. Each conversion specifier tells it to fetch one more argument of a given type with `va_arg`. Too few arguments, or mismatched types, are undefined behaviour, which is why compilers check `printf` formats (`-Wformat`) and why user-controlled format strings are a security hole.")
    yield qa("Why can't you use va_arg(ap, float)?",
             "Because a `float` passed through `...` is promoted to `double` by the caller. The callee must read it as `double`; asking for a `float` reads the wrong number of bytes / wrong register — undefined behaviour.")


@topic(G, "error-handling", "Error Handling: errno & Return Codes", "alert-circle")
def _():
    yield lead("C has no exceptions. Functions report failure through their **return value** (`NULL`, `-1`, `EOF`), and the library adds detail in the global `errno`. Checking every result is the programmer’s job.")
    yield section("Library conventions", "list")
    yield table(
        ["Function kind", "Failure signal", "Details"],
        ["Returns a pointer (`fopen`, `malloc`)", "`NULL`", "`errno` set (by POSIX)"],
        ["Returns a count (`fread`, `scanf`)", "Fewer items than requested / `EOF`", "`feof` / `ferror`"],
        ["POSIX system calls (`open`, `read`)", "`-1`", "`errno`"],
        ["Conversions (`strtol`)", "Result + `end` pointer", "`errno == ERANGE` on overflow"],
        ["Math (`sqrt(-1)`, `log(0)`)", "NaN / ±HUGE_VAL", "`errno == EDOM` / `ERANGE` (if `math_errhandling` says so)"],
    )
    yield section("errno, strerror, perror", "bug")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>
        #include <errno.h>
        #include <stdlib.h>

        int main(void) {
            FILE *f = fopen("does-not-exist.txt", "r");
            if (f == NULL) {
                int saved = errno;                 /* save it: the next call may overwrite it */
                printf("fopen failed: errno=%d (%s)\n", saved, strerror(saved));
                printf("is ENOENT? %s\n", saved == ENOENT ? "yes" : "no");
                perror("fopen");                   /* prints "fopen: No such file..." to stderr */
            }

            errno = 0;                             /* strtol only sets errno on error: reset first */
            long v = strtol("99999999999999999999", NULL, 10);
            if (errno == ERANGE) printf("overflow, clamped to %ld\n", v);
            return 0;
        }
    ''', out='''
        fopen failed: errno=2 (No such file or directory)
        is ENOENT? yes
        overflow, clamped to 9223372036854775807
    ''')
    yield warn("`errno` is only meaningful right after a function has *reported* failure. Successful calls may leave any value in it, so never test `errno` alone to detect an error.")
    yield section("Designing your own error reporting", "code")
    yield snippet("c", r'''
        #include <stdio.h>

        typedef enum { ERR_OK = 0, ERR_EMPTY, ERR_RANGE, ERR_PARSE } Err;

        const char *err_str(Err e) {
            static const char *msg[] = {"ok", "empty input", "out of range", "not a number"};
            return msg[e];
        }

        /* return the status; deliver the result through an out-parameter */
        Err parse_percent(const char *s, int *out) {
            if (!s || !*s) return ERR_EMPTY;
            int v = 0;
            for (; *s; s++) {
                if (*s < '0' || *s > '9') return ERR_PARSE;
                v = v * 10 + (*s - '0');
                if (v > 100) return ERR_RANGE;
            }
            *out = v;
            return ERR_OK;
        }

        int main(void) {
            const char *inputs[] = {"42", "", "250", "4x"};
            for (int i = 0; i < 4; i++) {
                int p;
                Err e = parse_percent(inputs[i], &p);
                if (e == ERR_OK) printf("'%s' -> %d%%\n", inputs[i], p);
                else printf("'%s' -> error: %s\n", inputs[i], err_str(e));
            }
            return 0;
        }
    ''', out='''
        '42' -> 42%
        '' -> error: empty input
        '250' -> error: out of range
        '4x' -> error: not a number
    ''')
    yield section("Cleanup with goto", "arrow-back-up")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int process(const char *path) {
            int rc = -1;
            char *buf = NULL;
            FILE *f = fopen(path, "w+");
            if (!f) goto out;

            buf = malloc(64);
            if (!buf) goto close_file;

            if (fputs("data\n", f) == EOF) goto free_buf;
            rewind(f);
            if (!fgets(buf, 64, f)) goto free_buf;
            printf("read back: %s", buf);
            rc = 0;                                 /* success */

        free_buf:                                   /* release in reverse order of acquisition */
            free(buf);
        close_file:
            fclose(f);
        out:
            return rc;
        }

        int main(void) {
            printf("rc = %d\n", process("work.txt"));
            printf("rc = %d\n", process("no-such-dir/work.txt"));
            return 0;
        }
    ''', out='''
        read back: data
        rc = 0
        rc = -1
    ''')
    yield section("Terminating", "power")
    yield table(
        ["Call", "Effect"],
        ["`return n;` from `main`", "Same as `exit(n)`"],
        ["`exit(status)`", "Runs `atexit` handlers, flushes and closes streams, then ends the process"],
        ["`_Exit(status)` / `_exit`", "Ends immediately — no handlers, no flushing"],
        ["`abort()`", "Raises `SIGABRT` — abnormal termination, core dump; used by `assert`"],
        ["`quick_exit` (C11)", "Runs `at_quick_exit` handlers only"],
    )
    yield qa("How do you handle errors in C without exceptions?",
             "Return a status code (or `NULL`/`-1`) from every fallible function and pass results through out-parameters; check every return value; propagate errors upward; use `errno` / `strerror` for library failures; and structure cleanup with the `goto cleanup` pattern so each resource is released exactly once on every path. `setjmp`/`longjmp` exist for non-local jumps but skip cleanup and are rarely appropriate.")
    yield qa("Is errno thread-safe?",
             "Yes on modern systems: since C11, `errno` is a macro that expands to a *thread-local* lvalue (often `(*__errno_location())`), so each thread has its own copy.")
