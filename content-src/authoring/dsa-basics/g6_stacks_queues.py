from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Stacks & Queues"


@topic(G, "stack", "Stack", "stack-2")
def _():
    yield lead("A stack is a **Last In, First Out** (LIFO) collection: you can only add to or remove from one end, the *top*. It is the data structure behind function calls, undo, bracket matching and expression evaluation.")
    yield define("Stack", "a linear data structure where insertion (`push`) and deletion (`pop`) happen at the same end, called the top. The element pushed last is popped first.")
    yield diagram('''
        push(40)  →   ┌────┐  ← top        pop()  →  returns 40
                      │ 40 │
                      ├────┤
                      │ 30 │
                      ├────┤
                      │ 20 │
                      ├────┤
                      │ 10 │  ← bottom
                      └────┘
    ''', "A stack after push(10), push(20), push(30), push(40)")

    yield section("Operations", "list-check")
    yield table(
        ["Operation", "What it does", "Time"],
        ["`push(x)`", "Insert `x` at the top", "O(1)"],
        ["`pop()`", "Remove and return the top element", "O(1)"],
        ["`peek()` / `top()`", "Return the top element without removing it", "O(1)"],
        ["`isEmpty()`", "`true` when the stack has no elements", "O(1)"],
        ["`size()`", "Number of elements", "O(1)"],
    )
    yield warn("**Underflow** — calling `pop()` or `peek()` on an empty stack. **Overflow** — calling `push()` on a fixed-capacity stack that is full. Always check `isEmpty()` before popping; the built-in containers below raise an error (Python/Java) or return `undefined` (JavaScript) instead.")

    yield section("Using the built-in containers", "box")
    yield p("Every language already has a container that works as a stack. Use the end of a dynamic array (append / pop at the back are amortised O(1)) — never the front, where every operation shifts all elements.")
    yield multi('''
        top: c
        popped: c
        popped: b
        size: 1
        empty: False
    ''', py='''
        stack = []                 # a list used as a stack
        stack.append('a')          # push
        stack.append('b')
        stack.append('c')
        print("top:", stack[-1])   # peek
        print("popped:", stack.pop())
        print("popped:", stack.pop())
        print("size:", len(stack))
        print("empty:", len(stack) == 0)
    ''', cpp='''
        #include <iostream>
        #include <stack>
        using namespace std;

        int main() {
            stack<char> st;            // std::stack adapts a deque
            st.push('a');
            st.push('b');
            st.push('c');
            cout << "top: " << st.top() << "\\n";
            cout << "popped: " << st.top() << "\\n"; st.pop();   // pop() returns nothing in C++
            cout << "popped: " << st.top() << "\\n"; st.pop();
            cout << "size: " << st.size() << "\\n";
            cout << "empty: " << (st.empty() ? "True" : "False") << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            public static void main(String[] args) {
                Deque<Character> stack = new ArrayDeque<>();   // preferred over the legacy java.util.Stack
                stack.push('a');
                stack.push('b');
                stack.push('c');
                System.out.println("top: " + stack.peek());
                System.out.println("popped: " + stack.pop());
                System.out.println("popped: " + stack.pop());
                System.out.println("size: " + stack.size());
                System.out.println("empty: " + (stack.isEmpty() ? "True" : "False"));
            }
        }
    ''', js='''
        const stack = [];              // an array used as a stack
        stack.push('a');
        stack.push('b');
        stack.push('c');
        console.log("top:", stack[stack.length - 1]);
        console.log("popped:", stack.pop());
        console.log("popped:", stack.pop());
        console.log("size:", stack.length);
        console.log("empty:", stack.length === 0 ? "True" : "False");
    ''')
    yield note("Python's `collections.deque` and `queue.LifoQueue` also work as stacks. `deque` is the right choice when the same container must also behave as a queue; `LifoQueue` is thread-safe and meant for producer/consumer code, not for algorithms.")

    yield section("Implementing a stack with a linked list", "link")
    yield p("Pushing and popping at the head of a singly linked list are both O(1), so a linked list gives a stack that never needs resizing. The head node is the top.")
    yield diagram('''
        top
         ↓
        ┌────┬───┐   ┌────┬───┐   ┌────┬───┐
        │ 30 │ ●─┼──▶│ 20 │ ●─┼──▶│ 10 │ ∅ │
        └────┴───┘   └────┴───┘   └────┴───┘
    ''', "push(10), push(20), push(30) — the newest node becomes the head")
    yield multi('''
        30 20 10
        size: 3
        popped: 30
        peek: 20
    ''', py='''
        class Node:
            def __init__(self, value):
                self.value = value
                self.next = None

        class Stack:
            def __init__(self):
                self.head = None
                self.size = 0

            def push(self, value):
                node = Node(value)
                node.next = self.head      # new node points at the old top
                self.head = node
                self.size += 1

            def pop(self):
                if self.head is None:
                    raise IndexError("pop from empty stack")
                node = self.head
                self.head = node.next
                self.size -= 1
                return node.value

            def peek(self):
                return None if self.head is None else self.head.value

            def is_empty(self):
                return self.head is None

        s = Stack()
        for x in (10, 20, 30):
            s.push(x)
        node = s.head
        while node:                      # print top → bottom
            print(node.value, end=" ")
            node = node.next
        print()
        print("size:", s.size)
        print("popped:", s.pop())
        print("peek:", s.peek())
    ''', cpp='''
        #include <iostream>
        #include <stdexcept>
        using namespace std;

        struct Node {
            int value;
            Node* next;
            Node(int v) : value(v), next(nullptr) {}
        };

        class Stack {
            Node* head = nullptr;
            int count = 0;
        public:
            ~Stack() { while (head) pop(); }
            void push(int v) {
                Node* node = new Node(v);
                node->next = head;           // new node points at the old top
                head = node;
                count++;
            }
            int pop() {
                if (!head) throw runtime_error("pop from empty stack");
                Node* node = head;
                int v = node->value;
                head = node->next;
                delete node;
                count--;
                return v;
            }
            int peek() const { return head->value; }
            bool isEmpty() const { return head == nullptr; }
            int size() const { return count; }
            Node* top() const { return head; }
        };

        int main() {
            Stack s;
            for (int x : {10, 20, 30}) s.push(x);
            for (Node* n = s.top(); n; n = n->next) cout << n->value << " ";
            cout << "\\n";
            cout << "size: " << s.size() << "\\n";
            cout << "popped: " << s.pop() << "\\n";
            cout << "peek: " << s.peek() << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int value; Node next;
                Node(int v) { value = v; }
            }

            static class Stack {
                Node head; int size;
                void push(int v) {
                    Node node = new Node(v);
                    node.next = head;            // new node points at the old top
                    head = node;
                    size++;
                }
                int pop() {
                    if (head == null) throw new RuntimeException("pop from empty stack");
                    int v = head.value;
                    head = head.next;
                    size--;
                    return v;
                }
                Integer peek() { return head == null ? null : head.value; }
                boolean isEmpty() { return head == null; }
            }

            public static void main(String[] args) {
                Stack s = new Stack();
                for (int x : new int[]{10, 20, 30}) s.push(x);
                StringBuilder sb = new StringBuilder();
                for (Node n = s.head; n != null; n = n.next) sb.append(n.value).append(' ');
                System.out.println(sb.toString().trim());
                System.out.println("size: " + s.size);
                System.out.println("popped: " + s.pop());
                System.out.println("peek: " + s.peek());
            }
        }
    ''', js='''
        class Node {
            constructor(value) { this.value = value; this.next = null; }
        }

        class Stack {
            constructor() { this.head = null; this.size = 0; }
            push(value) {
                const node = new Node(value);
                node.next = this.head;           // new node points at the old top
                this.head = node;
                this.size++;
            }
            pop() {
                if (!this.head) throw new Error("pop from empty stack");
                const node = this.head;
                this.head = node.next;
                this.size--;
                return node.value;
            }
            peek() { return this.head ? this.head.value : null; }
            isEmpty() { return this.head === null; }
        }

        const s = new Stack();
        for (const x of [10, 20, 30]) s.push(x);
        const parts = [];
        for (let n = s.head; n; n = n.next) parts.push(n.value);
        console.log(parts.join(" "));
        console.log("size:", s.size);
        console.log("popped:", s.pop());
        console.log("peek:", s.peek());
    ''')
    yield complexity("O(1) per operation", "O(n) for n elements")

    yield section("Where stacks are used", "apps")
    yield cards(
        ("Function calls", "The call stack stores one frame per active call; returning pops it. Deep recursion overflows it.", "stack-3"),
        ("Balanced brackets", "Push every opener, pop on every closer and check that it matches — see below.", "brackets"),
        ("Undo / redo, back / forward", "Each action is pushed; undo pops it onto a second stack for redo.", "arrow-back-up"),
        ("Expression evaluation", "Infix → postfix conversion and postfix evaluation both run on a stack.", "math-function"),
        ("Reversing", "Push everything, then pop everything — the order reverses.", "arrows-left-right"),
        ("Monotonic stack problems", "Next greater element, stock span, histogram area (DSA Advanced → Stack).", "chart-bar"),
        cols=3,
    )

    yield section("Problem: check for balanced parentheses", "brackets")
    yield io("s = \"([])\"", "Yes", "s = \"([)]\"", "No", "s = \"((\"", "No")
    yield idea("Scan left to right. Push every opening bracket. On a closing bracket the stack must be non-empty and its top must be the matching opener — pop it. At the end the stack must be empty. Any violation means the string is unbalanced.")
    yield steps(
        ("Opening bracket", "Push it onto the stack."),
        ("Closing bracket", "If the stack is empty → unbalanced. Pop the top; if it is not the matching opener → unbalanced."),
        ("End of string", "Balanced only if the stack is empty (every opener was closed)."),
    )
    yield multi('''
        ([]) → Yes
        ([)] → No
        (( → No
        {[()]} → Yes
    ''', py='''
        def is_balanced(s):
            match = {')': '(', ']': '[', '}': '{'}
            stack = []
            for ch in s:
                if ch in '([{':
                    stack.append(ch)
                elif ch in match:
                    if not stack or stack.pop() != match[ch]:
                        return False
            return not stack

        for s in ["([])", "([)]", "((", "{[()]}"]:
            print(s, "→", "Yes" if is_balanced(s) else "No")
    ''', cpp='''
        #include <iostream>
        #include <stack>
        #include <string>
        using namespace std;

        bool isBalanced(const string& s) {
            stack<char> st;
            for (char ch : s) {
                if (ch == '(' || ch == '[' || ch == '{') {
                    st.push(ch);
                } else {
                    if (st.empty()) return false;
                    char open = st.top(); st.pop();
                    if ((ch == ')' && open != '(') || (ch == ']' && open != '[') || (ch == '}' && open != '{'))
                        return false;
                }
            }
            return st.empty();
        }

        int main() {
            for (string s : {"([])", "([)]", "((", "{[()]}"})
                cout << s << " → " << (isBalanced(s) ? "Yes" : "No") << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static boolean isBalanced(String s) {
                Deque<Character> stack = new ArrayDeque<>();
                for (char ch : s.toCharArray()) {
                    if (ch == '(' || ch == '[' || ch == '{') {
                        stack.push(ch);
                    } else {
                        if (stack.isEmpty()) return false;
                        char open = stack.pop();
                        if ((ch == ')' && open != '(') || (ch == ']' && open != '[') || (ch == '}' && open != '{'))
                            return false;
                    }
                }
                return stack.isEmpty();
            }

            public static void main(String[] args) {
                for (String s : new String[]{"([])", "([)]", "((", "{[()]}"})
                    System.out.println(s + " → " + (isBalanced(s) ? "Yes" : "No"));
            }
        }
    ''', js='''
        function isBalanced(s) {
            const match = { ')': '(', ']': '[', '}': '{' };
            const stack = [];
            for (const ch of s) {
                if ('([{'.includes(ch)) {
                    stack.push(ch);
                } else if (ch in match) {
                    if (!stack.length || stack.pop() !== match[ch]) return false;
                }
            }
            return stack.length === 0;
        }

        for (const s of ["([])", "([)]", "((", "{[()]}"])
            console.log(s, "→", isBalanced(s) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("Forgetting the final `stack is empty` check accepts `\"((\"`; forgetting the `empty before pop` check crashes on `\")\"`. Both are classic interview slips.")

    yield section("Interview Q&A", "message-question")
    yield qa("Array or linked list for a stack — which is better?",
             "Both give O(1) push/pop. An array (dynamic) is cache-friendly and usually faster; occasionally a push triggers an O(n) resize, but the amortised cost stays O(1). A linked list never resizes and has no capacity limit, at the price of one pointer per element and scattered memory.")
    yield qa("What is stack overflow in the context of recursion?",
             "Every call pushes a frame on the call stack. Recursion that goes too deep (no base case, or a very large input) exhausts the stack's fixed size — Python raises `RecursionError` at about 1000 frames; C++ and Java crash with a stack overflow. Convert to iteration or use an explicit stack when depth can be large.")
    yield qa("How would you implement a queue using two stacks?",
             "Push into stack `in`. To dequeue, if `out` is empty, pop everything from `in` and push onto `out` (this reverses the order), then pop from `out`. Each element moves at most twice, so operations are amortised O(1). See the Queue topic.")


@topic(G, "queue", "Queue", "arrows-right")
def _():
    yield lead("A queue is a **First In, First Out** (FIFO) collection: elements enter at the *rear* and leave from the *front*, exactly like a line at a ticket counter. It is the data structure behind scheduling, buffering and breadth-first search.")
    yield define("Queue", "a linear data structure where insertion (`enqueue`) happens at one end, the rear, and deletion (`dequeue`) happens at the other end, the front. The element that has waited longest is served first.")
    yield diagram('''
        dequeue()  ◀──  ┌────┬────┬────┬────┬────┐  ◀──  enqueue(x)
                        │ 10 │ 15 │ 20 │ 30 │ 40 │
                        └────┴────┴────┴────┴────┘
                          ↑                   ↑
                        front               rear
    ''', "A queue after enqueue(10), enqueue(15), enqueue(20), enqueue(30), enqueue(40) — 10 leaves first")

    yield section("Operations", "list-check")
    yield table(
        ["Operation", "What it does", "Time"],
        ["`enqueue(x)`", "Insert `x` at the rear", "O(1)"],
        ["`dequeue()`", "Remove and return the front element", "O(1)"],
        ["`front()` / `getFront()`", "Return the front element without removing it", "O(1)"],
        ["`rear()` / `getRear()`", "Return the rear element without removing it", "O(1)"],
        ["`isEmpty()`", "`true` when the queue has no elements", "O(1)"],
        ["`size()`", "Number of elements", "O(1)"],
    )
    yield p("Every operation is O(1) — *provided the implementation is right*. A plain array where `dequeue` removes index 0 is the classic way to get this wrong: every remaining element shifts one slot left, so `dequeue` becomes O(n). The circular-array section below fixes that.")
    yield warn("**Underflow** — `dequeue()` or `front()` on an empty queue. **Overflow** — `enqueue()` on a fixed-capacity queue that is full. Check `isEmpty()` / `isFull()` first; the built-in containers raise (Python/C++ UB/Java `remove`) or return `null`/`undefined` (Java `poll`, JavaScript `shift`).")

    yield section("Where queues are used", "apps")
    yield cards(
        ("One resource, many consumers", "Ticket counters, printer spooling, a single CPU shared by many processes — whoever asked first is served first.", "ticket"),
        ("Buffers between fast and slow devices", "The keyboard buffer, network sockets and audio/video pipelines queue data produced faster than it is consumed.", "device-desktop"),
        ("Operating systems", "FCFS (first-come, first-served) scheduling, semaphore wait lists, I/O request queues, spooling.", "cpu"),
        ("Networks and messaging", "Routers and switches queue packets; mail servers and message brokers (RabbitMQ, Kafka) queue jobs.", "network"),
        ("Breadth-first search", "BFS on graphs and level-order traversal of trees visit nodes in the order they were discovered — a queue (see Trees and Graphs).", "topology-star"),
        ("Variations", "**Deque** (both ends), **priority queue** (served by priority, not arrival), **double-ended priority queue** (min and max).", "arrows-shuffle"),
        cols=3,
    )

    yield section("Using the built-in containers", "box")
    yield p("Every language ships a ready-made queue. The rule is the same everywhere: add at the back, remove at the front, and make sure removing at the front is O(1).")
    yield multi('''
        front: 10
        rear: 30
        dequeued: 10
        dequeued: 20
        size: 1
        empty: False
    ''', py='''
        from collections import deque

        q = deque()                       # O(1) at both ends
        q.append(10)                      # enqueue at the rear
        q.append(20)
        q.append(30)
        print("front:", q[0])
        print("rear:", q[-1])
        print("dequeued:", q.popleft())   # dequeue from the front
        print("dequeued:", q.popleft())
        print("size:", len(q))
        print("empty:", len(q) == 0)
    ''', cpp='''
        #include <iostream>
        #include <queue>
        using namespace std;

        int main() {
            queue<int> q;                 // std::queue adapts a std::deque
            q.push(10);                   // enqueue at the back
            q.push(20);
            q.push(30);
            cout << "front: " << q.front() << "\\n";
            cout << "rear: " << q.back() << "\\n";
            cout << "dequeued: " << q.front() << "\\n"; q.pop();   // pop() returns nothing in C++
            cout << "dequeued: " << q.front() << "\\n"; q.pop();
            cout << "size: " << q.size() << "\\n";
            cout << "empty: " << (q.empty() ? "True" : "False") << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;

        public class Main {
            public static void main(String[] args) {
                ArrayDeque<Integer> q = new ArrayDeque<>();   // implements Queue (and Deque)
                q.offer(10);                                  // enqueue at the tail
                q.offer(20);
                q.offer(30);
                System.out.println("front: " + q.peek());
                System.out.println("rear: " + q.peekLast());  // a Deque extra — Queue alone has no rear access
                System.out.println("dequeued: " + q.poll());  // dequeue from the head
                System.out.println("dequeued: " + q.poll());
                System.out.println("size: " + q.size());
                System.out.println("empty: " + (q.isEmpty() ? "True" : "False"));
            }
        }
    ''', js='''
        const q = [];                       // an array used as a queue
        q.push(10);                         // enqueue at the end
        q.push(20);
        q.push(30);
        console.log("front:", q[0]);
        console.log("rear:", q[q.length - 1]);
        console.log("dequeued:", q.shift());   // O(n): every element moves one slot left
        console.log("dequeued:", q.shift());
        console.log("size:", q.length);
        console.log("empty:", q.length === 0 ? "True" : "False");
    ''')
    yield table(
        ["Language", "Container", "enqueue", "dequeue", "front", "Notes"],
        ["Python", "`collections.deque`", "`append(x)`", "`popleft()`", "`q[0]`", "O(1) at both ends; `q[-1]` is the rear"],
        ["Python", "`queue.Queue`", "`put(x)`", "`get()`", "—", "thread-safe, blocking — for producer/consumer code, not algorithms"],
        ["C++", "`std::queue<T>`", "`push(x)`", "`pop()` (returns nothing)", "`front()`", "`back()` is the rear; adapts `std::deque`"],
        ["Java", "`ArrayDeque<T>` / `LinkedList<T>` as `Queue<T>`", "`offer(x)` / `add(x)`", "`poll()` / `remove()`", "`peek()` / `element()`", "`offer/poll/peek` return `false`/`null` on failure, `add/remove/element` throw"],
        ["JavaScript", "`Array`", "`push(x)`", "`shift()`", "`q[0]`", "`shift()` is O(n) — fine for small queues, a trap in BFS on large graphs"],
    )
    yield pitfall("Using a Python **list** as a queue. `q.pop(0)` shifts every remaining element, so a loop that dequeues `n` items costs O(n²). The notes' original list version is shown below only to make the point — reach for `collections.deque`.")
    yield code('''
        q = []
        q.append(10)
        q.append(20)
        q.append(30)
        print(q)          # [10, 20, 30]
        print(q.pop(0))   # 10   ← removes the front, but shifts 20 and 30 left: O(n)
        print(q)          # [20, 30]
        q.pop(0)
        print(q)          # [30]
    ''')
    yield note("`queue.Queue` is for threads: `get()` **blocks** until an item arrives, so calling it on an empty queue in single-threaded code hangs the program. Use `get_nowait()` / `put_nowait()` if you must use it outside a producer/consumer setting.")
    yield code('''
        from queue import Queue

        q = Queue()
        q.put(10)
        q.put(20)
        print(q.get())            # 10
        print(q.qsize())          # 1
        print(q.empty())          # False
        print(q.get_nowait())     # 20
    ''')

    yield section("Implementing a queue with a linked list", "link")
    yield p("Keep two pointers: `front` (the head, where we dequeue) and `rear` (the tail, where we enqueue). Appending at the tail and removing at the head of a singly linked list are both O(1), and the queue never needs resizing.")
    yield diagram('''
        front                                   rear
         ↓                                       ↓
        ┌────┬───┐   ┌────┬───┐   ┌────┬───┐
        │ 10 │ ●─┼──▶│ 20 │ ●─┼──▶│ 30 │ ∅ │   enqueue(40): rear.next = node, rear = node
        └────┴───┘   └────┴───┘   └────┴───┘   dequeue():   front = front.next
    ''', "enqueue(10), enqueue(20), enqueue(30) — the oldest node is the head")
    yield steps(
        ("enqueue(x)", "Create a node. If the queue is empty, `front = rear = node`; otherwise `rear.next = node` and `rear = node`."),
        ("dequeue()", "Save `front.value`, move `front = front.next`. If `front` became `null`, also set `rear = null` — the classic bug is leaving `rear` pointing at the freed node."),
        ("getFront / getRear", "Read `front.value` / `rear.value` — O(1) because we keep both pointers."),
    )
    yield multi('''
        front: 10
        rear: 30
        dequeued: 10
        front: 20
        rear: 30
        size: 2
        empty: False
    ''', py='''
        class Node:
            def __init__(self, value):
                self.value = value
                self.next = None

        class Queue:
            def __init__(self):
                self.front = None        # dequeue here (head)
                self.rear = None         # enqueue here (tail)
                self.size = 0

            def enqueue(self, value):
                node = Node(value)
                if self.rear is None:            # empty: the node is both front and rear
                    self.front = self.rear = node
                else:
                    self.rear.next = node        # link after the old tail
                    self.rear = node
                self.size += 1

            def dequeue(self):
                if self.front is None:
                    raise IndexError("dequeue from empty queue")
                node = self.front
                self.front = node.next
                if self.front is None:           # became empty: rear must not dangle
                    self.rear = None
                self.size -= 1
                return node.value

            def get_front(self):
                return None if self.front is None else self.front.value

            def get_rear(self):
                return None if self.rear is None else self.rear.value

            def is_empty(self):
                return self.size == 0

        q = Queue()
        for x in (10, 20, 30):
            q.enqueue(x)
        print("front:", q.get_front())
        print("rear:", q.get_rear())
        print("dequeued:", q.dequeue())
        print("front:", q.get_front())
        print("rear:", q.get_rear())
        print("size:", q.size)
        print("empty:", q.is_empty())
    ''', cpp='''
        #include <iostream>
        #include <stdexcept>
        using namespace std;

        struct Node {
            int value;
            Node* next;
            Node(int v) : value(v), next(nullptr) {}
        };

        class Queue {
            Node* front = nullptr;     // dequeue here (head)
            Node* rear = nullptr;      // enqueue here (tail)
            int count = 0;
        public:
            ~Queue() { while (front) dequeue(); }
            void enqueue(int v) {
                Node* node = new Node(v);
                if (!rear) front = rear = node;          // empty: the node is both front and rear
                else { rear->next = node; rear = node; } // link after the old tail
                count++;
            }
            int dequeue() {
                if (!front) throw runtime_error("dequeue from empty queue");
                Node* node = front;
                int v = node->value;
                front = node->next;
                if (!front) rear = nullptr;              // became empty: rear must not dangle
                delete node;
                count--;
                return v;
            }
            int getFront() const { return front->value; }
            int getRear() const { return rear->value; }
            bool isEmpty() const { return count == 0; }
            int size() const { return count; }
        };

        int main() {
            Queue q;
            for (int x : {10, 20, 30}) q.enqueue(x);
            cout << "front: " << q.getFront() << "\\n";
            cout << "rear: " << q.getRear() << "\\n";
            cout << "dequeued: " << q.dequeue() << "\\n";
            cout << "front: " << q.getFront() << "\\n";
            cout << "rear: " << q.getRear() << "\\n";
            cout << "size: " << q.size() << "\\n";
            cout << "empty: " << (q.isEmpty() ? "True" : "False") << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int value; Node next;
                Node(int v) { value = v; }
            }

            static class Queue {
                Node front, rear;          // dequeue at front (head), enqueue at rear (tail)
                int size;
                void enqueue(int v) {
                    Node node = new Node(v);
                    if (rear == null) front = rear = node;      // empty: the node is both front and rear
                    else { rear.next = node; rear = node; }     // link after the old tail
                    size++;
                }
                int dequeue() {
                    if (front == null) throw new RuntimeException("dequeue from empty queue");
                    int v = front.value;
                    front = front.next;
                    if (front == null) rear = null;             // became empty: rear must not dangle
                    size--;
                    return v;
                }
                Integer getFront() { return front == null ? null : front.value; }
                Integer getRear() { return rear == null ? null : rear.value; }
                boolean isEmpty() { return size == 0; }
            }

            public static void main(String[] args) {
                Queue q = new Queue();
                for (int x : new int[]{10, 20, 30}) q.enqueue(x);
                System.out.println("front: " + q.getFront());
                System.out.println("rear: " + q.getRear());
                System.out.println("dequeued: " + q.dequeue());
                System.out.println("front: " + q.getFront());
                System.out.println("rear: " + q.getRear());
                System.out.println("size: " + q.size);
                System.out.println("empty: " + (q.isEmpty() ? "True" : "False"));
            }
        }
    ''', js='''
        class Node {
            constructor(value) { this.value = value; this.next = null; }
        }

        class Queue {
            constructor() { this.front = null; this.rear = null; this.size = 0; }
            enqueue(value) {
                const node = new Node(value);
                if (this.rear === null) this.front = this.rear = node;   // empty: both ends
                else { this.rear.next = node; this.rear = node; }        // link after the old tail
                this.size++;
            }
            dequeue() {
                if (this.front === null) throw new Error("dequeue from empty queue");
                const node = this.front;
                this.front = node.next;
                if (this.front === null) this.rear = null;               // became empty: rear must not dangle
                this.size--;
                return node.value;
            }
            getFront() { return this.front ? this.front.value : null; }
            getRear() { return this.rear ? this.rear.value : null; }
            isEmpty() { return this.size === 0; }
        }

        const q = new Queue();
        for (const x of [10, 20, 30]) q.enqueue(x);
        console.log("front:", q.getFront());
        console.log("rear:", q.getRear());
        console.log("dequeued:", q.dequeue());
        console.log("front:", q.getFront());
        console.log("rear:", q.getRear());
        console.log("size:", q.size);
        console.log("empty:", q.isEmpty() ? "True" : "False");
    ''')
    yield complexity("O(1) per operation", "O(n) for n elements")
    yield pitfall("Enqueueing at the **head** and dequeueing at the tail would need the node *before* the tail, which a singly linked list cannot reach in O(1). Always enqueue at the tail and dequeue at the head.")

    yield section("Implementing a queue with a circular array", "repeat")
    yield p("A fixed array of capacity `cap` has two naive designs, and both are bad. If `dequeue` removes `slots[0]` and shifts everything, it is O(n). If instead it just advances a `front` index, each dequeue leaves a dead slot behind: after a few dequeues `rear` reaches the end and `enqueue` fails even though the array is half empty.")
    yield diagram('''
        Plain array, dequeue by advancing front (capacity 5):

          index:   0     1     2     3     4
                ┌─────┬─────┬─────┬─────┬─────┐
                │  ×  │  ×  │ 30  │ 40  │ 50  │   front = 2, rear = 5
                └─────┴─────┴─────┴─────┴─────┘
                   ↑ dead slots              ↑ rear is past the end:
                                               enqueue(60) fails although two slots are free
    ''', "Advancing front without wrapping wastes every slot that has been dequeued")
    yield p("The fix is to let both indices **wrap around** with the modulo operator: `rear = (rear + 1) % cap` and `front = (front + 1) % cap`. The array is treated as a ring, so a dequeued slot is reused by the next enqueue.")
    yield diagram('''
        Circular array — same state, then enqueue(60), enqueue(70):

          index:   0     1     2     3     4
                ┌─────┬─────┬─────┬─────┬─────┐
                │ 60  │ 70  │ 30  │ 40  │ 50  │   rear wrapped: 5 % 5 = 0, then 1
                └─────┴─────┴─────┴─────┴─────┘
                               ↑ front = 2
                   ↑ rear = 2 (next free slot) — equal to front, so size tells us: full

          logical order (front → rear):  30  40  50  60  70
    ''', "The ring reuses the slots freed by dequeue; the logical order is read from front, wrapping with % cap")
    yield note("When `front == rear` the ring is either **empty or full** — the indices alone cannot tell. Either keep a `size` counter (done below) or deliberately leave one slot unused and treat `(rear + 1) % cap == front` as full.")
    yield io("capacity = 5; enqueue 10 20 30 40 50; dequeue ×2; enqueue 60 70", "slots: 60 70 30 40 50 — logical order 30 40 50 60 70")
    yield multi('''
        front: 10
        rear: 50
        full: True
        dequeued: 10
        dequeued: 20
        enqueue 60 → slot 0
        enqueue 70 → slot 1
        slots: 60 70 30 40 50
        front = 2 rear = 2 size = 5
        in order: 30 40 50 60 70
    ''', py='''
        class CircularQueue:
            def __init__(self, capacity):
                self.slots = [None] * capacity
                self.cap = capacity
                self.front = 0          # index of the first element
                self.rear = 0           # index where the next element goes
                self.size = 0           # needed: front == rear for both empty and full

            def is_empty(self):
                return self.size == 0

            def is_full(self):
                return self.size == self.cap

            def enqueue(self, value):
                if self.is_full():
                    raise OverflowError("queue is full")
                slot = self.rear
                self.slots[slot] = value
                self.rear = (self.rear + 1) % self.cap     # wrap around
                self.size += 1
                return slot

            def dequeue(self):
                if self.is_empty():
                    raise IndexError("queue is empty")
                value = self.slots[self.front]
                self.front = (self.front + 1) % self.cap   # wrap around
                self.size -= 1
                return value

            def get_front(self):
                return self.slots[self.front]

            def get_rear(self):
                return self.slots[(self.rear - 1 + self.cap) % self.cap]

        q = CircularQueue(5)
        for x in (10, 20, 30, 40, 50):
            q.enqueue(x)
        print("front:", q.get_front())
        print("rear:", q.get_rear())
        print("full:", q.is_full())
        print("dequeued:", q.dequeue())
        print("dequeued:", q.dequeue())
        print("enqueue 60 → slot", q.enqueue(60))
        print("enqueue 70 → slot", q.enqueue(70))
        print("slots:", *q.slots)
        print("front =", q.front, "rear =", q.rear, "size =", q.size)
        print("in order:", *(q.slots[(q.front + i) % q.cap] for i in range(q.size)))
    ''', cpp='''
        #include <iostream>
        #include <stdexcept>
        #include <vector>
        using namespace std;

        class CircularQueue {
        public:
            vector<int> slots;
            int cap, front = 0, rear = 0, size = 0;   // size: front == rear for both empty and full
            CircularQueue(int capacity) : slots(capacity, 0), cap(capacity) {}
            bool isEmpty() const { return size == 0; }
            bool isFull() const { return size == cap; }
            int enqueue(int value) {
                if (isFull()) throw runtime_error("queue is full");
                int slot = rear;
                slots[slot] = value;
                rear = (rear + 1) % cap;              // wrap around
                size++;
                return slot;
            }
            int dequeue() {
                if (isEmpty()) throw runtime_error("queue is empty");
                int value = slots[front];
                front = (front + 1) % cap;            // wrap around
                size--;
                return value;
            }
            int getFront() const { return slots[front]; }
            int getRear() const { return slots[(rear - 1 + cap) % cap]; }
        };

        int main() {
            CircularQueue q(5);
            for (int x : {10, 20, 30, 40, 50}) q.enqueue(x);
            cout << "front: " << q.getFront() << "\\n";
            cout << "rear: " << q.getRear() << "\\n";
            cout << "full: " << (q.isFull() ? "True" : "False") << "\\n";
            cout << "dequeued: " << q.dequeue() << "\\n";
            cout << "dequeued: " << q.dequeue() << "\\n";
            cout << "enqueue 60 → slot " << q.enqueue(60) << "\\n";
            cout << "enqueue 70 → slot " << q.enqueue(70) << "\\n";
            cout << "slots:";
            for (int v : q.slots) cout << " " << v;
            cout << "\\n";
            cout << "front = " << q.front << " rear = " << q.rear << " size = " << q.size << "\\n";
            cout << "in order:";
            for (int i = 0; i < q.size; i++) cout << " " << q.slots[(q.front + i) % q.cap];
            cout << "\\n";
        }
    ''', java='''
        public class Main {
            static class CircularQueue {
                int[] slots;
                int cap, front = 0, rear = 0, size = 0;   // size: front == rear for both empty and full
                CircularQueue(int capacity) { slots = new int[capacity]; cap = capacity; }
                boolean isEmpty() { return size == 0; }
                boolean isFull() { return size == cap; }
                int enqueue(int value) {
                    if (isFull()) throw new RuntimeException("queue is full");
                    int slot = rear;
                    slots[slot] = value;
                    rear = (rear + 1) % cap;              // wrap around
                    size++;
                    return slot;
                }
                int dequeue() {
                    if (isEmpty()) throw new RuntimeException("queue is empty");
                    int value = slots[front];
                    front = (front + 1) % cap;            // wrap around
                    size--;
                    return value;
                }
                int getFront() { return slots[front]; }
                int getRear() { return slots[(rear - 1 + cap) % cap]; }
            }

            public static void main(String[] args) {
                CircularQueue q = new CircularQueue(5);
                for (int x : new int[]{10, 20, 30, 40, 50}) q.enqueue(x);
                System.out.println("front: " + q.getFront());
                System.out.println("rear: " + q.getRear());
                System.out.println("full: " + (q.isFull() ? "True" : "False"));
                System.out.println("dequeued: " + q.dequeue());
                System.out.println("dequeued: " + q.dequeue());
                System.out.println("enqueue 60 → slot " + q.enqueue(60));
                System.out.println("enqueue 70 → slot " + q.enqueue(70));
                StringBuilder sb = new StringBuilder("slots:");
                for (int v : q.slots) sb.append(' ').append(v);
                System.out.println(sb);
                System.out.println("front = " + q.front + " rear = " + q.rear + " size = " + q.size);
                sb = new StringBuilder("in order:");
                for (int i = 0; i < q.size; i++) sb.append(' ').append(q.slots[(q.front + i) % q.cap]);
                System.out.println(sb);
            }
        }
    ''', js='''
        class CircularQueue {
            constructor(capacity) {
                this.slots = new Array(capacity).fill(null);
                this.cap = capacity;
                this.front = 0;        // index of the first element
                this.rear = 0;         // index where the next element goes
                this.size = 0;         // needed: front == rear for both empty and full
            }
            isEmpty() { return this.size === 0; }
            isFull() { return this.size === this.cap; }
            enqueue(value) {
                if (this.isFull()) throw new Error("queue is full");
                const slot = this.rear;
                this.slots[slot] = value;
                this.rear = (this.rear + 1) % this.cap;      // wrap around
                this.size++;
                return slot;
            }
            dequeue() {
                if (this.isEmpty()) throw new Error("queue is empty");
                const value = this.slots[this.front];
                this.front = (this.front + 1) % this.cap;    // wrap around
                this.size--;
                return value;
            }
            getFront() { return this.slots[this.front]; }
            getRear() { return this.slots[(this.rear - 1 + this.cap) % this.cap]; }
        }

        const q = new CircularQueue(5);
        for (const x of [10, 20, 30, 40, 50]) q.enqueue(x);
        console.log("front:", q.getFront());
        console.log("rear:", q.getRear());
        console.log("full:", q.isFull() ? "True" : "False");
        console.log("dequeued:", q.dequeue());
        console.log("dequeued:", q.dequeue());
        console.log("enqueue 60 → slot", q.enqueue(60));
        console.log("enqueue 70 → slot", q.enqueue(70));
        console.log("slots:", q.slots.join(" "));
        console.log("front =", q.front, "rear =", q.rear, "size =", q.size);
        const order = [];
        for (let i = 0; i < q.size; i++) order.push(q.slots[(q.front + i) % q.cap]);
        console.log("in order:", order.join(" "));
    ''')
    yield complexity("O(1) per operation", "O(cap)")
    yield pitfall("`getRear()` is **not** `slots[rear - 1]`: after a wrap `rear` can be 0, and index `-1` is out of bounds in C++/Java (and silently the last element in Python). Use `(rear - 1 + cap) % cap`. Also note that a dequeued slot is not cleared — printing the raw array shows stale values until they are overwritten.")
    yield note("Dynamic-array queues (`std::deque`, Java `ArrayDeque`, Python `deque`) are circular buffers that double the capacity when full, so they never overflow: amortised O(1) enqueue.")

    yield section("Problem: implement a stack using queues", "stack-2")
    yield io("push(10), push(20), push(30), top(), pop(), top()", "30, 30, 20")
    yield idea("A queue gives you the *oldest* element; a stack needs the *newest*. Make `push` expensive: put the new element into an empty auxiliary queue, move everything else behind it, then swap the queues. The front of `q1` is now always the most recently pushed element, so `pop` and `top` are plain O(1) queue operations.")
    yield steps(
        ("push(x) — version 1", "Move everything from `q1` to `q2`, enqueue `x` into `q1`, move everything back from `q2` to `q1`. Two full copies per push."),
        ("push(x) — optimised", "Enqueue `x` into `q2`, move everything from `q1` behind it, then **swap** `q1` and `q2`. One copy per push, same effect."),
        ("pop() / top()", "Dequeue / peek the front of `q1` — O(1)."),
        ("size() / isEmpty()", "Delegate to `q1`; `isFull()` is always `false` for a dynamic queue."),
    )
    yield diagram('''
        push(10):  q2 = [10]                 swap → q1 = [10]        q2 = []
        push(20):  q2 = [20] ← move 10 →     q2 = [20 10]   swap → q1 = [20 10]
        push(30):  q2 = [30] ← move 20 10 →  q2 = [30 20 10] swap → q1 = [30 20 10]
                                                                      ↑ front = top of stack
    ''', "The optimised push: the new element goes in first, older elements queue behind it")
    yield multi('''
        top: 30
        popped: 30
        top: 20
        size: 2
    ''', py='''
        from collections import deque

        class Stack:
            def __init__(self):
                self.q1 = deque()      # holds the items, newest at the front
                self.q2 = deque()      # auxiliary, empty between operations

            def push(self, x):
                self.q2.append(x)                      # a) x goes in first ...
                while self.q1:                         # b) ... then everything older behind it
                    self.q2.append(self.q1.popleft())
                self.q1, self.q2 = self.q2, self.q1    # c) swap: q1 holds the items again

            def pop(self):
                return self.q1.popleft()               # front of q1 is the newest item

            def top(self):
                return self.q1[0]

            def size(self):
                return len(self.q1)

            def is_empty(self):
                return len(self.q1) == 0

        s = Stack()
        s.push(10)
        s.push(20)
        s.push(30)
        print("top:", s.top())
        print("popped:", s.pop())
        print("top:", s.top())
        print("size:", s.size())
    ''', cpp='''
        #include <iostream>
        #include <queue>
        #include <utility>
        using namespace std;

        class Stack {
            queue<int> q1, q2;         // q1 holds the items, newest at the front
        public:
            void push(int x) {
                q2.push(x);                                            // a) x goes in first ...
                while (!q1.empty()) { q2.push(q1.front()); q1.pop(); } // b) ... older items behind it
                swap(q1, q2);                                          // c) q1 holds the items again
            }
            int pop() { int x = q1.front(); q1.pop(); return x; }     // front of q1 is the newest item
            int top() const { return q1.front(); }
            int size() const { return (int)q1.size(); }
            bool isEmpty() const { return q1.empty(); }
        };

        int main() {
            Stack s;
            s.push(10);
            s.push(20);
            s.push(30);
            cout << "top: " << s.top() << "\\n";
            cout << "popped: " << s.pop() << "\\n";
            cout << "top: " << s.top() << "\\n";
            cout << "size: " << s.size() << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {
            static class Stack {
                Queue<Integer> q1 = new ArrayDeque<>();   // holds the items, newest at the front
                Queue<Integer> q2 = new ArrayDeque<>();   // auxiliary
                void push(int x) {
                    q2.offer(x);                                   // a) x goes in first ...
                    while (!q1.isEmpty()) q2.offer(q1.poll());     // b) ... older items behind it
                    Queue<Integer> tmp = q1; q1 = q2; q2 = tmp;    // c) swap
                }
                int pop() { return q1.poll(); }                    // front of q1 is the newest item
                int top() { return q1.peek(); }
                int size() { return q1.size(); }
                boolean isEmpty() { return q1.isEmpty(); }
            }

            public static void main(String[] args) {
                Stack s = new Stack();
                s.push(10);
                s.push(20);
                s.push(30);
                System.out.println("top: " + s.top());
                System.out.println("popped: " + s.pop());
                System.out.println("top: " + s.top());
                System.out.println("size: " + s.size());
            }
        }
    ''', js='''
        class Stack {
            constructor() {
                this.q1 = [];          // holds the items, newest at the front
                this.q2 = [];          // auxiliary
            }
            push(x) {
                this.q2.push(x);                                   // a) x goes in first ...
                while (this.q1.length) this.q2.push(this.q1.shift()); // b) ... older items behind it
                [this.q1, this.q2] = [this.q2, this.q1];           // c) swap
            }
            pop() { return this.q1.shift(); }                      // front of q1 is the newest item
            top() { return this.q1[0]; }
            size() { return this.q1.length; }
            isEmpty() { return this.q1.length === 0; }
        }

        const s = new Stack();
        s.push(10);
        s.push(20);
        s.push(30);
        console.log("top:", s.top());
        console.log("popped:", s.pop());
        console.log("top:", s.top());
        console.log("size:", s.size());
    ''')
    yield complexity("push O(n), pop/top O(1)", "O(n)")
    yield note("**One queue is enough**: enqueue `x`, then dequeue-and-re-enqueue the other `size − 1` elements so `x` rotates to the front. Same O(n) push, no auxiliary queue. The mirror design — cheap push, O(n) pop that rotates all but the last element — is also valid; pick the one that matches which operation is more frequent.")

    yield section("Problem: implement a queue using two stacks", "arrows-shuffle")
    yield io("enqueue(10), enqueue(20), enqueue(30), dequeue(), dequeue(), enqueue(40), front()", "10, 20, 30")
    yield idea("Two LIFO reversals make a FIFO. Push every new element onto `inbox`. To dequeue, pop from `outbox`; when `outbox` is empty, pour all of `inbox` into it first — popping and pushing reverses the order, so the oldest element ends up on top of `outbox`.")
    yield steps(
        ("enqueue(x)", "`inbox.push(x)` — O(1)."),
        ("dequeue() / front()", "If `outbox` is empty, move every element from `inbox` to `outbox` (pop one, push the other). Then pop / peek `outbox`."),
        ("Why not pour every time?", "Only pour when `outbox` is empty. Elements already in `outbox` are older than anything in `inbox`, so the order stays correct, and each element is moved at most once."),
    )
    yield multi('''
        front: 10
        dequeued: 10
        dequeued: 20
        front: 30
        size: 2
    ''', py='''
        class Queue:
            def __init__(self):
                self.inbox = []        # enqueue pushes here
                self.outbox = []       # dequeue pops from here (reversed = FIFO order)

            def enqueue(self, x):
                self.inbox.append(x)

            def _pour(self):
                if not self.outbox:                    # only when outbox is empty
                    while self.inbox:
                        self.outbox.append(self.inbox.pop())

            def dequeue(self):
                self._pour()
                return self.outbox.pop()

            def front(self):
                self._pour()
                return self.outbox[-1]

            def size(self):
                return len(self.inbox) + len(self.outbox)

        q = Queue()
        for x in (10, 20, 30):
            q.enqueue(x)
        print("front:", q.front())
        print("dequeued:", q.dequeue())
        print("dequeued:", q.dequeue())
        q.enqueue(40)
        print("front:", q.front())
        print("size:", q.size())
    ''', cpp='''
        #include <iostream>
        #include <stack>
        using namespace std;

        class Queue {
            stack<int> inbox, outbox;  // enqueue pushes to inbox; dequeue pops from outbox
            void pour() {
                if (outbox.empty())                              // only when outbox is empty
                    while (!inbox.empty()) { outbox.push(inbox.top()); inbox.pop(); }
            }
        public:
            void enqueue(int x) { inbox.push(x); }
            int dequeue() { pour(); int x = outbox.top(); outbox.pop(); return x; }
            int front() { pour(); return outbox.top(); }
            int size() const { return (int)(inbox.size() + outbox.size()); }
        };

        int main() {
            Queue q;
            for (int x : {10, 20, 30}) q.enqueue(x);
            cout << "front: " << q.front() << "\\n";
            cout << "dequeued: " << q.dequeue() << "\\n";
            cout << "dequeued: " << q.dequeue() << "\\n";
            q.enqueue(40);
            cout << "front: " << q.front() << "\\n";
            cout << "size: " << q.size() << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Queue {
                Deque<Integer> inbox = new ArrayDeque<>();    // enqueue pushes here
                Deque<Integer> outbox = new ArrayDeque<>();   // dequeue pops from here
                void enqueue(int x) { inbox.push(x); }
                void pour() {
                    if (outbox.isEmpty())                     // only when outbox is empty
                        while (!inbox.isEmpty()) outbox.push(inbox.pop());
                }
                int dequeue() { pour(); return outbox.pop(); }
                int front() { pour(); return outbox.peek(); }
                int size() { return inbox.size() + outbox.size(); }
            }

            public static void main(String[] args) {
                Queue q = new Queue();
                for (int x : new int[]{10, 20, 30}) q.enqueue(x);
                System.out.println("front: " + q.front());
                System.out.println("dequeued: " + q.dequeue());
                System.out.println("dequeued: " + q.dequeue());
                q.enqueue(40);
                System.out.println("front: " + q.front());
                System.out.println("size: " + q.size());
            }
        }
    ''', js='''
        class Queue {
            constructor() {
                this.inbox = [];       // enqueue pushes here
                this.outbox = [];      // dequeue pops from here (reversed = FIFO order)
            }
            enqueue(x) { this.inbox.push(x); }
            pour() {
                if (this.outbox.length === 0)                  // only when outbox is empty
                    while (this.inbox.length) this.outbox.push(this.inbox.pop());
            }
            dequeue() { this.pour(); return this.outbox.pop(); }
            front() { this.pour(); return this.outbox[this.outbox.length - 1]; }
            size() { return this.inbox.length + this.outbox.length; }
        }

        const q = new Queue();
        for (const x of [10, 20, 30]) q.enqueue(x);
        console.log("front:", q.front());
        console.log("dequeued:", q.dequeue());
        console.log("dequeued:", q.dequeue());
        q.enqueue(40);
        console.log("front:", q.front());
        console.log("size:", q.size());
    ''')
    yield complexity("amortised O(1) per operation", "O(n)")
    yield pitfall("Pouring `inbox` into `outbox` while `outbox` still has elements breaks the order: the poured (newer) elements would land on top of older ones. Pour **only when `outbox` is empty**. Each element is pushed and popped at most twice, which is why the amortised cost is O(1) even though one dequeue can be O(n).")

    yield section("Interview Q&A", "message-question")
    yield qa("Stack vs queue — when do you use which?",
             "A stack (LIFO) when the most recent thing matters: function calls, undo, bracket matching, DFS. A queue (FIFO) when arrival order matters: scheduling, buffering, BFS / level-order traversal. Both have O(1) insert and remove; the only difference is which end you remove from.")
    yield qa("Why is a circular array better than a plain array for a queue?",
             "A plain array either shifts all elements on every dequeue (O(n)) or wastes every slot it has dequeued, failing with a *full* error while most of the array is empty. Wrapping `front` and `rear` with `% capacity` lets freed slots be reused, so every operation is O(1) and all `capacity` slots are usable.")
    yield qa("In a circular queue front == rear — is it empty or full?",
             "Either, so the indices alone are ambiguous. Two standard fixes: keep a `size` counter (empty when `size == 0`, full when `size == capacity`), or sacrifice one slot and declare the queue full when `(rear + 1) % capacity == front`.")
    yield qa("Why not use a Python list or a JavaScript array as a queue?",
             "`list.pop(0)` and `Array.shift()` remove the first element by shifting every other element left — O(n) per dequeue, O(n²) for a loop that drains the queue. Use `collections.deque` (O(1) `popleft`) in Python; in JavaScript write a small linked-list or two-pointer queue (or keep a `head` index into the array) for anything large, e.g. BFS over a big graph.")
    yield qa("How do you implement a queue with two stacks, and what is the complexity?",
             "Push into `inbox`. To dequeue, if `outbox` is empty pour everything from `inbox` into `outbox` (which reverses it), then pop `outbox`. A single dequeue can cost O(n), but each element is moved at most once, so `n` operations cost O(n) in total — amortised O(1).")
    yield qa("What is a priority queue, and how does it differ from a queue?",
             "A queue serves elements in arrival order; a priority queue serves the element with the highest (or lowest) priority first, regardless of arrival. It is normally built on a binary heap: O(log n) insert and remove-top, O(1) peek. A deque is a different variation — a queue that allows insertion and removal at *both* ends.")


@topic(G, "deque", "Deque", "arrows-horizontal")
def _():
    yield lead("A deque (*double-ended queue*, pronounced “deck”) lets you insert and delete at **both** ends in O(1). It is a stack and a queue in one container, and the workhorse behind sliding-window problems, undo histories and work-stealing schedulers.")
    yield define("Deque", "a linear data structure that generalises the stack and the queue: elements can be added or removed at the front and at the rear, all in O(1). Access to the middle may or may not be supported depending on the implementation.")
    yield diagram('''
        insertFront(x) ──▶  ┌────┬────┬────┬────┐  ◀── insertRear(x)
        deleteFront()  ◀──  │ 10 │ 20 │ 30 │ 40 │  ──▶ deleteRear()
                            └────┴────┴────┴────┘
                              ↑              ↑
                            front           rear

        use only the rear  →  a stack   (push = insertRear, pop = deleteRear)
        rear in, front out →  a queue   (enqueue = insertRear, dequeue = deleteFront)
    ''', "A deque is a queue whose both ends are open — restrict yourself to one pattern and you get a stack or a queue")

    yield section("Operations", "list-check")
    yield table(
        ["Operation", "What it does", "Time"],
        ["`insertFront(x)`", "Add `x` before the current front", "O(1)"],
        ["`insertRear(x)`", "Add `x` after the current rear", "O(1)"],
        ["`deleteFront()`", "Remove and return the front element", "O(1)"],
        ["`deleteRear()`", "Remove and return the rear element", "O(1)"],
        ["`getFront()` / `getRear()`", "Peek at either end", "O(1)"],
        ["`isEmpty()` / `isFull()`", "Empty check; `isFull()` only for fixed-capacity deques", "O(1)"],
        ["`size()`", "Number of elements", "O(1)"],
    )
    yield p("The same operations have different names in every library — this table is worth memorising, because it is also the stack and queue API of each language:")
    yield table(
        ["", "Python `collections.deque`", "C++ `std::deque`", "Java `ArrayDeque` (`Deque<T>`)", "JavaScript `Array`"],
        ["insertFront", "`appendleft(x)`", "`push_front(x)`", "`offerFirst(x)` / `addFirst(x)` / `push(x)`", "`unshift(x)` — O(n)"],
        ["insertRear", "`append(x)`", "`push_back(x)`", "`offerLast(x)` / `addLast(x)` / `offer(x)`", "`push(x)`"],
        ["deleteFront", "`popleft()`", "`pop_front()`", "`pollFirst()` / `removeFirst()` / `pop()` / `poll()`", "`shift()` — O(n)"],
        ["deleteRear", "`pop()`", "`pop_back()`", "`pollLast()` / `removeLast()`", "`pop()`"],
        ["getFront / getRear", "`d[0]` / `d[-1]`", "`front()` / `back()`", "`peekFirst()` / `peekLast()`", "`a[0]` / `a[a.length - 1]`"],
    )
    yield warn("JavaScript has no built-in deque. `unshift()` and `shift()` re-index the whole array, so they are O(n). For small inputs that is fine; for sliding windows over large arrays, implement a deque yourself (circular array or doubly linked list — both below) or keep two indices into a plain array.")

    yield section("Where deques are used", "apps")
    yield cards(
        ("Stack and queue in one", "A deque does everything both do, so one implementation (Python's `deque`, Java's `ArrayDeque`) serves as the standard stack *and* the standard queue.", "stack-2"),
        ("History of actions", "Browser history, undo buffers, “recently used” lists: push new actions at one end, drop the oldest from the other when the history is full (`deque(maxlen=n)` does this automatically).", "history"),
        ("Work-stealing schedulers", "Each worker thread keeps its tasks in a deque: it pushes and pops at the rear (LIFO, cache-warm); idle threads *steal* from the front (the oldest, largest tasks). Used by Java's ForkJoinPool and Go's runtime.", "cpu"),
        ("Two-level priority queue", "Urgent items go to the front, normal items to the rear, always serve the front — a priority queue with exactly two priorities, as in 0-1 BFS on graphs with edge weights 0 and 1.", "arrows-sort"),
        ("Sliding window maximum / minimum", "Maximum of every subarray of size `k` in O(n): the deque keeps candidate indices in decreasing order of value — see **DSA Advanced → Sliding Window**.", "chart-bar"),
        ("Palindromes and symmetry checks", "Compare the two ends and remove both until the middle is reached — solved below.", "arrows-left-right"),
        cols=3,
    )

    yield section("Using the built-in containers", "box")
    yield multi('''
        10 20 30
        100 10 20 30
        100 10 20
        10 20
        front: 10 rear: 20
    ''', py='''
        from collections import deque

        def show(d):
            print(*d)

        d = deque()
        d.append(10)            # insert at the rear
        d.append(20)
        d.append(30)
        show(d)
        d.appendleft(100)       # insert at the front
        show(d)
        d.pop()                 # delete from the rear
        show(d)
        d.popleft()             # delete from the front
        show(d)
        print("front:", d[0], "rear:", d[-1])
    ''', cpp='''
        #include <deque>
        #include <iostream>
        using namespace std;

        void show(const deque<int>& d) {
            for (size_t i = 0; i < d.size(); i++) cout << (i ? " " : "") << d[i];   // deque allows d[i]
            cout << "\\n";
        }

        int main() {
            deque<int> d;
            d.push_back(10);        // insert at the rear
            d.push_back(20);
            d.push_back(30);
            show(d);
            d.push_front(100);      // insert at the front
            show(d);
            d.pop_back();           // delete from the rear
            show(d);
            d.pop_front();          // delete from the front
            show(d);
            cout << "front: " << d.front() << " rear: " << d.back() << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static void show(Deque<Integer> d) {
                StringBuilder sb = new StringBuilder();
                for (int v : d) sb.append(sb.length() == 0 ? "" : " ").append(v);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Deque<Integer> d = new ArrayDeque<>();   // preferred over LinkedList
                d.addLast(10);          // insert at the rear
                d.addLast(20);
                d.addLast(30);
                show(d);
                d.addFirst(100);        // insert at the front
                show(d);
                d.removeLast();         // delete from the rear
                show(d);
                d.removeFirst();        // delete from the front
                show(d);
                System.out.println("front: " + d.peekFirst() + " rear: " + d.peekLast());
            }
        }
    ''', js='''
        const show = (d) => console.log(d.join(" "));

        const d = [];               // an array used as a deque
        d.push(10);                 // insert at the rear
        d.push(20);
        d.push(30);
        show(d);
        d.unshift(100);             // insert at the front — O(n) on an array
        show(d);
        d.pop();                    // delete from the rear
        show(d);
        d.shift();                  // delete from the front — O(n) on an array
        show(d);
        console.log("front:", d[0], "rear:", d[d.length - 1]);
    ''')
    yield p("Python's `deque` also has a handful of list-like extras. They are convenient, but note which of them walk the whole structure (next section).")
    yield code('''
        from collections import deque

        d = deque([10, 20, 30, 40])
        d.insert(2, 15)
        print(list(d))          # [10, 20, 15, 30, 40]
        print(d.count(10))      # 1
        d.remove(10)            # removes the first occurrence
        print(list(d))          # [20, 15, 30, 40]
        d.extend([50, 60])
        print(list(d))          # [20, 15, 30, 40, 50, 60]
        d.extendleft([10, 20])
        print(list(d))          # [20, 10, 20, 15, 30, 40, 50, 60]   ← appendleft one by one, so the order flips
        d.reverse()
        print(list(d))          # [60, 50, 40, 30, 15, 20, 10, 20]
    ''')
    yield code('''
        from collections import deque

        d = deque([10, 20, 30, 40, 50])
        d.rotate(2)             # positive: the last 2 elements move to the front
        print(list(d))          # [40, 50, 10, 20, 30]
        d.rotate(-2)            # negative: the first 2 elements move to the back
        print(list(d))          # [10, 20, 30, 40, 50]
        print(d[2])             # 30   ← indexing works, but the middle is O(n)
        d[2] = 100
        print(list(d))          # [10, 20, 100, 40, 50]
        print(d[0], d[-1])      # 10 50

        history = deque(maxlen=3)        # bounded: a full deque drops the opposite end
        for x in (1, 2, 3, 4):
            history.append(x)
        print(list(history))    # [2, 3, 4]   ← 1 fell off the front
    ''')
    yield pitfall("`extendleft([10, 20])` produces `20, 10, …` — it calls `appendleft` for each element in turn, so the sequence appears reversed. Pass `reversed(items)` if you want to keep their order.")

    yield section("Time complexities and internal working", "clock")
    yield table(
        ["Complexity", "Python `deque` operations", "Why"],
        ["O(1)", "`append`, `appendleft`, `pop`, `popleft`, `len`, `d[0]`, `d[-1]`", "both ends are directly reachable"],
        ["O(n)", "`d[i]` in the middle, `count(x)`, `insert(i, x)`, `remove(x)`, `x in d`, `reverse()`", "must walk the blocks from one end"],
        ["O(min(k, n − k))", "`rotate(k)`", "moves `k` elements one by one, going the shorter way round"],
        ["O(len(l))", "`extend(l)`, `extendleft(l)`", "one `append` / `appendleft` per element"],
    )
    yield p("CPython's `deque` is a **doubly linked list of fixed-size blocks** (64 slots each). The ends live in the leftmost and rightmost blocks, so pushing or popping at either end touches one slot and occasionally allocates or frees one block; walking to `d[i]` means hopping `i // 64` blocks, hence O(n) in the middle.")
    yield diagram('''
        collections.deque — a doubly linked list of 64-slot blocks

           leftblock               ...                 rightblock
          ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
          │ · · · 10 20 30│◀──▶│ 40 50 … … 90  │◀──▶│ 100 110 · · · │
          └───────────────┘    └───────────────┘    └───────────────┘
                 ↑ leftindex                             ↑ rightindex

          appendleft / popleft move leftindex   → O(1)
          append / pop move rightindex          → O(1)
          d[i] hops i // 64 blocks              → O(n) in the middle
    ''', "Why both ends are O(1) but the middle is not")
    yield table(
        ["Library", "Internal structure", "Both ends", "Random access `d[i]`"],
        ["Python `collections.deque`", "doubly linked list of 64-slot blocks", "O(1)", "O(n) in the middle, O(1) near the ends"],
        ["C++ `std::deque`", "array of pointers to fixed-size chunks (“map of blocks”)", "O(1)", "O(1) — two lookups"],
        ["Java `ArrayDeque`", "circular, growable array (doubles when full)", "amortised O(1)", "not supported (no `get(i)`)"],
        ["Java `LinkedList`", "doubly linked list of nodes", "O(1)", "O(n)"],
    )
    yield note("`std::deque` is the one standard deque with O(1) indexing, which is why `std::stack` and `std::queue` adapt it by default. Java's `ArrayDeque` is faster and leaner than `LinkedList` for stack/queue work (one array, no per-node objects) but refuses `null` elements.")

    yield section("Implementing a deque with a doubly linked list", "link")
    yield p("A **singly** linked list gives O(1) at the head and, with a tail pointer, O(1) `insertRear` — but `deleteRear` needs the node *before* the tail, which only a walk from the head can find: O(n). A **doubly** linked list stores a `prev` pointer in every node, so `tail = tail.prev` is one step and every deque operation is O(1).")
    yield diagram('''
        head (front)                                        tail (rear)
         ↓                                                   ↓
        ┌───┬────┬───┐     ┌───┬────┬───┐     ┌───┬────┬───┐
        │ ∅ │ 10 │ ●─┼────▶│ ● │ 20 │ ●─┼────▶│ ● │ 30 │ ∅ │
        │   │    │   │◀────┼─● │    │   │◀────┼─● │    │   │
        └───┴────┴───┘     └───┴────┴───┘     └───┴────┴───┘
        prev value next

        deleteRear(): tail = tail.prev; tail.next = ∅         ← O(1) thanks to prev
        insertFront(x): node.next = head; head.prev = node; head = node
    ''', "Each node knows both neighbours, so either end can be removed without a search")
    yield steps(
        ("insertFront(x) / insertRear(x)", "Create a node. If empty, `head = tail = node`. Otherwise link it before `head` (set `node.next`, `head.prev`, `head`) or after `tail` (set `node.prev`, `tail.next`, `tail`)."),
        ("deleteFront() / deleteRear()", "Advance `head = head.next` (or `tail = tail.prev`). If the deque became empty set the *other* pointer to `null` too; otherwise clear the new end's dangling `prev` (or `next`)."),
        ("Both empty cases matter", "The original notes did `head = head.next; head.prev = None` without checking — deleting the last element then crashes on `None.prev`. Guard it."),
    )
    yield io("insertRear 10 20 30; deleteFront; deleteRear; insertFront 100, 1000", "front/rear: 10/30 → 20/30 → 20/20; final order 1000 100 20")
    yield multi('''
        front: 10 rear: 30
        deleteFront → front: 20 rear: 30
        deleteRear → front: 20 rear: 20
        size: 1 empty: False
        1000 100 20
    ''', py='''
        class Node:
            def __init__(self, value):
                self.value = value
                self.prev = None
                self.next = None

        class Deque:
            def __init__(self):
                self.head = None       # front
                self.tail = None       # rear
                self.size = 0

            def is_empty(self):
                return self.size == 0

            def insert_front(self, value):
                node = Node(value)
                if self.is_empty():
                    self.head = self.tail = node
                else:
                    node.next = self.head
                    self.head.prev = node
                    self.head = node
                self.size += 1

            def insert_rear(self, value):
                node = Node(value)
                if self.is_empty():
                    self.head = self.tail = node
                else:
                    node.prev = self.tail
                    self.tail.next = node
                    self.tail = node
                self.size += 1

            def delete_front(self):
                if self.is_empty():
                    raise IndexError("deque is empty")
                value = self.head.value
                self.head = self.head.next
                if self.head is None:          # became empty
                    self.tail = None
                else:
                    self.head.prev = None
                self.size -= 1
                return value

            def delete_rear(self):
                if self.is_empty():
                    raise IndexError("deque is empty")
                value = self.tail.value
                self.tail = self.tail.prev     # O(1) thanks to prev
                if self.tail is None:          # became empty
                    self.head = None
                else:
                    self.tail.next = None
                self.size -= 1
                return value

            def get_front(self):
                return None if self.is_empty() else self.head.value

            def get_rear(self):
                return None if self.is_empty() else self.tail.value

            def display(self):
                node, parts = self.head, []
                while node:
                    parts.append(str(node.value))
                    node = node.next
                print(" ".join(parts))

        d = Deque()
        for x in (10, 20, 30):
            d.insert_rear(x)
        print("front:", d.get_front(), "rear:", d.get_rear())
        d.delete_front()
        print("deleteFront → front:", d.get_front(), "rear:", d.get_rear())
        d.delete_rear()
        print("deleteRear → front:", d.get_front(), "rear:", d.get_rear())
        print("size:", d.size, "empty:", d.is_empty())
        d.insert_front(100)
        d.insert_front(1000)
        d.display()
    ''', cpp='''
        #include <iostream>
        #include <stdexcept>
        using namespace std;

        struct Node {
            int value;
            Node* prev;
            Node* next;
            Node(int v) : value(v), prev(nullptr), next(nullptr) {}
        };

        class Deque {
            Node* head = nullptr;      // front
            Node* tail = nullptr;      // rear
            int count = 0;
        public:
            ~Deque() { while (head) deleteFront(); }
            bool isEmpty() const { return count == 0; }
            int size() const { return count; }
            void insertFront(int v) {
                Node* node = new Node(v);
                if (isEmpty()) head = tail = node;
                else { node->next = head; head->prev = node; head = node; }
                count++;
            }
            void insertRear(int v) {
                Node* node = new Node(v);
                if (isEmpty()) head = tail = node;
                else { node->prev = tail; tail->next = node; tail = node; }
                count++;
            }
            int deleteFront() {
                if (isEmpty()) throw runtime_error("deque is empty");
                Node* node = head;
                int v = node->value;
                head = head->next;
                if (!head) tail = nullptr;             // became empty
                else head->prev = nullptr;
                delete node;
                count--;
                return v;
            }
            int deleteRear() {
                if (isEmpty()) throw runtime_error("deque is empty");
                Node* node = tail;
                int v = node->value;
                tail = tail->prev;                     // O(1) thanks to prev
                if (!tail) head = nullptr;             // became empty
                else tail->next = nullptr;
                delete node;
                count--;
                return v;
            }
            int getFront() const { return head->value; }
            int getRear() const { return tail->value; }
            void display() const {
                for (Node* n = head; n; n = n->next) cout << n->value << (n->next ? " " : "");
                cout << "\\n";
            }
        };

        int main() {
            Deque d;
            for (int x : {10, 20, 30}) d.insertRear(x);
            cout << "front: " << d.getFront() << " rear: " << d.getRear() << "\\n";
            d.deleteFront();
            cout << "deleteFront → front: " << d.getFront() << " rear: " << d.getRear() << "\\n";
            d.deleteRear();
            cout << "deleteRear → front: " << d.getFront() << " rear: " << d.getRear() << "\\n";
            cout << "size: " << d.size() << " empty: " << (d.isEmpty() ? "True" : "False") << "\\n";
            d.insertFront(100);
            d.insertFront(1000);
            d.display();
        }
    ''', java='''
        public class Main {
            static class Node {
                int value; Node prev, next;
                Node(int v) { value = v; }
            }

            static class Deque {
                Node head, tail;           // front, rear
                int size;
                boolean isEmpty() { return size == 0; }
                void insertFront(int v) {
                    Node node = new Node(v);
                    if (isEmpty()) head = tail = node;
                    else { node.next = head; head.prev = node; head = node; }
                    size++;
                }
                void insertRear(int v) {
                    Node node = new Node(v);
                    if (isEmpty()) head = tail = node;
                    else { node.prev = tail; tail.next = node; tail = node; }
                    size++;
                }
                int deleteFront() {
                    if (isEmpty()) throw new RuntimeException("deque is empty");
                    int v = head.value;
                    head = head.next;
                    if (head == null) tail = null;         // became empty
                    else head.prev = null;
                    size--;
                    return v;
                }
                int deleteRear() {
                    if (isEmpty()) throw new RuntimeException("deque is empty");
                    int v = tail.value;
                    tail = tail.prev;                      // O(1) thanks to prev
                    if (tail == null) head = null;         // became empty
                    else tail.next = null;
                    size--;
                    return v;
                }
                Integer getFront() { return isEmpty() ? null : head.value; }
                Integer getRear() { return isEmpty() ? null : tail.value; }
                void display() {
                    StringBuilder sb = new StringBuilder();
                    for (Node n = head; n != null; n = n.next) sb.append(n.value).append(n.next != null ? " " : "");
                    System.out.println(sb);
                }
            }

            public static void main(String[] args) {
                Deque d = new Deque();
                for (int x : new int[]{10, 20, 30}) d.insertRear(x);
                System.out.println("front: " + d.getFront() + " rear: " + d.getRear());
                d.deleteFront();
                System.out.println("deleteFront → front: " + d.getFront() + " rear: " + d.getRear());
                d.deleteRear();
                System.out.println("deleteRear → front: " + d.getFront() + " rear: " + d.getRear());
                System.out.println("size: " + d.size + " empty: " + (d.isEmpty() ? "True" : "False"));
                d.insertFront(100);
                d.insertFront(1000);
                d.display();
            }
        }
    ''', js='''
        class Node {
            constructor(value) { this.value = value; this.prev = null; this.next = null; }
        }

        class Deque {
            constructor() { this.head = null; this.tail = null; this.size = 0; }   // front, rear
            isEmpty() { return this.size === 0; }
            insertFront(value) {
                const node = new Node(value);
                if (this.isEmpty()) this.head = this.tail = node;
                else { node.next = this.head; this.head.prev = node; this.head = node; }
                this.size++;
            }
            insertRear(value) {
                const node = new Node(value);
                if (this.isEmpty()) this.head = this.tail = node;
                else { node.prev = this.tail; this.tail.next = node; this.tail = node; }
                this.size++;
            }
            deleteFront() {
                if (this.isEmpty()) throw new Error("deque is empty");
                const value = this.head.value;
                this.head = this.head.next;
                if (this.head === null) this.tail = null;      // became empty
                else this.head.prev = null;
                this.size--;
                return value;
            }
            deleteRear() {
                if (this.isEmpty()) throw new Error("deque is empty");
                const value = this.tail.value;
                this.tail = this.tail.prev;                    // O(1) thanks to prev
                if (this.tail === null) this.head = null;      // became empty
                else this.tail.next = null;
                this.size--;
                return value;
            }
            getFront() { return this.isEmpty() ? null : this.head.value; }
            getRear() { return this.isEmpty() ? null : this.tail.value; }
            display() {
                const parts = [];
                for (let n = this.head; n; n = n.next) parts.push(n.value);
                console.log(parts.join(" "));
            }
        }

        const d = new Deque();
        for (const x of [10, 20, 30]) d.insertRear(x);
        console.log("front:", d.getFront(), "rear:", d.getRear());
        d.deleteFront();
        console.log("deleteFront → front:", d.getFront(), "rear:", d.getRear());
        d.deleteRear();
        console.log("deleteRear → front:", d.getFront(), "rear:", d.getRear());
        console.log("size:", d.size, "empty:", d.isEmpty() ? "True" : "False");
        d.insertFront(100);
        d.insertFront(1000);
        d.display();
    ''')
    yield complexity("O(1) per operation", "O(n) for n elements")

    yield section("Implementing a deque with a circular array", "repeat")
    yield p("The circular-array queue extends naturally: `insertFront` steps `front` **backwards** (wrapping from 0 to `cap − 1`), `insertRear` fills the slot after the rear (wrapping from `cap − 1` to 0). Keeping `front` and `size` is enough — the rear index is always `(front + size − 1) % cap`, and `size` disambiguates empty from full.")
    yield diagram('''
        capacity 5: insertFront(10), insertFront(20), insertFront(30), insertRear(40), insertRear(50)

          index:   0     1     2     3     4
                ┌─────┬─────┬─────┬─────┬─────┐
                │ 40  │ 50  │ 30  │ 20  │ 10  │
                └─────┴─────┴─────┴─────┴─────┘
                               ↑ front = 2        rear = (front + size − 1) % 5 = 1

          insertFront moves front backwards:  0 → 4 (10) → 3 (20) → 2 (30)   wraps to the end
          insertRear fills the slot after rear: 4 → 0 (40) → 1 (50)          wraps to the start
          logical order (front → rear):  30  20  10  40  50
    ''', "Both ends wrap; the physical array order differs from the logical order")
    yield io("capacity = 5; insertFront 10 20 30; insertRear 40 50; deleteFront; deleteRear", "order 30 20 10 40 50 → after deletes 20 10 40")
    yield multi('''
        in order: 30 20 10 40 50
        slots: 40 50 30 20 10
        front = 2 size = 5
        full: True
        deleteFront → 30
        deleteRear → 50
        in order: 20 10 40
        front: 20 rear: 40
    ''', py='''
        class ArrayDeque:
            def __init__(self, capacity):
                self.slots = [None] * capacity
                self.cap = capacity
                self.front = 0        # index of the first element
                self.size = 0         # rear index is derived: (front + size - 1) % cap

            def is_empty(self):
                return self.size == 0

            def is_full(self):
                return self.size == self.cap

            def insert_front(self, value):
                if self.is_full():
                    raise OverflowError("deque is full")
                self.front = (self.front - 1 + self.cap) % self.cap   # step back, wrapping to the end
                self.slots[self.front] = value
                self.size += 1

            def insert_rear(self, value):
                if self.is_full():
                    raise OverflowError("deque is full")
                self.slots[(self.front + self.size) % self.cap] = value   # next free slot after rear
                self.size += 1

            def delete_front(self):
                if self.is_empty():
                    raise IndexError("deque is empty")
                value = self.slots[self.front]
                self.front = (self.front + 1) % self.cap
                self.size -= 1
                return value

            def delete_rear(self):
                if self.is_empty():
                    raise IndexError("deque is empty")
                value = self.slots[(self.front + self.size - 1) % self.cap]
                self.size -= 1                                # rear simply moves back by one
                return value

            def get_front(self):
                return self.slots[self.front]

            def get_rear(self):
                return self.slots[(self.front + self.size - 1) % self.cap]

            def in_order(self):
                return [self.slots[(self.front + i) % self.cap] for i in range(self.size)]

        d = ArrayDeque(5)
        for x in (10, 20, 30):
            d.insert_front(x)
        for x in (40, 50):
            d.insert_rear(x)
        print("in order:", *d.in_order())
        print("slots:", *d.slots)
        print("front =", d.front, "size =", d.size)
        print("full:", d.is_full())
        print("deleteFront →", d.delete_front())
        print("deleteRear →", d.delete_rear())
        print("in order:", *d.in_order())
        print("front:", d.get_front(), "rear:", d.get_rear())
    ''', cpp='''
        #include <iostream>
        #include <stdexcept>
        #include <vector>
        using namespace std;

        class ArrayDeque {
        public:
            vector<int> slots;
            int cap, front = 0, size = 0;    // rear index is derived: (front + size - 1) % cap
            ArrayDeque(int capacity) : slots(capacity, 0), cap(capacity) {}
            bool isEmpty() const { return size == 0; }
            bool isFull() const { return size == cap; }
            void insertFront(int v) {
                if (isFull()) throw runtime_error("deque is full");
                front = (front - 1 + cap) % cap;              // step back, wrapping to the end
                slots[front] = v;
                size++;
            }
            void insertRear(int v) {
                if (isFull()) throw runtime_error("deque is full");
                slots[(front + size) % cap] = v;              // next free slot after rear
                size++;
            }
            int deleteFront() {
                if (isEmpty()) throw runtime_error("deque is empty");
                int v = slots[front];
                front = (front + 1) % cap;
                size--;
                return v;
            }
            int deleteRear() {
                if (isEmpty()) throw runtime_error("deque is empty");
                int v = slots[(front + size - 1) % cap];
                size--;                                       // rear simply moves back by one
                return v;
            }
            int getFront() const { return slots[front]; }
            int getRear() const { return slots[(front + size - 1) % cap]; }
            void printInOrder() const {
                cout << "in order:";
                for (int i = 0; i < size; i++) cout << " " << slots[(front + i) % cap];
                cout << "\\n";
            }
        };

        int main() {
            ArrayDeque d(5);
            for (int x : {10, 20, 30}) d.insertFront(x);
            for (int x : {40, 50}) d.insertRear(x);
            d.printInOrder();
            cout << "slots:";
            for (int v : d.slots) cout << " " << v;
            cout << "\\n";
            cout << "front = " << d.front << " size = " << d.size << "\\n";
            cout << "full: " << (d.isFull() ? "True" : "False") << "\\n";
            cout << "deleteFront → " << d.deleteFront() << "\\n";
            cout << "deleteRear → " << d.deleteRear() << "\\n";
            d.printInOrder();
            cout << "front: " << d.getFront() << " rear: " << d.getRear() << "\\n";
        }
    ''', java='''
        public class Main {
            static class ArrayDeque {
                int[] slots;
                int cap, front = 0, size = 0;    // rear index is derived: (front + size - 1) % cap
                ArrayDeque(int capacity) { slots = new int[capacity]; cap = capacity; }
                boolean isEmpty() { return size == 0; }
                boolean isFull() { return size == cap; }
                void insertFront(int v) {
                    if (isFull()) throw new RuntimeException("deque is full");
                    front = (front - 1 + cap) % cap;          // step back, wrapping to the end
                    slots[front] = v;
                    size++;
                }
                void insertRear(int v) {
                    if (isFull()) throw new RuntimeException("deque is full");
                    slots[(front + size) % cap] = v;          // next free slot after rear
                    size++;
                }
                int deleteFront() {
                    if (isEmpty()) throw new RuntimeException("deque is empty");
                    int v = slots[front];
                    front = (front + 1) % cap;
                    size--;
                    return v;
                }
                int deleteRear() {
                    if (isEmpty()) throw new RuntimeException("deque is empty");
                    int v = slots[(front + size - 1) % cap];
                    size--;                                   // rear simply moves back by one
                    return v;
                }
                int getFront() { return slots[front]; }
                int getRear() { return slots[(front + size - 1) % cap]; }
                void printInOrder() {
                    StringBuilder sb = new StringBuilder("in order:");
                    for (int i = 0; i < size; i++) sb.append(' ').append(slots[(front + i) % cap]);
                    System.out.println(sb);
                }
            }

            public static void main(String[] args) {
                ArrayDeque d = new ArrayDeque(5);
                for (int x : new int[]{10, 20, 30}) d.insertFront(x);
                for (int x : new int[]{40, 50}) d.insertRear(x);
                d.printInOrder();
                StringBuilder sb = new StringBuilder("slots:");
                for (int v : d.slots) sb.append(' ').append(v);
                System.out.println(sb);
                System.out.println("front = " + d.front + " size = " + d.size);
                System.out.println("full: " + (d.isFull() ? "True" : "False"));
                System.out.println("deleteFront → " + d.deleteFront());
                System.out.println("deleteRear → " + d.deleteRear());
                d.printInOrder();
                System.out.println("front: " + d.getFront() + " rear: " + d.getRear());
            }
        }
    ''', js='''
        class ArrayDeque {
            constructor(capacity) {
                this.slots = new Array(capacity).fill(null);
                this.cap = capacity;
                this.front = 0;       // index of the first element
                this.size = 0;        // rear index is derived: (front + size - 1) % cap
            }
            isEmpty() { return this.size === 0; }
            isFull() { return this.size === this.cap; }
            insertFront(value) {
                if (this.isFull()) throw new Error("deque is full");
                this.front = (this.front - 1 + this.cap) % this.cap;   // step back, wrapping to the end
                this.slots[this.front] = value;
                this.size++;
            }
            insertRear(value) {
                if (this.isFull()) throw new Error("deque is full");
                this.slots[(this.front + this.size) % this.cap] = value;   // next free slot after rear
                this.size++;
            }
            deleteFront() {
                if (this.isEmpty()) throw new Error("deque is empty");
                const value = this.slots[this.front];
                this.front = (this.front + 1) % this.cap;
                this.size--;
                return value;
            }
            deleteRear() {
                if (this.isEmpty()) throw new Error("deque is empty");
                const value = this.slots[(this.front + this.size - 1) % this.cap];
                this.size--;                                  // rear simply moves back by one
                return value;
            }
            getFront() { return this.slots[this.front]; }
            getRear() { return this.slots[(this.front + this.size - 1) % this.cap]; }
            inOrder() {
                const out = [];
                for (let i = 0; i < this.size; i++) out.push(this.slots[(this.front + i) % this.cap]);
                return out;
            }
        }

        const d = new ArrayDeque(5);
        for (const x of [10, 20, 30]) d.insertFront(x);
        for (const x of [40, 50]) d.insertRear(x);
        console.log("in order:", d.inOrder().join(" "));
        console.log("slots:", d.slots.join(" "));
        console.log("front =", d.front, "size =", d.size);
        console.log("full:", d.isFull() ? "True" : "False");
        console.log("deleteFront →", d.deleteFront());
        console.log("deleteRear →", d.deleteRear());
        console.log("in order:", d.inOrder().join(" "));
        console.log("front:", d.getFront(), "rear:", d.getRear());
    ''')
    yield complexity("O(1) per operation", "O(cap)")
    yield pitfall("Stepping the front backwards as `front - 1` gives `-1` when `front == 0`. In C++/Java that is an out-of-bounds read; in Python `slots[-1]` silently hits the last slot *and* leaves `front` negative. Always write `(front - 1 + cap) % cap` — and avoid the `-1`-means-empty sentinel of the original notes, which needs four special cases per operation; a `size` counter needs none.")

    yield section("Array or linked list?", "scale")
    yield p("The original notes list the array version's advantages as “random access, supports all operations, cache friendly, O(1) time”. Here is the full comparison:")
    yield table(
        ["", "Circular array", "Doubly linked list"],
        ["Insert / delete at both ends", "O(1) (amortised O(1) if it grows by doubling)", "O(1)"],
        ["Random access `d[i]`", "O(1) — `slots[(front + i) % cap]`", "O(n)"],
        ["Memory", "one contiguous block, no per-element overhead; some unused capacity", "two pointers per node, scattered allocations"],
        ["Cache behaviour", "friendly — neighbours are adjacent in memory", "poor — every step is a pointer chase"],
        ["Capacity", "fixed, or resize by doubling (copy O(n), rarely)", "unbounded, never copies"],
        ["Used by", "Java `ArrayDeque`, C++ `std::deque` (chunked), Python `deque` (blocks)", "Java `LinkedList`"],
    )
    yield good("Default to the array-based deque of your language: it is faster in practice and supports indexing. Reach for a linked list only when you need stable node references (an element must keep its identity while others are added) or truly unbounded growth without copying.")

    yield section("Problem: check whether a string is a palindrome", "arrows-left-right")
    yield io("s = \"Nurses run\"", "Yes", "s = \"hello\"", "No")
    yield idea("Load the cleaned characters into a deque, then repeatedly compare and remove the two ends. A palindrome reads the same from both directions, so every pair must match until at most one character is left.")
    yield multi('''
        racecar → Yes
        Nurses run → Yes
        hello → No
        No lemon, no melon → Yes
    ''', py='''
        from collections import deque

        def is_palindrome(s):
            d = deque(ch.lower() for ch in s if ch.isalnum())   # ignore spaces, case, punctuation
            while len(d) > 1:
                if d.popleft() != d.pop():                        # compare both ends, O(1) each
                    return False
            return True

        for s in ["racecar", "Nurses run", "hello", "No lemon, no melon"]:
            print(s, "→", "Yes" if is_palindrome(s) else "No")
    ''', cpp='''
        #include <cctype>
        #include <deque>
        #include <iostream>
        #include <string>
        using namespace std;

        bool isPalindrome(const string& s) {
            deque<char> d;
            for (char ch : s)                                         // ignore spaces, case, punctuation
                if (isalnum((unsigned char)ch)) d.push_back((char)tolower((unsigned char)ch));
            while (d.size() > 1) {
                if (d.front() != d.back()) return false;              // compare both ends, O(1) each
                d.pop_front();
                d.pop_back();
            }
            return true;
        }

        int main() {
            for (string s : {"racecar", "Nurses run", "hello", "No lemon, no melon"})
                cout << s << " → " << (isPalindrome(s) ? "Yes" : "No") << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static boolean isPalindrome(String s) {
                Deque<Character> d = new ArrayDeque<>();
                for (char ch : s.toCharArray())                       // ignore spaces, case, punctuation
                    if (Character.isLetterOrDigit(ch)) d.addLast(Character.toLowerCase(ch));
                while (d.size() > 1) {
                    char a = d.pollFirst(), b = d.pollLast();         // unbox before comparing!
                    if (a != b) return false;                         // compare both ends, O(1) each
                }
                return true;
            }

            public static void main(String[] args) {
                for (String s : new String[]{"racecar", "Nurses run", "hello", "No lemon, no melon"})
                    System.out.println(s + " → " + (isPalindrome(s) ? "Yes" : "No"));
            }
        }
    ''', js='''
        function isPalindrome(s) {
            const d = [];
            for (const ch of s.toLowerCase())                         // ignore spaces, case, punctuation
                if (/[a-z0-9]/.test(ch)) d.push(ch);
            while (d.length > 1) {
                if (d.shift() !== d.pop()) return false;              // compare both ends (shift is O(n) on arrays)
            }
            return true;
        }

        for (const s of ["racecar", "Nurses run", "hello", "No lemon, no melon"])
            console.log(s, "→", isPalindrome(s) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n)")
    yield pitfall("In Java, `d.pollFirst() != d.pollLast()` compares two `Character` **objects by reference**. It happens to work for ASCII because of the small-value cache, and silently fails beyond it — unbox to `char` (or use `.equals`) first. In JavaScript the array `shift()` makes this O(n²); two indices `i`, `j` walking inwards give the same answer in O(n) with no deque at all.")
    yield note("The flagship deque problem — **maximum of every window of size k** in O(n) — keeps the deque sorted by value with indices, popping from the rear anything smaller than the new element and from the front anything that has left the window. It is worked through in **DSA Advanced → Sliding Window**.")

    yield section("Interview Q&A", "message-question")
    yield qa("What is a deque, and how does it relate to stacks and queues?",
             "A double-ended queue: insert and delete in O(1) at both the front and the rear. Use only one end and it is a stack; insert at the rear and delete at the front and it is a queue. That is why `collections.deque` and `ArrayDeque` are the recommended stack *and* queue in Python and Java.")
    yield qa("Why does a deque need a doubly linked list rather than a singly linked one?",
             "`deleteRear()` must make the previous node the new tail. In a singly linked list that node is only reachable by walking from the head — O(n). A `prev` pointer makes it `tail = tail.prev`, O(1). Everything else (head operations, tail insert) a singly linked list with a tail pointer can already do in O(1).")
    yield qa("How does Python's deque give O(1) at both ends, and why is d[i] O(n)?",
             "It is a doubly linked list of fixed-size blocks (64 slots). The two ends live in the leftmost and rightmost blocks, so pushing or popping there touches one slot. Indexing the middle has to hop block by block from the nearer end — O(n/64), i.e. O(n). Use a list when you need random access, a deque when you need both ends.")
    yield qa("ArrayDeque or LinkedList in Java?",
             "`ArrayDeque` for stacks and queues: a circular growable array, cache-friendly, no per-element node objects, faster in practice. `LinkedList` only when you also need `List` operations (index-based insert/remove via an iterator) or must store `null`, which `ArrayDeque` rejects.")
    yield qa("How do you implement a deque with a fixed array, and how do you tell empty from full?",
             "Treat the array as a ring. `insertFront` moves `front` to `(front − 1 + cap) % cap`; `insertRear` writes at `(front + size) % cap`. Keep a `size` counter: empty when `size == 0`, full when `size == cap`. Without the counter `front` and `rear` coincide in both states and you have to waste one slot to disambiguate.")
    yield qa("Name a problem where a deque beats both a stack and a queue.",
             "Sliding window maximum: for each window of size `k`, the deque holds indices of candidates in decreasing value order. New elements evict smaller ones from the rear (they can never be a maximum again), and indices that fall out of the window are dropped from the front. Each index enters and leaves once — O(n) overall, versus O(nk) naively.")
