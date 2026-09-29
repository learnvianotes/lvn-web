"""Build content-src/legacy-html/machine_learning_ai/index.html (subject "Machine Learning", catalog id `ml-ai`)
from the topic modules, verifying every snippet.

Uses the Data Science virtualenv (NumPy, pandas, scikit-learn, SciPy, matplotlib) — no extra installs:

    content-src/authoring/data-science/.venv/bin/python content-src/authoring/machine-learning/build.py

Edit the g*_*.py topic modules, not the generated HTML. The build fails if any code sample raises or if a
`print(...)  # expected` comment doesn't match what the code really prints. Examples use tiny built-in or
synthetic datasets with fixed seeds, so the whole build runs in well under a minute.

Topic ids are permanent (learner progress is keyed on them). The 12 ids of the original notes are kept:
data_modeling, problem_formulation, data_collection, train_test, modeling_approaches, error_analysis,
evaluation_metrics, common_pitfalls, stat_significance, ml_pipeline, ai_ethics, interview_scenarios.
AUDIT.md lists the mistakes found in the original notes and how they were corrected.
"""
import os
import sys
import tempfile
from pathlib import Path

# Before anything imports matplotlib: render plots off-screen (a GUI window must never open).
os.environ["MPLBACKEND"] = "Agg"
os.environ.setdefault("OMP_NUM_THREADS", "1")    # before NumPy/sklearn load: identical results on every machine

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # shared kit.py

missing = []
for mod in ("numpy", "pandas", "sklearn", "scipy", "matplotlib"):
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)
if missing:
    sys.exit(f"Missing libraries: {', '.join(missing)} — run this with content-src/authoring/data-science/.venv/bin/python "
             f"(see the setup at the top of data-science/build.py)")

import kit  # noqa: E402
import g01_foundations, g02_data, g03_core, g04_supervised, g05_unsupervised  # noqa: F401,E402  (register topics,
import g06_evaluation, g07_statistics, g08_special, g09_production, g10_interview  # noqa: F401,E402  in sidebar order)


def env():
    import matplotlib
    import warnings
    matplotlib.use("Agg", force=True)                # plots render off-screen; plt.show() is a no-op
    warnings.filterwarnings("ignore", message=".*non-interactive.*")
    os.chdir(tempfile.mkdtemp(prefix="lvn-ml-"))     # examples that write files (model.joblib) do it in a scratch folder


out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "legacy-html" / "machine_learning_ai" / "index.html"
kit.build(out.resolve(), "Machine Learning", env_setup=env)
