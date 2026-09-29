"""Build content-src/legacy-html/data_science/index.html from the topic modules, verifying every snippet.

    npm run content:data-science

Needs the libraries the examples use. One-time setup (from this folder):

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python -c "import nltk; [nltk.download(p, download_dir='.venv/nltk_data') for p in ('punkt','punkt_tab','stopwords','wordnet','omw-1.4')]"

Edit the g*_*.py topic modules, not the generated HTML. The build fails if any code sample raises
or if a `print(...)  # expected` comment doesn't match what the code really prints.
Source material: the course notebooks (files, os, NumPy, pandas, web scraping, ML, NLP).
"""
import os
import sys
import tempfile
from pathlib import Path

# Before anything imports matplotlib: render plots off-screen (plt.show() must never open a window).
os.environ["MPLBACKEND"] = "Agg"

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # shared kit.py

missing = []
for mod in ("numpy", "pandas", "sklearn", "scipy", "bs4", "nltk", "spacy", "matplotlib"):
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)
if missing:
    sys.exit(f"Missing libraries: {', '.join(missing)} — see the setup at the top of {Path(__file__).name}")

import kit  # noqa: E402
import g1_files_numpy, g2_pandas_scraping, g3_ml, g4_nlp, g5_interview  # noqa: F401,E402  (register topics)


def env():
    import matplotlib
    import warnings
    matplotlib.use("Agg", force=True)                # plots render off-screen; plt.show() is a no-op
    warnings.filterwarnings("ignore", message=".*non-interactive.*")
    os.environ.setdefault("NLTK_DATA", str(HERE / ".venv" / "nltk_data"))
    os.chdir(tempfile.mkdtemp(prefix="lvn-ds-"))     # examples that write files do it in a scratch folder


out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "legacy-html" / "data_science" / "index.html"
kit.build(out.resolve(), "Data Science", env_setup=env)
