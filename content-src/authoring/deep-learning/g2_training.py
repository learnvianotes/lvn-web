from kit import *

G = "Training Neural Networks"


@topic(G, "loss-functions", "Loss Functions", "target-arrow")
def _():
    yield lead("The loss turns “how wrong is the network?” into one number to minimise. Pick it from the task — and in PyTorch, feed classification losses **raw logits**, not probabilities.")
    yield table(
        ["Task", "Output layer", "Loss", "PyTorch"],
        ["Regression", "Linear (no activation)", "MSE (or MAE / Huber if outliers)", "`nn.MSELoss`, `nn.L1Loss`, `nn.HuberLoss`"],
        ["Binary / multi-label", "1 logit per label", "Binary cross-entropy", "`nn.BCEWithLogitsLoss`"],
        ["Multi-class (one label)", "1 logit per class", "Cross-entropy", "`nn.CrossEntropyLoss`"],
    )
    yield section("Regression: MSE, MAE, Huber", "chart-line")
    yield formula("MSE = (1/n) Σ (yᵢ − ŷᵢ)²        MAE = (1/n) Σ |yᵢ − ŷᵢ|")
    yield code('''
        import numpy as np

        y     = np.array([3.0, 5.0, 2.0, 8.0])
        y_hat = np.array([2.5, 5.0, 3.0, 4.0])      # the last prediction is badly off

        err = y - y_hat
        print(np.mean(err ** 2))                    # 4.3125 ← MSE: the outlier dominates (4² = 16)
        print(np.mean(np.abs(err)))                 # 1.375 ← MAE: every unit of error counts the same
    ''')
    yield p("MSE punishes large errors quadratically (good when big mistakes are very bad, bad when labels contain outliers). MAE is robust to outliers but its gradient doesn't shrink near the optimum. **Huber** is quadratic for small errors and linear for large ones — a compromise.")
    yield section("Binary cross-entropy", "toggle-right")
    yield formula("BCE = −(1/n) Σ [ yᵢ log pᵢ + (1 − yᵢ) log(1 − pᵢ) ]        p = σ(logit)")
    yield code('''
        import numpy as np

        def bce(y, p):
            return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

        y = np.array([1, 0, 1])
        print(round(bce(y, np.array([0.9, 0.1, 0.8])), 4))    # 0.1446 ← confident and right
        print(round(bce(y, np.array([0.1, 0.9, 0.2])), 4))    # 2.0715 ← confident and wrong: huge loss
    ''')
    yield section("Cross-entropy for multi-class", "category")
    yield formula("CE = −log p_true = −log softmax(z)_true = −z_true + log Σⱼ e^zⱼ")
    yield p("Cross-entropy only looks at the probability given to the **correct** class. Predicting 0.7 for the right class costs `−log 0.7 ≈ 0.36`; predicting 0.01 costs 4.6. With `k` classes, a model that guesses uniformly scores `log k` — a handy sanity check for the first loss you see.")
    yield code('''
        import numpy as np
        import torch
        from torch import nn

        logits = np.array([[2.0, 1.0, 0.1],       # sample 0: true class 0
                           [0.5, 2.5, 0.3]])      # sample 1: true class 1
        target = np.array([0, 1])

        log_probs = logits - np.log(np.exp(logits).sum(axis=1, keepdims=True))   # log-softmax
        ce = -log_probs[np.arange(2), target].mean()
        print(round(ce, 4))                                            # 0.3185

        loss_fn = nn.CrossEntropyLoss()                               # log-softmax + NLL in one stable op
        print(round(loss_fn(torch.tensor(logits), torch.tensor(target)).item(), 4))   # 0.3185
        print(round(np.log(3), 4))                                    # 1.0986 ← loss of a uniform guess over 3 classes
    ''')
    yield section("Logits in, not probabilities", "alert-triangle")
    yield code('''
        import torch
        from torch import nn

        logits = torch.tensor([[2.0, -1.0]])      # one sample, 2 classes; true class 0
        target = torch.tensor([0])
        ce = nn.CrossEntropyLoss()

        print(round(ce(logits, target).item(), 4))                        # 0.0486 ← correct usage
        print(round(ce(torch.softmax(logits, 1), target).item(), 4))      # 0.3397 ← softmax applied twice: wrong

        bce = nn.BCEWithLogitsLoss()               # sigmoid + BCE, numerically stable
        print(round(bce(torch.tensor([3.0]), torch.tensor([1.0])).item(), 4))   # 0.0486
    ''')
    yield warn("`nn.CrossEntropyLoss` and `nn.BCEWithLogitsLoss` apply softmax/sigmoid **internally**. Adding your own softmax/sigmoid before them squashes the gradients and training stalls. Apply softmax only when you need probabilities for display or decisions.")
    yield qa("Why cross-entropy instead of MSE for classification?",
             "Cross-entropy is the negative log-likelihood of the correct class, so it punishes confident wrong answers heavily and its gradient with softmax is simply `p − y` — large when wrong. MSE on sigmoid/softmax outputs gives tiny gradients when the output saturates, so learning is slow.")
    yield qa("What loss would you expect at the start of training a 10-class classifier?",
             "About `ln 10 ≈ 2.30`. Much higher means the initial logits are too large (bad init or a bug); it's one of the quickest sanity checks.")


@topic(G, "gradient-descent", "Gradient Descent", "trending-down")
def _():
    yield lead("Training = walking downhill on the loss surface. The gradient points uphill, so each step moves the weights a little in the opposite direction.")
    yield formula("θ ← θ − η · ∇θ L(θ)        η = learning rate")
    yield section("Batch, mini-batch and stochastic", "stack")
    yield table(
        ["Variant", "Gradient computed on", "Pros", "Cons"],
        ["Batch GD", "The whole dataset", "Exact gradient, smooth path", "Slow per step; dataset must fit in memory"],
        ["Stochastic GD (SGD)", "One example", "Cheap steps, noise can escape bad regions", "Very noisy; poor hardware use"],
        ["**Mini-batch** GD", "A batch of 32–1024 examples", "GPU-friendly, reasonably stable — **the default**", "Batch size is another hyper-parameter"],
    )
    yield p("In deep learning “SGD” almost always means mini-batch SGD. Vocabulary: one **iteration** (step) processes one batch; one **epoch** is a full pass over the data — `ceil(N / batch_size)` iterations.")
    yield section("Mini-batch GD from scratch", "code")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        X = rng.uniform(-1, 1, size=200)
        y = 3 * X + 2 + rng.normal(0, 0.1, size=200)     # true line: y = 3x + 2

        w, b, lr, batch = 0.0, 0.0, 0.1, 20
        for epoch in range(50):
            idx = rng.permutation(len(X))                 # reshuffle every epoch
            for start in range(0, len(X), batch):
                j = idx[start:start + batch]
                err = (w * X[j] + b) - y[j]
                w -= lr * 2 * np.mean(err * X[j])         # ∂MSE/∂w
                b -= lr * 2 * np.mean(err)                # ∂MSE/∂b

        print(round(w, 2), round(b, 2))                   # 2.99 2.0
        print(len(X) // batch * 50)                       # 500 ← updates made (10 per epoch × 50 epochs)
    ''')
    yield section("The learning rate", "adjustments-horizontal")
    yield code('''
        def descend(lr, steps=20, w=5.0):
            for _ in range(steps):
                w -= lr * 2 * w            # minimise f(w) = w², gradient 2w
            return w

        print(round(descend(0.01), 3))     # 3.338 ← too small: barely moved
        print(round(descend(0.1), 3))      # 0.058 ← good: close to the minimum at 0
        print(round(descend(1.1), 1))      # 191.7 ← too large: diverges
    ''')
    yield table(
        ["Symptom", "Likely cause"],
        ["Loss goes to `nan` or explodes", "Learning rate too high"],
        ["Loss drops very slowly", "Learning rate too low"],
        ["Loss oscillates / is very noisy", "LR a bit high or batch too small"],
    )
    yield note("Typical starting points: `1e-3` for Adam/AdamW, `0.1` for SGD with momentum on CNNs. If you change the batch size a lot, retune the learning rate (a common heuristic scales it linearly with the batch size).")
    yield warn("The loss surface of a deep network is not a bowl — it has saddle points, flat regions and many minima. Mini-batch noise actually helps: it keeps the optimiser moving through flat areas and tends to find wider minima that generalise better.")
    yield qa("What is the difference between an epoch, a batch and an iteration?",
             "A batch is the subset of examples used for one gradient step; an iteration is one such step; an epoch is one pass over the whole training set. With 10,000 examples and batch size 100, one epoch is 100 iterations.")
    yield qa("How does batch size affect training?",
             "Bigger batches give smoother gradients and better GPU utilisation but need more memory, often a larger learning rate, and can generalise slightly worse. Smaller batches are noisier (a mild regulariser) but slower per epoch.")


@topic(G, "backpropagation", "Backpropagation", "git-branch")
def _():
    yield lead("Backpropagation computes the gradient of the loss with respect to every weight in one backward sweep, reusing intermediate results via the chain rule. It's what makes training deep networks affordable.")
    yield define("Backpropagation", "reverse-mode automatic differentiation: run the forward pass and remember the intermediate values, then walk the computational graph backwards, multiplying each node's **local gradient** by the gradient flowing in from above.")
    yield formula("chain rule:  ∂L/∂w = ∂L/∂a · ∂a/∂z · ∂z/∂w")
    yield section("A computational graph by hand", "sitemap")
    yield p("One neuron with a squared-error loss: `z = w·x + b`, `a = σ(z)`, `L = (a − y)²`.")
    yield flow("x, w, b", "z = w·x + b", "a = σ(z)", "L = (a − y)²")
    yield code('''
        import math

        x, y, w, b = 2.0, 1.0, 0.5, -0.5
        # forward
        z = w * x + b                           # 0.5
        a = 1 / (1 + math.exp(-z))              # σ(0.5)
        L = (a - y) ** 2
        # backward — one local derivative per edge, multiplied right to left
        dL_da = 2 * (a - y)
        da_dz = a * (1 - a)
        dL_dz = dL_da * da_dz
        dL_dw = dL_dz * x                       # ∂z/∂w = x
        dL_db = dL_dz * 1                       # ∂z/∂b = 1
        print(round(L, 4), round(dL_dw, 4), round(dL_db, 4))   # 0.1425 -0.3549 -0.1774
    ''')
    yield p("PyTorch's autograd does exactly this bookkeeping for you:")
    yield code('''
        import torch

        x, y = torch.tensor(2.0), torch.tensor(1.0)
        w = torch.tensor(0.5, requires_grad=True)
        b = torch.tensor(-0.5, requires_grad=True)

        L = (torch.sigmoid(w * x + b) - y) ** 2
        L.backward()                            # fills w.grad and b.grad
        print(round(w.grad.item(), 4), round(b.grad.item(), 4))   # -0.3549 -0.1774
    ''')
    yield section("A 2-layer network from scratch", "code")
    yield p("Forward: `H = relu(X W₁ + b₁)`, `P = σ(H W₂ + b₂)`, BCE loss. Backward, the key results are: for sigmoid + BCE, `∂L/∂logits = (P − y) / n`; for a linear layer `Y = XW`, `∂L/∂W = Xᵀ · ∂L/∂Y` and `∂L/∂X = ∂L/∂Y · Wᵀ`; for ReLU, pass the gradient where the input was positive.")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
        y = np.array([[0], [1], [1], [0]], dtype=float)              # XOR

        params = {"W1": rng.normal(0, 1, (2, 8)), "b1": np.full(8, 0.1),
                  "W2": rng.normal(0, 1, (8, 1)), "b2": np.zeros(1)}

        def forward_backward(p):
            Z1 = X @ p["W1"] + p["b1"]; H = np.maximum(0, Z1)       # forward
            Z2 = H @ p["W2"] + p["b2"]; P = 1 / (1 + np.exp(-Z2))
            loss = -np.mean(y * np.log(P) + (1 - y) * np.log(1 - P))
            dZ2 = (P - y) / len(X)                                   # backward
            dW2, db2 = H.T @ dZ2, dZ2.sum(0)
            dH = dZ2 @ p["W2"].T
            dZ1 = dH * (Z1 > 0)
            dW1, db1 = X.T @ dZ1, dZ1.sum(0)
            return loss, {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}

        loss, grads = forward_backward(params)
        print(round(loss, 4))                     # 0.7371 ← before training
    ''')
    yield section("Gradient checking", "checks")
    yield p("Always verify a hand-written backward pass numerically. Nudge each weight by `±ε` and compare the slope of the loss with the analytic gradient:")
    yield formula("∂L/∂θ ≈ [ L(θ + ε) − L(θ − ε) ] / 2ε        relative error = |g_analytic − g_numeric| / (|g_analytic| + |g_numeric|)")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
        y = np.array([[0], [1], [1], [0]], dtype=float)
        params = {"W1": rng.normal(0, 1, (2, 8)), "b1": np.full(8, 0.1),
                  "W2": rng.normal(0, 1, (8, 1)), "b2": np.zeros(1)}

        def forward_backward(p):
            Z1 = X @ p["W1"] + p["b1"]; H = np.maximum(0, Z1)
            Z2 = H @ p["W2"] + p["b2"]; P = 1 / (1 + np.exp(-Z2))
            loss = -np.mean(y * np.log(P) + (1 - y) * np.log(1 - P))
            dZ2 = (P - y) / len(X)
            dH = dZ2 @ p["W2"].T
            dZ1 = dH * (Z1 > 0)
            return loss, {"W1": X.T @ dZ1, "b1": dZ1.sum(0), "W2": H.T @ dZ2, "b2": dZ2.sum(0)}

        _, grads = forward_backward(params)
        eps, worst = 1e-6, 0.0
        for name, value in params.items():
            for i in np.ndindex(value.shape):
                old = value[i]
                value[i] = old + eps; up, _ = forward_backward(params)
                value[i] = old - eps; down, _ = forward_backward(params)
                value[i] = old
                numeric, analytic = (up - down) / (2 * eps), grads[name][i]
                if abs(numeric) + abs(analytic) > 0:
                    worst = max(worst, abs(numeric - analytic) / (abs(numeric) + abs(analytic)))
        print(worst < 1e-6)            # True ← analytic and numeric gradients agree
    ''')
    yield section("Training it", "player-play")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
        y = np.array([[0], [1], [1], [0]], dtype=float)
        p = {"W1": rng.normal(0, 1, (2, 8)), "b1": np.full(8, 0.1),
             "W2": rng.normal(0, 1, (8, 1)), "b2": np.zeros(1)}

        def forward_backward(p):
            Z1 = X @ p["W1"] + p["b1"]; H = np.maximum(0, Z1)
            Z2 = H @ p["W2"] + p["b2"]; P = 1 / (1 + np.exp(-Z2))
            loss = -np.mean(y * np.log(P) + (1 - y) * np.log(1 - P))
            dZ2 = (P - y) / len(X)
            dH = dZ2 @ p["W2"].T
            dZ1 = dH * (Z1 > 0)
            return loss, P, {"W1": X.T @ dZ1, "b1": dZ1.sum(0), "W2": H.T @ dZ2, "b2": dZ2.sum(0)}

        history = []
        for step in range(2000):
            loss, P, grads = forward_backward(p)
            for k in p:
                p[k] -= 0.5 * grads[k]                  # plain gradient descent
            if step % 500 == 0:
                history.append(round(float(loss), 3))
        print(history)                                  # [0.737, 0.003, 0.001, 0.001] ← loss every 500 steps
        print((P > 0.5).astype(int).ravel().tolist())   # [0, 1, 1, 0] ← XOR learned
    ''')
    yield note("Cost: the backward pass costs roughly **2×** the forward pass, and it needs the stored activations — which is why training uses much more memory than inference.")
    yield warn("Gradient checking is for debugging only — it costs two forward passes per parameter. Use `float64`, a small `ε` (~1e-6) and avoid points where ReLU is exactly at its kink.")
    yield qa("Explain backpropagation in two sentences.",
             "After a forward pass that stores intermediate values, we apply the chain rule backwards from the loss: each node multiplies the incoming gradient by its local derivative and passes it to its inputs. This gives the gradient for every parameter in about the cost of one extra forward pass.")
    yield qa("Why reverse mode and not forward mode differentiation?",
             "A network has millions of inputs (parameters) and one scalar output (the loss). Reverse mode gets all parameter gradients in one backward pass; forward mode would need one pass per parameter.")


@topic(G, "optimizers", "Optimizers: Momentum, RMSProp, Adam", "rocket")
def _():
    yield lead("Plain SGD uses only the current gradient. Modern optimizers also remember past gradients — to build speed in consistent directions (momentum) and to give each parameter its own step size (RMSProp, Adam).")
    yield table(
        ["Optimizer", "Update (g = gradient)", "Idea"],
        ["SGD", "`θ ← θ − η·g`", "Step against the gradient"],
        ["Momentum", "`v ← βv + g;  θ ← θ − η·v`", "A heavy ball: speeds up along consistent directions, damps zig-zag"],
        ["Nesterov", "Gradient evaluated at the look-ahead point `θ − ηβv`", "Momentum that corrects earlier"],
        ["RMSProp", "`s ← ρs + (1−ρ)g²;  θ ← θ − η·g / (√s + ε)`", "Divide by recent gradient size — per-parameter step"],
        ["Adam", "`m ← β₁m + (1−β₁)g;  v ← β₂v + (1−β₂)g²;  θ ← θ − η·m̂ / (√v̂ + ε)`", "Momentum + RMSProp, with bias correction `m̂ = m / (1−β₁ᵗ)`"],
        ["AdamW", "Adam + `θ ← θ − η·λ·θ` applied separately", "Weight decay **decoupled** from the adaptive step"],
    )
    yield section("Racing them on a narrow valley", "chart-line")
    yield p("`f(x, y) = x² + 100y²` is steep in `y` and flat in `x` — like many real loss surfaces. Plain SGD must keep its step below 0.01 to avoid bouncing out of the valley in `y`, and then crawls along `x`. All three start at `(5, 1)` and take 100 steps; the minimum is `f = 0`.")
    yield code('''
        import numpy as np

        grad = lambda t: np.array([2 * t[0], 200 * t[1]])     # ∇ of f = x² + 100y²
        f = lambda t: t[0] ** 2 + 100 * t[1] ** 2
        start, steps = np.array([5.0, 1.0]), 100

        def sgd(lr=0.009):                                    # above 0.01 it diverges in y
            t = start.copy()
            for _ in range(steps):
                t -= lr * grad(t)
            return f(t)

        def momentum(lr=0.005, beta=0.9):
            t, v = start.copy(), np.zeros(2)
            for _ in range(steps):
                v = beta * v + grad(t)
                t -= lr * v
            return f(t)

        def adam(lr=0.3, b1=0.9, b2=0.999, eps=1e-8):
            t, m, v = start.copy(), np.zeros(2), np.zeros(2)
            for k in range(1, steps + 1):
                g = grad(t)
                m = b1 * m + (1 - b1) * g
                v = b2 * v + (1 - b2) * g ** 2
                m_hat, v_hat = m / (1 - b1 ** k), v / (1 - b2 ** k)
                t -= lr * m_hat / (np.sqrt(v_hat) + eps)
            return f(t)

        print(f"{sgd():.4f}")        # 0.6611 ← still far from the minimum
        print(f"{momentum():.4f}")   # 0.0004
        print(f"{adam():.4f}")       # 0.0007
    ''')
    yield section("In PyTorch", "flame")
    yield code('''
        import torch
        from torch import nn

        model = nn.Linear(10, 1)
        opt_sgd = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9, nesterov=True)
        opt_adam = torch.optim.Adam(model.parameters(), lr=1e-3)
        opt_adamw = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

        print(opt_adamw.defaults["betas"], opt_adamw.defaults["eps"])   # (0.9, 0.999) 1e-08
    ''')
    yield steps(
        ("`optimizer.zero_grad()`", "Clear old gradients — PyTorch **accumulates** them otherwise."),
        ("`loss.backward()`", "Compute fresh gradients into each parameter's `.grad`."),
        ("`optimizer.step()`", "Update the parameters using those gradients (and the optimizer's memory)."),
    )
    yield section("Adam vs AdamW", "scale")
    yield p("L2 regularisation adds `λθ` to the gradient. In Adam that term is then divided by `√v̂`, so parameters with large gradients get *less* regularisation — not what we want. **AdamW** applies the decay directly to the weights, outside the adaptive step. It's the default for Transformers.")
    yield table(
        ["Choose", "When"],
        ["AdamW (lr ≈ 1e-3 … 1e-4)", "Default for most work: Transformers, MLPs, fine-tuning"],
        ["SGD + momentum 0.9 (lr ≈ 0.1) + schedule", "CNNs on images, when you can tune — often generalises slightly better"],
        ["Adam", "Quick prototypes; same as AdamW with `weight_decay=0`"],
    )
    yield warn("An optimizer keeps state: Adam stores two extra tensors (`m`, `v`) per parameter — the model's weights ×3 in memory. Save the optimizer's `state_dict()` with checkpoints or resumed training will behave differently.")
    yield qa("Why does Adam need bias correction?",
             "`m` and `v` start at zero, so during the first steps they're biased toward zero (e.g. after step 1, `m = 0.1·g`). Dividing by `1 − βᵗ` rescales them to proper averages; the correction fades as `t` grows.")
    yield qa("What does momentum do?",
             "It keeps an exponentially-weighted running sum of past gradients. Components that point the same way every step add up (faster progress along valleys); components that flip sign cancel (less zig-zagging).")


@topic(G, "learning-rate-schedules", "Learning-Rate Schedules & Warmup", "calendar-stats")
def _():
    yield lead("The best learning rate changes during training: large early to make progress, small late to settle into a minimum. Schedules automate that — and warmup protects the fragile first steps.")
    yield table(
        ["Schedule", "Shape", "Typical use"],
        ["Step decay", "Multiply by γ (e.g. 0.1) every N epochs", "Classic CNN training (ResNet)"],
        ["Exponential", "Multiply by γ every epoch", "Simple smooth decay"],
        ["Cosine annealing", "Half a cosine from max to ~0", "Modern default for vision & LLMs"],
        ["Linear warmup + decay", "Ramp 0 → max over the first steps, then cosine/linear down", "Transformers, large batches, fine-tuning"],
        ["One-cycle", "Up then down in one cycle", "Fast training on a fixed budget"],
        ["Reduce on plateau", "Cut LR when validation loss stops improving", "When you don't know the length of training"],
    )
    yield section("Step and cosine in PyTorch", "flame")
    yield code('''
        import torch
        from torch import nn

        def lrs(make_scheduler, epochs=8):
            opt = torch.optim.SGD(nn.Linear(2, 1).parameters(), lr=0.1)
            sched = make_scheduler(opt)
            out = []
            for _ in range(epochs):
                out.append(round(opt.param_groups[0]["lr"], 4))
                opt.step()                    # (training for one epoch would go here)
                sched.step()                  # then advance the schedule
            return out

        print(lrs(lambda o: torch.optim.lr_scheduler.StepLR(o, step_size=3, gamma=0.1)))   # [0.1, 0.1, 0.1, 0.01, 0.01, 0.01, 0.001, 0.001]
        print(lrs(lambda o: torch.optim.lr_scheduler.CosineAnnealingLR(o, T_max=8)))       # [0.1, 0.0962, 0.0854, 0.0691, 0.05, 0.0309, 0.0146, 0.0038]
    ''')
    yield section("Warmup + cosine", "flame")
    yield p("Adam's early estimates of `v` are noisy, and a freshly initialised network has large, badly-scaled gradients. Starting with a tiny LR and ramping up over the first few hundred or thousand steps avoids early divergence.")
    yield code('''
        import math
        import torch
        from torch import nn

        warmup, total = 3, 10
        def factor(step):                                   # multiplier on the base LR
            if step < warmup:
                return (step + 1) / warmup                  # linear ramp
            progress = (step - warmup) / (total - warmup)
            return 0.5 * (1 + math.cos(math.pi * progress)) # cosine down to 0

        opt = torch.optim.AdamW(nn.Linear(2, 1).parameters(), lr=1e-3)
        sched = torch.optim.lr_scheduler.LambdaLR(opt, factor)
        seen = []
        for _ in range(total):
            seen.append(round(opt.param_groups[0]["lr"] * 1000, 2))   # in units of 1e-3
            opt.step(); sched.step()
        print(seen)     # [0.33, 0.67, 1.0, 1.0, 0.95, 0.81, 0.61, 0.39, 0.19, 0.05]
    ''')
    yield warn("Call `scheduler.step()` **after** `optimizer.step()`, and be consistent about the unit — per epoch or per batch. Transformers usually step the schedule every batch; `ReduceLROnPlateau.step(val_loss)` takes the metric as an argument.")
    yield section("Finding a good max LR", "search")
    yield p("An **LR range test**: train for a few hundred steps while increasing the LR exponentially (1e-7 → 1), plot loss vs LR, and pick a value about 10× smaller than where the loss is lowest (before it blows up).")
    yield qa("Why use learning-rate warmup?",
             "At the start, weights are random and optimizer statistics are unreliable, so large steps can push the network into a bad region or cause `nan`s. A short linear warmup lets things stabilise before the full learning rate kicks in; it matters most for Transformers, Adam and large batch sizes.")
    yield qa("Why decay the learning rate?",
             "A large LR explores and makes fast progress but bounces around the minimum; lowering it lets the weights settle into the bottom of the basin, which usually lowers both training and validation loss at the end.")
