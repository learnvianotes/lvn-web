from kit import *

G = "Inheritance & Polymorphism"


@topic(G, "inheritance", "Inheritance & Access Specifiers", "hierarchy")
def _():
    yield lead("A derived class inherits the members of its base class and can add or customise behaviour. Public inheritance models an **is-a** relationship.")
    yield section("Basics", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>

        class Animal {
        public:
            explicit Animal(std::string name) : name_(std::move(name)) { std::cout << "Animal()\n"; }
            ~Animal() { std::cout << "~Animal()\n"; }
            void eat() const { std::cout << name_ << " eats\n"; }
        protected:
            std::string name_;                 // visible to derived classes, not to outsiders
        };

        class Dog : public Animal {
        public:
            Dog(std::string name, std::string breed)
                : Animal(std::move(name)), breed_(std::move(breed)) { std::cout << "Dog()\n"; }   // base first
            ~Dog() { std::cout << "~Dog()\n"; }
            void bark() const { std::cout << name_ << " the " << breed_ << " barks\n"; }
        private:
            std::string breed_;
        };

        int main() {
            Dog d("Rex", "beagle");
            d.eat();          // inherited
            d.bark();         // added
        }
    ''', out='''
        Animal()
        Dog()
        Rex eats
        Rex the beagle barks
        ~Dog()
        ~Animal()
    ''')
    yield note("Construction goes **base → members → derived body**; destruction runs in exactly the reverse order.", "Order")
    yield section("Inheritance access", "lock-access")
    yield table(
        ["Base member is…", "`public` inheritance", "`protected` inheritance", "`private` inheritance"],
        ["`public`", "public", "protected", "private"],
        ["`protected`", "protected", "protected", "private"],
        ["`private`", "inaccessible", "inaccessible", "inaccessible"],
    )
    yield ul(
        "`public` inheritance = *is-a* (a `Dog` can be used wherever an `Animal&` is expected). 99% of the time this is what you want.",
        "`private` inheritance = *implemented-in-terms-of* — usually better expressed with composition (a member).",
        "`class D : B` defaults to **private** inheritance; `struct D : B` to public.",
    )
    yield section("Hiding, `using` and calling the base version", "eye-off")
    yield snippet("cpp", r'''
        #include <iostream>

        struct Base {
            void greet() const { std::cout << "Base::greet\n"; }
            void greet(int n) const { std::cout << "Base::greet(" << n << ")\n"; }
        };

        struct Derived : Base {
            using Base::greet;                 // without this, greet(int) would be hidden
            void greet() const {
                std::cout << "Derived::greet, then ";
                Base::greet();                 // call the base version explicitly
            }
        };

        struct WithCtors : Base {
            using Base::Base;                  // inherit constructors (C++11)
        };

        int main() {
            Derived d;
            d.greet();
            d.greet(3);
        }
    ''', out='''
        Derived::greet, then Base::greet
        Base::greet(3)
    ''')
    yield warn("Declaring a function in the derived class with the same *name* hides **all** base overloads of that name, whatever their parameters. Bring them back with `using Base::name;`.")
    yield section("Composition vs inheritance", "puzzle")
    yield dodont("Use inheritance for genuine is-a relationships with polymorphic behaviour; prefer **composition** (has-a) for reuse: a `Car` *has an* `Engine`.", "Inheriting just to reuse code (`class Stack : public std::vector<int>`) — it exposes every base operation and couples you to its implementation.")
    yield qa("What is not inherited from a base class?",
             "Constructors (unless brought in with `using Base::Base;`), the destructor, copy/move assignment operators (the derived class gets its own implicitly-declared ones), and friendships. Private members *are* inherited — they're part of the object — but not accessible.")


@topic(G, "virtual-functions", "Virtual Functions & vtables", "arrows-shuffle")
def _():
    yield lead("A `virtual` function is dispatched on the object's *dynamic* type at run time — the mechanism behind runtime polymorphism.")
    yield section("Static vs dynamic binding", "switch-horizontal")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <vector>

        struct Shape {
            virtual double area() const { return 0; }
            std::string kind() const { return "shape"; }        // non-virtual
            virtual ~Shape() = default;                         // virtual destructor!
        };
        struct Rect : Shape {
            double w, h;
            Rect(double a, double b) : w(a), h(b) {}
            double area() const override { return w * h; }     // `override`: compiler checks it overrides
            std::string kind() const { return "rect"; }         // hides, doesn't override
        };
        struct Circle : Shape {
            double r;
            explicit Circle(double x) : r(x) {}
            double area() const override { return 3.14 * r * r; }
        };

        int main() {
            std::vector<std::unique_ptr<Shape>> shapes;
            shapes.push_back(std::make_unique<Rect>(2, 3));
            shapes.push_back(std::make_unique<Circle>(1));
            for (const auto& s : shapes) std::cout << s->kind() << ' ' << s->area() << '\n';

            Rect r(1, 1);
            Shape& ref = r;
            std::cout << ref.area() << ' ' << ref.kind() << ' ' << r.kind() << '\n';
        }
    ''', out='''
        shape 6
        shape 3.14
        1 shape rect
    ''')
    yield table(
        ["Call through…", "Non-virtual function", "Virtual function"],
        ["Object `r.f()`", "Static type", "Static type (= dynamic)"],
        ["Pointer/reference to base `p->f()`", "**Static** type (`Shape::f`)", "**Dynamic** type (`Rect::f`)"],
    )
    yield section("How it works: vptr & vtable", "table")
    yield steps(
        ("vtable per class", "Each class with virtual functions gets one static table of function pointers, one slot per virtual function."),
        ("vptr per object", "Every object carries a hidden pointer (usually the first 8 bytes) to its class's vtable. Constructors set it."),
        ("Call", "`p->area()` compiles to: load `p->vptr`, load slot *k*, call it — one or two extra memory loads."),
    )
    yield snippet("cpp", r'''
        #include <iostream>
        struct Plain   { int x; void f() {} };
        struct Virtual { int x; virtual void f() {} virtual ~Virtual() = default; };
        int main() {
            std::cout << sizeof(Plain) << ' ' << sizeof(Virtual) << '\n';   // 4 vs 16: vptr (8) + int + padding
        }
    ''', out="4 16")
    yield section("`override` and `final`", "check")
    yield snippet("cpp", r'''
        struct Base {
            virtual void save(int version) const {}
            virtual ~Base() = default;
        };
        struct Derived : Base {
            void save(long version) const override {}   // error: doesn't override (parameter type differs)
        };
        int main() {}
    ''', fails=True)
    yield snippet("cpp", r'''
        #include <iostream>
        struct Base { virtual void run() const { std::cout << "base\n"; } virtual ~Base() = default; };
        struct Leaf final : Base {                       // no class may derive from Leaf
            void run() const override { std::cout << "leaf\n"; }
        };
        struct Mid : Base { void run() const final { std::cout << "mid\n"; } };   // run can't be overridden further
        int main() {
            const Base& b = Leaf{};
            b.run();
            Mid{}.run();
        }
    ''', out='''
        leaf
        mid
    ''')
    yield section("Virtual destructors", "trash")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Base {
            virtual void speak() const {}
            ~Base() { std::cout << "~Base\n"; }                        // NOT virtual
        };
        struct Derived : Base {
            int* data = new int[100];
            ~Derived() { delete[] data; std::cout << "~Derived\n"; }
        };
        int main() {
            Base* p = new Derived;
            delete p;          // undefined behaviour: only ~Base would run → ~Derived skipped, leak
        }
    ''', fails=True, caption="C++ — missing virtual destructor")
    yield output('''
        error: delete called on non-final 'Base' that has virtual functions but non-virtual destructor [-Werror,-Wdelete-non-abstract-non-virtual-dtor]
    ''', caption="Compiler error (-Wall)")
    yield warn("If a class has any virtual function (or is meant to be deleted through a base pointer), give it a `virtual` destructor. Otherwise `delete basePtr;` skips the derived destructor.")
    yield section("Object slicing", "slice")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Animal { virtual const char* sound() const { return "..."; } virtual ~Animal() = default; };
        struct Cat : Animal { const char* sound() const override { return "meow"; } };
        void byValue(Animal a)            { std::cout << a.sound() << '\n'; }   // copies only the Animal part
        void byRef(const Animal& a)       { std::cout << a.sound() << '\n'; }
        int main() {
            Cat c;
            byValue(c);
            byRef(c);
        }
    ''', out='''
        ...
        meow
    ''')
    yield warn("Passing or storing a derived object *by value* as its base type **slices** off the derived part — virtual calls then use the base version. Pass polymorphic objects by reference or (smart) pointer; store them as `std::vector<std::unique_ptr<Base>>`.")
    yield section("Calling virtuals in constructors", "alert-triangle")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Base {
            Base() { hello(); }                          // dispatches to Base::hello, not Derived's!
            virtual void hello() const { std::cout << "Base::hello\n"; }
            virtual ~Base() = default;
        };
        struct Derived : Base { void hello() const override { std::cout << "Derived::hello\n"; } };
        int main() { Derived d; d.hello(); }
    ''', out='''
        Base::hello
        Derived::hello
    ''')
    yield qa("How are virtual functions implemented?",
             "Typically with a per-class *vtable* (array of function pointers) and a hidden *vptr* in each object pointing to its class's table. A virtual call loads the vptr, indexes the table and calls indirectly. Cost: one pointer per object, an indirect call that can't normally be inlined.")
    yield qa("Why is calling a virtual function from a constructor dangerous?",
             "While the base constructor runs, the derived part doesn't exist yet and the vptr points to the base vtable, so the call goes to the base version (or is undefined for a pure virtual). The same applies in destructors.")


@topic(G, "abstract-classes", "Abstract Classes & Interfaces", "template")
def _():
    yield lead("A *pure virtual* function (`= 0`) has no implementation in the base class. A class with at least one is **abstract**: it can't be instantiated, only derived from — that's how C++ spells “interface”.")
    yield section("Interface + implementations", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <string>
        #include <vector>

        class Notifier {                                   // interface: only pure virtuals
        public:
            virtual ~Notifier() = default;
            virtual void send(const std::string& msg) = 0;
            virtual std::string channel() const = 0;
        };

        class EmailNotifier : public Notifier {
        public:
            void send(const std::string& msg) override { std::cout << "email: " << msg << '\n'; }
            std::string channel() const override { return "email"; }
        };

        class SmsNotifier : public Notifier {
        public:
            void send(const std::string& msg) override { std::cout << "sms: " << msg.substr(0, 10) << '\n'; }
            std::string channel() const override { return "sms"; }
        };

        void alertAll(const std::vector<std::unique_ptr<Notifier>>& targets, const std::string& msg) {
            for (const auto& t : targets) t->send(msg);   // depends only on the interface
        }

        int main() {
            std::vector<std::unique_ptr<Notifier>> targets;
            targets.push_back(std::make_unique<EmailNotifier>());
            targets.push_back(std::make_unique<SmsNotifier>());
            alertAll(targets, "Server CPU at 97%");
            // Notifier n;   // error: abstract class
        }
    ''', out='''
        email: Server CPU at 97%
        sms: Server CPU
    ''')
    yield snippet("cpp", r'''
        struct Shape { virtual double area() const = 0; virtual ~Shape() = default; };
        struct Square : Shape { double s = 1; };      // forgot to override area → still abstract
        int main() {
            Square sq;                                // error: variable type 'Square' is an abstract class
        }
    ''', fails=True)
    yield section("Template method pattern", "list-check")
    yield snippet("cpp", r'''
        #include <iostream>

        class Report {
        public:
            void generate() const {              // fixed algorithm (non-virtual)…
                std::cout << "== " << title() << " ==\n";
                body();
                std::cout << "-- end --\n";
            }
            virtual ~Report() = default;
        private:
            virtual const char* title() const = 0;    // …customisation points (private virtual is fine)
            virtual void body() const = 0;
        };

        class SalesReport : public Report {
            const char* title() const override { return "Sales"; }
            void body() const override { std::cout << "total: 42\n"; }
        };

        int main() { SalesReport{}.generate(); }
    ''', out='''
        == Sales ==
        total: 42
        -- end --
    ''')
    yield section("Pure virtual with a body", "info-circle")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Base {
            virtual ~Base() = 0;                         // pure virtual destructor: makes Base abstract…
            virtual void log() const = 0;
        };
        Base::~Base() { std::cout << "~Base\n"; }       // …but it MUST still have a body
        void Base::log() const { std::cout << "default logging\n"; }   // optional default implementation

        struct Impl : Base { void log() const override { Base::log(); } };
        int main() { Impl i; i.log(); }
    ''', out='''
        default logging
        ~Base
    ''')
    yield table(
        ["", "Abstract class", "Interface (C++ convention)"],
        ["Pure virtual functions", "At least one", "All (plus virtual dtor)"],
        ["Data members", "Allowed", "None"],
        ["Implemented functions", "Allowed", "None"],
        ["Multiple inheritance", "Possible but careful", "Safe and common"],
    )
    yield qa("Can an abstract class have a constructor?",
             "Yes. You can't create a standalone object of it, but its constructor runs as part of constructing every derived object — useful to initialise the base's data members. It's often made `protected`.")
    yield qa("Abstract class vs interface in C++?",
             "C++ has no `interface` keyword. An “interface” is just an abstract class with only pure virtual functions, a virtual destructor and no data. An abstract class may additionally carry state and shared implementation.")


@topic(G, "multiple-inheritance", "Multiple & Virtual Inheritance", "git-merge")
def _():
    yield lead("A class can inherit from several bases. That's safe for interfaces, but when two bases share a common ancestor you get the **diamond problem** — solved by `virtual` inheritance.")
    yield section("Multiple inheritance", "git-merge")
    yield snippet("cpp", r'''
        #include <iostream>

        struct Printable { virtual void print() const = 0; virtual ~Printable() = default; };
        struct Serializable { virtual std::string serialize() const = 0; virtual ~Serializable() = default; };

        struct Point : Printable, Serializable {         // implements two interfaces
            int x = 1, y = 2;
            void print() const override { std::cout << "Point(" << x << ", " << y << ")\n"; }
            std::string serialize() const override { return std::to_string(x) + "," + std::to_string(y); }
        };

        int main() {
            Point p;
            const Printable& pr = p;
            const Serializable& se = p;
            pr.print();
            std::cout << se.serialize() << '\n';
        }
    ''', out='''
        Point(1, 2)
        1,2
    ''')
    yield section("The diamond problem", "diamond")
    yield flow("`Device`", "`Scanner` / `Printer`", "`Copier`")
    yield snippet("cpp", r'''
        #include <iostream>

        struct Device { int id = 0; };
        struct Scanner : Device {};
        struct Printer : Device {};
        struct Copier : Scanner, Printer {};      // contains TWO Device sub-objects

        int main() {
            Copier c;
            c.Scanner::id = 1;                     // must disambiguate
            c.Printer::id = 2;
            std::cout << c.Scanner::id << ' ' << c.Printer::id << ' ' << sizeof(Copier) / sizeof(int) << '\n';
            // c.id = 5;                           // error: ambiguous
        }
    ''', out="1 2 2")
    yield section("Virtual inheritance", "share")
    yield snippet("cpp", r'''
        #include <iostream>

        struct Device {
            int id;
            explicit Device(int i) : id(i) { std::cout << "Device(" << i << ")\n"; }
        };
        struct Scanner : virtual Device { Scanner() : Device(1) {} };   // shared base
        struct Printer : virtual Device { Printer() : Device(2) {} };
        struct Copier : Scanner, Printer {
            Copier() : Device(3) {}               // the MOST-DERIVED class initialises the virtual base
        };

        int main() {
            Copier c;
            std::cout << c.id << '\n';            // one Device, no ambiguity
        }
    ''', out='''
        Device(3)
        3
    ''')
    yield ul(
        "With `virtual` inheritance there is exactly **one** shared base sub-object.",
        "The most-derived class constructs the virtual base; the intermediate classes' initialisers for it are ignored.",
        "Cost: an extra indirection (virtual base offset) to reach the shared base, and more complex object layout.",
    )
    yield section("Name clashes between bases", "arrows-cross")
    yield snippet("cpp", r'''
        #include <iostream>
        struct Camera { void start() const { std::cout << "camera on\n"; } };
        struct Phone  { void start() const { std::cout << "phone on\n"; } };
        struct SmartPhone : Camera, Phone {
            void start() const { Phone::start(); Camera::start(); }   // resolve explicitly
        };
        int main() { SmartPhone{}.start(); }
    ''', out='''
        phone on
        camera on
    ''')
    yield dodont("Use multiple inheritance of *interfaces* (pure abstract bases) freely.", "Deep hierarchies with multiple *stateful* bases — prefer composition.")
    yield qa("What is the diamond problem and how does C++ solve it?",
             "When `D` inherits from `B` and `C`, which both inherit from `A`, `D` contains two copies of `A`, so `A`'s members are ambiguous and the state is duplicated. Declaring `B : virtual A` and `C : virtual A` makes them share one `A` sub-object, which the most-derived class (`D`) constructs.")


@topic(G, "casts-rtti", "Casts & RTTI", "arrows-exchange")
def _():
    yield lead("C++ replaces the all-powerful C cast with four named casts, each saying *what* you're doing. `dynamic_cast` and `typeid` use Run-Time Type Information.")
    yield section("The four casts", "list")
    yield table(
        ["Cast", "Checked", "Use"],
        ["`static_cast<T>`", "Compile time", "Numeric conversions, `void*` → `T*`, up-casts, down-casts you *know* are valid, enum ↔ int"],
        ["`dynamic_cast<T>`", "**Run time**", "Safe down-cast/cross-cast in a polymorphic hierarchy; `nullptr` (pointers) or `std::bad_cast` (references) on failure"],
        ["`const_cast<T>`", "Compile time", "Remove/add `const` — e.g. calling a legacy API that forgot `const`. Modifying a truly const object is UB"],
        ["`reinterpret_cast<T>`", "None", "Reinterpret bits: pointer ↔ integer, unrelated pointer types. Platform-specific"],
    )
    yield section("`static_cast`", "arrows-exchange")
    yield snippet("cpp", r'''
        #include <iostream>
        enum class Level { Low = 1, High = 3 };
        int main() {
            double avg = static_cast<double>(7) / 2;
            int lvl = static_cast<int>(Level::High);
            char c = static_cast<char>(65);
            void* vp = &lvl;
            int* ip = static_cast<int*>(vp);
            std::cout << avg << ' ' << lvl << ' ' << c << ' ' << *ip << '\n';
        }
    ''', out="3.5 3 A 3")
    yield section("`dynamic_cast`", "shield-check")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <memory>
        #include <typeinfo>
        #include <vector>

        struct Animal { virtual ~Animal() = default; };     // must be polymorphic
        struct Dog : Animal { void fetch() const { std::cout << "fetching\n"; } };
        struct Cat : Animal {};

        int main() {
            std::vector<std::unique_ptr<Animal>> zoo;
            zoo.push_back(std::make_unique<Dog>());
            zoo.push_back(std::make_unique<Cat>());
            for (const auto& a : zoo) {
                if (auto* d = dynamic_cast<Dog*>(a.get())) d->fetch();     // nullptr if not a Dog
                else std::cout << "not a dog\n";
            }
            Cat cat;
            Animal& ref = cat;
            try {
                Dog& d = dynamic_cast<Dog&>(ref);                         // reference form throws
                d.fetch();
            } catch (const std::bad_cast&) {
                std::cout << "bad_cast\n";
            }
        }
    ''', out='''
        fetching
        not a dog
        bad_cast
    ''')
    yield note("Needing lots of `dynamic_cast` is a design smell — usually a virtual function should do the type-specific work. It also costs a run-time walk of the type hierarchy.")
    yield section("`typeid`", "id")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <typeinfo>
        struct Base { virtual ~Base() = default; };
        struct Derived : Base {};
        struct NonPoly {};
        struct NonPolyDerived : NonPoly {};
        int main() {
            Derived d;
            Base& b = d;
            NonPolyDerived npd;
            NonPoly& np = npd;
            std::cout << (typeid(b) == typeid(Derived)) << ' ' << (typeid(np) == typeid(NonPolyDerived)) << '\n';
            std::cout << typeid(int).name() << ' ' << typeid(double).name() << '\n';   // implementation-defined names
        }
    ''', out='''
        1 0
        i d
    ''')
    yield section("`const_cast` & `reinterpret_cast`", "alert-triangle")
    yield snippet("cpp", r'''
        #include <cstdint>
        #include <cstring>
        #include <iostream>

        void legacyPrint(char* s) { std::cout << s << '\n'; }   // doesn't modify, but isn't const-correct

        int main() {
            const char* msg = "hello";
            legacyPrint(const_cast<char*>(msg));                 // OK only because legacyPrint doesn't write

            int value = 0x01020304;
            auto addr = reinterpret_cast<std::uintptr_t>(&value);   // pointer → integer
            std::cout << (addr % alignof(int)) << '\n';

            float f = 1.0f;
            std::uint32_t bits;
            std::memcpy(&bits, &f, sizeof bits);                 // the safe way to inspect bits (or std::bit_cast)
            std::cout << std::hex << bits << '\n';
        }
    ''', out='''
        hello
        0
        3f800000
    ''')
    yield warn("`*reinterpret_cast<std::uint32_t*>(&f)` violates *strict aliasing* (undefined behaviour). Use `std::memcpy` or C++20 `std::bit_cast<std::uint32_t>(f)` to reinterpret an object's bytes.")
    yield qa("Why avoid C-style casts in C++?",
             "`(T)x` silently tries `const_cast`, `static_cast` and `reinterpret_cast` combinations until one compiles, so it can cast away `const` or reinterpret pointers by accident. Named casts state intent, are restricted to what they say, and are easy to grep for.")
    yield qa("static_cast vs dynamic_cast for down-casting?",
             "`static_cast<Derived*>(basePtr)` trusts you: no run-time check, UB if the object isn't really a `Derived`. `dynamic_cast` checks the actual type using RTTI and returns `nullptr` (or throws for references) when it's wrong — safer but slower, and it only works on polymorphic types.")
