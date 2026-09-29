"""Build content-src/legacy-html/deep_learning/index.html from the topic modules, verifying every snippet.

    content-src/authoring/deep-learning/.venv/bin/python content-src/authoring/deep-learning/build.py

Needs NumPy and PyTorch (CPU is enough — every example is tiny). One-time setup (from this folder):

    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt

Edit the g*_*.py topic modules, not the generated HTML. The build fails if any code sample raises
or if a `print(...)  # expected` comment doesn't match what the code really prints. Examples seed
NumPy and PyTorch and print rounded values so the outputs are stable; the build runs PyTorch on one
CPU thread for reproducibility.
"""
import os
import sys
import tempfile
from pathlib import Path

# Before anything could import matplotlib: render off-screen (a GUI window must never open).
os.environ["MPLBACKEND"] = "Agg"

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # shared kit.py

missing = []
for mod in ("numpy", "torch"):
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)
if missing:
    sys.exit(f"Missing libraries: {', '.join(missing)} — see the setup at the top of {Path(__file__).name}")

import kit  # noqa: E402
import g1_foundations, g2_training, g3_stability, g4_pytorch, g5_cnn, g6_sequences, g7_generative, g8_interview  # noqa: F401,E402


def env():
    import warnings
    import torch
    torch.set_num_threads(1)                          # same reduction order every run → same rounded numbers
    warnings.filterwarnings("ignore")
    os.chdir(tempfile.mkdtemp(prefix="lvn-dl-"))      # examples that save checkpoints do it in a scratch folder


out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "legacy-html" / "deep_learning" / "index.html"
kit.build(out.resolve(), "Deep Learning", env_setup=env)
