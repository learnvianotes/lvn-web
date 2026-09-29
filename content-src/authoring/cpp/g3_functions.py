from kit import *

G = "Functions"


@topic(G, "functions-basics", "Functions", "function")
def _():
    yield lead("A function is a named, typed block of code: a return type, a name, a parameter list and a body. It must be *declared* before it is called.")
    yield section("Declaration vs definition", "file-code")
    yield snippet("cpp", r'''
        #include <iostream>

        int add(int a, int b);                 // declaration (prototype): signature only

        int main() {
            std::cout << add(2, 3) << '\n';    // OK: the compiler has seen the declaration
        }

        int add(int a, int b) {                // definition: signature + body
            return a + b;
        }
    ''', out="5")
    yield table(
        ["Part", "Example", "Notes"],
        ["Return type", "`int`, `void`, `auto`", "`void` = returns nothing; `auto` = deduced from `return` (C++14)"],
        ["Name", "`add`", "Can be overloaded (same name, different parameters)"],
        ["Parameters", "`(int a, int b)`", "Each is a local variable initialised from the argument"],
        ["Trailing return", "`auto add(int a, int b) -> int`", "Useful when the type depends on parameters"],
        ["Specifiers", "`inline`, `constexpr`, `static`, `noexcept`, `[[nodiscard]]`", "Change linkage, evaluation or guarantees"],
    )
    yield section("Return values", "arrow-back-up")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <utility>

        auto average(double a, double b) { return (a + b) / 2; }          // deduced: double

        std::pair<int, int> divmod(int a, int b) { return {a / b, a % b}; } // two results

        [[nodiscard]] bool save(const std::string& path) { return !path.empty(); }

        void greet(const std::string& who) {
            if (who.empty()) return;              // early return from a void function
            std::cout << "Hello, " << who << '\n';
        }

        int main() {
            std::cout << average(3, 4) << '\n';
            auto [q, r] = divmod(17, 5);
            std::cout << q << ' ' << r << '\n';
            greet("Ada");
            greet("");
            if (!save("out.txt")) std::cout << "failed\n";
        }
    ''', out='''
        3.5
        3 2
        Hello, Ada
    ''')
    yield note("`[[nodiscard]]` makes ignoring the return value a warning — great for error codes and functions like `empty()` that are easily confused with `clear()`.")
    yield section("Function call mechanics", "stack-2")
    yield steps(
        ("Arguments evaluated", "In unspecified order, then copied/bound into the parameters."),
        ("Stack frame pushed", "Parameters and locals live in the new frame (automatic storage)."),
        ("Body runs", "Until `return` or the closing brace."),
        ("Frame popped", "Locals are destroyed (destructors run, in reverse order). The return value is handed back — often constructed directly in the caller's space (*copy elision*)."),
    )
    yield warn("Never return a reference or pointer to a local variable — the frame is gone after the return, so it dangles. Return by value instead; copy elision and move semantics make it cheap.")
    yield snippet("cpp", r'''
        #include <iostream>
        int& broken() {
            int local = 42;
            return local;          // warning (error with -Werror): reference to stack memory returned
        }
        int main() { std::cout << broken() << '\n'; }
    ''', fails=True)
    yield section("`main` and static locals", "clock")
    yield snippet("cpp", r'''
        #include <iostream>
        int nextId() {
            static int counter = 0;   // initialised once, lives for the whole program
            return ++counter;
        }
        int main() {
            nextId(); nextId();
            std::cout << nextId() << '\n';
        }
    ''', out="3")
    yield qa("What is copy elision / RVO?",
             "When a function returns a local object by value, the compiler constructs it directly in the caller's storage instead of creating it locally and copying. Since C++17 this is *guaranteed* for returning a prvalue (`return Widget{...};`) and very common for named locals (NRVO). That's why returning big objects by value is idiomatic.")


@topic(G, "parameter-passing", "Pass by Value, Reference & Pointer", "arrows-exchange")
def _():
    yield lead("How a parameter is declared decides whether the function gets a copy, an alias to the caller's object, or its address.")
    yield section("The three ways", "switch-3")
    yield snippet("cpp", r'''
        #include <iostream>

        void byValue(int x)      { x = 100; std::cout << "inside " << x << '\n'; }  // a copy
        void byReference(int& x) { x = 200; }        // x IS the caller's variable
        void byPointer(int* x)   { if (x) *x = 300; } // modifies through the address (may be null)

        int main() {
            int a = 1;
            byValue(a);      std::cout << a << '\n';
            byReference(a);  std::cout << a << '\n';
            byPointer(&a);   std::cout << a << '\n';
            byPointer(nullptr);                       // allowed: pointers can express “no object”
        }
    ''', out='''
        inside 100
        1
        200
        300
    ''')
    yield table(
        ["Style", "Copies?", "Can modify caller?", "Can be null?", "Use for"],
        ["`T x`", "Yes", "No", "—", "Cheap types (`int`, `double`, small structs, iterators), or when you need a copy anyway"],
        ["`const T& x`", "No", "No", "No", "**Read-only** access to anything non-trivial (`std::string`, `std::vector`)"],
        ["`T& x`", "No", "Yes", "No", "Out/in-out parameters"],
        ["`T* x`", "No", "Yes", "**Yes**", "Optional objects, C APIs"],
        ["`T&& x`", "No", "Yes (steals)", "No", "Taking ownership of temporaries (move semantics)"],
    )
    yield section("Why `const&` for big objects", "gauge")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        struct Tracker {
            std::string name;
            Tracker(std::string n) : name(std::move(n)) {}
            Tracker(const Tracker& other) : name(other.name) { std::cout << "copy!\n"; }
        };

        void slow(Tracker t)        { std::cout << "slow " << t.name << '\n'; }
        void fast(const Tracker& t) { std::cout << "fast " << t.name << '\n'; }

        int main() {
            Tracker big("report");
            slow(big);      // copies the whole object
            fast(big);      // no copy
        }
    ''', out='''
        copy!
        slow report
        fast report
    ''')
    yield section("Swapping — the classic example", "arrows-left-right")
    yield snippet("cpp", r'''
        #include <iostream>
        void swapRef(int& a, int& b) { int t = a; a = b; b = t; }
        void swapPtr(int* a, int* b) { int t = *a; *a = *b; *b = t; }
        int main() {
            int x = 1, y = 2;
            swapRef(x, y);
            std::cout << x << y << '\n';
            swapPtr(&x, &y);
            std::cout << x << y << '\n';
        }
    ''', out='''
        21
        12
    ''')
    yield section("Passing arrays and containers", "brackets")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>

        int sumArray(const int* arr, std::size_t n) {   // a C array decays to a pointer: size is lost
            int s = 0;
            for (std::size_t i = 0; i < n; ++i) s += arr[i];
            return s;
        }
        void doubleAll(std::vector<int>& v) { for (int& x : v) x *= 2; }

        int main() {
            int raw[] = {1, 2, 3};
            std::cout << sumArray(raw, 3) << '\n';
            std::vector<int> v{1, 2, 3};
            doubleAll(v);
            std::cout << v[0] << v[1] << v[2] << '\n';
        }
    ''', out='''
        6
        246
    ''')
    yield note("Rule of thumb: **in** params — by value if cheap to copy (≤ ~2 words), else `const T&`. **Out/in-out** — `T&`. **Optional** — `T*` or `std::optional`. **Sink** params you'll store — by value, then `std::move` into place.", "Guideline")
    yield warn("A non-const reference can't bind to a temporary: `void f(std::string& s); f(\"hi\");` is an error. `const std::string&` can — the temporary lives until the call returns.")
    yield qa("Is Java/Python-style pass by reference the same as C++ references?",
             "No. Java and Python pass a *reference value* by value: reassigning the parameter doesn't affect the caller. A C++ `T&` parameter is a true alias: `x = other;` inside the function assigns to the caller's object.")
    yield qa("When would you pass by pointer instead of reference?",
             "When “no object” is a valid input (`nullptr`), when interoperating with C APIs, or when you want the call site to show that the argument may be modified (`update(&config)`). Otherwise references are safer: they can't be null or re-seated.")


@topic(G, "overloading-default-args", "Overloading, Default Arguments & inline", "versions")
def _():
    yield lead("Several functions can share a name if their parameter lists differ; the compiler picks the best match at compile time. Default arguments fill in trailing parameters.")
    yield section("Function overloading", "copy")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        int area(int side)               { return side * side; }
        int area(int w, int h)           { return w * h; }
        double area(double radius)       { return 3.14159 * radius * radius; }
        std::string describe(int)        { return "int"; }
        std::string describe(long)       { return "long"; }
        std::string describe(const std::string&) { return "string"; }

        int main() {
            std::cout << area(4) << ' ' << area(2, 3) << ' ' << area(1.0) << '\n';
            std::cout << describe(1) << ' ' << describe(1L) << ' ' << describe("hi") << '\n';
            std::cout << describe('c') << '\n';   // char → int is a promotion: best match
        }
    ''', out='''
        16 6 3.14159
        int long string
        int
    ''')
    yield table(
        ["Rank", "Conversion needed", "Example"],
        ["1. Exact match", "None (or trivial: array→pointer, adding `const`)", "`f(int)` for `f(5)`"],
        ["2. Promotion", "`char`/`short`/`bool` → `int`, `float` → `double`", "`f(int)` for `f('c')`"],
        ["3. Standard conversion", "`int` → `double`, `double` → `int`, derived* → base*", "`f(double)` for `f(5)`"],
        ["4. User-defined", "Constructor or conversion operator", "`f(std::string)` for `f(\"hi\")`"],
    )
    yield warn("Return type alone can't distinguish overloads, and two equally good matches are a compile error: with `f(int)` and `f(double)`, calling `f(5L)` is **ambiguous**.")
    yield snippet("cpp", r'''
        void f(int) {}
        void f(double) {}
        int main() {
            f(5L);      // error: call to 'f' is ambiguous (long → int and long → double rank the same)
        }
    ''', fails=True)
    yield section("Default arguments", "adjustments")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        void log(const std::string& msg, int level = 1, char end = '\n') {
            std::cout << "[" << level << "] " << msg << end;
        }

        int main() {
            log("start");
            log("warn", 2);
            log("inline", 3, ' ');
            log("done");
        }
    ''', out='''
        [1] start
        [2] warn
        [3] inline [1] done
    ''')
    yield ul(
        "Defaults must be the **trailing** parameters: `void f(int a = 1, int b);` is illegal.",
        "Specify them once — in the declaration (header), not again in the definition.",
        "They're substituted at the *call site* at compile time; for virtual functions the default comes from the *static* type — a classic trap.",
    )
    yield section("`inline`", "arrow-bar-to-right")
    yield p("`inline` originally meant “please paste the body at the call site”. Today compilers decide inlining themselves; the keyword's real meaning is **ODR**: an `inline` function (or C++17 `inline` variable) may be defined in a header included by many `.cpp` files without “multiple definition” link errors.")
    yield snippet("cpp", r'''
        #include <iostream>
        inline int maxOf(int a, int b) { return a > b ? a : b; }   // OK to live in a header
        inline constexpr int kVersion = 3;                           // C++17 inline variable
        struct Box {
            int w = 2;
            int width() const { return w; }   // member functions defined in the class are implicitly inline
        };
        int main() { std::cout << maxOf(3, 9) << ' ' << kVersion << ' ' << Box{}.width() << '\n'; }
    ''', out="9 3 2")
    yield qa("Can overloaded functions differ only by const on a by-value parameter?",
             "No. `void f(int)` and `void f(const int)` declare the *same* function — top-level `const` on a by-value parameter isn't part of the signature. `f(int&)` vs `f(const int&)`, however, are distinct overloads.")
    yield qa("What's the difference between a macro and an inline function?",
             "A macro is textual substitution by the preprocessor: no types, no scope, arguments may be evaluated twice (`MAX(i++, j)`). An inline function is a real function — type-checked, scoped, arguments evaluated once — and is optimised just as well.")


@topic(G, "lambdas", "Lambda Expressions", "lambda")
def _():
    yield lead("A lambda is an unnamed function object written inline: `[captures](params) { body }`. It's how you pass behaviour to algorithms, threads and callbacks.")
    yield section("Syntax", "code")
    yield formula("`[capture](parameters) mutable noexcept -> ReturnType { body }`")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            auto add = [](int a, int b) { return a + b; };       // return type deduced
            std::cout << add(2, 3) << '\n';

            std::vector<int> v{5, 2, 8, 1};
            std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });   // descending
            for (int x : v) std::cout << x << ' ';
            std::cout << '\n';

            int threshold = 3;
            auto big = std::count_if(v.begin(), v.end(), [threshold](int x) { return x > threshold; });
            std::cout << big << '\n';
        }
    ''', out='''
        5
        8 5 2 1
        2
    ''')
    yield section("Captures", "hand-grab")
    yield table(
        ["Capture", "Meaning"],
        ["`[]`", "Nothing captured"],
        ["`[x]`", "`x` by value (a copy taken when the lambda is created)"],
        ["`[&x]`", "`x` by reference"],
        ["`[=]`", "Everything used, by value"],
        ["`[&]`", "Everything used, by reference"],
        ["`[=, &x]` / `[&, x]`", "Default plus exceptions"],
        ["`[this]` / `[*this]`", "The enclosing object by pointer / by copy (C++17)"],
        ["`[y = expr]`", "Init-capture (C++14): new variable, e.g. `[p = std::move(ptr)]`"],
    )
    yield snippet("cpp", r'''
        #include <iostream>
        int main() {
            int n = 1;
            auto byVal = [n] { return n; };      // copies n now
            auto byRef = [&n] { return n; };     // refers to n
            n = 10;
            std::cout << byVal() << ' ' << byRef() << '\n';

            auto counter = [count = 0]() mutable { return ++count; };   // own state; `mutable` allows changing copies
            counter(); counter();
            std::cout << counter() << '\n';
        }
    ''', out='''
        1 10
        3
    ''')
    yield warn("Capturing by reference (`[&]`) in a lambda that outlives the scope — stored in a `std::function`, passed to a thread, returned from a function — leaves dangling references. Capture by value (or move) for anything that escapes.")
    yield section("Generic and immediately-invoked lambdas", "template")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>
        #include <string>
        int main() {
            auto twice = [](auto x) { return x + x; };               // generic lambda (C++14)
            std::cout << twice(21) << ' ' << twice(std::string("ab")) << '\n';

            const int config = [] {                                  // IIFE: initialise a const in steps
                int v = 0;
                for (int i = 1; i <= 4; ++i) v += i;
                return v;
            }();
            std::cout << config << '\n';

            std::function<int(int)> fib = [&fib](int k) {            // recursive lambda via std::function
                return k < 2 ? k : fib(k - 1) + fib(k - 2);
            };
            std::cout << fib(10) << '\n';
        }
    ''', out='''
        42 abab
        10
        55
    ''')
    yield note("Recursive lambdas: C++23 *deducing this* (`[](this auto self, int k)`) is the clean way; in C++20 use `std::function` (as above) or pass the lambda to itself as an `auto&` parameter.", "Recursion")
    yield section("What a lambda really is", "box")
    yield p("The compiler turns each lambda into an unnamed class with an `operator()` — captured variables become data members. Captureless lambdas also convert to plain function pointers.")
    yield snippet("cpp", r'''
        #include <iostream>
        struct AddN {                       // roughly what [n](int x) { return x + n; } becomes
            int n;
            int operator()(int x) const { return x + n; }
        };
        int main() {
            int n = 5;
            auto lambda = [n](int x) { return x + n; };
            AddN functor{n};
            int (*fp)(int) = [](int x) { return x * 2; };    // captureless → function pointer
            std::cout << lambda(1) << ' ' << functor(1) << ' ' << fp(4) << '\n';
        }
    ''', out="6 6 8")
    yield qa("Why does a by-value capture need mutable to be modified?",
             "The generated `operator()` is `const` by default, so captured copies are read-only inside the body. `mutable` removes that `const`, letting the lambda change *its own copies* (never the originals).")
    yield qa("What's the type of a lambda?",
             "A unique, unnamed closure type generated by the compiler — two identical-looking lambdas have different types. That's why you store them with `auto`, pass them as template parameters, or wrap them in `std::function` when you need one uniform type.")


@topic(G, "function-pointers-std-function", "Function Pointers, Functors & std::function", "plug")
def _():
    yield lead("Three ways to treat “a function” as a value: raw function pointers (C-style), function objects (classes with `operator()`), and the type-erased `std::function` wrapper.")
    yield section("Function pointers", "pointer")
    yield snippet("cpp", r'''
        #include <iostream>

        int add(int a, int b) { return a + b; }
        int mul(int a, int b) { return a * b; }

        int apply(int (*op)(int, int), int x, int y) { return op(x, y); }

        using BinaryOp = int (*)(int, int);          // alias makes the syntax readable

        int main() {
            BinaryOp ops[] = {add, mul};             // table of functions
            for (BinaryOp op : ops) std::cout << apply(op, 3, 4) << ' ';
            std::cout << '\n';
            int (*p)(int, int) = &add;               // & and * are optional for functions
            std::cout << (*p)(1, 1) << ' ' << p(2, 2) << '\n';
        }
    ''', out='''
        7 12
        2 4
    ''')
    yield section("Functors (function objects)", "box")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        class InRange {                               // a functor can carry state
            int lo_, hi_;
        public:
            InRange(int lo, int hi) : lo_(lo), hi_(hi) {}
            bool operator()(int x) const { return lo_ <= x && x <= hi_; }
        };

        int main() {
            std::vector<int> v{1, 5, 9, 12, 7};
            std::cout << std::count_if(v.begin(), v.end(), InRange(5, 10)) << '\n';
            std::sort(v.begin(), v.end(), std::greater<int>());   // standard functor from <functional>
            std::cout << v.front() << '\n';
        }
    ''', out='''
        3
        12
    ''')
    yield section("`std::function`", "plug-connected")
    yield p("`std::function<R(Args...)>` can hold *any* callable with that signature — function pointer, functor or lambda (even with captures). It's the tool for storing callbacks of unknown type, at the cost of a possible heap allocation and an indirect call.")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>
        #include <map>
        #include <string>

        int sub(int a, int b) { return a - b; }

        int main() {
            int bonus = 100;
            std::map<std::string, std::function<int(int, int)>> calc{
                {"+", [](int a, int b) { return a + b; }},
                {"-", sub},
                {"max", [](int a, int b) { return std::max(a, b); }},
                {"bonus", [bonus](int a, int) { return a + bonus; }},
            };
            for (const auto& [name, fn] : calc) std::cout << name << ' ' << fn(8, 3) << '\n';

            std::function<void()> empty;
            std::cout << std::boolalpha << static_cast<bool>(empty) << '\n';   // calling it would throw bad_function_call
        }
    ''', out='''
        + 11
        - 5
        bonus 108
        max 8
        false
    ''')
    yield section("`std::bind` and `std::invoke`", "link")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>

        int power(int base, int exp) { int r = 1; while (exp--) r *= base; return r; }
        struct Account { int balance = 50; int get() const { return balance; } };

        int main() {
            using namespace std::placeholders;
            auto square = std::bind(power, _1, 2);           // fix the second argument
            auto squareL = [](int b) { return power(b, 2); }; // the lambda equivalent (preferred)
            std::cout << square(7) << ' ' << squareL(7) << '\n';

            Account acc;
            std::cout << std::invoke(&Account::get, acc) << ' ' << std::invoke(power, 2, 5) << '\n';  // uniform call syntax
        }
    ''', out='''
        49 49
        50 32
    ''')
    yield table(
        ["Option", "Overhead", "Holds state?", "Use when"],
        ["Function pointer", "Indirect call", "No", "C APIs, simple tables of functions"],
        ["Lambda / functor + template parameter", "**None** (inlined)", "Yes", "Algorithms, hot paths: `template <class F> void run(F f)`"],
        ["`std::function`", "Type erasure; maybe allocation", "Yes", "Storing heterogeneous callbacks (maps, members, event handlers)"],
    )
    yield qa("Why is std::sort with a lambda often faster than C's qsort?",
             "`qsort` calls the comparator through a `void*`-based function pointer on every comparison, which the compiler usually can't inline. `std::sort` is a template: the lambda's type is part of the instantiation, so the comparison is inlined into the sorting loop.")


@topic(G, "recursion", "Recursion", "recycle")
def _():
    yield lead("A recursive function calls itself on a smaller input until it reaches a base case. Every call gets its own stack frame.")
    yield section("Anatomy", "hierarchy")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        long long factorial(int n) {
            if (n <= 1) return 1;              // base case
            return n * factorial(n - 1);       // recursive case: smaller problem
        }

        int power(int b, int e) {              // fast exponentiation: O(log e)
            if (e == 0) return 1;
            int half = power(b, e / 2);
            return e % 2 ? half * half * b : half * half;
        }

        bool isPalindrome(const std::string& s, int l, int r) {
            if (l >= r) return true;
            return s[l] == s[r] && isPalindrome(s, l + 1, r - 1);
        }

        int main() {
            std::cout << factorial(20) << '\n';
            std::cout << power(3, 13) << '\n';
            std::cout << isPalindrome("racecar", 0, 6) << isPalindrome("rocket", 0, 5) << '\n';
        }
    ''', out='''
        2432902008176640000
        1594323
        10
    ''')
    yield section("Backtracking: generate all subsets", "binary-tree")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>

        void subsets(const std::vector<int>& nums, std::size_t i, std::vector<int>& cur) {
            if (i == nums.size()) {
                std::cout << '{';
                for (int x : cur) std::cout << x;
                std::cout << "} ";
                return;
            }
            subsets(nums, i + 1, cur);          // exclude nums[i]
            cur.push_back(nums[i]);             // include nums[i]
            subsets(nums, i + 1, cur);
            cur.pop_back();                     // undo (backtrack)
        }

        int main() {
            std::vector<int> cur;
            subsets({1, 2, 3}, 0, cur);
            std::cout << '\n';
        }
    ''', out="{} {3} {2} {23} {1} {13} {12} {123} ")
    yield section("Memoisation", "database")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>

        long long fib(int n, std::vector<long long>& memo) {
            if (n < 2) return n;
            if (memo[n] != -1) return memo[n];          // already computed
            return memo[n] = fib(n - 1, memo) + fib(n - 2, memo);
        }

        int main() {
            std::vector<long long> memo(91, -1);
            std::cout << fib(90, memo) << '\n';          // instant; naive recursion would take ages
        }
    ''', out="2880067194370816120")
    yield warn("Deep recursion overflows the stack (default ~1–8 MB): a recursive DFS on a 10⁶-node path graph will crash. Convert to an explicit stack/loop when depth can be large.")
    yield table(
        ["", "Recursion", "Iteration"],
        ["Readability", "Natural for trees, divide & conquer, backtracking", "Natural for linear scans"],
        ["Memory", "O(depth) stack frames", "O(1) extra (or an explicit stack)"],
        ["Risk", "Stack overflow", "—"],
    )
    yield qa("Does C++ guarantee tail-call optimisation?",
             "No. Compilers often turn tail calls into jumps at `-O2`, but the standard doesn't require it and destructors of locals can prevent it. Don't rely on it for unbounded recursion depth.")
