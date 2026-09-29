from kit import *

G = "Logic, Knowledge & Planning"


@topic(G, "propositional-logic", "Propositional Logic", "logic-and")
def _():
    yield lead("A **knowledge-based agent** stores facts as sentences in a formal language and derives new facts by inference. Propositional logic is the simplest such language: sentences are built from true/false symbols with connectives.")
    yield flow("TELL the KB what is perceived", "ASK the KB what to do (inference)", "TELL the KB the action taken")
    yield section("Syntax and semantics", "code")
    yield table(
        ["Connective", "Symbol", "Read as", "True when"],
        ["Negation", "`¬P`", "not P", "`P` is false"],
        ["Conjunction", "`P ∧ Q`", "P and Q", "both are true"],
        ["Disjunction", "`P ∨ Q`", "P or Q", "at least one is true"],
        ["Implication", "`P ⇒ Q`", "if P then Q", "`P` is false **or** `Q` is true"],
        ["Biconditional", "`P ⇔ Q`", "P if and only if Q", "both have the same value"],
    )
    yield warn("`P ⇒ Q` is true whenever `P` is false (“if pigs fly, 1 = 2” is true). Implication in logic states no causal link — only that the case “P true, Q false” does not happen.")
    yield section("Key vocabulary", "book")
    yield table(
        ["Term", "Meaning"],
        ["**Model**", "An assignment of true/false to every symbol — a possible world"],
        ["**Entailment** `KB ⊨ α`", "`α` is true in *every* model where the KB is true"],
        ["**Inference** `KB ⊢ α`", "An algorithm derives `α` from the KB"],
        ["**Sound**", "Derives only entailed sentences (never lies)"],
        ["**Complete**", "Can derive every entailed sentence"],
        ["**Valid** (tautology)", "True in all models: `P ∨ ¬P`"],
        ["**Satisfiable**", "True in at least one model; *unsatisfiable* = true in none"],
    )
    yield note("Two facts power all of logical inference: `KB ⊨ α` **iff** `KB ⇒ α` is valid (deduction theorem), and **iff** `KB ∧ ¬α` is unsatisfiable (proof by contradiction — the basis of resolution).")
    yield section("Inference by model checking", "table")
    yield p("The simplest sound and complete method: enumerate every model (a truth table) and check that `α` holds wherever the KB holds. KB: *If it rains the grass is wet* (`R ⇒ W`), *the sprinkler is on or it rains* (`S ∨ R`), *the sprinkler is off* (`¬S`).")
    yield code('''
        from itertools import product

        SYMBOLS = ["R", "S", "W"]
        implies = lambda a, b: (not a) or b
        KB = [lambda m: implies(m["R"], m["W"]),
              lambda m: m["S"] or m["R"],
              lambda m: not m["S"]]

        def entails(kb, query):
            models = [dict(zip(SYMBOLS, values)) for values in product([False, True], repeat=len(SYMBOLS))]
            kb_models = [m for m in models if all(sentence(m) for sentence in kb)]
            return all(query(m) for m in kb_models), len(models), len(kb_models)

        print(entails(KB, lambda m: m["W"]))        # (True, 8, 1) ← KB ⊨ W: in the only KB-model the grass is wet
        print(entails(KB, lambda m: m["S"]))        # (False, 8, 1)

        valid = lambda f: all(f(*v) for v in product([False, True], repeat=2))
        print(valid(lambda p, q: implies(p, q) == implies(not q, not p)))    # True ← contraposition is valid
        print(valid(lambda p, q: implies(p, q) == implies(q, p)))            # False ← the converse is not
    ''')
    yield p("Model checking is exact but costs `O(2ⁿ)` for `n` symbols. Real systems use **theorem proving** (inference rules) or **SAT solvers**, which search the models cleverly.")
    yield section("Standard equivalences", "equal")
    yield table(
        ["Name", "Equivalence"],
        ["Implication elimination", "`P ⇒ Q ≡ ¬P ∨ Q`"],
        ["Contraposition", "`P ⇒ Q ≡ ¬Q ⇒ ¬P`"],
        ["Biconditional elimination", "`P ⇔ Q ≡ (P ⇒ Q) ∧ (Q ⇒ P)`"],
        ["De Morgan", "`¬(P ∧ Q) ≡ ¬P ∨ ¬Q`,   `¬(P ∨ Q) ≡ ¬P ∧ ¬Q`"],
        ["Double negation", "`¬¬P ≡ P`"],
        ["Distributivity", "`P ∨ (Q ∧ R) ≡ (P ∨ Q) ∧ (P ∨ R)`"],
    )
    yield table(
        ["Inference rule", "From", "Infer"],
        ["**Modus ponens**", "`P ⇒ Q`,  `P`", "`Q`"],
        ["Modus tollens", "`P ⇒ Q`,  `¬Q`", "`¬P`"],
        ["And-elimination", "`P ∧ Q`", "`P`"],
        ["**Resolution**", "`P ∨ Q`,  `¬Q ∨ R`", "`P ∨ R`"],
    )
    yield qa("What is the difference between entailment and inference?",
             "Entailment (`⊨`) is a semantic relationship: α is true in every model of the KB. Inference (`⊢`) is a syntactic procedure that derives sentences. A good inference procedure is sound (derives only entailed sentences) and complete (derives all of them).")
    yield qa("How do you check whether KB entails α?",
             "Either enumerate all models and check α in each model of the KB (truth tables, `O(2ⁿ)`), or show that `KB ∧ ¬α` is unsatisfiable — with resolution or a SAT solver.")


@topic(G, "resolution-chaining", "Resolution, Forward & Backward Chaining", "arrows-split-2")
def _():
    yield lead("Resolution is a single inference rule that is complete for propositional logic when used for proof by contradiction. For the restricted but common **Horn clause** form, forward and backward chaining are simpler and run in linear time.")
    yield section("Converting to CNF", "transform")
    yield p("Resolution works on **conjunctive normal form** (CNF): a conjunction of **clauses**, each a disjunction of literals. Any sentence can be converted:")
    yield steps(
        ("Eliminate ⇔", "`α ⇔ β` → `(α ⇒ β) ∧ (β ⇒ α)`"),
        ("Eliminate ⇒", "`α ⇒ β` → `¬α ∨ β`"),
        ("Move ¬ inwards", "De Morgan and double negation until ¬ applies only to symbols"),
        ("Distribute ∨ over ∧", "`α ∨ (β ∧ γ)` → `(α ∨ β) ∧ (α ∨ γ)`"),
    )
    yield example("`B ⇔ (P ∨ Q)` → `(¬B ∨ P ∨ Q) ∧ (¬P ∨ B) ∧ (¬Q ∨ B)`", "CNF example")
    yield section("Resolution refutation", "scissors")
    yield p("To prove `α`: add `¬α` to the KB's clauses and resolve pairs of clauses with complementary literals. Deriving the **empty clause** (a contradiction) proves `KB ⊨ α`; if no new clauses can be produced, `α` is not entailed.")
    yield code('''
        from itertools import combinations

        def resolve(a, b):
            out = []
            for lit in sorted(a):
                neg = lit[1:] if lit.startswith("~") else "~" + lit
                if neg in b:
                    out.append((a - {lit}) | (b - {neg}))
            return out

        def resolution(clauses, query):
            neg = query[1:] if query.startswith("~") else "~" + query
            clauses = set(clauses) | {frozenset([neg])}              # add the negated goal
            derived = []
            while True:
                new = set()
                for a, b in combinations(sorted(clauses, key=sorted), 2):
                    for r in resolve(a, b):
                        if not r:
                            return True, derived                     # empty clause: contradiction
                        if r not in clauses and r not in new:
                            new.add(frozenset(r))
                            derived.append(sorted(r))
                if not new:
                    return False, derived                            # nothing new: not entailed
                clauses |= new

        # KB:  P ⇒ Q,  Q ⇒ R,  P       as clauses: {¬P, Q}, {¬Q, R}, {P}
        kb = [frozenset({"~P", "Q"}), frozenset({"~Q", "R"}), frozenset({"P"})]
        proved, derived = resolution(kb, "R")
        print(proved, derived)          # True [['Q'], ['R', '~P'], ['~Q'], ['R']]
        print(resolution(kb, "~R")[0])  # False ← R is entailed, so ¬R is not
    ''')
    yield note("Resolution is **refutation-complete**: if `KB ⊨ α`, resolution on `KB ∧ ¬α` will eventually derive the empty clause. Modern **SAT solvers** (DPLL / CDCL, WalkSAT) decide satisfiability of millions of clauses and power hardware verification, planning and scheduling.")
    yield section("Horn clauses, forward and backward chaining", "arrows-right")
    yield define("Definite / Horn clause", "a clause with at most one positive literal — equivalently a rule `A ∧ B ∧ … ⇒ C` or a fact `C`. Inference with Horn clauses takes time linear in the size of the KB and is easy for humans to read.")
    yield p("The textbook KB: `P ⇒ Q`, `L ∧ M ⇒ P`, `B ∧ L ⇒ M`, `A ∧ P ⇒ L`, `A ∧ B ⇒ L`, and facts `A`, `B`.")
    yield code('''
        RULES = [(["P"], "Q"), (["L", "M"], "P"), (["B", "L"], "M"), (["A", "P"], "L"), (["A", "B"], "L")]
        FACTS = ["A", "B"]

        def forward_chain(rules, facts, query):
            known, agenda, order = set(), list(facts), []
            count = {i: len(prem) for i, (prem, _) in enumerate(rules)}    # unsatisfied premises per rule
            while agenda:
                p = agenda.pop(0)
                if p in known:
                    continue
                known.add(p)
                order.append(p)
                if p == query:
                    return True, order
                for i, (prem, concl) in enumerate(rules):
                    if p in prem:
                        count[i] -= 1
                        if count[i] == 0:                                   # all premises known → fire
                            agenda.append(concl)
            return False, order

        def backward_chain(rules, facts, goal, seen=()):
            if goal in facts:
                return True
            if goal in seen:                                                # avoid looping on P ⇒ … ⇒ P
                return False
            return any(all(backward_chain(rules, facts, g, seen + (goal,)) for g in prem)
                       for prem, concl in rules if concl == goal)

        print(forward_chain(RULES, FACTS, "Q"))     # (True, ['A', 'B', 'L', 'M', 'P', 'Q'])
        print(backward_chain(RULES, FACTS, "Q"))    # True
        print(backward_chain(RULES, FACTS, "Z"))    # False ← no rule concludes Z
    ''')
    yield table(
        ["", "Forward chaining", "Backward chaining"],
        ["Direction", "**Data-driven**: from known facts to all consequences", "**Goal-driven**: from the query back to facts"],
        ["Fires", "Every rule whose premises become true", "Only rules relevant to the goal"],
        ["Good for", "Monitoring, reacting to new data, deriving everything", "Answering specific questions"],
        ["Cost", "May derive many irrelevant facts", "Often much less than linear in KB size"],
        ["Used in", "Production systems, expert-system shells (CLIPS), Datalog", "Prolog, diagnostic systems (MYCIN)"],
    )
    yield qa("Explain resolution refutation.",
             "Convert KB ∧ ¬α to CNF, then repeatedly resolve pairs of clauses containing a literal and its negation, adding the resolvents. Deriving the empty clause shows KB ∧ ¬α is unsatisfiable, so KB ⊨ α. It's sound and refutation-complete.")
    yield qa("Forward vs backward chaining — when to use which?",
             "Forward chaining is data-driven: good when new facts arrive and you want all consequences (alerting, production systems). Backward chaining is goal-driven: good for answering a specific query, since it only explores rules relevant to the goal (Prolog, diagnosis).")
    yield qa("What is a Horn clause and why does it matter?",
             "A clause with at most one positive literal, i.e. a rule with a single conclusion or a fact. With Horn clauses, entailment can be decided in linear time using forward or backward chaining, instead of the exponential worst case of general propositional inference.")


@topic(G, "first-order-logic", "First-Order Logic & Unification", "variable")
def _():
    yield lead("Propositional logic needs a separate symbol for every fact. First-order logic (FOL) adds **objects, relations, functions and quantifiers**, so one sentence can say something about *all* objects — “every king is a person”.")
    yield table(
        ["Element", "Examples", "Denotes"],
        ["Constant symbols", "`John`, `Richard`, `2`", "Objects"],
        ["Predicate symbols", "`King(x)`, `Brother(x, y)`, `>`", "Relations (true/false)"],
        ["Function symbols", "`LeftLeg(x)`, `Mother(x)`, `+`", "Functions returning objects"],
        ["Variables", "`x`, `y`", "Range over objects"],
        ["Quantifiers", "`∀x` (for all), `∃x` (there exists)", "Generality"],
        ["Equality", "`Father(John) = Henry`", "Two terms name the same object"],
    )
    yield section("Translating English", "language")
    yield table(
        ["English", "First-order logic"],
        ["All kings are persons", "`∀x King(x) ⇒ Person(x)`"],
        ["King John has a crown on his head", "`∃x Crown(x) ∧ OnHead(x, John)`"],
        ["Everybody loves somebody", "`∀x ∃y Loves(x, y)`"],
        ["There is someone who is loved by everyone", "`∃y ∀x Loves(x, y)`"],
        ["Nobody likes taxes", "`¬∃x Likes(x, Taxes)` ≡ `∀x ¬Likes(x, Taxes)`"],
        ["Brothers are siblings", "`∀x, y Brother(x, y) ⇒ Sibling(x, y)`"],
    )
    yield dodont("Pair `∀` with `⇒` and `∃` with `∧`: `∀x King(x) ⇒ Person(x)`; `∃x Crown(x) ∧ OnHead(x, John)`.",
                 "`∀x King(x) ∧ Person(x)` (says *everything* is a king) or `∃x Crown(x) ⇒ OnHead(x, John)` (true as soon as anything is not a crown).")
    yield note("Quantifier order matters: `∀x ∃y Loves(x, y)` (everyone loves someone, maybe different people) is much weaker than `∃y ∀x Loves(x, y)` (one person loved by all). Duality: `¬∀x P ≡ ∃x ¬P` and `¬∃x P ≡ ∀x ¬P`.")
    yield section("Unification", "link")
    yield define("Unification", "finding a substitution θ that makes two expressions identical: `Unify(p, q) = θ` where `Subst(θ, p) = Subst(θ, q)`. The **most general unifier** (MGU) commits to as little as possible.")
    yield code('''
        def is_var(t):
            return isinstance(t, str) and t[0].islower()        # variables: lowercase; constants: Capitalised

        def substitute(t, theta):
            if is_var(t):
                return substitute(theta[t], theta) if t in theta else t
            if isinstance(t, tuple):
                return tuple(substitute(a, theta) for a in t)
            return t

        def occurs(var, t, theta):
            t = substitute(t, theta)
            return t == var or (isinstance(t, tuple) and any(occurs(var, a, theta) for a in t))

        def unify(x, y, theta):
            if theta is None:
                return None
            x, y = substitute(x, theta), substitute(y, theta)
            if x == y:
                return theta
            if is_var(x):
                return None if occurs(x, y, theta) else {**theta, x: y}      # occurs check
            if is_var(y):
                return unify(y, x, theta)
            if isinstance(x, tuple) and isinstance(y, tuple) and len(x) == len(y):
                for a, b in zip(x, y):
                    theta = unify(a, b, theta)
                return theta
            return None

        def show(theta):
            return theta if theta is None else {v: substitute(v, theta) for v in theta}

        q = ("Knows", "John", "x")
        print(show(unify(q, ("Knows", "John", "Jane"), {})))               # {'x': 'Jane'}
        print(show(unify(q, ("Knows", "y", "Bill"), {})))                  # {'y': 'John', 'x': 'Bill'}
        print(show(unify(q, ("Knows", "y", ("Mother", "y")), {})))         # {'y': 'John', 'x': ('Mother', 'John')}
        print(show(unify(q, ("Knows", "x", "Elizabeth"), {})))             # None ← x can't be John and Elizabeth
        print(show(unify(q, ("Knows", "x2", "Elizabeth"), {})))            # {'x2': 'John', 'x': 'Elizabeth'} ← fixed by standardising apart
    ''')
    yield section("Inference in FOL", "arrows-right")
    yield p("**Generalised modus ponens** lifts modus ponens with unification: from `King(John)`, `Greedy(y)` and `∀x King(x) ∧ Greedy(x) ⇒ Evil(x)`, unify to `θ = {x/John, y/John}` and infer `Evil(John)` — only if `Greedy(John)` also unifies. Forward chaining with it gives Datalog-style reasoning. The classic crime KB:")
    yield code('''
        FACTS = {("American", "West"), ("Missile", "M1"), ("Owns", "Nono", "M1"), ("Enemy", "Nono", "America")}
        RULES = [
            ([("American", "x"), ("Weapon", "y"), ("Sells", "x", "y", "z"), ("Hostile", "z")], ("Criminal", "x")),
            ([("Missile", "x"), ("Owns", "Nono", "x")], ("Sells", "West", "x", "Nono")),
            ([("Missile", "x")], ("Weapon", "x")),
            ([("Enemy", "x", "America")], ("Hostile", "x")),
        ]

        def match(pattern, fact, theta):                   # one-way unification: variables only in the pattern
            if len(pattern) != len(fact) or pattern[0] != fact[0]:
                return None
            theta = dict(theta)
            for p, f in zip(pattern[1:], fact[1:]):
                if p[0].islower():
                    if theta.setdefault(p, f) != f:
                        return None
                elif p != f:
                    return None
            return theta

        def solutions(premises, facts, theta):
            if not premises:
                yield theta
                return
            for fact in sorted(facts):
                t = match(premises[0], fact, theta)
                if t is not None:
                    yield from solutions(premises[1:], facts, t)

        def forward_chain(facts, rules):
            facts, rounds = set(facts), []
            while True:
                new = {tuple(theta.get(a, a) for a in concl)
                       for prem, concl in rules for theta in solutions(prem, facts, {})} - facts
                if not new:
                    return facts, rounds
                rounds.append(sorted(new))
                facts |= new

        facts, rounds = forward_chain(FACTS, RULES)
        print(rounds[0])                                   # [('Hostile', 'Nono'), ('Sells', 'West', 'M1', 'Nono'), ('Weapon', 'M1')]
        print(rounds[1])                                   # [('Criminal', 'West')]
        print(("Criminal", "West") in facts)               # True
    ''')
    yield table(
        ["Method", "How", "Used in"],
        ["Forward chaining", "Generalised modus ponens from facts until nothing new", "Datalog, production systems, deductive databases"],
        ["Backward chaining", "Depth-first from the goal, unifying with rule heads", "**Prolog**, logic programming"],
        ["Resolution", "Convert to clausal form (Skolemise ∃), resolve with unification", "Automated theorem provers (Vampire, E)"],
    )
    yield warn("FOL entailment is only **semi-decidable**: if `KB ⊨ α` a complete procedure will eventually say so, but if not it may run forever. That's why practical systems restrict the language (Horn clauses, Datalog, description logics).")
    yield qa("Why is first-order logic more expressive than propositional logic?",
             "It has objects, relations, functions and quantifiers, so general rules (`∀x King(x) ⇒ Person(x)`) replace one propositional symbol per individual fact. It can describe infinite domains that propositional logic cannot.")
    yield qa("What does unification do? Give an example.",
             "It finds the most general substitution making two expressions identical. `Knows(John, x)` and `Knows(y, Mother(y))` unify with `{y/John, x/Mother(John)}`. It's the core step of generalised modus ponens, Prolog and resolution.")
    yield qa("What is the occurs check?",
             "Before binding a variable `x` to a term, check that `x` does not occur inside that term — otherwise `x = F(x)` would create an infinite term. Prolog omits it by default for speed.")


@topic(G, "knowledge-representation", "Knowledge Representation & Expert Systems", "books")
def _():
    yield lead("Knowledge representation (KR) is about organising what an agent knows — categories, objects, properties, defaults and rules — so that inference is efficient. Expert systems were AI's first big commercial success, and today's knowledge graphs are their descendants.")
    yield section("Main representation schemes", "layout-grid")
    yield cards(
        ("Semantic networks", "A graph: nodes are objects/categories, labelled edges are relations (`is-a`, `part-of`, `has`). Properties are **inherited** down `is-a` links. Easy to visualise; weak on negation and quantifiers.", "affiliate"),
        ("Frames", "Record-like structures (Minsky, 1974): a frame for *Restaurant* has **slots** (cuisine, price) with **default** values and procedures (“if-needed”). The ancestor of objects and classes in OOP.", "id"),
        ("Ontologies", "A formal, shared vocabulary of categories and relations for a domain. Upper ontologies define general concepts (events, time, physical objects); OWL/RDF encode them as triples; description logics give decidable reasoning.", "hierarchy-3"),
        ("Rules / production systems", "IF-THEN rules over a working memory of facts, fired by an inference engine (forward or backward chaining). Conflict resolution picks which matching rule fires; the Rete algorithm matches efficiently.", "list-check"),
        cols=2,
    )
    yield section("Inheritance with exceptions", "affiliate")
    yield code('''
        # a semantic network as (subject, relation, object) triples
        TRIPLES = [
            ("Bird", "is-a", "Animal"), ("Animal", "breathes", True),
            ("Bird", "can-fly", True), ("Bird", "has", "feathers"),
            ("Penguin", "is-a", "Bird"), ("Penguin", "can-fly", False),     # an exception overrides the default
            ("Tweety", "instance-of", "Bird"), ("Pingu", "instance-of", "Penguin"),
        ]

        def lookup(entity, attribute):
            node = entity
            while node:
                for s, r, o in TRIPLES:
                    if s == node and r == attribute:
                        return o                           # the most specific value wins
                parents = [o for s, r, o in TRIPLES if s == node and r in ("is-a", "instance-of")]
                node = parents[0] if parents else None     # climb the is-a hierarchy
            return None

        print(lookup("Tweety", "can-fly"), lookup("Pingu", "can-fly"))     # True False
        print(lookup("Pingu", "has"), lookup("Pingu", "breathes"))         # feathers True ← inherited from Bird and Animal
    ''')
    yield p("This is **default (non-monotonic) reasoning**: birds fly *unless* we learn otherwise. Classical logic is *monotonic* — adding facts never removes conclusions — so defaults need special logics (default logic, circumscription) or the inheritance trick above.")
    yield section("Expert systems", "stethoscope")
    yield table(
        ["Component", "Role"],
        ["**Knowledge base**", "Domain rules and facts captured from human experts"],
        ["**Inference engine**", "Applies the rules (forward or backward chaining) to the case at hand"],
        ["**Working memory**", "Facts about the current case (symptoms, test results)"],
        ["**Explanation facility**", "Answers *why* a question is asked and *how* a conclusion was reached"],
        ["**Knowledge-acquisition interface**", "Lets experts and engineers add and edit rules"],
    )
    yield code('''
        RULES = [
            ("R1", {"fever", "cough"}, "flu-suspected"),
            ("R2", {"flu-suspected", "short-of-breath"}, "refer-to-doctor"),
            ("R3", {"sneezing", "itchy-eyes"}, "allergy-suspected"),
        ]

        def diagnose(symptoms):
            facts, how = set(symptoms), {}
            changed = True
            while changed:                                  # forward chaining until nothing new fires
                changed = False
                for name, conditions, conclusion in RULES:
                    if conditions <= facts and conclusion not in facts:
                        facts.add(conclusion)
                        how[conclusion] = f"{name}: {' + '.join(sorted(conditions))}"
                        changed = True
            return how

        result = diagnose({"fever", "cough", "short-of-breath"})
        print(list(result))                         # ['flu-suspected', 'refer-to-doctor']
        print(result["refer-to-doctor"])            # R2: flu-suspected + short-of-breath ← the "how" explanation
    ''')
    yield table(
        ["System", "Domain", "Note"],
        ["DENDRAL (1965)", "Inferring molecular structure from mass spectra", "First expert system"],
        ["MYCIN (1970s)", "Diagnosing blood infections, recommending antibiotics", "Hundreds of backward-chaining rules with **certainty factors**; matched specialists but was never used clinically"],
        ["XCON / R1 (1980)", "Configuring DEC VAX computers", "Saved DEC an estimated $40M a year; grew to thousands of rules"],
    )
    yield warn("Why expert systems faded: the **knowledge-acquisition bottleneck** (experts can't articulate everything), brittleness outside their narrow rules, no learning, and heavy maintenance as rule bases grew. Machine learning replaced much of this — but rule engines still run business logic, and **knowledge graphs** (Wikidata, Google Knowledge Graph) ground search and LLM answers (retrieval-augmented generation).")
    yield section("Hard problems in KR", "alert-triangle")
    yield table(
        ["Problem", "Description"],
        ["**Frame problem**", "Representing what does *not* change when an action happens without writing an axiom for every unaffected fact"],
        ["**Qualification problem**", "Listing every precondition of an action is impossible (the car starts… unless the battery is dead, the tank empty, a potato in the exhaust…)"],
        ["**Closed-world assumption**", "Databases and Prolog treat anything not known to be true as false — convenient, but not valid for open worlds like the web"],
        ["**Common sense**", "Vast everyday knowledge (water is wet, people have one mother) that is hard to write down — the target of projects like Cyc"],
    )
    yield qa("Compare semantic networks and frames.",
             "Both organise knowledge around objects and categories with inheritance. Semantic networks emphasise relations as labelled graph edges; frames bundle an object's properties into slots with defaults and attached procedures. They are largely interchangeable and both map to subsets of first-order logic.")
    yield qa("What are the components of an expert system?",
             "A knowledge base of rules, an inference engine (forward/backward chaining), working memory for case facts, an explanation facility, and a knowledge-acquisition interface. The user interface asks questions and presents conclusions.")


@topic(G, "classical-planning", "Classical Planning (STRIPS & PDDL)", "list-check")
def _():
    yield lead("Planning finds a sequence of actions that achieves a goal, using a **factored** representation: states are sets of facts and actions are schemas with preconditions and effects. That structure allows domain-independent heuristics that make planners scale to huge problems.")
    yield section("The STRIPS representation", "file-code")
    yield table(
        ["Part", "Meaning", "Blocks world"],
        ["State", "Conjunction of ground facts (fluents); everything else is false (closed world)", "`On(C, A) ∧ OnTable(A) ∧ OnTable(B) ∧ Clear(C) ∧ Clear(B)`"],
        ["Goal", "Conjunction of facts that must hold (a partial state)", "`On(A, B) ∧ On(B, C)`"],
        ["Action schema", "Name, **preconditions**, **add list**, **delete list**", "`Move(b, x, y)`"],
    )
    yield p("An action is applicable when its preconditions hold; its result is `(state − delete list) ∪ add list`. Facts not mentioned stay unchanged — this is how STRIPS sidesteps the frame problem. **PDDL** (Planning Domain Definition Language) is the standard modern syntax:")
    yield output('''
        (:action move
          :parameters (?b ?x ?y)
          :precondition (and (on ?b ?x) (clear ?b) (clear ?y))
          :effect (and (on ?b ?y) (clear ?x)
                       (not (on ?b ?x)) (not (clear ?y))))
    ''', "PDDL")
    yield section("Forward (progression) planning", "arrow-right")
    yield p("Treat planning as search: states are fact sets, successors come from applicable ground actions. Here is the **Sussman anomaly** — start with C on A; goal A on B on C:")
    yield code('''
        from collections import deque

        BLOCKS = ["A", "B", "C"]
        PLACES = BLOCKS + ["Table"]

        def ground_actions():                               # every instance of Move(b, x, y)
            for b in BLOCKS:
                for x in PLACES:
                    for y in PLACES:
                        if len({b, x, y}) == 3:
                            pre = {("On", b, x), ("Clear", b)} | ({("Clear", y)} if y != "Table" else set())
                            add = {("On", b, y)} | ({("Clear", x)} if x != "Table" else set())
                            delete = {("On", b, x)} | ({("Clear", y)} if y != "Table" else set())
                            yield f"Move({b},{x},{y})", frozenset(pre), frozenset(add), frozenset(delete)

        ACTIONS = list(ground_actions())

        def plan(start, goal):                              # breadth-first progression search
            frontier, seen = deque([(start, [])]), {start}
            while frontier:
                state, steps = frontier.popleft()
                if goal <= state:
                    return steps, len(seen)
                for name, pre, add, delete in ACTIONS:
                    if pre <= state:
                        nxt = (state - delete) | add
                        if nxt not in seen:
                            seen.add(nxt)
                            frontier.append((nxt, steps + [name]))

        start = frozenset({("On", "C", "A"), ("On", "A", "Table"), ("On", "B", "Table"), ("Clear", "C"), ("Clear", "B")})
        goal = {("On", "A", "B"), ("On", "B", "C")}
        print(len(ACTIONS))           # 18 ← ground actions from one schema
        print(plan(start, goal))      # (['Move(C,A,Table)', 'Move(B,Table,C)', 'Move(A,Table,B)'], 13)
    ''')
    yield note("The Sussman anomaly defeats planners that achieve goals **one at a time**: stacking A on B first (after clearing C) must be undone to get B onto C, and achieving B on C first buries A. The goals interact, so a planner must interleave them.")
    yield section("Search strategies and heuristics", "route")
    yield table(
        ["Approach", "Idea"],
        ["**Forward (progression)** search", "From the initial state apply applicable actions. Many irrelevant actions — needs a good heuristic."],
        ["**Backward (regression)** search", "From the goal, consider only *relevant* actions (that add a goal fact without deleting another); regress the goal through them. Smaller branching factor."],
        ["**Ignore-delete-lists** heuristic", "Solve the relaxed problem where actions never remove facts (the basis of FF and HSP planners). Admissible variants give A*-optimal plans."],
        ["**Ignore-preconditions** heuristic", "Count how many actions are needed if any action could always be applied — roughly the number of unsatisfied goals."],
        ["**Planning graphs / GraphPlan**", "Layered graph of reachable facts and actions with mutex links; the level where all goals first appear is a heuristic estimate."],
        ["**SAT planning**", "Encode “is there a plan of length `T`?” as a Boolean formula and hand it to a SAT solver."],
    )
    yield section("Partial-order planning", "git-branch")
    yield p("A **partial-order planner** (POP) searches in the space of *plans*, not states, and commits to an ordering only when necessary (**least commitment**). A plan has actions, ordering constraints `A ≺ B`, and **causal links** `A →p→ B` (A achieves precondition `p` of B). A **threat** is an action that could delete `p` between A and B — resolved by ordering it before A (demotion) or after B (promotion).")
    yield example("Putting on shoes: `RightSock ≺ RightShoe` and `LeftSock ≺ LeftShoe`, but the left and right sides are unordered — the plan allows any of the 6 interleavings.", "Least commitment")
    yield table(
        ["Beyond classical planning", "Handles"],
        ["Hierarchical task networks (HTN)", "High-level actions refined into sub-plans — how most real planners (and games' NPCs) work"],
        ["Scheduling with resources", "Durations, deadlines, limited machines/crew — critical-path method"],
        ["Contingent / conformant planning", "Partial observability: plans with sensing actions and branches"],
        ["Replanning & execution monitoring", "Detect when the world deviates from the plan and repair it"],
        ["MDPs (next group)", "Stochastic action outcomes — a *policy* instead of a fixed sequence"],
    )
    yield qa("What is STRIPS?",
             "A planning representation where states are sets of ground facts and each action has preconditions, an add list and a delete list. Anything not mentioned is unchanged, which avoids writing frame axioms. PDDL is its modern, more expressive successor.")
    yield qa("Forward vs backward state-space planning?",
             "Forward search starts from the initial state and applies applicable actions — simple but branches on many irrelevant actions. Backward (regression) search starts from the goal and only considers relevant actions, giving a smaller branching factor, but works on sets of states and makes heuristics harder.")
    yield qa("Why can planning use domain-independent heuristics while plain search cannot?",
             "The factored representation exposes the structure of actions, so a planner can automatically build relaxed problems — ignoring delete lists or preconditions — and solve them to get heuristic estimates without any domain-specific coding.")
