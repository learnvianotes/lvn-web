"""Build content-src/legacy-html/java/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/java/build.py

Edit the g*_*.py topic modules, not the generated HTML. Every Java sample is compiled and run with
JDK 21 (`java -ea File.java`); the build fails if one errors or prints anything but its `out`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # shared kit.py

import kit
import g1_basics, g2_core, g3_oop, g4_inheritance, g5_types, g6_exceptions_generics  # noqa: F401,E402
import g7_collections, g8_functional, g9_concurrency, g10_jvm, g11_interview  # noqa: F401,E402  (register topics, in order)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "java" / "index.html"
kit.build(out, "Java")
