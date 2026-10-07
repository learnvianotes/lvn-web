"""Verify the code samples of one or more topic modules without building the whole subject.

    python3 content-src/authoring/check.py dsa-basics g6_stacks_queues [g7_trees_heaps …]

Imports only the named modules, runs every snippet (Python, C++, Java, JavaScript) and reports the
failures with their source — exit 1 if anything fails. Also lists the topics registered (group · id · title)
and writes a preview HTML of those topics to content-src/authoring/.cache/preview-<subject>.html.
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
subject, modules = sys.argv[1], sys.argv[2:]
sys.path.insert(0, str(HERE / subject))
sys.path.insert(0, str(HERE))

import kit  # noqa: E402

for m in modules:
    importlib.import_module(m)

print(f"{len(kit.TOPICS)} topic(s):")
for g, tid, title, icon, body in kit.TOPICS:
    n = sum(1 for s in kit.SNIPPETS if s[0] == tid)
    print(f"  {g} · {tid} · {title} · {n} code samples · {len(body):,} chars")

failures = kit.verify()
if failures:
    print(f"\n{len(failures)} snippet problem(s):\n")
    print("\n".join(failures))
    sys.exit(1)
ran = sum(1 for s in kit.SNIPPETS if s[3])
print(f"\nOK — {len(kit.SNIPPETS)} code samples, {ran} executed, all outputs match.")

preview = HERE / ".cache" / f"preview-{subject}.html"
preview.parent.mkdir(parents=True, exist_ok=True)
preview.write_text("<!doctype html><meta charset=utf-8><body>" + "\n".join(
    f'<div class="topic" id="topic-{tid}"><h1>{kit.esc(title)}</h1>{body}</div>' for _, tid, title, _, body in kit.TOPICS))
print(f"preview → {preview}")
