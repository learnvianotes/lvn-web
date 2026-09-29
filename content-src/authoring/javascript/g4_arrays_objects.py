from kit import *

G = "Arrays & Objects"


@topic(G, "arrays", "Arrays", "brackets")
def _():
    yield lead("Arrays are ordered, zero-indexed, dynamically sized lists that can hold any mix of values. Under the hood they are objects with numeric keys and a magic `length`.")
    yield section("Creating arrays", "plus")
    yield snippet("js", '''
        const a = [1, "two", { three: 3 }, [4]];
        console.log(a, a.length);
        console.log(Array.of(7), Array(3), Array(3).fill(0));
        console.log(Array.from("abc"), Array.from({ length: 4 }, (_, i) => i * i));
        console.log([..."hi"], Array.from(new Set([1, 1, 2])));
    ''', out='''
        [ 1, 'two', { three: 3 }, [ 4 ] ] 4
        [ 7 ] [ <3 empty items> ] [ 0, 0, 0 ]
        [ 'a', 'b', 'c' ] [ 0, 1, 4, 9 ]
        [ 'h', 'i' ] [ 1, 2 ]
    ''')
    yield warn("`Array(3)` creates 3 *holes* (empty slots), not 3 `undefined`s — and `map` skips holes. Use `Array.from({ length: 3 }, fn)` or `Array(3).fill(x)`.")
    yield section("Adding and removing", "arrows-left-right")
    yield table(
        ["Method", "Where", "Mutates?", "Returns"],
        ["`push(x)` / `pop()`", "End", "Yes", "new length / removed item"],
        ["`unshift(x)` / `shift()`", "Start (O(n))", "Yes", "new length / removed item"],
        ["`splice(i, n, ...items)`", "Anywhere", "Yes", "array of removed items"],
        ["`slice(i, j)`", "Copy a range", "No", "new array"],
        ["`concat(...arrs)`", "Join", "No", "new array"],
        ["`toSpliced`, `with(i, v)`", "Copying variants (ES2023)", "No", "new array"],
    )
    yield snippet("js", '''
        const arr = ["a", "b", "c", "d"];
        arr.push("e");
        const last = arr.pop();
        arr.unshift("z");
        const first = arr.shift();
        console.log(arr, last, first);

        const removed = arr.splice(1, 2, "X", "Y", "Z");   // at 1: remove 2, insert 3
        console.log(arr, removed);
        console.log(arr.slice(1, 3), arr.slice(-2), arr.with(0, "!"), arr[0]);
    ''', out='''
        [ 'a', 'b', 'c', 'd' ] e z
        [ 'a', 'X', 'Y', 'Z', 'd' ] [ 'b', 'c' ]
        [ 'X', 'Y' ] [ 'Z', 'd' ] [ '!', 'X', 'Y', 'Z', 'd' ] a
    ''')
    yield section("`length` is writable", "ruler")
    yield snippet("js", '''
        const nums = [1, 2, 3, 4, 5];
        nums.length = 2;                 // truncates
        console.log(nums);
        nums[5] = 6;                     // creates holes
        console.log(nums, nums.length);
        console.log(nums.at(-1), nums[nums.length - 1]);
    ''', out='''
        [ 1, 2 ]
        [ 1, 2, <3 empty items>, 6 ] 6
        6 6
    ''')
    yield section("Checking and converting", "checks")
    yield snippet("js", '''
        console.log(Array.isArray([]), typeof []);
        console.log([1, [2, 3]].toString(), String([null, undefined, 1]));
        console.log([3, 1, 2].join(" < "), "a-b-c".split("-"));
    ''', out='''
        true object
        1,2,3 ,,1
        3 < 1 < 2 [ 'a', 'b', 'c' ]
    ''')
    yield qa("How do you empty an array?",
             "`arr.length = 0` (mutates — every reference sees an empty array), `arr.splice(0)` (mutates, returns the removed items), or `arr = []` (rebinds only this variable; other references keep the old contents).")


@topic(G, "array-methods", "map, filter & reduce", "arrows-shuffle")
def _():
    yield lead("The three workhorses of functional JavaScript: transform every item, keep some items, fold everything into one value — without mutating the original.")
    yield section("map — transform each element", "arrow-right")
    yield snippet("js", '''
        const prices = [10, 20, 30];
        const withTax = prices.map((p) => p * 1.1);
        console.log(withTax.map((p) => p.toFixed(2)));
        const users = [{ name: "Asha", age: 28 }, { name: "Ravi", age: 17 }];
        console.log(users.map(({ name }) => name));
        console.log(users.map((u, i) => `${i + 1}. ${u.name}`));
    ''', out='''
        [ '11.00', '22.00', '33.00' ]
        [ 'Asha', 'Ravi' ]
        [ '1. Asha', '2. Ravi' ]
    ''')
    yield section("filter — keep what passes the test", "filter")
    yield snippet("js", '''
        const nums = [5, 12, 8, 130, 44];
        console.log(nums.filter((n) => n > 10));
        const mixed = [0, "a", null, "", 7, undefined, false];
        console.log(mixed.filter(Boolean));          // remove falsy values
        const unique = [1, 2, 2, 3, 1].filter((x, i, arr) => arr.indexOf(x) === i);
        console.log(unique);
    ''', out='''
        [ 12, 130, 44 ]
        [ 'a', 7 ]
        [ 1, 2, 3 ]
    ''')
    yield section("reduce — fold into a single value", "arrows-join")
    yield formula("`array.reduce((accumulator, current, index, array) => newAccumulator, initialValue)`")
    yield snippet("js", '''
        const nums = [1, 2, 3, 4];
        console.log(nums.reduce((sum, n) => sum + n, 0));
        console.log(nums.reduce((max, n) => (n > max ? n : max), -Infinity));

        const words = ["apple", "avocado", "banana", "cherry", "blueberry"];
        const byLetter = words.reduce((groups, w) => {
          (groups[w[0]] ??= []).push(w);
          return groups;
        }, {});
        console.log(byLetter);

        const pairs = [["a", 1], ["b", 2]];
        console.log(pairs.reduce((obj, [k, v]) => ({ ...obj, [k]: v }), {}));
    ''', out='''
        10
        4
        {
          a: [ 'apple', 'avocado' ],
          b: [ 'banana', 'blueberry' ],
          c: [ 'cherry' ]
        }
        { a: 1, b: 2 }
    ''')
    yield warn("Always pass the initial value. Without it, `reduce` uses the first element as the accumulator — and throws `TypeError: Reduce of empty array with no initial value` on `[]`.")
    yield snippet("js", '''
        try {
          [].reduce((a, b) => a + b);
        } catch (e) {
          console.log(e.message);
        }
        console.log([].reduce((a, b) => a + b, 0));
    ''', out='''
        Reduce of empty array with no initial value
        0
    ''')
    yield section("Chaining", "link")
    yield snippet("js", '''
        const orders = [
          { item: "book", qty: 2, price: 12, paid: true },
          { item: "pen", qty: 10, price: 1.5, paid: false },
          { item: "lamp", qty: 1, price: 40, paid: true },
        ];
        const revenue = orders
          .filter((o) => o.paid)
          .map((o) => o.qty * o.price)
          .reduce((sum, v) => sum + v, 0);
        console.log(revenue);
    ''', out="64")
    yield section("forEach and flatMap", "list")
    yield snippet("js", '''
        const out = [];
        const r = ["x", "y"].forEach((v, i) => out.push(v + i));
        console.log(out, r);          // forEach always returns undefined
        const sentences = ["hello world", "hi there"];
        console.log(sentences.flatMap((s) => s.split(" ")));
        console.log([1, 2, 3].flatMap((n) => (n % 2 ? [n, n * 10] : [])));
    ''', out='''
        [ 'x0', 'y1' ] undefined
        [ 'hello', 'world', 'hi', 'there' ]
        [ 1, 10, 3, 30 ]
    ''')
    yield table(
        ["Method", "Returns", "Use when"],
        ["`map`", "New array, same length", "Transforming each item"],
        ["`filter`", "New array, ≤ length", "Selecting items"],
        ["`reduce`", "Any single value", "Sums, grouping, building objects"],
        ["`forEach`", "`undefined`", "Side effects only (logging, DOM)"],
        ["`flatMap`", "New array, flattened one level", "Map where each item yields 0..n items"],
    )
    yield qa("What is the difference between map and forEach?",
             "`map` returns a new array of the callback's return values and is chainable; `forEach` returns `undefined` and exists only for side effects. Neither can be stopped early with `break`.")
    yield qa("Implement map using reduce.",
             "`const map = (arr, fn) => arr.reduce((acc, x, i) => (acc.push(fn(x, i, arr)), acc), []);` — push each transformed item into the accumulator array.")


@topic(G, "array-search-sort", "Searching, Sorting & Flattening", "sort-ascending")
def _():
    yield lead("Find things, test things, sort things (carefully!) and flatten nested arrays — plus the ES2023 non-mutating copies.")
    yield section("Finding and testing", "search")
    yield table(
        ["Method", "Returns", "Stops early?"],
        ["`find(fn)` / `findLast(fn)`", "First / last matching element or `undefined`", "Yes"],
        ["`findIndex(fn)` / `findLastIndex(fn)`", "Index or `-1`", "Yes"],
        ["`indexOf(x)` / `lastIndexOf(x)`", "Index via `===` or `-1`", "Yes"],
        ["`includes(x)`", "Boolean (finds `NaN`)", "Yes"],
        ["`some(fn)`", "`true` if any passes", "Yes, on first `true`"],
        ["`every(fn)`", "`true` if all pass (`true` for `[]`)", "Yes, on first `false`"],
    )
    yield snippet("js", '''
        const users = [
          { id: 1, name: "Asha", admin: false },
          { id: 2, name: "Ravi", admin: true },
          { id: 3, name: "Mei", admin: true },
        ];
        console.log(users.find((u) => u.admin).name, users.findLast((u) => u.admin).name);
        console.log(users.findIndex((u) => u.id === 3), users.find((u) => u.id === 9));
        console.log(users.some((u) => u.admin), users.every((u) => u.admin));
        console.log([].every((x) => x > 100), [].some((x) => x > 100));
        console.log([1, 2, NaN].includes(NaN), [1, 2, NaN].indexOf(NaN));
    ''', out='''
        Ravi Mei
        2 undefined
        true false
        true false
        true -1
    ''')
    yield section("Sorting — the big pitfall", "alert-triangle")
    yield snippet("js", '''
        const nums = [10, 1, 5, 100, 25];
        console.log([...nums].sort());                 // compares as STRINGS
        console.log([...nums].sort((a, b) => a - b));  // numeric ascending
        console.log([...nums].sort((a, b) => b - a));  // descending
    ''', out='''
        [ 1, 10, 100, 25, 5 ]
        [ 1, 5, 10, 25, 100 ]
        [ 100, 25, 10, 5, 1 ]
    ''')
    yield warn("`sort()` with no comparator converts elements to strings and compares UTF-16 code units. It also **mutates** the array in place (and returns the same array). Use `toSorted` for a copy.")
    yield p("The comparator returns a negative number if `a` goes first, positive if `b` goes first, `0` to keep order. Since ES2019 the sort is **stable**, so equal items keep their relative order — which lets you sort by several keys.")
    yield snippet("js", '''
        const people = [
          { name: "Zoe", dept: "HR", age: 30 },
          { name: "adam", dept: "Eng", age: 25 },
          { name: "Émile", dept: "Eng", age: 35 },
          { name: "Bob", dept: "HR", age: 25 },
        ];
        const byDeptThenAge = people.toSorted(
          (a, b) => a.dept.localeCompare(b.dept) || a.age - b.age
        );
        console.log(byDeptThenAge.map((p) => `${p.dept}:${p.name}`).join(" "));
        const names = people.map((p) => p.name);
        console.log(names.toSorted());
        console.log(names.toSorted((a, b) => a.localeCompare(b)));
        console.log(people[0].name);   // original untouched by toSorted
    ''', out='''
        Eng:adam Eng:Émile HR:Bob HR:Zoe
        [ 'Bob', 'Zoe', 'adam', 'Émile' ]
        [ 'adam', 'Bob', 'Émile', 'Zoe' ]
        Zoe
    ''')
    yield section("Mutating vs copying (ES2023)", "copy")
    yield table(
        ["Mutates", "Non-mutating copy"],
        ["`sort(fn)`", "`toSorted(fn)`"],
        ["`reverse()`", "`toReversed()`"],
        ["`splice(i, n, …)`", "`toSpliced(i, n, …)`"],
        ["`arr[i] = v`", "`arr.with(i, v)`"],
        ["`fill`, `copyWithin`, `push`, `pop`, `shift`, `unshift`", "spread / `slice` / `concat`"],
    )
    yield section("Flattening", "stack-pop")
    yield snippet("js", '''
        const nested = [1, [2, [3, [4, [5]]]]];
        console.log(nested.flat());
        console.log(nested.flat(2));
        console.log(nested.flat(Infinity));
    ''', out='''
        [ 1, 2, [ 3, [ 4, [Array] ] ] ]
        [ 1, 2, 3, [ 4, [ 5 ] ] ]
        [ 1, 2, 3, 4, 5 ]
    ''')
    yield note("`console.log` shows nested structures only 2 levels deep, printing `[Array]` / `[Object]` beyond that. Use `console.dir(x, { depth: null })` or `JSON.stringify` to see everything.", "Reading the output")
    yield section("Useful one-liners", "wand")
    yield snippet("js", '''
        const arr = [3, 1, 3, 2, 1];
        console.log([...new Set(arr)]);                                  // unique
        console.log(Math.max(...arr), arr.reduce((a, b) => a + b, 0));   // max, sum
        const chunk = (a, n) => Array.from({ length: Math.ceil(a.length / n) }, (_, i) => a.slice(i * n, i * n + n));
        console.log(chunk([1, 2, 3, 4, 5], 2));
        const zip = (a, b) => a.map((x, i) => [x, b[i]]);
        console.log(zip(["a", "b"], [1, 2]));
        console.log([1, 2, 3, 4].filter((x) => [2, 4, 6].includes(x)));  // intersection
    ''', out='''
        [ 3, 1, 2 ]
        3 10
        [ [ 1, 2 ], [ 3, 4 ], [ 5 ] ]
        [ [ 'a', 1 ], [ 'b', 2 ] ]
        [ 2, 4 ]
    ''')
    yield qa("Why does [10, 1, 5].sort() return [1, 10, 5]?",
             "Without a comparator, `sort` converts elements to strings and compares them lexicographically: `'10' < '5'` because `'1' < '5'`. Pass `(a, b) => a - b` for numbers.")
    yield qa("find vs filter?",
             "`find` returns the first matching element (or `undefined`) and stops searching; `filter` scans everything and returns an array of all matches (possibly empty).")


@topic(G, "objects", "Objects", "braces")
def _():
    yield lead("Objects are collections of key → value properties. Keys are strings or symbols; values can be anything, including functions (methods).")
    yield section("Object literals, modern syntax", "code")
    yield snippet("js", '''
        const name = "Asha", age = 28;
        const field = "email";
        const user = {
          name,                                  // shorthand for name: name
          age,
          [field]: "asha@example.com",           // computed key
          [`is${"Admin"}`]: false,
          "full name": "Asha Rao",               // any string can be a key
          greet() { return `Hi, ${this.name}`; },  // method shorthand
        };
        console.log(user);
        console.log(user.greet(), user["full name"], user[field]);
    ''', out='''
        {
          name: 'Asha',
          age: 28,
          email: 'asha@example.com',
          isAdmin: false,
          'full name': 'Asha Rao',
          greet: [Function: greet]
        }
        Hi, Asha Asha Rao asha@example.com
    ''')
    yield section("Reading, writing, deleting, checking", "edit")
    yield snippet("js", '''
        const car = { brand: "Tata", year: 2020 };
        car.color = "red";           // add
        car.year = 2021;             // update
        delete car.brand;            // remove
        console.log(car);
        console.log("color" in car, Object.hasOwn(car, "color"), car.speed);
        console.log("toString" in car, Object.hasOwn(car, "toString"));
    ''', out='''
        { year: 2021, color: 'red' }
        true true undefined
        true false
    ''')
    yield table(
        ["Check", "Own props", "Inherited props", "Value `undefined` counts?"],
        ["`obj.key !== undefined`", "Yes", "Yes", "No — misses explicit `undefined`"],
        ["`'key' in obj`", "Yes", "Yes", "Yes"],
        ["`Object.hasOwn(obj, 'key')`", "Yes", "No", "Yes"],
    )
    yield section("Keys are strings (or symbols)", "key")
    yield snippet("js", '''
        const obj = {};
        obj[1] = "number key";
        obj[{}] = "object key";
        console.log(Object.keys(obj), obj["1"]);
        const order = { b: 1, 2: "two", a: 2, 1: "one" };
        console.log(Object.keys(order));
    ''', out='''
        [ '1', '[object Object]' ] number key
        [ '1', '2', 'b', 'a' ]
    ''')
    yield note("Property order: integer-like keys first in ascending order, then string keys in insertion order, then symbols. Need real non-string keys? Use a `Map`.")
    yield section("Getters and setters", "arrows-exchange")
    yield snippet("js", '''
        const temperature = {
          celsius: 25,
          get fahrenheit() {
            return this.celsius * 9 / 5 + 32;
          },
          set fahrenheit(f) {
            this.celsius = Math.round((f - 32) * 5 / 9);
          },
        };
        console.log(temperature.fahrenheit);
        temperature.fahrenheit = 212;
        console.log(temperature.celsius, temperature);
    ''', out='''
        77
        100 { celsius: 100, fahrenheit: [Getter/Setter] }
    ''')
    yield section("Iterating an object", "repeat")
    yield snippet("js", '''
        const scores = { math: 90, art: 75, music: 88 };
        for (const [subject, score] of Object.entries(scores)) {
          console.log(`${subject.padEnd(6)} ${score}`);
        }
        const total = Object.values(scores).reduce((a, b) => a + b, 0);
        console.log(total, Object.keys(scores).length);
    ''', out='''
        math   90
        art    75
        music  88
        253 3
    ''')
    yield qa("How do you check if an object is empty?",
             "`Object.keys(obj).length === 0` (own enumerable string keys). For a stricter check include symbols and non-enumerables: `Reflect.ownKeys(obj).length === 0`.")
    yield qa("Difference between dot and bracket notation?",
             "Dot needs a valid identifier known when writing the code (`obj.name`). Brackets take any expression evaluated at runtime (`obj[key]`, `obj['full name']`, `obj[sym]`).")


@topic(G, "property-descriptors", "Property Descriptors, freeze & seal", "lock")
def _():
    yield lead("Every property has hidden attributes — writable, enumerable, configurable — that control whether it can change, show up in loops, or be deleted.")
    yield section("Inspecting descriptors", "search")
    yield snippet("js", '''
        const obj = { visible: 1 };
        console.log(Object.getOwnPropertyDescriptor(obj, "visible"));
        Object.defineProperty(obj, "secret", { value: 42 });   // attributes default to false!
        console.log(Object.getOwnPropertyDescriptor(obj, "secret"));
        console.log(obj, Object.keys(obj), obj.secret);
    ''', out='''
        { value: 1, writable: true, enumerable: true, configurable: true }
        { value: 42, writable: false, enumerable: false, configurable: false }
        { visible: 1 } [ 'visible' ] 42
    ''')
    yield table(
        ["Attribute", "When `false`"],
        ["`writable`", "The value cannot be reassigned (throws in strict mode)"],
        ["`enumerable`", "Hidden from `for…in`, `Object.keys`, spread and `JSON.stringify`"],
        ["`configurable`", "Cannot be deleted, and its attributes cannot be changed (except writable → false)"],
        ["`get` / `set`", "Accessor property instead of a data property (no `value`/`writable`)"],
    )
    yield snippet("js", '''
        const account = {};
        Object.defineProperty(account, "id", { value: "AC-1", enumerable: true });
        try {
          account.id = "hacked";
        } catch (e) {
          console.log(e.message);
        }
        try {
          delete account.id;
        } catch (e) {
          console.log(e.message);
        }
        console.log(account.id);
    ''', out='''
        Cannot assign to read only property 'id' of object '#<Object>'
        Cannot delete property 'id' of #<Object>
        AC-1
    ''')
    yield section("preventExtensions, seal, freeze", "lock-square")
    yield table(
        ["", "Add props", "Delete props", "Change values", "Check"],
        ["`Object.preventExtensions`", "No", "Yes", "Yes", "`Object.isExtensible`"],
        ["`Object.seal`", "No", "No", "Yes", "`Object.isSealed`"],
        ["`Object.freeze`", "No", "No", "No", "`Object.isFrozen`"],
    )
    yield snippet("js", '''
        const sealed = Object.seal({ a: 1 });
        sealed.a = 2;
        try { sealed.b = 3; } catch (e) { console.log("seal:", e.message); }

        const frozen = Object.freeze({ a: 1, nested: { b: 1 } });
        try { frozen.a = 2; } catch (e) { console.log("freeze:", e.message); }
        frozen.nested.b = 99;                 // freeze is SHALLOW
        console.log(sealed, frozen, Object.isFrozen(frozen.nested));
    ''', out='''
        seal: Cannot add property b, object is not extensible
        freeze: Cannot assign to read only property 'a' of object '#<Object>'
        { a: 2 } { a: 1, nested: { b: 99 } } false
    ''')
    yield note("In sloppy mode these writes fail **silently**; in strict mode (modules, classes) they throw a `TypeError`.")
    yield section("Deep freeze", "snowflake")
    yield snippet("js", '''
        function deepFreeze(obj) {
          for (const value of Object.values(obj)) {
            if (value && typeof value === "object") deepFreeze(value);
          }
          return Object.freeze(obj);
        }
        const config = deepFreeze({ db: { host: "localhost", ports: [5432] } });
        try {
          config.db.ports.push(1);
        } catch (e) {
          console.log(e.message);
        }
    ''', out="Cannot add property 1, object is not extensible")
    yield qa("What is the difference between Object.freeze and const?",
             "`const` prevents reassigning the *variable*; the object stays mutable. `Object.freeze` makes the *object's* own properties read-only and non-extensible — but only one level deep, and it says nothing about the variable.")
    yield qa("seal vs freeze?",
             "Both prevent adding and deleting properties. `seal` still allows changing existing values; `freeze` also makes every existing data property read-only.")


@topic(G, "destructuring", "Destructuring", "package-export")
def _():
    yield lead("Unpack values from arrays and properties from objects into variables — with defaults, renaming, rest and nesting.")
    yield section("Array destructuring (by position)", "brackets")
    yield snippet("js", '''
        const rgb = [255, 128, 0, 0.5];
        const [red, green, , alpha = 1] = rgb;       // skip with a hole
        console.log(red, green, alpha);
        const [head, ...tail] = "hello";             // any iterable
        console.log(head, tail);
        let a = 1, b = 2;
        [a, b] = [b, a];                             // swap without a temp
        console.log(a, b);
        const [x = 10, y = 20] = [undefined, null];  // default only for undefined
        console.log(x, y);
    ''', out='''
        255 128 0.5
        h [ 'e', 'l', 'l', 'o' ]
        2 1
        10 null
    ''')
    yield section("Object destructuring (by name)", "braces")
    yield snippet("js", '''
        const user = { id: 7, name: "Asha", address: { city: "Pune", zip: "411001" } };
        const { name, role = "member", id: userId } = user;          // default + rename
        const { address: { city }, ...rest } = user;                 // nested + rest
        console.log(name, role, userId, city);
        console.log(rest);
        const key = "zip";
        const { [key]: zipCode } = user.address;                     // computed key
        console.log(zipCode);
    ''', out='''
        Asha member 7 Pune
        { id: 7, name: 'Asha' }
        411001
    ''')
    yield section("In function parameters and loops", "function")
    yield snippet("js", '''
        const format = ({ first, last = "", title = "" } = {}) => `${title} ${first} ${last}`.trim();
        console.log(format({ first: "Ada", last: "Lovelace", title: "Countess" }));
        console.log(format({ first: "Linus" }));

        const entries = Object.entries({ a: 1, b: 2 });
        for (const [key, value] of entries) console.log(key, value);
        const points = [{ x: 1, y: 2 }, { x: 3, y: 4 }];
        console.log(points.map(({ x, y }) => x + y));
    ''', out='''
        Countess Ada Lovelace
        Linus
        a 1
        b 2
        [ 3, 7 ]
    ''')
    yield section("Pitfalls", "alert-triangle")
    yield snippet("js", '''
        try {
          const { a } = null;
        } catch (e) {
          console.log(e.constructor.name);
        }
        let value;
        ({ value } = { value: 5 });   // parentheses needed when not declaring
        console.log(value);
    ''', out='''
        TypeError
        5
    ''')
    yield ul(
        "Destructuring `null` or `undefined` throws — give parameters a default `= {}`.",
        "An assignment without `let`/`const` must be wrapped in `( )`, otherwise `{` starts a block.",
        "Defaults apply only for `undefined`, never for `null`.",
    )
    yield qa("How do you swap two variables without a temporary?",
             "`[a, b] = [b, a];` — the right side builds a temporary array, which is destructured back into the two names.")


@topic(G, "object-static-methods", "Object Static Methods", "list-details")
def _():
    yield lead("The `Object` constructor carries the toolbox for inspecting, copying, converting and grouping objects.")
    yield table(
        ["Method", "Does"],
        ["`Object.keys / values / entries(o)`", "Own enumerable string keys / values / `[key, value]` pairs"],
        ["`Object.fromEntries(iterable)`", "Pairs → object (inverse of `entries`)"],
        ["`Object.assign(target, ...src)`", "Copy own enumerable props into `target` (mutates, shallow)"],
        ["`Object.create(proto, descriptors?)`", "New object with the given prototype"],
        ["`Object.getPrototypeOf / setPrototypeOf`", "Read / change the prototype"],
        ["`Object.defineProperty / defineProperties`", "Add props with explicit attributes"],
        ["`Object.freeze / seal / preventExtensions`", "Restrict changes"],
        ["`Object.hasOwn(o, k)`", "Own-property check (ES2022)"],
        ["`Object.is(a, b)`", "SameValue equality"],
        ["`Object.groupBy(items, fn)`", "Group into a null-prototype object (ES2024)"],
        ["`Object.getOwnPropertyNames / getOwnPropertySymbols`", "Include non-enumerables / symbols"],
    )
    yield section("entries ⇄ fromEntries: transform an object", "transform")
    yield snippet("js", '''
        const prices = { apple: 1.2, bread: 2.5, milk: 0.99 };
        const doubled = Object.fromEntries(
          Object.entries(prices).map(([k, v]) => [k, v * 2])
        );
        console.log(doubled);
        const cheap = Object.fromEntries(Object.entries(prices).filter(([, v]) => v < 2));
        console.log(cheap);
        console.log(Object.fromEntries(new Map([["x", 1]])));
        console.log(Object.fromEntries(new URLSearchParams("q=js&page=2")));
    ''', out='''
        { apple: 2.4, bread: 5, milk: 1.98 }
        { apple: 1.2, milk: 0.99 }
        { x: 1 }
        { q: 'js', page: '2' }
    ''')
    yield section("assign vs spread", "copy")
    yield snippet("js", '''
        const defaults = { theme: "light", lang: "en" };
        const user = { lang: "hi" };
        const merged = Object.assign({}, defaults, user);
        const spread = { ...defaults, ...user };
        console.log(merged, spread);
        Object.assign(defaults, { theme: "dark" });   // mutates the target
        console.log(defaults);
    ''', out='''
        { theme: 'light', lang: 'hi' } { theme: 'light', lang: 'hi' }
        { theme: 'dark', lang: 'en' }
    ''')
    yield note("Later sources win. `Object.assign` *invokes setters* on the target; spread defines fresh properties. Both are shallow copies.")
    yield section("Object.groupBy (ES2024)", "category")
    yield snippet("js", '''
        const inventory = [
          { name: "asparagus", type: "veg", qty: 5 },
          { name: "banana", type: "fruit", qty: 0 },
          { name: "goat", type: "meat", qty: 23 },
          { name: "cherry", type: "fruit", qty: 5 },
        ];
        const byType = Object.groupBy(inventory, ({ type }) => type);
        console.log(Object.keys(byType), byType.fruit.length);
        const stock = Map.groupBy(inventory, ({ qty }) => (qty > 0 ? "ok" : "restock"));
        console.log(stock.get("restock"));
    ''', out='''
        [ 'veg', 'fruit', 'meat' ] 2
        [ { name: 'banana', type: 'fruit', qty: 0 } ]
    ''')
    yield section("Object.create", "sparkles")
    yield snippet("js", '''
        const animal = { speak() { return `${this.name} makes a sound`; } };
        const dog = Object.create(animal);
        dog.name = "Rex";
        console.log(dog.speak(), Object.getPrototypeOf(dog) === animal);
        const dict = Object.create(null);          // no prototype at all
        dict.key = "v";
        console.log("toString" in dict, dict);
    ''', out='''
        Rex makes a sound true
        false [Object: null prototype] { key: 'v' }
    ''')
    yield qa("Object.keys vs Object.getOwnPropertyNames vs Reflect.ownKeys?",
             "`Object.keys` → own **enumerable** string keys. `getOwnPropertyNames` → own string keys including non-enumerable. `Reflect.ownKeys` → all own keys, strings and symbols, enumerable or not.")


@topic(G, "json", "JSON", "json")
def _():
    yield lead("JSON is a text format for data, borrowed from JavaScript literal syntax. `JSON.stringify` serialises, `JSON.parse` deserialises — each with a hook for customisation.")
    yield section("JSON vs JavaScript objects", "file-code")
    yield table(
        ["JSON", "JavaScript object literal"],
        ["Keys **must** be double-quoted strings", "Keys can be bare identifiers"],
        ["Strings in double quotes only", "`'single'`, `\"double\"` and backtick templates"],
        ["Values: string, number, boolean, `null`, object, array", "Also functions, `undefined`, symbols, BigInt, Date, Map…"],
        ["No trailing commas, no comments", "Trailing commas allowed"],
    )
    yield section("stringify", "arrow-right")
    yield snippet("js", '''
        const data = {
          name: "Asha",
          tags: ["js", "node"],
          born: new Date(Date.UTC(1995, 11, 4)),
          skip: undefined,
          fn() {},
          sym: Symbol("s"),
          nan: NaN,
          inf: Infinity,
        };
        console.log(JSON.stringify(data));
        console.log(JSON.stringify([undefined, () => {}, NaN]));
        console.log(JSON.stringify({ a: 1, b: [1, 2] }, null, 2));
    ''', out='''
        {"name":"Asha","tags":["js","node"],"born":"1995-12-04T00:00:00.000Z","nan":null,"inf":null}
        [null,null,null]
        {
          "a": 1,
          "b": [
            1,
            2
          ]
        }
    ''')
    yield warn("Silently lost: `undefined`, functions and symbols (dropped in objects, `null` in arrays); `NaN`/`Infinity` become `null`; `Date` becomes a string; `Map`/`Set` become `{}`. BigInt **throws**. Circular references **throw**.")
    yield section("Replacer, toJSON and reviver", "adjustments")
    yield snippet("js", '''
        const user = { name: "Ravi", password: "hunter2", age: 30 };
        console.log(JSON.stringify(user, ["name", "age"]));
        console.log(JSON.stringify(user, (k, v) => (k === "password" ? undefined : v)));

        class Money {
          constructor(cents) { this.cents = cents; }
          toJSON() { return `$${(this.cents / 100).toFixed(2)}`; }
        }
        console.log(JSON.stringify({ total: new Money(1999) }));

        const text = '{"when":"2024-01-15T10:00:00.000Z","n":1}';
        const parsed = JSON.parse(text, (k, v) => (k === "when" ? new Date(v) : v));
        console.log(parsed.when instanceof Date, parsed.when.getUTCFullYear());
    ''', out='''
        {"name":"Ravi","age":30}
        {"name":"Ravi","age":30}
        {"total":"$19.99"}
        true 2024
    ''')
    yield section("Errors", "alert-circle")
    yield snippet("js", '''
        try {
          JSON.parse("{name: 'x'}");
        } catch (e) {
          console.log(e.name);
        }
        const a = { name: "loop" };
        a.self = a;
        try {
          JSON.stringify(a);
        } catch (e) {
          console.log(e.message.split("\\n")[0]);
        }
        try {
          JSON.stringify({ n: 1n });
        } catch (e) {
          console.log(e.message);
        }
    ''', out='''
        SyntaxError
        Converting circular structure to JSON
        Do not know how to serialize a BigInt
    ''')
    yield good("Always wrap `JSON.parse` of external input in `try/catch`, and validate the shape of what you get (a schema library like Zod) — valid JSON is not necessarily valid data.")
    yield qa("Is JSON.parse(JSON.stringify(obj)) a good deep clone?",
             "Only for plain JSON-safe data. It drops `undefined`/functions/symbols, turns Dates into strings, Maps/Sets into `{}`, `NaN` into `null`, loses prototypes, and throws on BigInt and cycles. Use `structuredClone` instead.")


@topic(G, "copying", "Immutability & Copying", "copy")
def _():
    yield lead("Assignment copies references. To copy data you choose between a shallow copy (top level only) and a deep copy (everything) — and immutable updates build new objects instead of mutating old ones.")
    yield section("Shallow copies share nested objects", "stack-2")
    yield snippet("js", '''
        const original = { name: "Asha", skills: ["js"], meta: { level: 1 } };
        const shallow = { ...original };
        shallow.name = "Ravi";          // top level: independent
        shallow.skills.push("css");     // nested: SHARED
        shallow.meta.level = 99;
        console.log(original);
        console.log(shallow.skills === original.skills);
    ''', out='''
        { name: 'Asha', skills: [ 'js', 'css' ], meta: { level: 99 } }
        true
    ''')
    yield table(
        ["Shallow copy tools", "Arrays", "Objects"],
        ["Spread", "`[...arr]`", "`{...obj}`"],
        ["Built-ins", "`arr.slice()`, `Array.from(arr)`, `arr.concat()`", "`Object.assign({}, obj)`"],
    )
    yield section("Deep copy with structuredClone", "copy-check")
    yield snippet("js", '''
        const original = {
          when: new Date(0),
          tags: new Set(["a"]),
          lookup: new Map([["k", { deep: true }]]),
          nested: { list: [1, [2, 3]] },
        };
        original.self = original;              // cycles are fine
        const clone = structuredClone(original);
        clone.nested.list[1].push(4);
        console.log(original.nested.list, clone.nested.list);
        console.log(clone.when instanceof Date, clone.tags, clone.self === clone);
    ''', out='''
        [ 1, [ 2, 3 ] ] [ 1, [ 2, 3, 4 ] ]
        true Set(1) { 'a' } true
    ''')
    yield snippet("js", '''
        class Point { constructor(x) { this.x = x; } norm() { return Math.abs(this.x); } }
        const copy = structuredClone(new Point(-3));
        console.log(copy, copy instanceof Point);
        try {
          structuredClone({ fn() {} });
        } catch (e) {
          console.log(e.name);
        }
    ''', out='''
        { x: -3 } false
        DataCloneError
    ''')
    yield table(
        ["Method", "Dates / Map / Set", "Cycles", "Functions", "Class instances"],
        ["Spread / `assign`", "shared refs (shallow)", "shared", "copied (ref)", "prototype lost for spread"],
        ["`JSON.parse(JSON.stringify())`", "Date → string, Map/Set → `{}`", "throws", "dropped", "plain object"],
        ["`structuredClone`", "✔ preserved", "✔", "throws `DataCloneError`", "plain object (prototype lost)"],
        ["Custom recursive / lodash `cloneDeep`", "✔", "✔ (with a map)", "kept by reference", "configurable"],
    )
    yield section("Immutable update patterns", "refresh")
    yield snippet("js", '''
        const state = { user: { name: "Asha", prefs: { theme: "light" } }, todos: [{ id: 1, done: false }] };

        const next = {
          ...state,
          user: { ...state.user, prefs: { ...state.user.prefs, theme: "dark" } },
          todos: state.todos.map((t) => (t.id === 1 ? { ...t, done: true } : t)),
        };
        console.log(state.user.prefs.theme, next.user.prefs.theme);
        console.log(state.todos[0].done, next.todos[0].done);
        console.log(state.user === next.user, state === next);
    ''', out='''
        light dark
        false true
        false false
    ''')
    yield note("Immutable updates copy only the *path* that changed and share the rest (structural sharing). That lets React, Redux and memoisation detect changes with a cheap `===`.", "Why it matters")
    yield table(
        ["Instead of (mutating)", "Write (immutable)"],
        ["`arr.push(x)`", "`[...arr, x]`"],
        ["`arr.splice(i, 1)`", "`arr.filter((_, j) => j !== i)` or `arr.toSpliced(i, 1)`"],
        ["`arr[i] = v`", "`arr.with(i, v)` or `arr.map(...)`"],
        ["`arr.sort()`", "`arr.toSorted()`"],
        ["`obj.k = v`", "`{ ...obj, k: v }`"],
        ["`delete obj.k`", "`const { k, ...rest } = obj`"],
    )
    yield qa("Shallow copy vs deep copy?",
             "A shallow copy duplicates only the top level; nested objects are still shared with the original. A deep copy recursively duplicates everything, so the copies are fully independent. Use spread for shallow, `structuredClone` for deep.")
