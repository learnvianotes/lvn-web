from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Searching, Sorting & Hashing"


@topic(G, "searching", "Searching", "search")
def _():
    yield lead("Advanced searching is rarely “find `x` in a sorted array”. It is recognising that a problem has a **monotone structure** — an index range that can be halved, an answer range that can be halved, or two ends that can be walked inwards — and then applying binary search or two pointers to it.")
    yield define("Binary search (general form)", "given a predicate that is `false` for a prefix of the search space and `true` for the rest, find the boundary in `O(log n)` probes. Searching for a value in a sorted array is just the special case `arr[i] >= x`.")

    yield section("The four patterns in this topic", "puzzle")
    yield cards(
        ("Binary search on an index", "The array is sorted, or *piecewise* sorted (rotated, bitonic). Decide in `O(1)` which half can contain the answer and discard the other.", "search"),
        ("Binary search on the answer", "The array is not sorted, but the *answer* is a number and “is `ans` feasible?” is monotone. Binary search over the answer range, checking feasibility in `O(n)`.", "target"),
        ("Two pointers", "One pointer at each end of a sorted array; the sum tells you which pointer to move. Pair / triplet with a given sum.", "arrows-left-right"),
        ("Cycle detection on indices", "Treat `i → arr[i]` as a linked list. Floyd's tortoise-and-hare finds the repeated value in `O(n)` time and `O(1)` space without touching the array.", "repeat"),
        cols=2,
    )
    yield table(
        ["Problem", "Pattern", "Time", "Extra space"],
        ["Search in an infinite sorted array", "doubling + binary search", "`O(log p)` (`p` = position)", "`O(1)`"],
        ["Search in a sorted rotated array", "binary search with a sorted-half test", "`O(log n)`", "`O(1)`"],
        ["Find a peak element", "binary search towards the rising side", "`O(log n)`", "`O(1)`"],
        ["Pair with given sum (sorted)", "two pointers", "`O(n)`", "`O(1)`"],
        ["Triplet with given sum (sorted)", "fix one + two pointers", "`O(n²)`", "`O(1)`"],
        ["Median of two sorted arrays", "binary search on a partition", "`O(log min(n1, n2))`", "`O(1)`"],
        ["Repeating element", "Floyd's cycle detection", "`O(n)`", "`O(1)`"],
        ["Allocate minimum pages", "binary search on the answer", "`O(n log S)`", "`O(1)`"],
    )
    yield note("Every solution below uses the same loop skeleton: `while low <= high: mid = low + (high - low) // 2 …` with `low = mid + 1` or `high = mid - 1`. Writing `low + (high - low) / 2` instead of `(low + high) / 2` avoids integer overflow in C++ and Java when `low + high` exceeds `2³¹ - 1`.")

    # ── infinite sorted array ─────────────────────────────────────────
    yield section("Search in an infinite sorted array", "infinity")
    yield io("arr = [10, 15, 20, 40, 80, 80, 90, 100, 120, …], x = 100", "7",
             "arr = [10, 15, 20, 40, 80, 80, 90, 100, 120, …], x = 50", "-1")
    yield p("The array has no known size (think of a stream, a file, or an API that returns elements by index), so `high = n - 1` is unavailable. A linear scan is `O(p)` where `p` is the position of `x`. We can do better: find a bracket around `x` first.")
    yield idea("**Double the index** until `arr[i] >= x`: probe `1, 2, 4, 8, …`. After `O(log p)` probes we know `x` lies in `(i/2, i]`, a range of size `i/2`. One binary search on that range finds it in another `O(log p)` steps.")
    yield steps(
        ("Check index 0", "If `arr[0] == x` return 0."),
        ("Gallop", "Start at `i = 1`; while `arr[i] < x` set `i = 2i`. Stop when `arr[i] >= x` (or we have overshot into values larger than `x`)."),
        ("Binary search", "Search for `x` in `[i/2 + 1, i]` — every index below `i/2 + 1` was already seen to be `< x`."),
    )
    yield snippet("py", r'''
        # Naive: scan until we pass x — O(p) probes
        def search(arr, x):
            i = 0
            while True:
                if arr[i] == x:
                    return i
                if arr[i] > x:      # sorted, so x cannot appear later
                    return -1
                i += 1

        arr = [10, 15, 20, 40, 80, 80, 90, 100, 120]
        print(search(arr, 100))
        print(search(arr, 50))
    ''', out="7\n-1")
    yield p("The efficient version only needs `at(i)` — a way to read the element at position `i`. The demo below models the infinite array with a function that returns a very large value beyond the data we actually have, which is exactly how a real stream would look (“everything further out is bigger than anything we are searching for”).")
    yield multi('''
        x = 100 → 7
        x = 50 → -1
        x = 40 → 3
    ''', py=r'''
        INF = 10**9
        data = [10, 15, 20, 40, 80, 80, 90, 100, 120]

        def at(i):                      # the "infinite" array: beyond our data everything is huge
            return data[i] if i < len(data) else INF

        def binary_search(low, high, x):
            while low <= high:
                mid = low + (high - low) // 2
                if at(mid) == x:
                    return mid
                if at(mid) < x:
                    low = mid + 1
                else:
                    high = mid - 1
            return -1

        def search(x):
            if at(0) == x:
                return 0
            i = 1
            while at(i) < x:            # gallop: 1, 2, 4, 8, ...
                i *= 2
            if at(i) == x:
                return i
            return binary_search(i // 2 + 1, i - 1, x)

        for x in (100, 50, 40):
            print(f"x = {x} → {search(x)}")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        const int INF = 1000000000;
        vector<int> arr = {10, 15, 20, 40, 80, 80, 90, 100, 120};

        int at(int i) {                  // the "infinite" array: beyond our data everything is huge
            return i < (int)arr.size() ? arr[i] : INF;
        }

        int binarySearch(int low, int high, int x) {
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (at(mid) == x) return mid;
                if (at(mid) < x) low = mid + 1;
                else high = mid - 1;
            }
            return -1;
        }

        int search(int x) {
            if (at(0) == x) return 0;
            int i = 1;
            while (at(i) < x) i *= 2;    // gallop: 1, 2, 4, 8, ...
            if (at(i) == x) return i;
            return binarySearch(i / 2 + 1, i - 1, x);
        }

        int main() {
            for (int x : {100, 50, 40})
                cout << "x = " << x << " → " << search(x) << "\n";
        }
    ''', java=r'''
        public class Main {
            static final int INF = 1_000_000_000;
            static int[] data = {10, 15, 20, 40, 80, 80, 90, 100, 120};

            static int at(int i) {       // the "infinite" array: beyond our data everything is huge
                return i < data.length ? data[i] : INF;
            }

            static int binarySearch(int low, int high, int x) {
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (at(mid) == x) return mid;
                    if (at(mid) < x) low = mid + 1;
                    else high = mid - 1;
                }
                return -1;
            }

            static int search(int x) {
                if (at(0) == x) return 0;
                int i = 1;
                while (at(i) < x) i *= 2;   // gallop: 1, 2, 4, 8, ...
                if (at(i) == x) return i;
                return binarySearch(i / 2 + 1, i - 1, x);
            }

            public static void main(String[] args) {
                for (int x : new int[]{100, 50, 40})
                    System.out.println("x = " + x + " → " + search(x));
            }
        }
    ''', js=r'''
        const INF = 1e9;
        const data = [10, 15, 20, 40, 80, 80, 90, 100, 120];

        const at = (i) => (i < data.length ? data[i] : INF);   // the "infinite" array

        function binarySearch(low, high, x) {
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (at(mid) === x) return mid;
                if (at(mid) < x) low = mid + 1;
                else high = mid - 1;
            }
            return -1;
        }

        function search(x) {
            if (at(0) === x) return 0;
            let i = 1;
            while (at(i) < x) i *= 2;       // gallop: 1, 2, 4, 8, ...
            if (at(i) === x) return i;
            return binarySearch(Math.floor(i / 2) + 1, i - 1, x);
        }

        for (const x of [100, 50, 40]) console.log(`x = ${x} → ${search(x)}`);
    ''')
    yield complexity("O(log p)", "O(1)")
    yield note("`p` is the position of `x`, not the (unknown) array size. The same “gallop then binary search” trick is **exponential search**; Timsort uses it to merge runs of very different lengths.")

    # ── sorted rotated array ──────────────────────────────────────────
    yield section("Search in a sorted rotated array", "rotate-clockwise")
    yield io("arr = [10, 20, 30, 40, 50, 8, 9], x = 30", "2", "arr = [100, 200, 300, 10, 20], x = 40", "-1")
    yield p("A sorted array rotated by some unknown amount consists of two sorted runs, with the second run entirely smaller than the first. Plain binary search fails because `arr[mid] < x` no longer tells you which side `x` is on.")
    yield diagram('''
        index:   0   1   2   3   4   5   6
        value:  10  20  30  40  50   8   9
                └─── sorted run 1 ────┘ └ run 2 ┘
                 mid = 3 → arr[low]=10 < arr[mid]=40, so [0..3] is sorted
    ''', "Whichever half contains mid's boundary, the other half is always a plain sorted run")
    yield idea("At every step **one of the two halves is sorted** — if `arr[low] < arr[mid]` the left half is, otherwise the right half is. Check whether `x` lies inside the sorted half (a simple range test); if yes, search there, otherwise search the other half. Each step still discards half the array.")
    yield multi('''
        x = 30 → 2
        x = 8 → 5
        x = 40 → -1
    ''', py=r'''
        def search_rotated(arr, x):
            low, high = 0, len(arr) - 1
            while low <= high:
                mid = low + (high - low) // 2
                if arr[mid] == x:
                    return mid
                if arr[low] <= arr[mid]:                 # left half [low..mid] is sorted
                    if arr[low] <= x < arr[mid]:
                        high = mid - 1
                    else:
                        low = mid + 1
                else:                                    # right half [mid..high] is sorted
                    if arr[mid] < x <= arr[high]:
                        low = mid + 1
                    else:
                        high = mid - 1
            return -1

        a = [10, 20, 30, 40, 50, 8, 9]
        print("x = 30 →", search_rotated(a, 30))
        print("x = 8 →", search_rotated(a, 8))
        print("x = 40 →", search_rotated([100, 200, 300, 10, 20], 40))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int searchRotated(const vector<int>& arr, int x) {
            int low = 0, high = (int)arr.size() - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (arr[mid] == x) return mid;
                if (arr[low] <= arr[mid]) {              // left half [low..mid] is sorted
                    if (arr[low] <= x && x < arr[mid]) high = mid - 1;
                    else low = mid + 1;
                } else {                                 // right half [mid..high] is sorted
                    if (arr[mid] < x && x <= arr[high]) low = mid + 1;
                    else high = mid - 1;
                }
            }
            return -1;
        }

        int main() {
            vector<int> a = {10, 20, 30, 40, 50, 8, 9};
            cout << "x = 30 → " << searchRotated(a, 30) << "\n";
            cout << "x = 8 → " << searchRotated(a, 8) << "\n";
            cout << "x = 40 → " << searchRotated({100, 200, 300, 10, 20}, 40) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int searchRotated(int[] arr, int x) {
                int low = 0, high = arr.length - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (arr[mid] == x) return mid;
                    if (arr[low] <= arr[mid]) {          // left half [low..mid] is sorted
                        if (arr[low] <= x && x < arr[mid]) high = mid - 1;
                        else low = mid + 1;
                    } else {                             // right half [mid..high] is sorted
                        if (arr[mid] < x && x <= arr[high]) low = mid + 1;
                        else high = mid - 1;
                    }
                }
                return -1;
            }

            public static void main(String[] args) {
                int[] a = {10, 20, 30, 40, 50, 8, 9};
                System.out.println("x = 30 → " + searchRotated(a, 30));
                System.out.println("x = 8 → " + searchRotated(a, 8));
                System.out.println("x = 40 → " + searchRotated(new int[]{100, 200, 300, 10, 20}, 40));
            }
        }
    ''', js=r'''
        function searchRotated(arr, x) {
            let low = 0, high = arr.length - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                if (arr[mid] === x) return mid;
                if (arr[low] <= arr[mid]) {              // left half [low..mid] is sorted
                    if (arr[low] <= x && x < arr[mid]) high = mid - 1;
                    else low = mid + 1;
                } else {                                 // right half [mid..high] is sorted
                    if (arr[mid] < x && x <= arr[high]) low = mid + 1;
                    else high = mid - 1;
                }
            }
            return -1;
        }

        const a = [10, 20, 30, 40, 50, 8, 9];
        console.log("x = 30 →", searchRotated(a, 30));
        console.log("x = 8 →", searchRotated(a, 8));
        console.log("x = 40 →", searchRotated([100, 200, 300, 10, 20], 40));
    ''')
    yield complexity("O(log n)", "O(1)")
    yield pitfall("Use `arr[low] <= arr[mid]` (not `<`) so that a two-element window like `[8, 9]` with `mid == low` is classified as “left half sorted”. The original notes used `<`, which sends `x = 8` the wrong way in such windows. With **duplicates** (`[3, 1, 3, 3, 3]`) neither half can be identified and the worst case degrades to `O(n)`.")

    # ── peak element ──────────────────────────────────────────────────
    yield section("Find a peak element", "mountain")
    yield io("arr = [5, 10, 20, 15, 7]", "20", "arr = [10, 20, 15, 5, 23, 90, 67]", "20 (90 is also a valid answer)")
    yield p("A **peak** is an element that is not smaller than its neighbours (the ends only have one neighbour). Every array has at least one peak — the maximum is always one — but we only need *any* peak, which is what makes `O(log n)` possible.")
    yield idea("Look at `mid`. If it is a peak, done. If its **left** neighbour is bigger, the left half must contain a peak: walking left along rising values must eventually stop, either at a local maximum or at index 0 — both are peaks. Symmetrically, if the right neighbour is bigger, go right.")
    yield diagram('''
        10  20  15   5  23  90  67
         0   1   2   3   4   5   6
                     ↑ mid=3: arr[2]=15 > 5 → a peak exists on the left
             ↑ mid=1: 10 ≤ 20 ≥ 15 → peak = 20
    ''', "Binary search follows the rising side; it never needs the global maximum")
    yield snippet("py", r'''
        # Naive: check every element against its neighbours — O(n)
        def get_peak(arr):
            n = len(arr)
            for i in range(n):
                left_ok = i == 0 or arr[i - 1] <= arr[i]
                right_ok = i == n - 1 or arr[i + 1] <= arr[i]
                if left_ok and right_ok:
                    return arr[i]

        print(get_peak([5, 10, 20, 15, 7]))
        print(get_peak([10, 20, 15, 5, 23, 90, 67]))
    ''', out="20\n20")
    yield multi('''
        20
        20
        3
        7
    ''', py=r'''
        def get_peak(arr):
            n = len(arr)
            low, high = 0, n - 1
            while low <= high:
                mid = low + (high - low) // 2
                left_ok = mid == 0 or arr[mid - 1] <= arr[mid]
                right_ok = mid == n - 1 or arr[mid + 1] <= arr[mid]
                if left_ok and right_ok:
                    return arr[mid]                # mid is a peak
                if mid > 0 and arr[mid - 1] > arr[mid]:
                    high = mid - 1                 # rising towards the left → peak there
                else:
                    low = mid + 1                  # rising towards the right
            return -1

        print(get_peak([5, 10, 20, 15, 7]))
        print(get_peak([10, 20, 15, 5, 23, 90, 67]))
        print(get_peak([1, 2, 3]))
        print(get_peak([7]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int getPeak(const vector<int>& arr) {
            int n = arr.size();
            int low = 0, high = n - 1;
            while (low <= high) {
                int mid = low + (high - low) / 2;
                bool leftOk = mid == 0 || arr[mid - 1] <= arr[mid];
                bool rightOk = mid == n - 1 || arr[mid + 1] <= arr[mid];
                if (leftOk && rightOk) return arr[mid];          // mid is a peak
                if (mid > 0 && arr[mid - 1] > arr[mid]) high = mid - 1;   // rising to the left
                else low = mid + 1;                                       // rising to the right
            }
            return -1;
        }

        int main() {
            cout << getPeak({5, 10, 20, 15, 7}) << "\n";
            cout << getPeak({10, 20, 15, 5, 23, 90, 67}) << "\n";
            cout << getPeak({1, 2, 3}) << "\n";
            cout << getPeak({7}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int getPeak(int[] arr) {
                int n = arr.length;
                int low = 0, high = n - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    boolean leftOk = mid == 0 || arr[mid - 1] <= arr[mid];
                    boolean rightOk = mid == n - 1 || arr[mid + 1] <= arr[mid];
                    if (leftOk && rightOk) return arr[mid];      // mid is a peak
                    if (mid > 0 && arr[mid - 1] > arr[mid]) high = mid - 1;   // rising to the left
                    else low = mid + 1;                                       // rising to the right
                }
                return -1;
            }

            public static void main(String[] args) {
                System.out.println(getPeak(new int[]{5, 10, 20, 15, 7}));
                System.out.println(getPeak(new int[]{10, 20, 15, 5, 23, 90, 67}));
                System.out.println(getPeak(new int[]{1, 2, 3}));
                System.out.println(getPeak(new int[]{7}));
            }
        }
    ''', js=r'''
        function getPeak(arr) {
            const n = arr.length;
            let low = 0, high = n - 1;
            while (low <= high) {
                const mid = low + Math.floor((high - low) / 2);
                const leftOk = mid === 0 || arr[mid - 1] <= arr[mid];
                const rightOk = mid === n - 1 || arr[mid + 1] <= arr[mid];
                if (leftOk && rightOk) return arr[mid];          // mid is a peak
                if (mid > 0 && arr[mid - 1] > arr[mid]) high = mid - 1;   // rising to the left
                else low = mid + 1;                                       // rising to the right
            }
            return -1;
        }

        console.log(getPeak([5, 10, 20, 15, 7]));
        console.log(getPeak([10, 20, 15, 5, 23, 90, 67]));
        console.log(getPeak([1, 2, 3]));
        console.log(getPeak([7]));
    ''')
    yield complexity("O(log n)", "O(1)")
    yield note("The array is **not sorted** here — binary search works because the predicate “a peak exists in this half” can be decided from `mid` and one neighbour. The same reasoning finds the maximum of a *bitonic* array (strictly increasing then strictly decreasing).")

    # ── two pointers: pair sum ────────────────────────────────────────
    yield section("Two-pointer approach: pair with a given sum", "arrows-left-right")
    yield io("arr = [2, 5, 8, 12, 30], x = 17", "true", "arr = [3, 8, 13, 18], x = 14", "false")
    yield p("Given a **sorted** array, is there a pair whose sum is `x`? The brute force tries all `n(n-1)/2` pairs.")
    yield snippet("py", r'''
        # Naive: every pair — O(n²)
        def has_pair(arr, x):
            n = len(arr)
            for i in range(n - 1):
                for j in range(i + 1, n):
                    if arr[i] + arr[j] == x:
                        return True
            return False

        print("true" if has_pair([2, 5, 8, 12, 30], 17) else "false")
        print("true" if has_pair([3, 8, 13, 18], 14) else "false")
    ''', out="true\nfalse")
    yield idea("Put `i` at the start and `j` at the end. If `arr[i] + arr[j] < x` the sum must grow — only moving `i` right can do that (every pair with this `i` and a smaller `j` is even smaller, so `i` is finished). If the sum is too large, move `j` left. Each step retires one index, so at most `n` steps.")
    yield multi('''
        [2, 5, 8, 12, 30] x=17 → true
        [3, 8, 13, 18] x=14 → false
    ''', py=r'''
        def has_pair(arr, x):
            i, j = 0, len(arr) - 1
            while i < j:
                s = arr[i] + arr[j]
                if s == x:
                    return True
                if s < x:
                    i += 1          # need a bigger sum
                else:
                    j -= 1          # need a smaller sum
            return False

        print("[2, 5, 8, 12, 30] x=17 →", "true" if has_pair([2, 5, 8, 12, 30], 17) else "false")
        print("[3, 8, 13, 18] x=14 →", "true" if has_pair([3, 8, 13, 18], 14) else "false")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool hasPair(const vector<int>& arr, int x) {
            int i = 0, j = (int)arr.size() - 1;
            while (i < j) {
                int s = arr[i] + arr[j];
                if (s == x) return true;
                if (s < x) i++;       // need a bigger sum
                else j--;             // need a smaller sum
            }
            return false;
        }

        int main() {
            cout << "[2, 5, 8, 12, 30] x=17 → " << (hasPair({2, 5, 8, 12, 30}, 17) ? "true" : "false") << "\n";
            cout << "[3, 8, 13, 18] x=14 → " << (hasPair({3, 8, 13, 18}, 14) ? "true" : "false") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean hasPair(int[] arr, int x) {
                int i = 0, j = arr.length - 1;
                while (i < j) {
                    int s = arr[i] + arr[j];
                    if (s == x) return true;
                    if (s < x) i++;   // need a bigger sum
                    else j--;         // need a smaller sum
                }
                return false;
            }

            public static void main(String[] args) {
                System.out.println("[2, 5, 8, 12, 30] x=17 → " + hasPair(new int[]{2, 5, 8, 12, 30}, 17));
                System.out.println("[3, 8, 13, 18] x=14 → " + hasPair(new int[]{3, 8, 13, 18}, 14));
            }
        }
    ''', js=r'''
        function hasPair(arr, x) {
            let i = 0, j = arr.length - 1;
            while (i < j) {
                const s = arr[i] + arr[j];
                if (s === x) return true;
                if (s < x) i++;       // need a bigger sum
                else j--;             // need a smaller sum
            }
            return false;
        }

        console.log("[2, 5, 8, 12, 30] x=17 →", hasPair([2, 5, 8, 12, 30], 17));
        console.log("[3, 8, 13, 18] x=14 →", hasPair([3, 8, 13, 18], 14));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("If the array is **not** sorted, two pointers need an `O(n log n)` sort first; a hash set gives `O(n)` time with `O(n)` space instead (see Hashing). Two pointers win when the input is already sorted or when `O(1)` extra space is required.")

    # ── triplet ───────────────────────────────────────────────────────
    yield section("Triplet in a sorted array", "hierarchy-3")
    yield io("arr = [2, 3, 4, 8, 9, 20, 40], x = 32", "true", "arr = [1, 2, 5, 6], x = 14", "false")
    yield idea("Fix the smallest element `arr[i]` of the triplet, then ask the two-pointer routine for a **pair with sum `x - arr[i]`** in the suffix `arr[i+1..]`. Searching only to the right avoids reusing `arr[i]` and avoids counting the same triplet three times. `n` fixes × `O(n)` pair search = `O(n²)`, down from the `O(n³)` triple loop.")
    yield multi('''
        [2, 3, 4, 8, 9, 20, 40] x=32 → true
        [1, 2, 5, 6] x=14 → false
    ''', py=r'''
        def has_pair_from(arr, start, x):
            i, j = start, len(arr) - 1
            while i < j:
                s = arr[i] + arr[j]
                if s == x:
                    return True
                if s < x:
                    i += 1
                else:
                    j -= 1
            return False

        def has_triplet(arr, x):
            for i in range(len(arr) - 2):              # fix the smallest element
                if has_pair_from(arr, i + 1, x - arr[i]):
                    return True
            return False

        print("[2, 3, 4, 8, 9, 20, 40] x=32 →", "true" if has_triplet([2, 3, 4, 8, 9, 20, 40], 32) else "false")
        print("[1, 2, 5, 6] x=14 →", "true" if has_triplet([1, 2, 5, 6], 14) else "false")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool hasPairFrom(const vector<int>& arr, int start, int x) {
            int i = start, j = (int)arr.size() - 1;
            while (i < j) {
                int s = arr[i] + arr[j];
                if (s == x) return true;
                if (s < x) i++; else j--;
            }
            return false;
        }

        bool hasTriplet(const vector<int>& arr, int x) {
            int n = arr.size();
            for (int i = 0; i < n - 2; i++)                 // fix the smallest element
                if (hasPairFrom(arr, i + 1, x - arr[i])) return true;
            return false;
        }

        int main() {
            cout << "[2, 3, 4, 8, 9, 20, 40] x=32 → " << (hasTriplet({2, 3, 4, 8, 9, 20, 40}, 32) ? "true" : "false") << "\n";
            cout << "[1, 2, 5, 6] x=14 → " << (hasTriplet({1, 2, 5, 6}, 14) ? "true" : "false") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean hasPairFrom(int[] arr, int start, int x) {
                int i = start, j = arr.length - 1;
                while (i < j) {
                    int s = arr[i] + arr[j];
                    if (s == x) return true;
                    if (s < x) i++; else j--;
                }
                return false;
            }

            static boolean hasTriplet(int[] arr, int x) {
                for (int i = 0; i < arr.length - 2; i++)    // fix the smallest element
                    if (hasPairFrom(arr, i + 1, x - arr[i])) return true;
                return false;
            }

            public static void main(String[] args) {
                System.out.println("[2, 3, 4, 8, 9, 20, 40] x=32 → " + hasTriplet(new int[]{2, 3, 4, 8, 9, 20, 40}, 32));
                System.out.println("[1, 2, 5, 6] x=14 → " + hasTriplet(new int[]{1, 2, 5, 6}, 14));
            }
        }
    ''', js=r'''
        function hasPairFrom(arr, start, x) {
            let i = start, j = arr.length - 1;
            while (i < j) {
                const s = arr[i] + arr[j];
                if (s === x) return true;
                if (s < x) i++; else j--;
            }
            return false;
        }

        function hasTriplet(arr, x) {
            for (let i = 0; i < arr.length - 2; i++)         // fix the smallest element
                if (hasPairFrom(arr, i + 1, x - arr[i])) return true;
            return false;
        }

        console.log("[2, 3, 4, 8, 9, 20, 40] x=32 →", hasTriplet([2, 3, 4, 8, 9, 20, 40], 32));
        console.log("[1, 2, 5, 6] x=14 →", hasTriplet([1, 2, 5, 6], 14));
    ''')
    yield complexity("O(n²)", "O(1)")
    yield note("This is the standard **3-Sum** technique. To *list* all distinct triplets instead of answering yes/no, skip over equal values after each move of `i`, `j` and the fixed index so duplicates are not reported twice.")

    # ── median of two sorted arrays ───────────────────────────────────
    yield section("Median of two sorted arrays", "divide")
    yield io("a1 = [10, 20, 30, 40, 50], a2 = [5, 15, 25, 35, 45]", "27.5", "a1 = [1, 2, 3], a2 = [4, 5, 6]", "3.5", "a1 = [1, 3, 5], a2 = [2, 4, 6, 8, 10]", "4.5")
    yield p("The median of the merged array is wanted, **without merging**. Merging takes `O(n1 + n2)` time and space; the target is `O(log min(n1, n2))`.")
    yield snippet("py", r'''
        # Naive: merge (like merge sort's merge step), then pick the middle — O(n1 + n2)
        def median_by_merge(a1, a2):
            merged, i, j = [], 0, 0
            while i < len(a1) and j < len(a2):
                if a1[i] <= a2[j]:
                    merged.append(a1[i]); i += 1
                else:
                    merged.append(a2[j]); j += 1
            merged += a1[i:] + a2[j:]
            n = len(merged)
            if n % 2 == 1:
                return merged[n // 2]
            return (merged[n // 2 - 1] + merged[n // 2]) / 2

        print(median_by_merge([10, 20, 30, 40, 50], [5, 15, 25, 35, 45]))
        print(median_by_merge([1, 3, 5], [2, 4, 6, 8, 10]))
    ''', out="27.5\n4.5")
    yield idea("The median splits the `n1 + n2` elements into a **left half** and a **right half** of (almost) equal size. Take `i1` elements from `a1` and `i2 = (n1 + n2 + 1) / 2 - i1` from `a2` to form the left half. The split is correct exactly when every left element is `<=` every right element: `maxLeft1 <= minRight2` and `maxLeft2 <= minRight1`. If `maxLeft1 > minRight2`, `i1` is too big — binary search `i1` over `[0, n1]`.")
    yield diagram('''
        a1 = 10 20 | 30 40 50       i1 = 2  →  maxLeft1 = 20, minRight1 = 30
        a2 =  5 15 25 | 35 45       i2 = 3  →  maxLeft2 = 25, minRight2 = 35

        left half  = {10, 20, 5, 15, 25}   max = 25
        right half = {30, 40, 50, 35, 45}  min = 30
        20 ≤ 35 and 25 ≤ 30 ✓  →  median = (25 + 30) / 2 = 27.5
    ''', "A valid partition: five elements on the left, five on the right")
    yield steps(
        ("Make `a1` the shorter array", "Swap if needed, so the search space is `[0, n1]` with `n1 = min`, and `i2` always stays within `[0, n2]`."),
        ("Binary search `i1`", "`i1 = (low + high) / 2`, `i2 = (n1 + n2 + 1) / 2 - i1`. Use `-∞` / `+∞` when a side of a split is empty."),
        ("Check the partition", "`maxLeft1 <= minRight2` and `maxLeft2 <= minRight1` → found. If `maxLeft1 > minRight2` move `high = i1 - 1`, else `low = i1 + 1`."),
        ("Read the median", "Odd total: `max(maxLeft1, maxLeft2)`. Even total: average of that and `min(minRight1, minRight2)`."),
    )
    yield p("To keep the four programs' output byte-identical the code computes **twice the median** as an integer (the sum of the two middle values) and prints it as `k.0` or `k.5` — the median of integers is always a whole or half number.")
    yield multi('''
        27.5
        3.5
        4.5
        2.0
    ''', py=r'''
        INF = float("inf")

        def median_x2(a1, a2):
            if len(a1) > len(a2):
                a1, a2 = a2, a1                     # binary search over the shorter array
            n1, n2 = len(a1), len(a2)
            low, high = 0, n1
            while low <= high:
                i1 = (low + high) // 2
                i2 = (n1 + n2 + 1) // 2 - i1
                max_l1 = -INF if i1 == 0 else a1[i1 - 1]
                min_r1 = INF if i1 == n1 else a1[i1]
                max_l2 = -INF if i2 == 0 else a2[i2 - 1]
                min_r2 = INF if i2 == n2 else a2[i2]
                if max_l1 <= min_r2 and max_l2 <= min_r1:       # valid partition
                    if (n1 + n2) % 2 == 1:
                        return 2 * max(max_l1, max_l2)
                    return max(max_l1, max_l2) + min(min_r1, min_r2)
                if max_l1 > min_r2:
                    high = i1 - 1                    # took too many from a1
                else:
                    low = i1 + 1                     # took too few from a1
            return 0

        def show(a1, a2):
            m2 = int(median_x2(a1, a2))
            print(f"{m2 // 2}.{'5' if m2 % 2 else '0'}")

        show([10, 20, 30, 40, 50], [5, 15, 25, 35, 45])
        show([1, 2, 3], [4, 5, 6])
        show([1, 3, 5], [2, 4, 6, 8, 10])
        show([1, 2], [3])
    ''', cpp=r'''
        #include <algorithm>
        #include <climits>
        #include <iostream>
        #include <vector>
        using namespace std;

        int medianX2(vector<int> a1, vector<int> a2) {
            if (a1.size() > a2.size()) swap(a1, a2);        // binary search over the shorter array
            int n1 = a1.size(), n2 = a2.size();
            int low = 0, high = n1;
            while (low <= high) {
                int i1 = (low + high) / 2;
                int i2 = (n1 + n2 + 1) / 2 - i1;
                int maxL1 = i1 == 0 ? INT_MIN : a1[i1 - 1];
                int minR1 = i1 == n1 ? INT_MAX : a1[i1];
                int maxL2 = i2 == 0 ? INT_MIN : a2[i2 - 1];
                int minR2 = i2 == n2 ? INT_MAX : a2[i2];
                if (maxL1 <= minR2 && maxL2 <= minR1) {        // valid partition
                    if ((n1 + n2) % 2 == 1) return 2 * max(maxL1, maxL2);
                    return max(maxL1, maxL2) + min(minR1, minR2);
                }
                if (maxL1 > minR2) high = i1 - 1;              // took too many from a1
                else low = i1 + 1;                             // took too few from a1
            }
            return 0;
        }

        void show(const vector<int>& a1, const vector<int>& a2) {
            int m2 = medianX2(a1, a2);
            cout << m2 / 2 << "." << (m2 % 2 ? "5" : "0") << "\n";
        }

        int main() {
            show({10, 20, 30, 40, 50}, {5, 15, 25, 35, 45});
            show({1, 2, 3}, {4, 5, 6});
            show({1, 3, 5}, {2, 4, 6, 8, 10});
            show({1, 2}, {3});
        }
    ''', java=r'''
        public class Main {
            static int medianX2(int[] a1, int[] a2) {
                if (a1.length > a2.length) { int[] t = a1; a1 = a2; a2 = t; }   // search the shorter array
                int n1 = a1.length, n2 = a2.length;
                int low = 0, high = n1;
                while (low <= high) {
                    int i1 = (low + high) / 2;
                    int i2 = (n1 + n2 + 1) / 2 - i1;
                    int maxL1 = i1 == 0 ? Integer.MIN_VALUE : a1[i1 - 1];
                    int minR1 = i1 == n1 ? Integer.MAX_VALUE : a1[i1];
                    int maxL2 = i2 == 0 ? Integer.MIN_VALUE : a2[i2 - 1];
                    int minR2 = i2 == n2 ? Integer.MAX_VALUE : a2[i2];
                    if (maxL1 <= minR2 && maxL2 <= minR1) {    // valid partition
                        if ((n1 + n2) % 2 == 1) return 2 * Math.max(maxL1, maxL2);
                        return Math.max(maxL1, maxL2) + Math.min(minR1, minR2);
                    }
                    if (maxL1 > minR2) high = i1 - 1;          // took too many from a1
                    else low = i1 + 1;                         // took too few from a1
                }
                return 0;
            }

            static void show(int[] a1, int[] a2) {
                int m2 = medianX2(a1, a2);
                System.out.println(m2 / 2 + "." + (m2 % 2 == 1 ? "5" : "0"));
            }

            public static void main(String[] args) {
                show(new int[]{10, 20, 30, 40, 50}, new int[]{5, 15, 25, 35, 45});
                show(new int[]{1, 2, 3}, new int[]{4, 5, 6});
                show(new int[]{1, 3, 5}, new int[]{2, 4, 6, 8, 10});
                show(new int[]{1, 2}, new int[]{3});
            }
        }
    ''', js=r'''
        function medianX2(a1, a2) {
            if (a1.length > a2.length) [a1, a2] = [a2, a1];   // binary search over the shorter array
            const n1 = a1.length, n2 = a2.length;
            let low = 0, high = n1;
            while (low <= high) {
                const i1 = Math.floor((low + high) / 2);
                const i2 = Math.floor((n1 + n2 + 1) / 2) - i1;
                const maxL1 = i1 === 0 ? -Infinity : a1[i1 - 1];
                const minR1 = i1 === n1 ? Infinity : a1[i1];
                const maxL2 = i2 === 0 ? -Infinity : a2[i2 - 1];
                const minR2 = i2 === n2 ? Infinity : a2[i2];
                if (maxL1 <= minR2 && maxL2 <= minR1) {        // valid partition
                    if ((n1 + n2) % 2 === 1) return 2 * Math.max(maxL1, maxL2);
                    return Math.max(maxL1, maxL2) + Math.min(minR1, minR2);
                }
                if (maxL1 > minR2) high = i1 - 1;              // took too many from a1
                else low = i1 + 1;                             // took too few from a1
            }
            return 0;
        }

        function show(a1, a2) {
            const m2 = medianX2(a1, a2);
            console.log(`${Math.floor(m2 / 2)}.${m2 % 2 ? "5" : "0"}`);
        }

        show([10, 20, 30, 40, 50], [5, 15, 25, 35, 45]);
        show([1, 2, 3], [4, 5, 6]);
        show([1, 3, 5], [2, 4, 6, 8, 10]);
        show([1, 2], [3]);
    ''')
    yield complexity("O(log min(n1, n2))", "O(1)")
    yield pitfall("Three bugs in the original notes, all fixed above: `maxLeft1` for an empty left part must be `-∞`, not `+∞`; `a2[i2]` and `a2[i2 - 1]` need the same empty-side guards as `a1`, otherwise `i2 == n2` indexes out of range; and the solution assumed `len(a1) <= len(a2)` without enforcing it. Also the notes' answer for `[1, 3, 5]` and `[2, 4, 6, 8, 10]` was `4.0` — the merged array is `1 2 3 4 5 6 8 10`, so the median is `4.5`.")

    # ── repeating element ─────────────────────────────────────────────
    yield section("Repeating element", "copy")
    yield p("Constraints that make this problem interesting:")
    yield ul(
        "array size `n >= 2`",
        "**exactly one** value repeats — any number of times",
        "all values from `0` to `max(arr)` are present, so `0 <= max(arr) <= n - 2`",
    )
    yield io("arr = [0, 2, 1, 3, 2, 2]", "2", "arr = [1, 3, 2, 4, 3, 3]", "3")
    yield table(
        ["Approach", "Time", "Extra space", "Modifies array?"],
        ["Compare every pair", "`O(n²)`", "`O(1)`", "no"],
        ["Sort, then compare neighbours", "`O(n log n)`", "`O(1)`", "**yes**"],
        ["Hash set of seen values", "`O(n)`", "`O(n)`", "no"],
        ["Boolean `visited` array (values are `< n`)", "`O(n)`", "`O(n)`", "no"],
        ["Floyd's cycle detection on `i → arr[i]`", "`O(n)`", "`O(1)`", "no"],
    )
    yield snippet("py", r'''
        # Sort-based: O(n log n), but the array is reordered
        def repeating_by_sort(arr):
            arr = sorted(arr)
            for i in range(len(arr) - 1):
                if arr[i] == arr[i + 1]:
                    return arr[i]
            return -1

        # Set-based: O(n) time but O(n) extra space
        def repeating_by_set(arr):
            seen = set()
            for x in arr:
                if x in seen:
                    return x
                seen.add(x)
            return -1

        print(repeating_by_sort([0, 2, 1, 3, 2, 2]), repeating_by_set([0, 2, 1, 3, 2, 2]))
        print(repeating_by_sort([1, 3, 2, 4, 3, 3]), repeating_by_set([1, 3, 2, 4, 3, 3]))
    ''', out="2 2\n3 3")
    yield p("Because every value is smaller than `n`, a boolean array indexed by value replaces the hash set — same `O(n)` time, less constant overhead, no hashing.")
    yield multi('''
        2
        3
    ''', py=r'''
        def repeating(arr):
            visited = [False] * len(arr)       # values lie in 0..n-2, so index by value
            for x in arr:
                if visited[x]:
                    return x
                visited[x] = True
            return -1

        print(repeating([0, 2, 1, 3, 2, 2]))
        print(repeating([1, 3, 2, 4, 3, 3]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int repeating(const vector<int>& arr) {
            vector<bool> visited(arr.size(), false);   // values lie in 0..n-2, so index by value
            for (int x : arr) {
                if (visited[x]) return x;
                visited[x] = true;
            }
            return -1;
        }

        int main() {
            cout << repeating({0, 2, 1, 3, 2, 2}) << "\n";
            cout << repeating({1, 3, 2, 4, 3, 3}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int repeating(int[] arr) {
                boolean[] visited = new boolean[arr.length];  // values lie in 0..n-2, so index by value
                for (int x : arr) {
                    if (visited[x]) return x;
                    visited[x] = true;
                }
                return -1;
            }

            public static void main(String[] args) {
                System.out.println(repeating(new int[]{0, 2, 1, 3, 2, 2}));
                System.out.println(repeating(new int[]{1, 3, 2, 4, 3, 3}));
            }
        }
    ''', js=r'''
        function repeating(arr) {
            const visited = new Array(arr.length).fill(false);   // values lie in 0..n-2, so index by value
            for (const x of arr) {
                if (visited[x]) return x;
                visited[x] = true;
            }
            return -1;
        }

        console.log(repeating([0, 2, 1, 3, 2, 2]));
        console.log(repeating([1, 3, 2, 4, 3, 3]));
    ''')
    yield complexity("O(n)", "O(n)")

    yield section("Repeating element in O(n) time, O(1) space, array unchanged", "repeat")
    yield io("arr = [0, 2, 1, 3, 2, 2]", "2", "arr = [1, 3, 2, 4, 3, 3]", "3", "arr = [0, 0]", "0")
    yield p("Now the array may not be modified and no extra array is allowed. The trick is to stop looking at the values as *data* and treat them as *pointers*.")
    yield idea("Define `next(i) = arr[i] + 1`. Index `0` is never anybody's `next` (values are `>= 0`, so `next >= 1`), and every index has exactly one outgoing edge — the structure is a **linked list that ends in a cycle** (a ρ shape), starting at `0`. The repeated value is the node with two incoming edges, which is precisely where the cycle begins. Floyd's tortoise-and-hare finds that node in `O(n)` with two integer variables; subtract the `+1` to recover the value.")
    yield diagram('''
        arr = [0, 2, 1, 3, 2, 2]        next(i) = arr[i] + 1

        0 → 1 → 3 → 4 → 3 → 4 → …        4 and 5 both point to 3
                    ↑___|                 (arr[4] = arr[5] = 2)
                5 ──┘
        cycle starts at node 3  →  value = 3 - 1 = 2
    ''', "Indices as a functional graph: the cycle entry has two in-edges, i.e. the repeated value")
    yield steps(
        ("Phase 1 — meet inside the cycle", "`slow = next(slow)`, `fast = next(next(fast))` from `0` until they are equal. They must meet because once both are on the cycle the gap shrinks by one every step."),
        ("Phase 2 — find the entry", "Reset `slow = 0`; move both one step at a time. They meet exactly at the cycle entry (the distance from `0` to the entry equals the distance from the meeting point to the entry, modulo the cycle length)."),
        ("Recover the value", "The entry index is `v + 1` for the repeated value `v`, so return `entry - 1`."),
    )
    yield multi('''
        2
        3
        0
    ''', py=r'''
        def repeating(arr):
            nxt = lambda i: arr[i] + 1          # +1 so that index 0 is never a target
            slow = fast = 0
            while True:                         # phase 1: meet somewhere on the cycle
                slow = nxt(slow)
                fast = nxt(nxt(fast))
                if slow == fast:
                    break
            slow = 0                            # phase 2: walk to the cycle entry
            while slow != fast:
                slow = nxt(slow)
                fast = nxt(fast)
            return slow - 1

        print(repeating([0, 2, 1, 3, 2, 2]))
        print(repeating([1, 3, 2, 4, 3, 3]))
        print(repeating([0, 0]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int repeating(const vector<int>& arr) {
            auto next = [&](int i) { return arr[i] + 1; };   // +1 so that index 0 is never a target
            int slow = 0, fast = 0;
            do {                                             // phase 1: meet somewhere on the cycle
                slow = next(slow);
                fast = next(next(fast));
            } while (slow != fast);
            slow = 0;                                        // phase 2: walk to the cycle entry
            while (slow != fast) {
                slow = next(slow);
                fast = next(fast);
            }
            return slow - 1;
        }

        int main() {
            cout << repeating({0, 2, 1, 3, 2, 2}) << "\n";
            cout << repeating({1, 3, 2, 4, 3, 3}) << "\n";
            cout << repeating({0, 0}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int repeating(int[] arr) {
                int slow = 0, fast = 0;
                do {                                         // phase 1: meet somewhere on the cycle
                    slow = arr[slow] + 1;                    // +1 so that index 0 is never a target
                    fast = arr[arr[fast] + 1] + 1;
                } while (slow != fast);
                slow = 0;                                    // phase 2: walk to the cycle entry
                while (slow != fast) {
                    slow = arr[slow] + 1;
                    fast = arr[fast] + 1;
                }
                return slow - 1;
            }

            public static void main(String[] args) {
                System.out.println(repeating(new int[]{0, 2, 1, 3, 2, 2}));
                System.out.println(repeating(new int[]{1, 3, 2, 4, 3, 3}));
                System.out.println(repeating(new int[]{0, 0}));
            }
        }
    ''', js=r'''
        function repeating(arr) {
            const next = (i) => arr[i] + 1;     // +1 so that index 0 is never a target
            let slow = 0, fast = 0;
            do {                                // phase 1: meet somewhere on the cycle
                slow = next(slow);
                fast = next(next(fast));
            } while (slow !== fast);
            slow = 0;                           // phase 2: walk to the cycle entry
            while (slow !== fast) {
                slow = next(slow);
                fast = next(fast);
            }
            return slow - 1;
        }

        console.log(repeating([0, 2, 1, 3, 2, 2]));
        console.log(repeating([1, 3, 2, 4, 3, 3]));
        console.log(repeating([0, 0]));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("The `+1` shift matters. Without it, `arr[0] == 0` makes index `0` point to itself and the “start” is already inside a cycle, so Floyd's phase 2 returns the wrong node. The popular variant *Find the Duplicate Number* (`n + 1` values in `1..n`) needs no shift because its values are already `>= 1` — use `next(i) = arr[i]` and return the entry itself. The notes' example `[1, 1]` belongs to that variant (it violates `max(arr) <= n - 2`), so it was replaced by `[0, 0]`.")

    # ── allocate minimum pages ────────────────────────────────────────
    yield section("Allocate minimum number of pages", "book")
    yield io("pages = [10, 20, 30, 40], k = 2", "60", "pages = [10, 20, 30], k = 1", "60", "pages = [10, 20, 30, 40], k = 3", "40")
    yield p("`n` books with `pages[i]` pages must be split among `k` students. Each student gets a **contiguous** run of books and every book goes to someone. Minimise the maximum number of pages any one student reads. For `[10, 20, 30, 40]` and `k = 2` the best split is `[10, 20, 30] | [40]` → `max(60, 40) = 60`.")
    yield snippet("py", r'''
        # Naive: try every position for the last cut, recursively — exponential
        def min_pages(pages, n, k):
            if k == 1:
                return sum(pages[:n])          # one student takes all remaining books
            if n == 1:
                return pages[0]
            best = float("inf")
            for i in range(1, n):              # last student gets pages[i..n-1]
                best = min(best, max(min_pages(pages, i, k - 1), sum(pages[i:n])))
            return best

        print(min_pages([10, 20, 30, 40], 4, 2))
        print(min_pages([10, 20, 30], 3, 1))
    ''', out="60\n60")
    yield p("The recursion explores `C(n-1, k-1)` ways of placing cuts. Memoising it gives an `O(n² k)` dynamic programme — still slow. The breakthrough is to search over the **answer** instead of over the cuts.")
    yield idea("Ask the inverse question: *“can every student stay within `cap` pages?”* Greedily fill students left to right; start a new student whenever adding the next book would exceed `cap`. If at most `k` students were needed, `cap` is feasible. Feasibility is **monotone** — a larger cap is never harder — so binary search the smallest feasible cap between `max(pages)` (one book must fit) and `sum(pages)` (one student takes all).")
    yield steps(
        ("Bounds", "`low = max(pages)`, `high = sum(pages)`. The answer is always in this range."),
        ("Probe", "`mid = (low + high) / 2`. Run the greedy `isFeasible(mid)` in `O(n)`."),
        ("Shrink", "Feasible → record `mid`, try smaller (`high = mid - 1`). Not feasible → `low = mid + 1`."),
    )
    yield multi('''
        60
        60
        40
    ''', py=r'''
        def is_feasible(pages, k, cap):
            students, current = 1, 0
            for pg in pages:
                if pg > cap:
                    return False
                if current + pg > cap:          # this book starts a new student's share
                    students += 1
                    current = pg
                else:
                    current += pg
            return students <= k

        def min_pages(pages, k):
            low, high = max(pages), sum(pages)
            result = high
            while low <= high:                  # binary search on the answer
                mid = low + (high - low) // 2
                if is_feasible(pages, k, mid):
                    result = mid
                    high = mid - 1              # try an even smaller cap
                else:
                    low = mid + 1
            return result

        print(min_pages([10, 20, 30, 40], 2))
        print(min_pages([10, 20, 30], 1))
        print(min_pages([10, 20, 30, 40], 3))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <numeric>
        #include <vector>
        using namespace std;

        bool isFeasible(const vector<int>& pages, int k, int cap) {
            int students = 1, current = 0;
            for (int pg : pages) {
                if (pg > cap) return false;
                if (current + pg > cap) {       // this book starts a new student's share
                    students++;
                    current = pg;
                } else {
                    current += pg;
                }
            }
            return students <= k;
        }

        int minPages(const vector<int>& pages, int k) {
            int low = *max_element(pages.begin(), pages.end());
            int high = accumulate(pages.begin(), pages.end(), 0);
            int result = high;
            while (low <= high) {               // binary search on the answer
                int mid = low + (high - low) / 2;
                if (isFeasible(pages, k, mid)) { result = mid; high = mid - 1; }   // try smaller
                else low = mid + 1;
            }
            return result;
        }

        int main() {
            cout << minPages({10, 20, 30, 40}, 2) << "\n";
            cout << minPages({10, 20, 30}, 1) << "\n";
            cout << minPages({10, 20, 30, 40}, 3) << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isFeasible(int[] pages, int k, int cap) {
                int students = 1, current = 0;
                for (int pg : pages) {
                    if (pg > cap) return false;
                    if (current + pg > cap) {   // this book starts a new student's share
                        students++;
                        current = pg;
                    } else {
                        current += pg;
                    }
                }
                return students <= k;
            }

            static int minPages(int[] pages, int k) {
                int low = 0, high = 0;
                for (int pg : pages) { low = Math.max(low, pg); high += pg; }
                int result = high;
                while (low <= high) {           // binary search on the answer
                    int mid = low + (high - low) / 2;
                    if (isFeasible(pages, k, mid)) { result = mid; high = mid - 1; }   // try smaller
                    else low = mid + 1;
                }
                return result;
            }

            public static void main(String[] args) {
                System.out.println(minPages(new int[]{10, 20, 30, 40}, 2));
                System.out.println(minPages(new int[]{10, 20, 30}, 1));
                System.out.println(minPages(new int[]{10, 20, 30, 40}, 3));
            }
        }
    ''', js=r'''
        function isFeasible(pages, k, cap) {
            let students = 1, current = 0;
            for (const pg of pages) {
                if (pg > cap) return false;
                if (current + pg > cap) {       // this book starts a new student's share
                    students++;
                    current = pg;
                } else {
                    current += pg;
                }
            }
            return students <= k;
        }

        function minPages(pages, k) {
            let low = Math.max(...pages), high = pages.reduce((a, b) => a + b, 0);
            let result = high;
            while (low <= high) {               // binary search on the answer
                const mid = low + Math.floor((high - low) / 2);
                if (isFeasible(pages, k, mid)) { result = mid; high = mid - 1; }   // try smaller
                else low = mid + 1;
            }
            return result;
        }

        console.log(minPages([10, 20, 30, 40], 2));
        console.log(minPages([10, 20, 30], 1));
        console.log(minPages([10, 20, 30, 40], 3));
    ''')
    yield complexity("O(n log S), S = sum of pages", "O(1)")
    yield note("**Binary search on the answer** is a template worth memorising: *Split Array Largest Sum*, *Painter's Partition*, *Koko Eating Bananas*, *Capacity to Ship Packages*, *Aggressive Cows* and *Minimum Days to Make Bouquets* are all “smallest (or largest) value for which a greedy `O(n)` check passes”. The two things to get right are the bounds and the direction of monotonicity.")
    yield pitfall("The notes' `isFeasible` read `n` from a global variable and the naive solution summed slices inside the loop (`O(n)` per cut). Also note `k > n` is impossible to satisfy if every student must receive a book — decide and document that edge case before coding.")

    # ── Q&A ───────────────────────────────────────────────────────────
    yield section("Interview Q&A", "message-question")
    yield qa("When can binary search be applied to an unsorted array?",
             "Whenever there is a predicate over positions that is `false … false true … true` (monotone), or a way to tell from `O(1)` local information which half must contain an answer. Peak finding (compare `mid` with a neighbour) and rotated-array search (one half is always sorted) are both examples; the array itself is not sorted.")
    yield qa("What does “binary search on the answer” mean and when does it apply?",
             "Instead of searching the input, search the range of possible answers. It applies when (1) the answer is a number in a known range, (2) you can check in polynomial time whether a candidate works, and (3) feasibility is monotone — if `x` works, every larger (or every smaller) value works too. Minimum pages, Koko bananas and painter's partition fit this mould; each check is a greedy `O(n)` pass.")
    yield qa("Why does `low + (high - low) / 2` matter in C++ and Java?",
             "`(low + high)` can overflow a 32-bit `int` when both are near `2³¹ - 1`, yielding a negative `mid` and an out-of-bounds read. `low + (high - low) / 2` never exceeds `high`. Python and JavaScript are not affected (arbitrary-precision ints / 64-bit doubles), but write it the same way for habit.")
    yield qa("How does the two-pointer method guarantee it does not skip the answer?",
             "When `arr[i] + arr[j] < x`, every pair `(i, j')` with `j' < j` has an even smaller sum, so index `i` can never be part of a solution — discarding it is safe. The symmetric argument applies when the sum is too large. Each step permanently retires one index, so the loop terminates after at most `n - 1` steps and never discards a valid pair.")
    yield qa("Explain Floyd's cycle detection and why it finds the repeated element.",
             "Treat each index as a node with one outgoing edge `i → arr[i] + 1`. A node with two incoming edges is a repeated value; with one start node that nobody points to, the path from it enters a cycle exactly at such a node. Phase 1 (slow 1 step, fast 2 steps) meets inside the cycle; phase 2 (reset slow to the start, both 1 step) meets at the cycle entry because the start-to-entry distance equals the meeting-point-to-entry distance modulo the cycle length. Two variables, `O(n)` steps, no writes.")
    yield qa("Median of two sorted arrays — why search the shorter array?",
             "`i1` ranges over `0..n1`; the matching `i2 = (n1 + n2 + 1) / 2 - i1` must stay in `0..n2`. That is guaranteed only when `n1 <= n2`. Searching the shorter array also gives the better `O(log min(n1, n2))` bound and halves the special cases you need to reason about.")


@topic(G, "sorting", "Sorting", "arrows-sort")
def _():
    yield lead("At this level sorting is a **toolbox, not one algorithm**: the shape of the data (binary, three-valued, small range, uniformly distributed, nearly sorted) decides the algorithm, and the partition / merge / counting ideas behind the sorts solve a whole family of problems on their own.")
    yield define("Sorting decision", "choose the algorithm by asking three questions — *how big is `n`, what do the values look like, and what is the cost of memory versus writes versus comparisons?* — then pick the one whose guarantees match. The default (library sort) is right most of the time, but interview problems are built around the exceptions.")

    yield section("Which algorithm for which input", "list-check")
    yield table(
        ["Situation", "Best choice", "Why"],
        ["Binary array (two kinds of values)", "one partition pass (two pointers)", "`O(n)` time, `O(1)` space, no comparison sort needed"],
        ["Array of three values (0/1/2)", "Dutch national flag", "one pass, three regions"],
        ["Size `n`, values in a small range `k`", "counting sort", "`Θ(n + k)`, stable"],
        ["Size `n`, values up to `n²` or `n³`", "radix sort (base `n`)", "`O(d · n)` with `d = 2` or `3` passes"],
        ["Uniformly distributed over a range", "bucket sort", "expected `O(n)` with `k ≈ n` buckets"],
        ["Memory writes are expensive (flash, EEPROM)", "cycle sort", "minimum possible writes: each element written once"],
        ["Only adjacent swaps allowed", "bubble sort", "it is the only one that moves elements one step at a time"],
        ["Small `n` (≈ under 16)", "insertion sort", "tiny constants, adaptive, no recursion"],
        ["Almost sorted input", "insertion sort / Timsort", "`O(n + inversions)`"],
        ["Very little extra memory", "heap sort / in-place quick sort", "`O(1)` or `O(log n)` auxiliary"],
        ["Must be stable, general purpose", "merge sort / Timsort", "`O(n log n)` worst case, stable"],
        ["Linked list", "merge sort", "needs no random access; `O(1)` extra space"],
        ["Data on disk (external sorting)", "merge sort (k-way)", "sequential reads of sorted runs"],
    )
    yield p("The **general-purpose** comparison sorts are merge sort, heap sort and quick sort — all `O(n log n)` on average, each with a different weakness (extra memory, cache behaviour, worst case). Real libraries combine them into **hybrids**:")
    yield cards(
        ("Timsort", "Finds the natural *runs* already present in the data, extends short runs with insertion sort, then merges runs with merge sort using galloping. Stable, `O(n)` on sorted input, `O(n log n)` worst case.", "arrows-shuffle"),
        ("Introsort", "Quick sort that watches its recursion depth; when it exceeds `2 log₂ n` it switches to heap sort (guaranteeing `O(n log n)`), and finishes small partitions with insertion sort. Unstable, in place.", "git-branch"),
        ("Dual-pivot quick sort", "Two pivots split each range into three parts; fewer comparisons and better cache use on random data than one pivot. Java uses it for primitive arrays, where stability does not matter.", "arrows-split"),
        cols=3,
    )
    yield table(
        ["Library call", "Algorithm", "Stable?"],
        ["Python `sorted()`, `list.sort()`", "Timsort (merge policy refined to *powersort* in 3.11+)", "yes"],
        ["Java `Arrays.sort(int[])` (primitives)", "dual-pivot quick sort", "no (irrelevant for primitives)"],
        ["Java `Arrays.sort(Object[])`, `Collections.sort`, `List.sort`", "Timsort", "yes"],
        ["C++ `std::sort`", "introsort", "**no**"],
        ["C++ `std::stable_sort`", "merge sort (buffer) / in-place merge if no memory", "yes"],
        ["C `qsort`", "implementation-defined (glibc: merge sort, falling back to quick sort)", "not guaranteed"],
        ["JavaScript `Array.prototype.sort`", "Timsort in V8 (stable required since ES2019)", "yes"],
    )

    yield section("Stable sort with a custom key in each language", "arrows-sort")
    yield p("A sort is **stable** when equal keys keep their input order. Sorting students by marks: with a stable sort, two students on 70 stay in the order they were entered. This matters for multi-key sorts (sort by name, then stable-sort by department gives “grouped by department, alphabetical inside”).")
    yield multi('''
        Ravi 70
        John 70
        Asha 80
        Meena 80
        Zoe 90
    ''', py=r'''
        students = [("Asha", 80), ("Ravi", 70), ("Meena", 80), ("John", 70), ("Zoe", 90)]
        students.sort(key=lambda s: s[1])            # Timsort: stable, equal marks keep input order
        for name, marks in students:
            print(name, marks)
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Student { string name; int marks; };

        int main() {
            vector<Student> students = {{"Asha", 80}, {"Ravi", 70}, {"Meena", 80}, {"John", 70}, {"Zoe", 90}};
            // std::sort (introsort) is NOT stable — use stable_sort when equal keys must keep their order
            stable_sort(students.begin(), students.end(),
                        [](const Student& a, const Student& b) { return a.marks < b.marks; });
            for (const Student& s : students) cout << s.name << " " << s.marks << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Comparator;
        import java.util.List;

        public class Main {
            record Student(String name, int marks) {}

            public static void main(String[] args) {
                List<Student> students = new ArrayList<>(List.of(
                    new Student("Asha", 80), new Student("Ravi", 70), new Student("Meena", 80),
                    new Student("John", 70), new Student("Zoe", 90)));
                students.sort(Comparator.comparingInt(Student::marks));   // Timsort for objects: stable
                for (Student s : students) System.out.println(s.name() + " " + s.marks());
            }
        }
    ''', js=r'''
        const students = [["Asha", 80], ["Ravi", 70], ["Meena", 80], ["John", 70], ["Zoe", 90]];
        students.sort((a, b) => a[1] - b[1]);        // stable since ES2019 (V8 uses Timsort)
        for (const [name, marks] of students) console.log(name, marks);
    ''')
    yield pitfall("`std::sort` in C++ may reorder equal elements — the Asha/Meena order would be unspecified. Reach for `std::stable_sort` whenever ties matter. In JavaScript, `sort()` without a comparator converts elements to **strings** (`[10, 9, 1].sort()` → `1 10 9`); always pass `(a, b) => a - b` for numbers.")

    # ── tail call elimination in quick sort ───────────────────────────
    yield section("Tail call elimination in quick sort", "stack-3")
    yield p("Textbook quick sort recurses twice. The second call is a **tail call** — nothing happens after it returns — so it can be replaced by a loop that simply updates `low` and continues. That alone saves one frame per level, but the real win comes from choosing *which* side to recurse on.")
    yield snippet("py", r'''
        def partition(arr, low, high):            # Lomuto: pivot = arr[high]
            pivot, i = arr[high], low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def quick_sort(arr, low, high):           # two recursive calls
            if low < high:
                p = partition(arr, low, high)
                quick_sort(arr, low, p - 1)
                quick_sort(arr, p + 1, high)      # tail call: nothing after it

        def quick_sort_tce(arr, low, high):       # tail call replaced by a loop
            while low < high:
                p = partition(arr, low, high)
                quick_sort_tce(arr, low, p - 1)
                low = p + 1                        # "call" on the right part = continue the loop

        a = [10, 80, 30, 90, 40, 50, 70]
        quick_sort_tce(a, 0, len(a) - 1)
        print(*a)
    ''', out="10 30 40 50 70 80 90")
    yield idea("Recurse on the **smaller** partition and loop on the larger one. The recursive call then always handles at most half the elements, so the recursion depth is bounded by `log₂ n` — even on adversarial input where plain quick sort would go `n` deep and overflow the stack. (Time is still `O(n²)` in the worst case; only the *stack* is now safe.)")
    yield pitfall("The notes recursed with `qsort(arr, l, p)` after a Lomuto partition. The pivot is already in its final place at `p`, so the left call must be `(l, p - 1)`; including `p` makes `qsort(l, r)` call itself with the same range when the pivot is the maximum — infinite recursion.")
    yield multi('''
        sorted: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
        max recursion depth: 2
    ''', py=r'''
        depth = max_depth = 0

        def partition(arr, low, high):
            pivot, i = arr[high], low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def quick_sort(arr, low, high):
            global depth, max_depth
            depth += 1
            max_depth = max(max_depth, depth)
            while low < high:
                p = partition(arr, low, high)
                if p - low < high - p:              # recurse into the smaller side ...
                    quick_sort(arr, low, p - 1)
                    low = p + 1                     # ... and loop on the larger one
                else:
                    quick_sort(arr, p + 1, high)
                    high = p - 1
            depth -= 1

        a = list(range(1, 17))                      # already sorted: worst case for arr[high] pivots
        quick_sort(a, 0, len(a) - 1)
        print("sorted:", *a)
        print("max recursion depth:", max_depth)
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        int depth = 0, maxDepth = 0;

        int partition(vector<int>& arr, int low, int high) {
            int pivot = arr[high], i = low - 1;
            for (int j = low; j < high; j++)
                if (arr[j] <= pivot) swap(arr[++i], arr[j]);
            swap(arr[i + 1], arr[high]);
            return i + 1;
        }

        void quickSort(vector<int>& arr, int low, int high) {
            depth++;
            maxDepth = max(maxDepth, depth);
            while (low < high) {
                int p = partition(arr, low, high);
                if (p - low < high - p) {           // recurse into the smaller side ...
                    quickSort(arr, low, p - 1);
                    low = p + 1;                    // ... and loop on the larger one
                } else {
                    quickSort(arr, p + 1, high);
                    high = p - 1;
                }
            }
            depth--;
        }

        int main() {
            vector<int> a(16);
            for (int i = 0; i < 16; i++) a[i] = i + 1;   // already sorted: worst case for arr[high] pivots
            quickSort(a, 0, 15);
            cout << "sorted:";
            for (int x : a) cout << " " << x;
            cout << "\nmax recursion depth: " << maxDepth << "\n";
        }
    ''', java=r'''
        public class Main {
            static int depth = 0, maxDepth = 0;

            static int partition(int[] arr, int low, int high) {
                int pivot = arr[high], i = low - 1;
                for (int j = low; j < high; j++)
                    if (arr[j] <= pivot) { i++; int t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
                int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;
                return i + 1;
            }

            static void quickSort(int[] arr, int low, int high) {
                depth++;
                maxDepth = Math.max(maxDepth, depth);
                while (low < high) {
                    int p = partition(arr, low, high);
                    if (p - low < high - p) {       // recurse into the smaller side ...
                        quickSort(arr, low, p - 1);
                        low = p + 1;                // ... and loop on the larger one
                    } else {
                        quickSort(arr, p + 1, high);
                        high = p - 1;
                    }
                }
                depth--;
            }

            public static void main(String[] args) {
                int[] a = new int[16];
                for (int i = 0; i < 16; i++) a[i] = i + 1;   // already sorted: worst case for arr[high] pivots
                quickSort(a, 0, 15);
                StringBuilder sb = new StringBuilder("sorted:");
                for (int x : a) sb.append(' ').append(x);
                System.out.println(sb);
                System.out.println("max recursion depth: " + maxDepth);
            }
        }
    ''', js=r'''
        let depth = 0, maxDepth = 0;

        function partition(arr, low, high) {
            const pivot = arr[high];
            let i = low - 1;
            for (let j = low; j < high; j++)
                if (arr[j] <= pivot) { i++; [arr[i], arr[j]] = [arr[j], arr[i]]; }
            [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
            return i + 1;
        }

        function quickSort(arr, low, high) {
            depth++;
            maxDepth = Math.max(maxDepth, depth);
            while (low < high) {
                const p = partition(arr, low, high);
                if (p - low < high - p) {           // recurse into the smaller side ...
                    quickSort(arr, low, p - 1);
                    low = p + 1;                    // ... and loop on the larger one
                } else {
                    quickSort(arr, p + 1, high);
                    high = p - 1;
                }
            }
            depth--;
        }

        const a = Array.from({ length: 16 }, (_, i) => i + 1);   // already sorted: worst case for arr[high] pivots
        quickSort(a, 0, 15);
        console.log("sorted:", a.join(" "));
        console.log("max recursion depth:", maxDepth);
    ''')
    yield complexity("O(n log n) average, O(n²) worst", "O(log n) stack — guaranteed")
    yield note("On this already-sorted input every partition is maximally unbalanced (`p == high`), so the naive version would recurse 16 levels deep. The smaller-side rule keeps the depth at 3 — and would keep it under 31 for any array that fits in memory. Combined with a randomised or median-of-three pivot this is what production quick sorts do.")

    # ── kth smallest ──────────────────────────────────────────────────
    yield section("Kth smallest element (quickselect)", "number")
    yield io("arr = [10, 5, 30, 12], k = 2", "10", "arr = [7, 10, 4, 3, 20, 15], k = 3", "7")
    yield snippet("py", r'''
        # Naive: sort everything, then index — O(n log n)
        def kth_smallest(arr, k):
            return sorted(arr)[k - 1]

        print(kth_smallest([10, 5, 30, 12], 2))
        print(kth_smallest([7, 10, 4, 3, 20, 15], 3))
    ''', out="10\n7")
    yield idea("Sorting does more work than needed — we only want position `k - 1`. After one Lomuto partition the pivot sits at its **final sorted index `p`**. If `p == k - 1` we are done; if `p > k - 1` the answer is in the left part, otherwise in the right. Unlike quick sort we recurse into **one** side only, so the expected work is `n + n/2 + n/4 + … = O(n)`.")
    yield multi('''
        2nd smallest of [10, 5, 30, 12] = 10
        3rd smallest of [7, 10, 4, 3, 20, 15] = 7
        4th smallest of [7, 10, 4, 3, 20, 15] = 10
    ''', py=r'''
        def partition(arr, low, high):
            pivot, i = arr[high], low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1

        def kth_smallest(arr, k):
            low, high = 0, len(arr) - 1
            while low <= high:
                p = partition(arr, low, high)   # pivot lands at its final sorted index
                if p == k - 1:
                    return arr[p]
                if p > k - 1:
                    high = p - 1                # answer is on the left
                else:
                    low = p + 1                 # answer is on the right
            return -1

        for arr, k, label in [([10, 5, 30, 12], 2, "2nd"), ([7, 10, 4, 3, 20, 15], 3, "3rd"), ([7, 10, 4, 3, 20, 15], 4, "4th")]:
            print(f"{label} smallest of [{', '.join(map(str, arr))}] = {kth_smallest(arr[:], k)}")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        int partition(vector<int>& arr, int low, int high) {
            int pivot = arr[high], i = low - 1;
            for (int j = low; j < high; j++)
                if (arr[j] <= pivot) swap(arr[++i], arr[j]);
            swap(arr[i + 1], arr[high]);
            return i + 1;
        }

        int kthSmallest(vector<int> arr, int k) {
            int low = 0, high = (int)arr.size() - 1;
            while (low <= high) {
                int p = partition(arr, low, high);   // pivot lands at its final sorted index
                if (p == k - 1) return arr[p];
                if (p > k - 1) high = p - 1;         // answer is on the left
                else low = p + 1;                    // answer is on the right
            }
            return -1;
        }

        void show(const vector<int>& arr, int k, const string& label) {
            cout << label << " smallest of [";
            for (int i = 0; i < (int)arr.size(); i++) cout << (i ? ", " : "") << arr[i];
            cout << "] = " << kthSmallest(arr, k) << "\n";
        }

        int main() {
            show({10, 5, 30, 12}, 2, "2nd");
            show({7, 10, 4, 3, 20, 15}, 3, "3rd");
            show({7, 10, 4, 3, 20, 15}, 4, "4th");
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static int partition(int[] arr, int low, int high) {
                int pivot = arr[high], i = low - 1;
                for (int j = low; j < high; j++)
                    if (arr[j] <= pivot) { i++; int t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
                int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;
                return i + 1;
            }

            static int kthSmallest(int[] arr, int k) {
                int low = 0, high = arr.length - 1;
                while (low <= high) {
                    int p = partition(arr, low, high);   // pivot lands at its final sorted index
                    if (p == k - 1) return arr[p];
                    if (p > k - 1) high = p - 1;         // answer is on the left
                    else low = p + 1;                    // answer is on the right
                }
                return -1;
            }

            static void show(int[] arr, int k, String label) {
                String list = Arrays.toString(arr);      // "[10, 5, 30, 12]"
                System.out.println(label + " smallest of " + list + " = " + kthSmallest(arr.clone(), k));
            }

            public static void main(String[] args) {
                show(new int[]{10, 5, 30, 12}, 2, "2nd");
                show(new int[]{7, 10, 4, 3, 20, 15}, 3, "3rd");
                show(new int[]{7, 10, 4, 3, 20, 15}, 4, "4th");
            }
        }
    ''', js=r'''
        function partition(arr, low, high) {
            const pivot = arr[high];
            let i = low - 1;
            for (let j = low; j < high; j++)
                if (arr[j] <= pivot) { i++; [arr[i], arr[j]] = [arr[j], arr[i]]; }
            [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
            return i + 1;
        }

        function kthSmallest(arr, k) {
            let low = 0, high = arr.length - 1;
            while (low <= high) {
                const p = partition(arr, low, high);   // pivot lands at its final sorted index
                if (p === k - 1) return arr[p];
                if (p > k - 1) high = p - 1;           // answer is on the left
                else low = p + 1;                      // answer is on the right
            }
            return -1;
        }

        const show = (arr, k, label) =>
            console.log(`${label} smallest of [${arr.join(", ")}] = ${kthSmallest([...arr], k)}`);

        show([10, 5, 30, 12], 2, "2nd");
        show([7, 10, 4, 3, 20, 15], 3, "3rd");
        show([7, 10, 4, 3, 20, 15], 4, "4th");
    ''')
    yield complexity("O(n) expected, O(n²) worst", "O(1)")
    yield pitfall("Quickselect **rearranges** the array (copy it first if the caller needs the original) and has an `O(n²)` worst case with a bad pivot. A random pivot makes the worst case vanishingly unlikely; the *median of medians* pivot makes it a guaranteed `O(n)` at the price of a large constant. A size-`k` heap gives `O(n log k)` without modifying the input — better when `k` is tiny or the data streams in.")

    # ── minimum difference ────────────────────────────────────────────
    yield section("Minimum difference in an array", "minus")
    yield io("arr = [1, 8, 12, 5, 18]", "3", "arr = [8, 15]", "7", "arr = [10]", "INF")
    yield idea("The two closest values in a set are **neighbours once the array is sorted** — any other pair has a sorted element between them, which is closer to both. So: sort, scan adjacent differences, take the minimum. `O(n log n)` instead of `O(n²)` for all pairs.")
    yield multi('''
        [1, 8, 12, 5, 18] → 3
        [8, 15] → 7
        [10] → INF
    ''', py=r'''
        def min_diff(arr):
            if len(arr) < 2:
                return "INF"
            arr = sorted(arr)
            best = arr[1] - arr[0]
            for i in range(2, len(arr)):
                best = min(best, arr[i] - arr[i - 1])     # closest pair are sorted neighbours
            return str(best)

        for a in ([1, 8, 12, 5, 18], [8, 15], [10]):
            print(f"[{', '.join(map(str, a))}] → {min_diff(a)}")
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        string minDiff(vector<int> arr) {
            if (arr.size() < 2) return "INF";
            sort(arr.begin(), arr.end());
            int best = arr[1] - arr[0];
            for (int i = 2; i < (int)arr.size(); i++)
                best = min(best, arr[i] - arr[i - 1]);   // closest pair are sorted neighbours
            return to_string(best);
        }

        int main() {
            for (vector<int> a : {vector<int>{1, 8, 12, 5, 18}, {8, 15}, {10}}) {
                cout << "[";
                for (int i = 0; i < (int)a.size(); i++) cout << (i ? ", " : "") << a[i];
                cout << "] → " << minDiff(a) << "\n";
            }
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static String minDiff(int[] arr) {
                if (arr.length < 2) return "INF";
                arr = arr.clone();
                Arrays.sort(arr);
                int best = arr[1] - arr[0];
                for (int i = 2; i < arr.length; i++)
                    best = Math.min(best, arr[i] - arr[i - 1]);   // closest pair are sorted neighbours
                return String.valueOf(best);
            }

            public static void main(String[] args) {
                for (int[] a : new int[][]{{1, 8, 12, 5, 18}, {8, 15}, {10}})
                    System.out.println(Arrays.toString(a) + " → " + minDiff(a));
            }
        }
    ''', js=r'''
        function minDiff(arr) {
            if (arr.length < 2) return "INF";
            arr = [...arr].sort((a, b) => a - b);          // numeric comparator!
            let best = arr[1] - arr[0];
            for (let i = 2; i < arr.length; i++)
                best = Math.min(best, arr[i] - arr[i - 1]);   // closest pair are sorted neighbours
            return String(best);
        }

        for (const a of [[1, 8, 12, 5, 18], [8, 15], [10]])
            console.log(`[${a.join(", ")}] → ${minDiff(a)}`);
    ''')
    yield complexity("O(n log n)", "O(1) beyond the sort")

    # ── chocolate distribution ────────────────────────────────────────
    yield section("Chocolate distribution problem", "candy")
    yield io("packets = [7, 3, 2, 4, 9, 12, 56], m = 3", "2", "packets = [3, 4, 1, 9, 56, 7, 9, 12], m = 5", "6")
    yield p("`n` packets with the given chocolate counts; `m` children each get exactly one packet. Minimise the difference between the largest and smallest packet handed out.")
    yield idea("Sort. The `m` chosen packets should be **consecutive in sorted order** — if the chosen set had a gap, swapping an extreme element for the skipped one can only shrink the spread. So the answer is `min over i` of `sorted[i + m - 1] - sorted[i]`: a sliding window of width `m`.")
    yield diagram('''
        sorted: 2  3  4  7  9  12  56        m = 3
                [2  3  4]              → 4 - 2 = 2   ← minimum
                   [3  4  7]           → 7 - 3 = 4
                      [4  7  9]        → 9 - 4 = 5
                         [7  9  12]    → 12 - 7 = 5
                            [9  12 56] → 56 - 9 = 47
    ''', "Every window of m consecutive sorted values is a candidate")
    yield multi('''
        2
        6
    ''', py=r'''
        def min_spread(packets, m):
            if m == 0 or len(packets) == 0:
                return 0
            if len(packets) < m:
                return -1                              # not enough packets
            packets = sorted(packets)
            best = packets[m - 1] - packets[0]
            for i in range(1, len(packets) - m + 1):   # window [i, i + m - 1]
                best = min(best, packets[i + m - 1] - packets[i])
            return best

        print(min_spread([7, 3, 2, 4, 9, 12, 56], 3))
        print(min_spread([3, 4, 1, 9, 56, 7, 9, 12], 5))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        int minSpread(vector<int> packets, int m) {
            int n = packets.size();
            if (m == 0 || n == 0) return 0;
            if (n < m) return -1;                      // not enough packets
            sort(packets.begin(), packets.end());
            int best = packets[m - 1] - packets[0];
            for (int i = 1; i + m - 1 < n; i++)        // window [i, i + m - 1]
                best = min(best, packets[i + m - 1] - packets[i]);
            return best;
        }

        int main() {
            cout << minSpread({7, 3, 2, 4, 9, 12, 56}, 3) << "\n";
            cout << minSpread({3, 4, 1, 9, 56, 7, 9, 12}, 5) << "\n";
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static int minSpread(int[] packets, int m) {
                int n = packets.length;
                if (m == 0 || n == 0) return 0;
                if (n < m) return -1;                  // not enough packets
                packets = packets.clone();
                Arrays.sort(packets);
                int best = packets[m - 1] - packets[0];
                for (int i = 1; i + m - 1 < n; i++)    // window [i, i + m - 1]
                    best = Math.min(best, packets[i + m - 1] - packets[i]);
                return best;
            }

            public static void main(String[] args) {
                System.out.println(minSpread(new int[]{7, 3, 2, 4, 9, 12, 56}, 3));
                System.out.println(minSpread(new int[]{3, 4, 1, 9, 56, 7, 9, 12}, 5));
            }
        }
    ''', js=r'''
        function minSpread(packets, m) {
            const n = packets.length;
            if (m === 0 || n === 0) return 0;
            if (n < m) return -1;                      // not enough packets
            packets = [...packets].sort((a, b) => a - b);
            let best = packets[m - 1] - packets[0];
            for (let i = 1; i + m - 1 < n; i++)        // window [i, i + m - 1]
                best = Math.min(best, packets[i + m - 1] - packets[i]);
            return best;
        }

        console.log(minSpread([7, 3, 2, 4, 9, 12, 56], 3));
        console.log(minSpread([3, 4, 1, 9, 56, 7, 9, 12], 5));
    ''')
    yield complexity("O(n log n)", "O(1) beyond the sort")
    yield note("Minimum difference is the special case `m = 2`. Both problems share the lesson: **sorting turns a “which pair / which subset” question into a scan of neighbours**.")

    # ── two types ─────────────────────────────────────────────────────
    yield section("Sort an array with two types of elements", "layout-columns")
    yield p("Three classic variants of the same problem — move every element of one *type* before every element of the other, in a single pass with `O(1)` space:")
    yield io("Segregate negatives and positives: [15, 18, -3, -2]", "-2 -3 18 15 (any order inside a group is accepted)",
             "Segregate even and odd: [15, 14, 13, 12]", "12 14 13 15",
             "Sort a binary array: [0, 1, 1, 1, 0]", "0 0 1 1 1")
    yield snippet("py", r'''
        # Naive: copy the "left" type, then the "right" type, into a temporary array — O(n) time but O(n) space
        def two_types_naive(arr, is_left):
            temp = [x for x in arr if is_left(x)] + [x for x in arr if not is_left(x)]
            for i in range(len(arr)):
                arr[i] = temp[i]
            return arr

        print(*two_types_naive([15, 18, -3, -2], lambda x: x < 0))
        print(*two_types_naive([0, 1, 1, 1, 0], lambda x: x == 0))
    ''', out="-3 -2 15 18\n0 0 1 1 1")
    yield idea("This is exactly **Hoare's partition** from quick sort with the predicate playing the role of “less than pivot”. `i` walks right over elements already of the left type, `j` walks left over elements already of the right type; when both stop they point at two misplaced elements — swap them. Each element is examined once.")
    yield multi('''
        negatives first: -2 -3 18 15
        evens first: 12 14 13 15
        binary: 0 0 1 1 1
    ''', py=r'''
        def two_types(arr, is_left):
            i, j = 0, len(arr) - 1
            while i < j:
                while i < j and is_left(arr[i]):        # already on the correct side
                    i += 1
                while i < j and not is_left(arr[j]):
                    j -= 1
                if i < j:                               # arr[i] is right-type, arr[j] is left-type
                    arr[i], arr[j] = arr[j], arr[i]
                    i += 1
                    j -= 1
            return arr

        print("negatives first:", *two_types([15, 18, -3, -2], lambda x: x < 0))
        print("evens first:", *two_types([15, 14, 13, 12], lambda x: x % 2 == 0))
        print("binary:", *two_types([0, 1, 1, 1, 0], lambda x: x == 0))
    ''', cpp=r'''
        #include <functional>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        void twoTypes(vector<int>& arr, const function<bool(int)>& isLeft) {
            int i = 0, j = (int)arr.size() - 1;
            while (i < j) {
                while (i < j && isLeft(arr[i])) i++;    // already on the correct side
                while (i < j && !isLeft(arr[j])) j--;
                if (i < j) swap(arr[i++], arr[j--]);    // arr[i] is right-type, arr[j] is left-type
            }
        }

        void show(const string& label, vector<int> arr, const function<bool(int)>& isLeft) {
            twoTypes(arr, isLeft);
            cout << label << ":";
            for (int x : arr) cout << " " << x;
            cout << "\n";
        }

        int main() {
            show("negatives first", {15, 18, -3, -2}, [](int x) { return x < 0; });
            show("evens first", {15, 14, 13, 12}, [](int x) { return x % 2 == 0; });
            show("binary", {0, 1, 1, 1, 0}, [](int x) { return x == 0; });
        }
    ''', java=r'''
        import java.util.function.IntPredicate;

        public class Main {
            static void twoTypes(int[] arr, IntPredicate isLeft) {
                int i = 0, j = arr.length - 1;
                while (i < j) {
                    while (i < j && isLeft.test(arr[i])) i++;    // already on the correct side
                    while (i < j && !isLeft.test(arr[j])) j--;
                    if (i < j) { int t = arr[i]; arr[i++] = arr[j]; arr[j--] = t; }   // swap misplaced pair
                }
            }

            static void show(String label, int[] arr, IntPredicate isLeft) {
                twoTypes(arr, isLeft);
                StringBuilder sb = new StringBuilder(label + ":");
                for (int x : arr) sb.append(' ').append(x);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                show("negatives first", new int[]{15, 18, -3, -2}, x -> x < 0);
                show("evens first", new int[]{15, 14, 13, 12}, x -> x % 2 == 0);
                show("binary", new int[]{0, 1, 1, 1, 0}, x -> x == 0);
            }
        }
    ''', js=r'''
        function twoTypes(arr, isLeft) {
            let i = 0, j = arr.length - 1;
            while (i < j) {
                while (i < j && isLeft(arr[i])) i++;        // already on the correct side
                while (i < j && !isLeft(arr[j])) j--;
                if (i < j) { [arr[i], arr[j]] = [arr[j], arr[i]]; i++; j--; }   // swap misplaced pair
            }
            return arr;
        }

        console.log("negatives first:", twoTypes([15, 18, -3, -2], (x) => x < 0).join(" "));
        console.log("evens first:", twoTypes([15, 14, 13, 12], (x) => x % 2 === 0).join(" "));
        console.log("binary:", twoTypes([0, 1, 1, 1, 0], (x) => x === 0).join(" "));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("The **Lomuto-style** one-pass alternative — keep a boundary `j`; for each `i`, if `arr[i]` is left-type swap it to `arr[j]` and `j++` — is shorter but does more swaps. Neither version is stable; if the relative order inside each group must be preserved you need the `O(n)`-space copy (or an `O(n log n)` stable partition).")

    # ── three types ───────────────────────────────────────────────────
    yield section("Sort an array with three types (Dutch national flag)", "flag")
    yield io("Sort 0s, 1s and 2s: [0, 1, 2, 1, 1, 2]", "0 1 1 1 2 2",
             "Three-way partition around pivot 2: [2, 1, 2, 20, 10, 20, 1]", "1 1 2 2 20 10 20",
             "Partition around range [5, 10]: [10, 5, 6, 3, 20, 9, 40]", "3 5 6 10 9 40 20")
    yield snippet("py", r'''
        # Naive: three passes collecting 0s, then 1s, then 2s — O(n) time, O(n) space
        def sort012_naive(arr):
            return [x for x in arr if x == 0] + [x for x in arr if x == 1] + [x for x in arr if x == 2]

        print(*sort012_naive([0, 1, 2, 1, 1, 2]))
    ''', out="0 1 1 1 2 2")
    yield idea("Maintain **three regions** with two boundaries: `[0, low)` holds *small* values, `[low, mid)` holds *middle* values, `(high, n-1]` holds *large* values, and `[mid, high]` is unknown. Look at `arr[mid]`: small → swap with `arr[low]`, advance both; middle → just advance `mid`; large → swap with `arr[high]` and shrink `high` (do **not** advance `mid`, the swapped-in element is unexamined). When `mid` passes `high` the unknown region is empty.")
    yield diagram('''
        [ small … | middle … | ??? unknown ??? | large … ]
          0      low        mid             high       n-1

        arr[mid] < L   → swap(arr[low], arr[mid]); low++; mid++
        L ≤ arr[mid] ≤ U → mid++
        arr[mid] > U   → swap(arr[mid], arr[high]); high--
    ''', "Dijkstra's three-way partition: one pass, O(1) space")
    yield p("One routine, parameterised by the middle range `[L, U]`, solves all three variants: 0/1/2 sorting is `L = U = 1`, three-way partitioning around a pivot is `L = U = pivot`, and partitioning around a range is the general case.")
    yield multi('''
        0 1 1 1 2 2
        1 1 2 2 20 10 20
        3 5 6 10 9 40 20
    ''', py=r'''
        def three_way(arr, L, U):
            low, mid, high = 0, 0, len(arr) - 1
            while mid <= high:
                if arr[mid] < L:                           # small → grow the left region
                    arr[low], arr[mid] = arr[mid], arr[low]
                    low += 1
                    mid += 1
                elif arr[mid] > U:                         # large → grow the right region
                    arr[mid], arr[high] = arr[high], arr[mid]
                    high -= 1                              # mid stays: new arr[mid] is unexamined
                else:                                      # middle → already in place
                    mid += 1
            return arr

        print(*three_way([0, 1, 2, 1, 1, 2], 1, 1))         # sort 0s, 1s, 2s
        print(*three_way([2, 1, 2, 20, 10, 20, 1], 2, 2))   # partition around pivot 2
        print(*three_way([10, 5, 6, 3, 20, 9, 40], 5, 10))  # partition around range [5, 10]
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void threeWay(vector<int>& arr, int L, int U) {
            int low = 0, mid = 0, high = (int)arr.size() - 1;
            while (mid <= high) {
                if (arr[mid] < L) swap(arr[low++], arr[mid++]);     // small → grow the left region
                else if (arr[mid] > U) swap(arr[mid], arr[high--]); // large → grow the right (mid stays)
                else mid++;                                         // middle → already in place
            }
        }

        void show(vector<int> arr, int L, int U) {
            threeWay(arr, L, U);
            for (int i = 0; i < (int)arr.size(); i++) cout << (i ? " " : "") << arr[i];
            cout << "\n";
        }

        int main() {
            show({0, 1, 2, 1, 1, 2}, 1, 1);          // sort 0s, 1s, 2s
            show({2, 1, 2, 20, 10, 20, 1}, 2, 2);    // partition around pivot 2
            show({10, 5, 6, 3, 20, 9, 40}, 5, 10);   // partition around range [5, 10]
        }
    ''', java=r'''
        public class Main {
            static void threeWay(int[] arr, int L, int U) {
                int low = 0, mid = 0, high = arr.length - 1;
                while (mid <= high) {
                    if (arr[mid] < L) {                              // small → grow the left region
                        int t = arr[low]; arr[low] = arr[mid]; arr[mid] = t;
                        low++; mid++;
                    } else if (arr[mid] > U) {                       // large → grow the right (mid stays)
                        int t = arr[mid]; arr[mid] = arr[high]; arr[high] = t;
                        high--;
                    } else {
                        mid++;                                       // middle → already in place
                    }
                }
            }

            static void show(int[] arr, int L, int U) {
                threeWay(arr, L, U);
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < arr.length; i++) sb.append(i > 0 ? " " : "").append(arr[i]);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                show(new int[]{0, 1, 2, 1, 1, 2}, 1, 1);          // sort 0s, 1s, 2s
                show(new int[]{2, 1, 2, 20, 10, 20, 1}, 2, 2);    // partition around pivot 2
                show(new int[]{10, 5, 6, 3, 20, 9, 40}, 5, 10);   // partition around range [5, 10]
            }
        }
    ''', js=r'''
        function threeWay(arr, L, U) {
            let low = 0, mid = 0, high = arr.length - 1;
            while (mid <= high) {
                if (arr[mid] < L) {                                  // small → grow the left region
                    [arr[low], arr[mid]] = [arr[mid], arr[low]];
                    low++; mid++;
                } else if (arr[mid] > U) {                           // large → grow the right (mid stays)
                    [arr[mid], arr[high]] = [arr[high], arr[mid]];
                    high--;
                } else {
                    mid++;                                           // middle → already in place
                }
            }
            return arr;
        }

        console.log(threeWay([0, 1, 2, 1, 1, 2], 1, 1).join(" "));         // sort 0s, 1s, 2s
        console.log(threeWay([2, 1, 2, 20, 10, 20, 1], 2, 2).join(" "));   // partition around pivot 2
        console.log(threeWay([10, 5, 6, 3, 20, 9, 40], 5, 10).join(" "));  // partition around range [5, 10]
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Advancing `mid` after swapping with `high` skips an element that was never looked at — the most common bug in this algorithm. Also note that the order *inside* the small and large groups is arbitrary (`20 10 20` above); the notes' range example showed a stable order because it used three list comprehensions, which cost `O(n)` extra space.")

    # ── merge overlapping intervals ───────────────────────────────────
    yield section("Merge overlapping intervals", "arrows-join")
    yield io("[[1, 3], [2, 4], [5, 7], [6, 8]]", "[1,4] [5,8]", "[[7, 9], [6, 10], [4, 5], [1, 3], [2, 4]]", "[1,5] [6,10]")
    yield p("Two intervals `a` and `b` overlap when `a.start <= b.end` and `b.start <= a.end` (they touch or cross). The naive approach repeatedly picks an interval, merges everything that overlaps it and deletes the absorbed ones — up to `n` passes of `O(n²)` work.")
    yield idea("**Sort by start.** Walk through the sorted list keeping the last merged interval `m`. If the next interval starts at or before `m.end`, it overlaps `m` — extend `m.end`. Otherwise it starts a new merged interval. The key claim: a new interval can never overlap any *earlier* merged interval `m'` because `x.start >= m.start > m'.end` — once sorted, overlaps are only ever with the most recent one.")
    yield diagram('''
        sorted:  [1,3] [2,4] [5,7] [6,8]

        [1,3]            → start result: [1,3]
        [2,4]  2 ≤ 3     → overlaps, extend: [1,4]
        [5,7]  5 > 4     → new interval:     [1,4] [5,7]
        [6,8]  6 ≤ 7     → overlaps, extend: [1,4] [5,8]
    ''', "After sorting, each interval is compared with the last merged one only")
    yield multi('''
        [1,4] [5,8]
        [1,5] [6,10]
    ''', py=r'''
        def merge_intervals(intervals):
            intervals.sort(key=lambda iv: iv[0])          # by start
            merged = [intervals[0]]
            for start, end in intervals[1:]:
                if start <= merged[-1][1]:                # overlaps the last merged interval
                    merged[-1][1] = max(merged[-1][1], end)
                else:
                    merged.append([start, end])
            return merged

        for ivs in ([[1, 3], [2, 4], [5, 7], [6, 8]], [[7, 9], [6, 10], [4, 5], [1, 3], [2, 4]]):
            print(" ".join(f"[{s},{e}]" for s, e in merge_intervals(ivs)))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<pair<int, int>> mergeIntervals(vector<pair<int, int>> iv) {
            sort(iv.begin(), iv.end());                   // pairs sort by start, then end
            vector<pair<int, int>> merged = {iv[0]};
            for (int i = 1; i < (int)iv.size(); i++) {
                if (iv[i].first <= merged.back().second)  // overlaps the last merged interval
                    merged.back().second = max(merged.back().second, iv[i].second);
                else
                    merged.push_back(iv[i]);
            }
            return merged;
        }

        int main() {
            vector<vector<pair<int, int>>> tests = {{{1, 3}, {2, 4}, {5, 7}, {6, 8}},
                                                    {{7, 9}, {6, 10}, {4, 5}, {1, 3}, {2, 4}}};
            for (auto& t : tests) {
                auto m = mergeIntervals(t);
                for (int i = 0; i < (int)m.size(); i++)
                    cout << (i ? " " : "") << "[" << m[i].first << "," << m[i].second << "]";
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Arrays;
        import java.util.List;

        public class Main {
            static List<int[]> mergeIntervals(int[][] iv) {
                Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));   // by start
                List<int[]> merged = new ArrayList<>();
                merged.add(iv[0]);
                for (int i = 1; i < iv.length; i++) {
                    int[] last = merged.get(merged.size() - 1);
                    if (iv[i][0] <= last[1])                          // overlaps the last merged interval
                        last[1] = Math.max(last[1], iv[i][1]);
                    else
                        merged.add(iv[i]);
                }
                return merged;
            }

            public static void main(String[] args) {
                int[][][] tests = {{{1, 3}, {2, 4}, {5, 7}, {6, 8}}, {{7, 9}, {6, 10}, {4, 5}, {1, 3}, {2, 4}}};
                for (int[][] t : tests) {
                    StringBuilder sb = new StringBuilder();
                    for (int[] m : mergeIntervals(t))
                        sb.append(sb.length() > 0 ? " " : "").append("[").append(m[0]).append(",").append(m[1]).append("]");
                    System.out.println(sb);
                }
            }
        }
    ''', js=r'''
        function mergeIntervals(intervals) {
            intervals.sort((a, b) => a[0] - b[0]);            // by start
            const merged = [intervals[0]];
            for (let i = 1; i < intervals.length; i++) {
                const last = merged[merged.length - 1];
                if (intervals[i][0] <= last[1])               // overlaps the last merged interval
                    last[1] = Math.max(last[1], intervals[i][1]);
                else
                    merged.push(intervals[i]);
            }
            return merged;
        }

        for (const ivs of [[[1, 3], [2, 4], [5, 7], [6, 8]], [[7, 9], [6, 10], [4, 5], [1, 3], [2, 4]]])
            console.log(mergeIntervals(ivs).map(([s, e]) => `[${s},${e}]`).join(" "));
    ''')
    yield complexity("O(n log n)", "O(n) for the result (O(1) if merged in place)")
    yield note("Decide whether touching intervals (`[1, 3]` and `[3, 5]`) merge: the `<=` test above merges them; use `<` to keep them apart. The same sort-then-sweep handles *insert interval*, *interval intersection* and *minimum meeting rooms* (the next problem).")

    # ── meeting maximum guests ────────────────────────────────────────
    yield section("Meeting maximum guests", "users")
    yield io("arrival = [900, 940], departure = [1000, 1030]", "2", "arrival = [800, 700, 600, 500], departure = [840, 820, 830, 530]", "3")
    yield p("Guest `i` is present from `arrival[i]` to `departure[i]` (times `0000`–`2359`). Find the maximum number of guests present at the same time — the moment to hold a toast. Checking every minute against every guest is `O(1440 · n)`; checking every arrival against every guest is `O(n²)`.")
    yield idea("Sort arrivals and departures **separately** and sweep through them as a merged sequence of events. An arrival increments the current count, a departure decrements it; the maximum count seen is the answer. Who arrived or left does not matter, only *how many* are present — which is why the two arrays may be sorted independently.")
    yield diagram('''
        arrivals:    500  600  700  800
        departures:  530  820  830  840

        time  500 → +1 (1)   530 → -1 (0)   600 → +1 (1)   700 → +1 (2)
              800 → +1 (3)   820 → -1 (2)   830 → -1 (1)   840 → -1 (0)
        maximum = 3
    ''', "Sweep both sorted arrays like a merge, counting current guests")
    yield multi('''
        2
        3
    ''', py=r'''
        def max_guests(arrival, departure):
            arrival, departure = sorted(arrival), sorted(departure)
            n = len(arrival)
            i, j = 1, 0
            current = best = 1 if n else 0
            while i < n and j < n:
                if arrival[i] <= departure[j]:      # next event is an arrival (ties count as overlap)
                    current += 1
                    i += 1
                else:                               # next event is a departure
                    current -= 1
                    j += 1
                best = max(best, current)
            return best

        print(max_guests([900, 940], [1000, 1030]))
        print(max_guests([800, 700, 600, 500], [840, 820, 830, 530]))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        int maxGuests(vector<int> arrival, vector<int> departure) {
            sort(arrival.begin(), arrival.end());
            sort(departure.begin(), departure.end());
            int n = arrival.size();
            int i = 1, j = 0, current = n ? 1 : 0, best = current;
            while (i < n && j < n) {
                if (arrival[i] <= departure[j]) { current++; i++; }   // arrival (ties count as overlap)
                else { current--; j++; }                               // departure
                best = max(best, current);
            }
            return best;
        }

        int main() {
            cout << maxGuests({900, 940}, {1000, 1030}) << "\n";
            cout << maxGuests({800, 700, 600, 500}, {840, 820, 830, 530}) << "\n";
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static int maxGuests(int[] arrival, int[] departure) {
                arrival = arrival.clone(); departure = departure.clone();
                Arrays.sort(arrival);
                Arrays.sort(departure);
                int n = arrival.length;
                int i = 1, j = 0, current = n > 0 ? 1 : 0, best = current;
                while (i < n && j < n) {
                    if (arrival[i] <= departure[j]) { current++; i++; }   // arrival (ties count as overlap)
                    else { current--; j++; }                               // departure
                    best = Math.max(best, current);
                }
                return best;
            }

            public static void main(String[] args) {
                System.out.println(maxGuests(new int[]{900, 940}, new int[]{1000, 1030}));
                System.out.println(maxGuests(new int[]{800, 700, 600, 500}, new int[]{840, 820, 830, 530}));
            }
        }
    ''', js=r'''
        function maxGuests(arrival, departure) {
            arrival = [...arrival].sort((a, b) => a - b);
            departure = [...departure].sort((a, b) => a - b);
            const n = arrival.length;
            let i = 1, j = 0, current = n ? 1 : 0, best = current;
            while (i < n && j < n) {
                if (arrival[i] <= departure[j]) { current++; i++; }   // arrival (ties count as overlap)
                else { current--; j++; }                               // departure
                best = Math.max(best, current);
            }
            return best;
        }

        console.log(maxGuests([900, 940], [1000, 1030]));
        console.log(maxGuests([800, 700, 600, 500], [840, 820, 830, 530]));
    ''')
    yield complexity("O(n log n)", "O(1) beyond the sorts")
    yield note("Because times are bounded (`0..2359`), a **counting** variant is `O(n + 2360)`: add `+1` at each arrival, `-1` just after each departure in a 2360-slot array, then take the running maximum. This is the *difference array* trick, and it is the right answer when `n` is huge and the time range is small. The loop needs `i` to start at `1` with `current = 1` because the first arrival is always the first event.")

    # ── counting sort ─────────────────────────────────────────────────
    yield section("Counting sort", "123")
    yield define("Counting sort", "a `Θ(n + k)` **non-comparison** sort for values in a known range `0..k-1`: count how many times each value occurs, convert the counts to starting positions, then place each element directly at its position.")
    yield io("arr = [1, 4, 4, 1, 0, 1], k = 5", "0 1 1 1 4 4")
    yield snippet("py", r'''
        # Simplest form: count, then write each value count[v] times — fine for plain integers
        def counting_sort_simple(arr, k):
            count = [0] * k
            for x in arr:
                count[x] += 1
            idx = 0
            for v in range(k):
                for _ in range(count[v]):
                    arr[idx] = v
                    idx += 1

        a = [1, 4, 4, 1, 0, 1]
        counting_sort_simple(a, 5)
        print(*a)
    ''', out="0 1 1 1 4 4")
    yield p("That version only works when the *value is the whole record*. To sort students by marks (records with a key) you must move the original objects, which needs the **stable** formulation:")
    yield diagram('''
        arr   = 1 4 4 1 0 1          k = 5

        count = [1, 3, 0, 0, 2]      how many of each value
        prefix= [1, 4, 4, 4, 6]      count[v] = number of elements ≤ v  (= end position of value v)

        scan arr from the RIGHT, place each x at output[count[x] - 1], then count[x]--:
          x=1 → output[3]=1, count[1]=3      x=0 → output[0]=0
          x=1 → output[2]=1, count[1]=2      x=1 → output[1]=1
          x=4 → output[5]=4, count[4]=1      x=4 → output[4]=4
        output = 0 1 1 1 4 4
    ''', "Prefix sums turn counts into positions; scanning right-to-left keeps equal keys in input order")
    yield multi('''
        0 1 1 1 4 4
    ''', py=r'''
        def counting_sort(arr, k):
            count = [0] * k
            for x in arr:
                count[x] += 1
            for v in range(1, k):
                count[v] += count[v - 1]          # count[v] = number of elements <= v
            output = [0] * len(arr)
            for x in reversed(arr):               # right-to-left keeps the sort stable
                count[x] -= 1
                output[count[x]] = x
            arr[:] = output

        a = [1, 4, 4, 1, 0, 1]
        counting_sort(a, 5)
        print(*a)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        void countingSort(vector<int>& arr, int k) {
            vector<int> count(k, 0);
            for (int x : arr) count[x]++;
            for (int v = 1; v < k; v++) count[v] += count[v - 1];   // count[v] = number of elements <= v
            vector<int> output(arr.size());
            for (int i = (int)arr.size() - 1; i >= 0; i--)          // right-to-left keeps the sort stable
                output[--count[arr[i]]] = arr[i];
            arr = output;
        }

        int main() {
            vector<int> a = {1, 4, 4, 1, 0, 1};
            countingSort(a, 5);
            for (int i = 0; i < (int)a.size(); i++) cout << (i ? " " : "") << a[i];
            cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static void countingSort(int[] arr, int k) {
                int[] count = new int[k];
                for (int x : arr) count[x]++;
                for (int v = 1; v < k; v++) count[v] += count[v - 1];   // count[v] = number of elements <= v
                int[] output = new int[arr.length];
                for (int i = arr.length - 1; i >= 0; i--)               // right-to-left keeps the sort stable
                    output[--count[arr[i]]] = arr[i];
                System.arraycopy(output, 0, arr, 0, arr.length);
            }

            public static void main(String[] args) {
                int[] a = {1, 4, 4, 1, 0, 1};
                countingSort(a, 5);
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < a.length; i++) sb.append(i > 0 ? " " : "").append(a[i]);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function countingSort(arr, k) {
            const count = new Array(k).fill(0);
            for (const x of arr) count[x]++;
            for (let v = 1; v < k; v++) count[v] += count[v - 1];   // count[v] = number of elements <= v
            const output = new Array(arr.length);
            for (let i = arr.length - 1; i >= 0; i--)               // right-to-left keeps the sort stable
                output[--count[arr[i]]] = arr[i];
            for (let i = 0; i < arr.length; i++) arr[i] = output[i];
        }

        const a = [1, 4, 4, 1, 0, 1];
        countingSort(a, 5);
        console.log(a.join(" "));
    ''')
    yield complexity("Θ(n + k)", "Θ(n + k)")
    yield snippet("py", r'''
        # Stability in action: sort records by a key, then any range by shifting with min(arr)
        def counting_sort_by(items, key, k):
            count = [0] * k
            for it in items:
                count[key(it)] += 1
            for v in range(1, k):
                count[v] += count[v - 1]
            output = [None] * len(items)
            for it in reversed(items):
                count[key(it)] -= 1
                output[count[key(it)]] = it
            return output

        students = [("Asha", 3), ("Ravi", 1), ("Meena", 3), ("John", 1), ("Zoe", 2)]
        print(counting_sort_by(students, key=lambda s: s[1], k=4))

        def counting_sort_any_range(arr):           # values in [min, max] — shift by min
            lo = min(arr)
            return counting_sort_by(arr, key=lambda x: x - lo, k=max(arr) - lo + 1)

        print(counting_sort_any_range([1, -2, 4, 4, -1, 1, 0]))
    ''', out="[('Ravi', 1), ('John', 1), ('Zoe', 2), ('Asha', 3), ('Meena', 3)]\n[-2, -1, 0, 1, 1, 4, 4]")
    yield ul(
        "**Not comparison based** — it beats the `Ω(n log n)` lower bound because it exploits the value range.",
        "**Stable** when written with prefix sums and a right-to-left scan — this is what radix sort relies on.",
        "**Not in place**: needs the `count` array and an `output` array.",
        "Useless when `k` is much larger than `n` (sorting five values in `0..10⁹` would allocate a billion counters) — that is where radix sort takes over.",
    )
    yield pitfall("The notes' “updated solution” defined `countingSort` but then called the old `Countingsort` — a Python name-case slip that silently ran the wrong function. Case matters in identifiers in all four languages.")

    # ── cycle sort ────────────────────────────────────────────────────
    yield section("Cycle sort", "refresh")
    yield define("Cycle sort", "an in-place, unstable `O(n²)` sort that performs the **minimum possible number of writes** — every element is written at most once, directly into its final position. It is the algorithm of choice when writes are expensive (flash memory, EEPROM) or when you need the minimum number of swaps to sort an array.")
    yield io("arr = [30, 40, 50, 10, 20, 50]", "10 20 30 40 50 50 (5 writes)")
    yield idea("The final index of a value equals the **number of elements smaller than it** (plus the number of equal elements already placed). Take the element at position `cs`, count how many are smaller to find its destination, write it there and pick up the element that was there — follow this *cycle* of displacements until it returns to `cs`. Then move to `cs + 1`.")
    yield diagram('''
        arr = 30 40 50 10 20 50       start at cs = 0, item = 30

        30 has 2 smaller → goes to index 2, picks up 50
        50 has 3 smaller, one equal already placed? no → index 4, picks up 20
        20 has 1 smaller → index 1, picks up 40
        40 has 3 smaller → index 3, picks up 10
        10 has 0 smaller → index 0 = cs → cycle closed

        arr = 10 20 30 40 50 50       5 writes for 5 misplaced elements
    ''', "One cycle of displacements fixes five elements with five writes")
    yield multi('''
        10 20 30 40 50 50
        writes: 5
    ''', py=r'''
        def cycle_sort(arr):
            writes = 0
            n = len(arr)
            for cs in range(n - 1):
                item = arr[cs]
                pos = cs
                for i in range(cs + 1, n):               # destination = number of smaller elements
                    if arr[i] < item:
                        pos += 1
                if pos == cs:
                    continue                             # already in place
                while item == arr[pos]:                  # skip duplicates already placed
                    pos += 1
                arr[pos], item = item, arr[pos]          # write, pick up the displaced element
                writes += 1
                while pos != cs:                         # follow the cycle back to cs
                    pos = cs
                    for i in range(cs + 1, n):
                        if arr[i] < item:
                            pos += 1
                    while item == arr[pos]:
                        pos += 1
                    arr[pos], item = item, arr[pos]
                    writes += 1
            return writes

        a = [30, 40, 50, 10, 20, 50]
        w = cycle_sort(a)
        print(*a)
        print("writes:", w)
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int cycleSort(vector<int>& arr) {
            int writes = 0, n = arr.size();
            for (int cs = 0; cs < n - 1; cs++) {
                int item = arr[cs], pos = cs;
                for (int i = cs + 1; i < n; i++)         // destination = number of smaller elements
                    if (arr[i] < item) pos++;
                if (pos == cs) continue;                 // already in place
                while (item == arr[pos]) pos++;          // skip duplicates already placed
                swap(arr[pos], item); writes++;          // write, pick up the displaced element
                while (pos != cs) {                      // follow the cycle back to cs
                    pos = cs;
                    for (int i = cs + 1; i < n; i++)
                        if (arr[i] < item) pos++;
                    while (item == arr[pos]) pos++;
                    swap(arr[pos], item); writes++;
                }
            }
            return writes;
        }

        int main() {
            vector<int> a = {30, 40, 50, 10, 20, 50};
            int w = cycleSort(a);
            for (int i = 0; i < (int)a.size(); i++) cout << (i ? " " : "") << a[i];
            cout << "\nwrites: " << w << "\n";
        }
    ''', java=r'''
        public class Main {
            static int cycleSort(int[] arr) {
                int writes = 0, n = arr.length;
                for (int cs = 0; cs < n - 1; cs++) {
                    int item = arr[cs], pos = cs;
                    for (int i = cs + 1; i < n; i++)     // destination = number of smaller elements
                        if (arr[i] < item) pos++;
                    if (pos == cs) continue;             // already in place
                    while (item == arr[pos]) pos++;      // skip duplicates already placed
                    int t = arr[pos]; arr[pos] = item; item = t; writes++;   // write, pick up displaced
                    while (pos != cs) {                  // follow the cycle back to cs
                        pos = cs;
                        for (int i = cs + 1; i < n; i++)
                            if (arr[i] < item) pos++;
                        while (item == arr[pos]) pos++;
                        t = arr[pos]; arr[pos] = item; item = t; writes++;
                    }
                }
                return writes;
            }

            public static void main(String[] args) {
                int[] a = {30, 40, 50, 10, 20, 50};
                int w = cycleSort(a);
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < a.length; i++) sb.append(i > 0 ? " " : "").append(a[i]);
                System.out.println(sb);
                System.out.println("writes: " + w);
            }
        }
    ''', js=r'''
        function cycleSort(arr) {
            let writes = 0;
            const n = arr.length;
            for (let cs = 0; cs < n - 1; cs++) {
                let item = arr[cs], pos = cs;
                for (let i = cs + 1; i < n; i++)         // destination = number of smaller elements
                    if (arr[i] < item) pos++;
                if (pos === cs) continue;                // already in place
                while (item === arr[pos]) pos++;         // skip duplicates already placed
                [arr[pos], item] = [item, arr[pos]]; writes++;   // write, pick up the displaced element
                while (pos !== cs) {                     // follow the cycle back to cs
                    pos = cs;
                    for (let i = cs + 1; i < n; i++)
                        if (arr[i] < item) pos++;
                    while (item === arr[pos]) pos++;
                    [arr[pos], item] = [item, arr[pos]]; writes++;
                }
            }
            return writes;
        }

        const a = [30, 40, 50, 10, 20, 50];
        const w = cycleSort(a);
        console.log(a.join(" "));
        console.log("writes:", w);
    ''')
    yield complexity("O(n²)", "O(1)")
    yield ul(
        "Worst and average case `O(n²)` comparisons — never use it for speed.",
        "At most `n - 1` writes in total, versus up to `O(n²)` for insertion or bubble sort.",
        "In place, **not stable**.",
        "The number of writes equals the **minimum number of swaps** needed to sort the array — the standard way to solve that interview question. When the values are a permutation of `0..n-1`, the destination of `x` is simply `x`, no counting needed, and the whole sort becomes `O(n)`.",
    )

    # ── radix sort ────────────────────────────────────────────────────
    yield section("Radix sort", "binary")
    yield define("Radix sort (LSD)", "sort the numbers digit by digit, from the **least significant digit** to the most significant, using a *stable* counting sort for each digit. After processing the most significant digit the array is fully sorted.")
    yield io("arr = [319, 212, 6, 8, 100, 50]", "6 8 50 100 212 319")
    yield diagram('''
        write with leading zeros:   319 212 006 008 100 050

        stable sort by units digit:     100 050 212 006 008 319
        stable sort by tens digit:      100 006 008 212 319 050
        stable sort by hundreds digit:  006 008 050 100 212 319
    ''', "Three stable passes (one per digit) — each pass preserves the order established by the previous ones")
    yield idea("Why LSD works: after sorting by the tens digit, numbers with equal tens digits are still in units-digit order **because the pass is stable**. Induction over the digits gives a fully sorted array after the last pass. Each pass is a counting sort with `k = 10`, so the total is `O(d · (n + 10))` where `d` is the number of digits of the maximum.")
    yield multi('''
        after pass exp=1: 100 50 212 6 8 319
        after pass exp=10: 100 6 8 212 319 50
        after pass exp=100: 6 8 50 100 212 319
    ''', py=r'''
        def counting_sort_by_digit(arr, exp):
            output = [0] * len(arr)
            count = [0] * 10
            for x in arr:
                count[(x // exp) % 10] += 1
            for d in range(1, 10):
                count[d] += count[d - 1]
            for x in reversed(arr):                    # stable
                d = (x // exp) % 10
                count[d] -= 1
                output[count[d]] = x
            arr[:] = output

        def radix_sort(arr):
            mx = max(arr)
            exp = 1
            while mx // exp > 0:                       # one pass per digit of the maximum
                counting_sort_by_digit(arr, exp)
                print(f"after pass exp={exp}:", *arr)
                exp *= 10

        radix_sort([319, 212, 6, 8, 100, 50])
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        void countingSortByDigit(vector<int>& arr, int exp) {
            vector<int> output(arr.size()), count(10, 0);
            for (int x : arr) count[(x / exp) % 10]++;
            for (int d = 1; d < 10; d++) count[d] += count[d - 1];
            for (int i = (int)arr.size() - 1; i >= 0; i--)   // stable
                output[--count[(arr[i] / exp) % 10]] = arr[i];
            arr = output;
        }

        void radixSort(vector<int>& arr) {
            int mx = *max_element(arr.begin(), arr.end());
            for (int exp = 1; mx / exp > 0; exp *= 10) {   // one pass per digit of the maximum
                countingSortByDigit(arr, exp);
                cout << "after pass exp=" << exp << ":";
                for (int x : arr) cout << " " << x;
                cout << "\n";
            }
        }

        int main() {
            vector<int> a = {319, 212, 6, 8, 100, 50};
            radixSort(a);
        }
    ''', java=r'''
        public class Main {
            static void countingSortByDigit(int[] arr, int exp) {
                int[] output = new int[arr.length], count = new int[10];
                for (int x : arr) count[(x / exp) % 10]++;
                for (int d = 1; d < 10; d++) count[d] += count[d - 1];
                for (int i = arr.length - 1; i >= 0; i--)        // stable
                    output[--count[(arr[i] / exp) % 10]] = arr[i];
                System.arraycopy(output, 0, arr, 0, arr.length);
            }

            static void radixSort(int[] arr) {
                int mx = 0;
                for (int x : arr) mx = Math.max(mx, x);
                for (int exp = 1; mx / exp > 0; exp *= 10) {     // one pass per digit of the maximum
                    countingSortByDigit(arr, exp);
                    StringBuilder sb = new StringBuilder("after pass exp=" + exp + ":");
                    for (int x : arr) sb.append(' ').append(x);
                    System.out.println(sb);
                }
            }

            public static void main(String[] args) {
                radixSort(new int[]{319, 212, 6, 8, 100, 50});
            }
        }
    ''', js=r'''
        function countingSortByDigit(arr, exp) {
            const output = new Array(arr.length), count = new Array(10).fill(0);
            for (const x of arr) count[Math.floor(x / exp) % 10]++;
            for (let d = 1; d < 10; d++) count[d] += count[d - 1];
            for (let i = arr.length - 1; i >= 0; i--)            // stable
                output[--count[Math.floor(arr[i] / exp) % 10]] = arr[i];
            for (let i = 0; i < arr.length; i++) arr[i] = output[i];
        }

        function radixSort(arr) {
            const mx = Math.max(...arr);
            for (let exp = 1; Math.floor(mx / exp) > 0; exp *= 10) {   // one pass per digit of the maximum
                countingSortByDigit(arr, exp);
                console.log(`after pass exp=${exp}:`, arr.join(" "));
            }
        }

        radixSort([319, 212, 6, 8, 100, 50]);
    ''')
    yield complexity("O(d · (n + b)), b = base", "O(n + b)")
    yield note("**Choosing the base.** With `b = n` (not 10) a number up to `n²` has only `d = 2` “digits”, so radix sort runs in `O(2 · 2n) = O(n)` — this is the “values up to `n²` or `n³`” row of the decision table. Radix sort is not comparison based, is stable, needs `O(n)` extra memory, and extends to negative numbers (offset or sort by sign first), fixed-length strings and floats (by their IEEE bit pattern). The notes' loop condition `mx/exp > 1` was wrong: it skips the final pass when the maximum has a leading digit of 1 (e.g. `mx = 100` would stop after the tens pass); `mx // exp > 0` is correct.")

    # ── bucket sort ───────────────────────────────────────────────────
    yield section("Bucket sort", "bucket")
    yield define("Bucket sort", "**scatter** the elements into `k` buckets by value range, **sort** each bucket (insertion sort or any library sort), then **gather** the buckets in order. Expected `O(n)` when the input is uniformly distributed over the range and `k ≈ n`.")
    yield p("Typical inputs: integers uniformly spread over `1..10⁸` (too wide for counting sort, too many digits for radix), or floating-point numbers uniformly spread in `[0, 1)` where the bucket index is simply `floor(k · x)`.")
    yield io("arr = [20, 88, 70, 85, 75, 95, 18, 82, 60], range 0..99, k = 5 buckets", "18 20 60 70 75 82 85 88 95")
    yield diagram('''
        Scatter (bucket = 5 * x / 100):           Sort each bucket:
          bucket 0 (00-19): 18                       18
          bucket 1 (20-39): 20                       20
          bucket 2 (40-59):                          (empty)
          bucket 3 (60-79): 70 75 60                 60 70 75
          bucket 4 (80-99): 88 85 95 82              82 85 88 95

        Gather: 18 20 60 70 75 82 85 88 95
    ''', "Scatter → sort buckets → gather")
    yield multi('''
        bucket 0: 18
        bucket 1: 20
        bucket 2:
        bucket 3: 70 75 60
        bucket 4: 88 85 95 82
        sorted: 18 20 60 70 75 82 85 88 95
    ''', py=r'''
        def bucket_sort(arr, k):
            rs = max(arr) + 1                          # values lie in [0, rs)
            buckets = [[] for _ in range(k)]
            for x in arr:
                buckets[(k * x) // rs].append(x)       # scatter
            for i, b in enumerate(buckets):
                print(f"bucket {i}:", *b)
            idx = 0
            for b in buckets:
                b.sort()                               # sort each bucket (small → cheap)
                for x in b:                            # gather
                    arr[idx] = x
                    idx += 1

        a = [20, 88, 70, 85, 75, 95, 18, 82, 60]
        bucket_sort(a, 5)
        print("sorted:", *a)
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        void bucketSort(vector<int>& arr, int k) {
            int rs = *max_element(arr.begin(), arr.end()) + 1;   // values lie in [0, rs)
            vector<vector<int>> buckets(k);
            for (int x : arr) buckets[(k * x) / rs].push_back(x);   // scatter
            for (int i = 0; i < k; i++) {
                cout << "bucket " << i << ":";
                for (int x : buckets[i]) cout << " " << x;
                cout << "\n";
            }
            int idx = 0;
            for (auto& b : buckets) {
                sort(b.begin(), b.end());                        // sort each bucket (small → cheap)
                for (int x : b) arr[idx++] = x;                  // gather
            }
        }

        int main() {
            vector<int> a = {20, 88, 70, 85, 75, 95, 18, 82, 60};
            bucketSort(a, 5);
            cout << "sorted:";
            for (int x : a) cout << " " << x;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.Collections;
        import java.util.List;

        public class Main {
            static void bucketSort(int[] arr, int k) {
                int rs = 0;
                for (int x : arr) rs = Math.max(rs, x);
                rs++;                                            // values lie in [0, rs)
                List<List<Integer>> buckets = new ArrayList<>();
                for (int i = 0; i < k; i++) buckets.add(new ArrayList<>());
                for (int x : arr) buckets.get((k * x) / rs).add(x);   // scatter
                for (int i = 0; i < k; i++) {
                    StringBuilder sb = new StringBuilder("bucket " + i + ":");
                    for (int x : buckets.get(i)) sb.append(' ').append(x);
                    System.out.println(sb);
                }
                int idx = 0;
                for (List<Integer> b : buckets) {
                    Collections.sort(b);                         // sort each bucket (small → cheap)
                    for (int x : b) arr[idx++] = x;              // gather
                }
            }

            public static void main(String[] args) {
                int[] a = {20, 88, 70, 85, 75, 95, 18, 82, 60};
                bucketSort(a, 5);
                StringBuilder sb = new StringBuilder("sorted:");
                for (int x : a) sb.append(' ').append(x);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function bucketSort(arr, k) {
            const rs = Math.max(...arr) + 1;               // values lie in [0, rs)
            const buckets = Array.from({ length: k }, () => []);
            for (const x of arr) buckets[Math.floor((k * x) / rs)].push(x);   // scatter
            buckets.forEach((b, i) => console.log(`bucket ${i}:${b.map((x) => " " + x).join("")}`));
            let idx = 0;
            for (const b of buckets) {
                b.sort((x, y) => x - y);                   // sort each bucket (small → cheap)
                for (const x of b) arr[idx++] = x;         // gather
            }
        }

        const a = [20, 88, 70, 85, 75, 95, 18, 82, 60];
        bucketSort(a, 5);
        console.log("sorted:", a.join(" "));
    ''')
    yield complexity("O(n + k) expected, O(n log n) worst", "O(n + k)")
    yield pitfall("Bucket sort degrades to the cost of the inner sort when the data is **skewed** — if every value lands in one bucket you have just paid `O(n)` to run a regular sort. Pick the bucket function from the known distribution, not from hope. The notes' diagram listed `92` in the last bucket although the input contained `82`; the example above is consistent.")

    yield section("Comparison of all sorting algorithms", "table")
    yield table(
        ["Algorithm", "Best", "Average", "Worst", "Space", "Stable", "In place", "Notes"],
        ["Bubble", "`O(n)`", "`O(n²)`", "`O(n²)`", "`O(1)`", "yes", "yes", "adjacent swaps only"],
        ["Selection", "`O(n²)`", "`O(n²)`", "`O(n²)`", "`O(1)`", "no", "yes", "`O(n)` swaps"],
        ["Insertion", "`O(n)`", "`O(n²)`", "`O(n²)`", "`O(1)`", "yes", "yes", "best for small / nearly sorted"],
        ["Merge", "`O(n log n)`", "`O(n log n)`", "`O(n log n)`", "`O(n)`", "yes", "no", "linked lists, external sort"],
        ["Quick (Lomuto/Hoare)", "`O(n log n)`", "`O(n log n)`", "`O(n²)`", "`O(log n)`*", "no", "yes", "fastest in practice; *with smaller-side recursion"],
        ["Heap", "`O(n log n)`", "`O(n log n)`", "`O(n log n)`", "`O(1)`", "no", "yes", "poor cache behaviour"],
        ["Counting", "`Θ(n + k)`", "`Θ(n + k)`", "`Θ(n + k)`", "`O(n + k)`", "yes", "no", "small integer range"],
        ["Radix (LSD)", "`O(d(n + b))`", "`O(d(n + b))`", "`O(d(n + b))`", "`O(n + b)`", "yes", "no", "fixed-width keys"],
        ["Bucket", "`O(n + k)`", "`O(n + k)`", "`O(n log n)`", "`O(n + k)`", "yes*", "no", "uniform data; *if inner sort is stable"],
        ["Cycle", "`O(n²)`", "`O(n²)`", "`O(n²)`", "`O(1)`", "no", "yes", "minimum writes"],
        ["Timsort", "`O(n)`", "`O(n log n)`", "`O(n log n)`", "`O(n)`", "yes", "no", "Python, Java objects, V8"],
        ["Introsort", "`O(n log n)`", "`O(n log n)`", "`O(n log n)`", "`O(log n)`", "no", "yes", "C++ `std::sort`"],
    )
    yield formula("Any comparison sort needs `Ω(n log n)` comparisons in the worst case — counting, radix and bucket sort escape this by not comparing.")

    # ── Q&A ───────────────────────────────────────────────────────────
    yield section("Interview Q&A", "message-question")
    yield qa("Why do libraries use hybrid algorithms instead of plain quick sort or merge sort?",
             "Each pure algorithm has a weakness: quick sort has an `O(n²)` worst case and deep recursion, merge sort needs `O(n)` extra memory and does unnecessary work on already-sorted data, insertion sort is quadratic but unbeatable for tiny arrays. Introsort (quick → heap on deep recursion → insertion on small parts) and Timsort (natural runs + insertion + merge) combine the strengths: guaranteed `O(n log n)`, fast on real data, and — for Timsort — stability plus `O(n)` on sorted input.")
    yield qa("Quickselect vs a heap for the kth smallest — when is each better?",
             "Quickselect: expected `O(n)`, `O(1)` space, but modifies the array and has an `O(n²)` worst case (fix with a random pivot). Min/max heap of size `k`: `O(n log k)`, does not touch the input, works on a stream, and is better when `k` is small or when the data cannot be held in memory. For `k` near `n/2` on in-memory data quickselect wins.")
    yield qa("How can you sort in O(n)? Doesn't the lower bound forbid it?",
             "The `Ω(n log n)` bound applies to **comparison** sorts. Counting, radix and bucket sort use the values themselves (as array indices or digit groups) and never compare two elements. They need extra assumptions — a small range, fixed-width keys, or a uniform distribution — and extra memory.")
    yield qa("Why is the right-to-left scan needed for counting sort to be stable, and why does radix sort need stability?",
             "After prefix sums, `count[v]` is the position *just past* the last slot for value `v`. Scanning the input from the right and decrementing before placing fills each value's slots from the back, so the last occurrence lands last — input order is preserved. Radix sort relies on this: when sorting by the tens digit, elements with equal tens digits must keep the units-digit order produced by the previous pass, otherwise the earlier passes are wasted.")
    yield qa("Explain tail call elimination in quick sort. Does it fix the O(n²) worst case?",
             "No — it fixes the **stack**, not the time. Replacing the second recursive call with a loop and always recursing on the smaller partition bounds the recursion depth by `log₂ n`, so even adversarial input cannot overflow the stack. The number of comparisons on that input is still quadratic; a randomised or median-of-three pivot is what makes the worst case unlikely.")
    yield qa("Minimum number of swaps to sort an array — which sorting idea applies?",
             "Cycle sort. Write each element directly to its sorted position (found by sorting a copy with indices, or by counting smaller elements), following cycles of displacement. Each cycle of length `L` needs `L - 1` swaps, and the total over all cycles is the minimum. For a permutation of `0..n-1` the whole thing is `O(n)`.")
