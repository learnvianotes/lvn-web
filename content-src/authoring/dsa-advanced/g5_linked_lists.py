from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Linked Lists, Stacks & Queues"


@topic(G, "linked_list", "LinkedList", "link")
def _():
    yield lead("Linked-list problems are pointer puzzles: almost every classic one is solved by **two pointers moving at different speeds or distances**, by **reversing links in place**, or by **re-wiring nodes without allocating**. This topic collects the problems interviewers actually ask and the handful of techniques that solve them.")
    yield define("Singly linked list", "a chain of nodes where each node stores a value (`data`) and a reference to the next node (`next`); the last node's `next` is `null`. Only the `head` is kept — every other node is reached by following links, so random access is `O(n)` but splicing nodes in and out is `O(1)` once you stand next to them.")
    yield diagram('''
        head
         ↓
        ┌────┬───┐   ┌────┬───┐   ┌────┬───┐   ┌────┬───┐
        │ 10 │ ●─┼──▶│ 20 │ ●─┼──▶│ 30 │ ●─┼──▶│ 40 │ ∅ │
        └────┴───┘   └────┴───┘   └────┴───┘   └────┴───┘
         data next
    ''', "The list 10 → 20 → 30 → 40 — every solution below works on this shape")

    yield section("Recap: what costs what", "table")
    yield table(
        ["Operation", "Singly linked list", "Dynamic array"],
        ["Access `i`-th element", "`O(n)` — walk from head", "`O(1)`"],
        ["Insert / delete at head", "`O(1)`", "`O(n)` — shift everything"],
        ["Insert / delete after a known node", "`O(1)` — re-wire two links", "`O(n)`"],
        ["Insert / delete at tail", "`O(n)` (`O(1)` with a tail pointer)", "amortised `O(1)`"],
        ["Search", "`O(n)`", "`O(n)` (`O(log n)` if sorted)"],
        ["Memory per element", "value + one pointer, scattered", "value only, contiguous and cache-friendly"],
    )
    yield p("The problems in this topic exploit the one thing a list does better than an array: **moving a node costs `O(1)` and no allocation**. Reversing, merging, swapping pairs and segregating are all done by changing `next` pointers, never by copying values into a new container.")

    yield section("The techniques behind every problem", "bulb")
    yield cards(
        ("Slow and fast pointers", "`slow` moves one node per step, `fast` two. When `fast` reaches the end, `slow` is at the middle; if `fast` ever catches `slow`, there is a loop. Used for: middle, palindrome, loop detection.", "route"),
        ("Two pointers a fixed gap apart", "Send `first` ahead by `n` nodes, then move both together; when `first` falls off, `second` is `n` from the end. Used for: nth node from end, intersection (after aligning lengths).", "arrows-left-right"),
        ("Reverse links in place", "Three pointers `prev`, `curr`, `next` flip each link in one pass. Used for: reverse, reverse in groups of `k`, palindrome (reverse the second half).", "repeat"),
        ("Dummy head node", "A throwaway node in front of the list removes every “is this the first node?” special case. Used for: merge, pairwise swap, deleting nodes.", "box"),
        ("Hash the node references", "A set or map keyed by node *identity* (not value) gives a straightforward `O(n)`-space solution — the baseline you beat with pointer tricks. Used for: loop, intersection, clone.", "hash"),
        ("Re-wire instead of allocate", "Thread existing nodes into new sublists (even/odd, merged) or interleave copies inside the original list (clone). Used for: segregate, clone with random pointers.", "git-branch"),
        cols=3,
    )

    yield section("Node and helpers used in every solution", "code")
    yield p("Every program below carries the same three pieces: a `Node`, `build(values)` that turns an array into a list, and `toStr(head)` that prints a list as space-separated values. They are the only boilerplate — the solutions themselves are the functions in between.")
    yield multi('''
        10 20 30 40 50
        length: 5
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):                 # [1, 2, 3] → 1 → 2 → 3
            head = None
            for v in reversed(values):     # prepend from the back, so order is kept
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):                  # "1 2 3"
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def length(head):
            n = 0
            while head:
                n += 1
                head = head.next
            return n

        head = build([10, 20, 30, 40, 50])
        print(to_str(head))
        print("length:", length(head))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {            // {1, 2, 3} → 1 → 2 → 3
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {   // prepend from the back
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {                     // "1 2 3"
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        int length(Node* head) {
            int n = 0;
            for (Node* c = head; c; c = c->next) n++;
            return n;
        }

        int main() {
            Node* head = build({10, 20, 30, 40, 50});
            cout << toStr(head) << "\\n";
            cout << "length: " << length(head) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {                 // {1, 2, 3} → 1 → 2 → 3
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {   // prepend from the back
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {             // "1 2 3"
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static int length(Node head) {
                int n = 0;
                for (Node c = head; c != null; c = c.next) n++;
                return n;
            }

            public static void main(String[] args) {
                Node head = build(new int[]{10, 20, 30, 40, 50});
                System.out.println(toStr(head));
                System.out.println("length: " + length(head));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {                       // [1, 2, 3] → 1 → 2 → 3
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {   // prepend from the back
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {                         // "1 2 3"
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function length(head) {
            let n = 0;
            for (let c = head; c; c = c.next) n++;
            return n;
        }

        const head = build([10, 20, 30, 40, 50]);
        console.log(toStr(head));
        console.log("length:", length(head));
    ''')
    yield note("`build` prepends from the back of the array so the list comes out in array order without a tail pointer. In C++ the nodes are allocated with `new` and never freed in these short programs — fine for a demo, a leak in real code; a destructor or `unique_ptr` chain fixes that.")

    yield section("Middle of a linked list", "route")
    yield io("10 → 20 → 30 → 40 → 50", "30", "10 → 20 → 30 → 40", "30 (the second of the two middle nodes)")
    yield idea("Two pointers start at the head. `slow` advances one node, `fast` two. When `fast` runs off the end, `fast` has covered the whole list and `slow` exactly half of it — `slow` is standing on the middle. One pass, no counting.")
    yield diagram('''
        step 0:   slow            fast
                   ↓               ↓
                  10 → 20 → 30 → 40 → 50
        step 1:        slow       fast
        step 2:             slow            fast = ∅ → stop, slow = 30
    ''', "fast moves two for every one of slow, so slow ends at the middle")
    yield multi('''
        10 20 30 40 50 → middle 30
        10 20 30 40 → middle 30
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def middle(head):
            slow = fast = head
            while fast and fast.next:      # fast moves 2, slow moves 1
                slow = slow.next
                fast = fast.next.next
            return slow

        for values in ([10, 20, 30, 40, 50], [10, 20, 30, 40]):
            head = build(values)
            print(to_str(head), "→ middle", middle(head).data)
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* middle(Node* head) {
            Node* slow = head;
            Node* fast = head;
            while (fast && fast->next) {       // fast moves 2, slow moves 1
                slow = slow->next;
                fast = fast->next->next;
            }
            return slow;
        }

        int main() {
            for (vector<int> values : {vector<int>{10, 20, 30, 40, 50}, vector<int>{10, 20, 30, 40}}) {
                Node* head = build(values);
                cout << toStr(head) << " → middle " << middle(head)->data << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node middle(Node head) {
                Node slow = head, fast = head;
                while (fast != null && fast.next != null) {   // fast moves 2, slow moves 1
                    slow = slow.next;
                    fast = fast.next.next;
                }
                return slow;
            }

            public static void main(String[] args) {
                for (int[] values : new int[][]{{10, 20, 30, 40, 50}, {10, 20, 30, 40}}) {
                    Node head = build(values);
                    System.out.println(toStr(head) + " → middle " + middle(head).data);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function middle(head) {
            let slow = head, fast = head;
            while (fast && fast.next) {        // fast moves 2, slow moves 1
                slow = slow.next;
                fast = fast.next.next;
            }
            return slow;
        }

        for (const values of [[10, 20, 30, 40, 50], [10, 20, 30, 40]]) {
            const head = build(values);
            console.log(toStr(head), "→ middle", middle(head).data);
        }
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("For an even length this returns the **second** middle (`30` of `10 20 30 40`). To get the first middle instead, loop while `fast.next and fast.next.next` — that variant is exactly what the palindrome check below uses, because it wants `slow` at the end of the first half.")

    yield section("Nth node from the end", "arrows-left-right")
    yield io("10 → 20 → 30 → 40 → 50, n = 2", "40", "10 → 20 → 30 → 40 → 50, n = 6", "none (list is shorter than n)")
    yield idea("Move `first` ahead by `n` nodes. Now move `first` and `second` together; the gap between them stays `n`, so when `first` falls off the end, `second` is exactly `n` nodes from the end. The naive alternative — count the length, then walk `len − n` nodes — also works in `O(n)` but needs two passes.")
    yield multi('''
        n = 1 → 50
        n = 2 → 40
        n = 5 → 10
        n = 6 → none
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def nth_from_end(head, n):
            first = head
            for _ in range(n):               # move first n nodes ahead
                if first is None:
                    return None              # n is larger than the length
                first = first.next
            second = head
            while first:                     # now move both; the gap stays n
                first = first.next
                second = second.next
            return second

        head = build([10, 20, 30, 40, 50])
        for n in (1, 2, 5, 6):
            node = nth_from_end(head, n)
            print("n =", n, "→", node.data if node else "none")
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        Node* nthFromEnd(Node* head, int n) {
            Node* first = head;
            for (int i = 0; i < n; i++) {        // move first n nodes ahead
                if (!first) return nullptr;      // n is larger than the length
                first = first->next;
            }
            Node* second = head;
            while (first) {                      // now move both; the gap stays n
                first = first->next;
                second = second->next;
            }
            return second;
        }

        int main() {
            Node* head = build({10, 20, 30, 40, 50});
            for (int n : {1, 2, 5, 6}) {
                Node* node = nthFromEnd(head, n);
                cout << "n = " << n << " → " << (node ? to_string(node->data) : "none") << "\\n";
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static Node nthFromEnd(Node head, int n) {
                Node first = head;
                for (int i = 0; i < n; i++) {        // move first n nodes ahead
                    if (first == null) return null;  // n is larger than the length
                    first = first.next;
                }
                Node second = head;
                while (first != null) {              // now move both; the gap stays n
                    first = first.next;
                    second = second.next;
                }
                return second;
            }

            public static void main(String[] args) {
                Node head = build(new int[]{10, 20, 30, 40, 50});
                for (int n : new int[]{1, 2, 5, 6}) {
                    Node node = nthFromEnd(head, n);
                    System.out.println("n = " + n + " → " + (node != null ? String.valueOf(node.data) : "none"));
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function nthFromEnd(head, n) {
            let first = head;
            for (let i = 0; i < n; i++) {          // move first n nodes ahead
                if (!first) return null;           // n is larger than the length
                first = first.next;
            }
            let second = head;
            while (first) {                        // now move both; the gap stays n
                first = first.next;
                second = second.next;
            }
            return second;
        }

        const head = build([10, 20, 30, 40, 50]);
        for (const n of [1, 2, 5, 6]) {
            const node = nthFromEnd(head, n);
            console.log("n =", n, "→", node ? node.data : "none");
        }
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Check `first` for `null` *inside* the first loop. Without that check, `n` larger than the length dereferences `null` — a crash in C++/Java/JavaScript and an `AttributeError` in Python. “Delete the nth node from the end” is the same walk with a dummy head so that deleting the first node is not a special case.")

    yield section("Reverse a linked list", "repeat")
    yield io("10 → 20 → 30 → 40 → 50", "50 → 40 → 30 → 20 → 10")
    yield idea("**Iterative:** walk the list once with three pointers. `prev` is the already-reversed part, `curr` is the node being flipped, `next` saves the rest so it is not lost when `curr.next` is overwritten. **Recursive:** reverse everything after `head`, then make the old second node (`head.next`) point back to `head` and set `head.next = null` — `head` becomes the tail.")
    yield diagram('''
        before:   prev   curr   next
                   ∅  ←  10  →  20 → 30 → 40 → 50

        flip:      ∅  ←  10     20 → 30 → 40 → 50      curr.next = prev

        advance:         prev   curr   next
                   ∅  ←  10     20  →  30 → 40 → 50    prev = curr, curr = next
    ''', "One step of the iterative reversal — repeat until curr is ∅, then prev is the new head")
    yield multi('''
        iterative: 50 40 30 20 10
        recursive: 10 20 30 40 50
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def reverse_iter(head):
            prev, curr = None, head
            while curr:
                nxt = curr.next              # save the rest of the list
                curr.next = prev             # flip the link
                prev, curr = curr, nxt       # advance both pointers
            return prev                      # prev is the new head

        def reverse_rec(head):
            if head is None or head.next is None:
                return head                  # empty or single node: already reversed
            rest = reverse_rec(head.next)    # reverse everything after head
            head.next.next = head            # old second node now points back at head
            head.next = None                 # head becomes the tail
            return rest

        head = build([10, 20, 30, 40, 50])
        head = reverse_iter(head)
        print("iterative:", to_str(head))
        head = reverse_rec(head)             # reverse it back
        print("recursive:", to_str(head))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* reverseIter(Node* head) {
            Node* prev = nullptr;
            Node* curr = head;
            while (curr) {
                Node* next = curr->next;         // save the rest of the list
                curr->next = prev;               // flip the link
                prev = curr;                     // advance both pointers
                curr = next;
            }
            return prev;                         // prev is the new head
        }

        Node* reverseRec(Node* head) {
            if (!head || !head->next) return head;   // empty or single node
            Node* rest = reverseRec(head->next);     // reverse everything after head
            head->next->next = head;                 // old second node points back at head
            head->next = nullptr;                    // head becomes the tail
            return rest;
        }

        int main() {
            Node* head = build({10, 20, 30, 40, 50});
            head = reverseIter(head);
            cout << "iterative: " << toStr(head) << "\\n";
            head = reverseRec(head);                 // reverse it back
            cout << "recursive: " << toStr(head) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node reverseIter(Node head) {
                Node prev = null, curr = head;
                while (curr != null) {
                    Node next = curr.next;           // save the rest of the list
                    curr.next = prev;                // flip the link
                    prev = curr;                     // advance both pointers
                    curr = next;
                }
                return prev;                         // prev is the new head
            }

            static Node reverseRec(Node head) {
                if (head == null || head.next == null) return head;   // empty or single node
                Node rest = reverseRec(head.next);   // reverse everything after head
                head.next.next = head;               // old second node points back at head
                head.next = null;                    // head becomes the tail
                return rest;
            }

            public static void main(String[] args) {
                Node head = build(new int[]{10, 20, 30, 40, 50});
                head = reverseIter(head);
                System.out.println("iterative: " + toStr(head));
                head = reverseRec(head);             // reverse it back
                System.out.println("recursive: " + toStr(head));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function reverseIter(head) {
            let prev = null, curr = head;
            while (curr) {
                const next = curr.next;              // save the rest of the list
                curr.next = prev;                    // flip the link
                prev = curr;                         // advance both pointers
                curr = next;
            }
            return prev;                             // prev is the new head
        }

        function reverseRec(head) {
            if (!head || !head.next) return head;    // empty or single node
            const rest = reverseRec(head.next);      // reverse everything after head
            head.next.next = head;                   // old second node points back at head
            head.next = null;                        // head becomes the tail
            return rest;
        }

        let head = build([10, 20, 30, 40, 50]);
        head = reverseIter(head);
        console.log("iterative:", toStr(head));
        head = reverseRec(head);                     // reverse it back
        console.log("recursive:", toStr(head));
    ''')
    yield complexity("O(n)", "O(1) iterative · O(n) recursive (call stack)")
    yield pitfall("Forgetting to save `next` before `curr.next = prev` loses the rest of the list. In the recursive version, forgetting `head.next = null` leaves a cycle between the last two nodes — the first node still points at the second, which now points back. Prefer the iterative version in production: the recursive one uses one stack frame per node and overflows on long lists (Python at ~1000).")

    yield section("Reverse a linked list in groups of k", "arrows-shuffle")
    yield io("10 → 20 → 30 → 40 → 50 → 60, k = 3", "30 → 20 → 10 → 60 → 50 → 40", "10 → 20 → 30 → 40 → 50, k = 3", "30 → 20 → 10 → 50 → 40")
    yield idea("Reverse the first `k` nodes with the ordinary three-pointer loop. The group's old first node (`head`) is now its last node, so its `next` must point at the result of reversing the rest — either a recursive call, or the next group in an iterative loop. The last group is reversed even when it holds fewer than `k` nodes (the LeetCode variant leaves a short tail untouched — add a length check if that is required).")
    yield diagram('''
        10 → 20 → 30 │ 40 → 50 → 60          groups of k = 3

        reverse group 1:   30 → 20 → 10 → ?          10 was the head, now the tail
        reverse group 2:                60 → 50 → 40
        link:              30 → 20 → 10 → 60 → 50 → 40
    ''', "Each group is reversed on its own; the old head of a group links to the new head of the next")
    yield p("**Recursive** — the natural way to express “reverse this group, then link to the reversed rest”:")
    yield multi('''
        30 20 10 60 50 40
        30 20 10 50 40
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def reverse_k_rec(head, k):
            curr, prev = head, None
            count = 0
            while curr and count < k:        # reverse the first k nodes
                nxt = curr.next
                curr.next = prev
                prev = curr
                curr = nxt
                count += 1
            if curr:                         # more nodes left: reverse them and link
                head.next = reverse_k_rec(curr, k)   # head is now the tail of this group
            return prev                      # prev is the new head of this group

        for values in ([10, 20, 30, 40, 50, 60], [10, 20, 30, 40, 50]):
            print(to_str(reverse_k_rec(build(values), 3)))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* reverseKRec(Node* head, int k) {
            Node* curr = head;
            Node* prev = nullptr;
            int count = 0;
            while (curr && count < k) {          // reverse the first k nodes
                Node* next = curr->next;
                curr->next = prev;
                prev = curr;
                curr = next;
                count++;
            }
            if (curr)                            // more nodes left: reverse them and link
                head->next = reverseKRec(curr, k);   // head is now the tail of this group
            return prev;                         // prev is the new head of this group
        }

        int main() {
            for (vector<int> values : {vector<int>{10, 20, 30, 40, 50, 60}, vector<int>{10, 20, 30, 40, 50}})
                cout << toStr(reverseKRec(build(values), 3)) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node reverseKRec(Node head, int k) {
                Node curr = head, prev = null;
                int count = 0;
                while (curr != null && count < k) {  // reverse the first k nodes
                    Node next = curr.next;
                    curr.next = prev;
                    prev = curr;
                    curr = next;
                    count++;
                }
                if (curr != null)                    // more nodes left: reverse them and link
                    head.next = reverseKRec(curr, k);    // head is now the tail of this group
                return prev;                         // prev is the new head of this group
            }

            public static void main(String[] args) {
                for (int[] values : new int[][]{{10, 20, 30, 40, 50, 60}, {10, 20, 30, 40, 50}})
                    System.out.println(toStr(reverseKRec(build(values), 3)));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function reverseKRec(head, k) {
            let curr = head, prev = null, count = 0;
            while (curr && count < k) {              // reverse the first k nodes
                const next = curr.next;
                curr.next = prev;
                prev = curr;
                curr = next;
                count++;
            }
            if (curr)                                // more nodes left: reverse them and link
                head.next = reverseKRec(curr, k);    // head is now the tail of this group
            return prev;                             // prev is the new head of this group
        }

        for (const values of [[10, 20, 30, 40, 50, 60], [10, 20, 30, 40, 50]])
            console.log(toStr(reverseKRec(build(values), 3)));
    ''')
    yield complexity("O(n)", "O(n / k) recursion depth")
    yield p("**Iterative** — same work, constant extra space. Remember the first node of each group: after the group is reversed it is the group's tail, and the *previous* group's tail must be pointed at the new head of this group.")
    yield multi('''
        30 20 10 60 50 40
        30 20 10 50 40
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def reverse_k_iter(head, k):
            curr = head
            new_head = None
            prev_tail = None                 # tail of the previous reversed group
            while curr:
                group_first = curr           # will become this group's tail
                prev = None
                count = 0
                while curr and count < k:    # reverse one group
                    nxt = curr.next
                    curr.next = prev
                    prev = curr
                    curr = nxt
                    count += 1
                if new_head is None:
                    new_head = prev          # first group's new head is the list's head
                else:
                    prev_tail.next = prev    # link previous group to this one
                prev_tail = group_first
            return new_head

        for values in ([10, 20, 30, 40, 50, 60], [10, 20, 30, 40, 50]):
            print(to_str(reverse_k_iter(build(values), 3)))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* reverseKIter(Node* head, int k) {
            Node* curr = head;
            Node* newHead = nullptr;
            Node* prevTail = nullptr;            // tail of the previous reversed group
            while (curr) {
                Node* groupFirst = curr;         // will become this group's tail
                Node* prev = nullptr;
                int count = 0;
                while (curr && count < k) {      // reverse one group
                    Node* next = curr->next;
                    curr->next = prev;
                    prev = curr;
                    curr = next;
                    count++;
                }
                if (!newHead) newHead = prev;    // first group's new head is the list's head
                else prevTail->next = prev;      // link previous group to this one
                prevTail = groupFirst;
            }
            return newHead;
        }

        int main() {
            for (vector<int> values : {vector<int>{10, 20, 30, 40, 50, 60}, vector<int>{10, 20, 30, 40, 50}})
                cout << toStr(reverseKIter(build(values), 3)) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node reverseKIter(Node head, int k) {
                Node curr = head, newHead = null;
                Node prevTail = null;                // tail of the previous reversed group
                while (curr != null) {
                    Node groupFirst = curr;          // will become this group's tail
                    Node prev = null;
                    int count = 0;
                    while (curr != null && count < k) {   // reverse one group
                        Node next = curr.next;
                        curr.next = prev;
                        prev = curr;
                        curr = next;
                        count++;
                    }
                    if (newHead == null) newHead = prev;  // first group's new head is the list's head
                    else prevTail.next = prev;            // link previous group to this one
                    prevTail = groupFirst;
                }
                return newHead;
            }

            public static void main(String[] args) {
                for (int[] values : new int[][]{{10, 20, 30, 40, 50, 60}, {10, 20, 30, 40, 50}})
                    System.out.println(toStr(reverseKIter(build(values), 3)));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function reverseKIter(head, k) {
            let curr = head, newHead = null;
            let prevTail = null;                     // tail of the previous reversed group
            while (curr) {
                const groupFirst = curr;             // will become this group's tail
                let prev = null, count = 0;
                while (curr && count < k) {          // reverse one group
                    const next = curr.next;
                    curr.next = prev;
                    prev = curr;
                    curr = next;
                    count++;
                }
                if (!newHead) newHead = prev;        // first group's new head is the list's head
                else prevTail.next = prev;           // link previous group to this one
                prevTail = groupFirst;
            }
            return newHead;
        }

        for (const values of [[10, 20, 30, 40, 50, 60], [10, 20, 30, 40, 50]])
            console.log(toStr(reverseKIter(build(values), 3)));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("The two bugs here are both linking bugs: forgetting `head.next = …` after the recursive call (groups come back disconnected), or linking `prev_tail` to the group's *first* node instead of its *new head* `prev`.")

    yield section("Detect a loop — hash set of visited nodes", "hash")
    yield io("10 → 20 → 30 → 40 → 50, and 50 → 30", "Yes", "10 → 20 → 30 → 40 → 50", "No")
    yield diagram('''
        10 → 20 → 30 → 40 → 50
                  ↑          │
                  └──────────┘          50.next = 30 — a traversal never ends
    ''', "A loop: the last node points back into the list")
    yield idea("Walk the list, putting each node's **reference** (not its value — values may repeat) into a set. The first node already in the set is the loop entry; reaching `null` means no loop. Simple and `O(n)` time, but `O(n)` extra memory — the baseline Floyd's algorithm improves on.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def has_loop_set(head):
            seen = set()
            curr = head
            while curr:
                if curr in seen:             # visited before → we went round a loop
                    return True
                seen.add(curr)               # nodes hash by identity, not by value
                curr = curr.next
            return False

        head = build([10, 20, 30, 40, 50])
        print("10 → 20 → 30 → 40 → 50:", "Yes" if has_loop_set(head) else "No")
        tail = head
        while tail.next:
            tail = tail.next
        tail.next = head.next.next           # 50 → 30 creates the loop
        print("with 50 → 30:", "Yes" if has_loop_set(head) else "No")
    ''', out='''
        10 → 20 → 30 → 40 → 50: No
        with 50 → 30: Yes
    ''')
    yield note("The set must hold **references**: in C++ an `unordered_set<Node*>` keyed by address, in Java a `HashSet<Node>` (identity semantics because `Node` does not override `equals`/`hashCode`), in JavaScript a `Set` of objects. A set of *values* would report a false loop on `1 → 2 → 1`.")
    yield complexity("O(n)", "O(n)")
    yield note("Two other `O(1)`-space tricks you may see: a `visited` flag inside each node (needs a field you usually cannot add), or pointing every visited node's `next` at a sentinel dummy node (destroys the list). Floyd's algorithm needs neither.")

    yield section("Detect a loop — Floyd's cycle detection", "search")
    yield io("10 → 20 → 30 → 40 → 50, and 50 → 30", "Yes", "10 → 20 → 30 → 40 → 50", "No")
    yield idea("Run `slow` (one step) and `fast` (two steps) from the head. If there is no loop, `fast` reaches `null`. If there is a loop, both pointers eventually circle inside it, and `fast` gains exactly one node on `slow` every step — so it must land on `slow` within one lap. Two pointers, no memory.")
    yield steps(
        ("Initialise", "`slow = head`, `fast = head`."),
        ("Advance", "Each step: `slow = slow.next`, `fast = fast.next.next`. Stop with “no loop” when `fast` or `fast.next` is `null`."),
        ("Compare", "If `slow` is the same node as `fast`, there is a loop."),
    )
    yield p("**Why they must meet.** `fast` enters the loop no later than `slow`. Suppose that when `slow` enters the loop, `fast` is `k` nodes ahead of it (`0 ≤ k < n` for a loop of length `n`) — equivalently, `fast` is `n − k` nodes *behind* `slow` going round the circle. Every step `slow` moves one and `fast` moves two, so the gap behind closes by exactly one node per step. After `n − k` steps the gap is zero: they stand on the same node. Because the gap shrinks by one (not two), `fast` can never jump over `slow`.")
    yield diagram('''
        10 → 20 → 30 → 40 → 50 → (back to 30)        loop length n = 3

        step   slow   fast
          0     10     10
          1     20     30
          2     30     50
          3     40     40   ← meet
    ''', "Trace on the example: slow enters the loop at step 2 with fast one ahead; one more step and they meet")
    yield multi('''
        10 → 20 → 30 → 40 → 50: No
        with 50 → 30: Yes
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def has_loop(head):
            slow = fast = head
            while fast and fast.next:
                slow = slow.next             # one step
                fast = fast.next.next        # two steps
                if slow is fast:             # same node (not same value) → loop
                    return True
            return False                     # fast ran off the end

        head = build([10, 20, 30, 40, 50])
        print("10 → 20 → 30 → 40 → 50:", "Yes" if has_loop(head) else "No")
        tail = head
        while tail.next:
            tail = tail.next
        tail.next = head.next.next           # 50 → 30 creates the loop
        print("with 50 → 30:", "Yes" if has_loop(head) else "No")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        bool hasLoop(Node* head) {
            Node* slow = head;
            Node* fast = head;
            while (fast && fast->next) {
                slow = slow->next;               // one step
                fast = fast->next->next;         // two steps
                if (slow == fast) return true;   // same address → loop
            }
            return false;                        // fast ran off the end
        }

        int main() {
            Node* head = build({10, 20, 30, 40, 50});
            cout << "10 → 20 → 30 → 40 → 50: " << (hasLoop(head) ? "Yes" : "No") << "\\n";
            Node* tail = head;
            while (tail->next) tail = tail->next;
            tail->next = head->next->next;       // 50 → 30 creates the loop
            cout << "with 50 → 30: " << (hasLoop(head) ? "Yes" : "No") << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static boolean hasLoop(Node head) {
                Node slow = head, fast = head;
                while (fast != null && fast.next != null) {
                    slow = slow.next;                // one step
                    fast = fast.next.next;           // two steps
                    if (slow == fast) return true;   // same reference → loop
                }
                return false;                        // fast ran off the end
            }

            public static void main(String[] args) {
                Node head = build(new int[]{10, 20, 30, 40, 50});
                System.out.println("10 → 20 → 30 → 40 → 50: " + (hasLoop(head) ? "Yes" : "No"));
                Node tail = head;
                while (tail.next != null) tail = tail.next;
                tail.next = head.next.next;          // 50 → 30 creates the loop
                System.out.println("with 50 → 30: " + (hasLoop(head) ? "Yes" : "No"));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function hasLoop(head) {
            let slow = head, fast = head;
            while (fast && fast.next) {
                slow = slow.next;                    // one step
                fast = fast.next.next;               // two steps
                if (slow === fast) return true;      // same object → loop
            }
            return false;                            // fast ran off the end
        }

        const head = build([10, 20, 30, 40, 50]);
        console.log("10 → 20 → 30 → 40 → 50:", hasLoop(head) ? "Yes" : "No");
        let tail = head;
        while (tail.next) tail = tail.next;
        tail.next = head.next.next;                  // 50 → 30 creates the loop
        console.log("with 50 → 30:", hasLoop(head) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Compare the **nodes**, not their values (`slow is fast` / `==` on references) — a list with repeated values has no loop. And test `fast.next` as well as `fast` before stepping twice; `fast.next.next` on the last node is a `null` dereference.")

    yield section("Detect and remove a loop", "alert-triangle")
    yield io("10 → 15 → 5 → 20, and 20 → 15", "10 → 15 → 5 → 20 (loop of length 3 starting at 15 removed)")
    yield idea("Floyd's meeting point is not the loop's first node — but it is a fixed distance from it. Move `slow` back to `head`, keep `fast` at the meeting point, and advance both **one step at a time**: they meet exactly at the first node of the loop. Then walk round the loop once more to find the node whose `next` is that first node, and set its `next` to `null`.")
    yield steps(
        ("Detect", "Run Floyd's algorithm. If `slow` and `fast` never meet, there is no loop — stop."),
        ("Loop length (variation 1)", "From the meeting point, walk round until you are back: the number of steps is the loop length `n`."),
        ("First node of the loop (variation 2)", "Put `slow` at `head`, leave `fast` at the meeting point. Move both one step until they are equal — that node is the loop start."),
        ("Cut", "From the loop start, walk until `node.next` is the loop start again; that node is the last node of the loop. Set its `next = null`."),
    )
    yield p("**Why moving one pointer back to the head works.** Let `m` be the distance from `head` to the loop start, `n` the loop length, and `k` the distance from the loop start to the meeting point. When they meet, `slow` has walked `m + k + x·n` and `fast` twice that, `m + k + y·n`, for some lap counts `x`, `y`:")
    yield formula("2(m + k + x·n) = m + k + y·n  ⟹  m + k = (y − 2x)·n")
    yield p("So `m + k` is a **multiple of the loop length**. A pointer that starts at the meeting point (already `k` into the loop) and walks `m` more steps is `m + k ≡ 0 (mod n)` into the loop — i.e. back at the loop start. A pointer that starts at `head` and walks `m` steps is also at the loop start. Walking both at the same speed, they coincide for the first time exactly there.")
    yield diagram('''
        10 → 15 → 5 → 20 → (back to 15)        m = 1, n = 3

        Floyd:   slow 10,15,5,20     fast 10,5,15,20  → meet at 20  (k = 2, m + k = 3 = n ✓)
        phase 2: slow = head = 10, fast = 20
                 one step each:  slow → 15, fast → 15   → loop starts at 15
        cut:     from 15 walk to the node whose next is 15: that is 20 → 20.next = ∅
    ''', "Trace on the example")
    yield multi('''
        loop length: 3
        loop starts at: 15
        after removal: 10 15 5 20
        no loop
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def detect_and_remove(head):
            slow = fast = head
            while fast and fast.next:            # 1. Floyd: find a meeting point
                slow = slow.next
                fast = fast.next.next
                if slow is fast:
                    break
            else:
                print("no loop")
                return
            length = 1                           # 2. loop length: walk round once
            p = fast.next
            while p is not fast:
                p = p.next
                length += 1
            print("loop length:", length)
            slow = head                          # 3. loop start: same speed from head and meeting point
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            print("loop starts at:", slow.data)
            last = slow                          # 4. find the last node of the loop and cut
            while last.next is not slow:
                last = last.next
            last.next = None

        head = build([10, 15, 5, 20])
        head.next.next.next.next = head.next     # 20 → 15 creates the loop
        detect_and_remove(head)
        print("after removal:", to_str(head))
        detect_and_remove(head)                  # run again: the list is clean now
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        void detectAndRemove(Node* head) {
            Node* slow = head;
            Node* fast = head;
            bool met = false;
            while (fast && fast->next) {             // 1. Floyd: find a meeting point
                slow = slow->next;
                fast = fast->next->next;
                if (slow == fast) { met = true; break; }
            }
            if (!met) { cout << "no loop\\n"; return; }
            int length = 1;                          // 2. loop length: walk round once
            for (Node* p = fast->next; p != fast; p = p->next) length++;
            cout << "loop length: " << length << "\\n";
            slow = head;                             // 3. loop start: same speed from head and meeting point
            while (slow != fast) {
                slow = slow->next;
                fast = fast->next;
            }
            cout << "loop starts at: " << slow->data << "\\n";
            Node* last = slow;                       // 4. find the last node of the loop and cut
            while (last->next != slow) last = last->next;
            last->next = nullptr;
        }

        int main() {
            Node* head = build({10, 15, 5, 20});
            head->next->next->next->next = head->next;   // 20 → 15 creates the loop
            detectAndRemove(head);
            cout << "after removal: " << toStr(head) << "\\n";
            detectAndRemove(head);                   // run again: the list is clean now
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static void detectAndRemove(Node head) {
                Node slow = head, fast = head;
                boolean met = false;
                while (fast != null && fast.next != null) {   // 1. Floyd: find a meeting point
                    slow = slow.next;
                    fast = fast.next.next;
                    if (slow == fast) { met = true; break; }
                }
                if (!met) { System.out.println("no loop"); return; }
                int length = 1;                          // 2. loop length: walk round once
                for (Node p = fast.next; p != fast; p = p.next) length++;
                System.out.println("loop length: " + length);
                slow = head;                             // 3. loop start: same speed from head and meeting point
                while (slow != fast) {
                    slow = slow.next;
                    fast = fast.next;
                }
                System.out.println("loop starts at: " + slow.data);
                Node last = slow;                        // 4. find the last node of the loop and cut
                while (last.next != slow) last = last.next;
                last.next = null;
            }

            public static void main(String[] args) {
                Node head = build(new int[]{10, 15, 5, 20});
                head.next.next.next.next = head.next;    // 20 → 15 creates the loop
                detectAndRemove(head);
                System.out.println("after removal: " + toStr(head));
                detectAndRemove(head);                   // run again: the list is clean now
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function detectAndRemove(head) {
            let slow = head, fast = head, met = false;
            while (fast && fast.next) {                  // 1. Floyd: find a meeting point
                slow = slow.next;
                fast = fast.next.next;
                if (slow === fast) { met = true; break; }
            }
            if (!met) { console.log("no loop"); return; }
            let length = 1;                              // 2. loop length: walk round once
            for (let p = fast.next; p !== fast; p = p.next) length++;
            console.log("loop length:", length);
            slow = head;                                 // 3. loop start: same speed from head and meeting point
            while (slow !== fast) {
                slow = slow.next;
                fast = fast.next;
            }
            console.log("loop starts at:", slow.data);
            let last = slow;                             // 4. find the last node of the loop and cut
            while (last.next !== slow) last = last.next;
            last.next = null;
        }

        const head = build([10, 15, 5, 20]);
        head.next.next.next.next = head.next;            // 20 → 15 creates the loop
        detectAndRemove(head);
        console.log("after removal:", toStr(head));
        detectAndRemove(head);                           // run again: the list is clean now
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("When the loop starts at the head itself (`m = 0`), the meeting point *is* the loop start, so the phase-2 loop runs zero times — no special case needed. The original notes handled that separately; the version above does not have to because it compares `slow` and `fast` directly rather than `slow.next` and `fast.next`.")

    yield section("Intersection point of two linked lists", "git-branch")
    yield io("A: 5 → 8 → 7 → 10 → 12 → 15,  B: 9 → 10 → 12 → 15 (B's second node is A's node 10)", "10")
    yield diagram('''
        A:  5 → 8 → 7 ─┐
                       ├─▶ 10 → 12 → 15 → ∅
        B:        9 ───┘
    ''', "Two lists sharing a tail — the intersection is the first shared node, by identity, not by value")
    yield p("**Baseline — hash set of nodes.** Put every node of `A` in a set, then walk `B` and return the first node already present. `O(m + n)` time, `O(m)` space.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def intersection_set(a, b):
            seen = set()
            while a:
                seen.add(a)                  # node identity, not value
                a = a.next
            while b:
                if b in seen:
                    return b
                b = b.next
            return None

        a = build([5, 8, 7, 10, 12, 15])
        b = Node(9)
        b.next = a.next.next.next            # 9 → 10 → 12 → 15, sharing from 10
        node = intersection_set(a, b)
        print("intersection:", node.data if node else "none")
    ''', out="intersection: 10")
    yield p("**Efficient — align the lengths.** Both lists share their whole tail from the intersection on, so they differ only in the number of nodes *before* it. Count both lengths, advance the longer list's pointer by the difference, then walk both together; the first time the two pointers are the same node is the intersection (or both reach `null`).")
    yield idea("After skipping `|len(A) − len(B)|` nodes of the longer list, both pointers are the same distance from the end. From then on they move in lock-step, so they reach the shared tail at the same moment.")
    yield multi('''
        A: 5 8 7 10 12 15
        B: 9 10 12 15
        intersection: 10
        intersection with 1 → 2: none
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def length(head):
            n = 0
            while head:
                n += 1
                head = head.next
            return n

        def intersection(a, b):
            la, lb = length(a), length(b)
            while la > lb:                   # advance the longer list by the difference
                a = a.next
                la -= 1
            while lb > la:
                b = b.next
                lb -= 1
            while a is not b:                # same distance from the end: walk together
                a = a.next
                b = b.next
            return a                         # None when both ran off the end

        a = build([5, 8, 7, 10, 12, 15])
        b = Node(9)
        b.next = a.next.next.next            # 9 → 10 → 12 → 15, sharing from 10
        print("A:", to_str(a))
        print("B:", to_str(b))
        node = intersection(a, b)
        print("intersection:", node.data if node else "none")
        node = intersection(a, build([1, 2]))
        print("intersection with 1 → 2:", node.data if node else "none")
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        int length(Node* head) {
            int n = 0;
            for (Node* c = head; c; c = c->next) n++;
            return n;
        }

        Node* intersection(Node* a, Node* b) {
            int la = length(a), lb = length(b);
            while (la > lb) { a = a->next; la--; }   // advance the longer list by the difference
            while (lb > la) { b = b->next; lb--; }
            while (a != b) {                         // same distance from the end: walk together
                a = a->next;
                b = b->next;
            }
            return a;                                // nullptr when both ran off the end
        }

        int main() {
            Node* a = build({5, 8, 7, 10, 12, 15});
            Node* b = new Node(9);
            b->next = a->next->next->next;           // 9 → 10 → 12 → 15, sharing from 10
            cout << "A: " << toStr(a) << "\\n";
            cout << "B: " << toStr(b) << "\\n";
            Node* node = intersection(a, b);
            cout << "intersection: " << (node ? to_string(node->data) : "none") << "\\n";
            node = intersection(a, build({1, 2}));
            cout << "intersection with 1 → 2: " << (node ? to_string(node->data) : "none") << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static int length(Node head) {
                int n = 0;
                for (Node c = head; c != null; c = c.next) n++;
                return n;
            }

            static Node intersection(Node a, Node b) {
                int la = length(a), lb = length(b);
                while (la > lb) { a = a.next; la--; }    // advance the longer list by the difference
                while (lb > la) { b = b.next; lb--; }
                while (a != b) {                         // same distance from the end: walk together
                    a = a.next;
                    b = b.next;
                }
                return a;                                // null when both ran off the end
            }

            public static void main(String[] args) {
                Node a = build(new int[]{5, 8, 7, 10, 12, 15});
                Node b = new Node(9);
                b.next = a.next.next.next;               // 9 → 10 → 12 → 15, sharing from 10
                System.out.println("A: " + toStr(a));
                System.out.println("B: " + toStr(b));
                Node node = intersection(a, b);
                System.out.println("intersection: " + (node != null ? String.valueOf(node.data) : "none"));
                node = intersection(a, build(new int[]{1, 2}));
                System.out.println("intersection with 1 → 2: " + (node != null ? String.valueOf(node.data) : "none"));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function length(head) {
            let n = 0;
            for (let c = head; c; c = c.next) n++;
            return n;
        }

        function intersection(a, b) {
            let la = length(a), lb = length(b);
            while (la > lb) { a = a.next; la--; }        // advance the longer list by the difference
            while (lb > la) { b = b.next; lb--; }
            while (a !== b) {                            // same distance from the end: walk together
                a = a.next;
                b = b.next;
            }
            return a;                                    // null when both ran off the end
        }

        const a = build([5, 8, 7, 10, 12, 15]);
        const b = new Node(9);
        b.next = a.next.next.next;                       // 9 → 10 → 12 → 15, sharing from 10
        console.log("A:", toStr(a));
        console.log("B:", toStr(b));
        let node = intersection(a, b);
        console.log("intersection:", node ? node.data : "none");
        node = intersection(a, build([1, 2]));
        console.log("intersection with 1 → 2:", node ? node.data : "none");
    ''')
    yield complexity("O(m + n)", "O(1)")
    yield note("**No-counting variant:** walk `pa` over `A` then `B`, and `pb` over `B` then `A`. Both travel exactly `len(A) + len(B)` nodes, so they reach the intersection together — or both hit `null` after the second list. Same complexity, slightly less code, harder to explain in an interview.")
    yield pitfall("Intersection means the **same node object**, not equal values — `1 → 2 → 3` and `9 → 3` with two different `3` nodes do not intersect. Compare references.")

    yield section("Segregate even and odd nodes", "arrows-sort")
    yield io("17 → 15 → 8 → 12 → 5", "8 → 12 → 17 → 15 → 5 (all even values first, relative order preserved)")
    yield p("**Naive — move odd nodes to the end.** Find the last node, then traverse once more: every odd node is detached and appended after the current last node. Stop after processing the *original* last node, otherwise the nodes you just appended are visited again and the loop never ends.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def segregate_naive(head):
            if head is None:
                return None
            last = head
            while last.next:
                last = last.next
            stop = last                      # original last node: do not go past it
            dummy = Node(0)
            dummy.next = head
            prev, curr = dummy, head
            while True:
                nxt = curr.next
                if curr.data % 2 == 1:       # odd: detach and append after last
                    prev.next = nxt
                    last.next = curr
                    curr.next = None
                    last = curr
                else:
                    prev = curr
                if curr is stop:
                    break
                curr = nxt
            return dummy.next

        print(to_str(segregate_naive(build([17, 15, 8, 12, 5]))))
        print(to_str(segregate_naive(build([1, 3, 5]))))
    ''', out='''
        8 12 17 15 5
        1 3 5
    ''')
    yield p("**One traversal — build two sublists and join them.** Keep the start and end of an *even* sublist and of an *odd* sublist. Every node is appended to the end of its own sublist as it is visited, so each sublist keeps the original relative order. At the end, link the even tail to the odd head and terminate the odd tail.")
    yield idea("Nothing is allocated and no node is moved twice: the four pointers `even_start`, `even_end`, `odd_start`, `odd_end` just thread the existing nodes into two chains, which are joined once.")
    yield diagram('''
        input:   17 → 15 → 8 → 12 → 5

        evens:   8 → 12                  even_start = 8,  even_end = 12
        odds:    17 → 15 → 5             odd_start = 17,  odd_end = 5

        join:    8 → 12 → 17 → 15 → 5 → ∅    even_end.next = odd_start, odd_end.next = ∅
    ''', "Two chains threaded through the same nodes, then joined")
    yield multi('''
        8 12 17 15 5
        1 3 5
        2 4 1
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def segregate(head):
            even_start = even_end = None
            odd_start = odd_end = None
            curr = head
            while curr:
                if curr.data % 2 == 0:
                    if even_start is None:
                        even_start = even_end = curr
                    else:
                        even_end.next = curr     # append to the even chain
                        even_end = curr
                else:
                    if odd_start is None:
                        odd_start = odd_end = curr
                    else:
                        odd_end.next = curr      # append to the odd chain
                        odd_end = curr
                curr = curr.next
            if even_start is None or odd_start is None:
                return head                  # all even or all odd: nothing to do
            even_end.next = odd_start        # join the chains
            odd_end.next = None              # terminate — or the list gets a cycle
            return even_start

        for values in ([17, 15, 8, 12, 5], [1, 3, 5], [1, 2, 4]):
            print(to_str(segregate(build(values))))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* segregate(Node* head) {
            Node *evenStart = nullptr, *evenEnd = nullptr;
            Node *oddStart = nullptr, *oddEnd = nullptr;
            for (Node* curr = head; curr; curr = curr->next) {
                if (curr->data % 2 == 0) {
                    if (!evenStart) evenStart = evenEnd = curr;
                    else { evenEnd->next = curr; evenEnd = curr; }   // append to the even chain
                } else {
                    if (!oddStart) oddStart = oddEnd = curr;
                    else { oddEnd->next = curr; oddEnd = curr; }     // append to the odd chain
                }
            }
            if (!evenStart || !oddStart) return head;   // all even or all odd: nothing to do
            evenEnd->next = oddStart;                    // join the chains
            oddEnd->next = nullptr;                      // terminate — or the list gets a cycle
            return evenStart;
        }

        int main() {
            for (vector<int> values : {vector<int>{17, 15, 8, 12, 5}, vector<int>{1, 3, 5}, vector<int>{1, 2, 4}})
                cout << toStr(segregate(build(values))) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node segregate(Node head) {
                Node evenStart = null, evenEnd = null, oddStart = null, oddEnd = null;
                for (Node curr = head; curr != null; curr = curr.next) {
                    if (curr.data % 2 == 0) {
                        if (evenStart == null) evenStart = evenEnd = curr;
                        else { evenEnd.next = curr; evenEnd = curr; }   // append to the even chain
                    } else {
                        if (oddStart == null) oddStart = oddEnd = curr;
                        else { oddEnd.next = curr; oddEnd = curr; }     // append to the odd chain
                    }
                }
                if (evenStart == null || oddStart == null) return head;  // all even or all odd
                evenEnd.next = oddStart;                 // join the chains
                oddEnd.next = null;                      // terminate — or the list gets a cycle
                return evenStart;
            }

            public static void main(String[] args) {
                for (int[] values : new int[][]{{17, 15, 8, 12, 5}, {1, 3, 5}, {1, 2, 4}})
                    System.out.println(toStr(segregate(build(values))));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function segregate(head) {
            let evenStart = null, evenEnd = null, oddStart = null, oddEnd = null;
            for (let curr = head; curr; curr = curr.next) {
                if (curr.data % 2 === 0) {
                    if (!evenStart) evenStart = evenEnd = curr;
                    else { evenEnd.next = curr; evenEnd = curr; }       // append to the even chain
                } else {
                    if (!oddStart) oddStart = oddEnd = curr;
                    else { oddEnd.next = curr; oddEnd = curr; }         // append to the odd chain
                }
            }
            if (!evenStart || !oddStart) return head;    // all even or all odd: nothing to do
            evenEnd.next = oddStart;                     // join the chains
            oddEnd.next = null;                          // terminate — or the list gets a cycle
            return evenStart;
        }

        for (const values of [[17, 15, 8, 12, 5], [1, 3, 5], [1, 2, 4]])
            console.log(toStr(segregate(build(values))));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("`odd_end.next = None` is the line everyone forgets. If the last node of the input is even, the odd tail still points at some even node that is now earlier in the list — and the result has a cycle that `to_str` would loop on forever. The same two-chain pattern solves “partition a list around a value `x`” and “odd/even *positions*” (LeetCode 328).")

    yield section("Pairwise swap nodes", "arrows-left-right")
    yield io("1 → 2 → 3 → 4", "2 → 1 → 4 → 3", "1 → 2 → 3 → 4 → 5", "2 → 1 → 4 → 3 → 5 (odd one out stays)")
    yield p("**Swap the data.** Walk two nodes at a time and exchange the values of each pair. Trivial — but it only works when swapping values is allowed and cheap. If nodes carry large payloads, or other code holds references to specific nodes (an LRU cache, an iterator), the values must stay with their nodes and the *links* have to be swapped instead.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def pairwise_swap_data(head):
            curr = head
            while curr and curr.next:        # at least one node ahead
                curr.data, curr.next.data = curr.next.data, curr.data
                curr = curr.next.next        # jump over the pair
            return head

        for values in ([1, 2, 3, 4], [1, 2, 3, 4, 5]):
            print(to_str(pairwise_swap_data(build(values))))
    ''', out='''
        2 1 4 3
        2 1 4 3 5
    ''')
    yield complexity("O(n)", "O(1)")
    yield p("**Swap the links.** For each pair `a → b`, make the node *before* the pair point at `b`, `b` point at `a`, and `a` point at whatever followed `b`. A dummy node in front of the head removes the special case for the first pair (whose “node before” would otherwise not exist), and the new head is simply `dummy.next`.")
    yield diagram('''
        prev → a → b → rest            before

        a.next = b.next   :  prev → a ─────▶ rest
                                      b ──▶ rest
        b.next = a        :  b → a → rest
        prev.next = b     :  prev → b → a → rest
        prev = a          :  ready for the next pair
    ''', "Three link changes per pair; prev moves to a, the pair's new tail")
    yield multi('''
        2 1 4 3
        2 1 4 3 5
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def pairwise_swap(head):
            dummy = Node(0)                  # sits before the head: no special first pair
            dummy.next = head
            prev = dummy
            while prev.next and prev.next.next:
                a = prev.next                # first node of the pair
                b = a.next                   # second node of the pair
                a.next = b.next              # a now points past the pair
                b.next = a                   # b points back at a
                prev.next = b                # the node before the pair points at b
                prev = a                     # a is the pair's new tail
            return dummy.next

        for values in ([1, 2, 3, 4], [1, 2, 3, 4, 5]):
            print(to_str(pairwise_swap(build(values))))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* pairwiseSwap(Node* head) {
            Node dummy(0);                       // sits before the head: no special first pair
            dummy.next = head;
            Node* prev = &dummy;
            while (prev->next && prev->next->next) {
                Node* a = prev->next;            // first node of the pair
                Node* b = a->next;               // second node of the pair
                a->next = b->next;               // a now points past the pair
                b->next = a;                     // b points back at a
                prev->next = b;                  // the node before the pair points at b
                prev = a;                        // a is the pair's new tail
            }
            return dummy.next;
        }

        int main() {
            for (vector<int> values : {vector<int>{1, 2, 3, 4}, vector<int>{1, 2, 3, 4, 5}})
                cout << toStr(pairwiseSwap(build(values))) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node pairwiseSwap(Node head) {
                Node dummy = new Node(0);            // sits before the head: no special first pair
                dummy.next = head;
                Node prev = dummy;
                while (prev.next != null && prev.next.next != null) {
                    Node a = prev.next;              // first node of the pair
                    Node b = a.next;                 // second node of the pair
                    a.next = b.next;                 // a now points past the pair
                    b.next = a;                      // b points back at a
                    prev.next = b;                   // the node before the pair points at b
                    prev = a;                        // a is the pair's new tail
                }
                return dummy.next;
            }

            public static void main(String[] args) {
                for (int[] values : new int[][]{{1, 2, 3, 4}, {1, 2, 3, 4, 5}})
                    System.out.println(toStr(pairwiseSwap(build(values))));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function pairwiseSwap(head) {
            const dummy = new Node(0);               // sits before the head: no special first pair
            dummy.next = head;
            let prev = dummy;
            while (prev.next && prev.next.next) {
                const a = prev.next;                 // first node of the pair
                const b = a.next;                    // second node of the pair
                a.next = b.next;                     // a now points past the pair
                b.next = a;                          // b points back at a
                prev.next = b;                       // the node before the pair points at b
                prev = a;                            // a is the pair's new tail
            }
            return dummy.next;
        }

        for (const values of [[1, 2, 3, 4], [1, 2, 3, 4, 5]])
            console.log(toStr(pairwiseSwap(build(values))));
    ''')
    yield complexity("O(n)", "O(1)")
    yield note("Pairwise swap is “reverse in groups of `k`” with `k = 2` and a short tail left alone. The dummy-head trick is worth memorising: it turns every “what if it is the first node?” branch into ordinary code.")

    yield section("Clone a linked list with random pointers", "copy")
    yield io("1 → 2 → 3 → 4 with random links 1→3, 2→1, 3→4, 4→2", "an independent copy with the same next and random structure")
    yield p("Each node has a second pointer, `random`, to any node in the list (or `null`). A plain copy that walks `next` cannot set `random` on the copies because the target copy may not exist yet — and even when it does, you have to *find* it. Two solutions: a map from original to copy, or a trick that stores the mapping inside the list itself.")
    yield diagram('''
                ┌─────────────────┐
                │        ┌────────┼───────┐
                ▼        │        │       ▼
        1 ───▶ 2 ───▶ 3 ───▶ 4      next (solid)
        │      ▲        │        ▲     random: 1→3, 2→1, 3→4, 4→2
        └──────┼────────┘        │
               └─────────────────┘
    ''', "A list whose random pointers can jump anywhere — forwards, backwards or to itself")
    yield p("**Method 1 — dictionary from original to copy.** Pass 1 creates a copy of every node and records `copy_of[original] = copy`. Pass 2 sets `copy_of[node].next = copy_of[node.next]` and `copy_of[node].random = copy_of[node.random]`; mapping `null → null` makes the end of the list and missing randoms fall out for free.")
    yield multi('''
        original: 1:3 2:1 3:4 4:2
        clone:    1:3 2:1 3:4 4:2
        after adding 100 to every original node
        original: 101:103 102:101 103:104 104:102
        clone:    1:3 2:1 3:4 4:2
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None
                self.random = None

        def pairs(head):                     # "data:random data:random …"
            parts = []
            while head:
                parts.append(f"{head.data}:{head.random.data if head.random else '-'}")
                head = head.next
            return " ".join(parts)

        def clone(head):
            copy_of = {None: None}           # original → copy; None maps to None
            curr = head
            while curr:                      # pass 1: create the copies
                copy_of[curr] = Node(curr.data)
                curr = curr.next
            curr = head
            while curr:                      # pass 2: wire next and random via the map
                copy_of[curr].next = copy_of[curr.next]
                copy_of[curr].random = copy_of[curr.random]
                curr = curr.next
            return copy_of[head]

        nodes = [Node(v) for v in (1, 2, 3, 4)]
        for i in range(3):
            nodes[i].next = nodes[i + 1]
        for i, r in enumerate((2, 0, 3, 1)):     # 1→3, 2→1, 3→4, 4→2
            nodes[i].random = nodes[r]
        head = nodes[0]
        copy = clone(head)
        print("original:", pairs(head))
        print("clone:   ", pairs(copy))
        print("after adding 100 to every original node")
        for n in nodes:
            n.data += 100
        print("original:", pairs(head))
        print("clone:   ", pairs(copy))      # unchanged: it shares no node with the original
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next; Node* random;
            Node(int d) : data(d), next(nullptr), random(nullptr) {}
        };

        string pairs(Node* head) {                 // "data:random data:random …"
            string s;
            for (Node* c = head; c; c = c->next)
                s += to_string(c->data) + ":" + (c->random ? to_string(c->random->data) : "-") + (c->next ? " " : "");
            return s;
        }

        Node* clone(Node* head) {
            unordered_map<Node*, Node*> copyOf;    // original → copy
            copyOf[nullptr] = nullptr;             // nullptr maps to nullptr
            for (Node* c = head; c; c = c->next)   // pass 1: create the copies
                copyOf[c] = new Node(c->data);
            for (Node* c = head; c; c = c->next) { // pass 2: wire next and random via the map
                copyOf[c]->next = copyOf[c->next];
                copyOf[c]->random = copyOf[c->random];
            }
            return copyOf[head];
        }

        int main() {
            vector<Node*> nodes;
            for (int v : {1, 2, 3, 4}) nodes.push_back(new Node(v));
            for (int i = 0; i < 3; i++) nodes[i]->next = nodes[i + 1];
            int r[] = {2, 0, 3, 1};                // 1→3, 2→1, 3→4, 4→2
            for (int i = 0; i < 4; i++) nodes[i]->random = nodes[r[i]];
            Node* head = nodes[0];
            Node* copy = clone(head);
            cout << "original: " << pairs(head) << "\\n";
            cout << "clone:    " << pairs(copy) << "\\n";
            cout << "after adding 100 to every original node\\n";
            for (Node* n : nodes) n->data += 100;
            cout << "original: " << pairs(head) << "\\n";
            cout << "clone:    " << pairs(copy) << "\\n";   // unchanged: shares no node with the original
        }
    ''', java='''
        import java.util.HashMap;
        import java.util.Map;

        public class Main {
            static class Node {
                int data; Node next, random;
                Node(int d) { data = d; }
            }

            static String pairs(Node head) {         // "data:random data:random …"
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next)
                    sb.append(c.data).append(':').append(c.random != null ? String.valueOf(c.random.data) : "-").append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node clone(Node head) {
                Map<Node, Node> copyOf = new HashMap<>();   // original → copy
                copyOf.put(null, null);                     // null maps to null
                for (Node c = head; c != null; c = c.next)  // pass 1: create the copies
                    copyOf.put(c, new Node(c.data));
                for (Node c = head; c != null; c = c.next) {   // pass 2: wire next and random via the map
                    copyOf.get(c).next = copyOf.get(c.next);
                    copyOf.get(c).random = copyOf.get(c.random);
                }
                return copyOf.get(head);
            }

            public static void main(String[] args) {
                Node[] nodes = new Node[4];
                for (int i = 0; i < 4; i++) nodes[i] = new Node(i + 1);
                for (int i = 0; i < 3; i++) nodes[i].next = nodes[i + 1];
                int[] r = {2, 0, 3, 1};                  // 1→3, 2→1, 3→4, 4→2
                for (int i = 0; i < 4; i++) nodes[i].random = nodes[r[i]];
                Node head = nodes[0];
                Node copy = clone(head);
                System.out.println("original: " + pairs(head));
                System.out.println("clone:    " + pairs(copy));
                System.out.println("after adding 100 to every original node");
                for (Node n : nodes) n.data += 100;
                System.out.println("original: " + pairs(head));
                System.out.println("clone:    " + pairs(copy));   // unchanged: shares no node with the original
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; this.random = null; }
        }

        function pairs(head) {                       // "data:random data:random …"
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(`${c.data}:${c.random ? c.random.data : "-"}`);
            return parts.join(" ");
        }

        function clone(head) {
            const copyOf = new Map([[null, null]]);  // original → copy; null maps to null
            for (let c = head; c; c = c.next)        // pass 1: create the copies
                copyOf.set(c, new Node(c.data));
            for (let c = head; c; c = c.next) {      // pass 2: wire next and random via the map
                copyOf.get(c).next = copyOf.get(c.next);
                copyOf.get(c).random = copyOf.get(c.random);
            }
            return copyOf.get(head);
        }

        const nodes = [1, 2, 3, 4].map(v => new Node(v));
        for (let i = 0; i < 3; i++) nodes[i].next = nodes[i + 1];
        [2, 0, 3, 1].forEach((r, i) => { nodes[i].random = nodes[r]; });   // 1→3, 2→1, 3→4, 4→2
        const head = nodes[0];
        const copy = clone(head);
        console.log("original:", pairs(head));
        console.log("clone:   ", pairs(copy));
        console.log("after adding 100 to every original node");
        for (const n of nodes) n.data += 100;
        console.log("original:", pairs(head));
        console.log("clone:   ", pairs(copy));      // unchanged: shares no node with the original
    ''')
    yield complexity("O(n)", "O(n) for the map")
    yield p("**Method 2 — interleave the copies, `O(1)` extra space.** Store the mapping *in the list*: insert each copy right after its original, so `original.next` is always its copy. Then `copy.random = original.random.next` finds the right copy in `O(1)` without a map. Finally unweave the two lists.")
    yield steps(
        ("Interleave", "For every original node `o`, create `o'` and insert it after `o`: `1 → 1' → 2 → 2' → 3 → 3' → 4 → 4'`."),
        ("Set randoms", "For every original `o` (step two at a time): `o.next.random = o.random.next` — the copy of `o.random` is the node right after it. Skip when `o.random` is `null`."),
        ("Unweave", "Restore `o.next = o.next.next` and set `o'.next = o'.next.next`, splitting the chain back into the original list and the clone."),
    )
    yield diagram('''
        after step 1:   1 → 1' → 2 → 2' → 3 → 3' → 4 → 4'

        step 2 for node 2 (random → 1):  2.next.random = 2.random.next
                                         2'.random     = 1.next = 1'  ✓

        after step 3:   1 → 2 → 3 → 4          original restored
                        1' → 2' → 3' → 4'      clone, with randoms among the primed nodes
    ''', "The copy of any node is always the node right after it — that is the whole trick")
    yield multi('''
        original: 1:3 2:1 3:4 4:2
        clone:    1:3 2:1 3:4 4:2
        after adding 100 to every original node
        original: 101:103 102:101 103:104 104:102
        clone:    1:3 2:1 3:4 4:2
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None
                self.random = None

        def pairs(head):                     # "data:random data:random …"
            parts = []
            while head:
                parts.append(f"{head.data}:{head.random.data if head.random else '-'}")
                head = head.next
            return " ".join(parts)

        def clone(head):
            if head is None:
                return None
            curr = head
            while curr:                      # 1. insert a copy after every original
                copy = Node(curr.data)
                copy.next = curr.next
                curr.next = copy
                curr = copy.next
            curr = head
            while curr:                      # 2. copy.random = the copy of original.random
                if curr.random:
                    curr.next.random = curr.random.next
                curr = curr.next.next
            clone_head = head.next
            curr = head
            while curr:                      # 3. unweave originals and copies
                copy = curr.next
                curr.next = copy.next
                copy.next = copy.next.next if copy.next else None
                curr = curr.next
            return clone_head

        nodes = [Node(v) for v in (1, 2, 3, 4)]
        for i in range(3):
            nodes[i].next = nodes[i + 1]
        for i, r in enumerate((2, 0, 3, 1)):     # 1→3, 2→1, 3→4, 4→2
            nodes[i].random = nodes[r]
        head = nodes[0]
        copy = clone(head)
        print("original:", pairs(head))
        print("clone:   ", pairs(copy))
        print("after adding 100 to every original node")
        for n in nodes:
            n.data += 100
        print("original:", pairs(head))
        print("clone:   ", pairs(copy))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next; Node* random;
            Node(int d) : data(d), next(nullptr), random(nullptr) {}
        };

        string pairs(Node* head) {                 // "data:random data:random …"
            string s;
            for (Node* c = head; c; c = c->next)
                s += to_string(c->data) + ":" + (c->random ? to_string(c->random->data) : "-") + (c->next ? " " : "");
            return s;
        }

        Node* clone(Node* head) {
            if (!head) return nullptr;
            for (Node* curr = head; curr; curr = curr->next->next) {   // 1. insert a copy after every original
                Node* copy = new Node(curr->data);
                copy->next = curr->next;
                curr->next = copy;
            }
            for (Node* curr = head; curr; curr = curr->next->next)     // 2. copy->random = copy of original->random
                if (curr->random) curr->next->random = curr->random->next;
            Node* cloneHead = head->next;
            for (Node* curr = head; curr; curr = curr->next) {         // 3. unweave originals and copies
                Node* copy = curr->next;
                curr->next = copy->next;
                copy->next = copy->next ? copy->next->next : nullptr;
            }
            return cloneHead;
        }

        int main() {
            vector<Node*> nodes;
            for (int v : {1, 2, 3, 4}) nodes.push_back(new Node(v));
            for (int i = 0; i < 3; i++) nodes[i]->next = nodes[i + 1];
            int r[] = {2, 0, 3, 1};                // 1→3, 2→1, 3→4, 4→2
            for (int i = 0; i < 4; i++) nodes[i]->random = nodes[r[i]];
            Node* head = nodes[0];
            Node* copy = clone(head);
            cout << "original: " << pairs(head) << "\\n";
            cout << "clone:    " << pairs(copy) << "\\n";
            cout << "after adding 100 to every original node\\n";
            for (Node* n : nodes) n->data += 100;
            cout << "original: " << pairs(head) << "\\n";
            cout << "clone:    " << pairs(copy) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next, random;
                Node(int d) { data = d; }
            }

            static String pairs(Node head) {         // "data:random data:random …"
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next)
                    sb.append(c.data).append(':').append(c.random != null ? String.valueOf(c.random.data) : "-").append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node clone(Node head) {
                if (head == null) return null;
                for (Node curr = head; curr != null; curr = curr.next.next) {   // 1. insert a copy after every original
                    Node copy = new Node(curr.data);
                    copy.next = curr.next;
                    curr.next = copy;
                }
                for (Node curr = head; curr != null; curr = curr.next.next)     // 2. copy.random = copy of original.random
                    if (curr.random != null) curr.next.random = curr.random.next;
                Node cloneHead = head.next;
                for (Node curr = head; curr != null; curr = curr.next) {        // 3. unweave originals and copies
                    Node copy = curr.next;
                    curr.next = copy.next;
                    copy.next = copy.next != null ? copy.next.next : null;
                }
                return cloneHead;
            }

            public static void main(String[] args) {
                Node[] nodes = new Node[4];
                for (int i = 0; i < 4; i++) nodes[i] = new Node(i + 1);
                for (int i = 0; i < 3; i++) nodes[i].next = nodes[i + 1];
                int[] r = {2, 0, 3, 1};                  // 1→3, 2→1, 3→4, 4→2
                for (int i = 0; i < 4; i++) nodes[i].random = nodes[r[i]];
                Node head = nodes[0];
                Node copy = clone(head);
                System.out.println("original: " + pairs(head));
                System.out.println("clone:    " + pairs(copy));
                System.out.println("after adding 100 to every original node");
                for (Node n : nodes) n.data += 100;
                System.out.println("original: " + pairs(head));
                System.out.println("clone:    " + pairs(copy));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; this.random = null; }
        }

        function pairs(head) {                       // "data:random data:random …"
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(`${c.data}:${c.random ? c.random.data : "-"}`);
            return parts.join(" ");
        }

        function clone(head) {
            if (!head) return null;
            for (let curr = head; curr; curr = curr.next.next) {   // 1. insert a copy after every original
                const copy = new Node(curr.data);
                copy.next = curr.next;
                curr.next = copy;
            }
            for (let curr = head; curr; curr = curr.next.next)     // 2. copy.random = copy of original.random
                if (curr.random) curr.next.random = curr.random.next;
            const cloneHead = head.next;
            for (let curr = head; curr; curr = curr.next) {        // 3. unweave originals and copies
                const copy = curr.next;
                curr.next = copy.next;
                copy.next = copy.next ? copy.next.next : null;
            }
            return cloneHead;
        }

        const nodes = [1, 2, 3, 4].map(v => new Node(v));
        for (let i = 0; i < 3; i++) nodes[i].next = nodes[i + 1];
        [2, 0, 3, 1].forEach((r, i) => { nodes[i].random = nodes[r]; });   // 1→3, 2→1, 3→4, 4→2
        const head = nodes[0];
        const copy = clone(head);
        console.log("original:", pairs(head));
        console.log("clone:   ", pairs(copy));
        console.log("after adding 100 to every original node");
        for (const n of nodes) n.data += 100;
        console.log("original:", pairs(head));
        console.log("clone:   ", pairs(copy));
    ''')
    yield complexity("O(n)", "O(1) extra (the clone itself is O(n))")
    yield pitfall("The original notes wrote `curr.next.random = curr.random.next` without checking `curr.random` — a `null` random crashes it. Also, step 3 must restore the originals' `next` pointers; a clone routine that leaves the input list interleaved has corrupted its caller's data.")

    yield section("Merge two sorted linked lists", "arrows-sort")
    yield io("10 → 20 → 30 and 5 → 25", "5 → 10 → 20 → 25 → 30")
    yield idea("Exactly the merge step of merge sort, but without a temporary array: compare the two heads, append the smaller to the result's tail, advance that list. When one list is exhausted, the whole remainder of the other is already sorted — link it in one step. A dummy head means the result's tail always exists, so no first-node special case.")
    yield diagram('''
        a: 10 → 20 → 30        b: 5 → 25

        dummy → 5                       take b (5 ≤ 10)
        dummy → 5 → 10                  take a
        dummy → 5 → 10 → 20             take a
        dummy → 5 → 10 → 20 → 25        take b
        dummy → 5 → 10 → 20 → 25 → 30   a has 30 left: link the rest
    ''', "Nodes are re-linked, not copied — the two inputs are consumed")
    yield multi('''
        5 10 20 25 30
        1 2 3 4 5 6
        1 2 3
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def merge(a, b):
            dummy = Node(0)                  # result tail always exists
            tail = dummy
            while a and b:
                if a.data <= b.data:         # take the smaller head (<= keeps it stable)
                    tail.next = a
                    a = a.next
                else:
                    tail.next = b
                    b = b.next
                tail = tail.next
            tail.next = a if a else b        # the rest of the other list is already sorted
            return dummy.next

        print(to_str(merge(build([10, 20, 30]), build([5, 25]))))
        print(to_str(merge(build([1, 3, 5]), build([2, 4, 6]))))
        print(to_str(merge(build([1, 2, 3]), None)))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* merge(Node* a, Node* b) {
            Node dummy(0);                       // result tail always exists
            Node* tail = &dummy;
            while (a && b) {
                if (a->data <= b->data) {        // take the smaller head (<= keeps it stable)
                    tail->next = a;
                    a = a->next;
                } else {
                    tail->next = b;
                    b = b->next;
                }
                tail = tail->next;
            }
            tail->next = a ? a : b;              // the rest of the other list is already sorted
            return dummy.next;
        }

        int main() {
            cout << toStr(merge(build({10, 20, 30}), build({5, 25}))) << "\\n";
            cout << toStr(merge(build({1, 3, 5}), build({2, 4, 6}))) << "\\n";
            cout << toStr(merge(build({1, 2, 3}), nullptr)) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node merge(Node a, Node b) {
                Node dummy = new Node(0);            // result tail always exists
                Node tail = dummy;
                while (a != null && b != null) {
                    if (a.data <= b.data) {          // take the smaller head (<= keeps it stable)
                        tail.next = a;
                        a = a.next;
                    } else {
                        tail.next = b;
                        b = b.next;
                    }
                    tail = tail.next;
                }
                tail.next = a != null ? a : b;       // the rest of the other list is already sorted
                return dummy.next;
            }

            public static void main(String[] args) {
                System.out.println(toStr(merge(build(new int[]{10, 20, 30}), build(new int[]{5, 25}))));
                System.out.println(toStr(merge(build(new int[]{1, 3, 5}), build(new int[]{2, 4, 6}))));
                System.out.println(toStr(merge(build(new int[]{1, 2, 3}), null)));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function merge(a, b) {
            const dummy = new Node(0);               // result tail always exists
            let tail = dummy;
            while (a && b) {
                if (a.data <= b.data) {              // take the smaller head (<= keeps it stable)
                    tail.next = a;
                    a = a.next;
                } else {
                    tail.next = b;
                    b = b.next;
                }
                tail = tail.next;
            }
            tail.next = a ? a : b;                   // the rest of the other list is already sorted
            return dummy.next;
        }

        console.log(toStr(merge(build([10, 20, 30]), build([5, 25]))));
        console.log(toStr(merge(build([1, 3, 5]), build([2, 4, 6]))));
        console.log(toStr(merge(build([1, 2, 3]), null)));
    ''')
    yield complexity("O(m + n)", "O(1)")
    yield p("The same idea reads naturally as recursion — the head of the merged list is the smaller head, and its `next` is the merge of what remains. Elegant, but it uses one stack frame per node, so keep it for short lists:")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def merge_rec(a, b):
            if a is None:
                return b
            if b is None:
                return a
            if a.data <= b.data:
                a.next = merge_rec(a.next, b)    # a is the head, merge the rest behind it
                return a
            b.next = merge_rec(a, b.next)
            return b

        print(to_str(merge_rec(build([10, 20, 30]), build([5, 25]))))
    ''', out="5 10 20 25 30")
    yield note("Merge is the building block of **merge sort on a linked list** — the sorting algorithm of choice for lists, because splitting (find the middle with slow/fast) and merging need no random access and no extra array: `O(n log n)` time, `O(log n)` stack. Merging `k` sorted lists uses a min-heap of the `k` current heads.")

    yield section("Palindrome linked list", "arrows-left-right")
    yield io("1 → 2 → 3 → 2 → 1", "Yes", "1 → 2 → 3 → 4", "No", "R → A → D → A → R", "Yes")
    yield p("**Naive — copy the values onto a stack.** Push every value, then walk the list again popping: pops come out in reverse order, so each pop must equal the current node. `O(n)` time but `O(n)` extra space.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def is_palindrome_stack(head):
            stack = []
            curr = head
            while curr:
                stack.append(curr.data)
                curr = curr.next
            curr = head
            while curr:
                if stack.pop() != curr.data:     # pops come out reversed
                    return False
                curr = curr.next
            return True

        for values in ([1, 2, 3, 2, 1], [1, 2, 3, 4]):
            print("Yes" if is_palindrome_stack(build(values)) else "No")
    ''', out='''
        Yes
        No
    ''')
    yield p("**Efficient — reverse the second half in place.** Find the end of the first half with slow/fast, reverse the second half, and walk the two halves together comparing values. Then reverse the second half again to restore the list — callers do not expect a read-only query to scramble their data.")
    yield idea("A palindrome reads the same backwards. Reversing just the second half turns “compare position `i` with position `n − 1 − i`” into a plain forward walk over two lists of (almost) equal length — no index arithmetic, no extra memory.")
    yield diagram('''
        1 → 2 → 3 → 2 → 1          slow stops at 3 (end of first half); second half = 2 → 1

        reverse second half:       1 → 2 → 3 → 1 → 2
                                   ↑           ↑
                                   a           b      compare a, b while b exists: 1=1, 2=2 → Yes
        restore:                   1 → 2 → 3 → 2 → 1
    ''', "Odd length: the middle node belongs to the first half and is never compared")
    yield multi('''
        1 2 3 2 1 → Yes
        1 2 3 4 → No
        1 2 2 1 → Yes
        list after the check: 1 2 3 2 1
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def build(values):
            head = None
            for v in reversed(values):
                node = Node(v)
                node.next = head
                head = node
            return head

        def to_str(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            return " ".join(parts)

        def reverse(head):
            prev = None
            while head:
                nxt = head.next
                head.next = prev
                prev = head
                head = nxt
            return prev

        def is_palindrome(head):
            if head is None or head.next is None:
                return True
            slow = fast = head
            while fast.next and fast.next.next:  # slow stops at the end of the first half
                slow = slow.next
                fast = fast.next.next
            second = reverse(slow.next)          # reverse the second half
            a, b = head, second
            same = True
            while b:                             # second half is never longer than the first
                if a.data != b.data:
                    same = False
                    break
                a = a.next
                b = b.next
            slow.next = reverse(second)          # restore the list
            return same

        for values in ([1, 2, 3, 2, 1], [1, 2, 3, 4], [1, 2, 2, 1]):
            head = build(values)
            print(to_str(head), "→", "Yes" if is_palindrome(head) else "No")
        head = build([1, 2, 3, 2, 1])
        is_palindrome(head)
        print("list after the check:", to_str(head))
    ''', cpp='''
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* build(const vector<int>& v) {
            Node* head = nullptr;
            for (int i = (int)v.size() - 1; i >= 0; i--) {
                Node* node = new Node(v[i]);
                node->next = head;
                head = node;
            }
            return head;
        }

        string toStr(Node* head) {
            string s;
            for (Node* c = head; c; c = c->next) s += to_string(c->data) + (c->next ? " " : "");
            return s;
        }

        Node* reverse(Node* head) {
            Node* prev = nullptr;
            while (head) {
                Node* next = head->next;
                head->next = prev;
                prev = head;
                head = next;
            }
            return prev;
        }

        bool isPalindrome(Node* head) {
            if (!head || !head->next) return true;
            Node* slow = head;
            Node* fast = head;
            while (fast->next && fast->next->next) {   // slow stops at the end of the first half
                slow = slow->next;
                fast = fast->next->next;
            }
            Node* second = reverse(slow->next);        // reverse the second half
            bool same = true;
            for (Node *a = head, *b = second; b; a = a->next, b = b->next)   // second half is never longer
                if (a->data != b->data) { same = false; break; }
            slow->next = reverse(second);              // restore the list
            return same;
        }

        int main() {
            for (vector<int> values : {vector<int>{1, 2, 3, 2, 1}, vector<int>{1, 2, 3, 4}, vector<int>{1, 2, 2, 1}}) {
                Node* head = build(values);
                cout << toStr(head) << " → " << (isPalindrome(head) ? "Yes" : "No") << "\\n";
            }
            Node* head = build({1, 2, 3, 2, 1});
            isPalindrome(head);
            cout << "list after the check: " << toStr(head) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node build(int[] v) {
                Node head = null;
                for (int i = v.length - 1; i >= 0; i--) {
                    Node node = new Node(v[i]);
                    node.next = head;
                    head = node;
                }
                return head;
            }

            static String toStr(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node c = head; c != null; c = c.next) sb.append(c.data).append(c.next != null ? " " : "");
                return sb.toString();
            }

            static Node reverse(Node head) {
                Node prev = null;
                while (head != null) {
                    Node next = head.next;
                    head.next = prev;
                    prev = head;
                    head = next;
                }
                return prev;
            }

            static boolean isPalindrome(Node head) {
                if (head == null || head.next == null) return true;
                Node slow = head, fast = head;
                while (fast.next != null && fast.next.next != null) {   // slow stops at the end of the first half
                    slow = slow.next;
                    fast = fast.next.next;
                }
                Node second = reverse(slow.next);        // reverse the second half
                boolean same = true;
                for (Node a = head, b = second; b != null; a = a.next, b = b.next)   // second half is never longer
                    if (a.data != b.data) { same = false; break; }
                slow.next = reverse(second);             // restore the list
                return same;
            }

            public static void main(String[] args) {
                for (int[] values : new int[][]{{1, 2, 3, 2, 1}, {1, 2, 3, 4}, {1, 2, 2, 1}}) {
                    Node head = build(values);
                    System.out.println(toStr(head) + " → " + (isPalindrome(head) ? "Yes" : "No"));
                }
                Node head = build(new int[]{1, 2, 3, 2, 1});
                isPalindrome(head);
                System.out.println("list after the check: " + toStr(head));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function build(values) {
            let head = null;
            for (let i = values.length - 1; i >= 0; i--) {
                const node = new Node(values[i]);
                node.next = head;
                head = node;
            }
            return head;
        }

        function toStr(head) {
            const parts = [];
            for (let c = head; c; c = c.next) parts.push(c.data);
            return parts.join(" ");
        }

        function reverse(head) {
            let prev = null;
            while (head) {
                const next = head.next;
                head.next = prev;
                prev = head;
                head = next;
            }
            return prev;
        }

        function isPalindrome(head) {
            if (!head || !head.next) return true;
            let slow = head, fast = head;
            while (fast.next && fast.next.next) {    // slow stops at the end of the first half
                slow = slow.next;
                fast = fast.next.next;
            }
            const second = reverse(slow.next);       // reverse the second half
            let same = true;
            for (let a = head, b = second; b; a = a.next, b = b.next)   // second half is never longer
                if (a.data !== b.data) { same = false; break; }
            slow.next = reverse(second);             // restore the list
            return same;
        }

        for (const values of [[1, 2, 3, 2, 1], [1, 2, 3, 4], [1, 2, 2, 1]]) {
            const head = build(values);
            console.log(toStr(head), "→", isPalindrome(head) ? "Yes" : "No");
        }
        const head = build([1, 2, 3, 2, 1]);
        isPalindrome(head);
        console.log("list after the check:", toStr(head));
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Use the `fast.next and fast.next.next` loop condition so that `slow` lands on the **end of the first half** (the middle node for odd length). With the plain `fast and fast.next` condition from the middle-finding problem, `slow` would be one node too far and the halves misaligned. Returning early on a mismatch without restoring the list is the other classic slip — the version above breaks out, restores, then returns.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why does Floyd's algorithm use speeds 1 and 2 — would 1 and 3 work?",
             "Any two different speeds work for *detection*: once both pointers are in a loop of length `n`, the gap changes by a constant each step and eventually hits a multiple of `n`. Speeds 1 and 2 are chosen because the gap shrinks by exactly one per step (guaranteeing a meeting within `n` steps of entering the loop) and because the `m + k = multiple of n` identity makes finding the loop *start* a one-liner. With speed 3 the second phase no longer works unchanged.")
    yield qa("How do you find the start of the loop after detecting it, and why does it work?",
             "Keep one pointer at the meeting point and move the other back to the head; advance both one step at a time — they meet at the loop's first node. Proof: with `m` = head-to-loop-start, `k` = loop-start-to-meeting-point and `n` = loop length, `fast` has travelled twice as far as `slow`, which gives `m + k = (y − 2x)·n`, a multiple of `n`. So after `m` steps the pointer from the meeting point has gone `m + k ≡ 0 (mod n)` into the loop — it is at the loop start, exactly where the pointer from the head has also arrived.")
    yield qa("How would you detect a loop or find an intersection without Floyd's algorithm?",
             "Hash the node references: a set of visited nodes finds a loop (first repeat) or an intersection (first node of `B` already seen while walking `A`) in `O(n)` time and `O(n)` space. It is the baseline — mention it first, then improve to `O(1)` space with slow/fast pointers or length alignment.")
    yield qa("Reverse a linked list in O(1) space — iterative or recursive?",
             "Iterative: three pointers (`prev`, `curr`, `next`) in one pass, `O(1)` extra space. The recursive version is shorter to write but uses `O(n)` stack — one frame per node — and overflows on long lists. Interviewers usually want the iterative version and then ask for the recursive one as a follow-up (or vice versa).")
    yield qa("What is the dummy-head trick and when do you use it?",
             "Create a throwaway node whose `next` is the real head, and work from it. Every operation that might change the head (insert at front, delete the first node, merge, pairwise swap) then has no special case — the first real node is just “the node after dummy”. Return `dummy.next` at the end. It costs one allocation and saves a branch and a bug.")
    yield qa("Clone a list with random pointers in O(1) extra space — how?",
             "Interleave: insert each node's copy right after it (`1 → 1' → 2 → 2' …`), so the copy of any node `x` is `x.next`. Set `x.next.random = x.random.next` for every original, then unweave the two lists in one more pass. Three passes, `O(n)` time, no map. The hash-map version is the simpler `O(n)`-space baseline.")
    yield qa("Which sorting algorithm fits a linked list best, and why not quicksort?",
             "Merge sort: split with slow/fast pointers, merge by re-linking nodes — `O(n log n)` with no random access and no extra array. Quicksort and heapsort need `O(1)` index access to partition or sift; on a list every `arr[i]` becomes an `O(n)` walk.")
