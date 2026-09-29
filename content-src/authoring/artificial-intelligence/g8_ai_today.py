from kit import *

G = "AI Today"


@topic(G, "modern-ai-landscape", "The Modern AI Landscape", "world")
def _():
    yield lead("Today “AI” usually means machine learning, and especially deep learning and large language models. But the classical ideas in these notes — search, constraints, logic, probability, decision theory — are still inside modern systems, often combined with learned components.")
    yield section("How the pieces fit", "map")
    yield table(
        ["Paradigm", "Knowledge comes from", "Core techniques", "Where to read more"],
        ["Search & planning", "A problem formulation", "BFS/A*, alpha-beta, MCTS, STRIPS planners, CSP solvers", "This subject"],
        ["Logic & knowledge", "Hand-written facts and rules", "Resolution, chaining, ontologies, knowledge graphs", "This subject"],
        ["Probabilistic reasoning", "Expert-built or learned models", "Bayesian networks, HMMs, MDPs", "This subject"],
        ["Machine learning", "Labelled/unlabelled data", "Regression, trees, SVMs, clustering, evaluation", "**Machine Learning**, **Data Science**"],
        ["Deep learning", "Large datasets + gradient descent", "CNNs, RNNs, Transformers, generative models", "**Deep Learning**"],
        ["Generative AI / LLMs", "Web-scale pretraining + fine-tuning + RLHF", "Prompting, RAG, agents, evaluation", "**Generative AI**"],
        ["Reinforcement learning", "Interaction and reward", "Q-learning, policy gradients, self-play", "This subject (intro) + **Deep Learning**"],
    )
    yield section("Classical AI inside modern systems", "puzzle")
    yield table(
        ["Classical idea", "Still used in"],
        ["A* and graph search", "Maps and ride-hailing routing, game path-finding, robot motion planning"],
        ["Minimax / MCTS", "Chess engines (Stockfish: alpha-beta + a neural evaluation), AlphaZero, game AI"],
        ["Constraint solving & SAT", "Airline crew and timetable scheduling, chip verification, package managers' dependency resolution"],
        ["Planning (PDDL/HTN)", "Logistics, space missions, NPC behaviour in games, LLM agents that decompose tasks"],
        ["Logic & knowledge graphs", "Search-engine knowledge panels, business rules engines, grounding LLM answers (RAG over graphs)"],
        ["Bayesian reasoning & HMMs", "Spam filters, medical decision support, Kalman/particle filters in robots and GPS"],
        ["MDPs & RL", "Recommendation, ad bidding, robotics, and RLHF for aligning LLMs"],
        ["Beam search", "Decoding text in translation and speech models"],
    )
    yield note("An **LLM agent** is the agent loop from the **Intelligent Agents** topic with an LLM as the decision-maker: it perceives (reads tool results), keeps state (memory), reasons toward a goal (plans), and acts (calls tools). Adding classical search or verification on top of LLM proposals is an active research area — *neuro-symbolic* AI.")
    yield section("Natural language processing", "language")
    yield table(
        ["Era", "Approach", "Example"],
        ["1960s–80s", "Hand-written rules and grammars", "ELIZA, SHRDLU"],
        ["1990s–2000s", "Statistical: n-gram language models, HMMs, CRFs", "Statistical machine translation, POS tagging"],
        ["2013–2017", "Word embeddings + RNN/LSTM sequence models", "word2vec, seq2seq translation"],
        ["2018–now", "Pretrained Transformers, then LLMs", "BERT, GPT family, instruction-tuned chat models"],
    )
    yield p("The idea behind every language model is the same — predict the next word from the context. A bigram model is the smallest version:")
    yield code('''
        from collections import Counter, defaultdict

        corpus = "the cat sat on the mat . the cat ate the fish . the dog sat on the log .".split()
        bigrams = defaultdict(Counter)
        for w1, w2 in zip(corpus, corpus[1:]):
            bigrams[w1][w2] += 1

        def next_word_probs(word):
            counts = bigrams[word]
            total = sum(counts.values())
            return {w: round(c / total, 2) for w, c in counts.most_common()}

        def generate(word, n=5):
            out = [word]
            for _ in range(n):
                word = bigrams[word].most_common(1)[0][0]     # greedy decoding
                out.append(word)
            return " ".join(out)

        print(next_word_probs("the"))     # {'cat': 0.33, 'mat': 0.17, 'fish': 0.17, 'dog': 0.17, 'log': 0.17}
        print(generate("dog"))            # dog sat on the cat sat ← greedy decoding soon loops
    ''')
    yield p("An LLM replaces the one-word context with thousands of tokens and the count table with a Transformer of billions of parameters — see the **Deep Learning** (Transformers) and **Generative AI** notes.")
    yield table(
        ["NLP task", "Input → output"],
        ["Classification (sentiment, spam, intent)", "Text → label"],
        ["Named-entity recognition, POS tagging", "Text → label per token"],
        ["Machine translation, summarisation", "Text → text"],
        ["Question answering, retrieval", "Question (+ documents) → answer"],
        ["Speech recognition / synthesis", "Audio ↔ text"],
    )
    yield section("Computer vision", "eye")
    yield table(
        ["Task", "Output", "Typical models"],
        ["Image classification", "One label per image", "CNNs (ResNet), Vision Transformers"],
        ["Object detection", "Boxes + labels", "YOLO, DETR"],
        ["Segmentation", "A label per pixel (semantic / instance)", "U-Net, Mask R-CNN, SAM"],
        ["Tracking, pose, depth", "Trajectories, keypoints, 3-D structure", "Specialised CNN/Transformer heads"],
        ["Generation & editing", "New images", "Diffusion models"],
        ["Vision–language", "Captions, answers about images", "CLIP-style encoders, multimodal LLMs"],
    )
    yield p("Vision went through the same shift as NLP: hand-designed features (edges, SIFT, HOG) + a classifier, replaced after 2012 by features *learned* end-to-end by CNNs, and more recently by Transformers and multimodal models.")
    yield chips("robotics", "speech", "recommender systems", "autonomous vehicles", "multi-agent systems", "AI for science (protein folding)", "neuro-symbolic AI")
    yield qa("Is classical (symbolic) AI obsolete now that we have deep learning?",
             "No. Learning excels at perception and pattern-matching from data; search, planning, constraint solving and logic excel at exact, verifiable reasoning over explicit structure. Strong systems combine them — AlphaZero (MCTS + networks), LLM agents with planners and tools, RAG over knowledge graphs.")
    yield qa("What is the difference between narrow AI systems today and AGI?",
             "Today's systems — even broad LLMs — are trained for particular distributions of tasks and fail in unfamiliar ways (hallucination, brittle planning). AGI would learn and perform essentially any intellectual task a human can, adapting robustly to new situations. Whether scaling current methods leads there is debated.")


@topic(G, "ai-ethics-safety", "AI Ethics, Safety & Fairness", "scale")
def _():
    yield lead("AI systems make or influence decisions about loans, jobs, medical care and what people see. Building them responsibly means asking not only *does it work?* but *for whom, with what failures, and who is accountable?*")
    yield section("Core principles", "list-check")
    yield cards(
        ("Fairness", "Outcomes shouldn't systematically disadvantage groups defined by race, gender, age, disability…", "users"),
        ("Transparency & explainability", "People affected should know AI is used and get understandable reasons for decisions.", "eye"),
        ("Privacy", "Data is collected with consent, minimised and protected; models shouldn't leak training data.", "lock"),
        ("Safety & robustness", "Systems behave reliably under distribution shift, adversarial inputs and misuse.", "shield-check"),
        ("Accountability", "A human or organisation is answerable for the system's decisions; there are audit trails and appeals.", "gavel"),
        ("Human oversight", "Humans can monitor, override or switch off the system, especially in high-stakes uses.", "user-check"),
        cols=3,
    )
    yield section("Where bias comes from", "filter")
    yield table(
        ["Source", "Example"],
        ["**Historical bias**", "Past hiring data reflects past discrimination; a model trained on it reproduces it"],
        ["**Representation / sampling bias**", "Face datasets with few darker-skinned faces → higher error rates for those groups"],
        ["**Measurement bias**", "Using arrests as a proxy for crime, or health spending as a proxy for health need"],
        ["**Proxy features**", "Removing “race” doesn't help if postcode or name still encodes it"],
        ["**Feedback loops**", "Predictive policing sends officers where arrests were recorded, generating more records there"],
    )
    yield section("Measuring fairness", "chart-bar")
    yield code('''
        # (group, true label, model prediction) for a toy loan-approval model; 1 = approve / would repay
        data = [("A", 1, 1), ("A", 1, 1), ("A", 1, 0), ("A", 0, 1), ("A", 0, 0), ("A", 0, 0),
                ("B", 1, 1), ("B", 1, 0), ("B", 1, 0), ("B", 0, 0), ("B", 0, 0), ("B", 0, 0)]

        def rates(group):
            rows = [(y, p) for g, y, p in data if g == group]
            selection = sum(p for _, p in rows) / len(rows)                   # P(approve)
            positives = [p for y, p in rows if y == 1]
            tpr = sum(positives) / len(positives)                              # P(approve | would repay)
            return selection, tpr

        a, b = rates("A"), rates("B")
        print([round(x, 2) for x in a], [round(x, 2) for x in b])   # [0.5, 0.67] [0.17, 0.33] ← [selection rate, true-positive rate]
        print(round(b[0] / a[0], 2))                          # 0.33 ← disparate impact ratio (the "80% rule" flags < 0.8)
        print(round(a[1] - b[1], 2))                          # 0.33 ← equal-opportunity gap in true-positive rate
    ''')
    yield table(
        ["Criterion", "Requires equal across groups", "Intuition"],
        ["Demographic parity", "Selection rate `P(ŷ = 1)`", "Same share of each group approved"],
        ["Equal opportunity", "True-positive rate `P(ŷ = 1 | y = 1)`", "Qualified people approved equally often"],
        ["Equalised odds", "TPR **and** false-positive rate", "Equal error rates of both kinds"],
        ["Predictive parity / calibration", "`P(y = 1 | ŷ = 1)` or scores mean the same", "An approval means the same thing for everyone"],
    )
    yield warn("These criteria **cannot all hold at once** when base rates differ between groups (the impossibility results of Kleinberg et al. and Chouldechova, 2016–17). Choosing a fairness metric is a value judgement about the application, not a purely technical choice.")
    yield section("Safety and alignment", "shield")
    yield table(
        ["Risk", "What it looks like", "Mitigation"],
        ["**Specification gaming / reward hacking**", "The system optimises the literal objective, not the intent (see **Reinforcement Learning**)", "Careful objectives, human feedback, red-teaming"],
        ["**Distribution shift**", "A model trained on one hospital's scans fails at another", "Monitoring, robust evaluation, domain adaptation"],
        ["**Adversarial examples**", "Tiny pixel changes flip a classifier; prompt injection hijacks an LLM agent", "Adversarial training, input validation, least-privilege tools"],
        ["**Hallucination / overconfidence**", "Fluent but false answers", "Retrieval grounding, calibrated uncertainty, citations, human review"],
        ["**Misuse**", "Deepfakes, fraud, disinformation, cyber-attacks", "Usage policies, watermarking, access controls"],
        ["**Alignment of capable systems**", "Goals that diverge from human values; hard to correct once deployed", "Interpretability, scalable oversight, evaluations before release"],
    )
    yield section("Governance", "building-bank")
    yield table(
        ["Framework", "Key idea"],
        ["**EU AI Act** (in force 2024, phased in to 2026–27)", "Risk tiers: *unacceptable* (banned, e.g. social scoring), *high-risk* (hiring, credit, medical — strict obligations), *limited* (transparency, e.g. chatbots must disclose), *minimal*; extra duties for general-purpose models"],
        ["NIST AI Risk Management Framework (2023)", "Voluntary US framework: Govern, Map, Measure, Manage"],
        ["OECD / UNESCO AI principles", "International baselines for trustworthy, human-centred AI"],
        ["Model cards & datasheets", "Documentation of intended use, training data, evaluation by subgroup and limitations"],
    )
    yield dodont("Evaluate performance **per subgroup**, document data and limits, keep a human in the loop for high-stakes decisions, and monitor after deployment.",
                 "Assume a model is fair because the protected attribute was dropped, or ship without a way to appeal or override its decisions.")
    yield p("The **Machine Learning** notes' *Responsible AI & Ethics* topic covers the practical checklist for ML projects in more depth.")
    yield qa("How can a model be biased if it never sees the protected attribute?",
             "Other features act as proxies (postcode, name, school), and the labels themselves may encode historical discrimination. Fairness must be measured on outcomes per group, not assumed from the input list.")
    yield qa("What is the alignment problem?",
             "Making sure an AI system pursues the goals its designers and users actually intend, including unstated constraints — rather than a literal proxy objective. It grows harder as systems become more capable and autonomous.")
    yield qa("Name two fairness metrics and explain why they can conflict.",
             "Demographic parity (equal approval rates) and equal opportunity (equal true-positive rates). If qualified-applicant base rates differ between groups, a perfectly accurate model satisfies equal opportunity but violates demographic parity; forcing parity then changes error rates for some group.")


@topic(G, "ai-interview-questions", "Interview Questions", "message-question")
def _():
    yield lead("Classical AI questions from university exams and ML/AI engineer interviews — short answers you can say out loud, with pointers to the topic that explains each one.")
    yield section("Foundations", "brain")
    yield qa("What is an intelligent agent? What makes it rational?",
             "Anything that perceives its environment through sensors and acts through actuators. It is rational if, for each percept sequence, it chooses the action expected to maximise its performance measure given its percepts and built-in knowledge. (See **Intelligent Agents & Environments**.)")
    yield qa("Describe the task environment of a self-driving car.",
             "PEAS — performance: safety, time, legality, comfort; environment: roads, traffic, pedestrians, weather; actuators: steering, throttle, brake, signals; sensors: cameras, LiDAR, radar, GPS. It is partially observable, multi-agent, stochastic, sequential, dynamic, continuous.")
    yield qa("Name the five agent architectures.",
             "Simple reflex, model-based reflex, goal-based, utility-based and learning agents — each adds internal state, goals, preferences or self-improvement to the previous one.")
    yield section("Search", "route")
    yield qa("Compare BFS, DFS, UCS and iterative deepening.",
             "BFS: complete, optimal for unit costs, `O(bᵈ)` time and memory. DFS: `O(bm)` memory but not complete or optimal. UCS: optimal for any positive costs, expands by path cost. IDDFS: BFS's guarantees with DFS's memory, at ~11% extra time for `b = 10`. (See **Depth-Limited, Iterative Deepening & Bidirectional Search**.)")
    yield qa("Why is A* optimal, and what conditions does the heuristic need?",
             "It expands nodes in order of `f = g + h`. With an admissible `h` it can never pop a suboptimal goal before some node on the optimal path; graph search additionally needs consistency so the first path found to every state is its cheapest.")
    yield qa("How would you design a heuristic for a new problem?",
             "Relax the problem — remove constraints until it is easy to solve exactly — and use the relaxed optimal cost (Manhattan distance, straight-line distance, ignore-delete-lists). Combine several admissible heuristics with `max`, or precompute pattern databases.")
    yield qa("When would you use local search instead of systematic search?",
             "When only the final state matters, the space is huge or continuous, and a good (not necessarily optimal) solution is enough — scheduling, layout, n-queens with millions of queens. Hill climbing with restarts, simulated annealing or genetic algorithms.")
    yield section("Games & CSPs", "chess")
    yield qa("Explain alpha-beta pruning and its best case.",
             "Minimax with bounds α (MAX's guaranteed value) and β (MIN's). When `α ≥ β` the rest of a node's children can't affect the decision and are skipped. With perfect move ordering the cost falls from `O(bᵐ)` to `O(b^(m/2))`, doubling the searchable depth.")
    yield qa("Why did Go need MCTS instead of alpha-beta?",
             "Go's branching factor (~250) makes full-width search shallow, and good evaluation functions were very hard to hand-write. MCTS grows an asymmetric tree using playouts and UCB1, and AlphaGo added learned policy and value networks.")
    yield qa("How do MRV, forward checking and AC-3 speed up a CSP solver?",
             "MRV picks the most constrained variable so dead ends appear early; forward checking prunes neighbours' domains after each assignment; AC-3 propagates constraints across all arcs, detecting conflicts between unassigned variables before search reaches them.")
    yield section("Logic, knowledge & planning", "logic-and")
    yield qa("What is the difference between soundness and completeness?",
             "A sound inference procedure derives only entailed sentences; a complete one derives every entailed sentence. Resolution is sound and refutation-complete for propositional logic; forward chaining is sound and complete for Horn clauses.")
    yield qa("Explain forward vs backward chaining with an example.",
             "Forward chaining starts from known facts and fires rules until the goal appears (production systems, monitoring). Backward chaining starts from the goal and works back through rules whose conclusion matches it (Prolog, diagnosis). (See **Resolution, Forward & Backward Chaining**.)")
    yield qa("What is unification and where is it used?",
             "Finding the most general substitution that makes two logical expressions identical, e.g. `Knows(John, x)` and `Knows(y, Mary)` → `{y/John, x/Mary}`. Used in generalised modus ponens, Prolog, and first-order resolution.")
    yield qa("What is the frame problem?",
             "The difficulty of representing what does *not* change when an action occurs without writing an explicit axiom for every unaffected fact. STRIPS handles it by assuming everything not in an action's add/delete lists stays the same.")
    yield qa("What is STRIPS / PDDL?",
             "A planning language where states are sets of facts and actions have preconditions, add lists and delete lists. PDDL is the standard modern form; the structure lets planners compute domain-independent heuristics such as ignore-delete-lists.")
    yield section("Uncertainty, decisions & learning", "percentage")
    yield qa("Why are Bayesian networks more compact than a full joint distribution?",
             "They encode conditional independence: each variable depends directly only on its parents, so the joint factorises into small CPTs. The burglary network needs 10 numbers instead of 31; the gap grows exponentially with more variables.")
    yield qa("What is an HMM and what is the Viterbi algorithm?",
             "A Markov chain over hidden states with noisy observations of each state. Viterbi is dynamic programming that finds the single most likely hidden-state sequence for an observation sequence in time linear in its length.")
    yield qa("Define an MDP and the Bellman equation.",
             "An MDP is states, actions, a transition model `P(s′|s,a)`, rewards and a discount `γ`. The Bellman equation `U(s) = maxₐ Σ P(s′|s,a)[R + γU(s′)]` characterises optimal utilities; value iteration applies it repeatedly.")
    yield qa("What's the difference between an MDP and reinforcement learning?",
             "In an MDP the transition and reward models are known, so you can plan (value/policy iteration). In RL they are unknown and the agent must learn from experienced transitions — model-based (learn the model, then plan) or model-free (Q-learning, policy gradients).")
    yield qa("Explain the Q-learning update.",
             "`Q(s,a) ← Q(s,a) + α[r + γ maxₐ′ Q(s′,a′) − Q(s,a)]`: move the estimate toward the observed reward plus the discounted value of the best next action. It's off-policy and converges to the optimal Q with enough exploration and a decaying learning rate.")
    yield section("Big picture", "world")
    yield qa("What were the causes of the AI winters, and are we in a bubble now?",
             "Over-promising followed by technical walls: combinatorial explosion in search and brittle, expensive expert systems. Today's systems deliver real value at scale, but costs, reliability (hallucination) and unmet expectations are the usual warning signs to watch.")
    yield qa("How would you explain the difference between AI, ML, DL and generative AI to a non-technical person?",
             "AI is making computers do things that seem intelligent. ML is doing that by learning from examples instead of hand-written rules. Deep learning is ML with large neural networks. Generative AI uses deep learning to create new text, images or audio.")
    yield qa("What are the main ethical risks of AI systems?",
             "Unfair outcomes from biased data, opaque decisions without recourse, privacy leakage, unsafe behaviour under distribution shift or attack, misuse (deepfakes, fraud), and misaligned objectives. Mitigations: subgroup evaluation, documentation, human oversight, monitoring and regulation-aligned governance.")
