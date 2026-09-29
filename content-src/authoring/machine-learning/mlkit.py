"""Machine-learning extras on top of the shared kit.

code_out(src, out) — a Python example whose *whole* stdout is checked against `out` and shown to the reader as an
Output block. Use it where the printed result is naturally multi-line (DataFrames, classification reports, tree
rules); everywhere else use kit.code() with `print(...)  # expected` comments.
"""
import textwrap

import kit
from kit import code, output

_CHECK = '''
import contextlib as _c, io as _io, textwrap as _t
_b = _io.StringIO()
with _c.redirect_stdout(_b):
    exec(compile({src!r}, "<example>", "exec"), {{"__name__": "__main__"}})
_n = lambda s: "\\n".join(l.rstrip() for l in _t.dedent(s).strip("\\n").split("\\n"))
if _n(_b.getvalue()) != _n({exp!r}):
    raise AssertionError("output mismatch\\n--- expected ---\\n" + _n({exp!r}) + "\\n--- actual ---\\n" + _n(_b.getvalue()))
'''


def code_out(src, out, caption="Python"):
    src = textwrap.dedent(src).strip("\n")
    exp = textwrap.dedent(out).strip("\n")
    html = code(src, caption)                      # registers the snippet …
    tid = kit.SNIPPETS[-1][0]
    kit.SNIPPETS[-1] = (tid, caption, _CHECK.format(src=src, exp=exp), True, True)   # … checked as a whole
    return html + output(exp)
