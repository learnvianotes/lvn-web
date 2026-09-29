from kit import *

G = "Local Search & Optimization"

QUEENS = '''
        def conflicts(state):                     # number of attacking pairs; 0 = solved
            n = len(state)
            return sum(1 for i in range(n) for j in range(i + 1, n)
                       if state[i] == state[j] or abs(state[i] - state[j]) == j - i)
'''


@topic(G, "hill-climbing", "Hill Climbing", "trending-up")
def _():
    yield lead("When only the final state matters — not the path — local search keeps **one current state** and repeatedly moves to a better neighbour. It uses almost no memory and handles huge or continuous spaces, but it can get stuck.")
    yield define("Local search", "an optimisation method that works on **complete-state** formulations (every state is a full candidate solution) and improves it by small changes. Used for n-queens, scheduling, circuit layout, travelling salesperson, and — in continuous form — training neural networks by gradient descent.")
    yield p("The **objective function** (or cost) defines a **state-space landscape**. Hill climbing moves uphill (maximising) or downhill (minimising cost) until no neighbour is better.")
    yield section("Steepest-ascent hill climbing on 8-queens", "chess-queen")
    yield p("State: one queen per column, `state[c]` = its row. Neighbours: move one queen within its column (8 × 7 = 56 neighbours). Cost `h`: pairs of queens attacking each other.")
    yield code(QUEENS + '''
        import random

        def neighbours(state):
            for col in range(len(state)):
                for row in range(len(state)):
                    if row != state[col]:
                        yield state[:col] + (row,) + state[col + 1:]

        def hill_climb(state):
            steps = 0
            while True:
                best = min(neighbours(state), key=conflicts)
                if conflicts(best) >= conflicts(state):
                    return state, steps                 # no neighbour is better: a peak (or plateau)
                state, steps = best, steps + 1

        random.seed(1)
        start = tuple(random.randrange(8) for _ in range(8))
        end, steps = hill_climb(start)
        print(start, conflicts(start))             # (2, 1, 4, 1, 7, 7, 7, 6) 9
        print(end, conflicts(end), steps)          # (5, 2, 4, 1, 7, 0, 3, 6) 1 4 ← stuck: a local minimum

        starts = [tuple(random.randrange(8) for _ in range(8)) for _ in range(200)]
        solved = sum(conflicts(hill_climb(s)[0]) == 0 for s in starts)
        print(f"{solved}/200 random starts solved")    # 31/200 random starts solved
    ''')
    yield section("Why it gets stuck", "mountain")
    yield cards(
        ("Local maximum", "A peak higher than every neighbour but lower than the global maximum. Every move looks worse, so the search stops.", "mountain"),
        ("Plateau / shoulder", "A flat region: all neighbours have the same value. No gradient to follow — the search wanders or stops.", "minus"),
        ("Ridge", "A sequence of local maxima that rises diagonally; single moves in any axis go down, so progress is very slow.", "chart-line"),
        cols=3,
    )
    yield section("Variants that escape", "arrow-bounce")
    yield table(
        ["Variant", "Idea", "Effect on 8-queens (textbook figures)"],
        ["Steepest ascent", "Take the best neighbour", "Solves ~14% of starts, in ~4 steps"],
        ["**Sideways moves**", "Allow up to *k* moves to equal-valued neighbours (plateaus)", "~94% solved, ~21 steps"],
        ["**Stochastic** hill climbing", "Pick randomly among uphill moves, weighted by steepness", "Slower but finds better peaks on some landscapes"],
        ["**First-choice**", "Generate random neighbours until one is better", "Good when there are thousands of neighbours"],
        ["**Random-restart**", "Run from random starts until a solution appears", "Complete with probability → 1; expected restarts ≈ 1/p"],
    )
    yield code(QUEENS + '''
        import random

        def hill_climb(state):
            while True:
                nbrs = [state[:c] + (r,) + state[c + 1:] for c in range(8) for r in range(8) if r != state[c]]
                best = min(nbrs, key=conflicts)
                if conflicts(best) >= conflicts(state):
                    return state
                state = best

        def random_restart(seed):
            random.seed(seed)
            restarts = 0
            while True:
                result = hill_climb(tuple(random.randrange(8) for _ in range(8)))
                if conflicts(result) == 0:
                    return result, restarts
                restarts += 1

        print(random_restart(1))     # ((5, 1, 6, 0, 2, 4, 7, 3), 3)
    ''')
    yield note("Random-restart hill climbing is surprisingly strong: with success probability `p` per run, it needs `1/p` runs on average. For 8-queens, `p ≈ 0.14` gives ~7 runs; with sideways moves, millions of queens can be solved in seconds.")
    yield warn("Hill climbing is **incomplete** — it can stop at a local optimum and report it as the answer. Always ask: what is the landscape like, and how will the search escape a local optimum?")
    yield qa("What is the main weakness of hill climbing and how do you fix it?",
             "It gets stuck on local maxima, plateaus and ridges because it only accepts improvements. Fixes: random restarts, sideways moves, stochastic moves, or accepting some downhill moves (simulated annealing).")
    yield qa("How is gradient descent related to hill climbing?",
             "Gradient descent is hill climbing (descending) in a continuous space: the neighbour is chosen by stepping along the negative gradient. It has the same local-minimum issue, softened in deep learning by noise (SGD), momentum and the high-dimensional landscape.")


@topic(G, "simulated-annealing", "Simulated Annealing & Beam Search", "temperature")
def _():
    yield lead("Simulated annealing is hill climbing that sometimes accepts a *worse* move — often early on, rarely later — so it can shake itself out of local optima. Beam search keeps several states instead of one.")
    yield p("The name comes from metallurgy: heating metal and cooling it slowly lets atoms settle into a low-energy crystal. The algorithm picks a **random** neighbour; if it is better it always moves, and if it is worse by `ΔE` it moves with probability:")
    yield formula("P(accept worse move) = e^(−ΔE / T)")
    yield code('''
        import math

        accept = {T: [round(math.exp(-delta / T), 3) for delta in (1, 2, 5)] for T in (10, 1, 0.1)}
        print(accept[10])      # [0.905, 0.819, 0.607] ← hot: almost any move is accepted (ΔE = 1, 2, 5)
        print(accept[1])       # [0.368, 0.135, 0.007]
        print(accept[0.1])     # [0.0, 0.0, 0.0] ← cold: pure hill climbing
    ''')
    yield p("The **temperature** `T` starts high (random walk) and decreases according to a **schedule** (e.g. `T ← 0.99·T`). As `T → 0` it becomes plain hill climbing. If `T` is lowered slowly enough, it finds the global optimum with probability approaching 1.")
    yield code('''
        import math
        import random

        def conflicts(s):
            return sum(1 for i in range(8) for j in range(i + 1, 8) if s[i] == s[j] or abs(s[i] - s[j]) == j - i)

        def simulated_annealing(state, T=2.0, cooling=0.995, steps=20000):
            for t in range(steps):
                if conflicts(state) == 0:
                    return state, t
                col, row = random.randrange(8), random.randrange(8)
                nxt = state[:col] + (row,) + state[col + 1:]           # a random neighbour
                delta = conflicts(nxt) - conflicts(state)              # > 0 means worse
                if delta <= 0 or random.random() < math.exp(-delta / T):
                    state = nxt
                T = max(T * cooling, 1e-3)                             # cooling schedule
            return state, steps

        random.seed(1)
        start = tuple(random.randrange(8) for _ in range(8))      # the start where hill climbing got stuck
        end, t = simulated_annealing(start)
        print(end, conflicts(end), t)                             # (2, 5, 7, 0, 3, 6, 4, 1) 0 711
    ''')
    yield section("Local beam search", "brand-databricks")
    yield p("Keep **k** states instead of one. Each step, generate all successors of all `k` states and keep the best `k` overall. Unlike `k` independent restarts, information is shared: states on a good hill attract the whole beam.")
    yield cards(
        ("Local beam search", "Deterministic: top-`k` of all successors. Risk: the beam collapses into one small region (lack of diversity).", "list-numbers"),
        ("Stochastic beam search", "Choose `k` successors at random, weighted by value — keeps diversity. Resembles natural selection, leading to genetic algorithms.", "dice"),
        ("Beam search in NLP", "The same idea decodes text from a language model: keep the `k` most probable partial sentences at each step (see **Generative AI**).", "message"),
        cols=3,
    )
    yield table(
        ["Method", "States kept", "Accepts worse moves?", "Complete?"],
        ["Hill climbing", "1", "No", "No"],
        ["Random-restart HC", "1 (many runs)", "No", "With probability → 1"],
        ["Simulated annealing", "1", "Yes, with prob. `e^(−ΔE/T)`", "With a slow enough schedule (in the limit)"],
        ["Local beam search", "`k`", "Only via the beam", "No"],
        ["Genetic algorithm", "Population", "Yes (selection is stochastic)", "No"],
    )
    yield warn("The cooling schedule is the hard part: too fast and it freezes in a local optimum like hill climbing; too slow and it wastes time as a random walk. Tune the start temperature so early acceptance of worse moves is high (~80%).")
    yield qa("How does simulated annealing escape local optima?",
             "It accepts worse moves with probability `e^(−ΔE/T)`. At high temperature many downhill moves are accepted (exploration); as `T` falls, it accepts fewer and settles into a good optimum (exploitation).")
    yield qa("Local beam search vs k random restarts?",
             "Restarts run independently. Beam search pools all successors and keeps the best `k`, so effort moves to the most promising regions — faster, but prone to losing diversity.")


@topic(G, "genetic-algorithms", "Genetic Algorithms", "dna")
def _():
    yield lead("A genetic algorithm (GA) evolves a **population** of candidate solutions: the fittest are selected to reproduce, their encodings are combined by **crossover**, and random **mutation** keeps diversity. It is stochastic beam search with sexual reproduction.")
    yield steps(
        ("Encode", "Represent each candidate as a string — bits, digits or a permutation. 8-queens: 8 digits, one row per column."),
        ("Initialise", "Create a random population of `N` individuals."),
        ("Evaluate fitness", "Score each individual (higher = better). 8-queens: non-attacking pairs, max 28."),
        ("Select", "Pick parents with probability rising with fitness (tournament or roulette-wheel selection)."),
        ("Crossover", "Cut two parents at a random point and swap the tails → children combine traits."),
        ("Mutate", "With small probability change a random gene — keeps diversity, explores."),
        ("Replace & repeat", "The children form the next generation (often keeping the best few — **elitism**) until fit enough or out of time."),
    )
    yield code('''
        import random

        def fitness(s):                               # non-attacking pairs; 28 = solution
            return 28 - sum(1 for i in range(8) for j in range(i + 1, 8)
                            if s[i] == s[j] or abs(s[i] - s[j]) == j - i)

        def select(pop):                              # tournament selection of size 3
            return max(random.sample(pop, 3), key=fitness)

        def crossover(a, b):
            cut = random.randrange(1, 8)
            return a[:cut] + b[cut:]

        def mutate(s, rate=0.2):
            if random.random() < rate:
                col = random.randrange(8)
                s = s[:col] + (random.randrange(8),) + s[col + 1:]
            return s

        def genetic_algorithm(size=60, generations=500):
            pop = [tuple(random.randrange(8) for _ in range(8)) for _ in range(size)]
            history = []
            for gen in range(generations):
                best = max(pop, key=fitness)
                history.append(fitness(best))
                if fitness(best) == 28:
                    return best, gen, history
                children = [mutate(crossover(select(pop), select(pop))) for _ in range(size - 2)]
                pop = sorted(pop, key=fitness)[-2:] + children          # elitism: keep the best 2
            return best, generations, history

        random.seed(7)
        best, gen, history = genetic_algorithm()
        print(best, fitness(best))           # (3, 7, 0, 2, 5, 1, 6, 4) 28
        print(gen)                           # 23 ← generations needed
        print(history[::4])                  # [26, 26, 27, 27, 27, 27] ← best fitness every 4th generation
    ''')
    yield section("Crossover in one picture", "git-merge")
    yield table(
        ["", "Genes (row of the queen in each column)"],
        ["Parent A", "`3 2 7 5 | 2 4 1 1`"],
        ["Parent B", "`2 4 7 4 | 7 5 5 2`"],
        ["Child", "`3 2 7 5 | 7 5 5 2` — head of A, tail of B"],
    )
    yield p("Crossover helps when the encoding has meaningful **building blocks** — contiguous substrings that are good on their own (a well-placed group of queens). If genes interact randomly, crossover is just a big random jump.")
    yield table(
        ["Strength", "Weakness"],
        ["Needs only a fitness function — no gradients, works on discrete or weird spaces", "Many evaluations; slow compared with problem-specific methods"],
        ["Population explores several regions in parallel", "Many knobs: population size, rates, selection pressure, encoding"],
        ["Easy to parallelise", "No optimality guarantee; can converge prematurely"],
    )
    yield chips("scheduling", "circuit & antenna design", "neural architecture search", "game-level generation", "feature selection", "evolution strategies (CMA-ES)", "genetic programming")
    yield warn("Premature convergence: if selection is too strong or mutation too weak, the population becomes clones of one early good individual and stops exploring. Raise mutation, use tournaments of smaller size, or add diversity measures.")
    yield qa("What are the main operators of a genetic algorithm?",
             "Selection (fitter individuals reproduce more), crossover (combine parts of two parents) and mutation (random small changes). Elitism optionally copies the best individuals unchanged into the next generation.")
    yield qa("How is a GA related to local beam search?",
             "Both keep a set of states and favour good ones. A GA is stochastic beam search where successors are made by combining *two* parents (crossover) rather than modifying one.")
