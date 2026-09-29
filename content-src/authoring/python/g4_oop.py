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


@topic(G, "dataclasses-typing", "Dataclasses, Enums & Type Hints", "file-certificate")
def _():
    yield lead("Less boilerplate, clearer intent: `@dataclass` writes the dull methods for you, `Enum` names your constants, and type hints document everything.")
    yield section("@dataclass", "wand")
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
        ["`order=True`", "Adds `<`, `<=`, `>`, `>=` comparing fields in order"],
        ["`frozen=True`", "Immutable instances (and hashable)"],
        ["`slots=True`", "Uses `__slots__` — less memory, faster attribute access (3.10+)"],
        ["`field(default_factory=…)`", "A fresh mutable default per instance"],
    )
    yield section("Enum", "list-numbers")
    yield code('''
        from enum import Enum, auto

        class Status(Enum):
            TODO = auto()
            DONE = auto()

        s = Status.DONE
        print(s, s.name, s.value)              # Status.DONE DONE 2
        print(Status["TODO"] is Status.TODO)   # True
        print([m.name for m in Status])        # ['TODO', 'DONE']
    ''')
    yield section("Type hints", "tag")
    yield code('''
        from typing import Optional, TypedDict, Callable

        def find(names: list[str], target: str) -> Optional[int]:
            return names.index(target) if target in names else None

        def apply(f: Callable[[int], int], x: int) -> int:
            return f(x)

        class User(TypedDict):
            id: int
            email: str

        u: User = {"id": 1, "email": "a@b.co"}
        print(find(["a", "b"], "b"), apply(lambda n: n * 2, 4), u["email"])   # 1 8 a@b.co
    ''')
    yield cards(
        ("Built-in generics", "`list[int]`, `dict[str, float]`, `tuple[int, ...]` (3.9+).", "brackets"),
        ("Unions", "`int | None` (3.10+) is the same as `Optional[int]`.", "arrows-join"),
        ("Checked by tools", "Hints are not enforced at runtime — run `mypy` or `pyright` to catch type errors.", "shield-check"),
        ("Why bother", "Better autocomplete, self-documenting signatures, fewer bugs in large code.", "bulb"),
    )
    yield section("__slots__", "database")
    yield code('''
        class Point:
            __slots__ = ("x", "y")      # no per-instance __dict__
            def __init__(self, x, y):
                self.x, self.y = x, y

        p = Point(1, 2)
        try:
            p.z = 3
        except AttributeError:
            print("no new attributes")  # no new attributes
    ''')
    yield note("`__slots__` saves memory when you create millions of small objects, at the cost of not being able to add attributes dynamically.")
