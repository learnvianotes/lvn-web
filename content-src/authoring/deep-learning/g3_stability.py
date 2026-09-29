from kit import *

G = "Stable Training & Regularization"


@topic(G, "vanishing-gradients-initialization", "Vanishing Gradients & Weight Init", "arrows-vertical")
def _():
    yield lead("In a deep network the signal is multiplied by one weight matrix per layer — forwards and backwards. If each multiplication shrinks it a little, gradients vanish; if each grows it a little, they explode. Good initialisation keeps the scale steady.")
    yield section("Why not start from zero?", "equal")
    yield p("If every weight in a layer starts equal, every unit computes the same output and receives the same gradient — they stay identical forever (**symmetry**). Random initialisation breaks the tie; the question is how large the random values should be.")
    yield code('''
        import numpy as np

        X = np.array([[1.0, 2.0], [0.5, -1.0]])
        W1 = np.full((2, 3), 0.5)                     # all hidden weights equal
        H = np.tanh(X @ W1)
        print(H.round(3).tolist())                    # [[0.905, 0.905, 0.905], [-0.245, -0.245, -0.245]] ← 3 hidden units, identical columns
    ''')
    yield section("Watching activations vanish", "chart-line")
    yield code('''
        import numpy as np

        def final_std(scale, act, layers=20, width=256):
            rng = np.random.default_rng(0)
            h = rng.normal(size=(512, width))
            for _ in range(layers):
                W = rng.normal(0, scale, size=(width, width))
                h = act(h @ W)
            return float(h.std())

        relu = lambda z: np.maximum(0, z)
        print(f"{final_std(0.01, np.tanh):.1e}")               # 1.1e-16 ← too small: signal dies
        print(f"{final_std(1.0, relu):.1e}")                   # 1.2e+21 ← too large: explodes
        print(f"{final_std(np.sqrt(1 / 256), np.tanh):.2f}")   # 0.15 ← Xavier with tanh: survives
        print(f"{final_std(np.sqrt(2 / 256), relu):.2f}")      # 1.05 ← He with ReLU: stays ~1
    ''')
    yield section("Xavier and He", "math-function")
    yield table(
        ["Scheme", "Weight variance", "Use with", "PyTorch"],
        ["Xavier / Glorot", "`2 / (fan_in + fan_out)`  (≈ `1 / fan_in`)", "tanh, sigmoid, linear", "`nn.init.xavier_uniform_`"],
        ["He / Kaiming", "`2 / fan_in`", "ReLU and variants", "`nn.init.kaiming_normal_(w, nonlinearity='relu')`"],
        ["PyTorch default for `nn.Linear`", "Uniform(±1/√fan_in)", "Reasonable baseline", "applied automatically"],
    )
    yield p("The idea: a sum of `fan_in` random terms has variance `fan_in × Var(w) × Var(x)`. Setting `Var(w) = 1/fan_in` keeps the output variance equal to the input's. ReLU zeroes half its inputs, halving the variance — so He doubles it back with `2/fan_in`.")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        layer = nn.Linear(512, 512)
        nn.init.kaiming_normal_(layer.weight, nonlinearity="relu")
        nn.init.zeros_(layer.bias)
        print(round(layer.weight.std().item(), 3), round((2 / 512) ** 0.5, 3))   # 0.063 0.062 ← measured vs target std
    ''')
    yield section("Vanishing and exploding gradients", "trending-down")
    yield p("By the chain rule, the gradient at layer 1 is a **product** of one factor per layer above it. Factors below 1 (saturated sigmoids: slope ≤ 0.25) shrink it exponentially — early layers stop learning. Factors above 1 (large weights, long RNN unrolls) blow it up — the loss becomes `nan`.")
    yield code('''
        import torch
        from torch import nn

        def first_layer_grad(act, he=False, depth=15):
            torch.manual_seed(0)
            layers = []
            for _ in range(depth):
                lin = nn.Linear(32, 32)
                if he:
                    nn.init.kaiming_normal_(lin.weight, nonlinearity="relu")
                layers += [lin, act()]
            net = nn.Sequential(*layers, nn.Linear(32, 1))
            net(torch.randn(64, 32)).pow(2).mean().backward()
            return net[0].weight.grad.abs().mean().item()

        print(f"{first_layer_grad(nn.Sigmoid):.0e}")        # 3e-15 ← sigmoid: vanished
        print(f"{first_layer_grad(nn.ReLU):.0e}")           # 2e-10 ← ReLU, default init: still shrinks
        print(f"{first_layer_grad(nn.ReLU, he=True):.0e}")  # 1e-03 ← ReLU + He init: healthy
    ''')
    yield table(
        ["Fix", "Helps with"],
        ["ReLU-family activations", "Vanishing (slope 1 for positive inputs)"],
        ["Xavier / He initialisation", "Both — keeps the scale steady at the start"],
        ["BatchNorm / LayerNorm", "Both — re-normalises activations every layer"],
        ["Residual (skip) connections", "Vanishing — gradient flows through the identity path (ResNets, Transformers)"],
        ["Gradient clipping", "Exploding — caps the gradient norm"],
        ["LSTM / GRU gates", "Vanishing through time in RNNs"],
    )
    yield section("Gradient clipping", "scissors")
    yield code('''
        import torch
        from torch import nn

        model = nn.Linear(4, 1)
        for p in model.parameters():
            p.grad = torch.full_like(p, 10.0)             # pretend a huge gradient arrived

        before = nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)   # returns the norm before clipping
        after = torch.cat([p.grad.flatten() for p in model.parameters()]).norm()
        print(round(before.item(), 2), round(after.item(), 2))   # 22.36 1.0
    ''')
    yield note("Clipping rescales the whole gradient vector when its norm exceeds `max_norm` — the direction is kept, only the step length is capped. Call it between `loss.backward()` and `optimizer.step()`. It's standard for RNNs and Transformers (`max_norm=1.0`).")
    yield qa("What is the vanishing gradient problem and how do you fix it?",
             "Gradients shrink exponentially as they flow backwards through many layers (or time steps) because they're multiplied by factors smaller than 1, so early layers barely learn. Fixes: ReLU-type activations, He/Xavier init, normalisation layers, residual connections, and gated RNNs (LSTM/GRU).")
    yield qa("Why can't all weights be initialised to zero?",
             "Every unit in a layer would compute the same function and get the same update, so the layer behaves like a single unit forever. (Biases can start at zero — the random weights already break the symmetry.)")


@topic(G, "normalization", "Batch Norm & Layer Norm", "adjustments")
def _():
    yield lead("Normalisation layers rescale activations to zero mean and unit variance inside the network, then let it learn the best scale and shift. Training becomes faster, more stable and less sensitive to initialisation.")
    yield formula("x̂ = (x − μ) / √(σ² + ε)        y = γ · x̂ + β      (γ, β learned)")
    yield table(
        ["", "BatchNorm", "LayerNorm"],
        ["Statistics over", "The **batch** (per feature/channel)", "The **features** of each sample"],
        ["Depends on batch size", "Yes — noisy for small batches", "No"],
        ["Train vs eval", "Different: uses running averages at eval", "Same computation"],
        ["Used in", "CNNs", "Transformers, RNNs"],
    )
    yield section("BatchNorm by hand", "code")
    yield code('''
        import numpy as np
        import torch
        from torch import nn

        x = np.array([[1.0, 200.0], [2.0, 220.0], [3.0, 240.0], [4.0, 260.0]])   # 4 samples, 2 features
        mu, var = x.mean(axis=0), x.var(axis=0)             # per feature, over the batch
        x_hat = (x - mu) / np.sqrt(var + 1e-5)
        print(x_hat[:, 0].round(3).tolist())               # [-1.342, -0.447, 0.447, 1.342]
        print(x_hat[:, 1].round(3).tolist())               # [-1.342, -0.447, 0.447, 1.342] ← same, whatever the original scale

        bn = nn.BatchNorm1d(2)                             # γ = 1, β = 0 at the start
        out = bn(torch.tensor(x, dtype=torch.float32))     # training mode: batch statistics
        print(np.allclose(out.detach().numpy(), x_hat, atol=1e-4))   # True
    ''')
    yield section("Train vs eval mode", "toggle-left")
    yield p("During training BatchNorm uses the current batch's mean and variance and updates **running averages**. In `model.eval()` it uses those running averages instead, so a single example gets a deterministic output.")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        bn = nn.BatchNorm1d(1, momentum=0.1)
        print(bn.running_mean.item(), bn.running_var.item())   # 0.0 1.0 ← initial values

        bn.train()
        for _ in range(100):
            bn(torch.randn(32, 1) * 3 + 10)                    # data with mean 10, std 3
        print(round(bn.running_mean.item(), 1), round(bn.running_var.item() ** 0.5, 1))   # 9.8 2.9

        bn.eval()
        print(round(bn(torch.tensor([[10.0]])).item(), 2))     # 0.07 ← ≈ 0: the value sits at the mean
    ''')
    yield warn("Forgetting `model.eval()` before validation or inference is a classic bug: BatchNorm then normalises with the statistics of whatever batch you pass in (and a batch of 1 breaks it), and dropout stays on. Always switch modes.")
    yield section("LayerNorm", "layout-rows")
    yield code('''
        import torch
        from torch import nn

        x = torch.tensor([[1.0, 2.0, 3.0, 4.0],
                          [10.0, 20.0, 30.0, 40.0]])
        ln = nn.LayerNorm(4)                          # normalise over the last dimension of each sample
        out = ln(x).detach()
        print([round(v, 3) for v in out[0].tolist()])   # [-1.342, -0.447, 0.447, 1.342]
        print([round(v, 3) for v in out[1].tolist()])   # [-1.342, -0.447, 0.447, 1.342] ← same: each row is scaled on its own
    ''')
    yield p("Each row is normalised on its own, so it works with any batch size (even 1) and with variable-length sequences — why Transformers use it. Many LLMs use **RMSNorm**, a cheaper variant that only divides by the root-mean-square (no mean subtraction).")
    yield cards(
        ("GroupNorm", "Normalises groups of channels per sample — a BatchNorm replacement for tiny batches (detection, segmentation).", "layout-grid"),
        ("Pre-LN vs Post-LN", "Transformers normalise *before* each sub-layer (Pre-LN) in most modern models — more stable to train than the original Post-LN.", "arrows-sort"),
    )
    yield qa("Why does batch normalization help?",
             "It keeps each layer's inputs in a well-scaled range, which allows higher learning rates, reduces sensitivity to initialisation and smooths the loss landscape. The batch noise also gives a mild regularising effect.")
    yield qa("BatchNorm vs LayerNorm — when do you use which?",
             "BatchNorm for CNNs with reasonably large batches. LayerNorm (or RMSNorm) for Transformers and RNNs, where sequence lengths vary, batches can be small, and train/inference behaviour should be identical.")


@topic(G, "regularization", "Regularization", "shield-check")
def _():
    yield lead("Big networks can memorise their training set. Regularisation makes memorising harder or less attractive, so the model learns patterns that generalise: weight decay, dropout, early stopping, data augmentation and more.")
    yield p("First diagnose (see the **Machine Learning** notes on train/test protocols): training loss far below validation loss means **overfitting** → regularise or get more data. Both losses high means **underfitting** → bigger model, train longer, less regularisation.")
    yield section("L2 regularisation / weight decay", "scale")
    yield formula("L_total = L_data + (λ/2) Σ w²        ⇒        w ← w − η(∇L_data + λw) = (1 − ηλ)·w − η∇L_data")
    yield p("Each step shrinks (“decays”) every weight towards zero; only weights that keep earning their place in the loss stay large. Smaller weights mean a smoother function. In PyTorch: `AdamW(..., weight_decay=0.01)`; it's usual to exclude biases and normalisation parameters.")
    yield section("Dropout", "grid-dots")
    yield p("During training, dropout zeroes each activation with probability `p` and scales the survivors by `1/(1−p)` (**inverted dropout**), so the expected value is unchanged and nothing needs rescaling at test time. The network can't rely on any single unit — like training an ensemble of thinned networks.")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        drop = nn.Dropout(p=0.5)
        x = torch.ones(8)

        drop.train()
        print(drop(x))             # tensor([0., 0., 2., 0., 0., 0., 2., 2.]) ← half zeroed, survivors scaled ×2
        drop.eval()
        print(drop(x))             # tensor([1., 1., 1., 1., 1., 1., 1., 1.]) ← identity at inference
    ''')
    yield note("Typical rates: 0.1 in Transformers, 0.2–0.5 in MLP heads. Dropout is used less in modern CNNs (BatchNorm + augmentation do the job).")
    yield section("Early stopping", "player-stop")
    yield p("Track the validation loss every epoch, keep the best weights, and stop when it hasn't improved for `patience` epochs.")
    yield code('''
        val_losses = [0.90, 0.72, 0.61, 0.55, 0.53, 0.54, 0.56, 0.55, 0.58, 0.60]

        best, best_epoch, patience, waited = float("inf"), None, 3, 0
        for epoch, loss in enumerate(val_losses):
            if loss < best:
                best, best_epoch, waited = loss, epoch, 0     # save a checkpoint here
            else:
                waited += 1
                if waited >= patience:
                    break
        print(epoch, best_epoch, best)     # 7 4 0.53 ← stopped at epoch 7, restore epoch 4
    ''')
    yield section("Data augmentation", "photo")
    yield p("Create new, label-preserving variations of the training data so the model sees more diversity. Applied on the fly, only to the training set.")
    yield code('''
        import torch

        torch.manual_seed(0)
        img = torch.arange(9.0).reshape(1, 3, 3)                 # (channels, height, width)
        flipped = torch.flip(img, dims=[2])                      # horizontal flip
        noisy = img + 0.1 * torch.randn_like(img)                # small Gaussian noise
        print(img[0, 0].tolist(), flipped[0, 0].tolist())        # [0.0, 1.0, 2.0] [2.0, 1.0, 0.0]
        print(noisy.shape == img.shape)                          # True
    ''')
    yield table(
        ["Data", "Common augmentations"],
        ["Images", "Random crop & resize, horizontal flip, colour jitter, rotation, Cutout, MixUp/CutMix (`torchvision.transforms.v2`)"],
        ["Text", "Back-translation, synonym replacement, token masking"],
        ["Audio", "Time shift, pitch shift, added noise, SpecAugment (masking spectrogram bands)"],
    )
    yield warn("Augmentations must keep the label valid: flipping a “6” vertically makes a “9”; flipping a road sign mirrors its text. Never augment the validation or test sets.")
    yield section("The toolbox", "tools")
    yield table(
        ["Technique", "How it regularises"],
        ["More data", "The best regulariser of all"],
        ["Weight decay (L2)", "Penalises large weights"],
        ["Dropout", "Random unit removal — no co-adaptation"],
        ["Early stopping", "Stops before memorisation starts"],
        ["Data augmentation", "More diverse training examples"],
        ["Label smoothing", "Targets like 0.9 / 0.1 instead of 1 / 0 — discourages over-confidence (`CrossEntropyLoss(label_smoothing=0.1)`)"],
        ["Smaller model", "Less capacity to memorise"],
        ["Transfer learning", "Start from features learned on lots of data"],
    )
    yield qa("How does dropout work, and what changes at test time?",
             "During training each unit is zeroed with probability `p` and the rest are scaled by `1/(1−p)`, so the network learns redundant features and can't depend on any one unit. At test time dropout is switched off (`model.eval()`); thanks to the inverted scaling no further adjustment is needed.")
    yield qa("L2 regularisation vs weight decay — are they the same?",
             "For plain SGD, yes: adding `λw` to the gradient is the same as shrinking the weights each step. For adaptive optimisers like Adam they differ, because the L2 term gets divided by the adaptive denominator. AdamW implements true (decoupled) weight decay.")
    yield qa("Your model has 99% training accuracy and 70% validation accuracy. What do you do?",
             "It's overfitting. Get more data or augment it, add weight decay/dropout, use early stopping, reduce model size, or start from a pretrained model. Also check the validation set comes from the same distribution and there's no leakage or label noise.")
