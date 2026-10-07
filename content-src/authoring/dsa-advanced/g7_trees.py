from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Trees & Heaps"

# The one sample tree every program in this topic builds (keys 10 … 90, 80 and 90 under 70).
# Each language has the same five-line builder so the reader sees identical numbers everywhere.


@topic(G, "trees", "Tree Data Structure", "binary-tree")
def _():
    yield lead("You already know the traversals and `height()`. This topic is the **problem toolkit** for binary trees: level-by-level BFS, horizontal distances, the *return height, record the answer on the side* pattern, two-stack tricks and (de)serialisation — the handful of techniques behind almost every tree interview question.")
    yield define("Binary tree", "a hierarchical structure in which every node has at most two children, `left` and `right`. Unlike a BST there is **no ordering rule**, so every problem here must be solved by visiting nodes, not by comparing keys.")
    yield diagram(r'''
                      10
                    /    \
                  20      30
                 /  \    /  \
                40  50  60   70
                            /  \
                           80   90
    ''', "The sample tree used by every program in this topic (9 nodes, height 4)")

    yield section("Conventions used in these notes", "ruler")
    yield table(
        ["Term", "Meaning here", "Sample tree"],
        ["Height", "number of **nodes** on the longest root-to-leaf path; an empty tree has height 0", "4 (10 → 30 → 70 → 80)"],
        ["Level", "root is level 0, its children level 1, …", "4 levels (0–3)"],
        ["Diameter", "number of nodes on the longest path between any two nodes", "6 (40 20 10 30 70 80)"],
        ["Horizontal distance (hd)", "root 0; a left child is `hd − 1`, a right child `hd + 1`", "40 is at −2, 90 at +3"],
        ["Balanced", "for every node, `|height(left) − height(right)| ≤ 1`", "yes"],
        ["Complete", "all levels full except possibly the last, which is filled left to right", "no (gap under 40/50/60)"],
    )
    yield note("Height is counted in **nodes** here, as in the original notes (a single node has height 1). Some books count edges — then every formula shifts by one. State your convention in an interview before writing code.")

    yield section("Node class and the sample tree", "code")
    yield p("Every program in this topic starts with the same `Node` class and a `sample()` builder that constructs the tree above by nesting constructor calls. Here it is with three warm-ups you already know: inorder, height and node count.")
    yield multi(r'''
        inorder: 40 20 50 10 60 30 80 70 90
        height: 4
        nodes: 9
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():                      # the tree used throughout these notes
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def inorder(n):
            if n is None:
                return
            inorder(n.left)
            print(n.key, end=" ")
            inorder(n.right)

        def height(n):                     # in nodes: a single node has height 1
            if n is None:
                return 0
            return 1 + max(height(n.left), height(n.right))

        def count_nodes(n):
            return 0 if n is None else 1 + count_nodes(n.left) + count_nodes(n.right)

        root = sample()
        print("inorder:", end=" "); inorder(root); print()
        print("height:", height(root))
        print("nodes:", count_nodes(root))
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };

        Node* sample() {                   // the tree used throughout these notes
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void inorder(Node* n) {
            if (!n) return;
            inorder(n->left);
            cout << n->key << " ";
            inorder(n->right);
        }

        int height(Node* n) {              // in nodes: a single node has height 1
            if (!n) return 0;
            return 1 + max(height(n->left), height(n->right));
        }

        int countNodes(Node* n) { return n ? 1 + countNodes(n->left) + countNodes(n->right) : 0; }

        int main() {
            Node* root = sample();
            cout << "inorder: "; inorder(root); cout << "\n";
            cout << "height: " << height(root) << "\n";
            cout << "nodes: " << countNodes(root) << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }

            static Node sample() {         // the tree used throughout these notes
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void inorder(Node n) {
                if (n == null) return;
                inorder(n.left);
                System.out.print(n.key + " ");
                inorder(n.right);
            }

            static int height(Node n) {    // in nodes: a single node has height 1
                if (n == null) return 0;
                return 1 + Math.max(height(n.left), height(n.right));
            }

            static int countNodes(Node n) { return n == null ? 0 : 1 + countNodes(n.left) + countNodes(n.right); }

            public static void main(String[] args) {
                Node root = sample();
                System.out.print("inorder: "); inorder(root); System.out.println();
                System.out.println("height: " + height(root));
                System.out.println("nodes: " + countNodes(root));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }

        const sample = () =>               // the tree used throughout these notes
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function inorder(n) {
            if (!n) return;
            inorder(n.left);
            process.stdout.write(n.key + " ");
            inorder(n.right);
        }

        function height(n) {               // in nodes: a single node has height 1
            return n ? 1 + Math.max(height(n.left), height(n.right)) : 0;
        }

        const countNodes = n => n ? 1 + countNodes(n.left) + countNodes(n.right) : 0;

        const root = sample();
        process.stdout.write("inorder: "); inorder(root); console.log();
        console.log("height:", height(root));
        console.log("nodes:", countNodes(root));
    ''')
    yield note("JavaScript's `console.log` always ends the line, so the programs use `process.stdout.write` when a value must be followed by a space instead of a newline — exactly what `print(x, end=\" \")` does in Python.")

    yield section("The technique toolbox", "tool")
    yield p("Almost every problem below is one of five patterns. Recognise the pattern and the code writes itself.")
    yield cards(
        ("Level-by-level BFS", "Queue; take `len(queue)` nodes per round. Gives level order, width, zigzag, bottom view.", "arrows-horizontal"),
        ("Return height, record on the side", "A post-order recursion returns one value (height) while a shared variable collects the answer: balanced, diameter, burn time.", "arrow-up"),
        ("Horizontal distance map", "Carry `hd` with each node; group by it in an ordered map: vertical traversal, top/bottom view.", "columns"),
        ("Preorder + inorder", "Preorder gives the root, inorder splits left from right: tree construction, serialisation.", "git-branch"),
        ("Explicit stack", "Simulate the recursion yourself: iterative inorder/preorder, two-stack spiral.", "stack-2"),
        ("Structural shortcuts", "Exploit shape: a perfect subtree has `2^h − 1` nodes, so a complete tree is counted in `O(log² n)`.", "bolt"),
        cols=3,
    )

    # ───────────────────────── level order line by line ─────────────────────────
    yield section("Level order traversal line by line", "list-numbers")
    yield io("the sample tree", "10 | 20 30 | 40 50 60 70 | 80 90   (| = new line)")
    yield p("Plain BFS prints all keys on one line. To start a new line after every level you need to know where a level ends. There are two classic ways.")
    yield idea("**Method 1 — a marker.** Push a `None` sentinel after the root. Whenever the sentinel comes out of the queue the current level is finished: print a newline and push the sentinel again so it sits behind the next level. Stop when the sentinel is the only thing left.")
    yield multi(r'''
        10
        20 30
        40 50 60 70
        80 90
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def print_levels(root):
            if root is None:
                return
            q = deque([root, None])          # None marks the end of a level
            while len(q) > 1:                # only the marker left → done
                curr = q.popleft()
                if curr is None:
                    print()                  # level finished: newline, re-arm the marker
                    q.append(None)
                    continue
                print(curr.key, end=" ")
                if curr.left:
                    q.append(curr.left)
                if curr.right:
                    q.append(curr.right)
            print()

        print_levels(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void printLevels(Node* root) {
            if (!root) return;
            queue<Node*> q;
            q.push(root);
            q.push(nullptr);                       // nullptr marks the end of a level
            while (q.size() > 1) {                 // only the marker left → done
                Node* curr = q.front(); q.pop();
                if (!curr) {
                    cout << "\n";                  // level finished: newline, re-arm the marker
                    q.push(nullptr);
                    continue;
                }
                cout << curr->key << " ";
                if (curr->left) q.push(curr->left);
                if (curr->right) q.push(curr->right);
            }
            cout << "\n";
        }

        int main() { printLevels(sample()); }
    ''', java=r'''
        import java.util.LinkedList;
        import java.util.Queue;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void printLevels(Node root) {
                if (root == null) return;
                Queue<Node> q = new LinkedList<>();    // ArrayDeque would reject the null marker
                q.add(root);
                q.add(null);                           // null marks the end of a level
                while (q.size() > 1) {                 // only the marker left → done
                    Node curr = q.poll();
                    if (curr == null) {
                        System.out.println();          // level finished: newline, re-arm the marker
                        q.add(null);
                        continue;
                    }
                    System.out.print(curr.key + " ");
                    if (curr.left != null) q.add(curr.left);
                    if (curr.right != null) q.add(curr.right);
                }
                System.out.println();
            }

            public static void main(String[] args) { printLevels(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function printLevels(root) {
            if (!root) return;
            const q = [root, null];                 // null marks the end of a level
            while (q.length > 1) {                  // only the marker left → done
                const curr = q.shift();
                if (curr === null) {
                    console.log();                  // level finished: newline, re-arm the marker
                    q.push(null);
                    continue;
                }
                process.stdout.write(curr.key + " ");
                if (curr.left) q.push(curr.left);
                if (curr.right) q.push(curr.right);
            }
            console.log();
        }

        printLevels(sample());
    ''')
    yield complexity("O(n)", "O(w) — w = maximum width")
    yield pitfall("Looping `while q` instead of `while len(q) > 1` never terminates: the marker keeps re-adding itself to an otherwise empty queue. In Java, `ArrayDeque` throws on `add(null)` — use `LinkedList` for this method, or the count method below which needs no marker.")
    yield idea("**Method 2 — count the level.** At the start of each round `len(queue)` is exactly the number of nodes on the current level. Pop that many, printing them and enqueuing their children, then print a newline. No sentinel, no special cases — this is the version to remember, and the backbone of width, zigzag and bottom-view problems.")
    yield multi(r'''
        10
        20 30
        40 50 60 70
        80 90
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def print_levels(root):
            if root is None:
                return
            q = deque([root])
            while q:
                for _ in range(len(q)):      # exactly the nodes of this level
                    curr = q.popleft()
                    print(curr.key, end=" ")
                    if curr.left:
                        q.append(curr.left)
                    if curr.right:
                        q.append(curr.right)
                print()                      # level done

        print_levels(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void printLevels(Node* root) {
            if (!root) return;
            queue<Node*> q;
            q.push(root);
            while (!q.empty()) {
                int count = q.size();                  // exactly the nodes of this level
                for (int i = 0; i < count; i++) {
                    Node* curr = q.front(); q.pop();
                    cout << curr->key << " ";
                    if (curr->left) q.push(curr->left);
                    if (curr->right) q.push(curr->right);
                }
                cout << "\n";                          // level done
            }
        }

        int main() { printLevels(sample()); }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void printLevels(Node root) {
                if (root == null) return;
                Queue<Node> q = new ArrayDeque<>();
                q.add(root);
                while (!q.isEmpty()) {
                    int count = q.size();                  // exactly the nodes of this level
                    for (int i = 0; i < count; i++) {
                        Node curr = q.poll();
                        System.out.print(curr.key + " ");
                        if (curr.left != null) q.add(curr.left);
                        if (curr.right != null) q.add(curr.right);
                    }
                    System.out.println();                  // level done
                }
            }

            public static void main(String[] args) { printLevels(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function printLevels(root) {
            if (!root) return;
            const q = [root];
            while (q.length) {
                const count = q.length;                 // exactly the nodes of this level
                const line = [];
                for (let i = 0; i < count; i++) {
                    const curr = q.shift();
                    line.push(curr.key);
                    if (curr.left) q.push(curr.left);
                    if (curr.right) q.push(curr.right);
                }
                console.log(line.join(" "));            // level done
            }
        }

        printLevels(sample());
    ''')
    yield complexity("O(n)", "O(w)")
    yield pitfall("Read `len(q)` **once**, before the inner loop. Writing `for _ in range(len(q))` is safe in Python because the range is evaluated once, but `while i < q.size()` in C++/Java re-reads a size that grows as children are added and merges levels.")

    # ───────────────────────── balanced ─────────────────────────
    yield section("Check for balanced binary tree", "scale")
    yield io("the sample tree", "Yes", "the sample tree with 100 added under 80", "No")
    yield diagram(r'''
        balanced (Yes)                         not balanced (No)
                  10                                   10
                /    \                               /    \
              20      30                           20      30   ← left height 1,
             /  \    /  \                         /  \    /  \    right height 3
            40  50  60   70                      40  50  60   70
                        /  \                                 /  \
                       80   90                              80   90
                                                           /
                                                         100
    ''', "A tree is balanced when every node's two subtrees differ in height by at most 1")
    yield idea("**Naive:** for every node compute the heights of both subtrees and compare, then recurse into the children. Correct, but `height()` is itself `O(n)`, and it is called again for every node — `O(n · h)`, which is `O(n²)` on a skewed tree.")
    yield multi(r'''
        sample tree: Yes
        with 100 under 80: No
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def height(n):
            return 0 if n is None else 1 + max(height(n.left), height(n.right))

        def is_balanced(n):
            if n is None:
                return True
            lh, rh = height(n.left), height(n.right)          # O(n) each, for every node
            return abs(lh - rh) <= 1 and is_balanced(n.left) and is_balanced(n.right)

        root = sample()
        print("sample tree:", "Yes" if is_balanced(root) else "No")
        root.right.right.left.left = Node(100)                # hang 100 under 80
        print("with 100 under 80:", "Yes" if is_balanced(root) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        #include <cstdlib>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        int height(Node* n) { return n ? 1 + max(height(n->left), height(n->right)) : 0; }

        bool isBalanced(Node* n) {
            if (!n) return true;
            int lh = height(n->left), rh = height(n->right);   // O(n) each, for every node
            return abs(lh - rh) <= 1 && isBalanced(n->left) && isBalanced(n->right);
        }

        int main() {
            Node* root = sample();
            cout << "sample tree: " << (isBalanced(root) ? "Yes" : "No") << "\n";
            root->right->right->left->left = new Node(100);    // hang 100 under 80
            cout << "with 100 under 80: " << (isBalanced(root) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static int height(Node n) { return n == null ? 0 : 1 + Math.max(height(n.left), height(n.right)); }

            static boolean isBalanced(Node n) {
                if (n == null) return true;
                int lh = height(n.left), rh = height(n.right);     // O(n) each, for every node
                return Math.abs(lh - rh) <= 1 && isBalanced(n.left) && isBalanced(n.right);
            }

            public static void main(String[] args) {
                Node root = sample();
                System.out.println("sample tree: " + (isBalanced(root) ? "Yes" : "No"));
                root.right.right.left.left = new Node(100);        // hang 100 under 80
                System.out.println("with 100 under 80: " + (isBalanced(root) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        const height = n => n ? 1 + Math.max(height(n.left), height(n.right)) : 0;

        function isBalanced(n) {
            if (!n) return true;
            const lh = height(n.left), rh = height(n.right);    // O(n) each, for every node
            return Math.abs(lh - rh) <= 1 && isBalanced(n.left) && isBalanced(n.right);
        }

        const root = sample();
        console.log("sample tree:", isBalanced(root) ? "Yes" : "No");
        root.right.right.left.left = new Node(100);             // hang 100 under 80
        console.log("with 100 under 80:", isBalanced(root) ? "Yes" : "No");
    ''')
    yield complexity("O(n · h) — O(n²) when skewed", "O(h) recursion")
    yield idea("**Efficient — the −1 trick.** Let one post-order function return the height of a subtree, but return **−1** as soon as any subtree is unbalanced. A parent that receives −1 from a child passes it straight up without recursing further. Each node is visited once, so the whole check is `O(n)`.")
    yield multi(r'''
        sample tree: Yes
        with 100 under 80: No
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def check(n):                      # height of n, or -1 if the subtree is unbalanced
            if n is None:
                return 0
            lh = check(n.left)
            if lh == -1:
                return -1                  # short-circuit: no need to look at the right side
            rh = check(n.right)
            if rh == -1 or abs(lh - rh) > 1:
                return -1
            return 1 + max(lh, rh)

        def is_balanced(root):
            return check(root) != -1

        root = sample()
        print("sample tree:", "Yes" if is_balanced(root) else "No")
        root.right.right.left.left = Node(100)
        print("with 100 under 80:", "Yes" if is_balanced(root) else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        #include <cstdlib>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        int check(Node* n) {               // height of n, or -1 if the subtree is unbalanced
            if (!n) return 0;
            int lh = check(n->left);
            if (lh == -1) return -1;       // short-circuit: no need to look at the right side
            int rh = check(n->right);
            if (rh == -1 || abs(lh - rh) > 1) return -1;
            return 1 + max(lh, rh);
        }

        bool isBalanced(Node* root) { return check(root) != -1; }

        int main() {
            Node* root = sample();
            cout << "sample tree: " << (isBalanced(root) ? "Yes" : "No") << "\n";
            root->right->right->left->left = new Node(100);
            cout << "with 100 under 80: " << (isBalanced(root) ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static int check(Node n) {         // height of n, or -1 if the subtree is unbalanced
                if (n == null) return 0;
                int lh = check(n.left);
                if (lh == -1) return -1;       // short-circuit: no need to look at the right side
                int rh = check(n.right);
                if (rh == -1 || Math.abs(lh - rh) > 1) return -1;
                return 1 + Math.max(lh, rh);
            }

            static boolean isBalanced(Node root) { return check(root) != -1; }

            public static void main(String[] args) {
                Node root = sample();
                System.out.println("sample tree: " + (isBalanced(root) ? "Yes" : "No"));
                root.right.right.left.left = new Node(100);
                System.out.println("with 100 under 80: " + (isBalanced(root) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function check(n) {                    // height of n, or -1 if the subtree is unbalanced
            if (!n) return 0;
            const lh = check(n.left);
            if (lh === -1) return -1;          // short-circuit: no need to look at the right side
            const rh = check(n.right);
            if (rh === -1 || Math.abs(lh - rh) > 1) return -1;
            return 1 + Math.max(lh, rh);
        }

        const isBalanced = root => check(root) !== -1;

        const root = sample();
        console.log("sample tree:", isBalanced(root) ? "Yes" : "No");
        root.right.right.left.left = new Node(100);
        console.log("with 100 under 80:", isBalanced(root) ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(h)")
    yield note("The same shape — *a post-order function that returns one quantity and smuggles a second one out* — solves diameter, burn time and many more. Learn it once.", "Pattern")

    # ───────────────────────── vertical traversal ─────────────────────────
    yield section("Vertical traversal", "columns")
    yield io("the sample tree", "40 | 20 | 10 50 60 | 30 80 | 70 | 90   (| = new line, one line per column)")
    yield diagram(r'''
        hd:   -2   -1    0    1    2    3
                        10
                   20        30
              40       50 60      70
                             80       90

        column -2: 40      column 1: 30 80
        column -1: 20      column 2: 70
        column  0: 10 50 60   column 3: 90
    ''', "Every node gets a horizontal distance: left child hd − 1, right child hd + 1")
    yield idea("Carry the **horizontal distance** with every node in a level-order traversal and group keys by it in an ordered map. BFS order guarantees that inside one column the upper node comes before the lower one, and that at the same level the left one comes first — exactly the order a vertical traversal wants. Sorting the keys of the map (or using an ordered map) prints the columns from left to right.")
    yield multi(r'''
        40
        20
        10 50 60
        30 80
        70
        90
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def vertical(root):
            if root is None:
                return
            groups = {}                                   # hd → keys in level order
            q = deque([(root, 0)])                        # node travels with its hd
            while q:
                node, hd = q.popleft()
                groups.setdefault(hd, []).append(node.key)
                if node.left:
                    q.append((node.left, hd - 1))
                if node.right:
                    q.append((node.right, hd + 1))
            for hd in sorted(groups):                     # leftmost column first
                print(*groups[hd])

        vertical(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <map>
        #include <queue>
        #include <vector>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void vertical(Node* root) {
            if (!root) return;
            map<int, vector<int>> groups;                 // std::map is ordered: leftmost column first
            queue<pair<Node*, int>> q;                    // node travels with its hd
            q.push({root, 0});
            while (!q.empty()) {
                auto [node, hd] = q.front(); q.pop();
                groups[hd].push_back(node->key);
                if (node->left) q.push({node->left, hd - 1});
                if (node->right) q.push({node->right, hd + 1});
            }
            for (auto& column : groups) {
                const vector<int>& keys = column.second;
                for (size_t i = 0; i < keys.size(); i++) cout << (i ? " " : "") << keys[i];
                cout << "\n";
            }
        }

        int main() { vertical(sample()); }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void vertical(Node root) {
                if (root == null) return;
                TreeMap<Integer, List<Integer>> groups = new TreeMap<>();   // sorted by hd
                Queue<Node> q = new ArrayDeque<>();
                Queue<Integer> hds = new ArrayDeque<>();                     // hd travels next to its node
                q.add(root); hds.add(0);
                while (!q.isEmpty()) {
                    Node node = q.poll();
                    int hd = hds.poll();
                    groups.computeIfAbsent(hd, k -> new ArrayList<>()).add(node.key);
                    if (node.left != null) { q.add(node.left); hds.add(hd - 1); }
                    if (node.right != null) { q.add(node.right); hds.add(hd + 1); }
                }
                for (List<Integer> keys : groups.values()) {           // leftmost column first
                    StringBuilder sb = new StringBuilder();
                    for (int k : keys) sb.append(k).append(' ');
                    System.out.println(sb.toString().trim());
                }
            }

            public static void main(String[] args) { vertical(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function vertical(root) {
            if (!root) return;
            const groups = new Map();                       // hd → keys in level order
            const q = [[root, 0]];                          // node travels with its hd
            while (q.length) {
                const [node, hd] = q.shift();
                if (!groups.has(hd)) groups.set(hd, []);
                groups.get(hd).push(node.key);
                if (node.left) q.push([node.left, hd - 1]);
                if (node.right) q.push([node.right, hd + 1]);
            }
            const hds = [...groups.keys()].sort((a, b) => a - b);   // leftmost column first
            for (const hd of hds) console.log(groups.get(hd).join(" "));
        }

        vertical(sample());
    ''')
    yield complexity("O(n log n) — sorting / ordered map over the columns", "O(n)")
    yield pitfall("Use **BFS**, not a preorder DFS, to fill the map. With DFS the node `50` (hd 0, level 2) would be recorded before `60` (hd 0, level 2) — fine — but `80` (hd 1, level 3) would come before `30` (hd 1, level 1), which is wrong: within a column the order must be top to bottom.")

    # ───────────────────────── bottom view ─────────────────────────
    yield section("Bottom view of a binary tree", "arrow-bar-to-down")
    yield io("the sample tree", "40 20 60 80 70 90", "the original notes' tree 10(20(30, 40), 50(60, 70))", "30 20 60 50 70")
    yield idea("The bottom view shows, for every column (`hd`), the **lowest** node — and when two nodes share both the column and the level, the one further to the **right** (the one BFS visits later). So run the same hd-tagged BFS and simply let every node **overwrite** its column's entry: the last write per column is the bottom view. Keeping the **first** write per column instead gives the **top view** for free.")
    yield multi(r'''
        bottom: 40 20 60 80 70 90
        top: 40 20 10 30 70 90
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def views(root):
            bottom, top = {}, {}
            q = deque([(root, 0)])
            while q:
                node, hd = q.popleft()
                bottom[hd] = node.key                 # a later node in BFS order overwrites
                if hd not in top:
                    top[hd] = node.key                # the first node seen in a column stays
                if node.left:
                    q.append((node.left, hd - 1))
                if node.right:
                    q.append((node.right, hd + 1))
            print("bottom:", *(bottom[hd] for hd in sorted(bottom)))
            print("top:", *(top[hd] for hd in sorted(top)))

        views(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <map>
        #include <queue>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void views(Node* root) {
            map<int, int> bottom, top;                    // ordered by hd
            queue<pair<Node*, int>> q;
            q.push({root, 0});
            while (!q.empty()) {
                auto [node, hd] = q.front(); q.pop();
                bottom[hd] = node->key;                   // a later node in BFS order overwrites
                if (!top.count(hd)) top[hd] = node->key;  // the first node seen in a column stays
                if (node->left) q.push({node->left, hd - 1});
                if (node->right) q.push({node->right, hd + 1});
            }
            cout << "bottom:";
            for (auto& e : bottom) cout << " " << e.second;
            cout << "\ntop:";
            for (auto& e : top) cout << " " << e.second;
            cout << "\n";
        }

        int main() { views(sample()); }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void views(Node root) {
                TreeMap<Integer, Integer> bottom = new TreeMap<>(), top = new TreeMap<>();
                Queue<Node> q = new ArrayDeque<>();
                Queue<Integer> hds = new ArrayDeque<>();
                q.add(root); hds.add(0);
                while (!q.isEmpty()) {
                    Node node = q.poll();
                    int hd = hds.poll();
                    bottom.put(hd, node.key);             // a later node in BFS order overwrites
                    top.putIfAbsent(hd, node.key);        // the first node seen in a column stays
                    if (node.left != null) { q.add(node.left); hds.add(hd - 1); }
                    if (node.right != null) { q.add(node.right); hds.add(hd + 1); }
                }
                StringBuilder b = new StringBuilder("bottom:"), t = new StringBuilder("top:");
                for (int k : bottom.values()) b.append(' ').append(k);
                for (int k : top.values()) t.append(' ').append(k);
                System.out.println(b);
                System.out.println(t);
            }

            public static void main(String[] args) { views(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function views(root) {
            const bottom = new Map(), top = new Map();
            const q = [[root, 0]];
            while (q.length) {
                const [node, hd] = q.shift();
                bottom.set(hd, node.key);                   // a later node in BFS order overwrites
                if (!top.has(hd)) top.set(hd, node.key);    // the first node seen in a column stays
                if (node.left) q.push([node.left, hd - 1]);
                if (node.right) q.push([node.right, hd + 1]);
            }
            const sorted = m => [...m.keys()].sort((a, b) => a - b).map(hd => m.get(hd));
            console.log("bottom:", sorted(bottom).join(" "));
            console.log("top:", sorted(top).join(" "));
        }

        views(sample());
    ''')
    yield complexity("O(n log n)", "O(n)")
    yield note("In the original notes' tree, `40` (right child of 20) and `60` (left child of 50) both sit at hd 0 on the same level. BFS visits `40` first and `60` second, so `60` overwrites and wins — that is the convention: **ties go to the node further right**. Had you used a DFS the winner would depend on traversal order, which is why the queue matters here.")

    # ───────────────────────── maximum width ─────────────────────────
    yield section("Maximum width of a binary tree", "arrows-horizontal")
    yield io("the sample tree", "4   (level 2 holds 40 50 60 70)", "the original notes' tree 10(20(40(80)), 30(50, 60))", "3")
    yield idea("Width is the number of nodes on a level, and the level-by-level BFS already knows that number: it is `len(queue)` at the start of each round. Keep the maximum over all rounds — no printing needed.")
    yield multi(r'''
        max width: 4
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def max_width(root):
            if root is None:
                return 0
            q = deque([root])
            best = 0
            while q:
                count = len(q)                   # size of the current level
                best = max(best, count)
                for _ in range(count):
                    node = q.popleft()
                    if node.left:
                        q.append(node.left)
                    if node.right:
                        q.append(node.right)
            return best

        print("max width:", max_width(sample()))
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <algorithm>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        int maxWidth(Node* root) {
            if (!root) return 0;
            queue<Node*> q;
            q.push(root);
            int best = 0;
            while (!q.empty()) {
                int count = q.size();                  // size of the current level
                best = max(best, count);
                for (int i = 0; i < count; i++) {
                    Node* node = q.front(); q.pop();
                    if (node->left) q.push(node->left);
                    if (node->right) q.push(node->right);
                }
            }
            return best;
        }

        int main() { cout << "max width: " << maxWidth(sample()) << "\n"; }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Queue;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static int maxWidth(Node root) {
                if (root == null) return 0;
                Queue<Node> q = new ArrayDeque<>();
                q.add(root);
                int best = 0;
                while (!q.isEmpty()) {
                    int count = q.size();                  // size of the current level
                    best = Math.max(best, count);
                    for (int i = 0; i < count; i++) {
                        Node node = q.poll();
                        if (node.left != null) q.add(node.left);
                        if (node.right != null) q.add(node.right);
                    }
                }
                return best;
            }

            public static void main(String[] args) { System.out.println("max width: " + maxWidth(sample())); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function maxWidth(root) {
            if (!root) return 0;
            const q = [root];
            let best = 0;
            while (q.length) {
                const count = q.length;                 // size of the current level
                best = Math.max(best, count);
                for (let i = 0; i < count; i++) {
                    const node = q.shift();
                    if (node.left) q.push(node.left);
                    if (node.right) q.push(node.right);
                }
            }
            return best;
        }

        console.log("max width:", maxWidth(sample()));
    ''')
    yield complexity("O(n)", "O(w)")
    yield note("This counts **present** nodes per level. LeetCode's *Maximum Width of Binary Tree* counts the span between the leftmost and rightmost node **including gaps** — for that, carry an index `i` with each node (`2i` and `2i + 1` for its children) and take `last − first + 1` per level.", "Variant")

    # ───────────────────────── binary tree → doubly linked list ─────────────────────────
    yield section("Convert a binary tree to a doubly linked list", "link")
    yield io("the sample tree", "40 <-> 20 <-> 50 <-> 10 <-> 60 <-> 30 <-> 80 <-> 70 <-> 90", "the original notes' tree 10(5, 20(30, 35))", "5 <-> 10 <-> 30 <-> 20 <-> 35")
    yield idea("The list must be in **inorder**, and the node's own `left` / `right` pointers become `prev` / `next` — no new nodes. Do an inorder traversal and keep a shared `prev`, the node visited just before the current one: link `prev.right = node`, `node.left = prev`, then advance `prev`. The first node ever visited (when `prev` is still `None`) is the head.")
    yield multi(r'''
        forward: 40 <-> 20 <-> 50 <-> 10 <-> 60 <-> 30 <-> 80 <-> 70 <-> 90
        backward: 90 70 80 30 60 10 50 20 40
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        prev = None                                   # node visited just before the current one

        def to_dll(node):                             # returns the head of the list
            global prev
            if node is None:
                return None
            head = to_dll(node.left)                  # inorder: left subtree first
            if prev is None:
                head = node                           # first node visited → head
            else:
                prev.right = node                     # link prev <-> node
                node.left = prev
            prev = node
            to_dll(node.right)
            return head

        head = to_dll(sample())
        keys, tail = [], None
        n = head
        while n:
            keys.append(str(n.key)); tail = n; n = n.right
        print("forward:", " <-> ".join(keys))
        print("backward:", end=" ")
        while tail:
            print(tail.key, end=" "); tail = tail.left
        print()
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        Node* last = nullptr;                          // node visited just before the current one (`prev` would clash with std::prev)

        Node* toDLL(Node* node) {                      // returns the head of the list
            if (!node) return nullptr;
            Node* head = toDLL(node->left);            // inorder: left subtree first
            if (!last) {
                head = node;                           // first node visited → head
            } else {
                last->right = node;                    // link last <-> node
                node->left = last;
            }
            last = node;
            toDLL(node->right);
            return head;
        }

        int main() {
            Node* head = toDLL(sample());
            Node* tail = nullptr;
            cout << "forward: ";
            for (Node* n = head; n; n = n->right) {
                cout << (n == head ? "" : " <-> ") << n->key;
                tail = n;
            }
            cout << "\nbackward: ";
            for (Node* n = tail; n; n = n->left) cout << n->key << " ";
            cout << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static Node prev = null;                       // node visited just before the current one

            static Node toDLL(Node node) {                 // returns the head of the list
                if (node == null) return null;
                Node head = toDLL(node.left);              // inorder: left subtree first
                if (prev == null) {
                    head = node;                           // first node visited → head
                } else {
                    prev.right = node;                     // link prev <-> node
                    node.left = prev;
                }
                prev = node;
                toDLL(node.right);
                return head;
            }

            public static void main(String[] args) {
                Node head = toDLL(sample());
                Node tail = null;
                StringBuilder sb = new StringBuilder("forward: ");
                for (Node n = head; n != null; n = n.right) {
                    sb.append(n == head ? "" : " <-> ").append(n.key);
                    tail = n;
                }
                System.out.println(sb);
                sb = new StringBuilder("backward:");
                for (Node n = tail; n != null; n = n.left) sb.append(' ').append(n.key);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        let prev = null;                                  // node visited just before the current one

        function toDLL(node) {                            // returns the head of the list
            if (!node) return null;
            let head = toDLL(node.left);                  // inorder: left subtree first
            if (!prev) {
                head = node;                              // first node visited → head
            } else {
                prev.right = node;                        // link prev <-> node
                node.left = prev;
            }
            prev = node;
            toDLL(node.right);
            return head;
        }

        const head = toDLL(sample());
        const keys = [];
        let tail = null;
        for (let n = head; n; n = n.right) { keys.push(n.key); tail = n; }
        console.log("forward:", keys.join(" <-> "));
        const back = [];
        for (let n = tail; n; n = n.left) back.push(n.key);
        console.log("backward:", back.join(" "));
    ''')
    yield complexity("O(n)", "O(h) recursion — no extra nodes")
    yield pitfall("Recurse into `node.left` **before** touching `node.left` — the recursion needs the original pointer. Setting `node.left = prev` first and then calling `to_dll(node.left)` walks back into the list and loops forever. The same applies to `prev`: it must be a variable shared across all calls (global / static / closure), not a parameter, or a deeper call's update is lost.")

    # ───────────────────────── construct from inorder + preorder ─────────────────────────
    yield section("Construct a binary tree from inorder and preorder", "git-branch")
    yield io("pre = [10 20 40 50 30 60 70 80 90], in = [40 20 50 10 60 30 80 70 90]", "the sample tree (printed level by level)", "pre = [10 20 30], in = [20 10 30]", "10 | 20 30")
    yield idea("**Preorder tells you the root, inorder tells you the split.** The first preorder key is the root. Find it in the inorder sequence: everything to its left is the left subtree, everything to its right is the right subtree. Recurse on the two halves, consuming preorder keys from a shared index — the left subtree is built first, so it takes the next keys, exactly as preorder lays them out.")
    yield diagram(r'''
        pre = 10 | 20 40 50 | 30 60 70 80 90           root = pre[0] = 10
        in  = 40 20 50 | 10 | 60 30 80 70 90           left of 10 in inorder → left subtree
              ^^^^^^^^        ^^^^^^^^^^^^^^           right of 10 → right subtree
              left (3 keys)   right (5 keys)
    ''', "One step of the construction: the next 3 preorder keys build the left subtree, the remaining 5 the right one")
    yield p("The straightforward version searches the inorder slice linearly for the root — `O(n)` per node, `O(n²)` in total on a skewed tree:")
    yield snippet("py", r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        pre_index = 0                                   # next preorder key to use

        def build(pre, ino, lo, hi):                    # builds the subtree whose inorder is ino[lo..hi]
            global pre_index
            if lo > hi:
                return None
            root = Node(pre[pre_index])
            pre_index += 1
            mid = ino.index(root.key, lo, hi + 1)       # linear search → O(n) per node
            root.left = build(pre, ino, lo, mid - 1)    # left first: it consumes the next preorder keys
            root.right = build(pre, ino, mid + 1, hi)
            return root

        def print_levels(root):
            q = deque([root])
            while q:
                print(*(n.key for n in q))
                q = deque(c for n in q for c in (n.left, n.right) if c)

        pre = [10, 20, 40, 50, 30, 60, 70, 80, 90]
        ino = [40, 20, 50, 10, 60, 30, 80, 70, 90]
        print_levels(build(pre, ino, 0, len(ino) - 1))
    ''', out=r'''
        10
        20 30
        40 50 60 70
        80 90
    ''')
    yield idea("**Efficient:** store the inorder position of every key in a hash map once (`O(n)`); then each root is located in `O(1)` and the whole tree is built in `O(n)`. This is the version to remember.")
    yield multi(r'''
        10
        20 30
        40 50 60 70
        80 90
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def build_tree(pre, ino):
            pos = {key: i for i, key in enumerate(ino)}     # key → index in inorder
            state = {"next": 0}                             # next preorder key to use

            def build(lo, hi):                              # subtree whose inorder is ino[lo..hi]
                if lo > hi:
                    return None
                root = Node(pre[state["next"]])
                state["next"] += 1
                mid = pos[root.key]                         # O(1) split point
                root.left = build(lo, mid - 1)              # left first (preorder order)
                root.right = build(mid + 1, hi)
                return root

            return build(0, len(ino) - 1)

        def print_levels(root):
            q = deque([root])
            while q:
                print(*(n.key for n in q))
                q = deque(c for n in q for c in (n.left, n.right) if c)

        pre = [10, 20, 40, 50, 30, 60, 70, 80, 90]
        ino = [40, 20, 50, 10, 60, 30, 80, 70, 90]
        print_levels(build_tree(pre, ino))
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };

        unordered_map<int, int> pos;                      // key → index in inorder
        int nextPre = 0;                                  // next preorder key to use

        Node* build(const vector<int>& pre, int lo, int hi) {   // subtree whose inorder is in[lo..hi]
            if (lo > hi) return nullptr;
            Node* root = new Node(pre[nextPre++]);
            int mid = pos[root->key];                     // O(1) split point
            root->left = build(pre, lo, mid - 1);         // left first (preorder order)
            root->right = build(pre, mid + 1, hi);
            return root;
        }

        void printLevels(Node* root) {
            queue<Node*> q;
            q.push(root);
            while (!q.empty()) {
                int count = q.size();
                for (int i = 0; i < count; i++) {
                    Node* n = q.front(); q.pop();
                    cout << (i ? " " : "") << n->key;
                    if (n->left) q.push(n->left);
                    if (n->right) q.push(n->right);
                }
                cout << "\n";
            }
        }

        int main() {
            vector<int> pre = {10, 20, 40, 50, 30, 60, 70, 80, 90};
            vector<int> in = {40, 20, 50, 10, 60, 30, 80, 70, 90};
            int n = in.size();
            for (int i = 0; i < n; i++) pos[in[i]] = i;
            printLevels(build(pre, 0, n - 1));
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
            }

            static Map<Integer, Integer> pos = new HashMap<>();   // key → index in inorder
            static int nextPre = 0;                               // next preorder key to use

            static Node build(int[] pre, int lo, int hi) {        // subtree whose inorder is in[lo..hi]
                if (lo > hi) return null;
                Node root = new Node(pre[nextPre++]);
                int mid = pos.get(root.key);                      // O(1) split point
                root.left = build(pre, lo, mid - 1);              // left first (preorder order)
                root.right = build(pre, mid + 1, hi);
                return root;
            }

            static void printLevels(Node root) {
                Queue<Node> q = new ArrayDeque<>();
                q.add(root);
                while (!q.isEmpty()) {
                    int count = q.size();
                    StringBuilder sb = new StringBuilder();
                    for (int i = 0; i < count; i++) {
                        Node n = q.poll();
                        sb.append(i > 0 ? " " : "").append(n.key);
                        if (n.left != null) q.add(n.left);
                        if (n.right != null) q.add(n.right);
                    }
                    System.out.println(sb);
                }
            }

            public static void main(String[] args) {
                int[] pre = {10, 20, 40, 50, 30, 60, 70, 80, 90};
                int[] in = {40, 20, 50, 10, 60, 30, 80, 70, 90};
                for (int i = 0; i < in.length; i++) pos.put(in[i], i);
                printLevels(build(pre, 0, in.length - 1));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }

        function buildTree(pre, ino) {
            const pos = new Map(ino.map((key, i) => [key, i]));   // key → index in inorder
            let nextPre = 0;                                        // next preorder key to use
            function build(lo, hi) {                                // subtree whose inorder is ino[lo..hi]
                if (lo > hi) return null;
                const root = new Node(pre[nextPre++]);
                const mid = pos.get(root.key);                      // O(1) split point
                root.left = build(lo, mid - 1);                     // left first (preorder order)
                root.right = build(mid + 1, hi);
                return root;
            }
            return build(0, ino.length - 1);
        }

        function printLevels(root) {
            let level = [root];
            while (level.length) {
                console.log(level.map(n => n.key).join(" "));
                level = level.flatMap(n => [n.left, n.right].filter(Boolean));
            }
        }

        const pre = [10, 20, 40, 50, 30, 60, 70, 80, 90];
        const ino = [40, 20, 50, 10, 60, 30, 80, 70, 90];
        printLevels(buildTree(pre, ino));
    ''')
    yield complexity("O(n)", "O(n) for the map + O(h) recursion")
    yield pitfall("Build the **left** subtree before the right one — the shared preorder index only works in that order. And the method assumes **distinct keys**: with duplicates the inorder position is ambiguous and no inorder + preorder pair identifies a unique tree. (Inorder + postorder works the same way, reading postorder from the back; preorder + postorder alone is *not* enough.)")
    yield note("The original notes' 'efficient' version used a stack and `stack[-1].key in io[:mp[value]]`, which re-scans a slice of the inorder list for every node — `O(n²)` again. The hash-map recursion above is the genuinely linear version.", "Corrected")

    # ───────────────────────── spiral / zigzag ─────────────────────────
    yield section("Spiral (zigzag) level order traversal", "arrows-shuffle")
    yield io("the sample tree", "10 30 20 40 50 60 70 90 80", "the original notes' tree 10(5, 20(30, 35))", "10 20 5 30 35")
    yield p("Even levels (0, 2, …) are printed left to right, odd levels right to left — so level 1 of the sample prints `30 20` and level 3 prints `90 80`.")
    yield idea("**Method 1 — level order + a stack.** Run the count-based level-by-level BFS. On a normal level print each node as it is dequeued; on a *reversed* level push the keys onto a stack instead and pop them all once the level is done — popping reverses the order. Toggle the flag after every level.")
    yield multi(r'''
        10 30 20 40 50 60 70 90 80
    ''', py=r'''
        from collections import deque

        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def spiral(root):
            if root is None:
                return
            q = deque([root])
            stack = []
            reverse = False                           # level 0 is left to right
            while q:
                for _ in range(len(q)):
                    node = q.popleft()
                    if reverse:
                        stack.append(node.key)        # hold back, print reversed later
                    else:
                        print(node.key, end=" ")
                    if node.left:
                        q.append(node.left)
                    if node.right:
                        q.append(node.right)
                while stack:                          # empty only on reversed levels
                    print(stack.pop(), end=" ")
                reverse = not reverse
            print()

        spiral(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <stack>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void spiral(Node* root) {
            if (!root) return;
            queue<Node*> q;
            stack<int> st;
            bool reverse = false;                     // level 0 is left to right
            q.push(root);
            while (!q.empty()) {
                int count = q.size();
                for (int i = 0; i < count; i++) {
                    Node* node = q.front(); q.pop();
                    if (reverse) st.push(node->key);  // hold back, print reversed later
                    else cout << node->key << " ";
                    if (node->left) q.push(node->left);
                    if (node->right) q.push(node->right);
                }
                while (!st.empty()) {                 // empty only on reversed levels
                    cout << st.top() << " ";
                    st.pop();
                }
                reverse = !reverse;
            }
            cout << "\n";
        }

        int main() { spiral(sample()); }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void spiral(Node root) {
                if (root == null) return;
                Queue<Node> q = new ArrayDeque<>();
                Deque<Integer> stack = new ArrayDeque<>();
                boolean reverse = false;                  // level 0 is left to right
                q.add(root);
                StringBuilder sb = new StringBuilder();
                while (!q.isEmpty()) {
                    int count = q.size();
                    for (int i = 0; i < count; i++) {
                        Node node = q.poll();
                        if (reverse) stack.push(node.key);   // hold back, print reversed later
                        else sb.append(node.key).append(' ');
                        if (node.left != null) q.add(node.left);
                        if (node.right != null) q.add(node.right);
                    }
                    while (!stack.isEmpty()) sb.append(stack.pop()).append(' ');   // reversed levels only
                    reverse = !reverse;
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) { spiral(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function spiral(root) {
            if (!root) return;
            const q = [root], stack = [], out = [];
            let reverse = false;                          // level 0 is left to right
            while (q.length) {
                const count = q.length;
                for (let i = 0; i < count; i++) {
                    const node = q.shift();
                    if (reverse) stack.push(node.key);    // hold back, print reversed later
                    else out.push(node.key);
                    if (node.left) q.push(node.left);
                    if (node.right) q.push(node.right);
                }
                while (stack.length) out.push(stack.pop());   // reversed levels only
                reverse = !reverse;
            }
            console.log(out.join(" "));
        }

        spiral(sample());
    ''')
    yield complexity("O(n)", "O(w)")
    yield idea("**Method 2 — two stacks.** Let `s1` hold the current left-to-right level and `s2` the next one. Pop everything from `s1`, printing and pushing each node's children **left then right** into `s2`; because a stack reverses, `s2` now pops right to left. Then pop everything from `s2`, pushing children **right then left** into `s1`, which reverses them back. Each stack hands the other exactly one level, already in the required order.")
    yield steps(
        ("Start", "Push the root onto `s1`."),
        ("While either stack is non-empty", "Drain `s1` (prints left → right): for each popped node push `left`, then `right` onto `s2`."),
        ("Then drain `s2`", "(prints right → left): for each popped node push `right`, then `left` onto `s1`."),
    )
    yield multi(r'''
        10 30 20 40 50 60 70 90 80
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def spiral(root):
            if root is None:
                return
            s1, s2 = [root], []                       # s1: left→right level, s2: right→left level
            while s1 or s2:
                while s1:
                    node = s1.pop()
                    print(node.key, end=" ")
                    if node.left:                     # left then right → s2 pops right first
                        s2.append(node.left)
                    if node.right:
                        s2.append(node.right)
                while s2:
                    node = s2.pop()
                    print(node.key, end=" ")
                    if node.right:                    # right then left → s1 pops left first
                        s1.append(node.right)
                    if node.left:
                        s1.append(node.left)
            print()

        spiral(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void spiral(Node* root) {
            if (!root) return;
            stack<Node*> s1, s2;                      // s1: left→right level, s2: right→left level
            s1.push(root);
            while (!s1.empty() || !s2.empty()) {
                while (!s1.empty()) {
                    Node* node = s1.top(); s1.pop();
                    cout << node->key << " ";
                    if (node->left) s2.push(node->left);     // left then right → s2 pops right first
                    if (node->right) s2.push(node->right);
                }
                while (!s2.empty()) {
                    Node* node = s2.top(); s2.pop();
                    cout << node->key << " ";
                    if (node->right) s1.push(node->right);   // right then left → s1 pops left first
                    if (node->left) s1.push(node->left);
                }
            }
            cout << "\n";
        }

        int main() { spiral(sample()); }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void spiral(Node root) {
                if (root == null) return;
                Deque<Node> s1 = new ArrayDeque<>(), s2 = new ArrayDeque<>();   // s1: left→right, s2: right→left
                s1.push(root);
                StringBuilder sb = new StringBuilder();
                while (!s1.isEmpty() || !s2.isEmpty()) {
                    while (!s1.isEmpty()) {
                        Node node = s1.pop();
                        sb.append(node.key).append(' ');
                        if (node.left != null) s2.push(node.left);     // left then right → s2 pops right first
                        if (node.right != null) s2.push(node.right);
                    }
                    while (!s2.isEmpty()) {
                        Node node = s2.pop();
                        sb.append(node.key).append(' ');
                        if (node.right != null) s1.push(node.right);   // right then left → s1 pops left first
                        if (node.left != null) s1.push(node.left);
                    }
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) { spiral(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function spiral(root) {
            if (!root) return;
            const s1 = [root], s2 = [], out = [];     // s1: left→right level, s2: right→left level
            while (s1.length || s2.length) {
                while (s1.length) {
                    const node = s1.pop();
                    out.push(node.key);
                    if (node.left) s2.push(node.left);      // left then right → s2 pops right first
                    if (node.right) s2.push(node.right);
                }
                while (s2.length) {
                    const node = s2.pop();
                    out.push(node.key);
                    if (node.right) s1.push(node.right);    // right then left → s1 pops left first
                    if (node.left) s1.push(node.left);
                }
            }
            console.log(out.join(" "));
        }

        spiral(sample());
    ''')
    yield complexity("O(n)", "O(w)")
    yield pitfall("The two inner loops push children in **opposite** orders (`left, right` into `s2` but `right, left` into `s1`). Swap one of them and every other level comes out in the wrong direction — trace the sample by hand once and the asymmetry becomes obvious.")

    # ───────────────────────── diameter ─────────────────────────
    yield section("Diameter of a binary tree", "arrows-horizontal")
    yield io("the sample tree", "6   (40 → 20 → 10 → 30 → 70 → 80, counted in nodes)")
    yield diagram(r'''
                      10
                    /    \
                  20      30
                 /  \    /  \
                40  50  60   70
                            /  \
                           80   90

        longest path: 40 – 20 – 10 – 30 – 70 – 80  (6 nodes, through the root)
        another:      80 – 70 – 90                 (3 nodes, not through the root)
    ''', "The diameter is the longest path between any two nodes — it need not pass through the root")
    yield idea("For every node, the longest path **through** it has `1 + height(left) + height(right)` nodes. The diameter is the maximum of this value over all nodes. **Naive:** compute it at every node with a fresh `height()` call — `O(n · h)`:")
    yield snippet("py", r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def height(n):
            return 0 if n is None else 1 + max(height(n.left), height(n.right))

        def diameter(n):
            if n is None:
                return 0
            through = 1 + height(n.left) + height(n.right)   # longest path through n — O(n) each time
            return max(through, diameter(n.left), diameter(n.right))

        print("diameter:", diameter(sample()))
    ''', out="diameter: 6")
    yield idea("**Efficient — return height, record the diameter on the side.** The post-order function returns the height of its subtree (what the parent needs) and, before returning, updates a shared `best` with `1 + lh + rh` (what the problem wants). Every node is visited once. The notes' intermediate version — a first pass that stores every height in a hash map, then a second pass — is also `O(n)`, but the single-pass version below needs no map.")
    yield multi(r'''
        diameter: 6
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        best = 0                                   # the diameter, recorded on the side

        def height(n):                             # returns height, updates best
            global best
            if n is None:
                return 0
            lh = height(n.left)
            rh = height(n.right)
            best = max(best, 1 + lh + rh)          # longest path through n
            return 1 + max(lh, rh)

        height(sample())
        print("diameter:", best)
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        int best = 0;                              // the diameter, recorded on the side

        int height(Node* n) {                      // returns height, updates best
            if (!n) return 0;
            int lh = height(n->left);
            int rh = height(n->right);
            best = max(best, 1 + lh + rh);         // longest path through n
            return 1 + max(lh, rh);
        }

        int main() {
            height(sample());
            cout << "diameter: " << best << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static int best = 0;                       // the diameter, recorded on the side

            static int height(Node n) {                // returns height, updates best
                if (n == null) return 0;
                int lh = height(n.left);
                int rh = height(n.right);
                best = Math.max(best, 1 + lh + rh);    // longest path through n
                return 1 + Math.max(lh, rh);
            }

            public static void main(String[] args) {
                height(sample());
                System.out.println("diameter: " + best);
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        let best = 0;                                 // the diameter, recorded on the side

        function height(n) {                          // returns height, updates best
            if (!n) return 0;
            const lh = height(n.left);
            const rh = height(n.right);
            best = Math.max(best, 1 + lh + rh);       // longest path through n
            return 1 + Math.max(lh, rh);
        }

        height(sample());
        console.log("diameter:", best);
    ''')
    yield complexity("O(n)", "O(h)")
    yield pitfall("Do not return the diameter from the recursion — the parent needs the **height**. Returning `max(lh, rh) + 1` while storing `1 + lh + rh` elsewhere is the whole trick. (If the question counts **edges**, the answer is `lh + rh` with heights in edges — one less than here: 5 for the sample.)")

    # ───────────────────────── LCA ─────────────────────────
    yield section("Lowest common ancestor (LCA)", "hierarchy")
    yield io("the sample tree, (40, 50)", "20", "(80, 30)", "30", "(50, 90)", "10", "(80, 90)", "70")
    yield define("Lowest common ancestor of `a` and `b`", "the deepest node that has both `a` and `b` in its subtree. A node counts as its own ancestor, so `LCA(80, 30) = 30`.")
    yield idea("**Method 1 — two root-to-node paths.** Record the path from the root to `a` and to `b` (a DFS that appends on the way down and pops on backtracking). Both paths start at the root; walk them in parallel while they agree — the last common node is the LCA. Two traversals and two `O(h)` paths; it also reports when a key is missing.")
    yield multi(r'''
        LCA(40, 50) = 20
        LCA(80, 30) = 30
        LCA(50, 90) = 10
        LCA(80, 90) = 70
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def find_path(n, key, path):               # fills path with root → key; False if absent
            if n is None:
                return False
            path.append(n.key)
            if n.key == key or find_path(n.left, key, path) or find_path(n.right, key, path):
                return True
            path.pop()                             # key not below n: backtrack
            return False

        def lca(root, a, b):
            pa, pb = [], []
            if not find_path(root, a, pa) or not find_path(root, b, pb):
                return None                        # one of the keys is missing
            i = 0
            while i < len(pa) and i < len(pb) and pa[i] == pb[i]:
                i += 1                             # walk while the paths agree
            return pa[i - 1]                       # last node they shared

        root = sample()
        for a, b in [(40, 50), (80, 30), (50, 90), (80, 90)]:
            print(f"LCA({a}, {b}) = {lca(root, a, b)}")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        bool findPath(Node* n, int key, vector<int>& path) {   // fills path with root → key
            if (!n) return false;
            path.push_back(n->key);
            if (n->key == key || findPath(n->left, key, path) || findPath(n->right, key, path))
                return true;
            path.pop_back();                                   // key not below n: backtrack
            return false;
        }

        int lca(Node* root, int a, int b) {
            vector<int> pa, pb;
            if (!findPath(root, a, pa) || !findPath(root, b, pb)) return -1;   // a key is missing
            size_t i = 0;
            while (i < pa.size() && i < pb.size() && pa[i] == pb[i]) i++;    // walk while they agree
            return pa[i - 1];                                                 // last shared node
        }

        int main() {
            Node* root = sample();
            int pairs[4][2] = {{40, 50}, {80, 30}, {50, 90}, {80, 90}};
            for (auto& p : pairs)
                cout << "LCA(" << p[0] << ", " << p[1] << ") = " << lca(root, p[0], p[1]) << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static boolean findPath(Node n, int key, List<Integer> path) {   // fills path with root → key
                if (n == null) return false;
                path.add(n.key);
                if (n.key == key || findPath(n.left, key, path) || findPath(n.right, key, path))
                    return true;
                path.remove(path.size() - 1);                                // key not below n: backtrack
                return false;
            }

            static Integer lca(Node root, int a, int b) {
                List<Integer> pa = new ArrayList<>(), pb = new ArrayList<>();
                if (!findPath(root, a, pa) || !findPath(root, b, pb)) return null;   // a key is missing
                int i = 0;
                while (i < pa.size() && i < pb.size() && pa.get(i).equals(pb.get(i))) i++;   // walk while they agree
                return pa.get(i - 1);                                                        // last shared node
            }

            public static void main(String[] args) {
                Node root = sample();
                int[][] pairs = {{40, 50}, {80, 30}, {50, 90}, {80, 90}};
                for (int[] p : pairs)
                    System.out.println("LCA(" + p[0] + ", " + p[1] + ") = " + lca(root, p[0], p[1]));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function findPath(n, key, path) {              // fills path with root → key; false if absent
            if (!n) return false;
            path.push(n.key);
            if (n.key === key || findPath(n.left, key, path) || findPath(n.right, key, path)) return true;
            path.pop();                                // key not below n: backtrack
            return false;
        }

        function lca(root, a, b) {
            const pa = [], pb = [];
            if (!findPath(root, a, pa) || !findPath(root, b, pb)) return null;   // a key is missing
            let i = 0;
            while (i < pa.length && i < pb.length && pa[i] === pb[i]) i++;    // walk while they agree
            return pa[i - 1];                                                  // last shared node
        }

        const root = sample();
        for (const [a, b] of [[40, 50], [80, 30], [50, 90], [80, 90]])
            console.log(`LCA(${a}, ${b}) = ${lca(root, a, b)}`);
    ''')
    yield complexity("O(n)", "O(h) for the two paths")
    yield idea("**Method 2 — one traversal.** Ask each node *what does your subtree contain?* A node returns itself if its key is `a` or `b`; otherwise it asks both children. If **both** sides return something, the two keys are on different sides and this node is the LCA. If only one side does, pass that result up — it is either the LCA found deeper or the single key seen so far. Four cases, one post-order pass.")
    yield table(
        ["Case at node `n`", "Return"],
        ["`n` is `a` or `b`", "`n` (no need to look below: if the other key is beneath, `n` is still the LCA)"],
        ["left returns a node **and** right returns a node", "`n` — the keys are on different sides"],
        ["only one side returns a node", "that node (both keys are below it, or only one was found)"],
        ["neither side returns a node", "`None`"],
    )
    yield multi(r'''
        LCA(40, 50) = 20
        LCA(80, 30) = 30
        LCA(50, 90) = 10
        LCA(80, 90) = 70
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def lca(n, a, b):
            if n is None:
                return None
            if n.key == a or n.key == b:
                return n                               # case 1: found one of the keys
            left = lca(n.left, a, b)
            right = lca(n.right, a, b)
            if left and right:
                return n                               # case 2: one key on each side → n is the LCA
            return left if left else right             # case 3/4: pass up whatever was found

        root = sample()
        for a, b in [(40, 50), (80, 30), (50, 90), (80, 90)]:
            print(f"LCA({a}, {b}) = {lca(root, a, b).key}")
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        Node* lca(Node* n, int a, int b) {
            if (!n) return nullptr;
            if (n->key == a || n->key == b) return n;         // case 1: found one of the keys
            Node* left = lca(n->left, a, b);
            Node* right = lca(n->right, a, b);
            if (left && right) return n;                      // case 2: one key on each side → n is the LCA
            return left ? left : right;                       // case 3/4: pass up whatever was found
        }

        int main() {
            Node* root = sample();
            int pairs[4][2] = {{40, 50}, {80, 30}, {50, 90}, {80, 90}};
            for (auto& p : pairs)
                cout << "LCA(" << p[0] << ", " << p[1] << ") = " << lca(root, p[0], p[1])->key << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static Node lca(Node n, int a, int b) {
                if (n == null) return null;
                if (n.key == a || n.key == b) return n;           // case 1: found one of the keys
                Node left = lca(n.left, a, b);
                Node right = lca(n.right, a, b);
                if (left != null && right != null) return n;      // case 2: one key on each side → n is the LCA
                return left != null ? left : right;               // case 3/4: pass up whatever was found
            }

            public static void main(String[] args) {
                Node root = sample();
                int[][] pairs = {{40, 50}, {80, 30}, {50, 90}, {80, 90}};
                for (int[] p : pairs)
                    System.out.println("LCA(" + p[0] + ", " + p[1] + ") = " + lca(root, p[0], p[1]).key);
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function lca(n, a, b) {
            if (!n) return null;
            if (n.key === a || n.key === b) return n;         // case 1: found one of the keys
            const left = lca(n.left, a, b);
            const right = lca(n.right, a, b);
            if (left && right) return n;                      // case 2: one key on each side → n is the LCA
            return left ? left : right;                       // case 3/4: pass up whatever was found
        }

        const root = sample();
        for (const [a, b] of [[40, 50], [80, 30], [50, 90], [80, 90]])
            console.log(`LCA(${a}, ${b}) = ${lca(root, a, b).key}`);
    ''')
    yield complexity("O(n)", "O(h)")
    yield pitfall("Method 2 **assumes both keys exist**. Ask for `LCA(40, 999)` and it happily returns `40` — the single key it found — because case 1 stops looking. Method 1 reports the missing key correctly. If keys may be absent, either verify existence first or have the recursion also return *how many* of the two keys it saw.")

    # ───────────────────────── burn a binary tree from a leaf ─────────────────────────
    yield section("Burn a binary tree from a leaf", "flame")
    yield io("the sample tree, fire starts at leaf 50", "5", "fire starts at leaf 60", "4", "the original notes' tree 10(20(40, 50), 30(60)), leaf 50", "4")
    yield diagram(r'''
        fire starts at 50; each second it spreads to every neighbour (parent and children)

        t=0: 50                       10 ←t=2
        t=1: 20                     /    \
        t=2: 10, 40           t=1→ 20      30 ←t=3
        t=3: 30                   /  \    /  \
        t=4: 60, 70       t=2→ 40  50  60   70 ←t=4
        t=5: 80, 90                t=0  t=4   /  \
                                            80   90 ←t=5  → answer 5
    ''', "Burn time = the distance from the leaf to the farthest node")
    yield idea("The farthest node from the leaf is reached by going **up** to some ancestor and then **down** into that ancestor's other subtree. So for every ancestor `n` of the leaf, the candidate answer is `dist(leaf, n) + height(other child of n)`. One post-order pass computes both: the function **returns the height** of a subtree (like before) and **reports the leaf's distance** through an out-parameter `dist` (−1 when the leaf is not below). At a node where `dist` came back from one side, update the answer with the other side's height.")
    yield multi(r'''
        burn from 50: 5
        burn from 60: 4
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        best = 0

        def burn(n, leaf, dist):          # returns height; dist[0] = distance of leaf below n, or -1
            global best
            dist[0] = -1
            if n is None:
                return 0
            if n.key == leaf:
                dist[0] = 0               # the fire starts here
                return 1
            ldist, rdist = [-1], [-1]
            lh = burn(n.left, leaf, ldist)
            rh = burn(n.right, leaf, rdist)
            if ldist[0] != -1:            # leaf is in the left subtree
                dist[0] = ldist[0] + 1
                best = max(best, dist[0] + rh)    # up to n, then down the right side
            elif rdist[0] != -1:          # leaf is in the right subtree
                dist[0] = rdist[0] + 1
                best = max(best, dist[0] + lh)
            return 1 + max(lh, rh)

        def burn_time(root, leaf):
            global best
            best = 0
            burn(root, leaf, [-1])
            return best

        root = sample()
        print("burn from 50:", burn_time(root, 50))
        print("burn from 60:", burn_time(root, 60))
    ''', cpp=r'''
        #include <iostream>
        #include <algorithm>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        int best = 0;

        int burn(Node* n, int leaf, int& dist) {   // returns height; dist = distance of leaf below n, or -1
            dist = -1;
            if (!n) return 0;
            if (n->key == leaf) { dist = 0; return 1; }      // the fire starts here
            int ldist, rdist;
            int lh = burn(n->left, leaf, ldist);
            int rh = burn(n->right, leaf, rdist);
            if (ldist != -1) {                               // leaf is in the left subtree
                dist = ldist + 1;
                best = max(best, dist + rh);                 // up to n, then down the right side
            } else if (rdist != -1) {                        // leaf is in the right subtree
                dist = rdist + 1;
                best = max(best, dist + lh);
            }
            return 1 + max(lh, rh);
        }

        int burnTime(Node* root, int leaf) {
            best = 0;
            int d;
            burn(root, leaf, d);
            return best;
        }

        int main() {
            Node* root = sample();
            cout << "burn from 50: " << burnTime(root, 50) << "\n";
            cout << "burn from 60: " << burnTime(root, 60) << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static int best = 0;

            static int burn(Node n, int leaf, int[] dist) {   // returns height; dist[0] = distance of leaf below n, or -1
                dist[0] = -1;
                if (n == null) return 0;
                if (n.key == leaf) { dist[0] = 0; return 1; }   // the fire starts here
                int[] ldist = {-1}, rdist = {-1};
                int lh = burn(n.left, leaf, ldist);
                int rh = burn(n.right, leaf, rdist);
                if (ldist[0] != -1) {                           // leaf is in the left subtree
                    dist[0] = ldist[0] + 1;
                    best = Math.max(best, dist[0] + rh);        // up to n, then down the right side
                } else if (rdist[0] != -1) {                    // leaf is in the right subtree
                    dist[0] = rdist[0] + 1;
                    best = Math.max(best, dist[0] + lh);
                }
                return 1 + Math.max(lh, rh);
            }

            static int burnTime(Node root, int leaf) {
                best = 0;
                burn(root, leaf, new int[]{-1});
                return best;
            }

            public static void main(String[] args) {
                Node root = sample();
                System.out.println("burn from 50: " + burnTime(root, 50));
                System.out.println("burn from 60: " + burnTime(root, 60));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        let best = 0;

        function burn(n, leaf, dist) {        // returns height; dist.v = distance of leaf below n, or -1
            dist.v = -1;
            if (!n) return 0;
            if (n.key === leaf) { dist.v = 0; return 1; }   // the fire starts here
            const ldist = { v: -1 }, rdist = { v: -1 };
            const lh = burn(n.left, leaf, ldist);
            const rh = burn(n.right, leaf, rdist);
            if (ldist.v !== -1) {                           // leaf is in the left subtree
                dist.v = ldist.v + 1;
                best = Math.max(best, dist.v + rh);         // up to n, then down the right side
            } else if (rdist.v !== -1) {                    // leaf is in the right subtree
                dist.v = rdist.v + 1;
                best = Math.max(best, dist.v + lh);
            }
            return 1 + Math.max(lh, rh);
        }

        function burnTime(root, leaf) {
            best = 0;
            burn(root, leaf, { v: -1 });
            return best;
        }

        const root = sample();
        console.log("burn from 50:", burnTime(root, 50));
        console.log("burn from 60:", burnTime(root, 60));
    ''')
    yield complexity("O(n)", "O(h)")
    yield pitfall("The function returns `1` at the leaf and uses `dist + height` — this only adds up when the fire really starts at a **leaf**. Starting at an internal node also needs `max(lh, rh)` of that node's own subtree as a candidate, and the height returned there must be the real height, not `1`. Interviewers love asking for that generalisation (*minimum time to burn from any node*); the BFS-on-parent-pointers approach handles it directly.")

    # ───────────────────────── count nodes in a complete binary tree ─────────────────────────
    yield section("Count nodes in a complete binary tree", "binary")
    yield io("complete tree 10(20(40(80, 90), 50(100)), 30(60, 70))", "10", "perfect tree 10(20(40, 50), 30(60, 70))", "7")
    yield diagram(r'''
                      10                 left height  (10 20 40 80) = 4
                    /    \               right height (10 30 70)    = 3   → not perfect, recurse
                  20      30
                 /  \    /  \            subtree 30: left 2, right 2 → perfect → 2² − 1 = 3 nodes
                40  50  60   70          subtree 20: left 3, right 2 → recurse
               /  \  /                     subtree 40: left 2, right 2 → perfect → 3 nodes
              80 90 100                    subtree 50: left 2, right 1 → recurse → 2 nodes
                                         total = 1 + (1 + 3 + 2) + 3 = 10
    ''', "A complete tree: every level full except the last, which fills from the left")
    yield idea("`1 + count(left) + count(right)` is `O(n)` and works for any tree. A **complete** tree has structure to exploit: walk down the leftmost and the rightmost path of a subtree. If the two heights are equal the subtree is **perfect** and has exactly `2^h − 1` nodes — no need to visit them. Otherwise recurse into both children, but at least one of them is perfect and answers immediately, so only one branch keeps recursing. `O(log n)` levels × `O(log n)` to measure the two heights = `O(log² n)`.")
    yield multi(r'''
        complete tree (10 nodes): 10
        perfect tree (7 nodes): 7
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def count_complete(n):
            lh = rh = 0
            cur = n
            while cur:                                # height along the leftmost path
                lh += 1
                cur = cur.left
            cur = n
            while cur:                                # height along the rightmost path
                rh += 1
                cur = cur.right
            if lh == rh:
                return (1 << lh) - 1                  # perfect subtree: 2^h - 1 nodes, no visit needed
            return 1 + count_complete(n.left) + count_complete(n.right)

        complete = Node(10, Node(20, Node(40, Node(80), Node(90)), Node(50, Node(100))),
                            Node(30, Node(60), Node(70)))
        perfect = Node(10, Node(20, Node(40), Node(50)), Node(30, Node(60), Node(70)))
        print("complete tree (10 nodes):", count_complete(complete))
        print("perfect tree (7 nodes):", count_complete(perfect))
    ''', cpp=r'''
        #include <iostream>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };

        int countComplete(Node* n) {
            int lh = 0, rh = 0;
            for (Node* cur = n; cur; cur = cur->left) lh++;     // height along the leftmost path
            for (Node* cur = n; cur; cur = cur->right) rh++;    // height along the rightmost path
            if (lh == rh) return (1 << lh) - 1;                 // perfect subtree: 2^h - 1 nodes
            return 1 + countComplete(n->left) + countComplete(n->right);
        }

        int main() {
            Node* complete = new Node(10, new Node(20, new Node(40, new Node(80), new Node(90)), new Node(50, new Node(100))),
                                          new Node(30, new Node(60), new Node(70)));
            Node* perfect = new Node(10, new Node(20, new Node(40), new Node(50)), new Node(30, new Node(60), new Node(70)));
            cout << "complete tree (10 nodes): " << countComplete(complete) << "\n";
            cout << "perfect tree (7 nodes): " << countComplete(perfect) << "\n";
        }
    ''', java=r'''
        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }

            static int countComplete(Node n) {
                int lh = 0, rh = 0;
                for (Node cur = n; cur != null; cur = cur.left) lh++;     // height along the leftmost path
                for (Node cur = n; cur != null; cur = cur.right) rh++;    // height along the rightmost path
                if (lh == rh) return (1 << lh) - 1;                       // perfect subtree: 2^h - 1 nodes
                return 1 + countComplete(n.left) + countComplete(n.right);
            }

            public static void main(String[] args) {
                Node complete = new Node(10, new Node(20, new Node(40, new Node(80), new Node(90)), new Node(50, new Node(100), null)),
                                             new Node(30, new Node(60), new Node(70)));
                Node perfect = new Node(10, new Node(20, new Node(40), new Node(50)), new Node(30, new Node(60), new Node(70)));
                System.out.println("complete tree (10 nodes): " + countComplete(complete));
                System.out.println("perfect tree (7 nodes): " + countComplete(perfect));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }

        function countComplete(n) {
            let lh = 0, rh = 0;
            for (let cur = n; cur; cur = cur.left) lh++;      // height along the leftmost path
            for (let cur = n; cur; cur = cur.right) rh++;     // height along the rightmost path
            if (lh === rh) return (1 << lh) - 1;              // perfect subtree: 2^h - 1 nodes
            return 1 + countComplete(n.left) + countComplete(n.right);
        }

        const complete = new Node(10, new Node(20, new Node(40, new Node(80), new Node(90)), new Node(50, new Node(100))),
                                      new Node(30, new Node(60), new Node(70)));
        const perfect = new Node(10, new Node(20, new Node(40), new Node(50)), new Node(30, new Node(60), new Node(70)));
        console.log("complete tree (10 nodes):", countComplete(complete));
        console.log("perfect tree (7 nodes):", countComplete(perfect));
    ''')
    yield complexity("O(log² n)", "O(log n)")
    yield pitfall("The shortcut is only valid for a **complete** tree. On an arbitrary tree `lh == rh` does not imply a perfect subtree (a node with a left-only chain of 2 and a right-only chain of 2 has equal heights but 5 nodes, not 7) — use the plain `O(n)` count there. This is also why heaps, which are complete trees, can live in arrays.")

    # ───────────────────────── serialize / deserialize ─────────────────────────
    yield section("Serialize and deserialize a binary tree", "file-export")
    yield io("the sample tree", "10 20 40 -1 -1 50 -1 -1 30 60 -1 -1 70 80 -1 -1 90 -1 -1   (preorder, −1 = empty)", "the original notes' tree 10(20, 30)", "10 20 -1 -1 30 -1 -1")
    yield define("Serialization", "turning a tree into a flat sequence (string or array) that can be stored or sent, such that **deserialization** rebuilds exactly the same tree. A single traversal order is not enough on its own — `10 20` could be a left child or a right child.")
    yield idea("**Approach A — inorder + separator + preorder.** Two traversals identify a tree with distinct keys (see *Construct from inorder and preorder*). Store the inorder, a separator such as `−1`, then the preorder, and rebuild with the hash-map construction. It works, but needs distinct keys and twice the space:")
    yield snippet("py", r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def inorder(n, out):
            if n:
                inorder(n.left, out); out.append(n.key); inorder(n.right, out)

        def preorder(n, out):
            if n:
                out.append(n.key); preorder(n.left, out); preorder(n.right, out)

        def serialize(root):
            arr = []
            inorder(root, arr)
            arr.append(-1)                                # separator
            preorder(root, arr)
            return arr

        def deserialize(arr):
            sep = arr.index(-1)
            ino, pre = arr[:sep], arr[sep + 1:]
            pos = {key: i for i, key in enumerate(ino)}
            state = {"next": 0}
            def build(lo, hi):
                if lo > hi:
                    return None
                root = Node(pre[state["next"]]); state["next"] += 1
                mid = pos[root.key]
                root.left = build(lo, mid - 1)
                root.right = build(mid + 1, hi)
                return root
            return build(0, len(ino) - 1)

        data = serialize(sample())
        print("serialized:", *data)
        again = serialize(deserialize(data))
        print("round trip identical:", "Yes" if again == data else "No")
    ''', out=r'''
        serialized: 40 20 50 10 60 30 80 70 90 -1 10 20 40 50 30 60 70 80 90
        round trip identical: Yes
    ''')
    yield idea("**Approach B — preorder with explicit empties (the one to remember).** A preorder traversal becomes unambiguous as soon as every missing child is written down too: emit the key, recurse left, recurse right, and emit `−1` for `None`. Deserialization reads the sequence in the same order with a shared index: read a value; if it is `−1` return `None`, otherwise create the node and build its left then right child from the following values. Duplicates are fine, and the output is `2n + 1` values.")
    yield diagram(r'''
             10            preorder with empties:
            /  \           10  20 -1 -1  30 -1 -1
          20    30             ^^^^^^^^  ^^^^^^^^
                           20 has no children, 30 has no children
    ''', "The −1 markers make the sequence decodable (assumption: −1 never appears as a key)")
    yield multi(r'''
        serialized: 10 20 40 -1 -1 50 -1 -1 30 60 -1 -1 70 80 -1 -1 90 -1 -1
        rebuilt inorder: 40 20 50 10 60 30 80 70 90
        round trip identical: Yes
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        EMPTY = -1

        def serialize(n, out):                    # preorder, writing EMPTY for every missing child
            if n is None:
                out.append(EMPTY)
                return
            out.append(n.key)
            serialize(n.left, out)
            serialize(n.right, out)

        def deserialize(arr, pos):                # pos[0] = next value to read, shared by all calls
            val = arr[pos[0]]
            pos[0] += 1
            if val == EMPTY:
                return None
            n = Node(val)
            n.left = deserialize(arr, pos)        # the following values describe the left subtree…
            n.right = deserialize(arr, pos)       # …then the right one
            return n

        def inorder(n):
            if n:
                inorder(n.left); print(n.key, end=" "); inorder(n.right)

        data = []
        serialize(sample(), data)
        print("serialized:", *data)
        rebuilt = deserialize(data, [0])
        print("rebuilt inorder:", end=" "); inorder(rebuilt); print()
        again = []
        serialize(rebuilt, again)
        print("round trip identical:", "Yes" if again == data else "No")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        const int EMPTY = -1;

        void serialize(Node* n, vector<int>& out) {     // preorder, writing EMPTY for every missing child
            if (!n) { out.push_back(EMPTY); return; }
            out.push_back(n->key);
            serialize(n->left, out);
            serialize(n->right, out);
        }

        Node* deserialize(const vector<int>& arr, int& pos) {   // pos = next value to read, shared
            int val = arr[pos++];
            if (val == EMPTY) return nullptr;
            Node* n = new Node(val);
            n->left = deserialize(arr, pos);            // the following values describe the left subtree…
            n->right = deserialize(arr, pos);           // …then the right one
            return n;
        }

        void inorder(Node* n) {
            if (!n) return;
            inorder(n->left); cout << n->key << " "; inorder(n->right);
        }

        int main() {
            vector<int> data;
            serialize(sample(), data);
            cout << "serialized:";
            for (int v : data) cout << " " << v;
            cout << "\n";
            int pos = 0;
            Node* rebuilt = deserialize(data, pos);
            cout << "rebuilt inorder: "; inorder(rebuilt); cout << "\n";
            vector<int> again;
            serialize(rebuilt, again);
            cout << "round trip identical: " << (again == data ? "Yes" : "No") << "\n";
        }
    ''', java=r'''
        import java.util.ArrayList;
        import java.util.List;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static final int EMPTY = -1;
            static int pos = 0;                                 // next value to read, shared by all calls

            static void serialize(Node n, List<Integer> out) {  // preorder, writing EMPTY for every missing child
                if (n == null) { out.add(EMPTY); return; }
                out.add(n.key);
                serialize(n.left, out);
                serialize(n.right, out);
            }

            static Node deserialize(List<Integer> arr) {
                int val = arr.get(pos++);
                if (val == EMPTY) return null;
                Node n = new Node(val);
                n.left = deserialize(arr);                      // the following values describe the left subtree…
                n.right = deserialize(arr);                     // …then the right one
                return n;
            }

            static void inorder(Node n, StringBuilder sb) {
                if (n == null) return;
                inorder(n.left, sb); sb.append(n.key).append(' '); inorder(n.right, sb);
            }

            public static void main(String[] args) {
                List<Integer> data = new ArrayList<>();
                serialize(sample(), data);
                StringBuilder sb = new StringBuilder("serialized:");
                for (int v : data) sb.append(' ').append(v);
                System.out.println(sb);
                pos = 0;
                Node rebuilt = deserialize(data);
                sb = new StringBuilder("rebuilt inorder: ");
                inorder(rebuilt, sb);
                System.out.println(sb.toString().trim());
                List<Integer> again = new ArrayList<>();
                serialize(rebuilt, again);
                System.out.println("round trip identical: " + (again.equals(data) ? "Yes" : "No"));
            }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        const EMPTY = -1;

        function serialize(n, out) {                  // preorder, writing EMPTY for every missing child
            if (!n) { out.push(EMPTY); return; }
            out.push(n.key);
            serialize(n.left, out);
            serialize(n.right, out);
        }

        let pos = 0;                                  // next value to read, shared by all calls

        function deserialize(arr) {
            const val = arr[pos++];
            if (val === EMPTY) return null;
            const n = new Node(val);
            n.left = deserialize(arr);                // the following values describe the left subtree…
            n.right = deserialize(arr);               // …then the right one
            return n;
        }

        const inorder = (n, out) => { if (n) { inorder(n.left, out); out.push(n.key); inorder(n.right, out); } };

        const data = [];
        serialize(sample(), data);
        console.log("serialized:", data.join(" "));
        pos = 0;
        const rebuilt = deserialize(data);
        const keys = [];
        inorder(rebuilt, keys);
        console.log("rebuilt inorder:", keys.join(" "));
        const again = [];
        serialize(rebuilt, again);
        console.log("round trip identical:", again.join() === data.join() ? "Yes" : "No");
    ''')
    yield complexity("O(n)", "O(n) — 2n + 1 values")
    yield pitfall("The read index must be **shared** across the recursive calls (a global, a reference, or a one-element list) — passing an `int` by value makes every call re-read the same position. And reset it to 0 before deserializing a second sequence. If `−1` can be a real key, pick a different marker (a string such as `#` or `N` in a text format).")

    # ───────────────────────── iterative inorder ─────────────────────────
    yield section("Iterative inorder traversal", "stack-2")
    yield io("the sample tree", "40 20 50 10 60 30 80 70 90", "the original notes' tree 10(20(40, 50), 30)", "40 20 10 30")
    yield idea("Recursion keeps the *pending* nodes on the call stack; do it yourself with an explicit stack. From the current node, push every node on the way down the **left** spine. Then pop: the popped node is the next one in inorder (its left side is finished), print it, and move to its **right** child — and push that child's left spine in the same way. Stop when both the stack and the current pointer are empty.")
    yield steps(
        ("Go left", "While `curr` is not empty: push `curr`, `curr = curr.left`."),
        ("Visit", "Pop the stack into `curr` and print it — everything to its left has been printed."),
        ("Go right", "`curr = curr.right`, then repeat from step 1. Finished when the stack is empty and `curr` is empty."),
    )
    yield multi(r'''
        40 20 50 10 60 30 80 70 90
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def inorder(root):
            stack, curr = [], root
            while stack or curr:
                while curr:                        # push the whole left spine
                    stack.append(curr)
                    curr = curr.left
                curr = stack.pop()                 # leftmost pending node
                print(curr.key, end=" ")
                curr = curr.right                  # now its right subtree, same procedure
            print()

        inorder(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void inorder(Node* root) {
            stack<Node*> st;
            Node* curr = root;
            while (!st.empty() || curr) {
                while (curr) {                     // push the whole left spine
                    st.push(curr);
                    curr = curr->left;
                }
                curr = st.top(); st.pop();         // leftmost pending node
                cout << curr->key << " ";
                curr = curr->right;                // now its right subtree, same procedure
            }
            cout << "\n";
        }

        int main() { inorder(sample()); }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void inorder(Node root) {
                Deque<Node> st = new ArrayDeque<>();
                Node curr = root;
                StringBuilder sb = new StringBuilder();
                while (!st.isEmpty() || curr != null) {
                    while (curr != null) {             // push the whole left spine
                        st.push(curr);
                        curr = curr.left;
                    }
                    curr = st.pop();                   // leftmost pending node
                    sb.append(curr.key).append(' ');
                    curr = curr.right;                 // now its right subtree, same procedure
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) { inorder(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function inorder(root) {
            const st = [], out = [];
            let curr = root;
            while (st.length || curr) {
                while (curr) {                         // push the whole left spine
                    st.push(curr);
                    curr = curr.left;
                }
                curr = st.pop();                       // leftmost pending node
                out.push(curr.key);
                curr = curr.right;                     // now its right subtree, same procedure
            }
            console.log(out.join(" "));
        }

        inorder(sample());
    ''')
    yield complexity("O(n)", "O(h) stack")
    yield note("The loop condition is `stack or curr`, not just `stack`: after popping the root (`10`) the stack may be empty while `curr` still points at the unvisited right subtree. The original notes avoided this by pre-pushing the left spine before the loop and re-pushing inside it — equivalent, but with the spine-push code written twice.")

    # ───────────────────────── iterative preorder ─────────────────────────
    yield section("Iterative preorder traversal", "stack-3")
    yield io("the sample tree", "10 20 40 50 30 60 70 80 90", "the original notes' tree 10(20(40, 50), 30(60))", "10 20 40 50 30 60")
    yield idea("**Version 1 — push right, then left.** Preorder visits a node *before* its children, so a node can be printed the moment it is popped. Push the root; then repeatedly pop, print, and push the **right** child first and the **left** child second — the stack is LIFO, so the left child comes out next, exactly as preorder requires.")
    yield multi(r'''
        10 20 40 50 30 60 70 80 90
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def preorder(root):
            if root is None:
                return
            stack = [root]
            while stack:
                curr = stack.pop()
                print(curr.key, end=" ")           # visit on pop
                if curr.right:
                    stack.append(curr.right)       # right first …
                if curr.left:
                    stack.append(curr.left)        # … so that left is popped next
            print()

        preorder(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void preorder(Node* root) {
            if (!root) return;
            stack<Node*> st;
            st.push(root);
            while (!st.empty()) {
                Node* curr = st.top(); st.pop();
                cout << curr->key << " ";              // visit on pop
                if (curr->right) st.push(curr->right); // right first …
                if (curr->left) st.push(curr->left);   // … so that left is popped next
            }
            cout << "\n";
        }

        int main() { preorder(sample()); }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void preorder(Node root) {
                if (root == null) return;
                Deque<Node> st = new ArrayDeque<>();
                st.push(root);
                StringBuilder sb = new StringBuilder();
                while (!st.isEmpty()) {
                    Node curr = st.pop();
                    sb.append(curr.key).append(' ');       // visit on pop
                    if (curr.right != null) st.push(curr.right);   // right first …
                    if (curr.left != null) st.push(curr.left);     // … so that left is popped next
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) { preorder(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function preorder(root) {
            if (!root) return;
            const st = [root], out = [];
            while (st.length) {
                const curr = st.pop();
                out.push(curr.key);                        // visit on pop
                if (curr.right) st.push(curr.right);       // right first …
                if (curr.left) st.push(curr.left);         // … so that left is popped next
            }
            console.log(out.join(" "));
        }

        preorder(sample());
    ''')
    yield complexity("O(n)", "O(n) worst case — the stack can hold up to half the nodes")
    yield idea("**Version 2 — push only right children (space-optimised).** Left children never need the stack: walk down the left spine printing each node as you go, and push only the **right** children you pass. When the spine ends, pop the most recent right child and continue from it. The stack now holds at most one node per level — `O(h)` instead of `O(n)`.")
    yield multi(r'''
        10 20 40 50 30 60 70 80 90
    ''', py=r'''
        class Node:
            def __init__(self, key, left=None, right=None):
                self.key, self.left, self.right = key, left, right

        def sample():
            return Node(10, Node(20, Node(40), Node(50)),
                            Node(30, Node(60), Node(70, Node(80), Node(90))))

        def preorder(root):
            stack, curr = [], root
            while stack or curr:
                while curr:
                    print(curr.key, end=" ")       # visit on the way down
                    if curr.right:
                        stack.append(curr.right)   # remember the right child for later
                    curr = curr.left               # keep walking the left spine
                if stack:
                    curr = stack.pop()             # resume at the most recent right child
            print()

        preorder(sample())
    ''', cpp=r'''
        #include <iostream>
        #include <stack>
        using namespace std;

        struct Node {
            int key; Node *left, *right;
            Node(int k, Node* l = nullptr, Node* r = nullptr) : key(k), left(l), right(r) {}
        };
        Node* sample() {
            return new Node(10, new Node(20, new Node(40), new Node(50)),
                                new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
        }

        void preorder(Node* root) {
            stack<Node*> st;
            Node* curr = root;
            while (!st.empty() || curr) {
                while (curr) {
                    cout << curr->key << " ";          // visit on the way down
                    if (curr->right) st.push(curr->right);   // remember the right child for later
                    curr = curr->left;                 // keep walking the left spine
                }
                if (!st.empty()) {
                    curr = st.top(); st.pop();         // resume at the most recent right child
                }
            }
            cout << "\n";
        }

        int main() { preorder(sample()); }
    ''', java=r'''
        import java.util.ArrayDeque;
        import java.util.Deque;

        public class Main {
            static class Node {
                int key; Node left, right;
                Node(int k) { key = k; }
                Node(int k, Node l, Node r) { key = k; left = l; right = r; }
            }
            static Node sample() {
                return new Node(10, new Node(20, new Node(40), new Node(50)),
                                    new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));
            }

            static void preorder(Node root) {
                Deque<Node> st = new ArrayDeque<>();
                Node curr = root;
                StringBuilder sb = new StringBuilder();
                while (!st.isEmpty() || curr != null) {
                    while (curr != null) {
                        sb.append(curr.key).append(' ');       // visit on the way down
                        if (curr.right != null) st.push(curr.right);   // remember the right child for later
                        curr = curr.left;                      // keep walking the left spine
                    }
                    if (!st.isEmpty()) curr = st.pop();        // resume at the most recent right child
                }
                System.out.println(sb.toString().trim());
            }

            public static void main(String[] args) { preorder(sample()); }
        }
    ''', js=r'''
        class Node {
            constructor(key, left = null, right = null) { this.key = key; this.left = left; this.right = right; }
        }
        const sample = () =>
            new Node(10, new Node(20, new Node(40), new Node(50)),
                         new Node(30, new Node(60), new Node(70, new Node(80), new Node(90))));

        function preorder(root) {
            const st = [], out = [];
            let curr = root;
            while (st.length || curr) {
                while (curr) {
                    out.push(curr.key);                        // visit on the way down
                    if (curr.right) st.push(curr.right);       // remember the right child for later
                    curr = curr.left;                          // keep walking the left spine
                }
                if (st.length) curr = st.pop();                // resume at the most recent right child
            }
            console.log(out.join(" "));
        }

        preorder(sample());
    ''')
    yield complexity("O(n)", "O(h) stack")
    yield table(
        ["Traversal", "Iterative trick", "Stack holds"],
        ["Inorder", "push the left spine, pop–print, go right", "`O(h)`"],
        ["Preorder v1", "pop–print, push right then left", "up to `O(n)`"],
        ["Preorder v2", "print on the way down the left spine, push right children only", "`O(h)`"],
        ["Postorder", "preorder with children swapped (root, right, left), then reverse the output — or two stacks", "`O(n)`"],
        ["Level order", "a queue instead of a stack", "`O(w)`"],
    )
    yield pitfall("Version 1 pushes the **right** child before the left. Push them the other way round and you get `10 30 70 90 80 60 20 50 40` — a mirrored preorder. The rule of thumb for every stack-based traversal: push in the *reverse* of the order you want to see.")

    # ───────────────────────── Q&A ─────────────────────────
    yield section("Interview Q&A", "message-question")
    yield qa("Height, depth, level, diameter — what is the difference, and does it count nodes or edges?",
             "**Depth** of a node is its distance from the root; **level** is depth (root = level 0). **Height** of a node is the longest downward path to a leaf; height of the tree is the root's height. **Diameter** is the longest path between any two nodes. Each may be counted in nodes or edges — the two conventions differ by one (a single node has height 1 in nodes, 0 in edges). These notes count nodes, like the original; say which you use before you code, and remember that the edge-diameter is `lh + rh` while the node-diameter is `1 + lh + rh`.")
    yield qa("Why does the 'return height, record the answer on the side' pattern keep showing up?",
             "Because many tree quantities (balanced, diameter, burn time, maximum path sum) are defined per node as a combination of its two subtree heights, yet a parent only needs the height back. A single post-order pass returns the height to the parent and updates a shared answer variable as a side effect — `O(n)` instead of the `O(n · h)` you get from calling `height()` afresh at every node. Balanced-check uses `−1` as a *poison* value so the recursion short-circuits.")
    yield qa("Which traversals uniquely determine a binary tree?",
             "Inorder together with preorder (or postorder) and distinct keys: the (pre/post)order supplies the root, the inorder splits left from right. Preorder + postorder alone do **not** (a root with a single child is ambiguous). Any single order determines a tree only if empties are recorded too — which is exactly the preorder-with-`−1` serialization. For a **BST** preorder alone suffices, since inorder is implied by sorting.")
    yield qa("How do the bottom view, top view and vertical traversal differ in code?",
             "All three run the same BFS with a horizontal distance per node and a map keyed by hd. Vertical traversal **appends** every key to its column; top view keeps the **first** key per column (`putIfAbsent`); bottom view keeps the **last** (overwrite on every visit). BFS, not DFS, is what guarantees the top-to-bottom, left-to-right tie-breaking.")
    yield qa("When would you choose the two-paths LCA over the single-traversal one?",
             "The single traversal is `O(n)` time, `O(h)` space and the version interviewers expect, but it silently returns a wrong node when one of the keys is absent. The two-paths method also runs in `O(n)` and reports a missing key honestly, at the cost of two traversals and two `O(h)` path lists. For BSTs neither is needed: walk down comparing keys in `O(h)`. For many LCA queries on a fixed tree, preprocess with binary lifting (`O(n log n)` build, `O(log n)` per query).")
    yield qa("Why is counting a complete binary tree `O(log² n)` and not `O(n)`?",
             "At any node of a complete tree the left or the right subtree is **perfect**, and a perfect subtree of height `h` has `2^h − 1` nodes without being visited. Measuring the left and right spine heights costs `O(log n)`; only one child needs a recursive call, so there are `O(log n)` such calls — `O(log n) × O(log n)`. The same completeness is why heaps fit in an array with children at `2i + 1` and `2i + 2`.")
