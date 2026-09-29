from kit import *

G = "Templates & Generic Programming"


@topic(G, "function-templates", "Function Templates", "template")
def _():
    yield lead("A template is a blueprint the compiler stamps out for each set of types you use it with. Write the algorithm once; get type-checked, fully optimised code for every type.")
    yield section("Defining and calling", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        template <typename T>                     // `class T` means the same
        T maxOf(T a, T b) { return a > b ? a : b; }

        template <typename T, typename U>
        auto add(T a, U b) { return a + b; }      // return type deduced from the expression

        template <typename T, int N>              // non-type template parameter
        constexpr int length(const T (&)[N]) { return N; }

        int main() {
            std::cout << maxOf(3, 7) << ' ' << maxOf(2.5, 1.5) << ' ' << maxOf<std::string>("pear", "apple") << '\n';
            std::cout << add(1, 2.5) << '\n';
            int arr[] = {1, 2, 3, 4};
            std::cout << length(arr) << '\n';
            // maxOf(3, 7.0);   // error: T deduced as both int and double
            std::cout << maxOf<double>(3, 7.5) << '\n';   // explicit template argument
        }
    ''', out='''
        7 2.5 pear
        3.5
        4
        7.5
    ''')
    yield section("How instantiation works", "cpu")
    yield steps(
        ("Deduction", "From the call `maxOf(3, 7)` the compiler deduces `T = int`."),
        ("Instantiation", "It generates `int maxOf<int>(int, int)` — a real function — and type-checks it."),
        ("Reuse", "Every call with `T = int` in this translation unit uses the same instantiation; identical instantiations in other TUs are merged by the linker."),
    )
    yield note("Templates are checked twice: syntax when defined, and fully when instantiated. Errors like “no match for `operator>`” appear only when you use the template with a type that lacks it — which is what **concepts** fix.")
    yield section("Overloading and explicit specialisation", "versions")
    yield snippet("cpp", r'''
        #include <cstring>
        #include <iostream>

        template <typename T>
        bool equal(const T& a, const T& b) { return a == b; }

        template <>                                               // full specialisation for const char*
        bool equal<const char*>(const char* const& a, const char* const& b) { return std::strcmp(a, b) == 0; }

        template <typename T>
        void describe(T)  { std::cout << "value\n"; }
        template <typename T>
        void describe(T*) { std::cout << "pointer\n"; }           // overload: more specialised, preferred

        int main() {
            const char* x = "hi";
            char buf[] = "hi";
            const char* y = buf;
            std::cout << equal(1, 1) << equal(x, y) << '\n';     // compares contents, not addresses
            int n = 0;
            describe(n);
            describe(&n);
        }
    ''', out='''
        11
        value
        pointer
    ''')
    yield note("Prefer *overloading* function templates to specialising them — specialisations don't take part in overload resolution, which surprises people.")
    yield section("Abbreviated templates (C++20)", "wand")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        auto sum(const auto& container) {          // `auto` parameter = implicit template
            typename std::decay_t<decltype(container)>::value_type total{};
            for (const auto& x : container) total += x;
            return total;
        }
        int main() {
            std::cout << sum(std::vector<int>{1, 2, 3}) << ' ' << sum(std::vector<double>{0.5, 0.25}) << '\n';
        }
    ''', out="6 0.75")
    yield qa("What is template argument deduction?",
             "The process where the compiler figures out template parameters from the types of the call's arguments, so you can write `maxOf(3, 7)` instead of `maxOf<int>(3, 7)`. Deduction doesn't consider implicit conversions: `maxOf(3, 7.0)` fails because `T` would have to be both `int` and `double`.")
    yield qa("Do templates cause code bloat?",
             "Each distinct instantiation is separate code, so using a template with many types can grow the binary. In exchange each version is specialised and inlinable. Mitigations: factor type-independent code into non-template helpers, and use type erasure where performance isn't critical.")


@topic(G, "class-templates", "Class Templates & Specialisation", "box-multiple")
def _():
    yield lead("Class templates are how the STL is built: `std::vector<T>`, `std::map<K, V>`, `std::array<T, N>`. The type parameter becomes part of the class's type.")
    yield section("A generic container", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>
        #include <string>
        #include <vector>

        template <typename T>
        class Stack {
        public:
            void push(const T& value) { items_.push_back(value); }
            void pop() {
                if (items_.empty()) throw std::out_of_range("pop on empty stack");
                items_.pop_back();
            }
            const T& top() const { return items_.back(); }
            bool empty() const { return items_.empty(); }
            std::size_t size() const { return items_.size(); }
        private:
            std::vector<T> items_;
        };

        int main() {
            Stack<int> s;
            s.push(1); s.push(2); s.push(3);
            s.pop();
            std::cout << s.top() << ' ' << s.size() << '\n';

            Stack<std::string> words;
            words.push("hello");
            std::cout << words.top() << '\n';
        }
    ''', out='''
        2 2
        hello
    ''')
    yield section("Defaults, non-type parameters and CTAD", "adjustments")
    yield snippet("cpp", r'''
        #include <array>
        #include <iostream>
        #include <utility>
        #include <vector>

        template <typename T, std::size_t Capacity = 4>
        class RingBuffer {
            std::array<T, Capacity> data_{};
            std::size_t head_ = 0, count_ = 0;
        public:
            void push(T v) {
                data_[(head_ + count_) % Capacity] = v;
                if (count_ < Capacity) ++count_; else head_ = (head_ + 1) % Capacity;
            }
            T front() const { return data_[head_]; }
            std::size_t size() const { return count_; }
        };

        int main() {
            RingBuffer<int, 3> rb;
            for (int i = 1; i <= 5; ++i) rb.push(i);       // keeps the last 3
            std::cout << rb.front() << ' ' << rb.size() << '\n';

            std::pair p{1, 2.5};                            // CTAD (C++17): pair<int, double>
            std::vector v{1, 2, 3};                         // vector<int>
            std::cout << p.second << ' ' << v.size() << '\n';
        }
    ''', out='''
        3 3
        2.5 3
    ''')
    yield section("Full and partial specialisation", "git-fork")
    yield snippet("cpp", r'''
        #include <iostream>

        template <typename T>
        struct TypeName { static const char* get() { return "unknown"; } };

        template <>                                   // full specialisation
        struct TypeName<int> { static const char* get() { return "int"; } };

        template <typename T>                         // partial specialisation: any pointer
        struct TypeName<T*> { static const char* get() { return "pointer"; } };

        template <typename K, typename V>
        struct Pair { const char* kind() const { return "general"; } };
        template <typename T>
        struct Pair<T, T> { const char* kind() const { return "same types"; } };   // partial

        int main() {
            std::cout << TypeName<int>::get() << ' ' << TypeName<double*>::get() << ' ' << TypeName<char>::get() << '\n';
            std::cout << Pair<int, double>{}.kind() << ", " << Pair<int, int>{}.kind() << '\n';
        }
    ''', out='''
        int pointer unknown
        general, same types
    ''')
    yield table(
        ["", "Function templates", "Class templates"],
        ["Full specialisation", "Yes", "Yes"],
        ["Partial specialisation", "**No** (overload instead)", "Yes"],
        ["Deduce arguments", "Yes (from call)", "C++17 CTAD (from constructor)"],
    )
    yield section("Member templates & `typename`", "code-dots")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <list>
        #include <vector>

        template <typename Container>
        typename Container::value_type first(const Container& c) {   // `typename`: a dependent *type*
            return *c.begin();
        }

        struct Printer {
            template <typename T>
            void print(const T& x) const { std::cout << x << '\n'; }   // member function template
        };

        int main() {
            std::cout << first(std::vector<int>{7, 8}) << ' ' << first(std::list<char>{'z'}) << '\n';
            Printer{}.print(3.5);
        }
    ''', out='''
        7 z
        3.5
    ''')
    yield qa("Why do you sometimes need the typename keyword inside a template?",
             "In `Container::value_type`, the compiler can't know whether `value_type` is a type or a static member until `Container` is known. By default it assumes a value; `typename` tells it the dependent name is a type.")
    yield qa("What is the difference between full and partial specialisation?",
             "Full specialisation fixes *all* template parameters (`TypeName<int>`); partial specialisation fixes some or constrains their form (`TypeName<T*>`, `Pair<T, T>`) and is still a template. Only class (and variable) templates can be partially specialised.")


@topic(G, "variadic-templates", "Variadic Templates & Fold Expressions", "dots")
def _():
    yield lead("A *parameter pack* (`typename... Args`) lets a template accept any number of arguments of any types — how `std::make_unique`, `std::tuple` and `emplace_back` work.")
    yield section("Fold expressions (C++17)", "sum")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        template <typename... Ts>
        auto sum(Ts... xs) { return (xs + ... + 0); }            // binary right fold with init 0

        template <typename... Ts>
        void printAll(const Ts&... xs) {
            ((std::cout << xs << ' '), ...);                     // unary fold over the comma operator
            std::cout << "(" << sizeof...(xs) << " args)\n";    // number of elements in the pack
        }

        template <typename... Ts>
        bool allPositive(Ts... xs) { return ((xs > 0) && ...); }

        int main() {
            std::cout << sum(1, 2, 3, 4) << ' ' << sum() << ' ' << sum(1.5, 2) << '\n';
            printAll(1, "two", 3.0, std::string("four"), 'v');
            std::cout << allPositive(1, 5, 9) << allPositive(1, -5) << '\n';
        }
    ''', out='''
        10 0 3.5
        1 two 3 four v (5 args)
        10
    ''')
    yield table(
        ["Fold", "Expands to"],
        ["`(pack op ...)`", "`x1 op (x2 op (x3 op x4))`"],
        ["`(... op pack)`", "`((x1 op x2) op x3) op x4`"],
        ["`(pack op ... op init)`", "`x1 op (x2 op (… op init))` — works for an empty pack"],
    )
    yield section("Recursive style (pre-C++17)", "recycle")
    yield snippet("cpp", r'''
        #include <iostream>

        void logAll() { std::cout << '\n'; }                 // base case: empty pack

        template <typename T, typename... Rest>
        void logAll(const T& first, const Rest&... rest) {  // peel off one argument per call
            std::cout << '[' << first << ']';
            logAll(rest...);                              // pack expansion
        }

        int main() { logAll("id", 42, 3.5); }
    ''', out="[id][42][3.5]")
    yield section("Forwarding a pack", "arrow-forward")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>
        #include <utility>

        struct User {
            std::string name;
            int age;
            User(std::string n, int a) : name(std::move(n)), age(a) {}
        };

        template <typename T, typename... Args>
        std::unique_ptr<T> create(Args&&... args) {                    // a hand-written make_unique
            return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
        }

        int main() {
            auto u = create<User>("Ada", 36);
            std::cout << u->name << ' ' << u->age << '\n';
        }
    ''', out="Ada 36")
    yield qa("What does sizeof...(args) return?",
             "The number of elements in the parameter pack, as a compile-time constant. It doesn't evaluate the arguments or measure their byte sizes.")


@topic(G, "perfect-forwarding", "Forwarding References & std::forward", "arrow-forward-up")
def _():
    yield lead("A template parameter `T&&` is a *forwarding reference*: it binds to lvalues and rvalues alike. `std::forward<T>` passes the argument on with its original value category, so moves stay moves and copies stay copies.")
    yield section("Reference collapsing", "arrows-minimize")
    yield table(
        ["Argument", "`T` deduced as", "`T&&` becomes"],
        ["lvalue `int x`", "`int&`", "`int& &&` → `int&`"],
        ["rvalue `42` / `std::move(x)`", "`int`", "`int&&`"],
    )
    yield p("Rule: `& &`, `& &&` and `&& &` collapse to `&`; only `&& &&` stays `&&`. A `T&&` is a forwarding reference **only** when `T` is being deduced (a template parameter or `auto&&`) — `std::string&&` is a plain rvalue reference.")
    yield section("The problem `std::forward` solves", "question-mark")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <utility>

        void consume(const std::string&) { std::cout << "copy\n"; }
        void consume(std::string&&)      { std::cout << "move\n"; }

        template <typename T>
        void wrapperBad(T&& arg) { consume(arg); }                    // a named variable is an lvalue!

        template <typename T>
        void wrapperGood(T&& arg) { consume(std::forward<T>(arg)); }  // restores the category

        int main() {
            std::string s = "x";
            wrapperBad(s);              wrapperBad(std::string("t"));
            wrapperGood(s);             wrapperGood(std::string("t"));
        }
    ''', out='''
        copy
        copy
        copy
        move
    ''')
    yield table(
        ["", "`std::move(x)`", "`std::forward<T>(x)`"],
        ["What it does", "Unconditionally casts to rvalue", "Casts to rvalue *only if* the original argument was an rvalue"],
        ["Use with", "Objects you own and are done with", "Forwarding references `T&&` in templates"],
    )
    yield section("Real use: emplace", "stack-push")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <vector>

        struct Order {
            std::string item;
            int qty;
            Order(std::string i, int q) : item(std::move(i)), qty(q) { std::cout << "construct\n"; }
            Order(const Order& o) : item(o.item), qty(o.qty) { std::cout << "copy\n"; }
            Order(Order&& o) noexcept : item(std::move(o.item)), qty(o.qty) { std::cout << "move\n"; }
        };

        int main() {
            std::vector<Order> orders;
            orders.reserve(4);
            orders.push_back(Order("pen", 2));     // construct a temporary, then move it in
            orders.emplace_back("ink", 1);         // forwards the arguments: construct in place
        }
    ''', out='''
        construct
        move
        construct
    ''')
    yield warn("Don't `std::forward` the same argument twice — the first call may already have moved from it. And don't overload a function on a forwarding reference: `template <class T> void f(T&&)` is an exact match for almost everything and will hijack your other overloads.")
    yield qa("What is perfect forwarding?",
             "Passing arguments through a generic wrapper to another function exactly as they were given — preserving lvalue/rvalue-ness and const — using a forwarding reference `T&&` plus `std::forward<T>(arg)`. It's how `make_unique`, `emplace_back` and `std::thread`'s constructor avoid unnecessary copies.")


@topic(G, "type-traits-if-constexpr", "Type Traits & if constexpr", "adjustments-code")
def _():
    yield lead("`<type_traits>` lets templates ask questions about types at compile time; `if constexpr` (C++17) keeps only the branch that applies, so each instantiation compiles just the code it needs.")
    yield section("Asking questions about types", "help")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <type_traits>

        int main() {
            std::cout << std::boolalpha
                      << std::is_integral_v<int> << ' '
                      << std::is_floating_point_v<int> << ' '
                      << std::is_pointer_v<char*> << ' '
                      << std::is_same_v<std::remove_const_t<const int>, int> << ' '
                      << std::is_trivially_copyable_v<std::string> << ' '
                      << std::is_base_of_v<std::exception, std::runtime_error> << '\n';
            static_assert(std::is_same_v<std::decay_t<const int&>, int>);
            static_assert(sizeof(long long) == 8, "this code assumes 64-bit long long");
        }
    ''', out="true false true true false true")
    yield table(
        ["Trait", "Question / transformation"],
        ["`is_integral_v<T>`, `is_floating_point_v<T>`, `is_arithmetic_v<T>`", "Category checks"],
        ["`is_same_v<A, B>`", "Exactly the same type?"],
        ["`is_base_of_v<B, D>`, `is_convertible_v<From, To>`", "Relationships"],
        ["`remove_reference_t<T>`, `remove_const_t<T>`, `decay_t<T>`", "Strip qualifiers (decay = what pass-by-value does)"],
        ["`conditional_t<Cond, A, B>`", "Compile-time ternary on types"],
        ["`enable_if_t<Cond, T>`", "Remove an overload unless `Cond` (pre-C++20 SFINAE)"],
    )
    yield section("`if constexpr`", "git-branch")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <type_traits>
        #include <vector>

        template <typename T>
        std::string describe(const T& value) {
            if constexpr (std::is_integral_v<T>)
                return "integer " + std::to_string(value * 2);     // only compiled for integers
            else if constexpr (std::is_floating_point_v<T>)
                return "float " + std::to_string(value);
            else if constexpr (requires { value.size(); })         // C++20 requires-expression
                return "sized thing of " + std::to_string(value.size());
            else
                return "something else";
        }

        int main() {
            std::cout << describe(21) << '\n' << describe(0.5) << '\n'
                      << describe(std::vector<int>{1, 2, 3}) << '\n' << describe(nullptr) << '\n';
        }
    ''', out='''
        integer 42
        float 0.500000
        sized thing of 3
        something else
    ''')
    yield note("With a plain `if`, *both* branches must compile for every `T` — `value * 2` on a `std::vector` would be an error. `if constexpr` discards the untaken branch inside templates.")
    yield section("Writing your own trait", "tool")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <list>
        #include <type_traits>
        #include <vector>

        template <typename T> struct is_vector : std::false_type {};
        template <typename T, typename A> struct is_vector<std::vector<T, A>> : std::true_type {};
        template <typename T> inline constexpr bool is_vector_v = is_vector<T>::value;

        int main() {
            std::cout << is_vector_v<std::vector<int>> << is_vector_v<std::list<int>> << is_vector_v<int> << '\n';
        }
    ''', out="100")
    yield qa("What is SFINAE?",
             "*Substitution Failure Is Not An Error*: if substituting template arguments into a function template's signature produces invalid code, that overload is silently dropped instead of causing an error. Pre-C++20 code uses it (via `std::enable_if`) to constrain templates; C++20 concepts express the same thing readably.")


@topic(G, "concepts", "Concepts & Constraints (C++20)", "filter-check")
def _():
    yield lead("A concept is a named, compile-time predicate on types. Constraining a template with one gives clear error messages and lets you overload on what a type can do.")
    yield section("Using standard concepts", "check")
    yield snippet("cpp", r'''
        #include <concepts>
        #include <iostream>

        template <std::integral T>                 // T must be an integer type
        T gcd(T a, T b) { return b == 0 ? a : gcd(b, a % b); }

        auto half(std::floating_point auto x) { return x / 2; }      // abbreviated syntax

        template <typename T>
            requires std::totally_ordered<T>       // requires-clause
        const T& clampTo(const T& v, const T& lo, const T& hi) { return v < lo ? lo : hi < v ? hi : v; }

        int main() {
            std::cout << gcd(48, 18) << ' ' << half(5.0) << ' ' << clampTo(15, 0, 10) << '\n';
            // gcd(4.5, 1.5);   // error: constraints not satisfied — 'double' is not integral
        }
    ''', out="6 2.5 10")
    yield snippet("cpp", r'''
        #include <concepts>
        template <std::integral T>
        T gcd(T a, T b) { return b == 0 ? a : gcd(b, a % b); }
        int main() { return static_cast<int>(gcd(4.5, 1.5)); }
    ''', fails=True, caption="C++ — constraint violated")
    yield output('''
        error: no matching function for call to 'gcd'
        note: candidate template ignored: constraints not satisfied [with T = double]
        note: because 'double' does not satisfy 'integral'
    ''', caption="Compiler error — short and to the point")
    yield section("Defining a concept", "puzzle")
    yield snippet("cpp", r'''
        #include <concepts>
        #include <iostream>
        #include <string>
        #include <vector>

        template <typename T>
        concept Shape = requires(const T& s) {
            { s.area() } -> std::convertible_to<double>;    // must have area() returning something double-like
            { s.name() } -> std::convertible_to<std::string>;
        };

        struct Square { double side; double area() const { return side * side; } std::string name() const { return "square"; } };
        struct Blob   { int size; };

        void report(const Shape auto& s) { std::cout << s.name() << ": " << s.area() << '\n'; }

        template <typename T>
        concept Container = requires(T c) { c.begin(); c.end(); c.size(); };

        void info(const Container auto& c) { std::cout << "container of " << c.size() << '\n'; }
        void info(const auto&)            { std::cout << "not a container\n"; }   // less constrained fallback

        int main() {
            report(Square{3});
            // report(Blob{1});   // error: Blob does not satisfy Shape
            info(std::vector<int>{1, 2});
            info(42);
            std::cout << Shape<Square> << Shape<Blob> << '\n';     // concepts are bool constants
        }
    ''', out='''
        square: 9
        container of 2
        not a container
        10
    ''')
    yield table(
        ["Concept (`<concepts>`, `<iterator>`, `<ranges>`)", "Satisfied when"],
        ["`std::integral`, `std::floating_point`", "Built-in integer / floating type"],
        ["`std::same_as<T, U>`, `std::convertible_to<From, To>`", "Type relationships"],
        ["`std::equality_comparable`, `std::totally_ordered`", "`==` / `<` etc. work"],
        ["`std::copyable`, `std::movable`, `std::default_initializable`", "Object capabilities"],
        ["`std::invocable<F, Args...>`, `std::predicate<F, Args...>`", "Callable with those arguments"],
        ["`std::ranges::range`, `std::random_access_iterator`", "Range / iterator categories"],
    )
    yield section("Four ways to write a constraint", "list")
    yield snippet("cpp", r'''
        #include <concepts>
        template <std::integral T> T a(T x) { return x; }                  // 1. constrained parameter
        template <typename T> requires std::integral<T> T b(T x) { return x; }   // 2. requires-clause
        template <typename T> T c(T x) requires std::integral<T> { return x; }   // 3. trailing requires
        std::integral auto d(std::integral auto x) { return x; }           // 4. abbreviated
    ''', caption="C++ — equivalent forms")
    yield qa("What problem do concepts solve compared with plain templates?",
             "Plain templates accept any type and fail deep inside the implementation with pages of errors. Concepts state requirements in the interface: misuse is rejected at the call site with a short message, overloads can be selected by capability (more-constrained wins), and the code documents itself. They replace most `enable_if`/SFINAE tricks.")
