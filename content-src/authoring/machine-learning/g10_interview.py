from kit import *

G = "Interview Prep"


@topic(G, "interview_scenarios", "Interview Scenarios", "user-check")
def _():
    yield lead("Scenario questions test whether you can turn a vague business problem into a working ML system. Use a consistent framework, state assumptions out loud, and always start from a baseline.")
    yield section("A framework for any ML design question", "route")
    yield steps(
        ("Clarify the goal", "What decision does the model drive? Who uses it? What counts as success (business metric)?"),
        ("Frame the ML task", "Target definition, prediction time, task type (classification, ranking…), constraints: latency, scale, interpretability, fairness."),
        ("Data & labels", "Sources, how labels are obtained and **how late they arrive**, class balance, biases, privacy."),
        ("Features", "Available at prediction time? Aggregates over history, real-time vs batch features, a feature store."),
        ("Model", "Baseline (rule or logistic regression) → gradient boosting → deep models if data is unstructured or huge."),
        ("Evaluation", "Offline metric that matches the goal, split by time/group, slices; then an online A/B test."),
        ("Serving", "Batch vs real-time, latency budget, fallbacks, shadow/canary rollout."),
        ("Monitoring & iteration", "Drift, data quality, delayed performance, feedback loops, retraining, fairness audits."),
    )
    yield section("Scenario 1 — Credit-card fraud detection", "credit-card")
    yield table(
        ["Aspect", "Answer"],
        ["Task", "Binary classification per transaction, scored in real time (e.g. < 50 ms) before approval"],
        ["Labels", "Chargebacks and analyst decisions — they arrive **weeks later**, so recent data is partly unlabelled; account for label delay in training windows and monitoring"],
        ["Imbalance", "Fraud ≈ 0.1%: evaluate with PR-AUC and recall at a precision the review team can handle; never accuracy"],
        ["Features", "Amount vs the card's history, merchant category, geo-velocity (distance since last transaction), device, counts in the last minute/hour/day from a low-latency feature store"],
        ["Model", "Gradient-boosted trees with class weights; rules as a baseline and safety net"],
        ["Validation", "Time-based split (train on earlier months, test on later), grouped so a card isn't in both"],
        ["Decision", "Threshold from **costs**: a missed fraud costs the amount; a false decline costs customer goodwill. Possibly three actions: approve / step-up authentication / decline"],
        ["Monitoring", "Fraudsters adapt (concept drift): monitor score distributions and precision of reviewed alerts, retrain frequently; shadow-deploy new models to check latency and agreement"],
    )
    yield section("Scenario 2 — A video recommendation feed", "device-tv")
    yield table(
        ["Aspect", "Answer"],
        ["Goal", "Long-term user satisfaction, measured online by watch time, return visits and explicit feedback — not clicks alone (clicks reward clickbait)"],
        ["Architecture", "**Candidate generation** (two-tower embeddings / matrix factorisation / co-watch) retrieves hundreds of videos from millions in milliseconds → **ranking** model scores them with rich features → re-ranking for diversity, freshness and policy"],
        ["Labels", "Consistent with the goal: e.g. predict expected watch time or a satisfaction-weighted engagement; treat clicks followed by an immediate exit as negative"],
        ["Features", "User history embeddings, video metadata and embeddings, context (device, time), freshness"],
        ["Offline eval", "Recall@k for retrieval, NDCG@k for ranking, on a time-based split"],
        ["Online eval", "A/B test on watch time and retention with guardrails (diversity, creator coverage, complaints)"],
        ["Pitfalls", "Popularity bias and feedback loops (the model only learns from what it showed) → exploration traffic; cold start for new videos → content embeddings"],
    )
    yield section("Scenario 3 — A CTR model's performance dropped", "trending-down")
    yield p("An ads click-through model was fine for months; this week online CTR and calibration fell. Debug in order — cheapest and most common causes first:")
    yield steps(
        ("Check the pipeline", "Recent deploys, schema changes, missing or defaulted features, logging bugs, a feature now computed differently online (training–serving skew)."),
        ("Check the data", "Data-quality dashboards: null rates, new categories, value ranges; PSI of key features between training data and this week."),
        ("Check the predictions", "Score distribution and calibration (predicted vs observed CTR) by segment; which slices dropped."),
        ("Check the world", "Seasonality, a new product or campaign, a competitor, a policy change — concept drift."),
        ("Fix", "Roll back if a release caused it; otherwise retrain on recent data (respecting label delay), recalibrate, and add monitors for whatever you missed."),
    )
    yield section("Scenario 4 — Customer churn", "user-minus")
    yield table(
        ["Aspect", "Answer"],
        ["Target", "No purchase/activity in the 30 days after a prediction date — defined with the retention team"],
        ["Features", "Only from before the prediction date: recency, frequency, monetary value, support tickets, plan changes, usage trends"],
        ["Split", "Train on earlier prediction dates, validate on later ones"],
        ["Metric", "Precision@k for the number of customers the team can contact; uplift if an intervention is tested"],
        ["Model", "Logistic regression baseline → gradient boosting; SHAP to explain the main drivers to the business"],
        ["Action", "Predicting churn isn't enough — an A/B test of the retention offer measures whether contacting high-risk customers actually changes behaviour (uplift modelling targets those who respond)"],
    )
    yield qa("You have only 200 labelled examples. What do you do?",
             "Start simple: a regularised linear model or small tree ensemble with cross-validation (repeated stratified K-fold) and strong domain features. Get more labels cheaply — active learning, weak supervision, semi-supervised learning — and use pretrained models/embeddings for text or images (transfer learning). Report confidence intervals: with 200 rows, scores are noisy.")
    yield qa("Your model is 99% accurate on a medical screening task. The doctors are unhappy. Why?",
             "If 99% of patients are healthy, predicting “healthy” always gives 99% accuracy while missing every case. Screening cares about recall (sensitivity) at an acceptable specificity; report the confusion matrix, choose the threshold with clinicians based on the cost of a missed case, and check calibration and performance across patient groups.")
    yield qa("How would you build a spam filter from scratch?",
             "Labels from user reports plus an annotated sample; features from text (TF-IDF or embeddings), sender reputation, links and headers; baseline Naive Bayes or logistic regression, then gradient boosting or a fine-tuned transformer; optimise recall at very high precision because false positives (lost real email) are costly; time-based validation; monitor drift as spammers adapt; retrain frequently.")


@topic(G, "interview-questions", "Interview Questions", "message-question")
def _():
    yield lead("Short, precise answers to the machine-learning questions asked most often — each points back to the topic that explains it in depth.")
    yield section("Fundamentals", "brain")
    yield qa("What is the difference between supervised, unsupervised and reinforcement learning?",
             "Supervised learns a mapping from inputs to known labels (classification, regression). Unsupervised finds structure without labels (clustering, dimensionality reduction). Reinforcement learning learns a policy from rewards received by acting in an environment. (See **Types of Learning**.)")
    yield qa("What is overfitting and how do you prevent it?",
             "The model learns noise in the training data, so training error is low but validation error is high. Prevent it with more data, simpler models, regularisation (L1/L2, pruning, early stopping), feature selection, bagging, and by validating properly with held-out data or cross-validation.")
    yield qa("Explain the bias–variance trade-off.",
             "Expected error = bias² + variance + irreducible noise. Simple models have high bias and low variance (underfit); flexible models the reverse (overfit). Model complexity is tuned to minimise the sum, using validation data. (See **Bias–Variance & Overfitting**.)")
    yield qa("Why do we split data into train, validation and test sets?",
             "Train fits parameters, validation guides choices (hyperparameters, features, threshold), and the untouched test set gives an unbiased final estimate. Using the test set for choices makes its score optimistic.")
    yield qa("What is cross-validation and when would you use GroupKFold or TimeSeriesSplit?",
             "Rotating held-out folds to estimate performance more reliably. GroupKFold when several rows belong to the same entity (patient, user) so an entity never appears on both sides; TimeSeriesSplit when data is time-ordered so models are always validated on the future.")
    yield qa("What is data leakage? Give two examples.",
             "Information unavailable at prediction time influencing training or evaluation. Examples: scaling or selecting features on the full dataset before splitting; a feature derived from the target (e.g. `refund_issued` for fraud); the same customer in train and test. (See **Data Leakage**.)")
    yield section("Algorithms", "binary-tree")
    yield qa("How does logistic regression work?",
             "It computes a linear score `w·x + b` and passes it through the sigmoid to get P(y = 1). It's trained by minimising log-loss (maximum likelihood), a convex problem. The decision boundary is linear; coefficients are changes in log-odds.")
    yield qa("L1 vs L2 regularisation?",
             "L1 (Lasso) adds `α·Σ|w|` and drives many weights exactly to zero — built-in feature selection. L2 (Ridge) adds `α·Σw²` and shrinks weights smoothly, handling correlated features well. Elastic Net combines them. Scale features first.")
    yield qa("How does a decision tree choose splits, and why do trees overfit?",
             "Greedily, by the largest impurity decrease (Gini/entropy for classification, squared error for regression). Grown without limits a tree isolates individual points; limit depth or leaf size, prune, or use ensembles.")
    yield qa("Random forest vs gradient boosting?",
             "A random forest averages many deep trees trained independently on bootstrap samples with random feature subsets — it reduces variance, is robust and needs little tuning. Gradient boosting adds shallow trees sequentially, each fitting the gradient of the loss of the current ensemble — it reduces bias and is usually more accurate but needs a learning rate and early stopping to avoid overfitting.")
    yield qa("How do SVMs work? What is the kernel trick?",
             "An SVM finds the hyperplane with the maximum margin; soft margins trade margin width against violations via `C`. The kernel trick replaces dot products with a kernel function, giving non-linear boundaries as if the data were mapped to a higher-dimensional space.")
    yield qa("How does k-NN work and what are its weaknesses?",
             "It predicts from the k nearest training points (vote or average). No training, but slow predictions, needs feature scaling, and suffers from irrelevant features and the curse of dimensionality.")
    yield qa("Why is Naive Bayes naive, and why does it still work?",
             "It assumes features are conditionally independent given the class. The probabilities it outputs are poorly calibrated, but the ranking of classes is often right, so classification works well — especially for text.")
    yield qa("How does k-means work and what are its assumptions?",
             "Alternately assign points to the nearest centroid and recompute centroids, minimising within-cluster squared distances. Assumes roughly spherical, similarly sized clusters and meaningful Euclidean distances; needs k, scaling and several initialisations.")
    yield qa("What is PCA and why scale before it?",
             "PCA projects data onto orthogonal directions of maximum variance (eigenvectors of the covariance matrix). Without scaling, features with large units dominate the variance and therefore the components.")
    yield section("Evaluation", "award")
    yield qa("Precision vs recall — when do you favour each?",
             "Precision = TP/(TP+FP): favour it when false alarms are costly (spam filtering). Recall = TP/(TP+FN): favour it when misses are costly (disease screening, fraud). The threshold moves you along the trade-off.")
    yield qa("ROC-AUC vs PR-AUC?",
             "ROC plots TPR vs FPR; its AUC is the probability a random positive is ranked above a random negative (0.5 = random). PR plots precision vs recall; its baseline is the positive prevalence, so it's more informative for rare positives.")
    yield qa("Can R² be negative?",
             "Yes — when predictions are worse than always predicting the mean of the true values, e.g. on test data after overfitting.")
    yield qa("How do you handle imbalanced data?",
             "Right metric (PR-AUC, recall at precision, cost), stratified splits, threshold tuning, class weights, resampling inside training folds only, more positive data; recalibrate probabilities afterwards. (See **Imbalanced Data**.)")
    yield qa("What is model calibration and how do you check it?",
             "A model is calibrated if events predicted with probability p happen about p of the time. Check with a reliability diagram, Brier score or log-loss; fix with Platt scaling or isotonic regression via `CalibratedClassifierCV`.")
    yield qa("How would you compare two models statistically?",
             "On the same test rows: McNemar's test on disagreements, or a bootstrap confidence interval of the metric difference; across CV folds a corrected paired t-test. Also ask whether the difference is practically meaningful.")
    yield section("Features & data", "table")
    yield qa("How do you handle missing values?",
             "Understand why they're missing (MCAR/MAR/MNAR). Options: drop, impute (median/most-frequent, KNN, iterative), add missing-indicator columns, or use models that handle NaN natively. Fit imputers on training data inside the pipeline.")
    yield qa("One-hot vs label (ordinal) encoding?",
             "One-hot for nominal categories so no false order is implied; ordinal codes for truly ordered categories (and acceptable for tree models). High cardinality → target encoding with cross-fitting, hashing or embeddings.")
    yield qa("Which models need feature scaling?",
             "Distance- and gradient-based or regularised models: k-NN, k-means, SVM, PCA, regularised linear/logistic regression, neural networks. Tree-based models don't.")
    yield qa("What is the curse of dimensionality?",
             "As dimensions grow, data becomes sparse and distances concentrate, so neighbourhoods stop being local and much more data is needed. It hurts distance-based methods most; use feature selection, dimensionality reduction or more data.")
    yield section("Production & responsible AI", "server")
    yield qa("What is concept drift vs data drift?",
             "Data (covariate) drift: P(X) changes. Label shift: P(y) changes. Concept drift: P(y|X) changes, so the learned relationship is outdated. Monitor inputs, predictions and delayed outcomes; retrain on recent data.")
    yield qa("What is training–serving skew?",
             "Features computed differently in training and in production (different code, freshness or bugs), so the model receives inputs unlike its training data. Prevent with shared pipelines or a feature store and by comparing logged production features with training data.")
    yield qa("How do you explain a black-box model's predictions?",
             "Globally with permutation importance and partial dependence; locally with SHAP (additive Shapley attributions) or LIME; counterfactuals for “what would change the decision”. Remember explanations describe the model, not causality.")
    yield qa("How do you measure fairness?",
             "Compute metrics per group: selection rate (demographic parity), TPR (equal opportunity), TPR and FPR (equalized odds), precision and calibration. Differing base rates make some criteria mutually incompatible, so choose based on the application and document the trade-off.")
    yield section("Beyond classic ML", "arrows-right")
    yield qa("When would you use deep learning instead of classic ML?",
             "For unstructured data (images, audio, text), very large datasets, or when a pretrained model can be fine-tuned. For small or medium tabular data, gradient-boosted trees are usually as good or better with less effort. (See **Deep Learning**.)")
    yield qa("What is the relationship between logistic regression and a neural network?",
             "Logistic regression is a single neuron with a sigmoid activation trained with log-loss. Neural networks stack many such units with non-linear activations, learning intermediate features, and are trained with backpropagation and gradient descent.")
