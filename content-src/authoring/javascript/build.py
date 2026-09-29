"""Build content-src/legacy-html/javascript/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/javascript/build.py

Edit the g*_*.py topic modules, not the generated HTML. Every `snippet("js", ...)` runs under Node
(as an ES module, main.mjs) and the build fails if it throws or prints anything other than its `out`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # shared kit.py

import kit
import g1_basics, g2_types, g3_functions, g4_arrays_objects, g5_oop, g6_collections  # noqa: F401,E402  (register topics)
import g7_async, g8_advanced, g9_platform, g10_modern, g11_interview  # noqa: F401,E402  (sidebar order = import order)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "javascript" / "index.html"
kit.build(out, "JavaScript")
