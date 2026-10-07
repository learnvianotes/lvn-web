"""Build content-src/legacy-html/dsa_basics/index.html (subject "DSA Basics", catalog id `dsa-basics`)
from the topic modules, verifying every code sample in every language.

    python3 content-src/authoring/dsa-basics/build.py      (or: npm run content:dsa-basics)

Edit the g*_*.py topic modules, not the generated HTML. Every algorithm is written in Python, C++, Java
and JavaScript (dsakit.multi); all four are executed and must print the same output, or the build fails.

Topic ids are permanent (learner progress is keyed on them). The 19 ids of the original notes are kept:
analysis, math, recursion, list, string, searching, sorting, hashing, set, dictionary, singly_linked,
circular_linked, doubly_linked, stack, queue, deque, trees, bst, heap.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # shared kit.py + dsakit.py

import kit  # noqa: E402
import g1_foundations, g2_arrays_strings, g3_search_sort, g4_hashing  # noqa: F401,E402  (register topics,
import g5_linked_lists, g6_stacks_queues, g7_trees_heaps  # noqa: F401,E402  in sidebar order)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "legacy-html" / "dsa_basics" / "index.html"
kit.build(out.resolve(), "DSA Basics")
