from kit import *

G = "Copy, Move & Smart Pointers"


@topic(G, "copy-semantics", "Copy Semantics: Shallow vs Deep", "copy")
def _():
    yield lead("Copying an object calls its copy constructor (new object) or copy assignment operator (existing object). If the class owns a raw resource, the default member-wise copy is *shallow* — and wrong.")
    yield section("Copy constructor vs copy assignment", "equal")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Tag {
            int v = 0;
            Tag() = default;
            Tag(const Tag& o) : v(o.v) { std::cout << "copy ctor\n"; }
            Tag& operator=(const Tag& o) { v = o.v; std::cout << "copy assign\n"; return *this; }
        };
        void byValue(Tag) {}
        int main() {
            Tag a;
            Tag b = a;       // copy ctor: b is being created (the '=' here is not assignment)
            Tag c(a);        // copy ctor
            c = b;           // copy assignment: c already exists
            byValue(a);      // copy ctor for the parameter
        }
    ''', out='''
        copy ctor
        copy ctor
        copy assign
        copy ctor
    ''')
    yield section("The shallow-copy bug", "bug")
    yield snippet("cpp", r'''
        #include <cstring>
        class Buffer {
            char* data_;
        public:
            explicit Buffer(const char* s) : data_(new char[std::strlen(s) + 1]) { std::strcpy(data_, s); }
            ~Buffer() { delete[] data_; }
            // no copy constructor → the compiler copies the *pointer*
        };
        int main() {
            Buffer a("hello");
            Buffer b = a;        // b.data_ == a.data_
        }                        // both destructors delete[] the same block → double free
    ''', fails=True, caption="C++ — double free (ASan)")
    yield section("Deep copy done right", "copy-check")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <cstring>
        #include <iostream>
        #include <utility>

        class Buffer {
            std::size_t size_;
            char* data_;
        public:
            explicit Buffer(const char* s) : size_(std::strlen(s)), data_(new char[size_ + 1]) {
                std::copy(s, s + size_ + 1, data_);
            }
            ~Buffer() { delete[] data_; }

            Buffer(const Buffer& o) : size_(o.size_), data_(new char[o.size_ + 1]) {   // deep copy
                std::copy(o.data_, o.data_ + size_ + 1, data_);
            }
            Buffer& operator=(Buffer o) {          // copy-and-swap: `o` is already a copy
                swap(*this, o);                    // take its contents; old ones die with `o`
                return *this;
            }
            friend void swap(Buffer& a, Buffer& b) noexcept {
                std::swap(a.size_, b.size_);
                std::swap(a.data_, b.data_);
            }
            void set(std::size_t i, char c) { data_[i] = c; }
            const char* str() const { return data_; }
        };

        int main() {
            Buffer a("hello");
            Buffer b = a;          // independent copy
            b.set(0, 'j');
            Buffer c("x");
            c = a;                 // assignment
            Buffer& alias = c;
            c = alias;             // self-assignment is safe
            std::cout << a.str() << ' ' << b.str() << ' ' << c.str() << '\n';
        }
    ''', out="hello jello hello")
    yield note("Copy-and-swap gives the **strong exception guarantee** (if the copy throws, `*this` is untouched) and handles self-assignment for free.", "Copy-and-swap")
    yield dodont("Hold resources in members that already know how to copy themselves (`std::string`, `std::vector`, `std::unique_ptr`) — then you write *no* copy code at all (Rule of Zero).", "Owning raw pointers (`char*`, `T*` from `new`) in a class without writing — or deleting — the copy operations.")
    yield qa("What's the difference between a shallow and a deep copy?",
             "A shallow copy duplicates the member values, so two objects' pointers end up pointing at the same resource (leading to double frees and aliasing bugs). A deep copy allocates a fresh resource and copies the pointed-to contents, giving each object its own.")
    yield qa("When is the copy constructor called?",
             "When a new object is initialised from an existing one: `T b = a;`, `T b(a);`, passing by value, returning by value (unless elided), throwing/catching by value, and when containers copy elements.")


@topic(G, "move-semantics", "Move Semantics & rvalue References", "arrow-move-right")
def _():
    yield lead("Moving transfers a resource from an object that's about to die (or that you no longer need) instead of copying it. A `std::vector` move is three pointer copies — no matter how many elements it holds.")
    yield section("Copy vs move", "arrows-right-left")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <utility>
        #include <vector>

        int main() {
            std::vector<int> a(1'000'000, 7);
            std::vector<int> b = a;               // copy: allocates and copies a million ints
            std::vector<int> c = std::move(a);    // move: steals a's buffer
            std::cout << a.size() << ' ' << b.size() << ' ' << c.size() << '\n';   // a is now empty (valid, unspecified)

            std::string s = "a fairly long string that will not fit in SSO";
            std::vector<std::string> names;
            names.push_back(s);                   // copies
            names.push_back(std::move(s));        // moves — s is left valid but unspecified
            std::cout << names.size() << ' ' << names[1].size() << '\n';
        }
    ''', out='''
        0 1000000 1000000
        2 45
    ''')
    yield section("Writing move operations", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <utility>

        class Buffer {
            int* data_ = nullptr;
            std::size_t size_ = 0;
        public:
            explicit Buffer(std::size_t n) : data_(new int[n]{}), size_(n) {}
            ~Buffer() { delete[] data_; }

            Buffer(const Buffer& o) : data_(new int[o.size_]), size_(o.size_) {
                std::copy(o.data_, o.data_ + size_, data_);
                std::cout << "copy\n";
            }
            Buffer(Buffer&& o) noexcept                                        // move constructor
                : data_(std::exchange(o.data_, nullptr)), size_(std::exchange(o.size_, 0)) {
                std::cout << "move\n";
            }
            Buffer& operator=(Buffer&& o) noexcept {                           // move assignment
                if (this != &o) {
                    delete[] data_;
                    data_ = std::exchange(o.data_, nullptr);
                    size_ = std::exchange(o.size_, 0);
                }
                return *this;
            }
            Buffer& operator=(const Buffer&) = delete;   // kept short for the example
            std::size_t size() const { return size_; }
        };

        Buffer make() { return Buffer(8); }             // guaranteed elision: no copy, no move

        int main() {
            Buffer a(4);
            Buffer b = std::move(a);        // move
            Buffer c = b;                   // copy
            Buffer d = make();              // nothing printed
            d = std::move(c);               // move assignment
            std::cout << a.size() << ' ' << b.size() << ' ' << c.size() << ' ' << d.size() << '\n';
        }
    ''', out='''
        move
        copy
        0 4 0 4
    ''')
    yield steps(
        ("Steal", "Take the source's pointers/handles."),
        ("Reset the source", "Leave it in a valid, destructible state (usually empty) — `std::exchange(o.p, nullptr)` does both in one step."),
        ("Mark `noexcept`", "`std::vector` only moves elements during reallocation if the move constructor is `noexcept`; otherwise it copies to keep the strong guarantee."),
    )
    yield section("Why `noexcept` matters", "shield-check")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        struct Safe   { Safe() = default;   Safe(const Safe&)   { std::cout << "C"; } Safe(Safe&&) noexcept { std::cout << "M"; } };
        struct Unsafe { Unsafe() = default; Unsafe(const Unsafe&) { std::cout << "C"; } Unsafe(Unsafe&&)       { std::cout << "M"; } };
        int main() {
            std::vector<Safe> a(2);
            a.reserve(10);             // reallocation moves the 2 elements
            std::cout << '\n';
            std::vector<Unsafe> b(2);
            b.reserve(10);             // reallocation copies — the move might throw
            std::cout << '\n';
        }
    ''', out='''
        MM
        CC
    ''')
    yield section("Pitfalls", "alert-triangle")
    yield ul(
        "`std::move` only *casts*; if the type has no move constructor, the copy constructor is used.",
        "Don't use a moved-from object except to assign to it or destroy it (standard types guarantee “valid but unspecified”).",
        "`return std::move(local);` **prevents** copy elision — just `return local;` (it's moved automatically if not elided).",
        "`const` objects can't be moved from: `std::move(constObj)` yields `const T&&`, which binds to the copy constructor.",
    )
    yield qa("What is an rvalue reference?",
             "A reference declared with `&&` that binds only to rvalues (temporaries or objects cast with `std::move`). It lets a function overload specifically for “this object is expiring”, so it can steal resources instead of copying. Inside the function, a named rvalue reference is itself an lvalue.")
    yield qa("Why should move constructors be noexcept?",
             "Containers like `std::vector` promise the strong exception guarantee when growing. They can only move elements into the new buffer if moving can't throw (otherwise a half-moved vector couldn't be restored), so they check `std::is_nothrow_move_constructible` and fall back to copying.")


@topic(G, "rule-of-three-five-zero", "Rule of 0 / 3 / 5", "rulers")
def _():
    yield lead("If a class needs a custom destructor, copy or move operation, it almost certainly needs all of them. Better still: design so it needs none.")
    yield section("The rules", "list-numbers")
    yield cards(
        ("Rule of Three (C++98)", "If you define any of *destructor*, *copy constructor*, *copy assignment*, define all three.", "number-3"),
        ("Rule of Five (C++11)", "Add *move constructor* and *move assignment*: define or `=delete` all five together.", "number-5"),
        ("Rule of Zero", "Don't manage resources by hand. Use members that manage themselves (`std::string`, `std::vector`, `std::unique_ptr`) and write **none** of the five.", "number-0"),
    )
    yield section("Rule of Zero in practice", "circle-check")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>
        #include <vector>

        class Document {                                    // no destructor, no copy/move code
            std::string title_;
            std::vector<std::string> lines_;
            std::unique_ptr<int> cache_ = std::make_unique<int>(0);   // move-only member
        public:
            explicit Document(std::string t) : title_(std::move(t)) {}
            void add(std::string line) { lines_.push_back(std::move(line)); }
            std::size_t size() const { return lines_.size(); }
        };

        int main() {
            Document d("notes");
            d.add("line 1");
            Document moved = std::move(d);   // compiler-generated move: correct automatically
            std::cout << moved.size() << ' ' << d.size() << '\n';
            // Document copy = moved;        // error: unique_ptr member makes it move-only
        }
    ''', out="1 0")
    yield section("Rule of Five, spelled out", "number-5")
    yield snippet("cpp", r'''
        #include <utility>

        class Handle {
            int* res_ = nullptr;
        public:
            explicit Handle(int v) : res_(new int(v)) {}
            ~Handle() { delete res_; }                                                   // 1 destructor
            Handle(const Handle& o) : res_(o.res_ ? new int(*o.res_) : nullptr) {}       // 2 copy ctor
            Handle& operator=(const Handle& o) {                                          // 3 copy assign
                Handle tmp(o);
                std::swap(res_, tmp.res_);
                return *this;
            }
            Handle(Handle&& o) noexcept : res_(std::exchange(o.res_, nullptr)) {}         // 4 move ctor
            Handle& operator=(Handle&& o) noexcept {                                      // 5 move assign
                std::swap(res_, o.res_);                                                  //   old value dies with o
                return *this;
            }
        };
    ''', caption="C++ — all five special members")
    yield section("What declaring one member suppresses", "table")
    yield table(
        ["You declare…", "Default ctor", "Copy ops", "Move ops"],
        ["Nothing", "Generated", "Generated", "Generated"],
        ["Any constructor", "**Not generated**", "Generated", "Generated"],
        ["Destructor", "Generated", "Generated (deprecated)", "**Not generated** → moves become copies"],
        ["Copy ctor or copy assignment", "—", "The other is generated (deprecated)", "**Not generated**"],
        ["Move ctor or move assignment", "—", "**Deleted**", "The other is not generated"],
    )
    yield warn("Adding an empty `~T() {}` “for logging” silently removes a class's move operations: every “move” becomes a copy. If you must declare a destructor, also `= default` the move and copy operations.")
    yield qa("Explain the Rule of Zero.",
             "Classes that aren't specifically resource managers shouldn't declare any of the special member functions. Let RAII members (containers, smart pointers, strings) handle ownership; the compiler-generated copy/move/destructor then do the right thing, and the code is shorter and exception-safe.")


@topic(G, "unique-ptr", "Smart Pointers: unique_ptr", "key")
def _():
    yield lead("`std::unique_ptr<T>` is the sole owner of a heap object and deletes it when it goes out of scope. It's move-only, has zero overhead over a raw pointer, and should be your default for heap objects.")
    yield section("Basics", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>

        struct Widget {
            std::string name;
            explicit Widget(std::string n) : name(std::move(n)) { std::cout << "make " << name << '\n'; }
            ~Widget() { std::cout << "free " << name << '\n'; }
        };

        int main() {
            auto a = std::make_unique<Widget>("a");       // preferred way to create
            std::cout << a->name << ' ' << (*a).name << '\n';

            std::unique_ptr<Widget> b = std::move(a);     // ownership moves; copying is a compile error
            std::cout << (a == nullptr) << ' ' << b->name << '\n';

            b.reset(new Widget("c"));                     // frees "a", now owns "c"
            Widget* raw = b.get();                        // non-owning peek
            std::cout << raw->name << '\n';
            std::cout << "leaving main\n";
        }                                                  // "c" freed automatically
    ''', out='''
        make a
        a a
        1 a
        make c
        free a
        c
        leaving main
        free c
    ''')
    yield table(
        ["Operation", "Meaning"],
        ["`std::make_unique<T>(args...)`", "Allocate and construct (exception-safe)"],
        ["`p.get()`", "Raw pointer, ownership kept"],
        ["`p.release()`", "Give up ownership — returns the raw pointer (you must delete it)"],
        ["`p.reset(q)`", "Delete current object, take ownership of `q` (or none)"],
        ["`std::move(p)`", "Transfer ownership"],
        ["`if (p)`", "Is it non-null?"],
        ["`std::make_unique<T[]>(n)`", "Array form — uses `delete[]`"],
    )
    yield section("Ownership in function signatures", "arrows-exchange")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <vector>

        struct Node { int value; };

        std::unique_ptr<Node> create(int v) { return std::make_unique<Node>(v); }  // returns ownership
        void inspect(const Node& n) { std::cout << "value " << n.value << '\n'; }  // just uses it
        void store(std::vector<std::unique_ptr<Node>>& pool, std::unique_ptr<Node> n) {  // takes ownership
            pool.push_back(std::move(n));
        }

        int main() {
            std::vector<std::unique_ptr<Node>> pool;
            auto n = create(7);
            inspect(*n);
            store(pool, std::move(n));
            store(pool, create(9));
            std::cout << pool.size() << ' ' << pool[1]->value << ' ' << (n == nullptr) << '\n';
        }
    ''', out='''
        value 7
        2 9 1
    ''')
    yield note("Pass `unique_ptr` by value only to *transfer* ownership. A function that just uses the object should take `T&`, `const T&` or `T*` — it shouldn't care how the object is owned.", "Guideline")
    yield section("Custom deleters", "trash")
    yield snippet("cpp", r'''
        #include <cstdio>
        #include <iostream>
        #include <memory>

        int main() {
            auto closer = [](std::FILE* f) { std::fclose(f); std::cout << "closed\n"; };
            {
                std::unique_ptr<std::FILE, decltype(closer)> file(std::fopen("up_demo.txt", "w"), closer);
                std::fputs("data", file.get());
            }
            std::remove("up_demo.txt");
        }
    ''', out="closed")
    yield section("Polymorphism & the pimpl idiom", "hierarchy")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <vector>

        struct Shape { virtual ~Shape() = default; virtual double area() const = 0; };
        struct Square : Shape { double s; explicit Square(double x) : s(x) {} double area() const override { return s * s; } };
        struct Circle : Shape { double r; explicit Circle(double x) : r(x) {} double area() const override { return 3.0 * r * r; } };

        int main() {
            std::vector<std::unique_ptr<Shape>> shapes;
            shapes.push_back(std::make_unique<Square>(2));
            shapes.push_back(std::make_unique<Circle>(1));
            double total = 0;
            for (const auto& s : shapes) total += s->area();
            std::cout << total << '\n';
        }
    ''', out="7")
    yield qa("Why prefer make_unique over unique_ptr<T>(new T)?",
             "It's shorter, never mentions `new`, and is exception-safe in expressions like `f(std::unique_ptr<A>(new A), g())` (before C++17 the `new A` could run, then `g()` throw, leaking A). It also keeps the “no naked new” rule easy to check.")
    yield qa("What is the overhead of unique_ptr?",
             "None in practice: with the default (stateless) deleter it is exactly one pointer in size, and `get()`, `*` and `->` compile to the same instructions as a raw pointer. The destructor just calls `delete`.")


@topic(G, "shared-weak-ptr", "shared_ptr & weak_ptr", "share")
def _():
    yield lead("`std::shared_ptr` allows *shared* ownership through reference counting; the object is destroyed when the last owner lets go. `std::weak_ptr` observes without owning — the cure for reference cycles.")
    yield section("Reference counting", "users")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>

        struct Texture {
            std::string file;
            explicit Texture(std::string f) : file(std::move(f)) {}
            ~Texture() { std::cout << "unload " << file << '\n'; }
        };

        int main() {
            auto tex = std::make_shared<Texture>("grass.png");   // count = 1
            std::cout << tex.use_count() << '\n';
            {
                auto sprite1 = tex;                               // count = 2
                std::shared_ptr<Texture> sprite2 = tex;           // count = 3
                std::cout << tex.use_count() << '\n';
            }                                                     // back to 1
            std::cout << tex.use_count() << '\n';
            tex.reset();                                          // 0 → destroyed
            std::cout << "done\n";
        }
    ''', out='''
        1
        3
        1
        unload grass.png
        done
    ''')
    yield section("How it works", "settings")
    yield p("A `shared_ptr` is two pointers: one to the object, one to a **control block** holding the strong count, the weak count and the deleter. `make_shared` allocates object and control block in *one* allocation.")
    yield table(
        ["", "`unique_ptr`", "`shared_ptr`"],
        ["Owners", "Exactly one", "Many"],
        ["Copyable", "No (move only)", "Yes (increments the count)"],
        ["Size", "1 pointer", "2 pointers"],
        ["Cost", "Free", "Atomic increments/decrements on copy/destroy"],
        ["Default choice?", "**Yes**", "Only when ownership is genuinely shared"],
    )
    yield section("Cycles leak — `weak_ptr` breaks them", "refresh-alert")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>

        struct Employee;
        struct Team {
            std::string name;
            std::shared_ptr<Employee> lead;         // owns its lead
            ~Team() { std::cout << "~Team\n"; }
        };
        struct Employee {
            std::string name;
            std::weak_ptr<Team> team;               // observes: does NOT keep the team alive
            ~Employee() { std::cout << "~Employee\n"; }
        };

        int main() {
            auto team = std::make_shared<Team>();
            auto ada = std::make_shared<Employee>();
            team->name = "core";
            team->lead = ada;
            ada->team = team;
            if (auto t = ada->team.lock())          // lock(): shared_ptr if still alive, else empty
                std::cout << "ada is in " << t->name << '\n';
            std::cout << team.use_count() << ' ' << ada.use_count() << '\n';
        }   // both destroyed; with shared_ptr in both directions neither destructor would run
    ''', out='''
        ada is in core
        1 2
        ~Team
        ~Employee
    ''')
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        int main() {
            std::weak_ptr<int> watcher;
            {
                auto p = std::make_shared<int>(42);
                watcher = p;
                std::cout << watcher.expired() << ' ' << *watcher.lock() << '\n';
            }
            std::cout << watcher.expired() << ' ' << (watcher.lock() == nullptr) << '\n';
        }
    ''', out='''
        0 42
        1 1
    ''')
    yield section("`enable_shared_from_this`", "arrow-back")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>

        struct Session : std::enable_shared_from_this<Session> {
            std::shared_ptr<Session> self() { return shared_from_this(); }   // NOT shared_ptr<Session>(this)!
        };

        int main() {
            auto s = std::make_shared<Session>();
            auto again = s->self();
            std::cout << s.use_count() << '\n';     // shares the same control block
        }
    ''', out="2")
    yield warn("Never create two `shared_ptr`s from the same raw pointer (`std::shared_ptr<T> a(raw), b(raw);`) — each gets its own control block and both delete the object. Create once with `make_shared` and copy the `shared_ptr`.")
    yield qa("Is shared_ptr thread-safe?",
             "The reference count is updated atomically, so copying and destroying *different* `shared_ptr` instances that share an object is safe across threads. Accessing the *pointed-to object*, or modifying the *same* `shared_ptr` instance from several threads, still needs synchronisation (C++20 offers `std::atomic<std::shared_ptr<T>>`).")
    yield qa("When would you use weak_ptr?",
             "To break ownership cycles (child → parent back-links, observer lists), and for caches that should not keep objects alive: `lock()` tells you whether the object still exists and gives you temporary ownership while you use it.")
