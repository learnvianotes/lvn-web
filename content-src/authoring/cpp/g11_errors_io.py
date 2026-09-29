from kit import *

G = "Errors, Streams & Utilities"


@topic(G, "exceptions", "Exceptions", "alert-octagon")
def _():
    yield lead("`throw` signals an error that the current function can't handle; the stack unwinds (destroying locals) until a matching `catch` is found.")
    yield section("throw / try / catch", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>
        #include <string>

        double divide(double a, double b) {
            if (b == 0) throw std::invalid_argument("division by zero");
            return a / b;
        }

        int parseAge(const std::string& s) {
            int age = std::stoi(s);                          // may throw invalid_argument / out_of_range
            if (age < 0 || age > 150) throw std::out_of_range("age " + s + " out of range");
            return age;
        }

        int main() {
            try {
                std::cout << divide(10, 4) << '\n';
                std::cout << divide(1, 0) << '\n';           // throws — the rest of the try is skipped
                std::cout << "never printed\n";
            } catch (const std::invalid_argument& e) {
                std::cout << "invalid: " << e.what() << '\n';
            }

            for (std::string input : {"42", "abc", "200"}) {
                try {
                    std::cout << parseAge(input) << '\n';
                } catch (const std::out_of_range& e) {       // most specific first
                    std::cout << "range: " << e.what() << '\n';
                } catch (const std::exception& e) {          // any standard exception
                    std::cout << "error: " << e.what() << '\n';
                } catch (...) {                              // anything at all
                    std::cout << "unknown\n";
                }
            }
        }
    ''', out='''
        2.5
        invalid: division by zero
        42
        error: stoi: no conversion
        range: age 200 out of range
    ''')
    yield note("Throw by value, catch by **const reference** (`catch (const std::exception& e)`). Catching by value copies and *slices* derived exceptions; catching by reference keeps their dynamic type and `what()`.", "Rule")
    yield section("The standard hierarchy", "hierarchy")
    yield table(
        ["Exception", "Thrown by / used for"],
        ["`std::exception`", "Base of all — has `virtual const char* what()`"],
        ["`std::logic_error` → `invalid_argument`, `out_of_range`, `length_error`, `domain_error`", "Bugs detectable before running: bad arguments, `vector::at`, `stoi`"],
        ["`std::runtime_error` → `range_error`, `overflow_error`, `system_error`", "Errors only detectable at run time: I/O, OS"],
        ["`std::bad_alloc`", "`new` failed"],
        ["`std::bad_cast`, `std::bad_optional_access`, `std::bad_variant_access`, `std::bad_function_call`", "Misused library types"],
    )
    yield section("Custom exceptions & rethrowing", "tool")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>
        #include <string>

        class HttpError : public std::runtime_error {
        public:
            HttpError(int code, const std::string& msg)
                : std::runtime_error(msg), code_(code) {}
            int code() const noexcept { return code_; }
        private:
            int code_;
        };

        void fetch() { throw HttpError(404, "page not found"); }

        void handler() {
            try {
                fetch();
            } catch (const HttpError& e) {
                std::cout << "log: " << e.code() << '\n';
                throw;                                       // rethrow the SAME exception object
            }
        }

        int main() {
            try { handler(); }
            catch (const std::exception& e) { std::cout << "top level: " << e.what() << '\n'; }
        }
    ''', out='''
        log: 404
        top level: page not found
    ''')
    yield section("Stack unwinding", "stack-pop")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>
        struct Guard {
            const char* name;
            ~Guard() { std::cout << "cleanup " << name << '\n'; }
        };
        void inner() { Guard g{"inner"}; throw std::runtime_error("fail"); }
        void outer() { Guard g{"outer"}; inner(); }
        int main() {
            try { outer(); } catch (const std::exception& e) { std::cout << "caught " << e.what() << '\n'; }
        }
    ''', out='''
        cleanup inner
        cleanup outer
        caught fail
    ''')
    yield dodont("Use exceptions for *exceptional* failures that the immediate caller can't sensibly handle (I/O failure, invalid config, out of memory). Rely on RAII so unwinding cleans up.", "Using exceptions for normal control flow (e.g. “not found” in a lookup), throwing from destructors, or `catch (...) {}` that silently swallows errors.")
    yield warn("If an exception escapes `main` (or any `noexcept` function), `std::terminate` is called and the program aborts — destructors of the remaining stack may not run.")
    yield qa("What happens when an exception is thrown?",
             "The exception object is copied/moved into special storage, then the runtime searches up the call stack for a matching `catch`. Each frame it leaves is *unwound*: local objects are destroyed in reverse order. When a handler matches (by type, allowing derived-to-base), it runs; if none matches, `std::terminate` is called.")
    yield qa("Exceptions vs error codes?",
             "Exceptions can't be ignored silently, separate the error path from the happy path, and carry rich information through many layers. Error codes (or `std::optional`/`std::expected`) are explicit in the signature, cheaper when failure is common, and required where exceptions are disabled (some embedded/game code). Many code bases use exceptions for rare failures and return values for expected ones.")


@topic(G, "noexcept-exception-safety", "noexcept & Exception Safety", "shield-check")
def _():
    yield lead("`noexcept` promises a function won't throw — enabling optimisations like moving elements during `vector` growth. Exception-safety guarantees describe what state is left behind when something *does* throw.")
    yield section("`noexcept`", "shield")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <type_traits>
        #include <utility>
        #include <vector>

        int safeAdd(int a, int b) noexcept { return a + b; }
        void mayThrow() { throw 1; }

        template <typename T>
        void swapValues(T& a, T& b) noexcept(std::is_nothrow_move_constructible_v<T>) {   // conditional
            T tmp = std::move(a);
            a = std::move(b);
            b = std::move(tmp);
        }

        int main() {
            std::cout << std::boolalpha
                      << noexcept(safeAdd(1, 2)) << ' '          // noexcept operator: compile-time query
                      << noexcept(mayThrow()) << ' '
                      << std::is_nothrow_move_constructible_v<std::string> << ' '
                      << std::is_nothrow_move_constructible_v<std::vector<int>> << '\n';
            std::string a = "x", b = "y";
            swapValues(a, b);
            std::cout << a << b << '\n';
        }
    ''', out='''
        true false true true
        yx
    ''')
    yield snippet("cpp", r'''
        #include <stdexcept>
        void promise() noexcept {
            throw std::runtime_error("broken promise");   // compiles, but calls std::terminate at run time
        }
        int main() { promise(); }
    ''', fails=True, flags=("-Wno-exceptions",), caption="C++ — throwing from noexcept terminates")
    yield ul(
        "Destructors, `operator delete` and (by default) compiler-generated move operations of well-behaved members are `noexcept`.",
        "Mark move constructors/assignments and `swap` `noexcept` — containers depend on it.",
        "Don't mark functions `noexcept` if they might throw someday; removing it later breaks callers that relied on it.",
    )
    yield section("The exception-safety guarantees", "stairs")
    yield table(
        ["Guarantee", "Promise if an exception is thrown", "Example"],
        ["**No-throw**", "Never throws", "Destructors, `swap`, move operations"],
        ["**Strong**", "Commit-or-rollback: state is unchanged", "`vector::push_back` (when the move ctor is `noexcept` or copyable)"],
        ["**Basic**", "No leaks, invariants hold, but state may have changed", "Most operations"],
        ["**None**", "Anything goes — avoid", "Code with raw `new`/`delete`"],
    )
    yield section("Getting the strong guarantee: copy-and-swap", "arrows-exchange")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <stdexcept>
        #include <string>
        #include <vector>

        class Inventory {
            std::vector<std::string> items_;
        public:
            void addAll(const std::vector<std::string>& newItems) {
                std::vector<std::string> copy = items_;          // 1. work on a copy
                for (const auto& it : newItems) {
                    if (it.empty()) throw std::invalid_argument("empty item");
                    copy.push_back(it);
                }
                items_.swap(copy);                               // 2. commit with a no-throw swap
            }
            std::size_t size() const { return items_.size(); }
        };

        int main() {
            Inventory inv;
            inv.addAll({"pen", "ink"});
            try { inv.addAll({"cap", "", "pad"}); } catch (const std::exception& e) { std::cout << e.what() << '\n'; }
            std::cout << inv.size() << '\n';                      // still 2: nothing half-added
        }
    ''', out='''
        empty item
        2
    ''')
    yield qa("Why are destructors implicitly noexcept?",
             "Destructors run during stack unwinding. If one threw while another exception was already propagating, C++ couldn't handle two exceptions at once and would call `std::terminate`. Making them `noexcept` by default turns that into a clear rule: never let exceptions escape a destructor.")


@topic(G, "optional-variant-any", "optional, variant & any", "box-multiple-1")
def _():
    yield lead("C++17 vocabulary types: `std::optional<T>` for “a value or nothing”, `std::variant<A, B, …>` for “exactly one of these types”, `std::any` for “any type at all”.")
    yield section("`std::optional`", "circle-dashed")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <optional>
        #include <string>

        std::optional<int> findAge(const std::map<std::string, int>& db, const std::string& name) {
            auto it = db.find(name);
            if (it == db.end()) return std::nullopt;          // “no value” — no sentinel like -1
            return it->second;
        }

        int main() {
            std::map<std::string, int> db{{"ada", 36}};
            if (auto age = findAge(db, "ada")) std::cout << "ada " << *age << '\n';     // contextual bool
            auto missing = findAge(db, "bob");
            std::cout << missing.has_value() << ' ' << missing.value_or(-1) << '\n';
            try { std::cout << missing.value(); }                                       // throws if empty
            catch (const std::bad_optional_access&) { std::cout << "bad_optional_access\n"; }

            std::optional<std::string> nick;
            nick = "Addy";
            nick.reset();
            nick.emplace(3, 'z');
            std::cout << *nick << ' ' << nick->size() << '\n';
        }
    ''', out='''
        ada 36
        0 -1
        bad_optional_access
        zzz 3
    ''')
    yield note("`optional` stores the value *inline* (no heap allocation) plus a `bool`. Use it for return values that may be absent and for optional members; don't use `optional<T&>` (not allowed) — use `T*` for optional references.")
    yield section("`std::variant` — a type-safe union", "switch-3")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <variant>
        #include <vector>

        template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };   // visitor helper

        using Json = std::variant<std::nullptr_t, bool, int, std::string>;

        int main() {
            std::vector<Json> values{nullptr, true, 42, std::string("hi")};
            for (const auto& v : values) {
                std::visit(overloaded{
                    [](std::nullptr_t)          { std::cout << "null\n"; },
                    [](bool b)                  { std::cout << "bool " << b << '\n'; },
                    [](int i)                   { std::cout << "int " << i << '\n'; },
                    [](const std::string& s)    { std::cout << "string " << s << '\n'; },
                }, v);
            }

            std::variant<int, std::string> x = 5;
            std::cout << x.index() << ' ' << std::holds_alternative<int>(x) << ' ' << std::get<int>(x) << '\n';
            x = "now a string";
            if (auto* s = std::get_if<std::string>(&x)) std::cout << *s << '\n';
            try { std::get<int>(x); } catch (const std::bad_variant_access&) { std::cout << "bad_variant_access\n"; }
        }
    ''', out='''
        null
        bool 1
        int 42
        string hi
        0 1 5
        now a string
        bad_variant_access
    ''', flags=("-Wno-unused-result",))
    yield p("A `variant` holds exactly one alternative at a time, knows which (`index()`), and its size is the largest alternative plus a tag. It's the value-semantic alternative to a class hierarchy when the set of types is closed: no heap, no virtual calls, and `std::visit` forces you to handle every case.")
    yield section("`std::any`", "question-mark")
    yield snippet("cpp", r'''
        #include <any>
        #include <iostream>
        #include <string>

        int main() {
            std::any a = 42;
            std::cout << a.type().name() << ' ' << std::any_cast<int>(a) << '\n';
            a = std::string("text");
            if (auto* s = std::any_cast<std::string>(&a)) std::cout << *s << '\n';   // pointer form: nullptr on mismatch
            try { std::any_cast<double>(a); } catch (const std::bad_any_cast&) { std::cout << "bad_any_cast\n"; }
            a.reset();
            std::cout << a.has_value() << '\n';
        }
    ''', out='''
        i 42
        text
        bad_any_cast
        0
    ''', flags=("-Wno-unused-result",))
    yield table(
        ["Type", "Holds", "Checked by", "Typical use"],
        ["`optional<T>`", "A `T` or nothing", "`has_value()`, `if (opt)`", "Maybe-absent results"],
        ["`variant<Ts...>`", "Exactly one of a *closed* set of types", "`index()`, `holds_alternative`, `visit`", "State machines, AST nodes, message types, parse results"],
        ["`any`", "Any copyable type", "`any_cast` (run time)", "Rarely: plugin/config bags with unknown types"],
    )
    yield note("C++23 adds `std::expected<T, E>` — a value **or an error** — for error handling without exceptions. (libc++ in C++20 mode doesn't provide it; with `-std=c++23` it's available.)", "C++23")
    yield qa("When would you use std::variant instead of inheritance?",
             "When the set of alternatives is fixed and known (closed), you want value semantics (copyable, no heap allocation), and you're adding *operations* more often than *types*. Inheritance suits open sets of types where new subclasses get added and operations are fixed.")


@topic(G, "file-streams", "File I/O with fstream", "file-text")
def _():
    yield lead("`<fstream>` gives you `std::ofstream` (write), `std::ifstream` (read) and `std::fstream` (both). They work exactly like `cin`/`cout` and close themselves (RAII).")
    yield section("Write, then read back", "file-pencil")
    yield snippet("cpp", r'''
        #include <cstdio>
        #include <fstream>
        #include <iostream>
        #include <string>

        int main() {
            {
                std::ofstream out("scores.txt");                 // truncates / creates
                if (!out) { std::cerr << "cannot open\n"; return 1; }
                out << "ada 91\n" << "bob 78\n" << "cy 85\n";
            }                                                     // closed (and flushed) here

            {
                std::ofstream app("scores.txt", std::ios::app);  // append mode
                app << "dee 99\n";
            }

            std::ifstream in("scores.txt");
            std::string name;
            int score, total = 0, count = 0;
            while (in >> name >> score) {                         // token-by-token
                total += score;
                ++count;
            }
            std::cout << count << " students, average " << total / count << '\n';

            in.clear();                                           // reset EOF flag…
            in.seekg(0);                                          // …and rewind
            std::string line;
            std::getline(in, line);                               // line-by-line
            std::cout << "first line: " << line << '\n';
            in.close();
            std::remove("scores.txt");
        }
    ''', out='''
        4 students, average 88
        first line: ada 91
    ''')
    yield table(
        ["Mode flag", "Meaning"],
        ["`std::ios::in` / `std::ios::out`", "Read / write (defaults for `ifstream` / `ofstream`)"],
        ["`std::ios::app`", "Every write goes to the end"],
        ["`std::ios::trunc`", "Discard existing contents (default for `ofstream`)"],
        ["`std::ios::binary`", "No newline translation (matters on Windows)"],
        ["`std::ios::ate`", "Start at the end, but may seek anywhere"],
    )
    yield section("Stream state", "traffic-lights")
    yield table(
        ["Check", "True when"],
        ["`if (stream)` / `!stream.fail()`", "Last operation succeeded"],
        ["`stream.eof()`", "Tried to read past the end"],
        ["`stream.fail()`", "Format error or EOF (e.g. reading letters into an `int`)"],
        ["`stream.bad()`", "Unrecoverable I/O error"],
        ["`stream.clear()`", "Resets the flags so you can continue"],
    )
    yield warn("`while (!in.eof()) { in >> x; … }` processes the last value twice (or garbage) because `eof()` only becomes true *after* a read fails. Loop on the read itself: `while (in >> x)` / `while (std::getline(in, line))`.")
    yield section("Binary files & whole-file reads", "binary")
    yield snippet("cpp", r'''
        #include <cstdio>
        #include <fstream>
        #include <iostream>
        #include <sstream>
        #include <vector>

        int main() {
            std::vector<int> data{1, 2, 3, 1000000};
            {
                std::ofstream out("data.bin", std::ios::binary);
                out.write(reinterpret_cast<const char*>(data.data()), data.size() * sizeof(int));
            }
            std::ifstream in("data.bin", std::ios::binary);
            std::vector<int> back(4);
            in.read(reinterpret_cast<char*>(back.data()), back.size() * sizeof(int));
            std::cout << in.gcount() << " bytes, last = " << back[3] << '\n';

            std::ofstream("note.txt") << "line one\nline two\n";
            std::ifstream t("note.txt");
            std::stringstream buffer;
            buffer << t.rdbuf();                                  // slurp the whole file
            std::cout << buffer.str().size() << " chars\n";
            std::remove("data.bin");
            std::remove("note.txt");
        }
    ''', out='''
        16 bytes, last = 1000000
        18 chars
    ''')
    yield note("For paths, directories, file sizes and existence checks, use `<filesystem>` (C++17): `std::filesystem::exists(p)`, `file_size(p)`, `directory_iterator`, `create_directories`.", "std::filesystem")
    yield qa("Do you need to call close() on an fstream?",
             "Usually not: the destructor flushes and closes the file when the stream goes out of scope (RAII). Call `close()` explicitly when you want to reuse the stream object, check for errors on close, or make sure data is on disk before doing something else with the file.")


@topic(G, "stringstream", "String Streams", "text-wrap")
def _():
    yield lead("`std::stringstream` (from `<sstream>`) is a stream whose buffer is a string — use it to parse text with `>>` or to build strings with `<<`.")
    yield section("Parsing", "scan")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <sstream>
        #include <string>
        #include <vector>

        int main() {
            std::istringstream in("3 4.5 hello 7");
            int a; double b; std::string word; int c;
            in >> a >> b >> word >> c;
            std::cout << a + c << ' ' << b << ' ' << word << '\n';

            std::string line = "10,20,30";
            std::stringstream ss(line);
            std::vector<int> nums;
            for (std::string tok; std::getline(ss, tok, ',');) nums.push_back(std::stoi(tok));
            std::cout << nums.size() << ' ' << nums[2] << '\n';

            std::istringstream bad("12abc");
            int n; std::string rest;
            bad >> n >> rest;                     // reads 12, then "abc"
            std::cout << n << ' ' << rest << '\n';

            std::istringstream words("  the   quick brown  ");
            int count = 0;
            for (std::string w; words >> w;) ++count;
            std::cout << count << " words\n";
        }
    ''', out='''
        10 4.5 hello
        3 30
        12 abc
        3 words
    ''')
    yield section("Building strings", "writing")
    yield snippet("cpp", r'''
        #include <iomanip>
        #include <iostream>
        #include <sstream>
        #include <string>

        std::string toHex(int value) {
            std::ostringstream os;
            os << "0x" << std::hex << std::setw(4) << std::setfill('0') << value;
            return os.str();
        }

        int main() {
            std::ostringstream report;
            report << "total=" << 42 << ", ratio=" << std::fixed << std::setprecision(2) << 0.4567;
            std::cout << report.str() << '\n';
            std::cout << toHex(255) << '\n';

            report.str("");                        // reuse: reset the contents…
            report.clear();                        // …and the state flags
            report << "fresh";
            std::cout << report.str() << '\n';
        }
    ''', out='''
        total=42, ratio=0.46
        0x00ff
        fresh
    ''')
    yield table(
        ["Class", "Direction"],
        ["`std::istringstream`", "Read from a string (`>>`, `getline`)"],
        ["`std::ostringstream`", "Write into a string (`<<`, then `.str()`)"],
        ["`std::stringstream`", "Both"],
    )
    yield note("For simple number formatting `std::format` / `std::to_string` are faster and clearer; for fast number parsing without exceptions or locale, use `std::from_chars` (`<charconv>`).")
    yield qa("How do you split a string by a delimiter in C++?",
             "Wrap it in a `std::stringstream` and call `std::getline(ss, token, delim)` in a loop — or, in C++20, iterate `str | std::views::split(delim)`. For whitespace-separated tokens, just use `ss >> token`.")


@topic(G, "chrono", "Time with <chrono>", "clock")
def _():
    yield lead("`<chrono>` models time with types: *durations* (`5s`, `250ms`), *time points* (a clock reading) and *clocks*. Units are checked at compile time — no more “was that seconds or milliseconds?”.")
    yield section("Durations", "hourglass")
    yield snippet("cpp", r'''
        #include <chrono>
        #include <iostream>

        int main() {
            using namespace std::chrono_literals;
            using namespace std::chrono;

            auto timeout = 2s + 500ms;                         // std::chrono::milliseconds (2500)
            std::cout << timeout.count() << "ms\n";

            seconds s = duration_cast<seconds>(timeout);        // lossy conversion must be explicit
            std::cout << s.count() << "s\n";

            minutes m = 90min;
            hours h = duration_cast<hours>(m);
            std::cout << h.count() << "h " << (m - h).count() << "min\n";

            duration<double> secs = timeout;                    // floating-point seconds: implicit is fine
            std::cout << secs.count() << '\n';
            std::cout << (1h > 59min) << '\n';
        }
    ''', out='''
        2500ms
        2s
        1h 30min
        2.5
        1
    ''')
    yield section("Measuring elapsed time", "stopwatch")
    yield snippet("cpp", r'''
        #include <chrono>
        #include <iostream>
        #include <numeric>
        #include <vector>

        int main() {
            auto start = std::chrono::steady_clock::now();       // monotonic: right clock for measuring
            std::vector<long long> v(1'000'000);
            std::iota(v.begin(), v.end(), 1);
            long long sum = std::accumulate(v.begin(), v.end(), 0LL);
            auto end = std::chrono::steady_clock::now();

            auto us = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            std::cout << "sum = " << sum << '\n';
            std::cout << "took " << us.count() << " us\n";      // varies run to run
        }
    ''', out=None)
    yield table(
        ["Clock", "Use"],
        ["`steady_clock`", "Measuring intervals (never goes backwards)"],
        ["`system_clock`", "Wall-clock time; convertible to calendar dates / `time_t`"],
        ["`high_resolution_clock`", "Alias of one of the above — prefer `steady_clock` explicitly"],
    )
    yield section("Calendar dates (C++20)", "calendar")
    yield snippet("cpp", r'''
        #include <chrono>
        #include <format>
        #include <iostream>

        int main() {
            using namespace std::chrono;
            year_month_day launch = 2024y / March / 15;
            sys_days d = launch;
            sys_days later = d + days(30);
            std::cout << std::format("{} -> {}\n", launch, year_month_day{later});
            std::cout << weekday{d} << ' ' << (2024y).is_leap() << '\n';
            std::cout << std::format("{}\n", 1500ms);
        }
    ''', out='''
        2024-03-15 -> 2024-04-14
        Fri 1
        1500ms
    ''')
    yield qa("Why use std::chrono instead of plain integers for time?",
             "The unit is part of the type, so `sleep_for(5)` doesn't compile (5 what?) but `sleep_for(5s)` does, and conversions between units are exact and automatic when lossless (`2s` → `2000ms`) but must be explicit when lossy (`duration_cast`). That eliminates a whole class of unit bugs at zero run-time cost.")


@topic(G, "random", "Random Numbers with <random>", "dice-5")
def _():
    yield lead("Modern C++ separates *engines* (sources of random bits) from *distributions* (shape the bits into the numbers you want). Forget `rand() % n`.")
    yield section("Engine + distribution", "dice")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <random>

        int main() {
            std::mt19937 rng(12345);                             // Mersenne Twister, fixed seed → reproducible
            std::uniform_int_distribution<int> dice(1, 6);       // inclusive range
            std::uniform_real_distribution<double> unit(0.0, 1.0);

            for (int i = 0; i < 5; ++i) std::cout << dice(rng) << ' ';
            std::cout << '\n';

            int counts[7] = {};
            for (int i = 0; i < 60000; ++i) ++counts[dice(rng)];
            bool roughlyUniform = true;
            for (int f = 1; f <= 6; ++f) roughlyUniform &= counts[f] > 9500 && counts[f] < 10500;
            std::cout << "uniform: " << roughlyUniform << '\n';

            double u = unit(rng);
            std::cout << (u >= 0.0 && u < 1.0) << '\n';
        }
    ''', out=None)
    yield p("Exact numbers from a seeded engine are reproducible for a given standard library, but *distributions* are implementation-defined, so libc++ and libstdc++ may print different dice rolls for the same seed.")
    yield section("Seeding", "plant")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <random>
        #include <vector>

        int main() {
            std::random_device rd;                               // non-deterministic seed source (OS entropy)
            std::mt19937 rng(rd());                              // different sequence every run
            std::vector<int> deck{1, 2, 3, 4, 5, 6, 7, 8};
            std::shuffle(deck.begin(), deck.end(), rng);
            std::sort(deck.begin(), deck.end());
            std::cout << deck.front() << deck.back() << '\n';    // deterministic after sorting
        }
    ''', out="18")
    yield table(
        ["Distribution", "Produces"],
        ["`uniform_int_distribution<int>(a, b)`", "Integers in [a, b]"],
        ["`uniform_real_distribution<double>(a, b)`", "Reals in [a, b)"],
        ["`normal_distribution<double>(mean, sd)`", "Gaussian"],
        ["`bernoulli_distribution(p)`", "`true` with probability p"],
        ["`discrete_distribution<int>{w...}`", "Index i with probability ∝ wᵢ"],
        ["`poisson_distribution`, `exponential_distribution`", "Counts, waiting times"],
    )
    yield dodont("Create **one** engine (seeded once) and reuse it; pass it by reference to functions that need randomness.", "Re-creating `std::mt19937 rng(std::random_device{}())` on every call, or `rand() % 6` (biased, low quality, global state).")
    yield warn("`std::mt19937` is fast and statistically good but **not** cryptographically secure — never use it for passwords, tokens or keys.")
    yield qa("What's wrong with rand() % n?",
             "`rand()` has implementation-defined (often poor) quality and a range that may be as small as 32767; `% n` introduces *modulo bias* when `RAND_MAX + 1` isn't a multiple of `n`; and it uses hidden global state that's not thread-safe. `<random>` fixes all three.")
