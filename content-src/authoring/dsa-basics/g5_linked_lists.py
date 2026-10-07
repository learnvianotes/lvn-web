from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Linked Lists"


@topic(G, "singly_linked", "Linked List", "link")
def _():
    yield lead("A linked list is a linear collection whose elements are **not** stored next to each other in memory: every node holds a value and a pointer to the next node. Insertion and deletion at a known position are O(1), at the price of O(n) access by index.")
    yield define("Singly linked list", "a sequence of **nodes**, each containing a `data` field and a `next` reference to the following node. The first node is the **head**; the list ends at the node whose `next` is `None`/`null`. Only the head is stored — everything else is reached by following `next` pointers.")
    yield diagram('''
        head
         ↓
        ┌──────┬──────┐    ┌──────┬──────┐    ┌──────┬──────┐
        │  10  │  ●───┼───▶│  20  │  ●───┼───▶│  30  │  ∅   │
        └──────┴──────┘    └──────┴──────┘    └──────┴──────┘
          data   next        data   next        data   next = None (end of list)
    ''', "A singly linked list with three nodes — only the head reference is stored by the program")

    yield section("Structure of a node", "box")
    yield p("A node is a tiny object (or struct) with two fields. Nodes are allocated one at a time, so the list grows and shrinks without ever copying or resizing an array. Traversal starts at the head and follows `next` until it becomes `None`.")
    yield multi('''
        10 -> 20 -> 30
        length: 3
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None             # no next node yet

        def show(head):
            parts = []
            curr = head
            while curr is not None:          # traversal: follow next until the end
                parts.append(str(curr.data))
                curr = curr.next
            print(" -> ".join(parts))

        def length(head):
            n, curr = 0, head
            while curr:
                n += 1
                curr = curr.next
            return n

        head = Node(10)                      # build by hand: 10 -> 20 -> 30
        head.next = Node(20)
        head.next.next = Node(30)
        show(head)
        print("length:", length(head))
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data;
            Node* next;
            Node(int d) : data(d), next(nullptr) {}   // no next node yet
        };

        void show(Node* head) {
            for (Node* curr = head; curr; curr = curr->next) {   // traversal: follow next until null
                cout << curr->data;
                if (curr->next) cout << " -> ";
            }
            cout << "\\n";
        }

        int length(Node* head) {
            int n = 0;
            for (Node* curr = head; curr; curr = curr->next) n++;
            return n;
        }

        int main() {
            Node* head = new Node(10);           // build by hand: 10 -> 20 -> 30
            head->next = new Node(20);
            head->next->next = new Node(30);
            show(head);
            cout << "length: " << length(head) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;              // next stays null until linked
                Node(int d) { data = d; }
            }

            static void show(Node head) {
                StringBuilder sb = new StringBuilder();
                for (Node curr = head; curr != null; curr = curr.next) {   // traversal
                    sb.append(curr.data);
                    if (curr.next != null) sb.append(" -> ");
                }
                System.out.println(sb);
            }

            static int length(Node head) {
                int n = 0;
                for (Node curr = head; curr != null; curr = curr.next) n++;
                return n;
            }

            public static void main(String[] args) {
                Node head = new Node(10);         // build by hand: 10 -> 20 -> 30
                head.next = new Node(20);
                head.next.next = new Node(30);
                show(head);
                System.out.println("length: " + length(head));
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }   // no next node yet
        }

        function show(head) {
            const parts = [];
            for (let curr = head; curr !== null; curr = curr.next)     // traversal
                parts.push(curr.data);
            console.log(parts.join(" -> "));
        }

        function length(head) {
            let n = 0;
            for (let curr = head; curr !== null; curr = curr.next) n++;
            return n;
        }

        const head = new Node(10);               // build by hand: 10 -> 20 -> 30
        head.next = new Node(20);
        head.next.next = new Node(30);
        show(head);
        console.log("length:", length(head));
    ''')
    yield complexity("O(n) traversal", "O(n) for n nodes")
    yield note("The list has no `size` unless you maintain a counter: `length` walks all nodes in O(n). Real implementations wrap the head in a `LinkedList` class that also stores `size` (and often a `tail`).")

    yield section("Why — and why not — a linked list", "scale")
    yield cards(
        ("Dynamic size", "Grows one node at a time; no capacity to guess, no O(n) resize copy.", "arrows-maximize"),
        ("O(1) insert / delete at a known node", "Re-link two pointers. An array must shift every later element.", "bolt"),
        ("No contiguous block needed", "Nodes can live anywhere in memory — useful when large arrays cannot be allocated.", "grid-dots"),
        ("No random access", "`list[i]` means walking `i` nodes: O(n). Binary search is impossible.", "search-off"),
        ("Extra memory", "One pointer per element (8 bytes on 64-bit) — a list of small ints doubles its footprint.", "database"),
        ("Cache unfriendly", "Nodes are scattered; each `next` is a potential cache miss, so traversals are slower than over an array of the same size.", "cpu"),
        cols=3,
    )
    yield p("Linked lists are the building block of other structures: stacks and queues (O(1) at the ends), hash-table chains, adjacency lists in graphs, and the LRU cache (a doubly linked list plus a hash map).")

    yield section("Operations and their cost", "list-check")
    yield table(
        ["Operation", "Time", "Why"],
        ["Insert at beginning", "O(1)", "New node points at the old head; the head reference moves. No traversal."],
        ["Insert at end", "O(n) — O(1) with a tail pointer", "Without a tail you must walk to the last node first."],
        ["Delete head", "O(1)", "Head moves to `head.next`."],
        ["Delete last", "O(n)", "Need the *second-to-last* node to clear its `next`; a singly linked list cannot go backwards."],
        ["Insert / delete after a given node", "O(1)", "Only pointers of the given node and its neighbour change."],
        ["Search", "O(n)", "Sequential scan; nothing better is possible without random access."],
        ["Access by index", "O(n)", "Walk `i` links."],
    )

    yield section("Insert at the beginning", "arrow-bar-to-left")
    yield io("list = 20 -> 30, insert 10 at the beginning", "10 -> 20 -> 30")
    yield idea("Create the node, make it point at the current head, and return it as the new head. No node is visited, so it is O(1) regardless of the list length — the one place where a linked list beats an array outright.")
    yield diagram('''
        before:   head ──▶ [20] ──▶ [30] ──▶ ∅

        step 1:   new = [10]           new.next = head        [10] ──▶ [20] ──▶ [30] ──▶ ∅
        step 2:   head = new                                   head ──▶ [10] ──▶ [20] ──▶ [30] ──▶ ∅
    ''', "Insert at the beginning: two pointer assignments")
    yield multi('''
        30
        20 -> 30
        10 -> 20 -> 30
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def insert_at_beginning(head, data):
            new_node = Node(data)
            new_node.next = head         # new node points at the old head
            return new_node              # it is the new head — caller must store it

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            print(" -> ".join(parts))

        head = None
        for x in (30, 20, 10):           # insert in reverse to get 10 -> 20 -> 30
            head = insert_at_beginning(head, x)
            show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* insertAtBeginning(Node* head, int data) {
            Node* newNode = new Node(data);
            newNode->next = head;        // new node points at the old head
            return newNode;              // it is the new head — caller must store it
        }

        void show(Node* head) {
            for (; head; head = head->next) cout << head->data << (head->next ? " -> " : "\\n");
        }

        int main() {
            Node* head = nullptr;
            for (int x : {30, 20, 10}) {     // insert in reverse to get 10 -> 20 -> 30
                head = insertAtBeginning(head, x);
                show(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node insertAtBeginning(Node head, int data) {
                Node newNode = new Node(data);
                newNode.next = head;         // new node points at the old head
                return newNode;              // it is the new head — caller must store it
            }

            static void show(Node head) {
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " -> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = null;
                for (int x : new int[]{30, 20, 10}) {   // insert in reverse to get 10 -> 20 -> 30
                    head = insertAtBeginning(head, x);
                    show(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function insertAtBeginning(head, data) {
            const newNode = new Node(data);
            newNode.next = head;             // new node points at the old head
            return newNode;                  // it is the new head — caller must store it
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.join(" -> "));
        }

        let head = null;
        for (const x of [30, 20, 10]) {      // insert in reverse to get 10 -> 20 -> 30
            head = insertAtBeginning(head, x);
            show(head);
        }
    ''')
    yield complexity("O(1)", "O(1)")
    yield pitfall("Functions that change the head must **return the new head** (or work on a wrapper object). Writing `insert_at_beginning(head, 10)` without `head = …` leaves the caller pointing at the old second node — the new node is lost.")

    yield section("Insert at the end", "arrow-bar-to-right")
    yield io("list = 10 -> 20, insert 30 at the end", "10 -> 20 -> 30", "list = empty, insert 10", "10")
    yield idea("Walk to the last node (the one whose `next` is `None`) and hang the new node there. The walk makes it O(n); keeping a `tail` pointer in a wrapper class makes it O(1). The empty list is a special case: the new node simply becomes the head.")
    yield multi('''
        10
        10 -> 20
        10 -> 20 -> 30
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def insert_at_end(head, data):
            new_node = Node(data)
            if head is None:                 # empty list: the new node is the head
                return new_node
            current = head
            while current.next is not None:  # O(n) walk to the last node
                current = current.next
            current.next = new_node
            return head                      # head is unchanged

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            print(" -> ".join(parts))

        head = None
        for x in (10, 20, 30):
            head = insert_at_end(head, x)
            show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* insertAtEnd(Node* head, int data) {
            Node* newNode = new Node(data);
            if (!head) return newNode;           // empty list: the new node is the head
            Node* current = head;
            while (current->next) current = current->next;   // O(n) walk to the last node
            current->next = newNode;
            return head;                         // head is unchanged
        }

        void show(Node* head) {
            for (; head; head = head->next) cout << head->data << (head->next ? " -> " : "\\n");
        }

        int main() {
            Node* head = nullptr;
            for (int x : {10, 20, 30}) {
                head = insertAtEnd(head, x);
                show(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node insertAtEnd(Node head, int data) {
                Node newNode = new Node(data);
                if (head == null) return newNode;    // empty list: the new node is the head
                Node current = head;
                while (current.next != null) current = current.next;   // O(n) walk to the last node
                current.next = newNode;
                return head;                         // head is unchanged
            }

            static void show(Node head) {
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " -> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = null;
                for (int x : new int[]{10, 20, 30}) {
                    head = insertAtEnd(head, x);
                    show(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function insertAtEnd(head, data) {
            const newNode = new Node(data);
            if (head === null) return newNode;       // empty list: the new node is the head
            let current = head;
            while (current.next !== null) current = current.next;   // O(n) walk to the last node
            current.next = newNode;
            return head;                             // head is unchanged
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.join(" -> "));
        }

        let head = null;
        for (const x of [10, 20, 30]) {
            head = insertAtEnd(head, x);
            show(head);
        }
    ''')
    yield complexity("O(n) — O(1) with a tail pointer", "O(1)")
    yield note("Building a list of `n` elements by repeated `insert_at_end` costs O(n²) without a tail pointer. Either keep a tail, or insert at the beginning and reverse once at the end.")

    yield section("Delete the head", "arrow-bar-left")
    yield io("list = 10 -> 20 -> 30", "20 -> 30", "list = 10", "empty")
    yield idea("The second node becomes the head: return `head.next`. In C++ free the old node; in Python, Java and JavaScript the garbage collector reclaims it once nothing refers to it. An empty list stays empty.")
    yield multi('''
        10 -> 20 -> 30
        after delete head: 20 -> 30
        after delete head: 30
        after delete head: empty
        after delete head: empty
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def delete_head(head):
            if head is None:
                return None                  # nothing to delete
            return head.next                 # the old head is garbage-collected

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            print(" -> ".join(parts) if parts else "empty")

        head = Node(10); head.next = Node(20); head.next.next = Node(30)
        show(head)
        for _ in range(4):
            head = delete_head(head)
            print("after delete head: ", end="")
            show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* deleteHead(Node* head) {
            if (!head) return nullptr;           // nothing to delete
            Node* next = head->next;
            delete head;                         // free the old head
            return next;
        }

        void show(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            for (; head; head = head->next) cout << head->data << (head->next ? " -> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(20); head->next->next = new Node(30);
            show(head);
            for (int i = 0; i < 4; i++) {
                head = deleteHead(head);
                cout << "after delete head: ";
                show(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node deleteHead(Node head) {
                if (head == null) return null;       // nothing to delete
                return head.next;                    // the old head is garbage-collected
            }

            static void show(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " -> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(20); head.next.next = new Node(30);
                show(head);
                for (int i = 0; i < 4; i++) {
                    head = deleteHead(head);
                    System.out.print("after delete head: ");
                    show(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function deleteHead(head) {
            if (head === null) return null;          // nothing to delete
            return head.next;                        // the old head is garbage-collected
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.length ? parts.join(" -> ") : "empty");
        }

        let head = new Node(10); head.next = new Node(20); head.next.next = new Node(30);
        show(head);
        for (let i = 0; i < 4; i++) {
            head = deleteHead(head);
            process.stdout.write("after delete head: ");
            show(head);
        }
    ''')
    yield complexity("O(1)", "O(1)")

    yield section("Delete the last node", "arrow-bar-right")
    yield io("list = 10 -> 20 -> 30", "10 -> 20", "list = 10", "empty")
    yield idea("A singly linked list cannot step backwards, so to drop the last node we must stop at the **second-to-last** one (`current.next.next is None`) and clear its `next`. That walk is what makes the operation O(n), while deleting the head is O(1).")
    yield multi('''
        10 -> 20 -> 30
        after delete last: 10 -> 20
        after delete last: 10
        after delete last: empty
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def delete_last(head):
            if head is None or head.next is None:
                return None                          # 0 or 1 node → empty list
            current = head
            while current.next.next is not None:     # stop at the second-to-last node
                current = current.next
            current.next = None
            return head

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data))
                head = head.next
            print(" -> ".join(parts) if parts else "empty")

        head = Node(10); head.next = Node(20); head.next.next = Node(30)
        show(head)
        for _ in range(3):
            head = delete_last(head)
            print("after delete last: ", end="")
            show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* deleteLast(Node* head) {
            if (!head || !head->next) { delete head; return nullptr; }   // 0 or 1 node → empty list
            Node* current = head;
            while (current->next->next) current = current->next;        // stop at the second-to-last node
            delete current->next;
            current->next = nullptr;
            return head;
        }

        void show(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            for (; head; head = head->next) cout << head->data << (head->next ? " -> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(20); head->next->next = new Node(30);
            show(head);
            for (int i = 0; i < 3; i++) {
                head = deleteLast(head);
                cout << "after delete last: ";
                show(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node deleteLast(Node head) {
                if (head == null || head.next == null) return null;       // 0 or 1 node → empty list
                Node current = head;
                while (current.next.next != null) current = current.next; // stop at the second-to-last node
                current.next = null;
                return head;
            }

            static void show(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " -> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(20); head.next.next = new Node(30);
                show(head);
                for (int i = 0; i < 3; i++) {
                    head = deleteLast(head);
                    System.out.print("after delete last: ");
                    show(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function deleteLast(head) {
            if (head === null || head.next === null) return null;        // 0 or 1 node → empty list
            let current = head;
            while (current.next.next !== null) current = current.next;   // stop at the second-to-last node
            current.next = null;
            return head;
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.length ? parts.join(" -> ") : "empty");
        }

        let head = new Node(10); head.next = new Node(20); head.next.next = new Node(30);
        show(head);
        for (let i = 0; i < 3; i++) {
            head = deleteLast(head);
            process.stdout.write("after delete last: ");
            show(head);
        }
    ''')
    yield complexity("O(n)", "O(1)")

    yield section("Search in a linked list", "search")
    yield io("list = 10 -> 20 -> 30, target = 20", "position 2", "target = 40", "-1")
    yield idea("Walk from the head comparing each node's data with the target and counting positions (1-indexed). Return the position on a match, `-1` after falling off the end. Without random access, a linear scan is the only option — even on a sorted list.")
    yield multi('''
        search 20: position 2
        search 10: position 1
        search 40: -1
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def search_list(head, target):
            current, position = head, 1
            while current is not None:
                if current.data == target:
                    return position
                current = current.next
                position += 1
            return -1                            # fell off the end

        def report(head, x):
            pos = search_list(head, x)
            print(f"search {x}:", f"position {pos}" if pos != -1 else -1)

        head = Node(10); head.next = Node(20); head.next.next = Node(30)
        for x in (20, 10, 40):
            report(head, x)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        int searchList(Node* head, int target) {
            int position = 1;
            for (Node* current = head; current; current = current->next, position++)
                if (current->data == target) return position;
            return -1;                           // fell off the end
        }

        void report(Node* head, int x) {
            int pos = searchList(head, x);
            cout << "search " << x << ": ";
            if (pos != -1) cout << "position " << pos << "\\n"; else cout << "-1\\n";
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(20); head->next->next = new Node(30);
            for (int x : {20, 10, 40}) report(head, x);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static int searchList(Node head, int target) {
                int position = 1;
                for (Node current = head; current != null; current = current.next, position++)
                    if (current.data == target) return position;
                return -1;                           // fell off the end
            }

            static void report(Node head, int x) {
                int pos = searchList(head, x);
                System.out.println("search " + x + ": " + (pos != -1 ? "position " + pos : "-1"));
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(20); head.next.next = new Node(30);
                for (int x : new int[]{20, 10, 40}) report(head, x);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function searchList(head, target) {
            let position = 1;
            for (let current = head; current !== null; current = current.next, position++)
                if (current.data === target) return position;
            return -1;                               // fell off the end
        }

        function report(head, x) {
            const pos = searchList(head, x);
            console.log(`search ${x}:`, pos !== -1 ? `position ${pos}` : -1);
        }

        const head = new Node(10); head.next = new Node(20); head.next.next = new Node(30);
        for (const x of [20, 10, 40]) report(head, x);
    ''')
    yield complexity("O(n)", "O(1)")

    yield section("Array vs linked list", "scale")
    yield table(
        ["Operation", "Array / dynamic array (contiguous)", "Linked list (pointers)"],
        ["Access by index", "O(1) — address = base + i · size", "O(n) — walk `i` links"],
        ["Search (unsorted)", "O(n)", "O(n)"],
        ["Search (sorted)", "O(log n) binary search", "O(n) — no random access, binary search impossible"],
        ["Insert / delete at start", "O(n) — shift every element", "O(1) — re-link the head"],
        ["Insert / delete at end", "O(1) amortised (occasional resize copy)", "O(n), or O(1) with a tail pointer (delete last stays O(n) for singly linked)"],
        ["Insert / delete in the middle (position known)", "O(n) — shift the tail", "O(1) — once you hold the previous node"],
        ["Extra memory", "None per element; unused capacity in dynamic arrays", "One `next` pointer per node"],
        ["Memory layout", "Contiguous — cache friendly, prefetchable", "Scattered — pointer chasing, cache misses"],
        ["Size", "Fixed, or resized by copying", "Grows node by node"],
    )
    yield good("Default to an array / dynamic array: random access and cache locality win most of the time. Reach for a linked list when you need many O(1) insertions or deletions at known nodes (queues, LRU caches, adjacency lists, splicing lists together) or cannot afford resize copies.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why is inserting at the front O(1) in a linked list but O(n) in an array?",
             "An array keeps elements contiguous, so making room at index 0 means moving every existing element one slot right. A linked list has no positions — a new node just points at the old head and becomes the new head; nothing else moves.")
    yield qa("Why is binary search not possible on a linked list?",
             "Binary search needs the middle element in O(1). In a linked list reaching the middle costs O(n/2) pointer hops, so every probe is O(n) and the search becomes O(n) overall — no better than a linear scan.")
    yield qa("How do you find the middle of a linked list in one pass?",
             "Two pointers: `slow` moves one node per step, `fast` two. When `fast` reaches the end, `slow` is at the middle. The same trick (Floyd's algorithm) detects a cycle: if `fast` ever meets `slow`, the list loops.")
    yield qa("How would you reverse a singly linked list?",
             "Iterate with three pointers `prev`, `curr`, `next`: save `next = curr.next`, redirect `curr.next = prev`, then advance `prev = curr`, `curr = next`. When `curr` is `None`, `prev` is the new head. O(n) time, O(1) space.")
    yield qa("When is a linked list a better choice than a dynamic array?",
             "When the workload is dominated by inserts/deletes at the ends or at nodes you already hold (a queue, an LRU cache, merging sorted lists), when element moves are expensive, or when a guaranteed O(1) without occasional resize pauses matters. For index-heavy or cache-sensitive code, arrays win.")


@topic(G, "circular_linked", "Circular Linked List", "refresh")
def _():
    yield lead("A circular linked list is a singly linked list whose **last node points back to the head** instead of to `None`. There is no end, so the list can be traversed from any node, and keeping a single pointer gives O(1) access to both the first and the last element.")
    yield define("Circular linked list", "a linked list in which the `next` of the last node refers to the first node. A one-node list points to itself. Traversal stops when we return to the node where we started, not when `next` is `None` — because it never is.")
    yield diagram('''
        head
         ↓
        ┌──────┬────┐    ┌──────┬────┐    ┌──────┬────┐    ┌──────┬────┐
        │  10  │ ●──┼───▶│   5  │ ●──┼───▶│  20  │ ●──┼───▶│  15  │ ●──┼──┐
        └──────┴────┘    └──────┴────┘    └──────┴────┘    └──────┴────┘  │
          ▲                                                               │
          └───────────────────────────────────────────────────────────────┘
                        the last node links back to the head
    ''', "10 → 5 → 20 → 15 → back to 10")

    yield section("Building and traversing", "repeat")
    yield p("The nodes are the same as in a singly linked list; only the last link differs. Traversal must **stop when it comes back to the head**, so the loop prints the head first and then walks until `curr == head` again. A `while curr.next != head` loop (as in the original notes) also works but needs the last node printed separately.")
    yield multi('''
        10 -> 5 -> 20 -> 15 -> (back to 10)
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def print_circular(head):
            if head is None:
                print("empty")
                return
            parts = [str(head.data)]
            curr = head.next
            while curr != head:              # stop when we are back at the start
                parts.append(str(curr.data))
                curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10)
        head.next = Node(5)
        head.next.next = Node(20)
        head.next.next.next = Node(15)
        head.next.next.next.next = head      # close the circle
        print_circular(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        void printCircular(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            cout << head->data;
            for (Node* curr = head->next; curr != head; curr = curr->next)   // stop when back at the start
                cout << " -> " << curr->data;
            cout << " -> (back to " << head->data << ")\\n";
        }

        int main() {
            Node* head = new Node(10);
            head->next = new Node(5);
            head->next->next = new Node(20);
            head->next->next->next = new Node(15);
            head->next->next->next->next = head;    // close the circle
            printCircular(head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static void printCircular(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder().append(head.data);
                for (Node curr = head.next; curr != head; curr = curr.next)   // stop when back at the start
                    sb.append(" -> ").append(curr.data);
                System.out.println(sb + " -> (back to " + head.data + ")");
            }

            public static void main(String[] args) {
                Node head = new Node(10);
                head.next = new Node(5);
                head.next.next = new Node(20);
                head.next.next.next = new Node(15);
                head.next.next.next.next = head;    // close the circle
                printCircular(head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function printCircular(head) {
            if (head === null) { console.log("empty"); return; }
            const parts = [head.data];
            for (let curr = head.next; curr !== head; curr = curr.next)   // stop when back at the start
                parts.push(curr.data);
            console.log(parts.join(" -> "), `-> (back to ${head.data})`);
        }

        const head = new Node(10);
        head.next = new Node(5);
        head.next.next = new Node(20);
        head.next.next.next = new Node(15);
        head.next.next.next.next = head;        // close the circle
        printCircular(head);
    ''')
    yield complexity("O(n) traversal", "O(1)")
    yield pitfall("A `while curr is not None` loop never terminates on a circular list. Every traversal must remember where it started and stop there.")

    yield section("Advantages and disadvantages", "scale")
    yield cards(
        ("Traverse from any node", "Starting anywhere, following `next` visits every node — no need to find the head first.", "refresh"),
        ("Round-robin scheduling", "The OS gives each process a time slice and moves to `next`; after the last process comes the first again. Also: multiplayer turns, circular buffers, music playlists on repeat.", "clock"),
        ("O(1) at both ends with one pointer", "Keep a reference to the **tail**: the head is `tail.next`, so insert at the beginning, insert at the end and delete the head are all O(1).", "bolt"),
        ("More complex code", "Every operation must handle the empty list, the one-node list (which points at itself) and the wrap-around; an off-by-one gives an infinite loop instead of a crash.", "alert-triangle"),
        cols=2,
    )
    yield table(
        ["Operation (holding `head` only)", "Naive", "Efficient trick", "Holding `tail` instead"],
        ["Insert at beginning", "O(n): walk to the last node to fix its `next`", "O(1): insert *after* head and swap data", "O(1)"],
        ["Insert at end", "O(n): walk to the last node", "O(1): same trick, return the new node as head", "O(1)"],
        ["Delete head", "O(n): walk to the last node to re-point it", "O(1): copy `head.next` into head and unlink `head.next`", "O(1)"],
        ["Delete k-th node", "O(k)", "—", "O(k)"],
        ["Search", "O(n)", "—", "O(n)"],
    )

    yield section("Insert at the beginning", "arrow-bar-to-left")
    yield io("list = 10 -> 5 -> 20 -> 15 (circular), insert 25 at the beginning", "25 -> 10 -> 5 -> 20 -> 15 -> (back to 25)")
    yield p("**Naive, O(n).** The last node must point at the new head, and the only way to reach the last node is to walk the whole circle.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def insert_beginning_naive(head, x):
            temp = Node(x)
            if head is None:
                temp.next = temp               # one node points at itself
                return temp
            curr = head
            while curr.next != head:           # O(n) walk to the last node
                curr = curr.next
            curr.next = temp                   # last node → new node
            temp.next = head                   # new node → old head
            return temp

        def print_circular(head):
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        head = insert_beginning_naive(head, 25)
        print_circular(head)
    ''', out="25 -> 10 -> 5 -> 20 -> 15 -> (back to 25)")
    yield complexity("O(n)", "O(1)")
    yield idea("**Efficient, O(1).** Insert the new node *right after* the head (two pointer changes — no walk) and then **swap the data** of the head and the new node. The head node now carries the new value and the old head value sits in second position: exactly the result of inserting at the front. The head reference does not even change.")
    yield diagram('''
        before:          head ──▶ [10] ──▶ [5] ──▶ [20] ──▶ [15] ──▶ back to 10
        insert after head:   head ──▶ [10] ──▶ [25] ──▶ [5] ──▶ [20] ──▶ [15] ──▶ back to 10
        swap data:           head ──▶ [25] ──▶ [10] ──▶ [5] ──▶ [20] ──▶ [15] ──▶ back to 25
    ''', "Insert at the beginning in O(1): insert after the head, then swap the two values")
    yield multi('''
        25 -> 10 -> 5 -> 20 -> 15 -> (back to 25)
        30 -> 25 -> 10 -> 5 -> 20 -> 15 -> (back to 30)
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def insert_beginning(head, x):
            temp = Node(x)
            if head is None:
                temp.next = temp                             # one node points at itself
                return temp
            temp.next = head.next                            # insert temp right after head
            head.next = temp
            head.data, temp.data = temp.data, head.data      # swap values: head now holds x
            return head

        def print_circular(head):
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        head = insert_beginning(head, 25); print_circular(head)
        head = insert_beginning(head, 30); print_circular(head)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* insertBeginning(Node* head, int x) {
            Node* temp = new Node(x);
            if (!head) { temp->next = temp; return temp; }   // one node points at itself
            temp->next = head->next;                         // insert temp right after head
            head->next = temp;
            swap(head->data, temp->data);                    // swap values: head now holds x
            return head;
        }

        void printCircular(Node* head) {
            cout << head->data;
            for (Node* curr = head->next; curr != head; curr = curr->next) cout << " -> " << curr->data;
            cout << " -> (back to " << head->data << ")\\n";
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(5); head->next->next = new Node(20);
            head->next->next->next = new Node(15); head->next->next->next->next = head;
            head = insertBeginning(head, 25); printCircular(head);
            head = insertBeginning(head, 30); printCircular(head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node insertBeginning(Node head, int x) {
                Node temp = new Node(x);
                if (head == null) { temp.next = temp; return temp; }   // one node points at itself
                temp.next = head.next;                                  // insert temp right after head
                head.next = temp;
                int t = head.data; head.data = temp.data; temp.data = t; // swap values: head now holds x
                return head;
            }

            static void printCircular(Node head) {
                StringBuilder sb = new StringBuilder().append(head.data);
                for (Node curr = head.next; curr != head; curr = curr.next) sb.append(" -> ").append(curr.data);
                System.out.println(sb + " -> (back to " + head.data + ")");
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
                head.next.next.next = new Node(15); head.next.next.next.next = head;
                head = insertBeginning(head, 25); printCircular(head);
                head = insertBeginning(head, 30); printCircular(head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function insertBeginning(head, x) {
            const temp = new Node(x);
            if (head === null) { temp.next = temp; return temp; }   // one node points at itself
            temp.next = head.next;                                   // insert temp right after head
            head.next = temp;
            [head.data, temp.data] = [temp.data, head.data];         // swap values: head now holds x
            return head;
        }

        function printCircular(head) {
            const parts = [head.data];
            for (let curr = head.next; curr !== head; curr = curr.next) parts.push(curr.data);
            console.log(parts.join(" -> "), `-> (back to ${head.data})`);
        }

        let head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
        head.next.next.next = new Node(15); head.next.next.next.next = head;
        head = insertBeginning(head, 25); printCircular(head);
        head = insertBeginning(head, 30); printCircular(head);
    ''')
    yield complexity("O(1)", "O(1)")
    yield pitfall("The swap trick moves a *value* into a different node. If other code holds references to specific nodes (or the data is large/expensive to copy), use the tail-pointer design instead: with `tail` known, `head = tail.next` and both ends are O(1) without any swapping.")

    yield section("Insert at the end", "arrow-bar-to-right")
    yield io("list = 10 -> 5 -> 20 -> 15 (circular), insert 35 at the end", "10 -> 5 -> 20 -> 15 -> 35 -> (back to 10)")
    yield p("**Naive, O(n).** Walk to the last node, link it to the new node and link the new node back to the head.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def insert_end_naive(head, x):
            temp = Node(x)
            if head is None:
                temp.next = temp
                return temp
            curr = head
            while curr.next != head:           # O(n) walk to the last node
                curr = curr.next
            curr.next = temp                   # last → new
            temp.next = head                   # new → head
            return head

        def print_circular(head):
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        head = insert_end_naive(head, 35)
        print_circular(head)
    ''', out="10 -> 5 -> 20 -> 15 -> 35 -> (back to 10)")
    yield complexity("O(n)", "O(1)")
    yield idea("**Efficient, O(1).** Same trick as before — insert the new node after the head and swap the values — but now **return the new node as the head**. Reading the circle from that node gives the old sequence first and the new value last: the head node (which now holds `x`) comes just before it.")
    yield multi('''
        10 -> 5 -> 20 -> 15 -> 35 -> (back to 10)
        10 -> 5 -> 20 -> 15 -> 35 -> 40 -> (back to 10)
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def insert_end(head, x):
            temp = Node(x)
            if head is None:
                temp.next = temp
                return temp
            temp.next = head.next                            # insert temp right after head
            head.next = temp
            head.data, temp.data = temp.data, head.data      # old head value moves to temp
            return temp                                      # temp is the new head; x sits just before it

        def print_circular(head):
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        head = insert_end(head, 35); print_circular(head)
        head = insert_end(head, 40); print_circular(head)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* insertEnd(Node* head, int x) {
            Node* temp = new Node(x);
            if (!head) { temp->next = temp; return temp; }
            temp->next = head->next;                         // insert temp right after head
            head->next = temp;
            swap(head->data, temp->data);                    // old head value moves to temp
            return temp;                                     // temp is the new head; x sits just before it
        }

        void printCircular(Node* head) {
            cout << head->data;
            for (Node* curr = head->next; curr != head; curr = curr->next) cout << " -> " << curr->data;
            cout << " -> (back to " << head->data << ")\\n";
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(5); head->next->next = new Node(20);
            head->next->next->next = new Node(15); head->next->next->next->next = head;
            head = insertEnd(head, 35); printCircular(head);
            head = insertEnd(head, 40); printCircular(head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node insertEnd(Node head, int x) {
                Node temp = new Node(x);
                if (head == null) { temp.next = temp; return temp; }
                temp.next = head.next;                                   // insert temp right after head
                head.next = temp;
                int t = head.data; head.data = temp.data; temp.data = t;  // old head value moves to temp
                return temp;                                             // temp is the new head; x sits just before it
            }

            static void printCircular(Node head) {
                StringBuilder sb = new StringBuilder().append(head.data);
                for (Node curr = head.next; curr != head; curr = curr.next) sb.append(" -> ").append(curr.data);
                System.out.println(sb + " -> (back to " + head.data + ")");
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
                head.next.next.next = new Node(15); head.next.next.next.next = head;
                head = insertEnd(head, 35); printCircular(head);
                head = insertEnd(head, 40); printCircular(head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function insertEnd(head, x) {
            const temp = new Node(x);
            if (head === null) { temp.next = temp; return temp; }
            temp.next = head.next;                                   // insert temp right after head
            head.next = temp;
            [head.data, temp.data] = [temp.data, head.data];         // old head value moves to temp
            return temp;                                             // temp is the new head; x sits just before it
        }

        function printCircular(head) {
            const parts = [head.data];
            for (let curr = head.next; curr !== head; curr = curr.next) parts.push(curr.data);
            console.log(parts.join(" -> "), `-> (back to ${head.data})`);
        }

        let head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
        head.next.next.next = new Node(15); head.next.next.next.next = head;
        head = insertEnd(head, 35); printCircular(head);
        head = insertEnd(head, 40); printCircular(head);
    ''')
    yield complexity("O(1)", "O(1)")

    yield section("Delete the head", "arrow-bar-left")
    yield io("list = 10 -> 5 -> 20 -> 15 (circular)", "5 -> 20 -> 15 -> (back to 5)", "list = 10 (one node)", "empty")
    yield p("**Naive, O(n).** The last node points at the head, so after removing the head the last node must be found and re-pointed at the second node — a full walk.")
    yield snippet("py", '''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def delete_head_naive(head):
            if head is None or head.next == head:   # empty or single node → empty
                return None
            curr = head
            while curr.next != head:                # O(n) walk to the last node
                curr = curr.next
            curr.next = head.next                   # last → second node
            return curr.next                        # second node is the new head

        def print_circular(head):
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        head = delete_head_naive(head)
        print_circular(head)
    ''', out="5 -> 20 -> 15 -> (back to 5)")
    yield complexity("O(n)", "O(1)")
    yield idea("**Efficient, O(1).** Instead of removing the head node, **copy the second node's value into it** and unlink the second node. The head node object survives, so the last node's back-pointer stays valid without any walk.")
    yield multi('''
        5 -> 20 -> 15 -> (back to 5)
        20 -> 15 -> (back to 20)
        15 -> (back to 15)
        empty
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def delete_head(head):
            if head is None or head.next == head:   # empty or single node → empty
                return None
            head.data = head.next.data               # pull the second value into the head node
            head.next = head.next.next               # unlink the second node
            return head

        def print_circular(head):
            if head is None:
                print("empty"); return
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        for _ in range(4):
            head = delete_head(head)
            print_circular(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* deleteHead(Node* head) {
            if (!head) return nullptr;
            if (head->next == head) { delete head; return nullptr; }   // single node → empty
            Node* second = head->next;
            head->data = second->data;               // pull the second value into the head node
            head->next = second->next;               // unlink the second node
            delete second;
            return head;
        }

        void printCircular(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            cout << head->data;
            for (Node* curr = head->next; curr != head; curr = curr->next) cout << " -> " << curr->data;
            cout << " -> (back to " << head->data << ")\\n";
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(5); head->next->next = new Node(20);
            head->next->next->next = new Node(15); head->next->next->next->next = head;
            for (int i = 0; i < 4; i++) {
                head = deleteHead(head);
                printCircular(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node deleteHead(Node head) {
                if (head == null || head.next == head) return null;   // empty or single node → empty
                head.data = head.next.data;              // pull the second value into the head node
                head.next = head.next.next;              // unlink the second node
                return head;
            }

            static void printCircular(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder().append(head.data);
                for (Node curr = head.next; curr != head; curr = curr.next) sb.append(" -> ").append(curr.data);
                System.out.println(sb + " -> (back to " + head.data + ")");
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
                head.next.next.next = new Node(15); head.next.next.next.next = head;
                for (int i = 0; i < 4; i++) {
                    head = deleteHead(head);
                    printCircular(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function deleteHead(head) {
            if (head === null || head.next === head) return null;    // empty or single node → empty
            head.data = head.next.data;                  // pull the second value into the head node
            head.next = head.next.next;                  // unlink the second node
            return head;
        }

        function printCircular(head) {
            if (head === null) { console.log("empty"); return; }
            const parts = [head.data];
            for (let curr = head.next; curr !== head; curr = curr.next) parts.push(curr.data);
            console.log(parts.join(" -> "), `-> (back to ${head.data})`);
        }

        let head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
        head.next.next.next = new Node(15); head.next.next.next.next = head;
        for (let i = 0; i < 4; i++) {
            head = deleteHead(head);
            printCircular(head);
        }
    ''')
    yield complexity("O(1)", "O(1)")

    yield section("Delete the k-th node", "list-numbers")
    yield io("list = 10 -> 5 -> 20 -> 15 (circular), k = 2", "10 -> 20 -> 15 -> (back to 10)", "k = 1", "5 -> 20 -> 15 -> (back to 5)")
    yield idea("`k = 1` is the head — reuse `delete_head`. Otherwise walk to the `(k-1)`-th node, which takes `k - 2` steps from the head, and bypass its successor: `curr.next = curr.next.next`. The circle stays closed because the bypassed node's `next` is reused.")
    yield steps(
        ("Empty list", "Return `None`."),
        ("`k == 1`", "Return `delete_head(head)` — the O(1) version above."),
        ("Walk", "`curr = head`; move `k - 2` times → `curr` is the `(k-1)`-th node."),
        ("Bypass", "`curr.next = curr.next.next` removes the `k`-th node."),
    )
    yield multi('''
        10 -> 5 -> 20 -> 15 -> (back to 10)
        delete 2nd: 10 -> 20 -> 15 -> (back to 10)
        delete 3rd: 10 -> 20 -> (back to 10)
        delete 1st: 20 -> (back to 20)
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.next = None

        def delete_head(head):
            if head is None or head.next == head:
                return None
            head.data = head.next.data
            head.next = head.next.next
            return head

        def delete_kth(head, k):
            if head is None:
                return None
            if k == 1:
                return delete_head(head)
            curr = head
            for _ in range(k - 2):                   # k-2 steps reach the (k-1)-th node
                curr = curr.next
            curr.next = curr.next.next               # bypass the k-th node
            return head

        def print_circular(head):
            parts, curr = [str(head.data)], head.next
            while curr != head:
                parts.append(str(curr.data)); curr = curr.next
            print(" -> ".join(parts), f"-> (back to {head.data})")

        head = Node(10); head.next = Node(5); head.next.next = Node(20); head.next.next.next = Node(15)
        head.next.next.next.next = head
        print_circular(head)
        for k, label in ((2, "2nd"), (3, "3rd"), (1, "1st")):
            head = delete_kth(head, k)
            print(f"delete {label}: ", end=""); print_circular(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* next;
            Node(int d) : data(d), next(nullptr) {}
        };

        Node* deleteHead(Node* head) {
            if (!head) return nullptr;
            if (head->next == head) { delete head; return nullptr; }
            Node* second = head->next;
            head->data = second->data; head->next = second->next;
            delete second;
            return head;
        }

        Node* deleteKth(Node* head, int k) {
            if (!head) return nullptr;
            if (k == 1) return deleteHead(head);
            Node* curr = head;
            for (int i = 0; i < k - 2; i++) curr = curr->next;   // k-2 steps reach the (k-1)-th node
            Node* victim = curr->next;
            curr->next = victim->next;                           // bypass the k-th node
            delete victim;
            return head;
        }

        void printCircular(Node* head) {
            cout << head->data;
            for (Node* curr = head->next; curr != head; curr = curr->next) cout << " -> " << curr->data;
            cout << " -> (back to " << head->data << ")\\n";
        }

        int main() {
            Node* head = new Node(10); head->next = new Node(5); head->next->next = new Node(20);
            head->next->next->next = new Node(15); head->next->next->next->next = head;
            printCircular(head);
            int ks[] = {2, 3, 1}; const char* labels[] = {"2nd", "3rd", "1st"};
            for (int i = 0; i < 3; i++) {
                head = deleteKth(head, ks[i]);
                cout << "delete " << labels[i] << ": "; printCircular(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node next;
                Node(int d) { data = d; }
            }

            static Node deleteHead(Node head) {
                if (head == null || head.next == head) return null;
                head.data = head.next.data; head.next = head.next.next;
                return head;
            }

            static Node deleteKth(Node head, int k) {
                if (head == null) return null;
                if (k == 1) return deleteHead(head);
                Node curr = head;
                for (int i = 0; i < k - 2; i++) curr = curr.next;   // k-2 steps reach the (k-1)-th node
                curr.next = curr.next.next;                         // bypass the k-th node
                return head;
            }

            static void printCircular(Node head) {
                StringBuilder sb = new StringBuilder().append(head.data);
                for (Node curr = head.next; curr != head; curr = curr.next) sb.append(" -> ").append(curr.data);
                System.out.println(sb + " -> (back to " + head.data + ")");
            }

            public static void main(String[] args) {
                Node head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
                head.next.next.next = new Node(15); head.next.next.next.next = head;
                printCircular(head);
                int[] ks = {2, 3, 1}; String[] labels = {"2nd", "3rd", "1st"};
                for (int i = 0; i < 3; i++) {
                    head = deleteKth(head, ks[i]);
                    System.out.print("delete " + labels[i] + ": "); printCircular(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.next = null; }
        }

        function deleteHead(head) {
            if (head === null || head.next === head) return null;
            head.data = head.next.data; head.next = head.next.next;
            return head;
        }

        function deleteKth(head, k) {
            if (head === null) return null;
            if (k === 1) return deleteHead(head);
            let curr = head;
            for (let i = 0; i < k - 2; i++) curr = curr.next;   // k-2 steps reach the (k-1)-th node
            curr.next = curr.next.next;                         // bypass the k-th node
            return head;
        }

        function printCircular(head) {
            const parts = [head.data];
            for (let curr = head.next; curr !== head; curr = curr.next) parts.push(curr.data);
            console.log(parts.join(" -> "), `-> (back to ${head.data})`);
        }

        let head = new Node(10); head.next = new Node(5); head.next.next = new Node(20);
        head.next.next.next = new Node(15); head.next.next.next.next = head;
        printCircular(head);
        for (const [k, label] of [[2, "2nd"], [3, "3rd"], [1, "1st"]]) {
            head = deleteKth(head, k);
            process.stdout.write(`delete ${label}: `); printCircular(head);
        }
    ''')
    yield complexity("O(k)", "O(1)")
    yield pitfall("The original notes looped `for i in range(1, k-2)`, which takes `k - 3` steps and deletes the wrong node for every `k > 2`. Count the steps on paper: from node 1, reaching node `k-1` is exactly `k - 2` hops. The code also assumes `k ≤ length`; add a length check (or stop when `curr.next == head`) for untrusted input.")

    yield section("Interview Q&A", "message-question")
    yield qa("How do you detect that a linked list is circular?",
             "Traverse with a `fast` pointer moving two steps and a `slow` pointer moving one (Floyd's cycle detection). In a circular list they eventually meet; in a normal list `fast` reaches `None`. O(n) time, O(1) space — a visited-set would also work but costs O(n) memory.")
    yield qa("Why keep a tail pointer rather than a head pointer in a circular list?",
             "Because `tail.next` *is* the head. With the tail you can insert at the front (`new.next = tail.next; tail.next = new`), insert at the back (same, then `tail = new`) and delete the front, all in O(1), without the value-swapping trick. Queues built on circular lists do exactly this.")
    yield qa("Where are circular linked lists used in practice?",
             "Round-robin CPU scheduling, turn order in games, circular buffers for streaming data, Fibonacci heaps (the root list is circular doubly linked), and the Josephus problem — every k-th person around a circle is eliminated until one remains.")
    yield qa("What goes wrong if you forget the single-node case?",
             "A one-node circular list has `head.next == head`. A `delete_head` that does `head.next = head.next.next` would leave the node pointing at itself and return it — the list never becomes empty. Always test the empty, one-node and two-node lists.")


@topic(G, "doubly_linked", "Doubly Linked List", "arrows-left-right")
def _():
    yield lead("A doubly linked list gives every node a **`prev`** pointer in addition to `next`, so the list can be walked in both directions and any node can be removed in O(1) given only a reference to it. It costs one extra pointer per node and a little more bookkeeping.")
    yield define("Doubly linked list", "a linked list whose nodes hold `data`, `next` (the following node) and `prev` (the preceding node). The head's `prev` and the tail's `next` are `None`. Every link is mirrored: `a.next == b` always implies `b.prev == a`.")
    yield diagram('''
                 head                                                   tail
                  ↓                                                       ↓
             ┌────┬──────┬────┐     ┌────┬──────┬────┐     ┌────┬──────┬────┐
        ∅ ◀──┼ ●  │  10  │ ●──┼────▶│ ●  │  20  │ ●──┼────▶│ ●  │  30  │ ●──┼──▶ ∅
             └────┴──────┴────┘◀────┼─●  │      │    │◀────┼─●  │      │    │
              prev  data  next      └────┴──────┴────┘     └────┴──────┴────┘

        None <-> 10 <-> 20 <-> 30 <-> None
    ''', "A doubly linked list: every node knows both its neighbours")

    yield section("Structure of a node and traversal in both directions", "box")
    yield p("Linking two nodes now means setting **two** pointers: `a.next = b` *and* `b.prev = a`. Forgetting one of them is the classic doubly-linked bug — the list looks fine going forward and breaks going backward. Traversal backwards starts from the last node and follows `prev`.")
    yield multi('''
        forward: 10 <-> 20 <-> 30
        backward: 30 <-> 20 <-> 10
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def show(head):
            parts, curr, last = [], head, None
            while curr is not None:
                parts.append(str(curr.data))
                last = curr                          # remember the tail for the way back
                curr = curr.next
            print("forward:", " <-> ".join(parts))
            parts, curr = [], last
            while curr is not None:                  # walk back along prev
                parts.append(str(curr.data))
                curr = curr.prev
            print("backward:", " <-> ".join(parts))

        head = Node(10); temp1 = Node(20); temp2 = Node(30)
        head.next = temp1;  temp1.prev = head        # every link is set in both directions
        temp1.next = temp2; temp2.prev = temp1
        show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        void show(Node* head) {
            Node* last = nullptr;
            cout << "forward:";
            for (Node* curr = head; curr; curr = curr->next) {
                cout << (curr == head ? " " : " <-> ") << curr->data;
                last = curr;                             // remember the tail for the way back
            }
            cout << "\\nbackward:";
            for (Node* curr = last; curr; curr = curr->prev)   // walk back along prev
                cout << (curr == last ? " " : " <-> ") << curr->data;
            cout << "\\n";
        }

        int main() {
            Node* head = new Node(10); Node* temp1 = new Node(20); Node* temp2 = new Node(30);
            head->next = temp1;  temp1->prev = head;     // every link is set in both directions
            temp1->next = temp2; temp2->prev = temp1;
            show(head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static void show(Node head) {
                StringBuilder sb = new StringBuilder("forward:");
                Node last = null;
                for (Node curr = head; curr != null; curr = curr.next) {
                    sb.append(curr == head ? " " : " <-> ").append(curr.data);
                    last = curr;                             // remember the tail for the way back
                }
                System.out.println(sb);
                sb = new StringBuilder("backward:");
                for (Node curr = last; curr != null; curr = curr.prev)   // walk back along prev
                    sb.append(curr == last ? " " : " <-> ").append(curr.data);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), temp1 = new Node(20), temp2 = new Node(30);
                head.next = temp1;  temp1.prev = head;       // every link is set in both directions
                temp1.next = temp2; temp2.prev = temp1;
                show(head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function show(head) {
            const parts = [];
            let last = null;
            for (let curr = head; curr !== null; curr = curr.next) {
                parts.push(curr.data);
                last = curr;                                 // remember the tail for the way back
            }
            console.log("forward:", parts.join(" <-> "));
            const back = [];
            for (let curr = last; curr !== null; curr = curr.prev)   // walk back along prev
                back.push(curr.data);
            console.log("backward:", back.join(" <-> "));
        }

        const head = new Node(10), temp1 = new Node(20), temp2 = new Node(30);
        head.next = temp1;  temp1.prev = head;               // every link is set in both directions
        temp1.next = temp2; temp2.prev = temp1;
        show(head);
    ''')
    yield complexity("O(n) traversal", "O(n) for n nodes")

    yield section("Advantages and disadvantages", "scale")
    yield cards(
        ("Traversal in both directions", "Walk forward with `next`, backward with `prev` — browsers' back/forward history, text editor cursors, undo/redo.", "arrows-left-right"),
        ("Delete a node in O(1) given its reference", "`node.prev.next = node.next; node.next.prev = node.prev`. A singly linked list would first need an O(n) walk to find the predecessor.", "bolt"),
        ("Insert / delete before a given node", "The predecessor is one pointer away, so inserting *before* is as cheap as inserting after.", "arrow-bar-to-left"),
        ("O(1) at both ends with a tail", "Keeping `tail` makes insert and delete at **both** ends O(1) — the basis of `deque` and the LRU cache.", "arrows-horizontal"),
        ("Extra space", "A second pointer per node: 16 bytes of links per element on a 64-bit machine.", "database"),
        ("More complex code", "Every operation updates up to four pointers and must keep `prev`/`next` consistent; more special cases for the head and tail.", "alert-triangle"),
        cols=3,
    )
    yield table(
        ["Operation", "Singly linked", "Doubly linked", "Why the difference"],
        ["Insert at beginning", "O(1)", "O(1)", "Both just re-point the head; doubly also sets the old head's `prev`."],
        ["Insert at end", "O(n) / O(1) with tail", "O(n) / O(1) with tail", "Same walk unless a tail is kept."],
        ["Delete head", "O(1)", "O(1)", "Doubly also clears the new head's `prev`."],
        ["Delete last", "O(n) even with tail", "**O(1) with tail**", "The tail's `prev` gives the new last node for free."],
        ["Delete a given node", "O(n)", "**O(1)**", "The predecessor is `node.prev`; singly must search for it."],
        ["Insert before a given node", "O(n)", "**O(1)**", "Same reason."],
        ["Reverse", "O(n)", "O(n)", "Doubly: swap `prev` and `next` in every node."],
    )

    yield section("Insert at the beginning", "arrow-bar-to-left")
    yield io("list = 10 <-> 20 <-> 30, insert 5 at the beginning", "5 <-> 10 <-> 20 <-> 30")
    yield idea("Point the new node's `next` at the old head, point the old head's `prev` back at the new node, and return the new node as head. Two pointer writes — O(1). The empty list needs a guard: there is no old head whose `prev` could be set (the original notes crashed on this case).")
    yield multi('''
        10 <-> 20 <-> 30
        5 <-> 10 <-> 20 <-> 30
        1 <-> 5 <-> 10 <-> 20 <-> 30
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def insert_at_beginning(head, data):
            temp = Node(data)
            temp.next = head                 # new → old head
            if head is not None:
                head.prev = temp             # old head → new (guard the empty list)
            return temp

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data)); head = head.next
            print(" <-> ".join(parts))

        head = Node(10); t1 = Node(20); t2 = Node(30)
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1
        show(head)
        head = insert_at_beginning(head, 5); show(head)
        head = insert_at_beginning(head, 1); show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        Node* insertAtBeginning(Node* head, int data) {
            Node* temp = new Node(data);
            temp->next = head;               // new → old head
            if (head) head->prev = temp;     // old head → new (guard the empty list)
            return temp;
        }

        void show(Node* head) {
            for (; head; head = head->next) cout << head->data << (head->next ? " <-> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); Node* t1 = new Node(20); Node* t2 = new Node(30);
            head->next = t1; t1->prev = head; t1->next = t2; t2->prev = t1;
            show(head);
            head = insertAtBeginning(head, 5); show(head);
            head = insertAtBeginning(head, 1); show(head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static Node insertAtBeginning(Node head, int data) {
                Node temp = new Node(data);
                temp.next = head;                    // new → old head
                if (head != null) head.prev = temp;  // old head → new (guard the empty list)
                return temp;
            }

            static void show(Node head) {
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " <-> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), t1 = new Node(20), t2 = new Node(30);
                head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
                show(head);
                head = insertAtBeginning(head, 5); show(head);
                head = insertAtBeginning(head, 1); show(head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function insertAtBeginning(head, data) {
            const temp = new Node(data);
            temp.next = head;                        // new → old head
            if (head !== null) head.prev = temp;     // old head → new (guard the empty list)
            return temp;
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.join(" <-> "));
        }

        let head = new Node(10), t1 = new Node(20), t2 = new Node(30);
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
        show(head);
        head = insertAtBeginning(head, 5); show(head);
        head = insertAtBeginning(head, 1); show(head);
    ''')
    yield complexity("O(1)", "O(1)")

    yield section("Insert at the end", "arrow-bar-to-right")
    yield io("list = 10 <-> 20 <-> 30, insert 40 at the end", "10 <-> 20 <-> 30 <-> 40", "list = empty, insert 40", "40")
    yield idea("Walk to the last node, link it forward to the new node and link the new node back with `prev`. O(n) because of the walk; a class that stores `tail` does the same two writes in O(1).")
    yield multi('''
        10 <-> 20 <-> 30 <-> 40
        40
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def insert_end(head, x):
            temp = Node(x)
            if head is None:
                return temp                      # empty list: new node is the head
            curr = head
            while curr.next is not None:         # O(n) walk to the last node
                curr = curr.next
            curr.next = temp                     # last → new
            temp.prev = curr                     # new → last
            return head

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data)); head = head.next
            print(" <-> ".join(parts))

        head = Node(10); t1 = Node(20); t2 = Node(30)
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1
        head = insert_end(head, 40); show(head)
        empty = insert_end(None, 40); show(empty)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        Node* insertEnd(Node* head, int x) {
            Node* temp = new Node(x);
            if (!head) return temp;                  // empty list: new node is the head
            Node* curr = head;
            while (curr->next) curr = curr->next;    // O(n) walk to the last node
            curr->next = temp;                       // last → new
            temp->prev = curr;                       // new → last
            return head;
        }

        void show(Node* head) {
            for (; head; head = head->next) cout << head->data << (head->next ? " <-> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); Node* t1 = new Node(20); Node* t2 = new Node(30);
            head->next = t1; t1->prev = head; t1->next = t2; t2->prev = t1;
            head = insertEnd(head, 40); show(head);
            Node* empty = insertEnd(nullptr, 40); show(empty);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static Node insertEnd(Node head, int x) {
                Node temp = new Node(x);
                if (head == null) return temp;               // empty list: new node is the head
                Node curr = head;
                while (curr.next != null) curr = curr.next;  // O(n) walk to the last node
                curr.next = temp;                            // last → new
                temp.prev = curr;                            // new → last
                return head;
            }

            static void show(Node head) {
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " <-> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), t1 = new Node(20), t2 = new Node(30);
                head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
                head = insertEnd(head, 40); show(head);
                Node empty = insertEnd(null, 40); show(empty);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function insertEnd(head, x) {
            const temp = new Node(x);
            if (head === null) return temp;                  // empty list: new node is the head
            let curr = head;
            while (curr.next !== null) curr = curr.next;     // O(n) walk to the last node
            curr.next = temp;                                // last → new
            temp.prev = curr;                                // new → last
            return head;
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.join(" <-> "));
        }

        let head = new Node(10), t1 = new Node(20), t2 = new Node(30);
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
        head = insertEnd(head, 40); show(head);
        const empty = insertEnd(null, 40); show(empty);
    ''')
    yield complexity("O(n) — O(1) with a tail pointer", "O(1)")

    yield section("Delete the head", "arrow-bar-left")
    yield io("list = 10 <-> 20 <-> 30", "20 <-> 30", "list = 10", "empty")
    yield idea("Move the head to the second node and clear its `prev` — without that step the new head would still point back at a node that is no longer in the list. A one-node list becomes empty.")
    yield multi('''
        after delete head: 20 <-> 30
        after delete head: 30
        after delete head: empty
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def delete_head(head):
            if head is None or head.next is None:
                return None                      # 0 or 1 node → empty
            head = head.next
            head.prev = None                     # the new head has no predecessor
            return head

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data)); head = head.next
            print(" <-> ".join(parts) if parts else "empty")

        head = Node(10); t1 = Node(20); t2 = Node(30)
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1
        for _ in range(3):
            head = delete_head(head)
            print("after delete head: ", end=""); show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        Node* deleteHead(Node* head) {
            if (!head) return nullptr;
            if (!head->next) { delete head; return nullptr; }   // 1 node → empty
            Node* newHead = head->next;
            newHead->prev = nullptr;                 // the new head has no predecessor
            delete head;
            return newHead;
        }

        void show(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            for (; head; head = head->next) cout << head->data << (head->next ? " <-> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); Node* t1 = new Node(20); Node* t2 = new Node(30);
            head->next = t1; t1->prev = head; t1->next = t2; t2->prev = t1;
            for (int i = 0; i < 3; i++) {
                head = deleteHead(head);
                cout << "after delete head: "; show(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static Node deleteHead(Node head) {
                if (head == null || head.next == null) return null;   // 0 or 1 node → empty
                head = head.next;
                head.prev = null;                        // the new head has no predecessor
                return head;
            }

            static void show(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " <-> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), t1 = new Node(20), t2 = new Node(30);
                head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
                for (int i = 0; i < 3; i++) {
                    head = deleteHead(head);
                    System.out.print("after delete head: "); show(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function deleteHead(head) {
            if (head === null || head.next === null) return null;    // 0 or 1 node → empty
            head = head.next;
            head.prev = null;                            // the new head has no predecessor
            return head;
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.length ? parts.join(" <-> ") : "empty");
        }

        let head = new Node(10), t1 = new Node(20), t2 = new Node(30);
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
        for (let i = 0; i < 3; i++) {
            head = deleteHead(head);
            process.stdout.write("after delete head: "); show(head);
        }
    ''')
    yield complexity("O(1)", "O(1)")

    yield section("Delete the last node", "arrow-bar-right")
    yield io("list = 10 <-> 20 <-> 30", "10 <-> 20", "list = 10", "empty")
    yield idea("Walk to the last node and cut it off via `last.prev.next = None`. Thanks to `prev` the predecessor is one hop away; the only O(n) part is reaching the last node, which disappears when a `tail` pointer is kept — the operation a singly linked list cannot do in O(1) even with a tail.")
    yield multi('''
        after delete last: 10 <-> 20
        after delete last: 10
        after delete last: empty
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def delete_last(head):
            if head is None or head.next is None:
                return None                      # 0 or 1 node → empty
            curr = head
            while curr.next is not None:         # walk to the last node (O(1) with a tail pointer)
                curr = curr.next
            curr.prev.next = None                # predecessor is one hop away via prev
            return head

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data)); head = head.next
            print(" <-> ".join(parts) if parts else "empty")

        head = Node(10); t1 = Node(20); t2 = Node(30)
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1
        for _ in range(3):
            head = delete_last(head)
            print("after delete last: ", end=""); show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        Node* deleteLast(Node* head) {
            if (!head) return nullptr;
            if (!head->next) { delete head; return nullptr; }   // 1 node → empty
            Node* curr = head;
            while (curr->next) curr = curr->next;    // walk to the last node (O(1) with a tail pointer)
            curr->prev->next = nullptr;              // predecessor is one hop away via prev
            delete curr;
            return head;
        }

        void show(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            for (; head; head = head->next) cout << head->data << (head->next ? " <-> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); Node* t1 = new Node(20); Node* t2 = new Node(30);
            head->next = t1; t1->prev = head; t1->next = t2; t2->prev = t1;
            for (int i = 0; i < 3; i++) {
                head = deleteLast(head);
                cout << "after delete last: "; show(head);
            }
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static Node deleteLast(Node head) {
                if (head == null || head.next == null) return null;   // 0 or 1 node → empty
                Node curr = head;
                while (curr.next != null) curr = curr.next;   // walk to the last node (O(1) with a tail pointer)
                curr.prev.next = null;                        // predecessor is one hop away via prev
                return head;
            }

            static void show(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " <-> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), t1 = new Node(20), t2 = new Node(30);
                head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
                for (int i = 0; i < 3; i++) {
                    head = deleteLast(head);
                    System.out.print("after delete last: "); show(head);
                }
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function deleteLast(head) {
            if (head === null || head.next === null) return null;    // 0 or 1 node → empty
            let curr = head;
            while (curr.next !== null) curr = curr.next;     // walk to the last node (O(1) with a tail pointer)
            curr.prev.next = null;                           // predecessor is one hop away via prev
            return head;
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.length ? parts.join(" <-> ") : "empty");
        }

        let head = new Node(10), t1 = new Node(20), t2 = new Node(30);
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
        for (let i = 0; i < 3; i++) {
            head = deleteLast(head);
            process.stdout.write("after delete last: "); show(head);
        }
    ''')
    yield complexity("O(n) — O(1) with a tail pointer", "O(1)")

    yield section("Delete a node given its reference", "bolt")
    yield io("list = 10 <-> 20 <-> 30, node = the node holding 20", "10 <-> 30")
    yield idea("This is the operation that justifies the extra pointer. With `node.prev` and `node.next` both known, unlink in O(1): the predecessor's `next` skips to the successor and the successor's `prev` skips back to the predecessor. Guard the ends: if `node` is the head there is no predecessor (the head moves), if it is the tail there is no successor.")
    yield diagram('''
        before:   [10] ◀──▶ [20] ◀──▶ [30]
                            node

        node.prev.next = node.next     [10] ───────▶ [30]       (10's next skips 20)
        node.next.prev = node.prev     [10] ◀─────── [30]       (30's prev skips 20)

        after:    [10] ◀──▶ [30]
    ''', "Deleting a node in O(1): two pointer writes on its neighbours")
    yield multi('''
        10 <-> 20 <-> 30
        delete node 20: 10 <-> 30
        delete node 10 (head): 30
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def delete_node(head, node):
            if node.prev is not None:
                node.prev.next = node.next       # predecessor skips over node
            else:
                head = node.next                 # node was the head
            if node.next is not None:
                node.next.prev = node.prev       # successor skips back over node
            return head

        def show(head):
            parts = []
            while head:
                parts.append(str(head.data)); head = head.next
            print(" <-> ".join(parts) if parts else "empty")

        head = Node(10); t1 = Node(20); t2 = Node(30)
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1
        show(head)
        head = delete_node(head, t1); print("delete node 20: ", end=""); show(head)
        head = delete_node(head, head); print("delete node 10 (head): ", end=""); show(head)
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        Node* deleteNode(Node* head, Node* node) {
            if (node->prev) node->prev->next = node->next;   // predecessor skips over node
            else head = node->next;                          // node was the head
            if (node->next) node->next->prev = node->prev;   // successor skips back over node
            delete node;
            return head;
        }

        void show(Node* head) {
            if (!head) { cout << "empty\\n"; return; }
            for (; head; head = head->next) cout << head->data << (head->next ? " <-> " : "\\n");
        }

        int main() {
            Node* head = new Node(10); Node* t1 = new Node(20); Node* t2 = new Node(30);
            head->next = t1; t1->prev = head; t1->next = t2; t2->prev = t1;
            show(head);
            head = deleteNode(head, t1); cout << "delete node 20: "; show(head);
            head = deleteNode(head, head); cout << "delete node 10 (head): "; show(head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static Node deleteNode(Node head, Node node) {
                if (node.prev != null) node.prev.next = node.next;   // predecessor skips over node
                else head = node.next;                               // node was the head
                if (node.next != null) node.next.prev = node.prev;   // successor skips back over node
                return head;
            }

            static void show(Node head) {
                if (head == null) { System.out.println("empty"); return; }
                StringBuilder sb = new StringBuilder();
                for (; head != null; head = head.next) sb.append(head.data).append(head.next != null ? " <-> " : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), t1 = new Node(20), t2 = new Node(30);
                head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
                show(head);
                head = deleteNode(head, t1); System.out.print("delete node 20: "); show(head);
                head = deleteNode(head, head); System.out.print("delete node 10 (head): "); show(head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function deleteNode(head, node) {
            if (node.prev !== null) node.prev.next = node.next;   // predecessor skips over node
            else head = node.next;                                // node was the head
            if (node.next !== null) node.next.prev = node.prev;   // successor skips back over node
            return head;
        }

        function show(head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(parts.length ? parts.join(" <-> ") : "empty");
        }

        let head = new Node(10), t1 = new Node(20), t2 = new Node(30);
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
        show(head);
        head = deleteNode(head, t1); process.stdout.write("delete node 20: "); show(head);
        head = deleteNode(head, head); process.stdout.write("delete node 10 (head): "); show(head);
    ''')
    yield complexity("O(1)", "O(1)")
    yield note("This is exactly how an **LRU cache** evicts and promotes entries: a hash map gives the node for a key in O(1), and the doubly linked list moves that node to the front in O(1). Neither structure alone can do both.")

    yield section("Reverse a doubly linked list", "arrows-exchange")
    yield io("list = 10 <-> 20 <-> 30", "30 <-> 20 <-> 10")
    yield idea("Reversing means every node's `next` becomes its `prev` and vice versa — so **swap the two pointers in each node**. After the swap, the *old* `next` is reachable as `curr.prev`, which is how the loop advances. The last node visited is the new head.")
    yield steps(
        ("Walk the list", "`curr = head`, remembering the node just processed in `prev`."),
        ("Swap in place", "`curr.next, curr.prev = curr.prev, curr.next`."),
        ("Advance", "`curr = curr.prev` — that field now holds the old `next`."),
        ("Finish", "When `curr` is `None`, `prev` is the last node processed: the new head."),
    )
    yield multi('''
        forward: 10 <-> 20 <-> 30
        reversed: 30 <-> 20 <-> 10
        back again: 10 <-> 20 <-> 30
    ''', py='''
        class Node:
            def __init__(self, data):
                self.data = data
                self.prev = None
                self.next = None

        def reverse_dll(head):
            prev, curr = None, head
            while curr is not None:
                prev = curr
                curr.next, curr.prev = curr.prev, curr.next   # swap the two links
                curr = curr.prev                              # old next now lives in prev
            return prev                                       # last node processed = new head

        def show(label, head):
            parts = []
            while head:
                parts.append(str(head.data)); head = head.next
            print(label + ":", " <-> ".join(parts))

        head = Node(10); t1 = Node(20); t2 = Node(30)
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1
        show("forward", head)
        head = reverse_dll(head); show("reversed", head)
        head = reverse_dll(head); show("back again", head)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        using namespace std;

        struct Node {
            int data; Node* prev; Node* next;
            Node(int d) : data(d), prev(nullptr), next(nullptr) {}
        };

        Node* reverseDLL(Node* head) {
            Node* prev = nullptr;
            for (Node* curr = head; curr; curr = curr->prev) {   // after the swap, prev holds the old next
                prev = curr;
                swap(curr->next, curr->prev);                      // swap the two links
            }
            return prev;                                           // last node processed = new head
        }

        void show(const char* label, Node* head) {
            cout << label << ":";
            for (; head; head = head->next) cout << " " << head->data << (head->next ? " <->" : "");
            cout << "\\n";
        }

        int main() {
            Node* head = new Node(10); Node* t1 = new Node(20); Node* t2 = new Node(30);
            head->next = t1; t1->prev = head; t1->next = t2; t2->prev = t1;
            show("forward", head);
            head = reverseDLL(head); show("reversed", head);
            head = reverseDLL(head); show("back again", head);
        }
    ''', java='''
        public class Main {
            static class Node {
                int data; Node prev, next;
                Node(int d) { data = d; }
            }

            static Node reverseDLL(Node head) {
                Node prev = null;
                for (Node curr = head; curr != null; curr = curr.prev) {   // after the swap, prev holds the old next
                    prev = curr;
                    Node t = curr.next; curr.next = curr.prev; curr.prev = t;   // swap the two links
                }
                return prev;                                               // last node processed = new head
            }

            static void show(String label, Node head) {
                StringBuilder sb = new StringBuilder(label + ":");
                for (; head != null; head = head.next) sb.append(" ").append(head.data).append(head.next != null ? " <->" : "");
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node head = new Node(10), t1 = new Node(20), t2 = new Node(30);
                head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
                show("forward", head);
                head = reverseDLL(head); show("reversed", head);
                head = reverseDLL(head); show("back again", head);
            }
        }
    ''', js='''
        class Node {
            constructor(data) { this.data = data; this.prev = null; this.next = null; }
        }

        function reverseDLL(head) {
            let prev = null;
            for (let curr = head; curr !== null; curr = curr.prev) {   // after the swap, prev holds the old next
                prev = curr;
                [curr.next, curr.prev] = [curr.prev, curr.next];        // swap the two links
            }
            return prev;                                                // last node processed = new head
        }

        function show(label, head) {
            const parts = [];
            for (; head !== null; head = head.next) parts.push(head.data);
            console.log(label + ":", parts.join(" <-> "));
        }

        let head = new Node(10), t1 = new Node(20), t2 = new Node(30);
        head.next = t1; t1.prev = head; t1.next = t2; t2.prev = t1;
        show("forward", head);
        head = reverseDLL(head); show("reversed", head);
        head = reverseDLL(head); show("back again", head);
    ''')
    yield complexity("O(n)", "O(1)")
    yield pitfall("Advancing with `curr = curr.next` *after* the swap walks backwards into the part already reversed and loops forever (or stops after one node). The old `next` is in `curr.prev` once the swap has happened.")

    yield section("Interview Q&A", "message-question")
    yield qa("What does the extra `prev` pointer buy you?",
             "O(1) deletion of a node you hold a reference to, O(1) insertion *before* a node, O(1) removal from the tail (with a tail pointer) and backward traversal. The price is one more pointer per node and twice as many links to keep consistent.")
    yield qa("How does an LRU cache use a doubly linked list?",
             "Entries are nodes ordered from most to least recently used; a hash map points from each key to its node. On access, the node is unlinked in O(1) (possible only because of `prev`) and re-inserted at the front. On eviction the tail node is removed in O(1). All operations are O(1).")
    yield qa("Singly vs doubly linked list — how do you choose?",
             "Singly when you only move forward and operate at the head (stacks, hash chains, adjacency lists) — it is smaller and simpler. Doubly when you need deletions in the middle by reference, both-end operations (deques) or backward iteration. Java's `LinkedList` and C++ `std::list` are doubly linked; `std::forward_list` is singly linked.")
    yield qa("How would you reverse a doubly linked list?",
             "Swap `next` and `prev` in every node and return the last node visited. One pass, no extra memory. Because the old `next` ends up in `prev`, the loop advances with `curr = curr.prev`.")
    yield qa("What is an XOR linked list?",
             "A memory-saving trick: each node stores `prev XOR next` in a single field. Walking forward from a known predecessor, `next = stored XOR prev`. It halves the pointer overhead but defeats garbage collectors and makes the code fragile — an interview curiosity rather than a production structure.")
