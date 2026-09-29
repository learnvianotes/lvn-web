from kit import *

G = "Classes & Objects"


@topic(G, "classes-objects", "Classes & Objects", "box")
def _():
    yield lead("A class bundles data (members) with the functions that operate on it (member functions), and controls access with `public`, `private` and `protected`.")
    yield define("Class", "a user-defined type. An **object** is an instance of it. The class's *invariant* (e.g. “balance is never negative”) is protected by keeping data `private` and changing it only through member functions.")
    yield section("Defining a class", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>
        #include <string>

        class BankAccount {
        public:                                          // the interface
            BankAccount(std::string owner, double balance)
                : owner_(std::move(owner)), balance_(balance) {}

            void deposit(double amount) {
                if (amount <= 0) throw std::invalid_argument("amount must be positive");
                balance_ += amount;
            }
            bool withdraw(double amount) {
                if (amount > balance_) return false;     // invariant: balance_ >= 0
                balance_ -= amount;
                return true;
            }
            double balance() const { return balance_; }  // const: doesn't modify the object
            const std::string& owner() const { return owner_; }

        private:                                         // the implementation
            std::string owner_;
            double balance_;
        };

        int main() {
            BankAccount acc("Ada", 100);
            acc.deposit(50);
            std::cout << acc.withdraw(500) << ' ' << acc.withdraw(30) << '\n';
            std::cout << acc.owner() << ": " << acc.balance() << '\n';
            // acc.balance_ = 1e9;   // error: 'balance_' is a private member
        }
    ''', out='''
        0 1
        Ada: 120
    ''')
    yield table(
        ["Access", "Accessible from"],
        ["`public`", "Anywhere"],
        ["`protected`", "The class, its friends and derived classes"],
        ["`private`", "Only the class itself and its friends"],
    )
    yield section("`struct` vs `class`", "git-compare")
    yield p("They are the same thing except for defaults: `struct` members and bases are **public** by default, `class` ones **private**. Convention: `struct` for plain data bundles, `class` when there's an invariant to protect.")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Point {                  // aggregate: public data, no constructors needed
            int x = 0;
            int y = 0;
            int manhattan() const { return (x < 0 ? -x : x) + (y < 0 ? -y : y); }
        };
        int main() {
            Point p{3, -4};                        // aggregate initialisation
            Point q{.x = 1, .y = 2};               // designated initialisers (C++20)
            std::cout << p.manhattan() << ' ' << q.y << '\n';
        }
    ''', out="7 2")
    yield section("`const` member functions & `this`", "lock")
    yield snippet("cpp", r'''
        #include <iostream>
        class Counter {
            int value_ = 0;
            mutable int reads_ = 0;               // mutable: may change even in const functions
        public:
            Counter& increment() { ++value_; return *this; }   // return *this to allow chaining
            int value() const { ++reads_; return value_; }
            int reads() const { return reads_; }
        };
        int main() {
            Counter c;
            c.increment().increment().increment();
            const Counter& view = c;
            std::cout << view.value() << ' ' << view.value() << ' ' << view.reads() << '\n';
            // view.increment();    // error: increment() is not const
        }
    ''', out="3 3 2")
    yield ul(
        "`this` is a pointer to the object the member function was called on; `*this` is the object.",
        "A `const` member function gets a `const T* this` — it can't modify members (except `mutable` ones) or call non-const members.",
        "Only `const` member functions can be called on `const` objects and through `const&` — so mark every non-mutating function `const`.",
    )
    yield section("Declaring in a header, defining in a `.cpp`", "files")
    yield snippet("cpp", r'''
        #include <iostream>
        class Circle {
        public:
            explicit Circle(double r);
            double area() const;           // declared here (header)
        private:
            double r_;
        };

        Circle::Circle(double r) : r_(r) {}                 // defined outside with ClassName::
        double Circle::area() const { return 3.14159 * r_ * r_; }

        int main() { std::cout << Circle(2).area() << '\n'; }
    ''', out="12.5664")
    yield qa("What are the four pillars of OOP and how does C++ express them?",
             "**Encapsulation** — `private` data + public member functions. **Abstraction** — abstract classes / pure interfaces. **Inheritance** — `class D : public B`. **Polymorphism** — virtual functions (run time) and overloading/templates (compile time).")
    yield qa("What is the size of an object?",
             "The sum of its non-static data members plus padding (and a vptr if it has virtual functions). Member functions and static members don't take space in each object. An empty class has size 1.")


@topic(G, "constructors", "Constructors", "hammer")
def _():
    yield lead("A constructor initialises an object when it is created. C++ has default, parameterised, copy and move constructors, plus member initializer lists, delegation and `explicit`.")
    yield section("Kinds of constructors", "list")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        class Person {
        public:
            Person() : name_("anonymous"), age_(0) { std::cout << "default\n"; }
            Person(std::string name, int age) : name_(std::move(name)), age_(age) { std::cout << "param\n"; }
            Person(const Person& o) : name_(o.name_), age_(o.age_) { std::cout << "copy\n"; }
            Person(Person&& o) noexcept : name_(std::move(o.name_)), age_(o.age_) { std::cout << "move\n"; }
            void show() const { std::cout << name_ << " (" << age_ << ")\n"; }
        private:
            std::string name_;
            int age_;
        };

        int main() {
            Person a;                   // default
            Person b("Ada", 36);        // parameterised
            Person c = b;               // copy
            Person d = std::move(b);    // move
            a.show(); c.show(); d.show();
        }
    ''', out='''
        default
        param
        copy
        move
        anonymous (0)
        Ada (36)
        Ada (36)
    ''')
    yield section("Member initializer lists", "list-check")
    yield p("Members are initialised *before* the constructor body runs. Initialise them in the list — assigning in the body means default-construct first, then assign. `const` members, references and members without a default constructor **must** use the list.")
    yield snippet("cpp", r'''
        #include <iostream>
        class Config {
            const int maxUsers_;          // const: must be initialised, can't be assigned
            int& counter_;                // reference: same
            int timeout_ = 30;            // default member initializer (C++11)
        public:
            Config(int maxUsers, int& counter) : maxUsers_(maxUsers), counter_(counter) { ++counter_; }
            Config(int maxUsers, int& counter, int timeout) : Config(maxUsers, counter) {   // delegating
                timeout_ = timeout;
            }
            void show() const { std::cout << maxUsers_ << ' ' << timeout_ << ' ' << counter_ << '\n'; }
        };
        int main() {
            int created = 0;
            Config a(10, created);
            Config b(20, created, 5);
            a.show();
            b.show();
        }
    ''', out='''
        10 30 2
        20 5 2
    ''')
    yield warn("Members are initialised in the order they are **declared in the class**, not the order in the initializer list. `B(int v) : b_(v), a_(b_) {}` with `a_` declared first reads `b_` before it's initialised. (`-Wall` warns about the mismatch.)")
    yield section("`explicit`", "hand-stop")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Meters {
            double v;
            explicit Meters(double x) : v(x) {}      // no implicit double → Meters
        };
        struct Label {
            int id;
            Label(int i) : id(i) {}                  // implicit conversion allowed
        };
        void run(Meters m) { std::cout << m.v << "m\n"; }
        void print(Label l) { std::cout << "#" << l.id << '\n'; }
        int main() {
            run(Meters(5));       // must be explicit
            print(42);            // 42 silently becomes a Label — often surprising
            // run(5.0);          // error: no implicit conversion
        }
    ''', out='''
        5m
        #42
    ''')
    yield note("Mark single-argument constructors `explicit` unless the implicit conversion is genuinely natural (like `std::string` from `const char*`).", "Guideline")
    yield section("Compiler-generated constructors", "robot")
    yield table(
        ["Special member", "Generated when…"],
        ["Default constructor `T()`", "You declare **no** constructors at all"],
        ["Copy constructor / copy assignment", "You don't declare a move operation (deprecated if you declare a destructor)"],
        ["Move constructor / move assignment", "You declare **none** of: copy ops, move ops, destructor"],
        ["Destructor", "You don't declare one"],
    )
    yield snippet("cpp", r'''
        #include <iostream>
        struct Widget {
            int size = 1;
            Widget() = default;                  // bring back the default ctor alongside another one
            explicit Widget(int s) : size(s) {}
            Widget(const Widget&) = delete;      // forbid copying
        };
        int main() {
            Widget a;
            Widget b(5);
            std::cout << a.size << ' ' << b.size << '\n';
            // Widget c = b;   // error: call to deleted constructor
        }
    ''', out="1 5")
    yield section("The most vexing parse", "confused")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Timer { int ticks = 0; };
        int main() {
            Timer t{};        // an object
            // Timer u();     // declares a *function* u returning Timer — not an object!
            std::cout << t.ticks << '\n';
        }
    ''', out="0")
    yield qa("Why initialise members in the initializer list rather than the constructor body?",
             "Because members are always initialised before the body runs. Assigning in the body means default-constructing then assigning (wasteful for strings/containers), and it's impossible for `const` members, references and types without a default constructor.")
    yield qa("Can a constructor be virtual?",
             "No. When a constructor runs, the object's dynamic type is being built, so there's nothing to dispatch on yet. For “virtual construction” use a factory function or a virtual `clone()` method.")


@topic(G, "destructors-raii", "Destructors & RAII", "recycle")
def _():
    yield lead("A destructor `~T()` runs automatically when an object's lifetime ends. **RAII** ties a resource (memory, file, lock, socket) to an object so the destructor always releases it — even when an exception is thrown.")
    yield define("RAII", "*Resource Acquisition Is Initialization*: acquire the resource in the constructor, release it in the destructor. The object's scope becomes the resource's lifetime.")
    yield section("Destructor basics", "trash")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        struct Noisy {
            std::string name;
            explicit Noisy(std::string n) : name(std::move(n)) { std::cout << "ctor " << name << '\n'; }
            ~Noisy() { std::cout << "dtor " << name << '\n'; }
        };

        int main() {
            Noisy a("a");
            {
                Noisy b("b");
                Noisy c("c");
            }                             // c then b destroyed here — reverse order
            Noisy d("d");
            std::cout << "end of main\n";
        }                                 // d then a
    ''', out='''
        ctor a
        ctor b
        ctor c
        dtor c
        dtor b
        ctor d
        end of main
        dtor d
        dtor a
    ''')
    yield section("Writing an RAII wrapper", "file")
    yield snippet("cpp", r'''
        #include <cstdio>
        #include <iostream>
        #include <stdexcept>

        class File {
            std::FILE* f_;
        public:
            File(const char* path, const char* mode) : f_(std::fopen(path, mode)) {
                if (!f_) throw std::runtime_error("cannot open file");
            }
            ~File() { std::fclose(f_); std::cout << "file closed\n"; }
            File(const File&) = delete;              // one owner only
            File& operator=(const File&) = delete;
            std::FILE* get() const { return f_; }
        };

        void process() {
            File out("raii_demo.txt", "w");
            std::fputs("hello\n", out.get());
            throw std::runtime_error("something failed");   // destructor still closes the file
        }

        int main() {
            try { process(); } catch (const std::exception& e) { std::cout << "caught: " << e.what() << '\n'; }
            std::remove("raii_demo.txt");
        }
    ''', out='''
        file closed
        caught: something failed
    ''')
    yield cards(
        ("Memory", "`std::unique_ptr`, `std::shared_ptr`, `std::vector`, `std::string`", "database"),
        ("Locks", "`std::lock_guard`, `std::unique_lock`, `std::scoped_lock`", "lock"),
        ("Files & streams", "`std::ifstream` / `std::ofstream` close on destruction", "file-text"),
        ("Threads", "`std::jthread` joins on destruction", "arrows-split"),
    )
    yield section("Scope guards", "shield")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <utility>

        template <class F>
        class ScopeExit {                       // run any cleanup when the scope ends
            F fn_;
        public:
            explicit ScopeExit(F fn) : fn_(std::move(fn)) {}
            ~ScopeExit() { fn_(); }
            ScopeExit(const ScopeExit&) = delete;
            ScopeExit& operator=(const ScopeExit&) = delete;
        };

        int main() {
            int depth = 0;
            {
                ++depth;
                ScopeExit restore([&] { --depth; std::cout << "restored\n"; });
                std::cout << "depth " << depth << '\n';
            }
            std::cout << "depth " << depth << '\n';
        }
    ''', out='''
        depth 1
        restored
        depth 0
    ''')
    yield warn("Destructors should never throw. They're implicitly `noexcept`; if one throws while the stack is already unwinding due to another exception, `std::terminate` is called.")
    yield qa("Why doesn't C++ need a garbage collector?",
             "Because resources are owned by objects with deterministic lifetimes: when the owner goes out of scope its destructor frees them. Containers and smart pointers apply RAII to memory; the same technique also handles non-memory resources (files, locks, sockets) that a GC wouldn't close promptly.")
    yield qa("When is a destructor called?",
             "Automatic objects: at the end of their scope (including during exception unwinding). Static objects: after `main` returns. Heap objects: on `delete` (or when the owning smart pointer releases them). Temporaries: at the end of the full expression. Members and bases: after the containing object's destructor body, in reverse declaration order.")


@topic(G, "operator-overloading", "Operator Overloading", "math-symbols")
def _():
    yield lead("You can give operators like `+`, `==`, `<<` and `[]` a meaning for your own types, so they read like built-ins. Overload only when the meaning is obvious.")
    yield section("A value type with arithmetic", "plus")
    yield snippet("cpp", r'''
        #include <iostream>

        struct Vec2 {
            double x = 0, y = 0;

            Vec2& operator+=(const Vec2& o) { x += o.x; y += o.y; return *this; }   // member: modifies *this
            Vec2 operator-() const { return {-x, -y}; }                             // unary minus
            bool operator==(const Vec2&) const = default;                           // C++20: memberwise ==
        };

        Vec2 operator+(Vec2 a, const Vec2& b) { return a += b; }        // non-member, built from +=
        Vec2 operator*(const Vec2& v, double k) { return {v.x * k, v.y * k}; }
        Vec2 operator*(double k, const Vec2& v) { return v * k; }         // allow 2 * v too

        std::ostream& operator<<(std::ostream& os, const Vec2& v) {       // printing
            return os << '(' << v.x << ", " << v.y << ')';
        }

        int main() {
            Vec2 a{1, 2}, b{3, 4};
            std::cout << a + b << ' ' << -a << ' ' << 2 * b << '\n';
            a += b;
            std::cout << a << ' ' << (a == Vec2{4, 6}) << ' ' << (a != b) << '\n';
        }
    ''', out='''
        (4, 6) (-1, -2) (6, 8)
        (4, 6) 1 1
    ''')
    yield section("Member or non-member?", "arrows-split")
    yield table(
        ["Operator", "Usually", "Why"],
        ["`=`, `[]`, `()`, `->`, conversion", "**Must** be members", "Language rule"],
        ["`+=`, `-=`, `++`, `--`, unary ops", "Member", "They modify / belong to `*this`"],
        ["`+`, `-`, `*`, `==`, `<`", "Non-member (often `friend`)", "Symmetric: allows conversions on *both* sides (`2 * v`)"],
        ["`<<`, `>>` (streams)", "Non-member", "Left operand is the stream, not your type"],
    )
    yield section("Comparison with `<=>` (C++20)", "arrows-sort")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <compare>
        #include <iostream>
        #include <string>
        #include <vector>

        struct Version {
            int major, minor, patch;
            auto operator<=>(const Version&) const = default;   // generates <, <=, >, >=, == and !=
        };

        struct Employee {
            std::string name;
            int salary;
            std::strong_ordering operator<=>(const Employee& o) const { return salary <=> o.salary; }
            bool operator==(const Employee& o) const { return salary == o.salary; }
        };

        int main() {
            std::cout << (Version{1, 2, 3} < Version{1, 10, 0}) << (Version{2, 0, 0} >= Version{1, 9, 9}) << '\n';
            std::vector<Employee> team{{"Bo", 50}, {"Al", 90}, {"Cy", 70}};
            std::sort(team.begin(), team.end());
            for (const auto& e : team) std::cout << e.name << ' ';
            std::cout << '\n';
        }
    ''', out='''
        11
        Bo Cy Al
    ''')
    yield section("Subscript, call, increment", "brackets")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>

        class IntArray {
            int data_[4] = {};
        public:
            int& operator[](std::size_t i) { return data_[i]; }              // non-const: allows writes
            const int& operator[](std::size_t i) const { return data_[i]; }  // const overload for const objects
        };

        struct Counter {
            int n = 0;
            Counter& operator++() { ++n; return *this; }                 // prefix
            Counter operator++(int) { Counter old = *this; ++n; return old; }   // postfix (dummy int)
            int operator()(int step) { return n += step; }               // call operator: a functor
            explicit operator bool() const { return n != 0; }            // conversion
        };

        int main() {
            IntArray a;
            a[2] = 7;
            std::cout << a[2] << '\n';
            Counter c;
            Counter before = c++;
            ++c;
            std::cout << before.n << ' ' << c.n << ' ' << c(10) << ' ' << static_cast<bool>(c) << '\n';
            if (c) std::cout << "non-zero\n";      // explicit bool still works in conditions
        }
    ''', out='''
        7
        0 2 12 1
        non-zero
    ''')
    yield section("Copy assignment", "equal")
    yield p("`operator=` should return `*this` by reference and survive self-assignment. The *copy-and-swap* idiom gets both, plus exception safety — see **Copy Semantics**.")
    yield table(
        ["Can't overload", "Shouldn't overload"],
        ["`::`  `.`  `.*`  `?:`  `sizeof`  `typeid`", "`&&`, `||` (lose short-circuiting), `,`, unary `&`"],
    )
    yield warn("Keep the natural meaning: `+` shouldn't modify its operands, `==` must be symmetric and consistent with `!=`, and `<` must be a strict weak ordering if you want to use the type in `std::sort` or `std::map`.")
    yield qa("Why return a reference from operator+= but a value from operator+?",
             "`a += b` modifies `a` and yields `a` itself, so returning `*this` by reference allows chaining without copies. `a + b` produces a *new* value, leaving both operands untouched — returning a reference would dangle.")
    yield qa("Why is operator<< for streams a non-member function?",
             "The left operand of `std::cout << obj` is the stream. A member `operator<<` would have to be a member of `std::ostream`, which you can't modify. As a non-member it takes `(std::ostream&, const T&)` and returns the stream for chaining. Make it a `friend` if it needs private members.")


@topic(G, "static-members", "Static Members", "pin")
def _():
    yield lead("A `static` member belongs to the class itself, not to any object: one shared copy of a data member, and member functions callable without an object.")
    yield section("Static data and functions", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        class User {
        public:
            explicit User(std::string name) : name_(std::move(name)), id_(++created_) { ++alive_; }
            ~User() { --alive_; }
            User(const User&) = delete;

            static int alive() { return alive_; }       // no `this`: can only touch static members
            int id() const { return id_; }

            static constexpr int kMaxNameLength = 32;    // compile-time constant
        private:
            std::string name_;
            int id_;
            inline static int created_ = 0;              // C++17: define in-class with `inline`
            static int alive_;                           // classic: declared here…
        };
        int User::alive_ = 0;                            // …defined once in a .cpp

        int main() {
            User a("ada");
            {
                User b("bob");
                std::cout << User::alive() << ' ' << b.id() << '\n';
            }
            User c("cy");
            std::cout << User::alive() << ' ' << c.id() << ' ' << User::kMaxNameLength << '\n';
        }
    ''', out='''
        2 2
        2 3 32
    ''')
    yield table(
        ["", "Non-static member", "Static member"],
        ["Belongs to", "Each object", "The class (one copy)"],
        ["Access", "`obj.m`", "`Class::m` (or `obj.m`)"],
        ["Has `this`", "Yes", "No — can't use non-static members directly"],
        ["Can be `virtual` / `const`", "Yes", "No"],
    )
    yield section("Singleton & factory patterns", "building")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        class Logger {
        public:
            static Logger& instance() {            // Meyers singleton: thread-safe lazy init (C++11)
                static Logger logger;
                return logger;
            }
            void log(const std::string& msg) { std::cout << ++count_ << ": " << msg << '\n'; }
            Logger(const Logger&) = delete;
            Logger& operator=(const Logger&) = delete;
        private:
            Logger() = default;                    // nobody else can construct one
            int count_ = 0;
        };

        class Temperature {
            double kelvin_;
            explicit Temperature(double k) : kelvin_(k) {}
        public:
            static Temperature fromCelsius(double c) { return Temperature(c + 273.15); }   // named constructors
            static Temperature fromKelvin(double k)  { return Temperature(k); }
            double kelvin() const { return kelvin_; }
        };

        int main() {
            Logger::instance().log("start");
            Logger::instance().log("again");
            std::cout << Temperature::fromCelsius(25).kelvin() << '\n';
        }
    ''', out='''
        1: start
        2: again
        298.15
    ''')
    yield section("The many meanings of `static`", "list")
    yield table(
        ["Where", "Meaning"],
        ["Class member", "Shared by all objects"],
        ["Local variable", "Keeps its value between calls; initialised once"],
        ["Namespace-scope function/variable", "Internal linkage — private to this `.cpp` (prefer an anonymous namespace)"],
    )
    yield warn("Global and static objects in *different* `.cpp` files are initialised in an unspecified order (the *static initialisation order fiasco*). If one global's constructor uses another, wrap it in a function returning a function-local static.")
    yield qa("Why can't a static member function be const or virtual?",
             "Both are about `this`: `const` qualifies the object the function is called on, and virtual dispatch uses the object's vtable. A static member function has no object and no `this`.")


@topic(G, "friend", "Friend Functions & Classes", "users")
def _():
    yield lead("A `friend` declaration grants a specific function or class access to a class's private members — a controlled exception to encapsulation.")
    yield section("Friend function", "user")
    yield snippet("cpp", r'''
        #include <iostream>

        class Fraction {
            int num_, den_;
        public:
            Fraction(int n, int d) : num_(n), den_(d) {}
            friend std::ostream& operator<<(std::ostream& os, const Fraction& f) {   // hidden friend
                return os << f.num_ << '/' << f.den_;
            }
            friend Fraction operator*(const Fraction& a, const Fraction& b) {
                return {a.num_ * b.num_, a.den_ * b.den_};
            }
            friend bool sameValue(const Fraction& a, const Fraction& b);
        };

        bool sameValue(const Fraction& a, const Fraction& b) {    // defined outside, still a friend
            return a.num_ * b.den_ == b.num_ * a.den_;
        }

        int main() {
            Fraction half(1, 2), third(1, 3);
            std::cout << half * third << ' ' << sameValue(half, Fraction(2, 4)) << '\n';
        }
    ''', out="1/6 1")
    yield section("Friend class", "users-group")
    yield snippet("cpp", r'''
        #include <iostream>

        class Engine {
            int rpm_ = 0;
            friend class Mechanic;          // Mechanic may touch Engine's privates
        };

        class Mechanic {
        public:
            static void tune(Engine& e, int rpm) { e.rpm_ = rpm; }
            static int read(const Engine& e) { return e.rpm_; }
        };

        int main() {
            Engine e;
            Mechanic::tune(e, 3000);
            std::cout << Mechanic::read(e) << '\n';
        }
    ''', out="3000")
    yield ul(
        "Friendship is **granted, not taken** — the class decides who its friends are.",
        "It's **not symmetric** (A friend of B doesn't make B a friend of A), **not transitive**, and **not inherited**.",
        "A *hidden friend* (defined inside the class) is found only by argument-dependent lookup — the preferred way to write operators.",
    )
    yield dodont("Use friends for tightly coupled pairs: operators, stream I/O, a container and its iterator, test helpers.", "Using `friend` to dodge a design problem — if many outsiders need private access, the interface is wrong.")
    yield qa("Does friend break encapsulation?",
             "Used deliberately, it *strengthens* it: instead of adding public getters/setters that everyone can call, you grant access to one specific function that is logically part of the class's interface (like `operator<<`). The class still controls exactly who gets in.")
