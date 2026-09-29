from kit import *
from mlkit import code_out

G = "Evaluation & Model Selection"


@topic(G, "evaluation_metrics", "Classification Metrics", "award")
def _():
    yield lead("Every classification metric is built from the four cells of the confusion matrix. Pick the one that reflects what errors **cost** in your problem — accuracy alone is rarely enough.")
    yield section("The confusion matrix", "table")
    yield table(
        ["", "Predicted positive", "Predicted negative"],
        ["**Actual positive**", "True positive (TP)", "False negative (FN) — Type II error, a miss"],
        ["**Actual negative**", "False positive (FP) — Type I error, a false alarm", "True negative (TN)"],
    )
    yield code('''
        from sklearn.metrics import confusion_matrix

        y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        y_pred = [1, 1, 1, 0, 1, 1, 0, 0, 0, 0]
        cm = confusion_matrix(y_true, y_pred)
        print(cm.tolist())                     # [[4, 2], [1, 3]] ← rows = actual, columns = predicted, labels sorted: 0 then 1
        tn, fp, fn, tp = cm.ravel()
        print(tp, fp, fn, tn)                  # 3 2 1 4
    ''')
    yield warn("scikit-learn orders labels ascending, so for 0/1 labels the matrix is `[[TN, FP], [FN, TP]]` — negatives first, the opposite of most textbook diagrams. Unpack with `tn, fp, fn, tp = cm.ravel()`.")
    yield section("The metrics", "math-symbols")
    yield table(
        ["Metric", "Formula", "Question it answers"],
        ["Accuracy", "`(TP + TN) / all`", "What fraction of predictions are right?"],
        ["Precision", "`TP / (TP + FP)`", "When the model says positive, how often is it right?"],
        ["Recall (sensitivity, TPR)", "`TP / (TP + FN)`", "What fraction of actual positives does it find?"],
        ["Specificity (TNR)", "`TN / (TN + FP)`", "What fraction of actual negatives does it clear?"],
        ["False positive rate", "`FP / (FP + TN)` = 1 − specificity", "How many negatives get a false alarm?"],
        ["F1", "`2·P·R / (P + R)`", "Harmonic mean of precision and recall"],
        ["Fβ", "`(1 + β²)·P·R / (β²·P + R)`", "β > 1 weights recall more; β < 1 precision"],
        ["Balanced accuracy", "`(TPR + TNR) / 2`", "Accuracy that isn't fooled by imbalance"],
        ["MCC", "`(TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))`", "Correlation between prediction and truth, −1 … 1"],
        ["Log-loss", "`−mean[y·log p + (1 − y)·log(1 − p)]`", "How good are the predicted **probabilities**?"],
    )
    yield code('''
        from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score, fbeta_score,
                                     matthews_corrcoef, precision_score, recall_score)

        y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        y_pred = [1, 1, 1, 0, 1, 1, 0, 0, 0, 0]        # TP=3, FN=1, FP=2, TN=4
        print(accuracy_score(y_true, y_pred))                                         # 0.7 ← 7/10
        print(precision_score(y_true, y_pred), recall_score(y_true, y_pred))          # 0.6 0.75 ← 3/5, 3/4
        print(round(f1_score(y_true, y_pred), 3), round(fbeta_score(y_true, y_pred, beta=2), 3))   # 0.667 0.714
        print(round(balanced_accuracy_score(y_true, y_pred), 3), round(matthews_corrcoef(y_true, y_pred), 3))   # 0.708 0.408
    ''')
    yield note("Precision and recall pull against each other: raising the decision threshold usually increases precision and lowers recall. F1 is high only when **both** are high — the harmonic mean is dragged toward the smaller one.")
    yield section("The accuracy paradox", "alert-triangle")
    yield code('''
        import numpy as np
        from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score,
                                     matthews_corrcoef, recall_score)

        y_true = np.array([1] * 10 + [0] * 990)       # 1% positives
        y_pred = np.zeros(1000, dtype=int)            # a "model" that never predicts positive
        print(accuracy_score(y_true, y_pred))                                        # 0.99 ← looks great
        print(recall_score(y_true, y_pred), f1_score(y_true, y_pred, zero_division=0))  # 0.0 0.0 ← finds nothing
        print(balanced_accuracy_score(y_true, y_pred), matthews_corrcoef(y_true, y_pred))  # 0.5 0.0 ← chance level
    ''')
    yield section("Multi-class: averaging", "category")
    yield table(
        ["Average", "How", "Use when"],
        ["Macro", "Compute the metric per class, then the plain mean", "Every class matters equally (rare classes count as much as common ones)"],
        ["Weighted", "Per-class metric weighted by class support", "Summarise overall performance, respecting class sizes"],
        ["Micro", "Pool all TP/FP/FN, then compute", "Overall per-prediction performance; for single-label multi-class, micro-F1 = accuracy"],
    )
    yield code_out('''
        from sklearn.metrics import classification_report, f1_score

        y_true = ["cat"] * 6 + ["dog"] * 3 + ["bird"] * 1
        y_pred = ["cat"] * 5 + ["dog"] + ["dog", "dog", "cat"] + ["cat"]
        print(classification_report(y_true, y_pred, zero_division=0))
        print(round(f1_score(y_true, y_pred, average="micro"), 3),
              round(f1_score(y_true, y_pred, average="macro", zero_division=0), 3))
    ''', out='''
              precision    recall  f1-score   support

        bird       0.00      0.00      0.00         1
         cat       0.71      0.83      0.77         6
         dog       0.67      0.67      0.67         3

    accuracy                           0.70        10
   macro avg       0.46      0.50      0.48        10
weighted avg       0.63      0.70      0.66        10

0.7 0.479
''')
    yield p("The rare class “bird” is never predicted: macro-F1 exposes that, while accuracy and micro-F1 (both 0.7) hide it.")
    yield section("Which metric?", "compass")
    yield table(
        ["Situation", "Prefer"],
        ["Balanced classes, equal error costs", "Accuracy (plus the confusion matrix)"],
        ["False positives are expensive (spam filter, a costly intervention)", "Precision (at a minimum recall)"],
        ["False negatives are expensive (disease screening, fraud)", "Recall (at a minimum precision), F2"],
        ["Imbalanced, need one threshold-free number", "PR-AUC (average precision); also MCC at a chosen threshold"],
        ["Ranking quality, roughly balanced", "ROC-AUC"],
        ["Probabilities will be used as probabilities", "Log-loss, Brier score, calibration curve"],
        ["Real costs known", "Expected cost / profit at the chosen threshold"],
    )
    yield qa("Explain precision and recall with an example.",
             "A fraud model flags 100 transactions; 80 are really fraud → precision 0.8. There were 200 frauds in total; it caught 80 → recall 0.4. Precision is about the trustworthiness of alarms, recall about coverage of the positives.")
    yield qa("When is F1 a poor choice?",
             "When error costs are very asymmetric (use Fβ or expected cost), when true negatives matter (F1 ignores them), when you care about probabilities rather than a single threshold, and when the positive class is not the one of interest — F1 depends on which class is labelled positive.")
    yield qa("What is the difference between macro and micro averaging?",
             "Macro averages the per-class scores, so each class counts equally and poor performance on a rare class shows up. Micro pools all decisions before computing, so frequent classes dominate; for single-label multi-class problems micro-precision, micro-recall and micro-F1 all equal accuracy.")


@topic(G, "roc-pr-thresholds", "ROC, PR, Thresholds & Calibration", "chart-line")
def _():
    yield lead("Most classifiers output a **score**; a threshold turns it into a decision. Curves summarise performance over every threshold, threshold tuning picks the operating point, and calibration makes the scores trustworthy probabilities.")
    yield section("ROC curve and ROC-AUC", "chart-line")
    yield p("The ROC curve plots the **true positive rate (recall)** on the y-axis against the **false positive rate** on the x-axis as the threshold sweeps from high to low. The diagonal is a random classifier; the top-left corner is perfect.")
    yield define("ROC-AUC", "the area under the ROC curve = the probability that a randomly chosen positive gets a higher score than a randomly chosen negative. 1.0 = perfect ranking, 0.5 = random, below 0.5 = ranked backwards.")
    yield code('''
        import numpy as np
        from sklearn.metrics import roc_auc_score, roc_curve

        y = np.array([0, 0, 1, 0, 1, 1, 0, 1])
        score = np.array([0.1, 0.3, 0.35, 0.4, 0.6, 0.7, 0.8, 0.9])

        pos, neg = score[y == 1], score[y == 0]
        pairs = [(p > n) + 0.5 * (p == n) for p in pos for n in neg]
        print(np.mean(pairs), roc_auc_score(y, score))       # 0.75 0.75 ← AUC = P(positive ranked above negative)

        fpr, tpr, thr = roc_curve(y, score)
        print(fpr.tolist())                                   # [0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 1.0] ← x-axis
        print(tpr.tolist())                                   # [0.0, 0.25, 0.25, 0.75, 0.75, 1.0, 1.0] ← y-axis
    ''')
    yield section("Precision–recall curve", "chart-area-line")
    yield p("The PR curve plots **precision** (y) against **recall** (x). It ignores true negatives, so it reflects how many false alarms come with each level of recall. Its baseline is the **positive-class prevalence**: a random classifier has precision ≈ prevalence at every recall, and at recall = 1 (everything predicted positive) precision equals the prevalence — not 0. The area is summarised by **average precision** (AP ≈ PR-AUC).")
    yield code('''
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import average_precision_score, roc_auc_score
        from sklearn.model_selection import train_test_split

        X, y = make_classification(n_samples=20000, weights=[0.99], class_sep=1.2, flip_y=0, random_state=0)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)
        p = LogisticRegression().fit(X_tr, y_tr).predict_proba(X_te)[:, 1]

        print(round(y_te.mean(), 4))                        # 0.01 ← prevalence = PR baseline
        print(round(roc_auc_score(y_te, p), 3))             # 0.946 ← looks excellent
        print(round(average_precision_score(y_te, p), 3))   # 0.587 ← the harder truth about the positives
    ''')
    yield note("ROC-AUC isn't “wrong” on imbalanced data — TPR and FPR are each computed within one class, so it is insensitive to the class ratio. But a tiny FPR can still mean more false alarms than true hits when negatives outnumber positives 100:1. PR-AUC shows that directly.")
    yield table(
        ["", "ROC-AUC", "PR-AUC (average precision)"],
        ["Axes", "TPR vs FPR", "Precision vs recall"],
        ["Random baseline", "0.5", "Prevalence"],
        ["Uses true negatives", "Yes", "No"],
        ["Best for", "Ranking quality with reasonably balanced classes; comparing models across datasets", "Rare positives where false alarms matter (fraud, retrieval)"],
    )
    yield section("Choosing the threshold", "adjustments-horizontal")
    yield p("0.5 is only the right cut-off for calibrated probabilities with equal error costs. Choose the threshold on **validation data** (never the test set) from the business requirement — a minimum recall, a maximum alert volume, or the lowest expected cost:")
    yield code_out('''
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import precision_recall_curve, precision_score, recall_score
        from sklearn.model_selection import train_test_split

        X, y = make_classification(n_samples=4000, weights=[0.9], class_sep=0.8, random_state=1)
        X_tr, X_val, y_tr, y_val = train_test_split(X, y, stratify=y, random_state=0)
        p = LogisticRegression().fit(X_tr, y_tr).predict_proba(X_val)[:, 1]

        for t in (0.3, 0.5, 0.7):
            pred = p >= t
            print(t, round(precision_score(y_val, pred), 3), round(recall_score(y_val, pred), 3))

        prec, rec, thr = precision_recall_curve(y_val, p)
        ok = rec[:-1] >= 0.8                          # requirement: catch at least 80% of positives
        best = np.argmax(np.where(ok, prec[:-1], -1))  # … with the best precision
        print("threshold", round(thr[best], 3), "precision", round(prec[best], 3), "recall", round(rec[best], 3))

        cost_fn, cost_fp = 10, 1                      # a miss costs 10× a false alarm
        costs = [cost_fn * np.sum((p < t) & (y_val == 1)) + cost_fp * np.sum((p >= t) & (y_val == 0)) for t in thr]
        print("min-cost threshold", round(thr[int(np.argmin(costs))], 3))
    ''', out='''
0.3 0.938 0.892
0.5 0.977 0.824
0.7 0.987 0.735
threshold 0.449 precision 0.977 recall 0.843
min-cost threshold 0.154
''')
    yield p("scikit-learn can tune the threshold by cross-validation for you with `TunedThresholdClassifierCV(estimator, scoring=...)`, or fix one with `FixedThresholdClassifier`.")
    yield section("Calibration", "target")
    yield define("Calibrated classifier", "among all cases predicted with probability 0.8, about 80% are positive. Needed whenever the probability itself is used — expected-cost decisions, risk scores, combining models.")
    yield ul(
        "Logistic regression is usually well calibrated. Naive Bayes is overconfident; SVM scores aren't probabilities; random forests are under-confident near 0 and 1; boosted trees vary.",
        "Oversampling or class weights shift predicted probabilities upward — recalibrate afterwards.",
        "Measure with a **reliability diagram** (`calibration_curve`), the **Brier score** `mean((p − y)²)` and log-loss.",
        "Fix with `CalibratedClassifierCV`: `method=\"sigmoid\"` (Platt scaling, good for small data) or `\"isotonic\"` (more flexible, needs more data). It fits the calibrator on held-out folds.",
    )
    yield code('''
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.datasets import make_classification
        from sklearn.metrics import brier_score_loss, log_loss
        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import GaussianNB

        X, y = make_classification(n_samples=5000, n_features=20, n_informative=5, n_redundant=10, random_state=0)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)

        raw = GaussianNB().fit(X_tr, y_tr).predict_proba(X_te)[:, 1]
        cal = CalibratedClassifierCV(GaussianNB(), method="isotonic", cv=5).fit(X_tr, y_tr).predict_proba(X_te)[:, 1]
        print(round(brier_score_loss(y_te, raw), 4), round(brier_score_loss(y_te, cal), 4))   # 0.1217 0.1074 ← lower is better
        print(round(log_loss(y_te, raw), 3), round(log_loss(y_te, cal), 3))                   # 0.612 0.351 ← NB's overconfidence punished
    ''')
    yield qa("ROC-AUC or PR-AUC for a fraud model with 0.1% positives?",
             "PR-AUC (average precision). With so few positives, ROC-AUC can be very high while most alerts are still false alarms, because FPR divides by the huge number of negatives. PR-AUC's baseline is the prevalence (0.001), and it directly reflects alert precision at each recall level.")
    yield qa("What does an AUC of 0.5 mean? And 0.3?",
             "0.5: the scores rank positives above negatives no better than chance. 0.3: the ranking is systematically backwards — flipping the scores would give 0.7, which usually indicates a label or sign bug.")
    yield qa("How do you pick a classification threshold?",
             "On a validation set, from the business constraint: maximise expected profit/minimise expected cost given the cost of FP and FN, hit a required recall or precision, or match a capacity limit (top k alerts per day). Re-check it when base rates drift.")


@topic(G, "regression-metrics", "Regression Metrics", "calculator")
def _():
    yield lead("Regression metrics measure how far predictions are from the true values. They differ in how they punish large errors, in their units, and in what baseline they compare against.")
    yield table(
        ["Metric", "Formula", "Units", "Notes"],
        ["MAE", "`mean |y − ŷ|`", "Target's", "Every unit of error counts the same; less sensitive to outliers than MSE"],
        ["MSE", "`mean (y − ŷ)²`", "Target's squared", "Punishes large errors heavily; the usual training loss"],
        ["RMSE", "`√MSE`", "Target's", "Like MSE but interpretable; always ≥ MAE"],
        ["R²", "`1 − SS_res / SS_tot`", "Unitless", "Share of variance explained relative to predicting the mean"],
        ["Adjusted R²", "`1 − (1 − R²)(n − 1)/(n − p − 1)`", "Unitless", "Penalises extra predictors"],
        ["MAPE", "`mean |y − ŷ| / |y|`", "%", "Scale-free, but undefined at y = 0, explodes near 0, asymmetric"],
        ["RMSLE", "RMSE of `log(1 + y)`", "≈ relative", "For targets spanning orders of magnitude; penalises under-prediction more"],
        ["Median absolute error", "`median |y − ŷ|`", "Target's", "Robust to a few huge errors"],
    )
    yield formula("SS_res = Σ(yᵢ − ŷᵢ)²        SS_tot = Σ(yᵢ − ȳ)²        R² = 1 − SS_res / SS_tot")
    yield code('''
        import numpy as np
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error

        y = np.array([100, 150, 200, 250, 300])
        y_hat = np.array([110, 140, 210, 240, 380])            # one big miss

        print(mean_absolute_error(y, y_hat), mean_squared_error(y, y_hat))    # 24.0 1360.0
        print(round(root_mean_squared_error(y, y_hat), 2))                    # 36.88 ← pulled up by the 80 error
        ss_res, ss_tot = np.sum((y - y_hat) ** 2), np.sum((y - y.mean()) ** 2)
        print(round(1 - ss_res / ss_tot, 4), round(r2_score(y, y_hat), 4))    # 0.728 0.728
    ''')
    yield section("R² can be negative", "alert-triangle")
    yield p("R² compares the model with always predicting the mean of the true values. A model worse than that baseline has R² < 0 — common on a test set when a model has overfit or the data has drifted. R² = 1 is perfect; there is no lower bound.")
    yield code('''
        import numpy as np
        from sklearn.metrics import r2_score

        y = np.array([3.0, 5.0, 7.0, 9.0])
        print(r2_score(y, np.full(4, y.mean())))              # 0.0 ← predicting the mean
        print(r2_score(y, np.array([9.0, 7.0, 5.0, 3.0])))    # -3.0 ← worse than the mean
    ''')
    yield section("MAE vs RMSE, and the MAPE trap", "scale")
    yield code('''
        import numpy as np
        from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, root_mean_squared_error

        y = np.array([10.0, 10.0, 10.0, 10.0])
        spread = np.array([12.0, 8.0, 12.0, 8.0])      # four errors of 2
        one_big = np.array([10.0, 10.0, 10.0, 18.0])   # one error of 8
        print(mean_absolute_error(y, spread), mean_absolute_error(y, one_big))            # 2.0 2.0 ← MAE: same
        print(root_mean_squared_error(y, spread), root_mean_squared_error(y, one_big))    # 2.0 4.0 ← RMSE prefers spread-out errors

        demand = np.array([0.5, 100.0])                 # a near-zero actual
        print(round(mean_absolute_percentage_error(demand, np.array([1.5, 100.0])), 2))   # 1.0 ← off by 1 unit → 100% MAPE
    ''')
    yield table(
        ["Choose", "When"],
        ["MAE", "Errors cost proportionally; outliers shouldn't dominate; you want the median-type prediction"],
        ["RMSE", "Large errors are disproportionately bad; matches a squared-error training loss"],
        ["R²", "Communicating fit relative to a naive baseline (always report an error metric too)"],
        ["MAPE / sMAPE / WAPE", "Stakeholders think in percentages and actuals are far from 0 (WAPE = Σ|e| / Σ|y| is more stable)"],
        ["RMSLE", "Targets such as prices or counts spanning orders of magnitude"],
    )
    yield qa("Can R² be negative?",
             "Yes. R² = 1 − SS_res/SS_tot, and if the model's squared errors exceed those of predicting the mean of the true values, it is below 0. On training data with an intercept, OLS can't do worse than the mean, but on test data any model can.")
    yield qa("MAE or RMSE?",
             "RMSE squares errors before averaging, so it penalises large errors more and is sensitive to outliers; MAE treats all errors linearly. Pick the one that matches the cost of errors in the business. RMSE ≥ MAE always; a large gap signals a few big errors.")


@topic(G, "error_analysis", "Error Analysis", "bug")
def _():
    yield lead("Aggregate metrics say *how much* a model is wrong; error analysis finds *where* and *why*, so the next hour of work goes to the change that helps most.")
    yield section("First: which kind of error?", "stethoscope")
    yield table(
        ["Compare", "Gap means", "Typical fixes"],
        ["Human-level (≈ Bayes) error → training error", "**Avoidable bias**", "Bigger/more flexible model, better features, train longer, less regularisation"],
        ["Training → validation error", "**Variance** (overfitting)", "More data, regularisation, simpler model, augmentation"],
        ["Validation on training-like data → validation on target data", "**Data mismatch**", "Collect data like production, re-weight, domain features"],
        ["Validation → test error", "**Overfitting the validation set** (too many experiments)", "Bigger/fresh validation set, fewer comparisons"],
    )
    yield example("Human error 1%, training 8%, validation 10% → avoidable bias 7 points dominates variance 2 points: work on the model's capacity or features, not on regularisation.")
    yield section("The procedure", "list-numbers")
    yield steps(
        ("Collect the errors", "Take ~100 misclassified validation examples (or the worst regression residuals). Also look at the most **confidently** wrong ones."),
        ("Tag them", "Read each one and tag the apparent cause: blurry image, sarcasm, missing feature, rare category, **label error**…"),
        ("Count", "A spreadsheet of tag frequencies shows where the errors concentrate."),
        ("Prioritise", "Expected gain ≈ share of errors in the category × how fixable it is. Fixing 5% of errors can at most gain 5% of the error rate — the *ceiling*."),
        ("Act and repeat", "Targeted data collection, features, relabelling or a separate model for a segment; then re-measure."),
    )
    yield section("Slice the metrics", "chart-pie")
    yield p("An overall score can hide a segment where the model fails. Compute metrics per slice — country, device, new vs returning users, time period:")
    yield code_out('''
        import numpy as np
        import pandas as pd
        from sklearn.linear_model import LogisticRegression

        rng = np.random.default_rng(0)
        n = 3000
        segment = rng.choice(["returning", "new"], size=n, p=[0.85, 0.15])
        x = rng.normal(size=(n, 3))
        logit = 2 * x[:, 0] - x[:, 1]
        logit[segment == "new"] = 2 * x[segment == "new", 2]     # new users behave differently
        y = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)

        model = LogisticRegression().fit(x[:2000], y[:2000])
        test = pd.DataFrame({"segment": segment[2000:], "correct": model.predict(x[2000:]) == y[2000:]})
        print(round(test["correct"].mean(), 3))
        print(test.groupby("segment")["correct"].agg(["mean", "size"]).round(3))
    ''', out='''
0.778
            mean  size
segment
new        0.541   146
returning  0.819   854
''')
    yield p("The overall accuracy looks acceptable, yet for new users the model is barely better than a coin flip — invisible without slicing. Slicing is also the basis of **fairness** audits (see **Fairness, Privacy & Responsible AI**).")
    yield section("Which classes get confused?", "arrows-exchange")
    yield code('''
        import numpy as np
        from sklearn.datasets import load_digits
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import confusion_matrix
        from sklearn.model_selection import cross_val_predict
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_digits(return_X_y=True)
        pred = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)), X, y, cv=5)
        cm = confusion_matrix(y, pred)
        np.fill_diagonal(cm, 0)                                   # keep only the mistakes
        top = np.dstack(np.unravel_index(np.argsort(cm.ravel())[::-1][:3], cm.shape))[0]
        print([(int(a), int(b), int(cm[a, b])) for a, b in top])  # [(8, 1, 13), (3, 8, 12), (7, 9, 12)] ← (true, predicted, count): most frequent confusions
    ''')
    yield p("`cross_val_predict` gives every row an out-of-fold prediction — ideal for error analysis without touching the test set.")
    yield section("Checklist", "checklist")
    yield ul(
        "Are some “errors” actually **label mistakes**? Confidently wrong predictions often are — fix labels in the evaluation set first.",
        "Do errors cluster in a slice, a time period or a data source (a new app version, one sensor)?",
        "Is there a feature the model would need but doesn't have?",
        "Are errors near the decision threshold (threshold/calibration issue) or far from it (model/data issue)?",
    )
    yield qa("Your model's accuracy is 85%. How do you decide what to improve?",
             "Compare training, validation and (if available) human-level error to see whether bias or variance dominates. Then do error analysis: sample misclassified validation examples, tag causes, count them, and estimate the ceiling gain per category; slice metrics by key segments. Work on the largest, most fixable source first.")
    yield qa("What is slice-based evaluation?",
             "Computing metrics separately for meaningful subgroups (region, device, demographic, data source). It reveals failures hidden by the average and is required for fairness and reliability checks before deployment.")


@topic(G, "hyperparameter-tuning", "Hyperparameter Tuning", "adjustments-alt")
def _():
    yield lead("Hyperparameters (tree depth, `C`, learning rate) aren't learned by `fit`; you choose them by comparing cross-validated scores. The search strategy decides how much compute that takes.")
    yield table(
        ["Strategy", "How", "Pros / cons"],
        ["Manual", "Intuition + a few runs", "Quick for 1–2 knobs; not reproducible"],
        ["Grid search", "Every combination of listed values", "Exhaustive and simple; cost multiplies with each hyperparameter"],
        ["Random search", "Sample combinations from distributions", "Same budget explores more distinct values of each hyperparameter — usually better when only a few matter (Bergstra & Bengio, 2012)"],
        ["Successive halving / Hyperband", "Evaluate many configs on little data/iterations, keep the best fraction, give them more", "Much cheaper; early rounds can be noisy"],
        ["Bayesian optimisation", "A surrogate model (Gaussian process, TPE) predicts promising configs; an acquisition function balances exploring and exploiting", "Fewest evaluations for expensive models; sequential; tools: Optuna, scikit-optimize, Hyperopt"],
    )
    yield section("Grid search", "grid-dots")
    yield code('''
        from sklearn.datasets import load_breast_cancer
        from sklearn.model_selection import GridSearchCV, train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        X, y = load_breast_cancer(return_X_y=True)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)

        pipe = Pipeline([("scale", StandardScaler()), ("svc", SVC())])
        grid = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [0.001, 0.01, 0.1]}    # step__param names
        search = GridSearchCV(pipe, grid, cv=5, scoring="roc_auc").fit(X_tr, y_tr)

        print(search.best_params_)                      # {'svc__C': 10, 'svc__gamma': 0.001}
        print(round(search.best_score_, 4))             # 0.9962 ← mean CV score of the winner (optimistic)
        print(round(search.score(X_te, y_te), 4))       # 0.9937 ← refit on all training data, scored once on test
    ''')
    yield section("Random search", "dice")
    yield code('''
        from scipy.stats import loguniform, randint
        from sklearn.datasets import load_breast_cancer
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.model_selection import RandomizedSearchCV

        X, y = load_breast_cancer(return_X_y=True)
        dists = {
            "learning_rate": loguniform(0.01, 0.5),          # sample on a log scale
            "max_leaf_nodes": randint(4, 64),
            "min_samples_leaf": randint(5, 50),
            "l2_regularization": loguniform(1e-4, 10),
        }
        search = RandomizedSearchCV(HistGradientBoostingClassifier(random_state=0), dists, n_iter=15,
                                    cv=3, scoring="roc_auc", random_state=0).fit(X, y)
        print(round(search.best_score_, 4))                                   # 0.9934
        print(sorted(search.best_params_))                                    # ['l2_regularization', 'learning_rate', 'max_leaf_nodes', 'min_samples_leaf']
    ''')
    yield section("Successive halving", "filter")
    yield code('''
        from sklearn.experimental import enable_halving_search_cv  # noqa: F401  (still experimental)
        from sklearn.model_selection import HalvingGridSearchCV
        from sklearn.datasets import load_digits
        from sklearn.ensemble import RandomForestClassifier

        X, y = load_digits(return_X_y=True)
        grid = {"max_depth": [4, 8, None], "min_samples_leaf": [1, 5, 20], "max_features": ["sqrt", 0.5]}
        search = HalvingGridSearchCV(RandomForestClassifier(n_estimators=50, random_state=0), grid,
                                     resource="n_samples", factor=3, cv=3, random_state=0).fit(X, y)
        print(search.n_candidates_)              # [18, 6, 2] ← candidates per round: most are dropped early on little data
        print(search.n_resources_)               # [199, 597, 1791] ← samples used per round
    ''')
    yield section("Tips", "bulb")
    yield ul(
        "Search learning rates and regularisation strengths on a **log scale** (0.001, 0.01, 0.1 …).",
        "Go coarse → fine: a wide random search, then a narrow one around the best region.",
        "Tune the hyperparameters that matter most (for GBMs: learning rate, number of trees via early stopping, depth/leaves, subsampling).",
        "Put preprocessing in the `Pipeline` so each CV fold fits its own scaler/encoder, and tune preprocessing choices too (`\"scale\": [StandardScaler(), \"passthrough\"]`).",
        "`best_score_` is optimistically biased (it's the maximum of many noisy estimates) — report a held-out test score or nested CV.",
        "Fix `random_state`s and record every trial (MLflow, Weights & Biases) so results are reproducible.",
    )
    yield qa("Why can random search beat grid search?",
             "With a fixed budget, a grid tests only a few distinct values of each hyperparameter, and many runs are wasted varying ones that don't matter. Random search tries a new value of every hyperparameter in every run, so it explores the important dimensions much more finely.")
    yield qa("How does Bayesian optimisation work?",
             "It fits a cheap surrogate model of score as a function of hyperparameters to the trials so far, then picks the next trial by maximising an acquisition function (e.g. expected improvement) that trades off exploring uncertain regions and exploiting good ones. It needs far fewer expensive training runs than grid or random search.")
    yield qa("Can you tune hyperparameters on the test set?",
             "No — the chosen hyperparameters would be fitted to the test set, and its score would no longer estimate performance on new data. Tune with a validation set or cross-validation on the training data; use the test set once at the end.")


@topic(G, "imbalanced-data", "Imbalanced Data", "scale-outline")
def _():
    yield lead("When one class is rare (fraud 0.1%, disease 2%), a model can score high accuracy by ignoring it. Fix the **evaluation** first, then the **decision threshold**, and only then the training data or loss.")
    yield steps(
        ("Measure the right thing", "Precision/recall, PR-AUC, recall at a fixed precision, expected cost — never accuracy alone."),
        ("Split carefully", "Stratified splits and stratified CV so every fold has positives."),
        ("Tune the threshold", "Often the single most effective step (see **ROC, PR, Thresholds & Calibration**)."),
        ("Re-weight the loss", "`class_weight=\"balanced\"` or explicit weights make each positive count more."),
        ("Resample the training data", "Random over/under-sampling, SMOTE — inside the training folds only."),
        ("Get more positives", "More data, better labels, or reframe as anomaly detection when positives are extremely rare."),
    )
    yield section("Class weights", "weight")
    yield formula("balanced weight of class c = n_samples / (n_classes × n_c)")
    yield code_out('''
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import average_precision_score, precision_score, recall_score
        from sklearn.model_selection import train_test_split

        X, y = make_classification(n_samples=10000, weights=[0.97], class_sep=1.5, flip_y=0, random_state=0)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)

        for cw in (None, "balanced"):
            m = LogisticRegression(class_weight=cw).fit(X_tr, y_tr)
            p = m.predict_proba(X_te)[:, 1]
            pred = m.predict(X_te)
            print(cw, round(precision_score(y_te, pred), 3), round(recall_score(y_te, pred), 3),
                  round(average_precision_score(y_te, p), 3), round(p.mean(), 3))
    ''', out='''
None 0.824 0.56 0.725 0.03
balanced 0.263 0.947 0.713 0.141
''')
    yield p("Columns: precision, recall (at the default 0.5 threshold), PR-AUC, mean predicted probability (the true positive rate is 0.03). Class weights mainly move the **effective threshold**: recall rises, precision falls, while the ranking quality (PR-AUC) barely changes. Note the mean predicted probability — weighted models overestimate how often positives occur, so recalibrate if probabilities matter.")
    yield section("Resampling", "arrows-shuffle")
    yield table(
        ["Technique", "How", "Risk"],
        ["Random undersampling", "Drop majority rows", "Throws information away; fine when data is plentiful"],
        ["Random oversampling", "Duplicate minority rows", "Overfitting to the duplicated rows"],
        ["SMOTE", "Synthesise minority points between a minority row and one of its minority neighbours: `x_new = xᵢ + λ(x_nn − xᵢ)`, `λ ~ U(0, 1)`", "Can create points in overlapping/noisy regions; numeric features only (SMOTENC for categoricals)"],
    )
    yield code('''
        import numpy as np
        from sklearn.neighbors import NearestNeighbors

        rng = np.random.default_rng(0)
        minority = np.array([[1.0, 1.0], [1.2, 0.9], [0.9, 1.3], [1.4, 1.2]])

        def smote(X, n_new, k=2):
            nn = NearestNeighbors(n_neighbors=k + 1).fit(X)
            _, idx = nn.kneighbors(X)                     # idx[:, 0] is the point itself
            out = []
            for _ in range(n_new):
                i = rng.integers(len(X))
                j = idx[i, rng.integers(1, k + 1)]        # one of its k minority neighbours
                out.append(X[i] + rng.random() * (X[j] - X[i]))
            return np.array(out)

        print(smote(minority, 3).round(3).tolist())   # [[1.292, 1.146], [1.197, 0.902], [0.909, 1.274]] ← new points on segments between minority neighbours
    ''')
    yield p("In practice use the `imbalanced-learn` package (`SMOTE`, `RandomUnderSampler`) and its `imblearn.pipeline.Pipeline`, which applies samplers during `fit` only.")
    yield warn("Resample **only the training data, inside each CV fold**. Oversampling before the split copies (or interpolates) minority rows into the validation fold, so the model is tested on near-duplicates of its training rows — a classic leakage bug. Never resample the test set: it must keep the real class ratio.")
    yield p("Undersampling negatives inflates predicted probabilities. If negatives were kept with probability `β`, a score `pₛ` from the resampled model corresponds to the true-prior probability `p = β·pₛ / (β·pₛ − pₛ + 1)`.")
    yield qa("How do you handle a highly imbalanced classification problem?",
             "Use metrics that focus on the rare class (PR-AUC, recall at a precision target, cost), stratified CV, and tune the decision threshold. Then try class weights or resampling within training folds, gather more positive examples, and consider anomaly detection if positives are extremely rare. Recalibrate probabilities if they're used downstream.")
    yield qa("Does SMOTE always help?",
             "No. It often helps weak learners a little, but with strong models (gradient boosting) threshold tuning or class weights usually match it. It can hurt by generating minority points inside majority regions, and it distorts probabilities. Evaluate it with correctly nested CV against simple baselines.")


@topic(G, "common_pitfalls", "Common Pitfalls", "alert-triangle")
def _():
    yield lead("Most ML failures are process bugs, not algorithm choices. This checklist collects the classic ones with their symptoms and fixes.")
    yield table(
        ["Pitfall", "Symptom", "Fix"],
        ["Data leakage", "Offline scores too good; collapse in production", "Split first, `Pipeline`, check feature availability at prediction time (see **Data Leakage**)"],
        ["Duplicates / same entity across splits", "Near-perfect validation scores", "Deduplicate; group splits"],
        ["Random split of time-ordered data", "Production worse than validation", "Time-based split / `TimeSeriesSplit`"],
        ["Accuracy on imbalanced data", "High accuracy, useless model", "PR-AUC, recall/precision, cost; baseline comparison"],
        ["No baseline", "Can't tell if the model adds value", "Dummy model + existing rule"],
        ["Tuning on the test set", "Test score optimistic; disappointment later", "Validation/CV for all choices; nested CV"],
        ["Overfitting the validation set", "Many experiments, tiny “wins” that don't replicate", "Larger validation set, repeated CV, report variance"],
        ["Preprocessing fitted on all data", "Slightly-to-very optimistic scores", "Fit scalers/encoders/imputers/selectors inside CV"],
        ["Training–serving skew", "Same input, different prediction online vs offline", "One shared feature pipeline; log production features and compare"],
        ["Distribution shift", "Slow decay after launch", "Monitor inputs/outputs, retrain (see **Deployment, Monitoring & MLOps**)"],
        ["Spurious correlations (shortcut learning)", "Great on validation, fails on new sources", "Error analysis, explainability, test on data from other sources/times"],
        ["Selection / sampling bias", "Model fails on groups under-represented in training", "Fix collection; slice metrics"],
        ["Label noise", "Plateaued accuracy; confident “errors” that are right", "Audit labels, agreement metrics, clean the test set"],
        ["Unscaled features for distance/regularised models", "k-NN/SVM/Lasso behave oddly", "Scale inside the pipeline"],
        ["Single run, no uncertainty", "Improvements within noise", "CV mean ± std, confidence intervals, significance tests"],
        ["Deep learning on small tabular data", "Hours of tuning, worse than a forest", "Start with linear models and gradient boosting"],
    )
    yield section("Demo: duplicates across the split", "copy")
    yield p("Random labels — nothing to learn — but each row appears three times. A random split puts copies of test rows into training, and a 1-nearest-neighbour model “recognises” them:")
    yield code('''
        import numpy as np
        from sklearn.model_selection import GroupShuffleSplit, train_test_split
        from sklearn.neighbors import KNeighborsClassifier

        rng = np.random.default_rng(0)
        X0 = rng.normal(size=(300, 5))
        y0 = rng.integers(0, 2, size=300)                  # random labels
        X, y = np.repeat(X0, 3, axis=0), np.repeat(y0, 3)  # every row duplicated 3×
        row_id = np.repeat(np.arange(300), 3)

        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)
        print(round(KNeighborsClassifier(1).fit(X_tr, y_tr).score(X_te, y_te), 2))   # 0.97 ← "learned" noise

        tr, te = next(GroupShuffleSplit(test_size=0.3, random_state=0).split(X, y, groups=row_id))
        print(round(KNeighborsClassifier(1).fit(X[tr], y[tr]).score(X[te], y[te]), 2))   # 0.53 ← honest: chance level
    ''')
    yield section("Before you trust a result", "shield-check")
    yield ol(
        "Is there a baseline, and does the model clearly beat it?",
        "Was the split done first, and by time/group where needed?",
        "Is every feature available at prediction time?",
        "Is all preprocessing inside the pipeline?",
        "Is the metric the one the business cares about, at the threshold that will be used?",
        "Is the improvement larger than the run-to-run variance?",
        "Has the test set been used only once?",
    )
    yield qa("What are the most common mistakes in ML projects?",
             "Leakage (target leakage, preprocessing before splitting, duplicates or groups across splits, random splits of time series), evaluating with the wrong metric (accuracy on imbalanced data), no baseline, tuning on the test set, and ignoring training–serving skew and drift after deployment.")
    yield qa("A model does great offline but poorly in production. What could be wrong?",
             "Leakage in offline evaluation, training–serving skew (features computed differently online), distribution or concept drift since the training data, a different population in production (selection bias), or a threshold chosen for a different base rate. Compare logged production features and predictions with the training data to find out which.")
