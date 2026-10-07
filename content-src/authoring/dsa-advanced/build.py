"""Build content-src/legacy-html/dsa_advanced/index.html (subject "DSA Advanced", catalog id `dsa-advanced`)
from the topic modules, verifying every code sample in every language.

    python3 content-src/authoring/dsa-advanced/build.py      (or: npm run content:dsa-advanced)

Edit the g*_*.py topic modules, not the generated HTML. Every algorithm is written in Python, C++, Java
and JavaScript (dsakit.multi); all four are executed and must print the same output, or the build fails.

Topic ids are permanent (learner progress is keyed on them). The 23 ids of the original notes are kept:
bit_magic, list, matrix, recursion, searching, sorting, hashing, string, linked_list, stack, infix_postfix,
queue_deque, trees, bst, heap, graph, greedy, backtracking, dp, trie, disjoint_set, segment_tree,
binary_indexed_tree.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # shared kit.py + dsakit.py

import kit  # noqa: E402
import g1_bits_recursion, g2_arrays_matrix, g3_search_sort, g4_hashing_strings  # noqa: F401,E402  (register topics,
import g5_linked_lists, g6_stacks_queues, g7_trees, g8_bst_heap  # noqa: F401,E402  in sidebar order)
import g9_graphs, g10_greedy_backtracking, g11_dp, g12_structures  # noqa: F401,E402

out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "legacy-html" / "dsa_advanced" / "index.html"
kit.build(out.resolve(), "DSA Advanced")
