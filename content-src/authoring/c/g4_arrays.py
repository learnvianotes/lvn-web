from kit import *

G = "Arrays & Strings"


@topic(G, "arrays", "Arrays", "brackets")
def _():
    yield lead("An array is a fixed-size block of *contiguous* elements of one type, indexed from 0. C never checks the index — staying in bounds is your job.")
    yield section("Declaring and initialising", "pencil")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[5] = {10, 20, 30, 40, 50};
            int b[5] = {1, 2};              /* rest are zero: 1 2 0 0 0 */
            int c[] = {7, 8, 9};            /* size deduced: 3 */
            int d[5] = {0};                 /* all zeros */
            int e[6] = {[2] = 5, [4] = 9};  /* designated initializers (C99) */

            size_t n = sizeof a / sizeof a[0];     /* element count */
            printf("n=%zu sizeof(c)=%zu\n", n, sizeof c);
            for (int i = 0; i < 5; i++) printf("%d ", b[i]);
            printf("| %d | ", d[3]);
            for (int i = 0; i < 6; i++) printf("%d ", e[i]);
            printf("\n");
            return 0;
        }
    ''', out='''
        n=5 sizeof(c)=12
        1 2 0 0 0 | 0 | 0 0 5 0 9 0
    ''')
    yield note("`sizeof arr / sizeof arr[0]` gives the element count — but **only** where `arr` is a real array. Inside a function that received it as a parameter, `arr` is a pointer and the trick silently returns 2 (8 / 4).")
    yield section("Memory layout", "layout-columns")
    yield table(
        ["Index", "0", "1", "2", "3", "4"],
        ["Value", "10", "20", "30", "40", "50"],
        ["Offset (bytes)", "0", "4", "8", "12", "16"],
    )
    yield p("`a[i]` is defined as `*(a + i)`: start address plus `i × sizeof(int)`. That is why indexing is O(1) — and why an index past the end silently reads whatever lies next in memory.")
    yield section("Passing arrays to functions", "arrow-right")
    yield snippet("c", r'''
        #include <stdio.h>

        /* the array decays to a pointer: the size must travel separately */
        int max_of(const int arr[], size_t n) {
            int best = arr[0];
            for (size_t i = 1; i < n; i++)
                if (arr[i] > best) best = arr[i];
            return best;
        }

        void double_all(int *arr, size_t n) {     /* same as int arr[] */
            for (size_t i = 0; i < n; i++) arr[i] *= 2;
        }

        int main(void) {
            int v[] = {3, 9, 2, 7};
            size_t n = sizeof v / sizeof v[0];
            double_all(v, n);                      /* modifies the caller's array */
            printf("max = %d, v[0] = %d\n", max_of(v, n), v[0]);
            return 0;
        }
    ''', out="max = 18, v[0] = 6")
    yield section("Common array algorithms", "list-search")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {4, -1, 7, 3, 7, 0};
            int n = sizeof a / sizeof a[0];

            int sum = 0, maxi = 0;
            for (int i = 0; i < n; i++) {
                sum += a[i];
                if (a[i] > a[maxi]) maxi = i;
            }
            printf("sum=%d max=%d at %d\n", sum, a[maxi], maxi);

            /* linear search */
            int key = 3, pos = -1;
            for (int i = 0; i < n; i++) if (a[i] == key) { pos = i; break; }
            printf("3 found at %d\n", pos);

            /* rotate left by one */
            int first = a[0];
            for (int i = 0; i < n - 1; i++) a[i] = a[i + 1];
            a[n - 1] = first;
            for (int i = 0; i < n; i++) printf("%d ", a[i]);
            printf("\n");
            return 0;
        }
    ''', out='''
        sum=20 max=7 at 2
        3 found at 3
        -1 7 3 7 0 4
    ''')
    yield section("Variable-length arrays (C99)", "arrows-horizontal")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int n = 4;
            int squares[n];                   /* size known only at run time: VLA on the stack */
            for (int i = 0; i < n; i++) squares[i] = i * i;
            printf("%d %zu\n", squares[3], sizeof squares);
            return 0;
        }
    ''', out="9 16")
    yield warn("VLAs live on the stack: a large or attacker-controlled size overflows the stack with no error reported. They became *optional* in C11, and the Linux kernel bans them. Prefer `malloc` for run-time sizes.")
    yield section("Out of bounds is undefined behaviour", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int a[5] = {1, 2, 3, 4, 5};
            int sum = 0;
            for (int i = 0; i <= 5; i++)    /* off by one: touches a[5] */
                sum += a[i];
            printf("%d\n", sum);
            return 0;
        }
    ''', fails=True, caption="C — caught by the sanitizer")
    yield output("main.c:7:16: runtime error: index 5 out of bounds for type 'int[5]'", "UBSan")
    yield dodont("Keep the length next to the pointer (`const int *a, size_t n`), and loop with `i < n`.",
                 "Rely on a sentinel you never wrote, or on `sizeof` of a parameter.")
    yield qa("Why can't you assign one array to another with =?",
             "An array is not a modifiable lvalue: in most expressions its name decays to a pointer to its first element, so `a = b` would mean assigning to an address. Copy element by element or with `memcpy(a, b, sizeof a)`. (Wrapping an array in a `struct` makes it copyable by assignment.)")
    yield qa("What is array decay?",
             "In almost every expression, an array of `T` is converted to a pointer to its first element (`T *`). The exceptions are `sizeof arr`, `&arr` and a string literal used to initialise a `char` array. Decay is why functions cannot know an array's length.")


@topic(G, "multi-dimensional-arrays", "Multi-dimensional Arrays", "table")
def _():
    yield lead("A 2-D array in C is an *array of arrays*, stored **row by row** (row-major) in one contiguous block.")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int m[2][3] = {
                {1, 2, 3},
                {4, 5, 6},
            };
            for (int r = 0; r < 2; r++) {
                for (int c = 0; c < 3; c++) printf("%d ", m[r][c]);
                printf("\n");
            }
            printf("sizeof m = %zu, sizeof m[0] = %zu\n", sizeof m, sizeof m[0]);

            int *flat = &m[0][0];               /* row-major: rows are laid end to end */
            for (int i = 0; i < 6; i++) printf("%d ", flat[i]);
            printf("\n");
            return 0;
        }
    ''', out='''
        1 2 3
        4 5 6
        sizeof m = 24, sizeof m[0] = 12
        1 2 3 4 5 6
    ''')
    yield formula("address of `m[r][c]` = base + (r × COLS + c) × sizeof(element)")
    yield section("Passing a 2-D array to a function", "arrow-right")
    yield p("All dimensions except the first must be known to the function, because the compiler needs the row length to compute `m[r][c]`.")
    yield snippet("c", r'''
        #include <stdio.h>

        #define COLS 3

        int trace_like_sum(int m[][COLS], int rows) {        /* fixed column count */
            int s = 0;
            for (int r = 0; r < rows; r++)
                for (int c = 0; c < COLS; c++) s += m[r][c];
            return s;
        }

        void print_matrix(int rows, int cols, int m[rows][cols]) {   /* C99 VLA parameter */
            for (int r = 0; r < rows; r++) {
                for (int c = 0; c < cols; c++) printf("%3d", m[r][c]);
                printf("\n");
            }
        }

        int main(void) {
            int a[2][COLS] = {{1, 2, 3}, {4, 5, 6}};
            printf("sum = %d\n", trace_like_sum(a, 2));
            print_matrix(2, COLS, a);
            return 0;
        }
    ''', out='''
        sum = 21
          1  2  3
          4  5  6
    ''')
    yield section("Matrix multiplication", "math-x-plus-x")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            int A[2][3] = {{1, 2, 3}, {4, 5, 6}};
            int B[3][2] = {{7, 8}, {9, 10}, {11, 12}};
            int C[2][2] = {{0}};
            for (int i = 0; i < 2; i++)
                for (int j = 0; j < 2; j++)
                    for (int k = 0; k < 3; k++)
                        C[i][j] += A[i][k] * B[k][j];
            printf("%d %d\n%d %d\n", C[0][0], C[0][1], C[1][0], C[1][1]);
            return 0;
        }
    ''', out='''
        58 64
        139 154
    ''')
    yield section("Arrays of strings", "list-letters")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            char names[3][8] = {"Ann", "Bob", "Charlie"};    /* 2-D char array: 24 bytes */
            const char *langs[] = {"C", "Go", "Rust"};       /* array of pointers */
            for (int i = 0; i < 3; i++) printf("%s/%s ", names[i], langs[i]);
            printf("\n%zu %zu\n", sizeof names, sizeof langs);
            return 0;
        }
    ''', out='''
        Ann/C Bob/Go Charlie/Rust
        24 24
    ''')
    yield table(
        ["`char names[3][8]`", "`const char *langs[3]`"],
        ["3 × 8 bytes, each row a writable copy", "3 pointers to string literals (read-only)"],
        ["Rows have a fixed maximum length", "Each string can have any length"],
        ["Wastes space for short strings", "Only pointer overhead"],
    )
    yield note("Iterate row by row (`for r … for c …`) — row-major order visits memory sequentially and is cache-friendly. Swapping the loops on a big matrix can be several times slower.", "Performance")
    yield qa("How is int a[3][4] laid out in memory?",
             "As 12 consecutive `int`s: row 0 (4 ints), then row 1, then row 2. `a[i]` is an `int[4]` array, `a` decays to `int (*)[4]` (pointer to a row), and `a[i][j]` is `*(*(a + i) + j)`.")
    yield qa("Why must a function parameter for a 2-D array specify the column count?",
             "To compute the address of `m[r][c]` the compiler needs the length of each row (`r × COLS + c`). The first dimension is not needed because the parameter is really a pointer to a row.")


@topic(G, "strings", "Strings in C", "quote")
def _():
    yield lead("C has no string type. A string is an array of `char` terminated by a **NUL byte** `'\\0'` — every string function walks the bytes until it finds that terminator.")
    yield section("Arrays vs pointers to literals", "arrows-diff")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s1[] = "hello";            /* array of 6 bytes (a writable copy) */
            char s2[10] = "hi";             /* rest zero-filled */
            const char *s3 = "world";       /* pointer to a read-only literal */

            s1[0] = 'H';                    /* fine: s1 is our own array */
            printf("%s %s %s\n", s1, s2, s3);
            printf("sizeof: %zu %zu %zu\n", sizeof s1, sizeof s2, sizeof s3);
            printf("strlen: %zu %zu %zu\n", strlen(s1), strlen(s2), strlen(s3));
            return 0;
        }
    ''', out='''
        Hello hi world
        sizeof: 6 10 8
        strlen: 5 2 5
    ''')
    yield table(
        ["", "`char s[] = \"hello\";`", "`const char *p = \"hello\";`"],
        ["What it is", "Array of 6 `char`, initialised from the literal", "Pointer to a literal stored in read-only memory"],
        ["Modifiable?", "Yes", "**No** — writing is undefined behaviour (usually a crash)"],
        ["`sizeof`", "6 (includes `\\0`)", "8 (size of a pointer)"],
        ["Reassignable?", "No (`s = \"x\"` is an error)", "Yes (`p = \"x\"` points elsewhere)"],
    )
    yield section("The terminator is everything", "circle-dot")
    yield snippet("c", r'''
        #include <stdio.h>

        int main(void) {
            char word[] = {'c', 'a', 't', '\0'};    /* same as "cat" */
            printf("%s\n", word);
            word[1] = '\0';                         /* cut the string short */
            printf("%s\n", word);
            for (int i = 0; i < 4; i++) printf("%d ", word[i]);
            printf("\n");
            return 0;
        }
    ''', out='''
        cat
        c
        99 0 116 0
    ''')
    yield section("Writing string functions yourself", "code")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <ctype.h>

        size_t my_strlen(const char *s) {
            const char *p = s;
            while (*p) p++;
            return (size_t)(p - s);
        }

        void reverse(char *s) {
            size_t n = my_strlen(s);
            for (size_t i = 0, j = n ? n - 1 : 0; i < j; i++, j--) {
                char t = s[i]; s[i] = s[j]; s[j] = t;
            }
        }

        int is_palindrome(const char *s) {
            size_t i = 0, j = my_strlen(s);
            while (i < j) {
                if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j - 1])) return 0;
                i++; j--;
            }
            return 1;
        }

        int count_words(const char *s) {
            int words = 0, in_word = 0;
            for (; *s; s++) {
                if (isspace((unsigned char)*s)) in_word = 0;
                else if (!in_word) { in_word = 1; words++; }
            }
            return words;
        }

        int main(void) {
            char buf[] = "stressed";
            reverse(buf);
            printf("%s %zu\n", buf, my_strlen(buf));
            printf("%d %d\n", is_palindrome("Racecar"), is_palindrome("hello"));
            printf("%d\n", count_words("  the quick  brown fox "));
            return 0;
        }
    ''', out='''
        desserts 8
        1 0
        4
    ''')
    yield section("Converting between strings and numbers", "transform")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            char *end;
            long n = strtol("  1234xyz", &end, 10);       /* stops at the first non-digit */
            printf("%ld, rest = \"%s\"\n", n, end);
            printf("%ld %ld\n", strtol("ff", NULL, 16), strtol("101", NULL, 2));
            printf("%.2f\n", strtod("3.14159", NULL));
            printf("%d\n", atoi("42"));                   /* no error reporting at all */

            char out[32];
            int len = snprintf(out, sizeof out, "%d-%s-%.1f", 7, "ab", 2.5);
            printf("%s (%d chars)\n", out, len);
            return 0;
        }
    ''', out='''
        1234, rest = "xyz"
        255 5
        3.14
        42
        7-ab-2.5 (8 chars)
    ''')
    yield note("Prefer `strtol` / `strtod` over `atoi` / `atof`: they report where parsing stopped and set `errno` to `ERANGE` on overflow. Use `snprintf` (never `sprintf`) to build strings safely.")
    yield section("Pitfalls", "alert-triangle")
    yield snippet("c", r'''
        int main(void) {
            char *s = "hello";      /* legal in C (not C++), but the literal is read-only */
            s[0] = 'H';             /* undefined behaviour: crashes on most systems */
            return 0;
        }
    ''', fails=True, caption="C — writing to a string literal (bus error / segfault at run time)")
    yield ul(
        "Forgetting room for `'\\0'`: `char s[5] = \"hello\";` compiles in C but has no terminator.",
        "Comparing with `==` compares *addresses* — use `strcmp`.",
        "Returning a pointer to a local `char` array from a function (it dies on return).",
        "Passing a plain `char` (possibly negative) to `isalpha` / `toupper` — cast to `unsigned char` first.",
    )
    yield qa("What is the difference between char s[] = \"abc\" and char *s = \"abc\"?",
             "The first creates a 4-byte array on the stack (or in `.data`) initialised with a copy of the literal — you can modify it. The second creates a pointer to the literal itself, which lives in read-only memory; modifying it is undefined behaviour. `sizeof` gives 4 vs 8.")
    yield qa("How is the length of a C string determined?",
             "By scanning for the NUL terminator — `strlen` is O(n). The length is not stored anywhere, which is why repeated `strlen` calls in a loop condition (`for (i = 0; i < strlen(s); i++)`) make a loop O(n²).")


@topic(G, "string-functions", "string.h Functions", "text-caption")
def _():
    yield lead("`<string.h>` provides string (`str…`) and raw memory (`mem…`) functions. None of them allocate memory or check destination sizes — you supply buffers big enough.")
    yield table(
        ["Function", "Does", "Notes"],
        ["`strlen(s)`", "Length excluding `\\0`", "O(n)"],
        ["`strcpy(d, s)` / `strncpy(d, s, n)`", "Copy", "`strcpy` overflows if `d` is too small; `strncpy` may **not** NUL-terminate"],
        ["`strcat(d, s)` / `strncat(d, s, n)`", "Append", "`strncat` always terminates; `n` = max chars to append"],
        ["`strcmp(a, b)` / `strncmp`", "Compare", "<0, 0, >0 — not just −1/0/1"],
        ["`strchr(s, c)` / `strrchr`", "First / last occurrence of a char", "Returns pointer or `NULL`"],
        ["`strstr(h, n)`", "Find substring", "Pointer or `NULL`"],
        ["`strspn` / `strcspn`", "Length of prefix made of / not made of a set", "`s[strcspn(s, \"\\n\")] = 0` strips a newline"],
        ["`strtok(s, delims)`", "Split into tokens", "Modifies `s`, keeps hidden static state — not reentrant"],
        ["`memcpy(d, s, n)`", "Copy `n` bytes", "Regions must **not** overlap"],
        ["`memmove(d, s, n)`", "Copy `n` bytes", "Overlap-safe"],
        ["`memset(p, byte, n)`", "Fill bytes", "Sets *bytes*, not ints"],
        ["`memcmp(a, b, n)`", "Compare bytes", "Don’t use on structs (padding bytes)"],
    )
    yield section("Copy, concatenate, compare", "copy")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char buf[32];
            strcpy(buf, "Hello");
            strcat(buf, ", ");
            strncat(buf, "world!!!", 6);          /* append at most 6 chars */
            printf("%s (%zu)\n", buf, strlen(buf));

            printf("%d %d %d\n", strcmp("apple", "apple") == 0,
                   strcmp("apple", "banana") < 0, strcmp("b", "a") > 0);
            printf("%d\n", strncmp("prefix-match", "prefix-other", 6) == 0);
            return 0;
        }
    ''', out='''
        Hello, world! (13)
        1 1 1
        1
    ''')
    yield section("Searching", "search")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *path = "/usr/local/bin/gcc";
            const char *slash = strrchr(path, '/');
            printf("file: %s\n", slash + 1);
            printf("dir length: %td\n", slash - path);

            const char *hit = strstr(path, "local");
            printf("found \"local\" at index %td\n", hit - path);
            printf("%s\n", strchr(path, 'z') == NULL ? "no z" : "has z");
            printf("vowel-free prefix of \"strength\": %zu\n", strcspn("strength", "aeiou"));
            return 0;
        }
    ''', out='''
        file: gcc
        dir length: 14
        found "local" at index 5
        no z
        vowel-free prefix of "strength": 3
    ''')
    yield section("Tokenising with strtok", "cut")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char csv[] = "name,,age;city";              /* must be writable */
            for (char *tok = strtok(csv, ",;"); tok; tok = strtok(NULL, ",;"))
                printf("[%s] ", tok);                    /* empty fields are skipped */
            printf("\n");
            return 0;
        }
    ''', out="[name] [age] [city]")
    yield section("Memory functions", "cpu")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            int a[5] = {1, 2, 3, 4, 5}, b[5];
            memcpy(b, a, sizeof a);                  /* copy the whole array */

            memmove(a + 1, a, 3 * sizeof a[0]);      /* overlapping shift right */
            for (int i = 0; i < 5; i++) printf("%d ", a[i]);
            printf("\n");

            memset(b, 0, sizeof b);                  /* zero is safe for any type */
            printf("%d %d\n", b[0], b[4]);

            int ones[2];
            memset(ones, 1, sizeof ones);            /* sets BYTES to 1: 0x01010101 */
            printf("%d\n", ones[0]);
            return 0;
        }
    ''', out='''
        1 1 2 3 5
        0 0
        16843009
    ''')
    yield section("Buffer overflow with strcpy", "alert-triangle")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char small[8];
            const char *input = "this is far too long";
            strcpy(small, input);          /* writes 21 bytes into 8 */
            printf("%s\n", small);
            return 0;
        }
    ''', fails=True, caption="C — stack-buffer-overflow caught by AddressSanitizer")
    yield snippet("c", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char small[8];
            const char *input = "this is far too long";
            snprintf(small, sizeof small, "%s", input);   /* truncates, always terminates */
            printf("%s\n", small);
            return 0;
        }
    ''', out="this is", caption="C — the safe version")
    yield warn("`strncpy(d, s, n)` does **not** add `'\\0'` when `s` has `n` or more characters, and it pads with zeros otherwise. Prefer `snprintf(d, size, \"%s\", s)` or set `d[n - 1] = '\\0'` yourself.")
    yield qa("What is the difference between memcpy and memmove?",
             "Both copy `n` bytes. `memcpy` assumes the source and destination do not overlap (undefined behaviour if they do), so it can copy in any order and is slightly faster. `memmove` handles overlap correctly, as if copying through a temporary buffer.")
    yield qa("Why is strtok considered unsafe?",
             "It modifies the input string (writes `\\0` over delimiters), cannot be used on string literals, and keeps a hidden static pointer between calls — so it is not thread-safe and you cannot tokenise two strings at once. POSIX `strtok_r` takes the state as a parameter.")
