from kit import *
from mlkit import code_out

G = "Unsupervised Learning"


@topic(G, "k-means", "k-Means Clustering", "chart-dots")
def _():
    yield lead("k-means splits the data into `k` groups by placing `k` centroids and assigning every point to the nearest one. It is fast and simple — and it quietly assumes round, similarly sized clusters.")
    yield formula("minimise  inertia = Σₖ Σ_{x ∈ Cₖ} ‖x − μₖ‖²        (within-cluster sum of squared distances)")
    yield steps(
        ("Initialise", "Pick k starting centroids — **k-means++** spreads them out (scikit-learn's default)."),
        ("Assign", "Put each point in the cluster of its nearest centroid."),
        ("Update", "Move each centroid to the mean of its points."),
        ("Repeat", "Until assignments stop changing. Each step lowers inertia, so it converges — but to a **local** minimum."),
    )
    yield p("Because the result depends on the starting centroids, scikit-learn runs several initialisations (`n_init`) and keeps the one with the lowest inertia.")
    yield code('''
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_blobs

        X, y_true = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=0)
        km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X)

        print(km.cluster_centers_.round(2).tolist())        # [[0.85, 4.44], [1.98, 0.83], [-1.44, 7.78], [-1.66, 2.76]]
        print(round(km.inertia_, 1))                         # 369.5
        print(np.bincount(km.labels_).tolist())              # [81, 74, 73, 72] ← cluster sizes
        print(km.predict([[0, 4], [2, 1]]))                  # [0 1] ← new points go to the nearest centroid
    ''')
    yield section("Choosing k", "list-numbers")
    yield p("Inertia always falls as `k` grows (k = n gives 0), so you can't just minimise it. Two common heuristics:")
    yield ul(
        "**Elbow method** — plot inertia against k and look for the bend after which gains flatten.",
        "**Silhouette score** — for each point `s = (b − a) / max(a, b)`, where `a` is its mean distance to its own cluster and `b` to the nearest other cluster. Ranges from −1 to 1; pick the k with the highest average.",
    )
    yield code('''
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_blobs
        from sklearn.metrics import silhouette_score

        X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=0)
        inertia, silhouette = {}, {}
        for k in range(2, 8):
            km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
            inertia[k] = round(km.inertia_)
            silhouette[k] = round(silhouette_score(X, km.labels_), 3)
        print(inertia)       # {2: 1349, 3: 709, 4: 370, 5: 326, 6: 292, 7: 260} ← big drops up to k = 4, small after: the elbow
        print(silhouette)    # {2: 0.496, 3: 0.515, 4: 0.58, 5: 0.503, 6: 0.43, 7: 0.396} ← highest at k = 4
    ''')
    yield note("Let the use case have the final say: five customer segments the marketing team can act on beat seven segments with a marginally better silhouette.")
    yield section("Assumptions and failure modes", "alert-triangle")
    yield table(
        ["k-means assumes…", "So it struggles with…", "Try instead"],
        ["Clusters are roughly spherical (isotropic)", "Elongated or curved clusters (moons, rings)", "Gaussian mixtures, DBSCAN, spectral clustering"],
        ["Clusters have similar size and density", "One big sparse cluster next to a small dense one", "Gaussian mixtures, HDBSCAN"],
        ["Euclidean distance is meaningful", "Unscaled features; categorical data", "Scale first; k-modes / k-prototypes for categories"],
        ["Every point belongs to a cluster", "Outliers dragging centroids", "DBSCAN (labels noise), k-medoids"],
        ["You know k", "Unknown number of groups", "DBSCAN/HDBSCAN, silhouette/BIC to choose"],
    )
    yield code('''
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_moons
        from sklearn.metrics import adjusted_rand_score

        X, y = make_moons(n_samples=300, noise=0.05, random_state=0)      # two curved clusters
        labels = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
        print(round(adjusted_rand_score(y, labels), 2))    # 0.24 ← far from 1: straight boundary cuts both moons
    ''')
    yield ul(
        "**Scale features** first (k-means is distance-based).",
        "`MiniBatchKMeans` handles very large datasets.",
        "Evaluating without labels: silhouette, Davies–Bouldin (lower is better), Calinski–Harabasz (higher is better). With ground truth: adjusted Rand index (ARI), normalised mutual information.",
    )
    yield qa("How does k-means work and what does it optimise?",
             "It alternates between assigning each point to its nearest centroid and moving each centroid to the mean of its assigned points, which monotonically decreases the within-cluster sum of squares. It converges to a local optimum, so it's restarted from several k-means++ initialisations.")
    yield qa("How do you choose k?",
             "Elbow in the inertia curve, the maximum average silhouette score, the gap statistic, or BIC with a Gaussian mixture — combined with whether the clusters are useful and stable for the business question.")
    yield qa("When does k-means fail?",
             "Non-spherical or nested clusters, clusters of very different size or density, unscaled or categorical features, strong outliers, and high dimensions where distances concentrate.")


@topic(G, "clustering-methods", "Hierarchical, DBSCAN & Gaussian Mixtures", "affiliate")
def _():
    yield lead("Beyond k-means: hierarchical clustering builds a tree of merges, DBSCAN finds dense regions of any shape and labels noise, and Gaussian mixtures give soft, elliptical clusters with probabilities.")
    yield section("Hierarchical (agglomerative) clustering", "hierarchy-2")
    yield p("Start with every point as its own cluster and repeatedly merge the two closest clusters until one remains. The merge history is a **dendrogram**; cutting it at a height (or asking for `n_clusters`) gives the clusters.")
    yield table(
        ["Linkage", "Distance between clusters", "Tends to produce"],
        ["Single", "Closest pair of points", "Long chains; finds non-convex shapes but is fooled by bridges of noise"],
        ["Complete", "Farthest pair of points", "Compact clusters of similar diameter"],
        ["Average", "Mean of all pairwise distances", "A compromise"],
        ["Ward", "Increase in total within-cluster variance", "Compact, similar-sized clusters (like k-means) — the default"],
    )
    yield code('''
        import numpy as np
        from scipy.cluster.hierarchy import fcluster, linkage
        from sklearn.cluster import AgglomerativeClustering

        X = np.array([[1.0], [1.2], [1.1], [5.0], [5.3], [9.0]])
        Z = linkage(X, method="ward")                            # merge history
        print(Z[:, 2].round(2).tolist())                         # [0.1, 0.17, 0.3, 4.45, 9.24] ← merge heights: a big jump = natural cut
        print(fcluster(Z, t=3, criterion="maxclust").tolist())   # [1, 1, 1, 2, 2, 3] ← cut into 3 clusters
        print(AgglomerativeClustering(n_clusters=3).fit_predict(X).tolist())   # [1, 1, 1, 0, 0, 2] ← same grouping (ids arbitrary)
    ''')
    yield p("No need to pick k up front and the dendrogram is informative — but the standard algorithm needs O(n²) memory, so it suits thousands of points, not millions.")
    yield section("DBSCAN — density-based clustering", "grain")
    yield p("A point is a **core point** if at least `min_samples` points (itself included) lie within distance `eps`. Clusters are chains of core points plus the **border points** they reach; everything else is **noise** (label `−1`). No `k` needed, any shape works:")
    yield code('''
        import numpy as np
        from sklearn.cluster import DBSCAN, KMeans
        from sklearn.datasets import make_moons
        from sklearn.metrics import adjusted_rand_score

        X, y = make_moons(n_samples=300, noise=0.05, random_state=0)
        X = np.vstack([X, [[2.5, 1.5], [-1.5, -0.8]]])            # two far-away outliers
        y = np.r_[y, -1, -1]

        db = DBSCAN(eps=0.2, min_samples=5).fit(X)
        print(sorted(set(db.labels_.tolist())))                   # [-1, 0, 1] ← two clusters + noise (−1)
        print(np.where(db.labels_ == -1)[0].tolist())             # [300, 301] ← the outliers we added
        km = KMeans(n_clusters=2, n_init=10, random_state=0).fit(X)
        print(round(adjusted_rand_score(y, db.labels_), 2), round(adjusted_rand_score(y, km.labels_), 2))   # 1.0 0.23 ← DBSCAN vs k-means
    ''')
    yield ul(
        "Choosing `eps`: plot each point's distance to its `min_samples`-th nearest neighbour, sorted; pick the knee (the “k-distance plot”).",
        "Struggles when clusters have **very different densities** (one `eps` can't fit all) and in high dimensions. **HDBSCAN** (`sklearn.cluster.HDBSCAN`) handles varying densities and needs only a minimum cluster size.",
        "Scale features first — `eps` is a distance.",
    )
    yield section("Gaussian mixture models", "chart-bell-curve")
    yield formula("p(x) = Σₖ πₖ · N(x | μₖ, Σₖ)        fitted by expectation–maximisation (EM)")
    yield p("A GMM assumes the data comes from `k` Gaussian blobs with their own means, covariances (so **elliptical** shapes and different sizes) and weights. EM alternates between computing each point's membership probabilities (E-step) and re-estimating the blobs from them (M-step). It gives **soft** assignments; k-means is roughly the special case with equal spherical covariances and hard assignments.")
    yield code('''
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_blobs
        from sklearn.metrics import adjusted_rand_score
        from sklearn.mixture import GaussianMixture

        X, y = make_blobs(n_samples=400, centers=3, random_state=170)
        X = X @ np.array([[0.6, -0.6], [-0.4, 0.8]])              # stretch into elongated ellipses

        km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
        gmm = GaussianMixture(n_components=3, covariance_type="full", random_state=0).fit(X)
        print(round(adjusted_rand_score(y, km.labels_), 2), round(adjusted_rand_score(y, gmm.predict(X)), 2))   # 0.55 1.0 ← k-means vs GMM
        print(gmm.predict_proba(X[:2]).round(3).tolist())         # [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]] ← soft memberships
        print([round(GaussianMixture(n_components=k, random_state=0).fit(X).bic(X)) for k in (1, 2, 3, 4, 5)])   # [2858, 2417, 2103, 2474, 2168] ← lowest BIC → 3 components
    ''')
    yield section("Which clustering method?", "table")
    yield table(
        ["Method", "Needs k?", "Cluster shapes", "Noise handling", "Scales to"],
        ["k-means", "Yes", "Spherical, similar size", "None — outliers pull centroids", "Millions (mini-batch)"],
        ["Agglomerative", "No (cut the tree)", "Depends on linkage", "Poor", "Thousands"],
        ["DBSCAN / HDBSCAN", "No", "Arbitrary", "Labels noise points", "Large, low-dimensional data"],
        ["Gaussian mixture", "Yes (choose with BIC)", "Ellipses of any orientation", "Low-probability points can be flagged", "Medium"],
    )
    yield qa("What is the difference between k-means and a Gaussian mixture model?",
             "k-means makes hard assignments and implicitly assumes spherical clusters of equal size. A GMM models each cluster as a Gaussian with its own mean, covariance and weight, gives soft (probabilistic) assignments, and can fit elliptical clusters; it's trained with EM and k can be chosen with BIC.")
    yield qa("When would you use DBSCAN?",
             "When clusters have arbitrary shapes, the number of clusters is unknown, and you want outliers labelled as noise — e.g. GPS points into places. Avoid it when densities vary a lot (use HDBSCAN) or in high dimensions.")
    yield qa("What does the linkage choose in hierarchical clustering?",
             "How the distance between two clusters is measured — closest pair (single), farthest pair (complete), average of all pairs (average) or the increase in within-cluster variance (Ward). It changes the shapes of clusters the method prefers.")


@topic(G, "pca", "PCA & Dimensionality Reduction", "chart-arrows")
def _():
    yield lead("Principal component analysis finds new, uncorrelated axes — the directions along which the data varies most — and lets you keep only the first few. It compresses, denoises and visualises data, but only captures linear structure.")
    yield steps(
        ("Standardise", "Centre every feature (PCA does this) and usually scale to unit variance (you must do this)."),
        ("Covariance", "Compute the covariance matrix of the features."),
        ("Eigen-decompose", "Its eigenvectors are the principal components; each eigenvalue is the variance along that component."),
        ("Project", "Keep the top-k components: `Z = X_centred · W_k`."),
    )
    yield code('''
        import numpy as np
        from sklearn.decomposition import PCA

        rng = np.random.default_rng(0)
        x = rng.normal(size=500)
        X = np.c_[x, 0.5 * x + rng.normal(scale=0.3, size=500)]     # two correlated features

        eigvals, eigvecs = np.linalg.eigh(np.cov(X, rowvar=False))  # by hand
        print((eigvals[::-1] / eigvals.sum()).round(3))             # [0.954 0.046] ← share of variance per component

        pca = PCA().fit(X)
        print(pca.explained_variance_ratio_.round(3))              # [0.954 0.046] ← same
        print(np.abs(pca.components_[0]).round(3))                 # [0.882 0.471] ← PC1 direction (sign is arbitrary)
    ''')
    yield section("Scale first", "ruler-measure")
    yield p("PCA maximises variance, so a feature measured in large units dominates. On the wine data, proline (values in the hundreds to thousands) alone makes up almost all the “variance” until the features are standardised:")
    yield code('''
        from sklearn.datasets import load_wine
        from sklearn.decomposition import PCA
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        X, _ = load_wine(return_X_y=True)
        print(PCA(n_components=3).fit(X).explained_variance_ratio_.round(3))   # [0.998 0.002 0.   ] ← PC1 is just proline
        scaled = make_pipeline(StandardScaler(), PCA(n_components=3)).fit(X)
        print(scaled[-1].explained_variance_ratio_.round(3))                   # [0.362 0.192 0.111] ← real structure
    ''')
    yield section("How many components?", "list-numbers")
    yield code('''
        import numpy as np
        from sklearn.datasets import load_digits
        from sklearn.decomposition import PCA

        X, _ = load_digits(return_X_y=True)                     # 64 pixel features
        cum = np.cumsum(PCA().fit(X).explained_variance_ratio_)
        print(int(np.argmax(cum >= 0.95)) + 1)                  # 29 ← components needed for 95% of the variance

        pca = PCA(n_components=0.95).fit(X)                     # or ask for the fraction directly
        X_back = pca.inverse_transform(pca.transform(X))
        print(pca.n_components_, round(np.mean((X - X_back) ** 2), 2))   # 29 0.85 ← reconstruction error is small
    ''')
    yield p("Common rules: keep enough components for 90–99% of the variance, look for an elbow in the scree plot, or treat k as a hyperparameter and pick it by the downstream model's cross-validated score.")
    yield section("Uses and caveats", "checklist")
    yield table(
        ["Use", "Caveat"],
        ["Visualise high-dimensional data in 2-D/3-D", "Only linear structure; clusters may overlap in a linear projection"],
        ["Compress, denoise, speed up downstream models", "Fit PCA on the training split only (inside the `Pipeline`)"],
        ["Remove multicollinearity (components are uncorrelated)", "Components are mixtures of all features — harder to explain"],
        ["Fight the curse of dimensionality", "PCA ignores the target: a low-variance direction can be the predictive one"],
    )
    yield p("Relatives: `TruncatedSVD` works on sparse matrices (text — “latent semantic analysis”); **LDA** (linear discriminant analysis) is supervised and finds directions that separate classes; `KernelPCA` handles non-linear structure.")
    yield section("t-SNE and UMAP — for looking, not for modelling", "eye")
    yield table(
        ["", "t-SNE", "UMAP"],
        ["Preserves", "Local neighbourhoods", "Local neighbourhoods, somewhat more global structure"],
        ["Key setting", "`perplexity` (~5–50)", "`n_neighbors`, `min_dist`"],
        ["Speed", "Slow on large data", "Faster"],
        ["New points", "No `transform` in scikit-learn — refit", "Can transform new data"],
        ["Where", "`sklearn.manifold.TSNE`", "`umap-learn` package"],
    )
    yield warn("In t-SNE/UMAP plots, cluster **sizes** and the **distances between clusters** are not meaningful, and results change with the random seed and hyperparameters. Use them to explore, not as features or as evidence that clusters exist.")
    yield qa("What does PCA do?",
             "It rotates the (centred) data onto orthogonal axes ordered by how much variance they capture — the eigenvectors of the covariance matrix — and optionally drops the low-variance ones. The result is a lower-dimensional, uncorrelated representation that keeps as much variance as possible.")
    yield qa("Why must you scale data before PCA?",
             "PCA maximises variance, and variance depends on units. Unscaled, the feature with the largest numeric range dominates the first components regardless of how informative it is. Standardising gives every feature an equal starting weight.")
    yield qa("PCA vs t-SNE?",
             "PCA is linear, deterministic, fast, preserves global variance and can project new data — good for preprocessing. t-SNE is non-linear and stochastic, preserves local neighbourhoods for 2-D visualisation, distorts global distances and isn't used to transform new data for models.")


@topic(G, "anomaly-detection", "Anomaly Detection", "zoom-exclamation")
def _():
    yield lead("Anomaly detection finds rows that don't look like the rest — fraud, intrusions, faulty sensors, manufacturing defects. Labels are usually scarce, so most methods learn what *normal* looks like and score deviations from it.")
    yield table(
        ["Kind", "Example"],
        ["Point anomaly", "A $9,000 purchase on a card that averages $40"],
        ["Contextual anomaly", "30 °C is normal in July, anomalous in January"],
        ["Collective anomaly", "A burst of small logins from one IP, each normal on its own"],
    )
    yield section("Approaches", "list-details")
    yield table(
        ["Approach", "Method", "Idea"],
        ["Statistical", "z-score, IQR, robust z-score (median/MAD)", "Far from the centre of one feature's distribution"],
        ["Isolation", "`IsolationForest`", "Random splits isolate anomalies in fewer steps (shorter tree paths)"],
        ["Density / distance", "`LocalOutlierFactor`, k-NN distance", "Much lower local density than the neighbours"],
        ["Boundary", "`OneClassSVM`", "A boundary enclosing the normal data"],
        ["Reconstruction", "PCA, autoencoders", "Normal data compresses well; anomalies reconstruct badly"],
        ["Supervised", "Any classifier with class weights", "When enough labelled anomalies exist — usually the most accurate"],
    )
    yield formula("robust z = 0.6745 · (x − median) / MAD        flag if |robust z| > 3.5        (MAD = median |x − median|)")
    yield code('''
        import numpy as np

        x = np.array([12, 14, 13, 15, 14, 13, 16, 14, 95])
        med = np.median(x)
        mad = np.median(np.abs(x - med))
        robust_z = 0.6745 * (x - med) / mad
        print(med, mad, robust_z.round(1).tolist())   # 14.0 1.0 [-1.3, 0.0, -0.7, 0.7, 0.0, -0.7, 1.3, 0.0, 54.6] ← the 95 stands out; the plain z-score gave only 2.83
    ''')
    yield section("Isolation Forest and LOF", "trees")
    yield code('''
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.metrics import precision_score, recall_score
        from sklearn.neighbors import LocalOutlierFactor

        rng = np.random.default_rng(0)
        normal = rng.normal(0, 1, size=(300, 2))
        anomalies = rng.uniform(-6, 6, size=(15, 2))
        anomalies = anomalies[np.linalg.norm(anomalies, axis=1) > 4]      # keep clearly unusual points
        X = np.vstack([normal, anomalies])
        truth = np.r_[np.zeros(len(normal)), np.ones(len(anomalies))]

        iso = IsolationForest(contamination=0.03, random_state=0).fit(X)
        flag_iso = iso.predict(X) == -1                                    # −1 = anomaly, 1 = normal
        flag_lof = LocalOutlierFactor(n_neighbors=20, contamination=0.03).fit_predict(X) == -1

        print(len(anomalies), int(flag_iso.sum()), int(flag_lof.sum()))    # 11 10 10 ← true anomalies, flagged by each
        print(round(precision_score(truth, flag_iso), 2), round(recall_score(truth, flag_iso), 2))   # 1.0 0.91 ← Isolation Forest
        print(round(precision_score(truth, flag_lof), 2), round(recall_score(truth, flag_lof), 2))   # 0.9 0.82 ← LOF
    ''')
    yield p("`contamination` sets the expected share of anomalies — it only moves the **threshold** on the anomaly score (`score_samples` / `decision_function`). In practice, rank rows by score and review the top k.")
    yield section("Practical notes", "notes")
    yield ul(
        "**Outlier detection** (training data contains anomalies) vs **novelty detection** (train on clean data, score new points — `LocalOutlierFactor(novelty=True)`, `OneClassSVM`).",
        "Evaluate with whatever labels exist: precision@k (analysts review k alerts a day), recall on known incidents, PR-AUC. Accuracy is meaningless when 99.9% of rows are normal.",
        "Scale features for distance-based methods; Isolation Forest doesn't need it.",
        "Once labelled anomalies accumulate, a supervised model (often gradient boosting with class weights) usually beats unsupervised scores — or use the scores as features for it.",
        "Attackers adapt: monitor and retrain (see **Deployment, Monitoring & MLOps**).",
    )
    yield qa("How does Isolation Forest work?",
             "It builds random trees that split on a random feature at a random threshold. Anomalies are few and different, so they are isolated near the root — their average path length across trees is short — while normal points need many splits. The anomaly score is based on that average path length.")
    yield qa("How do you evaluate an anomaly detector without labels?",
             "Get at least a small labelled sample (analyst review of the top-scored and a random set of rows), then measure precision@k and recall. Also check stability of scores over time and use synthetic injected anomalies as a sanity check.")
