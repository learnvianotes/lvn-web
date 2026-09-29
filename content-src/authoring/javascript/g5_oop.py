from kit import *

G = "Prototypes & Classes"


@topic(G, "prototypes", "Prototypes & the Prototype Chain", "hierarchy")
def _():
    yield lead("JavaScript objects inherit directly from other objects. Every object has a hidden link, `[[Prototype]]`, and property lookups walk that chain until they find a match or hit `null`.")
    yield define("Prototype", "the object another object delegates to for properties it does not have itself. Read it with `Object.getPrototypeOf(obj)` (or the legacy `obj.__proto__`).")
    yield section("Lookup walks the chain", "link")
    yield snippet("js", '''
        const animal = { eats: true, describe() { return `${this.name} eats: ${this.eats}`; } };
        const rabbit = Object.create(animal);
        rabbit.name = "Bunny";
        rabbit.jumps = true;

        console.log(rabbit.jumps, rabbit.eats, rabbit.describe());
        console.log(Object.hasOwn(rabbit, "eats"), "eats" in rabbit);
        console.log(Object.getPrototypeOf(rabbit) === animal);
        console.log(Object.getPrototypeOf(animal) === Object.prototype);
        console.log(Object.getPrototypeOf(Object.prototype));
    ''', out='''
        true true Bunny eats: true
        false true
        true
        true
        null
    ''')
    yield flow("`rabbit`", "`animal`", "`Object.prototype`", "`null`")
    yield section("Writes do not walk the chain", "pencil")
    yield snippet("js", '''
        const proto = { greeting: "hello", list: [] };
        const child = Object.create(proto);
        child.greeting = "hi";           // creates an OWN property (shadowing)
        child.list.push(1);              // mutates the SHARED array on the prototype
        console.log(child.greeting, proto.greeting, proto.list);
    ''', out="hi hello [ 1 ]")
    yield section("`prototype` vs `[[Prototype]]`", "arrows-exchange")
    yield p("Two different things with confusingly similar names:")
    yield cards(
        ("`Fn.prototype`", "A regular property that exists on functions (and classes). It becomes the `[[Prototype]]` of objects created with `new Fn()`.", "function"),
        ("`[[Prototype]]` / `__proto__`", "The internal link every object has, pointing to the object it inherits from.", "link"),
    )
    yield snippet("js", '''
        function Dog(name) { this.name = name; }
        Dog.prototype.bark = function () { return `${this.name}: woof`; };

        const rex = new Dog("Rex");
        console.log(rex.bark());
        console.log(Object.getPrototypeOf(rex) === Dog.prototype);
        console.log(Dog.prototype.constructor === Dog, rex.constructor.name);
        console.log(Object.hasOwn(rex, "bark"), rex instanceof Dog);
    ''', out='''
        Rex: woof
        true
        true Dog
        false true
    ''')
    yield note("Methods live **once** on the prototype and are shared by every instance — cheaper than giving each instance its own copy.")
    yield section("Built-in chains", "sitemap")
    yield snippet("js", '''
        const arr = [1, 2];
        console.log(Object.getPrototypeOf(arr) === Array.prototype);
        console.log(Object.getPrototypeOf(Array.prototype) === Object.prototype);
        const fn = () => {};
        console.log(Object.getPrototypeOf(fn) === Function.prototype);
        console.log(arr.hasOwnProperty("length"), arr.hasOwnProperty("map"));
    ''', out='''
        true
        true
        true
        true false
    ''')
    yield section("How instanceof works", "search")
    yield snippet("js", '''
        function myInstanceOf(obj, Ctor) {
          let proto = Object.getPrototypeOf(obj);
          while (proto !== null) {
            if (proto === Ctor.prototype) return true;
            proto = Object.getPrototypeOf(proto);
          }
          return false;
        }
        console.log(myInstanceOf([], Array), myInstanceOf([], Object), myInstanceOf([], Map));
    ''', out="true true false")
    yield warn("Never extend built-in prototypes (`Array.prototype.myThing = …`) in shared code — it can clash with future standard methods (this is why `Array.prototype.flatten` had to be renamed `flat`).")
    yield qa("Explain prototypal inheritance.",
             "Each object has an internal `[[Prototype]]` link to another object. When a property is not found on the object, the engine looks it up on the prototype, then that object's prototype, and so on until `null`. Methods are shared this way; classes are syntax over the same mechanism.")
    yield qa("What is the difference between __proto__ and prototype?",
             "`__proto__` (really `[[Prototype]]`) is the link on every object to what it inherits from. `prototype` is a property on constructor functions/classes: the object that becomes the `[[Prototype]]` of instances created with `new`.")


@topic(G, "constructors-new", "Constructor Functions & new", "building-factory-2")
def _():
    yield lead("Before classes there were constructor functions. Knowing what `new` does step by step explains classes, `this`, and a favourite interview question.")
    yield section("What `new Fn(args)` does", "list-numbers")
    yield steps(
        ("Create", "A brand-new empty object is created."),
        ("Link", "Its `[[Prototype]]` is set to `Fn.prototype`."),
        ("Bind and run", "`Fn` is called with `this` = the new object and the given arguments."),
        ("Return", "If `Fn` returns an **object**, that object is the result; otherwise the new object is returned."),
    )
    yield snippet("js", '''
        function myNew(Ctor, ...args) {
          const obj = Object.create(Ctor.prototype);   // steps 1 + 2
          const result = Ctor.apply(obj, args);        // step 3
          return result !== null && typeof result === "object" ? result : obj;  // step 4
        }

        function User(name) { this.name = name; }
        User.prototype.hi = function () { return `hi ${this.name}`; };

        const u = myNew(User, "Asha");
        console.log(u, u.hi(), u instanceof User);
    ''', out="User { name: 'Asha' } hi Asha true")
    yield section("Returning an object overrides `this`", "arrow-back")
    yield snippet("js", '''
        function A() { this.x = 1; return { y: 2 }; }
        function B() { this.x = 1; return 42; }   // primitives are ignored
        console.log(new A(), new B());
    ''', out="{ y: 2 } B { x: 1 }")
    yield section("Forgetting `new`", "alert-triangle")
    yield snippet("js", '''
        function Point(x) { this.x = x; }
        try {
          Point(5);                        // strict mode: this is undefined
        } catch (e) {
          console.log(e.message);
        }
        function SafePoint(x) {
          if (!new.target) return new SafePoint(x);   // guard with new.target
          this.x = x;
        }
        console.log(SafePoint(5));
    ''', out='''
        Cannot set properties of undefined (setting 'x')
        SafePoint { x: 5 }
    ''')
    yield section("Inheritance the ES5 way", "hierarchy-2")
    yield snippet("js", '''
        function Animal(name) { this.name = name; }
        Animal.prototype.speak = function () { return `${this.name} makes a sound`; };

        function Dog(name, breed) {
          Animal.call(this, name);                         // "super(name)"
          this.breed = breed;
        }
        Dog.prototype = Object.create(Animal.prototype);  // link prototypes
        Dog.prototype.constructor = Dog;                  // repair constructor
        Dog.prototype.speak = function () {
          return Animal.prototype.speak.call(this) + " (woof)";
        };

        const d = new Dog("Rex", "lab");
        console.log(d.speak(), d instanceof Animal, d.constructor.name);
    ''', out="Rex makes a sound (woof) true Dog")
    yield note("This is exactly what `class Dog extends Animal` does for you, with fewer ways to get it wrong.")
    yield qa("What happens when you call a function with new?",
             "A new object is created, linked to `Fn.prototype`, `Fn` runs with `this` bound to it, and the new object is returned unless the function explicitly returns another object.")


@topic(G, "classes", "Classes", "box-model-2")
def _():
    yield lead("`class` is clean syntax over prototypes — with real extras: public and `#private` fields, static members, static blocks, accessors, and strict mode by default.")
    yield section("Anatomy of a class", "code")
    yield snippet("js", '''
        class BankAccount {
          static bankName = "JS Bank";        // static field (on the class)
          static #count = 0;                  // private static field
          owner;                              // public instance field
          #balance = 0;                       // private instance field

          constructor(owner, deposit = 0) {
            this.owner = owner;
            this.#balance = deposit;
            BankAccount.#count++;
          }
          deposit(amount) {                   // method on BankAccount.prototype
            if (amount <= 0) throw new RangeError("amount must be positive");
            this.#balance += amount;
            return this;                      // enables chaining
          }
          get balance() { return this.#balance; }      // accessor
          #audit() { return `audited ${this.owner}`; } // private method
          report() { return this.#audit(); }
          static count() { return BankAccount.#count; }
        }

        const acc = new BankAccount("Asha", 100);
        acc.deposit(50).deposit(25);
        console.log(acc.balance, acc.report(), acc);
        console.log(BankAccount.bankName, BankAccount.count(), typeof BankAccount);
    ''', out='''
        175 audited Asha BankAccount { owner: 'Asha' }
        JS Bank 1 function
    ''')
    yield section("Private really means private", "lock")
    yield snippet("js", '''
        class Secret {
          #code = 1234;
          static isSecret(obj) { return #code in obj; }   // brand check (ES2022)
        }
        const s = new Secret();
        console.log(s.code, Object.keys(s), JSON.stringify(s));
        console.log(Secret.isSecret(s), Secret.isSecret({ code: 1 }));
    ''', out='''
        undefined [] {}
        true false
    ''')
    yield p("Accessing `s.#code` outside the class body is a **SyntaxError** — the program does not even parse. Before `#`, the convention was a leading underscore (`this._code`), which is only a hint.")
    yield section("Class fields with arrow functions", "arrow-right")
    yield snippet("js", '''
        class Button {
          label = "Save";
          handleArrow = () => `clicked ${this.label}`;   // per-instance, this is bound
          handleMethod() { return `clicked ${this?.label}`; }
        }
        const b = new Button();
        const { handleArrow, handleMethod } = b;          // detach both
        console.log(handleArrow(), "|", handleMethod.call(undefined));
        console.log(Object.hasOwn(b, "handleArrow"), Object.hasOwn(b, "handleMethod"));
    ''', out='''
        clicked Save | clicked undefined
        true false
    ''')
    yield note("Arrow-function fields fix lost-`this` in callbacks, but each instance gets its own copy (more memory) and they cannot be overridden via `super` — trade-offs worth mentioning.")
    yield section("Static blocks and getters", "bolt")
    yield snippet("js", '''
        class Config {
          static defaults;
          static {
            // runs once when the class is defined
            Config.defaults = Object.freeze({ retries: 3, timeout: 1000 });
          }
          static get retries() { return Config.defaults.retries; }
        }
        console.log(Config.retries, Config.defaults);
    ''', out="3 { retries: 3, timeout: 1000 }")
    yield section("Classes are special functions", "info-circle")
    yield table(
        ["Behaviour", "Detail"],
        ["Must be called with `new`", "`BankAccount()` → `TypeError: Class constructor … cannot be invoked without 'new'`"],
        ["Hoisted into the TDZ", "Using a class before its declaration throws `ReferenceError`"],
        ["Strict mode", "The whole class body is strict"],
        ["Methods are non-enumerable", "They do not show up in `for…in` over instances"],
        ["Fields run per instance", "Initialised before the constructor body (after `super()` in subclasses)"],
    )
    yield snippet("js", '''
        class Foo {}
        try {
          Foo();
        } catch (e) {
          console.log(e.message);
        }
    ''', out="Class constructor Foo cannot be invoked without 'new'")
    yield qa("Are JavaScript classes real classes?",
             "They are syntax over prototypal inheritance: a class is a constructor function, methods go on `Class.prototype`, and `extends` links prototype chains. But they add real semantics — mandatory `new`, strict mode, `#private` fields, `super`, and static blocks.")
    yield qa("How do you make a property private?",
             "Use a `#field` (hard privacy, enforced by the language, ES2022). Older options: closures (factory functions), `WeakMap` keyed by the instance, or the `_underscore` convention (not enforced).")


@topic(G, "inheritance", "Inheritance: extends & super", "hierarchy-3")
def _():
    yield lead("`extends` sets up the prototype chain between two classes; `super` calls the parent's constructor and methods.")
    yield section("Extending a class", "code")
    yield snippet("js", '''
        class Shape {
          constructor(name) { this.name = name; }
          area() { return 0; }
          toString() { return `${this.name} with area ${this.area().toFixed(2)}`; }
          static create(...args) { return new this(...args); }   // `this` = the called class
        }
        class Circle extends Shape {
          constructor(r) {
            super("Circle");           // must come before using `this`
            this.r = r;
          }
          area() { return Math.PI * this.r ** 2; }                // override
        }
        class Square extends Shape {
          constructor(side) { super("Square"); this.side = side; }
          area() { return this.side ** 2; }
          toString() { return "■ " + super.toString(); }          // extend parent method
        }

        const shapes = [new Circle(1), Square.create(2)];
        for (const s of shapes) console.log(String(s));
        console.log(shapes[1] instanceof Square, shapes[1] instanceof Shape);
    ''', out='''
        Circle with area 3.14
        ■ Square with area 4.00
        true true
    ''')
    yield section("Rules for super", "alert-triangle")
    yield snippet("js", '''
        class Parent {}
        class Child extends Parent {
          constructor() {
            this.x = 1;       // before super() → error
            super();
          }
        }
        try {
          new Child();
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
    ''', out="ReferenceError: Must call super constructor in derived class before accessing 'this' or returning from derived constructor")
    yield ul(
        "A subclass without its own `constructor` gets `constructor(...args) { super(...args); }` automatically.",
        "`super(...)` only in constructors; `super.method()` in any method (also static methods).",
        "Parent fields are initialised when `super()` returns; child fields right after.",
    )
    yield section("Polymorphism and the chain", "sitemap")
    yield snippet("js", '''
        class Animal { speak() { return "..."; } }
        class Dog extends Animal { speak() { return "Woof"; } }
        class Puppy extends Dog { speak() { return super.speak() + " (squeaky)"; } }

        for (const a of [new Animal(), new Dog(), new Puppy()]) {
          console.log(a.constructor.name.padEnd(6), a.speak());
        }
        console.log(Object.getPrototypeOf(Puppy) === Dog);                    // static inheritance
        console.log(Object.getPrototypeOf(Puppy.prototype) === Dog.prototype); // instance inheritance
    ''', out='''
        Animal ...
        Dog    Woof
        Puppy  Woof (squeaky)
        true
        true
    ''')
    yield section("Extending built-ins", "brackets")
    yield snippet("js", '''
        class Stack extends Array {
          peek() { return this.at(-1); }
        }
        const s = Stack.from([1, 2, 3]);
        s.push(4);
        console.log(s.peek(), s.length, s instanceof Array);
        console.log(s.map((x) => x * 2) instanceof Stack);   // derived methods return Stack

        class ValidationError extends Error {
          constructor(field) {
            super(`${field} is invalid`);
            this.name = "ValidationError";
            this.field = field;
          }
        }
        const err = new ValidationError("email");
        console.log(err.name, err.message, err instanceof Error);
    ''', out='''
        4 4 true
        true
        ValidationError email is invalid true
    ''')
    yield section("Composition over inheritance", "puzzle")
    yield p("Deep hierarchies are brittle. Often it is simpler to **compose** behaviours: build objects from small functions or *mixins*.")
    yield snippet("js", '''
        const canFly = (Base) => class extends Base { fly() { return `${this.name} flies`; } };
        const canSwim = (Base) => class extends Base { swim() { return `${this.name} swims`; } };
        class Creature { constructor(name) { this.name = name; } }
        class Duck extends canSwim(canFly(Creature)) {}

        const d = new Duck("Donald");
        console.log(d.fly(), "/", d.swim());

        // object composition with plain functions
        const withLogger = (obj) => ({ ...obj, log: (msg) => `[${obj.name}] ${msg}` });
        const service = withLogger({ name: "api" });
        console.log(service.log("started"));
    ''', out='''
        Donald flies / Donald swims
        [api] started
    ''')
    yield qa("Why must super() be called before this in a derived constructor?",
             "In a derived class the parent constructor is responsible for creating the object. Until `super()` runs there is no `this` to use, so accessing it throws a `ReferenceError`.")
    yield qa("Does JavaScript support multiple inheritance?",
             "No — an object has exactly one prototype. You get similar results with mixins (functions that take a class and return an extended class), `Object.assign` of method objects, or composition.")
