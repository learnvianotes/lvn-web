from kit import *

G = "Sequences & Transformers"


@topic(G, "rnn-lstm-gru", "RNNs, LSTM & GRU", "repeat")
def _():
    yield lead("Recurrent networks read a sequence one step at a time, carrying a hidden state that summarises everything seen so far. LSTMs and GRUs add gates so that memory survives over long sequences.")
    yield table(
        ["Pattern", "Input → output", "Example"],
        ["Many-to-one", "Sequence → one label", "Sentiment of a review, activity from sensor data"],
        ["One-to-many", "One input → sequence", "Image captioning, music generation"],
        ["Many-to-many (aligned)", "One output per step", "Part-of-speech tagging, frame labelling"],
        ["Many-to-many (seq2seq)", "Sequence → different-length sequence", "Translation, summarisation (encoder–decoder)"],
    )
    yield section("The vanilla RNN", "refresh")
    yield formula("hₜ = tanh(W_x xₜ + W_h hₜ₋₁ + b)        the same weights at every time step")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        d_in, d_h, T = 3, 4, 5
        W_x, W_h, b = rng.normal(0, 0.5, (d_in, d_h)), rng.normal(0, 0.5, (d_h, d_h)), np.zeros(d_h)
        xs = rng.normal(size=(T, d_in))            # a sequence of 5 steps, 3 features each

        h = np.zeros(d_h)
        for x_t in xs:                             # unroll through time
            h = np.tanh(x_t @ W_x + h @ W_h + b)
        print(h.shape, h.round(3).tolist())        # (4,) [0.403, -0.613, 0.626, 0.503] ← final state summarises the sequence
    ''')
    yield p("Training unrolls the loop and backpropagates through every step (**backpropagation through time**, BPTT). The gradient reaching step 1 has been multiplied by `W_h` and a tanh slope once per step — so over long sequences it vanishes (or explodes). A plain RNN effectively remembers only the last few steps.")
    yield section("LSTM and GRU", "lock-open")
    yield table(
        ["", "LSTM", "GRU"],
        ["State", "Hidden `h` + separate **cell** `c` (long-term memory)", "Hidden `h` only"],
        ["Gates", "Forget, input, output (+ candidate)", "Update, reset (+ candidate)"],
        ["Key update", "`c ← f ⊙ c + i ⊙ c̃` — additive, so gradients flow", "`h ← (1 − z) ⊙ h + z ⊙ h̃`"],
        ["Parameters", "4× a vanilla RNN", "3× a vanilla RNN"],
        ["Use", "The default for long dependencies", "Slightly faster, often as good"],
    )
    yield p("Gates are sigmoid layers (outputs between 0 and 1) that decide what to erase, what to write and what to expose. Because the cell state is updated by **addition** rather than repeated multiplication, information and gradients can travel across many steps — the forget gate set near 1 keeps a memory intact.")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        x = torch.randn(2, 7, 10)                      # (batch, time steps, features) with batch_first=True
        lstm = nn.LSTM(input_size=10, hidden_size=20, num_layers=1, batch_first=True)
        out, (h_n, c_n) = lstm(x)
        print(out.shape, h_n.shape, c_n.shape)         # torch.Size([2, 7, 20]) torch.Size([1, 2, 20]) torch.Size([1, 2, 20])
        print(torch.allclose(out[:, -1], h_n[0]))      # True ← last output = final hidden state

        count = lambda m: sum(p.numel() for p in m.parameters())
        print(count(nn.RNN(10, 20)), count(nn.GRU(10, 20)), count(lstm))   # 640 1920 2560 ← 1× : 3× : 4×
    ''')
    yield code('''
        import torch
        from torch import nn

        class SentimentLSTM(nn.Module):                 # many-to-one classifier
            def __init__(self, vocab, emb=32, hidden=64, classes=2):
                super().__init__()
                self.embed = nn.Embedding(vocab, emb, padding_idx=0)
                self.lstm = nn.LSTM(emb, hidden, batch_first=True, bidirectional=True)
                self.head = nn.Linear(2 * hidden, classes)     # forward + backward directions

            def forward(self, tokens):
                _, (h_n, _) = self.lstm(self.embed(tokens))
                return self.head(torch.cat([h_n[0], h_n[1]], dim=1))

        torch.manual_seed(0)
        model = SentimentLSTM(vocab=1000)
        print(model(torch.randint(1, 1000, (4, 12))).shape)   # torch.Size([4, 2]) ← 4 reviews of 12 tokens
    ''')
    yield warn("RNNs process steps sequentially, so they can't parallelise over time and are slow on long sequences. For most language tasks Transformers replaced them; RNNs remain useful for streaming, small on-device models and some time-series work.")
    yield qa("How does an LSTM solve the vanishing gradient problem?",
             "Its cell state is updated additively (`c = f·c + i·c̃`) and controlled by gates. When the forget gate is near 1 the gradient flows back through the cell almost unchanged, instead of being squashed by a matrix and tanh at every step.")
    yield qa("LSTM vs GRU?",
             "GRU merges the cell and hidden state and uses two gates instead of three, so it has ~25% fewer parameters and trains faster. Performance is usually similar; LSTM can be better on very long dependencies.")


@topic(G, "embeddings", "Embeddings", "vector")
def _():
    yield lead("An embedding maps each discrete item — a word, token, user or product — to a learned dense vector. Similar items end up close together, and the vectors feed straight into a network.")
    yield table(
        ["", "One-hot", "Embedding"],
        ["Size", "Vocabulary size (e.g. 50,000), all zeros but one", "Small and dense (e.g. 64–4096)"],
        ["Similarity", "Every pair equally different", "Learned: `cat` is near `dog`"],
        ["Parameters", "None", "`vocab × dim` table, trained with the model"],
    )
    yield section("An embedding layer is a lookup table", "table")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        emb = nn.Embedding(num_embeddings=5, embedding_dim=3)     # 5 tokens, 3-D vectors
        ids = torch.tensor([[1, 4, 1]])                           # a batch with one sequence of token ids
        vectors = emb(ids)
        print(vectors.shape)                                      # torch.Size([1, 3, 3]) ← (batch, sequence, dim)
        print(torch.equal(vectors[0, 0], emb.weight[1]))          # True ← row 1 of the table

        one_hot = nn.functional.one_hot(torch.tensor(4), 5).float()
        print(torch.allclose(one_hot @ emb.weight, emb.weight[4]))   # True ← same as one-hot × matrix, but cheaper
    ''')
    yield p("Mathematically, an embedding is a linear layer applied to a one-hot vector — but indexing a row is far cheaper than multiplying a 50,000-wide sparse vector. Gradients only update the rows that were used in the batch.")
    yield section("Similarity between vectors", "angle")
    yield formula("cosine similarity(a, b) = (a · b) / (‖a‖ ‖b‖)        1 = same direction, 0 = unrelated, −1 = opposite")
    yield code('''
        import numpy as np

        # toy 4-D vectors (real ones are learned and have hundreds of dimensions)
        vec = {"king":  np.array([0.9, 0.8, 0.1, 0.7]),
               "queen": np.array([0.9, 0.1, 0.8, 0.7]),
               "man":   np.array([0.1, 0.9, 0.1, 0.2]),
               "woman": np.array([0.1, 0.2, 0.8, 0.2]),
               "apple": np.array([0.0, 0.1, 0.1, -0.9])}

        cos = lambda a, b: a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
        print(round(cos(vec["king"], vec["queen"]), 2), round(cos(vec["king"], vec["apple"]), 2))   # 0.75 -0.42

        target = vec["king"] - vec["man"] + vec["woman"]         # the famous analogy
        best = max((w for w in vec if w not in ("king", "man", "woman")), key=lambda w: cos(vec[w], target))
        print(best)                                              # queen
    ''')
    yield table(
        ["Kind", "How it's learned", "Examples"],
        ["Static word embeddings", "Predict neighbouring words", "word2vec, GloVe, fastText"],
        ["Task embeddings", "End-to-end with the model (`nn.Embedding`)", "Token embeddings in every Transformer"],
        ["Contextual embeddings", "Transformer hidden states — the vector depends on the sentence", "BERT (“bank” of a river vs a bank account)"],
        ["Sentence / document embeddings", "Contrastive training on similar pairs", "Semantic search, RAG (see the **GenAI** notes)"],
        ["Entity embeddings", "Learned inside a recommender or tabular model", "Users, products, categories"],
    )
    yield note("`padding_idx=0` keeps the padding token's vector fixed at zero and excluded from updates. Embedding tables are often the largest part of small language models: 50,000 tokens × 768 dims = 38 M parameters.")
    yield qa("What is an embedding, and why not use one-hot vectors?",
             "A dense, learned vector for each discrete item. One-hot vectors are huge, sparse and make every pair of items equally distant; embeddings are compact and place related items near each other, which lets the model generalise from one item to similar ones.")


@topic(G, "attention", "Attention & Self-Attention", "eye")
def _():
    yield lead("Attention lets every position look at every other position and take a weighted average of what it finds, with weights computed from the data. It's the core operation of Transformers.")
    yield p("The analogy is a soft dictionary lookup. Each token produces a **query** (what am I looking for?), a **key** (what do I contain?) and a **value** (what I'll hand over). A query is compared with every key; the softmax of those scores says how much of each value to take.")
    yield formula("Attention(Q, K, V) = softmax( Q Kᵀ / √d_k ) V")
    yield steps(
        ("Project", "`Q = X W_Q`, `K = X W_K`, `V = X W_V` — three learned linear maps of the same input (that's what makes it *self*-attention)."),
        ("Score", "`Q Kᵀ` — dot product of every query with every key: an (n × n) matrix."),
        ("Scale", "Divide by `√d_k` so the scores don't grow with the vector size."),
        ("Mask (optional)", "Set forbidden scores to `−∞` — future tokens in a decoder, padding."),
        ("Softmax", "Row-wise: each token's weights over all tokens sum to 1."),
        ("Mix", "Multiply by `V`: each output is a weighted average of value vectors."),
    )
    yield section("From scratch", "code")
    yield code('''
        import numpy as np

        def softmax(z):
            e = np.exp(z - z.max(axis=-1, keepdims=True))
            return e / e.sum(axis=-1, keepdims=True)

        def attention(Q, K, V, mask=None):
            scores = Q @ K.T / np.sqrt(K.shape[-1])
            if mask is not None:
                scores = np.where(mask, scores, -np.inf)
            weights = softmax(scores)
            return weights @ V, weights

        rng = np.random.default_rng(0)
        n, d_model, d_k = 4, 8, 8                      # 4 tokens
        X = rng.normal(size=(n, d_model))
        W_q, W_k, W_v = (rng.normal(0, d_model ** -0.5, (d_model, d_k)) for _ in range(3))
        Q, K, V = X @ W_q, X @ W_k, X @ W_v

        out, w = attention(Q, K, V)
        print(out.shape, w.shape)                      # (4, 8) (4, 4) ← one output per token; n × n weights
        print(w.sum(axis=1).round(6).tolist())         # [1.0, 1.0, 1.0, 1.0] ← each row sums to 1

        causal = np.tril(np.ones((n, n), dtype=bool))  # token i may only look at tokens ≤ i
        _, w_causal = attention(Q, K, V, mask=causal)
        print(w_causal[2].round(2).tolist())           # [0.31, 0.34, 0.35, 0.0] ← token 2 sees tokens 0–2; token 3 is masked
        print(w_causal[0].round(2).tolist())           # [1.0, 0.0, 0.0, 0.0] ← token 0 can only attend to itself
    ''')
    yield code('''
        import numpy as np
        import torch
        import torch.nn.functional as F

        torch.manual_seed(0)
        Q, K, V = torch.randn(1, 4, 8), torch.randn(1, 4, 8), torch.randn(1, 4, 8)   # (batch, tokens, d_k)

        manual = torch.softmax(Q @ K.transpose(-2, -1) / 8 ** 0.5, dim=-1) @ V
        fused = F.scaled_dot_product_attention(Q, K, V)          # PyTorch's optimised kernel (FlashAttention on GPUs)
        print(torch.allclose(manual, fused, atol=1e-6))          # True
        first = F.scaled_dot_product_attention(Q, K, V, is_causal=True)[0, 0]
        print(torch.allclose(first, V[0, 0]))                    # True ← causal: the first token can only copy its own value
    ''')
    yield section("Why divide by √d_k?", "divide")
    yield code('''
        import numpy as np

        rng = np.random.default_rng(0)
        for_d = {}
        for d in (4, 64, 1024):
            q, k = rng.normal(size=(10000, d)), rng.normal(size=(10000, d))
            dots = (q * k).sum(axis=1)
            for_d[d] = (round(float(dots.std()), 1), round(float((dots / np.sqrt(d)).std()), 2))
        print(for_d)       # {4: (2.0, 1.0), 64: (8.1, 1.01), 1024: (32.0, 1.0)} ← raw std ≈ √d; scaled std ≈ 1
    ''')
    yield p("Dot products of random `d`-dimensional vectors have standard deviation `√d`. Large scores push softmax into saturation — nearly one-hot, with vanishing gradients. Dividing by `√d_k` keeps the scores at unit scale.")
    yield table(
        ["Variant", "Q comes from", "K, V come from", "Used in"],
        ["Self-attention", "The sequence", "The same sequence", "Encoders (BERT), decoders (GPT)"],
        ["Masked (causal) self-attention", "The sequence", "Earlier positions only", "Decoders / LLMs — no peeking at the future"],
        ["Cross-attention", "The decoder", "The encoder's output", "Translation, image captioning, diffusion text conditioning"],
    )
    yield warn("Attention compares every token with every other: time and memory grow as **O(n²)** in sequence length. Doubling the context quadruples the attention cost — the reason for FlashAttention, sparse/sliding-window attention and KV caching.")
    yield qa("Explain self-attention.",
             "Each token is projected into a query, key and value. A token's output is a weighted average of all value vectors, where the weights are the softmax of its query's (scaled) dot products with every key. This lets each token gather information from the most relevant other tokens, in parallel for the whole sequence.")
    yield qa("Why is attention better than an RNN for long sequences?",
             "Any two positions interact directly in one step (path length 1 instead of n), so long-range dependencies are easy to learn and gradients don't vanish across time; and all positions are processed in parallel on a GPU. The cost is O(n²) compute and memory in the sequence length.")


@topic(G, "transformers", "Transformers", "cube-send")
def _():
    yield lead("The Transformer (“Attention Is All You Need”, 2017) drops recurrence entirely: stacks of self-attention and feed-forward layers, with residual connections and layer norm. It powers modern language, vision and audio models.")
    yield flow("Tokens", "Embeddings + positional encoding", "N × [Multi-head attention → Add & Norm → Feed-forward → Add & Norm]", "Output head")
    yield section("Encoder, decoder, or both", "arrows-left-right")
    yield table(
        ["Type", "Attention", "Trained to", "Examples", "Good for"],
        ["Encoder-only", "Bidirectional self-attention", "Fill in masked tokens", "BERT, RoBERTa", "Classification, embeddings, extraction"],
        ["Decoder-only", "Causal self-attention", "Predict the next token", "GPT, LLaMA, Claude", "Text generation, chat — today's LLMs"],
        ["Encoder–decoder", "Encoder self-attention + decoder cross-attention", "Map input sequence → output sequence", "Original Transformer, T5, Whisper", "Translation, summarisation, speech-to-text"],
    )
    yield p("The **GenAI** notes cover the LLM side (GPT vs BERT, tokens, context windows, sampling); here we look at the machinery.")
    yield section("Positional encoding", "list-numbers")
    yield p("Attention is permutation-invariant — shuffle the tokens and each output is just shuffled too — so order must be injected. The original paper adds sinusoids of different frequencies to the embeddings; many models learn position embeddings, and modern LLMs use rotary embeddings (RoPE) applied inside attention.")
    yield formula("PE(pos, 2i) = sin(pos / 10000^(2i/d))        PE(pos, 2i+1) = cos(pos / 10000^(2i/d))")
    yield code('''
        import numpy as np

        def positional_encoding(n_positions, d):
            pos = np.arange(n_positions)[:, None]
            i = np.arange(0, d, 2)[None, :]
            angle = pos / 10000 ** (i / d)
            pe = np.zeros((n_positions, d))
            pe[:, 0::2], pe[:, 1::2] = np.sin(angle), np.cos(angle)
            return pe

        pe = positional_encoding(50, 16)
        print(pe.shape)                          # (50, 16)
        print(pe[0, :4].tolist())                # [0.0, 1.0, 0.0, 1.0] ← position 0: sin 0, cos 0, …
        print(pe[1, :4].round(3).tolist())       # [0.841, 0.54, 0.311, 0.95]
        near, far = pe[10] @ pe[11], pe[10] @ pe[40]
        print(near > far)                        # True ← nearby positions have more similar codes
    ''')
    yield section("Multi-head attention", "layout-columns")
    yield p("Instead of one attention with `d_model`-wide vectors, split into `h` heads of size `d_model / h`, attend in each independently, concatenate and project. Different heads learn different relations — one follows syntax, another coreference, another nearby tokens — at the same total cost.")
    yield formula("MultiHead(X) = Concat(head₁, …, head_h) W_O        headᵢ = Attention(X W_Qⁱ, X W_Kⁱ, X W_Vⁱ)")
    yield code('''
        import torch
        from torch import nn

        torch.manual_seed(0)
        mha = nn.MultiheadAttention(embed_dim=64, num_heads=8, batch_first=True)   # 8 heads of size 8
        x = torch.randn(2, 10, 64)                       # (batch, tokens, d_model)
        out, weights = mha(x, x, x)                      # self-attention: query = key = value = x
        print(out.shape, weights.shape)                  # torch.Size([2, 10, 64]) torch.Size([2, 10, 10]) ← weights averaged over heads
        print(sum(p.numel() for p in mha.parameters()))  # 16640 ← 4 projections of 64×64 (+ biases)
    ''')
    yield section("A Transformer block", "box")
    yield code('''
        import torch
        from torch import nn

        class TransformerBlock(nn.Module):
            """Pre-LN block, as in GPT-2 and most modern models."""
            def __init__(self, d_model=64, n_heads=4, d_ff=256, dropout=0.1):
                super().__init__()
                self.ln1, self.ln2 = nn.LayerNorm(d_model), nn.LayerNorm(d_model)
                self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
                self.ff = nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model), nn.Dropout(dropout))

            def forward(self, x, causal=True):
                n = x.shape[1]
                mask = torch.triu(torch.ones(n, n, dtype=torch.bool), diagonal=1) if causal else None   # True = blocked
                h = self.ln1(x)
                x = x + self.attn(h, h, h, attn_mask=mask, need_weights=False)[0]   # residual 1
                x = x + self.ff(self.ln2(x))                                         # residual 2
                return x

        torch.manual_seed(0)
        block = TransformerBlock()
        x = torch.randn(2, 10, 64)
        print(block(x).shape)                                   # torch.Size([2, 10, 64]) ← same shape in and out: blocks stack
        print(sum(p.numel() for p in block.parameters()))       # 49984

        layer = nn.TransformerEncoderLayer(d_model=64, nhead=4, dim_feedforward=256, batch_first=True, norm_first=True)
        encoder = nn.TransformerEncoder(layer, num_layers=6, enable_nested_tensor=False)   # built-in, 6 deep
        print(encoder(x).shape)                                 # torch.Size([2, 10, 64])
    ''')
    yield table(
        ["Component", "Role"],
        ["Multi-head self-attention", "Tokens exchange information"],
        ["Feed-forward network (FFN)", "Processes each token independently; usually 4× wider; holds most parameters"],
        ["Residual connections", "Gradient highway; each sub-layer adds a refinement"],
        ["LayerNorm (Pre-LN)", "Stable training of deep stacks"],
        ["Output head", "Linear layer to vocabulary logits (often tied to the input embedding matrix)"],
    )
    yield section("Why Transformers won", "trophy")
    yield ul(
        "**Parallel** training over all positions — unlike RNNs — so they use GPUs efficiently.",
        "**Direct long-range interactions** between any two tokens.",
        "**Scale predictably**: loss keeps falling as data, parameters and compute grow (scaling laws).",
        "**General**: the same block works on text tokens, image patches (ViT), audio frames and more.",
    )
    yield warn("Costs: attention is O(n²) in context length, and generation is sequential — one token at a time, with a KV cache storing past keys and values. Serving tricks (KV caching, quantisation, speculative decoding) are covered in the **GenAI** notes under LLM Optimization.")
    yield qa("Walk through a Transformer layer.",
             "Input vectors (token embeddings + positions) go through LayerNorm and multi-head self-attention, whose output is added back to the input (residual). Then another LayerNorm and a position-wise feed-forward network (two linear layers with GELU), again added residually. The shape is unchanged, so N such layers stack.")
    yield qa("Why do Transformers need positional encodings?",
             "Self-attention treats the input as a set — it has no notion of order. Positional encodings (sinusoidal, learned, or rotary) inject each token's position so “dog bites man” differs from “man bites dog”.")
    yield qa("What is the purpose of multiple attention heads?",
             "Each head attends in its own lower-dimensional subspace, so the layer can capture several kinds of relationships at once (syntax, coreference, position) for about the same cost as one full-width head.")
