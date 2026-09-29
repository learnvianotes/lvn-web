from kit import *

G = "Collections & Iteration"


@topic(G, "map-set", "Map & Set", "list-search")
def _():
    yield lead("`Map` is a key → value store where keys can be *anything*; `Set` is a collection of unique values. Both keep insertion order and have O(1) average lookups.")
    yield section("Map", "map-2")
    yield snippet("js", '''
        const m = new Map();
        const objKey = { id: 1 };
        m.set("name", "Asha").set(42, "number key").set(objKey, "object key");
        console.log(m.get(objKey), m.get(42), m.get("missing"));
        console.log(m.has("name"), m.size);
        m.delete(42);
        console.log(m);
        for (const [key, value] of m) console.log(key, "→", value);
        console.log([...m.keys()], new Map(Object.entries({ a: 1 })));
    ''', out='''
        object key number key undefined
        true 3
        Map(2) { 'name' => 'Asha', { id: 1 } => 'object key' }
        name → Asha
        { id: 1 } → object key
        [ 'name', { id: 1 } ] Map(1) { 'a' => 1 }
    ''')
    yield section("Map vs plain object", "scale")
    yield table(
        ["", "`Object`", "`Map`"],
        ["Key types", "Strings and symbols (others are stringified)", "Any value — objects, functions, `NaN`"],
        ["Order", "Integer keys first, then insertion", "Pure insertion order"],
        ["Size", "`Object.keys(o).length`", "`m.size`"],
        ["Iteration", "Via `Object.entries`", "Directly iterable"],
        ["Accidental keys", "Inherits `toString`, `constructor`, `__proto__` risks", "None"],
        ["Frequent add/delete", "Slower", "Optimised for it"],
        ["JSON support", "Native", "Convert: `Object.fromEntries(m)`"],
    )
    yield good("Use a `Map` for dynamic dictionaries (caches, counts, lookups by id or by object); use an object for fixed-shape records.")
    yield section("Set", "circles")
    yield snippet("js", '''
        const s = new Set([3, 1, 3, 2, 1]);
        s.add(4).add(1);
        console.log(s, s.size, s.has(2));
        s.delete(3);
        console.log([...s]);
        console.log([...new Set("mississippi")].join(""));
    ''', out='''
        Set(4) { 3, 1, 2, 4 } 4 true
        [ 1, 2, 4 ]
        misp
    ''')
    yield section("Set operations (ES2025, Node 22+)", "math-symbols")
    yield snippet("js", '''
        const a = new Set([1, 2, 3, 4]);
        const b = new Set([3, 4, 5]);
        console.log(a.union(b));
        console.log(a.intersection(b));
        console.log(a.difference(b), a.symmetricDifference(b));
        console.log(new Set([3]).isSubsetOf(a), a.isDisjointFrom(new Set([9])));
        // the classic way, still common in interviews:
        console.log([...a].filter((x) => b.has(x)));
    ''', out='''
        Set(5) { 1, 2, 3, 4, 5 }
        Set(2) { 3, 4 }
        Set(2) { 1, 2 } Set(3) { 1, 2, 5 }
        true true
        [ 3, 4 ]
    ''')
    yield section("Equality of keys", "equal")
    yield snippet("js", '''
        const s = new Set([NaN, NaN, 0, -0, {}, {}]);
        console.log(s.size);             // NaN once, 0/-0 once, two distinct objects
        const m = new Map([[[1], "a"]]);
        console.log(m.get([1]));         // a different array → different key
    ''', out='''
        4
        undefined
    ''')
    yield qa("When would you use a Map instead of an object?",
             "When keys are not strings (objects, numbers you don't want stringified), when keys are added and removed frequently, when you need the size or guaranteed insertion order, or when keys come from user input (no prototype pollution risk).")
    yield qa("How do you remove duplicates from an array?",
             "`[...new Set(arr)]` — O(n), keeps first-occurrence order. For objects by a field: `[...new Map(arr.map((o) => [o.id, o])).values()]`.")


@topic(G, "weak-collections", "WeakMap, WeakSet & WeakRef", "ghost")
def _():
    yield lead("Weak collections hold their keys *weakly*: if nothing else references a key object, it can be garbage-collected and its entry silently disappears.")
    yield table(
        ["", "`Map` / `Set`", "`WeakMap` / `WeakSet`"],
        ["Keys", "Anything", "Objects (and non-registered symbols) only"],
        ["Keeps key alive?", "Yes — strong reference", "No — weak reference"],
        ["Iterable / `size`?", "Yes", "No (contents depend on the GC)"],
        ["Methods", "Full API", "`get/set/has/delete` · `add/has/delete`"],
    )
    yield section("Use case: private data / metadata per object", "lock")
    yield snippet("js", '''
        const privateData = new WeakMap();
        class Person {
          constructor(name, ssn) {
            this.name = name;
            privateData.set(this, { ssn });   // disappears when the Person is collected
          }
          lastFour() { return privateData.get(this).ssn.slice(-4); }
        }
        const p = new Person("Asha", "123-45-6789");
        console.log(p.lastFour(), p);
    ''', out="6789 Person { name: 'Asha' }")
    yield section("Use case: caching without leaks", "database")
    yield snippet("js", '''
        const cache = new WeakMap();
        function expensiveSummary(obj) {
          if (cache.has(obj)) return cache.get(obj) + " (cached)";
          const result = `keys=${Object.keys(obj).length}`;
          cache.set(obj, result);
          return result;
        }
        const report = { a: 1, b: 2 };
        console.log(expensiveSummary(report));
        console.log(expensiveSummary(report));
    ''', out='''
        keys=2
        keys=2 (cached)
    ''')
    yield section("WeakSet: tagging objects", "tag")
    yield snippet("js", '''
        const visited = new WeakSet();
        function visit(node) {
          if (visited.has(node)) return "already visited";
          visited.add(node);
          return "visiting";
        }
        const node = {};
        console.log(visit(node), "/", visit(node));
        try {
          visited.add("string");
        } catch (e) {
          console.log(e.message);
        }
    ''', out='''
        visiting / already visited
        Invalid value used in weak set
    ''')
    yield section("WeakRef and FinalizationRegistry (ES2021)", "ghost-2")
    yield snippet("js", '''
        let big = { data: "large object" };
        const ref = new WeakRef(big);
        console.log(ref.deref()?.data);   // still alive
        big = null;                       // now only weakly reachable — may be collected later
        const registry = new FinalizationRegistry((label) => console.log("collected", label));
        registry.register({}, "temp object");
    ''', out="large object")
    yield warn("GC timing is unpredictable: `deref()` may return the object long after you dropped it, and finalizers may never run. Use these only for caches and resource cleanup hints — never for program logic.")
    yield qa("Why can't you iterate a WeakMap?",
             "Its entries vanish whenever the garbage collector reclaims a key, which happens at non-deterministic times. Exposing iteration or `size` would make program behaviour depend on GC timing, so the API deliberately hides them.")


@topic(G, "symbols", "Symbols", "at")
def _():
    yield lead("A `symbol` is a unique, immutable primitive used as a property key that can never collide with any other key — and the gateway to customising built-in behaviour.")
    yield section("Creating symbols", "plus")
    yield snippet("js", '''
        const id1 = Symbol("id");
        const id2 = Symbol("id");
        console.log(id1 === id2, typeof id1, id1.description, id1.toString());

        const user = { name: "Asha", [id1]: 123 };
        console.log(user[id1], Object.keys(user), JSON.stringify(user));
        console.log(Object.getOwnPropertySymbols(user), Reflect.ownKeys(user));

        const shared = Symbol.for("app.token");      // global registry
        console.log(shared === Symbol.for("app.token"), Symbol.keyFor(shared));
    ''', out='''
        false symbol id Symbol(id)
        123 [ 'name' ] {"name":"Asha"}
        [ Symbol(id) ] [ 'name', Symbol(id) ]
        true app.token
    ''')
    yield note("Symbol keys are skipped by `for…in`, `Object.keys` and `JSON.stringify` — handy for metadata that should not leak into serialisation. They are *not* private: `Object.getOwnPropertySymbols` finds them.")
    yield section("Well-known symbols", "star")
    yield table(
        ["Symbol", "Customises"],
        ["`Symbol.iterator`", "`for…of`, spread, destructuring"],
        ["`Symbol.asyncIterator`", "`for await…of`"],
        ["`Symbol.toPrimitive`", "Conversion to number/string"],
        ["`Symbol.toStringTag`", "`Object.prototype.toString` output"],
        ["`Symbol.hasInstance`", "`instanceof`"],
        ["`Symbol.dispose` / `asyncDispose`", "`using` declarations (explicit resource management)"],
    )
    yield snippet("js", '''
        class Temperature {
          constructor(c) { this.c = c; }
          get [Symbol.toStringTag]() { return "Temperature"; }
          [Symbol.toPrimitive](hint) { return hint === "string" ? `${this.c}°C` : this.c; }
        }
        const t = new Temperature(21);
        console.log(Object.prototype.toString.call(t), `${t}`, t + 1);

        class Even {
          static [Symbol.hasInstance](n) { return Number.isInteger(n) && n % 2 === 0; }
        }
        console.log(4 instanceof Even, 3 instanceof Even);
    ''', out='''
        [object Temperature] 21°C 22
        true false
    ''')
    yield qa("What are Symbols used for?",
             "Collision-free property keys (for libraries adding metadata to objects they don't own), constants that can't be confused with strings, and well-known symbols to hook into language behaviour (`Symbol.iterator`, `Symbol.toPrimitive`, …).")


@topic(G, "iterators", "Iterators & Iterables", "repeat")
def _():
    yield lead("The iteration protocols are what make `for…of`, spread, destructuring, `Array.from` and `Promise.all` work on any collection — including your own.")
    yield section("The two protocols", "list-check")
    yield cards(
        ("Iterable", "An object with a `[Symbol.iterator]()` method that returns an iterator. Arrays, strings, Maps, Sets, `arguments`, NodeLists and generators are iterable. Plain objects are **not**.", "repeat"),
        ("Iterator", "An object with a `next()` method returning `{ value, done }`. Optional `return()` is called on early exit (`break`).", "player-track-next"),
    )
    yield snippet("js", '''
        const arr = ["a", "b"];
        const it = arr[Symbol.iterator]();
        console.log(it.next(), it.next(), it.next());
        try {
          for (const x of { a: 1 }) {}
        } catch (e) {
          console.log(e.message);
        }
    ''', out='''
        { value: 'a', done: false } { value: 'b', done: false } { value: undefined, done: true }
        {(intermediate value)} is not iterable
    ''')
    yield section("A custom iterable", "code")
    yield snippet("js", '''
        class Range {
          constructor(start, end, step = 1) { Object.assign(this, { start, end, step }); }
          [Symbol.iterator]() {
            let current = this.start;
            const { end, step } = this;
            return {
              next: () =>
                current <= end ? { value: (current += step) - step, done: false } : { value: undefined, done: true },
              [Symbol.iterator]() { return this; },   // iterators are usually iterable too
            };
          }
        }
        const r = new Range(1, 10, 3);
        console.log([...r]);
        const [first, second] = r;
        console.log(first, second, Math.max(...r), Array.from(r, (n) => n * 10));
        for (const n of new Range(1, 3)) console.log(n);
    ''', out='''
        [ 1, 4, 7, 10 ]
        1 4 10 [ 10, 40, 70, 100 ]
        1
        2
        3
    ''')
    yield section("Iterators are lazy and one-shot", "hourglass")
    yield snippet("js", '''
        const it = [1, 2, 3].values();
        console.log([...it], [...it]);          // second spread: already exhausted
        const m = new Map([["x", 1], ["y", 2]]);
        console.log(m.entries().next().value);
    ''', out='''
        [ 1, 2, 3 ] []
        [ 'x', 1 ]
    ''')
    yield section("Iterator helpers (ES2025, Node 22+)", "wand")
    yield snippet("js", '''
        function* naturals() { let n = 1; while (true) yield n++; }   // infinite!
        const firstSquaresOfEvens = naturals()
          .filter((n) => n % 2 === 0)
          .map((n) => n * n)
          .take(4)
          .toArray();
        console.log(firstSquaresOfEvens);
        console.log(Iterator.from([5, 6, 7]).drop(1).reduce((a, b) => a + b, 0));
    ''', out='''
        [ 4, 16, 36, 64 ]
        13
    ''')
    yield note("Iterator helpers are **lazy**: nothing is computed until `toArray()`, `for…of` or a reducer pulls values — so they work on infinite sequences where array methods cannot.")
    yield qa("How do you make an object iterable?",
             "Give it a `[Symbol.iterator]` method that returns an object with `next()` returning `{ value, done }` — or, easiest, make `[Symbol.iterator]` a generator: `*[Symbol.iterator]() { yield* this.items; }`.")


@topic(G, "generators", "Generators", "player-pause")
def _():
    yield lead("A generator is a function that can pause (`yield`) and resume later, producing a sequence of values on demand.")
    yield section("Basics", "code")
    yield snippet("js", '''
        function* countdown(n) {
          console.log("started");
          while (n > 0) yield n--;
          return "liftoff";
        }
        const gen = countdown(2);          // nothing runs yet
        console.log(gen.next());
        console.log(gen.next());
        console.log(gen.next());
        console.log(gen.next());
        console.log([...countdown(3)]);    // return value is not included by for…of / spread
    ''', out='''
        started
        { value: 2, done: false }
        { value: 1, done: false }
        { value: 'liftoff', done: true }
        { value: undefined, done: true }
        started
        [ 3, 2, 1 ]
    ''')
    yield section("Lazy and infinite sequences", "infinity")
    yield snippet("js", '''
        function* fibonacci() {
          let [a, b] = [0, 1];
          while (true) {
            yield a;
            [a, b] = [b, a + b];
          }
        }
        const out = [];
        for (const f of fibonacci()) {
          if (f > 50) break;          // break calls gen.return() — clean exit
          out.push(f);
        }
        console.log(out.join(" "));

        function* take(iter, n) { for (const x of iter) { if (n-- <= 0) return; yield x; } }
        console.log([...take(fibonacci(), 5)]);
    ''', out='''
        0 1 1 2 3 5 8 13 21 34
        [ 0, 1, 1, 2, 3 ]
    ''')
    yield section("Two-way communication", "arrows-exchange")
    yield snippet("js", '''
        function* conversation() {
          const name = yield "What's your name?";
          const lang = yield `Hi ${name}! Favourite language?`;
          return `${name} likes ${lang}`;
        }
        const chat = conversation();
        console.log(chat.next().value);             // runs to the first yield
        console.log(chat.next("Asha").value);       // "Asha" becomes the result of that yield
        console.log(chat.next("JavaScript"));
    ''', out='''
        What's your name?
        Hi Asha! Favourite language?
        { value: 'Asha likes JavaScript', done: true }
    ''')
    yield section("`yield*` delegation and generator methods", "sitemap")
    yield snippet("js", '''
        class Tree {
          constructor(value, children = []) { this.value = value; this.children = children; }
          *[Symbol.iterator]() {               // depth-first traversal
            yield this.value;
            for (const child of this.children) yield* child;
          }
        }
        const tree = new Tree("root", [new Tree("a", [new Tree("a1")]), new Tree("b")]);
        console.log([...tree]);
    ''', out="[ 'root', 'a', 'a1', 'b' ]")
    yield table(
        ["Method", "Effect"],
        ["`gen.next(v)`", "Resume; `v` becomes the value of the paused `yield`"],
        ["`gen.return(v)`", "Finish early (runs `finally` blocks)"],
        ["`gen.throw(err)`", "Throw `err` at the paused `yield` (catchable inside)"],
    )
    yield qa("What is the difference between a generator and a normal function?",
             "A normal function runs to completion when called. A generator function returns an iterator immediately without running; each `next()` runs it until the next `yield`, keeping its local state between calls. That makes it ideal for lazy sequences, custom iterators and (historically) async flow control.")


@topic(G, "regex", "Regular Expressions", "regex")
def _():
    yield lead("Patterns for searching, validating and transforming text. Write them as literals `/pattern/flags` or with `new RegExp(string, flags)`.")
    yield section("Syntax cheat sheet", "list")
    yield table(
        ["Token", "Matches"],
        ["`.`", "Any char except newline (any char with the `s` flag)"],
        ["`\\d \\w \\s`", "Digit, word char `[A-Za-z0-9_]`, whitespace — uppercase negates"],
        ["`[abc]`, `[^abc]`, `[a-z]`", "Character class, negated class, range"],
        ["`^` `$` `\\b`", "Start, end (per line with `m`), word boundary"],
        ["`* + ? {n,m}`", "0+, 1+, 0–1, n to m — add `?` for lazy (`*?`)"],
        ["`(…)` `(?<name>…)` `(?:…)`", "Capture group, named group, non-capturing group"],
        ["`a|b`", "Alternation"],
        ["`(?=…)` `(?!…)` `(?<=…)` `(?<!…)`", "Lookahead, negative lookahead, lookbehind, negative lookbehind"],
    )
    yield table(
        ["Flag", "Meaning"],
        ["`g`", "Global — all matches"],
        ["`i`", "Case-insensitive"],
        ["`m`", "Multiline `^`/`$`"],
        ["`s`", "`.` matches newlines (dotAll)"],
        ["`u` / `v`", "Unicode mode / Unicode sets (ES2024)"],
        ["`y`", "Sticky — match at `lastIndex` only"],
        ["`d`", "Record match indices"],
    )
    yield section("The main methods", "code")
    yield snippet("js", '''
        const text = "Order #123 shipped on 2024-03-15, order #456 on 2024-04-01.";
        console.log(/order/i.test(text));
        console.log(text.match(/#\\d+/));              // first match + details
        console.log(text.match(/#\\d+/g));             // all matches (no details)
        console.log(text.search(/\\d{4}/));
        console.log(text.replace(/(\\d{4})-(\\d{2})-(\\d{2})/g, "$3/$2/$1"));
        console.log("a1b22c333".split(/\\d+/));
    ''', out='''
        true
        [
          '#123',
          index: 6,
          input: 'Order #123 shipped on 2024-03-15, order #456 on 2024-04-01.',
          groups: undefined
        ]
        [ '#123', '#456' ]
        22
        Order #123 shipped on 15/03/2024, order #456 on 01/04/2024.
        [ 'a', 'b', 'c', '' ]
    ''')
    yield section("Named groups and matchAll", "brackets-contain")
    yield snippet("js", '''
        const log = "user=asha id=7; user=ravi id=12";
        const re = /user=(?<name>\\w+) id=(?<id>\\d+)/g;
        for (const m of log.matchAll(re)) {
          console.log(m.groups.name, Number(m.groups.id), m.index);
        }
        const { year, month } = "2024-09".match(/(?<year>\\d{4})-(?<month>\\d{2})/).groups;
        console.log(year, month);
    ''', out='''
        asha 7 0
        ravi 12 16
        2024 09
    ''')
    yield section("Greedy vs lazy, lookarounds", "eye")
    yield snippet("js", '''
        const html = "<b>bold</b> and <i>italic</i>";
        console.log(html.match(/<.+>/)[0]);       // greedy: as much as possible
        console.log(html.match(/<.+?>/)[0]);      // lazy: as little as possible
        console.log("1234567.89".replace(/\\B(?=(\\d{3})+(?!\\d))/g, ","));
        console.log("price: $30, €40".match(/(?<=\\$)\\d+/)[0]);
        const strong = /^(?=.*[A-Z])(?=.*\\d)(?=.*[^\\w\\s]).{8,}$/;
        console.log(strong.test("Passw0rd!"), strong.test("password"));
    ''', out='''
        <b>bold</b> and <i>italic</i>
        <b>
        1,234,567.89
        30
        true false
    ''')
    yield section("The `lastIndex` trap", "alert-triangle")
    yield snippet("js", '''
        const re = /a/g;
        console.log(re.test("a"), re.test("a"), re.test("a"));
    ''', out="true false true")
    yield warn("A regex with `g` or `y` is **stateful**: `test`/`exec` continue from `lastIndex`. Reusing one global regex across calls gives alternating results. Drop the `g` for `test`, or reset `re.lastIndex = 0`.")
    yield section("Dynamic patterns", "variable")
    yield snippet("js", '''
        const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&");
        const term = "a.b";
        console.log(new RegExp(term).test("axb"), new RegExp(escapeRegExp(term)).test("axb"));
        console.log(new RegExp(`^${escapeRegExp("1+1")}$`).source);
    ''', out='''
        true false
        ^1\\+1$
    ''')
    yield qa("What does the g flag change?",
             "With `g`, `match` returns all matches (without groups), `replace` replaces every match, `matchAll` requires it, and `test`/`exec` become stateful via `lastIndex`. Without it, only the first match is considered.")


@topic(G, "dates-intl", "Dates & Intl", "calendar")
def _():
    yield lead("`Date` stores a single number — milliseconds since 1 Jan 1970 UTC — and has an awkward API. `Intl` formats dates, numbers and lists for any locale; `Temporal` is the modern replacement arriving now.")
    yield section("Creating dates", "calendar-plus")
    yield snippet("js", '''
        const epoch = new Date(0);
        console.log(epoch.toISOString());
        const utc = new Date(Date.UTC(2024, 0, 31, 12, 30));   // months are 0-based!
        console.log(utc.toISOString(), utc.getTime());
        console.log(new Date("2024-02-29T10:00:00Z").toISOString());
        console.log(new Date("not a date").getTime(), String(new Date("nope")));
    ''', out='''
        1970-01-01T00:00:00.000Z
        2024-01-31T12:30:00.000Z 1706704200000
        2024-02-29T10:00:00.000Z
        NaN Invalid Date
    ''')
    yield warn("Months are **0-based** (`0` = January) but days are 1-based. Date-only strings like `\"2024-01-15\"` are parsed as **UTC**, while `\"2024-01-15T10:00\"` (no zone) is **local** time. Always store and send ISO strings with `Z` or an offset.")
    yield section("Reading and doing arithmetic", "calculator")
    yield snippet("js", '''
        const d = new Date(Date.UTC(2024, 0, 31));
        console.log(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), d.getUTCDay());
        d.setUTCMonth(d.getUTCMonth() + 1);        // Jan 31 + 1 month → overflows!
        console.log(d.toISOString().slice(0, 10));

        const a = new Date("2024-03-01T00:00:00Z"), b = new Date("2024-03-15T00:00:00Z");
        const days = (b - a) / (1000 * 60 * 60 * 24);   // subtraction → milliseconds
        console.log(days, a < b);
        const addDays = (date, n) => new Date(date.getTime() + n * 86_400_000);
        console.log(addDays(a, 10).toISOString());
    ''', out='''
        2024 0 31 3
        2024-03-02
        14 true
        2024-03-11T00:00:00.000Z
    ''')
    yield note("`Date` objects are **mutable** — `setX` methods change them in place. Copy first: `new Date(d)`. Adding fixed milliseconds ignores daylight-saving shifts; for calendar maths use `Temporal` or a library (date-fns, Luxon, Day.js).")
    yield section("Formatting with Intl", "world")
    yield snippet("js", '''
        const when = new Date(Date.UTC(2024, 6, 4, 15, 5));
        const opts = { dateStyle: "long", timeStyle: "short", timeZone: "UTC" };
        console.log(new Intl.DateTimeFormat("en-US", opts).format(when));
        console.log(new Intl.DateTimeFormat("en-GB", opts).format(when));
        console.log(when.toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata", weekday: "short", day: "numeric", month: "short" }));

        console.log(new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(1234567.5));
        console.log(new Intl.NumberFormat("en-US", { notation: "compact" }).format(2_500_000));
        console.log(new Intl.NumberFormat("en-US", { style: "percent" }).format(0.256));
        const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
        console.log(rtf.format(-1, "day"), "|", rtf.format(3, "week"));
        console.log(new Intl.ListFormat("en", { type: "conjunction" }).format(["JS", "CSS", "HTML"]));
        console.log(new Intl.PluralRules("en", { type: "ordinal" }).select(22));
    ''', out='''
        July 4, 2024 at 3:05 PM
        4 July 2024 at 15:05
        Thu, 4 Jul
        ₹12,34,567.50
        2.5M
        26%
        yesterday | in 3 weeks
        JS, CSS, and HTML
        two
    ''')
    yield section("Temporal (the future of dates)", "clock-hour-4")
    yield p("`Temporal` (Stage 3, shipping in browsers from 2025–26) replaces `Date` with immutable, zone-aware types: `Temporal.PlainDate`, `PlainTime`, `ZonedDateTime`, `Instant`, `Duration`. Month numbers start at 1, and arithmetic like `date.add({ months: 1 })` is calendar-correct.")
    yield snippet("js", '''
        // Temporal isn't enabled by default in Node 24 — shown for reference.
        const d = Temporal.PlainDate.from("2024-01-31");
        console.log(d.add({ months: 1 }).toString());   // 2024-02-29 (clamped, not overflowed)
    ''', run=False)
    yield qa("How do you compare two dates?",
             "Compare their timestamps: `a.getTime() === b.getTime()` for equality (`===` on Date objects compares references), and `<`/`>` or subtraction for ordering, since Dates coerce to their millisecond value.")
