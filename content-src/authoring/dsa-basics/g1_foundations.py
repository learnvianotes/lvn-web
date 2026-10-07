from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Foundations"


@topic(G, "analysis", "Analysis of Algorithms", "chart-line")
def _():
    yield lead("Before writing a single data structure you need a way to say *how fast* and *how much memory* an algorithm uses without timing it on one particular computer. Asymptotic notation, loop analysis and recurrences are that language — every other topic in these notes ends with a line written in it.")
    yield define("Algorithm analysis", "the process of determining the amount of time (**time complexity**) and memory (**space complexity**) an algorithm needs as a function of its input size `n`, independent of hardware, language or compiler.")

    yield section("Why analyse algorithms?", "bulb")
    yield cards(
        ("Predict before you build", "Count operations on paper and you know whether a solution will finish for `n = 10⁶` before implementing it — no benchmark needed.", "clock"),
        ("Machine-independent", "A faster laptop changes the constant, never the *shape* of the curve. `O(n²)` loses to `O(n log n)` on every machine once `n` is large enough.", "cpu"),
        ("Compare and choose", "Two correct algorithms for the same problem are compared by their order of growth — the standard interview follow-up is always “can you do better?”.", "arrows-sort"),
        ("Common vocabulary", "“Linear”, “logarithmic”, “quadratic” are precise claims about how running time scales, understood by every engineer.", "language"),
    )
    yield p("We count **elementary operations** (comparisons, assignments, arithmetic) rather than seconds, and we care about the **order of growth** — how the count scales when `n` doubles — not the exact number. Constants and lower-order terms are dropped: `3n² + 10n + 7` is simply `O(n²)`.")

    yield section("Asymptotic notation: Big-O, Omega, Theta", "math-function")
    yield p("Asymptotic analysis describes the growth of a function `f(n)` (the operation count) as `n → ∞` by comparing it with a simpler function `g(n)`. Three bounds are used:")
    yield cards(
        ("Big-O — upper bound", "`f(n) = O(g(n))` if there are constants `c > 0` and `n₀` such that `f(n) ≤ c·g(n)` for all `n ≥ n₀`. “It grows **no faster** than `g`.” This is what we usually quote.", "arrow-up"),
        ("Omega — lower bound", "`f(n) = Ω(g(n))` if `f(n) ≥ c·g(n)` for all `n ≥ n₀`. “It grows **at least** as fast as `g`.” Used to prove problems need a minimum amount of work (comparison sorting is `Ω(n log n)`).", "arrow-down"),
        ("Theta — tight bound", "`f(n) = Θ(g(n))` if `c₁·g(n) ≤ f(n) ≤ c₂·g(n)` for all `n ≥ n₀` — both `O` and `Ω` hold. “It grows **exactly** like `g`.”", "equal"),
        cols=3,
    )
    yield formula("f(n) = O(g(n))  ⇔  ∃ c > 0, n₀ : f(n) ≤ c · g(n) for all n ≥ n₀")
    yield example("`f(n) = 3n² + 10n + 7`. For `n ≥ 1`, `10n ≤ 10n²` and `7 ≤ 7n²`, so `f(n) ≤ 20n²` — pick `c = 20`, `n₀ = 1` and `f(n) = O(n²)`. Also `f(n) ≥ 3n²`, so `f(n) = Ω(n²)`, and therefore `f(n) = Θ(n²)`.", "Worked example")
    yield table(
        ["Expression", "Simplified", "Why"],
        ["`5n + 20`", "`O(n)`", "drop the constant factor 5 and the lower-order term 20"],
        ["`n² + n log n`", "`O(n²)`", "`n log n` grows slower than `n²`"],
        ["`2ⁿ + n¹⁰⁰`", "`O(2ⁿ)`", "any exponential eventually beats any polynomial"],
        ["`log₂ n` vs `log₁₀ n`", "both `O(log n)`", "logarithms of different bases differ by a constant factor (`log₂ n = 3.32 · log₁₀ n`)"],
        ["`n + m`", "`O(n + m)`", "two independent sizes stay in the answer — neither can be dropped"],
        ["`100`", "`O(1)`", "constant — does not depend on `n` at all"],
    )
    yield warn("`O`, `Ω`, `Θ` are **bounds on a function**; *best case*, *worst case* and *average case* are **which input** you analyse. They are independent: linear search is `Θ(1)` in the best case and `Θ(n)` in the worst case. When someone says “the algorithm is `O(n²)`” they almost always mean the worst-case running time is `Θ(n²)` — say which case you mean.", "Big-O is not “worst case”")
    yield note("Because `O` is only an upper bound, `n = O(n²)` is technically true — but useless. Always give the **tightest** bound you can prove; that is why `Θ` is the honest answer in a proof and `O` is the everyday shorthand for it.")

    yield section("Big-O growth table", "chart-bar")
    yield p("The classes below cover almost every algorithm you will meet, from fastest to slowest. The right-hand column is the rule of thumb for coding interviews and contests: roughly `10⁸` simple operations run in about a second.")
    yield table(
        ["Class", "Name", "`n = 10`", "`n = 100`", "`n = 1000`", "Largest `n` in ~1 s", "Typical example"],
        ["`O(1)`", "constant", "1", "1", "1", "any", "array index, hash lookup, push/pop"],
        ["`O(log n)`", "logarithmic", "3", "7", "10", "any", "binary search, balanced BST operations"],
        ["`O(√n)`", "square root", "3", "10", "32", "`10¹⁶`", "trial-division primality test"],
        ["`O(n)`", "linear", "10", "100", "1 000", "`10⁸`", "linear search, one pass over an array"],
        ["`O(n log n)`", "linearithmic", "33", "664", "9 966", "`5·10⁶`", "merge sort, heap sort, sorting then scanning"],
        ["`O(n²)`", "quadratic", "100", "10⁴", "10⁶", "`10⁴`", "bubble/insertion sort, all pairs"],
        ["`O(n³)`", "cubic", "1 000", "10⁶", "10⁹", "`500`", "naive matrix multiplication, Floyd–Warshall"],
        ["`O(2ⁿ)`", "exponential", "1 024", "1.3·10³⁰", "10³⁰¹", "`25`", "all subsets, naive recursion with two branches"],
        ["`O(n!)`", "factorial", "3.6·10⁶", "9·10¹⁵⁷", "—", "`11`", "all permutations, brute-force TSP"],
    )
    yield diagram('''
        O(1) < O(log n) < O(√n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!)
        ───────────────────────────────▶ slower growth, smaller feasible n
    ''', "Order of growth, fastest to slowest")
    yield pitfall("Big-O hides constants, so for *small* `n` a “worse” algorithm can win: insertion sort (`O(n²)`) beats merge sort on arrays of 10–20 elements, which is exactly why library sorts switch to it for tiny sub-arrays. Big-O tells you what happens as `n` grows, not which program is faster on your input.")

    yield section("How to analyse a loop", "list-numbers")
    yield p("Almost all non-recursive analysis reduces to one question per loop: **how many times does the body run as a function of `n`?** Then combine the loops with two rules.")
    yield steps(
        ("Find the loop variable's path", "Write down its start value, its stop condition and how it changes per iteration (`+1`, `+k`, `×2`, squared…)."),
        ("Solve for the iteration count", "`i = 0, 1, 2, … n−1` → `n` iterations. `i = n, n−k, n−2k…` → `n/k`. `i = 1, 2, 4, 8 … n` → `log₂ n`. `i = 2, 2², 2⁴, 2⁸ … n` → `log log n`."),
        ("Nested loops multiply", "If the inner loop runs `g(n)` times for each of `f(n)` outer iterations, the total is `f(n) · g(n)`. When the inner count depends on `i`, **sum** it: `Σ i` for `i = 1..n` is `n(n+1)/2 = Θ(n²)`."),
        ("Sequential loops add", "Loop A then loop B costs `A + B`; keep only the dominant term (`n² + n = O(n²)`), but keep both when sizes are independent (`O(n + m)`)."),
        ("Charge the body", "Multiply the iteration count by the cost of the body. A body that itself calls an `O(log n)` function inside an `O(n)` loop gives `O(n log n)`."),
        ("Drop constants and lower-order terms", "`3n + 5 → O(n)`; `n²/2 + n → O(n²)`. Keep the tightest class that remains."),
    )
    yield table(
        ["Loop variable moves…", "Example", "Iterations", "Class"],
        ["by a constant (`+1`, `−1`)", "`for i in range(n)`", "`n`", "`O(n)`"],
        ["by a constant `k`", "`while x >= b: x -= b`", "`n / k`", "`O(n)` — the `1/k` is a constant"],
        ["multiplied / divided by `c`", "`while x < n: x *= c`", "`log_c n`", "`O(log n)`"],
        ["raised to a power `c`", "`while x < n: x = x ** c`", "`log log n`", "`O(log log n)`"],
        ["inner loop `0..n` for every outer `0..n`", "`for i … for j …`", "`n · n`", "`O(n²)`"],
        ["inner loop `i..n` (triangle)", "`for i … for j in range(i, n)`", "`n(n+1)/2`", "`O(n²)` — half the square is still a square"],
        ["inner loop doubles", "`for i … j = 1; while j <= n: j *= 2`", "`n · log n`", "`O(n log n)`"],
    )

    yield section("Loop pattern: linear and fractional increments", "arrows-right")
    yield p("The learner's original four examples are kept here, instrumented to **print their iteration count** so the complexity is visible. `add` decrements `b` by one per iteration, so it runs `b` times — `O(b)`. `subtract` removes `b` from `a` per iteration, so it runs `a / b` times — still linear in `a` for a fixed `b`, because `1/b` is a constant factor.")
    yield multi('''
        add(5, 7) = 12 after 7 iterations
        add(5, 70) = 75 after 70 iterations
        subtract(100, 10) = 10 after 10 iterations
        subtract(1000, 10) = 100 after 100 iterations
    ''', py='''
        def add(a, b):              # result += 1 while b counts down: O(b)
            result, steps = a, 0
            while b > 0:
                result += 1
                b -= 1
                steps += 1
            return result, steps

        def subtract(a, b):         # how many times does b fit in a? O(a / b)
            count, steps = 0, 0
            while a >= b:
                a -= b
                count += 1
                steps += 1
            return count, steps

        for a, b in [(5, 7), (5, 70)]:
            r, s = add(a, b)
            print(f"add({a}, {b}) = {r} after {s} iterations")
        for a, b in [(100, 10), (1000, 10)]:
            r, s = subtract(a, b)
            print(f"subtract({a}, {b}) = {r} after {s} iterations")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int steps;                          // iteration counter shared by both functions

        int add(int a, int b) {             // result += 1 while b counts down: O(b)
            int result = a;
            steps = 0;
            while (b > 0) { result++; b--; steps++; }
            return result;
        }

        int subtract(int a, int b) {        // how many times does b fit in a? O(a / b)
            int count = 0;
            steps = 0;
            while (a >= b) { a -= b; count++; steps++; }
            return count;
        }

        int main() {
            int adds[2][2] = {{5, 7}, {5, 70}};
            for (auto& ab : adds) {
                int r = add(ab[0], ab[1]);
                cout << "add(" << ab[0] << ", " << ab[1] << ") = " << r << " after " << steps << " iterations\n";
            }
            int subs[2][2] = {{100, 10}, {1000, 10}};
            for (auto& ab : subs) {
                int r = subtract(ab[0], ab[1]);
                cout << "subtract(" << ab[0] << ", " << ab[1] << ") = " << r << " after " << steps << " iterations\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int steps;                       // iteration counter shared by both functions

            static int add(int a, int b) {          // result += 1 while b counts down: O(b)
                int result = a;
                steps = 0;
                while (b > 0) { result++; b--; steps++; }
                return result;
            }

            static int subtract(int a, int b) {     // how many times does b fit in a? O(a / b)
                int count = 0;
                steps = 0;
                while (a >= b) { a -= b; count++; steps++; }
                return count;
            }

            public static void main(String[] args) {
                int[][] adds = {{5, 7}, {5, 70}};
                for (int[] ab : adds) {
                    int r = add(ab[0], ab[1]);
                    System.out.println("add(" + ab[0] + ", " + ab[1] + ") = " + r + " after " + steps + " iterations");
                }
                int[][] subs = {{100, 10}, {1000, 10}};
                for (int[] ab : subs) {
                    int r = subtract(ab[0], ab[1]);
                    System.out.println("subtract(" + ab[0] + ", " + ab[1] + ") = " + r + " after " + steps + " iterations");
                }
            }
        }
    ''', js=r'''
        function add(a, b) {                // result += 1 while b counts down: O(b)
            let result = a, steps = 0;
            while (b > 0) { result++; b--; steps++; }
            return [result, steps];
        }

        function subtract(a, b) {           // how many times does b fit in a? O(a / b)
            let count = 0, steps = 0;
            while (a >= b) { a -= b; count++; steps++; }
            return [count, steps];
        }

        for (const [a, b] of [[5, 7], [5, 70]]) {
            const [r, s] = add(a, b);
            console.log(`add(${a}, ${b}) = ${r} after ${s} iterations`);
        }
        for (const [a, b] of [[100, 10], [1000, 10]]) {
            const [r, s] = subtract(a, b);
            console.log(`subtract(${a}, ${b}) = ${r} after ${s} iterations`);
        }
    ''')
    yield complexity("O(n) — n iterations, or n/k for a step of k", "O(1)")
    yield note("Ten times the input → ten times the iterations: that proportionality **is** linear time. `subtract(1000, 10)` runs 100 times, not 1000, but the `1/10` is a constant and disappears in Big-O.")

    yield section("Loop pattern: logarithmic and log-log scaling", "trending-up")
    yield p("When the loop variable is **multiplied** by a constant `c` each round, it reaches `n` after `log_c n` rounds — a thousandfold larger input adds only a handful of iterations. When the variable is **raised to a power** each round (`2 → 4 → 16 → 256 → 65536`), the exponent itself doubles, so the loop runs `log log n` times — practically constant.")
    yield multi('''
        multiply(1000, 10) = 1000 after 3 iterations
        multiply(1024, 2) = 1024 after 10 iterations
        multiply(1000000, 2) = 1048576 after 20 iterations
        exponent(65536, 2) = 65536 after 4 iterations
        exponent(1000000000, 2) = 4294967296 after 5 iterations
    ''', py='''
        def multiply(n, c):          # result *= c until it reaches n: log_c(n) iterations
            result, steps = 1, 0
            while result < n:
                result *= c
                steps += 1
            return result, steps

        def exponent(n, c):          # result = result ** c: the exponent doubles each time → log log n
            result, steps = 2, 0
            while result < n:
                result = result ** c
                steps += 1
            return result, steps

        for n, c in [(1000, 10), (1024, 2), (1000000, 2)]:
            r, s = multiply(n, c)
            print(f"multiply({n}, {c}) = {r} after {s} iterations")
        for n, c in [(65536, 2), (1000000000, 2)]:
            r, s = exponent(n, c)
            print(f"exponent({n}, {c}) = {r} after {s} iterations")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int steps;

        long long multiply(long long n, long long c) {   // result *= c until it reaches n: log_c(n)
            long long result = 1;
            steps = 0;
            while (result < n) { result *= c; steps++; }
            return result;
        }

        long long ipow(long long base, long long e) {    // integer power for the log-log loop
            long long r = 1;
            for (long long i = 0; i < e; i++) r *= base;
            return r;
        }

        long long exponent(long long n, long long c) {   // result = result^c: exponent doubles → log log n
            long long result = 2;
            steps = 0;
            while (result < n) { result = ipow(result, c); steps++; }
            return result;
        }

        int main() {
            long long m[3][2] = {{1000, 10}, {1024, 2}, {1000000, 2}};
            for (auto& nc : m) {
                long long r = multiply(nc[0], nc[1]);
                cout << "multiply(" << nc[0] << ", " << nc[1] << ") = " << r << " after " << steps << " iterations\n";
            }
            long long e[2][2] = {{65536, 2}, {1000000000, 2}};
            for (auto& nc : e) {
                long long r = exponent(nc[0], nc[1]);
                cout << "exponent(" << nc[0] << ", " << nc[1] << ") = " << r << " after " << steps << " iterations\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int steps;

            static long multiply(long n, long c) {     // result *= c until it reaches n: log_c(n)
                long result = 1;
                steps = 0;
                while (result < n) { result *= c; steps++; }
                return result;
            }

            static long ipow(long base, long e) {      // integer power for the log-log loop
                long r = 1;
                for (long i = 0; i < e; i++) r *= base;
                return r;
            }

            static long exponent(long n, long c) {     // result = result^c: exponent doubles → log log n
                long result = 2;
                steps = 0;
                while (result < n) { result = ipow(result, c); steps++; }
                return result;
            }

            public static void main(String[] args) {
                long[][] m = {{1000, 10}, {1024, 2}, {1000000, 2}};
                for (long[] nc : m) {
                    long r = multiply(nc[0], nc[1]);
                    System.out.println("multiply(" + nc[0] + ", " + nc[1] + ") = " + r + " after " + steps + " iterations");
                }
                long[][] e = {{65536, 2}, {1000000000L, 2}};
                for (long[] nc : e) {
                    long r = exponent(nc[0], nc[1]);
                    System.out.println("exponent(" + nc[0] + ", " + nc[1] + ") = " + r + " after " + steps + " iterations");
                }
            }
        }
    ''', js=r'''
        function multiply(n, c) {        // result *= c until it reaches n: log_c(n) iterations
            let result = 1, steps = 0;
            while (result < n) { result *= c; steps++; }
            return [result, steps];
        }

        function exponent(n, c) {        // result = result ** c: exponent doubles each time → log log n
            let result = 2, steps = 0;
            while (result < n) { result = result ** c; steps++; }
            return [result, steps];
        }

        for (const [n, c] of [[1000, 10], [1024, 2], [1000000, 2]]) {
            const [r, s] = multiply(n, c);
            console.log(`multiply(${n}, ${c}) = ${r} after ${s} iterations`);
        }
        for (const [n, c] of [[65536, 2], [1000000000, 2]]) {
            const [r, s] = exponent(n, c);
            console.log(`exponent(${n}, ${c}) = ${r} after ${s} iterations`);
        }
    ''')
    yield complexity("O(log n) for multiply, O(log log n) for exponent", "O(1)")
    yield note("`multiply(1000000, 2)` needs only 20 rounds and `exponent(10⁹, 2)` only 5. Whenever you see a loop variable that *halves* or *doubles* — binary search, heap sift, exponentiation by squaring — think `log n`.")

    yield section("Loop pattern: nested and sequential loops", "layout-grid")
    yield p("Nested loops **multiply**; loops one after another **add**. The program below counts the body executions of three classic nestings for `n = 8` so you can match each count to its formula.")
    yield multi('''
        n = 8
        square (i in 0..n, j in 0..n): 64 = n*n
        triangle (i in 0..n, j in i..n): 36 = n(n+1)/2
        doubling (i in 0..n, j = 1,2,4..n): 32 = n * (log2 n + 1)
        sequential (loop n then loop n): 16 = 2n
    ''', py='''
        n = 8

        square = 0
        for i in range(n):
            for j in range(n):           # inner runs n times for each of n outer → n²
                square += 1

        triangle = 0
        for i in range(n):
            for j in range(i, n):        # inner runs n-i times: n + (n-1) + … + 1 = n(n+1)/2
                triangle += 1

        doubling = 0
        for i in range(n):
            j = 1
            while j <= n:                # inner doubles: log2(n) + 1 rounds → n log n
                doubling += 1
                j *= 2

        sequential = 0
        for i in range(n):               # one loop then another: n + n = 2n → O(n)
            sequential += 1
        for i in range(n):
            sequential += 1

        print("n =", n)
        print(f"square (i in 0..n, j in 0..n): {square} = n*n")
        print(f"triangle (i in 0..n, j in i..n): {triangle} = n(n+1)/2")
        print(f"doubling (i in 0..n, j = 1,2,4..n): {doubling} = n * (log2 n + 1)")
        print(f"sequential (loop n then loop n): {sequential} = 2n")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int main() {
            int n = 8;

            int square = 0;
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++) square++;          // n * n

            int triangle = 0;
            for (int i = 0; i < n; i++)
                for (int j = i; j < n; j++) triangle++;        // n + (n-1) + … + 1 = n(n+1)/2

            int doubling = 0;
            for (int i = 0; i < n; i++)
                for (int j = 1; j <= n; j *= 2) doubling++;    // inner doubles: log2(n) + 1 rounds

            int sequential = 0;
            for (int i = 0; i < n; i++) sequential++;          // n + n = 2n → O(n)
            for (int i = 0; i < n; i++) sequential++;

            cout << "n = " << n << "\n";
            cout << "square (i in 0..n, j in 0..n): " << square << " = n*n\n";
            cout << "triangle (i in 0..n, j in i..n): " << triangle << " = n(n+1)/2\n";
            cout << "doubling (i in 0..n, j = 1,2,4..n): " << doubling << " = n * (log2 n + 1)\n";
            cout << "sequential (loop n then loop n): " << sequential << " = 2n\n";
        }
    ''', java=r'''
        public class Main {
            public static void main(String[] args) {
                int n = 8;

                int square = 0;
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < n; j++) square++;          // n * n

                int triangle = 0;
                for (int i = 0; i < n; i++)
                    for (int j = i; j < n; j++) triangle++;        // n + (n-1) + … + 1 = n(n+1)/2

                int doubling = 0;
                for (int i = 0; i < n; i++)
                    for (int j = 1; j <= n; j *= 2) doubling++;    // inner doubles: log2(n) + 1 rounds

                int sequential = 0;
                for (int i = 0; i < n; i++) sequential++;          // n + n = 2n → O(n)
                for (int i = 0; i < n; i++) sequential++;

                System.out.println("n = " + n);
                System.out.println("square (i in 0..n, j in 0..n): " + square + " = n*n");
                System.out.println("triangle (i in 0..n, j in i..n): " + triangle + " = n(n+1)/2");
                System.out.println("doubling (i in 0..n, j = 1,2,4..n): " + doubling + " = n * (log2 n + 1)");
                System.out.println("sequential (loop n then loop n): " + sequential + " = 2n");
            }
        }
    ''', js=r'''
        const n = 8;

        let square = 0;
        for (let i = 0; i < n; i++)
            for (let j = 0; j < n; j++) square++;          // n * n

        let triangle = 0;
        for (let i = 0; i < n; i++)
            for (let j = i; j < n; j++) triangle++;        // n + (n-1) + … + 1 = n(n+1)/2

        let doubling = 0;
        for (let i = 0; i < n; i++)
            for (let j = 1; j <= n; j *= 2) doubling++;    // inner doubles: log2(n) + 1 rounds

        let sequential = 0;
        for (let i = 0; i < n; i++) sequential++;          // n + n = 2n → O(n)
        for (let i = 0; i < n; i++) sequential++;

        console.log("n =", n);
        console.log(`square (i in 0..n, j in 0..n): ${square} = n*n`);
        console.log(`triangle (i in 0..n, j in i..n): ${triangle} = n(n+1)/2`);
        console.log(`doubling (i in 0..n, j = 1,2,4..n): ${doubling} = n * (log2 n + 1)`);
        console.log(`sequential (loop n then loop n): ${sequential} = 2n`);
    ''')
    yield complexity("O(n²), O(n²), O(n log n), O(n) respectively", "O(1)")
    yield pitfall("“The inner loop starts at `i`, so it is only half the work — `O(n²/2)`, which is better.” It is not: `n²/2` is `Θ(n²)`. Halving a quadratic leaves a quadratic; only a change in the *shape* (e.g. doubling instead of incrementing) changes the class.")

    yield section("Recurrence relations for recursive algorithms", "repeat")
    yield p("A recursive algorithm's running time is defined in terms of itself: the cost of the current call plus the cost of the recursive calls it makes. Writing that down gives a **recurrence relation**; solving it gives the complexity.")
    yield define("Recurrence relation", "an equation that expresses `T(n)`, the time for input size `n`, in terms of `T` on smaller inputs plus the work done outside the recursive calls, with a base case such as `T(1) = Θ(1)`. Example: merge sort is `T(n) = 2T(n/2) + Θ(n)`.")
    yield table(
        ["Algorithm", "Recurrence", "What it says", "Solution"],
        ["Linear recursion (sum of `n` numbers, factorial)", "`T(n) = T(n−1) + Θ(1)`", "one call of size `n−1`, constant work", "`Θ(n)`"],
        ["Binary search", "`T(n) = T(n/2) + Θ(1)`", "one call on half the input", "`Θ(log n)`"],
        ["Merge sort", "`T(n) = 2T(n/2) + Θ(n)`", "two halves plus a linear merge", "`Θ(n log n)`"],
        ["Selection sort written recursively", "`T(n) = T(n−1) + Θ(n)`", "one smaller call plus a linear scan", "`Θ(n²)`"],
        ["Tower of Hanoi", "`T(n) = 2T(n−1) + Θ(1)`", "two calls on `n−1` discs", "`Θ(2ⁿ)`"],
        ["Naive Fibonacci", "`T(n) = T(n−1) + T(n−2) + Θ(1)`", "two calls, barely smaller", "`Θ(φⁿ) ≈ Θ(1.618ⁿ)`"],
        ["Strassen matrix multiply", "`T(n) = 7T(n/2) + Θ(n²)`", "seven half-size products", "`Θ(n^log₂7) ≈ Θ(n^2.81)`"],
    )
    yield p("Three methods solve a recurrence:")
    yield cards(
        ("Substitution method", "**Guess** the answer (e.g. `T(n) = O(n log n)`), then prove it by induction: assume it holds for all smaller sizes, substitute into the recurrence, and show it still holds for `n`. Rigorous but needs a good guess.", "pencil"),
        ("Recursion tree method", "**Draw** the calls as a tree. Write the non-recursive work at every node, sum each level, then sum the levels. It makes the guess for substitution obvious and is the way to *see* why merge sort is `n log n`.", "binary-tree"),
        ("Master method", "A **template** for `T(n) = aT(n/b) + f(n)`: compare `f(n)` with `n^(log_b a)` and read off the answer. Covers most divide-and-conquer algorithms in one line.", "bolt"),
        cols=3,
    )

    yield section("Recursion tree: why merge sort is n log n", "binary-tree")
    yield p("For `T(n) = 2T(n/2) + n` every level of the tree does `n` work in total — the input is split in half but there are twice as many pieces. There are `log₂ n` levels of splitting plus the leaves, so the total is `n · (log₂ n + 1) = Θ(n log n)`.")
    yield diagram('''
        level 0:                 n                       work: n
                              /     \\
        level 1:          n/2         n/2                work: 2 · n/2  = n
                         /   \\       /   \\
        level 2:       n/4   n/4   n/4   n/4             work: 4 · n/4  = n
                        …     …     …     …
        level log n:   1  1  1  1  1  1  1  1   (n leaves)  work: n · 1 = n
                                                          ─────────────────
                                              total: n · (log₂ n + 1) = Θ(n log n)
    ''', "Recursion tree of T(n) = 2T(n/2) + n")
    yield p("The program below evaluates that recurrence exactly for powers of two and prints the total next to the closed form — the two columns agree at every size.")
    yield multi('''
        n = 1: T(n) = 1, n*(log2 n + 1) = 1
        n = 2: T(n) = 4, n*(log2 n + 1) = 4
        n = 4: T(n) = 12, n*(log2 n + 1) = 12
        n = 8: T(n) = 32, n*(log2 n + 1) = 32
        n = 16: T(n) = 80, n*(log2 n + 1) = 80
        n = 1024: T(n) = 11264, n*(log2 n + 1) = 11264
    ''', py='''
        def T(n):                        # T(n) = 2 T(n/2) + n, T(1) = 1
            if n == 1:
                return 1
            return 2 * T(n // 2) + n

        def closed(n):                   # n * (log2 n + 1)
            log2 = 0
            while (1 << log2) < n:
                log2 += 1
            return n * (log2 + 1)

        for n in [1, 2, 4, 8, 16, 1024]:
            print(f"n = {n}: T(n) = {T(n)}, n*(log2 n + 1) = {closed(n)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long T(long long n) {               // T(n) = 2 T(n/2) + n, T(1) = 1
            if (n == 1) return 1;
            return 2 * T(n / 2) + n;
        }

        long long closed(long long n) {          // n * (log2 n + 1)
            int log2 = 0;
            while ((1LL << log2) < n) log2++;
            return n * (log2 + 1);
        }

        int main() {
            for (long long n : {1, 2, 4, 8, 16, 1024})
                cout << "n = " << n << ": T(n) = " << T(n) << ", n*(log2 n + 1) = " << closed(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static long T(long n) {                  // T(n) = 2 T(n/2) + n, T(1) = 1
                if (n == 1) return 1;
                return 2 * T(n / 2) + n;
            }

            static long closed(long n) {             // n * (log2 n + 1)
                int log2 = 0;
                while ((1L << log2) < n) log2++;
                return n * (log2 + 1);
            }

            public static void main(String[] args) {
                for (long n : new long[]{1, 2, 4, 8, 16, 1024})
                    System.out.println("n = " + n + ": T(n) = " + T(n) + ", n*(log2 n + 1) = " + closed(n));
            }
        }
    ''', js=r'''
        function T(n) {                          // T(n) = 2 T(n/2) + n, T(1) = 1
            if (n === 1) return 1;
            return 2 * T(Math.floor(n / 2)) + n;
        }

        function closed(n) {                     // n * (log2 n + 1)
            let log2 = 0;
            while ((1 << log2) < n) log2++;
            return n * (log2 + 1);
        }

        for (const n of [1, 2, 4, 8, 16, 1024])
            console.log(`n = ${n}: T(n) = ${T(n)}, n*(log2 n + 1) = ${closed(n)}`);
    ''')
    yield complexity("Θ(n log n) — the recurrence's solution", "O(log n) recursion depth")

    yield section("Master theorem", "bolt")
    yield p("For divide-and-conquer recurrences of the form `T(n) = a·T(n/b) + f(n)` with `a ≥ 1` subproblems each of size `n/b` (`b > 1`), the answer depends on which wins: the leaves (`n^(log_b a)` of them, each `Θ(1)`) or the root's work `f(n)`.")
    yield formula("T(n) = a · T(n / b) + f(n)   —   compare f(n) with n^(log_b a)")
    yield table(
        ["Case", "Condition", "Meaning", "Result"],
        ["1 — leaves dominate", "`f(n) = O(n^(log_b a − ε))` for some `ε > 0`", "`f(n)` is polynomially *smaller* than `n^(log_b a)`", "`T(n) = Θ(n^(log_b a))`"],
        ["2 — balanced", "`f(n) = Θ(n^(log_b a))`", "every level does the same work; there are `log n` levels", "`T(n) = Θ(n^(log_b a) · log n)`"],
        ["3 — root dominates", "`f(n) = Ω(n^(log_b a + ε))` and `a·f(n/b) ≤ c·f(n)` for some `c < 1`", "`f(n)` is polynomially *larger*; the top call does most of the work", "`T(n) = Θ(f(n))`"],
    )
    yield table(
        ["Recurrence", "`a`, `b`", "`n^(log_b a)`", "`f(n)`", "Case", "Solution"],
        ["`T(n) = 2T(n/2) + n` (merge sort)", "2, 2", "`n¹`", "`n`", "2", "`Θ(n log n)`"],
        ["`T(n) = T(n/2) + 1` (binary search)", "1, 2", "`n⁰ = 1`", "`1`", "2", "`Θ(log n)`"],
        ["`T(n) = 4T(n/2) + n`", "4, 2", "`n²`", "`n`", "1", "`Θ(n²)`"],
        ["`T(n) = 8T(n/2) + n²` (naive matrix multiply)", "8, 2", "`n³`", "`n²`", "1", "`Θ(n³)`"],
        ["`T(n) = 7T(n/2) + n²` (Strassen)", "7, 2", "`n^2.81`", "`n²`", "1", "`Θ(n^log₂7)`"],
        ["`T(n) = 2T(n/2) + n²`", "2, 2", "`n`", "`n²`", "3", "`Θ(n²)`"],
        ["`T(n) = T(n/2) + n`", "1, 2", "`1`", "`n`", "3", "`Θ(n)`"],
        ["`T(n) = 2T(n/2) + n log n`", "2, 2", "`n`", "`n log n`", "none — not polynomially larger", "`Θ(n log² n)` (extended form)"],
    )
    yield steps(
        ("Identify `a`, `b`, `f(n)`", "`a` = number of recursive calls, `b` = the factor the input shrinks by, `f(n)` = the work done outside the calls (splitting, merging, scanning)."),
        ("Compute the critical exponent", "`p = log_b a`. Examples: `a = 2, b = 2 → p = 1`; `a = 4, b = 2 → p = 2`; `a = 1, b = 2 → p = 0`."),
        ("Compare `f(n)` with `n^p`", "Smaller by a polynomial factor → case 1. Equal → case 2. Larger by a polynomial factor → case 3 (check regularity)."),
        ("Read off `T(n)`", "`Θ(n^p)`, `Θ(n^p log n)` or `Θ(f(n))`."),
    )
    yield warn("The master theorem does **not** apply when the sub-problems are not of size `n/b` (`T(n) = T(n−1) + …` — use the recursion tree or unroll by hand), when `a < 1`, or when `f(n)` differs from `n^(log_b a)` by less than a polynomial factor (`n log n` vs `n` is only a `log` apart — a gap between cases 2 and 3). `T(n) = 2T(n/2) + n log n` is the standard trap.", "When it does not apply")

    yield section("Space complexity vs auxiliary space", "database")
    yield table(
        ["Term", "What is counted", "Example: sum an array of `n` numbers iteratively"],
        ["**Space complexity**", "all memory the algorithm needs — the input itself **plus** any extra", "`O(n)` — the array has to be there"],
        ["**Auxiliary space**", "only the **extra** memory beyond the input: temporaries, new arrays, hash maps, the recursion stack", "`O(1)` — one accumulator"],
    )
    yield p("Interviewers nearly always mean **auxiliary space** when they ask “what is the space complexity?”, because it is what distinguishes solutions: sorting in place is `O(1)` auxiliary, merge sort's buffer is `O(n)`, and a recursive solution pays for its call stack. Recursion is the classic hidden cost — each pending call keeps a frame alive until it returns.")
    yield io("n = 5", "sum = 15, deepest call stack = 6 frames (n + 1: the base-case call add_recursion(0) is a frame too)")
    yield multi('''
        add_recursion(5) = 15, max depth = 6
        add_recursion(50) = 1275, max depth = 51
        add_iterative(50) = 1275, extra variables = 2
    ''', py='''
        depth = 0
        max_depth = 0

        def add_recursion(n):            # each pending call holds a frame: O(n) auxiliary space
            global depth, max_depth
            depth += 1
            max_depth = max(max_depth, depth)
            result = 0 if n <= 0 else n + add_recursion(n - 1)
            depth -= 1
            return result

        def add_iterative(n):            # a counter and an accumulator: O(1) auxiliary space
            total = 0
            for i in range(1, n + 1):
                total += i
            return total

        for n in (5, 50):
            max_depth = 0
            print(f"add_recursion({n}) = {add_recursion(n)}, max depth = {max_depth}")
        print(f"add_iterative(50) = {add_iterative(50)}, extra variables = 2")
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        using namespace std;

        int depth = 0, maxDepth = 0;

        int addRecursion(int n) {            // each pending call holds a frame: O(n) auxiliary space
            depth++;
            maxDepth = max(maxDepth, depth);
            int result = n <= 0 ? 0 : n + addRecursion(n - 1);
            depth--;
            return result;
        }

        int addIterative(int n) {            // a counter and an accumulator: O(1) auxiliary space
            int total = 0;
            for (int i = 1; i <= n; i++) total += i;
            return total;
        }

        int main() {
            for (int n : {5, 50}) {
                maxDepth = 0;
                int r = addRecursion(n);
                cout << "add_recursion(" << n << ") = " << r << ", max depth = " << maxDepth << "\n";
            }
            cout << "add_iterative(50) = " << addIterative(50) << ", extra variables = 2\n";
        }
    ''', java=r'''
        public class Main {
            static int depth = 0, maxDepth = 0;

            static int addRecursion(int n) {         // each pending call holds a frame: O(n) auxiliary space
                depth++;
                maxDepth = Math.max(maxDepth, depth);
                int result = n <= 0 ? 0 : n + addRecursion(n - 1);
                depth--;
                return result;
            }

            static int addIterative(int n) {         // a counter and an accumulator: O(1) auxiliary space
                int total = 0;
                for (int i = 1; i <= n; i++) total += i;
                return total;
            }

            public static void main(String[] args) {
                for (int n : new int[]{5, 50}) {
                    maxDepth = 0;
                    int r = addRecursion(n);
                    System.out.println("add_recursion(" + n + ") = " + r + ", max depth = " + maxDepth);
                }
                System.out.println("add_iterative(50) = " + addIterative(50) + ", extra variables = 2");
            }
        }
    ''', js=r'''
        let depth = 0, maxDepth = 0;

        function addRecursion(n) {           // each pending call holds a frame: O(n) auxiliary space
            depth++;
            maxDepth = Math.max(maxDepth, depth);
            const result = n <= 0 ? 0 : n + addRecursion(n - 1);
            depth--;
            return result;
        }

        function addIterative(n) {           // a counter and an accumulator: O(1) auxiliary space
            let total = 0;
            for (let i = 1; i <= n; i++) total += i;
            return total;
        }

        for (const n of [5, 50]) {
            maxDepth = 0;
            const r = addRecursion(n);
            console.log(`add_recursion(${n}) = ${r}, max depth = ${maxDepth}`);
        }
        console.log(`add_iterative(50) = ${addIterative(50)}, extra variables = 2`);
    ''')
    yield complexity("O(n) time for both", "O(n) auxiliary (recursive) vs O(1) (iterative)")
    yield pitfall("Counting the recursion stack is the step most people forget: the recursive sum *looks* like it uses no memory, yet `n + 1` frames are alive at the deepest point. Python stops at about 1000 frames with `RecursionError`; C++ and Java crash with a stack overflow a few thousand frames later. Depth, not the number of calls, is what costs space — a function that makes `2ⁿ` calls but is never more than `n` deep uses `O(n)` stack.")

    yield section("Interview Q&A", "message-question")
    yield qa("What is the difference between Big-O, Big-Omega and Big-Theta?",
             "`O(g)` is an upper bound (grows no faster than `g`), `Ω(g)` a lower bound (grows at least as fast), `Θ(g)` a tight bound (both). All three are statements about a function's growth, not about best or worst case. In everyday use “`O(n log n)`” is shorthand for “the worst case is `Θ(n log n)`”.")
    yield qa("Why do we ignore constants and lower-order terms?",
             "Because they depend on the machine, the compiler and the exact operation mix — and because for large `n` they do not change which algorithm wins: `100n` beats `n²` as soon as `n > 100`. Asymptotic notation captures what survives all those details: the shape of the growth curve. Constants still matter when choosing between two algorithms of the *same* class.")
    yield qa("Can an O(n²) algorithm be faster than an O(n log n) one?",
             "Yes, for small inputs or when the constant factors differ a lot. Insertion sort beats merge sort below roughly 20 elements, which is why production sorts (Timsort, introsort) switch to it for small sub-arrays. Big-O describes behaviour as `n → ∞`, not the timing of a particular run.")
    yield qa("How do you find the time complexity of nested loops?",
             "Count the body executions: multiply independent loop counts (`n × n = n²`), sum dependent ones (`Σ (n − i) = n(n+1)/2 = Θ(n²)`), and multiply by the body's own cost. Watch the increment: `i += 1` gives `n`, `i *= 2` gives `log n`, `i = i²` gives `log log n`.")
    yield qa("What is the master theorem and when can you not use it?",
             "For `T(n) = aT(n/b) + f(n)` it compares `f(n)` with `n^(log_b a)`: polynomially smaller → `Θ(n^(log_b a))`; equal → `Θ(n^(log_b a) log n)`; polynomially larger (with the regularity condition) → `Θ(f(n))`. It does not apply to subtract-and-conquer recurrences like `T(n−1)`, to `a < 1`, or when `f(n)` and `n^(log_b a)` differ by only a logarithmic factor (`2T(n/2) + n log n`), which needs the extended version or a recursion tree.")
    yield qa("What is the difference between space complexity and auxiliary space?",
             "Space complexity counts everything including the input; auxiliary space counts only the extra memory the algorithm allocates — temporaries, new containers and the recursion stack. Interviewers mean auxiliary space: an in-place sort is `O(1)`, merge sort is `O(n)`, and a recursive function is at least `O(depth)`.")
    yield qa("What is amortised analysis?",
             "Averaging the cost of an operation over a long sequence rather than looking at the worst single call. Appending to a dynamic array occasionally costs `O(n)` to resize, but doubling the capacity makes the total for `n` appends `O(n)`, so each append is **amortised** `O(1)`. It is a guarantee about the sequence, not a probability — unlike average-case analysis.")


@topic(G, "math", "Mathematics", "math-function")
def _():
    yield lead("A dozen small number problems — digits, divisors, primes, GCD, powers — that every later topic quietly relies on. Each one has an obvious loop and a better idea; learning to see the better idea (`√n`, Euclid, the sieve, squaring) is the real lesson.")
    yield define("Number-theory basics for DSA", "the handful of facts about integers that recur in algorithm problems: digits come off with `% 10` and `// 10`; divisors come in pairs around `√n`; `gcd(a, b) = gcd(b, a mod b)`; the primes up to `n` can all be found in `O(n log log n)`; `xⁿ` needs only `O(log n)` multiplications.")
    yield table(
        ["Problem", "Naive", "Better idea", "Time"],
        ["Sum of `1..n`", "loop", "`n(n+1)/2`", "`O(1)`"],
        ["Count digits", "convert to string", "repeat `n //= 10`", "`O(d)`, `d` = digits"],
        ["Palindrome number", "string reverse", "build the reversed number", "`O(d)`"],
        ["Factorial", "—", "loop or recursion", "`O(n)`"],
        ["Trailing zeros of `n!`", "compute `n!`", "count factors of 5", "`O(log₅ n)`"],
        ["GCD", "try every candidate", "Euclid: `gcd(b, a mod b)`", "`O(log min(a,b))`"],
        ["LCM", "try every multiple", "`a / gcd · b`", "`O(log min(a,b))`"],
        ["Is prime?", "divide by `2..n−1`", "divide by `6k ± 1` up to `√n`", "`O(√n)`"],
        ["Prime factors", "test every `i` for primality", "divide out `2`, `3`, then `6k ± 1` up to `√n`", "`O(√n)`"],
        ["All divisors", "test `1..n`", "pairs `(i, n/i)` up to `√n`", "`O(√n)`"],
        ["All primes `≤ n`", "test each number", "Sieve of Eratosthenes", "`O(n log log n)`"],
        ["`xⁿ`", "multiply `n` times", "square-and-multiply", "`O(log n)`"],
    )

    yield section("Sum of the first n natural numbers", "sum")
    yield io("n = 5", "15  (1 + 2 + 3 + 4 + 5)", "n = 50", "1275")
    yield idea("Pair the first and last terms: `1 + n`, `2 + (n−1)`, … — every pair sums to `n + 1` and there are `n/2` pairs, so the total is `n(n + 1) / 2`. No loop needed.")
    yield p("The loop is the obvious `O(n)` solution; the formula is `O(1)`. One subtlety: `n(n + 1)` may overflow before the division, so divide the **even** factor first — one of `n` and `n + 1` is always even, which keeps every intermediate value within the final answer's size.")
    yield multi('''
        sum(5): loop = 15, formula = 15
        sum(50): loop = 1275, formula = 1275
        sum(51): loop = 1326, formula = 1326
    ''', py='''
        def sum_loop(n):                      # O(n): add the numbers one by one
            total = 0
            for x in range(1, n + 1):
                total += x
            return total

        def sum_formula(n):                   # O(1): divide the even factor first (no overflow)
            if n % 2 == 0:
                return (n // 2) * (n + 1)
            return ((n + 1) // 2) * n         # n odd → n + 1 is even

        for n in (5, 50, 51):
            print(f"sum({n}): loop = {sum_loop(n)}, formula = {sum_formula(n)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long sumLoop(int n) {            // O(n): add the numbers one by one
            long long total = 0;
            for (int x = 1; x <= n; x++) total += x;
            return total;
        }

        long long sumFormula(long long n) {   // O(1): divide the even factor first (no overflow)
            if (n % 2 == 0) return (n / 2) * (n + 1);
            return ((n + 1) / 2) * n;         // n odd → n + 1 is even
        }

        int main() {
            for (int n : {5, 50, 51})
                cout << "sum(" << n << "): loop = " << sumLoop(n) << ", formula = " << sumFormula(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static long sumLoop(int n) {          // O(n): add the numbers one by one
                long total = 0;
                for (int x = 1; x <= n; x++) total += x;
                return total;
            }

            static long sumFormula(long n) {      // O(1): divide the even factor first (no overflow)
                if (n % 2 == 0) return (n / 2) * (n + 1);
                return ((n + 1) / 2) * n;         // n odd → n + 1 is even
            }

            public static void main(String[] args) {
                for (int n : new int[]{5, 50, 51})
                    System.out.println("sum(" + n + "): loop = " + sumLoop(n) + ", formula = " + sumFormula(n));
            }
        }
    ''', js=r'''
        function sumLoop(n) {                 // O(n): add the numbers one by one
            let total = 0;
            for (let x = 1; x <= n; x++) total += x;
            return total;
        }

        function sumFormula(n) {              // O(1): divide the even factor first (no overflow)
            if (n % 2 === 0) return (n / 2) * (n + 1);
            return ((n + 1) / 2) * n;         // n odd → n + 1 is even
        }

        for (const n of [5, 50, 51])
            console.log(`sum(${n}): loop = ${sumLoop(n)}, formula = ${sumFormula(n)}`);
    ''')
    yield complexity("O(1) with the formula, O(n) with the loop", "O(1)")
    yield pitfall("The original notes used `/` in Python, which returns a **float** (`15.0`). Use integer division `//` — and in C++/Java use a 64-bit type, since `n(n+1)` overflows a 32-bit `int` for `n` around 46 000 even though the answer still fits.")

    yield section("Count digits", "123")
    yield io("n = 256", "3", "n = 75", "2", "n = 5", "1")
    yield idea("`n % 10` is the last digit and `n // 10` drops it. Count how many times you can drop a digit before reaching `0` — that is the number of digits. The loop runs once per digit, i.e. `⌊log₁₀ n⌋ + 1` times.")
    yield multi('''
        256 → 3
        75 → 2
        5 → 1
        0 → 1
        9253 → 4
    ''', py='''
        def count_digits(n):
            n = abs(n)
            if n == 0:
                return 1                 # 0 is one digit, but the loop below would say 0
            count = 0
            while n > 0:
                n //= 10                 # drop the last digit
                count += 1
            return count

        for n in (256, 75, 5, 0, 9253):
            print(n, "→", count_digits(n))
    ''', cpp=r'''
        #include <iostream>
        #include <cstdlib>
        using namespace std;

        int countDigits(int n) {
            n = abs(n);
            if (n == 0) return 1;        // 0 is one digit, but the loop below would say 0
            int count = 0;
            while (n > 0) {
                n /= 10;                 // drop the last digit
                count++;
            }
            return count;
        }

        int main() {
            for (int n : {256, 75, 5, 0, 9253})
                cout << n << " → " << countDigits(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int countDigits(int n) {
                n = Math.abs(n);
                if (n == 0) return 1;        // 0 is one digit, but the loop below would say 0
                int count = 0;
                while (n > 0) {
                    n /= 10;                 // drop the last digit
                    count++;
                }
                return count;
            }

            public static void main(String[] args) {
                for (int n : new int[]{256, 75, 5, 0, 9253})
                    System.out.println(n + " → " + countDigits(n));
            }
        }
    ''', js=r'''
        function countDigits(n) {
            n = Math.abs(n);
            if (n === 0) return 1;       // 0 is one digit, but the loop below would say 0
            let count = 0;
            while (n > 0) {
                n = Math.floor(n / 10);  // drop the last digit (no integer division in JS)
                count++;
            }
            return count;
        }

        for (const n of [256, 75, 5, 0, 9253])
            console.log(n, "→", countDigits(n));
    ''')
    yield complexity("O(d) = O(log₁₀ n)", "O(1)")
    yield note("Alternatives: `len(str(n))` (allocates a string) or `floor(log10(n)) + 1` (floating-point, breaks for `n = 0` and can be off by one for exact powers of ten). The loop is the one to remember — the same `% 10` / `// 10` pattern reverses numbers, sums digits and checks palindromes.")

    yield section("Palindrome number", "arrows-left-right")
    yield io("n = 12321", "Yes", "n = 42322", "No", "n = 78987", "Yes")
    yield idea("A number reads the same backwards if it equals its own digit-reversal. Build the reversed number with `rev = rev * 10 + n % 10` while stripping digits off `n`, then compare with the original — no string conversion, `O(1)` extra space.")
    yield diagram('''
        n = 12321, rev = 0
        step 1: digit 1 → rev = 1        n = 1232
        step 2: digit 2 → rev = 12       n = 123
        step 3: digit 3 → rev = 123      n = 12
        step 4: digit 2 → rev = 1232     n = 1
        step 5: digit 1 → rev = 12321    n = 0   → rev == original → palindrome
    ''', "Reversing 12321 digit by digit")
    yield multi('''
        12321 → Yes
        42322 → No
        78987 → Yes
        10 → No
    ''', py='''
        def is_palindrome(n):
            if n < 0:
                return False             # "-121" reversed is "121-"
            rev, x = 0, n
            while x > 0:
                rev = rev * 10 + x % 10  # append the last digit of x to rev
                x //= 10
            return rev == n

        for n in (12321, 42322, 78987, 10):
            print(n, "→", "Yes" if is_palindrome(n) else "No")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        bool isPalindrome(long long n) {
            if (n < 0) return false;     // "-121" reversed is "121-"
            long long rev = 0, x = n;
            while (x > 0) {
                rev = rev * 10 + x % 10; // append the last digit of x to rev
                x /= 10;
            }
            return rev == n;
        }

        int main() {
            for (long long n : {12321, 42322, 78987, 10})
                cout << n << " → " << (isPalindrome(n) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isPalindrome(long n) {
                if (n < 0) return false;     // "-121" reversed is "121-"
                long rev = 0, x = n;
                while (x > 0) {
                    rev = rev * 10 + x % 10; // append the last digit of x to rev
                    x /= 10;
                }
                return rev == n;
            }

            public static void main(String[] args) {
                for (long n : new long[]{12321, 42322, 78987, 10})
                    System.out.println(n + " → " + (isPalindrome(n) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isPalindrome(n) {
            if (n < 0) return false;             // "-121" reversed is "121-"
            let rev = 0, x = n;
            while (x > 0) {
                rev = rev * 10 + (x % 10);       // append the last digit of x to rev
                x = Math.floor(x / 10);
            }
            return rev === n;
        }

        for (const n of [12321, 42322, 78987, 10])
            console.log(n, "→", isPalindrome(n) ? "Yes" : "No");
    ''')
    yield complexity("O(d)", "O(1)")
    yield pitfall("The reversed value of a large `int` can overflow even when the input fits (`1 000 000 003` reversed is `3 000 000 001 > 2³¹`). Use a 64-bit type for `rev`, or stop halfway: reverse only the second half and compare it with the first (the LeetCode variant).")

    yield section("Factorial", "math-x-divide-y-2")
    yield io("n = 3", "6  (3 × 2 × 1)", "n = 5", "120", "n = 0", "1")
    yield idea("`n! = n × (n−1)!` with `0! = 1`. A loop multiplies `1..n` into an accumulator; the recursive version is the definition written as code. Both are `O(n)` time — the difference is the `O(n)` call stack the recursion needs.")
    yield multi('''
        0! = 1 (iterative) 1 (recursive)
        3! = 6 (iterative) 6 (recursive)
        5! = 120 (iterative) 120 (recursive)
        10! = 3628800 (iterative) 3628800 (recursive)
        20! = 2432902008176640000 (iterative) 2432902008176640000 (recursive)
    ''', py='''
        def fact_iterative(n):           # O(n) time, O(1) auxiliary space
            result = 1
            for i in range(2, n + 1):
                result *= i
            return result

        def fact_recursive(n):           # O(n) time, O(n) stack frames
            if n == 0:                   # base case: 0! = 1 (not n == 1, or fact(0) never stops)
                return 1
            return n * fact_recursive(n - 1)

        for n in (0, 3, 5, 10, 20):
            print(f"{n}! = {fact_iterative(n)} (iterative) {fact_recursive(n)} (recursive)")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long factIterative(int n) {     // O(n) time, O(1) auxiliary space
            long long result = 1;
            for (int i = 2; i <= n; i++) result *= i;
            return result;
        }

        long long factRecursive(int n) {     // O(n) time, O(n) stack frames
            if (n == 0) return 1;            // base case: 0! = 1
            return n * factRecursive(n - 1);
        }

        int main() {
            for (int n : {0, 3, 5, 10, 20})
                cout << n << "! = " << factIterative(n) << " (iterative) " << factRecursive(n) << " (recursive)\n";
        }
    ''', java=r'''
        public class Main {
            static long factIterative(int n) {   // O(n) time, O(1) auxiliary space
                long result = 1;
                for (int i = 2; i <= n; i++) result *= i;
                return result;
            }

            static long factRecursive(int n) {   // O(n) time, O(n) stack frames
                if (n == 0) return 1;            // base case: 0! = 1
                return n * factRecursive(n - 1);
            }

            public static void main(String[] args) {
                for (int n : new int[]{0, 3, 5, 10, 20})
                    System.out.println(n + "! = " + factIterative(n) + " (iterative) " + factRecursive(n) + " (recursive)");
            }
        }
    ''', js=r'''
        function factIterative(n) {          // O(n) time, O(1) auxiliary space — BigInt: 20! > 2^53
            let result = 1n;
            for (let i = 2n; i <= BigInt(n); i++) result *= i;
            return result;
        }

        function factRecursive(n) {          // O(n) time, O(n) stack frames
            if (n === 0) return 1n;          // base case: 0! = 1
            return BigInt(n) * factRecursive(n - 1);
        }

        for (const n of [0, 3, 5, 10, 20])
            console.log(`${n}! = ${factIterative(n)} (iterative) ${factRecursive(n)} (recursive)`);
    ''')
    yield complexity("O(n)", "O(1) iterative, O(n) recursive (call stack)")
    yield pitfall("The original notes had the space costs backwards: it is the **recursive** version that uses `O(n)` auxiliary space (one frame per pending multiplication); the loop uses `O(1)`. Also: `13!` overflows a 32-bit `int`, `21!` overflows 64 bits, and JavaScript's `Number` loses exactness after `18!` — hence `BigInt` above. Python integers are unbounded.")

    yield section("Trailing zeros in a factorial", "circle-0")
    yield io("n = 5", "1  (5! = 120)", "n = 10", "2  (10! = 3628800)", "n = 100", "24")
    yield idea("A trailing zero is a factor of `10 = 2 × 5`. In `n!` there are always far more factors of 2 than of 5, so the zeros are counted by the **factors of 5**: every multiple of 5 contributes one, every multiple of 25 contributes a second, every multiple of 125 a third… Sum `n/5 + n/25 + n/125 + …` using integer division.")
    yield formula("zeros(n!) = ⌊n/5⌋ + ⌊n/25⌋ + ⌊n/125⌋ + … (until the term is 0)")
    yield example("`n = 100`: `100/5 = 20`, `100/25 = 4`, `100/125 = 0` → `24` trailing zeros. Computing `100!` (158 digits) is never needed.", "Worked example")
    yield multi('''
        5 → 1
        10 → 2
        25 → 6
        50 → 12
        100 → 24
    ''', py='''
        def trailing_zeros(n):
            count = 0
            power = 5
            while n // power >= 1:       # 5, 25, 125, … each adds one more factor of 5
                count += n // power
                power *= 5
            return count

        for n in (5, 10, 25, 50, 100):
            print(n, "→", trailing_zeros(n))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int trailingZeros(int n) {
            int count = 0;
            for (long long power = 5; n / power >= 1; power *= 5)   // 5, 25, 125, …
                count += n / power;
            return count;
        }

        int main() {
            for (int n : {5, 10, 25, 50, 100})
                cout << n << " → " << trailingZeros(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int trailingZeros(int n) {
                int count = 0;
                for (long power = 5; n / power >= 1; power *= 5)     // 5, 25, 125, …
                    count += n / power;
                return count;
            }

            public static void main(String[] args) {
                for (int n : new int[]{5, 10, 25, 50, 100})
                    System.out.println(n + " → " + trailingZeros(n));
            }
        }
    ''', js=r'''
        function trailingZeros(n) {
            let count = 0;
            for (let power = 5; Math.floor(n / power) >= 1; power *= 5)   // 5, 25, 125, …
                count += Math.floor(n / power);
            return count;
        }

        for (const n of [5, 10, 25, 50, 100])
            console.log(n, "→", trailingZeros(n));
    ''')
    yield complexity("O(log₅ n)", "O(1)")
    yield pitfall("Counting only `n / 5` misses the extra fives: `25 = 5 × 5` contributes **two** zeros, so `25!` has 6 trailing zeros, not 5. The original example (“Input 50, Output 1”) was wrong — `50!` ends in 12 zeros; it is `5!` that ends in one.")

    yield section("GCD / HCF of two numbers", "divide")
    yield io("a = 20, b = 28", "4", "a = 100, b = 75", "25", "a = 17, b = 5", "1")
    yield p("The **greatest common divisor** (also called highest common factor) is the largest number that divides both. Factors of 20: `1 2 4 5 10 20`; factors of 28: `1 2 4 7 14 28`; the largest shared one is `4`.")
    yield p("The naive method walks down from `min(a, b)` until it finds a common divisor — `O(min(a, b))`:")
    yield code('''
        def gcd_naive(a, b):
            result = min(a, b)
            while result > 0:
                if a % result == 0 and b % result == 0:
                    break                       # first common divisor from the top is the greatest
                result -= 1
            return result

        print(gcd_naive(20, 28))    # 4
        print(gcd_naive(100, 75))   # 25
    ''')
    yield idea("**Euclid's algorithm**: any divisor of both `a` and `b` also divides `a − b`, and hence `a mod b`. So `gcd(a, b) = gcd(b, a mod b)`, and when `b` becomes `0` the answer is `a`. The remainder at least halves every two steps, giving `O(log min(a, b))`.")
    yield diagram('''
        gcd(1071, 462)
          1071 = 2 · 462 + 147   →  gcd(462, 147)
           462 = 3 · 147 +  21   →  gcd(147, 21)
           147 = 7 ·  21 +   0   →  gcd(21, 0) = 21
    ''', "Euclid's algorithm: the remainder shrinks fast")
    yield multi('''
        gcd(20, 28) = 4
        gcd(100, 75) = 25
        gcd(17, 5) = 1
        gcd(1071, 462) = 21
        gcd(0, 9) = 9
    ''', py='''
        def gcd_recursive(a, b):
            if b == 0:
                return a
            return gcd_recursive(b, a % b)   # gcd(a, b) = gcd(b, a mod b)

        def gcd(a, b):                       # same idea, iterative: O(1) space
            while b:
                a, b = b, a % b
            return a

        for a, b in [(20, 28), (100, 75), (17, 5), (1071, 462), (0, 9)]:
            assert gcd(a, b) == gcd_recursive(a, b)
            print(f"gcd({a}, {b}) = {gcd(a, b)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int gcdRecursive(int a, int b) {
            if (b == 0) return a;
            return gcdRecursive(b, a % b);   // gcd(a, b) = gcd(b, a mod b)
        }

        int gcd(int a, int b) {              // same idea, iterative: O(1) space
            while (b != 0) {
                int r = a % b;
                a = b;
                b = r;
            }
            return a;
        }

        int main() {
            int pairs[5][2] = {{20, 28}, {100, 75}, {17, 5}, {1071, 462}, {0, 9}};
            for (auto& ab : pairs) {
                int g = gcd(ab[0], ab[1]);
                if (g != gcdRecursive(ab[0], ab[1])) return 1;
                cout << "gcd(" << ab[0] << ", " << ab[1] << ") = " << g << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static int gcdRecursive(int a, int b) {
                if (b == 0) return a;
                return gcdRecursive(b, a % b);   // gcd(a, b) = gcd(b, a mod b)
            }

            static int gcd(int a, int b) {       // same idea, iterative: O(1) space
                while (b != 0) {
                    int r = a % b;
                    a = b;
                    b = r;
                }
                return a;
            }

            public static void main(String[] args) {
                int[][] pairs = {{20, 28}, {100, 75}, {17, 5}, {1071, 462}, {0, 9}};
                for (int[] ab : pairs) {
                    int g = gcd(ab[0], ab[1]);
                    assert g == gcdRecursive(ab[0], ab[1]);
                    System.out.println("gcd(" + ab[0] + ", " + ab[1] + ") = " + g);
                }
            }
        }
    ''', js=r'''
        function gcdRecursive(a, b) {
            if (b === 0) return a;
            return gcdRecursive(b, a % b);   // gcd(a, b) = gcd(b, a mod b)
        }

        function gcd(a, b) {                 // same idea, iterative: O(1) space
            while (b !== 0) [a, b] = [b, a % b];
            return a;
        }

        for (const [a, b] of [[20, 28], [100, 75], [17, 5], [1071, 462], [0, 9]]) {
            const g = gcd(a, b);
            if (g !== gcdRecursive(a, b)) throw new Error("mismatch");
            console.log(`gcd(${a}, ${b}) = ${g}`);
        }
    ''')
    yield complexity("O(log min(a, b))", "O(1) iterative, O(log min(a, b)) recursive")
    yield p("The original notes also had a **subtraction-only** version, `while a != b: subtract the smaller from the larger`. It is correct, but it is *not* the optimised one: for `gcd(1, 10⁹)` it loops a billion times, whereas the modulo version finishes in one step. Keep it as a curiosity:")
    yield code('''
        def gcd_subtract(a, b):
            while a != b:
                if a > b:
                    a -= b
                else:
                    b -= a                   # each step removes one multiple — O(max(a, b)) worst case
            return a

        print(gcd_subtract(20, 28))    # 4
    ''')
    yield note("Libraries: Python `math.gcd`, C++ `std::gcd` (`<numeric>`), Java `BigInteger.gcd` (no primitive version), JavaScript has none. In interviews write Euclid yourself — it is three lines.")

    yield section("LCM of two numbers", "arrows-join")
    yield io("a = 15, b = 20", "60", "a = 4, b = 6", "12")
    yield p("The **least common multiple** is the smallest positive number divisible by both. The naive way starts at `max(a, b)` and counts up until a common multiple appears — up to `a · b` steps:")
    yield code('''
        def lcm_naive(a, b):
            res = max(a, b)
            while True:
                if res % a == 0 and res % b == 0:
                    return res
                res += 1

        print(lcm_naive(15, 20))   # 60
    ''')
    yield idea("`a · b = gcd(a, b) · lcm(a, b)` — every prime factor appears in the product exactly once as a “shared” copy (the gcd) and once as a “max” copy (the lcm). So `lcm = a / gcd(a, b) · b`. Divide **before** multiplying to keep the intermediate value small.")
    yield multi('''
        lcm(15, 20) = 60
        lcm(4, 6) = 12
        lcm(7, 13) = 91
        lcm(12, 18) = 36
    ''', py='''
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a

        def lcm(a, b):
            return a // gcd(a, b) * b        # divide first: a/g is an integer, product stays small

        for a, b in [(15, 20), (4, 6), (7, 13), (12, 18)]:
            print(f"lcm({a}, {b}) = {lcm(a, b)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long gcd(long long a, long long b) {
            while (b != 0) { long long r = a % b; a = b; b = r; }
            return a;
        }

        long long lcm(long long a, long long b) {
            return a / gcd(a, b) * b;        // divide first: a/g is an integer, product stays small
        }

        int main() {
            long long pairs[4][2] = {{15, 20}, {4, 6}, {7, 13}, {12, 18}};
            for (auto& ab : pairs)
                cout << "lcm(" << ab[0] << ", " << ab[1] << ") = " << lcm(ab[0], ab[1]) << "\n";
        }
    ''', java=r'''
        public class Main {
            static long gcd(long a, long b) {
                while (b != 0) { long r = a % b; a = b; b = r; }
                return a;
            }

            static long lcm(long a, long b) {
                return a / gcd(a, b) * b;        // divide first: a/g is an integer, product stays small
            }

            public static void main(String[] args) {
                long[][] pairs = {{15, 20}, {4, 6}, {7, 13}, {12, 18}};
                for (long[] ab : pairs)
                    System.out.println("lcm(" + ab[0] + ", " + ab[1] + ") = " + lcm(ab[0], ab[1]));
            }
        }
    ''', js=r'''
        function gcd(a, b) {
            while (b !== 0) [a, b] = [b, a % b];
            return a;
        }

        function lcm(a, b) {
            return (a / gcd(a, b)) * b;      // divide first: a/g is an integer, product stays small
        }

        for (const [a, b] of [[15, 20], [4, 6], [7, 13], [12, 18]])
            console.log(`lcm(${a}, ${b}) = ${lcm(a, b)}`);
    ''')
    yield complexity("O(log min(a, b))", "O(1)")
    yield pitfall("`a * b / gcd` computes the product first and overflows for large inputs; `a / gcd * b` never exceeds the answer. And once more: Python's `/` yields a float (`60.0`) — the original notes' `abs(a * b) / GCD(a, b)` printed `60.0`.")

    yield section("Check for prime", "hash")
    yield io("n = 11", "Yes", "n = 10", "No", "n = 1", "No")
    yield p("A prime has exactly two divisors, `1` and itself; `1` is **not** prime. The naive test tries every `i` from `2` to `n − 1` — `O(n)`:")
    yield code('''
        def is_prime_naive(n):
            if n <= 1:
                return False
            for i in range(2, n):
                if n % i == 0:
                    return False
            return True

        print(is_prime_naive(11))   # True
        print(is_prime_naive(10))   # False
    ''')
    yield idea("Divisors come in pairs `(i, n / i)`, and one of them is always `≤ √n` — so if nothing up to `√n` divides `n`, nothing does. Then skip multiples of 2 and 3: every prime above 3 has the form `6k ± 1`, so after checking `2` and `3` it is enough to test `5, 7, 11, 13, 17, 19…` — a third of the candidates.")
    yield steps(
        ("Handle the small cases", "`n ≤ 1` → not prime; `n ≤ 3` → prime."),
        ("Remove multiples of 2 and 3", "If `n % 2 == 0` or `n % 3 == 0` → not prime."),
        ("Test `6k ± 1` up to `√n`", "`i = 5, 11, 17…` (step 6), checking both `i` and `i + 2`. Use `i * i <= n` instead of `sqrt` to avoid floating point."),
    )
    yield multi('''
        1 → No
        2 → Yes
        10 → No
        11 → Yes
        97 → Yes
        1000003 → Yes
        1000001 → No
    ''', py='''
        def is_prime(n):
            if n <= 1:
                return False
            if n <= 3:
                return True
            if n % 2 == 0 or n % 3 == 0:
                return False
            i = 5
            while i * i <= n:                # only up to √n
                if n % i == 0 or n % (i + 2) == 0:   # 6k - 1 and 6k + 1
                    return False
                i += 6
            return True

        for n in (1, 2, 10, 11, 97, 1000003, 1000001):
            print(n, "→", "Yes" if is_prime(n) else "No")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        bool isPrime(long long n) {
            if (n <= 1) return false;
            if (n <= 3) return true;
            if (n % 2 == 0 || n % 3 == 0) return false;
            for (long long i = 5; i * i <= n; i += 6)          // only up to √n
                if (n % i == 0 || n % (i + 2) == 0) return false;   // 6k - 1 and 6k + 1
            return true;
        }

        int main() {
            for (long long n : {1, 2, 10, 11, 97, 1000003, 1000001})
                cout << n << " → " << (isPrime(n) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static boolean isPrime(long n) {
                if (n <= 1) return false;
                if (n <= 3) return true;
                if (n % 2 == 0 || n % 3 == 0) return false;
                for (long i = 5; i * i <= n; i += 6)              // only up to √n
                    if (n % i == 0 || n % (i + 2) == 0) return false;   // 6k - 1 and 6k + 1
                return true;
            }

            public static void main(String[] args) {
                for (long n : new long[]{1, 2, 10, 11, 97, 1000003, 1000001})
                    System.out.println(n + " → " + (isPrime(n) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isPrime(n) {
            if (n <= 1) return false;
            if (n <= 3) return true;
            if (n % 2 === 0 || n % 3 === 0) return false;
            for (let i = 5; i * i <= n; i += 6)                  // only up to √n
                if (n % i === 0 || n % (i + 2) === 0) return false;   // 6k - 1 and 6k + 1
            return true;
        }

        for (const n of [1, 2, 10, 11, 97, 1000003, 1000001])
            console.log(n, "→", isPrime(n) ? "Yes" : "No");
    ''')
    yield complexity("O(√n)", "O(1)")
    yield pitfall("Forgetting `n = 1` (not prime) and `n = 2` (the only even prime) are the classic slips. Using `i <= sqrt(n)` with floating point can misjudge perfect squares of large primes; `i * i <= n` is exact (use a 64-bit `i` so the square cannot overflow).")

    yield section("Prime factorization", "binary-tree-2")
    yield io("n = 100", "2 2 5 5  (100 = 2² × 5²)", "n = 315", "3 3 5 7")
    yield p("The original notes tested every `i` from `2` to `n` for primality and then divided it out — `O(n √n)`. That primality test is unnecessary: if you divide out each factor **completely** as soon as you meet it, every later `i` that divides `n` is automatically prime (all its smaller factors are already gone).")
    yield idea("Divide out all 2s, then all 3s, then try `i = 5, 7, 11, 13…` (`6k ± 1`) while `i * i ≤ n`, dividing out each as many times as it goes. Whatever is left above `1` at the end is a single prime factor larger than `√n` — there can be at most one.")
    yield multi('''
        100 → 2 2 5 5
        315 → 3 3 5 7
        97 → 97
        1001 → 7 11 13
        1 →
    ''', py='''
        def prime_factors(n):
            factors = []
            while n % 2 == 0:                 # all the 2s
                factors.append(2)
                n //= 2
            while n % 3 == 0:                 # all the 3s
                factors.append(3)
                n //= 3
            i = 5
            while i * i <= n:                 # 6k ± 1 candidates up to √n
                for d in (i, i + 2):
                    while n % d == 0:
                        factors.append(d)
                        n //= d
                i += 6
            if n > 1:                         # one prime factor > √n may remain
                factors.append(n)
            return factors

        for n in (100, 315, 97, 1001, 1):
            print(n, "→", *prime_factors(n))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> primeFactors(int n) {
            vector<int> factors;
            while (n % 2 == 0) { factors.push_back(2); n /= 2; }   // all the 2s
            while (n % 3 == 0) { factors.push_back(3); n /= 3; }   // all the 3s
            for (int i = 5; i * i <= n; i += 6)                    // 6k ± 1 candidates up to √n
                for (int d : {i, i + 2})
                    while (n % d == 0) { factors.push_back(d); n /= d; }
            if (n > 1) factors.push_back(n);                       // one prime factor > √n may remain
            return factors;
        }

        int main() {
            for (int n : {100, 315, 97, 1001, 1}) {
                cout << n << " →";
                for (int f : primeFactors(n)) cout << " " << f;
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> primeFactors(int n) {
                List<Integer> factors = new ArrayList<>();
                while (n % 2 == 0) { factors.add(2); n /= 2; }        // all the 2s
                while (n % 3 == 0) { factors.add(3); n /= 3; }        // all the 3s
                for (int i = 5; i * i <= n; i += 6)                   // 6k ± 1 candidates up to √n
                    for (int d : new int[]{i, i + 2})
                        while (n % d == 0) { factors.add(d); n /= d; }
                if (n > 1) factors.add(n);                            // one prime factor > √n may remain
                return factors;
            }

            public static void main(String[] args) {
                for (int n : new int[]{100, 315, 97, 1001, 1}) {
                    StringBuilder sb = new StringBuilder(n + " →");
                    for (int f : primeFactors(n)) sb.append(' ').append(f);
                    System.out.println(sb);
                }
            }
        }
    ''', js=r'''
        function primeFactors(n) {
            const factors = [];
            while (n % 2 === 0) { factors.push(2); n /= 2; }         // all the 2s
            while (n % 3 === 0) { factors.push(3); n /= 3; }         // all the 3s
            for (let i = 5; i * i <= n; i += 6)                      // 6k ± 1 candidates up to √n
                for (const d of [i, i + 2])
                    while (n % d === 0) { factors.push(d); n /= d; }
            if (n > 1) factors.push(n);                              // one prime factor > √n may remain
            return factors;
        }

        for (const n of [100, 315, 97, 1001, 1])
            console.log(`${n} →${primeFactors(n).map(f => " " + f).join("")}`);
    ''')
    yield complexity("O(√n)", "O(log n) for the list of factors")
    yield pitfall("Stopping at `√n` without the final `if n > 1` check loses the largest factor: `1001 = 7 × 11 × 13` leaves `n = 13` after `7` and `11` are divided out, and `13 > √13`. Also `1` has no prime factors — the loop must print nothing, not `1`.")

    yield section("All divisors of a number", "list-numbers")
    yield io("n = 10", "1 2 5 10", "n = 100", "1 2 4 5 10 20 25 50 100")
    yield p("Naively, test every `i` in `1..n` — `O(n)`:")
    yield code('''
        def divisors_naive(n):
            return [i for i in range(1, n + 1) if n % i == 0]

        print(divisors_naive(10))   # [1, 2, 5, 10]
    ''')
    yield idea("Divisors come in **pairs** `(i, n / i)` with `i ≤ √n ≤ n / i`. Loop `i` from `1` while `i * i ≤ n` and emit both members of each pair — that finds every divisor in `O(√n)`. When `i * i == n` the pair is the same number: print it once.")
    yield p("Emitting both members as you go gives the divisors *unsorted* (`1 100 2 50 4 25 5 20 10`). To get them **sorted** with no extra memory, print the small members on the way up and the large partners on the way back down:")
    yield code('''
        import math

        def divisors_unsorted(n):            # O(√n), pairs printed together
            out = []
            i = 1
            while i * i <= n:
                if n % i == 0:
                    out.append(i)
                    if n // i != i:          # perfect square: don't print √n twice
                        out.append(n // i)
                i += 1
            return out

        print(divisors_unsorted(100))        # [1, 100, 2, 50, 4, 25, 5, 20, 10]
    ''')
    yield multi('''
        10 → 1 2 5 10
        100 → 1 2 4 5 10 20 25 50 100
        36 → 1 2 3 4 6 9 12 18 36
        97 → 1 97
    ''', py='''
        def divisors_sorted(n):
            out = []
            i = 1
            while i * i < n:                   # ascending: small members of each pair
                if n % i == 0:
                    out.append(i)
                i += 1
            if i * i == n:                     # perfect square: √n once
                out.append(i)
            i -= 1 if i * i == n else 0
            while i >= 1:                      # descending i → ascending partners n / i
                if n % i == 0 and i * i != n:
                    out.append(n // i)
                i -= 1
            return out

        for n in (10, 100, 36, 97):
            print(n, "→", *divisors_sorted(n))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> divisorsSorted(int n) {
            vector<int> out;
            int i = 1;
            for (; i * i < n; i++)                      // ascending: small members of each pair
                if (n % i == 0) out.push_back(i);
            if (i * i == n) out.push_back(i);           // perfect square: √n once
            for (i = i * i == n ? i - 1 : i; i >= 1; i--)   // descending i → ascending partners n / i
                if (n % i == 0 && i * i != n) out.push_back(n / i);
            return out;
        }

        int main() {
            for (int n : {10, 100, 36, 97}) {
                cout << n << " →";
                for (int d : divisorsSorted(n)) cout << " " << d;
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> divisorsSorted(int n) {
                List<Integer> out = new ArrayList<>();
                int i = 1;
                for (; i * i < n; i++)                      // ascending: small members of each pair
                    if (n % i == 0) out.add(i);
                if (i * i == n) out.add(i);                 // perfect square: √n once
                for (i = i * i == n ? i - 1 : i; i >= 1; i--)   // descending i → ascending partners n / i
                    if (n % i == 0 && i * i != n) out.add(n / i);
                return out;
            }

            public static void main(String[] args) {
                for (int n : new int[]{10, 100, 36, 97}) {
                    StringBuilder sb = new StringBuilder(n + " →");
                    for (int d : divisorsSorted(n)) sb.append(' ').append(d);
                    System.out.println(sb);
                }
            }
        }
    ''', js=r'''
        function divisorsSorted(n) {
            const out = [];
            let i = 1;
            for (; i * i < n; i++)                          // ascending: small members of each pair
                if (n % i === 0) out.push(i);
            if (i * i === n) out.push(i);                   // perfect square: √n once
            for (i = i * i === n ? i - 1 : i; i >= 1; i--)  // descending i → ascending partners n / i
                if (n % i === 0 && i * i !== n) out.push(n / i);
            return out;
        }

        for (const n of [10, 100, 36, 97])
            console.log(`${n} →${divisorsSorted(n).map(d => " " + d).join("")}`);
    ''')
    yield complexity("O(√n)", "O(1) besides the output")
    yield pitfall("`36 = 6 × 6`: the pair `(6, 6)` must be printed **once**. Checking `n / i != i` (unsorted version) or handling `i * i == n` separately (sorted version) is the detail interviewers look for.")

    yield section("Sieve of Eratosthenes", "grid-dots")
    yield io("n = 10", "2 3 5 7", "n = 50", "2 3 5 7 11 13 17 19 23 29 31 37 41 43 47")
    yield p("To list **all** primes up to `n`, testing each number separately costs `O(n √n)`. The sieve does far better by working the other way round: instead of asking “is `x` prime?”, it *crosses out* every multiple of each prime found.")
    yield idea("Keep a boolean array `is_prime[0..n]`, all `true`. For each `i` from `2` while `i * i ≤ n`: if `i` is still marked prime, cross out `i², i² + i, i² + 2i, …`. Smaller multiples like `2i, 3i` were already crossed out by smaller primes, which is why starting at `i²` is enough and why `i` only needs to run up to `√n`.")
    yield diagram('''
        n = 30, after sieving with 2, 3 and 5 (5² = 25 ≤ 30, 7² = 49 > 30 → stop)

         2  3  x  5  x  7  x  x  x 11  x 13  x  x  x 17  x 19  x  x  x 23  x  x  x  x  x 29  x
         ^  ^     ^     ^           ^     ^           ^     ^           ^                 ^
        primes: 2 3 5 7 11 13 17 19 23 29
    ''', "Crossing out multiples: everything still standing is prime")
    yield multi('''
        primes ≤ 10: 2 3 5 7
        primes ≤ 50: 2 3 5 7 11 13 17 19 23 29 31 37 41 43 47
        count ≤ 1000: 168
    ''', py='''
        def sieve(n):
            if n < 2:
                return []
            is_prime = [True] * (n + 1)
            is_prime[0] = is_prime[1] = False
            i = 2
            while i * i <= n:                          # only up to √n
                if is_prime[i]:
                    for j in range(i * i, n + 1, i):   # start at i²: smaller multiples are done
                        is_prime[j] = False
                i += 1
            return [x for x in range(2, n + 1) if is_prime[x]]

        print("primes ≤ 10:", *sieve(10))
        print("primes ≤ 50:", *sieve(50))
        print("count ≤ 1000:", len(sieve(1000)))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> sieve(int n) {
            vector<int> primes;
            if (n < 2) return primes;
            vector<bool> isPrime(n + 1, true);
            isPrime[0] = isPrime[1] = false;
            for (int i = 2; i * i <= n; i++)                     // only up to √n
                if (isPrime[i])
                    for (int j = i * i; j <= n; j += i)          // start at i²: smaller multiples are done
                        isPrime[j] = false;
            for (int x = 2; x <= n; x++)
                if (isPrime[x]) primes.push_back(x);
            return primes;
        }

        int main() {
            for (int n : {10, 50}) {
                cout << "primes ≤ " << n << ":";
                for (int p : sieve(n)) cout << " " << p;
                cout << "\n";
            }
            cout << "count ≤ 1000: " << sieve(1000).size() << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static List<Integer> sieve(int n) {
                List<Integer> primes = new ArrayList<>();
                if (n < 2) return primes;
                boolean[] composite = new boolean[n + 1];        // false = still prime
                for (int i = 2; (long) i * i <= n; i++)          // only up to √n
                    if (!composite[i])
                        for (int j = i * i; j <= n; j += i)      // start at i²: smaller multiples are done
                            composite[j] = true;
                for (int x = 2; x <= n; x++)
                    if (!composite[x]) primes.add(x);
                return primes;
            }

            public static void main(String[] args) {
                for (int n : new int[]{10, 50}) {
                    StringBuilder sb = new StringBuilder("primes ≤ " + n + ":");
                    for (int p : sieve(n)) sb.append(' ').append(p);
                    System.out.println(sb);
                }
                System.out.println("count ≤ 1000: " + sieve(1000).size());
            }
        }
    ''', js=r'''
        function sieve(n) {
            if (n < 2) return [];
            const isPrime = new Array(n + 1).fill(true);
            isPrime[0] = isPrime[1] = false;
            for (let i = 2; i * i <= n; i++)                     // only up to √n
                if (isPrime[i])
                    for (let j = i * i; j <= n; j += i)          // start at i²: smaller multiples are done
                        isPrime[j] = false;
            const primes = [];
            for (let x = 2; x <= n; x++) if (isPrime[x]) primes.push(x);
            return primes;
        }

        for (const n of [10, 50]) console.log(`primes ≤ ${n}: ${sieve(n).join(" ")}`);
        console.log("count ≤ 1000:", sieve(1000).length);
    ''')
    yield complexity("O(n log log n)", "O(n)")
    yield note("Why `n log log n`? Prime `p` crosses out `n/p` numbers, and `Σ 1/p` over primes up to `n` is about `log log n`. In practice it is *nearly linear*: sieving up to `10⁷` takes well under a second. Starting the inner loop at `i²` instead of `2i` is the small detail that makes the `√n` outer bound valid.")
    yield pitfall("`i * i` overflows a 32-bit `int` when `n` is near `2³¹` — cast to a 64-bit type in the loop condition (the Java version does). And a sieve answers “all primes up to `n`”; for a **single** large number use the `√n` test, not a sieve of size `n`.")

    yield section("Computing power xⁿ", "superscript")
    yield io("x = 2, n = 3", "8", "x = 3, n = 5", "243")
    yield p("Multiplying `x` by itself `n` times is `O(n)`:")
    yield code('''
        def power_naive(x, n):
            result = 1
            for _ in range(n):
                result *= x
            return result

        print(power_naive(2, 3))    # 8
        print(power_naive(3, 5))    # 243
    ''')
    yield idea("**Square and halve**: `xⁿ = (x^(n/2))²` when `n` is even, and `x · (x^(n/2))²` when `n` is odd. Each recursive call halves `n`, so only `O(log n)` multiplications are needed — compute `x^(n/2)` **once** and square it; calling the function twice brings the cost back to `O(n)`.")
    yield diagram('''
        3^13 = 3 · (3^6)²            13 is odd
        3^6  =     (3^3)²             6 is even
        3^3  = 3 · (3^1)²             3 is odd
        3^1  = 3 · (3^0)²
        3^0  = 1                      base case  →  4 levels for n = 13
    ''', "Recursive power: n halves at every level")
    yield multi('''
        2^3 = 8
        3^5 = 243
        3^13 = 1594323
        2^30 = 1073741824
        5^0 = 1
    ''', py='''
        def power(x, n):
            if n == 0:
                return 1
            half = power(x, n // 2)        # compute x^(n/2) once …
            if n % 2 == 0:
                return half * half         # … and square it
            return x * half * half

        for x, n in [(2, 3), (3, 5), (3, 13), (2, 30), (5, 0)]:
            print(f"{x}^{n} = {power(x, n)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long power(long long x, int n) {
            if (n == 0) return 1;
            long long half = power(x, n / 2);   // compute x^(n/2) once …
            if (n % 2 == 0) return half * half; // … and square it
            return x * half * half;
        }

        int main() {
            int cases[5][2] = {{2, 3}, {3, 5}, {3, 13}, {2, 30}, {5, 0}};
            for (auto& c : cases)
                cout << c[0] << "^" << c[1] << " = " << power(c[0], c[1]) << "\n";
        }
    ''', java=r'''
        public class Main {
            static long power(long x, int n) {
                if (n == 0) return 1;
                long half = power(x, n / 2);        // compute x^(n/2) once …
                if (n % 2 == 0) return half * half; // … and square it
                return x * half * half;
            }

            public static void main(String[] args) {
                int[][] cases = {{2, 3}, {3, 5}, {3, 13}, {2, 30}, {5, 0}};
                for (int[] c : cases)
                    System.out.println(c[0] + "^" + c[1] + " = " + power(c[0], c[1]));
            }
        }
    ''', js=r'''
        function power(x, n) {
            if (n === 0) return 1;
            const half = power(x, Math.floor(n / 2));   // compute x^(n/2) once …
            if (n % 2 === 0) return half * half;        // … and square it
            return x * half * half;
        }

        for (const [x, n] of [[2, 3], [3, 5], [3, 13], [2, 30], [5, 0]])
            console.log(`${x}^${n} = ${power(x, n)}`);
    ''')
    yield complexity("O(log n)", "O(log n) call stack")
    yield pitfall("`return power(x, n/2) * power(x, n/2)` is the famous mistake — two calls per level gives `T(n) = 2T(n/2) + 1 = O(n)`, no better than the loop. Store the half-result in a variable. (The original notes also handled negative exponents by dividing; that returns a float and is rarely wanted — restrict `n ≥ 0` or handle it separately.)")

    yield section("Iterative power: binary exponentiation", "binary")
    yield io("x = 3, n = 5", "243  (5 = 101₂ → 3⁴ · 3¹)", "x = 2, n = 100, mod = 10⁹ + 7", "976371285")
    yield idea("Every exponent is a sum of powers of two: `5 = 4 + 1`, so `3⁵ = 3⁴ · 3¹`. Walk through the **bits** of `n` from least significant: keep squaring `x` (`x, x², x⁴, x⁸…`) and multiply the current square into the result whenever the bit is `1`. `O(log n)` steps, no recursion.")
    yield diagram('''
        3^5, n = 5 = 101₂          res = 1,  x = 3
        bit 0 = 1 → res = 1 · 3 = 3        x = 3² = 9        n = 2 (10₂)
        bit 1 = 0 → res unchanged          x = 9² = 81       n = 1 (1₂)
        bit 2 = 1 → res = 3 · 81 = 243     x = 81² = 6561    n = 0 → stop
    ''', "The square-and-multiply loop on 3^5")
    yield p("The real-world form adds a modulus: `x^n mod m` for huge `n` (RSA, hashing, combinatorics mod `10⁹ + 7`). Reduce after every multiplication so the numbers never exceed `m²`.")
    yield multi('''
        3^5 = 243
        2^30 = 1073741824
        7^0 = 1
        2^100 mod 1000000007 = 976371285
        3^200 mod 1000000007 = 136318165
    ''', py='''
        def power(x, n):
            res = 1
            while n > 0:
                if n & 1:                 # current bit is 1: multiply this power of x in
                    res *= x
                x *= x                    # x, x², x⁴, x⁸ …
                n >>= 1                   # next bit
            return res

        def power_mod(x, n, m):
            res, x = 1, x % m
            while n > 0:
                if n & 1:
                    res = res * x % m     # reduce after every multiplication
                x = x * x % m
                n >>= 1
            return res

        for x, n in [(3, 5), (2, 30), (7, 0)]:
            print(f"{x}^{n} = {power(x, n)}")
        M = 1_000_000_007
        print(f"2^100 mod {M} = {power_mod(2, 100, M)}")
        print(f"3^200 mod {M} = {power_mod(3, 200, M)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long power(long long x, int n) {
            long long res = 1;
            while (n > 0) {
                if (n & 1) res *= x;      // current bit is 1: multiply this power of x in
                x *= x;                   // x, x², x⁴, x⁸ …
                n >>= 1;                  // next bit
            }
            return res;
        }

        long long powerMod(long long x, long long n, long long m) {
            long long res = 1;
            x %= m;
            while (n > 0) {
                if (n & 1) res = res * x % m;   // reduce after every multiplication
                x = x * x % m;
                n >>= 1;
            }
            return res;
        }

        int main() {
            int cases[3][2] = {{3, 5}, {2, 30}, {7, 0}};
            for (auto& c : cases) cout << c[0] << "^" << c[1] << " = " << power(c[0], c[1]) << "\n";
            const long long M = 1000000007LL;
            cout << "2^100 mod " << M << " = " << powerMod(2, 100, M) << "\n";
            cout << "3^200 mod " << M << " = " << powerMod(3, 200, M) << "\n";
        }
    ''', java=r'''
        public class Main {
            static long power(long x, int n) {
                long res = 1;
                while (n > 0) {
                    if ((n & 1) == 1) res *= x;   // current bit is 1: multiply this power of x in
                    x *= x;                       // x, x², x⁴, x⁸ …
                    n >>= 1;                      // next bit
                }
                return res;
            }

            static long powerMod(long x, long n, long m) {
                long res = 1;
                x %= m;
                while (n > 0) {
                    if ((n & 1) == 1) res = res * x % m;   // reduce after every multiplication
                    x = x * x % m;
                    n >>= 1;
                }
                return res;
            }

            public static void main(String[] args) {
                int[][] cases = {{3, 5}, {2, 30}, {7, 0}};
                for (int[] c : cases) System.out.println(c[0] + "^" + c[1] + " = " + power(c[0], c[1]));
                final long M = 1_000_000_007L;
                System.out.println("2^100 mod " + M + " = " + powerMod(2, 100, M));
                System.out.println("3^200 mod " + M + " = " + powerMod(3, 200, M));
            }
        }
    ''', js=r'''
        function power(x, n) {
            let res = 1;
            while (n > 0) {
                if (n & 1) res *= x;      // current bit is 1: multiply this power of x in
                x *= x;                   // x, x², x⁴, x⁸ …
                n >>= 1;                  // next bit
            }
            return res;
        }

        function powerMod(x, n, m) {      // BigInt: res * x can exceed 2^53
            let res = 1n;
            x = BigInt(x) % m;
            while (n > 0) {
                if (n & 1) res = res * x % m;   // reduce after every multiplication
                x = x * x % m;
                n >>= 1;
            }
            return res;
        }

        for (const [x, n] of [[3, 5], [2, 30], [7, 0]]) console.log(`${x}^${n} = ${power(x, n)}`);
        const M = 1000000007n;
        console.log(`2^100 mod ${M} = ${powerMod(2, 100, M)}`);
        console.log(`3^200 mod ${M} = ${powerMod(3, 200, M)}`);
    ''')
    yield complexity("O(log n)", "O(1)")
    yield pitfall("`res * x` with both below `10⁹ + 7` is up to `10¹⁸` — fits a 64-bit integer but **not** JavaScript's `Number` (exact only to `2⁵³`), hence `BigInt` there. Python's built-in `pow(x, n, m)` does exactly this loop in C.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why does checking divisors up to √n suffice for a primality test?",
             "If `n = a × b` with `a ≤ b`, then `a × a ≤ a × b = n`, so `a ≤ √n`. Every composite number therefore has a divisor no larger than `√n`; if none is found there, `n` is prime. The same pairing argument gives the `O(√n)` divisor listing.")
    yield qa("Explain Euclid's algorithm and its complexity.",
             "`gcd(a, b) = gcd(b, a mod b)`, because any common divisor of `a` and `b` also divides `a − qb`. Iterate until `b = 0`; the other value is the gcd. After any two steps the larger number at least halves, so it runs in `O(log min(a, b))` — about 45 steps for 64-bit inputs, versus up to `10⁹` for subtraction or trial division.")
    yield qa("How do you compute the LCM without overflow?",
             "`lcm(a, b) = a / gcd(a, b) × b`. Dividing first keeps the intermediate value equal to the final answer; `a × b / gcd` can overflow even when the lcm fits.")
    yield qa("How many trailing zeros does 100! have, and why not count factors of 2?",
             "24: `100/5 + 100/25 = 20 + 4`. A trailing zero needs a `2` and a `5`; in `n!` factors of 2 are far more common than factors of 5 (every second number vs every fifth), so the fives are the bottleneck and counting them alone is exact.")
    yield qa("Why does the sieve start crossing out at i² and stop at √n?",
             "Any multiple `k·i` with `k < i` was already removed when the prime `k` (or one of its factors) was processed, so `i²` is the first new composite. Once `i > √n`, `i² > n` — there is nothing left to cross out, so all survivors are prime.")
    yield qa("How does fast exponentiation reach O(log n), and where is it used?",
             "Write `n` in binary; `xⁿ` is the product of `x^(2^k)` over the set bits, and successive squaring produces those powers one per bit. That is `O(log n)` multiplications instead of `n`. Used for modular exponentiation (RSA, Diffie–Hellman, modular inverses by Fermat), matrix powers (Fibonacci in `O(log n)`) and any repeated application of an associative operation.")


@topic(G, "recursion", "Recursion", "repeat")
def _():
    yield lead("Recursion is a function solving a problem by calling **itself** on a smaller version of the same problem. It is the natural shape of divide and conquer, tree and graph traversal, backtracking and dynamic programming — and the source of the classic bugs: a missing base case and a blown call stack.")
    yield define("Recursion", "a technique where a function calls itself, directly or indirectly, until it reaches a **base case** that can be answered without a further call. Each call works on a strictly smaller input so that the chain of calls is guaranteed to end.")
    yield table(
        ["Kind", "Shape", "Example"],
        ["**Direct** recursion", "`f` calls `f`", "`fact(n)` calls `fact(n − 1)`"],
        ["**Indirect** (mutual) recursion", "`f` calls `g`, `g` calls `f`", "`is_even(n)` calls `is_odd(n − 1)`, which calls `is_even(n − 2)`"],
        ["Not recursion", "a loop repeats a block without a new call", "`for i in range(n): print(\"GFG\")` — the original notes' first example is this, a plain loop"],
    )

    yield section("Recursion background: how calls nest", "stack-2")
    yield p("A function call does not finish until the function it called has returned. The program below shows the order in which lines run when `fun2` calls `fun1`: the *before* lines go in, the *after* lines come out in reverse. Recursion is exactly this picture with the same function on every level.")
    yield multi('''
        Before Function 2
        Before Function 1
        Function 1 is called
        After Function 1
        After Function 2
    ''', py='''
        def fun1():
            print("Function 1 is called")

        def fun2():
            print("Before Function 1")
            fun1()                       # fun2 pauses here until fun1 returns
            print("After Function 1")

        print("Before Function 2")
        fun2()
        print("After Function 2")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        void fun1() {
            cout << "Function 1 is called\n";
        }

        void fun2() {
            cout << "Before Function 1\n";
            fun1();                      // fun2 pauses here until fun1 returns
            cout << "After Function 1\n";
        }

        int main() {
            cout << "Before Function 2\n";
            fun2();
            cout << "After Function 2\n";
        }
    ''', java=r'''
        public class Main {
            static void fun1() {
                System.out.println("Function 1 is called");
            }

            static void fun2() {
                System.out.println("Before Function 1");
                fun1();                  // fun2 pauses here until fun1 returns
                System.out.println("After Function 1");
            }

            public static void main(String[] args) {
                System.out.println("Before Function 2");
                fun2();
                System.out.println("After Function 2");
            }
        }
    ''', js=r'''
        function fun1() {
            console.log("Function 1 is called");
        }

        function fun2() {
            console.log("Before Function 1");
            fun1();                      // fun2 pauses here until fun1 returns
            console.log("After Function 1");
        }

        console.log("Before Function 2");
        fun2();
        console.log("After Function 2");
    ''')
    yield p("Every active call lives in a **frame** on the call stack holding its parameters, local variables and the point to return to. A recursive function has one frame per pending call, so `fact(3)` builds three frames before the first multiplication happens:")
    yield diagram('''
        fact(3)                      call stack (top = running)        returns
          └─ 3 * fact(2)             ┌──────────┐
               └─ 2 * fact(1)        │ fact(0)  │  → 1                 1
                    └─ 1 * fact(0)   │ fact(1)  │  → 1 * 1             1
                         └─ 1        │ fact(2)  │  → 2 * 1             2
                                     │ fact(3)  │  → 3 * 2             6
                                     └──────────┘
        frames are pushed going down (3, 2, 1, 0) and popped coming back up (0, 1, 2, 3)
    ''', "The call stack while computing fact(3)")

    yield section("Typical structure of a recursive function", "list-check")
    yield p("Every correct recursive function has the same two parts. Get either one wrong and the function never terminates — that is a **stack overflow**, not an infinite loop, because each call allocates a frame until memory runs out.")
    yield steps(
        ("Base case(s) first", "The smallest input, answered directly: `if n == 0: return 1`. There can be several (`n == 0 or n == 1` for Fibonacci)."),
        ("Recursive case", "Call the function on a **strictly smaller** input (`n − 1`, `n // 2`, a shorter string, a subtree) and combine the result with the current level's work."),
        ("Convince yourself it ends", "Each call must move towards a base case: `n − 1` reaches `0`; `n // 2` reaches `0`; `start + 1` reaches `end`. A call with the *same* parameters is an infinite recursion."),
    )
    yield diagram('''
        def fun(parameters):
            if base case:                 # answer directly, no call
                return simple answer
            # at least one parameter changes so the call moves towards the base case
            return combine(current work, fun(smaller parameters))
    ''', "Template of a recursive function")
    yield pitfall("`fact(n)` with the base case `n == 1` instead of `n == 0` is the original notes' own warning: `fact(0)` never hits the base case and recurses to `−1, −2, …` for ever. Pick the base case that every valid input can actually reach.")

    yield section("Where recursion is used", "apps")
    yield cards(
        ("Divide and conquer", "Binary search, merge sort, quick sort: split the input, solve the parts recursively, combine. The recurrence `T(n) = 2T(n/2) + n` of merge sort comes straight from the code.", "arrows-split"),
        ("Dynamic programming", "A recursive definition of the answer (`fib(n) = fib(n−1) + fib(n−2)`) plus memoisation of repeated sub-problems — recursion with a cache.", "table"),
        ("Backtracking", "Permutations, N-Queens, sudoku: choose, recurse, un-choose. The call stack *is* the path of choices made so far.", "route"),
        ("Inherently recursive structures", "Trees and graphs: pre-order, in-order, post-order traversal and DFS are each a few lines recursively and clumsy without a stack.", "binary-tree"),
        ("Tower of Hanoi", "Move `n − 1` discs aside, move the big one, move the `n − 1` back: `T(n) = 2T(n−1) + 1 = 2ⁿ − 1` moves — the textbook example of exponential recursion.", "stack-3"),
        ("Parsers and evaluators", "Expressions contain sub-expressions; JSON contains JSON. Recursive-descent parsing mirrors the grammar.", "braces"),
        cols=3,
    )

    yield section("Factorial and Fibonacci: two shapes of recursion", "git-branch")
    yield io("fact(5)", "120", "fib(10)", "55  (0 1 1 2 3 5 8 13 21 34 55)")
    yield p("Factorial makes **one** recursive call per level: `n` calls in total, `O(n)` time. Fibonacci as written in the definition makes **two**: `fib(n−1)` and `fib(n−2)` each recompute the same values again and again, so the number of calls grows like `2 · fib(n+1) − 1` — exponential. The program counts the calls to make this visible.")
    yield diagram('''
                            fib(5)
                       /             \\
                  fib(4)              fib(3)
                 /      \\            /      \\
             fib(3)    fib(2)    fib(2)    fib(1)
            /     \\    /    \\    /    \\
        fib(2) fib(1) fib(1) fib(0) fib(1) fib(0)
        /    \\
    fib(1) fib(0)                 fib(3) is computed twice, fib(2) three times
    ''', "The call tree of naive fib(5): 15 calls for an answer of 5")
    yield multi('''
        fact(5) = 120 in 6 calls
        fact(10) = 3628800 in 11 calls
        fib(5) = 5 in 15 calls
        fib(10) = 55 in 177 calls
        fib(20) = 6765 in 21891 calls
    ''', py='''
        calls = 0

        def fact(n):                  # one call per level: O(n)
            global calls
            calls += 1
            if n == 0:                # base case: 0! = 1
                return 1
            return n * fact(n - 1)

        def fib(n):                   # two calls per level: O(2^n) — the same values recomputed
            global calls
            calls += 1
            if n == 0 or n == 1:      # two base cases: fib(0) = 0, fib(1) = 1
                return n
            return fib(n - 1) + fib(n - 2)

        for n in (5, 10):
            calls = 0
            print(f"fact({n}) = {fact(n)} in {calls} calls")
        for n in (5, 10, 20):
            calls = 0
            print(f"fib({n}) = {fib(n)} in {calls} calls")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long calls = 0;

        long long fact(int n) {           // one call per level: O(n)
            calls++;
            if (n == 0) return 1;         // base case: 0! = 1
            return n * fact(n - 1);
        }

        long long fib(int n) {            // two calls per level: O(2^n) — the same values recomputed
            calls++;
            if (n == 0 || n == 1) return n;   // two base cases
            return fib(n - 1) + fib(n - 2);
        }

        int main() {
            for (int n : {5, 10}) {
                calls = 0;
                long long r = fact(n);
                cout << "fact(" << n << ") = " << r << " in " << calls << " calls\n";
            }
            for (int n : {5, 10, 20}) {
                calls = 0;
                long long r = fib(n);
                cout << "fib(" << n << ") = " << r << " in " << calls << " calls\n";
            }
        }
    ''', java=r'''
        public class Main {
            static long calls = 0;

            static long fact(int n) {             // one call per level: O(n)
                calls++;
                if (n == 0) return 1;             // base case: 0! = 1
                return n * fact(n - 1);
            }

            static long fib(int n) {              // two calls per level: O(2^n) — the same values recomputed
                calls++;
                if (n == 0 || n == 1) return n;   // two base cases
                return fib(n - 1) + fib(n - 2);
            }

            public static void main(String[] args) {
                for (int n : new int[]{5, 10}) {
                    calls = 0;
                    long r = fact(n);
                    System.out.println("fact(" + n + ") = " + r + " in " + calls + " calls");
                }
                for (int n : new int[]{5, 10, 20}) {
                    calls = 0;
                    long r = fib(n);
                    System.out.println("fib(" + n + ") = " + r + " in " + calls + " calls");
                }
            }
        }
    ''', js=r'''
        let calls = 0;

        function fact(n) {                // one call per level: O(n)
            calls++;
            if (n === 0) return 1;        // base case: 0! = 1
            return n * fact(n - 1);
        }

        function fib(n) {                 // two calls per level: O(2^n) — the same values recomputed
            calls++;
            if (n === 0 || n === 1) return n;   // two base cases
            return fib(n - 1) + fib(n - 2);
        }

        for (const n of [5, 10]) {
            calls = 0;
            const r = fact(n);
            console.log(`fact(${n}) = ${r} in ${calls} calls`);
        }
        for (const n of [5, 10, 20]) {
            calls = 0;
            const r = fib(n);
            console.log(`fib(${n}) = ${r} in ${calls} calls`);
        }
    ''')
    yield complexity("fact: O(n); naive fib: O(φⁿ) ≈ O(1.618ⁿ)", "O(n) call stack for both")
    yield note("`fib(20)` already needs 21 891 calls; `fib(50)` would need about 4·10¹⁰. The fix is **memoisation** — store each `fib(k)` the first time it is computed — which turns the tree into a line of `n` calls (`O(n)`). That is the entry point to dynamic programming. The original notes' series `0 1 1 2 3 5 8 12 20` had typos: it continues `13 21`.")

    yield section("Tail recursion", "arrow-big-right-line")
    yield define("Tail-recursive function", "a recursive function whose recursive call is the **last thing it does** — nothing happens after the call returns. Because the frame has no more work, a compiler can reuse it for the next call (tail-call optimisation), making the recursion as cheap as a loop.")
    yield p("Compare the two print functions from the notes. In the first the call is in tail position; in the second the `print` runs *after* the call returns, so the frame must be kept alive — it is **not** tail recursive even though the code looks almost identical.")
    yield multi('''
        tail recursive (print, then recurse): 5 4 3 2 1
        not tail recursive (recurse, then print): 1 2 3 4 5
    ''', py='''
        def fun_tail(n):
            if n == 0:
                return
            print(n, end=" ")
            fun_tail(n - 1)          # last action: tail recursive

        def fun_not_tail(n):
            if n == 0:
                return
            fun_not_tail(n - 1)
            print(n, end=" ")        # work after the call: NOT tail recursive

        print("tail recursive (print, then recurse):", end=" ")
        fun_tail(5)
        print()
        print("not tail recursive (recurse, then print):", end=" ")
        fun_not_tail(5)
        print()
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        void funTail(int n) {
            if (n == 0) return;
            cout << n << " ";
            funTail(n - 1);            // last action: tail recursive
        }

        void funNotTail(int n) {
            if (n == 0) return;
            funNotTail(n - 1);
            cout << n << " ";          // work after the call: NOT tail recursive
        }

        int main() {
            cout << "tail recursive (print, then recurse): ";
            funTail(5);
            cout << "\n";
            cout << "not tail recursive (recurse, then print): ";
            funNotTail(5);
            cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static void funTail(int n) {
                if (n == 0) return;
                System.out.print(n + " ");
                funTail(n - 1);            // last action: tail recursive
            }

            static void funNotTail(int n) {
                if (n == 0) return;
                funNotTail(n - 1);
                System.out.print(n + " ");  // work after the call: NOT tail recursive
            }

            public static void main(String[] args) {
                System.out.print("tail recursive (print, then recurse): ");
                funTail(5);
                System.out.println();
                System.out.print("not tail recursive (recurse, then print): ");
                funNotTail(5);
                System.out.println();
            }
        }
    ''', js=r'''
        let line = "";

        function funTail(n) {
            if (n === 0) return;
            line += n + " ";
            funTail(n - 1);            // last action: tail recursive
        }

        function funNotTail(n) {
            if (n === 0) return;
            funNotTail(n - 1);
            line += n + " ";           // work after the call: NOT tail recursive
        }

        line = "tail recursive (print, then recurse): ";
        funTail(5);
        console.log(line.trim());
        line = "not tail recursive (recurse, then print): ";
        funNotTail(5);
        console.log(line.trim());
    ''')
    yield complexity("O(n) both", "O(n) stack — O(1) for the tail version only if the compiler optimises tail calls")
    yield table(
        ["Function", "Tail recursive?", "Why"],
        ["print `N..1` (print, then call)", "yes", "the call is the last statement"],
        ["print `1..N` (call, then print)", "no", "prints after the call returns"],
        ["`fact(n) = n * fact(n − 1)`", "no", "the multiplication happens after the call"],
        ["`fact(n, acc) = fact(n − 1, n * acc)`", "yes", "the multiplication is done *before* the call, in the argument"],
        ["Quick sort (second call)", "yes", "sort the left part, then the last action is sorting the right part"],
        ["Merge sort, post-order traversal", "no", "work (merge / visit the node) happens after the calls return"],
        ["Binary search (recursive)", "yes", "returns the result of the single recursive call"],
    )
    yield p("A non-tail function can often be made tail-recursive by carrying the partial result in an **accumulator** parameter — the multiplication moves from *after* the call to *before* it:")
    yield multi('''
        fact(5) = 120
        fact_tail(5, 1) = 120
        fact(10) = 3628800
        fact_tail(10, 1) = 3628800
    ''', py='''
        def fact(n):                       # not tail recursive: multiplies after the call returns
            if n == 0:
                return 1
            return n * fact(n - 1)

        def fact_tail(n, acc=1):           # tail recursive: the running product travels in acc
            if n == 0:
                return acc
            return fact_tail(n - 1, n * acc)   # nothing left to do after this call

        for n in (5, 10):
            print(f"fact({n}) = {fact(n)}")
            print(f"fact_tail({n}, 1) = {fact_tail(n)}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        long long fact(int n) {                    // not tail recursive: multiplies after the call returns
            if (n == 0) return 1;
            return n * fact(n - 1);
        }

        long long factTail(int n, long long acc) { // tail recursive: the running product travels in acc
            if (n == 0) return acc;
            return factTail(n - 1, n * acc);       // nothing left to do after this call
        }

        int main() {
            for (int n : {5, 10}) {
                cout << "fact(" << n << ") = " << fact(n) << "\n";
                cout << "fact_tail(" << n << ", 1) = " << factTail(n, 1) << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static long fact(int n) {                  // not tail recursive: multiplies after the call returns
                if (n == 0) return 1;
                return n * fact(n - 1);
            }

            static long factTail(int n, long acc) {    // tail recursive: the running product travels in acc
                if (n == 0) return acc;
                return factTail(n - 1, n * acc);       // nothing left to do after this call
            }

            public static void main(String[] args) {
                for (int n : new int[]{5, 10}) {
                    System.out.println("fact(" + n + ") = " + fact(n));
                    System.out.println("fact_tail(" + n + ", 1) = " + factTail(n, 1));
                }
            }
        }
    ''', js=r'''
        function fact(n) {                     // not tail recursive: multiplies after the call returns
            if (n === 0) return 1;
            return n * fact(n - 1);
        }

        function factTail(n, acc = 1) {        // tail recursive: the running product travels in acc
            if (n === 0) return acc;
            return factTail(n - 1, n * acc);   // nothing left to do after this call
        }

        for (const n of [5, 10]) {
            console.log(`fact(${n}) = ${fact(n)}`);
            console.log(`fact_tail(${n}, 1) = ${factTail(n)}`);
        }
    ''')
    yield complexity("O(n)", "O(n) stack; O(1) with tail-call optimisation")
    yield warn("Tail-call optimisation is **not** guaranteed: C++ compilers do it at `-O2`, Java and Python never do, and JavaScript engines other than Safari dropped it. So in these four languages a tail-recursive function still uses `O(n)` stack — the real benefit is that a tail-recursive function converts to a loop *mechanically*, which is the next section.", "Do not rely on the optimisation")

    yield section("Removing recursion: converting to a loop", "refresh")
    yield p("Because a tail call passes nothing back, the recursion can be replaced by a loop in two mechanical edits (the original notes' recipe):")
    yield steps(
        ("Replace `if` with `while`", "The base-case test `if n == 0: return` becomes the loop condition `while n != 0:`."),
        ("Update the parameters at the end of the loop body", "The tail call `fun(n − 1)` becomes the assignment `n = n − 1` as the last statement."),
    )
    yield diagram('''
        tail recursive                         loop
        ─────────────────────────────          ─────────────────────────────
        def fun(n):                            def fun(n):
            if n == 0: return                      while n != 0:
            print(n)                                   print(n)
            fun(n - 1)                                 n = n - 1
    ''', "The two edits that turn a tail call into a loop")
    yield p("A **non**-tail function cannot be converted this way because the frame must remember what to do after the call. It can still be made iterative with an explicit stack (that is how iterative DFS and in-order traversal work) or, as with factorial, by moving the pending work into an accumulator first.")
    yield multi('''
        recursive: 5 4 3 2 1
        loop: 5 4 3 2 1
        sum of 1..100 recursive: 5050
        sum of 1..100 loop: 5050
    ''', py='''
        def print_recursive(n):
            if n == 0:
                return
            print(n, end=" ")
            print_recursive(n - 1)

        def print_loop(n):                 # if → while, tail call → parameter update
            while n != 0:
                print(n, end=" ")
                n = n - 1

        def sum_recursive(n, acc=0):       # tail recursive with an accumulator …
            if n == 0:
                return acc
            return sum_recursive(n - 1, acc + n)

        def sum_loop(n):                   # … becomes a loop with the same accumulator
            acc = 0
            while n != 0:
                acc = acc + n
                n = n - 1
            return acc

        print("recursive:", end=" "); print_recursive(5); print()
        print("loop:", end=" "); print_loop(5); print()
        print("sum of 1..100 recursive:", sum_recursive(100))
        print("sum of 1..100 loop:", sum_loop(100))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        void printRecursive(int n) {
            if (n == 0) return;
            cout << n << " ";
            printRecursive(n - 1);
        }

        void printLoop(int n) {                  // if → while, tail call → parameter update
            while (n != 0) {
                cout << n << " ";
                n = n - 1;
            }
        }

        int sumRecursive(int n, int acc) {       // tail recursive with an accumulator …
            if (n == 0) return acc;
            return sumRecursive(n - 1, acc + n);
        }

        int sumLoop(int n) {                     // … becomes a loop with the same accumulator
            int acc = 0;
            while (n != 0) { acc = acc + n; n = n - 1; }
            return acc;
        }

        int main() {
            cout << "recursive: "; printRecursive(5); cout << "\n";
            cout << "loop: "; printLoop(5); cout << "\n";
            cout << "sum of 1..100 recursive: " << sumRecursive(100, 0) << "\n";
            cout << "sum of 1..100 loop: " << sumLoop(100) << "\n";
        }
    ''', java=r'''
        public class Main {
            static void printRecursive(int n) {
                if (n == 0) return;
                System.out.print(n + " ");
                printRecursive(n - 1);
            }

            static void printLoop(int n) {               // if → while, tail call → parameter update
                while (n != 0) {
                    System.out.print(n + " ");
                    n = n - 1;
                }
            }

            static int sumRecursive(int n, int acc) {    // tail recursive with an accumulator …
                if (n == 0) return acc;
                return sumRecursive(n - 1, acc + n);
            }

            static int sumLoop(int n) {                  // … becomes a loop with the same accumulator
                int acc = 0;
                while (n != 0) { acc = acc + n; n = n - 1; }
                return acc;
            }

            public static void main(String[] args) {
                System.out.print("recursive: "); printRecursive(5); System.out.println();
                System.out.print("loop: "); printLoop(5); System.out.println();
                System.out.println("sum of 1..100 recursive: " + sumRecursive(100, 0));
                System.out.println("sum of 1..100 loop: " + sumLoop(100));
            }
        }
    ''', js=r'''
        function printRecursive(n, parts) {
            if (n === 0) return;
            parts.push(n);
            printRecursive(n - 1, parts);
        }

        function printLoop(n, parts) {           // if → while, tail call → parameter update
            while (n !== 0) {
                parts.push(n);
                n = n - 1;
            }
        }

        function sumRecursive(n, acc = 0) {      // tail recursive with an accumulator …
            if (n === 0) return acc;
            return sumRecursive(n - 1, acc + n);
        }

        function sumLoop(n) {                    // … becomes a loop with the same accumulator
            let acc = 0;
            while (n !== 0) { acc = acc + n; n = n - 1; }
            return acc;
        }

        let parts = []; printRecursive(5, parts); console.log("recursive:", parts.join(" "));
        parts = []; printLoop(5, parts); console.log("loop:", parts.join(" "));
        console.log("sum of 1..100 recursive:", sumRecursive(100));
        console.log("sum of 1..100 loop:", sumLoop(100));
    ''')
    yield complexity("O(n)", "O(n) recursive, O(1) loop")

    yield section("Tracing recursive functions", "search")
    yield p("Interviews love “what does this print?”. The method: write the calls as a tree, mark what happens **before** the recursive call (on the way down) and **after** it (on the way up), then read the output in order. Four puzzles from the notes, solved by the program:")
    yield table(
        ["Function", "Before the call", "After the call", "Output for the input", "What it computes"],
        ["print, call `n − 1`, print", "`n`", "`n`", "`4 3 2 1 1 2 3 4`", "the sequence down, then mirrored back up"],
        ["call `n − 1`, print, call `n − 1`", "—", "`n`, then a second subtree", "`1 2 1 3 1 2 1 4 1 2 1 3 1 2 1`", "`2ⁿ − 1` numbers — the ruler pattern; `O(2ⁿ)`"],
        ["`1 + fun(n // 2)` until `n ≤ 1`", "—", "add 1", "`fun(16) = 4`, `fun(13) = 3`", "how many times `n` can be halved: `⌊log₂ n⌋`"],
        ["call `n // 2`, print `n % 2`", "—", "print the bit", "`fun(13) = 1101`", "binary representation, most significant bit first"],
    )
    yield multi('''
        before and after, n = 4: 4 3 2 1 1 2 3 4
        double recursion, n = 4: 1 2 1 3 1 2 1 4 1 2 1 3 1 2 1
        halvings of 16: 4
        halvings of 13: 3
        binary of 13: 1101
        binary of 32: 100000
    ''', py='''
        def before_after(n):
            if n == 0:
                return
            print(n, end=" ")             # on the way down
            before_after(n - 1)
            print(n, end=" ")             # on the way up

        def double(n):
            if n == 0:
                return
            double(n - 1)
            print(n, end=" ")
            double(n - 1)                 # the whole left subtree printed again

        def halvings(n):                  # how many times can n be halved? floor(log2 n)
            if n <= 1:
                return 0
            return 1 + halvings(n // 2)

        def binary(n):                    # recurse first so the most significant bit prints first
            if n == 0:
                return
            binary(n // 2)
            print(n % 2, end="")

        print("before and after, n = 4:", end=" "); before_after(4); print()
        print("double recursion, n = 4:", end=" "); double(4); print()
        print("halvings of 16:", halvings(16))
        print("halvings of 13:", halvings(13))
        print("binary of 13:", end=" "); binary(13); print()
        print("binary of 32:", end=" "); binary(32); print()
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        void beforeAfter(int n) {
            if (n == 0) return;
            cout << n << " ";             // on the way down
            beforeAfter(n - 1);
            cout << n << " ";             // on the way up
        }

        void doubleRec(int n) {
            if (n == 0) return;
            doubleRec(n - 1);
            cout << n << " ";
            doubleRec(n - 1);             // the whole left subtree printed again
        }

        int halvings(int n) {             // how many times can n be halved? floor(log2 n)
            if (n <= 1) return 0;
            return 1 + halvings(n / 2);
        }

        void binary(int n) {              // recurse first so the most significant bit prints first
            if (n == 0) return;
            binary(n / 2);
            cout << n % 2;
        }

        int main() {
            cout << "before and after, n = 4: "; beforeAfter(4); cout << "\n";
            cout << "double recursion, n = 4: "; doubleRec(4); cout << "\n";
            cout << "halvings of 16: " << halvings(16) << "\n";
            cout << "halvings of 13: " << halvings(13) << "\n";
            cout << "binary of 13: "; binary(13); cout << "\n";
            cout << "binary of 32: "; binary(32); cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static void beforeAfter(int n) {
                if (n == 0) return;
                System.out.print(n + " ");    // on the way down
                beforeAfter(n - 1);
                System.out.print(n + " ");    // on the way up
            }

            static void doubleRec(int n) {
                if (n == 0) return;
                doubleRec(n - 1);
                System.out.print(n + " ");
                doubleRec(n - 1);             // the whole left subtree printed again
            }

            static int halvings(int n) {      // how many times can n be halved? floor(log2 n)
                if (n <= 1) return 0;
                return 1 + halvings(n / 2);
            }

            static void binary(int n) {       // recurse first so the most significant bit prints first
                if (n == 0) return;
                binary(n / 2);
                System.out.print(n % 2);
            }

            public static void main(String[] args) {
                System.out.print("before and after, n = 4: "); beforeAfter(4); System.out.println();
                System.out.print("double recursion, n = 4: "); doubleRec(4); System.out.println();
                System.out.println("halvings of 16: " + halvings(16));
                System.out.println("halvings of 13: " + halvings(13));
                System.out.print("binary of 13: "); binary(13); System.out.println();
                System.out.print("binary of 32: "); binary(32); System.out.println();
            }
        }
    ''', js=r'''
        let out = [];

        function beforeAfter(n) {
            if (n === 0) return;
            out.push(n);                  // on the way down
            beforeAfter(n - 1);
            out.push(n);                  // on the way up
        }

        function doubleRec(n) {
            if (n === 0) return;
            doubleRec(n - 1);
            out.push(n);
            doubleRec(n - 1);             // the whole left subtree printed again
        }

        function halvings(n) {            // how many times can n be halved? floor(log2 n)
            if (n <= 1) return 0;
            return 1 + halvings(Math.floor(n / 2));
        }

        function binary(n) {              // recurse first so the most significant bit prints first
            if (n === 0) return;
            binary(Math.floor(n / 2));
            out.push(n % 2);
        }

        out = []; beforeAfter(4); console.log("before and after, n = 4:", out.join(" "));
        out = []; doubleRec(4); console.log("double recursion, n = 4:", out.join(" "));
        console.log("halvings of 16:", halvings(16));
        console.log("halvings of 13:", halvings(13));
        out = []; binary(13); console.log("binary of 13:", out.join(""));
        out = []; binary(32); console.log("binary of 32:", out.join(""));
    ''')
    yield complexity("O(n), O(2ⁿ), O(log n), O(log n) respectively", "O(n) / O(n) / O(log n) / O(log n) stack")
    yield note("`binary(n)` is the general trick for **reversing the order of output**: do the recursive call first and print on the way back up. Printing `n % 2` *before* the call would give the bits least-significant first (`1011`).")

    yield section("Problem: print 1 to N and N to 1", "list-numbers")
    yield io("n = 4", "1 2 3 4   and   4 3 2 1")
    yield idea("With no loop allowed, the only question is *where the print goes*. Print **after** the recursive call and the numbers come out in increasing order (the deepest call, `1`, prints first); print **before** it and they come out decreasing. Same function, one line moved.")
    yield multi('''
        1 to 4: 1 2 3 4
        4 to 1: 4 3 2 1
        1 to 7: 1 2 3 4 5 6 7
        7 to 1: 7 6 5 4 3 2 1
    ''', py='''
        def print_1_to_n(n):
            if n == 0:
                return
            print_1_to_n(n - 1)         # first everything below n …
            print(n, end=" ")           # … then n: ascending (not tail recursive)

        def print_n_to_1(n):
            if n == 0:
                return
            print(n, end=" ")           # n first …
            print_n_to_1(n - 1)         # … then everything below: descending (tail recursive)

        for n in (4, 7):
            print(f"1 to {n}:", end=" "); print_1_to_n(n); print()
            print(f"{n} to 1:", end=" "); print_n_to_1(n); print()
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        void print1ToN(int n) {
            if (n == 0) return;
            print1ToN(n - 1);           // first everything below n …
            cout << n << " ";           // … then n: ascending (not tail recursive)
        }

        void printNTo1(int n) {
            if (n == 0) return;
            cout << n << " ";           // n first …
            printNTo1(n - 1);           // … then everything below: descending (tail recursive)
        }

        int main() {
            for (int n : {4, 7}) {
                cout << "1 to " << n << ": "; print1ToN(n); cout << "\n";
                cout << n << " to 1: "; printNTo1(n); cout << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static void print1ToN(int n) {
                if (n == 0) return;
                print1ToN(n - 1);               // first everything below n …
                System.out.print(n + " ");      // … then n: ascending (not tail recursive)
            }

            static void printNTo1(int n) {
                if (n == 0) return;
                System.out.print(n + " ");      // n first …
                printNTo1(n - 1);               // … then everything below: descending (tail recursive)
            }

            public static void main(String[] args) {
                for (int n : new int[]{4, 7}) {
                    System.out.print("1 to " + n + ": "); print1ToN(n); System.out.println();
                    System.out.print(n + " to 1: "); printNTo1(n); System.out.println();
                }
            }
        }
    ''', js=r'''
        function print1ToN(n, parts) {
            if (n === 0) return;
            print1ToN(n - 1, parts);    // first everything below n …
            parts.push(n);              // … then n: ascending (not tail recursive)
        }

        function printNTo1(n, parts) {
            if (n === 0) return;
            parts.push(n);              // n first …
            printNTo1(n - 1, parts);    // … then everything below: descending (tail recursive)
        }

        for (const n of [4, 7]) {
            let parts = []; print1ToN(n, parts); console.log(`1 to ${n}: ${parts.join(" ")}`);
            parts = []; printNTo1(n, parts); console.log(`${n} to 1: ${parts.join(" ")}`);
        }
    ''')
    yield complexity("O(n)", "O(n) call stack")
    yield pitfall("Both functions are `O(n)` deep: `print_1_to_n(100000)` overflows the stack in every one of these languages (Python gives up at ~1000). Recursion is the *exercise* here; a loop is the production answer.")

    yield section("Problem: sum of digits", "sum")
    yield io("n = 253", "10  (2 + 5 + 3)", "n = 9", "9")
    yield idea("The last digit is `n % 10` and the rest of the number is `n // 10`. So `sum(n) = sum(n // 10) + n % 10`, with the base case that a single digit (`n < 10`) is its own sum. One call per digit.")
    yield multi('''
        253 → 10
        9 → 9
        99999 → 45
        1000 → 1
    ''', py='''
        def sum_of_digits(n):
            if n < 10:                            # base case: a single digit
                return n
            return sum_of_digits(n // 10) + n % 10   # digits of the rest + the last digit

        for n in (253, 9, 99999, 1000):
            print(n, "→", sum_of_digits(n))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        int sumOfDigits(int n) {
            if (n < 10) return n;                 // base case: a single digit
            return sumOfDigits(n / 10) + n % 10;  // digits of the rest + the last digit
        }

        int main() {
            for (int n : {253, 9, 99999, 1000})
                cout << n << " → " << sumOfDigits(n) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int sumOfDigits(int n) {
                if (n < 10) return n;                 // base case: a single digit
                return sumOfDigits(n / 10) + n % 10;  // digits of the rest + the last digit
            }

            public static void main(String[] args) {
                for (int n : new int[]{253, 9, 99999, 1000})
                    System.out.println(n + " → " + sumOfDigits(n));
            }
        }
    ''', js=r'''
        function sumOfDigits(n) {
            if (n < 10) return n;                               // base case: a single digit
            return sumOfDigits(Math.floor(n / 10)) + (n % 10);  // digits of the rest + the last digit
        }

        for (const n of [253, 9, 99999, 1000])
            console.log(n, "→", sumOfDigits(n));
    ''')
    yield complexity("O(d) — one call per digit", "O(d) call stack")

    yield section("Problem: palindrome check of a string", "arrows-left-right")
    yield io("s = \"aabbaa\"", "Yes", "s = \"abcba\"", "Yes", "s = \"abca\"", "No")
    yield idea("Compare the outer characters, then ask the same question about the string without them: `palin(s, start, end) = s[start] == s[end] and palin(s, start + 1, end − 1)`. When `start >= end` (zero or one character left) the answer is trivially yes. Two indices avoid copying substrings.")
    yield diagram('''
        s = a a b b a a       start = 0, end = 5   a == a ✓
              a b b a         start = 1, end = 4   a == a ✓
                b b           start = 2, end = 3   b == b ✓
                              start = 3, end = 2   start >= end → True
    ''', "palin(\"aabbaa\", 0, 5) — the window shrinks from both ends")
    yield multi('''
        aabbaa → Yes
        abcba → Yes
        abca → No
        a → Yes
         → Yes
    ''', py='''
        def is_palindrome(s, start, end):
            if start >= end:                       # 0 or 1 characters left
                return True
            return s[start] == s[end] and is_palindrome(s, start + 1, end - 1)

        for s in ["aabbaa", "abcba", "abca", "a", ""]:
            print(s, "→", "Yes" if is_palindrome(s, 0, len(s) - 1) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        using namespace std;

        bool isPalindrome(const string& s, int start, int end) {
            if (start >= end) return true;         // 0 or 1 characters left
            return s[start] == s[end] && isPalindrome(s, start + 1, end - 1);
        }

        int main() {
            for (string s : {"aabbaa", "abcba", "abca", "a", ""}) {
                int n = s.size();
                cout << s << " → " << (isPalindrome(s, 0, n - 1) ? "Yes" : "No") << "\n";
            }
        }
    ''', java=r'''
        public class Main {
            static boolean isPalindrome(String s, int start, int end) {
                if (start >= end) return true;     // 0 or 1 characters left
                return s.charAt(start) == s.charAt(end) && isPalindrome(s, start + 1, end - 1);
            }

            public static void main(String[] args) {
                for (String s : new String[]{"aabbaa", "abcba", "abca", "a", ""})
                    System.out.println(s + " → " + (isPalindrome(s, 0, s.length() - 1) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        function isPalindrome(s, start, end) {
            if (start >= end) return true;         // 0 or 1 characters left
            return s[start] === s[end] && isPalindrome(s, start + 1, end - 1);
        }

        for (const s of ["aabbaa", "abcba", "abca", "a", ""])
            console.log(s, "→", isPalindrome(s, 0, s.length - 1) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n) call stack")
    yield pitfall("The original notes gave `\"aabbaa\" → False`; it **is** a palindrome (`a a b | b a a`). Also note the `and` short-circuits: as soon as one pair differs the recursion stops, so a mismatch at the ends costs `O(1)`.")

    yield section("Recursion vs iteration", "arrows-exchange")
    yield table(
        ["", "Recursion", "Iteration"],
        ["Code", "mirrors the mathematical definition; short for trees, graphs, divide and conquer", "explicit state; short for simple counting"],
        ["Memory", "`O(depth)` call stack, hidden", "`O(1)` or an explicit stack you control"],
        ["Speed", "function-call overhead per step", "none"],
        ["Risk", "stack overflow on deep input; exponential blow-up without memoisation", "off-by-one errors, state bugs"],
        ["Convertible?", "tail recursion → loop mechanically; other recursion → loop + explicit stack", "any loop can be written recursively"],
    )
    yield cards(
        ("Missing or unreachable base case", "`fact` with base case `n == 1` loops for ever on `0`. Test the smallest inputs first.", "alert-triangle"),
        ("Not shrinking the input", "A call with the same arguments is infinite recursion: `fun(n)` calling `fun(n)`.", "repeat-off"),
        ("Exponential recomputation", "Two calls per level that overlap (`fib`) — memoise, or rewrite bottom-up.", "chart-arrows"),
        ("Deep recursion", "Depth `n = 10⁵` overflows the stack. Use a loop, an explicit stack, or raise the limit only when you know the depth.", "stack-3"),
        cols=2,
    )

    yield section("Interview Q&A", "message-question")
    yield qa("What is a base case and what happens without one?",
             "The input the function answers directly without calling itself (`n == 0` for factorial, an empty subtree for a traversal). Without a reachable base case every call pushes another frame and the program dies with a stack overflow (`RecursionError` in Python after about 1000 frames). Always check the base case against the smallest valid inputs — `0`, `1`, empty.")
    yield qa("What is tail recursion and why does it matter?",
             "A recursive call in tail position: nothing is done after it returns. The frame can be discarded before the call, so an optimising compiler turns it into a jump (`O(1)` stack), and a programmer can turn it into a loop with two edits: `if → while`, call → parameter update. Factorial becomes tail recursive by passing the running product as an accumulator. Python, Java and most JavaScript engines do *not* optimise tail calls, so convert by hand when depth matters.")
    yield qa("How do you find the time complexity of a recursive function?",
             "Write the recurrence: calls per level × size reduction + work per call. `T(n) = T(n−1) + 1 → O(n)` (factorial), `T(n) = T(n/2) + 1 → O(log n)` (halving, binary search), `T(n) = 2T(n−1) + 1 → O(2ⁿ)` (the double-recursion puzzle, Tower of Hanoi), `T(n) = 2T(n/2) + n → O(n log n)` (merge sort). The Analysis of Algorithms topic covers solving them.")
    yield qa("What is the space complexity of a recursive function?",
             "At least the maximum depth of the call stack, because every pending call keeps a frame: `O(n)` for factorial and `print 1..n`, `O(log n)` for halving functions, `O(height)` for a tree traversal. Depth, not total number of calls: naive `fib(n)` makes `O(2ⁿ)` calls but is only `n` deep, so it uses `O(n)` stack.")
    yield qa("Why is naive recursive Fibonacci slow and how do you fix it?",
             "`fib(n)` calls `fib(n−1)` and `fib(n−2)`, which both recompute `fib(n−3)`, and so on — about `2 · fib(n+1)` calls, exponential. Memoise (store results in a dictionary or array, `O(n)` time and space) or compute bottom-up with two variables (`O(n)` time, `O(1)` space). Fast exponentiation of the matrix `[[1,1],[1,0]]` gives `O(log n)`.")
    yield qa("Direct vs indirect recursion?",
             "Direct: a function calls itself. Indirect (mutual): `f` calls `g` which calls `f` — for instance `is_even(n) = is_odd(n−1)` and `is_odd(n) = is_even(n−1)` with base cases at `0`, or a recursive-descent parser where `expression` calls `term` which calls `expression` inside parentheses. The base-case and shrinking-input rules apply across the whole cycle.")
