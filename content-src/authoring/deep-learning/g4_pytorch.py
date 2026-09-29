from kit import *

G = "PyTorch in Practice"


@topic(G, "pytorch-tensors-autograd", "Tensors & Autograd", "flame")
def _():
    yield lead("PyTorch is NumPy with two superpowers: tensors can live on a GPU, and every operation can be recorded so gradients are computed automatically.")
    yield section("Creating tensors", "cube")
    yield code('''
        import torch

        a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        print(a.shape, a.dtype)                      # torch.Size([2, 2]) torch.float32
        print(torch.zeros(2, 3).shape, torch.ones(4).tolist())   # torch.Size([2, 3]) [1.0, 1.0, 1.0, 1.0]
        print(torch.arange(0, 10, 3).tolist())       # [0, 3, 6, 9]
        print(torch.tensor([1, 2]).dtype)            # torch.int64 ← integers default to int64

        torch.manual_seed(0)
        r = torch.randn(3)                           # standard normal, reproducible with the seed
        print(r.round(decimals=4))                   # tensor([ 1.5410, -0.2934, -2.1788])
    ''')
    yield section("Shapes, maths and broadcasting", "arrows-maximize")
    yield code('''
        import torch

        x = torch.arange(6.0)
        m = x.reshape(2, 3)                         # or x.view(2, 3) — same data, new shape
        print(m.tolist())                           # [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]
        print(m.T.shape, m.unsqueeze(0).shape, m.flatten().shape)   # torch.Size([3, 2]) torch.Size([1, 2, 3]) torch.Size([6])

        print((m @ m.T).tolist())                   # [[5.0, 14.0], [14.0, 50.0]] ← matrix multiply (2×3 @ 3×2)
        print((m * 10).tolist())                    # [[0.0, 10.0, 20.0], [30.0, 40.0, 50.0]] ← element-wise
        print((m + torch.tensor([100.0, 200.0, 300.0])).tolist())   # [[100.0, 201.0, 302.0], [103.0, 204.0, 305.0]] ← broadcast over rows
        print(m.sum(dim=0).tolist(), m.mean(dim=1).tolist())        # [3.0, 5.0, 7.0] [1.0, 4.0] ← per column / per row
        print(m.argmax(dim=1).tolist())             # [2, 2]
    ''')
    yield table(
        ["Operation", "PyTorch", "NumPy equivalent"],
        ["Change shape", "`x.view(...)`, `x.reshape(...)`", "`x.reshape(...)`"],
        ["Add / remove a size-1 axis", "`x.unsqueeze(0)`, `x.squeeze()`", "`x[None]`, `x.squeeze()`"],
        ["Reorder axes", "`x.permute(0, 2, 1)`, `x.T`", "`x.transpose(0, 2, 1)`"],
        ["Join", "`torch.cat([a, b], dim=0)`, `torch.stack`", "`np.concatenate`, `np.stack`"],
        ["Reduce along an axis", "`x.sum(dim=1)`", "`x.sum(axis=1)`"],
    )
    yield section("NumPy bridge and devices", "device-desktop")
    yield code('''
        import numpy as np
        import torch

        arr = np.array([1.0, 2.0, 3.0])
        t = torch.from_numpy(arr)          # shares memory with arr
        arr[0] = 99
        print(t.tolist())                  # [99.0, 2.0, 3.0] ← the change shows up
        print(t.dtype)                     # torch.float64 ← NumPy's float64 is kept

        device = "cuda" if torch.cuda.is_available() else "cpu"
        x = torch.ones(2, device=device)   # create directly on the device
        print(x.cpu().numpy().tolist())    # [1.0, 1.0] ← back to NumPy (must be on the CPU)
    ''')
    yield warn("Tensors in one operation must be on the same device and usually the same dtype: `float32` weights × `float64` data raises an error. Convert data with `torch.tensor(arr, dtype=torch.float32)` or `.float()`. On Apple silicon the GPU device is `\"mps\"`.")
    yield section("Autograd", "git-branch")
    yield p("Set `requires_grad=True` on a tensor and PyTorch records every operation on it in a graph. `loss.backward()` walks that graph backwards and stores `∂loss/∂x` in `x.grad`.")
    yield code('''
        import torch

        x = torch.tensor(3.0, requires_grad=True)
        y = x ** 2 + 2 * x              # y = x² + 2x
        y.backward()
        print(x.grad)                   # tensor(8.) ← dy/dx = 2x + 2 = 8

        w = torch.tensor([1.0, -2.0], requires_grad=True)
        loss = (w ** 2).sum()
        loss.backward()
        print(w.grad)                   # tensor([ 2., -4.]) ← 2w
        loss = (w ** 2).sum()
        loss.backward()
        print(w.grad)                   # tensor([ 4., -8.]) ← gradients ACCUMULATE
        w.grad.zero_()                  # what optimizer.zero_grad() does
        print(w.grad)                   # tensor([0., 0.])
    ''')
    yield code('''
        import torch

        w = torch.tensor([1.0, 2.0], requires_grad=True)
        with torch.no_grad():                   # no graph: for evaluation and manual weight updates
            y = w * 2
        print(y.requires_grad)                  # False

        z = (w * 3).detach()                    # a copy cut off from the graph
        print(z.requires_grad, z.tolist())      # False [3.0, 6.0]
        print((w * 3).grad_fn is not None)      # True ← operations remember how they were made
    ''')
    yield table(
        ["Tool", "Use it for"],
        ["`requires_grad=True`", "Tensors you want gradients for (model parameters have it already)"],
        ["`loss.backward()`", "Compute gradients of a **scalar** loss"],
        ["`.grad` / `.zero_()`", "Read / reset accumulated gradients"],
        ["`torch.no_grad()`", "Inference and evaluation — saves memory and time"],
        ["`.detach()`", "Use a value without letting gradients flow back through it"],
        ["`.item()`", "Pull a Python number out of a one-element tensor (e.g. for logging)"],
    )
    yield qa("Why do we call zero_grad() every iteration?",
             "PyTorch adds new gradients to whatever is in `.grad` (useful for gradient accumulation across micro-batches). Without resetting, each step would use the sum of all past gradients.")
    yield qa("view vs reshape?",
             "`view` never copies — it needs the tensor's memory to be laid out compatibly (contiguous) and errors otherwise. `reshape` returns a view when it can and copies when it must.")


@topic(G, "pytorch-modules-data", "nn.Module, Dataset & DataLoader", "box")
def _():
    yield lead("Models are `nn.Module` subclasses: declare layers in `__init__`, describe the computation in `forward`. Data comes in through a `Dataset` (one example at a time) wrapped in a `DataLoader` (batches, shuffling, workers).")
    yield section("Writing a model", "code")
    yield code('''
        import torch
        from torch import nn

        class MLP(nn.Module):
            def __init__(self, n_in, n_hidden, n_out, p_drop=0.1):
                super().__init__()                          # always call this first
                self.net = nn.Sequential(
                    nn.Linear(n_in, n_hidden), nn.ReLU(), nn.Dropout(p_drop),
                    nn.Linear(n_hidden, n_out),
                )

            def forward(self, x):                           # call model(x), never model.forward(x)
                return self.net(x)

        torch.manual_seed(0)
        model = MLP(4, 32, 3)
        print(model(torch.randn(8, 4)).shape)               # torch.Size([8, 3])
        print([name for name, _ in model.named_parameters()])   # ['net.0.weight', 'net.0.bias', 'net.3.weight', 'net.3.bias']
        print(sum(p.numel() for p in model.parameters() if p.requires_grad))   # 259
    ''')
    yield table(
        ["Building block", "What it is"],
        ["`nn.Linear`, `nn.Conv2d`, `nn.LSTM`, `nn.Embedding`…", "Layers with learnable parameters"],
        ["`nn.ReLU`, `nn.Dropout`, `nn.LayerNorm`…", "Activations, regularisers, normalisers"],
        ["`nn.Sequential`", "Chains modules; `forward` is automatic"],
        ["`nn.ModuleList` / `nn.ModuleDict`", "Lists/dicts of layers that are **registered** (a plain Python list is not)"],
        ["`model.parameters()`", "Every learnable tensor — what you hand to the optimizer"],
        ["`model.to(device)`", "Moves all parameters and buffers to CPU/GPU"],
    )
    yield warn("Layers kept in a plain Python `list` are invisible to `model.parameters()`, `.to(device)` and `state_dict()` — they silently never train. Use `nn.ModuleList`.")
    yield section("Dataset and DataLoader", "database")
    yield code('''
        import torch
        from torch.utils.data import Dataset, DataLoader, TensorDataset

        class SquaresDataset(Dataset):
            """x → x², generated on demand."""
            def __init__(self, n):
                self.x = torch.arange(n, dtype=torch.float32)
            def __len__(self):
                return len(self.x)
            def __getitem__(self, i):                      # one (input, target) pair
                return self.x[i:i + 1], self.x[i:i + 1] ** 2

        ds = SquaresDataset(10)
        print(len(ds), ds[3])                              # 10 (tensor([3.]), tensor([9.]))

        loader = DataLoader(ds, batch_size=4, shuffle=False)
        print([xb.shape[0] for xb, yb in loader])          # [4, 4, 2] ← last batch is smaller
        xb, yb = next(iter(loader))
        print(xb.shape, yb.ravel().tolist())               # torch.Size([4, 1]) [0.0, 1.0, 4.0, 9.0]

        # For tensors already in memory, TensorDataset does the same job:
        tds = TensorDataset(torch.randn(100, 5), torch.randint(0, 2, (100,)))
        train_loader = DataLoader(tds, batch_size=32, shuffle=True, drop_last=True)
        print(len(train_loader))                           # 3 ← 100 // 32 full batches
    ''')
    yield table(
        ["`DataLoader` argument", "Meaning"],
        ["`batch_size`", "Examples per batch"],
        ["`shuffle=True`", "New random order each epoch — **training only**"],
        ["`num_workers`", "Background processes that load/augment data in parallel"],
        ["`pin_memory=True`", "Faster CPU → GPU copies"],
        ["`drop_last=True`", "Skip the smaller final batch (keeps BatchNorm statistics sane)"],
        ["`collate_fn`", "Custom batching — e.g. padding variable-length sequences"],
    )
    yield qa("What's the difference between a Dataset and a DataLoader?",
             "A `Dataset` knows how many examples there are and how to fetch example `i` (`__len__`, `__getitem__`). A `DataLoader` wraps it to produce shuffled mini-batches, stacking examples into tensors and optionally loading in parallel worker processes.")


@topic(G, "pytorch-training-loop", "The Training Loop", "refresh")
def _():
    yield lead("Every PyTorch project has the same heartbeat: for each batch — forward, loss, zero_grad, backward, step. Around it: an evaluation loop in `eval()` mode under `no_grad()`, and checkpoints.")
    yield steps(
        ("`model.train()`", "Dropout on, BatchNorm uses batch statistics."),
        ("Forward", "`logits = model(xb)` then `loss = loss_fn(logits, yb)`."),
        ("`optimizer.zero_grad()`", "Clear gradients from the previous step."),
        ("`loss.backward()`", "Compute gradients."),
        ("`optimizer.step()`", "Update weights (then `scheduler.step()` if you use one)."),
        ("Evaluate", "`model.eval()` + `torch.no_grad()` on the validation set; keep the best checkpoint."),
    )
    yield section("A complete example", "player-play")
    yield p("Classify points by whether they lie inside a circle — a non-linear boundary a linear model can't learn.")
    yield code('''
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset

        torch.manual_seed(0)
        X = torch.rand(1000, 2) * 2 - 1                      # points in [-1, 1]²
        y = ((X ** 2).sum(dim=1) < 0.5).long()               # class 1 inside the circle
        train_ds, val_ds = TensorDataset(X[:800], y[:800]), TensorDataset(X[800:], y[800:])
        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=200)

        model = nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 2))
        loss_fn = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-2)

        def evaluate(loader):
            model.eval()
            correct = total = 0
            with torch.no_grad():
                for xb, yb in loader:
                    correct += (model(xb).argmax(dim=1) == yb).sum().item()
                    total += len(yb)
            return correct / total

        for epoch in range(20):
            model.train()
            for xb, yb in train_loader:
                loss = loss_fn(model(xb), yb)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        print(f"train acc {evaluate(train_loader):.2f}, val acc {evaluate(val_loader):.2f}")   # train acc 0.99, val acc 0.97
    ''')
    yield section("Saving and loading", "device-floppy")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        model = nn.Linear(3, 1)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

        torch.save(model.state_dict(), "model.pt")                   # weights only — the usual way
        torch.save({"epoch": 5, "model": model.state_dict(),          # full checkpoint to resume training
                    "optimizer": optimizer.state_dict()}, "checkpoint.pt")

        restored = nn.Linear(3, 1)                                    # rebuild the architecture first…
        restored.load_state_dict(torch.load("model.pt"))              # …then load the weights
        restored.eval()
        x = torch.ones(1, 3)
        print(torch.equal(model(x), restored(x)))                     # True

        ckpt = torch.load("checkpoint.pt")
        print(ckpt["epoch"], list(ckpt["model"].keys()))              # 5 ['weight', 'bias']
    ''')
    yield note("A `state_dict` is an ordered dict of parameter and buffer tensors keyed by name. Save that (not the whole pickled model object) — it survives code refactors and is safe to load with `torch.load(..., weights_only=True)`, the default in recent PyTorch.")
    yield section("Using a GPU", "cpu")
    yield code('''
        device = torch.device("cuda" if torch.cuda.is_available()
                              else "mps" if torch.backends.mps.is_available() else "cpu")
        model = model.to(device)                     # parameters move once
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)    # every batch must follow
            ...
        # load a GPU checkpoint on a CPU-only machine:
        state = torch.load("model.pt", map_location="cpu")
    ''', run=False)
    yield dodont("Call `model.eval()` and wrap validation/inference in `torch.no_grad()` (or `torch.inference_mode()`); log `loss.item()`, not the tensor.",
                 "Accumulate `total_loss += loss` — it keeps every step's graph alive and leaks memory.")
    yield qa("Walk me through a PyTorch training step.",
             "Put the model in train mode, move the batch to the device, run the forward pass to get logits, compute the loss, call `optimizer.zero_grad()`, `loss.backward()` to compute gradients, optionally clip them, then `optimizer.step()` to update the weights (and step the LR scheduler).")
    yield qa("What does model.eval() change?",
             "It switches layers that behave differently at inference: dropout is disabled and BatchNorm uses its running statistics. It does **not** disable gradient tracking — that's what `torch.no_grad()` is for.")


@topic(G, "training-in-practice", "Training in Practice", "bug")
def _():
    yield lead("Most failed training runs are bugs or bad settings, not bad architectures. A short, disciplined routine — start small, overfit one batch, read the loss curves, then tune — finds problems quickly.")
    yield section("A debugging routine", "list-check")
    yield steps(
        ("Look at the data", "Plot samples with their labels; check shapes, ranges, class balance, normalisation, and that inputs and labels still line up after shuffling."),
        ("Check the first loss", "For `k` balanced classes it should be ≈ `ln k`. Far off → wrong loss, wrong labels or bad init."),
        ("Overfit one small batch", "A healthy model + training loop drives the loss on 10–50 examples to ~0. If it can't, there's a bug."),
        ("Train a simple baseline", "Small model, Adam(W) at `1e-3`, no fancy tricks. Get something working end-to-end."),
        ("Scale up and regularise", "Bigger model, more data, augmentation, schedules — one change at a time, tracking validation metrics."),
    )
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        xb = torch.randn(16, 10)                          # one small batch with random labels —
        yb = torch.randint(0, 4, (16,))                   # impossible to generalise, easy to memorise
        model = nn.Sequential(nn.Linear(10, 64), nn.ReLU(), nn.Linear(64, 4))
        opt = torch.optim.Adam(model.parameters(), lr=1e-2)
        loss_fn = nn.CrossEntropyLoss()

        first = loss_fn(model(xb), yb).item()
        for _ in range(200):
            loss = loss_fn(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()

        print(round(first, 1), round(torch.log(torch.tensor(4.0)).item(), 1))   # 1.4 1.4 ← first loss ≈ ln 4
        print(loss.item() < 0.01)                                              # True ← memorised: the loop works
    ''')
    yield section("Reading loss curves", "chart-line")
    yield table(
        ["What you see", "Diagnosis", "Try"],
        ["Train ↓, validation ↓ then ↑", "Overfitting", "Early stopping, regularisation, augmentation, more data"],
        ["Both high and flat", "Underfitting or LR too low", "Bigger model, higher LR, train longer, check for bugs"],
        ["Loss jumps to `nan` / `inf`", "Exploding gradients, LR too high, `log(0)`", "Lower LR, gradient clipping, warmup, check the loss inputs"],
        ["Very noisy loss", "LR too high or batch too small", "Lower LR, larger batch, LR decay"],
        ["Validation better than training", "Dropout/augmentation only in training — or a leaky validation set", "Usually fine; check for leakage"],
        ["Plateau, then sudden drop", "Poor init or LR schedule kicking in", "Warmup, better init"],
    )
    yield section("Hyper-parameter tuning", "adjustments-horizontal")
    yield table(
        ["Priority", "Hyper-parameter", "Typical search"],
        ["1", "Learning rate", "Log scale: 1e-4, 3e-4, 1e-3, 3e-3…"],
        ["2", "Batch size / schedule / epochs", "As large as memory allows; cosine + warmup"],
        ["3", "Weight decay, dropout", "0–0.1; 0–0.5"],
        ["4", "Architecture (depth, width)", "Scale up until validation stops improving"],
    )
    yield note("Prefer **random search** over grid search (it explores important dimensions better), sample learning rates on a log scale, and tune on a smaller budget before full runs. Tools such as Optuna or Ray Tune automate this; Weights & Biases or TensorBoard track the runs.")
    yield section("Mixed precision", "bolt")
    yield p("Running most operations in 16-bit floats (`float16` or `bfloat16`) halves memory and uses fast tensor cores, with little accuracy loss. `torch.autocast` picks the precision per operation — matrix multiplies in 16-bit, sensitive reductions in 32-bit.")
    yield code('''
        import torch
        from torch import nn

        model = nn.Linear(8, 4)
        x = torch.randn(2, 8)
        with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
            out = model(x)
        print(out.dtype, model.weight.dtype)      # torch.bfloat16 torch.float32 ← compute in bf16, weights stay fp32
    ''')
    yield code('''
        scaler = torch.amp.GradScaler("cuda")          # float16 on CUDA needs loss scaling (bfloat16 doesn't)
        for xb, yb in loader:
            optimizer.zero_grad()
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                loss = loss_fn(model(xb), yb)
            scaler.scale(loss).backward()              # scale up so small gradients don't underflow
            scaler.step(optimizer)                     # unscales; skips the step if inf/nan appeared
            scaler.update()
    ''', run=False)
    yield section("GPU memory and gradient accumulation", "cpu")
    yield p("Memory holds weights, gradients, optimizer state (Adam: 2× weights) and the activations saved for backprop, which grow with batch size. When a batch doesn't fit, **accumulate** gradients over several micro-batches before stepping:")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        model = nn.Linear(4, 1)
        X, y = torch.randn(8, 4), torch.randn(8, 1)
        loss_fn = nn.MSELoss()

        model.zero_grad()
        loss_fn(model(X), y).backward()                    # one batch of 8
        full = model.weight.grad.clone()

        model.zero_grad()
        for xb, yb in zip(X.split(2), y.split(2)):         # 4 micro-batches of 2
            (loss_fn(model(xb), yb) / 4).backward()        # divide by the number of micro-batches
        print(torch.allclose(full, model.weight.grad, atol=1e-6))   # True ← same gradient
    ''')
    yield table(
        ["Speed-up", "How"],
        ["Keep the GPU fed", "`num_workers > 0`, `pin_memory=True`, avoid `.item()` / `.cpu()` inside the loop"],
        ["Mixed precision", "`torch.autocast` + bf16/fp16"],
        ["Compile", "`model = torch.compile(model)` fuses operations"],
        ["Bigger batches", "Better hardware use (retune the LR)"],
        ["Multiple GPUs", "`DistributedDataParallel` (DDP); FSDP to shard huge models"],
        ["Save memory", "Gradient checkpointing (recompute activations), smaller batch + accumulation"],
    )
    yield qa("Your loss isn't decreasing. How do you debug it?",
             "Check the data and labels first, then the initial loss against `ln k`, then try to overfit a single small batch. If that fails, look for bugs: missing `zero_grad`, softmax before `CrossEntropyLoss`, wrong label dtype/shape, frozen parameters, forgetting `optimizer.step()`, or an LR that's far too high or low. Then inspect gradient norms per layer.")
    yield qa("What is mixed precision training?",
             "Doing most computation in 16-bit floats while keeping a 32-bit master copy of the weights. It cuts memory and speeds up training on tensor-core GPUs. With float16 a gradient scaler prevents small gradients from underflowing; bfloat16 has float32's range and usually doesn't need one.")


@topic(G, "evaluating-models", "Evaluating Deep Learning Models", "chart-bar")
def _():
    yield lead("Measure on data the model never trained on, in eval mode, with the metric that matches the real goal. Loss tells you how training is going; task metrics tell you whether the model is useful.")
    yield section("Three splits", "arrows-split")
    yield table(
        ["Split", "Used for", "Touched"],
        ["Training", "Computing gradients", "Every step"],
        ["Validation", "Early stopping, hyper-parameters, model selection", "Every epoch"],
        ["Test", "Final, unbiased estimate", "**Once**, at the end"],
    )
    yield warn("Tuning on the test set turns it into a second validation set — the final number becomes optimistic. Also watch for leakage: near-duplicate images, the same patient/user in two splits, or time series split randomly instead of by time.")
    yield section("From logits to metrics", "calculator")
    yield code('''
        import torch

        logits = torch.tensor([[2.0, 0.1, -1.0], [0.2, 1.5, 0.3], [1.2, 0.8, 0.1],
                               [-0.5, 0.2, 2.2], [0.1, 2.0, -0.3], [0.3, 0.1, 0.9]])
        y_true = torch.tensor([0, 1, 1, 2, 1, 0])

        probs = torch.softmax(logits, dim=1)
        y_pred = probs.argmax(dim=1)
        print(y_pred.tolist())                                   # [0, 1, 0, 2, 1, 2]
        print(round((y_pred == y_true).float().mean().item(), 3))   # 0.667 ← accuracy

        k = 3
        cm = torch.zeros(k, k, dtype=torch.long)                 # rows = true class, cols = predicted
        for t, p in zip(y_true, y_pred):
            cm[t, p] += 1
        print(cm.tolist())                                       # [[1, 0, 1], [1, 2, 0], [0, 0, 1]]

        tp = cm.diag().float()
        precision = tp / cm.sum(dim=0).clamp(min=1)              # per predicted column
        recall = tp / cm.sum(dim=1).clamp(min=1)                 # per true row
        print([round(v, 2) for v in precision.tolist()], [round(v, 2) for v in recall.tolist()])   # [0.5, 1.0, 0.5] [0.5, 0.67, 1.0]

        top2 = logits.topk(2, dim=1).indices
        print(round((top2 == y_true[:, None]).any(dim=1).float().mean().item(), 3))   # 1.0 ← top-2 accuracy
    ''')
    yield table(
        ["Task", "Metrics"],
        ["Classification", "Accuracy, precision/recall/F1 (per class, macro/weighted), ROC-AUC, top-k accuracy, confusion matrix"],
        ["Regression", "MAE, RMSE, R²"],
        ["Detection / segmentation", "mAP (mean average precision), IoU, Dice"],
        ["Language models", "Perplexity = `exp(mean cross-entropy)`, plus task benchmarks"],
        ["Generation", "FID (images), BLEU/ROUGE (text), human or LLM-judge evaluation"],
    )
    yield code('''
        import math
        mean_ce = 2.0                     # average cross-entropy per token, in nats
        print(round(math.exp(mean_ce), 2))   # 7.39 ← perplexity: as unsure as choosing among ~7.4 tokens
    ''')
    yield section("Beyond one number", "zoom-check")
    yield ul(
        "**Calibration** — does 90% confidence mean right 90% of the time? Deep nets are often over-confident; temperature scaling on the validation set fixes much of it.",
        "**Slices** — accuracy per class, per demographic, per data source; averages hide failures.",
        "**Error analysis** — look at the worst mistakes (see **Error Analysis** in the Machine Learning notes).",
        "**Variance** — rerun with a few seeds; differences smaller than seed-to-seed noise aren't real.",
        "**Cost** — latency, memory and throughput at inference matter as much as accuracy in production.",
    )
    yield qa("Why is accuracy misleading on imbalanced data?",
             "If 99% of transactions are legitimate, predicting “legit” for everything scores 99% while catching zero fraud. Use per-class precision/recall, F1, PR-AUC and a confusion matrix instead.")
    yield qa("What is perplexity?",
             "The exponential of the average per-token cross-entropy of a language model. It's the effective number of equally likely choices the model is torn between at each step — lower is better.")
