from kit import *
from mlkit import code_out

G = "Statistics for ML"


@topic(G, "probability-distributions", "Probability, Bayes & Distributions", "chart-bell-curve")
def _():
    yield lead("ML models are statistical models. A handful of probability ideas — conditional probability, Bayes' rule, common distributions, the central limit theorem and maximum likelihood — explain most of what they do.")
    yield section("Rules you use constantly", "math-symbols")
    yield table(
        ["Rule", "Formula"],
        ["Conditional probability", "`P(A | B) = P(A ∩ B) / P(B)`"],
        ["Independence", "`P(A ∩ B) = P(A)·P(B)` ⇔ `P(A | B) = P(A)`"],
        ["Addition", "`P(A ∪ B) = P(A) + P(B) − P(A ∩ B)`"],
        ["Total probability", "`P(B) = Σᵢ P(B | Aᵢ)·P(Aᵢ)` for a partition `A₁, A₂, …`"],
        ["Bayes' rule", "`P(A | B) = P(B | A)·P(A) / P(B)`"],
    )
    yield section("Bayes' rule and the base-rate fallacy", "percentage")
    yield p("A disease affects 1% of people. A test catches 99% of cases (sensitivity) and correctly clears 95% of healthy people (specificity). Given a positive test, how likely is the disease?")
    yield code('''
        prior = 0.01                 # P(disease)
        sens = 0.99                  # P(+ | disease)
        fpr = 1 - 0.95               # P(+ | healthy)

        p_pos = sens * prior + fpr * (1 - prior)          # total probability of a positive test
        posterior = sens * prior / p_pos                  # Bayes' rule
        print(round(p_pos, 4), round(posterior, 3))       # 0.0594 0.167 ← only about 1 in 6 positives is sick
    ''')
    yield p("Most positives come from the huge healthy group. This is exactly why **precision** collapses on rare classes even for an accurate classifier — and why the base rate must be part of any threshold decision.")
    yield section("Describing data", "calculator")
    yield table(
        ["Statistic", "Definition", "Note"],
        ["Mean", "`Σx / n`", "Sensitive to outliers"],
        ["Median", "Middle value", "Robust to outliers and skew"],
        ["Variance (population)", "`Σ(x − μ)² / n`", "Average squared deviation"],
        ["Variance (sample)", "`Σ(x − x̄)² / (n − 1)`", "Bessel's correction — unbiased estimate of the population variance"],
        ["Standard deviation", "√variance", "Same units as the data"],
        ["Covariance / correlation", "`cov(X, Y)`; `ρ = cov / (σ_X σ_Y)`", "Correlation is unitless, −1 … 1, linear only"],
    )
    yield code('''
        import numpy as np
        import pandas as pd

        x = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        print(x.mean(), np.median(x))                      # 5.0 4.5
        print(np.var(x), round(np.var(x, ddof=1), 4))      # 4.0 4.5714 ← NumPy default ddof=0 (population)
        print(round(pd.Series(x).var(), 4))                # 4.5714 ← pandas default ddof=1 (sample) — a classic mismatch
    ''')
    yield section("Common distributions", "chart-histogram")
    yield table(
        ["Distribution", "Models", "Mean", "Variance", "ML example"],
        ["Bernoulli(p)", "One yes/no trial", "`p`", "`p(1 − p)`", "A single click; logistic regression's likelihood"],
        ["Binomial(n, p)", "Successes in n trials", "`np`", "`np(1 − p)`", "Conversions out of n visitors"],
        ["Poisson(λ)", "Counts of rare events in an interval", "`λ`", "`λ`", "Orders per hour, defects per batch"],
        ["Uniform(a, b)", "Equally likely values", "`(a + b)/2`", "`(b − a)²/12`", "Random search, initialisation"],
        ["Normal(μ, σ²)", "Sums of many small effects", "`μ`", "`σ²`", "Measurement noise; linear-regression errors"],
        ["Exponential(λ)", "Waiting time between Poisson events", "`1/λ`", "`1/λ²`", "Time between requests"],
        ["Log-normal", "Products of many effects; positive, right-skewed", "—", "—", "Incomes, prices, session lengths (log them)"],
    )
    yield code('''
        from scipy import stats

        print(round(stats.binom.pmf(3, n=10, p=0.2), 4))                  # 0.2013 ← P(exactly 3 conversions of 10)
        print(round(stats.poisson.pmf(0, mu=2), 4))                        # 0.1353 ← P(no orders in an hour | 2 per hour on average)
        print([round(float(stats.norm.cdf(k) - stats.norm.cdf(-k)), 4) for k in (1, 2, 3)])   # [0.6827, 0.9545, 0.9973] ← the 68–95–99.7 rule
        print(round(stats.norm.ppf(0.975), 3))                             # 1.96 ← z for a two-sided 95% interval
    ''')
    yield section("Central limit theorem", "chart-bell-curve")
    yield define("Central limit theorem", "for **independent, identically distributed** observations with **finite variance** σ², the distribution of the sample mean approaches a normal distribution with mean μ and standard deviation σ/√n as n grows — whatever the shape of the original distribution.")
    yield formula("standard error of the mean = σ / √n")
    yield code('''
        import numpy as np
        from scipy.stats import skew

        rng = np.random.default_rng(0)
        data = rng.exponential(scale=1.0, size=(10000, 50))    # very skewed: mean 1, sd 1
        means = data.mean(axis=1)                              # 10,000 sample means, n = 50 each

        print(round(skew(data.ravel()), 2), round(skew(means), 2))   # 2.02 0.31 ← raw skew ≈ 2; means nearly symmetric
        print(round(means.mean(), 3), round(means.std(), 3), round(1 / np.sqrt(50), 3))   # 0.999 0.143 0.141 ← sd of means ≈ σ/√n
    ''')
    yield warn("The CLT is about **means** (and sums), not the data: it does not make your features normal. It needs finite variance (it fails for the Cauchy distribution) and independent observations; how large n must be depends on the skew — 30 is folklore, not a law.")
    yield p("The **law of large numbers** is the simpler cousin: sample averages converge to the expected value. Together they justify confidence intervals, A/B tests and cross-validation averages.")
    yield section("Maximum likelihood — where loss functions come from", "target")
    yield p("Maximum likelihood estimation picks the parameters under which the observed data is most probable. Two famous consequences: assuming Gaussian noise, maximising the likelihood of a regression model is exactly **minimising squared error**; assuming Bernoulli labels, it is exactly **minimising log-loss** (logistic regression).")
    yield code('''
        import numpy as np
        from scipy.optimize import minimize_scalar

        flips = np.array([1, 0, 1, 1, 0, 1, 1, 1, 0, 1])          # 7 heads in 10
        nll = lambda p: -np.sum(flips * np.log(p) + (1 - flips) * np.log(1 - p))   # negative log-likelihood = log-loss × n
        best = minimize_scalar(nll, bounds=(0.01, 0.99), method="bounded")
        print(round(best.x, 3), flips.mean())                     # 0.7 0.7 ← the MLE of p is the sample proportion
    ''')
    yield qa("What is Bayes' theorem and why does it matter in ML?",
             "`P(A|B) = P(B|A)P(A)/P(B)`: it updates a prior belief with evidence. It underlies Naive Bayes, Bayesian inference and the base-rate reasoning behind precision on rare classes — a 99%-sensitive test for a 1%-prevalence disease still gives mostly false positives.")
    yield qa("State the central limit theorem.",
             "For i.i.d. samples with finite variance, the sampling distribution of the mean tends to a normal distribution with mean μ and standard deviation σ/√n as n grows, regardless of the population's shape. It justifies normal-based confidence intervals and tests for means and proportions.")
    yield qa("Why divide by n − 1 for the sample variance?",
             "Deviations are measured from the sample mean, which is itself fitted to the data, so they are on average too small; dividing by n − 1 (one degree of freedom used by the mean) makes the variance estimate unbiased.")


@topic(G, "stat_significance", "Hypothesis Tests & Significance", "chart-arrows-vertical")
def _():
    yield lead("A hypothesis test asks whether a difference — between groups, between models — is larger than chance alone would plausibly produce. Used carefully, it separates real improvements from noise.")
    yield steps(
        ("State hypotheses", "Null `H₀`: no difference (model B's accuracy = model A's). Alternative `H₁`: there is a difference."),
        ("Choose α", "The false-positive rate you accept, usually 0.05 — decided before looking at the data."),
        ("Compute a test statistic", "How far the observed data is from what `H₀` predicts, in units of its standard error."),
        ("Get the p-value", "The probability, **assuming H₀ is true**, of a result at least as extreme as observed."),
        ("Decide", "Reject `H₀` if p ≤ α; otherwise “fail to reject” (not the same as proving `H₀`)."),
    )
    yield table(
        ["", "H₀ true", "H₀ false"],
        ["**Reject H₀**", "Type I error (false positive) — probability α", "Correct — probability = **power** (1 − β)"],
        ["**Fail to reject**", "Correct", "Type II error (false negative) — probability β"],
    )
    yield section("What a p-value is not", "alert-triangle")
    yield ul(
        "Not the probability that `H₀` is true, nor that the result is due to chance.",
        "Not the size or importance of the effect — with huge samples, trivial differences become “significant”.",
        "Not a pass/fail on truth: p = 0.049 and p = 0.051 are practically the same evidence.",
        "Report the **effect size with a confidence interval** alongside the p-value.",
    )
    yield section("Choosing a test", "list-details")
    yield table(
        ["Question", "Test", "SciPy"],
        ["Mean of two independent groups", "Welch's t-test (no equal-variance assumption)", "`ttest_ind(a, b, equal_var=False)`"],
        ["Same units measured twice / paired", "Paired t-test", "`ttest_rel`"],
        ["Two groups, no normality assumption", "Mann–Whitney U", "`mannwhitneyu`"],
        ["Means of 3+ groups", "One-way ANOVA", "`f_oneway`"],
        ["Two categorical variables / proportions", "Chi-square test of independence; z-test for two proportions", "`chi2_contingency`"],
        ["Same distribution?", "Kolmogorov–Smirnov", "`ks_2samp`"],
        ["Two classifiers on the same test set", "McNemar's test (on disagreements)", "`binomtest` on the discordant counts"],
    )
    yield code('''
        import numpy as np
        from scipy import stats

        rng = np.random.default_rng(0)
        a = rng.normal(loc=50, scale=10, size=200)      # e.g. session minutes, variant A
        b = rng.normal(loc=53, scale=12, size=200)      # variant B

        t, p = stats.ttest_ind(b, a, equal_var=False)
        print(round(t, 2), round(p, 4))                 # 1.61 0.1076 ← not significant at 0.05 (true gap is 3, but n is small)

        diff = b.mean() - a.mean()
        se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        print(round(diff, 2), [round(float(diff - 1.96 * se), 2), round(float(diff + 1.96 * se), 2)])   # 1.79 [-0.38, 3.95] ← effect and its 95% CI: includes 0

        table = np.array([[120, 880], [150, 850]])      # clicked / not clicked, per variant
        chi2, p_chi, dof, _ = stats.chi2_contingency(table)
        print(round(chi2, 2), round(p_chi, 4), dof)     # 3.6 0.0577 1 ← 12% vs 15% CTR: borderline with 1,000 users each
    ''')
    yield note("A 95% confidence interval comes from a procedure that captures the true value in 95% of repeated experiments. If the interval for a difference excludes 0, the corresponding two-sided test at α = 0.05 rejects `H₀`.")
    yield section("Bootstrap confidence intervals", "refresh")
    yield p("For metrics with no simple formula (F1, AUC, median), resample the test set **with replacement** many times, recompute the metric each time, and read off percentiles:")
    yield code('''
        import numpy as np
        from sklearn.datasets import load_breast_cancer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import f1_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, y = load_breast_cancer(return_X_y=True)
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)
        pred = make_pipeline(StandardScaler(), LogisticRegression()).fit(X_tr, y_tr).predict(X_te)

        rng = np.random.default_rng(0)
        boot = []
        for _ in range(2000):
            idx = rng.integers(0, len(y_te), len(y_te))       # resample test rows with replacement
            boot.append(f1_score(y_te[idx], pred[idx]))
        print(round(f1_score(y_te, pred), 3), np.percentile(boot, [2.5, 97.5]).round(3))   # 0.967 [0.937 0.99 ] ← F1 and its 95% CI
    ''')
    yield section("Is model B really better than model A?", "git-compare")
    yield p("Both models are scored on the **same** test rows, so compare them in a paired way. McNemar's test looks only at the rows where they disagree: `b` = A right & B wrong, `c` = A wrong & B right. Under `H₀` each disagreement is a coin flip:")
    yield code('''
        import numpy as np
        from scipy.stats import binomtest

        rng = np.random.default_rng(1)
        y = rng.integers(0, 2, 1000)
        a_right = rng.random(1000) < 0.85                  # model A: ~85% accurate
        b_right = np.where(rng.random(1000) < 0.8, a_right, rng.random(1000) < 0.90)   # B: correlated with A, slightly better

        b = int(np.sum(a_right & ~b_right))
        c = int(np.sum(~a_right & b_right))
        print(a_right.mean(), b_right.mean(), b, c)        # 0.832 0.841 17 26
        print(round(binomtest(b, b + c, 0.5).pvalue, 4))   # 0.2221 ← exact McNemar p-value: B's 9 extra wins could be chance
    ''')
    yield ul(
        "Across CV folds, a paired t-test on per-fold scores is common but optimistic (folds share training data); the corrected resampled t-test (Nadeau & Bengio) or repeated CV is safer.",
        "A bootstrap CI of the **difference** in metric (resampling rows, scoring both models on the same resample) is simple and works for any metric.",
    )
    yield section("Multiple comparisons", "stack-3")
    yield code('''
        import numpy as np

        print(round(1 - 0.95 ** 20, 3))                    # 0.642 ← P(at least one false positive) in 20 tests at α = 0.05

        p = np.array([0.001, 0.008, 0.012, 0.04, 0.2])     # p-values from 5 tests
        print((p <= 0.05 / len(p)).tolist())               # [True, True, False, False, False] ← Bonferroni: α / m
        m = len(p)                                         # Benjamini–Hochberg (controls the false discovery rate)
        order = np.argsort(p)
        passed = p[order] <= 0.05 * np.arange(1, m + 1) / m
        k = passed.nonzero()[0].max() + 1 if passed.any() else 0
        print(sorted(order[:k].tolist()))                  # [0, 1, 2, 3] ← indices of discoveries
    ''')
    yield warn("Testing many metrics, segments or model variants and reporting only the significant ones (**p-hacking**) guarantees false discoveries. Pre-register the primary metric, correct for multiple tests, and confirm surprises on fresh data.")
    yield qa("What is a p-value?",
             "The probability of observing data at least as extreme as what we saw, assuming the null hypothesis is true. A small p-value means the data would be surprising under H₀. It is not the probability that H₀ is true, and it says nothing about how big or important the effect is.")
    yield qa("What are Type I and Type II errors?",
             "Type I: rejecting a true null (false positive), controlled by α. Type II: failing to reject a false null (false negative), probability β; power = 1 − β grows with sample size and effect size.")
    yield qa("How do you know if a new model is significantly better than the old one?",
             "Evaluate both on the same held-out data and use a paired method: McNemar's test on disagreements for accuracy, or a bootstrap confidence interval of the metric difference. Make sure the difference is also practically meaningful and confirm with an online A/B test if the model affects users.")


@topic(G, "ab-testing", "A/B Testing", "arrows-split")
def _():
    yield lead("Offline metrics say a model *should* help; an A/B test measures whether it *does*. Users are randomly split between the current system (A, control) and the new one (B, treatment), and a pre-chosen metric is compared.")
    yield steps(
        ("Hypothesis & metric", "One primary metric (conversion, revenue per user), plus guardrail metrics that must not get worse (latency, complaints)."),
        ("Randomisation unit", "Usually the user (not the page view), so one person sees one variant consistently."),
        ("Sample size", "Power analysis from the baseline rate, the minimum detectable effect (MDE), α and power."),
        ("Run", "For the planned duration — whole weeks to cover weekly cycles — without stopping early on a good-looking day."),
        ("Check sanity", "Sample-ratio mismatch (did the 50/50 split really come out 50/50?), logging, novelty effects."),
        ("Analyse & decide", "Effect size with a confidence interval, not just a p-value; ship, iterate or roll back."),
    )
    yield section("How many users?", "users")
    yield formula("n per group ≈ (z₁₋α/₂ + z₁₋β)² · [p₁(1 − p₁) + p₂(1 − p₂)] / (p₁ − p₂)²")
    yield code('''
        from scipy.stats import norm

        p1, p2 = 0.10, 0.11                                   # baseline 10%, want to detect +1 point
        alpha, power = 0.05, 0.80
        z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
        n = z ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p1 - p2) ** 2
        print(round(norm.ppf(1 - alpha / 2), 3), round(norm.ppf(power), 3))   # 1.96 0.842
        print(round(n))                                       # 14748 ← users per group
    ''')
    yield p("Halving the detectable effect quadruples the required sample (n ∝ 1/Δ²). Small effects on rare events need a lot of traffic.")
    yield section("Analysing a conversion test", "chart-bar")
    yield code('''
        import numpy as np
        from scipy.stats import norm

        conv_a, n_a = 1200, 10000
        conv_b, n_b = 1290, 10000
        pa, pb = conv_a / n_a, conv_b / n_b

        pooled = (conv_a + conv_b) / (n_a + n_b)                       # under H0 both rates are equal
        se0 = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
        z = (pb - pa) / se0
        p_value = 2 * (1 - norm.cdf(abs(z)))
        print(round(pb - pa, 4), round(z, 3), round(p_value, 4))       # 0.009 1.928 0.0539

        se = np.sqrt(pa * (1 - pa) / n_a + pb * (1 - pb) / n_b)       # unpooled SE for the interval
        print([round(float(pb - pa - 1.96 * se), 4), round(float(pb - pa + 1.96 * se), 4)])   # [-0.0002, 0.0182] ← 95% CI of the lift
    ''')
    yield p("Here p ≈ 0.05 and the interval barely touches 0: the lift is plausible but uncertain — a case for the pre-planned sample size, not for declaring victory.")
    yield section("Why you must not peek", "eye-off")
    yield p("Checking the p-value every day and stopping at the first p < 0.05 inflates the false-positive rate far above 5%. Simulated A/A tests (no real difference) checked 20 times each:")
    yield code('''
        import numpy as np
        from scipy.stats import norm

        rng = np.random.default_rng(0)
        sims, looks, batch, p = 2000, 20, 500, 0.10
        a = rng.binomial(batch, p, size=(sims, looks)).cumsum(axis=1)     # both arms identical
        b = rng.binomial(batch, p, size=(sims, looks)).cumsum(axis=1)
        n = batch * np.arange(1, looks + 1)
        pooled = (a + b) / (2 * n)
        z = (b - a) / n / np.sqrt(pooled * (1 - pooled) * 2 / n)
        significant = np.abs(z) > norm.ppf(0.975)

        print(round(significant[:, -1].mean(), 3))        # 0.048 ← analyse once at the end: ≈ 5% false positives
        print(round(significant.any(axis=1).mean(), 3))   # 0.241 ← stop at the first significant peek: far above 5%
    ''')
    yield p("If you need to monitor continuously, use a method designed for it: sequential tests with alpha spending, always-valid p-values, or Bayesian decision rules with a pre-set stopping criterion.")
    yield section("Common pitfalls", "alert-triangle")
    yield table(
        ["Pitfall", "What goes wrong", "Remedy"],
        ["Sample-ratio mismatch", "Assignment or logging bug biases the groups", "Chi-square test on group sizes before analysing"],
        ["Novelty / primacy effects", "Users react to *change*, not to quality", "Run longer; look at the effect over time"],
        ["Interference / network effects", "Treated users affect control users (marketplaces, social)", "Cluster or switchback randomisation"],
        ["Many metrics & segments", "Some will be “significant” by chance", "One primary metric; correct for multiple tests"],
        ["Unit mismatch", "Randomise by user but analyse per page view → underestimated variance", "Analyse at the randomisation unit (or use the delta method)"],
        ["Seasonality", "A holiday week isn't typical", "Whole weeks; avoid unusual periods"],
    )
    yield p("Offline evaluation is still the first filter: A/B tests are slow and expensive. Interleaving (for rankers) and multi-armed bandits (which shift traffic toward the better variant while learning) are common complements.")
    yield qa("How would you A/B test a new recommendation model?",
             "Randomise users 50/50 into the current and the new model; choose one primary metric (e.g. watch time or purchases per user) and guardrails (latency, diversity, complaints); size the test with a power analysis for the smallest lift worth shipping; run whole weeks; check sample-ratio mismatch; then report the lift with a confidence interval and decide.")
    yield qa("Why is peeking at A/B test results a problem?",
             "Each look is another chance for noise to cross the significance threshold. Stopping at the first significant look turns a 5% false-positive rate into something like 20–30% with many looks. Fix the sample size in advance, or use sequential methods built for continuous monitoring.")
    yield qa("The test shows p = 0.03 but a +0.1% lift. Ship it?",
             "Statistically significant isn't necessarily meaningful. Compare the lift and its confidence interval with the cost of shipping and maintaining the change, check guardrails and segment consistency, and consider whether it was the pre-registered primary metric.")
