from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Searching, Sorting & Hashing"


@topic(G, "hashing", "Hashing", "hash")
def _():
    yield lead("A hash set or hash map answers **“have I seen this value?”** in `O(1)` on average. Almost every problem in this topic is an `O(n²)` double loop that collapses to `O(n)` once the inner loop is replaced by one hash lookup — and half of them use the same trick: **prefix sums stored in a hash map**.")
    yield define("Hashing (as a problem-solving tool)", "replacing *search* with *lookup*. Instead of scanning for a value, you keep every value you have met in a hash table and ask the table. Average `O(1)` per insert / lookup / delete, `O(n)` extra space, and no ordering.")

    yield section("The containers you will reach for", "box")
    yield table(
        ["Need", "Python", "C++", "Java", "JavaScript"],
        ["membership only", "`set`", "`unordered_set`", "`HashSet`", "`Set`"],
        ["key → value / count", "`dict`, `Counter`", "`unordered_map`", "`HashMap`", "`Map`"],
        ["insert / lookup / erase", "`O(1)` avg", "`O(1)` avg", "`O(1)` avg", "`O(1)` avg"],
        ["iteration order", "insertion order", "unspecified", "unspecified", "insertion order"],
    )
    yield warn("Iteration order over a hash container is **not** the same across languages (C++ and Java make no promise at all). When an answer is a *set of values*, sort it before printing — every solution below that prints several keys does exactly that.")
    yield p("Two questions decide the whole design of a hashing solution:")
    yield cards(
        ("What is the key?", "The raw value (`pair with sum`), a running prefix sum (`subarray with sum`), or a derived value such as `prefix(a) − prefix(b)` (`common span`).", "key"),
        ("What do I store with it?", "Nothing (a set), a **count** (frequency problems), or the **first index** where the key appeared (longest-subarray problems).", "database"),
    )

    yield section("The prefix-sum + hash map pattern", "bulb")
    yield p("Let `prefix[j] = arr[0] + … + arr[j]`. Then the sum of any subarray is a difference of two prefix sums:")
    yield formula("sum(arr[i..j]) = prefix[j] − prefix[i−1]")
    yield p("So *“is there a subarray ending at `j` with sum `S`?”* becomes *“did the value `prefix[j] − S` appear as an earlier prefix sum?”* — a single hash lookup instead of an inner loop over every start `i`.")
    yield diagram('''
        index   :   0    1    2    3    4    5    6
        arr     : [ 5,   8,  -4,  -4,   9,  -2,   2 ]
        prefix  : [ 5,  13,   9,   5,  14,  12,  14 ]
                    ↑              ↑
               prefix[0] = 5  prefix[3] = 5   →  arr[1..3] = 8 − 4 − 4 = 0   (length 3 − 0 = 3)
    ''', "Two equal prefix sums ⇒ the elements between them sum to 0")
    yield steps(
        ("Seed the map with `prefix = 0` at index `−1`", "The empty prefix. It makes a subarray that starts at index 0 fall out of the same formula instead of needing a special case."),
        ("Walk left to right, updating `prefix`", "One addition per element."),
        ("Look up `prefix − S`", "Found at index `k` ⇒ `arr[k+1..j]` sums to `S`. For *existence* answer immediately; for *longest* take `j − k`; for *count* add the stored count."),
        ("Insert `prefix` only if it is new", "Keeping the **first** index gives the longest subarray; a later duplicate would only shorten it."),
    )
    yield note("Four problems below are this one template with a different `S` or a different array: subarray with 0 sum (`S = 0`), longest subarray with given sum, longest subarray with equal 0s and 1s (map `0 → −1`, then `S = 0`) and longest common span of two binary arrays (use `a[i] − b[i]`, then `S = 0`).")

    # ── Intersection ───────────────────────────────────────────────────────────
    yield section("Intersection of two unsorted arrays", "arrows-join")
    yield io("a = [10, 15, 20, 5, 20], b = [30, 5, 30, 80]", "1", "a = [1, 2, 3, 2, 4, 5], b = [3, 4, 5, 6]", "3")
    yield p("Count the **distinct** values that appear in both arrays. Duplicates inside one array (the two `20`s, the two `30`s) are counted once.")
    yield p("Naive: for each element of `a`, skip it if it already appeared earlier in `a`, otherwise scan `b` for it. Two nested scans per element.")
    yield snippet("py", r'''
        def intersection_count(a, b):
            res = 0
            for i in range(len(a)):
                seen_before = False
                for j in range(i):              # did a[i] already appear in a[0..i-1]?
                    if a[j] == a[i]:
                        seen_before = True
                        break
                if seen_before:
                    continue
                for y in b:                     # is a[i] present in b?
                    if y == a[i]:
                        res += 1
                        break
            return res

        print(intersection_count([10, 15, 20, 5, 20], [30, 5, 30, 80]))
        print(intersection_count([1, 2, 3, 2, 4, 5], [3, 4, 5, 6]))
    ''', out="1\n3", caption="Python — naive")
    yield complexity("O(m · (m + n))", "O(1)")
    yield idea("Put the distinct elements of `a` into a set. Scan `b`: every element found in the set is a common value — count it and **remove it from the set**, so a repeated value in `b` cannot be counted twice. Each element is touched once.")
    yield multi('''
        1
        3
    ''', py=r'''
        def intersection_count(a, b):
            remaining = set(a)             # distinct elements of a
            count = 0
            for x in b:
                if x in remaining:         # common value — count it once …
                    count += 1
                    remaining.remove(x)    # … by removing it immediately
            return count

        print(intersection_count([10, 15, 20, 5, 20], [30, 5, 30, 80]))
        print(intersection_count([1, 2, 3, 2, 4, 5], [3, 4, 5, 6]))
    ''', cpp=r'''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        using namespace std;

        int intersectionCount(const vector<int>& a, const vector<int>& b) {
            unordered_set<int> remaining(a.begin(), a.end());   // distinct elements of a
            int count = 0;
            for (int x : b) {
                if (remaining.count(x)) {      // common value — count it once …
                    count++;
                    remaining.erase(x);        // … by removing it immediately
                }
            }
            return count;
        }

        int main() {
            cout << intersectionCount({10, 15, 20, 5, 20}, {30, 5, 30, 80}) << "\n";
            cout << intersectionCount({1, 2, 3, 2, 4, 5}, {3, 4, 5, 6}) << "\n";
        }
    ''', java=r'''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static int intersectionCount(int[] a, int[] b) {
                Set<Integer> remaining = new HashSet<>();     // distinct elements of a
                for (int x : a) remaining.add(x);
                int count = 0;
                for (int x : b) {
                    if (remaining.remove(x)) count++;        // remove() is true only if x was present
                }
                return count;
            }

            public static void main(String[] args) {
                System.out.println(intersectionCount(new int[]{10, 15, 20, 5, 20}, new int[]{30, 5, 30, 80}));
                System.out.println(intersectionCount(new int[]{1, 2, 3, 2, 4, 5}, new int[]{3, 4, 5, 6}));
            }
        }
    ''', js=r'''
        function intersectionCount(a, b) {
            const remaining = new Set(a);          // distinct elements of a
            let count = 0;
            for (const x of b) {
                if (remaining.delete(x)) count++;  // delete() is true only if x was present
            }
            return count;
        }

        console.log(intersectionCount([10, 15, 20, 5, 20], [30, 5, 30, 80]));
        console.log(intersectionCount([1, 2, 3, 2, 4, 5], [3, 4, 5, 6]));
    ''')
    yield complexity("O(m + n)", "O(m)")
    yield note("Building two sets and counting the elements of one that are in the other (`len(set(a) & set(b))` in Python) is the same `O(m + n)` idea; the remove-on-hit version needs only one set and no second pass.")

    # ── Union ──────────────────────────────────────────────────────────────────
    yield section("Union of two unsorted arrays", "circles")
    yield io("a = [15, 20, 5, 15], b = [15, 15, 15, 20, 10]", "4", "a = [1, 2, 3, 2, 4, 5], b = [3, 4, 5, 6]", "6")
    yield p("Count the distinct values present in at least one of the arrays. The naive way copies both into one array of `m + n` elements and, for each element, scans everything before it to see whether it is a repeat.")
    yield snippet("py", r'''
        def union_count(a, b):
            c = a + b                        # all m + n elements
            res = 0
            for i in range(len(c)):
                repeat = False
                for j in range(i):           # did c[i] already appear?
                    if c[j] == c[i]:
                        repeat = True
                        break
                if not repeat:
                    res += 1
            return res

        print(union_count([15, 20, 5, 15], [15, 15, 15, 20, 10]))
        print(union_count([1, 2, 3, 2, 4, 5], [3, 4, 5, 6]))
    ''', out="4\n6", caption="Python — naive")
    yield complexity("O((m + n)²)", "O(m + n)")
    yield idea("A set *is* a union with duplicates removed. Insert every element of both arrays and read off its size.")
    yield multi('''
        4
        6
    ''', py=r'''
        def union_count(a, b):
            s = set()
            for x in a:
                s.add(x)          # duplicates are silently ignored
            for x in b:
                s.add(x)
            return len(s)

        print(union_count([15, 20, 5, 15], [15, 15, 15, 20, 10]))
        print(union_count([1, 2, 3, 2, 4, 5], [3, 4, 5, 6]))
    ''', cpp=r'''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        using namespace std;

        int unionCount(const vector<int>& a, const vector<int>& b) {
            unordered_set<int> s;
            for (int x : a) s.insert(x);      // duplicates are silently ignored
            for (int x : b) s.insert(x);
            return (int)s.size();
        }

        int main() {
            cout << unionCount({15, 20, 5, 15}, {15, 15, 15, 20, 10}) << "\n";
            cout << unionCount({1, 2, 3, 2, 4, 5}, {3, 4, 5, 6}) << "\n";
        }
    ''', java=r'''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static int unionCount(int[] a, int[] b) {
                Set<Integer> s = new HashSet<>();
                for (int x : a) s.add(x);        // duplicates are silently ignored
                for (int x : b) s.add(x);
                return s.size();
            }

            public static void main(String[] args) {
                System.out.println(unionCount(new int[]{15, 20, 5, 15}, new int[]{15, 15, 15, 20, 10}));
                System.out.println(unionCount(new int[]{1, 2, 3, 2, 4, 5}, new int[]{3, 4, 5, 6}));
            }
        }
    ''', js=r'''
        function unionCount(a, b) {
            const s = new Set();
            for (const x of a) s.add(x);         // duplicates are silently ignored
            for (const x of b) s.add(x);
            return s.size;
        }

        console.log(unionCount([15, 20, 5, 15], [15, 15, 15, 20, 10]));
        console.log(unionCount([1, 2, 3, 2, 4, 5], [3, 4, 5, 6]));
    ''')
    yield complexity("O(m + n)", "O(m + n)")
    yield note("If the arrays were **sorted**, both union and intersection could be done with the two-pointer merge walk in `O(m + n)` time and `O(1)` space — the hash set is what buys you the same time on *unsorted* input.")

    # ── Pair with given sum ────────────────────────────────────────────────────
    yield section("Pair with given sum", "plus")
    yield io("arr = [3, 2, 8, 15, -18], sum = 17", "Yes  (2 + 15)", "arr = [2, 1, 6, 3], sum = 6", "No")
    yield p("Does the array contain two *different* elements whose sum is `x`? The naive check tries every pair.")
    yield snippet("py", r'''
        def has_pair(arr, x):
            n = len(arr)
            for i in range(n):
                for j in range(i + 1, n):
                    if arr[i] + arr[j] == x:
                        return True
            return False

        print("Yes" if has_pair([3, 2, 8, 15, -18], 17) else "No")
        print("Yes" if has_pair([2, 1, 6, 3], 6) else "No")
    ''', out="Yes\nNo", caption="Python — naive")
    yield complexity("O(n²)", "O(1)")
    yield idea("Walk the array once. Before inserting `arr[i]`, ask the set whether its **complement** `x − arr[i]` has already been seen. Checking *before* inserting guarantees the two elements are at different positions — `[3]` with `x = 6` correctly answers `No`.")
    yield multi('''
        sum = 17 → Yes
        sum = 6 → No
        sum = 6 → No
    ''', py=r'''
        def has_pair(arr, x):
            seen = set()
            for v in arr:
                if x - v in seen:       # complement met earlier → pair found
                    return True
                seen.add(v)             # insert AFTER the check
            return False

        for arr, x in [([3, 2, 8, 15, -18], 17), ([2, 1, 6, 3], 6), ([3], 6)]:
            print("sum =", x, "→", "Yes" if has_pair(arr, x) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        using namespace std;

        bool hasPair(const vector<int>& arr, int x) {
            unordered_set<int> seen;
            for (int v : arr) {
                if (seen.count(x - v)) return true;   // complement met earlier → pair found
                seen.insert(v);                       // insert AFTER the check
            }
            return false;
        }

        int main() {
            vector<pair<vector<int>, int>> tests = {{{3, 2, 8, 15, -18}, 17}, {{2, 1, 6, 3}, 6}, {{3}, 6}};
            for (auto& [arr, x] : tests)
                cout << "sum = " << x << " → " << (hasPair(arr, x) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static boolean hasPair(int[] arr, int x) {
                Set<Integer> seen = new HashSet<>();
                for (int v : arr) {
                    if (seen.contains(x - v)) return true;   // complement met earlier → pair found
                    seen.add(v);                             // insert AFTER the check
                }
                return false;
            }

            public static void main(String[] args) {
                int[][] arrays = {{3, 2, 8, 15, -18}, {2, 1, 6, 3}, {3}};
                int[] sums = {17, 6, 6};
                for (int t = 0; t < arrays.length; t++)
                    System.out.println("sum = " + sums[t] + " → " + (hasPair(arrays[t], sums[t]) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function hasPair(arr, x) {
            const seen = new Set();
            for (const v of arr) {
                if (seen.has(x - v)) return true;   // complement met earlier → pair found
                seen.add(v);                        // insert AFTER the check
            }
            return false;
        }

        for (const [arr, x] of [[[3, 2, 8, 15, -18], 17], [[2, 1, 6, 3], 6], [[3], 6]])
            console.log("sum =", x, "→", hasPair(arr, x) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("Inserting all elements first and *then* asking `x − v in set` for each `v` accepts an element paired with itself (`[3]`, `x = 6` → wrong `Yes`). Insert after the lookup, or store counts and demand two copies when `x − v == v`.")

    # ── Subarray with 0 sum ────────────────────────────────────────────────────
    yield section("Subarray with 0 sum", "equal")
    yield io("arr = [1, 2, 3, 2, 4, 5]", "No", "arr = [-1, 4, -3, 5, 1]", "Yes  (4 − 3 − 1 = 0 … [-1, 4, -3])", "arr = [4, -3, -1, 2]", "Yes")
    yield p("Is there a contiguous subarray whose elements sum to zero? The naive solution computes the sum of every `(i, j)` range.")
    yield snippet("py", r'''
        def has_zero_sum(arr):
            n = len(arr)
            for i in range(n):
                s = 0
                for j in range(i, n):      # extend the subarray one element at a time
                    s += arr[j]
                    if s == 0:
                        return True
            return False

        print("Yes" if has_zero_sum([1, 2, 3, 2, 4, 5]) else "No")
        print("Yes" if has_zero_sum([-1, 4, -3, 5, 1]) else "No")
    ''', out="No\nYes", caption="Python — naive")
    yield complexity("O(n²)", "O(1)")
    yield idea("First use of the prefix-sum pattern. A zero-sum subarray `arr[i..j]` exists exactly when two prefix sums are equal, `prefix[i−1] == prefix[j]` — or when some `prefix[j]` is itself `0` (the subarray starts at index 0). Keep every prefix sum in a set; the first repeat (or a `0`) is the answer.")
    yield diagram('''
        arr    : [ -1,  4, -3,  5,  1 ]
        prefix : [ -1,  3,  0,  5,  6 ]
                             ↑
                       prefix[2] = 0  →  arr[0..2] sums to 0  →  Yes
    ''', "Prefix sums of the second example")
    yield multi('''
        No
        Yes
        Yes
    ''', py=r'''
        def has_zero_sum(arr):
            seen = {0}            # the empty prefix: lets a subarray start at index 0
            prefix = 0
            for v in arr:
                prefix += v
                if prefix in seen:    # same prefix twice → the gap sums to 0
                    return True
                seen.add(prefix)
            return False

        for arr in [[1, 2, 3, 2, 4, 5], [-1, 4, -3, 5, 1], [4, -3, -1, 2]]:
            print("Yes" if has_zero_sum(arr) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        using namespace std;

        bool hasZeroSum(const vector<int>& arr) {
            unordered_set<int> seen = {0};     // the empty prefix: lets a subarray start at index 0
            int prefix = 0;
            for (int v : arr) {
                prefix += v;
                if (seen.count(prefix)) return true;   // same prefix twice → the gap sums to 0
                seen.insert(prefix);
            }
            return false;
        }

        int main() {
            vector<vector<int>> tests = {{1, 2, 3, 2, 4, 5}, {-1, 4, -3, 5, 1}, {4, -3, -1, 2}};
            for (auto& arr : tests) cout << (hasZeroSum(arr) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static boolean hasZeroSum(int[] arr) {
                Set<Integer> seen = new HashSet<>();
                seen.add(0);                       // the empty prefix: lets a subarray start at index 0
                int prefix = 0;
                for (int v : arr) {
                    prefix += v;
                    if (!seen.add(prefix)) return true;   // add() is false when prefix was already there
                }
                return false;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 2, 3, 2, 4, 5}, {-1, 4, -3, 5, 1}, {4, -3, -1, 2}};
                for (int[] arr : tests) System.out.println(hasZeroSum(arr) ? "Yes" : "No");
            }
        }
    ''', js=r'''
        function hasZeroSum(arr) {
            const seen = new Set([0]);      // the empty prefix: lets a subarray start at index 0
            let prefix = 0;
            for (const v of arr) {
                prefix += v;
                if (seen.has(prefix)) return true;   // same prefix twice → the gap sums to 0
                seen.add(prefix);
            }
            return false;
        }

        for (const arr of [[1, 2, 3, 2, 4, 5], [-1, 4, -3, 5, 1], [4, -3, -1, 2]])
            console.log(hasZeroSum(arr) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n)")
    yield note("**Subarray with a given sum `S`** is the same code with `prefix − S` looked up instead of `prefix`. Seeding the set with `0` is what replaces the separate `if prefix == 0` test of the original notes.")

    # ── Palindrome permutation ────────────────────────────────────────────────
    yield section("Check for palindrome permutation", "letter-case")
    yield io("s = \"geek\"", "No", "s = \"geegg\"", "Yes  (gegeg, eggge, …)", "s = \"aab\"", "Yes  (aba)")
    yield p("Can the characters of `s` be rearranged into a palindrome? Generating every permutation and testing each one is hopeless beyond a handful of characters — `n!` candidates.")
    yield snippet("py", r'''
        from itertools import permutations

        def can_be_palindrome(s):
            for perm in permutations(s):           # n! permutations
                t = ''.join(perm)
                if t == t[::-1]:
                    return True
            return False

        print("Yes" if can_be_palindrome("geek") else "No")
        print("Yes" if can_be_palindrome("geegg") else "No")
    ''', out="No\nYes", caption="Python — naive")
    yield complexity("O(n! · n)", "O(n)")
    yield idea("A palindrome pairs every character with its mirror, so each character must occur an **even** number of times — except the single middle character of an odd-length string. Count frequencies in a hash map; the answer is `Yes` iff **at most one** count is odd. (Even length ⇒ zero odd counts; odd length ⇒ exactly one — “at most one” covers both.)")
    yield multi('''
        geek → No
        geegg → Yes
        aab → Yes
        abc → No
    ''', py=r'''
        def can_be_palindrome(s):
            freq = {}
            for ch in s:
                freq[ch] = freq.get(ch, 0) + 1
            odd = 0
            for count in freq.values():
                if count % 2 == 1:
                    odd += 1
                    if odd > 1:          # two characters without a partner
                        return False
            return True

        for s in ["geek", "geegg", "aab", "abc"]:
            print(s, "→", "Yes" if can_be_palindrome(s) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <unordered_map>
        using namespace std;

        bool canBePalindrome(const string& s) {
            unordered_map<char, int> freq;
            for (char ch : s) freq[ch]++;
            int odd = 0;
            for (auto& [ch, count] : freq) {
                if (count % 2 == 1 && ++odd > 1) return false;   // two characters without a partner
            }
            return true;
        }

        int main() {
            for (string s : {"geek", "geegg", "aab", "abc"})
                cout << s << " → " << (canBePalindrome(s) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        import java.util.HashMap;
        import java.util.Map;

        public class Main {
            static boolean canBePalindrome(String s) {
                Map<Character, Integer> freq = new HashMap<>();
                for (char ch : s.toCharArray()) freq.merge(ch, 1, Integer::sum);
                int odd = 0;
                for (int count : freq.values()) {
                    if (count % 2 == 1 && ++odd > 1) return false;   // two characters without a partner
                }
                return true;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"geek", "geegg", "aab", "abc"})
                    System.out.println(s + " → " + (canBePalindrome(s) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function canBePalindrome(s) {
            const freq = new Map();
            for (const ch of s) freq.set(ch, (freq.get(ch) ?? 0) + 1);
            let odd = 0;
            for (const count of freq.values()) {
                if (count % 2 === 1 && ++odd > 1) return false;   // two characters without a partner
            }
            return true;
        }

        for (const s of ["geek", "geegg", "aab", "abc"])
            console.log(s, "→", canBePalindrome(s) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(k) for k distinct characters")
    yield note("For a fixed alphabet a 26- or 256-slot array beats the hash map; for an unbounded alphabet (Unicode) the map is the right tool. A bit-twiddling variant toggles bit `c` in an integer mask and checks `mask & (mask − 1) == 0` at the end.")

    # ── Longest subarray with given sum ───────────────────────────────────────
    yield section("Longest subarray with given sum", "arrows-horizontal")
    yield io("arr = [5, 8, -4, -4, 9, -2, 2], sum = 0", "3  ([8, -4, -4])", "arr = [3, 1, 0, 1, 8, 2, 3, 6], sum = 5", "4  ([3, 1, 0, 1])", "arr = [8, 3, 7], sum = 15", "0")
    yield p("Return the length of the longest contiguous subarray whose sum is exactly `S` (`0` if none). Naive: start at every `i`, extend to every `j`, keep the longest hit.")
    yield snippet("py", r'''
        def longest_with_sum(arr, S):
            n, res = len(arr), 0
            for i in range(n):
                s = 0
                for j in range(i, n):
                    s += arr[j]
                    if s == S:
                        res = max(res, j - i + 1)
            return res

        print(longest_with_sum([5, 8, -4, -4, 9, -2, 2], 0))
        print(longest_with_sum([3, 1, 0, 1, 8, 2, 3, 6], 5))
    ''', out="3\n4", caption="Python — naive")
    yield complexity("O(n²)", "O(1)")
    yield idea("Prefix-sum pattern, *longest* flavour. At index `j`, if `prefix[j] − S` was first seen at index `k`, then `arr[k+1..j]` sums to `S` and has length `j − k`. Store each prefix sum with the **first** index it appeared at and never overwrite it — the earliest start gives the longest subarray. Seeding the map with `0 → −1` handles subarrays that start at index 0 (`prefix[j] == S` gives length `j + 1`).")
    yield multi('''
        3
        4
        0
    ''', py=r'''
        def longest_with_sum(arr, S):
            first = {0: -1}            # prefix sum → first index where it occurred
            prefix = 0
            best = 0
            for j, v in enumerate(arr):
                prefix += v
                if prefix - S in first:                 # subarray (first[prefix-S], j] sums to S
                    best = max(best, j - first[prefix - S])
                if prefix not in first:                 # keep the FIRST occurrence only
                    first[prefix] = j
            return best

        print(longest_with_sum([5, 8, -4, -4, 9, -2, 2], 0))
        print(longest_with_sum([3, 1, 0, 1, 8, 2, 3, 6], 5))
        print(longest_with_sum([8, 3, 7], 15))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        int longestWithSum(const vector<int>& arr, int S) {
            unordered_map<int, int> first = {{0, -1}};   // prefix sum → first index where it occurred
            int prefix = 0, best = 0;
            int n = arr.size();
            for (int j = 0; j < n; j++) {
                prefix += arr[j];
                auto it = first.find(prefix - S);
                if (it != first.end()) best = max(best, j - it->second);   // subarray (it->second, j] sums to S
                first.try_emplace(prefix, j);            // inserts only if absent → keeps the FIRST occurrence
            }
            return best;
        }

        int main() {
            cout << longestWithSum({5, 8, -4, -4, 9, -2, 2}, 0) << "\n";
            cout << longestWithSum({3, 1, 0, 1, 8, 2, 3, 6}, 5) << "\n";
            cout << longestWithSum({8, 3, 7}, 15) << "\n";
        }
    ''', java=r'''
        import java.util.HashMap;
        import java.util.Map;

        public class Main {
            static int longestWithSum(int[] arr, int S) {
                Map<Integer, Integer> first = new HashMap<>();   // prefix sum → first index where it occurred
                first.put(0, -1);
                int prefix = 0, best = 0;
                for (int j = 0; j < arr.length; j++) {
                    prefix += arr[j];
                    Integer k = first.get(prefix - S);
                    if (k != null) best = Math.max(best, j - k);   // subarray (k, j] sums to S
                    first.putIfAbsent(prefix, j);                  // keeps the FIRST occurrence
                }
                return best;
            }

            public static void main(String[] args) {
                System.out.println(longestWithSum(new int[]{5, 8, -4, -4, 9, -2, 2}, 0));
                System.out.println(longestWithSum(new int[]{3, 1, 0, 1, 8, 2, 3, 6}, 5));
                System.out.println(longestWithSum(new int[]{8, 3, 7}, 15));
            }
        }
    ''', js=r'''
        function longestWithSum(arr, S) {
            const first = new Map([[0, -1]]);     // prefix sum → first index where it occurred
            let prefix = 0, best = 0;
            for (let j = 0; j < arr.length; j++) {
                prefix += arr[j];
                if (first.has(prefix - S)) best = Math.max(best, j - first.get(prefix - S));  // (k, j] sums to S
                if (!first.has(prefix)) first.set(prefix, j);   // keeps the FIRST occurrence
            }
            return best;
        }

        console.log(longestWithSum([5, 8, -4, -4, 9, -2, 2], 0));
        console.log(longestWithSum([3, 1, 0, 1, 8, 2, 3, 6], 5));
        console.log(longestWithSum([8, 3, 7], 15));
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("Overwriting `first[prefix]` on every occurrence (or using `first[prefix] = j` unconditionally) gives the **shortest** subarray, not the longest. Also, the two-pointer sliding window only works for arrays without negative numbers — this array has them, so the hash map is required.")

    # ── Equal 0s and 1s ───────────────────────────────────────────────────────
    yield section("Longest subarray with equal 0s and 1s", "binary")
    yield io("arr = [1, 0, 0, 1, 0, 1, 1]", "6  ([1, 0, 0, 1, 0, 1] or [0, 0, 1, 0, 1, 1])", "arr = [1, 1, 1, 0]", "2", "arr = [0, 0, 1, 1, 0]", "4")
    yield p("In a binary array, find the longest contiguous subarray with as many `0`s as `1`s. The naive version tracks a running `+1 / −1` score from each start.")
    yield snippet("py", r'''
        def longest_equal(arr):
            n, best, start = len(arr), 0, -1
            for i in range(n):
                score = 0
                for j in range(i, n):
                    score += 1 if arr[j] == 1 else -1
                    if score == 0 and j - i + 1 > best:
                        best, start = j - i + 1, i
            if best:
                print("indices", start, "to", start + best - 1)
            return best

        print(longest_equal([1, 0, 0, 1, 0, 1, 1]))
    ''', out="indices 0 to 5\n6", caption="Python — naive")
    yield complexity("O(n²)", "O(1)")
    yield idea("Treat every `0` as `−1`. A subarray with equal 0s and 1s is then exactly a subarray with **sum 0** — the previous problem with `S = 0`. Only the first index of each prefix sum is kept.")
    yield multi('''
        6
        2
        4
    ''', py=r'''
        def longest_equal(arr):
            first = {0: -1}
            prefix = 0
            best = 0
            for j, bit in enumerate(arr):
                prefix += 1 if bit == 1 else -1      # 0 counts as -1 (the input is not modified)
                if prefix in first:
                    best = max(best, j - first[prefix])
                else:
                    first[prefix] = j
            return best

        for arr in [[1, 0, 0, 1, 0, 1, 1], [1, 1, 1, 0], [0, 0, 1, 1, 0]]:
            print(longest_equal(arr))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        int longestEqual(const vector<int>& arr) {
            unordered_map<int, int> first = {{0, -1}};
            int prefix = 0, best = 0;
            int n = arr.size();
            for (int j = 0; j < n; j++) {
                prefix += arr[j] == 1 ? 1 : -1;        // 0 counts as -1 (the input is not modified)
                auto it = first.find(prefix);
                if (it != first.end()) best = max(best, j - it->second);
                else first[prefix] = j;
            }
            return best;
        }

        int main() {
            vector<vector<int>> tests = {{1, 0, 0, 1, 0, 1, 1}, {1, 1, 1, 0}, {0, 0, 1, 1, 0}};
            for (auto& arr : tests) cout << longestEqual(arr) << "\n";
        }
    ''', java=r'''
        import java.util.HashMap;
        import java.util.Map;

        public class Main {
            static int longestEqual(int[] arr) {
                Map<Integer, Integer> first = new HashMap<>();
                first.put(0, -1);
                int prefix = 0, best = 0;
                for (int j = 0; j < arr.length; j++) {
                    prefix += arr[j] == 1 ? 1 : -1;    // 0 counts as -1 (the input is not modified)
                    Integer k = first.get(prefix);
                    if (k != null) best = Math.max(best, j - k);
                    else first.put(prefix, j);
                }
                return best;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 0, 0, 1, 0, 1, 1}, {1, 1, 1, 0}, {0, 0, 1, 1, 0}};
                for (int[] arr : tests) System.out.println(longestEqual(arr));
            }
        }
    ''', js=r'''
        function longestEqual(arr) {
            const first = new Map([[0, -1]]);
            let prefix = 0, best = 0;
            for (let j = 0; j < arr.length; j++) {
                prefix += arr[j] === 1 ? 1 : -1;       // 0 counts as -1 (the input is not modified)
                if (first.has(prefix)) best = Math.max(best, j - first.get(prefix));
                else first.set(prefix, j);
            }
            return best;
        }

        for (const arr of [[1, 0, 0, 1, 0, 1, 1], [1, 1, 1, 0], [0, 0, 1, 1, 0]])
            console.log(longestEqual(arr));
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("The original notes overwrote the input (`arr[i] = -1`) before scanning. Compute the `±1` on the fly instead — callers rarely expect their array to come back changed, and the test harness that prints the input afterwards will expose it.")

    # ── Common span ───────────────────────────────────────────────────────────
    yield section("Longest common span with same sum in two binary arrays", "arrows-split")
    yield io("a = [0, 1, 0, 0, 0, 0], b = [1, 0, 1, 0, 0, 1]", "4  (a[1..4] and b[1..4] both sum to 1)", "a = [0, 0, 0], b = [1, 1, 1]", "0", "a = [0, 0, 1, 0], b = [1, 1, 1, 1]", "1")
    yield p("Two binary arrays of the same length. Find the longest index range `[i..j]` such that `a[i..j]` and `b[i..j]` have the same sum. Naive: for every start, extend both running sums together.")
    yield snippet("py", r'''
        def longest_common_span(a, b):
            n, res = len(a), 0
            for i in range(n):
                sum_a = sum_b = 0
                for j in range(i, n):
                    sum_a += a[j]
                    sum_b += b[j]
                    if sum_a == sum_b:
                        res = max(res, j - i + 1)
            return res

        print(longest_common_span([0, 1, 0, 0, 0, 0], [1, 0, 1, 0, 0, 1]))
        print(longest_common_span([0, 0, 0], [1, 1, 1]))
    ''', out="4\n0", caption="Python — naive")
    yield complexity("O(n²)", "O(1)")
    yield idea("`sum(a[i..j]) == sum(b[i..j])` ⟺ `sum((a − b)[i..j]) == 0`. So build the difference `d[i] = a[i] − b[i]` (values `−1`, `0`, `1`) and find the **longest subarray with sum 0** in it — the same prefix-sum code again.")
    yield diagram('''
        a      : [ 0,  1,  0,  0,  0,  0 ]
        b      : [ 1,  0,  1,  0,  0,  1 ]
        a − b  : [-1,  1, -1,  0,  0, -1 ]
        prefix : [-1,  0, -1, -1, -1, -2 ]
                   ↑               ↑
             first(-1) = 0      j = 4   →  length 4 − 0 = 4
    ''', "Equal prefix sums of a − b at indices 0 and 4 ⇒ a[1..4] and b[1..4] have equal sums")
    yield multi('''
        4
        0
        1
    ''', py=r'''
        def longest_common_span(a, b):
            first = {0: -1}
            prefix = 0
            best = 0
            for j in range(len(a)):
                prefix += a[j] - b[j]         # prefix sum of the difference array
                if prefix in first:
                    best = max(best, j - first[prefix])
                else:
                    first[prefix] = j
            return best

        print(longest_common_span([0, 1, 0, 0, 0, 0], [1, 0, 1, 0, 0, 1]))
        print(longest_common_span([0, 0, 0], [1, 1, 1]))
        print(longest_common_span([0, 0, 1, 0], [1, 1, 1, 1]))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        int longestCommonSpan(const vector<int>& a, const vector<int>& b) {
            unordered_map<int, int> first = {{0, -1}};
            int prefix = 0, best = 0;
            int n = a.size();
            for (int j = 0; j < n; j++) {
                prefix += a[j] - b[j];               // prefix sum of the difference array
                auto it = first.find(prefix);
                if (it != first.end()) best = max(best, j - it->second);
                else first[prefix] = j;
            }
            return best;
        }

        int main() {
            cout << longestCommonSpan({0, 1, 0, 0, 0, 0}, {1, 0, 1, 0, 0, 1}) << "\n";
            cout << longestCommonSpan({0, 0, 0}, {1, 1, 1}) << "\n";
            cout << longestCommonSpan({0, 0, 1, 0}, {1, 1, 1, 1}) << "\n";
        }
    ''', java=r'''
        import java.util.HashMap;
        import java.util.Map;

        public class Main {
            static int longestCommonSpan(int[] a, int[] b) {
                Map<Integer, Integer> first = new HashMap<>();
                first.put(0, -1);
                int prefix = 0, best = 0;
                for (int j = 0; j < a.length; j++) {
                    prefix += a[j] - b[j];           // prefix sum of the difference array
                    Integer k = first.get(prefix);
                    if (k != null) best = Math.max(best, j - k);
                    else first.put(prefix, j);
                }
                return best;
            }

            public static void main(String[] args) {
                System.out.println(longestCommonSpan(new int[]{0, 1, 0, 0, 0, 0}, new int[]{1, 0, 1, 0, 0, 1}));
                System.out.println(longestCommonSpan(new int[]{0, 0, 0}, new int[]{1, 1, 1}));
                System.out.println(longestCommonSpan(new int[]{0, 0, 1, 0}, new int[]{1, 1, 1, 1}));
            }
        }
    ''', js=r'''
        function longestCommonSpan(a, b) {
            const first = new Map([[0, -1]]);
            let prefix = 0, best = 0;
            for (let j = 0; j < a.length; j++) {
                prefix += a[j] - b[j];               // prefix sum of the difference array
                if (first.has(prefix)) best = Math.max(best, j - first.get(prefix));
                else first.set(prefix, j);
            }
            return best;
        }

        console.log(longestCommonSpan([0, 1, 0, 0, 0, 0], [1, 0, 1, 0, 0, 1]));
        console.log(longestCommonSpan([0, 0, 0], [1, 1, 1]));
        console.log(longestCommonSpan([0, 0, 1, 0], [1, 1, 1, 1]));
    ''')
    yield complexity("O(n)", "O(n)")
    yield note("The difference array has only `2n + 1` possible prefix values (`−n … n`), so an array indexed by `prefix + n` can replace the hash map here — same `O(n)` but no hashing at all. Nothing in the method needs the arrays to be binary; it works for any two integer arrays.")

    # ── Longest consecutive subsequence ──────────────────────────────────────
    yield section("Longest consecutive subsequence", "list-numbers")
    yield io("arr = [1, 9, 3, 4, 2, 20]", "4  (1, 2, 3, 4)", "arr = [8, 20, 7, 30]", "2  (7, 8)", "arr = [20, 30, 40]", "1")
    yield p("Find the length of the longest run of consecutive integers `x, x+1, x+2, …` whose members all appear in the array — in any order and possibly with duplicates. Sorting makes runs adjacent, which gives an `O(n log n)` solution.")
    yield snippet("py", r'''
        def longest_consecutive(arr):
            arr = sorted(arr)
            best = run = 1
            for i in range(1, len(arr)):
                if arr[i] == arr[i - 1]:          # duplicate: neither extends nor breaks the run
                    continue
                if arr[i] == arr[i - 1] + 1:
                    run += 1
                else:
                    best = max(best, run)
                    run = 1
            return max(best, run)

        print(longest_consecutive([1, 9, 3, 4, 2, 20]))
        print(longest_consecutive([1, 2, 2, 3]))      # the original notes' version returned 2 here
    ''', out="4\n3", caption="Python — sorting")
    yield complexity("O(n log n)", "O(n) for the sorted copy")
    yield idea("Put everything in a set. A run `x, x+1, …` can only be *counted from its start*, and `x` is a start exactly when `x − 1` is **not** in the set. For each start, walk upward while `x + k` is present. Every element is reached by at most one such walk, so the total work is `O(n)` even though there is a nested `while`.")
    yield multi('''
        4
        2
        1
    ''', py=r'''
        def longest_consecutive(arr):
            s = set(arr)
            best = 0
            for x in s:                      # iterate the set: duplicates handled for free
                if x - 1 in s:
                    continue                 # not the start of a run
                run = 1
                while x + run in s:          # walk the run upward
                    run += 1
                best = max(best, run)
            return best

        for arr in [[1, 9, 3, 4, 2, 20], [8, 20, 7, 30], [20, 30, 40]]:
            print(longest_consecutive(arr))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <unordered_set>
        #include <vector>
        using namespace std;

        int longestConsecutive(const vector<int>& arr) {
            unordered_set<int> s(arr.begin(), arr.end());
            int best = 0;
            for (int x : s) {                       // iterate the set: duplicates handled for free
                if (s.count(x - 1)) continue;       // not the start of a run
                int run = 1;
                while (s.count(x + run)) run++;     // walk the run upward
                best = max(best, run);
            }
            return best;
        }

        int main() {
            vector<vector<int>> tests = {{1, 9, 3, 4, 2, 20}, {8, 20, 7, 30}, {20, 30, 40}};
            for (auto& arr : tests) cout << longestConsecutive(arr) << "\n";
        }
    ''', java=r'''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static int longestConsecutive(int[] arr) {
                Set<Integer> s = new HashSet<>();
                for (int x : arr) s.add(x);
                int best = 0;
                for (int x : s) {                            // iterate the set: duplicates handled for free
                    if (s.contains(x - 1)) continue;         // not the start of a run
                    int run = 1;
                    while (s.contains(x + run)) run++;       // walk the run upward
                    best = Math.max(best, run);
                }
                return best;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 9, 3, 4, 2, 20}, {8, 20, 7, 30}, {20, 30, 40}};
                for (int[] arr : tests) System.out.println(longestConsecutive(arr));
            }
        }
    ''', js=r'''
        function longestConsecutive(arr) {
            const s = new Set(arr);
            let best = 0;
            for (const x of s) {                     // iterate the set: duplicates handled for free
                if (s.has(x - 1)) continue;          // not the start of a run
                let run = 1;
                while (s.has(x + run)) run++;        // walk the run upward
                best = Math.max(best, run);
            }
            return best;
        }

        for (const arr of [[1, 9, 3, 4, 2, 20], [8, 20, 7, 30], [20, 30, 40]])
            console.log(longestConsecutive(arr));
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("Without the `x − 1 not in set` test the inner `while` restarts from every element of a run and the algorithm degrades to `O(n²)` on `[1, 2, 3, …, n]`. The check is what makes each run be walked exactly once.")

    # ── Distinct in every window ─────────────────────────────────────────────
    yield section("Count distinct elements in every window", "layout-columns")
    yield io("arr = [10, 20, 20, 10, 30, 40, 10], k = 4", "2 3 4 3", "arr = [10, 20, 30, 40], k = 3", "3 3")
    yield p("For each of the `n − k + 1` windows of size `k`, print the number of distinct values in it. The naive solution rebuilds a set for every window.")
    yield snippet("py", r'''
        def distinct_in_windows(arr, k):
            n = len(arr)
            return [len(set(arr[i:i + k])) for i in range(n - k + 1)]   # n-k+1 windows, O(k) each

        print(*distinct_in_windows([10, 20, 20, 10, 30, 40, 10], 4))
        print(*distinct_in_windows([10, 20, 30, 40], 3))
    ''', out="2 3 4 3\n3 3", caption="Python — naive")
    yield complexity("O(n · k)", "O(k)")
    yield idea("Consecutive windows differ by one element on each side. Keep a **count map** of the current window: when the window slides, decrement the outgoing element (delete the key when its count hits 0) and increment the incoming one. The number of keys in the map is the answer for that window — maintained in `O(1)` per slide.")
    yield diagram('''
        arr = [10, 20, 20, 10, 30, 40, 10],  k = 4

        window [10 20 20 10]   counts {10:2, 20:2}            → 2
        slide:  −10  +30       counts {10:1, 20:2, 30:1}      → 3
        slide:  −20  +40       counts {10:1, 20:1, 30:1, 40:1}→ 4
        slide:  −20  +10       counts {10:2, 30:1, 40:1}      → 3   (20 dropped to 0 → key removed)
    ''', "Each slide changes two counts; the map size is the answer")
    yield multi('''
        2 3 4 3
        3 3
    ''', py=r'''
        def distinct_in_windows(arr, k):
            count = {}
            for x in arr[:k]:                      # first window
                count[x] = count.get(x, 0) + 1
            res = [len(count)]
            for i in range(k, len(arr)):
                out, inc = arr[i - k], arr[i]
                count[out] -= 1
                if count[out] == 0:
                    del count[out]                 # a key with count 0 must not stay in the map
                count[inc] = count.get(inc, 0) + 1
                res.append(len(count))
            return res

        print(" ".join(map(str, distinct_in_windows([10, 20, 20, 10, 30, 40, 10], 4))))
        print(" ".join(map(str, distinct_in_windows([10, 20, 30, 40], 3))))
    ''', cpp=r'''
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        vector<int> distinctInWindows(const vector<int>& arr, int k) {
            unordered_map<int, int> count;
            int n = arr.size();
            for (int i = 0; i < k; i++) count[arr[i]]++;        // first window
            vector<int> res = {(int)count.size()};
            for (int i = k; i < n; i++) {
                int out = arr[i - k];
                if (--count[out] == 0) count.erase(out);        // a key with count 0 must not stay in the map
                count[arr[i]]++;
                res.push_back((int)count.size());
            }
            return res;
        }

        void print(const vector<int>& v) {
            for (size_t i = 0; i < v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\n";
        }

        int main() {
            print(distinctInWindows({10, 20, 20, 10, 30, 40, 10}, 4));
            print(distinctInWindows({10, 20, 30, 40}, 3));
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.HashMap;
        import java.util.List;
        import java.util.Map;

        public class Main {
            static List<Integer> distinctInWindows(int[] arr, int k) {
                Map<Integer, Integer> count = new HashMap<>();
                for (int i = 0; i < k; i++) count.merge(arr[i], 1, Integer::sum);   // first window
                List<Integer> res = new ArrayList<>();
                res.add(count.size());
                for (int i = k; i < arr.length; i++) {
                    int out = arr[i - k];
                    if (count.merge(out, -1, Integer::sum) == 0) count.remove(out);  // count 0 → remove the key
                    count.merge(arr[i], 1, Integer::sum);
                    res.add(count.size());
                }
                return res;
            }

            static void print(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                print(distinctInWindows(new int[]{10, 20, 20, 10, 30, 40, 10}, 4));
                print(distinctInWindows(new int[]{10, 20, 30, 40}, 3));
            }
        }
    ''', js=r'''
        function distinctInWindows(arr, k) {
            const count = new Map();
            for (let i = 0; i < k; i++) count.set(arr[i], (count.get(arr[i]) ?? 0) + 1);   // first window
            const res = [count.size];
            for (let i = k; i < arr.length; i++) {
                const out = arr[i - k];
                if (count.get(out) === 1) count.delete(out);        // a key with count 0 must not stay in the map
                else count.set(out, count.get(out) - 1);
                count.set(arr[i], (count.get(arr[i]) ?? 0) + 1);
                res.push(count.size);
            }
            return res;
        }

        console.log(distinctInWindows([10, 20, 20, 10, 30, 40, 10], 4).join(" "));
        console.log(distinctInWindows([10, 20, 30, 40], 3).join(" "));
    ''')
    yield complexity("O(n)", "O(k)")
    yield pitfall("Forgetting to **delete** a key whose count reached 0 makes `len(count)` too large — the map still “remembers” a value that left the window. Python's `Counter` has the same trap: `c[x] -= 1` leaves a zero entry behind.")

    # ── More than n/k ─────────────────────────────────────────────────────────
    yield section("Elements appearing more than n/k times", "chart-bar")
    yield io("arr = [30, 10, 20, 20, 10, 20, 30, 30], k = 4", "20 30  (n/k = 2; 20 and 30 appear 3 times)", "arr = [2, 2, 1, 2, 3, 2], k = 2", "2  (the majority element)")
    yield p("Print every value that occurs **strictly more** than `n / k` times (`n / k` with integer division). `k = 2` is the classic *majority element*. Sorting groups equal values together, so a single pass can count runs:")
    yield snippet("py", r'''
        def more_than_n_by_k(arr, k):
            arr = sorted(arr)
            n = len(arr)
            res = []
            i = 0
            while i < n:
                j = i
                while j < n and arr[j] == arr[i]:   # end of this run of equal values
                    j += 1
                if j - i > n // k:
                    res.append(arr[i])
                i = j
            return res

        print(*more_than_n_by_k([30, 10, 20, 20, 10, 20, 30, 30], 4))
        print(*more_than_n_by_k([2, 2, 1, 2, 3, 2], 2))
    ''', out="20 30\n2", caption="Python — sorting")
    yield complexity("O(n log n)", "O(1) extra (in-place sort)")
    yield idea("**Hash map of counts.** One pass to count, one pass over the map to report keys with `count > n / k`. The result is sorted before printing because map order is not portable.")
    yield multi('''
        20 30
        2
    ''', py=r'''
        def more_than_n_by_k(arr, k):
            n = len(arr)
            count = {}
            for x in arr:
                count[x] = count.get(x, 0) + 1
            return sorted(x for x, c in count.items() if c > n // k)   # sort: map order is not portable

        print(" ".join(map(str, more_than_n_by_k([30, 10, 20, 20, 10, 20, 30, 30], 4))))
        print(" ".join(map(str, more_than_n_by_k([2, 2, 1, 2, 3, 2], 2))))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        vector<int> moreThanNByK(const vector<int>& arr, int k) {
            int n = arr.size();
            unordered_map<int, int> count;
            for (int x : arr) count[x]++;
            vector<int> res;
            for (auto& [x, c] : count)
                if (c > n / k) res.push_back(x);
            sort(res.begin(), res.end());          // sort: map order is not portable
            return res;
        }

        void print(const vector<int>& v) {
            for (size_t i = 0; i < v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\n";
        }

        int main() {
            print(moreThanNByK({30, 10, 20, 20, 10, 20, 30, 30}, 4));
            print(moreThanNByK({2, 2, 1, 2, 3, 2}, 2));
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Collections;
        import java.util.HashMap;
        import java.util.List;
        import java.util.Map;

        public class Main {
            static List<Integer> moreThanNByK(int[] arr, int k) {
                int n = arr.length;
                Map<Integer, Integer> count = new HashMap<>();
                for (int x : arr) count.merge(x, 1, Integer::sum);
                List<Integer> res = new ArrayList<>();
                for (Map.Entry<Integer, Integer> e : count.entrySet())
                    if (e.getValue() > n / k) res.add(e.getKey());
                Collections.sort(res);                 // sort: map order is not portable
                return res;
            }

            static void print(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                print(moreThanNByK(new int[]{30, 10, 20, 20, 10, 20, 30, 30}, 4));
                print(moreThanNByK(new int[]{2, 2, 1, 2, 3, 2}, 2));
            }
        }
    ''', js=r'''
        function moreThanNByK(arr, k) {
            const n = arr.length;
            const count = new Map();
            for (const x of arr) count.set(x, (count.get(x) ?? 0) + 1);
            const res = [];
            for (const [x, c] of count)
                if (c > Math.floor(n / k)) res.push(x);
            return res.sort((a, b) => a - b);          // sort: map order is not portable
        }

        console.log(moreThanNByK([30, 10, 20, 20, 10, 20, 30, 30], 4).join(" "));
        console.log(moreThanNByK([2, 2, 1, 2, 3, 2], 2).join(" "));
    ''')
    yield complexity("O(n)", "O(n)")
    yield p("**Space-efficient method — `O(nk)` time, `O(k)` space.** At most `k − 1` values can appear more than `n / k` times (if `k` of them did, they would add up to more than `n` elements). So it is enough to track **`k − 1` candidates**, in the style of the Boyer–Moore majority vote:")
    yield steps(
        ("Candidate seen again", "If `arr[i]` is already a candidate, increment its count."),
        ("Room for a new candidate", "If fewer than `k − 1` candidates are stored, add `arr[i]` with count 1."),
        ("Table full", "Otherwise decrement **every** candidate's count and drop the ones that reach 0. This “cancels” `k` distinct values at once — the `k − 1` candidates and `arr[i]`."),
        ("Verify", "A value with more than `n / k` occurrences cannot be cancelled away (each cancellation round consumes `k` distinct elements, so there are fewer than `n / k` rounds), but a survivor is not guaranteed to be frequent. Recount the real occurrences of each survivor in a second pass and keep those above `n / k`."),
    )
    yield multi('''
        20 30
        2
    ''', py=r'''
        def more_than_n_by_k(arr, k):
            n = len(arr)
            cand = {}                                  # at most k-1 candidates
            for x in arr:
                if x in cand:
                    cand[x] += 1
                elif len(cand) < k - 1:
                    cand[x] = 1
                else:                                  # table full: cancel k distinct values
                    for key in list(cand):
                        cand[key] -= 1
                        if cand[key] == 0:
                            del cand[key]
            for key in cand:                           # second pass: real counts of the survivors
                cand[key] = 0
            for x in arr:
                if x in cand:
                    cand[x] += 1
            return sorted(x for x, c in cand.items() if c > n // k)

        print(" ".join(map(str, more_than_n_by_k([30, 10, 20, 20, 10, 20, 30, 30], 4))))
        print(" ".join(map(str, more_than_n_by_k([2, 2, 1, 2, 3, 2], 2))))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        vector<int> moreThanNByK(const vector<int>& arr, int k) {
            int n = arr.size();
            unordered_map<int, int> cand;                        // at most k-1 candidates
            for (int x : arr) {
                auto it = cand.find(x);
                if (it != cand.end()) it->second++;
                else if ((int)cand.size() < k - 1) cand[x] = 1;
                else {                                           // table full: cancel k distinct values
                    for (auto c = cand.begin(); c != cand.end();) {
                        if (--c->second == 0) c = cand.erase(c);
                        else ++c;
                    }
                }
            }
            for (auto& [key, c] : cand) c = 0;                   // second pass: real counts of the survivors
            for (int x : arr) {
                auto it = cand.find(x);
                if (it != cand.end()) it->second++;
            }
            vector<int> res;
            for (auto& [x, c] : cand) if (c > n / k) res.push_back(x);
            sort(res.begin(), res.end());
            return res;
        }

        void print(const vector<int>& v) {
            for (size_t i = 0; i < v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\n";
        }

        int main() {
            print(moreThanNByK({30, 10, 20, 20, 10, 20, 30, 30}, 4));
            print(moreThanNByK({2, 2, 1, 2, 3, 2}, 2));
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Collections;
        import java.util.HashMap;
        import java.util.Iterator;
        import java.util.List;
        import java.util.Map;

        public class Main {
            static List<Integer> moreThanNByK(int[] arr, int k) {
                int n = arr.length;
                Map<Integer, Integer> cand = new HashMap<>();            // at most k-1 candidates
                for (int x : arr) {
                    if (cand.containsKey(x)) cand.merge(x, 1, Integer::sum);
                    else if (cand.size() < k - 1) cand.put(x, 1);
                    else {                                               // table full: cancel k distinct values
                        Iterator<Map.Entry<Integer, Integer>> it = cand.entrySet().iterator();
                        while (it.hasNext()) {
                            Map.Entry<Integer, Integer> e = it.next();
                            if (e.getValue() == 1) it.remove();
                            else e.setValue(e.getValue() - 1);
                        }
                    }
                }
                for (Map.Entry<Integer, Integer> e : cand.entrySet()) e.setValue(0);   // second pass
                for (int x : arr) if (cand.containsKey(x)) cand.merge(x, 1, Integer::sum);
                List<Integer> res = new ArrayList<>();
                for (Map.Entry<Integer, Integer> e : cand.entrySet())
                    if (e.getValue() > n / k) res.add(e.getKey());
                Collections.sort(res);
                return res;
            }

            static void print(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                print(moreThanNByK(new int[]{30, 10, 20, 20, 10, 20, 30, 30}, 4));
                print(moreThanNByK(new int[]{2, 2, 1, 2, 3, 2}, 2));
            }
        }
    ''', js=r'''
        function moreThanNByK(arr, k) {
            const n = arr.length;
            const cand = new Map();                                // at most k-1 candidates
            for (const x of arr) {
                if (cand.has(x)) cand.set(x, cand.get(x) + 1);
                else if (cand.size < k - 1) cand.set(x, 1);
                else {                                             // table full: cancel k distinct values
                    for (const [key, c] of [...cand]) {
                        if (c === 1) cand.delete(key);
                        else cand.set(key, c - 1);
                    }
                }
            }
            for (const key of cand.keys()) cand.set(key, 0);       // second pass: real counts of the survivors
            for (const x of arr) if (cand.has(x)) cand.set(x, cand.get(x) + 1);
            const res = [];
            for (const [x, c] of cand) if (c > Math.floor(n / k)) res.push(x);
            return res.sort((a, b) => a - b);
        }

        console.log(moreThanNByK([30, 10, 20, 20, 10, 20, 30, 30], 4).join(" "));
        console.log(moreThanNByK([2, 2, 1, 2, 3, 2], 2).join(" "));
    ''')
    yield complexity("O(n · k)", "O(k)")
    yield pitfall("Skipping the **second pass** is the classic error: the candidate table can hold values that are *not* frequent (every element of `[1, 2, 3, 4]` with `k = 4` survives the first pass, yet none appears more than once). Candidates are only *possible* answers.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why do the “longest subarray” problems store the first index of each prefix sum, while “subarray exists” only needs a set?",
             "Existence needs one bit of information: *has this prefix sum appeared?* Longest needs *where did it first appear?* — the earliest index gives the longest span ending at the current position, so the map must never overwrite an existing key. A third variant, *count the subarrays with sum S*, stores **how many times** each prefix sum appeared and adds that count at every step.")
    yield qa("What is the worst-case time of these solutions, and does it matter?",
             "Hash table operations are `O(1)` on average but `O(n)` in the worst case (all keys collide), so every “`O(n)`” above is really expected time. With the built-in hash functions and random-looking data this never bites; in adversarial settings (competitive programming hacks, untrusted input) use a randomised hash or fall back to sorting (`O(n log n)` guaranteed).")
    yield qa("When would you choose sorting over hashing for these problems?",
             "When memory is tight (sorting can be in place, a hash table costs `O(n)` extra), when you need the output in order anyway, or when the keys are hard to hash (floating point, large composite objects). Union/intersection of arrays that are *already sorted* are `O(m + n)` with two pointers and need no hash table at all.")
    yield qa("The 0/1 subarray problem and the common-span problem look different from “subarray with sum 0” — how do you spot the reduction?",
             "Ask what *equal counts* means arithmetically: equal 0s and 1s ⇔ `Σ(+1 for 1, −1 for 0) = 0`; equal sums in `a` and `b` ⇔ `Σ(a[i] − b[i]) = 0`. Whenever a condition can be written as *some derived array sums to 0 (or to S) over a range*, the prefix-sum + hash map template applies unchanged.")
    yield qa("Explain why the n/k candidate method needs only k − 1 slots.",
             "If `k` different values each appeared more than `n / k` times, together they would account for more than `n` elements, which is impossible. Hence at most `k − 1` values can qualify, and a table of `k − 1` counters suffices to track every possible answer — the same argument that gives the single counter of Boyer–Moore majority voting for `k = 2`.")


@topic(G, "string", "String", "letter-case")
def _():
    yield lead("String problems are about **finding a pattern inside a text** without re-comparing characters you have already looked at. Naive matching restarts from scratch after every mismatch; Rabin–Karp compares hashes first; KMP precomputes exactly how far the pattern can safely slide. Around them sit the classic sliding-window and counting problems: anagram search, longest distinct substring and the lexicographic rank of a string.")
    yield define("Pattern searching", "given a text `txt` of length `n` and a pattern `pat` of length `m` (`1 ≤ m ≤ n`), report every index `i` such that `txt[i..i+m−1] == pat`. There are `n − m + 1` candidate positions.")

    yield section("The landscape of pattern-searching algorithms", "map")
    yield table(
        ["Preprocessing", "Algorithm", "Time", "Notes"],
        ["none", "naive", "`O((n − m + 1) · m)`", "simple; the bound is tight for `txt = aaaa…`, `pat = aaab`"],
        ["none", "naive, pattern characters distinct", "`O(n)`", "after a mismatch at `j`, slide by `j`"],
        ["pattern", "Rabin–Karp", "`O((n − m + 1) · m)` worst, `O(n + m)` expected", "compares a rolling hash first; great for many patterns of the same length"],
        ["pattern", "KMP (Knuth–Morris–Pratt)", "`O(n + m)` guaranteed", "LPS array tells how far to fall back; never re-reads a text character"],
        ["text", "suffix tree / suffix array", "`O(m)` per query after `O(n)` build", "when the same text is searched for many patterns"],
    )
    yield note("Preprocess whichever side is reused. One text, many patterns → preprocess the **text** (suffix structures). One pattern, many texts (or a streaming text) → preprocess the **pattern** (KMP, Rabin–Karp).")

    # ── Naive ─────────────────────────────────────────────────────────────────
    yield section("Naive pattern searching", "search")
    yield io("txt = \"GEEKSFORGEEKS\", pat = \"EKS\"", "2 10", "txt = \"AAAA\", pat = \"AAA\"", "0 1", "txt = \"geeks for geeks\", pat = \"geeks\"", "0 10")
    yield p("Library search already does this: Python's `str.find(pat, start)` repeated from `pos + 1` finds every (possibly overlapping) occurrence.")
    yield snippet("py", r'''
        def find_all(txt, pat):
            pos = txt.find(pat)
            while pos >= 0:
                print(pos, end=" ")
                pos = txt.find(pat, pos + 1)      # start just after the last hit → overlaps are found too
            print()

        find_all("GEEKSFORGEEKS", "EKS")
        find_all("AAAA", "AAA")
    ''', out="2 10\n0 1", caption="Python — using str.find")
    yield idea("Try every start `i` from `0` to `n − m`. Compare `pat[0..m−1]` with `txt[i..i+m−1]` character by character and stop at the first mismatch. Report `i` when all `m` characters matched. (The original notes printed inside the inner loop, which reports a hit only when the last compared character happens to be the final one — the report belongs *after* the inner loop.)")
    yield multi('''
        EKS in GEEKSFORGEEKS → 2 10
        AAA in AAAA → 0 1
        geeks in geeks for geeks → 0 10
    ''', py=r'''
        def naive_search(txt, pat):
            n, m = len(txt), len(pat)
            res = []
            for i in range(n - m + 1):              # every candidate start
                j = 0
                while j < m and txt[i + j] == pat[j]:
                    j += 1
                if j == m:                          # all m characters matched
                    res.append(i)
            return res

        for txt, pat in [("GEEKSFORGEEKS", "EKS"), ("AAAA", "AAA"), ("geeks for geeks", "geeks")]:
            print(pat, "in", txt, "→", " ".join(map(str, naive_search(txt, pat))))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        vector<int> naiveSearch(const string& txt, const string& pat) {
            int n = txt.size(), m = pat.size();
            vector<int> res;
            for (int i = 0; i + m <= n; i++) {           // every candidate start
                int j = 0;
                while (j < m && txt[i + j] == pat[j]) j++;
                if (j == m) res.push_back(i);            // all m characters matched
            }
            return res;
        }

        string join(const vector<int>& v) {
            string s;
            for (size_t i = 0; i < v.size(); i++) s += (i ? " " : "") + to_string(v[i]);
            return s;
        }

        int main() {
            vector<pair<string, string>> tests = {{"GEEKSFORGEEKS", "EKS"}, {"AAAA", "AAA"}, {"geeks for geeks", "geeks"}};
            for (auto& [txt, pat] : tests)
                cout << pat << " in " << txt << " → " << join(naiveSearch(txt, pat)) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> naiveSearch(String txt, String pat) {
                int n = txt.length(), m = pat.length();
                List<Integer> res = new ArrayList<>();
                for (int i = 0; i + m <= n; i++) {                // every candidate start
                    int j = 0;
                    while (j < m && txt.charAt(i + j) == pat.charAt(j)) j++;
                    if (j == m) res.add(i);                       // all m characters matched
                }
                return res;
            }

            static String join(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                String[][] tests = {{"GEEKSFORGEEKS", "EKS"}, {"AAAA", "AAA"}, {"geeks for geeks", "geeks"}};
                for (String[] t : tests)
                    System.out.println(t[1] + " in " + t[0] + " → " + join(naiveSearch(t[0], t[1])));
            }
        }
    ''', js=r'''
        function naiveSearch(txt, pat) {
            const n = txt.length, m = pat.length;
            const res = [];
            for (let i = 0; i + m <= n; i++) {               // every candidate start
                let j = 0;
                while (j < m && txt[i + j] === pat[j]) j++;
                if (j === m) res.push(i);                    // all m characters matched
            }
            return res;
        }

        for (const [txt, pat] of [["GEEKSFORGEEKS", "EKS"], ["AAAA", "AAA"], ["geeks for geeks", "geeks"]])
            console.log(pat, "in", txt, "→", naiveSearch(txt, pat).join(" "));
    ''')
    yield complexity("O((n − m + 1) · m)", "O(1)")
    yield note("The worst case needs a text and pattern that agree for a long time before each mismatch — `txt = \"AAAAAAAAAB\"`, `pat = \"AAAB\"` compares `m` characters at almost every start. On typical text the first character already mismatches and the naive search runs close to `O(n)`.")

    # ── Improved naive ─────────────────────────────────────────────────────────
    yield section("Improved naive when the pattern's characters are distinct", "letter-spacing")
    yield io("txt = \"ABCABCDABCD\", pat = \"ABCD\"", "3 7", "txt = \"AAAB\", pat = \"AB\"", "2")
    yield idea("Suppose the comparison at start `i` fails at position `j > 0`, so `txt[i..i+j−1] == pat[0..j−1]`. Could a match begin at `i + s` for some `1 ≤ s < j`? It would need `txt[i+s] == pat[0]`, but `txt[i+s] = pat[s]`, and all pattern characters are **distinct**, so `pat[s] ≠ pat[0]`. Therefore the next possible start is `i + j`: slide by `j` instead of `1`. Every text character is now compared at most twice, giving `O(n)`.")
    yield diagram('''
        txt :  A B C A B C D A B C D
        pat :  A B C D                 mismatch at j = 3 (A ≠ D)
                     A B C D           slide by 3 → match at i = 3
                             A B C D   slide by m = 4 → match at i = 7
    ''', "Text characters are never re-scanned from the middle of a partial match")
    yield multi('''
        3 7
        2
    ''', py=r'''
        def distinct_search(txt, pat):
            n, m = len(txt), len(pat)
            res = []
            i = 0
            while i <= n - m:
                j = 0
                while j < m and txt[i + j] == pat[j]:
                    j += 1
                if j == m:
                    res.append(i)
                i += max(1, j)            # slide by j (by 1 when the very first character failed)
            return res

        print(" ".join(map(str, distinct_search("ABCABCDABCD", "ABCD"))))
        print(" ".join(map(str, distinct_search("AAAB", "AB"))))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        vector<int> distinctSearch(const string& txt, const string& pat) {
            int n = txt.size(), m = pat.size();
            vector<int> res;
            int i = 0;
            while (i <= n - m) {
                int j = 0;
                while (j < m && txt[i + j] == pat[j]) j++;
                if (j == m) res.push_back(i);
                i += max(1, j);                // slide by j (by 1 when the very first character failed)
            }
            return res;
        }

        string join(const vector<int>& v) {
            string s;
            for (size_t i = 0; i < v.size(); i++) s += (i ? " " : "") + to_string(v[i]);
            return s;
        }

        int main() {
            cout << join(distinctSearch("ABCABCDABCD", "ABCD")) << "\n";
            cout << join(distinctSearch("AAAB", "AB")) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> distinctSearch(String txt, String pat) {
                int n = txt.length(), m = pat.length();
                List<Integer> res = new ArrayList<>();
                int i = 0;
                while (i <= n - m) {
                    int j = 0;
                    while (j < m && txt.charAt(i + j) == pat.charAt(j)) j++;
                    if (j == m) res.add(i);
                    i += Math.max(1, j);       // slide by j (by 1 when the very first character failed)
                }
                return res;
            }

            static String join(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                System.out.println(join(distinctSearch("ABCABCDABCD", "ABCD")));
                System.out.println(join(distinctSearch("AAAB", "AB")));
            }
        }
    ''', js=r'''
        function distinctSearch(txt, pat) {
            const n = txt.length, m = pat.length;
            const res = [];
            let i = 0;
            while (i <= n - m) {
                let j = 0;
                while (j < m && txt[i + j] === pat[j]) j++;
                if (j === m) res.push(i);
                i += Math.max(1, j);           // slide by j (by 1 when the very first character failed)
            }
            return res;
        }

        console.log(distinctSearch("ABCABCDABCD", "ABCD").join(" "));
        console.log(distinctSearch("AAAB", "AB").join(" "));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("The original notes ran this with `pat = \"geeks\"` — whose `e` repeats — so the precondition was violated (and the Python `for j in range(m)` loop could never reach `j == m`). With a repeated character, sliding by `j` can skip a real match: `txt = \"aab\"`, `pat = \"ab\"` fails at `j = 1` on start 0 and would jump to start 1 — fine here, but `txt = \"aaab\"`, `pat = \"aab\"` fails at `j = 2` and skips the match at 1. That is exactly the gap KMP closes.")

    # ── Rabin–Karp ─────────────────────────────────────────────────────────────
    yield section("Rabin–Karp with a rolling hash", "hash")
    yield io("txt = \"geeks for geeks\", pat = \"geeks\"", "0 10", "txt = \"GEEKSFORGEEKS\", pat = \"EKS\"", "2 10", "txt = \"aaaaab\", pat = \"aaaa\"", "0 1")
    yield p("Like the naive algorithm, slide the pattern over every start — but compare a **hash** of the pattern with a hash of the current window first, and only compare characters when the hashes agree. The trick is computing the next window's hash from the previous one in `O(1)` — a *rolling hash*.")
    yield steps(
        ("A first attempt: the sum of character codes", "`t(i+1) = t(i) + txt[i+m] − txt[i]` — `O(1)` per shift, but every anagram of the pattern (`abc`, `bca`, `cab`) has the same hash, so spurious hits are common."),
        ("A better hash: treat the window as a base-`d` number", "`h(s) = s[0]·d^(m−1) + s[1]·d^(m−2) + … + s[m−1]·d^0`. With `d = 5` and `a = 1, b = 2, c = 3, d = 4`: `h(\"abc\") = 1·25 + 2·5 + 3 = 38`, `h(\"dab\") = 4·25 + 1·5 + 2 = 107`. Position now matters."),
        ("Roll it", "Remove the leading digit, shift left, append the new digit: `t(i+1) = d · (t(i) − txt[i] · d^(m−1)) + txt[i+m]`. Three multiplications and two additions — `O(1)` whatever `m` is."),
        ("Keep numbers small", "Take everything modulo a prime `q` (`d = 256` for bytes, `q = 101` in the examples). Equal hashes are then only *probably* equal strings — the character check settles it."),
    )
    yield formula("t(i+1) = ( d · ( t(i) − txt[i] · d^(m−1) ) + txt[i+m] ) mod q")
    yield idea("Hashing shifts the cost from `O(m)` per window to `O(1)` per window plus `O(m)` only when the hashes collide. A good hash collides rarely, so the expected time is `O(n + m)`; with a bad hash (or an adversarial input) every window collides and it degrades to the naive `O(n · m)`. The program below also reports **spurious hits** — windows whose hash matched but whose text did not.")
    yield multi('''
        geeks in geeks for geeks → 0 10
        EKS in GEEKSFORGEEKS → 2 10 (spurious hits at 5)
        aaaa in aaaaab → 0 1
    ''', py=r'''
        d, q = 256, 101                              # alphabet size, prime modulus

        def rabin_karp(txt, pat):
            n, m = len(txt), len(pat)
            h = 1                                    # h = d^(m-1) mod q
            for _ in range(m - 1):
                h = (h * d) % q
            p = t = 0
            for i in range(m):                       # hash of the pattern and of the first window
                p = (p * d + ord(pat[i])) % q
                t = (t * d + ord(txt[i])) % q
            hits, spurious = [], []
            for i in range(n - m + 1):
                if p == t:                           # hashes agree → verify character by character
                    if txt[i:i + m] == pat:
                        hits.append(i)
                    else:
                        spurious.append(i)
                if i < n - m:                        # roll: drop txt[i], append txt[i+m]
                    t = (d * (t - ord(txt[i]) * h) + ord(txt[i + m])) % q
                    if t < 0:
                        t += q                       # (Python's % is never negative; kept for symmetry)
            return hits, spurious

        for txt, pat in [("geeks for geeks", "geeks"), ("GEEKSFORGEEKS", "EKS"), ("aaaaab", "aaaa")]:
            hits, spurious = rabin_karp(txt, pat)
            line = pat + " in " + txt + " → " + " ".join(map(str, hits))
            if spurious:
                line += " (spurious hits at " + " ".join(map(str, spurious)) + ")"
            print(line)
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        const int d = 256, q = 101;                  // alphabet size, prime modulus

        string join(const vector<int>& v) {
            string s;
            for (size_t i = 0; i < v.size(); i++) s += (i ? " " : "") + to_string(v[i]);
            return s;
        }

        void rabinKarp(const string& txt, const string& pat) {
            int n = txt.size(), m = pat.size();
            int h = 1;                                // h = d^(m-1) mod q
            for (int i = 0; i < m - 1; i++) h = (h * d) % q;
            int p = 0, t = 0;
            for (int i = 0; i < m; i++) {             // hash of the pattern and of the first window
                p = (p * d + pat[i]) % q;
                t = (t * d + txt[i]) % q;
            }
            vector<int> hits, spurious;
            for (int i = 0; i <= n - m; i++) {
                if (p == t) {                         // hashes agree → verify character by character
                    if (txt.compare(i, m, pat) == 0) hits.push_back(i);
                    else spurious.push_back(i);
                }
                if (i < n - m) {                      // roll: drop txt[i], append txt[i+m]
                    t = (d * (t - txt[i] * h) + txt[i + m]) % q;
                    if (t < 0) t += q;                // C++ % can be negative
                }
            }
            cout << pat << " in " << txt << " → " << join(hits);
            if (!spurious.empty()) cout << " (spurious hits at " << join(spurious) << ")";
            cout << "\n";
        }

        int main() {
            rabinKarp("geeks for geeks", "geeks");
            rabinKarp("GEEKSFORGEEKS", "EKS");
            rabinKarp("aaaaab", "aaaa");
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static final int d = 256, q = 101;        // alphabet size, prime modulus

            static String join(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }

            static void rabinKarp(String txt, String pat) {
                int n = txt.length(), m = pat.length();
                int h = 1;                            // h = d^(m-1) mod q
                for (int i = 0; i < m - 1; i++) h = (h * d) % q;
                int p = 0, t = 0;
                for (int i = 0; i < m; i++) {         // hash of the pattern and of the first window
                    p = (p * d + pat.charAt(i)) % q;
                    t = (t * d + txt.charAt(i)) % q;
                }
                List<Integer> hits = new ArrayList<>(), spurious = new ArrayList<>();
                for (int i = 0; i <= n - m; i++) {
                    if (p == t) {                     // hashes agree → verify character by character
                        if (txt.startsWith(pat, i)) hits.add(i);
                        else spurious.add(i);
                    }
                    if (i < n - m) {                  // roll: drop txt[i], append txt[i+m]
                        t = (d * (t - txt.charAt(i) * h) + txt.charAt(i + m)) % q;
                        if (t < 0) t += q;            // Java % can be negative
                    }
                }
                String line = pat + " in " + txt + " → " + join(hits);
                if (!spurious.isEmpty()) line += " (spurious hits at " + join(spurious) + ")";
                System.out.println(line);
            }

            public static void main(String[] args) {
                rabinKarp("geeks for geeks", "geeks");
                rabinKarp("GEEKSFORGEEKS", "EKS");
                rabinKarp("aaaaab", "aaaa");
            }
        }
    ''', js=r'''
        const d = 256, q = 101;                        // alphabet size, prime modulus

        function rabinKarp(txt, pat) {
            const n = txt.length, m = pat.length;
            let h = 1;                                 // h = d^(m-1) mod q
            for (let i = 0; i < m - 1; i++) h = (h * d) % q;
            let p = 0, t = 0;
            for (let i = 0; i < m; i++) {              // hash of the pattern and of the first window
                p = (p * d + pat.charCodeAt(i)) % q;
                t = (t * d + txt.charCodeAt(i)) % q;
            }
            const hits = [], spurious = [];
            for (let i = 0; i <= n - m; i++) {
                if (p === t) {                         // hashes agree → verify character by character
                    if (txt.startsWith(pat, i)) hits.push(i);
                    else spurious.push(i);
                }
                if (i < n - m) {                       // roll: drop txt[i], append txt[i+m]
                    t = (d * (t - txt.charCodeAt(i) * h) + txt.charCodeAt(i + m)) % q;
                    if (t < 0) t += q;                 // JavaScript % can be negative
                }
            }
            let line = pat + " in " + txt + " → " + hits.join(" ");
            if (spurious.length) line += " (spurious hits at " + spurious.join(" ") + ")";
            console.log(line);
        }

        rabinKarp("geeks for geeks", "geeks");
        rabinKarp("GEEKSFORGEEKS", "EKS");
        rabinKarp("aaaaab", "aaaa");
    ''')
    yield complexity("O(n + m) expected, O(n · m) worst", "O(1)")
    yield note("Window 5 of `GEEKSFORGEEKS` is `SFO`, which happens to hash to the same value as `EKS` modulo 101 — a **spurious hit** caught by the character comparison. A larger prime (`10^9 + 7` with 64-bit arithmetic) makes such collisions rare in practice; in C++/Java use `long` so `d · t` cannot overflow.")
    yield pitfall("The subtraction in the rolling step makes the remainder **negative** in C++, Java and JavaScript (`-7 % 101 == -7`). Always add `q` back (or write `((x % q) + q) % q`). Python's `%` already returns a non-negative result, which is why the bug does not show in Python prototypes.")

    # ── LPS ─────────────────────────────────────────────────────────────────────
    yield section("KMP: the LPS array (longest proper prefix which is also a suffix)", "arrows-right-left")
    yield io("pat = \"ababc\"", "lps = [0, 0, 1, 2, 0]", "pat = \"aaaa\"", "lps = [0, 1, 2, 3]", "pat = \"abacabad\"", "lps = [0, 0, 1, 0, 1, 2, 3, 0]")
    yield p("A **proper prefix** of a string is a prefix that is not the whole string; likewise for suffixes. For `\"abc\"`: proper prefixes `\"\"`, `\"a\"`, `\"ab\"`; proper suffixes `\"\"`, `\"c\"`, `\"bc\"`. `lps[i]` is the length of the longest proper prefix of `pat[0..i]` that is also a suffix of `pat[0..i]`.")
    yield diagram('''
        pat[0..i]    longest proper prefix that is also a suffix    lps[i]
        a            ""                                                0
        ab           ""                                                0
        aba          "a"                                               1
        abab         "ab"                                              2
        ababc        ""                                                0
    ''', "lps for \"ababc\" = [0, 0, 1, 2, 0]")
    yield p("Computing each entry by brute force — try every length from `i` down to `1` and compare — is simple but cubic:")
    yield snippet("py", r'''
        def longest_proper_prefix_suffix(s):
            n = len(s)
            for length in range(n - 1, 0, -1):             # longest first
                if s[:length] == s[n - length:]:
                    return length
            return 0

        def lps_naive(pat):
            return [longest_proper_prefix_suffix(pat[:i + 1]) for i in range(len(pat))]

        print(lps_naive("ababc"))
        print(lps_naive("abacabad"))
    ''', out="[0, 0, 1, 2, 0]\n[0, 0, 1, 0, 1, 2, 3, 0]", caption="Python — naive")
    yield complexity("O(n³)", "O(n)")
    yield idea("Build `lps` left to right, reusing the previous answer. Let `len = lps[i−1]` — the prefix `pat[0..len−1]` matches the suffix ending at `i−1`. If `pat[len] == pat[i]`, that match extends by one: `lps[i] = len + 1`. Otherwise fall back to the **next shorter** candidate: the longest proper prefix-suffix of `pat[0..len−1]`, which is `lps[len−1]`, and compare again. Fall back until a match or `len == 0`.")
    yield diagram('''
        pat = a b a c a b a d        lps so far = 0 0 1 0 1 2 3 ?       (i = 7, len = lps[6] = 3)

        pat[3] = 'c' ≠ pat[7] = 'd'   →  len = lps[2] = 1
        pat[1] = 'b' ≠ 'd'            →  len = lps[0] = 0
        pat[0] = 'a' ≠ 'd', len == 0  →  lps[7] = 0
    ''', "Falling back through shorter prefix-suffix candidates instead of rescanning")
    yield multi('''
        ababc → 0 0 1 2 0
        aaaa → 0 1 2 3
        abacabad → 0 0 1 0 1 2 3 0
    ''', py=r'''
        def compute_lps(pat):
            m = len(pat)
            lps = [0] * m
            length = 0                         # length of the previous longest prefix-suffix
            i = 1
            while i < m:
                if pat[i] == pat[length]:
                    length += 1
                    lps[i] = length            # the match extends by one
                    i += 1
                elif length != 0:
                    length = lps[length - 1]   # fall back to the next shorter candidate; i stays
                else:
                    lps[i] = 0
                    i += 1
            return lps

        for pat in ["ababc", "aaaa", "abacabad"]:
            print(pat, "→", " ".join(map(str, compute_lps(pat))))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        vector<int> computeLps(const string& pat) {
            int m = pat.size();
            vector<int> lps(m, 0);
            int len = 0;                           // length of the previous longest prefix-suffix
            int i = 1;
            while (i < m) {
                if (pat[i] == pat[len]) {
                    lps[i++] = ++len;              // the match extends by one
                } else if (len != 0) {
                    len = lps[len - 1];            // fall back to the next shorter candidate; i stays
                } else {
                    lps[i++] = 0;
                }
            }
            return lps;
        }

        int main() {
            for (string pat : {"ababc", "aaaa", "abacabad"}) {
                cout << pat << " →";
                for (int x : computeLps(pat)) cout << " " << x;
                cout << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int[] computeLps(String pat) {
                int m = pat.length();
                int[] lps = new int[m];
                int len = 0;                           // length of the previous longest prefix-suffix
                int i = 1;
                while (i < m) {
                    if (pat.charAt(i) == pat.charAt(len)) {
                        lps[i++] = ++len;              // the match extends by one
                    } else if (len != 0) {
                        len = lps[len - 1];            // fall back to the next shorter candidate; i stays
                    } else {
                        lps[i++] = 0;
                    }
                }
                return lps;
            }

            public static void main(String[] args) {
                for (String pat : new String[]{"ababc", "aaaa", "abacabad"}) {
                    StringBuilder sb = new StringBuilder(pat + " →");
                    for (int x : computeLps(pat)) sb.append(" ").append(x);
                    System.out.println(sb);
                }
            }
        }
    ''', js=r'''
        function computeLps(pat) {
            const m = pat.length;
            const lps = new Array(m).fill(0);
            let len = 0;                               // length of the previous longest prefix-suffix
            let i = 1;
            while (i < m) {
                if (pat[i] === pat[len]) {
                    lps[i++] = ++len;                  // the match extends by one
                } else if (len !== 0) {
                    len = lps[len - 1];                // fall back to the next shorter candidate; i stays
                } else {
                    lps[i++] = 0;
                }
            }
            return lps;
        }

        for (const pat of ["ababc", "aaaa", "abacabad"])
            console.log(pat, "→", computeLps(pat).join(" "));
    ''')
    yield complexity("O(m)", "O(m)")
    yield note("Why `O(m)` despite the inner fall-back loop: `len` increases at most once per character (by 1) and every fall-back strictly decreases it, so the total number of fall-backs over the whole run is at most `m`. The same argument gives the linear bound for the matching phase below.")

    # ── KMP matching ─────────────────────────────────────────────────────────────
    yield section("KMP string matching", "bolt")
    yield io("txt = \"abcdefg\", pat = \"bcd\"", "1", "txt = \"aaaaab\", pat = \"aaaa\"", "0 1", "txt = \"aaaaabaaaaac\", pat = \"aaaa\"", "0 1 6 7")
    yield idea("Run two indices, `i` over the text and `j` over the pattern. On a match advance both. On a mismatch with `j > 0`, the characters `txt[i−j..i−1]` equal `pat[0..j−1]` — and `lps[j−1]` says how long a prefix of the pattern is *still* aligned with the end of that stretch. So set `j = lps[j−1]` and compare again **without moving `i`**. When `j` reaches `m` report `i − m` and continue the same way (`j = lps[m−1]`) to find overlapping occurrences. `i` never moves backwards, so the text is read once.")
    yield diagram('''
        txt :  a a a a a b a a a a a c
        pat :  a a a a                  j = 4 = m → report 0, j = lps[3] = 3
        pat :    a a a a                txt[4] = a = pat[3] → j = 4 → report 1, j = 3
        pat :      a a a a              txt[5] = b ≠ pat[3] → j = lps[2] = 2 … → j = 0, then i++
        pat :              a a a a      matches resume at i = 6 → report 6, then 7
    ''', "The text index i never goes back; only the pattern index j falls back")
    yield multi('''
        bcd in abcdefg → 1
        aaaa in aaaaab → 0 1
        aaaa in aaaaabaaaaac → 0 1 6 7
    ''', py=r'''
        def compute_lps(pat):
            lps = [0] * len(pat)
            length, i = 0, 1
            while i < len(pat):
                if pat[i] == pat[length]:
                    length += 1
                    lps[i] = length
                    i += 1
                elif length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
            return lps

        def kmp_search(txt, pat):
            n, m = len(txt), len(pat)
            lps = compute_lps(pat)
            res = []
            i = j = 0                          # i → text, j → pattern
            while i < n:
                if txt[i] == pat[j]:
                    i += 1
                    j += 1
                    if j == m:                 # full match ends at i-1
                        res.append(i - j)
                        j = lps[j - 1]         # keep going: overlapping matches
                elif j != 0:
                    j = lps[j - 1]             # fall back in the pattern; i does not move
                else:
                    i += 1                     # no partial match to reuse
            return res

        for txt, pat in [("abcdefg", "bcd"), ("aaaaab", "aaaa"), ("aaaaabaaaaac", "aaaa")]:
            print(pat, "in", txt, "→", " ".join(map(str, kmp_search(txt, pat))))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        vector<int> computeLps(const string& pat) {
            int m = pat.size();
            vector<int> lps(m, 0);
            int len = 0, i = 1;
            while (i < m) {
                if (pat[i] == pat[len]) lps[i++] = ++len;
                else if (len != 0) len = lps[len - 1];
                else lps[i++] = 0;
            }
            return lps;
        }

        vector<int> kmpSearch(const string& txt, const string& pat) {
            int n = txt.size(), m = pat.size();
            vector<int> lps = computeLps(pat), res;
            int i = 0, j = 0;                          // i → text, j → pattern
            while (i < n) {
                if (txt[i] == pat[j]) {
                    i++; j++;
                    if (j == m) {                      // full match ends at i-1
                        res.push_back(i - j);
                        j = lps[j - 1];                // keep going: overlapping matches
                    }
                } else if (j != 0) {
                    j = lps[j - 1];                    // fall back in the pattern; i does not move
                } else {
                    i++;                               // no partial match to reuse
                }
            }
            return res;
        }

        string join(const vector<int>& v) {
            string s;
            for (size_t i = 0; i < v.size(); i++) s += (i ? " " : "") + to_string(v[i]);
            return s;
        }

        int main() {
            vector<pair<string, string>> tests = {{"abcdefg", "bcd"}, {"aaaaab", "aaaa"}, {"aaaaabaaaaac", "aaaa"}};
            for (auto& [txt, pat] : tests)
                cout << pat << " in " << txt << " → " << join(kmpSearch(txt, pat)) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static int[] computeLps(String pat) {
                int m = pat.length();
                int[] lps = new int[m];
                int len = 0, i = 1;
                while (i < m) {
                    if (pat.charAt(i) == pat.charAt(len)) lps[i++] = ++len;
                    else if (len != 0) len = lps[len - 1];
                    else lps[i++] = 0;
                }
                return lps;
            }

            static List<Integer> kmpSearch(String txt, String pat) {
                int n = txt.length(), m = pat.length();
                int[] lps = computeLps(pat);
                List<Integer> res = new ArrayList<>();
                int i = 0, j = 0;                          // i → text, j → pattern
                while (i < n) {
                    if (txt.charAt(i) == pat.charAt(j)) {
                        i++; j++;
                        if (j == m) {                      // full match ends at i-1
                            res.add(i - j);
                            j = lps[j - 1];                // keep going: overlapping matches
                        }
                    } else if (j != 0) {
                        j = lps[j - 1];                    // fall back in the pattern; i does not move
                    } else {
                        i++;                               // no partial match to reuse
                    }
                }
                return res;
            }

            static String join(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                String[][] tests = {{"abcdefg", "bcd"}, {"aaaaab", "aaaa"}, {"aaaaabaaaaac", "aaaa"}};
                for (String[] t : tests)
                    System.out.println(t[1] + " in " + t[0] + " → " + join(kmpSearch(t[0], t[1])));
            }
        }
    ''', js=r'''
        function computeLps(pat) {
            const m = pat.length, lps = new Array(m).fill(0);
            let len = 0, i = 1;
            while (i < m) {
                if (pat[i] === pat[len]) lps[i++] = ++len;
                else if (len !== 0) len = lps[len - 1];
                else lps[i++] = 0;
            }
            return lps;
        }

        function kmpSearch(txt, pat) {
            const n = txt.length, m = pat.length;
            const lps = computeLps(pat), res = [];
            let i = 0, j = 0;                              // i → text, j → pattern
            while (i < n) {
                if (txt[i] === pat[j]) {
                    i++; j++;
                    if (j === m) {                         // full match ends at i-1
                        res.push(i - j);
                        j = lps[j - 1];                    // keep going: overlapping matches
                    }
                } else if (j !== 0) {
                    j = lps[j - 1];                        // fall back in the pattern; i does not move
                } else {
                    i++;                                   // no partial match to reuse
                }
            }
            return res;
        }

        for (const [txt, pat] of [["abcdefg", "bcd"], ["aaaaab", "aaaa"], ["aaaaabaaaaac", "aaaa"]])
            console.log(pat, "in", txt, "→", kmpSearch(txt, pat).join(" "));
    ''')
    yield complexity("O(n + m)", "O(m)")
    yield pitfall("After a full match do **not** reset `j = 0` — that misses overlapping occurrences (`aaaa` in `aaaaab` occurs at both 0 and 1). `j = lps[m − 1]` keeps the longest reusable overlap. And guard the mismatch branch with `j != 0` before indexing `lps[j − 1]`.")

    # ── Anagram search ─────────────────────────────────────────────────────────
    yield section("Anagram search", "arrows-shuffle")
    yield io("txt = \"geeksforgeeks\", pat = \"forg\"", "Yes  (window \"forg\" at 5)", "txt = \"geeksforgeeks\", pat = \"rseek\"", "No")
    yield p("Does the text contain any **permutation** of the pattern as a substring? Order no longer matters, only the multiset of characters, so hashing by comparison fails and we count instead. Naive: for every window, count the pattern's characters up and the window's characters down and check that everything cancels.")
    yield snippet("py", r'''
        CHAR = 256

        def is_anagram_at(txt, pat, i):
            count = [0] * CHAR
            for j in range(len(pat)):
                count[ord(pat[j])] += 1
                count[ord(txt[i + j])] -= 1
            return all(c == 0 for c in count)

        def contains_anagram(txt, pat):
            n, m = len(txt), len(pat)
            return any(is_anagram_at(txt, pat, i) for i in range(n - m + 1))

        print("Yes" if contains_anagram("geeksforgeeks", "forg") else "No")
        print("Yes" if contains_anagram("geeksforgeeks", "rseek") else "No")
    ''', out="Yes\nNo", caption="Python — naive")
    yield complexity("O((n − m + 1) · (m + CHAR))", "O(CHAR)")
    yield idea("Sliding window of size `m` with two count arrays: `cp` for the pattern (fixed) and `ct` for the current window. Moving the window one step changes **two** counts in `ct` (one character in, one out) — `O(1)`. After each move compare `ct` with `cp`; a window is an anagram exactly when the two arrays are equal.")
    yield multi('''
        forg in geeksforgeeks → Yes
        rseek in geeksforgeeks → No
        abc in cbaebabacd → Yes
    ''', py=r'''
        CHAR = 256

        def contains_anagram(txt, pat):
            n, m = len(txt), len(pat)
            if m > n:
                return False
            ct, cp = [0] * CHAR, [0] * CHAR
            for i in range(m):                     # first window and the pattern
                ct[ord(txt[i])] += 1
                cp[ord(pat[i])] += 1
            for i in range(m, n):
                if ct == cp:
                    return True
                ct[ord(txt[i])] += 1               # character entering the window
                ct[ord(txt[i - m])] -= 1           # character leaving the window
            return ct == cp                        # the last window

        for txt, pat in [("geeksforgeeks", "forg"), ("geeksforgeeks", "rseek"), ("cbaebabacd", "abc")]:
            print(pat, "in", txt, "→", "Yes" if contains_anagram(txt, pat) else "No")
    ''', cpp=r'''
        #include <array>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        const int CHAR = 256;

        bool containsAnagram(const string& txt, const string& pat) {
            int n = txt.size(), m = pat.size();
            if (m > n) return false;
            array<int, CHAR> ct{}, cp{};
            for (int i = 0; i < m; i++) {                      // first window and the pattern
                ct[(unsigned char)txt[i]]++;
                cp[(unsigned char)pat[i]]++;
            }
            for (int i = m; i < n; i++) {
                if (ct == cp) return true;
                ct[(unsigned char)txt[i]]++;                   // character entering the window
                ct[(unsigned char)txt[i - m]]--;               // character leaving the window
            }
            return ct == cp;                                   // the last window
        }

        int main() {
            vector<pair<string, string>> tests = {{"geeksforgeeks", "forg"}, {"geeksforgeeks", "rseek"}, {"cbaebabacd", "abc"}};
            for (auto& [txt, pat] : tests)
                cout << pat << " in " << txt << " → " << (containsAnagram(txt, pat) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static final int CHAR = 256;

            static boolean containsAnagram(String txt, String pat) {
                int n = txt.length(), m = pat.length();
                if (m > n) return false;
                int[] ct = new int[CHAR], cp = new int[CHAR];
                for (int i = 0; i < m; i++) {                  // first window and the pattern
                    ct[txt.charAt(i)]++;
                    cp[pat.charAt(i)]++;
                }
                for (int i = m; i < n; i++) {
                    if (Arrays.equals(ct, cp)) return true;
                    ct[txt.charAt(i)]++;                       // character entering the window
                    ct[txt.charAt(i - m)]--;                   // character leaving the window
                }
                return Arrays.equals(ct, cp);                  // the last window
            }

            public static void main(String[] args) {
                String[][] tests = {{"geeksforgeeks", "forg"}, {"geeksforgeeks", "rseek"}, {"cbaebabacd", "abc"}};
                for (String[] t : tests)
                    System.out.println(t[1] + " in " + t[0] + " → " + (containsAnagram(t[0], t[1]) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        const CHAR = 256;

        function sameCounts(a, b) {
            for (let i = 0; i < CHAR; i++) if (a[i] !== b[i]) return false;
            return true;
        }

        function containsAnagram(txt, pat) {
            const n = txt.length, m = pat.length;
            if (m > n) return false;
            const ct = new Array(CHAR).fill(0), cp = new Array(CHAR).fill(0);
            for (let i = 0; i < m; i++) {                      // first window and the pattern
                ct[txt.charCodeAt(i)]++;
                cp[pat.charCodeAt(i)]++;
            }
            for (let i = m; i < n; i++) {
                if (sameCounts(ct, cp)) return true;
                ct[txt.charCodeAt(i)]++;                       // character entering the window
                ct[txt.charCodeAt(i - m)]--;                   // character leaving the window
            }
            return sameCounts(ct, cp);                         // the last window
        }

        for (const [txt, pat] of [["geeksforgeeks", "forg"], ["geeksforgeeks", "rseek"], ["cbaebabacd", "abc"]])
            console.log(pat, "in", txt, "→", containsAnagram(txt, pat) ? "Yes" : "No");
    ''')
    yield complexity("O(n · CHAR)", "O(CHAR)")
    yield note("`CHAR` is a constant, so this is linear — but comparing 256 counters per window is the dominant cost. The standard refinement keeps a single `mismatches` counter: when a count in `ct` changes, update whether that slot agrees with `cp`; the window is an anagram when `mismatches == 0`. That is `O(n)` with no array comparison at all.")

    # ── Lexicographic rank ─────────────────────────────────────────────────────
    yield section("Lexicographic rank of a string", "sort-ascending-letters")
    yield io("s = \"ABC\"", "1", "s = \"BAC\"", "3", "s = \"STRING\"", "598")
    yield p("Among all permutations of the string's characters listed in dictionary order, which position does the string itself hold (1-based)? For `\"ABC\"` the six permutations are:")
    yield table(
        ["Rank", "Permutation"],
        ["1", "`ABC`"], ["2", "`ACB`"], ["3", "`BAC`"], ["4", "`BCA`"], ["5", "`CAB`"], ["6", "`CBA`"],
    )
    yield p("The pen-and-paper method generates every permutation and counts — `O(n · n!)`:")
    yield snippet("py", r'''
        from itertools import permutations

        def rank_naive(s):
            perms = sorted(''.join(p) for p in permutations(s))     # n! strings, sorted
            return perms.index(s) + 1

        print(rank_naive("ABC"), rank_naive("BAC"), rank_naive("STRING"))
    ''', out="1 3 598", caption="Python — naive")
    yield idea("Count how many permutations come **before** `s`. Every permutation that starts with a character smaller than `s[0]` precedes `s` — there are `(number of smaller characters) × (n − 1)!` of them. Fix `s[0]` and repeat on the remainder: at position `i`, add `(smaller unused characters to the right of i) × (n − i − 1)!`. A cumulative count array `count[c] = number of unused characters ≤ c` answers “how many smaller” in `O(1)`; after using `s[i]`, decrement `count[c]` for every `c ≥ s[i]`.")
    yield diagram('''
        s = "BAC",  n = 3,  (n-1)! = 2

        i = 0, 'B' : smaller unused chars = {A} → 1 × 2! = 2 permutations start with 'A'
        i = 1, 'A' : smaller unused chars = {}  → 0 × 1! = 0
        rank = 1 + 2 + 0 = 3
    ''', "Rank of \"BAC\"")
    yield multi('''
        ABC → 1
        BAC → 3
        CBA → 6
        STRING → 598
    ''', py=r'''
        CHAR = 256

        def factorial(n):
            r = 1
            for i in range(2, n + 1):
                r *= i
            return r

        def lex_rank(s):
            n = len(s)
            count = [0] * CHAR
            for ch in s:
                count[ord(ch)] += 1
            for c in range(1, CHAR):                 # cumulative: count[c] = #chars <= c
                count[c] += count[c - 1]
            rank = 1
            mul = factorial(n)
            for i in range(n - 1):
                mul //= n - i                        # (n - i - 1)!
                c = ord(s[i])
                rank += count[c - 1] * mul           # unused chars smaller than s[i]
                for j in range(c, CHAR):             # s[i] is used up now
                    count[j] -= 1
            return rank

        for s in ["ABC", "BAC", "CBA", "STRING"]:
            print(s, "→", lex_rank(s))
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        const int CHAR = 256;

        long long factorial(int n) {
            long long r = 1;
            for (int i = 2; i <= n; i++) r *= i;
            return r;
        }

        long long lexRank(const string& s) {
            int n = s.size();
            int count[CHAR] = {0};
            for (char ch : s) count[(unsigned char)ch]++;
            for (int c = 1; c < CHAR; c++) count[c] += count[c - 1];   // cumulative: count[c] = #chars <= c
            long long rank = 1, mul = factorial(n);
            for (int i = 0; i < n - 1; i++) {
                mul /= n - i;                                    // (n - i - 1)!
                int c = (unsigned char)s[i];
                rank += count[c - 1] * mul;                      // unused chars smaller than s[i]
                for (int j = c; j < CHAR; j++) count[j]--;       // s[i] is used up now
            }
            return rank;
        }

        int main() {
            for (string s : {"ABC", "BAC", "CBA", "STRING"})
                cout << s << " → " << lexRank(s) << "\n";
        }
    ''', java=r'''
        public class Main {
            static final int CHAR = 256;

            static long factorial(int n) {
                long r = 1;
                for (int i = 2; i <= n; i++) r *= i;
                return r;
            }

            static long lexRank(String s) {
                int n = s.length();
                int[] count = new int[CHAR];
                for (char ch : s.toCharArray()) count[ch]++;
                for (int c = 1; c < CHAR; c++) count[c] += count[c - 1];   // cumulative: count[c] = #chars <= c
                long rank = 1, mul = factorial(n);
                for (int i = 0; i < n - 1; i++) {
                    mul /= n - i;                                    // (n - i - 1)!
                    int c = s.charAt(i);
                    rank += count[c - 1] * mul;                      // unused chars smaller than s[i]
                    for (int j = c; j < CHAR; j++) count[j]--;       // s[i] is used up now
                }
                return rank;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"ABC", "BAC", "CBA", "STRING"})
                    System.out.println(s + " → " + lexRank(s));
            }
        }
    ''', js=r'''
        const CHAR = 256;

        function factorial(n) {
            let r = 1;
            for (let i = 2; i <= n; i++) r *= i;
            return r;
        }

        function lexRank(s) {
            const n = s.length;
            const count = new Array(CHAR).fill(0);
            for (const ch of s) count[ch.charCodeAt(0)]++;
            for (let c = 1; c < CHAR; c++) count[c] += count[c - 1];   // cumulative: count[c] = #chars <= c
            let rank = 1, mul = factorial(n);
            for (let i = 0; i < n - 1; i++) {
                mul /= n - i;                                    // (n - i - 1)!  (exact: mul is a multiple)
                const c = s.charCodeAt(i);
                rank += count[c - 1] * mul;                      // unused chars smaller than s[i]
                for (let j = c; j < CHAR; j++) count[j]--;       // s[i] is used up now
            }
            return rank;
        }

        for (const s of ["ABC", "BAC", "CBA", "STRING"])
            console.log(s, "→", lexRank(s));
    ''')
    yield complexity("O(n · CHAR)", "O(CHAR)")
    yield pitfall("This formula assumes **distinct characters**. With repeats (`\"AAB\"`) the count of permutations starting with a smaller character must be divided by the factorials of the repeated characters' counts. Also `n!` overflows a 32-bit `int` from `n = 13` — use 64-bit integers (as above), which last until `n = 20`.")

    # ── Longest distinct substring ─────────────────────────────────────────────
    yield section("Longest substring with distinct characters", "ruler-measure")
    yield io("s = \"abcdabc\"", "4  (\"abcd\")", "s = \"aaa\"", "1", "s = \"geeksforgeeks\"", "7  (\"eksforg\")")
    yield p("Find the length of the longest substring in which no character repeats. The naive version tests every substring; the *better* one notices that once a substring from `i` contains a repeat, no longer substring from `i` can be distinct — so it breaks out of the inner loop.")
    yield snippet("py", r'''
        def longest_distinct_naive(s):                 # O(n^3): every (i, j), each checked in O(n)
            n, best = len(s), 0
            for i in range(n):
                for j in range(i, n):
                    if len(set(s[i:j + 1])) == j - i + 1:
                        best = max(best, j - i + 1)
            return best

        def longest_distinct_better(s):                # O(n^2): extend from i until the first repeat
            n, best = len(s), 0
            for i in range(n):
                seen = set()
                for j in range(i, n):
                    if s[j] in seen:
                        break
                    seen.add(s[j])
                    best = max(best, j - i + 1)
            return best

        print(longest_distinct_naive("abcdabc"), longest_distinct_better("abcdabc"))
        print(longest_distinct_naive("geeksforgeeks"), longest_distinct_better("geeksforgeeks"))
    ''', out="4 4\n7 7", caption="Python — naive O(n³) and better O(n²)")
    yield idea("Sliding window with a **last-seen index** per character. Let `start` be the left end of the current distinct window and let `j` move right. If `s[j]` was last seen at `prev[s[j]] ≥ start`, the window must begin after that occurrence: `start = prev[s[j]] + 1`. Taking `start = max(start, prev[s[j]] + 1)` handles both cases in one line; `j − start + 1` is the length of the longest distinct substring ending at `j`. Each character is visited once.")
    yield diagram('''
        s     :  a  b  c  d  a  b  c
        j = 4 : 'a' last seen at 0 → start = 1, window "bcda" (length 4)
        j = 5 : 'b' last seen at 1 → start = 2, window "cdab" (length 4)
        j = 6 : 'c' last seen at 2 → start = 3, window "dabc" (length 4)
    ''', "The window start only ever moves right")
    yield multi('''
        abcdabc → 4
        aaa → 1
        geeksforgeeks → 7
        abcdefg → 7
    ''', py=r'''
        def longest_distinct(s):
            prev = [-1] * 256                 # last index where each character was seen
            start = 0                         # left end of the current distinct window
            best = 0
            for j, ch in enumerate(s):
                start = max(start, prev[ord(ch)] + 1)   # jump past the previous occurrence
                best = max(best, j - start + 1)
                prev[ord(ch)] = j
            return best

        for s in ["abcdabc", "aaa", "geeksforgeeks", "abcdefg"]:
            print(s, "→", longest_distinct(s))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        using namespace std;

        int longestDistinct(const string& s) {
            int prev[256];
            fill(prev, prev + 256, -1);                  // last index where each character was seen
            int start = 0, best = 0;                     // start = left end of the current distinct window
            int n = s.size();
            for (int j = 0; j < n; j++) {
                unsigned char ch = s[j];
                start = max(start, prev[ch] + 1);        // jump past the previous occurrence
                best = max(best, j - start + 1);
                prev[ch] = j;
            }
            return best;
        }

        int main() {
            for (string s : {"abcdabc", "aaa", "geeksforgeeks", "abcdefg"})
                cout << s << " → " << longestDistinct(s) << "\n";
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static int longestDistinct(String s) {
                int[] prev = new int[256];
                Arrays.fill(prev, -1);                       // last index where each character was seen
                int start = 0, best = 0;                     // start = left end of the current distinct window
                for (int j = 0; j < s.length(); j++) {
                    char ch = s.charAt(j);
                    start = Math.max(start, prev[ch] + 1);   // jump past the previous occurrence
                    best = Math.max(best, j - start + 1);
                    prev[ch] = j;
                }
                return best;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"abcdabc", "aaa", "geeksforgeeks", "abcdefg"})
                    System.out.println(s + " → " + longestDistinct(s));
            }
        }
    ''', js=r'''
        function longestDistinct(s) {
            const prev = new Array(256).fill(-1);            // last index where each character was seen
            let start = 0, best = 0;                         // start = left end of the current distinct window
            for (let j = 0; j < s.length; j++) {
                const ch = s.charCodeAt(j);
                start = Math.max(start, prev[ch] + 1);       // jump past the previous occurrence
                best = Math.max(best, j - start + 1);
                prev[ch] = j;
            }
            return best;
        }

        for (const s of ["abcdabc", "aaa", "geeksforgeeks", "abcdefg"])
            console.log(s, "→", longestDistinct(s));
    ''')
    yield complexity("O(n)", "O(CHAR)")
    yield pitfall("Writing `start = prev[ch] + 1` without the `max` is wrong: a repeat that lies *before* the current window (`prev[ch] < start`) must not pull `start` backwards. In `\"abba\"` at `j = 3` the earlier `a` is at 0, but the window already starts at 2.")

    yield section("Interview Q&A", "message-question")
    yield qa("KMP or Rabin–Karp — when do you pick which?",
             "KMP gives a guaranteed `O(n + m)` for one pattern and is the safe default. Rabin–Karp shines when you search for **many patterns of the same length** at once (hash each pattern into a set, then one rolling pass over the text), or for 2-D / plagiarism-style matching where hashes of many windows must be compared. Its worst case is `O(n · m)`, so it is a poor fit for adversarial inputs.")
    yield qa("What exactly does lps[i] mean, and why is it the right amount to fall back?",
             "`lps[i]` is the length of the longest *proper* prefix of `pat[0..i]` that is also a suffix of it. On a mismatch after matching `j` characters, the text we just consumed ends with `pat[0..j−1]`; its longest proper prefix-suffix (`lps[j−1]` characters) is the longest stretch of that text that could still be the *beginning* of a match. Anything longer is ruled out by maximality, and anything shorter would skip a possible match — so `lps[j−1]` is exactly the safe shift.")
    yield qa("Why is KMP O(n + m) when it has a loop that does not advance i?",
             "Charge each iteration to either `i` or `j`. Iterations that match advance `i` (at most `n` of them). Iterations that fall back strictly decrease `j`, and `j` only grows together with `i`, so there can be at most `n` fall-backs in total. The LPS construction is the same argument over `m`.")
    yield qa("The Rabin–Karp hash matched but the strings differ — is the algorithm wrong?",
             "No, that is a **spurious hit**, expected behaviour of any hash modulo `q`. Correctness comes from the character-by-character verification that runs only when hashes agree; the hash merely filters candidates. Pick a large prime (and 64-bit arithmetic) so spurious hits are rare, which keeps the *expected* time linear.")
    yield qa("How would you return the anagram positions instead of Yes/No, and the substring instead of the length?",
             "Anagram search: whenever `ct == cp` for the window starting at `i − m`, record `i − m` and continue instead of returning. Longest distinct substring: whenever `j − start + 1` improves `best`, also remember `start`; the answer is `s[start..start+best−1]`. Both keep the same complexity.")
    yield qa("Lexicographic rank with repeated characters?",
             "Permutations with repeats are counted by the multinomial `n! / (c1! · c2! · …)`. At position `i`, for each unused character smaller than `s[i]`, add `(n − i − 1)! / Π(count of each remaining character)!` where that character's count is reduced by one. Same scan, one extra division per step; precompute factorials once.")
