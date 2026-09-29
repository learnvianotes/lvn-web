from kit import *

G = "Standard Library, Modern C & Interview"


@topic(G, "stdlib-tour", "Standard Library Tour: stdlib.h", "books")
def _():
    yield lead("The C standard library is small — about 30 headers. `<stdlib.h>` is the grab-bag: memory, conversions, random numbers, sorting, searching, integer arithmetic and process control.")
    yield section("The headers you will use", "list")
    yield table(
        ["Header", "Provides"],
        ["`<stdio.h>`", "Streams, `printf`/`scanf` families, files"],
        ["`<stdlib.h>`", "`malloc`/`free`, `strtol`/`strtod`, `rand`, `qsort`/`bsearch`, `abs`/`div`, `exit`, `getenv`, `system`"],
        ["`<string.h>`", "`str…` and `mem…` functions"],
        ["`<ctype.h>`", "Character classification and case conversion"],
        ["`<math.h>`", "`sqrt`, `pow`, trigonometry, rounding (link with `-lm` on Linux)"],
        ["`<time.h>`", "`time`, `clock`, `struct tm`, `strftime`, `mktime`"],
        ["`<stdint.h>` / `<inttypes.h>`", "Fixed-width integers and their printf macros"],
        ["`<stdbool.h>` / `<stddef.h>`", "`bool`; `size_t`, `NULL`, `offsetof`, `ptrdiff_t`"],
        ["`<limits.h>` / `<float.h>`", "Ranges of the numeric types"],
        ["`<errno.h>` / `<assert.h>`", "Error numbers; debug assertions"],
        ["`<stdarg.h>`", "Variadic functions"],
        ["`<signal.h>` / `<setjmp.h>`", "Signals; non-local jumps"],
        ["`<stdatomic.h>` / `<threads.h>` (C11)", "Atomics; threads (optional — often POSIX `pthread.h` instead)"],
    )
    yield section("Integer helpers", "calculator")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            printf("%d %ld %lld\n", abs(-7), labs(-70000L), llabs(-9000000000LL));
            div_t d = div(17, 5);                 /* quotient and remainder together */
            printf("17 / 5 = %d r %d\n", d.quot, d.rem);
            printf("%ld %lu %.3f\n", strtol("-0x1F", NULL, 16), strtoul("777", NULL, 8), strtod("6.02e23", NULL) / 1e23);
            return 0;
        }
    ''', out='''
        7 70000 9000000000
        17 / 5 = 3 r 2
        -31 511 6.020
    ''')
    yield section("Random numbers", "dice")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int roll(void) { return rand() % 6 + 1; }              /* slight modulo bias; fine for games */

        int main(void) {
            srand(42);                                          /* same seed -> same sequence */
            int first[5], ok = 1;
            for (int i = 0; i < 5; i++) { first[i] = roll(); if (first[i] < 1 || first[i] > 6) ok = 0; }
            srand(42);
            for (int i = 0; i < 5; i++) if (roll() != first[i]) ok = 0;
            printf("rolls in 1..6 and reproducible: %s\n", ok ? "yes" : "no");
            printf("RAND_MAX >= 32767: %s\n", RAND_MAX >= 32767 ? "yes" : "no");

            double u = rand() / (RAND_MAX + 1.0);               /* uniform in [0, 1) */
            printf("u in [0,1): %s\n", u >= 0 && u < 1 ? "yes" : "no");
            return 0;
        }
    ''', out='''
        rolls in 1..6 and reproducible: yes
        RAND_MAX >= 32767: yes
        u in [0,1): yes
    ''')
    yield note("Seed once with `srand((unsigned)time(NULL))` for different runs. `rand()` is low quality and **never** suitable for security — use the OS (`getrandom`, `arc4random`, `/dev/urandom`).")
    yield section("Process and environment", "settings")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        void goodbye(void) { printf("atexit handler ran\n"); }

        int main(void) {
            atexit(goodbye);                     /* runs when main returns or exit() is called */
            const char *path = getenv("PATH");
            printf("PATH is %s\n", path ? "set" : "unset");
            printf("NO_SUCH_VAR -> %s\n", getenv("NO_SUCH_VAR_123") ? "set" : "NULL");
            return EXIT_SUCCESS;
        }
    ''', out='''
        PATH is set
        NO_SUCH_VAR -> NULL
        atexit handler ran
    ''')
    yield qa("What does exit() do that return from a function does not?",
             "`exit` terminates the whole process from anywhere: it calls functions registered with `atexit` in reverse order, flushes and closes all open streams, removes `tmpfile` files, and returns the status to the OS. Returning from `main` does the same; returning from any other function just goes back to its caller.")


@topic(G, "math-ctype-time", "math.h, ctype.h & time.h", "math-function")
def _():
    yield lead("Three small headers you reach for constantly: floating-point maths, character classification, and dates & times.")
    yield section("math.h", "math")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <math.h>

        int main(void) {
            printf("sqrt=%.4f pow=%.0f cbrt=%.1f hypot=%.1f\n", sqrt(2.0), pow(2, 10), cbrt(27), hypot(3, 4));
            printf("floor=%.0f ceil=%.0f round=%.0f trunc=%.0f\n", floor(-2.5), ceil(-2.5), round(-2.5), trunc(-2.5));
            printf("fabs=%.1f fmod=%.1f\n", fabs(-3.5), fmod(10.5, 3));
            printf("exp(1)=%.5f log=%.4f log10=%.1f log2=%.1f\n", exp(1), log(10), log10(1000), log2(8));
            double pi = acos(-1.0);
            printf("pi=%.6f sin(pi/6)=%.2f atan2(1,1)=%.4f\n", pi, sin(pi / 6), atan2(1, 1));
            printf("%f %f %d %d\n", sqrt(-1.0), INFINITY, isnan(sqrt(-1.0)), isinf(-INFINITY));
            return 0;
        }
    ''', out='''
        sqrt=1.4142 pow=1024 cbrt=3.0 hypot=5.0
        floor=-3 ceil=-2 round=-3 trunc=-2
        fabs=3.5 fmod=1.5
        exp(1)=2.71828 log=2.3026 log10=3.0 log2=3.0
        pi=3.141593 sin(pi/6)=0.50 atan2(1,1)=0.7854
        nan inf 1 1
    ''', caption="C — macOS output (Linux glibc may print -nan for sqrt(-1))")
    yield warn("Trig functions take **radians**. `abs()` is for `int` — `abs(-2.5)` silently truncates; use `fabs` for doubles. On Linux, link with `-lm`.")
    yield section("ctype.h", "abc")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <ctype.h>

        int main(void) {
            const char *s = "Hi 42_x!";
            for (const char *p = s; *p; p++) {
                unsigned char c = (unsigned char)*p;        /* the cast avoids UB for negative chars */
                printf("'%c' alpha=%d digit=%d space=%d punct=%d upper=%d -> '%c'\n",
                       c, !!isalpha(c), !!isdigit(c), !!isspace(c), !!ispunct(c), !!isupper(c), toupper(c));
            }
            return 0;
        }
    ''', out='''
        'H' alpha=1 digit=0 space=0 punct=0 upper=1 -> 'H'
        'i' alpha=1 digit=0 space=0 punct=0 upper=0 -> 'I'
        ' ' alpha=0 digit=0 space=1 punct=0 upper=0 -> ' '
        '4' alpha=0 digit=1 space=0 punct=0 upper=0 -> '4'
        '2' alpha=0 digit=1 space=0 punct=0 upper=0 -> '2'
        '_' alpha=0 digit=0 space=0 punct=1 upper=0 -> '_'
        'x' alpha=1 digit=0 space=0 punct=0 upper=0 -> 'X'
        '!' alpha=0 digit=0 space=0 punct=1 upper=0 -> '!'
    ''')
    yield table(
        ["Function", "True for"],
        ["`isalpha` / `isdigit` / `isalnum`", "letters / `0-9` / either"],
        ["`isspace`", "space, `\\t`, `\\n`, `\\v`, `\\f`, `\\r`"],
        ["`isupper` / `islower`", "case"],
        ["`ispunct`", "printable, not alnum, not space"],
        ["`isxdigit`", "`0-9a-fA-F`"],
        ["`toupper` / `tolower`", "convert (other characters unchanged)"],
    )
    yield note("The `is…` functions return *non-zero* for true — not necessarily 1. That is why the sample uses `!!` to normalise.")
    yield section("time.h", "clock")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <time.h>

        int main(void) {
            struct tm launch = {0};
            launch.tm_year = 2026 - 1900;       /* years since 1900 */
            launch.tm_mon = 0;                  /* 0 = January */
            launch.tm_mday = 26;
            launch.tm_hour = 9;
            launch.tm_isdst = -1;               /* let mktime work out DST */

            time_t t = mktime(&launch);         /* normalises fields and fills tm_wday / tm_yday */
            char buf[64];
            strftime(buf, sizeof buf, "%A, %d %B %Y %H:%M", &launch);
            printf("%s (day %d of the year)\n", buf, launch.tm_yday + 1);

            struct tm later = launch;
            later.tm_mday += 40;                /* date arithmetic: mktime rolls over months */
            time_t t2 = mktime(&later);
            strftime(buf, sizeof buf, "%Y-%m-%d", &later);
            printf("+40 days = %s, difftime = %.0f days\n", buf, difftime(t2, t) / 86400);
            return 0;
        }
    ''', out='''
        Monday, 26 January 2026 09:00 (day 26 of the year)
        +40 days = 2026-03-07, difftime = 40 days
    ''')
    yield snippet("c", r'''
        #include <stdio.h>
        #include <time.h>

        int main(void) {
            time_t now = time(NULL);                       /* seconds since 1970-01-01 UTC */
            printf("now: %s", ctime(&now));

            clock_t start = clock();                       /* CPU time, not wall time */
            volatile double x = 0;
            for (int i = 0; i < 10000000; i++) x += i;
            printf("loop took %.3f s of CPU\n", (double)(clock() - start) / CLOCKS_PER_SEC);
            return 0;
        }
    ''', caption="C — current time and timing (output varies)")
    yield qa("What is the difference between time() and clock()?",
             "`time()` returns wall-clock calendar time (seconds since the Unix epoch). `clock()` returns the processor time used by the program, in `CLOCKS_PER_SEC` units — it does not advance while the process sleeps. For precise wall-clock intervals use POSIX `clock_gettime(CLOCK_MONOTONIC, …)` or C11 `timespec_get`.")


@topic(G, "concurrency", "Threads & Atomics (Intro)", "arrows-shuffle")
def _():
    yield lead("C11 standardised a memory model, `<stdatomic.h>` and an optional `<threads.h>`. In practice most C code uses POSIX threads (`pthread`). Shared data needs a mutex or atomics — otherwise it is a *data race* (undefined behaviour).")
    yield section("Creating and joining threads", "git-fork")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <pthread.h>

        typedef struct { int id; long from, to, result; } Job;

        void *sum_range(void *arg) {                 /* thread entry: void *(*)(void *) */
            Job *job = arg;
            long s = 0;
            for (long i = job->from; i < job->to; i++) s += i;
            job->result = s;                          /* each thread writes only its own Job */
            return NULL;
        }

        int main(void) {
            enum { N = 4 };
            pthread_t tid[N];
            Job jobs[N];
            for (int i = 0; i < N; i++) {
                jobs[i] = (Job){i, i * 250000L, (i + 1) * 250000L, 0};
                pthread_create(&tid[i], NULL, sum_range, &jobs[i]);
            }
            long total = 0;
            for (int i = 0; i < N; i++) {
                pthread_join(tid[i], NULL);           /* wait, then read the result */
                total += jobs[i].result;
            }
            printf("sum 0..999999 = %ld\n", total);
            return 0;
        }
    ''', out="sum 0..999999 = 499999500000", caption="C — pthreads (Linux: compile with -pthread)")
    yield section("Protecting shared state", "lock")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <pthread.h>
        #include <stdatomic.h>

        long plain_counter = 0;
        pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
        atomic_long atomic_counter = 0;

        void *work(void *arg) {
            (void)arg;
            for (int i = 0; i < 100000; i++) {
                pthread_mutex_lock(&lock);
                plain_counter++;                         /* critical section */
                pthread_mutex_unlock(&lock);
                atomic_fetch_add(&atomic_counter, 1);    /* lock-free alternative */
            }
            return NULL;
        }

        int main(void) {
            pthread_t t[4];
            for (int i = 0; i < 4; i++) pthread_create(&t[i], NULL, work, NULL);
            for (int i = 0; i < 4; i++) pthread_join(t[i], NULL);
            printf("mutex: %ld, atomic: %ld\n", plain_counter, atomic_load(&atomic_counter));
            return 0;
        }
    ''', out="mutex: 400000, atomic: 400000")
    yield warn("Without the mutex, `counter++` is a read-modify-write of three steps; two threads interleave and increments are lost (and the program has undefined behaviour). Detect races with `-fsanitize=thread` (ThreadSanitizer).")
    yield table(
        ["Tool", "Use"],
        ["`pthread_mutex_t`", "Mutual exclusion around a critical section"],
        ["`pthread_cond_t`", "Wait for a condition (producer/consumer)"],
        ["`pthread_rwlock_t`", "Many readers or one writer"],
        ["`_Atomic` / `atomic_int`", "Lock-free counters, flags"],
        ["`_Thread_local`", "Per-thread variables"],
        ["`pthread_once` / `call_once`", "One-time initialisation"],
    )
    yield qa("What is a race condition, and what is a deadlock?",
             "A race condition is when the result depends on the unpredictable interleaving of threads — e.g. two threads doing `count++` on shared data without synchronisation (in C a data race is undefined behaviour). A deadlock is when threads wait on each other forever — e.g. thread A holds lock 1 and wants lock 2 while thread B holds lock 2 and wants lock 1. Prevent deadlocks by always acquiring locks in a consistent global order.")
    yield qa("Is volatile enough for sharing a flag between threads?",
             "No. `volatile` prevents the compiler from caching the value but gives no atomicity and no ordering guarantees between CPU cores. Use `_Atomic` (e.g. `atomic_bool`) or a mutex.")


@topic(G, "modern-c", "C99, C11, C17 & C23 Features", "sparkles")
def _():
    yield lead("Modern C is much nicer than the C89 many tutorials still teach. Use `-std=c17` (or `-std=c23`) and these features freely.")
    yield section("C99", "number-9")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdbool.h>
        #include <stdint.h>

        struct Point { int x, y; };

        static inline int sq(int v) { return v * v; }        /* inline functions */

        int main(void) {
            // line comments
            for (int i = 0; i < 1; i++) { }                   /* declarations in for */
            bool ready = true;                                 /* <stdbool.h> */
            int64_t big = 1LL << 40;                           /* <stdint.h>, long long */
            struct Point p = {.y = 2, .x = 1};                 /* designated initializers */
            int arr[5] = {[4] = 9};
            int n = 3;
            int vla[n];                                        /* variable-length array */
            vla[0] = sq(n);
            struct Point *q = &(struct Point){5, 6};           /* compound literal */
            printf("%d %lld %d %d %d %d %d\n", ready, (long long)big, p.x, arr[4], vla[0], q->y, __func__[0]);
            return 0;
        }
    ''', out="1 1099511627776 1 9 9 6 109")
    yield section("C11", "number-11")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdalign.h>
        #include <stdnoreturn.h>
        #include <stdlib.h>

        /* _Generic: compile-time dispatch on the type of an expression */
        #define type_name(x) _Generic((x), \
            int: "int", double: "double", char *: "char *", default: "other")

        #define print_any(x) _Generic((x), int: print_int, double: print_double)(x)
        void print_int(int v) { printf("int %d\n", v); }
        void print_double(double v) { printf("double %.2f\n", v); }

        _Static_assert(sizeof(int) >= 4, "need 32-bit int");   /* compile-time check */

        struct Packet {
            int kind;
            union { int code; float value; };                    /* anonymous union */
        };

        noreturn void die(const char *msg) { fprintf(stderr, "%s\n", msg); exit(1); }

        int main(void) {
            char *s = "hi";
            printf("%s %s %s %s\n", type_name(42), type_name(3.0), type_name(s), type_name(1L));
            print_any(7);
            print_any(2.5);
            struct Packet pk = {.kind = 1, .code = 404};
            printf("%d %zu\n", pk.code, alignof(double));
            if (pk.code != 404) die("unexpected");
            return 0;
        }
    ''', out='''
        int double char * other
        int 7
        double 2.50
        404 8
    ''')
    yield table(
        ["C11 feature", "Purpose"],
        ["`_Generic`", "Type-generic macros (how `<tgmath.h>` works)"],
        ["`_Static_assert` / `static_assert`", "Compile-time assertions"],
        ["`_Alignas` / `_Alignof`", "Control / query alignment"],
        ["`_Noreturn`", "Function never returns (`exit`, `abort`)"],
        ["Anonymous structs/unions", "Access nested members directly"],
        ["`_Atomic`, `<stdatomic.h>`, memory model", "Portable concurrency"],
        ["`<threads.h>` (optional)", "Threads, mutexes, condition variables"],
        ["`_Thread_local`", "Thread-local storage"],
        ["Bounds-checked `_s` functions (Annex K)", "Optional; rarely implemented"],
        ["`gets` removed", "Finally"],
        ["`aligned_alloc`, `quick_exit`, `timespec_get`", "Library additions"],
    )
    yield section("C17", "number-17-small")
    yield p("C17 (also called C18) is a *bug-fix* release: no new features, only clarifications and defect fixes to C11. `__STDC_VERSION__` is `201710L`. It is the default of GCC 8+ and recent Clang.")
    yield section("C23", "number-23-small")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdckdint.h>

        [[nodiscard]] int twice(int x) { return 2 * x; }     /* standard attributes */

        enum Small : unsigned char { A, B, C };                  /* fixed underlying type */

        int main(void) {
            constexpr int size = 4;                              /* true compile-time constant */
            int arr[size] = {};                                  /* empty initializer = zero */
            bool ok = true;                                      /* bool/true/false are keywords */
            int *p = nullptr;                                    /* typed null pointer constant */
            typeof(size) mask = 0b1111'0000;                     /* typeof, binary literal, digit separator */
            auto ratio = 2.5;                                    /* type inference */
            int sum;
            bool overflow = ckd_add(&sum, 2147483647, 1);        /* checked arithmetic */
            static_assert(sizeof(enum Small) == 1);              /* message optional */
            printf("%d %d %d %d %.1f %d %d\n", arr[3], ok, p == nullptr, mask, ratio, twice(size), overflow);
            return 0;
        }
    ''', out="0 1 1 240 2.5 8 1", flags=("-std=c23",), caption="C — compiled with -std=c23")
    yield table(
        ["C23 feature", "Replaces"],
        ["`bool`, `true`, `false`, `static_assert`, `alignas`… as keywords", "`<stdbool.h>` etc."],
        ["`nullptr` / `nullptr_t`", "`NULL` (which may be `0`)"],
        ["`constexpr` objects", "`#define` / `enum` constants"],
        ["`typeof`, `typeof_unqual`", "GNU `__typeof__`"],
        ["`auto` type inference", "Spelling out types"],
        ["`[[nodiscard]]`, `[[maybe_unused]]`, `[[deprecated]]`, `[[fallthrough]]`", "`__attribute__`"],
        ["`0b` literals, `'` digit separators", "Hex masks"],
        ["`<stdckdint.h>`: `ckd_add`, `ckd_sub`, `ckd_mul`", "Hand-written overflow checks"],
        ["`#embed`, `#elifdef`, `__has_include`", "External tools, nested `#ifdef`"],
        ["`f(void)` ≡ `f()`; K&R definitions removed", "Unprototyped functions"],
        ["Two’s complement mandatory", "Implementation-defined representations"],
    )
    yield qa("What is _Generic used for?",
             "Selecting an expression at compile time based on the type of a controlling expression — the foundation of type-generic macros like `<tgmath.h>`’s `sqrt` that call `sqrtf`, `sqrt` or `sqrtl` depending on the argument type. It gives C a limited form of overloading.")
    yield qa("What are designated initializers?",
             "C99 syntax to initialise specific members or indexes by name: `struct Point p = {.y = 2, .x = 1};`, `int a[10] = {[9] = 1};`. Unmentioned members are zero-initialised, the order doesn’t matter, and the code survives reordering of struct fields.")


@topic(G, "best-practices", "Best Practices & Tooling", "checklist")
def _():
    yield lead("C rewards discipline. These habits and tools prevent most of the bugs covered in these notes.")
    yield section("Compile and test", "tools")
    yield table(
        ["Practice", "How"],
        ["Maximum warnings", "`-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wformat=2`, and `-Werror` in CI"],
        ["Sanitizers in debug/test builds", "`-fsanitize=address,undefined` (and `thread` for concurrent code)"],
        ["Memory checking", "`valgrind --leak-check=full ./app`"],
        ["Static analysis", "`clang --analyze`, `clang-tidy`, `cppcheck`, `gcc -fanalyzer`"],
        ["Debugger", "`gdb` / `lldb` with `-g -O0`: breakpoints, `bt`, `print`, watchpoints"],
        ["Fuzzing", "libFuzzer / AFL++ for parsers and anything taking untrusted input"],
        ["Formatting", "`clang-format` — never argue about braces again"],
        ["Hardening", "`-D_FORTIFY_SOURCE=2 -O2 -fstack-protector-strong`"],
    )
    yield section("Coding habits", "code")
    yield cards(
        ("Initialise everything", "`int count = 0;`, `struct cfg c = {0};`, `char *p = NULL;`. Uninitialised reads are undefined.", "square-check"),
        ("Check every return value", "`malloc`, `fopen`, `scanf`, `fread`, `snprintf`, `strtol`… Ignoring failures turns errors into crashes elsewhere.", "checks"),
        ("Carry sizes with buffers", "`void f(char *buf, size_t len)`. Use `snprintf`, `fgets`, `memcpy` with explicit sizes. Never `gets`, avoid `strcpy`/`sprintf`.", "ruler"),
        ("Clear ownership", "Document who frees each allocation; pair every `create` with a `destroy`; `NULL` pointers after `free`.", "user-check"),
        ("`const` and `static` by default", "`const` for read-only pointers; `static` for file-private functions and globals.", "lock"),
        ("Small functions, few globals", "Pass state explicitly. Globals make code untestable and thread-unsafe.", "puzzle"),
        ("Prefer functions to macros", "`static inline` functions and `enum` constants are type-checked; keep macros for what only macros can do.", "hash"),
        ("Use the right types", "`size_t` for sizes, `<stdint.h>` for exact widths, `unsigned` for bits, `bool` for flags.", "box"),
    )
    yield section("A defensive pattern in one place", "shield-check")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        typedef struct {
            char  *data;
            size_t len;
        } Text;

        /* returns 0 on success; on failure *out is untouched and nothing leaks */
        int text_read_file(const char *path, Text *out) {
            int rc = -1;
            char *buf = NULL;
            FILE *f = fopen(path, "rb");
            if (!f) goto done;
            if (fseek(f, 0, SEEK_END) != 0) goto done;
            long size = ftell(f);
            if (size < 0) goto done;
            rewind(f);
            buf = malloc((size_t)size + 1);
            if (!buf) goto done;
            if (fread(buf, 1, (size_t)size, f) != (size_t)size) goto done;
            buf[size] = '\0';
            out->data = buf;
            out->len = (size_t)size;
            buf = NULL;                  /* ownership transferred to *out */
            rc = 0;
        done:
            free(buf);                   /* free(NULL) is fine */
            if (f) fclose(f);
            return rc;
        }

        int main(void) {
            FILE *f = fopen("note.txt", "w");
            if (!f) return 1;
            fputs("clean C", f);
            fclose(f);

            Text t = {0};
            if (text_read_file("note.txt", &t) == 0) {
                printf("%zu bytes: %s\n", t.len, t.data);
                free(t.data);
            }
            printf("missing file -> %d\n", text_read_file("missing.txt", &t));
            return 0;
        }
    ''', out='''
        7 bytes: clean C
        missing file -> -1
    ''')
    yield section("Debugging workflow", "bug")
    yield shell('''
        $ gcc -g -O0 -Wall -Wextra -fsanitize=address,undefined app.c -o app
        $ ./app                       # sanitizer reports file:line of the first bad access
        $ gdb ./app                   # or: lldb ./app
        (gdb) break parse_line        # stop in a function
        (gdb) run input.txt
        (gdb) next / step / finish    # step over / into / out of
        (gdb) print *node             # inspect memory
        (gdb) bt                      # backtrace after a crash
        (gdb) watch count             # stop when a variable changes
    ''')
    yield qa("How would you debug a segmentation fault?",
             "Rebuild with `-g -fsanitize=address,undefined` and rerun — the sanitizer usually names the exact bad access and where the memory was allocated/freed. Otherwise run under `gdb`/`lldb` (or load the core dump) and take a backtrace (`bt`) to see the crashing line, then inspect the pointers involved. Valgrind is the alternative when you cannot recompile.")


@topic(G, "interview-questions", "C Interview Questions", "message-question")
def _():
    yield lead("The questions that come up again and again in C and embedded interviews — each with a crisp answer. Most are covered in depth in the earlier topics.")
    yield section("Output prediction warm-ups", "eye")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s[] = "interview";
            char *p = s;
            printf("%zu %zu\n", sizeof s, strlen(s));        /* 10 9 */
            printf("%c %c\n", *p + 1, *(p + 1));             /* 'i'+1 = 'j', then 'n' */

            int a[] = {1, 2, 3, 4, 5};
            int *q = a + 1;
            printf("%d %d %td\n", q[2], *(a + 4), &a[4] - q);

            unsigned int u = 5;
            int i = -10;
            printf("%s\n", u + i > 5 ? "big" : "small");     /* i converts to unsigned */

            int x = 10;
            printf("%d\n", x >> 1 << 2);                     /* (10 >> 1) << 2 = 20 */
            printf("%d\n", 3 == 3.0);                        /* 3 converts to double */
            printf("%d\n", 'A' + 1);
            return 0;
        }
    ''', out='''
        10 9
        j n
        4 5 3
        big
        20
        1
        66
    ''', flags=("-Wno-sign-compare",), caption="C — compiled with -Wno-sign-compare to allow the trap")
    yield section("Language fundamentals", "school")
    yield qa("What are the storage classes in C?",
             "`auto` (default for locals: block scope, automatic lifetime), `register` (auto + no address; historic hint), `static` (static lifetime; internal linkage at file scope; value persists between calls as a local), `extern` (declares an object/function defined elsewhere, external linkage), and C11 `_Thread_local`. `typedef` is grammatically a storage-class specifier too.")
    yield qa("What is the difference between declaration and definition?",
             "A declaration tells the compiler a name and its type (`extern int x;`, `int f(void);`). A definition also creates the object or supplies the function body (`int x = 0;`, `int f(void) { … }`). A name can be declared many times but defined exactly once.")
    yield qa("What is a volatile variable? Give examples.",
             "A variable whose value can change outside the program’s visible control flow, so the compiler must perform every read and write exactly as written: memory-mapped hardware registers, variables modified in signal handlers (`volatile sig_atomic_t`), and memory changed by DMA. It does not provide thread synchronisation.")
    yield qa("Explain const int *p, int *const p and const int *const p.",
             "Pointer to const int (can’t modify `*p`, can move `p`); const pointer to int (can modify `*p`, can’t move `p`); const pointer to const int (neither). Read the declaration right to left.")
    yield qa("What is the difference between ++i and i++ in a for loop?",
             "None for `int` in a standalone increment — compilers generate identical code. The difference only matters when the expression’s value is used: `i++` yields the old value, `++i` the new one.")
    yield qa("What are sequence points and why do they matter?",
             "Points in execution where all previous side effects are complete: the end of a full expression (`;`), after the first operand of `&&`, `||`, `?:` and `,`, and before a function call. Modifying an object twice (or modifying and reading it for another purpose) without an intervening sequence point is undefined behaviour — e.g. `i = i++`, `a[i] = i++`.")
    yield section("Pointers and memory", "pointer")
    yield qa("What is the difference between malloc and calloc? What does realloc do?",
             "`malloc(n)` returns `n` uninitialised bytes; `calloc(count, size)` returns zeroed memory for `count × size` bytes with overflow checking. `realloc(p, n)` resizes a block, possibly moving it (copying the old contents); on failure it returns `NULL` and leaves the old block intact.")
    yield qa("What are dangling pointers, wild pointers and memory leaks?",
             "A *dangling* pointer points to memory that has been freed or gone out of scope. A *wild* pointer was never initialised and holds a garbage address. A *leak* is allocated memory that is no longer referenced by any pointer, so it can never be freed.")
    yield qa("What is a NULL pointer vs a void pointer?",
             "A null pointer is a *value* — a pointer of any type that points to nothing. A `void *` is a *type* — a generic pointer that can hold the address of any object but must be cast before dereferencing. A `void *` can itself be null.")
    yield qa("Can you return a pointer to a local variable?",
             "No — the local’s lifetime ends when the function returns, so the pointer dangles. Return by value, use a `static` local (not reentrant), write into a caller-provided buffer, or return heap memory that the caller frees.")
    yield qa("What is the difference between arrays and pointers?",
             "An array is a block of storage whose name decays to a pointer to its first element in most expressions; a pointer is a variable storing an address. `sizeof` differs (whole array vs pointer size), an array name can’t be assigned, and `&array` has type pointer-to-array.")
    yield qa("How do you find the size of an array passed to a function?",
             "You can’t — it has decayed to a pointer. Pass the length as a separate parameter (or use a sentinel such as `'\\0'` for strings, or wrap the array in a struct).")
    yield qa("What is memory alignment and structure padding?",
             "Each type must be stored at an address that is a multiple of its alignment; the compiler inserts padding bytes between struct members and at the end to satisfy that for every member and for arrays of the struct. Ordering members from largest to smallest minimises padding.")
    yield qa("Explain stack vs heap.",
             "The stack holds function frames (locals, return addresses); allocation is automatic and very fast but the size is limited and data dies when the function returns. The heap holds `malloc`’d memory; it is large and lives until `free`, but allocation is slower and the programmer manages the lifetime (leaks, use-after-free).")
    yield section("Classic coding questions", "code")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        /* 1. reverse words in place: "the sky is blue" -> "blue is sky the" */
        static void rev(char *a, char *b) { while (a < b) { char t = *a; *a++ = *b; *b-- = t; } }
        void reverse_words(char *s) {
            size_t n = strlen(s);
            if (n == 0) return;
            rev(s, s + n - 1);                               /* reverse whole string */
            for (char *w = s; *w; ) {                        /* then each word */
                while (*w == ' ') w++;
                char *e = w;
                while (*e && *e != ' ') e++;
                if (e > w) rev(w, e - 1);
                w = e;
            }
        }

        /* 2. endianness check */
        int is_little_endian(void) { unsigned x = 1; return *(unsigned char *)&x == 1; }

        /* 3. my_atoi with sign and overflow saturation */
        int my_atoi(const char *s) {
            long v = 0;
            int sign = 1;
            while (*s == ' ') s++;
            if (*s == '-' || *s == '+') sign = (*s++ == '-') ? -1 : 1;
            while (*s >= '0' && *s <= '9') {
                v = v * 10 + (*s++ - '0');
                if (v > 2147483648L) break;
            }
            v *= sign;
            if (v > 2147483647L) return 2147483647;
            if (v < -2147483648L) return (int)-2147483648L;
            return (int)v;
        }

        /* 4. count set bits, reverse bits of a byte */
        unsigned char reverse_byte(unsigned char b) {
            unsigned char r = 0;
            for (int i = 0; i < 8; i++) { r = (unsigned char)((r << 1) | (b & 1)); b >>= 1; }
            return r;
        }

        int main(void) {
            char s[] = "the sky is blue";
            reverse_words(s);
            printf("%s\n", s);
            printf("little endian: %d\n", is_little_endian());
            printf("%d %d %d %d\n", my_atoi("  -42"), my_atoi("+17abc"), my_atoi("99999999999"), my_atoi("-99999999999"));
            printf("0x%02X\n", reverse_byte(0x01));
            return 0;
        }
    ''', out='''
        blue is sky the
        little endian: 1
        -42 17 2147483647 -2147483648
        0x80
    ''')
    yield section("Tricky questions", "brain")
    yield qa("What does printf return?",
             "The number of characters written (excluding the terminating NUL), or a negative value on error. So `printf(\"%d\", printf(\"hello\"))` prints `hello5`.")
    yield qa("What is the output of sizeof on an expression with side effects, e.g. sizeof(i++)?",
             "`i` is not incremented: `sizeof` does not evaluate its operand (except for variable-length arrays); it only inspects the type at compile time.")
    yield qa("How can you swap two variables without a temporary?",
             "`a ^= b; b ^= a; a ^= b;` or `a = a + b; b = a - b; a = a - b;`. Both are curiosities: the XOR version fails if `a` and `b` are the same object (it zeroes it), and the arithmetic version can overflow. A temporary is clearer and just as fast.")
    yield qa("What is the difference between #include guards and #pragma once?",
             "Both stop a header from being processed twice in one translation unit. Guards (`#ifndef X_H`) are standard and work everywhere; `#pragma once` is shorter, avoids guard-name collisions, and is supported by GCC, Clang and MSVC, but is not in the standard.")
    yield qa("Why is gets() dangerous and what replaces it?",
             "`gets` reads a line into a buffer without knowing the buffer’s size, so any long input overflows it — it was the vector of the 1988 Morris worm. It was removed in C11. Use `fgets(buf, sizeof buf, stdin)` (and strip the newline).")
    yield qa("What is a memory-mapped register and how do you access it in C?",
             "A hardware device register exposed at a fixed physical address. Access it through a pointer to `volatile` of the right width: `#define GPIO_OUT (*(volatile uint32_t *)0x40020014u)`, then `GPIO_OUT |= 1u << 5;`. `volatile` ensures every access actually reaches the hardware.")
    yield qa("What happens when you write int *p = malloc(10); p[10] = 1;?",
             "Undefined behaviour twice over: `malloc(10)` gives 10 *bytes* (2 ints on a 4-byte-int system, not 10 ints), and index 10 is far past the end. It may corrupt allocator metadata and crash later. Correct: `int *p = malloc(10 * sizeof *p);` and indexes 0–9.")
    yield qa("Does C use name mangling?",
             "C has no name mangling: the symbol for `int add(int, int)` is just `add` (sometimes `_add`). That is why C functions can’t be overloaded, and why C++ code calling C uses `extern \"C\"` to turn off C++ mangling.")
