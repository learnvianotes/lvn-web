from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Linked Lists, Stacks & Queues"


@topic(G, "stack", "Stack", "stack-2")
def _():
    yield lead("You know `push` and `pop`. The advanced stack problems are about three ideas: sharing one array between several stacks, the **monotonic stack** that answers *previous/next greater or smaller* questions in `O(n)`, and augmenting a stack so `getMin()` is `O(1)`.")
    yield define("Monotonic stack", "a stack whose elements are kept in sorted order (strictly decreasing or increasing from bottom to top) by popping everything that would break the order before each push. Each element is pushed once and popped at most once, so a whole scan costs `O(n)` even though it contains a nested `while`.")

    yield section("The three families of stack problems", "apps")
    yield cards(
        ("Space sharing", "Two stacks in one array, k stacks in one array. The trick is to let stacks grow towards each other or to thread a free list through the array so no slot is reserved for a stack that is empty.", "box"),
        ("Monotonic stack", "Stock span, previous greater, next greater, largest rectangle in a histogram, largest rectangle of 1s in a matrix. One pattern, five problems.", "chart-bar"),
        ("Augmented stack", "A stack that also answers `getMin()` in `O(1)` — first with a second stack, then with a single extra variable and an encoding trick.", "stack-3"),
        cols=3,
    )

    yield section("The monotonic stack pattern", "bulb")
    yield p("Most *nearest element* questions — *what is the closest element to the left that is greater than me?* — have an obvious `O(n²)` answer: for every `i` scan backwards. The stack version scans once and keeps only the candidates that can still be the answer for some future element.")
    yield idea("Walking left to right, if `arr[j] <= arr[i]` for some `j < i`, then `arr[j]` can never be the *previous greater* of anything after `i` — `arr[i]` is at least as large and closer. So when `arr[i]` arrives, pop every top that is `<= arr[i]`: they are dead. Whatever remains on top is the answer for `i`. Then push `i`. The stack stays strictly decreasing from bottom to top.")
    yield diagram('''
        arr = [15, 10, 18, 12, 4, 6, 2, 8]        stack holds values, decreasing bottom → top

        i  arr[i]  pop while top <= arr[i]      top after pops   previous greater   push → stack
        0   15     –                             (empty)          -1                 [15]
        1   10     –                             15               15                 [15, 10]
        2   18     10, 15                        (empty)          -1                 [18]
        3   12     –                             18               18                 [18, 12]
        4    4     –                             12               12                 [18, 12, 4]
        5    6     4                             12               12                 [18, 12, 6]
        6    2     –                             6                6                  [18, 12, 6, 2]
        7    8     2, 6                          12               12                 [18, 12, 8]
    ''', "Previous greater element with a monotonic stack — every element is pushed once and popped at most once")
    yield table(
        ["Question", "Scan direction", "Pop while", "Stack order (bottom → top)"],
        ["Previous greater", "left → right", "`top <= arr[i]`", "strictly decreasing"],
        ["Next greater", "right → left", "`top <= arr[i]`", "strictly decreasing"],
        ["Previous smaller", "left → right", "`top >= arr[i]`", "strictly increasing"],
        ["Next smaller", "right → left", "`top >= arr[i]`", "strictly increasing"],
    )
    yield note("**Why it is `O(n)` despite the nested loop.** Each index is pushed exactly once, and every iteration of the inner `while` pops one element. There can be no more pops than pushes, so the total work over the whole scan is at most `2n` stack operations. Amortised analysis, not worst-case per step, is the right lens.", "Amortised O(n)")
    yield p("Store **indices** on the stack rather than values when you also need distances (stock span, histogram widths). Store values when only the element itself is wanted. The rest of this topic uses this pattern five times; each section says which variant it is.")

    yield section("Implement two stacks in one array", "box")
    yield io("cap = 6; push1(5), push1(10), push1(15), push1(20); push2(25), push2(30); push2(35)", "push1(20) succeeds, push2(35) fails — the array is full only when 6 elements are stored", "pop1(), pop1(), pop2(), pop2()", "20 15 30 25")
    yield p("**Naive split.** Give the first half of the array to stack 1 and the second half to stack 2. Wasteful: with capacity 6, stack 1 is full after 3 pushes even if stack 2 is empty.")
    yield idea("Start the two stacks at the **two ends** of the array and let them grow towards each other: stack 1 grows from index `0` upwards (`top1` starts at `-1`), stack 2 grows from index `n-1` downwards (`top2` starts at `n`). The array is full only when the two tops meet: `top1 + 1 == top2`. Either stack may use any amount of the shared space.")
    yield diagram('''
        index:   0    1    2    3    4    5
               ┌────┬────┬────┬────┬────┬────┐
               │ 5  │ 10 │ 15 │ 20 │ 30 │ 25 │
               └────┴────┴────┴────┴────┴────┘
                 stack 1 ──────────▶  ◀── stack 2
                              top1 = 3   top2 = 4      full: top1 + 1 == top2
    ''', "After push1(5, 10, 15, 20) and push2(25, 30) in a capacity-6 array")
    yield multi('''
        push1(20): true
        push2(35): false
        pop1: 20
        pop1: 15
        pop2: 30
        pop2: 25
        size1: 2
        size2: 0
    ''', py=r'''
        class TwoStacks:
            def __init__(self, n):
                self.cap = n
                self.arr = [None] * n
                self.top1 = -1        # stack 1 grows from the left end
                self.top2 = n         # stack 2 grows from the right end

            def push1(self, x):
                if self.top1 + 1 == self.top2:     # the tops have met: no free slot
                    return False
                self.top1 += 1
                self.arr[self.top1] = x
                return True

            def push2(self, x):
                if self.top1 + 1 == self.top2:
                    return False
                self.top2 -= 1
                self.arr[self.top2] = x
                return True

            def pop1(self):
                if self.top1 < 0:
                    return None
                x = self.arr[self.top1]
                self.top1 -= 1
                return x

            def pop2(self):
                if self.top2 >= self.cap:
                    return None
                x = self.arr[self.top2]
                self.top2 += 1
                return x

            def size1(self):
                return self.top1 + 1

            def size2(self):
                return self.cap - self.top2

        s = TwoStacks(6)
        for x in (5, 10, 15):
            s.push1(x)
        print("push1(20):", "true" if s.push1(20) else "false")   # a 3+3 split would refuse this
        for x in (25, 30):
            s.push2(x)
        print("push2(35):", "true" if s.push2(35) else "false")   # now the array really is full
        print("pop1:", s.pop1())
        print("pop1:", s.pop1())
        print("pop2:", s.pop2())
        print("pop2:", s.pop2())
        print("size1:", s.size1())
        print("size2:", s.size2())
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        class TwoStacks {
            vector<int> arr;
            int cap, top1, top2;
        public:
            TwoStacks(int n) : arr(n), cap(n), top1(-1), top2(n) {}
            bool push1(int x) {
                if (top1 + 1 == top2) return false;    // the tops have met: no free slot
                arr[++top1] = x;
                return true;
            }
            bool push2(int x) {
                if (top1 + 1 == top2) return false;
                arr[--top2] = x;
                return true;
            }
            int pop1() { return top1 < 0 ? -1 : arr[top1--]; }
            int pop2() { return top2 >= cap ? -1 : arr[top2++]; }
            int size1() const { return top1 + 1; }
            int size2() const { return cap - top2; }
        };

        int main() {
            TwoStacks s(6);
            for (int x : {5, 10, 15}) s.push1(x);
            cout << "push1(20): " << (s.push1(20) ? "true" : "false") << "\n";   // a 3+3 split would refuse this
            for (int x : {25, 30}) s.push2(x);
            cout << "push2(35): " << (s.push2(35) ? "true" : "false") << "\n";   // now the array really is full
            cout << "pop1: " << s.pop1() << "\n";
            cout << "pop1: " << s.pop1() << "\n";
            cout << "pop2: " << s.pop2() << "\n";
            cout << "pop2: " << s.pop2() << "\n";
            cout << "size1: " << s.size1() << "\n";
            cout << "size2: " << s.size2() << "\n";
        }
    ''', java=r'''
        public class Main {
            static class TwoStacks {
                int[] arr;
                int cap, top1, top2;
                TwoStacks(int n) { arr = new int[n]; cap = n; top1 = -1; top2 = n; }
                boolean push1(int x) {
                    if (top1 + 1 == top2) return false;   // the tops have met: no free slot
                    arr[++top1] = x;
                    return true;
                }
                boolean push2(int x) {
                    if (top1 + 1 == top2) return false;
                    arr[--top2] = x;
                    return true;
                }
                int pop1() { return top1 < 0 ? -1 : arr[top1--]; }
                int pop2() { return top2 >= cap ? -1 : arr[top2++]; }
                int size1() { return top1 + 1; }
                int size2() { return cap - top2; }
            }

            public static void main(String[] args) {
                TwoStacks s = new TwoStacks(6);
                for (int x : new int[]{5, 10, 15}) s.push1(x);
                System.out.println("push1(20): " + s.push1(20));   // a 3+3 split would refuse this
                for (int x : new int[]{25, 30}) s.push2(x);
                System.out.println("push2(35): " + s.push2(35));   // now the array really is full
                System.out.println("pop1: " + s.pop1());
                System.out.println("pop1: " + s.pop1());
                System.out.println("pop2: " + s.pop2());
                System.out.println("pop2: " + s.pop2());
                System.out.println("size1: " + s.size1());
                System.out.println("size2: " + s.size2());
            }
        }
    ''', js=r'''
        class TwoStacks {
            constructor(n) {
                this.cap = n;
                this.arr = new Array(n);
                this.top1 = -1;       // stack 1 grows from the left end
                this.top2 = n;        // stack 2 grows from the right end
            }
            push1(x) {
                if (this.top1 + 1 === this.top2) return false;   // the tops have met: no free slot
                this.arr[++this.top1] = x;
                return true;
            }
            push2(x) {
                if (this.top1 + 1 === this.top2) return false;
                this.arr[--this.top2] = x;
                return true;
            }
            pop1() { return this.top1 < 0 ? null : this.arr[this.top1--]; }
            pop2() { return this.top2 >= this.cap ? null : this.arr[this.top2++]; }
            size1() { return this.top1 + 1; }
            size2() { return this.cap - this.top2; }
        }

        const s = new TwoStacks(6);
        for (const x of [5, 10, 15]) s.push1(x);
        console.log("push1(20):", s.push1(20));   // a 3+3 split would refuse this
        for (const x of [25, 30]) s.push2(x);
        console.log("push2(35):", s.push2(35));   // now the array really is full
        console.log("pop1:", s.pop1());
        console.log("pop1:", s.pop1());
        console.log("pop2:", s.pop2());
        console.log("pop2:", s.pop2());
        console.log("size1:", s.size1());
        console.log("size2:", s.size2());
    ''')
    yield complexity("O(1) per operation", "O(n) for the shared array")
    yield pitfall("The full test is `top1 + 1 == top2`, not `top1 == top2`. With `top1 = -1` and `top2 = n` the gap between them is exactly the number of free slots; when it reaches zero the tops are adjacent, never equal.")

    yield section("Implement k stacks in one array", "grid-dots")
    yield io("n = 10, k = 3; push(15, 0), push(45, 1), push(17, 0), push(39, 1), push(11, 2)", "pop(0) → 17, pop(1) → 39, pop(2) → 11, pop(0) → 15")
    yield p("The two-ends trick does not extend to three or more stacks. The general solution threads **linked lists through the array**: every stack is a linked list of slots, and the unused slots form one more linked list, the *free list*. Three small arrays do all the bookkeeping.")
    yield table(
        ["Array / variable", "Size", "Meaning"],
        ["`arr[n]`", "`n`", "the stored values"],
        ["`top[k]`", "`k`", "`top[sn]` = index of the top slot of stack `sn`; `-1` when that stack is empty"],
        ["`next[n]`", "`n`", "for a used slot: index of the slot *below* it in its stack; for a free slot: index of the next free slot (`-1` = none)"],
        ["`free`", "1", "index of the first free slot — the top of the free list"],
    )
    yield idea("`push(x, sn)` takes the slot `i = free` off the free list (`free = next[i]`), stores `x` there and links it on top of stack `sn` (`next[i] = top[sn]; top[sn] = i`). `pop(sn)` does the reverse: unlink `i = top[sn]` (`top[sn] = next[i]`) and give the slot back (`next[i] = free; free = i`). The array is full exactly when `free == -1`, regardless of how the stacks share it.")
    yield diagram('''
        after push(15,0) push(45,1) push(17,0) push(39,1) push(11,2)   with n = 10, k = 3

        index :  0    1    2    3    4    5    6    7    8    9
        arr   : 15   45   17   39   11    _    _    _    _    _
        next  : -1   -1    0    1   -1    6    7    8    9   -1
                 ↑         ↑    ↑    ↑         └── free list: 5 → 6 → 7 → 8 → 9 → -1
                 └─────────┘    │    └─ stack 2: 11                      free = 5
                 stack 0: 17 → 15    stack 1: 39 → 45          top = [2, 3, 4]
    ''', "Every stack is a linked list of array slots; `next[]` doubles as the free list")
    yield multi('''
        pop(0): 17
        pop(1): 39
        pop(2): 11
        pop(0): 15
        empty(2): true
        empty(0): true
    ''', py=r'''
        class KStacks:
            def __init__(self, n, k):
                self.arr = [None] * n
                self.top = [-1] * k                     # top[sn] = index of the top of stack sn
                self.next = [i + 1 for i in range(n)]   # free list: slot i → slot i+1
                self.next[n - 1] = -1
                self.free = 0                           # first free slot

            def is_full(self):
                return self.free == -1

            def is_empty(self, sn):
                return self.top[sn] == -1

            def push(self, x, sn):
                if self.is_full():
                    return False
                i = self.free
                self.free = self.next[i]        # take the slot off the free list
                self.arr[i] = x
                self.next[i] = self.top[sn]     # link it above the old top of stack sn
                self.top[sn] = i
                return True

            def pop(self, sn):
                if self.is_empty(sn):
                    return None
                i = self.top[sn]
                self.top[sn] = self.next[i]     # unlink the top slot
                self.next[i] = self.free        # give it back to the free list
                self.free = i
                return self.arr[i]

        s = KStacks(10, 3)
        for x, sn in ((15, 0), (45, 1), (17, 0), (39, 1), (11, 2)):
            s.push(x, sn)
        print("pop(0):", s.pop(0))
        print("pop(1):", s.pop(1))
        print("pop(2):", s.pop(2))
        print("pop(0):", s.pop(0))
        print("empty(2):", "true" if s.is_empty(2) else "false")
        print("empty(0):", "true" if s.is_empty(0) else "false")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        class KStacks {
            vector<int> arr, top, nxt;
            int freeTop;
        public:
            KStacks(int n, int k) : arr(n), top(k, -1), nxt(n), freeTop(0) {
                for (int i = 0; i < n; i++) nxt[i] = i + 1;   // free list: slot i → slot i+1
                nxt[n - 1] = -1;
            }
            bool isFull() const { return freeTop == -1; }
            bool isEmpty(int sn) const { return top[sn] == -1; }
            bool push(int x, int sn) {
                if (isFull()) return false;
                int i = freeTop;
                freeTop = nxt[i];          // take the slot off the free list
                arr[i] = x;
                nxt[i] = top[sn];          // link it above the old top of stack sn
                top[sn] = i;
                return true;
            }
            int pop(int sn) {
                if (isEmpty(sn)) return -1;
                int i = top[sn];
                top[sn] = nxt[i];          // unlink the top slot
                nxt[i] = freeTop;          // give it back to the free list
                freeTop = i;
                return arr[i];
            }
        };

        int main() {
            KStacks s(10, 3);
            int xs[] = {15, 45, 17, 39, 11}, sns[] = {0, 1, 0, 1, 2};
            for (int i = 0; i < 5; i++) s.push(xs[i], sns[i]);
            cout << "pop(0): " << s.pop(0) << "\n";
            cout << "pop(1): " << s.pop(1) << "\n";
            cout << "pop(2): " << s.pop(2) << "\n";
            cout << "pop(0): " << s.pop(0) << "\n";
            cout << "empty(2): " << (s.isEmpty(2) ? "true" : "false") << "\n";
            cout << "empty(0): " << (s.isEmpty(0) ? "true" : "false") << "\n";
        }
    ''', java=r'''
        import java.util.Arrays;

        public class Main {
            static class KStacks {
                int[] arr, top, next;
                int free;
                KStacks(int n, int k) {
                    arr = new int[n];
                    top = new int[k];
                    Arrays.fill(top, -1);
                    next = new int[n];
                    for (int i = 0; i < n; i++) next[i] = i + 1;   // free list: slot i → slot i+1
                    next[n - 1] = -1;
                    free = 0;
                }
                boolean isFull() { return free == -1; }
                boolean isEmpty(int sn) { return top[sn] == -1; }
                boolean push(int x, int sn) {
                    if (isFull()) return false;
                    int i = free;
                    free = next[i];            // take the slot off the free list
                    arr[i] = x;
                    next[i] = top[sn];         // link it above the old top of stack sn
                    top[sn] = i;
                    return true;
                }
                int pop(int sn) {
                    if (isEmpty(sn)) return -1;
                    int i = top[sn];
                    top[sn] = next[i];         // unlink the top slot
                    next[i] = free;            // give it back to the free list
                    free = i;
                    return arr[i];
                }
            }

            public static void main(String[] args) {
                KStacks s = new KStacks(10, 3);
                int[] xs = {15, 45, 17, 39, 11}, sns = {0, 1, 0, 1, 2};
                for (int i = 0; i < 5; i++) s.push(xs[i], sns[i]);
                System.out.println("pop(0): " + s.pop(0));
                System.out.println("pop(1): " + s.pop(1));
                System.out.println("pop(2): " + s.pop(2));
                System.out.println("pop(0): " + s.pop(0));
                System.out.println("empty(2): " + s.isEmpty(2));
                System.out.println("empty(0): " + s.isEmpty(0));
            }
        }
    ''', js=r'''
        class KStacks {
            constructor(n, k) {
                this.arr = new Array(n);
                this.top = new Array(k).fill(-1);                 // top[sn] = index of the top of stack sn
                this.next = Array.from({ length: n }, (_, i) => i + 1);   // free list: slot i → slot i+1
                this.next[n - 1] = -1;
                this.free = 0;                                    // first free slot
            }
            isFull() { return this.free === -1; }
            isEmpty(sn) { return this.top[sn] === -1; }
            push(x, sn) {
                if (this.isFull()) return false;
                const i = this.free;
                this.free = this.next[i];        // take the slot off the free list
                this.arr[i] = x;
                this.next[i] = this.top[sn];     // link it above the old top of stack sn
                this.top[sn] = i;
                return true;
            }
            pop(sn) {
                if (this.isEmpty(sn)) return null;
                const i = this.top[sn];
                this.top[sn] = this.next[i];     // unlink the top slot
                this.next[i] = this.free;        // give it back to the free list
                this.free = i;
                return this.arr[i];
            }
        }

        const s = new KStacks(10, 3);
        for (const [x, sn] of [[15, 0], [45, 1], [17, 0], [39, 1], [11, 2]]) s.push(x, sn);
        console.log("pop(0):", s.pop(0));
        console.log("pop(1):", s.pop(1));
        console.log("pop(2):", s.pop(2));
        console.log("pop(0):", s.pop(0));
        console.log("empty(2):", s.isEmpty(2));
        console.log("empty(0):", s.isEmpty(0));
    ''')
    yield complexity("O(1) per operation", "O(n + k) — `arr` and `next` of size n, `top` of size k")
    yield note("`next[]` plays two roles: inside a stack it points *down* to the element below; inside the free list it points to the *next free slot*. A slot is in exactly one of the two at any moment, so one array suffices. This is exactly how a memory allocator keeps its free blocks.")

    yield section("Stock span problem", "chart-bar")
    yield io("price = [13, 15, 12, 14, 16, 8, 6, 4, 10, 30]", "1 2 1 2 5 1 1 1 4 10")
    yield p("The **span** of a stock's price on day `i` is the number of consecutive days ending at `i` (including `i`) on which the price was less than or equal to `price[i]`. Day 4 (price 16) has span 5 because all of 13, 15, 12, 14 are below 16; day 8 (price 10) has span 4 because 8, 6, 4 are below it but 16 stops the run.")
    yield snippet("py", r'''
        def stock_span_naive(price):
            span = []
            for i in range(len(price)):
                j = i - 1
                while j >= 0 and price[j] <= price[i]:   # walk back while prices are not higher
                    j -= 1
                span.append(i - j)
            return span

        print(*stock_span_naive([13, 15, 12, 14, 16, 8, 6, 4, 10, 30]))
    ''', out="1 2 1 2 5 1 1 1 4 10", caption="Naive — O(n²): for each day walk back until a higher price")
    yield idea("`span[i] = i − (index of the previous greater element)`, or `i + 1` if there is none. So this is the **previous greater** variant of the monotonic stack with *indices* on the stack: pop every index whose price is `<= price[i]`, read the index left on top, push `i`.")
    yield multi("1 2 1 2 5 1 1 1 4 10", py=r'''
        def stock_span(price):
            st = []                      # indices; prices strictly decreasing bottom → top
            span = [0] * len(price)
            for i in range(len(price)):
                while st and price[st[-1]] <= price[i]:   # those days can never be a previous greater again
                    st.pop()
                span[i] = i + 1 if not st else i - st[-1]
                st.append(i)
            return span

        print(*stock_span([13, 15, 12, 14, 16, 8, 6, 4, 10, 30]))
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        #include <vector>
        using namespace std;

        vector<int> stockSpan(const vector<int>& price) {
            int n = price.size();
            vector<int> span(n);
            stack<int> st;               // indices; prices strictly decreasing bottom → top
            for (int i = 0; i < n; i++) {
                while (!st.empty() && price[st.top()] <= price[i]) st.pop();   // dead candidates
                span[i] = st.empty() ? i + 1 : i - st.top();
                st.push(i);
            }
            return span;
        }

        int main() {
            vector<int> price = {13, 15, 12, 14, 16, 8, 6, 4, 10, 30};
            for (int s : stockSpan(price)) cout << s << " ";
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int[] stockSpan(int[] price) {
                int n = price.length;
                int[] span = new int[n];
                Deque<Integer> st = new ArrayDeque<>();   // indices; prices strictly decreasing bottom → top
                for (int i = 0; i < n; i++) {
                    while (!st.isEmpty() && price[st.peek()] <= price[i]) st.pop();   // dead candidates
                    span[i] = st.isEmpty() ? i + 1 : i - st.peek();
                    st.push(i);
                }
                return span;
            }

            public static void main(String[] args) {
                int[] price = {13, 15, 12, 14, 16, 8, 6, 4, 10, 30};
                StringBuilder sb = new StringBuilder();
                for (int s : stockSpan(price)) sb.append(s).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js=r'''
        function stockSpan(price) {
            const st = [];               // indices; prices strictly decreasing bottom → top
            const span = new Array(price.length);
            for (let i = 0; i < price.length; i++) {
                while (st.length && price[st[st.length - 1]] <= price[i]) st.pop();   // dead candidates
                span[i] = st.length === 0 ? i + 1 : i - st[st.length - 1];
                st.push(i);
            }
            return span;
        }

        console.log(stockSpan([13, 15, 12, 14, 16, 8, 6, 4, 10, 30]).join(" "));
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("Pop on `<=`, not `<`. An earlier day with the *same* price cannot stop the span (the definition says *less than or equal*), so it must not survive on the stack. The strictness of the comparison is the detail that changes between the five monotonic-stack problems — decide it from the problem statement every time.")

    yield section("Previous greater element", "arrow-left")
    yield io("arr = [15, 10, 18, 12, 4, 6, 2, 8]", "-1 15 -1 18 12 12 6 12")
    yield p("For every element, the nearest element to its **left** that is strictly greater; `-1` if there is none. This is the pattern from the overview section in its purest form — the trace table above is exactly this input.")
    yield snippet("py", r'''
        def previous_greater_naive(arr):
            res = []
            for i in range(len(arr)):
                pg = -1
                for j in range(i - 1, -1, -1):     # scan left until something bigger
                    if arr[j] > arr[i]:
                        pg = arr[j]
                        break
                res.append(pg)
            return res

        print(*previous_greater_naive([15, 10, 18, 12, 4, 6, 2, 8]))
    ''', out="-1 15 -1 18 12 12 6 12", caption="Naive — O(n²)")
    yield idea("Left-to-right scan, values on the stack, pop while `top <= arr[i]`. After the pops the top (if any) is the nearest greater element to the left — everything between it and `i` was smaller than `arr[i]` and has been discarded.")
    yield multi("-1 15 -1 18 12 12 6 12", py=r'''
        def previous_greater(arr):
            st = []                           # values; strictly decreasing bottom → top
            res = []
            for x in arr:
                while st and st[-1] <= x:     # smaller-or-equal elements can never be an answer again
                    st.pop()
                res.append(-1 if not st else st[-1])
                st.append(x)
            return res

        print(*previous_greater([15, 10, 18, 12, 4, 6, 2, 8]))
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        #include <vector>
        using namespace std;

        vector<int> previousGreater(const vector<int>& arr) {
            stack<int> st;                    // values; strictly decreasing bottom → top
            vector<int> res;
            for (int x : arr) {
                while (!st.empty() && st.top() <= x) st.pop();   // can never be an answer again
                res.push_back(st.empty() ? -1 : st.top());
                st.push(x);
            }
            return res;
        }

        int main() {
            for (int v : previousGreater({15, 10, 18, 12, 4, 6, 2, 8})) cout << v << " ";
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int[] previousGreater(int[] arr) {
                Deque<Integer> st = new ArrayDeque<>();   // values; strictly decreasing bottom → top
                int[] res = new int[arr.length];
                for (int i = 0; i < arr.length; i++) {
                    while (!st.isEmpty() && st.peek() <= arr[i]) st.pop();   // can never be an answer again
                    res[i] = st.isEmpty() ? -1 : st.peek();
                    st.push(arr[i]);
                }
                return res;
            }

            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder();
                for (int v : previousGreater(new int[]{15, 10, 18, 12, 4, 6, 2, 8})) sb.append(v).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js=r'''
        function previousGreater(arr) {
            const st = [];                    // values; strictly decreasing bottom → top
            const res = [];
            for (const x of arr) {
                while (st.length && st[st.length - 1] <= x) st.pop();   // can never be an answer again
                res.push(st.length === 0 ? -1 : st[st.length - 1]);
                st.push(x);
            }
            return res;
        }

        console.log(previousGreater([15, 10, 18, 12, 4, 6, 2, 8]).join(" "));
    ''')
    yield complexity("O(n)", "O(n)")

    yield section("Next greater element", "arrow-right")
    yield io("arr = [5, 15, 10, 8, 12, 7]", "15 -1 12 12 -1 -1")
    yield p("Mirror image: for every element, the nearest **strictly greater** element to its **right**, `-1` if none. (The original notes listed seven answers for six inputs — the correct output has one answer per element.)")
    yield snippet("py", r'''
        def next_greater_naive(arr):
            res = []
            for i in range(len(arr)):
                ng = -1
                for j in range(i + 1, len(arr)):
                    if arr[j] > arr[i]:
                        ng = arr[j]
                        break
                res.append(ng)
            return res

        print(*next_greater_naive([5, 15, 10, 8, 12, 7]))
    ''', out="15 -1 12 12 -1 -1", caption="Naive — O(n²)")
    yield idea("Run the previous-greater algorithm **from right to left**: when the scan reaches `i`, the stack holds exactly the elements to its right that are still candidates, so after popping the `<= arr[i]` ones, the top is the next greater. Fill `res[i]` in reverse and print in order.")
    yield multi("15 -1 12 12 -1 -1", py=r'''
        def next_greater(arr):
            n = len(arr)
            st = []                           # values to the right of i; strictly decreasing bottom → top
            res = [-1] * n
            for i in range(n - 1, -1, -1):    # right to left
                while st and st[-1] <= arr[i]:
                    st.pop()
                res[i] = -1 if not st else st[-1]
                st.append(arr[i])
            return res

        print(*next_greater([5, 15, 10, 8, 12, 7]))
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        #include <vector>
        using namespace std;

        vector<int> nextGreater(const vector<int>& arr) {
            int n = arr.size();
            stack<int> st;                    // values to the right of i; strictly decreasing bottom → top
            vector<int> res(n, -1);
            for (int i = n - 1; i >= 0; i--) {          // right to left
                while (!st.empty() && st.top() <= arr[i]) st.pop();
                res[i] = st.empty() ? -1 : st.top();
                st.push(arr[i]);
            }
            return res;
        }

        int main() {
            for (int v : nextGreater({5, 15, 10, 8, 12, 7})) cout << v << " ";
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int[] nextGreater(int[] arr) {
                int n = arr.length;
                Deque<Integer> st = new ArrayDeque<>();   // values to the right of i; strictly decreasing
                int[] res = new int[n];
                for (int i = n - 1; i >= 0; i--) {        // right to left
                    while (!st.isEmpty() && st.peek() <= arr[i]) st.pop();
                    res[i] = st.isEmpty() ? -1 : st.peek();
                    st.push(arr[i]);
                }
                return res;
            }

            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder();
                for (int v : nextGreater(new int[]{5, 15, 10, 8, 12, 7})) sb.append(v).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js=r'''
        function nextGreater(arr) {
            const n = arr.length;
            const st = [];                    // values to the right of i; strictly decreasing bottom → top
            const res = new Array(n).fill(-1);
            for (let i = n - 1; i >= 0; i--) {            // right to left
                while (st.length && st[st.length - 1] <= arr[i]) st.pop();
                res[i] = st.length === 0 ? -1 : st[st.length - 1];
                st.push(arr[i]);
            }
            return res;
        }

        console.log(nextGreater([5, 15, 10, 8, 12, 7]).join(" "));
    ''')
    yield complexity("O(n)", "O(n)")
    yield note("**Left-to-right alternative.** Keep *indices* on the stack and scan forwards; when `arr[i]` pops an index `j`, you have just discovered that `arr[i]` is the next greater of `arr[j]`, so set `res[j] = arr[i]`. Whatever remains on the stack at the end gets `-1`. Same complexity; this version is the one to use when the input arrives as a stream and cannot be scanned backwards.")

    yield section("Largest rectangular area in a histogram", "chart-histogram")
    yield io("heights = [6, 2, 5, 4, 1, 5, 6]", "10")
    yield diagram('''
                       ■                  ■
          ■            ■               ■  ■
          ■      ■     ■               ■  ■
          ■      ■  ■  ■               ■  ■
          ■  ■   ■  ■  ■               ■  ■
          ■  ■   ■  ■  ■   ■           ■  ■       largest rectangle: height 5 over bars 5,6 → 10
          6  2   5  4  1   5  6
    ''', "Bars of width 1; the best rectangle spans the last two bars at height 5 (area 10)")
    yield p("Every bar is the *shortest bar* of exactly one maximal rectangle: the one that extends from the previous smaller bar to the next smaller bar. So the answer is `max over i of heights[i] × (nextSmaller[i] − prevSmaller[i] − 1)`. The problem is finding both boundaries fast — which is the monotonic stack again, this time the **smaller** variants.")
    yield snippet("py", r'''
        def max_area_naive(h):
            best = 0
            for i in range(len(h)):
                width = 1
                j = i - 1
                while j >= 0 and h[j] >= h[i]:      # extend left while bars are at least as tall
                    width += 1
                    j -= 1
                j = i + 1
                while j < len(h) and h[j] >= h[i]:  # extend right
                    width += 1
                    j += 1
                best = max(best, h[i] * width)
            return best

        print(max_area_naive([6, 2, 5, 4, 1, 5, 6]))
    ''', out="10", caption="Naive — O(n²): for every bar, extend left and right while the bars stay at least as tall")
    yield snippet("py", r'''
        def prev_smaller(h):
            st, res = [], [-1] * len(h)
            for i in range(len(h)):
                while st and h[st[-1]] >= h[i]:
                    st.pop()
                res[i] = st[-1] if st else -1          # -1 = no smaller bar on the left
                st.append(i)
            return res

        def next_smaller(h):
            n = len(h)
            st, res = [], [n] * n
            for i in range(n - 1, -1, -1):
                while st and h[st[-1]] >= h[i]:
                    st.pop()
                res[i] = st[-1] if st else n           # n = no smaller bar on the right
                st.append(i)
            return res

        def max_area_two_pass(h):
            ps, ns = prev_smaller(h), next_smaller(h)
            return max(h[i] * (ns[i] - ps[i] - 1) for i in range(len(h)))

        h = [6, 2, 5, 4, 1, 5, 6]
        print(*prev_smaller(h))
        print(*next_smaller(h))
        print(max_area_two_pass(h))
    ''', out='''
        -1 -1 1 1 -1 4 5
        1 4 3 4 7 7 7
        10
    ''', caption="Better — O(n) with two monotonic-stack passes (previous smaller, next smaller)")
    yield idea("**One pass.** Keep indices on a stack with heights *increasing* bottom to top. When `heights[i]` is smaller than the top, the top bar's rectangle ends here: `i` is its next smaller, and the index beneath it on the stack is its previous smaller, so its area is `heights[top] × (i − below − 1)`. Pop it and repeat. After the scan, treat a bar of height `0` at index `n` as the final element so every remaining bar is popped and measured.")
    yield multi("10", py=r'''
        def max_histogram_area(h):
            n = len(h)
            st = []                     # indices; heights increasing bottom → top
            best = 0
            for i in range(n + 1):
                cur = h[i] if i < n else 0            # a 0-high bar at the end flushes the stack
                while st and h[st[-1]] >= cur:
                    top = st.pop()                    # i is the next smaller of bar `top`
                    left = st[-1] if st else -1       # the bar below is its previous smaller
                    best = max(best, h[top] * (i - left - 1))
                st.append(i)
            return best

        print(max_histogram_area([6, 2, 5, 4, 1, 5, 6]))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <stack>
        #include <vector>
        using namespace std;

        int maxHistogramArea(const vector<int>& h) {
            int n = h.size();
            stack<int> st;              // indices; heights increasing bottom → top
            int best = 0;
            for (int i = 0; i <= n; i++) {
                int cur = i < n ? h[i] : 0;           // a 0-high bar at the end flushes the stack
                while (!st.empty() && h[st.top()] >= cur) {
                    int top = st.top(); st.pop();     // i is the next smaller of bar `top`
                    int left = st.empty() ? -1 : st.top();   // the bar below is its previous smaller
                    best = max(best, h[top] * (i - left - 1));
                }
                st.push(i);
            }
            return best;
        }

        int main() {
            cout << maxHistogramArea({6, 2, 5, 4, 1, 5, 6}) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int maxHistogramArea(int[] h) {
                int n = h.length;
                Deque<Integer> st = new ArrayDeque<>();   // indices; heights increasing bottom → top
                int best = 0;
                for (int i = 0; i <= n; i++) {
                    int cur = i < n ? h[i] : 0;           // a 0-high bar at the end flushes the stack
                    while (!st.isEmpty() && h[st.peek()] >= cur) {
                        int top = st.pop();               // i is the next smaller of bar `top`
                        int left = st.isEmpty() ? -1 : st.peek();   // the bar below is its previous smaller
                        best = Math.max(best, h[top] * (i - left - 1));
                    }
                    st.push(i);
                }
                return best;
            }

            public static void main(String[] args) {
                System.out.println(maxHistogramArea(new int[]{6, 2, 5, 4, 1, 5, 6}));
            }
        }
    ''', js=r'''
        function maxHistogramArea(h) {
            const n = h.length;
            const st = [];              // indices; heights increasing bottom → top
            let best = 0;
            for (let i = 0; i <= n; i++) {
                const cur = i < n ? h[i] : 0;             // a 0-high bar at the end flushes the stack
                while (st.length && h[st[st.length - 1]] >= cur) {
                    const top = st.pop();                 // i is the next smaller of bar `top`
                    const left = st.length ? st[st.length - 1] : -1;   // the bar below is its previous smaller
                    best = Math.max(best, h[top] * (i - left - 1));
                }
                st.push(i);
            }
            return best;
        }

        console.log(maxHistogramArea([6, 2, 5, 4, 1, 5, 6]));
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("Two off-by-one traps. The width is `i − left − 1` (the bars strictly between the two smaller ones), and when the stack is empty after the pop, `left` must be `−1`, not `0`. Test on a strictly increasing input such as `[1, 2, 3]` (answer 4) where nothing is popped until the sentinel.")
    yield note("Popping on `>=` (equal heights too) is safe: when two bars have the same height the one popped first gets a width that is too small, but the last one of the run extends over all of them and reports the full rectangle.")

    yield section("Largest rectangle with all 1s in a binary matrix", "table")
    yield io("mat = [[0,1,1,0], [1,1,1,1], [1,1,1,1], [1,1,0,0]]", "8")
    yield p("**Naive:** take every cell as a top-left corner, try every width and height, check that the rectangle contains only 1s — `O(R³C³)` or `O(R²C²)` with prefix sums. The efficient solution reuses the histogram algorithm row by row.")
    yield idea("Treat each row as the **base of a histogram**: `height[j]` is the number of consecutive 1s ending at the current row in column `j` (`0` if the cell is `0`). A rectangle of 1s whose bottom edge is on this row is exactly a rectangle under that histogram, so `maxHistogramArea(height)` for every row — keeping the best — is the answer.")
    yield diagram('''
        matrix          height[] after each row        best histogram area
        0 1 1 0         0 1 1 0                        2
        1 1 1 1         1 2 2 1                        4
        1 1 1 1         2 3 3 2                        8   ← 4 columns × height 2
        1 1 0 0         3 4 0 0                        6
    ''', "Each row's heights form a histogram; the maximum over all rows is 8")
    yield multi("8", py=r'''
        def max_histogram_area(h):
            st, best = [], 0
            for i in range(len(h) + 1):
                cur = h[i] if i < len(h) else 0
                while st and h[st[-1]] >= cur:
                    top = st.pop()
                    left = st[-1] if st else -1
                    best = max(best, h[top] * (i - left - 1))
                st.append(i)
            return best

        def max_rectangle_of_ones(mat):
            if not mat:
                return 0
            cols = len(mat[0])
            height = [0] * cols
            best = 0
            for row in mat:
                for j in range(cols):
                    height[j] = height[j] + 1 if row[j] == 1 else 0   # grow the bar or reset it
                best = max(best, max_histogram_area(height))          # best rectangle ending on this row
            return best

        mat = [[0, 1, 1, 0],
               [1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 0, 0]]
        print(max_rectangle_of_ones(mat))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <stack>
        #include <vector>
        using namespace std;

        int maxHistogramArea(const vector<int>& h) {
            int n = h.size(), best = 0;
            stack<int> st;
            for (int i = 0; i <= n; i++) {
                int cur = i < n ? h[i] : 0;
                while (!st.empty() && h[st.top()] >= cur) {
                    int top = st.top(); st.pop();
                    int left = st.empty() ? -1 : st.top();
                    best = max(best, h[top] * (i - left - 1));
                }
                st.push(i);
            }
            return best;
        }

        int maxRectangleOfOnes(const vector<vector<int>>& mat) {
            if (mat.empty()) return 0;
            int cols = mat[0].size(), best = 0;
            vector<int> height(cols, 0);
            for (const auto& row : mat) {
                for (int j = 0; j < cols; j++)
                    height[j] = row[j] == 1 ? height[j] + 1 : 0;      // grow the bar or reset it
                best = max(best, maxHistogramArea(height));           // best rectangle ending on this row
            }
            return best;
        }

        int main() {
            vector<vector<int>> mat = {{0, 1, 1, 0},
                                       {1, 1, 1, 1},
                                       {1, 1, 1, 1},
                                       {1, 1, 0, 0}};
            cout << maxRectangleOfOnes(mat) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int maxHistogramArea(int[] h) {
                int n = h.length, best = 0;
                Deque<Integer> st = new ArrayDeque<>();
                for (int i = 0; i <= n; i++) {
                    int cur = i < n ? h[i] : 0;
                    while (!st.isEmpty() && h[st.peek()] >= cur) {
                        int top = st.pop();
                        int left = st.isEmpty() ? -1 : st.peek();
                        best = Math.max(best, h[top] * (i - left - 1));
                    }
                    st.push(i);
                }
                return best;
            }

            static int maxRectangleOfOnes(int[][] mat) {
                if (mat.length == 0) return 0;
                int cols = mat[0].length, best = 0;
                int[] height = new int[cols];
                for (int[] row : mat) {
                    for (int j = 0; j < cols; j++)
                        height[j] = row[j] == 1 ? height[j] + 1 : 0;   // grow the bar or reset it
                    best = Math.max(best, maxHistogramArea(height));   // best rectangle ending on this row
                }
                return best;
            }

            public static void main(String[] args) {
                int[][] mat = {{0, 1, 1, 0},
                               {1, 1, 1, 1},
                               {1, 1, 1, 1},
                               {1, 1, 0, 0}};
                System.out.println(maxRectangleOfOnes(mat));
            }
        }
    ''', js=r'''
        function maxHistogramArea(h) {
            const st = [];
            let best = 0;
            for (let i = 0; i <= h.length; i++) {
                const cur = i < h.length ? h[i] : 0;
                while (st.length && h[st[st.length - 1]] >= cur) {
                    const top = st.pop();
                    const left = st.length ? st[st.length - 1] : -1;
                    best = Math.max(best, h[top] * (i - left - 1));
                }
                st.push(i);
            }
            return best;
        }

        function maxRectangleOfOnes(mat) {
            if (mat.length === 0) return 0;
            const cols = mat[0].length;
            const height = new Array(cols).fill(0);
            let best = 0;
            for (const row of mat) {
                for (let j = 0; j < cols; j++)
                    height[j] = row[j] === 1 ? height[j] + 1 : 0;      // grow the bar or reset it
                best = Math.max(best, maxHistogramArea(height));       // best rectangle ending on this row
            }
            return best;
        }

        const mat = [[0, 1, 1, 0],
                     [1, 1, 1, 1],
                     [1, 1, 1, 1],
                     [1, 1, 0, 0]];
        console.log(maxRectangleOfOnes(mat));
    ''')
    yield complexity("O(R × C)", "O(C) for the height array (plus the stack)")
    yield pitfall("Reset `height[j]` to `0` on a `0` cell — do not just skip it. A column that keeps its old height after a `0` would let a rectangle *jump over* the gap. The original notes' second version modified the matrix in place (`mat[i][j] += mat[i-1][j]`), which also works but destroys the input; a separate `height` array is the cleaner habit.")

    yield section("Design a stack with getMin() in O(1) — auxiliary stack", "arrow-down")
    yield io("push(20), push(10), getMin(), push(5), getMin(), pop(), getMin(), pop(), getMin()", "10 5 10 20")
    yield p("**Naive:** keep an ordinary stack and compute `min(stack)` on demand — `getMin()` becomes `O(n)`. The requirement is `O(1)` for *every* operation including `getMin()`.")
    yield idea("Keep a second stack `mins` in lock-step with the main one: `mins[i]` is the minimum of the main stack's bottom `i + 1` elements. On `push(x)` push `min(x, mins.top)`; on `pop()` pop both. `getMin()` is simply `mins.top`. Because the two stacks always have the same height, popping the main stack automatically *un-does* the minimum that element introduced.")
    yield diagram('''
        operation    main stack       mins stack      getMin()
        push(20)     [20]             [20]            20
        push(10)     [20, 10]         [20, 10]        10
        push(5)      [20, 10, 5]      [20, 10, 5]     5
        push(12)     [20, 10, 5, 12]  [20, 10, 5, 5]  5     ← 12 does not lower the min, so 5 is repeated
        pop()        [20, 10, 5]      [20, 10, 5]     5
        pop()        [20, 10]         [20, 10]        10
    ''', "mins[i] always equals the minimum of main[0..i]")
    yield multi('''
        getMin: 10
        getMin: 5
        pop: 5
        getMin: 10
        pop: 10
        getMin: 20
    ''', py=r'''
        class MinStack:
            def __init__(self):
                self.main = []
                self.mins = []               # mins[i] = min of main[0..i]

            def push(self, x):
                self.main.append(x)
                self.mins.append(x if not self.mins else min(x, self.mins[-1]))

            def pop(self):
                self.mins.pop()              # the two stacks always move together
                return self.main.pop()

            def top(self):
                return self.main[-1]

            def get_min(self):
                return self.mins[-1]

        s = MinStack()
        s.push(20)
        s.push(10)
        print("getMin:", s.get_min())
        s.push(5)
        print("getMin:", s.get_min())
        print("pop:", s.pop())
        print("getMin:", s.get_min())
        print("pop:", s.pop())
        print("getMin:", s.get_min())
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <stack>
        using namespace std;

        class MinStack {
            stack<int> main_, mins;      // mins.top() = min of everything in main_
        public:
            void push(int x) {
                main_.push(x);
                mins.push(mins.empty() ? x : min(x, mins.top()));
            }
            int pop() {
                int x = main_.top();
                main_.pop();
                mins.pop();              // the two stacks always move together
                return x;
            }
            int top() const { return main_.top(); }
            int getMin() const { return mins.top(); }
        };

        int main() {
            MinStack s;
            s.push(20);
            s.push(10);
            cout << "getMin: " << s.getMin() << "\n";
            s.push(5);
            cout << "getMin: " << s.getMin() << "\n";
            cout << "pop: " << s.pop() << "\n";
            cout << "getMin: " << s.getMin() << "\n";
            cout << "pop: " << s.pop() << "\n";
            cout << "getMin: " << s.getMin() << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class MinStack {
                Deque<Integer> main = new ArrayDeque<>();
                Deque<Integer> mins = new ArrayDeque<>();   // mins.peek() = min of everything in main
                void push(int x) {
                    main.push(x);
                    mins.push(mins.isEmpty() ? x : Math.min(x, mins.peek()));
                }
                int pop() {
                    mins.pop();                              // the two stacks always move together
                    return main.pop();
                }
                int top() { return main.peek(); }
                int getMin() { return mins.peek(); }
            }

            public static void main(String[] args) {
                MinStack s = new MinStack();
                s.push(20);
                s.push(10);
                System.out.println("getMin: " + s.getMin());
                s.push(5);
                System.out.println("getMin: " + s.getMin());
                System.out.println("pop: " + s.pop());
                System.out.println("getMin: " + s.getMin());
                System.out.println("pop: " + s.pop());
                System.out.println("getMin: " + s.getMin());
            }
        }
    ''', js=r'''
        class MinStack {
            constructor() {
                this.main = [];
                this.mins = [];              // mins[i] = min of main[0..i]
            }
            push(x) {
                this.main.push(x);
                this.mins.push(this.mins.length ? Math.min(x, this.mins[this.mins.length - 1]) : x);
            }
            pop() {
                this.mins.pop();             // the two stacks always move together
                return this.main.pop();
            }
            top() { return this.main[this.main.length - 1]; }
            getMin() { return this.mins[this.mins.length - 1]; }
        }

        const s = new MinStack();
        s.push(20);
        s.push(10);
        console.log("getMin:", s.getMin());
        s.push(5);
        console.log("getMin:", s.getMin());
        console.log("pop:", s.pop());
        console.log("getMin:", s.getMin());
        console.log("pop:", s.pop());
        console.log("getMin:", s.getMin());
    ''')
    yield complexity("O(1) per operation", "O(n) extra for the mins stack")
    yield note("A common space saving: push onto `mins` only when `x <= mins.top`, and pop from `mins` only when the popped value equals `mins.top`. Worst case it is still `O(n)` extra (a decreasing sequence), but on typical data the auxiliary stack stays short. The `<=` matters — with `<`, popping one of two equal minimums would wrongly remove the record.")

    yield section("Design a stack with getMin() in O(1) extra space", "wand")
    yield io("push(20), push(10), getMin(), push(5), getMin(), pop(), getMin(), pop(), getMin()", "10 5 10 20", "push(-2), push(0), push(-3), getMin(), pop(), getMin()", "-3 -2")
    yield p("The auxiliary stack stores one number per element. Can we do it with a **single extra variable** `minEle`? Yes — by storing an *encoded* value instead of `x` whenever `x` becomes the new minimum. The encoded value remembers the *previous* minimum, so `pop()` can restore it.")
    yield idea("Invariant: `minEle` is the current minimum, and an element sits in the stack as its real value unless it was a new minimum when pushed — then it is stored as `2x − minEle_old`, which is **less than `x`** (because `x < minEle_old`) and hence less than the new `minEle = x`. So a stored value *below* `minEle` is a flag meaning *this element is the current minimum*; its real value is `minEle`, and the previous minimum is recovered as `2·minEle − stored`.")
    yield table(
        ["Operation", "Condition", "Do"],
        ["`push(x)`", "stack empty", "push `x`; `minEle = x`"],
        ["`push(x)`", "`x >= minEle`", "push `x` as is"],
        ["`push(x)`", "`x < minEle`", "push `2x − minEle` (encoded); `minEle = x`"],
        ["`pop()`", "`top >= minEle`", "return `top`"],
        ["`pop()`", "`top < minEle`", "the real value is `minEle`; restore `minEle = 2·minEle − top`; return the old `minEle`"],
        ["`top()`", "`top < minEle`", "return `minEle`, else the stored value"],
        ["`getMin()`", "—", "return `minEle`"],
    )
    yield diagram('''
        operation   stored stack     minEle   note
        push(20)    [20]             20
        push(10)    [20, 0]          10       10 < 20 → store 2·10 − 20 = 0
        push(5)     [20, 0, 0]       5        5 < 10  → store 2·5 − 10 = 0
        pop()       [20, 0]          10       top 0 < minEle 5 → real value 5; minEle = 2·5 − 0 = 10
        pop()       [20]             20       top 0 < minEle 10 → real value 10; minEle = 2·10 − 0 = 20
    ''', "The encoded entries (here both 0) are below minEle, which marks them as 'I am the minimum'")
    yield multi('''
        getMin: 10
        getMin: 5
        pop: 5
        getMin: 10
        pop: 10
        getMin: 20
        --- negatives ---
        getMin: -3
        pop: -3
        getMin: -2
        top: 0
    ''', py=r'''
        class MinStack:
            def __init__(self):
                self.st = []
                self.min_ele = None

            def push(self, x):
                if not self.st:
                    self.st.append(x)
                    self.min_ele = x
                elif x < self.min_ele:
                    self.st.append(2 * x - self.min_ele)   # encoded: always < x < new min
                    self.min_ele = x
                else:
                    self.st.append(x)

            def pop(self):
                top = self.st.pop()
                if top < self.min_ele:                     # encoded entry: it *was* the minimum
                    real = self.min_ele
                    self.min_ele = 2 * self.min_ele - top  # restore the previous minimum
                    return real
                return top

            def top(self):
                t = self.st[-1]
                return self.min_ele if t < self.min_ele else t

            def get_min(self):
                return self.min_ele

        s = MinStack()
        s.push(20)
        s.push(10)
        print("getMin:", s.get_min())
        s.push(5)
        print("getMin:", s.get_min())
        print("pop:", s.pop())
        print("getMin:", s.get_min())
        print("pop:", s.pop())
        print("getMin:", s.get_min())

        print("--- negatives ---")
        s = MinStack()
        for x in (-2, 0, -3):
            s.push(x)
        print("getMin:", s.get_min())
        print("pop:", s.pop())
        print("getMin:", s.get_min())
        print("top:", s.top())
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        using namespace std;

        class MinStack {
            stack<long long> st;         // long long: 2x - minEle can exceed the int range
            long long minEle = 0;
        public:
            void push(long long x) {
                if (st.empty()) {
                    st.push(x);
                    minEle = x;
                } else if (x < minEle) {
                    st.push(2 * x - minEle);    // encoded: always < x < new min
                    minEle = x;
                } else {
                    st.push(x);
                }
            }
            long long pop() {
                long long top = st.top();
                st.pop();
                if (top < minEle) {              // encoded entry: it *was* the minimum
                    long long real = minEle;
                    minEle = 2 * minEle - top;   // restore the previous minimum
                    return real;
                }
                return top;
            }
            long long top() const {
                long long t = st.top();
                return t < minEle ? minEle : t;
            }
            long long getMin() const { return minEle; }
        };

        int main() {
            MinStack s;
            s.push(20);
            s.push(10);
            cout << "getMin: " << s.getMin() << "\n";
            s.push(5);
            cout << "getMin: " << s.getMin() << "\n";
            cout << "pop: " << s.pop() << "\n";
            cout << "getMin: " << s.getMin() << "\n";
            cout << "pop: " << s.pop() << "\n";
            cout << "getMin: " << s.getMin() << "\n";

            cout << "--- negatives ---\n";
            MinStack t;
            for (long long x : {-2, 0, -3}) t.push(x);
            cout << "getMin: " << t.getMin() << "\n";
            cout << "pop: " << t.pop() << "\n";
            cout << "getMin: " << t.getMin() << "\n";
            cout << "top: " << t.top() << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class MinStack {
                Deque<Long> st = new ArrayDeque<>();   // long: 2x - minEle can exceed the int range
                long minEle;
                void push(long x) {
                    if (st.isEmpty()) {
                        st.push(x);
                        minEle = x;
                    } else if (x < minEle) {
                        st.push(2 * x - minEle);        // encoded: always < x < new min
                        minEle = x;
                    } else {
                        st.push(x);
                    }
                }
                long pop() {
                    long top = st.pop();
                    if (top < minEle) {                  // encoded entry: it *was* the minimum
                        long real = minEle;
                        minEle = 2 * minEle - top;       // restore the previous minimum
                        return real;
                    }
                    return top;
                }
                long top() {
                    long t = st.peek();
                    return t < minEle ? minEle : t;
                }
                long getMin() { return minEle; }
            }

            public static void main(String[] args) {
                MinStack s = new MinStack();
                s.push(20);
                s.push(10);
                System.out.println("getMin: " + s.getMin());
                s.push(5);
                System.out.println("getMin: " + s.getMin());
                System.out.println("pop: " + s.pop());
                System.out.println("getMin: " + s.getMin());
                System.out.println("pop: " + s.pop());
                System.out.println("getMin: " + s.getMin());

                System.out.println("--- negatives ---");
                MinStack t = new MinStack();
                for (long x : new long[]{-2, 0, -3}) t.push(x);
                System.out.println("getMin: " + t.getMin());
                System.out.println("pop: " + t.pop());
                System.out.println("getMin: " + t.getMin());
                System.out.println("top: " + t.top());
            }
        }
    ''', js=r'''
        class MinStack {
            constructor() {
                this.st = [];
                this.minEle = null;
            }
            push(x) {
                if (this.st.length === 0) {
                    this.st.push(x);
                    this.minEle = x;
                } else if (x < this.minEle) {
                    this.st.push(2 * x - this.minEle);   // encoded: always < x < new min
                    this.minEle = x;
                } else {
                    this.st.push(x);
                }
            }
            pop() {
                const top = this.st.pop();
                if (top < this.minEle) {                  // encoded entry: it *was* the minimum
                    const real = this.minEle;
                    this.minEle = 2 * this.minEle - top;  // restore the previous minimum
                    return real;
                }
                return top;
            }
            top() {
                const t = this.st[this.st.length - 1];
                return t < this.minEle ? this.minEle : t;
            }
            getMin() { return this.minEle; }
        }

        let s = new MinStack();
        s.push(20);
        s.push(10);
        console.log("getMin:", s.getMin());
        s.push(5);
        console.log("getMin:", s.getMin());
        console.log("pop:", s.pop());
        console.log("getMin:", s.getMin());
        console.log("pop:", s.pop());
        console.log("getMin:", s.getMin());

        console.log("--- negatives ---");
        s = new MinStack();
        for (const x of [-2, 0, -3]) s.push(x);
        console.log("getMin:", s.getMin());
        console.log("pop:", s.pop());
        console.log("getMin:", s.getMin());
        console.log("top:", s.top());
    ''')
    yield complexity("O(1) per operation", "O(1) extra — one variable besides the stack")
    yield p("**Why `2x − minEle` works.** Let `m` be the old minimum and `x < m` the new one. The stored value is `e = 2x − m = x − (m − x) < x`. Since the new `minEle` is `x`, the stored `e` is below `minEle`, which is how `pop()` recognises it. Reversing: `2·minEle − e = 2x − (2x − m) = m`, the old minimum. Negative numbers need no special handling — the algebra never relied on signs, only on `x < m`. The original notes repeated the same class under *Handling negatives*; the `-2, 0, -3` driver above shows it works unchanged.")
    yield pitfall("`2x − minEle` can **overflow** a 32-bit integer when `x` and `minEle` are near the limits with opposite signs. Use a 64-bit type for the stored values (`long long` / `long` above), or fall back to the auxiliary stack when inputs can be extreme. Also: `top()` must decode exactly like `pop()` — returning the raw stored value is a classic bug that only shows up when the top happens to be the minimum.")

    yield section("Interview Q&A", "message-question")
    yield qa("When should I reach for a monotonic stack?",
             "Whenever the question is about the *nearest* element to the left or right satisfying an order relation — greater, smaller, greater-or-equal — or about spans/widths bounded by such elements. Signals: 'next greater', 'previous smaller', 'how many days until a warmer temperature', 'largest rectangle', 'trapping rain water', 'remove k digits to make the smallest number'. The nested `while` looks quadratic but is amortised `O(n)` because each element is popped at most once.")
    yield qa("Previous greater vs next greater: what actually changes in the code?",
             "Only the scan direction. Scan left-to-right and the stack contains candidates from the left (previous greater); scan right-to-left and it contains candidates from the right (next greater). Changing `<=` to `>=` in the pop condition switches from *greater* to *smaller*. Four problems, one template.")
    yield qa("Why is the histogram problem O(n) when each bar may pop many others?",
             "Each index is pushed once and popped once (at most), so the total number of pops across the whole run is at most `n`. The sentinel `0` bar at the end guarantees that every index is eventually popped and measured, so no separate clean-up loop with its own off-by-one risks is needed.")
    yield qa("How does the k-stacks structure differ from just using k dynamic arrays?",
             "`k` separate arrays either reserve capacity per stack (wasted when stacks are unbalanced) or resize independently. The single-array version guarantees that *any* distribution of up to `n` elements across the `k` stacks fits, with `O(1)` push/pop and `O(n + k)` total memory, by maintaining a free list inside the array — the same idea an allocator uses for free blocks.")
    yield qa("Is the O(1)-space getMin() trick safe in production code?",
             "It is correct for any integers as long as `2x − minEle` does not overflow, so store 64-bit values or check the range. It also only works for one tracked statistic (min *or* max) and makes `top()` subtle. Many engineers prefer the auxiliary-stack version for its clarity; know both and say why you would choose one.")
    yield qa("How would you find the next greater element for a circular array?",
             "Run the right-to-left scan twice over the array (`i` from `2n − 1` down to `0`, using `arr[i % n]`), filling results only during the second half. The first pass seeds the stack with every element so wrap-around candidates are available when the real scan starts. Still `O(n)`.")


@topic(G, "infix_postfix", "Infix, Postfix, Prefix", "math-symbols")
def _():
    yield lead("Humans write `x + y`; machines prefer `x y +` or `+ x y`, because those forms need no brackets, no precedence table and no associativity rules — a single left-to-right pass with a stack evaluates them. Converting between the three notations is the classic stack algorithm.")
    yield define("Infix / Postfix / Prefix", "the three ways to place an operator relative to its operands: **infix** between them (`x + y`), **postfix** after them (`x y +`, also called *Reverse Polish Notation*), **prefix** before them (`+ x y`, *Polish Notation*).")
    yield table(
        ["Infix", "Postfix", "Prefix"],
        ["`x + y`", "`x y +`", "`+ x y`"],
        ["`x + y * z`", "`x y z * +`", "`+ x * y z`"],
        ["`(x + y) * z`", "`x y + z *`", "`* + x y z`"],
        ["`a + b * (c - d) / e`", "`a b c d - * e / +`", "`+ a / * b - c d e`"],
        ["`a ^ b ^ c`  (right-assoc)", "`a b c ^ ^`", "`^ a ^ b c`"],
    )

    yield section("Why postfix and prefix are useful", "bulb")
    yield cards(
        ("No parentheses", "The position of each operator already says which operands it applies to, so brackets are never needed. `(x + y) * z` is just `x y + z *`.", "brackets-off"),
        ("No precedence or associativity rules", "Those rules only exist to disambiguate infix. Once an expression is in postfix or prefix, `*` before `+` is decided by position, not by a table.", "list-check"),
        ("One pass to evaluate", "A single left-to-right scan with one stack evaluates postfix (right-to-left for prefix). Compilers and calculators (HP's RPN models, the JVM's stack machine, PostScript) run on exactly this.", "bolt"),
        ("Same tree, three traversals", "All three notations are traversals of the same *expression tree*: prefix = preorder, infix = inorder, postfix = postorder. Converting is just re-traversing.", "binary-tree"),
    )
    yield diagram('''
                 +                    preorder  (prefix)  : + a * b c
               /   \\                  inorder   (infix)   : a + b * c
              a     *                 postorder (postfix) : a b c * +
                   / \\
                  b   c
    ''', "The expression tree of a + b * c and its three traversals")

    yield section("Precedence and associativity", "arrows-sort")
    yield p("Infix is ambiguous without two extra rules. **Precedence** decides which operator binds tighter when they differ; **associativity** decides the order when they are equal.")
    yield table(
        ["Operator", "Precedence", "Associativity", "Example"],
        ["`^`", "3 (highest)", "right to left", "`2 ^ 1 ^ 2 = 2 ^ (1 ^ 2) = 2 ^ 1 = 2`"],
        ["`*`, `/`", "2", "left to right", "`12 / 2 * 3 = (12 / 2) * 3 = 18`"],
        ["`+`, `-`", "1 (lowest)", "left to right", "`10 + 2 - 3 = (10 + 2) - 3 = 9`"],
    )
    yield ul(
        "**Precedence:** `10 + 20 * 2` → `10 + 40` → `50`, not `60`.",
        "**Left associativity:** `10 - 2 - 3` → `(10 - 2) - 3` → `5`, not `11`.",
        "**Right associativity:** `2 ^ 3 ^ 2` → `2 ^ (3 ^ 2)` → `2 ^ 9` → `512`, not `64`.",
    )
    yield note("In the conversion algorithms, precedence decides whether an incoming operator pops the stack top; associativity decides what happens when they are **equal**: left-associative operators pop the equal top (so the earlier one is output first), right-associative ones do not.", "How the rules enter the algorithm")

    yield section("Converting by hand: fully parenthesise, then move operators", "pencil")
    yield steps(
        ("Parenthesise fully", "Add brackets that make precedence and associativity explicit: `x + y * z` → `(x + (y * z))`."),
        ("Convert innermost first", "Replace each `(a op b)` by `a b op` (postfix) or `op a b` (prefix), working outwards: `(x + (y z *))` → `x y z * +`."),
        ("Drop the brackets", "They are no longer needed — the result is the postfix (or prefix) form."),
    )
    yield table(
        ["Infix", "Fully parenthesised", "Postfix", "Prefix"],
        ["`x + y * z`", "`(x + (y * z))`", "`x y z * +`", "`+ x * y z`"],
        ["`(x + y) * z`", "`((x + y) * z)`", "`x y + z *`", "`* + x y z`"],
        ["`a - b - c`", "`((a - b) - c)`", "`a b - c -`", "`- - a b c`"],
        ["`a ^ b ^ c`", "`(a ^ (b ^ c))`", "`a b c ^ ^`", "`^ a ^ b c`"],
    )

    yield section("Infix to postfix (shunting-yard algorithm)", "arrows-right")
    yield io("a+b*c", "abc*+", "(a+b)*c", "ab+c*", "a+b*(c-d)/e", "abcd-*e/+")
    yield idea("Operands go straight to the output; they are already in the right order. Operators wait on a stack until every operator that must be applied *before* them has been output. An operator on the stack must come out before an incoming operator of lower (or equal, for left-associative) precedence — that is the only rule. Brackets are a fence: `(` is pushed and nothing below it can be popped until the matching `)` arrives.")
    yield steps(
        ("Operand", "Append it to the output."),
        ("`(`", "Push it."),
        ("`)`", "Pop and output operators until the `(`; pop the `(` and discard it (brackets never appear in postfix)."),
        ("Operator `x`", "While the stack top is an operator with **higher** precedence than `x`, or **equal** precedence and `x` is left-associative, pop it to the output. Then push `x`."),
        ("End of input", "Pop and output everything left on the stack."),
    )
    yield table(
        ["Symbol", "Action", "Stack (bottom → top)", "Output"],
        ["`a`", "operand → output", "", "`a`"],
        ["`+`", "stack empty → push", "`+`", "`a`"],
        ["`b`", "operand → output", "`+`", "`a b`"],
        ["`*`", "higher than `+` → push", "`+ *`", "`a b`"],
        ["`(`", "push", "`+ * (`", "`a b`"],
        ["`c`", "operand → output", "`+ * (`", "`a b c`"],
        ["`-`", "top is `(` → push", "`+ * ( -`", "`a b c`"],
        ["`d`", "operand → output", "`+ * ( -`", "`a b c d`"],
        ["`)`", "pop to `(`: output `-`, discard `(`", "`+ *`", "`a b c d -`"],
        ["`/`", "equal to `*`, left-assoc → pop `*`; `+` is lower → stop; push `/`", "`+ /`", "`a b c d - *`"],
        ["`e`", "operand → output", "`+ /`", "`a b c d - * e`"],
        ["end", "pop everything", "", "`a b c d - * e / +`"],
    )
    yield multi('''
        a+b*c → abc*+
        (a+b)*c → ab+c*
        a+b*(c-d)/e → abcd-*e/+
        a^b^c → abc^^
        a-b-c → ab-c-
    ''', py=r'''
        PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        RIGHT_ASSOC = {'^'}

        def infix_to_postfix(expr):
            out, st = [], []
            for ch in expr:
                if ch == ' ':
                    continue
                if ch.isalnum():                       # operand: straight to the output
                    out.append(ch)
                elif ch == '(':
                    st.append(ch)
                elif ch == ')':
                    while st[-1] != '(':               # pop until the matching '('
                        out.append(st.pop())
                    st.pop()                           # discard the '(' itself
                else:                                  # operator
                    while (st and st[-1] != '(' and
                           (PREC[st[-1]] > PREC[ch] or
                            (PREC[st[-1]] == PREC[ch] and ch not in RIGHT_ASSOC))):
                        out.append(st.pop())           # higher (or equal, left-assoc) comes out first
                    st.append(ch)
            while st:
                out.append(st.pop())
            return ''.join(out)

        for e in ["a+b*c", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"]:
            print(e, "→", infix_to_postfix(e))
    ''', cpp=r'''
        #include <cctype>
        #include <iostream>
        #include <stack>
        #include <string>
        using namespace std;

        int prec(char op) {
            if (op == '^') return 3;
            if (op == '*' || op == '/') return 2;
            if (op == '+' || op == '-') return 1;
            return 0;
        }
        bool rightAssoc(char op) { return op == '^'; }

        string infixToPostfix(const string& expr) {
            string out;
            stack<char> st;
            for (char ch : expr) {
                if (ch == ' ') continue;
                if (isalnum(static_cast<unsigned char>(ch))) {
                    out += ch;                                   // operand: straight to the output
                } else if (ch == '(') {
                    st.push(ch);
                } else if (ch == ')') {
                    while (st.top() != '(') { out += st.top(); st.pop(); }   // pop until the matching '('
                    st.pop();                                    // discard the '(' itself
                } else {
                    while (!st.empty() && st.top() != '(' &&
                           (prec(st.top()) > prec(ch) || (prec(st.top()) == prec(ch) && !rightAssoc(ch)))) {
                        out += st.top(); st.pop();               // higher (or equal, left-assoc) comes out first
                    }
                    st.push(ch);
                }
            }
            while (!st.empty()) { out += st.top(); st.pop(); }
            return out;
        }

        int main() {
            for (string e : {"a+b*c", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"})
                cout << e << " → " << infixToPostfix(e) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int prec(char op) {
                if (op == '^') return 3;
                if (op == '*' || op == '/') return 2;
                if (op == '+' || op == '-') return 1;
                return 0;
            }
            static boolean rightAssoc(char op) { return op == '^'; }

            static String infixToPostfix(String expr) {
                StringBuilder out = new StringBuilder();
                Deque<Character> st = new ArrayDeque<>();
                for (char ch : expr.toCharArray()) {
                    if (ch == ' ') continue;
                    if (Character.isLetterOrDigit(ch)) {
                        out.append(ch);                              // operand: straight to the output
                    } else if (ch == '(') {
                        st.push(ch);
                    } else if (ch == ')') {
                        while (st.peek() != '(') out.append(st.pop());   // pop until the matching '('
                        st.pop();                                    // discard the '(' itself
                    } else {
                        while (!st.isEmpty() && st.peek() != '(' &&
                               (prec(st.peek()) > prec(ch) || (prec(st.peek()) == prec(ch) && !rightAssoc(ch))))
                            out.append(st.pop());                    // higher (or equal, left-assoc) comes out first
                        st.push(ch);
                    }
                }
                while (!st.isEmpty()) out.append(st.pop());
                return out.toString();
            }

            public static void main(String[] args) {
                for (String e : new String[]{"a+b*c", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"})
                    System.out.println(e + " → " + infixToPostfix(e));
            }
        }
    ''', js=r'''
        const PREC = { '+': 1, '-': 1, '*': 2, '/': 2, '^': 3 };
        const RIGHT_ASSOC = new Set(['^']);
        const isOperand = ch => /[A-Za-z0-9]/.test(ch);

        function infixToPostfix(expr) {
            const out = [], st = [];
            const top = () => st[st.length - 1];
            for (const ch of expr) {
                if (ch === ' ') continue;
                if (isOperand(ch)) {
                    out.push(ch);                                   // operand: straight to the output
                } else if (ch === '(') {
                    st.push(ch);
                } else if (ch === ')') {
                    while (top() !== '(') out.push(st.pop());       // pop until the matching '('
                    st.pop();                                       // discard the '(' itself
                } else {
                    while (st.length && top() !== '(' &&
                           (PREC[top()] > PREC[ch] || (PREC[top()] === PREC[ch] && !RIGHT_ASSOC.has(ch))))
                        out.push(st.pop());                         // higher (or equal, left-assoc) comes out first
                    st.push(ch);
                }
            }
            while (st.length) out.push(st.pop());
            return out.join('');
        }

        for (const e of ["a+b*c", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"])
            console.log(e, "→", infixToPostfix(e));
    ''')
    yield complexity("O(n)", "O(n) for the operator stack")
    yield pitfall("Three places where this goes wrong: (1) comparing precedence with a `(` on top — give `(` the lowest precedence or test for it explicitly, otherwise `)` never finds its partner; (2) using `>` instead of `>=` for left-associative operators, which turns `a-b-c` into `abc--` = `a-(b-c)`; (3) the `)` case must *discard* the `(` — brackets never reach the output.")

    yield section("Evaluating a postfix expression", "calculator")
    yield io("10 2 * 3 +", "23", "2 3 1 * + 9 -", "-4", "100 20 5 / -", "96")
    yield idea("Scan left to right. Operands are pushed. When an operator arrives, its two operands are the two most recent values — pop them, apply, push the result. The expression is well formed exactly when one value remains at the end. **Order matters for `-`, `/` and `^`:** the first pop is the *right* operand.")
    yield steps(
        ("Operand", "Push it."),
        ("Operator", "`right = pop()`, `left = pop()`, push `left op right`."),
        ("End", "The single remaining value is the result."),
    )
    yield diagram('''
        tokens:  10   2   *   3   +
        stack:  [10] [10 2] [20] [20 3] [23]        2 3 1 * + 9 -  →  [2] [2 3] [2 3 1] [2 3] [5] [5 9] [-4]
    ''', "Each operator replaces the top two values by one")
    yield multi('''
        10 2 * 3 + = 23
        2 3 1 * + 9 - = -4
        100 20 5 / - = 96
        2 3 ^ 1 - = 7
    ''', py=r'''
        def apply(op, a, b):
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/': return a // b           # integer division (operands kept positive here)
            if op == '^': return a ** b
            raise ValueError(op)

        def eval_postfix(expr):
            st = []
            for tok in expr.split():
                if tok.lstrip('-').isdigit():
                    st.append(int(tok))
                else:
                    right = st.pop()              # first pop is the RIGHT operand
                    left = st.pop()
                    st.append(apply(tok, left, right))
            return st[-1]                         # exactly one value remains

        for e in ["10 2 * 3 +", "2 3 1 * + 9 -", "100 20 5 / -", "2 3 ^ 1 -"]:
            print(e, "=", eval_postfix(e))
    ''', cpp=r'''
        #include <iostream>
        #include <sstream>
        #include <stack>
        #include <string>
        using namespace std;

        long long ipow(long long a, long long b) { long long r = 1; while (b-- > 0) r *= a; return r; }

        long long apply(const string& op, long long a, long long b) {
            if (op == "+") return a + b;
            if (op == "-") return a - b;
            if (op == "*") return a * b;
            if (op == "/") return a / b;         // integer division (operands kept positive here)
            return ipow(a, b);                   // "^"
        }

        long long evalPostfix(const string& expr) {
            stack<long long> st;
            istringstream in(expr);
            string tok;
            while (in >> tok) {
                if (isdigit(static_cast<unsigned char>(tok.back()))) {
                    st.push(stoll(tok));
                } else {
                    long long right = st.top(); st.pop();   // first pop is the RIGHT operand
                    long long left = st.top(); st.pop();
                    st.push(apply(tok, left, right));
                }
            }
            return st.top();                                // exactly one value remains
        }

        int main() {
            for (string e : {"10 2 * 3 +", "2 3 1 * + 9 -", "100 20 5 / -", "2 3 ^ 1 -"})
                cout << e << " = " << evalPostfix(e) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static long ipow(long a, long b) { long r = 1; while (b-- > 0) r *= a; return r; }

            static long apply(String op, long a, long b) {
                switch (op) {
                    case "+": return a + b;
                    case "-": return a - b;
                    case "*": return a * b;
                    case "/": return a / b;          // integer division (operands kept positive here)
                    default:  return ipow(a, b);     // "^"
                }
            }

            static long evalPostfix(String expr) {
                Deque<Long> st = new ArrayDeque<>();
                for (String tok : expr.split(" ")) {
                    if (Character.isDigit(tok.charAt(tok.length() - 1))) {
                        st.push(Long.parseLong(tok));
                    } else {
                        long right = st.pop();           // first pop is the RIGHT operand
                        long left = st.pop();
                        st.push(apply(tok, left, right));
                    }
                }
                return st.peek();                        // exactly one value remains
            }

            public static void main(String[] args) {
                for (String e : new String[]{"10 2 * 3 +", "2 3 1 * + 9 -", "100 20 5 / -", "2 3 ^ 1 -"})
                    System.out.println(e + " = " + evalPostfix(e));
            }
        }
    ''', js=r'''
        function apply(op, a, b) {
            switch (op) {
                case '+': return a + b;
                case '-': return a - b;
                case '*': return a * b;
                case '/': return Math.trunc(a / b);     // integer division (operands kept positive here)
                case '^': return a ** b;
            }
            throw new Error(op);
        }

        function evalPostfix(expr) {
            const st = [];
            for (const tok of expr.split(' ')) {
                if (/\d$/.test(tok)) {
                    st.push(Number(tok));
                } else {
                    const right = st.pop();              // first pop is the RIGHT operand
                    const left = st.pop();
                    st.push(apply(tok, left, right));
                }
            }
            return st[st.length - 1];                    // exactly one value remains
        }

        for (const e of ["10 2 * 3 +", "2 3 1 * + 9 -", "100 20 5 / -", "2 3 ^ 1 -"])
            console.log(e, "=", evalPostfix(e));
    ''')
    yield complexity("O(n)", "O(n) for the operand stack")
    yield pitfall("`op1 = pop(); op2 = pop(); push(op2 op op1)` — the original notes wrote it correctly, but swapping the two is the single most common bug: `10 2 -` must give `8`, not `-8`. Also tokenise on spaces when operands can have several digits; a character-by-character scan silently reads `10` as `1` and `0`.")

    yield section("Infix to prefix", "arrows-left")
    yield io("x+y*z", "+x*yz", "(a+b)*c", "*+abc", "a+b*(c-d)/e", "+a/*b-cde")
    yield p("By hand: fully parenthesise and convert from the innermost bracket outwards, writing each operator *before* its operands — `x + (y * z)` → `x + (* y z)` → `+ x * y z`. With a stack there are two routes; the reversal trick reuses the postfix code almost unchanged.")
    yield idea("Prefix is almost *postfix read backwards*: reverse the infix string (swapping `(` with `)`), run the postfix algorithm, and reverse the result. The one subtlety is associativity, which flips with the reversal: in the reversed string a left-associative operator must **not** pop an equal-precedence top (otherwise `a-b-c` would come out as `-a-bc` = `a-(b-c)`), while the right-associative `^` must.")
    yield steps(
        ("Reverse", "Reverse the infix string and swap every `(` with `)`: `(a+b)*c` → `c*(b+a)`."),
        ("Convert", "Run infix-to-postfix on it, popping on **strictly higher** precedence (or equal precedence when the operator is right-associative): `c*(b+a)` → `cba+*`."),
        ("Reverse again", "Reverse the output: `cba+*` → `*+abc`."),
    )
    yield multi('''
        x+y*z → +x*yz
        (a+b)*c → *+abc
        a+b*(c-d)/e → +a/*b-cde
        a^b^c → ^a^bc
        a-b-c → --abc
    ''', py=r'''
        PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        RIGHT_ASSOC = {'^'}

        def infix_to_prefix(expr):
            rev = ''.join(')' if c == '(' else '(' if c == ')' else c for c in reversed(expr))
            out, st = [], []
            for ch in rev:
                if ch == ' ':
                    continue
                if ch.isalnum():
                    out.append(ch)
                elif ch == '(':
                    st.append(ch)
                elif ch == ')':
                    while st[-1] != '(':
                        out.append(st.pop())
                    st.pop()
                else:
                    while (st and st[-1] != '(' and
                           (PREC[st[-1]] > PREC[ch] or
                            (PREC[st[-1]] == PREC[ch] and ch in RIGHT_ASSOC))):   # associativity flipped
                        out.append(st.pop())
                    st.append(ch)
            while st:
                out.append(st.pop())
            return ''.join(reversed(out))                                       # undo the reversal

        for e in ["x+y*z", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"]:
            print(e, "→", infix_to_prefix(e))
    ''', cpp=r'''
        #include <algorithm>
        #include <cctype>
        #include <iostream>
        #include <stack>
        #include <string>
        using namespace std;

        int prec(char op) {
            if (op == '^') return 3;
            if (op == '*' || op == '/') return 2;
            if (op == '+' || op == '-') return 1;
            return 0;
        }
        bool rightAssoc(char op) { return op == '^'; }

        string infixToPrefix(string expr) {
            reverse(expr.begin(), expr.end());
            for (char& c : expr) c = c == '(' ? ')' : c == ')' ? '(' : c;   // swap the brackets
            string out;
            stack<char> st;
            for (char ch : expr) {
                if (ch == ' ') continue;
                if (isalnum(static_cast<unsigned char>(ch))) {
                    out += ch;
                } else if (ch == '(') {
                    st.push(ch);
                } else if (ch == ')') {
                    while (st.top() != '(') { out += st.top(); st.pop(); }
                    st.pop();
                } else {
                    while (!st.empty() && st.top() != '(' &&
                           (prec(st.top()) > prec(ch) || (prec(st.top()) == prec(ch) && rightAssoc(ch)))) {
                        out += st.top(); st.pop();                        // associativity flipped
                    }
                    st.push(ch);
                }
            }
            while (!st.empty()) { out += st.top(); st.pop(); }
            reverse(out.begin(), out.end());                              // undo the reversal
            return out;
        }

        int main() {
            for (string e : {"x+y*z", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"})
                cout << e << " → " << infixToPrefix(e) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int prec(char op) {
                if (op == '^') return 3;
                if (op == '*' || op == '/') return 2;
                if (op == '+' || op == '-') return 1;
                return 0;
            }
            static boolean rightAssoc(char op) { return op == '^'; }

            static String infixToPrefix(String expr) {
                StringBuilder rev = new StringBuilder();
                for (int i = expr.length() - 1; i >= 0; i--) {              // reverse and swap the brackets
                    char c = expr.charAt(i);
                    rev.append(c == '(' ? ')' : c == ')' ? '(' : c);
                }
                StringBuilder out = new StringBuilder();
                Deque<Character> st = new ArrayDeque<>();
                for (char ch : rev.toString().toCharArray()) {
                    if (ch == ' ') continue;
                    if (Character.isLetterOrDigit(ch)) {
                        out.append(ch);
                    } else if (ch == '(') {
                        st.push(ch);
                    } else if (ch == ')') {
                        while (st.peek() != '(') out.append(st.pop());
                        st.pop();
                    } else {
                        while (!st.isEmpty() && st.peek() != '(' &&
                               (prec(st.peek()) > prec(ch) || (prec(st.peek()) == prec(ch) && rightAssoc(ch))))
                            out.append(st.pop());                        // associativity flipped
                        st.push(ch);
                    }
                }
                while (!st.isEmpty()) out.append(st.pop());
                return out.reverse().toString();                         // undo the reversal
            }

            public static void main(String[] args) {
                for (String e : new String[]{"x+y*z", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"})
                    System.out.println(e + " → " + infixToPrefix(e));
            }
        }
    ''', js=r'''
        const PREC = { '+': 1, '-': 1, '*': 2, '/': 2, '^': 3 };
        const RIGHT_ASSOC = new Set(['^']);
        const isOperand = ch => /[A-Za-z0-9]/.test(ch);

        function infixToPrefix(expr) {
            const rev = [...expr].reverse().map(c => c === '(' ? ')' : c === ')' ? '(' : c);   // swap the brackets
            const out = [], st = [];
            const top = () => st[st.length - 1];
            for (const ch of rev) {
                if (ch === ' ') continue;
                if (isOperand(ch)) {
                    out.push(ch);
                } else if (ch === '(') {
                    st.push(ch);
                } else if (ch === ')') {
                    while (top() !== '(') out.push(st.pop());
                    st.pop();
                } else {
                    while (st.length && top() !== '(' &&
                           (PREC[top()] > PREC[ch] || (PREC[top()] === PREC[ch] && RIGHT_ASSOC.has(ch))))
                        out.push(st.pop());                              // associativity flipped
                    st.push(ch);
                }
            }
            while (st.length) out.push(st.pop());
            return out.reverse().join('');                               // undo the reversal
        }

        for (const e of ["x+y*z", "(a+b)*c", "a+b*(c-d)/e", "a^b^c", "a-b-c"])
            console.log(e, "→", infixToPrefix(e));
    ''')
    yield complexity("O(n)", "O(n)")
    yield note("**Direct route without reversal:** scan the infix *right to left*, treating `)` as the opener and `(` as the closer, collect operands and popped operators into a list, and reverse that list at the end — this is exactly the step list in the original notes (push operands to `prefix`, push `)` to the stack, pop on `(`, compare precedence, finally reverse). The code above is the same algorithm with the reversal done up front, which lets it share its structure with the postfix converter.")

    yield section("Evaluating a prefix expression", "calculator")
    yield io("+ 10 * 2 3", "16", "- + 7 * 4 5 2", "25", "/ 100 - 20 15", "20")
    yield idea("Mirror the postfix evaluator: scan **right to left**. Operands are pushed; an operator pops two values, but now the first pop is the **left** operand (it was closer to the operator in the original text). Push the result; the last remaining value is the answer.")
    yield multi('''
        + 10 * 2 3 = 16
        - + 7 * 4 5 2 = 25
        / 100 - 20 15 = 20
    ''', py=r'''
        def apply(op, a, b):
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/': return a // b
            raise ValueError(op)

        def eval_prefix(expr):
            st = []
            for tok in reversed(expr.split()):      # right to left
                if tok.isdigit():
                    st.append(int(tok))
                else:
                    left = st.pop()                 # first pop is the LEFT operand this time
                    right = st.pop()
                    st.append(apply(tok, left, right))
            return st[-1]

        for e in ["+ 10 * 2 3", "- + 7 * 4 5 2", "/ 100 - 20 15"]:
            print(e, "=", eval_prefix(e))
    ''', cpp=r'''
        #include <cctype>
        #include <iostream>
        #include <sstream>
        #include <stack>
        #include <string>
        #include <vector>
        using namespace std;

        long long apply(const string& op, long long a, long long b) {
            if (op == "+") return a + b;
            if (op == "-") return a - b;
            if (op == "*") return a * b;
            return a / b;
        }

        long long evalPrefix(const string& expr) {
            vector<string> toks;
            istringstream in(expr);
            for (string t; in >> t;) toks.push_back(t);
            stack<long long> st;
            for (int i = (int)toks.size() - 1; i >= 0; i--) {         // right to left
                if (isdigit(static_cast<unsigned char>(toks[i].back()))) {
                    st.push(stoll(toks[i]));
                } else {
                    long long left = st.top(); st.pop();              // first pop is the LEFT operand this time
                    long long right = st.top(); st.pop();
                    st.push(apply(toks[i], left, right));
                }
            }
            return st.top();
        }

        int main() {
            for (string e : {"+ 10 * 2 3", "- + 7 * 4 5 2", "/ 100 - 20 15"})
                cout << e << " = " << evalPrefix(e) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static long apply(String op, long a, long b) {
                switch (op) {
                    case "+": return a + b;
                    case "-": return a - b;
                    case "*": return a * b;
                    default:  return a / b;
                }
            }

            static long evalPrefix(String expr) {
                String[] toks = expr.split(" ");
                Deque<Long> st = new ArrayDeque<>();
                for (int i = toks.length - 1; i >= 0; i--) {              // right to left
                    if (Character.isDigit(toks[i].charAt(toks[i].length() - 1))) {
                        st.push(Long.parseLong(toks[i]));
                    } else {
                        long left = st.pop();                             // first pop is the LEFT operand this time
                        long right = st.pop();
                        st.push(apply(toks[i], left, right));
                    }
                }
                return st.peek();
            }

            public static void main(String[] args) {
                for (String e : new String[]{"+ 10 * 2 3", "- + 7 * 4 5 2", "/ 100 - 20 15"})
                    System.out.println(e + " = " + evalPrefix(e));
            }
        }
    ''', js=r'''
        function apply(op, a, b) {
            switch (op) {
                case '+': return a + b;
                case '-': return a - b;
                case '*': return a * b;
                case '/': return Math.trunc(a / b);
            }
            throw new Error(op);
        }

        function evalPrefix(expr) {
            const toks = expr.split(' ');
            const st = [];
            for (let i = toks.length - 1; i >= 0; i--) {                  // right to left
                if (/\d$/.test(toks[i])) {
                    st.push(Number(toks[i]));
                } else {
                    const left = st.pop();                                // first pop is the LEFT operand this time
                    const right = st.pop();
                    st.push(apply(toks[i], left, right));
                }
            }
            return st[st.length - 1];
        }

        for (const e of ["+ 10 * 2 3", "- + 7 * 4 5 2", "/ 100 - 20 15"])
            console.log(e, "=", evalPrefix(e));
    ''')
    yield complexity("O(n)", "O(n)")

    yield section("The three notations side by side", "table")
    yield table(
        ["", "Infix", "Postfix", "Prefix"],
        ["Operator position", "between operands", "after operands", "before operands"],
        ["Needs brackets / precedence", "yes", "no", "no"],
        ["Evaluation scan", "needs two stacks or a parser", "left → right, one stack", "right → left, one stack"],
        ["First pop on an operator is", "—", "the **right** operand", "the **left** operand"],
        ["Tree traversal", "inorder", "postorder", "preorder"],
        ["Used by", "people, source code", "JVM / CPython bytecode, PostScript, RPN calculators", "Lisp, some compilers' IRs"],
    )

    yield section("Interview Q&A", "message-question")
    yield qa("Why do compilers and virtual machines prefer postfix?",
             "Because it maps directly onto a stack machine: each operand becomes a *push*, each operator a *pop-pop-compute-push*. No lookahead, no precedence table, one pass. The parser deals with precedence once, when it converts the source expression; the runtime never sees it again.")
    yield qa("How does the shunting-yard algorithm handle associativity?",
             "Only in the equal-precedence case. For a left-associative incoming operator, an equal-precedence top is popped first (so `a - b - c` → `a b - c -`); for a right-associative one (`^`) it stays, so the later operator is output first (`a ^ b ^ c` → `a b c ^ ^`).")
    yield qa("Can you evaluate an infix expression directly, without converting first?",
             "Yes — Dijkstra's two-stack algorithm: one stack for values and one for operators. It is the shunting-yard algorithm where, instead of *outputting* a popped operator, you immediately apply it to the top two values. The conversion and the evaluation are the same control flow with a different action.")
    yield qa("What is wrong with evaluating postfix character by character?",
             "Multi-digit numbers break: `10 2 *` would be read as `1`, `0`, `2`. Tokenise on spaces (or scan runs of digits) first. The same goes for identifiers longer than one character and for a unary minus, which needs its own token type.")
    yield qa("How are the three notations related to the expression tree?",
             "They are its three depth-first traversals: preorder prints the operator first (prefix), inorder prints it between the subtrees (infix, which is why it needs brackets to recover the structure), postorder prints it last (postfix). Both prefix and postfix determine the tree uniquely; infix without brackets does not.")


@topic(G, "queue_deque", "Queue & Deque", "arrows-horizontal")
def _():
    yield lead("A queue is **First In, First Out**; a deque (*double-ended queue*) lets you insert and remove at **both** ends in `O(1)`. The advanced problems here use the queue for breadth-first generation and the deque as a *sliding window* that keeps only the candidates that can still matter.")
    yield define("Deque", "a linear container with `O(1)` `pushFront`, `pushBack`, `popFront`, `popBack`, `front` and `back`. Restricting it to `pushBack` + `popFront` gives a queue; `pushBack` + `popBack` gives a stack — one structure covers both.")
    yield diagram('''
        pushFront(x) ──▶ ┌────┬────┬────┬────┬────┐ ◀── pushBack(x)
        popFront()   ◀── │ 20 │ 10 │ 15 │ 30 │ 7  │ ──▶ popBack()
                         └────┴────┴────┴────┴────┘
                          front                back
    ''', "A deque: both ends are open")

    yield section("Operations and the built-in containers", "box")
    yield table(
        ["Operation", "Python `collections.deque`", "C++ `std::deque`", "Java `ArrayDeque`", "JavaScript"],
        ["push back", "`append(x)`", "`push_back(x)`", "`addLast(x)` / `offer(x)`", "`arr.push(x)`"],
        ["push front", "`appendleft(x)`", "`push_front(x)`", "`addFirst(x)` / `push(x)`", "`arr.unshift(x)` — **O(n)**"],
        ["pop front", "`popleft()`", "`pop_front()` (+ `front()`)", "`pollFirst()` / `poll()`", "`arr.shift()` — **O(n)**"],
        ["pop back", "`pop()`", "`pop_back()` (+ `back()`)", "`pollLast()`", "`arr.pop()`"],
        ["peek front / back", "`dq[0]` / `dq[-1]`", "`front()` / `back()`", "`peekFirst()` / `peekLast()`", "`arr[0]` / `arr[arr.length-1]`"],
    )
    yield warn("JavaScript has no built-in deque. `shift()` and `unshift()` move every element, so a queue built on them is `O(n)` per operation. For small inputs it does not matter (the first two problems below use it for brevity); for real workloads keep a **head index** into the array (`arr[head++]` to dequeue — see the sliding-window solution) or write a small ring-buffer / two-index `Deque` class (see the min/max structure).")
    yield p("Python's `deque`, C++'s `std::deque` and Java's `ArrayDeque` are all `O(1)` at both ends. `std::queue` and `std::stack` are thin adapters over `std::deque`; Java's `Queue` and `Deque` interfaces are both implemented by `ArrayDeque` (prefer it over `LinkedList`, which allocates a node per element).")

    yield section("Reverse a queue", "arrows-left-right")
    yield io("q = [20, 10, 15, 30]  (20 at the front)", "30 15 10 20")
    yield idea("A stack reverses order. Dequeue everything into a stack, then pop everything back into the queue: the last element out of the queue is the first one pushed back. Only queue operations (`enqueue`, `dequeue`) and a stack are used — the queue is treated as a black box.")
    yield multi("30 15 10 20", py=r'''
        from collections import deque

        def reverse_queue(q):
            st = []
            while q:
                st.append(q.popleft())     # drain the queue into a stack
            while st:
                q.append(st.pop())         # refill: last out of the queue goes in first

        q = deque([20, 10, 15, 30])
        reverse_queue(q)
        print(*q)
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <stack>
        using namespace std;

        void reverseQueue(queue<int>& q) {
            stack<int> st;
            while (!q.empty()) { st.push(q.front()); q.pop(); }   // drain the queue into a stack
            while (!st.empty()) { q.push(st.top()); st.pop(); }   // refill: last out goes in first
        }

        int main() {
            queue<int> q;
            for (int x : {20, 10, 15, 30}) q.push(x);
            reverseQueue(q);
            while (!q.empty()) { cout << q.front() << " "; q.pop(); }
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;
        import java.util.Queue;

        public class Main {
            static void reverseQueue(Queue<Integer> q) {
                Deque<Integer> st = new ArrayDeque<>();
                while (!q.isEmpty()) st.push(q.poll());   // drain the queue into a stack
                while (!st.isEmpty()) q.add(st.pop());    // refill: last out goes in first
            }

            public static void main(String[] args) {
                Queue<Integer> q = new ArrayDeque<>();
                for (int x : new int[]{20, 10, 15, 30}) q.add(x);
                reverseQueue(q);
                StringBuilder sb = new StringBuilder();
                while (!q.isEmpty()) sb.append(q.poll()).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js=r'''
        function reverseQueue(q) {
            const st = [];
            while (q.length) st.push(q.shift());     // drain the queue into a stack (shift is O(n) in JS)
            while (st.length) q.push(st.pop());      // refill: last out goes in first
        }

        const q = [20, 10, 15, 30];
        reverseQueue(q);
        console.log(q.join(" "));
    ''')
    yield complexity("O(n)", "O(n) for the stack")
    yield p("**Recursive version.** The call stack *is* the stack: dequeue the front, reverse the rest recursively, then enqueue the front at the back. The deepest call enqueues the last element first.")
    yield multi("30 15 10 20", py=r'''
        from collections import deque

        def reverse_queue(q):
            if not q:
                return
            front = q.popleft()      # take the front out …
            reverse_queue(q)         # … reverse the remaining n-1 …
            q.append(front)          # … and put the old front at the back

        q = deque([20, 10, 15, 30])
        reverse_queue(q)
        print(*q)
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        using namespace std;

        void reverseQueue(queue<int>& q) {
            if (q.empty()) return;
            int front = q.front(); q.pop();   // take the front out …
            reverseQueue(q);                  // … reverse the remaining n-1 …
            q.push(front);                    // … and put the old front at the back
        }

        int main() {
            queue<int> q;
            for (int x : {20, 10, 15, 30}) q.push(x);
            reverseQueue(q);
            while (!q.empty()) { cout << q.front() << " "; q.pop(); }
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {
            static void reverseQueue(Queue<Integer> q) {
                if (q.isEmpty()) return;
                int front = q.poll();   // take the front out …
                reverseQueue(q);        // … reverse the remaining n-1 …
                q.add(front);           // … and put the old front at the back
            }

            public static void main(String[] args) {
                Queue<Integer> q = new ArrayDeque<>();
                for (int x : new int[]{20, 10, 15, 30}) q.add(x);
                reverseQueue(q);
                StringBuilder sb = new StringBuilder();
                while (!q.isEmpty()) sb.append(q.poll()).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js=r'''
        function reverseQueue(q) {
            if (q.length === 0) return;
            const front = q.shift();   // take the front out …
            reverseQueue(q);           // … reverse the remaining n-1 …
            q.push(front);             // … and put the old front at the back
        }

        const q = [20, 10, 15, 30];
        reverseQueue(q);
        console.log(q.join(" "));
    ''')
    yield complexity("O(n)", "O(n) call stack")
    yield pitfall("The recursive version uses `n` stack frames — Python's default limit is about 1000, so it is a teaching tool, not a production routine. The iterative version has the same complexity without the depth limit.")

    yield section("Generate the first n numbers with given digits", "list-numbers")
    yield io("n = 10, digits = [5, 6]", "5 6 55 56 65 66 555 556 565 566", "n = 7, digits = [1, 2, 3]", "1 2 3 11 12 13 21")
    yield p("Print, in increasing order, the first `n` positive integers whose decimal digits all come from the given set.")
    yield snippet("py", r'''
        def only_digits(num, digits):
            while num > 0:
                if num % 10 not in digits:
                    return False
                num //= 10
            return True

        def first_n_naive(n, digits):
            res, num = [], 1
            while len(res) < n:                 # try 1, 2, 3, … and keep the ones that qualify
                if only_digits(num, digits):
                    res.append(num)
                num += 1
            return res

        print(*first_n_naive(10, [5, 6]))
    ''', out="5 6 55 56 65 66 555 556 565 566", caption="Naive — test every natural number; with digits {5, 6} only 2^k of the k-digit numbers qualify, so this gets slow fast")
    yield idea("The valid numbers form a **tree**: the children of `x` are `x` with each allowed digit appended. A breadth-first traversal of that tree visits the numbers *in increasing order* — all 1-digit numbers, then all 2-digit numbers (smaller prefixes first), and so on. BFS is a queue: start with the single digits, repeatedly dequeue a number, print it, and enqueue its children. Each dequeue produces exactly one answer, so the loop runs `n` times.")
    yield diagram('''
                       (root)
                    /          \\
                   5            6                 ← dequeued 1st, 2nd
                 /   \\        /   \\
               55     56    65     66             ← 3rd … 6th
              /  \\   /  \\
            555 556 565 566 …                     ← 7th … 10th
    ''', "BFS order of the digit tree is numeric order, because every level is one digit longer and siblings are enqueued smallest-first")
    yield multi('''
        5 6 55 56 65 66 555 556 565 566
        1 2 3 11 12 13 21
    ''', py=r'''
        from collections import deque

        def first_n(n, digits):
            q = deque(str(d) for d in sorted(digits))   # level 1: the single digits, smallest first
            res = []
            while len(res) < n:
                cur = q.popleft()
                res.append(cur)
                for d in sorted(digits):
                    q.append(cur + str(d))              # children: one digit longer
            return res

        print(*first_n(10, [5, 6]))
        print(*first_n(7, [1, 2, 3]))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <queue>
        #include <string>
        #include <vector>
        using namespace std;

        vector<string> firstN(int n, vector<int> digits) {
            sort(digits.begin(), digits.end());
            queue<string> q;
            for (int d : digits) q.push(to_string(d));     // level 1: the single digits, smallest first
            vector<string> res;
            while ((int)res.size() < n) {
                string cur = q.front(); q.pop();
                res.push_back(cur);
                for (int d : digits) q.push(cur + to_string(d));   // children: one digit longer
            }
            return res;
        }

        int main() {
            for (const string& s : firstN(10, {5, 6})) cout << s << " ";
            cout << "\n";
            for (const string& s : firstN(7, {1, 2, 3})) cout << s << " ";
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.ArrayList;
        import java.util.Arrays;
        import java.util.List;
        import java.util.Queue;

        public class Main {
            static List<String> firstN(int n, int[] digits) {
                Arrays.sort(digits);
                Queue<String> q = new ArrayDeque<>();
                for (int d : digits) q.add(String.valueOf(d));   // level 1: the single digits, smallest first
                List<String> res = new ArrayList<>();
                while (res.size() < n) {
                    String cur = q.poll();
                    res.add(cur);
                    for (int d : digits) q.add(cur + d);          // children: one digit longer
                }
                return res;
            }

            public static void main(String[] args) {
                System.out.println(String.join(" ", firstN(10, new int[]{5, 6})));
                System.out.println(String.join(" ", firstN(7, new int[]{1, 2, 3})));
            }
        }
    ''', js=r'''
        function firstN(n, digits) {
            digits = [...digits].sort((a, b) => a - b);
            const q = digits.map(String);                  // level 1: the single digits, smallest first
            const res = [];
            while (res.length < n) {
                const cur = q.shift();
                res.push(cur);
                for (const d of digits) q.push(cur + d);   // children: one digit longer
            }
            return res;
        }

        console.log(firstN(10, [5, 6]).join(" "));
        console.log(firstN(7, [1, 2, 3]).join(" "));
    ''')
    yield complexity("O(n × k) for k allowed digits", "O(n × k) queue")
    yield note("Work with **strings**, not integers: appending a digit is string concatenation, and the numbers quickly exceed 64 bits (the 20th number with digits {5, 6} already has 5 digits; the 10 000th has 13). The original notes hard-coded `'5'` and `'6'`; the version above takes any digit set and sorts it so BFS order is numeric order.")

    yield section("Data structure with min/max operations", "arrows-vertical")
    yield p("Design a structure supporting all of the following in `O(1)`: `insertMin(x)`, `insertMax(x)`, `getMin()`, `getMax()`, `extractMin()`, `extractMax()`.")
    yield io("insertMin(5), insertMax(10), insertMin(3), insertMax(12); getMin, getMax, extractMin, getMin, extractMax, getMax", "3 12 3 5 12 10")
    yield idea("`insertMin(x)` is only ever called with a value that **is** the new minimum, and `insertMax(x)` only with the new maximum — that contract is what makes `O(1)` possible (a general priority queue needs `O(log n)`). So keep the elements **sorted in a deque**: the minimum lives at the front, the maximum at the back. `insertMin` = `pushFront`, `insertMax` = `pushBack`, `getMin`/`getMax` = `front`/`back`, `extractMin`/`extractMax` = `popFront`/`popBack`. Every operation is one deque operation.")
    yield diagram('''
        insertMin(5)      [5]
        insertMax(10)     [5, 10]
        insertMin(3)      [3, 5, 10]          ← front is always the min
        insertMax(12)     [3, 5, 10, 12]      ← back is always the max
        extractMin() → 3  [5, 10, 12]
        extractMax() → 12 [5, 10]
    ''', "The deque stays sorted because insertMin/insertMax only ever add at the correct end")
    yield multi('''
        getMin: 3
        getMax: 12
        extractMin: 3
        getMin: 5
        extractMax: 12
        getMax: 10
    ''', py=r'''
        from collections import deque

        class MinMaxStructure:
            def __init__(self):
                self.dq = deque()            # kept sorted: front = min, back = max

            def insert_min(self, x):         # contract: x <= current min
                self.dq.appendleft(x)

            def insert_max(self, x):         # contract: x >= current max
                self.dq.append(x)

            def get_min(self):
                return self.dq[0]

            def get_max(self):
                return self.dq[-1]

            def extract_min(self):
                return self.dq.popleft()

            def extract_max(self):
                return self.dq.pop()

        s = MinMaxStructure()
        s.insert_min(5)
        s.insert_max(10)
        s.insert_min(3)
        s.insert_max(12)
        print("getMin:", s.get_min())
        print("getMax:", s.get_max())
        print("extractMin:", s.extract_min())
        print("getMin:", s.get_min())
        print("extractMax:", s.extract_max())
        print("getMax:", s.get_max())
    ''', cpp=r'''
        #include <deque>
        #include <iostream>
        using namespace std;

        class MinMaxStructure {
            deque<int> dq;                   // kept sorted: front = min, back = max
        public:
            void insertMin(int x) { dq.push_front(x); }   // contract: x <= current min
            void insertMax(int x) { dq.push_back(x); }    // contract: x >= current max
            int getMin() const { return dq.front(); }
            int getMax() const { return dq.back(); }
            int extractMin() { int x = dq.front(); dq.pop_front(); return x; }
            int extractMax() { int x = dq.back(); dq.pop_back(); return x; }
        };

        int main() {
            MinMaxStructure s;
            s.insertMin(5);
            s.insertMax(10);
            s.insertMin(3);
            s.insertMax(12);
            cout << "getMin: " << s.getMin() << "\n";
            cout << "getMax: " << s.getMax() << "\n";
            cout << "extractMin: " << s.extractMin() << "\n";
            cout << "getMin: " << s.getMin() << "\n";
            cout << "extractMax: " << s.extractMax() << "\n";
            cout << "getMax: " << s.getMax() << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class MinMaxStructure {
                Deque<Integer> dq = new ArrayDeque<>();     // kept sorted: front = min, back = max
                void insertMin(int x) { dq.addFirst(x); }   // contract: x <= current min
                void insertMax(int x) { dq.addLast(x); }    // contract: x >= current max
                int getMin() { return dq.peekFirst(); }
                int getMax() { return dq.peekLast(); }
                int extractMin() { return dq.pollFirst(); }
                int extractMax() { return dq.pollLast(); }
            }

            public static void main(String[] args) {
                MinMaxStructure s = new MinMaxStructure();
                s.insertMin(5);
                s.insertMax(10);
                s.insertMin(3);
                s.insertMax(12);
                System.out.println("getMin: " + s.getMin());
                System.out.println("getMax: " + s.getMax());
                System.out.println("extractMin: " + s.extractMin());
                System.out.println("getMin: " + s.getMin());
                System.out.println("extractMax: " + s.extractMax());
                System.out.println("getMax: " + s.getMax());
            }
        }
    ''', js=r'''
        class Deque {                        // O(1) at both ends: indices grow outwards from 0
            constructor() { this.items = {}; this.head = 0; this.tail = 0; }   // tail = one past the last
            pushFront(x) { this.items[--this.head] = x; }
            pushBack(x) { this.items[this.tail++] = x; }
            popFront() { const x = this.items[this.head]; delete this.items[this.head++]; return x; }
            popBack() { const x = this.items[--this.tail]; delete this.items[this.tail]; return x; }
            front() { return this.items[this.head]; }
            back() { return this.items[this.tail - 1]; }
            get size() { return this.tail - this.head; }
        }

        class MinMaxStructure {
            constructor() { this.dq = new Deque(); }       // kept sorted: front = min, back = max
            insertMin(x) { this.dq.pushFront(x); }         // contract: x <= current min
            insertMax(x) { this.dq.pushBack(x); }          // contract: x >= current max
            getMin() { return this.dq.front(); }
            getMax() { return this.dq.back(); }
            extractMin() { return this.dq.popFront(); }
            extractMax() { return this.dq.popBack(); }
        }

        const s = new MinMaxStructure();
        s.insertMin(5);
        s.insertMax(10);
        s.insertMin(3);
        s.insertMax(12);
        console.log("getMin:", s.getMin());
        console.log("getMax:", s.getMax());
        console.log("extractMin:", s.extractMin());
        console.log("getMin:", s.getMin());
        console.log("extractMax:", s.extractMax());
        console.log("getMax:", s.getMax());
    ''')
    yield complexity("O(1) per operation", "O(n)")
    yield pitfall("State the contract out loud in an interview: this structure is correct **only if** `insertMin` is always given a value no larger than the current minimum and `insertMax` a value no smaller than the current maximum (the original notes called it a 'MinMaxStack' and did not say so). Insert `7` into `[3, 5, 10, 12]` through either method and the sorted order — and every later answer — is wrong. For arbitrary inserts you need a min-max heap or two heaps (`O(log n)`).")

    yield section("Maximums of all subarrays of size k (sliding window maximum)", "chart-bar")
    yield io("arr = [10, 8, 5, 12, 15, 7, 6], k = 3", "10 12 15 15 15")
    yield p("For every window of `k` consecutive elements, print its maximum. The windows here are `[10,8,5]`, `[8,5,12]`, `[5,12,15]`, `[12,15,7]`, `[15,7,6]`.")
    yield snippet("py", r'''
        def window_max_naive(arr, k):
            res = []
            for i in range(len(arr) - k + 1):
                res.append(max(arr[i:i + k]))    # rescan each window
            return res

        print(*window_max_naive([10, 8, 5, 12, 15, 7, 6], 3))
    ''', out="10 12 15 15 15", caption="Naive — O(n·k): recompute the maximum of every window")
    yield idea("Keep a deque of **indices** whose values are **decreasing** from front to back — the monotonic-stack idea from the Stack topic, with one extra operation. When `arr[i]` arrives, pop from the **back** every index whose value is `<= arr[i]` (they can never be a window maximum again: `arr[i]` is bigger and will outlive them). Push `i` at the back. Pop from the **front** the index that has slid out of the window (`front <= i − k`). The front is now the maximum of the current window. The deque is the set of elements that are still *useful* — each is the maximum of the suffix of the window that starts at it.")
    yield diagram('''
        arr = [10, 8, 5, 12, 15, 7, 6], k = 3        deque holds indices; shown as values

        i  arr[i]  pop back while <= arr[i]   push   drop front if out of window   deque (values)   window max
        0   10     –                          0      –                             [10]             (window not full)
        1    8     –                          1      –                             [10, 8]          (window not full)
        2    5     –                          2      –                             [10, 8, 5]       10
        3   12     5, 8, 10                   3      –                             [12]             12
        4   15     12                         4      –                             [15]             15
        5    7     –                          5      –                             [15, 7]          15
        6    6     –                          6      index 4 still inside          [15, 7, 6]       15
    ''', "Front of the deque = maximum of the current window; every index enters and leaves at most once")
    yield multi("10 12 15 15 15", py=r'''
        from collections import deque

        def window_max(arr, k):
            dq = deque()                 # indices; arr values decreasing front → back
            res = []
            for i in range(len(arr)):
                while dq and arr[dq[-1]] <= arr[i]:   # smaller-or-equal older elements are useless now
                    dq.pop()
                dq.append(i)
                if dq[0] <= i - k:                    # front has slid out of the window
                    dq.popleft()
                if i >= k - 1:                        # window is full: front is its maximum
                    res.append(arr[dq[0]])
            return res

        print(*window_max([10, 8, 5, 12, 15, 7, 6], 3))
    ''', cpp=r'''
        #include <deque>
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<int> windowMax(const vector<int>& arr, int k) {
            deque<int> dq;               // indices; arr values decreasing front → back
            vector<int> res;
            int n = arr.size();
            for (int i = 0; i < n; i++) {
                while (!dq.empty() && arr[dq.back()] <= arr[i]) dq.pop_back();   // useless now
                dq.push_back(i);
                if (dq.front() <= i - k) dq.pop_front();   // front has slid out of the window
                if (i >= k - 1) res.push_back(arr[dq.front()]);   // window is full: front is its max
            }
            return res;
        }

        int main() {
            for (int x : windowMax({10, 8, 5, 12, 15, 7, 6}, 3)) cout << x << " ";
            cout << "\n";
        }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static int[] windowMax(int[] arr, int k) {
                Deque<Integer> dq = new ArrayDeque<>();   // indices; arr values decreasing front → back
                int n = arr.length;
                int[] res = new int[n - k + 1];
                for (int i = 0; i < n; i++) {
                    while (!dq.isEmpty() && arr[dq.peekLast()] <= arr[i]) dq.pollLast();   // useless now
                    dq.addLast(i);
                    if (dq.peekFirst() <= i - k) dq.pollFirst();   // front has slid out of the window
                    if (i >= k - 1) res[i - k + 1] = arr[dq.peekFirst()];   // window full: front is its max
                }
                return res;
            }

            public static void main(String[] args) {
                StringBuilder sb = new StringBuilder();
                for (int x : windowMax(new int[]{10, 8, 5, 12, 15, 7, 6}, 3)) sb.append(x).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js=r'''
        function windowMax(arr, k) {
            const dq = [];               // indices; arr values decreasing front → back
            let head = 0;                // dq[head] is the front — no O(n) shift()
            const res = [];
            for (let i = 0; i < arr.length; i++) {
                while (dq.length > head && arr[dq[dq.length - 1]] <= arr[i]) dq.pop();   // useless now
                dq.push(i);
                if (dq[head] <= i - k) head++;                 // front has slid out of the window
                if (i >= k - 1) res.push(arr[dq[head]]);       // window is full: front is its maximum
            }
            return res;
        }

        console.log(windowMax([10, 8, 5, 12, 15, 7, 6], 3).join(" "));
    ''')
    yield complexity("O(n) — each index is pushed and popped at most once", "O(k) for the deque")
    yield pitfall("Store **indices**, not values — you need the index to know when the front has left the window. And pop from the back on `<=`, not `<`: an older *equal* element leaves the window earlier than the new one, so keeping it would only make the deque longer. The first `k − 1` iterations do not emit anything; the original notes handled that with a separate warm-up loop, the version above folds it into one loop with the `i >= k − 1` test.")
    yield note("The same deque gives the **sliding window minimum** by flipping the comparison to `>=`. It is also the engine behind `O(n)` solutions for *shortest subarray with sum at least k* and the monotonic-queue optimisation of some DP recurrences.", "Variants")

    yield section("First circular tour (petrol pumps)", "route")
    yield io("petrol = [4, 8, 7, 4], dist = [6, 5, 3, 5]  (pumps numbered from 1)", "2", "petrol = [1, 2, 3], dist = [3, 3, 3]", "-1")
    yield p("`n` petrol pumps sit on a circle. Pump `i` offers `petrol[i]` litres, and `dist[i]` litres are burned driving from pump `i` to pump `i + 1`. Starting with an empty tank, find the first pump from which a truck can complete the full circle, or report that none exists. Here the net gain at each pump is `-2, 3, 4, -1`; starting at pump 2 the tank reads `3 → 7 → 6 → 4`, never negative.")
    yield snippet("py", r'''
        def first_tour_naive(petrol, dist):
            n = len(petrol)
            for start in range(n):             # try every start …
                fuel, i = 0, start
                while True:                    # … and simulate the whole circle
                    fuel += petrol[i] - dist[i]
                    if fuel < 0:
                        break
                    i = (i + 1) % n
                    if i == start:
                        return start + 1
            return -1

        print(first_tour_naive([4, 8, 7, 4], [6, 5, 3, 5]))
        print(first_tour_naive([1, 2, 3], [3, 3, 3]))
    ''', out='''
        2
        -1
    ''', caption="Naive — O(n²): simulate the circle from every start")
    yield idea("Think of the visited pumps as a **queue**. If the tank goes negative on reaching pump `i` after starting at `s`, then every start between `s` and `i` fails too: the tank was non-negative on arrival at each of them, so starting there with an *empty* tank only makes things worse. Dequeue them all at once — the next candidate start is `i + 1`. Each pump is enqueued (visited as part of a tour) and dequeued (ruled out) at most once, so one pass suffices. Finally, the candidate that survives to the end is valid only if the **total** surplus (what it gains after its start plus the deficit of the skipped prefix it still has to cross) is `>= 0`.")
    yield steps(
        ("Scan once", "Keep `start = 0`, `fuel = 0` (fuel since `start`) and `deficit = 0` (total shortfall of all ruled-out prefixes)."),
        ("On a negative tank at pump i", "Everything from `start` to `i` is ruled out: `deficit += fuel`, `start = i + 1`, `fuel = 0`."),
        ("At the end", "`start` completes the circle only if `fuel + deficit >= 0` — the surplus it collects from `start` to `n − 1` must cover the deficit of the wrapped-around prefix. Otherwise no pump works (equivalently, `sum(petrol) < sum(dist)`)."),
    )
    yield multi('''
        2
        -1
    ''', py=r'''
        def first_tour(petrol, dist):
            start, fuel, deficit = 0, 0, 0
            for i in range(len(petrol)):
                fuel += petrol[i] - dist[i]
                if fuel < 0:                 # pumps start..i are all ruled out at once
                    deficit += fuel          # remember how short that stretch was
                    start = i + 1
                    fuel = 0
            return start + 1 if fuel + deficit >= 0 else -1   # 1-based pump number

        print(first_tour([4, 8, 7, 4], [6, 5, 3, 5]))
        print(first_tour([1, 2, 3], [3, 3, 3]))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        int firstTour(const vector<int>& petrol, const vector<int>& dist) {
            int start = 0, fuel = 0, deficit = 0;
            int n = petrol.size();
            for (int i = 0; i < n; i++) {
                fuel += petrol[i] - dist[i];
                if (fuel < 0) {              // pumps start..i are all ruled out at once
                    deficit += fuel;         // remember how short that stretch was
                    start = i + 1;
                    fuel = 0;
                }
            }
            return fuel + deficit >= 0 ? start + 1 : -1;   // 1-based pump number
        }

        int main() {
            cout << firstTour({4, 8, 7, 4}, {6, 5, 3, 5}) << "\n";
            cout << firstTour({1, 2, 3}, {3, 3, 3}) << "\n";
        }
    ''', java=r'''
        public class Main {
            static int firstTour(int[] petrol, int[] dist) {
                int start = 0, fuel = 0, deficit = 0;
                for (int i = 0; i < petrol.length; i++) {
                    fuel += petrol[i] - dist[i];
                    if (fuel < 0) {              // pumps start..i are all ruled out at once
                        deficit += fuel;         // remember how short that stretch was
                        start = i + 1;
                        fuel = 0;
                    }
                }
                return fuel + deficit >= 0 ? start + 1 : -1;   // 1-based pump number
            }

            public static void main(String[] args) {
                System.out.println(firstTour(new int[]{4, 8, 7, 4}, new int[]{6, 5, 3, 5}));
                System.out.println(firstTour(new int[]{1, 2, 3}, new int[]{3, 3, 3}));
            }
        }
    ''', js=r'''
        function firstTour(petrol, dist) {
            let start = 0, fuel = 0, deficit = 0;
            for (let i = 0; i < petrol.length; i++) {
                fuel += petrol[i] - dist[i];
                if (fuel < 0) {                  // pumps start..i are all ruled out at once
                    deficit += fuel;             // remember how short that stretch was
                    start = i + 1;
                    fuel = 0;
                }
            }
            return fuel + deficit >= 0 ? start + 1 : -1;   // 1-based pump number
        }

        console.log(firstTour([4, 8, 7, 4], [6, 5, 3, 5]));
        console.log(firstTour([1, 2, 3], [3, 3, 3]));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("**Why the final check is enough.** If `sum(petrol) >= sum(dist)` a tour always exists, and the scan above finds the *first* one: every start before `start` was explicitly ruled out, and `start` itself never ran dry on the stretch to the end; wrapping around, it meets the ruled-out prefixes with `fuel` in the tank, and `fuel + deficit >= 0` says that is enough. The explicit queue version (two indices `start`, `end` walking around the circle, dequeuing from the front while the tank is negative) is the same argument spelled out with `(end + 1) % n` arithmetic.")
    yield pitfall("The answer is the pump **number**, and the original notes count from 1 (`start + 1`); many online judges count from 0. Say which convention you use. Also do not forget the `-1` case — with `start` ending at `n` (every pump ruled out) the `start + 1` formula would otherwise return a nonsense `n + 1`.")

    yield section("Interview Q&A", "message-question")
    yield qa("Queue vs deque vs priority queue — when do I use which?",
             "A queue when the order of processing is the order of arrival (BFS, task scheduling). A deque when you also need the other end: sliding windows, work-stealing, palindromes, undo/redo with a bounded history. A priority queue when the next element is determined by a key, not by position — it costs `O(log n)` per operation instead of `O(1)`.")
    yield qa("Why is the sliding window maximum O(n) if there is a while loop inside the for loop?",
             "Every index is appended once and removed at most once (from the back by a bigger element, or from the front by sliding out). Total deque operations are at most `2n`, so the amortised cost per element is constant — the same argument as for the monotonic stack.")
    yield qa("How would you implement a deque yourself?",
             "A circular array with `head` and `tail` indices (and either a `size` counter or one wasted slot to tell full from empty) gives `O(1)` at both ends with cache-friendly storage; grow by doubling when full. A doubly linked list also works but spends a node per element. `collections.deque` uses blocks of 64 pointers in a doubly linked list of blocks; `ArrayDeque` is a circular array.")
    yield qa("How would you generate the numbers in the digit problem without a queue?",
             "Treat the index as a counter in base `k` (the number of digits) with a bijective numeration: the `m`-th number's digits are the base-`k` representation of `m` with digits mapped through the sorted digit set. That is `O(log m)` per number and needs no memory — but the BFS version is the one interviewers expect first, because it generalises to any 'generate in order by extending' problem.")
    yield qa("Why does the petrol-pump argument rule out all pumps between the start and the failure point?",
             "Suppose the tour from `s` first goes negative on arriving at `i`. For any `s < t <= i`, the tank on arrival at `t` (from `s`) was non-negative, so starting at `t` with an empty tank gives at every later pump at most the fuel the `s`-tour had there — and that went negative at `i`. So `t` fails too, and the next possible start is `i + 1`.")
