from kit import *

G = "Pointers"


@topic(G, "pointers", "Pointer Basics", "pointer")
def _():
    yield lead("A pointer is a variable that holds the *address* of another object. `&` takes an address, `*` follows one. Pointers are what make C fast, flexible — and dangerous.")
    yield define("Pointer", "an object whose value is a memory address, together with the *type* of what lives there. `int *p` means “`p` points to an `int`” — the type tells the compiler how many bytes to read through it and how far `p + 1` moves.")
    yield section("Declare, take an address, dereference", "code")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int x = 10;
            int *p = &x;          /* p holds the address of x */

            printf("x = %d, *p = %d\n", x, *p);
            *p = 20;              /* write through the pointer */
            printf("x = %d\n", x);
            printf("p == &x ? %d\n", p == &x);
            printf("sizeof p = %zu, sizeof *p = %zu\n", sizeof p, sizeof *p);
            return 0;
        }
    ''', out='''
        x = 10, *p = 10
        x = 20
        p == &x ? 1
        sizeof p = 8, sizeof *p = 4
    ''')
    yield table(
        ["Expression", "Meaning", "Value here"],
        ["`x`", "The `int` itself", "20"],
        ["`&x`", "Address of `x` (type `int *`)", "e.g. `0x16fdff1ac`"],
        ["`p`", "The address stored in `p`", "same as `&x`"],
        ["`*p`", "The `int` at that address", "20"],
        ["`&p`", "Address of the pointer variable (type `int **`)", "another address"],
    )
    yield section("Printing addresses", "at")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a = 1;
            double d = 2.0;
            printf("&a = %p\n&d = %p\n", (void *)&a, (void *)&d);
            return 0;
        }
    ''', caption="C — addresses change on every run (ASLR), so no fixed output")
    yield note("`%p` expects a `void *`; cast other pointer types. Addresses differ between runs because of *address space layout randomisation*.")
    yield section("NULL and pointer states", "circle-off")
    yield cards(
        ("Valid", "Points to a live object of the right type — the only state you may dereference.", "circle-check"),
        ("NULL", "`p = NULL;` — explicitly points nowhere. Test with `if (p)` / `if (p != NULL)`. Dereferencing it crashes.", "circle-off"),
        ("Wild / uninitialised", "`int *p;` holds garbage. Dereferencing it writes to a random address.", "alert-circle"),
        ("Dangling", "Pointed to an object whose lifetime ended (freed or out of scope).", "unlink"),
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int find(const int *a, int n, int key, const int **where) {
            for (int i = 0; i < n; i++)
                if (a[i] == key) { *where = &a[i]; return 1; }
            *where = NULL;
            return 0;
        }

        int main(void) {
            int nums[] = {4, 8, 15};
            const int *hit;
            if (find(nums, 3, 8, &hit)) printf("found %d at index %td\n", *hit, hit - nums);
            if (!find(nums, 3, 99, &hit) && hit == NULL) printf("99 not found, hit is NULL\n");
            return 0;
        }
    ''', out='''
        found 8 at index 1
        99 not found, hit is NULL
    ''')
    yield section("Dereferencing NULL", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int *p = NULL;
            printf("%d\n", *p);      /* segmentation fault */
            return 0;
        }
    ''', fails=True, caption="C — NULL dereference (UBSan: load of null pointer; without it, a segfault)")
    yield warn("`int* a, b;` declares **one** pointer (`a`) and one `int` (`b`) — the `*` binds to the name, not the type. Write `int *a, *b;` or one declaration per line.")
    yield qa("What is the size of a pointer?",
             "It depends on the platform, not on the pointed-to type: 8 bytes on 64-bit systems, 4 on 32-bit. `sizeof(char *) == sizeof(double *)` on all mainstream platforms (function pointers can differ on exotic ones).")
    yield qa("What is the difference between NULL, 0 and '\\0'?",
             "`NULL` is a null *pointer* constant (usually `((void *)0)`). `0` is an integer that also acts as a null pointer constant in pointer context. `'\\0'` is the NUL *character* (an `int` with value 0) used to terminate strings. They compare equal to zero but mean different things — use each in its own role. C23 adds `nullptr`.")
    yield qa("Why use pointers at all?",
             "To let functions modify caller data (out-parameters), to pass large objects cheaply, to work with dynamically allocated memory, to build linked data structures (lists, trees, graphs), to iterate arrays efficiently and to implement callbacks via function pointers.")


@topic(G, "pointer-arithmetic", "Pointer Arithmetic", "plus-minus")
def _():
    yield lead("Adding `n` to a pointer moves it by `n` *elements*, not bytes: `p + 1` advances by `sizeof *p`. Arithmetic is only valid within one array (plus one-past-the-end).")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {10, 20, 30, 40};
            int *p = a;                  /* &a[0] */
            char *c = (char *)a;

            printf("%d %d %d\n", *p, *(p + 1), *(p + 3));
            printf("int step  = %td bytes\n", (char *)(p + 1) - (char *)p);
            printf("char step = %td bytes\n", (c + 1) - c);

            int *end = a + 4;            /* one past the end: may be compared, never dereferenced */
            printf("elements between = %td\n", end - p);
            for (int *q = a; q < end; q++) printf("%d ", *q);
            printf("\n");
            return 0;
        }
    ''', out='''
        10 20 40
        int step  = 4 bytes
        char step = 1 bytes
        elements between = 4
        10 20 30 40
    ''')
    yield section("What is allowed", "list-check")
    yield table(
        ["Operation", "Allowed?", "Result"],
        ["`p + n`, `p - n`, `p++`, `p--`", "Yes, within the array / one past end", "Pointer"],
        ["`p - q` (same array)", "Yes", "`ptrdiff_t` element count (`%td`)"],
        ["`p < q`, `p == q`", "Yes (relational only within one array)", "0 / 1"],
        ["`p + q`, `p * 2`, `p / 2`", "**No** — compile error", "—"],
        ["`p + n` beyond one-past-end", "**Undefined** even without dereferencing", "—"],
        ["Arithmetic on `void *`", "Not in standard C (GNU extension treats it as `char *`)", "—"],
    )
    yield section("Idioms", "code")
    yield snippet("c", r'''
        #include <stdio.h>

        size_t length(const char *s) {
            const char *p = s;
            while (*p) p++;                 /* walk to the terminator */
            return (size_t)(p - s);         /* pointer difference = count */
        }

        void copy(char *dst, const char *src) {
            while ((*dst++ = *src++) != '\0') { }   /* classic K&R strcpy */
        }

        int sum(const int *begin, const int *end) {
            int s = 0;
            while (begin != end) s += *begin++;     /* *(begin++) */
            return s;
        }

        int main(void) {
            char buf[16];
            copy(buf, "pointer");
            int v[] = {1, 2, 3, 4, 5};
            printf("%s %zu %d\n", buf, length(buf), sum(v, v + 5));
            return 0;
        }
    ''', out="pointer 7 15")
    yield section("Precedence of `*` and `++`", "arrows-sort")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {10, 20, 30};
            int *p = a;
            int x;
            x = *p++;    printf("*p++   -> %d, now *p = %d\n", x, *p);   /* read, then move */
            x = *++p;    printf("*++p   -> %d\n", x);                    /* move, then read */
            p = a;
            x = ++*p;    printf("++*p   -> %d, a[0] = %d\n", x, a[0]);   /* increment the value */
            x = (*p)++;  printf("(*p)++ -> %d, a[0] = %d\n", x, a[0]);   /* read, then increment value */
            return 0;
        }
    ''', out='''
        *p++   -> 10, now *p = 20
        *++p   -> 30
        ++*p   -> 11, a[0] = 11
        (*p)++ -> 11, a[0] = 12
    ''')
    yield section("Walking off the end", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            int *a = malloc(3 * sizeof *a);
            if (!a) return 1;
            for (int *p = a; p <= a + 3; p++)   /* <= : writes a[3] */
                *p = 0;
            printf("%d\n", a[0]);
            free(a);
            return 0;
        }
    ''', fails=True, caption="C — heap-buffer-overflow caught by AddressSanitizer")
    yield qa("If int *p = (int *)1000, what is p + 1?",
             "`1004` on a platform with 4-byte `int` — pointer arithmetic scales by the size of the pointed-to type. For `char *` it would be `1001`, for `double *` `1008`.")
    yield qa("Can you subtract two pointers? Add them?",
             "You can subtract two pointers into the same array: the result is the number of elements between them (`ptrdiff_t`). Adding two pointers is meaningless and a compile error.")


@topic(G, "pointers-and-arrays", "Pointers & Arrays", "arrows-left-right")
def _():
    yield lead("Arrays and pointers are closely related but **not** the same thing: an array *is* storage; a pointer *refers to* storage. The link is decay — an array name converts to a pointer to its first element.")
    yield formula("`a[i]`  ≡  `*(a + i)`  ≡  `*(i + a)`  ≡  `i[a]`")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[4] = {1, 2, 3, 4};
            int *p = a;                      /* decay: p = &a[0] */

            printf("%d %d %d %d\n", a[2], *(a + 2), p[2], 2[a]);   /* all the same */
            printf("sizeof a = %zu, sizeof p = %zu\n", sizeof a, sizeof p);

            p++;                             /* a pointer can move... */
            printf("*p = %d\n", *p);
            /* a++;  ...an array cannot: error, array type is not assignable */
            return 0;
        }
    ''', out='''
        3 3 3 3
        sizeof a = 16, sizeof p = 8
        *p = 2
    ''')
    yield table(
        ["", "Array `int a[4]`", "Pointer `int *p`"],
        ["What it is", "4 ints of storage", "8 bytes holding an address"],
        ["`sizeof`", "16", "8"],
        ["Assignable (`a = …`)", "No", "Yes"],
        ["`&x`", "`int (*)[4]` — pointer to the whole array", "`int **`"],
        ["Where the data is", "Inside the array itself", "Somewhere else"],
    )
    yield section("&a vs a: same address, different types", "fingerprint")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[4] = {0};
            int *first = a;              /* int *      */
            int (*whole)[4] = &a;        /* int (*)[4] */
            printf("same address: %d\n", (void *)first == (void *)whole);
            printf("first + 1 moves %td bytes\n", (char *)(first + 1) - (char *)first);
            printf("whole + 1 moves %td bytes\n", (char *)(whole + 1) - (char *)whole);
            return 0;
        }
    ''', out='''
        same address: 1
        first + 1 moves 4 bytes
        whole + 1 moves 16 bytes
    ''')
    yield section("Arrays of pointers vs pointer to array", "list-tree")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int x = 1, y = 2, z = 3;
            int *arr_of_ptrs[3] = {&x, &y, &z};    /* 3 pointers */
            int grid[2][3] = {{1, 2, 3}, {4, 5, 6}};
            int (*row)[3] = grid;                  /* pointer to an array of 3 ints */

            printf("%d %d\n", *arr_of_ptrs[1], *arr_of_ptrs[2]);
            row++;                                 /* moves one whole row */
            printf("%d %d\n", (*row)[0], row[0][2]);
            return 0;
        }
    ''', out='''
        2 3
        4 6
    ''')
    yield section("sizeof inside a function", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>

        void f(int arr[10]) {                    /* the 10 is ignored: arr is int * */
            printf("in f: %zu\n", sizeof arr);
        }

        int main(void) {
            int data[10];
            printf("in main: %zu\n", sizeof data);
            f(data);
            return 0;
        }
    ''', fails=True, caption="C — clang flags the misleading sizeof (-Wsizeof-array-argument)")
    yield qa("Are arrays and pointers the same in C?",
             "No. An array is a contiguous block of objects; a pointer is a single variable holding an address. They behave alike because an array expression decays to a pointer to its first element and `a[i]` is defined via pointer arithmetic. They differ in `sizeof`, in assignability and in what `&` produces.")
    yield qa("What does int (*p)[5] declare, versus int *p[5]?",
             "`int (*p)[5]` is *one* pointer to an array of 5 ints (used to walk 2-D arrays row by row). `int *p[5]` is an *array of 5 pointers* to int — `[]` binds tighter than `*`.")


@topic(G, "pointer-to-pointer", "Pointers to Pointers", "link")
def _():
    yield lead("A `T **` points to a `T *`. You need one whenever a function must change *which* object a caller’s pointer refers to — and for arrays of strings like `argv`.")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int x = 5;
            int *p = &x;
            int **pp = &p;
            **pp = 50;                         /* x = 50 */
            printf("%d %d %d\n", x, *p, **pp);
            printf("%d %d\n", *pp == p, p == &x);
            return 0;
        }
    ''', out='''
        50 50 50
        1 1
    ''')
    yield flow("`pp` (`int **`)", "`p` (`int *`)", "`x` (`int`) = 50")
    yield section("Changing the caller's pointer", "arrow-back-up")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        /* allocate and hand back through an out-parameter */
        int make_array(int **out, int n) {
            int *a = malloc(n * sizeof *a);
            if (!a) return -1;
            for (int i = 0; i < n; i++) a[i] = i * 10;
            *out = a;                        /* modifies the caller's pointer */
            return 0;
        }

        void free_and_null(int **p) {
            free(*p);
            *p = NULL;                       /* caller's pointer no longer dangles */
        }

        int main(void) {
            int *data = NULL;
            if (make_array(&data, 4) == 0) printf("%d %d\n", data[1], data[3]);
            free_and_null(&data);
            printf("data is %s\n", data == NULL ? "NULL" : "set");
            return 0;
        }
    ''', out='''
        10 30
        data is NULL
    ''')
    yield section("Dynamic 2-D arrays (jagged)", "grid-dots")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            int rows = 3;
            int **tri = malloc(rows * sizeof *tri);          /* array of row pointers */
            if (!tri) return 1;
            for (int r = 0; r < rows; r++) {
                tri[r] = malloc((r + 1) * sizeof **tri);      /* each row its own length */
                if (!tri[r]) return 1;
                for (int c = 0; c <= r; c++)
                    tri[r][c] = (c == 0 || c == r) ? 1 : tri[r - 1][c - 1] + tri[r - 1][c];
            }
            for (int r = 0; r < rows; r++) {
                for (int c = 0; c <= r; c++) printf("%d ", tri[r][c]);
                printf("\n");
                free(tri[r]);                                  /* free rows first... */
            }
            free(tri);                                         /* ...then the spine */
            return 0;
        }
    ''', out='''
        1
        1 1
        1 2 1
    ''')
    yield note("A contiguous alternative is one `malloc(rows * cols * sizeof(int))` indexed as `a[r * cols + c]`, or a pointer to a VLA row type: `int (*m)[cols] = malloc(rows * sizeof *m);` — one allocation, one `free`, cache-friendly.")
    yield section("Linked-list insertion with `**`", "list")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        struct node { int val; struct node *next; };

        /* inserting at the head changes the caller's head pointer */
        void push(struct node **head, int v) {
            struct node *n = malloc(sizeof *n);
            if (!n) return;
            n->val = v;
            n->next = *head;
            *head = n;
        }

        int main(void) {
            struct node *head = NULL;
            push(&head, 3); push(&head, 2); push(&head, 1);
            for (struct node *n = head; n; n = n->next) printf("%d ", n->val);
            printf("\n");
            while (head) { struct node *next = head->next; free(head); head = next; }
            return 0;
        }
    ''', out="1 2 3")
    yield qa("When do you need a double pointer?",
             "When a function must modify a pointer owned by the caller (allocate into it, reset it to `NULL`, change a list head), and to represent arrays of pointers — `char **argv`, jagged 2-D arrays, arrays of strings.")


@topic(G, "const-pointers", "const with Pointers", "lock")
def _():
    yield lead("`const` can protect the *pointed-to data*, the *pointer itself*, or both. Read the declaration **right to left**.")
    yield table(
        ["Declaration", "Read as", "Change `*p`?", "Change `p`?"],
        ["`int *p`", "pointer to int", "Yes", "Yes"],
        ["`const int *p` (= `int const *p`)", "pointer to const int", "**No**", "Yes"],
        ["`int *const p`", "const pointer to int", "Yes", "**No**"],
        ["`const int *const p`", "const pointer to const int", "**No**", "**No**"],
    )
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a = 1, b = 2;

            const int *to_const = &a;     /* read-only view */
            to_const = &b;                /* OK: pointer can move */

            int *const fixed = &a;        /* pointer is fixed */
            *fixed = 10;                  /* OK: data can change */

            const int *const both = &b;
            printf("%d %d %d\n", *to_const, a, *both);
            return 0;
        }
    ''', out="2 10 2")
    yield snippet("c", r'''
        int main(void) {
            int a = 1, b = 2;
            const int *to_const = &a;
            *to_const = 5;                /* error: read-only */
            int *const fixed = &a;
            fixed = &b;                   /* error: pointer is const */
            return 0;
        }
    ''', fails=True, caption="C — both assignments are compile errors")
    yield section("const in function parameters", "function")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <ctype.h>

        /* const promises: "I will only read the characters" */
        int count_upper(const char *s) {
            int n = 0;
            for (; *s; s++)                 /* moving the pointer is fine */
                if (isupper((unsigned char)*s)) n++;
            return n;
        }

        int main(void) {
            char name[] = "Hello World";
            printf("%d\n", count_upper(name));   /* char * -> const char * is implicit */
            printf("%d\n", count_upper("ABC"));
            return 0;
        }
    ''', out='''
        2
        3
    ''')
    yield note("Converting `T *` → `const T *` is implicit and safe. The reverse (`const T *` → `T *`) needs a cast, and writing through the result to a truly `const` object is undefined behaviour.")
    yield dodont("Mark every pointer parameter you only read as `const` — `size_t strlen(const char *s)`, `void print(const struct item *it)`.",
                 "Cast `const` away to “make it compile”.")
    yield qa("What is the difference between const char *p, char const *p and char *const p?",
             "The first two are identical: a (modifiable) pointer to read-only `char`s. The third is a read-only pointer to modifiable `char`s — `p` must be initialised and can never point elsewhere. Rule: `const` applies to what is on its left, or to the right if nothing is on the left.")
    yield qa("Can a const variable be modified through a pointer?",
             "Only by casting away `const`, and if the object was *defined* `const` the result is undefined behaviour (it may live in read-only memory, or the compiler may have folded its value into the code).")


@topic(G, "function-pointers", "Function Pointers & Callbacks", "arrow-forward-up")
def _():
    yield lead("A function’s name decays to its address. Storing that in a *function pointer* lets you pass behaviour as data — callbacks, dispatch tables, plug-in strategies, `qsort` comparators.")
    yield section("Syntax", "code")
    yield snippet("c", r'''
        #include <stdio.h>

        int add(int a, int b) { return a + b; }
        int mul(int a, int b) { return a * b; }

        int main(void) {
            int (*op)(int, int) = add;        /* pointer to function taking (int,int) returning int */
            printf("%d\n", op(3, 4));
            op = &mul;                        /* & is optional */
            printf("%d\n", (*op)(3, 4));      /* explicit * is optional too */
            return 0;
        }
    ''', out='''
        7
        12
    ''')
    yield note("`int (*op)(int, int)` — the parentheses matter. `int *op(int, int)` would declare a *function* returning `int *`. A `typedef` makes it readable: `typedef int (*binop)(int, int);`.")
    yield section("Callbacks: qsort", "sort-ascending")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        int cmp_int_asc(const void *a, const void *b) {
            int x = *(const int *)a, y = *(const int *)b;
            return (x > y) - (x < y);         /* avoids overflow of x - y */
        }

        int cmp_str(const void *a, const void *b) {
            return strcmp(*(const char *const *)a, *(const char *const *)b);
        }

        int main(void) {
            int nums[] = {42, -7, 19, 0, 3};
            qsort(nums, 5, sizeof nums[0], cmp_int_asc);
            for (int i = 0; i < 5; i++) printf("%d ", nums[i]);
            printf("\n");

            const char *words[] = {"pear", "apple", "fig"};
            qsort(words, 3, sizeof words[0], cmp_str);
            printf("%s %s %s\n", words[0], words[1], words[2]);

            int key = 19;
            int *hit = bsearch(&key, nums, 5, sizeof nums[0], cmp_int_asc);
            printf("19 at index %td\n", hit - nums);
            return 0;
        }
    ''', out='''
        -7 0 3 19 42
        apple fig pear
        19 at index 3
    ''')
    yield warn("`return x - y;` in a comparator overflows for large values of opposite sign (`INT_MIN - 1`). Use `(x > y) - (x < y)`.")
    yield section("Your own higher-order function", "math-function")
    yield snippet("c", r'''
        #include <stdio.h>

        typedef int (*transform_fn)(int);

        int square(int x) { return x * x; }
        int negate(int x) { return -x; }

        void map(int *a, int n, transform_fn f) {
            for (int i = 0; i < n; i++) a[i] = f(a[i]);
        }

        int main(void) {
            int v[] = {1, 2, 3};
            map(v, 3, square);
            map(v, 3, negate);
            printf("%d %d %d\n", v[0], v[1], v[2]);
            return 0;
        }
    ''', out="-1 -4 -9")
    yield section("Dispatch tables", "table")
    yield snippet("c", r'''
        #include <stdio.h>

        double add(double a, double b) { return a + b; }
        double sub(double a, double b) { return a - b; }
        double mul(double a, double b) { return a * b; }
        double dvd(double a, double b) { return a / b; }

        int main(void) {
            struct { char sym; double (*fn)(double, double); } ops[] = {
                {'+', add}, {'-', sub}, {'*', mul}, {'/', dvd},
            };
            for (int i = 0; i < 4; i++)
                printf("8 %c 2 = %g\n", ops[i].sym, ops[i].fn(8, 2));
            return 0;
        }
    ''', out='''
        8 + 2 = 10
        8 - 2 = 6
        8 * 2 = 16
        8 / 2 = 4
    ''')
    yield section("Callbacks with context", "package")
    yield snippet("c", r'''
        #include <stdio.h>

        /* C has no closures: pass state through a void * "user data" pointer */
        void for_each(const int *a, int n, void (*visit)(int, void *), void *ctx) {
            for (int i = 0; i < n; i++) visit(a[i], ctx);
        }

        void accumulate(int x, void *ctx) { *(long *)ctx += x; }

        int main(void) {
            int a[] = {5, 10, 20};
            long total = 0;
            for_each(a, 3, accumulate, &total);
            printf("total = %ld\n", total);
            return 0;
        }
    ''', out="total = 35")
    yield qa("How do you declare a function that returns a function pointer?",
             "Directly: `int (*get_op(char c))(int, int);` — `get_op` takes a `char` and returns a pointer to a function `(int, int) -> int`. With a typedef it is readable: `typedef int (*binop)(int, int); binop get_op(char c);`.")
    yield qa("What are function pointers used for in real systems?",
             "Callbacks (`qsort`, `bsearch`, `atexit`, `signal`, event handlers), dispatch/jump tables for interpreters and state machines, plug-in interfaces (a struct of function pointers is C's version of a vtable — e.g. Linux `struct file_operations`), and dynamic loading with `dlsym`.")


@topic(G, "void-pointers", "void Pointers & Generic Code", "box-multiple")
def _():
    yield lead("`void *` is a pointer to *something* of unknown type. Any object pointer converts to and from it implicitly — it is how C writes generic code (`malloc`, `memcpy`, `qsort`).")
    yield snippet("c", r'''
        #include <stdio.h>

        void print_value(const void *p, char type) {
            switch (type) {
                case 'i': printf("int %d\n", *(const int *)p); break;
                case 'd': printf("double %.2f\n", *(const double *)p); break;
                case 's': printf("string %s\n", (const char *)p); break;
            }
        }

        int main(void) {
            int i = 7;
            double d = 2.5;
            print_value(&i, 'i');
            print_value(&d, 'd');
            print_value("text", 's');
            return 0;
        }
    ''', out='''
        int 7
        double 2.50
        string text
    ''')
    yield section("Rules", "list-check")
    yield ul(
        "You **cannot dereference** a `void *` — cast it to a concrete type first.",
        "No pointer arithmetic on `void *` in standard C (GCC allows it as an extension, treating the size as 1).",
        "`T *` → `void *` → `T *` round-trips safely. Converting to the *wrong* type and dereferencing is undefined behaviour.",
        "In C, `malloc`’s `void *` result needs no cast: `int *p = malloc(n * sizeof *p);`. (C++ requires one.)",
        "Function pointers are **not** guaranteed to convert to `void *` (POSIX allows it for `dlsym`).",
    )
    yield section("A generic swap", "arrows-exchange")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        void swap_any(void *a, void *b, size_t size) {
            unsigned char tmp[64];            /* enough for this demo */
            if (size > sizeof tmp) return;
            memcpy(tmp, a, size);
            memcpy(a, b, size);
            memcpy(b, tmp, size);
        }

        int main(void) {
            int x = 1, y = 2;
            double p = 1.5, q = 9.75;
            swap_any(&x, &y, sizeof x);
            swap_any(&p, &q, sizeof p);
            printf("%d %d %.2f %.2f\n", x, y, p, q);
            return 0;
        }
    ''', out="2 1 9.75 1.50")
    yield section("A generic linear search", "search")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        /* returns the index of the first element equal to key, or -1 */
        long find(const void *base, size_t n, size_t size, const void *key,
                  int (*eq)(const void *, const void *)) {
            const unsigned char *p = base;             /* byte pointer for arithmetic */
            for (size_t i = 0; i < n; i++)
                if (eq(p + i * size, key)) return (long)i;
            return -1;
        }

        int eq_int(const void *a, const void *b) { return *(const int *)a == *(const int *)b; }
        int eq_str(const void *a, const void *b) {
            return strcmp(*(const char *const *)a, *(const char *const *)b) == 0;
        }

        int main(void) {
            int nums[] = {3, 1, 4, 1, 5};
            int k = 4;
            const char *names[] = {"ann", "bob", "cy"};
            const char *who = "cy";
            printf("%ld %ld\n", find(nums, 5, sizeof nums[0], &k, eq_int),
                   find(names, 3, sizeof names[0], &who, eq_str));
            return 0;
        }
    ''', out="2 2")
    yield warn("`void *` throws away type checking — the compiler can no longer catch a wrong cast. Keep the `void *` boundary thin and convert back to real types immediately.")
    yield qa("Why can't a void pointer be dereferenced?",
             "Dereferencing needs to know the size and interpretation of the object. `void` is an incomplete type with no size, so the compiler cannot generate a load or store — you must first cast to a complete type.")
    yield qa("Why does qsort's comparator take const void *?",
             "`qsort` is written once for every element type, so it only knows the base address, the element count and the element size. It hands the comparator pointers to two elements as `const void *`; the comparator, which knows the real type, casts them back.")


@topic(G, "complex-declarations", "Reading Complex Declarations", "spiral")
def _():
    yield lead("C declarations mirror usage: `int *a[3]` says “`*a[i]` is an int”. Decode any declaration with the *right-left rule* — start at the name, go right, then left, and jump out of parentheses.")
    yield steps(
        ("Find the identifier", "Start at the name being declared."),
        ("Go right", "`[N]` → “array of N”, `(…)` → “function taking … returning”. Stop at a `)` or the end."),
        ("Go left", "`*` → “pointer to”, `const` → “const”. Stop at a `(`."),
        ("Jump out", "Leave the parentheses and repeat right-then-left until you reach the base type."),
    )
    yield table(
        ["Declaration", "Meaning"],
        ["`int *p[5]`", "array of 5 pointers to int"],
        ["`int (*p)[5]`", "pointer to an array of 5 ints"],
        ["`int *f(void)`", "function returning pointer to int"],
        ["`int (*f)(void)`", "pointer to a function returning int"],
        ["`int (*fs[4])(int)`", "array of 4 pointers to functions taking int returning int"],
        ["`char **argv`", "pointer to pointer to char"],
        ["`const char *const *p`", "pointer to const pointer to const char"],
        ["`void (*signal(int, void (*)(int)))(int)`", "function taking (int, pointer to handler) returning pointer to a handler `void (*)(int)`"],
        ["`int (*(*x)(void))[3]`", "pointer to function returning pointer to array of 3 ints"],
    )
    yield section("typedef tames them", "wand")
    yield snippet("c", r'''
        #include <stdio.h>

        typedef void (*handler_t)(int);         /* pointer to function (int) -> void */
        typedef int row3_t[3];                  /* array of 3 ints */

        void on_event(int code) { printf("event %d\n", code); }

        /* without typedef: void (*install(handler_t h))(int) */
        handler_t install(handler_t h) { return h; }

        int main(void) {
            handler_t table[2] = {on_event, on_event};
            install(table[0])(7);

            row3_t grid[2] = {{1, 2, 3}, {4, 5, 6}};
            row3_t *r = &grid[1];                  /* int (*r)[3] */
            printf("%d\n", (*r)[2]);
            return 0;
        }
    ''', out='''
        event 7
        6
    ''')
    yield note("`cdecl` (command-line tool / cdecl.org) translates both ways: `explain int (*(*x)(void))[3]`.", "Tool")
    yield qa("Explain void (*signal(int sig, void (*func)(int)))(int).",
             "`signal` is a function taking an `int` and a pointer to a function `(int) → void`, and it returns a pointer to a function `(int) → void` (the previous handler). With `typedef void (*sighandler_t)(int);` it reads `sighandler_t signal(int sig, sighandler_t func);`.")
