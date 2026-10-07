from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Trees & Heaps"


@topic(G, "bst", "Binary Search Tree", "hierarchy")
def _():
    yield lead("A binary search tree keeps its keys **ordered**: everything in a node's left subtree is smaller, everything in its right subtree is larger. That one invariant is what every problem here exploits — the inorder traversal is sorted, every search is a single root-to-leaf walk, and a count stored in each node turns *order statistics* into `O(h)` queries.")
    yield define("Binary Search Tree (BST)", "a binary tree in which, for **every** node, all keys in the left subtree are `<` the node's key and all keys in the right subtree are `>` it. The rule applies to whole subtrees, not just to the two children — this is the detail most wrong solutions miss.")
    yield diagram('''
                    20
                  /    \\
                 8      22
               /   \\
              4     12
                   /  \\
                 10    14

        inorder:  4  8  10  12  14  20  22      (always sorted)
    ''', "Tree A — the sample tree used throughout this topic")

    yield section("What the problems rely on", "bulb")
    yield p("The reader already knows search, insert and delete. The advanced problems are built from four consequences of the BST invariant:")
    yield cards(
        ("Inorder is sorted", "Left, node, right visits keys in ascending order. Anything you can do on a sorted array (two pointers, previous-element checks, kth element) you can do on a BST without materialising the array.", "list-numbers"),
        ("One path answers a query", "Search, floor, ceiling, predecessor and successor each follow a single root-to-leaf path: `O(h)` time, where `h` is the height.", "route"),
        ("Ancestors bound a node", "A node must lie strictly inside the range `(lower, upper)` set by all of its ancestors — not only by its parent.", "arrows-vertical"),
        ("Nodes can carry extra data", "Storing the size of the left subtree (an *augmented* BST) makes “kth smallest” and “rank of x” `O(h)` queries.", "database"),
        cols=2,
    )
    yield table(
        ["Operation", "Time", "Note"],
        ["search / insert / delete", "O(h)", "`h = O(log n)` when balanced, `O(n)` when skewed"],
        ["floor / ceiling / successor", "O(h)", "one path down, remember the best candidate"],
        ["kth smallest (plain)", "O(h + k)", "inorder traversal stopped after `k` nodes"],
        ["kth smallest (augmented)", "O(h)", "each node stores the size of its left subtree"],
        ["check if a tree is a BST", "O(n)", "range method or inorder-previous method"],
        ["inorder traversal", "O(n)", "stack holds at most `h` nodes"],
    )
    yield note("The library ordered containers — C++ `std::set` / `std::map`, Java `TreeSet` / `TreeMap` — are self-balancing BSTs (red-black trees), so `h = O(log n)` is guaranteed. Python and JavaScript ship no ordered set; you either write a small BST, keep a sorted list with `bisect` (`O(n)` inserts) or use a third-party package.")

    yield section("Floor and ceiling of a key", "arrows-vertical")
    yield io("tree A, x = 11", "floor 10, ceiling 12", "tree A, x = 23", "floor 22, ceiling -1 (none)", "tree A, x = 3", "floor -1 (none), ceiling 4")
    yield idea("Walk down from the root. For the **floor** (largest key `<= x`): when the current key is too big go left; when it is `<= x` it is a candidate — record it and go right to look for a closer one. The **ceiling** is the mirror image. The answer is the last candidate recorded on the path — no backtracking, no recursion.")
    yield multi('''
        x=11: floor 10 ceiling 12
        x=23: floor 22 ceiling -1
        x=3: floor -1 ceiling 4
        x=12: floor 12 ceiling 12
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def insert(root, key):
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
            elif key > root.key:
                root.right = insert(root.right, key)
            return root

        def floor_of(root, x):
            res = -1
            while root:
                if root.key == x:
                    return x
                if root.key > x:
                    root = root.left        # too big: only the left subtree can hold a floor
                else:
                    res = root.key          # candidate; a closer one may sit to the right
                    root = root.right
            return res

        def ceil_of(root, x):
            res = -1
            while root:
                if root.key == x:
                    return x
                if root.key < x:
                    root = root.right       # too small: only the right subtree can hold a ceiling
                else:
                    res = root.key          # candidate; a closer one may sit to the left
                    root = root.left
            return res

        root = None
        for k in [20, 8, 22, 4, 12, 10, 14]:
            root = insert(root, k)
        for x in [11, 23, 3, 12]:
            print(f"x={x}: floor {floor_of(root, x)} ceiling {ceil_of(root, x)}")
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        Node* insert(Node* root, int key) {
            if (!root) return new Node(key);
            if (key < root->key) root->left = insert(root->left, key);
            else if (key > root->key) root->right = insert(root->right, key);
            return root;
        }

        int floorOf(Node* root, int x) {
            int res = -1;
            while (root) {
                if (root->key == x) return x;
                if (root->key > x) root = root->left;          // too big: go left
                else { res = root->key; root = root->right; }  // candidate, look right for a closer one
            }
            return res;
        }

        int ceilOf(Node* root, int x) {
            int res = -1;
            while (root) {
                if (root->key == x) return x;
                if (root->key < x) root = root->right;         // too small: go right
                else { res = root->key; root = root->left; }   // candidate, look left for a closer one
            }
            return res;
        }

        int main() {
            Node* root = nullptr;
            for (int k : {20, 8, 22, 4, 12, 10, 14}) root = insert(root, k);
            for (int x : {11, 23, 3, 12})
                cout << "x=" << x << ": floor " << floorOf(root, x) << " ceiling " << ceilOf(root, x) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node insert(Node root, int key) {
                if (root == null) return new Node(key);
                if (key < root.key) root.left = insert(root.left, key);
                else if (key > root.key) root.right = insert(root.right, key);
                return root;
            }

            static int floorOf(Node root, int x) {
                int res = -1;
                while (root != null) {
                    if (root.key == x) return x;
                    if (root.key > x) root = root.left;            // too big: go left
                    else { res = root.key; root = root.right; }    // candidate, look right for a closer one
                }
                return res;
            }

            static int ceilOf(Node root, int x) {
                int res = -1;
                while (root != null) {
                    if (root.key == x) return x;
                    if (root.key < x) root = root.right;           // too small: go right
                    else { res = root.key; root = root.left; }     // candidate, look left for a closer one
                }
                return res;
            }

            public static void main(String[] args) {
                Node root = null;
                for (int k : new int[]{20, 8, 22, 4, 12, 10, 14}) root = insert(root, k);
                for (int x : new int[]{11, 23, 3, 12})
                    System.out.println("x=" + x + ": floor " + floorOf(root, x) + " ceiling " + ceilOf(root, x));
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insert(root, key) {
            if (!root) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            return root;
        }

        function floorOf(root, x) {
            let res = -1;
            while (root) {
                if (root.key === x) return x;
                if (root.key > x) root = root.left;               // too big: go left
                else { res = root.key; root = root.right; }       // candidate, look right for a closer one
            }
            return res;
        }

        function ceilOf(root, x) {
            let res = -1;
            while (root) {
                if (root.key === x) return x;
                if (root.key < x) root = root.right;              // too small: go right
                else { res = root.key; root = root.left; }        // candidate, look left for a closer one
            }
            return res;
        }

        let root = null;
        for (const k of [20, 8, 22, 4, 12, 10, 14]) root = insert(root, k);
        for (const x of [11, 23, 3, 12])
            console.log(`x=${x}: floor ${floorOf(root, x)} ceiling ${ceilOf(root, x)}`);
    ''')
    yield complexity("O(h)", "O(1)")
    yield pitfall("Returning as soon as you see a key `<= x` gives a *valid* floor but not the *greatest* one — `floor(11)` would stop at `8` instead of continuing right to `10`. Always keep walking and overwrite the candidate.")

    yield section("Ceiling on the left side of every element", "arrow-up-right")
    yield io("arr = [2, 8, 30, 15, 25, 12]", "-1 -1 -1 30 30 15", "arr = [30, 20, 10]", "-1 30 20")
    yield p("For every `arr[i]`, print the smallest element among `arr[0..i-1]` that is `>= arr[i]`, or `-1` if there is none. The first element never has one.")
    yield p("The obvious solution rescans the prefix for each element:")
    yield snippet("py", '''
        def left_ceilings_naive(arr):
            res = [-1]
            for i in range(1, len(arr)):
                best = -1
                for j in range(i):                                # scan everything to the left
                    if arr[j] >= arr[i] and (best == -1 or arr[j] < best):
                        best = arr[j]
                res.append(best)
            return res

        print(*left_ceilings_naive([2, 8, 30, 15, 25, 12]))
    ''', out="-1 -1 -1 30 30 15")
    yield complexity("O(n²)", "O(1)")
    yield idea("Keep the elements seen so far in an **ordered set** (a self-balancing BST). The ceiling of `arr[i]` is then one `O(log n)` query — `lower_bound` in C++, `TreeSet.ceiling` in Java — and inserting `arr[i]` afterwards is another. Python uses `bisect` on a sorted list (the query is `O(log n)`, the insert `O(n)` but with a very small constant); JavaScript reuses the hand-written BST from the previous section.")
    yield multi('''
        -1 -1 -1 30 30 15
        -1 30 20
    ''', py='''
        from bisect import bisect_left, insort

        def left_ceilings(arr):
            seen = []                              # kept sorted
            res = []
            for x in arr:
                i = bisect_left(seen, x)           # index of the first element >= x
                res.append(seen[i] if i < len(seen) else -1)
                insort(seen, x)                    # O(n) shift, but a tight memmove
            return res

        for arr in ([2, 8, 30, 15, 25, 12], [30, 20, 10]):
            print(*left_ceilings(arr))
    ''', cpp='''
        #include <iostream>
        #include <set>
        #include <vector>
        using namespace std;

        vector<int> leftCeilings(const vector<int>& arr) {
            set<int> seen;                                   // red-black tree
            vector<int> res;
            for (int x : arr) {
                auto it = seen.lower_bound(x);               // first element >= x, O(log n)
                res.push_back(it == seen.end() ? -1 : *it);
                seen.insert(x);
            }
            return res;
        }

        int main() {
            for (const vector<int>& arr : {vector<int>{2, 8, 30, 15, 25, 12}, vector<int>{30, 20, 10}}) {
                vector<int> res = leftCeilings(arr);
                for (int i = 0; i < (int)res.size(); i++) cout << (i ? " " : "") << res[i];
                cout << "\\n";
            }
        }
    ''', java='''
        import java.util.TreeSet;

        public class Main {
            static String leftCeilings(int[] arr) {
                TreeSet<Integer> seen = new TreeSet<>();      // red-black tree
                StringBuilder sb = new StringBuilder();
                for (int x : arr) {
                    Integer c = seen.ceiling(x);              // smallest element >= x, or null
                    sb.append(c == null ? -1 : c).append(' ');
                    seen.add(x);
                }
                return sb.toString().trim();
            }

            public static void main(String[] args) {
                System.out.println(leftCeilings(new int[]{2, 8, 30, 15, 25, 12}));
                System.out.println(leftCeilings(new int[]{30, 20, 10}));
            }
        }
    ''', js='''
        // JavaScript has no ordered set: reuse the BST insert + ceiling from above
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insert(root, key) {
            if (!root) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            return root;
        }

        function ceilOf(root, x) {
            let res = -1;
            while (root) {
                if (root.key === x) return x;
                if (root.key < x) root = root.right;
                else { res = root.key; root = root.left; }
            }
            return res;
        }

        function leftCeilings(arr) {
            let seen = null;
            const res = [];
            for (const x of arr) {
                res.push(ceilOf(seen, x));              // query the elements to the left
                seen = insert(seen, x);                 // then add the current one
            }
            return res;
        }

        for (const arr of [[2, 8, 30, 15, 25, 12], [30, 20, 10]])
            console.log(leftCeilings(arr).join(" "));
    ''')
    yield complexity("O(n log n)", "O(n)")
    yield note("Query **before** insert: if you insert `arr[i]` first, its own ceiling is itself and every answer becomes `arr[i]`. The same pattern (ordered set of the prefix + one query per element) solves *floor on the left*, *ceiling on the right* (scan from the end) and *count of smaller elements to the left*.")

    yield section("Kth smallest element", "list-numbers")
    yield io("tree A, k = 3", "10", "tree A, k = 7", "22", "tree A, k = 8", "-1 (fewer than 8 nodes)")
    yield idea("Inorder visits keys in ascending order, so the kth node visited **is** the kth smallest. Run an iterative inorder traversal with an explicit stack, count the nodes as they are popped, and stop as soon as the count reaches `k` — no need to finish the traversal.")
    yield multi('''
        k=3: 10
        k=7: 22
        k=8: -1
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def insert(root, key):
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
            elif key > root.key:
                root.right = insert(root.right, key)
            return root

        def kth_smallest(root, k):
            stack, node = [], root
            while stack or node:
                while node:                  # go as far left as possible
                    stack.append(node)
                    node = node.left
                node = stack.pop()           # the next key in sorted order
                k -= 1
                if k == 0:
                    return node.key
                node = node.right
            return -1                        # fewer than k nodes

        root = None
        for x in [20, 8, 22, 4, 12, 10, 14]:
            root = insert(root, x)
        for k in (3, 7, 8):
            print(f"k={k}: {kth_smallest(root, k)}")
    ''', cpp='''
        #include <iostream>
        #include <stack>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        Node* insert(Node* root, int key) {
            if (!root) return new Node(key);
            if (key < root->key) root->left = insert(root->left, key);
            else if (key > root->key) root->right = insert(root->right, key);
            return root;
        }

        int kthSmallest(Node* root, int k) {
            stack<Node*> st;
            Node* node = root;
            while (!st.empty() || node) {
                while (node) { st.push(node); node = node->left; }   // go as far left as possible
                node = st.top(); st.pop();                           // next key in sorted order
                if (--k == 0) return node->key;
                node = node->right;
            }
            return -1;                                               // fewer than k nodes
        }

        int main() {
            Node* root = nullptr;
            for (int x : {20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
            for (int k : {3, 7, 8}) cout << "k=" << k << ": " << kthSmallest(root, k) << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node insert(Node root, int key) {
                if (root == null) return new Node(key);
                if (key < root.key) root.left = insert(root.left, key);
                else if (key > root.key) root.right = insert(root.right, key);
                return root;
            }

            static int kthSmallest(Node root, int k) {
                Deque<Node> stack = new ArrayDeque<>();
                Node node = root;
                while (!stack.isEmpty() || node != null) {
                    while (node != null) { stack.push(node); node = node.left; }   // go as far left as possible
                    node = stack.pop();                                             // next key in sorted order
                    if (--k == 0) return node.key;
                    node = node.right;
                }
                return -1;                                                          // fewer than k nodes
            }

            public static void main(String[] args) {
                Node root = null;
                for (int x : new int[]{20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
                for (int k : new int[]{3, 7, 8}) System.out.println("k=" + k + ": " + kthSmallest(root, k));
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insert(root, key) {
            if (!root) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            return root;
        }

        function kthSmallest(root, k) {
            const stack = [];
            let node = root;
            while (stack.length || node) {
                while (node) { stack.push(node); node = node.left; }   // go as far left as possible
                node = stack.pop();                                     // next key in sorted order
                if (--k === 0) return node.key;
                node = node.right;
            }
            return -1;                                                  // fewer than k nodes
        }

        let root = null;
        for (const x of [20, 8, 22, 4, 12, 10, 14]) root = insert(root, x);
        for (const k of [3, 7, 8]) console.log(`k=${k}: ${kthSmallest(root, k)}`);
    ''')
    yield complexity("O(h + k)", "O(h)")
    yield pitfall("The original notes used a recursive traversal with a **global counter** and a `return` after printing — but the `return` only leaves the current frame, the parent frames continue into their right subtrees, and the counter is never reset for a second query. An explicit stack (or a counter object passed down and a boolean *found* flag) avoids both bugs.")

    yield p("When the tree is queried many times, or `k` is large, pay a little memory to make every query `O(h)`: store in each node the **number of nodes in its left subtree** (`lcount`). Insert maintains it — every time the new key goes left, the node it passes gains one left descendant.")
    yield diagram('''
                    20 (lcount 5)
                  /    \\
         (lcount 1) 8    22 (0)
               /   \\
          (0) 4     12 (lcount 1)
                   /  \\
             (0) 10    14 (0)

        kth(k=3) at 20: lcount+1 = 6 > 3   → go left, k stays 3
                  at 8: lcount+1 = 2 < 3   → go right, k = 3-2 = 1
                 at 12: lcount+1 = 2 > 1   → go left
                 at 10: lcount+1 = 1 == 1  → answer 10
    ''', "Augmented tree A: each node knows the size of its left subtree")
    yield multi('''
        k=3: 10
        k=7: 22
        k=8: -1
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None
                self.lcount = 0              # number of nodes in the left subtree

        def insert(root, key):
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
                root.lcount += 1             # one more node went into my left subtree
            elif key > root.key:
                root.right = insert(root.right, key)
            return root

        def kth_smallest(root, k):
            while root:
                rank = root.lcount + 1       # this node is the rank-th smallest of its subtree
                if rank == k:
                    return root.key
                if k < rank:
                    root = root.left         # answer is in the left subtree
                else:
                    k -= rank                # skip the left subtree and this node
                    root = root.right
            return -1

        root = None
        for x in [20, 8, 22, 4, 12, 10, 14]:
            root = insert(root, x)
        for k in (3, 7, 8):
            print(f"k={k}: {kth_smallest(root, k)}")
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int key;
            int lcount = 0;                      // number of nodes in the left subtree
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        Node* insert(Node* root, int key) {
            if (!root) return new Node(key);
            if (key < root->key) {
                root->left = insert(root->left, key);
                root->lcount++;                  // one more node went into my left subtree
            } else if (key > root->key) {
                root->right = insert(root->right, key);
            }
            return root;
        }

        int kthSmallest(Node* root, int k) {
            while (root) {
                int rank = root->lcount + 1;     // this node is the rank-th smallest of its subtree
                if (rank == k) return root->key;
                if (k < rank) root = root->left;             // answer is in the left subtree
                else { k -= rank; root = root->right; }      // skip the left subtree and this node
            }
            return -1;
        }

        int main() {
            Node* root = nullptr;
            for (int x : {20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
            for (int k : {3, 7, 8}) cout << "k=" << k << ": " << kthSmallest(root, k) << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int key, lcount;                 // lcount = number of nodes in the left subtree
                Node left, right;
                Node(int k) { key = k; }
            }

            static Node insert(Node root, int key) {
                if (root == null) return new Node(key);
                if (key < root.key) {
                    root.left = insert(root.left, key);
                    root.lcount++;               // one more node went into my left subtree
                } else if (key > root.key) {
                    root.right = insert(root.right, key);
                }
                return root;
            }

            static int kthSmallest(Node root, int k) {
                while (root != null) {
                    int rank = root.lcount + 1;  // this node is the rank-th smallest of its subtree
                    if (rank == k) return root.key;
                    if (k < rank) root = root.left;              // answer is in the left subtree
                    else { k -= rank; root = root.right; }       // skip the left subtree and this node
                }
                return -1;
            }

            public static void main(String[] args) {
                Node root = null;
                for (int x : new int[]{20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
                for (int k : new int[]{3, 7, 8}) System.out.println("k=" + k + ": " + kthSmallest(root, k));
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; this.lcount = 0; }
        }

        function insert(root, key) {
            if (!root) return new Node(key);
            if (key < root.key) {
                root.left = insert(root.left, key);
                root.lcount++;                   // one more node went into my left subtree
            } else if (key > root.key) {
                root.right = insert(root.right, key);
            }
            return root;
        }

        function kthSmallest(root, k) {
            while (root) {
                const rank = root.lcount + 1;    // this node is the rank-th smallest of its subtree
                if (rank === k) return root.key;
                if (k < rank) root = root.left;                  // answer is in the left subtree
                else { k -= rank; root = root.right; }           // skip the left subtree and this node
            }
            return -1;
        }

        let root = null;
        for (const x of [20, 8, 22, 4, 12, 10, 14]) root = insert(root, x);
        for (const k of [3, 7, 8]) console.log(`k=${k}: ${kthSmallest(root, k)}`);
    ''')
    yield complexity("O(h)", "O(1)")
    yield note("The same `lcount` field answers **rank(x)** (how many keys are `< x`) in `O(h)`, and `n - k + 1` turns *kth smallest* into *kth largest*. If the tree also supports `delete`, every node on the deletion path whose left subtree shrank must have its `lcount` decremented — forgetting that silently corrupts later queries.")

    yield section("Check whether a binary tree is a BST", "checks")
    yield diagram('''
          tree A (valid)             tree B (NOT a BST)
                20                         20
              /    \\                     /    \\
             8      22                  8      22
           /   \\                      /   \\
          4     12                   4     25   ← 25 > 20 but sits in 20's left subtree
               /  \\
             10    14
    ''', "Every node of tree B passes a parent-vs-children check, yet tree B is not a BST")
    yield io("tree A", "Yes", "tree B", "No")
    yield p("The tempting solution compares each node with its two children only. It accepts tree B:")
    yield snippet("py", '''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def looks_like_bst(root):                 # WRONG: only compares a node with its own children
            if root is None:
                return True
            if root.left and root.left.key > root.key:
                return False
            if root.right and root.right.key < root.key:
                return False
            return looks_like_bst(root.left) and looks_like_bst(root.right)

        b = Node(20)
        b.left, b.right = Node(8), Node(22)
        b.left.left, b.left.right = Node(4), Node(25)      # 25 violates the rule at its grandparent 20
        print("tree B:", "Yes" if looks_like_bst(b) else "No")
    ''', out="tree B: Yes")
    yield bad("`8 < 20`, `4 < 8 < 25`, `20 < 22` — every local check passes, yet `25` is in the left subtree of `20`. The BST rule constrains a node by **all** of its ancestors, not just its parent.")
    yield p("A correct but slow fix checks, for every node, the maximum of the whole left subtree and the minimum of the whole right subtree. Each node is scanned by each of its ancestors, which is `O(n²)` on a skewed tree:")
    yield snippet("py", '''
        import sys

        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def max_key(root):
            if root is None:
                return -sys.maxsize
            return max(root.key, max_key(root.left), max_key(root.right))

        def min_key(root):
            if root is None:
                return sys.maxsize
            return min(root.key, min_key(root.left), min_key(root.right))

        def is_bst_slow(root):
            if root is None:
                return True
            if root.left and max_key(root.left) >= root.key:        # whole left subtree must be smaller
                return False
            if root.right and min_key(root.right) <= root.key:      # whole right subtree must be larger
                return False
            return is_bst_slow(root.left) and is_bst_slow(root.right)

        a = Node(20)
        a.left, a.right = Node(8), Node(22)
        a.left.left, a.left.right = Node(4), Node(12)
        a.left.right.left, a.left.right.right = Node(10), Node(14)

        b = Node(20)
        b.left, b.right = Node(8), Node(22)
        b.left.left, b.left.right = Node(4), Node(25)

        print("tree A:", "Yes" if is_bst_slow(a) else "No")
        print("tree B:", "Yes" if is_bst_slow(b) else "No")
    ''', out='''
        tree A: Yes
        tree B: No
    ''')
    yield complexity("O(n²) worst case", "O(h)")
    yield idea("**Range method.** Pass down the open interval `(lo, hi)` that the ancestors allow. The root may be anything; going left tightens `hi` to the current key, going right tightens `lo`. Each node is visited once and checked against two numbers — `O(n)`.")
    yield multi('''
        tree A: Yes
        tree B: No
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def is_bst(root, lo=float("-inf"), hi=float("inf")):
            if root is None:
                return True
            if not (lo < root.key < hi):             # must lie strictly inside the ancestors' range
                return False
            return (is_bst(root.left, lo, root.key)   # left subtree: everything < root.key
                    and is_bst(root.right, root.key, hi))   # right subtree: everything > root.key

        a = Node(20)
        a.left, a.right = Node(8), Node(22)
        a.left.left, a.left.right = Node(4), Node(12)
        a.left.right.left, a.left.right.right = Node(10), Node(14)

        b = Node(20)
        b.left, b.right = Node(8), Node(22)
        b.left.left, b.left.right = Node(4), Node(25)

        print("tree A:", "Yes" if is_bst(a) else "No")
        print("tree B:", "Yes" if is_bst(b) else "No")
    ''', cpp='''
        #include <climits>
        #include <iostream>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        bool isBST(Node* root, long long lo, long long hi) {
            if (!root) return true;
            if (root->key <= lo || root->key >= hi) return false;     // outside the ancestors' range
            return isBST(root->left, lo, root->key)                  // left: everything < key
                && isBST(root->right, root->key, hi);                // right: everything > key
        }

        int main() {
            Node* a = new Node(20);
            a->left = new Node(8); a->right = new Node(22);
            a->left->left = new Node(4); a->left->right = new Node(12);
            a->left->right->left = new Node(10); a->left->right->right = new Node(14);

            Node* b = new Node(20);
            b->left = new Node(8); b->right = new Node(22);
            b->left->left = new Node(4); b->left->right = new Node(25);

            cout << "tree A: " << (isBST(a, LLONG_MIN, LLONG_MAX) ? "Yes" : "No") << "\\n";
            cout << "tree B: " << (isBST(b, LLONG_MIN, LLONG_MAX) ? "Yes" : "No") << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static boolean isBST(Node root, long lo, long hi) {
                if (root == null) return true;
                if (root.key <= lo || root.key >= hi) return false;   // outside the ancestors' range
                return isBST(root.left, lo, root.key)                 // left: everything < key
                    && isBST(root.right, root.key, hi);               // right: everything > key
            }

            public static void main(String[] args) {
                Node a = new Node(20);
                a.left = new Node(8); a.right = new Node(22);
                a.left.left = new Node(4); a.left.right = new Node(12);
                a.left.right.left = new Node(10); a.left.right.right = new Node(14);

                Node b = new Node(20);
                b.left = new Node(8); b.right = new Node(22);
                b.left.left = new Node(4); b.left.right = new Node(25);

                System.out.println("tree A: " + (isBST(a, Long.MIN_VALUE, Long.MAX_VALUE) ? "Yes" : "No"));
                System.out.println("tree B: " + (isBST(b, Long.MIN_VALUE, Long.MAX_VALUE) ? "Yes" : "No"));
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function isBST(root, lo = -Infinity, hi = Infinity) {
            if (!root) return true;
            if (root.key <= lo || root.key >= hi) return false;       // outside the ancestors' range
            return isBST(root.left, lo, root.key)                     // left: everything < key
                && isBST(root.right, root.key, hi);                   // right: everything > key
        }

        const a = new Node(20);
        a.left = new Node(8); a.right = new Node(22);
        a.left.left = new Node(4); a.left.right = new Node(12);
        a.left.right.left = new Node(10); a.left.right.right = new Node(14);

        const b = new Node(20);
        b.left = new Node(8); b.right = new Node(22);
        b.left.left = new Node(4); b.left.right = new Node(25);

        console.log("tree A:", isBST(a) ? "Yes" : "No");
        console.log("tree B:", isBST(b) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(h)")
    yield pitfall("Using `INT_MIN` / `INT_MAX` as the initial bounds with `int` keys rejects a tree that legitimately contains `INT_MIN` or `INT_MAX` (the check is strict). Use a wider type for the bounds (`long long` / `long`), `±Infinity` in JavaScript, or `None` sentinels meaning *unbounded*.")
    yield idea("**Inorder-previous method.** Inorder of a BST is strictly increasing. Traverse inorder and remember the previous key; the moment the current key is `<=` the previous one, the tree is not a BST. One pass, no bounds, and it stops at the first violation.")
    yield multi('''
        tree A: Yes
        tree B: No
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def is_bst(root):
            stack, node, prev = [], root, None
            while stack or node:
                while node:                        # iterative inorder traversal
                    stack.append(node)
                    node = node.left
                node = stack.pop()
                if prev is not None and node.key <= prev:     # inorder must strictly increase
                    return False
                prev = node.key
                node = node.right
            return True

        a = Node(20)
        a.left, a.right = Node(8), Node(22)
        a.left.left, a.left.right = Node(4), Node(12)
        a.left.right.left, a.left.right.right = Node(10), Node(14)

        b = Node(20)
        b.left, b.right = Node(8), Node(22)
        b.left.left, b.left.right = Node(4), Node(25)

        print("tree A:", "Yes" if is_bst(a) else "No")
        print("tree B:", "Yes" if is_bst(b) else "No")
    ''', cpp='''
        #include <iostream>
        #include <stack>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        bool isBST(Node* root) {
            stack<Node*> st;
            Node* node = root;
            bool havePrev = false;
            int prev = 0;
            while (!st.empty() || node) {
                while (node) { st.push(node); node = node->left; }   // iterative inorder traversal
                node = st.top(); st.pop();
                if (havePrev && node->key <= prev) return false;     // inorder must strictly increase
                prev = node->key; havePrev = true;
                node = node->right;
            }
            return true;
        }

        int main() {
            Node* a = new Node(20);
            a->left = new Node(8); a->right = new Node(22);
            a->left->left = new Node(4); a->left->right = new Node(12);
            a->left->right->left = new Node(10); a->left->right->right = new Node(14);

            Node* b = new Node(20);
            b->left = new Node(8); b->right = new Node(22);
            b->left->left = new Node(4); b->left->right = new Node(25);

            cout << "tree A: " << (isBST(a) ? "Yes" : "No") << "\\n";
            cout << "tree B: " << (isBST(b) ? "Yes" : "No") << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static boolean isBST(Node root) {
                Deque<Node> stack = new ArrayDeque<>();
                Node node = root;
                Integer prev = null;
                while (!stack.isEmpty() || node != null) {
                    while (node != null) { stack.push(node); node = node.left; }   // iterative inorder
                    node = stack.pop();
                    if (prev != null && node.key <= prev) return false;             // must strictly increase
                    prev = node.key;
                    node = node.right;
                }
                return true;
            }

            public static void main(String[] args) {
                Node a = new Node(20);
                a.left = new Node(8); a.right = new Node(22);
                a.left.left = new Node(4); a.left.right = new Node(12);
                a.left.right.left = new Node(10); a.left.right.right = new Node(14);

                Node b = new Node(20);
                b.left = new Node(8); b.right = new Node(22);
                b.left.left = new Node(4); b.left.right = new Node(25);

                System.out.println("tree A: " + (isBST(a) ? "Yes" : "No"));
                System.out.println("tree B: " + (isBST(b) ? "Yes" : "No"));
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function isBST(root) {
            const stack = [];
            let node = root, prev = null;
            while (stack.length || node) {
                while (node) { stack.push(node); node = node.left; }   // iterative inorder traversal
                node = stack.pop();
                if (prev !== null && node.key <= prev) return false;    // inorder must strictly increase
                prev = node.key;
                node = node.right;
            }
            return true;
        }

        const a = new Node(20);
        a.left = new Node(8); a.right = new Node(22);
        a.left.left = new Node(4); a.left.right = new Node(12);
        a.left.right.left = new Node(10); a.left.right.right = new Node(14);

        const b = new Node(20);
        b.left = new Node(8); b.right = new Node(22);
        b.left.left = new Node(4); b.left.right = new Node(25);

        console.log("tree A:", isBST(a) ? "Yes" : "No");
        console.log("tree B:", isBST(b) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(h)")
    yield note("Both methods use a **strict** comparison, so a tree with duplicate keys is rejected. If your definition allows duplicates on one side (say `left <= node`), relax exactly that one bound — and say so in the interview before you code.")

    yield section("Fix a BST with two nodes swapped", "arrows-exchange")
    yield diagram('''
            given (two keys swapped)             fixed
                    20                             20
                  /    \\                         /    \\
                60      80        ──▶           8      80
               /  \\    /  \\                   /  \\    /  \\
              4   10  8   100                4   10  60   100

        inorder:  4  60  10  20  8  80  100   →   4  8  10  20  60  80  100
                     ^^^^^^      ^^^^^
                      dip 1       dip 2
    ''', "Swapping 60 and 8 back restores the sorted inorder sequence")
    yield io("tree above", "inorder before: 4 60 10 20 8 80 100, after: 4 8 10 20 60 80 100")
    yield idea("The inorder sequence of a BST is sorted; swapping two keys creates **one or two dips** (a place where a key is smaller than its predecessor). With two dips, the swapped nodes are the *larger* element of the first dip and the *smaller* element of the second; with one dip (the two nodes are inorder-adjacent) they are the two elements of that dip. Record `first` at the first dip and overwrite `second` at every dip, then swap their keys.")
    yield steps(
        ("Traverse inorder, remembering `prev`", "At each node compare `node.key` with `prev.key`."),
        ("First dip (`node.key < prev.key`)", "Set `first = prev` and `second = node`."),
        ("Second dip", "Only `second = node` changes — `first` stays the larger element of the first dip."),
        ("Swap", "Exchange `first.key` and `second.key`. The structure of the tree is untouched."),
    )
    yield multi('''
        before: 4 60 10 20 8 80 100
        after: 4 8 10 20 60 80 100
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        class Fixer:
            def __init__(self):
                self.prev = self.first = self.second = None

            def visit(self, node):                        # inorder, looking for dips
                if node is None:
                    return
                self.visit(node.left)
                if self.prev and node.key < self.prev.key:  # a dip: smaller key after a larger one
                    if self.first is None:
                        self.first = self.prev            # first dip: remember the larger element
                    self.second = node                    # the smaller element (overwritten by a 2nd dip)
                self.prev = node
                self.visit(node.right)

        def fix_bst(root):
            f = Fixer()
            f.visit(root)
            if f.first and f.second:
                f.first.key, f.second.key = f.second.key, f.first.key

        def inorder(node, out):
            if node:
                inorder(node.left, out)
                out.append(node.key)
                inorder(node.right, out)

        root = Node(20)
        root.left, root.right = Node(60), Node(80)
        root.left.left, root.left.right = Node(4), Node(10)
        root.right.left, root.right.right = Node(8), Node(100)

        before = []
        inorder(root, before)
        print("before:", *before)
        fix_bst(root)
        after = []
        inorder(root, after)
        print("after:", *after)
    ''', cpp='''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        struct Fixer {
            Node *prev = nullptr, *first = nullptr, *second = nullptr;
            void visit(Node* node) {                           // inorder, looking for dips
                if (!node) return;
                visit(node->left);
                if (prev && node->key < prev->key) {           // a dip: smaller key after a larger one
                    if (!first) first = prev;                  // first dip: remember the larger element
                    second = node;                             // the smaller element (overwritten by a 2nd dip)
                }
                prev = node;
                visit(node->right);
            }
        };

        void fixBST(Node* root) {
            Fixer f;
            f.visit(root);
            if (f.first && f.second) swap(f.first->key, f.second->key);
        }

        void inorder(Node* node, vector<int>& out) {
            if (!node) return;
            inorder(node->left, out);
            out.push_back(node->key);
            inorder(node->right, out);
        }

        void printKeys(const char* label, Node* root) {
            vector<int> keys;
            inorder(root, keys);
            cout << label;
            for (int k : keys) cout << " " << k;
            cout << "\\n";
        }

        int main() {
            Node* root = new Node(20);
            root->left = new Node(60); root->right = new Node(80);
            root->left->left = new Node(4); root->left->right = new Node(10);
            root->right->left = new Node(8); root->right->right = new Node(100);

            printKeys("before:", root);
            fixBST(root);
            printKeys("after:", root);
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static class Fixer {
                Node prev, first, second;
                void visit(Node node) {                        // inorder, looking for dips
                    if (node == null) return;
                    visit(node.left);
                    if (prev != null && node.key < prev.key) { // a dip: smaller key after a larger one
                        if (first == null) first = prev;       // first dip: remember the larger element
                        second = node;                         // the smaller element (overwritten by a 2nd dip)
                    }
                    prev = node;
                    visit(node.right);
                }
            }

            static void fixBST(Node root) {
                Fixer f = new Fixer();
                f.visit(root);
                if (f.first != null && f.second != null) {
                    int t = f.first.key; f.first.key = f.second.key; f.second.key = t;
                }
            }

            static void inorder(Node node, List<Integer> out) {
                if (node == null) return;
                inorder(node.left, out);
                out.add(node.key);
                inorder(node.right, out);
            }

            static void printKeys(String label, Node root) {
                List<Integer> keys = new ArrayList<>();
                inorder(root, keys);
                StringBuilder sb = new StringBuilder(label);
                for (int k : keys) sb.append(' ').append(k);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                Node root = new Node(20);
                root.left = new Node(60); root.right = new Node(80);
                root.left.left = new Node(4); root.left.right = new Node(10);
                root.right.left = new Node(8); root.right.right = new Node(100);

                printKeys("before:", root);
                fixBST(root);
                printKeys("after:", root);
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        class Fixer {
            constructor() { this.prev = null; this.first = null; this.second = null; }
            visit(node) {                                        // inorder, looking for dips
                if (!node) return;
                this.visit(node.left);
                if (this.prev && node.key < this.prev.key) {     // a dip: smaller key after a larger one
                    if (!this.first) this.first = this.prev;     // first dip: remember the larger element
                    this.second = node;                          // the smaller element (overwritten by a 2nd dip)
                }
                this.prev = node;
                this.visit(node.right);
            }
        }

        function fixBST(root) {
            const f = new Fixer();
            f.visit(root);
            if (f.first && f.second) [f.first.key, f.second.key] = [f.second.key, f.first.key];
        }

        function inorder(node, out) {
            if (!node) return;
            inorder(node.left, out);
            out.push(node.key);
            inorder(node.right, out);
        }

        const root = new Node(20);
        root.left = new Node(60); root.right = new Node(80);
        root.left.left = new Node(4); root.left.right = new Node(10);
        root.right.left = new Node(8); root.right.right = new Node(100);

        const before = [];
        inorder(root, before);
        console.log("before:", before.join(" "));
        fixBST(root);
        const after = [];
        inorder(root, after);
        console.log("after:", after.join(" "));
    ''')
    yield complexity("O(n)", "O(h)")
    yield pitfall("Setting `second = prev` at the second dip (instead of `second = node`) picks the wrong node. Trace the adjacent case too: in `8 / 20 22` (the root `20` swapped with its child `8`) the inorder is `20 8 22` — a single dip, so `first = 20`, `second = 8`, and the single swap is correct. The original notes kept `prev`/`first`/`second` as globals, which breaks as soon as the function is called twice; the `Fixer` object above resets them per call.")

    yield section("Pair with a given sum in a BST", "plus")
    yield io("tree A, sum = 30", "Yes (8 + 22, or 10 + 20)", "tree A, sum = 29", "No")
    yield idea("**Method 1 — inorder + two pointers.** Inorder gives the keys sorted. Then the classic sorted-array trick: a pointer at each end, move the left one right when the sum is too small and the right one left when it is too large. `O(n)` time, `O(n)` for the array.")
    yield multi('''
        sum=30: Yes (8 + 22)
        sum=29: No
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def insert(root, key):
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
            elif key > root.key:
                root.right = insert(root.right, key)
            return root

        def inorder(node, out):
            if node:
                inorder(node.left, out)
                out.append(node.key)
                inorder(node.right, out)

        def pair_sum(root, target):
            keys = []
            inorder(root, keys)                     # sorted keys
            i, j = 0, len(keys) - 1
            while i < j:                            # two pointers on a sorted array
                s = keys[i] + keys[j]
                if s == target:
                    return (keys[i], keys[j])
                if s < target:
                    i += 1                          # need a bigger sum
                else:
                    j -= 1                          # need a smaller sum
            return None

        root = None
        for x in [20, 8, 22, 4, 12, 10, 14]:
            root = insert(root, x)
        for target in (30, 29):
            res = pair_sum(root, target)
            print(f"sum={target}:", f"Yes ({res[0]} + {res[1]})" if res else "No")
    ''', cpp='''
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        Node* insert(Node* root, int key) {
            if (!root) return new Node(key);
            if (key < root->key) root->left = insert(root->left, key);
            else if (key > root->key) root->right = insert(root->right, key);
            return root;
        }

        void inorder(Node* node, vector<int>& out) {
            if (!node) return;
            inorder(node->left, out);
            out.push_back(node->key);
            inorder(node->right, out);
        }

        bool pairSum(Node* root, int target, int& a, int& b) {
            vector<int> keys;
            inorder(root, keys);                              // sorted keys
            int i = 0, j = (int)keys.size() - 1;
            while (i < j) {                                   // two pointers on a sorted array
                int s = keys[i] + keys[j];
                if (s == target) { a = keys[i]; b = keys[j]; return true; }
                if (s < target) i++;                          // need a bigger sum
                else j--;                                     // need a smaller sum
            }
            return false;
        }

        int main() {
            Node* root = nullptr;
            for (int x : {20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
            for (int target : {30, 29}) {
                int a, b;
                if (pairSum(root, target, a, b)) cout << "sum=" << target << ": Yes (" << a << " + " << b << ")\\n";
                else cout << "sum=" << target << ": No\\n";
            }
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node insert(Node root, int key) {
                if (root == null) return new Node(key);
                if (key < root.key) root.left = insert(root.left, key);
                else if (key > root.key) root.right = insert(root.right, key);
                return root;
            }

            static void inorder(Node node, List<Integer> out) {
                if (node == null) return;
                inorder(node.left, out);
                out.add(node.key);
                inorder(node.right, out);
            }

            static int[] pairSum(Node root, int target) {
                List<Integer> keys = new ArrayList<>();
                inorder(root, keys);                              // sorted keys
                int i = 0, j = keys.size() - 1;
                while (i < j) {                                   // two pointers on a sorted array
                    int s = keys.get(i) + keys.get(j);
                    if (s == target) return new int[]{keys.get(i), keys.get(j)};
                    if (s < target) i++;                          // need a bigger sum
                    else j--;                                     // need a smaller sum
                }
                return null;
            }

            public static void main(String[] args) {
                Node root = null;
                for (int x : new int[]{20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
                for (int target : new int[]{30, 29}) {
                    int[] res = pairSum(root, target);
                    System.out.println("sum=" + target + ": " + (res == null ? "No" : "Yes (" + res[0] + " + " + res[1] + ")"));
                }
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insert(root, key) {
            if (!root) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            return root;
        }

        function inorder(node, out) {
            if (!node) return;
            inorder(node.left, out);
            out.push(node.key);
            inorder(node.right, out);
        }

        function pairSum(root, target) {
            const keys = [];
            inorder(root, keys);                                  // sorted keys
            let i = 0, j = keys.length - 1;
            while (i < j) {                                       // two pointers on a sorted array
                const s = keys[i] + keys[j];
                if (s === target) return [keys[i], keys[j]];
                if (s < target) i++;                              // need a bigger sum
                else j--;                                         // need a smaller sum
            }
            return null;
        }

        let root = null;
        for (const x of [20, 8, 22, 4, 12, 10, 14]) root = insert(root, x);
        for (const target of [30, 29]) {
            const res = pairSum(root, target);
            console.log(`sum=${target}:`, res ? `Yes (${res[0]} + ${res[1]})` : "No");
        }
    ''')
    yield complexity("O(n)", "O(n)")
    yield idea("**Method 2 — hash set during the traversal.** Visit the nodes (inorder here, but any order works) and keep the keys seen so far in a set. At each node ask whether `target - key` has already been seen; if not, add `key`. This is exactly the array “pair sum with hashing” solution, run on the tree in place. It reports a different (equally valid) pair than the two-pointer method — `10 + 20` is complete as soon as `20` is visited, before `22` is reached.")
    yield multi('''
        sum=30: Yes (10 + 20)
        sum=29: No
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def insert(root, key):
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
            elif key > root.key:
                root.right = insert(root.right, key)
            return root

        def pair_sum(node, target, seen):
            if node is None:
                return None
            found = pair_sum(node.left, target, seen)
            if found:
                return found
            if target - node.key in seen:            # the partner was visited earlier
                return (target - node.key, node.key)
            seen.add(node.key)
            return pair_sum(node.right, target, seen)

        root = None
        for x in [20, 8, 22, 4, 12, 10, 14]:
            root = insert(root, x)
        for target in (30, 29):
            res = pair_sum(root, target, set())      # a fresh set per query
            print(f"sum={target}:", f"Yes ({res[0]} + {res[1]})" if res else "No")
    ''', cpp='''
        #include <iostream>
        #include <unordered_set>
        using namespace std;

        struct Node {
            int key;
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        Node* insert(Node* root, int key) {
            if (!root) return new Node(key);
            if (key < root->key) root->left = insert(root->left, key);
            else if (key > root->key) root->right = insert(root->right, key);
            return root;
        }

        bool pairSum(Node* node, int target, unordered_set<int>& seen, int& a, int& b) {
            if (!node) return false;
            if (pairSum(node->left, target, seen, a, b)) return true;
            if (seen.count(target - node->key)) {               // the partner was visited earlier
                a = target - node->key; b = node->key;
                return true;
            }
            seen.insert(node->key);
            return pairSum(node->right, target, seen, a, b);
        }

        int main() {
            Node* root = nullptr;
            for (int x : {20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
            for (int target : {30, 29}) {
                unordered_set<int> seen;                         // a fresh set per query
                int a, b;
                if (pairSum(root, target, seen, a, b)) cout << "sum=" << target << ": Yes (" << a << " + " << b << ")\\n";
                else cout << "sum=" << target << ": No\\n";
            }
        }
    ''', java='''
        import java.util.HashSet;
        import java.util.Set;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node insert(Node root, int key) {
                if (root == null) return new Node(key);
                if (key < root.key) root.left = insert(root.left, key);
                else if (key > root.key) root.right = insert(root.right, key);
                return root;
            }

            static int[] pairSum(Node node, int target, Set<Integer> seen) {
                if (node == null) return null;
                int[] found = pairSum(node.left, target, seen);
                if (found != null) return found;
                if (seen.contains(target - node.key))             // the partner was visited earlier
                    return new int[]{target - node.key, node.key};
                seen.add(node.key);
                return pairSum(node.right, target, seen);
            }

            public static void main(String[] args) {
                Node root = null;
                for (int x : new int[]{20, 8, 22, 4, 12, 10, 14}) root = insert(root, x);
                for (int target : new int[]{30, 29}) {
                    int[] res = pairSum(root, target, new HashSet<>());   // a fresh set per query
                    System.out.println("sum=" + target + ": " + (res == null ? "No" : "Yes (" + res[0] + " + " + res[1] + ")"));
                }
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insert(root, key) {
            if (!root) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            return root;
        }

        function pairSum(node, target, seen) {
            if (!node) return null;
            const found = pairSum(node.left, target, seen);
            if (found) return found;
            if (seen.has(target - node.key))                      // the partner was visited earlier
                return [target - node.key, node.key];
            seen.add(node.key);
            return pairSum(node.right, target, seen);
        }

        let root = null;
        for (const x of [20, 8, 22, 4, 12, 10, 14]) root = insert(root, x);
        for (const target of [30, 29]) {
            const res = pairSum(root, target, new Set());        // a fresh set per query
            console.log(`sum=${target}:`, res ? `Yes (${res[0]} + ${res[1]})` : "No");
        }
    ''')
    yield complexity("O(n)", "O(n)")
    yield note("Both methods are `O(n)` time and `O(n)` extra space. The **`O(h)` space** version runs the two-pointer idea directly on the tree: one stack performs a forward inorder (left-node-right) and a second stack a reverse inorder (right-node-left); advance whichever side the two-pointer rule says to move. It is the same algorithm with the sorted array replaced by two lazy iterators.")
    yield pitfall("`target - node.key in seen` must be checked **before** `seen.add(node.key)`; otherwise a node pairs with itself when `target = 2 * key` (sum `40` would report `20 + 20` on tree A).")

    yield section("Interview Q&A", "message-question")
    yield qa("Why is the inorder traversal of a BST sorted?",
             "Inorder visits the left subtree, then the node, then the right subtree. By the BST invariant everything in the left subtree is smaller than the node and everything in the right subtree is larger, and the same holds recursively inside each subtree — so the sequence produced is ascending. Reverse inorder (right, node, left) gives descending order.")
    yield qa("How do you find the kth smallest in O(h) when the tree changes over time?",
             "Augment every node with the size of its left subtree. Insert and delete update that count along the single path they touch (`O(h)`), and the query walks down comparing `k` with `lcount + 1`. The plain inorder method is `O(h + k)` per query and needs no extra field — fine for one-off queries, not for a stream of them.")
    yield qa("Why does comparing a node with its children not prove a tree is a BST?",
             "Because the invariant constrains a node by **all** its ancestors. In tree B above, `25` is a valid right child of `8` but it lives in the left subtree of `20`, where every key must be below `20`. Pass down the `(lo, hi)` range from the ancestors, or check that the inorder sequence strictly increases — both are `O(n)`.")
    yield qa("Two nodes of a BST were swapped. How many dips can the inorder sequence have, and which nodes do you swap back?",
             "One or two. If the swapped nodes are adjacent in inorder there is one dip and its two elements are the culprits. Otherwise there are two dips: the larger element of the first dip and the smaller element of the second. Recording `first = prev` only at the first dip and `second = node` at every dip handles both cases with one pass.")
    yield qa("What are std::set, TreeMap and heapq in terms of BSTs?",
             "`std::set`/`std::map` and Java's `TreeSet`/`TreeMap` are red-black trees — self-balancing BSTs with `O(log n)` insert, delete, `lower_bound`/`ceiling`, `floor` and ordered iteration. `heapq` is **not** a BST: a heap only exposes its minimum, so it cannot answer floor/ceiling or kth queries. Python and JavaScript have no ordered-set container in the standard library.")
    yield qa("How would you find the lowest common ancestor of two keys in a BST?",
             "Walk down from the root: if both keys are smaller go left, if both are larger go right, otherwise the current node is the split point and therefore the LCA. `O(h)` time, no parent pointers and no recursion needed — a general binary tree needs an `O(n)` traversal instead.")


@topic(G, "heap", "Heap", "triangle")
def _():
    yield lead("A heap gives you the smallest (or largest) element of a changing collection in `O(1)`, with `O(log n)` insert and remove. Almost every “top k”, “k-way merge” and “running statistic” problem is a heap of the right **type** and the right **size**.")
    yield define("Binary heap", "a complete binary tree stored in an array where every node is `<=` its children (**min-heap**) or `>=` its children (**max-heap**). The root is therefore the minimum (or maximum). A *priority queue* is the abstract interface; a binary heap is its usual implementation.")
    yield diagram('''
        min-heap as a tree              the same heap as an array
                 5                      index:  0   1   2   3   4
               /   \\                   value:  5   8  10  15  20
              8     10
             / \\                       parent(i) = (i - 1) / 2
           15   20                     children(i) = 2i + 1, 2i + 2
    ''', "A heap is just an array with a parent/child index rule — no pointers")
    yield table(
        ["Operation", "Time", "How"],
        ["`peek()` — min or max", "O(1)", "it is `a[0]`"],
        ["`push(x)`", "O(log n)", "append, then *sift up* while smaller than the parent"],
        ["`pop()`", "O(log n)", "move the last element to the root, then *sift down*"],
        ["`heapify(array)`", "O(n)", "sift down from the last internal node to the root — cheaper than `n` pushes"],
        ["search for an arbitrary key", "O(n)", "a heap is **not** sorted; only the root is special"],
    )
    yield note("The heap property says nothing about the order between siblings or between subtrees — `a[1..]` is not sorted. Printing the array of a heap or iterating a `PriorityQueue` gives an arbitrary-looking order; to get sorted output you must pop repeatedly.")

    yield section("Priority queues in each language", "box")
    yield table(
        ["Language", "Type", "Default", "Max-heap"],
        ["Python", "`heapq` functions on a list", "min-heap", "push `-x`, negate on pop (or `(-key, item)` tuples)"],
        ["C++", "`std::priority_queue<T>`", "**max**-heap", "default; min-heap needs `priority_queue<T, vector<T>, greater<T>>`"],
        ["Java", "`java.util.PriorityQueue<T>`", "min-heap", "`new PriorityQueue<>(Collections.reverseOrder())` or a comparator"],
        ["JavaScript", "none built in", "—", "write a small `Heap` class with a comparator once (below) and reuse it"],
    )
    yield multi('''
        min-heap: 5 8 10 15 20
        max-heap: 20 15 10 8 5
    ''', py='''
        import heapq

        nums = [5, 15, 10, 20, 8]

        mn = []                                  # heapq is a min-heap only
        for x in nums:
            heapq.heappush(mn, x)
        print("min-heap:", *(heapq.heappop(mn) for _ in range(len(nums))))

        mx = [-x for x in nums]                  # max-heap: store the negated keys
        heapq.heapify(mx)                        # O(n) build
        print("max-heap:", *(-heapq.heappop(mx) for _ in range(len(nums))))
    ''', cpp='''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        int main() {
            vector<int> nums = {5, 15, 10, 20, 8};

            priority_queue<int, vector<int>, greater<int>> mn;     // min-heap needs greater<>
            for (int x : nums) mn.push(x);
            cout << "min-heap:";
            while (!mn.empty()) { cout << " " << mn.top(); mn.pop(); }
            cout << "\\n";

            priority_queue<int> mx(nums.begin(), nums.end());       // default is a max-heap; O(n) build
            cout << "max-heap:";
            while (!mx.empty()) { cout << " " << mx.top(); mx.pop(); }
            cout << "\\n";
        }
    ''', java='''
        import java.util.Collections;
        import java.util.PriorityQueue;

        public class Main {
            public static void main(String[] args) {
                int[] nums = {5, 15, 10, 20, 8};

                PriorityQueue<Integer> mn = new PriorityQueue<>();        // min-heap by default
                for (int x : nums) mn.add(x);
                StringBuilder sb = new StringBuilder("min-heap:");
                while (!mn.isEmpty()) sb.append(' ').append(mn.poll());
                System.out.println(sb);

                PriorityQueue<Integer> mx = new PriorityQueue<>(Collections.reverseOrder());   // or (a, b) -> b - a
                for (int x : nums) mx.add(x);
                sb = new StringBuilder("max-heap:");
                while (!mx.isEmpty()) sb.append(' ').append(mx.poll());
                System.out.println(sb);
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }   // cmp(x, y) < 0 → x comes out first
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {                                    // sift up
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {                                     // sift down
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        const nums = [5, 15, 10, 20, 8];

        const mn = new Heap((a, b) => a - b);                      // min-heap
        for (const x of nums) mn.push(x);
        const small = [];
        while (mn.size()) small.push(mn.pop());
        console.log("min-heap:", small.join(" "));

        const mx = new Heap((a, b) => b - a);                      // max-heap: flip the comparator
        for (const x of nums) mx.push(x);
        const big = [];
        while (mx.size()) big.push(mx.pop());
        console.log("max-heap:", big.join(" "));
    ''')
    yield note("The JavaScript `Heap` class above is reused unchanged in every solution below — comparator `(a, b) => a - b` for a min-heap, `(a, b) => b - a` for a max-heap, or compare a field of an array/object. Python's `heapq` compares tuples lexicographically, which is how `(key, payload)` pairs are ordered in the k-closest and merge problems.")
    yield pitfall("Python: `heapq.heappush(h, -x)` and forgetting to negate on the way out is the classic max-heap slip. Java: `(a, b) -> b - a` overflows for values near `Integer.MIN_VALUE` / `MAX_VALUE` — use `Integer.compare(b, a)` or `Collections.reverseOrder()`. C++: remember the default `priority_queue` is a **max**-heap.")

    yield section("Sort a k-sorted (nearly sorted) array", "arrows-sort")
    yield io("arr = [9, 8, 7, 18, 19, 17], k = 2", "7 8 9 17 18 19", "arr = [10, 9, 8, 7, 4, 70, 60, 50], k = 4", "4 7 8 9 10 50 60 70")
    yield p("Every element is at most `k` positions away from its sorted position. A full sort is `O(n log n)`; exploiting `k` gives `O(n log k)`.")
    yield idea("The element that belongs at index `i` lies somewhere in `arr[i..i+k]`. So keep a min-heap of the next `k+1` unplaced elements: its minimum is guaranteed to be the next output. Push one element, and whenever the heap holds `k+1` items pop its minimum into the result; drain the heap at the end.")
    yield multi('''
        7 8 9 17 18 19
        4 7 8 9 10 50 60 70
    ''', py='''
        import heapq

        def sort_k(arr, k):
            h, res = [], []
            for x in arr:
                heapq.heappush(h, x)
                if len(h) > k:                   # k+1 elements inside → the minimum is final
                    res.append(heapq.heappop(h))
            while h:                             # drain the last k elements in order
                res.append(heapq.heappop(h))
            return res

        print(*sort_k([9, 8, 7, 18, 19, 17], 2))
        print(*sort_k([10, 9, 8, 7, 4, 70, 60, 50], 4))
    ''', cpp='''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<int> sortK(const vector<int>& arr, int k) {
            priority_queue<int, vector<int>, greater<int>> h;     // min-heap
            vector<int> res;
            for (int x : arr) {
                h.push(x);
                if ((int)h.size() > k) { res.push_back(h.top()); h.pop(); }   // k+1 inside → the minimum is final
            }
            while (!h.empty()) { res.push_back(h.top()); h.pop(); }           // drain the last k elements
            return res;
        }

        void print(const vector<int>& v) {
            for (int i = 0; i < (int)v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\\n";
        }

        int main() {
            print(sortK({9, 8, 7, 18, 19, 17}, 2));
            print(sortK({10, 9, 8, 7, 4, 70, 60, 50}, 4));
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.PriorityQueue;

        public class Main {
            static List<Integer> sortK(int[] arr, int k) {
                PriorityQueue<Integer> h = new PriorityQueue<>();     // min-heap
                List<Integer> res = new ArrayList<>();
                for (int x : arr) {
                    h.add(x);
                    if (h.size() > k) res.add(h.poll());              // k+1 inside → the minimum is final
                }
                while (!h.isEmpty()) res.add(h.poll());               // drain the last k elements
                return res;
            }

            static String join(List<Integer> xs) {
                StringBuilder sb = new StringBuilder();
                for (int x : xs) sb.append(x).append(' ');
                return sb.toString().trim();
            }

            public static void main(String[] args) {
                System.out.println(join(sortK(new int[]{9, 8, 7, 18, 19, 17}, 2)));
                System.out.println(join(sortK(new int[]{10, 9, 8, 7, 4, 70, 60, 50}, 4)));
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        function sortK(arr, k) {
            const h = new Heap(), res = [];                        // min-heap
            for (const x of arr) {
                h.push(x);
                if (h.size() > k) res.push(h.pop());               // k+1 inside → the minimum is final
            }
            while (h.size()) res.push(h.pop());                    // drain the last k elements
            return res;
        }

        console.log(sortK([9, 8, 7, 18, 19, 17], 2).join(" "));
        console.log(sortK([10, 9, 8, 7, 4, 70, 60, 50], 4).join(" "));
    ''')
    yield complexity("O(n log k)", "O(k)")
    yield pitfall("The heap must hold `k + 1` elements before you trust its minimum, not `k`: with `k = 2` and `[9, 8, 7, …]`, the `7` is only pushed as the third element. Popping after `k` pushes would emit `8` first. When `k >= n` the method degenerates to heap sort — still correct, just `O(n log n)`.")

    yield section("Purchase maximum items with a budget", "coin")
    yield io("cost = [1, 12, 5, 111, 200], budget = 10", "2  (buy 1 and 5)", "cost = [20, 10, 5, 30, 100], budget = 35", "3  (buy 5, 10 and 20)")
    yield idea("Greedy: always buy the cheapest remaining item — a more expensive one can never let you afford *more* items. Sorting gives the cheapest items in order in `O(n log n)`:")
    yield snippet("py", '''
        def max_items_sorted(cost, budget):
            count = 0
            for c in sorted(cost):            # cheapest first
                if c > budget:
                    break
                budget -= c
                count += 1
            return count

        print(max_items_sorted([1, 12, 5, 111, 200], 10))
        print(max_items_sorted([20, 10, 5, 30, 100], 35))
    ''', out='''
        2
        3
    ''')
    yield complexity("O(n log n)", "O(1) extra (in-place sort)")
    yield p("But you usually stop long before the end — the budget runs out after `r` items. A min-heap built in `O(n)` and popped `r` times costs `O(n + r log n)`, which beats a sort when `r` is small (a tight budget, a huge catalogue).")
    yield multi('''
        2
        3
    ''', py='''
        import heapq

        def max_items(cost, budget):
            h = list(cost)
            heapq.heapify(h)                     # O(n) — cheaper than sorting everything
            count = 0
            while h and h[0] <= budget:          # cheapest remaining item is affordable
                budget -= heapq.heappop(h)
                count += 1
            return count

        print(max_items([1, 12, 5, 111, 200], 10))
        print(max_items([20, 10, 5, 30, 100], 35))
    ''', cpp='''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        int maxItems(const vector<int>& cost, int budget) {
            priority_queue<int, vector<int>, greater<int>> h(cost.begin(), cost.end());   // O(n) heapify
            int count = 0;
            while (!h.empty() && h.top() <= budget) {    // cheapest remaining item is affordable
                budget -= h.top();
                h.pop();
                count++;
            }
            return count;
        }

        int main() {
            cout << maxItems({1, 12, 5, 111, 200}, 10) << "\\n";
            cout << maxItems({20, 10, 5, 30, 100}, 35) << "\\n";
        }
    ''', java='''
        import java.util.PriorityQueue;

        public class Main {
            static int maxItems(int[] cost, int budget) {
                PriorityQueue<Integer> h = new PriorityQueue<>();
                for (int c : cost) h.add(c);                 // n pushes: O(n log n); a Collection ctor heapifies in O(n)
                int count = 0;
                while (!h.isEmpty() && h.peek() <= budget) { // cheapest remaining item is affordable
                    budget -= h.poll();
                    count++;
                }
                return count;
            }

            public static void main(String[] args) {
                System.out.println(maxItems(new int[]{1, 12, 5, 111, 200}, 10));
                System.out.println(maxItems(new int[]{20, 10, 5, 30, 100}, 35));
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        function maxItems(cost, budget) {
            const h = new Heap();                            // min-heap
            for (const c of cost) h.push(c);
            let count = 0;
            while (h.size() && h.peek() <= budget) {         // cheapest remaining item is affordable
                budget -= h.pop();
                count++;
            }
            return count;
        }

        console.log(maxItems([1, 12, 5, 111, 200], 10));
        console.log(maxItems([20, 10, 5, 30, 100], 35));
    ''')
    yield complexity("O(n + r log n)", "O(n)")
    yield note("The original notes' heap version had two bugs: it iterated `for i in cost` while popping from the *same* list (`pq = cost` aliases, it does not copy), and the driver called the sorting function instead. Copy the list before `heapify`, and loop on the heap's top, not on an index.")

    yield section("K largest elements", "sort-descending")
    yield io("arr = [5, 15, 10, 20, 8], k = 2", "15 20", "arr = [3, 9, 1, 7, 5, 8], k = 3", "7 8 9")
    yield idea("Keep a **min-heap of size k** holding the `k` largest elements seen so far. Its root is the smallest of those `k` — the *threshold*. A new element that is not above the threshold can never be in the answer; one that is replaces the root. The heap is tiny, so each step is `O(log k)`.")
    yield steps(
        ("Build", "Put the first `k` elements into a min-heap."),
        ("Scan the rest", "If `x <= heap.top()` ignore it; otherwise pop the top and push `x`."),
        ("Collect", "The heap now holds exactly the `k` largest. Pop them for ascending order."),
    )
    yield multi('''
        15 20
        7 8 9
    ''', py='''
        import heapq

        def k_largest(arr, k):
            h = arr[:k]
            heapq.heapify(h)                      # min-heap of the k largest seen so far
            for x in arr[k:]:
                if x > h[0]:                      # bigger than the current threshold
                    heapq.heapreplace(h, x)       # pop the root and push x in one sift
            return sorted(h)

        print(*k_largest([5, 15, 10, 20, 8], 2))
        print(*k_largest([3, 9, 1, 7, 5, 8], 3))
    ''', cpp='''
        #include <algorithm>
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<int> kLargest(const vector<int>& arr, int k) {
            priority_queue<int, vector<int>, greater<int>> h;     // min-heap of the k largest seen so far
            int n = arr.size();
            for (int i = 0; i < n; i++) {
                if (i < k) h.push(arr[i]);
                else if (arr[i] > h.top()) { h.pop(); h.push(arr[i]); }   // beats the threshold
            }
            vector<int> res;
            while (!h.empty()) { res.push_back(h.top()); h.pop(); }       // popped in ascending order
            return res;
        }

        void print(const vector<int>& v) {
            for (int i = 0; i < (int)v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\\n";
        }

        int main() {
            print(kLargest({5, 15, 10, 20, 8}, 2));
            print(kLargest({3, 9, 1, 7, 5, 8}, 3));
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.PriorityQueue;

        public class Main {
            static List<Integer> kLargest(int[] arr, int k) {
                PriorityQueue<Integer> h = new PriorityQueue<>();     // min-heap of the k largest seen so far
                for (int i = 0; i < arr.length; i++) {
                    if (i < k) h.add(arr[i]);
                    else if (arr[i] > h.peek()) { h.poll(); h.add(arr[i]); }   // beats the threshold
                }
                List<Integer> res = new ArrayList<>();
                while (!h.isEmpty()) res.add(h.poll());               // polled in ascending order
                return res;
            }

            static String join(List<Integer> xs) {
                StringBuilder sb = new StringBuilder();
                for (int x : xs) sb.append(x).append(' ');
                return sb.toString().trim();
            }

            public static void main(String[] args) {
                System.out.println(join(kLargest(new int[]{5, 15, 10, 20, 8}, 2)));
                System.out.println(join(kLargest(new int[]{3, 9, 1, 7, 5, 8}, 3)));
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        function kLargest(arr, k) {
            const h = new Heap();                                  // min-heap of the k largest seen so far
            for (let i = 0; i < arr.length; i++) {
                if (i < k) h.push(arr[i]);
                else if (arr[i] > h.peek()) { h.pop(); h.push(arr[i]); }   // beats the threshold
            }
            const res = [];
            while (h.size()) res.push(h.pop());                    // popped in ascending order
            return res;
        }

        console.log(kLargest([5, 15, 10, 20, 8], 2).join(" "));
        console.log(kLargest([3, 9, 1, 7, 5, 8], 3).join(" "));
    ''')
    yield complexity("O(n log k)", "O(k)")
    yield p("The alternative is a max-heap of **all** `n` elements, popped `k` times. It is simpler and gives the results largest-first, but it needs `O(n)` memory and cannot process a stream:")
    yield snippet("py", '''
        import heapq

        def k_largest_maxheap(arr, k):
            h = [-x for x in arr]                   # max-heap via negation
            heapq.heapify(h)                        # O(n)
            return [-heapq.heappop(h) for _ in range(k)]   # k pops, O(k log n)

        print(*k_largest_maxheap([5, 15, 10, 20, 8], 2))
    ''', out="20 15")
    yield table(
        ["Approach", "Time", "Space", "Works on a stream?"],
        ["sort, take the last `k`", "O(n log n)", "O(1)", "no"],
        ["max-heap of all, pop `k`", "O(n + k log n)", "O(n)", "no"],
        ["**min-heap of size `k`**", "O(n log k)", "O(k)", "yes — the heap is the running answer"],
        ["quickselect", "O(n) average", "O(1)", "no (unordered result)"],
    )
    yield pitfall("Use a **min**-heap for the k *largest* and a **max**-heap for the k *smallest*. The heap type is the opposite of what you are looking for, because the root must be the element you are willing to throw away.")

    yield section("K closest elements to x", "target")
    yield io("arr = [10, 15, 7, 3, 4], x = 8, k = 2", "7 10", "arr = [5, 15, 10, 20, 8], x = 12, k = 3", "8 10 15")
    yield p("Pick the `k` elements with the smallest `|arr[i] - x|`. The naive approach finds the closest element, removes it and repeats `k` times:")
    yield snippet("py", '''
        def k_closest_naive(arr, x, k):
            arr = list(arr)
            res = []
            for _ in range(k):                                     # k passes …
                mi = 0
                for j in range(1, len(arr)):                       # … each scanning the whole array
                    if abs(arr[j] - x) < abs(arr[mi] - x):
                        mi = j
                res.append(arr.pop(mi))
            return sorted(res)

        print(*k_closest_naive([10, 15, 7, 3, 4], 8, 2))
    ''', out="7 10")
    yield complexity("O(n · k)", "O(k)")
    yield idea("This is *k smallest* with the key `|arr[i] - x|`, so flip the previous recipe: a **max-heap of size k** keyed on the distance. The root is the farthest of the current best `k`; a new element closer than it replaces it. Store `(distance, value)` pairs so the heap orders by distance but you can still print the value.")
    yield multi('''
        7 10
        8 10 15
    ''', py='''
        import heapq

        def k_closest(arr, x, k):
            h = []                                        # max-heap on distance: push (-dist, -value)
            for v in arr:
                heapq.heappush(h, (-abs(v - x), -v))
                if len(h) > k:
                    heapq.heappop(h)                      # drop the farthest (on ties: the larger value)
            return sorted(-v for _, v in h)

        print(*k_closest([10, 15, 7, 3, 4], 8, 2))
        print(*k_closest([5, 15, 10, 20, 8], 12, 3))
    ''', cpp='''
        #include <algorithm>
        #include <cstdlib>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<int> kClosest(const vector<int>& arr, int x, int k) {
            priority_queue<pair<int, int>> h;             // max-heap on (distance, value)
            for (int v : arr) {
                h.push({abs(v - x), v});
                if ((int)h.size() > k) h.pop();           // drop the farthest (on ties: the larger value)
            }
            vector<int> res;
            while (!h.empty()) { res.push_back(h.top().second); h.pop(); }
            sort(res.begin(), res.end());
            return res;
        }

        void print(const vector<int>& v) {
            for (int i = 0; i < (int)v.size(); i++) cout << (i ? " " : "") << v[i];
            cout << "\\n";
        }

        int main() {
            print(kClosest({10, 15, 7, 3, 4}, 8, 2));
            print(kClosest({5, 15, 10, 20, 8}, 12, 3));
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.Collections;
        import java.util.List;
        import java.util.PriorityQueue;

        public class Main {
            static List<Integer> kClosest(int[] arr, int x, int k) {
                // max-heap on distance, then on value: int[]{distance, value}
                PriorityQueue<int[]> h = new PriorityQueue<>(
                    (a, b) -> a[0] != b[0] ? Integer.compare(b[0], a[0]) : Integer.compare(b[1], a[1]));
                for (int v : arr) {
                    h.add(new int[]{Math.abs(v - x), v});
                    if (h.size() > k) h.poll();                   // drop the farthest (on ties: the larger value)
                }
                List<Integer> res = new ArrayList<>();
                while (!h.isEmpty()) res.add(h.poll()[1]);
                Collections.sort(res);
                return res;
            }

            static String join(List<Integer> xs) {
                StringBuilder sb = new StringBuilder();
                for (int v : xs) sb.append(v).append(' ');
                return sb.toString().trim();
            }

            public static void main(String[] args) {
                System.out.println(join(kClosest(new int[]{10, 15, 7, 3, 4}, 8, 2)));
                System.out.println(join(kClosest(new int[]{5, 15, 10, 20, 8}, 12, 3)));
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        function kClosest(arr, x, k) {
            // max-heap on distance, then on value: [distance, value]
            const h = new Heap((a, b) => a[0] !== b[0] ? b[0] - a[0] : b[1] - a[1]);
            for (const v of arr) {
                h.push([Math.abs(v - x), v]);
                if (h.size() > k) h.pop();                         // drop the farthest (on ties: the larger value)
            }
            const res = [];
            while (h.size()) res.push(h.pop()[1]);
            return res.sort((a, b) => a - b);
        }

        console.log(kClosest([10, 15, 7, 3, 4], 8, 2).join(" "));
        console.log(kClosest([5, 15, 10, 20, 8], 12, 3).join(" "));
    ''')
    yield complexity("O(n log k)", "O(k)")
    yield note("Ties matter: two elements at the same distance (`7` and `9` for `x = 8`) — decide which one wins *before* coding and encode it in the comparator (here: on equal distance the larger value is dropped, so the smaller one is kept). Python's tuple ordering, C++'s `pair` ordering and the explicit Java/JavaScript comparators all implement that same rule. If the array is **sorted**, a two-pointer window or binary search solves it in `O(log n + k)` with no heap at all.")

    yield section("Merge k sorted arrays", "git-merge")
    yield io("arrays = [[10, 20, 30], [5, 15], [1, 9, 11, 18]]", "1 5 9 10 11 15 18 20 30")
    yield p("`N` is the total number of elements, `k` the number of arrays. Two obvious approaches ignore the fact that the inputs are already sorted:")
    yield snippet("py", '''
        # 1. concatenate everything and sort: O(N log N) — ignores the existing order
        def merge_k_sort(arrays):
            res = []
            for a in arrays:
                res.extend(a)
            return sorted(res)

        # 2. merge the arrays one by one into the result: O(N · k) — the result is re-merged k times
        def merge_two(a, b):
            res, i, j = [], 0, 0
            while i < len(a) and j < len(b):
                if a[i] < b[j]:
                    res.append(a[i]); i += 1
                else:
                    res.append(b[j]); j += 1
            return res + a[i:] + b[j:]

        def merge_k_pairwise(arrays):
            res = list(arrays[0])
            for a in arrays[1:]:
                res = merge_two(res, a)
            return res

        arrays = [[10, 20, 30], [5, 15], [1, 9, 11, 18]]
        print(*merge_k_sort(arrays))
        print(*merge_k_pairwise(arrays))
    ''', out='''
        1 5 9 10 11 15 18 20 30
        1 5 9 10 11 15 18 20 30
    ''')
    yield idea("At any moment the next output is the smallest among the **heads** of the `k` arrays. Keep those `k` heads in a min-heap as `(value, array index, element index)`. Pop the minimum, append it, and push the next element of the same array. Each of the `N` elements enters and leaves a heap of size `<= k` once.")
    yield diagram('''
        heap of heads          output so far
        {10, 5, 1}       pop 1  → push 9       1
        {10, 5, 9}       pop 5  → push 15      1 5
        {10, 15, 9}      pop 9  → push 11      1 5 9
        {10, 15, 11}     pop 10 → push 20      1 5 9 10
        {20, 15, 11}     pop 11 → push 18      1 5 9 10 11
        ...
    ''', "The heap never holds more than one element per array")
    yield multi('''
        1 5 9 10 11 15 18 20 30
    ''', py='''
        import heapq

        def merge_k(arrays):
            h = [(a[0], i, 0) for i, a in enumerate(arrays) if a]   # (value, which array, index in it)
            heapq.heapify(h)
            res = []
            while h:
                val, ai, j = heapq.heappop(h)
                res.append(val)
                if j + 1 < len(arrays[ai]):                          # the same array has more
                    heapq.heappush(h, (arrays[ai][j + 1], ai, j + 1))
            return res

        print(*merge_k([[10, 20, 30], [5, 15], [1, 9, 11, 18]]))
    ''', cpp='''
        #include <array>
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<int> mergeK(const vector<vector<int>>& arrays) {
            using Item = array<int, 3>;                              // {value, which array, index in it}
            priority_queue<Item, vector<Item>, greater<Item>> h;     // min-heap, compares lexicographically
            int k = arrays.size();
            for (int i = 0; i < k; i++)
                if (!arrays[i].empty()) h.push({arrays[i][0], i, 0});
            vector<int> res;
            while (!h.empty()) {
                Item it = h.top(); h.pop();
                int val = it[0], ai = it[1], j = it[2];
                res.push_back(val);
                if (j + 1 < (int)arrays[ai].size())                  // the same array has more
                    h.push({arrays[ai][j + 1], ai, j + 1});
            }
            return res;
        }

        int main() {
            vector<int> res = mergeK({{10, 20, 30}, {5, 15}, {1, 9, 11, 18}});
            for (int i = 0; i < (int)res.size(); i++) cout << (i ? " " : "") << res[i];
            cout << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.List;
        import java.util.PriorityQueue;

        public class Main {
            static List<Integer> mergeK(int[][] arrays) {
                // int[]{value, which array, index in it}, ordered by value
                PriorityQueue<int[]> h = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
                for (int i = 0; i < arrays.length; i++)
                    if (arrays[i].length > 0) h.add(new int[]{arrays[i][0], i, 0});
                List<Integer> res = new ArrayList<>();
                while (!h.isEmpty()) {
                    int[] it = h.poll();
                    int val = it[0], ai = it[1], j = it[2];
                    res.add(val);
                    if (j + 1 < arrays[ai].length)                   // the same array has more
                        h.add(new int[]{arrays[ai][j + 1], ai, j + 1});
                }
                return res;
            }

            public static void main(String[] args) {
                List<Integer> res = mergeK(new int[][]{{10, 20, 30}, {5, 15}, {1, 9, 11, 18}});
                StringBuilder sb = new StringBuilder();
                for (int v : res) sb.append(v).append(' ');
                System.out.println(sb.toString().trim());
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        function mergeK(arrays) {
            const h = new Heap((a, b) => a[0] - b[0]);               // [value, which array, index in it]
            arrays.forEach((a, i) => { if (a.length) h.push([a[0], i, 0]); });
            const res = [];
            while (h.size()) {
                const [val, ai, j] = h.pop();
                res.push(val);
                if (j + 1 < arrays[ai].length)                       // the same array has more
                    h.push([arrays[ai][j + 1], ai, j + 1]);
            }
            return res;
        }

        console.log(mergeK([[10, 20, 30], [5, 15], [1, 9, 11, 18]]).join(" "));
    ''')
    yield complexity("O(N log k)", "O(k) for the heap, plus the output")
    yield table(
        ["Approach", "Time", "Why"],
        ["concatenate + sort", "O(N log N)", "throws away the input order"],
        ["merge one array at a time", "O(N · k)", "the growing result is re-merged `k - 1` times"],
        ["**min-heap of `k` heads**", "O(N log k)", "every element passes once through a heap of size `k`"],
        ["divide and conquer (merge pairs)", "O(N log k)", "same bound, no heap, more copying"],
    )
    yield pitfall("Push the **array index and position**, not just the value — otherwise you cannot tell which array to advance. Pushing the whole remaining array into the heap instead of one head makes it `O(N log N)` again. The same heap-of-heads pattern merges `k` sorted linked lists, `k` sorted files on disk (external sorting) and `k` sorted streams.")

    yield section("Median of a stream", "chart-line")
    yield io("stream = [25, 7, 10, 15, 20]", "25.0 16.0 10.0 12.5 15.0")
    yield p("After each new number, report the median of everything seen so far. A median needs the *middle* of the data, not its minimum — the trick is to split the data in two halves.")
    yield table(
        ["Numbers so far", "Sorted", "Median"],
        ["`25`", "25", "25.0"],
        ["`25 7`", "7 25", "(7 + 25) / 2 = 16.0"],
        ["`25 7 10`", "7 10 25", "10.0"],
        ["`25 7 10 15`", "7 10 15 25", "(10 + 15) / 2 = 12.5"],
        ["`25 7 10 15 20`", "7 10 15 20 25", "15.0"],
    )
    yield p("Re-sorting after every arrival works but costs `O(n log n)` per element (or `O(n)` with insertion into a sorted list):")
    yield snippet("py", '''
        def medians_naive(stream):
            seen, out = [], []
            for x in stream:
                seen.append(x)
                seen.sort()                                   # O(n log n) every time
                n = len(seen)
                m = seen[n // 2] if n % 2 else (seen[n // 2 - 1] + seen[n // 2]) / 2
                out.append(f"{m:.1f}")
            return out

        print(*medians_naive([25, 7, 10, 15, 20]))
    ''', out="25.0 16.0 10.0 12.5 15.0")
    yield complexity("O(n² log n) total", "O(n)")
    yield idea("**Two heaps.** Keep the smaller half in a **max-heap** `small` and the larger half in a **min-heap** `large`, with `|small| - |large|` kept at `0` or `1`. The median is then `small.top()` (odd count) or the average of the two tops (even count). Every insertion is two or three heap operations.")
    yield steps(
        ("Push `x` into `small`", "The max-heap of the lower half."),
        ("Move `small.top()` to `large`", "Guarantees every element of `small` is `<=` every element of `large`, even if `x` was big."),
        ("Rebalance", "If `large` has more elements than `small`, move `large.top()` back. Now `|small| = |large|` or `|small| = |large| + 1`."),
        ("Read the median", "`small.top()` when `small` is bigger, else `(small.top() + large.top()) / 2`."),
    )
    yield diagram('''
        x = 20 arrives (seen: 25 7 10 15)
          small (max-heap) = {10, 7}     large (min-heap) = {15, 25}

        1. small.push(20)        small = {20, 10, 7}   large = {15, 25}
        2. large.push(small.pop) small = {10, 7}       large = {15, 20, 25}   ← 20 belongs in the upper half
        3. |large| > |small|     small = {15, 10, 7}   large = {20, 25}       ← move 15 back
        4. |small| > |large|     median = small.top() = 15
    ''', "One insertion into the two-heap structure")
    yield multi('''
        25.0 16.0 10.0 12.5 15.0
    ''', py='''
        import heapq

        def running_medians(stream):
            small, large = [], []                   # small: max-heap via negation; large: min-heap
            out = []
            for x in stream:
                heapq.heappush(small, -x)
                heapq.heappush(large, -heapq.heappop(small))      # largest of small moves up
                if len(large) > len(small):
                    heapq.heappush(small, -heapq.heappop(large))  # rebalance: small keeps the extra one
                if len(small) > len(large):
                    out.append(f"{-small[0]:.1f}")
                else:
                    out.append(f"{(-small[0] + large[0]) / 2:.1f}")
            return out

        print(*running_medians([25, 7, 10, 15, 20]))
    ''', cpp='''
        #include <functional>
        #include <iomanip>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        int main() {
            vector<int> stream = {25, 7, 10, 15, 20};
            priority_queue<int> small;                                 // max-heap: lower half
            priority_queue<int, vector<int>, greater<int>> large;      // min-heap: upper half
            cout << fixed << setprecision(1);
            bool firstOut = true;
            for (int x : stream) {
                small.push(x);
                large.push(small.top()); small.pop();                  // largest of small moves up
                if (large.size() > small.size()) { small.push(large.top()); large.pop(); }   // rebalance
                double median = small.size() > large.size() ? small.top() : (small.top() + large.top()) / 2.0;
                cout << (firstOut ? "" : " ") << median;
                firstOut = false;
            }
            cout << "\\n";
        }
    ''', java='''
        import java.util.Collections;
        import java.util.Locale;
        import java.util.PriorityQueue;

        public class Main {
            public static void main(String[] args) {
                int[] stream = {25, 7, 10, 15, 20};
                PriorityQueue<Integer> small = new PriorityQueue<>(Collections.reverseOrder());   // max-heap: lower half
                PriorityQueue<Integer> large = new PriorityQueue<>();                             // min-heap: upper half
                StringBuilder sb = new StringBuilder();
                for (int x : stream) {
                    small.add(x);
                    large.add(small.poll());                                   // largest of small moves up
                    if (large.size() > small.size()) small.add(large.poll());  // rebalance
                    double median = small.size() > large.size() ? small.peek() : (small.peek() + large.peek()) / 2.0;
                    sb.append(String.format(Locale.ROOT, "%.1f", median)).append(' ');
                }
                System.out.println(sb.toString().trim());
            }
        }
    ''', js='''
        class Heap {
            constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (this.cmp(a[i], a[p]) >= 0) break;
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }
            pop() {
                const a = this.a, top = a[0], last = a.pop();
                if (a.length) {
                    a[0] = last;
                    let i = 0;
                    for (;;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
                        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
                        if (m === i) break;
                        [a[i], a[m]] = [a[m], a[i]];
                        i = m;
                    }
                }
                return top;
            }
        }

        function runningMedians(stream) {
            const small = new Heap((a, b) => b - a);                  // max-heap: lower half
            const large = new Heap((a, b) => a - b);                  // min-heap: upper half
            const out = [];
            for (const x of stream) {
                small.push(x);
                large.push(small.pop());                              // largest of small moves up
                if (large.size() > small.size()) small.push(large.pop());   // rebalance
                const median = small.size() > large.size() ? small.peek() : (small.peek() + large.peek()) / 2;
                out.push(median.toFixed(1));
            }
            return out;
        }

        console.log(runningMedians([25, 7, 10, 15, 20]).join(" "));
    ''')
    yield complexity("O(log n) per element", "O(n)")
    yield note("An **augmented BST** (each node storing its subtree size, as in the BST topic) also works: insert in `O(h)`, then find the `n/2`-th and `n/2 + 1`-th smallest in `O(h)`. It additionally supports deleting elements (a *sliding-window* median), which the two heaps cannot do cheaply. For a pure stream the two heaps are simpler and faster.")
    yield pitfall("Pushing `x` straight into whichever heap *looks* right (`x < small.top()` → `small`) and only then rebalancing is also correct, but it has more branches and an empty-heap edge case. The push-then-move routine above has no special cases. And compute the average in floating point (`/ 2.0`): integer division would print `12` for `12.5`.")

    yield section("Choosing the heap", "adjustments")
    yield table(
        ["Problem", "Heap type", "Heap size", "Time"],
        ["k largest / k-th largest", "min-heap", "`k`", "O(n log k)"],
        ["k smallest / k closest", "max-heap (on the key)", "`k`", "O(n log k)"],
        ["sort a k-sorted array", "min-heap", "`k + 1`", "O(n log k)"],
        ["merge k sorted arrays", "min-heap of heads", "`k`", "O(N log k)"],
        ["buy cheapest first / schedule by priority", "min-heap of everything", "`n`", "O(n + r log n)"],
        ["running median", "max-heap + min-heap", "`n/2` each", "O(log n) per element"],
    )
    yield good("Ask two questions for every heap problem: *what key does the heap order by* (value, distance, array head) and *how large may it grow* (`k`, `k + 1`, `n`). The root is always the element you are prepared to discard.")

    yield section("Interview Q&A", "message-question")
    yield qa("Why is building a heap O(n) when n inserts cost O(n log n)?",
             "`heapify` sifts **down** from the last internal node to the root. Most nodes are near the bottom and sift only a step or two; summing `height × nodes-at-that-height` over the tree gives `O(n)`. Pushing one at a time sifts **up** from the bottom, where most nodes have `log n` ancestors — `O(n log n)`.")
    yield qa("Why a min-heap for the k largest elements?",
             "The heap holds the current best `k` and its root is the smallest of them — the only one that can be evicted. A new element either fails to beat that root (ignore it) or replaces it. With a max-heap the root is the best element, which you would never want to evict, so you would have to keep all `n` elements.")
    yield qa("Heap or balanced BST for a running median?",
             "Two heaps: `O(log n)` per element and only the two tops are ever read. A balanced BST augmented with subtree sizes also gives `O(log n)` and can additionally delete elements (sliding-window median) and answer any order statistic, at the price of a far bigger implementation — Python and JavaScript have no built-in ordered set to lean on.")
    yield qa("How do you get a max-heap in Python, and what is the catch?",
             "`heapq` only implements a min-heap, so push `-x` and negate when popping; for records push `(-key, item)` tuples. The catch is forgetting the negation on the way out, and for tuples that ties on the key fall through to comparing the payload — make the payload comparable (an index) or wrap it.")
    yield qa("Does a priority queue preserve insertion order for equal priorities?",
             "No — binary heaps are not stable. If FIFO order among equal priorities matters, store a sequence number as a secondary key: `(priority, seq, item)`. The same trick breaks ties deterministically in the k-closest problem.")
    yield qa("What are the time bounds of the heap operations and why is search O(n)?",
             "`peek` is `O(1)`, `push` and `pop` are `O(log n)` (one root-to-leaf path), `heapify` is `O(n)`. A heap only orders parent against children, so an arbitrary key can be anywhere below the root; finding or deleting it needs a linear scan, or an auxiliary index map (the *indexed heap* used by Dijkstra's decrease-key).")
