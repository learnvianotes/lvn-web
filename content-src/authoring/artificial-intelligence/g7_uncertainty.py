from kit import *

G = "Uncertainty & Decision Making"


@topic(G, "probability-bayes", "Probability & Bayes' Rule", "percentage")
def _():
    yield lead("Logic says a sentence is true, false or unknown. Real agents need *degrees of belief*: a toothache makes a cavity likely, not certain. Probability theory is the calculus of belief, and Bayes' rule is how an agent updates it when evidence arrives.")
    yield section("Why logic isn't enough", "question-mark")
    yield p("A rule like `Toothache ⇒ Cavity` is wrong (gum disease, abscesses…), and listing every exception fails for three reasons: **laziness** (too many rules), **theoretical ignorance** (medicine has no complete theory) and **practical ignorance** (not every test has been run). Probabilities summarise all of that uncertainty.")
    yield section("The rules you need", "math-function")
    yield table(
        ["Rule", "Formula"],
        ["Conditional probability", "`P(a | b) = P(a ∧ b) / P(b)`"],
        ["Product rule", "`P(a ∧ b) = P(a | b) · P(b)`"],
        ["Marginalisation (sum out)", "`P(a) = Σ_b P(a, b)`"],
        ["Independence", "`P(a | b) = P(a)`  ⇔  `P(a ∧ b) = P(a)·P(b)`"],
        ["Conditional independence", "`P(a ∧ b | c) = P(a | c) · P(b | c)`"],
        ["**Bayes' rule**", "`P(cause | effect) = P(effect | cause) · P(cause) / P(effect)`"],
    )
    yield p("With the full joint distribution, *any* question is answered by summing entries. The textbook dentist domain (Toothache, Cavity, the probe Catches):")
    yield code('''
        # full joint distribution P(Toothache, Catch, Cavity)
        JOINT = {
            (True, True, True): 0.108, (True, True, False): 0.016,
            (True, False, True): 0.012, (True, False, False): 0.064,
            (False, True, True): 0.072, (False, True, False): 0.144,
            (False, False, True): 0.008, (False, False, False): 0.576,
        }
        def P(cond):
            return sum(p for (toothache, catch, cavity), p in JOINT.items() if cond(toothache, catch, cavity))

        print(round(P(lambda t, c, cav: cav), 3))                     # 0.2 ← prior P(cavity), by marginalising
        p_both = P(lambda t, c, cav: cav and t)
        print(round(p_both / P(lambda t, c, cav: t), 3))              # 0.6 ← P(cavity | toothache)

        # normalisation: compute unnormalised values for each value of the query, then scale to sum to 1
        unnorm = [P(lambda t, c, cav: t and cav), P(lambda t, c, cav: t and not cav)]
        print([round(x / sum(unnorm), 3) for x in unnorm])             # [0.6, 0.4] ← P(Cavity | toothache) = α ⟨0.12, 0.08⟩
    ''')
    yield warn("The full joint grows as `2ⁿ` for `n` Boolean variables — 2³⁰ ≈ a billion numbers for just 30 symptoms. Independence and conditional independence (Bayesian networks, next topic) are what make probabilistic reasoning tractable.")
    yield section("Bayes' rule and the base-rate fallacy", "flask")
    yield formula("P(D | +) = P(+ | D) · P(D) / [ P(+ | D) · P(D) + P(+ | ¬D) · P(¬D) ]")
    yield code('''
        prevalence = 0.01           # P(disease)
        sensitivity = 0.90          # P(positive | disease)
        false_positive = 0.09       # P(positive | no disease)

        p_positive = sensitivity * prevalence + false_positive * (1 - prevalence)
        posterior = sensitivity * prevalence / p_positive
        print(round(p_positive, 4), round(posterior, 3))       # 0.0981 0.092 ← a positive test means only ~9% chance of disease

        second = sensitivity * posterior / (sensitivity * posterior + false_positive * (1 - posterior))
        print(round(second, 3))                                  # 0.503 ← a second positive: yesterday's posterior is today's prior
    ''')
    yield note("Most positives come from the 99% of healthy people. Ignoring the prior (the base rate) is the **base-rate fallacy** — a favourite interview question. Bayes' rule is also *diagnostic reasoning*: we usually know `P(effect | cause)` (how a disease causes symptoms) and want `P(cause | effect)`.")
    yield section("Naive Bayes", "mail")
    yield p("Assume every effect is conditionally independent given the cause: `P(Cause, e₁…eₙ) = P(Cause) · Π P(eᵢ | Cause)`. Wrong in detail, but it needs only `O(n)` numbers and works remarkably well for text classification:")
    yield code('''
        from collections import Counter
        import math

        train = [("win money now", "spam"), ("cheap money offer", "spam"), ("win a cheap prize", "spam"),
                 ("meeting at noon", "ham"), ("project meeting notes", "ham"), ("lunch at noon", "ham")]
        words = {c: Counter(w for text, lab in train if lab == c for w in text.split()) for c in ("spam", "ham")}
        prior = Counter(lab for _, lab in train)
        vocab = {w for text, _ in train for w in text.split()}

        def log_posterior(text, c):                 # log P(c) + Σ log P(word | c), Laplace smoothing (+1)
            total = sum(words[c].values())
            return math.log(prior[c] / len(train)) + sum(
                math.log((words[c][w] + 1) / (total + len(vocab))) for w in text.split())

        print(max(("spam", "ham"), key=lambda c: log_posterior("win cheap money", c)))    # spam
        print(max(("spam", "ham"), key=lambda c: log_posterior("noon meeting", c)))       # ham
    ''')
    yield p("The **Machine Learning** notes cover naive Bayes as a classifier (variants, evaluation); here it matters as the simplest Bayesian network — one cause with independent effects.")
    yield qa("State Bayes' rule and explain each term.",
             "`P(H | E) = P(E | H) · P(H) / P(E)`. `P(H)` is the prior belief in the hypothesis, `P(E | H)` the likelihood of the evidence if H is true, `P(E)` the total probability of the evidence (a normaliser), and `P(H | E)` the posterior belief after seeing the evidence.")
    yield qa("A test is 90% sensitive with a 9% false-positive rate; the disease affects 1%. You test positive — what's the probability you have it?",
             "About 9%: `0.9 × 0.01 / (0.9 × 0.01 + 0.09 × 0.99) ≈ 0.092`. The low base rate means false positives from healthy people outnumber true positives.")
    yield qa("Why is naive Bayes called naive?",
             "It assumes all features are conditionally independent given the class, which is rarely true (words in an email are correlated). The assumption makes it fast and data-efficient, and classification often stays accurate even when the probabilities themselves are poorly calibrated.")


@topic(G, "bayesian-networks", "Bayesian Networks", "affiliate")
def _():
    yield lead("A Bayesian network is a directed acyclic graph whose nodes are random variables and whose edges mean “directly influences”. Each node stores a small conditional probability table (CPT); together they define the full joint distribution compactly.")
    yield formula("P(x₁, …, xₙ) = Π P(xᵢ | Parents(Xᵢ))")
    yield section("The burglar alarm network", "alarm")
    yield table(
        ["Node", "Parents", "CPT"],
        ["Burglary (B)", "—", "`P(b) = 0.001`"],
        ["Earthquake (E)", "—", "`P(e) = 0.002`"],
        ["Alarm (A)", "B, E", "`P(a | b, e) = 0.95`, `P(a | b, ¬e) = 0.94`, `P(a | ¬b, e) = 0.29`, `P(a | ¬b, ¬e) = 0.001`"],
        ["JohnCalls (J)", "A", "`P(j | a) = 0.90`, `P(j | ¬a) = 0.05`"],
        ["MaryCalls (M)", "A", "`P(m | a) = 0.70`, `P(m | ¬a) = 0.01`"],
    )
    yield p("10 numbers instead of the 2⁵ − 1 = 31 of the full joint — and the savings grow exponentially with more variables. Each variable is conditionally independent of its non-descendants given its parents: John's call depends on the alarm, not directly on burglaries.")
    yield section("Exact inference by enumeration", "sum")
    yield p("To answer `P(Burglary | JohnCalls, MaryCalls)`, sum the joint over the hidden variables (E, A) for each value of B, then normalise:")
    yield formula("P(B | j, m) = α Σₑ Σₐ P(B) · P(e) · P(a | B, e) · P(j | a) · P(m | a)")
    yield code('''
        from itertools import product

        P_B, P_E = 0.001, 0.002
        P_A = {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001}
        P_J = {True: 0.90, False: 0.05}
        P_M = {True: 0.70, False: 0.01}

        def pr(p_true, value):
            return p_true if value else 1 - p_true

        def joint(b, e, a, j, m):                    # product of the local CPT entries
            return pr(P_B, b) * pr(P_E, e) * pr(P_A[(b, e)], a) * pr(P_J[a], j) * pr(P_M[a], m)

        print(f"{joint(False, False, True, True, True):.6f}")   # 0.000628 ← P(j, m, a, ¬b, ¬e)

        def query_burglary(j, m):
            unnorm = [sum(joint(b, e, a, j, m) for e, a in product([True, False], repeat=2)) for b in (True, False)]
            return round(unnorm[0] / sum(unnorm), 3)             # normalise (α)

        print(query_burglary(True, True))     # 0.284 ← both neighbours call: still only ~28%
        print(query_burglary(True, False))    # 0.005 ← only John calls
    ''')
    yield note("Enumeration costs `O(2ⁿ)` in the worst case. **Variable elimination** caches repeated sub-products and is linear for singly-connected networks (polytrees). Exact inference in general networks is NP-hard, hence approximate methods.")
    yield section("Approximate inference by sampling", "dice")
    yield code('''
        import random

        P_B, P_E = 0.001, 0.002
        P_A = {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001}
        P_J = {True: 0.90, False: 0.05}
        P_M = {True: 0.70, False: 0.01}

        def likelihood_weighting(n):
            """Sample non-evidence variables in topological order; weight by the likelihood of evidence j, m."""
            weights = {True: 0.0, False: 0.0}
            for _ in range(n):
                b = random.random() < P_B
                e = random.random() < P_E
                a = random.random() < P_A[(b, e)]
                weights[b] += P_J[a] * P_M[a]          # evidence is fixed, not sampled
            return round(weights[True] / (weights[True] + weights[False]), 2)

        random.seed(0)
        print(likelihood_weighting(200_000))     # 0.28 ← close to the exact 0.284
    ''')
    yield table(
        ["Method", "Idea", "Weakness"],
        ["Rejection sampling", "Sample the whole network, discard samples that contradict the evidence", "Wastes almost everything when evidence is rare (here `P(j, m) ≈ 0.002`)"],
        ["Likelihood weighting", "Fix evidence variables, weight each sample by the evidence likelihood", "Poor when evidence is downstream of unlikely causes"],
        ["Gibbs sampling (MCMC)", "Resample one variable at a time given its Markov blanket", "Slow mixing with near-deterministic CPTs"],
    )
    yield section("Reading independence from the graph", "git-fork")
    yield table(
        ["Pattern", "Shape", "X and Y independent…"],
        ["Causal chain", "`X → Z → Y`", "…given `Z` (Burglary ⟂ JohnCalls | Alarm)"],
        ["Common cause", "`X ← Z → Y`", "…given `Z` (JohnCalls ⟂ MaryCalls | Alarm)"],
        ["Common effect (v-structure)", "`X → Z ← Y`", "…only when `Z` (and its descendants) is **not** observed — observing the alarm makes burglary and earthquake dependent (“explaining away”)"],
    )
    yield qa("What does an edge in a Bayesian network mean, and why is the network compact?",
             "An edge `X → Y` means X directly influences Y; each node is conditionally independent of its non-descendants given its parents. The joint is then a product of small local CPTs, so a node with `k` Boolean parents needs `2ᵏ` numbers instead of the exponential full joint.")
    yield qa("What is explaining away?",
             "In a v-structure `Burglary → Alarm ← Earthquake`, the causes are independent until the alarm is observed. Once it rings, learning there was an earthquake *lowers* the probability of a burglary — the earthquake explains the alarm away.")
    yield qa("How do you do inference in a Bayesian network?",
             "Exactly by enumeration or variable elimination (sum out hidden variables, normalise) — exponential in general, linear on polytrees. Approximately by sampling: rejection sampling, likelihood weighting or MCMC such as Gibbs sampling.")


@topic(G, "markov-models-hmm", "Markov Chains & Hidden Markov Models", "timeline-event")
def _():
    yield lead("To reason over time, model the world as a sequence of states where the future depends only on the present. When the states themselves are hidden and only noisy observations are seen, you get a hidden Markov model (HMM).")
    yield define("Markov assumption", "the next state depends only on the current state: `P(Xₜ | X₀…Xₜ₋₁) = P(Xₜ | Xₜ₋₁)`. With a fixed transition matrix the process is **stationary** and is a Markov chain.")
    yield code('''
        # weather Markov chain: rows = today, columns = tomorrow (sunny, rainy)
        T = [[0.9, 0.1],
             [0.5, 0.5]]

        def step(dist):
            return [sum(dist[i] * T[i][j] for i in range(2)) for j in range(2)]

        dist = [0.0, 1.0]                      # it's raining today
        tomorrow = step(dist)
        for _ in range(50):
            dist = step(dist)
        print([round(p, 3) for p in tomorrow])   # [0.5, 0.5]
        print([round(p, 3) for p in dist])       # [0.833, 0.167] ← stationary distribution: the start no longer matters
    ''')
    yield section("Hidden Markov models", "eye-off")
    yield p("An HMM adds a **sensor model** `P(Eₜ | Xₜ)`. The textbook *umbrella world*: a guard underground can't see the weather, only whether the director brings an umbrella. Rain persists with probability 0.7; the umbrella appears on 90% of rainy days and 20% of dry days.")
    yield table(
        ["Task", "Computes", "Algorithm"],
        ["**Filtering**", "`P(Xₜ | e₁:ₜ)` — belief about now", "Forward algorithm"],
        ["**Prediction**", "`P(Xₜ₊ₖ | e₁:ₜ)` — the future", "Forward, then transitions only"],
        ["**Smoothing**", "`P(Xₖ | e₁:ₜ)`, `k < t` — the past, with hindsight", "Forward–backward"],
        ["**Most likely explanation**", "`argmax P(x₁:ₜ | e₁:ₜ)` — the best state sequence", "**Viterbi** (dynamic programming)"],
        ["Learning", "Transition and sensor models from data", "Baum–Welch (EM)"],
    )
    yield code('''
        TRANS = {True: 0.7, False: 0.3}          # P(rain today | rain yesterday = key)
        SENSOR = {True: 0.9, False: 0.2}         # P(umbrella | rain = key)

        def forward(evidence, prior=0.5):
            belief = {True: prior, False: 1 - prior}
            history = []
            for umbrella in evidence:
                predicted = {r: sum(belief[prev] * (TRANS[prev] if r else 1 - TRANS[prev]) for prev in (True, False))
                             for r in (True, False)}                                        # predict
                weighted = {r: predicted[r] * (SENSOR[r] if umbrella else 1 - SENSOR[r]) for r in (True, False)}
                total = sum(weighted.values())
                belief = {r: weighted[r] / total for r in (True, False)}                    # update + normalise
                history.append(round(belief[True], 3))
            return history

        def viterbi(evidence, prior=0.5):
            like = lambda r, u: SENSOR[r] if u else 1 - SENSOR[r]
            trans = lambda prev, r: TRANS[prev] if r else 1 - TRANS[prev]
            best = {r: (prior * like(r, evidence[0]), [r]) for r in (True, False)}
            for u in evidence[1:]:
                best = {r: max(((p * trans(prev, r) * like(r, u), path + [r]) for prev, (p, path) in best.items()),
                               key=lambda x: x[0]) for r in (True, False)}
            return ["rain" if r else "dry" for r in max(best.values(), key=lambda x: x[0])[1]]

        print(forward([True, True]))                         # [0.818, 0.883] ← P(rain) after day 1 and day 2
        print(viterbi([True, True, False, True, True]))      # ['rain', 'rain', 'dry', 'rain', 'rain']
    ''')
    yield note("Before deep learning, HMMs powered speech recognition, part-of-speech tagging and gene finding. The same filtering idea with continuous states and Gaussian noise is the **Kalman filter** (tracking, GPS, robotics); with samples it is the **particle filter** (robot localisation).")
    yield qa("What is the Markov assumption?",
             "The future is conditionally independent of the past given the present state: `P(Xₜ | X₀:ₜ₋₁) = P(Xₜ | Xₜ₋₁)`. It keeps models of time compact; if it doesn't hold, enrich the state (add more history or variables).")
    yield qa("What problems does an HMM solve, and with which algorithms?",
             "Filtering (forward algorithm), prediction, smoothing (forward–backward), the most likely hidden-state sequence (Viterbi), and learning the parameters (Baum–Welch / EM). Each runs in time linear in the sequence length.")


@topic(G, "mdp-value-iteration", "Utility & Markov Decision Processes", "adjustments-horizontal")
def _():
    yield lead("When actions have uncertain outcomes, the agent needs more than a plan: it needs a **policy** — the best action in every state — chosen to maximise expected utility. MDPs formalise this, and the Bellman equation says how to solve them.")
    yield section("Utility theory in one minute", "scale")
    yield p("A rational agent picks the action with **maximum expected utility** (MEU): `EU(a) = Σ P(outcome | a) · U(outcome)`. Utilities are not money: most people prefer a sure $1M to a 50% chance of $3M because the utility of money is concave (**risk aversion**).")
    yield code('''
        import math

        lotteries = {"sure $1M": [(1.0, 1_000_000)], "50% of $3M": [(0.5, 3_000_000), (0.5, 0)]}
        EMV = {k: sum(p * x for p, x in v) for k, v in lotteries.items()}
        EU = {k: round(sum(p * math.log10(1 + x) for p, x in v), 2) for k, v in lotteries.items()}   # concave utility
        print(max(EMV, key=EMV.get), EMV)     # 50% of $3M {'sure $1M': 1000000.0, '50% of $3M': 1500000.0} ← expected money prefers the gamble
        print(max(EU, key=EU.get), EU)        # sure $1M {'sure $1M': 6.0, '50% of $3M': 3.24} ← a risk-averse utility prefers the sure thing
    ''')
    yield section("Markov decision processes", "route-2")
    yield table(
        ["Component", "Meaning"],
        ["States `S`", "Fully observable world states"],
        ["Actions `A(s)`", "Actions available in each state"],
        ["Transition model `P(s′ | s, a)`", "Probability of reaching `s′` — outcomes are stochastic but Markovian"],
        ["Reward `R(s, a, s′)`", "Immediate reward for a transition"],
        ["Discount `γ ∈ [0, 1]`", "How much future rewards count; `γ < 1` keeps infinite sums finite and prefers sooner rewards"],
    )
    yield p("A **policy** `π(s)` maps states to actions. The utility (value) of a state under the optimal policy satisfies the **Bellman equation**:")
    yield formula("U(s) = max over a of Σ_s′ P(s′ | s, a) · [ R(s, a, s′) + γ · U(s′) ]")
    yield section("Value iteration on the 4×3 grid world", "grid-4x4")
    yield p("The textbook world: start bottom-left, +1 and −1 exits on the right, a wall at (2, 2). Each move goes the intended way with probability 0.8 and slips sideways with 0.1 each; every step costs 0.04. Value iteration applies the Bellman equation as an update until the utilities stop changing:")
    yield code('''
        COLS, ROWS, WALL = 4, 3, (2, 2)
        TERMINAL = {(4, 3): 1.0, (4, 2): -1.0}
        STEP_REWARD, GAMMA = -0.04, 1.0
        MOVES = {"^": (0, 1), "v": (0, -1), "<": (-1, 0), ">": (1, 0)}
        SIDEWAYS = {"^": "<>", "v": "<>", "<": "^v", ">": "^v"}
        STATES = [(c, r) for c in range(1, COLS + 1) for r in range(1, ROWS + 1) if (c, r) != WALL]

        def go(s, move):
            dc, dr = MOVES[move]
            t = (s[0] + dc, s[1] + dr)
            return t if t in STATES else s                        # bumping into a wall/edge: stay put

        def outcomes(s, a):                                        # [(probability, next state)]
            return [(0.8, go(s, a))] + [(0.1, go(s, side)) for side in SIDEWAYS[a]]

        def q_value(U, s, a):
            return sum(p * (STEP_REWARD + GAMMA * U[t]) for p, t in outcomes(s, a))

        def value_iteration(eps=1e-6):
            U = {s: TERMINAL.get(s, 0.0) for s in STATES}
            sweeps = 0
            while True:
                sweeps += 1
                new = {s: U[s] if s in TERMINAL else max(q_value(U, s, a) for a in MOVES) for s in STATES}
                delta = max(abs(new[s] - U[s]) for s in STATES)
                U = new
                if delta < eps:
                    return U, sweeps

        U, sweeps = value_iteration()
        policy = {s: max(MOVES, key=lambda a: q_value(U, s, a)) for s in STATES if s not in TERMINAL}

        def row(r, show):
            return " ".join(show(c, r) for c in range(1, COLS + 1))
        val = lambda c, r: "  ## " if (c, r) == WALL else f"{U[(c, r)]:5.3f}"
        arrow = lambda c, r: "#" if (c, r) == WALL else ("+" if U.get((c, r)) == 1 else "-") if (c, r) in TERMINAL else policy[(c, r)]

        print(sweeps)                          # 28
        print(row(3, val))                     # 0.812 0.868 0.918 1.000
        print(row(2, val))                     # 0.762   ##  0.660 -1.000
        print(row(1, val))                     # 0.705 0.655 0.611 0.388
        print(row(3, arrow), "|", row(2, arrow), "|", row(1, arrow))   # > > > + | ^ # ^ - | ^ < < < ← top | middle | bottom row
    ''')
    yield p("Look at (3, 2) and (4, 1), next to the −1 exit: the policy goes up and left — the long way round — rather than risk a 10% slip into the pit. Make the step cost much larger (say −2 per step) and the agent would dive into the −1 exit just to stop paying.")
    yield section("Policy iteration", "refresh")
    yield steps(
        ("Policy evaluation", "For the current policy π, compute `U^π(s) = Σ P(s′ | s, π(s)) [R + γ U^π(s′)]` — a linear system (no max), solvable exactly or by a few sweeps."),
        ("Policy improvement", "Make π greedy with respect to `U^π`: `π(s) ← argmaxₐ Σ P(s′ | s, a)[R + γ U^π(s′)]`."),
        ("Repeat", "Stop when the policy no longer changes — it is then optimal. Usually converges in very few iterations."),
    )
    yield code('''
        COLS, ROWS, WALL = 4, 3, (2, 2)
        TERMINAL = {(4, 3): 1.0, (4, 2): -1.0}
        MOVES = {"^": (0, 1), "v": (0, -1), "<": (-1, 0), ">": (1, 0)}
        SIDEWAYS = {"^": "<>", "v": "<>", "<": "^v", ">": "^v"}
        STATES = [(c, r) for c in range(1, COLS + 1) for r in range(1, ROWS + 1) if (c, r) != WALL]

        def go(s, m):
            t = (s[0] + MOVES[m][0], s[1] + MOVES[m][1])
            return t if t in STATES else s

        def q(U, s, a):
            return sum(p * (-0.04 + U[t]) for p, t in [(0.8, go(s, a))] + [(0.1, go(s, x)) for x in SIDEWAYS[a]])

        def policy_iteration():
            policy = {s: "^" for s in STATES if s not in TERMINAL}         # an arbitrary start: always go up
            U = {s: TERMINAL.get(s, 0.0) for s in STATES}
            for iteration in range(1, 100):
                for _ in range(100):                                       # evaluate (simplified: repeated sweeps)
                    U = {s: U[s] if s in TERMINAL else q(U, s, policy[s]) for s in STATES}
                new = {s: max(MOVES, key=lambda a: q(U, s, a)) for s in policy}   # improve
                if new == policy:
                    return policy, iteration
                policy = new

        policy, iterations = policy_iteration()
        print(iterations)                                                   # 5
        print("".join(policy[s] for s in sorted(policy)))                   # ^^><><^>< ← states (1,1), (1,2), … (4,1): the same policy as value iteration
    ''')
    yield table(
        ["", "Value iteration", "Policy iteration"],
        ["Each iteration", "One Bellman update (with max) of every state", "Full policy evaluation + one improvement"],
        ["Iterations", "Many cheap ones", "Few expensive ones"],
        ["Converges to", "Optimal utilities (policy extracted at the end)", "Optimal policy exactly, in finitely many steps"],
    )
    yield warn("MDPs assume the agent *knows* `P` and `R` and can *see* the state. If the state is hidden, it's a POMDP (plan over belief states — much harder). If `P` and `R` are unknown, the agent must learn from experience — reinforcement learning.")
    yield qa("What is the Bellman equation?",
             "It defines the utility of a state recursively: the best action's expected immediate reward plus the discounted utility of the next state, `U(s) = maxₐ Σ P(s′|s,a)[R + γU(s′)]`. Value iteration turns it into an update rule; its unique solution gives the optimal policy.")
    yield qa("What does the discount factor γ do?",
             "It weighs future rewards: `γ` near 0 makes the agent short-sighted, near 1 far-sighted. With `γ < 1` infinite-horizon sums stay finite and value iteration converges geometrically; it can also model uncertainty about whether the future happens at all.")
    yield qa("Value iteration vs policy iteration?",
             "Value iteration repeatedly applies the Bellman update to utilities and extracts the policy at the end. Policy iteration alternates evaluating the current policy and making it greedy; it needs fewer iterations, each more expensive. Both converge to the optimal policy.")


@topic(G, "reinforcement-learning", "Reinforcement Learning", "robot-face")
def _():
    yield lead("Reinforcement learning (RL) solves an MDP **without knowing** its transition model or reward function: the agent learns from trial and error, guided only by rewards. It powers game-playing agents, robotics controllers and the RLHF stage of LLM training.")
    yield flow("Agent observes state s", "Chooses action a", "Environment returns reward r and next state s′", "Agent updates its estimates")
    yield table(
        ["Approach", "Learns", "Example"],
        ["**Model-based**", "`P(s′ | s, a)` and `R`, then plans (value iteration)", "Dyna, AlphaZero (known rules), MuZero (learned model)"],
        ["**Model-free, value-based**", "`Q(s, a)` — value of an action in a state", "Q-learning, SARSA, DQN"],
        ["**Model-free, policy-based**", "The policy `π(a | s)` directly, by gradient ascent on reward", "REINFORCE, actor-critic, PPO"],
    )
    yield section("Exploration vs exploitation", "compass")
    yield p("An agent that always takes the best-known action (**exploit**) may never discover a better one; one that always tries new actions (**explore**) never cashes in. **ε-greedy** explores with probability ε. A 3-armed bandit with win rates 0.2, 0.5 and 0.7:")
    yield code('''
        import random

        def bandit(epsilon, pulls=2000, true_p=(0.2, 0.5, 0.7)):
            counts, values, total = [0, 0, 0], [0.0, 0.0, 0.0], 0
            for _ in range(pulls):
                if random.random() < epsilon:
                    arm = random.randrange(3)                                # explore
                else:
                    arm = max(range(3), key=lambda i: values[i])             # exploit
                reward = 1 if random.random() < true_p[arm] else 0
                counts[arm] += 1
                values[arm] += (reward - values[arm]) / counts[arm]          # running average
                total += reward
            return counts, total

        random.seed(1)
        print(bandit(0.0))     # ([2000, 0, 0], 406) ← greedy: never tries the other arms
        print(bandit(0.1))     # ([74, 73, 1853], 1355) ← explores, then mostly pulls the best arm
    ''')
    yield section("Temporal-difference learning and Q-learning", "math-function")
    yield p("TD learning updates an estimate towards a **one-step bootstrapped target** after every transition — no need to wait for the episode to end, and no model required:")
    yield formula("TD(0):   U(s) ← U(s) + α [ r + γ U(s′) − U(s) ]")
    yield formula("Q-learning:   Q(s, a) ← Q(s, a) + α [ r + γ · maxₐ′ Q(s′, a′) − Q(s, a) ]")
    yield formula("SARSA:   Q(s, a) ← Q(s, a) + α [ r + γ · Q(s′, a′) − Q(s, a) ]     (a′ = the action actually taken next)")
    yield p("Q-learning is **off-policy**: it learns the value of the *greedy* policy while behaving ε-greedily. SARSA is **on-policy**: it learns the value of the policy it actually follows, exploration included. The classic *cliff walking* grid shows the difference — walk from the bottom-left to the bottom-right corner; stepping into the cliff between them costs −100 and restarts:")
    yield code('''
        import random

        ROWS, COLS = 4, 12
        START, GOAL = (3, 0), (3, 11)
        ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]              # up, down, left, right

        def step(s, a):
            r, c = min(max(s[0] + a[0], 0), ROWS - 1), min(max(s[1] + a[1], 0), COLS - 1)
            if r == 3 and 0 < c < 11:
                return START, -100                                 # fell off the cliff
            return (r, c), -1

        def choose(Q, s, eps):
            if random.random() < eps:
                return random.randrange(4)
            return max(range(4), key=lambda a: Q[(s, a)])

        def train(method, episodes=500, alpha=0.5, gamma=1.0, eps=0.1):
            Q = {((r, c), a): 0.0 for r in range(ROWS) for c in range(COLS) for a in range(4)}
            returns = []
            for _ in range(episodes):
                s, a, total = START, choose(Q, START, eps), 0
                while s != GOAL:
                    s2, reward = step(s, ACTIONS[a])
                    a2 = choose(Q, s2, eps)
                    if method == "q-learning":
                        target = reward + gamma * max(Q[(s2, b)] for b in range(4))   # best next action
                    else:
                        target = reward + gamma * Q[(s2, a2)]                          # the action we will take
                    if s2 == GOAL:
                        target = reward
                    Q[(s, a)] += alpha * (target - Q[(s, a)])
                    s, a, total = s2, a2, total + reward
                returns.append(total)
            return Q, sum(returns[-100:]) / 100

        def greedy_path(Q):
            s, path = START, [START]
            while s != GOAL and len(path) < 50:
                s, _ = step(s, ACTIONS[max(range(4), key=lambda a: Q[(s, a)])])
                path.append(s)
            return path

        random.seed(0)
        Q1, avg1 = train("q-learning")
        Q2, avg2 = train("sarsa")
        p1, p2 = greedy_path(Q1), greedy_path(Q2)
        print(len(p1) - 1, min(r for r, c in p1))     # 13 2 ← Q-learning: shortest path, right along the cliff edge (row 2)
        print(len(p2) - 1, min(r for r, c in p2))     # 17 0 ← SARSA: longer, safe path along the top row (row 0)
        print(round(avg1), round(avg2))               # -43 -26 ← yet SARSA earns more *while exploring*
    ''')
    yield note("Q-learning learns the optimal path along the cliff edge, but with ε-greedy exploration it occasionally slips off while training. SARSA accounts for its own exploration and prefers a safer route — lower optimal-path quality, higher reward during learning.")
    yield section("Scaling up: deep RL", "brain")
    yield table(
        ["Milestone", "Idea"],
        ["TD-Gammon (1992)", "TD learning with a small neural network reached master-level backgammon"],
        ["DQN (2015)", "Q-learning with a CNN over raw pixels + experience replay + target network; human-level on many Atari games"],
        ["AlphaGo / AlphaZero (2016–17)", "Self-play RL + MCTS + policy/value networks; superhuman Go, chess, shogi"],
        ["PPO & actor-critic", "Stable policy-gradient methods for robotics and continuous control"],
        ["RLHF (2022–)", "A reward model trained on human preferences, optimised with PPO-style RL, aligns LLMs (see **Generative AI**)"],
    )
    yield warn("**Reward hacking**: an RL agent optimises the reward you wrote, not the one you meant — a boat-racing agent learned to spin in circles collecting points instead of finishing the race. Reward design is part of AI safety (see **AI Ethics, Safety & Fairness**).")
    yield qa("How does reinforcement learning differ from supervised learning?",
             "There are no labelled correct actions — only scalar rewards, often delayed. The agent's own actions determine what data it sees, so it must balance exploration and exploitation and solve credit assignment (which earlier action earned a later reward).")
    yield qa("Q-learning vs SARSA?",
             "Both are TD methods learning `Q(s, a)`. Q-learning is off-policy — its target uses `max Q(s′, ·)`, the greedy action — so it learns the optimal policy regardless of exploration. SARSA is on-policy — its target uses the action actually taken next — so it learns the value of the exploring policy and behaves more cautiously (cliff walking).")
    yield qa("What is the exploration–exploitation trade-off? Name some strategies.",
             "Exploiting uses current knowledge to maximise reward now; exploring gathers information that may pay off later. Strategies: ε-greedy (often with ε decaying), softmax/Boltzmann exploration, optimism in the face of uncertainty (optimistic initial values, UCB), and Thompson sampling.")
