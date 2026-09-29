from kit import *

G = "STL Algorithms & Ranges"


@topic(G, "algorithms-basics", "Searching & Counting Algorithms", "search")
def _():
    yield lead("`<algorithm>` has ~100 well-tested, optimised functions that work on iterator ranges. Knowing the common ones replaces most hand-written loops.")
    yield section("Find & count", "zoom")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>

        int main() {
            std::vector<int> v{4, 8, 15, 16, 23, 42};

            auto it = std::find(v.begin(), v.end(), 15);
            std::cout << "15 at index " << (it - v.begin()) << '\n';
            if (std::find(v.begin(), v.end(), 99) == v.end()) std::cout << "99 not found\n";

            auto odd = std::find_if(v.begin(), v.end(), [](int x) { return x % 2 == 1; });
            std::cout << "first odd " << *odd << '\n';

            std::cout << std::count(v.begin(), v.end(), 42) << ' '
                      << std::count_if(v.begin(), v.end(), [](int x) { return x > 10; }) << '\n';

            std::string s = "mississippi";
            std::cout << std::count(s.begin(), s.end(), 's') << '\n';
        }
    ''', out='''
        15 at index 2
        99 not found
        first odd 15
        1 4
        4
    ''')
    yield section("Predicates over a range", "checks")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v{2, 4, 6, 7};
            auto even = [](int x) { return x % 2 == 0; };
            std::cout << std::all_of(v.begin(), v.end(), even)
                      << std::any_of(v.begin(), v.end(), even)
                      << std::none_of(v.begin(), v.end(), [](int x) { return x < 0; }) << '\n';

            auto [mn, mx] = std::minmax_element(v.begin(), v.end());
            std::cout << *mn << ' ' << *mx << ' ' << *std::max_element(v.begin(), v.end()) << '\n';
            std::cout << std::max({3, 9, 1}) << ' ' << std::min(5, 2) << ' ' << std::clamp(15, 0, 10) << '\n';

            std::vector<int> w{2, 4, 6, 8};
            std::cout << std::equal(v.begin(), v.begin() + 3, w.begin()) << '\n';     // first 3 equal?
            auto mm = std::mismatch(v.begin(), v.end(), w.begin());
            std::cout << *mm.first << " vs " << *mm.second << '\n';
        }
    ''', out='''
        011
        2 7 7
        9 2 10
        1
        7 vs 8
    ''')
    yield section("Searching for sequences", "text-scan-2")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> data{1, 2, 3, 1, 2, 3, 4};
            std::vector<int> pat{2, 3, 4};
            auto it = std::search(data.begin(), data.end(), pat.begin(), pat.end());
            std::cout << "pattern at " << (it - data.begin()) << '\n';
            auto adj = std::adjacent_find(data.begin(), data.end(), [](int a, int b) { return b < a; });
            std::cout << "first descent at " << (adj - data.begin()) << '\n';
        }
    ''', out='''
        pattern at 4
        first descent at 2
    ''')
    yield table(
        ["Algorithm", "Returns", "Complexity"],
        ["`find`, `find_if`, `find_if_not`", "Iterator to first match or `last`", "O(n)"],
        ["`count`, `count_if`", "Number of matches", "O(n)"],
        ["`all_of`, `any_of`, `none_of`", "`bool`", "O(n), short-circuits"],
        ["`min_element`, `max_element`, `minmax_element`", "Iterator(s)", "O(n)"],
        ["`equal`, `mismatch`", "`bool` / pair of iterators", "O(n)"],
        ["`search`, `find_end`, `adjacent_find`", "Iterator", "O(n·m) / O(n)"],
        ["`binary_search`, `lower_bound`, …", "On **sorted** ranges", "O(log n)"],
    )
    yield qa("Why prefer std algorithms over raw loops?",
             "They name the intent (`any_of` says more than a loop with a flag), they're correct and well-tested (no off-by-one), they're optimised (and some have parallel versions), and they compose with iterators and ranges. Sean Parent's advice: “no raw loops”.")


@topic(G, "modifying-algorithms", "Transforming & Modifying Algorithms", "wand")
def _():
    yield lead("Algorithms that write: copy, transform, fill, replace, reverse, rotate — and the remove-erase idiom, the most misunderstood algorithm pair in the STL.")
    yield section("Copy, transform, fill", "copy")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <cctype>
        #include <iostream>
        #include <iterator>
        #include <string>
        #include <vector>

        int main() {
            std::vector<int> src{1, 2, 3, 4};
            std::vector<int> dst(src.size());
            std::transform(src.begin(), src.end(), dst.begin(), [](int x) { return x * x; });

            std::vector<int> sums;
            std::transform(src.begin(), src.end(), dst.begin(), std::back_inserter(sums), std::plus<>{});   // binary

            std::vector<int> big;
            std::copy_if(dst.begin(), dst.end(), std::back_inserter(big), [](int x) { return x > 4; });

            std::string s = "Hello";
            std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return std::toupper(c); });

            std::vector<int> filled(4);
            std::fill(filled.begin(), filled.end(), 7);
            std::fill_n(filled.begin(), 2, 0);

            for (auto* vec : {&dst, &sums, &big, &filled}) {
                for (int x : *vec) std::cout << x << ' ';
                std::cout << "| ";
            }
            std::cout << s << '\n';
        }
    ''', out="1 4 9 16 | 2 6 12 20 | 9 16 | 0 0 7 7 | HELLO")
    yield warn("Output algorithms don't grow the destination. `std::copy(a.begin(), a.end(), empty.begin())` writes past the end of an empty vector — use `std::back_inserter(empty)` or size the destination first.")
    yield section("The remove–erase idiom", "trash")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 0, 2, 0, 3, 0};
            auto newEnd = std::remove(v.begin(), v.end(), 0);   // shifts keepers forward; size unchanged!
            std::cout << v.size() << ' ' << (newEnd - v.begin()) << '\n';
            v.erase(newEnd, v.end());                           // actually shrink
            for (int x : v) std::cout << x;
            std::cout << '\n';

            std::vector<int> w{5, 6, 7, 8, 9};
            w.erase(std::remove_if(w.begin(), w.end(), [](int x) { return x % 2; }), w.end());
            std::erase(w, 8);                                   // C++20: both steps in one call
            for (int x : w) std::cout << x;
            std::cout << '\n';
        }
    ''', out='''
        6 3
        123
        6
    ''')
    yield note("`std::remove` can't change a container's size — it only sees iterators. It moves the elements to keep to the front and returns the new logical end; `erase` removes the leftover tail. In C++20, `std::erase` / `std::erase_if` do both.", "Why two steps?")
    yield section("Reorder: reverse, rotate, unique, shuffle", "arrows-shuffle")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <random>
        #include <vector>

        void show(const std::vector<int>& v) { for (int x : v) std::cout << x; std::cout << ' '; }

        int main() {
            std::vector<int> v{1, 2, 3, 4, 5};
            std::reverse(v.begin(), v.end());              show(v);
            std::rotate(v.begin(), v.begin() + 2, v.end()); show(v);   // element at +2 becomes first

            std::vector<int> d{1, 1, 2, 2, 2, 3, 1};
            d.erase(std::unique(d.begin(), d.end()), d.end());          // collapse *adjacent* duplicates
            show(d);

            std::vector<int> r{1, 2, 3};
            std::replace(r.begin(), r.end(), 2, 9);                      show(r);
            std::swap(r[0], r[2]);                                       show(r);

            std::mt19937 rng(42);
            std::vector<int> deck{1, 2, 3, 4, 5};
            std::shuffle(deck.begin(), deck.end(), rng);
            std::sort(deck.begin(), deck.end());                         show(deck);   // back in order
            std::cout << '\n';
        }
    ''', out="54321 32154 1231 193 391 12345")
    yield section("Dedupe a whole vector", "filter")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        int main() {
            std::vector<int> v{3, 1, 3, 2, 1};
            std::sort(v.begin(), v.end());                        // 1 1 2 3 3
            v.erase(std::unique(v.begin(), v.end()), v.end());    // 1 2 3
            for (int x : v) std::cout << x << ' ';
            std::cout << '\n';
        }
    ''', out="1 2 3")
    yield qa("What does std::unique do?",
             "It removes *consecutive* duplicate elements by shifting the unique ones forward and returning the new logical end (like `remove`). To dedupe an arbitrary vector, sort it first, then `erase(unique(...), end())`.")


@topic(G, "sorting", "Sorting & Custom Comparators", "arrows-sort")
def _():
    yield lead("`std::sort` is an introsort: O(n log n) worst case, not stable. Its relatives handle stability, partial results and selection.")
    yield section("`std::sort` and comparators", "sort-ascending")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <functional>
        #include <iostream>
        #include <string>
        #include <vector>

        struct Employee { std::string name; int dept; int salary; };

        int main() {
            std::vector<int> v{5, 2, 9, 1, 5, 6};
            std::sort(v.begin(), v.end());                         // ascending
            std::sort(v.begin(), v.end(), std::greater<>());       // descending
            for (int x : v) std::cout << x;
            std::cout << '\n';

            std::vector<std::string> words{"kiwi", "fig", "banana", "apple"};
            std::sort(words.begin(), words.end(), [](const auto& a, const auto& b) {
                return a.size() < b.size();                        // by length
            });
            for (const auto& w : words) std::cout << w << ' ';
            std::cout << '\n';

            std::vector<Employee> staff{{"ann", 2, 70}, {"bob", 1, 50}, {"cat", 2, 90}, {"dan", 1, 60}};
            std::sort(staff.begin(), staff.end(), [](const Employee& a, const Employee& b) {
                if (a.dept != b.dept) return a.dept < b.dept;      // dept ascending
                return a.salary > b.salary;                        // then salary descending
            });
            for (const auto& e : staff) std::cout << e.name << ' ';
            std::cout << '\n';
        }
    ''', out='''
        965521
        fig kiwi apple banana
        dan bob cat ann
    ''')
    yield warn("A comparator must be a **strict weak ordering**: `comp(a, a)` must be `false`. Using `<=` instead of `<` breaks that and can make `std::sort` read out of bounds or crash.")
    yield section("Stable, partial, nth", "stairs")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <utility>
        #include <vector>

        int main() {
            std::vector<std::pair<int, std::string>> v{{2, "b1"}, {1, "a"}, {2, "b2"}, {1, "c"}};
            std::stable_sort(v.begin(), v.end(), [](const auto& x, const auto& y) { return x.first < y.first; });
            for (const auto& [k, s] : v) std::cout << s << ' ';      // equal keys keep original order
            std::cout << '\n';

            std::vector<int> scores{50, 90, 20, 70, 85, 60};
            std::partial_sort(scores.begin(), scores.begin() + 3, scores.end(), std::greater<>());
            std::cout << scores[0] << ' ' << scores[1] << ' ' << scores[2] << '\n';     // top 3, sorted

            std::vector<int> m{7, 1, 5, 3, 9};
            std::nth_element(m.begin(), m.begin() + 2, m.end());    // median in O(n) average
            std::cout << "median " << m[2] << '\n';

            std::vector<int> p{1, 2, 3, 4, 5, 6};
            auto mid = std::partition(p.begin(), p.end(), [](int x) { return x % 2 == 0; });
            std::cout << (mid - p.begin()) << " evens first\n";
            std::cout << std::is_sorted(p.begin(), p.end()) << '\n';
        }
    ''', out='''
        a c b1 b2
        90 85 70
        median 5
        3 evens first
        0
    ''')
    yield table(
        ["Algorithm", "Result", "Complexity", "Stable"],
        ["`sort`", "Fully sorted", "O(n log n)", "No"],
        ["`stable_sort`", "Fully sorted, equal elements keep order", "O(n log n) (O(n log² n) without extra memory)", "Yes"],
        ["`partial_sort(first, mid, last)`", "Smallest `mid-first` elements sorted at the front", "O(n log k)", "No"],
        ["`nth_element`", "Element at *n* is what it would be if sorted; smaller before, larger after", "O(n) avg", "No"],
        ["`partition` / `stable_partition`", "Predicate-true elements first", "O(n)", "No / Yes"],
        ["`list::sort()`", "For `std::list` (no random access)", "O(n log n)", "Yes"],
    )
    yield section("Sort indices, not objects", "list-numbers")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <numeric>
        #include <vector>
        int main() {
            std::vector<int> height{170, 155, 182, 160};
            std::vector<int> idx(height.size());
            std::iota(idx.begin(), idx.end(), 0);                       // 0 1 2 3
            std::sort(idx.begin(), idx.end(), [&](int a, int b) { return height[a] < height[b]; });
            for (int i : idx) std::cout << i << ' ';                    // argsort
            std::cout << '\n';
        }
    ''', out="1 3 0 2")
    yield qa("What algorithm does std::sort use?",
             "*Introsort*: quicksort with median-of-three pivots, switching to heapsort if the recursion gets too deep (guaranteeing O(n log n) worst case) and to insertion sort for small partitions. It's not stable; use `std::stable_sort` (a merge sort) when the order of equal elements matters.")


@topic(G, "binary-search", "Binary Search: lower_bound & upper_bound", "binary")
def _():
    yield lead("On a **sorted** range, the STL's binary searches answer “where would x go?” in O(log n). `lower_bound` is the one to remember.")
    yield section("The four functions", "search")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{1, 3, 3, 3, 5, 8};
            //                 0  1  2  3  4  5
            auto lb = std::lower_bound(v.begin(), v.end(), 3);   // first element >= 3
            auto ub = std::upper_bound(v.begin(), v.end(), 3);   // first element >  3
            std::cout << (lb - v.begin()) << ' ' << (ub - v.begin()) << " count=" << (ub - lb) << '\n';

            std::cout << std::binary_search(v.begin(), v.end(), 5)
                      << std::binary_search(v.begin(), v.end(), 4) << '\n';

            auto [lo, hi] = std::equal_range(v.begin(), v.end(), 3);
            std::cout << (lo - v.begin()) << ' ' << (hi - v.begin()) << '\n';

            auto pos = std::lower_bound(v.begin(), v.end(), 6);   // insertion point that keeps v sorted
            v.insert(pos, 6);
            for (int x : v) std::cout << x;
            std::cout << '\n';
            std::cout << (std::lower_bound(v.begin(), v.end(), 100) == v.end()) << '\n';   // all smaller → end()
        }
    ''', out='''
        1 4 count=3
        10
        1 4
        1333568
        1
    ''')
    yield table(
        ["Call", "Returns"],
        ["`lower_bound(x)`", "First position with element **≥ x**"],
        ["`upper_bound(x)`", "First position with element **> x**"],
        ["`equal_range(x)`", "`{lower_bound, upper_bound}` — all elements equal to x"],
        ["`binary_search(x)`", "`bool` only"],
    )
    yield section("Common recipes", "chef-hat")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>

        int main() {
            std::vector<int> v{2, 4, 4, 7, 9};
            int x = 5;
            // largest element < x
            auto it = std::lower_bound(v.begin(), v.end(), x);
            if (it != v.begin()) std::cout << "floor-ish " << *std::prev(it) << '\n';
            // number of elements <= 4
            std::cout << "count<=4 " << (std::upper_bound(v.begin(), v.end(), 4) - v.begin()) << '\n';

            // descending data: pass the same comparator used to sort
            std::vector<int> d{9, 7, 4, 2};
            auto p = std::lower_bound(d.begin(), d.end(), 5, std::greater<>());   // first element <= 5
            std::cout << *p << '\n';
        }
    ''', out='''
        floor-ish 4
        count<=4 3
        4
    ''')
    yield section("Binary search on the answer", "target")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <vector>

        // Minimum capacity to ship all packages within `days` days (LeetCode 1011 style).
        bool canShip(const std::vector<int>& w, int days, int cap) {
            int used = 1, load = 0;
            for (int x : w) {
                if (x > cap) return false;
                if (load + x > cap) { ++used; load = 0; }
                load += x;
            }
            return used <= days;
        }

        int main() {
            std::vector<int> w{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
            int lo = 1, hi = 55;                        // answer is in [lo, hi]
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;           // avoids overflow of (lo + hi)
                if (canShip(w, 5, mid)) hi = mid;       // feasible: try smaller
                else lo = mid + 1;
            }
            std::cout << lo << '\n';
        }
    ''', out="15")
    yield note("For `std::set`/`std::map` use the **member** `s.lower_bound(x)` (O(log n)). `std::lower_bound(s.begin(), s.end(), x)` also compiles, but tree iterators aren't random access, so it's O(n).", "Sets & maps")
    yield qa("What's the difference between lower_bound and upper_bound?",
             "`lower_bound(x)` returns the first position whose element is not less than `x` (≥ x); `upper_bound(x)` the first whose element is greater than `x`. Their difference is the number of elements equal to `x`; if `x` is absent both return the same insertion point.")


@topic(G, "numeric-algorithms", "Numeric Algorithms", "sum")
def _():
    yield lead("`<numeric>` covers folds and scans: sums, products, prefix sums, dot products, sequences, `gcd`/`lcm`.")
    yield section("Folds", "sum")
    yield snippet("cpp", r'''
        #include <functional>
        #include <iostream>
        #include <numeric>
        #include <string>
        #include <vector>

        int main() {
            std::vector<int> v{1, 2, 3, 4, 5};
            std::cout << std::accumulate(v.begin(), v.end(), 0) << '\n';                        // sum
            std::cout << std::accumulate(v.begin(), v.end(), 1LL, std::multiplies<>()) << '\n'; // product
            std::cout << std::reduce(v.begin(), v.end()) << '\n';                              // like accumulate, may reorder

            std::vector<std::string> words{"a", "b", "c"};
            std::string joined = std::accumulate(std::next(words.begin()), words.end(), words[0],
                                                 [](std::string acc, const std::string& w) { return acc + "-" + w; });
            std::cout << joined << '\n';

            std::vector<int> a{1, 2, 3}, b{4, 5, 6};
            std::cout << std::inner_product(a.begin(), a.end(), b.begin(), 0) << '\n';          // dot product
        }
    ''', out='''
        15
        120
        15
        a-b-c
        32
    ''')
    yield warn("The *type of the initial value* decides the accumulator type. `std::accumulate(v.begin(), v.end(), 0)` on `double`s truncates every partial sum to `int`; on big `int`s it overflows. Pass `0.0` or `0LL`.")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <numeric>
        #include <vector>
        int main() {
            std::vector<double> prices{1.5, 2.5, 3.5};
            std::cout << std::accumulate(prices.begin(), prices.end(), 0) << ' '       // int accumulator!
                      << std::accumulate(prices.begin(), prices.end(), 0.0) << '\n';
        }
    ''', out="6 7.5")
    yield section("Scans & sequences", "stairs-up")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <numeric>
        #include <vector>

        int main() {
            std::vector<int> v{3, 1, 4, 1, 5};
            std::vector<int> prefix(v.size());
            std::partial_sum(v.begin(), v.end(), prefix.begin());               // running total
            for (int x : prefix) std::cout << x << ' ';
            std::cout << "| sum[1..3] = " << prefix[3] - prefix[0] << '\n';     // range sum in O(1)

            std::vector<int> diff(v.size());
            std::adjacent_difference(v.begin(), v.end(), diff.begin());
            for (int x : diff) std::cout << x << ' ';
            std::cout << '\n';

            std::vector<int> ids(5);
            std::iota(ids.begin(), ids.end(), 10);                              // 10 11 12 13 14
            std::cout << ids.back() << ' ' << std::gcd(84, 36) << ' ' << std::lcm(4, 6) << '\n';

            std::vector<int> ex(v.size());
            std::exclusive_scan(v.begin(), v.end(), ex.begin(), 0);             // sums *before* each element
            for (int x : ex) std::cout << x << ' ';
            std::cout << '\n';
        }
    ''', out='''
        3 4 8 9 14 | sum[1..3] = 6
        3 -2 3 -3 4
        14 12 12
        0 3 4 8 9
    ''')
    yield table(
        ["Algorithm", "Computes"],
        ["`accumulate(f, l, init, op)`", "Left fold, in order"],
        ["`reduce(f, l, init, op)`", "Fold in any order (parallelisable; `op` must be associative & commutative)"],
        ["`inner_product` / `transform_reduce`", "Σ aᵢ·bᵢ (or custom ops)"],
        ["`partial_sum` / `inclusive_scan`", "Prefix sums including the current element"],
        ["`exclusive_scan`", "Prefix sums excluding it"],
        ["`adjacent_difference`", "`out[i] = in[i] - in[i-1]`"],
        ["`iota(f, l, start)`", "Fill with `start, start+1, …`"],
        ["`gcd`, `lcm`", "C++17"],
    )
    yield qa("How do prefix sums answer range-sum queries in O(1)?",
             "Precompute `pre[i] = a[0] + … + a[i-1]` (size n+1, `pre[0] = 0`) once in O(n). Then the sum of `a[l..r]` is `pre[r+1] - pre[l]` — one subtraction per query.")


@topic(G, "ranges", "Ranges & Views (C++20)", "filter")
def _():
    yield lead("C++20 ranges let you pass a whole container to an algorithm (`std::ranges::sort(v)`) and build lazy pipelines with views: `v | views::filter(...) | views::transform(...)`.")
    yield section("Range algorithms", "arrows-sort")
    yield snippet("cpp", r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>

        struct Person { std::string name; int age; };

        int main() {
            std::vector<int> v{5, 3, 9, 1};
            std::ranges::sort(v);                                   // no begin()/end() noise
            std::cout << v.front() << ' ' << std::ranges::max(v) << ' ' << std::ranges::count(v, 3) << '\n';

            std::vector<Person> people{{"cy", 30}, {"al", 25}, {"bo", 35}};
            std::ranges::sort(people, {}, &Person::age);            // projection: sort by a member
            for (const auto& p : people) std::cout << p.name << ' ';
            std::cout << '\n';
            auto it = std::ranges::find(people, "bo", &Person::name);
            std::cout << it->age << '\n';
        }
    ''', out='''
        1 9 1
        al cy bo
        35
    ''')
    yield section("Views: lazy pipelines", "arrow-right-bar")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <ranges>
        #include <vector>

        int main() {
            namespace views = std::views;
            std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

            auto evenSquares = v | views::filter([](int x) { return x % 2 == 0; })
                                 | views::transform([](int x) { return x * x; });
            for (int x : evenSquares) std::cout << x << ' ';           // computed on the fly, no temp vector
            std::cout << '\n';

            for (int x : views::iota(1) | views::take(5)) std::cout << x;      // infinite range, first 5
            std::cout << '\n';
            for (int x : v | views::reverse | views::drop(7)) std::cout << x;
            std::cout << '\n';
            for (int x : v | views::take_while([](int x) { return x < 4; })) std::cout << x;
            std::cout << '\n';
        }
    ''', out='''
        4 16 36 64 100
        12345
        321
        123
    ''')
    yield table(
        ["View", "Produces"],
        ["`views::filter(pred)`", "Elements satisfying `pred`"],
        ["`views::transform(f)`", "`f(x)` for each element"],
        ["`views::take(n)` / `views::drop(n)`", "First n / all but first n"],
        ["`views::take_while(p)` / `views::drop_while(p)`", "Prefix while `p` holds / the rest"],
        ["`views::reverse`", "Reverse order"],
        ["`views::iota(a, b)`", "`a, a+1, …, b-1` (unbounded without `b`)"],
        ["`views::keys` / `views::values` / `views::elements<N>`", "Parts of pairs/tuples"],
        ["`views::split(delim)`, `views::join`", "Split / flatten"],
        ["`views::enumerate`, `views::zip`, `views::chunk`", "C++23"],
    )
    yield section("Views over maps, strings & collecting results", "map")
    yield snippet("cpp", r'''
        #include <iostream>
        #include <map>
        #include <ranges>
        #include <string>
        #include <string_view>
        #include <vector>

        int main() {
            std::map<std::string, int> stock{{"apple", 0}, {"kiwi", 4}, {"pear", 2}};
            for (const auto& name : stock | std::views::filter([](const auto& kv) { return kv.second > 0; })
                                          | std::views::keys)
                std::cout << name << ' ';
            std::cout << '\n';

            std::string_view csv = "red,green,blue";
            for (auto part : csv | std::views::split(','))
                std::cout << '[' << std::string_view(part.begin(), part.end()) << ']';
            std::cout << '\n';

            auto sq = std::views::iota(1, 6) | std::views::transform([](int x) { return x * x; });
            std::vector<int> out(sq.begin(), sq.end());          // materialise (C++23: std::ranges::to<std::vector>())
            std::cout << out.size() << ' ' << out.back() << '\n';
        }
    ''', out='''
        kiwi pear
        [red][green][blue]
        5 25
    ''')
    yield warn("Views don't own data. A view over a temporary container (`auto v = getVector() | views::filter(f);`) or one kept after its container changed will dangle. Some views (`filter`) also cache their `begin()` — don't modify the elements through them in a way that changes the predicate.")
    yield qa("What is the difference between a range algorithm and a view?",
             "A range algorithm (`std::ranges::sort(v)`) is eager — it does its work immediately, like classic algorithms but taking a whole range and supporting projections. A view (`views::filter`) is lazy — a lightweight, non-owning adaptor that computes elements only when iterated, so pipelines don't create intermediate containers.")
