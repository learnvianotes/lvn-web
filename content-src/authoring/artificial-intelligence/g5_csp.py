from kit import *

G = "Constraint Satisfaction"

AUSTRALIA = '''
        NEIGHBOURS = {"WA": ["NT", "SA"], "NT": ["WA", "SA", "Q"], "SA": ["WA", "NT", "Q", "NSW", "V"],
                      "Q": ["NT", "SA", "NSW"], "NSW": ["Q", "SA", "V"], "V": ["SA", "NSW"], "T": []}
        COLOURS = ["red", "green", "blue"]
'''


@topic(G, "csp-backtracking", "CSPs & Backtracking Search", "puzzle")
def _():
    yield lead("A constraint satisfaction problem (CSP) describes a state as **variables with domains** and the goal as a set of **constraints**. That factored structure lets one general-purpose solver handle map colouring, Sudoku, scheduling and timetabling — and prune huge parts of the search space.")
    yield define("CSP", "a triple **(X, D, C)**: variables `X₁…Xₙ`, a domain `Dᵢ` of allowed values for each, and constraints `C` that restrict which combinations of values are allowed. A **solution** is a *complete* and *consistent* assignment — every variable has a value and no constraint is violated.")
    yield section("Example: colouring the map of Australia", "map")
    yield table(
        ["Part", "Map colouring"],
        ["Variables", "WA, NT, SA, Q, NSW, V, T (the seven states and territories)"],
        ["Domains", "{red, green, blue} for each"],
        ["Constraints", "Neighbouring regions differ: WA ≠ NT, WA ≠ SA, NT ≠ SA, NT ≠ Q, SA ≠ Q, SA ≠ NSW, SA ≠ V, Q ≠ NSW, NSW ≠ V"],
    )
    yield p("Binary constraints form a **constraint graph**: nodes are variables, edges connect variables that share a constraint. Tasmania (T) has no edges — an independent sub-problem.")
    yield section("Kinds of constraints and problems", "category")
    yield table(
        ["Kind", "Example"],
        ["Unary (one variable)", "SA ≠ green"],
        ["Binary (two variables)", "WA ≠ NT"],
        ["Global / higher-order", "`Alldiff(F, T, U, W, R, O)` in cryptarithmetic; each Sudoku row/column/box"],
        ["Preference (soft)", "“Prof. X prefers mornings” → a **constraint optimisation** problem"],
    )
    yield chips("Sudoku: 81 variables, domain 1–9, 27 Alldiff constraints", "N-queens", "exam timetabling", "job-shop scheduling", "SEND + MORE = MONEY", "circuit layout", "register allocation (graph colouring)")
    yield section("Backtracking search", "arrow-back-up")
    yield p("Backtracking is depth-first search that assigns **one variable per level**, checks constraints immediately and undoes the last choice when no value fits. Because assignment order doesn't matter (commutativity), it explores `dⁿ` leaves instead of the `n!·dⁿ` a naive search would.")
    yield code(AUSTRALIA + '''
        def consistent(var, colour, assignment):
            return all(assignment.get(n) != colour for n in NEIGHBOURS[var])

        def backtrack(assignment, stats):
            if len(assignment) == len(NEIGHBOURS):
                return assignment                                   # complete and consistent
            var = next(v for v in NEIGHBOURS if v not in assignment)  # first unassigned variable
            for colour in COLOURS:
                stats["tried"] += 1
                if consistent(var, colour, assignment):
                    assignment[var] = colour
                    if backtrack(assignment, stats):
                        return assignment
                    del assignment[var]                             # undo and try the next value
            return None                                             # no value works → backtrack

        stats = {"tried": 0}
        print(backtrack({}, stats))     # {'WA': 'red', 'NT': 'green', 'SA': 'blue', 'Q': 'red', 'NSW': 'green', 'V': 'red', 'T': 'red'}
        print(stats)                    # {'tried': 11}
    ''')
    yield section("Counting every solution: 8-queens", "chess-queen")
    yield code('''
        def queens(n):
            solutions, nodes = [], 0
            def place(rows):                          # rows[c] = row of the queen in column c
                nonlocal nodes
                nodes += 1
                if len(rows) == n:
                    solutions.append(rows)
                    return
                c = len(rows)
                for r in range(n):
                    if all(r != r2 and abs(r - r2) != c - c2 for c2, r2 in enumerate(rows)):
                        place(rows + [r])
            place([])
            return solutions, nodes

        solutions, nodes = queens(8)
        print(len(solutions), nodes)     # 92 2057 ← 92 solutions; 2,057 consistent partial boards visited (incl. the empty one)
        print(solutions[0])              # [0, 4, 7, 5, 2, 6, 1, 3]
    ''')
    yield note("Plain backtracking already beats generate-and-test (8⁸ ≈ 16.8 million full boards) by checking constraints on *partial* assignments. The next topic makes it smarter: choose variables and values wisely, and propagate constraints ahead.")
    yield qa("What is a CSP? Give an example.",
             "A problem defined by variables, domains and constraints, solved by finding an assignment that satisfies all constraints. Examples: map colouring, Sudoku, N-queens, timetabling.")
    yield qa("Why is backtracking better than plain DFS over assignments?",
             "It fixes one variable per tree level (assignments commute) and checks constraints as soon as a variable is assigned, abandoning a partial assignment the moment it violates a constraint instead of completing it first.")


@topic(G, "csp-heuristics-inference", "CSP Heuristics, Forward Checking & AC-3", "filter")
def _():
    yield lead("Three questions make backtracking fast: **which variable** next, **which value** first, and **what can we infer** after each assignment. Good answers turn exponential searches into near-linear ones.")
    yield table(
        ["Heuristic", "Rule", "Intuition"],
        ["**MRV** — minimum remaining values", "Pick the variable with the fewest legal values left", "*Fail first*: tackle the most constrained variable before it becomes impossible"],
        ["**Degree heuristic**", "Tie-break by the variable involved in the most constraints with unassigned variables", "Reduces future branching (SA first in Australia)"],
        ["**LCV** — least constraining value", "Try the value that rules out the fewest choices for neighbours", "*Fail last*: leave maximum flexibility — we only need one solution"],
    )
    yield section("Inference: forward checking and arc consistency", "filter")
    yield cards(
        ("Forward checking", "After assigning `X = v`, delete `v`-inconsistent values from the domains of `X`'s unassigned neighbours. If a domain becomes empty, backtrack immediately.", "arrow-forward"),
        ("Arc consistency", "Arc `X → Y` is consistent if every value of `X` has *some* supporting value in `Y`. AC-3 enforces this for all arcs, propagating deletions until nothing changes.", "arrows-right-left"),
        ("MAC", "*Maintaining arc consistency*: run AC-3 after every assignment during backtracking — stronger than forward checking.", "refresh"),
        cols=3,
    )
    yield code('''
        def solve(n, mrv=False, forward_check=False):
            nodes = 0
            def backtrack(assign, domains):
                nonlocal nodes
                if len(assign) == n:
                    return dict(assign)
                free = [c for c in range(n) if c not in assign]
                var = min(free, key=lambda c: len(domains[c])) if mrv else free[0]
                for row in sorted(domains[var]):
                    if any(row == r or abs(row - r) == abs(var - c) for c, r in assign.items()):
                        continue
                    nodes += 1
                    assign[var] = row
                    new = domains
                    if forward_check:              # prune neighbours' domains; empty domain → dead end
                        new = {c: d if c in assign else {x for x in d if x != row and abs(x - row) != abs(c - var)}
                               for c, d in domains.items()}
                    if all(new[c] for c in new if c not in assign) and (res := backtrack(assign, new)):
                        return res
                    del assign[var]
                return None
            backtrack({}, {c: set(range(n)) for c in range(n)})
            return nodes

        print(solve(16))                                  # 10052 ← plain backtracking
        print(solve(16, forward_check=True))              # 7560
        print(solve(16, mrv=True, forward_check=True))    # 44 ← MRV + forward checking
    ''')
    yield section("AC-3", "arrows-right-left")
    yield steps(
        ("Queue every arc", "For each binary constraint between X and Y add both arcs `(X, Y)` and `(Y, X)`."),
        ("Revise", "Pop an arc `(X, Y)`; delete each value of `X` that has no compatible value in `Y`'s domain."),
        ("Propagate", "If `X`'s domain shrank, re-queue every arc `(Z, X)` for neighbours `Z ≠ Y`."),
        ("Stop", "When the queue is empty (arc-consistent) — or a domain becomes empty (no solution)."),
    )
    yield code('''
        from collections import deque

        def ac3(domains, constraints):
            """constraints: {(X, Y): predicate(x, y)} — both directions must be listed."""
            queue = deque(constraints)
            while queue:
                x, y = queue.popleft()
                ok = constraints[(x, y)]
                removed = {vx for vx in domains[x] if not any(ok(vx, vy) for vy in domains[y])}
                if removed:
                    domains[x] -= removed
                    if not domains[x]:
                        return False                                  # inconsistency detected
                    queue.extend((z, w) for (z, w) in constraints if w == x and z != y)
            return True

        # X < Y < Z with values 1..3: propagation alone solves it
        doms = {v: {1, 2, 3} for v in "XYZ"}
        lt, gt = (lambda a, b: a < b), (lambda a, b: a > b)
        print(ac3(doms, {("X", "Y"): lt, ("Y", "X"): gt, ("Y", "Z"): lt, ("Z", "Y"): gt}), doms)   # True {'X': {1}, 'Y': {2}, 'Z': {3}}

        # Australia after WA = red, Q = green: forward checking leaves NT = SA = {blue} and doesn't notice…
        edges = [("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"), ("SA", "Q"), ("SA", "NSW"),
                 ("SA", "V"), ("Q", "NSW"), ("NSW", "V")]
        ne = lambda a, b: a != b
        cons = {**{(a, b): ne for a, b in edges}, **{(b, a): ne for a, b in edges}}
        doms = {v: {"red", "green", "blue"} for v in ["WA", "NT", "SA", "Q", "NSW", "V", "T"]}
        doms["WA"], doms["Q"] = {"red"}, {"green"}
        print(ac3(doms, cons))       # False ← …AC-3 proves there is no solution with this partial assignment
    ''')
    yield p("AC-3 runs in `O(c·d³)` for `c` arcs and domain size `d`. Arc consistency alone doesn't always find a solution (map colouring with 2 colours on a triangle stays arc-consistent), but combined with search it removes most dead ends early.")
    yield section("Local search for CSPs: min-conflicts", "arrows-shuffle")
    yield p("Start from a complete (inconsistent) assignment; repeatedly pick a conflicted variable and give it the value with the **fewest conflicts**. Remarkably effective on large, loosely constrained problems — started from a greedy initial assignment it solves the million-queens problem in about 50 steps on average, and it is used for real-time rescheduling.")
    yield code('''
        import random

        def min_conflicts(n, max_steps=1000):
            rows = [random.randrange(n) for _ in range(n)]
            def conflicts(c, r):
                return sum(1 for c2 in range(n) if c2 != c and (rows[c2] == r or abs(rows[c2] - r) == abs(c2 - c)))
            for step in range(max_steps):
                bad = [c for c in range(n) if conflicts(c, rows[c])]
                if not bad:
                    return rows, step
                c = random.choice(bad)
                rows[c] = min(range(n), key=lambda r: (conflicts(c, r), random.random()))   # random tie-break
            return None, max_steps

        random.seed(0)
        rows, steps = min_conflicts(40)
        print(steps)     # 152 ← steps to solve 40-queens from a random start
    ''')
    yield section("Exploiting problem structure", "binary-tree-2")
    yield table(
        ["Structure", "Technique", "Cost"],
        ["Independent sub-problems (Tasmania)", "Solve connected components separately", "`O(dᶜ · n/c)` instead of `O(dⁿ)`"],
        ["Tree-structured constraint graph", "Order topologically, make arcs consistent backwards, assign forwards", "`O(n·d²)` — linear in `n`"],
        ["Nearly a tree", "**Cutset conditioning**: assign a small cycle cutset, solve the remaining tree", "`O(dᶜ · (n − c)·d²)`"],
        ["Symmetric values", "Symmetry-breaking constraints (e.g. NT < SA < WA)", "Removes equivalent solutions"],
    )
    yield qa("Explain MRV and LCV — why is one 'fail first' and the other 'fail last'?",
             "MRV picks the variable with the fewest legal values: every variable must be assigned eventually, so discovering a dead end early saves work. LCV orders the chosen variable's values so the one that leaves neighbours the most options comes first: we only need one solution, so try the value most likely to succeed.")
    yield qa("Forward checking vs arc consistency?",
             "Forward checking only prunes the domains of variables directly connected to the one just assigned. Arc consistency (AC-3) propagates further: every arc is revised until stable, catching conflicts between two *unassigned* variables — like NT and SA both reduced to {blue}.")
    yield qa("What is the time complexity of AC-3?",
             "`O(c·d³)`: each of the `c` arcs can be re-queued at most `d` times (once per deleted value), and revising an arc costs `O(d²)`.")
