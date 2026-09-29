from kit import *
from mlkit import code_out

G = "Production & Responsible AI"


@topic(G, "ml_pipeline", "End-to-End Pipeline: Pipeline & ColumnTransformer", "git-fork")
def _():
    yield lead("A real project chains many steps — imputing, encoding, scaling, modelling. scikit-learn's `Pipeline` and `ColumnTransformer` bundle them into **one estimator**, so cross-validation can't leak, tuning covers preprocessing, and the exact same transformations run in production.")
    yield section("The lifecycle", "route")
    yield flow("Frame problem & metric", "Collect & label data", "Split (time / group / stratified)", "EDA on training data", "Pipeline: preprocess + model", "Cross-validate & tune", "Error analysis", "Test once", "Deploy (shadow → canary)", "Monitor & retrain")
    yield p("It is a loop, not a line: monitoring feeds new data and new failure cases back into labelling and training.")
    yield section("Building blocks", "puzzle")
    yield table(
        ["Tool", "Role"],
        ["`Pipeline([(name, step), …])`", "Chains transformers and a final estimator; `fit` fits each step on the output of the previous one"],
        ["`ColumnTransformer`", "Applies different preprocessing to different columns (numeric vs categorical) and concatenates the results"],
        ["`make_column_selector(dtype_include=…)`", "Selects columns by dtype instead of hard-coded names"],
        ["`FunctionTransformer`", "Wraps a custom function (log, ratios) as a pipeline step"],
        ["`step__param` names", "Address any step's hyperparameter in `GridSearchCV`, e.g. `model__C`, `prep__num__impute__strategy`"],
    )
    yield section("A complete example", "code")
    yield code_out('''
        import joblib
        import numpy as np
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import GridSearchCV, train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        # ── a churn-like dataset with numeric, categorical and missing values ──
        rng = np.random.default_rng(0)
        n = 1500
        df = pd.DataFrame({
            "tenure_months": rng.integers(1, 72, n),
            "monthly_charges": rng.normal(70, 20, n).round(2),
            "contract": rng.choice(["monthly", "one_year", "two_year"], n, p=[0.55, 0.25, 0.2]),
            "payment": rng.choice(["card", "bank", "cash"], n),
        })
        df.loc[rng.random(n) < 0.05, "monthly_charges"] = np.nan          # 5% missing
        logit = -1 - 0.04 * df["tenure_months"] + 0.02 * df["monthly_charges"].fillna(70) \\
                + df["contract"].map({"monthly": 1.5, "one_year": 0.0, "two_year": -1.5})
        df["churn"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)

        X, y = df.drop(columns="churn"), df["churn"]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)   # 1. split first

        numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
        categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                ("onehot", OneHotEncoder(handle_unknown="ignore"))])
        prep = ColumnTransformer([("num", numeric, ["tenure_months", "monthly_charges"]),
                                  ("cat", categorical, ["contract", "payment"])])
        pipe = Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=1000))])   # 2. one estimator

        search = GridSearchCV(pipe, {"model__C": [0.01, 0.1, 1, 10]}, cv=5, scoring="roc_auc")
        search.fit(X_tr, y_tr)                                          # 3. every fold refits the preprocessing
        print("best C:", search.best_params_["model__C"], "| CV ROC-AUC:", round(search.best_score_, 3))
        print("test ROC-AUC:", round(search.score(X_te, y_te), 3))     # 4. test once

        best = search.best_estimator_
        print(best.named_steps["prep"].get_feature_names_out().tolist())

        joblib.dump(best, "churn_model.joblib")                         # 5. ship ONE artefact
        loaded = joblib.load("churn_model.joblib")
        new_customer = pd.DataFrame([{"tenure_months": 3, "monthly_charges": np.nan,
                                      "contract": "monthly", "payment": "crypto"}])   # missing value + unseen category
        print("churn probability:", round(loaded.predict_proba(new_customer)[0, 1], 3))
    ''', out='''
best C: 1 | CV ROC-AUC: 0.805
test ROC-AUC: 0.819
['num__tenure_months', 'num__monthly_charges', 'cat__contract_monthly', 'cat__contract_one_year', 'cat__contract_two_year', 'cat__payment_bank', 'cat__payment_card', 'cat__payment_cash']
churn probability: 0.846
''')
    yield p("The raw new row — with a missing charge and a payment type never seen in training — goes straight into the loaded pipeline: imputation, scaling and encoding happen exactly as in training.")
    yield section("Why pipelines matter", "shield-check")
    yield ul(
        "**No leakage**: in cross-validation every transformer is fitted on the training folds only.",
        "**Tune everything**: imputation strategy, encoder settings and even whether to scale become hyperparameters.",
        "**One artefact**: preprocessing and model are saved and versioned together — no re-implementing feature logic in the serving code, the #1 source of training–serving skew.",
        "Use `pipe.set_output(transform=\"pandas\")` to keep column names through the steps while debugging.",
    )
    yield warn("`joblib`/`pickle` files can execute code when loaded — only load models from trusted sources, and pin library versions: a model pickled with one scikit-learn version is not guaranteed to load in another. For cross-language serving consider ONNX (`skl2onnx`).")
    yield qa("Why use a scikit-learn Pipeline?",
             "It fits preprocessing only on training data in every CV fold (preventing leakage), lets GridSearchCV tune preprocessing and model together, and produces a single object that applies identical transformations at prediction time — avoiding training–serving skew.")
    yield qa("How would you handle numeric and categorical columns differently in one model?",
             "With a ColumnTransformer: a numeric sub-pipeline (impute median, scale) and a categorical one (impute most frequent, one-hot with `handle_unknown=\"ignore\"`), combined and followed by the model inside a Pipeline.")
    yield qa("Walk me through an end-to-end ML project.",
             "Define the decision, target and metric with stakeholders; collect and label data; split (by time/group if needed); explore the training data; build a baseline; build a pipeline with preprocessing and candidate models; cross-validate and tune; analyse errors and slices; evaluate once on the test set; package and deploy (shadow, canary, A/B); monitor data, predictions and outcomes; retrain when needed.")


@topic(G, "deployment-monitoring", "Deployment, Monitoring & MLOps", "server")
def _():
    yield lead("A model creates value only in production — and production data changes. Deploy safely, monitor inputs, outputs and outcomes, and automate retraining. MLOps is the engineering discipline that makes this repeatable.")
    yield section("Serving patterns", "server-2")
    yield table(
        ["Pattern", "How", "Example"],
        ["Batch", "Score everything on a schedule, store results", "Nightly churn scores for the CRM"],
        ["Online (real-time)", "A service answers each request (REST/gRPC) in milliseconds", "Fraud check at payment time"],
        ["Streaming", "Score events from a queue (Kafka) as they arrive", "Anomaly alerts on sensor streams"],
        ["Edge / on-device", "Model runs on the phone or device", "Keyboard suggestions, offline vision"],
    )
    yield section("Rolling out safely", "rocket")
    yield table(
        ["Strategy", "How", "Catches"],
        ["Shadow", "New model scores live traffic, but its outputs are only logged", "Crashes, latency, training–serving skew — no user risk"],
        ["Canary", "Route a small % of traffic to the new model, grow it gradually", "Problems at small blast radius"],
        ["A/B test", "Randomised split, compare business metrics", "Whether it actually helps (see **A/B Testing**)"],
        ["Blue–green + rollback", "Keep the previous version ready to switch back instantly", "Anything missed above"],
    )
    yield section("Why models decay: drift", "trending-down")
    yield table(
        ["Type", "What changes", "Example"],
        ["Covariate (data) shift", "`P(X)` changes, `P(y | X)` stays", "A marketing campaign brings younger users"],
        ["Label (prior) shift", "`P(y)` changes", "Fraud rate doubles during a holiday season"],
        ["Concept drift", "`P(y | X)` changes — the same inputs now mean something else", "Spending patterns after a price shock; fraudsters change tactics"],
        ["Upstream data changes", "A pipeline bug, unit change or new category", "A field starts arriving in cents instead of dollars"],
    )
    yield section("Measuring input drift", "chart-histogram")
    yield formula("PSI = Σ_bins (actual% − expected%) · ln(actual% / expected%)        < 0.1 stable · 0.1–0.25 moderate · > 0.25 major shift")
    yield code('''
        import numpy as np
        from scipy.stats import ks_2samp

        rng = np.random.default_rng(0)
        train = rng.normal(50, 10, 10000)                 # feature at training time
        same = rng.normal(50, 10, 5000)                   # production, unchanged
        shifted = rng.normal(56, 12, 5000)                # production, drifted

        def psi(expected, actual, bins=10):
            edges = np.quantile(expected, np.linspace(0, 1, bins + 1))
            edges[0], edges[-1] = -np.inf, np.inf
            e = np.histogram(expected, edges)[0] / len(expected)
            a = np.histogram(actual, edges)[0] / len(actual)
            e, a = np.clip(e, 1e-6, None), np.clip(a, 1e-6, None)
            return float(np.sum((a - e) * np.log(a / e)))

        print(round(psi(train, same), 3), round(psi(train, shifted), 3))                          # 0.002 0.293
        print(round(ks_2samp(train, same).statistic, 3), round(ks_2samp(train, shifted).statistic, 3))   # 0.008 0.22 ← KS distance
    ''')
    yield note("With large samples, KS p-values flag even trivial differences as significant — alert on effect sizes (PSI, KS statistic, Wasserstein distance) and on the features that matter most to the model.")
    yield section("What to monitor", "activity")
    yield table(
        ["Layer", "Signals"],
        ["Service health", "Latency, throughput, error rate, memory"],
        ["Data quality", "Schema, missing-value rates, out-of-range values, unseen categories"],
        ["Input drift", "PSI / KS per important feature"],
        ["Prediction drift", "Distribution of scores and predicted classes; share of positives"],
        ["Model performance", "Accuracy/precision/recall or error once labels arrive — often delayed by days or weeks"],
        ["Business KPIs", "Conversion, fraud losses, complaints"],
    )
    yield section("Retraining", "refresh")
    yield ul(
        "**Scheduled** — retrain weekly/monthly on a sliding window; simple and predictable.",
        "**Triggered** — retrain when drift or performance alerts fire.",
        "**Continuous / online** — incremental updates (`partial_fit`) for fast-moving data.",
        "Always validate the new model against the current one on recent data before promoting it; retraining on bad (buggy, poisoned) data makes things worse.",
    )
    yield section("MLOps practices", "settings-automation")
    yield table(
        ["Practice", "Why", "Tools (examples)"],
        ["Version code, data and models", "Reproduce any model and debug regressions", "Git, DVC, lakeFS"],
        ["Experiment tracking", "Compare runs, parameters, metrics, artefacts", "MLflow, Weights & Biases"],
        ["Model registry", "Staging → production promotion, lineage, rollback", "MLflow Model Registry, SageMaker, Vertex AI"],
        ["Feature store", "Same feature definitions offline (training) and online (serving)", "Feast, Tecton"],
        ["CI/CD/CT", "Automated tests, builds, deployments — and continuous training", "GitHub Actions, Kubeflow, Airflow"],
        ["Data validation", "Catch schema and distribution problems before training/serving", "Great Expectations, TFDV, pandera"],
        ["Documentation", "Intended use, data, metrics by slice, limitations", "Model cards, datasheets for datasets"],
    )
    yield define("Training–serving skew", "a difference between how features are computed at training time and at serving time (different code, different data freshness, a timezone bug). The model sees inputs it was never trained on. Prevent with shared feature code or a feature store, and by logging production features to compare with training data.")
    yield qa("How do you detect and handle model drift in production?",
             "Monitor input feature distributions (PSI/KS), prediction distributions and — as labels arrive — actual performance, plus data-quality checks. When alerts fire, first rule out pipeline bugs and training–serving skew, then diagnose the type of drift, retrain on recent data (or adjust thresholds for pure label shift), validate against the current model, and roll out gradually.")
    yield qa("What is the difference between covariate shift and concept drift?",
             "Covariate shift: the input distribution P(X) changes but the relationship P(y|X) is the same — the model may still be right where it has data, but sees unfamiliar regions. Concept drift: P(y|X) itself changes, so the learned mapping is wrong and the model must be retrained with new labels.")
    yield qa("Shadow vs canary deployment?",
             "Shadow: the new model receives a copy of live traffic but its predictions aren't used — zero user impact, good for checking latency and skew. Canary: the new model actually serves a small fraction of users, which tests real impact with limited risk before a full rollout.")


@topic(G, "ai_ethics", "Fairness, Privacy & Responsible AI", "shield-half")
def _():
    yield lead("Models learn from historical data, including its biases, and they act at scale. Responsible ML means measuring who the model fails, protecting the people in the data, and documenting what the model should and shouldn't be used for.")
    yield section("Where bias comes from", "alert-triangle")
    yield table(
        ["Source", "Example"],
        ["Historical bias", "Past hiring decisions favoured one group; a model trained on them repeats it"],
        ["Representation bias", "Few examples from some groups (skin tones, accents, regions)"],
        ["Measurement bias", "A proxy target: “arrests” as a stand-in for “crime”"],
        ["Aggregation bias", "One model for groups whose features relate to the outcome differently"],
        ["Evaluation bias", "Benchmark that doesn't represent the deployed population"],
        ["Feedback loops", "Predictions change the data that future models are trained on"],
    )
    yield section("Group fairness metrics", "scale")
    yield table(
        ["Criterion", "Requires equal across groups", "Formula (A = group)"],
        ["Demographic (statistical) parity", "Selection rate", "`P(ŷ = 1 | A = a)`"],
        ["Equal opportunity", "True positive rate", "`P(ŷ = 1 | y = 1, A = a)`"],
        ["Equalized odds", "TPR **and** FPR", "`P(ŷ = 1 | y, A = a)` for y = 0 and 1"],
        ["Predictive parity", "Precision", "`P(y = 1 | ŷ = 1, A = a)`"],
        ["Calibration within groups", "Meaning of a score", "`P(y = 1 | score = s, A = a) = s`"],
    )
    yield p("The **disparate impact ratio** (lowest selection rate ÷ highest) is often checked against the US “four-fifths rule” (≥ 0.8) as a screening heuristic.")
    yield code_out('''
        import numpy as np
        import pandas as pd

        rng = np.random.default_rng(0)
        n = 4000
        group = rng.choice(["A", "B"], n)
        y = (rng.random(n) < np.where(group == "A", 0.30, 0.15)).astype(int)     # different base rates
        score = np.clip(0.35 * y + rng.normal(0.3, 0.15, n) + np.where(group == "B", -0.05, 0), 0, 1)
        pred = (score >= 0.5).astype(int)

        df = pd.DataFrame({"group": group, "y": y, "pred": pred})
        rows = {}
        for g, d in df.groupby("group"):
            rows[g] = {
                "base_rate": d.y.mean(),
                "selection_rate": d.pred.mean(),
                "TPR": d.pred[d.y == 1].mean(),
                "FPR": d.pred[d.y == 0].mean(),
                "precision": d.y[d.pred == 1].mean(),
            }
        report = pd.DataFrame(rows).T.round(3)
        print(report)
        print("disparate impact:", round(report.selection_rate.min() / report.selection_rate.max(), 3))
    ''', out='''
   base_rate  selection_rate    TPR    FPR  precision
A      0.291           0.305  0.850  0.082      0.811
B      0.159           0.165  0.742  0.056      0.713
disparate impact: 0.541
''')
    yield p("Group B is selected far less often — partly because its base rate is lower (not necessarily unfair) and partly because its scores are shifted down, which lowers its TPR (equal opportunity is violated). Which criterion matters is a policy decision about the application, not a purely technical one.")
    yield warn("**Impossibility result** (Kleinberg et al.; Chouldechova, 2016–17): when base rates differ between groups, a classifier cannot be calibrated within groups *and* have equal TPR and FPR across them — except in the degenerate case of perfect prediction. You must choose which notion of fairness fits the decision.")
    yield warn("**Fairness through unawareness** — just dropping the protected attribute — doesn't work: zip code, name, school or shopping history act as proxies. You often need the attribute to *measure* fairness at all.")
    yield section("Mitigation", "tool")
    yield table(
        ["Stage", "Techniques"],
        ["Pre-processing", "Collect more representative data, re-weight or re-sample groups, fix biased labels"],
        ["In-processing", "Fairness constraints or penalties during training (e.g. `fairlearn` reductions)"],
        ["Post-processing", "Group-specific thresholds to equalise TPR/FPR (check legality: some domains forbid group-dependent treatment)"],
        ["Process", "Slice-based evaluation before launch, human review for high-stakes decisions, appeal mechanisms, monitoring after launch"],
    )
    yield section("Privacy", "lock")
    yield ul(
        "**Data minimisation** — collect and keep only what the model needs; remove direct identifiers.",
        "**Anonymisation is hard** — combinations of quasi-identifiers (zip code, birth date, gender) re-identify most people; models can also leak training data (membership-inference attacks).",
        "**Differential privacy (DP)** — a formal guarantee: a mechanism M is ε-differentially private if for any two datasets differing in one person, `P[M(D) ∈ S] ≤ e^ε · P[M(D′) ∈ S]`. Adding calibrated noise is how it's achieved (Laplace mechanism for counts; DP-SGD for training). Smaller ε = more privacy, less accuracy.",
        "**Federated learning** — train across devices without centralising raw data; model updates can still leak information, so it's combined with secure aggregation and DP.",
        "Regulations such as GDPR (purpose limitation, data subject rights, rules on automated decisions) and the EU AI Act (risk-based obligations) shape what is allowed.",
    )
    yield code_out('''
        import numpy as np

        rng = np.random.default_rng(0)
        true_count = 132                                   # e.g. patients with a condition
        for eps in (0.1, 1.0, 10.0):
            noisy = true_count + rng.laplace(scale=1 / eps, size=5)   # Laplace mechanism: sensitivity 1 / ε
            print(eps, noisy.round(1).tolist())
    ''', out='''
0.1 [135.2, 125.8, 107.0, 97.9, 141.8]
1.0 [133.7, 132.2, 132.6, 132.1, 134.0]
10.0 [132.1, 131.5, 132.1, 131.7, 132.1]
''')
    yield p("Smaller ε means more noise: stronger privacy for any individual, less accurate answers.")
    yield section("Documentation and oversight", "file-certificate")
    yield ul(
        "**Model cards** — intended use, out-of-scope uses, training data, metrics overall and by slice, limitations, ethical considerations.",
        "**Datasheets for datasets** — how data was collected, by whom, consent, known gaps.",
        "Human oversight and contestability for high-stakes decisions (credit, hiring, health, justice).",
        "Security: adversarial examples, data poisoning and model extraction — see **Deep Learning** and **Generative AI** for model-specific risks such as prompt injection and hallucination.",
    )
    yield qa("What is the difference between demographic parity and equalized odds?",
             "Demographic parity requires the same positive-prediction rate in each group regardless of the true labels. Equalized odds requires equal true-positive and false-positive rates — equal error rates conditioned on the true outcome. When base rates differ, satisfying one generally violates the other.")
    yield qa("Removing the sensitive attribute makes the model fair — true?",
             "No. Other features act as proxies, so the model can reconstruct the attribute and reproduce the bias. And without the attribute you can't even measure group disparities. Fairness needs measurement per group and deliberate mitigation.")
    yield qa("What is differential privacy?",
             "A mathematical guarantee that the output of an analysis or trained model changes very little whether or not any single person's data is included, bounded by ε. It is achieved by adding calibrated random noise (Laplace mechanism, DP-SGD) and trades privacy against accuracy.")


@topic(G, "explainability", "Explainability", "eye")
def _():
    yield lead("Explainability answers *why* a model predicts what it does — globally (which features drive the model) and locally (why this one prediction). It builds trust, finds bugs and leakage, and is required in regulated decisions.")
    yield table(
        ["Method", "Scope", "Idea", "Caveats"],
        ["Interpretable model (linear, small tree)", "Global + local", "The model *is* the explanation", "Coefficients need comparable scales; correlated features muddle them"],
        ["Impurity importance (MDI)", "Global", "Total impurity decrease from a feature's splits", "Training-data based; biased toward continuous/high-cardinality features"],
        ["Permutation importance", "Global", "Score drop when a feature's values are shuffled", "Correlated features share/hide importance; shuffling creates unrealistic rows"],
        ["Partial dependence (PDP) / ICE", "Global / per row", "Average prediction as one feature varies", "Averages can hide interactions; assumes feature independence"],
        ["SHAP", "Local (aggregates to global)", "Shapley-value attribution of each feature's contribution", "Costly for general models; depends on the background data; not causal"],
        ["LIME", "Local", "Fit a simple surrogate model on perturbed samples around one row", "Unstable across runs; depends on the perturbation scheme"],
        ["Counterfactuals", "Local", "Smallest input change that flips the decision", "May suggest changes that aren't actionable"],
    )
    yield section("Permutation vs impurity importance", "arrows-shuffle")
    yield p("Five generated features (0–2 informative, 3–4 pure noise), plus a random continuous column (5) and a random 3-level category (6). Labels are noisy, so the forest's deep trees happily split on noise:")
    yield code('''
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.inspection import permutation_importance
        from sklearn.model_selection import train_test_split

        X, y = make_classification(n_samples=1000, n_features=5, n_informative=3, n_redundant=0,
                                   flip_y=0.15, shuffle=False, random_state=0)   # informative = 0, 1, 2
        rng = np.random.default_rng(0)
        X = np.c_[X, rng.normal(size=len(X)), rng.integers(0, 3, len(X))]  # 5: random numbers, 6: random category
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)

        rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_tr, y_tr)
        perm = permutation_importance(rf, X_te, y_te, n_repeats=10, random_state=0)
        print(rf.feature_importances_.round(3).tolist())       # [0.21, 0.267, 0.206, 0.1, 0.1, 0.092, 0.025] ← MDI: noise columns 3–5 get ~0.1 each
        print(perm.importances_mean.round(3).tolist())         # [0.162, 0.228, 0.184, -0.002, -0.004, 0.003, 0.001] ← permutation on test data: noise ≈ 0
    ''')
    yield p("Impurity importance hands the continuous noise column almost half the credit of a real feature — and much more than the equally useless 3-level category, because a feature with many distinct values offers many candidate splits. Permutation importance on held-out data correctly gives all noise columns about zero.")
    yield section("Partial dependence", "chart-line")
    yield code('''
        import numpy as np
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.inspection import partial_dependence

        rng = np.random.default_rng(0)
        X = rng.uniform(-3, 3, size=(2000, 2))
        y = X[:, 0] ** 2 + 0.5 * X[:, 1] + rng.normal(0, 0.3, 2000)      # U-shape in x0, linear in x1
        model = HistGradientBoostingRegressor(random_state=0).fit(X, y)

        pd0 = partial_dependence(model, X, features=[0], grid_resolution=5)
        print(pd0["grid_values"][0].round(1).tolist())         # [-2.7, -1.4, -0.0, 1.3, 2.7]
        print(pd0["average"][0].round(1).tolist())             # [4.5, -1.1, -3.0, -1.3, 4.1] ← recovers the U-shape
    ''')
    yield section("SHAP in one idea", "chart-bar")
    yield p("SHAP treats features as players in a cooperative game whose payout is the prediction. A feature's **Shapley value** is its average marginal contribution over all orders in which features could be added. Key property (*efficiency*): the contributions add up exactly to `prediction − baseline` (the average prediction). Other properties: symmetric features get equal credit; a feature that never changes the output gets 0.")
    yield formula("f(x) = φ₀ + Σⱼ φⱼ        φ₀ = E[f(X)]        linear model, independent features: φⱼ = wⱼ · (xⱼ − E[xⱼ])")
    yield code('''
        import numpy as np
        from sklearn.linear_model import LinearRegression

        rng = np.random.default_rng(0)
        X = rng.normal(size=(500, 3))
        y = 3 * X[:, 0] - 2 * X[:, 1] + 0.5 * X[:, 2] + rng.normal(0, 0.1, 500)
        m = LinearRegression().fit(X, y)

        x = X[0]
        phi = m.coef_ * (x - X.mean(axis=0))                   # exact SHAP values for a linear model
        base = m.predict(X).mean()
        print(phi.round(3).tolist())                           # [0.755, 0.424, 0.324] ← each feature's push away from the average
        print(round(base + phi.sum(), 4), round(m.predict([x])[0], 4))   # 0.9597 0.9597 ← baseline + contributions = prediction
    ''')
    yield p("The `shap` package computes these for any model — exactly and quickly for tree ensembles (TreeSHAP), approximately for others (KernelSHAP) — and draws summary, dependence and waterfall plots.")
    yield warn("Explanations describe the **model**, not the world: a large SHAP value means the model relies on the feature, not that changing the feature would change the outcome. With correlated features, credit is split in ways that depend on the method.")
    yield qa("What is the difference between interpretability and explainability?",
             "Interpretability usually means the model is understandable by design (linear model, small tree). Explainability means post-hoc techniques (permutation importance, PDP, SHAP, LIME, counterfactuals) that explain a model that may be a black box.")
    yield qa("Why prefer permutation importance over a random forest's feature_importances_?",
             "Impurity-based importance is computed on training data and inflates features with many possible split points (continuous or high-cardinality), even pure noise. Permutation importance measures the actual drop in a held-out score when a feature is scrambled, so irrelevant features score about zero.")
    yield qa("How does SHAP work?",
             "It assigns each feature its Shapley value — the average change in the prediction when that feature is added, over all possible orders of adding features, relative to a background expectation. The values are additive (they sum to prediction minus the baseline), consistent and fair in the game-theoretic sense; TreeSHAP computes them exactly for tree models.")
