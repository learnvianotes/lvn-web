from kit import *

G = "Convolutional Networks"


@topic(G, "convolutions", "Convolutions, Padding, Stride & Pooling", "grid-dots")
def _():
    yield lead("A convolutional layer slides small learned filters over an image. Each filter detects one local pattern (an edge, a texture) everywhere in the image, using the same few weights at every position.")
    yield section("Why not a dense layer?", "question-mark")
    yield cards(
        ("Locality", "Nearby pixels are related; a 3×3 filter looks only at a small neighbourhood.", "focus-2"),
        ("Weight sharing", "The same filter is used at every position — far fewer parameters than connecting every pixel to every unit.", "copy"),
        ("Translation equivariance", "Shift the input and the feature map shifts the same way: a cat is detected wherever it is.", "arrows-move"),
        ("Hierarchy", "Stacked layers see larger regions: edges → textures → parts → objects.", "stack-2"),
        cols=2,
    )
    yield section("The operation", "math")
    yield p("At each position, multiply the filter element-wise with the patch underneath and sum (deep-learning “convolution” is technically cross-correlation — the filter isn't flipped).")
    yield code('''
        import numpy as np

        def conv2d(img, k):
            kh, kw = k.shape
            out = np.zeros((img.shape[0] - kh + 1, img.shape[1] - kw + 1))
            for i in range(out.shape[0]):
                for j in range(out.shape[1]):
                    out[i, j] = np.sum(img[i:i + kh, j:j + kw] * k)
            return out

        img = np.array([[0, 0, 0, 9, 9, 9]] * 5, dtype=float)    # dark left half, bright right half
        vertical_edge = np.array([[-1, 0, 1],
                                  [-1, 0, 1],
                                  [-1, 0, 1]], dtype=float)     # Sobel-like filter
        out = conv2d(img, vertical_edge)
        print(out.shape)            # (3, 4) ← 5×6 input, 3×3 filter
        print(out[0].tolist())      # [0.0, 27.0, 27.0, 0.0] ← fires only where brightness changes
    ''')
    yield section("Output size: padding and stride", "ruler")
    yield formula("out = ⌊ (n + 2p − k) / s ⌋ + 1        n = input size, k = kernel, p = padding, s = stride")
    yield table(
        ["Setting", "Effect"],
        ["Padding `p = (k−1)/2` (“same”)", "Output keeps the input size (stride 1) — edges get processed too"],
        ["No padding (“valid”)", "Output shrinks by `k − 1`"],
        ["Stride 2", "Moves the filter 2 pixels at a time — roughly halves height and width"],
        ["Dilation `d`", "Spreads the filter taps out — larger view, same parameters"],
    )
    yield code('''
        import torch
        from torch import nn

        out_size = lambda n, k, p=0, s=1: (n + 2 * p - k) // s + 1
        print(out_size(32, 3), out_size(32, 3, p=1), out_size(32, 3, p=1, s=2), out_size(224, 7, p=3, s=2))   # 30 32 16 112

        x = torch.randn(8, 3, 32, 32)                    # (batch, channels, height, width)
        conv = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1, stride=2)
        print(conv(x).shape)                             # torch.Size([8, 16, 16, 16])
        print(conv.weight.shape, conv.bias.shape)        # torch.Size([16, 3, 3, 3]) torch.Size([16]) ← 16 filters, each 3×3×3
        print(sum(p.numel() for p in conv.parameters()))   # 448 ← 16·(3·3·3) + 16
    ''')
    yield formula("conv parameters = C_out × (C_in × k × k) + C_out        — independent of the image size")
    yield note("Each filter spans **all** input channels: a 3×3 filter on an RGB image has 3×3×3 = 27 weights. The layer's output has one channel (feature map) per filter. Compare: a dense layer from a 32×32×3 image to 16×16×16 outputs would need about 12.6 million weights; this conv has 448.")
    yield section("Pooling", "arrows-minimize")
    yield code('''
        import torch
        from torch import nn

        x = torch.tensor([[[[1.0, 3.0, 2.0, 0.0],
                            [4.0, 2.0, 1.0, 1.0],
                            [0.0, 1.0, 5.0, 6.0],
                            [2.0, 2.0, 7.0, 8.0]]]])            # (1, 1, 4, 4)
        print(nn.MaxPool2d(2)(x).squeeze().tolist())          # [[4.0, 2.0], [2.0, 8.0]] ← max of each 2×2 block
        print(nn.AvgPool2d(2)(x).squeeze().tolist())          # [[2.5, 1.0], [1.25, 6.5]]
        print(nn.AdaptiveAvgPool2d(1)(x).flatten().tolist())  # [2.8125] ← global average pooling
    ''')
    yield p("Pooling shrinks feature maps (less compute, bigger receptive field) and adds a little tolerance to small shifts. It has **no parameters**. Modern CNNs often use stride-2 convolutions instead, and end with **global average pooling** — one number per channel — before the classifier.")
    yield section("Receptive field", "focus-centered")
    yield p("The receptive field is the patch of the input that can influence one output unit. Each 3×3 conv (stride 1) adds 2 pixels; each stride multiplies how fast later layers grow it.")
    yield code('''
        def receptive_field(layers):          # layers: list of (kernel, stride)
            rf, jump = 1, 1
            for k, s in layers:
                rf += (k - 1) * jump
                jump *= s
            return rf

        print(receptive_field([(3, 1)] * 2))                 # 5 ← two 3×3 convs see 5×5 (like one 5×5)
        print(receptive_field([(3, 1)] * 3))                 # 7 ← three see 7×7
        print(receptive_field([(3, 1), (2, 2), (3, 1), (2, 2), (3, 1)]))   # 18 ← pooling speeds growth
    ''')
    yield note("Two stacked 3×3 convs see the same 5×5 area as one 5×5 conv but use `2·9 = 18` weights per channel pair instead of 25 — and add an extra non-linearity. That's VGG's key insight.")
    yield qa("How do you compute the output size of a conv layer?",
             "`⌊(n + 2p − k)/s⌋ + 1`. Example: 224×224 input, 7×7 kernel, padding 3, stride 2 → `⌊(224 + 6 − 7)/2⌋ + 1 = 112`.")
    yield qa("Why are CNNs better than MLPs for images?",
             "They exploit image structure: local connectivity and weight sharing cut parameters by orders of magnitude, translation equivariance means a pattern is recognised anywhere, and stacking builds a feature hierarchy. An MLP on raw pixels has to learn every pattern separately at every position.")


@topic(G, "cnn-architectures", "CNN Architectures & ResNet", "building")
def _():
    yield lead("The classic CNNs trace how the field learned to go deeper: bigger datasets and GPUs (AlexNet), small stacked filters (VGG), and finally skip connections (ResNet) that made 100+ layers trainable.")
    yield table(
        ["Model", "Year", "Key idea", "Depth / params"],
        ["LeNet-5", "1998", "Conv → pool → conv → pool → dense; read handwritten digits", "5 layers, 60 K"],
        ["AlexNet", "2012", "ReLU, dropout, data augmentation, trained on GPUs — won ImageNet by a wide margin", "8 layers, 60 M"],
        ["VGG-16", "2014", "Only 3×3 convs, stacked deep; simple and uniform", "16 layers, 138 M"],
        ["GoogLeNet / Inception", "2014", "Parallel 1×1, 3×3, 5×5 branches; 1×1 convs to cut channels", "22 layers, 7 M"],
        ["ResNet", "2015", "**Residual connections** `y = F(x) + x`", "18–152 layers, 11–60 M"],
        ["MobileNet / EfficientNet", "2017–19", "Depthwise-separable convs; scaling width/depth/resolution together", "Few M, for phones"],
        ["ConvNeXt, ViT", "2020–22", "Transformer ideas for vision: patches + attention (ViT), modernised CNNs", "—"],
    )
    yield section("A small CNN, shape by shape", "stack-2")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        model = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(),   # 28×28
            nn.MaxPool2d(2),                                                  # → 14×14
            nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),                                                  # → 7×7
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),                            # → 32 numbers
            nn.Linear(32, 10),                                                # → 10 class logits
        )
        x = torch.randn(4, 1, 28, 28)             # a batch of 4 MNIST-sized images
        shapes = []
        for layer in model:
            x = layer(x)
            if isinstance(layer, (nn.MaxPool2d, nn.Flatten, nn.Linear)):
                shapes.append(tuple(x.shape))
        print(shapes)                             # [(4, 16, 14, 14), (4, 32, 7, 7), (4, 32), (4, 10)]
        print(sum(p.numel() for p in model.parameters()))   # 5226
    ''')
    yield p("The pattern — conv/BN/ReLU blocks, downsampling that halves the resolution while channels double, global pooling, a linear head — describes most CNNs.")
    yield section("Residual connections", "arrow-back-up")
    yield define("Residual block", "instead of learning `H(x)` directly, the block learns the change `F(x) = H(x) − x` and outputs `F(x) + x`. If the best thing is to do nothing, it only has to push `F` to zero.")
    yield flow("x", "conv → BN → ReLU → conv → BN = F(x)", "F(x) + x", "ReLU")
    yield code('''
        import torch
        from torch import nn

        class ResidualBlock(nn.Module):
            def __init__(self, channels):
                super().__init__()
                self.body = nn.Sequential(
                    nn.Conv2d(channels, channels, 3, padding=1, bias=False), nn.BatchNorm2d(channels), nn.ReLU(),
                    nn.Conv2d(channels, channels, 3, padding=1, bias=False), nn.BatchNorm2d(channels),
                )

            def forward(self, x):
                return torch.relu(self.body(x) + x)          # the skip connection

        torch.manual_seed(0)
        block = ResidualBlock(8)
        x = torch.randn(2, 8, 16, 16)
        print(block(x).shape)                                # torch.Size([2, 8, 16, 16]) ← shape preserved so x can be added

        nn.init.zeros_(block.body[4].weight)                 # zero the last BN's scale → F(x) = 0
        print(torch.allclose(block(x), torch.relu(x)))       # True ← the block passes x straight through
    ''')
    yield p("Why it works: the gradient of `F(x) + x` with respect to `x` is `∂F/∂x + 1`. The **+1** path carries gradients straight back through any number of blocks, so early layers keep learning. When the shapes differ (more channels, stride 2), the shortcut uses a 1×1 conv to match them.")
    yield cards(
        ("1×1 convolutions", "Mix channels at each pixel without looking at neighbours — cheap way to shrink or expand channel count (bottlenecks in Inception/ResNet-50).", "arrows-diagonal-minimize"),
        ("Depthwise-separable conv", "A per-channel 3×3 conv followed by a 1×1 conv: ~8–9× fewer operations than a full 3×3 conv (MobileNet).", "bolt"),
        cols=2,
    )
    yield qa("Why do residual connections help train very deep networks?",
             "They give gradients an identity path (the `+x`), so they don't vanish through many layers, and they make it easy for extra layers to do nothing harmful (learn `F = 0`). Plain 56-layer nets trained worse than 20-layer ones; ResNets kept improving past 100 layers.")
    yield qa("What does a 1×1 convolution do?",
             "It's a linear layer applied at every pixel across channels: it changes the number of channels (e.g. 256 → 64) and mixes information between them, cheaply, without changing the spatial size.")


@topic(G, "transfer-learning", "Transfer Learning & Fine-Tuning", "transfer")
def _():
    yield lead("Don't train from scratch when someone has already trained a model on millions of examples. Reuse its learned features, replace the head for your task, and fine-tune — you need far less data and compute.")
    yield flow("Pretrained backbone (e.g. ImageNet ResNet)", "Replace the head", "Train head (backbone frozen)", "Optionally unfreeze & fine-tune with a low LR")
    yield table(
        ["Your data", "Similar to pretraining data", "Different from it"],
        ["**Small**", "Feature extraction: freeze everything, train only the head", "Freeze early layers, fine-tune later ones carefully"],
        ["**Large**", "Fine-tune the whole network", "Fine-tune everything (or train longer / from scratch)"],
    )
    yield section("Freezing and replacing the head", "lock")
    yield p("Here a small network stands in for a pretrained backbone; with a real one the code is identical.")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        backbone = nn.Sequential(                              # pretend these weights came from ImageNet
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
        )
        for p in backbone.parameters():
            p.requires_grad = False                            # freeze: no gradients, no updates

        model = nn.Sequential(backbone, nn.Linear(64, 5))      # new head for our 5 classes
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in model.parameters())
        print(trainable, total)                                # 325 19717 ← only the head trains

        optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=1e-3)
        print(model(torch.randn(2, 3, 32, 32)).shape)          # torch.Size([2, 5])
    ''')
    yield section("Fine-tuning with smaller learning rates for the backbone", "adjustments")
    yield code('''
        import torch
        from torch import nn

        backbone, head = nn.Linear(10, 10), nn.Linear(10, 2)
        optimizer = torch.optim.AdamW([
            {"params": backbone.parameters(), "lr": 1e-5},     # gentle: keep the pretrained features
            {"params": head.parameters(), "lr": 1e-3},         # the new head learns faster
        ], weight_decay=0.01)
        print([g["lr"] for g in optimizer.param_groups])       # [1e-05, 0.001]
    ''')
    yield section("With torchvision", "photo")
    yield code('''
        import torch
        from torch import nn
        from torchvision import models

        weights = models.ResNet18_Weights.DEFAULT
        model = models.resnet18(weights=weights)            # downloads ImageNet weights once
        for p in model.parameters():
            p.requires_grad = False
        model.fc = nn.Linear(model.fc.in_features, 5)       # 512 → 5 classes (new layer is trainable)
        preprocess = weights.transforms()                    # the exact resize/normalisation used in pretraining
    ''', run=False)
    yield dodont("Use the pretrained model's own preprocessing (input size, mean/std normalisation); start with a frozen backbone, then unfreeze with an LR 10–100× smaller.",
                 "Fine-tune the whole network at a large learning rate — it wrecks the pretrained features (“catastrophic forgetting”).")
    yield note("The same recipe powers NLP: take a pretrained Transformer (BERT, an LLM) and fine-tune it — fully, or with parameter-efficient methods like LoRA, covered in the **GenAI** notes (Fine-Tuning & PEFT).")
    yield qa("What is transfer learning and why does it work?",
             "Reusing a model trained on a large dataset as the starting point for a new task. Early layers learn general features (edges, textures; or syntax in language models) that are useful across tasks, so the new task only needs to learn a small head or small adjustments — with much less data and compute.")
    yield qa("Feature extraction vs fine-tuning?",
             "Feature extraction freezes the pretrained network and trains only the new head — fast, safe for small datasets. Fine-tuning also updates some or all pretrained layers (with a lower learning rate) — better accuracy when you have more data or the domain differs.")
