from kit import *

G = "Modern C++ & Interview Prep"


@topic(G, "modern-cpp-tour", "Modern C++ Feature Tour (11 → 23)", "rocket")
def _():
    yield lead("A quick map of what each standard added, with the features you'll actually use and be asked about.")
    yield section("C++11 — the big one", "number-11")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <unordered_map>
        #include <vector>

        enum class Color { Red, Green };                             // scoped enums

        int main() {
            auto v = std::vector<int>{1, 2, 3};                      // auto + brace init
            for (auto x : v) std::cout << x;                         // range-for
            std::cout << '\n';
            auto p = std::shared_ptr<int>(new int(7));               // smart pointers
            std::unordered_map<int, int> m{{1, 1}};                  // hash containers
            int* none = nullptr;                                     // nullptr
            auto sq = [](int x) { return x * x; };                   // lambdas
            static_assert(sizeof(int) >= 4);                         // static_assert
            constexpr int k = 3;                                     // constexpr
            std::vector<std::unique_ptr<int>> owners;
            owners.push_back(std::make_unique<int>(1));              // move semantics (make_unique is C++14)
            std::cout << *p + sq(k) + m[1] + (none == nullptr) + *owners[0] << '\n';
            Color c = Color::Green;
            std::cout << static_cast<int>(c) << '\n';
        }
    ''', out='''
        123
        19
        1
    ''')
    yield table(
        ["Standard", "Language", "Library"],
        ["**C++11**", "`auto`, `decltype`, lambdas, rvalue refs & move, `nullptr`, `constexpr`, range-for, `enum class`, `override`/`final`, variadic templates, `= default`/`= delete`, uniform init, `noexcept`", "`unique_ptr`/`shared_ptr`, `unordered_*`, `thread`/`mutex`/`atomic`, `chrono`, `random`, `tuple`, `array`, `function`"],
        ["**C++14**", "Generic lambdas, return-type deduction, relaxed `constexpr`, binary literals, digit separators `1'000`", "`make_unique`, `std::exchange`"],
        ["**C++17**", "Structured bindings, `if constexpr`, `if (init; cond)`, fold expressions, CTAD, inline variables, guaranteed copy elision, nested namespaces", "`optional`, `variant`, `any`, `string_view`, `filesystem`, parallel algorithms, `gcd`/`lcm`"],
        ["**C++20**", "Concepts, `<=>`, designated initialisers, `consteval`/`constinit`, coroutines, modules, `using enum`, lambda templates", "Ranges, `format`, `span`, `jthread`, `stop_token`, `latch`/`barrier`/`semaphore`, calendar & time zones, `contains()`, `starts_with()`"],
        ["**C++23**", "Deducing `this`, `if consteval`, multidimensional `operator[]`, `auto(x)` decay copy", "`print`/`println`, `expected`, `ranges::to`, `views::zip/enumerate/chunk`, `flat_map`, `mdspan`, `stacktrace`"],
    )
    yield section("C++17 & C++20 in one program", "sparkles")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <compare>
        #include <concepts>
        #include <format>
        #include <iostream>
        #include <map>
        #include <optional>
        #include <ranges>
        #include <span>
        #include <string>
        #include <vector>

        struct Version {
            int major{}, minor{};
            auto operator<=>(const Version&) const = default;           // C++20 spaceship
        };

        std::optional<int> parse(std::string_view s) {                 // C++17 optional + string_view
            int n = 0;
            for (char c : s) { if (c < '0' || c > '9') return std::nullopt; n = n * 10 + (c - '0'); }
            return n;
        }

        std::integral auto total(std::span<const int> xs) {            // C++20 concepts + span
            int s = 0;
            for (int x : xs) s += x;
            return s;
        }

        int main() {
            std::map<std::string, Version> deps{{"fmt", {.major = 10, .minor = 1}}, {"boost", {1, 84}}};  // designated init
            for (const auto& [name, ver] : deps)                                                          // structured bindings
                std::cout << std::format("{:<6}{}.{}\n", name, ver.major, ver.minor);                     // std::format
            std::cout << (Version{1, 84} < Version{10, 1}) << '\n';

            std::vector<int> nums{5, 3, 8};
            std::ranges::sort(nums);                                                                      // ranges
            if (auto n = parse("42"); n) std::cout << *n + total(nums) << '\n';                           // if-init
            std::cout << deps.contains("fmt") << '\n';
        }
    ''', out='''
        boost 1.84
        fmt   10.1
        1
        58
        1
    ''')
    yield section("Features to know by name", "list")
    yield cards(
        ("Coroutines (C++20)", "Functions that can suspend (`co_await`, `co_yield`, `co_return`). The language provides the machinery; you need a library type (e.g. C++23 `std::generator`) to use them comfortably.", "player-pause"),
        ("Modules (C++20)", "`import std;` / `export module math;` replace textual `#include`: faster builds, no macro leakage. Toolchain support is still maturing.", "packages"),
        ("`std::expected` (C++23)", "Return a value *or* an error without exceptions: `std::expected<int, std::string> parse(...)`.", "circle-check"),
        ("Deducing `this` (C++23)", "`void f(this auto& self)` — one member function for const/non-const, recursive lambdas, CRTP without templates.", "arrow-back-up"),
    )
    yield qa("What were the most important changes in C++11?",
             "Move semantics and rvalue references (cheap transfers of resources), smart pointers (safe ownership), lambdas, `auto`, range-based for, a memory model with `std::thread`/atomics, `nullptr`, `constexpr`, `enum class`, `override`/`final` and variadic templates. Together they made “modern C++” — code without manual `new`/`delete`.")


@topic(G, "competitive-programming", "Competitive Programming & Fast I/O", "trophy")
def _():
    yield lead("C++ dominates contests because of speed and the STL. A few habits — fast I/O, `long long`, the right container — prevent most wrong answers and time-limit errors.")
    yield section("The template", "template")
    yield snippet("cpp", r'''
        #include <bits/stdc++.h>          // GCC-only “everything” header; clang/MSVC: include what you use
        using namespace std;
        using ll = long long;

        int main() {
            ios::sync_with_stdio(false);   // don't sync C++ streams with C stdio
            cin.tie(nullptr);              // don't flush cout before every cin

            int t;
            cin >> t;
            while (t--) {
                int n;
                cin >> n;
                vector<ll> a(n);
                for (auto& x : a) cin >> x;
                ll best = *max_element(a.begin(), a.end());
                ll sum = accumulate(a.begin(), a.end(), 0LL);
                cout << best << ' ' << sum << '\n';     // '\n', never endl in hot loops
            }
        }
    ''', run=False, caption="C++ — contest template (GCC)")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <numeric>
        #include <vector>
        using namespace std;
        using ll = long long;

        int main() {
            ios::sync_with_stdio(false);
            cin.tie(nullptr);
            int t;
            cin >> t;
            while (t--) {
                int n;
                cin >> n;
                vector<ll> a(n);
                for (auto& x : a) cin >> x;
                cout << *max_element(a.begin(), a.end()) << ' ' << accumulate(a.begin(), a.end(), 0LL) << '\n';
            }
        }
    ''', stdin="2\n3\n1 5 2\n2\n1000000000 1000000000\n", out='''
        5 8
        1000000000 2000000000
    ''', caption="C++ — the same, portable")
    yield note("`<bits/stdc++.h>` exists only in GCC's libstdc++ (the usual contest compiler); it doesn't exist with clang/libc++ on macOS. Include the real headers when you're not on a judge.", "Portability")
    yield section("Habits that save you", "checklist")
    yield table(
        ["Trap", "Fix"],
        ["`int` overflow (sums, products > 2·10⁹)", "`long long` (`ll`) everywhere sums live; `1LL * a * b`"],
        ["Slow I/O with 10⁶ numbers", "`sync_with_stdio(false)` + `cin.tie(nullptr)`, `'\\n'` instead of `endl`"],
        ["`unordered_map` hacked with collisions", "Custom hash with a random seed, or `map`"],
        ["Recursion depth 10⁵–10⁶", "Iterative DFS with an explicit stack"],
        ["Large local arrays → stack overflow", "Global arrays or `vector`"],
        ["Comparing doubles", "Use an epsilon, or stay in integers"],
        ["`v.size() - 1` when empty", "Cast: `(int)v.size() - 1`"],
        ["Modular arithmetic", "`(a % M + M) % M` for negatives; multiply in `long long`"],
    )
    yield section("Handy snippets", "code")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <bit>
        #include <iostream>
        #include <numeric>
        #include <vector>
        using ll = long long;
        constexpr ll MOD = 1'000'000'007;

        ll power(ll base, ll exp, ll mod) {                  // fast modular exponentiation
            ll result = 1;
            base %= mod;
            while (exp > 0) {
                if (exp & 1) result = result * base % mod;
                base = base * base % mod;
                exp >>= 1;
            }
            return result;
        }

        std::vector<int> sieve(int n) {                      // primes up to n
            std::vector<bool> composite(n + 1);
            std::vector<int> primes;
            for (int i = 2; i <= n; ++i) {
                if (composite[i]) continue;
                primes.push_back(i);
                for (ll j = 1LL * i * i; j <= n; j += i) composite[j] = true;
            }
            return primes;
        }

        struct DSU {                                         // union–find
            std::vector<int> parent, size;
            explicit DSU(int n) : parent(n), size(n, 1) { std::iota(parent.begin(), parent.end(), 0); }
            int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }
            bool unite(int a, int b) {
                a = find(a); b = find(b);
                if (a == b) return false;
                if (size[a] < size[b]) std::swap(a, b);
                parent[b] = a; size[a] += size[b];
                return true;
            }
        };

        int main() {
            std::cout << power(2, 1'000'000, MOD) << '\n';
            auto p = sieve(30);
            std::cout << p.size() << ' ' << p.back() << '\n';
            DSU d(5);
            d.unite(0, 1); d.unite(3, 4); d.unite(1, 4);
            std::cout << (d.find(0) == d.find(3)) << (d.find(2) == d.find(0)) << '\n';
            std::cout << __builtin_popcount(13) << ' ' << __builtin_ctz(8) << ' '
                      << std::popcount(13u) << ' ' << std::bit_width(1000u) - 1 << '\n';   // portable <bit> versions
        }
    ''', out='''
        235042059
        10 29
        10
        3 3 3 9
    ''')
    yield note("GCC/Clang builtins: `__builtin_popcount(x)` (set bits), `__builtin_ctz(x)` (trailing zeros), `__builtin_clz(x)` (leading zeros); libstdc++ also has `std::__lg(x)` (floor log2). Portable C++20 equivalents live in `<bit>`: `std::popcount`, `std::countr_zero`, `std::bit_width(x) - 1`.")
    yield section("Operations per second", "gauge")
    yield table(
        ["n", "Feasible complexity (≈10⁸ simple ops/s)"],
        ["≤ 10–12", "O(n!)"],
        ["≤ 20–25", "O(2ⁿ)"],
        ["≤ 500", "O(n³)"],
        ["≤ 5 000", "O(n²)"],
        ["≤ 10⁶", "O(n log n)"],
        ["≤ 10⁸", "O(n)"],
        ["> 10⁹", "O(log n) or O(1) — math"],
    )
    yield qa("What do ios::sync_with_stdio(false) and cin.tie(nullptr) do?",
             "The first stops C++ streams from synchronising with C's `stdio` buffers after every operation, letting `cin`/`cout` buffer independently (after it, don't mix `scanf`/`printf` with `cin`/`cout`). The second unties `cin` from `cout`, so `cout` isn't flushed before every read. Together they make stream I/O about as fast as `scanf`/`printf`.")


@topic(G, "undefined-behavior", "Undefined Behaviour & Common Pitfalls", "bug")
def _():
    yield lead("Undefined behaviour (UB) means the standard places *no requirements* on what happens. The program may crash, work by accident, or be “optimised” into something surprising. Know the usual suspects.")
    yield define("Undefined behaviour", "the result of executing an operation the standard doesn't define — e.g. out-of-bounds access or signed overflow. Compilers assume UB never happens and optimise on that assumption, so its effects can show up far from the bug.")
    yield section("The usual suspects", "list")
    yield table(
        ["UB", "Example", "Tool that catches it"],
        ["Out-of-bounds access", "`v[v.size()]`, `arr[10]` on `int arr[10]`", "ASan, `.at()`, `-D_GLIBCXX_ASSERTIONS`"],
        ["Use after free / dangling", "Reference into a vector that grew, returning `&local`", "ASan"],
        ["Uninitialised read", "`int x; if (x) …`", "`-Wall` (sometimes), MSan, Valgrind"],
        ["Signed integer overflow", "`INT_MAX + 1`", "UBSan"],
        ["Null dereference", "`*p` with `p == nullptr`", "Crash / UBSan"],
        ["Data race", "Two threads write a non-atomic variable", "TSan"],
        ["Shift out of range", "`1 << 32` on a 32-bit `int`, negative shift", "UBSan"],
        ["Strict-aliasing violation", "`*(int*)&someFloat`", "`-fstrict-aliasing` warnings; use `memcpy`/`bit_cast`"],
        ["Modifying a const object", "`const_cast` then write", "—"],
        ["Missing `return` in a non-void function", "Falling off the end", "`-Wreturn-type` (error in clang)"],
    )
    yield section("Sanitizers find UB for you", "shield-search")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v(3);
            int* data = v.data();
            std::cout << data[3] << '\n';     // one past the end → AddressSanitizer: heap-buffer-overflow
        }
    ''', fails=True, caption="C++ — heap buffer overflow")
    yield snippet("cpp", r'''
        #include <iostream>
        int main(int argc, char**) {
            int shift = 31 + argc;            // 32 at run time
            std::cout << (1 << shift) << '\n'; // UBSan: shift exponent 32 is too large for 32-bit type 'int'
        }
    ''', fails=True, caption="C++ — oversized shift")
    yield shell('''
        $ clang++ -std=c++20 -g -fsanitize=address,undefined main.cpp && ./a.out   # memory errors + UB
        $ clang++ -std=c++20 -g -fsanitize=thread main.cpp && ./a.out              # data races
    ''')
    yield section("Classic pitfalls (not all UB, all bugs)", "alert-triangle")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <vector>

        int main() {
            // 1. Integer division before conversion
            double avg = 7 / 2;                     // 3, not 3.5
            std::cout << avg << '\n';

            // 2. Assignment instead of comparison (clang warns; parentheses silence it)
            int x = 0;
            if ((x = 5)) std::cout << "always true\n";

            // 3. Unsigned wrap-around
            std::vector<int> empty;
            std::cout << (empty.size() - 1 > 0) << '\n';   // true: 18446744073709551615 > 0

            // 4. Copy in range-for
            std::vector<std::string> names{"a", "b"};
            for (auto n : names) n += "!";          // modifies copies
            std::cout << names[0] << '\n';

            // 5. Char arithmetic
            std::string s = "abc";
            std::cout << s[0] + s[1] << '\n';       // 195 — chars promote to int
        }
    ''', out='''
        3
        always true
        1
        a
        195
    ''')
    yield warn("“It works on my machine” means nothing for UB. A different compiler, optimisation level or input can change the behaviour. Always test with `-Wall -Wextra` and sanitizers on.")
    yield qa("What's the difference between undefined, unspecified and implementation-defined behaviour?",
             "**Undefined**: no requirements at all (out-of-bounds, signed overflow). **Unspecified**: one of several valid outcomes, not documented (order of evaluating function arguments). **Implementation-defined**: one outcome the implementation must document (`sizeof(long)`, whether `char` is signed).")
    yield qa("Why doesn't C++ just check array bounds?",
             "Zero-overhead philosophy: checks cost time in tight loops, and many accesses are provably in range. C++ gives you the choice — `at()`, `std::span` with hardening, debug-mode library assertions, sanitizers in testing — without charging code that doesn't need it.")


@topic(G, "best-practices", "Best Practices & Idioms", "checklist")
def _():
    yield lead("A condensed set of rules (drawn from the C++ Core Guidelines) that keep modern C++ safe, readable and fast.")
    yield section("Resource management", "recycle")
    yield dodont("Let objects own resources (RAII): containers, `std::string`, `std::unique_ptr` (default), `std::shared_ptr` (when truly shared). Aim for the Rule of Zero.", "`new`/`delete`, `malloc`/`free`, owning raw pointers, manual `lock()`/`unlock()`.")
    yield section("Types & interfaces", "file-code")
    yield ul(
        "Make things `const` by default — variables, parameters (`const T&`), member functions.",
        "Prefer `enum class`, `std::array`/`std::vector`, `std::string_view`/`std::span` for views, `std::optional` for “maybe”.",
        "Mark single-argument constructors `explicit`; mark overrides `override`; give polymorphic bases a `virtual` destructor.",
        "Pass cheap types by value, others by `const&`; return by value (move/elision make it cheap).",
        "Use strong types instead of `bool`/`int` soup: `setTimeout(Seconds{5})`, not `setTimeout(5)`.",
    )
    yield section("Expressions & control", "code")
    yield ul(
        "Initialise every variable at declaration; prefer `{}` to catch narrowing.",
        "Use `auto` to avoid repeating types, not to hide important ones.",
        "Prefer algorithms and range-for over index loops; prefer `std::ranges::` versions in C++20.",
        "Use named casts (`static_cast`) and minimise them; never C-style casts.",
        "Keep functions short and single-purpose; limit scope of variables (`if (auto x = …; cond)`).",
    )
    yield section("Tooling", "tools")
    yield table(
        ["Tool", "Why"],
        ["`-Wall -Wextra -Wpedantic -Werror`", "Catch mistakes at compile time"],
        ["ASan / UBSan / TSan", "Catch memory errors, UB and races in tests"],
        ["`clang-tidy`", "Static analysis, modernisation checks (`modernize-*`, `cppcoreguidelines-*`)"],
        ["`clang-format`", "Consistent formatting, no style debates"],
        ["CMake + a package manager (vcpkg/Conan)", "Reproducible builds and dependencies"],
        ["GoogleTest / Catch2", "Unit tests"],
    )
    yield section("Idioms worth knowing", "bulb")
    yield cards(
        ("RAII", "Resource lifetime = object lifetime.", "recycle"),
        ("Copy-and-swap", "Strongly exception-safe assignment.", "arrows-exchange"),
        ("Pimpl", "`std::unique_ptr<Impl>` member hides implementation, cuts compile times, stabilises ABI.", "eye-off"),
        ("CRTP", "`class D : Base<D>` — static polymorphism without virtual calls.", "repeat"),
        ("Erase–remove", "`v.erase(std::remove(...), v.end())`, now `std::erase_if`.", "trash"),
        ("Type erasure", "`std::function`, `std::any` — uniform interface over unrelated types.", "box"),
    )
    yield snippet("cpp", r'''
        #include <iostream>

        template <typename Derived>
        struct Shape {                                           // CRTP base
            double area() const { return static_cast<const Derived&>(*this).areaImpl(); }
            void describe() const { std::cout << "area " << area() << '\n'; }
        };
        struct Square : Shape<Square> {
            double s;
            explicit Square(double x) : s(x) {}
            double areaImpl() const { return s * s; }
        };

        int main() { Square{3}.describe(); }                     // resolved at compile time, no vtable
    ''', out="area 9")
    yield qa("What is CRTP and why use it?",
             "The Curiously Recurring Template Pattern: a class derives from a base template instantiated with itself (`class D : public Base<D>`). The base can call derived members via `static_cast<Derived&>(*this)`, giving polymorphic-looking code resolved at compile time — no vtable, fully inlinable. Used for mixins (e.g. adding comparison operators) and static interfaces.")


@topic(G, "interview-qa", "C++ Interview Questions", "message-question")
def _():
    yield lead("The questions that come up again and again, with crisp answers. Each links back to a topic in these notes for depth.")
    yield section("Fundamentals", "school")
    yield qa("What is the difference between struct and class in C++?",
             "Only the defaults: members and base classes are `public` by default in a `struct` and `private` in a `class`. Otherwise identical — both can have constructors, methods, inheritance and virtual functions.")
    yield qa("What is the difference between a pointer and a reference?",
             "A reference is an alias: must be initialised, can't be null or re-seated. A pointer is an object holding an address: can be null, re-pointed, has arithmetic. Use references by default, pointers for optional or re-seatable relationships.")
    yield qa("What are the differences between new/delete and malloc/free?",
             "`new` allocates *and* calls the constructor, returns a typed pointer and throws `std::bad_alloc` on failure; `delete` calls the destructor. `malloc`/`free` deal with raw bytes, return `void*`/`NULL`, and never run constructors or destructors. Never mix them.")
    yield qa("What does the static keyword mean in different contexts?",
             "Inside a function: the variable persists across calls and is initialised once. At namespace scope: internal linkage (file-private). In a class: the member is shared by all instances (static functions have no `this`).")
    yield qa("What is the difference between const and constexpr?",
             "`const` = read-only after initialisation (value may be known only at run time). `constexpr` = must be computable at compile time (variables) or can be evaluated at compile time (functions).")
    yield section("OOP", "hierarchy")
    yield qa("How does runtime polymorphism work in C++?",
             "Through virtual functions: each polymorphic class has a vtable of function pointers and each object a hidden vptr to it. A call through a base pointer/reference looks up the right function in the object's vtable at run time.")
    yield qa("Why should a base class destructor be virtual?",
             "So that `delete basePtr;` runs the derived destructor first. Without `virtual`, only the base destructor runs — undefined behaviour and usually leaks.")
    yield qa("What is object slicing?",
             "Copying a derived object into a base-class *value* keeps only the base part; the derived data and overrides are lost. Avoid it by passing polymorphic objects by reference or pointer.")
    yield qa("Can constructors be virtual? Can destructors be pure virtual?",
             "Constructors can't be virtual (no object exists yet to dispatch on). Destructors can be pure virtual (`virtual ~Base() = 0;`) to make a class abstract — but they still need a definition, because derived destructors call them.")
    yield qa("What is the diamond problem?",
             "With `B : A`, `C : A`, `D : B, C`, `D` contains two `A` sub-objects, making `A`'s members ambiguous. Virtual inheritance (`B : virtual A`, `C : virtual A`) shares a single `A`, constructed by the most-derived class.")
    yield section("Memory & lifetime", "database")
    yield qa("What are the Rule of Three, Five and Zero?",
             "If you define a destructor, copy constructor or copy assignment, you likely need all three (Three); add move constructor and move assignment (Five). Best: compose your class from RAII members so you define none of them (Zero).")
    yield qa("Explain move semantics.",
             "Rvalue references (`T&&`) let a class provide a *move* constructor/assignment that steals the resources of an expiring object instead of copying them, leaving the source valid but empty. `std::move` casts an lvalue to an rvalue to opt into this.")
    yield qa("unique_ptr vs shared_ptr vs weak_ptr?",
             "`unique_ptr`: single owner, move-only, zero overhead — the default. `shared_ptr`: shared ownership via an atomic reference count; object dies with the last owner. `weak_ptr`: non-owning observer of a `shared_ptr` object; breaks cycles; `lock()` to use it.")
    yield qa("What is RAII?",
             "Resource Acquisition Is Initialization: acquire a resource in a constructor and release it in the destructor, so the resource's lifetime is bound to an object's scope and cleanup happens automatically — even during exception unwinding.")
    yield qa("What is a memory leak and how do you prevent it in C++?",
             "Heap memory that is never freed because the last pointer to it was lost. Prevent it by never owning memory through raw pointers: use containers and smart pointers, and check with ASan/LeakSanitizer or Valgrind.")
    yield section("STL & templates", "building-warehouse")
    yield qa("vector vs list? map vs unordered_map?",
             "`vector` is contiguous (fast iteration, O(1) random access, amortised O(1) push_back); `list` is linked (O(1) splice/insert given an iterator, no random access, poor cache use). `map` is a sorted red-black tree (O(log n), ordered); `unordered_map` is a hash table (O(1) average, unordered).")
    yield qa("What is iterator invalidation?",
             "Operations that restructure a container can make existing iterators, pointers and references dangle: e.g. `vector::push_back` that reallocates invalidates all of them; `erase` invalidates those at/after the erased position. Using an invalidated iterator is UB.")
    yield qa("How does std::sort work and what does it require?",
             "Introsort (quicksort + heapsort fallback + insertion sort for small ranges): O(n log n) worst case, not stable. It needs random-access iterators and a comparator that is a strict weak ordering.")
    yield qa("What are templates and when are they instantiated?",
             "Blueprints for functions/classes parameterised by types or values. The compiler generates (instantiates) a concrete version when a template is used with specific arguments, which is why template definitions usually live in headers.")
    yield qa("What are concepts?",
             "C++20 named compile-time predicates on template arguments (`std::integral`, custom `concept Shape = requires …`). They constrain templates, give readable errors, and enable overloading by capability, replacing most SFINAE.")
    yield section("Modern C++ & concurrency", "rocket")
    yield qa("What is the difference between std::thread and std::async?",
             "`std::thread` just runs a function; results/exceptions need manual plumbing and it must be joined. `std::async` returns a `std::future` that yields the result (or rethrows the exception) via `get()`.")
    yield qa("What is a data race and how do you prevent it?",
             "Concurrent access to the same memory location by two threads, at least one writing, without synchronisation — undefined behaviour. Prevent it with mutexes (`std::lock_guard`, `std::scoped_lock`), atomics, or by not sharing mutable data.")
    yield qa("What does noexcept do and why does it matter for performance?",
             "It declares a function won't throw (violations call `std::terminate`). Containers check it: `std::vector` moves elements during reallocation only if the move constructor is `noexcept`, otherwise it copies.")
    yield qa("What is std::move vs std::forward?",
             "`std::move` unconditionally casts to an rvalue (“I'm done with this”). `std::forward<T>` casts to an rvalue only if the original argument was one — used with forwarding references (`T&&` in templates) for perfect forwarding.")
    yield section("Tricky output questions", "puzzle")
    yield snippet("cpp", r'''
        #include <iostream>

        struct A {
            A()  { std::cout << "A"; }
            virtual ~A() { std::cout << "~A"; }
            virtual void f() { std::cout << "A::f "; }
        };
        struct B : A {
            B()  { std::cout << "B "; }
            ~B() override { std::cout << "~B"; }
            void f() override { std::cout << "B::f "; }
        };

        int main() {
            A* p = new B;        // prints "AB "
            p->f();              // virtual dispatch
            A a = *p;            // slicing: copy of the A part (copy ctor prints nothing)
            a.f();
            delete p;            // virtual destructor: ~B then ~A
            std::cout << '\n';
        }                        // then the sliced copy `a` is destroyed
    ''', out="AB B::f A::f ~B~A\n~A")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>

        int main() {
            int i = 5;
            int& r = i;
            int* p = &i;
            r++;
            (*p) *= 2;
            std::cout << i << ' ';

            std::vector<int> v{1, 2, 3};
            auto a = v;          // copy
            auto& b = v;         // alias
            a.push_back(4);
            b.push_back(5);
            std::cout << v.size() << a.size() << ' ';

            int x = 10;
            auto byVal = [x]() { return x; };
            auto byRef = [&x]() { return x; };
            x = 20;
            std::cout << byVal() << ' ' << byRef() << ' ';
            std::cout << sizeof(char) << sizeof(bool) << '\n';
        }
    ''', out="12 44 10 20 11")
    yield note("Walk through these line by line before running them — interviewers use exactly this kind of snippet to test construction order, virtual dispatch, slicing, references and lambda captures.", "Practice")
