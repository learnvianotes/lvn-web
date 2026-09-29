from kit import *

G = "Advanced Concepts"


@topic(G, "error-handling", "Error Handling & Custom Errors", "alert-octagon")
def _():
    yield lead("Throw `Error` objects (never strings), catch where you can actually do something about it, and give your own failures meaningful classes.")
    yield section("try / catch / finally", "shield")
    yield snippet("js", '''
        function parseAge(input) {
          const n = Number(input);
          if (!Number.isInteger(n) || n < 0) throw new RangeError(`invalid age: ${input}`);
          return n;
        }
        for (const input of ["42", "-3", "abc"]) {
          try {
            console.log("age", parseAge(input));
          } catch (err) {
            console.log(err.name, "-", err.message);
          } finally {
            console.log("  checked", JSON.stringify(input));
          }
        }
    ''', out='''
        age 42
          checked "42"
        RangeError - invalid age: -3
          checked "-3"
        RangeError - invalid age: abc
          checked "abc"
    ''')
    yield section("Built-in error types", "list")
    yield table(
        ["Type", "Thrown when"],
        ["`SyntaxError`", "Code (or `JSON.parse` input) cannot be parsed"],
        ["`ReferenceError`", "An undeclared variable, or a TDZ access"],
        ["`TypeError`", "A value is the wrong type: calling a non-function, reading a property of `undefined`, writing a read-only property"],
        ["`RangeError`", "A number out of range: `new Array(-1)`, `toFixed(200)`, stack overflow"],
        ["`URIError`", "`decodeURIComponent('%')`"],
        ["`AggregateError`", "Several errors at once (`Promise.any`)"],
        ["`EvalError`", "Legacy, practically unused"],
    )
    yield snippet("js", '''
        const attempts = [
          () => null.name,
          () => undefinedVariable,
          () => (1).toFixed(500),
          () => decodeURIComponent("%"),
          () => JSON.parse("{bad json}"),
        ];
        for (const fn of attempts) {
          try { fn(); } catch (e) { console.log(`${e.name}: ${e.message}`); }
        }
    ''', out='''
        TypeError: Cannot read properties of null (reading 'name')
        ReferenceError: undefinedVariable is not defined
        RangeError: toFixed() digits argument must be between 0 and 100
        URIError: URI malformed
        SyntaxError: Expected property name or '}' in JSON at position 1 (line 1 column 2)
    ''')
    yield section("Custom error classes", "hierarchy")
    yield snippet("js", '''
        class AppError extends Error {
          constructor(message, options) {
            super(message, options);            // options.cause (ES2022)
            this.name = this.constructor.name;
          }
        }
        class NotFoundError extends AppError {
          constructor(resource, id) {
            super(`${resource} ${id} not found`);
            this.status = 404;
          }
        }
        class DatabaseError extends AppError {}

        function findUser(id) {
          try {
            throw new Error("connection reset");        // low-level failure
          } catch (cause) {
            throw new DatabaseError(`could not load user ${id}`, { cause });
          }
        }
        try {
          findUser(7);
        } catch (e) {
          console.log(e.name, "|", e.message, "|", e.cause.message);
          console.log(e instanceof DatabaseError, e instanceof AppError, e instanceof Error);
        }
        const nf = new NotFoundError("Order", 42);
        console.log(nf.name, nf.status, nf.message);
    ''', out='''
        DatabaseError | could not load user 7 | connection reset
        true true true
        NotFoundError 404 Order 42 not found
    ''')
    yield good("Wrap low-level errors with `{ cause }` so logs keep the whole story; branch on `instanceof` (or an error `code`), not on message text.")
    yield section("Uncaught errors", "bomb")
    yield p("An exception nobody catches ends the script (in Node the process exits with code 1). The build confirms this example really fails:")
    yield snippet("js", '''
        function divide(a, b) {
          if (b === 0) throw new Error("Division by zero");
          return a / b;
        }
        console.log(divide(10, 2));
        console.log(divide(1, 0));   // uncaught → crash
        console.log("never reached");
    ''', fails=True)
    yield output('''
        5
        file:///…/main.mjs:2
          if (b === 0) throw new Error("Division by zero");
                             ^

        Error: Division by zero
            at divide (file:///…/main.mjs:2:22)
            at file:///…/main.mjs:6:13

        Node.js v24.12.0
    ''', "Terminal (stack trimmed) — exit code 1")
    yield section("Async errors", "clock-exclamation")
    yield snippet("js", '''
        try {
          setTimeout(() => { /* throw here would NOT be caught below */ }, 0);
        } catch {
          console.log("never");
        }
        async function load() { throw new Error("async failure"); }
        try {
          await load();                              // await makes try/catch work
        } catch (e) {
          console.log("caught:", e.message);
        }
        load().catch((e) => console.log("caught via .catch:", e.message));
    ''', out='''
        caught: async failure
        caught via .catch: async failure
    ''')
    yield table(
        ["Safety net", "Environment"],
        ["`window.addEventListener('error', …)`", "Browser: uncaught sync errors"],
        ["`window.addEventListener('unhandledrejection', …)`", "Browser: rejected promises without a handler"],
        ["`process.on('uncaughtException')` / `('unhandledRejection')`", "Node: log and exit — don't keep running in an unknown state"],
    )
    yield dodont("Throw `Error` instances (they capture a stack trace); catch narrowly and rethrow what you can't handle; always handle promise rejections.",
                 "`throw \"oops\"` (no stack), empty `catch {}` blocks that swallow failures, and using exceptions for ordinary control flow.")
    yield qa("Can try/catch catch errors thrown inside a setTimeout callback?",
             "No. By the time the callback runs, the `try` block has long finished — it is a different call stack. Put the `try/catch` inside the callback, or use promises with `await`/`.catch`.")
    yield qa("What does finally do if both try and finally return?",
             "`finally` always runs; if it has its own `return` (or `throw`), that overrides the result of `try`/`catch`. Avoid returning from `finally`.")


@topic(G, "modules", "Modules: ESM vs CommonJS", "packages")
def _():
    yield lead("Modules give each file its own scope and explicit imports/exports. JavaScript has two systems: standard **ES modules** and Node's older **CommonJS**.")
    yield section("ES module syntax", "file-export")
    yield snippet("js", '''
        // math.js
        export const PI = 3.14159;
        export function area(r) { return PI * r * r; }
        export default class Calculator { /* ... */ }

        // app.js
        import Calculator, { PI, area as circleArea } from "./math.js";
        import * as math from "./math.js";
        export { circleArea };                    // re-export
        export * from "./other.js";
        const { heavy } = await import("./heavy.js");   // dynamic import (returns a promise)
    ''', run=False)
    yield p("Exports are *live bindings*, which a runnable demo can show by importing an inline module from a `data:` URL:")
    yield snippet("js", '''
        const source = `
          export let count = 0;
          export function increment() { count++; }
          export default "the default export";
        `;
        const mod = await import("data:text/javascript," + encodeURIComponent(source));
        console.log(mod.default, mod.count);
        mod.increment();
        console.log(mod.count);                   // live binding: sees the update
        try {
          mod.count = 99;                         // importers cannot assign
        } catch (e) {
          console.log(e.name);
        }
        console.log(Object.keys(mod));
    ''', out='''
        the default export 0
        1
        TypeError
        [ 'count', 'default', 'increment' ]
    ''')
    yield section("ESM vs CommonJS", "scale")
    yield table(
        ["", "ES modules (ESM)", "CommonJS (CJS)"],
        ["Syntax", "`import` / `export`", "`require()` / `module.exports`"],
        ["Loading", "Static graph, parsed before running; async-capable", "Synchronous, at runtime"],
        ["Top-level `await`", "Yes", "No"],
        ["Bindings", "Live, read-only", "A copied value (`exports` object)"],
        ["Strict mode", "Always", "Only with `\"use strict\"`"],
        ["Top-level `this`", "`undefined`", "`module.exports`"],
        ["File detection in Node", "`.mjs`, or `.js` with `\"type\": \"module\"`", "`.cjs`, or `.js` by default"],
        ["`__dirname`, `require`", "Not defined — use `import.meta.dirname`, `createRequire`", "Available"],
        ["Tree-shaking", "Yes (static analysis)", "Hard"],
    )
    yield snippet("js", '''
        import { createRequire } from "node:module";
        import path from "node:path";

        const require = createRequire(import.meta.url);     // CJS require inside ESM
        const os = require("node:os");
        console.log(typeof os.platform, typeof require.resolve);
        console.log(path.basename(import.meta.filename), import.meta.url.startsWith("file://"));
        console.log(typeof __dirname, typeof module, this);
    ''', out='''
        function function
        main.mjs true
        undefined undefined undefined
    ''')
    yield section("CommonJS for reference", "file-code")
    yield snippet("js", '''
        // counter.cjs
        let count = 0;
        module.exports = { count, increment() { count++; } };

        // app.cjs
        const counter = require("./counter.cjs");
        counter.increment();
        console.log(counter.count);   // 0 — a copy was exported, not a live binding
    ''', run=False)
    yield section("Module facts worth knowing", "bulb")
    yield ul(
        "A module is evaluated **once**, then cached — every importer gets the same instance (natural singletons).",
        "Imports are hoisted and resolved before the module body runs; circular imports see TDZ bindings until the other module finishes.",
        "In browsers: `<script type=\"module\">` is deferred by default, runs in strict mode and needs full URLs or an import map.",
        "Dynamic `import()` enables code splitting and lazy loading; it works in CJS too.",
        "`require(esm)` is supported in modern Node (22+) for ES modules without top-level `await`.",
    )
    yield qa("What are the main differences between CommonJS and ES modules?",
             "ESM uses static `import`/`export`, is analysed before execution (enabling tree-shaking and top-level await), exports live read-only bindings and is always strict. CJS uses synchronous runtime `require`, exports a plain object (copied values), and has `__dirname`/`module`.")


@topic(G, "functional-patterns", "Currying, Composition & Memoization", "math-function")
def _():
    yield lead("Functional techniques built from closures and higher-order functions — and staple interview implementations.")
    yield section("Currying", "arrow-right")
    yield define("Currying", "transforming `f(a, b, c)` into `f(a)(b)(c)` — a chain of single-argument functions. *Partial application* is the looser idea of fixing some arguments now and the rest later.")
    yield snippet("js", '''
        function curry(fn) {
          return function curried(...args) {
            return args.length >= fn.length
              ? fn.apply(this, args)
              : (...more) => curried.apply(this, [...args, ...more]);
          };
        }
        const volume = (l, w, h) => l * w * h;
        const cv = curry(volume);
        console.log(cv(2)(3)(4), cv(2, 3)(4), cv(2)(3, 4), cv(2, 3, 4));

        const log = curry((level, scope, msg) => `[${level}] ${scope}: ${msg}`);
        const warnDb = log("WARN")("db");
        console.log(warnDb("slow query"));
    ''', out='''
        24 24 24 24
        [WARN] db: slow query
    ''')
    yield section("Infinite currying: sum(1)(2)(3)()", "infinity")
    yield snippet("js", '''
        const sum = (a) => (b) => (b === undefined ? a : sum(a + b));
        console.log(sum(1)(2)(3)(4)());
    ''', out="10")
    yield section("Composition and pipe", "arrows-right")
    yield snippet("js", '''
        const compose = (...fns) => (x) => fns.reduceRight((acc, f) => f(acc), x);
        const pipe = (...fns) => (x) => fns.reduce((acc, f) => f(acc), x);

        const trim = (s) => s.trim();
        const lower = (s) => s.toLowerCase();
        const slugify = (s) => s.replace(/\\s+/g, "-");

        console.log(pipe(trim, lower, slugify)("  Hello Big World "));
        console.log(compose(slugify, lower, trim)("  Hello Big World "));
    ''', out='''
        hello-big-world
        hello-big-world
    ''')
    yield note("`pipe` runs left → right (reads like a recipe); `compose` right → left (mirrors maths: `f(g(x))`).")
    yield section("Memoization", "database")
    yield snippet("js", '''
        function memoize(fn, keyFn = (...args) => JSON.stringify(args)) {
          const cache = new Map();
          return function (...args) {
            const key = keyFn(...args);
            if (cache.has(key)) return cache.get(key);
            const result = fn.apply(this, args);
            cache.set(key, result);
            return result;
          };
        }
        let calls = 0;
        const slowSquare = (n) => { calls++; return n * n; };
        const fastSquare = memoize(slowSquare);
        console.log(fastSquare(9), fastSquare(9), fastSquare(3), "calls:", calls);

        const fib = memoize((n) => (n < 2 ? n : fib(n - 1) + fib(n - 2)));
        console.log(fib(90));
    ''', out='''
        81 81 9 calls: 2
        2880067194370816000
    ''')
    yield warn("Memoize only **pure** functions. An unbounded cache is a memory leak — cap it (LRU) or key it with a `WeakMap` when arguments are objects.")
    yield section("once, partial and friends", "tool")
    yield snippet("js", '''
        const partial = (fn, ...preset) => (...later) => fn(...preset, ...later);
        const greet = (greeting, name) => `${greeting}, ${name}!`;
        console.log(partial(greet, "Welcome")("Mei"));

        const not = (pred) => (...args) => !pred(...args);
        const isEven = (n) => n % 2 === 0;
        console.log([1, 2, 3, 4].filter(not(isEven)));

        const tap = (fn) => (x) => { fn(x); return x; };
        console.log([1, 2].map(tap((x) => console.log("saw", x))));
    ''', out='''
        Welcome, Mei!
        [ 1, 3 ]
        saw 1
        saw 2
        [ 1, 2 ]
    ''')
    yield qa("Implement a curry function.",
             "Return a function that collects arguments; when it has at least `fn.length` of them, call `fn`, otherwise return another function that appends further arguments (see the implementation above).")
    yield qa("What is memoization?",
             "Caching a function's results keyed by its arguments so repeated calls with the same input return instantly. It trades memory for speed and is only correct for pure functions.")


@topic(G, "debounce-throttle", "Debounce & Throttle", "hand-stop")
def _():
    yield lead("Two ways to rate-limit a function that fires too often (typing, scrolling, resizing): **debounce** waits for quiet, **throttle** runs at most once per interval.")
    yield cards(
        ("Debounce", "Run only after the calls have **stopped** for `wait` ms. Every new call resets the timer. → search-as-you-type, auto-save, resize end.", "player-pause"),
        ("Throttle", "Run at most **once every** `wait` ms, no matter how often it is called. → scroll position, mouse move, rate-limited APIs.", "gauge"),
    )
    yield section("Debounce", "code")
    yield snippet("js", '''
        function debounce(fn, wait) {
          let timer;
          return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), wait);
          };
        }

        const search = debounce((q) => console.log("searching for:", q), 30);
        search("j");
        search("ja");
        search("jav");                          // only this one survives the burst
        setTimeout(() => search("javascript"), 60);
    ''', out='''
        searching for: jav
        searching for: javascript
    ''')
    yield section("Throttle", "code")
    yield snippet("js", '''
        function throttle(fn, wait) {
          let last = 0, timer = null, pendingArgs = null;
          return function (...args) {
            const now = Date.now();
            const remaining = wait - (now - last);
            if (remaining <= 0) {               // leading call
              last = now;
              fn.apply(this, args);
            } else {                            // remember the latest call for the trailing edge
              pendingArgs = args;
              timer ??= setTimeout(() => {
                last = Date.now();
                timer = null;
                fn.apply(this, pendingArgs);
              }, remaining);
            }
          };
        }

        const onScroll = throttle((y) => console.log("handle scroll at", y), 50);
        onScroll(0);                  // runs immediately (leading edge)
        onScroll(10);                 // ignored…
        onScroll(20);                 // …but the latest is kept for the trailing edge
    ''', out='''
        handle scroll at 0
        handle scroll at 20
    ''')
    yield table(
        ["", "Debounce", "Throttle"],
        ["Runs", "Once, after the burst ends", "Regularly during the burst"],
        ["Guarantee", "Latest value, eventually", "At most one call per `wait`"],
        ["Typical use", "Search box, validation, auto-save", "Scroll, resize, drag, analytics"],
    )
    yield note("Production versions (lodash `debounce`/`throttle`) add `leading`/`trailing` options, `cancel()` and `flush()`. Remember to cancel pending timers when a component unmounts.")
    yield qa("Debounce vs throttle?",
             "Debounce delays execution until calls stop for a quiet period (only the last call runs). Throttle lets a call through at most once per interval, spreading executions evenly while calls continue.")


@topic(G, "proxy-reflect", "Proxy & Reflect", "arrow-guide")
def _():
    yield lead("A `Proxy` wraps an object and intercepts fundamental operations — get, set, delete, `in`, function calls. `Reflect` provides the default behaviour for each trap.")
    yield section("Traps", "list")
    yield table(
        ["Trap", "Intercepts"],
        ["`get(target, prop, receiver)`", "`obj.prop`, `obj[prop]`"],
        ["`set(target, prop, value, receiver)`", "`obj.prop = value`"],
        ["`has(target, prop)`", "`prop in obj`"],
        ["`deleteProperty(target, prop)`", "`delete obj.prop`"],
        ["`ownKeys(target)`", "`Object.keys`, `for…in`, `Reflect.ownKeys`"],
        ["`apply(target, thisArg, args)`", "Calling a function proxy"],
        ["`construct(target, args)`", "`new` on a proxy"],
    )
    yield section("Validation and defaults", "shield-check")
    yield snippet("js", '''
        const user = new Proxy({}, {
          set(target, prop, value, receiver) {
            if (prop === "age" && (!Number.isInteger(value) || value < 0)) {
              throw new TypeError(`age must be a non-negative integer, got ${value}`);
            }
            return Reflect.set(target, prop, value, receiver);   // default behaviour
          },
          get(target, prop, receiver) {
            return prop in target ? Reflect.get(target, prop, receiver) : `<no ${String(prop)}>`;
          },
        });
        user.name = "Asha";
        user.age = 30;
        try { user.age = -5; } catch (e) { console.log(e.message); }
        console.log(user.name, user.age, user.email);
    ''', out='''
        age must be a non-negative integer, got -5
        Asha 30 <no email>
    ''')
    yield section("Observing changes (how Vue 3 reactivity works)", "eye")
    yield snippet("js", '''
        function reactive(obj, onChange) {
          return new Proxy(obj, {
            set(target, prop, value) {
              const old = target[prop];
              const ok = Reflect.set(target, prop, value);
              if (old !== value) onChange(prop, old, value);
              return ok;
            },
          });
        }
        const state = reactive({ count: 0 }, (k, a, b) => console.log(`${k}: ${a} → ${b}`));
        state.count++;
        state.count += 5;
        state.count = 6;          // unchanged → no notification
    ''', out='''
        count: 0 → 1
        count: 1 → 6
    ''')
    yield section("Negative array indices, and hiding private keys", "eye-off")
    yield snippet("js", '''
        const arr = new Proxy([10, 20, 30], {
          get(target, prop, receiver) {
            const i = Number(prop);
            return Number.isInteger(i) && i < 0 ? target[target.length + i] : Reflect.get(target, prop, receiver);
          },
        });
        console.log(arr[-1], arr[0], arr.length);

        const hidden = new Proxy({ id: 1, _secret: "x" }, {
          has: (t, p) => !String(p).startsWith("_") && p in t,
          ownKeys: (t) => Reflect.ownKeys(t).filter((k) => !String(k).startsWith("_")),
        });
        console.log("_secret" in hidden, Object.keys(hidden));
    ''', out='''
        30 10 3
        false [ 'id' ]
    ''')
    yield section("Reflect", "arrows-left-right")
    yield snippet("js", '''
        const obj = { a: 1 };
        console.log(Reflect.has(obj, "a"), Reflect.ownKeys(obj), Reflect.get(obj, "a"));
        console.log(Reflect.defineProperty(Object.freeze({}), "x", { value: 1 }));   // false, no throw
        console.log(Reflect.apply(Math.max, null, [1, 5, 3]));
    ''', out='''
        true [ 'a' ] 1
        false
        5
    ''')
    yield note("`Reflect` methods mirror the proxy traps one-to-one and return booleans instead of throwing. Inside a trap, forward to `Reflect.x(...)` with the same arguments (including `receiver`) to keep getters and inheritance working.")
    yield warn("Proxies add overhead to every intercepted operation, and `===` sees the proxy and target as different objects. Built-ins with internal slots (`Map`, `Date`, `#private` fields) don't work transparently through a proxy.")
    yield qa("What are real-world uses of Proxy?",
             "Reactivity systems (Vue 3, MobX), validation, default values, logging/tracing, access control, negative indexing, API clients that turn property access into requests, and mocks in tests.")


@topic(G, "memory-gc", "Garbage Collection & Memory Leaks", "recycle")
def _():
    yield lead("JavaScript frees memory automatically once objects become unreachable. Leaks happen when you *accidentally keep them reachable*.")
    yield section("Reachability", "route")
    yield p("The collector starts from **roots** — globals, the current call stack, active closures, pending callbacks — and marks everything reachable from them. Anything not marked is garbage, even if it points to other garbage (so cycles are fine).")
    yield steps(
        ("Mark", "Traverse from the roots and mark every reachable object."),
        ("Sweep / compact", "Reclaim unmarked memory; optionally move live objects together."),
    )
    yield cards(
        ("Young generation", "New objects are allocated here. Most die young, so it is collected often and cheaply (*scavenge*).", "baby-carriage"),
        ("Old generation", "Objects that survive a few collections are promoted. Collected less often with incremental / concurrent mark-sweep-compact.", "old"),
    )
    yield note("V8's collector (*Orinoco*) is generational, incremental and mostly concurrent, keeping pauses short. You cannot trigger GC from normal code (`node --expose-gc` gives `global.gc()` for experiments).")
    yield section("Common leaks", "droplet")
    yield table(
        ["Leak", "Why it stays reachable", "Fix"],
        ["Forgotten timers", "`setInterval` callback (and everything it closes over) is referenced by the timer", "`clearInterval` on cleanup"],
        ["Event listeners", "Listener closures on long-lived targets (window, document, emitters)", "`removeEventListener`, `{ signal }`, `{ once: true }`"],
        ["Unbounded caches / Maps", "Keys and values are held strongly forever", "LRU limit, `WeakMap`, TTL"],
        ["Closures capturing big data", "A small long-lived function keeps a huge outer variable alive", "Copy only what's needed; null out references"],
        ["Detached DOM nodes", "Removed from the page but still referenced from JS", "Drop references; use `WeakMap` for per-node data"],
        ["Accidental globals", "Sloppy-mode `x = …` creates a global root", "Strict mode / modules"],
    )
    yield snippet("js", '''
        import { EventEmitter } from "node:events";
        const bus = new EventEmitter();

        function subscribeLeaky() {
          const bigBuffer = new Array(1e5).fill("*");      // captured by the listener below
          bus.on("tick", () => bigBuffer.length);
        }
        for (let i = 0; i < 3; i++) subscribeLeaky();
        console.log("listeners after 3 leaky subscribes:", bus.listenerCount("tick"));

        function subscribeClean(signal) {
          const handler = () => {};
          bus.on("tock", handler);
          signal.addEventListener("abort", () => bus.off("tock", handler));
        }
        const ac = new AbortController();
        subscribeClean(ac.signal);
        ac.abort();                                       // component unmounted
        console.log("listeners after cleanup:", bus.listenerCount("tock"));
    ''', out='''
        listeners after 3 leaky subscribes: 3
        listeners after cleanup: 0
    ''')
    yield section("Measuring", "chart-line")
    yield snippet("js", '''
        const before = process.memoryUsage().heapUsed;
        let data = Array.from({ length: 200_000 }, (_, i) => ({ i }));
        const during = process.memoryUsage().heapUsed;
        console.log("grew by more than 5 MB:", during - before > 5 * 1024 * 1024);
        data = null;   // now unreachable — eligible for collection
    ''', out="grew by more than 5 MB: true")
    yield ul(
        "Browser: DevTools → **Memory** → heap snapshots (compare two) and the allocation timeline; look for growing *Detached* elements.",
        "Node: `process.memoryUsage()`, `node --inspect` + Chrome DevTools, `--heapsnapshot-signal`, `v8.writeHeapSnapshot()`.",
    )
    yield qa("How does garbage collection work in JavaScript?",
             "Engines use tracing mark-and-sweep: starting from roots (globals, stack, closures) they mark reachable objects and reclaim the rest. V8 is generational — frequent cheap collection of the young generation, rarer mark-compact of the old — and does much of the work incrementally and concurrently.")
    yield qa("Can circular references cause memory leaks?",
             "Not with mark-and-sweep: a cycle that is unreachable from the roots is collected. (They did leak with old reference-counting collectors, e.g. IE6 DOM/JS cycles.)")


@topic(G, "strict-mode", "Strict Mode", "shield-lock")
def _():
    yield lead("`\"use strict\"` opts a script or function into a safer dialect that turns silent mistakes into errors. ES modules and class bodies are strict automatically.")
    yield section("Turning it on", "toggle-right")
    yield snippet("js", '''
        "use strict";            // first statement of a script
        function f() {
          "use strict";          // or of a single function
        }
    ''', run=False)
    yield p("You rarely write it today: **every ES module** (`import`/`export`, `.mjs`, `type=\"module\"`) and **every `class` body** is strict whether or not the directive is present. Old-style scripts and CommonJS files are *sloppy* unless you opt in.")
    yield section("What changes", "list-details")
    yield table(
        ["Situation", "Sloppy mode", "Strict mode"],
        ["Assign to undeclared variable", "Creates a global", "`ReferenceError`"],
        ["`this` in a plain function call", "`globalThis`", "`undefined`"],
        ["Write to read-only / getter-only property", "Silently ignored", "`TypeError`"],
        ["Add property to frozen / non-extensible object", "Silently ignored", "`TypeError`"],
        ["`delete` a non-configurable property", "Returns `false`", "`TypeError`"],
        ["Duplicate parameter names", "Allowed", "`SyntaxError`"],
        ["`with` statement", "Allowed", "`SyntaxError`"],
        ["Octal literal `010`", "8", "`SyntaxError` (use `0o10`)"],
        ["`arguments` ↔ parameters", "Linked (aliasing)", "Independent"],
        ["`eval` creates variables in the caller", "Yes", "No — own scope"],
        ["Reserved future words (`let`, `static`, `implements`…)", "Usable as names", "Reserved"],
    )
    yield section("Seeing both modes side by side", "code")
    yield p("This file is a module (strict). Code built with the `Function` constructor is sloppy unless it says otherwise — a handy way to compare:")
    yield snippet("js", '''
        const sloppy = new Function(`
          leaked = 1;                         // becomes a global
          const frozen = Object.freeze({ a: 1 });
          frozen.a = 2;                       // silently ignored
          return [typeof globalThis.leaked, frozen.a, this === globalThis];
        `);
        console.log("sloppy:", sloppy());

        const strict = new Function(`
          "use strict";
          try { leaked2 = 1; } catch (e) { return e.name + " / this=" + this; }
        `);
        console.log("strict:", strict());

        function args(a) { a = 99; return arguments[0]; }       // module → strict
        console.log("arguments unlinked:", args(1));
    ''', out='''
        sloppy: [ 'number', 1, true ]
        strict: ReferenceError / this=undefined
        arguments unlinked: 1
    ''')
    yield qa("What is strict mode and why use it?",
             "An opt-in restricted variant of JavaScript (ES5) that throws on silent errors (undeclared assignments, writes to read-only properties), makes `this` `undefined` in plain calls, forbids confusing features (`with`, duplicate params, octal literals) and enables engine optimisations. It is on by default in modules and classes.")
