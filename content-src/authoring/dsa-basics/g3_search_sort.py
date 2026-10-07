from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Searching & Sorting"


@topic(G, "searching", "Searching", "search")
def _():
    yield lead("Searching is finding **where** (or whether) a value lives in a collection. Linear search works on anything in `O(n)`; binary search needs sorted data and answers in `O(log n)` — and the same halving trick solves a whole family of problems: first/last occurrence, counting, square roots, peaks.")
    yield define("Searching", "given a collection and a *key* `x`, return the index of an element equal to `x` (or `-1` / *not found*). The two fundamental strategies are **linear search** (look at every element) and **binary search** (halve a *sorted* range each step).")

    yield section("Linear search vs binary search", "scale")
    yield table(
        ["", "Linear search", "Binary search"],
        ["Requirement", "none — any order, any container", "data **sorted** (and random access, e.g. an array)"],
        ["Best case", "`O(1)` — first element", "`O(1)` — middle element"],
        ["Average / worst", "`O(n)`", "`O(log n)`"],
        ["Comparisons for n = 1,000,000", "up to 1,000,000", "at most 20"],
        ["Space", "`O(1)`", "`O(1)` iterative · `O(log n)` recursive (call stack)"],
        ["Works on linked lists?", "yes", "no — no `O(1)` jump to the middle"],
        ["Use when", "data is unsorted or tiny, or you search once", "data is sorted and searched many times"],
    )
    yield note("Sorting an unsorted array just to binary-search it **once** costs `O(n log n)` — more than the `O(n)` linear search. Binary search pays off when the array is already sorted or is queried repeatedly.")

    yield section("Linear search", "list-search")
    yield io("arr = [10, 20, 30, 40, 50], x = 30", "2", "arr = [10, 20, 30, 40, 50], x = 35", "-1")
    yield idea("Walk the array from left to right and stop at the first element equal to `x`. Nothing is assumed about the order, so this is the only option for unsorted data.")
    yield multi('''
        index of 30: 2
        index of 35: -1
    ''', py='''
        def linear_search(arr, x):
            for i in range(len(arr)):
                if arr[i] == x:          # first match wins
                    return i
            return -1

        arr = [10, 20, 30, 40, 50]
        print("index of 30:", linear_search(arr, 30))
        print("index of 35:", linear_search(arr, 35))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int linearSearch(const vector<int>& arr, int x) {
            int n = arr.size();
            for (int i = 0; i < n; i++)
                if (arr[i] == x) return i;   // first match wins
            return -1;
        }

        int main() {
            vector<int> arr = {10, 20, 30, 40, 50};
            cout << "index of 30: " << linearSearch(arr, 30) << "\\n";
            cout << "index of 35: " << linearSearch(arr, 35) << "\\n";
        }
    ''', java='''
        public class Main {
            static int linearSearch(int[] arr, int x) {
                for (int i = 0; i < arr.length; i++)
                    if (arr[i] == x) return i;   // first match wins
                return -1;
            }

            public static void main(String[] args) {
                int[] arr = {10, 20, 30, 40, 50};
                System.out.println("index of 30: " + linearSearch(arr, 30));
                System.out.println("index of 35: " + linearSearch(arr, 35));
            }
        }
    ''', js='''
        function linearSearch(arr, x) {
            for (let i = 0; i < arr.length; i++)
                if (arr[i] === x) return i;      // first match wins
            return -1;
        }

        const arr = [10, 20, 30, 40, 50];
        console.log("index of 30:", linearSearch(arr, 30));
        console.log("index of 35:", linearSearch(arr, 35));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Every language has this built in: Python `arr.index(x)` / `x in arr`, C++ `std::find`, Java `List.indexOf`, JavaScript `arr.indexOf(x)` / `arr.includes(x)`. They are all linear scans.")

    yield section("Binary search", "binary")
    yield io("arr = [10, 20, 30, 40, 50, 60], x = 40", "3", "arr = [10, 20, 30, 40, 50, 60], x = 25", "-1")
    yield idea("Because the array is sorted, comparing `x` with the **middle** element tells you which half can contain it — the other half is discarded without looking at it. Each step halves the search range, so `n` elements need only about `log2 n` steps.")
    yield diagram('''
        x = 40          index:  0    1    2    3    4    5
                              [10,  20,  30,  40,  50,  60]
        step 1  low=0 high=5    ^         mid=2 (30) < 40  →  low = mid + 1
        step 2  low=3 high=5                   ^    mid=4 (50) > 40  →  high = mid - 1
        step 3  low=3 high=3                   mid=3 (40) == 40  →  found at 3
    ''', "Binary search for 40: the range shrinks 6 → 3 → 1")
    yield steps(
        ("Set the range", "`low = 0`, `high = n - 1` — the key, if present, is inside `arr[low..high]`."),
        ("Look at the middle", "`mid = low + (high - low) // 2`. If `arr[mid] == x` — done."),
        ("Discard a half", "`arr[mid] < x` → `x` can only be to the right: `low = mid + 1`. `arr[mid] > x` → `high = mid - 1`."),
        ("Stop when the range is empty", "`low > high` means no element can equal `x` → return `-1`."),
    )
    yield multi('''
        index of 40: 3
        index of 25: -1
        index of 10: 0
    ''', py='''
        def binary_search(arr, x):
            low, high = 0, len(arr) - 1
            while low <= high:                   # range arr[low..high] is non-empty
                mid = low + (high - low) // 2    # never overflows (matters in C++/Java)
                if arr[mid] == x:
                    return mid
                elif arr[mid] < x:
                    low = mid + 1                # x is in the right half
                else:
                    high = mid - 1               # x is in the left half
            return -1

        arr = [10, 20, 30, 40, 50, 60]
        print("index of 40:", binary_search(arr, 40))
        print("index of 25:", binary_search(arr, 25))
        print("index of 10:", binary_search(arr, 10))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int binarySearch(const vector<int>& arr, int x) {
            int low = 0, high = (int)arr.size() - 1;
            while (low <= high) {                  // range arr[low..high] is non-empty
                int mid = low + (high - low) / 2;  // never overflows, unlike (low + high) / 2
                if (arr[mid] == x) return mid;
                else if (arr[mid] < x) low = mid + 1;    // x is in the right half
                else high = mid - 1;                     // x is in the left half
            }
            return -1;
        }

        int main() {
            vector<int> arr = {10, 20, 30, 40, 50, 60};
            cout << "index of 40: " << binarySearch(arr, 40) << "\\n";
            cout << "index of 25: " << binarySearch(arr, 25) << "\\n";
            cout << "index of 10: " << binarySearch(arr, 10) << "\\n";
        }
    ''', java='''
        public class Main {
            static int binarySearch(int[] arr, int x) {
                int low = 0, high = arr.length - 1;
                while (low <= high) {                  // range arr[low..high] is non-empty
                    int mid = low + (high - low) / 2;  // never overflows, unlike (low + high) / 2
                    if (arr[mid] == x) return mid;
                    else if (arr[mid] < x) low = mid + 1;    // x is in the right half
                    else high = mid - 1;                     // x is in the left half
                }
                return -1;
            }

            public static void main(String[] args) {
                int[] arr = {10, 20, 30, 40, 50, 60};
                System.out.println("index of 40: " + binarySearch(arr, 40));
                System.out.println("index of 25: " + binarySearch(arr, 25));
                System.out.println("index of 10: " + binarySearch(arr, 10));
            }
        }
    ''', js='''
        function binarySearch(arr, x) {
            let low = 0, high = arr.length - 1;
            while (low <= high) {                              // range arr[low..high] is non-empty
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] === x) return mid;
                else if (arr[mid] < x) low = mid + 1;          // x is in the right half
                else high = mid - 1;                           // x is in the left half
            }
            return -1;
        }

        const arr = [10, 20, 30, 40, 50, 60];
        console.log("index of 40:", binarySearch(arr, 40));
        console.log("index of 25:", binarySearch(arr, 25));
        console.log("index of 10:", binarySearch(arr, 10));
    ''')
    yield complexity("O(log n)", "O(1)")
    yield pitfall("`mid = (low + high) / 2` overflows a 32-bit `int` in C++/Java when `low + high > 2^31 - 1` (arrays of a billion elements — this was a real bug in the JDK for nine years). Always write `low + (high - low) / 2`. In JavaScript use `Math.floor` — `/` gives a fractional index.")
    yield pitfall("Off-by-one loops. The loop condition is `low <= high` (not `<`), and the updates must be `mid + 1` / `mid - 1` — using `low = mid` can loop forever when `low == high - 1`.")

    yield section("Binary search, recursive", "repeat")
    yield p("The same algorithm expressed with recursion: the function searches `arr[low..high]` and calls itself on one half. It is *tail recursive* — the recursive call is the last thing done — so many compilers turn it into the loop above; Python does not, and it uses one stack frame per halving.")
    yield multi('''
        index of 50: 4
        index of 10: 0
        index of 55: -1
    ''', py='''
        def binary_search(arr, x, low, high):
            if low > high:                        # empty range: not found
                return -1
            mid = low + (high - low) // 2
            if arr[mid] == x:
                return mid
            if arr[mid] < x:
                return binary_search(arr, x, mid + 1, high)   # right half
            return binary_search(arr, x, low, mid - 1)        # left half

        arr = [10, 20, 30, 40, 50, 60]
        n = len(arr)
        print("index of 50:", binary_search(arr, 50, 0, n - 1))
        print("index of 10:", binary_search(arr, 10, 0, n - 1))
        print("index of 55:", binary_search(arr, 55, 0, n - 1))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int binarySearch(const vector<int>& arr, int x, int low, int high) {
            if (low > high) return -1;            // empty range: not found
            int mid = low + (high - low) / 2;
            if (arr[mid] == x) return mid;
            if (arr[mid] < x) return binarySearch(arr, x, mid + 1, high);   // right half
            return binarySearch(arr, x, low, mid - 1);                      // left half
        }

        int main() {
            vector<int> arr = {10, 20, 30, 40, 50, 60};
            int n = arr.size();
            cout << "index of 50: " << binarySearch(arr, 50, 0, n - 1) << "\\n";
            cout << "index of 10: " << binarySearch(arr, 10, 0, n - 1) << "\\n";
            cout << "index of 55: " << binarySearch(arr, 55, 0, n - 1) << "\\n";
        }
    ''', java='''
        public class Main {
            static int binarySearch(int[] arr, int x, int low, int high) {
                if (low > high) return -1;            // empty range: not found
                int mid = low + (high - low) / 2;
                if (arr[mid] == x) return mid;
                if (arr[mid] < x) return binarySearch(arr, x, mid + 1, high);   // right half
                return binarySearch(arr, x, low, mid - 1);                      // left half
            }

            public static void main(String[] args) {
                int[] arr = {10, 20, 30, 40, 50, 60};
                int n = arr.length;
                System.out.println("index of 50: " + binarySearch(arr, 50, 0, n - 1));
                System.out.println("index of 10: " + binarySearch(arr, 10, 0, n - 1));
                System.out.println("index of 55: " + binarySearch(arr, 55, 0, n - 1));
            }
        }
    ''', js='''
        function binarySearch(arr, x, low, high) {
            if (low > high) return -1;                // empty range: not found
            const mid = low + Math.floor((high - low) / 2);
            if (arr[mid] === x) return mid;
            if (arr[mid] < x) return binarySearch(arr, x, mid + 1, high);   // right half
            return binarySearch(arr, x, low, mid - 1);                      // left half
        }

        const arr = [10, 20, 30, 40, 50, 60];
        const n = arr.length;
        console.log("index of 50:", binarySearch(arr, 50, 0, n - 1));
        console.log("index of 10:", binarySearch(arr, 10, 0, n - 1));
        console.log("index of 55:", binarySearch(arr, 55, 0, n - 1));
    ''')
    yield complexity("O(log n)", "O(log n) call stack")

    yield section("Analysis of binary search", "chart-bar")
    yield p("After `k` halvings the range has at most `n / 2^k` elements. The search ends when the range is empty, i.e. when `n / 2^k < 1`, so `k ≤ log2 n + 1`. Every step does one comparison (two in the worst case), which gives the recurrence and the bound below.")
    yield formula("T(n) = T(n / 2) + Θ(1)  ⇒  T(n) = Θ(log n)")
    yield table(
        ["Case", "When", "Time"],
        ["Best", "`x` is the first middle element", "`Θ(1)`"],
        ["Average", "`x` anywhere, or absent", "`Θ(log n)`"],
        ["Worst", "`x` absent, or found on the last halving", "`Θ(log n)` — ⌊log2 n⌋ + 1 iterations"],
        ["Space (iterative)", "three indices", "`O(1)`"],
        ["Space (recursive)", "one frame per halving", "`O(log n)`"],
    )
    yield table(
        ["n", "16", "1,024", "1,000,000", "1,000,000,000"],
        ["Max halvings (⌊log2 n⌋ + 1)", "5", "11", "20", "30"],
    )
    yield note("The halving idea is more general than *find x*. Whenever a predicate is **monotonic** over a range — `false false false true true true` — binary search finds the boundary in `O(log n)`. Every problem below is an instance of that: first/last occurrence, counting 1s, floor of a square root, peak element.")

    yield section("Binary search on an unsorted list", "arrows-sort")
    yield p("Binary search is meaningless on unsorted data: discarding a half assumes the half cannot contain `x`. The only ways to use it are to **sort first** (and then search the sorted array — the indices refer to the sorted order) or to exploit some other structure, like the slope of a mountain array below.")
    yield io("arr = [3, 6, 1, 9, 4, 2], x = 3", "sorted: 1 2 3 4 6 9 — index 2 in the sorted array")
    yield multi('''
        original: 3 6 1 9 4 2
        sorted copy: 1 2 3 4 6 9
        index of 3 in sorted copy: 2
        index of 3 in original: 0
    ''', py='''
        def binary_search(arr, x):
            low, high = 0, len(arr) - 1
            while low <= high:
                mid = low + (high - low) // 2
                if arr[mid] == x:
                    return mid
                if arr[mid] < x:
                    low = mid + 1
                else:
                    high = mid - 1
            return -1

        arr = [3, 6, 1, 9, 4, 2]
        aux = sorted(arr)                      # O(n log n) copy; arr keeps its order
        print("original:", *arr)
        print("sorted copy:", *aux)
        print("index of 3 in sorted copy:", binary_search(aux, 3))
        print("index of 3 in original:", arr.index(3))      # linear search
    ''', cpp='''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        int binarySearch(const vector<int>& arr, int x) {
            int low = 0, high = (int)arr.size() - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (arr[mid] == x) return mid;
                if (arr[mid] < x) low = mid + 1; else high = mid - 1;
            }
            return -1;
        }

        void show(const char* label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        int main() {
            vector<int> arr = {3, 6, 1, 9, 4, 2};
            vector<int> aux = arr;                 // copy, then sort the copy: O(n log n)
            sort(aux.begin(), aux.end());
            show("original:", arr);
            show("sorted copy:", aux);
            cout << "index of 3 in sorted copy: " << binarySearch(aux, 3) << "\\n";
            int pos = find(arr.begin(), arr.end(), 3) - arr.begin();     // linear search
            cout << "index of 3 in original: " << pos << "\\n";
        }
    ''', java='''
        import java.util.Arrays;

        public class Main {
            static int binarySearch(int[] arr, int x) {
                int low = 0, high = arr.length - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (arr[mid] == x) return mid;
                    if (arr[mid] < x) low = mid + 1; else high = mid - 1;
                }
                return -1;
            }

            static String join(int[] a) {
                StringBuilder sb = new StringBuilder();
                for (int x : a) sb.append(' ').append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                int[] arr = {3, 6, 1, 9, 4, 2};
                int[] aux = arr.clone();               // copy, then sort the copy: O(n log n)
                Arrays.sort(aux);
                System.out.println("original:" + join(arr));
                System.out.println("sorted copy:" + join(aux));
                System.out.println("index of 3 in sorted copy: " + binarySearch(aux, 3));
                int pos = -1;                           // linear search
                for (int i = 0; i < arr.length; i++) if (arr[i] == 3) { pos = i; break; }
                System.out.println("index of 3 in original: " + pos);
            }
        }
    ''', js='''
        function binarySearch(arr, x) {
            let low = 0, high = arr.length - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] === x) return mid;
                if (arr[mid] < x) low = mid + 1; else high = mid - 1;
            }
            return -1;
        }

        const arr = [3, 6, 1, 9, 4, 2];
        const aux = [...arr].sort((a, b) => a - b);   // copy, then sort the copy (numeric comparator!)
        console.log("original:", arr.join(" "));
        console.log("sorted copy:", aux.join(" "));
        console.log("index of 3 in sorted copy:", binarySearch(aux, 3));
        console.log("index of 3 in original:", arr.indexOf(3));     // linear search
    ''')
    yield complexity("O(n log n) sort + O(log n) per query", "O(n) for the copy")
    yield pitfall("The index returned is a position in the **sorted** array, not in the original. If the caller needs original positions, sort an array of `(value, index)` pairs, or sort the indices by value.")

    yield section("Peak element in a mountain array", "mountain")
    yield io("nums = [1, 2, 1, 3, 5, 6, 4]", "5 (nums[5] = 6 is greater than both neighbours)", "nums = [1, 2, 3, 1]", "2")
    yield idea("A **peak** is an element not smaller than its neighbours. Binary search works without sorting because the slope at `mid` tells you where a peak must exist: if `nums[mid] < nums[mid + 1]` you are on an *ascending* slope, so a peak lies to the right (the array must come down eventually — or end, and the last element is then a peak). Otherwise a peak lies at `mid` or to its left.")
    yield multi('''
        peak at index 5 (value 6)
        peak at index 2 (value 3)
    ''', py='''
        def find_peak(nums):
            left, right = 0, len(nums) - 1
            while left < right:                     # stop when one candidate is left
                mid = left + (right - left) // 2
                if nums[mid] < nums[mid + 1]:
                    left = mid + 1                  # ascending: a peak is to the right
                else:
                    right = mid                     # mid may itself be the peak
            return left

        for nums in ([1, 2, 1, 3, 5, 6, 4], [1, 2, 3, 1]):
            i = find_peak(nums)
            print(f"peak at index {i} (value {nums[i]})")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int findPeak(const vector<int>& nums) {
            int left = 0, right = (int)nums.size() - 1;
            while (left < right) {                   // stop when one candidate is left
                int mid = left + (right - left) / 2;
                if (nums[mid] < nums[mid + 1]) left = mid + 1;   // ascending: a peak is to the right
                else right = mid;                                // mid may itself be the peak
            }
            return left;
        }

        int main() {
            vector<vector<int>> tests = {{1, 2, 1, 3, 5, 6, 4}, {1, 2, 3, 1}};
            for (const auto& nums : tests) {
                int i = findPeak(nums);
                cout << "peak at index " << i << " (value " << nums[i] << ")\\n";
            }
        }
    ''', java='''
        public class Main {
            static int findPeak(int[] nums) {
                int left = 0, right = nums.length - 1;
                while (left < right) {                   // stop when one candidate is left
                    int mid = left + (right - left) / 2;
                    if (nums[mid] < nums[mid + 1]) left = mid + 1;   // ascending: a peak is to the right
                    else right = mid;                                // mid may itself be the peak
                }
                return left;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 2, 1, 3, 5, 6, 4}, {1, 2, 3, 1}};
                for (int[] nums : tests) {
                    int i = findPeak(nums);
                    System.out.println("peak at index " + i + " (value " + nums[i] + ")");
                }
            }
        }
    ''', js='''
        function findPeak(nums) {
            let left = 0, right = nums.length - 1;
            while (left < right) {                       // stop when one candidate is left
                const mid = left + Math.floor((right - left) / 2);
                if (nums[mid] < nums[mid + 1]) left = mid + 1;   // ascending: a peak is to the right
                else right = mid;                                // mid may itself be the peak
            }
            return left;
        }

        for (const nums of [[1, 2, 1, 3, 5, 6, 4], [1, 2, 3, 1]]) {
            const i = findPeak(nums);
            console.log(`peak at index ${i} (value ${nums[i]})`);
        }
    ''')
    yield complexity("O(log n)", "O(1)")
    yield note("`[1, 2, 1, 3, 5, 6, 4]` has two peaks (index 1 and index 5); binary search returns *a* peak, not necessarily the first one. Note the loop uses `left < right` and `right = mid` (not `mid - 1`) because `mid` itself may be the answer — and `mid + 1` is always in range since `mid < right`.")

    yield section("Index of first occurrence in a sorted array", "arrow-bar-to-left")
    yield io("arr = [10, 10, 20, 30, 40, 40, 40, 40], x = 20", "2", "arr = [10, 10, 20, 30, 40, 40, 40, 40], x = 40", "4", "x = 25", "-1")
    yield p("The naive solution scans from the left and returns the first match — `O(n)`, and the only option when the array is unsorted.")
    yield snippet("py", '''
        def first_occurrence_naive(arr, x):
            for i in range(len(arr)):
                if arr[i] == x:
                    return i          # the first match from the left
            return -1

        arr = [1, 10, 20, 10, 20, 30, 30, 10]      # unsorted — only a scan works
        print(first_occurrence_naive(arr, 20))
    ''', out="2")
    yield idea("Plain binary search stops at *any* `x`. To get the **first** one, when `arr[mid] == x` check whether it is the first: it is if `mid == 0` or `arr[mid - 1] < x` (equivalently `x > arr[mid - 1]`). Otherwise there are more copies to the left — keep searching the left half (`high = mid - 1`). The other two cases are unchanged.")
    yield steps(
        ("`arr[mid] < x`", "Search right: `low = mid + 1`."),
        ("`arr[mid] > x`", "Search left: `high = mid - 1`."),
        ("`arr[mid] == x` and (`mid == 0` or `arr[mid - 1] != x`)", "This is the first occurrence → return `mid`."),
        ("`arr[mid] == x` otherwise", "A copy exists to the left → `high = mid - 1`."),
    )
    yield multi('''
        first 20: recursive 2, iterative 2
        first 40: recursive 4, iterative 4
        first 25: recursive -1, iterative -1
    ''', py='''
        def first_rec(arr, low, high, x):
            if low > high:
                return -1
            mid = low + (high - low) // 2
            if arr[mid] < x:
                return first_rec(arr, mid + 1, high, x)
            if arr[mid] > x:
                return first_rec(arr, low, mid - 1, x)
            if mid == 0 or arr[mid - 1] != x:        # arr[mid] == x and nothing equal before it
                return mid
            return first_rec(arr, low, mid - 1, x)   # more copies to the left

        def first_iter(arr, x):
            low, high = 0, len(arr) - 1
            while low <= high:
                mid = low + (high - low) // 2
                if arr[mid] < x:
                    low = mid + 1
                elif arr[mid] > x:
                    high = mid - 1
                elif mid == 0 or arr[mid - 1] != x:
                    return mid
                else:
                    high = mid - 1                   # more copies to the left
            return -1

        arr = [10, 10, 20, 30, 40, 40, 40, 40]
        for x in (20, 40, 25):
            print(f"first {x}: recursive {first_rec(arr, 0, len(arr) - 1, x)}, iterative {first_iter(arr, x)}")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int firstRec(const vector<int>& arr, int low, int high, int x) {
            if (low > high) return -1;
            int mid = low + (high - low) / 2;
            if (arr[mid] < x) return firstRec(arr, mid + 1, high, x);
            if (arr[mid] > x) return firstRec(arr, low, mid - 1, x);
            if (mid == 0 || arr[mid - 1] != x) return mid;   // arr[mid] == x and nothing equal before it
            return firstRec(arr, low, mid - 1, x);           // more copies to the left
        }

        int firstIter(const vector<int>& arr, int x) {
            int low = 0, high = (int)arr.size() - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (arr[mid] < x) low = mid + 1;
                else if (arr[mid] > x) high = mid - 1;
                else if (mid == 0 || arr[mid - 1] != x) return mid;
                else high = mid - 1;                         // more copies to the left
            }
            return -1;
        }

        int main() {
            vector<int> arr = {10, 10, 20, 30, 40, 40, 40, 40};
            int n = arr.size();
            for (int x : {20, 40, 25})
                cout << "first " << x << ": recursive " << firstRec(arr, 0, n - 1, x)
                     << ", iterative " << firstIter(arr, x) << "\\n";
        }
    ''', java='''
        public class Main {
            static int firstRec(int[] arr, int low, int high, int x) {
                if (low > high) return -1;
                int mid = low + (high - low) / 2;
                if (arr[mid] < x) return firstRec(arr, mid + 1, high, x);
                if (arr[mid] > x) return firstRec(arr, low, mid - 1, x);
                if (mid == 0 || arr[mid - 1] != x) return mid;   // arr[mid] == x and nothing equal before it
                return firstRec(arr, low, mid - 1, x);           // more copies to the left
            }

            static int firstIter(int[] arr, int x) {
                int low = 0, high = arr.length - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (arr[mid] < x) low = mid + 1;
                    else if (arr[mid] > x) high = mid - 1;
                    else if (mid == 0 || arr[mid - 1] != x) return mid;
                    else high = mid - 1;                         // more copies to the left
                }
                return -1;
            }

            public static void main(String[] args) {
                int[] arr = {10, 10, 20, 30, 40, 40, 40, 40};
                for (int x : new int[]{20, 40, 25})
                    System.out.println("first " + x + ": recursive " + firstRec(arr, 0, arr.length - 1, x)
                                       + ", iterative " + firstIter(arr, x));
            }
        }
    ''', js='''
        function firstRec(arr, low, high, x) {
            if (low > high) return -1;
            const mid = low + Math.floor((high - low) / 2);
            if (arr[mid] < x) return firstRec(arr, mid + 1, high, x);
            if (arr[mid] > x) return firstRec(arr, low, mid - 1, x);
            if (mid === 0 || arr[mid - 1] !== x) return mid;   // arr[mid] == x and nothing equal before it
            return firstRec(arr, low, mid - 1, x);             // more copies to the left
        }

        function firstIter(arr, x) {
            let low = 0, high = arr.length - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] < x) low = mid + 1;
                else if (arr[mid] > x) high = mid - 1;
                else if (mid === 0 || arr[mid - 1] !== x) return mid;
                else high = mid - 1;                           // more copies to the left
            }
            return -1;
        }

        const arr = [10, 10, 20, 30, 40, 40, 40, 40];
        for (const x of [20, 40, 25])
            console.log(`first ${x}: recursive ${firstRec(arr, 0, arr.length - 1, x)}, iterative ${firstIter(arr, x)}`);
    ''')
    yield complexity("O(log n)", "O(1) iterative · O(log n) recursive")
    yield note("This is exactly what `bisect_left` (Python) and `lower_bound` (C++) compute — the first position whose value is `≥ x` — except that they return the insertion point instead of `-1` when `x` is absent.")

    yield section("Index of last occurrence in a sorted array", "arrow-bar-to-right")
    yield io("arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8], x = 8", "9", "arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8], x = 2", "4", "x = 5", "-1")
    yield p("Naive: scan the whole array and remember the last index where `arr[i] == x` (or scan from the right and stop at the first match) — `O(n)`, works unsorted.")
    yield snippet("py", '''
        def last_occurrence_naive(arr, x):
            last = -1
            for i in range(len(arr)):
                if arr[i] == x:
                    last = i              # keep overwriting: the final value is the last match
            return last

        arr = [10, 20, 30, 20, 30, 40, 40, 40]
        print(last_occurrence_naive(arr, 30))
        print(last_occurrence_naive(arr, 50))
    ''', out="4\n-1")
    yield idea("Mirror image of first occurrence: when `arr[mid] == x`, it is the last one if `mid == n - 1` or `arr[mid + 1] != x`; otherwise more copies lie to the right, so continue with `low = mid + 1`.")
    yield multi('''
        last 8: recursive 9, iterative 9
        last 2: recursive 4, iterative 4
        last 5: recursive -1, iterative -1
    ''', py='''
        def last_rec(arr, low, high, x):
            if low > high:
                return -1
            mid = low + (high - low) // 2
            if arr[mid] < x:
                return last_rec(arr, mid + 1, high, x)
            if arr[mid] > x:
                return last_rec(arr, low, mid - 1, x)
            if mid == len(arr) - 1 or arr[mid + 1] != x:   # nothing equal after it
                return mid
            return last_rec(arr, mid + 1, high, x)         # more copies to the right

        def last_iter(arr, x):
            low, high = 0, len(arr) - 1
            while low <= high:
                mid = low + (high - low) // 2
                if arr[mid] < x:
                    low = mid + 1
                elif arr[mid] > x:
                    high = mid - 1
                elif mid == len(arr) - 1 or arr[mid + 1] != x:
                    return mid
                else:
                    low = mid + 1                          # more copies to the right
            return -1

        arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8]
        for x in (8, 2, 5):
            print(f"last {x}: recursive {last_rec(arr, 0, len(arr) - 1, x)}, iterative {last_iter(arr, x)}")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int lastRec(const vector<int>& arr, int low, int high, int x) {
            if (low > high) return -1;
            int mid = low + (high - low) / 2;
            if (arr[mid] < x) return lastRec(arr, mid + 1, high, x);
            if (arr[mid] > x) return lastRec(arr, low, mid - 1, x);
            if (mid == (int)arr.size() - 1 || arr[mid + 1] != x) return mid;   // nothing equal after it
            return lastRec(arr, mid + 1, high, x);                             // more copies to the right
        }

        int lastIter(const vector<int>& arr, int x) {
            int n = arr.size(), low = 0, high = n - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (arr[mid] < x) low = mid + 1;
                else if (arr[mid] > x) high = mid - 1;
                else if (mid == n - 1 || arr[mid + 1] != x) return mid;
                else low = mid + 1;                                            // more copies to the right
            }
            return -1;
        }

        int main() {
            vector<int> arr = {1, 2, 2, 2, 2, 3, 4, 7, 8, 8};
            int n = arr.size();
            for (int x : {8, 2, 5})
                cout << "last " << x << ": recursive " << lastRec(arr, 0, n - 1, x)
                     << ", iterative " << lastIter(arr, x) << "\\n";
        }
    ''', java='''
        public class Main {
            static int lastRec(int[] arr, int low, int high, int x) {
                if (low > high) return -1;
                int mid = low + (high - low) / 2;
                if (arr[mid] < x) return lastRec(arr, mid + 1, high, x);
                if (arr[mid] > x) return lastRec(arr, low, mid - 1, x);
                if (mid == arr.length - 1 || arr[mid + 1] != x) return mid;   // nothing equal after it
                return lastRec(arr, mid + 1, high, x);                        // more copies to the right
            }

            static int lastIter(int[] arr, int x) {
                int n = arr.length, low = 0, high = n - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (arr[mid] < x) low = mid + 1;
                    else if (arr[mid] > x) high = mid - 1;
                    else if (mid == n - 1 || arr[mid + 1] != x) return mid;
                    else low = mid + 1;                                       // more copies to the right
                }
                return -1;
            }

            public static void main(String[] args) {
                int[] arr = {1, 2, 2, 2, 2, 3, 4, 7, 8, 8};
                for (int x : new int[]{8, 2, 5})
                    System.out.println("last " + x + ": recursive " + lastRec(arr, 0, arr.length - 1, x)
                                       + ", iterative " + lastIter(arr, x));
            }
        }
    ''', js='''
        function lastRec(arr, low, high, x) {
            if (low > high) return -1;
            const mid = low + Math.floor((high - low) / 2);
            if (arr[mid] < x) return lastRec(arr, mid + 1, high, x);
            if (arr[mid] > x) return lastRec(arr, low, mid - 1, x);
            if (mid === arr.length - 1 || arr[mid + 1] !== x) return mid;   // nothing equal after it
            return lastRec(arr, mid + 1, high, x);                          // more copies to the right
        }

        function lastIter(arr, x) {
            let low = 0, high = arr.length - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] < x) low = mid + 1;
                else if (arr[mid] > x) high = mid - 1;
                else if (mid === arr.length - 1 || arr[mid + 1] !== x) return mid;
                else low = mid + 1;                                         // more copies to the right
            }
            return -1;
        }

        const arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8];
        for (const x of [8, 2, 5])
            console.log(`last ${x}: recursive ${lastRec(arr, 0, arr.length - 1, x)}, iterative ${lastIter(arr, x)}`);
    ''')
    yield complexity("O(log n)", "O(1) iterative · O(log n) recursive")
    yield pitfall("Checking `arr[mid + 1]` before `mid == n - 1` reads past the end of the array (undefined behaviour in C++, an exception in Java, `undefined` in JavaScript). Keep the bounds test **first** in the `or` — short-circuit evaluation then skips the access.")

    yield section("Count occurrences in a sorted array", "sum")
    yield io("arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8], x = 2", "4", "arr = [10, 20, 20, 20, 30, 30], x = 20", "3", "x = 25", "0")
    yield table(
        ["Approach", "How", "Time"],
        ["Naive", "Linear scan, count matches", "`O(n)`"],
        ["Better", "One binary search to find any `x`, then expand left and right over the copies", "`O(log n + k)` for `k` copies — `O(n)` when every element is `x`"],
        ["Efficient", "Two binary searches: `last − first + 1`", "`O(log n)`"],
    )
    yield idea("Copies of `x` sit in one contiguous block of a sorted array. Find the block's two ends with the first-occurrence and last-occurrence searches above; the count is `last − first + 1`, or `0` when `first` is `-1`. One parameterised search (`find_first = true/false`) does both jobs: on a match it records the index and keeps going left or right.")
    yield multi('''
        count of 2: 4
        count of 8: 2
        count of 5: 0
        count of 20 in [10 20 20 20 30 30]: 3
    ''', py='''
        def bound(arr, x, find_first):
            answer, low, high = -1, 0, len(arr) - 1
            while low <= high:
                mid = low + (high - low) // 2
                if arr[mid] < x:
                    low = mid + 1
                elif arr[mid] > x:
                    high = mid - 1
                else:
                    answer = mid                 # a match — remember it, then keep looking ...
                    if find_first:
                        high = mid - 1           # ... further left
                    else:
                        low = mid + 1            # ... further right
            return answer

        def count_occurrences(arr, x):
            first = bound(arr, x, True)
            if first == -1:
                return 0
            return bound(arr, x, False) - first + 1

        arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8]
        for x in (2, 8, 5):
            print(f"count of {x}:", count_occurrences(arr, x))
        print("count of 20 in [10 20 20 20 30 30]:", count_occurrences([10, 20, 20, 20, 30, 30], 20))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int bound(const vector<int>& arr, int x, bool findFirst) {
            int answer = -1, low = 0, high = (int)arr.size() - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (arr[mid] < x) low = mid + 1;
                else if (arr[mid] > x) high = mid - 1;
                else {
                    answer = mid;                            // a match — remember it, then keep looking ...
                    if (findFirst) high = mid - 1;           // ... further left
                    else low = mid + 1;                      // ... further right
                }
            }
            return answer;
        }

        int countOccurrences(const vector<int>& arr, int x) {
            int first = bound(arr, x, true);
            if (first == -1) return 0;
            return bound(arr, x, false) - first + 1;
        }

        int main() {
            vector<int> arr = {1, 2, 2, 2, 2, 3, 4, 7, 8, 8};
            for (int x : {2, 8, 5}) cout << "count of " << x << ": " << countOccurrences(arr, x) << "\\n";
            cout << "count of 20 in [10 20 20 20 30 30]: " << countOccurrences({10, 20, 20, 20, 30, 30}, 20) << "\\n";
        }
    ''', java='''
        public class Main {
            static int bound(int[] arr, int x, boolean findFirst) {
                int answer = -1, low = 0, high = arr.length - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (arr[mid] < x) low = mid + 1;
                    else if (arr[mid] > x) high = mid - 1;
                    else {
                        answer = mid;                            // a match — remember it, then keep looking ...
                        if (findFirst) high = mid - 1;           // ... further left
                        else low = mid + 1;                      // ... further right
                    }
                }
                return answer;
            }

            static int countOccurrences(int[] arr, int x) {
                int first = bound(arr, x, true);
                if (first == -1) return 0;
                return bound(arr, x, false) - first + 1;
            }

            public static void main(String[] args) {
                int[] arr = {1, 2, 2, 2, 2, 3, 4, 7, 8, 8};
                for (int x : new int[]{2, 8, 5}) System.out.println("count of " + x + ": " + countOccurrences(arr, x));
                System.out.println("count of 20 in [10 20 20 20 30 30]: " + countOccurrences(new int[]{10, 20, 20, 20, 30, 30}, 20));
            }
        }
    ''', js='''
        function bound(arr, x, findFirst) {
            let answer = -1, low = 0, high = arr.length - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] < x) low = mid + 1;
                else if (arr[mid] > x) high = mid - 1;
                else {
                    answer = mid;                            // a match — remember it, then keep looking ...
                    if (findFirst) high = mid - 1;           // ... further left
                    else low = mid + 1;                      // ... further right
                }
            }
            return answer;
        }

        function countOccurrences(arr, x) {
            const first = bound(arr, x, true);
            if (first === -1) return 0;
            return bound(arr, x, false) - first + 1;
        }

        const arr = [1, 2, 2, 2, 2, 3, 4, 7, 8, 8];
        for (const x of [2, 8, 5]) console.log(`count of ${x}:`, countOccurrences(arr, x));
        console.log("count of 20 in [10 20 20 20 30 30]:", countOccurrences([10, 20, 20, 20, 30, 30], 20));
    ''')
    yield complexity("O(log n)", "O(1)")
    yield pitfall("The original notes labelled a version with two **linear** scans (first from the left, last from the right) as *efficient*. It gives the right answer but is `O(n)` — no better than counting directly. Only the two binary searches reach `O(log n)`.")

    yield section("Count 1's in a sorted binary array", "binary")
    yield io("arr = [1, 1, 0, 0, 0, 0, 0]", "2", "arr = [1, 1, 1, 1, 1, 1, 1]", "7", "arr = [0, 0, 0, 0, 0, 0, 0]", "0")
    yield p("The array is sorted in *descending* order — all the 1s come first, then all the 0s. The naive solution walks from the left and stops at the first 0.")
    yield snippet("py", '''
        def count_ones_naive(arr):
            count = 0
            for v in arr:
                if v == 0:
                    break             # sorted: no more 1s after the first 0
                count += 1
            return count

        print(count_ones_naive([1, 1, 1, 1, 0, 0, 0]))
    ''', out="4")
    yield idea("This is *index of last occurrence* of `1`, plus one. At `mid`: if `arr[mid] == 1` and (`mid` is the last index or `arr[mid + 1] == 0`) it is the last 1 → answer `mid + 1`. If `arr[mid] == 1` otherwise, the boundary is to the right; if `arr[mid] == 0` it is to the left.")
    yield p("**Recursive version** — one call per halving:")
    yield multi('''
        1 1 0 0 0 0 0 -> 2
        1 1 1 1 1 1 1 -> 7
        0 0 0 0 0 0 0 -> 0
        1 1 1 1 0 0 0 -> 4
    ''', py='''
        def count_ones(arr, low, high):
            if low > high:
                return 0                              # no 1 at all
            mid = low + (high - low) // 2
            if arr[mid] == 1 and (mid == high or arr[mid + 1] == 0):
                return mid + 1                        # mid is the last 1
            if arr[mid] == 1:
                return count_ones(arr, mid + 1, high)   # last 1 is further right
            return count_ones(arr, low, mid - 1)        # arr[mid] == 0: look left

        tests = [[1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0]]
        for arr in tests:
            print(*arr, "->", count_ones(arr, 0, len(arr) - 1))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int countOnes(const vector<int>& arr, int low, int high) {
            if (low > high) return 0;                            // no 1 at all
            int mid = low + (high - low) / 2;
            if (arr[mid] == 1 && (mid == high || arr[mid + 1] == 0))
                return mid + 1;                                  // mid is the last 1
            if (arr[mid] == 1) return countOnes(arr, mid + 1, high);   // last 1 is further right
            return countOnes(arr, low, mid - 1);                       // arr[mid] == 0: look left
        }

        int main() {
            vector<vector<int>> tests = {{1, 1, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 1, 1, 1}, {0, 0, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 0, 0, 0}};
            for (const auto& arr : tests) {
                for (int v : arr) cout << v << " ";
                cout << "-> " << countOnes(arr, 0, (int)arr.size() - 1) << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static int countOnes(int[] arr, int low, int high) {
                if (low > high) return 0;                            // no 1 at all
                int mid = low + (high - low) / 2;
                if (arr[mid] == 1 && (mid == high || arr[mid + 1] == 0))
                    return mid + 1;                                  // mid is the last 1
                if (arr[mid] == 1) return countOnes(arr, mid + 1, high);   // last 1 is further right
                return countOnes(arr, low, mid - 1);                       // arr[mid] == 0: look left
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 1, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 1, 1, 1}, {0, 0, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 0, 0, 0}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int v : arr) sb.append(v).append(' ');
                    System.out.println(sb + "-> " + countOnes(arr, 0, arr.length - 1));
                }
            }
        }
    ''', js='''
        function countOnes(arr, low, high) {
            if (low > high) return 0;                                // no 1 at all
            const mid = low + Math.floor((high - low) / 2);
            if (arr[mid] === 1 && (mid === high || arr[mid + 1] === 0))
                return mid + 1;                                      // mid is the last 1
            if (arr[mid] === 1) return countOnes(arr, mid + 1, high);   // last 1 is further right
            return countOnes(arr, low, mid - 1);                        // arr[mid] == 0: look left
        }

        const tests = [[1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0]];
        for (const arr of tests)
            console.log(arr.join(" "), "->", countOnes(arr, 0, arr.length - 1));
    ''')
    yield complexity("O(log n)", "O(log n) call stack")
    yield p("**Iterative version** — same decisions in a loop, `O(1)` space:")
    yield multi('''
        1 1 0 0 0 0 0 -> 2
        1 1 1 1 1 1 1 -> 7
        0 0 0 0 0 0 0 -> 0
        1 1 1 1 0 0 0 -> 4
    ''', py='''
        def count_ones(arr):
            n = len(arr)
            low, high = 0, n - 1
            while low <= high:
                mid = low + (high - low) // 2
                if arr[mid] == 0:
                    high = mid - 1                    # the boundary is to the left
                elif mid == n - 1 or arr[mid + 1] == 0:
                    return mid + 1                    # mid is the last 1
                else:
                    low = mid + 1                     # the boundary is to the right
            return 0

        tests = [[1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0]]
        for arr in tests:
            print(*arr, "->", count_ones(arr))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        int countOnes(const vector<int>& arr) {
            int n = arr.size(), low = 0, high = n - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (arr[mid] == 0) high = mid - 1;                     // the boundary is to the left
                else if (mid == n - 1 || arr[mid + 1] == 0) return mid + 1;   // mid is the last 1
                else low = mid + 1;                                    // the boundary is to the right
            }
            return 0;
        }

        int main() {
            vector<vector<int>> tests = {{1, 1, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 1, 1, 1}, {0, 0, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 0, 0, 0}};
            for (const auto& arr : tests) {
                for (int v : arr) cout << v << " ";
                cout << "-> " << countOnes(arr) << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static int countOnes(int[] arr) {
                int n = arr.length, low = 0, high = n - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (arr[mid] == 0) high = mid - 1;                     // the boundary is to the left
                    else if (mid == n - 1 || arr[mid + 1] == 0) return mid + 1;   // mid is the last 1
                    else low = mid + 1;                                    // the boundary is to the right
                }
                return 0;
            }

            public static void main(String[] args) {
                int[][] tests = {{1, 1, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 1, 1, 1}, {0, 0, 0, 0, 0, 0, 0}, {1, 1, 1, 1, 0, 0, 0}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int v : arr) sb.append(v).append(' ');
                    System.out.println(sb + "-> " + countOnes(arr));
                }
            }
        }
    ''', js='''
        function countOnes(arr) {
            const n = arr.length;
            let low = 0, high = n - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] === 0) high = mid - 1;                        // the boundary is to the left
                else if (mid === n - 1 || arr[mid + 1] === 0) return mid + 1;   // mid is the last 1
                else low = mid + 1;                                        // the boundary is to the right
            }
            return 0;
        }

        const tests = [[1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0]];
        for (const arr of tests)
            console.log(arr.join(" "), "->", countOnes(arr));
    ''')
    yield complexity("O(log n)", "O(1)")
    yield note("If the array were sorted *ascending* (`0 0 0 1 1`), the count of 1s is `n − (index of the first 1)` — the first-occurrence search. Either way it is a boundary search on a monotonic sequence.")

    yield section("Square root (floor) by binary search", "square-root")
    yield io("x = 4", "2", "x = 10", "3 (3² = 9 ≤ 10 < 16 = 4²)", "x = 1000000", "1000")
    yield p("`floor(sqrt(x))` is the largest integer `i` with `i² ≤ x`. The naive solution counts up from 1 until `i² > x` — `O(√x)` iterations.")
    yield snippet("py", '''
        def floor_sqrt_naive(x):
            i = 1
            while i * i <= x:
                i += 1
            return i - 1              # the last i whose square did not exceed x

        print(floor_sqrt_naive(4), floor_sqrt_naive(10), floor_sqrt_naive(1000000))
    ''', out="2 3 1000")
    yield idea("The predicate `mid² ≤ x` is `true` for small `mid` and `false` for large `mid` — monotonic, so binary search over `1..x` finds the boundary. Whenever `mid² ≤ x`, `mid` is a candidate answer: remember it and move right; otherwise move left.")
    yield multi('''
        sqrt(4) = 2
        sqrt(10) = 3
        sqrt(1) = 1
        sqrt(0) = 0
        sqrt(1000000) = 1000
        sqrt(2147395599) = 46339
    ''', py='''
        def floor_sqrt(x):
            low, high, ans = 1, x, 0           # ans = 0 handles x == 0
            while low <= high:
                mid = low + (high - low) // 2
                sq = mid * mid
                if sq == x:
                    return mid
                if sq < x:
                    ans = mid                  # mid works — maybe a bigger one does too
                    low = mid + 1
                else:
                    high = mid - 1
            return ans

        for x in (4, 10, 1, 0, 1000000, 2147395599):
            print(f"sqrt({x}) = {floor_sqrt(x)}")
    ''', cpp='''
        #include <iostream>
        using namespace std;

        long long floorSqrt(long long x) {
            long long low = 1, high = x, ans = 0;   // ans = 0 handles x == 0
            while (low <= high) {
                long long mid = low + (high - low) / 2;
                long long sq = mid * mid;             // long long: mid * mid overflows int for x > 2^31
                if (sq == x) return mid;
                if (sq < x) { ans = mid; low = mid + 1; }   // mid works — maybe a bigger one does too
                else high = mid - 1;
            }
            return ans;
        }

        int main() {
            for (long long x : {4LL, 10LL, 1LL, 0LL, 1000000LL, 2147395599LL})
                cout << "sqrt(" << x << ") = " << floorSqrt(x) << "\\n";
        }
    ''', java='''
        public class Main {
            static long floorSqrt(long x) {
                long low = 1, high = x, ans = 0;      // ans = 0 handles x == 0
                while (low <= high) {
                    long mid = low + (high - low) / 2;
                    long sq = mid * mid;              // long: mid * mid overflows int for x > 2^31
                    if (sq == x) return mid;
                    if (sq < x) { ans = mid; low = mid + 1; }   // mid works — maybe a bigger one does too
                    else high = mid - 1;
                }
                return ans;
            }

            public static void main(String[] args) {
                for (long x : new long[]{4, 10, 1, 0, 1000000, 2147395599L})
                    System.out.println("sqrt(" + x + ") = " + floorSqrt(x));
            }
        }
    ''', js='''
        function floorSqrt(x) {
            let low = 1, high = x, ans = 0;           // ans = 0 handles x == 0
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                const sq = mid * mid;                 // exact up to 2^53 in JavaScript
                if (sq === x) return mid;
                if (sq < x) { ans = mid; low = mid + 1; }   // mid works — maybe a bigger one does too
                else high = mid - 1;
            }
            return ans;
        }

        for (const x of [4, 10, 1, 0, 1000000, 2147395599])
            console.log(`sqrt(${x}) = ${floorSqrt(x)}`);
    ''')
    yield complexity("O(log x)", "O(1)")
    yield pitfall("`mid * mid` overflows a 32-bit `int` once `mid > 46340`. Use `long long` / `long`, or compare `mid <= x / mid` instead of squaring. Also set `high = x / 2` for `x ≥ 2` if you like — the root never exceeds half of `x` there — but the plain `high = x` is correct too.")

    yield section("Built-in search functions", "box")
    yield table(
        ["Language", "Linear", "Binary (sorted input)", "Notes"],
        ["Python", "`x in arr`, `arr.index(x)`", "`bisect.bisect_left(arr, x)`, `bisect_right`", "`bisect_left` returns the insertion point — check `arr[i] == x` yourself"],
        ["C++", "`std::find(b, e, x)`", "`std::binary_search` (bool), `std::lower_bound`, `std::upper_bound`", "`lower_bound` = first element `≥ x`; `upper_bound` = first `> x`; `equal_range` gives both"],
        ["Java", "`list.indexOf(x)`, `list.contains(x)`", "`Arrays.binarySearch(arr, x)`, `Collections.binarySearch`", "returns `-(insertionPoint) - 1` when absent; **any** index among duplicates"],
        ["JavaScript", "`arr.indexOf(x)`, `arr.includes(x)`, `arr.find(fn)`", "*none* — write your own", "`indexOf` uses `===`, so `NaN` is never found (`includes` handles `NaN`)"],
    )
    yield multi('''
        index of 20: 2
        index of 25: -1
    ''', py='''
        from bisect import bisect_left

        def search(arr, x):
            i = bisect_left(arr, x)                  # first position with arr[i] >= x
            return i if i < len(arr) and arr[i] == x else -1

        arr = [10, 10, 20, 30, 40, 40, 40, 40]
        print("index of 20:", search(arr, 20))
        print("index of 25:", search(arr, 25))
    ''', cpp='''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        int search(const vector<int>& arr, int x) {
            auto it = lower_bound(arr.begin(), arr.end(), x);   // first element >= x
            return (it != arr.end() && *it == x) ? (int)(it - arr.begin()) : -1;
        }

        int main() {
            vector<int> arr = {10, 10, 20, 30, 40, 40, 40, 40};
            cout << "index of 20: " << search(arr, 20) << "\\n";
            cout << "index of 25: " << search(arr, 25) << "\\n";
        }
    ''', java='''
        import java.util.Arrays;

        public class Main {
            static int search(int[] arr, int x) {
                int i = Arrays.binarySearch(arr, x);      // negative when absent: -(insertion point) - 1
                return i >= 0 ? i : -1;
            }

            public static void main(String[] args) {
                int[] arr = {10, 10, 20, 30, 40, 40, 40, 40};
                System.out.println("index of 20: " + search(arr, 20));
                System.out.println("index of 25: " + search(arr, 25));
            }
        }
    ''', js='''
        // No binary search in the standard library — indexOf is a linear scan
        const arr = [10, 10, 20, 30, 40, 40, 40, 40];
        console.log("index of 20:", arr.indexOf(20));
        console.log("index of 25:", arr.indexOf(25));
    ''')
    yield pitfall("`Arrays.binarySearch` on `[10, 10, 20, 30, 40, 40, 40, 40]` with `x = 40` may return 4, 5, 6 or 7 — the contract only promises *some* matching index. For the first or last occurrence, use the hand-written searches above (or `lower_bound` / `bisect_left`, which do guarantee the first position).")

    yield section("Interview Q&A", "message-question")
    yield qa("Why write mid = low + (high - low) / 2 instead of (low + high) / 2?",
             "Both give the same value mathematically, but `low + high` can exceed the maximum `int` (2³¹ − 1) for very large arrays and wrap to a negative number, producing a negative index. `low + (high - low) / 2` never computes a value larger than `high`. (Python integers do not overflow, but the habit is worth keeping.)")
    yield qa("Can you binary-search a linked list?",
             "Not usefully. The algorithm needs `O(1)` access to the middle element; in a linked list reaching the middle costs `O(n)`, so the total is `O(n)` — no better than a linear scan. Skip lists and balanced BSTs are the pointer-based structures that give `O(log n)` search.")
    yield qa("When is linear search the better choice?",
             "When the data is unsorted and searched only once (sorting costs `O(n log n)`), when `n` is tiny (a dozen elements — the constant factors and cache behaviour favour the scan), or when the container has no random access (linked list, stream).")
    yield qa("How do first-occurrence and lower_bound differ?",
             "`lower_bound(x)` / `bisect_left(x)` returns the first index whose value is **≥ x** — if `x` is absent that is the position where it would be inserted. First-occurrence returns the same index when `x` is present and `-1` otherwise. `upper_bound(x)` returns the first index with value **> x**, so `upper_bound − lower_bound` is the count of `x`.")
    yield qa("What problems can binary search solve besides finding a value?",
             "Anything where a yes/no predicate is monotonic over a range: first/last occurrence, counting 1s in a sorted binary array, floor of a square root (`mid² ≤ x`), peak in a mountain array, the smallest capacity that ships packages within `d` days, the minimum page limit in *allocate books* — \"binary search on the answer\". Each step evaluates the predicate once, so the cost is `O(log range × cost of predicate)`.")
    yield qa("What is the worst-case number of comparisons of binary search on 1,000,000 elements?",
             "About 20: ⌊log2 1,000,000⌋ + 1 = 20 halvings, each with at most two comparisons. Linear search needs up to 1,000,000.")


@topic(G, "sorting", "Sorting", "arrows-sort")
def _():
    yield lead("Sorting arranges data in increasing or decreasing order. It is the most studied problem in computer science because so much else — binary search, deduplication, merging, finding medians, grouping — becomes easy once the data is sorted. These notes cover the library sorts you should actually call and the classic algorithms you must be able to write and analyse: bubble, selection, insertion, merge, quick and heap sort.")
    yield define("Sorting", "rearranging a sequence so that every element is `≤` the one after it (ascending) or `≥` it (descending), according to a *comparison* — numeric, alphabetic, or any custom key.")

    yield section("Comparison of sorting algorithms", "table")
    yield p("The two properties interviewers ask about after time complexity are **stability** (equal elements keep their original relative order) and whether the sort is **in-place** (needs only `O(1)` — or `O(log n)` stack — extra memory).")
    yield table(
        ["Algorithm", "Best", "Average", "Worst", "Extra space", "Stable", "In-place", "Notes"],
        ["Bubble sort", "`O(n)`*", "`O(n²)`", "`O(n²)`", "`O(1)`", "yes", "yes", "*with the *swapped* flag; academic only"],
        ["Selection sort", "`O(n²)`", "`O(n²)`", "`O(n²)`", "`O(1)`", "no", "yes", "fewest writes: at most `n − 1` swaps"],
        ["Insertion sort", "`O(n)`", "`O(n²)`", "`O(n²)`", "`O(1)`", "yes", "yes", "best for small or nearly sorted input; used inside Timsort / introsort"],
        ["Merge sort", "`O(n log n)`", "`O(n log n)`", "`O(n log n)`", "`O(n)`", "yes", "no", "linked lists and external sorting; guaranteed `n log n`"],
        ["Quick sort", "`O(n log n)`", "`O(n log n)`", "`O(n²)`", "`O(log n)` stack", "no", "yes", "fastest in practice: cache-friendly, low constants"],
        ["Heap sort", "`O(n log n)`", "`O(n log n)`", "`O(n log n)`", "`O(1)`", "no", "yes", "guaranteed `n log n` in place; poor cache behaviour"],
        ["Timsort (library)", "`O(n)`", "`O(n log n)`", "`O(n log n)`", "`O(n)`", "yes", "no", "merge sort + insertion sort on natural runs; Python, Java objects, V8"],
    )
    yield note("Any sort that only *compares* elements needs `Ω(n log n)` comparisons in the worst case — there are `n!` orderings and each comparison rules out at most half. Merge, heap and quick sort are optimal in that sense; counting and radix sort beat it only by not comparing (they index on the values).")

    yield section("Built-in sorting in each language", "box")
    yield p("In real code you call the library sort. Know what it runs, whether it is stable, and how to pass a key or comparator.")
    yield table(
        ["Language", "Call", "Algorithm", "Stable", "Custom order"],
        ["Python", "`sorted(iterable, key=, reverse=)` → new list · `list.sort()` in place", "Timsort", "yes", "`key=` function (`len`, `abs`, `lambda p: (p.x, p.y)`)"],
        ["C++", "`std::sort(begin, end, cmp)`", "introsort (quick + heap + insertion)", "**no**", "comparator: `greater<int>()`, lambda"],
        ["C++", "`std::stable_sort(begin, end, cmp)`", "merge sort", "yes", "same comparator"],
        ["Java", "`Arrays.sort(int[])` (primitives)", "dual-pivot quicksort", "n/a (primitives are indistinguishable)", "—"],
        ["Java", "`Arrays.sort(T[])`, `Collections.sort(list)`, `list.sort(cmp)`", "Timsort", "yes", "`Comparator.comparingInt(...)`, `reverseOrder()`"],
        ["JavaScript", "`arr.sort(cmp)` in place · `arr.toSorted(cmp)` copy", "Timsort (V8)", "yes (since ES2019)", "`(a, b) => a - b` — **required** for numbers"],
    )
    yield multi('''
        ascending: 1 5 10 15
        descending: 15 10 5 1
        by length: Nani Thrishank Kuntimaddi
    ''', py='''
        nums = [5, 10, 15, 1]
        print("ascending:", *sorted(nums))
        print("descending:", *sorted(nums, reverse=True))

        words = ["Thrishank", "Nani", "Kuntimaddi"]
        print("by length:", *sorted(words, key=len))        # key: sort by what len() returns
    ''', cpp='''
        #include <algorithm>
        #include <functional>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        int main() {
            vector<int> nums = {5, 10, 15, 1};
            sort(nums.begin(), nums.end());
            cout << "ascending:";
            for (int x : nums) cout << " " << x;
            cout << "\\n";
            sort(nums.begin(), nums.end(), greater<int>());        // comparator: descending
            cout << "descending:";
            for (int x : nums) cout << " " << x;
            cout << "\\n";

            vector<string> words = {"Thrishank", "Nani", "Kuntimaddi"};
            stable_sort(words.begin(), words.end(),                // stable: equal lengths keep their order
                        [](const string& a, const string& b) { return a.size() < b.size(); });
            cout << "by length:";
            for (const string& w : words) cout << " " << w;
            cout << "\\n";
        }
    ''', java='''
        import java.util.Arrays;
        import java.util.Collections;
        import java.util.Comparator;

        public class Main {
            public static void main(String[] args) {
                Integer[] nums = {5, 10, 15, 1};                      // boxed: needed for a Comparator
                Arrays.sort(nums);
                System.out.println("ascending: " + join(nums));
                Arrays.sort(nums, Collections.reverseOrder());        // comparator: descending
                System.out.println("descending: " + join(nums));

                String[] words = {"Thrishank", "Nani", "Kuntimaddi"};
                Arrays.sort(words, Comparator.comparingInt(String::length));   // Timsort: stable
                System.out.println("by length: " + join(words));
            }

            static String join(Object[] a) {
                StringBuilder sb = new StringBuilder();
                for (Object x : a) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }
        }
    ''', js='''
        const nums = [5, 10, 15, 1];
        console.log("ascending:", [...nums].sort((a, b) => a - b).join(" "));    // numeric comparator!
        console.log("descending:", [...nums].sort((a, b) => b - a).join(" "));

        const words = ["Thrishank", "Nani", "Kuntimaddi"];
        console.log("by length:", words.toSorted((a, b) => a.length - b.length).join(" "));   // stable
    ''')
    yield pitfall("JavaScript's `arr.sort()` **without a comparator converts every element to a string** and compares the strings. Numbers come out in dictionary order — a classic bug.")
    yield snippet("js", '''
        const arr = [10, 9, 1, 100];
        console.log([...arr].sort().join(" "));              // "10" < "9" as strings
        console.log([...arr].sort((a, b) => a - b).join(" "));
    ''', out='''
        1 10 100 9
        1 9 10 100
    ''')

    yield section("Python: sort() and sorted()", "brand-python")
    yield table(
        ["", "`list.sort()`", "`sorted(iterable)`"],
        ["Works on", "lists only", "any iterable: list, tuple, string, set, dict (its keys), generator"],
        ["Result", "sorts **in place**, returns `None`", "returns a **new list**; the input is untouched"],
        ["Parameters", "`key=`, `reverse=`", "`key=`, `reverse=` — identical meaning"],
        ["Algorithm", "Timsort, stable, `O(n log n)` worst, `O(n)` on sorted input", "same"],
    )
    yield code('''
        l1 = [5, 10, 15, 1]
        l1.sort()                          # in place
        print(l1)                          # [1, 5, 10, 15]

        l2 = [5, 10, 15, 1]
        l2.sort(reverse=True)
        print(l2)                          # [15, 10, 5, 1]

        l3 = ['Thrishank', 'Nani', 'Kuntimaddi']
        l3.sort()                          # strings: dictionary order
        print(l3)                          # ['Kuntimaddi', 'Nani', 'Thrishank']

        l4 = ['Thrishank', 'Nani', 'Kuntimaddi']
        l4.sort(key=len)                   # sort by the key's value: 4, 9, 10
        print(l4)                          # ['Nani', 'Thrishank', 'Kuntimaddi']
        l4.sort(key=len, reverse=True)
        print(l4)                          # ['Kuntimaddi', 'Thrishank', 'Nani']

        print([5, 1, 3].sort())            # None   ← sort() returns None: a classic slip
    ''')
    yield pitfall("`x = l.sort()` leaves `x` as `None`. Use `l.sort()` on its own line, or `x = sorted(l)`.")
    yield p("**Sorting objects.** Either pass a `key` function that extracts the field to compare, or define `__lt__` on the class so the objects compare themselves. A tuple key such as `(p.x, p.y)` sorts by `x` and breaks ties by `y`.")
    yield snippet("py", '''
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __lt__(self, other):           # "less than": lets sort() compare Points directly
                if self.x == other.x:
                    return self.y < other.y    # tie on x → compare y
                return self.x < other.x

        pts = [Point(10, 15), Point(1, 15), Point(3, 8), Point(1, 7)]

        by_x = sorted(pts, key=lambda p: p.x)             # key function: compare x only (stable → 1 15 before 1 7)
        print("by x:", *(f"({p.x},{p.y})" for p in by_x))

        pts.sort()                                        # uses __lt__: x, then y
        print("by x then y:", *(f"({p.x},{p.y})" for p in pts))

        pts.sort(key=lambda p: (p.y, p.x))                # tuple key: y, then x
        print("by y then x:", *(f"({p.x},{p.y})" for p in pts))
    ''', out='''
        by x: (1,15) (1,7) (3,8) (10,15)
        by x then y: (1,7) (1,15) (3,8) (10,15)
        by y then x: (1,7) (3,8) (1,15) (10,15)
    ''')
    yield p("**`sorted()` on other iterables** — the result is always a list, even for a tuple, string or set. A dict sorts by its keys.")
    yield code('''
        l = [30, 8, 23, 76, 12, 1, 12]
        print(sorted(l))                         # [1, 8, 12, 12, 23, 30, 76]
        print(l)                                 # [30, 8, 23, 76, 12, 1, 12]   ← untouched

        l = [10, -15, -2, 1]
        print(sorted(l, key=abs))                # [1, -2, 10, -15]
        print(sorted(l, key=abs, reverse=True))  # [-15, 10, -2, 1]
        print(sorted(l))                         # [-15, -2, 1, 10]

        print(sorted((10, 12, 5, 1)))            # [1, 5, 10, 12]
        print(sorted({'Thrishank', 'Nani', 'Kuntimaddi'}))   # ['Kuntimaddi', 'Nani', 'Thrishank']
        print(sorted('gfg'))                     # ['f', 'g', 'g']
        print(sorted({10: 'a', 12: 'b', 5: 'c'}))            # [5, 10, 12]   ← keys only
        print(sorted([(10, 15), (12, 15), (3, 8)]))          # [(3, 8), (10, 15), (12, 15)]
    ''')
    yield note("**Timsort** (Tim Peters, 2002) is a hybrid: it finds already-ordered *runs* in the input, sorts short runs with insertion sort, then merges runs with merge sort. That is why it is stable, `O(n log n)` in the worst case and `O(n)` on already-sorted data. Java uses it for objects and V8 for `Array.prototype.sort`.")

    yield section("Stability", "equal")
    yield define("Stable sort", "a sort that keeps elements with **equal keys** in the same relative order they had in the input.")
    yield diagram('''
        input   (name, marks):  (Anil, 50)  (Ayan, 80)  (Pyush, 50)  (Ramesh, 80)

        sort by marks, stable:  (Anil, 50)  (Pyush, 50)  (Ayan, 80)  (Ramesh, 80)
                                 ^ Anil still before Pyush, Ayan still before Ramesh

        a possible unstable result:  (Pyush, 50)  (Anil, 50)  (Ayan, 80)  (Ramesh, 80)
                                      ^ the two 50s swapped — equal keys, order lost
    ''', "Stability only matters when keys repeat")
    yield p("**Why it matters:** stability lets you sort by several fields in *passes*. Sort by the secondary key first, then stably by the primary key — rows with the same primary key stay in secondary order. Spreadsheets, SQL `ORDER BY a, b` and \"sort by marks, then alphabetically\" all rely on this. It is also what makes `sort by marks` leave an already alphabetical list alphabetical within each group.")
    yield multi('''
        input: Ramesh 80, Anil 50, Pyush 50, Ayan 80
        by marks only: Anil 50, Pyush 50, Ramesh 80, Ayan 80
        by name, then by marks: Anil 50, Pyush 50, Ayan 80, Ramesh 80
    ''', py='''
        students = [("Ramesh", 80), ("Anil", 50), ("Pyush", 50), ("Ayan", 80)]
        show = lambda rows: ", ".join(f"{name} {marks}" for name, marks in rows)

        print("input:", show(students))
        print("by marks only:", show(sorted(students, key=lambda s: s[1])))   # ties keep input order

        by_name = sorted(students)                                 # pass 1: secondary key
        by_both = sorted(by_name, key=lambda s: s[1])              # pass 2: primary key, stable
        print("by name, then by marks:", show(by_both))
    ''', cpp='''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <utility>
        #include <vector>
        using namespace std;

        using Student = pair<string, int>;

        void show(const char* label, const vector<Student>& rows) {
            cout << label;
            for (size_t i = 0; i < rows.size(); i++)
                cout << (i ? ", " : " ") << rows[i].first << " " << rows[i].second;
            cout << "\\n";
        }

        int main() {
            vector<Student> students = {{"Ramesh", 80}, {"Anil", 50}, {"Pyush", 50}, {"Ayan", 80}};
            auto byMarks = [](const Student& a, const Student& b) { return a.second < b.second; };
            show("input:", students);

            vector<Student> v = students;
            stable_sort(v.begin(), v.end(), byMarks);          // std::sort would NOT guarantee the tie order
            show("by marks only:", v);

            v = students;
            sort(v.begin(), v.end());                          // pass 1: by name (pairs compare by first)
            stable_sort(v.begin(), v.end(), byMarks);          // pass 2: by marks, stable
            show("by name, then by marks:", v);
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.Comparator;
        import java.util.List;

        public class Main {
            record Student(String name, int marks) {}

            static String show(List<Student> rows) {
                StringBuilder sb = new StringBuilder();
                for (Student s : rows) sb.append(sb.length() == 0 ? "" : ", ").append(s.name()).append(' ').append(s.marks());
                return sb.toString();
            }

            public static void main(String[] args) {
                List<Student> students = List.of(new Student("Ramesh", 80), new Student("Anil", 50),
                                                 new Student("Pyush", 50), new Student("Ayan", 80));
                System.out.println("input: " + show(students));

                List<Student> v = new ArrayList<>(students);
                v.sort(Comparator.comparingInt(Student::marks));     // List.sort is Timsort: stable
                System.out.println("by marks only: " + show(v));

                v = new ArrayList<>(students);
                v.sort(Comparator.comparing(Student::name));         // pass 1: by name
                v.sort(Comparator.comparingInt(Student::marks));     // pass 2: by marks, stable
                System.out.println("by name, then by marks: " + show(v));
            }
        }
    ''', js='''
        const students = [["Ramesh", 80], ["Anil", 50], ["Pyush", 50], ["Ayan", 80]];
        const show = rows => rows.map(([name, marks]) => `${name} ${marks}`).join(", ");

        console.log("input:", show(students));
        console.log("by marks only:", show(students.toSorted((a, b) => a[1] - b[1])));   // stable since ES2019

        const byName = students.toSorted((a, b) => a[0].localeCompare(b[0]));   // pass 1: by name
        const byBoth = byName.toSorted((a, b) => a[1] - b[1]);                  // pass 2: by marks, stable
        console.log("by name, then by marks:", show(byBoth));
    ''')
    yield table(
        ["Stable", "Not stable", "Why"],
        ["Bubble sort", "Selection sort", "selection swaps the minimum over elements it has not compared with — a long-distance swap can jump one equal element over another"],
        ["Insertion sort", "Quick sort", "partition swaps elements across the whole range"],
        ["Merge sort", "Heap sort", "the heap's swaps with the last leaf reorder equal keys"],
        ["Timsort, counting sort", "`std::sort`, `Arrays.sort(int[])`", "introsort / quicksort based"],
    )
    yield note("Any unstable sort can be made stable by sorting `(key, original index)` pairs — at the cost of `O(n)` extra memory. And stability is irrelevant when keys are *all* of the data (sorting plain integers): two equal `5`s are indistinguishable.")

    yield section("Bubble sort", "bubble")
    yield io("arr = [10, 12, 5, 1, 10, 4, 56, 100]", "1 4 5 10 10 12 56 100")
    yield idea("Repeatedly walk the array and **swap adjacent elements that are out of order**. After pass 1 the largest element has *bubbled* to the end; after pass `i` the last `i` positions are final, so each pass can stop earlier. If a whole pass makes no swap the array is sorted — stop early.")
    yield diagram('''
        pass 1 on [5, 1, 4, 2]:
          (5 1) 4 2  →  swap  →  1 5 4 2
          1 (5 4) 2  →  swap  →  1 4 5 2
          1 4 (5 2)  →  swap  →  1 4 2 5      5 is now final
        pass 2 on the first 3:
          (1 4) 2    →  ok
          1 (4 2)    →  swap  →  1 2 4 5      4 is now final
        pass 3: (1 2) ok → no swap in the whole pass → sorted
    ''', "Each pass carries the largest remaining element to its place")
    yield multi('''
        sorted: 1 4 5 10 10 12 56 100
        passes: 5
        sorted: 1 2 3 4 5
        passes: 1
    ''', py='''
        def bubble_sort(arr):
            n = len(arr)
            passes = 0
            for i in range(n - 1):
                swapped = False
                passes += 1
                for j in range(n - i - 1):            # last i elements are already in place
                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                        swapped = True
                if not swapped:                       # a clean pass: already sorted
                    break
            return passes

        for arr in ([10, 12, 5, 1, 10, 4, 56, 100], [1, 2, 3, 4, 5]):
            passes = bubble_sort(arr)
            print("sorted:", *arr)
            print("passes:", passes)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        int bubbleSort(vector<int>& arr) {
            int n = arr.size(), passes = 0;
            for (int i = 0; i < n - 1; i++) {
                bool swapped = false;
                passes++;
                for (int j = 0; j < n - i - 1; j++) {        // last i elements are already in place
                    if (arr[j] > arr[j + 1]) {
                        swap(arr[j], arr[j + 1]);
                        swapped = true;
                    }
                }
                if (!swapped) break;                           // a clean pass: already sorted
            }
            return passes;
        }

        int main() {
            vector<vector<int>> tests = {{10, 12, 5, 1, 10, 4, 56, 100}, {1, 2, 3, 4, 5}};
            for (auto& arr : tests) {
                int passes = bubbleSort(arr);
                cout << "sorted:";
                for (int x : arr) cout << " " << x;
                cout << "\\npasses: " << passes << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static int bubbleSort(int[] arr) {
                int n = arr.length, passes = 0;
                for (int i = 0; i < n - 1; i++) {
                    boolean swapped = false;
                    passes++;
                    for (int j = 0; j < n - i - 1; j++) {        // last i elements are already in place
                        if (arr[j] > arr[j + 1]) {
                            int t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t;
                            swapped = true;
                        }
                    }
                    if (!swapped) break;                           // a clean pass: already sorted
                }
                return passes;
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 12, 5, 1, 10, 4, 56, 100}, {1, 2, 3, 4, 5}};
                for (int[] arr : tests) {
                    int passes = bubbleSort(arr);
                    StringBuilder sb = new StringBuilder("sorted:");
                    for (int x : arr) sb.append(' ').append(x);
                    System.out.println(sb);
                    System.out.println("passes: " + passes);
                }
            }
        }
    ''', js='''
        function bubbleSort(arr) {
            const n = arr.length;
            let passes = 0;
            for (let i = 0; i < n - 1; i++) {
                let swapped = false;
                passes++;
                for (let j = 0; j < n - i - 1; j++) {            // last i elements are already in place
                    if (arr[j] > arr[j + 1]) {
                        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
                        swapped = true;
                    }
                }
                if (!swapped) break;                               // a clean pass: already sorted
            }
            return passes;
        }

        for (const arr of [[10, 12, 5, 1, 10, 4, 56, 100], [1, 2, 3, 4, 5]]) {
            const passes = bubbleSort(arr);
            console.log("sorted:", arr.join(" "));
            console.log("passes:", passes);
        }
    ''')
    yield complexity("O(n²) — O(n) best with the swapped flag", "O(1)")
    yield ul(
        "**Stable**: only adjacent elements are swapped, and only when strictly greater — equal neighbours never cross.",
        "**In-place**, trivially simple — which is why it appears in every textbook and almost no real program.",
        "Without the `swapped` flag it always runs `n − 1` full passes, even on sorted input.",
    )

    yield section("Selection sort", "hand-finger")
    yield io("arr = [29, 10, 14, 37, 13]", "10 13 14 29 37")
    yield idea("Position `i` should hold the `i`-th smallest value. Find the **minimum of the unsorted part** `arr[i..n-1]` and swap it into position `i`; the sorted prefix grows by one each pass. Exactly `n − 1` swaps, whatever the input.")
    yield multi('''
        pass 1: min 10 -> 10 29 14 37 13
        pass 2: min 13 -> 10 13 14 37 29
        pass 3: min 14 -> 10 13 14 37 29
        pass 4: min 29 -> 10 13 14 29 37
        sorted: 1 4 5 10 10 12 56 100
    ''', py='''
        def selection_sort(arr, trace=False):
            n = len(arr)
            for i in range(n - 1):
                min_index = i
                for j in range(i + 1, n):           # find the minimum of arr[i..n-1]
                    if arr[j] < arr[min_index]:
                        min_index = j
                arr[i], arr[min_index] = arr[min_index], arr[i]   # one swap per pass
                if trace:
                    print(f"pass {i + 1}: min {arr[i]} ->", *arr)

        selection_sort([29, 10, 14, 37, 13], trace=True)
        arr = [10, 12, 5, 1, 10, 4, 56, 100]
        selection_sort(arr)
        print("sorted:", *arr)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        void show(const vector<int>& arr) {
            for (int x : arr) cout << " " << x;
            cout << "\\n";
        }

        void selectionSort(vector<int>& arr, bool trace = false) {
            int n = arr.size();
            for (int i = 0; i < n - 1; i++) {
                int minIndex = i;
                for (int j = i + 1; j < n; j++)              // find the minimum of arr[i..n-1]
                    if (arr[j] < arr[minIndex]) minIndex = j;
                swap(arr[i], arr[minIndex]);                 // one swap per pass
                if (trace) { cout << "pass " << i + 1 << ": min " << arr[i] << " ->"; show(arr); }
            }
        }

        int main() {
            vector<int> small = {29, 10, 14, 37, 13};
            selectionSort(small, true);
            vector<int> arr = {10, 12, 5, 1, 10, 4, 56, 100};
            selectionSort(arr);
            cout << "sorted:";
            show(arr);
        }
    ''', java='''
        public class Main {
            static String join(int[] arr) {
                StringBuilder sb = new StringBuilder();
                for (int x : arr) sb.append(' ').append(x);
                return sb.toString();
            }

            static void selectionSort(int[] arr, boolean trace) {
                int n = arr.length;
                for (int i = 0; i < n - 1; i++) {
                    int minIndex = i;
                    for (int j = i + 1; j < n; j++)              // find the minimum of arr[i..n-1]
                        if (arr[j] < arr[minIndex]) minIndex = j;
                    int t = arr[i]; arr[i] = arr[minIndex]; arr[minIndex] = t;   // one swap per pass
                    if (trace) System.out.println("pass " + (i + 1) + ": min " + arr[i] + " ->" + join(arr));
                }
            }

            public static void main(String[] args) {
                selectionSort(new int[]{29, 10, 14, 37, 13}, true);
                int[] arr = {10, 12, 5, 1, 10, 4, 56, 100};
                selectionSort(arr, false);
                System.out.println("sorted:" + join(arr));
            }
        }
    ''', js='''
        function selectionSort(arr, trace = false) {
            const n = arr.length;
            for (let i = 0; i < n - 1; i++) {
                let minIndex = i;
                for (let j = i + 1; j < n; j++)                  // find the minimum of arr[i..n-1]
                    if (arr[j] < arr[minIndex]) minIndex = j;
                [arr[i], arr[minIndex]] = [arr[minIndex], arr[i]];   // one swap per pass
                if (trace) console.log(`pass ${i + 1}: min ${arr[i]} ->`, arr.join(" "));
            }
        }

        selectionSort([29, 10, 14, 37, 13], true);
        const arr = [10, 12, 5, 1, 10, 4, 56, 100];
        selectionSort(arr);
        console.log("sorted:", arr.join(" "));
    ''')
    yield complexity("Θ(n²) in every case", "O(1)")
    yield ul(
        "Always `Θ(n²)` comparisons — it cannot notice that the input is already sorted.",
        "**Fewest memory writes** of the simple sorts (at most `n − 1` swaps), useful when writes are expensive (flash memory). Cycle sort is the optimum for writes.",
        "**Not stable**: in pass 1 on `[2a, 2b, 1]` the `1` is swapped with `2a`, which lands after `2b`.",
        "In-place. Its idea — repeatedly extract the minimum — is the seed of **heap sort**, which extracts it in `O(log n)` instead of `O(n)`.",
    )

    yield section("Insertion sort", "arrow-bar-to-down")
    yield io("arr = [10, 12, 5, 1, 10, 4]", "1 4 5 10 10 12")
    yield idea("Keep the prefix `arr[0..i-1]` sorted (as you would sort cards in your hand). Take the next element `x = arr[i]`, **shift** every larger element of the prefix one slot to the right, and drop `x` into the gap. On nearly sorted input almost nothing shifts, which is why it is `O(n)` in the best case.")
    yield diagram('''
        i = 2, x = 5:     [10, 12 | 5, 1, 10, 4]
                           shift 12 →  [10, _, 12]   shift 10 →  [_, 10, 12]   place 5 →  [5, 10, 12 | 1, 10, 4]
    ''', "Insert arr[i] into the sorted prefix by shifting, not swapping")
    yield multi('''
        insert 12: 10 12 5 1 10 4
        insert 5: 5 10 12 1 10 4
        insert 1: 1 5 10 12 10 4
        insert 10: 1 5 10 10 12 4
        insert 4: 1 4 5 10 10 12
        sorted: 1 4 5 10 10 12 56 100
    ''', py='''
        def insertion_sort(arr, trace=False):
            for i in range(1, len(arr)):
                x = arr[i]                             # the element to insert
                j = i - 1
                while j >= 0 and arr[j] > x:           # shift larger elements right ...
                    arr[j + 1] = arr[j]
                    j -= 1
                arr[j + 1] = x                         # ... and drop x into the gap
                if trace:
                    print(f"insert {x}:", *arr)

        insertion_sort([10, 12, 5, 1, 10, 4], trace=True)
        arr = [10, 12, 5, 1, 10, 4, 56, 100]
        insertion_sort(arr)
        print("sorted:", *arr)
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        void show(const vector<int>& arr) {
            for (int x : arr) cout << " " << x;
            cout << "\\n";
        }

        void insertionSort(vector<int>& arr, bool trace = false) {
            int n = arr.size();
            for (int i = 1; i < n; i++) {
                int x = arr[i];                              // the element to insert
                int j = i - 1;
                while (j >= 0 && arr[j] > x) {               // shift larger elements right ...
                    arr[j + 1] = arr[j];
                    j--;
                }
                arr[j + 1] = x;                              // ... and drop x into the gap
                if (trace) { cout << "insert " << x << ":"; show(arr); }
            }
        }

        int main() {
            vector<int> small = {10, 12, 5, 1, 10, 4};
            insertionSort(small, true);
            vector<int> arr = {10, 12, 5, 1, 10, 4, 56, 100};
            insertionSort(arr);
            cout << "sorted:";
            show(arr);
        }
    ''', java='''
        public class Main {
            static String join(int[] arr) {
                StringBuilder sb = new StringBuilder();
                for (int x : arr) sb.append(' ').append(x);
                return sb.toString();
            }

            static void insertionSort(int[] arr, boolean trace) {
                for (int i = 1; i < arr.length; i++) {
                    int x = arr[i];                              // the element to insert
                    int j = i - 1;
                    while (j >= 0 && arr[j] > x) {               // shift larger elements right ...
                        arr[j + 1] = arr[j];
                        j--;
                    }
                    arr[j + 1] = x;                              // ... and drop x into the gap
                    if (trace) System.out.println("insert " + x + ":" + join(arr));
                }
            }

            public static void main(String[] args) {
                insertionSort(new int[]{10, 12, 5, 1, 10, 4}, true);
                int[] arr = {10, 12, 5, 1, 10, 4, 56, 100};
                insertionSort(arr, false);
                System.out.println("sorted:" + join(arr));
            }
        }
    ''', js='''
        function insertionSort(arr, trace = false) {
            for (let i = 1; i < arr.length; i++) {
                const x = arr[i];                                // the element to insert
                let j = i - 1;
                while (j >= 0 && arr[j] > x) {                   // shift larger elements right ...
                    arr[j + 1] = arr[j];
                    j--;
                }
                arr[j + 1] = x;                                  // ... and drop x into the gap
                if (trace) console.log(`insert ${x}:`, arr.join(" "));
            }
        }

        insertionSort([10, 12, 5, 1, 10, 4], true);
        const arr = [10, 12, 5, 1, 10, 4, 56, 100];
        insertionSort(arr);
        console.log("sorted:", arr.join(" "));
    ''')
    yield complexity("O(n²) worst / average · O(n) best (sorted input)", "O(1)")
    yield ul(
        "**Stable** (shifts only strictly greater elements) and **in-place**.",
        "The practical choice for **small arrays** (≈ 16–32 elements) and nearly sorted data — Timsort and introsort both switch to insertion sort for short ranges.",
        "`O(n + d)` where `d` is the number of inversions: an array with few elements out of place sorts in almost linear time.",
    )
    yield pitfall("The original notes compared `x < l[i]` in the inner loop. `l[i]` *is* `x`, so the condition is never true and nothing is ever shifted — the array came back unsorted. The comparison must be against `arr[j]`, the element being shifted.")

    yield section("Merging two sorted arrays", "git-merge")
    yield io("a = [10, 15, 20], b = [5, 6, 6, 30]", "5 6 6 10 15 20 30")
    yield p("Naive: concatenate and sort — `O((m + n) log(m + n))`. It ignores the fact that both inputs are already sorted.")
    yield snippet("py", '''
        def merge_naive(a, b):
            res = a + b
            res.sort()                 # throws away the order we already had
            return res

        print(*merge_naive([10, 15, 20], [5, 6, 6, 30]))
    ''', out="5 6 6 10 15 20 30")
    yield idea("**Two pointers.** The smallest remaining element of the union is either `a[i]` or `b[j]` — the heads of the two arrays. Compare them, copy the smaller one to the result and advance its pointer. When one array runs out, copy the rest of the other. Every element is looked at once: `O(m + n)`.")
    yield diagram('''
        a = [10, 15, 20]       b = [5, 6, 6, 30]       res = []
             i                      j
        10 > 5   → take 5          res = [5]              j → 6
        10 > 6   → take 6          res = [5 6]            j → 6
        10 > 6   → take 6          res = [5 6 6]          j → 30
        10 < 30  → take 10         res = [5 6 6 10]       i → 15
        15 < 30  → take 15         res = [5 6 6 10 15]    i → 20
        20 < 30  → take 20         res = [5 6 6 10 15 20] a is exhausted
        copy the rest of b         res = [5 6 6 10 15 20 30]
    ''', "The merge step: always take the smaller head")
    yield multi('''
        5 6 6 10 15 20 30
    ''', py='''
        def merge(a, b):
            res = []
            i = j = 0
            while i < len(a) and j < len(b):
                if a[i] <= b[j]:             # <= keeps the merge stable (a's element first on a tie)
                    res.append(a[i])
                    i += 1
                else:
                    res.append(b[j])
                    j += 1
            res.extend(a[i:])                # at most one of these has anything left
            res.extend(b[j:])
            return res

        print(*merge([10, 15, 20], [5, 6, 6, 30]))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> merge(const vector<int>& a, const vector<int>& b) {
            vector<int> res;
            int m = a.size(), n = b.size(), i = 0, j = 0;
            while (i < m && j < n) {
                if (a[i] <= b[j]) res.push_back(a[i++]);   // <= keeps the merge stable
                else res.push_back(b[j++]);
            }
            while (i < m) res.push_back(a[i++]);           // at most one of these has anything left
            while (j < n) res.push_back(b[j++]);
            return res;
        }

        int main() {
            vector<int> res = merge({10, 15, 20}, {5, 6, 6, 30});
            for (size_t k = 0; k < res.size(); k++) cout << (k ? " " : "") << res[k];
            cout << "\\n";
        }
    ''', java='''
        public class Main {
            static int[] merge(int[] a, int[] b) {
                int m = a.length, n = b.length, i = 0, j = 0, k = 0;
                int[] res = new int[m + n];
                while (i < m && j < n) {
                    if (a[i] <= b[j]) res[k++] = a[i++];     // <= keeps the merge stable
                    else res[k++] = b[j++];
                }
                while (i < m) res[k++] = a[i++];             // at most one of these has anything left
                while (j < n) res[k++] = b[j++];
                return res;
            }

            public static void main(String[] args) {
                int[] res = merge(new int[]{10, 15, 20}, new int[]{5, 6, 6, 30});
                StringBuilder sb = new StringBuilder();
                for (int x : res) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }
        }
    ''', js='''
        function merge(a, b) {
            const res = [];
            let i = 0, j = 0;
            while (i < a.length && j < b.length) {
                if (a[i] <= b[j]) res.push(a[i++]);       // <= keeps the merge stable
                else res.push(b[j++]);
            }
            while (i < a.length) res.push(a[i++]);        // at most one of these has anything left
            while (j < b.length) res.push(b[j++]);
            return res;
        }

        console.log(merge([10, 15, 20], [5, 6, 6, 30]).join(" "));
    ''')
    yield complexity("O(m + n)", "O(m + n) for the result")
    yield note("Use `<=` (not `<`) when comparing `a[i]` with `b[j]`: on a tie the element from the *left* array is taken first, which is what makes merge sort stable.")

    yield section("Merge subarray", "arrows-join")
    yield io("a = [10, 15, 20, 11, 13], low = 0, mid = 2, high = 4", "10 11 13 15 20")
    yield p("Merge sort needs the same merge, but **inside one array**: the two sorted halves are `a[low..mid]` and `a[mid+1..high]`, and the merged result must land back in `a[low..high]`. Copy the two halves into temporary arrays `left` and `right`, then merge them back starting at index `low`.")
    yield multi('''
        10 11 13 15 20
    ''', py='''
        def merge(a, low, mid, high):
            left = a[low:mid + 1]                   # copies: a[low..mid] and a[mid+1..high]
            right = a[mid + 1:high + 1]
            i = j = 0
            k = low                                 # write position in a
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    a[k] = left[i]
                    i += 1
                else:
                    a[k] = right[j]
                    j += 1
                k += 1
            while i < len(left):                    # leftovers
                a[k] = left[i]
                i += 1
                k += 1
            while j < len(right):
                a[k] = right[j]
                j += 1
                k += 1

        a = [10, 15, 20, 11, 13]
        merge(a, 0, 2, 4)
        print(*a)
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        void merge(vector<int>& a, int low, int mid, int high) {
            vector<int> left(a.begin() + low, a.begin() + mid + 1);        // a[low..mid]
            vector<int> right(a.begin() + mid + 1, a.begin() + high + 1);  // a[mid+1..high]
            int nl = left.size(), nr = right.size(), i = 0, j = 0, k = low;   // k: write position in a
            while (i < nl && j < nr) {
                if (left[i] <= right[j]) a[k++] = left[i++];
                else a[k++] = right[j++];
            }
            while (i < nl) a[k++] = left[i++];        // leftovers
            while (j < nr) a[k++] = right[j++];
        }

        int main() {
            vector<int> a = {10, 15, 20, 11, 13};
            merge(a, 0, 2, 4);
            for (size_t k = 0; k < a.size(); k++) cout << (k ? " " : "") << a[k];
            cout << "\\n";
        }
    ''', java='''
        import java.util.Arrays;

        public class Main {
            static void merge(int[] a, int low, int mid, int high) {
                int[] left = Arrays.copyOfRange(a, low, mid + 1);         // a[low..mid]
                int[] right = Arrays.copyOfRange(a, mid + 1, high + 1);   // a[mid+1..high]
                int i = 0, j = 0, k = low;                                // k: write position in a
                while (i < left.length && j < right.length) {
                    if (left[i] <= right[j]) a[k++] = left[i++];
                    else a[k++] = right[j++];
                }
                while (i < left.length) a[k++] = left[i++];              // leftovers
                while (j < right.length) a[k++] = right[j++];
            }

            public static void main(String[] args) {
                int[] a = {10, 15, 20, 11, 13};
                merge(a, 0, 2, 4);
                StringBuilder sb = new StringBuilder();
                for (int x : a) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }
        }
    ''', js='''
        function merge(a, low, mid, high) {
            const left = a.slice(low, mid + 1);            // a[low..mid]
            const right = a.slice(mid + 1, high + 1);      // a[mid+1..high]
            let i = 0, j = 0, k = low;                     // k: write position in a
            while (i < left.length && j < right.length) {
                if (left[i] <= right[j]) a[k++] = left[i++];
                else a[k++] = right[j++];
            }
            while (i < left.length) a[k++] = left[i++];   // leftovers
            while (j < right.length) a[k++] = right[j++];
        }

        const a = [10, 15, 20, 11, 13];
        merge(a, 0, 2, 4);
        console.log(a.join(" "));
    ''')
    yield complexity("O(high − low + 1)", "O(high − low + 1) temporary copies")

    yield section("Merge sort", "binary-tree")
    yield io("arr = [38, 27, 43, 3, 9, 82, 10]", "3 9 10 27 38 43 82")
    yield idea("**Divide and conquer.** A one-element array is sorted. Otherwise split the array in half, sort each half recursively, and *merge* the two sorted halves with the merge above. All the real work happens in the merges: `log n` levels, each merging `n` elements in total.")
    yield diagram('''
                        [38 27 43 3 9 82 10]
                       /                    \\                  divide
                [38 27 43 3]              [9 82 10]
                 /        \\                /       \\
             [38 27]    [43 3]         [9 82]     [10]
             /    \\      /   \\         /   \\
           [38]  [27]  [43]  [3]     [9]  [82]
             \\    /      \\   /         \\   /
             [27 38]    [3 43]        [9 82]     [10]           merge
                 \\        /                \\       /
                [3 27 38 43]              [9 10 82]
                       \\                    /
                        [3 9 10 27 38 43 82]
    ''', "Split down to single elements, then merge back up — log2 n levels")
    yield multi('''
        3 9 10 27 38 43 82
        10 11 13 15 20
    ''', py='''
        def merge(a, low, mid, high):
            left, right = a[low:mid + 1], a[mid + 1:high + 1]
            i = j = 0
            k = low
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    a[k] = left[i]; i += 1
                else:
                    a[k] = right[j]; j += 1
                k += 1
            while i < len(left):
                a[k] = left[i]; i += 1; k += 1
            while j < len(right):
                a[k] = right[j]; j += 1; k += 1

        def merge_sort(a, low, high):
            if low < high:                       # at least two elements
                mid = low + (high - low) // 2
                merge_sort(a, low, mid)          # sort the left half
                merge_sort(a, mid + 1, high)     # sort the right half
                merge(a, low, mid, high)         # combine

        for arr in ([38, 27, 43, 3, 9, 82, 10], [10, 15, 20, 11, 13]):
            merge_sort(arr, 0, len(arr) - 1)
            print(*arr)
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        void merge(vector<int>& a, int low, int mid, int high) {
            vector<int> left(a.begin() + low, a.begin() + mid + 1);
            vector<int> right(a.begin() + mid + 1, a.begin() + high + 1);
            int nl = left.size(), nr = right.size(), i = 0, j = 0, k = low;
            while (i < nl && j < nr) a[k++] = (left[i] <= right[j]) ? left[i++] : right[j++];
            while (i < nl) a[k++] = left[i++];
            while (j < nr) a[k++] = right[j++];
        }

        void mergeSort(vector<int>& a, int low, int high) {
            if (low < high) {                          // at least two elements
                int mid = low + (high - low) / 2;
                mergeSort(a, low, mid);                // sort the left half
                mergeSort(a, mid + 1, high);           // sort the right half
                merge(a, low, mid, high);              // combine
            }
        }

        int main() {
            vector<vector<int>> tests = {{38, 27, 43, 3, 9, 82, 10}, {10, 15, 20, 11, 13}};
            for (auto& arr : tests) {
                mergeSort(arr, 0, (int)arr.size() - 1);
                for (size_t k = 0; k < arr.size(); k++) cout << (k ? " " : "") << arr[k];
                cout << "\\n";
            }
        }
    ''', java='''
        import java.util.Arrays;

        public class Main {
            static void merge(int[] a, int low, int mid, int high) {
                int[] left = Arrays.copyOfRange(a, low, mid + 1);
                int[] right = Arrays.copyOfRange(a, mid + 1, high + 1);
                int i = 0, j = 0, k = low;
                while (i < left.length && j < right.length) a[k++] = (left[i] <= right[j]) ? left[i++] : right[j++];
                while (i < left.length) a[k++] = left[i++];
                while (j < right.length) a[k++] = right[j++];
            }

            static void mergeSort(int[] a, int low, int high) {
                if (low < high) {                          // at least two elements
                    int mid = low + (high - low) / 2;
                    mergeSort(a, low, mid);                // sort the left half
                    mergeSort(a, mid + 1, high);           // sort the right half
                    merge(a, low, mid, high);              // combine
                }
            }

            public static void main(String[] args) {
                int[][] tests = {{38, 27, 43, 3, 9, 82, 10}, {10, 15, 20, 11, 13}};
                for (int[] arr : tests) {
                    mergeSort(arr, 0, arr.length - 1);
                    StringBuilder sb = new StringBuilder();
                    for (int x : arr) sb.append(sb.length() == 0 ? "" : " ").append(x);
                    System.out.println(sb);
                }
            }
        }
    ''', js='''
        function merge(a, low, mid, high) {
            const left = a.slice(low, mid + 1), right = a.slice(mid + 1, high + 1);
            let i = 0, j = 0, k = low;
            while (i < left.length && j < right.length) a[k++] = (left[i] <= right[j]) ? left[i++] : right[j++];
            while (i < left.length) a[k++] = left[i++];
            while (j < right.length) a[k++] = right[j++];
        }

        function mergeSort(a, low, high) {
            if (low < high) {                              // at least two elements
                const mid = low + Math.floor((high - low) / 2);
                mergeSort(a, low, mid);                    // sort the left half
                mergeSort(a, mid + 1, high);               // sort the right half
                merge(a, low, mid, high);                  // combine
            }
        }

        for (const arr of [[38, 27, 43, 3, 9, 82, 10], [10, 15, 20, 11, 13]]) {
            mergeSort(arr, 0, arr.length - 1);
            console.log(arr.join(" "));
        }
    ''')
    yield complexity("Θ(n log n) in every case", "O(n) temporary arrays + O(log n) stack")
    yield formula("T(n) = 2 T(n / 2) + Θ(n)  ⇒  T(n) = Θ(n log n)")
    yield ul(
        "**Stable** (the `<=` in merge) and **guaranteed** `Θ(n log n)` — no bad inputs, unlike quick sort.",
        "**Not in-place**: the merge needs `O(n)` temporary space. (In-place variants exist but are slow or complex.)",
        "Ideal for **linked lists**: splitting and merging lists needs no extra array, so it sorts a list in `O(1)` auxiliary space — and it is the default list sort in many libraries.",
        "Used in **external sorting** (data larger than memory): sort chunks that fit in RAM, then merge the sorted chunks sequentially from disk.",
        "Timsort is merge sort with insertion-sorted runs; it is what Python and Java's object sort run.",
    )
    yield pitfall("Writing `mergeSort(a, mid, high)` for the right half re-includes `a[mid]` in both halves and recurses forever on two elements. The halves are `[low..mid]` and `[mid+1..high]`.")

    yield section("Union of two sorted arrays", "circles")
    yield io("a = [3, 5, 8, 9, 10, 15], b = [2, 8, 9, 10, 15]", "2 3 5 8 9 10 15", "a = [1, 1, 3, 3, 5], b = [1, 2, 2, 3]", "1 2 3 5")
    yield p("The union is every distinct value present in either array, in sorted order. Naive: concatenate, sort, then print each element that differs from its predecessor — `O((m + n) log(m + n))`.")
    yield snippet("py", '''
        def union_naive(a, b):
            c = sorted(a + b)
            return [c[i] for i in range(len(c)) if i == 0 or c[i] != c[i - 1]]   # skip repeats

        print(*union_naive([3, 5, 8, 9, 10, 15], [2, 8, 9, 10, 15]))
    ''', out="2 3 5 8 9 10 15")
    yield idea("It is the **merge** two-pointer walk with two extra rules: skip an element equal to the previous one in its own array (duplicates *within* an array), and when `a[i] == b[j]` output it once and advance both pointers (duplicates *across* the arrays). The leftovers after one array is exhausted need the same within-array duplicate check.")
    yield multi('''
        2 3 5 8 9 10 15
        1 2 3 5
    ''', py='''
        def union(a, b):
            res = []
            i = j = 0
            m, n = len(a), len(b)
            while i < m and j < n:
                if i > 0 and a[i] == a[i - 1]:          # duplicate inside a: skip
                    i += 1
                elif j > 0 and b[j] == b[j - 1]:        # duplicate inside b: skip
                    j += 1
                elif a[i] < b[j]:
                    res.append(a[i]); i += 1
                elif a[i] > b[j]:
                    res.append(b[j]); j += 1
                else:                                   # equal: take once, advance both
                    res.append(a[i]); i += 1; j += 1
            while i < m:                                # leftovers of a (still skipping duplicates)
                if i == 0 or a[i] != a[i - 1]:
                    res.append(a[i])
                i += 1
            while j < n:                                # leftovers of b
                if j == 0 or b[j] != b[j - 1]:
                    res.append(b[j])
                j += 1
            return res

        print(*union([3, 5, 8, 9, 10, 15], [2, 8, 9, 10, 15]))
        print(*union([1, 1, 3, 3, 5], [1, 2, 2, 3]))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> unionOf(const vector<int>& a, const vector<int>& b) {
            vector<int> res;
            int m = a.size(), n = b.size(), i = 0, j = 0;
            while (i < m && j < n) {
                if (i > 0 && a[i] == a[i - 1]) i++;              // duplicate inside a: skip
                else if (j > 0 && b[j] == b[j - 1]) j++;         // duplicate inside b: skip
                else if (a[i] < b[j]) res.push_back(a[i++]);
                else if (a[i] > b[j]) res.push_back(b[j++]);
                else { res.push_back(a[i]); i++; j++; }          // equal: take once, advance both
            }
            for (; i < m; i++) if (i == 0 || a[i] != a[i - 1]) res.push_back(a[i]);   // leftovers of a
            for (; j < n; j++) if (j == 0 || b[j] != b[j - 1]) res.push_back(b[j]);   // leftovers of b
            return res;
        }

        void show(const vector<int>& v) {
            for (size_t k = 0; k < v.size(); k++) cout << (k ? " " : "") << v[k];
            cout << "\\n";
        }

        int main() {
            show(unionOf({3, 5, 8, 9, 10, 15}, {2, 8, 9, 10, 15}));
            show(unionOf({1, 1, 3, 3, 5}, {1, 2, 2, 3}));
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> union(int[] a, int[] b) {
                List<Integer> res = new ArrayList<>();
                int m = a.length, n = b.length, i = 0, j = 0;
                while (i < m && j < n) {
                    if (i > 0 && a[i] == a[i - 1]) i++;              // duplicate inside a: skip
                    else if (j > 0 && b[j] == b[j - 1]) j++;         // duplicate inside b: skip
                    else if (a[i] < b[j]) res.add(a[i++]);
                    else if (a[i] > b[j]) res.add(b[j++]);
                    else { res.add(a[i]); i++; j++; }                // equal: take once, advance both
                }
                for (; i < m; i++) if (i == 0 || a[i] != a[i - 1]) res.add(a[i]);   // leftovers of a
                for (; j < n; j++) if (j == 0 || b[j] != b[j - 1]) res.add(b[j]);   // leftovers of b
                return res;
            }

            static void show(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                show(union(new int[]{3, 5, 8, 9, 10, 15}, new int[]{2, 8, 9, 10, 15}));
                show(union(new int[]{1, 1, 3, 3, 5}, new int[]{1, 2, 2, 3}));
            }
        }
    ''', js='''
        function union(a, b) {
            const res = [];
            let i = 0, j = 0;
            while (i < a.length && j < b.length) {
                if (i > 0 && a[i] === a[i - 1]) i++;                 // duplicate inside a: skip
                else if (j > 0 && b[j] === b[j - 1]) j++;            // duplicate inside b: skip
                else if (a[i] < b[j]) res.push(a[i++]);
                else if (a[i] > b[j]) res.push(b[j++]);
                else { res.push(a[i]); i++; j++; }                   // equal: take once, advance both
            }
            for (; i < a.length; i++) if (i === 0 || a[i] !== a[i - 1]) res.push(a[i]);   // leftovers of a
            for (; j < b.length; j++) if (j === 0 || b[j] !== b[j - 1]) res.push(b[j]);   // leftovers of b
            return res;
        }

        console.log(union([3, 5, 8, 9, 10, 15], [2, 8, 9, 10, 15]).join(" "));
        console.log(union([1, 1, 3, 3, 5], [1, 2, 2, 3]).join(" "));
    ''')
    yield complexity("O(m + n)", "O(m + n) for the result")
    yield pitfall("The original notes' leftover loops printed an element only when it **equalled** its predecessor and advanced the pointer only in that case — so they printed the wrong values and looped forever on a non-duplicate. The leftover loop must advance on every iteration and print when the element *differs* from its predecessor.")

    yield section("Intersection of two sorted arrays", "circles-relation")
    yield io("a = [3, 5, 10, 10, 10, 10, 15, 15, 20], b = [5, 10, 10, 15, 30]", "5 10 15")
    yield p("The intersection is every distinct value present in **both** arrays. Naive: for each element of `a` (skipping repeats), scan `b` for it — `O(m · n)`.")
    yield snippet("py", '''
        def intersection_naive(a, b):
            res = []
            for i in range(len(a)):
                if i > 0 and a[i] == a[i - 1]:
                    continue                         # already handled this value
                for x in b:                          # linear scan of b
                    if x == a[i]:
                        res.append(x)
                        break
            return res

        print(*intersection_naive([3, 5, 10, 10, 10, 10, 15, 15, 20], [5, 10, 10, 15, 30]))
    ''', out="5 10 15")
    yield idea("Two pointers again. Skip duplicates in `a`. If `a[i] < b[j]`, `a[i]` cannot be in `b` any more — advance `i`; if `a[i] > b[j]` advance `j`; if equal, output it and advance both. Duplicates in `b` are harmless: after a match `i` moves to a larger value, so the repeated `b[j]` is simply skipped by the `>` rule.")
    yield multi('''
        5 10 15
        2 3
    ''', py='''
        def intersection(a, b):
            res = []
            i = j = 0
            while i < len(a) and j < len(b):
                if i > 0 and a[i] == a[i - 1]:      # duplicate inside a: skip
                    i += 1
                elif a[i] < b[j]:                   # a[i] is too small to be in b from here on
                    i += 1
                elif a[i] > b[j]:                   # b[j] is too small
                    j += 1
                else:                               # common value
                    res.append(a[i]); i += 1; j += 1
            return res

        print(*intersection([3, 5, 10, 10, 10, 10, 15, 15, 20], [5, 10, 10, 15, 30]))
        print(*intersection([1, 2, 2, 3, 3, 3], [2, 2, 3, 4]))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> intersection(const vector<int>& a, const vector<int>& b) {
            vector<int> res;
            int m = a.size(), n = b.size(), i = 0, j = 0;
            while (i < m && j < n) {
                if (i > 0 && a[i] == a[i - 1]) i++;          // duplicate inside a: skip
                else if (a[i] < b[j]) i++;                   // a[i] is too small to be in b from here on
                else if (a[i] > b[j]) j++;                   // b[j] is too small
                else { res.push_back(a[i]); i++; j++; }      // common value
            }
            return res;
        }

        void show(const vector<int>& v) {
            for (size_t k = 0; k < v.size(); k++) cout << (k ? " " : "") << v[k];
            cout << "\\n";
        }

        int main() {
            show(intersection({3, 5, 10, 10, 10, 10, 15, 15, 20}, {5, 10, 10, 15, 30}));
            show(intersection({1, 2, 2, 3, 3, 3}, {2, 2, 3, 4}));
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> intersection(int[] a, int[] b) {
                List<Integer> res = new ArrayList<>();
                int m = a.length, n = b.length, i = 0, j = 0;
                while (i < m && j < n) {
                    if (i > 0 && a[i] == a[i - 1]) i++;          // duplicate inside a: skip
                    else if (a[i] < b[j]) i++;                   // a[i] is too small to be in b from here on
                    else if (a[i] > b[j]) j++;                   // b[j] is too small
                    else { res.add(a[i]); i++; j++; }            // common value
                }
                return res;
            }

            static void show(List<Integer> v) {
                StringBuilder sb = new StringBuilder();
                for (int x : v) sb.append(sb.length() == 0 ? "" : " ").append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                show(intersection(new int[]{3, 5, 10, 10, 10, 10, 15, 15, 20}, new int[]{5, 10, 10, 15, 30}));
                show(intersection(new int[]{1, 2, 2, 3, 3, 3}, new int[]{2, 2, 3, 4}));
            }
        }
    ''', js='''
        function intersection(a, b) {
            const res = [];
            let i = 0, j = 0;
            while (i < a.length && j < b.length) {
                if (i > 0 && a[i] === a[i - 1]) i++;             // duplicate inside a: skip
                else if (a[i] < b[j]) i++;                       // a[i] is too small to be in b from here on
                else if (a[i] > b[j]) j++;                       // b[j] is too small
                else { res.push(a[i]); i++; j++; }               // common value
            }
            return res;
        }

        console.log(intersection([3, 5, 10, 10, 10, 10, 15, 15, 20], [5, 10, 10, 15, 30]).join(" "));
        console.log(intersection([1, 2, 2, 3, 3, 3], [2, 2, 3, 4]).join(" "));
    ''')
    yield complexity("O(m + n)", "O(min(m, n)) for the result")
    yield note("Union and intersection on **unsorted** arrays: put one array in a hash set and scan the other — `O(m + n)` expected time, `O(m)` space. Sorting first costs `O(n log n)` but needs no extra memory and keeps the output sorted.")

    yield section("Count inversions", "arrows-cross")
    yield define("Inversion", "a pair of indices `i < j` with `arr[i] > arr[j]` — two elements that are in the wrong order relative to each other. A sorted array has 0 inversions; a reverse-sorted one has `n(n − 1) / 2`. The count measures *how unsorted* an array is.")
    yield io("arr = [2, 4, 1, 3, 5]", "3  — the pairs (2,1), (4,1), (4,3)", "arr = [5, 4, 3, 2, 1]", "10")
    yield p("Naive: check every pair — `O(n²)`.")
    yield snippet("py", '''
        def count_inversions_naive(arr):
            n = len(arr)
            count = 0
            for i in range(n - 1):
                for j in range(i + 1, n):
                    if arr[i] > arr[j]:
                        count += 1
            return count

        print(count_inversions_naive([2, 4, 1, 3, 5]), count_inversions_naive([2, 4, 1, 3, 5, 2]))
    ''', out="3 6")
    yield idea("Piggy-back on **merge sort**. Split the array at `mid`; every inversion `(x, y)` has both elements in the left half, both in the right half, or `x` on the left and `y` on the right. The first two kinds are counted by the recursive calls. The third kind is counted *during the merge*: when `right[j]` is taken before `left[i]`, it is smaller than `left[i]` **and every element after it** in the sorted left half — that is `len(left) − i` inversions at once.")
    yield diagram('''
        merge  left = [2 4]   right = [1 3 5]
               take 1 from right  → 1 < every remaining left element (2, 4)   → +2 inversions
               take 2 from left
               take 3 from right  → 3 < remaining left (4)                   → +1 inversion
               take 4, 5                                                      total: 3
    ''', "Cross inversions are counted in bulk while merging")
    yield multi('''
        [2 4 1 3 5]: 3
        [2 4 1 3 5 2]: 6
        [5 4 3 2 1]: 10
        [1 2 3 4 5]: 0
    ''', py='''
        def count_merge(arr, low, mid, high):
            left, right = arr[low:mid + 1], arr[mid + 1:high + 1]
            count = 0
            i = j = 0
            k = low
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    arr[k] = left[i]; i += 1
                else:
                    arr[k] = right[j]; j += 1
                    count += len(left) - i          # right[j] is smaller than all remaining left elements
                k += 1
            while i < len(left):
                arr[k] = left[i]; i += 1; k += 1
            while j < len(right):
                arr[k] = right[j]; j += 1; k += 1
            return count

        def count_inversions(arr, low, high):
            count = 0
            if low < high:
                mid = low + (high - low) // 2
                count += count_inversions(arr, low, mid)        # both in the left half
                count += count_inversions(arr, mid + 1, high)   # both in the right half
                count += count_merge(arr, low, mid, high)       # one in each half
            return count

        for arr in ([2, 4, 1, 3, 5], [2, 4, 1, 3, 5, 2], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5]):
            label = "[" + " ".join(map(str, arr)) + "]"
            print(f"{label}:", count_inversions(arr, 0, len(arr) - 1))    # note: arr ends up sorted
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        long long countMerge(vector<int>& arr, int low, int mid, int high) {
            vector<int> left(arr.begin() + low, arr.begin() + mid + 1);
            vector<int> right(arr.begin() + mid + 1, arr.begin() + high + 1);
            int nl = left.size(), nr = right.size(), i = 0, j = 0, k = low;
            long long count = 0;
            while (i < nl && j < nr) {
                if (left[i] <= right[j]) arr[k++] = left[i++];
                else { arr[k++] = right[j++]; count += nl - i; }   // right[j] < all remaining left elements
            }
            while (i < nl) arr[k++] = left[i++];
            while (j < nr) arr[k++] = right[j++];
            return count;
        }

        long long countInversions(vector<int>& arr, int low, int high) {
            long long count = 0;
            if (low < high) {
                int mid = low + (high - low) / 2;
                count += countInversions(arr, low, mid);          // both in the left half
                count += countInversions(arr, mid + 1, high);     // both in the right half
                count += countMerge(arr, low, mid, high);         // one in each half
            }
            return count;
        }

        int main() {
            vector<vector<int>> tests = {{2, 4, 1, 3, 5}, {2, 4, 1, 3, 5, 2}, {5, 4, 3, 2, 1}, {1, 2, 3, 4, 5}};
            for (auto& arr : tests) {
                cout << "[";
                for (size_t k = 0; k < arr.size(); k++) cout << (k ? " " : "") << arr[k];
                cout << "]: " << countInversions(arr, 0, (int)arr.size() - 1) << "\\n";   // arr ends up sorted
            }
        }
    ''', java='''
        import java.util.Arrays;

        public class Main {
            static long countMerge(int[] arr, int low, int mid, int high) {
                int[] left = Arrays.copyOfRange(arr, low, mid + 1);
                int[] right = Arrays.copyOfRange(arr, mid + 1, high + 1);
                int i = 0, j = 0, k = low;
                long count = 0;
                while (i < left.length && j < right.length) {
                    if (left[i] <= right[j]) arr[k++] = left[i++];
                    else { arr[k++] = right[j++]; count += left.length - i; }   // right[j] < all remaining left
                }
                while (i < left.length) arr[k++] = left[i++];
                while (j < right.length) arr[k++] = right[j++];
                return count;
            }

            static long countInversions(int[] arr, int low, int high) {
                long count = 0;
                if (low < high) {
                    int mid = low + (high - low) / 2;
                    count += countInversions(arr, low, mid);          // both in the left half
                    count += countInversions(arr, mid + 1, high);     // both in the right half
                    count += countMerge(arr, low, mid, high);         // one in each half
                }
                return count;
            }

            public static void main(String[] args) {
                int[][] tests = {{2, 4, 1, 3, 5}, {2, 4, 1, 3, 5, 2}, {5, 4, 3, 2, 1}, {1, 2, 3, 4, 5}};
                for (int[] arr : tests) {
                    StringBuilder sb = new StringBuilder("[");
                    for (int k = 0; k < arr.length; k++) sb.append(k > 0 ? " " : "").append(arr[k]);
                    System.out.println(sb + "]: " + countInversions(arr, 0, arr.length - 1));   // arr ends up sorted
                }
            }
        }
    ''', js='''
        function countMerge(arr, low, mid, high) {
            const left = arr.slice(low, mid + 1), right = arr.slice(mid + 1, high + 1);
            let i = 0, j = 0, k = low, count = 0;
            while (i < left.length && j < right.length) {
                if (left[i] <= right[j]) arr[k++] = left[i++];
                else { arr[k++] = right[j++]; count += left.length - i; }   // right[j] < all remaining left
            }
            while (i < left.length) arr[k++] = left[i++];
            while (j < right.length) arr[k++] = right[j++];
            return count;
        }

        function countInversions(arr, low, high) {
            let count = 0;
            if (low < high) {
                const mid = low + Math.floor((high - low) / 2);
                count += countInversions(arr, low, mid);          // both in the left half
                count += countInversions(arr, mid + 1, high);     // both in the right half
                count += countMerge(arr, low, mid, high);         // one in each half
            }
            return count;
        }

        for (const arr of [[2, 4, 1, 3, 5], [2, 4, 1, 3, 5, 2], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5]]) {
            const label = "[" + arr.join(" ") + "]";
            console.log(`${label}:`, countInversions(arr, 0, arr.length - 1));   // arr ends up sorted
        }
    ''')
    yield complexity("O(n log n)", "O(n)")
    yield pitfall("Use `<=` when comparing `left[i]` with `right[j]`: equal elements are **not** an inversion (`arr[i] > arr[j]` is strict), so a tie must take the left element without counting. The count can reach `n(n − 1) / 2 ≈ 5 × 10¹⁷` for `n = 10⁹` — use a 64-bit integer in C++/Java.")

    yield section("Partition around a pivot", "separator-horizontal")
    yield define("Partition", "rearranging `arr[low..high]` around a chosen **pivot** value so that everything `≤ pivot` comes before everything `> pivot`, and returning the boundary. It is the heart of quick sort: after partitioning, the pivot is in its final sorted position and the two sides can be sorted independently.")
    yield io("arr = [3, 8, 6, 12, 10, 7], pivot = arr[5] = 7", "3 6 7 8 12 10 (any order inside each side is valid)")
    yield p("Naive, **stable** partition: move the pivot to the end, copy the `≤ pivot` elements and then the `> pivot` elements into a temporary array, copy back — `O(n)` time but `O(n)` extra space.")
    yield snippet("py", '''
        def partition_naive(arr, p):
            n = len(arr)
            arr[p], arr[n - 1] = arr[n - 1], arr[p]       # pivot goes to the end
            pivot = arr[n - 1]
            temp = [x for x in arr if x <= pivot]          # smaller-or-equal first (includes the pivot) ...
            temp += [x for x in arr if x > pivot]          # ... then the larger ones; order inside each part kept
            arr[:] = temp
            return len([x for x in arr if x <= pivot]) - 1   # index of the pivot

        arr = [3, 8, 6, 12, 10, 7]
        print("pivot index:", partition_naive(arr, 5))
        print(*arr)
    ''', out="pivot index: 2\n3 6 7 8 12 10")
    yield p("The two in-place schemes below do it in `O(1)` extra space. Both are **unstable**.")

    yield section("Lomuto partition", "arrow-move-right")
    yield io("arr = [10, 80, 30, 90, 40, 50, 70], pivot = arr[high] = 70", "pivot index 4, arr = 10 30 40 50 70 90 80")
    yield idea("Pivot is the **last** element. Keep an index `i` marking the end of the `≤ pivot` zone (initially `low − 1`). Scan `j` from `low` to `high − 1`: whenever `arr[j] ≤ pivot`, grow the zone (`i++`) and swap `arr[j]` into it. Finally swap the pivot into position `i + 1` — it is now exactly between the two zones, so it **is guaranteed to be in its final place**.")
    yield diagram('''
        pivot = 70       zone of <= pivot | zone of > pivot | unscanned
        start   i=-1     [10 80 30 90 40 50 | 70]
        j=0 10<=70  i=0  [10 | 80 30 90 40 50 | 70]
        j=1 80 > 70      [10 | 80 30 90 40 50 | 70]
        j=2 30<=70  i=1  [10 30 | 80 90 40 50 | 70]      swap arr[1], arr[2]
        j=3 90 > 70      [10 30 | 80 90 40 50 | 70]
        j=4 40<=70  i=2  [10 30 40 | 90 80 50 | 70]      swap arr[2], arr[4]
        j=5 50<=70  i=3  [10 30 40 50 | 80 90 | 70]      swap arr[3], arr[5]
        end: swap pivot into i+1 = 4  →  [10 30 40 50 | 70 | 90 80]
    ''', "Lomuto: the ≤ zone grows from the left; the pivot lands at i + 1")
    yield multi('''
        before: 10 80 30 90 40 50 70
        pivot index: 4
        after: 10 30 40 50 70 90 80
    ''', py='''
        def lomuto_partition(arr, low, high):
            pivot = arr[high]                         # last element is the pivot
            i = low - 1                               # end of the "<= pivot" zone
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]   # pull arr[j] into the zone
            arr[i + 1], arr[high] = arr[high], arr[i + 1]   # pivot goes between the zones
            return i + 1

        arr = [10, 80, 30, 90, 40, 50, 70]
        print("before:", *arr)
        print("pivot index:", lomuto_partition(arr, 0, len(arr) - 1))
        print("after:", *arr)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        int lomutoPartition(vector<int>& arr, int low, int high) {
            int pivot = arr[high];                        // last element is the pivot
            int i = low - 1;                              // end of the "<= pivot" zone
            for (int j = low; j < high; j++) {
                if (arr[j] <= pivot) swap(arr[++i], arr[j]);   // pull arr[j] into the zone
            }
            swap(arr[i + 1], arr[high]);                  // pivot goes between the zones
            return i + 1;
        }

        void show(const char* label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        int main() {
            vector<int> arr = {10, 80, 30, 90, 40, 50, 70};
            show("before:", arr);
            cout << "pivot index: " << lomutoPartition(arr, 0, (int)arr.size() - 1) << "\\n";
            show("after:", arr);
        }
    ''', java='''
        public class Main {
            static int lomutoPartition(int[] arr, int low, int high) {
                int pivot = arr[high];                        // last element is the pivot
                int i = low - 1;                              // end of the "<= pivot" zone
                for (int j = low; j < high; j++) {
                    if (arr[j] <= pivot) {
                        i++;
                        int t = arr[i]; arr[i] = arr[j]; arr[j] = t;   // pull arr[j] into the zone
                    }
                }
                int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;   // pivot between the zones
                return i + 1;
            }

            static String join(int[] a) {
                StringBuilder sb = new StringBuilder();
                for (int x : a) sb.append(' ').append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                int[] arr = {10, 80, 30, 90, 40, 50, 70};
                System.out.println("before:" + join(arr));
                System.out.println("pivot index: " + lomutoPartition(arr, 0, arr.length - 1));
                System.out.println("after:" + join(arr));
            }
        }
    ''', js='''
        function lomutoPartition(arr, low, high) {
            const pivot = arr[high];                          // last element is the pivot
            let i = low - 1;                                  // end of the "<= pivot" zone
            for (let j = low; j < high; j++) {
                if (arr[j] <= pivot) {
                    i++;
                    [arr[i], arr[j]] = [arr[j], arr[i]];      // pull arr[j] into the zone
                }
            }
            [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];   // pivot goes between the zones
            return i + 1;
        }

        const arr = [10, 80, 30, 90, 40, 50, 70];
        console.log("before:", arr.join(" "));
        console.log("pivot index:", lomutoPartition(arr, 0, arr.length - 1));
        console.log("after:", arr.join(" "));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Lomuto returns the pivot's **final index** — quick sort then recurses on `[low..p−1]` and `[p+1..high]`, never touching `p` again. To use a different pivot (random, median-of-three), swap it to `arr[high]` first.")

    yield section("Hoare partition", "arrows-horizontal")
    yield io("arr = [10, 80, 30, 90, 40, 50, 70, 100, 120, 10, 5], pivot = arr[low] = 10", "returns 1, arr = 5 10 30 90 40 50 70 100 120 80 10")
    yield idea("Pivot is the **first** element. Two indices walk towards each other: `i` from the left stops at an element `≥ pivot`, `j` from the right stops at one `≤ pivot`. If they have not crossed, swap and continue; once `i ≥ j`, return `j`. Everything in `[low..j]` is `≤ pivot` and everything in `[j+1..high]` is `≥ pivot` — but the pivot itself can be **anywhere in the left part**, so quick sort must recurse on `[low..j]` and `[j+1..high]`, not skip `j`.")
    yield multi('''
        before: 10 80 30 90 40 50 70 100 120 10 5
        returned: 1
        after: 5 10 30 90 40 50 70 100 120 80 10
    ''', py='''
        def hoare_partition(arr, low, high):
            pivot = arr[low]                     # first element is the pivot
            i, j = low - 1, high + 1
            while True:
                i += 1
                while arr[i] < pivot:            # stop at something >= pivot
                    i += 1
                j -= 1
                while arr[j] > pivot:            # stop at something <= pivot
                    j -= 1
                if i >= j:                       # crossed: [low..j] <= pivot <= [j+1..high]
                    return j
                arr[i], arr[j] = arr[j], arr[i]

        arr = [10, 80, 30, 90, 40, 50, 70, 100, 120, 10, 5]
        print("before:", *arr)
        print("returned:", hoare_partition(arr, 0, len(arr) - 1))
        print("after:", *arr)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        int hoarePartition(vector<int>& arr, int low, int high) {
            int pivot = arr[low];                    // first element is the pivot
            int i = low - 1, j = high + 1;
            while (true) {
                do { i++; } while (arr[i] < pivot);  // stop at something >= pivot
                do { j--; } while (arr[j] > pivot);  // stop at something <= pivot
                if (i >= j) return j;                // crossed: [low..j] <= pivot <= [j+1..high]
                swap(arr[i], arr[j]);
            }
        }

        void show(const char* label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        int main() {
            vector<int> arr = {10, 80, 30, 90, 40, 50, 70, 100, 120, 10, 5};
            show("before:", arr);
            cout << "returned: " << hoarePartition(arr, 0, (int)arr.size() - 1) << "\\n";
            show("after:", arr);
        }
    ''', java='''
        public class Main {
            static int hoarePartition(int[] arr, int low, int high) {
                int pivot = arr[low];                    // first element is the pivot
                int i = low - 1, j = high + 1;
                while (true) {
                    do { i++; } while (arr[i] < pivot);  // stop at something >= pivot
                    do { j--; } while (arr[j] > pivot);  // stop at something <= pivot
                    if (i >= j) return j;                // crossed: [low..j] <= pivot <= [j+1..high]
                    int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
                }
            }

            static String join(int[] a) {
                StringBuilder sb = new StringBuilder();
                for (int x : a) sb.append(' ').append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                int[] arr = {10, 80, 30, 90, 40, 50, 70, 100, 120, 10, 5};
                System.out.println("before:" + join(arr));
                System.out.println("returned: " + hoarePartition(arr, 0, arr.length - 1));
                System.out.println("after:" + join(arr));
            }
        }
    ''', js='''
        function hoarePartition(arr, low, high) {
            const pivot = arr[low];                      // first element is the pivot
            let i = low - 1, j = high + 1;
            while (true) {
                do { i++; } while (arr[i] < pivot);      // stop at something >= pivot
                do { j--; } while (arr[j] > pivot);      // stop at something <= pivot
                if (i >= j) return j;                    // crossed: [low..j] <= pivot <= [j+1..high]
                [arr[i], arr[j]] = [arr[j], arr[i]];
            }
        }

        const arr = [10, 80, 30, 90, 40, 50, 70, 100, 120, 10, 5];
        console.log("before:", arr.join(" "));
        console.log("returned:", hoarePartition(arr, 0, arr.length - 1));
        console.log("after:", arr.join(" "));
    ''')
    yield complexity("O(n)", "O(1)")
    yield table(
        ["", "Lomuto", "Hoare"],
        ["Pivot", "last element `arr[high]`", "first element `arr[low]`"],
        ["Returns", "the pivot's final index `p`", "a boundary `j`; the pivot is somewhere in `[low..j]`"],
        ["Quick sort recursion", "`[low..p−1]` and `[p+1..high]`", "`[low..j]` and `[j+1..high]`"],
        ["Swaps", "about `n/2` on average", "about `n/6` — roughly three times fewer"],
        ["All-equal input", "degenerates: every element goes left → `O(n²)`", "splits in the middle → stays `O(n log n)`"],
        ["Simplicity", "easier to get right", "the stop conditions and the `i >= j` test are easy to get wrong"],
    )
    yield pitfall("With Hoare, recursing on `[low..j−1]` and `[j+1..high]` (as for Lomuto) loses the element at `j`, which is **not** necessarily the pivot. And the inner loops must use strict `<` / `>` — with `<=` they can run off the ends of the array.")

    yield section("Quick sort", "bolt")
    yield io("arr = [10, 80, 30, 90, 40, 50, 70]", "10 30 40 50 70 80 90", "arr = [3, 5, 6, 7, 1, 2, 4]", "1 2 3 4 5 6 7")
    yield idea("**Divide and conquer** where the work is in the *divide*: partition the array around a pivot, then sort the two sides recursively. There is no merge step — once both sides are sorted, the whole array is, because every left element `≤` pivot `≤` every right element.")
    yield diagram('''
        [3 5 6 7 1 2 4]   pivot 4 (Lomuto, last)
               ↓ partition
        [3 1 2] 4 [5 6 7]          4 is final
          ↓            ↓
        [1] 2 [3]    [5 6] 7        2 and 7 are final
                       ↓
                     [5] 6          6 is final
        result: 1 2 3 4 5 6 7
    ''', "Each partition fixes the pivot; the sides are sorted independently")
    yield multi('''
        lomuto: 10 30 40 50 70 80 90
        hoare: 10 30 40 50 70 80 90
        lomuto: 1 2 3 4 5 6 7
        hoare: 1 2 3 4 5 6 7
    ''', py='''
        def lomuto_partition(arr, low, high):
            pivot, i = arr[high], low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def hoare_partition(arr, low, high):
            pivot, i, j = arr[low], low - 1, high + 1
            while True:
                i += 1
                while arr[i] < pivot: i += 1
                j -= 1
                while arr[j] > pivot: j -= 1
                if i >= j: return j
                arr[i], arr[j] = arr[j], arr[i]

        def quick_sort_lomuto(arr, low, high):
            if low < high:
                p = lomuto_partition(arr, low, high)
                quick_sort_lomuto(arr, low, p - 1)      # pivot at p is final: skip it
                quick_sort_lomuto(arr, p + 1, high)

        def quick_sort_hoare(arr, low, high):
            if low < high:
                p = hoare_partition(arr, low, high)
                quick_sort_hoare(arr, low, p)           # p is a boundary, not the pivot: include it
                quick_sort_hoare(arr, p + 1, high)

        for arr in ([10, 80, 30, 90, 40, 50, 70], [3, 5, 6, 7, 1, 2, 4]):
            a, b = arr[:], arr[:]
            quick_sort_lomuto(a, 0, len(a) - 1)
            quick_sort_hoare(b, 0, len(b) - 1)
            print("lomuto:", *a)
            print("hoare:", *b)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        int lomutoPartition(vector<int>& arr, int low, int high) {
            int pivot = arr[high], i = low - 1;
            for (int j = low; j < high; j++)
                if (arr[j] <= pivot) swap(arr[++i], arr[j]);
            swap(arr[i + 1], arr[high]);
            return i + 1;
        }

        int hoarePartition(vector<int>& arr, int low, int high) {
            int pivot = arr[low], i = low - 1, j = high + 1;
            while (true) {
                do { i++; } while (arr[i] < pivot);
                do { j--; } while (arr[j] > pivot);
                if (i >= j) return j;
                swap(arr[i], arr[j]);
            }
        }

        void quickSortLomuto(vector<int>& arr, int low, int high) {
            if (low < high) {
                int p = lomutoPartition(arr, low, high);
                quickSortLomuto(arr, low, p - 1);        // pivot at p is final: skip it
                quickSortLomuto(arr, p + 1, high);
            }
        }

        void quickSortHoare(vector<int>& arr, int low, int high) {
            if (low < high) {
                int p = hoarePartition(arr, low, high);
                quickSortHoare(arr, low, p);             // p is a boundary, not the pivot: include it
                quickSortHoare(arr, p + 1, high);
            }
        }

        void show(const char* label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        int main() {
            vector<vector<int>> tests = {{10, 80, 30, 90, 40, 50, 70}, {3, 5, 6, 7, 1, 2, 4}};
            for (const auto& arr : tests) {
                vector<int> a = arr, b = arr;
                quickSortLomuto(a, 0, (int)a.size() - 1);
                quickSortHoare(b, 0, (int)b.size() - 1);
                show("lomuto:", a);
                show("hoare:", b);
            }
        }
    ''', java='''
        public class Main {
            static int lomutoPartition(int[] arr, int low, int high) {
                int pivot = arr[high], i = low - 1;
                for (int j = low; j < high; j++)
                    if (arr[j] <= pivot) { i++; int t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
                int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;
                return i + 1;
            }

            static int hoarePartition(int[] arr, int low, int high) {
                int pivot = arr[low], i = low - 1, j = high + 1;
                while (true) {
                    do { i++; } while (arr[i] < pivot);
                    do { j--; } while (arr[j] > pivot);
                    if (i >= j) return j;
                    int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
                }
            }

            static void quickSortLomuto(int[] arr, int low, int high) {
                if (low < high) {
                    int p = lomutoPartition(arr, low, high);
                    quickSortLomuto(arr, low, p - 1);        // pivot at p is final: skip it
                    quickSortLomuto(arr, p + 1, high);
                }
            }

            static void quickSortHoare(int[] arr, int low, int high) {
                if (low < high) {
                    int p = hoarePartition(arr, low, high);
                    quickSortHoare(arr, low, p);             // p is a boundary, not the pivot: include it
                    quickSortHoare(arr, p + 1, high);
                }
            }

            static String join(int[] a) {
                StringBuilder sb = new StringBuilder();
                for (int x : a) sb.append(' ').append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                int[][] tests = {{10, 80, 30, 90, 40, 50, 70}, {3, 5, 6, 7, 1, 2, 4}};
                for (int[] arr : tests) {
                    int[] a = arr.clone(), b = arr.clone();
                    quickSortLomuto(a, 0, a.length - 1);
                    quickSortHoare(b, 0, b.length - 1);
                    System.out.println("lomuto:" + join(a));
                    System.out.println("hoare:" + join(b));
                }
            }
        }
    ''', js='''
        function lomutoPartition(arr, low, high) {
            const pivot = arr[high];
            let i = low - 1;
            for (let j = low; j < high; j++)
                if (arr[j] <= pivot) { i++; [arr[i], arr[j]] = [arr[j], arr[i]]; }
            [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
            return i + 1;
        }

        function hoarePartition(arr, low, high) {
            const pivot = arr[low];
            let i = low - 1, j = high + 1;
            while (true) {
                do { i++; } while (arr[i] < pivot);
                do { j--; } while (arr[j] > pivot);
                if (i >= j) return j;
                [arr[i], arr[j]] = [arr[j], arr[i]];
            }
        }

        function quickSortLomuto(arr, low, high) {
            if (low < high) {
                const p = lomutoPartition(arr, low, high);
                quickSortLomuto(arr, low, p - 1);            // pivot at p is final: skip it
                quickSortLomuto(arr, p + 1, high);
            }
        }

        function quickSortHoare(arr, low, high) {
            if (low < high) {
                const p = hoarePartition(arr, low, high);
                quickSortHoare(arr, low, p);                 // p is a boundary, not the pivot: include it
                quickSortHoare(arr, p + 1, high);
            }
        }

        for (const arr of [[10, 80, 30, 90, 40, 50, 70], [3, 5, 6, 7, 1, 2, 4]]) {
            const a = [...arr], b = [...arr];
            quickSortLomuto(a, 0, a.length - 1);
            quickSortHoare(b, 0, b.length - 1);
            console.log("lomuto:", a.join(" "));
            console.log("hoare:", b.join(" "));
        }
    ''')
    yield complexity("O(n log n) average · O(n²) worst", "O(log n) stack on average")

    yield section("Analysis of quick sort", "chart-bar")
    yield table(
        ["Case", "When", "Recurrence", "Time"],
        ["Best", "every partition splits in half", "`T(n) = 2T(n/2) + Θ(n)`", "`Θ(n log n)`"],
        ["Average", "random pivots / random input", "`T(n) = T(n/4) + T(3n/4) + Θ(n)` (a typical uneven split)", "`Θ(n log n)` — about `1.39 n log2 n` comparisons"],
        ["Worst", "the pivot is always the min or max — sorted input with first/last pivot, or all equal values with Lomuto", "`T(n) = T(n − 1) + Θ(n)`", "`Θ(n²)`"],
        ["Space", "recursion depth", "`O(log n)` average; `O(n)` in the worst case unless the smaller side is recursed first", ""],
    )
    yield p("Despite the `O(n²)` worst case, quick sort is usually the fastest comparison sort in practice:")
    yield cards(
        ("In-place", "Partition needs `O(1)` extra memory; merge sort needs an `O(n)` buffer.", "box"),
        ("Cache-friendly", "Partition sweeps the array sequentially; heap sort jumps around and misses the cache.", "cpu"),
        ("Small constants", "The inner loop is a compare and an occasional swap — less work per element than merge sort's copying.", "bolt"),
        ("Tail recursion", "The second recursive call can become a loop; recursing on the *smaller* side first bounds the stack at `O(log n)`.", "repeat"),
        ("Worst case is avoidable", "A random pivot (or median-of-three) makes the `O(n²)` case astronomically unlikely; introsort falls back to heap sort if the depth gets too large.", "dice"),
        ("Not stable", "Both in-place partitions move elements across the range, so equal keys can swap order. Use merge sort / Timsort when stability matters.", "equal-not"),
        cols=3,
    )
    yield pitfall("Three statements in the original notes were wrong: the *best* case is `Θ(n log n)`, not `Θ(log n)` — you cannot sort without looking at every element; the space complexity is `O(log n)` on average (recursion depth), not `Θ(n)`; and Hoare's partition is not \"three times faster\" overall — it does about **three times fewer swaps** on average, which makes it somewhat faster. Hoare also handles many equal keys gracefully, while Lomuto degrades to `O(n²)` on them.")
    yield note("`std::sort` in C++ is **introsort**: quick sort with median-of-three pivots, switching to heap sort when the recursion depth exceeds `2 log n` and to insertion sort for ranges of ≈ 16 elements. Java sorts primitives with a dual-pivot quick sort. Both are `O(n log n)` worst case in practice.")

    yield section("Heap sort", "hierarchy")
    yield io("arr = [4, 10, 3, 5, 1, 12, 7]", "1 3 4 5 7 10 12")
    yield idea("Selection sort finds the maximum in `O(n)` per pass; a **max-heap** finds it in `O(1)` and restores itself in `O(log n)`. So: build a max-heap from the array in place, then repeatedly swap the root (the maximum) with the last element of the heap, shrink the heap by one and *heapify* the new root down. The sorted elements accumulate at the end of the array.")
    yield diagram('''
        array [12 10 7 5 1 3 4] as a max-heap:      children of i are 2i+1 and 2i+2

                      12 (0)
                    /        \\
               10 (1)         7 (2)
              /     \\        /    \\
           5 (3)   1 (4)   3 (5)  4 (6)

        swap root 12 with last (4)  →  [4 10 7 5 1 3 | 12]   heapify 4 down over the first 6
    ''', "A max-heap stored in an array; sorting pulls the root out one at a time")
    yield steps(
        ("heapify(i)", "Compare node `i` with its children; swap with the larger child if it is bigger, and continue down. `O(log n)`."),
        ("build heap", "Call `heapify` on every internal node from the last one (`n/2 − 1`) down to the root. Leaves are already heaps. This takes `O(n)` in total, not `O(n log n)`."),
        ("extract", "For `i = n − 1 … 1`: swap `arr[0]` (the max) with `arr[i]`, then `heapify(0)` on the heap of size `i`. Each extraction is `O(log n)`."),
    )
    yield multi('''
        max-heap: 12 10 7 5 1 3 4
        sorted: 1 3 4 5 7 10 12
        max-heap: 50 20 10 4 15
        sorted: 4 10 15 20 50
    ''', py='''
        def heapify(arr, n, i):
            largest = i
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and arr[left] > arr[largest]:
                largest = left
            if right < n and arr[right] > arr[largest]:
                largest = right
            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                heapify(arr, n, largest)                 # keep sinking the displaced value

        def build_heap(arr):
            n = len(arr)
            for i in range(n // 2 - 1, -1, -1):          # internal nodes, bottom-up
                heapify(arr, n, i)

        def heap_sort(arr):
            n = len(arr)
            build_heap(arr)
            print("max-heap:", *arr)
            for i in range(n - 1, 0, -1):
                arr[0], arr[i] = arr[i], arr[0]          # max goes to the end
                heapify(arr, i, 0)                       # restore the heap of size i

        for arr in ([4, 10, 3, 5, 1, 12, 7], [50, 20, 10, 4, 15]):
            heap_sort(arr)
            print("sorted:", *arr)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        void heapify(vector<int>& arr, int n, int i) {
            int largest = i, left = 2 * i + 1, right = 2 * i + 2;
            if (left < n && arr[left] > arr[largest]) largest = left;
            if (right < n && arr[right] > arr[largest]) largest = right;
            if (largest != i) {
                swap(arr[i], arr[largest]);
                heapify(arr, n, largest);                // keep sinking the displaced value
            }
        }

        void show(const char* label, const vector<int>& v) {
            cout << label;
            for (int x : v) cout << " " << x;
            cout << "\\n";
        }

        void heapSort(vector<int>& arr) {
            int n = arr.size();
            for (int i = n / 2 - 1; i >= 0; i--) heapify(arr, n, i);   // build heap, bottom-up
            show("max-heap:", arr);
            for (int i = n - 1; i > 0; i--) {
                swap(arr[0], arr[i]);                    // max goes to the end
                heapify(arr, i, 0);                      // restore the heap of size i
            }
        }

        int main() {
            vector<vector<int>> tests = {{4, 10, 3, 5, 1, 12, 7}, {50, 20, 10, 4, 15}};
            for (auto& arr : tests) {
                heapSort(arr);
                show("sorted:", arr);
            }
        }
    ''', java='''
        public class Main {
            static void heapify(int[] arr, int n, int i) {
                int largest = i, left = 2 * i + 1, right = 2 * i + 2;
                if (left < n && arr[left] > arr[largest]) largest = left;
                if (right < n && arr[right] > arr[largest]) largest = right;
                if (largest != i) {
                    int t = arr[i]; arr[i] = arr[largest]; arr[largest] = t;
                    heapify(arr, n, largest);            // keep sinking the displaced value
                }
            }

            static String join(int[] a) {
                StringBuilder sb = new StringBuilder();
                for (int x : a) sb.append(' ').append(x);
                return sb.toString();
            }

            static void heapSort(int[] arr) {
                int n = arr.length;
                for (int i = n / 2 - 1; i >= 0; i--) heapify(arr, n, i);   // build heap, bottom-up
                System.out.println("max-heap:" + join(arr));
                for (int i = n - 1; i > 0; i--) {
                    int t = arr[0]; arr[0] = arr[i]; arr[i] = t;   // max goes to the end
                    heapify(arr, i, 0);                            // restore the heap of size i
                }
            }

            public static void main(String[] args) {
                int[][] tests = {{4, 10, 3, 5, 1, 12, 7}, {50, 20, 10, 4, 15}};
                for (int[] arr : tests) {
                    heapSort(arr);
                    System.out.println("sorted:" + join(arr));
                }
            }
        }
    ''', js='''
        function heapify(arr, n, i) {
            let largest = i;
            const left = 2 * i + 1, right = 2 * i + 2;
            if (left < n && arr[left] > arr[largest]) largest = left;
            if (right < n && arr[right] > arr[largest]) largest = right;
            if (largest !== i) {
                [arr[i], arr[largest]] = [arr[largest], arr[i]];
                heapify(arr, n, largest);                // keep sinking the displaced value
            }
        }

        function heapSort(arr) {
            const n = arr.length;
            for (let i = Math.floor(n / 2) - 1; i >= 0; i--) heapify(arr, n, i);   // build heap, bottom-up
            console.log("max-heap:", arr.join(" "));
            for (let i = n - 1; i > 0; i--) {
                [arr[0], arr[i]] = [arr[i], arr[0]];     // max goes to the end
                heapify(arr, i, 0);                      // restore the heap of size i
            }
        }

        for (const arr of [[4, 10, 3, 5, 1, 12, 7], [50, 20, 10, 4, 15]]) {
            heapSort(arr);
            console.log("sorted:", arr.join(" "));
        }
    ''')
    yield complexity("O(n log n) in every case", "O(1)")
    yield ul(
        "An optimisation of **selection sort**: the same *extract the extreme, shrink the range* loop, with an `O(log n)` extraction instead of `O(n)`.",
        "**Guaranteed** `O(n log n)` and **in-place** — the combination merge sort and quick sort each lack. The price: poor cache locality, so it is slower than quick sort in practice.",
        "**Not stable**: swapping the root with the last leaf can jump an element over equal keys.",
        "Used as the fallback inside **introsort** (`std::sort`) and wherever a worst-case guarantee matters. The heap itself is the DSA Basics → Heap topic.",
    )

    yield section("Interview Q&A", "message-question")
    yield qa("Which sorting algorithm would you pick, and why?",
             "For general use, the library sort: Timsort (Python/Java objects/JS) or introsort (`std::sort`). Hand-rolled: quick sort for speed on arrays in memory; merge sort when stability or a guaranteed `n log n` is needed, for linked lists, or for data that does not fit in memory; heap sort when memory is tight and the worst case must be bounded; insertion sort for tiny or nearly sorted inputs; counting/radix sort when keys are small integers.")
    yield qa("What does stable mean, and which algorithms are stable?",
             "Equal keys keep their input order. Stable: bubble, insertion, merge, Timsort, counting sort. Not stable: selection, quick, heap, `std::sort`. It matters for multi-key sorts (sort by name, then stably by marks) and for sorting records by one field while keeping a meaningful prior order.")
    yield qa("Why is quick sort faster than merge sort in practice if both are O(n log n)?",
             "Quick sort partitions in place with a tight inner loop and sequential memory access; merge sort copies every element into a buffer at every level. Quick sort does more comparisons on average (`≈ 1.39 n log n` vs `n log n`) but fewer memory moves and far fewer cache misses. Merge sort wins on linked lists, on stability, and when a worst-case guarantee is required.")
    yield qa("When does quick sort degrade to O(n²), and how do you prevent it?",
             "When every partition is maximally unbalanced: already sorted or reverse-sorted input with a first/last pivot, or many equal keys with Lomuto. Fixes: choose a random pivot or the median of three, use Hoare or three-way (Dutch flag) partitioning for duplicates, recurse on the smaller side first to cap the stack, and switch to heap sort if the depth exceeds `2 log n` (introsort).")
    yield qa("Can you sort in better than O(n log n)?",
             "Not by comparing: a comparison sort must distinguish `n!` permutations, which needs `log2(n!) = Θ(n log n)` comparisons. Non-comparison sorts use the structure of the keys: counting sort is `O(n + k)` for integers in `0..k`, radix sort `O(d(n + k))` for `d`-digit keys, bucket sort for uniformly distributed reals.")
    yield qa("What is the difference between sort() and sorted() in Python?",
             "`list.sort()` sorts the list in place and returns `None`; `sorted(iterable)` accepts any iterable and returns a new list, leaving the input untouched. Both are Timsort, stable, and take the same `key=` and `reverse=` arguments.")
    yield qa("Why does [10, 9, 1].sort() give [1, 10, 9] in JavaScript?",
             "Without a comparator, `Array.prototype.sort` converts elements to strings and compares them lexicographically: `\"10\" < \"9\"` because `\"1\" < \"9\"`. Always pass `(a, b) => a - b` for numbers.")
    yield qa("How many swaps does selection sort make, and why is that interesting?",
             "At most `n − 1` — one per pass — regardless of input, versus `O(n²)` for bubble sort and `O(n²)` shifts for insertion sort. On media where writes are expensive (flash) that can matter; cycle sort takes the idea to its limit with the minimum possible number of writes.")
