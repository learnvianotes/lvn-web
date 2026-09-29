from kit import *
from mlkit import code_out

G = "Core Concepts"


@topic(G, "train_test", "Train, Validation & Test Sets", "flask")
def _():
    yield lead("You can't measure generalisation on the data you trained on. Hold data back: a **validation** set to make choices and a **test** set, used once, to report how the final model will do on new data.")
    yield table(
        ["Split", "Used for", "Typical share"],
        ["Training", "Fitting parameters (`fit`)", "60–80%"],
        ["Validation", "Choosing hyperparameters, features, the model, the decision threshold; early stopping", "10–20% (or cross-validation instead)"],
        ["Test", "One final, unbiased estimate of performance — after all decisions are made", "10–20%"],
    )
    yield p("The shares are rules of thumb. With millions of rows, 1% can be a perfectly large test set; with a few hundred rows, prefer cross-validation for model selection and keep a small test set — or use nested cross-validation.")
    yield section("A three-way split", "arrows-split-2")
    yield code('''
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split

        X, y = make_classification(n_samples=1000, weights=[0.9], random_state=0)   # ~10% positives

        X_tmp, X_test, y_tmp, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        X_train, X_val, y_train, y_val = train_test_split(X_tmp, y_tmp, test_size=0.25,   # 0.25 × 0.8 = 0.2
                                                          stratify=y_tmp, random_state=42)
        print(len(X_train), len(X_val), len(X_test))                                    # 600 200 200
        print(round(y_train.mean(), 3), round(y_val.mean(), 3), round(y_test.mean(), 3))  # 0.102 0.105 0.1 ← same class balance
    ''')
    yield section("Why stratify", "chart-pie")
    yield p("With a rare class, a purely random split can leave the test set with almost no positives. `stratify=y` keeps the class proportions identical in every split:")
    yield code('''
        import numpy as np
        from sklearn.model_selection import train_test_split

        y = np.array([1] * 5 + [0] * 95)                    # 5% positives
        random_counts = [int(train_test_split(y, test_size=0.2, random_state=s)[1].sum()) for s in range(8)]
        strat_counts = [int(train_test_split(y, test_size=0.2, stratify=y, random_state=s)[1].sum()) for s in range(8)]
        print(random_counts)    # [1, 0, 3, 0, 1, 0, 1, 0] ← positives in the 20-row test set, per seed
        print(strat_counts)     # [1, 1, 1, 1, 1, 1, 1, 1]
    ''')
    yield section("When a random split is wrong", "alert-triangle")
    yield table(
        ["Data", "Problem with a random split", "Split instead by"],
        ["Time-ordered (sales, prices, logs)", "Training on the future to predict the past", "Time: train on earlier, validate/test on later"],
        ["Grouped (several rows per patient, user, device)", "The model recognises the entity, not the pattern", "Group: all rows of an entity in one split"],
        ["Near-duplicates (same image resized, reposted listings)", "Test rows are copies of training rows", "Deduplicate first, or group duplicates"],
    )
    yield section("Rules that keep evaluation honest", "shield-check")
    yield ol(
        "Split **first**, before fitting any imputer, scaler, encoder or feature selector.",
        "Fit everything on the training data; only `transform` the validation and test data.",
        "Make every decision with validation data or cross-validation.",
        "Look at the test set **once**. If you then change the model because of it, it has become a validation set and its score is optimistic.",
        "After choosing the model, refit it on train + validation before deploying (more data, same recipe).",
    )
    yield section("Reading the gaps", "stethoscope")
    yield table(
        ["Training error", "Validation error", "Diagnosis", "Next step"],
        ["High", "High (similar)", "Underfitting (high bias)", "More capacity, better features, less regularisation"],
        ["Low", "Much higher", "Overfitting (high variance)", "More data, regularisation, simpler model, early stopping"],
        ["Low", "Low", "Good fit", "Confirm on the test set"],
    )
    yield p("See **Bias–Variance & Overfitting** for the theory and learning curves.")
    yield qa("Why do we need a validation set in addition to a test set?",
             "Every choice made by comparing scores — hyperparameters, features, models — fits the data those scores came from. If you make them on the test set, the test score becomes optimistically biased. The validation set absorbs that selection bias; the untouched test set then gives an honest final estimate.")
    yield qa("You tuned on the test set by mistake. What now?",
             "Treat that score as a validation score, not a generalisation estimate. Get a fresh held-out set (new data, or a later time period) for the final evaluation, and switch to cross-validation for tuning.")


@topic(G, "cross-validation", "Cross-Validation", "refresh")
def _():
    yield lead("Cross-validation (CV) rotates which part of the data is held out, so every row is used for both training and validation. It gives a more reliable estimate than a single split — especially on small datasets — plus a sense of its variability.")
    yield define("k-fold cross-validation", "split the training data into k folds; train k models, each on k−1 folds, and score each on the remaining fold. Report the mean (and standard deviation) of the k scores. Typical k: 5 or 10.")
    yield flow("Fold 1 held out", "Fold 2 held out", "…", "Fold k held out", "Average the k scores")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_breast_cancer(return_X_y=True)
        model = make_pipeline(StandardScaler(), LogisticRegression())      # scaler refit inside every fold

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
        print(scores.round(3))                                   # [0.956 0.974 0.982 1.    0.982]
        print(round(scores.mean(), 3), round(scores.std(), 3))   # 0.979 0.014

        res = cross_validate(model, X, y, cv=cv, scoring=["accuracy", "roc_auc"], return_train_score=True)
        print(round(res["train_accuracy"].mean(), 3), round(res["test_roc_auc"].mean(), 3))   # 0.988 0.995
    ''')
    yield note("CV **estimates** how well a modelling *recipe* generalises; it doesn't produce a model. After choosing the recipe, refit it once on all the training data. And CV only reduces the variance of the estimate — with 50 rows, it is still noisy.")
    yield section("Choosing the splitter", "list-details")
    yield table(
        ["Splitter", "Use when"],
        ["`KFold`", "Regression, i.i.d. rows (use `shuffle=True` if rows are ordered)"],
        ["`StratifiedKFold`", "Classification — keeps class proportions in every fold (the default for classifiers when you pass `cv=5`)"],
        ["`GroupKFold` / `StratifiedGroupKFold`", "Several rows per patient/user/session — a group never appears on both sides"],
        ["`TimeSeriesSplit`", "Time-ordered data — always train on the past, validate on the future"],
        ["`LeaveOneOut`", "Very small datasets (n models; high-variance estimate, expensive)"],
        ["`RepeatedStratifiedKFold`", "Small data — repeat k-fold with different shuffles to stabilise the estimate"],
    )
    yield section("Group leakage in action", "users")
    yield p("30 patients, 10 samples each. Every patient has a distinctive feature “signature”, and the label is a per-patient property unrelated to that signature — so there is nothing general to learn. Plain k-fold puts each patient's samples on both sides and k-NN simply recognises the patient:")
    yield code('''
        import numpy as np
        from sklearn.model_selection import GroupKFold, KFold, cross_val_score
        from sklearn.neighbors import KNeighborsClassifier

        rng = np.random.default_rng(0)
        groups = np.repeat(np.arange(30), 10)                       # patient id of each row
        signature = rng.normal(size=(30, 5))
        X = signature[groups] + rng.normal(scale=0.1, size=(300, 5))
        y = rng.integers(0, 2, size=30)[groups]                     # label depends only on who the patient is

        model = KNeighborsClassifier(n_neighbors=3)
        kfold = cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=0)).mean()
        group = cross_val_score(model, X, y, cv=GroupKFold(n_splits=5), groups=groups).mean()
        print(round(kfold, 2), round(group, 2))                     # 1.0 0.38 ← memorised patients vs honest (chance-level) estimate
    ''')
    yield section("Time-series splits", "timeline")
    yield code_out('''
        import numpy as np
        from sklearn.model_selection import TimeSeriesSplit

        days = np.arange(10)                                        # rows already in time order
        for train_idx, test_idx in TimeSeriesSplit(n_splits=3).split(days):
            print(train_idx.tolist(), "→", test_idx.tolist())
    ''', out='''
[0, 1, 2, 3] → [4, 5]
[0, 1, 2, 3, 4, 5] → [6, 7]
[0, 1, 2, 3, 4, 5, 6, 7] → [8, 9]
''')
    yield p("An expanding window: each fold trains on everything before the validation period. Use `gap=` to leave a buffer when labels take time to arrive, and `max_train_size=` for a sliding window.")
    yield section("Nested cross-validation", "stack-2")
    yield p("If you tune hyperparameters with CV and report that same CV score, it is optimistically biased — you picked the best of many. **Nested CV** wraps the tuning (inner loop) inside an outer CV that only scores the whole tune-then-fit procedure:")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.model_selection import GridSearchCV, cross_val_score
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        X, y = load_breast_cancer(return_X_y=True)
        inner = GridSearchCV(make_pipeline(StandardScaler(), SVC()), {"svc__C": [0.1, 1, 10]}, cv=3)
        outer_scores = cross_val_score(inner, X, y, cv=5)          # each outer fold runs its own grid search
        print(round(outer_scores.mean(), 3))                       # 0.974 ← estimate for "SVC tuned by grid search"
    ''')
    yield qa("Why use stratified k-fold for classification?",
             "It keeps the class ratio the same in every fold. With imbalanced classes, plain k-fold can produce folds with very few (or zero) positives, making fold scores noisy or undefined (e.g. ROC-AUC needs both classes).")
    yield qa("How do you cross-validate a time-series model?",
             "With forward-chaining splits (`TimeSeriesSplit`): train on data up to time t, validate on the period after t, move t forward. Never shuffle; build lag/rolling features from past values only; leave a gap if labels arrive late.")
    yield qa("What is nested cross-validation for?",
             "An unbiased performance estimate when hyperparameters are tuned by CV. The inner loop selects hyperparameters; the outer loop evaluates the complete selection procedure on folds the inner loop never saw.")


@topic(G, "loss-gradient-descent", "Loss Functions & Gradient Descent", "trending-down")
def _():
    yield lead("Training means minimising a **loss function** — a number that says how wrong the model is. Gradient descent does this by repeatedly stepping the parameters downhill along the negative gradient.")
    yield table(
        ["Term", "Meaning"],
        ["Loss", "Error on one example, e.g. `(y − ŷ)²`"],
        ["Cost / objective", "Average loss over the training set, plus any regularisation penalty — what the optimiser minimises"],
        ["Metric", "What *you* care about when evaluating (accuracy, F1, MAE); it need not be differentiable and may differ from the training loss"],
    )
    yield section("Common losses", "list-details")
    yield table(
        ["Loss", "Formula (one example)", "Used by", "Notes"],
        ["Squared error (MSE)", "`(y − ŷ)²`", "Linear regression, regression trees", "Penalises large errors heavily; predicts the conditional **mean**"],
        ["Absolute error (MAE)", "`|y − ŷ|`", "Robust regression, quantile models", "Less sensitive to outliers; predicts the conditional **median**"],
        ["Huber", "Squared for `|y − ŷ| ≤ δ`, linear beyond", "`HuberRegressor`, boosting", "MSE near zero, MAE for outliers"],
        ["Log-loss (binary cross-entropy)", "`−[y·log p + (1 − y)·log(1 − p)]`", "Logistic regression, boosting, neural nets", "Punishes confident wrong probabilities without limit"],
        ["Hinge", "`max(0, 1 − y·f(x))`, `y ∈ {−1, +1}`", "SVM", "Zero once a point is beyond the margin"],
    )
    yield code_out('''
        import numpy as np
        from sklearn.metrics import log_loss, mean_absolute_error, mean_squared_error

        y = np.array([3.0, 5.0, 2.0, 8.0])
        y_hat = np.array([2.5, 5.0, 4.0, 7.0])
        print(np.mean((y - y_hat) ** 2), mean_squared_error(y, y_hat))
        print(np.mean(np.abs(y - y_hat)), mean_absolute_error(y, y_hat))

        # log-loss for a positive example (y = 1) at different predicted probabilities
        for p in (0.9, 0.5, 0.1, 0.01):
            print(p, round(-np.log(p), 3))
        print(round(log_loss([1, 0], [0.9, 0.2]), 4))   # mean of −log 0.9 and −log 0.8
    ''', out='''
1.3125 1.3125
0.875 0.875
0.9 0.105
0.5 0.693
0.1 2.303
0.01 4.605
0.1643
''')
    yield section("Gradient descent", "arrow-down-right")
    yield formula("θ ← θ − η · ∇J(θ)        η = learning rate, ∇J = gradient of the cost")
    yield p("The gradient points uphill; stepping against it lowers the cost. For linear regression with MSE cost `J(θ) = (1/n)·‖Xθ − y‖²`, the gradient is `(2/n)·Xᵀ(Xθ − y)`:")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        x = rng.uniform(0, 2, 100)
        y = 4 + 3 * x + rng.normal(0, 0.5, 100)
        X = np.c_[np.ones(100), x]                      # column of 1s for the intercept

        theta = np.zeros(2)
        lr = 0.1
        for step in range(1000):
            grad = 2 / len(y) * X.T @ (X @ theta - y)
            theta -= lr * grad
        print(theta.round(3))                                   # [3.996 2.967] ← gradient descent

        print(np.linalg.lstsq(X, y, rcond=None)[0].round(3))    # [3.996 2.967] ← closed-form least squares: same answer
    ''')
    yield section("The learning rate", "gauge")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        x = rng.uniform(0, 2, 100)
        y = 4 + 3 * x + rng.normal(0, 0.5, 100)
        X = np.c_[np.ones(100), x]

        def final_cost(lr, steps=50):
            theta = np.zeros(2)
            for _ in range(steps):
                theta -= lr * 2 / len(y) * X.T @ (X @ theta - y)
            return np.mean((X @ theta - y) ** 2)

        print(f"{final_cost(0.001):.3g}")   # 34.7 ← too small: still far from the minimum after 50 steps
        print(f"{final_cost(0.1):.3g}")     # 0.248 ← good: at the noise level (0.5² ≈ 0.25)
        print(f"{final_cost(1.0):.3g}")     # 1.36e+60 ← too large: overshoots and diverges
    ''')
    yield table(
        ["Variant", "Gradient computed on", "Trade-off"],
        ["Batch gradient descent", "All n examples each step", "Exact, smooth; slow for large n"],
        ["Stochastic (SGD)", "One example each step", "Cheap, noisy steps — the noise can escape shallow bumps"],
        ["Mini-batch", "A batch of 32–1024 examples", "The practical default: vectorised and reasonably smooth"],
    )
    yield ul(
        "**Scale features** first — with very different scales the cost surface is a long narrow valley and gradient descent zig-zags.",
        "Linear and logistic regression costs are **convex**: any minimum is the global minimum. Neural-network losses are not (see **Deep Learning** for momentum, Adam and learning-rate schedules).",
        "Stop when the cost stops improving on validation data (**early stopping**) or after a fixed number of epochs.",
    )
    yield qa("What happens if the learning rate is too high or too low?",
             "Too low: tiny steps, very slow convergence, may stall. Too high: steps overshoot the minimum, the cost oscillates or diverges to infinity. Try values on a log scale (0.001, 0.01, 0.1…) and watch the training curve.")
    yield qa("Why is log-loss used for classification instead of MSE?",
             "It is the negative log-likelihood of a Bernoulli model, so minimising it gives maximum-likelihood probabilities. Combined with a sigmoid it is convex in the weights and gives large gradients when the model is confidently wrong; MSE with a sigmoid is non-convex and its gradients vanish on confident mistakes.")
    yield qa("Batch vs stochastic vs mini-batch gradient descent?",
             "They differ in how many examples are used per update: all of them (accurate but slow), one (fast, noisy), or a small batch (the usual compromise that uses vectorised hardware well).")


@topic(G, "bias-variance", "Bias–Variance & Overfitting", "scale")
def _():
    yield lead("A model's expected error on new data splits into **bias** (wrong assumptions), **variance** (sensitivity to the particular training set) and **irreducible noise**. Making a model more flexible trades bias for variance.")
    yield formula("E[(y − f̂(x))²] = Bias[f̂(x)]² + Var[f̂(x)] + σ²")
    yield table(
        ["Term", "Meaning", "Too much of it looks like"],
        ["Bias²", "How far the *average* model (over many training sets) is from the truth", "Underfitting: a straight line through a curve"],
        ["Variance", "How much the model changes when trained on a different sample", "Overfitting: wiggly fit that chases noise"],
        ["σ² (irreducible)", "Noise in `y` itself", "A floor no model can go below"],
    )
    yield section("See it: polynomial degree", "chart-line")
    yield p("Fit polynomials of increasing degree to 20 noisy points from a sine curve and measure the error on 200 fresh points:")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import root_mean_squared_error
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import PolynomialFeatures

        rng = np.random.default_rng(1)
        def sample(n):
            x = rng.uniform(0, 1, n)
            return x.reshape(-1, 1), np.sin(2 * np.pi * x) + rng.normal(0, 0.2, n)

        X_tr, y_tr = sample(20)
        X_te, y_te = sample(200)

        def errors(degree):
            m = make_pipeline(PolynomialFeatures(degree), LinearRegression()).fit(X_tr, y_tr)
            return round(root_mean_squared_error(y_tr, m.predict(X_tr)), 2), round(root_mean_squared_error(y_te, m.predict(X_te)), 2)

        print(errors(1))    # (0.37, 0.52) ← underfit: both errors high
        print(errors(4))    # (0.18, 0.25) ← good: both near the noise level 0.2
        print(errors(15))   # (0.16, 1.97) ← overfit: lowest training error, test error explodes
    ''')
    yield section("Measure bias and variance directly", "math")
    yield p("Repeat an experiment on 300 different training sets and look at the predictions at fixed points: bias² is how far their *average* is from the truth, variance is how much they scatter. k-nearest-neighbour regression makes the trade-off easy to see — small `k` is flexible, large `k` averages a lot:")
    yield code('''
        import numpy as np
        from sklearn.neighbors import KNeighborsRegressor

        rng = np.random.default_rng(0)
        x_grid = np.linspace(0.05, 0.95, 50).reshape(-1, 1)
        truth = np.sin(2 * np.pi * x_grid).ravel()

        def bias_variance(k, runs=300, n=50):
            preds = []
            for _ in range(runs):                                   # 300 independent training sets
                x = rng.uniform(0, 1, n)
                y = np.sin(2 * np.pi * x) + rng.normal(0, 0.3, n)   # noise σ² = 0.09
                preds.append(KNeighborsRegressor(n_neighbors=k).fit(x.reshape(-1, 1), y).predict(x_grid))
            preds = np.array(preds)
            bias2 = np.mean((preds.mean(axis=0) - truth) ** 2)
            var = np.mean(preds.var(axis=0))
            return round(float(bias2), 3), round(float(var), 3), round(float(bias2 + var), 3)

        print(bias_variance(1))    # (0.0, 0.094, 0.095) ← (bias², variance, sum): very flexible → variance dominates
        print(bias_variance(5))    # (0.0, 0.023, 0.024) ← the sweet spot
        print(bias_variance(25))   # (0.07, 0.02, 0.09) ← averages over half the data → bias dominates
    ''')
    yield p("Expected test error is this sum plus the noise σ² = 0.09 — the sum is U-shaped in `k`, exactly the curve in every textbook.")
    yield section("Fixes", "tool")
    yield table(
        ["Underfitting (high bias)", "Overfitting (high variance)"],
        ["More flexible model (higher degree, deeper trees, boosting)", "More training data"],
        ["Better / more features", "Regularisation (L1/L2), pruning / `max_depth`, `min_samples_leaf`"],
        ["Less regularisation", "Fewer features, feature selection"],
        ["Train longer (if not converged)", "Bagging / random forests; early stopping"],
    )
    yield section("Learning curves", "chart-arrows-vertical")
    yield p("A learning curve plots training and validation scores against training-set size. It tells you whether **more data** would help:")
    yield code_out('''
        import numpy as np
        from sklearn.datasets import load_digits
        from sklearn.model_selection import learning_curve
        from sklearn.naive_bayes import GaussianNB
        from sklearn.svm import SVC

        X, y = load_digits(return_X_y=True)
        sizes = [100, 400, 800, 1400]
        for name, model in [("naive bayes", GaussianNB()), ("svc", SVC(gamma=0.001))]:
            n, train, val = learning_curve(model, X, y, train_sizes=sizes, cv=5)
            print(name, train.mean(axis=1).round(2).tolist(), val.mean(axis=1).round(2).tolist())
    ''', out='''
naive bayes [1.0, 0.95, 0.89, 0.87] [0.59, 0.77, 0.79, 0.81]
svc [0.99, 1.0, 1.0, 1.0] [0.83, 0.91, 0.95, 0.97]
''')
    yield p("Naive Bayes: the curves converge around 0.8–0.87 — adding data barely helps (bias-limited). SVC: training accuracy stays near 1.0 while validation keeps climbing — more data still pays off.")
    yield ul(
        "**Both curves plateau low and close together** → high bias: more data won't help; use a more flexible model or better features.",
        "**Large gap that narrows as data grows** → high variance: more data (or regularisation) will help.",
    )
    yield section("Validation curves", "adjustments-horizontal")
    yield p("A validation curve plots scores against one hyperparameter — here the maximum depth of a decision tree. Training accuracy keeps rising with depth; validation accuracy peaks and then falls — the classic overfitting picture:")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.model_selection import validation_curve
        from sklearn.tree import DecisionTreeClassifier

        X, y = load_breast_cancer(return_X_y=True)
        depths = [1, 2, 3, 5, 8, 12]
        train, val = validation_curve(DecisionTreeClassifier(random_state=0), X, y,
                                      param_name="max_depth", param_range=depths, cv=5)
        print(train.mean(axis=1).round(3).tolist())   # [0.924, 0.952, 0.974, 0.991, 1.0, 1.0]
        print(val.mean(axis=1).round(3).tolist())     # [0.9, 0.928, 0.917, 0.916, 0.916, 0.917]
    ''')
    yield note("Very large neural networks can show **double descent** — test error falls again past the point where the model can fit the training data exactly. It doesn't overturn bias–variance for classic models; see **Deep Learning**.")
    yield qa("Explain the bias–variance trade-off.",
             "Expected test error = bias² + variance + irreducible noise. Simple models make strong assumptions (high bias) but barely change between training sets (low variance); flexible models are the reverse. Increasing flexibility first lowers total error (bias falls) and then raises it (variance dominates). The goal is the sweet spot, found with validation data.")
    yield qa("How can you tell whether a model is overfitting or underfitting?",
             "Compare training and validation error. Both high and close → underfitting. Training much lower than validation → overfitting. Learning curves show whether more data would close the gap.")
    yield qa("Does adding more data fix underfitting?",
             "No. Underfitting is a bias problem: the model can't represent the pattern even with infinite data. It needs more capacity or better features. More data mainly reduces variance.")


@topic(G, "regularization", "Regularization: L1, L2 & Elastic Net", "adjustments")
def _():
    yield lead("Regularisation adds a penalty on model complexity to the training objective, trading a little bias for a large reduction in variance. For linear models the penalty is on the size of the weights.")
    yield formula("Ridge (L2):  Σ(y − ŷ)² + α·Σ wⱼ²        Lasso (L1):  (1/2n)·Σ(y − ŷ)² + α·Σ|wⱼ|")
    yield formula("Elastic Net:  (1/2n)·Σ(y − ŷ)² + α·[ ρ·Σ|wⱼ| + ((1 − ρ)/2)·Σ wⱼ² ]        ρ = l1_ratio")
    yield p("These are scikit-learn's exact objectives — note `Ridge` uses the plain sum of squares while `Lasso`/`ElasticNet` divide by 2n, so the same `alpha` means different strengths in each. The intercept is never penalised. Larger `alpha` → stronger penalty → smaller weights → simpler model.")
    yield table(
        ["", "L2 — Ridge", "L1 — Lasso", "Elastic Net"],
        ["Effect on weights", "Shrinks all toward 0, rarely exactly 0", "Sets many **exactly to 0** (feature selection)", "Sparse, but more stable"],
        ["Correlated features", "Spreads weight across them", "Picks one somewhat arbitrarily", "Tends to keep or drop the group together"],
        ["Solution", "Closed form; always unique", "No closed form (coordinate descent)", "Coordinate descent"],
        ["Use when", "Many small effects, multicollinearity", "You expect few relevant features", "Many correlated features, want sparsity"],
    )
    yield code_out('''
        import numpy as np
        from sklearn.datasets import make_regression
        from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge

        X, y = make_regression(n_samples=50, n_features=10, n_informative=3, noise=10, random_state=0)

        for model in [LinearRegression(), Ridge(alpha=10), Lasso(alpha=5), ElasticNet(alpha=1, l1_ratio=0.9)]:
            w = model.fit(X, y).coef_
            print(f"{type(model).__name__:16} zeros={np.sum(w == 0):2}  |w|={np.abs(w).sum():7.1f}  {w.round(1).tolist()}")
    ''', out='''
LinearRegression zeros= 0  |w|=  192.9  [-1.5, 2.9, 97.2, 45.2, -0.5, -0.7, 2.1, -0.8, 1.3, 40.7]
Ridge            zeros= 0  |w|=  163.5  [0.3, -3.6, 74.4, 37.9, 1.8, -0.8, 7.3, -1.4, 5.9, 30.2]
Lasso            zeros= 7  |w|=  164.2  [-0.0, 0.0, 90.9, 39.2, -0.0, 0.0, 0.0, -0.0, 0.0, 34.1]
ElasticNet       zeros= 4  |w|=  165.6  [-0.0, -0.0, 83.8, 40.0, 0.0, -0.0, 4.4, -0.6, 3.2, 33.7]
''')
    yield p("Only features 2, 3 and 9 are informative. Lasso keeps exactly those three (`-0.0` is still zero), Elastic Net keeps them plus a few small weights, Ridge shrinks everything but zeroes nothing.")
    yield section("Why L1 gives exact zeros", "vector")
    yield p("Geometrically, penalised regression finds where the loss contours first touch the constraint region. The L1 region `|w₁| + |w₂| ≤ t` is a diamond with corners **on the axes**, so the contact point is often a corner where some weights are exactly 0; the L2 region is a circle with no corners. Algebraically, the L1 penalty's pull toward zero is a constant `α` however small the weight, while the L2 pull `2αw` fades as `w` shrinks.")
    yield code_out('''
        import numpy as np
        from sklearn.datasets import make_regression
        from sklearn.linear_model import Lasso, Ridge

        X, y = make_regression(n_samples=50, n_features=10, n_informative=3, noise=10, random_state=0)
        for a in (0.1, 1, 10, 100):
            print(a, np.sum(Lasso(alpha=a).fit(X, y).coef_ != 0), round(np.abs(Ridge(alpha=a).fit(X, y).coef_).sum(), 1))
    ''', out='''
0.1 10 192.3
1 7 187.7
10 3 163.5
100 0 73.2
''')
    yield p("Lasso keeps fewer non-zero weights as `alpha` grows; Ridge's weights shrink smoothly but stay non-zero.")
    yield warn("Scale features before penalised models. The penalty treats every weight the same, so a feature measured in grams (large values, tiny weight) is penalised far less than the same feature in kilograms. Put a `StandardScaler` in the pipeline.")
    yield section("Regularisation elsewhere", "adjustments-alt")
    yield table(
        ["Model", "Knob", "Direction"],
        ["`LogisticRegression`, `SVC`, `LinearSVC`", "`C` = 1 / (regularisation strength)", "**Smaller** `C` = stronger regularisation (L2 by default!)"],
        ["`Ridge`, `Lasso`, `ElasticNet`", "`alpha`", "Larger `alpha` = stronger"],
        ["Decision trees / forests", "`max_depth`, `min_samples_leaf`, `ccp_alpha` (pruning)", "Shallower / bigger leaves = stronger"],
        ["Gradient boosting", "`learning_rate`, number of trees, subsampling, early stopping", "Smaller steps + early stopping = stronger"],
        ["Neural networks", "Weight decay, dropout, early stopping, data augmentation", "See **Deep Learning**"],
    )
    yield qa("Why does L1 regularisation produce sparse models while L2 doesn't?",
             "The L1 penalty's gradient has constant magnitude α, so it keeps pushing small weights all the way to exactly zero; its constraint region has corners on the axes where solutions tend to land. L2's push is proportional to the weight, so weights shrink toward zero but essentially never reach it.")
    yield qa("What happens as the regularisation strength goes to 0 and to infinity?",
             "At 0 you get the unregularised model (ordinary least squares), which may overfit. As it grows to infinity all weights are forced to 0 and the model predicts a constant (the intercept) — maximum bias.")
    yield qa("In scikit-learn's LogisticRegression, does C=100 mean strong regularisation?",
             "No — `C` is the *inverse* of the regularisation strength, so `C=100` is weak regularisation and `C=0.01` strong. Note also that `LogisticRegression` is L2-regularised by default (`C=1.0`).")
