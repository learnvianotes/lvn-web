from kit import *

G = "Control Flow & Functions"


@topic(G, "conditionals", "Conditionals: if, else & ?:", "git-branch")
def _():
    yield lead("C has no boolean type in conditions — any scalar value is tested against zero: `0` (or `NULL`) is false, everything else is true.")
    yield section("if / else if / else", "arrows-split")
    yield snippet("c", r'''
        #include <stdio.h>

        const char *grade(int score) {
            if (score >= 90) {
                return "A";
            } else if (score >= 75) {
                return "B";
            } else if (score >= 50) {
                return "C";
            } else {
                return "F";
            }
        }

        int main(void) {
            int scores[] = {95, 80, 50, 12};
            for (int i = 0; i < 4; i++)
                printf("%d -> %s\n", scores[i], grade(scores[i]));
            return 0;
        }
    ''', out='''
        95 -> A
        80 -> B
        50 -> C
        12 -> F
    ''')
    yield section("Truth in C", "toggle-left")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdbool.h>

        int main(void) {
            int n = -3;
            char *p = NULL;
            if (n) printf("-3 is true\n");
            if (!p) printf("NULL is false\n");
            if (0.0) printf("never\n"); else printf("0.0 is false\n");

            bool done = 5;                  /* any non-zero converts to true (1) */
            printf("done = %d\n", done);
            return 0;
        }
    ''', out='''
        -3 is true
        NULL is false
        0.0 is false
        done = 1
    ''')
    yield section("The conditional (ternary) operator", "question-mark")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a = 7, b = 12;
            int max = a > b ? a : b;
            printf("max = %d, %s\n", max, a % 2 ? "a is odd" : "a is even");
            return 0;
        }
    ''', out="max = 12, a is odd")
    yield section("Pitfalls", "alert-triangle")
    yield table(
        ["Bug", "What happens", "Prevention"],
        ["`if (x = 5)`", "Assigns 5, always true", "`-Wall` warns (`-Wparentheses`); some write `if (5 == x)`"],
        ["`if (x > 0);` `{ … }`", "Empty statement — block always runs", "Brace style, `-Wempty-body`"],
        ["Dangling `else`", "`else` binds to the **nearest** `if`", "Always use braces"],
        ["`if (0.1 + 0.2 == 0.3)`", "False — floating rounding", "Compare with a tolerance"],
        ["`if (a < b < c)`", "Parsed as `(a < b) < c` → compares 0/1 with `c`", "`a < b && b < c`"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int x = 0;
            if (x = 5)                 /* assignment used as condition */
                printf("always\n");
            return 0;
        }
    ''', fails=True, caption="C — rejected: -Wparentheses under -Werror")
    yield qa("What is the dangling else problem?",
             "In `if (a) if (b) s1; else s2;` the `else` belongs to the inner `if (b)`, regardless of indentation. C resolves the ambiguity by binding `else` to the nearest unmatched `if`. Braces make the intent explicit.")


@topic(G, "switch", "The switch Statement", "switch-horizontal")
def _():
    yield lead("`switch` jumps to the `case` label matching an integer value. Execution *falls through* into the next case unless you `break`.")
    yield snippet("c", r'''
        #include <stdio.h>

        const char *day_type(int day) {
            switch (day) {
                case 0:
                case 6:
                    return "weekend";      /* several labels share one body */
                case 1: case 2: case 3: case 4: case 5:
                    return "weekday";
                default:
                    return "invalid";
            }
        }

        int main(void) {
            printf("%s %s %s\n", day_type(0), day_type(3), day_type(9));
            return 0;
        }
    ''', out="weekend weekday invalid")
    yield section("Fall-through", "arrow-down")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int level = 2;
            switch (level) {
                case 3: printf("gold ");
                        /* fall through */
                case 2: printf("silver ");
                        /* fall through */
                case 1: printf("bronze ");
                        break;
                default: printf("none");
            }
            printf("\n");
            return 0;
        }
    ''', out="silver bronze")
    yield note("Mark intentional fall-through with a comment (or C23 `[[fallthrough]];`). `-Wimplicit-fallthrough` flags the unmarked ones.")
    yield section("Rules", "list-check")
    yield ul(
        "The controlling expression must have an **integer** type (`int`, `char`, `enum`…) — not a string or `double`.",
        "`case` labels must be **integer constant expressions** and unique. `const int` variables are not allowed in C; use `enum` or `#define`.",
        "`default` is optional and may appear anywhere; it runs when no case matches.",
        "Declaring a variable right after a `case` label needs a block: `case 1: { int t = 0; … break; }`.",
        "For strings, use `if`/`else if` with `strcmp`.",
    )
    yield snippet("c", r'''
        #include <stdio.h>

        enum Color { RED, GREEN, BLUE };

        int main(void) {
            enum Color c = GREEN;
            switch (c) {
                case RED:   printf("stop\n");  break;
                case GREEN: printf("go\n");    break;
                case BLUE:  printf("calm\n");  break;
            }
            return 0;
        }
    ''', out="go")
    yield note("Switching on an `enum` without a `default` lets the compiler warn (`-Wswitch`) when you add a new enumerator and forget to handle it.", "Tip")
    yield qa("switch vs if-else chain — which is faster?",
             "For dense integer cases the compiler can turn a `switch` into a *jump table* (O(1) dispatch) or a binary search; an `if`-chain is tested top to bottom. Modern optimisers often transform both, so choose for readability: `switch` for many discrete values of one integer, `if` for ranges and complex conditions.")


@topic(G, "loops", "Loops: for, while, do-while", "repeat")
def _():
    yield lead("Three loop forms, plus `break`, `continue` and (rarely) `goto`. Pick `for` when you count, `while` when you wait for a condition, `do-while` when the body must run at least once.")
    yield section("The three loops", "refresh")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            for (int i = 0; i < 5; i++)          /* init; condition; step */
                printf("%d ", i);
            printf("\n");

            int n = 1234, digits = 0;
            while (n != 0) {                     /* test before each iteration */
                n /= 10;
                digits++;
            }
            printf("digits = %d\n", digits);

            int k = 100;
            do {                                 /* body runs at least once */
                printf("k = %d\n", k);
            } while (k < 10);
            return 0;
        }
    ''', out='''
        0 1 2 3 4
        digits = 4
        k = 100
    ''')
    yield section("break and continue", "player-skip-forward")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            for (int i = 1; i <= 10; i++) {
                if (i % 2 == 0) continue;   /* skip even numbers */
                if (i > 7) break;           /* leave the loop entirely */
                printf("%d ", i);
            }
            printf("\n");
            return 0;
        }
    ''', out="1 3 5 7")
    yield section("Nested loops and patterns", "grid-dots")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int n = 4;
            for (int row = 1; row <= n; row++) {
                for (int s = 0; s < n - row; s++) putchar('.');
                for (int star = 0; star < 2 * row - 1; star++) putchar('*');
                putchar('\n');
            }
            return 0;
        }
    ''', out='''
        ...*
        ..***
        .*****
        *******
    ''')
    yield section("Breaking out of nested loops: goto", "arrow-back-up")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int grid[3][3] = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
            int target = 5;
            for (int r = 0; r < 3; r++)
                for (int c = 0; c < 3; c++)
                    if (grid[r][c] == target) {
                        printf("found at (%d,%d)\n", r, c);
                        goto done;              /* one of the few acceptable uses */
                    }
            printf("not found\n");
        done:
            return 0;
        }
    ''', out="found at (1,1)")
    yield note("`goto` is legitimate in C for two idioms: leaving deeply nested loops and the *single cleanup exit* pattern (`goto cleanup;` to free resources in reverse order — used throughout the Linux kernel). Never jump backwards to build loops.", "goto")
    yield section("Loop idioms", "list")
    yield table(
        ["Idiom", "Code"],
        ["Infinite loop", "`for (;;) { … }` or `while (1) { … }`"],
        ["Iterate an array", "`for (size_t i = 0; i < n; i++)`"],
        ["Count down with `size_t`", "`for (size_t i = n; i-- > 0; )` (avoids the unsigned wrap trap)"],
        ["Read until EOF", "`while ((c = getchar()) != EOF)`"],
        ["Two indexes", "`for (int i = 0, j = n - 1; i < j; i++, j--)`"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {1, 2, 3, 4, 5};
            size_t n = sizeof a / sizeof a[0];
            for (size_t i = n; i-- > 0; )           /* safe reverse loop with unsigned index */
                printf("%d ", a[i]);
            printf("\n");
            for (int i = 0, j = (int)n - 1; i < j; i++, j--) {   /* reverse in place */
                int t = a[i]; a[i] = a[j]; a[j] = t;
            }
            for (size_t i = 0; i < n; i++) printf("%d ", a[i]);
            printf("\n");
            return 0;
        }
    ''', out='''
        5 4 3 2 1
        5 4 3 2 1
    ''')
    yield warn("Off-by-one: `for (i = 0; i <= n; i++)` over an array of `n` elements touches `a[n]` — one past the end. That is a buffer overflow (see Memory Bugs).")
    yield qa("What is the difference between while and do-while?",
             "`while` checks the condition *before* each iteration, so the body may run zero times. `do-while` checks *after*, so the body always runs at least once — useful for menus and input validation loops.")
    yield qa("Why is for (unsigned i = n - 1; i >= 0; i--) an infinite loop?",
             "An unsigned value is always `>= 0`; when `i` is 0, `i--` wraps to `UINT_MAX`. Use a signed index or the `for (size_t i = n; i-- > 0; )` idiom.")


@topic(G, "functions", "Functions & Call by Value", "function")
def _():
    yield lead("A function packages a computation behind a name and a *prototype*. C passes every argument **by value** — the function receives copies; to modify the caller’s variable you pass its address.")
    yield section("Declaration, definition, call", "code")
    yield snippet("c", r'''
        #include <stdio.h>

        double average(const int *values, int count);   /* prototype */

        int main(void) {
            int marks[] = {70, 85, 90};
            printf("%.2f\n", average(marks, 3));
            return 0;
        }

        double average(const int *values, int count) {  /* definition */
            if (count == 0) return 0.0;
            long sum = 0;
            for (int i = 0; i < count; i++) sum += values[i];
            return (double)sum / count;
        }
    ''', out="81.67")
    yield table(
        ["Part", "Example", "Notes"],
        ["Return type", "`double`", "`void` if nothing is returned"],
        ["Name", "`average`", "External linkage by default; `static` to hide it"],
        ["Parameters", "`(const int *values, int count)`", "`(void)` means *no* parameters; `()` means *unspecified* (pre-C23)"],
        ["Body", "`{ … }`", "`return expr;` ends the call"],
    )
    yield section("Call by value", "copy")
    yield snippet("c", r'''
        #include <stdio.h>

        void broken_swap(int a, int b) {    /* swaps the copies only */
            int t = a; a = b; b = t;
        }

        void swap(int *a, int *b) {         /* receives addresses ("call by reference" emulation) */
            int t = *a; *a = *b; *b = t;
        }

        int main(void) {
            int x = 1, y = 2;
            broken_swap(x, y);
            printf("after broken_swap: %d %d\n", x, y);
            swap(&x, &y);
            printf("after swap:        %d %d\n", x, y);
            return 0;
        }
    ''', out='''
        after broken_swap: 1 2
        after swap:        2 1
    ''')
    yield note("Even the pointer is passed by value: `swap` gets *copies* of the addresses. It can change what they point to, but not where the caller’s pointer variables point. To change a caller’s pointer, pass a pointer to it (`int **`).")
    yield section("Arrays and structs as parameters", "brackets")
    yield ul(
        "An array argument *decays* to a pointer to its first element: `void f(int a[])` is exactly `void f(int *a)`. The size is lost — pass it separately.",
        "A `struct` is copied in full. For big structs pass `const struct T *` to avoid the copy.",
        "Mark pointer parameters you don’t modify as `const` — it documents intent and lets the compiler check it.",
    )
    yield section("Returning several values", "arrow-back")
    yield snippet("c", r'''
        #include <stdio.h>

        /* return a status, deliver results through out-parameters */
        int divide(int a, int b, int *quot, int *rem) {
            if (b == 0) return -1;
            *quot = a / b;
            *rem = a % b;
            return 0;
        }

        int main(void) {
            int q, r;
            if (divide(17, 5, &q, &r) == 0)
                printf("17 = 5 * %d + %d\n", q, r);
            if (divide(1, 0, &q, &r) != 0)
                printf("division by zero rejected\n");
            return 0;
        }
    ''', out='''
        17 = 5 * 3 + 2
        division by zero rejected
    ''')
    yield section("inline and the order of evaluation", "bolt")
    yield ul(
        "`static inline int sq(int x) { return x * x; }` — a hint to expand the body at the call site; typical in headers as a type-safe macro replacement.",
        "The order in which arguments are evaluated is **unspecified**: in `f(g(), h())` either may run first. Never depend on it.",
        "A function with a non-`void` return type that falls off the end without `return` — and whose value is used — is undefined behaviour (`-Wreturn-type`).",
    )
    yield snippet("c", r'''
        int sign(int x) {
            if (x > 0) return 1;
            if (x < 0) return -1;
        }   /* missing return when x == 0 */
    ''', fails=True, caption="C — rejected: non-void function does not return a value in all paths")
    yield qa("Does C support call by reference?",
             "No — C only has call by value. Passing a pointer *emulates* call by reference: the pointer is copied, but both copies point to the same object, so the callee can modify it through `*p`.")
    yield qa("What is a function prototype and why is it needed?",
             "A declaration giving the return type and parameter types (`int max(int, int);`). It lets the compiler check calls, convert arguments to the right types and catch mistakes, even if the definition appears later or in another file.")
    yield qa("What is the difference between f() and f(void) in a declaration?",
             "Before C23, `int f();` declares a function taking an *unspecified* number of arguments (old K&R style — no checking), while `int f(void);` declares a function that takes *no* arguments. C23 makes them equivalent, but `(void)` is still the portable choice.")


@topic(G, "recursion", "Recursion", "recycle")
def _():
    yield lead("A recursive function calls itself on a smaller problem until it reaches a *base case*. Each call gets its own stack frame, so depth is limited by the stack size.")
    yield section("Anatomy", "list-numbers")
    yield snippet("c", r'''
        #include <stdio.h>

        unsigned long long factorial(unsigned n) {
            if (n <= 1) return 1;              /* base case */
            return n * factorial(n - 1);       /* recursive case: smaller input */
        }

        int main(void) {
            for (unsigned i = 0; i <= 5; i++) printf("%u! = %llu\n", i, factorial(i));
            printf("20! = %llu\n", factorial(20));
            return 0;
        }
    ''', out='''
        0! = 1
        1! = 1
        2! = 2
        3! = 6
        4! = 24
        5! = 120
        20! = 2432902008176640000
    ''')
    yield section("How the call stack unwinds", "stack-2")
    yield snippet("c", r'''
        #include <stdio.h>

        void count(int n, int depth) {
            if (n == 0) { printf("%*sbase\n", depth * 2, ""); return; }
            printf("%*senter %d\n", depth * 2, "", n);
            count(n - 1, depth + 1);
            printf("%*sleave %d\n", depth * 2, "", n);
        }

        int main(void) {
            count(3, 0);
            return 0;
        }
    ''', out='''
        enter 3
          enter 2
            enter 1
              base
            leave 1
          leave 2
        leave 3
    ''')
    yield section("Classic recursive functions", "tree")
    yield snippet("c", r'''
        #include <stdio.h>

        int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }   /* Euclid, tail-recursive */

        long power(long base, int exp) {                                /* fast exponentiation O(log n) */
            if (exp == 0) return 1;
            long half = power(base, exp / 2);
            return exp % 2 ? half * half * base : half * half;
        }

        int sum_digits(int n) { return n < 10 ? n : n % 10 + sum_digits(n / 10); }

        void hanoi(int n, char from, char to, char via) {
            if (n == 0) return;
            hanoi(n - 1, from, via, to);
            printf("move disk %d %c->%c\n", n, from, to);
            hanoi(n - 1, via, to, from);
        }

        int main(void) {
            printf("gcd=%d pow=%ld digits=%d\n", gcd(84, 36), power(3, 13), sum_digits(98765));
            hanoi(2, 'A', 'C', 'B');
            return 0;
        }
    ''', out='''
        gcd=12 pow=1594323 digits=35
        move disk 1 A->B
        move disk 2 A->C
        move disk 1 B->C
    ''')
    yield section("Exponential blow-up and memoisation", "chart-line")
    yield snippet("c", r'''
        #include <stdio.h>

        static long calls = 0;

        long fib_naive(int n) {
            calls++;
            return n < 2 ? n : fib_naive(n - 1) + fib_naive(n - 2);
        }

        long memo[91];
        long fib_memo(int n) {
            if (n < 2) return n;
            if (memo[n]) return memo[n];
            return memo[n] = fib_memo(n - 1) + fib_memo(n - 2);
        }

        int main(void) {
            printf("fib(25) = %ld using %ld calls\n", fib_naive(25), calls);
            printf("fib(90) = %ld\n", fib_memo(90));
            return 0;
        }
    ''', out='''
        fib(25) = 75025 using 242785 calls
        fib(90) = 2880067194370816120
    ''')
    yield table(
        ["Recursion", "Iteration"],
        ["Natural for trees, divide & conquer, backtracking", "Natural for linear scans"],
        ["Uses O(depth) stack — risk of **stack overflow**", "O(1) extra space"],
        ["Function-call overhead", "No call overhead"],
        ["Tail calls *may* be optimised at `-O2` (not guaranteed by C)", "Always constant stack"],
    )
    yield warn("Missing or unreachable base case → infinite recursion → *stack overflow* (segfault). Default stacks are only ~8 MB on Linux/macOS main threads, often much less on threads and embedded targets.")
    yield qa("What is tail recursion?",
             "A call is a *tail call* when it is the last action of the function (`return f(n - 1, acc * n);`). The compiler can then reuse the current stack frame, turning recursion into a loop. C compilers do this at higher optimisation levels, but the standard does not guarantee it.")
    yield qa("What is the time complexity of naive recursive Fibonacci?",
             "O(φⁿ) ≈ O(1.618ⁿ) calls because every call branches into two overlapping subproblems. Memoisation or a bottom-up loop makes it O(n).")


@topic(G, "scope-lifetime", "Scope, Linkage & Lifetime", "eye")
def _():
    yield lead("Three independent questions about every identifier: *where* can the name be used (scope), *how long* does the object exist (storage duration) and *can other files see it* (linkage).")
    yield section("Scope — where a name is visible", "focus")
    yield table(
        ["Scope", "Begins / ends", "Example"],
        ["Block", "Declaration → closing `}`", "Locals, loop variables `for (int i…)`"],
        ["File", "Declaration → end of translation unit", "Globals, functions"],
        ["Function", "Whole function", "Only `goto` labels"],
        ["Function prototype", "End of the prototype", "`int f(int n);` — the name `n`"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int x = 1;                           /* file scope */

        int main(void) {
            printf("global x = %d\n", x);
            int x = 2;                       /* shadows the global */
            {
                int x = 3;                   /* shadows the outer local */
                printf("inner x = %d\n", x);
            }
            printf("local x = %d\n", x);
            for (int i = 0; i < 1; i++) {
                printf("i = %d\n", i);
            }
            /* i is out of scope here */
            return 0;
        }
    ''', out='''
        global x = 1
        inner x = 3
        local x = 2
        i = 0
    ''')
    yield section("Storage duration — how long the object lives", "clock")
    yield table(
        ["Duration", "Objects", "Lifetime", "Where"],
        ["Automatic", "Locals, parameters", "Until the block exits", "Stack"],
        ["Static", "Globals, `static` locals, string literals", "Whole program", "`.data` / `.bss` / `.rodata`"],
        ["Allocated", "`malloc` / `calloc` / `realloc`", "Until `free`", "Heap"],
        ["Thread (C11)", "`_Thread_local`", "Lifetime of the thread", "Per-thread storage"],
    )
    yield section("Lifetime ends while a pointer lives on", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>

        int *make_counter(void) {
            int count = 0;
            return &count;           /* address of a local that dies on return */
        }

        int main(void) {
            int *p = make_counter();
            printf("%d\n", *p);
            return 0;
        }
    ''', fails=True, caption="C — rejected: returning the address of a local variable")
    yield output("main.c:5:13: error: address of stack memory associated with local variable 'count' returned [-Werror,-Wreturn-stack-address]", "Compiler")
    yield p("Fixes: return the value itself, use a `static` local, let the caller pass a buffer, or allocate with `malloc` (caller frees).")
    yield section("Linkage — can other files see it?", "link")
    yield cards(
        ("External", "Globals and functions by default. The same name in every file refers to one object.", "world"),
        ("Internal", "`static` at file scope. Private to one translation unit.", "lock"),
        ("None", "Locals and parameters. Every declaration is a distinct object.", "circle-off"),
        cols=3,
    )
    yield qa("What is the difference between scope and lifetime?",
             "Scope is a compile-time property of a *name* (the region of source where it can be used). Lifetime is a run-time property of an *object* (when its storage exists). A `static` local has block scope but lives for the whole program; a `malloc`ed object has no name at all but lives until `free`.")
    yield qa("What is variable shadowing?",
             "Declaring a variable in an inner scope with the same name as one in an outer scope; the inner name hides the outer one until its block ends. It is legal but confusing — `-Wshadow` warns about it.")
