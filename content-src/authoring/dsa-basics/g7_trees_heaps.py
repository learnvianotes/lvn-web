from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Trees & Heaps"

# ── the sample binary tree from the notes, built identically in every language ───────────────────
# Every program in the `trees` topic starts with one of these preludes so the reader sees the same
# tree (10 / 20 30 / 40 50 60 / 70 80) in every example and every output.

PY_TREE = '''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def sample_tree():                   # the tree from the notes
            root = Node(10)
            root.left = Node(20)
            root.right = Node(30)
            root.left.left = Node(40)
            root.left.right = Node(50)
            root.right.right = Node(60)
            root.left.right.left = Node(70)
            root.left.right.right = Node(80)
            return root
'''

CPP_TREE = '''
        #include <iostream>
        using namespace std;

        struct Node {
            int key;
            Node *left, *right;
            Node(int k) : key(k), left(nullptr), right(nullptr) {}
        };

        Node* sampleTree() {                 // the tree from the notes
            Node* root = new Node(10);
            root->left = new Node(20);
            root->right = new Node(30);
            root->left->left = new Node(40);
            root->left->right = new Node(50);
            root->right->right = new Node(60);
            root->left->right->left = new Node(70);
            root->left->right->right = new Node(80);
            return root;
        }
'''

JAVA_TREE = '''
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node sampleTree() {           // the tree from the notes
                Node root = new Node(10);
                root.left = new Node(20);
                root.right = new Node(30);
                root.left.left = new Node(40);
                root.left.right = new Node(50);
                root.right.right = new Node(60);
                root.left.right.left = new Node(70);
                root.left.right.right = new Node(80);
                return root;
            }
'''

JS_TREE = '''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function sampleTree() {              // the tree from the notes
            const root = new Node(10);
            root.left = new Node(20);
            root.right = new Node(30);
            root.left.left = new Node(40);
            root.left.right = new Node(50);
            root.right.right = new Node(60);
            root.left.right.left = new Node(70);
            root.left.right.right = new Node(80);
            return root;
        }
'''


@topic(G, "trees", "Tree Data Structures", "binary-tree")
def _():
    yield lead("A tree is a **non-linear**, hierarchical data structure: one root node with children, each of which is the root of a smaller tree. Folders, HTML documents, organisation charts, expression parsers, database indexes and every search tree and heap are trees — and most tree algorithms are five-line recursions once you see the structure.")
    yield define("Tree", "a collection of nodes connected by edges such that there is exactly one *root* and every other node has exactly one parent — so there are no cycles and `n` nodes always have `n − 1` edges. A **binary tree** is a tree in which every node has at most two children, called `left` and `right`.")
    yield diagram('''
                         10                  ← root (depth 0, level 0)
                       /    \\
                     20      30              ← depth 1
                    /  \\       \\
                  40    50      60           ← depth 2
                       /  \\
                     70    80                ← depth 3 — 40, 70, 80, 60 are the leaves
    ''', "The sample binary tree used in every example below")

    yield section("Terminology", "vocabulary")
    yield table(
        ["Term", "Meaning", "In the sample tree"],
        ["**Node**", "One element: a key plus links to its children", "`10`, `20`, … (8 nodes)"],
        ["**Edge**", "The link from a parent to a child; a tree of `n` nodes has `n − 1` edges", "7 edges"],
        ["**Root**", "The topmost node — the only node without a parent", "`10`"],
        ["**Parent / child**", "The node directly above / directly below along an edge", "`50` is the parent of `70` and `80`"],
        ["**Siblings**", "Children of the same parent", "`70` and `80`; `20` and `30`"],
        ["**Leaf** (external node)", "A node with no children", "`40`, `70`, `80`, `60`"],
        ["**Internal node**", "A node with at least one child", "`10`, `20`, `30`, `50`"],
        ["**Subtree**", "A node together with all its descendants — itself a tree", "the subtree rooted at `20` is `20, 40, 50, 70, 80`"],
        ["**Ancestors**", "All nodes on the path from a node up to the root", "ancestors of `70`: `50`, `20`, `10`"],
        ["**Descendants**", "All nodes in a node's subtree except itself", "descendants of `20`: `40`, `50`, `70`, `80`"],
        ["**Degree** of a node", "Number of children (at most 2 in a binary tree)", "degree of `20` is 2, of `30` is 1, of `40` is 0"],
        ["**Depth** of a node", "Number of edges from the root down to the node", "depth of `70` is 3, of the root is 0"],
        ["**Level**", "All nodes at the same depth (`level 0` = root)", "level 2 is `40 50 60`"],
        ["**Height** of a node", "Number of edges on the longest downward path to a leaf (a leaf has height 0)", "height of `20` is 2"],
        ["**Height** of the tree", "Height of the root", "3 edges — or 4 if you count **nodes** on that path (the convention of these notes)"],
    )
    yield note("Two height conventions exist. Counting **edges**, the sample tree has height 3 and an empty tree has height −1. Counting **nodes** on the longest root-to-leaf path (what the notes and GeeksforGeeks do, and what the `height()` code below returns), it has height 4 and an empty tree has height 0. Interviewers accept either — just say which one you use.")

    yield section("Where trees are used", "apps")
    yield p("Trees are the natural representation of anything **hierarchical**, and the basis of most fast search structures.")
    yield cards(
        ("Hierarchical data", "Organisation structures, folder / file systems, XML and HTML documents (the DOM), nested JSON objects, class inheritance in OOP.", "sitemap"),
        ("Binary search tree", "Keys kept in sorted order with `O(log n)` search, insert and delete — `std::map`, `TreeMap` (next topic).", "hierarchy"),
        ("Binary heap", "A complete binary tree in an array; the priority queue behind heap sort, Dijkstra and schedulers (topic after next).", "triangle"),
        ("B and B+ trees", "Wide, shallow search trees that keep disk reads to a minimum — the indexes of every relational database.", "database"),
        ("Spanning and shortest-path trees", "Prim's and Kruskal's minimum spanning trees, Dijkstra's shortest-path tree — the backbone of routing in computer networks.", "topology-star"),
        ("Parse and expression trees", "Compilers turn source code into a syntax tree; `(a + b) * c` is a tree with `*` at the root.", "math-function"),
        cols=3,
    )
    yield p("**Special-purpose variations** you will meet later in DSA Advanced:")
    yield table(
        ["Variation", "What it is for"],
        ["**Trie** (prefix tree)", "Strings keyed character by character — autocomplete, spell check, IP routing tables"],
        ["**Suffix tree**", "All suffixes of a text — substring search in `O(m)`"],
        ["**Binary Indexed Tree** (Fenwick tree)", "Prefix sums with `O(log n)` point updates in a plain array"],
        ["**Segment tree**", "Range queries (sum, min, max) with `O(log n)` updates"],
    )

    yield section("Kinds of binary tree", "binary-tree")
    yield p("The same `n` keys can form very different binary trees. The shape decides the height, and the height decides how fast everything runs — so the special shapes have names.")
    yield diagram('''
          FULL (0 or 2 children)      COMPLETE (left-filled)      PERFECT (all leaves same level)
                   1                          1                            1
                 /   \\                      /   \\                        /   \\
                2     3                    2     3                      2     3
               / \\                        / \\   /                      / \\   / \\
              4   5                      4   5 6                      4   5 6   7

          BALANCED (|hL − hR| ≤ 1 at every node)      DEGENERATE / SKEWED (a linked list)
                   1                                      1
                 /   \\                                     \\
                2     3                                      2
               /       \\                                      \\
              4         5                                       3
                                                                 \\
                                                                  4
    ''', "The named shapes of a binary tree")
    yield table(
        ["Kind", "Rule", "Why it matters"],
        ["**Full** (strict / proper)", "Every node has either 0 or 2 children", "Leaves = internal nodes + 1; expression trees are full"],
        ["**Complete**", "Every level is completely filled except possibly the last, which is filled from **left to right**", "Can be stored in an array with no gaps — this is what a binary heap is"],
        ["**Perfect**", "All internal nodes have 2 children and all leaves are on the same level", "Exactly `2^h − 1` nodes for height `h` (in nodes); the densest possible tree"],
        ["**Balanced**", "Height is `O(log n)` — e.g. AVL: left and right heights differ by at most 1 at every node", "Guarantees `O(log n)` search, insert and delete in a BST"],
        ["**Degenerate** (skewed)", "Every node has exactly one child", "Height `n − 1`: it behaves like a linked list, every operation becomes `O(n)`"],
    )
    yield p("Useful facts (height counted in nodes): level `l` holds at most `2^l` nodes; a tree of height `h` holds at most `2^h − 1` nodes; therefore `n` nodes need height at least `⌈log₂(n + 1)⌉`. A perfect tree is always complete and full; a complete tree need not be full (node `3` above has one child); a full tree need not be complete.")

    yield section("Binary tree node and building the sample tree", "code")
    yield p("A binary tree is a **linked** data structure, like a linked list with two links. Each node stores a key and pointers to its left and right child; a missing child is `None` / `nullptr` / `null`. The tree is identified by its root pointer alone — there is no separate container object. Every program in this topic starts by building the sample tree with this node class.")
    yield multi('''
        root: 10
        children of root: 20 30
        left child of 20: 40
        right child of 30: 60
        30 has a left child: false
        70 is a leaf: true
    ''', py=PY_TREE + '''
        def is_leaf(node):
            return node.left is None and node.right is None

        root = sample_tree()
        print("root:", root.key)
        print("children of root:", root.left.key, root.right.key)
        print("left child of 20:", root.left.left.key)
        print("right child of 30:", root.right.right.key)
        print("30 has a left child:", "true" if root.right.left else "false")
        print("70 is a leaf:", "true" if is_leaf(root.left.right.left) else "false")
    ''', cpp=CPP_TREE + '''
        bool isLeaf(Node* node) { return !node->left && !node->right; }

        int main() {
            Node* root = sampleTree();
            cout << "root: " << root->key << "\\n";
            cout << "children of root: " << root->left->key << " " << root->right->key << "\\n";
            cout << "left child of 20: " << root->left->left->key << "\\n";
            cout << "right child of 30: " << root->right->right->key << "\\n";
            cout << "30 has a left child: " << (root->right->left ? "true" : "false") << "\\n";
            cout << "70 is a leaf: " << (isLeaf(root->left->right->left) ? "true" : "false") << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static boolean isLeaf(Node node) { return node.left == null && node.right == null; }

            public static void main(String[] args) {
                Node root = sampleTree();
                System.out.println("root: " + root.key);
                System.out.println("children of root: " + root.left.key + " " + root.right.key);
                System.out.println("left child of 20: " + root.left.left.key);
                System.out.println("right child of 30: " + root.right.right.key);
                System.out.println("30 has a left child: " + (root.right.left != null ? "true" : "false"));
                System.out.println("70 is a leaf: " + (isLeaf(root.left.right.left) ? "true" : "false"));
            }
        }
    ''', js=JS_TREE + '''
        const isLeaf = (node) => node.left === null && node.right === null;

        const root = sampleTree();
        console.log("root:", root.key);
        console.log("children of root:", root.left.key, root.right.key);
        console.log("left child of 20:", root.left.left.key);
        console.log("right child of 30:", root.right.right.key);
        console.log("30 has a left child:", root.right.left ? "true" : "false");
        console.log("70 is a leaf:", isLeaf(root.left.right.left) ? "true" : "false");
    ''')
    yield note("Building a tree by hand like this is fine for examples. Real code builds trees by **insertion** (a BST), from an array (a heap, or a level-order array with `-1` for missing nodes) or by parsing input.")

    yield section("Tree traversals", "route")
    yield p("Traversing means visiting every node exactly once. A list has one natural order; a tree has several, and each one is useful for something.")
    yield table(
        ["Traversal", "Order", "Sample tree gives", "Typical use"],
        ["**Inorder** (depth-first)", "Left subtree → **Root** → Right subtree", "`40 20 70 50 80 10 30 60`", "Sorted output of a binary search tree"],
        ["**Preorder** (depth-first)", "**Root** → Left → Right", "`10 20 40 50 70 80 30 60`", "Copying / serialising a tree, prefix expressions"],
        ["**Postorder** (depth-first)", "Left → Right → **Root**", "`40 70 80 50 20 60 30 10`", "Deleting a tree (children before parent), folder sizes, postfix expressions"],
        ["**Level order** (breadth-first)", "Level 0, then level 1, … left to right", "`10 20 30 40 50 60 70 80`", "Shortest paths, printing by level, anything that needs *closest first*"],
    )
    yield diagram('''
                   10            Inorder   : (left of 10) 10 (right of 10)
                 /    \\                     = (40 20 70 50 80) 10 (30 60)
               20      30
              /  \\       \\      Preorder  : 10 (left of 10) (right of 10)
            40    50      60                = 10 (20 40 50 70 80) (30 60)
                 /  \\
               70    80          Postorder : (left of 10) (right of 10) 10
                                            = (40 70 80 50 20) (60 30) 10
    ''', "The three depth-first orders differ only in when the root is visited relative to its subtrees")
    yield idea("All three depth-first traversals are the **same recursion** — `visit(root.left)`, `visit(root.right)` and *print the root* — in a different order. The names say where the root goes: **pre**-order before the children, **in**-order in between, **post**-order after. Each recursive call handles one node and makes two calls, so the total work is `O(n)`; the recursion stack is as deep as the tree, so auxiliary space is `O(h)`.")

    yield section("Inorder traversal", "arrow-bar-to-down")
    yield io("the sample tree", "40 20 70 50 80 10 30 60")
    yield p("Recurse into the left subtree, print the node, recurse into the right subtree. On a BST this prints the keys in sorted order, which is why inorder is the traversal you will use most.")
    yield multi('''
        40 20 70 50 80 10 30 60
    ''', py=PY_TREE + '''
        def inorder(root):
            if root is None:                 # base case: empty subtree
                return
            inorder(root.left)               # 1. left subtree
            print(root.key, end=" ")         # 2. root
            inorder(root.right)              # 3. right subtree

        inorder(sample_tree())
        print()
    ''', cpp=CPP_TREE + '''
        void inorder(Node* root) {
            if (!root) return;               // base case: empty subtree
            inorder(root->left);             // 1. left subtree
            cout << root->key << " ";        // 2. root
            inorder(root->right);            // 3. right subtree
        }

        int main() {
            inorder(sampleTree());
            cout << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static void inorder(Node root) {
                if (root == null) return;        // base case: empty subtree
                inorder(root.left);              // 1. left subtree
                System.out.print(root.key + " "); // 2. root
                inorder(root.right);             // 3. right subtree
            }

            public static void main(String[] args) {
                inorder(sampleTree());
                System.out.println();
            }
        }
    ''', js=JS_TREE + '''
        function inorder(root) {
            if (root === null) return;       // base case: empty subtree
            inorder(root.left);              // 1. left subtree
            process.stdout.write(root.key + " "); // 2. root
            inorder(root.right);             // 3. right subtree
        }

        inorder(sampleTree());
        console.log();
    ''')
    yield complexity("O(n)", "O(h) recursion stack — O(n) for a skewed tree, O(log n) when balanced")
    yield pitfall("The notes' comment *Auxiliary space Θ(n)* is the worst case only. The stack holds one frame per **ancestor** of the current node, so its depth is the height `h`; it reaches `n` only for a degenerate (linked-list-shaped) tree.")

    yield section("Preorder traversal", "arrow-bar-up")
    yield io("the sample tree", "10 20 40 50 70 80 30 60")
    yield p("Print the node first, then its subtrees. Preorder lists every node before its descendants, so writing a tree out in preorder (with markers for missing children) is enough to rebuild it — this is how trees are serialised and copied.")
    yield multi('''
        10 20 40 50 70 80 30 60
    ''', py=PY_TREE + '''
        def preorder(root):
            if root is None:
                return
            print(root.key, end=" ")         # 1. root first
            preorder(root.left)              # 2. left subtree
            preorder(root.right)             # 3. right subtree

        preorder(sample_tree())
        print()
    ''', cpp=CPP_TREE + '''
        void preorder(Node* root) {
            if (!root) return;
            cout << root->key << " ";        // 1. root first
            preorder(root->left);            // 2. left subtree
            preorder(root->right);           // 3. right subtree
        }

        int main() {
            preorder(sampleTree());
            cout << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static void preorder(Node root) {
                if (root == null) return;
                System.out.print(root.key + " "); // 1. root first
                preorder(root.left);             // 2. left subtree
                preorder(root.right);            // 3. right subtree
            }

            public static void main(String[] args) {
                preorder(sampleTree());
                System.out.println();
            }
        }
    ''', js=JS_TREE + '''
        function preorder(root) {
            if (root === null) return;
            process.stdout.write(root.key + " "); // 1. root first
            preorder(root.left);             // 2. left subtree
            preorder(root.right);            // 3. right subtree
        }

        preorder(sampleTree());
        console.log();
    ''')
    yield complexity("O(n)", "O(h)")

    yield section("Postorder traversal", "arrow-bar-down")
    yield io("the sample tree", "40 70 80 50 20 60 30 10")
    yield p("Both subtrees first, the node last. Postorder visits children before their parent, so it is the order for anything that must finish the parts before the whole: freeing a tree's nodes, computing directory sizes, evaluating an expression tree.")
    yield multi('''
        40 70 80 50 20 60 30 10
    ''', py=PY_TREE + '''
        def postorder(root):
            if root is None:
                return
            postorder(root.left)             # 1. left subtree
            postorder(root.right)            # 2. right subtree
            print(root.key, end=" ")         # 3. root last

        postorder(sample_tree())
        print()
    ''', cpp=CPP_TREE + '''
        void postorder(Node* root) {
            if (!root) return;
            postorder(root->left);           // 1. left subtree
            postorder(root->right);          // 2. right subtree
            cout << root->key << " ";        // 3. root last
        }

        int main() {
            postorder(sampleTree());
            cout << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static void postorder(Node root) {
                if (root == null) return;
                postorder(root.left);            // 1. left subtree
                postorder(root.right);           // 2. right subtree
                System.out.print(root.key + " "); // 3. root last
            }

            public static void main(String[] args) {
                postorder(sampleTree());
                System.out.println();
            }
        }
    ''', js=JS_TREE + '''
        function postorder(root) {
            if (root === null) return;
            postorder(root.left);            // 1. left subtree
            postorder(root.right);           // 2. right subtree
            process.stdout.write(root.key + " "); // 3. root last
        }

        postorder(sampleTree());
        console.log();
    ''')
    yield complexity("O(n)", "O(h)")
    yield note("In C++ the destructor of a tree *is* a postorder traversal: `delete` the left subtree, `delete` the right subtree, then the node — deleting the node first would lose the pointers to its children.")

    yield section("Height of a binary tree", "arrows-vertical")
    yield io("the sample tree", "4 (nodes on the longest root-to-leaf path 10 → 20 → 50 → 70)", "an empty tree", "0")
    yield idea("The height of a tree is **one more than the taller of its two subtrees**. That is the whole algorithm: recurse into both children, take the maximum, add 1. The base case — an empty subtree — has height 0 under the node-counting convention.")
    yield multi('''
        height: 4
        height of left subtree: 3
        height of right subtree: 2
    ''', py=PY_TREE + '''
        def height(root):
            if root is None:
                return 0                             # empty tree (node convention)
            return max(height(root.left), height(root.right)) + 1   # +1 for the root

        root = sample_tree()
        print("height:", height(root))
        print("height of left subtree:", height(root.left))
        print("height of right subtree:", height(root.right))
    ''', cpp=CPP_TREE + '''
        int height(Node* root) {
            if (!root) return 0;                     // empty tree (node convention)
            return max(height(root->left), height(root->right)) + 1;   // +1 for the root
        }

        int main() {
            Node* root = sampleTree();
            cout << "height: " << height(root) << "\\n";
            cout << "height of left subtree: " << height(root->left) << "\\n";
            cout << "height of right subtree: " << height(root->right) << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static int height(Node root) {
                if (root == null) return 0;              // empty tree (node convention)
                return Math.max(height(root.left), height(root.right)) + 1;   // +1 for the root
            }

            public static void main(String[] args) {
                Node root = sampleTree();
                System.out.println("height: " + height(root));
                System.out.println("height of left subtree: " + height(root.left));
                System.out.println("height of right subtree: " + height(root.right));
            }
        }
    ''', js=JS_TREE + '''
        function height(root) {
            if (root === null) return 0;             // empty tree (node convention)
            return Math.max(height(root.left), height(root.right)) + 1;   // +1 for the root
        }

        const root = sampleTree();
        console.log("height:", height(root));
        console.log("height of left subtree:", height(root.left));
        console.log("height of right subtree:", height(root.right));
    ''')
    yield complexity("O(n)", "O(h)")
    yield note("To count **edges** instead, return `-1` for an empty tree; the sample tree then has height 3. The `+ 1` stays the same.")

    yield section("Print nodes at distance K from the root", "arrows-horizontal")
    yield io("the sample tree, K = 2", "40 50 60", "K = 1", "20 30", "K = 3", "70 80")
    yield idea("A node is at distance `K` from the root exactly when it is at distance `K − 1` from one of the root's children. So pass `K` down the recursion, decrementing at each level; when it reaches 0, the current node is one of the answers. Nothing needs to come back up — the recursion just needs to reach depth `K`.")
    yield multi('''
        k = 0: 10
        k = 1: 20 30
        k = 2: 40 50 60
        k = 3: 70 80
    ''', py=PY_TREE + '''
        def print_k_distance(root, k):
            if root is None:
                return
            if k == 0:                           # reached distance K: this node is an answer
                print(root.key, end=" ")
            else:                                # both children are one step closer
                print_k_distance(root.left, k - 1)
                print_k_distance(root.right, k - 1)

        root = sample_tree()
        for k in range(4):
            print(f"k = {k}:", end=" ")
            print_k_distance(root, k)
            print()
    ''', cpp=CPP_TREE + '''
        void printKDistance(Node* root, int k) {
            if (!root) return;
            if (k == 0) {                            // reached distance K: this node is an answer
                cout << root->key << " ";
            } else {                                 // both children are one step closer
                printKDistance(root->left, k - 1);
                printKDistance(root->right, k - 1);
            }
        }

        int main() {
            Node* root = sampleTree();
            for (int k = 0; k < 4; k++) {
                cout << "k = " << k << ": ";
                printKDistance(root, k);
                cout << "\\n";
            }
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static void printKDistance(Node root, int k) {
                if (root == null) return;
                if (k == 0) {                            // reached distance K: this node is an answer
                    System.out.print(root.key + " ");
                } else {                                 // both children are one step closer
                    printKDistance(root.left, k - 1);
                    printKDistance(root.right, k - 1);
                }
            }

            public static void main(String[] args) {
                Node root = sampleTree();
                for (int k = 0; k < 4; k++) {
                    System.out.print("k = " + k + ": ");
                    printKDistance(root, k);
                    System.out.println();
                }
            }
        }
    ''', js=JS_TREE + '''
        function printKDistance(root, k) {
            if (root === null) return;
            if (k === 0) {                           // reached distance K: this node is an answer
                process.stdout.write(root.key + " ");
            } else {                                 // both children are one step closer
                printKDistance(root.left, k - 1);
                printKDistance(root.right, k - 1);
            }
        }

        const root = sampleTree();
        for (let k = 0; k < 4; k++) {
            process.stdout.write(`k = ${k}: `);
            printKDistance(root, k);
            console.log();
        }
    ''')
    yield complexity("O(n)", "O(h)")
    yield note("The recursion visits at most all nodes down to depth `K`, so it is `O(n)` in the worst case but stops early for small `K`. Nodes at distance `K` from the root are exactly **level K** — the level-order traversal below produces the same groups without recursion.")

    yield section("Level order traversal (breadth-first)", "layers-intersect")
    yield io("the sample tree", "10 20 30 40 50 60 70 80", "the tree 3 → 4 → 5 (each the left child of the previous)", "3 4 5")
    yield idea("Recursion naturally goes *deep*. To go *wide* — whole level before the next — use a **queue**: start with the root, and every time you dequeue a node, enqueue its children. Because a queue is FIFO, all of level `d` is dequeued before anything from level `d + 1`, which was enqueued later.")
    yield steps(
        ("Start", "Push the root into an empty queue."),
        ("Loop while the queue is not empty", "Pop the front node and print it."),
        ("Enqueue children", "Push its left child, then its right child (if they exist) — they will be visited after everything already in the queue."),
    )
    yield diagram('''
        queue →  [10]                 print 10, push 20 30
                 [20 30]              print 20, push 40 50
                 [30 40 50]           print 30, push 60
                 [40 50 60]           print 40 (leaf)
                 [50 60]              print 50, push 70 80
                 [60 70 80]           print 60, 70, 80 (leaves)
                 []                   done:  10 20 30 40 50 60 70 80
    ''', "The queue holds at most one level (plus part of the next) at any time")
    yield multi('''
        10 20 30 40 50 60 70 80
    ''', py=PY_TREE + '''
        from collections import deque

        def level_order(root):
            if root is None:
                return
            q = deque([root])
            while q:
                node = q.popleft()               # oldest node first (FIFO)
                print(node.key, end=" ")
                if node.left:                    # its children join the back of the line
                    q.append(node.left)
                if node.right:
                    q.append(node.right)

        level_order(sample_tree())
        print()
    ''', cpp='''
        #include <queue>''' + CPP_TREE + '''
        void levelOrder(Node* root) {
            if (!root) return;
            queue<Node*> q;
            q.push(root);
            while (!q.empty()) {
                Node* node = q.front(); q.pop();     // oldest node first (FIFO)
                cout << node->key << " ";
                if (node->left) q.push(node->left);  // its children join the back of the line
                if (node->right) q.push(node->right);
            }
        }

        int main() {
            levelOrder(sampleTree());
            cout << "\\n";
        }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {''' + JAVA_TREE + '''
            static void levelOrder(Node root) {
                if (root == null) return;
                Queue<Node> q = new ArrayDeque<>();
                q.offer(root);
                while (!q.isEmpty()) {
                    Node node = q.poll();                // oldest node first (FIFO)
                    System.out.print(node.key + " ");
                    if (node.left != null) q.offer(node.left);   // children join the back of the line
                    if (node.right != null) q.offer(node.right);
                }
            }

            public static void main(String[] args) {
                levelOrder(sampleTree());
                System.out.println();
            }
        }
    ''', js=JS_TREE + '''
        function levelOrder(root) {
            if (root === null) return;
            const q = [root];
            let head = 0;                        // index of the front: avoids O(n) shift()
            while (head < q.length) {
                const node = q[head++];          // oldest node first (FIFO)
                process.stdout.write(node.key + " ");
                if (node.left) q.push(node.left);    // its children join the back of the line
                if (node.right) q.push(node.right);
            }
        }

        levelOrder(sampleTree());
        console.log();
    ''')
    yield complexity("O(n)", "O(w) — the widest level, up to n/2 nodes for a perfect tree")
    yield p("**Level by level.** Interviewers usually want each level on its own line. Record the queue's size at the start of each round: exactly that many nodes belong to the current level, so pop just those, then start the next line.")
    yield multi('''
        10
        20 30
        40 50 60
        70 80
    ''', py=PY_TREE + '''
        from collections import deque

        def level_order_lines(root):
            if root is None:
                return
            q = deque([root])
            while q:
                count = len(q)                   # nodes of the current level
                for _ in range(count):
                    node = q.popleft()
                    print(node.key, end=" ")
                    if node.left:
                        q.append(node.left)
                    if node.right:
                        q.append(node.right)
                print()                          # level finished

        level_order_lines(sample_tree())
    ''', cpp='''
        #include <queue>''' + CPP_TREE + '''
        void levelOrderLines(Node* root) {
            if (!root) return;
            queue<Node*> q;
            q.push(root);
            while (!q.empty()) {
                int count = (int)q.size();           // nodes of the current level
                for (int i = 0; i < count; i++) {
                    Node* node = q.front(); q.pop();
                    cout << node->key << " ";
                    if (node->left) q.push(node->left);
                    if (node->right) q.push(node->right);
                }
                cout << "\\n";                        // level finished
            }
        }

        int main() { levelOrderLines(sampleTree()); }
    ''', java='''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {''' + JAVA_TREE + '''
            static void levelOrderLines(Node root) {
                if (root == null) return;
                Queue<Node> q = new ArrayDeque<>();
                q.offer(root);
                while (!q.isEmpty()) {
                    int count = q.size();                // nodes of the current level
                    for (int i = 0; i < count; i++) {
                        Node node = q.poll();
                        System.out.print(node.key + " ");
                        if (node.left != null) q.offer(node.left);
                        if (node.right != null) q.offer(node.right);
                    }
                    System.out.println();                // level finished
                }
            }

            public static void main(String[] args) { levelOrderLines(sampleTree()); }
        }
    ''', js=JS_TREE + '''
        function levelOrderLines(root) {
            if (root === null) return;
            let level = [root];
            while (level.length) {               // the current level is a whole array
                const next = [];
                process.stdout.write(level.map(n => n.key).join(" ") + "\\n");
                for (const node of level) {
                    if (node.left) next.push(node.left);
                    if (node.right) next.push(node.right);
                }
                level = next;                    // level finished
            }
        }

        levelOrderLines(sampleTree());
    ''')
    yield complexity("O(n)", "O(w)")
    yield pitfall("Using a plain list / array as the queue and removing from the front (`list.pop(0)`, `Array.shift()`) makes every dequeue `O(n)` and the traversal `O(n²)`. Use `collections.deque`, `std::queue`, `ArrayDeque`, or an index into the array as above.")

    yield section("Size of a binary tree", "sum")
    yield io("the sample tree", "8", "an empty tree", "0")
    yield idea("The size of a tree is the size of the left subtree plus the size of the right subtree plus one for the root. Same shape as `height()`, with `+` instead of `max`.")
    yield multi('''
        size: 8
        size of left subtree: 5
        size of right subtree: 2
    ''', py=PY_TREE + '''
        def size(root):
            if root is None:
                return 0
            return size(root.left) + size(root.right) + 1    # left + right + the root

        root = sample_tree()
        print("size:", size(root))
        print("size of left subtree:", size(root.left))
        print("size of right subtree:", size(root.right))
    ''', cpp=CPP_TREE + '''
        int size(Node* root) {
            if (!root) return 0;
            return size(root->left) + size(root->right) + 1;  // left + right + the root
        }

        int main() {
            Node* root = sampleTree();
            cout << "size: " << size(root) << "\\n";
            cout << "size of left subtree: " << size(root->left) << "\\n";
            cout << "size of right subtree: " << size(root->right) << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static int size(Node root) {
                if (root == null) return 0;
                return size(root.left) + size(root.right) + 1;    // left + right + the root
            }

            public static void main(String[] args) {
                Node root = sampleTree();
                System.out.println("size: " + size(root));
                System.out.println("size of left subtree: " + size(root.left));
                System.out.println("size of right subtree: " + size(root.right));
            }
        }
    ''', js=JS_TREE + '''
        function size(root) {
            if (root === null) return 0;
            return size(root.left) + size(root.right) + 1;    // left + right + the root
        }

        const root = sampleTree();
        console.log("size:", size(root));
        console.log("size of left subtree:", size(root.left));
        console.log("size of right subtree:", size(root.right));
    ''')
    yield complexity("O(n)", "O(h)")
    yield note("Every node is visited once and does `O(1)` work, hence `O(n)` time. An iterative version is level order with a counter — the recursion is just shorter.")

    yield section("Maximum value in a binary tree", "arrow-up-circle")
    yield io("the sample tree", "80", "an empty tree", "-inf (no maximum)")
    yield idea("The maximum of a tree is the largest of three things: the root's key, the maximum of the left subtree and the maximum of the right subtree. The base case returns `−∞` so that an empty subtree never wins. A plain binary tree has no ordering, so **every** node must be looked at — unlike a BST, where the maximum is simply the rightmost node.")
    yield multi('''
        max: 80
        max of right subtree: 60
    ''', py=PY_TREE + '''
        import math

        def get_max(root):
            if root is None:
                return -math.inf                     # identity for max: never wins
            return max(root.key, get_max(root.left), get_max(root.right))

        root = sample_tree()
        print("max:", get_max(root))
        print("max of right subtree:", get_max(root.right))
    ''', cpp='''
        #include <algorithm>
        #include <climits>''' + CPP_TREE + '''
        int getMax(Node* root) {
            if (!root) return INT_MIN;               // identity for max: never wins
            return max({root->key, getMax(root->left), getMax(root->right)});
        }

        int main() {
            Node* root = sampleTree();
            cout << "max: " << getMax(root) << "\\n";
            cout << "max of right subtree: " << getMax(root->right) << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_TREE + '''
            static int getMax(Node root) {
                if (root == null) return Integer.MIN_VALUE;   // identity for max: never wins
                return Math.max(root.key, Math.max(getMax(root.left), getMax(root.right)));
            }

            public static void main(String[] args) {
                Node root = sampleTree();
                System.out.println("max: " + getMax(root));
                System.out.println("max of right subtree: " + getMax(root.right));
            }
        }
    ''', js=JS_TREE + '''
        function getMax(root) {
            if (root === null) return -Infinity;     // identity for max: never wins
            return Math.max(root.key, getMax(root.left), getMax(root.right));
        }

        const root = sampleTree();
        console.log("max:", getMax(root));
        console.log("max of right subtree:", getMax(root.right));
    ''')
    yield complexity("O(n)", "O(h)")
    yield pitfall("Returning `0` for an empty subtree is wrong as soon as all keys are negative. Use the smallest possible value (`-math.inf`, `INT_MIN`, `Integer.MIN_VALUE`, `-Infinity`) as the base case — the same trick gives `getMin` with `+∞` and `min`.")

    yield section("Recursion on trees: the pattern", "repeat")
    yield p("Height, size, maximum, and most other tree problems have the same three-line shape — remember it and you can derive the others in an interview.")
    yield steps(
        ("Base case", "`if root is None: return <identity>` — `0` for counting, `0`/`-1` for height, `−∞` for max, `+∞` for min, `True` for *is valid*."),
        ("Recurse", "Solve the problem for `root.left` and `root.right` — trust the recursion to return the right answer for each subtree."),
        ("Combine", "Mix the two answers with the root: `max(l, r) + 1`, `l + r + 1`, `max(key, l, r)`, `l and r and <condition on root>`."),
    )
    yield table(
        ["Problem", "Base case", "Combine"],
        ["Height", "`0`", "`max(l, r) + 1`"],
        ["Size", "`0`", "`l + r + 1`"],
        ["Maximum", "`−∞`", "`max(key, l, r)`"],
        ["Sum of keys", "`0`", "`l + r + key`"],
        ["Count leaves", "`0`; a leaf returns `1`", "`l + r`"],
        ["Is balanced", "`True`", "`l and r and |height(left) − height(right)| ≤ 1`"],
    )

    yield section("Interview Q&A", "message-question")
    yield qa("What is the difference between a binary tree and a binary search tree?",
             "A binary tree only limits every node to at most two children — the keys can be anywhere. A binary search tree adds an **ordering invariant**: every key in a node's left subtree is smaller and every key in its right subtree is larger. That invariant is what makes search `O(h)` instead of `O(n)`.")
    yield qa("Why is the height of a tree so important?",
             "Almost every operation walks one root-to-leaf path, so it costs `O(h)`. For a balanced tree `h = O(log n)`; for a skewed tree `h = n − 1`, and the tree degrades into a linked list. Self-balancing trees (AVL, red-black) exist purely to keep `h` logarithmic.")
    yield qa("Which traversal would you use to delete every node of a tree, and why?",
             "**Postorder**: both children are freed before the parent, so no pointer to a child is ever lost. Preorder would free the parent — and the links to its children — first.")
    yield qa("How do you get the inorder sequence without recursion?",
             "Use an explicit stack: walk left pushing every node, pop one and print it, then move to its right child and repeat. It is the same `O(n)` time and `O(h)` space, but the stack is yours instead of the call stack — useful in languages with a small recursion limit (Python stops at about 1000 frames).")
    yield qa("Is level order traversal depth-first or breadth-first, and what data structure does it need?",
             "Breadth-first — it finishes a level before starting the next. It needs a **queue**; the three depth-first traversals need a **stack** (the call stack when written recursively). Space is `O(w)` for the widest level versus `O(h)` for depth-first; for a perfect tree the last level holds about `n/2` nodes, so BFS can use far more memory.")
    yield qa("Can you rebuild a binary tree from its traversals?",
             "From **inorder plus preorder** (or inorder plus postorder), yes: the first preorder element is the root, its position in the inorder sequence splits the inorder into the left and right subtrees, and you recurse. Preorder plus postorder alone is **not** enough — a node with a single child is ambiguous. A single traversal with `null` markers is also enough, which is how serialisation works.")


# ── the sample BST from the notes: insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7 ──────────────────
# Every program in the `bst` topic (after Insert) starts with one of these preludes.

PY_BST = '''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def insert(root, key):               # insert key, keeping the BST invariant
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
            elif key > root.key:
                root.right = insert(root.right, key)
            return root                      # duplicates are ignored

        def inorder(root):
            if root:
                inorder(root.left)
                print(root.key, end=" ")
                inorder(root.right)

        def sample_bst():                    # insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7
            root = None
            for key in (20, 15, 30, 40, 50, 12, 18, 35, 80, 7):
                root = insert(root, key)
            return root
'''

CPP_BST = '''
        #include <iostream>
        using namespace std;

        struct Node {
            int key;
            Node *left, *right;
            Node(int k) : key(k), left(nullptr), right(nullptr) {}
        };

        Node* insert(Node* root, int key) {       // insert key, keeping the BST invariant
            if (!root) return new Node(key);
            if (key < root->key) root->left = insert(root->left, key);
            else if (key > root->key) root->right = insert(root->right, key);
            return root;                          // duplicates are ignored
        }

        void inorder(Node* root) {
            if (!root) return;
            inorder(root->left);
            cout << root->key << " ";
            inorder(root->right);
        }

        Node* sampleBST() {                       // insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7
            Node* root = nullptr;
            for (int key : {20, 15, 30, 40, 50, 12, 18, 35, 80, 7}) root = insert(root, key);
            return root;
        }
'''

JAVA_BST = '''
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node insert(Node root, int key) {   // insert key, keeping the BST invariant
                if (root == null) return new Node(key);
                if (key < root.key) root.left = insert(root.left, key);
                else if (key > root.key) root.right = insert(root.right, key);
                return root;                           // duplicates are ignored
            }

            static void inorder(Node root) {
                if (root == null) return;
                inorder(root.left);
                System.out.print(root.key + " ");
                inorder(root.right);
            }

            static Node sampleBST() {                  // insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7
                Node root = null;
                for (int key : new int[]{20, 15, 30, 40, 50, 12, 18, 35, 80, 7}) root = insert(root, key);
                return root;
            }
'''

JS_BST = '''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insert(root, key) {              // insert key, keeping the BST invariant
            if (root === null) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            return root;                          // duplicates are ignored
        }

        function inorder(root) {
            if (root === null) return;
            inorder(root.left);
            process.stdout.write(root.key + " ");
            inorder(root.right);
        }

        function sampleBST() {                    // insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7
            let root = null;
            for (const key of [20, 15, 30, 40, 50, 12, 18, 35, 80, 7]) root = insert(root, key);
            return root;
        }
'''


@topic(G, "bst", "Binary Search Tree", "hierarchy")
def _():
    yield lead("A binary search tree keeps keys **in order**: smaller keys to the left, larger to the right, at every node. That one rule turns search, insert, delete, floor and ceiling into a single walk down one path — `O(log n)` when the tree is balanced — and makes an inorder traversal print the keys sorted.")
    yield define("Binary search tree (BST)", "a binary tree in which, for **every** node, all keys in its left subtree are smaller than the node's key and all keys in its right subtree are greater. Keys are usually assumed distinct. Like a linked list it is a *linked* data structure: nodes connected by pointers, no fixed capacity.")
    yield diagram('''
                        20
                     /      \\
                   15        30
                  /  \\         \\
                12    18        40
               /               /  \\
              7              35    50
                                     \\
                                      80
    ''', "The sample BST: an empty tree after inserting 20, 15, 30, 40, 50, 12, 18, 35, 80, 7 in that order")
    yield p("Check the invariant at any node: left of `20` are `15 12 18 7` (all smaller), right are `30 40 35 50 80` (all larger). Left of `40` is `35`, right is `50 80`. It holds **for the whole subtree**, not just the two children — a tree where `35` sat under `15` would have every child in order and still be wrong.")
    yield warn("The invariant is *left subtree < node < right subtree*, **not** *left child < node < right child*. A node's right child may have a left child, and that grandchild must still be greater than the node — e.g. `35` is a left child of `40` but greater than `30`.")

    yield section("Why a BST: comparison with other structures", "scale")
    yield p("A BST is the structure for data that must stay **sorted while it changes**. Arrays are fast at one thing and slow at the other; a hash table is fastest for exact lookups but knows nothing about order.")
    yield table(
        ["Operation", "Unsorted array", "Sorted array", "Linked list", "BST (balanced)", "Hash table"],
        ["Search", "O(n)", "O(log n)", "O(n)", "**O(log n)**", "O(1) average"],
        ["Insert", "O(1)", "O(n)", "O(1)", "**O(log n)**", "O(1) average"],
        ["Delete", "O(n)", "O(n)", "O(n)", "**O(log n)**", "O(1) average"],
        ["Find closest (floor / ceiling)", "O(n)", "O(log n)", "O(n)", "**O(log n)**", "O(n)"],
        ["Sorted traversal", "O(n log n)", "O(n)", "O(n log n)", "**O(n)**", "O(n log n)"],
    )
    yield p("Every BST operation walks one root-to-leaf path, so it costs `O(h)` where `h` is the height. The *balanced* column assumes `h = O(log n)`; the self-balancing section shows how libraries guarantee it. Those libraries are the ready-made BSTs you should normally use:")
    yield table(
        ["Language", "Ordered set", "Ordered map", "Implementation"],
        ["C++", "`std::set`, `std::multiset`", "`std::map`, `std::multimap`", "red-black tree"],
        ["Java", "`TreeSet`", "`TreeMap`", "red-black tree"],
        ["Python", "— (use `sortedcontainers.SortedList`, or `bisect` on a list)", "—", "no BST in the standard library"],
        ["JavaScript", "—", "—", "none built in — implement one or use a library"],
    )

    yield section("Operations and their cost", "list-check")
    yield table(
        ["Operation", "How", "Time"],
        ["`search(k)`", "Go left if `k` is smaller, right if larger, stop on match or `null`", "O(h)"],
        ["`insert(k)`", "Search for `k`; attach a new leaf where the search fell off", "O(h)"],
        ["`delete(k)`", "Search, then one of three cases (leaf, one child, two children)", "O(h)"],
        ["`min()` / `max()`", "Follow left / right pointers to the end", "O(h)"],
        ["`floor(k)` / `ceil(k)`", "Search, remembering the last candidate on the way down", "O(h)"],
        ["`inorder()`", "Left, node, right — visits keys in sorted order", "O(n)"],
    )
    yield p("`h` is `⌈log₂(n + 1)⌉` for a perfectly balanced tree and `n` for a degenerate one, so the same code runs in `O(log n)` or `O(n)` depending only on the **shape**.")

    yield section("Insert", "plus")
    yield io("insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7 into an empty tree", "the sample BST; inorder 7 12 15 18 20 30 35 40 50 80", "then insert 60", "60 becomes the left child of 80")
    yield idea("Search for the key. If you find it, do nothing (no duplicates). If you fall off the tree at a `null` pointer, that is exactly where the key belongs: create a leaf there. The recursive version returns the (possibly new) root of each subtree so the parent can re-attach it — `root.left = insert(root.left, key)` — which handles the empty-tree case for free.")
    yield diagram('''
        insert 7:   20 → smaller, go left            20
                    15 → smaller, go left          /    \\
                    12 → smaller, go left        15      30
                    null → create 7 here        /  \\       \\
                                              12    18      40
                                             /             /  \\
                                           [7]           35    50
    ''', "Every insert adds a new leaf at the point where the search ends")
    yield multi('''
        inorder: 7 12 15 18 20 30 35 40 50 80
        root: 20
        after insert 40 (duplicate): 7 12 15 18 20 30 35 40 50 80
        after insert 60: 7 12 15 18 20 30 35 40 50 60 80
    ''', py=PY_BST + '''
        root = sample_bst()
        print("inorder:", end=" "); inorder(root); print()
        print("root:", root.key)
        root = insert(root, 40)              # already present: tree unchanged
        print("after insert 40 (duplicate):", end=" "); inorder(root); print()
        root = insert(root, 60)              # 20 → 30 → 40 → 50 → 80 → left of 80
        print("after insert 60:", end=" "); inorder(root); print()
    ''', cpp=CPP_BST + '''
        int main() {
            Node* root = sampleBST();
            cout << "inorder: "; inorder(root); cout << "\\n";
            cout << "root: " << root->key << "\\n";
            root = insert(root, 40);              // already present: tree unchanged
            cout << "after insert 40 (duplicate): "; inorder(root); cout << "\\n";
            root = insert(root, 60);              // 20 → 30 → 40 → 50 → 80 → left of 80
            cout << "after insert 60: "; inorder(root); cout << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_BST + '''
            public static void main(String[] args) {
                Node root = sampleBST();
                System.out.print("inorder: "); inorder(root); System.out.println();
                System.out.println("root: " + root.key);
                root = insert(root, 40);               // already present: tree unchanged
                System.out.print("after insert 40 (duplicate): "); inorder(root); System.out.println();
                root = insert(root, 60);               // 20 → 30 → 40 → 50 → 80 → left of 80
                System.out.print("after insert 60: "); inorder(root); System.out.println();
            }
        }
    ''', js=JS_BST + '''
        let root = sampleBST();
        process.stdout.write("inorder: "); inorder(root); console.log();
        console.log("root:", root.key);
        root = insert(root, 40);                  // already present: tree unchanged
        process.stdout.write("after insert 40 (duplicate): "); inorder(root); console.log();
        root = insert(root, 60);                  // 20 → 30 → 40 → 50 → 80 → left of 80
        process.stdout.write("after insert 60: "); inorder(root); console.log();
    ''')
    yield complexity("O(h)", "O(h) recursion stack")
    yield p("**Iterative insert** avoids the recursion stack: walk down with a `parent` pointer until `curr` is `null`, then hang the new node on the correct side of `parent`. Same `O(h)` time, `O(1)` extra space.")
    yield multi('''
        inorder: 7 12 15 18 20 30 35 40 50 80
        root: 20
        after insert 40 (duplicate): 7 12 15 18 20 30 35 40 50 80
        after insert 60: 7 12 15 18 20 30 35 40 50 60 80
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = None
                self.right = None

        def insert_iter(root, key):
            node = Node(key)
            if root is None:
                return node                      # empty tree: the new node is the root
            parent, curr = None, root
            while curr is not None:              # search, remembering the parent
                if key == curr.key:
                    return root                  # duplicate: nothing to do
                parent = curr
                curr = curr.left if key < curr.key else curr.right
            if key < parent.key:                 # hang the leaf on the correct side
                parent.left = node
            else:
                parent.right = node
            return root

        def inorder(root):
            if root:
                inorder(root.left)
                print(root.key, end=" ")
                inorder(root.right)

        root = None
        for key in (20, 15, 30, 40, 50, 12, 18, 35, 80, 7):
            root = insert_iter(root, key)
        print("inorder:", end=" "); inorder(root); print()
        print("root:", root.key)
        root = insert_iter(root, 40)
        print("after insert 40 (duplicate):", end=" "); inorder(root); print()
        root = insert_iter(root, 60)
        print("after insert 60:", end=" "); inorder(root); print()
    ''', cpp='''
        #include <iostream>
        using namespace std;

        struct Node {
            int key;
            Node *left, *right;
            Node(int k) : key(k), left(nullptr), right(nullptr) {}
        };

        Node* insertIter(Node* root, int key) {
            Node* node = new Node(key);
            if (!root) return node;                   // empty tree: the new node is the root
            Node* parent = nullptr;
            Node* curr = root;
            while (curr) {                            // search, remembering the parent
                if (key == curr->key) { delete node; return root; }   // duplicate
                parent = curr;
                curr = key < curr->key ? curr->left : curr->right;
            }
            if (key < parent->key) parent->left = node;   // hang the leaf on the correct side
            else parent->right = node;
            return root;
        }

        void inorder(Node* root) {
            if (!root) return;
            inorder(root->left);
            cout << root->key << " ";
            inorder(root->right);
        }

        int main() {
            Node* root = nullptr;
            for (int key : {20, 15, 30, 40, 50, 12, 18, 35, 80, 7}) root = insertIter(root, key);
            cout << "inorder: "; inorder(root); cout << "\\n";
            cout << "root: " << root->key << "\\n";
            root = insertIter(root, 40);
            cout << "after insert 40 (duplicate): "; inorder(root); cout << "\\n";
            root = insertIter(root, 60);
            cout << "after insert 60: "; inorder(root); cout << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Node insertIter(Node root, int key) {
                Node node = new Node(key);
                if (root == null) return node;             // empty tree: the new node is the root
                Node parent = null, curr = root;
                while (curr != null) {                     // search, remembering the parent
                    if (key == curr.key) return root;      // duplicate: nothing to do
                    parent = curr;
                    curr = key < curr.key ? curr.left : curr.right;
                }
                if (key < parent.key) parent.left = node;  // hang the leaf on the correct side
                else parent.right = node;
                return root;
            }

            static void inorder(Node root) {
                if (root == null) return;
                inorder(root.left);
                System.out.print(root.key + " ");
                inorder(root.right);
            }

            public static void main(String[] args) {
                Node root = null;
                for (int key : new int[]{20, 15, 30, 40, 50, 12, 18, 35, 80, 7}) root = insertIter(root, key);
                System.out.print("inorder: "); inorder(root); System.out.println();
                System.out.println("root: " + root.key);
                root = insertIter(root, 40);
                System.out.print("after insert 40 (duplicate): "); inorder(root); System.out.println();
                root = insertIter(root, 60);
                System.out.print("after insert 60: "); inorder(root); System.out.println();
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; }
        }

        function insertIter(root, key) {
            const node = new Node(key);
            if (root === null) return node;           // empty tree: the new node is the root
            let parent = null, curr = root;
            while (curr !== null) {                   // search, remembering the parent
                if (key === curr.key) return root;    // duplicate: nothing to do
                parent = curr;
                curr = key < curr.key ? curr.left : curr.right;
            }
            if (key < parent.key) parent.left = node; // hang the leaf on the correct side
            else parent.right = node;
            return root;
        }

        function inorder(root) {
            if (root === null) return;
            inorder(root.left);
            process.stdout.write(root.key + " ");
            inorder(root.right);
        }

        let root = null;
        for (const key of [20, 15, 30, 40, 50, 12, 18, 35, 80, 7]) root = insertIter(root, key);
        process.stdout.write("inorder: "); inorder(root); console.log();
        console.log("root:", root.key);
        root = insertIter(root, 40);
        process.stdout.write("after insert 40 (duplicate): "); inorder(root); console.log();
        root = insertIter(root, 60);
        process.stdout.write("after insert 60: "); inorder(root); console.log();
    ''')
    yield complexity("O(h)", "O(1)")
    yield pitfall("Inserting keys that arrive **already sorted** (`1, 2, 3, 4, …`) builds a right-skewed chain of height `n`: every later operation is `O(n)`. Shuffle the input, or use a self-balancing tree.")
    yield note("Inorder traversal of a BST always prints the keys in ascending order — so *build a BST, traverse inorder* is a sorting algorithm (tree sort), `O(n log n)` when the tree stays balanced.")

    yield section("Search", "search")
    yield io("the sample BST, key = 7", "true", "key = 25", "false")
    yield idea("Compare the key with the current node. Equal — found. Smaller — the key can only be in the left subtree, so go left. Larger — go right. Reaching `null` means the key is absent. Each step discards an entire subtree, which is why it is `O(h)` and not `O(n)`: binary search on a tree.")
    yield diagram('''
        search 7:  20 → 15 → 12 → 7  ✓ found (4 comparisons)
        search 25: 20 → 30 → null    ✗ 25 > 20 go right, 25 < 30 go left, nothing there
    ''', "A search follows one path from the root")
    yield multi('''
        search 7: true
        search 25: false
        search 35 (iterative): true
        search 100 (iterative): false
    ''', py=PY_BST + '''
        def search(root, key):                   # recursive
            if root is None:
                return False
            if key == root.key:
                return True
            if key < root.key:
                return search(root.left, key)    # only the left subtree can hold it
            return search(root.right, key)

        def search_iter(root, key):              # iterative: O(1) space
            while root is not None:
                if key == root.key:
                    return True
                root = root.left if key < root.key else root.right
            return False

        root = sample_bst()
        print("search 7:", "true" if search(root, 7) else "false")
        print("search 25:", "true" if search(root, 25) else "false")
        print("search 35 (iterative):", "true" if search_iter(root, 35) else "false")
        print("search 100 (iterative):", "true" if search_iter(root, 100) else "false")
    ''', cpp=CPP_BST + '''
        bool search(Node* root, int key) {            // recursive
            if (!root) return false;
            if (key == root->key) return true;
            if (key < root->key) return search(root->left, key);   // only the left subtree can hold it
            return search(root->right, key);
        }

        bool searchIter(Node* root, int key) {        // iterative: O(1) space
            while (root) {
                if (key == root->key) return true;
                root = key < root->key ? root->left : root->right;
            }
            return false;
        }

        int main() {
            Node* root = sampleBST();
            cout << "search 7: " << (search(root, 7) ? "true" : "false") << "\\n";
            cout << "search 25: " << (search(root, 25) ? "true" : "false") << "\\n";
            cout << "search 35 (iterative): " << (searchIter(root, 35) ? "true" : "false") << "\\n";
            cout << "search 100 (iterative): " << (searchIter(root, 100) ? "true" : "false") << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_BST + '''
            static boolean search(Node root, int key) {        // recursive
                if (root == null) return false;
                if (key == root.key) return true;
                if (key < root.key) return search(root.left, key);   // only the left subtree can hold it
                return search(root.right, key);
            }

            static boolean searchIter(Node root, int key) {    // iterative: O(1) space
                while (root != null) {
                    if (key == root.key) return true;
                    root = key < root.key ? root.left : root.right;
                }
                return false;
            }

            public static void main(String[] args) {
                Node root = sampleBST();
                System.out.println("search 7: " + search(root, 7));
                System.out.println("search 25: " + search(root, 25));
                System.out.println("search 35 (iterative): " + searchIter(root, 35));
                System.out.println("search 100 (iterative): " + searchIter(root, 100));
            }
        }
    ''', js=JS_BST + '''
        function search(root, key) {                  // recursive
            if (root === null) return false;
            if (key === root.key) return true;
            if (key < root.key) return search(root.left, key);   // only the left subtree can hold it
            return search(root.right, key);
        }

        function searchIter(root, key) {              // iterative: O(1) space
            while (root !== null) {
                if (key === root.key) return true;
                root = key < root.key ? root.left : root.right;
            }
            return false;
        }

        const root = sampleBST();
        console.log("search 7:", search(root, 7));
        console.log("search 25:", search(root, 25));
        console.log("search 35 (iterative):", searchIter(root, 35));
        console.log("search 100 (iterative):", searchIter(root, 100));
    ''')
    yield complexity("O(h)", "O(h) recursive, O(1) iterative")
    yield note("The recursion here is a **tail call** — nothing happens after it returns — which is why the iterative version is a trivial rewrite and the one to prefer in production code.")

    yield section("Delete", "trash")
    yield io("the sample BST, delete 7 (a leaf)", "inorder 12 15 18 20 30 35 40 50 80", "delete 30 (one child)", "40 takes its place: 12 15 18 20 35 40 50 80", "delete 20 (two children)", "replaced by its inorder successor 35: 12 15 18 35 40 50 80")
    yield idea("Search for the key, then fix the hole it leaves. A **leaf** can simply go. A node with **one child** is replaced by that child. A node with **two children** cannot be unlinked without breaking the shape — instead copy the **inorder successor** (the smallest key of the right subtree, found by walking left from `right`) into the node and delete the successor from the right subtree; the successor has no left child, so that second deletion is always case 1 or 2.")
    yield diagram('''
       Case 1 — leaf: unlink it            Case 2 — one child: parent adopts the child
               15                                   20                 20
              /  \\        delete 7                   \\     delete 30     \\
            12    18     ────────▶    12             30   ──────────▶    40
           /                                            \\               /  \\
          7                                              40           35    50

       Case 3 — two children: copy the inorder successor, then delete the successor
               20          successor of 20 = min of right subtree = 35
            /      \\                                   35
          15        40        delete 20             /      \\
         /  \\      /  \\      ────────▶            15        40
       12    18  35    50                        /  \\         \\
        /               \\                      12    18        50
       7                 80                     /                \\
                                               7                  80
    ''', "The three cases of BST deletion")
    yield steps(
        ("Find the node", "Recurse left or right as in search; `root.left = delete(root.left, key)` re-attaches whatever comes back."),
        ("Leaf, or one child", "Return the child (or `null`) to the parent — the node is bypassed."),
        ("Two children", "Find `succ = min(root.right)`, copy `succ.key` into `root`, then `root.right = delete(root.right, succ.key)`."),
    )
    yield multi('''
        delete 7 (leaf): 12 15 18 20 30 35 40 50 80
        delete 30 (one child): 12 15 18 20 35 40 50 80
        delete 20 (two children): 12 15 18 35 40 50 80
        new root: 35
    ''', py=PY_BST + '''
        def min_node(node):                      # leftmost node of a subtree
            while node.left is not None:
                node = node.left
            return node

        def delete_key(root, key):
            if root is None:
                return None
            if key < root.key:
                root.left = delete_key(root.left, key)
            elif key > root.key:
                root.right = delete_key(root.right, key)
            else:                                # found it
                if root.left is None:            # case 1 & 2: zero or one child
                    return root.right
                if root.right is None:
                    return root.left
                succ = min_node(root.right)      # case 3: two children
                root.key = succ.key              # copy the inorder successor ...
                root.right = delete_key(root.right, succ.key)   # ... and remove it from the right
            return root

        root = sample_bst()
        root = delete_key(root, 7)
        print("delete 7 (leaf):", end=" "); inorder(root); print()
        root = delete_key(root, 30)
        print("delete 30 (one child):", end=" "); inorder(root); print()
        root = delete_key(root, 20)
        print("delete 20 (two children):", end=" "); inorder(root); print()
        print("new root:", root.key)
    ''', cpp=CPP_BST + '''
        Node* minNode(Node* node) {                   // leftmost node of a subtree
            while (node->left) node = node->left;
            return node;
        }

        Node* deleteKey(Node* root, int key) {
            if (!root) return nullptr;
            if (key < root->key) root->left = deleteKey(root->left, key);
            else if (key > root->key) root->right = deleteKey(root->right, key);
            else {                                    // found it
                if (!root->left || !root->right) {    // case 1 & 2: zero or one child
                    Node* child = root->left ? root->left : root->right;
                    delete root;
                    return child;
                }
                Node* succ = minNode(root->right);    // case 3: two children
                root->key = succ->key;                // copy the inorder successor ...
                root->right = deleteKey(root->right, succ->key);   // ... and remove it from the right
            }
            return root;
        }

        int main() {
            Node* root = sampleBST();
            root = deleteKey(root, 7);
            cout << "delete 7 (leaf): "; inorder(root); cout << "\\n";
            root = deleteKey(root, 30);
            cout << "delete 30 (one child): "; inorder(root); cout << "\\n";
            root = deleteKey(root, 20);
            cout << "delete 20 (two children): "; inorder(root); cout << "\\n";
            cout << "new root: " << root->key << "\\n";
        }
    ''', java='''
        public class Main {''' + JAVA_BST + '''
            static Node minNode(Node node) {               // leftmost node of a subtree
                while (node.left != null) node = node.left;
                return node;
            }

            static Node deleteKey(Node root, int key) {
                if (root == null) return null;
                if (key < root.key) root.left = deleteKey(root.left, key);
                else if (key > root.key) root.right = deleteKey(root.right, key);
                else {                                     // found it
                    if (root.left == null) return root.right;   // case 1 & 2: zero or one child
                    if (root.right == null) return root.left;
                    Node succ = minNode(root.right);       // case 3: two children
                    root.key = succ.key;                   // copy the inorder successor ...
                    root.right = deleteKey(root.right, succ.key);   // ... and remove it from the right
                }
                return root;
            }

            public static void main(String[] args) {
                Node root = sampleBST();
                root = deleteKey(root, 7);
                System.out.print("delete 7 (leaf): "); inorder(root); System.out.println();
                root = deleteKey(root, 30);
                System.out.print("delete 30 (one child): "); inorder(root); System.out.println();
                root = deleteKey(root, 20);
                System.out.print("delete 20 (two children): "); inorder(root); System.out.println();
                System.out.println("new root: " + root.key);
            }
        }
    ''', js=JS_BST + '''
        function minNode(node) {                      // leftmost node of a subtree
            while (node.left !== null) node = node.left;
            return node;
        }

        function deleteKey(root, key) {
            if (root === null) return null;
            if (key < root.key) root.left = deleteKey(root.left, key);
            else if (key > root.key) root.right = deleteKey(root.right, key);
            else {                                    // found it
                if (root.left === null) return root.right;    // case 1 & 2: zero or one child
                if (root.right === null) return root.left;
                const succ = minNode(root.right);     // case 3: two children
                root.key = succ.key;                  // copy the inorder successor ...
                root.right = deleteKey(root.right, succ.key);   // ... and remove it from the right
            }
            return root;
        }

        let root = sampleBST();
        root = deleteKey(root, 7);
        process.stdout.write("delete 7 (leaf): "); inorder(root); console.log();
        root = deleteKey(root, 30);
        process.stdout.write("delete 30 (one child): "); inorder(root); console.log();
        root = deleteKey(root, 20);
        process.stdout.write("delete 20 (two children): "); inorder(root); console.log();
        console.log("new root:", root.key);
    ''')
    yield complexity("O(h)", "O(h)")
    yield pitfall("In case 3 you may equally use the **inorder predecessor** (max of the left subtree). What you must not do is move the successor *node* without removing it from where it was, or forget to re-attach the result of the recursive delete — the classic bug is `delete_key(root.right, succ.key)` without the `root.right =`.")
    yield note("Why `O(h)`: the search is one path down, and the successor walk plus its deletion continue down the **same** path (successor is in the right subtree, and deleting it is another walk down). Total work is at most twice the height.")

    yield section("Floor in a BST", "arrow-down-circle")
    yield io("the sample BST, x = 14", "12 (the largest key ≤ 14)", "x = 1", "none (every key is larger)", "x = 20", "20", "x = 100", "80")
    yield define("Floor of x", "the largest key in the tree that is **≤ x**. Ceiling is the smallest key **≥ x**. Together they answer *what is closest to x* — something a hash table cannot do.")
    yield idea("Walk down as in search, keeping the best candidate seen so far. At a node with key **< x** the node is a candidate — remember it, then go **right** to look for something closer to `x`. At a node with key **> x** it cannot be the floor, go **left**. On an exact match the answer is the node itself. When the walk hits `null`, the remembered candidate is the floor.")
    yield steps(
        ("key == x", "Return this node — nothing can be closer."),
        ("key > x", "Too big; the floor must be in the left subtree: `root = root.left`."),
        ("key < x", "A valid candidate; a larger one may exist to the right: `res = root; root = root.right`."),
    )
    yield diagram('''
        floor(14):  20 > 14  → go left           candidate: —
                    15 > 14  → go left           candidate: —
                    12 < 14  → remember, go right  candidate: 12
                    null     → answer 12
    ''', "The candidate is updated only when we step right")
    yield multi('''
        floor(14) = 12
        floor(1) = none
        floor(20) = 20
        floor(100) = 80
    ''', py=PY_BST + '''
        def floor(root, x):
            res = None
            while root is not None:
                if root.key == x:
                    return root                  # exact match
                if root.key > x:
                    root = root.left             # too big: look left
                else:
                    res = root                   # candidate; a larger one may be on the right
                    root = root.right
            return res

        root = sample_bst()
        for x in (14, 1, 20, 100):
            node = floor(root, x)
            print(f"floor({x}) =", node.key if node else "none")
    ''', cpp=CPP_BST + '''
        Node* floorNode(Node* root, int x) {
            Node* res = nullptr;
            while (root) {
                if (root->key == x) return root;      // exact match
                if (root->key > x) root = root->left; // too big: look left
                else { res = root; root = root->right; }   // candidate; a larger one may be on the right
            }
            return res;
        }

        int main() {
            Node* root = sampleBST();
            for (int x : {14, 1, 20, 100}) {
                Node* node = floorNode(root, x);
                cout << "floor(" << x << ") = ";
                if (node) cout << node->key << "\\n"; else cout << "none\\n";
            }
        }
    ''', java='''
        public class Main {''' + JAVA_BST + '''
            static Node floor(Node root, int x) {
                Node res = null;
                while (root != null) {
                    if (root.key == x) return root;            // exact match
                    if (root.key > x) root = root.left;        // too big: look left
                    else { res = root; root = root.right; }    // candidate; a larger one may be on the right
                }
                return res;
            }

            public static void main(String[] args) {
                Node root = sampleBST();
                for (int x : new int[]{14, 1, 20, 100}) {
                    Node node = floor(root, x);
                    System.out.println("floor(" + x + ") = " + (node != null ? String.valueOf(node.key) : "none"));
                }
            }
        }
    ''', js=JS_BST + '''
        function floor(root, x) {
            let res = null;
            while (root !== null) {
                if (root.key === x) return root;          // exact match
                if (root.key > x) root = root.left;       // too big: look left
                else { res = root; root = root.right; }   // candidate; a larger one may be on the right
            }
            return res;
        }

        const root = sampleBST();
        for (const x of [14, 1, 20, 100]) {
            const node = floor(root, x);
            console.log(`floor(${x}) =`, node ? node.key : "none");
        }
    ''')
    yield complexity("O(h)", "O(1)")

    yield section("Ceiling in a BST", "arrow-up-circle")
    yield io("the sample BST, x = 21", "30 (the smallest key ≥ 21)", "x = 5", "7", "x = 7", "7", "x = 81", "none")
    yield idea("The mirror image of floor. A key **> x** is a candidate — remember it and go **left** for something closer; a key **< x** is useless, go **right**; an exact match is the answer.")
    yield steps(
        ("key == x", "Return this node."),
        ("key < x", "Too small; the ceiling must be on the right: `root = root.right`."),
        ("key > x", "A valid candidate; a smaller one may exist to the left: `res = root; root = root.left`."),
    )
    yield multi('''
        ceil(21) = 30
        ceil(5) = 7
        ceil(7) = 7
        ceil(81) = none
    ''', py=PY_BST + '''
        def ceil(root, x):
            res = None
            while root is not None:
                if root.key == x:
                    return root                  # exact match
                if root.key < x:
                    root = root.right            # too small: look right
                else:
                    res = root                   # candidate; a smaller one may be on the left
                    root = root.left
            return res

        root = sample_bst()
        for x in (21, 5, 7, 81):
            node = ceil(root, x)
            print(f"ceil({x}) =", node.key if node else "none")
    ''', cpp=CPP_BST + '''
        Node* ceilNode(Node* root, int x) {
            Node* res = nullptr;
            while (root) {
                if (root->key == x) return root;       // exact match
                if (root->key < x) root = root->right; // too small: look right
                else { res = root; root = root->left; }   // candidate; a smaller one may be on the left
            }
            return res;
        }

        int main() {
            Node* root = sampleBST();
            for (int x : {21, 5, 7, 81}) {
                Node* node = ceilNode(root, x);
                cout << "ceil(" << x << ") = ";
                if (node) cout << node->key << "\\n"; else cout << "none\\n";
            }
        }
    ''', java='''
        public class Main {''' + JAVA_BST + '''
            static Node ceil(Node root, int x) {
                Node res = null;
                while (root != null) {
                    if (root.key == x) return root;            // exact match
                    if (root.key < x) root = root.right;       // too small: look right
                    else { res = root; root = root.left; }     // candidate; a smaller one may be on the left
                }
                return res;
            }

            public static void main(String[] args) {
                Node root = sampleBST();
                for (int x : new int[]{21, 5, 7, 81}) {
                    Node node = ceil(root, x);
                    System.out.println("ceil(" + x + ") = " + (node != null ? String.valueOf(node.key) : "none"));
                }
            }
        }
    ''', js=JS_BST + '''
        function ceil(root, x) {
            let res = null;
            while (root !== null) {
                if (root.key === x) return root;          // exact match
                if (root.key < x) root = root.right;      // too small: look right
                else { res = root; root = root.left; }    // candidate; a smaller one may be on the left
            }
            return res;
        }

        const root = sampleBST();
        for (const x of [21, 5, 7, 81]) {
            const node = ceil(root, x);
            console.log(`ceil(${x}) =`, node ? node.key : "none");
        }
    ''')
    yield complexity("O(h)", "O(1)")
    yield note("Floor and ceiling in a **sorted array** are binary search (`bisect_right(a, x) - 1` and `bisect_left(a, x)` in Python). The BST versions are the same idea on a structure that also supports `O(log n)` insert and delete — which is exactly what *floor / ceiling in a stream* needs.")

    yield section("Self-balancing BSTs: why and how", "git-branch")
    yield p("The same set of keys can make BSTs of very different heights — it depends only on the **insertion order**. The operations above are `O(h)`, so the whole point of balancing is to keep `h = O(log n)` no matter what order the keys arrive in.")
    yield diagram('''
        insert 7, 10, 11, 15, 30, 35, 40          insert 15, 10, 35, 7, 11, 30, 40
        (sorted order → height 7)                 (balanced → height 3)

          7                                                  15
           \\                                               /    \\
            10                                           10      35
              \\                                         /  \\    /  \\
               11                                      7    11 30   40
                 \\
                  15
                    \\
                     30
                       \\
                        35
                          \\
                           40
    ''', "Same keys, two heights: every operation is O(n) on the left and O(log n) on the right")
    yield p("If all keys were known in advance we could build the perfectly balanced tree directly (insert the middle of the sorted keys, then recurse on each half). With **random insertions and deletions** we cannot — so a self-balancing tree **restructures** itself after every insert or delete that makes it lopsided.")
    yield diagram('''
        insert 100          insert 200          insert 300           restructure
                                                                     (rotate left at 100)
           100                 100                 100                     200
                                  \\                   \\                   /   \\
                                   200                 200              100     300
                                                          \\
                                                           300
    ''', "Inserting 100, 200, 300 produces a chain; one rotation turns it back into a balanced tree")
    yield p("The restructuring tool is the **rotation**: a local change of two or three pointers that moves a subtree one level up on one side and one level down on the other **without breaking the BST order** — the inorder sequence `T1 y T2 x T3` is the same before and after.")
    yield diagram('''
                P                                            P
                |                                            |
                x            Right rotation at x             y
              /   \\         ─────────────────────▶         /   \\
             y     T3                                     T1    x
            / \\             ◀─────────────────────             / \\
          T1   T2            Left rotation at y              T2   T3

        inorder before:  T1  y  T2  x  T3          inorder after:  T1  y  T2  x  T3   (unchanged)
    ''', "A rotation re-hangs T2 on the other node and is O(1)")
    yield table(
        ["Rotation", "Pointer changes", "Effect"],
        ["**Right** rotation at `x`", "`y = x.left; x.left = y.right; y.right = x`; `P` now points at `y`", "Left subtree gets one level shorter, right subtree one level taller"],
        ["**Left** rotation at `y`", "`x = y.right; y.right = x.left; x.left = y`; `P` now points at `x`", "The mirror image"],
    )
    yield p("The two famous self-balancing BSTs differ only in **what counts as balanced** and therefore in when they rotate: the **AVL tree** (strict, by height) and the **red-black tree** (looser, by colouring).")

    yield section("AVL tree", "arrows-vertical")
    yield define("AVL tree", "a BST in which, for **every** node, the heights of the left and right subtrees differ by at most 1. The **balance factor** `bf = height(left) − height(right)` is therefore always `−1`, `0` or `+1`; a node with `|bf| > 1` is unbalanced and must be rotated.")
    yield p("Named after Adelson-Velsky and Landis (1962). The height condition guarantees `h ≤ 1.44 log₂ n`, so every operation is `O(log n)`. Each node stores its height so the balance factor is `O(1)` to compute.")
    yield steps(
        ("Normal BST insert", "Walk down and attach the new leaf as usual."),
        ("Walk back up updating heights", "The recursion returns through every ancestor of the new node; recompute `height = 1 + max(hL, hR)` at each."),
        ("Find the first unbalanced ancestor", "The lowest node with `|bf| > 1`. Only ancestors can be unbalanced, and fixing the lowest one fixes everything above it for an insert."),
        ("Rotate according to one of four cases", "Decided by *which grandchild subtree* the new key went into."),
    )
    yield table(
        ["Case", "Where the key went", "Fix", "Rotations"],
        ["**Left-Left** (LL)", "Left child's left subtree (`bf > 1` and `key < left.key`)", "Right rotation at the unbalanced node", "1 (single)"],
        ["**Right-Right** (RR)", "Right child's right subtree (`bf < −1` and `key > right.key`)", "Left rotation at the unbalanced node", "1 (single)"],
        ["**Left-Right** (LR)", "Left child's right subtree (`bf > 1` and `key > left.key`)", "Left rotation at the left child, then right rotation at the node", "2 (double)"],
        ["**Right-Left** (RL)", "Right child's left subtree (`bf < −1` and `key < right.key`)", "Right rotation at the right child, then left rotation at the node", "2 (double)"],
    )
    yield diagram('''
        insert 20         insert 15         insert 5             Left-Left at 20:
                                                                 right rotation
           20                20                20                      15
                            /                 /                      /    \\
                          15                15                      5      20
                                           /
                                          5          bf(20) = 2 - 0 = +2 → unbalanced
    ''', "The LL case: the chain 20 → 15 → 5 becomes a balanced tree rooted at 15 (from the notes)")
    yield diagram('''
        Left-Right at 30 (insert 30, 10, 20):      Right-Left at 10 (insert 10, 30, 20):

            30            30            20            10           10            20
           /    left     /    right    /  \\            \\   right    \\   left    /  \\
         10   rotate   20   rotate   10    30          30  rotate   20  rotate 10    30
           \\  at 10    /     at 30                     /   at 30      \\   at 10
            20       10                              20                30
    ''', "The double-rotation cases: the first rotation turns them into LL / RR, the second fixes the balance")
    yield io("insert 20, 15, 5", "root 15 — preorder 15 5 20", "insert 20, 15, 30, 40, 50, 12, 18, 35, 80, 7", "preorder 20 15 12 7 18 40 30 35 50 80, height 4 (a plain BST has height 5)")
    yield multi('''
        LL 20 15 5: root 15, preorder 15 5 20
        RR 100 200 300: root 200, preorder 200 100 300
        LR 30 10 20: root 20, preorder 20 10 30
        RL 10 30 20: root 20, preorder 20 10 30
        sample keys: preorder 20 15 12 7 18 40 30 35 50 80
        height: 4
    ''', py='''
        class Node:
            def __init__(self, key):
                self.key = key
                self.left = self.right = None
                self.height = 1                  # a new node is a leaf (node-counting convention)

        def height(node):
            return node.height if node else 0

        def balance(node):
            return height(node.left) - height(node.right)

        def update(node):
            node.height = 1 + max(height(node.left), height(node.right))

        def rotate_right(x):                     # x's left child y becomes the subtree root
            y = x.left
            x.left = y.right                     # T2 moves across
            y.right = x
            update(x); update(y)                 # x first: it is now below y
            return y

        def rotate_left(x):                      # mirror image
            y = x.right
            x.right = y.left
            y.left = x
            update(x); update(y)
            return y

        def insert(root, key):
            if root is None:
                return Node(key)
            if key < root.key:
                root.left = insert(root.left, key)
            elif key > root.key:
                root.right = insert(root.right, key)
            else:
                return root                      # duplicate
            update(root)                         # on the way back up
            bf = balance(root)
            if bf > 1 and key < root.left.key:   # Left-Left
                return rotate_right(root)
            if bf < -1 and key > root.right.key: # Right-Right
                return rotate_left(root)
            if bf > 1 and key > root.left.key:   # Left-Right
                root.left = rotate_left(root.left)
                return rotate_right(root)
            if bf < -1 and key < root.right.key: # Right-Left
                root.right = rotate_right(root.right)
                return rotate_left(root)
            return root

        def preorder(root):
            if root:
                print(root.key, end=" ")
                preorder(root.left)
                preorder(root.right)

        def build(keys):
            root = None
            for k in keys:
                root = insert(root, k)
            return root

        for label, keys in (("LL", (20, 15, 5)), ("RR", (100, 200, 300)), ("LR", (30, 10, 20)), ("RL", (10, 30, 20))):
            root = build(keys)
            print(label, " ".join(map(str, keys)) + ": root", str(root.key) + ", preorder", end=" ")
            preorder(root); print()
        root = build((20, 15, 30, 40, 50, 12, 18, 35, 80, 7))
        print("sample keys: preorder", end=" "); preorder(root); print()
        print("height:", root.height)
    ''', cpp='''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        struct Node {
            int key, height = 1;                 // a new node is a leaf (node-counting convention)
            Node *left = nullptr, *right = nullptr;
            Node(int k) : key(k) {}
        };

        int height(Node* n) { return n ? n->height : 0; }
        int balance(Node* n) { return height(n->left) - height(n->right); }
        void update(Node* n) { n->height = 1 + max(height(n->left), height(n->right)); }

        Node* rotateRight(Node* x) {             // x's left child y becomes the subtree root
            Node* y = x->left;
            x->left = y->right;                  // T2 moves across
            y->right = x;
            update(x); update(y);                // x first: it is now below y
            return y;
        }

        Node* rotateLeft(Node* x) {              // mirror image
            Node* y = x->right;
            x->right = y->left;
            y->left = x;
            update(x); update(y);
            return y;
        }

        Node* insert(Node* root, int key) {
            if (!root) return new Node(key);
            if (key < root->key) root->left = insert(root->left, key);
            else if (key > root->key) root->right = insert(root->right, key);
            else return root;                                   // duplicate
            update(root);                                       // on the way back up
            int bf = balance(root);
            if (bf > 1 && key < root->left->key) return rotateRight(root);       // Left-Left
            if (bf < -1 && key > root->right->key) return rotateLeft(root);      // Right-Right
            if (bf > 1 && key > root->left->key) {                               // Left-Right
                root->left = rotateLeft(root->left);
                return rotateRight(root);
            }
            if (bf < -1 && key < root->right->key) {                             // Right-Left
                root->right = rotateRight(root->right);
                return rotateLeft(root);
            }
            return root;
        }

        void preorder(Node* root) {
            if (!root) return;
            cout << root->key << " ";
            preorder(root->left);
            preorder(root->right);
        }

        Node* build(const vector<int>& keys) {
            Node* root = nullptr;
            for (int k : keys) root = insert(root, k);
            return root;
        }

        int main() {
            vector<pair<string, vector<int>>> cases = {
                {"LL", {20, 15, 5}}, {"RR", {100, 200, 300}}, {"LR", {30, 10, 20}}, {"RL", {10, 30, 20}}};
            for (auto& [label, keys] : cases) {
                Node* root = build(keys);
                cout << label;
                for (int k : keys) cout << " " << k;
                cout << ": root " << root->key << ", preorder ";
                preorder(root); cout << "\\n";
            }
            Node* root = build({20, 15, 30, 40, 50, 12, 18, 35, 80, 7});
            cout << "sample keys: preorder "; preorder(root); cout << "\\n";
            cout << "height: " << root->height << "\\n";
        }
    ''', java='''
        public class Main {
            static class Node {
                int key, height = 1;             // a new node is a leaf (node-counting convention)
                Node left, right;
                Node(int k) { key = k; }
            }

            static int height(Node n) { return n == null ? 0 : n.height; }
            static int balance(Node n) { return height(n.left) - height(n.right); }
            static void update(Node n) { n.height = 1 + Math.max(height(n.left), height(n.right)); }

            static Node rotateRight(Node x) {    // x's left child y becomes the subtree root
                Node y = x.left;
                x.left = y.right;                // T2 moves across
                y.right = x;
                update(x); update(y);            // x first: it is now below y
                return y;
            }

            static Node rotateLeft(Node x) {     // mirror image
                Node y = x.right;
                x.right = y.left;
                y.left = x;
                update(x); update(y);
                return y;
            }

            static Node insert(Node root, int key) {
                if (root == null) return new Node(key);
                if (key < root.key) root.left = insert(root.left, key);
                else if (key > root.key) root.right = insert(root.right, key);
                else return root;                                   // duplicate
                update(root);                                       // on the way back up
                int bf = balance(root);
                if (bf > 1 && key < root.left.key) return rotateRight(root);       // Left-Left
                if (bf < -1 && key > root.right.key) return rotateLeft(root);      // Right-Right
                if (bf > 1 && key > root.left.key) {                               // Left-Right
                    root.left = rotateLeft(root.left);
                    return rotateRight(root);
                }
                if (bf < -1 && key < root.right.key) {                             // Right-Left
                    root.right = rotateRight(root.right);
                    return rotateLeft(root);
                }
                return root;
            }

            static void preorder(Node root) {
                if (root == null) return;
                System.out.print(root.key + " ");
                preorder(root.left);
                preorder(root.right);
            }

            static Node build(int[] keys) {
                Node root = null;
                for (int k : keys) root = insert(root, k);
                return root;
            }

            public static void main(String[] args) {
                String[] labels = {"LL", "RR", "LR", "RL"};
                int[][] cases = {{20, 15, 5}, {100, 200, 300}, {30, 10, 20}, {10, 30, 20}};
                for (int i = 0; i < 4; i++) {
                    Node root = build(cases[i]);
                    StringBuilder sb = new StringBuilder(labels[i]);
                    for (int k : cases[i]) sb.append(" ").append(k);
                    System.out.print(sb + ": root " + root.key + ", preorder ");
                    preorder(root); System.out.println();
                }
                Node root = build(new int[]{20, 15, 30, 40, 50, 12, 18, 35, 80, 7});
                System.out.print("sample keys: preorder "); preorder(root); System.out.println();
                System.out.println("height: " + root.height);
            }
        }
    ''', js='''
        class Node {
            constructor(key) { this.key = key; this.left = null; this.right = null; this.height = 1; }
        }                                        // a new node is a leaf (node-counting convention)

        const height = (n) => n === null ? 0 : n.height;
        const balance = (n) => height(n.left) - height(n.right);
        const update = (n) => { n.height = 1 + Math.max(height(n.left), height(n.right)); };

        function rotateRight(x) {                // x's left child y becomes the subtree root
            const y = x.left;
            x.left = y.right;                    // T2 moves across
            y.right = x;
            update(x); update(y);                // x first: it is now below y
            return y;
        }

        function rotateLeft(x) {                 // mirror image
            const y = x.right;
            x.right = y.left;
            y.left = x;
            update(x); update(y);
            return y;
        }

        function insert(root, key) {
            if (root === null) return new Node(key);
            if (key < root.key) root.left = insert(root.left, key);
            else if (key > root.key) root.right = insert(root.right, key);
            else return root;                                   // duplicate
            update(root);                                       // on the way back up
            const bf = balance(root);
            if (bf > 1 && key < root.left.key) return rotateRight(root);       // Left-Left
            if (bf < -1 && key > root.right.key) return rotateLeft(root);      // Right-Right
            if (bf > 1 && key > root.left.key) {                               // Left-Right
                root.left = rotateLeft(root.left);
                return rotateRight(root);
            }
            if (bf < -1 && key < root.right.key) {                             // Right-Left
                root.right = rotateRight(root.right);
                return rotateLeft(root);
            }
            return root;
        }

        function preorder(root) {
            if (root === null) return;
            process.stdout.write(root.key + " ");
            preorder(root.left);
            preorder(root.right);
        }

        const build = (keys) => keys.reduce((root, k) => insert(root, k), null);

        for (const [label, keys] of [["LL", [20, 15, 5]], ["RR", [100, 200, 300]], ["LR", [30, 10, 20]], ["RL", [10, 30, 20]]]) {
            const root = build(keys);
            process.stdout.write(`${label} ${keys.join(" ")}: root ${root.key}, preorder `);
            preorder(root); console.log();
        }
        const root = build([20, 15, 30, 40, 50, 12, 18, 35, 80, 7]);
        process.stdout.write("sample keys: preorder "); preorder(root); console.log();
        console.log("height:", root.height);
    ''')
    yield complexity("O(log n) per insert — one path down plus at most two rotations", "O(log n) recursion stack")
    yield note("Why at most **two** rotations: after an insert, fixing the lowest unbalanced node restores that subtree to its **original height**, so no ancestor can still be unbalanced. Deletion is different — a rotation may shorten the subtree, so the fix can cascade up the whole path, `O(log n)` rotations.")
    yield pitfall("The notes wrote the AVL condition as `|lh − rh| < 1`; it is `|lh − rh| ≤ 1`. With `< 1` only perfect trees would qualify and no tree with `n = 2` nodes could exist.")

    yield section("Red-black tree", "palette")
    yield define("Red-black tree", "a BST in which every node carries one extra bit — a **colour**, red or black — and four rules on the colours keep the longest root-to-leaf path at most **twice** as long as the shortest. This guarantees `h ≤ 2 log₂(n + 1)`, so all operations are `O(log n)`.")
    yield ol(
        "Every node is either **red** or **black**.",
        "The **root** is always black.",
        "**No two consecutive reds**: a red node has only black children (a red node's parent is black).",
        "Every path from a node down to its descendant `null` leaves has the **same number of black nodes** (the *black height*).",
    )
    yield diagram('''
                         20 (B)
                      /         \\
                 15 (B)           40 (B)
                /     \\          /      \\
           12 (B)    18 (B)   30 (B)    50 (B)
           /                      \\         \\
        7 (R)                    35 (R)    80 (R)

        black nodes on every root → null path: 3   (20-15-12, 20-15-18, 20-40-30, 20-40-50, …)
        longest path: 20-15-12-7-null (4 nodes)   shortest: 20-15-18-null (3 nodes)  → ≤ 2×
    ''', "A valid red-black tree holding the sample keys — the colouring the notes drew violated rule 4, so it is redrawn here")
    yield p("**Why the rules bound the height.** Rule 4 says every path has the same number `b` of black nodes; rule 3 says reds cannot be adjacent, so a path has at most `b` reds squeezed between its blacks. The shortest possible path is all black (`b` nodes); the longest alternates (`2b` nodes). Hence *no path is more than twice as long as any other* — the statement at the end of the notes — and since a tree with `b` blacks on every path has at least `2^b − 1` nodes, `b ≤ log₂(n + 1)` and `h ≤ 2 log₂(n + 1)`.")
    yield p("Insertion colours the new node **red** (that never breaks rule 4), then fixes any red-red violation by **recolouring** and at most two rotations. Deletion is more involved but also needs at most three rotations. The code is long and rarely asked in interviews; the properties and the comparison below are.")
    yield table(
        ["", "AVL tree", "Red-black tree"],
        ["Balance rule", "`|hL − hR| ≤ 1` at every node (strict)", "Colour rules; longest path ≤ 2 × shortest (loose)"],
        ["Height bound", "`≤ 1.44 log₂ n` — shorter", "`≤ 2 log₂ n` — a bit taller"],
        ["Search", "Faster (shorter tree)", "Slightly slower"],
        ["Insert", "≤ 2 rotations, but more frequent rebalancing", "≤ 2 rotations, mostly just recolouring"],
        ["Delete", "Up to `O(log n)` rotations", "≤ 3 rotations"],
        ["Extra data per node", "Height (an int) or balance factor", "1 bit (the colour)"],
        ["Best for", "Lookup-heavy data that changes rarely (databases, dictionaries)", "Frequent inserts/deletes"],
        ["Used in", "Some database indexes, Windows kernel", "`std::map`/`set`, Java `TreeMap`/`TreeSet`, Linux scheduler (CFS) and memory manager"],
    )

    yield section("Applications of a BST", "apps")
    yield cards(
        ("Sorted dynamic data", "Keep a stream of keys sorted while they keep arriving: inorder is always sorted, insert/delete stay `O(log n)` — `std::set`, `TreeMap`.", "sort-ascending"),
        ("Double-ended priority queue", "A heap gives only the min *or* the max; a BST gives both (leftmost and rightmost) plus delete-any in `O(log n)`.", "arrows-vertical"),
        ("Floor, ceiling, nearest in a stream", "*What is the largest value ≤ x among the values seen so far?* — floor/ceiling on a self-balancing BST.", "target"),
        ("Count smaller / greater in a stream", "Augment each node with the size of its subtree; rank queries then take one walk down, `O(log n)`.", "chart-bar"),
        ("Range queries", "All keys in `[lo, hi]`: go down to `lo`, then inorder until `hi` — `O(h + k)` for `k` results.", "arrows-horizontal"),
        ("Language libraries", "C++ `map`/`set`/`multimap`/`multiset`, Java `TreeMap`/`TreeSet` are red-black trees; database B-trees are the same idea with many keys per node.", "box"),
        cols=3,
    )

    yield section("Interview Q&A", "message-question")
    yield qa("How do you check whether a binary tree is a BST?",
             "Not by comparing each node with its two children — that misses a grandchild on the wrong side. Either do an **inorder traversal** and check that the sequence is strictly increasing, or pass a valid **range** `(lo, hi)` down the recursion: the left child must be in `(lo, node.key)`, the right in `(node.key, hi)`. Both are `O(n)`.")
    yield qa("What is the worst-case complexity of search in a BST, and how do you avoid it?",
             "`O(n)`, when the tree is skewed (keys inserted in sorted order make a linked list). Avoid it with a **self-balancing** tree — AVL or red-black — which guarantees `h = O(log n)` by rotating after inserts and deletes.")
    yield qa("How do you delete a node that has two children?",
             "Replace its key with the **inorder successor** (the minimum of the right subtree) or the inorder predecessor (maximum of the left), then delete that successor from the subtree it came from. The successor has at most one child, so the second deletion is the easy case. Total `O(h)`.")
    yield qa("How do you find the kth smallest element in a BST?",
             "An inorder traversal visits keys in ascending order, so stop at the kth visited node — `O(h + k)`. If the query is frequent, store the **subtree size** in each node: at a node with `s` keys in its left subtree, go left if `k ≤ s`, return the node if `k = s + 1`, else go right with `k − s − 1`. That is `O(h)`.")
    yield qa("AVL or red-black — which would you choose?",
             "AVL for lookup-heavy workloads: its stricter balance keeps the tree shorter. Red-black for insert/delete-heavy workloads: fewer rotations per update and only one bit of extra storage. Most standard libraries (`std::map`, `TreeMap`) chose red-black.")
    yield qa("How do a BST and a hash table compare?",
             "A hash table gives `O(1)` average search/insert/delete but has no notion of order: no min/max, floor/ceiling, sorted traversal or range queries. A balanced BST gives all of those in `O(log n)` and has no worst-case collisions. Use a hash table for pure key lookups, a BST when order matters.")


@topic(G, "heap", "Binary Heap", "triangle")
def _():
    yield lead("A binary heap is a **complete binary tree stored in a plain array** in which every parent is smaller (min-heap) or larger (max-heap) than its children. It gives the minimum in `O(1)` and insert / extract-min in `O(log n)` with no pointers at all — it is the structure behind every priority queue and heap sort.")
    yield define("Binary heap", "an array `a` viewed as a complete binary tree — `a[0]` is the root, the children of `a[i]` are `a[2i + 1]` and `a[2i + 2]` — that satisfies the **heap property**: in a **min-heap** every node is ≤ its children (so the minimum is at the root); in a **max-heap** every node is ≥ its children (the maximum is at the root).")
    yield diagram('''
        index:   0     1     2     3     4     5
               ┌─────┬─────┬─────┬─────┬─────┬─────┐
               │  2  │  3  │ 15  │  5  │  4  │ 45  │        parent(i) = (i − 1) / 2
               └─────┴─────┴─────┴─────┴─────┴─────┘        left(i)   = 2i + 1
                                                            right(i)  = 2i + 2
                             2 [0]
                           /      \\
                       3 [1]       15 [2]         e.g. 15 at index 2: parent (2−1)/2 = 0 → 2
                      /    \\       /                               left 2·2+1 = 5 → 45
                  5 [3]   4 [4]  45 [5]                           right 2·2+2 = 6 → none
    ''', "A min-heap: the array is the tree, read level by level, left to right")
    yield p("Used in **heap sort** and to implement a **priority queue** — the data structure of *always give me the most urgent item*: Dijkstra's and Prim's algorithms, Huffman coding, event schedulers, the *k largest* and *running median* problems.")

    yield section("A complete binary tree stored as an array", "table")
    yield p("The array trick only works because a heap is a **complete** binary tree: every level is full except possibly the last, and that one is filled strictly from left to right. Reading such a tree level by level leaves **no gaps**, so position in the array ↔ position in the tree, and the parent/child relations become arithmetic.")
    yield diagram('''
            COMPLETE                          NOT COMPLETE
               ●                                  ●
             /   \\                              /   \\
            ●     ●                            ●     ●
           / \\                                  \\
          ●   ●                                  ●      ← the last level has a gap on its left:
                                                          index 3 would be empty while index 4 is used
        array: ● ● ● ● ●  (indices 0–4)        the array would need a hole → not a heap shape
    ''', "Every level must be filled from left to right with no gap")
    yield table(
        ["Relation", "0-based array (used here)", "1-based array (the notes' first version)"],
        ["Root", "`a[0]`", "`a[1]`"],
        ["Parent of `i`", "`(i − 1) / 2` (integer division)", "`i / 2`"],
        ["Left child of `i`", "`2i + 1`", "`2i`"],
        ["Right child of `i`", "`2i + 2`", "`2i + 1`"],
        ["Leaves", "indices `n/2 … n − 1`", "indices `n/2 + 1 … n`"],
        ["Last internal node", "`n/2 − 1`", "`n/2`"],
    )
    yield p("Because a complete tree of `n` nodes has height `⌊log₂ n⌋`, every root-to-leaf walk — which is what insert and extract do — takes `O(log n)` steps. And because there are no pointers, a heap of `n` ints is exactly `n` ints of memory, laid out contiguously and cache-friendly.")
    yield note("A heap is **not** a search structure. The heap property says nothing about the relation between the two subtrees of a node — `15` is left of `5` in the example above — so finding an arbitrary value is `O(n)`. If you need search *and* min/max, use a balanced BST.")

    yield section("Min-heap and max-heap", "arrows-sort")
    yield table(
        ["", "Min-heap", "Max-heap"],
        ["Heap property", "every node **≤** its children (and so ≤ all its descendants)", "every node **≥** its children"],
        ["Root holds", "the minimum", "the maximum"],
        ["Priority queue", "the item with the **lowest** value has the highest priority", "the item with the **highest** value has the highest priority"],
        ["Default in", "Python `heapq`, Java `PriorityQueue`", "C++ `std::priority_queue`"],
    )
    yield p("Everything below is written for a min-heap; a max-heap is the same code with every comparison flipped — or, cheaper, a min-heap of the **negated** values.")
    yield p("**Which of these are min-heaps?** (from the notes)")
    yield diagram('''
        (a)       10                        (b)        10
                /    \\                               /    \\
              20      30                           40      50
                      /                           /  \\
                    40                          44    100

        (a) NOT a heap — 40 hangs under 30 while 20 has no child, so the last level is not
            filled left to right: the tree is not complete (array would be 10 20 30 _ _ 40).
        (b) a min-heap — complete, and 10 ≤ 40, 50;  40 ≤ 44, 100.
    ''', "Both conditions are needed: the shape (complete) and the order (heap property)")

    yield section("Operations and their cost", "list-check")
    yield table(
        ["Operation", "How", "Time", "Why"],
        ["`getMin()` / `peek()`", "Return `a[0]`", "O(1)", "The root is always the minimum"],
        ["`insert(x)`", "Append at the end, then **sift up** while smaller than the parent", "O(log n)", "Climbs at most the height of the tree"],
        ["`extractMin()`", "Move the last element to the root, then **sift down** (heapify)", "O(log n)", "Descends at most the height"],
        ["`decreaseKey(i, x)`", "Lower `a[i]` to `x`, then sift up", "O(log n)", "Only the path to the root can be violated"],
        ["`delete(i)`", "`decreaseKey(i, −∞)` then `extractMin()`", "O(log n)", "Two logarithmic steps"],
        ["`buildHeap(arr)`", "Heapify every internal node from the last one up to the root", "**O(n)**", "Most nodes are near the bottom and move only a few levels"],
        ["search for a value", "Scan the array", "O(n)", "No ordering between siblings"],
    )

    yield section("Insert (sift up)", "arrow-up")
    yield io("insert 3, 2, 15, 5, 4, 45 into an empty min-heap", "array 2 3 15 5 4 45 — min 2")
    yield idea("Put the new element in the **first free slot** (`a[n]`) — that keeps the tree complete. The only thing that can now be wrong is that the new element is smaller than its parent, so **swap it upward** until its parent is smaller or it reaches the root. Each swap fixes the pair without disturbing anything else, and the walk is at most `h = ⌊log₂ n⌋` steps.")
    yield diagram('''
        insert 2 into [3]:          append at the end        2 < parent 3: swap

              3          ──────▶         3          ──────▶         2
                                        /                          /
                                       2                          3

        insert 4 into [2, 3, 15, 5]:  append at index 4; parent is index 1 (3) ≤ 4 → stop

              2                       2
            /   \\       ──────▶     /   \\
           3     15                3     15        array: 2 3 15 5 4
          /                       / \\
         5                       5   4
    ''', "Sift up: compare with the parent, swap while smaller")
    yield multi('''
        insert 3: 3
        insert 2: 2 3
        insert 15: 2 3 15
        insert 5: 2 3 15 5
        insert 4: 2 3 15 5 4
        insert 45: 2 3 15 5 4 45
        min: 2
    ''', py='''
        class MinHeap:
            def __init__(self):
                self.a = []

            def parent(self, i):
                return (i - 1) // 2

            def insert(self, x):
                a = self.a
                a.append(x)                              # 1. first free slot: tree stays complete
                i = len(a) - 1
                while i > 0 and a[self.parent(i)] > a[i]:   # 2. sift up while the parent is larger
                    p = self.parent(i)
                    a[i], a[p] = a[p], a[i]
                    i = p

            def get_min(self):
                return self.a[0]

        h = MinHeap()
        for x in (3, 2, 15, 5, 4, 45):
            h.insert(x)
            print(f"insert {x}:", *h.a)
        print("min:", h.get_min())
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        class MinHeap {
            vector<int> a;
        public:
            int parent(int i) { return (i - 1) / 2; }

            void insert(int x) {
                a.push_back(x);                              // 1. first free slot: tree stays complete
                int i = (int)a.size() - 1;
                while (i > 0 && a[parent(i)] > a[i]) {       // 2. sift up while the parent is larger
                    swap(a[i], a[parent(i)]);
                    i = parent(i);
                }
            }

            int getMin() { return a[0]; }
            void print() { for (int x : a) cout << x << " "; cout << "\\n"; }
        };

        int main() {
            MinHeap h;
            for (int x : {3, 2, 15, 5, 4, 45}) {
                h.insert(x);
                cout << "insert " << x << ": "; h.print();
            }
            cout << "min: " << h.getMin() << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;

        public class Main {
            static class MinHeap {
                ArrayList<Integer> a = new ArrayList<>();

                int parent(int i) { return (i - 1) / 2; }

                void swap(int i, int j) { int t = a.get(i); a.set(i, a.get(j)); a.set(j, t); }

                void insert(int x) {
                    a.add(x);                                    // 1. first free slot: tree stays complete
                    int i = a.size() - 1;
                    while (i > 0 && a.get(parent(i)) > a.get(i)) {   // 2. sift up while the parent is larger
                        swap(i, parent(i));
                        i = parent(i);
                    }
                }

                int getMin() { return a.get(0); }
                void print() { StringBuilder sb = new StringBuilder(); for (int x : a) sb.append(x).append(' '); System.out.println(sb.toString().trim()); }
            }

            public static void main(String[] args) {
                MinHeap h = new MinHeap();
                for (int x : new int[]{3, 2, 15, 5, 4, 45}) {
                    h.insert(x);
                    System.out.print("insert " + x + ": "); h.print();
                }
                System.out.println("min: " + h.getMin());
            }
        }
    ''', js='''
        class MinHeap {
            constructor() { this.a = []; }

            parent(i) { return Math.floor((i - 1) / 2); }

            insert(x) {
                const a = this.a;
                a.push(x);                                   // 1. first free slot: tree stays complete
                let i = a.length - 1;
                while (i > 0 && a[this.parent(i)] > a[i]) {  // 2. sift up while the parent is larger
                    const p = this.parent(i);
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }

            getMin() { return this.a[0]; }
        }

        const h = new MinHeap();
        for (const x of [3, 2, 15, 5, 4, 45]) {
            h.insert(x);
            console.log(`insert ${x}:`, h.a.join(" "));
        }
        console.log("min:", h.getMin());
    ''')
    yield complexity("O(log n)", "O(1)")
    yield pitfall("In JavaScript `(i - 1) / 2` is a **float** — `Math.floor` is required. In Python use `//`. Forgetting this gives fractional indices and a heap that silently never sifts.")

    yield section("Extract min (sift down / heapify)", "arrow-down")
    yield io("the heap 2 3 15 5 4 45", "returns 2; heap becomes 3 4 15 5 45", "extract again", "returns 3; heap becomes 4 5 15 45")
    yield idea("The minimum is the root, but removing the root leaves a hole at the top and a complete tree can only lose its **last** slot. So: save `a[0]`, move the **last** element into the root, shrink the array by one. The only violation now is at the root, which may be larger than a child — **sift it down**: swap it with the *smaller* of its two children (so the new parent is ≤ both) and repeat from there until it is ≤ both children or becomes a leaf. This repair step is `minHeapify(i)` — it assumes both subtrees of `i` are valid heaps and fixes node `i`.")
    yield diagram('''
        heap 2 3 15 5 4 45        take out 2,        heapify(0): smaller child of 45    heapify(1): smaller child
                                  move 45 to root     is 3 → swap                        of 45 is 4 → swap
               2                       45                      3                              3
             /   \\                   /    \\                  /   \\                          /   \\
            3     15                3      15              45     15                       4     15
           / \\   /                 / \\                    / \\                            / \\
          5   4 45                5   4                   5   4                          5   45

        returned 2;  heap is now 3 4 15 5 45
    ''', "Extract-min moves the last element to the root and sifts it down along one path")
    yield multi('''
        heap: 2 3 15 5 4 45
        extract min: 2
        heap: 3 4 15 5 45
        extract min: 3
        heap: 4 5 15 45
    ''', py='''
        class MinHeap:
            def __init__(self):
                self.a = []

            def parent(self, i): return (i - 1) // 2
            def left(self, i): return 2 * i + 1
            def right(self, i): return 2 * i + 2

            def insert(self, x):
                a = self.a
                a.append(x)
                i = len(a) - 1
                while i > 0 and a[self.parent(i)] > a[i]:
                    p = self.parent(i)
                    a[i], a[p] = a[p], a[i]
                    i = p

            def min_heapify(self, i):            # subtrees of i are heaps; fix node i
                a, n = self.a, len(self.a)
                l, r, smallest = self.left(i), self.right(i), i
                if l < n and a[l] < a[smallest]:
                    smallest = l
                if r < n and a[r] < a[smallest]:
                    smallest = r
                if smallest != i:                # a child is smaller: swap and continue below
                    a[i], a[smallest] = a[smallest], a[i]
                    self.min_heapify(smallest)

            def extract_min(self):
                a = self.a
                if not a:
                    return None
                res = a[0]                       # 1. the answer is the root
                a[0] = a[-1]                     # 2. last element moves to the root
                a.pop()
                if a:
                    self.min_heapify(0)          # 3. sift it down
                return res

        h = MinHeap()
        for x in (3, 2, 15, 5, 4, 45):
            h.insert(x)
        print("heap:", *h.a)
        print("extract min:", h.extract_min())
        print("heap:", *h.a)
        print("extract min:", h.extract_min())
        print("heap:", *h.a)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        class MinHeap {
            vector<int> a;
            int parent(int i) { return (i - 1) / 2; }
            int left(int i) { return 2 * i + 1; }
            int right(int i) { return 2 * i + 2; }
        public:
            void insert(int x) {
                a.push_back(x);
                int i = (int)a.size() - 1;
                while (i > 0 && a[parent(i)] > a[i]) { swap(a[i], a[parent(i)]); i = parent(i); }
            }

            void minHeapify(int i) {                     // subtrees of i are heaps; fix node i
                int n = (int)a.size();
                int l = left(i), r = right(i), smallest = i;
                if (l < n && a[l] < a[smallest]) smallest = l;
                if (r < n && a[r] < a[smallest]) smallest = r;
                if (smallest != i) {                     // a child is smaller: swap and continue below
                    swap(a[i], a[smallest]);
                    minHeapify(smallest);
                }
            }

            int extractMin() {
                int res = a[0];                          // 1. the answer is the root
                a[0] = a.back();                         // 2. last element moves to the root
                a.pop_back();
                if (!a.empty()) minHeapify(0);           // 3. sift it down
                return res;
            }

            void print() { cout << "heap: "; for (int x : a) cout << x << " "; cout << "\\n"; }
        };

        int main() {
            MinHeap h;
            for (int x : {3, 2, 15, 5, 4, 45}) h.insert(x);
            h.print();
            cout << "extract min: " << h.extractMin() << "\\n";
            h.print();
            cout << "extract min: " << h.extractMin() << "\\n";
            h.print();
        }
    ''', java='''
        import java.util.ArrayList;

        public class Main {
            static class MinHeap {
                ArrayList<Integer> a = new ArrayList<>();
                int parent(int i) { return (i - 1) / 2; }
                int left(int i) { return 2 * i + 1; }
                int right(int i) { return 2 * i + 2; }
                void swap(int i, int j) { int t = a.get(i); a.set(i, a.get(j)); a.set(j, t); }

                void insert(int x) {
                    a.add(x);
                    int i = a.size() - 1;
                    while (i > 0 && a.get(parent(i)) > a.get(i)) { swap(i, parent(i)); i = parent(i); }
                }

                void minHeapify(int i) {                     // subtrees of i are heaps; fix node i
                    int n = a.size();
                    int l = left(i), r = right(i), smallest = i;
                    if (l < n && a.get(l) < a.get(smallest)) smallest = l;
                    if (r < n && a.get(r) < a.get(smallest)) smallest = r;
                    if (smallest != i) {                     // a child is smaller: swap and continue below
                        swap(i, smallest);
                        minHeapify(smallest);
                    }
                }

                int extractMin() {
                    int res = a.get(0);                      // 1. the answer is the root
                    a.set(0, a.get(a.size() - 1));           // 2. last element moves to the root
                    a.remove(a.size() - 1);
                    if (!a.isEmpty()) minHeapify(0);         // 3. sift it down
                    return res;
                }

                void print() { StringBuilder sb = new StringBuilder("heap:"); for (int x : a) sb.append(' ').append(x); System.out.println(sb); }
            }

            public static void main(String[] args) {
                MinHeap h = new MinHeap();
                for (int x : new int[]{3, 2, 15, 5, 4, 45}) h.insert(x);
                h.print();
                System.out.println("extract min: " + h.extractMin());
                h.print();
                System.out.println("extract min: " + h.extractMin());
                h.print();
            }
        }
    ''', js='''
        class MinHeap {
            constructor() { this.a = []; }
            parent(i) { return Math.floor((i - 1) / 2); }
            left(i) { return 2 * i + 1; }
            right(i) { return 2 * i + 2; }

            insert(x) {
                const a = this.a;
                a.push(x);
                let i = a.length - 1;
                while (i > 0 && a[this.parent(i)] > a[i]) {
                    const p = this.parent(i);
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }

            minHeapify(i) {                              // subtrees of i are heaps; fix node i
                const a = this.a, n = a.length;
                const l = this.left(i), r = this.right(i);
                let smallest = i;
                if (l < n && a[l] < a[smallest]) smallest = l;
                if (r < n && a[r] < a[smallest]) smallest = r;
                if (smallest !== i) {                    // a child is smaller: swap and continue below
                    [a[i], a[smallest]] = [a[smallest], a[i]];
                    this.minHeapify(smallest);
                }
            }

            extractMin() {
                const a = this.a;
                if (a.length === 0) return null;
                const res = a[0];                        // 1. the answer is the root
                a[0] = a[a.length - 1];                  // 2. last element moves to the root
                a.pop();
                if (a.length) this.minHeapify(0);        // 3. sift it down
                return res;
            }
        }

        const h = new MinHeap();
        for (const x of [3, 2, 15, 5, 4, 45]) h.insert(x);
        console.log("heap:", h.a.join(" "));
        console.log("extract min:", h.extractMin());
        console.log("heap:", h.a.join(" "));
        console.log("extract min:", h.extractMin());
        console.log("heap:", h.a.join(" "));
    ''')
    yield complexity("O(log n)", "O(log n) for the recursive heapify — O(1) if written as a loop")
    yield pitfall("`minHeapify` must swap with the **smaller** child, not just any smaller child. Swapping with the larger one puts it above its sibling and breaks the heap property. Also check `l < n` / `r < n` before reading — the notes' first version read `a[rightChild]` past the end when a node had only a left child.")

    yield section("Decrease key and delete", "adjustments")
    yield io("the heap 2 3 15 5 4 45; decreaseKey(index 2, 1)", "15 becomes 1 and rises to the root: 1 3 2 5 4 45", "then delete(index 1)", "the value 3 is removed: 1 4 2 5 45")
    yield idea("**Decrease key** lowers one value. A smaller value can only violate the heap property with its *parent*, so the fix is the same sift-up as insert. **Delete at index i** needs no new mechanism: decrease the key to `−∞` so it rises to the root, then `extractMin()` throws it away. Both are `O(log n)`. (*Increase key* would be the mirror: set the value, then `minHeapify(i)`.)")
    yield multi('''
        heap: 2 3 15 5 4 45
        decrease key at index 2 (15 -> 1): 1 3 2 5 4 45
        delete index 1 (value 3): 1 4 2 5 45
        min: 1
    ''', py='''
        import math

        class MinHeap:
            def __init__(self):
                self.a = []

            def parent(self, i): return (i - 1) // 2

            def sift_up(self, i):                    # shared by insert and decrease_key
                a = self.a
                while i > 0 and a[self.parent(i)] > a[i]:
                    p = self.parent(i)
                    a[i], a[p] = a[p], a[i]
                    i = p

            def insert(self, x):
                self.a.append(x)
                self.sift_up(len(self.a) - 1)

            def min_heapify(self, i):
                a, n = self.a, len(self.a)
                l, r, smallest = 2 * i + 1, 2 * i + 2, i
                if l < n and a[l] < a[smallest]: smallest = l
                if r < n and a[r] < a[smallest]: smallest = r
                if smallest != i:
                    a[i], a[smallest] = a[smallest], a[i]
                    self.min_heapify(smallest)

            def extract_min(self):
                a = self.a
                res = a[0]
                a[0] = a[-1]
                a.pop()
                if a:
                    self.min_heapify(0)
                return res

            def decrease_key(self, i, x):            # x must be <= a[i]
                self.a[i] = x
                self.sift_up(i)                      # only the path to the root can be wrong

            def delete(self, i):
                self.decrease_key(i, -math.inf)      # 1. send it to the root ...
                self.extract_min()                   # 2. ... and remove the root

        h = MinHeap()
        for x in (3, 2, 15, 5, 4, 45):
            h.insert(x)
        print("heap:", *h.a)
        h.decrease_key(2, 1)
        print("decrease key at index 2 (15 -> 1):", *h.a)
        h.delete(1)
        print("delete index 1 (value 3):", *h.a)
        print("min:", h.a[0])
    ''', cpp='''
        #include <climits>
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        class MinHeap {
            vector<int> a;
            int parent(int i) { return (i - 1) / 2; }

            void siftUp(int i) {                         // shared by insert and decreaseKey
                while (i > 0 && a[parent(i)] > a[i]) { swap(a[i], a[parent(i)]); i = parent(i); }
            }

            void minHeapify(int i) {
                int n = (int)a.size();
                int l = 2 * i + 1, r = 2 * i + 2, smallest = i;
                if (l < n && a[l] < a[smallest]) smallest = l;
                if (r < n && a[r] < a[smallest]) smallest = r;
                if (smallest != i) { swap(a[i], a[smallest]); minHeapify(smallest); }
            }
        public:
            void insert(int x) { a.push_back(x); siftUp((int)a.size() - 1); }

            int extractMin() {
                int res = a[0];
                a[0] = a.back();
                a.pop_back();
                if (!a.empty()) minHeapify(0);
                return res;
            }

            void decreaseKey(int i, int x) {             // x must be <= a[i]
                a[i] = x;
                siftUp(i);                               // only the path to the root can be wrong
            }

            void erase(int i) {                          // "delete" is a keyword in C++
                decreaseKey(i, INT_MIN);                 // 1. send it to the root ...
                extractMin();                            // 2. ... and remove the root
            }

            int getMin() { return a[0]; }
            void print() { for (int x : a) cout << x << " "; cout << "\\n"; }
        };

        int main() {
            MinHeap h;
            for (int x : {3, 2, 15, 5, 4, 45}) h.insert(x);
            cout << "heap: "; h.print();
            h.decreaseKey(2, 1);
            cout << "decrease key at index 2 (15 -> 1): "; h.print();
            h.erase(1);
            cout << "delete index 1 (value 3): "; h.print();
            cout << "min: " << h.getMin() << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;

        public class Main {
            static class MinHeap {
                ArrayList<Integer> a = new ArrayList<>();
                int parent(int i) { return (i - 1) / 2; }
                void swap(int i, int j) { int t = a.get(i); a.set(i, a.get(j)); a.set(j, t); }

                void siftUp(int i) {                         // shared by insert and decreaseKey
                    while (i > 0 && a.get(parent(i)) > a.get(i)) { swap(i, parent(i)); i = parent(i); }
                }

                void minHeapify(int i) {
                    int n = a.size();
                    int l = 2 * i + 1, r = 2 * i + 2, smallest = i;
                    if (l < n && a.get(l) < a.get(smallest)) smallest = l;
                    if (r < n && a.get(r) < a.get(smallest)) smallest = r;
                    if (smallest != i) { swap(i, smallest); minHeapify(smallest); }
                }

                void insert(int x) { a.add(x); siftUp(a.size() - 1); }

                int extractMin() {
                    int res = a.get(0);
                    a.set(0, a.get(a.size() - 1));
                    a.remove(a.size() - 1);
                    if (!a.isEmpty()) minHeapify(0);
                    return res;
                }

                void decreaseKey(int i, int x) {             // x must be <= a[i]
                    a.set(i, x);
                    siftUp(i);                               // only the path to the root can be wrong
                }

                void delete(int i) {
                    decreaseKey(i, Integer.MIN_VALUE);       // 1. send it to the root ...
                    extractMin();                            // 2. ... and remove the root
                }

                String show() { StringBuilder sb = new StringBuilder(); for (int x : a) sb.append(x).append(' '); return sb.toString().trim(); }
            }

            public static void main(String[] args) {
                MinHeap h = new MinHeap();
                for (int x : new int[]{3, 2, 15, 5, 4, 45}) h.insert(x);
                System.out.println("heap: " + h.show());
                h.decreaseKey(2, 1);
                System.out.println("decrease key at index 2 (15 -> 1): " + h.show());
                h.delete(1);
                System.out.println("delete index 1 (value 3): " + h.show());
                System.out.println("min: " + h.a.get(0));
            }
        }
    ''', js='''
        class MinHeap {
            constructor() { this.a = []; }
            parent(i) { return Math.floor((i - 1) / 2); }

            siftUp(i) {                                  // shared by insert and decreaseKey
                const a = this.a;
                while (i > 0 && a[this.parent(i)] > a[i]) {
                    const p = this.parent(i);
                    [a[i], a[p]] = [a[p], a[i]];
                    i = p;
                }
            }

            insert(x) { this.a.push(x); this.siftUp(this.a.length - 1); }

            minHeapify(i) {
                const a = this.a, n = a.length;
                const l = 2 * i + 1, r = 2 * i + 2;
                let smallest = i;
                if (l < n && a[l] < a[smallest]) smallest = l;
                if (r < n && a[r] < a[smallest]) smallest = r;
                if (smallest !== i) { [a[i], a[smallest]] = [a[smallest], a[i]]; this.minHeapify(smallest); }
            }

            extractMin() {
                const a = this.a;
                const res = a[0];
                a[0] = a[a.length - 1];
                a.pop();
                if (a.length) this.minHeapify(0);
                return res;
            }

            decreaseKey(i, x) {                          // x must be <= a[i]
                this.a[i] = x;
                this.siftUp(i);                          // only the path to the root can be wrong
            }

            delete(i) {
                this.decreaseKey(i, -Infinity);          // 1. send it to the root ...
                this.extractMin();                       // 2. ... and remove the root
            }
        }

        const h = new MinHeap();
        for (const x of [3, 2, 15, 5, 4, 45]) h.insert(x);
        console.log("heap:", h.a.join(" "));
        h.decreaseKey(2, 1);
        console.log("decrease key at index 2 (15 -> 1):", h.a.join(" "));
        h.delete(1);
        console.log("delete index 1 (value 3):", h.a.join(" "));
        console.log("min:", h.a[0]);
    ''')
    yield complexity("O(log n) each", "O(1)")
    yield note("`decreaseKey` is what Dijkstra's algorithm needs when a shorter path to a vertex is found. It requires knowing the **index** of the element, which the array can only provide with an extra `value → index` map; the library priority queues below do not offer it, so Dijkstra implementations usually push a fresh entry instead (*lazy deletion*).")
    yield pitfall("The notes' second implementation had two typos that make it silently wrong: `lchild` returned `2 * 1 + 1` (always 3) instead of `2 * i + 1`, and `decreasekey` compared `arr[self.parent(i) > arr[i]]` — indexing with a boolean — instead of `arr[self.parent(i)] > arr[i]`. Running the code with a known heap and checking the array after every operation, as above, catches both.")

    yield section("Build heap in O(n)", "building")
    yield io("arr = 40 10 30 50 20 15", "min-heap 10 20 15 50 40 30")
    yield idea("Inserting `n` elements one by one costs `O(n log n)`. Building **bottom-up** is faster: the leaves (indices `n/2 … n − 1`) are already one-node heaps, so call `minHeapify(i)` for `i = n/2 − 1` down to `0`. Each call assumes both subtrees are heaps — true, because every index below `i` was fixed first — and repairs node `i` by sifting it down.")
    yield diagram('''
       arr = 40 10 30 50 20 15        n = 6, last internal node = 6/2 − 1 = 2

                 40 [0]            heapify(2): 30 vs child 15 → swap        40
               /       \\                                                  /    \\
           10 [1]      30 [2]      heapify(1): 10 ≤ 50, 20 → nothing      10     15
           /   \\       /                                                 / \\    /
       50 [3] 20 [4] 15 [5]        heapify(0): 40 vs 10, 15 → swap 10   50  20  30
                                       then 40 vs 50, 20 → swap 20
       result: 10 20 15 50 40 30
    ''', "Build-heap fixes the internal nodes from the bottom up; each sift-down only goes as far as it must")
    yield p("**Why `O(n)` and not `O(n log n)`.** A node at height `h` (leaves at height 0) sifts down at most `h` steps, and there are at most `n / 2^(h+1)` nodes at that height. Total work is `Σ h · n / 2^(h+1) = n · Σ h / 2^(h+1) ≤ n · 1 = O(n)` — half the nodes are leaves and cost nothing, a quarter move at most one level, and so on. The `O(n log n)` bound counts `log n` for every node, which is far too pessimistic.")
    yield multi('''
        build heap from 40 10 30 50 20 15: 10 20 15 50 40 30
        extract all: 10 15 20 30 40 50
    ''', py='''
        def min_heapify(a, n, i):                # fix node i, given that its subtrees are heaps
            l, r, smallest = 2 * i + 1, 2 * i + 2, i
            if l < n and a[l] < a[smallest]: smallest = l
            if r < n and a[r] < a[smallest]: smallest = r
            if smallest != i:
                a[i], a[smallest] = a[smallest], a[i]
                min_heapify(a, n, smallest)

        def build_heap(a):
            n = len(a)
            for i in range(n // 2 - 1, -1, -1):  # last internal node down to the root
                min_heapify(a, n, i)

        def extract_min(a):
            res = a[0]
            a[0] = a[-1]
            a.pop()
            if a:
                min_heapify(a, len(a), 0)
            return res

        a = [40, 10, 30, 50, 20, 15]
        build_heap(a)
        print("build heap from 40 10 30 50 20 15:", *a)
        out = []
        while a:
            out.append(extract_min(a))
        print("extract all:", *out)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        void minHeapify(vector<int>& a, int n, int i) {   // fix node i, given that its subtrees are heaps
            int l = 2 * i + 1, r = 2 * i + 2, smallest = i;
            if (l < n && a[l] < a[smallest]) smallest = l;
            if (r < n && a[r] < a[smallest]) smallest = r;
            if (smallest != i) {
                swap(a[i], a[smallest]);
                minHeapify(a, n, smallest);
            }
        }

        void buildHeap(vector<int>& a) {
            int n = (int)a.size();
            for (int i = n / 2 - 1; i >= 0; i--)          // last internal node down to the root
                minHeapify(a, n, i);
        }

        int extractMin(vector<int>& a) {
            int res = a[0];
            a[0] = a.back();
            a.pop_back();
            if (!a.empty()) minHeapify(a, (int)a.size(), 0);
            return res;
        }

        int main() {
            vector<int> a = {40, 10, 30, 50, 20, 15};
            buildHeap(a);
            cout << "build heap from 40 10 30 50 20 15:";
            for (int x : a) cout << " " << x;
            cout << "\\nextract all:";
            while (!a.empty()) cout << " " << extractMin(a);
            cout << "\\n";
        }
    ''', java='''
        import java.util.ArrayList;
        import java.util.Arrays;

        public class Main {
            static void minHeapify(ArrayList<Integer> a, int n, int i) {   // fix node i, given that its subtrees are heaps
                int l = 2 * i + 1, r = 2 * i + 2, smallest = i;
                if (l < n && a.get(l) < a.get(smallest)) smallest = l;
                if (r < n && a.get(r) < a.get(smallest)) smallest = r;
                if (smallest != i) {
                    int t = a.get(i); a.set(i, a.get(smallest)); a.set(smallest, t);
                    minHeapify(a, n, smallest);
                }
            }

            static void buildHeap(ArrayList<Integer> a) {
                int n = a.size();
                for (int i = n / 2 - 1; i >= 0; i--)          // last internal node down to the root
                    minHeapify(a, n, i);
            }

            static int extractMin(ArrayList<Integer> a) {
                int res = a.get(0);
                a.set(0, a.get(a.size() - 1));
                a.remove(a.size() - 1);
                if (!a.isEmpty()) minHeapify(a, a.size(), 0);
                return res;
            }

            public static void main(String[] args) {
                ArrayList<Integer> a = new ArrayList<>(Arrays.asList(40, 10, 30, 50, 20, 15));
                buildHeap(a);
                StringBuilder sb = new StringBuilder("build heap from 40 10 30 50 20 15:");
                for (int x : a) sb.append(' ').append(x);
                System.out.println(sb);
                sb = new StringBuilder("extract all:");
                while (!a.isEmpty()) sb.append(' ').append(extractMin(a));
                System.out.println(sb);
            }
        }
    ''', js='''
        function minHeapify(a, n, i) {               // fix node i, given that its subtrees are heaps
            const l = 2 * i + 1, r = 2 * i + 2;
            let smallest = i;
            if (l < n && a[l] < a[smallest]) smallest = l;
            if (r < n && a[r] < a[smallest]) smallest = r;
            if (smallest !== i) {
                [a[i], a[smallest]] = [a[smallest], a[i]];
                minHeapify(a, n, smallest);
            }
        }

        function buildHeap(a) {
            const n = a.length;
            for (let i = Math.floor(n / 2) - 1; i >= 0; i--)   // last internal node down to the root
                minHeapify(a, n, i);
        }

        function extractMin(a) {
            const res = a[0];
            a[0] = a[a.length - 1];
            a.pop();
            if (a.length) minHeapify(a, a.length, 0);
            return res;
        }

        const a = [40, 10, 30, 50, 20, 15];
        buildHeap(a);
        console.log("build heap from 40 10 30 50 20 15:", a.join(" "));
        const out = [];
        while (a.length) out.push(extractMin(a));
        console.log("extract all:", out.join(" "));
    ''')
    yield complexity("O(n) to build; O(n log n) to extract everything", "O(1) extra (in place)")
    yield note("*Build heap, then extract everything* is already a sorting algorithm — the extraction order is ascending. Heap sort below does the same thing **in place**, without a second array, by using a max-heap.")

    yield section("Heap sort", "sort-ascending")
    yield io("arr = 40 10 30 50 20 15", "10 15 20 30 40 50")
    yield idea("Build a **max-heap** in place (`O(n)`). The maximum is now at `a[0]`; swap it with the last element so it sits in its final sorted position, shrink the heap by one and `maxHeapify(0)` to restore the heap on the remaining prefix. Repeat `n − 1` times: each round places one more element at the end, so the sorted suffix grows while the heap prefix shrinks — all inside the same array.")
    yield steps(
        ("Build max-heap", "`for i = n/2 − 1 … 0: maxHeapify(a, n, i)` — the largest element is at `a[0]`."),
        ("Repeat for `end = n − 1 … 1`", "Swap `a[0]` and `a[end]` (the max is now in place), then `maxHeapify(a, end, 0)` on the prefix of length `end`."),
        ("Done", "The prefix shrinks to one element; the array is sorted ascending."),
    )
    yield diagram('''
        max-heap:  50 40 30 10 20 15   | sorted suffix
        swap 50 ↔ 15, heapify prefix:  40 20 30 10 15 | 50
        swap 40 ↔ 15, heapify prefix:  30 20 15 10 | 40 50
        swap 30 ↔ 10, heapify prefix:  20 10 15 | 30 40 50
        swap 20 ↔ 15, heapify prefix:  15 10 | 20 30 40 50
        swap 15 ↔ 10:                  10 | 15 20 30 40 50
    ''', "Each round moves the current maximum to the front of the sorted suffix")
    yield multi('''
        max-heap: 50 40 30 10 20 15
        sorted: 10 15 20 30 40 50
    ''', py='''
        def max_heapify(a, n, i):
            l, r, largest = 2 * i + 1, 2 * i + 2, i
            if l < n and a[l] > a[largest]: largest = l
            if r < n and a[r] > a[largest]: largest = r
            if largest != i:
                a[i], a[largest] = a[largest], a[i]
                max_heapify(a, n, largest)

        def heap_sort(a):
            n = len(a)
            for i in range(n // 2 - 1, -1, -1):          # 1. build max-heap: O(n)
                max_heapify(a, n, i)
            print("max-heap:", *a)
            for end in range(n - 1, 0, -1):              # 2. n − 1 rounds
                a[0], a[end] = a[end], a[0]              #    max goes to its final place
                max_heapify(a, end, 0)                   #    restore the heap on a[0..end)

        a = [40, 10, 30, 50, 20, 15]
        heap_sort(a)
        print("sorted:", *a)
    ''', cpp='''
        #include <iostream>
        #include <utility>
        #include <vector>
        using namespace std;

        void maxHeapify(vector<int>& a, int n, int i) {
            int l = 2 * i + 1, r = 2 * i + 2, largest = i;
            if (l < n && a[l] > a[largest]) largest = l;
            if (r < n && a[r] > a[largest]) largest = r;
            if (largest != i) { swap(a[i], a[largest]); maxHeapify(a, n, largest); }
        }

        void print(const char* label, const vector<int>& a) {
            cout << label; for (int x : a) cout << " " << x; cout << "\\n";
        }

        void heapSort(vector<int>& a) {
            int n = (int)a.size();
            for (int i = n / 2 - 1; i >= 0; i--) maxHeapify(a, n, i);   // 1. build max-heap: O(n)
            print("max-heap:", a);
            for (int end = n - 1; end > 0; end--) {                    // 2. n − 1 rounds
                swap(a[0], a[end]);                                    //    max goes to its final place
                maxHeapify(a, end, 0);                                 //    restore the heap on a[0..end)
            }
        }

        int main() {
            vector<int> a = {40, 10, 30, 50, 20, 15};
            heapSort(a);
            print("sorted:", a);
        }
    ''', java='''
        public class Main {
            static void maxHeapify(int[] a, int n, int i) {
                int l = 2 * i + 1, r = 2 * i + 2, largest = i;
                if (l < n && a[l] > a[largest]) largest = l;
                if (r < n && a[r] > a[largest]) largest = r;
                if (largest != i) {
                    int t = a[i]; a[i] = a[largest]; a[largest] = t;
                    maxHeapify(a, n, largest);
                }
            }

            static void print(String label, int[] a) {
                StringBuilder sb = new StringBuilder(label);
                for (int x : a) sb.append(' ').append(x);
                System.out.println(sb);
            }

            static void heapSort(int[] a) {
                int n = a.length;
                for (int i = n / 2 - 1; i >= 0; i--) maxHeapify(a, n, i);   // 1. build max-heap: O(n)
                print("max-heap:", a);
                for (int end = n - 1; end > 0; end--) {                    // 2. n − 1 rounds
                    int t = a[0]; a[0] = a[end]; a[end] = t;               //    max goes to its final place
                    maxHeapify(a, end, 0);                                 //    restore the heap on a[0..end)
                }
            }

            public static void main(String[] args) {
                int[] a = {40, 10, 30, 50, 20, 15};
                heapSort(a);
                print("sorted:", a);
            }
        }
    ''', js='''
        function maxHeapify(a, n, i) {
            const l = 2 * i + 1, r = 2 * i + 2;
            let largest = i;
            if (l < n && a[l] > a[largest]) largest = l;
            if (r < n && a[r] > a[largest]) largest = r;
            if (largest !== i) {
                [a[i], a[largest]] = [a[largest], a[i]];
                maxHeapify(a, n, largest);
            }
        }

        function heapSort(a) {
            const n = a.length;
            for (let i = Math.floor(n / 2) - 1; i >= 0; i--) maxHeapify(a, n, i);   // 1. build max-heap: O(n)
            console.log("max-heap:", a.join(" "));
            for (let end = n - 1; end > 0; end--) {                                // 2. n − 1 rounds
                [a[0], a[end]] = [a[end], a[0]];                                   //    max goes to its final place
                maxHeapify(a, end, 0);                                             //    restore the heap on a[0..end)
            }
        }

        const a = [40, 10, 30, 50, 20, 15];
        heapSort(a);
        console.log("sorted:", a.join(" "));
    ''')
    yield complexity("O(n log n) always — no bad input", "O(1) extra (in place; O(log n) stack if heapify is recursive)")
    yield table(
        ["", "Heap sort", "Merge sort", "Quick sort"],
        ["Worst case", "`O(n log n)`", "`O(n log n)`", "`O(n²)`"],
        ["Extra space", "`O(1)`", "`O(n)`", "`O(log n)` stack"],
        ["Stable", "No", "Yes", "No"],
        ["In practice", "Slower (poor cache locality: jumps across the array)", "Fast, used for linked lists and external sorting", "Fastest on arrays; libraries use introsort = quick sort that falls back to heap sort"],
    )

    yield section("Built-in priority queues", "box")
    yield p("You will rarely write a heap by hand outside an interview. Every language but JavaScript ships one; the API is always *push*, *pop the best*, *peek*.")
    yield table(
        ["Language", "Priority queue", "Default order", "push / pop / peek", "Max-heap instead"],
        ["Python", "`heapq` — functions on a plain list", "**min**-heap", "`heappush(h, x)` / `heappop(h)` / `h[0]`", "push `-x`, or `(−priority, item)` tuples"],
        ["C++", "`std::priority_queue<T>`", "**max**-heap", "`push(x)` / `pop()` (returns nothing) / `top()`", "it is max by default; min: `priority_queue<int, vector<int>, greater<int>>`"],
        ["Java", "`java.util.PriorityQueue<T>`", "**min**-heap", "`offer(x)` / `poll()` / `peek()`", "`new PriorityQueue<>(Collections.reverseOrder())`"],
        ["JavaScript", "— none built in", "", "write a `MinHeap` class (below) or use a library", ""],
    )
    yield io("start from 5 20 1 30 4; push 3; pop everything", "min 1; popped order 1 3 4 5 20 30")
    yield multi('''
        min: 1
        after push 3, min: 1
        popped in order: 1 3 4 5 20 30
    ''', py='''
        import heapq

        h = [5, 20, 1, 30, 4]
        heapq.heapify(h)                     # O(n) build, in place
        print("min:", h[0])
        heapq.heappush(h, 3)                 # O(log n)
        print("after push 3, min:", h[0])
        out = []
        while h:
            out.append(heapq.heappop(h))     # O(log n) each
        print("popped in order:", *out)
    ''', cpp='''
        #include <functional>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        int main() {
            vector<int> v = {5, 20, 1, 30, 4};
            priority_queue<int, vector<int>, greater<int>> pq(v.begin(), v.end());   // min-heap; O(n) build
            cout << "min: " << pq.top() << "\\n";
            pq.push(3);                                                             // O(log n)
            cout << "after push 3, min: " << pq.top() << "\\n";
            cout << "popped in order:";
            while (!pq.empty()) { cout << " " << pq.top(); pq.pop(); }              // O(log n) each
            cout << "\\n";
        }
    ''', java='''
        import java.util.Arrays;
        import java.util.PriorityQueue;

        public class Main {
            public static void main(String[] args) {
                PriorityQueue<Integer> pq = new PriorityQueue<>(Arrays.asList(5, 20, 1, 30, 4));   // min-heap
                System.out.println("min: " + pq.peek());
                pq.offer(3);                                                         // O(log n)
                System.out.println("after push 3, min: " + pq.peek());
                StringBuilder sb = new StringBuilder("popped in order:");
                while (!pq.isEmpty()) sb.append(' ').append(pq.poll());              // O(log n) each
                System.out.println(sb);
            }
        }
    ''', js='''
        class MinHeap {                          // JavaScript has no built-in priority queue
            constructor(items = []) { this.a = [...items]; for (let i = (this.a.length >> 1) - 1; i >= 0; i--) this.down(i); }
            size() { return this.a.length; }
            peek() { return this.a[0]; }
            push(x) { this.a.push(x); this.up(this.a.length - 1); }
            pop() {
                const a = this.a, res = a[0], last = a.pop();
                if (a.length) { a[0] = last; this.down(0); }
                return res;
            }
            up(i) {
                const a = this.a;
                while (i > 0) {
                    const p = (i - 1) >> 1;
                    if (a[p] <= a[i]) break;
                    [a[p], a[i]] = [a[i], a[p]]; i = p;
                }
            }
            down(i) {
                const a = this.a, n = a.length;
                for (;;) {
                    const l = 2 * i + 1, r = l + 1;
                    let s = i;
                    if (l < n && a[l] < a[s]) s = l;
                    if (r < n && a[r] < a[s]) s = r;
                    if (s === i) break;
                    [a[s], a[i]] = [a[i], a[s]]; i = s;
                }
            }
        }

        const pq = new MinHeap([5, 20, 1, 30, 4]);   // O(n) build
        console.log("min:", pq.peek());
        pq.push(3);                                  // O(log n)
        console.log("after push 3, min:", pq.peek());
        const out = [];
        while (pq.size()) out.push(pq.pop());        // O(log n) each
        console.log("popped in order:", out.join(" "));
    ''')
    yield complexity("O(log n) push / pop, O(1) peek", "O(n)")
    yield p("`heapq` also has a few conveniences worth knowing — `nlargest`, `nsmallest` and `heapreplace` (pop then push in a single sift, faster than the two calls). The list *is* the heap, so you can print it and see the array layout from the diagrams:")
    yield code('''
        import heapq

        p = [5, 20, 1, 30, 4]
        heapq.heapify(p)
        print(p)                          # [1, 4, 5, 30, 20]   ← a valid min-heap, not a sorted list
        heapq.heappush(p, 3)
        print(p)                          # [1, 4, 3, 30, 20, 5]
        print(heapq.heappop(p))           # 1
        print(p)                          # [3, 4, 5, 30, 20]
        print(heapq.nlargest(2, p))       # [30, 20]
        print(heapq.nsmallest(2, p))      # [3, 4]
        print(heapq.heapreplace(p, -1))   # 3   ← pops the min, then pushes -1 (one sift instead of two)
        print(p)                          # [-1, 4, 5, 30, 20]
    ''')
    yield pitfall("A heap is **not sorted** — only `h[0]` is guaranteed to be the minimum. Iterating over `heapq`'s list, `PriorityQueue`'s iterator or printing the array gives level order, not ascending order. To get sorted output, pop repeatedly.")
    yield note("For a **max-heap in Python** push the negated values (`heappush(h, -x)`, read `-h[0]`); for tuples `(priority, item)` the heap orders by priority first — make sure items are comparable or add a tie-breaking counter. In Java pass `Collections.reverseOrder()` or a `Comparator`; in C++ the default `priority_queue<int>` already is a max-heap.")

    yield section("Where heaps are used", "apps")
    yield cards(
        ("Priority queue", "Task scheduling, event simulation, bandwidth management — serve the most urgent item first, `O(log n)` per operation.", "list-numbers"),
        ("Heap sort", "`O(n log n)` worst case with `O(1)` extra space; the fallback inside introsort.", "sort-ascending"),
        ("Graph algorithms", "Dijkstra's shortest paths and Prim's minimum spanning tree pop the closest vertex from a min-heap.", "topology-star"),
        ("k largest / smallest", "Keep a min-heap of size `k`; push each element and pop when the size exceeds `k` — `O(n log k)` instead of sorting everything.", "chart-bar"),
        ("Median of a stream", "A max-heap of the lower half and a min-heap of the upper half; the median is at the roots.", "divide"),
        ("Merge k sorted lists", "Push the head of each list; pop the smallest and push its successor — `O(N log k)`. Huffman coding uses the same pattern.", "git-merge"),
        cols=3,
    )

    yield section("Interview Q&A", "message-question")
    yield qa("Why can a heap be stored in an array but a BST cannot?",
             "A heap is a **complete** binary tree, so reading it level by level leaves no gaps and parent/child positions are pure arithmetic (`(i−1)/2`, `2i+1`, `2i+2`). A BST can have any shape; storing it the same way would need an array of size `2^h` with mostly empty slots.")
    yield qa("Why is building a heap O(n) when a single insert is O(log n)?",
             "Bottom-up build calls `heapify` on the internal nodes from the bottom, and a node at height `h` sifts down at most `h` levels. Half of the nodes are leaves (cost 0), a quarter are at height 1, an eighth at height 2 … so the total is `n · Σ h / 2^(h+1)`, a series that converges to `n`. Inserting one by one instead sifts **up**, and most elements are deep, so that is `Θ(n log n)`.")
    yield qa("Heap or balanced BST for a priority queue?",
             "A heap: `O(1)` peek, `O(log n)` push/pop, `O(n)` build, no pointers and great cache behaviour. A BST gives the same `O(log n)` bounds plus search, predecessor/successor and delete-by-value, at the cost of pointers and constants — use it only when you need those extras (e.g. a double-ended priority queue).")
    yield qa("How do you find the k largest elements of a stream, and why a min-heap?",
             "Keep a **min-heap of size k**. For each element, push it; if the size exceeds `k`, pop the minimum — the smallest of the current candidates leaves. The root is always the kth largest so far. `O(n log k)` time and `O(k)` space, versus `O(n log n)` for sorting. A max-heap would make the *largest* easy to find but the one to evict hard.")
    yield qa("Is heap sort stable? Is it used in practice?",
             "Not stable — the long-range swaps reorder equal keys. In practice it loses to quick sort on arrays because of cache misses, but its guaranteed `O(n log n)` and `O(1)` space make it the fallback in **introsort** (C++ `std::sort`), which switches to heap sort when quick sort's recursion gets too deep.")
    yield qa("What does decreaseKey need that a library priority queue does not provide?",
             "The **index** of the element inside the heap. Library queues hide the array, so you cannot address an element. Dijkstra implementations therefore push a new `(distance, vertex)` pair whenever a shorter path is found and skip stale pairs when they are popped — lazy deletion — which keeps the same `O(E log V)` bound.")
