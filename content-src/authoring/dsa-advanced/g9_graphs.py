from kit import *
from dsakit import multi, complexity, io, diagram, idea, pitfall

G = "Graphs"


@topic(G, "graph", "Graph Data Structure", "topology-star")
def _():
    yield lead("A graph is a set of **vertices** joined by **edges** — the most general way to store pairwise relationships. Road maps, social networks, task dependencies and the web are all graphs, and almost every algorithm here (BFS, DFS, topological sort, Dijkstra, MST) is an interview staple.")
    yield define("Graph", "a pair `G = (V, E)` where `V` is a finite set of vertices (nodes) and `E` is a set of edges, each edge joining two vertices. Unlike a tree a graph may contain cycles, may be disconnected, and has no root.")
    yield diagram('''
        Graph                                    Tree
                                                 
        v1 ───── v3                                  v1
        │        │ ╲                                ╱  ╲
        │        │  v5                            v2    v3
        │        │ ╱
        v2 ───── v4

        V = {v1, v2, v3, v4, v5}
        E = {(v1,v2), (v1,v3), (v2,v4), (v3,v4), (v3,v5), (v4,v5)}
    ''', "A graph with |V| = 5 and |E| = 6, next to a tree (a connected graph with no cycles)")

    yield section("Graph vs tree", "binary-tree")
    yield table(
        ["", "Tree", "Graph"],
        ["Edges", "Exactly `n − 1` for `n` nodes", "Any number, `0 … V(V−1)/2` (undirected)"],
        ["Cycles", "Never", "Allowed"],
        ["Connected", "Always", "May be disconnected"],
        ["Root / hierarchy", "One root, parent → child", "No root; vertices are peers"],
        ["Traversal", "Pre/in/post-order, level order", "BFS / DFS with a `visited` array (cycles would loop forever)"],
    )
    yield note("A tree is a special case of a graph: a connected, acyclic, undirected graph. Everything that works on graphs works on trees, but tree algorithms rely on the absence of cycles and need `visited` bookkeeping before they can run on a graph.")

    yield section("Directed and undirected graphs", "arrows-right-left")
    yield diagram('''
        Directed graph                 Undirected graph

        v1 ─────▶ v3                   v1 ───── v3
        ▲         ▲                    │        │ ╲
        │         │                    │        │  v5
        │         │                    │        │ ╱
        v2 ─────▶ v4                   v2 ───── v4

        indegree(v3)  = 2              degree(v3) = 3
        outdegree(v3) = 0
    ''', "Edges with a direction (arcs) versus symmetric edges")
    yield table(
        ["", "Directed graph (digraph)", "Undirected graph"],
        ["Edge `(u, v)`", "Goes from `u` to `v` only", "Joins `u` and `v` both ways"],
        ["Degree", "`indegree(v)` = edges into `v`, `outdegree(v)` = edges out of `v`", "`degree(v)` = number of edges touching `v`"],
        ["Degree sum", "`Σ indegree = Σ outdegree = |E|`", "`Σ degree = 2·|E|` (every edge is counted at both ends)"],
        ["Maximum edges (no self-loops)", "`|V| · (|V| − 1)` — every ordered pair", "`|V| · (|V| − 1) / 2` — every unordered pair"],
        ["Examples", "Web links, task dependencies, follows on Twitter", "Roads, friendships, electrical circuits"],
    )
    yield formula("Undirected: 0 ≤ |E| ≤ |V|(|V|−1)/2        Directed: 0 ≤ |E| ≤ |V|(|V|−1)")
    yield note("The degree-sum formula (the *handshake lemma*) gives a quick sanity check: in an undirected graph the number of odd-degree vertices is always even. A graph with `|E|` close to the maximum is **dense**; one with `|E| ≈ |V|` is **sparse** — the distinction decides between the two representations below.")

    yield section("Walk, path and cycle", "route")
    yield p("In the undirected graph above:")
    yield ul(
        "**Walk** — any sequence of vertices where consecutive vertices are adjacent; vertices and edges may repeat: `v1, v2, v4, v3, v1, v2`.",
        "**Path** — a walk with no repeated vertex: `v1, v2, v4`.",
        "**Cycle** — a walk that starts and ends at the same vertex (a *simple* cycle repeats no other vertex): `v1, v2, v4, v3, v1`.",
        "**Connected** (undirected) — a path exists between every pair of vertices. **Strongly connected** (directed) — a directed path exists in both directions between every pair.",
    )
    yield cards(
        ("Cyclic directed", "A digraph that contains at least one directed cycle, e.g. `A → B → C → A`. Topological sort is impossible.", "repeat"),
        ("Cyclic undirected", "Any undirected graph with a cycle; a graph with more than `V − 1` edges is always cyclic.", "repeat"),
        ("Undirected acyclic", "A forest — each connected component is a tree, exactly `V − 1` edges when connected.", "binary-tree"),
        ("Directed acyclic (DAG)", "Directed with no cycles: dependency graphs, build systems, course prerequisites. Admits a topological order.", "git-branch"),
    )

    yield section("Weighted and unweighted graphs", "coin")
    yield diagram('''
        Weighted                             Unweighted

             10                              v1 ───── v3
        v1 ─────── v3                        │        │ ╲
        │          │ ╲ 5                     │        │  v5
     20 │       50 │  v5                     │        │ ╱
        │          │ ╱ 60                    v2 ───── v4
        v2 ─────── v4
             30
    ''', "A weight (cost, distance, time, capacity) on every edge, or none")
    yield ul(
        "**Unweighted** — every edge counts as 1. The shortest path is the one with the fewest edges and **BFS** finds it.",
        "**Weighted** — each edge carries a number. The shortest path minimises the sum of weights: **Dijkstra** (non-negative weights), **Bellman–Ford** (negative weights allowed), or a single pass over a topological order (DAGs).",
        "Weights can be negative; a **negative cycle** makes “shortest path” undefined because going round it again always lowers the total.",
    )

    yield section("Representation: adjacency matrix", "table")
    yield p("A `V × V` matrix with `mat[i][j] = 1` (or the weight) when there is an edge from `i` to `j`, else `0`. An undirected graph gives a symmetric matrix; a directed graph does not.")
    yield diagram('''
        Undirected                           Directed

        0 ───── 1          0 1 2 3          0 ────▶ 1           0 1 2 3
        │     ╱         0  0 1 1 0          │     ╱          0  0 1 1 0
        │   ╱           1  1 0 1 0          │   ╱            1  0 0 1 0
        │ ╱             2  1 1 0 1          ▼ ◀              2  0 0 0 1
        2 ───── 3       3  0 0 1 0          2 ────▶ 3        3  0 0 0 0
    ''', "Edges 0-1, 0-2, 1-2, 2-3 as a matrix — symmetric when undirected")
    yield multi('''
        0 1 1 0
        1 0 1 0
        1 1 0 1
        0 0 1 0
        adjacent(1, 2): true
        adjacent(0, 3): false
        degree(2): 3
    ''', py=r'''
        def build_matrix(n, edges, directed=False):
            mat = [[0] * n for _ in range(n)]
            for u, v in edges:
                mat[u][v] = 1
                if not directed:
                    mat[v][u] = 1              # undirected: the matrix is symmetric
            return mat

        edges = [(0, 1), (0, 2), (1, 2), (2, 3)]
        mat = build_matrix(4, edges)
        for row in mat:
            print(*row)
        print("adjacent(1, 2):", "true" if mat[1][2] else "false")   # O(1) lookup
        print("adjacent(0, 3):", "true" if mat[0][3] else "false")
        print("degree(2):", sum(mat[2]))                               # O(V): scan one row
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> buildMatrix(int n, const vector<pair<int,int>>& edges, bool directed) {
            vector<vector<int>> mat(n, vector<int>(n, 0));
            for (auto [u, v] : edges) {
                mat[u][v] = 1;
                if (!directed) mat[v][u] = 1;      // undirected: the matrix is symmetric
            }
            return mat;
        }

        int main() {
            vector<pair<int,int>> edges = {{0, 1}, {0, 2}, {1, 2}, {2, 3}};
            auto mat = buildMatrix(4, edges, false);
            for (auto& row : mat) {
                for (int x : row) cout << x << " ";
                cout << "\n";
            }
            cout << "adjacent(1, 2): " << (mat[1][2] ? "true" : "false") << "\n";   // O(1) lookup
            cout << "adjacent(0, 3): " << (mat[0][3] ? "true" : "false") << "\n";
            int deg = 0;
            for (int x : mat[2]) deg += x;                                           // O(V): scan one row
            cout << "degree(2): " << deg << "\n";
        }
    ''', java=r'''
        public class Main {
            static int[][] buildMatrix(int n, int[][] edges, boolean directed) {
                int[][] mat = new int[n][n];
                for (int[] e : edges) {
                    mat[e[0]][e[1]] = 1;
                    if (!directed) mat[e[1]][e[0]] = 1;    // undirected: the matrix is symmetric
                }
                return mat;
            }

            public static void main(String[] args) {
                int[][] edges = {{0, 1}, {0, 2}, {1, 2}, {2, 3}};
                int[][] mat = buildMatrix(4, edges, false);
                for (int[] row : mat) {
                    StringBuilder sb = new StringBuilder();
                    for (int x : row) sb.append(x).append(' ');
                    System.out.println(sb.toString().trim());
                }
                System.out.println("adjacent(1, 2): " + (mat[1][2] == 1 ? "true" : "false"));   // O(1) lookup
                System.out.println("adjacent(0, 3): " + (mat[0][3] == 1 ? "true" : "false"));
                int deg = 0;
                for (int x : mat[2]) deg += x;                                                    // O(V): scan one row
                System.out.println("degree(2): " + deg);
            }
        }
    ''', js=r'''
        function buildMatrix(n, edges, directed = false) {
            const mat = Array.from({ length: n }, () => new Array(n).fill(0));
            for (const [u, v] of edges) {
                mat[u][v] = 1;
                if (!directed) mat[v][u] = 1;          // undirected: the matrix is symmetric
            }
            return mat;
        }

        const edges = [[0, 1], [0, 2], [1, 2], [2, 3]];
        const mat = buildMatrix(4, edges);
        for (const row of mat) console.log(row.join(" "));
        console.log("adjacent(1, 2):", mat[1][2] ? "true" : "false");   // O(1) lookup
        console.log("adjacent(0, 3):", mat[0][3] ? "true" : "false");
        console.log("degree(2):", mat[2].reduce((a, b) => a + b, 0));   // O(V): scan one row
    ''')
    yield table(
        ["Adjacency matrix", "Cost"],
        ["Space", "`Θ(V²)` — even for a graph with very few edges"],
        ["Is `u` adjacent to `v`?", "`Θ(1)` — read `mat[u][v]`"],
        ["All neighbours of `u`", "`Θ(V)` — scan row `u`"],
        ["Degree of `u`", "`Θ(V)` — count the 1s in row `u`"],
        ["Add / remove an edge", "`Θ(1)`"],
        ["Add / remove a vertex", "`Θ(V²)` — the whole matrix is rebuilt"],
    )

    yield section("Vertices with arbitrary names", "hash")
    yield p("Algorithms index arrays by vertex number, but real vertices are cities, user ids or strings. Keep **two mappings**: a hash map `name → index` to translate input, and an array `index → name` (just the list of names) to translate results back. Everything in between runs on plain integers.")
    yield multi('''
        Delhi: Mumbai Kolkata
        Mumbai: Delhi Chennai
        Chennai: Mumbai Kolkata
        Kolkata: Delhi Chennai
        index of Chennai: 2
    ''', py=r'''
        names = ["Delhi", "Mumbai", "Chennai", "Kolkata"]
        index = {name: i for i, name in enumerate(names)}        # name -> vertex number
        edges = [("Delhi", "Mumbai"), ("Delhi", "Kolkata"), ("Mumbai", "Chennai"), ("Chennai", "Kolkata")]

        adj = [[] for _ in names]
        for a, b in edges:
            u, v = index[a], index[b]                             # translate once, on input
            adj[u].append(v)
            adj[v].append(u)

        for u, name in enumerate(names):                          # names[i] is the reverse mapping
            print(name + ":", " ".join(names[v] for v in adj[u]))
        print("index of Chennai:", index["Chennai"])
    ''', cpp=r'''
        #include <iostream>
        #include <string>
        #include <unordered_map>
        #include <vector>
        using namespace std;

        int main() {
            vector<string> names = {"Delhi", "Mumbai", "Chennai", "Kolkata"};
            unordered_map<string, int> index;                      // name -> vertex number
            for (int i = 0; i < (int)names.size(); i++) index[names[i]] = i;
            vector<pair<string, string>> edges = {{"Delhi", "Mumbai"}, {"Delhi", "Kolkata"},
                                                  {"Mumbai", "Chennai"}, {"Chennai", "Kolkata"}};

            vector<vector<int>> adj(names.size());
            for (auto& [a, b] : edges) {
                int u = index[a], v = index[b];                    // translate once, on input
                adj[u].push_back(v);
                adj[v].push_back(u);
            }

            for (int u = 0; u < (int)names.size(); u++) {         // names[i] is the reverse mapping
                cout << names[u] << ":";
                for (int v : adj[u]) cout << " " << names[v];
                cout << "\n";
            }
            cout << "index of Chennai: " << index["Chennai"] << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            public static void main(String[] args) {
                String[] names = {"Delhi", "Mumbai", "Chennai", "Kolkata"};
                Map<String, Integer> index = new HashMap<>();          // name -> vertex number
                for (int i = 0; i < names.length; i++) index.put(names[i], i);
                String[][] edges = {{"Delhi", "Mumbai"}, {"Delhi", "Kolkata"},
                                    {"Mumbai", "Chennai"}, {"Chennai", "Kolkata"}};

                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < names.length; i++) adj.add(new ArrayList<>());
                for (String[] e : edges) {
                    int u = index.get(e[0]), v = index.get(e[1]);    // translate once, on input
                    adj.get(u).add(v);
                    adj.get(v).add(u);
                }

                for (int u = 0; u < names.length; u++) {             // names[i] is the reverse mapping
                    StringBuilder sb = new StringBuilder(names[u] + ":");
                    for (int v : adj.get(u)) sb.append(' ').append(names[v]);
                    System.out.println(sb);
                }
                System.out.println("index of Chennai: " + index.get("Chennai"));
            }
        }
    ''', js=r'''
        const names = ["Delhi", "Mumbai", "Chennai", "Kolkata"];
        const index = new Map(names.map((name, i) => [name, i]));    // name -> vertex number
        const edges = [["Delhi", "Mumbai"], ["Delhi", "Kolkata"], ["Mumbai", "Chennai"], ["Chennai", "Kolkata"]];

        const adj = names.map(() => []);
        for (const [a, b] of edges) {
            const u = index.get(a), v = index.get(b);                // translate once, on input
            adj[u].push(v);
            adj[v].push(u);
        }

        names.forEach((name, u) =>                                   // names[i] is the reverse mapping
            console.log(name + ":", adj[u].map(v => names[v]).join(" ")));
        console.log("index of Chennai:", index.get("Chennai"));
    ''')

    yield section("Representation: adjacency list", "list")
    yield p("An array of `V` lists; `adj[u]` holds the neighbours of `u` (for a weighted graph, `(neighbour, weight)` pairs). The lists are usually dynamic arrays (`vector`, `ArrayList`, Python list) — linked lists also work but are slower to scan. This is the default representation for every algorithm in these notes.")
    yield diagram('''
        0 ───── 1            adj[0] → 1 → 2
        │     ╱              adj[1] → 0 → 2
        │   ╱                adj[2] → 0 → 1 → 3
        │ ╱                  adj[3] → 2
        2 ───── 3
    ''', "The same undirected graph as a list of neighbour lists — each edge appears twice")
    yield multi('''
        0: 1 2
        1: 0 2
        2: 0 1 3
        3: 2
        degree(2): 3
        has edge 1-3: false
    ''', py=r'''
        def build(n, edges, directed=False):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                if not directed:
                    adj[v].append(u)               # undirected: store the edge at both ends
            return adj

        adj = build(4, [(0, 1), (0, 2), (1, 2), (2, 3)])
        for u in range(len(adj)):
            print(f"{u}:", *adj[u])
        print("degree(2):", len(adj[2]))                               # O(1)
        print("has edge 1-3:", "true" if 3 in adj[1] else "false")     # O(degree(1)) scan
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges, bool directed) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) {
                adj[u].push_back(v);
                if (!directed) adj[v].push_back(u);    // undirected: store the edge at both ends
            }
            return adj;
        }

        int main() {
            auto adj = build(4, {{0, 1}, {0, 2}, {1, 2}, {2, 3}}, false);
            for (int u = 0; u < (int)adj.size(); u++) {
                cout << u << ":";
                for (int v : adj[u]) cout << " " << v;
                cout << "\n";
            }
            cout << "degree(2): " << adj[2].size() << "\n";                       // O(1)
            bool has = find(adj[1].begin(), adj[1].end(), 3) != adj[1].end();   // O(degree(1)) scan
            cout << "has edge 1-3: " << (has ? "true" : "false") << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges, boolean directed) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) {
                    adj.get(e[0]).add(e[1]);
                    if (!directed) adj.get(e[1]).add(e[0]);   // undirected: store the edge at both ends
                }
                return adj;
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(4, new int[][]{{0, 1}, {0, 2}, {1, 2}, {2, 3}}, false);
                for (int u = 0; u < adj.size(); u++) {
                    StringBuilder sb = new StringBuilder(u + ":");
                    for (int v : adj.get(u)) sb.append(' ').append(v);
                    System.out.println(sb);
                }
                System.out.println("degree(2): " + adj.get(2).size());                    // O(1)
                System.out.println("has edge 1-3: " + (adj.get(1).contains(3) ? "true" : "false"));   // O(degree(1))
            }
        }
    ''', js=r'''
        function build(n, edges, directed = false) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) {
                adj[u].push(v);
                if (!directed) adj[v].push(u);         // undirected: store the edge at both ends
            }
            return adj;
        }

        const adj = build(4, [[0, 1], [0, 2], [1, 2], [2, 3]]);
        adj.forEach((nbrs, u) => console.log(`${u}:`, nbrs.join(" ")));
        console.log("degree(2):", adj[2].length);                                 // O(1)
        console.log("has edge 1-3:", adj[1].includes(3) ? "true" : "false");      // O(degree(1)) scan
    ''')
    yield table(
        ["Adjacency list", "Cost"],
        ["Space", "`Θ(V + E)` — `V + 2E` list entries undirected, `V + E` directed"],
        ["Is `u` adjacent to `v`?", "`O(degree(u))` — scan `adj[u]` (`O(1)` if each list is a hash set)"],
        ["All neighbours of `u`", "`Θ(degree(u))`"],
        ["Degree of `u`", "`Θ(1)` — the list length"],
        ["Add an edge", "`Θ(1)` — append"],
        ["Remove an edge", "`O(degree(u))` — find it first"],
    )

    yield section("Adjacency list vs adjacency matrix", "arrows-shuffle")
    yield table(
        ["Operation", "Adjacency list", "Adjacency matrix"],
        ["Memory", "`Θ(V + E)`", "`Θ(V²)`"],
        ["Is there an edge `u → v`?", "`O(degree(u))`, worst `O(V)`", "`Θ(1)`"],
        ["Visit all neighbours of `u`", "`Θ(degree(u))`", "`Θ(V)`"],
        ["Add an edge", "`Θ(1)`", "`Θ(1)`"],
        ["Remove an edge", "`O(V)`", "`Θ(1)`"],
        ["Whole traversal (BFS / DFS)", "`Θ(V + E)`", "`Θ(V²)`"],
    )
    yield note("Use the **list** for sparse graphs (`E ≈ V`, which is nearly every real graph — a road network or social graph has far fewer than `V²` edges) and whenever you traverse. Use the **matrix** for dense graphs, when edge lookups dominate, or for matrix algorithms such as Floyd–Warshall. The matrix also stores *redundant* information for undirected graphs: both `mat[u][v]` and `mat[v][u]`.")

    yield section("Breadth First Search (BFS)", "arrows-horizontal")
    yield p("BFS explores a graph **level by level** from a source: first the source, then every vertex one edge away, then two edges away, and so on. A queue holds the frontier; a `visited` array stops cycles from being walked twice.")
    yield diagram('''
        0 ───── 1          level 0:  0
        │       │          level 1:  1 2
        2 ───── 3          level 2:  3 4
        │       │          level 3:  5
        4 ───── 5
    ''', "The traversal graph used for BFS and DFS: edges 0-1, 0-2, 1-3, 2-3, 2-4, 3-5, 4-5")
    yield io("edges = 0-1, 0-2, 1-3, 2-3, 2-4, 3-5, 4-5, s = 0", "0 1 2 3 4 5", "same graph, s = 2", "2 0 3 4 1 5")
    yield idea("Mark the source visited and enqueue it. Repeatedly dequeue a vertex, output it, and enqueue every **unvisited** neighbour, marking it visited the moment it is enqueued. Because the queue is FIFO, all vertices at distance `d` leave the queue before any vertex at distance `d + 1` — which is exactly what makes BFS find shortest paths in unweighted graphs.")
    yield multi('''
        from 0: 0 1 2 3 4 5
        from 2: 2 0 3 4 1 5
    ''', py=r'''
        from collections import deque

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def bfs(adj, s):
            visited = [False] * len(adj)
            order = []
            q = deque([s])
            visited[s] = True                 # mark when enqueued, not when dequeued
            while q:
                u = q.popleft()
                order.append(u)
                for v in adj[u]:
                    if not visited[v]:
                        visited[v] = True
                        q.append(v)
            return order

        adj = build(6, [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])
        print("from 0:", *bfs(adj, 0))
        print("from 2:", *bfs(adj, 2))
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        vector<int> bfs(const vector<vector<int>>& adj, int s) {
            vector<bool> visited(adj.size(), false);
            vector<int> order;
            queue<int> q;
            q.push(s);
            visited[s] = true;                 // mark when enqueued, not when dequeued
            while (!q.empty()) {
                int u = q.front(); q.pop();
                order.push_back(u);
                for (int v : adj[u])
                    if (!visited[v]) { visited[v] = true; q.push(v); }
            }
            return order;
        }

        int main() {
            auto adj = build(6, {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {2, 4}, {3, 5}, {4, 5}});
            for (int s : {0, 2}) {
                cout << "from " << s << ":";
                for (int u : bfs(adj, s)) cout << " " << u;
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static List<Integer> bfs(List<List<Integer>> adj, int s) {
                boolean[] visited = new boolean[adj.size()];
                List<Integer> order = new ArrayList<>();
                Deque<Integer> q = new ArrayDeque<>();
                q.add(s);
                visited[s] = true;                 // mark when enqueued, not when dequeued
                while (!q.isEmpty()) {
                    int u = q.poll();
                    order.add(u);
                    for (int v : adj.get(u))
                        if (!visited[v]) { visited[v] = true; q.add(v); }
                }
                return order;
            }

            static String join(List<Integer> xs) {
                StringBuilder sb = new StringBuilder();
                for (int x : xs) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(6, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {2, 4}, {3, 5}, {4, 5}});
                System.out.println("from 0: " + join(bfs(adj, 0)));
                System.out.println("from 2: " + join(bfs(adj, 2)));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function bfs(adj, s) {
            const visited = new Array(adj.length).fill(false);
            const order = [];
            const q = [s];
            let head = 0;                      // index into q: shift() would be O(n)
            visited[s] = true;                 // mark when enqueued, not when dequeued
            while (head < q.length) {
                const u = q[head++];
                order.push(u);
                for (const v of adj[u])
                    if (!visited[v]) { visited[v] = true; q.push(v); }
            }
            return order;
        }

        const adj = build(6, [[0, 1], [0, 2], [1, 3], [2, 3], [2, 4], [3, 5], [4, 5]]);
        console.log("from 0:", bfs(adj, 0).join(" "));
        console.log("from 2:", bfs(adj, 2).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield pitfall("Marking a vertex visited when it is **dequeued** instead of when it is **enqueued** lets the same vertex enter the queue several times (once per neighbour that sees it) — correct output on small graphs, but up to `O(E)` queue entries and duplicated work on large ones.")

    yield section("BFS on a disconnected graph and counting components", "grid-dots")
    yield p("A single BFS only reaches the source's component. To cover a graph that may be disconnected, loop over every vertex and start a new BFS from each one that is still unvisited. Every restart is one more **connected component**.")
    yield diagram('''
        0 ───── 2        3 ───── 4        5 ───── 7
                │                         │     ╱
                │                         │   ╱
                1                         6 ╱
    ''', "A graph with 3 connected components: edges 0-2, 2-1, 3-4, 5-7, 5-6, 6-7")
    yield io("edges = 0-2, 2-1, 3-4, 5-7, 5-6, 6-7, V = 8", "3 components: {0,2,1} {3,4} {5,7,6}")
    yield idea("Share one `visited` array across all the BFS calls. The outer loop `for u in 0..V-1` finds the next unvisited vertex; each BFS from it visits exactly its component, so the number of BFS calls equals the number of components.")
    yield multi('''
        component 1: 0 2 1
        component 2: 3 4
        component 3: 5 7 6
        components: 3
    ''', py=r'''
        from collections import deque

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def bfs(adj, s, visited):             # visits the component of s, returns it in BFS order
            comp = []
            q = deque([s])
            visited[s] = True
            while q:
                u = q.popleft()
                comp.append(u)
                for v in adj[u]:
                    if not visited[v]:
                        visited[v] = True
                        q.append(v)
            return comp

        def bfs_all(adj):
            visited = [False] * len(adj)      # shared by every BFS call
            count = 0
            for u in range(len(adj)):
                if not visited[u]:            # a fresh start = a new component
                    count += 1
                    print(f"component {count}:", *bfs(adj, u, visited))
            return count

        adj = build(8, [(0, 2), (2, 1), (3, 4), (5, 7), (5, 6), (6, 7)])
        print("components:", bfs_all(adj))
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        vector<int> bfs(const vector<vector<int>>& adj, int s, vector<bool>& visited) {
            vector<int> comp;                  // the component of s, in BFS order
            queue<int> q;
            q.push(s);
            visited[s] = true;
            while (!q.empty()) {
                int u = q.front(); q.pop();
                comp.push_back(u);
                for (int v : adj[u])
                    if (!visited[v]) { visited[v] = true; q.push(v); }
            }
            return comp;
        }

        int bfsAll(const vector<vector<int>>& adj) {
            vector<bool> visited(adj.size(), false);   // shared by every BFS call
            int count = 0;
            for (int u = 0; u < (int)adj.size(); u++) {
                if (visited[u]) continue;
                count++;                                 // a fresh start = a new component
                cout << "component " << count << ":";
                for (int x : bfs(adj, u, visited)) cout << " " << x;
                cout << "\n";
            }
            return count;
        }

        int main() {
            auto adj = build(8, {{0, 2}, {2, 1}, {3, 4}, {5, 7}, {5, 6}, {6, 7}});
            int total = bfsAll(adj);
            cout << "components: " << total << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static List<Integer> bfs(List<List<Integer>> adj, int s, boolean[] visited) {
                List<Integer> comp = new ArrayList<>();   // the component of s, in BFS order
                Deque<Integer> q = new ArrayDeque<>();
                q.add(s);
                visited[s] = true;
                while (!q.isEmpty()) {
                    int u = q.poll();
                    comp.add(u);
                    for (int v : adj.get(u))
                        if (!visited[v]) { visited[v] = true; q.add(v); }
                }
                return comp;
            }

            static int bfsAll(List<List<Integer>> adj) {
                boolean[] visited = new boolean[adj.size()];   // shared by every BFS call
                int count = 0;
                for (int u = 0; u < adj.size(); u++) {
                    if (visited[u]) continue;
                    count++;                                     // a fresh start = a new component
                    StringBuilder sb = new StringBuilder("component " + count + ":");
                    for (int x : bfs(adj, u, visited)) sb.append(' ').append(x);
                    System.out.println(sb);
                }
                return count;
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(8, new int[][]{{0, 2}, {2, 1}, {3, 4}, {5, 7}, {5, 6}, {6, 7}});
                System.out.println("components: " + bfsAll(adj));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function bfs(adj, s, visited) {        // visits the component of s, returns it in BFS order
            const comp = [];
            const q = [s];
            let head = 0;
            visited[s] = true;
            while (head < q.length) {
                const u = q[head++];
                comp.push(u);
                for (const v of adj[u])
                    if (!visited[v]) { visited[v] = true; q.push(v); }
            }
            return comp;
        }

        function bfsAll(adj) {
            const visited = new Array(adj.length).fill(false);   // shared by every BFS call
            let count = 0;
            for (let u = 0; u < adj.length; u++) {
                if (visited[u]) continue;
                count++;                                           // a fresh start = a new component
                console.log(`component ${count}:`, bfs(adj, u, visited).join(" "));
            }
            return count;
        }

        const adj = build(8, [[0, 2], [2, 1], [3, 4], [5, 7], [5, 6], [6, 7]]);
        console.log("components:", bfsAll(adj));
    ''')
    yield complexity("O(V + E)", "O(V)")

    yield section("Shortest path in an unweighted graph (BFS distances)", "route")
    yield p("Because BFS visits vertices in order of their distance from the source, the first time it reaches a vertex is along a shortest path. Record `dist[v] = dist[u] + 1` and `parent[v] = u` when `v` is enqueued from `u`; following `parent` backwards from any vertex rebuilds the path.")
    yield diagram('''
        0 ───── 1                          dist:  0  1  1  2  3  4  4
        │       │                          vertex 0  1  2  3  4  5  6
        2 ───── 3 ───── 4 ───── 5
                        │
                        6
    ''', "Edges 0-1, 0-2, 1-3, 2-3, 3-4, 4-5, 4-6; distances from 0")
    yield io("edges = 0-1, 0-2, 1-3, 2-3, 3-4, 4-5, 4-6, s = 0", "dist = 0 1 1 2 3 4 4, path 0→5 = 0 1 3 4 5")
    yield idea("Initialise every distance to `-1` (unreached). The `visited` array becomes unnecessary: `dist[v] == -1` means not yet seen. A vertex that is still `-1` after BFS is unreachable from the source.")
    yield multi('''
        0: 0
        1: 1
        2: 1
        3: 2
        4: 3
        5: 4
        6: 4
        path 0 -> 5: 0 1 3 4 5
    ''', py=r'''
        from collections import deque

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def bfs_distances(adj, s):
            n = len(adj)
            dist = [-1] * n                   # -1 = not reached yet (doubles as visited)
            parent = [-1] * n
            dist[s] = 0
            q = deque([s])
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1 # one more edge than u
                        parent[v] = u
                        q.append(v)
            return dist, parent

        def path_to(parent, t):
            path = []
            while t != -1:                    # walk back to the source
                path.append(t)
                t = parent[t]
            return path[::-1]

        adj = build(7, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (4, 6)])
        dist, parent = bfs_distances(adj, 0)
        for v in range(len(adj)):
            print(f"{v}: {dist[v]}")
        print("path 0 -> 5:", *path_to(parent, 5))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        void bfsDistances(const vector<vector<int>>& adj, int s, vector<int>& dist, vector<int>& parent) {
            int n = adj.size();
            dist.assign(n, -1);                // -1 = not reached yet (doubles as visited)
            parent.assign(n, -1);
            dist[s] = 0;
            queue<int> q;
            q.push(s);
            while (!q.empty()) {
                int u = q.front(); q.pop();
                for (int v : adj[u])
                    if (dist[v] == -1) {
                        dist[v] = dist[u] + 1; // one more edge than u
                        parent[v] = u;
                        q.push(v);
                    }
            }
        }

        vector<int> pathTo(const vector<int>& parent, int t) {
            vector<int> path;
            for (; t != -1; t = parent[t]) path.push_back(t);   // walk back to the source
            reverse(path.begin(), path.end());
            return path;
        }

        int main() {
            auto adj = build(7, {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}, {4, 6}});
            vector<int> dist, parent;
            bfsDistances(adj, 0, dist, parent);
            for (int v = 0; v < (int)adj.size(); v++) cout << v << ": " << dist[v] << "\n";
            cout << "path 0 -> 5:";
            for (int v : pathTo(parent, 5)) cout << " " << v;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static int[] parent;

            static int[] bfsDistances(List<List<Integer>> adj, int s) {
                int n = adj.size();
                int[] dist = new int[n];
                parent = new int[n];
                Arrays.fill(dist, -1);             // -1 = not reached yet (doubles as visited)
                Arrays.fill(parent, -1);
                dist[s] = 0;
                Deque<Integer> q = new ArrayDeque<>();
                q.add(s);
                while (!q.isEmpty()) {
                    int u = q.poll();
                    for (int v : adj.get(u))
                        if (dist[v] == -1) {
                            dist[v] = dist[u] + 1; // one more edge than u
                            parent[v] = u;
                            q.add(v);
                        }
                }
                return dist;
            }

            static List<Integer> pathTo(int t) {
                List<Integer> path = new ArrayList<>();
                for (; t != -1; t = parent[t]) path.add(t);   // walk back to the source
                Collections.reverse(path);
                return path;
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(7, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}, {4, 6}});
                int[] dist = bfsDistances(adj, 0);
                for (int v = 0; v < adj.size(); v++) System.out.println(v + ": " + dist[v]);
                StringBuilder sb = new StringBuilder("path 0 -> 5:");
                for (int v : pathTo(5)) sb.append(' ').append(v);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function bfsDistances(adj, s) {
            const n = adj.length;
            const dist = new Array(n).fill(-1);    // -1 = not reached yet (doubles as visited)
            const parent = new Array(n).fill(-1);
            dist[s] = 0;
            const q = [s];
            let head = 0;
            while (head < q.length) {
                const u = q[head++];
                for (const v of adj[u])
                    if (dist[v] === -1) {
                        dist[v] = dist[u] + 1;     // one more edge than u
                        parent[v] = u;
                        q.push(v);
                    }
            }
            return { dist, parent };
        }

        function pathTo(parent, t) {
            const path = [];
            for (; t !== -1; t = parent[t]) path.push(t);   // walk back to the source
            return path.reverse();
        }

        const adj = build(7, [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [4, 5], [4, 6]]);
        const { dist, parent } = bfsDistances(adj, 0);
        dist.forEach((d, v) => console.log(`${v}: ${d}`));
        console.log("path 0 -> 5:", pathTo(parent, 5).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield note("This only works when every edge costs the same. With weights, a path with more edges can be cheaper — that is what Dijkstra and Bellman–Ford handle below.")

    yield section("Applications of BFS", "apps")
    yield cards(
        ("Shortest path, unweighted", "Fewest hops between two vertices — road hops, degrees of separation, moves in a puzzle.", "route"),
        ("Web crawlers", "Start at a seed page and visit links level by level, so nearby pages are indexed first.", "world"),
        ("Peer-to-peer networks", "Finding neighbouring peers (e.g. BitTorrent) — close nodes are discovered before distant ones.", "topology-star"),
        ("Social network search", "Friends within `k` hops, friend suggestions: a BFS cut off at depth `k`.", "users"),
        ("Garbage collection", "Cheney's copying collector is a BFS over live objects starting from the roots.", "trash"),
        ("Cycle detection", "In an undirected graph a visited neighbour that is not the parent closes a cycle.", "repeat"),
        ("Broadcasting", "A message sent to all neighbours, who forward it to theirs — flooding in networks.", "broadcast"),
        ("Max flow (Edmonds–Karp)", "Ford–Fulkerson with BFS to pick the shortest augmenting path each round.", "arrows-split"),
        cols=3,
    )

    yield section("Depth First Search (DFS)", "arrows-vertical")
    yield p("DFS goes **as deep as possible** before backtracking: from the current vertex it recurses into the first unvisited neighbour, and only when that whole branch is exhausted does it try the next neighbour. The recursion stack (or an explicit stack) replaces BFS's queue.")
    yield io("edges = 0-1, 0-2, 1-3, 2-3, 2-4, 3-5, 4-5, s = 0", "0 1 3 2 4 5", "same graph, s = 2", "2 0 1 3 5 4")
    yield idea("`dfs(u)`: mark `u` visited, output it, then `dfs(v)` for every unvisited neighbour `v`. The `visited` check is what prevents an infinite loop on cycles — compare the tree traversals, which need no such check.")
    yield multi('''
        from 0: 0 1 3 2 4 5
        from 2: 2 0 1 3 5 4
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def dfs_rec(adj, u, visited, order):
            visited[u] = True
            order.append(u)                   # pre-order: record u on entry
            for v in adj[u]:
                if not visited[v]:
                    dfs_rec(adj, v, visited, order)

        def dfs(adj, s):
            visited = [False] * len(adj)
            order = []
            dfs_rec(adj, s, visited, order)
            return order

        adj = build(6, [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])
        print("from 0:", *dfs(adj, 0))
        print("from 2:", *dfs(adj, 2))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        void dfsRec(const vector<vector<int>>& adj, int u, vector<bool>& visited, vector<int>& order) {
            visited[u] = true;
            order.push_back(u);                // pre-order: record u on entry
            for (int v : adj[u])
                if (!visited[v]) dfsRec(adj, v, visited, order);
        }

        vector<int> dfs(const vector<vector<int>>& adj, int s) {
            vector<bool> visited(adj.size(), false);
            vector<int> order;
            dfsRec(adj, s, visited, order);
            return order;
        }

        int main() {
            auto adj = build(6, {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {2, 4}, {3, 5}, {4, 5}});
            for (int s : {0, 2}) {
                cout << "from " << s << ":";
                for (int u : dfs(adj, s)) cout << " " << u;
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static void dfsRec(List<List<Integer>> adj, int u, boolean[] visited, List<Integer> order) {
                visited[u] = true;
                order.add(u);                      // pre-order: record u on entry
                for (int v : adj.get(u))
                    if (!visited[v]) dfsRec(adj, v, visited, order);
            }

            static List<Integer> dfs(List<List<Integer>> adj, int s) {
                boolean[] visited = new boolean[adj.size()];
                List<Integer> order = new ArrayList<>();
                dfsRec(adj, s, visited, order);
                return order;
            }

            static String join(List<Integer> xs) {
                StringBuilder sb = new StringBuilder();
                for (int x : xs) sb.append(sb.length() == 0 ? "" : " ").append(x);
                return sb.toString();
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(6, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {2, 4}, {3, 5}, {4, 5}});
                System.out.println("from 0: " + join(dfs(adj, 0)));
                System.out.println("from 2: " + join(dfs(adj, 2)));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function dfsRec(adj, u, visited, order) {
            visited[u] = true;
            order.push(u);                         // pre-order: record u on entry
            for (const v of adj[u])
                if (!visited[v]) dfsRec(adj, v, visited, order);
        }

        function dfs(adj, s) {
            const visited = new Array(adj.length).fill(false);
            const order = [];
            dfsRec(adj, s, visited, order);
            return order;
        }

        const adj = build(6, [[0, 1], [0, 2], [1, 3], [2, 3], [2, 4], [3, 5], [4, 5]]);
        console.log("from 0:", dfs(adj, 0).join(" "));
        console.log("from 2:", dfs(adj, 2).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V) for visited + recursion stack")
    yield pitfall("Recursive DFS on a long path uses one stack frame per vertex: Python stops at ~1000 frames and Java/C++ crash on graphs with tens of thousands of vertices in a chain. For large inputs convert to an explicit stack — but note that the naive iterative version (push all neighbours, pop one) visits in a *different* order than the recursive one.")

    yield section("DFS on a disconnected graph and counting components", "grid-dots")
    yield p("Exactly as with BFS: an outer loop over all vertices, a shared `visited` array, and one recursive DFS per unvisited vertex. The number of calls made by the outer loop is the number of connected components.")
    yield io("edges = 0-2, 2-1, 3-4, 5-7, 5-6, 6-7, V = 8", "3 components")
    yield multi('''
        component 1: 0 2 1
        component 2: 3 4
        component 3: 5 7 6
        components: 3
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def dfs_rec(adj, u, visited, comp):
            visited[u] = True
            comp.append(u)
            for v in adj[u]:
                if not visited[v]:
                    dfs_rec(adj, v, visited, comp)

        def count_components(adj):
            visited = [False] * len(adj)      # shared by every DFS call
            count = 0
            for u in range(len(adj)):
                if not visited[u]:            # unvisited vertex = start of a new component
                    count += 1
                    comp = []
                    dfs_rec(adj, u, visited, comp)
                    print(f"component {count}:", *comp)
            return count

        adj = build(8, [(0, 2), (2, 1), (3, 4), (5, 7), (5, 6), (6, 7)])
        print("components:", count_components(adj))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        void dfsRec(const vector<vector<int>>& adj, int u, vector<bool>& visited, vector<int>& comp) {
            visited[u] = true;
            comp.push_back(u);
            for (int v : adj[u])
                if (!visited[v]) dfsRec(adj, v, visited, comp);
        }

        int countComponents(const vector<vector<int>>& adj) {
            vector<bool> visited(adj.size(), false);   // shared by every DFS call
            int count = 0;
            for (int u = 0; u < (int)adj.size(); u++) {
                if (visited[u]) continue;                // unvisited vertex = start of a new component
                count++;
                vector<int> comp;
                dfsRec(adj, u, visited, comp);
                cout << "component " << count << ":";
                for (int x : comp) cout << " " << x;
                cout << "\n";
            }
            return count;
        }

        int main() {
            auto adj = build(8, {{0, 2}, {2, 1}, {3, 4}, {5, 7}, {5, 6}, {6, 7}});
            int total = countComponents(adj);
            cout << "components: " << total << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static void dfsRec(List<List<Integer>> adj, int u, boolean[] visited, List<Integer> comp) {
                visited[u] = true;
                comp.add(u);
                for (int v : adj.get(u))
                    if (!visited[v]) dfsRec(adj, v, visited, comp);
            }

            static int countComponents(List<List<Integer>> adj) {
                boolean[] visited = new boolean[adj.size()];   // shared by every DFS call
                int count = 0;
                for (int u = 0; u < adj.size(); u++) {
                    if (visited[u]) continue;                    // unvisited vertex = start of a new component
                    count++;
                    List<Integer> comp = new ArrayList<>();
                    dfsRec(adj, u, visited, comp);
                    StringBuilder sb = new StringBuilder("component " + count + ":");
                    for (int x : comp) sb.append(' ').append(x);
                    System.out.println(sb);
                }
                return count;
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(8, new int[][]{{0, 2}, {2, 1}, {3, 4}, {5, 7}, {5, 6}, {6, 7}});
                System.out.println("components: " + countComponents(adj));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function dfsRec(adj, u, visited, comp) {
            visited[u] = true;
            comp.push(u);
            for (const v of adj[u])
                if (!visited[v]) dfsRec(adj, v, visited, comp);
        }

        function countComponents(adj) {
            const visited = new Array(adj.length).fill(false);   // shared by every DFS call
            let count = 0;
            for (let u = 0; u < adj.length; u++) {
                if (visited[u]) continue;                          // unvisited vertex = start of a new component
                count++;
                const comp = [];
                dfsRec(adj, u, visited, comp);
                console.log(`component ${count}:`, comp.join(" "));
            }
            return count;
        }

        const adj = build(8, [[0, 2], [2, 1], [3, 4], [5, 7], [5, 6], [6, 7]]);
        console.log("components:", countComponents(adj));
    ''')
    yield complexity("O(V + E)", "O(V)")

    yield section("Applications of DFS", "apps")
    yield ul(
        "**Cycle detection** — a back edge to a vertex that is still on the recursion stack (directed) or to a visited non-parent (undirected).",
        "**Topological sorting** — vertices in decreasing order of DFS finish time.",
        "**Strongly connected components** — Kosaraju's and Tarjan's algorithms are two DFS passes, or one DFS with low-link values.",
        "**Mazes and puzzles** — explore one path to the end before trying another; backtracking is DFS over the state space.",
        "**Path finding** — any path (not necessarily shortest) between two vertices; articulation points and bridges via discovery times.",
    )
    yield table(
        ["", "BFS", "DFS"],
        ["Data structure", "Queue", "Stack / recursion"],
        ["Visits", "By distance (level order)", "Along one branch, then backtracks"],
        ["Finds shortest paths (unweighted)", "Yes", "No"],
        ["Memory", "`O(width)` — the frontier", "`O(depth)` — the current path"],
        ["Typical uses", "Shortest path, nearest neighbour, level-wise processing", "Cycles, topological order, SCCs, connectivity, backtracking"],
    )

    yield section("Detect a cycle in an undirected graph", "repeat")
    yield diagram('''
        Graph 1 (cycle)              Graph 2 (no cycle — a tree)

        0 ───── 1 ───── 2            0 ───── 1 ───── 2
                │     ╱                      │
                │   ╱                        │
                3 ╱                          3
    ''', "Edges 0-1, 1-2, 1-3, 2-3 versus 0-1, 1-2, 1-3")
    yield io("edges = 0-1, 1-2, 1-3, 2-3", "cycle", "edges = 0-1, 1-2, 1-3", "no cycle")
    yield idea("Run DFS remembering each vertex's **parent** (the vertex we came from). Reaching a neighbour that is already visited and is *not* the parent means there are two different routes to it — a cycle. Without the parent check every undirected edge would look like a cycle, because `u → v` and `v → u` are the same edge.")
    yield multi('''
        graph 1: cycle
        graph 2: no cycle
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def has_cycle_from(adj, u, parent, visited):
            visited[u] = True
            for v in adj[u]:
                if not visited[v]:
                    if has_cycle_from(adj, v, u, visited):
                        return True
                elif v != parent:             # visited, and not the edge we arrived by -> cycle
                    return True
            return False

        def has_cycle(adj):
            visited = [False] * len(adj)
            for u in range(len(adj)):         # every component
                if not visited[u] and has_cycle_from(adj, u, -1, visited):
                    return True
            return False

        g1 = build(4, [(0, 1), (1, 2), (1, 3), (2, 3)])
        g2 = build(4, [(0, 1), (1, 2), (1, 3)])
        print("graph 1:", "cycle" if has_cycle(g1) else "no cycle")
        print("graph 2:", "cycle" if has_cycle(g2) else "no cycle")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        bool hasCycleFrom(const vector<vector<int>>& adj, int u, int parent, vector<bool>& visited) {
            visited[u] = true;
            for (int v : adj[u]) {
                if (!visited[v]) {
                    if (hasCycleFrom(adj, v, u, visited)) return true;
                } else if (v != parent) {      // visited, and not the edge we arrived by -> cycle
                    return true;
                }
            }
            return false;
        }

        bool hasCycle(const vector<vector<int>>& adj) {
            vector<bool> visited(adj.size(), false);
            for (int u = 0; u < (int)adj.size(); u++)   // every component
                if (!visited[u] && hasCycleFrom(adj, u, -1, visited)) return true;
            return false;
        }

        int main() {
            auto g1 = build(4, {{0, 1}, {1, 2}, {1, 3}, {2, 3}});
            auto g2 = build(4, {{0, 1}, {1, 2}, {1, 3}});
            cout << "graph 1: " << (hasCycle(g1) ? "cycle" : "no cycle") << "\n";
            cout << "graph 2: " << (hasCycle(g2) ? "cycle" : "no cycle") << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static boolean hasCycleFrom(List<List<Integer>> adj, int u, int parent, boolean[] visited) {
                visited[u] = true;
                for (int v : adj.get(u)) {
                    if (!visited[v]) {
                        if (hasCycleFrom(adj, v, u, visited)) return true;
                    } else if (v != parent) {      // visited, and not the edge we arrived by -> cycle
                        return true;
                    }
                }
                return false;
            }

            static boolean hasCycle(List<List<Integer>> adj) {
                boolean[] visited = new boolean[adj.size()];
                for (int u = 0; u < adj.size(); u++)   // every component
                    if (!visited[u] && hasCycleFrom(adj, u, -1, visited)) return true;
                return false;
            }

            public static void main(String[] args) {
                List<List<Integer>> g1 = build(4, new int[][]{{0, 1}, {1, 2}, {1, 3}, {2, 3}});
                List<List<Integer>> g2 = build(4, new int[][]{{0, 1}, {1, 2}, {1, 3}});
                System.out.println("graph 1: " + (hasCycle(g1) ? "cycle" : "no cycle"));
                System.out.println("graph 2: " + (hasCycle(g2) ? "cycle" : "no cycle"));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function hasCycleFrom(adj, u, parent, visited) {
            visited[u] = true;
            for (const v of adj[u]) {
                if (!visited[v]) {
                    if (hasCycleFrom(adj, v, u, visited)) return true;
                } else if (v !== parent) {         // visited, and not the edge we arrived by -> cycle
                    return true;
                }
            }
            return false;
        }

        function hasCycle(adj) {
            const visited = new Array(adj.length).fill(false);
            for (let u = 0; u < adj.length; u++)   // every component
                if (!visited[u] && hasCycleFrom(adj, u, -1, visited)) return true;
            return false;
        }

        const g1 = build(4, [[0, 1], [1, 2], [1, 3], [2, 3]]);
        const g2 = build(4, [[0, 1], [1, 2], [1, 3]]);
        console.log("graph 1:", hasCycle(g1) ? "cycle" : "no cycle");
        console.log("graph 2:", hasCycle(g2) ? "cycle" : "no cycle");
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield pitfall("The parent check breaks down with **parallel edges** (two edges between the same pair) — they form a cycle, yet the second one looks like the edge we arrived by. Track the parent *edge index* instead of the parent vertex if the input may contain multi-edges. Shortcut: a connected undirected graph with `E ≥ V` edges always has a cycle.")

    yield section("Detect a cycle in a directed graph", "repeat")
    yield diagram('''
        Graph 1 (cycle 1 → 2 → 3 → 1)      Graph 2 (no cycle — a DAG)

        0 ────▶ 1 ────▶ 2                  0 ────▶ 1
                ▲       │                  │       │
                │       ▼                  ▼       ▼
                └────── 3                  2 ────▶ 3
    ''', "Edges 0→1, 1→2, 2→3, 3→1 versus 0→1, 0→2, 1→3, 2→3")
    yield io("edges = 0→1, 1→2, 2→3, 3→1", "cycle", "edges = 0→1, 0→2, 1→3, 2→3", "no cycle")
    yield idea("In a digraph “visited” is not enough: graph 2 reaches `3` twice (via `1` and via `2`) without any cycle. A cycle exists only when DFS reaches a vertex that is **still on the recursion stack** — an ancestor of the current call. Keep a second array `onStack` that is set on entry and cleared on exit; a neighbour with `onStack[v]` true is a back edge.")
    yield multi('''
        graph 1: cycle
        graph 2: no cycle
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)                  # directed: one direction only
            return adj

        def has_cycle_from(adj, u, visited, on_stack):
            visited[u] = True
            on_stack[u] = True                    # u is an ancestor of everything below
            for v in adj[u]:
                if not visited[v]:
                    if has_cycle_from(adj, v, visited, on_stack):
                        return True
                elif on_stack[v]:                 # back edge to an ancestor -> cycle
                    return True
            on_stack[u] = False                   # done with u's subtree
            return False

        def has_cycle(adj):
            n = len(adj)
            visited, on_stack = [False] * n, [False] * n
            for u in range(n):
                if not visited[u] and has_cycle_from(adj, u, visited, on_stack):
                    return True
            return False

        g1 = build(4, [(0, 1), (1, 2), (2, 3), (3, 1)])
        g2 = build(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
        print("graph 1:", "cycle" if has_cycle(g1) else "no cycle")
        print("graph 2:", "cycle" if has_cycle(g2) else "no cycle")
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) adj[u].push_back(v);   // directed: one direction only
            return adj;
        }

        bool hasCycleFrom(const vector<vector<int>>& adj, int u, vector<bool>& visited, vector<bool>& onStack) {
            visited[u] = true;
            onStack[u] = true;                    // u is an ancestor of everything below
            for (int v : adj[u]) {
                if (!visited[v]) {
                    if (hasCycleFrom(adj, v, visited, onStack)) return true;
                } else if (onStack[v]) {          // back edge to an ancestor -> cycle
                    return true;
                }
            }
            onStack[u] = false;                   // done with u's subtree
            return false;
        }

        bool hasCycle(const vector<vector<int>>& adj) {
            int n = adj.size();
            vector<bool> visited(n, false), onStack(n, false);
            for (int u = 0; u < n; u++)
                if (!visited[u] && hasCycleFrom(adj, u, visited, onStack)) return true;
            return false;
        }

        int main() {
            auto g1 = build(4, {{0, 1}, {1, 2}, {2, 3}, {3, 1}});
            auto g2 = build(4, {{0, 1}, {0, 2}, {1, 3}, {2, 3}});
            cout << "graph 1: " << (hasCycle(g1) ? "cycle" : "no cycle") << "\n";
            cout << "graph 2: " << (hasCycle(g2) ? "cycle" : "no cycle") << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) adj.get(e[0]).add(e[1]);   // directed: one direction only
                return adj;
            }

            static boolean hasCycleFrom(List<List<Integer>> adj, int u, boolean[] visited, boolean[] onStack) {
                visited[u] = true;
                onStack[u] = true;                    // u is an ancestor of everything below
                for (int v : adj.get(u)) {
                    if (!visited[v]) {
                        if (hasCycleFrom(adj, v, visited, onStack)) return true;
                    } else if (onStack[v]) {          // back edge to an ancestor -> cycle
                        return true;
                    }
                }
                onStack[u] = false;                   // done with u's subtree
                return false;
            }

            static boolean hasCycle(List<List<Integer>> adj) {
                int n = adj.size();
                boolean[] visited = new boolean[n], onStack = new boolean[n];
                for (int u = 0; u < n; u++)
                    if (!visited[u] && hasCycleFrom(adj, u, visited, onStack)) return true;
                return false;
            }

            public static void main(String[] args) {
                List<List<Integer>> g1 = build(4, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 1}});
                List<List<Integer>> g2 = build(4, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}});
                System.out.println("graph 1: " + (hasCycle(g1) ? "cycle" : "no cycle"));
                System.out.println("graph 2: " + (hasCycle(g2) ? "cycle" : "no cycle"));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) adj[u].push(v);       // directed: one direction only
            return adj;
        }

        function hasCycleFrom(adj, u, visited, onStack) {
            visited[u] = true;
            onStack[u] = true;                        // u is an ancestor of everything below
            for (const v of adj[u]) {
                if (!visited[v]) {
                    if (hasCycleFrom(adj, v, visited, onStack)) return true;
                } else if (onStack[v]) {              // back edge to an ancestor -> cycle
                    return true;
                }
            }
            onStack[u] = false;                       // done with u's subtree
            return false;
        }

        function hasCycle(adj) {
            const n = adj.length;
            const visited = new Array(n).fill(false), onStack = new Array(n).fill(false);
            for (let u = 0; u < n; u++)
                if (!visited[u] && hasCycleFrom(adj, u, visited, onStack)) return true;
            return false;
        }

        const g1 = build(4, [[0, 1], [1, 2], [2, 3], [3, 1]]);
        const g2 = build(4, [[0, 1], [0, 2], [1, 3], [2, 3]]);
        console.log("graph 1:", hasCycle(g1) ? "cycle" : "no cycle");
        console.log("graph 2:", hasCycle(g2) ? "cycle" : "no cycle");
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield note("The same idea is often written with three **colours**: white = unvisited, grey = on the recursion stack, black = finished. An edge to a grey vertex is a back edge (cycle); an edge to a black vertex is a cross/forward edge and harmless. Kahn's algorithm below detects directed cycles without recursion.")

    yield section("Topological sort — Kahn's algorithm (BFS)", "arrows-sort")
    yield define("Topological order", "a linear ordering of the vertices of a **DAG** such that for every edge `u → v`, `u` comes before `v`. It is the order in which tasks with dependencies can be executed. A graph with a cycle has no topological order; a DAG may have several.")
    yield diagram('''
        5 ────▶ 2 ────▶ 3
        │               │
        ▼               ▼
        0 ◀──── 4 ────▶ 1
    ''', "The DAG used for both topological sorts: edges 5→2, 5→0, 4→0, 4→1, 2→3, 3→1")
    yield io("edges = 5→2, 5→0, 4→0, 4→1, 2→3, 3→1, V = 6", "4 5 2 0 3 1 (one valid order; 5 4 2 3 1 0 is another)")
    yield idea("A vertex with **indegree 0** has no unfinished prerequisites, so it can go first. Output it, then “delete” it by decrementing the indegree of each neighbour; any neighbour that drops to 0 is now free and joins the queue. Repeat until the queue is empty.")
    yield steps(
        ("Count indegrees", "`indeg[v]` = number of edges into `v`, one pass over the adjacency lists."),
        ("Seed the queue", "Enqueue every vertex with `indeg[v] == 0`."),
        ("Process", "Dequeue `u`, append it to the order; for every neighbour `v`: `indeg[v] -= 1`, and enqueue `v` when it reaches 0."),
        ("Finish", "When the queue is empty the order is complete — if it holds fewer than `V` vertices, the graph has a cycle (next section)."),
    )
    yield multi('''
        topological order: 4 5 2 0 3 1
    ''', py=r'''
        from collections import deque

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
            return adj

        def kahn(adj):
            n = len(adj)
            indeg = [0] * n
            for u in range(n):
                for v in adj[u]:
                    indeg[v] += 1                 # step 1: indegrees
            q = deque(u for u in range(n) if indeg[u] == 0)   # step 2: no prerequisites
            order = []
            while q:
                u = q.popleft()
                order.append(u)
                for v in adj[u]:
                    indeg[v] -= 1                 # "remove" edge u -> v
                    if indeg[v] == 0:
                        q.append(v)               # all prerequisites of v are done
            return order

        adj = build(6, [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)])
        print("topological order:", *kahn(adj))
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) adj[u].push_back(v);
            return adj;
        }

        vector<int> kahn(const vector<vector<int>>& adj) {
            int n = adj.size();
            vector<int> indeg(n, 0);
            for (int u = 0; u < n; u++)
                for (int v : adj[u]) indeg[v]++;              // step 1: indegrees
            queue<int> q;
            for (int u = 0; u < n; u++)
                if (indeg[u] == 0) q.push(u);                 // step 2: no prerequisites
            vector<int> order;
            while (!q.empty()) {
                int u = q.front(); q.pop();
                order.push_back(u);
                for (int v : adj[u])
                    if (--indeg[v] == 0) q.push(v);           // all prerequisites of v are done
            }
            return order;
        }

        int main() {
            auto adj = build(6, {{5, 2}, {5, 0}, {4, 0}, {4, 1}, {2, 3}, {3, 1}});
            cout << "topological order:";
            for (int u : kahn(adj)) cout << " " << u;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) adj.get(e[0]).add(e[1]);
                return adj;
            }

            static List<Integer> kahn(List<List<Integer>> adj) {
                int n = adj.size();
                int[] indeg = new int[n];
                for (int u = 0; u < n; u++)
                    for (int v : adj.get(u)) indeg[v]++;          // step 1: indegrees
                Deque<Integer> q = new ArrayDeque<>();
                for (int u = 0; u < n; u++)
                    if (indeg[u] == 0) q.add(u);                  // step 2: no prerequisites
                List<Integer> order = new ArrayList<>();
                while (!q.isEmpty()) {
                    int u = q.poll();
                    order.add(u);
                    for (int v : adj.get(u))
                        if (--indeg[v] == 0) q.add(v);            // all prerequisites of v are done
                }
                return order;
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(6, new int[][]{{5, 2}, {5, 0}, {4, 0}, {4, 1}, {2, 3}, {3, 1}});
                StringBuilder sb = new StringBuilder("topological order:");
                for (int u : kahn(adj)) sb.append(' ').append(u);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) adj[u].push(v);
            return adj;
        }

        function kahn(adj) {
            const n = adj.length;
            const indeg = new Array(n).fill(0);
            for (const nbrs of adj)
                for (const v of nbrs) indeg[v]++;                 // step 1: indegrees
            const q = [];
            for (let u = 0; u < n; u++)
                if (indeg[u] === 0) q.push(u);                    // step 2: no prerequisites
            const order = [];
            let head = 0;
            while (head < q.length) {
                const u = q[head++];
                order.push(u);
                for (const v of adj[u])
                    if (--indeg[v] === 0) q.push(v);              // all prerequisites of v are done
            }
            return order;
        }

        const adj = build(6, [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]]);
        console.log("topological order:", kahn(adj).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield note("Swap the queue for a min-priority queue and Kahn's algorithm yields the **lexicographically smallest** topological order — a common follow-up question.")

    yield section("Cycle detection with Kahn's algorithm", "alert-triangle")
    yield p("Kahn's algorithm only ever outputs vertices whose indegree reached 0. The vertices on a cycle depend on each other, so none of them ever reaches 0 and they are never output. Therefore: **fewer than `V` vertices in the result ⇔ the graph has a cycle.** This is the iterative alternative to the recursion-stack method.")
    yield io("edges = 5→2, 5→0, 4→0, 4→1, 2→3, 3→1, V = 6", "no cycle", "edges = 0→1, 1→2, 2→3, 3→1, V = 4", "cycle")
    yield multi('''
        graph 1: no cycle (6 of 6 vertices ordered)
        graph 2: cycle (1 of 4 vertices ordered)
    ''', py=r'''
        from collections import deque

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
            return adj

        def kahn_count(adj):
            n = len(adj)
            indeg = [0] * n
            for u in range(n):
                for v in adj[u]:
                    indeg[v] += 1
            q = deque(u for u in range(n) if indeg[u] == 0)
            count = 0                             # vertices that made it into the order
            while q:
                u = q.popleft()
                count += 1
                for v in adj[u]:
                    indeg[v] -= 1
                    if indeg[v] == 0:
                        q.append(v)
            return count                          # vertices on a cycle never reach indegree 0

        def report(name, adj):
            c = kahn_count(adj)
            verdict = "no cycle" if c == len(adj) else "cycle"
            print(f"{name}: {verdict} ({c} of {len(adj)} vertices ordered)")

        report("graph 1", build(6, [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]))
        report("graph 2", build(4, [(0, 1), (1, 2), (2, 3), (3, 1)]))
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <string>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) adj[u].push_back(v);
            return adj;
        }

        int kahnCount(const vector<vector<int>>& adj) {
            int n = adj.size();
            vector<int> indeg(n, 0);
            for (int u = 0; u < n; u++)
                for (int v : adj[u]) indeg[v]++;
            queue<int> q;
            for (int u = 0; u < n; u++)
                if (indeg[u] == 0) q.push(u);
            int count = 0;                                    // vertices that made it into the order
            while (!q.empty()) {
                int u = q.front(); q.pop();
                count++;
                for (int v : adj[u])
                    if (--indeg[v] == 0) q.push(v);
            }
            return count;                                     // vertices on a cycle never reach indegree 0
        }

        void report(const string& name, const vector<vector<int>>& adj) {
            int c = kahnCount(adj), n = adj.size();
            cout << name << ": " << (c == n ? "no cycle" : "cycle") << " (" << c << " of " << n << " vertices ordered)\n";
        }

        int main() {
            report("graph 1", build(6, {{5, 2}, {5, 0}, {4, 0}, {4, 1}, {2, 3}, {3, 1}}));
            report("graph 2", build(4, {{0, 1}, {1, 2}, {2, 3}, {3, 1}}));
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) adj.get(e[0]).add(e[1]);
                return adj;
            }

            static int kahnCount(List<List<Integer>> adj) {
                int n = adj.size();
                int[] indeg = new int[n];
                for (int u = 0; u < n; u++)
                    for (int v : adj.get(u)) indeg[v]++;
                Deque<Integer> q = new ArrayDeque<>();
                for (int u = 0; u < n; u++)
                    if (indeg[u] == 0) q.add(u);
                int count = 0;                                    // vertices that made it into the order
                while (!q.isEmpty()) {
                    int u = q.poll();
                    count++;
                    for (int v : adj.get(u))
                        if (--indeg[v] == 0) q.add(v);
                }
                return count;                                     // vertices on a cycle never reach indegree 0
            }

            static void report(String name, List<List<Integer>> adj) {
                int c = kahnCount(adj), n = adj.size();
                System.out.println(name + ": " + (c == n ? "no cycle" : "cycle") + " (" + c + " of " + n + " vertices ordered)");
            }

            public static void main(String[] args) {
                report("graph 1", build(6, new int[][]{{5, 2}, {5, 0}, {4, 0}, {4, 1}, {2, 3}, {3, 1}}));
                report("graph 2", build(4, new int[][]{{0, 1}, {1, 2}, {2, 3}, {3, 1}}));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) adj[u].push(v);
            return adj;
        }

        function kahnCount(adj) {
            const n = adj.length;
            const indeg = new Array(n).fill(0);
            for (const nbrs of adj)
                for (const v of nbrs) indeg[v]++;
            const q = [];
            for (let u = 0; u < n; u++)
                if (indeg[u] === 0) q.push(u);
            let count = 0, head = 0;                              // count = vertices that made it into the order
            while (head < q.length) {
                const u = q[head++];
                count++;
                for (const v of adj[u])
                    if (--indeg[v] === 0) q.push(v);
            }
            return count;                                         // vertices on a cycle never reach indegree 0
        }

        function report(name, adj) {
            const c = kahnCount(adj), n = adj.length;
            console.log(`${name}: ${c === n ? "no cycle" : "cycle"} (${c} of ${n} vertices ordered)`);
        }

        report("graph 1", build(6, [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]]));
        report("graph 2", build(4, [[0, 1], [1, 2], [2, 3], [3, 1]]));
    ''')
    yield complexity("O(V + E)", "O(V)")

    yield section("Topological sort using DFS", "arrows-sort")
    yield idea("When `dfs(u)` **finishes**, every vertex reachable from `u` has already finished (it was either visited inside the call or earlier). So a vertex finishes *after* all of its descendants — reversing the finish order puts every `u` before everything it points to. Push each vertex onto a stack as its DFS returns, then pop the stack.")
    yield steps(
        ("Visit every vertex", "For `u` in `0 … V−1`: if `u` is unvisited, call `dfs(u)` — this covers disconnected DAGs."),
        ("`dfs(u)`", "Mark `u` visited, recurse into every unvisited neighbour, and **then** push `u` onto the stack (post-order)."),
        ("Read the stack", "Pop until empty — the pop order is a topological order."),
    )
    yield multi('''
        topological order: 5 4 2 3 1 0
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
            return adj

        def dfs(adj, u, visited, stack):
            visited[u] = True
            for v in adj[u]:
                if not visited[v]:
                    dfs(adj, v, visited, stack)
            stack.append(u)                       # post-order: u is pushed after all its descendants

        def topo_sort(adj):
            n = len(adj)
            visited = [False] * n
            stack = []
            for u in range(n):
                if not visited[u]:
                    dfs(adj, u, visited, stack)
            return stack[::-1]                    # pop everything = reverse finish order

        adj = build(6, [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)])
        print("topological order:", *topo_sort(adj))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) adj[u].push_back(v);
            return adj;
        }

        void dfs(const vector<vector<int>>& adj, int u, vector<bool>& visited, vector<int>& stack) {
            visited[u] = true;
            for (int v : adj[u])
                if (!visited[v]) dfs(adj, v, visited, stack);
            stack.push_back(u);                   // post-order: u is pushed after all its descendants
        }

        vector<int> topoSort(const vector<vector<int>>& adj) {
            int n = adj.size();
            vector<bool> visited(n, false);
            vector<int> stack;
            for (int u = 0; u < n; u++)
                if (!visited[u]) dfs(adj, u, visited, stack);
            reverse(stack.begin(), stack.end());  // pop everything = reverse finish order
            return stack;
        }

        int main() {
            auto adj = build(6, {{5, 2}, {5, 0}, {4, 0}, {4, 1}, {2, 3}, {3, 1}});
            cout << "topological order:";
            for (int u : topoSort(adj)) cout << " " << u;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) adj.get(e[0]).add(e[1]);
                return adj;
            }

            static void dfs(List<List<Integer>> adj, int u, boolean[] visited, Deque<Integer> stack) {
                visited[u] = true;
                for (int v : adj.get(u))
                    if (!visited[v]) dfs(adj, v, visited, stack);
                stack.push(u);                        // post-order: u is pushed after all its descendants
            }

            static List<Integer> topoSort(List<List<Integer>> adj) {
                int n = adj.size();
                boolean[] visited = new boolean[n];
                Deque<Integer> stack = new ArrayDeque<>();
                for (int u = 0; u < n; u++)
                    if (!visited[u]) dfs(adj, u, visited, stack);
                List<Integer> order = new ArrayList<>();
                while (!stack.isEmpty()) order.add(stack.pop());   // pop everything = reverse finish order
                return order;
            }

            public static void main(String[] args) {
                List<List<Integer>> adj = build(6, new int[][]{{5, 2}, {5, 0}, {4, 0}, {4, 1}, {2, 3}, {3, 1}});
                StringBuilder sb = new StringBuilder("topological order:");
                for (int u : topoSort(adj)) sb.append(' ').append(u);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) adj[u].push(v);
            return adj;
        }

        function dfs(adj, u, visited, stack) {
            visited[u] = true;
            for (const v of adj[u])
                if (!visited[v]) dfs(adj, v, visited, stack);
            stack.push(u);                            // post-order: u is pushed after all its descendants
        }

        function topoSort(adj) {
            const n = adj.length;
            const visited = new Array(n).fill(false);
            const stack = [];
            for (let u = 0; u < n; u++)
                if (!visited[u]) dfs(adj, u, visited, stack);
            return stack.reverse();                   // pop everything = reverse finish order
        }

        const adj = build(6, [[5, 2], [5, 0], [4, 0], [4, 1], [2, 3], [3, 1]]);
        console.log("topological order:", topoSort(adj).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield pitfall("The DFS version silently produces a (wrong) order when the graph has a cycle — it never checks. Either run the directed-cycle check first (`onStack`) or use Kahn's algorithm, which detects the cycle for free.")

    yield section("Shortest path in a DAG", "route")
    yield p("In a DAG a vertex's distance is final as soon as every vertex that can reach it is settled — and a topological order lists exactly those vertices first. One relaxation pass in topological order therefore gives all shortest paths, even with **negative** weights, in linear time. No priority queue, no repeated passes.")
    yield diagram('''
             2        3        6
        0 ──────▶ 1 ──────▶ 2 ──────▶ 3
        │                   ▲         ▲
        │ 1               2 │         │ 1
        ▼                   │         │
        4 ──────────────────┘         │
        │                             │
        └────────────▶ 5 ─────────────┘
               4
    ''', "Weighted DAG: 0→1 (2), 0→4 (1), 1→2 (3), 4→2 (2), 4→5 (4), 2→3 (6), 5→3 (1)")
    yield io("edges above, s = 0", "0 2 3 6 1 5", "s = 1", "INF 0 3 9 INF INF")
    yield steps(
        ("Initialise", "`dist[v] = INF` for all `v`, `dist[s] = 0`."),
        ("Topological order", "DFS-based (or Kahn's) topological sort of the whole graph."),
        ("Relax in order", "For each `u` in topological order with `dist[u] != INF`: for each edge `u → v` with weight `w`, if `dist[u] + w < dist[v]` set `dist[v] = dist[u] + w`."),
    )
    yield multi('''
        from 0: 0 2 3 6 1 5
        from 1: INF 0 3 9 INF INF
    ''', py=r'''
        INF = 10 ** 9

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v, w in edges:
                adj[u].append((v, w))             # weighted, directed
            return adj

        def dfs(adj, u, visited, stack):
            visited[u] = True
            for v, _ in adj[u]:
                if not visited[v]:
                    dfs(adj, v, visited, stack)
            stack.append(u)

        def dag_shortest(adj, s):
            n = len(adj)
            visited, stack = [False] * n, []
            for u in range(n):
                if not visited[u]:
                    dfs(adj, u, visited, stack)
            dist = [INF] * n
            dist[s] = 0
            for u in reversed(stack):             # topological order
                if dist[u] == INF:
                    continue                      # unreachable: nothing to relax from here
                for v, w in adj[u]:
                    if dist[u] + w < dist[v]:
                        dist[v] = dist[u] + w     # relax u -> v
            return dist

        adj = build(6, [(0, 1, 2), (0, 4, 1), (1, 2, 3), (4, 2, 2), (4, 5, 4), (2, 3, 6), (5, 3, 1)])
        for s in (0, 1):
            print(f"from {s}:", *("INF" if d == INF else d for d in dag_shortest(adj, s)))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        const int INF = 1e9;
        struct Edge { int u, v, w; };

        vector<vector<pair<int,int>>> build(int n, const vector<Edge>& edges) {
            vector<vector<pair<int,int>>> adj(n);
            for (auto& e : edges) adj[e.u].push_back({e.v, e.w});   // weighted, directed
            return adj;
        }

        void dfs(const vector<vector<pair<int,int>>>& adj, int u, vector<bool>& visited, vector<int>& stack) {
            visited[u] = true;
            for (auto [v, w] : adj[u])
                if (!visited[v]) dfs(adj, v, visited, stack);
            stack.push_back(u);
        }

        vector<int> dagShortest(const vector<vector<pair<int,int>>>& adj, int s) {
            int n = adj.size();
            vector<bool> visited(n, false);
            vector<int> stack;
            for (int u = 0; u < n; u++)
                if (!visited[u]) dfs(adj, u, visited, stack);
            vector<int> dist(n, INF);
            dist[s] = 0;
            for (int i = n - 1; i >= 0; i--) {          // topological order = reverse finish order
                int u = stack[i];
                if (dist[u] == INF) continue;           // unreachable: nothing to relax from here
                for (auto [v, w] : adj[u])
                    if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;   // relax u -> v
            }
            return dist;
        }

        int main() {
            auto adj = build(6, {{0, 1, 2}, {0, 4, 1}, {1, 2, 3}, {4, 2, 2}, {4, 5, 4}, {2, 3, 6}, {5, 3, 1}});
            for (int s : {0, 1}) {
                cout << "from " << s << ":";
                for (int d : dagShortest(adj, s)) {
                    if (d == INF) cout << " INF"; else cout << " " << d;
                }
                cout << "\n";
            }
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static final int INF = 1_000_000_000;

            static List<List<int[]>> build(int n, int[][] edges) {
                List<List<int[]>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) adj.get(e[0]).add(new int[]{e[1], e[2]});   // weighted, directed
                return adj;
            }

            static void dfs(List<List<int[]>> adj, int u, boolean[] visited, Deque<Integer> stack) {
                visited[u] = true;
                for (int[] e : adj.get(u))
                    if (!visited[e[0]]) dfs(adj, e[0], visited, stack);
                stack.push(u);
            }

            static int[] dagShortest(List<List<int[]>> adj, int s) {
                int n = adj.size();
                boolean[] visited = new boolean[n];
                Deque<Integer> stack = new ArrayDeque<>();
                for (int u = 0; u < n; u++)
                    if (!visited[u]) dfs(adj, u, visited, stack);
                int[] dist = new int[n];
                Arrays.fill(dist, INF);
                dist[s] = 0;
                while (!stack.isEmpty()) {                  // popping gives topological order
                    int u = stack.pop();
                    if (dist[u] == INF) continue;           // unreachable: nothing to relax from here
                    for (int[] e : adj.get(u))
                        if (dist[u] + e[1] < dist[e[0]]) dist[e[0]] = dist[u] + e[1];   // relax u -> v
                }
                return dist;
            }

            public static void main(String[] args) {
                List<List<int[]>> adj = build(6, new int[][]{{0, 1, 2}, {0, 4, 1}, {1, 2, 3}, {4, 2, 2}, {4, 5, 4}, {2, 3, 6}, {5, 3, 1}});
                for (int s : new int[]{0, 1}) {
                    StringBuilder sb = new StringBuilder("from " + s + ":");
                    for (int d : dagShortest(adj, s)) sb.append(' ').append(d == INF ? "INF" : String.valueOf(d));
                    System.out.println(sb);
                }
            }
        }
    ''', js=r'''
        const INF = 1e9;

        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v, w] of edges) adj[u].push([v, w]);   // weighted, directed
            return adj;
        }

        function dfs(adj, u, visited, stack) {
            visited[u] = true;
            for (const [v] of adj[u])
                if (!visited[v]) dfs(adj, v, visited, stack);
            stack.push(u);
        }

        function dagShortest(adj, s) {
            const n = adj.length;
            const visited = new Array(n).fill(false), stack = [];
            for (let u = 0; u < n; u++)
                if (!visited[u]) dfs(adj, u, visited, stack);
            const dist = new Array(n).fill(INF);
            dist[s] = 0;
            for (const u of stack.reverse()) {            // topological order
                if (dist[u] === INF) continue;            // unreachable: nothing to relax from here
                for (const [v, w] of adj[u])
                    if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;   // relax u -> v
            }
            return dist;
        }

        const adj = build(6, [[0, 1, 2], [0, 4, 1], [1, 2, 3], [4, 2, 2], [4, 5, 4], [2, 3, 6], [5, 3, 1]]);
        for (const s of [0, 1])
            console.log(`from ${s}:`, dagShortest(adj, s).map(d => d === INF ? "INF" : d).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield note("Negate every weight (or use `max` instead of `min`) and the same pass gives the **longest** path in a DAG — the critical path in project scheduling. Longest path in a general graph is NP-hard; the DAG structure is what makes it easy.")

    yield section("Dijkstra's algorithm", "route")
    yield p("Single-source shortest paths in a weighted graph with **non-negative** edge weights. It is a greedy BFS: instead of a FIFO queue it always expands the unsettled vertex with the smallest tentative distance, so each vertex is settled exactly once, in increasing order of distance.")
    yield diagram('''
                 4
        0 ─────────── 1
        │           ╱ │
      1 │        2 ╱  │ 5
        │        ╱    │
        2 ─────────── 3
         ╲     8     ╱
       10 ╲         ╱ 2
           ╲       ╱
               4
    ''', "The weighted graph used for Dijkstra, Prim and Kruskal: 0-1 (4), 0-2 (1), 1-2 (2), 1-3 (5), 2-3 (8), 2-4 (10), 3-4 (2)")
    yield io("edges above (undirected), s = 0", "dist = 0 3 1 8 10, path 0→4 = 0 2 1 3 4")
    yield idea("Suppose `u` has the smallest tentative distance among the unsettled vertices. Any other route to `u` would have to leave the settled set through some unsettled vertex `x` with `dist[x] ≥ dist[u]`, and with non-negative weights it can only get longer from there — so `dist[u]` is already optimal. Settle `u`, relax its edges, repeat. A negative edge breaks the “can only get longer” step, which is why Dijkstra fails with negative weights.")
    yield steps(
        ("Initialise", "`dist[s] = 0`, every other `dist[v] = INF`; push `(0, s)` into a min-heap keyed by distance."),
        ("Extract-min", "Pop `(d, u)`. If `d > dist[u]` it is a stale entry — skip it (lazy deletion)."),
        ("Relax", "For every edge `u → v` with weight `w`: if `dist[u] + w < dist[v]`, set `dist[v] = dist[u] + w`, `parent[v] = u`, and push `(dist[v], v)`."),
        ("Stop", "When the heap is empty every reachable vertex is settled; `INF` marks the unreachable ones."),
    )
    yield multi('''
        dist: 0 3 1 8 10
        path 0 -> 4: 0 2 1 3 4
    ''', py=r'''
        import heapq

        INF = 10 ** 9

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v, w in edges:
                adj[u].append((v, w))
                adj[v].append((u, w))             # undirected, weighted
            return adj

        def dijkstra(adj, s):
            n = len(adj)
            dist, parent = [INF] * n, [-1] * n
            dist[s] = 0
            pq = [(0, s)]                         # (distance, vertex) min-heap
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue                      # stale entry: u was already settled with a smaller d
                for v, w in adj[u]:
                    if d + w < dist[v]:           # relax u -> v
                        dist[v] = d + w
                        parent[v] = u
                        heapq.heappush(pq, (dist[v], v))
            return dist, parent

        def path_to(parent, t):
            path = []
            while t != -1:
                path.append(t)
                t = parent[t]
            return path[::-1]

        adj = build(5, [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8), (2, 4, 10), (3, 4, 2)])
        dist, parent = dijkstra(adj, 0)
        print("dist:", *dist)
        print("path 0 -> 4:", *path_to(parent, 4))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <queue>
        #include <vector>
        using namespace std;

        const int INF = 1e9;
        struct Edge { int u, v, w; };

        vector<vector<pair<int,int>>> build(int n, const vector<Edge>& edges) {
            vector<vector<pair<int,int>>> adj(n);
            for (auto& e : edges) {
                adj[e.u].push_back({e.v, e.w});
                adj[e.v].push_back({e.u, e.w});   // undirected, weighted
            }
            return adj;
        }

        vector<int> dijkstra(const vector<vector<pair<int,int>>>& adj, int s, vector<int>& parent) {
            int n = adj.size();
            vector<int> dist(n, INF);
            parent.assign(n, -1);
            dist[s] = 0;
            priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;   // min-heap of (distance, vertex)
            pq.push({0, s});
            while (!pq.empty()) {
                auto [d, u] = pq.top(); pq.pop();
                if (d > dist[u]) continue;        // stale entry: u was already settled with a smaller d
                for (auto [v, w] : adj[u]) {
                    if (d + w < dist[v]) {        // relax u -> v
                        dist[v] = d + w;
                        parent[v] = u;
                        pq.push({dist[v], v});
                    }
                }
            }
            return dist;
        }

        int main() {
            auto adj = build(5, {{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}});
            vector<int> parent;
            vector<int> dist = dijkstra(adj, 0, parent);
            cout << "dist:";
            for (int d : dist) cout << " " << d;
            cout << "\npath 0 -> 4:";
            vector<int> path;
            for (int t = 4; t != -1; t = parent[t]) path.push_back(t);
            reverse(path.begin(), path.end());
            for (int v : path) cout << " " << v;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static final int INF = 1_000_000_000;

            static List<List<int[]>> build(int n, int[][] edges) {
                List<List<int[]>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) {
                    adj.get(e[0]).add(new int[]{e[1], e[2]});
                    adj.get(e[1]).add(new int[]{e[0], e[2]});   // undirected, weighted
                }
                return adj;
            }

            static int[] parent;

            static int[] dijkstra(List<List<int[]>> adj, int s) {
                int n = adj.size();
                int[] dist = new int[n];
                parent = new int[n];
                Arrays.fill(dist, INF);
                Arrays.fill(parent, -1);
                dist[s] = 0;
                // min-heap of {distance, vertex}
                PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] != b[0] ? Integer.compare(a[0], b[0]) : Integer.compare(a[1], b[1]));
                pq.add(new int[]{0, s});
                while (!pq.isEmpty()) {
                    int[] top = pq.poll();
                    int d = top[0], u = top[1];
                    if (d > dist[u]) continue;        // stale entry: u was already settled with a smaller d
                    for (int[] e : adj.get(u)) {
                        int v = e[0], w = e[1];
                        if (d + w < dist[v]) {        // relax u -> v
                            dist[v] = d + w;
                            parent[v] = u;
                            pq.add(new int[]{dist[v], v});
                        }
                    }
                }
                return dist;
            }

            public static void main(String[] args) {
                List<List<int[]>> adj = build(5, new int[][]{{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}});
                int[] dist = dijkstra(adj, 0);
                StringBuilder sb = new StringBuilder("dist:");
                for (int d : dist) sb.append(' ').append(d);
                System.out.println(sb);
                List<Integer> path = new ArrayList<>();
                for (int t = 4; t != -1; t = parent[t]) path.add(t);
                Collections.reverse(path);
                sb = new StringBuilder("path 0 -> 4:");
                for (int v : path) sb.append(' ').append(v);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        const INF = 1e9;

        // Minimal binary min-heap of [key, value] pairs (JavaScript has no built-in priority queue).
        class MinHeap {
            constructor() { this.a = []; }
            get size() { return this.a.length; }
            less(i, j) { const x = this.a[i], y = this.a[j]; return x[0] !== y[0] ? x[0] < y[0] : x[1] < y[1]; }
            swap(i, j) { [this.a[i], this.a[j]] = [this.a[j], this.a[i]]; }
            push(item) {
                this.a.push(item);
                for (let i = this.a.length - 1; i > 0; i = (i - 1) >> 1)
                    if (this.less(i, (i - 1) >> 1)) this.swap(i, (i - 1) >> 1); else break;
            }
            pop() {
                const top = this.a[0], last = this.a.pop();
                if (this.a.length) {
                    this.a[0] = last;
                    for (let i = 0; ;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < this.a.length && this.less(l, m)) m = l;
                        if (r < this.a.length && this.less(r, m)) m = r;
                        if (m === i) break;
                        this.swap(i, m); i = m;
                    }
                }
                return top;
            }
        }

        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v, w] of edges) { adj[u].push([v, w]); adj[v].push([u, w]); }   // undirected, weighted
            return adj;
        }

        function dijkstra(adj, s) {
            const n = adj.length;
            const dist = new Array(n).fill(INF), parent = new Array(n).fill(-1);
            dist[s] = 0;
            const pq = new MinHeap();                 // [distance, vertex]
            pq.push([0, s]);
            while (pq.size) {
                const [d, u] = pq.pop();
                if (d > dist[u]) continue;            // stale entry: u was already settled with a smaller d
                for (const [v, w] of adj[u]) {
                    if (d + w < dist[v]) {            // relax u -> v
                        dist[v] = d + w;
                        parent[v] = u;
                        pq.push([dist[v], v]);
                    }
                }
            }
            return { dist, parent };
        }

        const adj = build(5, [[0, 1, 4], [0, 2, 1], [1, 2, 2], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2]]);
        const { dist, parent } = dijkstra(adj, 0);
        console.log("dist:", dist.join(" "));
        const path = [];
        for (let t = 4; t !== -1; t = parent[t]) path.push(t);
        console.log("path 0 -> 4:", path.reverse().join(" "));
    ''')
    yield complexity("O((V + E) log V) with a binary heap", "O(V + E)")
    yield p("The textbook version without a heap scans the whole `dist` array to find the minimum each round. It is `O(V²)` — fine for dense graphs or an adjacency matrix, and worth knowing because it is what the heap version optimises:")
    yield snippet("py", r'''
        INF = 10 ** 9

        def dijkstra_matrix(graph, src):          # graph[u][v] = weight, 0 = no edge
            n = len(graph)
            dist = [INF] * n
            dist[src] = 0
            settled = [False] * n
            for _ in range(n):
                u = -1                            # O(V) scan for the closest unsettled vertex
                for i in range(n):
                    if not settled[i] and (u == -1 or dist[i] < dist[u]):
                        u = i
                if dist[u] == INF:
                    break                         # the rest is unreachable
                settled[u] = True
                for v in range(n):
                    if graph[u][v] and not settled[v]:
                        dist[v] = min(dist[v], dist[u] + graph[u][v])
            return dist

        graph = [[0, 4, 1, 0, 0],
                 [4, 0, 2, 5, 0],
                 [1, 2, 0, 8, 10],
                 [0, 5, 8, 0, 2],
                 [0, 0, 10, 2, 0]]
        print(*dijkstra_matrix(graph, 0))
    ''', out="0 3 1 8 10", caption="Python — O(V²) array version")
    yield pitfall("**Negative edge weights break Dijkstra.** The algorithm assumes a settled vertex can never be improved; a negative edge discovered later can improve it. With a `settled` array the result is simply wrong; with the lazy-deletion heap version it may still be right but can re-settle vertices exponentially many times, and a negative cycle makes it loop forever. Use Bellman–Ford instead.")
    yield note("**Does adding a constant to every edge keep the shortest path?** No. Path `0→1→2` with weights 1 + 1 = 2 beats the direct edge `0→2` of weight 3; add 2 to every edge and it becomes 6 against 5. Paths with more edges are penalised more, so the shortest path can change — which is why Johnson's algorithm reweights with vertex potentials rather than a constant.")

    yield section("Bellman–Ford algorithm", "route")
    yield p("Single-source shortest paths that **allow negative edge weights** and **detect negative cycles**. Instead of picking vertices cleverly it relaxes *every* edge, `V − 1` times. After pass `i`, every shortest path that uses at most `i` edges is final; a shortest path has at most `V − 1` edges, so `V − 1` passes suffice.")
    yield diagram('''
                -1             2
        0 ──────────▶ 1 ──────────▶ 4
        │           ▲ │ ╲           │
      4 │         1 │ │  ╲ 2        │ -3
        ▼           │ ▼   ▼         │
        2 ◀─────────┴─────3 ◀───────┘
                5   3
    ''', "Directed graph with negative edges: 0→1 (−1), 0→2 (4), 1→2 (3), 1→3 (2), 1→4 (2), 3→2 (5), 3→1 (1), 4→3 (−3)")
    yield io("edges above, s = 0, V = 5", "0 -1 2 -2 1", "same edges plus 3→4 (−1)", "negative-weight cycle")
    yield idea("Shortest paths of one edge are found in pass 1, two edges in pass 2, and so on — each pass extends the frontier of correct distances by one edge. If a `V`-th pass can still improve something, a path with `V` edges is shorter than every path with fewer edges, which is only possible by going round a negative cycle.")
    yield steps(
        ("Initialise", "`dist[s] = 0`, every other `dist[v] = INF`."),
        ("Relax `V − 1` times", "For every edge `(u, v, w)`: if `dist[u] != INF` and `dist[u] + w < dist[v]`, set `dist[v] = dist[u] + w`."),
        ("Check for a negative cycle", "One more pass over all edges — if any edge can still be relaxed, a negative-weight cycle is reachable from `s`."),
    )
    yield multi('''
        graph 1: 0 -1 2 -2 1
        graph 2: negative-weight cycle
    ''', py=r'''
        INF = 10 ** 9

        def bellman_ford(n, edges, s):            # edges: list of (u, v, w); no adjacency list needed
            dist = [INF] * n
            dist[s] = 0
            for _ in range(n - 1):                # V - 1 passes
                for u, v, w in edges:
                    if dist[u] != INF and dist[u] + w < dist[v]:
                        dist[v] = dist[u] + w     # relax u -> v
            for u, v, w in edges:                 # pass V: anything still improving = negative cycle
                if dist[u] != INF and dist[u] + w < dist[v]:
                    return None
            return dist

        edges = [(0, 1, -1), (0, 2, 4), (1, 2, 3), (1, 3, 2), (1, 4, 2), (3, 2, 5), (3, 1, 1), (4, 3, -3)]
        d = bellman_ford(5, edges, 0)
        print("graph 1:", *d)
        d = bellman_ford(5, edges + [(3, 4, -1)], 0)         # 3 -> 4 -> 3 has weight -4
        print("graph 2:", "negative-weight cycle" if d is None else " ".join(map(str, d)))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        const int INF = 1e9;
        struct Edge { int u, v, w; };

        // returns false when a negative-weight cycle is reachable from s
        bool bellmanFord(int n, const vector<Edge>& edges, int s, vector<int>& dist) {
            dist.assign(n, INF);
            dist[s] = 0;
            for (int i = 0; i < n - 1; i++)       // V - 1 passes
                for (auto& e : edges)
                    if (dist[e.u] != INF && dist[e.u] + e.w < dist[e.v])
                        dist[e.v] = dist[e.u] + e.w;          // relax u -> v
            for (auto& e : edges)                 // pass V: anything still improving = negative cycle
                if (dist[e.u] != INF && dist[e.u] + e.w < dist[e.v]) return false;
            return true;
        }

        void report(const char* name, int n, const vector<Edge>& edges) {
            vector<int> dist;
            cout << name << ":";
            if (!bellmanFord(n, edges, 0, dist)) { cout << " negative-weight cycle\n"; return; }
            for (int d : dist) cout << " " << d;
            cout << "\n";
        }

        int main() {
            vector<Edge> edges = {{0, 1, -1}, {0, 2, 4}, {1, 2, 3}, {1, 3, 2}, {1, 4, 2}, {3, 2, 5}, {3, 1, 1}, {4, 3, -3}};
            report("graph 1", 5, edges);
            edges.push_back({3, 4, -1});          // 3 -> 4 -> 3 has weight -4
            report("graph 2", 5, edges);
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static final int INF = 1_000_000_000;

            // returns null when a negative-weight cycle is reachable from s
            static int[] bellmanFord(int n, List<int[]> edges, int s) {
                int[] dist = new int[n];
                Arrays.fill(dist, INF);
                dist[s] = 0;
                for (int i = 0; i < n - 1; i++)       // V - 1 passes
                    for (int[] e : edges)
                        if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]])
                            dist[e[1]] = dist[e[0]] + e[2];       // relax u -> v
                for (int[] e : edges)                 // pass V: anything still improving = negative cycle
                    if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) return null;
                return dist;
            }

            static void report(String name, int n, List<int[]> edges) {
                int[] dist = bellmanFord(n, edges, 0);
                StringBuilder sb = new StringBuilder(name + ":");
                if (dist == null) sb.append(" negative-weight cycle");
                else for (int d : dist) sb.append(' ').append(d);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                List<int[]> edges = new ArrayList<>(List.of(new int[]{0, 1, -1}, new int[]{0, 2, 4}, new int[]{1, 2, 3},
                        new int[]{1, 3, 2}, new int[]{1, 4, 2}, new int[]{3, 2, 5}, new int[]{3, 1, 1}, new int[]{4, 3, -3}));
                report("graph 1", 5, edges);
                edges.add(new int[]{3, 4, -1});       // 3 -> 4 -> 3 has weight -4
                report("graph 2", 5, edges);
            }
        }
    ''', js=r'''
        const INF = 1e9;

        function bellmanFord(n, edges, s) {           // edges: [u, v, w]; returns null on a negative cycle
            const dist = new Array(n).fill(INF);
            dist[s] = 0;
            for (let i = 0; i < n - 1; i++)           // V - 1 passes
                for (const [u, v, w] of edges)
                    if (dist[u] !== INF && dist[u] + w < dist[v]) dist[v] = dist[u] + w;   // relax u -> v
            for (const [u, v, w] of edges)            // pass V: anything still improving = negative cycle
                if (dist[u] !== INF && dist[u] + w < dist[v]) return null;
            return dist;
        }

        function report(name, n, edges) {
            const dist = bellmanFord(n, edges, 0);
            console.log(`${name}:`, dist === null ? "negative-weight cycle" : dist.join(" "));
        }

        const edges = [[0, 1, -1], [0, 2, 4], [1, 2, 3], [1, 3, 2], [1, 4, 2], [3, 2, 5], [3, 1, 1], [4, 3, -3]];
        report("graph 1", 5, edges);
        report("graph 2", 5, [...edges, [3, 4, -1]]);   // 3 -> 4 -> 3 has weight -4
    ''')
    yield complexity("O(V · E)", "O(V)")
    yield table(
        ["", "BFS", "DAG pass", "Dijkstra", "Bellman–Ford"],
        ["Weights", "none / all equal", "any (DAG only)", "non-negative", "any"],
        ["Negative cycles", "—", "impossible in a DAG", "wrong result", "detected"],
        ["Time", "`O(V + E)`", "`O(V + E)`", "`O((V + E) log V)`", "`O(V · E)`"],
        ["Typical use", "hops, grids", "scheduling, DP on DAGs", "maps, routing", "currency arbitrage, distance-vector routing (RIP)"],
    )
    yield note("Stop early when a whole pass changes nothing — on most graphs that happens long before `V − 1` passes. **SPFA** (queue-based Bellman–Ford) only re-relaxes edges out of vertices whose distance changed; same worst case, much faster on average.")

    yield section("Strongly connected components — Kosaraju's algorithm", "topology-star")
    yield define("Strongly connected component (SCC)", "a maximal set of vertices in a directed graph in which every vertex can reach every other. Collapsing each SCC to a single vertex turns any digraph into a DAG (the *condensation*).")
    yield diagram('''
        0 ───▶ 1 ───▶ 3 ───▶ 4 ───▶ 6
        ▲      │      ▲      │
        │      ▼      │      ▼
        └───── 2      └───── 5

        SCCs: {0, 1, 2}   {3, 4, 5}   {6}
    ''', "The digraph used for both SCC algorithms: 0→1, 1→2, 2→0, 1→3, 3→4, 4→5, 5→3, 4→6")
    yield io("edges above, V = 7", "{0,1,2} {3,4,5} {6} — 3 components")
    yield idea("Reverse every edge and the SCCs stay the same, but the edges *between* them flip. A DFS on the original graph finishes the “source” SCC last; starting the second DFS there, on the **reversed** graph, cannot leak into other SCCs (their edges now point *towards* it), so each DFS of the second pass collects exactly one SCC.")
    yield steps(
        ("DFS and record finish order", "Run DFS over the whole graph, pushing each vertex onto a stack as it finishes (the same post-order used for topological sort)."),
        ("Reverse the graph", "Build `rev` with every edge `u → v` turned into `v → u`."),
        ("DFS the reversed graph in stack order", "Pop vertices from the stack; for each unvisited one, DFS in `rev` — every vertex reached is in its SCC."),
    )
    yield multi('''
        SCC: 0 1 2
        SCC: 3 4 5
        SCC: 6
        count: 3
    ''', py=r'''
        def build(n, edges, reverse=False):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                if reverse:
                    adj[v].append(u)
                else:
                    adj[u].append(v)
            return adj

        def dfs(adj, u, visited, out):
            visited[u] = True
            for v in adj[u]:
                if not visited[v]:
                    dfs(adj, v, visited, out)
            out.append(u)                             # post-order

        def kosaraju(n, edges):
            adj = build(n, edges)
            visited, finish = [False] * n, []
            for u in range(n):                        # step 1: finish order on the original graph
                if not visited[u]:
                    dfs(adj, u, visited, finish)
            rev = build(n, edges, reverse=True)       # step 2: reversed graph
            visited = [False] * n
            sccs = []
            for u in reversed(finish):                # step 3: latest finisher first
                if not visited[u]:
                    comp = []
                    dfs(rev, u, visited, comp)        # reaches exactly one SCC
                    sccs.append(sorted(comp))
            return sccs

        edges = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (4, 6)]
        sccs = kosaraju(7, edges)
        for comp in sccs:
            print("SCC:", *comp)
        print("count:", len(sccs))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges, bool reverse) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) {
                if (reverse) adj[v].push_back(u); else adj[u].push_back(v);
            }
            return adj;
        }

        void dfs(const vector<vector<int>>& adj, int u, vector<bool>& visited, vector<int>& out) {
            visited[u] = true;
            for (int v : adj[u])
                if (!visited[v]) dfs(adj, v, visited, out);
            out.push_back(u);                             // post-order
        }

        vector<vector<int>> kosaraju(int n, const vector<pair<int,int>>& edges) {
            auto adj = build(n, edges, false);
            vector<bool> visited(n, false);
            vector<int> finish;
            for (int u = 0; u < n; u++)                   // step 1: finish order on the original graph
                if (!visited[u]) dfs(adj, u, visited, finish);
            auto rev = build(n, edges, true);             // step 2: reversed graph
            visited.assign(n, false);
            vector<vector<int>> sccs;
            for (int i = n - 1; i >= 0; i--) {            // step 3: latest finisher first
                int u = finish[i];
                if (visited[u]) continue;
                vector<int> comp;
                dfs(rev, u, visited, comp);               // reaches exactly one SCC
                sort(comp.begin(), comp.end());
                sccs.push_back(comp);
            }
            return sccs;
        }

        int main() {
            vector<pair<int,int>> edges = {{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {4, 6}};
            auto sccs = kosaraju(7, edges);
            for (auto& comp : sccs) {
                cout << "SCC:";
                for (int v : comp) cout << " " << v;
                cout << "\n";
            }
            cout << "count: " << sccs.size() << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges, boolean reverse) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) {
                    if (reverse) adj.get(e[1]).add(e[0]); else adj.get(e[0]).add(e[1]);
                }
                return adj;
            }

            static void dfs(List<List<Integer>> adj, int u, boolean[] visited, List<Integer> out) {
                visited[u] = true;
                for (int v : adj.get(u))
                    if (!visited[v]) dfs(adj, v, visited, out);
                out.add(u);                                   // post-order
            }

            static List<List<Integer>> kosaraju(int n, int[][] edges) {
                List<List<Integer>> adj = build(n, edges, false);
                boolean[] visited = new boolean[n];
                List<Integer> finish = new ArrayList<>();
                for (int u = 0; u < n; u++)                   // step 1: finish order on the original graph
                    if (!visited[u]) dfs(adj, u, visited, finish);
                List<List<Integer>> rev = build(n, edges, true);   // step 2: reversed graph
                visited = new boolean[n];
                List<List<Integer>> sccs = new ArrayList<>();
                for (int i = n - 1; i >= 0; i--) {            // step 3: latest finisher first
                    int u = finish.get(i);
                    if (visited[u]) continue;
                    List<Integer> comp = new ArrayList<>();
                    dfs(rev, u, visited, comp);               // reaches exactly one SCC
                    Collections.sort(comp);
                    sccs.add(comp);
                }
                return sccs;
            }

            public static void main(String[] args) {
                int[][] edges = {{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {4, 6}};
                List<List<Integer>> sccs = kosaraju(7, edges);
                for (List<Integer> comp : sccs) {
                    StringBuilder sb = new StringBuilder("SCC:");
                    for (int v : comp) sb.append(' ').append(v);
                    System.out.println(sb);
                }
                System.out.println("count: " + sccs.size());
            }
        }
    ''', js=r'''
        function build(n, edges, reverse = false) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) {
                if (reverse) adj[v].push(u); else adj[u].push(v);
            }
            return adj;
        }

        function dfs(adj, u, visited, out) {
            visited[u] = true;
            for (const v of adj[u])
                if (!visited[v]) dfs(adj, v, visited, out);
            out.push(u);                                      // post-order
        }

        function kosaraju(n, edges) {
            const adj = build(n, edges);
            let visited = new Array(n).fill(false);
            const finish = [];
            for (let u = 0; u < n; u++)                       // step 1: finish order on the original graph
                if (!visited[u]) dfs(adj, u, visited, finish);
            const rev = build(n, edges, true);                // step 2: reversed graph
            visited = new Array(n).fill(false);
            const sccs = [];
            for (let i = n - 1; i >= 0; i--) {                // step 3: latest finisher first
                const u = finish[i];
                if (visited[u]) continue;
                const comp = [];
                dfs(rev, u, visited, comp);                   // reaches exactly one SCC
                sccs.push(comp.sort((a, b) => a - b));
            }
            return sccs;
        }

        const edges = [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3], [4, 6]];
        const sccs = kosaraju(7, edges);
        for (const comp of sccs) console.log("SCC:", comp.join(" "));
        console.log("count:", sccs.length);
    ''')
    yield complexity("O(V + E)", "O(V + E) for the reversed graph")
    yield note("Kosaraju emits SCCs in **topological order of the condensation** (sources first: `{0,1,2}` before `{3,4,5}` before `{6}`); Tarjan's algorithm below emits them in reverse. A digraph is strongly connected exactly when the count is 1.")

    yield section("Strongly connected components — Tarjan's algorithm", "topology-star")
    yield p("One DFS pass instead of two. Every vertex gets a **discovery time** `disc[u]` and a **low-link** `low[u]`: the smallest discovery time reachable from `u`'s subtree using at most one back edge to a vertex that is still on the stack. A vertex with `low[u] == disc[u]` is the *root* of an SCC — everything above it on the stack belongs to that component.")
    yield idea("Keep every vertex on an explicit stack from the moment it is discovered until its SCC is complete. A back edge to a stacked vertex `v` lowers `low[u]` to `disc[v]`; after visiting a child `v`, `low[u] = min(low[u], low[v])`. If, when `u` finishes, nothing in its subtree reached anything discovered earlier (`low[u] == disc[u]`), then `u` and all vertices stacked after it form one SCC — pop them off.")
    yield multi('''
        SCC: 6
        SCC: 3 4 5
        SCC: 0 1 2
        count: 3
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
            return adj

        def tarjan(adj):
            n = len(adj)
            disc, low = [-1] * n, [0] * n
            on_stack, stack, sccs = [False] * n, [], []
            timer = [0]

            def dfs(u):
                disc[u] = low[u] = timer[0]
                timer[0] += 1
                stack.append(u)
                on_stack[u] = True
                for v in adj[u]:
                    if disc[v] == -1:                 # tree edge
                        dfs(v)
                        low[u] = min(low[u], low[v])
                    elif on_stack[v]:                 # back edge into the current SCC
                        low[u] = min(low[u], disc[v])
                if low[u] == disc[u]:                 # u is the root of an SCC
                    comp = []
                    while True:
                        v = stack.pop()
                        on_stack[v] = False
                        comp.append(v)
                        if v == u:
                            break
                    sccs.append(sorted(comp))

            for u in range(n):
                if disc[u] == -1:
                    dfs(u)
            return sccs

        adj = build(7, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (4, 6)])
        sccs = tarjan(adj)
        for comp in sccs:
            print("SCC:", *comp)
        print("count:", len(sccs))
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Tarjan {
            const vector<vector<int>>& adj;
            vector<int> disc, low, stack;
            vector<bool> onStack;
            vector<vector<int>> sccs;
            int timer = 0;

            Tarjan(const vector<vector<int>>& g) : adj(g), disc(g.size(), -1), low(g.size(), 0), onStack(g.size(), false) {}

            void dfs(int u) {
                disc[u] = low[u] = timer++;
                stack.push_back(u);
                onStack[u] = true;
                for (int v : adj[u]) {
                    if (disc[v] == -1) {                  // tree edge
                        dfs(v);
                        low[u] = min(low[u], low[v]);
                    } else if (onStack[v]) {              // back edge into the current SCC
                        low[u] = min(low[u], disc[v]);
                    }
                }
                if (low[u] == disc[u]) {                  // u is the root of an SCC
                    vector<int> comp;
                    while (true) {
                        int v = stack.back(); stack.pop_back();
                        onStack[v] = false;
                        comp.push_back(v);
                        if (v == u) break;
                    }
                    sort(comp.begin(), comp.end());
                    sccs.push_back(comp);
                }
            }

            vector<vector<int>> run() {
                for (int u = 0; u < (int)adj.size(); u++)
                    if (disc[u] == -1) dfs(u);
                return sccs;
            }
        };

        int main() {
            vector<vector<int>> adj(7);
            for (auto [u, v] : vector<pair<int,int>>{{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {4, 6}})
                adj[u].push_back(v);
            auto sccs = Tarjan(adj).run();
            for (auto& comp : sccs) {
                cout << "SCC:";
                for (int v : comp) cout << " " << v;
                cout << "\n";
            }
            cout << "count: " << sccs.size() << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> adj;
            static int[] disc, low;
            static boolean[] onStack;
            static Deque<Integer> stack = new ArrayDeque<>();
            static List<List<Integer>> sccs = new ArrayList<>();
            static int timer = 0;

            static void dfs(int u) {
                disc[u] = low[u] = timer++;
                stack.push(u);
                onStack[u] = true;
                for (int v : adj.get(u)) {
                    if (disc[v] == -1) {                      // tree edge
                        dfs(v);
                        low[u] = Math.min(low[u], low[v]);
                    } else if (onStack[v]) {                  // back edge into the current SCC
                        low[u] = Math.min(low[u], disc[v]);
                    }
                }
                if (low[u] == disc[u]) {                      // u is the root of an SCC
                    List<Integer> comp = new ArrayList<>();
                    while (true) {
                        int v = stack.pop();
                        onStack[v] = false;
                        comp.add(v);
                        if (v == u) break;
                    }
                    Collections.sort(comp);
                    sccs.add(comp);
                }
            }

            public static void main(String[] args) {
                int n = 7;
                int[][] edges = {{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {4, 6}};
                adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) adj.get(e[0]).add(e[1]);
                disc = new int[n]; low = new int[n]; onStack = new boolean[n];
                Arrays.fill(disc, -1);
                for (int u = 0; u < n; u++)
                    if (disc[u] == -1) dfs(u);
                for (List<Integer> comp : sccs) {
                    StringBuilder sb = new StringBuilder("SCC:");
                    for (int v : comp) sb.append(' ').append(v);
                    System.out.println(sb);
                }
                System.out.println("count: " + sccs.size());
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) adj[u].push(v);
            return adj;
        }

        function tarjan(adj) {
            const n = adj.length;
            const disc = new Array(n).fill(-1), low = new Array(n).fill(0);
            const onStack = new Array(n).fill(false), stack = [], sccs = [];
            let timer = 0;

            function dfs(u) {
                disc[u] = low[u] = timer++;
                stack.push(u);
                onStack[u] = true;
                for (const v of adj[u]) {
                    if (disc[v] === -1) {                     // tree edge
                        dfs(v);
                        low[u] = Math.min(low[u], low[v]);
                    } else if (onStack[v]) {                  // back edge into the current SCC
                        low[u] = Math.min(low[u], disc[v]);
                    }
                }
                if (low[u] === disc[u]) {                     // u is the root of an SCC
                    const comp = [];
                    for (;;) {
                        const v = stack.pop();
                        onStack[v] = false;
                        comp.push(v);
                        if (v === u) break;
                    }
                    sccs.push(comp.sort((a, b) => a - b));
                }
            }

            for (let u = 0; u < n; u++)
                if (disc[u] === -1) dfs(u);
            return sccs;
        }

        const adj = build(7, [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 3], [4, 6]]);
        const sccs = tarjan(adj);
        for (const comp of sccs) console.log("SCC:", comp.join(" "));
        console.log("count:", sccs.length);
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield pitfall("For the back-edge case use `disc[v]`, not `low[v]`, and only when `v` is **still on the stack** — a visited vertex that has already been popped belongs to a finished SCC and must not lower `low[u]`. Using `low[v]` still yields correct SCCs here, but the identical-looking articulation-point algorithm below genuinely breaks with that mistake.")

    yield section("Articulation points (cut vertices)", "alert-triangle")
    yield define("Articulation point", "a vertex of a connected undirected graph whose removal (with its edges) disconnects the graph — the single point of failure in a network. A graph with no articulation point is **biconnected**.")
    yield diagram('''
        0 ───── 1 ───── 3 ───── 4
        │     ╱
        │   ╱
        2 ╱

        remove 1 → {0, 2} and {3, 4}    remove 3 → {0, 1, 2} and {4}
        remove 0, 2 or 4 → still connected
    ''', "The graph used for articulation points and bridges: edges 0-1, 0-2, 1-2, 1-3, 3-4; vertices 1 and 3 are articulation points")
    yield io("edges = 0-1, 0-2, 1-2, 1-3, 3-4, V = 5", "1 3")
    yield p("**Naive solution.** Remove every vertex in turn and count the connected components of what is left (skipping the removed vertex). If the count goes above 1, the vertex is an articulation point. One DFS per vertex: `O(V · (V + E))`.")
    yield snippet("py", r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def dfs(adj, u, visited):
            visited[u] = True
            for v in adj[u]:
                if not visited[v]:
                    dfs(adj, v, visited)

        def components_without(adj, removed):
            visited = [False] * len(adj)
            visited[removed] = True                   # pretend the vertex is gone
            count = 0
            for u in range(len(adj)):
                if not visited[u]:
                    count += 1
                    dfs(adj, u, visited)
            return count

        def articulation_points_naive(adj):
            return [u for u in range(len(adj)) if components_without(adj, u) > 1]

        adj = build(5, [(0, 1), (0, 2), (1, 2), (1, 3), (3, 4)])
        print("articulation points (naive):", *articulation_points_naive(adj))
    ''', out="articulation points (naive): 1 3", caption="Python — naive O(V · (V + E))")
    yield p("**First idea (DFS tree, root only).** Run a DFS and look at its tree. If the **root** has two or more DFS children, the root is an articulation point: the subtrees are separate branches that no back edge can connect (an undirected DFS tree has no cross edges, so an edge between two subtrees would have been a tree edge). The rule is only valid for the root — any other vertex can have several children that are still joined through back edges to its ancestors.")
    yield snippet("py", r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def dfs(adj, u, visited):
            visited[u] = True
            for v in adj[u]:
                if not visited[v]:
                    dfs(adj, v, visited)

        def root_children(adj, root):
            visited = [False] * len(adj)
            visited[root] = True
            children = 0
            for v in adj[root]:
                if not visited[v]:                    # each unvisited neighbour starts a new subtree
                    children += 1
                    dfs(adj, v, visited)
            return children

        adj = build(5, [(0, 1), (0, 2), (1, 2), (1, 3), (3, 4)])
        for root in (0, 3):
            c = root_children(adj, root)
            print(f"root {root}: {c} DFS child(ren) ->", "articulation point" if c >= 2 else "not an articulation point")
    ''', out='''
        root 0: 1 DFS child(ren) -> not an articulation point
        root 3: 2 DFS child(ren) -> articulation point
    ''', caption="Python — the root rule")
    yield p("**Tarjan's algorithm (low-link values).** Give every vertex a **discovery time** `disc[u]` (the DFS counter when `u` is first visited) and a **low value** `low[u]`: the smallest discovery time reachable from `u`'s subtree using tree edges plus at most one back edge. A non-root `u` is an articulation point iff some DFS child `v` has `low[v] ≥ disc[u]` — nothing in `v`'s subtree climbs above `u`, so removing `u` strands that subtree.")
    yield idea("`low[u]` starts as `disc[u]`. A back edge `u – v` to an already visited vertex (that is not the parent) lowers it to `disc[v]`; after returning from a child `v`, `low[u] = min(low[u], low[v])`. The check `low[v] >= disc[u]` is made right after `dfs(v)` returns, when `low[v]` is final.")
    yield steps(
        ("Discover", "On entering `u`: `disc[u] = low[u] = timer++`, `children = 0`."),
        ("Tree edge", "For an unvisited neighbour `v`: `children++`, `dfs(v)`, then `low[u] = min(low[u], low[v])`. If `u` is not the root and `low[v] >= disc[u]`, mark `u`."),
        ("Back edge", "For a visited neighbour `v` that is not the parent: `low[u] = min(low[u], disc[v])`."),
        ("Root rule", "After the loop: if `u` is the root and `children >= 2`, mark `u`."),
    )
    yield multi('''
        disc: 0 1 2 3 4
        low: 0 0 0 3 4
        articulation points: 1 3
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def articulation_points(adj):
            n = len(adj)
            disc, low, parent = [-1] * n, [0] * n, [-1] * n
            is_ap = [False] * n
            timer = [0]

            def dfs(u):
                disc[u] = low[u] = timer[0]
                timer[0] += 1
                children = 0
                for v in adj[u]:
                    if disc[v] == -1:                     # tree edge
                        parent[v] = u
                        children += 1
                        dfs(v)
                        low[u] = min(low[u], low[v])
                        if parent[u] != -1 and low[v] >= disc[u]:
                            is_ap[u] = True               # v's subtree cannot climb above u
                    elif v != parent[u]:                  # back edge
                        low[u] = min(low[u], disc[v])
                if parent[u] == -1 and children >= 2:
                    is_ap[u] = True                       # root rule

            for u in range(n):
                if disc[u] == -1:
                    dfs(u)
            print("disc:", *disc)
            print("low:", *low)
            return [u for u in range(n) if is_ap[u]]

        adj = build(5, [(0, 1), (0, 2), (1, 2), (1, 3), (3, 4)])
        print("articulation points:", *articulation_points(adj))
    ''', cpp=r'''
        #include <iostream>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        vector<int> disc, low, parent;
        vector<bool> isAp;
        int timer = 0;

        void dfs(const vector<vector<int>>& adj, int u) {
            disc[u] = low[u] = timer++;
            int children = 0;
            for (int v : adj[u]) {
                if (disc[v] == -1) {                      // tree edge
                    parent[v] = u;
                    children++;
                    dfs(adj, v);
                    low[u] = min(low[u], low[v]);
                    if (parent[u] != -1 && low[v] >= disc[u])
                        isAp[u] = true;                   // v's subtree cannot climb above u
                } else if (v != parent[u]) {              // back edge
                    low[u] = min(low[u], disc[v]);
                }
            }
            if (parent[u] == -1 && children >= 2) isAp[u] = true;   // root rule
        }

        int main() {
            auto adj = build(5, {{0, 1}, {0, 2}, {1, 2}, {1, 3}, {3, 4}});
            int n = adj.size();
            disc.assign(n, -1); low.assign(n, 0); parent.assign(n, -1); isAp.assign(n, false);
            for (int u = 0; u < n; u++)
                if (disc[u] == -1) dfs(adj, u);
            cout << "disc:";
            for (int d : disc) cout << " " << d;
            cout << "\nlow:";
            for (int l : low) cout << " " << l;
            cout << "\narticulation points:";
            for (int u = 0; u < n; u++)
                if (isAp[u]) cout << " " << u;
            cout << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static List<List<Integer>> adj;
            static int[] disc, low, parent;
            static boolean[] isAp;
            static int timer = 0;

            static void dfs(int u) {
                disc[u] = low[u] = timer++;
                int children = 0;
                for (int v : adj.get(u)) {
                    if (disc[v] == -1) {                      // tree edge
                        parent[v] = u;
                        children++;
                        dfs(v);
                        low[u] = Math.min(low[u], low[v]);
                        if (parent[u] != -1 && low[v] >= disc[u])
                            isAp[u] = true;                   // v's subtree cannot climb above u
                    } else if (v != parent[u]) {              // back edge
                        low[u] = Math.min(low[u], disc[v]);
                    }
                }
                if (parent[u] == -1 && children >= 2) isAp[u] = true;   // root rule
            }

            public static void main(String[] args) {
                adj = build(5, new int[][]{{0, 1}, {0, 2}, {1, 2}, {1, 3}, {3, 4}});
                int n = adj.size();
                disc = new int[n]; low = new int[n]; parent = new int[n]; isAp = new boolean[n];
                Arrays.fill(disc, -1);
                Arrays.fill(parent, -1);
                for (int u = 0; u < n; u++)
                    if (disc[u] == -1) dfs(u);
                StringBuilder sb = new StringBuilder("disc:");
                for (int d : disc) sb.append(' ').append(d);
                System.out.println(sb);
                sb = new StringBuilder("low:");
                for (int l : low) sb.append(' ').append(l);
                System.out.println(sb);
                sb = new StringBuilder("articulation points:");
                for (int u = 0; u < n; u++)
                    if (isAp[u]) sb.append(' ').append(u);
                System.out.println(sb);
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function articulationPoints(adj) {
            const n = adj.length;
            const disc = new Array(n).fill(-1), low = new Array(n).fill(0), parent = new Array(n).fill(-1);
            const isAp = new Array(n).fill(false);
            let timer = 0;

            function dfs(u) {
                disc[u] = low[u] = timer++;
                let children = 0;
                for (const v of adj[u]) {
                    if (disc[v] === -1) {                     // tree edge
                        parent[v] = u;
                        children++;
                        dfs(v);
                        low[u] = Math.min(low[u], low[v]);
                        if (parent[u] !== -1 && low[v] >= disc[u])
                            isAp[u] = true;                   // v's subtree cannot climb above u
                    } else if (v !== parent[u]) {             // back edge
                        low[u] = Math.min(low[u], disc[v]);
                    }
                }
                if (parent[u] === -1 && children >= 2) isAp[u] = true;   // root rule
            }

            for (let u = 0; u < n; u++)
                if (disc[u] === -1) dfs(u);
            console.log("disc:", disc.join(" "));
            console.log("low:", low.join(" "));
            return [...Array(n).keys()].filter(u => isAp[u]);
        }

        const adj = build(5, [[0, 1], [0, 2], [1, 2], [1, 3], [3, 4]]);
        console.log("articulation points:", articulationPoints(adj).join(" "));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield pitfall("Two classic mistakes. (1) Applying the `low[v] >= disc[u]` test to the **root**: the root's `disc` is 0, so every child passes it and the root would always be reported — the root needs the children count instead. (2) Writing `low[u] = min(low[u], low[v])` for a **back edge**: `low[v]` may already have been lowered through `v`'s own back edges to vertices *above* `u`, which makes `u` look safe when it is not. For a back edge use `disc[v]`.")
    yield note("The same `disc`/`low` arrays answer several questions at once: articulation points (`low[v] >= disc[u]`), bridges (`low[v] > disc[u]`, next section) and, in a directed graph, strongly connected components (`low[u] == disc[u]`). Learn the DFS once and remember the three conditions.")

    yield section("Bridges (cut edges)", "link")
    yield define("Bridge", "an edge of a connected undirected graph whose removal disconnects the graph. Every bridge lies on no cycle; equivalently, an edge is a bridge exactly when it is not part of any cycle.")
    yield diagram('''
        Graph 1                           Graph 2 (two triangles sharing 2)

        0 ───── 1 ═════ 3 ═════ 4         0 ───── 1         3 ───── 4
        │     ╱                            ╲     ╱           ╲     ╱
        │   ╱                               ╲   ╱             ╲   ╱
        2 ╱                                   2 ───────────────┘

        bridges: 1-3, 3-4                 bridges: none (2 is an articulation point, though)
    ''', "Edges 0-1, 0-2, 1-2, 1-3, 3-4 versus 0-1, 1-2, 2-0, 2-3, 3-4, 4-2")
    yield io("edges = 0-1, 0-2, 1-2, 1-3, 3-4", "1-3 3-4", "edges = 0-1, 1-2, 2-0, 2-3, 3-4, 4-2", "none")
    yield idea("Same DFS, same `disc` and `low`, one character different. The tree edge `u – v` is a bridge iff `low[v] > disc[u]`: nothing in `v`'s subtree reaches `u` **or anything above it**, so the tree edge is the only way out. With `>=` a back edge landing exactly on `u` would still count as a cycle through `u – v`, which is why that case is an articulation point but not a bridge. There is no root special case for bridges.")
    yield multi('''
        graph 1: 1-3 3-4
        graph 2: none
    ''', py=r'''
        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            return adj

        def bridges(adj):
            n = len(adj)
            disc, low = [-1] * n, [0] * n
            found = []
            timer = [0]

            def dfs(u, parent):
                disc[u] = low[u] = timer[0]
                timer[0] += 1
                for v in adj[u]:
                    if disc[v] == -1:                     # tree edge
                        dfs(v, u)
                        low[u] = min(low[u], low[v])
                        if low[v] > disc[u]:              # v's subtree never reaches u or above
                            found.append((min(u, v), max(u, v)))
                    elif v != parent:                     # back edge
                        low[u] = min(low[u], disc[v])

            for u in range(n):
                if disc[u] == -1:
                    dfs(u, -1)
            return sorted(found)

        g1 = build(5, [(0, 1), (0, 2), (1, 2), (1, 3), (3, 4)])
        g2 = build(5, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)])
        for name, g in (("graph 1", g1), ("graph 2", g2)):
            b = bridges(g)
            print(f"{name}:", " ".join(f"{u}-{v}" for u, v in b) if b else "none")
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <string>
        #include <vector>
        using namespace std;

        vector<vector<int>> build(int n, const vector<pair<int,int>>& edges) {
            vector<vector<int>> adj(n);
            for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
            return adj;
        }

        struct Bridges {
            const vector<vector<int>>& adj;
            vector<int> disc, low;
            vector<pair<int,int>> found;
            int timer = 0;

            Bridges(const vector<vector<int>>& g) : adj(g), disc(g.size(), -1), low(g.size(), 0) {}

            void dfs(int u, int parent) {
                disc[u] = low[u] = timer++;
                for (int v : adj[u]) {
                    if (disc[v] == -1) {                      // tree edge
                        dfs(v, u);
                        low[u] = min(low[u], low[v]);
                        if (low[v] > disc[u])                 // v's subtree never reaches u or above
                            found.push_back({min(u, v), max(u, v)});
                    } else if (v != parent) {                 // back edge
                        low[u] = min(low[u], disc[v]);
                    }
                }
            }

            vector<pair<int,int>> run() {
                for (int u = 0; u < (int)adj.size(); u++)
                    if (disc[u] == -1) dfs(u, -1);
                sort(found.begin(), found.end());
                return found;
            }
        };

        void report(const string& name, const vector<vector<int>>& g) {
            auto b = Bridges(g).run();
            cout << name << ":";
            if (b.empty()) cout << " none";
            for (auto [u, v] : b) cout << " " << u << "-" << v;
            cout << "\n";
        }

        int main() {
            report("graph 1", build(5, {{0, 1}, {0, 2}, {1, 2}, {1, 3}, {3, 4}}));
            report("graph 2", build(5, {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 2}}));
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<Integer>> build(int n, int[][] edges) {
                List<List<Integer>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
                return adj;
            }

            static List<List<Integer>> adj;
            static int[] disc, low;
            static List<int[]> found;
            static int timer;

            static void dfs(int u, int parent) {
                disc[u] = low[u] = timer++;
                for (int v : adj.get(u)) {
                    if (disc[v] == -1) {                      // tree edge
                        dfs(v, u);
                        low[u] = Math.min(low[u], low[v]);
                        if (low[v] > disc[u])                 // v's subtree never reaches u or above
                            found.add(new int[]{Math.min(u, v), Math.max(u, v)});
                    } else if (v != parent) {                 // back edge
                        low[u] = Math.min(low[u], disc[v]);
                    }
                }
            }

            static List<int[]> bridges(List<List<Integer>> g) {
                adj = g;
                int n = g.size();
                disc = new int[n]; low = new int[n]; found = new ArrayList<>(); timer = 0;
                Arrays.fill(disc, -1);
                for (int u = 0; u < n; u++)
                    if (disc[u] == -1) dfs(u, -1);
                found.sort((a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);
                return found;
            }

            static void report(String name, List<List<Integer>> g) {
                List<int[]> b = bridges(g);
                StringBuilder sb = new StringBuilder(name + ":");
                if (b.isEmpty()) sb.append(" none");
                for (int[] e : b) sb.append(' ').append(e[0]).append('-').append(e[1]);
                System.out.println(sb);
            }

            public static void main(String[] args) {
                report("graph 1", build(5, new int[][]{{0, 1}, {0, 2}, {1, 2}, {1, 3}, {3, 4}}));
                report("graph 2", build(5, new int[][]{{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 2}}));
            }
        }
    ''', js=r'''
        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v] of edges) { adj[u].push(v); adj[v].push(u); }
            return adj;
        }

        function bridges(adj) {
            const n = adj.length;
            const disc = new Array(n).fill(-1), low = new Array(n).fill(0);
            const found = [];
            let timer = 0;

            function dfs(u, parent) {
                disc[u] = low[u] = timer++;
                for (const v of adj[u]) {
                    if (disc[v] === -1) {                     // tree edge
                        dfs(v, u);
                        low[u] = Math.min(low[u], low[v]);
                        if (low[v] > disc[u])                 // v's subtree never reaches u or above
                            found.push([Math.min(u, v), Math.max(u, v)]);
                    } else if (v !== parent) {                // back edge
                        low[u] = Math.min(low[u], disc[v]);
                    }
                }
            }

            for (let u = 0; u < n; u++)
                if (disc[u] === -1) dfs(u, -1);
            return found.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
        }

        function report(name, g) {
            const b = bridges(g);
            console.log(`${name}:`, b.length ? b.map(([u, v]) => `${u}-${v}`).join(" ") : "none");
        }

        report("graph 1", build(5, [[0, 1], [0, 2], [1, 2], [1, 3], [3, 4]]));
        report("graph 2", build(5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 2]]));
    ''')
    yield complexity("O(V + E)", "O(V)")
    yield table(
        ["", "Articulation point `u`", "Bridge `u – v`"],
        ["Condition (tree edge `u → v`)", "`low[v] >= disc[u]`", "`low[v] > disc[u]`"],
        ["Root special case", "Yes — `>= 2` DFS children", "None"],
        ["Removing it", "Disconnects the graph; also removes its edges", "Disconnects the graph; vertices stay"],
        ["Relation", "Both endpoints of a bridge are articulation points unless they have degree 1", "A graph can have articulation points but no bridges (graph 2 above)"],
    )
    yield pitfall("With **parallel edges** the `v != parent` test is wrong for bridges — a doubled edge `u = v` is never a bridge, yet both copies are skipped as “the edge we came from”. Skip only the parent *edge index* (pass the index of the edge used to enter `u`), not every edge to the parent vertex. This matters for bridges more than for articulation points, because a double edge genuinely changes the answer.")

    yield section("Minimum spanning tree — Kruskal's algorithm", "git-branch")
    yield define("Minimum spanning tree (MST)", "of a connected, undirected, weighted graph: a subset of `V − 1` edges that connects every vertex (a spanning tree) with the smallest possible total weight. Laying cable between cities, clustering, approximating TSP — anything that asks for the cheapest way to connect everything.")
    yield diagram('''
                 4                                   MST (total 10)
        0 ─────────── 1
        │           ╱ │                              0       1
      1 │        2 ╱  │ 5                          1 │     ╱ │ 5
        │        ╱    │                              │  2 ╱  │
        2 ─────────── 3                              2 ╱     3
         ╲     8     ╱                                       │ 2
       10 ╲         ╱ 2                                      4
           ╲       ╱
               4
    ''', "The weighted graph from Dijkstra again: 0-1 (4), 0-2 (1), 1-2 (2), 1-3 (5), 2-3 (8), 2-4 (10), 3-4 (2) — its MST uses 0-2, 1-2, 3-4, 1-3")
    yield io("edges above, V = 5", "MST edges 0-2 (1), 1-2 (2), 3-4 (2), 1-3 (5); total weight 10")
    yield idea("**Greedy on edges.** Sort all edges by weight and take them in order, keeping an edge only if its two endpoints are not already connected — otherwise it would close a cycle. The cheapest edge crossing any cut belongs to some MST (the *cut property*), and the first edge that joins two separate pieces is exactly that cheapest crossing edge. Stop after `V − 1` edges.")
    yield steps(
        ("Sort", "All `E` edges by weight, ascending — `O(E log E)`."),
        ("Initialise", "`mst = {}`, `total = 0`, every vertex in its own set."),
        ("Scan", "For each edge `(u, v, w)` in sorted order, while `|mst| < V − 1`: if `u` and `v` are in different sets, add the edge, `total += w`, and merge the two sets."),
        ("Return", "`total` and the chosen edges."),
    )
    yield p("**Naive version (from the notes).** Keep the partial MST as a *separate graph* and, for every candidate edge, run a DFS in it to see whether `u` can already reach `v` — if so, the edge would form a cycle. Correct, but each check costs `O(V)` and there are `E` of them: `O(E · V)`.")
    yield snippet("py", r'''
        def connected(mst_adj, u, v):             # DFS inside the partial MST: can u already reach v?
            visited = [False] * len(mst_adj)
            stack = [u]
            visited[u] = True
            while stack:
                x = stack.pop()
                if x == v:
                    return True
                for y in mst_adj[x]:
                    if not visited[y]:
                        visited[y] = True
                        stack.append(y)
            return False

        def kruskal_naive(n, edges):
            mst_adj = [[] for _ in range(n)]      # a second graph holding only chosen edges
            total, chosen = 0, []
            for u, v, w in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
                if len(chosen) == n - 1:
                    break
                if not connected(mst_adj, u, v):  # O(V) check per edge
                    mst_adj[u].append(v)
                    mst_adj[v].append(u)
                    chosen.append((u, v, w))
                    total += w
            return total, chosen

        edges = [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8), (2, 4, 10), (3, 4, 2)]
        total, chosen = kruskal_naive(5, edges)
        for u, v, w in chosen:
            print(f"{u}-{v} ({w})")
        print("total weight:", total)
    ''', out='''
        0-2 (1)
        1-2 (2)
        3-4 (2)
        1-3 (5)
        total weight: 10
    ''', caption="Python — naive O(E · V) cycle check")
    yield p("**Efficient version.** The “are `u` and `v` already connected?” question is exactly what a **disjoint set (union–find)** answers in near-constant time: `find(u) == find(v)` means same component; `union(u, v)` merges two. With **path compression** (point every node on the `find` path straight at the root) and **union by rank** (hang the shorter tree under the taller) each operation is `O(α(V))`, effectively constant, so the sort dominates.")
    yield multi('''
        0-2 (1)
        1-2 (2)
        3-4 (2)
        1-3 (5)
        total weight: 10
    ''', py=r'''
        class DisjointSet:
            def __init__(self, n):
                self.parent = list(range(n))
                self.rank = [0] * n

            def find(self, u):
                if self.parent[u] != u:
                    self.parent[u] = self.find(self.parent[u])   # path compression
                return self.parent[u]

            def union(self, u, v):                # returns false if u and v were already joined
                ru, rv = self.find(u), self.find(v)
                if ru == rv:
                    return False
                if self.rank[ru] < self.rank[rv]:  # union by rank: shorter tree under the taller
                    ru, rv = rv, ru
                self.parent[rv] = ru
                if self.rank[ru] == self.rank[rv]:
                    self.rank[ru] += 1
                return True

        def kruskal(n, edges):
            edges = sorted(edges, key=lambda e: (e[2], e[0], e[1]))   # by weight (ties: by endpoints)
            ds = DisjointSet(n)
            total, chosen = 0, []
            for u, v, w in edges:
                if len(chosen) == n - 1:
                    break                         # a spanning tree has exactly V - 1 edges
                if ds.union(u, v):                # different components -> no cycle
                    chosen.append((u, v, w))
                    total += w
            return total, chosen

        edges = [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8), (2, 4, 10), (3, 4, 2)]
        total, chosen = kruskal(5, edges)
        for u, v, w in chosen:
            print(f"{u}-{v} ({w})")
        print("total weight:", total)
    ''', cpp=r'''
        #include <algorithm>
        #include <iostream>
        #include <vector>
        using namespace std;

        struct Edge { int u, v, w; };

        struct DisjointSet {
            vector<int> parent, rank_;
            DisjointSet(int n) : parent(n), rank_(n, 0) {
                for (int i = 0; i < n; i++) parent[i] = i;
            }
            int find(int u) {
                if (parent[u] != u) parent[u] = find(parent[u]);   // path compression
                return parent[u];
            }
            bool unite(int u, int v) {            // false if u and v were already joined
                int ru = find(u), rv = find(v);
                if (ru == rv) return false;
                if (rank_[ru] < rank_[rv]) swap(ru, rv);           // union by rank
                parent[rv] = ru;
                if (rank_[ru] == rank_[rv]) rank_[ru]++;
                return true;
            }
        };

        int kruskal(int n, vector<Edge> edges, vector<Edge>& chosen) {
            sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
                if (a.w != b.w) return a.w < b.w;                  // by weight (ties: by endpoints)
                return a.u != b.u ? a.u < b.u : a.v < b.v;
            });
            DisjointSet ds(n);
            int total = 0;
            for (auto& e : edges) {
                if ((int)chosen.size() == n - 1) break;            // a spanning tree has V - 1 edges
                if (ds.unite(e.u, e.v)) {                          // different components -> no cycle
                    chosen.push_back(e);
                    total += e.w;
                }
            }
            return total;
        }

        int main() {
            vector<Edge> edges = {{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}};
            vector<Edge> chosen;
            int total = kruskal(5, edges, chosen);
            for (auto& e : chosen) cout << e.u << "-" << e.v << " (" << e.w << ")\n";
            cout << "total weight: " << total << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static class DisjointSet {
                int[] parent, rank;
                DisjointSet(int n) {
                    parent = new int[n]; rank = new int[n];
                    for (int i = 0; i < n; i++) parent[i] = i;
                }
                int find(int u) {
                    if (parent[u] != u) parent[u] = find(parent[u]);   // path compression
                    return parent[u];
                }
                boolean union(int u, int v) {         // false if u and v were already joined
                    int ru = find(u), rv = find(v);
                    if (ru == rv) return false;
                    if (rank[ru] < rank[rv]) { int t = ru; ru = rv; rv = t; }   // union by rank
                    parent[rv] = ru;
                    if (rank[ru] == rank[rv]) rank[ru]++;
                    return true;
                }
            }

            static List<int[]> chosen = new ArrayList<>();

            static int kruskal(int n, int[][] edges) {
                Arrays.sort(edges, (a, b) -> a[2] != b[2] ? a[2] - b[2]        // by weight
                                           : a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);   // ties: by endpoints
                DisjointSet ds = new DisjointSet(n);
                int total = 0;
                for (int[] e : edges) {
                    if (chosen.size() == n - 1) break;              // a spanning tree has V - 1 edges
                    if (ds.union(e[0], e[1])) {                     // different components -> no cycle
                        chosen.add(e);
                        total += e[2];
                    }
                }
                return total;
            }

            public static void main(String[] args) {
                int[][] edges = {{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}};
                int total = kruskal(5, edges);
                for (int[] e : chosen) System.out.println(e[0] + "-" + e[1] + " (" + e[2] + ")");
                System.out.println("total weight: " + total);
            }
        }
    ''', js=r'''
        class DisjointSet {
            constructor(n) {
                this.parent = Array.from({ length: n }, (_, i) => i);
                this.rank = new Array(n).fill(0);
            }
            find(u) {
                if (this.parent[u] !== u) this.parent[u] = this.find(this.parent[u]);   // path compression
                return this.parent[u];
            }
            union(u, v) {                             // false if u and v were already joined
                let ru = this.find(u), rv = this.find(v);
                if (ru === rv) return false;
                if (this.rank[ru] < this.rank[rv]) [ru, rv] = [rv, ru];   // union by rank
                this.parent[rv] = ru;
                if (this.rank[ru] === this.rank[rv]) this.rank[ru]++;
                return true;
            }
        }

        function kruskal(n, edges) {
            const sorted = [...edges].sort((a, b) => a[2] - b[2] || a[0] - b[0] || a[1] - b[1]);   // by weight, ties by endpoints
            const ds = new DisjointSet(n);
            let total = 0;
            const chosen = [];
            for (const [u, v, w] of sorted) {
                if (chosen.length === n - 1) break;   // a spanning tree has V - 1 edges
                if (ds.union(u, v)) {                 // different components -> no cycle
                    chosen.push([u, v, w]);
                    total += w;
                }
            }
            return { total, chosen };
        }

        const edges = [[0, 1, 4], [0, 2, 1], [1, 2, 2], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2]];
        const { total, chosen } = kruskal(5, edges);
        for (const [u, v, w] of chosen) console.log(`${u}-${v} (${w})`);
        console.log("total weight:", total);
    ''')
    yield complexity("O(E log E) for the sort; the union–find work is O(E · α(V))", "O(V + E)")
    yield pitfall("Forgetting the cycle check (just taking the `V − 1` cheapest edges) is the classic wrong answer: here the three cheapest edges are 0-2, 1-2, 3-4 and the fourth cheapest, 0-1 (4), closes the triangle 0-1-2 — Kruskal must skip it and take 1-3 (5). Also: if the graph is **disconnected**, fewer than `V − 1` edges get chosen and the result is a minimum spanning *forest*, not a tree — check the count.")
    yield note("Kruskal works on the plain **edge list** — no adjacency list needed — and is the natural choice when the edges are already sorted or arrive one at a time. Because it processes edges globally rather than growing from a vertex, it also handles disconnected graphs gracefully.")

    yield section("Minimum spanning tree — Prim's algorithm", "git-branch")
    yield idea("**Greedy on vertices.** Grow the tree from one start vertex: at every step add the **cheapest edge that leaves the tree** (one endpoint inside, one outside). That edge crosses the cut between the tree and the rest, so by the cut property it belongs to an MST. It is Dijkstra with a different key: the edge weight alone instead of the distance from the source.")
    yield io("edges above, start = 0", "MST edges 0-2 (1), 2-1 (2), 1-3 (5), 3-4 (2); total weight 10 — the same tree Kruskal found, grown in a different order")
    yield steps(
        ("Initialise", "`inMST[v] = false` for all `v`; push `(0, start, −1)` into a min-heap keyed by weight."),
        ("Extract-min", "Pop `(w, v, from)`. If `v` is already in the tree, skip (a stale entry)."),
        ("Add", "Mark `inMST[v]`; if `from != −1` record the edge `from – v` and `total += w`."),
        ("Push neighbours", "For every edge `v – x` with weight `w'` where `x` is not in the tree: push `(w', x, v)`."),
    )
    yield multi('''
        0-2 (1)
        2-1 (2)
        1-3 (5)
        3-4 (2)
        total weight: 10
    ''', py=r'''
        import heapq

        def build(n, edges):
            adj = [[] for _ in range(n)]
            for u, v, w in edges:
                adj[u].append((v, w))
                adj[v].append((u, w))             # undirected, weighted
            return adj

        def prim(adj, start=0):
            n = len(adj)
            in_mst = [False] * n
            pq = [(0, start, -1)]                 # (weight, vertex, from) min-heap
            total, chosen = 0, []
            while pq:
                w, v, frm = heapq.heappop(pq)
                if in_mst[v]:
                    continue                      # stale entry: v was added via a cheaper edge
                in_mst[v] = True
                if frm != -1:
                    chosen.append((frm, v, w))    # the edge that brought v into the tree
                    total += w
                for x, wx in adj[v]:
                    if not in_mst[x]:
                        heapq.heappush(pq, (wx, x, v))
            return total, chosen

        adj = build(5, [(0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 8), (2, 4, 10), (3, 4, 2)])
        total, chosen = prim(adj)
        for u, v, w in chosen:
            print(f"{u}-{v} ({w})")
        print("total weight:", total)
    ''', cpp=r'''
        #include <iostream>
        #include <queue>
        #include <tuple>
        #include <vector>
        using namespace std;

        struct Edge { int u, v, w; };

        vector<vector<pair<int,int>>> build(int n, const vector<Edge>& edges) {
            vector<vector<pair<int,int>>> adj(n);
            for (auto& e : edges) {
                adj[e.u].push_back({e.v, e.w});
                adj[e.v].push_back({e.u, e.w});   // undirected, weighted
            }
            return adj;
        }

        int prim(const vector<vector<pair<int,int>>>& adj, int start, vector<Edge>& chosen) {
            int n = adj.size();
            vector<bool> inMst(n, false);
            using Item = tuple<int,int,int>;     // (weight, vertex, from) — tuples compare lexicographically
            priority_queue<Item, vector<Item>, greater<Item>> pq;
            pq.push({0, start, -1});
            int total = 0;
            while (!pq.empty()) {
                auto [w, v, from] = pq.top(); pq.pop();
                if (inMst[v]) continue;           // stale entry: v was added via a cheaper edge
                inMst[v] = true;
                if (from != -1) {
                    chosen.push_back({from, v, w});   // the edge that brought v into the tree
                    total += w;
                }
                for (auto [x, wx] : adj[v])
                    if (!inMst[x]) pq.push({wx, x, v});
            }
            return total;
        }

        int main() {
            auto adj = build(5, {{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}});
            vector<Edge> chosen;
            int total = prim(adj, 0, chosen);
            for (auto& e : chosen) cout << e.u << "-" << e.v << " (" << e.w << ")\n";
            cout << "total weight: " << total << "\n";
        }
    ''', java=r'''
        import java.util.*;

        public class Main {
            static List<List<int[]>> build(int n, int[][] edges) {
                List<List<int[]>> adj = new ArrayList<>();
                for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
                for (int[] e : edges) {
                    adj.get(e[0]).add(new int[]{e[1], e[2]});
                    adj.get(e[1]).add(new int[]{e[0], e[2]});   // undirected, weighted
                }
                return adj;
            }

            static List<int[]> chosen = new ArrayList<>();

            static int prim(List<List<int[]>> adj, int start) {
                int n = adj.size();
                boolean[] inMst = new boolean[n];
                // min-heap of {weight, vertex, from}, compared field by field
                PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) ->
                        a[0] != b[0] ? a[0] - b[0] : a[1] != b[1] ? a[1] - b[1] : a[2] - b[2]);
                pq.add(new int[]{0, start, -1});
                int total = 0;
                while (!pq.isEmpty()) {
                    int[] top = pq.poll();
                    int w = top[0], v = top[1], from = top[2];
                    if (inMst[v]) continue;           // stale entry: v was added via a cheaper edge
                    inMst[v] = true;
                    if (from != -1) {
                        chosen.add(new int[]{from, v, w});   // the edge that brought v into the tree
                        total += w;
                    }
                    for (int[] e : adj.get(v))
                        if (!inMst[e[0]]) pq.add(new int[]{e[1], e[0], v});
                }
                return total;
            }

            public static void main(String[] args) {
                List<List<int[]>> adj = build(5, new int[][]{{0, 1, 4}, {0, 2, 1}, {1, 2, 2}, {1, 3, 5}, {2, 3, 8}, {2, 4, 10}, {3, 4, 2}});
                int total = prim(adj, 0);
                for (int[] e : chosen) System.out.println(e[0] + "-" + e[1] + " (" + e[2] + ")");
                System.out.println("total weight: " + total);
            }
        }
    ''', js=r'''
        // Minimal binary min-heap of [weight, vertex, from] triples, compared field by field
        // (JavaScript has no built-in priority queue; a sorted array with splice() also works for small graphs).
        class MinHeap {
            constructor() { this.a = []; }
            get size() { return this.a.length; }
            less(i, j) {
                const x = this.a[i], y = this.a[j];
                return x[0] !== y[0] ? x[0] < y[0] : x[1] !== y[1] ? x[1] < y[1] : x[2] < y[2];
            }
            swap(i, j) { [this.a[i], this.a[j]] = [this.a[j], this.a[i]]; }
            push(item) {
                this.a.push(item);
                for (let i = this.a.length - 1; i > 0; i = (i - 1) >> 1)
                    if (this.less(i, (i - 1) >> 1)) this.swap(i, (i - 1) >> 1); else break;
            }
            pop() {
                const top = this.a[0], last = this.a.pop();
                if (this.a.length) {
                    this.a[0] = last;
                    for (let i = 0; ;) {
                        let m = i;
                        const l = 2 * i + 1, r = l + 1;
                        if (l < this.a.length && this.less(l, m)) m = l;
                        if (r < this.a.length && this.less(r, m)) m = r;
                        if (m === i) break;
                        this.swap(i, m); i = m;
                    }
                }
                return top;
            }
        }

        function build(n, edges) {
            const adj = Array.from({ length: n }, () => []);
            for (const [u, v, w] of edges) { adj[u].push([v, w]); adj[v].push([u, w]); }   // undirected, weighted
            return adj;
        }

        function prim(adj, start = 0) {
            const n = adj.length;
            const inMst = new Array(n).fill(false);
            const pq = new MinHeap();                 // [weight, vertex, from]
            pq.push([0, start, -1]);
            let total = 0;
            const chosen = [];
            while (pq.size) {
                const [w, v, from] = pq.pop();
                if (inMst[v]) continue;               // stale entry: v was added via a cheaper edge
                inMst[v] = true;
                if (from !== -1) {
                    chosen.push([from, v, w]);        // the edge that brought v into the tree
                    total += w;
                }
                for (const [x, wx] of adj[v])
                    if (!inMst[x]) pq.push([wx, x, v]);
            }
            return { total, chosen };
        }

        const adj = build(5, [[0, 1, 4], [0, 2, 1], [1, 2, 2], [1, 3, 5], [2, 3, 8], [2, 4, 10], [3, 4, 2]]);
        const { total, chosen } = prim(adj);
        for (const [u, v, w] of chosen) console.log(`${u}-${v} (${w})`);
        console.log("total weight:", total);
    ''')
    yield complexity("O((V + E) log V) with a binary heap; O(V²) with an array scan", "O(V + E)")
    yield pitfall("Prim's key is the **weight of the single edge** into the tree, not the accumulated distance from the start — copy Dijkstra's `d + w` by habit and you get a shortest-path tree, which is generally *not* a minimum spanning tree. On this graph the two happen to coincide (same four edges, total 10); on the triangle 0-1 (2), 1-2 (2), 0-2 (3) the MST is `{0-1, 1-2}` with weight 4 while Dijkstra's tree from 0 is `{0-1, 0-2}` with weight 5. Prim also assumes a **connected** graph: started from one vertex it never reaches another component.")
    yield table(
        ["", "Kruskal", "Prim"],
        ["Grows", "A forest: picks edges globally, cheapest first", "One tree from a start vertex, cheapest outgoing edge first"],
        ["Input it wants", "Edge list (sorted)", "Adjacency list (or matrix)"],
        ["Data structure", "Disjoint set (union–find)", "Min-heap keyed by edge weight"],
        ["Time", "`O(E log E)`", "`O((V + E) log V)` heap · `O(V²)` array"],
        ["Best for", "**Sparse** graphs, edges already sorted, streaming edges, disconnected graphs (gives a forest)", "**Dense** graphs (`E ≈ V²` — use the `O(V²)` array version), adjacency-matrix input"],
        ["Result", "Same total weight; with distinct edge weights the MST is unique and both return the identical tree", "Same"],
    )
    yield note("Both are greedy and both are correct because of the **cut property**: for any partition of the vertices into two sets, the cheapest edge crossing the partition is in some MST. Kruskal applies it to the cut between the two components an edge joins; Prim applies it to the cut between the tree and everything else.")

    yield section("Which algorithm when", "bulb")
    yield table(
        ["Problem", "Algorithm", "Graph type", "Time", "Remember"],
        ["Traverse / reach / count components", "BFS or DFS", "Any", "`O(V + E)`", "Shared `visited` array; outer loop over all vertices for disconnected graphs"],
        ["Shortest path, unweighted", "BFS", "Any", "`O(V + E)`", "`dist[v] = dist[u] + 1`, `parent[]` for the path"],
        ["Cycle detection", "DFS (`parent` / `onStack`) or Kahn", "Undirected / directed", "`O(V + E)`", "Undirected: visited non-parent; directed: vertex on the recursion stack"],
        ["Topological order", "Kahn (BFS) or DFS finish order", "DAG", "`O(V + E)`", "Kahn detects cycles for free; min-heap gives the lexicographically smallest order"],
        ["Shortest path, weighted DAG", "One relaxation pass in topological order", "DAG, any weights", "`O(V + E)`", "Also longest path (negate weights)"],
        ["Shortest path, non-negative weights", "Dijkstra", "Directed or undirected, `w ≥ 0`", "`O((V + E) log V)`", "Min-heap of `(dist, v)`, skip stale entries"],
        ["Shortest path, negative weights", "Bellman–Ford", "Directed, any weights", "`O(V · E)`", "`V − 1` passes over all edges; a `V`-th improvement = negative cycle"],
        ["Strongly connected components", "Kosaraju (2 DFS) or Tarjan (1 DFS)", "Directed", "`O(V + E)`", "Kosaraju: reverse graph + finish order; Tarjan: `low[u] == disc[u]`"],
        ["Articulation points / bridges", "Tarjan low-link DFS", "Undirected", "`O(V + E)`", "`low[v] >= disc[u]` (vertex, root: ≥ 2 children) · `low[v] > disc[u]` (edge)"],
        ["Minimum spanning tree", "Kruskal or Prim", "Undirected, weighted, connected", "`O(E log E)` · `O((V + E) log V)`", "Kruskal: sort + union–find (sparse); Prim: heap from a start vertex (dense)"],
    )
    yield note("Two questions sort almost every graph problem: **directed or undirected?** and **weighted or not?** Unweighted → BFS; weighted and non-negative → Dijkstra; negative edges → Bellman–Ford (or a DAG pass); “order the tasks” → topological sort; “connect everything cheaply” → MST; “single point of failure” → articulation points and bridges.")

    yield section("Interview Q&A", "message-question")
    yield qa("BFS or DFS — how do you decide?",
             "BFS when **distance from the source** matters: shortest path in an unweighted graph, nearest neighbour, anything level by level. DFS when the **structure** matters: cycle detection, topological order, strongly connected components, articulation points, backtracking through a state space. Both are `O(V + E)`; BFS uses `O(width)` memory for the frontier, DFS `O(depth)` for the recursion stack (and recursion can overflow on long paths — use an explicit stack for big inputs).")
    yield qa("Why does Dijkstra fail with negative edge weights?",
             "Dijkstra settles the closest unsettled vertex and assumes its distance is final, because with non-negative weights any other route must pass through a farther vertex and can only get longer. A negative edge breaks that assumption: a longer-looking route can end up shorter once it takes the negative edge, so an already settled vertex would need to be improved. Example: `0→1 (2)`, `0→2 (5)`, `2→1 (−4)` — Dijkstra settles 1 at distance 2, but the true distance is 1. Use Bellman–Ford, or a single topological pass if the graph is a DAG.")
    yield qa("Kahn's algorithm or DFS for topological sort?",
             "Both are `O(V + E)` and both give a valid order. Kahn's (indegree + queue) is iterative, detects cycles automatically (fewer than `V` vertices output) and, with a min-heap in place of the queue, gives the lexicographically smallest order — which is why it is usually preferred in interviews. The DFS version (reverse finish order) is shorter to write and is the same post-order that Kosaraju's SCC algorithm uses, but it silently produces garbage on a cyclic graph unless you add the `onStack` check.")
    yield qa("Adjacency list or adjacency matrix — which do you choose and why?",
             "Default to the **adjacency list**: `Θ(V + E)` memory and `Θ(degree)` to scan a vertex's neighbours, so every traversal is `Θ(V + E)`. Real graphs are sparse — a social network with a billion users does not have `10^18` friendships — and a matrix would need `Θ(V²)` space just to store zeros. Pick the **matrix** when the graph is dense (`E ≈ V²`), when `O(1)` “is there an edge `u – v`?” lookups dominate, or when the algorithm is matrix-shaped (Floyd–Warshall, Prim's `O(V²)` version).")
    yield qa("Kruskal or Prim — which would you use?",
             "Both are greedy, both are correct by the cut property, and both give an MST of the same weight. **Kruskal** sorts the edge list and uses union–find: `O(E log E)`, works straight from an edge list, handles disconnected graphs (it returns a spanning forest) — the choice for sparse graphs or when edges are already sorted. **Prim** grows one tree with a heap: `O((V + E) log V)`, or `O(V²)` with a plain array scan, which beats Kruskal on dense graphs and adjacency-matrix input. In practice: sparse → Kruskal, dense → Prim.")
    yield qa("What does the low-link value mean, and what are the three conditions built on it?",
             "`disc[u]` is the DFS counter when `u` is discovered; `low[u]` is the smallest `disc` that `u`'s subtree can reach using tree edges plus at most one back edge. It measures how far *up* the DFS tree a subtree can climb without using its parent edge. Three tests follow from it, all `O(V + E)` in one DFS: a tree edge `u – v` is a **bridge** when `low[v] > disc[u]` (the subtree cannot climb to `u` or above); a non-root `u` is an **articulation point** when `low[v] >= disc[u]` for some child `v` (the subtree reaches `u` at best — removing `u` strands it; the root instead needs two or more DFS children); and in a directed graph `u` is the **root of an SCC** when `low[u] == disc[u]`, at which point the stack above `u` is popped as one component.")
