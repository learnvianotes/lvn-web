from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Arrays & Strings"


@topic(G, "list", "List", "list-numbers")
def _():
    yield lead("A list is Python's **dynamic array**: an ordered, index-addressable, resizable collection (the same idea as C++ `std::vector`, Java `ArrayList` and the JavaScript `Array`). Arrays are the foundation that almost every other data structure is built on, so knowing exactly what is cheap and what is expensive on one is the first DSA skill.")
    yield define("Array", "a block of elements stored in **contiguous** memory, so element `i` lives at `base + i × size`. That one formula is why reading `arr[i]` costs `O(1)` for any `i`.")
    yield define("Dynamic array (list)", "an array that grows on demand. It keeps some spare **capacity**; when that runs out it allocates a bigger block, copies everything over and frees the old one. Python lists may also mix element types (`[2, 'p', True]`) because each slot stores a *reference* to an object, not the object itself.")
    yield diagram('''
        list   = [ 10,  20,  30,  40,  50 ]
        index      0    1    2    3    4
        -ve index -5   -4   -3   -2   -1
    ''', "Positive indices count from the front, negative ones (Python only) from the back: l[-1] is the last element")

    yield section("How a dynamic array grows", "arrows-maximize")
    yield p("The list pre-allocates a little extra room. `append` writes into that room in `O(1)`. Only when the room is gone does the list resize:")
    yield steps(
        ("Allocate a bigger block", "Typically a multiple of the current capacity (×2 in most textbooks and in C++ `vector`; CPython uses a gentler ≈1.125× plus a constant, Java `ArrayList` uses 1.5×)."),
        ("Copy", "Move all `n` existing elements into the new block — this is the `O(n)` step."),
        ("Free the old block", "The list now points at the new memory and has spare capacity again."),
    )
    yield diagram('''
        capacity 4 (full)        append(50) → grow to capacity 8, copy 4, write 1
        ┌────┬────┬────┬────┐    ┌────┬────┬────┬────┬────┬────┬────┬────┐
        │ 10 │ 20 │ 30 │ 40 │ →  │ 10 │ 20 │ 30 │ 40 │ 50 │    │    │    │
        └────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┴────┴────┘
                                                        ↑ next 3 appends are O(1)
    ''', "Doubling: after an expensive copy there is room for as many cheap appends as elements copied")
    yield example("Append 1 000 numbers to an empty list that starts with room for 10. Resizes happen at 10, 20, 40, 80, 160, 320, 640 elements — 7 copies totalling about 1 270 element moves, i.e. roughly **one extra move per append**. The occasional `O(n)` copy is spread over the `O(n)` cheap appends that follow it, so each append costs `O(1)` **amortised**.", "Why append is O(1) amortised")
    yield formula("With doubling, inserting `n` elements costs at most `n + (1 + 2 + 4 + … + n) < 3n` element writes → `O(1)` amortised per append")
    yield table(
        ["", "Python", "C++", "Java", "JavaScript"],
        ["Type", "`list`", "`std::vector<T>`", "`ArrayList<T>`", "`Array`"],
        ["Fixed-size cousin", "`array.array`, NumPy", "`T arr[n]`, `std::array`", "`int[] arr`", "typed arrays"],
        ["Mixed element types", "yes (references)", "no", "no (one `T`)", "yes"],
        ["Negative indices", "yes", "no", "no", "`arr.at(-1)` only"],
    )
    yield cards(
        ("Random access", "`arr[i]` is one multiplication and one memory read — `O(1)` for any index.", "bolt"),
        ("Cache friendly", "Elements sit next to each other, so iterating pulls whole cache lines of useful data (locality of reference).", "cpu"),
        ("Slow in the middle", "Inserting or deleting at index `i` shifts every element after it — `O(n)`. Searching an unsorted array is also `O(n)`.", "alert-triangle"),
        cols=3,
    )

    yield section("Operations and their complexities", "list-check")
    yield table(
        ["Operation", "Python", "Time", "Why"],
        ["Read / write by index", "`l[i]`, `l[i] = x`", "O(1)", "address arithmetic"],
        ["Append at end", "`l.append(x)`", "O(1) amortised", "spare capacity; rare copy"],
        ["Pop from end", "`l.pop()`", "O(1)", "nothing to shift"],
        ["Insert at index", "`l.insert(i, x)`", "O(n)", "shifts `n - i` elements right"],
        ["Delete by index / value", "`del l[i]`, `l.pop(i)`, `l.remove(x)`", "O(n)", "shifts elements left (`remove` also searches)"],
        ["Search", "`x in l`, `l.index(x)`, `l.count(x)`", "O(n)", "linear scan"],
        ["Length", "`len(l)`", "O(1)", "stored with the list"],
        ["Min / max / sum", "`min(l)`, `max(l)`, `sum(l)`", "O(n)", "one pass"],
        ["Reverse", "`l.reverse()`, `l[::-1]`", "O(n)", "swap from both ends"],
        ["Sort", "`l.sort()`, `sorted(l)`", "O(n log n)", "Timsort"],
        ["Slice", "`l[a:b]`", "O(b − a)", "copies the slice"],
    )
    yield pitfall("`l.insert(0, x)` and `l.pop(0)` look innocent but shift the whole list every time — a loop of them is `O(n²)`. Use `collections.deque` when you need cheap operations at the front.")

    yield section("Indexing and negative indices", "hash")
    yield p("Python lets you count from the back with negative indices; the other languages need `n - k`. Reading past either end is an `IndexError` in Python, an exception in Java, `undefined` in JavaScript and **undefined behaviour** in C++ (`v.at(i)` checks, `v[i]` does not).")
    yield multi('''
        first: 10
        fourth: 40
        last: 50
        third from end: 30
        length: 5
    ''', py=r'''
        l = [10, 20, 30, 40, 50]
        print("first:", l[0])
        print("fourth:", l[3])
        print("last:", l[-1])             # negative index counts from the end
        print("third from end:", l[-3])
        print("length:", len(l))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int main() {
            vector<int> v = {10, 20, 30, 40, 50};
            int n = v.size();
            cout << "first: " << v[0] << "\n";
            cout << "fourth: " << v[3] << "\n";
            cout << "last: " << v[n - 1] << "\n";            // no negative indices: use n - k
            cout << "third from end: " << v[n - 3] << "\n";
            cout << "length: " << n << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(10, 20, 30, 40, 50));
                int n = l.size();
                System.out.println("first: " + l.get(0));
                System.out.println("fourth: " + l.get(3));
                System.out.println("last: " + l.get(n - 1));            // no negative indices: use n - k
                System.out.println("third from end: " + l.get(n - 3));
                System.out.println("length: " + n);
            }
        }
    ''', js=r'''
        const l = [10, 20, 30, 40, 50];
        const n = l.length;
        console.log("first:", l[0]);
        console.log("fourth:", l[3]);
        console.log("last:", l[n - 1]);              // l.at(-1) also works
        console.log("third from end:", l.at(-3));
        console.log("length:", n);
    ''')

    yield section("Adding and searching", "search")
    yield p("`append` goes to the end; `insert` makes room at an index by shifting. Membership (`in`), `count` and `index` all scan from the left — there is no faster way on an unsorted array.")
    yield multi('''
        10 20 30 40 50 30
        10 60 20 30 40 50 30
        contains 60: true
        count of 30: 2
        first 30 at: 3
        30 at or after index 4: 6
    ''', py=r'''
        l = [10, 20, 30, 40, 50]
        l.append(30)                 # add at the end — amortised O(1)
        print(*l)
        l.insert(1, 60)              # insert at index 1 — O(n): shifts everything after it
        print(*l)
        print("contains 60:", "true" if 60 in l else "false")   # linear search
        print("count of 30:", l.count(30))
        print("first 30 at:", l.index(30))                      # ValueError if absent
        print("30 at or after index 4:", l.index(30, 4))        # search l[4:] only
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        void show(const vector<int>& v) {
            for (int i = 0; i < (int)v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\n";
        }

        int main() {
            vector<int> v = {10, 20, 30, 40, 50};
            v.push_back(30);                              // add at the end — amortised O(1)
            show(v);
            v.insert(v.begin() + 1, 60);                  // insert at index 1 — O(n)
            show(v);
            bool has = find(v.begin(), v.end(), 60) != v.end();
            cout << "contains 60: " << (has ? "true" : "false") << "\n";
            cout << "count of 30: " << count(v.begin(), v.end(), 30) << "\n";
            cout << "first 30 at: " << (find(v.begin(), v.end(), 30) - v.begin()) << "\n";
            cout << "30 at or after index 4: " << (find(v.begin() + 4, v.end(), 30) - v.begin()) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Collections;
        import java.util.List;

        public class Main {
            static String show(List<Integer> l) {
                StringBuilder sb = new StringBuilder();
                for (int x : l) sb.append(x).append(' ');
                return sb.toString().trim();
            }

            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(10, 20, 30, 40, 50));
                l.add(30);                                   // add at the end — amortised O(1)
                System.out.println(show(l));
                l.add(1, 60);                                // insert at index 1 — O(n)
                System.out.println(show(l));
                System.out.println("contains 60: " + l.contains(60));
                System.out.println("count of 30: " + Collections.frequency(l, 30));
                System.out.println("first 30 at: " + l.indexOf(30));      // -1 if absent
                System.out.println("30 at or after index 4: " + (l.subList(4, l.size()).indexOf(30) + 4));
            }
        }
    ''', js=r'''
        const l = [10, 20, 30, 40, 50];
        l.push(30);                                   // add at the end — amortised O(1)
        console.log(l.join(" "));
        l.splice(1, 0, 60);                           // insert at index 1 — O(n)
        console.log(l.join(" "));
        console.log("contains 60:", l.includes(60));
        console.log("count of 30:", l.filter(x => x === 30).length);
        console.log("first 30 at:", l.indexOf(30));           // -1 if absent
        console.log("30 at or after index 4:", l.indexOf(30, 4));
    ''')
    yield note("Python's `index()` raises `ValueError` when the value is missing, while Java's `indexOf` and JavaScript's `indexOf` return `-1`. Check with `in` first, or catch the exception.")

    yield section("Removing elements", "trash")
    yield p("Three ways to remove in Python: `remove(x)` by **value** (first match), `pop(i)` by **index** returning the element, `del l[i]` / `del l[a:b]` by index or slice. Everything except popping from the end is `O(n)`.")
    yield multi('''
        10 20 40 50 60 70
        popped: 70
        10 20 40 50 60
        popped at 2: 40
        10 20 50 60
        10 50 60
        60
    ''', py=r'''
        l = [10, 20, 30, 40, 50, 60, 70]
        l.remove(30)                       # first 30, by value — O(n); ValueError if absent
        print(*l)
        print("popped:", l.pop())          # remove and return the last — O(1)
        print(*l)
        print("popped at 2:", l.pop(2))    # by index — O(n)
        print(*l)
        del l[1]                           # delete by index
        print(*l)
        del l[0:2]                         # delete a slice
        print(*l)
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        void show(const vector<int>& v) {
            for (int i = 0; i < (int)v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\n";
        }

        int main() {
            vector<int> v = {10, 20, 30, 40, 50, 60, 70};
            v.erase(find(v.begin(), v.end(), 30));        // first 30, by value — O(n)
            show(v);
            int last = v.back(); v.pop_back();            // pop_back() returns nothing
            cout << "popped: " << last << "\n";
            show(v);
            int at2 = v[2]; v.erase(v.begin() + 2);       // by index — O(n)
            cout << "popped at 2: " << at2 << "\n";
            show(v);
            v.erase(v.begin() + 1);                       // delete by index
            show(v);
            v.erase(v.begin(), v.begin() + 2);            // delete the range [0, 2)
            show(v);
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static String show(List<Integer> l) {
                StringBuilder sb = new StringBuilder();
                for (int x : l) sb.append(x).append(' ');
                return sb.toString().trim();
            }

            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(10, 20, 30, 40, 50, 60, 70));
                l.remove(Integer.valueOf(30));               // by value — remove(int) would mean "by index"!
                System.out.println(show(l));
                System.out.println("popped: " + l.remove(l.size() - 1));   // remove the last
                System.out.println(show(l));
                System.out.println("popped at 2: " + l.remove(2));         // by index — O(n)
                System.out.println(show(l));
                l.remove(1);
                System.out.println(show(l));
                l.subList(0, 2).clear();                     // delete the range [0, 2)
                System.out.println(show(l));
            }
        }
    ''', js=r'''
        const l = [10, 20, 30, 40, 50, 60, 70];
        l.splice(l.indexOf(30), 1);                   // first 30, by value — O(n)
        console.log(l.join(" "));
        console.log("popped:", l.pop());              // remove and return the last — O(1)
        console.log(l.join(" "));
        console.log("popped at 2:", l.splice(2, 1)[0]);   // by index — O(n)
        console.log(l.join(" "));
        l.splice(1, 1);                               // delete by index
        console.log(l.join(" "));
        l.splice(0, 2);                               // delete 2 elements from index 0
        console.log(l.join(" "));
    ''')
    yield pitfall("Never remove from a list while iterating over it with `for x in l` — elements shift under the loop and some get skipped. Build a new list (`[x for x in l if keep(x)]`) or iterate over a copy.")

    yield section("min, max, sum, reverse and sort", "arrows-sort")
    yield multi('''
        min: 10
        max: 50
        sum: 150
        reversed: 30 20 50 10 40
        sorted: 10 20 30 40 50
        sorted descending: 50 40 30 20 10
    ''', py=r'''
        l = [40, 10, 50, 20, 30]
        print("min:", min(l))
        print("max:", max(l))
        print("sum:", sum(l))
        l.reverse()                        # in place; reversed(l) gives an iterator instead
        print("reversed:", *l)
        l.sort()                           # in place, O(n log n); sorted(l) returns a new list
        print("sorted:", *l)
        l.sort(reverse=True)
        print("sorted descending:", *l)
    ''', cpp=r'''
        #include <algorithm>
        #include <functional>
        #include <iostream>
        #include <numeric>
        #include <string>
        #include <vector>
        using namespace std;

        void show(const string& label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\n";
        }

        int main() {
            vector<int> v = {40, 10, 50, 20, 30};
            cout << "min: " << *min_element(v.begin(), v.end()) << "\n";
            cout << "max: " << *max_element(v.begin(), v.end()) << "\n";
            cout << "sum: " << accumulate(v.begin(), v.end(), 0) << "\n";
            reverse(v.begin(), v.end());
            show("reversed:", v);
            sort(v.begin(), v.end());                    // O(n log n)
            show("sorted:", v);
            sort(v.begin(), v.end(), greater<int>());
            show("sorted descending:", v);
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Collections;
        import java.util.List;

        public class Main {
            static String show(List<Integer> l) {
                StringBuilder sb = new StringBuilder();
                for (int x : l) sb.append(' ').append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                List<Integer> l = new ArrayList<>(List.of(40, 10, 50, 20, 30));
                System.out.println("min: " + Collections.min(l));
                System.out.println("max: " + Collections.max(l));
                int sum = 0;
                for (int x : l) sum += x;
                System.out.println("sum: " + sum);
                Collections.reverse(l);
                System.out.println("reversed:" + show(l));
                Collections.sort(l);                         // O(n log n)
                System.out.println("sorted:" + show(l));
                l.sort(Collections.reverseOrder());
                System.out.println("sorted descending:" + show(l));
            }
        }
    ''', js=r'''
        const l = [40, 10, 50, 20, 30];
        console.log("min:", Math.min(...l));
        console.log("max:", Math.max(...l));
        console.log("sum:", l.reduce((a, b) => a + b, 0));
        l.reverse();                                  // in place
        console.log("reversed:", l.join(" "));
        l.sort((a, b) => a - b);                      // ALWAYS pass a comparator for numbers
        console.log("sorted:", l.join(" "));
        l.sort((a, b) => b - a);
        console.log("sorted descending:", l.join(" "));
    ''')
    yield p("Two language-specific traps worth seeing once:")
    yield snippet("py", r'''
        l = [10, 'twenty', 30]        # a list may mix types …
        print(sum(l))                 # … but sum(), sort(), min() need comparable/addable elements
    ''', fails=True)
    yield output("TypeError: unsupported operand type(s) for +: 'int' and 'str'")
    yield snippet("js", r'''
        console.log([10, 9, 1].sort().join(" "));             // compares as strings: "10" < "9"
        console.log([10, 9, 1].sort((a, b) => a - b).join(" "));
    ''', out='''
        1 10 9
        1 9 10
    ''')

    yield section("Slicing", "scissors")
    yield p("`l[start:stop:step]` returns a **new list** with the elements from `start` up to but not including `stop`, every `step`-th one. Every part is optional; negative indices and a negative step work too. Slicing also works on tuples and strings.")
    yield table(
        ["Slice", "Meaning", "Result for `[10, 20, 11, 40, 15, 19]`"],
        ["`l[0:5]`", "indices 0..4", "`[10, 20, 11, 40, 15]`"],
        ["`l[0:5:2]`", "indices 0, 2, 4", "`[10, 11, 15]`"],
        ["`l[:]`", "a shallow copy of everything", "`[10, 20, 11, 40, 15, 19]`"],
        ["`l[3:]`", "from index 3 to the end", "`[40, 15, 19]`"],
        ["`l[:3]`", "the first three", "`[10, 20, 11]`"],
        ["`l[-2:]`", "the last two", "`[15, 19]`"],
        ["`l[::-1]`", "reversed copy", "`[19, 15, 40, 11, 20, 10]`"],
    )
    yield code(r'''
        l = [10, 20, 11, 40, 15, 19]
        print(l[0:5])      # [10, 20, 11, 40, 15]
        print(l[0:5:2])    # [10, 11, 15]
        print(l[:])        # [10, 20, 11, 40, 15, 19]
        print(l[3:])       # [40, 15, 19]
        print(l[:3])       # [10, 20, 11]
        print(l[-2:])      # [15, 19]
        print(l[::-1])     # [19, 15, 40, 11, 20, 10]
        print(l[10:])      # []  ← out-of-range slices are clipped, never an error
    ''')
    yield p("A slice is a copy: equal in value (`==`) but a different object (`is`). Note that `l in dup` asks whether the *whole list* `l` is one of `dup`'s elements — not whether the elements overlap.")
    yield code(r'''
        l = [10, 20, 11, 40, 15, 19]
        dup = l[:]                 # same as l.copy() or list(l)
        print(dup == l)            # True  ← same contents
        print(dup is l)            # False ← different objects in memory
        dup[0] = 99
        print(l[0])                # 10    ← changing the copy leaves l alone
        print(l in dup)            # False ← is the list l an *element* of dup? no

        t1 = (10, 20, 30)          # tuples slice exactly the same way …
        print(t1[1:])              # (20, 30)
        print(t1 == (10, 20, 30))  # True
        print(10 in t1)            # True
    ''')
    yield note("`t1 is t2` for two equal tuple literals is an implementation detail (CPython may or may not reuse the constant), so never rely on `is` for value comparison — use `==`.")
    yield table(
        ["Idiom", "Python", "C++", "Java", "JavaScript"],
        ["Sub-range copy", "`l[a:b]`", "`vector<int>(v.begin()+a, v.begin()+b)`", "`new ArrayList<>(l.subList(a, b))`", "`arr.slice(a, b)`"],
        ["Copy", "`l[:]`, `l.copy()`", "`vector<int> c = v;`", "`new ArrayList<>(l)`", "`[...arr]`, `arr.slice()`"],
        ["Last k", "`l[-k:]`", "`vector<int>(v.end()-k, v.end())`", "`l.subList(n-k, n)`", "`arr.slice(-k)`"],
    )
    yield pitfall("Java's `subList(a, b)` is a **view** of the original list, not a copy — changes to one show in the other. Wrap it in `new ArrayList<>(…)` when you need an independent copy.")

    yield section("Comprehensions", "code")
    yield p("A comprehension builds a new collection from any *iterable* (a list, a `range`, a string, a file …) in one expression: `[expression for item in iterable if condition]`. It is the Pythonic replacement for the “make an empty list, loop, append” pattern — same `O(n)` time, less code.")
    yield code(r'''
        l = [x for x in range(11)]
        print(l)                                     # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        print([i for i in range(11) if i % 2 == 0])  # [0, 2, 4, 6, 8, 10]
        print([x for x in range(11) if x % 2 == 1])  # [1, 3, 5, 7, 9]
        print([x * x for x in range(11)])            # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

        s = "ThrishankKuntimaddi"
        print([ch for ch in s if ch in 'aeiou'])     # ['i', 'a', 'u', 'i', 'a', 'i']

        names = ['Thrishank', 'Kuntimaddi', 'ThrishankKuntimaddi', 'Nani']
        print([n for n in names if n.startswith("T")])          # ['Thrishank', 'ThrishankKuntimaddi']
        print([n.lower() for n in names if n.startswith("T")])  # ['thrishank', 'thrishankkuntimaddi']
    ''')
    yield p("The two list problems below, written as comprehensions:")
    yield code(r'''
        l = [10, 20, 11, 40, 15, 19]

        def get_smaller(l, x):
            return [e for e in l if e < x]

        def get_even_odd(l):
            even = [i for i in l if i % 2 == 0]
            odd = [i for i in l if i % 2 == 1]
            return even, odd

        print(get_smaller(l, 21))     # [10, 20, 11, 15, 19]
        even, odd = get_even_odd(l)
        print(even)                   # [10, 20, 40]
        print(odd)                    # [11, 15, 19]
    ''')
    yield p("Curly braces give a **set** or **dict** comprehension; `zip` pairs two lists up so `dict(zip(keys, values))` builds a mapping.")
    yield code(r'''
        print({x for x in range(11)})          # {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}  ← set: no duplicates, no order guarantee
        print({x: x * 2 for x in range(6)})    # {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10}

        l1 = [10, 20, 30]
        l2 = ['a', 'b', 'c']
        print(dict(zip(l1, l2)))               # {10: 'a', 20: 'b', 30: 'c'}
    ''')
    yield p("The same *filter → map* idea exists everywhere; only Python has the dedicated syntax. Squares of the even numbers in `0..10`:")
    yield multi('''
        0 4 16 36 64 100
    ''', py=r'''
        squares = [x * x for x in range(11) if x % 2 == 0]
        print(*squares)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int main() {
            vector<int> squares;
            for (int x = 0; x <= 10; x++)          // no comprehension: a plain loop
                if (x % 2 == 0) squares.push_back(x * x);
            for (int i = 0; i < (int)squares.size(); i++) cout << (i ? " " : "") << squares[i];
            cout << "\n";
        }
    ''', java=r'''
        import java.util.stream.Collectors;
        import java.util.stream.IntStream;

        public class Main {
            public static void main(String[] args) {
                String squares = IntStream.rangeClosed(0, 10)
                        .filter(x -> x % 2 == 0)
                        .map(x -> x * x)
                        .mapToObj(String::valueOf)
                        .collect(Collectors.joining(" "));
                System.out.println(squares);
            }
        }
    ''', js=r'''
        const squares = Array.from({ length: 11 }, (_, i) => i)
            .filter(x => x % 2 === 0)
            .map(x => x * x);
        console.log(squares.join(" "));
    ''')

    yield section("Problem: average (mean) of a list", "math-function")
    yield io("l = [10, 20, 30, 40]", "25.0", "l = [3, 4, 4]", "3.7")
    yield idea("Add everything up in one pass and divide by the count. The only things that go wrong are **integer division** (in C++ and Java `100 / 4` is `25` but `11 / 3` is `3`) and an **empty list** (division by zero) — guard both.")
    yield multi('''
        25.0
        3.7
    ''', py=r'''
        def average(l):
            total = 0
            for x in l:
                total += x
            return total / len(l)         # / is true division: 100 / 4 → 25.0 (sum(l) / len(l) is the idiom)

        for l in ([10, 20, 30, 40], [3, 4, 4]):
            print(f"{average(l):.1f}")
    ''', cpp=r'''
        #include <iomanip>
        #include <iostream>
        #include <vector>
        using namespace std;

        double average(const vector<int>& v) {
            long long total = 0;
            for (int x : v) total += x;
            return (double)total / v.size();      // cast first — integer division would give 25 and 3
        }

        int main() {
            cout << fixed << setprecision(1);
            cout << average({10, 20, 30, 40}) << "\n";
            cout << average({3, 4, 4}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static double average(int[] a) {
                long total = 0;
                for (int x : a) total += x;
                return (double) total / a.length;     // cast first — integer division would give 25 and 3
            }

            public static void main(String[] args) {
                System.out.println(String.format("%.1f", average(new int[]{10, 20, 30, 40})));
                System.out.println(String.format("%.1f", average(new int[]{3, 4, 4})));
            }
        }
    ''', js=r'''
        function average(arr) {
            let total = 0;
            for (const x of arr) total += x;
            return total / arr.length;            // JS numbers are doubles: 100 / 4 = 25, 11 / 3 = 3.666…
        }

        for (const arr of [[10, 20, 30, 40], [3, 4, 4]])
            console.log(average(arr).toFixed(1));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Summing many large `int`s overflows in C++/Java — accumulate into a `long long` / `long`. Python integers never overflow, and never shadow the built-in `sum` with a variable called `sum`.")

    yield section("Problem: separate even and odd numbers", "arrows-split-2")
    yield io("l = [10, 20, 11, 40, 15, 19]", "even: 10 20 40 / odd: 11 15 19")
    yield idea("One pass, one test per element: `x % 2 == 0` sends it to the even list, everything else to the odd list. Order within each group is preserved.")
    yield multi('''
        even: 10 20 40
        odd: 11 15 19
    ''', py=r'''
        def get_even_odd(l):
            even, odd = [], []
            for x in l:
                if x % 2 == 0:
                    even.append(x)
                else:
                    odd.append(x)
            return even, odd

        even, odd = get_even_odd([10, 20, 11, 40, 15, 19])
        print("even:", *even)
        print("odd:", *odd)
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        void show(const string& label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\n";
        }

        int main() {
            vector<int> l = {10, 20, 11, 40, 15, 19};
            vector<int> even, odd;
            for (int x : l) {
                if (x % 2 == 0) even.push_back(x);
                else odd.push_back(x);
            }
            show("even:", even);
            show("odd:", odd);
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static String show(List<Integer> l) {
                StringBuilder sb = new StringBuilder();
                for (int x : l) sb.append(' ').append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                int[] l = {10, 20, 11, 40, 15, 19};
                List<Integer> even = new ArrayList<>(), odd = new ArrayList<>();
                for (int x : l) {
                    if (x % 2 == 0) even.add(x);
                    else odd.add(x);
                }
                System.out.println("even:" + show(even));
                System.out.println("odd:" + show(odd));
            }
        }
    ''', js=r'''
        function getEvenOdd(arr) {
            const even = [], odd = [];
            for (const x of arr) {
                if (x % 2 === 0) even.push(x);
                else odd.push(x);
            }
            return [even, odd];
        }

        const [even, odd] = getEvenOdd([10, 20, 11, 40, 15, 19]);
        console.log("even:", even.join(" "));
        console.log("odd:", odd.join(" "));
    ''')
    yield complexity("O(n)", "O(n)")
    yield note("For negative numbers `x % 2` is `-1` in C++, Java and JavaScript but `1` in Python. Testing `x % 2 == 0` (rather than `== 1`) is correct in every language.")

    yield section("Problem: elements smaller than x", "filter")
    yield io("l = [10, 20, 11, 40, 15, 19], x = 21", "10 20 11 15 19")
    yield idea("A filter: keep each element that passes the test `e < x`. This is the shape of every “select the elements that …” problem — a single scan with a condition.")
    yield multi('''
        smaller than 21: 10 20 11 15 19
    ''', py=r'''
        def get_smaller(l, x):
            res = []
            for e in l:
                if e < x:
                    res.append(e)
            return res                       # or simply: [e for e in l if e < x]

        print("smaller than 21:", *get_smaller([10, 20, 11, 40, 15, 19], 21))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> getSmaller(const vector<int>& l, int x) {
            vector<int> res;
            for (int e : l)
                if (e < x) res.push_back(e);
            return res;
        }

        int main() {
            vector<int> res = getSmaller({10, 20, 11, 40, 15, 19}, 21);
            cout << "smaller than 21:";
            for (int e : res) cout << " " << e;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> getSmaller(int[] l, int x) {
                List<Integer> res = new ArrayList<>();
                for (int e : l)
                    if (e < x) res.add(e);
                return res;
            }

            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder("smaller than 21:");
                for (int e : getSmaller(new int[]{10, 20, 11, 40, 15, 19}, 21)) sb.append(' ').append(e);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function getSmaller(arr, x) {
            const res = [];
            for (const e of arr)
                if (e < x) res.push(e);
            return res;                      // or simply: arr.filter(e => e < x)
        }

        console.log("smaller than 21:", getSmaller([10, 20, 11, 40, 15, 19], 21).join(" "));
    ''')
    yield complexity("O(n)", "O(n)")

    yield section("Problem: largest element", "arrow-big-up")
    yield io("l = [10, 5, 20, 8]", "20", "l = []", "None")
    yield p("The naive approach checks, for every `x`, whether *no* element is bigger than it. Python's `for … else` runs the `else` only when the inner loop never hit `break` — handy, but the method is `O(n²)`:")
    yield snippet("py", r'''
        def get_max_naive(l):
            for x in l:
                for y in l:
                    if y > x:
                        break          # x is not the largest
                else:
                    return x           # the inner loop never broke → nothing is bigger
            return None

        print(get_max_naive([10, 5, 20, 8]))
    ''', out="20")
    yield idea("Keep a running maximum: start with the first element and replace it whenever you see something bigger. One pass, `O(n)`. Return `None` for an empty list instead of crashing on `l[0]`.")
    yield multi('''
        largest: 20
        largest: None
    ''', py=r'''
        def get_max(l):
            if not l:
                return None
            res = l[0]
            for i in range(1, len(l)):
                if l[i] > res:
                    res = l[i]
            return res                      # built-in: max(l) — but it also raises on an empty list

        print("largest:", get_max([10, 5, 20, 8]))
        print("largest:", get_max([]))
    ''', cpp=r'''
        #include <iostream>
        #include <optional>
        #include <vector>
        using namespace std;

        optional<int> getMax(const vector<int>& l) {
            if (l.empty()) return nullopt;
            int res = l[0];
            for (int i = 1; i < (int)l.size(); i++)
                if (l[i] > res) res = l[i];
            return res;                     // library: *max_element(l.begin(), l.end())
        }

        void show(optional<int> r) {
            if (r) cout << "largest: " << *r << "\n";
            else cout << "largest: None\n";
        }

        int main() {
            show(getMax({10, 5, 20, 8}));
            show(getMax({}));
        }
    ''', java=r'''
        public class Main {
            static Integer getMax(int[] l) {
                if (l.length == 0) return null;
                int res = l[0];
                for (int i = 1; i < l.length; i++)
                    if (l[i] > res) res = l[i];
                return res;
            }

            static void show(Integer r) {
                System.out.println("largest: " + (r == null ? "None" : r.toString()));
            }

            public static void main(String[] args) {
                show(getMax(new int[]{10, 5, 20, 8}));
                show(getMax(new int[]{}));
            }
        }
    ''', js=r'''
        function getMax(arr) {
            if (arr.length === 0) return null;
            let res = arr[0];
            for (let i = 1; i < arr.length; i++)
                if (arr[i] > res) res = arr[i];
            return res;                     // Math.max(...arr) works too, but gives -Infinity for []
        }

        const show = r => console.log("largest:", r === null ? "None" : r);
        show(getMax([10, 5, 20, 8]));
        show(getMax([]));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Initialising `res = 0` instead of `res = l[0]` returns the wrong answer for an all-negative list such as `[-3, -7]`.")

    yield section("Problem: second largest element", "arrow-big-up-lines")
    yield io("l = [10, 20, 4, 5, 6, 1]", "10", "l = [10, 10, 10]", "None")
    yield p("Two-pass version: find the largest, then the largest among elements *not equal* to it. Correct and `O(n)`, but it reads the list twice:")
    yield snippet("py", r'''
        def second_largest_two_pass(l):
            if len(l) <= 1:
                return None
            largest = max(l)
            second = None
            for x in l:
                if x != largest:                       # skip every copy of the maximum
                    if second is None or x > second:
                        second = x
            return second

        print(second_largest_two_pass([10, 20, 4, 5, 6, 1]))
        print(second_largest_two_pass([10, 10, 10]))
    ''', out='''
        10
        None
    ''')
    yield idea("Single pass with two trackers. When `x` beats the largest, the old largest *becomes* the second largest. When `x` is between them (and not equal to the largest), it becomes the new second. Duplicates of the maximum are ignored, so `[10, 10, 10]` has no second largest.")
    yield multi('''
        second largest: 10
        second largest: None
        second largest: 20
    ''', py=r'''
        def second_largest(l):
            if len(l) <= 1:
                return None
            largest, second = l[0], None
            for x in l[1:]:
                if x > largest:
                    second, largest = largest, x          # old largest drops to second place
                elif x != largest:
                    if second is None or x > second:
                        second = x
            return second

        for l in ([10, 20, 4, 5, 6, 1], [10, 10, 10], [20, 30, 20, 30]):
            print("second largest:", second_largest(l))
    ''', cpp=r'''
        #include <iostream>
        #include <optional>
        #include <vector>
        using namespace std;

        optional<int> secondLargest(const vector<int>& l) {
            if (l.size() <= 1) return nullopt;
            int largest = l[0];
            optional<int> second;
            for (int i = 1; i < (int)l.size(); i++) {
                int x = l[i];
                if (x > largest) {
                    second = largest;                      // old largest drops to second place
                    largest = x;
                } else if (x != largest) {
                    if (!second || x > *second) second = x;
                }
            }
            return second;
        }

        int main() {
            for (vector<int> l : {vector<int>{10, 20, 4, 5, 6, 1}, {10, 10, 10}, {20, 30, 20, 30}}) {
                optional<int> r = secondLargest(l);
                if (r) cout << "second largest: " << *r << "\n";
                else cout << "second largest: None\n";
            }
        }
    ''', java=r'''
        public class Main {
            static Integer secondLargest(int[] l) {
                if (l.length <= 1) return null;
                int largest = l[0];
                Integer second = null;
                for (int i = 1; i < l.length; i++) {
                    int x = l[i];
                    if (x > largest) {
                        second = largest;                  // old largest drops to second place
                        largest = x;
                    } else if (x != largest) {
                        if (second == null || x > second) second = x;
                    }
                }
                return second;
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 20, 4, 5, 6, 1}, {10, 10, 10}, {20, 30, 20, 30}};
                for (int[] l : tests) {
                    Integer r = secondLargest(l);
                    System.out.println("second largest: " + (r == null ? "None" : r.toString()));
                }
            }
        }
    ''', js=r'''
        function secondLargest(arr) {
            if (arr.length <= 1) return null;
            let largest = arr[0], second = null;
            for (let i = 1; i < arr.length; i++) {
                const x = arr[i];
                if (x > largest) {
                    second = largest;                      // old largest drops to second place
                    largest = x;
                } else if (x !== largest) {
                    if (second === null || x > second) second = x;
                }
            }
            return second;
        }

        for (const arr of [[10, 20, 4, 5, 6, 1], [10, 10, 10], [20, 30, 20, 30]])
            console.log("second largest:", secondLargest(arr) === null ? "None" : secondLargest(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("`sorted(l)[-2]` is `O(n log n)` and wrong for `[10, 10, 5]` (gives `10`). The one-pass version is the expected interview answer; mention explicitly how you treat duplicates.")

    yield section("Problem: check if a list is sorted", "sort-ascending")
    yield io("l = [10, 20, 30]", "Yes", "l = [29, 24, 32]", "No")
    yield p("Naive: sort a copy and compare — `O(n log n)` time and `O(n)` extra space just to answer a yes/no question:")
    yield snippet("py", r'''
        def is_sorted_naive(l):
            return sorted(l) == l

        print("Yes" if is_sorted_naive([10, 20, 30]) else "No")
        print("Yes" if is_sorted_naive([29, 24, 32]) else "No")
    ''', out='''
        Yes
        No
    ''')
    yield idea("A list is sorted (non-decreasing) exactly when **no adjacent pair is out of order**. Scan once and return `No` the moment `l[i] < l[i-1]`. Equal neighbours are fine, and an empty or one-element list is trivially sorted.")
    yield multi('''
        10 20 30: Yes
        29 24 32: No
        7 7 7: Yes
        : Yes
    ''', py=r'''
        def is_sorted(l):
            for i in range(1, len(l)):
                if l[i] < l[i - 1]:          # one inversion is enough to say No
                    return False
            return True

        for l in ([10, 20, 30], [29, 24, 32], [7, 7, 7], []):
            print(" ".join(map(str, l)) + ":", "Yes" if is_sorted(l) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool isSorted(const vector<int>& l) {
            for (int i = 1; i < (int)l.size(); i++)
                if (l[i] < l[i - 1]) return false;   // one inversion is enough to say No
            return true;                             // library: is_sorted(l.begin(), l.end())
        }

        int main() {
            for (vector<int> l : {vector<int>{10, 20, 30}, {29, 24, 32}, {7, 7, 7}, {}}) {
                for (int i = 0; i < (int)l.size(); i++) cout << (i ? " " : "") << l[i];
                cout << ": " << (isSorted(l) ? "Yes" : "No") << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static boolean isSorted(int[] l) {
                for (int i = 1; i < l.length; i++)
                    if (l[i] < l[i - 1]) return false;   // one inversion is enough to say No
                return true;
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 20, 30}, {29, 24, 32}, {7, 7, 7}, {}};
                for (int[] l : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < l.length; i++) sb.append(i > 0 ? " " : "").append(l[i]);
                    System.out.println(sb + ": " + (isSorted(l) ? "Yes" : "No"));
                }
            }
        }
    ''', js=r'''
        function isSorted(arr) {
            for (let i = 1; i < arr.length; i++)
                if (arr[i] < arr[i - 1]) return false;   // one inversion is enough to say No
            return true;
        }

        for (const arr of [[10, 20, 30], [29, 24, 32], [7, 7, 7], []])
            console.log(arr.join(" ") + ":", isSorted(arr) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Best case `O(1)` (the first pair is already out of order), worst case `O(n)`. Ask the interviewer whether “sorted” means strictly increasing — then the test becomes `l[i] <= l[i-1]`.")

    yield section("Problem: reverse a list", "arrows-left-right")
    yield io("l = [10, 20, 30, 40]", "40 30 20 10")
    yield p("Python has four ready-made ways; `reverse()` works in place, the other three produce a new list:")
    yield code(r'''
        l = [10, 20, 30]
        l.reverse()                   # Method 1: in place
        print(l)                      # [30, 20, 10]

        l = [10, 20, 30]
        print(l[::-1])                # [30, 20, 10]  ← Method 2: reversed copy via slicing
        print(list(reversed(l)))      # [30, 20, 10]  ← Method 3: reversed() iterator → list

        res = []                      # Method 4: walk from the back
        for i in range(len(l) - 1, -1, -1):
            res.append(l[i])
        print(res)                    # [30, 20, 10]
    ''')
    yield idea("The hand-written version worth remembering swaps the two ends and walks inward: `l[s] ↔ l[e]`, `s += 1`, `e -= 1`, until the pointers meet. Only `n / 2` swaps and **no extra list** — that is the “two-pointer” pattern used all over DSA.")
    yield diagram('''
        s                 e          s         e            s   e
        ↓                 ↓          ↓         ↓            ↓   ↓
        10  20  30  40  50    →  50  20  30  40  10   →  50  40  30  20  10
        swap l[0], l[4]              swap l[1], l[3]        s ≥ e → stop
    ''', "Two pointers meet in the middle after ⌊n/2⌋ swaps")
    yield multi('''
        reversed: 50 40 30 20 10
    ''', py=r'''
        def reverse(l):
            s, e = 0, len(l) - 1
            while s < e:
                l[s], l[e] = l[e], l[s]      # swap the ends
                s += 1
                e -= 1

        l = [10, 20, 30, 40, 50]
        reverse(l)
        print("reversed:", *l)
    ''', cpp=r'''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        void reverseList(vector<int>& l) {
            int s = 0, e = l.size() - 1;
            while (s < e) {
                swap(l[s], l[e]);               // swap the ends
                s++;
                e--;
            }                                   // library: reverse(l.begin(), l.end())
        }

        int main() {
            vector<int> l = {10, 20, 30, 40, 50};
            reverseList(l);
            cout << "reversed:";
            for (int x : l) cout << " " << x;
            cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static void reverse(int[] l) {
                int s = 0, e = l.length - 1;
                while (s < e) {
                    int tmp = l[s]; l[s] = l[e]; l[e] = tmp;   // swap the ends
                    s++;
                    e--;
                }
            }

            public static void main(String[] args) {
                int[] l = {10, 20, 30, 40, 50};
                reverse(l);
                StringBuilder sb = new StringBuilder("reversed:");
                for (int x : l) sb.append(' ').append(x);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function reverse(arr) {
            let s = 0, e = arr.length - 1;
            while (s < e) {
                [arr[s], arr[e]] = [arr[e], arr[s]];   // swap the ends
                s++;
                e--;
            }                                          // library: arr.reverse()
        }

        const l = [10, 20, 30, 40, 50];
        reverse(l);
        console.log("reversed:", l.join(" "));
    ''')
    yield complexity("O(n)", "O(1)")
    yield table(
        ["", "Python", "C++", "Java", "JavaScript"],
        ["In place", "`l.reverse()`", "`reverse(v.begin(), v.end())`", "`Collections.reverse(list)`", "`arr.reverse()`"],
        ["New reversed copy", "`l[::-1]`, `list(reversed(l))`", "`vector<int>(v.rbegin(), v.rend())`", "copy, then reverse", "`arr.toReversed()`, `[...arr].reverse()`"],
    )

    yield section("Problem: remove duplicates from a sorted array", "copy-off")
    yield io("arr = [10, 20, 20, 30, 30, 30, 30]", "10 20 30, size = 3")
    yield p("Because the array is **sorted**, all copies of a value sit next to each other, so a duplicate is simply an element equal to the one just before it. The naive version writes the distinct values into a second array — correct, but `O(n)` extra space:")
    yield snippet("py", r'''
        def remove_duplicates_naive(arr):
            temp = [arr[0]]
            for i in range(1, len(arr)):
                if arr[i] != temp[-1]:          # differs from the last kept value → new distinct value
                    temp.append(arr[i])
            return temp

        res = remove_duplicates_naive([10, 20, 20, 30, 30, 30, 30])
        print(*res)
        print("size:", len(res))
    ''', out='''
        10 20 30
        size: 3
    ''')
    yield idea("Do it **in place** with two pointers: `res` marks where the next distinct value should be written, `i` scans. Whenever `arr[i]` differs from the last written value `arr[res-1]`, copy it to `arr[res]` and advance `res`. The first `res` slots hold the answer; what remains after them is garbage.")
    yield diagram('''
        arr = 10  20  20  30  30  30  30        read i, compare with arr[res-1]
                  ↑res=1
        i=1: 20 ≠ 10 → arr[1]=20, res=2
        i=2: 20 = 20 → skip
        i=3: 30 ≠ 20 → arr[2]=30, res=3
        i=4..6: 30 = 30 → skip
        arr = 10  20  30 | 30  30  30  30       answer = first res = 3 slots
    ''', "Trace of the in-place version")
    yield multi('''
        10 20 30
        size: 3
    ''', py=r'''
        def remove_duplicates(arr):
            if not arr:
                return 0
            res = 1                              # arr[0] is always kept
            for i in range(1, len(arr)):
                if arr[i] != arr[res - 1]:
                    arr[res] = arr[i]            # write the next distinct value
                    res += 1
            return res

        arr = [10, 20, 20, 30, 30, 30, 30]
        n = remove_duplicates(arr)
        print(*arr[:n])
        print("size:", n)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int removeDuplicates(vector<int>& arr) {
            if (arr.empty()) return 0;
            int res = 1;                             // arr[0] is always kept
            for (int i = 1; i < (int)arr.size(); i++) {
                if (arr[i] != arr[res - 1])
                    arr[res++] = arr[i];             // write the next distinct value
            }
            return res;                              // library: unique(arr.begin(), arr.end()) - arr.begin()
        }

        int main() {
            vector<int> arr = {10, 20, 20, 30, 30, 30, 30};
            int n = removeDuplicates(arr);
            for (int i = 0; i < n; i++) cout << (i ? " " : "") << arr[i];
            cout << "\n";
            cout << "size: " << n << "\n";
        }
    ''', java=r'''
        public class Main {
            static int removeDuplicates(int[] arr) {
                if (arr.length == 0) return 0;
                int res = 1;                             // arr[0] is always kept
                for (int i = 1; i < arr.length; i++) {
                    if (arr[i] != arr[res - 1])
                        arr[res++] = arr[i];             // write the next distinct value
                }
                return res;
            }

            public static void main(String[] args) {
                int[] arr = {10, 20, 20, 30, 30, 30, 30};
                int n = removeDuplicates(arr);
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < n; i++) sb.append(i > 0 ? " " : "").append(arr[i]);
                System.out.println(sb);
                System.out.println("size: " + n);
            }
        }
    ''', js=r'''
        function removeDuplicates(arr) {
            if (arr.length === 0) return 0;
            let res = 1;                                 // arr[0] is always kept
            for (let i = 1; i < arr.length; i++) {
                if (arr[i] !== arr[res - 1])
                    arr[res++] = arr[i];                 // write the next distinct value
            }
            return res;
        }

        const arr = [10, 20, 20, 30, 30, 30, 30];
        const n = removeDuplicates(arr);
        console.log(arr.slice(0, n).join(" "));
        console.log("size:", n);
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("The two-pointer trick **requires sorted input**. On an unsorted array (`[10, 20, 20, 30, 40, 30, 30]`) you must either sort first (`O(n log n)`) or use a set (`O(n)` extra space) — equal values are no longer adjacent. The original notes sorted inside the function; do that only when the problem does not promise sorted input.")

    yield section("Problem: left rotate by one", "rotate-2")
    yield io("l = [10, 20, 30, 40]", "20 30 40 10")
    yield p("A left (counter-clockwise) rotation moves the first element to the end and every other element one step to the left. Python can do it with slicing or `pop`/`append`:")
    yield code(r'''
        l = [10, 20, 30, 40]
        print(l[1:] + l[0:1])         # [20, 30, 40, 10]  ← Method 1: new list from two slices

        l = [10, 20, 30, 40]
        l.append(l.pop(0))            # Method 2: pop the front (O(n) shift), push it at the back
        print(l)                      # [20, 30, 40, 10]
    ''')
    yield idea("By hand: save `l[0]`, shift every element one place left (`l[i-1] = l[i]`), then put the saved value in the last slot. One pass, no extra array.")
    yield multi('''
        rotated: 20 30 40 50 10
    ''', py=r'''
        def rotate_by_one(l):
            n = len(l)
            if n == 0:
                return
            first = l[0]                     # save the element that falls off the front
            for i in range(1, n):
                l[i - 1] = l[i]              # shift left
            l[n - 1] = first                 # it re-enters at the back

        l = [10, 20, 30, 40, 50]
        rotate_by_one(l)
        print("rotated:", *l)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void rotateByOne(vector<int>& l) {
            int n = l.size();
            if (n == 0) return;
            int first = l[0];                    // save the element that falls off the front
            for (int i = 1; i < n; i++) l[i - 1] = l[i];   // shift left
            l[n - 1] = first;                    // it re-enters at the back
        }                                        // library: rotate(l.begin(), l.begin() + 1, l.end())

        int main() {
            vector<int> l = {10, 20, 30, 40, 50};
            rotateByOne(l);
            cout << "rotated:";
            for (int x : l) cout << " " << x;
            cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static void rotateByOne(int[] l) {
                int n = l.length;
                if (n == 0) return;
                int first = l[0];                    // save the element that falls off the front
                for (int i = 1; i < n; i++) l[i - 1] = l[i];   // shift left
                l[n - 1] = first;                    // it re-enters at the back
            }

            public static void main(String[] args) {
                int[] l = {10, 20, 30, 40, 50};
                rotateByOne(l);
                StringBuilder sb = new StringBuilder("rotated:");
                for (int x : l) sb.append(' ').append(x);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function rotateByOne(arr) {
            const n = arr.length;
            if (n === 0) return;
            const first = arr[0];                    // save the element that falls off the front
            for (let i = 1; i < n; i++) arr[i - 1] = arr[i];   // shift left
            arr[n - 1] = first;                      // it re-enters at the back
        }

        const l = [10, 20, 30, 40, 50];
        rotateByOne(l);
        console.log("rotated:", l.join(" "));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Rotating by `d` positions by repeating this `d` times costs `O(n·d)`. The `O(n)` answer is the **reversal algorithm**: reverse the first `d`, reverse the rest, then reverse the whole array — covered in DSA Advanced → Arrays.")

    yield section("Collecting input into a list: chicken or duck", "egg")
    yield p("A small competitive-programming exercise from the notes that shows the standard pattern of reading `T` test cases **into a list first** and processing them afterwards. A chicken has `X` legs, a duck `Y` legs; given `Z` legs in total, could they all be chickens (`Z % X == 0`), all ducks, either (`Any`) or neither (`Null`)?")
    yield io("4 cases: (2 3 6), (2 3 4), (2 3 9), (2 3 7)", "Any / Chicken / Duck / Null")
    yield multi('''
        collected 4 cases
        Any
        Chicken
        Duck
        Null
    ''', stdin="4\n2 3 6\n2 3 4\n2 3 9\n2 3 7\n", py=r'''
        import sys

        data = sys.stdin.read().split()          # read everything at once, split on whitespace
        t = int(data[0])
        cases = []                               # collect every test case in a list first
        pos = 1
        for _ in range(t):
            x, y, z = int(data[pos]), int(data[pos + 1]), int(data[pos + 2])
            cases.append((x, y, z))
            pos += 3
        print("collected", len(cases), "cases")

        for x, y, z in cases:
            chickens = z % x == 0
            ducks = z % y == 0
            if chickens and ducks:
                print("Any")
            elif chickens:
                print("Chicken")
            elif ducks:
                print("Duck")
            else:
                print("Null")
    ''', cpp=r'''
        #include <array>
        #include <iostream>
        #include <vector>
        using namespace std;

        int main() {
            int t;
            cin >> t;
            vector<array<int, 3>> cases;          // collect every test case in a list first
            for (int i = 0; i < t; i++) {
                int x, y, z;
                cin >> x >> y >> z;
                cases.push_back({x, y, z});
            }
            cout << "collected " << cases.size() << " cases\n";

            for (auto& c : cases) {
                bool chickens = c[2] % c[0] == 0;
                bool ducks = c[2] % c[1] == 0;
                if (chickens && ducks) cout << "Any\n";
                else if (chickens) cout << "Chicken\n";
                else if (ducks) cout << "Duck\n";
                else cout << "Null\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.Scanner;

        public class Main {
            public static void main(String[] args) {
                Scanner in = new Scanner(System.in);
                int t = in.nextInt();
                List<int[]> cases = new ArrayList<>();      // collect every test case in a list first
                for (int i = 0; i < t; i++)
                    cases.add(new int[]{in.nextInt(), in.nextInt(), in.nextInt()});
                System.out.println("collected " + cases.size() + " cases");

                for (int[] c : cases) {
                    boolean chickens = c[2] % c[0] == 0;
                    boolean ducks = c[2] % c[1] == 0;
                    if (chickens && ducks) System.out.println("Any");
                    else if (chickens) System.out.println("Chicken");
                    else if (ducks) System.out.println("Duck");
                    else System.out.println("Null");
                }
            }
        }
    ''', js=r'''
        import { readFileSync } from "node:fs";

        const data = readFileSync(0, "utf8").trim().split(/\s+/).map(Number);   // fd 0 = stdin
        const t = data[0];
        const cases = [];                              // collect every test case in a list first
        for (let i = 0; i < t; i++)
            cases.push(data.slice(1 + 3 * i, 4 + 3 * i));
        console.log("collected", cases.length, "cases");

        for (const [x, y, z] of cases) {
            const chickens = z % x === 0;
            const ducks = z % y === 0;
            if (chickens && ducks) console.log("Any");
            else if (chickens) console.log("Chicken");
            else if (ducks) console.log("Duck");
            else console.log("Null");
        }
    ''')
    yield complexity("O(T)", "O(T)")
    yield note("Reading all of standard input in one go (`sys.stdin.read()`, `readFileSync(0)`) is much faster than calling `input()` in a loop when there are thousands of lines — a common cause of “Time Limit Exceeded”.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why is appending to a dynamic array O(1) amortised and not O(1) worst case?",
             "A single append can trigger a resize that copies all `n` elements — that one call is `O(n)`. But after growing by a constant factor the next ~`n` appends are free, so the total cost of `n` appends is `O(n)` and the *average* per append is `O(1)`. Worst case for one call remains `O(n)`; amortised analysis spreads the rare expensive call over the cheap ones.")
    yield qa("Array vs linked list — when would you pick each?",
             "Arrays: `O(1)` random access, cache-friendly, less memory per element; but `O(n)` insert/delete in the middle. Linked lists: `O(1)` insert/delete *at a known node* and no resizing; but `O(n)` to reach the k-th element and poor locality. For most workloads arrays (vectors) win; linked lists shine for queues/deques and when you hold references to nodes.")
    yield qa("What is the difference between l.sort() and sorted(l)? Between l.reverse() and l[::-1]?",
             "`l.sort()` and `l.reverse()` modify the list **in place** and return `None`; `sorted(l)` and `l[::-1]` leave `l` alone and return a **new list**. A classic bug is `l = l.sort()`, which sets `l` to `None`.")
    yield qa("Why does `[[0] * 3] * 3` behave strangely?",
             "The outer `*` copies the *reference* to the same inner list three times, so changing `grid[0][0]` changes every row. Build nested lists with a comprehension: `[[0] * 3 for _ in range(3)]`.")
    yield qa("How do you find the second largest in one pass, and what about duplicates?",
             "Track `largest` and `second`. If `x > largest`, demote `largest` to `second` and take `x`; else if `x != largest` and `x > second`, update `second`. Skipping `x == largest` means duplicates of the maximum do not count — `[10, 10, 5]` gives `5`, and `[10, 10]` gives `None`. State that convention aloud.")
    yield qa("Removing duplicates: why does the in-place solution need sorted input?",
             "It only compares each element with the **last kept** one, which is enough when equal values are adjacent. For unsorted input equal values can be far apart, so you need a hash set (`O(n)` space) or a sort first (`O(n log n)`).")


@topic(G, "string", "String (Immutable)", "letter-case")
def _():
    yield lead("A string is a **sequence of characters** — text read from a file, a name, a message. In Python, Java and JavaScript strings are **immutable**: every “change” creates a new string. Most string problems are really array problems in disguise (two pointers, counting with a frequency array), so this topic reuses everything from Lists.")
    yield define("String", "an ordered, indexable sequence of characters. Each character is stored as a number — its character code — so `'A'` is `65`, `'a'` is `97` and `'0'` is `48`; comparisons and “count the letters” tricks rely on these codes.")
    yield define("Immutable", "the object's contents cannot change after creation. `s[0] = 'x'` is an error; `s.upper()` returns a **new** string and leaves `s` untouched. Changing text means building a new string (or using a mutable buffer: a list of characters, `StringBuilder`, an array).")
    yield diagram('''
        s   =   g    e    e    k
        index   0    1    2    3
        -ve    -4   -3   -2   -1
    ''', "Indexing a string works exactly like a list — including Python's negative indices")

    yield section("Characters are numbers: ASCII codes", "binary")
    yield p("Typically a program deals with a small set of characters. ASCII assigns each one a number from 0 to 127; the ranges below are the ones that matter in DSA, because a frequency array of size 128 or 256 indexed by the code gives `O(1)` counting.")
    yield table(
        ["Characters", "Codes", "Note"],
        ["`'A'` … `'Z'`", "65 … 90", "`ord('A') + 32 == ord('a')` — one bit apart"],
        ["`'a'` … `'z'`", "97 … 122", "letters are contiguous, so `ord(c) - ord('a')` is 0..25"],
        ["`'0'` … `'9'`", "48 … 57", "`ord(c) - ord('0')` converts a digit character to its value"],
        ["space", "32", "the first printable character"],
    )
    yield multi('''
        a 97
        A 65
        z 122
        Z 90
        0 48
        9 57
        space 32
        97 a
        65 A
        48 0
    ''', py=r'''
        for ch in "aAzZ09":
            print(ch, ord(ch))               # ord: character → code
        print("space", ord(" "))
        for code in (97, 65, 48):
            print(code, chr(code))           # chr: code → character
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        int main() {
            for (char ch : string("aAzZ09"))
                cout << ch << " " << (int)ch << "\n";       // a char IS a small integer; cast to print it
            cout << "space " << (int)' ' << "\n";
            for (int code : {97, 65, 48})
                cout << code << " " << (char)code << "\n";
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                for (char ch : "aAzZ09".toCharArray())
                    System.out.println(ch + " " + (int) ch);     // cast char → int
                System.out.println("space " + (int) ' ');
                for (int code : new int[]{97, 65, 48})
                    System.out.println(code + " " + (char) code);
            }
        }
    ''', js=r'''
        for (const ch of "aAzZ09")
            console.log(ch, ch.charCodeAt(0));          // code of the character at index 0
        console.log("space", " ".charCodeAt(0));
        for (const code of [97, 65, 48])
            console.log(code, String.fromCharCode(code));
    ''')
    yield note("Python 3 strings are Unicode: `ord('€')` is `8364`, so a 256-slot count array only works when the input is guaranteed ASCII. Say so in an interview, or use a dictionary / hash map instead.")

    yield section("What “immutable” means in each language", "lock")
    yield table(
        ["Language", "Type", "Mutable?", "`s[0] = 'G'`", "Efficient way to build / edit text"],
        ["Python", "`str`", "no", "`TypeError`", "`list(s)` → edit → `''.join(…)`; `''.join(parts)` instead of `+=` in a loop"],
        ["Java", "`String`", "no", "compile error (no indexer)", "`StringBuilder` (`append`, `setCharAt`, `reverse`), or `char[]` via `toCharArray()`"],
        ["JavaScript", "`string`", "no", "silently ignored (throws in strict mode)", "`s.split('')` → edit → `join('')`; collect parts in an array and `join`"],
        ["C++", "`std::string`", "**yes**", "works — `s[0] = 'G'`", "edit in place; `+=` and `push_back` are amortised `O(1)`"],
    )
    yield p("Immutability is what makes strings safe to share, usable as dictionary keys (their hash can never change) and cheap to compare by identity in interned pools. The price: every modification allocates a new string, so **repeated concatenation in a loop is `O(n²)`** in principle — collect pieces and join them once.")
    yield snippet("py", r'''
        s = 'geek'
        s[0] = 'G'                 # strings cannot be changed in place
    ''', fails=True)
    yield output("TypeError: 'str' object does not support item assignment")
    yield p("Changing one character the right way in each language — note that C++ edits a *copy* only because we chose to keep the original:")
    yield multi('''
        new: Geek
        original: geek
    ''', py=r'''
        s = "geek"
        t = "G" + s[1:]                 # build a new string; s is untouched
        print("new:", t)
        print("original:", s)
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        int main() {
            string s = "geek";
            string t = s;               // copy …
            t[0] = 'G';                 // … then mutate in place: std::string is mutable
            cout << "new: " << t << "\n";
            cout << "original: " << s << "\n";
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                String s = "geek";
                char[] chars = s.toCharArray();   // mutable copy of the characters
                chars[0] = 'G';
                String t = new String(chars);     // or: "G" + s.substring(1)
                System.out.println("new: " + t);
                System.out.println("original: " + s);
            }
        }
    ''', js=r'''
        const s = "geek";
        const t = "G" + s.slice(1);     // build a new string; s is untouched
        console.log("new:", t);
        console.log("original:", s);
    ''')

    yield section("Creating strings", "quote")
    yield p("Single and double quotes are interchangeable in Python; triple quotes allow line breaks inside the literal. Indexing works like a list and `type()` confirms the class.")
    yield code(r'''
        s = 'geek'
        print(s)              # geek
        print(type(s))        # <class 'str'>
        print(s[0], s[3])     # g k
        print(s[-1], s[-4])   # k g
        print(len(s))         # 4

        s = """welcome
        to my world"""        # triple quotes keep the newline
        print(s.splitlines())  # ['welcome', 'to my world']
    ''')

    yield section("Escape sequences", "backslash")
    yield p("A backslash inside a literal gives the next character a special meaning. It is how you put a quote inside a quoted string, a newline inside a one-line literal, or a literal backslash.")
    yield table(
        ["Escape", "Meaning"],
        ["`\\'` , `\\\"`", "a quote that does not end the string"],
        ["`\\n`", "newline"],
        ["`\\t`", "tab"],
        ["`\\\\`", "one literal backslash"],
        ["`\\uXXXX`", "Unicode character by code (Python, Java, JavaScript)"],
    )
    yield p("Without escaping, a quote inside the string ends it early — the rest is a syntax error:")
    yield snippet("py", r'''
        s = 'Welcome to my worl'd'      # the second ' closes the literal; d' is garbage
        print(s)
    ''', fails=True)
    yield output("SyntaxError: unterminated string literal")
    yield snippet("py", r'''
        print('Welcome to my worl\'d')      # escape the quote …
        print("Welcome to my worl'd")       # … or just use the other quote style
        print("Hi,\nI'm fine")
        print('A simple example \\')
        print('A simple \t example')
    ''', out="Welcome to my worl'd\nWelcome to my worl'd\nHi,\nI'm fine\nA simple example \\\nA simple \t example")
    yield pitfall("A backslash before a letter that is **not** an escape (`'A simple \\example'`) is kept literally, but Python emits a `SyntaxWarning: invalid escape sequence` — and future versions may make it an error. Write `\\\\` or use a raw string.")

    yield section("Raw strings", "letter-r")
    yield p("Prefixing a literal with `r` (or `R`) turns escape processing off — backslashes are kept as typed. Essential for Windows paths and regular expressions, where `\\n`, `\\t` or `\\d` would otherwise be mangled.")
    yield code(r'''
        s1 = 'c:\new\table.py'         # \n and \t are escapes!
        print(repr(s1))                # 'c:\new\table.py'  ← repr shows the escapes; print() would show a line break and a tab
        print(s1.count("\n"), s1.count("\t"))   # 1 1
        s2 = r'c:\new\table.py'        # raw: backslashes are kept
        print(s2)                      # c:\new\table.py
        print(len(s1), len(s2))        # 13 15
    ''')
    yield note("A raw string still cannot end in a single backslash (`r'c:\\'` is a syntax error) because the quote would be escaped. Use `'c:\\\\'` or `r'c:\\' + '\\\\'` for that case. Java and JavaScript have no raw strings; use `\\\\` (or JavaScript's `String.raw` tag).")

    yield section("Formatted strings", "braces")
    yield p("Three generations of Python formatting do the same job; **f-strings** (3.6+) are the modern choice — any expression goes inside the braces, with optional format specs such as `:.2f` or `:>10`.")
    yield code(r'''
        name = 'ABC'
        course = 'Python Course'
        print('Welcome %s to %s' % (name, course))            # Welcome ABC to Python Course  ← C-style %
        print('Welcome {} to {}'.format(name, course))        # Welcome ABC to Python Course  ← str.format
        print(f'Welcome {name} to {course}')                  # Welcome ABC to Python Course  ← f-string
    ''')
    yield multi('''
        Sum of 10 and 20 is 30
        lower case of ABC is abc
        upper case of abc is ABC
    ''', py=r'''
        a, b = 10, 20
        print(f'Sum of {a} and {b} is {a + b}')      # any expression inside the braces

        x, y = 'ABC', 'abc'
        print(f"lower case of {x} is {x.lower()}")
        print(f"upper case of {y} is {y.upper()}")
    ''', cpp=r'''
        #include <algorithm>
        #include <cctype>
        #include <iostream>
        #include <string>
        using namespace std;

        int main() {
            int a = 10, b = 20;
            cout << "Sum of " << a << " and " << b << " is " << a + b << "\n";   // or printf("%d", …)

            string x = "ABC", y = "abc";
            string lower = x, upper = y;
            transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
            transform(upper.begin(), upper.end(), upper.begin(), ::toupper);
            cout << "lower case of " << x << " is " << lower << "\n";
            cout << "upper case of " << y << " is " << upper << "\n";
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                int a = 10, b = 20;
                System.out.println(String.format("Sum of %d and %d is %d", a, b, a + b));   // printf-style

                String x = "ABC", y = "abc";
                System.out.println("lower case of " + x + " is " + x.toLowerCase());
                System.out.println("upper case of " + y + " is " + y.toUpperCase());
            }
        }
    ''', js=r'''
        const a = 10, b = 20;
        console.log(`Sum of ${a} and ${b} is ${a + b}`);     // template literal: backticks + ${…}

        const x = "ABC", y = "abc";
        console.log(`lower case of ${x} is ${x.toLowerCase()}`);
        console.log(`upper case of ${y} is ${y.toUpperCase()}`);
    ''')

    yield section("String comparison", "equal")
    yield p("`==` compares **contents** character by character. `<` and `>` compare **lexicographically**: the first differing character decides, using character codes — so every uppercase letter sorts before every lowercase one, and a prefix sorts before the longer string.")
    yield multi('''
        gfg == ide: false
        gfg != ide: true
        gfg > ide: false
        gfg < ide: true
        gfg <= ide: true
        apple < banana: true
        Zebra < apple: true
        ab < abc: true
    ''', py=r'''
        s1, s2 = 'gfg', 'ide'
        b = lambda v: "true" if v else "false"
        print("gfg == ide:", b(s1 == s2))
        print("gfg != ide:", b(s1 != s2))
        print("gfg > ide:", b(s1 > s2))            # 'g' (103) < 'i' (105) → gfg is smaller
        print("gfg < ide:", b(s1 < s2))
        print("gfg <= ide:", b(s1 <= s2))
        print("apple < banana:", b("apple" < "banana"))
        print("Zebra < apple:", b("Zebra" < "apple"))    # 'Z' (90) < 'a' (97): uppercase first
        print("ab < abc:", b("ab" < "abc"))              # a prefix is smaller
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        const char* b(bool v) { return v ? "true" : "false"; }

        int main() {
            string s1 = "gfg", s2 = "ide";              // std::string overloads ==, <, > …
            cout << "gfg == ide: " << b(s1 == s2) << "\n";
            cout << "gfg != ide: " << b(s1 != s2) << "\n";
            cout << "gfg > ide: " << b(s1 > s2) << "\n";
            cout << "gfg < ide: " << b(s1 < s2) << "\n";
            cout << "gfg <= ide: " << b(s1 <= s2) << "\n";
            cout << "apple < banana: " << b(string("apple") < "banana") << "\n";
            cout << "Zebra < apple: " << b(string("Zebra") < "apple") << "\n";
            cout << "ab < abc: " << b(string("ab") < "abc") << "\n";
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                String s1 = "gfg", s2 = "ide";
                System.out.println("gfg == ide: " + s1.equals(s2));          // NOT s1 == s2 (reference check)
                System.out.println("gfg != ide: " + !s1.equals(s2));
                System.out.println("gfg > ide: " + (s1.compareTo(s2) > 0));  // compareTo: <0, 0, >0
                System.out.println("gfg < ide: " + (s1.compareTo(s2) < 0));
                System.out.println("gfg <= ide: " + (s1.compareTo(s2) <= 0));
                System.out.println("apple < banana: " + ("apple".compareTo("banana") < 0));
                System.out.println("Zebra < apple: " + ("Zebra".compareTo("apple") < 0));
                System.out.println("ab < abc: " + ("ab".compareTo("abc") < 0));
            }
        }
    ''', js=r'''
        const s1 = "gfg", s2 = "ide";
        console.log("gfg == ide:", s1 === s2);          // === compares contents for strings
        console.log("gfg != ide:", s1 !== s2);
        console.log("gfg > ide:", s1 > s2);
        console.log("gfg < ide:", s1 < s2);
        console.log("gfg <= ide:", s1 <= s2);
        console.log("apple < banana:", "apple" < "banana");
        console.log("Zebra < apple:", "Zebra" < "apple");    // 'Z' (90) < 'a' (97): uppercase first
        console.log("ab < abc:", "ab" < "abc");              // a prefix is smaller
    ''')
    yield pitfall("In Java `s1 == s2` asks whether both variables point to the **same object**. It happens to be `true` for two identical literals (they are interned) and `false` for strings built at runtime — always use `equals()`. For case-insensitive comparison use `s.lower()` / `equalsIgnoreCase` / `toLowerCase()`.")

    yield section("String operations", "tools")
    yield p("A substring is a contiguous piece: the substrings of `'ABCD'` include `'A'`, `'AB'`, `'BCD'`, `'ABCD'` — but not `'AC'` (that is a *subsequence*). `in` tests for a substring, `+` concatenates, `index`/`find` locate one.")
    yield code(r'''
        s1 = 'geeksforgeeks'
        s2 = 'geeks'
        print(s2 in s1)          # True
        print(s2 not in s1)      # False
        print(s1 in s2)          # False  ← the longer string cannot be inside the shorter one

        print('geeks' + 'for' + 'geeks')             # geeksforgeeks  ← concatenation makes a new string
        print('geeks' + ' ' + 'for' + ' ' + 'geeks')  # geeks for geeks

        print(s1.index(s2))      # 0   ← first occurrence
        print(s1.rindex(s2))     # 8   ← last occurrence
        print(s1.index(s2, 1))   # 8   ← first occurrence at or after index 1
        print(s1.find('xyz'))    # -1  ← find returns -1; index would raise ValueError
    ''')
    yield p("The everyday toolbox, all of which return **new** strings or plain values:")
    yield code(r'''
        s1 = 'Thrishank is a name'
        s2 = 'Kav'
        print(len(s1))                           # 19
        print(s1.upper())                        # THRISHANK IS A NAME
        print(s1.lower())                        # thrishank is a name
        print(s1.isupper())                      # False
        print(s1.islower())                      # False
        print(s1.startswith('Th'))               # True
        print(s1.startswith('th'))               # False  ← case-sensitive
        print(s1.endswith('nk'))                 # False  ← it ends with 'name'
        print(s1.startswith(" ", 1))             # False  ← does s1[1:] start with a space? no, with 'h'
        print(s1.endswith('a', 5, len(s1)))      # False  ← s1[5:19] ends with 'e'
        print(s1.split(' '))                     # ['Thrishank', 'is', 'a', 'name']
        print(s1.split('n'))                     # ['Thrisha', 'k is a ', 'ame']
        print(s1.split('r', 1))                  # ['Th', 'ishank is a name']  ← at most 1 split
        print(''.join(s1))                       # Thrishank is a name
        print(' '.join(s1))                      # T h r i s h a n k   i s   a   n a m e
        print(s1.strip(" "))                     # Thrishank is a name  ← nothing to strip here
        print(s1.lstrip(" "))                    # Thrishank is a name
        print(s1.rstrip(" "))                    # Thrishank is a name
        print(s1.replace('Thrishank', 'Kavya'))  # Kavya is a name
        print(s1.replace('h', 'H'))              # THrisHank is a name  ← every occurrence
        print(s1.find(s2))                       # -1
        print(s1.find(s2, 0, 13))                # -1
        print(s1.find('sha'))                    # 4
    ''')
    yield table(
        ["Task", "Python", "C++ `std::string`", "Java `String`", "JavaScript"],
        ["Length", "`len(s)`", "`s.size()`", "`s.length()`", "`s.length`"],
        ["Character at `i`", "`s[i]`", "`s[i]`", "`s.charAt(i)`", "`s[i]`"],
        ["Substring", "`s[a:b]`", "`s.substr(a, b - a)`", "`s.substring(a, b)`", "`s.slice(a, b)`"],
        ["Contains", "`t in s`", "`s.find(t) != npos`", "`s.contains(t)`", "`s.includes(t)`"],
        ["Find index", "`s.find(t)` (−1)", "`s.find(t)` (`npos`)", "`s.indexOf(t)` (−1)", "`s.indexOf(t)` (−1)"],
        ["Upper / lower", "`s.upper()`", "`transform(…, ::toupper)`", "`s.toUpperCase()`", "`s.toUpperCase()`"],
        ["Starts / ends with", "`s.startswith(t)`", "`s.starts_with(t)` (C++20)", "`s.startsWith(t)`", "`s.startsWith(t)`"],
        ["Split on spaces", "`s.split()`", "`istringstream >> word`", "`s.split(\" \")`", "`s.split(\" \")`"],
        ["Join", "`\" \".join(parts)`", "loop with `+=`", "`String.join(\" \", parts)`", "`parts.join(\" \")`"],
        ["Trim whitespace", "`s.strip()`", "manual", "`s.strip()` / `s.trim()`", "`s.trim()`"],
        ["Replace all", "`s.replace(a, b)`", "loop with `find`", "`s.replace(a, b)`", "`s.replaceAll(a, b)`"],
        ["Compare", "`==`, `<`", "`==`, `<`", "`equals`, `compareTo`", "`===`, `<`"],
    )

    yield section("Problem: reverse a string", "arrows-left-right")
    yield io("s = \"Nani\"", "inaN", "s = \"hello\"", "olleh")
    yield p("The naive loop builds the answer by prepending each character — `rev = ch + rev`. Because strings are immutable, every step copies the whole partial result, so it is `O(n²)`:")
    yield snippet("py", r'''
        s = "Nani"
        rev = ""
        for ch in s:
            rev = ch + rev           # new string of length k at step k → O(n²) total
        print(rev)

        print(s[::-1])               # the Pythonic way: slice with step -1 → O(n)
    ''', out='''
        inaN
        inaN
    ''')
    yield idea("Turn the string into a mutable sequence of characters, swap from both ends with two pointers (exactly as for a list) and join back. Where the string is already mutable (C++) swap in place.")
    yield multi('''
        reversed: inaN
        reversed: olleh
    ''', py=r'''
        def reverse(s):
            chars = list(s)                    # mutable copy
            i, j = 0, len(chars) - 1
            while i < j:
                chars[i], chars[j] = chars[j], chars[i]
                i += 1
                j -= 1
            return "".join(chars)              # back to an (immutable) string

        for s in ("Nani", "hello"):
            print("reversed:", reverse(s))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <utility>
        using namespace std;

        string reverseStr(string s) {         // taken by value → we may edit the copy in place
            int i = 0, j = s.size() - 1;
            while (i < j) {
                swap(s[i], s[j]);
                i++;
                j--;
            }
            return s;                          // library: reverse(s.begin(), s.end())
        }

        int main() {
            for (string s : {"Nani", "hello"})
                cout << "reversed: " << reverseStr(s) << "\n";
        }
    ''', java=r'''
        public class Main {
            static String reverse(String s) {
                char[] c = s.toCharArray();                  // mutable copy
                int i = 0, j = c.length - 1;
                while (i < j) {
                    char tmp = c[i]; c[i] = c[j]; c[j] = tmp;
                    i++;
                    j--;
                }
                return new String(c);                        // library: new StringBuilder(s).reverse()
            }

            public static void main(String[] args) {
                for (String s : new String[]{"Nani", "hello"})
                    System.out.println("reversed: " + reverse(s));
            }
        }
    ''', js=r'''
        function reverse(s) {
            const c = s.split("");                        // mutable copy
            let i = 0, j = c.length - 1;
            while (i < j) {
                [c[i], c[j]] = [c[j], c[i]];
                i++;
                j--;
            }
            return c.join("");                            // library: s.split("").reverse().join("")
        }

        for (const s of ["Nani", "hello"])
            console.log("reversed:", reverse(s));
    ''')
    yield complexity("O(n)", "O(n) for the character copy (O(1) in C++)")

    yield section("Problem: check if two strings are rotations", "rotate")
    yield io("s1 = \"ABCD\", s2 = \"CDAB\"", "Yes", "s1 = \"ABCD\", s2 = \"ABCA\"", "No")
    yield p("`ABCD → BCDA → CDAB`: rotating left twice turns `ABCD` into `CDAB`. Trying every rotation and comparing is `O(n²)`.")
    yield idea("Concatenate `s1` with itself: `ABCDABCD` contains **every** rotation of `ABCD` as a substring (`BCDA`, `CDAB`, `DABC`). So `s2` is a rotation exactly when the lengths match and `s2` occurs inside `s1 + s1`.")
    yield diagram('''
        s1 + s1 = A B C D A B C D
                      └─────┘        CDAB  (rotation by 2)
                    └─────┘          BCDA  (rotation by 1)
                          └─────┘    DABC  (rotation by 3)
    ''', "Every rotation of s1 is a window of length n inside s1 + s1")
    yield multi('''
        ABCD, CDAB: Yes
        ABCD, ABCA: No
        ABCD, ABC: No
    ''', py=r'''
        def are_rotations(s1, s2):
            if len(s1) != len(s2):
                return False
            return s2 in s1 + s1             # substring search

        for s1, s2 in (("ABCD", "CDAB"), ("ABCD", "ABCA"), ("ABCD", "ABC")):
            print(f"{s1}, {s2}:", "Yes" if are_rotations(s1, s2) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        bool areRotations(const string& s1, const string& s2) {
            if (s1.size() != s2.size()) return false;
            return (s1 + s1).find(s2) != string::npos;     // substring search
        }

        int main() {
            pair<string, string> tests[] = {{"ABCD", "CDAB"}, {"ABCD", "ABCA"}, {"ABCD", "ABC"}};
            for (auto& t : tests)
                cout << t.first << ", " << t.second << ": " << (areRotations(t.first, t.second) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean areRotations(String s1, String s2) {
                if (s1.length() != s2.length()) return false;
                return (s1 + s1).contains(s2);             // substring search
            }

            public static void main(String[] args) {
                String[][] tests = {{"ABCD", "CDAB"}, {"ABCD", "ABCA"}, {"ABCD", "ABC"}};
                for (String[] t : tests)
                    System.out.println(t[0] + ", " + t[1] + ": " + (areRotations(t[0], t[1]) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function areRotations(s1, s2) {
            if (s1.length !== s2.length) return false;
            return (s1 + s1).includes(s2);                 // substring search
        }

        for (const [s1, s2] of [["ABCD", "CDAB"], ["ABCD", "ABCA"], ["ABCD", "ABC"]])
            console.log(`${s1}, ${s2}:`, areRotations(s1, s2) ? "Yes" : "No");
    ''')
    yield complexity("O(n) with a linear-time substring search (KMP); naive `find` is O(n²) worst case", "O(n)")
    yield pitfall("Forgetting the length check: `\"AB\"` is a substring of `\"ABCDABCD\"` but not a rotation of `\"ABCD\"`.")

    yield section("Problem: check for palindrome", "arrows-horizontal")
    yield io("s = \"abba\"", "Yes", "s = \"abA\"", "No", "s = \"10022001\"", "Yes")
    yield p("A palindrome reads the same backwards. The check is case-sensitive unless stated otherwise (`abA` is not one). Fun fact from the notes: the date `10-02-2001` without separators, `10022001`, is a palindrome.")
    yield idea("Two pointers again: compare `s[low]` with `s[high]`, move them towards each other, and stop with `No` at the first mismatch. If they cross without a mismatch the string is a palindrome. No copy of the string is needed.")
    yield multi('''
        abba: Yes
        abA: No
        10022001: Yes
        racecar: Yes
    ''', py=r'''
        def is_palindrome(s):
            low, high = 0, len(s) - 1
            while low < high:
                if s[low] != s[high]:
                    return False
                low += 1
                high -= 1
            return True                     # one-liner: s == s[::-1] (but that copies the string)

        for s in ("abba", "abA", "10022001", "racecar"):
            print(f"{s}:", "Yes" if is_palindrome(s) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        bool isPalindrome(const string& s) {
            int low = 0, high = s.size() - 1;
            while (low < high) {
                if (s[low] != s[high]) return false;
                low++;
                high--;
            }
            return true;
        }

        int main() {
            for (string s : {"abba", "abA", "10022001", "racecar"})
                cout << s << ": " << (isPalindrome(s) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isPalindrome(String s) {
                int low = 0, high = s.length() - 1;
                while (low < high) {
                    if (s.charAt(low) != s.charAt(high)) return false;
                    low++;
                    high--;
                }
                return true;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"abba", "abA", "10022001", "racecar"})
                    System.out.println(s + ": " + (isPalindrome(s) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isPalindrome(s) {
            let low = 0, high = s.length - 1;
            while (low < high) {
                if (s[low] !== s[high]) return false;
                low++;
                high--;
            }
            return true;
        }

        for (const s of ["abba", "abA", "10022001", "racecar"])
            console.log(`${s}:`, isPalindrome(s) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Python's `while … else` from the original notes runs the `else` branch only when the loop finished without `break` — the same effect as returning `True` after the loop. The interview follow-up is usually “ignore case and non-letters” (`\"A man, a plan…\"`): skip characters that are not alphanumeric and compare lower-cased.")

    yield section("Problem: check if a string is a subsequence", "arrow-right-circle")
    yield io("s1 = \"ABCD\", s2 = \"AD\"", "Yes", "s1 = \"ABCDE\", s2 = \"AED\"", "No")
    yield define("Subsequence", "the characters of `s2` appear in `s1` in the **same order**, not necessarily adjacent. `AD` is a subsequence of `ABCD`; `AED` is not, because `E` comes after `D` in `ABCDE`.")
    yield idea("Greedy two pointers: walk through `s1` once; whenever the current character matches `s2[j]`, advance `j`. If `j` reaches the end of `s2`, every character was found in order. Matching the *earliest* possible occurrence is always safe — it leaves the most room for the rest.")
    yield multi('''
        AD in ABCD: Yes
        AED in ABCDE: No
        ACE in ABCDE: Yes
    ''', py=r'''
        def is_subsequence(s1, s2):
            i = j = 0
            while i < len(s1) and j < len(s2):
                if s1[i] == s2[j]:
                    j += 1                       # matched s2[j], look for the next one
                i += 1
            return j == len(s2)

        for s1, s2 in (("ABCD", "AD"), ("ABCDE", "AED"), ("ABCDE", "ACE")):
            print(f"{s2} in {s1}:", "Yes" if is_subsequence(s1, s2) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        bool isSubsequence(const string& s1, const string& s2) {
            int i = 0, j = 0, n = s1.size(), m = s2.size();
            while (i < n && j < m) {
                if (s1[i] == s2[j]) j++;         // matched s2[j], look for the next one
                i++;
            }
            return j == m;
        }

        int main() {
            pair<string, string> tests[] = {{"ABCD", "AD"}, {"ABCDE", "AED"}, {"ABCDE", "ACE"}};
            for (auto& t : tests)
                cout << t.second << " in " << t.first << ": " << (isSubsequence(t.first, t.second) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isSubsequence(String s1, String s2) {
                int i = 0, j = 0;
                while (i < s1.length() && j < s2.length()) {
                    if (s1.charAt(i) == s2.charAt(j)) j++;   // matched s2[j], look for the next one
                    i++;
                }
                return j == s2.length();
            }

            public static void main(String[] args) {
                String[][] tests = {{"ABCD", "AD"}, {"ABCDE", "AED"}, {"ABCDE", "ACE"}};
                for (String[] t : tests)
                    System.out.println(t[1] + " in " + t[0] + ": " + (isSubsequence(t[0], t[1]) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isSubsequence(s1, s2) {
            let i = 0, j = 0;
            while (i < s1.length && j < s2.length) {
                if (s1[i] === s2[j]) j++;        // matched s2[j], look for the next one
                i++;
            }
            return j === s2.length;
        }

        for (const [s1, s2] of [["ABCD", "AD"], ["ABCDE", "AED"], ["ABCDE", "ACE"]])
            console.log(`${s2} in ${s1}:`, isSubsequence(s1, s2) ? "Yes" : "No");
    ''')
    yield complexity("O(n + m)", "O(1)")
    yield p("The same idea written recursively, from the back: if the last characters match, drop both; otherwise drop only the last character of `s1`. It is `O(n + m)` time but uses `O(n)` stack — the iterative version is preferred.")
    yield snippet("py", r'''
        def is_subsequence(s1, s2, m, n):      # m, n = lengths still to consider
            if n == 0:
                return True                   # all of s2 matched
            if m == 0:
                return False                  # s1 exhausted first
            if s1[m - 1] == s2[n - 1]:
                return is_subsequence(s1, s2, m - 1, n - 1)
            return is_subsequence(s1, s2, m - 1, n)

        print("Yes" if is_subsequence("ABCD", "AD", 4, 2) else "No")
        print("Yes" if is_subsequence("ABCDE", "AED", 5, 3) else "No")
    ''', out='''
        Yes
        No
    ''')

    yield section("Problem: check for anagram", "arrows-shuffle")
    yield io("s1 = \"listen\", s2 = \"silent\"", "Yes", "s1 = \"aabc\", s2 = \"acab\"", "Yes", "s1 = \"aabd\", s2 = \"acab\"", "No")
    yield define("Anagram", "two strings with the **same length**, the **same characters** and the **same count** of each — one is a rearrangement of the other.")
    yield p("Naive: sort both strings and compare — `O(n log n)`:")
    yield snippet("py", r'''
        def are_anagrams_sorted(s1, s2):
            return len(s1) == len(s2) and sorted(s1) == sorted(s2)

        print("Yes" if are_anagrams_sorted("listen", "silent") else "No")
        print("Yes" if are_anagrams_sorted("aabd", "acab") else "No")
    ''', out='''
        Yes
        No
    ''')
    yield idea("Count characters with a frequency array indexed by character code: `+1` for each character of `s1`, `-1` for each of `s2`. The strings are anagrams exactly when every count ends at zero. One pass over the strings plus a fixed 256-slot scan → `O(n)`.")
    yield multi('''
        listen, silent: Yes
        aabc, acab: Yes
        aabd, acab: No
    ''', py=r'''
        CHAR = 256

        def are_anagrams(s1, s2):
            if len(s1) != len(s2):
                return False
            count = [0] * CHAR
            for i in range(len(s1)):
                count[ord(s1[i])] += 1          # s1 adds …
                count[ord(s2[i])] -= 1          # … s2 cancels
            return all(c == 0 for c in count)

        for s1, s2 in (("listen", "silent"), ("aabc", "acab"), ("aabd", "acab")):
            print(f"{s1}, {s2}:", "Yes" if are_anagrams(s1, s2) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        const int CHAR = 256;

        bool areAnagrams(const string& s1, const string& s2) {
            if (s1.size() != s2.size()) return false;
            int count[CHAR] = {0};
            for (int i = 0; i < (int)s1.size(); i++) {
                count[(unsigned char)s1[i]]++;        // s1 adds …
                count[(unsigned char)s2[i]]--;        // … s2 cancels
            }
            for (int c : count)
                if (c != 0) return false;
            return true;
        }

        int main() {
            pair<string, string> tests[] = {{"listen", "silent"}, {"aabc", "acab"}, {"aabd", "acab"}};
            for (auto& t : tests)
                cout << t.first << ", " << t.second << ": " << (areAnagrams(t.first, t.second) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static final int CHAR = 256;

            static boolean areAnagrams(String s1, String s2) {
                if (s1.length() != s2.length()) return false;
                int[] count = new int[CHAR];
                for (int i = 0; i < s1.length(); i++) {
                    count[s1.charAt(i)]++;              // s1 adds …
                    count[s2.charAt(i)]--;              // … s2 cancels
                }
                for (int c : count)
                    if (c != 0) return false;
                return true;
            }

            public static void main(String[] args) {
                String[][] tests = {{"listen", "silent"}, {"aabc", "acab"}, {"aabd", "acab"}};
                for (String[] t : tests)
                    System.out.println(t[0] + ", " + t[1] + ": " + (areAnagrams(t[0], t[1]) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        const CHAR = 256;

        function areAnagrams(s1, s2) {
            if (s1.length !== s2.length) return false;
            const count = new Array(CHAR).fill(0);
            for (let i = 0; i < s1.length; i++) {
                count[s1.charCodeAt(i)]++;              // s1 adds …
                count[s2.charCodeAt(i)]--;              // … s2 cancels
            }
            return count.every(c => c === 0);
        }

        for (const [s1, s2] of [["listen", "silent"], ["aabc", "acab"], ["aabd", "acab"]])
            console.log(`${s1}, ${s2}:`, areAnagrams(s1, s2) ? "Yes" : "No");
    ''')
    yield complexity("O(n + CHAR)", "O(CHAR) = O(1)")
    yield note("The original notes' second test used `aabd` vs `acab` (not anagrams) while the example said `aabc` vs `acab` (anagrams) — both are included above. For Unicode input swap the 256-array for a dictionary / `HashMap` of counts.")

    yield section("Problem: leftmost repeating character", "repeat")
    yield io("s = \"geeksforgeeks\"", "0", "s = \"abbcc\"", "1", "s = \"abcd\"", "-1")
    yield p("Return the index of the first character that appears **again later**. In `geeksforgeeks` the `g` at index 0 reappears at index 8, so the answer is `0` (not `1`, even though `e` repeats sooner). Naive: for each `i`, scan the rest for an equal character — `O(n²)`:")
    yield snippet("py", r'''
        def leftmost_repeating_naive(s):
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    if s[i] == s[j]:
                        return i
            return -1

        print(leftmost_repeating_naive("geeksforgeeks"))
        print(leftmost_repeating_naive("abcd"))
    ''', out='''
        0
        -1
    ''')
    yield idea("**Two passes, `O(n)`:** count every character first, then walk from the left and return the first index whose character has count `> 1`.")
    yield multi('''
        geeksforgeeks: 0
        abbcc: 1
        abcd: -1
        Thrishank: 1
    ''', py=r'''
        CHAR = 256

        def leftmost_repeating(s):
            count = [0] * CHAR
            for ch in s:
                count[ord(ch)] += 1
            for i, ch in enumerate(s):               # left to right: first one seen more than once
                if count[ord(ch)] > 1:
                    return i
            return -1

        for s in ("geeksforgeeks", "abbcc", "abcd", "Thrishank"):
            print(f"{s}:", leftmost_repeating(s))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        const int CHAR = 256;

        int leftmostRepeating(const string& s) {
            int count[CHAR] = {0};
            for (char ch : s) count[(unsigned char)ch]++;
            for (int i = 0; i < (int)s.size(); i++)          // left to right: first one seen more than once
                if (count[(unsigned char)s[i]] > 1) return i;
            return -1;
        }

        int main() {
            for (string s : {"geeksforgeeks", "abbcc", "abcd", "Thrishank"})
                cout << s << ": " << leftmostRepeating(s) << "\n";
        }
    ''', java=r'''
        public class Main {
            static final int CHAR = 256;

            static int leftmostRepeating(String s) {
                int[] count = new int[CHAR];
                for (int i = 0; i < s.length(); i++) count[s.charAt(i)]++;
                for (int i = 0; i < s.length(); i++)          // left to right: first one seen more than once
                    if (count[s.charAt(i)] > 1) return i;
                return -1;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"geeksforgeeks", "abbcc", "abcd", "Thrishank"})
                    System.out.println(s + ": " + leftmostRepeating(s));
            }
        }
    ''', js=r'''
        const CHAR = 256;

        function leftmostRepeating(s) {
            const count = new Array(CHAR).fill(0);
            for (const ch of s) count[ch.charCodeAt(0)]++;
            for (let i = 0; i < s.length; i++)            // left to right: first one seen more than once
                if (count[s.charCodeAt(i)] > 1) return i;
            return -1;
        }

        for (const s of ["geeksforgeeks", "abbcc", "abcd", "Thrishank"])
            console.log(`${s}:`, leftmostRepeating(s));
    ''')
    yield complexity("O(n + CHAR)", "O(CHAR)")
    yield p("**One pass, storing first indices.** Remember where each character was first seen; on a later sighting, the first index is a candidate answer — keep the smallest. (The original returned `sys.maxsize` when nothing repeats; it should be `-1`.)")
    yield snippet("py", r'''
        CHAR = 256

        def leftmost_repeating(s):
            first_index = [-1] * CHAR
            res = -1
            for i, ch in enumerate(s):
                c = ord(ch)
                if first_index[c] == -1:
                    first_index[c] = i                     # first sighting
                elif res == -1 or first_index[c] < res:
                    res = first_index[c]                   # repeated: its FIRST index is a candidate
            return res

        print(leftmost_repeating("geeksforgeeks"))
        print(leftmost_repeating("Thrishank"))
        print(leftmost_repeating("abcd"))
    ''', out='''
        0
        1
        -1
    ''')
    yield idea("**One pass from the right, the neatest version.** Scan right to left with a `visited` array. When you meet a character you have already seen (further right), it repeats — record this index. Because the scan moves left, the last recorded index is the leftmost one.")
    yield multi('''
        geeksforgeeks: 0
        abbcc: 1
        abcd: -1
        Thrishank: 1
    ''', py=r'''
        CHAR = 256

        def leftmost_repeating(s):
            visited = [False] * CHAR
            res = -1
            for i in range(len(s) - 1, -1, -1):        # right to left
                c = ord(s[i])
                if visited[c]:
                    res = i                            # seen further right → repeats; keep overwriting
                else:
                    visited[c] = True
            return res

        for s in ("geeksforgeeks", "abbcc", "abcd", "Thrishank"):
            print(f"{s}:", leftmost_repeating(s))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        const int CHAR = 256;

        int leftmostRepeating(const string& s) {
            bool visited[CHAR] = {false};
            int res = -1;
            for (int i = (int)s.size() - 1; i >= 0; i--) {    // right to left
                unsigned char c = s[i];
                if (visited[c]) res = i;                       // seen further right → repeats
                else visited[c] = true;
            }
            return res;
        }

        int main() {
            for (string s : {"geeksforgeeks", "abbcc", "abcd", "Thrishank"})
                cout << s << ": " << leftmostRepeating(s) << "\n";
        }
    ''', java=r'''
        public class Main {
            static final int CHAR = 256;

            static int leftmostRepeating(String s) {
                boolean[] visited = new boolean[CHAR];
                int res = -1;
                for (int i = s.length() - 1; i >= 0; i--) {    // right to left
                    char c = s.charAt(i);
                    if (visited[c]) res = i;                   // seen further right → repeats
                    else visited[c] = true;
                }
                return res;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"geeksforgeeks", "abbcc", "abcd", "Thrishank"})
                    System.out.println(s + ": " + leftmostRepeating(s));
            }
        }
    ''', js=r'''
        const CHAR = 256;

        function leftmostRepeating(s) {
            const visited = new Array(CHAR).fill(false);
            let res = -1;
            for (let i = s.length - 1; i >= 0; i--) {     // right to left
                const c = s.charCodeAt(i);
                if (visited[c]) res = i;                   // seen further right → repeats
                else visited[c] = true;
            }
            return res;
        }

        for (const s of ["geeksforgeeks", "abbcc", "abcd", "Thrishank"])
            console.log(`${s}:`, leftmostRepeating(s));
    ''')
    yield complexity("O(n)", "O(CHAR)")

    yield section("Problem: leftmost non-repeating character", "letter-case")
    yield io("s = \"geeksforgeeks\"", "5", "s = \"abcabc\"", "-1")
    yield p("Return the index of the first character that occurs **exactly once**. In `geeksforgeeks` that is `f` at index 5. The naive nested loop is `O(n²)` — and the version in the original notes had its `return -1` indented inside the outer loop, so it gave up after checking only `s[0]`. Fixed:")
    yield snippet("py", r'''
        def non_repeating_naive(s):
            for i in range(len(s)):
                repeated = False
                for j in range(len(s)):
                    if i != j and s[i] == s[j]:
                        repeated = True
                        break
                if not repeated:
                    return i
            return -1                     # must be OUTSIDE the outer loop

        print(non_repeating_naive("geeksforgeeks"))
        print(non_repeating_naive("aaa"))
    ''', out='''
        5
        -1
    ''')
    yield idea("Same frequency array as before: count everything, then return the first index whose character has count exactly `1`. Two passes over the string, `O(n)`.")
    yield multi('''
        geeksforgeeks: 5
        abcabc: -1
        aaa: -1
        Thrishank: 0
    ''', py=r'''
        CHAR = 256

        def leftmost_non_repeating(s):
            count = [0] * CHAR
            for ch in s:
                count[ord(ch)] += 1
            for i, ch in enumerate(s):
                if count[ord(ch)] == 1:              # appears exactly once
                    return i
            return -1

        for s in ("geeksforgeeks", "abcabc", "aaa", "Thrishank"):
            print(f"{s}:", leftmost_non_repeating(s))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        const int CHAR = 256;

        int leftmostNonRepeating(const string& s) {
            int count[CHAR] = {0};
            for (char ch : s) count[(unsigned char)ch]++;
            for (int i = 0; i < (int)s.size(); i++)
                if (count[(unsigned char)s[i]] == 1) return i;   // appears exactly once
            return -1;
        }

        int main() {
            for (string s : {"geeksforgeeks", "abcabc", "aaa", "Thrishank"})
                cout << s << ": " << leftmostNonRepeating(s) << "\n";
        }
    ''', java=r'''
        public class Main {
            static final int CHAR = 256;

            static int leftmostNonRepeating(String s) {
                int[] count = new int[CHAR];
                for (int i = 0; i < s.length(); i++) count[s.charAt(i)]++;
                for (int i = 0; i < s.length(); i++)
                    if (count[s.charAt(i)] == 1) return i;     // appears exactly once
                return -1;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"geeksforgeeks", "abcabc", "aaa", "Thrishank"})
                    System.out.println(s + ": " + leftmostNonRepeating(s));
            }
        }
    ''', js=r'''
        const CHAR = 256;

        function leftmostNonRepeating(s) {
            const count = new Array(CHAR).fill(0);
            for (const ch of s) count[ch.charCodeAt(0)]++;
            for (let i = 0; i < s.length; i++)
                if (count[s.charCodeAt(i)] === 1) return i;    // appears exactly once
            return -1;
        }

        for (const s of ["geeksforgeeks", "abcabc", "aaa", "Thrishank"])
            console.log(`${s}:`, leftmostNonRepeating(s));
    ''')
    yield complexity("O(n + CHAR)", "O(CHAR)")
    yield p("**Single pass over the string** (then a scan of the 256 slots): store each character's first index; mark it `-2` the moment it is seen again. The answer is the smallest index that is still `>= 0`.")
    yield snippet("py", r'''
        CHAR = 256

        def leftmost_non_repeating(s):
            first_index = [-1] * CHAR            # -1 never seen, -2 seen more than once, else the index
            for i, ch in enumerate(s):
                c = ord(ch)
                if first_index[c] == -1:
                    first_index[c] = i
                else:
                    first_index[c] = -2
            res = -1
            for idx in first_index:
                if idx >= 0 and (res == -1 or idx < res):
                    res = idx
            return res

        print(leftmost_non_repeating("geeksforgeeks"))
        print(leftmost_non_repeating("aaa"))
    ''', out='''
        5
        -1
    ''')
    yield note("This variant reads the string once, which matters when the string is a stream you cannot rewind. For plain strings the two-pass count is just as fast and easier to get right.")

    yield section("Problem: reverse the words in a string", "text-wrap")
    yield io("s = \"Welcome to gfg\"", "gfg to Welcome", "s = \"abc\"", "abc")
    yield p("Words are separated by single spaces; reverse their **order**, not the letters. The straightforward way splits into words, pushes them on a stack (or reverses the list) and joins — `O(n)` time but `O(n)` extra space for the words:")
    yield multi('''
        gfg to Welcome
        abc
    ''', py=r'''
        def reverse_words(s):
            stack = []
            for word in s.split():           # split on whitespace
                stack.append(word)
            out = []
            while stack:
                out.append(stack.pop())      # LIFO → last word comes out first
            return " ".join(out)             # idiom: " ".join(reversed(s.split()))

        print(reverse_words("Welcome to gfg"))
        print(reverse_words("abc"))
    ''', cpp=r'''
        #include <iostream>
        #include <sstream>
        #include <stack>
        #include <string>
        using namespace std;

        string reverseWords(const string& s) {
            istringstream in(s);
            stack<string> st;
            string word;
            while (in >> word) st.push(word);     // split on whitespace
            string out;
            while (!st.empty()) {
                if (!out.empty()) out += " ";
                out += st.top();                  // LIFO → last word comes out first
                st.pop();
            }
            return out;
        }

        int main() {
            cout << reverseWords("Welcome to gfg") << "\n";
            cout << reverseWords("abc") << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static String reverseWords(String s) {
                Deque<String> stack = new ArrayDeque<>();
                for (String word : s.split(" ")) stack.push(word);   // split on spaces
                StringBuilder out = new StringBuilder();
                while (!stack.isEmpty()) {
                    if (out.length() > 0) out.append(' ');
                    out.append(stack.pop());                           // LIFO → last word comes out first
                }
                return out.toString();
            }

            public static void main(String[] args) {
                System.out.println(reverseWords("Welcome to gfg"));
                System.out.println(reverseWords("abc"));
            }
        }
    ''', js=r'''
        function reverseWords(s) {
            const stack = [];
            for (const word of s.split(" ")) stack.push(word);   // split on spaces
            const out = [];
            while (stack.length) out.push(stack.pop());          // LIFO → last word comes out first
            return out.join(" ");                                // idiom: s.split(" ").reverse().join(" ")
        }

        console.log(reverseWords("Welcome to gfg"));
        console.log(reverseWords("abc"));
    ''')
    yield complexity("O(n)", "O(n)")
    yield idea("**`O(1)` auxiliary space:** reverse each word in place, then reverse the whole string. Reversing twice restores the letters inside each word while the words themselves end up in reverse order. It needs a *mutable* character sequence — a list in Python, `char[]` in Java, an array in JavaScript, the string itself in C++.")
    yield diagram('''
        Welcome to gfg      original
        emocleW ot gfg      step 1: reverse every word in place
        gfg to Welcome      step 2: reverse the whole string
    ''', "Two reversals: letters are flipped twice (back to normal), word order once")
    yield multi('''
        gfg to Welcome
        abc
    ''', py=r'''
        def reverse_range(chars, b, e):
            while b < e:
                chars[b], chars[e] = chars[e], chars[b]
                b += 1
                e -= 1

        def reverse_words(s):
            chars = list(s)                            # mutable copy — str is immutable
            n = len(chars)
            start = 0
            for i in range(n):
                if chars[i] == ' ':
                    reverse_range(chars, start, i - 1)   # step 1: reverse this word
                    start = i + 1
            reverse_range(chars, start, n - 1)           # the last word
            reverse_range(chars, 0, n - 1)               # step 2: reverse everything
            return "".join(chars)

        print(reverse_words("Welcome to gfg"))
        print(reverse_words("abc"))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <utility>
        using namespace std;

        void reverseRange(string& s, int b, int e) {
            while (b < e) swap(s[b++], s[e--]);
        }

        string reverseWords(string s) {               // std::string is mutable: work on the copy
            int n = s.size(), start = 0;
            for (int i = 0; i < n; i++) {
                if (s[i] == ' ') {
                    reverseRange(s, start, i - 1);    // step 1: reverse this word
                    start = i + 1;
                }
            }
            reverseRange(s, start, n - 1);            // the last word
            reverseRange(s, 0, n - 1);                // step 2: reverse everything
            return s;
        }

        int main() {
            cout << reverseWords("Welcome to gfg") << "\n";
            cout << reverseWords("abc") << "\n";
        }
    ''', java=r'''
        public class Main {
            static void reverseRange(char[] c, int b, int e) {
                while (b < e) { char t = c[b]; c[b] = c[e]; c[e] = t; b++; e--; }
            }

            static String reverseWords(String s) {
                char[] c = s.toCharArray();               // mutable copy — String is immutable
                int n = c.length, start = 0;
                for (int i = 0; i < n; i++) {
                    if (c[i] == ' ') {
                        reverseRange(c, start, i - 1);    // step 1: reverse this word
                        start = i + 1;
                    }
                }
                reverseRange(c, start, n - 1);            // the last word
                reverseRange(c, 0, n - 1);                // step 2: reverse everything
                return new String(c);
            }

            public static void main(String[] args) {
                System.out.println(reverseWords("Welcome to gfg"));
                System.out.println(reverseWords("abc"));
            }
        }
    ''', js=r'''
        function reverseRange(c, b, e) {
            while (b < e) { [c[b], c[e]] = [c[e], c[b]]; b++; e--; }
        }

        function reverseWords(s) {
            const c = s.split("");                        // mutable copy — string is immutable
            const n = c.length;
            let start = 0;
            for (let i = 0; i < n; i++) {
                if (c[i] === " ") {
                    reverseRange(c, start, i - 1);        // step 1: reverse this word
                    start = i + 1;
                }
            }
            reverseRange(c, start, n - 1);                // the last word
            reverseRange(c, 0, n - 1);                    // step 2: reverse everything
            return c.join("");
        }

        console.log(reverseWords("Welcome to gfg"));
        console.log(reverseWords("abc"));
    ''')
    yield complexity("O(n)", "O(1) extra (beyond the mutable copy that immutable languages force)")
    yield pitfall("Multiple consecutive spaces break the in-place version (it would produce empty “words” and keep every space). Normalise the input first, or use `split()` without an argument, which collapses runs of whitespace.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why are strings immutable in Python, Java and JavaScript?",
             "Safety and speed: an immutable string can be shared freely between threads and functions, cached (interned), and used as a dictionary / `HashMap` key because its hash can never change. The cost is that every edit allocates a new string — so builders (`join`, `StringBuilder`, arrays) exist for heavy editing. C++ chose the opposite trade-off: `std::string` is a mutable buffer you own.")
    yield qa("Why is building a string with `+=` in a loop considered O(n²)?",
             "Each `+=` on an immutable string copies the whole current result into a new object; copying 1, 2, 3, … n characters sums to `O(n²)`. Collect the pieces in a list and `''.join()` once (`O(n)`), or use `StringBuilder` in Java. CPython has an optimisation that often makes `+=` fast, but you should not rely on it.")
    yield qa("How do you check if two strings are anagrams in O(n)?",
             "Length check, then a frequency array indexed by character code: `+1` for every character of the first string, `-1` for the second; all counts must end at zero. For Unicode or when the alphabet is unknown, use a hash map of counts instead of a fixed 256-slot array.")
    yield qa("Substring vs subsequence?",
             "A **substring** is contiguous (`'BC'` in `'ABCD'`); a **subsequence** keeps order but may skip characters (`'AD'` in `'ABCD'`). Substring search is `find`/KMP; subsequence check is the two-pointer greedy walk.")
    yield qa("How do you check whether one string is a rotation of another?",
             "Same length and `s2 in s1 + s1`. Doubling `s1` lays every rotation out as a window of length `n`, so one substring search answers the question in `O(n)` with a linear-time matcher.")
    yield qa("Leftmost repeating character in one pass — how?",
             "Scan from the **right** with a `visited` array: whenever the current character was already visited (i.e. appears further right), record its index. The scan moves left, so the last recorded index is the leftmost repeating one. `O(n)` time, `O(CHAR)` space.")
