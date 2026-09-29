from kit import *

G = "Getting Started"


@topic(G, "intro", "Introduction to JavaScript", "brand-javascript")
def _():
    yield lead("The language of the web — a dynamic, garbage-collected, single-threaded language with first-class functions, now running everywhere from browsers to servers to phones.")
    yield define("JavaScript", "a high-level, dynamically typed, multi-paradigm language (procedural, object-oriented via *prototypes*, functional). Its official specification is **ECMAScript** (ECMA-262); a new edition ships every June.")
    yield section("Why JavaScript?", "bulb")
    yield cards(
        ("The only language browsers run natively", "HTML gives structure, CSS gives style, JavaScript gives behaviour. (WebAssembly runs alongside it, but JS is the glue.)", "browser"),
        ("Runs everywhere", "Servers (Node.js, Deno, Bun), mobile (React Native), desktop (Electron), edge functions, databases (MongoDB shell).", "world"),
        ("First-class functions", "Functions are values: pass them, return them, store them. Closures make callbacks and modules natural.", "function"),
        ("Asynchronous by design", "A single thread plus an event loop handles thousands of concurrent I/O operations without blocking.", "bolt"),
    )
    yield section("A short history", "history")
    yield table(
        ["Year", "Milestone"],
        ["1995", "Brendan Eich writes it in ~10 days at Netscape (Mocha → LiveScript → JavaScript)."],
        ["1997", "Standardised as **ECMAScript 1** by Ecma International."],
        ["2009", "**ES5**: strict mode, `JSON`, `Array.prototype.map/filter/reduce`. Node.js is released."],
        ["2015", "**ES6 / ES2015** — the big one: `let`/`const`, arrows, classes, modules, promises, destructuring, `Map`/`Set`."],
        ["2016 →", "Yearly editions: `async`/`await` (2017), `?.` and `??` (2020), top-level `await` (2022), `toSorted` (2023), `Object.groupBy` (2024)…"],
    )
    yield note("*JavaScript* has nothing to do with *Java* — the name was a 1995 marketing decision. ECMAScript is the spec; JavaScript is the most famous implementation of it.", "Name")
    yield section("Engines and runtimes", "engine")
    yield p("An **engine** parses and executes JavaScript. A **runtime** wraps an engine and adds APIs to talk to the outside world (DOM, files, network, timers).")
    yield table(
        ["Engine", "Used by"],
        ["**V8** (C++)", "Chrome, Edge, Node.js, Deno, Electron"],
        ["**SpiderMonkey**", "Firefox (the first JS engine ever)"],
        ["**JavaScriptCore**", "Safari, Bun, React Native (with Hermes as an alternative)"],
    )
    yield table(
        ["Runtime", "Extra APIs it provides"],
        ["Browser", "`window`, `document` (DOM), `fetch`, `localStorage`, `setTimeout`, events"],
        ["Node.js", "`fs`, `path`, `process`, `http`, `Buffer`, `EventEmitter`, CommonJS + ESM modules"],
        ["Deno / Bun", "Node-compatible APIs, built-in TypeScript, secure-by-default (Deno)"],
    )
    yield warn("`setTimeout`, `console` and `fetch` are **not part of the language** — they come from the runtime. The ECMAScript spec itself has no I/O at all.")
    yield section("Your first program", "code")
    yield snippet("js", '''
        const language = "JavaScript";
        const year = 1995;
        console.log(`Hello, ${language}! Born in ${year}.`);
        console.log(typeof language, typeof year);
        console.log([1, 2, 3].map((n) => n * 2));
    ''', out='''
        Hello, JavaScript! Born in 1995.
        string number
        [ 2, 4, 6 ]
    ''')
    yield shell('''
        $ node --version            # check Node
        $ node app.js               # run a file
        $ node                      # interactive REPL (.exit to quit)
        $ node --watch app.js       # re-run on every save
    ''')
    yield p("In a browser, open DevTools (F12) → **Console** and type expressions directly, or load a file with `<script src=\"app.js\" defer></script>`.")
    yield note("All examples in these notes run on **Node 24** as an ES module (`main.mjs`) and show their real output. ES modules are always in *strict mode* — this matters for `this` and a few other rules, and is pointed out where relevant.", "About the examples")


@topic(G, "how-js-runs", "How JavaScript Runs", "cpu")
def _():
    yield lead("Source text → tokens → AST → bytecode → optimised machine code. One call stack, one heap, and an event loop that feeds it work.")
    yield section("The pipeline inside V8", "route")
    yield flow("Source code", "Parser → AST", "Ignition (bytecode)", "TurboFan (optimised machine code)")
    yield steps(
        ("Parse", "The source is tokenised and turned into an **Abstract Syntax Tree**. Syntax errors are found here — before a single line runs."),
        ("Interpret", "The **Ignition** interpreter compiles the AST to compact bytecode and starts running it immediately (fast startup)."),
        ("Profile", "While running, the engine records which functions are *hot* and which types they see."),
        ("Optimise (JIT)", "Hot functions are compiled by **TurboFan** (and the mid-tier Maglev) into machine code specialised for the observed types."),
        ("Deoptimise", "If an assumption breaks (a function that always saw numbers suddenly gets a string), the engine throws the optimised code away and falls back to bytecode."),
    )
    yield define("JIT (Just-In-Time) compilation", "compiling code to machine code *while the program runs*, using runtime type feedback — so JavaScript is neither purely interpreted nor ahead-of-time compiled.")
    yield note("Write *monomorphic* code: keep the same object shapes and argument types in hot paths. Mixing types in one function (`add(1, 2)` then `add('a', 'b')`) makes it polymorphic and slower.", "Performance tip")
    yield section("Memory: stack and heap", "stack-2")
    yield cards(
        ("Call stack", "A LIFO stack of **execution contexts** — one frame per running function call, holding its local variables and where to return to.", "stack"),
        ("Heap", "A large unstructured region where objects, arrays and closures live. Managed automatically by the **garbage collector**.", "database"),
    )
    yield section("Execution contexts", "box")
    yield p("Every time code runs it gets an **execution context**. There is one *global* context, plus one new context per function call. Each context is created in two phases:")
    yield table(
        ["Phase", "What happens"],
        ["**Creation** (memory)", "Scope is set up; `var` names are created as `undefined`, function declarations are stored in full, `let`/`const`/`class` names are created but *uninitialised* (TDZ). `this` is determined."],
        ["**Execution**", "Code runs line by line; assignments fill in the values."],
    )
    yield section("The call stack in action", "stack")
    yield snippet("js", '''
        function third() {
          console.log("3. in third — stack: global → first → second → third");
        }
        function second() {
          console.log("2. in second");
          third();
          console.log("4. back in second");
        }
        function first() {
          console.log("1. in first");
          second();
          console.log("5. back in first");
        }
        first();
    ''', out='''
        1. in first
        2. in second
        3. in third — stack: global → first → second → third
        4. back in second
        5. back in first
    ''')
    yield p("If functions call each other without end, the stack overflows:")
    yield snippet("js", '''
        function forever(n) {
          return forever(n + 1);
        }
        try {
          forever(0);
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
    ''', out="RangeError: Maximum call stack size exceeded")
    yield section("Single-threaded, yet non-blocking", "bolt")
    yield p("JavaScript runs your code on **one thread**. Slow work (network, disk, timers) is handed to the runtime; when it finishes, a callback is queued and the **event loop** pushes it onto the stack once the stack is empty. See *The Event Loop* topic for the full picture.")
    yield flow("Call stack", "Runtime APIs (timers, I/O)", "Task queues", "Event loop → back to stack")
    yield qa("Is JavaScript interpreted or compiled?",
             "Both. Modern engines parse to bytecode and interpret it for fast startup, then JIT-compile hot functions to optimised machine code using runtime type feedback — and can deoptimise if assumptions break.")
    yield qa("What is an execution context?",
             "The environment a piece of code runs in: its variable environment (scope), the outer-scope reference (scope chain), and the value of `this`. A global context is created first, then one per function call, pushed onto the call stack.")


@topic(G, "variables", "Variables: var, let & const", "variable")
def _():
    yield lead("`const` by default, `let` when you must reassign, `var` never — and know *why*: scope, hoisting and the temporal dead zone.")
    yield section("The three declarations", "table")
    yield table(
        ["", "`var`", "`let`", "`const`"],
        ["Scope", "Function", "Block `{ }`", "Block `{ }`"],
        ["Hoisted?", "Yes, initialised to `undefined`", "Yes, but uninitialised (TDZ)", "Yes, but uninitialised (TDZ)"],
        ["Re-declare in same scope", "Allowed", "SyntaxError", "SyntaxError"],
        ["Reassign", "Yes", "Yes", "No — TypeError"],
        ["Creates `globalThis` property (scripts)", "Yes", "No", "No"],
    )
    yield section("Block scope vs function scope", "brackets-contain")
    yield snippet("js", '''
        function demo() {
          if (true) {
            var a = "var leaks out of the block";
            let b = "let stays inside";
          }
          console.log(a);
          console.log(typeof b);
        }
        demo();
    ''', out='''
        var leaks out of the block
        undefined
    ''')
    yield section("`const` means constant *binding*, not immutable value", "lock")
    yield snippet("js", '''
        const user = { name: "Asha" };
        user.name = "Ravi";          // fine: mutating the object
        user.age = 30;               // fine
        console.log(user);
        try {
          user = {};                 // not fine: rebinding the name
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
    ''', out='''
        { name: 'Ravi', age: 30 }
        TypeError: Assignment to constant variable.
    ''')
    yield note("To make the *object* itself read-only, use `Object.freeze(user)` (shallow).")
    yield section("Hoisting and the Temporal Dead Zone", "clock-pause")
    yield define("Temporal Dead Zone (TDZ)", "the period from the start of a block until a `let`/`const`/`class` declaration is evaluated. Touching the name in that window throws a `ReferenceError`.")
    yield snippet("js", '''
        console.log(x);        // var is hoisted and set to undefined
        var x = 5;

        try {
          console.log(y);      // y exists but is in the TDZ
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
        let y = 10;
    ''', out='''
        undefined
        ReferenceError: Cannot access 'y' before initialization
    ''')
    yield p("The TDZ is *temporal* (about time, not position): a function that reads the variable is fine as long as it is *called* after the declaration runs.")
    yield snippet("js", '''
        function read() { return value; }  // refers to value declared below
        let value = 42;
        console.log(read());               // called after initialisation → OK
    ''', out="42")
    yield section("The classic loop bug", "bug")
    yield snippet("js", '''
        const withVar = [];
        for (var i = 0; i < 3; i++) withVar.push(() => i);
        console.log(withVar.map((f) => f()));

        const withLet = [];
        for (let j = 0; j < 3; j++) withLet.push(() => j);
        console.log(withLet.map((f) => f()));
    ''', out='''
        [ 3, 3, 3 ]
        [ 0, 1, 2 ]
    ''')
    yield p("`var i` is one variable shared by every closure (it is 3 when they run). `let j` creates a **fresh binding per iteration**, so each closure captures its own value.")
    yield section("Naming rules", "writing")
    yield ul(
        "Letters, digits, `_` and `$`; cannot start with a digit; case-sensitive (`name` ≠ `Name`).",
        "Reserved words (`class`, `return`, `new`…) cannot be names.",
        "Conventions: `camelCase` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for true constants.",
    )
    yield dodont("Default to `const`; switch to `let` only when the variable is reassigned. It documents intent and prevents accidental reassignment.",
                 "`var` in new code, and undeclared assignments like `total = 0` (creates an accidental global in sloppy mode, throws in strict mode).")
    yield qa("What is the difference between var, let and const?",
             "`var` is function-scoped, hoisted with value `undefined`, and can be re-declared. `let` and `const` are block-scoped and hoisted into the TDZ (accessing them before the declaration throws). `const` additionally forbids reassignment of the binding — but the object it points to can still be mutated.")
    yield qa("Are let and const hoisted?",
             "Yes — their names are created when the scope is entered (that is why they *shadow* outer variables from the start of the block), but they are not initialised, so any access before the declaration line throws a `ReferenceError`. That window is the temporal dead zone.")


@topic(G, "data-types", "Data Types & typeof", "box")
def _():
    yield lead("Seven primitive types plus objects. Values have types; variables do not.")
    yield section("The eight types", "category")
    yield table(
        ["Type", "Examples", "`typeof`"],
        ["**Number**", "`42`, `3.14`, `-0`, `NaN`, `Infinity`", "`\"number\"`"],
        ["**BigInt**", "`9007199254740993n`", "`\"bigint\"`"],
        ["**String**", "`'hi'`, `\"hi\"`, template literals with backticks", "`\"string\"`"],
        ["**Boolean**", "`true`, `false`", "`\"boolean\"`"],
        ["**Undefined**", "`undefined` — declared but no value", "`\"undefined\"`"],
        ["**Null**", "`null` — intentional “no value”", "`\"object\"` (historic bug!)"],
        ["**Symbol**", "`Symbol('id')` — unique key", "`\"symbol\"`"],
        ["**Object**", "`{}`, `[]`, functions, dates, maps…", "`\"object\"` / `\"function\"`"],
    )
    yield section("`typeof` in practice", "search")
    yield snippet("js", '''
        console.log(typeof 42, typeof 10n, typeof "s", typeof true);
        console.log(typeof undefined, typeof Symbol(), typeof {}, typeof []);
        console.log(typeof null);                 // the famous bug
        console.log(typeof function () {}, typeof class {});
        console.log(typeof notDeclaredAnywhere);  // no ReferenceError
    ''', out='''
        number bigint string boolean
        undefined symbol object object
        object
        function function
        undefined
    ''')
    yield warn("`typeof null === \"object\"` is a bug from JavaScript's first implementation, kept for backward compatibility. Test for null with `value === null`.")
    yield section("Checking types reliably", "checks")
    yield table(
        ["Question", "Use"],
        ["Is it an array?", "`Array.isArray(x)` (not `typeof`)"],
        ["Is it null?", "`x === null`"],
        ["Null or undefined?", "`x == null` (the one accepted use of `==`) or `x ?? fallback`"],
        ["Instance of a class?", "`x instanceof Date` (walks the prototype chain)"],
        ["Exact built-in tag?", "`Object.prototype.toString.call(x)`"],
        ["Is it NaN?", "`Number.isNaN(x)`"],
    )
    yield snippet("js", '''
        const tag = (x) => Object.prototype.toString.call(x);
        console.log(Array.isArray([]), [] instanceof Array);
        console.log(tag(null), tag([]), tag(new Date(0)), tag(/re/));
    ''', out='''
        true true
        [object Null] [object Array] [object Date] [object RegExp]
    ''')
    yield section("`undefined` vs `null`", "circle-off")
    yield cards(
        ("`undefined`", "The engine's “nothing here”: an unassigned variable, a missing property, a missing argument, a function with no `return`.", "question-mark"),
        ("`null`", "The programmer's “nothing here”: an intentional empty value you assign yourself.", "circle-off"),
    )
    yield snippet("js", '''
        let a;
        const obj = {};
        function f() {}
        console.log(a, obj.missing, f());
        console.log(null == undefined, null === undefined);
        console.log(Number(null), Number(undefined));
    ''', out='''
        undefined undefined undefined
        true false
        0 NaN
    ''')
    yield section("Dynamic typing", "arrows-shuffle")
    yield snippet("js", '''
        let value = 10;
        console.log(typeof value);
        value = "ten";
        console.log(typeof value);
        value = [10];
        console.log(typeof value, Array.isArray(value));
    ''', out='''
        number
        string
        object true
    ''')
    yield qa("How many data types does JavaScript have?",
             "Eight: seven primitives (`number`, `bigint`, `string`, `boolean`, `undefined`, `null`, `symbol`) and `object`. Arrays, functions, dates and maps are all objects.")
    yield qa("Why does typeof null return \"object\"?",
             "In the first implementation values carried a type tag, and the tag for objects was 0; `null` was the null pointer (all zeros), so it read as an object. Fixing it would break the web, so it stays.")


@topic(G, "primitives-vs-references", "Primitives vs References", "arrows-exchange")
def _():
    yield lead("Primitives are copied by value; objects are shared by reference. Almost every “why did my data change?” bug comes from this.")
    yield section("Copying a primitive", "copy")
    yield snippet("js", '''
        let a = 10;
        let b = a;     // b gets its own copy of the value
        b = 20;
        console.log(a, b);
    ''', out="10 20")
    yield section("Copying an object reference", "link")
    yield snippet("js", '''
        const original = { score: 10 };
        const alias = original;   // copies the *reference*, not the object
        alias.score = 99;
        console.log(original.score);
        console.log(original === alias);
    ''', out='''
        99
        true
    ''')
    yield table(
        ["", "Primitives", "Objects (incl. arrays, functions)"],
        ["Stored as", "The value itself", "A reference to a heap object"],
        ["Assignment copies", "The value", "The reference"],
        ["`===` compares", "Values", "Identity (same object?)"],
        ["Mutable?", "No — immutable", "Yes"],
    )
    yield section("Equality compares identity for objects", "equal")
    yield snippet("js", '''
        console.log("abc" === "abc");
        console.log({ a: 1 } === { a: 1 });
        console.log([1, 2] === [1, 2]);
        const arr = [1, 2];
        console.log(arr === arr);
    ''', out='''
        true
        false
        false
        true
    ''')
    yield section("Passing to functions: always by value (of the reference)", "arrow-right")
    yield p("JavaScript is **pass-by-value**. For objects the *value* being passed is a reference — so a function can mutate the caller's object, but reassigning the parameter never affects the caller.")
    yield snippet("js", '''
        function mutate(obj) {
          obj.touched = true;   // changes the shared object
        }
        function reassign(obj) {
          obj = { replaced: true };  // only rebinds the local parameter
        }
        const data = {};
        mutate(data);
        reassign(data);
        console.log(data);
    ''', out="{ touched: true }")
    yield section("Primitives are immutable", "lock")
    yield snippet("js", '''
        const s = "hello";
        const upper = s.toUpperCase();   // returns a NEW string
        console.log(s, upper);
        const t = "cat";
        try {
          t[0] = "b";                    // strings can't change in place
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
        console.log(t);
    ''', out='''
        hello HELLO
        TypeError: Cannot assign to read only property '0' of string 'cat'
        cat
    ''')
    yield p("In strict mode (every ES module) the assignment throws; in a sloppy script it is *silently ignored*. Either way the string never changes.")
    yield note("Methods on primitives work because of **autoboxing**: `\"hi\".length` briefly wraps the string in a `String` object, reads the property, and discards the wrapper.", "Autoboxing")
    yield warn("To copy an object, use spread (`{...obj}`, shallow) or `structuredClone(obj)` (deep) — see *Immutability & Copying*.")
    yield qa("Is JavaScript pass-by-reference?",
             "No. It is always pass-by-value; for objects the value is a reference (sometimes called *call by sharing*). Mutating through the parameter is visible to the caller, but reassigning the parameter is not.")
