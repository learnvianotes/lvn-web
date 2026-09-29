from kit import *
from mlkit import code_out

G = "Supervised Learning"


@topic(G, "linear-regression", "Linear & Polynomial Regression", "chart-line")
def _():
    yield lead("Linear regression predicts a number as a weighted sum of the features. It is fast, interpretable, the baseline for every regression problem — and, with polynomial features, it can fit curves too.")
    yield formula("ŷ = w₀ + w₁x₁ + w₂x₂ + … + wₚxₚ")
    yield section("Ordinary least squares", "math")
    yield p("OLS chooses the weights that minimise the sum of squared residuals `Σ(yᵢ − ŷᵢ)²`. The minimiser has a closed form, the **normal equation** (in practice solved with a stable least-squares routine rather than an explicit inverse):")
    yield formula("w = (XᵀX)⁻¹ Xᵀ y        (X includes a column of 1s for the intercept)")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression

        rng = np.random.default_rng(0)
        X = rng.normal(size=(100, 2))
        y = 1.5 + 2.0 * X[:, 0] - 3.0 * X[:, 1] + rng.normal(0, 0.5, size=100)

        Xb = np.c_[np.ones(len(X)), X]
        w = np.linalg.solve(Xb.T @ Xb, Xb.T @ y)           # normal equation
        print(w.round(3))                                   # [ 1.418  1.946 -2.913] ← [intercept, w1, w2]

        m = LinearRegression().fit(X, y)
        print(round(m.intercept_, 3), m.coef_.round(3))     # 1.418 [ 1.946 -2.913] ← identical
        print(round(m.score(X, y), 3))                      # 0.97 ← R² on the training data
    ''')
    yield section("Reading the coefficients", "eye")
    yield p("`wⱼ` is the expected change in `ŷ` when `xⱼ` increases by one unit **with the other features held fixed**. Two cautions: coefficients depend on the feature's units (standardise features to compare magnitudes), and they describe association in this data, not cause and effect.")
    yield section("Assumptions (and what breaks when they fail)", "checklist")
    yield table(
        ["Assumption", "Check", "If violated"],
        ["**Linearity** — `E[y | x]` is linear in the parameters", "Residuals vs fitted values show no pattern", "Biased predictions → transform features, add polynomial terms, or use a non-linear model"],
        ["**Independent errors**", "No autocorrelation in residuals over time/order (Durbin-Watson)", "Standard errors too small → time-series models, clustered errors"],
        ["**Homoscedasticity** — constant error variance", "No funnel shape in residuals vs fitted", "Unreliable intervals/p-values → log-transform `y`, weighted least squares, robust standard errors"],
        ["**Normal errors**", "Q–Q plot of residuals", "Only affects small-sample confidence intervals and p-values — not the predictions"],
        ["**No perfect multicollinearity**", "Variance inflation factor (VIF) — above ~5–10 is a warning", "Unstable, uninterpretable coefficients → drop/combine features, Ridge"],
    )
    yield note("Under linearity, exogeneity (`E[ε | X] = 0`) and uncorrelated constant-variance errors, OLS is the **best linear unbiased estimator** (Gauss–Markov). Normality is *not* required for that — only for exact small-sample tests. For p-values and confidence intervals use `statsmodels`' OLS; scikit-learn focuses on prediction.")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression

        rng = np.random.default_rng(0)
        x = np.linspace(0, 10, 60)
        y = x ** 2 + rng.normal(0, 3, size=60)          # the truth is curved

        m = LinearRegression().fit(x.reshape(-1, 1), y)
        resid = y - m.predict(x.reshape(-1, 1))
        print([round(float(r.mean()), 1) for r in np.array_split(resid, 3)])   # [3.6, -7.7, 4.1] ← +, −, +: a pattern = missed curvature
    ''')
    yield p("Multicollinearity check — `x3` is almost `x1 + x2`, so each of them is well predicted by the others:")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression

        rng = np.random.default_rng(0)
        x1, x2 = rng.normal(size=(2, 200))
        x3 = x1 + x2 + rng.normal(0, 0.1, 200)
        X = np.c_[x1, x2, x3]

        def vif(X, j):                                  # VIF_j = 1 / (1 − R²_j), R²_j from regressing x_j on the rest
            others = np.delete(X, j, axis=1)
            r2 = LinearRegression().fit(others, X[:, j]).score(others, X[:, j])
            return 1 / (1 - r2)

        print([round(vif(X, j), 1) for j in range(3)])   # [95.4, 108.2, 189.6]
    ''')
    yield section("Polynomial regression", "chart-arrows")
    yield p("Add powers (and products) of the features, then fit an ordinary linear model. The model is still **linear in its parameters**, so OLS applies unchanged. Choose the degree with cross-validation — too high overfits:")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_score
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import PolynomialFeatures

        rng = np.random.default_rng(0)
        x = rng.uniform(-3, 3, size=(60, 1))
        y = 0.5 * x[:, 0] ** 3 - x[:, 0] ** 2 + rng.normal(0, 2, size=60)

        def cv_rmse(degree):
            model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
            return round(float(-cross_val_score(model, x, y, cv=5, scoring="neg_root_mean_squared_error").mean()), 2)

        print([cv_rmse(d) for d in (1, 2, 3, 6, 12)])   # [4.64, 2.89, 2.34, 2.81, 7.47] ← lowest at the true degree, 3
    ''')
    yield warn("With several features, `PolynomialFeatures(degree=d)` creates every product up to degree d — the column count explodes (10 features, degree 3 → 286 columns). Combine it with scaling and Ridge, or use splines (`SplineTransformer`) or a tree model.")
    yield dodont("Use as a fast, interpretable baseline; when relationships are roughly linear; when you need coefficients to explain.",
                 "Expect it to capture interactions or thresholds you didn't engineer; trust coefficients of correlated features; extrapolate far beyond the training range.")
    yield qa("What is the difference between R² and adjusted R²?",
             "R² never decreases when you add a feature, even a useless one. Adjusted R² = `1 − (1 − R²)(n − 1)/(n − p − 1)` penalises the number of predictors `p`, so it only rises if a new feature helps more than chance would.")
    yield qa("Why not use linear regression for classification?",
             "Its outputs aren't bounded to [0, 1], so they aren't probabilities, and squared error on 0/1 labels lets far-away, correctly classified points drag the boundary. Logistic regression models the log-odds instead and is fitted by maximum likelihood.")
    yield qa("What does multicollinearity do to a linear regression?",
             "Predictions can remain fine, but coefficients become unstable (large standard errors, signs that flip with small data changes) because the model can't tell the correlated features' effects apart. Detect with VIF; fix by dropping or combining features, or with Ridge regularisation.")


@topic(G, "logistic-regression", "Logistic Regression", "percentage")
def _():
    yield lead("Logistic regression is the standard linear **classifier**: it computes a weighted sum of the features and squashes it through the sigmoid to get a probability.")
    yield formula("z = w·x + b        p = P(y = 1 | x) = σ(z) = 1 / (1 + e⁻ᶻ)        log(p / (1 − p)) = z")
    yield p("The model is linear in the **log-odds**. Predict class 1 when `p ≥ 0.5` — equivalently `z ≥ 0` — so the decision boundary `w·x + b = 0` is a straight line (hyperplane). The threshold can and often should be moved (see **ROC, PR, Thresholds & Calibration**).")
    yield code('''
        import numpy as np

        sigmoid = lambda z: 1 / (1 + np.exp(-z))
        print(sigmoid(np.array([-4, -1, 0, 1, 4])).round(3))    # [0.018 0.269 0.5   0.731 0.982]
        print(round(np.log(0.8 / 0.2), 3))                      # 1.386 ← logit: p = 0.8 means z ≈ 1.386
    ''')
    yield section("Training: maximum likelihood = minimum log-loss", "trending-down")
    yield formula("J(w, b) = −(1/n) Σ [ yᵢ log pᵢ + (1 − yᵢ) log(1 − pᵢ) ]        ∂J/∂w = (1/n) Σ (pᵢ − yᵢ) xᵢ")
    yield p("The cost is convex, so solvers (`lbfgs` by default) find the global minimum; there is no closed form. scikit-learn adds an **L2 penalty by default** (`C=1.0`, where smaller `C` = stronger regularisation), so scale your features.")
    yield section("Interpreting a coefficient: odds ratios", "eye")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LogisticRegression

        rng = np.random.default_rng(0)
        hours = rng.uniform(0, 10, 300)
        passed = rng.random(300) < 1 / (1 + np.exp(-1.2 * (hours - 5)))   # true w = 1.2, boundary at 5 h

        m = LogisticRegression(C=np.inf).fit(hours.reshape(-1, 1), passed)   # C=inf → no penalty
        w, b = m.coef_[0, 0], m.intercept_[0]
        print(round(w, 2), round(b, 2))                         # 1.11 -5.79
        print(round(np.exp(w), 2))                              # 3.04 ← each extra hour multiplies the odds of passing by this
        print(round(-b / w, 2))                                 # 5.21 ← hours where p = 0.5 (the decision boundary)
        print(m.predict_proba([[3.0], [7.0]])[:, 1].round(3))   # [0.079 0.88 ]
    ''')
    yield section("A real dataset", "code")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_breast_cancer(return_X_y=True)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)

        clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(X_tr, y_tr)
        print(round(clf.score(X_te, y_te), 3))                  # 0.958
        print(clf.predict_proba(X_te[:3]).round(3).tolist())    # [[0.004, 0.996], [1.0, 0.0], [1.0, 0.0]] ← [P(class 0), P(class 1)] per row
        print(clf.predict(X_te[:3]))                            # [1 0 0]
    ''')
    yield section("More than two classes", "category")
    yield p("With the default `lbfgs` solver, scikit-learn fits a **multinomial** (softmax) model: one weight vector per class, `P(y = k | x) = e^{zₖ} / Σⱼ e^{zⱼ}`. The alternative, one-vs-rest, trains one binary model per class (`OneVsRestClassifier`).")
    yield code('''
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression

        X, y = load_iris(return_X_y=True)
        clf = LogisticRegression(max_iter=1000).fit(X, y)
        proba = clf.predict_proba(X[[0, 75, 140]])
        print(proba.round(3).tolist())             # [[0.982, 0.018, 0.0], [0.005, 0.92, 0.075], [0.0, 0.02, 0.98]]
        print(proba.sum(axis=1).round(6).tolist()) # [1.0, 1.0, 1.0] ← each row sums to 1
        print(clf.coef_.shape)                     # (3, 4) ← one weight vector per class
    ''')
    yield dodont("Use as the first classifier on any problem: fast, well-calibrated probabilities, interpretable coefficients, works well on high-dimensional sparse data (text).",
                 "Expect curved boundaries without engineered features (polynomials, splines, interactions); forget to scale features when regularising; read an unpenalised model's coefficients on perfectly separable data (they diverge).")
    yield qa("Why is it called regression if it's a classifier?",
             "It is a regression model for the **log-odds** of the positive class (a generalised linear model with a logit link). Thresholding the resulting probability turns it into a classifier.")
    yield qa("How do you interpret a logistic regression coefficient?",
             "A one-unit increase in the feature adds `w` to the log-odds, i.e. multiplies the odds `p/(1−p)` by `e^w`, holding other features fixed. With standardised features, it's per standard deviation.")
    yield qa("Is the decision boundary of logistic regression linear?",
             "Yes — `w·x + b = 0` is a hyperplane in the feature space it is given. Adding polynomial or interaction features makes the boundary curved in the original space while the model stays linear in its parameters.")


@topic(G, "knn", "k-Nearest Neighbors", "circles-relation")
def _():
    yield lead("k-NN makes a prediction from the `k` training points closest to the query: a majority vote for classification, an average for regression. There is no training step — the model *is* the data.")
    yield steps(
        ("Store", "Keep the (scaled) training data."),
        ("Measure", "Compute the distance from the query to every training point."),
        ("Select", "Take the `k` nearest."),
        ("Predict", "Majority class (optionally distance-weighted) or mean target."),
    )
    yield table(
        ["Distance", "Formula", "Notes"],
        ["Euclidean (L2)", "`√Σ(aᵢ − bᵢ)²`", "Default (Minkowski with p = 2)"],
        ["Manhattan (L1)", "`Σ|aᵢ − bᵢ|`", "Less dominated by one large difference"],
        ["Minkowski", "`(Σ|aᵢ − bᵢ|ᵖ)^(1/p)`", "p = 1 Manhattan, p = 2 Euclidean"],
        ["Cosine distance", "`1 − a·b / (‖a‖‖b‖)`", "Direction only — text and embeddings"],
    )
    yield code('''
        import numpy as np
        from sklearn.neighbors import KNeighborsClassifier

        X = np.array([[1, 1], [2, 1], [1, 2], [6, 5], [7, 7], [6, 6]])
        y = np.array(["red", "red", "red", "blue", "blue", "blue"])
        query = np.array([3, 3])

        d = np.sqrt(((X - query) ** 2).sum(axis=1))
        nearest = np.argsort(d)[:3]
        print(d.round(2))                  # [2.83 2.24 2.24 3.61 5.66 4.24]
        print(nearest, y[nearest])         # [1 2 0] ['red' 'red' 'red'] ← vote: red wins
        print(KNeighborsClassifier(n_neighbors=3).fit(X, y).predict([query]))   # ['red']
    ''')
    yield section("Choosing k", "adjustments")
    yield p("Small `k` → jagged boundary that follows noise (low bias, high variance); large `k` → over-smoothed (high bias). `k = 1` always scores 100% on its own training data. Pick `k` by cross-validation, **with the features scaled**:")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.model_selection import cross_val_score
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_breast_cancer(return_X_y=True)
        scores = {k: cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k)), X, y, cv=5).mean()
                  for k in (1, 3, 7, 15, 51, 151)}
        print({k: round(float(s), 3) for k, s in scores.items()})   # {1: 0.954, 3: 0.96, 7: 0.97, 15: 0.961, 51: 0.951, 151: 0.912}
    ''')
    yield section("The curse of dimensionality", "cube")
    yield p("As the number of features grows, space becomes vast and empty. Distances between random points **concentrate**: the nearest and the farthest neighbour end up almost equally far away, so “nearest” stops meaning “similar”.")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        def contrast(d, n=500):
            X = rng.uniform(size=(n, d))
            dist = np.linalg.norm(X - rng.uniform(size=d), axis=1)
            return round(float((dist.max() - dist.min()) / dist.min()), 2)     # relative gap farthest vs nearest

        print([contrast(d) for d in (2, 10, 100, 1000)])   # [40.73, 4.65, 0.36, 0.11] ← shrinks toward 0 as dimensions grow
    ''')
    yield p("Another view: to capture a fraction `r` of uniformly spread data with a small cube around a point, the cube's side must be `r^(1/d)`. For 1% of the data that is 0.01 of the range in 1-D, 0.63 in 10-D and 0.95 in 100-D — the “neighbourhood” spans almost the whole range of every feature.")
    yield code('''
        print([round(0.01 ** (1 / d), 2) for d in (1, 10, 100)])   # [0.01, 0.63, 0.95]
    ''')
    yield ul(
        "Distance-based methods (k-NN, k-means, RBF kernels) suffer most.",
        "The data needed to cover the space grows exponentially with the dimension; models overfit more easily.",
        "Fixes: feature selection, dimensionality reduction (PCA), more data, models that don't rely on raw distances (trees, linear models).",
        "Real data usually lies near a lower-dimensional structure, which is why k-NN still works on, e.g., 64-pixel digits.",
    )
    yield dodont("Use for small-to-medium, low-dimensional data with meaningful distances; as a baseline; for similarity search (with approximate-neighbour indexes at scale).",
                 "Use without scaling; with many irrelevant features; when predictions must be fast on large training sets — each prediction scans the data (KD/ball trees help only in low dimensions).")
    yield qa("How does k affect the bias–variance trade-off in k-NN?",
             "Small k: flexible, low bias, high variance (k = 1 memorises the training set). Large k: smoother, higher bias, lower variance; k = n predicts the majority class everywhere. Choose k by cross-validation; an odd k avoids ties in binary problems.")
    yield qa("What is the curse of dimensionality?",
             "In high dimensions data becomes sparse and distances concentrate, so neighbourhoods are no longer local and the amount of data needed to generalise grows exponentially. It hurts distance-based methods most; the remedies are fewer or better features, dimensionality reduction and more data.")


@topic(G, "naive-bayes", "Naive Bayes", "chart-bar")
def _():
    yield lead("Naive Bayes applies Bayes' rule with one strong simplification — features are **independent given the class** — which makes it extremely fast and surprisingly good for text.")
    yield formula("P(y | x₁, …, xₚ) ∝ P(y) · P(x₁ | y) · P(x₂ | y) · … · P(xₚ | y)")
    yield p("Pick the class with the largest right-hand side. `P(y)` is the class frequency; each `P(xᵢ | y)` is estimated separately from the training data — that's why training is a single counting pass.")
    yield table(
        ["Variant", "Feature model", "Use for"],
        ["`MultinomialNB`", "Word counts / frequencies", "Text classification (bag-of-words, TF-IDF)"],
        ["`ComplementNB`", "Like multinomial, estimated from the complement of each class", "Imbalanced text classes"],
        ["`BernoulliNB`", "Binary present/absent features", "Short texts, binary flags"],
        ["`GaussianNB`", "Each feature normal within each class", "Continuous features"],
        ["`CategoricalNB`", "Categorical features", "Label-encoded categories"],
    )
    yield section("Worked example: spam", "mail")
    yield p("Two spam and two ham messages; classify “free money meeting”. With Laplace smoothing (`α = 1`), `P(word | class) = (count + 1) / (words in class + vocabulary size)`. Each class has 5 words and the vocabulary has 7:")
    yield code('''
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB

        docs = ["free money now", "free prize", "meeting now", "project meeting notes"]
        labels = ["spam", "spam", "ham", "ham"]

        # by hand: prior 0.5 each; counts of free, money, meeting in each class
        spam = 0.5 * (2 + 1) / 12 * (1 + 1) / 12 * (0 + 1) / 12
        ham = 0.5 * (0 + 1) / 12 * (0 + 1) / 12 * (2 + 1) / 12
        print(round(spam / (spam + ham), 3))            # 0.667 ← P(spam | "free money meeting")

        vec = CountVectorizer()
        nb = MultinomialNB(alpha=1.0).fit(vec.fit_transform(docs), labels)
        print(nb.classes_, nb.predict_proba(vec.transform(["free money meeting"])).round(3))   # ['ham' 'spam'] [[0.333 0.667]]
    ''')
    yield section("Two practical details", "settings")
    yield ul(
        "**Zero-frequency problem** — without smoothing, “meeting” never appeared in spam, so `P(meeting | spam) = 0` and one unseen word wipes out all other evidence. Laplace/additive smoothing (`alpha`) adds a pseudo-count to every word.",
        "**Log space** — multiplying hundreds of small probabilities underflows to 0, so implementations sum log-probabilities instead.",
    )
    yield section("Gaussian Naive Bayes", "chart-bell-curve")
    yield formula("P(xᵢ | y) = (1 / √(2πσ²ᵧᵢ)) · exp(−(xᵢ − μᵧᵢ)² / (2σ²ᵧᵢ))")
    yield code('''
        from sklearn.datasets import load_wine
        from sklearn.model_selection import cross_val_score
        from sklearn.naive_bayes import GaussianNB

        X, y = load_wine(return_X_y=True)
        print(round(cross_val_score(GaussianNB(), X, y, cv=5).mean(), 3))   # 0.966 ← no scaling or tuning needed
    ''')
    yield dodont("Use for text classification, very large or streaming data (`partial_fit`), tiny training sets, and as a fast baseline.",
                 "Trust its probabilities — correlated features are counted as independent evidence, so outputs are pushed toward 0 and 1 (calibrate them if you need probabilities). Expect it to learn feature interactions.")
    yield p("The **Data Science** notes build a full TF-IDF + Naive Bayes text classifier.")
    yield qa("Why is Naive Bayes called naive?",
             "It assumes all features are conditionally independent given the class, which is almost never true (words like “New” and “York” co-occur). The assumption makes estimation trivial, and classification often still works because only the ranking of class scores matters, not their exact values.")
    yield qa("What is Laplace smoothing?",
             "Adding a pseudo-count (usually 1) to every feature count per class so no conditional probability is exactly zero. Otherwise a single word unseen in a class during training would force that class's probability to zero for any document containing it.")


@topic(G, "svm", "Support Vector Machines", "separator-vertical")
def _():
    yield lead("An SVM finds the separating hyperplane with the **widest margin** between classes. Only the points on or inside the margin — the support vectors — define it. Kernels extend the same idea to non-linear boundaries.")
    yield formula("decision: f(x) = w·x + b        predict sign(f(x))        margin width = 2 / ‖w‖")
    yield section("Hard and soft margins", "border-outer")
    yield formula("hard margin: minimise ½‖w‖²  subject to  yᵢ(w·xᵢ + b) ≥ 1  for all i   (yᵢ ∈ {−1, +1})")
    yield formula("soft margin: minimise ½‖w‖² + C · Σ max(0, 1 − yᵢ f(xᵢ))        (hinge loss)")
    yield p("Real data overlaps, so the soft margin lets some points violate the margin at a cost `C`. **Large `C`** punishes violations → narrow margin, fits training data closely (risk of overfitting). **Small `C`** → wider margin, more violations tolerated (more regularisation).")
    yield code('''
        import numpy as np
        from sklearn.datasets import make_blobs
        from sklearn.svm import SVC

        X, y = make_blobs(n_samples=40, centers=2, random_state=6)
        clf = SVC(kernel="linear", C=1000).fit(X, y)          # large C ≈ hard margin on separable data

        print(len(clf.support_vectors_))                               # 3 ← only these points define the boundary
        print(round(2 / np.linalg.norm(clf.coef_[0]), 3))              # 2.284 ← margin width
        print(np.abs(clf.decision_function(clf.support_vectors_)).round(2))   # [1. 1. 1.] ← all on the margin: |f(x)| = 1
    ''')
    yield code('''
        from sklearn.datasets import make_blobs
        from sklearn.svm import SVC

        X, y = make_blobs(n_samples=200, centers=2, cluster_std=2.5, random_state=0)   # overlapping classes
        print([len(SVC(kernel="linear", C=c).fit(X, y).support_) for c in (0.01, 1, 100)])   # [114, 97, 96] ← smaller C, wider margin, more SVs
    ''')
    yield section("Kernels", "topology-star-3")
    yield p("The dual form of the SVM only uses dot products between points. Replacing `xᵢ·xⱼ` with a **kernel** `K(xᵢ, xⱼ)` is equivalent to working in a higher-dimensional feature space without ever computing it — the **kernel trick**.")
    yield table(
        ["Kernel", "K(x, x′)", "Notes"],
        ["Linear", "`x·x′`", "High-dimensional sparse data (text); use `LinearSVC` for speed"],
        ["Polynomial", "`(γ x·x′ + r)ᵈ`", "Feature interactions up to degree d"],
        ["RBF (Gaussian)", "`exp(−γ‖x − x′‖²)`", "Default; smooth, flexible boundaries"],
        ["Sigmoid", "`tanh(γ x·x′ + r)`", "Rarely the best choice"],
    )
    yield code_out('''
        from sklearn.datasets import make_moons
        from sklearn.model_selection import cross_val_score
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        X, y = make_moons(n_samples=300, noise=0.2, random_state=0)       # two interleaved half-circles
        for kernel in ("linear", "poly", "rbf"):
            acc = cross_val_score(make_pipeline(StandardScaler(), SVC(kernel=kernel)), X, y, cv=5).mean()
            print(kernel, round(acc, 3))
    ''', out='''
linear 0.837
poly 0.87
rbf 0.97
''')
    yield p("`gamma` sets how far one training point's influence reaches. Small `gamma` → smooth boundary; large `gamma` → every point gets its own little island (overfitting):")
    yield code_out('''
        from sklearn.datasets import make_moons
        from sklearn.model_selection import cross_validate
        from sklearn.svm import SVC

        X, y = make_moons(n_samples=300, noise=0.2, random_state=0)
        for gamma in (0.1, 1, 100):
            r = cross_validate(SVC(gamma=gamma), X, y, cv=5, return_train_score=True)
            print(gamma, round(r["train_score"].mean(), 3), round(r["test_score"].mean(), 3))
    ''', out='''
0.1 0.852 0.853
1 0.982 0.983
100 0.991 0.953
''')
    yield section("Practical notes", "notes")
    yield ul(
        "**Scale features** — the margin and RBF distances depend on units.",
        "Tune `C` and `gamma` together on a log grid (e.g. 0.01 … 1000).",
        "Kernel SVM training scales between O(n²) and O(n³): fine for thousands of rows, impractical for millions → `LinearSVC`, `SGDClassifier(loss=\"hinge\")`, or kernel approximation (`Nystroem`) + a linear model.",
        "No native probabilities: `SVC(probability=True)` fits Platt scaling with internal cross-validation — slower, and its argmax can disagree with `predict`. Use `decision_function` for ranking.",
        "Regression version: `SVR` fits a tube of width `ε` and ignores errors inside it.",
    )
    yield qa("What are support vectors?",
             "The training points that lie on the margin or violate it. They alone determine the hyperplane; removing any other point leaves the model unchanged — which is why SVMs are memory-efficient at prediction time.")
    yield qa("What is the kernel trick?",
             "Algorithms that only need dot products can replace them with a kernel function equal to a dot product in some (possibly infinite-dimensional) feature space. You get a non-linear boundary in the original space at the cost of computing `K(x, x′)`, without building the high-dimensional features.")
    yield qa("How do C and gamma affect an RBF SVM?",
             "`C` trades margin width against training errors — larger `C` fits the training data harder. `gamma` controls the reach of each point's influence — larger `gamma` gives wigglier boundaries. Both large → overfitting; both small → underfitting.")


@topic(G, "decision-trees", "Decision Trees", "binary-tree")
def _():
    yield lead("A decision tree asks a sequence of yes/no questions about single features (`petal width ≤ 0.8?`) and predicts from the leaf it reaches. Trees are easy to read, need no scaling, and capture non-linear effects and interactions — but a single deep tree overfits.")
    yield section("How a split is chosen", "git-branch")
    yield p("CART (scikit-learn's algorithm) grows the tree greedily: at each node it tries every feature and threshold and keeps the split that most reduces **impurity**, then recurses until a stopping rule.")
    yield formula("Gini = 1 − Σₖ pₖ²        Entropy H = −Σₖ pₖ log₂ pₖ        Information gain = H(parent) − Σⱼ (nⱼ / n)·H(childⱼ)")
    yield code('''
        import numpy as np

        def gini(counts):
            p = np.array(counts) / sum(counts)
            return 1 - np.sum(p ** 2)

        def entropy(counts):
            p = np.array([c for c in counts if c]) / sum(counts)
            return -np.sum(p * np.log2(p))

        parent = [5, 5]                         # 5 yes, 5 no
        left, right = [4, 1], [1, 4]            # candidate split

        w = [sum(left) / 10, sum(right) / 10]
        print(gini(parent), round(entropy(parent), 3))                                   # 0.5 1.0 ← maximally mixed
        print(round(gini(left), 3), round(entropy(left), 3))                             # 0.32 0.722
        print(round(gini(parent) - (w[0] * gini(left) + w[1] * gini(right)), 3))         # 0.18 ← Gini decrease
        print(round(entropy(parent) - (w[0] * entropy(left) + w[1] * entropy(right)), 3))   # 0.278 ← information gain
    ''')
    yield p("Gini and entropy almost always choose the same splits; Gini is slightly cheaper (no logarithm). Regression trees use the reduction in **squared error (variance)** instead and predict the mean of each leaf.")
    yield section("A readable model", "eye")
    yield code_out('''
        from sklearn.datasets import load_iris
        from sklearn.tree import DecisionTreeClassifier, export_text

        iris = load_iris()
        tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(iris.data, iris.target)
        print(export_text(tree, feature_names=iris.feature_names))
        print(tree.predict([[5.0, 3.0, 5.0, 1.8]]))
    ''', out='''
|--- petal width (cm) <= 0.80
|   |--- class: 0
|--- petal width (cm) >  0.80
|   |--- petal width (cm) <= 1.75
|   |   |--- class: 1
|   |--- petal width (cm) >  1.75
|   |   |--- class: 2

[2]
''')
    yield section("Overfitting and pruning", "cut")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.model_selection import train_test_split
        from sklearn.tree import DecisionTreeClassifier

        X, y = load_breast_cancer(return_X_y=True)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)

        def report(**params):
            t = DecisionTreeClassifier(random_state=0, **params).fit(X_tr, y_tr)
            return t.get_depth(), int(t.get_n_leaves()), round(t.score(X_tr, y_tr), 3), round(t.score(X_te, y_te), 3)

        print(report())                        # (5, 18, 1.0, 0.902) ← (depth, leaves, train acc, test acc): grown until pure
        print(report(max_depth=3))             # (3, 8, 0.977, 0.916) ← pre-pruning
        print(report(min_samples_leaf=10))     # (4, 8, 0.955, 0.916)
        print(report(ccp_alpha=0.01))          # (3, 6, 0.972, 0.923) ← cost-complexity (post-)pruning
    ''')
    yield table(
        ["Knob", "Effect"],
        ["`max_depth`", "Limits the number of questions per path"],
        ["`min_samples_split` / `min_samples_leaf`", "No tiny leaves that memorise single rows"],
        ["`max_leaf_nodes`", "Caps total complexity"],
        ["`ccp_alpha`", "Grows the full tree, then prunes branches whose impurity reduction doesn't justify their size"],
    )
    yield dodont("Use when you need a transparent model or rules, mixed feature types, non-linear effects — and as the building block of random forests and gradient boosting.",
                 "Rely on one deep tree: it has high variance (small data changes → a different tree), makes axis-aligned staircase boundaries, and cannot extrapolate beyond the training range of the target.")
    yield warn("scikit-learn's trees need numeric input — encode categorical features first (they are not handled “natively”, unlike in LightGBM, CatBoost or `HistGradientBoosting*`). Missing values *are* supported since scikit-learn 1.3.")
    yield qa("How does a decision tree decide where to split?",
             "For every feature and candidate threshold it computes the weighted impurity (Gini or entropy for classification, squared error for regression) of the two children and picks the split with the largest impurity decrease. This greedy, one-step-ahead search repeats at each child until a stopping criterion.")
    yield qa("Why do decision trees overfit and how do you prevent it?",
             "Grown to purity, a tree can carve out a leaf for every training point, fitting noise. Prevent it by limiting depth or leaf size, cost-complexity pruning, or by averaging many trees (random forests) or boosting shallow ones.")
    yield qa("Gini impurity vs entropy?",
             "Both measure how mixed a node is (0 = pure). Entropy is information-theoretic and slightly more sensitive to rare classes; Gini avoids a logarithm. They produce nearly identical trees in practice.")


@topic(G, "random-forests", "Bagging & Random Forests", "trees")
def _():
    yield lead("Averaging many high-variance models cancels much of their variance. **Bagging** trains each model on a bootstrap sample; a **random forest** also restricts each split to a random subset of features so the trees are less alike.")
    yield section("Why averaging works", "math-avg")
    yield formula("Var(average of B models) = ρσ² + (1 − ρ)σ² / B        σ² = variance of one model, ρ = correlation between models")
    yield p("More trees shrink the second term toward 0 but the first stays: highly correlated trees can't cancel each other's errors. Random feature subsets lower `ρ` — that is the whole idea of a random forest. Bagging mainly **reduces variance**; it does little for bias, so it suits deep, low-bias trees.")
    yield section("Bootstrap samples and out-of-bag rows", "arrows-shuffle")
    yield p("A bootstrap sample draws n rows **with replacement**. Each row is left out with probability `(1 − 1/n)ⁿ → 1/e ≈ 0.368`, so each tree sees about 63.2% of the distinct rows. The unseen ~36.8% are that tree's **out-of-bag (OOB)** rows — a free validation set.")
    yield code('''
        import numpy as np

        n = 1000
        print(round(1 - (1 - 1 / n) ** n, 4))                   # 0.6323 ← expected share of distinct rows
        rng = np.random.default_rng(0)
        sample = rng.integers(0, n, size=n)                     # one bootstrap sample
        print(len(np.unique(sample)) / n)                       # 0.622
    ''')
    yield section("One tree vs bagging vs random forest", "trees")
    yield code('''
        from sklearn.datasets import make_classification
        from sklearn.ensemble import BaggingClassifier, RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        from sklearn.tree import DecisionTreeClassifier

        X, y = make_classification(n_samples=600, n_features=20, n_informative=6, random_state=1)
        models = {
            "tree": DecisionTreeClassifier(random_state=0),
            "bagging": BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=0),
            "forest": RandomForestClassifier(n_estimators=100, random_state=0),
        }
        print({name: round(float(cross_val_score(m, X, y, cv=5).mean()), 3) for name, m in models.items()})   # {'tree': 0.892, 'bagging': 0.923, 'forest': 0.937}

        rf = RandomForestClassifier(n_estimators=200, oob_score=True, random_state=0).fit(X, y)
        print(round(rf.oob_score_, 3))                          # 0.938 ← OOB accuracy: close to the CV estimate
    ''')
    yield section("Key hyperparameters", "adjustments")
    yield table(
        ["Parameter", "Meaning", "Guidance"],
        ["`n_estimators`", "Number of trees", "More never overfits — it only stops improving; a few hundred is typical"],
        ["`max_features`", "Features considered at each split", "`\"sqrt\"` (classifier default); lower → less correlated trees. Note `RandomForestRegressor` defaults to `1.0` (all features = plain bagging)"],
        ["`max_depth`, `min_samples_leaf`", "Tree size", "Defaults grow full trees; limit them on noisy data"],
        ["`class_weight`", "Weights for imbalanced classes", "`\"balanced\"` or `\"balanced_subsample\"`"],
        ["`n_jobs`", "Parallel training", "Trees are independent — bagging parallelises perfectly"],
    )
    yield warn("`feature_importances_` (mean decrease in impurity) is computed on training data and is biased toward continuous and high-cardinality features. Prefer permutation importance on held-out data (see **Explainability**).")
    yield dodont("Use as a strong, low-effort default for tabular data: little tuning, no scaling, robust to outliers, OOB estimate included.",
                 "Expect it to extrapolate beyond the training range, to be small or fast at prediction time with thousands of deep trees, or to be as interpretable as one tree. `ExtraTreesClassifier` (random thresholds too) is a faster, even more randomised cousin.")
    yield qa("Why does a random forest generalise better than a single decision tree?",
             "Each deep tree has low bias but high variance. Averaging many trees trained on bootstrap samples, with a random subset of features at each split to decorrelate them, cancels much of that variance while keeping the bias low.")
    yield qa("What is the out-of-bag score?",
             "Each tree skips ~37% of the rows in its bootstrap sample. Predicting each row using only the trees that didn't see it gives an almost free validation estimate, similar to cross-validation.")
    yield qa("Can adding more trees to a random forest overfit?",
             "No — adding trees only reduces the variance of the average; the error converges to a limit. The forest can still overfit through its individual trees (too deep on noisy data), which is controlled with depth/leaf-size settings.")


@topic(G, "boosting", "Boosting: AdaBoost & Gradient Boosting", "rocket")
def _():
    yield lead("Boosting builds an ensemble **sequentially**: each new weak model concentrates on what the current ensemble gets wrong. It mainly **reduces bias**, and gradient-boosted trees (XGBoost, LightGBM, CatBoost, scikit-learn's HistGradientBoosting) are the go-to models for tabular data.")
    yield table(
        ["", "Bagging / random forest", "Boosting"],
        ["Training", "Parallel, independent models", "Sequential, each depends on the previous ones"],
        ["Base learners", "Deep, low-bias trees", "Shallow, high-bias trees (stumps to depth ~8)"],
        ["Mainly reduces", "Variance", "Bias (and some variance)"],
        ["Overfits when adding learners?", "No", "**Yes** — control with learning rate and early stopping"],
        ["Sensitivity to noisy labels", "Robust", "More sensitive (keeps chasing hard/mislabelled points)"],
    )
    yield section("AdaBoost", "arrow-up-right")
    yield p("AdaBoost (labels ±1) re-weights the training rows after each round: misclassified rows gain weight, so the next weak learner focuses on them. Each learner gets a vote proportional to its accuracy:")
    yield formula("εₜ = weighted error of learner t        αₜ = ½ · ln((1 − εₜ) / εₜ)        wᵢ ← wᵢ · exp(−αₜ yᵢ hₜ(xᵢ)), then normalise        F(x) = sign(Σₜ αₜ hₜ(x))")
    yield code('''
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.ensemble import AdaBoostClassifier
        from sklearn.model_selection import cross_val_score
        from sklearn.tree import DecisionTreeClassifier

        print([round(float(0.5 * np.log((1 - e) / e)), 3) for e in (0.1, 0.3, 0.5)])   # [1.099, 0.424, 0.0] ← a coin-flip learner (ε = 0.5) gets no vote

        X, y = make_classification(n_samples=600, n_features=20, n_informative=6, random_state=1)
        stump = DecisionTreeClassifier(max_depth=1)
        print(round(cross_val_score(stump, X, y, cv=5).mean(), 3))                                    # 0.827 ← one stump
        print(round(cross_val_score(AdaBoostClassifier(stump, n_estimators=200, random_state=0), X, y, cv=5).mean(), 3))   # 0.94
    ''')
    yield section("Gradient boosting", "trending-down")
    yield formula("Fₘ(x) = Fₘ₋₁(x) + η · hₘ(x)        hₘ is fitted to the negative gradient  −∂L(y, F)/∂F  at Fₘ₋₁")
    yield p("Start from a constant (the mean for squared error), then repeatedly fit a small regression tree to the **pseudo-residuals** and add a shrunken copy of it (learning rate `η`). For squared-error loss the negative gradient is exactly the residual `y − F(x)`; for log-loss it is `y − p`. Other losses give other pseudo-residuals — that's what “gradient” boosting means.")
    yield code_out('''
        import numpy as np
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.tree import DecisionTreeRegressor

        rng = np.random.default_rng(0)
        X = rng.uniform(0, 6, size=(200, 1))
        y = np.sin(X[:, 0]) + rng.normal(0, 0.2, 200)

        lr, F = 0.1, np.full(200, y.mean())                      # start from the mean
        for m in range(100):
            residuals = y - F                                    # negative gradient of ½(y − F)²
            tree = DecisionTreeRegressor(max_depth=2, random_state=0).fit(X, residuals)
            F += lr * tree.predict(X)                            # add a shrunken copy of the tree
            if m in (0, 9, 99):
                print(m + 1, round(np.mean((y - F) ** 2), 4))

        sk = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=2, random_state=0).fit(X, y)
        print(np.allclose(F, sk.predict(X)))                     # ← scikit-learn does the same thing
    ''', out='''
1 0.4458
10 0.1216
100 0.0268
True
''')
    yield section("Learning rate, number of trees and early stopping", "player-stop")
    yield p("A smaller learning rate needs more trees but usually generalises better. Too many trees overfit — so hold out validation data and stop when it stops improving:")
    yield code('''
        from sklearn.datasets import make_classification
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.model_selection import train_test_split

        X, y = make_classification(n_samples=2000, n_features=20, n_informative=6, flip_y=0.1, random_state=0)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)

        full = HistGradientBoostingClassifier(learning_rate=0.3, max_iter=500, early_stopping=False, random_state=0).fit(X_tr, y_tr)
        early = HistGradientBoostingClassifier(learning_rate=0.3, max_iter=500, early_stopping=True,
                                               validation_fraction=0.2, n_iter_no_change=10, random_state=0).fit(X_tr, y_tr)
        print(full.n_iter_, round(full.score(X_tr, y_tr), 3), round(full.score(X_te, y_te), 3))     # 500 1.0 0.858 ← trees, train acc, test acc
        print(early.n_iter_, round(early.score(X_tr, y_tr), 3), round(early.score(X_te, y_te), 3))  # 21 0.975 0.862 ← stopped early
    ''')
    yield section("The modern libraries", "books")
    yield table(
        ["Library", "Key ideas"],
        ["scikit-learn `HistGradientBoosting*`", "Bins features into ≤ 255 buckets for fast split finding (inspired by LightGBM); native missing-value and categorical support; built-in early stopping"],
        ["XGBoost", "Second-order (gradient + Hessian) updates; explicit regularisation of the tree (`lambda`, `alpha` on leaf weights, `gamma` per extra leaf); sparsity-aware splits; histogram method; GPU support"],
        ["LightGBM", "Histogram-based; **leaf-wise** growth (control with `num_leaves`); gradient-based one-side sampling (GOSS) and exclusive feature bundling (EFB) for speed"],
        ["CatBoost", "Ordered target statistics for categorical features and ordered boosting to avoid target leakage; symmetric (oblivious) trees; strong defaults"],
    )
    yield table(
        ["Hyperparameter", "Typical range", "Effect"],
        ["Learning rate (`eta`)", "0.01 – 0.3", "Smaller = more trees needed, usually better"],
        ["Number of trees", "100s – 1000s (use early stopping)", "Too many overfits"],
        ["Tree depth / `num_leaves`", "depth 3–8 / 15–255 leaves", "Interaction order and capacity"],
        ["Row / column subsampling", "0.5 – 1.0", "Adds randomness, reduces variance (stochastic gradient boosting)"],
        ["`min_child_weight` / `min_samples_leaf`", "Problem-dependent", "Prevents tiny, noisy leaves"],
        ["L1/L2 on leaf weights", "0 – 10", "Regularisation"],
    )
    yield qa("What is the difference between bagging and boosting?",
             "Bagging trains models independently on bootstrap samples and averages them — it reduces variance and doesn't overfit as models are added. Boosting trains models sequentially, each correcting the current ensemble's errors — it reduces bias, is usually more accurate on tabular data, but can overfit and needs a learning rate and early stopping.")
    yield qa("Why is it called gradient boosting?",
             "Each new tree is fitted to the negative gradient of the loss with respect to the current predictions — gradient descent in function space. For squared error those are the ordinary residuals, but any differentiable loss (log-loss, Huber, quantile) works the same way.")
    yield qa("Why do gradient-boosted trees often beat neural networks on tabular data?",
             "Tabular features are heterogeneous, often uninformative, and relationships have sharp thresholds; trees handle mixed scales, missing values and irregular functions naturally and need less data and tuning. Neural networks shine when there is spatial/sequential structure (images, text) or very large datasets.")


@topic(G, "modeling_approaches", "Choosing & Combining Models", "cpu")
def _():
    yield lead("There is no single best algorithm (the “no free lunch” theorem) — but there are good defaults. Start simple, compare candidates with the same cross-validation, and combine models when it pays.")
    yield table(
        ["Algorithm", "Boundary / shape", "Scaling needed", "Interpretability", "Good for", "Weak spots"],
        ["Linear / logistic regression", "Linear", "Yes (when regularised)", "High (coefficients)", "Baselines, high-dimensional sparse data, probabilities", "Non-linear effects unless engineered"],
        ["k-NN", "Any (local)", "Yes", "Medium (show neighbours)", "Small, low-dimensional data", "Slow predictions, high dimensions"],
        ["Naive Bayes", "Linear-ish", "No", "Medium", "Text, tiny data, speed", "Correlated features, poor probabilities"],
        ["SVM (RBF)", "Any (smooth)", "Yes", "Low", "Small/medium data, many features", "Large n, needs tuning, no native probabilities"],
        ["Decision tree", "Axis-aligned steps", "No", "High (rules)", "Explanations, rules", "High variance"],
        ["Random forest", "Axis-aligned, averaged", "No", "Medium", "Strong default for tabular data", "Size, extrapolation"],
        ["Gradient boosting", "Axis-aligned, additive", "No", "Medium", "Best accuracy on most tabular problems", "Tuning, overfits without early stopping"],
        ["Neural networks", "Any", "Yes", "Low", "Images, audio, text, very large data", "Data-hungry, tuning, compute"],
    )
    yield section("A practical order of attack", "route")
    yield steps(
        ("Baseline", "`DummyClassifier` / `DummyRegressor` and any existing business rule."),
        ("Simple model", "Regularised linear or logistic regression in a pipeline — fast, often surprisingly strong, and a sanity check for leakage."),
        ("Tree ensemble", "Random forest, then gradient boosting (HistGradientBoosting / LightGBM / XGBoost) with early stopping."),
        ("Unstructured data", "Pretrained deep models (fine-tuning or embeddings) — see **Deep Learning** and **Generative AI**."),
        ("Pick with constraints", "Accuracy is one criterion; latency, memory, interpretability, calibration and maintenance matter too."),
    )
    yield section("Compare candidates fairly", "scale")
    yield code_out('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        X, y = load_breast_cancer(return_X_y=True)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)      # same folds for every model
        candidates = {
            "logistic": make_pipeline(StandardScaler(), LogisticRegression()),
            "knn": make_pipeline(StandardScaler(), KNeighborsClassifier()),
            "svc": make_pipeline(StandardScaler(), SVC()),
            "random forest": RandomForestClassifier(random_state=0),
            "hist gboost": HistGradientBoostingClassifier(random_state=0),
        }
        for name, model in candidates.items():
            s = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
            print(f"{name:14} {s.mean():.3f} ± {s.std():.3f}")
    ''', out='''
logistic       0.995 ± 0.006
knn            0.981 ± 0.009
svc            0.996 ± 0.005
random forest  0.992 ± 0.007
hist gboost    0.994 ± 0.005
''')
    yield p("On this small, clean dataset the linear model is as good as anything — a reminder to always try the simple option. Differences inside one standard deviation are usually noise (see **Hypothesis Tests & Significance** for proper comparisons).")
    yield section("Voting and stacking", "stack-2")
    yield table(
        ["Method", "How", "Notes"],
        ["Hard voting", "Majority of predicted labels", "Simple; ignores confidence"],
        ["Soft voting", "Average predicted probabilities", "Usually better; needs reasonably calibrated models"],
        ["Stacking", "A meta-model learns how to combine base models' **out-of-fold** predictions", "Most flexible; base models should be diverse"],
    )
    yield code_out('''
        from sklearn.datasets import make_classification
        from sklearn.ensemble import RandomForestClassifier, StackingClassifier, VotingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        from sklearn.naive_bayes import GaussianNB
        from sklearn.neighbors import KNeighborsClassifier

        X, y = make_classification(n_samples=600, n_features=20, n_informative=6, random_state=1)
        base = [("lr", LogisticRegression()), ("rf", RandomForestClassifier(random_state=0)),
                ("knn", KNeighborsClassifier()), ("nb", GaussianNB())]

        for name, est in base:
            print(name, round(cross_val_score(est, X, y, cv=5).mean(), 3))
        vote = VotingClassifier(base, voting="soft")
        stack = StackingClassifier(base, final_estimator=LogisticRegression(), cv=5)
        print("soft vote", round(cross_val_score(vote, X, y, cv=5).mean(), 3))
        print("stacking", round(cross_val_score(stack, X, y, cv=5).mean(), 3))
    ''', out='''
lr 0.95
rf 0.937
knn 0.937
nb 0.915
soft vote 0.95
stacking 0.957
''')
    yield warn("Stacking must train the meta-model on **out-of-fold** predictions (`StackingClassifier` does this with its internal `cv`). Training it on predictions the base models made for their own training rows leaks — the meta-model learns to trust overfit models.")
    yield section("From ML to neural networks", "brain")
    yield p("Logistic regression *is* a one-neuron network: weighted sum → sigmoid → log-loss. A multi-layer perceptron stacks layers of such units with non-linear activations, so it can learn non-linear boundaries and its own features:")
    yield code('''
        from sklearn.datasets import make_moons
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        from sklearn.neural_network import MLPClassifier

        X, y = make_moons(n_samples=400, noise=0.2, random_state=0)
        print(round(cross_val_score(LogisticRegression(), X, y, cv=5).mean(), 3))    # 0.875 ← one linear boundary
        mlp = MLPClassifier(hidden_layer_sizes=(16, 16), max_iter=3000, random_state=0)
        print(round(cross_val_score(mlp, X, y, cv=5).mean(), 3))                     # 0.948 ← hidden layers bend the boundary
    ''')
    yield p("For anything beyond small experiments, neural networks are built in PyTorch or similar — backpropagation, optimisers, CNNs, RNNs and transformers are covered in **Deep Learning**.")
    yield qa("How would you choose a model for a tabular classification problem?",
             "Establish a dummy baseline, then a regularised logistic regression pipeline, then a tree ensemble (random forest, then gradient boosting with early stopping). Compare them with the same stratified CV folds on the metric that matters, check calibration and latency, and prefer the simpler model when the difference is within noise.")
    yield qa("What is stacking and how do you avoid leakage in it?",
             "A meta-model learns to combine the predictions of several base models. Its training inputs must be out-of-fold predictions (each row predicted by base models that didn't train on it); otherwise it learns from over-optimistic in-sample predictions.")
    yield qa("What does the no-free-lunch theorem say?",
             "Averaged over all possible problems, no learning algorithm beats any other. Every algorithm's success comes from assumptions that match the problem at hand — which is why we compare candidates empirically on our own data.")
