from kit import *

G = "STL Containers & Iterators"


@topic(G, "stl-overview", "STL Overview", "building-warehouse")
def _():
    yield lead("The Standard Template Library is three ideas that plug together: **containers** hold data, **iterators** walk it, **algorithms** process it — all generic, all zero-overhead.")
    yield flow("Container", "Iterators `begin()`/`end()`", "Algorithm")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <list>
        #include <vector>

        int main() {
            std::vector<int> v{4, 1, 3};
            std::list<int> l{4, 1, 3};
            // The same algorithm works on any container through iterators:
            std::cout << *std::max_element(v.begin(), v.end()) << ' '
                      << *std::max_element(l.begin(), l.end()) << '\n';
            std::cout << std::count(v.begin(), v.end(), 3) << '\n';
        }
    ''', out='''
        4 4
        1
    ''')
    yield section("Container families", "category")
    yield table(
        ["Family", "Containers", "Organised by"],
        ["**Sequence**", "`vector`, `deque`, `list`, `forward_list`, `array`", "Position (the order you insert)"],
        ["**Ordered associative**", "`set`, `multiset`, `map`, `multimap`", "Sorted keys (red-black tree)"],
        ["**Unordered associative**", "`unordered_set/_multiset`, `unordered_map/_multimap`", "Hash of the key"],
        ["**Adaptors**", "`stack`, `queue`, `priority_queue`", "A restricted interface over another container"],
        ["**Views** (non-owning)", "`string_view`, `span`, ranges views", "Refer to someone else's data"],
    )
    yield section("Complexity cheat sheet", "clock")
    yield table(
        ["Container", "Access", "Search", "Insert/erase at end", "Insert/erase in middle / front"],
        ["`vector`", "O(1) random", "O(n)", "O(1) amortised", "O(n)"],
        ["`deque`", "O(1) random", "O(n)", "O(1)", "O(1) at front, O(n) middle"],
        ["`list`", "O(n)", "O(n)", "O(1)", "O(1) given an iterator"],
        ["`set` / `map`", "—", "O(log n)", "O(log n)", "O(log n)"],
        ["`unordered_set` / `unordered_map`", "—", "O(1) avg, O(n) worst", "O(1) avg", "O(1) avg"],
        ["`priority_queue`", "O(1) top", "—", "push/pop O(log n)", "—"],
    )
    yield section("Choosing a container", "route")
    yield steps(
        ("Default", "`std::vector` — contiguous, cache-friendly, fastest for most workloads, even with some middle inserts."),
        ("Need lookup by key?", "`std::unordered_map`/`unordered_set` for speed; `std::map`/`set` when you need sorted order or range queries (`lower_bound`)."),
        ("Push/pop at both ends?", "`std::deque`."),
        ("LIFO / FIFO / “always give me the max”?", "`std::stack` / `std::queue` / `std::priority_queue`."),
        ("Many inserts/erases in the middle with stable iterators?", "`std::list` — rarely the right answer in practice."),
    )
    yield qa("Why is std::vector usually faster than std::list even for insertions?",
             "A vector's elements are contiguous, so iterating and shifting elements is sequential memory access that the CPU cache and prefetcher love. A list node is a separate heap allocation; finding the insertion point means chasing pointers with a cache miss per node, which usually costs more than the O(n) shift in a vector for realistic sizes.")


@topic(G, "vector", "std::vector", "list")
def _():
    yield lead("A dynamic array: contiguous storage that grows automatically. The container you should reach for first.")
    yield section("Core operations", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v;                      // empty
            std::vector<int> zeros(5);               // 5 × 0
            std::vector<int> sevens(3, 7);           // 3 × 7
            std::vector<int> list{1, 2, 3};          // initializer list

            v.push_back(10);                         // append
            v.emplace_back(20);                      // construct in place
            v.insert(v.begin(), 5);                  // insert at front: O(n)
            std::cout << v.size() << ' ' << v.front() << ' ' << v.back() << ' ' << v[1] << '\n';

            v.pop_back();                            // remove last
            v.erase(v.begin());                      // remove first: O(n)
            std::cout << v.size() << ' ' << v[0] << '\n';

            list.resize(5);                          // grow with zeros
            std::cout << list[4] << ' ' << zeros.size() << ' ' << sevens[2] << '\n';
            list.clear();
            std::cout << list.empty() << '\n';
        }
    ''', out='''
        3 5 20 10
        1 10
        0 5 7
        1
    ''')
    yield section("Size vs capacity", "arrows-maximize")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v;
            std::size_t lastCap = 0;
            for (int i = 0; i < 100; ++i) {
                v.push_back(i);
                if (v.capacity() != lastCap) { lastCap = v.capacity(); std::cout << lastCap << ' '; }
            }
            std::cout << '\n';
            std::vector<int> r;
            r.reserve(100);                    // one allocation up front
            std::cout << r.size() << ' ' << r.capacity() << '\n';
            v.resize(10);
            v.shrink_to_fit();                 // non-binding request to release spare capacity
            std::cout << v.size() << ' ' << v.capacity() << '\n';
        }
    ''', out='''
        1 2 4 8 16 32 64 128
        0 100
        10 10
    ''')
    yield note("When full, `push_back` allocates a bigger buffer (libc++ and libstdc++ double it; MSVC grows by 1.5×), moves the elements over and frees the old one. Each element is moved O(1) times on average → **amortised O(1)** append. If you know the final size, `reserve` it.", "Growth")
    yield section("Iterator invalidation", "alert-triangle")
    yield table(
        ["Operation", "Invalidates"],
        ["`push_back` / `emplace_back` / `insert` causing reallocation", "**All** iterators, pointers, references"],
        ["`insert` without reallocation", "Those at or after the insertion point"],
        ["`erase`", "Those at or after the erased element"],
        ["`reserve`, `shrink_to_fit`", "All, if the capacity changes"],
    )
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v{1, 2, 3, 4, 5, 6};
            for (auto it = v.begin(); it != v.end(); ) {     // erase while iterating: use the returned iterator
                if (*it % 2 == 0) it = v.erase(it);
                else ++it;
            }
            for (int x : v) std::cout << x;
            std::cout << '\n';
            std::erase_if(v, [](int x) { return x > 3; });   // C++20 one-liner
            for (int x : v) std::cout << x;
            std::cout << '\n';
        }
    ''', out='''
        135
        13
    ''')
    yield section("2-D vectors & useful members", "grid-dots")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<std::vector<int>> grid(3, std::vector<int>(4, 0));   // 3 rows × 4 cols
            grid[1][2] = 5;
            std::cout << grid.size() << 'x' << grid[0].size() << ' ' << grid[1][2] << '\n';

            std::vector<int> a{1, 2, 3}, b{1, 2, 4};
            std::cout << (a < b) << (a == b) << '\n';        // lexicographic comparison
            a.swap(b);                                       // O(1)
            a.assign(2, 9);                                  // replace contents
            int* raw = a.data();                             // pointer to the contiguous buffer
            std::cout << a.size() << ' ' << raw[1] << ' ' << b.back() << '\n';
        }
    ''', out='''
        3x4 5
        10
        2 9 3
    ''')
    yield warn("`v[i]` doesn't check bounds (out-of-range is UB); `v.at(i)` throws `std::out_of_range`. And `std::vector<bool>` is a space-optimised bit-packed specialisation: `&v[0]` isn't a `bool*` and its elements aren't real references.")
    yield qa("What happens when you push_back into a full vector?",
             "It allocates a larger block (typically 2× or 1.5× the capacity), move-constructs (or copies, if the move constructor isn't `noexcept`) the existing elements into it, constructs the new element, destroys the old elements and frees the old block. All iterators, pointers and references into the vector are invalidated.")
    yield qa("What's the difference between reserve and resize?",
             "`reserve(n)` only changes *capacity* — it allocates room for `n` elements without creating any; `size()` is unchanged. `resize(n)` changes *size*: it creates value-initialised elements (or destroys extras), so `v[n-1]` becomes valid.")


@topic(G, "deque-list", "deque, list & forward_list", "arrows-left-right")
def _():
    yield lead("`std::deque` is a double-ended queue with O(1) push/pop at both ends and random access; `std::list` is a doubly linked list with O(1) splicing anywhere.")
    yield section("`std::deque`", "arrows-left-right")
    yield snippet("cpp", r'''
        #include <deque>
        #include <iostream>
        int main() {
            std::deque<int> d{3, 4};
            d.push_front(2);
            d.push_front(1);
            d.push_back(5);
            std::cout << d.front() << ' ' << d.back() << ' ' << d[2] << ' ' << d.size() << '\n';
            d.pop_front();
            d.pop_back();
            for (int x : d) std::cout << x;
            std::cout << '\n';
        }
    ''', out='''
        1 5 3 5
        234
    ''')
    yield p("Internally a deque is an array of fixed-size blocks, so growing at either end never moves existing elements (references stay valid on push at the ends) — but elements aren't contiguous overall.")
    yield section("`std::list`", "link")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <iterator>
        #include <list>

        int main() {
            std::list<int> l{5, 1, 4, 1, 3};
            auto it = std::next(l.begin(), 2);     // no random access: walk there
            l.insert(it, 99);                      // O(1) once you have the iterator
            l.remove(1);                           // remove all 1s
            l.sort();                              // member sort (std::sort needs random access)
            for (int x : l) std::cout << x << ' ';
            std::cout << '\n';

            std::list<int> other{7, 8};
            l.splice(l.begin(), other);            // move nodes from other in O(1) — no copies
            l.unique();                            // drop consecutive duplicates
            l.reverse();
            for (int x : l) std::cout << x << ' ';
            std::cout << "| other size " << other.size() << '\n';
        }
    ''', out='''
        3 4 5 99
        99 5 4 3 8 7 | other size 0
    ''')
    yield section("`std::forward_list`", "arrow-right")
    yield snippet("cpp", r'''
        #include <forward_list>
        #include <iostream>
        int main() {
            std::forward_list<int> fl{2, 3};       // singly linked: one pointer per node, no size()
            fl.push_front(1);
            fl.insert_after(fl.begin(), 10);       // only insert *after* a position
            for (int x : fl) std::cout << x << ' ';
            std::cout << '\n';
        }
    ''', out="1 10 2 3")
    yield table(
        ["", "`vector`", "`deque`", "`list`"],
        ["Random access `[i]`", "O(1)", "O(1)", "—"],
        ["push/pop front", "O(n)", "**O(1)**", "O(1)"],
        ["Insert in middle", "O(n)", "O(n)", "**O(1)** with iterator"],
        ["Contiguous memory", "Yes", "No (chunks)", "No (nodes)"],
        ["Iterators stay valid on insert", "No (reallocation)", "No (but refs do at ends)", "**Yes**"],
        ["Memory overhead", "Low", "Medium", "2 pointers per element"],
    )
    yield qa("When would you actually use std::list?",
             "When you need iterators/references to stay valid while inserting and erasing elsewhere, or you splice elements between lists in O(1) — e.g. an LRU cache (list + hash map of iterators). For plain sequences, `vector` wins on speed and memory.")


@topic(G, "set-multiset", "set & multiset", "circles")
def _():
    yield lead("`std::set` keeps unique keys in sorted order (a balanced binary search tree); `std::multiset` allows duplicates. Everything is O(log n).")
    yield section("`std::set`", "circle-dot")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <set>

        int main() {
            std::set<int> s{5, 1, 4, 1, 3};              // duplicates dropped, sorted
            for (int x : s) std::cout << x << ' ';
            std::cout << '\n';

            auto [it, inserted] = s.insert(4);            // already there
            std::cout << inserted << ' ' << *it << '\n';
            std::cout << s.count(3) << s.contains(9) << '\n';   // contains: C++20
            s.erase(1);
            std::cout << *s.begin() << ' ' << *s.rbegin() << ' ' << s.size() << '\n';   // min, max

            std::cout << *s.lower_bound(4) << ' ' << *s.upper_bound(4) << '\n';   // first >= 4, first > 4
        }
    ''', out='''
        1 3 4 5
        0 4
        10
        3 5 3
        4 5
    ''')
    yield section("Custom order", "arrows-sort")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>
        #include <set>
        #include <string>

        struct ByLength {
            bool operator()(const std::string& a, const std::string& b) const {
                return a.size() != b.size() ? a.size() < b.size() : a < b;   // tie-break so distinct words stay distinct
            }
        };

        int main() {
            std::set<int, std::greater<int>> desc{3, 1, 2};
            for (int x : desc) std::cout << x;
            std::cout << '\n';
            std::set<std::string, ByLength> words{"banana", "fig", "apple", "kiwi", "pear"};
            for (const auto& w : words) std::cout << w << ' ';
            std::cout << '\n';
        }
    ''', out='''
        321
        fig kiwi pear apple banana
    ''')
    yield warn("Set elements are `const` — you can't modify a key in place (it would break the ordering). Erase and re-insert, or use C++17 `extract` to modify a node's key without reallocating.")
    yield section("`std::multiset`", "circles")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <set>
        int main() {
            std::multiset<int> ms{3, 1, 3, 2, 3};
            std::cout << ms.count(3) << ' ' << ms.size() << '\n';
            ms.erase(ms.find(3));           // erase ONE copy
            std::cout << ms.count(3) << '\n';
            ms.erase(3);                    // erase ALL copies
            for (int x : ms) std::cout << x;
            std::cout << '\n';
        }
    ''', out='''
        3 5
        2
        12
    ''')
    yield note("A `multiset` works as a *sliding-window sorted bag*: insert/erase in O(log n) and read the min/max from `begin()`/`rbegin()` — handy for “median / max of the last k elements” problems.", "DSA use")
    yield qa("How is std::set implemented and what are its complexities?",
             "As a self-balancing binary search tree (a red-black tree in all major implementations). Insert, erase and find are O(log n); iteration visits keys in sorted order; `lower_bound`/`upper_bound` answer “first key ≥ / > x” in O(log n).")


@topic(G, "map-multimap", "map & multimap", "map")
def _():
    yield lead("`std::map<K, V>` stores key → value pairs sorted by key, with unique keys and O(log n) operations. `std::multimap` allows repeated keys.")
    yield section("Core operations", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <string>

        int main() {
            std::map<std::string, int> stock{{"apple", 5}, {"pear", 2}};
            stock["kiwi"] = 7;                          // insert or overwrite
            stock["apple"] += 1;
            stock.insert({"pear", 100});                // no effect: key exists
            stock.emplace("fig", 3);

            for (const auto& [fruit, qty] : stock) std::cout << fruit << '=' << qty << ' ';   // sorted by key
            std::cout << '\n';

            if (auto it = stock.find("kiwi"); it != stock.end()) std::cout << "kiwi: " << it->second << '\n';
            std::cout << stock.count("mango") << ' ' << stock.contains("fig") << '\n';
            stock.erase("pear");
            std::cout << stock.size() << ' ' << stock.at("fig") << '\n';
        }
    ''', out='''
        apple=6 fig=3 kiwi=7 pear=2
        kiwi: 7
        0 1
        3 3
    ''')
    yield section("The `operator[]` trap", "alert-triangle")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <string>
        int main() {
            std::map<std::string, int> ages{{"ada", 36}};
            if (ages["bob"] == 0) std::cout << "bob not found?\n";   // [] INSERTS "bob" with 0!
            std::cout << ages.size() << '\n';
            // const std::map<...>& cref = ages; cref["x"];          // error: no const operator[]
            try { std::cout << ages.at("cy"); } catch (const std::out_of_range&) { std::cout << "at() throws\n"; }
        }
    ''', out='''
        bob not found?
        2
        at() throws
    ''')
    yield table(
        ["Access", "Missing key", "Use for"],
        ["`m[key]`", "Inserts a default-constructed value", "Counting, building up (`freq[word]++`)"],
        ["`m.at(key)`", "Throws `std::out_of_range`", "Must exist"],
        ["`m.find(key)`", "Returns `m.end()`", "Lookup without side effects"],
        ["`m.contains(key)` (C++20) / `m.count(key)`", "`false` / `0`", "Existence check"],
        ["`m.insert_or_assign(k, v)` / `m.try_emplace(k, args…)`", "Inserts", "Explicit upsert / insert-if-absent"],
    )
    yield section("Word frequency & range queries", "chart-bar")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <sstream>
        #include <string>

        int main() {
            std::istringstream text("the cat and the hat and the bat");
            std::map<std::string, int> freq;
            std::string w;
            while (text >> w) ++freq[w];
            for (const auto& [word, n] : freq) std::cout << word << ':' << n << ' ';
            std::cout << '\n';

            std::map<int, std::string> events{{900, "standup"}, {1200, "lunch"}, {1500, "review"}, {1800, "gym"}};
            for (auto it = events.lower_bound(1000); it != events.upper_bound(1600); ++it)   // keys in [1000, 1600]
                std::cout << it->first << ' ' << it->second << '\n';
        }
    ''', out='''
        and:2 bat:1 cat:1 hat:1 the:3
        1200 lunch
        1500 review
    ''')
    yield section("`std::multimap`", "sitemap")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <string>
        int main() {
            std::multimap<std::string, std::string> phone{{"ada", "111"}, {"bob", "222"}, {"ada", "333"}};
            auto [first, last] = phone.equal_range("ada");     // all entries with key "ada"
            for (auto it = first; it != last; ++it) std::cout << it->second << ' ';
            std::cout << phone.count("ada") << '\n';
        }
    ''', out="111 333 2")
    yield qa("map vs unordered_map?",
             "`map` is a balanced BST: O(log n) operations, keys iterated in sorted order, supports `lower_bound`/range queries, needs `<`. `unordered_map` is a hash table: O(1) average (O(n) worst) operations, no ordering, needs `std::hash` and `==`. Use `unordered_map` for pure lookup speed, `map` when order or ranges matter or worst-case guarantees are needed.")


@topic(G, "unordered-containers", "unordered_map & unordered_set", "hash")
def _():
    yield lead("Hash tables: average O(1) insert, erase and lookup, no ordering. The workhorse for frequency counts, “seen before?” checks and caches.")
    yield section("Usage", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <string>
        #include <unordered_map>
        #include <unordered_set>
        #include <vector>

        int main() {
            std::vector<int> nums{2, 7, 11, 15};
            int target = 18;
            std::unordered_map<int, int> seen;              // value → index
            for (int i = 0; i < static_cast<int>(nums.size()); ++i) {
                if (auto it = seen.find(target - nums[i]); it != seen.end())
                    std::cout << "two-sum: " << it->second << ',' << i << '\n';
                seen[nums[i]] = i;
            }

            std::unordered_set<std::string> visited;
            for (std::string city : {"paris", "rome", "paris"})
                if (!visited.insert(city).second) std::cout << "repeat: " << city << '\n';
            std::cout << visited.size() << ' ' << visited.contains("rome") << '\n';
        }
    ''', out='''
        two-sum: 1,2
        repeat: paris
        2 1
    ''')
    yield warn("Iteration order of unordered containers is unspecified and can change after a rehash or between library versions. Never print or depend on it — copy into a `std::vector` and sort if you need a stable order.")
    yield section("Buckets, load factor, rehashing", "database")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <unordered_map>
        int main() {
            std::unordered_map<int, int> m;
            m.reserve(1000);                              // pre-size buckets: avoids rehashing while filling
            for (int i = 0; i < 1000; ++i) m[i] = i * i;
            std::cout << m.size() << ' ' << (m.bucket_count() >= 1000) << ' ' << (m.load_factor() <= m.max_load_factor()) << '\n';
            std::cout << m.max_load_factor() << '\n';     // default 1.0: rehash when size > buckets
        }
    ''', out='''
        1000 1 1
        1
    ''')
    yield section("Hashing your own type", "fingerprint")
    yield snippet("cpp", r'''
        #include <cstddef>
        #include <functional>
        #include <iostream>
        #include <unordered_set>

        struct Point {
            int x, y;
            bool operator==(const Point&) const = default;          // needed for collisions
        };

        struct PointHash {
            std::size_t operator()(const Point& p) const noexcept {
                std::size_t h1 = std::hash<int>{}(p.x), h2 = std::hash<int>{}(p.y);
                return h1 ^ (h2 + 0x9e3779b9 + (h1 << 6) + (h1 >> 2));   // hash_combine
            }
        };

        int main() {
            std::unordered_set<Point, PointHash> cells{{0, 0}, {1, 2}, {0, 0}};
            std::cout << cells.size() << ' ' << cells.count({1, 2}) << '\n';
        }
    ''', out="2 1")
    yield table(
        ["", "`unordered_map`", "`map`"],
        ["Structure", "Hash table (buckets of nodes)", "Red-black tree"],
        ["Lookup", "O(1) avg, O(n) worst", "O(log n) always"],
        ["Order", "None", "Sorted by key"],
        ["Key needs", "`std::hash<K>` + `==`", "`<`"],
        ["Memory", "Higher (buckets)", "3 pointers + colour per node"],
    )
    yield warn("In competitive programming, adversarial inputs can force many collisions in `std::unordered_map<int, …>` (the default `std::hash<int>` is the identity), turning O(1) into O(n). Use a randomised custom hash, or `std::map`.")
    yield qa("How does an unordered_map handle collisions?",
             "The standard containers use *separate chaining*: each bucket holds a linked list of the nodes whose hash maps there. When the load factor (size / bucket count) exceeds `max_load_factor` (default 1.0), the table allocates more buckets and rehashes every element.")


@topic(G, "container-adaptors", "stack, queue & priority_queue", "stack")
def _():
    yield lead("Container adaptors wrap a sequence container and expose only a restricted interface: LIFO (`stack`), FIFO (`queue`) or “largest first” (`priority_queue`).")
    yield section("`std::stack` & `std::queue`", "stack-push")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <queue>
        #include <stack>
        #include <string>

        bool balanced(const std::string& s) {
            std::stack<char> st;
            for (char c : s) {
                if (c == '(' || c == '[' || c == '{') st.push(c);
                else {
                    if (st.empty()) return false;
                    char open = st.top();
                    st.pop();
                    if ((c == ')' && open != '(') || (c == ']' && open != '[') || (c == '}' && open != '{')) return false;
                }
            }
            return st.empty();
        }

        int main() {
            std::cout << balanced("{[()]}") << balanced("([)]") << '\n';

            std::queue<std::string> q;                  // FIFO
            q.push("first"); q.push("second"); q.push("third");
            q.pop();
            std::cout << q.front() << ' ' << q.back() << ' ' << q.size() << '\n';
        }
    ''', out='''
        10
        second third 2
    ''')
    yield table(
        ["Adaptor", "Operations", "Default underlying container"],
        ["`stack<T>`", "`push`, `pop`, `top`, `empty`, `size`", "`deque<T>`"],
        ["`queue<T>`", "`push`, `pop`, `front`, `back`, `empty`, `size`", "`deque<T>`"],
        ["`priority_queue<T>`", "`push`, `pop`, `top`, `empty`, `size`", "`vector<T>` (binary heap)"],
    )
    yield warn("`pop()` returns `void` — read `top()`/`front()` first. Calling `top()`, `front()` or `pop()` on an empty adaptor is undefined behaviour. None of them are iterable.")
    yield section("`std::priority_queue`", "sort-descending")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <string>
        #include <vector>

        int main() {
            std::priority_queue<int> maxHeap;                                   // largest on top
            for (int x : {3, 1, 4, 1, 5}) maxHeap.push(x);
            std::cout << maxHeap.top() << ' ';
            maxHeap.pop();
            std::cout << maxHeap.top() << '\n';

            std::priority_queue<int, std::vector<int>, std::greater<int>> minHeap{std::greater<int>(), {3, 1, 4}};
            std::cout << minHeap.top() << '\n';                                 // smallest on top

            using Task = std::pair<int, std::string>;                           // (priority, name)
            auto cmp = [](const Task& a, const Task& b) { return a.first > b.first; };   // lower number = more urgent
            std::priority_queue<Task, std::vector<Task>, decltype(cmp)> tasks(cmp);
            tasks.push({2, "email"}); tasks.push({1, "outage"}); tasks.push({3, "lunch"});
            while (!tasks.empty()) { std::cout << tasks.top().second << ' '; tasks.pop(); }
            std::cout << '\n';
        }
    ''', out='''
        5 4
        1
        outage email lunch
    ''')
    yield note("The comparator says “`a` has *lower* priority than `b`” — so `std::less` (default) gives a max-heap and `std::greater` a min-heap. It's the reverse of what you'd expect from sorting.", "Comparator direction")
    yield section("Top-k with a heap", "trophy")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        int main() {
            std::vector<int> scores{50, 90, 20, 70, 85, 60};
            std::priority_queue<int, std::vector<int>, std::greater<int>> top3;   // min-heap of size k
            for (int s : scores) {
                top3.push(s);
                if (top3.size() > 3) top3.pop();       // drop the smallest: O(n log k)
            }
            while (!top3.empty()) { std::cout << top3.top() << ' '; top3.pop(); }
            std::cout << '\n';
        }
    ''', out="70 85 90")
    yield qa("How is priority_queue implemented?",
             "As a binary heap stored in a `std::vector`, using `std::push_heap`/`std::pop_heap`: `top` is O(1), `push` and `pop` are O(log n), and building from n elements is O(n). It has no decrease-key; Dijkstra implementations push duplicates and skip stale entries instead.")


@topic(G, "pair-tuple", "pair & tuple", "brackets-contain")
def _():
    yield lead("`std::pair<A, B>` holds two values; `std::tuple<Ts...>` holds any number. Both compare lexicographically, which makes them handy as keys and sort criteria.")
    yield section("`std::pair`", "code")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <utility>
        #include <vector>

        int main() {
            std::pair<std::string, int> p{"ada", 36};
            auto q = std::make_pair(std::string("bob"), 25);
            std::cout << p.first << ' ' << p.second << ' ' << (p < q) << '\n';

            std::vector<std::pair<int, char>> v{{2, 'b'}, {1, 'z'}, {2, 'a'}};
            std::sort(v.begin(), v.end());                  // by first, then by second
            for (const auto& [n, c] : v) std::cout << n << c << ' ';
            std::cout << '\n';
        }
    ''', out='''
        ada 36 1
        1z 2a 2b
    ''')
    yield section("`std::tuple`", "brackets")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <tuple>

        std::tuple<int, int, int> minMaxSum(int a, int b, int c) {
            return {std::min({a, b, c}), std::max({a, b, c}), a + b + c};
        }

        int main() {
            std::tuple<std::string, int, double> t{"x", 1, 2.5};
            std::cout << std::get<0>(t) << ' ' << std::get<int>(t) << ' ' << std::tuple_size_v<decltype(t)> << '\n';

            auto [lo, hi, sum] = minMaxSum(4, 9, 2);        // structured bindings
            std::cout << lo << ' ' << hi << ' ' << sum << '\n';

            int a, b;
            std::tie(a, b, std::ignore) = minMaxSum(1, 2, 3);   // unpack into existing variables
            std::cout << a << b << '\n';

            auto joined = std::tuple_cat(std::make_tuple(1, 'c'), std::make_tuple(2.5));
            std::cout << std::get<2>(joined) << '\n';
        }
    ''', out='''
        x 1 3
        2 9 15
        13
        2.5
    ''')
    yield section("Multi-key comparison with `std::tie`", "arrows-sort")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <tuple>
        #include <vector>

        struct Student { std::string name; int grade; int age; };

        int main() {
            std::vector<Student> s{{"cy", 90, 20}, {"al", 85, 22}, {"bo", 90, 19}};
            std::sort(s.begin(), s.end(), [](const Student& a, const Student& b) {
                return std::tie(b.grade, a.age) < std::tie(a.grade, b.age);   // grade desc, then age asc
            });
            for (const auto& st : s) std::cout << st.name << ' ';
            std::cout << '\n';
        }
    ''', out="bo cy al")
    yield note("For anything with meaning, prefer a small named `struct` over `pair`/`tuple`: `result.quotient` reads better than `std::get<0>(result)`. Tuples shine in generic code and quick multi-value returns.")
    yield qa("How do pairs and tuples compare?",
             "Lexicographically: compare the first elements; only if they're equal compare the second, and so on. This is why sorting a `vector<pair<int,int>>` sorts by `first` then `second`, and why `std::tie(a.x, a.y) < std::tie(b.x, b.y)` is the idiomatic multi-field comparison.")


@topic(G, "iterators", "Iterators", "arrow-right-circle")
def _():
    yield lead("An iterator is a generalised pointer: it points to an element, `*it` reads it, `++it` moves on. Iterators are the glue that lets any algorithm run on any container.")
    yield section("Basics", "code")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <iterator>
        #include <vector>

        int main() {
            std::vector<int> v{10, 20, 30, 40};
            for (auto it = v.begin(); it != v.end(); ++it) std::cout << *it << ' ';   // [begin, end)
            std::cout << '\n';
            for (auto it = v.rbegin(); it != v.rend(); ++it) std::cout << *it << ' '; // reverse
            std::cout << '\n';

            auto it = v.begin() + 2;                    // random access
            std::cout << *it << ' ' << it[1] << ' ' << (it - v.begin()) << '\n';
            std::cout << *std::next(v.begin()) << ' ' << *std::prev(v.end()) << ' ' << std::distance(v.begin(), v.end()) << '\n';

            for (auto cit = v.cbegin(); cit != v.cend(); ++cit) { /* *cit = 0; would not compile */ }
        }
    ''', out='''
        10 20 30 40
        40 30 20 10
        30 40 2
        20 40 4
    ''')
    yield note("`end()` points **one past** the last element — it marks the end and must never be dereferenced. An empty container has `begin() == end()`.", "Half-open ranges")
    yield section("Iterator categories", "stairs")
    yield table(
        ["Category", "Supports", "Example containers"],
        ["Input / Output", "Single pass: `++`, `*` (read or write)", "`istream_iterator` / `ostream_iterator`, `back_inserter`"],
        ["Forward", "Multi-pass `++`", "`forward_list`, `unordered_*`"],
        ["Bidirectional", "+ `--`", "`list`, `set`, `map`"],
        ["Random access", "+ `it + n`, `it[n]`, `<`, `it2 - it1`", "`deque`"],
        ["Contiguous (C++20)", "+ elements adjacent in memory", "`vector`, `array`, `string`, raw arrays"],
    )
    yield p("Algorithms state what they need: `std::sort` requires random access (so `std::list` has its own `sort()`), `std::reverse` needs bidirectional, `std::find` just input.")
    yield section("Iterator adaptors", "plug")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <iterator>
        #include <sstream>
        #include <vector>

        int main() {
            std::istringstream in("5 3 8 1");
            std::vector<int> v(std::istream_iterator<int>{in}, std::istream_iterator<int>{});   // read all ints

            std::vector<int> evens;
            std::copy_if(v.begin(), v.end(), std::back_inserter(evens), [](int x) { return x % 2 == 0; });

            std::copy(v.begin(), v.end(), std::ostream_iterator<int>(std::cout, ","));   // print with separator
            std::cout << " evens=" << evens.size() << '\n';
        }
    ''', out="5,3,8,1, evens=1")
    yield section("Making your own class iterable", "repeat")
    yield snippet("cpp", r'''
        #include <iostream>

        class Range {                                   // like Python's range(lo, hi)
            int lo_, hi_;
        public:
            Range(int lo, int hi) : lo_(lo), hi_(hi) {}
            struct iterator {
                int cur;
                int operator*() const { return cur; }
                iterator& operator++() { ++cur; return *this; }
                bool operator==(const iterator&) const = default;
            };
            iterator begin() const { return {lo_}; }
            iterator end() const { return {hi_}; }
        };

        int main() {
            for (int i : Range(3, 7)) std::cout << i << ' ';
            std::cout << '\n';
        }
    ''', out="3 4 5 6")
    yield warn("An iterator is only valid while its container isn't restructured: e.g. a `vector` reallocation or erasing the element it points to invalidates it. Using an invalidated iterator is undefined behaviour.")
    yield qa("Why does the STL use half-open ranges [begin, end)?",
             "An empty range is simply `begin == end`, the length is `end - begin`, loops are `while (it != end)`, and ranges split cleanly: `[a, m)` and `[m, b)` share no element and miss none. It also allows `end()` for containers where a “last element” pointer would be awkward.")
