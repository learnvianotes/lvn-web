"""Build content-src/legacy-html/artificial_intelligence/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/artificial-intelligence/build.py

Standard library only — no venv needed. Every example is tiny and seeds `random`, so outputs are stable.

Edit the g*_*.py topic modules, not the generated HTML. The build fails if any code sample raises
or if a `print(...)  # expected` comment doesn't match what the code really prints.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # shared kit.py

import kit  # noqa: E402
import g1_foundations, g2_search, g3_local_search, g4_games, g5_csp  # noqa: F401,E402  (register topics,
import g6_logic, g7_uncertainty, g8_ai_today  # noqa: F401,E402                            in sidebar order)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "legacy-html" / "artificial_intelligence" / "index.html"
kit.build(out.resolve(), "Artificial Intelligence")
