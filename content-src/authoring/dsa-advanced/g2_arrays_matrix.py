from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Arrays, Bits & Recursion"


@topic(G, "list", "List", "list-numbers")
def _():
    yield lead("A list (Python's dynamic array) is the input of most interview problems. These notes collect the classic array problems and the handful of patterns — running minimum, prefix sums, two pointers, sliding window, Kadane's running best, difference arrays, majority voting — that turn the obvious `O(n²)` double loop into a single `O(n)` pass.")
    yield define("Array / list", "a contiguous block of elements addressed by index. `arr[i]` costs `O(1)`; appending at the end is amortised `O(1)`; inserting or deleting anywhere else shifts everything after it — `O(n)`.")
    yield diagram('''
        index:   0    1    2    3    4    5    6
               ┌────┬────┬────┬────┬────┬────┬────┐
        arr:   │ 2  │ 3  │ 10 │ 6  │ 4  │ 8  │ 1  │     n = 7
               └────┴────┴────┴────┴────┴────┴────┘
        subarray arr[2..4] = 10 6 4   (contiguous)      subsequence 2 10 1 (not contiguous)
    ''', "Vocabulary: a *subarray* is contiguous; a *subsequence* keeps order but may skip")

    yield section("The patterns behind every solution", "bulb")
    yield p("Almost every naive solution below fixes a left end `i` and scans every right end `j` — `n(n-1)/2` pairs, hence `O(n²)`. The efficient solution replaces the inner scan with something that is already known when we reach `j`: the minimum so far, a prefix sum, the best subarray ending here. One pass, `O(n)`.")
    yield table(
        ["Pattern", "What you carry while scanning", "Problems"],
        ["Running min / max", "The best `arr[i]` seen so far — the inner loop over `i < j` disappears", "Maximum difference, trapping rain water"],
        ["Greedy local steps", "Add every upward step; the sum of steps equals the best transaction set", "Stock buy and sell"],
        ["Kadane (running best ending here)", "`maxEnding = max(maxEnding + x, x)` — extend or restart", "Maximum subarray sum, circular sum, even-odd subarray"],
        ["Sliding window", "The sum of the last `k` elements: add the new one, drop the old one", "Max sum of `k` consecutive"],
        ["Two pointers", "A window `[s, i]` that grows at the right and shrinks at the left", "Subarray with given sum"],
        ["Prefix sum", "`psum[i]` = sum of `arr[0..i]`, so any range sum is one subtraction", "Range sum queries, equilibrium point"],
        ["Difference array", "`+1` at `left`, `-1` at `right+1`; a prefix sum turns it into counts", "Maximum appearing element in ranges"],
        ["Boyer–Moore voting", "A candidate and a counter; every mismatch cancels one vote", "Majority element"],
        ["Reversal", "Three reversals rotate in place", "Left rotate by `d`"],
    )

    # ── Left rotate by d ───────────────────────────────────────────────
    yield section("Left rotate by d places", "rotate")
    yield io("arr = [1, 2, 3, 4, 5], d = 2", "3 4 5 1 2", "arr = [10, 20, 30], d = 1", "20 30 10")
    yield p("Python can do this in one line with slicing or `deque.rotate`, both `O(n)` but using `O(n)` extra space. Popping from the front `d` times is `O(n · d)` because every `pop(0)` shifts the whole list.")
    yield snippet("py", r'''
        from collections import deque

        l = [10, 20, 30, 40, 50]
        d = 2
        print(*(l[d:] + l[:d]))        # slicing: new list, O(n) space

        dq = deque(l)
        dq.rotate(-d)                  # negative = left rotation
        print(*dq)

        def left_rotate_slow(l, d):    # O(n * d): pop(0) shifts every element
            for _ in range(d):
                l.append(l.pop(0))
        left_rotate_slow(l, d)
        print(*l)
    ''', out='''
        30 40 50 10 20
        30 40 50 10 20
        30 40 50 10 20
    ''')
    yield idea("**Reversal algorithm.** Reverse the first `d` elements, reverse the remaining `n-d`, then reverse the whole array. Each element is touched a constant number of times and nothing is copied: `O(n)` time, `O(1)` space.")
    yield diagram('''
        1 2 3 4 5     d = 2
        2 1 | 3 4 5   reverse arr[0..d-1]
        2 1 | 5 4 3   reverse arr[d..n-1]
        3 4 5 1 2     reverse arr[0..n-1]
    ''', "Three reversals rotate left by d")
    yield multi('''
        3 4 5 1 2
        20 30 10
    ''', py=r'''
        def reverse_range(arr, b, e):
            while b < e:
                arr[b], arr[e] = arr[e], arr[b]
                b += 1
                e -= 1

        def left_rotate(arr, d):
            n = len(arr)
            d %= n                        # rotating by n is a no-op
            reverse_range(arr, 0, d - 1)  # 2 1 | 3 4 5
            reverse_range(arr, d, n - 1)  # 2 1 | 5 4 3
            reverse_range(arr, 0, n - 1)  # 3 4 5 1 2

        for arr, d in (([1, 2, 3, 4, 5], 2), ([10, 20, 30], 1)):
            left_rotate(arr, d)
            print(*arr)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <utility>
        using namespace std;

        void reverseRange(vector<int>& arr, int b, int e) {
            while (b < e) swap(arr[b++], arr[e--]);
        }

        void leftRotate(vector<int>& arr, int d) {
            int n = arr.size();
            d %= n;                        // rotating by n is a no-op
            reverseRange(arr, 0, d - 1);   // 2 1 | 3 4 5
            reverseRange(arr, d, n - 1);   // 2 1 | 5 4 3
            reverseRange(arr, 0, n - 1);   // 3 4 5 1 2
        }

        int main() {
            vector<int> a = {1, 2, 3, 4, 5}, b = {10, 20, 30};
            leftRotate(a, 2);
            leftRotate(b, 1);
            for (int x : a) cout << x << " ";
            cout << "\n";
            for (int x : b) cout << x << " ";
            cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static void reverseRange(int[] arr, int b, int e) {
                while (b < e) { int t = arr[b]; arr[b] = arr[e]; arr[e] = t; b++; e--; }
            }

            static void leftRotate(int[] arr, int d) {
                int n = arr.length;
                d %= n;                        // rotating by n is a no-op
                reverseRange(arr, 0, d - 1);   // 2 1 | 3 4 5
                reverseRange(arr, d, n - 1);   // 2 1 | 5 4 3
                reverseRange(arr, 0, n - 1);   // 3 4 5 1 2
            }

            static void print(int[] arr) {
                StringBuilder sb = new StringBuilder();
                for (int x : arr) sb.append(x).append(' ');
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) {
                int[] a = {1, 2, 3, 4, 5}, b = {10, 20, 30};
                leftRotate(a, 2);
                leftRotate(b, 1);
                print(a);
                print(b);
            }
        }
    ''', js=r'''
        function reverseRange(arr, b, e) {
            while (b < e) { [arr[b], arr[e]] = [arr[e], arr[b]]; b++; e--; }
        }

        function leftRotate(arr, d) {
            const n = arr.length;
            d %= n;                        // rotating by n is a no-op
            reverseRange(arr, 0, d - 1);   // 2 1 | 3 4 5
            reverseRange(arr, d, n - 1);   // 2 1 | 5 4 3
            reverseRange(arr, 0, n - 1);   // 3 4 5 1 2
        }

        for (const [arr, d] of [[[1, 2, 3, 4, 5], 2], [[10, 20, 30], 1]]) {
            leftRotate(arr, d);
            console.log(arr.join(" "));
        }
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("A right rotation by `d` is a left rotation by `n - d`. Always reduce `d % n` first — `d` may be larger than `n`.")

    # ── Maximum difference ────────────────────────────────────────────
    yield section("Maximum difference", "arrows-diff")
    yield p("Find the maximum value of `arr[j] - arr[i]` with `i < j` (buy once, sell once later).")
    yield io("arr = [2, 3, 10, 6, 4, 8, 1]", "8", "arr = [7, 9, 5, 6, 3, 2]", "2", "arr = [30, 20, 10]", "-10")
    yield p("The naive solution tries every pair `(i, j)` — `O(n²)`:")
    yield snippet("py", r'''
        def max_diff_naive(arr):
            n = len(arr)
            res = arr[1] - arr[0]
            for i in range(n - 1):
                for j in range(i + 1, n):          # every pair i < j
                    res = max(res, arr[j] - arr[i])
            return res

        print(max_diff_naive([2, 3, 10, 6, 4, 8, 1]))
    ''', out="8")
    yield idea("For a fixed `j`, the best `i` is simply the **minimum element before `j`**. Carry that minimum while scanning left to right: at each `j` compute `arr[j] - minSoFar`, then update the minimum. The inner loop collapses into one variable.")
    yield multi('''
        8
        2
        -10
    ''', py=r'''
        def max_diff(arr):
            res = arr[1] - arr[0]
            min_val = arr[0]                     # smallest element before j
            for j in range(1, len(arr)):
                res = max(res, arr[j] - min_val)
                min_val = min(min_val, arr[j])   # update AFTER using it (i must be < j)
            return res

        for arr in ([2, 3, 10, 6, 4, 8, 1], [7, 9, 5, 6, 3, 2], [30, 20, 10]):
            print(max_diff(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int maxDiff(const vector<int>& arr) {
            int n = arr.size();
            int res = arr[1] - arr[0];
            int minVal = arr[0];                     // smallest element before j
            for (int j = 1; j < n; j++) {
                res = max(res, arr[j] - minVal);
                minVal = min(minVal, arr[j]);        // update AFTER using it (i must be < j)
            }
            return res;
        }

        int main() {
            vector<vector<int>> tests = {{2, 3, 10, 6, 4, 8, 1}, {7, 9, 5, 6, 3, 2}, {30, 20, 10}};
            for (auto& arr : tests) cout << maxDiff(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxDiff(int[] arr) {
                int res = arr[1] - arr[0];
                int minVal = arr[0];                     // smallest element before j
                for (int j = 1; j < arr.length; j++) {
                    res = Math.max(res, arr[j] - minVal);
                    minVal = Math.min(minVal, arr[j]);   // update AFTER using it (i must be < j)
                }
                return res;
            }

            public static void main(String[] args) {
                int[][] tests = {{2, 3, 10, 6, 4, 8, 1}, {7, 9, 5, 6, 3, 2}, {30, 20, 10}};
                for (int[] arr : tests) System.out.println(maxDiff(arr));
            }
        }
    ''', js=r'''
        function maxDiff(arr) {
            let res = arr[1] - arr[0];
            let minVal = arr[0];                     // smallest element before j
            for (let j = 1; j < arr.length; j++) {
                res = Math.max(res, arr[j] - minVal);
                minVal = Math.min(minVal, arr[j]);   // update AFTER using it (i must be < j)
            }
            return res;
        }

        for (const arr of [[2, 3, 10, 6, 4, 8, 1], [7, 9, 5, 6, 3, 2], [30, 20, 10]])
            console.log(maxDiff(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Initialise `res` with `arr[1] - arr[0]`, not `0` — for a strictly decreasing array the answer is negative. Also update `min_val` *after* computing the difference, or you allow `i == j`.")

    # ── Stock buy and sell ────────────────────────────────────────────
    yield section("Stock buy and sell", "coin")
    yield p("Given daily prices, buy and sell any number of times (one share at a time, sell before buying again). Maximise the total profit.")
    yield io("price = [1, 5, 3, 8, 12]", "13", "price = [30, 20, 10]", "0", "price = [1, 2, 3, 4]", "3")
    yield p("The naive idea considers every pair `(i, j)` with `price[j] > price[i]` as one transaction and recurses on both sides: `profit = (price[j] - price[i]) + maxProfit(0, i-1) + maxProfit(j+1, n-1)`. For `[1, 5, 3, 8, 12]` the pair `(1, 5)` gives `4 + 0 + 9 = 13`. It is exponential.")
    yield snippet("py", r'''
        def max_profit_naive(price, b, e):
            if e <= b:
                return 0
            res = 0
            for i in range(b, e):
                for j in range(i + 1, e + 1):
                    if price[j] > price[i]:
                        curr = (price[j] - price[i]
                                + max_profit_naive(price, b, i - 1)
                                + max_profit_naive(price, j + 1, e))
                        res = max(res, curr)
            return res

        print(max_profit_naive([1, 5, 3, 8, 12], 0, 4))
    ''', out="13")
    yield idea("Every rise `price[i] > price[i-1]` can be collected on its own: buying at the bottom and selling at the top of a rising run equals the sum of its daily rises. So just **add every positive day-to-day difference** — a greedy one-pass solution.")
    yield diagram('''
        price:  1   5   3   8   12
        rises:   +4  -2  +5  +4        collect the rises: 4 + 5 + 4 = 13
    ''', "Local rises sum to the optimal profit")
    yield multi('''
        13
        0
        3
    ''', py=r'''
        def max_profit(price):
            profit = 0
            for i in range(1, len(price)):
                if price[i] > price[i - 1]:          # a rise: buy yesterday, sell today
                    profit += price[i] - price[i - 1]
            return profit

        for price in ([1, 5, 3, 8, 12], [30, 20, 10], [1, 2, 3, 4]):
            print(max_profit(price))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int maxProfit(const vector<int>& price) {
            int n = price.size();
            int profit = 0;
            for (int i = 1; i < n; i++)
                if (price[i] > price[i - 1])             // a rise: buy yesterday, sell today
                    profit += price[i] - price[i - 1];
            return profit;
        }

        int main() {
            vector<vector<int>> tests = {{1, 5, 3, 8, 12}, {30, 20, 10}, {1, 2, 3, 4}};
            for (auto& price : tests) cout << maxProfit(price) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxProfit(int[] price) {
                int profit = 0;
                for (int i = 1; i < price.length; i++)
                    if (price[i] > price[i - 1])             // a rise: buy yesterday, sell today
                        profit += price[i] - price[i - 1];
                return profit;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 5, 3, 8, 12}, {30, 20, 10}, {1, 2, 3, 4}};
                for (int[] price : tests) System.out.println(maxProfit(price));
            }
        }
    ''', js=r'''
        function maxProfit(price) {
            let profit = 0;
            for (let i = 1; i < price.length; i++)
                if (price[i] > price[i - 1])             // a rise: buy yesterday, sell today
                    profit += price[i] - price[i - 1];
            return profit;
        }

        for (const price of [[1, 5, 3, 8, 12], [30, 20, 10], [1, 2, 3, 4]])
            console.log(maxProfit(price));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("With **one** transaction only, the problem becomes *maximum difference* above (clamped at 0). With at most `k` transactions it needs dynamic programming.")

    # ── Trapping rain water ───────────────────────────────────────────
    yield section("Trapping rain water", "droplet")
    yield p("`arr[i]` is the height of bar `i`. How much water is trapped between the bars after rain?")
    yield io("arr = [3, 0, 1, 2, 5]", "6", "arr = [2, 0, 2]", "2", "arr = [1, 2, 3]", "0", "arr = [3, 2, 1]", "0")
    yield diagram('''
                    █
                    █
        █     ~  ~  █          water over bar i = min(highest bar on the left,
        █  ~  ~  █  █                                 highest bar on the right) - arr[i]
        █  ~  █  █  █
        3  0  1  2  5          3 + 2 + 1 = 6
    ''', "Each column holds water up to the lower of its two surrounding maxima")
    yield p("The water above bar `i` is `min(lmax, rmax) - arr[i]`, where `lmax` is the tallest bar at or left of `i` and `rmax` the tallest at or right of it. The naive solution recomputes both maxima for every `i` — `O(n²)`:")
    yield snippet("py", r'''
        def get_water_naive(arr):
            n, res = len(arr), 0
            for i in range(1, n - 1):
                lmax = max(arr[:i + 1])           # O(n) scan to the left
                rmax = max(arr[i:])               # O(n) scan to the right
                res += min(lmax, rmax) - arr[i]
            return res

        print(get_water_naive([3, 0, 1, 2, 5]))
    ''', out="6")
    yield idea("Precompute `lmax[i]` (prefix maximum) in one left-to-right pass and `rmax[i]` (suffix maximum) in one right-to-left pass. Then every `min(lmax[i], rmax[i]) - arr[i]` is `O(1)`: three passes, `O(n)` time, `O(n)` space.")
    yield multi('''
        6
        2
        0
        0
    ''', py=r'''
        def get_water(arr):
            n = len(arr)
            if n < 3:
                return 0
            lmax = [0] * n                       # lmax[i] = max(arr[0..i])
            rmax = [0] * n                       # rmax[i] = max(arr[i..n-1])
            lmax[0] = arr[0]
            for i in range(1, n):
                lmax[i] = max(lmax[i - 1], arr[i])
            rmax[n - 1] = arr[n - 1]
            for i in range(n - 2, -1, -1):
                rmax[i] = max(rmax[i + 1], arr[i])
            res = 0
            for i in range(1, n - 1):            # the two end bars never hold water
                res += min(lmax[i], rmax[i]) - arr[i]
            return res

        for arr in ([3, 0, 1, 2, 5], [2, 0, 2], [1, 2, 3], [3, 2, 1]):
            print(get_water(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int getWater(const vector<int>& arr) {
            int n = arr.size();
            if (n < 3) return 0;
            vector<int> lmax(n), rmax(n);           // prefix max / suffix max
            lmax[0] = arr[0];
            for (int i = 1; i < n; i++) lmax[i] = max(lmax[i - 1], arr[i]);
            rmax[n - 1] = arr[n - 1];
            for (int i = n - 2; i >= 0; i--) rmax[i] = max(rmax[i + 1], arr[i]);
            int res = 0;
            for (int i = 1; i < n - 1; i++)         // the two end bars never hold water
                res += min(lmax[i], rmax[i]) - arr[i];
            return res;
        }

        int main() {
            vector<vector<int>> tests = {{3, 0, 1, 2, 5}, {2, 0, 2}, {1, 2, 3}, {3, 2, 1}};
            for (auto& arr : tests) cout << getWater(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int getWater(int[] arr) {
                int n = arr.length;
                if (n < 3) return 0;
                int[] lmax = new int[n], rmax = new int[n];   // prefix max / suffix max
                lmax[0] = arr[0];
                for (int i = 1; i < n; i++) lmax[i] = Math.max(lmax[i - 1], arr[i]);
                rmax[n - 1] = arr[n - 1];
                for (int i = n - 2; i >= 0; i--) rmax[i] = Math.max(rmax[i + 1], arr[i]);
                int res = 0;
                for (int i = 1; i < n - 1; i++)                // the two end bars never hold water
                    res += Math.min(lmax[i], rmax[i]) - arr[i];
                return res;
            }

            public static void main(String[] args) {
                int[][] tests = {{3, 0, 1, 2, 5}, {2, 0, 2}, {1, 2, 3}, {3, 2, 1}};
                for (int[] arr : tests) System.out.println(getWater(arr));
            }
        }
    ''', js=r'''
        function getWater(arr) {
            const n = arr.length;
            if (n < 3) return 0;
            const lmax = new Array(n), rmax = new Array(n);   // prefix max / suffix max
            lmax[0] = arr[0];
            for (let i = 1; i < n; i++) lmax[i] = Math.max(lmax[i - 1], arr[i]);
            rmax[n - 1] = arr[n - 1];
            for (let i = n - 2; i >= 0; i--) rmax[i] = Math.max(rmax[i + 1], arr[i]);
            let res = 0;
            for (let i = 1; i < n - 1; i++)                    // the two end bars never hold water
                res += Math.min(lmax[i], rmax[i]) - arr[i];
            return res;
        }

        for (const arr of [[3, 0, 1, 2, 5], [2, 0, 2], [1, 2, 3], [3, 2, 1]])
            console.log(getWater(arr));
    ''')
    yield complexity("O(n)", "O(n)")
    yield p("**Two-pointer refinement, `O(1)` space.** Walk `l` and `r` inwards from both ends. If `arr[l] < arr[r]`, the water above `l` is decided by `lmax` alone (there is certainly a bar at least as tall as `arr[r] > arr[l]` on the right), so settle `l` and move it; otherwise settle `r`.")
    yield multi('''
        6
        2
        0
        0
    ''', py=r'''
        def get_water(arr):
            l, r = 0, len(arr) - 1
            lmax = rmax = 0
            res = 0
            while l < r:
                if arr[l] < arr[r]:              # right side is tall enough: lmax decides
                    lmax = max(lmax, arr[l])
                    res += lmax - arr[l]
                    l += 1
                else:                            # left side is tall enough: rmax decides
                    rmax = max(rmax, arr[r])
                    res += rmax - arr[r]
                    r -= 1
            return res

        for arr in ([3, 0, 1, 2, 5], [2, 0, 2], [1, 2, 3], [3, 2, 1]):
            print(get_water(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int getWater(const vector<int>& arr) {
            int l = 0, r = (int)arr.size() - 1;
            int lmax = 0, rmax = 0, res = 0;
            while (l < r) {
                if (arr[l] < arr[r]) {               // right side is tall enough: lmax decides
                    lmax = max(lmax, arr[l]);
                    res += lmax - arr[l];
                    l++;
                } else {                             // left side is tall enough: rmax decides
                    rmax = max(rmax, arr[r]);
                    res += rmax - arr[r];
                    r--;
                }
            }
            return res;
        }

        int main() {
            vector<vector<int>> tests = {{3, 0, 1, 2, 5}, {2, 0, 2}, {1, 2, 3}, {3, 2, 1}};
            for (auto& arr : tests) cout << getWater(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int getWater(int[] arr) {
                int l = 0, r = arr.length - 1;
                int lmax = 0, rmax = 0, res = 0;
                while (l < r) {
                    if (arr[l] < arr[r]) {               // right side is tall enough: lmax decides
                        lmax = Math.max(lmax, arr[l]);
                        res += lmax - arr[l];
                        l++;
                    } else {                             // left side is tall enough: rmax decides
                        rmax = Math.max(rmax, arr[r]);
                        res += rmax - arr[r];
                        r--;
                    }
                }
                return res;
            }

            public static void main(String[] args) {
                int[][] tests = {{3, 0, 1, 2, 5}, {2, 0, 2}, {1, 2, 3}, {3, 2, 1}};
                for (int[] arr : tests) System.out.println(getWater(arr));
            }
        }
    ''', js=r'''
        function getWater(arr) {
            let l = 0, r = arr.length - 1;
            let lmax = 0, rmax = 0, res = 0;
            while (l < r) {
                if (arr[l] < arr[r]) {               // right side is tall enough: lmax decides
                    lmax = Math.max(lmax, arr[l]);
                    res += lmax - arr[l];
                    l++;
                } else {                             // left side is tall enough: rmax decides
                    rmax = Math.max(rmax, arr[r]);
                    res += rmax - arr[r];
                    r--;
                }
            }
            return res;
        }

        for (const arr of [[3, 0, 1, 2, 5], [2, 0, 2], [1, 2, 3], [3, 2, 1]])
            console.log(getWater(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("The original naive version re-used the loop variable `j` for `rmax = arr[j]` after the first inner loop ended — it happened to equal `arr[i-1]`, which is wrong. Start `rmax` at `arr[i]`, or better, use the prefix/suffix maxima above.")

    # ── Maximum subarray sum (Kadane) ─────────────────────────────────
    yield section("Maximum subarray sum (Kadane's algorithm)", "chart-line")
    yield io("arr = [2, 3, -8, 7, -1, 2, 3]", "11", "arr = [5, 8, 3]", "16", "arr = [-6, -1, -8]", "-1")
    yield p("The naive solution fixes a start `i`, extends the end `j` and keeps a running `curr` sum — `O(n²)` because every start is scanned separately:")
    yield snippet("py", r'''
        def max_sum_naive(arr):
            res = arr[0]
            for i in range(len(arr)):
                curr = 0
                for j in range(i, len(arr)):       # every subarray starting at i
                    curr += arr[j]
                    res = max(res, curr)
            return res

        print(max_sum_naive([2, 3, -8, 7, -1, 2, 3]))
    ''', out="11")
    yield idea("Let `maxEnding` be the best sum of a subarray that **ends at `i`**. It is either the previous best extended by `arr[i]`, or `arr[i]` alone if the previous best had become negative (a negative prefix never helps): `maxEnding = max(maxEnding + arr[i], arr[i])`. The answer is the largest `maxEnding` seen.")
    yield diagram('''
        arr:        2   3  -8   7  -1   2   3
        maxEnding:  2   5  -3   7   6   8  11     ← restart at 7 because -3 + 7 < 7
        res:        2   5   5   7   7   8  11
    ''', "Kadane's running values")
    yield multi('''
        11
        16
        -1
    ''', py=r'''
        def max_sum(arr):
            res = arr[0]
            max_ending = arr[0]                  # best subarray ending at the current index
            for i in range(1, len(arr)):
                max_ending = max(max_ending + arr[i], arr[i])   # extend or restart
                res = max(res, max_ending)
            return res

        for arr in ([2, 3, -8, 7, -1, 2, 3], [5, 8, 3], [-6, -1, -8]):
            print(max_sum(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int maxSum(const vector<int>& arr) {
            int n = arr.size();
            int res = arr[0], maxEnding = arr[0];    // best subarray ending at the current index
            for (int i = 1; i < n; i++) {
                maxEnding = max(maxEnding + arr[i], arr[i]);   // extend or restart
                res = max(res, maxEnding);
            }
            return res;
        }

        int main() {
            vector<vector<int>> tests = {{2, 3, -8, 7, -1, 2, 3}, {5, 8, 3}, {-6, -1, -8}};
            for (auto& arr : tests) cout << maxSum(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxSum(int[] arr) {
                int res = arr[0], maxEnding = arr[0];    // best subarray ending at the current index
                for (int i = 1; i < arr.length; i++) {
                    maxEnding = Math.max(maxEnding + arr[i], arr[i]);   // extend or restart
                    res = Math.max(res, maxEnding);
                }
                return res;
            }

            public static void main(String[] args) {
                int[][] tests = {{2, 3, -8, 7, -1, 2, 3}, {5, 8, 3}, {-6, -1, -8}};
                for (int[] arr : tests) System.out.println(maxSum(arr));
            }
        }
    ''', js=r'''
        function maxSum(arr) {
            let res = arr[0], maxEnding = arr[0];    // best subarray ending at the current index
            for (let i = 1; i < arr.length; i++) {
                maxEnding = Math.max(maxEnding + arr[i], arr[i]);   // extend or restart
                res = Math.max(res, maxEnding);
            }
            return res;
        }

        for (const arr of [[2, 3, -8, 7, -1, 2, 3], [5, 8, 3], [-6, -1, -8]])
            console.log(maxSum(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Initialising `res = 0` returns `0` for an all-negative array instead of `-1`. Start both `res` and `maxEnding` at `arr[0]` — a subarray must contain at least one element.")

    # ── Maximum length even-odd subarray ──────────────────────────────
    yield section("Maximum length even-odd subarray", "arrows-shuffle")
    yield p("Find the longest subarray in which consecutive elements alternate between even and odd.")
    yield io("arr = [10, 12, 14, 7, 8]", "3", "arr = [7, 10, 13, 14]", "4", "arr = [10, 12, 8, 4]", "1")
    yield p("Naively, start at every `i` and extend while the parity keeps alternating — `O(n²)` in the worst case (a fully alternating array).")
    yield idea("Same shape as Kadane: `curr` is the length of the alternating run **ending at `i`**. If `arr[i]` and `arr[i-1]` have different parity, `curr += 1`; otherwise the run breaks and `curr = 1`. Two parities differ exactly when `(arr[i] + arr[i-1]) % 2 == 1`, which also works for negative numbers.")
    yield multi('''
        3
        4
        1
    ''', py=r'''
        def max_even_odd(arr):
            res = curr = 1
            for i in range(1, len(arr)):
                if (arr[i] + arr[i - 1]) % 2 == 1:   # parities differ → run continues
                    curr += 1
                    res = max(res, curr)
                else:
                    curr = 1                         # run breaks
            return res

        for arr in ([10, 12, 14, 7, 8], [7, 10, 13, 14], [10, 12, 8, 4]):
            print(max_even_odd(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int maxEvenOdd(const vector<int>& arr) {
            int n = arr.size();
            int res = 1, curr = 1;
            for (int i = 1; i < n; i++) {
                if ((arr[i] + arr[i - 1]) % 2 != 0) {    // parities differ → run continues
                    curr++;
                    res = max(res, curr);
                } else {
                    curr = 1;                            // run breaks
                }
            }
            return res;
        }

        int main() {
            vector<vector<int>> tests = {{10, 12, 14, 7, 8}, {7, 10, 13, 14}, {10, 12, 8, 4}};
            for (auto& arr : tests) cout << maxEvenOdd(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxEvenOdd(int[] arr) {
                int res = 1, curr = 1;
                for (int i = 1; i < arr.length; i++) {
                    if ((arr[i] + arr[i - 1]) % 2 != 0) {    // parities differ → run continues
                        curr++;
                        res = Math.max(res, curr);
                    } else {
                        curr = 1;                            // run breaks
                    }
                }
                return res;
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 12, 14, 7, 8}, {7, 10, 13, 14}, {10, 12, 8, 4}};
                for (int[] arr : tests) System.out.println(maxEvenOdd(arr));
            }
        }
    ''', js=r'''
        function maxEvenOdd(arr) {
            let res = 1, curr = 1;
            for (let i = 1; i < arr.length; i++) {
                if ((arr[i] + arr[i - 1]) % 2 !== 0) {    // parities differ → run continues
                    curr++;
                    res = Math.max(res, curr);
                } else {
                    curr = 1;                             // run breaks
                }
            }
            return res;
        }

        for (const arr of [[10, 12, 14, 7, 8], [7, 10, 13, 14], [10, 12, 8, 4]])
            console.log(maxEvenOdd(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("In C++, Java and JavaScript `-7 % 2` is `-1`, so testing `arr[i] % 2 == 1` misses negative odd numbers. Compare `% 2 != 0`, or test the parity of the sum as above.")

    # ── Maximum circular subarray sum ─────────────────────────────────
    yield section("Maximum circular subarray sum", "refresh")
    yield p("The array is circular: a subarray may wrap around from the last element to the first. For `[10, 5, -5]` the circular subarrays include `{-5, 10}` and `{5, -5, 10}` as well as the normal ones.")
    yield io("arr = [5, -2, 3, 4]", "12", "arr = [10, 5, -5]", "15", "arr = [-3, -2, -1]", "-1")
    yield p("Naively start at every `i` and extend `n-1` times with the index `(i + j) % n` — `O(n²)`:")
    yield snippet("py", r'''
        def max_circular_naive(arr):
            n = len(arr)
            res = arr[0]
            for i in range(n):
                curr_sum = arr[i]
                curr_max = arr[i]
                for j in range(1, n):
                    curr_sum += arr[(i + j) % n]      # wrap around with modulo
                    curr_max = max(curr_max, curr_sum)
                res = max(res, curr_max)
            return res

        print(max_circular_naive([5, -2, 3, 4]))
    ''', out="12")
    yield idea("The answer is either a **normal** subarray (plain Kadane) or a **wrapping** one. A wrapping subarray is the whole array minus some normal subarray in the middle, so its sum is `total - minSubarraySum`. The minimum subarray sum is Kadane on the negated array (`-maxSum(-arr)`), which is why the original notes flip every sign. If every element is negative, the normal answer is the only valid one.")
    yield diagram('''
        arr:   5  -2   3   4         total = 10
                 └──┘               minimum subarray  = -2
        wrap:  5 ...... 3   4       10 - (-2) = 12 = sum of {3, 4, 5}
    ''', "A wrapping subarray is the complement of a middle subarray")
    yield multi('''
        12
        15
        -1
    ''', py=r'''
        def kadane(arr):
            res = max_ending = arr[0]
            for i in range(1, len(arr)):
                max_ending = max(max_ending + arr[i], arr[i])
                res = max(res, max_ending)
            return res

        def max_circular(arr):
            max_normal = kadane(arr)
            if max_normal < 0:                        # all negative: wrapping cannot help
                return max_normal
            total = sum(arr)
            min_sub = -kadane([-x for x in arr])      # min subarray = -(max subarray of negated)
            max_wrap = total - min_sub
            return max(max_normal, max_wrap)

        for arr in ([5, -2, 3, 4], [10, 5, -5], [-3, -2, -1]):
            print(max_circular(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int kadane(const vector<int>& arr) {
            int n = arr.size();
            int res = arr[0], maxEnding = arr[0];
            for (int i = 1; i < n; i++) {
                maxEnding = max(maxEnding + arr[i], arr[i]);
                res = max(res, maxEnding);
            }
            return res;
        }

        int maxCircular(const vector<int>& arr) {
            int maxNormal = kadane(arr);
            if (maxNormal < 0) return maxNormal;        // all negative: wrapping cannot help
            int total = 0;
            vector<int> neg;
            for (int x : arr) { total += x; neg.push_back(-x); }
            int minSub = -kadane(neg);                  // min subarray = -(max subarray of negated)
            return max(maxNormal, total - minSub);
        }

        int main() {
            vector<vector<int>> tests = {{5, -2, 3, 4}, {10, 5, -5}, {-3, -2, -1}};
            for (auto& arr : tests) cout << maxCircular(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int kadane(int[] arr) {
                int res = arr[0], maxEnding = arr[0];
                for (int i = 1; i < arr.length; i++) {
                    maxEnding = Math.max(maxEnding + arr[i], arr[i]);
                    res = Math.max(res, maxEnding);
                }
                return res;
            }

            static int maxCircular(int[] arr) {
                int maxNormal = kadane(arr);
                if (maxNormal < 0) return maxNormal;        // all negative: wrapping cannot help
                int total = 0;
                int[] neg = new int[arr.length];
                for (int i = 0; i < arr.length; i++) { total += arr[i]; neg[i] = -arr[i]; }
                int minSub = -kadane(neg);                  // min subarray = -(max subarray of negated)
                return Math.max(maxNormal, total - minSub);
            }

            public static void main(String[] args) {
                int[][] tests = {{5, -2, 3, 4}, {10, 5, -5}, {-3, -2, -1}};
                for (int[] arr : tests) System.out.println(maxCircular(arr));
            }
        }
    ''', js=r'''
        function kadane(arr) {
            let res = arr[0], maxEnding = arr[0];
            for (let i = 1; i < arr.length; i++) {
                maxEnding = Math.max(maxEnding + arr[i], arr[i]);
                res = Math.max(res, maxEnding);
            }
            return res;
        }

        function maxCircular(arr) {
            const maxNormal = kadane(arr);
            if (maxNormal < 0) return maxNormal;        // all negative: wrapping cannot help
            const total = arr.reduce((a, b) => a + b, 0);
            const minSub = -kadane(arr.map(x => -x));   // min subarray = -(max subarray of negated)
            return Math.max(maxNormal, total - minSub);
        }

        for (const arr of [[5, -2, 3, 4], [10, 5, -5], [-3, -2, -1]])
            console.log(maxCircular(arr));
    ''')
    yield complexity("O(n)", "O(n) for the negated copy — O(1) if you run a min-Kadane instead")
    yield pitfall("Without the all-negative check, `total - minSub` would be `0` (the empty complement) for `[-3, -2, -1]` and beat the correct `-1`.")

    # ── Majority element ──────────────────────────────────────────────
    yield section("Majority element (Boyer–Moore voting)", "users")
    yield p("A majority element appears **more than `n/2`** times. Return it, or report that there is none.")
    yield io("arr = [8, 3, 4, 8, 8]", "8", "arr = [3, 7, 4, 7, 7, 5]", "none", "arr = [2, 2, 1, 1, 1, 2, 2]", "2")
    yield p("Naively count every element with an inner loop — `O(n²)`. A hash map of counts gives `O(n)` time but `O(n)` space. Boyer–Moore does it in `O(1)` space.")
    yield idea("Keep a `candidate` and a `count`. Each equal element adds a vote, each different element cancels one; when the count reaches `0`, the next element becomes the candidate. A true majority has more votes than everything else combined, so it can never be cancelled out completely — it must be the final candidate. The candidate is only a *possibility* when no majority exists, so a second pass **verifies** its count.")
    yield diagram('''
        arr:        8   3   4   8   8
        candidate:  8   8   4   4   8      count hits 0 after 3, 4 takes over, hits 0 after 8
        count:      1   0   1   0   1
        verify: 8 appears 3 times > 5/2 → majority
    ''', "Voting on [8, 3, 4, 8, 8]")
    yield multi('''
        8
        none
        2
    ''', py=r'''
        def majority(arr):
            n = len(arr)
            cand, count = arr[0], 1
            for i in range(1, n):                 # pass 1: find the only possible candidate
                if arr[i] == cand:
                    count += 1
                else:
                    count -= 1
                if count == 0:
                    cand, count = arr[i], 1
            if arr.count(cand) > n // 2:          # pass 2: verify
                return str(cand)
            return "none"

        for arr in ([8, 3, 4, 8, 8], [3, 7, 4, 7, 7, 5], [2, 2, 1, 1, 1, 2, 2]):
            print(majority(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <string>
        using namespace std;

        string majority(const vector<int>& arr) {
            int n = arr.size();
            int cand = arr[0], count = 1;
            for (int i = 1; i < n; i++) {                 // pass 1: find the only possible candidate
                if (arr[i] == cand) count++;
                else count--;
                if (count == 0) { cand = arr[i]; count = 1; }
            }
            int freq = 0;
            for (int x : arr) if (x == cand) freq++;      // pass 2: verify
            return freq > n / 2 ? to_string(cand) : "none";
        }

        int main() {
            vector<vector<int>> tests = {{8, 3, 4, 8, 8}, {3, 7, 4, 7, 7, 5}, {2, 2, 1, 1, 1, 2, 2}};
            for (auto& arr : tests) cout << majority(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static String majority(int[] arr) {
                int n = arr.length;
                int cand = arr[0], count = 1;
                for (int i = 1; i < n; i++) {                 // pass 1: find the only possible candidate
                    if (arr[i] == cand) count++;
                    else count--;
                    if (count == 0) { cand = arr[i]; count = 1; }
                }
                int freq = 0;
                for (int x : arr) if (x == cand) freq++;      // pass 2: verify
                return freq > n / 2 ? String.valueOf(cand) : "none";
            }

            public static void main(String[] args) {
                int[][] tests = {{8, 3, 4, 8, 8}, {3, 7, 4, 7, 7, 5}, {2, 2, 1, 1, 1, 2, 2}};
                for (int[] arr : tests) System.out.println(majority(arr));
            }
        }
    ''', js=r'''
        function majority(arr) {
            const n = arr.length;
            let cand = arr[0], count = 1;
            for (let i = 1; i < n; i++) {                 // pass 1: find the only possible candidate
                if (arr[i] === cand) count++;
                else count--;
                if (count === 0) { cand = arr[i]; count = 1; }
            }
            let freq = 0;
            for (const x of arr) if (x === cand) freq++;  // pass 2: verify
            return freq > Math.floor(n / 2) ? String(cand) : "none";
        }

        for (const arr of [[8, 3, 4, 8, 8], [3, 7, 4, 7, 7, 5], [2, 2, 1, 1, 1, 2, 2]])
            console.log(majority(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Skipping the verification pass returns a wrong answer for `[3, 7, 4, 7, 7, 5]` — the first pass ends with candidate `5`, which is not a majority. The original notes returned an *index* of the majority element; any index holding the value is acceptable, so these notes return the value.")

    # ── Minimum group flips ───────────────────────────────────────────
    yield section("Minimum group flips to make a binary array uniform", "toggle-left")
    yield p("A binary array has alternating *groups* of equal bits. Flip the fewest groups so that every element becomes the same, and print the groups to flip.")
    yield io("arr = [1, 1, 0, 0, 0, 1]", "From 2 to 4", "arr = [1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1]", "From 1 to 3; From 5 to 6", "arr = [1, 1, 1]", "nothing to flip", "arr = [0, 1]", "From 1 to 1")
    yield idea("Groups alternate `0,1,0,1,…`, so the number of `0`-groups and `1`-groups differ by at most one — and when they differ, the kind of the **first** group is the more frequent one. Therefore flipping every group that differs from `arr[0]` is always optimal, and it needs one pass: a group of the other kind starts when `arr[i] != arr[i-1]` and `arr[i] != arr[0]`, and ends just before the next change.")
    yield diagram('''
        index: 0 1 2 3 4 5 6 7 8 9 10
        arr:   1 0 0 0 1 0 0 1 1 1 1
               ─ ───── ─ ─── ───────
        groups:1   0   1  0     1        groups ≠ arr[0]: [1..3] and [5..6] → 2 flips
    ''', "Flip the groups that differ from the first element")
    yield multi('''
        1 1 0 0 0 1 -> From 2 to 4
        1 0 0 0 1 0 0 1 1 1 1 -> From 1 to 3; From 5 to 6
        1 1 1 -> nothing to flip
        0 1 -> From 1 to 1
    ''', py=r'''
        def group_flips(arr):
            n = len(arr)
            groups = []
            start = 0
            for i in range(1, n):
                if arr[i] != arr[i - 1]:               # a group boundary
                    if arr[i] != arr[0]:
                        start = i                      # a group of the other kind begins
                    else:
                        groups.append(f"From {start} to {i - 1}")   # ... and ends
            if arr[n - 1] != arr[0]:                   # last group was never closed
                groups.append(f"From {start} to {n - 1}")
            return "; ".join(groups) if groups else "nothing to flip"

        for arr in ([1, 1, 0, 0, 0, 1], [1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1], [1, 1, 1], [0, 1]):
            print(*arr, "->", group_flips(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <string>
        using namespace std;

        string groupFlips(const vector<int>& arr) {
            int n = arr.size();
            string res;
            int start = 0;
            auto add = [&](int a, int b) {
                if (!res.empty()) res += "; ";
                res += "From " + to_string(a) + " to " + to_string(b);
            };
            for (int i = 1; i < n; i++) {
                if (arr[i] != arr[i - 1]) {                // a group boundary
                    if (arr[i] != arr[0]) start = i;       // a group of the other kind begins
                    else add(start, i - 1);                // ... and ends
                }
            }
            if (arr[n - 1] != arr[0]) add(start, n - 1);   // last group was never closed
            return res.empty() ? "nothing to flip" : res;
        }

        int main() {
            vector<vector<int>> tests = {{1, 1, 0, 0, 0, 1}, {1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1}, {1, 1, 1}, {0, 1}};
            for (auto& arr : tests) {
                for (int x : arr) cout << x << " ";
                cout << "-> " << groupFlips(arr) << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static String groupFlips(int[] arr) {
                int n = arr.length;
                StringBuilder res = new StringBuilder();
                int start = 0;
                for (int i = 1; i < n; i++) {
                    if (arr[i] != arr[i - 1]) {                // a group boundary
                        if (arr[i] != arr[0]) start = i;       // a group of the other kind begins
                        else add(res, start, i - 1);           // ... and ends
                    }
                }
                if (arr[n - 1] != arr[0]) add(res, start, n - 1);   // last group was never closed
                return res.length() == 0 ? "nothing to flip" : res.toString();
            }

            static void add(StringBuilder res, int a, int b) {
                if (res.length() > 0) res.append("; ");
                res.append("From ").append(a).append(" to ").append(b);
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 1, 0, 0, 0, 1}, {1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1}, {1, 1, 1}, {0, 1}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : arr) sb.append(x).append(' ');
                    System.out.println(sb + "-> " + groupFlips(arr));
                }
            }
        }
    ''', js=r'''
        function groupFlips(arr) {
            const n = arr.length;
            const groups = [];
            let start = 0;
            for (let i = 1; i < n; i++) {
                if (arr[i] !== arr[i - 1]) {               // a group boundary
                    if (arr[i] !== arr[0]) start = i;      // a group of the other kind begins
                    else groups.push(`From ${start} to ${i - 1}`);   // ... and ends
                }
            }
            if (arr[n - 1] !== arr[0]) groups.push(`From ${start} to ${n - 1}`);   // never closed
            return groups.length ? groups.join("; ") : "nothing to flip";
        }

        for (const arr of [[1, 1, 0, 0, 0, 1], [1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1], [1, 1, 1], [0, 1]])
            console.log(arr.join(" ") + " -> " + groupFlips(arr));
    ''')
    yield complexity("O(n)", "O(1) besides the output")
    yield pitfall("Do not forget the check after the loop: when the array ends inside a group of the other kind (`[1, 1, 0, 0, 0]`) that group has no closing boundary. The original notes listed `From 0 to 0; From 1 to 1` for `[0, 1]` — flipping both groups is not minimal; one flip (`From 1 to 1`) suffices.")

    # ── Sliding window ────────────────────────────────────────────────
    yield section("Sliding window: maximum sum of k consecutive elements", "layout-columns")
    yield io("arr = [1, 8, 30, -5, 20, 7], k = 3", "45", "arr = [5, -10, 6, 90, 3], k = 2", "96")
    yield p("Naively sum each of the `n - k + 1` windows from scratch — `O(n · k)`:")
    yield snippet("py", r'''
        def max_k_sum_naive(arr, k):
            res = float("-inf")
            for i in range(len(arr) - k + 1):
                curr = sum(arr[i:i + k])          # O(k) per window
                res = max(res, curr)
            return res

        print(max_k_sum_naive([1, 8, 30, -5, 20, 7], 3))
    ''', out="45")
    yield idea("Consecutive windows overlap in `k - 1` elements. Sliding the window one step right **adds `arr[i]` and removes `arr[i-k]`** — `O(1)` per step instead of `O(k)`.")
    yield diagram('''
        arr:   1   8  30  -5  20   7      k = 3
              [1   8  30]                 39
                  [8  30  -5]             39 + (-5) - 1  = 33
                     [30  -5  20]         33 + 20  - 8  = 45  ← max
                         [-5  20   7]     45 + 7   - 30 = 22
    ''', "Each slide adds the entering element and subtracts the leaving one")
    yield multi('''
        45
        96
    ''', py=r'''
        def max_k_sum(arr, k):
            curr = sum(arr[:k])                  # first window
            res = curr
            for i in range(k, len(arr)):
                curr += arr[i] - arr[i - k]      # slide: add entering, drop leaving
                res = max(res, curr)
            return res

        print(max_k_sum([1, 8, 30, -5, 20, 7], 3))
        print(max_k_sum([5, -10, 6, 90, 3], 2))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int maxKSum(const vector<int>& arr, int k) {
            int n = arr.size();
            int curr = 0;
            for (int i = 0; i < k; i++) curr += arr[i];     // first window
            int res = curr;
            for (int i = k; i < n; i++) {
                curr += arr[i] - arr[i - k];                // slide: add entering, drop leaving
                res = max(res, curr);
            }
            return res;
        }

        int main() {
            cout << maxKSum({1, 8, 30, -5, 20, 7}, 3) << "\n";
            cout << maxKSum({5, -10, 6, 90, 3}, 2) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxKSum(int[] arr, int k) {
                int curr = 0;
                for (int i = 0; i < k; i++) curr += arr[i];     // first window
                int res = curr;
                for (int i = k; i < arr.length; i++) {
                    curr += arr[i] - arr[i - k];                // slide: add entering, drop leaving
                    res = Math.max(res, curr);
                }
                return res;
            }

            public static void main(String[] args) {
                System.out.println(maxKSum(new int[]{1, 8, 30, -5, 20, 7}, 3));
                System.out.println(maxKSum(new int[]{5, -10, 6, 90, 3}, 2));
            }
        }
    ''', js=r'''
        function maxKSum(arr, k) {
            let curr = 0;
            for (let i = 0; i < k; i++) curr += arr[i];     // first window
            let res = curr;
            for (let i = k; i < arr.length; i++) {
                curr += arr[i] - arr[i - k];                // slide: add entering, drop leaving
                res = Math.max(res, curr);
            }
            return res;
        }

        console.log(maxKSum([1, 8, 30, -5, 20, 7], 3));
        console.log(maxKSum([5, -10, 6, 90, 3], 2));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Fixed-size windows work for any associative, invertible aggregate (sum, count, XOR). For *maximum* in a window you need a monotonic deque instead — subtraction cannot undo a max.")

    # ── Subarray with given sum ───────────────────────────────────────
    yield section("Subarray with given sum", "target")
    yield p("Does a contiguous subarray of a **non-negative** array sum to exactly `target`?")
    yield io("arr = [1, 4, 20, 3, 10, 15], target = 33", "Yes", "arr = [2, 4], target = 3", "No", "arr = [1, 4, 0, 0, 3, 10, 5], target = 7", "Yes")
    yield p("Naively try every start and extend — `O(n²)`:")
    yield snippet("py", r'''
        def has_sum_naive(arr, target):
            for i in range(len(arr)):
                curr = 0
                for j in range(i, len(arr)):
                    curr += arr[j]
                    if curr == target:
                        return True
            return False

        print("Yes" if has_sum_naive([1, 4, 20, 3, 10, 15], 33) else "No")
    ''', out="Yes")
    yield idea("**Variable-size sliding window (two pointers).** Keep a window `[s, i]` and its sum. Extend `i` every step; while the sum exceeds `target`, shrink from the left by advancing `s`. Because the elements are non-negative, shrinking only ever decreases the sum, so no candidate is skipped. Both pointers move only forward: `O(n)`.")
    yield multi('''
        Yes
        No
        Yes
    ''', py=r'''
        def has_sum(arr, target):
            s = 0
            curr = 0
            for i in range(len(arr)):
                curr += arr[i]                   # grow at the right
                while curr > target and s < i:   # shrink at the left while too big
                    curr -= arr[s]
                    s += 1
                if curr == target:
                    return True
            return False

        for arr, target in (([1, 4, 20, 3, 10, 15], 33), ([2, 4], 3), ([1, 4, 0, 0, 3, 10, 5], 7)):
            print("Yes" if has_sum(arr, target) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool hasSum(const vector<int>& arr, int target) {
            int n = arr.size();
            int s = 0, curr = 0;
            for (int i = 0; i < n; i++) {
                curr += arr[i];                          // grow at the right
                while (curr > target && s < i) {         // shrink at the left while too big
                    curr -= arr[s];
                    s++;
                }
                if (curr == target) return true;
            }
            return false;
        }

        int main() {
            cout << (hasSum({1, 4, 20, 3, 10, 15}, 33) ? "Yes" : "No") << "\n";
            cout << (hasSum({2, 4}, 3) ? "Yes" : "No") << "\n";
            cout << (hasSum({1, 4, 0, 0, 3, 10, 5}, 7) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean hasSum(int[] arr, int target) {
                int s = 0, curr = 0;
                for (int i = 0; i < arr.length; i++) {
                    curr += arr[i];                          // grow at the right
                    while (curr > target && s < i) {         // shrink at the left while too big
                        curr -= arr[s];
                        s++;
                    }
                    if (curr == target) return true;
                }
                return false;
            }

            public static void main(String[] args) {
                System.out.println(hasSum(new int[]{1, 4, 20, 3, 10, 15}, 33) ? "Yes" : "No");
                System.out.println(hasSum(new int[]{2, 4}, 3) ? "Yes" : "No");
                System.out.println(hasSum(new int[]{1, 4, 0, 0, 3, 10, 5}, 7) ? "Yes" : "No");
            }
        }
    ''', js=r'''
        function hasSum(arr, target) {
            let s = 0, curr = 0;
            for (let i = 0; i < arr.length; i++) {
                curr += arr[i];                          // grow at the right
                while (curr > target && s < i) {         // shrink at the left while too big
                    curr -= arr[s];
                    s++;
                }
                if (curr === target) return true;
            }
            return false;
        }

        console.log(hasSum([1, 4, 20, 3, 10, 15], 33) ? "Yes" : "No");
        console.log(hasSum([2, 4], 3) ? "Yes" : "No");
        console.log(hasSum([1, 4, 0, 0, 3, 10, 5], 7) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Two pointers rely on **non-negative** elements. With negatives, shrinking the window can increase the sum and the window can skip a valid answer. Use prefix sums with a hash set instead: a subarray ending at `i` sums to `target` exactly when `prefix[i] - target` was an earlier prefix sum.")
    yield multi('''
        Yes
        No
        Yes
        Yes
    ''', py=r'''
        def has_sum(arr, target):
            seen = {0}                           # prefix sums seen so far (empty prefix = 0)
            curr = 0
            for x in arr:
                curr += x
                if curr - target in seen:        # some earlier prefix leaves exactly target
                    return True
                seen.add(curr)
            return False

        for arr, target in (([1, 4, 20, 3, 10, 15], 33), ([2, 4], 3),
                            ([1, 4, 0, 0, 3, 10, 5], 7), ([10, 2, -2, -20, 10], -10)):
            print("Yes" if has_sum(arr, target) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <unordered_set>
        using namespace std;

        bool hasSum(const vector<int>& arr, int target) {
            unordered_set<int> seen = {0};           // prefix sums seen so far (empty prefix = 0)
            int curr = 0;
            for (int x : arr) {
                curr += x;
                if (seen.count(curr - target)) return true;   // an earlier prefix leaves exactly target
                seen.insert(curr);
            }
            return false;
        }

        int main() {
            cout << (hasSum({1, 4, 20, 3, 10, 15}, 33) ? "Yes" : "No") << "\n";
            cout << (hasSum({2, 4}, 3) ? "Yes" : "No") << "\n";
            cout << (hasSum({1, 4, 0, 0, 3, 10, 5}, 7) ? "Yes" : "No") << "\n";
            cout << (hasSum({10, 2, -2, -20, 10}, -10) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static boolean hasSum(int[] arr, int target) {
                Set<Integer> seen = new HashSet<>();     // prefix sums seen so far
                seen.add(0);                             // the empty prefix
                int curr = 0;
                for (int x : arr) {
                    curr += x;
                    if (seen.contains(curr - target)) return true;   // an earlier prefix leaves exactly target
                    seen.add(curr);
                }
                return false;
            }

            public static void main(String[] args) {
                System.out.println(hasSum(new int[]{1, 4, 20, 3, 10, 15}, 33) ? "Yes" : "No");
                System.out.println(hasSum(new int[]{2, 4}, 3) ? "Yes" : "No");
                System.out.println(hasSum(new int[]{1, 4, 0, 0, 3, 10, 5}, 7) ? "Yes" : "No");
                System.out.println(hasSum(new int[]{10, 2, -2, -20, 10}, -10) ? "Yes" : "No");
            }
        }
    ''', js=r'''
        function hasSum(arr, target) {
            const seen = new Set([0]);               // prefix sums seen so far (empty prefix = 0)
            let curr = 0;
            for (const x of arr) {
                curr += x;
                if (seen.has(curr - target)) return true;   // an earlier prefix leaves exactly target
                seen.add(curr);
            }
            return false;
        }

        console.log(hasSum([1, 4, 20, 3, 10, 15], 33) ? "Yes" : "No");
        console.log(hasSum([2, 4], 3) ? "Yes" : "No");
        console.log(hasSum([1, 4, 0, 0, 3, 10, 5], 7) ? "Yes" : "No");
        console.log(hasSum([10, 2, -2, -20, 10], -10) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n)")

    # ── Prefix sum ────────────────────────────────────────────────────
    yield section("Prefix sum technique: range sum queries", "sum")
    yield p("Given a fixed array and **many** queries `getSum(l, r)`, answer each in `O(1)` after a one-time `O(n)` preprocessing.")
    yield io("arr = [2, 8, 3, 9, 6, 5, 4]; getSum(0, 2), getSum(1, 3), getSum(2, 6)", "13 20 27")
    yield p("Answering each query by adding `arr[l..r]` costs `O(r - l + 1)` — `O(n)` per query, `O(n · q)` for `q` queries.")
    yield idea("Precompute `psum[i] = arr[0] + … + arr[i]`. Then `sum(l..r) = psum[r] - psum[l-1]`, with `psum[r]` alone when `l == 0`. Storing one extra leading zero (`psum[i]` = sum of the first `i` elements) removes that special case: `sum(l..r) = psum[r+1] - psum[l]`.")
    yield diagram('''
        index:   0   1   2   3   4   5   6
        arr:     2   8   3   9   6   5   4
        psum:    2  10  13  22  28  33  37        getSum(2, 6) = psum[6] - psum[1] = 37 - 10 = 27
    ''', "Prefix sums: a range sum is one subtraction")
    yield multi('''
        13
        20
        27
    ''', py=r'''
        def build_prefix(arr):
            psum = [0] * (len(arr) + 1)          # psum[i] = sum of arr[0..i-1]
            for i, x in enumerate(arr):
                psum[i + 1] = psum[i] + x
            return psum

        def get_sum(psum, l, r):                 # inclusive l..r
            return psum[r + 1] - psum[l]

        psum = build_prefix([2, 8, 3, 9, 6, 5, 4])
        for l, r in ((0, 2), (1, 3), (2, 6)):
            print(get_sum(psum, l, r))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> buildPrefix(const vector<int>& arr) {
            int n = arr.size();
            vector<int> psum(n + 1, 0);              // psum[i] = sum of arr[0..i-1]
            for (int i = 0; i < n; i++) psum[i + 1] = psum[i] + arr[i];
            return psum;
        }

        int getSum(const vector<int>& psum, int l, int r) {   // inclusive l..r
            return psum[r + 1] - psum[l];
        }

        int main() {
            vector<int> psum = buildPrefix({2, 8, 3, 9, 6, 5, 4});
            cout << getSum(psum, 0, 2) << "\n";
            cout << getSum(psum, 1, 3) << "\n";
            cout << getSum(psum, 2, 6) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int[] buildPrefix(int[] arr) {
                int[] psum = new int[arr.length + 1];     // psum[i] = sum of arr[0..i-1]
                for (int i = 0; i < arr.length; i++) psum[i + 1] = psum[i] + arr[i];
                return psum;
            }

            static int getSum(int[] psum, int l, int r) {    // inclusive l..r
                return psum[r + 1] - psum[l];
            }

            public static void main(String[] args) {
                int[] psum = buildPrefix(new int[]{2, 8, 3, 9, 6, 5, 4});
                System.out.println(getSum(psum, 0, 2));
                System.out.println(getSum(psum, 1, 3));
                System.out.println(getSum(psum, 2, 6));
            }
        }
    ''', js=r'''
        function buildPrefix(arr) {
            const psum = new Array(arr.length + 1).fill(0);   // psum[i] = sum of arr[0..i-1]
            for (let i = 0; i < arr.length; i++) psum[i + 1] = psum[i] + arr[i];
            return psum;
        }

        function getSum(psum, l, r) {                        // inclusive l..r
            return psum[r + 1] - psum[l];
        }

        const psum = buildPrefix([2, 8, 3, 9, 6, 5, 4]);
        console.log(getSum(psum, 0, 2));
        console.log(getSum(psum, 1, 3));
        console.log(getSum(psum, 2, 6));
    ''')
    yield complexity("O(n) preprocessing, O(1) per query", "O(n)")
    yield p("**Weighted range sum.** The same trick answers `sum of (i - l) · arr[i]` for `i` in `l..r` — each element weighted by its offset inside the range. Keep a second prefix array `W[i] = sum of i · arr[i]`; then `sum(i · arr[i]) - l · sum(arr[i])` over the range is two subtractions.")
    yield io("arr = [1, 2, 3, 4, 5]; weighted(0, 2) = 0·1 + 1·2 + 2·3", "8", "weighted(1, 3) = 0·2 + 1·3 + 2·4", "11")
    yield snippet("py", r'''
        def preprocess(arr):
            n = len(arr)
            P = [0] * (n + 1)                    # P[i] = sum of arr[0..i-1]
            W = [0] * (n + 1)                    # W[i] = sum of k * arr[k] for k < i
            for i, x in enumerate(arr):
                P[i + 1] = P[i] + x
                W[i + 1] = W[i] + i * x
            return P, W

        def weighted_sum(P, W, l, r):            # sum of (i - l) * arr[i], i in l..r
            return (W[r + 1] - W[l]) - l * (P[r + 1] - P[l])

        P, W = preprocess([1, 2, 3, 4, 5])
        print(weighted_sum(P, W, 0, 2))
        print(weighted_sum(P, W, 1, 3))
    ''', out='''
        8
        11
    ''')
    yield complexity("O(n) preprocessing, O(1) per query", "O(n)")
    yield pitfall("Prefix sums overflow 32-bit integers quickly (`10⁵` elements of `10⁵` already exceed `2³¹`). Use `long long` / `long` in C++ and Java; Python and JavaScript numbers are safe up to `2⁵³` in JS and unbounded in Python.")

    # ── Equilibrium point ─────────────────────────────────────────────
    yield section("Equilibrium point", "scale")
    yield p("An index `i` is an equilibrium point when the sum of elements before it equals the sum after it. Return the first such index, or `-1`.")
    yield io("arr = [3, 4, 8, -9, 20, 6]", "4", "arr = [4, 2, -2]", "0", "arr = [4, 2, 2]", "-1")
    yield p("Naively compute left and right sums for every `i` — `O(n²)`:")
    yield snippet("py", r'''
        def equilibrium_naive(arr):
            n = len(arr)
            for i in range(n):
                if sum(arr[:i]) == sum(arr[i + 1:]):   # two O(n) sums per index
                    return i
            return -1

        print(equilibrium_naive([3, 4, 8, -9, 20, 6]))
    ''', out="4")
    yield idea("`rightSum = total - leftSum - arr[i]`, so one running `leftSum` is enough: compute `total` once, then walk left to right subtracting the current element from the right sum and adding it to the left sum. A prefix sum without storing the array.")
    yield multi('''
        4
        0
        -1
    ''', py=r'''
        def equilibrium(arr):
            right = sum(arr)                     # everything is to the right at first
            left = 0
            for i, x in enumerate(arr):
                right -= x                       # arr[i] leaves the right side
                if left == right:
                    return i
                left += x                        # ... and joins the left side
            return -1

        for arr in ([3, 4, 8, -9, 20, 6], [4, 2, -2], [4, 2, 2]):
            print(equilibrium(arr))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int equilibrium(const vector<int>& arr) {
            int n = arr.size();
            int right = 0, left = 0;
            for (int x : arr) right += x;            // everything is to the right at first
            for (int i = 0; i < n; i++) {
                right -= arr[i];                     // arr[i] leaves the right side
                if (left == right) return i;
                left += arr[i];                      // ... and joins the left side
            }
            return -1;
        }

        int main() {
            vector<vector<int>> tests = {{3, 4, 8, -9, 20, 6}, {4, 2, -2}, {4, 2, 2}};
            for (auto& arr : tests) cout << equilibrium(arr) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int equilibrium(int[] arr) {
                int right = 0, left = 0;
                for (int x : arr) right += x;            // everything is to the right at first
                for (int i = 0; i < arr.length; i++) {
                    right -= arr[i];                     // arr[i] leaves the right side
                    if (left == right) return i;
                    left += arr[i];                      // ... and joins the left side
                }
                return -1;
            }

            public static void main(String[] args) {
                int[][] tests = {{3, 4, 8, -9, 20, 6}, {4, 2, -2}, {4, 2, 2}};
                for (int[] arr : tests) System.out.println(equilibrium(arr));
            }
        }
    ''', js=r'''
        function equilibrium(arr) {
            let right = arr.reduce((a, b) => a + b, 0);  // everything is to the right at first
            let left = 0;
            for (let i = 0; i < arr.length; i++) {
                right -= arr[i];                         // arr[i] leaves the right side
                if (left === right) return i;
                left += arr[i];                          // ... and joins the left side
            }
            return -1;
        }

        for (const arr of [[3, 4, 8, -9, 20, 6], [4, 2, -2], [4, 2, 2]])
            console.log(equilibrium(arr));
    ''')
    yield complexity("O(n)", "O(1)")
    yield p("**Variant: partition into three parts with equal sum.** If `total % 3 != 0` it is impossible. Otherwise scan once, accumulating a running sum and cutting a part whenever it reaches `total / 3`; three or more cuts mean a valid partition (extra cuts happen only when `total / 3 == 0`, and then merging the extra parts keeps every sum equal).")
    yield io("arr = [1, 2, 3, 0, 3]", "true", "arr = [0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1]", "true", "arr = [1, 2, 3]", "false")
    yield multi('''
        true
        true
        false
    ''', py=r'''
        def three_equal_parts(arr):
            total = sum(arr)
            if total % 3 != 0:
                return False
            target = total // 3
            curr = parts = 0
            for x in arr:
                curr += x
                if curr == target:               # close a part, start the next one
                    parts += 1
                    curr = 0
            return parts >= 3

        for arr in ([1, 2, 3, 0, 3], [0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1], [1, 2, 3]):
            print("true" if three_equal_parts(arr) else "false")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool threeEqualParts(const vector<int>& arr) {
            int total = 0;
            for (int x : arr) total += x;
            if (total % 3 != 0) return false;
            int target = total / 3, curr = 0, parts = 0;
            for (int x : arr) {
                curr += x;
                if (curr == target) { parts++; curr = 0; }   // close a part, start the next one
            }
            return parts >= 3;
        }

        int main() {
            vector<vector<int>> tests = {{1, 2, 3, 0, 3}, {0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1}, {1, 2, 3}};
            for (auto& arr : tests) cout << (threeEqualParts(arr) ? "true" : "false") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean threeEqualParts(int[] arr) {
                int total = 0;
                for (int x : arr) total += x;
                if (total % 3 != 0) return false;
                int target = total / 3, curr = 0, parts = 0;
                for (int x : arr) {
                    curr += x;
                    if (curr == target) { parts++; curr = 0; }   // close a part, start the next one
                }
                return parts >= 3;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 2, 3, 0, 3}, {0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1}, {1, 2, 3}};
                for (int[] arr : tests) System.out.println(threeEqualParts(arr));
            }
        }
    ''', js=r'''
        function threeEqualParts(arr) {
            const total = arr.reduce((a, b) => a + b, 0);
            if (total % 3 !== 0) return false;
            const target = total / 3;
            let curr = 0, parts = 0;
            for (const x of arr) {
                curr += x;
                if (curr === target) { parts++; curr = 0; }   // close a part, start the next one
            }
            return parts >= 3;
        }

        for (const arr of [[1, 2, 3, 0, 3], [0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1], [1, 2, 3]])
            console.log(threeEqualParts(arr));
    ''')
    yield complexity("O(n)", "O(1)")

    # ── Maximum appearing element in ranges ───────────────────────────
    yield section("Maximum appearing element in ranges", "chart-histogram")
    yield p("Given `left[i]..right[i]` ranges over small integers (`0 ≤ left[i] ≤ right[i] < 100`), find the number that lies in the most ranges.")
    yield io("left = [1, 2, 5, 15], right = [5, 8, 7, 18]", "5", "left = [1, 4, 3, 1], right = [15, 8, 5, 4]", "4")
    yield p("Naively walk every range and increment a frequency counter for each number inside it — `O(n · range length)`, up to `O(100 · n)`:")
    yield snippet("py", r'''
        def max_appearing_naive(left, right):
            freq = [0] * 100
            for l, r in zip(left, right):
                for x in range(l, r + 1):            # touch every number in the range
                    freq[x] += 1
            return freq.index(max(freq))

        print(max_appearing_naive([1, 2, 5, 15], [5, 8, 7, 18]))
    ''', out="5")
    yield idea("**Difference array.** Mark only the two ends of each range: `freq[left] += 1` and `freq[right + 1] -= 1`. A prefix sum over `freq` then yields, for every number, how many ranges contain it — each range costs `O(1)` instead of `O(length)`.")
    yield diagram('''
        ranges:  [1..5]  [2..8]  [5..7]  [15..18]
        index:    0  1  2  3  4  5  6  7  8  9 ... 15 16 17 18 19
        marks:    0 +1 +1  0  0 +1 -1  0 -1 -1 ... +1  0  0  0 -1
        prefix:   0  1  2  2  2  3  2  2  1  0 ...  1  1  1  1  0      ← max 3 at index 5
    ''', "Difference array + prefix sum = coverage count")
    yield multi('''
        5
        4
    ''', py=r'''
        def max_appearing(left, right):
            freq = [0] * 101                         # one extra slot for right + 1
            for l, r in zip(left, right):
                freq[l] += 1                         # range starts here
                freq[r + 1] -= 1                     # ... and stops after r
            best, res = freq[0], 0
            for i in range(1, 100):
                freq[i] += freq[i - 1]               # prefix sum → coverage count
                if freq[i] > best:
                    best, res = freq[i], i
            return res

        print(max_appearing([1, 2, 5, 15], [5, 8, 7, 18]))
        print(max_appearing([1, 4, 3, 1], [15, 8, 5, 4]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int maxAppearing(const vector<int>& left, const vector<int>& right) {
            int n = left.size();
            vector<int> freq(101, 0);                    // one extra slot for right + 1
            for (int i = 0; i < n; i++) {
                freq[left[i]]++;                         // range starts here
                freq[right[i] + 1]--;                    // ... and stops after right
            }
            int best = freq[0], res = 0;
            for (int i = 1; i < 100; i++) {
                freq[i] += freq[i - 1];                  // prefix sum → coverage count
                if (freq[i] > best) { best = freq[i]; res = i; }
            }
            return res;
        }

        int main() {
            cout << maxAppearing({1, 2, 5, 15}, {5, 8, 7, 18}) << "\n";
            cout << maxAppearing({1, 4, 3, 1}, {15, 8, 5, 4}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int maxAppearing(int[] left, int[] right) {
                int[] freq = new int[101];                   // one extra slot for right + 1
                for (int i = 0; i < left.length; i++) {
                    freq[left[i]]++;                         // range starts here
                    freq[right[i] + 1]--;                    // ... and stops after right
                }
                int best = freq[0], res = 0;
                for (int i = 1; i < 100; i++) {
                    freq[i] += freq[i - 1];                  // prefix sum → coverage count
                    if (freq[i] > best) { best = freq[i]; res = i; }
                }
                return res;
            }

            public static void main(String[] args) {
                System.out.println(maxAppearing(new int[]{1, 2, 5, 15}, new int[]{5, 8, 7, 18}));
                System.out.println(maxAppearing(new int[]{1, 4, 3, 1}, new int[]{15, 8, 5, 4}));
            }
        }
    ''', js=r'''
        function maxAppearing(left, right) {
            const freq = new Array(101).fill(0);         // one extra slot for right + 1
            for (let i = 0; i < left.length; i++) {
                freq[left[i]]++;                         // range starts here
                freq[right[i] + 1]--;                    // ... and stops after right
            }
            let best = freq[0], res = 0;
            for (let i = 1; i < 100; i++) {
                freq[i] += freq[i - 1];                  // prefix sum → coverage count
                if (freq[i] > best) { best = freq[i]; res = i; }
            }
            return res;
        }

        console.log(maxAppearing([1, 2, 5, 15], [5, 8, 7, 18]));
        console.log(maxAppearing([1, 4, 3, 1], [15, 8, 5, 4]));
    ''')
    yield complexity("O(n + 100)", "O(100)")
    yield note("The difference array is the inverse of the prefix sum: a prefix sum turns point marks into range counts, so a `+1 / -1` pair applies `+1` to a whole range for `O(1)`. It handles `q` range *updates* followed by one read-out in `O(n + q)`.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why are so many array problems O(n²) naively, and what do the efficient versions have in common?",
             "The naive solutions enumerate pairs `(i, j)` or restart a scan from every index. The efficient versions carry a summary of the prefix already seen — the running minimum (maximum difference), the best subarray ending here (Kadane), the prefix sum (range queries, equilibrium), the window sum (sliding window) — so each new element is processed in `O(1)` using that summary.")
    yield qa("Explain Kadane's algorithm and why restarting at a negative running sum is safe.",
             "`maxEnding[i] = max(maxEnding[i-1] + arr[i], arr[i])`. If `maxEnding[i-1]` is negative, prepending it to any subarray starting at `i` can only lower the sum, so the best subarray ending at `i` is `arr[i]` alone. The overall answer is `max` over all `maxEnding[i]`. Initialise with `arr[0]`, not `0`, so an all-negative array returns its largest element.")
    yield qa("When do two pointers / sliding window fail, and what replaces them?",
             "They need monotonic behaviour: growing the window must never decrease the quantity and shrinking must never increase it. Non-negative sums have that property; arrays with negatives do not. Replace with prefix sums plus a hash set/map (`prefix[i] - target` seen before?), which also counts the subarrays in `O(n)`.")
    yield qa("How does Boyer–Moore voting find the majority in O(1) space, and why is the second pass needed?",
             "Pair every candidate element with a different element and cancel both. A majority element has more copies than all other elements together, so after all cancellations some copies of it remain — it is the surviving candidate. If no majority exists, the survivor is arbitrary, so a second pass counts the candidate and rejects it unless its count exceeds `n/2`.")
    yield qa("What is a difference array and when would you use one?",
             "An array `d` where `d[l] += v` and `d[r+1] -= v` encodes 'add `v` to every element of `l..r`'. One prefix sum over `d` materialises all updates. It turns `q` range updates with one final read into `O(n + q)` instead of `O(n · q)` — the maximum-appearing-element problem is exactly this with `v = 1`.")
    yield qa("How do you rotate an array in place in O(n) time?",
             "The reversal algorithm: reverse `arr[0..d-1]`, reverse `arr[d..n-1]`, reverse the whole array. Each element moves a constant number of times and no extra array is needed. Alternatives: the juggling algorithm (move elements in `gcd(n, d)` cycles), or in Python `collections.deque.rotate` — simple but `O(n)` extra space.")


@topic(G, "matrix", "Matrix", "grid-dots")
def _():
    yield lead("A matrix is a 2-D array: a list of rows, each a list of values, addressed as `mat[i][j]`. Matrix problems are mostly about **traversal order** (snake, boundary, spiral), **in-place rearrangement** (transpose, rotate) and **exploiting sortedness** (staircase search, median by binary search on the value range).")
    yield define("Matrix (2-D array)", "`R` rows × `C` columns of elements; `mat[i][j]` is the element in row `i` (`0..R-1`) and column `j` (`0..C-1`). In Python, C++ and Java it is an array of row arrays; in memory the rows are stored one after another (row-major order).")
    yield diagram('''
                 j=0  j=1  j=2  j=3
               ┌────┬────┬────┬────┐
        i=0    │  1 │  2 │  3 │  4 │     R = 3 rows, C = 4 columns
               ├────┼────┼────┼────┤
        i=1    │  5 │  6 │  7 │  8 │     mat[1][2] = 7
               ├────┼────┼────┼────┤
        i=2    │  9 │ 10 │ 11 │ 12 │     row-major memory: 1 2 3 4 5 6 7 8 9 10 11 12
               └────┴────┴────┴────┘
    ''', "Indices: first the row i, then the column j")

    yield section("2-D arrays in each language", "code")
    yield table(
        ["", "Python", "C++", "Java", "JavaScript"],
        ["Literal", "`[[1,2,3],[4,5,6]]`", "`vector<vector<int>> m = {{1,2,3},{4,5,6}};`", "`int[][] m = {{1,2,3},{4,5,6}};`", "`[[1,2,3],[4,5,6]]`"],
        ["Rows", "`len(m)`", "`m.size()`", "`m.length`", "`m.length`"],
        ["Columns of row `i`", "`len(m[i])`", "`m[i].size()`", "`m[i].length`", "`m[i].length`"],
        ["`R × C` zeros", "`[[0]*C for _ in range(R)]`", "`vector<vector<int>>(R, vector<int>(C, 0))`", "`new int[R][C]`", "`Array.from({length: R}, () => Array(C).fill(0))`"],
        ["Pass to a function", "by reference (the list object)", "`vector<vector<int>>&`", "`int[][]` (reference)", "by reference"],
    )
    yield p("Rows can have different lengths in all four languages (a *jagged* array), so always read the column count from the row you are about to use — `len(mat[i])` — not from `mat[0]` unless the matrix is known to be rectangular.")
    yield multi('''
        1 2 3
        4 5 6
        rows: 2
        cols: 3
    ''', py=r'''
        def print_matrix(mat):                   # a 2-D list is passed by reference
            for row in mat:
                print(*row)                      # space-separated row

        mat = [[1, 2, 3],
               [4, 5, 6]]
        print_matrix(mat)
        print("rows:", len(mat))
        print("cols:", len(mat[0]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void printMatrix(const vector<vector<int>>& mat) {   // pass by reference: no copy
            for (const auto& row : mat) {
                for (int x : row) cout << x << " ";
                cout << "\n";
            }
        }

        int main() {
            vector<vector<int>> mat = {{1, 2, 3},
                                       {4, 5, 6}};
            printMatrix(mat);
            cout << "rows: " << mat.size() << "\n";
            cout << "cols: " << mat[0].size() << "\n";
        }
    ''', java=r'''
        public class Main {
            static void printMatrix(int[][] mat) {       // arrays are passed by reference
                for (int[] row : mat) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : row) sb.append(x).append(' ');
                    System.out.println(sb.toString().trim());
                }
            }

            public static void main(String[] args) {
                int[][] mat = {{1, 2, 3},
                               {4, 5, 6}};
                printMatrix(mat);
                System.out.println("rows: " + mat.length);
                System.out.println("cols: " + mat[0].length);
            }
        }
    ''', js=r'''
        function printMatrix(mat) {                  // arrays are passed by reference
            for (const row of mat) console.log(row.join(" "));
        }

        const mat = [[1, 2, 3],
                     [4, 5, 6]];
        printMatrix(mat);
        console.log("rows:", mat.length);
        console.log("cols:", mat[0].length);
    ''')
    yield p("**User-specified dimensions.** Build an `R × C` matrix of zeros and fill it. The one trap is Python's `[[0] * C] * R`, which repeats the *same* row object `R` times:")
    yield snippet("py", r'''
        rows, cols = 3, 4
        bad = [[0] * cols] * rows          # three references to ONE row
        bad[0][0] = 1
        for r in bad:
            print(*r)                      # the 1 shows up in every row

        good = [[0] * cols for _ in range(rows)]   # a fresh row each time
        good[0][0] = 1
        for r in good:
            print(*r)
    ''', out='''
        1 0 0 0
        1 0 0 0
        1 0 0 0
        1 0 0 0
        0 0 0 0
        0 0 0 0
    ''')
    yield multi('''
        1 2 3 4
        5 6 7 8
        9 10 11 12
    ''', py=r'''
        rows, cols = 3, 4
        mat = [[0] * cols for _ in range(rows)]  # R independent rows of C zeros
        for i in range(rows):
            for j in range(cols):
                mat[i][j] = i * cols + j + 1     # row-major numbering
        for row in mat:
            print(*row)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int main() {
            int rows = 3, cols = 4;
            vector<vector<int>> mat(rows, vector<int>(cols, 0));   // R rows of C zeros
            for (int i = 0; i < rows; i++)
                for (int j = 0; j < cols; j++)
                    mat[i][j] = i * cols + j + 1;    // row-major numbering
            for (const auto& row : mat) {
                for (int x : row) cout << x << " ";
                cout << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                int rows = 3, cols = 4;
                int[][] mat = new int[rows][cols];           // zero-filled
                for (int i = 0; i < rows; i++)
                    for (int j = 0; j < cols; j++)
                        mat[i][j] = i * cols + j + 1;        // row-major numbering
                for (int[] row : mat) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : row) sb.append(x).append(' ');
                    System.out.println(sb.toString().trim());
                }
            }
        }
    ''', js=r'''
        const rows = 3, cols = 4;
        const mat = Array.from({ length: rows }, () => Array(cols).fill(0));   // R independent rows
        for (let i = 0; i < rows; i++)
            for (let j = 0; j < cols; j++)
                mat[i][j] = i * cols + j + 1;            // row-major numbering
        for (const row of mat) console.log(row.join(" "));
    ''')
    yield pitfall("`Array(rows).fill(Array(cols).fill(0))` in JavaScript has the same aliasing bug as Python's `[[0]*C]*R` — every row is the same array. Use `Array.from` with a factory, or a loop that pushes a new row each time.")

    yield section("Print a matrix in snake pattern", "wave-sine")
    yield p("Traverse even-numbered rows left to right and odd-numbered rows right to left, as a snake winds through the grid.")
    yield io("mat = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]", "1 2 3 6 5 4 7 8 9 12 11 10")
    yield diagram('''
        1 → 2 → 3
                ↓
        6 ← 5 ← 4
        ↓
        7 → 8 → 9
                ↓
       12 ← 11 ← 10
    ''', "Snake order: alternate the direction on every row")
    yield idea("The row index decides the direction: `i % 2 == 0` → columns `0..C-1`, otherwise `C-1..0`. No extra space is needed.")
    yield multi('''
        1 2 3 6 5 4 7 8 9 12 11 10
    ''', py=r'''
        def snake(mat):
            out = []
            for i, row in enumerate(mat):
                if i % 2 == 0:
                    out.extend(row)                  # left → right
                else:
                    out.extend(reversed(row))        # right → left
            return out

        mat = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
        print(*snake(mat))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void snake(const vector<vector<int>>& mat) {
            int R = mat.size();
            for (int i = 0; i < R; i++) {
                int C = mat[i].size();
                if (i % 2 == 0)
                    for (int j = 0; j < C; j++) cout << mat[i][j] << " ";        // left → right
                else
                    for (int j = C - 1; j >= 0; j--) cout << mat[i][j] << " ";   // right → left
            }
            cout << "\n";
        }

        int main() {
            snake({{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}});
        }
    ''', java=r'''
        public class Main {
            static void snake(int[][] mat) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < mat.length; i++) {
                    int C = mat[i].length;
                    if (i % 2 == 0)
                        for (int j = 0; j < C; j++) sb.append(mat[i][j]).append(' ');        // left → right
                    else
                        for (int j = C - 1; j >= 0; j--) sb.append(mat[i][j]).append(' ');   // right → left
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) {
                snake(new int[][]{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}});
            }
        }
    ''', js=r'''
        function snake(mat) {
            const out = [];
            for (let i = 0; i < mat.length; i++) {
                const C = mat[i].length;
                if (i % 2 === 0)
                    for (let j = 0; j < C; j++) out.push(mat[i][j]);        // left → right
                else
                    for (let j = C - 1; j >= 0; j--) out.push(mat[i][j]);   // right → left
            }
            return out;
        }

        console.log(snake([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]).join(" "));
    ''')
    yield complexity("O(R · C)", "O(1)")

    yield section("Matrix boundary traversal", "border-all")
    yield p("Print the outer ring clockwise: top row, right column, bottom row (backwards), left column (upwards).")
    yield io("mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]", "1 2 3 4 8 12 11 10 9 5", "mat = [[1], [2], [3]]", "1 2 3", "mat = [[1, 2, 3]]", "1 2 3")
    yield diagram('''
        1 → 2 → 3 → 4
        ↑           ↓
        5   6   7   8
        ↑           ↓
        9 ← 10 ← 11 ← 12
    ''', "Boundary order on a 3 × 4 matrix")
    yield idea("Walk the four sides, each stopping one short of the next corner so no corner is printed twice. A single row or a single column is a special case — the ring collapses to a line and the generic four-side walk would print cells twice.")
    yield multi('''
        1 2 3 4 8 12 11 10 9 5
        1 2 3
        1 2 3
    ''', py=r'''
        def boundary(mat):
            R, C = len(mat), len(mat[0])
            if R == 1:
                return list(mat[0])                              # single row
            if C == 1:
                return [mat[i][0] for i in range(R)]             # single column
            out = []
            for j in range(C):           out.append(mat[0][j])       # top: left → right
            for i in range(1, R):        out.append(mat[i][C - 1])   # right: top → bottom
            for j in range(C - 2, -1, -1): out.append(mat[R - 1][j]) # bottom: right → left
            for i in range(R - 2, 0, -1):  out.append(mat[i][0])     # left: bottom → top
            return out

        for mat in ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], [[1], [2], [3]], [[1, 2, 3]]):
            print(*boundary(mat))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> boundary(const vector<vector<int>>& mat) {
            int R = mat.size(), C = mat[0].size();
            vector<int> out;
            if (R == 1) return mat[0];                                        // single row
            if (C == 1) { for (int i = 0; i < R; i++) out.push_back(mat[i][0]); return out; }
            for (int j = 0; j < C; j++) out.push_back(mat[0][j]);             // top: left → right
            for (int i = 1; i < R; i++) out.push_back(mat[i][C - 1]);         // right: top → bottom
            for (int j = C - 2; j >= 0; j--) out.push_back(mat[R - 1][j]);    // bottom: right → left
            for (int i = R - 2; i > 0; i--) out.push_back(mat[i][0]);         // left: bottom → top
            return out;
        }

        int main() {
            vector<vector<vector<int>>> tests = {{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}}, {{1}, {2}, {3}}, {{1, 2, 3}}};
            for (auto& mat : tests) {
                for (int x : boundary(mat)) cout << x << " ";
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> boundary(int[][] mat) {
                int R = mat.length, C = mat[0].length;
                List<Integer> out = new ArrayList<>();
                if (R == 1) { for (int x : mat[0]) out.add(x); return out; }                // single row
                if (C == 1) { for (int i = 0; i < R; i++) out.add(mat[i][0]); return out; } // single column
                for (int j = 0; j < C; j++) out.add(mat[0][j]);                 // top: left → right
                for (int i = 1; i < R; i++) out.add(mat[i][C - 1]);             // right: top → bottom
                for (int j = C - 2; j >= 0; j--) out.add(mat[R - 1][j]);        // bottom: right → left
                for (int i = R - 2; i > 0; i--) out.add(mat[i][0]);             // left: bottom → top
                return out;
            }

            public static void main(String[] args) {
                int[][][] tests = {{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}}, {{1}, {2}, {3}}, {{1, 2, 3}}};
                for (int[][] mat : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : boundary(mat)) sb.append(x).append(' ');
                    System.out.println(sb.toString().trim());
                }
            }
        }
    ''', js=r'''
        function boundary(mat) {
            const R = mat.length, C = mat[0].length;
            if (R === 1) return [...mat[0]];                                  // single row
            if (C === 1) return mat.map(row => row[0]);                       // single column
            const out = [];
            for (let j = 0; j < C; j++) out.push(mat[0][j]);                  // top: left → right
            for (let i = 1; i < R; i++) out.push(mat[i][C - 1]);              // right: top → bottom
            for (let j = C - 2; j >= 0; j--) out.push(mat[R - 1][j]);         // bottom: right → left
            for (let i = R - 2; i > 0; i--) out.push(mat[i][0]);              // left: bottom → top
            return out;
        }

        for (const mat of [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], [[1], [2], [3]], [[1, 2, 3]]])
            console.log(boundary(mat).join(" "));
    ''')
    yield complexity("O(R + C)", "O(1) besides the output")
    yield pitfall("Without the single-row / single-column cases, the four loops print the row `1 2 3` as `1 2 3 2 1` — the bottom side is the same cells walked backwards.")

    yield section("Transpose of a matrix", "arrows-diagonal")
    yield p("Rows become columns: `T[i][j] = mat[j][i]`.")
    yield io("mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]", "1 5 9 13 / 2 6 10 14 / 3 7 11 15 / 4 8 12 16")
    yield p("The naive version copies every element into a new `N × N` matrix and copies it back — `O(N²)` extra space:")
    yield snippet("py", r'''
        def transpose_copy(mat):
            N = len(mat)
            temp = [[0] * N for _ in range(N)]
            for i in range(N):
                for j in range(N):
                    temp[i][j] = mat[j][i]
            return temp

        for row in transpose_copy([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]):
            print(*row)
    ''', out='''
        1 5 9 13
        2 6 10 14
        3 7 11 15
        4 8 12 16
    ''')
    yield idea("For a **square** matrix, transposing just swaps `mat[i][j]` with `mat[j][i]`. Visit only the cells **above the diagonal** (`j > i`) and swap each with its mirror — visiting both triangles would swap everything twice and restore the original.")
    yield diagram('''
        1   2   3   4         diagonal stays; each ↔ pair is swapped once
        5   6   7   8         (0,1)↔(1,0)  (0,2)↔(2,0)  (0,3)↔(3,0)
        9  10  11  12         (1,2)↔(2,1)  (1,3)↔(3,1)
       13  14  15  16         (2,3)↔(3,2)
    ''', "In-place transpose touches the upper triangle only")
    yield multi('''
        1 5 9 13
        2 6 10 14
        3 7 11 15
        4 8 12 16
    ''', py=r'''
        def transpose(mat):
            N = len(mat)
            for i in range(N):
                for j in range(i + 1, N):            # upper triangle only
                    mat[i][j], mat[j][i] = mat[j][i], mat[i][j]

        mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
        transpose(mat)
        for row in mat:
            print(*row)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <utility>
        using namespace std;

        void transpose(vector<vector<int>>& mat) {
            int N = mat.size();
            for (int i = 0; i < N; i++)
                for (int j = i + 1; j < N; j++)          // upper triangle only
                    swap(mat[i][j], mat[j][i]);
        }

        int main() {
            vector<vector<int>> mat = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
            transpose(mat);
            for (auto& row : mat) {
                for (int x : row) cout << x << " ";
                cout << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static void transpose(int[][] mat) {
                int N = mat.length;
                for (int i = 0; i < N; i++)
                    for (int j = i + 1; j < N; j++) {        // upper triangle only
                        int t = mat[i][j]; mat[i][j] = mat[j][i]; mat[j][i] = t;
                    }
            }

            public static void main(String[] args) {
                int[][] mat = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
                transpose(mat);
                for (int[] row : mat) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : row) sb.append(x).append(' ');
                    System.out.println(sb.toString().trim());
                }
            }
        }
    ''', js=r'''
        function transpose(mat) {
            const N = mat.length;
            for (let i = 0; i < N; i++)
                for (let j = i + 1; j < N; j++)          // upper triangle only
                    [mat[i][j], mat[j][i]] = [mat[j][i], mat[i][j]];
        }

        const mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]];
        transpose(mat);
        for (const row of mat) console.log(row.join(" "));
    ''')
    yield complexity("O(N²)", "O(1)")
    yield note("A non-square `R × C` matrix cannot be transposed in place with this trick — the result is `C × R`, a different shape. Allocate the new matrix and fill `T[j][i] = mat[i][j]`.")

    yield section("Rotate a matrix by 90 degrees", "rotate-2")
    yield p("Rotate a square matrix **anticlockwise** by 90°: the last column becomes the first row, the second-last column the second row, and so on.")
    yield io("mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]", "4 8 12 16 / 3 7 11 15 / 2 6 10 14 / 1 5 9 13")
    yield p("Naively, `temp[N-1-j][i] = mat[i][j]` into a new matrix — `O(N²)` extra space:")
    yield snippet("py", r'''
        def rotate_copy(mat):
            N = len(mat)
            temp = [[0] * N for _ in range(N)]
            for i in range(N):
                for j in range(N):
                    temp[N - 1 - j][i] = mat[i][j]   # column j → row N-1-j
            return temp

        for row in rotate_copy([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]):
            print(*row)
    ''', out='''
        4 8 12 16
        3 7 11 15
        2 6 10 14
        1 5 9 13
    ''')
    yield idea("**Transpose, then reverse the order of the rows.** The transpose turns column `j` into row `j`; reversing the row order puts the last column first. Reversing every *column* of the transpose (the original's second method) is the same thing done cell by cell — swapping whole rows is simpler and just as in-place. For a **clockwise** rotation, transpose and reverse each *row* instead.")
    yield diagram('''
        1  2  3  4      transpose     1  5  9 13      reverse rows     4  8 12 16
        5  6  7  8      ─────────▶    2  6 10 14      ────────────▶    3  7 11 15
        9 10 11 12                    3  7 11 15                       2  6 10 14
       13 14 15 16                    4  8 12 16                       1  5  9 13
    ''', "Anticlockwise 90° = transpose + reverse the row order")
    yield multi('''
        4 8 12 16
        3 7 11 15
        2 6 10 14
        1 5 9 13
    ''', py=r'''
        def transpose(mat):
            N = len(mat)
            for i in range(N):
                for j in range(i + 1, N):
                    mat[i][j], mat[j][i] = mat[j][i], mat[i][j]

        def rotate_anticlockwise(mat):
            transpose(mat)
            lo, hi = 0, len(mat) - 1
            while lo < hi:                           # reverse the order of the rows
                mat[lo], mat[hi] = mat[hi], mat[lo]
                lo += 1
                hi -= 1

        mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
        rotate_anticlockwise(mat)
        for row in mat:
            print(*row)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <utility>
        using namespace std;

        void transpose(vector<vector<int>>& mat) {
            int N = mat.size();
            for (int i = 0; i < N; i++)
                for (int j = i + 1; j < N; j++) swap(mat[i][j], mat[j][i]);
        }

        void rotateAnticlockwise(vector<vector<int>>& mat) {
            transpose(mat);
            int lo = 0, hi = (int)mat.size() - 1;
            while (lo < hi) swap(mat[lo++], mat[hi--]);   // reverse the order of the rows
        }

        int main() {
            vector<vector<int>> mat = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
            rotateAnticlockwise(mat);
            for (auto& row : mat) {
                for (int x : row) cout << x << " ";
                cout << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static void transpose(int[][] mat) {
                int N = mat.length;
                for (int i = 0; i < N; i++)
                    for (int j = i + 1; j < N; j++) {
                        int t = mat[i][j]; mat[i][j] = mat[j][i]; mat[j][i] = t;
                    }
            }

            static void rotateAnticlockwise(int[][] mat) {
                transpose(mat);
                int lo = 0, hi = mat.length - 1;
                while (lo < hi) {                                // reverse the order of the rows
                    int[] t = mat[lo]; mat[lo] = mat[hi]; mat[hi] = t;
                    lo++; hi--;
                }
            }

            public static void main(String[] args) {
                int[][] mat = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
                rotateAnticlockwise(mat);
                for (int[] row : mat) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : row) sb.append(x).append(' ');
                    System.out.println(sb.toString().trim());
                }
            }
        }
    ''', js=r'''
        function transpose(mat) {
            const N = mat.length;
            for (let i = 0; i < N; i++)
                for (let j = i + 1; j < N; j++)
                    [mat[i][j], mat[j][i]] = [mat[j][i], mat[i][j]];
        }

        function rotateAnticlockwise(mat) {
            transpose(mat);
            mat.reverse();                               // reverse the order of the rows
        }

        const mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]];
        rotateAnticlockwise(mat);
        for (const row of mat) console.log(row.join(" "));
    ''')
    yield complexity("O(N²)", "O(1)")
    yield table(
        ["Rotation", "Recipe", "Check with `mat[0][0] = 1`"],
        ["90° anticlockwise", "transpose, then reverse row order (or reverse each column)", "`1` ends bottom-left"],
        ["90° clockwise", "transpose, then reverse each row", "`1` ends top-right"],
        ["180°", "reverse row order, then reverse each row", "`1` ends bottom-right"],
    )

    yield section("Spiral traversal of a matrix", "spiral")
    yield p("Print the matrix in a clockwise spiral starting at the top-left corner, peeling one ring at a time.")
    yield io("mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]", "1 2 3 4 8 12 16 15 14 13 9 5 6 7 11 10", "mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]", "1 2 3 4 8 12 11 10 9 5 6 7")
    yield diagram('''
        1 → 2 → 3 → 4
                    ↓
        5 → 6 → 7   8
        ↑       ↓   ↓
        9  10 ← 11  12
        ↑           ↓
       13 ← 14 ← 15 ← 16
    ''', "Spiral: top row, right column, bottom row, left column, then the inner ring")
    yield idea("Keep four boundaries `top`, `bottom`, `left`, `right`. Print the top row and move `top` down, the right column and move `right` left, the bottom row (if a row is left) and move `bottom` up, the left column (if a column is left) and move `left` right. Stop when the boundaries cross. The two `if` checks matter for non-square matrices, where the last ring can be a single row or column.")
    yield steps(
        ("Top row", "`left → right` along row `top`; then `top += 1`."),
        ("Right column", "`top → bottom` along column `right`; then `right -= 1`."),
        ("Bottom row", "only if `top <= bottom`: `right → left` along row `bottom`; then `bottom -= 1`."),
        ("Left column", "only if `left <= right`: `bottom → top` along column `left`; then `left += 1`."),
    )
    yield multi('''
        1 2 3 4 8 12 16 15 14 13 9 5 6 7 11 10
        1 2 3 4 8 12 11 10 9 5 6 7
    ''', py=r'''
        def spiral(mat):
            out = []
            top, bottom = 0, len(mat) - 1
            left, right = 0, len(mat[0]) - 1
            while top <= bottom and left <= right:
                for j in range(left, right + 1):          # top row →
                    out.append(mat[top][j])
                top += 1
                for i in range(top, bottom + 1):          # right column ↓
                    out.append(mat[i][right])
                right -= 1
                if top <= bottom:                         # a row is still left
                    for j in range(right, left - 1, -1):  # bottom row ←
                        out.append(mat[bottom][j])
                    bottom -= 1
                if left <= right:                         # a column is still left
                    for i in range(bottom, top - 1, -1):  # left column ↑
                        out.append(mat[i][left])
                    left += 1
            return out

        print(*spiral([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]))
        print(*spiral([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void spiral(const vector<vector<int>>& mat) {
            int top = 0, bottom = (int)mat.size() - 1;
            int left = 0, right = (int)mat[0].size() - 1;
            while (top <= bottom && left <= right) {
                for (int j = left; j <= right; j++) cout << mat[top][j] << " ";      // top row →
                top++;
                for (int i = top; i <= bottom; i++) cout << mat[i][right] << " ";    // right column ↓
                right--;
                if (top <= bottom) {                                                 // a row is still left
                    for (int j = right; j >= left; j--) cout << mat[bottom][j] << " ";   // bottom row ←
                    bottom--;
                }
                if (left <= right) {                                                 // a column is still left
                    for (int i = bottom; i >= top; i--) cout << mat[i][left] << " ";     // left column ↑
                    left++;
                }
            }
            cout << "\n";
        }

        int main() {
            spiral({{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}});
            spiral({{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}});
        }
    ''', java=r'''
        public class Main {
            static void spiral(int[][] mat) {
                StringBuilder sb = new StringBuilder();
                int top = 0, bottom = mat.length - 1;
                int left = 0, right = mat[0].length - 1;
                while (top <= bottom && left <= right) {
                    for (int j = left; j <= right; j++) sb.append(mat[top][j]).append(' ');      // top row →
                    top++;
                    for (int i = top; i <= bottom; i++) sb.append(mat[i][right]).append(' ');    // right column ↓
                    right--;
                    if (top <= bottom) {                                                         // a row is still left
                        for (int j = right; j >= left; j--) sb.append(mat[bottom][j]).append(' ');   // bottom row ←
                        bottom--;
                    }
                    if (left <= right) {                                                         // a column is still left
                        for (int i = bottom; i >= top; i--) sb.append(mat[i][left]).append(' ');     // left column ↑
                        left++;
                    }
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) {
                spiral(new int[][]{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}});
                spiral(new int[][]{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}});
            }
        }
    ''', js=r'''
        function spiral(mat) {
            const out = [];
            let top = 0, bottom = mat.length - 1;
            let left = 0, right = mat[0].length - 1;
            while (top <= bottom && left <= right) {
                for (let j = left; j <= right; j++) out.push(mat[top][j]);      // top row →
                top++;
                for (let i = top; i <= bottom; i++) out.push(mat[i][right]);    // right column ↓
                right--;
                if (top <= bottom) {                                            // a row is still left
                    for (let j = right; j >= left; j--) out.push(mat[bottom][j]);   // bottom row ←
                    bottom--;
                }
                if (left <= right) {                                            // a column is still left
                    for (let i = bottom; i >= top; i--) out.push(mat[i][left]);     // left column ↑
                    left++;
                }
            }
            return out;
        }

        console.log(spiral([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]).join(" "));
        console.log(spiral([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]).join(" "));
    ''')
    yield complexity("O(R · C)", "O(1) besides the output")
    yield pitfall("The original notes looped the right column with `range(top, bottom - 1)`, which skips the last two cells of the column — the 4 × 4 example only printed correctly by accident. The range must be `top..bottom` inclusive. Also, dropping the two `if` guards prints the middle row of a `3 × 4` matrix twice (`… 5 6 7 7 6 5`).")

    yield section("Search in a row-wise and column-wise sorted matrix", "search")
    yield p("Every row is sorted left to right and every column top to bottom. Find `x`, or report that it is absent.")
    yield io("mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], x = 11", "Found at (2, 2)", "x = 10", "Found at (2, 1)", "x = 17", "Not found")
    yield p("A full scan is `O(R · C)`. Binary-searching each row is `O(R log C)`. The staircase search below is `O(R + C)` and needs no binary search at all.")
    yield idea("**Staircase search.** Start at the **top-right** corner. Everything to its left is smaller, everything below it is larger. So if `mat[i][j] > x`, column `j` can be discarded (move left); if `mat[i][j] < x`, row `i` can be discarded (move down). Each step eliminates a whole row or column, so at most `R + C` steps are taken.")
    yield diagram('''
         1   2   3  [4]      x = 11: start at 4   (4 < 11 → down)
         5   6   7  [8]                 8 < 11 → down
         9  10 [11] 12                 12 > 11 → left,  11 found at (2, 2)
        13  14  15  16
    ''', "Each comparison discards a row or a column")
    yield multi('''
        Found at (2, 2)
        Found at (2, 1)
        Not found
    ''', py=r'''
        def search(mat, x):
            R, C = len(mat), len(mat[0])
            i, j = 0, C - 1                      # top-right corner
            while i < R and j >= 0:
                if mat[i][j] == x:
                    return f"Found at ({i}, {j})"
                if mat[i][j] > x:
                    j -= 1                       # whole column j is too big
                else:
                    i += 1                       # whole row i is too small
            return "Not found"

        mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
        for x in (11, 10, 17):
            print(search(mat, x))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <string>
        using namespace std;

        string search(const vector<vector<int>>& mat, int x) {
            int R = mat.size(), C = mat[0].size();
            int i = 0, j = C - 1;                        // top-right corner
            while (i < R && j >= 0) {
                if (mat[i][j] == x) return "Found at (" + to_string(i) + ", " + to_string(j) + ")";
                if (mat[i][j] > x) j--;                  // whole column j is too big
                else i++;                                // whole row i is too small
            }
            return "Not found";
        }

        int main() {
            vector<vector<int>> mat = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
            for (int x : {11, 10, 17}) cout << search(mat, x) << "\n";
        }
    ''', java=r'''
        public class Main {
            static String search(int[][] mat, int x) {
                int R = mat.length, C = mat[0].length;
                int i = 0, j = C - 1;                        // top-right corner
                while (i < R && j >= 0) {
                    if (mat[i][j] == x) return "Found at (" + i + ", " + j + ")";
                    if (mat[i][j] > x) j--;                  // whole column j is too big
                    else i++;                                // whole row i is too small
                }
                return "Not found";
            }

            public static void main(String[] args) {
                int[][] mat = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
                for (int x : new int[]{11, 10, 17}) System.out.println(search(mat, x));
            }
        }
    ''', js=r'''
        function search(mat, x) {
            const R = mat.length, C = mat[0].length;
            let i = 0, j = C - 1;                        // top-right corner
            while (i < R && j >= 0) {
                if (mat[i][j] === x) return `Found at (${i}, ${j})`;
                if (mat[i][j] > x) j--;                  // whole column j is too big
                else i++;                                // whole row i is too small
            }
            return "Not found";
        }

        const mat = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]];
        for (const x of [11, 10, 17]) console.log(search(mat, x));
    ''')
    yield complexity("O(R + C)", "O(1)")
    yield note("Starting at the **bottom-left** corner works symmetrically (smaller → up, larger → right). Starting at the top-left or bottom-right does *not*: both neighbours there move in the same direction, so a comparison cannot discard anything.")

    yield section("Median of a row-wise sorted matrix", "percentage")
    yield p("Each row is sorted, but the rows are unrelated to each other. Find the median of all `R × C` elements (assume `R × C` is odd).")
    yield io("mat = [[1, 3, 5], [2, 6, 9], [3, 6, 9]]", "5", "mat = [[5, 10, 20, 30, 40], [1, 2, 3, 4, 6], [11, 13, 15, 17, 19]]", "11")
    yield p("Naively, copy everything into one array, sort it and take the middle — `O(RC log RC)` time and `O(RC)` space:")
    yield snippet("py", r'''
        def median_naive(mat):
            flat = sorted(x for row in mat for x in row)
            return flat[len(flat) // 2]              # middle of an odd-length sorted list

        print(median_naive([[1, 3, 5], [2, 6, 9], [3, 6, 9]]))
    ''', out="5")
    yield idea("**Binary search on the answer.** The median is the smallest value `m` such that at least `(R·C + 1) / 2` elements are `≤ m`. The count of elements `≤ m` is monotonic in `m` and, because every row is sorted, it can be computed with one `upper_bound` per row in `O(R log C)`. Binary-search `m` between the smallest first-column value and the largest last-column value.")
    yield steps(
        ("Bounds", "`lo` = min of the first column, `hi` = max of the last column — the median lies between them."),
        ("Count", "For `mid = (lo + hi) / 2`, count how many elements are `≤ mid`: `upper_bound` in each row."),
        ("Narrow", "If `count < (R·C + 1) / 2`, the median is larger: `lo = mid + 1`; otherwise `hi = mid`."),
        ("Answer", "When `lo == hi` it is the median — it is guaranteed to be an element of the matrix."),
    )
    yield multi('''
        5
        11
    ''', py=r'''
        from bisect import bisect_right

        def median(mat):
            R, C = len(mat), len(mat[0])
            lo = min(row[0] for row in mat)
            hi = max(row[-1] for row in mat)
            target = (R * C + 1) // 2                        # rank of the median
            while lo < hi:
                mid = (lo + hi) // 2
                count = sum(bisect_right(row, mid) for row in mat)   # elements <= mid
                if count < target:
                    lo = mid + 1                             # median is bigger
                else:
                    hi = mid                                 # mid could be the median
            return lo

        print(median([[1, 3, 5], [2, 6, 9], [3, 6, 9]]))
        print(median([[5, 10, 20, 30, 40], [1, 2, 3, 4, 6], [11, 13, 15, 17, 19]]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        int median(const vector<vector<int>>& mat) {
            int R = mat.size(), C = mat[0].size();
            int lo = mat[0][0], hi = mat[0][C - 1];
            for (int i = 1; i < R; i++) {
                lo = min(lo, mat[i][0]);
                hi = max(hi, mat[i][C - 1]);
            }
            int target = (R * C + 1) / 2;                           // rank of the median
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                int count = 0;
                for (const auto& row : mat)                          // elements <= mid
                    count += upper_bound(row.begin(), row.end(), mid) - row.begin();
                if (count < target) lo = mid + 1;                    // median is bigger
                else hi = mid;                                       // mid could be the median
            }
            return lo;
        }

        int main() {
            cout << median({{1, 3, 5}, {2, 6, 9}, {3, 6, 9}}) << "\n";
            cout << median({{5, 10, 20, 30, 40}, {1, 2, 3, 4, 6}, {11, 13, 15, 17, 19}}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int upperBound(int[] row, int x) {        // first index with row[idx] > x
                int lo = 0, hi = row.length;
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (row[mid] <= x) lo = mid + 1; else hi = mid;
                }
                return lo;
            }

            static int median(int[][] mat) {
                int R = mat.length, C = mat[0].length;
                int lo = mat[0][0], hi = mat[0][C - 1];
                for (int i = 1; i < R; i++) {
                    lo = Math.min(lo, mat[i][0]);
                    hi = Math.max(hi, mat[i][C - 1]);
                }
                int target = (R * C + 1) / 2;                 // rank of the median
                while (lo < hi) {
                    int mid = lo + (hi - lo) / 2;
                    int count = 0;
                    for (int[] row : mat) count += upperBound(row, mid);   // elements <= mid
                    if (count < target) lo = mid + 1;         // median is bigger
                    else hi = mid;                            // mid could be the median
                }
                return lo;
            }

            public static void main(String[] args) {
                System.out.println(median(new int[][]{{1, 3, 5}, {2, 6, 9}, {3, 6, 9}}));
                System.out.println(median(new int[][]{{5, 10, 20, 30, 40}, {1, 2, 3, 4, 6}, {11, 13, 15, 17, 19}}));
            }
        }
    ''', js=r'''
        function upperBound(row, x) {                    // first index with row[idx] > x
            let lo = 0, hi = row.length;
            while (lo < hi) {
                const mid = (lo + hi) >> 1;
                if (row[mid] <= x) lo = mid + 1; else hi = mid;
            }
            return lo;
        }

        function median(mat) {
            const R = mat.length, C = mat[0].length;
            let lo = Math.min(...mat.map(row => row[0]));
            let hi = Math.max(...mat.map(row => row[C - 1]));
            const target = Math.floor((R * C + 1) / 2);  // rank of the median
            while (lo < hi) {
                const mid = Math.floor((lo + hi) / 2);
                let count = 0;
                for (const row of mat) count += upperBound(row, mid);   // elements <= mid
                if (count < target) lo = mid + 1;        // median is bigger
                else hi = mid;                           // mid could be the median
            }
            return lo;
        }

        console.log(median([[1, 3, 5], [2, 6, 9], [3, 6, 9]]));
        console.log(median([[5, 10, 20, 30, 40], [1, 2, 3, 4, 6], [11, 13, 15, 17, 19]]));
    ''')
    yield complexity("O(R · log C · log(max − min))", "O(1)")
    yield pitfall("The original notes ran this on the 4 × 4 matrix `1..16` and claimed the output `20` — an even count has no single middle element and `20` is not even in the matrix. For an even `R × C`, run the search twice for ranks `RC/2` and `RC/2 + 1` and average the two values.")
    yield note("`upper_bound` (count of elements `≤ mid`) is what makes duplicates work: with `bisect_left` / `lower_bound` the count would exclude copies of `mid` itself and the search could overshoot.")

    yield section("Interview Q&A", "message-question")
    yield qa("How do you rotate a square matrix 90° in place?",
             "Transpose it (swap `mat[i][j]` with `mat[j][i]` for `j > i`), then reverse the row order for an anticlockwise rotation or reverse each row for a clockwise one. Both steps are `O(N²)` time and `O(1)` extra space. A non-square matrix changes shape, so it needs a new `C × R` array.")
    yield qa("Why does the staircase search start at the top-right (or bottom-left) corner?",
             "At the top-right corner the two possible moves point in opposite directions in terms of value: left is smaller, down is larger. One comparison therefore discards a whole row or column. At the top-left corner both right and down are larger, so a comparison cannot eliminate anything.")
    yield qa("What is the time complexity of the staircase search and why?",
             "`O(R + C)`. Every step moves either one column left or one row down, and neither pointer ever reverses, so there are at most `C` left moves and `R` down moves.")
    yield qa("How does binary search on the answer find the median of a row-wise sorted matrix?",
             "The predicate 'at least `(RC+1)/2` elements are `≤ m`' is false for small `m` and true for large `m`, so binary search over the value range `[min, max]` finds the smallest `m` that satisfies it — the median. Each probe costs `O(R log C)` using `upper_bound` on every row, giving `O(R · log C · log(max − min))` overall with `O(1)` extra space.")
    yield qa("What goes wrong with `[[0] * cols] * rows` in Python?",
             "The outer `*` copies the *reference* to a single inner list, so all rows alias the same object and `mat[0][0] = 1` changes column 0 of every row. Use a comprehension, `[[0] * cols for _ in range(rows)]`, which creates a fresh list per row. JavaScript's `Array(rows).fill([])` has the same bug.")
    yield qa("How would you print a matrix in spiral order without the boundary-crossing bugs?",
             "Keep `top`, `bottom`, `left`, `right`. Print the top row and right column unconditionally, then print the bottom row only if `top <= bottom` and the left column only if `left <= right`. Those two guards prevent re-printing the middle row or column of a non-square matrix on its last ring.")
