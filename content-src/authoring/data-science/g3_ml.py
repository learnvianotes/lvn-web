from kit import *

G = "Machine Learning"


@topic(G, "ml-workflow", "The scikit-learn Workflow", "route")
def _():
    yield lead("Every scikit-learn model follows the same few steps — so once you know one, you know them all.")
    yield steps(
        ("Load data", "Features `X` (a 2-D table: rows = samples, columns = features) and target `y` (what to predict)."),
        ("Split", "`train_test_split` holds back unseen data to measure honestly."),
        ("Create & fit", "`model = SomeModel(...)` then `model.fit(X_train, y_train)` learns from the training set."),
        ("Predict", "`model.predict(X_test)` on data it has never seen."),
        ("Evaluate", "Compare predictions with the truth: `accuracy_score`, `classification_report`, `mean_squared_error`…"),
    )
    yield code('''
        from sklearn.datasets import load_iris
        from sklearn.model_selection import train_test_split
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.metrics import accuracy_score

        X, y = load_iris(return_X_y=True)                        # 150 flowers, 4 measurements, 3 species
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        print(X.shape, X_train.shape, X_test.shape)              # (150, 4) (105, 4) (45, 4)

        model = KNeighborsClassifier(n_neighbors=5)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(round(accuracy_score(y_test, y_pred), 2))          # 0.98
    ''')
    yield cards(
        ("Supervised", "Learns from labelled examples: **classification** (a category — spam / not spam) or **regression** (a number — price).", "school"),
        ("Unsupervised", "Finds structure in unlabelled data: **clustering** (K-Means), dimensionality reduction (PCA).", "chart-dots"),
    )
    yield section("Why split the data?", "arrows-split")
    yield p("A model scored on the data it trained on can simply memorise it. Testing on held-out data shows how it will do on new, real inputs. `random_state` fixes the shuffle so results are reproducible.")
    yield warn("**Overfitting** = great on training data, poor on test data (the model memorised noise). **Underfitting** = poor on both (the model is too simple). Compare train vs test scores to tell them apart.")
    yield table(
        ["Metric", "For", "Meaning"],
        ["Accuracy", "Classification", "Share of correct predictions — misleading when classes are imbalanced"],
        ["Precision", "Classification", "Of those predicted positive, how many really are"],
        ["Recall", "Classification", "Of the real positives, how many were found"],
        ["F1-score", "Classification", "Balance of precision and recall"],
        ["MSE / RMSE, R²", "Regression", "Average squared error / share of variance explained"],
    )


@topic(G, "regression", "Polynomial Regression", "chart-line")
def _():
    yield lead("Linear regression fits a straight line. When the relationship curves, add powers of the input (x², x³…) as extra features — the model stays linear in its coefficients, but the fitted curve bends.")
    yield define("Polynomial features", "turning `[x]` into `[1, x, x²]` (degree 2). `PolynomialFeatures` does this; `LinearRegression` then fits `y ≈ b₀ + b₁x + b₂x²`.")
    yield code('''
        import numpy as np
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression

        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([3, 8, 9, 70, 80])

        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        print(X_poly[1])                                  # [1. 2. 4.]   ← 1, x, x² for x = 2

        model = LinearRegression().fit(X_poly, y)
        print(model.predict(poly.transform([[6]])).round(1))   # [133.8]
        print(round(model.score(X_poly, y), 3))           # 0.884
    ''')
    yield section("Cleaner with a pipeline", "git-merge")
    yield code('''
        import numpy as np
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression

        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([3, 8, 9, 70, 80])
        model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
        model.fit(X, y)                                   # transform + fit in one step
        print(model.predict([[6]]).round(1))              # [133.8]
    ''')
    yield section("Plotting the fit", "chart-line")
    yield code('''
        import numpy as np
        import matplotlib.pyplot as plt
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression

        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([3, 8, 9, 70, 80])
        model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression()).fit(X, y)

        X_range = np.linspace(0, 6, 100).reshape(-1, 1)   # 100 points to draw a smooth curve
        plt.scatter(X, y, label="Data points")
        plt.plot(X_range, model.predict(X_range), color="red", label="Polynomial fit")
        plt.xlabel("X"); plt.ylabel("y"); plt.legend()
        plt.show()
    ''', check=False)
    yield warn("Higher degree isn't better: with 5 points, degree 4 passes through every point exactly and predicts nonsense between and beyond them. Choose the degree by testing on held-out data.")


@topic(G, "classification", "SVM, Decision Trees & Random Forests", "binary-tree")
def _():
    yield lead("Three classic classifiers on the Iris dataset (150 flowers, 4 measurements, 3 species) — how they decide, and what each is good at.")
    yield section("Support Vector Machine (SVM)", "separator")
    yield define("SVM", "finds the boundary that separates the classes with the **widest margin**. With a kernel such as `rbf`, the boundary can curve.")
    yield code('''
        from sklearn import datasets
        from sklearn.model_selection import train_test_split
        from sklearn.svm import SVC
        from sklearn.metrics import accuracy_score

        iris = datasets.load_iris()
        X = iris.data[:, :2]              # only 2 features (sepal length & width) so it can be plotted in 2-D
        y = iris.target
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

        model = SVC(kernel="rbf", C=1.0, gamma="auto").fit(X_train, y_train)
        print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")   # Accuracy: 0.80
    ''')
    yield table(
        ["Parameter", "Effect"],
        ["`kernel`", "`linear` (straight boundary), `rbf` (curved), `poly`"],
        ["`C`", "Low = wider margin, tolerates mistakes; high = fits training data tightly (risk of overfitting)"],
        ["`gamma`", "For `rbf`: how far one sample's influence reaches — high gamma makes wiggly boundaries"],
    )
    yield note("Using only two features caps the accuracy (0.80). Features matter more than the algorithm — the trees below use all four and score 0.98.")
    yield section("Decision Tree", "binary-tree-2")
    yield define("Decision tree", "a flowchart of yes/no questions on the features (“petal length ≤ 2.45?”). Each split is chosen to make the groups as pure as possible, measured by **Gini impurity** or **entropy**.")
    yield code('''
        from sklearn.datasets import load_iris
        from sklearn.model_selection import train_test_split
        from sklearn.tree import DecisionTreeClassifier, export_text
        from sklearn.metrics import accuracy_score

        iris = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.3, random_state=0)
        model = DecisionTreeClassifier(criterion="entropy", max_depth=3, random_state=0).fit(X_train, y_train)
        print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")   # Accuracy: 0.98
        print(export_text(model, feature_names=iris.feature_names).splitlines()[0])   # |--- petal width (cm) <= 0.75
    ''')
    yield note("`max_depth` limits how many questions deep the tree can go — the main defence against a tree memorising the training data. Draw it with `sklearn.tree.plot_tree(model, filled=True)`.")
    yield section("Random Forest", "trees")
    yield define("Random forest", "many decision trees, each trained on a random sample of rows and features; they **vote**. Averaging many noisy trees gives a stronger, more stable model (an *ensemble*).")
    yield code('''
        from sklearn.datasets import load_iris
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score

        iris = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.3, random_state=0)
        model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=0).fit(X_train, y_train)
        print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")   # Accuracy: 0.98

        ranked = sorted(zip(model.feature_importances_, iris.feature_names), reverse=True)
        print([name for _, name in ranked[:2]])          # ['petal length (cm)', 'petal width (cm)']
    ''')
    yield table(
        ["", "SVM", "Decision tree", "Random forest"],
        ["Idea", "Widest-margin boundary", "Sequence of feature questions", "Many trees voting"],
        ["Interpretable", "Low", "**High** (you can read the tree)", "Medium (feature importances)"],
        ["Scaling features", "**Needed**", "Not needed", "Not needed"],
        ["Overfitting risk", "Tune `C`, `gamma`", "High — limit depth", "Low"],
    )


@topic(G, "naive-bayes", "Text Classification with Naive Bayes", "message")
def _():
    yield lead("Classify documents by their words: turn each text into word counts, then let Naive Bayes estimate which class makes those words most likely.")
    yield steps(
        ("Vectorise", "`CountVectorizer` builds a vocabulary and turns each document into a vector of word counts (bag of words)."),
        ("Train", "`MultinomialNB` learns how often each word appears in each class."),
        ("Predict", "For a new text it picks the class with the highest probability, assuming words are independent — the “naive” part."),
    )
    yield code('''
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB

        texts = ["the team won the cricket match", "stocks fell as markets closed lower",
                 "a great goal in the final", "the bank raised interest rates",
                 "fans cheered the winning shot", "investors sold shares today"]
        labels = ["sports", "finance", "sports", "finance", "sports", "finance"]

        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(texts)          # sparse matrix: 6 documents × vocabulary
        print(X.shape)                               # (6, 27)

        model = MultinomialNB().fit(X, labels)
        new = vectorizer.transform(["the match was a great win", "interest rates and shares"])
        print(model.predict(new).tolist())           # ['sports', 'finance']
    ''')
    yield warn("Call `fit_transform` on training text only, then `transform` on new text — otherwise the vocabulary (and the columns) change between training and prediction.")
    yield section("The notebook's real dataset", "database")
    yield code('''
        from sklearn.datasets import fetch_20newsgroups
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.model_selection import train_test_split
        from sklearn import metrics

        data = fetch_20newsgroups(subset="all")                  # ~18,800 posts in 20 topics (downloads once)
        X = CountVectorizer().fit_transform(data.data)
        X_train, X_test, y_train, y_test = train_test_split(X, data.target, test_size=0.3, random_state=0)
        model = MultinomialNB().fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print(f"Accuracy: {metrics.accuracy_score(y_test, y_pred):.2f}")   # 0.85 in the notebook run
        print(metrics.classification_report(y_test, y_pred, target_names=data.target_names))
    ''', run=False)
    yield note("The report shows per-class precision and recall. In the notebook, `comp.os.ms-windows.misc` had precision 0.97 but recall 0.25 — the model was rarely wrong when it chose that class, but missed most of its posts. Accuracy alone would hide that.")
    yield cards(
        ("Why Naive Bayes for text", "Fast, works with little data, handles huge vocabularies — a strong baseline for spam filters and topic tagging.", "bolt"),
        ("Improving it", "`TfidfVectorizer` (down-weights common words), removing stop words, bigrams (`ngram_range=(1, 2)`).", "adjustments"),
    )


@topic(G, "clustering", "K-Means Clustering", "chart-dots")
def _():
    yield lead("K-Means groups unlabelled points into K clusters around centres (centroids). The elbow method helps choose K.")
    yield steps(
        ("Start", "Pick K initial centroids (`k-means++` spreads them out smartly)."),
        ("Assign", "Each point joins its nearest centroid."),
        ("Update", "Each centroid moves to the mean of its points."),
        ("Repeat", "Until assignments stop changing (or `max_iter`)."),
    )
    yield code('''
        from collections import Counter
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_blobs

        X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)
        km = KMeans(n_clusters=4, init="k-means++", n_init=10, random_state=0).fit(X)
        print(km.cluster_centers_.shape)          # (4, 2)
        print(sorted(Counter(km.labels_).values()))   # [75, 75, 75, 75]   ← 4 equal clusters
    ''')
    yield section("Choosing K: the elbow method", "chart-line")
    yield p("Run K-Means for K = 1…10 and record the **WCSS** (within-cluster sum of squares, `inertia_`). It always falls as K grows; the “elbow” where it stops falling sharply is a good K.")
    yield code('''
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_blobs

        X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)
        wcss = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(X).inertia_ for k in range(1, 11)]
        drops = [round(wcss[i] - wcss[i + 1]) for i in range(5)]
        print(drops)       # [1621, 644, 335, 23, 18]   ← big drops until K = 4, then small ones
    ''')
    yield code('''
        import matplotlib.pyplot as plt
        plt.plot(range(1, 11), wcss, marker="o")
        plt.xlabel("Number of clusters (K)"); plt.ylabel("WCSS"); plt.title("Elbow Method")
        plt.show()
    ''', run=False)
    yield section("The same with SciPy", "math")
    yield code('''
        import numpy as np
        from scipy.cluster.vq import kmeans, vq
        from sklearn.datasets import make_blobs

        X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)
        centroids, _ = kmeans(X, 4, seed=0)       # centroids
        labels, _ = vq(X, centroids)              # nearest centroid for each point
        print(centroids.shape, len(np.unique(labels)))   # (4, 2) 4
    ''')
    yield warn("K-Means assumes round, similar-sized clusters and is sensitive to feature scales — standardise features first (`StandardScaler`). For odd shapes, try DBSCAN.")
