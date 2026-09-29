"""Build content-src/legacy-html/python/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/python/build.py      (or: npm run content:python)

Edit the g*_*.py topic modules, not the generated HTML. The build fails if any code sample raises
or if a `print(...)  # expected` comment doesn't match what the code really prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import kit
import g1_basics, g2_data, g3_functions, g4_oop, g5_advanced, g6_interview  # noqa: F401  (register topics)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "python" / "index.html"

failures = kit.verify()
if failures:
    print(f"{len(failures)} snippet problem(s):\n")
    print("\n".join(failures))
    sys.exit(1)

nav, pages, group = [], [], None
for g, tid, title, icon, body in kit.TOPICS:
    if g != group:
        nav.append(f'  <div class="nav-section">{kit.esc(g)}</div>')
        group = g
    nav.append(f'  <div class="nav-item" id="nav-{tid}"><i class="ti ti-{icon}"></i>{kit.esc(title)}</div>')
    pages.append(
        f'<div class="topic" id="topic-{tid}">\n'
        f'<div class="page-tag">{kit.esc(g)}</div>\n'
        f'<h1 class="page-title">{kit.esc(title)}</h1>\n'
        f"{body}\n</div>"
    )

html = f"""<!doctype html>
<!--
  Python — study notes source for the content pipeline (scripts/content/extract.mjs).
  Vocabulary: see scripts/content/sanitize.mjs. Every code sample here was executed and its
  printed output checked when this file was generated.
-->
<html lang="en">
<head><meta charset="utf-8"><title>Python</title></head>
<body>
<nav class="sidebar">
{chr(10).join(nav)}
</nav>
<main>
{chr(10).join(pages)}
</main>
</body>
</html>
"""
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
ran = sum(1 for s in kit.SNIPPETS if s[3])
checked = sum(1 for s in kit.SNIPPETS if s[3] and s[4])
print(f"{len(kit.TOPICS)} topics, {len(kit.SNIPPETS)} code samples ({ran} executed, {checked} output-checked) → {out}")
