from kit import *

G = "Interview Prep"


@topic(G, "predict-output", "Predict the Output", "zoom-question")
def _():
    yield lead("The most common JavaScript interview format: read a snippet, say what it prints and *why*. Try each one before looking at the output.")
    yield section("1. Hoisting", "arrow-bar-up")
    yield snippet("js", '''
        var x = 1;
        function test() {
          console.log(x);
          var x = 2;
          console.log(x);
        }
        test();
        console.log(typeof hoisted, typeof expr);
        function hoisted() {}
        var expr = function () {};
    ''', out='''
        undefined
        2
        function undefined
    ''')
    yield p("The local `var x` is hoisted to the top of `test` (as `undefined`) and shadows the global. `expr` is a `var` still holding `undefined` when `typeof` runs.")
    yield section("2. Closures in loops", "repeat")
    yield snippet("js", '''
        const fns = [];
        for (var i = 0; i < 3; i++) fns.push(() => i);
        const fns2 = [];
        for (let i = 0; i < 3; i++) fns2.push(() => i);
        console.log(fns.map((f) => f()), fns2.map((f) => f()));
    ''', out="[ 3, 3, 3 ] [ 0, 1, 2 ]")
    yield section("3. this", "pointer")
    yield snippet("js", '''
        const obj = {
          name: "obj",
          regular() { return this.name; },
          arrow: () => typeof this,
          nested() {
            const inner = () => this.name;     // arrow borrows nested()'s this
            function plain() { return this; }  // plain call → undefined (strict)
            return [inner(), plain()];
          },
        };
        const { regular } = obj;
        console.log(obj.regular(), obj.arrow(), obj.nested());
        try { regular(); } catch (e) { console.log(e.constructor.name); }
    ''', out='''
        obj undefined [ 'obj', undefined ]
        TypeError
    ''')
    yield section("4. Event loop ordering", "refresh-dot")
    yield snippet("js", '''
        console.log(1);
        setTimeout(() => console.log(2), 0);
        Promise.resolve().then(() => {
          console.log(3);
          setTimeout(() => console.log(4), 0);
          Promise.resolve().then(() => console.log(5));
        });
        (async () => {
          console.log(6);
          await undefined;
          console.log(7);
        })();
        console.log(8);
    ''', out='''
        1
        6
        8
        3
        7
        5
        2
        4
    ''')
    yield p("Sync first (1, 6, 8). Then microtasks in queue order: the `then` (3, which queues 5 and timer 4), the `await` continuation (7), then 5. Finally macrotasks in order: 2, then 4.")
    yield section("5. Coercion", "transform")
    yield snippet("js", '''
        console.log(1 < 2 < 3, 3 > 2 > 1);
        console.log("5" + 3, "5" - 3, "5" * "2", true + true);
        console.log([] + null + 1, [2] * [3], {} + []);
        console.log(0 || null || "" || undefined, 1 && "a" && 0);
    ''', out='''
        true false
        53 2 10 2
        null1 6 [object Object]
        undefined 0
    ''')
    yield p("`3 > 2 > 1` → `true > 1` → `1 > 1` → `false`. `[] + null + 1` → `\"\" + \"null\"` → `\"null\" + 1`. `||` returns the last operand when all are falsy; `&&` returns the first falsy one.")
    yield section("6. References and copies", "copy")
    yield snippet("js", '''
        let a = { n: 1 };
        let b = a;
        a.n = 2;
        a = { n: 3 };
        console.log(b.n);

        const arr = [1, 2, 3];
        const copy = arr;
        copy.push(4);
        const spread = [...arr];
        spread.push(5);
        console.log(arr.length, spread.length);

        function change(o) { o.value = "changed"; o = { value: "replaced" }; }
        const item = { value: "original" };
        change(item);
        console.log(item.value);
    ''', out='''
        2
        4 5
        changed
    ''')
    yield section("7. Promises", "circle-dashed-check")
    yield snippet("js", '''
        const p = new Promise((resolve, reject) => {
          console.log("A");
          resolve("B");
          reject("C");
          console.log("D");
        });
        p.then(console.log).catch(() => console.log("never"));
        Promise.reject(new Error("E"))
          .then(() => console.log("skipped"))
          .catch((e) => e.message)
          .then((m) => console.log(m + "!"))
          .finally(() => console.log("F"));
        console.log("G");
    ''', out='''
        A
        D
        G
        B
        E!
        F
    ''')
    yield section("8. Mixed bag", "puzzle")
    yield snippet("js", '''
        console.log(typeof typeof 1, typeof [] === typeof null);
        console.log([..."abc"].map(parseInt));
        console.log(0.1 + 0.2 == 0.3, 0.5 + 0.25 == 0.75);
        const x = { a: 1 }, y = { a: 1 };
        console.log(x == y, JSON.stringify(x) === JSON.stringify(y));
        console.log([1, 2, 3].indexOf(3) > -1 ? "found" : "missing", [10, 1, 3].sort().join());
        function Foo() { return this; }
        console.log(new Foo() instanceof Foo, Foo());
    ''', out='''
        string true
        [ NaN, NaN, NaN ]
        false true
        false true
        found 1,10,3
        true undefined
    ''')
    yield note("`parseInt(\"a\", 0)` → `NaN` (radix 0 means default 10, but `a` is not a digit), then radix 1 is invalid, and `\"c\"` isn't a base-2 digit. `0.5 + 0.25` is exact because both are powers of two.")


@topic(G, "coding-challenges", "Coding Challenges", "code-dots")
def _():
    yield lead("Short problems that show up again and again in JavaScript interviews — each with a clean, idiomatic solution and its complexity.")
    yield section("Strings", "letter-case")
    yield snippet("js", '''
        const isAnagram = (a, b) => {
          if (a.length !== b.length) return false;
          const counts = new Map();
          for (const ch of a) counts.set(ch, (counts.get(ch) ?? 0) + 1);
          for (const ch of b) {
            if (!counts.get(ch)) return false;
            counts.set(ch, counts.get(ch) - 1);
          }
          return true;
        };
        const firstUnique = (s) => {
          const freq = {};
          for (const ch of s) freq[ch] = (freq[ch] ?? 0) + 1;
          return [...s].find((ch) => freq[ch] === 1) ?? null;
        };
        const longestUniqueSubstring = (s) => {        // sliding window, O(n)
          let best = 0, start = 0;
          const lastSeen = new Map();
          [...s].forEach((ch, i) => {
            if (lastSeen.get(ch) >= start) start = lastSeen.get(ch) + 1;
            lastSeen.set(ch, i);
            best = Math.max(best, i - start + 1);
          });
          return best;
        };
        const compress = (s) => s.replace(/(.)\\1*/g, (run, ch) => ch + run.length);

        console.log(isAnagram("listen", "silent"), isAnagram("rat", "car"));
        console.log(firstUnique("swiss"), longestUniqueSubstring("abcabcbb"), compress("aaabccdddd"));
    ''', out='''
        true false
        w 3 a3b1c2d4
    ''')
    yield section("Arrays", "brackets")
    yield snippet("js", '''
        const twoSum = (nums, target) => {             // O(n) with a hash map
          const seen = new Map();
          for (const [i, n] of nums.entries()) {
            if (seen.has(target - n)) return [seen.get(target - n), i];
            seen.set(n, i);
          }
          return null;
        };
        const maxSubarray = (nums) => {                // Kadane, O(n)
          let best = -Infinity, current = 0;
          for (const n of nums) {
            current = Math.max(n, current + n);
            best = Math.max(best, current);
          }
          return best;
        };
        const rotate = (arr, k) => {
          k %= arr.length;
          return [...arr.slice(-k), ...arr.slice(0, -k)];
        };
        const missingNumber = (nums) => (nums.length * (nums.length + 1)) / 2 - nums.reduce((a, b) => a + b, 0);
        const moveZeros = (arr) => [...arr.filter((x) => x !== 0), ...arr.filter((x) => x === 0)];

        console.log(twoSum([2, 7, 11, 15], 9), maxSubarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]));
        console.log(rotate([1, 2, 3, 4, 5], 2), missingNumber([3, 0, 1]), moveZeros([0, 1, 0, 3, 12]));
    ''', out='''
        [ 0, 1 ] 6
        [ 4, 5, 1, 2, 3 ] 2 [ 1, 3, 12, 0, 0 ]
    ''')
    yield section("Objects and data shaping", "braces")
    yield snippet("js", '''
        const flattenObject = (obj, prefix = "") =>
          Object.entries(obj).reduce((acc, [k, v]) => {
            const key = prefix ? `${prefix}.${k}` : k;
            return v && typeof v === "object" && !Array.isArray(v)
              ? { ...acc, ...flattenObject(v, key) }
              : { ...acc, [key]: v };
          }, {});
        const get = (obj, path, fallback) =>
          path.split(".").reduce((cur, key) => cur?.[key], obj) ?? fallback;
        const invert = (obj) => Object.fromEntries(Object.entries(obj).map(([k, v]) => [v, k]));

        const config = { db: { host: "localhost", port: 5432 }, debug: true };
        console.log(flattenObject(config));
        console.log(get(config, "db.port"), get(config, "db.user.name", "n/a"));
        console.log(invert({ a: "x", b: "y" }));
    ''', out='''
        { 'db.host': 'localhost', 'db.port': 5432, debug: true }
        5432 n/a
        { x: 'a', y: 'b' }
    ''')
    yield section("Async utilities", "clock")
    yield snippet("js", '''
        const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

        async function retry(fn, { retries = 3, delay = 5 } = {}) {
          for (let attempt = 1; ; attempt++) {
            try {
              return await fn(attempt);
            } catch (err) {
              if (attempt > retries) throw err;
              await sleep(delay * 2 ** (attempt - 1));     // exponential back-off
            }
          }
        }

        async function mapWithConcurrency(items, limit, fn) {
          const results = new Array(items.length);
          let next = 0, active = 0, peak = 0;
          async function worker() {
            while (next < items.length) {
              const i = next++;
              peak = Math.max(peak, ++active);
              results[i] = await fn(items[i]);
              active--;
            }
          }
          await Promise.all(Array.from({ length: limit }, worker));
          return { results, peak };
        }

        const flaky = async (attempt) => {
          if (attempt < 3) throw new Error(`attempt ${attempt} failed`);
          return `succeeded on attempt ${attempt}`;
        };
        console.log(await retry(flaky));
        const { results, peak } = await mapWithConcurrency([1, 2, 3, 4, 5], 2, async (n) => {
          await sleep(5);
          return n * n;
        });
        console.log(results, "max concurrent:", peak);
    ''', out='''
        succeeded on attempt 3
        [ 1, 4, 9, 16, 25 ] max concurrent: 2
    ''')
    yield section("A tiny LRU cache", "database")
    yield snippet("js", '''
        class LRUCache {
          #map = new Map();                       // Map remembers insertion order
          constructor(capacity) { this.capacity = capacity; }
          get(key) {
            if (!this.#map.has(key)) return -1;
            const value = this.#map.get(key);
            this.#map.delete(key);                // move to most-recent position
            this.#map.set(key, value);
            return value;
          }
          put(key, value) {
            this.#map.delete(key);
            this.#map.set(key, value);
            if (this.#map.size > this.capacity) {
              this.#map.delete(this.#map.keys().next().value);   // evict least recent
            }
          }
          keys() { return [...this.#map.keys()]; }
        }
        const lru = new LRUCache(2);
        lru.put("a", 1);
        lru.put("b", 2);
        lru.get("a");
        lru.put("c", 3);                          // evicts "b"
        console.log(lru.keys(), lru.get("b"), lru.get("c"));
    ''', out="[ 'a', 'c' ] -1 3")
    yield note("Talk through complexity as you go: the anagram and two-sum solutions are O(n) time / O(n) space; the LRU operations are O(1) because `Map` keeps insertion order.")


@topic(G, "interview-qa", "JavaScript Interview Q&A", "message-question")
def _():
    yield lead("Rapid-fire questions from junior to senior level. Expand each for a crisp, interview-ready answer; follow the topic links in your head to go deeper.")
    yield section("Fundamentals", "school")
    yield qa("What are the data types in JavaScript?",
             "Seven primitives — `number`, `bigint`, `string`, `boolean`, `undefined`, `null`, `symbol` — and `object` (which includes arrays, functions, dates, maps…). Primitives are immutable and compared by value; objects are compared by reference.")
    yield qa("var vs let vs const?",
             "`var`: function scope, hoisted as `undefined`, re-declarable. `let`: block scope, TDZ, reassignable. `const`: block scope, TDZ, no reassignment (object contents still mutable).")
    yield qa("What is the temporal dead zone?",
             "The span between entering a scope and the line where a `let`/`const`/`class` is declared. The binding exists (it is hoisted) but is uninitialised; any access throws `ReferenceError`.")
    yield qa("null vs undefined?",
             "`undefined` means a value was never assigned (missing variable value, property, argument or return). `null` is an explicit “empty” set by the programmer. `null == undefined` is `true`, `===` is `false`, `typeof null` is `\"object\"`.")
    yield qa("== vs ===?",
             "`===` compares type and value with no conversion. `==` coerces operands first (e.g. `'1' == 1`). Use `===`, except `x == null` to test for null-or-undefined.")
    yield qa("What is NaN and how do you test for it?",
             "“Not a Number”, a `number` value produced by invalid maths (`0/0`, `Number('x')`). It is not equal to itself, so use `Number.isNaN(x)` or `Object.is(x, NaN)`.")
    yield section("Functions & scope", "function")
    yield qa("What is a closure?",
             "A function plus the lexical environment it was created in. Inner functions keep access to outer variables after the outer function returns — used for private state, factories, memoization, and callbacks.")
    yield qa("What is hoisting?",
             "Declarations are processed before code runs: function declarations are fully available, `var`s are `undefined`, `let`/`const`/`class` sit in the TDZ.")
    yield qa("Explain this in JavaScript.",
             "Determined at call time: `new` → new object; `call/apply/bind` → given object; `obj.fn()` → `obj`; plain call → `undefined` (strict) or global (sloppy). Arrow functions inherit `this` lexically.")
    yield qa("call vs apply vs bind?",
             "`call(this, a, b)` and `apply(this, [a, b])` invoke immediately; `bind(this, a)` returns a new permanently bound function.")
    yield qa("Arrow functions vs regular functions?",
             "Arrows have lexical `this` and `arguments`, cannot be constructors, have no `prototype`, and are always expressions. Regular functions get a dynamic `this` and can be used with `new`.")
    yield qa("What are higher-order functions?",
             "Functions that take functions as arguments or return functions — `map`, `filter`, `reduce`, `setTimeout`, decorators like `debounce` and `memoize`.")
    yield qa("Currying vs partial application?",
             "Currying turns an n-ary function into n unary functions `f(a)(b)(c)`. Partial application fixes some arguments and returns a function taking the rest (`bind`, `partial`).")
    yield section("Objects & prototypes", "hierarchy")
    yield qa("How does prototypal inheritance work?",
             "Every object links to a prototype. Missing properties are looked up along the chain until `null`. `class`/`extends` builds these chains; methods are shared through `Class.prototype`.")
    yield qa("What does the new keyword do?",
             "Creates an object, links it to `Ctor.prototype`, runs the constructor with `this` bound to it, and returns it (unless the constructor returns another object).")
    yield qa("How do you deep-copy an object?",
             "`structuredClone(obj)` (handles Dates, Maps, Sets, cycles; not functions or class prototypes). `JSON.parse(JSON.stringify(obj))` only for JSON-safe data. Spread and `Object.assign` are shallow.")
    yield qa("Object.freeze vs Object.seal?",
             "Both stop adding/removing properties; `freeze` also makes values read-only. Both are shallow.")
    yield qa("Map vs Object, Set vs Array?",
             "`Map`: any key type, insertion order, `size`, fast frequent updates, no prototype keys. `Set`: unique values with O(1) `has`, versus an array's O(n) `includes`.")
    yield qa("What are WeakMap and WeakSet for?",
             "Associating data with objects without preventing their garbage collection — private data, caches, “visited” marks. Keys must be objects; they are not iterable.")
    yield section("Asynchronous JavaScript", "clock")
    yield qa("Explain the event loop.",
             "JS runs on one call stack. Async work is delegated to the runtime; completions queue callbacks. When the stack is empty the loop drains all microtasks (promise reactions), then runs the next macrotask (timer, I/O, event), and in browsers may render between tasks.")
    yield qa("Microtask vs macrotask?",
             "Microtasks: promise `then`/`catch`/`finally`, `await` continuations, `queueMicrotask` — all run right after the current task. Macrotasks: `setTimeout`, `setInterval`, I/O, UI events — one per loop turn. Hence `Promise.then` runs before `setTimeout(…, 0)`.")
    yield qa("What is a Promise?",
             "An object representing the eventual result of an async operation; pending → fulfilled/rejected, settled once. `then` returns a new promise, enabling chaining and centralised error handling with `catch`.")
    yield qa("Promise.all vs allSettled vs race vs any?",
             "`all`: all fulfil or first rejection. `allSettled`: waits for all, reports each. `race`: first to settle. `any`: first to fulfil, `AggregateError` if all reject.")
    yield qa("How does async/await relate to promises?",
             "Syntax sugar: an `async` function returns a promise; `await` pauses that function until a promise settles, resuming with its value or throwing its reason, so `try/catch` works.")
    yield qa("How do you run async tasks in parallel vs in sequence?",
             "Parallel: start them all, then `await Promise.all([...])`. Sequence: `for…of` with `await` inside. Never `forEach` with an async callback.")
    yield qa("How do you cancel a fetch or other async work?",
             "Pass an `AbortController`'s `signal` to `fetch` (or your own function), then call `controller.abort()`. `AbortSignal.timeout(ms)` gives a ready-made timeout signal.")
    yield section("Browser & performance", "browser")
    yield qa("What is event delegation?",
             "One listener on a parent handles events from many children via bubbling and `event.target.closest(...)` — fewer listeners and it works for elements added later.")
    yield qa("Event bubbling vs capturing?",
             "Events travel from window down to the target (capture), then back up (bubble). Listeners run in the bubble phase unless registered with `{ capture: true }`. `stopPropagation()` halts the journey.")
    yield qa("Debounce vs throttle?",
             "Debounce runs once after activity stops for N ms (search input). Throttle runs at most once every N ms during activity (scroll).")
    yield qa("What causes memory leaks in JavaScript?",
             "Anything that keeps unused objects reachable: uncleared intervals, listeners never removed, unbounded caches, closures holding big data, detached DOM nodes referenced from JS, accidental globals.")
    yield qa("localStorage vs sessionStorage vs cookies?",
             "localStorage persists, sessionStorage is per-tab; both ~5 MB, JS-only. Cookies are small, sent with requests, and can be HttpOnly — use them for auth.")
    yield qa("What is CORS?",
             "A browser mechanism that lets servers opt in to cross-origin reads via `Access-Control-Allow-*` headers, with preflight `OPTIONS` requests for non-simple requests. It protects users; it is enforced by browsers, not servers.")
    yield section("Modules, tooling & modern JS", "packages")
    yield qa("ES modules vs CommonJS?",
             "ESM: static `import`/`export`, live bindings, async loading, top-level await, strict by default, tree-shakable. CJS: runtime `require`, `module.exports` object, synchronous, Node-specific.")
    yield qa("What is strict mode?",
             "A safer JS variant: undeclared assignments throw, `this` is `undefined` in plain calls, silent failures become errors, `with` is banned. Automatic in modules and classes.")
    yield qa("What is a polyfill vs a transpiler?",
             "A polyfill adds a missing built-in API at runtime (e.g. `Array.prototype.flat`). A transpiler (Babel, TypeScript) rewrites new *syntax* into older syntax at build time.")
    yield qa("Why use TypeScript?",
             "Static types catch errors at compile time, power editor autocompletion and safe refactoring, and document intent. It compiles to plain JavaScript; types disappear at runtime.")
    yield qa("What are generators used for?",
             "Functions that can pause with `yield` — lazy/infinite sequences, custom iterators, two-way coroutines, and (async generators) streaming data such as paginated APIs.")
    yield qa("What is a Proxy?",
             "A wrapper that intercepts operations (get, set, has, delete, apply…) on a target object — used for validation, reactivity (Vue 3), logging and virtual properties. `Reflect` supplies the default behaviour.")
    yield section("How to answer well", "bulb")
    yield steps(
        ("Define", "One precise sentence (“A closure is…”)."),
        ("Show", "A 3–5 line example — ideally one you can run in your head."),
        ("Explain the why", "Mention the underlying mechanism (scope chain, prototype chain, event loop)."),
        ("Trade-offs & pitfalls", "When not to use it, the common bug, the modern alternative."),
    )
