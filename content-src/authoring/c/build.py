"""Build content-src/legacy-html/c/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/c/build.py

Edit the g*_*.py topic modules, not the generated HTML. Every C sample is compiled with
clang -std=c17 -Wall -Wextra -Werror plus AddressSanitizer/UBSan and its output is checked.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # shared kit.py

import kit
import g1_basics, g2_types, g3_control, g4_arrays, g5_pointers  # noqa: F401,E402  (register topics)
import g6_memory, g7_structs, g8_ds, g9_system, g10_advanced  # noqa: F401,E402  (sidebar order)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "c" / "index.html"
kit.build(out, "C")
