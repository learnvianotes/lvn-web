from kit import *

G = "Interview Prep"


@topic(G, "interview-questions", "Interview Questions", "message-question")
def _():
    yield lead("Data science questions that come up in placements and interviews — short answers you can say out loud.")
    yield section("Python & data handling", "brand-python")
    yield qa("What's the difference between a Python list and a NumPy array?",
             "A list holds any objects and grows easily, but maths needs a loop. A NumPy array holds one type in contiguous memory, so operations are **vectorised** — `arr * 2` multiplies every element in C, far faster. Arrays also support multi-dimensional shapes, axes and broadcasting.")
    yield qa("What does axis=0 vs axis=1 mean?",
             "`axis=0` works down the rows — one result per **column**. `axis=1` works across the columns — one result per **row**. For a (rows, cols) array, `sum(axis=0)` has one value per column.")
    yield qa("Series vs DataFrame?",
             "A Series is one labelled column (values + index). A DataFrame is a table of Series sharing the same index — rows and named columns.")
    yield qa("loc vs iloc?",
             "`loc` selects by **labels** (index values and column names; slices include the end). `iloc` selects by integer **position** (slices exclude the end).")
    yield qa("How do you handle missing values?",
             "First measure them (`df.isna().sum()`). Then per column: drop rows (`dropna`), fill with a constant or the mean/median/mode (`fillna`), or model them; sometimes add a “was missing” flag. The choice depends on how much is missing and why.")
    yield section("Machine learning", "brain")
    yield qa("Supervised vs unsupervised learning?",
             "Supervised learning uses labelled examples to predict a target — classification (categories) or regression (numbers). Unsupervised learning finds structure without labels — clustering (K-Means) or dimensionality reduction (PCA).")
    yield qa("Why do we split data into train and test sets?",
             "To measure performance on data the model hasn't seen. A score on training data rewards memorisation; the test score estimates real-world performance. Cross-validation repeats the split several times for a more reliable estimate.")
    yield qa("What are overfitting and underfitting?",
             "Overfitting: great on training data, poor on test data — the model learned noise (fix: simpler model, regularisation, more data, limit tree depth). Underfitting: poor on both — the model is too simple (fix: more features, a more flexible model).")
    yield qa("Precision vs recall?",
             "Precision: of everything predicted positive, how much really is positive. Recall: of all real positives, how many were found. Spam filters favour precision (don't lose real mail); disease screening favours recall (don't miss a case). F1 balances both.")
    yield qa("Decision tree vs random forest?",
             "A single tree is easy to read but overfits easily. A random forest trains many trees on random samples of rows and features and lets them vote — more accurate and stable, less interpretable, with feature importances as a summary.")
    yield qa("How does K-Means work, and how do you choose K?",
             "Pick K centroids, assign each point to the nearest, move each centroid to the mean of its points, repeat until stable. Choose K with the elbow method (plot within-cluster sum of squares against K) or the silhouette score.")
    yield qa("Why is Naive Bayes “naive”?",
             "It assumes features (e.g. words) are independent given the class. That's rarely true, but the model is fast, needs little data and works surprisingly well for text classification.")
    yield section("Text & scraping", "world-www")
    yield qa("Stemming vs lemmatization?",
             "Stemming chops suffixes by rules and may produce non-words (`changes` → `chang`). Lemmatization uses a dictionary and part of speech to return the real base form (`changed` → `change`, `better` → `good`). Lemmatization is more accurate, stemming faster.")
    yield qa("What are stop words, and when should you keep them?",
             "Very common words (“the”, “is”) removed to focus on meaningful words. Keep them when they matter — negations like “not” in sentiment analysis, or for models that read full sentences.")
    yield qa("How do you turn text into numbers for a model?",
             "Tokenize, build a vocabulary, then encode: word IDs, bag-of-words counts (`CountVectorizer`), TF-IDF weights, or dense embeddings (Word2Vec, transformer models).")
    yield qa("requests + BeautifulSoup vs Selenium — when do you need Selenium?",
             "requests fetches the HTML the server sends; BeautifulSoup parses it — fast and light. If content is created by JavaScript after the page loads (infinite scroll, clicks, logins), `requests` sees an empty shell; Selenium drives a real browser so you get what users see.")
    yield section("Quick-fire checklist", "checklist")
    yield chips(
        "File modes r/w/a", "os.walk", "ndarray vs list", "Broadcasting", "axis", "loc vs iloc", "Missing values",
        "groupby", "BeautifulSoup find/find_all", "Selenium waits", "Train/test split", "Overfitting",
        "Precision & recall", "Random forest", "K-Means & elbow", "Naive Bayes", "Tokenization", "Lemmatization",
        "Stop words", "Regex", "TF-IDF & embeddings",
    )
