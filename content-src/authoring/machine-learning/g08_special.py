from kit import *
from mlkit import code_out

G = "Time Series & Recommenders"


@topic(G, "time-series", "Time-Series Basics", "timeline")
def _():
    yield lead("A time series is a sequence of observations in time order — sales per day, CPU load per minute. Order matters: neighbouring values are correlated, the future must never leak into the past, and a simple “same as last week” baseline is surprisingly hard to beat.")
    yield table(
        ["Component", "Meaning", "Example"],
        ["Trend", "Long-term increase or decrease", "Growing user base"],
        ["Seasonality", "Repeating pattern with a fixed period", "Weekly shopping cycle, yearly peaks"],
        ["Cycles", "Rises and falls without a fixed period", "Business cycles"],
        ["Noise", "Irregular variation", "Random day-to-day fluctuation"],
    )
    yield define("Stationarity", "a series whose statistical properties (mean, variance, autocorrelation) don't change over time. Classical models like ARIMA assume it; trends and seasonality are removed first, e.g. by **differencing** (`y_t − y_{t−1}`, or `y_t − y_{t−7}` for weekly seasonality).")
    yield section("A forecasting example", "chart-line")
    yield p("Daily demand with a trend, a weekly pattern and noise. Forecast the last 28 days using only information available the day before:")
    yield code('''
        import numpy as np
        import pandas as pd
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_absolute_error

        rng = np.random.default_rng(0)
        days = pd.date_range("2024-01-01", periods=364, freq="D")
        t = np.arange(364)
        weekly = np.array([0, 2, 3, 3, 5, 12, 9])[days.dayofweek]          # busier on weekends
        y = pd.Series(50 + 0.05 * t + weekly + rng.normal(0, 2, 364), index=days)

        print(round(y.autocorr(lag=1), 2), round(y.autocorr(lag=7), 2))     # 0.68 0.91 ← strong weekly autocorrelation

        df = pd.DataFrame({"y": y})
        df["lag_1"] = y.shift(1)                                  # yesterday
        df["lag_7"] = y.shift(7)                                  # same weekday last week
        df["roll_7"] = y.shift(1).rolling(7).mean()               # past week's mean — shift FIRST, then roll
        df["dow"] = df.index.dayofweek
        df = pd.get_dummies(df, columns=["dow"], dtype=float).dropna()

        train, test = df.iloc[:-28], df.iloc[-28:]                 # split by time, never shuffle
        X_cols = [c for c in df.columns if c != "y"]
        model = Ridge(alpha=1.0).fit(train[X_cols], train["y"])

        print(round(mean_absolute_error(test["y"], test["lag_1"]), 2))                 # 5.18 ← naive: tomorrow = today
        print(round(mean_absolute_error(test["y"], test["lag_7"]), 2))                 # 2.51 ← seasonal naive: = last week
        print(round(mean_absolute_error(test["y"], model.predict(test[X_cols])), 2))   # 1.99 ← model with lag + calendar features
    ''')
    yield warn("`y.rolling(7).mean()` without the `shift(1)` includes today's value — the very thing you are predicting. Build every lag/rolling/aggregate feature from data strictly before the prediction time, and validate with `TimeSeriesSplit` or a hold-out of the latest period.")
    yield section("Approaches", "list-details")
    yield table(
        ["Family", "Examples", "Good for"],
        ["Baselines", "Naive, seasonal naive, moving average", "Always — the bar to beat"],
        ["Classical statistical", "Exponential smoothing (ETS, Holt-Winters), ARIMA/SARIMA (`statsmodels`)", "Single series, clear trend/seasonality, small data, prediction intervals"],
        ["ML on engineered features", "Lags, rolling stats, calendar and holiday features + gradient boosting / linear models", "Many related series, external drivers (price, promotions, weather)"],
        ["Deep learning", "RNN/LSTM, temporal CNNs, transformers (see **Deep Learning**)", "Very many long series, complex patterns"],
    )
    yield section("Practical points", "notes")
    yield ul(
        "**Multi-step horizons**: recursive (feed predictions back as lags) accumulates errors; direct (one model per horizon) avoids that at more cost.",
        "**Metrics**: MAE/RMSE per horizon; MASE = MAE ÷ MAE of the seasonal-naive forecast (below 1 beats the baseline); avoid MAPE with values near 0.",
        "**Validation**: rolling-origin (expanding window) evaluation mirrors how forecasts are produced in production.",
        "**Label availability**: if yesterday's sales are only final two days later, `lag_1` isn't available at prediction time — use a gap.",
        "Report **prediction intervals**, not only point forecasts — inventory and staffing decisions depend on the uncertainty.",
    )
    yield qa("How is validating a time-series model different?",
             "The split must respect time: train on the past, validate on the following period (walk-forward / `TimeSeriesSplit`), never shuffle, and make sure every feature uses only information available at the forecast origin. Random K-fold leaks the future and gives optimistic errors.")
    yield qa("What is stationarity and why does it matter?",
             "Constant mean, variance and autocorrelation over time. ARIMA-type models assume it, and non-stationary series produce spurious correlations. Detrend or difference the series (and test with ADF/KPSS) before fitting such models; tree models on lag features are more forgiving but still can't extrapolate a trend.")
    yield qa("What baseline would you use for a forecasting problem?",
             "The naive forecast (last value) and the seasonal naive forecast (value one season ago, e.g. same weekday last week). Many sophisticated models fail to beat them; MASE expresses error relative to that baseline.")


@topic(G, "recommender-systems", "Recommender Systems", "thumb-up")
def _():
    yield lead("Recommenders predict which items a user will like from past interactions (ratings, clicks, purchases, watch time) and item information. The core families are content-based filtering, collaborative filtering and matrix factorisation — usually combined.")
    yield table(
        ["Approach", "Idea", "Strength", "Weakness"],
        ["Popularity", "Recommend what's popular (per segment)", "Strong baseline, no cold start for users", "Not personal; reinforces popularity"],
        ["Content-based", "Items similar to what the user liked, using item features (text, genre, tags)", "Works for new items; explainable", "Over-specialised; needs good item features"],
        ["Collaborative filtering (neighbourhood)", "Users who agreed before will agree again / items liked by the same users are similar", "No item features needed; finds surprising items", "Cold start for new users and items; sparse data"],
        ["Matrix factorisation", "Learn a latent vector per user and per item; score = their dot product", "Scales, captures hidden tastes", "Cold start; less explainable"],
        ["Hybrid / two-stage", "Candidate generation (fast retrieval of hundreds of items) → ranking model with rich features", "Industry standard at scale", "More components to build and monitor"],
    )
    yield section("Content-based: similar items", "file-text")
    yield code('''
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        titles = ["space adventure alien war", "romantic comedy wedding", "alien invasion space thriller",
                  "wedding drama romance", "robot space exploration"]
        tfidf = TfidfVectorizer().fit_transform(titles)
        sim = cosine_similarity(tfidf)

        liked = 0                                                # the user liked "space adventure alien war"
        ranked = [int(i) for i in np.argsort(sim[liked])[::-1] if i != liked]
        print(ranked[:2])                                        # [2, 4] ← the other space/alien films
        print(sim[liked].round(2).tolist())                      # [1.0, 0.0, 0.35, 0.0, 0.16]
    ''')
    yield section("Collaborative filtering: item–item similarity", "users")
    yield code('''
        import numpy as np

        # ratings: rows = users, columns = items A..E; 0 = not rated
        R = np.array([[5, 4, 0, 1, 0],
                      [4, 5, 1, 0, 1],
                      [1, 0, 5, 4, 5],
                      [0, 1, 4, 5, 4],
                      [5, 5, 0, 0, 1]], dtype=float)

        norms = np.linalg.norm(R, axis=0)
        item_sim = (R.T @ R) / np.outer(norms, norms)            # cosine similarity between item columns
        print(item_sim[0].round(2).tolist())                     # [1.0, 0.97, 0.17, 0.17, 0.26] ← item A is most like item B

        user, item = 0, 2                                         # predict user 0's rating of item C
        rated = R[user] > 0
        w = item_sim[item, rated]
        print(round(float(w @ R[user, rated] / w.sum()), 2))     # 1.92 ← similarity-weighted average of their ratings
    ''')
    yield section("Matrix factorisation", "grid-4x4")
    yield formula("r̂ᵤᵢ = pᵤ · qᵢ        minimise  Σ_(u,i observed) (rᵤᵢ − pᵤ·qᵢ)² + λ(‖pᵤ‖² + ‖qᵢ‖²)")
    yield p("Each user and item gets a vector of `k` latent factors (think “how much action / romance”). Only **observed** ratings enter the loss — treating missing ratings as 0 (plain SVD) would teach the model that unseen means disliked. Alternating least squares (ALS) fixes the items and solves a small ridge regression per user, then swaps:")
    yield code('''
        import numpy as np

        R = np.array([[5, 4, 0, 1, 0],
                      [4, 5, 1, 0, 1],
                      [1, 0, 5, 4, 5],
                      [0, 1, 4, 5, 4],
                      [5, 5, 0, 0, 1]], dtype=float)
        observed = R > 0
        k, lam = 2, 0.1
        rng = np.random.default_rng(0)
        P = rng.normal(0, 0.1, (5, k))                            # user factors
        Q = rng.normal(0, 0.1, (5, k))                            # item factors

        for _ in range(50):                                       # alternating least squares
            for u in range(5):
                Qo = Q[observed[u]]
                P[u] = np.linalg.solve(Qo.T @ Qo + lam * np.eye(k), Qo.T @ R[u, observed[u]])
            for i in range(5):
                Po = P[observed[:, i]]
                Q[i] = np.linalg.solve(Po.T @ Po + lam * np.eye(k), Po.T @ R[observed[:, i], i])

        pred = P @ Q.T
        print(round(float(np.sqrt(np.mean((pred - R)[observed] ** 2))), 3))   # 0.345 ← training RMSE on observed ratings
        print(np.clip(pred[0], 1, 5).round(1).tolist())         # [4.4, 4.5, 1.0, 1.1, 1.0] ← user 0, clipped to the 1–5 scale: C and E filled in
    ''')
    yield p("User 0 loves A and B and dislikes D; the factors place C and E with D, so both get low predicted ratings — the recommender won't suggest them. (Raw dot products can leave the rating scale, hence the clipping; real systems also add a global mean plus user and item **bias** terms: `r̂ = μ + bᵤ + bᵢ + pᵤ·qᵢ`.)")
    yield section("Evaluating recommendations", "list-numbers")
    yield table(
        ["Metric", "Meaning"],
        ["Precision@k / Recall@k", "Share of the top-k that are relevant / share of relevant items that appear in the top-k"],
        ["Hit rate@k", "Did at least one relevant item appear in the top-k?"],
        ["MRR", "Mean of 1 / rank of the first relevant item"],
        ["NDCG@k", "Rewards relevant items near the top with a log discount, normalised by the ideal ordering"],
        ["Coverage, diversity, novelty", "Is the system recommending more than the same popular items?"],
    )
    yield formula("DCG@k = Σᵢ₌₁ᵏ relᵢ / log₂(i + 1)        NDCG@k = DCG@k / IDCG@k")
    yield code('''
        import numpy as np

        def ndcg_at_k(relevance, k):
            rel = np.asarray(relevance, dtype=float)[:k]
            discounts = 1 / np.log2(np.arange(2, len(rel) + 2))
            ideal = np.sort(np.asarray(relevance, dtype=float))[::-1][:k]
            return float(rel @ discounts / (ideal @ discounts))

        print(round(ndcg_at_k([3, 2, 0, 1], 4), 3))    # 0.985 ← good items near the top
        print(round(ndcg_at_k([0, 1, 2, 3], 4), 3))    # 0.614 ← same items, worst order
    ''')
    yield ul(
        "**Implicit feedback** (clicks, views) is far more plentiful than ratings but has no explicit negatives — unobserved ≠ disliked; sample negatives carefully.",
        "**Cold start**: new users → popularity, onboarding questions, context; new items → content features.",
        "Split **by time** for offline evaluation, and confirm with an online A/B test — offline metrics only partly predict online engagement.",
        "Watch **feedback loops** and popularity bias: the model only learns from what it chose to show.",
    )
    yield qa("Content-based vs collaborative filtering?",
             "Content-based recommends items whose features resemble what the user liked — handles new items, but stays within the user's known tastes. Collaborative filtering uses the behaviour of similar users/items — needs no item features and can surprise, but suffers from cold start and sparsity. Production systems combine them.")
    yield qa("How does matrix factorisation work for recommendations?",
             "It represents each user and item by a low-dimensional latent vector and predicts a rating (or preference) as their dot product, learning the vectors by minimising error on observed interactions plus L2 regularisation, with ALS or SGD. Missing entries are not treated as zeros.")
    yield qa("How do you solve the cold-start problem?",
             "For new users: popularity or trending items, onboarding preferences, context (location, device, time), then quickly adapt to the first interactions. For new items: content features and embeddings, and deliberate exploration (e.g. bandits) to gather interactions.")
