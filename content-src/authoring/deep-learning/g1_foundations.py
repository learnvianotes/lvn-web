from kit import *

G = "Foundations"


@topic(G, "what-is-deep-learning", "What Is Deep Learning?", "brain")
def _():
    yield lead("Deep learning is machine learning with **neural networks of many layers** that learn their own features from raw data — pixels, audio samples, characters — instead of relying on hand-crafted ones.")
    yield define("Deep learning", "a family of ML methods that stack many simple, differentiable layers. Each layer transforms its input into a slightly more useful *representation*; the whole stack is trained end-to-end with gradient descent.")
    yield flow("Artificial Intelligence", "Machine Learning", "Neural Networks", "Deep Learning (many layers)")
    yield p("In classic ML (see the **Machine Learning** notes) a person designs the features — word counts, edge histograms, ratios — and a model such as a random forest learns from them. A deep network learns the features too: early layers of an image model detect edges, middle layers textures and parts, late layers whole objects.")
    yield section("Deep learning vs classic ML", "arrows-left-right")
    yield table(
        ["", "Classic ML", "Deep learning"],
        ["Features", "Hand-engineered", "**Learned** from raw data"],
        ["Best on", "Tabular data, small datasets", "Images, audio, text, video — unstructured data"],
        ["Data needed", "Hundreds to thousands of rows", "Usually thousands to billions of examples (or a pretrained model)"],
        ["Compute", "CPU, seconds to minutes", "GPUs/TPUs, minutes to months"],
        ["Interpretability", "Often readable (trees, coefficients)", "Hard — millions of weights"],
        ["Scaling with data", "Plateaus", "Keeps improving with more data and bigger models"],
    )
    yield section("A network is a stack of functions", "stack-2")
    yield p("Each layer is a matrix multiply plus a non-linearity. Stacking them turns a raw input vector into a prediction:")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        x = rng.normal(size=(1, 784))                  # one 28×28 image, flattened
        W1, W2, W3 = rng.normal(size=(784, 128)), rng.normal(size=(128, 64)), rng.normal(size=(64, 10))

        h1 = np.maximum(0, x @ W1)                     # layer 1: 784 → 128 features
        h2 = np.maximum(0, h1 @ W2)                    # layer 2: 128 → 64 features
        logits = h2 @ W3                               # output: 64 → 10 class scores
        print(h1.shape, h2.shape, logits.shape)        # (1, 128) (1, 64) (1, 10)
        print(W1.size + W2.size + W3.size)             # 109184   ← weights to learn (biases left out)
    ''')
    yield section("The training recipe", "route")
    yield p("Every deep learning model — from a 3-layer classifier to a large language model — is trained with the same loop:")
    yield flow("Batch of data", "Forward pass → prediction", "Loss (how wrong?)", "Backprop → gradients", "Optimizer updates weights")
    yield section("Why now?", "rocket")
    yield cards(
        ("Data", "The web, phones and sensors produced labelled datasets such as ImageNet (1.2 M images) and huge text corpora.", "database"),
        ("Compute", "GPUs do thousands of matrix multiplies in parallel; AlexNet (2012) trained on two gaming GPUs.", "cpu"),
        ("Algorithms", "ReLU, good initialisation, dropout, BatchNorm, Adam, residual connections, attention — tricks that make deep stacks trainable.", "bulb"),
        ("Software", "PyTorch, TensorFlow and JAX compute gradients automatically, so a new model is a few dozen lines.", "code"),
        cols=2,
    )
    yield section("Where it's used", "world")
    yield table(
        ["Domain", "Typical architecture", "Examples"],
        ["Vision", "CNNs, Vision Transformers", "Classification, detection, segmentation, medical imaging"],
        ["Language", "Transformers", "Translation, chatbots, search, code completion"],
        ["Speech & audio", "CNNs + Transformers", "Speech recognition, text-to-speech"],
        ["Generation", "Diffusion models, GANs, VAEs, LLMs", "Image generation, text generation"],
        ["Sequences & time series", "RNNs/LSTMs, Transformers", "Forecasting, anomaly detection"],
    )
    yield warn("Deep learning is not automatically the best choice. On small **tabular** datasets, gradient-boosted trees (XGBoost, LightGBM) usually match or beat a neural network with far less effort.")
    yield qa("When would you not use deep learning?",
             "When data is small or tabular, when you need a simple interpretable model (credit decisions, regulated settings), or when compute and latency budgets are tight. Start with a simple baseline; reach for deep learning when the data is unstructured or plentiful — or when a pretrained model can be fine-tuned.")
    yield qa("What does “deep” mean?",
             "Many layers between input and output. Depth lets the network build features hierarchically — edges → textures → parts → objects — which is far more parameter-efficient than one enormous layer.")


@topic(G, "neuron-perceptron", "The Neuron & Perceptron", "circle-dot")
def _():
    yield lead("An artificial neuron takes a weighted sum of its inputs, adds a bias and passes the result through an activation function. The perceptron is the oldest version — and its failure on XOR explains why we need hidden layers.")
    yield formula("z = w₁x₁ + w₂x₂ + … + wₙxₙ + b = w · x + b        a = f(z)")
    yield table(
        ["Part", "Role"],
        ["Inputs `x`", "Features (pixel values, measurements, outputs of the previous layer)"],
        ["Weights `w`", "How much each input matters — learned"],
        ["Bias `b`", "Shifts the threshold — lets the neuron fire even when all inputs are 0"],
        ["Activation `f`", "A non-linearity (step, sigmoid, ReLU…) applied to the sum `z`"],
    )
    yield code('''
        import numpy as np

        x = np.array([0.5, -1.0, 2.0])     # inputs
        w = np.array([0.4, 0.3, -0.2])     # weights
        b = 0.1                            # bias

        z = w @ x + b                      # weighted sum: 0.2 - 0.3 - 0.4 + 0.1
        a = 1 / (1 + np.exp(-z))           # sigmoid activation
        print(round(z, 2), round(a, 3))    # -0.4 0.401
    ''')
    yield section("The perceptron learning rule", "school")
    yield p("Rosenblatt's perceptron (1958) uses a **step** activation (output 1 if `z > 0`, else 0) and a simple rule: after each example, nudge the weights toward the right answer.")
    yield formula("w ← w + η (y − ŷ) x        b ← b + η (y − ŷ)")
    yield code('''
        import numpy as np

        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])

        def train_perceptron(X, y, epochs=20, lr=0.1):
            w, b = np.zeros(2), 0.0
            for _ in range(epochs):
                for xi, yi in zip(X, y):
                    pred = int(xi @ w + b > 0)
                    w += lr * (yi - pred) * xi          # no change when the prediction is right
                    b += lr * (yi - pred)
            return (X @ w + b > 0).astype(int).tolist()

        print(train_perceptron(X, np.array([0, 0, 0, 1])))       # [0, 0, 0, 1] ← AND: learned
        print(train_perceptron(X, np.array([0, 1, 1, 1])))       # [0, 1, 1, 1] ← OR: learned
        print(train_perceptron(X, np.array([0, 1, 1, 0]), 1000)) # [1, 1, 0, 0] ← XOR: wrong, whatever the epochs
    ''')
    yield section("Why XOR breaks it", "separator")
    yield p("A single neuron draws one straight line (a hyperplane) through the input space. AND and OR are **linearly separable**; XOR is not — no single line puts (0,1) and (1,0) on one side and (0,0), (1,1) on the other. Minsky & Papert's 1969 book made this point and helped cause the first “AI winter”.")
    yield note("The fix is a **hidden layer**: two neurons each draw a line, and a third combines them. That is a multi-layer perceptron (next topics), trained with backpropagation.")
    yield table(
        ["", "Biological neuron", "Artificial neuron"],
        ["Inputs", "Dendrites receive signals", "Numbers `x₁…xₙ`"],
        ["Integration", "Cell body sums charge", "Weighted sum `w · x + b`"],
        ["Firing", "Spikes past a threshold", "Activation function `f(z)`"],
    )
    yield warn("The biological analogy is loose inspiration only. Modern networks are best understood as differentiable functions optimised by gradient descent.")
    yield qa("What is the role of the bias term?",
             "Without it, `w · x` is 0 whenever `x` is 0, so the decision boundary must pass through the origin. The bias shifts the boundary (or the activation's threshold), giving the neuron one more degree of freedom.")
    yield qa("Can a single perceptron learn XOR?",
             "No. It can only separate classes with a straight line, and XOR isn't linearly separable. One hidden layer with a non-linear activation is enough.")


@topic(G, "activation-functions", "Activation Functions", "wave-sine")
def _():
    yield lead("Activations add the non-linearity that lets networks learn curved decision boundaries. Without them, any stack of layers collapses into one linear layer.")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        W1, W2 = rng.normal(size=(3, 4)), rng.normal(size=(4, 2))
        x = rng.normal(size=(5, 3))

        two_layers = (x @ W1) @ W2           # two linear layers, no activation…
        one_layer = x @ (W1 @ W2)            # …equal one linear layer with weights W1 @ W2
        print(np.allclose(two_layers, one_layer))   # True
    ''')
    yield section("The common ones", "list-details")
    yield table(
        ["Function", "Formula", "Range", "Used for", "Watch out"],
        ["Sigmoid", "`σ(z) = 1 / (1 + e^-z)`", "(0, 1)", "Binary output (probability), gates in LSTMs", "Saturates → vanishing gradients; max slope 0.25; not zero-centred"],
        ["Tanh", "`tanh(z)`", "(−1, 1)", "RNN hidden states", "Zero-centred but still saturates"],
        ["ReLU", "`max(0, z)`", "[0, ∞)", "Default for CNNs & MLPs", "“Dying ReLU” — units stuck at 0 never recover"],
        ["Leaky ReLU", "`z if z > 0 else 0.01·z`", "(−∞, ∞)", "When many ReLUs die", "Extra hyper-parameter (slope)"],
        ["GELU", "`z · Φ(z)` (Φ = normal CDF)", "≈ (−0.17, ∞)", "Transformers (BERT, GPT)", "Slightly more compute"],
        ["SiLU / Swish", "`z · σ(z)`", "≈ (−0.28, ∞)", "Modern CNNs, LLaMA-style FFNs (SwiGLU)", "—"],
        ["Softmax", "`e^zᵢ / Σⱼ e^zⱼ`", "(0, 1), sums to 1", "Multi-class output layer", "Overflows without the max-subtraction trick"],
    )
    yield code('''
        import numpy as np
        from math import erf, sqrt

        z = np.array([-2.0, 0.0, 2.0])
        sigmoid = 1 / (1 + np.exp(-z))
        tanh = np.tanh(z)
        relu = np.maximum(0, z)
        leaky = np.where(z > 0, z, 0.01 * z)
        gelu = z * 0.5 * (1 + np.array([erf(v / sqrt(2)) for v in z]))

        print(sigmoid.round(3).tolist())    # [0.119, 0.5, 0.881]
        print(tanh.round(3).tolist())       # [-0.964, 0.0, 0.964]
        print(relu.tolist())                # [0.0, 0.0, 2.0]
        print(leaky.tolist())               # [-0.02, 0.0, 2.0]
        print(gelu.round(3).tolist())       # [-0.046, 0.0, 1.954]
    ''')
    yield section("Derivatives — why ReLU won", "trending-down")
    yield p("Backprop multiplies one activation derivative per layer. Sigmoid's derivative is at most 0.25, so ten sigmoid layers can shrink a gradient by `0.25¹⁰ ≈ 10⁻⁶`. ReLU's derivative is exactly 1 for positive inputs, so gradients pass through unchanged.")
    yield code('''
        import numpy as np

        z = np.array([-4.0, 0.0, 4.0])
        s = 1 / (1 + np.exp(-z))
        print((s * (1 - s)).round(4).tolist())     # [0.0177, 0.25, 0.0177] ← σ'(z) = σ(z)(1 − σ(z)); max 0.25
        print((1 - np.tanh(z) ** 2).round(4).tolist())   # [0.0013, 1.0, 0.0013] ← tanh'(z); max 1
        print((z > 0).astype(float).tolist())      # [0.0, 0.0, 1.0] ← ReLU'(z)
        print(0.25 ** 10)                          # 9.5367431640625e-07 ← best case after 10 sigmoid layers
    ''')
    yield section("Softmax, safely", "percentage")
    yield p("Softmax turns a vector of scores (**logits**) into probabilities. Subtracting the maximum first gives the same answer (it cancels in the ratio) but prevents `exp` from overflowing.")
    yield code('''
        import numpy as np

        def softmax(z):
            e = np.exp(z - z.max())            # shift so the largest exponent is e^0 = 1
            return e / e.sum()

        logits = np.array([2.0, 1.0, 0.1])
        p = softmax(logits)
        print(p.round(3).tolist(), round(p.sum(), 6))    # [0.659, 0.242, 0.099] 1.0

        big = np.array([1000.0, 999.0, 998.1])           # same gaps, huge values
        with np.errstate(over="ignore", invalid="ignore"):
            naive = np.exp(big) / np.exp(big).sum()
        print(naive.tolist())                            # [nan, nan, nan] ← inf / inf
        print(softmax(big).round(3).tolist())            # [0.659, 0.242, 0.099]
    ''')
    yield section("In PyTorch", "flame")
    yield code('''
        import torch
        import torch.nn.functional as F

        z = torch.tensor([-2.0, 0.0, 2.0])
        print(torch.relu(z))                        # tensor([0., 0., 2.])
        print(torch.sigmoid(z).round(decimals=3))   # tensor([0.1190, 0.5000, 0.8810])
        print(F.gelu(z).round(decimals=3))          # tensor([-0.0460,  0.0000,  1.9540])
        print(torch.softmax(torch.tensor([2.0, 1.0, 0.1]), dim=0).round(decimals=3))   # tensor([0.6590, 0.2420, 0.0990])
    ''')
    yield dodont("Use ReLU (or GELU/SiLU) in hidden layers; pick the **output** activation from the task: none for regression, sigmoid for binary, softmax for multi-class.",
                 "Sigmoid/tanh in the hidden layers of a deep feed-forward net — gradients vanish.")
    yield qa("Why do we need non-linear activation functions?",
             "A composition of linear maps is linear, so without non-linearities a 100-layer network could only learn what logistic/linear regression learns. Non-linearities let it approximate curved functions.")
    yield qa("What is the dying ReLU problem?",
             "If a unit's pre-activation becomes negative for every input (e.g. after a large update or a bad bias), its output and gradient are 0 everywhere and it never recovers. Fixes: lower learning rate, He initialisation, Leaky ReLU/GELU.")
    yield qa("Sigmoid vs softmax at the output?",
             "Sigmoid gives an independent probability per output — binary or **multi-label** (an image can be both “dog” and “outdoor”). Softmax gives a distribution over mutually exclusive classes that sums to 1 — **multi-class**.")


@topic(G, "mlp-forward-pass", "MLPs & the Forward Pass", "stack-2")
def _():
    yield lead("A multi-layer perceptron (MLP) stacks fully-connected layers with activations in between. The forward pass is just matrix multiplies — computed for a whole batch at once.")
    yield define("Fully-connected (dense / linear) layer", "every output unit is connected to every input: `Y = X W + b`, where `X` is (batch, n_in), `W` is (n_in, n_out) and `b` is (n_out,).")
    yield flow("Input layer (features)", "Hidden layer 1 + ReLU", "Hidden layer 2 + ReLU", "Output layer (logits)")
    yield section("Shapes and parameter counts", "ruler")
    yield formula("parameters of a dense layer = n_in × n_out + n_out   (weights + biases)")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        sizes = [4, 16, 8, 3]                  # 4 features → 16 → 8 → 3 classes
        params = [(rng.normal(0, 0.5, (a, b)), np.zeros(b)) for a, b in zip(sizes, sizes[1:])]

        def forward(X):
            h = X
            for i, (W, b) in enumerate(params):
                h = h @ W + b
                if i < len(params) - 1:       # ReLU on hidden layers only
                    h = np.maximum(0, h)
            return h                           # logits

        X = rng.normal(size=(5, 4))            # a batch of 5 samples
        print(forward(X).shape)                # (5, 3)
        print(sum(W.size + b.size for W, b in params))   # 243 ← (4·16+16) + (16·8+8) + (8·3+3)
    ''')
    yield section("A hidden layer solves XOR", "puzzle")
    yield p("With hand-picked weights, two ReLU units are enough: `h₁ = relu(x₁ + x₂)` counts the ones, `h₂ = relu(x₁ + x₂ − 1)` fires only when both are 1, and the output is `h₁ − 2h₂`.")
    yield code('''
        import numpy as np

        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        W1 = np.array([[1, 1], [1, 1]]); b1 = np.array([0, -1])
        W2 = np.array([1, -2]);          b2 = 0

        H = np.maximum(0, X @ W1 + b1)
        print(H.tolist())                  # [[0, 0], [1, 0], [1, 0], [2, 1]] ← the hidden representation
        print((H @ W2 + b2).tolist())      # [0, 1, 1, 0] ← XOR
    ''')
    yield note("The hidden layer re-maps the inputs so that the classes *become* linearly separable — (0,1) and (1,0) both land on `[1, 0]`. That is what “learning a representation” means. Backpropagation finds such weights automatically (see **Backpropagation**).")
    yield section("The same network in PyTorch", "flame")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        model = nn.Sequential(
            nn.Linear(4, 16), nn.ReLU(),
            nn.Linear(16, 8), nn.ReLU(),
            nn.Linear(8, 3),                  # raw logits — the loss applies softmax
        )
        X = torch.randn(5, 4)
        print(model(X).shape)                                    # torch.Size([5, 3])
        print(sum(p.numel() for p in model.parameters()))       # 243
    ''')
    yield section("Universal approximation", "infinity")
    yield define("Universal approximation theorem", "an MLP with **one** hidden layer and a non-linear activation can approximate any continuous function on a bounded domain as closely as you like — given enough hidden units.")
    yield warn("The theorem says a good network *exists*, not that gradient descent will find it or that it will generalise. The required width can be astronomically large; in practice **depth** gives the same power with far fewer parameters.")
    yield table(
        ["Choice", "Rule of thumb"],
        ["Hidden layers", "1–3 for tabular data; deeper nets need tricks (normalisation, residuals)"],
        ["Width", "Powers of two (64, 128, 256…) — wide enough to overfit a small batch"],
        ["Hidden activation", "ReLU / GELU"],
        ["Output layer", "Linear, with `n_out` = 1 (regression / binary) or number of classes"],
    )
    yield qa("What happens in a forward pass?",
             "Input flows layer by layer: each layer computes `XW + b`, applies its activation and passes the result on, until the output layer produces predictions (logits). Intermediate activations are kept in memory because backprop needs them.")
    yield qa("How many parameters does a Linear(512, 256) layer have?",
             "`512 × 256 + 256 = 131,328` — one weight per input–output pair plus one bias per output.")
