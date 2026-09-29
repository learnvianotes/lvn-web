"""Tiny authoring kit that emits the legacy-HTML vocabulary the content pipeline understands
(scripts/content/sanitize.mjs): page-subtitle, section-title, def-card, highlight-box, warning-box,
pros/cons, card-grid/card, code-block-container, step-row, chips, qa-card, tables.

Every code() snippet is executed at build time. With check=True, each `print(...)` line must carry a
trailing `# expected output` comment, and the real output must match — so the notes never lie.
"""
import contextlib
import html
import io
import re
import textwrap

SNIPPETS = []  # (topic_id, caption, src, run, check)
_topic = None


def esc(s):
    return html.escape(s, quote=False)


def md(s):
    """Inline markup: `code`, **bold**, *italic*. Text is escaped first."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def p(text):
    return f"<p>{md(text)}</p>"


def lead(text):
    return f'<p class="page-subtitle">{md(text)}</p>'


def section(title, icon="point"):
    return f'<div class="section-title"><i class="ti ti-{icon}"></i>{md(title)}</div>'


def ul(*items):
    return "<ul>" + "".join(f"<li>{md(i)}</li>" for i in items) + "</ul>"


def ol(*items):
    return "<ol>" + "".join(f"<li>{md(i)}</li>" for i in items) + "</ol>"


def _box(cls, label, body):
    lab = f'<div class="label">{md(label)}</div>' if label else ""
    inner = body if body.lstrip().startswith("<") else p(body)
    return f'<div class="{cls}">{lab}{inner}</div>'


def define(term, body):
    return f'<div class="def-card"><p><strong>{esc(term)}</strong> — {md(body)}</p></div>'


def note(body, label="Key point"):
    return _box("highlight-box", label, body)


def warn(body, label="Watch out"):
    return _box("warning-box", label, body)


def good(body, label="Do"):
    return _box("pros", label, body)


def bad(body, label="Avoid"):
    return _box("cons", label, body)


def dodont(do, dont):
    return f'<div class="card-grid">{good(do)}{bad(dont)}</div>'


def cards(*items, cols=2):
    """items: (title, body, icon?)"""
    cls = "card-grid-3" if cols == 3 else "card-grid"
    out = []
    for it in items:
        title, body = it[0], it[1]
        icon = it[2] if len(it) > 2 else "point"
        out.append(f'<div class="card"><h3><i class="ti ti-{icon}"></i>{md(title)}</h3>{p(body)}</div>')
    return f'<div class="{cls}">{"".join(out)}</div>'


def table(head, *rows):
    th = "".join(f"<th>{md(h)}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def steps(*items):
    """items: (title, desc)"""
    out = []
    for i, (t, d) in enumerate(items, 1):
        out.append(
            f'<div class="step-row"><div class="step-num">{i}</div><div class="step-body">'
            f'<div class="step-title">{md(t)}</div><div class="step-desc">{md(d)}</div></div></div>'
        )
    return "".join(out)


def chips(*items):
    return '<div class="chips">' + "".join(f'<span class="chip">{md(i)}</span>' for i in items) + "</div>"


def qa(question, *answer_parts):
    body = "".join(a if a.lstrip().startswith("<") else p(a) for a in answer_parts)
    return f'<div class="qa-card"><div class="qa-question">{esc(question.replace("`", ""))}</div><div class="qa-answer">{body}</div></div>'


def code(src, caption="Python", run=True, check=True):
    src = textwrap.dedent(src).strip("\n")
    SNIPPETS.append((_topic, caption, src, run, check))
    return f'<div class="code-block-container"><div class="code-lang">{esc(caption)}</div><pre>{esc(src)}</pre></div>'


def shell(src, caption="Terminal"):
    src = textwrap.dedent(src).strip("\n")
    return f'<div class="code-block-container"><div class="code-lang">{esc(caption)}</div><pre>{esc(src)}</pre></div>'


# ── topics registry ─────────────────────────────────────────

TOPICS = []  # (group, id, title, icon, html)


def topic(group, tid, title, icon):
    def wrap(fn):
        global _topic
        _topic = tid
        body = "\n".join(fn())
        TOPICS.append((group, tid, title, icon, body))
        _topic = None
        return fn
    return wrap


# ── verification ────────────────────────────────────────────

PRINT_LINE = re.compile(r"^(\s*)print\(.*\)\s*#\s?(.*)$")


def verify():
    failures = []
    for tid, caption, src, run, check in SNIPPETS:
        if not run:
            continue
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(src, f"<{tid}>", "exec"), {"__name__": "__main__"})
        except Exception as e:  # noqa: BLE001
            failures.append(f"{tid}: raised {type(e).__name__}: {e}\n{src}\n")
            continue
        if not check:
            continue
        expected = [m.group(2).rstrip() for line in src.splitlines() if (m := PRINT_LINE.match(line))]
        actual = buf.getvalue().rstrip("\n").split("\n") if buf.getvalue() else []
        if expected and expected != actual:
            failures.append(f"{tid}: output mismatch\n  expected {expected}\n  actual   {actual}\n{src}\n")
    return failures
