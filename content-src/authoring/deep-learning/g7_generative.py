from kit import *

G = "Generative Models"


@topic(G, "autoencoders-vae", "Autoencoders & VAEs", "arrows-minimize")
def _():
    yield lead("An autoencoder squeezes its input through a narrow bottleneck and learns to rebuild it — so the bottleneck must capture what matters. A variational autoencoder (VAE) makes that bottleneck a smooth probability space you can sample new data from.")
    yield flow("Input x", "Encoder", "Latent code z (small)", "Decoder", "Reconstruction x̂")
    yield section("A plain autoencoder", "arrows-minimize")
    yield p("Trained only to minimise reconstruction error `‖x − x̂‖²` — no labels needed (self-supervised). Here the 10-D data secretly lives on a 2-D plane, and a 2-unit bottleneck is enough to rebuild it:")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        basis = torch.randn(2, 10)
        X = torch.randn(512, 2) @ basis                   # 512 points in 10-D that lie on a 2-D plane

        encoder = nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 2))
        decoder = nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Linear(32, 10))
        params = list(encoder.parameters()) + list(decoder.parameters())
        opt = torch.optim.Adam(params, lr=1e-2)

        for step in range(1000):
            loss = ((decoder(encoder(X)) - X) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()

        print(encoder(X).shape)                                 # torch.Size([512, 2]) ← 10 numbers compressed to 2
        print(round(X.var().item(), 2), loss.item() < 0.05)     # 2.46 True ← data variance vs reconstruction error
    ''')
    yield table(
        ["Use", "How"],
        ["Dimensionality reduction", "Use `z` as compact features (a non-linear PCA)"],
        ["Denoising", "Train on noisy inputs to reconstruct clean ones"],
        ["Anomaly detection", "Normal data reconstructs well; high reconstruction error flags anomalies"],
        ["Pretraining / compression", "Learn features from unlabelled data; latent space for diffusion models (Stable Diffusion's VAE)"],
    )
    yield warn("A plain autoencoder's latent space has gaps: decoding a random `z` usually gives garbage. It compresses, but it isn't a generator.")
    yield section("Variational autoencoder", "chart-dots-3")
    yield p("The VAE encoder outputs a **distribution** — a mean `μ` and a standard deviation `σ` per latent dimension. We sample `z` from it, decode, and add a penalty that keeps every such distribution close to a standard normal `N(0, I)`. The latent space becomes smooth and filled in, so decoding `z ~ N(0, I)` produces new, plausible data.")
    yield formula("loss = reconstruction(x, x̂) + KL( N(μ, σ²) ‖ N(0, 1) )        KL = ½ Σ ( μ² + σ² − log σ² − 1 )")
    yield define("Reparameterisation trick", "sampling isn't differentiable, so write `z = μ + σ ⊙ ε` with `ε ~ N(0, I)`. The randomness sits in `ε`; gradients flow through `μ` and `σ`.")
    yield code('''
        import torch
        from torch import nn
        import torch.nn.functional as F

        class VAE(nn.Module):
            def __init__(self, d_in=784, d_hidden=256, d_latent=16):
                super().__init__()
                self.enc = nn.Sequential(nn.Linear(d_in, d_hidden), nn.ReLU())
                self.mu = nn.Linear(d_hidden, d_latent)
                self.log_var = nn.Linear(d_hidden, d_latent)       # predict log σ² — any real number is valid
                self.dec = nn.Sequential(nn.Linear(d_latent, d_hidden), nn.ReLU(), nn.Linear(d_hidden, d_in))

            def forward(self, x):
                h = self.enc(x)
                mu, log_var = self.mu(h), self.log_var(h)
                z = mu + torch.exp(0.5 * log_var) * torch.randn_like(mu)   # reparameterisation
                return self.dec(z), mu, log_var

        def vae_loss(logits, x, mu, log_var):
            recon = F.binary_cross_entropy_with_logits(logits, x, reduction="sum") / len(x)
            kl = 0.5 * (mu ** 2 + log_var.exp() - log_var - 1).sum() / len(x)
            return recon + kl, kl

        torch.manual_seed(0)
        vae = VAE()
        x = torch.rand(8, 784)                                # a batch of 8 "images" with pixels in [0, 1]
        logits, mu, log_var = vae(x)
        loss, kl = vae_loss(logits, x, mu, log_var)
        print(logits.shape, mu.shape)                         # torch.Size([8, 784]) torch.Size([8, 16])
        print(loss.item() > 0, kl.item() >= 0)                # True True

        new_images = torch.sigmoid(vae.dec(torch.randn(4, 16)))   # generate: decode samples from the prior
        print(new_images.shape)                               # torch.Size([4, 784])
    ''')
    yield code('''
        import numpy as np

        kl = lambda mu, sigma: 0.5 * np.sum(mu ** 2 + sigma ** 2 - np.log(sigma ** 2) - 1)
        print(kl(np.array([0.0]), np.array([1.0])))            # 0.0 ← already N(0, 1): no penalty
        print(round(kl(np.array([2.0]), np.array([0.5])), 3))  # 2.318 ← far from N(0, 1): penalised
    ''')
    yield note("The two terms pull against each other: reconstruction wants distinct, precise codes; KL wants everything to look like `N(0, 1)`. That's why VAE samples tend to be slightly blurry — and why β-VAE adds a weight on the KL term to trade one for the other.")
    yield qa("Autoencoder vs VAE?",
             "An autoencoder maps each input to a single point and is trained only to reconstruct — good for compression and anomaly detection, but its latent space has holes. A VAE maps each input to a distribution and adds a KL penalty toward `N(0, I)`, giving a continuous latent space you can sample from to generate new data.")
    yield qa("What is the reparameterization trick?",
             "Writing a sample as `z = μ + σ·ε` with `ε` drawn from a fixed `N(0, 1)`. The random draw no longer depends on the parameters, so backpropagation can compute gradients with respect to `μ` and `σ`.")


@topic(G, "gans", "GANs", "swords")
def _():
    yield lead("A generative adversarial network trains two networks against each other: a generator that turns random noise into fake samples, and a discriminator that tries to tell fakes from real data. Each improves by beating the other.")
    yield flow("Noise z", "Generator G", "Fake sample G(z)", "Discriminator D ← also sees real data", "Real or fake?")
    yield formula("min_G max_D   E[ log D(x) ] + E[ log(1 − D(G(z))) ]")
    yield steps(
        ("Train D", "On a batch of real data (label 1) and generated data (label 0): ordinary binary classification."),
        ("Train G", "Generate a batch and label it **real**; backprop through D (frozen for this step) into G. G improves when it fools D."),
        ("Alternate", "Repeat. At the ideal equilibrium, fakes match the data distribution and D outputs 0.5 everywhere."),
    )
    yield section("A GAN in 1-D", "code")
    yield p("Real data: numbers drawn from `N(4, 1.25²)`. The generator starts out producing values near 0 and must learn to imitate them.")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        real_data = lambda n: torch.randn(n, 1) * 1.25 + 4.0

        G = nn.Sequential(nn.Linear(1, 16), nn.ReLU(), nn.Linear(16, 1))                # noise → sample
        D = nn.Sequential(nn.Linear(1, 16), nn.LeakyReLU(0.2), nn.Linear(16, 1))        # sample → real/fake logit
        opt_g = torch.optim.Adam(G.parameters(), lr=1e-3, betas=(0.5, 0.999))
        opt_d = torch.optim.Adam(D.parameters(), lr=1e-3, betas=(0.5, 0.999))
        bce = nn.BCEWithLogitsLoss()
        ones, zeros = torch.ones(64, 1), torch.zeros(64, 1)

        with torch.no_grad():
            print(round(G(torch.randn(10000, 1)).mean().item(), 1))    # 0.0 ← before training

        for step in range(3000):
            real, fake = real_data(64), G(torch.randn(64, 1))
            loss_d = bce(D(real), ones) + bce(D(fake.detach()), zeros)   # detach: don't update G here
            opt_d.zero_grad(); loss_d.backward(); opt_d.step()

            loss_g = bce(D(fake), ones)                                  # G wants D to say "real"
            opt_g.zero_grad(); loss_g.backward(); opt_g.step()

        with torch.no_grad():
            samples = G(torch.randn(10000, 1))
        print(round(samples.mean().item(), 1), round(samples.std().item(), 1))   # 4.0 0.5 ← mean learned; spread too narrow
    ''')
    yield p("The generator found the right centre but its samples are too concentrated (std 0.5 instead of 1.25) — a mild form of **mode collapse**: producing a narrow slice of plausible outputs is enough to fool this discriminator. Real GANs need care to avoid it.")
    yield section("Why GANs are hard to train", "alert-triangle")
    yield table(
        ["Problem", "What happens", "Remedies"],
        ["Mode collapse", "G produces only a few kinds of output", "Minibatch discrimination, Wasserstein loss, unrolled GANs"],
        ["Non-convergence", "G and D oscillate instead of settling", "Lower LRs, Adam with β₁ = 0.5, two-timescale updates"],
        ["Vanishing G gradient", "D wins too easily, `log(1 − D(G(z)))` saturates", "Non-saturating loss (train G to maximise `log D(G(z))`, as above)"],
        ["Hard to evaluate", "No likelihood to report", "FID, Inception Score, human evaluation"],
    )
    yield cards(
        ("DCGAN", "Conv generator/discriminator with BatchNorm — the first stable image GAN recipe.", "photo"),
        ("WGAN / WGAN-GP", "Wasserstein distance + gradient penalty: smoother, more informative gradients.", "ruler-measure"),
        ("StyleGAN", "Style-based generator; photorealistic faces at 1024×1024.", "user"),
        ("CycleGAN / pix2pix", "Image-to-image translation: horses ↔ zebras, sketches → photos.", "arrows-exchange"),
        cols=2,
    )
    yield qa("How does a GAN work?",
             "Two networks play a minimax game. The generator maps random noise to samples; the discriminator classifies samples as real or generated. The discriminator is trained to classify correctly, the generator to make the discriminator wrong. Over training, generated samples become harder to distinguish from real data.")
    yield qa("What is mode collapse?",
             "The generator learns to produce only a small variety of outputs (one kind of face, one digit) because those reliably fool the discriminator, ignoring the rest of the data distribution.")


@topic(G, "diffusion-models", "Diffusion Models", "sparkles")
def _():
    yield lead("A diffusion model learns to reverse a gradual noising process. Training: add noise to real data and teach a network to predict that noise. Generation: start from pure noise and remove it step by step. It's the engine behind Stable Diffusion, DALL·E 3 and most image and video generators.")
    yield flow("Image x₀", "add a little noise … ×T", "Pure noise x_T", "denoise step by step (learned)", "New image")
    yield section("The forward (noising) process", "arrow-right")
    yield p("Each step mixes in a little Gaussian noise according to a schedule `β₁ … β_T`. Conveniently, you can jump straight to any step `t` in closed form — no need to loop:")
    yield formula("x_t = √ᾱ_t · x₀ + √(1 − ᾱ_t) · ε        ε ~ N(0, I),   ᾱ_t = Π (1 − β_s)")
    yield code('''
        import numpy as np

        T = 1000
        betas = np.linspace(1e-4, 0.02, T)          # the original DDPM linear schedule
        alpha_bar = np.cumprod(1 - betas)

        for_steps = {t: round(float(np.sqrt(alpha_bar[t])), 3) for t in (0, 250, 500, 999)}
        print(for_steps)          # {0: 1.0, 250: 0.722, 500: 0.279, 999: 0.006} ← how much of the original signal remains

        rng = np.random.default_rng(0)
        x0 = np.array([1.0, -1.0, 0.5])
        t = 500
        xt = np.sqrt(alpha_bar[t]) * x0 + np.sqrt(1 - alpha_bar[t]) * rng.normal(size=3)
        print(xt.round(2).tolist())                 # [0.4, -0.41, 0.75] ← x₀ at step 500: mostly noise
    ''')
    yield section("Training: predict the noise", "target-arrow")
    yield formula("loss = ‖ ε − ε_θ(x_t, t) ‖²        (t random, ε random, x₀ from the data)")
    yield p("That's the whole objective: a plain mean-squared error. The network (a U-Net or a Transformer — “DiT”) takes the noisy input and the step `t`, and guesses the noise that was added. A toy version on 1-D data — a mixture of two bumps at −2 and +2:")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        T = 100
        betas = torch.linspace(1e-4, 0.1, T)
        alphas, alpha_bar = 1 - betas, torch.cumprod(1 - betas, dim=0)
        data = lambda n: torch.where(torch.rand(n, 1) < 0.5, -2.0, 2.0) + 0.3 * torch.randn(n, 1)

        model = nn.Sequential(nn.Linear(2, 64), nn.SiLU(), nn.Linear(64, 64), nn.SiLU(), nn.Linear(64, 1))
        opt = torch.optim.Adam(model.parameters(), lr=2e-3)

        for step in range(3000):                                      # training
            x0 = data(256)
            t = torch.randint(0, T, (256, 1))
            eps = torch.randn_like(x0)
            xt = alpha_bar[t].sqrt() * x0 + (1 - alpha_bar[t]).sqrt() * eps   # jump to step t
            loss = ((model(torch.cat([xt, t / T], dim=1)) - eps) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()

        with torch.no_grad():                                         # sampling (DDPM)
            x = torch.randn(2000, 1)                                  # start from pure noise
            for t in reversed(range(T)):
                eps_hat = model(torch.cat([x, torch.full_like(x, t / T)], dim=1))
                x = (x - betas[t] / (1 - alpha_bar[t]).sqrt() * eps_hat) / alphas[t].sqrt()
                if t > 0:
                    x = x + betas[t].sqrt() * torch.randn_like(x)     # a little fresh noise each step

        print(round(alpha_bar[-1].item(), 3))                         # 0.006 ← x_T is essentially pure noise
        print(round((x < 0).float().mean().item(), 2))                # 0.49 ← about half the samples in each bump
        print(round(x[x < 0].mean().item(), 1), round(x[x > 0].mean().item(), 1))   # -2.0 2.0 ← centred on the two modes
    ''')
    yield section("Making it practical", "adjustments")
    yield table(
        ["Idea", "What it does"],
        ["DDIM & faster samplers", "Deterministic updates that skip steps: 20–50 steps instead of 1000"],
        ["Latent diffusion", "Diffuse in a VAE's small latent space instead of pixels — much cheaper (Stable Diffusion)"],
        ["Text conditioning", "Feed a text encoder's embeddings to the denoiser via cross-attention"],
        ["Classifier-free guidance", "`ε = ε_uncond + w · (ε_cond − ε_uncond)`, `w` ≈ 3–8: follow the prompt more strongly"],
        ["Distillation / consistency models", "Few-step or one-step generation from a trained diffusion model"],
    )
    yield section("Comparing generative models", "scale")
    yield table(
        ["", "VAE", "GAN", "Diffusion"],
        ["Sample quality", "Blurry", "Sharp", "**Sharp and diverse**"],
        ["Diversity / mode coverage", "Good", "Mode collapse risk", "Good"],
        ["Training", "Stable", "Unstable (adversarial)", "Stable (simple MSE)"],
        ["Sampling speed", "One pass", "One pass", "Many steps (slow) — samplers help"],
        ["Likelihood / latent", "Yes / yes", "No / noise vector", "Approximate / no compact latent"],
    )
    yield note("The **GenAI** notes (Diffusion & GANs) cover these models from the product side; the key mechanical idea is simply: learn to denoise at every noise level, then chain the denoising steps.")
    yield qa("How do diffusion models generate images?",
             "They're trained to predict the noise added to real images at random noise levels. To generate, start from pure Gaussian noise and repeatedly subtract the predicted noise (plus a little fresh noise), moving from step T to 0 until a clean image remains; text prompts steer each step through cross-attention and classifier-free guidance.")
    yield qa("Why did diffusion models overtake GANs for image generation?",
             "Their training objective is a stable regression loss (no adversarial game), they cover the data distribution without mode collapse, and they scale well with data and compute. The main drawback — slow multi-step sampling — was largely solved by better samplers, latent diffusion and distillation.")
