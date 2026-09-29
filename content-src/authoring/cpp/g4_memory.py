from kit import *

G = "Pointers, Arrays & Strings"


@topic(G, "pointers", "Pointers", "pointer")
def _():
    yield lead("A pointer is a variable that holds the *address* of an object. `&x` takes an address, `*p` follows it.")
    yield define("Pointer", "an object of type `T*` whose value is the memory address of a `T` (or `nullptr`). The pointer and the object it points to are separate — each can be `const` independently.")
    yield section("Basics", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            int x = 10;
            int* p = &x;          // p holds x's address
            *p = 20;              // write through the pointer
            std::cout << x << ' ' << *p << ' ' << (p == &x) << '\n';

            int y = 7;
            p = &y;               // re-point to another object
            std::cout << *p << '\n';

            int** pp = &p;        // pointer to pointer
            **pp = 8;
            std::cout << y << ' ' << sizeof(p) << '\n';   // every data pointer is 8 bytes on 64-bit
        }
    ''', out='''
        20 20 1
        7
        8 8
    ''')
    yield table(
        ["Expression", "Meaning"],
        ["`int* p;`", "Declare `p` as pointer to `int` (uninitialised — dangerous)"],
        ["`int* p = nullptr;`", "Null pointer — points to nothing"],
        ["`&x`", "Address of `x`"],
        ["`*p`", "The object `p` points to (dereference)"],
        ["`p->m`", "Member `m` of the pointed-to object = `(*p).m`"],
        ["`p + n`", "Address `n` *elements* further (scaled by `sizeof(T)`)"],
        ["`p[i]`", "`*(p + i)`"],
    )
    yield section("Pointer arithmetic & arrays", "calculator")
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            int arr[5] = {10, 20, 30, 40, 50};
            int* p = arr;                 // array decays to a pointer to its first element
            std::cout << *(p + 2) << ' ' << p[3] << '\n';
            int* end = arr + 5;           // one-past-the-end: may be compared, never dereferenced
            for (int* it = arr; it != end; ++it) std::cout << *it / 10;
            std::cout << '\n' << (end - p) << '\n';   // difference = number of elements (ptrdiff_t)
        }
    ''', out='''
        30 40
        12345
        5
    ''')
    yield section("`nullptr` vs `NULL` vs `0`", "circle-off")
    yield snippet("cpp", r'''
        #include <iostream>
        void f(int)   { std::cout << "f(int)\n"; }
        void f(int*)  { std::cout << "f(int*)\n"; }
        int main() {
            f(0);          // 0 is an int → f(int)
            f(nullptr);    // nullptr has its own type → f(int*)
            int* p = nullptr;
            if (!p) std::cout << "null\n";
        }
    ''', out='''
        f(int)
        f(int*)
        null
    ''')
    yield note("Always use `nullptr` (C++11). `NULL` is a macro for `0` (or `0L`) and picks integer overloads.")
    yield section("Pointer dangers", "alert-triangle")
    yield cards(
        ("Null dereference", "`*p` when `p == nullptr` — crash (undefined behaviour). Check before use.", "circle-off"),
        ("Dangling pointer", "Points to an object that was destroyed (freed heap memory, a local that went out of scope).", "unlink"),
        ("Wild pointer", "Never initialised — holds garbage. Always initialise pointers.", "question-mark"),
        ("Out of bounds", "Arithmetic past the array — reads/writes someone else's memory.", "arrows-maximize"),
    )
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            int* p = nullptr;
            {
                int local = 5;
                p = &local;
            }                         // local destroyed here — p now dangles
            std::cout << *p << '\n';  // AddressSanitizer: stack-use-after-scope
        }
    ''', fails=True, caption="C++ — dangling pointer (ASan catches it)")
    yield section("`const` and pointers", "lock")
    yield table(
        ["Declaration", "Can change `*p`?", "Can change `p`?"],
        ["`int* p`", "Yes", "Yes"],
        ["`const int* p` (= `int const* p`)", "No", "Yes"],
        ["`int* const p`", "Yes", "No"],
        ["`const int* const p`", "No", "No"],
    )
    yield qa("What's the difference between a pointer and a reference?",
             "A pointer is an object holding an address: it can be null, re-pointed, and has its own address; you dereference it explicitly. A reference is an *alias* for an existing object: it must be initialised, can't be null or re-seated, and is used with ordinary syntax. Prefer references for parameters; use pointers when “no object” or re-pointing is needed.")
    yield qa("What is the size of a pointer?",
             "It depends on the platform, not the pointee: 8 bytes on 64-bit systems, 4 on 32-bit. `sizeof(char*) == sizeof(double*)`. (Pointers to members can be larger.)")


@topic(G, "references", "References in Depth", "link")
def _():
    yield lead("A reference is another name for an existing object. C++ has lvalue references (`T&`), const references (`const T&`) and rvalue references (`T&&`).")
    yield section("lvalue references", "link")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            int x = 1;
            int& r = x;          // r is x
            r = 5;
            std::cout << x << ' ' << (&r == &x) << '\n';

            int y = 99;
            r = y;               // NOT re-binding: assigns 99 to x
            std::cout << x << '\n';

            std::vector<int> v{1, 2, 3};
            int& first = v[0];   // reference to an element
            first = 100;
            std::cout << v[0] << '\n';
        }
    ''', out='''
        5 1
        99
        100
    ''')
    yield ul(
        "Must be initialised: `int& r;` is an error.",
        "Can't be null and can't be re-seated to another object.",
        "No “reference to reference”, no arrays of references, no pointers to references.",
    )
    yield section("const references bind to temporaries", "lock")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        std::string makeName() { return "temp"; }
        int main() {
            const std::string& ref = makeName();   // lifetime of the temporary is extended to ref's scope
            const int& n = 42;                     // binds to a materialised temporary
            std::cout << ref << ' ' << n << '\n';
            // std::string& bad = makeName();      // error: non-const lvalue ref can't bind to an rvalue
        }
    ''', out="temp 42")
    yield section("lvalues and rvalues", "category")
    yield define("lvalue", "an expression that names an object with an identity — you can take its address: variables, `*p`, `v[i]`, a function returning `T&`.")
    yield define("rvalue", "a temporary or literal with no persistent identity: `42`, `a + b`, `makeName()`, `std::move(x)`. Rvalue references `T&&` bind only to these — the basis of move semantics.")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <utility>

        void take(const std::string&) { std::cout << "lvalue (or const)\n"; }
        void take(std::string&&)      { std::cout << "rvalue — can steal its guts\n"; }

        int main() {
            std::string s = "hi";
            take(s);                     // lvalue
            take(std::string("tmp"));    // prvalue (temporary)
            take(s + "!");               // result of an expression is a temporary
            take(std::move(s));          // std::move casts s to an rvalue (xvalue)
        }
    ''', out='''
        lvalue (or const)
        rvalue — can steal its guts
        rvalue — can steal its guts
        rvalue — can steal its guts
    ''')
    yield table(
        ["Reference", "Binds to lvalue", "Binds to rvalue", "Typical use"],
        ["`T&`", "Yes", "No", "Modify caller's object"],
        ["`const T&`", "Yes", "Yes", "Read-only parameter, no copy"],
        ["`T&&`", "No", "Yes", "Move constructors, sink parameters"],
        ["`auto&&` / `T&&` in a template", "Yes", "Yes", "Forwarding (“universal”) reference"],
    )
    yield section("Dangling references", "unlink")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v{1, 2, 3};
            int& ref = v[0];
            v.push_back(4);             // may reallocate: ref now refers to freed memory
            std::cout << ref << '\n';   // AddressSanitizer: heap-use-after-free
        }
    ''', fails=True, caption="C++ — reference invalidated by reallocation")
    yield warn("References don't keep objects alive (except the temporary-lifetime-extension case above). Returning a reference to a local, or holding one into a `vector` that grows, is undefined behaviour.")
    yield qa("Can a reference be null?",
             "Not in a valid program. You can *create* one by dereferencing a null pointer (`int& r = *p;`), but that dereference is already undefined behaviour. Code may assume references always refer to an object.")
    yield qa("What does it mean that std::move doesn't move anything?",
             "`std::move(x)` is just a cast to `T&&` — it marks `x` as an rvalue so that overload resolution picks the move constructor/assignment. The actual moving happens in that constructor. After being moved from, `x` is valid but in an unspecified state.")


@topic(G, "arrays-span", "Arrays, std::array & std::span", "brackets")
def _():
    yield lead("C arrays are fixed-size blocks that decay to pointers. `std::array` is the same thing with value semantics and a size; `std::span` is a non-owning view over any contiguous sequence.")
    yield section("C-style arrays", "brackets")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <iterator>

        int main() {
            int a[5] = {1, 2, 3};                 // remaining elements are zero-initialised
            int b[] = {4, 5, 6};                  // size deduced: 3
            int grid[2][3] = {{1, 2, 3}, {4, 5, 6}};

            std::cout << a[3] << ' ' << std::size(b) << ' ' << sizeof(a) / sizeof(a[0]) << '\n';
            std::cout << grid[1][2] << '\n';
            for (int x : b) std::cout << x;       // range-for works: the size is part of the type
            std::cout << '\n';
        }
    ''', out='''
        0 3 5
        6
        456
    ''')
    yield warn("An array passed to a function **decays** to a pointer — `sizeof` inside the function gives the pointer size, and bounds are never checked. Arrays can't be copied or assigned with `=` either.")
    yield section("`std::array<T, N>`", "box")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <array>
        #include <iostream>

        std::array<int, 3> doubled(std::array<int, 3> arr) {   // passed & returned by value — just works
            for (int& x : arr) x *= 2;
            return arr;
        }

        int main() {
            std::array<int, 5> a{5, 3, 9, 1, 7};
            std::sort(a.begin(), a.end());
            std::cout << a.size() << ' ' << a.front() << ' ' << a.back() << '\n';

            auto copy = a;                 // arrays are copyable
            copy[0] = 100;
            std::cout << a[0] << ' ' << (a == copy) << '\n';

            auto d = doubled({1, 2, 3});
            std::cout << d[2] << '\n';

            try {
                std::cout << a.at(10) << '\n';      // bounds-checked access
            } catch (const std::out_of_range& e) {
                std::cout << "out_of_range\n";
            }
        }
    ''', out='''
        5 1 9
        1 0
        6
        out_of_range
    ''')
    yield table(
        ["", "C array `T[N]`", "`std::array<T,N>`", "`std::vector<T>`"],
        ["Size", "Fixed, compile time", "Fixed, compile time", "Dynamic"],
        ["Storage", "Inline (stack/static)", "Inline (stack/static)", "Heap"],
        ["Knows its size", "Only in scope of declaration", "`.size()`", "`.size()`"],
        ["Copy / compare with `=` `==`", "No", "Yes", "Yes"],
        ["Decays to pointer", "Yes", "No (`.data()` if needed)", "No"],
        ["Bounds check", "Never", "`.at()`", "`.at()`"],
    )
    yield section("`std::span` (C++20)", "arrows-horizontal")
    yield p("A `span<T>` is a pointer + length — a cheap *view*. Write one function that accepts a C array, `std::array` or `std::vector`:")
    yield snippet("cpp", r'''
        #include <array>
        #include <iostream>
        #include <span>
        #include <vector>

        int sum(std::span<const int> xs) {
            int s = 0;
            for (int x : xs) s += x;
            return s;
        }

        int main() {
            int raw[] = {1, 2, 3};
            std::array<int, 2> arr{10, 20};
            std::vector<int> vec{100, 200, 300, 400};
            std::cout << sum(raw) << ' ' << sum(arr) << ' ' << sum(vec) << '\n';
            std::span<int> part(vec.data() + 1, 2);        // a sub-range
            part[0] = 0;                                    // writes through to vec
            std::cout << sum(part) << ' ' << vec[1] << ' ' << sum(std::span(vec).first(2)) << '\n';
        }
    ''', out='''
        6 30 1000
        300 0 100
    ''')
    yield warn("Like any view, a `span` doesn't own memory — it dangles if the vector reallocates or is destroyed.")
    yield qa("Why can't you get the size of an array inside a function that receives it?",
             "Because `void f(int arr[])` is really `void f(int* arr)` — the array decayed to a pointer and the length isn't part of a pointer. Pass the size separately, take `std::array<int, N>&`, a template `T (&arr)[N]`, or a `std::span`.")


@topic(G, "dynamic-memory", "Dynamic Memory: new & delete", "database")
def _():
    yield lead("`new` allocates an object on the heap and constructs it; `delete` destroys it and frees the memory. Every `new` needs exactly one matching `delete` — which is why modern C++ hides both inside smart pointers and containers.")
    yield section("Syntax", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        int main() {
            int* n = new int(42);                  // one int
            std::string* s = new std::string("heap");
            int* arr = new int[4]{1, 2, 3, 4};     // array

            std::cout << *n << ' ' << *s << ' ' << s->size() << ' ' << arr[3] << '\n';

            delete n;          // single object → delete
            delete s;
            delete[] arr;      // array → delete[]
            n = nullptr;       // avoid a dangling pointer
        }
    ''', out="42 heap 4 4")
    yield table(
        ["", "`malloc` / `free` (C)", "`new` / `delete` (C++)"],
        ["Constructs/destroys objects", "No — raw bytes", "Yes — calls constructor / destructor"],
        ["Returns", "`void*` (needs a cast in C++)", "Typed `T*`"],
        ["On failure", "Returns `NULL`", "Throws `std::bad_alloc` (or `nullptr` with `new (std::nothrow)`)"],
        ["Size", "You compute bytes", "Computed from the type"],
        ["Can be overloaded", "No", "Yes (`operator new`)"],
    )
    yield section("The classic bugs", "bug")
    yield cards(
        ("Memory leak", "Forgetting `delete` (or an early `return`/exception skipping it). Memory is never reclaimed.", "droplet"),
        ("Double delete", "Deleting the same pointer twice — heap corruption.", "copy-x"),
        ("Use after free", "Using memory after `delete` — a dangling pointer.", "unlink"),
        ("Mismatched forms", "`new[]` with `delete` (or `new` with `delete[]`) — undefined behaviour.", "arrows-diff"),
    )
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            int* p = new int(7);
            delete p;
            std::cout << *p << '\n';   // AddressSanitizer: heap-use-after-free
        }
    ''', fails=True, caption="C++ — use after free")
    yield snippet("cpp", r'''
        int main() {
            int* arr = new int[10];
            delete arr;                // clang -Wall rejects it; at run time ASan reports alloc-dealloc-mismatch
        }
    ''', fails=True, caption="C++ — mismatched delete")
    yield section("Leaks via exceptions — and the fix", "shield-check")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <stdexcept>
        #include <vector>

        void risky(bool fail) {
            // int* buf = new int[100];  ... delete[] buf;  ← leaks if anything in between throws
            auto buf = std::make_unique<int[]>(100);   // freed automatically, even on exceptions
            std::vector<int> better(100);              // or simply use a container
            buf[0] = better[0] = 1;
            if (fail) throw std::runtime_error("boom");
        }

        int main() {
            try { risky(true); } catch (const std::exception& e) { std::cout << "caught " << e.what() << ", no leak\n"; }
        }
    ''', out="caught boom, no leak")
    yield dodont("Use `std::vector`, `std::string`, `std::make_unique`, `std::make_shared` — they own memory and free it in their destructors (RAII).", "Writing `new`/`delete` in application code. If you see a raw `delete`, ask who else might delete or use that pointer.")
    yield section("2-D dynamic arrays", "grid-dots")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            int rows = 3, cols = 4;
            std::vector<std::vector<int>> grid(rows, std::vector<int>(cols, 0));   // no new/delete needed
            grid[2][3] = 9;
            std::vector<int> flat(rows * cols);                                  // one block: faster
            flat[2 * cols + 3] = 9;                                              // row-major index
            std::cout << grid[2][3] << ' ' << flat[11] << '\n';
        }
    ''', out="9 9")
    yield qa("What's the difference between delete and delete[]?",
             "`delete p` destroys one object; `delete[] p` destroys every element of an array allocated with `new T[n]` (the runtime stores the count) and frees the block. Mixing them is undefined behaviour.")
    yield qa("What happens if new fails?",
             "Plain `new` throws `std::bad_alloc`; it never returns null. `new (std::nothrow) T` returns `nullptr` instead. Checking `if (p == nullptr)` after plain `new` is dead code.")


@topic(G, "memory-layout", "Stack, Heap & Object Lifetime", "stack-2")
def _():
    yield lead("Where an object lives decides how long it lives. C++ has four *storage durations*; knowing them is the key to avoiding dangling pointers.")
    yield section("Memory segments of a process", "layout-rows")
    yield table(
        ["Region", "Holds", "Lifetime", "Managed by"],
        ["**Stack**", "Local variables, parameters, return addresses", "Until the enclosing block ends", "Automatic (push/pop)"],
        ["**Heap** (free store)", "Objects from `new` / containers' buffers", "Until `delete`", "You (or RAII owners)"],
        ["**Static / global data**", "Globals, `static` locals & members", "Whole program", "Runtime"],
        ["**Code (text)**", "Machine instructions, string literals (read-only data)", "Whole program", "Loader"],
    )
    yield section("Storage durations", "clock")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>

        struct Tracer {
            std::string name;
            explicit Tracer(std::string n) : name(std::move(n)) { std::cout << "+ " << name << '\n'; }
            ~Tracer() { std::cout << "- " << name << '\n'; }
        };

        Tracer global("static");                 // static: before main, destroyed after main

        void f() {
            static Tracer once("static-local");  // created on first call only
            Tracer local("automatic");           // destroyed at the end of f
        }

        int main() {
            std::cout << "main starts\n";
            f();
            f();
            auto heap = std::make_unique<Tracer>("dynamic");   // lives until its owner lets go
            heap.reset();
            std::cout << "main ends\n";
        }
    ''', out='''
        + static
        main starts
        + static-local
        + automatic
        - automatic
        + automatic
        - automatic
        + dynamic
        - dynamic
        main ends
        - static-local
        - static
    ''')
    yield ul(
        "**Automatic** — block-scoped locals. Destroyed in *reverse order of construction* when the block ends.",
        "**Static** — globals, namespace variables, `static` locals/members. Static locals are initialised on first use (thread-safe since C++11).",
        "**Dynamic** — `new`/`delete`, or owned by smart pointers/containers.",
        "**Thread** — `thread_local` variables: one instance per thread.",
    )
    yield section("Stack vs heap", "scale")
    yield table(
        ["", "Stack", "Heap"],
        ["Allocation speed", "Very fast (move a pointer)", "Slower (allocator bookkeeping)"],
        ["Size limit", "Small (~1–8 MB)", "Large (up to available memory)"],
        ["Lifetime", "Tied to scope", "Explicit / owner-controlled"],
        ["Fragmentation", "None", "Possible"],
        ["Typical failure", "Stack overflow (deep recursion, huge local arrays)", "Leaks, use-after-free"],
    )
    yield warn("`int big[10'000'000];` as a local variable (40 MB) overflows the stack. Use `std::vector<int> big(10'000'000);` — the vector object sits on the stack, its buffer on the heap.")
    yield section("Object size & alignment", "ruler")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Padded  { char a; int b; char c; };    // 1 + 3 pad + 4 + 1 + 3 pad
        struct Ordered { int b; char a; char c; };    // 4 + 1 + 1 + 2 pad
        struct Empty {};
        int main() {
            std::cout << sizeof(Padded) << ' ' << sizeof(Ordered) << ' ' << alignof(int) << ' ' << sizeof(Empty) << '\n';
        }
    ''', out="12 8 4 1")
    yield note("Members are laid out in declaration order with padding to satisfy alignment. Ordering members from largest to smallest often shrinks a struct. An empty class still has size 1 so distinct objects have distinct addresses.")
    yield qa("Why is the stack faster than the heap?",
             "Allocating on the stack is just adjusting the stack pointer, and freeing is automatic at scope exit; the memory is also hot in cache. Heap allocation must find a free block of the right size (and possibly lock for thread safety), then later return it.")
    yield qa("In what order are local objects destroyed?",
             "In reverse order of construction, when control leaves their scope — whether by reaching `}`, `return`, `break`, or an exception unwinding the stack. This deterministic order is what makes RAII reliable.")


@topic(G, "strings", "std::string", "letter-case")
def _():
    yield lead("`std::string` is a growable, owning sequence of `char` with value semantics — copying a string copies its characters. Forget `char*` for text.")
    yield section("Create, combine, access", "code")
    yield snippet("cpp", r'''
        #include <cctype>
        #include <iostream>
        #include <string>

        int main() {
            std::string a = "Hello";
            std::string b(3, '!');              // "!!!"
            std::string c = a + ", world" + b;  // concatenation
            c += '?';
            std::cout << c << ' ' << c.size() << '\n';
            std::cout << c[0] << c.front() << c.back() << ' ' << c.at(4) << '\n';
            std::cout << std::boolalpha << c.empty() << ' ' << (a == "Hello") << ' ' << (a < "Help") << '\n';
            for (char& ch : a) ch = static_cast<char>(std::toupper(static_cast<unsigned char>(ch)));
            std::cout << a << '\n';
        }
    ''', out='''
        Hello, world!!!? 16
        HH? o
        false true true
        HELLO
    ''')
    yield section("Search & modify", "search")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        int main() {
            std::string s = "the quick brown fox";
            std::cout << s.find("quick") << ' ' << s.find('o') << ' ' << s.rfind('o') << '\n';
            if (s.find("cat") == std::string::npos) std::cout << "no cat\n";

            std::cout << s.substr(4, 5) << '|' << s.substr(16) << '\n';   // substr(pos, count)
            s.replace(4, 5, "slow");                                      // replace(pos, count, text)
            s.insert(0, ">> ");
            s.erase(s.size() - 4);                                        // erase from pos to end
            std::cout << s << '\n';
            std::cout << s.starts_with(">>") << s.ends_with("brown") << '\n';  // C++20
        }
    ''', out='''
        4 12 17
        no cat
        quick|fox
        >> the slow brown
        11
    ''')
    yield table(
        ["Operation", "Call", "Notes"],
        ["Length", "`s.size()` / `s.length()`", "O(1)"],
        ["Find", "`s.find(x, pos)`, `rfind`, `find_first_of`", "Returns index or `std::string::npos`"],
        ["Substring", "`s.substr(pos, len)`", "Returns a *new* string (copy)"],
        ["Modify", "`+=`, `push_back`, `pop_back`, `insert`, `erase`, `replace`, `clear`", "Amortised O(1) append"],
        ["Compare", "`==`, `<`, `s.compare(t)`", "Lexicographic"],
        ["Prefix/suffix", "`starts_with`, `ends_with` (C++20), `contains` (C++23)", ""],
        ["C string", "`s.c_str()`", "Null-terminated `const char*` for C APIs"],
    )
    yield section("Numbers ↔ strings", "transform")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        int main() {
            int n = std::stoi("42");
            double d = std::stod("3.5");
            long long big = std::stoll("9000000000");
            std::string s = std::to_string(n + 1) + "/" + std::to_string(big);
            std::cout << n * 2 << ' ' << d * 2 << ' ' << s << '\n';
            std::cout << std::stoi("ff", nullptr, 16) << ' ' << std::stoi("  12abc") << '\n';   // base 16; stops at non-digits
            try { std::cout << std::stoi("abc"); } catch (const std::invalid_argument&) { std::cout << "invalid\n"; }
        }
    ''', out='''
        84 7 43/9000000000
        255 12
        invalid
    ''')
    yield section("Splitting and joining", "separator")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <sstream>
        #include <string>
        #include <vector>

        std::vector<std::string> split(const std::string& s, char delim) {
            std::vector<std::string> parts;
            std::stringstream ss(s);
            std::string item;
            while (std::getline(ss, item, delim)) parts.push_back(item);
            return parts;
        }

        int main() {
            auto parts = split("red,green,,blue", ',');
            std::cout << parts.size() << '\n';
            std::string joined;
            for (std::size_t i = 0; i < parts.size(); ++i) joined += (i ? " | " : "") + parts[i];
            std::cout << joined << '\n';
        }
    ''', out='''
        4
        red | green |  | blue
    ''')
    yield note("Small strings (≈ up to 15–22 chars depending on the library) are stored *inside* the string object — the **small string optimisation (SSO)** — so no heap allocation happens for them.", "SSO")
    yield warn("`s + 'a' + 'b'` is fine, but `\"abc\" + \"def\"` doesn't compile (two pointers), and `\"abc\" + 1` compiles to pointer arithmetic (`\"bc\"`)! Make one side a `std::string`: `std::string(\"abc\") + \"def\"` or `\"abc\"s + \"def\"`.")
    yield qa("What does std::string::npos mean?",
             "It's the largest value of `std::size_t` (`static_cast<size_t>(-1)`). Search functions return it to mean “not found”, and `substr`/`erase` accept it as “until the end”.")
    yield qa("Is std::string null-terminated?",
             "Since C++11, `s.c_str()` and `s.data()` are guaranteed to point to a null-terminated buffer and `s[s.size()]` is `'\\0'`. But a `std::string` may also contain embedded `'\\0'` characters, and `size()` doesn't count the terminator.")


@topic(G, "string-view", "std::string_view", "eye")
def _():
    yield lead("`std::string_view` (C++17) is a read-only, non-owning window onto characters: a pointer plus a length. Passing and slicing it never allocates.")
    yield section("Why use it", "bolt")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <string_view>

        std::size_t countVowels(std::string_view text) {       // accepts literals, std::string, substrings…
            std::size_t n = 0;
            for (char c : text) n += std::string_view("aeiou").find(c) != std::string_view::npos;
            return n;
        }

        int main() {
            std::string s = "education";
            std::cout << countVowels(s) << ' ' << countVowels("sky") << '\n';   // no temporary std::string for "sky"

            std::string_view sv = "  trim me  ";
            sv.remove_prefix(sv.find_first_not_of(' '));
            sv.remove_suffix(sv.size() - sv.find_last_not_of(' ') - 1);
            std::cout << '[' << sv << "] " << sv.substr(0, 4) << '\n';          // substr is O(1): no copy
        }
    ''', out='''
        5 0
        [trim me] trim
    ''')
    yield table(
        ["", "`const std::string&`", "`std::string_view`"],
        ["Pass a literal `\"abc\"`", "Creates a temporary `std::string` (may allocate)", "No allocation"],
        ["`substr`", "Copies → new string", "O(1), shares the characters"],
        ["Owns data", "The referred string does", "**Never**"],
        ["Null-terminated", "Yes (`c_str()`)", "**Not guaranteed**"],
        ["Can modify chars", "No (const)", "No"],
    )
    yield section("The dangling trap", "unlink")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <string_view>

        std::string makeGreeting() { return std::string(40, 'x'); }

        int main() {
            std::string_view sv = makeGreeting();   // view into a temporary that dies at the ';'
            std::cout << sv << '\n';                // clang warns (-Wdangling-gsl); at run time: use-after-free
        }
    ''', fails=True, caption="C++ — view outliving its string")
    yield warn("A `string_view` must never outlive the characters it views. Don't return one pointing into a local `std::string`, and don't store one in a long-lived object unless you control the owner's lifetime.")
    yield dodont("Use `std::string_view` for read-only *parameters* and short-lived parsing.", "Storing `string_view` members or returning views into temporaries; passing `sv.data()` to a C API that expects a null-terminated string.")
    yield qa("When should a function take std::string by value instead of string_view?",
             "When it will *keep* a copy (e.g. a constructor storing a name): take `std::string` by value and `std::move` it into the member. Callers with temporaries then pay only a move. `string_view` is for functions that only read during the call.")
