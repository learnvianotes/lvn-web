from kit import *

G = "Functions & Scope"


@topic(G, "functions", "Functions: Declarations, Expressions & Arrows", "function")
def _():
    yield lead("Functions are first-class objects: create them three ways, pass them around, return them — and pick arrows or regular functions for the right reasons.")
    yield section("Three ways to define a function", "code")
    yield snippet("js", '''
        // 1. Declaration — hoisted completely
        function add(a, b) {
          return a + b;
        }
        // 2. Expression — a value assigned to a variable (optionally named)
        const multiply = function mul(a, b) {
          return a * b;
        };
        // 3. Arrow function (ES2015) — concise, lexical `this`
        const square = (x) => x * x;
        const makePoint = (x, y) => ({ x, y });   // wrap object literals in ( )

        console.log(add(2, 3), multiply(2, 3), square(4), makePoint(1, 2));
        console.log(multiply.name, square.name, add.length);
    ''', out='''
        5 6 16 { x: 1, y: 2 }
        mul square 2
    ''')
    yield section("Declarations are hoisted, expressions are not", "arrow-bar-up")
    yield snippet("js", '''
        console.log(early());          // works: whole declaration is hoisted
        function early() { return "declared"; }

        try {
          late();
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
        const late = () => "expression";
    ''', out='''
        declared
        ReferenceError: Cannot access 'late' before initialization
    ''')
    yield section("Arrow vs regular functions", "arrows-diff")
    yield table(
        ["", "Regular `function`", "Arrow `=>`"],
        ["`this`", "Set by *how it is called*", "Inherited from the enclosing scope (lexical)"],
        ["`arguments`", "Yes", "No (use rest `...args`)"],
        ["Can be used with `new`", "Yes", "No — TypeError"],
        ["`prototype` property", "Yes", "No"],
        ["Hoisting", "Declarations are hoisted", "Like any `const` — TDZ"],
        ["Best for", "Methods, constructors, generators", "Callbacks, short transforms, keeping outer `this`"],
    )
    yield snippet("js", '''
        const Arrow = () => {};
        try {
          new Arrow();
        } catch (e) {
          console.log(e.message);
        }
        console.log(Arrow.prototype, typeof function () {}.prototype);
    ''', out='''
        Arrow is not a constructor
        undefined object
    ''')
    yield section("Functions are objects", "box")
    yield snippet("js", '''
        function greet(name) { return `Hi ${name}`; }
        greet.calls = 0;                       // attach properties like any object
        const fns = [greet, (s) => s.toUpperCase()];
        console.log(fns.map((f) => f("x")));
        console.log(typeof greet, greet instanceof Object, greet);
    ''', out='''
        [ 'Hi x', 'X' ]
        function true [Function: greet] { calls: 0 }
    ''')
    yield section("Return values", "arrow-back")
    yield ul(
        "A function without `return` (or with a bare `return;`) returns `undefined`.",
        "Arrow with a *concise body* (`x => x * 2`) returns the expression; with braces you need `return`.",
        "Automatic semicolon insertion: `return` followed by a newline returns `undefined` — keep the value on the same line.",
    )
    yield snippet("js", '''
        function broken() {
          return
            { ok: true };
        }
        const withBraces = (x) => { x * 2 };
        console.log(broken(), withBraces(2));
    ''', out="undefined undefined")
    yield qa("What is the difference between a function declaration and a function expression?",
             "A declaration (`function f() {}`) is a statement that is hoisted with its body, so it can be called before it appears. An expression creates the function as a value (assigned to a variable, passed as an argument); it only exists once that line runs.")
    yield qa("When should you NOT use an arrow function?",
             "As an object method that needs `this` to be the object, as a constructor, as a prototype method, as an event handler that needs `this` to be the element, or when you need `arguments` or a generator.")


@topic(G, "parameters", "Parameters, Defaults & Rest", "adjustments")
def _():
    yield lead("JavaScript never checks argument counts: missing ones are `undefined`, extras are ignored — defaults, rest parameters and destructuring make that manageable.")
    yield section("Missing and extra arguments", "question-mark")
    yield snippet("js", '''
        function show(a, b) {
          console.log(a, b, arguments.length);
        }
        show(1);
        show(1, 2, 3);
    ''', out='''
        1 undefined 1
        1 2 3
    ''')
    yield section("Default parameters", "adjustments-horizontal")
    yield snippet("js", '''
        function greet(name = "guest", greeting = `Hello, ${name}`) {
          return greeting;
        }
        console.log(greet());
        console.log(greet("Asha"));
        console.log(greet(undefined, "Hey"));   // undefined triggers the default
        console.log(greet(null));               // null does not
    ''', out='''
        Hello, guest
        Hello, Asha
        Hey
        Hello, null
    ''')
    yield note("Defaults are evaluated **at call time**, left to right, and can refer to earlier parameters. A fresh `[]` default is created on every call — no Python-style shared mutable default.")
    yield snippet("js", '''
        function append(item, list = []) {
          list.push(item);
          return list;
        }
        console.log(append(1), append(2));
        let counter = 0;
        const next = (id = ++counter) => id;
        console.log(next(), next(), next(99), next());
    ''', out='''
        [ 1 ] [ 2 ]
        1 2 99 3
    ''')
    yield section("Rest parameters vs `arguments`", "dots")
    yield snippet("js", '''
        function oldStyle() {
          console.log(Array.isArray(arguments), Array.from(arguments));
        }
        function modern(first, ...rest) {
          console.log(first, rest, Array.isArray(rest));
        }
        oldStyle(1, 2);
        modern(1, 2, 3);
        modern(1);
    ''', out='''
        false [ 1, 2 ]
        1 [ 2, 3 ] true
        1 [] true
    ''')
    yield table(
        ["", "`arguments`", "`...rest`"],
        ["Type", "Array-like object (no `map`)", "Real array"],
        ["In arrow functions", "Not available", "Works"],
        ["Contains", "All arguments", "Only the *remaining* ones"],
        ["Position", "—", "Must be the last parameter"],
    )
    yield section("Named options via destructuring", "list-details")
    yield snippet("js", '''
        function createUser({ name, role = "viewer", active = true } = {}) {
          return `${name} (${role}${active ? "" : ", inactive"})`;
        }
        console.log(createUser({ name: "Ravi" }));
        console.log(createUser({ name: "Mei", role: "admin", active: false }));
        console.log(createUser());
    ''', out='''
        Ravi (viewer)
        Mei (admin, inactive)
        undefined (viewer)
    ''')
    yield good("Use an options object for functions with more than 2–3 parameters: call sites become self-documenting and argument order stops mattering.")
    yield qa("What is the arguments object?",
             "An array-like object available inside regular (non-arrow) functions holding every argument passed. It has `length` and indices but no array methods. Prefer rest parameters in modern code.")


@topic(G, "scope-hoisting", "Scope, Scope Chain & Hoisting", "brackets-contain")
def _():
    yield lead("Scope decides where a name is visible. JavaScript uses *lexical* scope: what you can see is fixed by where the code is written, not where it is called.")
    yield section("Kinds of scope", "layers-subtract")
    yield table(
        ["Scope", "Created by", "Holds"],
        ["Global", "The program / script", "Globals, `globalThis` properties"],
        ["Module", "Each ES module file", "Top-level declarations of that module (not global!)"],
        ["Function", "Every function call", "Parameters, `var`, inner declarations"],
        ["Block", "`{ }`, `if`, `for`, `try`…", "`let`, `const`, `class` (and function declarations in strict mode)"],
    )
    yield section("The scope chain", "link")
    yield p("When a name is used, the engine looks in the current scope, then the enclosing one, and so on out to global. The first match wins (**shadowing**); if none matches → `ReferenceError`.")
    yield snippet("js", '''
        const level = "global";
        function outer() {
          const level = "outer";
          function inner() {
            const extra = "inner-only";
            console.log(level, extra);   // finds outer's `level`
          }
          inner();
        }
        outer();
        try {
          console.log(extra);
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
    ''', out='''
        outer inner-only
        ReferenceError: extra is not defined
    ''')
    yield section("Lexical, not dynamic", "map-pin")
    yield snippet("js", '''
        const x = "lexical";
        function readX() { return x; }
        function caller() {
          const x = "dynamic";
          return readX();              // readX sees where it was DEFINED
        }
        console.log(caller());
    ''', out="lexical")
    yield section("Hoisting summary", "arrow-bar-up")
    yield table(
        ["Declaration", "Hoisted?", "Value before the line runs"],
        ["`function f() {}`", "Yes", "The full function"],
        ["`var x`", "Yes", "`undefined`"],
        ["`let` / `const`", "Yes (binding)", "TDZ → `ReferenceError`"],
        ["`class C {}`", "Yes (binding)", "TDZ → `ReferenceError`"],
        ["`const f = () => {}`", "As a `const`", "TDZ"],
        ["`import`", "Yes", "Modules are linked before any code runs"],
    )
    yield snippet("js", '''
        console.log(typeof hoisted, typeof notYet);
        var notYet = function () {};
        function hoisted() {}

        var shadow = "global var";
        function test() {
          console.log(shadow);   // local var is hoisted → undefined, not "global var"
          var shadow = "local";
        }
        test();
    ''', out='''
        function undefined
        undefined
    ''')
    yield section("Accidental globals", "world")
    yield p("In sloppy mode, assigning to an undeclared name silently creates a global. In strict mode (and every ES module) it throws:")
    yield snippet("js", '''
        try {
          undeclaredTotal = 10;
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
    ''', out="ReferenceError: undeclaredTotal is not defined")
    yield qa("What is hoisting?",
             "During the creation phase of a scope, declarations are registered before code executes. Function declarations are available in full, `var`s start as `undefined`, and `let`/`const`/`class` exist but stay uninitialised (TDZ) until their line runs. Nothing is physically moved.")
    yield qa("What is lexical scoping?",
             "A function's accessible variables are determined by where it is written in the source. Each function remembers the scope it was created in — which is exactly what makes closures possible.")


@topic(G, "closures", "Closures", "lock-access")
def _():
    yield lead("A closure is a function bundled with the variables of the scope where it was created — it keeps them alive even after that scope has returned.")
    yield define("Closure", "the combination of a function and its **lexical environment**. Every JavaScript function is a closure; it becomes interesting when the function outlives the scope it was defined in.")
    yield section("The basic example", "code")
    yield snippet("js", '''
        function makeCounter() {
          let count = 0;               // private: only the returned functions can see it
          return {
            increment: () => ++count,
            decrement: () => --count,
            value: () => count,
          };
        }
        const a = makeCounter();
        const b = makeCounter();       // independent environment
        a.increment(); a.increment(); a.increment();
        b.decrement();
        console.log(a.value(), b.value(), a.count);
    ''', out="3 -1 undefined")
    yield section("What closures are used for", "tool")
    yield cards(
        ("Data privacy", "Variables that no outside code can touch — the *module pattern* before classes had `#private`.", "lock"),
        ("Function factories", "`makeMultiplier(3)` returns a function that remembers `3`.", "building-factory"),
        ("Callbacks & handlers", "Event handlers and timers remember the data they were created with.", "click"),
        ("Memoization, once, debounce", "Caches and timers kept between calls.", "database"),
    )
    yield snippet("js", '''
        const makeMultiplier = (factor) => (n) => n * factor;
        const double = makeMultiplier(2), triple = makeMultiplier(3);
        console.log(double(5), triple(5));

        function once(fn) {
          let done = false, result;
          return (...args) => {
            if (!done) { done = true; result = fn(...args); }
            return result;
          };
        }
        const init = once(() => { console.log("initialising…"); return 42; });
        console.log(init(), init());
    ''', out='''
        10 15
        initialising…
        42 42
    ''')
    yield section("Closures capture variables, not values", "variable")
    yield snippet("js", '''
        let message = "first";
        const say = () => message;
        message = "second";
        console.log(say());          // reads the variable's CURRENT value
    ''', out="second")
    yield section("The loop + closure interview classic", "bug")
    yield snippet("js", '''
        for (var i = 1; i <= 3; i++) {
          setTimeout(() => console.log("var:", i), 0);
        }
        for (let j = 1; j <= 3; j++) {
          setTimeout(() => console.log("let:", j), 0);
        }
        // pre-ES6 fix: an IIFE creates a new scope per iteration
        for (var k = 1; k <= 3; k++) {
          ((k) => setTimeout(() => console.log("iife:", k), 0))(k);
        }
    ''', out='''
        var: 4
        var: 4
        var: 4
        let: 1
        let: 2
        let: 3
        iife: 1
        iife: 2
        iife: 3
    ''')
    yield section("Module pattern with an IIFE", "package")
    yield snippet("js", '''
        const bank = (function () {
          let balance = 0;                              // private
          function log(msg) { return `[bank] ${msg}`; } // private
          return {
            deposit(amount) { balance += amount; return log(`+${amount}`); },
            get balance() { return balance; },
          };
        })();
        console.log(bank.deposit(50), bank.balance, bank.log);
    ''', out="[bank] +50 50 undefined")
    yield warn("A closure keeps its **whole** environment reachable. A long-lived closure (event listener, interval, cache) that references a big object keeps that object in memory — a common leak.", "Memory")
    yield qa("What is a closure? Give a practical use.",
             "A function together with references to the variables of the scope it was defined in; it can read and update them even after the outer function returned. Uses: private state (counters, module pattern), function factories, memoization caches, `once`, debounce/throttle, and preserving data in async callbacks.")
    yield qa("Why does the var loop print 4, 4, 4?",
             "`var` is function-scoped, so all three callbacks close over the *same* `i`. The callbacks run after the loop finished, when `i` is 4. `let` creates a new binding for each iteration, so each callback gets its own value.")


@topic(G, "this-binding", "The this Keyword", "pointer")
def _():
    yield lead("`this` is decided by **how a function is called**, not where it is written — except in arrow functions, which borrow it from their surroundings.")
    yield section("The four binding rules (+ arrows)", "list-numbers")
    yield table(
        ["Call style", "`this` is", "Priority"],
        ["`new Fn()`", "The newly created object", "1 (highest)"],
        ["`fn.call(obj)`, `fn.apply(obj)`, `fn.bind(obj)()`", "`obj` (explicit)", "2"],
        ["`obj.method()`", "`obj` (implicit — the object left of the dot)", "3"],
        ["`fn()` plain call", "`undefined` in strict mode, `globalThis` in sloppy mode", "4 (default)"],
        ["Arrow function", "`this` of the enclosing scope — never rebound", "ignores all rules"],
    )
    yield section("Implicit binding and how it is lost", "unlink")
    yield snippet("js", '''
        const user = {
          name: "Asha",
          hello() { return `Hi, I'm ${this?.name}`; },
        };
        console.log(user.hello());          // this = user

        const detached = user.hello;        // just a function now
        console.log(detached());            // plain call → this is undefined (strict)

        const other = { name: "Ravi", hello: user.hello };
        console.log(other.hello());         // this = other
    ''', out='''
        Hi, I'm Asha
        Hi, I'm undefined
        Hi, I'm Ravi
    ''')
    yield note("These examples run as an ES module, which is **always strict**: a plain call gets `this === undefined`. In an old-style sloppy script the same call would get the global object (`window` in browsers) — the source of many silent bugs.", "Strict vs sloppy")
    yield snippet("js", '''
        function strictThis() { return this; }
        const sloppyThis = new Function("return this");   // Function-constructor code is sloppy
        console.log(strictThis());
        console.log(sloppyThis() === globalThis);
        console.log(this);                                  // top level of a module
    ''', out='''
        undefined
        true
        undefined
    ''')
    yield section("Lost `this` in callbacks — and the fixes", "tool")
    yield snippet("js", '''
        class Timer {
          constructor() { this.ticks = 0; }
          startBroken() {
            return [1, 2].map(function () { return this?.ticks; });
          }
          startArrow() {
            return [1, 2].map(() => ++this.ticks);   // arrow: this = the Timer
          }
          startBound() {
            return [1, 2].map(function () { return this.ticks; }.bind(this));
          }
        }
        const t = new Timer();
        console.log(t.startBroken(), t.startArrow(), t.startBound());
    ''', out="[ undefined, undefined ] [ 1, 2 ] [ 2, 2 ]")
    yield section("Arrow functions as methods: a trap", "alert-triangle")
    yield snippet("js", '''
        const counter = {
          count: 10,
          arrow: () => typeof this,          // this of the module scope → undefined
          regular() { return this.count; },
        };
        console.log(counter.arrow(), counter.regular());
    ''', out="undefined 10")
    yield section("`new` binding", "plus")
    yield snippet("js", '''
        function Person(name) {
          this.name = name;      // `this` is the new object
        }
        const p = new Person("Mei");
        console.log(p, p instanceof Person);
    ''', out="Person { name: 'Mei' } true")
    yield qa("How is the value of this determined?",
             "By the call site, in priority order: `new` → the new object; `call`/`apply`/`bind` → the given object; method call `obj.f()` → `obj`; plain call → `undefined` (strict) or the global object (sloppy). Arrow functions have no own `this` and use the enclosing scope's.")
    yield qa("Why does passing obj.method as a callback lose this?",
             "Passing `obj.method` passes only the function value; the callback is later invoked as a plain call with no object before the dot, so `this` becomes `undefined`. Fix with an arrow wrapper `() => obj.method()`, `obj.method.bind(obj)`, or class fields with arrow functions.")


@topic(G, "call-apply-bind", "call, apply & bind", "link")
def _():
    yield lead("Three methods on every function that let you choose `this` explicitly — invoke now (`call`, `apply`) or later (`bind`).")
    yield table(
        ["Method", "Invokes immediately?", "Arguments", "Returns"],
        ["`fn.call(thisArg, a, b)`", "Yes", "Listed one by one", "The function's result"],
        ["`fn.apply(thisArg, [a, b])`", "Yes", "As an array", "The function's result"],
        ["`fn.bind(thisArg, a)`", "No", "Pre-filled (partial application)", "A new bound function"],
    )
    yield snippet("js", '''
        function introduce(greeting, punctuation) {
          return `${greeting}, I'm ${this.name}${punctuation}`;
        }
        const asha = { name: "Asha" };
        console.log(introduce.call(asha, "Hello", "!"));
        console.log(introduce.apply(asha, ["Hi", "."]));
        const boundHey = introduce.bind(asha, "Hey");
        console.log(boundHey("?"));
    ''', out='''
        Hello, I'm Asha!
        Hi, I'm Asha.
        Hey, I'm Asha?
    ''')
    yield section("Classic uses", "tool")
    yield snippet("js", '''
        // borrow array methods for array-likes
        function joinArgs() {
          return Array.prototype.join.call(arguments, "-");
        }
        console.log(joinArgs("a", "b", "c"));

        // apply spreads an array (pre-ES6 alternative to Math.max(...nums))
        console.log(Math.max.apply(null, [3, 7, 2]));

        // partial application with bind
        const multiply = (a, b) => a * b;
        const double = multiply.bind(null, 2);
        console.log(double(21));
    ''', out='''
        a-b-c
        7
        42
    ''')
    yield section("bind is permanent", "lock")
    yield snippet("js", '''
        function whoAmI() { return this.id; }
        const bound = whoAmI.bind({ id: "first" });
        const rebound = bound.bind({ id: "second" });
        console.log(bound(), rebound(), bound.call({ id: "third" }));
        console.log(bound.name);

        const arrow = () => this;
        console.log(arrow.call({ id: 1 }));   // arrows ignore call/apply/bind for this
    ''', out='''
        first first first
        bound whoAmI
        undefined
    ''')
    yield note("`new` beats `bind`: calling a bound function with `new` ignores the bound `this` (but keeps pre-filled arguments).")
    yield qa("What is the difference between call, apply and bind?",
             "All three set `this` explicitly. `call` invokes immediately with arguments listed individually; `apply` invokes immediately with arguments as an array; `bind` doesn't invoke — it returns a new function with `this` (and optionally leading arguments) permanently fixed.")


@topic(G, "higher-order-functions", "Higher-Order Functions & Callbacks", "stack-push")
def _():
    yield lead("A higher-order function takes a function as an argument or returns one. It is the core of functional-style JavaScript.")
    yield define("Higher-order function", "a function that **accepts** a function (a *callback*) and/or **returns** a function. `map`, `filter`, `setTimeout`, `addEventListener` and `bind` are all higher-order.")
    yield section("Taking a function", "arrow-down")
    yield snippet("js", '''
        function repeat(n, action) {
          for (let i = 0; i < n; i++) action(i);
        }
        repeat(3, (i) => console.log("tick", i));

        const applyAll = (value, ...fns) => fns.map((f) => f(value));
        console.log(applyAll(9, Math.sqrt, (x) => x * 2, String));
    ''', out='''
        tick 0
        tick 1
        tick 2
        [ 3, 18, '9' ]
    ''')
    yield section("Returning a function", "arrow-up")
    yield snippet("js", '''
        const greaterThan = (n) => (m) => m > n;
        const isAdult = greaterThan(17);
        console.log([12, 18, 30].filter(isAdult));

        function logged(fn) {
          return function (...args) {
            const result = fn.apply(this, args);
            console.log(`${fn.name}(${args.join(", ")}) = ${result}`);
            return result;
          };
        }
        const add = logged(function add(a, b) { return a + b; });
        add(2, 3);
    ''', out='''
        [ 18, 30 ]
        add(2, 3) = 5
    ''')
    yield section("Synchronous vs asynchronous callbacks", "clock")
    yield snippet("js", '''
        console.log("start");
        [1, 2].forEach((n) => console.log("sync callback", n));   // runs now
        setTimeout(() => console.log("async callback"), 0);        // runs later
        console.log("end");
    ''', out='''
        start
        sync callback 1
        sync callback 2
        end
        async callback
    ''')
    yield section("The `parseInt` trap", "alert-triangle")
    yield snippet("js", '''
        console.log(["1", "2", "3"].map(parseInt));
        console.log(["1", "2", "3"].map(Number));
        console.log(["1", "2", "3"].map((s) => parseInt(s, 10)));
    ''', out='''
        [ 1, NaN, NaN ]
        [ 1, 2, 3 ]
        [ 1, 2, 3 ]
    ''')
    yield warn("`map` calls its callback with `(element, index, array)`. `parseInt` treats the index as the radix: `parseInt('2', 1)` → `NaN`. Wrap callbacks whose extra parameters mean something else.")
    yield qa("What is a callback function?",
             "A function passed as an argument to another function, to be called by it — either synchronously (array methods) or later (timers, events, I/O).")


@topic(G, "iife-recursion-pure", "IIFE, Recursion & Pure Functions", "refresh")
def _():
    yield lead("Three function ideas that show up constantly: run-once scopes, functions that call themselves, and functions with no side effects.")
    yield section("IIFE — Immediately Invoked Function Expression", "player-play")
    yield snippet("js", '''
        const config = (() => {
          const env = "production";            // not visible outside
          return { env, debug: env !== "production" };
        })();
        console.log(config);

        (function named() {
          console.log("runs immediately");
        })();
    ''', out='''
        { env: 'production', debug: false }
        runs immediately
    ''')
    yield note("IIFEs were the pre-module way to avoid polluting the global scope. Today ES modules and block scope cover most uses; you still see them for one-off `async` setup: `(async () => { … })()`.")
    yield section("Recursion", "refresh")
    yield snippet("js", '''
        const factorial = (n) => (n <= 1 ? 1 : n * factorial(n - 1));
        const flatten = (arr) =>
          arr.reduce((acc, x) => (Array.isArray(x) ? acc.concat(flatten(x)) : acc.concat(x)), []);
        function fib(n, memo = {}) {
          if (n <= 1) return n;
          return (memo[n] ??= fib(n - 1, memo) + fib(n - 2, memo));
        }
        console.log(factorial(5), flatten([1, [2, [3, [4]]]]), fib(50));
    ''', out="120 [ 1, 2, 3, 4 ] 12586269025")
    yield warn("There is no practical tail-call optimisation in V8 or SpiderMonkey (only Safari implements it). Deep recursion (≈10k frames) throws `RangeError: Maximum call stack size exceeded` — convert to a loop or an explicit stack.")
    yield section("Pure functions and side effects", "leaf")
    yield cards(
        ("Pure", "Same input → same output, and no side effects (no mutation of arguments/globals, no I/O). Easy to test, cache and reason about.", "circle-check"),
        ("Impure", "Reads or writes outside state: `Math.random()`, `Date.now()`, DOM, network, mutating a parameter.", "circle-x"),
    )
    yield snippet("js", '''
        const addItemImpure = (cart, item) => { cart.push(item); return cart; };
        const addItemPure = (cart, item) => [...cart, item];

        const cart = ["apple"];
        const next = addItemPure(cart, "pear");
        console.log(cart, next);
        addItemImpure(cart, "plum");
        console.log(cart);
    ''', out='''
        [ 'apple' ] [ 'apple', 'pear' ]
        [ 'apple', 'plum' ]
    ''')
    yield qa("What is a pure function and why does it matter?",
             "A function whose output depends only on its inputs and that causes no observable side effects. Pure functions are predictable, trivially testable, safe to memoize and parallelise, and are the basis of React reducers and Redux.")
