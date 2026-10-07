"""DSA extras on top of the shared kit (used by dsa-basics/ and dsa-advanced/).

multi(out, py=…, cpp=…, java=…, js=…)
    One program written in up to four languages, shown to the reader as tabs (Python · C++ · Java ·
    JavaScript — the same order as Sheet 150) with a single shared Output block underneath. Every
    version is executed at build time and must print exactly `out`, so the four tabs can never drift
    apart. This is how every algorithm in the DSA notes is presented.

complexity(time, space)       chips "Time O(…)" / "Space O(…)" — put one under every solution
io(input, output, …)          an Input/Output example callout (several pairs allowed)
diagram(text, caption)        a monospaced drawing (tree, array, matrix) — rendered as a code block,
                              never as paragraphs
idea(body)                    a "Idea" key-point callout (the one-sentence insight behind a solution)
"""
import textwrap

import kit
from kit import LANG_CAPTION, esc, _block, _box, chips, note

LANGS = ("py", "cpp", "java", "js")


def multi(out=None, *, py=None, cpp=None, java=None, js=None, stdin="", run=True, output_caption="Output"):
    """Tabs with the same program in several languages; all are executed and must print `out`.

    out   exact expected stdout (shown once under the tabs). None → each version only has to run cleanly.
    Pass at least two languages. Java: the first top-level class must be `public class Main` holding `main`.
    """
    exp = None if out is None else textwrap.dedent(out).strip("\n")
    sources = {"py": py, "cpp": cpp, "java": java, "js": js}
    panels = []
    for lang in LANGS:
        src = sources[lang]
        if src is None:
            continue
        src = textwrap.dedent(src).strip("\n")
        kit.SNIPPETS.append((kit._topic, lang, src, run,
                             dict(out=exp, setup="", stdin=stdin, args=(), fails=False, flags=())))
        panels.append(f'<div class="tab-panel" data-label="{LANG_CAPTION[lang]}">{_block(src, LANG_CAPTION[lang], lang)}</div>')
    assert len(panels) >= 2, "multi() needs at least two languages — use snippet()/code() for one"
    html = f'<div class="tabs">{"".join(panels)}</div>'
    if exp:
        html += _block(exp, output_caption, "text")
    return html


def complexity(time, space="O(1)"):
    """Complexity chips, e.g. complexity("O(n log n)", "O(n)")."""
    return chips(f"Time {time}", f"Space {space}")


def io(*pairs):
    """io("arr = [1, 2, 3]", "6", "arr = []", "0") → an example callout with Input/Output lines."""
    assert len(pairs) % 2 == 0, "io() takes input/output pairs"
    lines = []
    for i in range(0, len(pairs), 2):
        lines.append(f"<strong>Input:</strong> <code>{esc(str(pairs[i]))}</code><br><strong>Output:</strong> <code>{esc(str(pairs[i + 1]))}</code>")
    return _box("example", "Example", "<p>" + "<br>".join(lines) + "</p>")


def diagram(text, caption="Diagram"):
    """A monospaced drawing (tree / array / matrix). Lines are kept exactly as written."""
    return _block(textwrap.dedent(text).strip("\n"), caption, "text")


def idea(body, label="Idea"):
    return note(body, label)


def pitfall(body):
    return kit.warn(body, "Pitfall")
