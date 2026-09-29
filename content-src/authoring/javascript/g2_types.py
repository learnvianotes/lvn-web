from kit import *

G = "Types, Values & Operators"


@topic(G, "type-coercion", "Type Coercion & == vs ===", "transform")
def _():
    yield lead("JavaScript silently converts values when an operator expects another type. Learn the three conversions (to string, number, boolean) and `==` stops being magic.")
    yield define("Type coercion", "automatic (implicit) conversion of a value from one type to another by an operator — as opposed to *explicit* conversion with `String(x)`, `Number(x)`, `Boolean(x)`.")
    yield section("Explicit conversion", "hand-finger")
    yield snippet("js", '''
        console.log(String(123), String(null), String([1, 2]), String({}));
        console.log(Number("42"), Number(""), Number("  7  "), Number("4px"));
        console.log(Number(true), Number(null), Number(undefined), Number([]), Number([5]));
        console.log(parseInt("4px"), parseFloat("3.5em"), parseInt("0x1F"), parseInt("101", 2));
        console.log(Boolean(""), Boolean("0"), Boolean([]), Boolean(0));
    ''', out='''
        123 null 1,2 [object Object]
        42 0 7 NaN
        1 0 NaN 0 5
        4 3.5 31 5
        false true true false
    ''')
    yield table(
        ["Value", "`Number(v)`", "`String(v)`", "`Boolean(v)`"],
        ["`undefined`", "`NaN`", "`\"undefined\"`", "`false`"],
        ["`null`", "`0`", "`\"null\"`", "`false`"],
        ["`true` / `false`", "`1` / `0`", "`\"true\"` / `\"false\"`", "same"],
        ["`\"\"`", "`0`", "`\"\"`", "`false`"],
        ["`\"12abc\"`", "`NaN`", "same", "`true`"],
        ["`[]`", "`0`", "`\"\"`", "`true`"],
        ["`{}`", "`NaN`", "`\"[object Object]\"`", "`true`"],
    )
    yield section("Implicit coercion by operators", "math-symbols")
    yield ul(
        "`+` with **any string** operand → string concatenation. Otherwise numeric addition.",
        "`- * / % **` and unary `+` → always numeric.",
        "`if`, `!`, `&&`, `||`, `? :` → boolean (truthiness).",
        "Objects are first turned into primitives via `Symbol.toPrimitive`, then `valueOf()`, then `toString()`.",
    )
    yield snippet("js", '''
        console.log(1 + "2", "3" - 1, "3" * "4", +"5", +"");
        console.log(true + 1, null + 1, undefined + 1);
        console.log([] + [], [] + {}, [1, 2] + [3]);
        console.log(1 + 2 + "3", "1" + 2 + 3);
    ''', out='''
        12 2 12 5 0
        2 1 NaN
         [object Object] 1,23
        33 123
    ''')
    yield note("Evaluation is left to right: `1 + 2 + \"3\"` is `3 + \"3\"` → `\"33\"`, while `\"1\" + 2 + 3` is `\"12\" + 3` → `\"123\"`.")
    yield section("`==` (loose) vs `===` (strict)", "equal")
    yield cards(
        ("`===` strict equality", "No conversion: different types → `false`. Objects: same reference. The only surprise: `NaN !== NaN`.", "equal-double"),
        ("`==` loose equality", "Converts first: `null == undefined` (and nothing else), otherwise booleans → numbers, strings → numbers, objects → primitives.", "equal"),
    )
    yield snippet("js", '''
        console.log(0 == "", 0 == "0", "" == "0");
        console.log(false == "0", false == [], null == 0, null == undefined);
        console.log([1] == 1, [1, 2] == "1,2", NaN == NaN);
        console.log(0 === "", null === undefined, 1 === 1.0);
    ''', out='''
        true true false
        true true false true
        true true false
        false false true
    ''')
    yield warn("`==` is not transitive: `0 == \"\"` and `0 == \"0\"` but `\"\" != \"0\"`. Always use `===` — except `x == null`, a handy check for *null or undefined*.")
    yield section("`Object.is` — SameValue", "fingerprint")
    yield snippet("js", '''
        console.log(NaN === NaN, Object.is(NaN, NaN));
        console.log(0 === -0, Object.is(0, -0));
        console.log([NaN].includes(NaN), [NaN].indexOf(NaN));
    ''', out='''
        false true
        true false
        true -1
    ''')
    yield table(
        ["Algorithm", "Used by", "`NaN` vs `NaN`", "`0` vs `-0`"],
        ["Strict (`===`)", "`===`, `indexOf`, `switch`", "not equal", "equal"],
        ["SameValueZero", "`includes`, `Map`/`Set` keys", "equal", "equal"],
        ["SameValue", "`Object.is`", "equal", "not equal"],
    )
    yield section("Objects to primitives", "box")
    yield snippet("js", '''
        const price = {
          valueOf() { return 42; },
          toString() { return "$42"; },
        };
        console.log(price + 1, `${price}`, price > 40);

        const temp = {
          [Symbol.toPrimitive](hint) {
            return hint === "number" ? 21 : hint === "string" ? "21°C" : "default";
          },
        };
        console.log(+temp, `${temp}`, temp + "");
    ''', out='''
        43 $42 true
        21 21°C default
    ''')
    yield qa("What is the difference between == and ===?",
             "`===` compares without type conversion (and objects by identity). `==` first coerces operands to a common type using the abstract equality rules — `null == undefined`, booleans and strings become numbers, objects become primitives. Prefer `===`; `x == null` is the common exception.")
    yield qa("What does [] + {} evaluate to?",
             "`\"[object Object]\"`. Both are converted to primitives: `[]` → `\"\"`, `{}` → `\"[object Object]\"`, and `+` with a string concatenates. (Typed at the start of a line in a console, `{}` may be parsed as an empty block, which is why `{} + []` can show `0`.)")


@topic(G, "truthy-falsy", "Truthy & Falsy Values", "toggle-left")
def _():
    yield lead("In a boolean context every value is either truthy or falsy — and there are only eight falsy values to memorise.")
    yield section("The complete falsy list", "list")
    yield chips("`false`", "`0`", "`-0`", "`0n`", "`\"\"` (empty string)", "`null`", "`undefined`", "`NaN`")
    yield p("**Everything else is truthy** — including `\"0\"`, `\"false\"`, `\" \"`, `[]`, `{}`, `function(){}`, `Infinity` and `new Boolean(false)`.")
    yield snippet("js", '''
        import { inspect } from "node:util";
        const values = [0, -0, "", null, undefined, NaN, 0n, "0", "false", " ", [], {}, -1];
        for (const v of values) {
          console.log(inspect(v).padEnd(9), "→", Boolean(v));
        }
    ''', out='''
        0         → false
        -0        → false
        ''        → false
        null      → false
        undefined → false
        NaN       → false
        0n        → false
        '0'       → true
        'false'   → true
        ' '       → true
        []        → true
        {}        → true
        -1        → true
    ''')
    yield section("Using truthiness", "code")
    yield snippet("js", '''
        const items = [];
        if (items.length) console.log("has items");
        else console.log("empty array (length 0 is falsy)");

        const name = "";
        console.log(name || "Anonymous");
        console.log(!!"text", !!0);
    ''', out='''
        empty array (length 0 is falsy)
        Anonymous
        true false
    ''')
    yield warn("`[]` and `{}` are truthy. Check emptiness explicitly: `arr.length === 0`, `Object.keys(obj).length === 0`.")
    yield section("`||` vs `??` for defaults", "arrows-split")
    yield snippet("js", '''
        const settings = { volume: 0, title: "" };
        console.log(settings.volume || 50, settings.volume ?? 50);
        console.log(settings.title || "Untitled", settings.title ?? "Untitled");
        console.log(settings.missing ?? "default");
    ''', out='''
        50 0
        Untitled
        default
    ''')
    yield note("`||` falls back on **any falsy** value (so a real `0` or `\"\"` is lost). `??` falls back only on `null`/`undefined` — usually what you want for defaults.")
    yield qa("List the falsy values in JavaScript.",
             "`false`, `0`, `-0`, `0n`, `\"\"`, `null`, `undefined`, `NaN`. (Browsers also have the legacy `document.all`.) Everything else, including empty arrays and objects, is truthy.")


@topic(G, "numbers", "Numbers, Math & BigInt", "number")
def _():
    yield lead("One `number` type for integers and decimals — a 64-bit IEEE 754 double — plus `BigInt` for arbitrarily large integers.")
    yield section("Floating-point reality", "alert-triangle")
    yield snippet("js", '''
        console.log(0.1 + 0.2);
        console.log(0.1 + 0.2 === 0.3);
        console.log(Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON);
        console.log((0.1 + 0.2).toFixed(2), Math.round(1.005 * 100) / 100);
    ''', out='''
        0.30000000000000004
        false
        true
        0.30 1
    ''')
    yield note("0.1 has no exact binary representation (like 1/3 in decimal). Compare floats with a tolerance, and do money in **integer cents** (or `BigInt`, or a decimal library).", "Money rule")
    yield section("Special values", "infinity")
    yield snippet("js", '''
        console.log(1 / 0, -1 / 0, 0 / 0);
        console.log(typeof NaN, NaN === NaN);
        console.log(isNaN("abc"), Number.isNaN("abc"));
        console.log(Number.isFinite("5"), isFinite("5"));
        console.log(Number.MAX_SAFE_INTEGER, Number.isSafeInteger(2 ** 53));
        console.log(2 ** 53 === 2 ** 53 + 1);
    ''', out='''
        Infinity -Infinity NaN
        number false
        true false
        false true
        9007199254740991 false
        true
    ''')
    yield table(
        ["Global (coerces)", "`Number.*` (no coercion) — prefer these"],
        ["`isNaN(\"abc\")` → `true`", "`Number.isNaN(\"abc\")` → `false`"],
        ["`isFinite(\"5\")` → `true`", "`Number.isFinite(\"5\")` → `false`"],
        ["`parseInt`, `parseFloat`", "`Number.parseInt`, `Number.parseFloat` (identical)"],
    )
    yield section("Formatting and parsing", "123")
    yield snippet("js", '''
        const n = 1234.5678;
        console.log(n.toFixed(2), n.toPrecision(3), (255).toString(16), (5).toString(2));
        console.log(Number("1_000"), 1_000_000, 0xff, 0b1010, 0o17, 1e3);
        console.log((1234567.891).toLocaleString("en-US"));
        console.log((1234567.891).toLocaleString("de-DE"));
    ''', out='''
        1234.57 1.23e+3 ff 101
        NaN 1000000 255 10 15 1000
        1,234,567.891
        1.234.567,891
    ''')
    yield section("The `Math` object", "math-function")
    yield table(
        ["Method", "Result"],
        ["`Math.round(2.5)`, `Math.round(-2.5)`", "`3`, `-2` (rounds half toward +∞)"],
        ["`Math.floor(-1.5)`, `Math.ceil(-1.5)`, `Math.trunc(-1.5)`", "`-2`, `-1`, `-1`"],
        ["`Math.max(...arr)`, `Math.min()`", "largest; `Math.min()` with no args is `Infinity`"],
        ["`Math.abs`, `Math.sign`, `Math.sqrt`, `Math.cbrt`, `Math.hypot`", "the usual"],
        ["`Math.random()`", "float in `[0, 1)` — **not** cryptographically secure"],
    )
    yield snippet("js", '''
        console.log(Math.round(2.5), Math.round(-2.5), Math.trunc(-1.7), Math.floor(-1.7));
        console.log(Math.max(3, 9, 1), Math.max(...[4, 8]), Math.max(), Math.min());
        console.log(Math.hypot(3, 4), 2 ** 10, 7 % 3, -7 % 3);
        const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
        const r = randInt(1, 6);
        console.log(r >= 1 && r <= 6 && Number.isInteger(r));
    ''', out='''
        3 -2 -1 -2
        9 8 -Infinity Infinity
        5 1024 1 -1
        true
    ''')
    yield warn("`%` is a *remainder*, not a modulo: its sign follows the dividend (`-7 % 3 === -1`). For a true modulo use `((n % m) + m) % m`.")
    yield section("BigInt", "numbers")
    yield snippet("js", '''
        const big = 2n ** 64n;
        console.log(big, typeof big);
        console.log(9007199254740993n + 1n, 9007199254740993 + 1);
        console.log(7n / 2n, BigInt("123") * 2n, 5n == 5, 5n === 5);
        try {
          console.log(1n + 1);
        } catch (e) {
          console.log(e.name + ": " + e.message);
        }
    ''', out='''
        18446744073709551616n bigint
        9007199254740994n 9007199254740992
        3n 246n true false
        TypeError: Cannot mix BigInt and other types, use explicit conversions
    ''')
    yield ul(
        "BigInt division truncates (`7n / 2n === 3n`); no decimals.",
        "Cannot mix with `number` in arithmetic — convert with `BigInt(n)` or `Number(b)`.",
        "Not usable with `Math.*`; `JSON.stringify` throws on BigInt unless you add a `toJSON`.",
    )
    yield qa("Why is 0.1 + 0.2 !== 0.3?",
             "Numbers are IEEE 754 binary doubles; 0.1 and 0.2 cannot be represented exactly, so their sum is `0.30000000000000004`. Compare with a tolerance (`Math.abs(a - b) < Number.EPSILON`) or work in integers.")
    yield qa("What is Number.MAX_SAFE_INTEGER?",
             "`2^53 − 1` (9007199254740991) — the largest integer where every integer below it is exactly representable. Beyond it, `n + 1` may equal `n`; use `BigInt`.")


@topic(G, "strings", "Strings & Template Literals", "quote")
def _():
    yield lead("Strings are immutable sequences of UTF-16 code units. Template literals give interpolation, multi-line text and tagged templates.")
    yield section("Three ways to write a string", "quote")
    yield snippet("js", '''
        const single = 'single';
        const double = "double";
        const name = "Asha";
        const tpl = `Hi ${name}, 2 + 3 = ${2 + 3}, upper: ${name.toUpperCase()}`;
        console.log(single, double);
        console.log(tpl);
        const multi = `line 1
        line 2`;
        console.log(multi);
    ''', out='''
        single double
        Hi Asha, 2 + 3 = 5, upper: ASHA
        line 1
        line 2
    ''')
    yield section("Indexing and immutability", "cut")
    yield snippet("js", '''
        const s = "JavaScript";
        console.log(s.length, s[0], s.at(-1), s.charAt(4), s[99]);
        console.log(s.slice(0, 4), s.slice(-6), s.substring(4, 0));
        console.log(s.charCodeAt(0), String.fromCharCode(74));
    ''', out='''
        10 J t S undefined
        Java Script Java
        74 J
    ''')
    yield section("Unicode gotcha", "mood-smile")
    yield snippet("js", '''
        const emoji = "😀";
        console.log(emoji.length, [...emoji].length);
        console.log("héllo".length, "héllo".normalize("NFD").length);
        const flag = "👍🏽";
        console.log(flag.length, [...flag].length);
    ''', out='''
        2 1
        5 6
        4 2
    ''')
    yield note("`.length` counts **UTF-16 code units**, not characters. Emoji outside the Basic Multilingual Plane take 2 units; `[...str]` iterates by *code point*. For user-perceived characters use `Intl.Segmenter`.")
    yield section("Escapes and raw strings", "slash")
    yield snippet("js", '''
        console.log("tab:\\tend", "quote: \\"", 'it\\'s');
        console.log("\\u0041\\u{1F600}");
        console.log(String.raw`C:\\new\\table`);
    ''', out='''
        tab:	end quote: " it's
        A😀
        C:\\new\\table
    ''')
    yield section("Tagged templates", "tag")
    yield p("A **tag** is a function called with the literal's string pieces and the interpolated values — used by `String.raw`, styled-components, GraphQL `gql`, SQL builders and HTML escapers.")
    yield snippet("js", '''
        function highlight(strings, ...values) {
          return strings.reduce(
            (out, str, i) => out + str + (i < values.length ? `[${values[i]}]` : ""),
            ""
          );
        }
        const item = "coffee", price = 3.5;
        console.log(highlight`One ${item} costs $${price}.`);

        function show(strings, ...values) {
          console.log(strings, values);
        }
        show`a${1}b${2}`;
    ''', out='''
        One [coffee] costs $[3.5].
        [ 'a', 'b', '' ] [ 1, 2 ]
    ''')
    yield qa("Why is \"😀\".length equal to 2?",
             "JS strings are UTF-16. Code points above U+FFFF are stored as a *surrogate pair* of two code units, and `.length` counts code units. Spread (`[...s]`) or `for…of` iterate by code point.")


@topic(G, "string-methods", "String Methods", "letter-case")
def _():
    yield lead("Every string method returns a new string (or a value) — the original never changes.")
    yield section("Cheat sheet", "list")
    yield table(
        ["Method", "Purpose", "Example → result"],
        ["`includes / startsWith / endsWith`", "Search → boolean", "`'hello'.startsWith('he')` → `true`"],
        ["`indexOf / lastIndexOf`", "Position or `-1`", "`'banana'.indexOf('a')` → `1`"],
        ["`slice(start, end)`", "Substring; negatives count from end", "`'hello'.slice(-3)` → `'llo'`"],
        ["`toUpperCase / toLowerCase`", "Case", "`'Hi'.toUpperCase()` → `'HI'`"],
        ["`trim / trimStart / trimEnd`", "Remove whitespace", "`'  x '.trim()` → `'x'`"],
        ["`padStart / padEnd`", "Pad to a length", "`'5'.padStart(3, '0')` → `'005'`"],
        ["`repeat(n)`", "Repeat", "`'ab'.repeat(3)` → `'ababab'`"],
        ["`split(sep)`", "String → array", "`'a,b'.split(',')` → `['a', 'b']`"],
        ["`replace / replaceAll`", "Substitute (string or regex)", "`'a-a'.replaceAll('-', '+')`"],
        ["`at(i)`", "Index with negatives", "`'abc'.at(-1)` → `'c'`"],
        ["`localeCompare`", "Locale-aware compare for sorting", "`'a'.localeCompare('b')` → `-1`"],
    )
    yield section("In action", "code")
    yield snippet("js", '''
        const text = "  The quick brown fox  ";
        const t = text.trim();
        console.log(`[${t}]`, t.length);
        console.log(t.includes("quick"), t.indexOf("o"), t.lastIndexOf("o"));
        console.log(t.split(" "), t.split(" ", 2));
        console.log(t.replace("o", "0"), "|", t.replaceAll("o", "0"));
        console.log(t.replace(/o/g, (m) => m.toUpperCase()));
        console.log("7".padStart(3, "0"), "ab".padEnd(5, "."), "=".repeat(5));
    ''', out='''
        [The quick brown fox] 19
        true 12 17
        [ 'The', 'quick', 'brown', 'fox' ] [ 'The', 'quick' ]
        The quick br0wn fox | The quick br0wn f0x
        The quick brOwn fOx
        007 ab... =====
    ''')
    yield warn("`replace` with a **string** pattern replaces only the *first* match. Use `replaceAll`, or a regex with the `g` flag.")
    yield section("Common interview manipulations", "puzzle")
    yield snippet("js", '''
        const reverse = (s) => [...s].reverse().join("");
        const isPalindrome = (s) => {
          const clean = s.toLowerCase().replace(/[^a-z0-9]/g, "");
          return clean === reverse(clean);
        };
        const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);
        const titleCase = (s) => s.split(" ").map(capitalize).join(" ");
        const countChars = (s) =>
          [...s].reduce((acc, ch) => ({ ...acc, [ch]: (acc[ch] ?? 0) + 1 }), {});

        console.log(reverse("hello"));
        console.log(isPalindrome("A man, a plan, a canal: Panama"));
        console.log(titleCase("learn via notes"));
        console.log(countChars("banana"));
    ''', out='''
        olleh
        true
        Learn Via Notes
        { b: 1, a: 3, n: 2 }
    ''')
    yield section("substring vs slice vs substr", "cut")
    yield table(
        ["Method", "Negative indices", "start > end", "Status"],
        ["`slice(s, e)`", "Count from end", "Returns `''`", "Use this"],
        ["`substring(s, e)`", "Treated as `0`", "Swaps the arguments", "OK"],
        ["`substr(s, len)`", "Start may be negative", "Second arg is a *length*", "Deprecated"],
    )
    yield qa("How do you reverse a string in JavaScript?",
             "`[...s].reverse().join('')`. Strings have no `reverse`, so convert to an array first; spread (rather than `split('')`) keeps emoji and other surrogate pairs intact.")


@topic(G, "operators", "Operators", "math-symbols")
def _():
    yield lead("Beyond arithmetic: short-circuit logic that returns operands, optional chaining, nullish coalescing, logical assignment and spread.")
    yield section("Operator families", "table")
    yield table(
        ["Kind", "Operators"],
        ["Arithmetic", "`+ - * / % **`, `++ --`"],
        ["Assignment", "`= += -= *= /= %= **=`, `&&= ||= ??=`"],
        ["Comparison", "`=== !== == != < > <= >=`"],
        ["Logical", "`&& || !`, `??`"],
        ["Bitwise", "`& | ^ ~ << >> >>>`"],
        ["Other", "`?.`, `? :`, `typeof`, `instanceof`, `in`, `delete`, `void`, `,`, `...`"],
    )
    yield section("`&&` and `||` return an operand", "arrows-split")
    yield snippet("js", '''
        console.log("a" && "b", 0 && "b", "a" || "b", "" || "b");
        console.log(null || undefined || 0);
        const user = { name: "Kai" };
        user && console.log("logged in as", user.name);   // guard idiom
    ''', out='''
        b 0 a b
        0
        logged in as Kai
    ''')
    yield p("`a && b` returns `a` if it is falsy, else `b`. `a || b` returns `a` if truthy, else `b`. Both **short-circuit**: the right side is not evaluated when unnecessary.")
    yield section("Optional chaining `?.` and nullish coalescing `??`", "question-mark")
    yield snippet("js", '''
        const order = { customer: { address: null }, items: [], total() { return 42; } };
        console.log(order.customer?.address?.city);
        console.log(order.shipping?.method ?? "standard");
        console.log(order.items?.[0], order.total?.(), order.refund?.());
        console.log(order.customer.address?.city.toUpperCase());  // stops at null
    ''', out='''
        undefined
        standard
        undefined 42 undefined
        undefined
    ''')
    yield warn("`??` cannot be mixed with `||`/`&&` without parentheses: `a || b ?? c` is a SyntaxError. Write `(a || b) ?? c`.")
    yield section("Logical assignment (ES2021)", "equal")
    yield snippet("js", '''
        const opts = { retries: 0, name: "", cache: null };
        opts.retries ||= 3;   // assigns if falsy
        opts.name &&= opts.name.trim();  // assigns if truthy
        opts.cache ??= new Map();        // assigns if null/undefined
        opts.timeout ??= 1000;
        console.log(opts);
    ''', out='''
        { retries: 3, name: '', cache: Map(0) {}, timeout: 1000 }
    ''')
    yield section("Spread and rest `...`", "dots")
    yield snippet("js", '''
        const a = [1, 2], b = [3, 4];
        console.log([...a, ...b], Math.max(...b));
        const base = { x: 1, y: 2 };
        console.log({ ...base, y: 20, z: 3 });
        function sum(...nums) { return nums.reduce((s, n) => s + n, 0); }
        const [first, ...others] = [10, 20, 30];
        console.log(sum(1, 2, 3), first, others);
    ''', out='''
        [ 1, 2, 3, 4 ] 4
        { x: 1, y: 20, z: 3 }
        6 10 [ 20, 30 ]
    ''')
    yield note("Same syntax, opposite jobs: **spread** expands an iterable/object *into* places; **rest** collects remaining items *into* an array/object (parameters, destructuring).")
    yield section("Increment, exponent and a few odd ones", "plus-minus")
    yield snippet("js", '''
        let i = 5;
        console.log(i++, i, ++i);
        console.log(2 ** 3 ** 2, (2 ** 3) ** 2);
        console.log("x" in { x: undefined }, void 0, (1, 2, 3));
        console.log(5 & 3, 5 | 3, 5 ^ 3, ~5, 1 << 4, -16 >> 2, -16 >>> 28);
    ''', out='''
        5 6 7
        512 64
        true undefined 3
        1 7 6 -6 16 -4 15
    ''')
    yield table(
        ["Precedence (high → low)", "Examples"],
        ["Grouping, member, call", "`( )`, `.`, `?.`, `[]`, `f()`, `new`"],
        ["Postfix / prefix / unary", "`x++`, `!`, `typeof`, `-x`"],
        ["Exponent (right-assoc.)", "`**`"],
        ["Multiplicative → additive", "`* / %` then `+ -`"],
        ["Relational → equality", "`< > in instanceof` then `== ===`"],
        ["Logical", "`&&` then `||` then `??`"],
        ["Conditional, assignment, comma", "`? :`, `= += ??=`, `,`"],
    )
    yield qa("What is the difference between || and ???",
             "`||` returns the right side when the left is *falsy* (`0`, `''`, `false`, `NaN`, `null`, `undefined`). `??` only when the left is `null` or `undefined`, so valid values like `0` and `''` are kept.")


@topic(G, "control-flow", "Control Flow & Loops", "git-branch")
def _():
    yield lead("`if`/`else`, `switch`, the ternary, five kinds of loop, and `break`/`continue` with labels.")
    yield section("Conditionals", "arrows-split-2")
    yield snippet("js", '''
        const grade = (score) => {
          if (score >= 90) return "A";
          else if (score >= 75) return "B";
          else return "C";
        };
        console.log(grade(95), grade(80), grade(10));
        const age = 20;
        console.log(age >= 18 ? "adult" : "minor");
    ''', out='''
        A B C
        adult
    ''')
    yield section("`switch` uses strict equality and falls through", "switch")
    yield snippet("js", '''
        function kind(day) {
          switch (day) {
            case "sat":
            case "sun":
              return "weekend";
            case 1:
              return "number one";
            default:
              return "weekday";
          }
        }
        console.log(kind("sun"), kind("mon"), kind(1), kind("1"));

        let log = [];
        switch (2) {
          case 1: log.push(1);
          case 2: log.push(2);   // no break → falls through
          case 3: log.push(3);
            break;
          case 4: log.push(4);
        }
        console.log(log);
    ''', out='''
        weekend weekday number one weekday
        [ 2, 3 ]
    ''')
    yield section("Loops", "repeat")
    yield table(
        ["Loop", "Iterates over", "Use for"],
        ["`for (init; cond; step)`", "a counter", "index-based work, early exit"],
        ["`while (cond)`", "until the condition fails", "unknown number of iterations"],
        ["`do { } while (cond)`", "at least once", "prompts / retries"],
        ["`for (const x of iterable)`", "**values** of arrays, strings, maps, sets, generators", "the default for arrays"],
        ["`for (const k in object)`", "enumerable **keys** (incl. inherited) as strings", "plain objects only"],
        ["`arr.forEach(fn)`", "array elements", "side effects; cannot `break`"],
    )
    yield snippet("js", '''
        const arr = ["a", "b"];
        arr.extra = "!";
        for (const i in arr) console.log("in:", i, typeof i);
        for (const v of arr) console.log("of:", v);
        for (const [i, v] of arr.entries()) console.log(i, v);
        for (const ch of "hi") console.log(ch);
    ''', out='''
        in: 0 string
        in: 1 string
        in: extra string
        of: a
        of: b
        0 a
        1 b
        h
        i
    ''')
    yield warn("Never use `for…in` on arrays: keys are strings, order is not guaranteed by intent, and it also visits extra/inherited enumerable properties. Use `for…of`.")
    yield section("while / do…while", "rotate")
    yield snippet("js", '''
        let n = 1;
        while (n < 100) n *= 3;
        console.log(n);
        let tries = 0;
        do {
          tries++;
        } while (false);
        console.log(tries);
    ''', out='''
        243
        1
    ''')
    yield section("break, continue and labels", "player-skip-forward")
    yield snippet("js", '''
        for (let i = 0; i < 6; i++) {
          if (i === 1) continue;
          if (i === 4) break;
          console.log(i);
        }
        outer: for (let r = 0; r < 3; r++) {
          for (let c = 0; c < 3; c++) {
            if (c === 1) continue outer;
            if (r === 2) break outer;
            console.log(`r${r}c${c}`);
          }
        }
    ''', out='''
        0
        2
        3
        r0c0
        r1c0
    ''')
    yield qa("What is the difference between for...in and for...of?",
             "`for…in` iterates over the enumerable *property keys* (strings) of an object, including inherited ones. `for…of` iterates over the *values* produced by an iterable (arrays, strings, Map, Set, generators). Use `for…of` for arrays and `Object.entries(obj)` with `for…of` for objects.")
    yield qa("Can you break out of forEach?",
             "No — `break` is a syntax error inside the callback and `return` only skips to the next element. Use `for…of`, or `some`/`every`/`find`, which stop early.")
