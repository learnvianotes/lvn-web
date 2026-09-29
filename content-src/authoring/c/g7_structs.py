from kit import *

G = "Structures & User-Defined Types"


@topic(G, "structs", "Structures", "packages")
def _():
    yield lead("A `struct` groups related values of different types into one object — C’s building block for records, and for every data structure.")
    yield section("Define, initialise, access", "code")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        struct Student {
            int id;
            char name[20];
            double gpa;
        };

        int main(void) {
            struct Student a = {1, "Asha", 8.9};                        /* positional */
            struct Student b = {.name = "Ravi", .gpa = 7.5, .id = 2};   /* designated (C99) */
            struct Student c = {0};                                     /* all zero */

            c.id = 3;
            strcpy(c.name, "Meera");
            c.gpa = 9.2;

            struct Student *p = &c;
            p->gpa += 0.1;                     /* p->gpa is (*p).gpa */

            printf("%d %s %.1f\n", a.id, a.name, a.gpa);
            printf("%d %s %.1f\n", b.id, b.name, b.gpa);
            printf("%d %s %.1f\n", p->id, (*p).name, p->gpa);
            return 0;
        }
    ''', out='''
        1 Asha 8.9
        2 Ravi 7.5
        3 Meera 9.3
    ''')
    yield table(
        ["Operator", "Use with", "Example"],
        ["`.`", "a struct object", "`s.gpa`"],
        ["`->`", "a pointer to a struct", "`p->gpa` ≡ `(*p).gpa`"],
    )
    yield section("Copying, passing and returning", "copy")
    yield snippet("c", r'''
        #include <stdio.h>

        typedef struct { double x, y; } Point;

        Point midpoint(Point a, Point b) {          /* by value: copies in, copy out */
            return (Point){(a.x + b.x) / 2, (a.y + b.y) / 2};    /* compound literal */
        }

        void translate(Point *p, double dx, double dy) {         /* by pointer: modifies caller */
            p->x += dx;
            p->y += dy;
        }

        int main(void) {
            Point a = {0, 0}, b = {4, 2};
            Point m = midpoint(a, b);
            Point copy = m;                 /* struct assignment copies every member */
            translate(&m, 1, 1);
            printf("m=(%.1f,%.1f) copy=(%.1f,%.1f)\n", m.x, m.y, copy.x, copy.y);
            return 0;
        }
    ''', out="m=(3.0,2.0) copy=(2.0,1.0)")
    yield note("Structs *can* be assigned, passed and returned by value (arrays can’t). They **cannot** be compared with `==` — compare member by member. Pass large structs as `const T *` to avoid copying.")
    yield section("Nested structs and arrays of structs", "hierarchy")
    yield snippet("c", r'''
        #include <stdio.h>

        struct Date { int d, m, y; };
        struct Employee {
            char name[16];
            struct Date joined;           /* nested */
            double salary;
        };

        int main(void) {
            struct Employee staff[] = {
                {"Anil", {1, 4, 2020}, 50000},
                {"Bina", {15, 9, 2018}, 72000},
                {"Chen", {3, 1, 2022}, 61000},
            };
            int n = sizeof staff / sizeof staff[0];
            double total = 0;
            for (int i = 0; i < n; i++) {
                total += staff[i].salary;
                printf("%-5s joined %02d/%02d/%d\n", staff[i].name,
                       staff[i].joined.d, staff[i].joined.m, staff[i].joined.y);
            }
            printf("average salary %.0f\n", total / n);
            return 0;
        }
    ''', out='''
        Anil  joined 01/04/2020
        Bina  joined 15/09/2018
        Chen  joined 03/01/2022
        average salary 61000
    ''')
    yield section("Self-referential structs", "link")
    yield snippet("c", r'''
        #include <stdio.h>

        struct Node {
            int value;
            struct Node *next;        /* a pointer to its own type is fine; a Node member is not */
        };

        int main(void) {
            struct Node c = {3, NULL}, b = {2, &c}, a = {1, &b};
            for (struct Node *n = &a; n != NULL; n = n->next) printf("%d -> ", n->value);
            printf("NULL\n");
            return 0;
        }
    ''', out="1 -> 2 -> 3 -> NULL")
    yield section("Flexible array member (C99)", "arrows-horizontal")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        typedef struct {
            size_t len;
            char data[];               /* flexible array member: must be last */
        } Buffer;

        int main(void) {
            const char *text = "variable length";
            size_t n = strlen(text) + 1;
            Buffer *b = malloc(sizeof *b + n);   /* header + payload in ONE allocation */
            if (!b) return 1;
            b->len = n - 1;
            memcpy(b->data, text, n);
            printf("%zu: %s (sizeof Buffer = %zu)\n", b->len, b->data, sizeof(Buffer));
            free(b);
            return 0;
        }
    ''', out="15: variable length (sizeof Buffer = 8)")
    yield section("Opaque types: encapsulation in C", "lock")
    yield p("Declaring `struct Stack;` in a header without its body (an *incomplete type*) lets users hold `struct Stack *` but not touch the fields — only functions in `stack.c` can. This is how `FILE` works.")
    yield snippet("c", r'''
        /* stack.h */
        typedef struct Stack Stack;           /* opaque: fields hidden */
        Stack *stack_new(void);
        void   stack_push(Stack *s, int v);
        int    stack_pop(Stack *s);
        void   stack_free(Stack *s);
    ''', caption="C — header of an opaque type (compile-checked)")
    yield qa("What is the difference between . and -> ?",
             "`.` accesses a member of a struct *object*; `->` accesses a member through a *pointer* to a struct. `p->m` is shorthand for `(*p).m`.")
    yield qa("Can you compare two structs with ==?",
             "No — C does not define `==` for structs. Compare members individually. `memcmp` is unreliable because padding bytes have unspecified values (and floating-point `-0.0`/`NaN` compare differently from their bytes).")
    yield qa("Why can't a struct contain a member of its own type?",
             "It would have infinite size. It can contain a *pointer* to its own type, because a pointer has a fixed size — that is how linked lists and trees are built.")


@topic(G, "padding-alignment", "Padding & Alignment", "layout-distribute-horizontal")
def _():
    yield lead("CPUs load data fastest (or only) at addresses that are multiples of its size. The compiler therefore inserts invisible **padding** bytes into structs, so `sizeof` is often larger than the sum of the members.")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stddef.h>

        struct Bad  { char a; int b; char c; };      /* 1 + 3 pad + 4 + 1 + 3 pad */
        struct Good { int b; char a; char c; };      /* 4 + 1 + 1 + 2 pad */

        int main(void) {
            printf("Bad  = %zu bytes\n", sizeof(struct Bad));
            printf("Good = %zu bytes\n", sizeof(struct Good));
            printf("offsets in Bad: a=%zu b=%zu c=%zu\n",
                   offsetof(struct Bad, a), offsetof(struct Bad, b), offsetof(struct Bad, c));
            printf("alignof(int)=%zu alignof(double)=%zu\n", _Alignof(int), _Alignof(double));
            return 0;
        }
    ''', out='''
        Bad  = 12 bytes
        Good = 8 bytes
        offsets in Bad: a=0 b=4 c=8
        alignof(int)=4 alignof(double)=8
    ''')
    yield section("The rules", "ruler-measure")
    yield steps(
        ("Each member is aligned", "A member of type `T` starts at an offset that is a multiple of `_Alignof(T)` — padding is inserted before it if needed."),
        ("The struct is aligned", "The struct’s alignment is the largest alignment of any member."),
        ("Tail padding", "`sizeof` is rounded up to a multiple of the struct’s alignment, so that in an array every element is aligned too."),
        ("Order is kept", "The compiler never reorders members — the first member is always at offset 0."),
    )
    yield table(
        ["Offset", "0", "1", "2", "3", "4–7", "8", "9–11"],
        ["`struct Bad`", "`a`", "pad", "pad", "pad", "`b`", "`c`", "pad"],
    )
    yield section("Minimising padding", "sort-descending")
    yield snippet("c", r'''
        #include <stdio.h>

        struct Messy  { char c1; double d; char c2; int i; short s; };
        struct Sorted { double d; int i; short s; char c1; char c2; };   /* largest first */

        int main(void) {
            printf("%zu %zu\n", sizeof(struct Messy), sizeof(struct Sorted));
            return 0;
        }
    ''', out="32 16")
    yield note("Order members from largest to smallest alignment. With arrays of millions of structs this halves memory use and improves cache behaviour.", "Tip")
    yield section("Packing (compiler extension)", "package")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdint.h>

        struct __attribute__((packed)) Header {     /* GCC/Clang; MSVC uses #pragma pack(1) */
            uint8_t  type;
            uint32_t length;
            uint16_t flags;
        };

        int main(void) {
            printf("packed size = %zu\n", sizeof(struct Header));
            return 0;
        }
    ''', out="packed size = 7")
    yield warn("Packed structs cause misaligned accesses — slower on x86, and a crash on some ARM/RISC CPUs if you take a pointer to a member. For file and network formats prefer reading bytes and assembling fields with shifts or `memcpy`.")
    yield section("Explicit alignment (C11)", "align-box-left-middle")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdalign.h>
        #include <stdint.h>

        struct Cacheline { alignas(64) char data[64]; };   /* avoid false sharing between threads */

        int main(void) {
            alignas(16) float v[4] = {0};
            printf("%zu %zu %d\n", alignof(struct Cacheline), sizeof(struct Cacheline),
                   (int)((uintptr_t)v % 16 == 0));
            return 0;
        }
    ''', out="64 64 1")
    yield qa("What is structure padding and why does it exist?",
             "Unused bytes the compiler inserts between (and after) struct members so that each member sits at an address that is a multiple of its alignment. Aligned loads/stores are a single fast instruction; misaligned ones are slower or fault on some architectures.")
    yield qa("What is sizeof(struct { char c; double d; })?",
             "16 on typical 64-bit platforms: `c` at offset 0, 7 bytes of padding, `d` at offset 8 (aligned to 8), total 16. Reversing the members gives 9 bytes of data rounded up to 16 as well (tail padding).")
    yield qa("How do you find the offset of a member?",
             "`offsetof(type, member)` from `<stddef.h>`. It is used for serialisation, for generic containers and in the Linux kernel’s `container_of` macro to get from a member pointer back to the enclosing struct.")


@topic(G, "unions", "Unions", "circles-relation")
def _():
    yield lead("A `union` is like a struct whose members all share the **same memory**. It is as large as its largest member, and only one member holds a meaningful value at a time.")
    yield snippet("c", r'''
        #include <stdio.h>

        union Value {
            int i;
            float f;
            char bytes[8];
        };

        int main(void) {
            union Value v;
            printf("sizeof = %zu\n", sizeof v);      /* the largest member */
            v.i = 65;
            printf("i = %d\n", v.i);
            v.f = 2.5f;                               /* overwrites the same bytes */
            printf("f = %.1f\n", v.f);
            printf("same address: %d\n", (void *)&v.i == (void *)&v.f);
            return 0;
        }
    ''', out='''
        sizeof = 8
        i = 65
        f = 2.5
        same address: 1
    ''')
    yield section("Tagged unions (sum types)", "tag")
    yield p("Pair a union with an `enum` tag recording which member is active — the C equivalent of a variant or `enum` in Rust:")
    yield snippet("c", r'''
        #include <stdio.h>

        typedef enum { SHAPE_CIRCLE, SHAPE_RECT } ShapeKind;

        typedef struct {
            ShapeKind kind;                 /* the tag */
            union {                         /* anonymous union (C11) */
                struct { double r; } circle;
                struct { double w, h; } rect;
            };
        } Shape;

        double area(const Shape *s) {
            switch (s->kind) {
                case SHAPE_CIRCLE: return 3.14159 * s->circle.r * s->circle.r;
                case SHAPE_RECT:   return s->rect.w * s->rect.h;
            }
            return 0;
        }

        int main(void) {
            Shape shapes[] = {
                {.kind = SHAPE_CIRCLE, .circle = {1.0}},
                {.kind = SHAPE_RECT, .rect = {3, 4}},
            };
            for (int i = 0; i < 2; i++) printf("area = %.2f\n", area(&shapes[i]));
            printf("sizeof(Shape) = %zu\n", sizeof(Shape));
            return 0;
        }
    ''', out='''
        area = 3.14
        area = 12.00
        sizeof(Shape) = 24
    ''')
    yield section("Inspecting bytes and endianness", "binary")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            union { uint32_t word; uint8_t b[4]; } u = {.word = 0x11223344};
            printf("%02X %02X %02X %02X\n", u.b[0], u.b[1], u.b[2], u.b[3]);
            printf("%s-endian\n", u.b[0] == 0x44 ? "little" : "big");
            return 0;
        }
    ''', out='''
        44 33 22 11
        little-endian
    ''')
    yield note("Reading a union member other than the one last written (*type punning*) is allowed in C (it reinterprets the bytes; C++ forbids it). `memcpy` is the portable alternative in both languages.")
    yield table(
        ["", "struct", "union"],
        ["Memory", "Each member has its own storage", "All members overlap"],
        ["`sizeof`", "≥ sum of members (plus padding)", "Largest member (plus padding)"],
        ["Active members", "All at once", "One at a time"],
        ["Use", "Records", "Variants, memory saving, byte views"],
    )
    yield qa("What is the difference between a structure and a union?",
             "In a struct every member has its own storage, so all can hold values simultaneously and the size is at least the sum of the members. In a union all members start at the same address and share storage, so the size is that of the largest member and writing one member overwrites the others.")
    yield qa("How can you check the endianness of a machine?",
             "Store a multi-byte integer such as `1` and inspect its first byte through a `unsigned char *` or a union: if the first byte is `1` the machine is little-endian (x86, ARM in its usual mode), otherwise big-endian.")


@topic(G, "enums", "Enumerations", "list-numbers")
def _():
    yield lead("An `enum` defines a set of named integer constants — readable names for states, options and error codes.")
    yield snippet("c", r'''
        #include <stdio.h>

        enum Weekday { MON, TUE, WED, THU, FRI, SAT, SUN };        /* 0, 1, 2, ... */
        enum Http { OK = 200, CREATED, NOT_FOUND = 404, TEAPOT = 418 };  /* CREATED = 201 */

        static const char *names[] = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"};

        int main(void) {
            enum Weekday d = FRI;
            printf("%d %s\n", d, names[d]);
            printf("%d %d %d\n", OK, CREATED, NOT_FOUND);
            for (enum Weekday w = SAT; w <= SUN; w++) printf("%s ", names[w]);
            printf("\nsizeof(enum Weekday) = %zu\n", sizeof(enum Weekday));
            return 0;
        }
    ''', out='''
        4 Fri
        200 201 404
        Sat Sun
        sizeof(enum Weekday) = 4
    ''')
    yield section("Idioms", "wand")
    yield snippet("c", r'''
        #include <stdio.h>

        /* a trailing COUNT enumerator gives the number of values for free */
        typedef enum { RED, GREEN, BLUE, COLOR_COUNT } Color;

        /* X-macro: one list generates both the enum and its names */
        #define STATES(X) X(IDLE) X(RUNNING) X(DONE)
        #define AS_ENUM(n) n,
        #define AS_NAME(n) #n,
        typedef enum { STATES(AS_ENUM) STATE_COUNT } State;
        static const char *state_names[] = { STATES(AS_NAME) };

        int main(void) {
            int hits[COLOR_COUNT] = {0};
            hits[GREEN]++;
            printf("colors: %d, green hits: %d\n", COLOR_COUNT, hits[GREEN]);
            for (int s = 0; s < STATE_COUNT; s++) printf("%d=%s ", s, state_names[s]);
            printf("\n");
            return 0;
        }
    ''', out='''
        colors: 3, green hits: 1
        0=IDLE 1=RUNNING 2=DONE
    ''')
    yield table(
        ["`enum`", "`#define`"],
        ["Scoped like variables", "Global text substitution"],
        ["Visible in the debugger by name", "Gone after preprocessing"],
        ["Auto-numbering", "Every value by hand"],
        ["`switch` can warn about missing cases", "No checking"],
        ["Only `int` values (C23 allows a fixed underlying type)", "Any value/type (strings, doubles)"],
    )
    yield warn("C enums are *weakly* typed: an `enum` variable is just an integer, and any `int` can be assigned to it without a diagnostic. Enumerator names share one namespace — prefix them (`COLOR_RED`) to avoid clashes.")
    yield qa("What is the default value of the first enumerator, and of the ones after it?",
             "The first is 0 unless given a value; each subsequent enumerator is the previous value + 1. Values can repeat and can be negative.")
    yield qa("What is the size of an enum?",
             "Implementation-defined: an integer type able to represent all enumerators — `int` (4 bytes) on common compilers. C23 lets you fix it: `enum Small : unsigned char { A, B };`.")


@topic(G, "typedef", "typedef", "tag")
def _():
    yield lead("`typedef` creates an *alias* for an existing type — shorter names, clearer intent and a single place to change a type. It never creates a new, distinct type.")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdint.h>

        typedef unsigned long ulong;                 /* shorter name */
        typedef int32_t Meters;                      /* documents intent (still an int32_t) */
        typedef struct { double re, im; } Complex;   /* anonymous struct, used without 'struct' */
        typedef int (*Compare)(int, int);            /* function pointer type */
        typedef char Name[32];                       /* array type */

        int ascending(int a, int b) { return a - b; }

        int main(void) {
            ulong big = 123456789UL;
            Meters height = 8849;
            Complex z = {1.5, -2.0};
            Compare cmp = ascending;
            Name who = "Tenzing";
            printf("%lu %d %.1f%+.1fi %d %s %zu\n", big, height, z.re, z.im, cmp(3, 1), who, sizeof(Name));
            return 0;
        }
    ''', out="123456789 8849 1.5-2.0i 2 Tenzing 32")
    yield section("typedef struct patterns", "packages")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        /* tag + typedef: the tag is needed for the self-reference inside the body */
        typedef struct Node {
            int value;
            struct Node *next;
        } Node;

        int main(void) {
            Node second = {2, NULL};
            Node first = {1, &second};
            struct Node *same = &first;          /* both names work */
            printf("%d %d\n", same->value, first.next->value);
            return 0;
        }
    ''', out="1 2")
    yield section("typedef vs #define", "arrows-diff")
    yield snippet("c", r'''
        #include <stdio.h>

        #define PTR_D int *
        typedef int *PtrT;

        int main(void) {
            int x = 1, y = 2;
            PTR_D a, b;       /* expands to: int *a, b;  -> b is an int! */
            PtrT  c, d;       /* both are int *                         */
            a = &x; b = y;
            c = &x; d = &y;
            printf("%zu %zu %zu %zu\n", sizeof a, sizeof b, sizeof c, sizeof d);
            return 0;
        }
    ''', out="8 4 8 8")
    yield dodont("Use `typedef` for function-pointer types, opaque handles and platform-dependent types (`size_t`, `uint32_t` are typedefs).",
                 "Hide pointers behind typedefs for ordinary data (`typedef struct node *NodePtr;`) — readers lose track of what is a pointer. The Linux kernel style bans most struct typedefs for this reason.")
    yield note("Names ending in `_t` are reserved by POSIX for future system types; in portable code prefer `Name` or `name_type`.")
    yield qa("Does typedef create a new type?",
             "No. It creates an alias: `typedef int Meters;` makes `Meters` and `int` fully interchangeable, with no extra type checking. To get a distinct type in C, wrap the value in a single-member `struct`.")


@topic(G, "bit-fields", "Bit-fields", "toggle-right")
def _():
    yield lead("A bit-field is a struct member with an explicit width in bits. It packs several small values into one integer — flags, compact records, protocol headers.")
    yield snippet("c", r'''
        #include <stdio.h>

        struct Flags {
            unsigned int visible  : 1;
            unsigned int editable : 1;
            unsigned int priority : 3;     /* 0..7 */
            unsigned int reserved : 3;
        };

        struct Date {                      /* day 1-31, month 1-12, year offset 0-127 */
            unsigned int day   : 5;
            unsigned int month : 4;
            unsigned int year  : 7;
        };

        int main(void) {
            struct Flags f = {.visible = 1, .priority = 5};
            f.editable = 1;
            printf("%u %u %u, sizeof = %zu\n", f.visible, f.editable, f.priority, sizeof f);

            f.priority = 9;                /* 9 doesn't fit in 3 bits: stored modulo 8 */
            printf("priority now %u\n", f.priority);

            struct Date d = {29, 9, 26};   /* 2026 as an offset from 2000 */
            printf("%02u/%02u/%u in %zu bytes\n", d.day, d.month, 2000 + d.year, sizeof d);
            return 0;
        }
    ''', out='''
        1 1 5, sizeof = 4
        priority now 1
        29/09/2026 in 4 bytes
    ''', flags=("-Wno-bitfield-constant-conversion",), caption="C — compiled with -Wno-bitfield-constant-conversion to show the truncation")
    yield section("Rules and limits", "list-check")
    yield ul(
        "Allowed types: `unsigned int`, `signed int`, `_Bool` (and others as an extension). Use `unsigned` — the signedness of a plain `int` bit-field is implementation-defined.",
        "You **cannot** take the address of a bit-field (`&f.visible` is an error) or make arrays of them.",
        "Layout (bit order, whether fields straddle storage units, padding) is **implementation-defined** — don’t use bit-fields to match an external binary format portably.",
        "An unnamed field `unsigned : 0;` forces the next field to start in a new storage unit.",
        "Reading/writing a bit-field compiles to load-mask-shift-store — slower than a plain `int`, and not atomic.",
    )
    yield section("Bit-fields vs masks", "arrows-diff")
    yield table(
        ["Bit-fields", "Manual masks (`flags & MASK`)"],
        ["Readable: `f.priority = 5`", "Verbose: `f = (f & ~PRIO_MASK) | (5u << PRIO_SHIFT)`"],
        ["Layout implementation-defined", "Layout exactly what you write"],
        ["Can’t take address, can’t pass a set of flags easily", "Flags combine naturally: `READ | WRITE`"],
        ["Good for in-memory compact records", "Good for hardware registers, file/network formats"],
    )
    yield qa("Can you take the address of a bit-field member?",
             "No. Bit-fields may start in the middle of a byte, and pointers address whole bytes, so `&s.field` is a compile error. `sizeof` can't be applied to a bit-field either.")
    yield qa("What is the size of struct { unsigned a:3; unsigned b:5; }?",
             "Typically 4 bytes: both fields fit into one `unsigned int` storage unit (8 bits used), and the struct is padded to the alignment of `unsigned int`. The exact layout is implementation-defined.")


@topic(G, "type-qualifiers", "Type Qualifiers: const, volatile, restrict", "adjustments")
def _():
    yield lead("Qualifiers add promises about an object: `const` — I won’t write it; `volatile` — it may change behind the compiler’s back; `restrict` — this pointer is the only way to reach that memory.")
    yield table(
        ["Qualifier", "Promise / meaning", "Typical use"],
        ["`const`", "Not modified through this name", "Read-only parameters, lookup tables"],
        ["`volatile`", "Every read and write must really happen, in order — no caching in registers", "Memory-mapped hardware registers, variables changed by signal handlers"],
        ["`restrict` (C99)", "For the pointer’s lifetime, the object is accessed only through it", "`memcpy`, numeric kernels — enables vectorisation"],
        ["`_Atomic` (C11)", "Accesses are atomic", "Lock-free counters shared between threads"],
    )
    yield section("volatile", "activity")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <signal.h>

        static volatile sig_atomic_t stop = 0;    /* changed by a signal handler */

        void on_signal(int sig) { (void)sig; stop = 1; }

        int main(void) {
            signal(SIGINT, on_signal);
            long spins = 0;
            while (!stop) {                        /* volatile: re-read every iteration */
                if (++spins == 1000000) raise(SIGINT);
            }
            printf("stopped after %ld spins\n", spins);
            return 0;
        }
    ''', out="stopped after 1000000 spins")
    yield warn("`volatile` does **not** make code thread-safe: it gives no atomicity and no memory ordering between CPUs. For threads use `_Atomic` / `<stdatomic.h>` or mutexes.")
    yield section("restrict", "arrows-split-2")
    yield snippet("c", r'''
        #include <stdio.h>

        /* the caller promises dst and src do not overlap, so the compiler may vectorise */
        void add_arrays(size_t n, float *restrict dst, const float *restrict src) {
            for (size_t i = 0; i < n; i++) dst[i] += src[i];
        }

        int main(void) {
            float a[4] = {1, 2, 3, 4}, b[4] = {10, 20, 30, 40};
            add_arrays(4, a, b);
            printf("%.0f %.0f %.0f %.0f\n", a[0], a[1], a[2], a[3]);
            return 0;
        }
    ''', out="11 22 33 44")
    yield p("The standard library uses it: `void *memcpy(void *restrict dst, const void *restrict src, size_t n);` — which is precisely why overlapping `memcpy` is undefined and `memmove` (no `restrict`) exists.")
    yield qa("Can a variable be both const and volatile?",
             "Yes — e.g. `const volatile uint32_t *status_reg`: the program must not write it (`const`) but hardware can change it at any time, so every read must go to memory (`volatile`). A read-only hardware status register is the classic example.")
    yield qa("What happens if you break a restrict promise?",
             "Undefined behaviour. The compiler optimised assuming no aliasing (e.g. keeping values in registers or reordering loads), so overlapping pointers can produce wrong results silently.")
