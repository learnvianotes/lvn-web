from kit import *

G = "Types, Variables & Operators"


@topic(G, "data-types", "Data Types & Sizes", "box")
def _():
    yield lead("C has a handful of built-in arithmetic types whose sizes are *implementation-defined* — the standard only guarantees minimum ranges. Always measure with `sizeof`.")
    yield section("The basic types", "category")
    yield table(
        ["Type", "Guaranteed minimum", "Typical size (64-bit Linux/macOS)", "Format"],
        ["`char`", "8 bits", "1 byte", "`%c` / `%d`"],
        ["`short`", "16 bits", "2 bytes", "`%hd`"],
        ["`int`", "16 bits", "4 bytes", "`%d`"],
        ["`long`", "32 bits", "8 bytes (4 on 64-bit Windows)", "`%ld`"],
        ["`long long`", "64 bits", "8 bytes", "`%lld`"],
        ["`float`", "~6 decimal digits", "4 bytes (IEEE 754 single)", "`%f`"],
        ["`double`", "~10 digits (15 in practice)", "8 bytes (IEEE 754 double)", "`%f` / `%lf`"],
        ["`long double`", "≥ `double`", "16 bytes x86-64 Linux, **8** on Apple arm64", "`%Lf`"],
        ["`_Bool` / `bool`", "holds 0 or 1", "1 byte", "`%d`"],
        ["`void`", "no value", "—", "—"],
    )
    yield note("Size ordering is guaranteed: `sizeof(char) == 1 ≤ sizeof(short) ≤ sizeof(int) ≤ sizeof(long) ≤ sizeof(long long)`. A “byte” in C is `CHAR_BIT` bits — 8 on every mainstream platform.")
    yield section("Measure with sizeof", "ruler")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdbool.h>

        int main(void) {
            printf("char        %zu\n", sizeof(char));
            printf("short       %zu\n", sizeof(short));
            printf("int         %zu\n", sizeof(int));
            printf("long        %zu\n", sizeof(long));
            printf("long long   %zu\n", sizeof(long long));
            printf("float       %zu\n", sizeof(float));
            printf("double      %zu\n", sizeof(double));
            printf("long double %zu\n", sizeof(long double));
            printf("bool        %zu\n", sizeof(bool));
            printf("pointer     %zu\n", sizeof(void *));
            return 0;
        }
    ''', out='''
        char        1
        short       2
        int         4
        long        8
        long long   8
        float       4
        double      8
        long double 8
        bool        1
        pointer     8
    ''', caption="C — output from a 64-bit Apple arm64 machine")
    yield p("`sizeof` is an *operator*, not a function: it is evaluated at compile time (except for VLAs), and its result has type `size_t` — print it with `%zu`. Parentheses are only needed around a type: `sizeof x` works for a variable.")
    yield section("signed and unsigned", "plus-minus")
    yield table(
        ["Type", "Range with 32-bit int"],
        ["`int` (= `signed int`)", "−2 147 483 648 … 2 147 483 647"],
        ["`unsigned int`", "0 … 4 294 967 295"],
        ["`signed char`", "−128 … 127"],
        ["`unsigned char`", "0 … 255 (the type for raw bytes)"],
        ["plain `char`", "**either** — signed on x86 and Apple arm64, unsigned on Linux ARM"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            unsigned int u = 0;
            u = u - 1;                    /* unsigned arithmetic wraps modulo 2^32 — well defined */
            printf("%u\n", u);

            unsigned char byte = 250;
            byte += 10;                   /* 260 mod 256 */
            printf("%d\n", byte);
            return 0;
        }
    ''', out='''
        4294967295
        4
    ''')
    yield warn("Unsigned overflow wraps around (defined). **Signed** overflow is *undefined behaviour* — the compiler may assume it never happens. See the UB topic.")
    yield section("Floating point", "decimal")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            double a = 0.1 + 0.2;
            printf("%.17f\n", a);
            printf("%s\n", a == 0.3 ? "equal" : "not equal");

            float f = 16777217.0f;        /* 2^24 + 1 cannot be stored in a float */
            printf("%.1f\n", f);
            printf("%f %f\n", 7 / 2.0, (double)(7 / 2));
            return 0;
        }
    ''', out='''
        0.30000000000000004
        not equal
        16777216.0
        3.500000 3.000000
    ''')
    yield note("Never compare floating-point values with `==`. Compare with a tolerance: `fabs(a - b) < 1e-9`. Use `double` by default — `float` only when memory matters (large arrays, GPUs).")
    yield section("Characters are small integers", "abc")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            char c = 'A';
            printf("%c %d %c %d\n", c, c, c + 2, '0');
            printf("digit value: %d\n", '7' - '0');
            printf("sizeof 'A' = %zu\n", sizeof 'A');   /* a char literal has type int in C */
            return 0;
        }
    ''', out='''
        A 65 C 48
        digit value: 7
        sizeof 'A' = 4
    ''')
    yield qa("What is the size of int in C?",
             "Implementation-defined; the standard only requires at least 16 bits. On virtually every modern desktop/server platform (ILP32, LP64, LLP64) it is 32 bits. That is why portable code uses `<stdint.h>` types such as `int32_t` when the exact width matters.")
    yield qa("Is char signed or unsigned?",
             "Implementation-defined. `char`, `signed char` and `unsigned char` are three distinct types. Use `unsigned char` for raw bytes and cast to `unsigned char` before passing a `char` to `<ctype.h>` functions.")
    yield qa("What does sizeof('A') return in C and in C++?",
             "In C a character constant has type `int`, so `sizeof('A')` is `sizeof(int)` (usually 4). In C++ it has type `char`, so the result is 1.")


@topic(G, "fixed-width-limits", "limits.h, stdint.h & Fixed-Width Types", "ruler-2")
def _():
    yield lead("`<limits.h>` tells you the range of the built-in types on *this* platform; `<stdint.h>` gives you types with an *exact* width when you need one.")
    yield section("limits.h and float.h", "arrows-vertical")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <limits.h>
        #include <float.h>

        int main(void) {
            printf("CHAR_BIT  = %d\n", CHAR_BIT);
            printf("SCHAR     = %d .. %d\n", SCHAR_MIN, SCHAR_MAX);
            printf("UCHAR_MAX = %d\n", UCHAR_MAX);
            printf("SHRT      = %d .. %d\n", SHRT_MIN, SHRT_MAX);
            printf("INT       = %d .. %d\n", INT_MIN, INT_MAX);
            printf("UINT_MAX  = %u\n", UINT_MAX);
            printf("LLONG_MAX = %lld\n", LLONG_MAX);
            printf("DBL_MAX   = %g, DBL_EPSILON = %g\n", DBL_MAX, DBL_EPSILON);
            return 0;
        }
    ''', out='''
        CHAR_BIT  = 8
        SCHAR     = -128 .. 127
        UCHAR_MAX = 255
        SHRT      = -32768 .. 32767
        INT       = -2147483648 .. 2147483647
        UINT_MAX  = 4294967295
        LLONG_MAX = 9223372036854775807
        DBL_MAX   = 1.79769e+308, DBL_EPSILON = 2.22045e-16
    ''')
    yield section("stdint.h — exact, least and fast types", "numbers")
    yield table(
        ["Type", "Meaning"],
        ["`int8_t`, `int16_t`, `int32_t`, `int64_t`", "Exactly N bits, two’s complement (optional but universally available)"],
        ["`uint8_t` … `uint64_t`", "Unsigned exact-width"],
        ["`int_least16_t`", "Smallest type with at least 16 bits"],
        ["`int_fast32_t`", "Fastest type with at least 32 bits"],
        ["`intmax_t` / `uintmax_t`", "Widest integer type"],
        ["`intptr_t` / `uintptr_t`", "Integer that can hold a pointer value"],
        ["`size_t` (`<stddef.h>`)", "Unsigned result of `sizeof`; use for sizes and indexes"],
        ["`ptrdiff_t` (`<stddef.h>`)", "Signed difference of two pointers"],
    )
    yield section("Printing them portably: inttypes.h", "printer")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdint.h>
        #include <inttypes.h>

        int main(void) {
            int64_t big = INT64_MAX;
            uint8_t small = UINT8_MAX;
            uint32_t mask = 0xDEADBEEF;
            printf("big   = %" PRId64 "\n", big);
            printf("small = %" PRIu8 "\n", small);
            printf("mask  = 0x%" PRIX32 "\n", mask);
            printf("sizes = %zu %zu %zu\n", sizeof(int8_t), sizeof(int32_t), sizeof(uint64_t));
            return 0;
        }
    ''', out='''
        big   = 9223372036854775807
        small = 255
        mask  = 0xDEADBEEF
        sizes = 1 4 8
    ''')
    yield note("`PRId64` is a string macro such as `\"lld\"` or `\"ld\"`; string-literal concatenation glues it into the format. This avoids guessing whether `int64_t` is `long` or `long long` on a given platform.")
    yield dodont("Use `uint8_t` for bytes, `uint32_t` for bit masks and file formats, `size_t` for sizes and array indexes.",
                 "Assume `long` is 64 bits — it is 32 bits on 64-bit Windows.")
    yield qa("When should you use int vs int32_t?",
             "Use `int` for ordinary counters and arithmetic where the natural word size is fine. Use exact-width types when layout matters: binary file formats, network protocols, hardware registers, hashing and bit manipulation.")
    yield qa("What is size_t and why is it unsigned?",
             "`size_t` is the unsigned integer type returned by `sizeof` and taken by `malloc`, `strlen`, `memcpy`… It is large enough to hold the size of any object. It is unsigned because sizes are never negative — beware loops like `for (size_t i = n - 1; i >= 0; i--)`, which never end.")


@topic(G, "variables-constants", "Variables, Constants & Literals", "variable")
def _():
    yield lead("A variable is a named, typed region of memory. C gives you three kinds of constants: literals, `const` objects, and `#define` / `enum` names.")
    yield section("Declaring and initialising", "pencil")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a = 10, b = 20;        /* several on one line */
            double ratio = a / (double)b;
            char grade = 'A';
            int uninit;                /* indeterminate value — do not read it! */
            uninit = 5;                /* assign before use */
            printf("%d %d %.2f %c %d\n", a, b, ratio, grade, uninit);
            return 0;
        }
    ''', out="10 20 0.50 A 5")
    yield warn("Local (automatic) variables are **not** initialised — their initial value is garbage and reading it is undefined behaviour. Globals and `static` variables are zero-initialised.")
    yield section("Identifier rules", "id")
    yield ul(
        "Letters, digits and `_`; cannot start with a digit; case-sensitive (`count` ≠ `Count`).",
        "Cannot be a keyword (`int`, `return`, `static`, `sizeof`…).",
        "Names starting with `_` + uppercase letter or `__` are *reserved* for the implementation — don’t use them.",
        "Convention: `snake_case` for variables and functions, `UPPER_CASE` for macros and constants.",
    )
    yield section("Literals", "quote")
    yield table(
        ["Literal", "Type", "Example"],
        ["Decimal / octal / hex integer", "`int` (or larger if needed)", "`42`, `052`, `0x2A`"],
        ["Suffixes `u`, `l`, `ll`", "`unsigned`, `long`, `long long`", "`42u`, `42L`, `42ULL`"],
        ["Floating", "`double` by default", "`3.14`, `1e-3`, `2.5f` (float), `2.5L` (long double)"],
        ["Character", "`int` (!)", "`'A'`, `'\\n'`, `'\\0'`, `'\\x41'`"],
        ["String", "`char[N]` (array incl. NUL)", "`\"hi\"` has 3 bytes"],
        ["Compound (C99)", "unnamed object", "`(int[]){1, 2, 3}`"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d %d\n", 42, 052, 0x2A);         /* same number, three bases */
            printf("%zu %zu %zu\n", sizeof 42, sizeof 42L, sizeof 42.0f);
            printf("[%s] has %zu bytes\n", "hi", sizeof "hi");
            printf("tab[\t] quote[\"] backslash[\\] newline next:\n.\n");
            return 0;
        }
    ''', out='''
        42 42 42
        4 8 4
        [hi] has 3 bytes
        tab[	] quote["] backslash[\\] newline next:
        .
    ''')
    yield warn("A leading `0` makes an integer literal **octal**: `010` is 8, and `09` is a compile error.")
    yield section("Three ways to name a constant", "lock")
    yield table(
        ["Form", "Example", "Typed?", "Scope", "Notes"],
        ["`#define`", "`#define MAX 100`", "No", "From definition to end of file", "Text substitution by the preprocessor; no address"],
        ["`const`", "`const int max = 100;`", "Yes", "Block / file", "A read-only *variable*; not a constant expression in C (can’t size a global array)"],
        ["`enum`", "`enum { MAX = 100 };`", "`int`", "Block / file", "A true integer constant expression, visible to the debugger"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        #define PI 3.14159
        enum { SIZE = 4 };

        int main(void) {
            const int answer = 42;
            int arr[SIZE] = {1, 2, 3, 4};           /* enum constant can size an array */
            printf("%.2f %d %d\n", PI * 2, answer, arr[SIZE - 1]);
            return 0;
        }
    ''', out="6.28 42 4")
    yield snippet("c", r'''
        int main(void) {
            const int limit = 10;
            limit = 20;              /* error: cannot assign to a const-qualified variable */
            return limit;
        }
    ''', fails=True, caption="C — modifying a const is a compile error")
    yield qa("What is the difference between #define and const?",
             "`#define` is a preprocessor text replacement: no type, no scope, no storage, invisible to the debugger, and prone to precedence surprises. `const` creates a typed, scoped, read-only object with an address. In C (unlike C++) a `const int` is not a constant expression, so `enum` or `#define` is still used for array sizes and `case` labels.")
    yield qa("What value does an uninitialised variable have?",
             "Objects with *static* storage duration (globals, `static` locals) are zero-initialised. *Automatic* locals have an indeterminate value; reading it is undefined behaviour, which is why compilers warn (`-Wuninitialized`).")


@topic(G, "storage-classes", "Storage Classes: auto, static, extern, register", "database")
def _():
    yield lead("A storage-class specifier decides *where* a variable lives, *how long* it lives (lifetime) and *who can see it* (linkage).")
    yield table(
        ["Specifier", "Lifetime", "Default value", "Scope / linkage", "Typical use"],
        ["`auto` (default for locals)", "Until the block ends", "Garbage", "Block, no linkage", "Ordinary local variables"],
        ["`static` (local)", "Whole program", "0", "Block, no linkage", "Remember a value between calls"],
        ["`static` (global / function)", "Whole program", "0", "File only (**internal** linkage)", "Hide helpers from other files"],
        ["`extern`", "Whole program", "0 (where defined)", "All files (**external** linkage)", "Share a global across files"],
        ["`register`", "Until the block ends", "Garbage", "Block", "Historic hint; cannot take its address"],
        ["`_Thread_local` (C11)", "Per thread", "0", "As above", "One copy per thread"],
    )
    yield section("static local: state that survives calls", "repeat")
    yield snippet("c", r'''
        #include <stdio.h>

        int next_id(void) {
            static int id = 0;      /* initialised once, before the program starts */
            int calls = 0;          /* automatic: recreated on every call */
            calls++;
            id++;
            printf("id=%d calls=%d\n", id, calls);
            return id;
        }

        int main(void) {
            next_id();
            next_id();
            next_id();
            return 0;
        }
    ''', out='''
        id=1 calls=1
        id=2 calls=1
        id=3 calls=1
    ''')
    yield section("static at file level: private to the file", "lock")
    yield snippet("c", r'''
        /* counter.c */
        static int count = 0;                 /* invisible to other .c files */

        static void log_change(void) { }      /* helper, internal linkage */

        void counter_increment(void) {
            count++;
            log_change();
        }

        int counter_value(void) { return count; }
    ''', caption="C — counter.c (compile-checked)")
    yield section("extern: one definition, many declarations", "share")
    yield snippet("c", r'''
        #include <stdio.h>

        extern int shared;             /* declaration: "defined somewhere else" */
        void bump(void);

        int main(void) {
            bump();
            bump();
            printf("shared = %d\n", shared);
            return 0;
        }

        int shared = 100;              /* the one definition (normally in another .c file) */

        void bump(void) { shared += 5; }
    ''', out="shared = 110")
    yield note("Put `extern int shared;` in a header, and `int shared = 0;` in exactly **one** `.c` file. Functions are `extern` by default, so `extern` on a prototype is redundant.")
    yield section("register", "cpu")
    yield snippet("c", r'''
        int main(void) {
            register int i = 0;
            int *p = &i;            /* error: address of register variable requested */
            return *p;
        }
    ''', fails=True)
    yield p("Modern compilers ignore `register` for optimisation — they allocate registers far better than humans. Its only remaining effect is forbidding `&`. (`auto` in C means “automatic storage”; C23 repurposes it for type inference like C++.)")
    yield qa("What are the differences between a static local variable and a global variable?",
             "Both have static storage duration (they live for the whole program and are zero-initialised). A `static` local is only *visible* inside its function (block scope), whereas a global is visible to the whole file and — unless declared `static` — to other files via `extern`.")
    yield qa("What does static mean for a function?",
             "It gives the function *internal linkage*: it can only be called from the translation unit that defines it. This is C’s way of making a function private and avoids name clashes between files.")
    yield qa("Can a static variable be initialised with a non-constant expression?",
             "No, not in C. Objects with static storage duration must be initialised with constant expressions because the initial values are baked into the executable’s data segment before `main` runs. (C++ allows dynamic initialisation.)")


@topic(G, "operators", "Operators & Precedence", "math-symbols")
def _():
    yield lead("C’s operators are compact and powerful. Most bugs come from precedence surprises, integer division, and unsequenced side effects — use parentheses generously.")
    yield section("Arithmetic", "calculator")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d %d %d\n", 17 / 5, 17 % 5, -17 / 5, -17 % 5);   /* truncates toward 0 */
            printf("%.2f\n", 17 / 5.0);                                   /* one double → real division */
            int i = 5;
            int a = i++;      /* a = 5, then i = 6 */
            int b = ++i;      /* i = 7, then b = 7 */
            printf("a=%d b=%d i=%d\n", a, b, i);
            return 0;
        }
    ''', out='''
        3 2 -3 -2
        3.40
        a=5 b=7 i=7
    ''')
    yield note("Integer `/` truncates toward zero (since C99) and `%` takes the sign of the left operand, so `(a / b) * b + a % b == a` always holds.")
    yield section("Relational, logical and short-circuit", "git-compare")
    yield snippet("c", r'''
        #include <stdio.h>

        int calls = 0;
        int check(int v) { calls++; return v; }

        int main(void) {
            printf("%d %d %d\n", 3 > 2, 3 == 2, !5);      /* results are int 1 or 0 */
            if (check(0) && check(1)) { }                 /* right side skipped */
            if (check(1) || check(1)) { }                 /* right side skipped */
            printf("calls = %d\n", calls);
            return 0;
        }
    ''', out='''
        1 0 0
        calls = 2
    ''')
    yield section("Assignment, comma, ternary, sizeof", "equal")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int x = 10;
            x += 5; x *= 2; x -= 6; x /= 4; x %= 4;
            printf("x = %d\n", x);

            int a, b;
            a = b = 7;                          /* assignment is an expression, right-assoc */
            int max = (a > 3) ? a : 3;          /* conditional operator */
            int last = (a++, b++, a + b);       /* comma: evaluate left, yield right */
            printf("%d %d %d %d\n", a, b, max, last);
            return 0;
        }
    ''', out='''
        x = 2
        8 8 7 16
    ''')
    yield section("Precedence table (high → low)", "list-numbers")
    yield table(
        ["Level", "Operators", "Associativity"],
        ["1", "`()` `[]` `->` `.` postfix `++` `--`", "left → right"],
        ["2", "prefix `++` `--`, unary `+` `-` `!` `~`, cast `(type)`, `*` (deref), `&` (address), `sizeof`", "right → left"],
        ["3", "`*` `/` `%`", "left → right"],
        ["4", "`+` `-`", "left → right"],
        ["5", "`<<` `>>`", "left → right"],
        ["6", "`<` `<=` `>` `>=`", "left → right"],
        ["7", "`==` `!=`", "left → right"],
        ["8", "`&`", "left → right"],
        ["9", "`^`", "left → right"],
        ["10", "`|`", "left → right"],
        ["11", "`&&`", "left → right"],
        ["12", "`||`", "left → right"],
        ["13", "`?:`", "right → left"],
        ["14", "`=` `+=` `-=` `*=` `/=` `%=` `<<=` `>>=` `&=` `^=` `|=`", "right → left"],
        ["15", "`,`", "left → right"],
    )
    yield section("Classic precedence traps", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int flags = 6;
            /* == binds tighter than &:  flags & (4 == 4)  →  6 & 1  →  0 */
            printf("%d\n", flags & 4 == 4 ? 1 : 0);
            printf("%d\n", (flags & 4) == 4 ? 1 : 0);

            /* + binds tighter than << :  1 << (2 + 1) */
            printf("%d\n", 1 << 2 + 1);

            int arr[] = {10, 20, 30};
            int *p = arr;
            int v = *p++;      /* *(p++): read 10, then advance p */
            printf("%d %d\n", v, *p);
            return 0;
        }
    ''', out='''
        0
        1
        8
        10 20
    ''', flags=("-Wno-parentheses",), caption="C — compiled with -Wno-parentheses to let the traps through")
    yield warn("`i = i++ + ++i;` or `printf(\"%d %d\", i, i++)` modify and read the same variable without a *sequence point* — that is **undefined behaviour**, not “compiler-dependent output”. Clang rejects it under `-Werror` (`-Wunsequenced`).")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int i = 1;
            i = i++ + ++i;
            printf("%d\n", i);
            return 0;
        }
    ''', fails=True, caption="C — unsequenced modification (rejected)")
    yield qa("What is the difference between i++ and ++i?",
             "Both add 1 to `i`. The *value of the expression* differs: `i++` yields the old value, `++i` yields the new value. As a standalone statement (`i++;`) they are identical and compile to the same code.")
    yield qa("What does short-circuit evaluation mean?",
             "`&&` stops as soon as the left side is false, `||` stops as soon as the left side is true, and there is a sequence point after the left operand. That makes guards like `if (p != NULL && p->count > 0)` safe.")


@topic(G, "conversions", "Integer Promotion & Type Conversions", "transform")
def _():
    yield lead("Before most arithmetic, C silently converts operands: small integers are *promoted* to `int`, and mixed types are brought to a *common type*. Signed/unsigned mixing is the classic source of bugs.")
    yield section("Integer promotion", "arrow-big-up")
    yield p("Any `char`, `short` or bit-field (signed or unsigned) used in an expression is first converted to `int` (or `unsigned int` if `int` can’t hold all its values).")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            unsigned char a = 200, b = 100;
            int sum = a + b;                 /* promoted to int: 300, no wrap */
            unsigned char stored = a + b;    /* converted back: 300 mod 256 */
            printf("%d %d\n", sum, stored);

            char c = 'x';
            printf("%zu %zu\n", sizeof c, sizeof(c + 0));   /* char vs int */

            unsigned char ones = 0xFF;
            printf("%d\n", ~ones);           /* ~ applied to int 255 → -256, not 0 */
            return 0;
        }
    ''', out='''
        300 44
        1 4
        -256
    ''')
    yield section("The usual arithmetic conversions", "stairs-up")
    yield steps(
        ("Any floating operand?", "Convert the other to the widest floating type involved (`long double` > `double` > `float`)."),
        ("Otherwise promote", "Apply integer promotion to both operands."),
        ("Same signedness", "Convert to the higher-rank type (`int` < `long` < `long long`)."),
        ("Mixed signedness", "If the unsigned type has rank ≥ the signed one, the **signed operand becomes unsigned**. Otherwise, if the signed type can represent every unsigned value, convert to the signed type; else to its unsigned counterpart."),
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int neg = -1;
            unsigned int one = 1;
            /* -1 is converted to unsigned: 4294967295 > 1 */
            if ((unsigned)neg > one) printf("-1 > 1u as unsigned!\n");
            printf("%u\n", (unsigned)neg);

            long long big = -1;
            printf("%d\n", big < one);     /* long long can hold every unsigned int: stays signed */
            return 0;
        }
    ''', out='''
        -1 > 1u as unsigned!
        4294967295
        1
    ''')
    yield p("Clang warns about the implicit version of this comparison (`-Wsign-compare`, part of `-Wextra`) — one more reason to keep warnings on:")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            int i = -1;
            if (i < strlen("abc"))       /* int vs size_t: i becomes huge */
                printf("smaller\n");
            return 0;
        }
    ''', fails=True, caption="C — signed/unsigned comparison (rejected by -Wextra -Werror)")
    yield section("Explicit casts and narrowing", "arrows-exchange")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            double d = 3.99;
            int truncated = (int)d;          /* toward zero, not rounded */
            int negative = (int)-3.99;
            printf("%d %d\n", truncated, negative);

            int total = 7, count = 2;
            printf("%d %.1f\n", total / count, (double)total / count);

            int big = 300;
            unsigned char small = (unsigned char)big;   /* modulo 256 */
            signed char sc = (signed char)200;          /* implementation-defined */
            printf("%d %d\n", small, sc);
            return 0;
        }
    ''', out='''
        3 -3
        3 3.5
        44 -56
    ''')
    yield table(
        ["Conversion", "Result"],
        ["Any integer → unsigned type", "Well defined: value modulo 2ᴺ"],
        ["Out-of-range integer → signed type", "Implementation-defined (wraps on all real compilers; C23 mandates two’s complement)"],
        ["Floating → integer", "Truncates toward zero; **UB** if the value doesn’t fit"],
        ["Integer → floating", "May lose precision for large values"],
        ["`double` → `float`", "Rounded; UB/inf if out of range"],
    )
    yield qa("Why does (unsigned char)255 + 1 give 256 and not 0?",
             "Because of integer promotion: the `unsigned char` operand is promoted to `int` before the addition, so the arithmetic is done in `int`. The result only wraps to 0 if it is stored back into an `unsigned char`.")
    yield qa("What is the result of -1 < 0u?",
             "`0` (false). `-1` is converted to `unsigned int` (becoming `UINT_MAX`) because both operands have the same rank and one is unsigned. This is why comparing an `int` with `strlen()` or `sizeof` can go wrong.")


@topic(G, "bitwise", "Bitwise Operators & Bit Tricks", "binary")
def _():
    yield lead("C lets you manipulate individual bits — the basis of flags, masks, hardware registers, compression, hashing and many interview puzzles.")
    yield table(
        ["Operator", "Name", "Example (a = 12 = `1100`, b = 10 = `1010`)", "Result"],
        ["`a & b`", "AND", "`1100 & 1010`", "`1000` = 8"],
        ["`a | b`", "OR", "`1100 | 1010`", "`1110` = 14"],
        ["`a ^ b`", "XOR", "`1100 ^ 1010`", "`0110` = 6"],
        ["`~a`", "NOT (one’s complement)", "`~12`", "−13 (for `int`)"],
        ["`a << n`", "left shift", "`12 << 1`", "24 (× 2ⁿ)"],
        ["`a >> n`", "right shift", "`12 >> 2`", "3 (÷ 2ⁿ for non-negative)"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        void print_bits(unsigned x, int width) {
            for (int i = width - 1; i >= 0; i--)
                putchar((x >> i) & 1u ? '1' : '0');
            putchar('\n');
        }

        int main(void) {
            unsigned a = 12, b = 10;
            printf("%u %u %u %u %u\n", a & b, a | b, a ^ b, a << 1, a >> 2);
            print_bits(a, 8);
            print_bits(~a & 0xFFu, 8);
            return 0;
        }
    ''', out='''
        8 14 6 24 3
        00001100
        11110011
    ''')
    yield section("Set, clear, toggle, test", "toggle-left")
    yield snippet("c", r'''
        #include <stdio.h>

        #define BIT(n) (1u << (n))

        int main(void) {
            unsigned flags = 0;
            flags |= BIT(3);              /* set bit 3     */
            flags |= BIT(0);              /* set bit 0     */
            printf("%u\n", flags);        /* 1001 = 9      */
            flags &= ~BIT(0);             /* clear bit 0   */
            flags ^= BIT(1);              /* toggle bit 1  */
            printf("%u\n", flags);        /* 1010 = 10     */
            printf("bit 3 is %s\n", (flags & BIT(3)) ? "set" : "clear");
            return 0;
        }
    ''', out='''
        9
        10
        bit 3 is set
    ''')
    yield section("Flags as a set of options", "flag")
    yield snippet("c", r'''
        #include <stdio.h>

        enum Perm { READ = 1 << 0, WRITE = 1 << 1, EXEC = 1 << 2 };

        int main(void) {
            unsigned perms = READ | WRITE;
            printf("can write? %s\n", (perms & WRITE) ? "yes" : "no");
            printf("can exec?  %s\n", (perms & EXEC) ? "yes" : "no");
            perms |= EXEC;
            printf("rwx = %u\n", perms);
            return 0;
        }
    ''', out='''
        can write? yes
        can exec?  no
        rwx = 7
    ''')
    yield section("Classic bit tricks", "wand")
    yield snippet("c", r'''
        #include <stdio.h>

        int is_power_of_two(unsigned x) { return x && !(x & (x - 1)); }

        int popcount(unsigned x) {          /* Kernighan: clear lowest set bit each step */
            int n = 0;
            while (x) { x &= x - 1; n++; }
            return n;
        }

        int main(void) {
            printf("%d %d %d\n", is_power_of_two(64), is_power_of_two(96), is_power_of_two(0));
            printf("popcount(255) = %d, popcount(96) = %d\n", popcount(255), popcount(96));
            printf("lowest set bit of 96 = %u\n", 96u & -96u);
            printf("odd? %d %d\n", 7 & 1, 10 & 1);

            int x = 5, y = 9;
            x ^= y; y ^= x; x ^= y;         /* XOR swap (a curiosity; use a temp in real code) */
            printf("x=%d y=%d\n", x, y);

            int nums[] = {4, 1, 2, 1, 2};   /* every number twice except one */
            int single = 0;
            for (int i = 0; i < 5; i++) single ^= nums[i];
            printf("single = %d\n", single);
            printf("builtin popcount = %d\n", __builtin_popcount(255u));
            return 0;
        }
    ''', out='''
        1 0 0
        popcount(255) = 8, popcount(96) = 2
        lowest set bit of 96 = 32
        odd? 1 0
        x=9 y=5
        single = 4
        builtin popcount = 8
    ''')
    yield table(
        ["Trick", "Expression"],
        ["Is power of two", "`x && !(x & (x - 1))`"],
        ["Clear lowest set bit", "`x & (x - 1)`"],
        ["Isolate lowest set bit", "`x & -x` (unsigned)"],
        ["Multiply / divide by 2ⁿ", "`x << n`, `x >> n` (unsigned)"],
        ["Check odd", "`x & 1`"],
        ["Swap without temp", "`a ^= b; b ^= a; a ^= b;` (breaks if `a` and `b` alias!)"],
        ["Round up to multiple of 8", "`(x + 7) & ~7u`"],
    )
    yield section("Shift pitfalls", "alert-triangle")
    yield ul(
        "Shifting by ≥ the width of the type (`1u << 32` for a 32-bit `unsigned`) is **undefined**.",
        "Left-shifting a negative value, or shifting a `1` into the sign bit of a signed `int` (`1 << 31`), is **undefined** — use unsigned types for bit work.",
        "Right-shifting a negative signed value is implementation-defined (usually arithmetic, copying the sign bit).",
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int shift = 32;
            unsigned x = 1u << shift;     /* UB: shift >= width of unsigned int */
            printf("%u\n", x);
            return 0;
        }
    ''', fails=True, caption="C — oversized shift (caught by UBSan)")
    yield output("main.c:5:21: runtime error: shift exponent 32 is too large for 32-bit type 'unsigned int'", "UBSan")
    yield qa("How do you check whether the k-th bit of n is set?",
             "`(n >> k) & 1` or `n & (1u << k)` (non-zero means set). Use unsigned operands so shifts into the top bit are well defined.")
    yield qa("How do you find the element that appears once when all others appear twice?",
             "XOR all elements: `x ^ x == 0` and `x ^ 0 == x`, and XOR is commutative, so pairs cancel and only the single element remains. O(n) time, O(1) space.")
