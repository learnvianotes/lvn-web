from kit import *

G = "Concurrency"


@topic(G, "threads", "Threads: std::thread & std::jthread", "arrows-split")
def _():
    yield lead("A `std::thread` runs a callable concurrently with the rest of the program. You must `join()` (wait for) or `detach()` it before it's destroyed; C++20's `std::jthread` joins automatically.")
    yield section("Starting and joining", "player-play")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <thread>
        #include <vector>

        void partialSum(const std::vector<int>& data, std::size_t from, std::size_t to, long long& out) {
            long long s = 0;
            for (std::size_t i = from; i < to; ++i) s += data[i];
            out = s;                                          // each thread writes its own slot: no race
        }

        int main() {
            std::vector<int> data(1'000'000, 1);
            long long left = 0, right = 0;
            std::size_t mid = data.size() / 2;

            std::thread t1(partialSum, std::cref(data), 0, mid, std::ref(left));   // args are COPIED unless wrapped
            std::thread t2([&] { partialSum(data, mid, data.size(), right); });    // or capture in a lambda
            t1.join();                                        // wait for both to finish
            t2.join();
            std::cout << left + right << '\n';
            std::cout << (std::thread::hardware_concurrency() > 0) << '\n';        // number of cores (hint)
        }
    ''', out='''
        1000000
        1
    ''')
    yield warn("If a joinable `std::thread` is destroyed (goes out of scope without `join()` or `detach()`), the program calls `std::terminate`. An exception thrown between creating and joining causes exactly this — which is why `std::jthread` exists.")
    yield section("`std::jthread` (C++20)", "player-stop")
    yield snippet("cpp", r'''
        #include <chrono>
        #include <iostream>
        #include <thread>

        int main() {
            int ticks = 0;
            {
                std::jthread worker([&ticks](std::stop_token st) {   // receives a stop token
                    while (!st.stop_requested()) {
                        ++ticks;
                        std::this_thread::sleep_for(std::chrono::milliseconds(1));
                    }
                });
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }   // ~jthread: request_stop() then join() — automatic
            std::cout << "worker stopped after " << (ticks > 0 ? "some" : "no") << " ticks\n";
        }
    ''', out="worker stopped after some ticks")
    yield section("Thread basics", "list")
    yield table(
        ["API", "Meaning"],
        ["`std::thread t(f, args...)`", "Start `f(args...)` on a new thread (arguments copied/moved into it)"],
        ["`t.join()`", "Block until `t` finishes"],
        ["`t.detach()`", "Let it run independently (you can no longer join it — rarely a good idea)"],
        ["`t.joinable()`", "Still represents a running/unjoined thread?"],
        ["`std::this_thread::sleep_for(d)` / `yield()` / `get_id()`", "Helpers for the current thread"],
        ["`std::ref(x)` / `std::cref(x)`", "Pass by reference into a thread"],
        ["`thread_local int x;`", "One separate variable per thread"],
    )
    yield section("Output order is not deterministic", "arrows-shuffle")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <thread>
        #include <vector>

        int main() {
            std::vector<std::jthread> workers;
            for (int id = 0; id < 3; ++id)
                workers.emplace_back([id] { std::cout << "worker " << id << " running\n"; });
        }   // lines may appear in any order — or even interleaved mid-line
    ''', out=None)
    yield qa("What's the difference between a process and a thread?",
             "A process has its own address space; threads within a process share memory (globals, heap) but each has its own stack and registers. Threads are cheaper to create and communicate through shared memory — which is exactly why they need synchronisation.")
    yield qa("What happens if you forget to join a std::thread?",
             "When the `std::thread` object is destroyed while still joinable, its destructor calls `std::terminate()`, aborting the program. Use `std::jthread` (joins in its destructor) or an RAII guard.")


@topic(G, "mutex-locks", "Mutexes, Locks & Deadlock", "lock")
def _():
    yield lead("A **data race** — two threads touching the same memory, at least one writing, without synchronisation — is undefined behaviour. A mutex makes a critical section run in one thread at a time.")
    yield section("A race, and the fix", "lock")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <mutex>
        #include <thread>
        #include <vector>

        int main() {
            long long counter = 0;
            std::mutex m;
            {
                std::vector<std::jthread> threads;
                for (int t = 0; t < 4; ++t)
                    threads.emplace_back([&] {
                        for (int i = 0; i < 100'000; ++i) {
                            std::lock_guard<std::mutex> lock(m);   // locks now, unlocks at end of scope
                            ++counter;                             // without the lock: lost updates
                        }
                    });
            }
            std::cout << counter << '\n';
        }
    ''', out="400000")
    yield note("`++counter` is read-modify-write: two threads can both read 5 and both write 6. Without the mutex the result is typically less than 400000 — and formally the program has undefined behaviour.", "Why the lock")
    yield section("Lock types", "key")
    yield table(
        ["RAII lock", "Use"],
        ["`std::lock_guard<M>`", "Simplest: lock for the whole scope"],
        ["`std::unique_lock<M>`", "Can unlock/relock, defer, time out, be moved; required by condition variables"],
        ["`std::scoped_lock<M1, M2…>` (C++17)", "Lock several mutexes at once *without deadlock*"],
        ["`std::shared_lock<std::shared_mutex>`", "Many readers or one writer"],
    )
    yield section("Deadlock", "lock-x")
    yield p("Thread A locks `m1` then waits for `m2`; thread B locks `m2` then waits for `m1` — both wait forever. Prevent it by always acquiring locks in the same global order, or by locking them together with `std::scoped_lock`.")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <mutex>
        #include <thread>

        struct Account {
            int balance;
            std::mutex m;
        };

        void transfer(Account& from, Account& to, int amount) {
            std::scoped_lock lock(from.m, to.m);       // deadlock-free, whatever order callers use
            from.balance -= amount;
            to.balance += amount;
        }

        int main() {
            Account a{1000, {}}, b{1000, {}};
            {
                std::jthread t1([&] { for (int i = 0; i < 1000; ++i) transfer(a, b, 1); });
                std::jthread t2([&] { for (int i = 0; i < 1000; ++i) transfer(b, a, 2); });
            }
            std::cout << a.balance << ' ' << b.balance << ' ' << a.balance + b.balance << '\n';
        }
    ''', out="2000 0 2000")
    yield section("Readers–writer lock", "book")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <mutex>
        #include <shared_mutex>
        #include <string>
        #include <thread>
        #include <vector>

        class Config {
            mutable std::shared_mutex m_;
            std::map<std::string, int> values_;
        public:
            int get(const std::string& k) const {
                std::shared_lock lock(m_);             // many readers at once
                auto it = values_.find(k);
                return it == values_.end() ? 0 : it->second;
            }
            void set(const std::string& k, int v) {
                std::unique_lock lock(m_);             // exclusive writer
                values_[k] = v;
            }
        };

        int main() {
            Config cfg;
            cfg.set("threads", 4);
            std::vector<std::jthread> readers;
            std::vector<int> seen(4);
            for (int i = 0; i < 4; ++i) readers.emplace_back([&, i] { seen[i] = cfg.get("threads"); });
            readers.clear();                           // join all
            std::cout << seen[0] + seen[1] + seen[2] + seen[3] << '\n';
        }
    ''', out="16")
    yield dodont("Keep critical sections short; never call unknown code (callbacks, virtual functions) while holding a lock; use RAII locks only.", "Calling `m.lock()` / `m.unlock()` by hand — an exception or early return leaves the mutex locked forever.")
    yield qa("What are the four conditions for deadlock?",
             "Mutual exclusion, hold-and-wait, no preemption and circular wait (Coffman conditions). Breaking any one prevents deadlock; in practice you break *circular wait* with a consistent lock order or by acquiring all locks atomically (`std::scoped_lock`/`std::lock`).")


@topic(G, "condition-variables", "Condition Variables & Producer–Consumer", "bell")
def _():
    yield lead("A `std::condition_variable` lets a thread sleep until another thread says “something changed”. Combined with a mutex and a queue it gives the classic producer–consumer pattern.")
    yield section("A thread-safe queue", "stack-push")
    yield snippet("cpp", r'''
        #include <condition_variable>
        #include <iostream>
        #include <mutex>
        #include <optional>
        #include <queue>
        #include <thread>

        template <typename T>
        class BlockingQueue {
            std::queue<T> q_;
            std::mutex m_;
            std::condition_variable cv_;
            bool closed_ = false;
        public:
            void push(T v) {
                { std::lock_guard lock(m_); q_.push(std::move(v)); }
                cv_.notify_one();                                     // wake one waiting consumer
            }
            void close() {
                { std::lock_guard lock(m_); closed_ = true; }
                cv_.notify_all();
            }
            std::optional<T> pop() {
                std::unique_lock lock(m_);
                cv_.wait(lock, [&] { return !q_.empty() || closed_; });   // predicate guards spurious wake-ups
                if (q_.empty()) return std::nullopt;                   // closed and drained
                T v = std::move(q_.front());
                q_.pop();
                return v;
            }
        };

        int main() {
            BlockingQueue<int> jobs;
            long long total = 0;
            int handled = 0;
            {
                std::jthread consumer([&] {
                    while (auto job = jobs.pop()) { total += *job; ++handled; }
                });
                std::jthread producer([&] {
                    for (int i = 1; i <= 100; ++i) jobs.push(i);
                    jobs.close();
                });
            }
            std::cout << handled << " jobs, total " << total << '\n';
        }
    ''', out="100 jobs, total 5050")
    yield steps(
        ("Lock", "The waiter takes a `std::unique_lock` on the mutex that protects the shared state."),
        ("Wait with a predicate", "`cv.wait(lock, pred)` checks `pred`; if false it *atomically* unlocks and sleeps, then relocks when woken and re-checks."),
        ("Modify, then notify", "The producer changes the state **under the mutex**, releases it, and calls `notify_one()` / `notify_all()`."),
    )
    yield warn("Always wait with a predicate (or in a `while` loop). Condition variables can wake up *spuriously*, and a notification sent before the waiter started waiting is lost — the predicate covers both cases.")
    yield qa("Why does condition_variable::wait need a unique_lock rather than a lock_guard?",
             "`wait` must unlock the mutex while sleeping and relock it before returning. `lock_guard` can't be unlocked and relocked; `unique_lock` can.")


@topic(G, "atomics", "Atomics & the Memory Model", "atom")
def _():
    yield lead("`std::atomic<T>` makes individual reads, writes and read-modify-write operations indivisible — lock-free synchronisation for counters, flags and pointers.")
    yield section("Atomic counter", "plus")
    yield snippet("cpp", r'''
        #include <atomic>
        #include <iostream>
        #include <thread>
        #include <vector>

        int main() {
            std::atomic<int> hits{0};
            {
                std::vector<std::jthread> ts;
                for (int t = 0; t < 8; ++t)
                    ts.emplace_back([&] { for (int i = 0; i < 10'000; ++i) hits.fetch_add(1); });   // or ++hits
            }
            std::cout << hits.load() << ' ' << hits.is_lock_free() << '\n';

            std::atomic<int> value{5};
            int expected = 5;
            bool swapped = value.compare_exchange_strong(expected, 10);   // CAS: if value == 5, set 10
            std::cout << swapped << ' ' << value << '\n';
            expected = 5;
            swapped = value.compare_exchange_strong(expected, 20);         // fails; expected becomes 10
            std::cout << swapped << ' ' << expected << '\n';
            std::cout << value.exchange(0) << ' ' << value << '\n';
        }
    ''', out='''
        80000 1
        1 10
        0 10
        10 0
    ''')
    yield table(
        ["Operation", "Meaning"],
        ["`load()` / `store(v)`", "Atomic read / write"],
        ["`fetch_add`, `fetch_sub`, `++`, `--`, `+=`", "Atomic read-modify-write; return old (fetch_) or new value"],
        ["`exchange(v)`", "Set and return the old value"],
        ["`compare_exchange_strong/weak(expected, desired)`", "CAS — the building block of lock-free algorithms"],
        ["`std::atomic_flag`", "Guaranteed lock-free boolean (spin locks)"],
    )
    yield section("Publishing data with a flag", "flag")
    yield snippet("cpp", r'''
        #include <atomic>
        #include <iostream>
        #include <string>
        #include <thread>

        int main() {
            std::string payload;
            std::atomic<bool> ready{false};
            std::jthread producer([&] {
                payload = "config loaded";                        // 1. write the data
                ready.store(true, std::memory_order_release);     // 2. publish
            });
            while (!ready.load(std::memory_order_acquire)) {}      // 3. wait (spin) for the flag
            std::cout << payload << '\n';                          // 4. guaranteed to see the write
        }
    ''', out="config loaded")
    yield p("The default ordering, `memory_order_seq_cst`, is the easiest to reason about. `release`/`acquire` pairs are cheaper on some CPUs: everything written before the release-store is visible after the matching acquire-load. `relaxed` guarantees atomicity only — fine for statistics counters.")
    yield table(
        ["", "`std::mutex`", "`std::atomic`"],
        ["Protects", "Any block of code / several variables", "One variable"],
        ["Blocking", "Yes (threads sleep)", "No (lock-free for built-in sizes)"],
        ["Best for", "Invariants spanning multiple fields", "Counters, flags, single pointers"],
    )
    yield warn("`volatile` is **not** for threads in C++ — it prevents some compiler optimisations for memory-mapped I/O but provides no atomicity or ordering. Use `std::atomic`.")
    yield qa("Is ++x on a std::atomic<int> thread-safe? What about x = x + 1?",
             "`++x` is a single atomic read-modify-write (`fetch_add`), so yes. `x = x + 1` is an atomic *load* followed by a separate atomic *store* — another thread can update `x` in between, so increments can be lost.")


@topic(G, "async-future", "async, future & promise", "hourglass-high")
def _():
    yield lead("`std::async` runs a function (possibly on another thread) and hands back a `std::future` — a handle to a result that will be available later. Exceptions travel through the future too.")
    yield section("`std::async` & `std::future`", "player-track-next")
    yield snippet("cpp", r'''
        #include <future>
        #include <iostream>
        #include <numeric>
        #include <stdexcept>
        #include <vector>

        long long sumRange(const std::vector<int>& v, std::size_t from, std::size_t to) {
            return std::accumulate(v.begin() + from, v.begin() + to, 0LL);
        }

        int main() {
            std::vector<int> v(10'000);
            std::iota(v.begin(), v.end(), 1);

            auto half = v.size() / 2;
            std::future<long long> first = std::async(std::launch::async, sumRange, std::cref(v), 0, half);
            long long second = sumRange(v, half, v.size());            // meanwhile, work on this thread
            std::cout << first.get() + second << '\n';                 // get() waits, then returns the value

            auto failing = std::async(std::launch::async, [] () -> int { throw std::runtime_error("task failed"); });
            try { failing.get(); }                                     // the exception is rethrown here
            catch (const std::exception& e) { std::cout << "caught: " << e.what() << '\n'; }
        }
    ''', out='''
        50005000
        caught: task failed
    ''', flags=("-Wno-unused-result",))
    yield table(
        ["Launch policy", "Behaviour"],
        ["`std::launch::async`", "Runs on a new thread immediately"],
        ["`std::launch::deferred`", "Runs lazily on the thread that calls `get()`/`wait()`"],
        ["default (`async | deferred`)", "Implementation chooses — pass `std::launch::async` if you need real concurrency"],
    )
    yield warn("The future returned by `std::async` **blocks in its destructor** until the task finishes. `std::async(f);` without keeping the future therefore runs synchronously — a common surprise.")
    yield section("`std::promise` — setting a future by hand", "send")
    yield snippet("cpp", r'''
        #include <future>
        #include <iostream>
        #include <string>
        #include <thread>

        int main() {
            std::promise<std::string> promise;
            std::future<std::string> result = promise.get_future();

            std::jthread worker([p = std::move(promise)]() mutable {
                p.set_value("downloaded 42 KB");                  // fulfils the future (once)
            });

            std::cout << result.get() << '\n';
        }
    ''', out="downloaded 42 KB")
    yield section("`std::packaged_task`", "package")
    yield snippet("cpp", r'''
        #include <future>
        #include <iostream>
        #include <thread>

        int main() {
            std::packaged_task<int(int, int)> task([](int a, int b) { return a * b; });   // wraps a callable
            std::future<int> f = task.get_future();
            std::jthread t(std::move(task), 6, 7);                // run it anywhere — e.g. a thread pool
            std::cout << f.get() << '\n';
        }
    ''', out="42")
    yield table(
        ["Tool", "Who produces the value", "Use for"],
        ["`std::async`", "The library runs your function", "Fire off a computation, collect the result"],
        ["`std::packaged_task`", "Whoever invokes the task", "Task queues / thread pools"],
        ["`std::promise`", "Your code calls `set_value`/`set_exception`", "Results produced by callbacks or events"],
        ["`std::shared_future`", "—", "Several threads waiting on the same result"],
    )
    yield qa("What's the difference between std::thread and std::async?",
             "`std::thread` just runs a function; getting a result or an exception back requires your own shared state and synchronisation. `std::async` returns a `std::future` that delivers the return value — or rethrows the exception — when you call `get()`, and with the default policy may not even create a thread.")
