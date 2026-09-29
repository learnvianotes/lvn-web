from kit import *

G = "Search"

ROMANIA = '''
        ROADS = """Arad Zerind 75, Arad Sibiu 140, Arad Timisoara 118, Zerind Oradea 71, Oradea Sibiu 151,
        Timisoara Lugoj 111, Lugoj Mehadia 70, Mehadia Drobeta 75, Drobeta Craiova 120, Craiova Rimnicu 146,
        Craiova Pitesti 138, Sibiu Fagaras 99, Sibiu Rimnicu 80, Rimnicu Pitesti 97, Fagaras Bucharest 211,
        Pitesti Bucharest 101, Bucharest Giurgiu 90, Bucharest Urziceni 85, Urziceni Hirsova 98,
        Hirsova Eforie 86, Urziceni Vaslui 142, Vaslui Iasi 92, Iasi Neamt 87"""
        graph = {}                                  # city -> {neighbour: road km}  ("Rimnicu" = Rimnicu Vilcea)
        for road in ROADS.split(","):
            a, b, km = road.split()
            graph.setdefault(a, {})[b] = int(km)
            graph.setdefault(b, {})[a] = int(km)
'''


@topic(G, "problem-formulation", "Problem Formulation & State Spaces", "route")
def _():
    yield lead("Before an agent can search for a solution, the problem must be stated precisely: what a state is, which actions exist, what they do, what counts as the goal and what each step costs. A good formulation can shrink the search space by orders of magnitude.")
    yield section("The five components of a search problem", "list-numbers")
    yield table(
        ["Component", "Meaning", "Route finding (Romania)", "8-puzzle"],
        ["**Initial state**", "Where the agent starts", "In(Arad)", "A scrambled board"],
        ["**Actions(s)**", "Moves applicable in state `s`", "Drive to a neighbouring city", "Slide the blank Up/Down/Left/Right"],
        ["**Transition model** Result(s, a)", "The state an action leads to", "In(Sibiu) after driving Arad → Sibiu", "Board with blank and tile swapped"],
        ["**Goal test**", "Is `s` a goal?", "In(Bucharest)", "Tiles in order 0–8"],
        ["**Path cost**", "Sum of step costs `c(s, a, s′)`", "Road kilometres", "1 per move"],
    )
    yield p("Initial state + actions + transition model define the **state space** — a graph whose nodes are states and edges are actions. A **solution** is an action sequence from the initial state to a goal; an **optimal** solution has the lowest path cost.")
    yield section("Formulating the 8-puzzle", "grid-dots")
    yield code('''
        from collections import deque

        GOAL = (0, 1, 2,
                3, 4, 5,
                6, 7, 8)                       # 0 is the blank

        def actions(state):
            row, col = divmod(state.index(0), 3)
            moves = []
            if row > 0: moves.append("Up")
            if row < 2: moves.append("Down")
            if col > 0: moves.append("Left")
            if col < 2: moves.append("Right")
            return moves

        def result(state, action):              # transition model: slide the blank
            i = state.index(0)
            j = i + {"Up": -3, "Down": 3, "Left": -1, "Right": 1}[action]
            s = list(state)
            s[i], s[j] = s[j], s[i]
            return tuple(s)

        start = (3, 1, 2,
                 0, 4, 5,
                 6, 7, 8)
        print(actions(start))                            # ['Up', 'Down', 'Right']
        print(result(start, "Up") == GOAL)               # True

        # the whole state space reachable from the goal, by breadth-first expansion
        seen, frontier = {GOAL}, deque([GOAL])
        while frontier:
            s = frontier.popleft()
            for a in actions(s):
                t = result(s, a)
                if t not in seen:
                    seen.add(t)
                    frontier.append(t)
        print(len(seen))                                 # 181440 ← 9!/2: only half of all 9! boards are reachable
    ''')
    yield section("Formulation decides the size of the space", "zoom-in")
    yield table(
        ["Problem", "Formulation", "States"],
        ["8-queens", "Add queens anywhere, one at a time (64 squares, 8 queens)", "64 · 63 · … · 57 ≈ 1.8 × 10¹⁴ sequences"],
        ["8-queens", "One queen per column, left to right, never attacking an earlier one", "2,057"],
        ["8-puzzle", "All boards", "9!/2 = 181,440 reachable"],
        ["15-puzzle", "All boards", "16!/2 ≈ 1.05 × 10¹³"],
        ["Rubik's cube", "All positions", "≈ 4.3 × 10¹⁹"],
    )
    yield note("**Abstraction** is the art of formulation: drop every detail that doesn't affect the solution (the radio, the weather, the exact route between cities). A good abstraction is valid (every abstract solution maps to a real one) and useful (the abstract actions are easy to carry out).")
    yield section("Search trees, frontiers and repeated states", "binary-tree")
    yield p("Search algorithms grow a **search tree** over the state space. Each **node** stores a state, its parent, the action that produced it, the path cost `g` and the depth. The **frontier** (open list) holds generated-but-not-expanded nodes; the order in which it is expanded is the *only* difference between most search strategies.")
    yield steps(
        ("Initialise", "Put a node for the initial state on the frontier."),
        ("Choose", "Remove a node from the frontier according to the strategy (FIFO, LIFO, lowest cost…)."),
        ("Test", "If its state is a goal, return the path (follow parent links back)."),
        ("Expand", "Otherwise generate its children — one per applicable action — and add them to the frontier."),
        ("Repeat", "Until the frontier is empty → failure."),
    )
    yield dodont("Use **graph search**: keep a *reached/explored* set so each state is expanded at most once — cycles and redundant paths (A→B→A→B…) are pruned.",
                 "Plain **tree search** on a graph with cycles or many paths to the same state — it can loop forever or blow up exponentially.")
    yield section("Measuring a search strategy", "ruler-measure")
    yield table(
        ["Criterion", "Question", "Symbols used"],
        ["**Completeness**", "Is it guaranteed to find a solution when one exists?", "`b` = branching factor (max children per node)"],
        ["**Optimality** (cost-optimal)", "Does it find the lowest-cost solution?", "`d` = depth of the shallowest goal"],
        ["**Time complexity**", "How many nodes does it generate?", "`m` = maximum depth of the state space (may be ∞)"],
        ["**Space complexity**", "How many nodes are in memory at once?", "`C*` = optimal cost, `ε` = smallest step cost"],
    )
    yield qa("What are the components of a well-defined search problem?",
             "Initial state, actions, transition model, goal test and path-cost function. The first three implicitly define the state space.")
    yield qa("What is the difference between a state and a node?",
             "A state is a configuration of the world. A node is a bookkeeping structure in the search tree: a state plus parent pointer, action, path cost and depth. The same state can appear in many nodes (reached by different paths).")
    yield qa("Tree search vs graph search?",
             "Graph search remembers visited states and never re-expands them, so it avoids loops and redundant paths at the cost of memory. Tree search keeps no such set and can revisit states indefinitely.")


@topic(G, "uninformed-search", "Uninformed Search: BFS, DFS & UCS", "sitemap")
def _():
    yield lead("Uninformed (blind) strategies know nothing about where the goal is — only how to generate successors and test for the goal. They differ solely in **which frontier node to expand next**.")
    yield table(
        ["Strategy", "Frontier", "Expands", "Finds"],
        ["**Breadth-first (BFS)**", "FIFO queue", "Shallowest node first — level by level", "The path with the **fewest steps**"],
        ["**Depth-first (DFS)**", "LIFO stack (or recursion)", "Deepest node first", "*Some* path — often long"],
        ["**Uniform-cost (UCS)**", "Priority queue on path cost `g(n)`", "Cheapest-so-far node first", "The **lowest-cost** path (Dijkstra's algorithm)"],
    )
    yield section("BFS and DFS on the Romania map", "map-2")
    yield p("The classic textbook example: drive from Arad to Bucharest. Roads have lengths in km; the neighbour order below is the order roads were listed.")
    yield code(ROMANIA + '''
        from collections import deque

        def path(parent, node):
            out = []
            while node:
                out.append(node)
                node = parent[node]
            return out[::-1]

        def bfs(start, goal):
            frontier, parent, expanded = deque([start]), {start: None}, 0
            while frontier:
                node = frontier.popleft()                     # FIFO: oldest node first
                expanded += 1
                for nbr in graph[node]:
                    if nbr not in parent:
                        parent[nbr] = node
                        if nbr == goal:                       # BFS may test the goal when a node is generated
                            return path(parent, nbr), expanded
                        frontier.append(nbr)

        def dfs(start, goal):
            frontier, parent, expanded = [start], {start: None}, 0
            while frontier:
                node = frontier.pop()                         # LIFO: newest node first
                if node == goal:
                    return path(parent, node), expanded
                expanded += 1
                for nbr in graph[node]:
                    if nbr not in parent:
                        parent[nbr] = node
                        frontier.append(nbr)

        def cost(route):
            return sum(graph[a][b] for a, b in zip(route, route[1:]))

        route, n = bfs("Arad", "Bucharest")
        print(route, cost(route), n)     # ['Arad', 'Sibiu', 'Fagaras', 'Bucharest'] 450 6
        route, n = dfs("Arad", "Bucharest")
        print(route, cost(route), n)     # ['Arad', 'Timisoara', 'Lugoj', 'Mehadia', 'Drobeta', 'Craiova', 'Pitesti', 'Bucharest'] 733 7
    ''')
    yield p("BFS finds the route with the fewest roads (3), but it is **not** the shortest in km. DFS dives down whichever branch it pushed last and returns a much longer route.")
    yield section("Uniform-cost search", "coins")
    yield p("UCS always expands the frontier node with the lowest path cost `g(n)`. It must test for the goal when a node is **popped**, not when it is generated — a cheaper route to the goal may still be on the frontier.")
    yield code(ROMANIA + '''
        import heapq

        def ucs(start, goal):
            frontier = [(0, start)]                           # (path cost g, city)
            best, parent, expanded = {start: 0}, {start: None}, []
            while frontier:
                g, node = heapq.heappop(frontier)
                if node == goal:                              # goal test on expansion → optimal
                    route = [node]
                    while parent[route[-1]]:
                        route.append(parent[route[-1]])
                    return route[::-1], g, expanded
                if g > best[node]:
                    continue                                  # stale entry: a cheaper path was found later
                expanded.append(node)
                for nbr, km in graph[node].items():
                    if g + km < best.get(nbr, float("inf")):
                        best[nbr], parent[nbr] = g + km, node
                        heapq.heappush(frontier, (g + km, nbr))

        route, g, expanded = ucs("Arad", "Bucharest")
        print(route, g)          # ['Arad', 'Sibiu', 'Rimnicu', 'Pitesti', 'Bucharest'] 418
        print(len(expanded))     # 12
        print(expanded[:6])      # ['Arad', 'Zerind', 'Timisoara', 'Sibiu', 'Oradea', 'Rimnicu']
    ''')
    yield note("UCS is Dijkstra's algorithm stopped at the goal. It expands nodes in rings of increasing cost — in all directions, because it has no idea where Bucharest is. Adding that knowledge gives A* (see **Informed Search**).")
    yield table(
        ["", "BFS", "DFS", "UCS"],
        ["Complete?", "Yes (finite `b`)", "No in infinite spaces or with loops (tree search); yes for finite graph search", "Yes if every step cost ≥ `ε > 0`"],
        ["Optimal?", "Only if all step costs are equal", "No", "Yes"],
        ["Time", "`O(bᵈ)`", "`O(bᵐ)`", "`O(b^(1 + ⌊C*/ε⌋))`"],
        ["Space", "`O(bᵈ)` — keeps the whole frontier", "`O(bm)` — only the current path + siblings", "`O(b^(1 + ⌊C*/ε⌋))`"],
    )
    yield warn("BFS's real problem is **memory**, not time: at `b = 10`, depth 10 means ~10¹⁰ nodes in memory — terabytes. DFS uses linear memory but can wander down an infinite branch.")
    yield qa("When is BFS optimal?",
             "When every action has the same cost (or cost is a non-decreasing function of depth). Then the shallowest goal is also the cheapest. With varied step costs use UCS.")
    yield qa("Why must UCS test the goal on expansion rather than generation?",
             "When the goal is first generated it may be via an expensive edge (Fagaras → Bucharest, total 450) while a cheaper route (via Pitesti, 418) is still on the frontier. Waiting until the goal is popped guarantees it's the cheapest.")
    yield qa("Is Dijkstra's algorithm the same as UCS?",
             "Essentially yes. Dijkstra computes shortest paths from a source to all nodes in an explicit graph; UCS stops at the goal and works on implicit graphs generated on the fly.")


@topic(G, "iterative-deepening", "Depth-Limited, Iterative Deepening & Bidirectional Search", "stairs-down")
def _():
    yield lead("Iterative deepening combines DFS's tiny memory with BFS's completeness and optimality — and is the preferred uninformed method when the solution depth is unknown. Bidirectional search meets in the middle to cut `bᵈ` to `2·b^(d/2)`.")
    yield section("Depth-limited and iterative deepening DFS", "stairs")
    yield p("**Depth-limited search (DLS)** is DFS that treats nodes at depth `ℓ` as leaves — it can't loop forever, but misses goals deeper than `ℓ`. **Iterative deepening (IDDFS)** runs DLS with `ℓ = 0, 1, 2, …` until a goal is found.")
    yield code(ROMANIA + '''
        def dls(node, goal, limit, route, counter):
            counter[0] += 1                                    # count expansions
            if node == goal:
                return route
            if limit == 0:
                return None                                    # cutoff
            for nbr in graph[node]:
                if nbr not in route:                           # avoid cycles along the current path
                    found = dls(nbr, goal, limit - 1, route + [nbr], counter)
                    if found:
                        return found
            return None

        def iddfs(start, goal, max_depth=10):
            total = 0
            for limit in range(max_depth + 1):
                counter = [0]
                found = dls(start, goal, limit, [start], counter)
                total += counter[0]
                if found:
                    return found, limit, total

        print(dls("Arad", "Bucharest", 2, ["Arad"], [0]))     # None ← limit too small
        print(iddfs("Arad", "Bucharest"))                     # (['Arad', 'Sibiu', 'Fagaras', 'Bucharest'], 3, 23)
    ''')
    yield p("Re-generating the shallow levels looks wasteful, but in a tree most nodes are at the bottom level, so the overhead is small:")
    yield formula("N(IDS) = d·b + (d−1)·b² + … + 1·bᵈ        N(BFS) = b + b² + … + bᵈ")
    yield code('''
        b, d = 10, 5
        n_bfs = sum(b ** i for i in range(1, d + 1))
        n_ids = sum((d - i + 1) * b ** i for i in range(1, d + 1))
        print(n_bfs, n_ids, f"{n_ids / n_bfs - 1:.0%}")    # 111110 123450 11% ← only ~11% more nodes, with O(bd) memory
    ''')
    yield section("Bidirectional search", "arrows-left-right")
    yield p("Search forward from the start and backward from the goal at the same time; stop when the frontiers meet. Two searches of depth `d/2` generate `2·b^(d/2)` nodes — far fewer than `bᵈ` (for `b = 10, d = 6`: 2,000 vs 1,000,000). It needs actions that can be *reversed* and an explicit goal state.")
    yield code(ROMANIA + '''
        from collections import deque

        def bidirectional(start, goal):
            parents = {start: {start: None}, goal: {goal: None}}      # one search tree per direction
            frontiers = {start: deque([start]), goal: deque([goal])}
            while frontiers[start] and frontiers[goal]:
                for side, other in ((start, goal), (goal, start)):    # alternate one layer each
                    for _ in range(len(frontiers[side])):
                        node = frontiers[side].popleft()
                        for nbr in graph[node]:
                            if nbr not in parents[side]:
                                parents[side][nbr] = node
                                frontiers[side].append(nbr)
                            if nbr in parents[other]:                  # the two searches meet
                                left, right, n = [], [], nbr
                                while n: left.append(n); n = parents[start][n]
                                n = parents[goal][nbr]
                                while n: right.append(n); n = parents[goal][n]
                                return left[::-1] + right, nbr

        print(bidirectional("Arad", "Bucharest"))    # (['Arad', 'Sibiu', 'Fagaras', 'Bucharest'], 'Fagaras')
    ''')
    yield section("Comparing the uninformed strategies", "table")
    yield table(
        ["Criterion", "BFS", "UCS", "DFS", "Depth-limited", "Iterative deepening", "Bidirectional"],
        ["Complete?", "Yes¹", "Yes¹ ²", "No", "No (if `ℓ < d`)", "Yes¹", "Yes¹ ⁴"],
        ["Optimal?", "Yes³", "Yes", "No", "No", "Yes³", "Yes³ ⁴"],
        ["Time", "`O(bᵈ)`", "`O(b^(1+⌊C*/ε⌋))`", "`O(bᵐ)`", "`O(bˡ)`", "`O(bᵈ)`", "`O(b^(d/2))`"],
        ["Space", "`O(bᵈ)`", "`O(b^(1+⌊C*/ε⌋))`", "`O(bm)`", "`O(bℓ)`", "`O(bd)`", "`O(b^(d/2))`"],
    )
    yield p("¹ if `b` is finite. ² if every step cost ≥ `ε > 0`. ³ if all step costs are equal. ⁴ if both directions use BFS (or UCS).")
    yield note("Rule of thumb: **IDDFS** when the space is large and the solution depth unknown; **UCS** when step costs differ; **BFS** only when the space is small enough to fit in memory; **DFS** when memory is tight and any solution will do (or all solutions are deep and plentiful).")
    yield qa("Why is iterative deepening not as wasteful as it looks?",
             "With branching factor `b`, the bottom level holds about `(b−1)/b` of all nodes, so re-generating the upper levels adds only a constant factor (~11% for `b = 10`). In return you get BFS's completeness/optimality with DFS's `O(bd)` memory.")
    yield qa("What does bidirectional search need to work?",
             "An explicit goal state (or a small set of them) and the ability to compute predecessors — i.e. reversible actions. It also needs an efficient check for when the two frontiers intersect (a hash set).")


@topic(G, "informed-search", "Informed Search: Greedy & A*", "star")
def _():
    yield lead("Informed search uses a **heuristic** `h(n)` — an estimate of the cost from `n` to the goal — to expand promising nodes first. A* combines the cost so far with the estimate to go, and is optimal when the heuristic never overestimates.")
    yield table(
        ["Strategy", "Evaluation `f(n)`", "Behaviour"],
        ["Uniform-cost", "`g(n)`", "Cheapest-so-far — ignores the goal"],
        ["**Greedy best-first**", "`h(n)`", "Whatever *looks* closest to the goal — fast, not optimal"],
        ["**A***", "`g(n) + h(n)`", "Cheapest estimated *total* path through `n` — optimal with an admissible `h`"],
        ["Weighted A*", "`g(n) + w·h(n)`, `w > 1`", "Faster, cost at most `w ×` optimal"],
    )
    yield formula("f(n) = g(n) + h(n)      g = cost from start to n,   h = estimated cost from n to goal")
    yield p("For route finding, the straight-line distance (SLD) to Bucharest is a natural heuristic — a road can't be shorter than a straight line:")
    yield code(ROMANIA + '''
        import heapq

        SLD = {"Arad": 366, "Bucharest": 0, "Craiova": 160, "Drobeta": 242, "Eforie": 161, "Fagaras": 176,
               "Giurgiu": 77, "Hirsova": 151, "Iasi": 226, "Lugoj": 244, "Mehadia": 241, "Neamt": 234,
               "Oradea": 380, "Pitesti": 100, "Rimnicu": 193, "Sibiu": 253, "Timisoara": 329,
               "Urziceni": 80, "Vaslui": 199, "Zerind": 374}

        def best_first(start, goal, f):
            frontier = [(f(0, start), 0, start, [start])]          # (priority, g, city, route)
            best_g, expanded = {start: 0}, []
            while frontier:
                _, g, node, route = heapq.heappop(frontier)
                if node == goal:
                    return route, g, expanded
                if g > best_g[node]:
                    continue
                expanded.append(node)
                for nbr, km in graph[node].items():
                    g2 = g + km
                    if g2 < best_g.get(nbr, float("inf")):
                        best_g[nbr] = g2
                        heapq.heappush(frontier, (f(g2, nbr), g2, nbr, route + [nbr]))

        greedy = lambda g, city: SLD[city]              # f = h
        astar = lambda g, city: g + SLD[city]           # f = g + h

        route, cost, expanded = best_first("Arad", "Bucharest", greedy)
        print(route, cost)       # ['Arad', 'Sibiu', 'Fagaras', 'Bucharest'] 450
        print(expanded)          # ['Arad', 'Sibiu', 'Fagaras']
        route, cost, expanded = best_first("Arad", "Bucharest", astar)
        print(route, cost)       # ['Arad', 'Sibiu', 'Rimnicu', 'Pitesti', 'Bucharest'] 418
        print(expanded)          # ['Arad', 'Sibiu', 'Rimnicu', 'Fagaras', 'Pitesti']
    ''')
    yield p("Greedy heads for Fagaras because it is closest to Bucharest in a straight line, and ends up 32 km worse. A* expands Fagaras too, but when Bucharest appears with `f = 450` it first expands Pitesti (`f = 317 + 100 = 417`) and finds the 418 km route. UCS needed 12 expansions for the same answer; A* needed 5.")
    yield section("Why A* is optimal", "shield-check")
    yield define("Admissible heuristic", "never overestimates the true cost to reach the goal: `h(n) ≤ h*(n)` for every `n`. It is *optimistic*.")
    yield define("Consistent (monotone) heuristic", "for every node `n` and successor `n′` via action `a`: `h(n) ≤ c(n, a, n′) + h(n′)` — a triangle inequality. Along any path, `f` never decreases. Every consistent heuristic is admissible.")
    yield steps(
        ("Admissible h", "`f(n) = g(n) + h(n)` never overestimates the cost of the best solution through `n`."),
        ("Suboptimal goal G₂ on the frontier", "`f(G₂) = g(G₂) > C*` because `h(G₂) = 0`."),
        ("Some node n on the optimal path is also on the frontier", "`f(n) ≤ C* < f(G₂)`, so `n` is expanded before `G₂`."),
        ("Conclusion", "A* never pops a suboptimal goal before the optimal one. With graph search, consistency guarantees each state's first expansion is via its cheapest path."),
    )
    yield table(
        ["Property of A*", "Holds when"],
        ["Complete", "Finite branching and step costs ≥ `ε > 0`"],
        ["Optimal — tree search", "`h` admissible"],
        ["Optimal — graph search (no re-opening)", "`h` consistent"],
        ["Optimally efficient", "No other optimal algorithm using the same `h` expands fewer nodes (up to ties)"],
        ["Space", "Exponential — keeps every generated node; this is A*'s real bottleneck"],
    )
    yield cards(
        ("IDA*", "Iterative deepening on `f` instead of depth: each iteration's cutoff is the smallest `f` that exceeded the last one. Linear memory; good for puzzles with unit costs.", "stairs"),
        ("SMA* / memory-bounded", "Runs A* until memory is full, then drops the worst leaf and remembers its `f` in the parent.", "database"),
        ("Weighted A*", "`f = g + w·h` with `w > 1`: expands far fewer nodes, solution cost ≤ `w · C*`. Common in games and robotics.", "scale"),
        ("Greedy best-first", "`f = h`. Often very fast, but not optimal and (tree search) not complete — it can loop.", "run"),
        cols=2,
    )
    yield warn("An **inadmissible** heuristic (one that sometimes overestimates) can make A* skip the optimal path. And a heuristic that is admissible but *inconsistent* needs graph search that can re-open closed nodes — otherwise optimality is lost.")
    yield qa("Explain A* and when it is optimal.",
             "A* is best-first search on `f(n) = g(n) + h(n)`, the estimated cost of the cheapest solution through `n`. It is optimal if `h` is admissible (tree search) or consistent (graph search), and complete with positive step costs and finite branching.")
    yield qa("What happens to A* when h = 0? When h = h* exactly?",
             "`h = 0` gives uniform-cost search (still optimal, but uninformed). With the perfect heuristic `h = h*`, A* expands only nodes on an optimal path — straight to the goal.")
    yield qa("Why does greedy best-first search fail to be optimal?",
             "It ignores the cost already paid (`g`), so it follows whatever looks closest even when that route is expensive — Arad → Sibiu → Fagaras → Bucharest (450 km) instead of 418 km.")


@topic(G, "heuristics", "Designing Heuristics", "bulb")
def _():
    yield lead("A* is only as good as its heuristic. Good heuristics are admissible, as close to the true cost as possible, and cheap to compute — and the standard way to invent one is to **relax** the problem.")
    yield section("Two classic 8-puzzle heuristics", "grid-dots")
    yield table(
        ["Heuristic", "Definition", "Relaxed problem it solves exactly"],
        ["`h₁` — misplaced tiles", "Number of tiles not in their goal square", "A tile can jump *anywhere* in one move"],
        ["`h₂` — Manhattan distance", "Sum over tiles of |row − goal row| + |col − goal col|", "A tile can move to *any adjacent* square, even an occupied one"],
    )
    yield p("A relaxed problem has *more* actions, so its optimal cost can only be lower — that is why a heuristic derived from a relaxation is automatically admissible (and consistent).")
    yield code('''
        import heapq

        GOAL = (0, 1, 2, 3, 4, 5, 6, 7, 8)         # 0 = blank

        def h1(s):                                  # misplaced tiles (the blank doesn't count)
            return sum(1 for i, tile in enumerate(s) if tile and tile != i)

        def h2(s):                                  # Manhattan distance
            return sum(abs(i // 3 - t // 3) + abs(i % 3 - t % 3) for i, t in enumerate(s) if t)

        def neighbours(s):
            i = s.index(0)
            r, c = divmod(i, 3)
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if 0 <= r + dr < 3 and 0 <= c + dc < 3:
                    j = (r + dr) * 3 + c + dc
                    t = list(s)
                    t[i], t[j] = t[j], t[i]
                    yield tuple(t)

        def astar(start, h):
            frontier, best, expanded = [(h(start), 0, start)], {start: 0}, 0
            while frontier:
                f, g, s = heapq.heappop(frontier)
                if s == GOAL:
                    return g, expanded
                if g > best[s]:
                    continue
                expanded += 1
                for t in neighbours(s):
                    if g + 1 < best.get(t, 99):
                        best[t] = g + 1
                        heapq.heappush(frontier, (g + 1 + h(t), g + 1, t))

        start = (7, 2, 4,
                 5, 0, 6,
                 8, 3, 1)
        print(h1(start), h2(start))                 # 8 18 ← true cost is 26
        print(astar(start, lambda s: 0))            # (26, 162240) ← h = 0 is uniform-cost search
        print(astar(start, h1))                     # (26, 44988)
        print(astar(start, h2))                     # (26, 4085)
    ''')
    yield p("All three find the optimal 26-move solution; Manhattan distance does it with roughly **40× fewer** expansions than no heuristic.")
    yield section("Dominance and the effective branching factor", "trending-down")
    yield define("Dominance", "if `h₂(n) ≥ h₁(n)` for every `n` and both are admissible, `h₂` **dominates** `h₁` and A* with `h₂` never expands more nodes. Larger is better — as long as it stays admissible.")
    yield p("To compare heuristics independently of problem size, compute the **effective branching factor** `b*`: the branching factor a uniform tree of depth `d` would need to contain the `N` nodes A* expanded. Close to 1 is ideal.")
    yield formula("N + 1 = 1 + b* + (b*)² + … + (b*)ᵈ")
    yield code('''
        def effective_branching(n_expanded, depth):
            lo, hi = 1.0, 10.0
            for _ in range(60):                        # bisection
                b = (lo + hi) / 2
                total = sum(b ** i for i in range(depth + 1))
                lo, hi = (b, hi) if total < n_expanded + 1 else (lo, b)
            return round(b, 2)

        print(effective_branching(162240, 26))     # 1.52 ← no heuristic
        print(effective_branching(44988, 26))      # 1.44 ← misplaced tiles
        print(effective_branching(4085, 26))       # 1.3 ← Manhattan distance
    ''')
    yield section("Recipes for heuristics", "chef-hat")
    yield cards(
        ("Relax the problem", "Remove constraints until the problem is easy to solve exactly: straight-line distance (ignore roads), Manhattan distance (ignore other tiles), ignore-preconditions in planning.", "wand"),
        ("Max of admissible heuristics", "`h(n) = max(h₁(n), …, hₖ(n))` is admissible and dominates each component — use it when no single one is best everywhere.", "arrow-bar-up"),
        ("Pattern databases", "Precompute exact costs for a sub-problem (e.g. tiles 1–4 only) for every configuration and look them up. Disjoint patterns can be *added*. Solves the 15-puzzle and Rubik's cube quickly.", "database"),
        ("Learn a heuristic", "Train a model to predict cost-to-go from features of a state (AlphaGo's value network is a learned evaluation). Fast, but no admissibility guarantee.", "school"),
        cols=2,
    )
    yield table(
        ["Domain", "Admissible heuristic"],
        ["Grid, 4-way moves", "Manhattan distance `|dx| + |dy|`"],
        ["Grid, 8-way moves (diagonal cost √2)", "Octile distance `max(dx, dy) + (√2 − 1)·min(dx, dy)`"],
        ["Any-angle / road maps", "Euclidean (straight-line) distance"],
        ["Travelling salesperson", "Cost of a minimum spanning tree of unvisited cities"],
    )
    yield warn("Manhattan distance is **not** admissible on an 8-connected grid — one diagonal step (cost √2 ≈ 1.41) covers Manhattan distance 2, so it overestimates.")
    yield qa("What makes a heuristic admissible? Give one for the 8-puzzle.",
             "It never overestimates the true cost to the goal. Manhattan distance: every tile must move at least its row and column offset, one square per move, so the sum can't exceed the real number of moves.")
    yield qa("Admissible vs consistent?",
             "Admissible: `h(n) ≤ h*(n)`. Consistent: `h(n) ≤ c(n, n′) + h(n′)` for every edge — a stronger condition that implies admissibility and guarantees `f` is non-decreasing along paths, so graph-search A* never needs to re-open nodes.")
    yield qa("If h₂ dominates h₁, is h₂ always better?",
             "It never expands more nodes, but it may cost more to *compute* per node. The best heuristic balances accuracy against evaluation time.")
