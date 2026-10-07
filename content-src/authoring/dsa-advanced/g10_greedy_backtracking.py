from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Algorithm Paradigms"


@topic(G, "greedy", "Greedy Algorithms", "coin")
def _():
    yield lead("A greedy algorithm builds a solution one piece at a time, always taking the choice that looks best **right now** and never revisiting it. When the problem has the right structure this is the fastest possible approach; when it does not, greedy quietly returns a wrong answer.")
    yield define("Greedy algorithm", "an algorithm that makes the *locally optimal* choice at every step, hoping (or proving) that these local choices add up to a *globally optimal* solution. There is no backtracking and no look-ahead — a choice once made is final.")

    yield section("Minimum coins — the motivating example", "coin")
    yield p("You have an infinite supply of coins of value `10, 5, 2, 1`. Someone asks for an amount — how do you pay it with the **fewest coins**? The natural instinct is greedy: hand over the largest coin that still fits, repeat.")
    yield io("coins = [10, 5, 2, 1], amount = 52", "6  (10 10 10 10 10 2)", "coins = [10, 5, 2, 1], amount = 93", "11  (10 ×9, 2, 1)")
    yield idea("Sort the denominations in decreasing order. For each denomination take as many coins as still fit (`amount // coin`), subtract them and move to the next smaller coin. The amount shrinks fastest when the biggest coin is used first.")
    yield multi('''
        52 → 6 coins: 10 10 10 10 10 2
        93 → 11 coins: 10 10 10 10 10 10 10 10 10 2 1
    ''', py='''
        def min_coins(coins, amount):
            coins = sorted(coins, reverse=True)       # largest denomination first
            picked = []
            for x in coins:
                k = amount // x                       # as many of this coin as still fit
                picked.extend([x] * k)
                amount -= k * x
                if amount == 0:
                    break
            return picked

        for amount in (52, 93):
            picked = min_coins([10, 5, 2, 1], amount)
            print(f"{amount} → {len(picked)} coins: {' '.join(map(str, picked))}")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        vector<int> minCoins(vector<int> coins, int amount) {
            sort(coins.rbegin(), coins.rend());            // largest denomination first
            vector<int> picked;
            for (int x : coins) {
                int k = amount / x;                        // as many of this coin as still fit
                for (int j = 0; j < k; j++) picked.push_back(x);
                amount -= k * x;
                if (amount == 0) break;
            }
            return picked;
        }

        int main() {
            for (int amount : {52, 93}) {
                vector<int> picked = minCoins({10, 5, 2, 1}, amount);
                cout << amount << " → " << picked.size() << " coins:";
                for (int c : picked) cout << " " << c;
                cout << "\\n";
            }
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.Arrays;
        import java.util.List;

        public class Main {
            static List<Integer> minCoins(int[] coins, int amount) {
                int[] c = coins.clone();
                Arrays.sort(c);                                   // ascending …
                List<Integer> picked = new ArrayList<>();
                for (int i = c.length - 1; i >= 0; i--) {         // … so walk it backwards: largest first
                    int k = amount / c[i];                        // as many of this coin as still fit
                    for (int j = 0; j < k; j++) picked.add(c[i]);
                    amount -= k * c[i];
                    if (amount == 0) break;
                }
                return picked;
            }

            public static void main(String[] args) {
                for (int amount : new int[]{52, 93}) {
                    List<Integer> picked = minCoins(new int[]{10, 5, 2, 1}, amount);
                    StringBuilder sb = new StringBuilder();
                    for (int x : picked) sb.append(' ').append(x);
                    System.out.println(amount + " → " + picked.size() + " coins:" + sb);
                }
            }
        }
    ''', js='''
        function minCoins(coins, amount) {
            const sorted = [...coins].sort((a, b) => b - a);   // largest denomination first
            const picked = [];
            for (const x of sorted) {
                const k = Math.floor(amount / x);               // as many of this coin as still fit
                for (let j = 0; j < k; j++) picked.push(x);
                amount -= k * x;
                if (amount === 0) break;
            }
            return picked;
        }

        for (const amount of [52, 93]) {
            const picked = minCoins([10, 5, 2, 1], amount);
            console.log(`${amount} → ${picked.length} coins: ${picked.join(" ")}`);
        }
    ''')
    yield complexity("O(k log k) to sort k denominations, then O(k)", "O(1) extra")
    yield note("This works for `10, 5, 2, 1` (and for every real currency system) because each coin is at least double the next smaller one, so a larger coin never *has* to be replaced by several smaller ones. That is a property of the input, not of greedy in general — see the counterexample below.")

    yield section("General structure of a greedy algorithm", "list-numbers")
    yield p("Every greedy algorithm has the same skeleton: order the candidates by some *selection rule*, then scan them once, keeping each candidate that keeps the partial solution *feasible*.")
    yield diagram('''
        getOptimal(items):
            res = empty solution
            while not all items considered:
                i = selectBestItem()          # the greedy choice (largest coin, earliest finish, …)
                if feasible(res + i):         # does adding i still respect the constraints?
                    res = res + i
            return res
    ''', "Pseudocode of a greedy algorithm — a selection rule plus a feasibility check")
    yield steps(
        ("Define the selection rule", "What makes one candidate *look* better than another? Largest value, earliest finish, highest value-per-weight… This is the whole design — pick it wrong and the algorithm is wrong."),
        ("Sort (or use a heap)", "Usually the candidates are sorted once by the rule, costing `O(n log n)`; Huffman and Dijkstra instead pull the current best from a priority queue."),
        ("Scan once", "Walk the candidates in order; accept each one that is still feasible, skip the rest. No step is ever undone."),
        ("Prove it", "Argue that the greedy choice is always part of *some* optimal solution. Without this step you only have a heuristic."),
    )

    yield section("When greedy works — and when it fails", "alert-triangle")
    yield p("A greedy algorithm is correct only when the problem has two properties:")
    yield cards(
        ("Greedy-choice property", "A globally optimal solution can be reached by making the locally optimal choice first — the first greedy pick is never a mistake. Proved by an **exchange argument**: take any optimal solution that does not contain the greedy choice, swap the greedy choice in, and show the result is no worse.", "check"),
        ("Optimal substructure", "After the greedy choice is made, what remains is a smaller instance of the same problem, and an optimal solution to the whole is the greedy choice plus an optimal solution to the remainder.", "puzzle"),
    )
    yield p("Change the coin system and the greedy-choice property disappears. With coins `18, 10, 1` and amount `20`, greedy grabs `18` first and is then forced to add two `1`s — three coins — while the optimum is `10 + 10`.")
    yield snippet("py", '''
        def greedy(coins, amount):
            count = 0
            for x in sorted(coins, reverse=True):
                count += amount // x
                amount %= x
            return count

        def optimal(coins, amount):                     # dynamic programming — always correct
            best = [0] + [float("inf")] * amount
            for a in range(1, amount + 1):
                for x in coins:
                    if x <= a:
                        best[a] = min(best[a], best[a - x] + 1)
            return best[amount]

        print("greedy :", greedy([18, 1, 10], 20))     # 18 + 1 + 1
        print("optimal:", optimal([18, 1, 10], 20))    # 10 + 10
    ''', out='''
        greedy : 3
        optimal: 2
    ''')
    yield pitfall("Greedy *looks* right on a few hand-made examples far more often than it *is* right. If you cannot state why the greedy choice is safe (an exchange argument), assume it is not and reach for dynamic programming — the 0/1 knapsack, general coin change and longest common subsequence are all problems where greedy fails.")

    yield section("Where greedy is used", "apps")
    yield p("Greedy shines in two situations: problems with a provable greedy-choice property, where it gives the fastest exact algorithm, and hard problems where a fast *approximate* answer is good enough.")
    yield cards(
        ("Activity selection", "Pick the maximum number of non-overlapping intervals — earliest finish first. Solved below.", "calendar"),
        ("Fractional knapsack", "Fill a bag of limited capacity with divisible items — highest value per weight first. Solved below.", "briefcase"),
        ("Job sequencing", "Schedule unit-time jobs with deadlines for maximum profit — highest profit first. Solved below.", "clock"),
        ("Huffman coding", "Build an optimal prefix code — repeatedly merge the two rarest symbols. Solved below.", "file-zip"),
        ("Prim's & Kruskal's", "Minimum spanning tree — always add the cheapest safe edge (see Graphs).", "topology-star"),
        ("Dijkstra's algorithm", "Shortest paths — always settle the closest unsettled vertex (see Graphs).", "route"),
        cols=3,
    )
    yield note("For **NP-hard** problems such as the Travelling Salesman Problem, greedy heuristics (nearest-neighbour, cheapest insertion) are used to get a reasonably good tour quickly, even though they do not guarantee the optimum.", "Approximation")

    yield section("Activity selection problem", "calendar")
    yield p("Given `n` activities with start and finish times, find the **maximum number** of activities a single person (or single-tasking machine) can perform — two activities can both be chosen only if they do not overlap.")
    yield io("activities = [(2, 3), (1, 4), (5, 8), (6, 10)]  as (start, finish)", "2  → (2, 3) and (5, 8)")
    yield idea("Always pick the activity that **finishes earliest** — it frees the machine as soon as possible and leaves the most room for the rest. Picking by shortest duration or earliest start both fail on simple counterexamples.")
    yield steps(
        ("Sort by finish time", "Ascending — the activity ending first comes first."),
        ("Take the first activity", "It is always part of some optimal solution (exchange argument: any optimal solution's first activity can be swapped for this one without creating an overlap)."),
        ("Scan the rest", "If the current activity starts **at or after** the finish of the last chosen one, choose it; otherwise it overlaps — skip it."),
    )
    yield diagram('''
        time  1   2   3   4   5   6   7   8   9   10
        (2,3)     ├───┤                                ✔ chosen (ends first)
        (1,4) ├───────────┤                            ✘ starts at 1 < 3
        (5,8)                 ├───────────┤            ✔ chosen (5 ≥ 3)
        (6,10)                    ├───────────────┤    ✘ starts at 6 < 8
    ''', "Sorted by finish time; a candidate is accepted when it starts no earlier than the last accepted finish")
    yield multi('''
        selected: (2,3) (5,8)
        count: 2
    ''', py='''
        def max_activities(activities):
            activities = sorted(activities, key=lambda a: a[1])   # earliest finish first
            chosen = [activities[0]]
            for start, finish in activities[1:]:
                if start >= chosen[-1][1]:                        # no overlap with the last chosen one
                    chosen.append((start, finish))
            return chosen

        acts = [(2, 3), (1, 4), (5, 8), (6, 10)]
        chosen = max_activities(acts)
        print("selected:", " ".join(f"({s},{f})" for s, f in chosen))
        print("count:", len(chosen))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <algorithm>
        using namespace std;

        vector<pair<int,int>> maxActivities(vector<pair<int,int>> acts) {
            sort(acts.begin(), acts.end(),
                 [](const pair<int,int>& a, const pair<int,int>& b) { return a.second < b.second; });  // earliest finish first
            vector<pair<int,int>> chosen = {acts[0]};
            for (size_t i = 1; i < acts.size(); i++)
                if (acts[i].first >= chosen.back().second)         // no overlap with the last chosen one
                    chosen.push_back(acts[i]);
            return chosen;
        }

        int main() {
            vector<pair<int,int>> acts = {{2, 3}, {1, 4}, {5, 8}, {6, 10}};
            vector<pair<int,int>> chosen = maxActivities(acts);
            cout << "selected:";
            for (auto& [s, f] : chosen) cout << " (" << s << "," << f << ")";
            cout << "\\ncount: " << chosen.size() << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.Arrays;
        import java.util.List;

        public class Main {
            static List<int[]> maxActivities(int[][] acts) {
                Arrays.sort(acts, (a, b) -> a[1] - b[1]);             // earliest finish first
                List<int[]> chosen = new ArrayList<>();
                chosen.add(acts[0]);
                for (int i = 1; i < acts.length; i++)
                    if (acts[i][0] >= chosen.get(chosen.size() - 1)[1])   // no overlap with the last chosen one
                        chosen.add(acts[i]);
                return chosen;
            }

            public static void main(String[] args) {
                int[][] acts = {{2, 3}, {1, 4}, {5, 8}, {6, 10}};
                List<int[]> chosen = maxActivities(acts);
                StringBuilder sb = new StringBuilder("selected:");
                for (int[] a : chosen) sb.append(" (").append(a[0]).append(",").append(a[1]).append(")");
                System.out.println(sb);
                System.out.println("count: " + chosen.size());
            }
        }
    ''', js='''
        function maxActivities(activities) {
            const acts = [...activities].sort((a, b) => a[1] - b[1]);   // earliest finish first
            const chosen = [acts[0]];
            for (let i = 1; i < acts.length; i++)
                if (acts[i][0] >= chosen[chosen.length - 1][1])          // no overlap with the last chosen one
                    chosen.push(acts[i]);
            return chosen;
        }

        const acts = [[2, 3], [1, 4], [5, 8], [6, 10]];
        const chosen = maxActivities(acts);
        console.log("selected:", chosen.map(([s, f]) => `(${s},${f})`).join(" "));
        console.log("count:", chosen.length);
    ''')
    yield complexity("O(n log n) for the sort; O(n) if already sorted", "O(1) extra")
    yield note("**Why earliest finish is safe (exchange argument).** Let `S` be any optimal set of activities and let `g` be the activity that finishes first overall. Replace the first activity of `S` with `g`: `g` finishes no later, so it cannot overlap the second activity of `S`. The new set is still valid and has the same size — so an optimal solution containing the greedy choice always exists.")
    yield pitfall("Use `start >= last_finish`, not `>`. An activity may begin at the very instant the previous one ends; writing `>` throws away valid pairs like `(1, 3)` and `(3, 5)`.")

    yield section("Fractional knapsack problem", "briefcase")
    yield p("A knapsack can carry at most `W` units of weight. Each item has a weight and a value, and — unlike the 0/1 knapsack — you may take **any fraction** of an item. Maximise the total value carried.")
    yield io("weights = [50, 20, 30], values = [600, 500, 400], W = 70", "1140.00")
    yield idea("Value per unit weight is what matters. Sort the items by `value / weight` descending, take whole items while they fit, then fill the remaining capacity with a fraction of the next item and stop — the knapsack is full.")
    yield table(
        ["Item (w, v)", "Ratio v/w", "Decision", "Value added", "Capacity left"],
        ["(20, 500)", "25.0", "take all", "500", "50"],
        ["(30, 400)", "13.3", "take all", "400", "20"],
        ["(50, 600)", "12.0", "take 20/50", "600 × 20/50 = 240", "0"],
    )
    yield multi('''
        item w=20 v=500: take all → 500.00
        item w=30 v=400: take all → 400.00
        item w=50 v=600: take 20/50 → 240.00
        max value: 1140.00
    ''', py='''
        def fractional_knapsack(items, capacity):
            items = sorted(items, key=lambda it: it[1] / it[0], reverse=True)   # best value per kg first
            total = 0.0
            for w, v in items:
                if capacity == 0:
                    break
                if w <= capacity:                             # the whole item fits
                    capacity -= w
                    total += v
                    print(f"item w={w} v={v}: take all → {v:.2f}")
                else:                                         # only a fraction fits — fill up and stop
                    part = v * capacity / w
                    print(f"item w={w} v={v}: take {capacity}/{w} → {part:.2f}")
                    total += part
                    capacity = 0
            return total

        items = [(50, 600), (20, 500), (30, 400)]             # (weight, value)
        print(f"max value: {fractional_knapsack(items, 70):.2f}")
    ''', cpp='''
        #include <iostream>
        #include <iomanip>
        #include <vector>
        #include <algorithm>
        using namespace std;

        struct Item { int weight, value; };

        double fractionalKnapsack(vector<Item> items, int capacity) {
            sort(items.begin(), items.end(), [](const Item& a, const Item& b) {
                return (double)a.value / a.weight > (double)b.value / b.weight;   // best value per kg first
            });
            double total = 0;
            for (const Item& it : items) {
                if (capacity == 0) break;
                if (it.weight <= capacity) {                   // the whole item fits
                    capacity -= it.weight;
                    total += it.value;
                    cout << "item w=" << it.weight << " v=" << it.value << ": take all → " << (double)it.value << "\\n";
                } else {                                       // only a fraction fits — fill up and stop
                    double part = (double)it.value * capacity / it.weight;
                    cout << "item w=" << it.weight << " v=" << it.value << ": take " << capacity << "/" << it.weight
                         << " → " << part << "\\n";
                    total += part;
                    capacity = 0;
                }
            }
            return total;
        }

        int main() {
            cout << fixed << setprecision(2);
            vector<Item> items = {{50, 600}, {20, 500}, {30, 400}};   // {weight, value}
            double best = fractionalKnapsack(items, 70);               // run first — it prints the steps
            cout << "max value: " << best << "\\n";
        }
    ''', java='''
        import java.util.Arrays;
        import java.util.Locale;

        public class Main {
            static double fractionalKnapsack(int[][] items, int capacity) {
                Arrays.sort(items, (a, b) -> Double.compare((double) b[1] / b[0], (double) a[1] / a[0]));  // best ratio first
                double total = 0;
                for (int[] it : items) {
                    int w = it[0], v = it[1];
                    if (capacity == 0) break;
                    if (w <= capacity) {                           // the whole item fits
                        capacity -= w;
                        total += v;
                        System.out.println("item w=" + w + " v=" + v + ": take all → " + String.format(Locale.US, "%.2f", (double) v));
                    } else {                                       // only a fraction fits — fill up and stop
                        double part = (double) v * capacity / w;
                        System.out.println("item w=" + w + " v=" + v + ": take " + capacity + "/" + w + " → "
                                           + String.format(Locale.US, "%.2f", part));
                        total += part;
                        capacity = 0;
                    }
                }
                return total;
            }

            public static void main(String[] args) {
                int[][] items = {{50, 600}, {20, 500}, {30, 400}};   // {weight, value}
                double best = fractionalKnapsack(items, 70);           // run first — it prints the steps
                System.out.println(String.format(Locale.US, "max value: %.2f", best));
            }
        }
    ''', js='''
        function fractionalKnapsack(items, capacity) {
            const sorted = [...items].sort((a, b) => b[1] / b[0] - a[1] / a[0]);   // best value per kg first
            let total = 0;
            for (const [w, v] of sorted) {
                if (capacity === 0) break;
                if (w <= capacity) {                               // the whole item fits
                    capacity -= w;
                    total += v;
                    console.log(`item w=${w} v=${v}: take all → ${v.toFixed(2)}`);
                } else {                                           // only a fraction fits — fill up and stop
                    const part = v * capacity / w;
                    console.log(`item w=${w} v=${v}: take ${capacity}/${w} → ${part.toFixed(2)}`);
                    total += part;
                    capacity = 0;
                }
            }
            return total;
        }

        const items = [[50, 600], [20, 500], [30, 400]];         // [weight, value]
        console.log(`max value: ${fractionalKnapsack(items, 70).toFixed(2)}`);
    ''')
    yield complexity("O(n log n)", "O(1) extra (O(n) if the input must not be reordered)")
    yield pitfall("The ratio rule is only correct because items are **divisible**. In the 0/1 knapsack (take an item whole or not at all) the same greedy fails: with `W = 50` and items `(10, 60), (20, 100), (30, 120)` the ratio order gives `160`, but `100 + 120 = 220` is optimal. 0/1 knapsack needs dynamic programming.")

    yield section("Job sequencing problem", "clock")
    yield p("Each job has a **deadline** and a **profit**, takes exactly one unit of time, and only one job can run at a time starting from time `0`. A job earns its profit only if it finishes by its deadline. Which jobs should be scheduled, and when, to maximise total profit?")
    yield io("jobs = a(2, 100) b(1, 19) c(2, 27) d(1, 25) e(3, 15)  as (deadline, profit), slots = 3", "142  → slot 1: c, slot 2: a, slot 3: e")
    yield idea("Consider jobs in **decreasing order of profit**. Give each job the **latest free slot** that is still before its deadline — leaving the earlier slots open for jobs with tighter deadlines that come later in the scan.")
    yield steps(
        ("Sort by profit, descending", "a(100), c(27), d(25), b(19), e(15)."),
        ("a (deadline 2)", "Latest free slot ≤ 2 is slot 2 → schedule a there."),
        ("c (deadline 2)", "Slot 2 is taken, slot 1 is free → schedule c in slot 1."),
        ("d (deadline 1), b (deadline 1)", "Slot 1 is taken → both are dropped."),
        ("e (deadline 3)", "Slot 3 is free → schedule e. Total profit 100 + 27 + 15 = 142."),
    )
    yield multi('''
        slot 1: c (profit 27)
        slot 2: a (profit 100)
        slot 3: e (profit 15)
        total profit: 142
    ''', py='''
        def job_sequencing(jobs, slots):
            jobs = sorted(jobs, key=lambda j: j[2], reverse=True)   # most profitable first
            schedule = [None] * slots                               # schedule[s] = job running in slot s+1
            for name, deadline, profit in jobs:
                for s in range(min(slots, deadline) - 1, -1, -1):  # latest free slot before the deadline
                    if schedule[s] is None:
                        schedule[s] = (name, profit)
                        break
            return schedule

        jobs = [("a", 2, 100), ("b", 1, 19), ("c", 2, 27), ("d", 1, 25), ("e", 3, 15)]   # (name, deadline, profit)
        total = 0
        for s, job in enumerate(job_sequencing(jobs, 3)):
            if job is not None:
                print(f"slot {s + 1}: {job[0]} (profit {job[1]})")
                total += job[1]
        print("total profit:", total)
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <string>
        #include <algorithm>
        using namespace std;

        struct Job { string name; int deadline, profit; };

        vector<Job> jobSequencing(vector<Job> jobs, int slots) {
            sort(jobs.begin(), jobs.end(),
                 [](const Job& a, const Job& b) { return a.profit > b.profit; });   // most profitable first
            vector<Job> schedule(slots, Job{"", 0, 0});                // schedule[s] = job running in slot s+1
            for (const Job& j : jobs)
                for (int s = min(slots, j.deadline) - 1; s >= 0; s--)  // latest free slot before the deadline
                    if (schedule[s].name.empty()) { schedule[s] = j; break; }
            return schedule;
        }

        int main() {
            vector<Job> jobs = {{"a", 2, 100}, {"b", 1, 19}, {"c", 2, 27}, {"d", 1, 25}, {"e", 3, 15}};
            vector<Job> schedule = jobSequencing(jobs, 3);
            int total = 0;
            for (int s = 0; s < (int)schedule.size(); s++) {
                if (schedule[s].name.empty()) continue;
                cout << "slot " << s + 1 << ": " << schedule[s].name << " (profit " << schedule[s].profit << ")\\n";
                total += schedule[s].profit;
            }
            cout << "total profit: " << total << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class Job {
                String name; int deadline, profit;
                Job(String n, int d, int p) { name = n; deadline = d; profit = p; }
            }

            static Job[] jobSequencing(List<Job> jobs, int slots) {
                jobs.sort((a, b) -> b.profit - a.profit);               // most profitable first
                Job[] schedule = new Job[slots];                         // schedule[s] = job running in slot s+1
                for (Job j : jobs)
                    for (int s = Math.min(slots, j.deadline) - 1; s >= 0; s--)   // latest free slot before the deadline
                        if (schedule[s] == null) { schedule[s] = j; break; }
                return schedule;
            }

            public static void main(String[] args) {
                List<Job> jobs = new ArrayList<>(List.of(new Job("a", 2, 100), new Job("b", 1, 19),
                        new Job("c", 2, 27), new Job("d", 1, 25), new Job("e", 3, 15)));
                Job[] schedule = jobSequencing(jobs, 3);
                int total = 0;
                for (int s = 0; s < schedule.length; s++) {
                    if (schedule[s] == null) continue;
                    System.out.println("slot " + (s + 1) + ": " + schedule[s].name + " (profit " + schedule[s].profit + ")");
                    total += schedule[s].profit;
                }
                System.out.println("total profit: " + total);
            }
        }
    ''', js='''
        function jobSequencing(jobs, slots) {
            const sorted = [...jobs].sort((a, b) => b.profit - a.profit);   // most profitable first
            const schedule = new Array(slots).fill(null);                   // schedule[s] = job running in slot s+1
            for (const job of sorted)
                for (let s = Math.min(slots, job.deadline) - 1; s >= 0; s--)   // latest free slot before the deadline
                    if (schedule[s] === null) { schedule[s] = job; break; }
            return schedule;
        }

        const jobs = [
            { name: "a", deadline: 2, profit: 100 }, { name: "b", deadline: 1, profit: 19 },
            { name: "c", deadline: 2, profit: 27 },  { name: "d", deadline: 1, profit: 25 },
            { name: "e", deadline: 3, profit: 15 },
        ];
        let total = 0;
        jobSequencing(jobs, 3).forEach((job, s) => {
            if (job === null) return;
            console.log(`slot ${s + 1}: ${job.name} (profit ${job.profit})`);
            total += job.profit;
        });
        console.log("total profit:", total);
    ''')
    yield complexity("O(n log n + n · slots) — O(n log n) with a disjoint-set to find the latest free slot", "O(slots)")
    yield pitfall("Placing a job in the **earliest** free slot instead of the latest one is the common mistake: `a` would take slot 1, and then `c` (deadline 2) still fits in slot 2 here, but in general early slots are the scarce resource that tight-deadline jobs need. Scanning backwards from `min(slots, deadline)` keeps them free.")

    yield section("Huffman coding", "file-zip")
    yield p("Huffman coding is a **lossless compression** scheme that gives each character a **variable-length** binary code: frequent characters get short codes, rare ones get long codes. Over the text `\"aabbacbababbabbabaab…\"` of 100 characters with frequencies `a: 70, b: 20, c: 10`, a fixed-length code spends 2 bits per character (200 bits); Huffman spends 130.")
    yield io("frequencies = a: 70, b: 20, c: 10", "a → 1, b → 01, c → 00  (130 bits total)")
    yield cards(
        ("Greedy idea", "The most frequent character must have the shortest code — so build the tree from the rarest characters upward, merging the two least frequent nodes at every step.", "bulb"),
        ("Prefix requirement", "For decompression to be unambiguous, no code may be a **prefix** of another. With `a = 1, b = 01, c = 00` the stream `1 00 1 01` can only mean `acab`. Leaves of a binary tree automatically satisfy this.", "binary"),
    )
    yield p("**High-level idea.** Build a binary tree in which every input character is a **leaf** and internal nodes carry a dummy character (`$`). Label every left edge `0` and every right edge `1`; the root-to-leaf path spells out the leaf's code. Then traverse the tree and print the codes.")
    yield diagram('''
        step 1  heap: c:10  b:20  a:70        pop c, b → new node $:30
        step 2  heap: $:30  a:70              pop $, a → new node $:100
        step 3  heap: $:100                   one node left — the root

                   ($:100)
                  0/     \\1
              ($:30)      a:70   → a = 1
             0/    \\1
           c:10    b:20          → c = 00, b = 01
    ''', "Building the Huffman tree with a min-heap; left edge = 0, right edge = 1")
    yield steps(
        ("Create the leaves", "One node per character with its frequency; push all of them into a **min-heap** keyed on frequency."),
        ("Merge while the heap has more than one node", "`left = extractMin()`, `right = extractMin()`; create a node with character `$`, frequency `left.freq + right.freq`, and the two popped nodes as children; push it back."),
        ("The last node is the root", "Its frequency is the total character count."),
        ("Print the codes", "`printCodes(root, \"\")`: at a leaf print the character and the accumulated string; otherwise recurse left with `code + \"0\"` and right with `code + \"1\"`."),
    )
    yield note("Two nodes may have the **same frequency**, and then the shape of the tree depends on which one the heap returns first. The code lengths — and the total compressed size — are identical either way, but the actual bit strings differ. The programs below break ties by *insertion order* so that all four print the same codes.", "Ties")
    yield multi('''
        c: 00
        b: 01
        a: 1
        total bits: 130 (fixed-length 2-bit codes: 200)
    ''', py='''
        import heapq

        class Node:
            def __init__(self, ch, freq, left=None, right=None):
                self.ch, self.freq, self.left, self.right = ch, freq, left, right

        def build_huffman_tree(freq):
            heap, order = [], 0
            for ch, f in freq:                                      # (freq, insertion order, node) — order breaks ties
                heap.append((f, order, Node(ch, f)))
                order += 1
            heapq.heapify(heap)
            while len(heap) > 1:
                f1, _, left = heapq.heappop(heap)                   # the two least frequent nodes …
                f2, _, right = heapq.heappop(heap)
                heapq.heappush(heap, (f1 + f2, order, Node('$', f1 + f2, left, right)))   # … become siblings
                order += 1
            return heap[0][2]

        def print_codes(node, code, codes):
            if node.ch != '$':                                      # leaf = an input character
                print(f"{node.ch}: {code}")
                codes[node.ch] = code
                return
            print_codes(node.left, code + "0", codes)
            print_codes(node.right, code + "1", codes)

        freq = [('a', 70), ('b', 20), ('c', 10)]
        root = build_huffman_tree(freq)
        codes = {}
        print_codes(root, "", codes)
        total = sum(f * len(codes[ch]) for ch, f in freq)
        chars = sum(f for _, f in freq)
        print(f"total bits: {total} (fixed-length 2-bit codes: {2 * chars})")
    ''', cpp='''
        #include <iostream>
        #include <queue>
        #include <string>
        #include <vector>
        #include <map>
        using namespace std;

        struct Node {
            char ch; int freq; Node *left, *right;
            Node(char c, int f, Node* l = nullptr, Node* r = nullptr) : ch(c), freq(f), left(l), right(r) {}
        };
        struct Entry { int freq, order; Node* node; };
        struct ByFreq {                                             // min-heap on (freq, insertion order)
            bool operator()(const Entry& a, const Entry& b) const {
                return a.freq != b.freq ? a.freq > b.freq : a.order > b.order;
            }
        };

        Node* buildHuffmanTree(const vector<pair<char,int>>& freq) {
            priority_queue<Entry, vector<Entry>, ByFreq> heap;
            int order = 0;
            for (auto& [ch, f] : freq) heap.push({f, order++, new Node(ch, f)});
            while (heap.size() > 1) {
                Entry l = heap.top(); heap.pop();                   // the two least frequent nodes …
                Entry r = heap.top(); heap.pop();
                heap.push({l.freq + r.freq, order++, new Node('$', l.freq + r.freq, l.node, r.node)});  // … become siblings
            }
            return heap.top().node;
        }

        void printCodes(Node* n, const string& code, map<char,string>& codes) {
            if (n->ch != '$') {                                     // leaf = an input character
                cout << n->ch << ": " << code << "\\n";
                codes[n->ch] = code;
                return;
            }
            printCodes(n->left, code + "0", codes);
            printCodes(n->right, code + "1", codes);
        }

        int main() {
            vector<pair<char,int>> freq = {{'a', 70}, {'b', 20}, {'c', 10}};
            Node* root = buildHuffmanTree(freq);
            map<char,string> codes;
            printCodes(root, "", codes);
            int total = 0, chars = 0;
            for (auto& [ch, f] : freq) { total += f * (int)codes[ch].size(); chars += f; }
            cout << "total bits: " << total << " (fixed-length 2-bit codes: " << 2 * chars << ")\\n";
        }
    ''', java='''
        import java.util.HashMap;
        import java.util.Map;
        import java.util.PriorityQueue;

        public class Main {
            static class Node {
                char ch; int freq, order; Node left, right;
                Node(char c, int f, int o, Node l, Node r) { ch = c; freq = f; order = o; left = l; right = r; }
            }

            static Node buildHuffmanTree(char[] chars, int[] freqs) {
                PriorityQueue<Node> heap = new PriorityQueue<>((a, b) ->
                        a.freq != b.freq ? a.freq - b.freq : a.order - b.order);   // min-heap on (freq, insertion order)
                int order = 0;
                for (int i = 0; i < chars.length; i++) heap.add(new Node(chars[i], freqs[i], order++, null, null));
                while (heap.size() > 1) {
                    Node left = heap.poll();                                     // the two least frequent nodes …
                    Node right = heap.poll();
                    heap.add(new Node('$', left.freq + right.freq, order++, left, right));   // … become siblings
                }
                return heap.poll();
            }

            static void printCodes(Node n, String code, Map<Character, String> codes) {
                if (n.ch != '$') {                                               // leaf = an input character
                    System.out.println(n.ch + ": " + code);
                    codes.put(n.ch, code);
                    return;
                }
                printCodes(n.left, code + "0", codes);
                printCodes(n.right, code + "1", codes);
            }

            public static void main(String[] args) {
                char[] chars = {'a', 'b', 'c'};
                int[] freqs = {70, 20, 10};
                Node root = buildHuffmanTree(chars, freqs);
                Map<Character, String> codes = new HashMap<>();
                printCodes(root, "", codes);
                int total = 0, count = 0;
                for (int i = 0; i < chars.length; i++) { total += freqs[i] * codes.get(chars[i]).length(); count += freqs[i]; }
                System.out.println("total bits: " + total + " (fixed-length 2-bit codes: " + 2 * count + ")");
            }
        }
    ''', js='''
        class Node {
            constructor(ch, freq, order, left = null, right = null) {
                Object.assign(this, { ch, freq, order, left, right });
            }
        }

        class MinHeap {                               // keyed on (freq, insertion order) so ties are deterministic
            constructor() { this.a = []; }
            less(i, j) { const x = this.a[i], y = this.a[j]; return x.freq !== y.freq ? x.freq < y.freq : x.order < y.order; }
            swap(i, j) { [this.a[i], this.a[j]] = [this.a[j], this.a[i]]; }
            push(node) {
                this.a.push(node);
                for (let i = this.a.length - 1; i > 0 && this.less(i, (i - 1) >> 1); i = (i - 1) >> 1) this.swap(i, (i - 1) >> 1);
            }
            pop() {
                const top = this.a[0], last = this.a.pop();
                if (this.a.length) {
                    this.a[0] = last;
                    for (let i = 0;;) {
                        let m = i; const l = 2 * i + 1, r = l + 1;
                        if (l < this.a.length && this.less(l, m)) m = l;
                        if (r < this.a.length && this.less(r, m)) m = r;
                        if (m === i) break;
                        this.swap(i, m); i = m;
                    }
                }
                return top;
            }
            get size() { return this.a.length; }
        }

        function buildHuffmanTree(freq) {
            const heap = new MinHeap();
            let order = 0;
            for (const [ch, f] of freq) heap.push(new Node(ch, f, order++));
            while (heap.size > 1) {
                const left = heap.pop();                                  // the two least frequent nodes …
                const right = heap.pop();
                heap.push(new Node('$', left.freq + right.freq, order++, left, right));   // … become siblings
            }
            return heap.pop();
        }

        function printCodes(n, code, codes) {
            if (n.ch !== '$') { console.log(`${n.ch}: ${code}`); codes[n.ch] = code; return; }   // leaf
            printCodes(n.left, code + "0", codes);
            printCodes(n.right, code + "1", codes);
        }

        const freq = [['a', 70], ['b', 20], ['c', 10]];
        const codes = {};
        printCodes(buildHuffmanTree(freq), "", codes);
        const total = freq.reduce((s, [ch, f]) => s + f * codes[ch].length, 0);
        const chars = freq.reduce((s, [, f]) => s + f, 0);
        console.log(`total bits: ${total} (fixed-length 2-bit codes: ${2 * chars})`);
    ''')
    yield complexity("O(k log k) for k distinct characters (k − 1 merges, each O(log k) on the heap)", "O(k) for the tree")
    yield pitfall("A text with a **single distinct character** produces a tree that is just one leaf and an empty code `\"\"`. Real encoders special-case this (give it the code `0`). Also remember that the frequency table must be stored alongside the compressed data, or the decoder cannot rebuild the same tree.")

    yield section("Interview Q&A", "message-question")
    yield qa("Greedy vs dynamic programming — how do you decide?",
             "Both need optimal substructure. Greedy additionally needs the **greedy-choice property**: a locally best choice that is provably part of an optimal solution, so you never have to look at alternatives. DP is for problems where the best choice at a step depends on the solutions of sub-problems, so you must evaluate all options and keep the best (0/1 knapsack, general coin change, LCS). Greedy is faster — usually `O(n log n)` — but only when it is correct.")
    yield qa("Why does greedy work for Indian/US coins but not for arbitrary denominations?",
             "In canonical coin systems every coin is worth at least as much as any combination of smaller coins that it could replace, so taking the largest coin never costs an extra coin later. Arbitrary systems like `{18, 10, 1}` break that: `20 = 10 + 10` beats `18 + 1 + 1`. Minimum coins for arbitrary denominations is a DP problem.")
    yield qa("Sketch the exchange argument for activity selection.",
             "Let `g` be the activity with the earliest finish and `S` an optimal solution whose first activity (by finish) is `x ≠ g`. Since `g` finishes no later than `x`, `S − {x} + {g}` has no overlaps and the same size — so there is an optimal solution containing `g`. Remove `g` and all activities overlapping it; the remainder is the same problem on fewer activities, so induction finishes the proof.")
    yield qa("Why are Huffman codes prefix-free, and why does that matter?",
             "Every character sits at a **leaf** of the tree, and a leaf's path can never be the prefix of another leaf's path (that other leaf would have to be inside its subtree). Prefix-freeness means the decoder can read bits one at a time and stop the moment it reaches a leaf — no separators between codes are needed.")
    yield qa("Is Huffman coding optimal?",
             "Yes — among all prefix codes for a given set of **per-symbol** frequencies it minimises the expected code length (proved by an exchange argument: in an optimal tree the two rarest symbols are sibling leaves at maximum depth). It is not optimal when symbols are correlated or when fractional bits per symbol would help — arithmetic coding and context modelling do better there.")
    yield qa("Name a problem where the obvious greedy rule is wrong and give the counterexample.",
             "0/1 knapsack by value-per-weight: `W = 50`, items `(10, 60), (20, 100), (30, 120)`. Ratios pick items 1 and 2 for value `160`, but items 2 and 3 give `220`. Another: activity selection by *shortest duration* — a short activity in the middle can block two longer ones on either side.")


@topic(G, "backtracking", "Backtracking", "arrows-shuffle")
def _():
    yield lead("Backtracking explores a space of candidate solutions by building them step by step and **abandoning a partial solution the moment it can no longer lead to a valid answer** — pruning whole branches of the recursion tree instead of generating every combination.")
    yield define("Backtracking", "a refinement of brute-force recursion: at each step *choose* one option, *explore* what follows, and if it fails *un-choose* it and try the next option. The key ingredient is a feasibility check that rejects a partial solution early.")
    yield diagram('''
                            ( )                         choose a value for position 0
                   ┌─────────┼─────────┐
                  (A)       (B)       (C)
               ┌───┴───┐  ┌──┴──┐   ┌──┴──┐
             (AB)   (AC) (BA) (BC) (CA) (CB)         choose a value for position 1
               ✘      │    │    │    ✘    │           ✘ = "AB" appeared → prune this branch
                    (ACB)(BAC)(BCA)     (CBA)         every surviving leaf is a solution
    ''', "Recursion tree for permutations of ABC without the substring \"AB\" — two branches are cut before they are expanded")

    yield section("The template: choose, explore, un-choose", "repeat")
    yield p("Every backtracking solution is the same recursive function. Only the three parts in the comments change from problem to problem.")
    yield diagram('''
        solve(state):
            if state is a complete solution:       # base case
                record / print it
                return

            for each option in candidates(state):  # the branching
                if not feasible(option, state):    # ← pruning: skip dead branches early
                    continue
                apply(option, state)               # choose
                solve(state)                       # explore
                undo(option, state)                # un-choose (restore the state exactly)
    ''', "The backtracking template — undo must perfectly reverse apply")
    yield steps(
        ("Choose", "Place a queen, step onto a cell, write a digit — mutate the shared state."),
        ("Explore", "Recurse to fill the next position. If it returns success and you only want one solution, return immediately."),
        ("Un-choose", "Undo the mutation so the loop can try the next option on a clean state. Forgetting this step is the #1 bug."),
    )
    yield table(
        ["Technique", "Explores", "Prunes?", "Reuses sub-results?", "Typical problems"],
        ["Plain recursion / brute force", "every candidate", "no", "no", "generate all subsets or permutations"],
        ["**Backtracking**", "candidates in a DFS order", "**yes** — as soon as a partial solution is infeasible", "no", "N-Queens, Sudoku, maze paths, constraint satisfaction"],
        ["Dynamic programming", "overlapping sub-problems", "no", "**yes** — memoised", "optimisation with optimal substructure"],
        ["Branch and bound", "candidates in a best-first order", "yes — by a cost bound", "no", "optimisation (TSP, 0/1 knapsack exact)"],
    )
    yield note("Backtracking does not change the **worst-case** complexity — N-Queens is still exponential — but the pruning makes the *typical* running time dramatically smaller than brute force. Whenever a yes/no feasibility test can be applied to a *partial* solution, backtracking applies.")

    yield section("Permutations without \"AB\" as a substring", "arrows-shuffle")
    yield p("Given a string, print all permutations that do **not** contain `\"AB\"` as a substring. The brute-force version generates all `n!` permutations and filters them at the leaves; backtracking checks the constraint *while* the permutation is being built and never expands a prefix that already contains `\"AB\"`.")
    yield io("str = \"ABC\"", "ACB BAC BCA CBA")
    yield idea("Fix the characters position by position by **swapping** `chars[i]` into position `l` (choose), recursing on `l + 1` (explore), and swapping back (un-choose). Right after a swap, if `chars[l-1] == 'A'` and `chars[l] == 'B'` the prefix is already invalid — skip the recursion for that choice.")
    yield multi('''
        ACB BAC BCA CBA
        count: 4
    ''', py='''
        def permute(chars, l, found):
            n = len(chars)
            if l == n:                                           # every position fixed — a complete permutation
                found.append("".join(chars))
                return
            for i in range(l, n):
                chars[l], chars[i] = chars[i], chars[l]          # choose: put chars[i] at position l
                if not (l > 0 and chars[l - 1] == 'A' and chars[l] == 'B'):   # prune: "AB" just appeared
                    permute(chars, l + 1, found)                 # explore
                chars[l], chars[i] = chars[i], chars[l]          # un-choose

        found = []
        permute(list("ABC"), 0, found)
        print(" ".join(found))
        print("count:", len(found))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        void permute(string& s, int l, vector<string>& found) {
            int n = s.size();
            if (l == n) { found.push_back(s); return; }          // every position fixed — a complete permutation
            for (int i = l; i < n; i++) {
                swap(s[l], s[i]);                                  // choose: put s[i] at position l
                if (!(l > 0 && s[l - 1] == 'A' && s[l] == 'B'))    // prune: "AB" just appeared
                    permute(s, l + 1, found);                      // explore
                swap(s[l], s[i]);                                  // un-choose
            }
        }

        int main() {
            string s = "ABC";
            vector<string> found;
            permute(s, 0, found);
            for (size_t i = 0; i < found.size(); i++) cout << (i ? " " : "") << found[i];
            cout << "\\ncount: " << found.size() << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static void permute(char[] s, int l, List<String> found) {
                if (l == s.length) { found.add(new String(s)); return; }   // every position fixed
                for (int i = l; i < s.length; i++) {
                    char t = s[l]; s[l] = s[i]; s[i] = t;                 // choose: put s[i] at position l
                    if (!(l > 0 && s[l - 1] == 'A' && s[l] == 'B'))        // prune: "AB" just appeared
                        permute(s, l + 1, found);                          // explore
                    t = s[l]; s[l] = s[i]; s[i] = t;                      // un-choose
                }
            }

            public static void main(String[] args) {
                List<String> found = new ArrayList<>();
                permute("ABC".toCharArray(), 0, found);
                System.out.println(String.join(" ", found));
                System.out.println("count: " + found.size());
            }
        }
    ''', js='''
        function permute(chars, l, found) {
            if (l === chars.length) { found.push(chars.join("")); return; }   // every position fixed
            for (let i = l; i < chars.length; i++) {
                [chars[l], chars[i]] = [chars[i], chars[l]];                  // choose: put chars[i] at position l
                if (!(l > 0 && chars[l - 1] === 'A' && chars[l] === 'B'))     // prune: "AB" just appeared
                    permute(chars, l + 1, found);                             // explore
                [chars[l], chars[i]] = [chars[i], chars[l]];                  // un-choose
            }
        }

        const found = [];
        permute([..."ABC"], 0, found);
        console.log(found.join(" "));
        console.log("count:", found.length);
    ''')
    yield complexity("O(n · n!) worst case — far fewer nodes are visited thanks to pruning", "O(n) recursion depth")
    yield pitfall("Checking the constraint only at the leaves (`if \"AB\" not in result`) is still correct but it is **not backtracking** — it is brute force with a filter, and it visits all `n!` leaves. The pruning line is what turns the recursion tree into something smaller.")

    yield section("Rat in a maze", "route")
    yield p("A rat starts in the top-left cell `(0, 0)` of an `N × N` maze and must reach the bottom-right cell `(N-1, N-1)`. A `1` is an open cell, a `0` is a wall. Only two moves are allowed: **down** and **right**. Print the path as a matrix of `1`s, or report that no path exists.")
    yield io("maze = [[1,0,0,0], [1,1,0,1], [0,1,0,0], [0,1,1,1]]", "1 0 0 0 / 1 1 0 0 / 0 1 0 0 / 0 1 1 1  (path marked with 1s)")
    yield diagram('''
        maze              path found
        1 0 0 0           1 0 0 0        (0,0) ↓ (1,0) → (1,1) ↓ (2,1) ↓ (3,1) → (3,2) → (3,3)
        1 1 0 1           1 1 0 0
        0 1 0 0           0 1 0 0        the 1 at (1,3) is open but unreachable with down/right moves
        0 1 1 1           0 1 1 1
    ''', "The rat may only move down or right; dead ends are un-marked when the recursion backs out")
    yield idea("Mark the current cell as part of the path (choose), try to reach the goal via the cell below, then via the cell to the right (explore). If neither works, this cell is a dead end — clear the mark (un-choose) and return `false` so the caller tries its other move.")
    yield steps(
        ("Reject", "Outside the grid, or the cell is a wall → return `false`."),
        ("Mark", "`path[r][c] = 1`. If this is the destination → return `true`."),
        ("Try down, then right", "If either recursive call succeeds, keep the mark and return `true`."),
        ("Backtrack", "Neither move led anywhere: `path[r][c] = 0`, return `false`."),
    )
    yield multi('''
        path:
        1 0 0 0
        1 1 0 0
        0 1 0 0
        0 1 1 1
    ''', py='''
        def solve_maze(maze):
            n = len(maze)
            path = [[0] * n for _ in range(n)]

            def solve(r, c):
                if r >= n or c >= n or maze[r][c] == 0:      # off the grid or a wall
                    return False
                path[r][c] = 1                               # choose: step on this cell
                if r == n - 1 and c == n - 1:                # reached the destination
                    return True
                if solve(r + 1, c) or solve(r, c + 1):       # explore: down first, then right
                    return True
                path[r][c] = 0                               # un-choose: dead end
                return False

            return path if solve(0, 0) else None

        maze = [[1, 0, 0, 0],
                [1, 1, 0, 1],
                [0, 1, 0, 0],
                [0, 1, 1, 1]]
        path = solve_maze(maze)
        if path is None:
            print("No path exists")
        else:
            print("path:")
            for row in path:
                print(" ".join(map(str, row)))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool solve(const vector<vector<int>>& maze, int r, int c, vector<vector<int>>& path) {
            int n = maze.size();
            if (r >= n || c >= n || maze[r][c] == 0) return false;   // off the grid or a wall
            path[r][c] = 1;                                           // choose: step on this cell
            if (r == n - 1 && c == n - 1) return true;                // reached the destination
            if (solve(maze, r + 1, c, path) || solve(maze, r, c + 1, path)) return true;   // explore: down, then right
            path[r][c] = 0;                                           // un-choose: dead end
            return false;
        }

        int main() {
            vector<vector<int>> maze = {{1, 0, 0, 0},
                                        {1, 1, 0, 1},
                                        {0, 1, 0, 0},
                                        {0, 1, 1, 1}};
            int n = maze.size();
            vector<vector<int>> path(n, vector<int>(n, 0));
            if (!solve(maze, 0, 0, path)) { cout << "No path exists\\n"; return 0; }
            cout << "path:\\n";
            for (auto& row : path) {
                for (int j = 0; j < n; j++) cout << (j ? " " : "") << row[j];
                cout << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static boolean solve(int[][] maze, int r, int c, int[][] path) {
                int n = maze.length;
                if (r >= n || c >= n || maze[r][c] == 0) return false;   // off the grid or a wall
                path[r][c] = 1;                                           // choose: step on this cell
                if (r == n - 1 && c == n - 1) return true;                // reached the destination
                if (solve(maze, r + 1, c, path) || solve(maze, r, c + 1, path)) return true;   // explore: down, then right
                path[r][c] = 0;                                           // un-choose: dead end
                return false;
            }

            public static void main(String[] args) {
                int[][] maze = {{1, 0, 0, 0},
                                {1, 1, 0, 1},
                                {0, 1, 0, 0},
                                {0, 1, 1, 1}};
                int n = maze.length;
                int[][] path = new int[n][n];
                if (!solve(maze, 0, 0, path)) { System.out.println("No path exists"); return; }
                System.out.println("path:");
                for (int[] row : path) {
                    StringBuilder sb = new StringBuilder();
                    for (int j = 0; j < n; j++) sb.append(j > 0 ? " " : "").append(row[j]);
                    System.out.println(sb);
                }
            }
        }
    ''', js='''
        function solveMaze(maze) {
            const n = maze.length;
            const path = Array.from({ length: n }, () => Array(n).fill(0));

            function solve(r, c) {
                if (r >= n || c >= n || maze[r][c] === 0) return false;   // off the grid or a wall
                path[r][c] = 1;                                           // choose: step on this cell
                if (r === n - 1 && c === n - 1) return true;              // reached the destination
                if (solve(r + 1, c) || solve(r, c + 1)) return true;      // explore: down first, then right
                path[r][c] = 0;                                           // un-choose: dead end
                return false;
            }

            return solve(0, 0) ? path : null;
        }

        const maze = [[1, 0, 0, 0],
                      [1, 1, 0, 1],
                      [0, 1, 0, 0],
                      [0, 1, 1, 1]];
        const path = solveMaze(maze);
        if (path === null) {
            console.log("No path exists");
        } else {
            console.log("path:");
            for (const row of path) console.log(row.join(" "));
        }
    ''')
    yield complexity("O(2^(N²)) worst case — each cell branches two ways", "O(N²) for the path matrix, O(N) recursion depth")
    yield note("If all four moves (up, down, left, right) are allowed, the same code loops forever bouncing between two cells. Add the condition `path[r][c] == 1 → return false` (already visited) so a cell is never entered twice on the same path.", "Four-direction variant")

    yield section("N-Queens problem", "chess")
    yield p("Place `N` queens on an `N × N` chessboard so that **no two queens attack each other** — no two share a row, a column or a diagonal. For `N = 4` there are exactly two solutions (mirror images of each other).")
    yield io("N = 4", ". Q . . / . . . Q / Q . . . / . . Q .  — 2 solutions in total")
    yield table(
        ["Approach", "Idea", "Configurations examined"],
        ["Super naive", "Choose any `N` of the `N²` cells, check each configuration", "`C(N², N)` — 1820 for N = 4, ~4.4 × 10⁹ for N = 8"],
        ["Naive", "One queen per row: try every permutation of column numbers, check diagonals", "`N!` — 24 for N = 4, 40 320 for N = 8"],
        ["**Backtracking**", "Place row by row; before placing in `(r, c)` check it against the queens already placed and **cut the branch** on the first conflict", "far fewer — 15 placements tried for N = 4, ~2 000 for N = 8"],
    )
    yield idea("Since every row holds exactly one queen, the state is just `cols[r]` = the column of the queen in row `r`. A new queen at `(r, c)` is safe iff for every earlier row `pr`: `cols[pr] != c` (column) and `|cols[pr] − c| != r − pr` (both diagonals). Place, recurse to the next row, un-place.")
    yield diagram('''
        row 0:  . Q . .        cols = [1, 3, 0, 2]
        row 1:  . . . Q        row 0 tried col 0 first: rows 1–2 could be filled (0,2,?) but row 3 had no safe
        row 2:  Q . . .        column → backtracked all the way to row 0 and moved the first queen to col 1
        row 3:  . . Q .
    ''', "The first solution found for N = 4")
    yield multi('''
        . Q . .
        . . . Q
        Q . . .
        . . Q .
        solutions: 2
    ''', py='''
        def solve_n_queens(n):
            cols = [-1] * n                     # cols[r] = column of the queen in row r
            solutions = []

            def safe(r, c):
                for pr in range(r):             # compare with every queen already placed
                    pc = cols[pr]
                    if pc == c or abs(pc - c) == r - pr:      # same column or same diagonal
                        return False
                return True

            def place(r):
                if r == n:                      # all rows filled — a solution
                    solutions.append(cols[:])
                    return
                for c in range(n):
                    if safe(r, c):              # prune: skip attacked squares
                        cols[r] = c             # choose
                        place(r + 1)            # explore
                        cols[r] = -1            # un-choose

            place(0)
            return solutions

        n = 4
        sols = solve_n_queens(n)
        for c in sols[0]:
            print(" ".join("Q" if j == c else "." for j in range(n)))
        print("solutions:", len(sols))
    ''', cpp='''
        #include <iostream>
        #include <vector>
        #include <cstdlib>
        using namespace std;

        bool safe(const vector<int>& cols, int r, int c) {
            for (int pr = 0; pr < r; pr++) {                     // compare with every queen already placed
                int pc = cols[pr];
                if (pc == c || abs(pc - c) == r - pr) return false;   // same column or same diagonal
            }
            return true;
        }

        void place(int r, int n, vector<int>& cols, vector<vector<int>>& solutions) {
            if (r == n) { solutions.push_back(cols); return; }   // all rows filled — a solution
            for (int c = 0; c < n; c++) {
                if (!safe(cols, r, c)) continue;                 // prune: skip attacked squares
                cols[r] = c;                                     // choose
                place(r + 1, n, cols, solutions);                // explore
                cols[r] = -1;                                    // un-choose
            }
        }

        int main() {
            int n = 4;
            vector<int> cols(n, -1);                             // cols[r] = column of the queen in row r
            vector<vector<int>> solutions;
            place(0, n, cols, solutions);
            for (int c : solutions[0]) {
                for (int j = 0; j < n; j++) cout << (j ? " " : "") << (j == c ? "Q" : ".");
                cout << "\\n";
            }
            cout << "solutions: " << solutions.size() << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static boolean safe(int[] cols, int r, int c) {
                for (int pr = 0; pr < r; pr++) {                     // compare with every queen already placed
                    int pc = cols[pr];
                    if (pc == c || Math.abs(pc - c) == r - pr) return false;   // same column or same diagonal
                }
                return true;
            }

            static void place(int r, int n, int[] cols, List<int[]> solutions) {
                if (r == n) { solutions.add(cols.clone()); return; }   // all rows filled — a solution
                for (int c = 0; c < n; c++) {
                    if (!safe(cols, r, c)) continue;                 // prune: skip attacked squares
                    cols[r] = c;                                     // choose
                    place(r + 1, n, cols, solutions);                // explore
                    cols[r] = -1;                                    // un-choose
                }
            }

            public static void main(String[] args) {
                int n = 4;
                int[] cols = new int[n];                             // cols[r] = column of the queen in row r
                java.util.Arrays.fill(cols, -1);
                List<int[]> solutions = new ArrayList<>();
                place(0, n, cols, solutions);
                for (int c : solutions.get(0)) {
                    StringBuilder sb = new StringBuilder();
                    for (int j = 0; j < n; j++) sb.append(j > 0 ? " " : "").append(j == c ? "Q" : ".");
                    System.out.println(sb);
                }
                System.out.println("solutions: " + solutions.size());
            }
        }
    ''', js='''
        function solveNQueens(n) {
            const cols = Array(n).fill(-1);          // cols[r] = column of the queen in row r
            const solutions = [];

            function safe(r, c) {
                for (let pr = 0; pr < r; pr++) {     // compare with every queen already placed
                    const pc = cols[pr];
                    if (pc === c || Math.abs(pc - c) === r - pr) return false;   // same column or same diagonal
                }
                return true;
            }

            function place(r) {
                if (r === n) { solutions.push([...cols]); return; }   // all rows filled — a solution
                for (let c = 0; c < n; c++) {
                    if (!safe(r, c)) continue;       // prune: skip attacked squares
                    cols[r] = c;                     // choose
                    place(r + 1);                    // explore
                    cols[r] = -1;                    // un-choose
                }
            }

            place(0);
            return solutions;
        }

        const n = 4;
        const sols = solveNQueens(n);
        for (const c of sols[0])
            console.log(Array.from({ length: n }, (_, j) => (j === c ? "Q" : ".")).join(" "));
        console.log("solutions:", sols.length);
    ''')
    yield complexity("O(N!) worst case (with pruning far fewer nodes are visited); O(N) per safety check", "O(N) for `cols` and the recursion")
    yield note("`safe()` can be made `O(1)` with three boolean arrays: `usedCol[c]`, `diag1[r + c]` and `diag2[r − c + N − 1]`. Set them when placing and clear them when un-placing — the same choose/un-choose discipline.", "Optimisation")
    yield pitfall("Checking only columns and the *main* diagonal is the classic omission — both `r − c` (↘) and `r + c` (↙) must be unique. The test `|pc − c| == r − pr` covers both at once.")

    yield section("Sudoku solver", "grid-dots")
    yield p("Fill the empty cells (`0`) of a `9 × 9` grid with digits `1–9` so that every **row**, every **column** and every **3 × 3 sub-grid** contains each digit exactly once.")
    yield io("the standard puzzle below (51 empty cells)", "the completed grid, printed one row per line")
    yield ul(
        "**Distinct rows** — a digit appears at most once in `board[row][*]`.",
        "**Distinct columns** — a digit appears at most once in `board[*][col]`.",
        "**Distinct sub-grids** — the 3 × 3 box starting at `(row − row % 3, col − col % 3)` has no repeats.",
    )
    yield idea("Find the next empty cell. Try digits `1..9`; for each digit that passes the three checks, write it (choose) and recurse (explore). If the recursion fails, erase the digit (un-choose) and try the next. If no digit works, return `false` so the previous cell changes its digit. No empty cell left means the board is solved.")
    yield steps(
        ("Find an empty cell", "Scan row-major for the first `0`. None left → solved, return `true`."),
        ("Try each digit 1–9", "`isSafe(row, col, d)` checks the row, the column and the 3 × 3 box."),
        ("Choose & explore", "`board[row][col] = d`; if `solve()` returns `true`, propagate the success."),
        ("Un-choose", "Otherwise `board[row][col] = 0`. After all nine digits fail, return `false`."),
    )
    yield multi('''
        5 3 4 6 7 8 9 1 2
        6 7 2 1 9 5 3 4 8
        1 9 8 3 4 2 5 6 7
        8 5 9 7 6 1 4 2 3
        4 2 6 8 5 3 7 9 1
        7 1 3 9 2 4 8 5 6
        9 6 1 5 3 7 2 8 4
        2 8 7 4 1 9 6 3 5
        3 4 5 2 8 6 1 7 9
    ''', py='''
        def is_safe(board, row, col, d):
            for x in range(9):
                if board[row][x] == d or board[x][col] == d:     # same row or same column
                    return False
            r0, c0 = row - row % 3, col - col % 3                # top-left corner of the 3×3 box
            for i in range(3):
                for j in range(3):
                    if board[r0 + i][c0 + j] == d:
                        return False
            return True

        def solve(board):
            for row in range(9):
                for col in range(9):
                    if board[row][col] == 0:                     # first empty cell
                        for d in range(1, 10):
                            if is_safe(board, row, col, d):
                                board[row][col] = d              # choose
                                if solve(board):                 # explore
                                    return True
                                board[row][col] = 0              # un-choose
                        return False                             # no digit fits here → backtrack
            return True                                          # no empty cell left — solved

        board = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
                 [6, 0, 0, 1, 9, 5, 0, 0, 0],
                 [0, 9, 8, 0, 0, 0, 0, 6, 0],
                 [8, 0, 0, 0, 6, 0, 0, 0, 3],
                 [4, 0, 0, 8, 0, 3, 0, 0, 1],
                 [7, 0, 0, 0, 2, 0, 0, 0, 6],
                 [0, 6, 0, 0, 0, 0, 2, 8, 0],
                 [0, 0, 0, 4, 1, 9, 0, 0, 5],
                 [0, 0, 0, 0, 8, 0, 0, 7, 9]]
        if solve(board):
            for row in board:
                print(" ".join(map(str, row)))
        else:
            print("No solution exists")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        bool isSafe(const vector<vector<int>>& b, int row, int col, int d) {
            for (int x = 0; x < 9; x++)
                if (b[row][x] == d || b[x][col] == d) return false;   // same row or same column
            int r0 = row - row % 3, c0 = col - col % 3;               // top-left corner of the 3×3 box
            for (int i = 0; i < 3; i++)
                for (int j = 0; j < 3; j++)
                    if (b[r0 + i][c0 + j] == d) return false;
            return true;
        }

        bool solve(vector<vector<int>>& b) {
            for (int row = 0; row < 9; row++)
                for (int col = 0; col < 9; col++)
                    if (b[row][col] == 0) {                           // first empty cell
                        for (int d = 1; d <= 9; d++)
                            if (isSafe(b, row, col, d)) {
                                b[row][col] = d;                      // choose
                                if (solve(b)) return true;            // explore
                                b[row][col] = 0;                      // un-choose
                            }
                        return false;                                 // no digit fits here → backtrack
                    }
            return true;                                              // no empty cell left — solved
        }

        int main() {
            vector<vector<int>> board = {{5, 3, 0, 0, 7, 0, 0, 0, 0},
                                         {6, 0, 0, 1, 9, 5, 0, 0, 0},
                                         {0, 9, 8, 0, 0, 0, 0, 6, 0},
                                         {8, 0, 0, 0, 6, 0, 0, 0, 3},
                                         {4, 0, 0, 8, 0, 3, 0, 0, 1},
                                         {7, 0, 0, 0, 2, 0, 0, 0, 6},
                                         {0, 6, 0, 0, 0, 0, 2, 8, 0},
                                         {0, 0, 0, 4, 1, 9, 0, 0, 5},
                                         {0, 0, 0, 0, 8, 0, 0, 7, 9}};
            if (!solve(board)) { cout << "No solution exists\\n"; return 0; }
            for (auto& row : board) {
                for (int j = 0; j < 9; j++) cout << (j ? " " : "") << row[j];
                cout << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static boolean isSafe(int[][] b, int row, int col, int d) {
                for (int x = 0; x < 9; x++)
                    if (b[row][x] == d || b[x][col] == d) return false;   // same row or same column
                int r0 = row - row % 3, c0 = col - col % 3;               // top-left corner of the 3×3 box
                for (int i = 0; i < 3; i++)
                    for (int j = 0; j < 3; j++)
                        if (b[r0 + i][c0 + j] == d) return false;
                return true;
            }

            static boolean solve(int[][] b) {
                for (int row = 0; row < 9; row++)
                    for (int col = 0; col < 9; col++)
                        if (b[row][col] == 0) {                           // first empty cell
                            for (int d = 1; d <= 9; d++)
                                if (isSafe(b, row, col, d)) {
                                    b[row][col] = d;                      // choose
                                    if (solve(b)) return true;            // explore
                                    b[row][col] = 0;                      // un-choose
                                }
                            return false;                                 // no digit fits here → backtrack
                        }
                return true;                                              // no empty cell left — solved
            }

            public static void main(String[] args) {
                int[][] board = {{5, 3, 0, 0, 7, 0, 0, 0, 0},
                                 {6, 0, 0, 1, 9, 5, 0, 0, 0},
                                 {0, 9, 8, 0, 0, 0, 0, 6, 0},
                                 {8, 0, 0, 0, 6, 0, 0, 0, 3},
                                 {4, 0, 0, 8, 0, 3, 0, 0, 1},
                                 {7, 0, 0, 0, 2, 0, 0, 0, 6},
                                 {0, 6, 0, 0, 0, 0, 2, 8, 0},
                                 {0, 0, 0, 4, 1, 9, 0, 0, 5},
                                 {0, 0, 0, 0, 8, 0, 0, 7, 9}};
                if (!solve(board)) { System.out.println("No solution exists"); return; }
                for (int[] row : board) {
                    StringBuilder sb = new StringBuilder();
                    for (int j = 0; j < 9; j++) sb.append(j > 0 ? " " : "").append(row[j]);
                    System.out.println(sb);
                }
            }
        }
    ''', js='''
        function isSafe(b, row, col, d) {
            for (let x = 0; x < 9; x++)
                if (b[row][x] === d || b[x][col] === d) return false;   // same row or same column
            const r0 = row - row % 3, c0 = col - col % 3;               // top-left corner of the 3×3 box
            for (let i = 0; i < 3; i++)
                for (let j = 0; j < 3; j++)
                    if (b[r0 + i][c0 + j] === d) return false;
            return true;
        }

        function solve(b) {
            for (let row = 0; row < 9; row++)
                for (let col = 0; col < 9; col++)
                    if (b[row][col] === 0) {                            // first empty cell
                        for (let d = 1; d <= 9; d++)
                            if (isSafe(b, row, col, d)) {
                                b[row][col] = d;                        // choose
                                if (solve(b)) return true;              // explore
                                b[row][col] = 0;                        // un-choose
                            }
                        return false;                                   // no digit fits here → backtrack
                    }
            return true;                                                // no empty cell left — solved
        }

        const board = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
                       [6, 0, 0, 1, 9, 5, 0, 0, 0],
                       [0, 9, 8, 0, 0, 0, 0, 6, 0],
                       [8, 0, 0, 0, 6, 0, 0, 0, 3],
                       [4, 0, 0, 8, 0, 3, 0, 0, 1],
                       [7, 0, 0, 0, 2, 0, 0, 0, 6],
                       [0, 6, 0, 0, 0, 0, 2, 8, 0],
                       [0, 0, 0, 4, 1, 9, 0, 0, 5],
                       [0, 0, 0, 0, 8, 0, 0, 7, 9]];
        if (!solve(board)) console.log("No solution exists");
        else for (const row of board) console.log(row.join(" "));
    ''')
    yield complexity("O(9^m) worst case for m empty cells — pruning makes real puzzles fast", "O(m) recursion depth")
    yield note("Two cheap speed-ups: keep three `bool[9][10]` tables (`rowHas`, `colHas`, `boxHas`) so `isSafe` is `O(1)`, and fill the empty cell with the **fewest candidates** first (most-constrained-variable heuristic) so wrong guesses are discovered as early as possible.", "Optimisation")
    yield pitfall("Returning `false` from the *loop over cells* only after trying all nine digits in the first empty cell is essential. A common bug is to `continue` scanning for other empty cells after the digits fail — that explores the board in the wrong order and reports unsolvable puzzles as solved.")

    yield section("Interview Q&A", "message-question")
    yield qa("What is the difference between backtracking and plain recursion?",
             "Plain recursive enumeration generates every candidate and tests complete ones. Backtracking tests **partial** candidates and abandons a branch as soon as it violates a constraint, so large parts of the recursion tree are never visited. Both have the same worst case; backtracking has a much better typical case.")
    yield qa("When is backtracking the right tool, and when is DP?",
             "Backtracking fits **constraint-satisfaction** and *enumerate all solutions* problems: the sub-problems do not overlap and there is no optimal-substructure recurrence (N-Queens, Sudoku, subsets with a property, permutations). DP fits **optimisation** problems whose sub-problems overlap and can be memoised (knapsack, LCS, edit distance). If you find yourself solving the same sub-state many times in a backtracking search, memoise it — that is DP.")
    yield qa("Why must the state be restored exactly after the recursive call?",
             "The loop that follows will try the next option on the same shared state. If a mark, a digit or a swap is left behind, later branches see a corrupted board and either miss valid solutions or report invalid ones. Rule of thumb: every mutation before the recursive call has a matching inverse right after it.")
    yield qa("How would you print all solutions of N-Queens rather than the first one?",
             "Do not return on success — when `row == N`, record the board and simply return to the caller, which continues its loop. The code above already does this (`solutions.append(...)`), which is why it can report the count `2` for `N = 4`.")
    yield qa("What is the time complexity of backtracking for N-Queens?",
             "Upper bound `O(N!)`: row 0 has `N` choices, row 1 at most `N − 1` columns are not attacked, and so on. The diagonal pruning removes most of those, but no polynomial bound is known — the problem of counting solutions is exponential in practice (92 solutions for N = 8, visited in a few thousand placements).")
