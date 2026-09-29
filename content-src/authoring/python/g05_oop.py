from kit import *

G = "Object-Oriented Python"


@topic(G, "classes", "Classes & Objects", "box")
def _():
    yield lead("A class bundles data (attributes) and behaviour (methods). In Python everything — even functions and classes themselves — is an object.")
    yield section("Anatomy of a class", "code")
    yield code('''
        class Account:
            bank = "LVN Bank"                   # class attribute: shared by all instances

            def __init__(self, owner, balance=0):
                self.owner = owner              # instance attributes: one per object
                self.balance = balance

            def deposit(self, amount):
                if amount <= 0:
                    raise ValueError("amount must be positive")
                self.balance += amount
                return self.balance

        a = Account("Asha")
        b = Account("Ravi", 100)
        a.deposit(50)
        print(a.balance, b.balance, a.bank)     # 50 100 LVN Bank
    ''')
    yield cards(
        ("`__init__`", "The *initializer*: runs after the object is created (`__new__` creates it) to set up its state.", "player-play"),
        ("`self`", "The instance the method was called on. `a.deposit(50)` is really `Account.deposit(a, 50)`.", "user"),
        ("Class attribute", "Defined in the class body, shared by every instance. Great for constants and counters.", "users"),
        ("Instance attribute", "Set on `self`, stored in the object's own `__dict__`.", "user-circle"),
    )
    yield warn("A mutable **class** attribute (e.g. `items = []` in the class body) is shared by all instances. Create per-object lists in `__init__`.")
    yield section("Three kinds of methods", "category")
    yield code('''
        class Temperature:
            def __init__(self, celsius):
                self.celsius = celsius

            def to_f(self):                      # instance method: gets self
                return self.celsius * 9 / 5 + 32

            @classmethod
            def from_f(cls, f):                  # class method: gets the class → alternative constructors
                return cls((f - 32) * 5 / 9)

            @staticmethod
            def is_freezing(c):                  # static method: a plain function in the class namespace
                return c <= 0

        t = Temperature.from_f(212)
        print(t.celsius, t.to_f(), Temperature.is_freezing(-3))   # 100.0 212.0 True
    ''')
    yield section("Properties: attributes with logic", "shield-check")
    yield code('''
        class Circle:
            def __init__(self, radius):
                self.radius = radius             # goes through the setter below

            @property
            def radius(self):
                return self._radius

            @radius.setter
            def radius(self, value):
                if value < 0:
                    raise ValueError("radius must be >= 0")
                self._radius = value

            @property
            def area(self):                      # computed, read-only
                return round(3.14159 * self._radius ** 2, 2)

        c = Circle(2)
        print(c.area)                            # 12.57
        try:
            c.radius = -1
        except ValueError as e:
            print(e)                             # radius must be >= 0
    ''')
    yield section("Encapsulation by convention", "lock")
    yield table(
        ["Name", "Meaning"],
        ["`name`", "Public API"],
        ["`_name`", "Internal — “please don't touch” (not enforced)"],
        ["`__name`", "Name-mangled to `_ClassName__name` to avoid clashes in subclasses"],
        ["`__name__`", "Special (dunder) names reserved for Python"],
    )
    yield note("Python has no `private` keyword. The culture is “we're all consenting adults”: mark internals with `_` and use properties when you need validation.")


@topic(G, "inheritance", "Inheritance, MRO & super()", "hierarchy")
def _():
    yield lead("A subclass reuses and specialises its parent. Python supports multiple inheritance and resolves methods with a predictable order — the MRO.")
    yield section("Inheritance & overriding", "hierarchy-2")
    yield code('''
        class Animal:
            def __init__(self, name):
                self.name = name
            def speak(self):
                return "..."
            def describe(self):
                return f"{self.name} says {self.speak()}"

        class Dog(Animal):
            def __init__(self, name, breed):
                super().__init__(name)           # let the parent set up its part
                self.breed = breed
            def speak(self):                     # override
                return "Woof"

        d = Dog("Rex", "lab")
        print(d.describe())                              # Rex says Woof
        print(isinstance(d, Animal), issubclass(Dog, Animal))   # True True
    ''')
    yield note("`describe` lives in `Animal` but calls `self.speak()` — Python looks it up on the actual object, so the `Dog` version runs. That's polymorphism.")
    yield section("Multiple inheritance & the MRO", "git-merge")
    yield define("MRO (Method Resolution Order)", "the order in which classes are searched for an attribute, computed with *C3 linearization*. See it with `Class.__mro__` or `Class.mro()`.")
    yield code('''
        class A:
            def hello(self): return "A"
        class B(A):
            def hello(self): return "B→" + super().hello()
        class C(A):
            def hello(self): return "C→" + super().hello()
        class D(B, C):
            def hello(self): return "D→" + super().hello()

        print(D().hello())                          # D→B→C→A
        print([k.__name__ for k in D.__mro__])      # ['D', 'B', 'C', 'A', 'object']
    ''')
    yield warn("`super()` means “the **next class in the MRO**”, not “my parent”. In `D(B, C)`, `B`'s `super()` goes to `C`, not `A` — that's what makes cooperative multiple inheritance work.")
    yield section("Abstract base classes", "template")
    yield code('''
        from abc import ABC, abstractmethod

        class Shape(ABC):
            @abstractmethod
            def area(self) -> float: ...

        class Square(Shape):
            def __init__(self, side):
                self.side = side
            def area(self):
                return self.side ** 2

        print(Square(3).area())          # 9
        try:
            Shape()
        except TypeError:
            print("can't instantiate")   # can't instantiate
    ''')
    yield section("Duck typing & composition", "puzzle")
    yield cards(
        ("Duck typing", "“If it walks like a duck…” — code relies on *what an object can do* (has `read()`, is iterable) rather than its class.", "feather"),
        ("Composition over inheritance", "Hold other objects as attributes (`self.engine = Engine()`) instead of building deep class trees.", "components"),
        ("Mixins", "Small classes adding one capability (e.g. `JsonMixin.to_json`) combined through multiple inheritance.", "blend-mode"),
        ("Protocols", "`typing.Protocol` describes the methods a type needs — static duck typing for type checkers.", "file-certificate"),
    )


@topic(G, "dunder-methods", "Magic (Dunder) Methods", "wand")
def _():
    yield lead("Double-underscore methods let your objects plug into Python's syntax: printing, `==`, `len()`, `[]`, `for`, `+`, `with` and more.")
    yield section("Representation", "eye")
    yield code('''
        class Money:
            def __init__(self, amount, cur="INR"):
                self.amount, self.cur = amount, cur
            def __repr__(self):                  # unambiguous, for developers
                return f"Money({self.amount!r}, {self.cur!r})"
            def __str__(self):                   # readable, for users
                return f"{self.amount:.2f} {self.cur}"

        m = Money(250)
        print(repr(m))        # Money(250, 'INR')
        print(m)              # 250.00 INR
        print([m])            # [Money(250, 'INR')]
    ''')
    yield note("Containers show their items with `repr()`. Always define `__repr__`; add `__str__` when a friendlier form helps.")
    yield section("Equality, hashing & ordering", "equal")
    yield code('''
        from functools import total_ordering

        @total_ordering
        class Version:
            def __init__(self, major, minor):
                self.key = (major, minor)
            def __eq__(self, other):
                return isinstance(other, Version) and self.key == other.key
            def __hash__(self):                   # equal objects must hash equally
                return hash(self.key)
            def __lt__(self, other):
                return self.key < other.key

        v1, v2 = Version(1, 2), Version(1, 10)
        print(v1 < v2, v1 >= v2, v1 == Version(1, 2))   # True False True
        print(len({v1, Version(1, 2)}))                  # 1
    ''')
    yield warn("Defining `__eq__` without `__hash__` makes instances **unhashable** (Python sets `__hash__ = None`). If objects can change, don't make them hashable.")
    yield section("Container & iteration protocols", "list")
    yield code('''
        class Playlist:
            def __init__(self, *songs):
                self._songs = list(songs)
            def __len__(self):
                return len(self._songs)
            def __getitem__(self, i):             # enables p[i], slicing and iteration
                return self._songs[i]
            def __contains__(self, song):
                return song in self._songs

        p = Playlist("a", "b", "c")
        print(len(p), p[0], p[-1], "b" in p)      # 3 a c True
        print(list(p), p[1:])                     # ['a', 'b', 'c'] ['b', 'c']
    ''')
    yield section("Operators & callables", "math")
    yield code('''
        class Vec:
            def __init__(self, x, y):
                self.x, self.y = x, y
            def __add__(self, o):
                return Vec(self.x + o.x, self.y + o.y)
            def __mul__(self, k):
                return Vec(self.x * k, self.y * k)
            def __abs__(self):
                return (self.x ** 2 + self.y ** 2) ** 0.5
            def __repr__(self):
                return f"Vec({self.x}, {self.y})"

        class Adder:
            def __init__(self, n):
                self.n = n
            def __call__(self, x):                # instances become callable
                return x + self.n

        print(Vec(1, 2) + Vec(3, 4), Vec(3, 4) * 2, abs(Vec(3, 4)))   # Vec(4, 6) Vec(6, 8) 5.0
        print(Adder(10)(5))                                            # 15
    ''')
    yield table(
        ["Syntax", "Calls"],
        ["`str(x)`, `repr(x)`", "`__str__`, `__repr__`"],
        ["`x == y`, `x < y`", "`__eq__`, `__lt__` (+ `__le__`, `__gt__`, `__ge__`)"],
        ["`len(x)`, `x[i]`, `v in x`", "`__len__`, `__getitem__`, `__contains__`"],
        ["`for v in x`", "`__iter__` (then `__next__` on the iterator)"],
        ["`x + y`, `x * y`", "`__add__`, `__mul__` (`__radd__` for `y + x`)"],
        ["`x()`", "`__call__`"],
        ["`with x:`", "`__enter__`, `__exit__`"],
        ["`bool(x)`", "`__bool__`, falling back to `__len__`"],
    )


@topic(G, "properties-descriptors", "Properties & Descriptors", "shield-check")
def _():
    yield lead("`@property` turns method calls into plain attribute access. Underneath it sits the *descriptor protocol* — the same mechanism that powers methods, `classmethod`, `staticmethod`, `__slots__` and `cached_property`.")
    yield section("property recap: getter, setter, deleter", "shield-check")
    yield p("Start with plain public attributes. When you later need validation or a computed value, swap in a `property` — callers keep writing `obj.attr` and nothing breaks. That is why Python code has no `getX()`/`setX()` boilerplate.")
    yield code('''
        class Temperature:
            def __init__(self, celsius):
                self.celsius = celsius            # goes through the setter → validated from the start

            @property
            def celsius(self):                    # getter
                return self._celsius

            @celsius.setter
            def celsius(self, value):             # setter: validation lives here
                if value < -273.15:
                    raise ValueError("below absolute zero")
                self._celsius = value

            @celsius.deleter
            def celsius(self):                    # deleter: runs on `del t.celsius`
                del self._celsius

            @property
            def fahrenheit(self):                 # computed and read-only (no setter)
                return self._celsius * 9 / 5 + 32

        t = Temperature(100)
        print(t.celsius, t.fahrenheit)            # 100 212.0
        t.celsius = 0
        print(t.fahrenheit)                       # 32.0
        try:
            t.fahrenheit = 50
        except AttributeError as e:
            print(type(e).__name__)               # AttributeError
        del t.celsius
        print(hasattr(t, "_celsius"))             # False
    ''')
    yield table(
        ["Pattern", "How"],
        ["Read-only attribute", "`@property` with no setter — assignment raises `AttributeError`"],
        ["Validated attribute", "Setter checks the value, stores it in `self._name`"],
        ["Computed attribute", "Getter derives it from other fields — never goes stale"],
        ["Lazy + cached", "`@functools.cached_property` — computed once, then stored"],
    )
    yield warn("Inside the getter, return `self._celsius`, not `self.celsius` — the latter calls the getter again and recurses until `RecursionError`.")
    yield section("How `obj.attr` is looked up", "search")
    yield define("Descriptor", "any object whose class defines `__get__`, `__set__` or `__delete__`, stored as a **class** attribute. Accessing it through an instance calls those methods instead of returning the object itself.")
    yield table(
        ["Kind", "Defines", "Priority vs the instance `__dict__`", "Examples"],
        ["**Data** descriptor", "`__get__` + `__set__` (or `__delete__`)", "Wins over `obj.__dict__`", "`property`, `__slots__` members"],
        ["**Non-data** descriptor", "only `__get__`", "Loses to `obj.__dict__`", "functions (methods), `classmethod`, `staticmethod`, `cached_property`"],
    )
    yield steps(
        ("Data descriptor on the class?", "Search `type(obj).__mro__`. If the attribute found there is a data descriptor, call its `__get__` and stop."),
        ("Instance dictionary", "Otherwise, if the name is in `obj.__dict__`, return that value."),
        ("Non-data descriptor or class attribute", "Otherwise use what was found on the class: call `__get__` if it has one, else return it as is."),
        ("`__getattr__` fallback", "Still nothing? Call `__getattr__(name)` if the class defines it, else raise `AttributeError`."),
    )
    yield code('''
        class Demo:
            @property
            def p(self):
                return "property"
            def m(self):
                return "method"

        d = Demo()
        d.__dict__["p"] = "instance value"       # sneak values straight into the instance dict
        d.__dict__["m"] = lambda: "instance value"
        print(d.p)       # property        ← data descriptor beats the instance dict
        print(d.m())     # instance value  ← the instance dict beats a non-data descriptor
    ''')
    yield note("All of this is implemented in `object.__getattribute__`, which runs for **every** attribute access.")
    yield section("Writing a reusable descriptor", "code")
    yield p("A property is tied to one attribute of one class. When many attributes need the same rule, write the rule once as a descriptor class and reuse it.")
    yield code('''
        class Positive:
            """A validated numeric field, reusable across classes."""
            def __set_name__(self, owner, name):      # called when the owning class is created
                self.name = name
                self.private = "_" + name

            def __get__(self, obj, objtype=None):
                if obj is None:                        # accessed on the class, not an instance
                    return self
                return getattr(obj, self.private)

            def __set__(self, obj, value):
                if not isinstance(value, (int, float)) or value <= 0:
                    raise ValueError(f"{self.name} must be a positive number, got {value!r}")
                setattr(obj, self.private, value)

        class Product:
            price = Positive()
            qty = Positive()

            def __init__(self, name, price, qty):
                self.name, self.price, self.qty = name, price, qty

        p = Product("pen", 20, 3)
        print(p.price * p.qty)            # 60
        try:
            p.qty = -1
        except ValueError as e:
            print(e)                      # qty must be a positive number, got -1
        print(Product.price.name)         # price
        print(sorted(vars(p)))            # ['_price', '_qty', 'name']
    ''')
    yield cards(
        ("`__set_name__(owner, name)`", "Tells the descriptor which attribute name it was assigned to (3.6+) — no need to repeat the name.", "tag"),
        ("`__get__(obj, objtype)`", "`obj` is the instance, or `None` when accessed on the class — return `self` then.", "download"),
        ("`__set__(obj, value)`", "Having it makes this a *data* descriptor, so it always intercepts assignment.", "upload"),
        ("Where to store the value", "On the instance (`obj._name`) — storing on the descriptor would share one value across all instances.", "database"),
    )
    yield section("Methods are descriptors too", "function")
    yield p("A function in a class body is a non-data descriptor. `obj.method` calls `function.__get__(obj, type(obj))`, which returns a **bound method** with `obj` pre-filled as `self`.")
    yield code('''
        class Greeter:
            def hello(self, name):
                return f"hi {name}"

        g = Greeter()
        f = Greeter.__dict__["hello"]           # the plain function stored in the class
        bound = f.__get__(g, Greeter)           # exactly what `g.hello` does
        print(bound("asha"))                    # hi asha
        print(bound.__self__ is g)              # True
        print(type(g.hello).__name__, type(Greeter.hello).__name__)   # method function
        print(hasattr(property, "__set__"), hasattr(f, "__set__"))    # True False
    ''')
    yield table(
        ["Built-in", "Descriptor kind", "`__get__` returns"],
        ["function", "non-data", "a bound method (instance) or the function (class)"],
        ["`classmethod`", "non-data", "a method bound to the **class**"],
        ["`staticmethod`", "non-data", "the underlying function, unbound"],
        ["`property`", "data", "the getter's result"],
        ["`__slots__` entry", "data (`member_descriptor`)", "the value in the object's fixed slot"],
    )
    yield section("`__getattr__`, `__getattribute__` & `__setattr__`", "adjustments")
    yield code('''
        class Config:
            def __init__(self, **values):
                object.__setattr__(self, "_values", values)   # bypass our own __setattr__

            def __getattr__(self, name):          # only called when normal lookup FAILS
                try:
                    return self._values[name]
                except KeyError:
                    raise AttributeError(name) from None

            def __setattr__(self, name, value):   # called for EVERY assignment
                raise AttributeError(f"Config is read-only ({name})")

        c = Config(debug=True, level=3)
        print(c.debug, c.level)                   # True 3
        print(getattr(c, "missing", "n/a"))       # n/a
        try:
            c.level = 5
        except AttributeError as e:
            print(e)                              # Config is read-only (level)
    ''')
    yield table(
        ["Hook", "Runs", "Typical use"],
        ["`__getattr__`", "Only when the attribute is **not found** normally", "Proxies, dynamic attributes, lazy loading"],
        ["`__getattribute__`", "On **every** attribute read", "Rarely — access logging, very special proxies"],
        ["`__setattr__` / `__delattr__`", "On every assignment / deletion", "Immutability, change tracking"],
    )
    yield warn("Inside `__getattribute__` or `__setattr__`, never use `self.x` for your own storage — it re-enters the hook and recurses. Call `object.__getattribute__(self, name)` / `super().__setattr__(name, value)`.")
    yield section("cached_property", "database")
    yield code('''
        from functools import cached_property

        class Report:
            def __init__(self, rows):
                self.rows = rows
                self.calls = 0

            @cached_property
            def total(self):                 # expensive work, done once per instance
                self.calls += 1
                return sum(self.rows)

        r = Report([1, 2, 3])
        print(r.total, r.total, r.calls)     # 6 6 1
        print("total" in r.__dict__)         # True  ← the result now lives in the instance dict
        del r.total                          # invalidate the cache
        print(r.total, r.calls)              # 6 2
    ''')
    yield note("`cached_property` is a *non-data* descriptor: after the first call the value sits in `obj.__dict__` and shadows it, so later reads cost nothing. It needs a per-instance `__dict__`, so it doesn't work with `__slots__`.")
    yield section("Interview angle", "message-question")
    yield qa("What is a descriptor?",
             "An object stored as a class attribute whose class implements `__get__`, `__set__` and/or `__delete__`. Attribute access on instances is routed through those methods. Properties, methods, `classmethod`, `staticmethod` and `__slots__` are all built on descriptors.")
    yield qa("Data vs non-data descriptor?",
             "A data descriptor defines `__set__` or `__delete__` and takes priority over the instance `__dict__`. A non-data descriptor defines only `__get__` and can be shadowed by a value in the instance `__dict__` — that's how `cached_property` caches, and why you can monkey-patch a method on one instance.")
    yield qa("`__getattr__` vs `__getattribute__`?",
             "`__getattribute__` is called for every attribute access; `__getattr__` is called only after normal lookup fails. Override `__getattr__` for fallbacks and proxies; override `__getattribute__` only if you really must intercept everything.")
    yield qa("When would you write a descriptor instead of a property?",
             "When the same logic (validation, type conversion, lazy loading, ORM columns) must apply to many attributes or many classes. A property is one-off; a descriptor is a reusable attribute type — like Django model fields or SQLAlchemy columns.")


@topic(G, "abc-protocols", "Abstract Base Classes & Protocols", "template")
def _():
    yield lead("Two ways to describe “what an object must be able to do”: **ABCs** check it by inheritance (nominal typing), **Protocols** by shape (structural typing — static duck typing).")
    yield section("abc.ABC and @abstractmethod", "template")
    yield p("An abstract base class can't be instantiated while it has abstract methods. Subclasses must implement every one of them — the error appears when you *create an object*, not when you call the missing method.")
    yield code('''
        from abc import ABC, abstractmethod

        class Exporter(ABC):
            """Template method pattern: export() fixes the algorithm, subclasses fill in the steps."""

            def export(self, rows):
                return [self.header()] + [self.format_row(r) for r in rows]

            @abstractmethod
            def header(self) -> str: ...

            @abstractmethod
            def format_row(self, row) -> str: ...

        class CsvExporter(Exporter):
            def header(self):
                return "name,score"
            def format_row(self, row):
                return f"{row[0]},{row[1]}"

        class Broken(Exporter):
            def header(self):
                return "x"

        print(CsvExporter().export([("asha", 91), ("ravi", 84)]))   # ['name,score', 'asha,91', 'ravi,84']
        try:
            Broken()
        except TypeError as e:
            print(e)   # Can't instantiate abstract class Broken without an implementation for abstract method 'format_row'
        print(sorted(Exporter.__abstractmethods__))                  # ['format_row', 'header']
    ''')
    yield section("Abstract properties & class methods", "stack")
    yield code('''
        from abc import ABC, abstractmethod

        class Shape(ABC):
            @property
            @abstractmethod                    # @abstractmethod must be the innermost decorator
            def sides(self) -> int: ...

            @classmethod
            @abstractmethod
            def unit(cls) -> "Shape": ...

            def describe(self):                # ABCs can hold ordinary, shared methods too
                return f"{type(self).__name__} with {self.sides} sides"

        class Triangle(Shape):
            sides = 3                          # a plain class attribute satisfies the abstract property
            @classmethod
            def unit(cls):
                return cls()

        print(Triangle.unit().describe())      # Triangle with 3 sides
    ''')
    yield note("An abstract method may still have a body; subclasses can call it with `super().method()` — handy for shared default behaviour that must be consciously opted into.")
    yield section("collections.abc: get methods for free", "list")
    yield p("The ABCs in `collections.abc` are *mixins*: implement the few abstract methods and inherit the rest. Implement `__getitem__` + `__len__` and `Sequence` gives you `in`, iteration, `reversed`, `index` and `count`.")
    yield code('''
        from collections.abc import Sequence

        class Countdown(Sequence):
            def __init__(self, n):
                self.n = n
            def __len__(self):
                return self.n
            def __getitem__(self, i):
                if isinstance(i, slice):
                    return [self[j] for j in range(*i.indices(len(self)))]
                if i < 0:
                    i += self.n
                if not 0 <= i < self.n:
                    raise IndexError(i)
                return self.n - i

        c = Countdown(5)
        print(list(c), c[-1], c[1:3])             # [5, 4, 3, 2, 1] 1 [4, 3]
        print(3 in c, c.index(2), c.count(9))     # True 3 0
        print(list(reversed(c)))                  # [1, 2, 3, 4, 5]
    ''')
    yield table(
        ["ABC", "You implement", "You get for free"],
        ["`Iterable`", "`__iter__`", "—"],
        ["`Iterator`", "`__next__`", "`__iter__`"],
        ["`Sequence`", "`__getitem__`, `__len__`", "`__contains__`, `__iter__`, `__reversed__`, `index`, `count`"],
        ["`MutableSequence`", "+ `__setitem__`, `__delitem__`, `insert`", "`append`, `extend`, `pop`, `remove`, `+=`…"],
        ["`Mapping`", "`__getitem__`, `__iter__`, `__len__`", "`get`, `keys`, `items`, `values`, `==`, `in`"],
        ["`MutableMapping`", "+ `__setitem__`, `__delitem__`", "`pop`, `setdefault`, `update`, `clear`…"],
        ["`Set`", "`__contains__`, `__iter__`, `__len__`", "`<=`, `|`, `&`, `-`, `^`, `isdisjoint`"],
    )
    yield section("isinstance with ABCs, register & __subclasshook__", "checks")
    yield code('''
        from collections.abc import Iterable, Mapping, Sized, Hashable, Callable

        print(isinstance([1], Iterable), isinstance({}, Mapping))      # True True
        print(isinstance("abc", Hashable), isinstance([], Hashable))   # True False

        class Bag:                     # doesn't inherit from Sized...
            def __len__(self):
                return 0

        print(isinstance(Bag(), Sized), isinstance(len, Callable))     # True True
    ''')
    yield p("Some ABCs (`Sized`, `Iterable`, `Hashable`, `Callable`…) check structurally through `__subclasshook__`: any class with the right method counts. You can also declare a *virtual subclass* with `register`.")
    yield code('''
        from abc import ABC, abstractmethod
        import io

        class Drawable(ABC):
            pass

        class LegacyWidget:                    # third-party class you can't modify
            def draw(self):
                return "drawn"

        Drawable.register(LegacyWidget)        # a *virtual* subclass
        print(isinstance(LegacyWidget(), Drawable), Drawable in LegacyWidget.__mro__)   # True False

        class Closeable(ABC):
            @abstractmethod
            def close(self): ...

            @classmethod
            def __subclasshook__(cls, C):      # structural check: "has a close() method"
                if cls is Closeable:
                    return any("close" in B.__dict__ for B in C.__mro__) or NotImplemented
                return NotImplemented

        print(isinstance(io.StringIO(), Closeable), isinstance(42, Closeable))   # True False
    ''')
    yield warn("`register` is a promise, not a check — Python never verifies that the registered class really implements the methods.")
    yield section("typing.Protocol — structural typing", "puzzle")
    yield p("A `Protocol` lists the methods a type needs. Any class with those methods matches — no inheritance, no registration. Type checkers (mypy, pyright) verify it statically; `@runtime_checkable` also enables `isinstance`.")
    yield code('''
        from typing import Protocol, runtime_checkable

        @runtime_checkable
        class SupportsArea(Protocol):
            def area(self) -> float: ...

        class Square:                          # no mention of SupportsArea anywhere
            def __init__(self, s):
                self.s = s
            def area(self):
                return self.s ** 2

        class Rect:
            def __init__(self, w, h):
                self.w, self.h = w, h
            def area(self):
                return self.w * self.h

        def total_area(shapes: list[SupportsArea]) -> float:
            return sum(s.area() for s in shapes)

        print(total_area([Square(2), Rect(2, 3)]))                     # 10
        print(isinstance(Square(1), SupportsArea), isinstance("x", SupportsArea))   # True False
    ''')
    yield warn("A runtime `isinstance` check against a Protocol only checks that the method **names** exist — not their signatures or return types. Signature checking happens only in the type checker.")
    yield section("ABC or Protocol?", "scale")
    yield table(
        ["", "ABC (`abc.ABC`)", "Protocol (`typing.Protocol`)"],
        ["Typing style", "Nominal — must inherit or `register`", "Structural — just have the methods"],
        ["Enforced", "At instantiation (`TypeError`)", "By the static type checker"],
        ["Shared code", "Yes — concrete methods, template methods", "Possible, but only for explicit subclasses"],
        ["Works with third-party classes", "Only via `register`", "Automatically"],
        ["Best for", "Frameworks and class hierarchies you own", "Library APIs, callbacks, “anything with `.read()`”"],
    )
    yield dodont(
        "Use an ABC when you own the hierarchy and want to share implementation; use a Protocol to describe what a function *accepts* from arbitrary callers.",
        "Creating an ABC for every class “just in case” — in Python, plain duck typing is often enough.",
    )
    yield section("Interview angle", "message-question")
    yield qa("Why can't you instantiate a class with abstract methods?",
             "`ABCMeta` records unimplemented `@abstractmethod`s in `__abstractmethods__`; `object.__new__` refuses to create an instance while that set is non-empty. The subclass becomes concrete once it overrides all of them.")
    yield qa("Nominal vs structural typing?",
             "Nominal: a type matches only if it *declares* the relationship (inherits from the ABC). Structural: a type matches if it *has the required members* (Protocol). Python's runtime is duck-typed; Protocols bring that duck typing to static type checkers.")
    yield qa("What does collections.abc give you beyond isinstance checks?",
             "Mixin methods. Subclass `Sequence`, `Mapping` or `MutableSet`, implement the handful of abstract methods, and you inherit a full, consistent API — the safe way to build a custom container instead of subclassing `list` or `dict` directly.")


@topic(G, "dataclasses-typing", "Dataclasses & __slots__", "file-certificate")
def _():
    yield lead("`@dataclass` writes the boring methods (`__init__`, `__repr__`, `__eq__`…) from type-annotated fields. `__slots__` trims per-object memory. Together they make compact, readable data classes.")
    yield section("@dataclass basics", "wand")
    yield code('''
        from dataclasses import dataclass, field

        @dataclass(order=True)
        class Student:
            name: str
            marks: int = 0
            tags: list[str] = field(default_factory=list)   # never a bare [] default

        s = Student("Asha", 91)
        print(s)                                    # Student(name='Asha', marks=91, tags=[])
        print(s == Student("Asha", 91))             # True
        print(sorted([Student("b", 2), Student("a", 5)])[0].name)   # a
    ''')
    yield table(
        ["Option", "Effect"],
        ["`@dataclass`", "Generates `__init__`, `__repr__`, `__eq__`"],
        ["`order=True`", "Adds `<`, `<=`, `>`, `>=` comparing fields as a tuple, in order"],
        ["`frozen=True`", "Assigning a field raises `FrozenInstanceError`; instances become hashable"],
        ["`slots=True`", "Uses `__slots__` — less memory, faster attribute access (3.10+)"],
        ["`kw_only=True`", "Every field must be passed by keyword (3.10+)"],
        ["`field(default_factory=…)`", "A fresh mutable default per instance"],
    )
    yield code('''
        from dataclasses import dataclass

        try:
            @dataclass
            class Bad:
                items: list = []
        except ValueError as e:
            print(e)   # mutable default <class 'list'> for field items is not allowed: use default_factory
    ''')
    yield section("__post_init__: validate and derive", "checks")
    yield code('''
        from dataclasses import dataclass, field

        @dataclass
        class Rectangle:
            w: float
            h: float
            area: float = field(init=False)      # computed — not an __init__ parameter

            def __post_init__(self):             # runs right after the generated __init__
                if self.w <= 0 or self.h <= 0:
                    raise ValueError("sides must be positive")
                self.area = self.w * self.h

        print(Rectangle(3, 4))                   # Rectangle(w=3, h=4, area=12)
        try:
            Rectangle(0, 4)
        except ValueError as e:
            print(e)                             # sides must be positive
    ''')
    yield section("Frozen dataclasses & helpers", "snowflake")
    yield code('''
        from dataclasses import dataclass, replace, asdict, astuple, FrozenInstanceError

        @dataclass(frozen=True)
        class Point:
            x: int
            y: int

        p = Point(1, 2)
        try:
            p.x = 5
        except FrozenInstanceError:
            print("frozen")                        # frozen
        q = replace(p, y=9)                        # copy with some fields changed
        print(q, len({p, Point(1, 2)}))            # Point(x=1, y=9) 1
        print(asdict(q), astuple(q))               # {'x': 1, 'y': 9} (1, 9)
    ''')
    yield note("`asdict()` recurses into nested dataclasses, lists and dicts — handy right before `json.dumps`.")
    yield section("Field options, keyword-only fields & InitVar", "adjustments")
    yield code('''
        from dataclasses import dataclass, field, KW_ONLY, InitVar

        @dataclass
        class User:
            name: str
            password: str = field(repr=False)                     # hidden from repr
            login_count: int = field(default=0, compare=False)    # ignored by ==
            _: KW_ONLY                                            # everything below is keyword-only
            admin: bool = False

        a = User("asha", "s3cret", 5)
        print(a)                                  # User(name='asha', login_count=5, admin=False)
        print(a == User("asha", "s3cret", 1, admin=False))   # True

        @dataclass
        class Account:
            owner: str
            raw_pin: InitVar[str]                 # passed to __init__ and __post_init__, never stored
            pin_len: int = field(init=False)

            def __post_init__(self, raw_pin):
                self.pin_len = len(raw_pin)

        acc = Account("ravi", "1234")
        print(acc, hasattr(acc, "raw_pin"))       # Account(owner='ravi', pin_len=4) False
    ''')
    yield table(
        ["`field(...)` argument", "Meaning"],
        ["`default` / `default_factory`", "Default value / zero-argument callable producing one"],
        ["`init=False`", "Not an `__init__` parameter (set it in `__post_init__`)"],
        ["`repr=False`", "Left out of `__repr__` (secrets, huge blobs)"],
        ["`compare=False`", "Ignored by `==` and ordering"],
        ["`hash=None`", "Follows `compare` for hashing"],
        ["`kw_only=True`", "This one field is keyword-only"],
    )
    yield section("dataclass vs the alternatives", "scale")
    yield table(
        ["Tool", "Mutable", "Validation", "Best for"],
        ["`@dataclass`", "Yes (or `frozen=True`)", "Manual, in `__post_init__`", "Plain internal records with behaviour"],
        ["`typing.NamedTuple`", "No", "None", "Lightweight immutable records that also behave as tuples"],
        ["`TypedDict`", "Yes (it's a `dict`)", "Static only", "Typing JSON-like dicts you receive"],
        ["`attrs` (3rd-party)", "Yes", "Validators & converters", "Everything dataclasses do, plus more"],
        ["`pydantic` (3rd-party)", "Yes", "Full runtime parsing & coercion", "API payloads, configs, untrusted input"],
    )
    yield section("__slots__", "database")
    yield code('''
        from dataclasses import dataclass

        class Point:
            __slots__ = ("x", "y")      # fixed attributes, no per-instance __dict__
            def __init__(self, x, y):
                self.x, self.y = x, y

        p = Point(1, 2)
        try:
            p.z = 3
        except AttributeError:
            print("no new attributes")  # no new attributes
        print(hasattr(p, "__dict__"))   # False

        @dataclass(slots=True)
        class Pixel:
            x: int
            y: int
        print(Pixel.__slots__)          # ('x', 'y')
    ''')
    yield note("`__slots__` saves memory when you create millions of small objects, at the cost of not being able to add attributes dynamically (and no `cached_property`). Subclasses need their own `__slots__` to keep the benefit.")
    yield section("Enums & type hints in brief", "tag")
    yield code('''
        from enum import Enum, auto
        from typing import Optional

        class Status(Enum):
            TODO = auto()
            DONE = auto()

        def find(names: list[str], target: str) -> Optional[int]:
            return names.index(target) if target in names else None

        print(Status.DONE, Status.DONE.value)       # Status.DONE 2
        print(find(["a", "b"], "b"), find([], "x")) # 1 None
    ''')
    yield p("Both get their own topics: see **Enums in Depth** and **Type Hints & mypy**.")
    yield qa("Why does a dataclass refuse `items: list = []`?",
             "Defaults are evaluated once, so every instance would share one list — the same bug as a mutable default argument. `dataclasses` detects `list`, `dict` and `set` defaults and raises `ValueError`; use `field(default_factory=list)`.")
    yield qa("When is a dataclass hashable?",
             "With the default `eq=True`, `__hash__` is set to `None` (unhashable), because mutable objects that compare by value must not be hashed. Use `frozen=True` (or `unsafe_hash=True` if you know what you're doing) to get a field-based `__hash__`.")


@topic(G, "enums", "Enums in Depth", "list-numbers")
def _():
    yield lead("An `Enum` is a fixed set of named, unique constants. Members are singletons, are iterable in definition order, and make invalid states unrepresentable — no more magic strings and numbers.")
    yield section("Basics: names, values, lookup", "list-numbers")
    yield code('''
        from enum import Enum

        class Color(Enum):
            RED = 1
            GREEN = 2
            BLUE = 3

        print(Color.RED, repr(Color.RED))            # Color.RED <Color.RED: 1>
        print(Color(2), Color["BLUE"])               # Color.GREEN Color.BLUE
        print(Color.RED.name, Color.RED.value)       # RED 1
        print(len(Color), [c.name for c in Color])   # 3 ['RED', 'GREEN', 'BLUE']
        print(Color.RED == 1, Color.RED is Color(1)) # False True
        try:
            Color(7)
        except ValueError as e:
            print(e)                                 # 7 is not a valid Color
    ''')
    yield table(
        ["You have", "You want", "Write"],
        ["a value (e.g. from a DB)", "the member", "`Color(2)`"],
        ["a name (e.g. from config)", "the member", "`Color['GREEN']`"],
        ["a member", "its name / value", "`m.name` / `m.value`"],
        ["the class", "all members", "`list(Color)` or `Color.__members__`"],
    )
    yield note("Members are **singletons**, so compare them with `is` (or `==`). A plain `Enum` member never equals its raw value: `Color.RED == 1` is `False`.")
    yield section("auto() and generated values", "wand")
    yield code('''
        from enum import Enum, auto

        class Status(Enum):
            TODO = auto()
            DOING = auto()
            DONE = auto()

        class Method(Enum):
            @staticmethod
            def _generate_next_value_(name, start, count, last_values):
                return name.lower()                # customise what auto() produces
            GET = auto()
            POST = auto()

        print([s.value for s in Status])           # [1, 2, 3]
        print(Method.POST.value)                   # post
    ''')
    yield section("Aliases and @unique", "copy")
    yield code('''
        from enum import Enum, unique

        class Shape(Enum):
            SQUARE = 2
            CIRCLE = 3
            BOX = 2                                  # same value → an alias of SQUARE

        print(Shape.BOX, Shape(2))                   # Shape.SQUARE Shape.SQUARE
        print([s.name for s in Shape], list(Shape.__members__))   # ['SQUARE', 'CIRCLE'] ['SQUARE', 'CIRCLE', 'BOX']

        try:
            @unique
            class Bad(Enum):
                A = 1
                B = 1
        except ValueError as e:
            print(e)                                 # duplicate values found in <enum 'Bad'>: B -> A
    ''')
    yield section("IntEnum, StrEnum & Flag", "category")
    yield code('''
        from enum import IntEnum, StrEnum, auto

        class Priority(IntEnum):
            LOW = 1
            HIGH = 3

        class Env(StrEnum):                          # 3.11+
            DEV = auto()                             # StrEnum's auto() → the lower-cased name
            PROD = auto()

        print(Priority.HIGH > Priority.LOW, Priority.HIGH + 1)   # True 4
        print(sorted([3, Priority.LOW]))                         # [<Priority.LOW: 1>, 3]
        print(Env.PROD, Env.PROD == "prod", Env.DEV.upper())     # prod True DEV
        print(f"api-{Env.DEV}.example.com")                     # api-dev.example.com
    ''')
    yield code('''
        from enum import Flag, auto

        class Perm(Flag):
            READ = auto()        # 1
            WRITE = auto()       # 2
            EXEC = auto()        # 4
            RW = READ | WRITE    # a named combination

        p = Perm.READ | Perm.EXEC
        print(p)                                         # Perm.READ|EXEC
        print(Perm.READ in p, Perm.WRITE in p)           # True False
        print(Perm.RW.value, [m.name for m in Perm.RW])  # 3 ['READ', 'WRITE']
        print(p & ~Perm.EXEC, bool(Perm(0)))             # Perm.READ False
    ''')
    yield table(
        ["Type", "Members are also…", "Use when"],
        ["`Enum`", "nothing else", "Default choice — strict, can't be mixed up with ints/strings"],
        ["`IntEnum`", "`int`s", "Interop with code/protocols that expect integers (HTTP status, DB codes)"],
        ["`StrEnum`", "`str`s", "Values go into JSON, URLs, logs, config files"],
        ["`Flag` / `IntFlag`", "bit flags", "Combinable options: permissions, feature toggles"],
    )
    yield warn("`IntEnum`/`StrEnum` members compare equal to raw ints/strings — convenient, but it gives up some of the type safety that makes enums useful. Prefer plain `Enum` unless you need the interop.")
    yield section("Methods, properties & data on members", "code")
    yield code('''
        from enum import Enum

        class Planet(Enum):
            MERCURY = (3.303e23, 2.4397e6)
            EARTH = (5.976e24, 6.37814e6)

            def __init__(self, mass, radius):       # the tuple value is unpacked into __init__
                self.mass, self.radius = mass, radius

            @property
            def gravity(self):
                return round(6.673e-11 * self.mass / self.radius ** 2, 2)

            @classmethod
            def heaviest(cls):
                return max(cls, key=lambda p: p.mass)

        print(Planet.EARTH.gravity, Planet.heaviest().name)   # 9.8 EARTH
    ''')
    yield section("Enums in match & JSON", "binary-tree")
    yield code('''
        import json
        from enum import Enum, StrEnum

        class Light(Enum):
            RED = "stop"
            YELLOW = "slow"
            GREEN = "go"

        def action(light):
            match light:
                case Light.RED | Light.YELLOW:        # dotted names are value patterns
                    return "brake"
                case Light.GREEN:
                    return "drive"

        print(action(Light.YELLOW), action(Light("go")))              # brake drive

        class Role(StrEnum):
            ADMIN = "admin"

        print(json.dumps({"role": Role.ADMIN}))                       # {"role": "admin"}
        try:
            json.dumps({"light": Light.RED})
        except TypeError:
            print("plain Enum is not JSON serializable")              # plain Enum is not JSON serializable
        print(json.dumps({"light": Light.RED}, default=lambda e: e.value))   # {"light": "stop"}
        print(Light(json.loads('{"light": "stop"}')["light"]))       # Light.RED
    ''')
    yield section("Interview angle", "message-question")
    yield qa("Why use an Enum instead of string or int constants?",
             "Typos become `AttributeError`s instead of silent bugs, the set of valid values is explicit and iterable, members carry a readable name in logs and reprs, and type checkers can verify that a function only receives valid members (and that a `match` handles all of them).")
    yield qa("How do you convert between an enum and its stored value?",
             "`Member.value` to store it (DB/JSON), `EnumClass(value)` to get the member back (raises `ValueError` for unknown values), and `EnumClass[name]` to look up by name.")
    yield qa("What is an enum alias?",
             "A second name defined with the same value. It resolves to the first member (`Shape.BOX is Shape.SQUARE`) and is skipped during iteration. Decorate the class with `@unique` to forbid aliases.")


@topic(G, "metaclasses", "Metaclasses & Class Creation", "building-factory")
def _():
    yield lead("Classes are objects too — created at runtime by a *metaclass*, which is `type` by default. Knowing how class creation works explains `__new__`, `__init_subclass__`, `ABC` and how frameworks like Django build models.")
    yield section("Classes are objects created by type", "box")
    yield code('''
        class Dog:
            sound = "woof"

        print(type(Dog), type(type))          # <class 'type'> <class 'type'>
        print(isinstance(Dog, object))        # True

        # The class statement is sugar for calling type(name, bases, namespace):
        Cat = type("Cat", (), {"sound": "meow", "speak": lambda self: self.sound})
        print(Cat().speak(), Cat.__name__)    # meow Cat
    ''')
    yield define("Metaclass", "the class of a class. `type(obj)` gives an object's class; `type(SomeClass)` gives its metaclass. Instances are made by classes; classes are made by metaclasses.")
    yield section("What happens when `class` runs", "list-numbers")
    yield steps(
        ("Pick the metaclass", "The explicit `metaclass=` keyword, else the most derived metaclass of the bases, else `type`."),
        ("Prepare the namespace", "`metaclass.__prepare__(name, bases)` returns the mapping the body will fill (a plain `dict` by default)."),
        ("Run the body", "The class body executes like a function body; every assignment and `def` lands in that namespace."),
        ("Create the class", "`metaclass(name, bases, namespace)` → `__new__` builds the class object, `__init__` initialises it."),
        ("Notify", "`type.__new__` calls `__set_name__` on each attribute (descriptors) and `__init_subclass__` on the parent."),
        ("Decorate", "Finally, class decorators are applied (`@dataclass` runs here)."),
    )
    yield section("__new__ vs __init__", "player-play")
    yield p("`__new__(cls, …)` **creates** and returns the instance; `__init__(self, …)` **initialises** it. You rarely override `__new__` — except for immutable types (whose value must be fixed at creation) and instance control such as singletons or caching.")
    yield code('''
        class Singleton:
            _instance = None

            def __new__(cls, *args, **kwargs):
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                return cls._instance

            def __init__(self, value):
                self.value = value            # NOTE: still runs on every call

        a = Singleton(1)
        b = Singleton(2)
        print(a is b, a.value)                # True 2

        class Celsius(float):                 # float is immutable → customise __new__, not __init__
            def __new__(cls, degrees):
                if degrees < -273.15:
                    raise ValueError("below absolute zero")
                return super().__new__(cls, round(degrees, 1))

        print(Celsius(21.456), Celsius(10) + 5)   # 21.5 15.0
    ''')
    yield warn("If `__new__` returns an instance of the class, `__init__` is called on it **every time** — which is why `a.value` became 2 above. For a real singleton, a module-level instance is usually simpler.")
    yield section("__init_subclass__: the easy hook (preferred)", "plug")
    yield p("Most metaclass use cases are really “do something whenever a subclass is defined”. `__init_subclass__` (3.6+) does exactly that with an ordinary classmethod — no metaclass needed.")
    yield code('''
        class Plugin:
            registry = {}

            def __init_subclass__(cls, /, name=None, **kwargs):
                super().__init_subclass__(**kwargs)
                Plugin.registry[name or cls.__name__.lower()] = cls

        class CsvLoader(Plugin, name="csv"):     # class keyword arguments reach __init_subclass__
            pass

        class JsonLoader(Plugin):
            pass

        print(list(Plugin.registry))             # ['csv', 'jsonloader']
        print(Plugin.registry["csv"] is CsvLoader)   # True
    ''')
    yield section("Writing a metaclass", "building-factory")
    yield code('''
        class RequireDocs(type):
            """Reject public methods without a docstring — checked when the class is defined."""
            def __new__(mcls, name, bases, ns):
                for attr, value in ns.items():
                    if callable(value) and not attr.startswith("_") and not value.__doc__:
                        raise TypeError(f"{name}.{attr} needs a docstring")
                return super().__new__(mcls, name, bases, ns)

        class Service(metaclass=RequireDocs):
            def run(self):
                """Run the service."""

        print(type(Service).__name__)            # RequireDocs
        try:
            class Worker(Service):               # the metaclass is inherited by subclasses
                def stop(self):
                    pass
        except TypeError as e:
            print(e)                             # Worker.stop needs a docstring

        class SingletonMeta(type):
            _instances = {}
            def __call__(cls, *args, **kwargs):  # runs on Config(...) — before __new__/__init__
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
                return cls._instances[cls]

        class Config(metaclass=SingletonMeta):
            pass

        print(Config() is Config())              # True
    ''')
    yield table(
        ["Metaclass method", "Runs when", "Used for"],
        ["`__prepare__`", "Before the class body", "Custom namespace (e.g. record definition order, forbid duplicates)"],
        ["`__new__`", "Class object is created", "Inspect / modify the namespace, validate, register"],
        ["`__init__`", "After `__new__`", "Post-creation setup"],
        ["`__call__`", "`MyClass(...)` is called", "Control instance creation: singletons, caching, pooling"],
    )
    yield section("Lighter alternatives", "feather")
    yield code('''
        class Box:
            def __class_getitem__(cls, item):    # powers Box[int] without a metaclass
                return f"Box of {item.__name__}"

        def add_repr(cls):                        # a class decorator: receives the finished class
            cls.__repr__ = lambda self: f"<{cls.__name__} {vars(self)}>"
            return cls

        @add_repr
        class Point:
            def __init__(self, x):
                self.x = x

        from abc import ABC
        print(Box[int], Point(3))                 # Box of int <Point {'x': 3}>
        print(type(ABC).__name__)                 # ABCMeta
    ''')
    yield table(
        ["Need", "Reach for"],
        ["Modify or register one class after it's built", "Class decorator"],
        ["React to every subclass being defined", "`__init_subclass__`"],
        ["Know the attribute name a field was assigned to", "Descriptor `__set_name__`"],
        ["Make `MyClass[...]` work", "`__class_getitem__`"],
        ["Change how the class namespace or `MyClass()` itself behaves", "Metaclass"],
    )
    yield note("“Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't.” — Tim Peters", "Rule of thumb")
    yield warn("A class can have only one metaclass. Inheriting from two bases with unrelated metaclasses (e.g. an `ABC` and a Django model) raises `TypeError: metaclass conflict`.")
    yield section("Interview angle", "message-question")
    yield qa("What is a metaclass?",
             "The class of a class — the object that creates class objects. The default is `type`. Defining `__new__`/`__init__`/`__call__` on a custom metaclass lets you customise class creation and instantiation. `ABCMeta`, Django's `ModelBase` and `EnumType` are real examples.")
    yield qa("What is the difference between `__new__` and `__init__`?",
             "`__new__` is a static method that creates and returns the new object; `__init__` receives that object and sets it up, returning `None`. Override `__new__` for immutable subclasses (`int`, `str`, `tuple`), singletons or instance caching.")
    yield qa("How would you auto-register every subclass of a base class?",
             "Define `__init_subclass__` on the base and add `cls` to a registry dict. It's simpler and composes better than a metaclass, and it can take class keyword arguments (`class A(Base, name='a')`).")
