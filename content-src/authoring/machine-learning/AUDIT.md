# Audit — old Machine Learning notes (`legacy-html/machine_learning_ai/index.html`, 12 topics)

Format: **topic → problem → correction**. "Omission" = an essential concept that was missing.
All corrections are applied in the rebuilt subject (`build.py` + `g*_*.py`).

## Whole subject

- **No runnable code at all** → not one sklearn/NumPy example; nothing was verified. → Every topic now has executed examples with checked output.
- **Core algorithms never explained** → linear regression/OLS, logistic regression, KNN, Naive Bayes, SVM, decision trees (Gini/entropy/information gain), bagging, AdaBoost/gradient boosting, k-means, hierarchical clustering, DBSCAN, GMM, PCA appear only as one-line cards or not at all. → One topic per algorithm: intuition, key formula, sklearn example, pros/cons.
- **Core math missing** → no loss functions, no gradient descent / learning rate, no regularization beyond the words "L1/L2", no bias–variance decomposition formula, no curse of dimensionality. → Added.
- **Data preparation missing** → no categorical encoding (one-hot/ordinal/target), no feature selection, no EDA, no cross-validation variants (Group K-Fold, nested CV), no sklearn `Pipeline`/`ColumnTransformer`. → Added.
- **Evaluation gaps** → no multi-class averaging (macro/micro/weighted), no log-loss, specificity, MCC, calibration, MAPE, adjusted R², no AUC interpretation. → Added.
- **Structure** → precision/recall/F1 defined twice (Error Analysis and Evaluation Metrics); over/underfitting defined twice (Train/Test and Common Pitfalls); statistics topic placed before problem formulation; the pipeline diagram and the stage list disagree (8 vs 12 steps, different order). → Regrouped into 10 groups, beginner → interview.
- **Scope creep** → CNN/RNN/Transformer cards, DQN, LLM hallucinations and FGSM belong to the Deep Learning / Generative AI subjects. → Replaced by a short "from ML to neural networks" bridge and cross-references.

## data_modeling (Data-Driven Modeling)

- Definition "discover statistical correlations and map inputs to outputs" → describes only supervised learning; ML also includes unsupervised and reinforcement learning, and models learn patterns, not just correlations. → Mitchell's definition (task T, experience E, performance P) plus the three learning types.
- `y = f(x) + ε` presented as *the* definition of ML → it is the supervised-regression setup only. → Kept, labelled as the supervised setting.
- "Types of Data" lists Structured, Unstructured, Time-series, Images, Audio, Text as parallel categories → images/audio/text *are* unstructured data; mixes structure with modality. "Structured data in SQL/NoSQL with strict schemas" → NoSQL stores are usually schema-flexible. → Separate structure (tabular vs unstructured) from statistical feature types.
- Omission → statistical feature types (continuous, discrete, nominal, ordinal, binary, datetime) — the thing that decides preprocessing. → Added (Data Types & EDA).
- "Features (X): the **independent** inputs" → features are usually correlated with each other; "independent variable" is regression jargon, not a property. → "input variables (predictors)".
- Missing values card → no MCAR/MAR/MNAR, no missing-indicator, no "fit the imputer on the training split only"; ">50 % missing → drop" presented as a rule. → Corrected; missingness can itself be predictive.
- Standardization card → omits that scaling does not change the distribution's shape (it does not make data normal) and that tree models don't need scaling. → Added.
- Dimensionality-reduction card → PCA must be applied after standardizing (otherwise large-unit features dominate) and is unsupervised (can discard low-variance but predictive directions). → Added.

## train_test (Train/Test Protocols)

- Random sampling "Use case: uniformly distributed datasets" → meaningless; the real condition is i.i.d. rows. A random split is wrong for time-ordered data and for grouped data (several rows per patient/user). → Stratified, group and time-based splits explained.
- "K-fold … overcomes small-data validation noise" → it only *reduces* the variance of the estimate. Also omitted: the final model is refit on all training data; Group K-Fold; nested CV for tuning + estimating; LOOCV. → Added (Cross-Validation topic).
- Leakage example "session duration to predict click probability" → unclear; the essential types (target leakage, train/test contamination, duplicate/group leakage, temporal leakage, preprocessing fit outside CV) were missing. → Dedicated Data Leakage topic with a runnable demo (feature selection on noise → fake 90%+ accuracy).
- Bias–variance SVG → x-axis "Model Complexity (e.g. Tree Depth, **NN Epochs**)" mixes training time with capacity; the drawing has **no irreducible-error (noise) term** — total error must be Bias² + Variance + σ² and can never drop below σ², but the curve dips below Bias² + Variance near the optimum. → Formula `E[(y−ŷ)²] = Bias² + Variance + σ²` and a measured train/test-error table by polynomial degree.
- Overfitting fixes → "add dropout layers" is neural-net-specific; missing early stopping, simpler model, feature selection, ensembling (bagging), cross-validation. → Corrected.
- Random search "statistically superior" → overstated; it is more *efficient* when only a few hyperparameters matter (Bergstra & Bengio 2012). Omission: Bayesian optimization, successive halving; tuning must never use the test set. → Hyperparameter Tuning topic.

## error_analysis (Error Analysis)

- Topic named "Error Analysis" but never describes the procedure (sample misclassified examples, tag error categories, count, prioritise by frequency × fixability). → Rewritten around the procedure, slicing, and the train/val/human-level diagnosis.
- Confusion-matrix diagram puts positives first → sklearn's `confusion_matrix` orders labels ascending, i.e. `[[TN, FP], [FN, TP]]` for 0/1 labels; readers get this wrong constantly. → Shown with real output.
- F1 "essential for class-imbalanced evaluations" → overstated: F1 ignores true negatives, depends on the threshold and on which class is called positive. → Context given; PR-AUC/MCC/cost-based metrics as alternatives.
- **PR-curve SVG ends at precision = 0 when recall = 1** → wrong: at recall = 1 (everything predicted positive) precision equals the **positive-class prevalence**, and a random classifier's PR curve is a horizontal line at the prevalence (not shown). → Stated and demonstrated.
- "Models output probability ranges [0, 1]. The default threshold is 0.5" → many models output uncalibrated scores (SVM decision function, boosted trees); 0.5 is only right for calibrated probabilities with equal error costs. Thresholds must be chosen on validation data. → Threshold & calibration topic.
- Omission → avoidable bias = train error − human-level error; variance = val − train; train–val vs val–test gap for data mismatch. → Added.

## stat_significance (Statistical Significance)

- CLT stated without conditions → needs independent samples from a distribution with **finite variance**; says nothing about how large n must be; standard error `σ/√n` never given. → Corrected with a simulation.
- Variance "mean squared deviations from the mean" → no population (÷n) vs sample (÷(n−1)) distinction. → Added (and NumPy's `ddof` pitfall).
- p-value defined correctly, but none of the classic misreadings addressed → a p-value is **not** P(H₀ is true) and not the effect size; statistical ≠ practical significance. Missing: Type I/II errors, power, confidence intervals, t-test/χ² choice, multiple-testing correction, and — despite the subtitle "verifying if performance improvements are real" — **no method for comparing two models** (paired tests across folds, McNemar, bootstrap CI). → Added.
- A/B testing card → missing: fix sample size in advance, **no peeking / optional stopping** (inflates false positives), randomization unit, sample-ratio mismatch, novelty effects. → Dedicated A/B Testing topic with a two-proportion z-test and sample-size calculation.

## problem_formulation (Problem Formulation)

- Learning paradigms → omits semi-supervised and **self-supervised** learning (how modern foundation models are pretrained). → Added (Types of Learning).
- Spam blueprint "Labels: user-flagged Mark as Spam" → labels are biased/noisy (most spam is never flagged, some wanted mail is), with no discussion. → Discussed.
- Omissions → "do you need ML at all?", a non-ML baseline, business metric vs ML metric, whether features exist at prediction time, cost of each error type. → Added.
- Forecasting metric "MAPE / RMSE" → MAPE is undefined when actuals are 0 and asymmetric. → Caveat in Regression Metrics.

## data_collection (Collection & Annotation)

- Weak supervision described as "deterministic labeling functions" → the point of Snorkel-style weak supervision is combining many noisy labeling functions with a label model that estimates their accuracies and correlations. → Corrected.
- Omissions → sampling/selection bias and representativeness, licensing/consent for scraped data, label definitions & annotation guidelines, measuring agreement in code (Cohen's κ), data versioning. → Added.

## modeling_approaches (Modeling Approaches)

- Decision trees "handle categorical features **natively**" → true of some implementations (C4.5, LightGBM, CatBoost, sklearn's HistGradientBoosting) but **not** of scikit-learn's `DecisionTreeClassifier`, which needs numeric encoding. → Corrected.
- Gradient boosting "each tree learns from the residual errors" → each tree fits the **negative gradient of the loss**; that equals the residual only for squared error. Also missing: learning rate/shrinkage, and that boosting **can overfit** as trees are added (unlike random forests). → Boosting topic.
- SVM "maximizes margins **using kernel tricks**" → conflates two ideas: margin maximization is the core; kernels are an optional way to get non-linear boundaries. Missing: soft margin `C`, feature scaling requirement, poor scaling to large n, no native probabilities. → SVM topic.
- KNN / k-means cards → no mention that both need feature scaling; k-means assumptions (roughly spherical, similar-size clusters, Euclidean distance, sensitive to initialisation → k-means++, n_init) missing; DBSCAN's weakness with varying densities missing. → Corrected.
- Deep-learning and RL cards → out of scope and very thin (RL "Environment: target context system" is not a definition). → Short bridge + links to Deep Learning / Artificial Intelligence subjects.
- Omission → how to choose between algorithms (data size, interpretability, tabular vs unstructured, latency). → "Choosing & Combining Models".

## evaluation_metrics (Evaluation Metrics)

- "Accuracy: do not use for imbalanced datasets" → too absolute; it is *misleading* there and must be compared with the majority-class baseline. → Corrected with a demo (99% accuracy doing nothing).
- MAE "robust to outliers" → only *less sensitive* than MSE (linear vs quadratic penalty). → Corrected.
- ROC-AUC → missing its meaning: probability that a random positive is ranked above a random negative; 0.5 = random. PR-AUC → missing that its baseline is the prevalence. → Added.
- R² → formula `1 − SS_res/SS_tot` missing; adjusted R² missing. (Negative R² was stated correctly.) → Added.
- Omissions → log-loss, specificity, balanced accuracy, MCC, Fβ, macro/micro/weighted averaging, Brier score. → Added.

## common_pitfalls (Common Pitfalls)

- Class imbalance fixes "Focal loss, class weights, SMOTE" → missing the first steps (right metric, threshold tuning); SMOTE/oversampling must be applied **inside the training folds only** (doing it before the split leaks duplicates into validation); resampling/class weights distort predicted probabilities (recalibrate). → Imbalanced Data topic.
- Small datasets "use transfer learning or data augmentation" → deep-learning-specific; for tabular data: simpler/regularized models, cross-validation, domain features. → Corrected.
- Distribution shift → omits **label (prior) shift** (P(y) changes); only covariate and concept drift given. → Added (Deployment & Monitoring).
- Leakage → only the mildest example (global scaling). → Dedicated topic.

## ai_ethics (Responsible AI & Ethics)

- Omissions → equal opportunity, predictive parity/calibration by group, the **impossibility result** (calibration and equalized odds cannot both hold when base rates differ, except for a perfect classifier), and "fairness through unawareness" failing because of proxy features. → Added with computed group metrics.
- "Explainability (post-hoc): using **external models** (LIME, SHAP)" → LIME fits a local surrogate model; SHAP is a Shapley-value attribution method (TreeSHAP is exact for trees), not an external model. → Explainability topic.
- "Interpretability by design: linear regression parameters directly reflect feature contributions" → only on comparable feature scales and without strong collinearity, and coefficients are associations, not causal effects. → Corrected.
- Differential privacy "adding noise to database queries so individuals cannot be identified" → DP is a formal guarantee (ε) that outputs barely change whether or not any one person is included; noise is the mechanism. Federated learning alone does not guarantee privacy (updates can leak). → Corrected.
- "Hallucinations — mitigate with RAG"; "adversarial attacks — fix with adversarial training" → both reduce, neither fixes; and both are Generative AI / Deep Learning material. → Moved out by reference.

## ml_pipeline (End-to-End ML Pipeline)

- SVG order "Model & Train → Error Analysis → Evaluate & Validate" → evaluation comes before error analysis; the diagram omits EDA and the **train/test split**, which must happen before fitting any preprocessing. The stage list calls scaling "feature engineering" (feature engineering is *creating* features). → Rewritten; the rebuilt topic is a runnable sklearn Pipeline + ColumnTransformer project.
- Omissions → baseline model, model versioning/registry, batch vs online serving, training–serving skew, CI/CD/continuous training. → Deployment & Monitoring topic.

## interview_scenarios (Interview Scenarios)

- YouTube recommender → formulation says "probability of clicking **and watching**" but labels are "click = 1, skip = 0" while the ranker optimises "expected watch time" — inconsistent; click labels reward clickbait. → Consistent labels (watch time / satisfaction signals), explicit candidate-generation + ranking.
- Fraud detection → omits label delay (chargebacks arrive weeks later), time-based validation, cost-based threshold, adversarial drift. → Added.
- CTR model degradation → jumps to "retrain weekly" without first checking for pipeline bugs / training–serving skew, calibration drift, or label delay. → Ordered debugging checklist.
- Omission → a bank of standard ML interview questions (bias–variance, L1 vs L2, bagging vs boosting, …). → New "Interview Questions" topic.
