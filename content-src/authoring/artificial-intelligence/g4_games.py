from kit import *

G = "Adversarial Search & Games"


@topic(G, "minimax", "Games & Minimax", "chess")
def _():
    yield lead("In a game the agent faces an **opponent** who is trying to make it lose. Minimax plans for the worst case: MAX picks the move with the highest value assuming MIN always answers with the move that is worst for MAX.")
    yield section("Kinds of games", "category")
    yield table(
        ["", "Deterministic", "Chance"],
        ["**Perfect information**", "Chess, Go, checkers, tic-tac-toe, connect-four", "Backgammon, Monopoly"],
        ["**Imperfect information**", "Battleship, Stratego", "Poker, bridge, Scrabble"],
    )
    yield p("Classical game search targets **two-player, turn-taking, zero-sum, perfect-information** games — one player's gain is exactly the other's loss.")
    yield section("A game as a search problem", "list-details")
    yield table(
        ["Element", "Meaning"],
        ["`S₀`", "Initial state (starting position)"],
        ["`ToMove(s)`", "Whose turn it is (MAX or MIN)"],
        ["`Actions(s)` / `Result(s, a)`", "Legal moves and the position they lead to"],
        ["`IsTerminal(s)`", "Is the game over?"],
        ["`Utility(s, p)`", "Final payoff for player `p`: e.g. +1 win, 0 draw, −1 loss"],
    )
    yield formula("MINIMAX(s) = Utility(s) if terminal;   max over a of MINIMAX(Result(s, a)) if MAX to move;   min over a … if MIN to move")
    yield section("Minimax on a two-ply tree", "binary-tree")
    yield p("The standard textbook tree: MAX moves at the root (A), MIN replies at B, C and D, and the leaves are utilities for MAX.")
    yield code('''
        TREE = {"A": ["B", "C", "D"],                    # MAX node
                "B": [3, 12, 8], "C": [2, 4, 6], "D": [14, 5, 2]}   # MIN nodes → leaf utilities

        def minimax(node, maximizing):
            if isinstance(node, int):                     # leaf: utility
                return node
            values = [minimax(child, not maximizing) for child in TREE[node]]
            return max(values) if maximizing else min(values)

        print([minimax(n, False) for n in TREE["A"]])     # [3, 2, 2] ← MIN's replies at B, C, D
        print(minimax("A", True))                         # 3 ← MAX moves to B
    ''')
    yield section("Perfect tic-tac-toe", "grid-3x3")
    yield code('''
        from functools import lru_cache

        LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

        def winner(b):
            for i, j, k in LINES:
                if b[i] != "." and b[i] == b[j] == b[k]:
                    return b[i]
            return None

        @lru_cache(maxsize=None)                  # the same position is reached by many move orders
        def value(board, player):                 # +1 = X wins, 0 = draw, −1 = O wins (perfect play)
            w = winner(board)
            if w:
                return 1 if w == "X" else -1
            if "." not in board:
                return 0
            nxt = "O" if player == "X" else "X"
            vals = [value(board[:i] + player + board[i + 1:], nxt) for i in range(9) if board[i] == "."]
            return max(vals) if player == "X" else min(vals)

        def best_move(board, player):
            nxt = "O" if player == "X" else "X"
            moves = [i for i in range(9) if board[i] == "."]
            pick = max if player == "X" else min
            return pick(moves, key=lambda i: value(board[:i] + player + board[i + 1:], nxt))

        print(value("." * 9, "X"))                # 0 ← perfect play from the empty board is a draw
        print(value.cache_info().currsize)        # 5478 ← distinct positions evaluated
        board = "XX." \\
                "OO." \\
                "..."
        print(best_move(board, "X"))              # 2 ← win at once (square 2)
        print(best_move("XO..O...X", "X"))        # 7 ← must block O's middle column
    ''')
    yield section("Cost of minimax", "clock")
    yield p("Minimax is a complete depth-first exploration of the game tree: time `O(bᵐ)`, space `O(bm)`. Tic-tac-toe has fewer than 9! = 362,880 move sequences, but chess has `b ≈ 35` and games of ~80 plies — about 10¹²³ positions in the tree. Real programs therefore **prune** (alpha-beta) and **cut off** the search at a fixed depth with an evaluation function.")
    yield note("Minimax is optimal against an optimal opponent. Against a weak opponent another strategy may win more — but minimax never does worse than its computed value.")
    yield qa("Explain minimax.",
             "Recursively evaluate the game tree: terminal states get their utility, MAX nodes take the maximum of their children and MIN nodes the minimum. The root's best child is the move that guarantees the best outcome against an opponent who also plays optimally.")
    yield qa("What is the time complexity of minimax?",
             "`O(bᵐ)` time and `O(bm)` space (depth-first), where `b` is the branching factor and `m` the maximum depth — infeasible for chess or Go without pruning and depth cut-offs.")


@topic(G, "alpha-beta-pruning", "Alpha-Beta Pruning", "cut")
def _():
    yield lead("Alpha-beta pruning returns exactly the minimax value while skipping branches that cannot affect the decision. With good move ordering it searches roughly **twice as deep** in the same time.")
    yield define("α (alpha)", "the best value MAX can already guarantee somewhere along the path to the root — a lower bound.")
    yield define("β (beta)", "the best (lowest) value MIN can already guarantee along the path — an upper bound.")
    yield p("While searching, if a node's value is proven to be outside `[α, β]`, the player above will never let the game reach it, so its remaining children are **pruned**: whenever `α ≥ β`.")
    yield code('''
        TREE = {"A": ["B", "C", "D"],
                "B": [3, 12, 8], "C": [2, 4, 6], "D": [14, 5, 2]}
        visited = []

        def alphabeta(node, alpha, beta, maximizing):
            if isinstance(node, int):
                visited.append(node)
                return node
            if maximizing:
                value = float("-inf")
                for child in TREE[node]:
                    value = max(value, alphabeta(child, alpha, beta, False))
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break                              # β cut-off: MIN above won't allow this
                return value
            value = float("inf")
            for child in TREE[node]:
                value = min(value, alphabeta(child, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta:
                    break                                  # α cut-off: MAX above already has better
            return value

        print(alphabeta("A", float("-inf"), float("inf"), True))   # 3 ← same answer as minimax
        print(visited, f"{len(visited)} of 9 leaves")               # [3, 12, 8, 2, 14, 5, 2] 7 of 9 leaves
    ''')
    yield steps(
        ("Explore B", "MIN sees 3, 12, 8 → B = 3. At the root α = 3: MAX is guaranteed at least 3."),
        ("First leaf of C is 2", "MIN at C can force ≤ 2, which is worse for MAX than the 3 it already has — so C's other leaves (4, 6) are **pruned**."),
        ("Explore D", "14 → 5 → 2: D's value is only bounded after the last leaf, so nothing is pruned there."),
        ("Result", "Root = max(3, ≤2, 2) = 3 — identical to minimax, with 7 leaves instead of 9."),
    )
    yield section("Move ordering is everything", "sort-descending")
    yield p("Pruning depends on examining the **best moves first**. On a random tree of depth 4 with 4 moves per node (256 leaves):")
    yield code('''
        import random

        random.seed(3)
        B, DEPTH = 4, 4
        def build(depth):
            return random.randint(0, 99) if depth == 0 else [build(depth - 1) for _ in range(B)]
        tree = build(DEPTH)

        def minimax(node, maximizing):
            if isinstance(node, int):
                return node
            vals = [minimax(c, not maximizing) for c in node]
            return max(vals) if maximizing else min(vals)

        def alphabeta(node, alpha, beta, maximizing, order, count):
            if isinstance(node, int):
                count[0] += 1
                return node
            best = float("-inf") if maximizing else float("inf")
            for child in order(node, maximizing):
                v = alphabeta(child, alpha, beta, not maximizing, order, count)
                if maximizing:
                    best, alpha = max(best, v), max(alpha, v)
                else:
                    best, beta = min(best, v), min(beta, v)
                if alpha >= beta:
                    break
            return best

        as_given = lambda node, maximizing: node
        worst_first = lambda node, maximizing: sorted(node, key=lambda c: minimax(c, not maximizing), reverse=not maximizing)
        best_first = lambda node, maximizing: sorted(node, key=lambda c: minimax(c, not maximizing), reverse=maximizing)

        counts = {}
        for name, order in [("worst-first", worst_first), ("as generated", as_given), ("best-first", best_first)]:
            count = [0]
            alphabeta(tree, float("-inf"), float("inf"), True, order, count)
            counts[name] = count[0]

        print(minimax(tree, True), B ** DEPTH)     # 47 256 ← value, and leaves plain minimax looks at
        print(counts["worst-first"])               # 238
        print(counts["as generated"])              # 61
        print(counts["best-first"])                # 31 ← 2·b^(d/2) − 1 = 31: the theoretical minimum
    ''')
    yield table(
        ["Move ordering", "Nodes examined", "Effective branching factor", "Depth reachable in the same time"],
        ["Worst (best moves last)", "`O(bᵐ)` — no pruning", "`b`", "`d`"],
        ["Random", "≈ `O(b^(3m/4))`", "≈ `b^(3/4)`", "≈ `4d/3`"],
        ["Perfect (best moves first)", "`O(b^(m/2))`", "`√b` (chess: 35 → ~6)", "`2d`"],
    )
    yield cards(
        ("Iterative deepening", "Search depth 1, 2, 3… and try the previous iteration's best move first — the deeper search inherits a near-perfect ordering.", "stairs"),
        ("Killer moves", "Moves that caused a cut-off at the same depth elsewhere are likely to cause one here — try them early.", "sword"),
        ("History heuristic", "Keep a score of moves that caused cut-offs anywhere; order by it.", "history"),
        ("Transposition table", "Hash positions already evaluated (reached by different move orders) and reuse their values and best moves.", "table"),
        cols=2,
    )
    yield warn("Alpha-beta never changes the minimax value at the root — if your pruned search returns a different move value than plain minimax, there's a bug (usually α/β passed or updated at the wrong level).")
    yield qa("What is alpha-beta pruning?",
             "An optimisation of minimax that tracks α (MAX's best guaranteed value) and β (MIN's best guaranteed value) along the current path. When `α ≥ β` at a node, the remaining children can't influence the decision and are skipped. The result equals minimax.")
    yield qa("What is the best-case complexity of alpha-beta and what does it require?",
             "`O(b^(m/2))` — the square root of minimax's `O(bᵐ)`, so it can search about twice as deep. It requires perfect move ordering: the best move examined first at every node.")


@topic(G, "game-search-beyond-minimax", "Evaluation Functions, Expectimax & MCTS", "dice")
def _():
    yield lead("Real games are too big to search to the end. Engines stop at a depth limit and **estimate** the position; games with dice need **expectation** instead of minimum; and Monte Carlo tree search replaces hand-made evaluation with random playouts.")
    yield section("Depth cut-off and evaluation functions", "scale")
    yield p("Replace `IsTerminal` with a **cut-off test** (depth limit, or time) and `Utility` with an **evaluation function** — an estimate of the expected utility of a position. Most classical engines use a weighted linear sum of features:")
    yield formula("Eval(s) = w₁·f₁(s) + w₂·f₂(s) + … + wₙ·fₙ(s)")
    yield code('''
        VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}    # classic material weights

        def material(pieces):                     # uppercase = White (MAX), lowercase = Black (MIN)
            return sum(VALUES[p.upper()] * (1 if p.isupper() else -1) for p in pieces)

        print(material("KQRRBNPPPPP" + "kqrbbnnpppppp"))   # -2 ← White: rook vs two minor pieces (−1) and a pawn down (−1)
    ''')
    yield table(
        ["Problem", "What goes wrong", "Remedy"],
        ["**Horizon effect**", "A delaying move pushes an unavoidable loss beyond the depth limit, so the engine thinks it is avoided", "Singular extensions — search forcing moves deeper"],
        ["**Non-quiescent positions**", "Cutting off in the middle of a capture sequence gives a wildly wrong estimate", "**Quiescence search** — keep searching captures until the position is quiet"],
        ["Weights are hand-tuned", "The evaluation encodes human biases and misses deep strategy", "Learn the evaluation (TD-Gammon, AlphaZero value networks)"],
    )
    yield section("Expectimax — games of chance", "dice-5")
    yield p("In backgammon a dice roll sits between the players' moves. Add **chance nodes** whose value is the probability-weighted average of their children:")
    yield formula("EXPECTIMINIMAX(s) = Σ over outcomes r of P(r) · EXPECTIMINIMAX(Result(s, r))    at chance nodes")
    yield code('''
        # MAX chooses a gamble; each gamble is a chance node: [(probability, payoff), ...]
        options = {
            "risky": [(0.5, 10), (0.5, 0)],
            "safe":  [(1.0, 4)],
        }
        worst_case = {a: min(v for _, v in outs) for a, outs in options.items()}    # minimax-style: assume the worst
        expected = {a: sum(p * v for p, v in outs) for a, outs in options.items()}  # expectimax

        print(worst_case, max(worst_case, key=worst_case.get))    # {'risky': 0, 'safe': 4} safe
        print(expected, max(expected, key=expected.get))          # {'risky': 5.0, 'safe': 4.0} risky
    ''')
    yield warn("With chance nodes the *scale* of the evaluation matters, not just the ranking: only a positive linear transformation of the true expected payoff preserves the best move. Minimax is indifferent to any order-preserving transformation.")
    yield section("Monte Carlo tree search (MCTS)", "binary-tree-2")
    yield p("MCTS needs no evaluation function: it estimates a position's value by playing many (quick, often random) games to the end, and grows a search tree focused on the most promising moves. Each iteration has four steps:")
    yield flow("1 · Selection (follow UCB1 down the tree)", "2 · Expansion (add one new child)", "3 · Simulation (random playout to the end)", "4 · Backpropagation (update wins/visits up the path)")
    yield formula("UCB1(n) = W(n)/N(n) + C · √( ln N(parent) / N(n) )      exploitation + exploration,  C ≈ √2")
    yield p("Demo on **Nim**: 10 sticks, each turn take 1–3, whoever takes the last stick wins. The winning strategy is to leave the opponent a multiple of 4 — so from 10 the right move is to take 2. MCTS discovers this from random playouts alone:")
    yield code('''
        import math
        import random

        class Node:
            def __init__(self, sticks, parent=None, move=None):
                self.sticks, self.parent, self.move = sticks, parent, move
                self.children, self.wins, self.visits = [], 0, 0
                self.untried = [m for m in (1, 2, 3) if m <= sticks]

        def ucb1(n, c=1.4):
            return n.wins / n.visits + c * math.sqrt(math.log(n.parent.visits) / n.visits)

        def playout(sticks):                      # random game; True if the player to move wins
            to_move_wins = False
            while sticks:
                sticks -= random.randint(1, min(3, sticks))
                to_move_wins = not to_move_wins   # whoever just moved flips the flag
            return to_move_wins

        def mcts(sticks, iterations=2000):
            root = Node(sticks)
            for _ in range(iterations):
                node = root
                while not node.untried and node.children:             # 1. selection
                    node = max(node.children, key=ucb1)
                if node.untried:                                      # 2. expansion
                    m = node.untried.pop()
                    node.children.append(Node(node.sticks - m, node, m))
                    node = node.children[-1]
                mover_won = not playout(node.sticks)                 # 3. simulation: opponent moves next
                while node:                                           # 4. backpropagation
                    node.visits += 1
                    node.wins += mover_won                            # wins for the player who moved into node
                    mover_won = not mover_won
                    node = node.parent
            best = max(root.children, key=lambda n: n.visits)
            return best.move, {n.move: n.visits for n in sorted(root.children, key=lambda n: n.move)}

        random.seed(0)
        print(mcts(10))      # (2, {1: 104, 2: 1854, 3: 42}) ← take 2, leaving 8
        print(mcts(7)[0])    # 3 ← take 3, leaving 4
    ''')
    yield table(
        ["", "Alpha-beta + evaluation", "MCTS"],
        ["Needs", "A good hand-crafted (or learned) evaluation function", "Only the rules (to simulate) — any-time"],
        ["Good for", "Tactical games with moderate `b` (chess, checkers)", "Huge `b`, hard-to-evaluate positions (Go: `b ≈ 250`)"],
        ["Search shape", "Uniform to a fixed depth", "Asymmetric — deep on promising lines"],
        ["Famous use", "Deep Blue (1997), Stockfish", "AlphaGo / AlphaZero (MCTS + policy and value networks)"],
    )
    yield note("AlphaZero replaced random playouts with a **value network** and biased selection with a **policy network**, both trained by self-play reinforcement learning — search and learning working together (see **Reinforcement Learning** and the **Deep Learning** notes).")
    yield qa("What is the horizon effect?",
             "A depth-limited search can't see consequences beyond its cut-off, so an engine may play delaying moves that merely push an inevitable loss past the horizon. Quiescence search and search extensions reduce it.")
    yield qa("When would you use expectimax instead of minimax?",
             "When outcomes involve chance (dice, card draws) or the opponent is not adversarial but random/suboptimal. Chance nodes take the probability-weighted average of their children instead of the minimum.")
    yield qa("Explain the four phases of MCTS.",
             "Selection: descend the tree choosing children by UCB1 (balancing win rate and uncertainty). Expansion: add a new child node. Simulation: play out the game from there with a default (often random) policy. Backpropagation: update visit and win counts along the path. The move with the most visits at the root is played.")
