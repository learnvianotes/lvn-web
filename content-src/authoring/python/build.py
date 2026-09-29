"""Build content-src/legacy-html/python/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/python/build.py      (or: npm run content:python)

Edit the g*_*.py topic modules, not the generated HTML. The build fails if any code sample raises
or if a `print(...)  # expected` comment doesn't match what the code really prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # shared kit.py

import kit
import g01_basics, g02_strings_numbers, g03_data, g04_functions, g05_oop, g06_advanced  # noqa: F401,E402  (register topics,
import g07_errors_modules_files, g08_stdlib, g09_concurrency, g10_testing_tooling, g11_interview  # noqa: F401,E402  in sidebar order)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "python" / "index.html"
kit.build(out, "Python")
