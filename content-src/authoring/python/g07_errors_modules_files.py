from kit import *

G = "Errors, Modules & Files"


@topic(G, "exceptions", "Exceptions: try, except, raise", "alert-octagon")
def _():
    yield lead("Errors are objects that propagate up the call stack until something handles them. `try` / `except` catches them, `raise` creates them, and `finally` (or `with`) guarantees cleanup.")
    yield define("Exception", "an object (an instance of a class derived from `BaseException`) that interrupts normal flow. If no `except` clause up the call stack matches it, the program stops and prints a *traceback*.")
    yield section("How an exception travels", "arrow-up")
    yield steps(
        ("Raised", "Something fails (`int('x')`) or your code runs `raise SomeError(...)`."),
        ("Unwinds", "Python abandons the current function and looks for a matching `except` in each caller, innermost first."),
        ("Handled — or not", "The first matching `except` runs and execution continues after its `try` statement. With no match, the traceback is printed and the interpreter exits with status 1."),
    )
    yield code('''
        def level3():
            return int("not a number")      # raises ValueError here

        def level2():
            return level3()                  # no handler → passes through

        def level1():
            try:
                return level2()
            except ValueError:
                return "handled in level1"

        print(level1())                      # handled in level1
    ''')
    yield section("try / except / else / finally", "shield")
    yield code('''
        def parse(value):
            try:
                n = int(value)
            except ValueError as e:
                return f"bad input: {e}"
            else:
                return n * 2            # runs only if no exception
            finally:
                pass                    # always runs: close files, release locks

        print(parse("21"))              # 42
        print(parse("x"))               # bad input: invalid literal for int() with base 10: 'x'
    ''')
    yield table(
        ["Block", "Runs when"],
        ["`try`", "Always — the code that might fail"],
        ["`except E`", "An exception of type `E` (or a subclass) was raised"],
        ["`else`", "The `try` block finished **without** an exception"],
        ["`finally`", "Always, even after `return`, `break` or an unhandled error"],
    )
    yield note("Keep only the risky line in `try` and put the follow-up work in `else` — otherwise a bug in the follow-up code could be caught by an `except` that was never meant for it.")
    yield section("Raising & custom exceptions", "flame")
    yield code('''
        class InsufficientFunds(Exception):
            def __init__(self, needed):
                super().__init__(f"need {needed} more")
                self.needed = needed

        def withdraw(balance, amount):
            if amount > balance:
                raise InsufficientFunds(amount - balance)
            return balance - amount

        try:
            withdraw(100, 150)
        except InsufficientFunds as e:
            print(e, e.needed)          # need 50 more 50

        try:
            try:
                {}["k"]
            except KeyError as e:
                raise LookupError("config missing") from e    # keep the original cause
        except LookupError as e:
            print(repr(e.__cause__))    # KeyError('k')
    ''')
    yield dodont(
        "Catch the most specific exception you can handle, keep `try` blocks small, and re-raise with `raise` (no argument) to preserve the traceback.",
        "Bare `except:` or `except Exception: pass` — it hides bugs, and a bare `except` even swallows `KeyboardInterrupt`.",
    )
    yield section("Exception hierarchy (the useful part)", "hierarchy-3")
    yield table(
        ["Exception", "Typical cause"],
        ["`ValueError`", "Right type, wrong value: `int('x')`"],
        ["`TypeError`", "Wrong type: `'a' + 1`"],
        ["`KeyError` / `IndexError`", "Missing dict key / list index out of range (both are `LookupError`s)"],
        ["`AttributeError`", "Object has no such attribute"],
        ["`NameError`", "Name not defined (typo, or used before assignment)"],
        ["`ZeroDivisionError`", "Division by zero (an `ArithmeticError`)"],
        ["`FileNotFoundError`", "Missing file (an `OSError`)"],
        ["`StopIteration`", "Iterator is exhausted"],
        ["`RecursionError`", "Recursion deeper than `sys.getrecursionlimit()`"],
    )
    yield p("The full tree, `BaseException` vs `Exception`, exception groups and chaining are in **Exception Hierarchy & Advanced Handling**.")
    yield section("Guaranteed cleanup: `finally` and `with`", "door-exit")
    yield code('''
        from contextlib import suppress

        events = []
        def risky():
            try:
                events.append("open")
                raise RuntimeError("boom")
            finally:
                events.append("close")          # runs even though the error escapes

        try:
            risky()
        except RuntimeError:
            pass
        print(events)                           # ['open', 'close']

        with suppress(FileNotFoundError):       # ignore one specific, expected error
            open("definitely-missing.txt")
        print("still running")                  # still running
    ''')
    yield note("`with` is the idiomatic way to pair setup with cleanup (files, locks, connections). How it works and how to write your own is covered in **Context Managers & contextlib**.")
    yield qa("What is the difference between `else` and `finally` in a try statement?",
             "`else` runs only when the `try` block raised nothing — it's for the success path. `finally` runs no matter what (success, exception, `return`, `break`) — it's for cleanup.")


@topic(G, "exceptions-advanced", "Exception Hierarchy & Advanced Handling", "alert-triangle")
def _():
    yield lead("Beyond `try`/`except`: the full class tree, designing your own error hierarchy, chaining, notes, exception groups, warnings and the patterns (EAFP, retry) that production code relies on.")
    yield section("The class tree", "hierarchy-3")
    yield output('''
        BaseException
        ├── SystemExit              ← sys.exit()
        ├── KeyboardInterrupt       ← Ctrl-C
        ├── GeneratorExit           ← generator.close()
        ├── BaseExceptionGroup
        └── Exception               ← everything you normally catch
            ├── ArithmeticError     → ZeroDivisionError, OverflowError
            ├── LookupError         → KeyError, IndexError
            ├── OSError             → FileNotFoundError, PermissionError, TimeoutError, ConnectionError…
            ├── ValueError          → UnicodeDecodeError…
            ├── TypeError, AttributeError, NameError, ImportError (→ ModuleNotFoundError)
            ├── RuntimeError        → RecursionError, NotImplementedError
            ├── StopIteration, StopAsyncIteration
            ├── ExceptionGroup
            └── Warning             → DeprecationWarning, UserWarning, SyntaxWarning…
    ''', caption="Built-in exception hierarchy (abridged)")
    yield code('''
        print(issubclass(KeyboardInterrupt, Exception))       # False
        print(issubclass(KeyboardInterrupt, BaseException))   # True
        print(issubclass(KeyError, LookupError), issubclass(ZeroDivisionError, ArithmeticError))   # True True
        print([c.__name__ for c in FileNotFoundError.__mro__])
        # ['FileNotFoundError', 'OSError', 'Exception', 'BaseException', 'object']
    ''', check=False)
    yield note("`except Exception` deliberately does **not** catch `SystemExit`, `KeyboardInterrupt` or `GeneratorExit` — those mean “stop now”, and swallowing them makes a program impossible to quit. A bare `except:` catches `BaseException`, which is why it's banned in good code.")
    yield code('''
        import sys
        try:
            sys.exit(2)                    # sys.exit just raises SystemExit
        except SystemExit as e:
            print("exit code", e.code)     # exit code 2
    ''')
    yield section("Designing a custom hierarchy", "sitemap")
    yield p("A library should raise its **own** base exception, with specific subclasses underneath. Callers can then catch everything from your library in one clause, or one precise failure.")
    yield code('''
        class PaymentError(Exception):
            """Base class for every error this library raises."""

        class CardDeclined(PaymentError):
            def __init__(self, reason):
                super().__init__(f"card declined ({reason})")
                self.reason = reason

        class GatewayTimeout(PaymentError):
            pass

        def charge(amount):
            if amount < 0:
                raise ValueError("amount must be >= 0")     # caller bug → a built-in error
            if amount > 1000:
                raise CardDeclined("limit")
            return "ok"

        try:
            charge(5000)
        except PaymentError as e:                           # the whole family
            print(type(e).__name__, "|", e, "|", e.reason)  # CardDeclined | card declined (limit) | limit
    ''')
    yield cards(
        ("Inherit from `Exception`", "Never from `BaseException` — your errors should be catchable with `except Exception`.", "hierarchy"),
        ("Name ends in `Error`", "`ConfigError`, `RateLimitError` — the PEP 8 convention.", "tag"),
        ("Carry data", "Store useful fields (`self.status`, `self.retry_after`) instead of making callers parse the message.", "database"),
        ("Reuse built-ins for caller bugs", "Wrong argument type → `TypeError`; bad value → `ValueError`. Custom classes are for *domain* failures.", "recycle"),
    )
    yield section("Catching several types & re-raising", "arrows-join")
    yield code('''
        def to_int(x):
            try:
                return int(x)
            except (TypeError, ValueError) as e:     # a tuple catches any of them
                return type(e).__name__

        print(to_int("7"), to_int("x"), to_int(None))   # 7 ValueError TypeError

        log = []
        def load(key):
            try:
                return {"a": 1}[key]
            except KeyError:
                log.append(f"missing {key}")          # do something useful…
                raise                                 # …then re-raise the SAME exception

        try:
            load("b")
        except KeyError as e:
            print(repr(e), log)                       # KeyError('b') ['missing b']
    ''')
    yield warn("`except` clauses are tried top to bottom and the first match wins — put **subclasses before base classes**. `except OSError:` above `except FileNotFoundError:` makes the second one unreachable.")
    yield code('''
        try:
            1 / 0
        except ZeroDivisionError as e:
            saved = e
        print("e" in dir(), type(saved).__name__)    # False ZeroDivisionError
    ''')
    yield note("The name bound by `except … as e` is **deleted** when the block ends (to break a reference cycle through the traceback). Assign it to another name if you need it later.")
    yield section("Chaining: `__context__` vs `__cause__`", "link")
    yield code('''
        def implicit():
            try:
                1 / 0
            except ZeroDivisionError:
                raise ValueError("bad ratio")              # error while handling another

        def explicit():
            try:
                1 / 0
            except ZeroDivisionError as e:
                raise ValueError("bad ratio") from e       # "this caused that"

        def hidden():
            try:
                1 / 0
            except ZeroDivisionError:
                raise ValueError("bad ratio") from None    # hide the internal detail

        def inspect(f):
            try:
                f()
            except ValueError as e:
                return type(e.__cause__).__name__, type(e.__context__).__name__, e.__suppress_context__

        print(inspect(implicit))   # ('NoneType', 'ZeroDivisionError', False)
        print(inspect(explicit))   # ('ZeroDivisionError', 'ZeroDivisionError', True)
        print(inspect(hidden))     # ('NoneType', 'ZeroDivisionError', True)
    ''')
    yield table(
        ["You write", "Attribute set", "Traceback says"],
        ["`raise New()` inside `except`", "`__context__`", "“During handling of the above exception, another exception occurred”"],
        ["`raise New() from e`", "`__cause__` (+ `__context__`)", "“The above exception was the direct cause of the following exception”"],
        ["`raise New() from None`", "`__suppress_context__ = True`", "Only the new exception"],
    )
    yield section("Adding context: `add_note` (3.11+)", "notes")
    yield code('''
        import traceback

        def parse_row(n, text):
            try:
                return int(text)
            except ValueError as e:
                e.add_note(f"while parsing row {n} of users.csv")
                raise

        try:
            parse_row(3, "abc")
        except ValueError as e:
            print(e.__notes__)                                       # ['while parsing row 3 of users.csv']
            print(traceback.format_exception_only(e)[-1].strip())    # while parsing row 3 of users.csv
    ''')
    yield p("Notes are printed under the error message in tracebacks — a lightweight way to add context without wrapping the exception in a new type.")
    yield section("ExceptionGroup and `except*` (3.11+)", "stack-2")
    yield p("When several independent operations fail at once (parallel tasks, validating many fields), raise them **together** as an `ExceptionGroup`. `except*` handles each type inside the group; several `except*` clauses can run for one group.")
    yield code('''
        def validate(user):
            errors = []
            if not user.get("name"):
                errors.append(ValueError("name is required"))
            if not isinstance(user.get("age"), int):
                errors.append(TypeError("age must be an int"))
            if "@" not in user.get("email", ""):
                errors.append(ValueError("email is invalid"))
            if errors:
                raise ExceptionGroup("invalid user", errors)

        try:
            validate({"name": "", "age": "x", "email": "nope"})
        except* ValueError as eg:
            print("values:", [str(e) for e in eg.exceptions])   # values: ['name is required', 'email is invalid']
        except* TypeError as eg:
            print("types:", [str(e) for e in eg.exceptions])    # types: ['age must be an int']
    ''')
    yield code('''
        eg = ExceptionGroup("batch", [ValueError(1), KeyError(2), ValueError(3)])
        values, rest = eg.split(ValueError)
        print(len(values.exceptions), [type(e).__name__ for e in rest.exceptions])   # 2 ['KeyError']
    ''')
    yield note("`asyncio.TaskGroup` raises an `ExceptionGroup` when tasks fail, so `except*` is the natural way to handle concurrent failures.")
    yield section("Inspecting tracebacks", "list-search")
    yield code('''
        import traceback

        def inner():
            return 1 / 0
        def outer():
            return inner()

        try:
            outer()
        except ZeroDivisionError as e:
            frames = traceback.extract_tb(e.__traceback__)
            print([f.name for f in frames])                          # ['<module>', 'outer', 'inner']
            print(traceback.format_exception_only(e)[0].strip())     # ZeroDivisionError: division by zero
    ''')
    yield p("`traceback.format_exc()` returns the full traceback as a string (for logging); `logger.exception(\"msg\")` does the same automatically inside an `except` block.")
    yield section("`assert` — for invariants, not validation", "check")
    yield code('''
        def mean(xs):
            assert xs, "mean() of an empty list"     # a developer's sanity check
            return sum(xs) / len(xs)

        try:
            mean([])
        except AssertionError as e:
            print(e)                                 # mean() of an empty list
    ''')
    yield warn("`python -O` strips every `assert`. Never use it to check user input, permissions or anything that must hold in production — `raise ValueError` instead. And `assert (cond, \"msg\")` is **always true** (a non-empty tuple); Python emits a `SyntaxWarning` for it.")
    yield section("Warnings", "alert-circle")
    yield p("A warning reports something suspicious without stopping the program — most often a deprecation. Warnings are printed once per location by default and can be filtered or turned into errors.")
    yield code('''
        import warnings

        def old_api():
            warnings.warn("old_api() is deprecated; use new_api()", DeprecationWarning, stacklevel=2)
            return 42

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = old_api()

        print(result, caught[0].category.__name__)   # 42 DeprecationWarning
        print(caught[0].message)                     # old_api() is deprecated; use new_api()
    ''')
    yield table(
        ["Filter action", "Effect"],
        ["`\"default\"`", "Print the first occurrence per location"],
        ["`\"always\"`", "Print every occurrence"],
        ["`\"ignore\"`", "Never print"],
        ["`\"error\"`", "Turn the warning into an exception — great in test suites (`python -W error`, `pytest -W error`)"],
    )
    yield section("`finally` beats `return`", "arrow-back-up")
    yield code('''
        def f():
            try:
                return "from try"
            finally:
                print("finally runs first")   # finally runs first

        print(f())                            # from try
    ''')
    yield code('''
        import warnings

        # A return inside finally silently DISCARDS an in-flight exception.
        # Python 3.14 warns about it at compile time (PEP 765); silenced here to show the behaviour.
        src = """
        def swallow():
            try:
                raise ValueError("lost!")
            finally:
                return "finally wins"
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            ns = {}
            exec(src, ns)
        print(ns["swallow"]())      # finally wins
    ''')
    yield warn("Never `return`, `break` or `continue` out of a `finally` block — the exception being propagated vanishes without a trace.")
    yield section("EAFP, cost and the retry pattern", "refresh")
    yield p("Setting up a `try` block is essentially free in Python 3.11+ (“zero-cost” exceptions); *raising* costs a few microseconds. So EAFP — just try and handle failure — is idiomatic when failure is the exception, not the rule.")
    yield code('''
        def get_port(cfg):
            try:
                return int(cfg["port"])
            except (KeyError, ValueError):
                return 8080

        print(get_port({"port": "5432"}), get_port({}), get_port({"port": "x"}))   # 5432 8080 8080
    ''')
    yield code('''
        import time

        def retry(fn, attempts=3, base_delay=0.001, retry_on=(ConnectionError, TimeoutError)):
            for attempt in range(1, attempts + 1):
                try:
                    return fn()
                except retry_on:
                    if attempt == attempts:
                        raise                                    # out of attempts: propagate
                    time.sleep(base_delay * 2 ** (attempt - 1))  # exponential backoff

        calls = []
        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionError("connection reset")
            return "connected"

        print(retry(flaky), len(calls))   # connected 3
    ''', caption="Python — retry with exponential backoff")
    yield dodont(
        "Retry only *transient* errors (timeouts, connection resets), cap the attempts, back off exponentially (add jitter in production) and log each failure.",
        "Retrying everything — a `ValueError` from bad input will fail identically every time.",
    )
    yield section("Interview questions", "message-question")
    yield qa("Why shouldn't you write `except:` or `except BaseException:`?",
             "They catch `KeyboardInterrupt` and `SystemExit` too, so Ctrl-C and `sys.exit()` stop working, and they hide real bugs. Catch `Exception` at most (e.g. at a top-level request handler that logs and continues), and specific types everywhere else.")
    yield qa("What is the difference between `raise X from e` and `raise X from None`?",
             "`from e` records `e` as the explicit cause (`__cause__`) and the traceback shows both, linked by “direct cause”. `from None` suppresses the context so only the new exception is shown — useful when the original is an implementation detail.")
    yield qa("What does `except*` do?",
             "It matches exceptions *inside* an `ExceptionGroup`. Each `except*` clause receives a sub-group of the matching exceptions; multiple clauses can run for the same group, and any unmatched exceptions are re-raised in a new group.")
    yield qa("When would you define a custom exception?",
             "When callers need to react to a specific domain failure (`CardDeclined`, `RateLimited`) differently from others. Give the library one base class so callers can catch all of its errors, and attach structured data as attributes.")


@topic(G, "modules-packages", "Modules, Packages & Imports", "package")
def _():
    yield lead("A module is a `.py` file; a package is a folder of modules. `import` finds, runs and caches them — understanding that cycle explains `__name__`, circular imports and `sys.modules`.")
    yield section("Importing", "download")
    yield code('''
        import math                          # whole module
        from collections import Counter      # one name
        import datetime as dt                # alias
        print(math.sqrt(16), Counter("aab")["a"], dt.date(2026, 1, 1).year)   # 4.0 2 2026
    ''')
    yield steps(
        ("Check the cache", "If the name is already in `sys.modules`, that module object is returned immediately."),
        ("Find", "Otherwise Python searches `sys.path`: the script's folder, `PYTHONPATH`, the standard library, then `site-packages`."),
        ("Execute once", "A new module object is created and the file's top-level code runs in its namespace."),
        ("Cache & bind", "The module is stored in `sys.modules` and the name is bound in the importing namespace."),
    )
    yield table(
        ["Form", "Binds", "Use when"],
        ["`import json`", "`json`", "Default — the call site shows where names come from (`json.dumps`)"],
        ["`import numpy as np`", "`np`", "Conventional short aliases"],
        ["`from pathlib import Path`", "`Path`", "Names you use a lot"],
        ["`from os import *`", "Every public name", "Almost never — pollutes the namespace and hides origins"],
    )
    yield section("Imports run once and are cached", "database")
    yield code('''
        import importlib, sys, tempfile
        from pathlib import Path

        folder = tempfile.mkdtemp()
        Path(folder, "lvn_greet.py").write_text('print("module body runs")\\nVALUE = 1\\n')
        sys.path.insert(0, folder)

        import lvn_greet                  # runs the file: prints "module body runs"
        import lvn_greet                  # cached in sys.modules: nothing printed
        print("lvn_greet" in sys.modules, lvn_greet.VALUE)

        lvn_greet.VALUE = 99
        importlib.reload(lvn_greet)       # re-executes the file (prints again), resetting VALUE
        print(lvn_greet.VALUE)

        sys.path.remove(folder)
        del sys.modules["lvn_greet"]
    ''', check=False)
    yield output('''
        module body runs
        True 1
        module body runs
        1
    ''')
    yield note("Because a module runs once, module-level variables act like singletons — every importer shares the same object. It's also why top-level side effects (connecting to a DB, printing) happen at import time: keep them out of importable modules.")
    yield section("`if __name__ == \"__main__\":`", "player-play")
    yield code('''
        # utils.py
        def add(a, b):
            return a + b

        if __name__ == "__main__":    # True only when run directly: python utils.py
            print(add(2, 3))          # 5
    ''')
    yield note("When the file is imported, `__name__` is `\"utils\"`, so the demo code doesn't run. Use this guard for scripts, tests and anything with side effects.")
    yield section("Module attributes", "info-circle")
    yield code('''
        import json, os

        print(json.__name__, os.path.__name__)                   # json posixpath
        print(json.__file__.endswith("json/__init__.py"))        # True   ← json is a package
        print(json.__doc__.splitlines()[0])                      # JSON (JavaScript Object Notation) <https://json.org> is a subset of
        print(__name__)                                          # __main__
    ''')
    yield table(
        ["Attribute", "Holds"],
        ["`__name__`", "The module's import name (`\"__main__\"` for the script being run)"],
        ["`__file__`", "Path of the source file (absent for built-in modules like `sys`)"],
        ["`__doc__`", "The module docstring — the first string literal in the file"],
        ["`__all__`", "Names exported by `from module import *`"],
        ["`__path__`", "Only on packages: where to look for submodules"],
    )
    yield section("`__all__` and `import *`", "asterisk")
    yield code('''
        import sys, tempfile
        from pathlib import Path

        folder = tempfile.mkdtemp()
        Path(folder, "lvn_shapes.py").write_text(
            "__all__ = ['area']\\n"
            "def area(r): return 3 * r * r\\n"
            "def debug(): pass\\n"
            "def _helper(): pass\\n"
        )
        sys.path.insert(0, folder)
        from lvn_shapes import *
        print("area" in dir(), "debug" in dir(), "_helper" in dir())   # True False False
        sys.path.remove(folder)
    ''')
    yield p("Without `__all__`, `import *` brings in every name that doesn't start with `_`. With it, only the listed names — `__all__` is how a module declares its public API.")
    yield section("Packages", "folders")
    yield shell('''
        shop/
        ├── __init__.py        # marks a regular package; runs on "import shop"
        ├── __main__.py        # runs on "python -m shop"
        ├── cart.py
        └── payments/
            ├── __init__.py
            └── upi.py

        from shop.cart import Cart            # absolute import (preferred)
        from .cart import Cart                # relative import (only inside the package)
        from ..payments import upi            # two dots = parent package
    ''', caption="Layout")
    yield cards(
        ("`__init__.py`", "Runs when the package is imported. Often empty, or re-exports the public API: `from .cart import Cart`.", "file"),
        ("Namespace packages", "A folder **without** `__init__.py` still imports (PEP 420) and can be split across several directories — used by big plugin ecosystems. Prefer regular packages for your own code.", "folders"),
        ("Relative imports", "`from . import x` works only inside a package; running such a file directly (`python shop/cart.py`) fails — use `python -m shop.cart`.", "arrow-back"),
        ("`python -m pkg.mod`", "Runs a module as a script with the right `sys.path`. `python -m http.server`, `python -m json.tool`, `python -m venv`, `python -m pip`.", "terminal"),
    )
    yield section("Importing by name: importlib", "plug")
    yield code('''
        import importlib

        mod = importlib.import_module("json")                     # module name as a string
        print(mod.dumps([1, 2]))                                  # [1, 2]

        plugin = "collections"                                    # e.g. read from a config file
        Counter = getattr(importlib.import_module(plugin), "Counter")
        print(Counter("aab")["a"])                                # 2
    ''')
    yield section("Circular imports", "refresh-alert")
    yield p("`a.py` imports `b`, and `b.py` imports `a`. The second import finds `a` **half-initialised** in `sys.modules`, so names defined later in `a` don't exist yet.")
    yield output('''
        ImportError: cannot import name 'User' from partially initialized module 'models'
        (most likely due to a circular import)
    ''', caption="Typical error")
    yield ol(
        "**Restructure**: move the shared code into a third module both can import (usually the real fix).",
        "Import the **module**, not the name: `import models` and use `models.User` at call time.",
        "Move the import **inside the function** that needs it (deferred import).",
        "For type hints only, guard with `if typing.TYPE_CHECKING:` and use string annotations.",
    )
    yield section("Virtual environments", "box-multiple")
    yield p("Each project should install its dependencies into its own virtual environment — see **Virtual Environments, pip & Packaging** for the full workflow.")
    yield shell('''
        $ python3 -m venv .venv && source .venv/bin/activate
        (.venv) $ pip install requests
    ''')
    yield qa("What happens when you import a module twice?",
             "The first import finds, executes and caches it in `sys.modules`; the second just returns the cached module object — the file doesn't run again. `importlib.reload` forces re-execution.")
    yield qa("How do you fix a circular import?",
             "Best: move the shared pieces into a separate module. Otherwise import the module rather than names from it, defer the import into a function, or use `TYPE_CHECKING` for imports needed only by type hints.")


@topic(G, "packaging", "Virtual Environments, pip & Packaging", "box-multiple")
def _():
    yield lead("Isolate each project's dependencies in a virtual environment, pin them for reproducible installs, and describe your own project in `pyproject.toml` so it can be installed and published.")
    yield define("Virtual environment", "a directory with its own `python` executable and `site-packages`. Packages installed while it's active go there, not into the system Python — so two projects can use different versions of the same library.")
    yield section("The venv lifecycle", "refresh")
    yield shell('''
        $ python3 -m venv .venv                   # create (once per project; don't commit it)
        $ source .venv/bin/activate               # activate — Windows: .venv\\Scripts\\activate
        (.venv) $ which python                    # → /path/to/project/.venv/bin/python
        (.venv) $ python -m pip install --upgrade pip
        (.venv) $ pip install "requests>=2.31" pytest
        (.venv) $ deactivate                      # back to the system Python
        $ rm -rf .venv                            # environments are disposable: delete & recreate
    ''')
    yield code('''
        import sys
        print("inside a venv:", sys.prefix != sys.base_prefix)   # True inside a venv, False otherwise
        print(sys.version_info >= (3, 10))                      # True
    ''', check=False)
    yield note("Activation only prepends `.venv/bin` to `PATH`. You can skip it entirely by calling the interpreter directly: `.venv/bin/python -m pytest`. Add `.venv/` to `.gitignore`.")
    yield section("pip essentials", "terminal")
    yield table(
        ["Command", "Does"],
        ["`pip install pkg`", "Install the latest compatible version (plus dependencies)"],
        ["`pip install \"pkg==1.4.2\"`", "Install an exact version"],
        ["`pip install -U pkg`", "Upgrade"],
        ["`pip uninstall pkg`", "Remove (dependencies stay installed)"],
        ["`pip list` / `pip list --outdated`", "What's installed / what can be upgraded"],
        ["`pip show pkg`", "Version, location, dependencies of one package"],
        ["`pip freeze > requirements.txt`", "Exact versions of everything installed"],
        ["`pip install -r requirements.txt`", "Install from a requirements file"],
        ["`pip install -e .`", "Editable install of the current project"],
    )
    yield warn("Prefer `python -m pip …` over bare `pip`: it guarantees you're installing into the interpreter you think you are. And never `sudo pip install` into the system Python.")
    yield section("Version specifiers", "versions")
    yield table(
        ["Specifier", "Means"],
        ["`==1.4.2`", "Exactly 1.4.2"],
        ["`>=1.4,<2`", "At least 1.4, below 2.0"],
        ["`~=1.4.2`", "Compatible release: `>=1.4.2, ==1.4.*`"],
        ["`~=1.4`", "`>=1.4, ==1.*` (i.e. below 2.0)"],
        ["`!=1.5.0`", "Anything except 1.5.0"],
        ["`requests[socks]`", "Install with an optional *extra*"],
        ["`tomli; python_version < \"3.11\"`", "Environment marker — only on older Pythons"],
    )
    yield section("requirements.txt vs lock files", "lock")
    yield cards(
        ("Library", "Declares **loose** ranges (`requests>=2.28`) in `pyproject.toml` so it can coexist with other packages.", "books"),
        ("Application", "Pins **exact** versions of every package, including transitive ones, for reproducible deploys.", "rocket"),
        ("`requirements.txt`", "A plain list, often produced by `pip freeze` or `pip-compile`. No hashes by default.", "file-text"),
        ("Lock files", "`uv.lock`, `poetry.lock`, `pylock.toml` (PEP 751): exact versions + hashes for every platform, generated from your declared ranges.", "lock"),
    )
    yield section("pyproject.toml", "file-settings")
    yield shell('''
        [project]
        name = "lvn-notes"
        version = "0.3.0"
        description = "Study notes toolkit"
        readme = "README.md"
        requires-python = ">=3.10"
        dependencies = ["requests>=2.31", "rich~=13.7"]

        [project.optional-dependencies]
        dev = ["pytest>=8", "mypy", "ruff"]

        [project.scripts]
        lvn = "lvn_notes.cli:main"          # installs an `lvn` command

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.ruff]
        line-length = 100
    ''', caption="pyproject.toml")
    yield p("It's plain TOML, so the standard library can read it:")
    yield code('''
        import tomllib

        text = """
        [project]
        name = "lvn-notes"
        requires-python = ">=3.10"
        dependencies = ["requests>=2.31", "rich~=13.7"]
        [project.scripts]
        lvn = "lvn_notes.cli:main"
        """
        meta = tomllib.loads(text)["project"]
        print(meta["name"], meta["dependencies"])   # lvn-notes ['requests>=2.31', 'rich~=13.7']
        print(tomllib.loads(text)["project"]["scripts"]["lvn"])   # lvn_notes.cli:main
    ''')
    yield section("Project layout, editable installs & publishing", "folders")
    yield shell('''
        lvn-notes/
        ├── pyproject.toml
        ├── README.md
        ├── src/
        │   └── lvn_notes/
        │       ├── __init__.py
        │       └── cli.py
        └── tests/
            └── test_cli.py
    ''', caption="src layout")
    yield shell('''
        (.venv) $ pip install -e ".[dev]"      # editable: code changes apply without reinstalling
        (.venv) $ python -m pip install build twine
        (.venv) $ python -m build              # → dist/lvn_notes-0.3.0.tar.gz and .whl
        (.venv) $ twine upload dist/*          # publish to PyPI (use TestPyPI first)
    ''')
    yield note("The `src/` layout stops tests from accidentally importing the package from the working directory — they must use the installed version, exactly like your users.")
    yield table(
        ["Artifact", "What it is"],
        ["sdist (`.tar.gz`)", "Source distribution — built on the user's machine"],
        ["wheel (`.whl`)", "Pre-built zip that installs by just unpacking — fast; platform-specific if it contains C extensions"],
    )
    yield section("The tool landscape", "tools")
    yield table(
        ["Tool", "Role"],
        ["`venv` + `pip`", "Built in. Enough for most projects"],
        ["**uv**", "Very fast Rust replacement for pip / venv / pip-tools; manages Python versions and `uv.lock` (`uv add`, `uv run`)"],
        ["**Poetry**", "Dependency management + lock file + build/publish in one tool"],
        ["**pipx**", "Installs CLI *applications* (black, httpie) each in its own isolated venv"],
        ["**conda**", "Environments with non-Python binaries too (CUDA, MKL) — popular in data science"],
        ["**pyenv**", "Install and switch between several Python versions"],
        ["**pip-tools**", "`pip-compile` turns loose `requirements.in` into pinned `requirements.txt`"],
    )
    yield qa("Why use a virtual environment?",
             "To isolate each project's dependencies: different projects can need different versions of the same library, and installing into the system Python can break OS tools. A venv also makes the dependency list explicit and reproducible.")
    yield qa("What is the difference between `pip freeze` output and `pyproject.toml` dependencies?",
             "`pyproject.toml` lists the *direct* dependencies with compatible ranges — what your code needs. `pip freeze` lists *every* installed package at its exact version — a snapshot for reproducing one environment.")
    yield qa("What does `pip install -e .` do?",
             "An editable (development) install: the package is registered in the environment but points at your source folder, so edits take effect immediately without reinstalling.")


@topic(G, "files-io", "Files & pathlib", "file-text")
def _():
    yield lead("Reading and writing files safely with `with`, text vs binary modes, seeking and chunked reads, `pathlib` for paths, and `shutil` / `tempfile` for everything around them.")
    yield section("Text files", "file")
    yield code('''
        import os, tempfile
        path = os.path.join(tempfile.mkdtemp(), "notes.txt")

        with open(path, "w", encoding="utf-8") as f:     # "w" truncates, "a" appends
            f.write("line one\\nline two\\n")

        with open(path, encoding="utf-8") as f:           # default mode "r"
            for line in f:                                # streams line by line
                print(line.rstrip())
    ''', check=False)
    yield output('''
        line one
        line two
    ''')
    yield table(
        ["Mode", "Meaning"],
        ["`'r'`", "Read (default) — error if missing"],
        ["`'w'`", "Write — creates or **truncates**"],
        ["`'a'`", "Append to the end"],
        ["`'x'`", "Create — error if it exists"],
        ["`'b'`", "Binary, e.g. `'rb'` for images"],
        ["`'+'`", "Read and write"],
    )
    yield warn("Always pass `encoding=\"utf-8\"` for text — the platform default differs between Windows and macOS/Linux.")
    yield section("Reading methods", "book")
    yield code('''
        import io
        f = io.StringIO("alpha\\nbeta\\ngamma\\n")    # behaves like an open text file

        print(f.readline())            # alpha
        print(f.read(3))               # bet
        print(f.readlines())           # ['a\\n', 'gamma\\n']
        print(repr(f.read()))          # ''   ← at the end, read() returns an empty string
    ''', check=False)
    yield output('''
        alpha

        bet
        ['a\\n', 'gamma\\n']
        ''
    ''')
    yield table(
        ["Call", "Returns", "Memory"],
        ["`for line in f`", "One line at a time", "O(1) — best for big files"],
        ["`f.read()`", "The whole file as one string", "Whole file"],
        ["`f.read(n)`", "Up to `n` characters (bytes in binary mode)", "O(n)"],
        ["`f.readline()`", "Next line, including `\\n`", "One line"],
        ["`f.readlines()`", "List of all lines", "Whole file"],
        ["`f.write(s)` / `f.writelines(lines)`", "Write text (no newline added)", "—"],
    )
    yield section("Binary files, chunks & seek/tell", "binary")
    yield code('''
        import os, tempfile
        path = os.path.join(tempfile.mkdtemp(), "data.bin")

        with open(path, "wb") as f:
            f.write(bytes(range(10)))

        chunks = []
        with open(path, "rb") as f:
            while chunk := f.read(4):             # fixed-size chunks: constant memory
                chunks.append(chunk)
        print(chunks)                             # [b'\\x00\\x01\\x02\\x03', b'\\x04\\x05\\x06\\x07', b'\\x08\\t']

        with open(path, "rb") as f:
            f.seek(6)                             # jump to byte offset 6
            print(f.tell(), f.read(2))            # 6 b'\\x06\\x07'
            f.seek(-1, os.SEEK_END)               # 1 byte before the end
            print(f.read())                       # b'\\t'
    ''')
    yield note("In text mode, `seek` only accepts offsets previously returned by `tell()` (or 0) because characters can be several bytes. Use binary mode for random access. Hashing a big file? Read it in chunks and call `h.update(chunk)`.")
    yield section("Temporary files & directories", "clock")
    yield code('''
        import os, tempfile

        with tempfile.TemporaryDirectory() as d:          # deleted with everything inside
            path = os.path.join(d, "scratch.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("draft")
            print(os.path.exists(path))                   # True
        print(os.path.exists(d))                          # False

        with tempfile.NamedTemporaryFile("w+", suffix=".txt", encoding="utf-8") as tmp:
            tmp.write("scratch")
            tmp.seek(0)                                   # rewind before reading back
            print(tmp.read(), tmp.name.endswith(".txt"))  # scratch True
    ''')
    yield section("pathlib", "folder")
    yield code('''
        from pathlib import Path
        import tempfile

        root = Path(tempfile.mkdtemp())
        report = root / "reports" / "2026.txt"      # "/" joins paths
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("ok", encoding="utf-8")

        print(report.name, report.stem, report.suffix)   # 2026.txt 2026 .txt
        print(report.read_text(encoding="utf-8"))         # ok
        print([p.name for p in root.rglob("*.txt")])      # ['2026.txt']
        print(report.relative_to(root).as_posix())        # reports/2026.txt
        print(report.with_suffix(".md").name)             # 2026.md
    ''')
    yield table(
        ["Task", "`os` / `os.path`", "`pathlib`"],
        ["Join", "`os.path.join(a, b)`", "`Path(a) / b`"],
        ["File name / extension", "`os.path.basename(p)`, `os.path.splitext(p)`", "`p.name`, `p.stem`, `p.suffix`"],
        ["Parent folder", "`os.path.dirname(p)`", "`p.parent`"],
        ["Exists / is file", "`os.path.exists(p)`, `os.path.isfile(p)`", "`p.exists()`, `p.is_file()`"],
        ["Make folders", "`os.makedirs(p, exist_ok=True)`", "`p.mkdir(parents=True, exist_ok=True)`"],
        ["List / pattern match", "`os.listdir(p)`, `glob.glob('*.py')`", "`p.iterdir()`, `p.glob('*.py')`, `p.rglob('*.py')`"],
        ["Read whole file", "`open(p).read()`", "`p.read_text(encoding=…)`, `p.read_bytes()`"],
        ["Absolute path", "`os.path.abspath(p)`", "`p.resolve()`"],
    )
    yield note("Prefer `pathlib` in new code — paths become objects with methods instead of strings passed to functions. Every standard-library function that takes a path also accepts a `Path`.")
    yield section("glob & shutil: finding, copying, moving", "copy")
    yield code('''
        import glob, os, shutil, tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ["a.py", "b.py", "notes.md"]:
                (root / name).write_text(name, encoding="utf-8")

            print(sorted(p.name for p in root.glob("*.py")))                          # ['a.py', 'b.py']
            print(sorted(os.path.basename(p) for p in glob.glob(str(root / "*.md"))))  # ['notes.md']

            backup = root / "backup"
            backup.mkdir()
            shutil.copy(root / "a.py", backup)                  # copy into a folder
            shutil.move(root / "notes.md", backup / "README.md")  # move + rename
            print(sorted(p.name for p in backup.iterdir()))     # ['README.md', 'a.py']

            shutil.rmtree(backup)                               # delete a whole tree
            print(backup.exists())                              # False
    ''')
    yield section("Safe writes", "shield-check")
    yield code('''
        import os, tempfile
        from pathlib import Path

        def atomic_write(path: Path, text: str) -> None:
            """Readers see either the old file or the new one — never half a file."""
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, path)            # atomic rename on the same filesystem

        target = Path(tempfile.mkdtemp()) / "settings.json"
        atomic_write(target, '{"theme": "dark"}')
        print(target.read_text(encoding="utf-8"))   # {"theme": "dark"}
    ''')
    yield dodont(
        "Use `with open(...)`, pass `encoding=\"utf-8\"`, stream big files line by line or in chunks, and use `tempfile` for scratch files.",
        "Calling `open()` without closing it, `read()` on multi-GB files, or building paths with string `+` (`folder + \"/\" + name`).",
    )
    yield p("Structured formats — JSON, CSV, pickle, TOML — are covered in **Serialization: JSON, CSV & pickle**.")
    yield qa("How would you process a 10 GB log file?",
             "Stream it: `with open(path, encoding='utf-8') as f: for line in f:` keeps one line in memory at a time. For binary data read fixed-size chunks with `f.read(1 << 20)`. Combine with generators to build a lazy pipeline.")


@topic(G, "serialization", "Serialization: JSON, CSV & pickle", "file-code")
def _():
    yield lead("Turning Python objects into bytes or text and back — JSON for APIs, CSV for tables, TOML/INI for config, pickle for Python-only caches, and `struct` for binary formats.")
    yield table(
        ["Format", "Module", "Human-readable", "Cross-language", "Safe on untrusted input"],
        ["JSON", "`json`", "Yes", "Yes", "Yes"],
        ["CSV", "`csv`", "Yes", "Yes", "Yes"],
        ["TOML", "`tomllib` (read-only)", "Yes", "Yes", "Yes"],
        ["INI", "`configparser`", "Yes", "Mostly", "Yes"],
        ["pickle", "`pickle`", "No", "**Python only**", "**No — can run code**"],
        ["SQLite", "`sqlite3`", "No (queryable)", "Yes", "Yes"],
        ["Packed binary", "`struct`", "No", "Yes (you define the layout)", "Yes"],
    )
    yield section("JSON basics & type mapping", "braces")
    yield code('''
        import json
        user = {"name": "Asha", "skills": ["python", "sql"], "active": True, "manager": None}
        text = json.dumps(user)                  # object → str
        print(text)                              # {"name": "Asha", "skills": ["python", "sql"], "active": true, "manager": null}
        print(json.loads(text)["skills"][0])     # python

        print(json.loads(json.dumps({1: (1, 2)})))   # {'1': [1, 2]}   ← int keys become strings, tuples become lists
    ''')
    yield table(
        ["Python", "JSON", "Back to Python"],
        ["`dict`", "object `{}`", "`dict` (keys always `str`)"],
        ["`list`, `tuple`", "array `[]`", "`list`"],
        ["`str`", "string", "`str`"],
        ["`int`, `float`", "number", "`int` / `float`"],
        ["`True` / `False`", "`true` / `false`", "`bool`"],
        ["`None`", "`null`", "`None`"],
        ["`set`, `datetime`, `Decimal`, objects", "**TypeError**", "— convert first"],
    )
    yield note("`dumps` / `loads` work with strings; `dump(obj, f)` / `load(f)` with open files.")
    yield section("Formatting options", "adjustments")
    yield code('''
        import json
        data = {"name": "Zoë", "tags": ["a", "b"], "id": 7}

        print(json.dumps(data))                                         # {"name": "Zo\\u00eb", "tags": ["a", "b"], "id": 7}
        print(json.dumps(data, ensure_ascii=False, sort_keys=True))     # {"id": 7, "name": "Zoë", "tags": ["a", "b"]}
        print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))   # {"name":"Zoë","tags":["a","b"],"id":7}
    ''')
    yield code('''
        import json
        print(json.dumps({"id": 7, "tags": ["a", "b"]}, indent=2))
    ''', check=False)
    yield output('''
        {
          "id": 7,
          "tags": [
            "a",
            "b"
          ]
        }
    ''')
    yield table(
        ["Option", "Effect"],
        ["`indent=2`", "Pretty-print (config files, debugging)"],
        ["`sort_keys=True`", "Stable key order — diff-friendly output, cache keys"],
        ["`ensure_ascii=False`", "Keep non-ASCII characters instead of `\\uXXXX` escapes"],
        ["`separators=(',', ':')`", "Most compact output (network payloads)"],
        ["`default=fn`", "Called for objects JSON can't encode"],
        ["`allow_nan=False`", "Reject `NaN`/`Infinity`, which are not valid JSON"],
    )
    yield section("Custom types: `default` and `object_hook`", "transform")
    yield code('''
        import json
        from dataclasses import dataclass, asdict, is_dataclass
        from datetime import date

        @dataclass
        class Event:
            title: str
            day: date
            tags: set

        def encode(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            if isinstance(obj, set):
                return sorted(obj)
            if is_dataclass(obj):
                return asdict(obj)
            raise TypeError(f"{type(obj).__name__} is not JSON serializable")

        text = json.dumps(Event("launch", date(2026, 9, 29), {"b", "a"}), default=encode)
        print(text)                                  # {"title": "launch", "day": "2026-09-29", "tags": ["a", "b"]}

        def decode(d):                               # called for every JSON object, innermost first
            if "day" in d:
                d["day"] = date.fromisoformat(d["day"])
            return d

        back = json.loads(text, object_hook=decode)
        print(back["day"].year, type(back["day"]).__name__)   # 2026 date
    ''')
    yield code('''
        import json
        try:
            json.loads("{'single': 'quotes'}")        # Python-style dict text is NOT JSON
        except json.JSONDecodeError as e:
            print(e.msg, "at position", e.pos)        # Expecting property name enclosed in double quotes at position 1
    ''')
    yield section("CSV: reading & writing", "table")
    yield code('''
        import csv, io

        rows = [{"name": "Asha", "city": "Pune, MH"}, {"name": "Ravi", "city": 'Say "hi"'}]
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["name", "city"])
        writer.writeheader()
        writer.writerows(rows)
        print(buf.getvalue().splitlines())   # ['name,city', 'Asha,"Pune, MH"', 'Ravi,"Say ""hi"""']   ← commas and quotes are escaped for you

        reader = csv.reader(io.StringIO(buf.getvalue()))
        header = next(reader)
        print(header, list(reader))       # ['name', 'city'] [['Asha', 'Pune, MH'], ['Ravi', 'Say "hi"']]

        raw = "name,score\\nasha,91\\nravi,84\\n"
        scores = [int(r["score"]) for r in csv.DictReader(io.StringIO(raw))]
        print(sum(scores) / len(scores))  # 87.5
    ''')
    yield code('''
        import csv, io
        tsv = "a\\tb\\n1\\t2\\n"
        print(list(csv.reader(io.StringIO(tsv), delimiter="\\t")))    # [['a', 'b'], ['1', '2']]

        buf = io.StringIO()
        csv.writer(buf, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\\n").writerow(["x", 1.5, 2])
        print(buf.getvalue().strip())                                # "x",1.5,2
    ''')
    yield warn("Open CSV files with `open(path, \"w\", newline=\"\", encoding=\"utf-8\")`. Without `newline=\"\"` you get blank lines between rows on Windows. And never split lines on `,` by hand — quoted fields contain commas.")
    yield note("Every CSV value is read as a **string** — convert types yourself. For heavy tabular work use pandas (`pd.read_csv`).")
    yield section("pickle — Python objects as bytes", "package")
    yield code('''
        import pickle

        data = {"ids": (1, 2, 3), "tags": {"py"}, "nested": [b"raw", None, 3.5]}
        blob = pickle.dumps(data)                    # tuples, sets, bytes: all preserved
        restored = pickle.loads(blob)
        print(type(blob).__name__, restored == data, type(restored["ids"]).__name__)   # bytes True tuple
    ''')
    yield warn("**Never unpickle data from an untrusted source.** A pickle can instruct the loader to call any function (via `__reduce__`), i.e. run arbitrary code. Use JSON for anything that crosses a trust boundary.", "Security")
    yield cards(
        ("How it stores classes", "By *import path* (`module.ClassName`), not code — the class must be importable when loading, and renaming it breaks old pickles.", "link"),
        ("Good uses", "Caching intermediate results, passing objects between your own processes (`multiprocessing` uses pickle).", "check"),
        ("Bad uses", "Long-term storage, APIs, anything shared across Python versions or teams.", "x"),
        ("`shelve`", "A persistent dict backed by pickle: `with shelve.open('cache') as db: db['k'] = obj`.", "archive"),
    )
    yield section("sqlite3 — a database in the standard library", "database")
    yield code('''
        import sqlite3

        con = sqlite3.connect(":memory:")            # or a file path
        con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        with con:                                    # commits on success, rolls back on error
            con.executemany("INSERT INTO users (name) VALUES (?)", [("Asha",), ("Ravi",)])
        print(con.execute("SELECT id, name FROM users ORDER BY id").fetchall())   # [(1, 'Asha'), (2, 'Ravi')]
        print(con.execute("SELECT name FROM users WHERE id = ?", (2,)).fetchone())  # ('Ravi',)
        con.close()
    ''')
    yield warn("Always pass values as parameters (`?`), never with f-strings — string-built SQL is an injection hole.")
    yield section("Config files: TOML & INI", "settings")
    yield code('''
        import tomllib, configparser

        cfg = tomllib.loads("""
        [server]
        host = "0.0.0.0"
        port = 8080
        debug = false

        [database]
        pool = { min = 1, max = 5 }
        """)
        print(cfg["server"]["port"], cfg["server"]["debug"], cfg["database"]["pool"]["max"])   # 8080 False 5

        cp = configparser.ConfigParser()
        cp.read_string("""
        [app]
        name = notes
        workers = 4
        debug = yes
        """)
        print(cp["app"]["name"], cp.getint("app", "workers"), cp.getboolean("app", "debug"))   # notes 4 True
    ''')
    yield note("TOML has real types (ints, booleans, dates, arrays); INI values are all strings until you call `getint` / `getboolean`. `tomllib` (3.11+) only reads — write TOML with the third-party `tomli-w`. Use `tomllib.load` with a file opened in **binary** mode.")
    yield section("Binary layouts with struct", "binary")
    yield code('''
        import struct

        # "<" little-endian, H = unsigned 16-bit, I = unsigned 32-bit, f = 32-bit float
        packed = struct.pack("<HIf", 7, 65536, 1.5)
        print(len(packed), packed.hex())             # 10 0700000001000000c03f
        print(struct.unpack("<HIf", packed))         # (7, 65536, 1.5)
        print(struct.calcsize("<HIf"), struct.calcsize("HIf"))   # 10 12   ← native mode adds alignment padding
    ''')
    yield qa("JSON vs pickle — when would you use each?",
             "JSON for data exchanged with other programs or stored long-term: it's text, language-neutral and safe to parse. Pickle only for short-lived, trusted, Python-to-Python data (caches, IPC) — it handles almost any Python object but is insecure and version-fragile.")
    yield qa("How do you serialize a datetime or a custom object to JSON?",
             "Pass `default=` to `json.dumps` — a function that converts unsupported objects (e.g. `dt.isoformat()`, `dataclasses.asdict(obj)`) — or subclass `json.JSONEncoder`. Decode with `object_hook=` to turn the dicts back into rich types.")
