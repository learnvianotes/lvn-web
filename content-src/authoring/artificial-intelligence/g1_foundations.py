from kit import *

G = "Foundations"


@topic(G, "what-is-ai", "What Is AI?", "brain")
def _():
    yield lead("Artificial Intelligence is the study and construction of **agents that act intelligently** — systems that perceive their situation, reason about it and choose actions that achieve goals. Machine learning is one (now dominant) way to build them; search, logic and probability are the others.")
    yield define("Artificial Intelligence", "the field that builds computer systems able to perform tasks that normally need human intelligence — perceiving, reasoning, planning, learning, understanding language and acting in the world.")
    yield flow("Artificial Intelligence", "Machine Learning", "Deep Learning", "Generative AI / LLMs")
    yield p("Every arrow is a *subset*: all deep learning is machine learning, and all machine learning is AI — but a chess engine using search, a route planner using A* and a medical expert system using rules are AI **without** any learning. Those classical techniques are what this subject covers; learning-based AI has its own notes (**Machine Learning**, **Deep Learning**, **Generative AI**).")
    yield section("Four ways to define AI", "layout-grid")
    yield p("Russell & Norvig's classic textbook sorts definitions along two axes — *thinking* vs *acting*, and matching *humans* vs being *rational* (doing the right thing):")
    yield table(
        ["", "Human-like", "Rational"],
        ["**Thinking**", "*Thinking humanly* — cognitive modelling: build programs that reason the way people do (cognitive science)", "*Thinking rationally* — the “laws of thought”: correct inference with formal logic"],
        ["**Acting**", "*Acting humanly* — the Turing test: behave indistinguishably from a person", "*Acting rationally* — the **rational agent**: act to achieve the best expected outcome"],
    )
    yield note("Modern AI mostly follows the **rational agent** approach: it is general (logic is one tool, not the only one), and “best expected outcome” is mathematically precise — unlike “human-like”.")
    yield section("The Turing test and the Chinese room", "message-chatbot")
    yield cards(
        ("Turing test (1950)", "A human judge chats by text with a hidden person and a hidden machine. If the judge can't reliably tell which is which, the machine passes. Passing needs natural-language processing, knowledge representation, automated reasoning and machine learning. The *total* Turing test adds computer vision and robotics.", "message-question"),
        ("Chinese room (Searle, 1980)", "A person who knows no Chinese follows a rulebook to answer Chinese notes and looks fluent from outside. Searle's point: manipulating symbols (syntax) is not the same as understanding (semantics) — so passing the Turing test would not prove a machine *thinks*.", "language"),
    )
    yield p("A 1966 program already shows why *acting* human is a weak test of *being* intelligent. ELIZA imitated a therapist with a handful of pattern → template rules and no understanding at all:")
    yield code('''
        import re

        RULES = [                                  # tried in order; the last one always matches
            (r"I need (.*)", "Why do you need {0}?"),
            (r"I am (.*)", "How long have you been {0}?"),
            (r".*\\bmother\\b.*", "Tell me more about your family."),
            (r"(.*)", "Please, go on."),
        ]
        REFLECT = {"my": "your", "me": "you", "i": "you", "am": "are"}

        def eliza(text):
            for pattern, reply in RULES:
                m = re.fullmatch(pattern, text.rstrip(".!"), re.IGNORECASE)
                if m:
                    parts = [" ".join(REFLECT.get(w.lower(), w) for w in g.split()) for g in m.groups()]
                    return reply.format(*parts)

        print(eliza("I need a holiday"))                  # Why do you need a holiday?
        print(eliza("I am worried about my exams."))      # How long have you been worried about your exams?
        print(eliza("My mother calls every day"))         # Tell me more about your family.
        print(eliza("The weather is nice"))               # Please, go on.
    ''')
    yield section("Weak vs strong, narrow vs general", "arrows-left-right")
    yield table(
        ["Term", "Meaning", "Status"],
        ["**Weak AI**", "Machines can *act as if* they were intelligent", "Philosophical claim — widely accepted"],
        ["**Strong AI**", "Machines that act intelligently really *think* / have minds", "Philosophical claim — open (Chinese room debate)"],
        ["**Narrow AI (ANI)**", "Excels at one task or domain: chess, face recognition, spam filtering, translation", "Every deployed system today"],
        ["**General AI (AGI)**", "Human-level competence across essentially all cognitive tasks, able to transfer and learn new ones", "Research goal; LLMs are broader than older systems but debated"],
        ["**Superintelligence (ASI)**", "Far exceeds humans in every domain", "Hypothetical — central to AI-safety discussions"],
    )
    yield warn("Don't mix the two pairs up: *weak/strong* is about whether the machine has a mind; *narrow/general* is about how many tasks it can do. A system could in principle be general but “weak”.")
    yield section("A short history — booms and winters", "timeline")
    yield table(
        ["Year", "Milestone"],
        ["1943", "McCulloch & Pitts model a neuron as a logic gate"],
        ["1950", "Turing, “Computing Machinery and Intelligence” — the imitation game"],
        ["1956", "**Dartmouth workshop** (McCarthy, Minsky, Shannon, Rochester) — the name “artificial intelligence”; the field is born"],
        ["1958–66", "Perceptron (Rosenblatt), Samuel's learning checkers player, the General Problem Solver, LISP, ELIZA"],
        ["1969–73", "Minsky & Papert show single perceptrons can't learn XOR; the Lighthill report criticises AI's “combinatorial explosion”"],
        ["1974–80", "**First AI winter** — promises unmet, funding cut"],
        ["1980–87", "**Expert systems** boom (XCON at DEC, MYCIN-style rule bases); Japan's Fifth Generation project; backprop popularised (1986)"],
        ["1987–93", "**Second AI winter** — Lisp-machine market collapses, expert systems prove brittle and costly to maintain"],
        ["1990s–2000s", "Probabilistic AI (Bayesian networks, HMMs), statistical ML; **Deep Blue** beats Kasparov (1997)"],
        ["2011–12", "IBM Watson wins *Jeopardy!*; **AlexNet** wins ImageNet — the deep-learning era begins"],
        ["2016", "**AlphaGo** beats Lee Sedol — deep networks + Monte Carlo tree search + reinforcement learning"],
        ["2017–now", "The Transformer (2017), large language models, ChatGPT (2022), multimodal models and LLM agents"],
    )
    yield cards(
        ("Symbolic AI (“GOFAI”)", "Knowledge written as symbols and rules; intelligence = search + logical inference. Transparent and precise, but brittle and hand-built. Dominated 1956–1990.", "sitemap"),
        ("Statistical / connectionist AI", "Knowledge *learned* from data as probabilities or network weights. Robust and scalable, but data-hungry and hard to interpret. Dominant since the 1990s–2010s.", "chart-dots"),
    )
    yield note("Winters followed hype: early researchers predicted human-level AI “within a generation”, then hit the **combinatorial explosion** of search and the **knowledge-acquisition bottleneck** of hand-written rules. Both problems — and the techniques built to tame them — are the core of this subject.")
    yield qa("What is the difference between AI, machine learning and deep learning?",
             "AI is the broad goal of building intelligent agents, by any method — search, logic, probability or learning. Machine learning is the subset where behaviour is learned from data instead of programmed. Deep learning is the subset of ML using many-layered neural networks.")
    yield qa("What is the rational agent approach, and why is it preferred?",
             "An agent is rational if, for every percept sequence, it picks the action expected to maximise its performance measure given what it knows. It's preferred because it is well-defined mathematically and general — it doesn't require copying human thought, and logical inference is just one way to act rationally.")
    yield qa("What were the AI winters?",
             "Periods of collapsed funding and interest (roughly 1974–80 and 1987–93) that followed over-promising: search didn't scale to real problems (combinatorial explosion) and expert systems were brittle and expensive to maintain.")


@topic(G, "intelligent-agents", "Intelligent Agents & Environments", "robot")
def _():
    yield lead("An **agent** perceives its environment through sensors and acts on it through actuators. Describing an AI problem starts by pinning down four things — its **PEAS** — and the properties of its environment, which decide which techniques will work.")
    yield flow("Environment", "Sensors → percept", "Agent program", "Actuators → action", "Environment")
    yield define("Agent function", "a mapping from every possible **percept sequence** (everything the agent has perceived so far) to an action. The **agent program** is the concrete code that implements it on a machine.")
    yield define("Rational agent", "for each possible percept sequence, selects the action expected to maximise its **performance measure**, given the evidence of the percepts and its built-in knowledge.")
    yield warn("Rational ≠ omniscient ≠ perfect. A rational agent maximises *expected* performance with the information it has; bad luck doesn't make it irrational. It should also gather information (look before crossing) and **learn** to compensate for incomplete prior knowledge.")
    yield section("The vacuum world", "home")
    yield p("The textbook toy: two squares, A and B, each clean or dirty. The agent perceives `(location, status)` and can `Suck`, move `Left` or `Right`. The performance measure awards one point per clean square per time step:")
    yield code('''
        def reflex_vacuum_agent(percept):
            location, status = percept
            if status == "Dirty":
                return "Suck"
            return "Right" if location == "A" else "Left"

        def run(agent, world, location="A", steps=6):
            score, actions = 0, []
            for _ in range(steps):
                action = agent((location, world[location]))
                actions.append(action)
                if action == "Suck":
                    world[location] = "Clean"
                elif action in ("Left", "Right"):
                    location = "B" if action == "Right" else "A"
                score += sum(s == "Clean" for s in world.values())   # performance measure
            return actions, score

        actions, score = run(reflex_vacuum_agent, {"A": "Dirty", "B": "Dirty"})
        print(actions)    # ['Suck', 'Right', 'Suck', 'Left', 'Right', 'Left']
        print(score)      # 10 ← 1 + 1 + 2 + 2 + 2 + 2
    ''')
    yield section("PEAS — specifying the task", "list-details")
    yield table(
        ["Agent", "Performance measure", "Environment", "Actuators", "Sensors"],
        ["Self-driving taxi", "Safe, fast, legal, comfortable trip; profit", "Roads, traffic, pedestrians, weather, passengers", "Steering, accelerator, brake, signals, display", "Cameras, LiDAR, radar, GPS, speedometer, odometer"],
        ["Medical diagnosis system", "Healthy patient, low cost, few tests", "Patient, hospital, staff", "Display questions, tests, diagnoses, treatments", "Keyboard entry of symptoms, test results"],
        ["Chess program", "Win / draw / loss", "Board, opponent, clock", "Moves on the board", "Board state"],
        ["Spam filter", "Spam caught, legitimate mail kept", "Mail stream, users", "Mark as spam / deliver", "Message text, headers, sender reputation"],
    )
    yield section("Properties of task environments", "adjustments")
    yield table(
        ["Dimension", "Easy end", "Hard end", "What it changes"],
        ["Observability", "**Fully observable** — sensors show the whole relevant state", "**Partially observable** — noisy sensors, hidden state", "Hidden state → agent must keep internal state / beliefs"],
        ["Agents", "**Single-agent**", "**Multi-agent** — competitive or cooperative", "Opponents → game theory, adversarial search"],
        ["Determinism", "**Deterministic** — next state fixed by state + action", "**Stochastic** (nondeterministic) — outcomes uncertain", "Uncertainty → probabilities, expected utility"],
        ["Episodes", "**Episodic** — each decision independent (classify one image)", "**Sequential** — actions affect the future (chess)", "Sequential → planning ahead"],
        ["Change", "**Static** — world waits while agent thinks", "**Dynamic** — world changes meanwhile", "Dynamic → time pressure, anytime algorithms"],
        ["State/time", "**Discrete** — finite states and actions", "**Continuous** — positions, speeds", "Continuous → optimisation, control theory"],
        ["Knowledge", "**Known** — rules/physics given", "**Unknown** — must learn how the world works", "Unknown → exploration, learning"],
    )
    yield table(
        ["Task", "Observable", "Agents", "Deterministic", "Episodic", "Static", "Discrete"],
        ["Crossword puzzle", "Fully", "Single", "Yes", "Sequential", "Static", "Discrete"],
        ["Chess with a clock", "Fully", "Multi", "Yes", "Sequential", "Semi", "Discrete"],
        ["Poker", "Partially", "Multi", "Stochastic", "Sequential", "Static", "Discrete"],
        ["Taxi driving", "Partially", "Multi", "Stochastic", "Sequential", "Dynamic", "Continuous"],
        ["Image classification", "Fully", "Single", "Yes", "Episodic", "Static", "Continuous"],
    )
    yield note("The real world is the hard end of every dimension: partially observable, multi-agent, stochastic, sequential, dynamic, continuous and unknown. Most techniques in these notes relax one or more dimensions — search assumes fully observable + deterministic + known; MDPs drop determinism; reinforcement learning drops “known”.")
    yield qa("What does PEAS stand for?",
             "Performance measure, Environment, Actuators, Sensors — the four things to specify before designing an agent.")
    yield qa("Is a rational agent always successful?",
             "No. It maximises *expected* performance given its percepts and knowledge. With partial information or a stochastic world it can make the best possible choice and still get a bad outcome.")
    yield qa("What's the difference between the agent function and the agent program?",
             "The agent function is the abstract mathematical mapping from percept histories to actions (often an infinite table). The agent program is the finite code running on the agent's architecture that implements it.")


@topic(G, "agent-types", "Types of Agents", "hierarchy")
def _():
    yield lead("Agent programs range from simple lookup rules to systems that plan, weigh trade-offs and improve themselves. Each type adds one capability to the previous one.")
    yield table(
        ["Agent type", "Decides using", "Strength", "Limitation", "Example"],
        ["**Simple reflex**", "Condition–action rules on the *current* percept", "Fast, simple", "Fails when the world is partially observable; can loop forever", "Thermostat, the vacuum agent above"],
        ["**Model-based reflex**", "Rules + an internal **state** updated by a model of how the world evolves", "Handles partial observability", "Still has no explicit goals", "Car tracking vehicles it can't currently see"],
        ["**Goal-based**", "A model + **goals**; searches/plans for action sequences that reach them", "Flexible — change the goal, not the rules", "Goals are binary: all paths to the goal look equally good", "Route planner, puzzle solver"],
        ["**Utility-based**", "A **utility function** scoring how *desirable* each state is; maximises expected utility", "Trades off speed, safety, cost; handles uncertainty", "Utility is hard to specify; heavy computation", "Self-driving car choosing a route"],
        ["**Learning agent**", "Any of the above + components that improve it from experience", "Works in unknown environments; gets better", "Needs data/experience; can learn wrong things", "Spam filter, game-playing RL agent"],
    )
    yield section("Why internal state matters", "database")
    yield p("Add a cost of 1 point per move to the vacuum world. The simple reflex agent can't remember that B is already clean, so it shuttles back and forth forever. A model-based agent remembers both squares and stops (`NoOp`):")
    yield code('''
        def reflex_agent(percept):
            location, status = percept
            if status == "Dirty":
                return "Suck"
            return "Right" if location == "A" else "Left"

        def make_model_based_agent():
            model = {"A": None, "B": None}               # internal state: what we believe about each square
            def agent(percept):
                location, status = percept
                model[location] = status                 # update the model from the percept
                if status == "Dirty":
                    model[location] = "Clean"            # predict the effect of our own action
                    return "Suck"
                if model["A"] == model["B"] == "Clean":
                    return "NoOp"
                return "Right" if location == "A" else "Left"
            return agent

        def run(agent, steps=10):
            world, location, score = {"A": "Dirty", "B": "Dirty"}, "A", 0
            for _ in range(steps):
                action = agent((location, world[location]))
                if action == "Suck":
                    world[location] = "Clean"
                elif action in ("Left", "Right"):
                    location = "B" if action == "Right" else "A"
                    score -= 1                                          # moving costs energy
                score += sum(s == "Clean" for s in world.values())
            return score

        print(run(reflex_agent))               # 10 ← keeps paying for pointless moves
        print(run(make_model_based_agent()))   # 17 ← stops once it knows both squares are clean
    ''')
    yield section("Goals vs utilities", "target")
    yield p("A goal-based agent asks *“does this reach the goal?”*; a utility-based agent asks *“how good is this outcome?”*. Utility is needed whenever goals conflict (speed vs safety) or success is uncertain — the agent then maximises **expected utility** (see **Utility & Markov Decision Processes**).")
    yield section("The learning agent", "school")
    yield cards(
        ("Performance element", "The agent proper — selects actions (any of the four designs above).", "player-play"),
        ("Critic", "Judges how well the agent is doing against a fixed performance standard and gives feedback (e.g. a reward).", "gavel"),
        ("Learning element", "Uses the critic's feedback to improve the performance element.", "school"),
        ("Problem generator", "Suggests exploratory actions that lead to new, informative experiences — exploration.", "compass"),
        cols=2,
    )
    yield note("LLM-based “AI agents” fit this template: the LLM is the performance element choosing actions (tool calls), a memory/scratchpad is the internal state, the user's task is the goal, and feedback loops play the critic. See the **Generative AI** notes.")
    yield qa("When is a simple reflex agent enough?",
             "When the environment is fully observable and the right action depends only on the current percept — e.g. a thermostat. With partial observability it needs internal state (model-based) or it may loop forever.")
    yield qa("Why would you prefer a utility-based agent over a goal-based one?",
             "Goals only distinguish success from failure. A utility function ranks outcomes, so the agent can trade off conflicting objectives and weigh the probability of success — essential under uncertainty.")
