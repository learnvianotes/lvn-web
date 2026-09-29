from kit import *

G = "Modern JS & Best Practices"


@topic(G, "es-features", "Modern ES Feature Tour (ES2015 → ES2025)", "sparkles")
def _():
    yield lead("What arrived in each edition since the ES2015 revolution — a map for reading any codebase and for “what's new in JavaScript?” questions.")
    yield table(
        ["Edition", "Headline features"],
        ["**ES2015 (ES6)**", "`let`/`const`, arrows, classes, template literals, destructuring, default/rest/spread, modules, Promise, Map/Set/WeakMap, Symbol, iterators, generators, `for…of`, Proxy/Reflect"],
        ["**ES2016**", "`**` exponent, `Array.prototype.includes`"],
        ["**ES2017**", "`async`/`await`, `Object.values/entries`, `padStart/padEnd`, `Object.getOwnPropertyDescriptors`, SharedArrayBuffer/Atomics"],
        ["**ES2018**", "Object rest/spread, async iteration (`for await`), `Promise.finally`, regex named groups, lookbehind, `s` flag"],
        ["**ES2019**", "`flat`/`flatMap`, `Object.fromEntries`, `trimStart/trimEnd`, optional `catch` binding, stable sort"],
        ["**ES2020**", "`?.`, `??`, BigInt, `Promise.allSettled`, `globalThis`, dynamic `import()`, `matchAll`"],
        ["**ES2021**", "`&&=` `||=` `??=`, `replaceAll`, `Promise.any`, numeric separators `1_000`, WeakRef"],
        ["**ES2022**", "Class fields, `#private`, static blocks, top-level `await`, `.at()`, `Object.hasOwn`, `Error` `cause`, `#x in obj`"],
        ["**ES2023**", "`toSorted/toReversed/toSpliced/with`, `findLast/findLastIndex`, hashbang, symbols as WeakMap keys"],
        ["**ES2024**", "`Object.groupBy`/`Map.groupBy`, `Promise.withResolvers`, `Array.fromAsync`, regex `v` flag, resizable ArrayBuffer, `String.isWellFormed`"],
        ["**ES2025**", "Iterator helpers, new `Set` methods (`union`, `intersection`…), `RegExp.escape`, `Promise.try`, JSON modules / import attributes, `Float16Array`"],
    )
    yield section("A tour in one program", "code")
    yield snippet("js", '''
        const users = [
          { name: "Asha", team: "web", profile: { city: "Pune" }, score: 72 },
          { name: "Ravi", team: "api", profile: null, score: 91 },
          { name: "Mei", team: "web", profile: { city: "Delhi" }, score: 85 },
        ];
        // ES2020 optional chaining + nullish coalescing
        console.log(users.map((u) => u.profile?.city ?? "unknown"));
        // ES2023 non-mutating sort + ES2022 at()
        console.log(users.toSorted((a, b) => b.score - a.score).at(0).name);
        // ES2024 groupBy
        const byTeam = Object.groupBy(users, (u) => u.team);
        console.log(Object.entries(byTeam).map(([t, list]) => `${t}:${list.length}`));
        // ES2021 numeric separators + logical assignment
        const config = { limit: null };
        config.limit ??= 1_000_000;
        console.log(config.limit);
        // ES2025 Promise.try + Set methods
        const result = await Promise.try(() => JSON.parse('{"ok":true}'));
        console.log(result, new Set(["a", "b"]).union(new Set(["c"])).size);
        // ES2022 top-level await, error cause
        const err = new Error("outer", { cause: new Error("inner") });
        console.log(err.cause.message);
    ''', out='''
        [ 'Pune', 'unknown', 'Delhi' ]
        Ravi
        [ 'web:2', 'api:1' ]
        1000000
        { ok: true } 3
        inner
    ''')
    yield section("On the horizon", "telescope")
    yield table(
        ["Proposal", "What it adds"],
        ["**Temporal**", "Modern immutable date/time API replacing `Date`"],
        ["**Explicit resource management**", "`using res = getResource()` — automatic cleanup via `Symbol.dispose`"],
        ["**Decorators**", "`@logged method() {}` — standardised class decorators (used by TypeScript/Angular)"],
        ["**Import defer / source phase imports**", "Lazier module evaluation, WebAssembly integration"],
    )
    yield section("How features arrive: the TC39 process", "stairs-up")
    yield steps(
        ("Stage 0–1", "Idea and proposal with a champion on the TC39 committee."),
        ("Stage 2 / 2.7", "Draft spec text chosen; 2.7 = approved in principle, awaiting tests."),
        ("Stage 3", "Recommended for implementation; engines ship it (often behind flags)."),
        ("Stage 4", "Two shipping implementations + tests → included in the next yearly edition."),
    )
    yield note("Transpilers (Babel, TypeScript, esbuild, SWC) convert new syntax to older syntax; **polyfills** (core-js) add missing built-in functions. Syntax cannot be polyfilled — it must be transpiled.")
    yield qa("What were the most important ES6 features?",
             "`let`/`const` (block scope), arrow functions, classes, template literals, destructuring, default/rest/spread, modules, promises, `Map`/`Set`, symbols, iterators/generators and `for…of`.")


@topic(G, "gotchas", "Common Gotchas", "alert-triangle")
def _():
    yield lead("The famous weird parts of JavaScript — each one is logical once you know the rule behind it.")
    yield section("Coercion surprises", "transform")
    yield snippet("js", '''
        console.log([] == ![], "b" + "a" + +"a" + "a");
        console.log(null >= 0, null > 0, null == 0);
        console.log([1, 2, 3] + [4, 5], typeof (1 + "1" - 1));
        console.log(Math.max() < Math.min(), 0.1 * 3, 9007199254740992 + 1);
        console.log("10" > "9", 10 > "9", [10, 9, 1].sort());
    ''', out='''
        true baNaNa
        true false false
        1,2,34,5 number
        true 0.30000000000000004 9007199254740992
        false true [ 1, 10, 9 ]
    ''')
    yield table(
        ["Expression", "Why"],
        ["`[] == ![]` → `true`", "`![]` is `false`; `[] == false` → `\"\" == 0` → `0 == 0`"],
        ["`'b' + 'a' + +'a' + 'a'`", "`+'a'` is `NaN`, concatenated as text"],
        ["`null >= 0` but not `null == 0`", "Relational operators convert `null` to `0`; `==` only equates `null` with `undefined`"],
        ["`Math.max() < Math.min()`", "`-Infinity < Infinity`"],
        ["`'10' > '9'` is `false`", "Two strings compare character by character"],
    )
    yield section("Syntax and semantics traps", "code-minus")
    yield snippet("js", '''
        // 1. Automatic semicolon insertion
        const a = 1
        const b = a
        ;[1, 2].forEach((n) => console.log("ASI needs the leading ;", n))

        // 2. typeof of a TDZ variable throws (unlike undeclared)
        try { typeof later; } catch (e) { console.log(e.name); }
        let later = 1;

        // 3. array holes and length
        const arr = [1, , 3];
        console.log(arr.length, arr.map((x) => x * 2), 1 in arr);

        // 4. delete on arrays leaves holes
        const nums = [1, 2, 3];
        delete nums[1];
        console.log(nums, nums.length);
    ''', out='''
        ASI needs the leading ; 1
        ASI needs the leading ; 2
        ReferenceError
        3 [ 2, <1 empty item>, 6 ] false
        [ 1, <1 empty item>, 3 ] 3
    ''')
    yield section("Numbers and dates", "number")
    yield snippet("js", '''
        console.log(parseInt("08"), parseInt(0.0000005), (0.1).toFixed(20));
        console.log(new Date(2024, 1, 30).getDate(), new Date(2024, 0, 1).getMonth());
        console.log(typeof NaN, [NaN].indexOf(NaN), Number.MIN_VALUE > 0);
    ''', out='''
        8 5 0.10000000000000000555
        1 0
        number -1 true
    ''')
    yield note("`parseInt(0.0000005)` is `5` because the number is first converted to the string `\"5e-7\"`. Feb 30 rolls over to March 1. `Number.MIN_VALUE` is the smallest *positive* double, not the most negative number.")
    yield section("Objects, this and references", "box")
    yield snippet("js", '''
        const key1 = {}, key2 = {};
        const lookup = {};
        lookup[key1] = "first";
        lookup[key2] = "second";                 // both become "[object Object]"
        console.log(lookup[key1]);

        const counter = { n: 0, inc: () => this?.n };
        console.log(counter.inc());               // arrow method: no own this

        const defaults = { tags: [] };
        const a = { ...defaults }, b = { ...defaults };
        a.tags.push("shared!");
        console.log(b.tags);                      // shallow copy shares the array
    ''', out='''
        second
        undefined
        [ 'shared!' ]
    ''')
    yield section("Async traps", "clock-exclamation")
    yield snippet("js", '''
        const results = [];
        [1, 2, 3].forEach(async (n) => {
          await null;
          results.push(n);
        });
        console.log("right after forEach:", results);   // nothing awaited it
        await null; await null;
        console.log("a bit later:", results);

        const p = new Promise((resolve) => resolve(1));
        p.then((v) => console.log("then with", v));
        console.log("sync line runs first");
    ''', out='''
        right after forEach: []
        a bit later: [ 1, 2, 3 ]
        sync line runs first
        then with 1
    ''')
    yield dodont("Use `===`, `const`, `Number.isNaN`, explicit comparators for `sort`, `Map` for object keys, `for…of`/`Promise.all` with `await`, and a linter (ESLint) that flags most of these.",
                 "Rely on ASI when a line starts with `(`, `[` or a backtick template; `for…in` on arrays; `delete` on arrays; arrow functions as object methods.")


@topic(G, "polyfills", "Polyfills: Implement It Yourself", "tools")
def _():
    yield lead("Re-implementing built-ins is the classic way interviewers test understanding of `this`, prototypes, closures and promises. Each implementation below is tested against the real thing.")
    yield section("Array.prototype.map / filter / reduce", "brackets")
    yield snippet("js", '''
        Array.prototype.myMap = function (callback, thisArg) {
          if (typeof callback !== "function") throw new TypeError(callback + " is not a function");
          const result = new Array(this.length);
          for (let i = 0; i < this.length; i++) {
            if (i in this) result[i] = callback.call(thisArg, this[i], i, this);   // skip holes
          }
          return result;
        };
        Array.prototype.myFilter = function (callback, thisArg) {
          const result = [];
          for (let i = 0; i < this.length; i++) {
            if (i in this && callback.call(thisArg, this[i], i, this)) result.push(this[i]);
          }
          return result;
        };
        Array.prototype.myReduce = function (callback, ...init) {
          let i = 0, acc;
          if (init.length) acc = init[0];
          else {
            while (i < this.length && !(i in this)) i++;
            if (i >= this.length) throw new TypeError("Reduce of empty array with no initial value");
            acc = this[i++];
          }
          for (; i < this.length; i++) if (i in this) acc = callback(acc, this[i], i, this);
          return acc;
        };

        const nums = [1, 2, 3, 4];
        console.log(nums.myMap((n) => n * 2), nums.map((n) => n * 2));
        console.log(nums.myFilter((n) => n % 2), nums.myReduce((a, b) => a + b), nums.myReduce((a, b) => a + b, 10));
        console.log([1, , 3].myMap((x) => x), [1, , 3].map((x) => x));
    ''', out='''
        [ 2, 4, 6, 8 ] [ 2, 4, 6, 8 ]
        [ 1, 3 ] 10 20
        [ 1, <1 empty item>, 3 ] [ 1, <1 empty item>, 3 ]
    ''')
    yield section("Function.prototype.bind / call", "link")
    yield snippet("js", '''
        Function.prototype.myCall = function (context, ...args) {
          context = context ?? globalThis;
          const key = Symbol("fn");                 // unique key: no clash with existing props
          context[key] = this;
          try {
            return context[key](...args);           // implicit binding does the work
          } finally {
            delete context[key];
          }
        };
        Function.prototype.myBind = function (context, ...preset) {
          const fn = this;
          function bound(...later) {
            // when called with `new`, ignore the bound context
            return new.target ? new fn(...preset, ...later) : fn.apply(context, [...preset, ...later]);
          }
          bound.prototype = Object.create(fn.prototype);
          return bound;
        };

        function intro(greeting, mark) { return `${greeting}, ${this.name}${mark}`; }
        const asha = { name: "Asha" };
        console.log(intro.myCall(asha, "Hello", "!"));
        console.log(intro.myBind(asha, "Hi")("?"), Object.keys(asha));

        function Point(x, y) { this.x = x; this.y = y; }
        const PointAtX1 = Point.myBind(null, 1);
        const p = new PointAtX1(2);
        console.log(p.x, p.y, p instanceof Point);
    ''', out='''
        Hello, Asha!
        Hi, Asha? [ 'name' ]
        1 2 true
    ''')
    yield section("Promise.all and Promise.allSettled", "arrows-join-2")
    yield snippet("js", '''
        function promiseAll(iterable) {
          return new Promise((resolve, reject) => {
            const items = [...iterable];
            const results = new Array(items.length);
            let remaining = items.length;
            if (remaining === 0) return resolve(results);
            items.forEach((item, i) => {
              Promise.resolve(item).then((value) => {
                results[i] = value;                 // keep INPUT order, not finish order
                if (--remaining === 0) resolve(results);
              }, reject);                           // first rejection wins
            });
          });
        }
        const promiseAllSettled = (iterable) =>
          promiseAll([...iterable].map((p) =>
            Promise.resolve(p).then(
              (value) => ({ status: "fulfilled", value }),
              (reason) => ({ status: "rejected", reason })
            )));

        const delay = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms));
        console.log(await promiseAll([delay(20, "slow"), delay(5, "fast"), 3]));
        console.log(await promiseAll([]));
        await promiseAll([delay(5, 1), Promise.reject(new Error("fail"))]).catch((e) => console.log(e.message));
        console.log(await promiseAllSettled([1, Promise.reject("no")]));
    ''', out='''
        [ 'slow', 'fast', 3 ]
        []
        fail
        [
          { status: 'fulfilled', value: 1 },
          { status: 'rejected', reason: 'no' }
        ]
    ''')
    yield section("Promise.race and a mini Promise", "circle-dashed-check")
    yield snippet("js", '''
        const promiseRace = (iterable) =>
          new Promise((resolve, reject) => {
            for (const p of iterable) Promise.resolve(p).then(resolve, reject);
          });

        class MyPromise {
          #state = "pending"; #value; #handlers = [];
          constructor(executor) {
            const settle = (state) => (value) => {
              if (this.#state !== "pending") return;
              if (state === "fulfilled" && value && typeof value.then === "function") {
                return value.then(settle("fulfilled"), settle("rejected"));   // adopt thenables
              }
              this.#state = state; this.#value = value;
              this.#handlers.forEach((h) => h());
            };
            try { executor(settle("fulfilled"), settle("rejected")); } catch (e) { settle("rejected")(e); }
          }
          then(onFul, onRej) {
            return new MyPromise((resolve, reject) => {
              const run = () => queueMicrotask(() => {
                const cb = this.#state === "fulfilled" ? onFul : onRej;
                if (typeof cb !== "function") return (this.#state === "fulfilled" ? resolve : reject)(this.#value);
                try { resolve(cb(this.#value)); } catch (e) { reject(e); }
              });
              this.#state === "pending" ? this.#handlers.push(run) : run();
            });
          }
          catch(onRej) { return this.then(undefined, onRej); }
        }

        console.log(await promiseRace([new Promise((r) => setTimeout(r, 20, "slow")), "instant"]));
        new MyPromise((res) => setTimeout(res, 5, 2))
          .then((v) => v * 10)
          .then((v) => { throw new Error(`boom at ${v}`); })
          .catch((e) => e.message)
          .then((msg) => console.log("MyPromise chain:", msg));
        const value = await new MyPromise((res) => res(new MyPromise((r) => r("adopted"))));
        console.log(value);
    ''', out='''
        instant
        adopted
        MyPromise chain: boom at 20
    ''')
    yield section("Deep clone, deep equal, flatten", "copy")
    yield snippet("js", '''
        function deepClone(value, seen = new WeakMap()) {
          if (value === null || typeof value !== "object") return value;
          if (value instanceof Date) return new Date(value);
          if (value instanceof RegExp) return new RegExp(value.source, value.flags);
          if (seen.has(value)) return seen.get(value);            // handle cycles
          if (value instanceof Map) {
            const m = new Map(); seen.set(value, m);
            value.forEach((v, k) => m.set(deepClone(k, seen), deepClone(v, seen)));
            return m;
          }
          const copy = Array.isArray(value) ? [] : Object.create(Object.getPrototypeOf(value));
          seen.set(value, copy);
          for (const key of Reflect.ownKeys(value)) copy[key] = deepClone(value[key], seen);
          return copy;
        }
        function deepEqual(a, b) {
          if (Object.is(a, b)) return true;
          if (typeof a !== "object" || typeof b !== "object" || !a || !b) return false;
          if (Object.getPrototypeOf(a) !== Object.getPrototypeOf(b)) return false;
          const ka = Reflect.ownKeys(a), kb = Reflect.ownKeys(b);
          return ka.length === kb.length && ka.every((k) => deepEqual(a[k], b[k]));
        }
        const flatten = (arr, depth = Infinity) =>
          depth < 1 ? arr.slice() : arr.reduce((acc, x) => acc.concat(Array.isArray(x) ? flatten(x, depth - 1) : [x]), []);

        const src = { d: new Date(0), list: [1, { two: 2 }], map: new Map([["k", [1]]]) };
        src.self = src;
        const copy = deepClone(src);
        console.log(copy.self === copy, copy.list[1] !== src.list[1], copy.map.get("k"));
        console.log(deepEqual({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] }), deepEqual([1], { 0: 1 }));
        console.log(flatten([1, [2, [3, [4]]]]), flatten([1, [2, [3]]], 1));
    ''', out='''
        true true [ 1 ]
        true false
        [ 1, 2, 3, 4 ] [ 1, 2, [ 3 ] ]
    ''')
    yield section("A tiny EventEmitter", "broadcast")
    yield snippet("js", '''
        class Emitter {
          #events = new Map();
          on(name, fn) {
            (this.#events.get(name) ?? this.#events.set(name, []).get(name)).push(fn);
            return () => this.off(name, fn);        // return an unsubscribe function
          }
          off(name, fn) {
            this.#events.set(name, (this.#events.get(name) ?? []).filter((f) => f !== fn && f.original !== fn));
          }
          once(name, fn) {
            const wrapper = (...args) => { this.off(name, wrapper); fn(...args); };
            wrapper.original = fn;
            return this.on(name, wrapper);
          }
          emit(name, ...args) {
            const list = [...(this.#events.get(name) ?? [])];   // copy: listeners may unsubscribe
            list.forEach((fn) => fn(...args));
            return list.length > 0;
          }
        }
        const e = new Emitter();
        const unsubscribe = e.on("msg", (m) => console.log("A got", m));
        e.once("msg", (m) => console.log("B (once) got", m));
        e.emit("msg", 1);
        e.emit("msg", 2);
        unsubscribe();
        console.log(e.emit("msg", 3));
    ''', out='''
        A got 1
        B (once) got 1
        A got 2
        false
    ''')
    yield warn("Real polyfills check `if (!Array.prototype.x)` before defining, use `Object.defineProperty` to stay non-enumerable, and follow the spec's edge cases. In production, use core-js rather than hand-written versions.")
    yield qa("Why does a correct Promise.all polyfill need a counter instead of checking results.length?",
             "Results are written by index as promises settle in any order; assigning `results[2]` first makes `length` 3 immediately. A countdown of pending items is the reliable completion signal.")


@topic(G, "best-practices", "Best Practices & Clean Code", "checklist")
def _():
    yield lead("Habits that keep JavaScript codebases readable, safe and fast — the things code reviewers look for.")
    yield section("Language habits", "code")
    yield cards(
        ("`const` first, `let` if needed", "Never `var`. Smaller scopes, fewer surprises.", "lock"),
        ("`===` always", "Except the deliberate `x == null`.", "equal-double"),
        ("Prefer immutability", "Spread, `map`/`filter`, `toSorted`, `structuredClone` over in-place mutation of shared data.", "copy"),
        ("Small pure functions", "One job each, early returns instead of deep nesting, descriptive names.", "function"),
        ("async/await + try/catch", "No floating promises; handle every rejection; parallelise with `Promise.all`.", "clock"),
        ("Modules, not globals", "ES modules, named exports, no implicit globals.", "packages"),
    )
    yield section("Readable code", "eye")
    yield snippet("js", '''
        // ✗ nested, magic numbers, unclear names
        function f(u) {
          if (u) {
            if (u.a > 17) {
              if (u.s === 1) return true;
            }
          }
          return false;
        }

        // ✓ guard clauses, named constants, descriptive names
        const ADULT_AGE = 18;
        const STATUS = Object.freeze({ ACTIVE: 1, BANNED: 2 });
        function canPurchase(user) {
          if (!user) return false;
          if (user.age < ADULT_AGE) return false;
          return user.status === STATUS.ACTIVE;
        }
        console.log(f({ a: 20, s: 1 }), canPurchase({ age: 20, status: STATUS.ACTIVE }), canPurchase(null));
    ''', out="true true false")
    yield section("Security", "shield-lock")
    yield table(
        ["Risk", "Practice"],
        ["XSS", "Use `textContent`, not `innerHTML`, for user data; sanitise HTML (DOMPurify); set a Content-Security-Policy"],
        ["`eval` / `new Function` / string `setTimeout`", "Never run strings built from input"],
        ["Prototype pollution", "Don't deep-merge untrusted JSON into objects; block `__proto__`/`constructor` keys; use `Map` or `Object.create(null)`"],
        ["Secrets", "Nothing secret in client code or `localStorage`; `HttpOnly` cookies for sessions"],
        ["Dependencies", "`npm audit`, lockfiles, minimal packages, pin and review updates"],
        ["ReDoS", "Avoid nested quantifiers like `(a+)+` on user input"],
    )
    yield snippet("js", '''
        const payload = JSON.parse('{"__proto__": {"isAdmin": true}}');
        function naiveMerge(target, src) {
          for (const k in src) {
            if (typeof src[k] === "object") naiveMerge((target[k] ??= {}), src[k]);
            else target[k] = src[k];
          }
          return target;
        }
        naiveMerge({}, payload);
        console.log("every object is now admin:", ({}).isAdmin);
        delete Object.prototype.isAdmin;                          // undo the damage
        console.log("after cleanup:", ({}).isAdmin);
    ''', out='''
        every object is now admin: true
        after cleanup: undefined
    ''')
    yield section("Performance", "gauge")
    yield ul(
        "Measure first (DevTools Performance panel, `performance.now()`, Lighthouse) — don't guess.",
        "Pick the right structure: `Set`/`Map` lookups are O(1); `array.includes` inside a loop is O(n²).",
        "Avoid blocking the main thread: chunk long work, use Web Workers, debounce/throttle event handlers.",
        "Keep object shapes stable (initialise all fields in the constructor) so the JIT can optimise.",
        "Ship less JavaScript: code-split with dynamic `import()`, tree-shake, lazy-load.",
    )
    yield section("Tooling", "tool")
    yield table(
        ["Tool", "Role"],
        ["ESLint", "Catches bugs and enforces conventions"],
        ["Prettier", "Formatting — end style debates"],
        ["TypeScript / JSDoc types", "Static types: catch whole classes of bugs before running"],
        ["Vitest / Jest / `node:test`", "Unit tests"],
        ["Vite / esbuild / webpack", "Bundling, dev server, transpiling"],
    )
    yield snippet("js", '''
        import { test } from "node:test";
        import assert from "node:assert/strict";

        const slugify = (s) => s.trim().toLowerCase().replace(/\\s+/g, "-");
        assert.equal(slugify("  Hello World "), "hello-world");
        assert.deepEqual([1, 2].map((x) => x * 2), [2, 4]);
        assert.throws(() => JSON.parse("{"), SyntaxError);
        console.log("all assertions passed");
    ''', out="all assertions passed")
    yield qa("How would you improve the performance of a slow page?",
             "Measure first. Then: reduce and split the JS bundle, defer non-critical scripts, avoid layout thrashing, debounce expensive handlers, move heavy computation to a Worker, virtualise long lists, cache network responses, and use efficient data structures.")
