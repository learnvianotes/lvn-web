"""Shared authoring kit (used by python/ and data-science/). Emits the legacy-HTML vocabulary the content pipeline understands
(scripts/content/sanitize.mjs): page-subtitle, section-title, def-card, highlight-box, warning-box,
pros/cons, card-grid/card, code-block-container, step-row, chips, qa-card, tables.

Every code() snippet is executed at build time. With check=True, each `print(...)` line must carry a
trailing `# expected output` comment, and the real output must match — so the notes never lie.
Anything after a `←` in that comment is an explanation for the reader and isn't compared.

Other languages go through snippet(lang, src, out=...): C and C++ are compiled with clang (warnings are
errors; AddressSanitizer + UBSan catch memory bugs), Java runs through `java File.java`, JavaScript through
node, SQL through SQLite. `out` is the exact stdout; it's shown to the reader as an "Output" block and the
build fails if the real program prints anything else. Results are cached by content hash, so re-builds only
run what changed.
"""
import contextlib
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import html
import io
import re
import textwrap
from pathlib import Path

SNIPPETS = []  # (topic_id, caption, src, run, check)
_topic = None


def esc(s):
    return html.escape(s, quote=False)


def md(s):
    """Inline markup: `code`, **bold**, *italic*. Text is escaped first."""
    s = esc(s)
    spans = []  # code spans are set aside first so `char **argv` or `*p` inside them never turns into bold/italic

    def keep(m):
        spans.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(spans) - 1}\x00"
    s = re.sub(r"`([^`]+)`", keep, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], s)


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


def example(body, label="Example"):
    return _box("example", label, body)


def flow(*nodes):
    """A left-to-right pipeline: flow("Source", "Compiler", "Binary")."""
    parts = []
    for i, n in enumerate(nodes):
        if i:
            parts.append('<div class="flow-arrow">→</div>')
        parts.append(f'<div class="flow-box">{md(n)}</div>')
    return f'<div class="flow">{"".join(parts)}</div>'


def formula(text):
    return f'<div class="math-formula">{md(text)}</div>'


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


LANG_CAPTION = {"c": "C", "cpp": "C++", "java": "Java", "js": "JavaScript", "sql": "SQL"}


def _block(src, caption, lang=""):
    attr = f' data-lang="{lang}"' if lang else ""
    return f'<div class="code-block-container"{attr}><div class="code-lang">{esc(caption)}</div><pre>{esc(src)}</pre></div>'


def snippet(lang, src, out=None, caption=None, *, run=True, setup="", stdin="", args=(), fails=False, flags=()):
    """A C / C++ / Java / JavaScript / SQL example, executed at build time.

    out    exact expected stdout (shown to the reader as an Output block). None → only has to run cleanly.
    setup  SQL run before `src` (sample tables) — not shown.   stdin / args  fed to the program.
    fails  the example is *supposed* to be rejected (compile error / exception) — shows why code is wrong.
    run    False → not executed at all (use only for fragments that can't stand alone).
    C/C++/Java sources without a main() are compile-checked only.
    """
    assert lang in LANG_CAPTION, lang
    src = textwrap.dedent(src).strip("\n")
    exp = None if out is None else textwrap.dedent(out).strip("\n")
    SNIPPETS.append((_topic, lang, src, run, dict(out=exp, setup=textwrap.dedent(setup), stdin=stdin,
                                                    args=tuple(args), fails=fails, flags=tuple(flags))))
    html_out = _block(src, caption or LANG_CAPTION[lang], lang)
    if exp is not None and exp != "":
        html_out += _block(exp, "Output", "text")
    return html_out


def output(text, caption="Output"):
    """A plain output/console block that isn't tied to a checked snippet (e.g. a compiler error message)."""
    return _block(textwrap.dedent(text).strip("\n"), caption, "text")


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


CACHE = Path(__file__).parent / ".cache" / "snippets"
_JDK = next((d for d in [os.environ.get("JAVA_HOME", ""), "/opt/homebrew/opt/openjdk@21", "/opt/homebrew/opt/openjdk"]
             if d and Path(d, "bin", "javac").exists()), None)
JAVA = str(Path(_JDK, "bin", "java")) if _JDK else "java"
JAVAC = str(Path(_JDK, "bin", "javac")) if _JDK else "javac"
SAN = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer", "-g"]
CFLAGS = {
    "c": ["clang", "-std=c17", "-Wall", "-Wextra", "-Werror", "-Wno-unused-variable", "-Wno-unused-parameter", "-Wno-unused-but-set-variable"],
    "cpp": ["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror", "-Wno-unused-variable", "-Wno-unused-parameter", "-Wno-unused-but-set-variable"],
}
HAS_MAIN = {"c": re.compile(r"\bint\s+main\s*\("), "cpp": re.compile(r"\bint\s+main\s*\("),
            "java": re.compile(r"static\s+void\s+main\s*\(")}


def _proc(cmd, cwd, stdin="", timeout=20):
    try:
        r = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=timeout,
                           env={**{k: v for k, v in os.environ.items() if k != "FORCE_COLOR"},
                                "ASAN_OPTIONS": "detect_leaks=0", "NO_COLOR": "1", "NODE_DISABLE_COLORS": "1"})
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"timed out after {timeout}s"


def _sql(src, setup):
    """Run statements one by one; every result set is printed as an aligned table (blank line between)."""
    db = sqlite3.connect(":memory:")
    blocks = []
    try:
        if setup.strip():
            db.executescript(setup)
        stmt = ""
        for line in (src + "\n").splitlines(keepends=True):
            stmt += line
            if not sqlite3.complete_statement(stmt):
                continue
            cur = db.execute(stmt)
            stmt = ""
            if cur.description:
                head = [d[0] for d in cur.description]
                rows = [["NULL" if v is None else str(v) for v in r] for r in cur.fetchall()]
                w = [max(len(x) for x in col) for col in zip(head, *rows)]
                fmt = lambda cells: " | ".join(c.ljust(w[i]) for i, c in enumerate(cells)).rstrip()
                blocks.append("\n".join([fmt(head), "-+-".join("-" * x for x in w)] + [fmt(r) for r in rows]))
        db.commit()
        return 0, "\n\n".join(blocks), ""
    except sqlite3.Error as e:
        return 1, "\n\n".join(blocks), f"{type(e).__name__}: {e}"


def _execute(lang, src, o):
    """→ (returncode, stdout, stderr). Cached by everything that affects the result."""
    key = hashlib.sha256(json.dumps([lang, src, o["setup"], o["stdin"], o["args"], o["flags"], 4]).encode()).hexdigest()
    hit = CACHE / f"{key}.json"
    if hit.exists():
        return tuple(json.loads(hit.read_text()))
    if lang == "sql":
        res = _sql(src, o["setup"])
    else:
        with tempfile.TemporaryDirectory() as d:
            if lang in ("c", "cpp"):
                f = Path(d) / ("main.c" if lang == "c" else "main.cpp")
                f.write_text(src + "\n")
                base = CFLAGS[lang] + list(o["flags"])
                if not HAS_MAIN[lang].search(src):
                    res = _proc(base + ["-fsyntax-only", str(f)], d)
                else:
                    rc, so, se = _proc(base + SAN + [str(f), "-o", "prog"] + (["-lm"] if lang == "c" else []), d, timeout=60)
                    res = (rc, so, "compile: " + se) if rc else _proc(["./prog", *o["args"]], d, o["stdin"])
            elif lang == "java":
                m = re.search(r"public\s+(?:final\s+|abstract\s+)*(?:class|interface|record|enum)\s+(\w+)", src)
                f = Path(d) / f"{m.group(1) if m else 'Main'}.java"
                f.write_text(src + "\n")
                if HAS_MAIN["java"].search(src):
                    res = _proc([JAVA, "-ea", *o["flags"], str(f.name), *o["args"]], d, o["stdin"], timeout=60)
                else:
                    res = _proc([JAVAC, "-Xlint:all", "-Werror", "-d", d, str(f.name)], d, timeout=60)
            else:  # js
                f = Path(d) / "main.mjs"
                f.write_text(src + "\n")
                res = _proc(["node", *o["flags"], str(f.name), *o["args"]], d, o["stdin"])
    if not res[2].startswith("timed out"):
        CACHE.mkdir(parents=True, exist_ok=True)
        hit.write_text(json.dumps(list(res)))
    return res


def _norm(text):
    return "\n".join(line.rstrip() for line in text.rstrip("\n").split("\n")).strip("\n")


def _check_external(tid, lang, src, o):
    rc, so, se = _execute(lang, src, o)
    if o["fails"]:
        return None if rc != 0 else f"{tid} [{lang}]: expected this example to fail, but it ran cleanly\n{src}\n"
    if rc != 0:
        return f"{tid} [{lang}]: exit {rc}\n{se.strip()[:3000]}\n--- source ---\n{src}\n"
    if o["out"] is not None and _norm(so) != _norm(o["out"]):
        return (f"{tid} [{lang}]: output mismatch\n--- expected ---\n{o['out']}\n--- actual ---\n{so.rstrip()}\n"
                f"--- source ---\n{src}\n")
    return None


def verify():
    from concurrent.futures import ThreadPoolExecutor
    failures = []
    ext = [(tid, lang, src, o) for tid, lang, src, run, o in SNIPPETS if run and isinstance(o, dict)]
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as pool:
        failures += [f for f in pool.map(lambda a: _check_external(*a), ext) if f]
    for tid, caption, src, run, check in SNIPPETS:
        if not run or isinstance(check, dict):
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
        expected = [m.group(2).split("←")[0].rstrip() for line in src.splitlines() if (m := PRINT_LINE.match(line))]
        actual = buf.getvalue().rstrip("\n").split("\n") if buf.getvalue() else []
        if expected and expected != actual:
            failures.append(f"{tid}: output mismatch\n  expected {expected}\n  actual   {actual}\n{src}\n")
    return failures


# ── page assembly ──────────────────────────────────────────

def build(out, subject_title, header_note="", env_setup=None):
    """Verify every snippet, then write the subject's source HTML to `out`. Exits 1 on any failure."""
    import sys
    from pathlib import Path
    if env_setup:
        env_setup()
    failures = verify()
    if failures:
        print(f"{len(failures)} snippet problem(s):\n")
        print("\n".join(failures))
        sys.exit(1)
    nav, pages, group = [], [], None
    for g, tid, title, icon, body in TOPICS:
        if g != group:
            nav.append(f'  <div class="nav-section">{esc(g)}</div>')
            group = g
        nav.append(f'  <div class="nav-item" id="nav-{tid}"><i class="ti ti-{icon}"></i>{esc(title)}</div>')
        pages.append(
            f'<div class="topic" id="topic-{tid}">\n'
            f'<div class="page-tag">{esc(g)}</div>\n'
            f'<h1 class="page-title">{esc(title)}</h1>\n'
            f"{body}\n</div>"
        )
    nl = "\n"
    html_out = f"""<!doctype html>
<!--
  {subject_title} — study notes source for the content pipeline (scripts/content/extract.mjs).
  Vocabulary: see scripts/content/sanitize.mjs. Every code sample here was executed and its
  printed output checked when this file was generated.{header_note}
-->
<html lang="en">
<head><meta charset="utf-8"><title>{esc(subject_title)}</title></head>
<body>
<nav class="sidebar">
{nl.join(nav)}
</nav>
<main>
{nl.join(pages)}
</main>
</body>
</html>
"""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_out, encoding="utf-8")
    ran = sum(1 for s in SNIPPETS if s[3])
    checked = sum(1 for s in SNIPPETS if s[3] and s[4] and (not isinstance(s[4], dict) or s[4]["out"] is not None or s[4]["fails"]))
    print(f"{len(TOPICS)} topics, {len(SNIPPETS)} code samples ({ran} executed, {checked} output-checked) → {out}")
