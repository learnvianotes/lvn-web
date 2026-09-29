from kit import *

G = "Memory Management"


@topic(G, "dynamic-memory", "malloc, calloc, realloc & free", "database-plus")
def _():
    yield lead("When the size or lifetime of data isn’t known at compile time, request memory from the **heap** at run time. Every successful allocation must be released with exactly one `free`.")
    yield table(
        ["Function (`<stdlib.h>`)", "Does", "Contents", "On failure"],
        ["`malloc(size)`", "Allocate `size` bytes", "Uninitialised (garbage)", "`NULL`"],
        ["`calloc(n, size)`", "Allocate `n × size` bytes (overflow-checked)", "All bits zero", "`NULL`"],
        ["`realloc(p, size)`", "Grow/shrink a block; may move it", "Old contents kept, new part uninitialised", "`NULL`, **old block still valid**"],
        ["`free(p)`", "Release a block", "—", "`free(NULL)` is a no-op"],
        ["`aligned_alloc(al, size)` (C11)", "Allocate with a given alignment", "Uninitialised", "`NULL`"],
    )
    yield section("malloc and free", "plus")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            int n = 5;
            int *a = malloc(n * sizeof *a);     /* sizeof *a: stays right if the type changes */
            if (a == NULL) {                    /* always check */
                fprintf(stderr, "out of memory\n");
                return 1;
            }
            for (int i = 0; i < n; i++) a[i] = i * i;
            for (int i = 0; i < n; i++) printf("%d ", a[i]);
            printf("\n");
            free(a);
            a = NULL;                           /* defensive: no dangling pointer */
            return 0;
        }
    ''', out="0 1 4 9 16")
    yield section("calloc: zeroed memory", "square-rounded-number-0")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            size_t n = 4;
            double *v = calloc(n, sizeof *v);    /* all zeros, and n * size cannot overflow silently */
            if (!v) return 1;
            v[2] = 3.5;
            for (size_t i = 0; i < n; i++) printf("%.1f ", v[i]);
            printf("\n");
            free(v);
            return 0;
        }
    ''', out="0.0 0.0 3.5 0.0")
    yield section("realloc: a growable array", "arrows-maximize")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        typedef struct {
            int *data;
            size_t len, cap;
        } Vec;

        int vec_push(Vec *v, int x) {
            if (v->len == v->cap) {
                size_t new_cap = v->cap ? v->cap * 2 : 1;          /* geometric growth: amortised O(1) */
                int *tmp = realloc(v->data, new_cap * sizeof *tmp);
                if (!tmp) return -1;                              /* v->data is still valid */
                v->data = tmp;
                v->cap = new_cap;
                printf("grew to %zu\n", new_cap);
            }
            v->data[v->len++] = x;
            return 0;
        }

        int main(void) {
            Vec v = {NULL, 0, 0};                 /* realloc(NULL, n) acts like malloc(n) */
            for (int i = 1; i <= 5; i++) vec_push(&v, i * 10);
            printf("len=%zu cap=%zu last=%d\n", v.len, v.cap, v.data[v.len - 1]);
            free(v.data);
            return 0;
        }
    ''', out='''
        grew to 1
        grew to 2
        grew to 4
        grew to 8
        len=5 cap=8 last=50
    ''')
    yield warn("Never write `p = realloc(p, n);` — if `realloc` fails it returns `NULL`, you overwrite your only pointer to the old block, and it leaks. Assign to a temporary first.")
    yield section("Allocating strings and structs", "text-plus")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        typedef struct { char *name; int age; } Person;

        char *dup_string(const char *s) {           /* like POSIX / C23 strdup */
            size_t n = strlen(s) + 1;               /* +1 for the terminator! */
            char *copy = malloc(n);
            if (copy) memcpy(copy, s, n);
            return copy;
        }

        Person *person_new(const char *name, int age) {
            Person *p = malloc(sizeof *p);
            if (!p) return NULL;
            p->name = dup_string(name);
            if (!p->name) { free(p); return NULL; }
            p->age = age;
            return p;
        }

        void person_free(Person *p) {
            if (!p) return;
            free(p->name);                          /* inner allocations first */
            free(p);
        }

        int main(void) {
            Person *p = person_new("Ada", 36);
            if (!p) return 1;
            printf("%s is %d\n", p->name, p->age);
            person_free(p);
            return 0;
        }
    ''', out="Ada is 36")
    yield section("Rules of ownership", "list-check")
    yield ul(
        "Every `malloc`/`calloc`/`realloc` success is matched by **exactly one** `free` of the same pointer.",
        "Only pass `free` a pointer that came from an allocation function (not a stack array, not `p + 1`).",
        "Decide and document *who owns* each allocation — the function that creates it, or the caller.",
        "Free nested allocations before the struct that points to them.",
        "Check sizes for overflow: `n * size` can wrap; `calloc` checks for you.",
        "Leak checkers: Valgrind (`valgrind --leak-check=full ./app`), LeakSanitizer (`-fsanitize=address` on Linux).",
    )
    yield qa("What is the difference between malloc and calloc?",
             "`malloc(bytes)` returns uninitialised memory. `calloc(count, size)` returns zero-filled memory for `count` elements and checks the multiplication for overflow. `calloc` can be as fast as `malloc` for large blocks because the OS hands out pre-zeroed pages.")
    yield qa("What happens if you call free twice on the same pointer?",
             "Undefined behaviour — a *double free*. It typically corrupts the allocator’s internal lists, can crash later in an unrelated `malloc`, and is exploitable. Setting the pointer to `NULL` after freeing makes a second `free(NULL)` harmless.")
    yield qa("Does free return memory to the operating system?",
             "Not necessarily. `free` returns the block to the allocator’s free lists so later `malloc`s can reuse it. Large blocks (served by `mmap`) are usually returned immediately; small ones typically stay with the process.")
    yield qa("Should you cast the result of malloc in C?",
             "No. `void *` converts implicitly to any object pointer type in C, and a cast can hide a missing `#include <stdlib.h>` in old compilers. The cast is required only in C++.")


@topic(G, "memory-layout", "Memory Layout of a C Program", "layout-rows")
def _():
    yield lead("A running C program’s address space is split into segments: code, read-only data, initialised data, zero-initialised data (bss), the heap growing up and the stack growing down.")
    yield table(
        ["Segment", "Holds", "Lifetime", "Notes"],
        ["**Text** (`.text`)", "Machine code of functions", "Program", "Read-only + executable; shared between processes"],
        ["**Read-only data** (`.rodata`)", "String literals, `const` globals", "Program", "Writing crashes"],
        ["**Data** (`.data`)", "Initialised globals / `static`s (`int g = 5;`)", "Program", "Values stored in the executable file"],
        ["**BSS** (`.bss`)", "Zero / uninitialised globals / `static`s", "Program", "Only the size is stored; zero-filled at load"],
        ["**Heap**", "`malloc` / `calloc` / `realloc`", "Until `free`", "Grows upward; managed by the allocator"],
        ["**Stack**", "Locals, parameters, return addresses", "Until the function returns", "Grows downward; ~8 MB default on Linux/macOS main thread"],
    )
    yield flow("high addresses: **stack** ↓", "(free space)", "↑ **heap**", "**.bss**", "**.data**", "**.rodata**", "low addresses: **.text**")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int initialised = 42;          /* .data */
        int zeroed;                    /* .bss  */
        const char *msg = "literal";   /* pointer in .data, the characters in .rodata */

        void where(void) { }           /* .text */

        int main(void) {
            int local = 1;                              /* stack */
            static int counter;                         /* .bss (static, zero) */
            int *heap = malloc(sizeof *heap);           /* heap  */
            if (!heap) return 1;
            printf("text   %p\n", (void *)(size_t)where);
            printf("rodata %p\n", (const void *)msg);
            printf("data   %p\n", (void *)&initialised);
            printf("bss    %p %p\n", (void *)&zeroed, (void *)&counter);
            printf("heap   %p\n", (void *)heap);
            printf("stack  %p\n", (void *)&local);
            free(heap);
            return 0;
        }
    ''', caption="C — addresses differ per run and platform (no fixed output)")
    yield section("Inspecting the segments", "zoom-in")
    yield shell('''
        $ size ./app                      # text / data / bss sizes (Linux)
           text    data     bss     dec     hex filename
           1845     616       8    2469     9a5 ./app
        $ objdump -h ./app                # section headers
        $ nm ./app | grep ' [bBdD] '      # symbols in bss (b/B) and data (d/D)
        $ ulimit -s                       # stack size limit in KB
        8192
    ''')
    yield section("Stack vs heap", "arrows-diff")
    yield table(
        ["", "Stack", "Heap"],
        ["Allocation", "Automatic (move the stack pointer)", "Explicit `malloc` / `free`"],
        ["Speed", "Very fast", "Slower (allocator bookkeeping, possible system call)"],
        ["Size", "Small, fixed limit", "Large — limited by RAM / address space"],
        ["Lifetime", "Ends when the function returns", "Until you `free` it"],
        ["Failure mode", "Stack overflow (crash)", "`malloc` returns `NULL`; leaks, fragmentation"],
        ["Typical bugs", "Returning addresses of locals, huge arrays, deep recursion", "Leaks, use-after-free, double free"],
    )
    yield section("Stack frames", "stack-2")
    yield p("Each call pushes a *frame*: return address, saved registers, parameters that don’t fit in registers, and locals. Returning pops it — which is exactly why a pointer to a local is dangling after the return.")
    yield snippet("c", r'''
        #include <stdio.h>

        int depth(int n) {
            char pad[1024];                /* 1 KB of stack per call */
            pad[0] = (char)n;
            if (n == 0) return pad[0];
            return depth(n - 1) + 1;
        }

        int main(void) {
            printf("%d frames deep, fine\n", depth(100));    /* ~100 KB of stack */
            return 0;
        }
    ''', out="100 frames deep, fine")
    yield warn("`char big[16 * 1024 * 1024];` as a local, or unbounded recursion, overflows the stack. Put large buffers on the heap or make them `static`.")
    yield qa("Where are string literals stored?",
             "In a read-only data segment (`.rodata`), with static storage duration. Identical literals may share storage. Modifying one is undefined behaviour and usually crashes.")
    yield qa("What is the difference between .data and .bss?",
             "Both hold objects with static storage duration. `.data` holds those with a non-zero initialiser — their initial bytes are stored in the executable. `.bss` holds zero-initialised ones; the file records only the total size and the loader zero-fills it, keeping executables small.")
    yield qa("Why does the stack grow down and the heap grow up?",
             "Historically, so both could share one free region between them and each could grow until they met, without choosing a fixed split in advance. Modern systems use separate mappings with guard pages, but the convention remains on most architectures.")


@topic(G, "memory-bugs", "Common Memory Bugs", "bug")
def _():
    yield lead("C’s most expensive bugs are memory errors: they compile silently, often *seem* to work, and later crash or become security holes. Sanitizers (`-fsanitize=address,undefined`) and Valgrind find them.")
    yield table(
        ["Bug", "What it is", "Caught by"],
        ["Buffer overflow", "Read/write past the end (or before the start) of a buffer", "ASan, `-D_FORTIFY_SOURCE`"],
        ["Use after free", "Access through a pointer to freed memory", "ASan, Valgrind"],
        ["Double free", "`free` the same block twice", "ASan, glibc checks"],
        ["Memory leak", "Lose the last pointer to a block without freeing it", "LeakSanitizer, Valgrind"],
        ["Dangling stack pointer", "Use a pointer to a local after its function returned", "Compiler warning, ASan (use-after-return)"],
        ["Uninitialised read", "Read a variable / malloc’d memory before writing it", "`-Wuninitialized`, MSan, Valgrind"],
        ["Invalid free", "`free` a pointer not from `malloc` (stack array, `p + 1`)", "ASan"],
        ["NULL dereference", "Use a pointer that is `NULL` (e.g. unchecked `malloc`)", "Crash (SIGSEGV), UBSan"],
    )
    yield section("Heap buffer overflow", "arrow-bar-right")
    yield snippet("c", r'''
        #include <stdlib.h>
        #include <string.h>

        int main(void) {
            char *name = malloc(5);
            strcpy(name, "Alice");        /* needs 6 bytes: 5 letters + '\0' */
            free(name);
            return 0;
        }
    ''', fails=True)
    yield output('''
        ==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000955
        WRITE of size 6 at 0x602000000955 thread T0
        0x602000000955 is located 0 bytes after 5-byte region [0x602000000950,0x602000000955)
    ''', "AddressSanitizer (trimmed)")
    yield section("Use after free", "trash")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            int *p = malloc(sizeof *p);
            if (!p) return 1;
            *p = 42;
            free(p);
            printf("%d\n", *p);           /* the block now belongs to the allocator */
            return 0;
        }
    ''', fails=True)
    yield output('''
        ==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000950
        READ of size 4 at 0x602000000950 thread T0
        freed by thread T0 here: ... in free
        previously allocated by thread T0 here: ... in malloc
    ''', "AddressSanitizer (trimmed)")
    yield section("Double free", "copy-off")
    yield snippet("c", r'''
        #include <stdlib.h>

        int main(void) {
            char *buf = malloc(16);
            free(buf);
            free(buf);                    /* second free of the same block */
            return 0;
        }
    ''', fails=True)
    yield output("==ERROR: AddressSanitizer: attempting double-free on 0x602000000950 in thread T0", "AddressSanitizer (trimmed)")
    yield section("Invalid free", "circle-x")
    yield snippet("c", r'''
        #include <stdlib.h>

        int main(void) {
            int *a = malloc(4 * sizeof *a);
            if (!a) return 1;
            a++;                          /* lost the original pointer */
            free(a);                      /* not the address malloc returned */
            return 0;
        }
    ''', fails=True)
    yield section("Stack buffer overflow & use after scope", "stack")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int *p;
            {
                int inner = 7;
                p = &inner;
            }                             /* inner's lifetime ends here */
            printf("%d\n", *p);
            return 0;
        }
    ''', fails=True, caption="C — stack-use-after-scope caught by AddressSanitizer")
    yield section("Memory leak", "droplet")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        char *greet(const char *name) {
            char *s = malloc(strlen(name) + 7);
            if (s) { strcpy(s, "Hello "); strcat(s, name); }
            return s;                      /* the caller now owns s */
        }

        int main(void) {
            for (int i = 0; i < 3; i++) {
                char *msg = greet("Bob");
                if (msg) puts(msg);
                /* missing free(msg): each iteration leaks 10 bytes */
            }
            return 0;
        }
    ''', out='''
        Hello Bob
        Hello Bob
        Hello Bob
    ''', caption="C — a leak runs “fine”, which is exactly the danger")
    yield output('''
        ==ERROR: LeakSanitizer: detected memory leaks
        Direct leak of 30 byte(s) in 3 object(s) allocated from:
            #0 in malloc
            #1 in greet main.c:6
    ''', "LeakSanitizer on Linux (illustrative)")
    yield note("Leaks don’t crash — they grow memory use until a long-running server is killed. Run tests under `-fsanitize=address` on Linux (LeakSanitizer is on by default there) or `valgrind --leak-check=full`.")
    yield section("Uninitialised reads", "question-mark")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int total;
            for (int i = 0; i < 3; i++) total += i;    /* total starts as garbage */
            printf("%d\n", total);
            return 0;
        }
    ''', fails=True, caption="C — rejected: variable 'total' is uninitialized when used")
    yield section("Defensive habits", "shield-check")
    yield ul(
        "Initialise every variable at declaration; `= {0}` for arrays and structs.",
        "Check every `malloc` / `fopen` / `realloc` result.",
        "Set pointers to `NULL` after `free`; keep one clear owner per allocation.",
        "Pass buffer sizes everywhere; prefer `snprintf`, `fgets`, `strncat`/`memcpy` with explicit lengths.",
        "Build debug and test runs with `-g -fsanitize=address,undefined`; run Valgrind in CI.",
        "Use the `goto cleanup` pattern so every exit path frees what was allocated.",
    )
    yield qa("What is a dangling pointer and how do you avoid it?",
             "A pointer that still holds the address of an object whose lifetime has ended — freed heap memory, or a local of a function that returned. Avoid it by setting pointers to `NULL` after `free`, never returning addresses of locals, and having a clear ownership rule for every allocation.")
    yield qa("What is the difference between a memory leak and a dangling pointer?",
             "A leak is memory that is still allocated but no longer reachable (no pointer to it) — wasted but harmless to correctness. A dangling pointer is the opposite: a pointer still exists but the memory is gone — using it is undefined behaviour.")
    yield qa("How does AddressSanitizer work?",
             "The compiler instruments every memory access with a check against *shadow memory* that records which bytes are addressable. The runtime surrounds allocations with poisoned *redzones* and quarantines freed blocks, so overflows and use-after-free hit poisoned bytes and are reported immediately with stack traces. Cost: ~2× slowdown and more memory.")


@topic(G, "undefined-behaviour", "Undefined Behaviour Catalogue", "alert-octagon")
def _():
    yield lead("*Undefined behaviour* (UB) means the standard places **no requirements** on what happens. The program may crash, print garbage, work by luck — or be “optimised” in surprising ways because the compiler assumes UB never happens.")
    yield table(
        ["Kind", "Meaning", "Example"],
        ["**Undefined**", "Anything can happen; the whole program is invalid", "Signed overflow, out-of-bounds access, NULL dereference"],
        ["**Unspecified**", "One of several valid outcomes, not documented", "Order of evaluating function arguments"],
        ["**Implementation-defined**", "Documented choice of the compiler/platform", "`sizeof(int)`, signedness of `char`, right shift of negatives"],
        ["**Locale-specific**", "Depends on the current locale", "`isalpha` for non-ASCII bytes"],
    )
    yield section("The catalogue", "list")
    yield table(
        ["Undefined behaviour", "Example"],
        ["Signed integer overflow", "`INT_MAX + 1`"],
        ["Division or modulo by zero; `INT_MIN / -1`", "`x / 0`"],
        ["Shift by negative or ≥ width; left-shift of negative", "`1 << 32`, `-1 << 1`"],
        ["Array access out of bounds (even reading)", "`a[5]` for `int a[5]`"],
        ["Pointer arithmetic beyond one-past-the-end", "`p + n + 1`"],
        ["Dereferencing NULL, dangling or misaligned pointers", "`*(int *)NULL`"],
        ["Reading an uninitialised automatic variable", "`int x; printf(\"%d\", x);`"],
        ["Modifying a variable twice between sequence points", "`i = i++;`"],
        ["Modifying a string literal or a `const` object", "`char *s = \"hi\"; s[0] = 'H';`"],
        ["Strict-aliasing violation", "Reading a `float` through an `int *`"],
        ["Use after free, double free", "see Memory Bugs"],
        ["Falling off a non-void function whose value is used", "missing `return`"],
        ["Mismatched `printf` format and argument", "`printf(\"%d\", 3.0)`"],
        ["Converting an out-of-range float to an integer", "`(int)1e20`"],
        ["Data race between threads", "two threads write one variable without sync"],
    )
    yield section("Signed overflow", "arrow-up-right")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <limits.h>

        int main(void) {
            int x = INT_MAX;
            x = x + 1;                      /* UB — not guaranteed to wrap to INT_MIN */
            printf("%d\n", x);
            return 0;
        }
    ''', fails=True)
    yield output("main.c:6:11: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'", "UBSan")
    yield p("Because overflow “cannot happen”, an optimiser may turn `if (x + 1 > x)` into `if (1)` and `for (int i = 0; i <= n; i++)` into a loop that assumes `n < INT_MAX`. Check *before* the operation:")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <limits.h>
        #include <stdbool.h>

        bool safe_add(int a, int b, int *out) {
            if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b)) return false;
            *out = a + b;
            return true;
        }

        int main(void) {
            int r;
            printf("%d\n", safe_add(INT_MAX, 1, &r));
            if (safe_add(40, 2, &r)) printf("%d\n", r);
            printf("%d\n", __builtin_add_overflow(INT_MAX, 1, &r));   /* GCC/Clang builtin (C23: ckd_add) */
            return 0;
        }
    ''', out='''
        0
        42
        1
    ''')
    yield section("Division by zero", "divide")
    yield snippet("c", r'''
        #include <stdio.h>

        int divide(int a, int b) { return a / b; }

        int main(void) {
            printf("%d\n", divide(10, 0));
            return 0;
        }
    ''', fails=True)
    yield output("main.c:3:37: runtime error: division by zero", "UBSan")
    yield section("Strict aliasing & type punning", "arrows-exchange")
    yield p("The compiler assumes pointers to different types don’t point to the same memory (except `char *`). To reinterpret bytes, use `memcpy` — it compiles to a single move:")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>
        #include <stdint.h>

        int main(void) {
            float f = 1.0f;
            uint32_t bits;
            memcpy(&bits, &f, sizeof bits);           /* well-defined type punning */
            printf("0x%08X\n", (unsigned)bits);       /* IEEE 754: sign 0, exponent 127, mantissa 0 */
            return 0;
        }
    ''', out="0x3F800000")
    yield section("Living with UB", "shield")
    yield ul(
        "Compile with `-Wall -Wextra` and fix every warning.",
        "Test with `-fsanitize=undefined,address` (and `thread` for concurrency).",
        "Use unsigned types for bit manipulation and wrap-around arithmetic.",
        "Validate inputs *before* arithmetic, indexing and shifting.",
        "`-fwrapv` makes signed overflow wrap (GCC/Clang) — a band-aid, not a fix.",
    )
    yield qa("What is undefined behaviour and why does C have it?",
             "Behaviour for which the standard imposes no requirements. It exists so C can map directly onto very different hardware and so compilers can optimise aggressively without inserting checks (bounds, overflow, null) — the programmer promises these situations never occur.")
    yield qa("Why can undefined behaviour 'time travel'?",
             "Because a program that executes UB has no defined meaning at all, the optimiser may assume the UB path is never taken and reason backwards — e.g. dereferencing `p` before a `if (p == NULL)` check lets the compiler delete the check, since `p` “must” be non-null.")
    yield qa("Is i = i++ undefined?",
             "Yes (in C). `i` is modified twice without an intervening sequence point — once by the assignment and once by the post-increment. C11 describes this as two *unsequenced* side effects on the same object, which is undefined.")
