from kit import *

G = "Asynchronous JavaScript"


@topic(G, "event-loop", "The Event Loop", "refresh-dot")
def _():
    yield lead("One thread, one call stack — and a loop that, whenever the stack is empty, drains *all* microtasks and then takes the next macrotask. Predicting output order is a top interview skill.")
    yield section("The moving parts", "components")
    yield cards(
        ("Call stack", "Where synchronous code runs, one frame at a time. Nothing else runs until it is empty.", "stack"),
        ("Web / runtime APIs", "Timers, network, file I/O, DOM events — handled outside the JS thread by the browser or libuv (Node).", "server"),
        ("Macrotask (task) queue", "`setTimeout`, `setInterval`, `setImmediate`, I/O callbacks, UI events, `MessageChannel`.", "list"),
        ("Microtask queue", "Promise reactions (`then`/`catch`/`finally`, code after `await`), `queueMicrotask`, `MutationObserver`. Node's `process.nextTick` has its own even-higher-priority queue.", "bolt"),
    )
    yield section("One turn of the loop", "rotate-clockwise")
    yield steps(
        ("Run a task", "Take the oldest macrotask (the initial script is the first) and run it to completion."),
        ("Drain microtasks", "Run **every** microtask — including ones queued while draining — until the queue is empty."),
        ("Render (browsers)", "If it's time for a frame: `requestAnimationFrame` callbacks, style, layout, paint."),
        ("Repeat", "Pick the next macrotask."),
    )
    yield section("Predict the output", "puzzle")
    yield snippet("js", '''
        console.log("1: sync start");
        setTimeout(() => console.log("6: timeout (macrotask)"), 0);
        Promise.resolve()
          .then(() => console.log("3: promise then (microtask)"))
          .then(() => console.log("5: chained then (microtask)"));
        queueMicrotask(() => console.log("4: queueMicrotask"));
        console.log("2: sync end");
    ''', out='''
        1: sync start
        2: sync end
        3: promise then (microtask)
        4: queueMicrotask
        5: chained then (microtask)
        6: timeout (macrotask)
    ''')
    yield note("A `setTimeout(fn, 0)` never runs before microtasks queued in the same task. `0` means “as soon as possible after at least 0 ms”, not “now”.")
    yield section("async/await in the ordering", "clock-play")
    yield snippet("js", '''
        async function task() {
          console.log("B: task starts (sync part)");
          await null;                               // everything after this is a microtask
          console.log("E: task resumes after await");
        }
        console.log("A: script start");
        setTimeout(() => console.log("G: timeout"), 0);
        task();
        new Promise((resolve) => {
          console.log("C: executor runs synchronously");
          resolve();
        }).then(() => console.log("F: then"));
        console.log("D: script end");
    ''', out='''
        A: script start
        B: task starts (sync part)
        C: executor runs synchronously
        D: script end
        E: task resumes after await
        F: then
        G: timeout
    ''')
    yield section("Microtasks can starve the loop", "alert-triangle")
    yield snippet("js", '''
        let count = 0;
        setTimeout(() => console.log("timeout finally runs, microtasks ran:", count), 0);
        function spin() {
          if (++count < 1000) queueMicrotask(spin);   // keeps refilling the queue
        }
        queueMicrotask(spin);
    ''', out="timeout finally runs, microtasks ran: 1000")
    yield warn("Because the microtask queue is drained completely, an endless chain of microtasks blocks timers, I/O and rendering just like a `while(true)` loop. Long synchronous work does the same — split it up or move it to a Worker.")
    yield section("Node specifics: nextTick, setImmediate", "brand-nodejs")
    yield table(
        ["Node phase / queue", "Runs"],
        ["`process.nextTick` queue", "After the current operation, before promise microtasks (from CommonJS/callbacks)"],
        ["Promise microtasks", "Right after the nextTick queue"],
        ["timers", "Expired `setTimeout` / `setInterval`"],
        ["poll", "I/O callbacks (fs, network)"],
        ["check", "`setImmediate`"],
        ["close", "`'close'` events"],
    )
    yield snippet("js", '''
        setTimeout(() => {
          console.log("inside a timer callback:");
          setTimeout(() => console.log("  4. setTimeout 0 (next timers phase)"), 0);
          setImmediate(() => console.log("  3. setImmediate (check phase comes first)"));
          Promise.resolve().then(() => console.log("  2. promise microtask"));
          process.nextTick(() => console.log("  1. process.nextTick"));
        }, 0);
    ''', out='''
        inside a timer callback:
          1. process.nextTick
          2. promise microtask
          3. setImmediate (check phase comes first)
          4. setTimeout 0 (next timers phase)
    ''')
    yield note("At the top level of an **ES module** the module body itself runs as part of a promise job, so there a `.then` callback can run before a `process.nextTick` — one reason not to depend on nextTick-vs-promise ordering.", "ESM subtlety")
    yield qa("What is the difference between microtasks and macrotasks?",
             "Macrotasks (timers, I/O, events) are taken one per loop turn. Microtasks (promise reactions, `queueMicrotask`) run right after the current task and the whole queue is drained before the next macrotask or render. So promise callbacks always beat a `setTimeout(…, 0)` scheduled at the same time.")
    yield qa("If JavaScript is single-threaded, how does it do async work?",
             "The engine is single-threaded, but the runtime is not: timers, network and disk I/O run in the browser or libuv thread pool. When they finish, their callbacks are queued, and the event loop runs them on the main thread when the call stack is empty.")


@topic(G, "callbacks", "Callbacks & Callback Hell", "phone-call")
def _():
    yield lead("The original async pattern: pass a function to be called when the work is done. Simple — until you nest five of them.")
    yield section("Error-first callbacks (Node convention)", "alert-circle")
    yield snippet("js", '''
        function readUser(id, callback) {
          setTimeout(() => {
            if (id <= 0) callback(new Error("invalid id"));
            else callback(null, { id, name: "User" + id });
          }, 10);
        }
        readUser(7, (err, user) => {
          if (err) return console.log("failed:", err.message);
          console.log("got", user);
        });
        readUser(-1, (err, user) => {
          if (err) return console.log("failed:", err.message);
          console.log("got", user);
        });
    ''', out='''
        got { id: 7, name: 'User7' }
        failed: invalid id
    ''')
    yield section("Callback hell (the pyramid of doom)", "stairs-down")
    yield snippet("js", '''
        const step = (name, cb) => setTimeout(() => cb(null, name), 5);
        step("login", (err, a) => {
          step("load profile", (err, b) => {
            step("load orders", (err, c) => {
              step("render", (err, d) => {
                console.log([a, b, c, d].join(" → "));
              });
            });
          });
        });
    ''', out="login → load profile → load orders → render")
    yield table(
        ["Problem", "Why it hurts"],
        ["Nesting", "Code drifts right; hard to read and refactor"],
        ["Error handling", "Must check `err` at every level; `try/catch` cannot catch errors thrown in later callbacks"],
        ["Inversion of control", "You trust the callee to call you exactly once, not zero or twice, not sync *and* async"],
        ["Composition", "Parallel work, timeouts and \"first one wins\" need hand-written bookkeeping"],
    )
    yield section("Promisify", "transform")
    yield snippet("js", '''
        import { promisify } from "node:util";
        function legacyAdd(a, b, cb) { setTimeout(() => cb(null, a + b), 5); }

        const addAsync = promisify(legacyAdd);
        console.log(await addAsync(2, 3));

        const manual = (a, b) =>
          new Promise((resolve, reject) => legacyAdd(a, b, (err, v) => (err ? reject(err) : resolve(v))));
        console.log(await manual(10, 20));
    ''', out='''
        5
        30
    ''')
    yield qa("What is callback hell and how do you avoid it?",
             "Deeply nested callbacks for sequential async steps, which make code hard to read, reason about and handle errors in. Avoid it with named functions, promises and chaining, and most of all `async`/`await`.")


@topic(G, "promises", "Promises", "circle-dashed-check")
def _():
    yield lead("A Promise is an object representing a value that will be available later — or an error. It is the foundation of modern async JavaScript.")
    yield define("Promise", "an object in one of three states: **pending**, then either **fulfilled** with a value or **rejected** with a reason. Once settled it never changes.")
    yield section("Creating and consuming", "code")
    yield snippet("js", '''
        const wait = (ms, value) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
        const fail = (msg) => new Promise((_, reject) => setTimeout(() => reject(new Error(msg)), 5));

        wait(10, "done").then((v) => console.log("fulfilled:", v));
        fail("boom")
          .then(() => console.log("never runs"))
          .catch((err) => console.log("rejected:", err.message))
          .finally(() => console.log("finally: cleanup either way"));
    ''', out='''
        rejected: boom
        finally: cleanup either way
        fulfilled: done
    ''')
    yield section("Chaining: every then returns a new promise", "link")
    yield snippet("js", '''
        Promise.resolve(2)
          .then((n) => n * 10)                         // return a value → next then gets it
          .then((n) => new Promise((r) => setTimeout(() => r(n + 1), 5)))  // return a promise → waits
          .then((n) => {
            console.log("value:", n);
            throw new Error("oops");                   // throw → skips to the next catch
          })
          .then(() => console.log("skipped"))
          .catch((e) => {
            console.log("caught:", e.message);
            return "recovered";                        // catch can recover the chain
          })
          .then((v) => console.log("after catch:", v));
    ''', out='''
        value: 21
        caught: oops
        after catch: recovered
    ''')
    yield table(
        ["Inside a `then` handler you…", "The returned promise…"],
        ["return a value", "fulfils with that value"],
        ["return a promise/thenable", "adopts its eventual state"],
        ["throw", "rejects with the thrown error"],
        ["return nothing", "fulfils with `undefined`"],
    )
    yield section("Common mistakes", "alert-triangle")
    yield snippet("js", '''
        const getData = () => Promise.resolve({ id: 1 });

        // 1. forgetting to return → the next then gets undefined
        getData()
          .then((d) => { getData(); })
          .then((v) => console.log("forgot return:", v));

        // 2. the executor runs synchronously; resolve only once
        const p = new Promise((resolve) => {
          console.log("executor runs now");
          resolve("first");
          resolve("second");                 // ignored
        });
        p.then((v) => console.log("settled with:", v));
    ''', out='''
        executor runs now
        settled with: first
        forgot return: undefined
    ''')
    yield warn("An unhandled rejection crashes Node (since v15) and logs an error in browsers. Every promise chain needs a `.catch` at the end (or an `await` inside `try/catch`).")
    yield section("Promise.resolve / reject / withResolvers", "tool")
    yield snippet("js", '''
        console.log(await Promise.resolve(42));
        const p = Promise.resolve(Promise.resolve("nested"));   // promises flatten
        console.log(await p);

        const { promise, resolve } = Promise.withResolvers();     // ES2024
        setTimeout(() => resolve("resolved from outside"), 5);
        console.log(await promise);
        await Promise.reject(new Error("x")).catch((e) => console.log("rejected with", e.message));
    ''', out='''
        42
        nested
        resolved from outside
        rejected with x
    ''')
    yield qa("What are the states of a Promise?",
             "Pending, fulfilled and rejected. Fulfilled and rejected are together called *settled*; a settled promise is immutable, and handlers attached later still run (asynchronously) with the settled value.")
    yield qa("Why do promise callbacks run asynchronously even if the promise is already resolved?",
             "Handlers are always queued as microtasks, never called synchronously. This guarantees consistent ordering — code after `.then(...)` always runs before the handler, whether the promise was already settled or not.")


@topic(G, "promise-combinators", "Promise.all, allSettled, race & any", "arrows-join-2")
def _():
    yield lead("Four static methods run many promises concurrently and combine the results — they differ only in *when they settle* and *what counts as failure*.")
    yield table(
        ["Method", "Fulfils when", "Rejects when", "Result"],
        ["`Promise.all`", "**All** fulfil", "**Any** rejects (fail-fast)", "Array of values, in input order"],
        ["`Promise.allSettled`", "All settle", "Never", "Array of `{status, value \\| reason}`"],
        ["`Promise.race`", "The **first to settle** fulfils", "The first to settle rejects", "That one value/reason"],
        ["`Promise.any`", "The **first to fulfil**", "**All** reject", "Value, or `AggregateError`"],
    )
    yield snippet("js", '''
        const ok = (ms, v) => new Promise((res) => setTimeout(() => res(v), ms));
        const bad = (ms, msg) => new Promise((_, rej) => setTimeout(() => rej(new Error(msg)), ms));

        console.log("all:", await Promise.all([ok(30, "a"), ok(10, "b"), 42]));
        await Promise.all([ok(10, "a"), bad(5, "db down")]).catch((e) => console.log("all rejected:", e.message));

        const settled = await Promise.allSettled([ok(5, "a"), bad(5, "nope")]);
        console.log(settled.map((r) => (r.status === "fulfilled" ? r : { ...r, reason: r.reason.message })));

        console.log("race:", await Promise.race([ok(20, "slow"), ok(5, "fast")]));
        console.log("any:", await Promise.any([bad(5, "x"), ok(15, "first success")]));
        try {
          await Promise.any([bad(5, "e1"), bad(5, "e2")]);
        } catch (e) {
          console.log(e.constructor.name, e.errors.map((x) => x.message));
        }
    ''', out='''
        all: [ 'a', 'b', 42 ]
        all rejected: db down
        [
          { status: 'fulfilled', value: 'a' },
          { status: 'rejected', reason: 'nope' }
        ]
        race: fast
        any: first success
        AggregateError [ 'e1', 'e2' ]
    ''')
    yield note("`Promise.all` rejects fast, but the other operations **keep running** — promises are not cancellable. Use an `AbortController` if you need to stop them.")
    yield section("Pattern: timeout with race", "clock-x")
    yield snippet("js", '''
        const timeout = (ms) => new Promise((_, rej) => setTimeout(() => rej(new Error(`timed out after ${ms}ms`)), ms));
        const slowFetch = new Promise((res) => setTimeout(() => res("data"), 50));
        try {
          await Promise.race([slowFetch, timeout(10)]);
        } catch (e) {
          console.log(e.message);
        }
    ''', out="timed out after 10ms")
    yield section("Sequential vs parallel", "arrows-right")
    yield snippet("js", '''
        const job = (id, log) => new Promise((res) => setTimeout(() => { log.push(id); res(id); }, 10 * (4 - id)));

        const seq = [];
        for (const id of [1, 2, 3]) await job(id, seq);          // one after another
        console.log("sequential finish order:", seq);

        const par = [];
        const results = await Promise.all([1, 2, 3].map((id) => job(id, par)));  // all at once
        console.log("parallel finish order:", par, "results:", results);
    ''', out='''
        sequential finish order: [ 1, 2, 3 ]
        parallel finish order: [ 3, 2, 1 ] results: [ 1, 2, 3 ]
    ''')
    yield qa("Promise.all vs Promise.allSettled?",
             "`all` fails fast: it rejects with the first error and you lose the other results. `allSettled` always waits for every promise and reports each outcome, so use it when partial success is acceptable (e.g. sending many notifications).")
    yield qa("race vs any?",
             "`race` settles with the first promise to settle, success or failure. `any` ignores rejections and fulfils with the first success; it rejects only if all reject (with an `AggregateError`).")


@topic(G, "async-await", "async / await", "player-play")
def _():
    yield lead("`async`/`await` is syntax over promises that lets asynchronous code read top-to-bottom like synchronous code — with ordinary `try/catch` for errors.")
    yield section("The rules", "list-check")
    yield ul(
        "An `async` function **always returns a promise** — a returned value is wrapped, a thrown error becomes a rejection.",
        "`await p` pauses *that function* (not the thread) until `p` settles, then returns the value or throws the reason.",
        "`await` works inside `async` functions and at the top level of ES modules.",
    )
    yield snippet("js", '''
        async function getNumber() { return 7; }
        async function explode() { throw new Error("async boom"); }

        console.log(getNumber() instanceof Promise);
        console.log(await getNumber());
        try {
          await explode();
        } catch (e) {
          console.log("caught:", e.message);
        }
    ''', out='''
        true
        7
        caught: async boom
    ''')
    yield section("Rewriting a promise chain", "transform")
    yield snippet("js", '''
        const db = {
          user: (id) => new Promise((r) => setTimeout(() => r({ id, name: "Asha" }), 5)),
          orders: (user) => new Promise((r) => setTimeout(() => r([{ total: 30 }, { total: 12 }]), 5)),
        };

        // with then
        db.user(1)
          .then((user) => db.orders(user).then((orders) => ({ user, orders })))
          .then(({ user, orders }) => console.log("then:", user.name, orders.length));

        // with async/await
        async function summary(id) {
          const user = await db.user(id);
          const orders = await db.orders(user);
          const total = orders.reduce((s, o) => s + o.total, 0);
          return `${user.name} spent ${total}`;
        }
        console.log("await:", await summary(1));
    ''', out='''
        then: Asha 2
        await: Asha spent 42
    ''')
    yield section("Do not serialise independent work", "arrows-split")
    yield snippet("js", '''
        const fetchA = () => new Promise((r) => setTimeout(() => r("A"), 30));
        const fetchB = () => new Promise((r) => setTimeout(() => r("B"), 30));

        let t = performance.now();
        const a1 = await fetchA();
        const b1 = await fetchB();                  // waits for A first: ~60 ms
        const slow = performance.now() - t;

        t = performance.now();
        const [a2, b2] = await Promise.all([fetchA(), fetchB()]);   // concurrently: ~30 ms
        const fast = performance.now() - t;
        console.log(a1 + b1, a2 + b2, slow > 55, fast < 50);
    ''', out="AB AB true true")
    yield section("await in loops", "repeat")
    yield snippet("js", '''
        const double = (n) => new Promise((r) => setTimeout(() => r(n * 2), 5));
        const nums = [1, 2, 3];

        const wrong = nums.forEach(async (n) => await double(n));   // forEach ignores promises
        console.log("forEach returns:", wrong);

        const out = [];
        for (const n of nums) out.push(await double(n));            // sequential, correct
        console.log(out, await Promise.all(nums.map(double)));      // parallel, correct
    ''', out='''
        forEach returns: undefined
        [ 2, 4, 6 ] [ 2, 4, 6 ]
    ''')
    yield warn("`array.forEach(async …)` fires all callbacks and returns immediately — nothing waits for them and their errors are unhandled. Use `for…of` with `await` (sequential) or `Promise.all(arr.map(…))` (parallel).")
    yield section("Error handling patterns", "shield")
    yield snippet("js", '''
        const risky = (ok) => (ok ? Promise.resolve("data") : Promise.reject(new Error("network")));

        // 1. try / catch / finally
        async function load() {
          try {
            return await risky(false);     // `return await` so the catch applies
          } catch (e) {
            return `fallback (${e.message})`;
          } finally {
            console.log("hide spinner");
          }
        }
        console.log(await load());

        // 2. Go-style tuple helper
        const to = (p) => p.then((v) => [null, v], (e) => [e, null]);
        const [err, data] = await to(risky(true));
        console.log(err, data);
    ''', out='''
        hide spinner
        fallback (network)
        null data
    ''')
    yield qa("What does an async function return?",
             "Always a Promise. A returned value resolves it; a thrown error rejects it; a returned promise is adopted.")
    yield qa("Does await block the thread?",
             "No. It suspends only the current async function; the rest of the function becomes a microtask continuation, and the event loop keeps running other code meanwhile.")


@topic(G, "timers", "Timers & Cancellation", "clock")
def _():
    yield lead("`setTimeout`, `setInterval`, `setImmediate`, `queueMicrotask` and `AbortController` — scheduling work and cancelling it.")
    yield table(
        ["API", "Schedules", "Cancel with"],
        ["`setTimeout(fn, ms, ...args)`", "Once, after at least `ms`", "`clearTimeout(id)`"],
        ["`setInterval(fn, ms)`", "Repeatedly every `ms`", "`clearInterval(id)`"],
        ["`setImmediate(fn)` (Node)", "Once, in the check phase", "`clearImmediate(id)`"],
        ["`queueMicrotask(fn)`", "As a microtask", "—"],
        ["`requestAnimationFrame(fn)` (browser)", "Before the next repaint", "`cancelAnimationFrame(id)`"],
    )
    yield snippet("js", '''
        const id = setTimeout(() => console.log("never printed"), 10);
        clearTimeout(id);

        setTimeout((a, b) => console.log("args:", a, b), 5, "x", "y");

        let n = 0;
        const iv = setInterval(() => {
          n++;
          console.log("tick", n);
          if (n === 3) clearInterval(iv);
        }, 5);
    ''', out='''
        args: x y
        tick 1
        tick 2
        tick 3
    ''')
    yield section("Delays are minimums", "hourglass")
    yield ul(
        "The callback runs **at least** `ms` later — later if the stack is busy.",
        "Browsers clamp nested timers (5+ levels deep) to ≥ 4 ms and throttle background tabs to ≥ 1 s.",
        "`setInterval` does not wait for slow callbacks; prefer a recursive `setTimeout` when each run must finish before the next is scheduled.",
    )
    yield snippet("js", '''
        const start = performance.now();
        setTimeout(() => {
          console.log("waited at least 20ms:", performance.now() - start >= 20);
        }, 10);
        while (performance.now() - start < 20) {}   // block the thread for 20ms
    ''', out="waited at least 20ms: true")
    yield section("Promise-based timers", "clock-play")
    yield snippet("js", '''
        import { setTimeout as sleep } from "node:timers/promises";
        const sleepAnywhere = (ms) => new Promise((r) => setTimeout(r, ms));   // browser version

        console.log(await sleep(5, "node timers/promises"));
        await sleepAnywhere(5);
        console.log("slept");
    ''', out='''
        node timers/promises
        slept
    ''')
    yield section("Cancellation with AbortController", "hand-stop")
    yield snippet("js", '''
        function cancellableDelay(ms, { signal } = {}) {
          return new Promise((resolve, reject) => {
            if (signal?.aborted) return reject(signal.reason);
            const id = setTimeout(resolve, ms, "finished");
            signal?.addEventListener("abort", () => {
              clearTimeout(id);
              reject(signal.reason);
            }, { once: true });
          });
        }
        const controller = new AbortController();
        setTimeout(() => controller.abort(new Error("user cancelled")), 10);
        try {
          await cancellableDelay(1000, { signal: controller.signal });
        } catch (e) {
          console.log(e.message);
        }
        try {
          await cancellableDelay(1000, { signal: AbortSignal.timeout(10) });
        } catch (e) {
          console.log(e.name);
        }
    ''', out='''
        user cancelled
        TimeoutError
    ''')
    yield note("`fetch(url, { signal })`, `addEventListener(…, { signal })`, Node streams and `timers/promises` all accept an `AbortSignal` — one controller can cancel a whole group of operations.")
    yield qa("Why might setTimeout(fn, 0) not run immediately?",
             "It only queues a macrotask. It runs after the current synchronous code, after all microtasks, and after any earlier timers — and browsers may clamp the delay.")


@topic(G, "async-iteration", "Async Iterators & for await", "arrow-loop-right")
def _():
    yield lead("When values arrive over time — pages of an API, lines of a file, chunks of a stream — async generators and `for await…of` let you loop over them naturally.")
    yield section("Async generators", "code")
    yield snippet("js", '''
        const fakeApi = (page) =>
          new Promise((r) => setTimeout(() => r({ items: [`p${page}-a`, `p${page}-b`], next: page < 3 ? page + 1 : null }), 5));

        async function* paginate() {
          let page = 1;
          while (page) {
            const { items, next } = await fakeApi(page);
            yield* items;
            page = next;
          }
        }
        for await (const item of paginate()) {
          console.log(item);
          if (item === "p3-a") break;
        }
    ''', out='''
        p1-a
        p1-b
        p2-a
        p2-b
        p3-a
    ''')
    yield section("for await over promises and streams", "arrows-down")
    yield snippet("js", '''
        const delays = [30, 10, 20].map((ms) => new Promise((r) => setTimeout(() => r(ms), ms)));
        for await (const ms of delays) console.log("resolved", ms);   // in ARRAY order, not finish order

        import { Readable } from "node:stream";
        const stream = Readable.from(["chunk1", "chunk2"]);
        for await (const chunk of stream) console.log(chunk);

        const collected = await Array.fromAsync(paginateSmall());      // ES2024
        async function* paginateSmall() { yield 1; yield 2; }
        console.log(collected);
    ''', out='''
        resolved 30
        resolved 10
        resolved 20
        chunk1
        chunk2
        [ 1, 2 ]
    ''')
    yield qa("What is the difference between for...of and for await...of?",
             "`for await…of` calls `[Symbol.asyncIterator]()` (falling back to the sync iterator) and awaits each value before the loop body runs, so it can consume async generators, streams and arrays of promises. It is only allowed in async functions and module top level.")
