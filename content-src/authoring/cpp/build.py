"""Build content-src/legacy-html/cpp/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/cpp/build.py

Edit the g*_*.py topic modules, not the generated HTML. Every C++ sample is compiled with
clang++ -std=c++20 -Wall -Wextra -Werror (+ AddressSanitizer/UBSan) and run; the build fails if a
sample doesn't compile, crashes, or prints anything other than its `out=`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # shared kit.py

import kit
import g1_start, g2_basics, g3_functions, g4_memory, g5_classes, g6_lifetime  # noqa: F401,E402  (register topics,
import g7_inheritance, g8_templates, g9_containers, g10_algorithms  # noqa: F401,E402   in sidebar order)
import g11_errors_io, g12_concurrency, g13_modern_interview  # noqa: F401,E402

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "cpp" / "index.html"
kit.build(out, "C++")
