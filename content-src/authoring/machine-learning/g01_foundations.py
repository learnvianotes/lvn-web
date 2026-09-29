from kit import *

G = "Foundations"


@topic(G, "data_modeling", "What Is Machine Learning?", "brain")
def _():
    yield lead("Machine learning builds programs that **improve at a task from data** instead of from hand-written rules. You supply examples; a learning algorithm finds the parameters of a model that generalises to examples it has never seen.")
    yield define("Machine learning (Mitchell, 1997)", "a program *learns* from experience **E** with respect to a task **T** and a performance measure **P** if its performance at T, measured by P, improves with E. Spam filtering: T = label emails, E = emails people marked as spam or not, P = the share of emails labelled correctly.")
    yield section("Rules vs learning", "arrows-exchange")
    yield p("In traditional programming a person writes the rules. In ML the rules — the model's parameters — are *fitted* from examples of inputs paired with the right answers.")
    yield flow("Data + hand-written rules", "Program", "Answers")
    yield flow("Data + known answers", "Learning algorithm", "Model (learned rules)", "Answers for new data")
    yield p("A tiny example: the algorithm is never told the rule `y = 3x + 2`; it recovers it from 50 noisy examples.")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression

        rng = np.random.default_rng(0)
        X = rng.uniform(0, 10, size=(50, 1))              # feature: hours studied
        y = 3 * X[:, 0] + 2 + rng.normal(0, 1, size=50)   # target: score, with noise

        model = LinearRegression().fit(X, y)              # training = fitting parameters
        print(round(model.coef_[0], 2), round(model.intercept_, 2))  # 3.05 1.76 ← close to the true 3 and 2
        print(round(model.predict([[4.0]])[0], 1))                   # 14.0 ← inference on a new input (true value 14)
    ''')
    yield section("The supervised setting", "math-function")
    yield formula("y = f(x) + ε        learn f̂ ≈ f from pairs (x₁, y₁), …, (xₙ, yₙ)")
    yield p("`f` is the unknown true relationship and `ε` is noise no model can predict (measurement error, missing information). Even a perfect `f̂` keeps the error caused by `ε` — the **irreducible error**. This picture covers supervised learning; unsupervised learning has no `y` at all (see **Types of Learning**).")
    yield section("Vocabulary", "vocabulary")
    yield table(
        ["Term", "Meaning", "House-price example"],
        ["Example / sample / row", "One observation", "One house sale"],
        ["Feature (input, predictor) `x`", "A measurable input variable", "Area, bedrooms, distance to metro"],
        ["Label / target `y`", "The value to predict (supervised learning only)", "Sale price"],
        ["Model", "A function `f̂` from features to predictions", "`price ≈ w₁·area + w₂·bedrooms + b`"],
        ["Parameters", "Learned from data during training", "The weights `w₁, w₂, b`"],
        ["Hyperparameters", "Chosen *before* training, tuned on validation data", "Regularisation strength, tree depth"],
        ["Training / fitting", "Adjusting parameters to reduce a loss on training data", "`model.fit(X, y)`"],
        ["Inference / prediction", "Applying the trained model to new inputs", "`model.predict(X_new)`"],
        ["Generalisation", "Performing well on unseen data from the same distribution", "Accurate prices for next month's listings"],
    )
    yield section("AI, ML and deep learning", "hierarchy")
    yield flow("Artificial Intelligence", "Machine Learning", "Deep Learning")
    yield table(
        ["Field", "What it is", "Example"],
        ["Artificial intelligence", "Any technique that makes machines act intelligently — including search, logic and planning that learn nothing from data", "A route planner using A* search"],
        ["Machine learning", "The part of AI that learns behaviour from data", "Gradient-boosted trees predicting customer churn"],
        ["Deep learning", "ML with many-layered neural networks that learn their own features from raw data", "A transformer transcribing speech"],
    )
    yield note("These notes cover classic ML on mostly tabular data. Neural networks are covered in **Deep Learning**, LLMs and prompting in **Generative AI**, search/logic/planning in **Artificial Intelligence**, and NumPy/pandas/plotting in **Data Science**.")
    yield section("When ML is — and isn't — the right tool", "scale")
    yield dodont("Use ML when rules are too many or unknown (spam, fraud, images), the patterns change over time, there is enough representative data, and occasional errors are acceptable.",
                 "Using ML when a few clear rules work, when there is no data (or no labels) to learn from, when every decision must be exactly explainable and guaranteed, or when a wrong answer is catastrophic and cannot be caught.")
    yield section("The workflow at a glance", "route")
    yield flow("Frame the problem", "Collect & explore data", "Split train / validation / test", "Prepare features", "Train a baseline, then better models", "Tune & validate", "Test once", "Deploy & monitor")
    yield p("Each box has its own topic in these notes. The split comes *before* any preprocessing is fitted, and the test set is used once at the end — breaking either rule causes **data leakage**.")
    yield qa("What is the difference between a parameter and a hyperparameter?",
             "Parameters are learned from the training data (regression weights, tree split thresholds). Hyperparameters are set before training and control *how* learning happens (learning rate, `max_depth`, regularisation strength `C`); they are chosen by comparing models on validation data or with cross-validation.")
    yield qa("What does it mean for a model to generalise?",
             "It performs about as well on new data from the same distribution as on the data it was trained on. We estimate this with held-out data the model never saw during training or tuning. A model that is excellent on training data but poor on held-out data has overfit.")
    yield qa("How is ML different from traditional programming?",
             "Traditional programs apply rules a developer wrote. ML programs apply rules (parameters) that an algorithm *fitted* from examples, so behaviour comes from the data — which is also why data quality, representativeness and leakage matter so much.")


@topic(G, "types-of-learning", "Types of Learning", "category")
def _():
    yield lead("ML problems are grouped by the feedback the learner gets: **labels** (supervised), **no labels** (unsupervised), **a few labels** (semi-supervised), **labels made from the data itself** (self-supervised) or **rewards** (reinforcement learning).")
    yield table(
        ["Type", "Training data", "Goal", "Typical tasks & algorithms"],
        ["Supervised", "Inputs `X` with labels `y`", "Predict `y` for new `X`", "Classification, regression — linear/logistic regression, trees, SVM, boosting"],
        ["Unsupervised", "Inputs `X` only", "Find structure", "Clustering (k-means, DBSCAN), dimensionality reduction (PCA), anomaly detection"],
        ["Semi-supervised", "Few labelled + many unlabelled rows", "Use unlabelled data to improve a supervised model", "Self-training, label propagation"],
        ["Self-supervised", "Raw data; labels created from the data (the next word, a masked patch)", "Learn general representations", "Pre-training language and vision models"],
        ["Reinforcement", "States, actions, rewards from an environment", "A policy maximising cumulative reward", "Game playing, robotics, recommendations as sequential decisions"],
    )
    yield section("Supervised vs unsupervised on the same data", "arrows-diff")
    yield p("The iris dataset has 150 flowers of 3 species. A classifier learns from the species labels; k-means never sees them but still finds groups that largely match them:")
    yield code('''
        from sklearn.cluster import KMeans
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import adjusted_rand_score

        X, y = load_iris(return_X_y=True)

        clf = LogisticRegression(max_iter=1000).fit(X, y)                 # supervised: uses y
        print(clf.predict(X[[0, 50, 100]]))                               # [0 1 2] ← species 0, 1, 2

        km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)       # unsupervised: never sees y
        print(km.labels_[[0, 50, 100]])                                   # [1 0 2] ← cluster ids are arbitrary names
        print(round(adjusted_rand_score(y, km.labels_), 2))               # 0.73 ← 1.0 = perfect match, ≈0 = random; versicolor/virginica overlap
    ''')
    yield section("Supervised: classification vs regression", "git-fork")
    yield table(
        ["", "Classification", "Regression"],
        ["Target", "A category (spam / not spam; cat / dog / bird)", "A number (price, temperature, demand)"],
        ["Output", "Class label, usually with a probability or score", "A real value"],
        ["Loss (training)", "Log-loss (cross-entropy), hinge", "Squared error, absolute error, Huber"],
        ["Metrics", "Accuracy, precision, recall, F1, ROC-AUC, PR-AUC", "MAE, RMSE, R²"],
        ["Variants", "Binary, multi-class (one of k), multi-label (any subset of k)", "Single- or multi-output"],
    )
    yield warn("“Logistic regression” is a **classification** algorithm — the name comes from regressing the log-odds. And a numeric-looking target is not automatically regression: star ratings 1–5 are often better treated as ordered classes.")
    yield section("Other ways to slice ML", "adjustments")
    yield table(
        ["Distinction", "One side", "Other side"],
        ["Batch vs online", "Batch: train on the full dataset, retrain periodically", "Online: update incrementally as data arrives (`partial_fit` in `SGDClassifier`, `MultinomialNB`)"],
        ["Model-based vs instance-based", "Model-based: learn parameters, then discard the data (linear models)", "Instance-based: keep the training data and compare new points to it (k-NN)"],
        ["Parametric vs non-parametric", "Parametric: a fixed number of parameters regardless of data size (linear/logistic regression, Naive Bayes)", "Non-parametric: complexity grows with the data (k-NN, decision trees, kernel SVMs)"],
        ["Discriminative vs generative", "Discriminative: model `P(y | x)` or the boundary directly (logistic regression, SVM)", "Generative: model how data is produced, `P(x | y)·P(y)` (Naive Bayes, Gaussian mixtures)"],
    )
    yield section("Reinforcement learning in one paragraph", "robot")
    yield p("An **agent** observes a **state**, takes an **action**, receives a **reward** and a new state from the **environment**, and learns a **policy** (state → action) that maximises total future reward. Unlike supervised learning, nobody gives the correct action — only delayed, scalar feedback — so the agent must balance **exploration** and **exploitation**. Q-learning, MDPs and value iteration are worked through in the **Artificial Intelligence** notes.")
    yield qa("Is anomaly detection supervised or unsupervised?",
             "Either. With labelled fraud cases it is (heavily imbalanced) supervised classification. Without labels it is unsupervised: model what “normal” looks like and flag points that don't fit (Isolation Forest, one-class SVM). Often a few labels are used only to evaluate an unsupervised detector.")
    yield qa("What is self-supervised learning and why does it matter?",
             "The labels are generated from the data itself — predict the next token, a masked word or a hidden image patch. It needs no human labelling, so it scales to internet-sized data; it is how large language and vision models are pre-trained before being fine-tuned on small labelled datasets.")
    yield qa("Parametric vs non-parametric — give an example of each.",
             "Logistic regression is parametric: one weight per feature no matter how many rows. k-NN is non-parametric: it stores all training points, so its effective complexity grows with the data. Non-parametric models are more flexible but need more data and are slower at prediction time.")


@topic(G, "problem_formulation", "Framing an ML Problem", "target-arrow")
def _():
    yield lead("Most failed ML projects fail at framing, not modelling: the wrong target, a metric nobody cares about, or features that won't exist at prediction time. Turn the business goal into a precise prediction task first.")
    yield steps(
        ("Business objective", "What decision will the prediction change? “Reduce churn” → “which customers should get a retention offer this week?”"),
        ("Prediction target", "Define `y` exactly, including time: *churned = no purchase in the 30 days after the prediction date*."),
        ("Prediction point & features", "Only use information available **at the moment the prediction is made**. Everything after it is leakage."),
        ("ML task", "Binary classification, regression, ranking, clustering…"),
        ("Metrics", "An offline ML metric (PR-AUC, RMSE) that tracks an online business metric (retained revenue); set a success threshold up front."),
        ("Baseline", "A trivial model or a simple rule. A model is only useful if it clearly beats it."),
        ("Constraints", "Latency, cost, interpretability, fairness, privacy, how often labels arrive."),
    )
    yield section("Common task types", "list-details")
    yield table(
        ["Task", "Predicts", "Example", "Typical metrics"],
        ["Regression", "A number", "Ride price from distance and time", "MAE, RMSE, R²"],
        ["Binary classification", "One of two classes", "Is this transaction fraud?", "Precision, recall, F1, PR-AUC, ROC-AUC"],
        ["Multi-class classification", "One of k classes", "Which product category?", "Accuracy, macro-F1, log-loss"],
        ["Multi-label classification", "Any subset of k labels", "Tags for an article", "Per-label F1, Hamming loss"],
        ["Ranking", "An ordering of items", "Search results for a query", "NDCG@k, MRR, MAP"],
        ["Recommendation", "Items a user will like", "Movies to show on the home page", "Recall@k, NDCG@k, online CTR / watch time"],
        ["Forecasting", "Future values of a time series", "Next week's demand per store", "MAE, RMSE, sMAPE/MASE"],
        ["Clustering", "Groups of similar rows (no labels)", "Customer segments", "Silhouette; usefulness to the business"],
        ["Anomaly detection", "Unusual rows", "Faulty sensor readings", "Precision@k, recall on known incidents"],
    )
    yield section("Always start with a baseline", "ruler-2")
    yield p("On the breast-cancer dataset (63% benign), a “model” that always predicts the majority class already gets 63% accuracy. A real model has to beat that, not 50%.")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.dummy import DummyClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_breast_cancer(return_X_y=True)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)

        baseline = DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)
        model = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_tr, y_tr)
        print(round(baseline.score(X_te, y_te), 3))   # 0.629 ← always predicts "benign"
        print(round(model.score(X_te, y_te), 3))      # 0.958
    ''')
    yield p("Good baselines: the majority class or the mean (`DummyClassifier`, `DummyRegressor`), yesterday's value for a time series, a hand-written rule the business already uses, or a small logistic/linear regression.")
    yield section("Worked example: a spam filter", "mail")
    yield table(
        ["Decision", "Choice", "Why / caveat"],
        ["Task", "Binary classification: spam vs not spam", "Output a probability so the threshold can be tuned"],
        ["Input", "Subject, body text, sender history, links, sending IP reputation", "All available when the email arrives"],
        ["Labels", "“Report spam” / “Not spam” clicks plus a sample reviewed by annotators", "User reports are biased and noisy: most spam is never reported and people also “report” newsletters they signed up for"],
        ["Metric", "Precision at a fixed recall, or recall at ≥ 99.9% precision", "A legitimate email lost in the spam folder (false positive) is far worse than one spam in the inbox"],
        ["Baseline", "Current blocklist and keyword rules", "The model must beat what already exists"],
        ["Constraints", "Milliseconds per email; spammers adapt", "Retrain often and monitor drift"],
    )
    yield section("Framing traps", "alert-triangle")
    yield ul(
        "**Proxy targets** — optimising clicks when you care about satisfaction rewards clickbait.",
        "**Features from the future** — `days_since_last_login` computed at training time over the whole history, but at prediction time only up to today.",
        "**Feedback loops** — a model that decides who gets a loan only ever sees outcomes for approved applicants.",
        "**No action attached** — a churn score nobody acts on has zero value, however high its AUC.",
    )
    yield qa("How would you frame a churn prediction problem?",
             "Pick a prediction date and define churn precisely (e.g. no activity in the next 30 days). Build features only from data before the prediction date, label from the 30 days after it, and split by time (train on earlier months, validate on later ones). It's binary classification with an imbalanced target: evaluate with PR-AUC or precision@k (the number of customers the retention team can contact) and compare to a baseline such as “inactive for 14 days”.")
    yield qa("Your model has 95% accuracy. Is it good?",
             "Unknown until you compare it with a baseline and the right metric. If 95% of cases are negative, predicting “negative” always gets 95%. Check precision/recall for the class you care about, the cost of each error, and whether the metric moves the business outcome.")
