from kit import *

G = "Browser & Node.js"


@topic(G, "dom-basics", "DOM Essentials", "browser")
def _():
    yield lead("The DOM (Document Object Model) is the browser's live tree of objects representing the page. JavaScript reads and changes the page by manipulating that tree.")
    yield note("Node.js has no DOM, so the browser examples in this topic and the next are shown without being executed (they are marked *not run*). Try them in any browser's DevTools console.", "Not run here")
    yield section("The tree", "binary-tree")
    yield flow("`window`", "`document`", "`<html>`", "`<body>`", "elements & text nodes")
    yield table(
        ["Concept", "Meaning"],
        ["Node", "Anything in the tree: elements, text, comments (`nodeType` 1, 3, 8)"],
        ["Element", "A tag like `<div>` — has attributes, `children`, `classList`…"],
        ["`window`", "The global object in browsers: timers, `location`, `history`, `localStorage`, `innerWidth`"],
        ["`document`", "Entry point to the page tree"],
    )
    yield section("Selecting elements", "pointer")
    yield snippet("js", '''
        document.getElementById("app");               // one element or null
        document.querySelector(".card > h2");         // first match (any CSS selector)
        document.querySelectorAll("li.item");         // static NodeList (has forEach)
        document.getElementsByClassName("item");      // LIVE HTMLCollection (updates itself)
        element.closest(".card");                     // nearest ancestor matching (incl. itself)
        element.matches("button.primary");            // does it match the selector?
    ''', "JavaScript (browser, not run)", run=False)
    yield warn("`querySelectorAll` returns a *static* snapshot; `getElementsBy*` and `children` are *live* and change while you loop over them. Convert to an array (`[...list]`) for `map`/`filter`.")
    yield section("Reading and changing content", "edit")
    yield snippet("js", '''
        const title = document.querySelector("h1");
        title.textContent = "Hello <b>world</b>";     // plain text — safe
        title.innerHTML = "Hello <b>world</b>";       // parses HTML — XSS risk with user input!
        title.classList.add("active");                // also remove / toggle / contains / replace
        title.style.color = "tomato";                 // inline style (camelCase properties)
        title.setAttribute("aria-label", "Greeting");
        title.dataset.userId = "42";                  // → data-user-id="42"
        const input = document.querySelector("input");
        input.value;                                  // current value (property) vs getAttribute("value") (initial)
    ''', "JavaScript (browser, not run)", run=False)
    yield section("Creating, inserting, removing", "circle-plus")
    yield snippet("js", '''
        const list = document.querySelector("#todo");
        const frag = document.createDocumentFragment();   // batch inserts → one reflow
        for (const text of ["Learn DOM", "Build app"]) {
          const li = document.createElement("li");
          li.textContent = text;
          frag.append(li);
        }
        list.append(frag);                    // also prepend / before / after / replaceWith
        list.insertAdjacentHTML("beforeend", "<li>Ship</li>");
        list.firstElementChild.remove();
    ''', "JavaScript (browser, not run)", run=False)
    yield section("Script loading and page lifecycle", "clock")
    yield table(
        ["Tag / event", "Behaviour"],
        ["`<script>`", "Blocks HTML parsing while it downloads and runs"],
        ["`<script defer>`", "Downloads in parallel; runs in order after parsing, before `DOMContentLoaded`"],
        ["`<script async>`", "Downloads in parallel; runs as soon as it arrives (order not guaranteed)"],
        ["`<script type=\"module\">`", "Deferred by default, strict mode, supports `import`"],
        ["`DOMContentLoaded`", "HTML parsed, DOM ready (images may still be loading)"],
        ["`load`", "Everything loaded, including images and stylesheets"],
    )
    yield section("Performance: reflow and repaint", "gauge")
    yield ul(
        "Changing geometry (size, position, adding nodes) triggers **layout/reflow**; colours only trigger **repaint**.",
        "Reading layout (`offsetHeight`, `getBoundingClientRect`) right after writing forces a synchronous reflow — batch reads, then writes (*layout thrashing*).",
        "Animate `transform` and `opacity` (compositor-only) and use `requestAnimationFrame` for visual updates.",
    )
    yield qa("textContent vs innerText vs innerHTML?",
             "`textContent` gets/sets raw text of all nodes (fast, no layout). `innerText` returns *rendered* text (respects CSS, triggers layout). `innerHTML` parses/serialises HTML — never assign untrusted input to it (XSS).")
    yield qa("defer vs async?",
             "Both download without blocking parsing. `defer` scripts execute in document order after parsing finishes; `async` scripts execute as soon as they download, in any order. Use `defer` for app code, `async` for independent scripts like analytics.")


@topic(G, "dom-events", "Events: Bubbling, Capturing & Delegation", "click")
def _():
    yield lead("A DOM event travels **down** the tree (capture), hits the target, then travels back **up** (bubble). Delegation uses the bubbling phase to handle many elements with one listener.")
    yield section("The three phases", "arrows-up-down")
    yield steps(
        ("Capture", "From `window` down through each ancestor to the target's parent. Listeners registered with `{ capture: true }` run here."),
        ("Target", "Listeners on the element itself."),
        ("Bubble", "Back up from the parent to `window`. Default listeners run here. (`focus`, `blur`, `mouseenter` don't bubble.)"),
    )
    yield snippet("js", '''
        // <div id="outer"><button id="inner">Click</button></div>
        outer.addEventListener("click", () => console.log("outer capture"), { capture: true });
        outer.addEventListener("click", () => console.log("outer bubble"));
        inner.addEventListener("click", () => console.log("button"));
        // clicking the button logs: outer capture → button → outer bubble
    ''', "JavaScript (browser, not run)", run=False)
    yield section("Event object essentials", "list-details")
    yield table(
        ["Member", "Purpose"],
        ["`event.target`", "The element that was actually clicked (deepest)"],
        ["`event.currentTarget`", "The element whose listener is running now"],
        ["`event.preventDefault()`", "Cancel the default action (follow link, submit form)"],
        ["`event.stopPropagation()`", "Stop travelling to further ancestors"],
        ["`event.stopImmediatePropagation()`", "Also skip remaining listeners on the same element"],
        ["`{ once: true }`, `{ passive: true }`, `{ signal }`", "Auto-remove; promise not to `preventDefault` (smooth scrolling); remove via `AbortController`"],
    )
    yield section("Event delegation", "hierarchy-2")
    yield snippet("js", '''
        // One listener for any number of (even future) <li> items:
        document.querySelector("#todo").addEventListener("click", (event) => {
          const item = event.target.closest("li[data-id]");
          if (!item || !event.currentTarget.contains(item)) return;
          if (event.target.matches(".delete")) item.remove();
          else item.classList.toggle("done");
        });
    ''', "JavaScript (browser, not run)", run=False)
    yield good("Delegation means fewer listeners (less memory), automatic handling of elements added later, and one place for the logic.")
    yield section("Runnable: EventTarget and CustomEvent", "code")
    yield p("`EventTarget`, `Event` and `CustomEvent` also exist in Node, so the listener API itself can be demonstrated (there is no tree, so no bubbling):")
    yield snippet("js", '''
        const cart = new EventTarget();
        const controller = new AbortController();

        cart.addEventListener("add", (e) => console.log("added", e.detail.item), { signal: controller.signal });
        cart.addEventListener("add", () => console.log("first add only"), { once: true });
        cart.addEventListener("checkout", (e) => {
          e.preventDefault();
          console.log("checkout blocked by listener");
        });

        cart.dispatchEvent(new CustomEvent("add", { detail: { item: "book" } }));
        cart.dispatchEvent(new CustomEvent("add", { detail: { item: "pen" } }));
        controller.abort();                                     // removes the first listener
        cart.dispatchEvent(new CustomEvent("add", { detail: { item: "lamp" } }));

        const ok = cart.dispatchEvent(new Event("checkout", { cancelable: true }));
        console.log("dispatch returned", ok);
    ''', out='''
        added book
        first add only
        added pen
        checkout blocked by listener
        dispatch returned false
    ''')
    yield qa("What is event delegation?",
             "Attaching a single listener to a common ancestor and using `event.target` (often with `closest`) to find which child triggered the event. It relies on bubbling and works for elements added after the listener was registered.")
    yield qa("target vs currentTarget?",
             "`target` is where the event originated (e.g. an `<span>` inside a button); `currentTarget` is the element the currently running listener is attached to (the button or the delegating parent).")


@topic(G, "browser-apis", "Browser APIs: fetch, Storage & More", "world-www")
def _():
    yield lead("The runtime gives JavaScript its superpowers: networking, storage, URLs, workers, observers. `fetch` and friends also exist in Node, so several examples here really run.")
    yield section("fetch", "cloud-download")
    yield p("`fetch` returns a promise for a `Response`. It **only rejects on network failure** — HTTP 404/500 still fulfils, so check `response.ok`. This demo starts a tiny local server so the output is deterministic:")
    yield snippet("js", '''
        import http from "node:http";
        const server = http.createServer((req, res) => {
          if (req.url === "/api/user") {
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ id: 1, name: "Asha" }));
          } else {
            res.writeHead(404).end("not found");
          }
        });
        await new Promise((r) => server.listen(0, r));
        const base = `http://localhost:${server.address().port}`;

        async function getJSON(url, options = {}) {
          const res = await fetch(url, options);
          if (!res.ok) throw new Error(`HTTP ${res.status}`);   // fetch doesn't throw on 404!
          return res.json();
        }
        console.log(await getJSON(`${base}/api/user`));
        try {
          await getJSON(`${base}/missing`);
        } catch (e) {
          console.log("failed:", e.message);
        }
        const res = await fetch(`${base}/api/user`, { signal: AbortSignal.timeout(2000) });
        console.log(res.status, res.headers.get("content-type"));
        server.close();
    ''', out='''
        { id: 1, name: 'Asha' }
        failed: HTTP 404
        200 application/json
    ''')
    yield snippet("js", '''
        await fetch("/api/todos", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ title: "Learn fetch" }),
          credentials: "include",            // send cookies cross-origin
        });
    ''', "JavaScript (POST request, not run)", run=False)
    yield section("Web storage", "database")
    yield table(
        ["", "`localStorage`", "`sessionStorage`", "Cookies", "IndexedDB"],
        ["Lifetime", "Until cleared", "Until the tab closes", "Set by expiry", "Until cleared"],
        ["Size", "~5–10 MB", "~5 MB", "~4 KB each", "Large (quota based)"],
        ["Sent to server", "No", "No", "With every request", "No"],
        ["API", "Sync, strings only", "Sync, strings only", "`document.cookie` string", "Async, structured data"],
    )
    yield snippet("js", '''
        localStorage.setItem("prefs", JSON.stringify({ theme: "dark" }));   // store strings only
        const prefs = JSON.parse(localStorage.getItem("prefs") ?? "{}");
        localStorage.removeItem("prefs");
        window.addEventListener("storage", (e) => console.log(e.key, e.newValue)); // other tabs
    ''', "JavaScript (browser, not run)", run=False)
    yield warn("Never store secrets or auth tokens in `localStorage` — any XSS can read it. Prefer `HttpOnly`, `Secure`, `SameSite` cookies for sessions.")
    yield section("Platform utilities that run everywhere", "tool")
    yield snippet("js", '''
        const url = new URL("https://shop.example.com:8080/items/42?color=red&size=m#reviews");
        console.log(url.hostname, url.port, url.pathname, url.hash);
        url.searchParams.set("size", "l");
        url.searchParams.append("tag", "new sale");
        console.log(url.search);
        console.log([...new TextEncoder().encode("hé")], btoa("hi"), atob("aGk="));
        console.log(encodeURIComponent("a b&c/d"), crypto.randomUUID().length);
        const blob = new Blob(["hello"], { type: "text/plain" });
        console.log(blob.size, await blob.text());
    ''', out='''
        shop.example.com 8080 /items/42 #reviews
        ?color=red&size=l&tag=new+sale
        [ 104, 195, 169 ] aGk= hi
        a%20b%26c%2Fd 36
        5 hello
    ''')
    yield section("Other APIs to know", "apps")
    yield table(
        ["API", "Use"],
        ["Web Workers", "Run CPU-heavy JS on another thread; talk via `postMessage` (no DOM access)"],
        ["Service Workers", "Network proxy for offline support, caching, push notifications (PWAs)"],
        ["`IntersectionObserver`", "Lazy-load images, infinite scroll — know when elements enter the viewport"],
        ["`MutationObserver` / `ResizeObserver`", "React to DOM changes / element size changes"],
        ["`requestAnimationFrame`", "Smooth animations synced to the display"],
        ["`history.pushState`, `location`", "Client-side routing in SPAs"],
        ["`navigator.clipboard`, `geolocation`, `Notification`", "Permission-gated device features"],
        ["WebSocket / EventSource", "Real-time two-way / server-sent streams"],
    )
    yield section("Same-origin policy and CORS", "lock-open")
    yield p("Browsers block scripts from reading responses from a different **origin** (scheme + host + port) unless the server opts in with CORS headers such as `Access-Control-Allow-Origin`. Non-simple requests (custom headers, `PUT`, JSON bodies) are preceded by an `OPTIONS` **preflight**. CORS is enforced by the browser, not the server — `curl` and Node ignore it.")
    yield qa("Does fetch reject on a 404?",
             "No. `fetch` rejects only on network errors (DNS failure, offline, CORS block, abort). Any HTTP response — including 404 and 500 — fulfils; check `response.ok` or `response.status` and throw yourself.")
    yield qa("localStorage vs sessionStorage vs cookies?",
             "`localStorage` persists across sessions, `sessionStorage` lasts for one tab session; both are ~5 MB, string-only, synchronous and never sent to the server. Cookies are tiny, sent with every matching request, and can be `HttpOnly` (hidden from JS) — the right place for session identifiers.")


@topic(G, "nodejs-essentials", "Node.js Essentials", "brand-nodejs")
def _():
    yield lead("Node.js is V8 plus libuv plus a standard library for files, networking, processes and streams — JavaScript outside the browser.")
    yield section("Architecture", "cpu")
    yield flow("Your JS", "V8 (executes)", "Node bindings", "libuv (event loop + thread pool)", "OS")
    yield ul(
        "Network I/O is non-blocking at the OS level; file-system, DNS lookups, crypto and zlib use libuv's thread pool (4 threads by default).",
        "One JS thread per process; scale with `cluster`, `worker_threads`, or multiple processes behind a load balancer.",
        "Globals: `process`, `Buffer`, `globalThis`, `setImmediate`, `structuredClone`, `fetch`; no `window` or `document`.",
    )
    yield section("path and process", "route")
    yield snippet("js", '''
        import path from "node:path";
        const file = "/home/asha/projects/app/src/index.test.js";
        console.log(path.basename(file), path.extname(file), path.dirname(file));
        console.log(path.join("/a/b", "../c", "d.txt"), path.resolve("/root", "x", "..", "y"));
        console.log(path.parse("/tmp/report.pdf"));
        console.log(typeof process.argv, process.argv.length >= 2, process.platform.length > 0);
        const port = Number(process.env.PORT ?? 3000);          // env vars are strings or undefined
        console.log(port, typeof process.exitCode);
    ''', out='''
        index.test.js .js /home/asha/projects/app/src
        /a/c/d.txt /root/y
        {
          root: '/',
          dir: '/tmp',
          base: 'report.pdf',
          ext: '.pdf',
          name: 'report'
        }
        object true true
        3000 undefined
    ''')
    yield section("The fs module (promises API)", "files")
    yield snippet("js", '''
        import { writeFile, readFile, appendFile, readdir, mkdir, rm, stat } from "node:fs/promises";
        import { existsSync } from "node:fs";

        await mkdir("data/logs", { recursive: true });
        await writeFile("data/logs/app.log", "started\\n");
        await appendFile("data/logs/app.log", "ready\\n");
        const text = await readFile("data/logs/app.log", "utf8");
        console.log(text.trim().split("\\n"));
        console.log(await readdir("data"), (await stat("data/logs/app.log")).size);
        try {
          await readFile("missing.txt", "utf8");
        } catch (e) {
          console.log(e.code);
        }
        await rm("data", { recursive: true });
        console.log(existsSync("data"));
    ''', out='''
        [ 'started', 'ready' ]
        [ 'logs' ] 14
        ENOENT
        false
    ''')
    yield note("Use `node:fs/promises` with `await` in application code. The `*Sync` variants block the event loop — fine in CLI scripts and at startup, harmful inside a server request handler.")
    yield section("A minimal HTTP server", "server")
    yield snippet("js", '''
        import http from "node:http";
        const server = http.createServer((req, res) => {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ method: req.method, path: req.url }));
        });
        server.listen(0, async () => {
          const { port } = server.address();
          const body = await (await fetch(`http://localhost:${port}/hello?x=1`)).json();
          console.log(body);
          server.close();
        });
    ''', out="{ method: 'GET', path: '/hello?x=1' }")
    yield section("npm and package.json", "package")
    yield shell('''
        $ npm init -y                    # create package.json
        $ npm install express            # dependency  → "dependencies"
        $ npm install -D vitest          # dev-only    → "devDependencies"
        $ npm run test                   # run a script from "scripts"
        $ npx eslint .                   # run a package binary without installing globally
        $ npm ci                         # clean, exact install from package-lock.json (CI)
    ''')
    yield table(
        ["Version range", "Accepts"],
        ["`\"4.18.2\"`", "Exactly that version"],
        ["`\"^4.18.2\"`", "`>=4.18.2 <5.0.0` — minor + patch updates (npm's default)"],
        ["`\"~4.18.2\"`", "`>=4.18.2 <4.19.0` — patch updates only"],
    )
    yield qa("Is Node.js single-threaded?",
             "Your JavaScript runs on a single main thread with an event loop, but Node itself uses libuv's thread pool for file I/O, DNS, crypto and compression, and you can create more JS threads with `worker_threads`.")


@topic(G, "node-events-streams", "EventEmitter & Streams", "arrows-right-left")
def _():
    yield lead("Most of Node is built on two ideas: objects that emit named events, and streams that move data in chunks instead of loading everything into memory.")
    yield section("EventEmitter", "broadcast")
    yield snippet("js", '''
        import { EventEmitter, once } from "node:events";

        class Order extends EventEmitter {
          place(item) {
            this.emit("placed", { item, at: "12:00" });
            if (item === "unknown") this.emit("error", new Error("no such item"));
          }
        }
        const order = new Order();
        order.on("placed", ({ item }) => console.log("email: placed", item));
        order.once("placed", () => console.log("analytics: first order only"));
        order.on("error", (err) => console.log("handled error:", err.message));

        order.place("book");
        order.place("unknown");
        console.log(order.listenerCount("placed"), order.eventNames());

        setTimeout(() => order.emit("shipped", "TRACK-1"), 5);
        const [tracking] = await once(order, "shipped");      // promise-based wait
        console.log("shipped with", tracking);
    ''', out='''
        email: placed book
        analytics: first order only
        email: placed unknown
        handled error: no such item
        1 [ 'placed', 'error' ]
        shipped with TRACK-1
    ''')
    yield warn("Emitting `'error'` with no `'error'` listener **throws** and crashes the process. Listeners run **synchronously**, in registration order, inside `emit`.")
    yield section("Streams", "arrows-right")
    yield table(
        ["Type", "Examples"],
        ["Readable", "`fs.createReadStream`, HTTP request (server side), `process.stdin`"],
        ["Writable", "`fs.createWriteStream`, HTTP response, `process.stdout`"],
        ["Duplex", "TCP socket"],
        ["Transform", "`zlib.createGzip()`, encryption, parsers"],
    )
    yield snippet("js", '''
        import { Readable, Transform, Writable } from "node:stream";
        import { pipeline } from "node:stream/promises";

        const source = Readable.from(["alpha\\n", "beta\\n", "gamma\\n"]);
        const upper = new Transform({
          transform(chunk, _enc, callback) {
            callback(null, chunk.toString().toUpperCase());
          },
        });
        const collected = [];
        const sink = new Writable({
          write(chunk, _enc, callback) {
            collected.push(chunk.toString().trim());
            callback();
          },
        });
        await pipeline(source, upper, sink);     // handles back-pressure and errors
        console.log(collected);
    ''', out="[ 'ALPHA', 'BETA', 'GAMMA' ]")
    yield note("**Back-pressure**: when the consumer is slower than the producer, `pipeline`/`pipe` pause the source so memory stays bounded — the reason to stream a 10 GB file instead of `readFile`-ing it.")
    yield qa("Why use streams instead of reading a whole file?",
             "Streams process data chunk by chunk, so memory use stays constant regardless of size, work starts before all data arrives, and back-pressure keeps fast producers from overwhelming slow consumers.")
