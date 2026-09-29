from kit import *
from mlkit import code_out

G = "Data & Features"


@topic(G, "data_collection", "Data Collection & Labeling", "tags")
def _():
    yield lead("A model can only be as good as its data. The training set must **represent the population the model will serve**, and the labels must be consistent enough to learn from.")
    yield section("Where data comes from", "database-import")
    yield table(
        ["Source", "Strengths", "Watch out for"],
        ["Product logs & databases", "Real, plentiful, matches production", "Logging bugs, missing fields, only sees what the current system shows users"],
        ["Public datasets", "Fast to start, benchmarks", "Different population; license terms"],
        ["APIs & web scraping", "Broad coverage", "Terms of service, copyright, personal data, rate limits"],
        ["Sensors / IoT", "High volume, time-stamped", "Drift, calibration errors, gaps"],
        ["Human annotation", "Labels exactly what you need", "Cost, inconsistency, annotator bias"],
        ["Synthetic data", "Rare cases, privacy", "May not reflect real-world messiness"],
    )
    yield section("Representativeness and sampling bias", "users-group")
    yield ul(
        "**Selection bias** — the sample isn't random: a loan model trained only on *approved* applicants never sees how rejected ones would have repaid.",
        "**Survivorship bias** — only the survivors are recorded (products still on sale, companies still trading).",
        "**Coverage gaps** — a speech model trained on one accent, a vision model trained on daytime photos.",
        "**Time mismatch** — data from last year when behaviour has since changed.",
    )
    yield note("Ask: *would the rows I train on look like the rows the model will score next month?* If not, fix the collection before tuning any model.")
    yield section("Labeling", "edit")
    yield steps(
        ("Write guidelines", "Exact definitions and edge cases (“is a sarcastic review negative?”) with examples."),
        ("Pilot and measure agreement", "Several annotators label the same items; compute inter-annotator agreement."),
        ("Label at scale with checks", "Gold questions with known answers, multiple labels per item, majority vote or a label model."),
        ("Audit", "Review disagreements and model–label conflicts; they often reveal unclear guidelines."),
    )
    yield p("Raw percent agreement is inflated by chance. **Cohen's kappa** corrects for the agreement two annotators would reach by guessing with their own label frequencies:")
    yield formula("κ = (pₒ − pₑ) / (1 − pₑ)        pₒ = observed agreement, pₑ = agreement expected by chance")
    yield code('''
        from sklearn.metrics import cohen_kappa_score

        a = ["spam", "ham", "spam", "spam", "ham", "ham", "spam", "ham", "ham", "ham"]
        b = ["spam", "ham", "ham", "spam", "ham", "ham", "spam", "ham", "spam", "ham"]

        p_o = sum(x == y for x, y in zip(a, b)) / len(a)
        p_e = 0.4 * 0.4 + 0.6 * 0.6            # both say spam 40% of the time, ham 60%
        print(p_o, round(p_e, 2))              # 0.8 0.52
        print(round((p_o - p_e) / (1 - p_e), 3), round(cohen_kappa_score(a, b), 3))   # 0.583 0.583 ← same number
    ''')
    yield p("Rough reading (Landis & Koch): < 0.4 poor to fair, 0.4–0.6 moderate, 0.6–0.8 substantial, > 0.8 near-perfect. Use Fleiss' kappa or Krippendorff's alpha for more than two annotators.")
    yield section("Getting labels cheaply", "coin")
    yield cards(
        ("Active learning", "Train on a few labels, then ask humans to label the examples the model is **least sure** about — they carry the most information per label.", "refresh"),
        ("Weak supervision", "Write several noisy **labeling functions** (keywords, regexes, heuristics, existing models); a label model estimates each function's accuracy and combines their votes into probabilistic labels (the Snorkel approach).", "wand"),
        ("Semi-supervised", "Use many unlabelled rows alongside a few labelled ones, e.g. self-training on confident predictions.", "chart-dots-3"),
        ("Transfer learning", "Start from a model pre-trained on related data so far fewer labels are needed (see **Deep Learning**).", "transfer"),
        cols=2,
    )
    yield code('''
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression

        X, y = make_classification(n_samples=500, random_state=0)
        labeled, pool = np.arange(20), np.arange(20, 500)        # we paid for 20 labels so far

        model = LogisticRegression().fit(X[labeled], y[labeled])
        p = model.predict_proba(X[pool])[:, 1]
        most_uncertain = np.argsort(np.abs(p - 0.5))[:5]           # probabilities closest to 0.5
        print(pool[most_uncertain])                               # [393 398 245 464 413] ← send these rows to annotators
        print(p[most_uncertain].round(2))                         # [0.5  0.5  0.51 0.51 0.49]
    ''')
    yield warn("Keep the raw data, the labeling guidelines and each dataset version together (DVC, lakeFS, or dated snapshots). A model whose training data can't be reproduced can't be debugged or audited.")
    yield qa("How do you handle noisy labels?",
             "Measure them first (agreement on a double-labelled sample). Then clarify guidelines, use several annotators with majority vote, review items where the model confidently disagrees with the label, and prefer models/losses that are robust to some noise. A clean, trustworthy **test** set matters most — you can't measure progress against wrong answers.")
    yield qa("What is active learning?",
             "An iterative loop: train on the current labels, score the unlabelled pool, send the most informative examples (usually the most uncertain) to annotators, add them and retrain. It reaches a target accuracy with fewer labels than random sampling.")


@topic(G, "eda", "Data Types & EDA", "chart-histogram")
def _():
    yield lead("Exploratory data analysis (EDA) is how you learn what's in the data before modelling: types, missing values, distributions, outliers, the target's balance and suspicious features.")
    yield section("Kinds of data", "table")
    yield p("**Structured** (tabular) data has rows and named columns — database tables, CSVs. **Unstructured** data — text, images, audio, video — has no predefined columns; classic ML needs features extracted from it, while deep learning learns them. Within a table, each column has a statistical type that decides how it is prepared:")
    yield table(
        ["Type", "Examples", "Typical preparation"],
        ["Numerical — continuous", "Price, temperature, duration", "Scaling; log-transform if skewed"],
        ["Numerical — discrete (counts)", "Number of purchases, children", "As numbers; sometimes capped or log-transformed"],
        ["Categorical — nominal (no order)", "City, product id, colour", "One-hot, target or hash encoding"],
        ["Categorical — ordinal (ordered)", "Size S < M < L, education level, star rating", "Ordered integer codes"],
        ["Binary", "Is_premium, has_children", "0 / 1"],
        ["Date / time", "Signup timestamp", "Extract parts (hour, weekday), elapsed time, cyclical encoding"],
        ["Free text", "Reviews, titles", "Bag-of-words / TF-IDF, embeddings"],
        ["Identifiers", "User id, row number", "Usually **not** features — they let a model memorise rows"],
    )
    yield section("A first look with pandas", "search")
    yield code('''
        import numpy as np
        import pandas as pd

        df = pd.DataFrame({
            "age":     [34, 45, np.nan, 23, 51, 38, 29, 62],
            "income":  [52_000, 61_000, 48_000, 31_000, 250_000, 58_000, 40_000, 75_000],
            "city":    ["Pune", "Delhi", "Pune", "Mumbai", "Delhi", "Pune", None, "Mumbai"],
            "plan":    ["basic", "pro", "basic", "basic", "premium", "pro", "basic", "pro"],
            "churned": [0, 0, 1, 1, 0, 0, 1, 0],
        })
        print(df.shape)                                        # (8, 5)
        print(df.isna().sum().to_dict())                       # {'age': 1, 'income': 0, 'city': 1, 'plan': 0, 'churned': 0}
        print(df["churned"].mean())                            # 0.375 ← share of positives: check the balance
        print(df["income"].agg(["mean", "median"]).tolist())   # [76875.0, 55000.0] ← mean pulled up by one 250k value
        print(round(df["income"].skew(), 2))                   # 2.63 ← strongly right-skewed
        print(df["city"].value_counts().to_dict())             # {'Pune': 3, 'Delhi': 2, 'Mumbai': 2}
        print(df[["age", "income", "churned"]].corr()["churned"].drop("churned").round(2).to_dict())   # {'age': -0.73, 'income': -0.43} ← only 8 rows: far too few to trust
    ''')
    yield section("EDA checklist", "list-check")
    yield table(
        ["Check", "How", "Why"],
        ["Shape, types, ids", "`df.info()`, `df.dtypes`", "Numbers stored as strings, ids that must not be features"],
        ["Missing values", "`df.isna().mean()`", "Choose imputation; missingness can be informative"],
        ["Duplicates", "`df.duplicated().sum()`", "Duplicates across train/test inflate scores"],
        ["Target distribution", "`value_counts(normalize=True)` / histogram", "Class imbalance, skewed regression targets"],
        ["Univariate distributions", "`describe()`, histograms, box plots", "Skew, impossible values (age = −1), outliers"],
        ["Relationships", "Scatter plots, `corr()`, grouped means by category", "Useful features, collinearity"],
        ["Too-good features", "A single feature almost perfectly predicting the target", "Usually **target leakage**"],
        ["Time", "Plot counts and target rate over time", "Drift, seasonality, logging changes"],
    )
    yield warn("Do the detailed EDA on the **training split**. Looking closely at the test set and designing features around it leaks information about it into your choices.")
    yield section("Correlation, carefully", "chart-scatter")
    yield code('''
        import numpy as np
        from scipy.stats import pearsonr, spearmanr

        x = np.arange(1, 11, dtype=float)
        y_curve = x ** 3                               # perfectly monotonic, but not linear
        print(round(pearsonr(x, y_curve)[0], 3))       # 0.928 ← Pearson: linear association
        print(round(spearmanr(x, y_curve)[0], 3))      # 1.0 ← Spearman: rank (monotonic) association

        u = np.linspace(-1, 1, 21)
        print(round(pearsonr(u, u ** 2)[0], 3))        # 0.0 ← y depends on u completely, yet correlation is 0
    ''')
    yield ul(
        "Pearson measures **linear** association only; zero correlation does not mean independence.",
        "Spearman uses ranks — robust to outliers and captures any monotonic trend.",
        "Correlation is not causation: ice-cream sales and drownings both rise in summer.",
        "For categorical–target relationships, compare target rates per category or use mutual information.",
    )
    yield qa("What do you look at first in a new dataset?",
             "Size and column types, the target's distribution, missing values and duplicates, obviously wrong values, then each feature's distribution and its relationship with the target. I also check how the data was collected and over what time span, and flag any feature that predicts the target suspiciously well.")
    yield qa("Why shouldn't an ID column be used as a feature?",
             "It carries no generalisable information but is unique per row, so flexible models memorise it and look great on training data. Worse, if ids were assigned in time order, it can leak time or target information.")


@topic(G, "missing-values-outliers", "Missing Values & Outliers", "eraser")
def _():
    yield lead("Real data has gaps and extreme values. Handle them deliberately: understand **why** a value is missing or extreme, then choose a strategy — and fit that strategy on the training data only.")
    yield section("Why values go missing", "question-mark")
    yield table(
        ["Mechanism", "Meaning", "Example", "Consequence"],
        ["MCAR — missing completely at random", "Missingness unrelated to anything", "A sensor randomly drops packets", "Dropping rows loses data but doesn't bias"],
        ["MAR — missing at random", "Depends on *observed* columns", "Older users skip the income question more often", "Impute using the other columns"],
        ["MNAR — missing not at random", "Depends on the missing value itself", "High earners hide their income", "Missingness is informative — add an indicator"],
    )
    yield section("Strategies", "tool")
    yield table(
        ["Strategy", "When", "Caveat"],
        ["Drop rows", "Few rows affected, MCAR", "Throws data away; can bias if not MCAR"],
        ["Drop column", "Mostly empty *and* uninformative", "Check first whether missingness predicts the target"],
        ["Mean / median / most-frequent / constant", "Quick baseline (`SimpleImputer`)", "Shrinks variance; median is robust to outliers"],
        ["Missing-indicator column", "Missingness may carry signal", "`add_indicator=True`"],
        ["KNN / iterative imputation", "Features are related to each other", "Slower; still fit on train only"],
        ["Native support", "`HistGradientBoosting*`, scikit-learn trees (≥ 1.3), XGBoost, LightGBM", "The model learns where missing values should go"],
    )
    yield code('''
        import numpy as np
        from sklearn.impute import KNNImputer, SimpleImputer

        X_train = np.array([[1.0, 10.0], [2.0, np.nan], [np.nan, 30.0], [4.0, 40.0]])
        X_test = np.array([[np.nan, np.nan]])

        imp = SimpleImputer(strategy="median", add_indicator=True).fit(X_train)
        print(imp.statistics_)                   # [ 2. 30.] ← medians learned from TRAIN only
        print(imp.transform(X_test))             # [[ 2. 30.  1.  1.]] ← filled values + one indicator per column with gaps

        knn = KNNImputer(n_neighbors=2).fit(X_train)
        print(knn.transform([[2.0, np.nan]]))    # [[ 2. 25.]] ← mean of column 2 over the 2 nearest rows (x = 1 and x = 4)
    ''')
    yield warn("Computing the imputation value on the full dataset before splitting leaks test information into training. Put imputers inside a `Pipeline` so each cross-validation fold fits its own.")
    yield section("Outliers: detect", "zoom-exclamation")
    yield formula("IQR rule: outlier if x < Q1 − 1.5·IQR or x > Q3 + 1.5·IQR        z-score rule: |x − mean| / std > 3")
    yield code('''
        import numpy as np

        x = np.array([12, 14, 13, 15, 14, 13, 16, 14, 95])
        q1, q3 = np.percentile(x, [25, 75])
        lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        print(q1, q3, lo, hi)                      # 13.0 15.0 10.0 18.0
        print(x[(x < lo) | (x > hi)])              # [95] ← IQR flags the 95

        z = (x - x.mean()) / x.std()
        print(round(z.max(), 2))                   # 2.83 ← below 3: the outlier inflates the std and hides itself
        print(np.clip(x, lo, hi))                  # [12. 14. 13. 15. 14. 13. 16. 14. 18.] ← capping (winsorising) instead of deleting
    ''')
    yield p("The z-score rule assumes roughly normal data and is distorted by the very outliers it looks for (**masking**); median/IQR-based rules are more robust. For many features at once use a model-based detector such as Isolation Forest (see **Anomaly Detection**).")
    yield section("Outliers: decide", "git-branch")
    yield table(
        ["Kind of outlier", "Action"],
        ["Data error (age 250, negative price)", "Fix or set to missing"],
        ["Real but rare (a genuine 250k salary)", "Keep; reduce its leverage with a log transform, capping, or a robust model/loss"],
        ["The thing you want to find (fraud)", "Definitely keep — it's the signal"],
    )
    yield ul(
        "Tree-based models split on thresholds, so extreme feature values barely affect them.",
        "Linear models, k-NN, k-means and anything using means or squared errors are sensitive to them.",
        "Robust choices: median instead of mean, `RobustScaler`, MAE or Huber loss instead of MSE.",
    )
    yield qa("Mean or median imputation?",
             "Median for skewed features or when outliers are present — the mean is pulled toward extreme values. Either way, add a missing indicator when missingness may carry information, and compare against a model that handles NaN natively.")
    yield qa("Should you remove outliers?",
             "Only if they are errors. Real extreme values are information — removing them makes the model overconfident on exactly the cases that matter. Prefer transformation, capping or robust methods, and never remove outliers from the test set to make scores look better.")


@topic(G, "feature-scaling", "Feature Scaling & Transforms", "ruler-measure")
def _():
    yield lead("Scaling puts features on comparable ranges. It matters for models that use **distances, dot products or gradient descent**, and not at all for tree-based models.")
    yield table(
        ["Scaler", "Formula", "Result", "Use when"],
        ["`StandardScaler`", "`z = (x − mean) / std`", "Mean 0, std 1 (unbounded)", "Default for linear models, SVM, PCA, k-NN, neural nets"],
        ["`MinMaxScaler`", "`(x − min) / (max − min)`", "Range [0, 1]", "Bounded inputs needed (pixel values); no big outliers"],
        ["`RobustScaler`", "`(x − median) / IQR`", "Median 0, IQR 1", "Outliers present"],
        ["`MaxAbsScaler`", "`x / max(|x|)`", "Range [−1, 1], keeps zeros", "Sparse data"],
        ["`Normalizer`", "Each **row** divided by its norm", "Every row has length 1", "Text vectors / cosine similarity — not a per-feature scaler"],
    )
    yield code('''
        import numpy as np
        from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

        x = np.array([[1.0], [2.0], [3.0], [4.0], [100.0]])      # one outlier
        print(StandardScaler().fit_transform(x).ravel().round(2))  # [-0.54 -0.51 -0.49 -0.46  2.  ]
        print(MinMaxScaler().fit_transform(x).ravel().round(2))    # [0.   0.01 0.02 0.03 1.  ] ← normal values squashed near 0
        print(RobustScaler().fit_transform(x).ravel().round(2))    # [-1.  -0.5  0.   0.5 48.5] ← normal values keep their spread
    ''')
    yield section("Why it matters: k-NN on the wine data", "chart-scatter")
    yield p("Two of the 13 wine features (magnesium, proline) have far larger numbers than the rest, so they dominate Euclidean distance until everything is standardised:")
    yield code('''
        from sklearn.datasets import load_wine
        from sklearn.model_selection import cross_val_score
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_wine(return_X_y=True)
        print(X.std(axis=0)[[4, 7, 12]].round(1).tolist())   # [14.2, 0.1, 314.0] ← magnesium, nonflavanoid phenols, proline

        raw = cross_val_score(KNeighborsClassifier(), X, y, cv=5).mean()
        scaled = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier()), X, y, cv=5).mean()
        print(round(raw, 3), round(scaled, 3))           # 0.691 0.949
    ''')
    yield table(
        ["Needs scaling", "Doesn't need scaling"],
        ["k-NN, k-means, SVM, PCA, linear/logistic regression **with regularisation**, anything trained by gradient descent (including neural nets)", "Decision trees, random forests, gradient-boosted trees, Naive Bayes (each feature handled separately)"],
    )
    yield section("Fit on train, transform everything", "lock")
    yield code('''
        import numpy as np
        from sklearn.preprocessing import StandardScaler

        X_train = np.array([[10.0], [20.0], [30.0]])
        X_test = np.array([[40.0]])

        scaler = StandardScaler().fit(X_train)            # learns mean 20 and std 8.165 from TRAIN
        print(scaler.mean_, scaler.scale_.round(3))       # [20.] [8.165]
        print(scaler.transform(X_test).round(3))          # [[2.449]] ← test uses the TRAIN statistics
    ''')
    yield dodont("Fit the scaler on the training data (inside a `Pipeline` for cross-validation) and use `transform` on validation/test/production data.",
                 "`fit_transform` on the whole dataset before splitting, or re-fitting on the test set — both leak or shift information.")
    yield section("Transforming skewed features", "chart-area-line")
    yield code('''
        import numpy as np
        from scipy.stats import skew
        from sklearn.preprocessing import PowerTransformer

        rng = np.random.default_rng(0)
        income = rng.lognormal(mean=10, sigma=1, size=1000)       # right-skewed, like real incomes
        print(round(skew(income), 2))                                             # 3.87
        print(round(skew(np.log1p(income)), 2))                                   # -0.07 ← log: roughly symmetric
        print(round(skew(PowerTransformer().fit_transform(income.reshape(-1, 1)).ravel()), 2))  # 0.0 ← Yeo-Johnson
    ''')
    yield warn("Standardising changes the **scale**, not the **shape**: a skewed feature stays skewed with mean 0 and std 1. Use a log / Box-Cox / Yeo-Johnson transform (or `QuantileTransformer`) to change the shape.")
    yield qa("Normalization vs standardization?",
             "Min-max normalization maps a feature to [0, 1] using its min and max — sensitive to outliers. Standardization subtracts the mean and divides by the standard deviation — unbounded, usually a safer default. Both are fitted on the training data. (Confusingly, sklearn's `Normalizer` does something else: it scales each *row* to unit length.)")
    yield qa("Does a random forest need feature scaling?",
             "No. Trees split on thresholds of one feature at a time, and any monotonic rescaling leaves the ordering — and therefore the splits — unchanged.")


@topic(G, "encoding-categoricals", "Encoding Categorical Features", "binary")
def _():
    yield lead("Most algorithms need numbers. The encoding must not invent an order that doesn't exist, must cope with categories never seen in training, and must not leak the target.")
    yield table(
        ["Encoding", "How", "Good for", "Watch out"],
        ["One-hot", "One 0/1 column per category", "Nominal features with few categories; linear models", "Many columns for high cardinality"],
        ["Ordinal", "Integer code per category in a chosen order", "Truly ordered categories (S < M < L); tree models", "Imposes an order a linear model will take literally"],
        ["Target (mean) encoding", "Replace each category by the (smoothed) target mean for it", "High-cardinality features (zip code, merchant)", "Leaks the target unless cross-fitted"],
        ["Frequency / count", "Replace by how often the category occurs", "High cardinality, tree models", "Different categories can collide on the same count"],
        ["Hashing", "Hash category into a fixed number of columns", "Huge or open-ended vocabularies, streaming", "Collisions; not reversible"],
        ["Embeddings", "Learned dense vectors", "Very high cardinality in neural nets", "Needs a neural model (see **Deep Learning**)"],
    )
    yield section("One-hot and ordinal in scikit-learn", "code")
    yield code('''
        import numpy as np
        from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

        cities = np.array([["Pune"], ["Delhi"], ["Pune"], ["Mumbai"]])
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(cities)
        print(ohe.get_feature_names_out().tolist())                # ['x0_Delhi', 'x0_Mumbai', 'x0_Pune']
        print(ohe.transform([["Delhi"], ["Chennai"]]).tolist())    # [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]] ← unseen "Chennai" → all zeros

        sizes = np.array([["S"], ["L"], ["M"]])
        enc = OrdinalEncoder(categories=[["S", "M", "L"]]).fit(sizes)   # order given explicitly
        print(enc.transform(sizes).ravel().tolist())               # [0.0, 2.0, 1.0]
    ''')
    yield warn("Plain integer codes for a **nominal** feature (Delhi = 0, Mumbai = 1, Pune = 2) tell a linear model that Pune is “twice” Mumbai. Trees cope better with arbitrary codes, but one-hot or target encoding is usually safer. Never rely on alphabetical order for an ordinal feature — pass `categories` explicitly.")
    yield section("The dummy-variable trap", "alert-triangle")
    yield p("With an intercept, the full set of one-hot columns always sums to 1, so one column is a linear combination of the others (perfect multicollinearity). Unregularised linear regression then has no unique solution — use `OneHotEncoder(drop=\"first\")`. With regularisation (Ridge, the default `LogisticRegression`) or tree models, keeping all columns is fine.")
    yield section("Many categories", "stack-3")
    yield code('''
        import numpy as np
        from sklearn.preprocessing import OneHotEncoder

        colors = np.array([["red"]] * 6 + [["blue"]] * 3 + [["teal"], ["plum"]])
        ohe = OneHotEncoder(min_frequency=2, handle_unknown="infrequent_if_exist", sparse_output=False).fit(colors)
        print(ohe.get_feature_names_out().tolist())   # ['x0_blue', 'x0_red', 'x0_infrequent_sklearn'] ← rare categories grouped together
    ''')
    yield formula("target encoding(c) = (n_c · mean_c + m · global_mean) / (n_c + m)        n_c = rows in category c, m = smoothing")
    yield p("**Target encoding** replaces each category by the mean target for that category, shrunk toward the global mean when the category is rare. Computed naively on the training rows it leaks each row's own label into its feature. scikit-learn's `TargetEncoder` avoids this with **cross-fitting**: `fit_transform` encodes each training row using statistics from the other folds, while `transform` on new data uses the full-training statistics.")
    yield code('''
        import numpy as np
        from sklearn.preprocessing import TargetEncoder

        X = np.array([["a"]] * 4 + [["b"]] * 4 + [["c"]])
        y = np.array([1, 1, 1, 0,   0, 0, 0, 1,   1])
        enc = TargetEncoder(target_type="binary", smooth=2.0, random_state=0).fit(X, y)
        print(round(enc.target_mean_, 3))                  # 0.556 ← global positive rate
        print(enc.encodings_[0].round(3))                  # [0.685 0.352 0.704] ← raw means 0.75, 0.25, 1.0 pulled toward 0.556
    ''')
    yield qa("How do you encode a feature with 10,000 categories?",
             "Not with one-hot for a dense model. Options: target encoding with cross-fitting and smoothing, frequency encoding, hashing into a few thousand columns, grouping rare categories into “other”, or learned embeddings in a neural network. Tree libraries like LightGBM/CatBoost also handle categoricals natively.")
    yield qa("How do you handle a category at prediction time that never appeared in training?",
             "Decide up front: `OneHotEncoder(handle_unknown=\"ignore\")` encodes it as all zeros, infrequent-category grouping maps it to “other”, target encoders fall back to the global mean. Monitor how often unknown categories appear in production — a rising rate signals drift.")


@topic(G, "feature-engineering", "Feature Engineering & Selection", "tool")
def _():
    yield lead("Feature engineering creates inputs that make the pattern easier to learn; feature selection removes inputs that add noise, cost or leakage. On tabular data, good features usually beat a fancier algorithm.")
    yield section("Engineering ideas", "bulb")
    yield table(
        ["Idea", "Example"],
        ["Ratios & differences", "`price_per_item = total / items`, `debt_to_income`"],
        ["Aggregates over history", "Purchases in the last 7 / 30 days, average basket size per user"],
        ["Date & time parts", "Hour, weekday, month, is_weekend, days since signup"],
        ["Cyclical encoding", "`sin(2π·hour/24)`, `cos(2π·hour/24)` so 23:00 is next to 00:00"],
        ["Binning", "Age bands — can help linear models capture non-linear effects"],
        ["Interactions & polynomials", "`area × quality`, `x²` for linear models (`PolynomialFeatures`)"],
        ["Text", "Length, keyword flags, TF-IDF (see **Data Science**)"],
        ["Domain knowledge", "BMI from height and weight; distance from coordinates"],
    )
    yield code('''
        import numpy as np
        import pandas as pd

        df = pd.DataFrame({
            "ts": pd.to_datetime(["2024-01-05 09:15", "2024-01-06 23:40", "2024-01-08 00:20"]),
            "total": [120.0, 80.0, 300.0],
            "items": [4, 1, 6],
        })
        df["hour"] = df["ts"].dt.hour
        df["is_weekend"] = df["ts"].dt.dayofweek >= 5          # Monday = 0 … Sunday = 6
        df["price_per_item"] = df["total"] / df["items"]
        print(df[["hour", "is_weekend", "price_per_item"]].values.tolist())   # [[9, False, 30.0], [23, True, 80.0], [0, False, 50.0]]

        angle = 2 * np.pi * df["hour"] / 24
        pts = np.c_[np.sin(angle), np.cos(angle)]
        print(abs(23 - 0), round(np.linalg.norm(pts[1] - pts[2]), 2))   # 23 0.26 ← raw gap vs cyclical distance
    ''')
    yield section("Selecting features", "filter")
    yield table(
        ["Family", "How it works", "scikit-learn", "Trade-off"],
        ["Filter", "Score each feature against the target, independently of any model", "`VarianceThreshold`, `SelectKBest(f_classif / chi2 / mutual_info_classif)`", "Fast; misses interactions"],
        ["Wrapper", "Search subsets by repeatedly training a model", "`RFE`, `RFECV`, `SequentialFeatureSelector`", "Model-aware; expensive, can overfit the selection"],
        ["Embedded", "Selection happens during training", "L1 (Lasso) coefficients, tree importances via `SelectFromModel`", "Cheap; tied to one model's view"],
    )
    yield code('''
        import numpy as np
        from sklearn.feature_selection import RFE, SelectFromModel, SelectKBest, f_classif
        from sklearn.linear_model import LogisticRegression

        rng = np.random.default_rng(0)
        X = rng.normal(size=(400, 10))                                    # 10 features …
        y = (2 * X[:, 0] - 1.5 * X[:, 1] + X[:, 2] + rng.normal(0, 0.5, 400) > 0).astype(int)   # … only 0, 1, 2 matter

        print(SelectKBest(f_classif, k=3).fit(X, y).get_support(indices=True))                     # [0 1 2] ← filter
        print(RFE(LogisticRegression(), n_features_to_select=3).fit(X, y).get_support(indices=True))    # [0 1 2] ← wrapper
        l1 = LogisticRegression(l1_ratio=1, solver="liblinear", C=0.05)                            # L1 penalty
        print(SelectFromModel(l1).fit(X, y).get_support(indices=True))                            # [0 1 2] ← embedded
    ''')
    yield warn("Feature selection is part of training. Selecting features on the full dataset and *then* cross-validating produces badly optimistic scores — the **Data Leakage** topic demonstrates a model scoring far above chance on pure noise this way. Put the selector inside the `Pipeline`.")
    yield section("Why bother selecting?", "help")
    yield ul(
        "Fewer irrelevant features → less overfitting, especially with few rows (see **Curse of Dimensionality** in the k-NN topic).",
        "Faster training and prediction; fewer data pipelines to maintain in production.",
        "Easier explanations.",
        "Removing features that are available in training but not at prediction time prevents leakage.",
    )
    yield qa("Filter vs wrapper vs embedded feature selection?",
             "Filters score features with a statistic (correlation, ANOVA F, mutual information) without training the final model — fast but blind to interactions. Wrappers (RFE, forward/backward selection) train models on candidate subsets — accurate but expensive and prone to overfitting the selection. Embedded methods select during training — Lasso zeroes coefficients, trees rank features by importance.")
    yield qa("How would you encode the hour of day?",
             "As a categorical (one-hot, 24 columns) if each hour behaves differently, or cyclically with `sin(2π·h/24)` and `cos(2π·h/24)` so the model sees 23:00 and 00:00 as neighbours. Tree models can also use the raw hour directly, splitting it into ranges.")


@topic(G, "data-leakage", "Data Leakage", "droplet")
def _():
    yield lead("Leakage is when information that won't be available at prediction time sneaks into training or evaluation. It produces excellent offline scores and a model that fails in production — the most expensive bug in applied ML.")
    yield table(
        ["Type", "What happens", "Example", "Prevention"],
        ["Target leakage", "A feature is derived from the target or only known after the outcome", "`refund_issued` used to predict fraud; `discharge_date` to predict admission", "For every feature ask: *is it known at prediction time?*"],
        ["Preprocessing leakage", "Scalers, imputers, encoders, feature selection or resampling fitted on all rows before splitting", "`StandardScaler().fit(X)` then `train_test_split`; SMOTE before cross-validation", "Split first; fit every step inside a `Pipeline`"],
        ["Duplicate / group leakage", "The same entity appears in train and test", "Several X-rays of one patient; near-duplicate product listings", "Deduplicate; split by group (`GroupKFold`)"],
        ["Temporal leakage", "Training uses the future", "Random split of time-series data; rolling features that include the current day's outcome", "Split by time (`TimeSeriesSplit`); build features only from the past"],
        ["Test-set reuse", "Repeatedly tuning against the test set", "Trying 50 models and reporting the best test score", "Tune with validation/CV; use the test set once"],
    )
    yield section("Demo: 85% accuracy on pure noise", "flask")
    yield p("5,000 random features, random labels — there is nothing to learn, so the honest accuracy is about 50%. Selecting the 20 “best” features on **all** rows before cross-validation lets the selector peek at every fold's labels:")
    yield code('''
        import numpy as np
        from sklearn.feature_selection import SelectKBest, f_classif
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        from sklearn.pipeline import make_pipeline

        rng = np.random.default_rng(0)
        X = rng.normal(size=(100, 5000))       # pure-noise features
        y = rng.integers(0, 2, size=100)       # random labels

        X_sel = SelectKBest(f_classif, k=20).fit_transform(X, y)          # ✗ selection saw all labels
        leaky = cross_val_score(LogisticRegression(), X_sel, y, cv=5).mean()

        pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression())
        honest = cross_val_score(pipe, X, y, cv=5).mean()                 # ✓ selection refit per training fold
        print(round(leaky, 2), round(honest, 2))                          # 0.85 0.48
    ''')
    yield section("Warning signs", "alert-octagon")
    yield ul(
        "Scores that are too good for the problem (AUC 0.99 on a hard business problem).",
        "One feature dominates importance, especially one with a name like `status`, `outcome_*`, `*_after`.",
        "A big drop from offline validation to the first production week.",
        "Performance collapses when you switch from a random split to a time or group split.",
    )
    yield dodont("Split first (by time or group where it applies), wrap all preprocessing in a `Pipeline`, reconstruct features “as of” the prediction timestamp, and keep one untouched test set.",
                 "Cleaning, scaling, imputing, encoding, selecting or oversampling the full dataset before splitting.")
    yield qa("What is data leakage? Give examples.",
             "Information unavailable at prediction time influencing training or evaluation. Examples: a feature computed from the label (target leakage), a scaler or feature selector fitted on the full data before the split, the same customer in train and test, random splits of time-series data, and tuning on the test set. All inflate offline scores.")
    yield qa("Your model gets 99% validation accuracy on a hard problem. What do you do?",
             "Suspect leakage before celebrating: check the top features and whether each is known at prediction time, look for duplicates or shared entities across splits, confirm preprocessing is fitted inside the training folds, and re-evaluate with a time-based or group-based split.")
