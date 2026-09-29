from kit import *

G = "Standard Library"


@topic(G, "datetime-module", "Dates & Times (datetime)", "calendar")
def _():
    yield lead("`datetime` models calendar dates, clock times and durations. The golden rule: store and compute in **UTC with time-zone-aware objects**, convert to local time only for display.")
    yield section("The four core types", "category")
    yield table(
        ["Type", "Holds", "Example"],
        ["`date`", "Year, month, day", "`date(2026, 9, 29)`"],
        ["`time`", "Hour … microsecond (+ optional tz)", "`time(14, 5)`"],
        ["`datetime`", "A date and a time (+ optional tz)", "`datetime(2026, 9, 29, 14, 5)`"],
        ["`timedelta`", "A duration: days, seconds, microseconds", "`timedelta(hours=36)`"],
    )
    yield code('''
        from datetime import date, datetime, timedelta

        d = date(2026, 9, 29)
        print(d.year, d.month, d.day, d.weekday())         # 2026 9 29 1   ← Monday is 0
        print(d.isoformat(), d.isocalendar().week)         # 2026-09-29 40

        dt = datetime(2026, 9, 29, 14, 5)
        print(dt.date(), dt.time())                        # 2026-09-29 14:05:00
        print(dt.replace(hour=9, minute=0))                # 2026-09-29 09:00:00
    ''')
    yield note("`date.today()` and `datetime.now()` depend on when and where the code runs — fine in programs, but never hard-code their output in tests. Pass a fixed `datetime` (or a clock function) into code you want to test.")
    yield section("Arithmetic with timedelta", "calculator")
    yield code('''
        from datetime import date, datetime, timedelta

        print(date(2026, 12, 25) - date(2026, 9, 29))          # 87 days, 0:00:00
        print((date(2026, 12, 25) - date(2026, 9, 29)).days)   # 87

        start = datetime(2026, 1, 31, 22, 30)
        print(start + timedelta(days=1, hours=3))              # 2026-02-02 01:30:00
        print(start + timedelta(days=30))                      # 2026-03-02 22:30:00   ← no "add a month" in timedelta

        span = timedelta(hours=36, minutes=15)
        print(span, span.total_seconds())                      # 1 day, 12:15:00 130500.0
        print(datetime(2026, 1, 1) < datetime(2026, 6, 1))     # True
    ''')
    yield warn("`timedelta` has no months or years (their length varies). For “same day next month”, compute it yourself or use `dateutil.relativedelta`.")
    yield section("Formatting & parsing: strftime / strptime", "text-caption")
    yield code('''
        from datetime import datetime

        dt = datetime(2026, 9, 29, 14, 5, 9)
        print(dt.strftime("%d/%m/%Y %H:%M"))              # 29/09/2026 14:05
        print(dt.strftime("%A, %d %B %Y at %I:%M %p"))    # Tuesday, 29 September 2026 at 02:05 PM
        print(f"{dt:%Y-%m-%d}")                           # 2026-09-29   ← format spec in an f-string

        parsed = datetime.strptime("29-Sep-2026 18:30", "%d-%b-%Y %H:%M")
        print(parsed)                                     # 2026-09-29 18:30:00
        print(datetime.fromisoformat("2026-09-29T14:05:00+05:30").utcoffset())   # 5:30:00
    ''')
    yield table(
        ["Code", "Meaning", "Example"],
        ["`%Y` / `%y`", "Year, 4 / 2 digits", "`2026` / `26`"],
        ["`%m` / `%B` / `%b`", "Month number / full name / short name", "`09` / `September` / `Sep`"],
        ["`%d` / `%j`", "Day of month / day of year", "`29` / `272`"],
        ["`%H` / `%I` / `%p`", "Hour 24h / 12h / AM-PM", "`14` / `02` / `PM`"],
        ["`%M` / `%S` / `%f`", "Minute / second / microsecond", "`05` / `09` / `000000`"],
        ["`%A` / `%a`", "Weekday full / short", "`Tuesday` / `Tue`"],
        ["`%z` / `%Z`", "UTC offset / zone name", "`+0530` / `IST`"],
    )
    yield note("Prefer ISO 8601 (`2026-09-29T14:05:00+05:30`) for storage and APIs: `isoformat()` and `fromisoformat()` round-trip it, and it sorts correctly as text.")
    yield section("Naive vs aware; time zones with zoneinfo", "world")
    yield define("Naive vs aware", "a *naive* `datetime` has no `tzinfo` — it's just wall-clock numbers. An *aware* one carries a UTC offset, so it denotes one exact instant.")
    yield code('''
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo

        utc = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)      # an exact instant
        print(utc.astimezone(ZoneInfo("Asia/Kolkata")))             # 2026-03-08 17:30:00+05:30
        print(utc.astimezone(ZoneInfo("America/New_York")))         # 2026-03-08 08:00:00-04:00   ← DST began that morning

        meeting = datetime(2026, 9, 29, 9, 0, tzinfo=ZoneInfo("Europe/London"))
        print(meeting.astimezone(timezone.utc))                     # 2026-09-29 08:00:00+00:00

        naive = datetime(2026, 1, 1)
        try:
            naive < utc
        except TypeError:
            print("can't compare naive and aware")                  # can't compare naive and aware
    ''')
    yield dodont(
        "Use `datetime.now(timezone.utc)` and store UTC; convert with `astimezone(ZoneInfo(...))` when displaying.",
        "`datetime.utcnow()` (deprecated since 3.12 — it returns a *naive* value that looks local) or storing local times without an offset.",
    )
    yield section("Timestamps, `time` and `calendar`", "clock")
    yield code('''
        import time, calendar
        from datetime import datetime, timezone

        instant = datetime(2026, 9, 29, tzinfo=timezone.utc)
        ts = instant.timestamp()                                   # seconds since 1970-01-01 UTC
        print(ts)                                                  # 1790640000.0
        print(datetime.fromtimestamp(ts, tz=timezone.utc))         # 2026-09-29 00:00:00+00:00

        print(calendar.isleap(2028), calendar.monthrange(2026, 2)[1])   # True 28

        t0 = time.perf_counter()                                   # for measuring durations
        sum(range(10_000))
        print(time.perf_counter() - t0 >= 0)                       # True
    ''')
    yield table(
        ["Clock", "Use for"],
        ["`time.time()`", "Wall-clock timestamp (can jump if the system clock changes)"],
        ["`time.monotonic()`", "Timeouts and intervals — never goes backwards"],
        ["`time.perf_counter()`", "Benchmarking — highest resolution"],
        ["`time.sleep(s)`", "Pause the current thread"],
    )
    yield qa("What is the difference between a naive and an aware datetime?",
             "A naive datetime has no time-zone information, so it can't be mapped to a single instant; an aware one has `tzinfo` (an offset), so comparisons and arithmetic across zones are correct. Python refuses to compare the two.")
    yield qa("How should you store timestamps in a database or API?",
             "As UTC — either an aware datetime / `TIMESTAMP WITH TIME ZONE`, or an ISO 8601 string with an offset (`2026-09-29T08:00:00+00:00`). Convert to the user's zone only when displaying.")
    yield qa("Why not use `time.time()` to measure how long code takes?",
             "It follows the system clock, which can be adjusted (NTP, manual changes). Use `time.perf_counter()` (or `monotonic()`), which only moves forward.")


@topic(G, "os-sys", "os, sys, shutil & subprocess", "terminal")
def _():
    yield lead("The modules that let a Python program talk to its environment: the interpreter (`sys`), the operating system (`os`), whole files and folders (`shutil`) and other programs (`subprocess`).")
    yield section("sys — the interpreter", "brand-python")
    yield code('''
        import sys

        print(sys.version_info >= (3, 10))          # True
        print(type(sys.argv).__name__)               # list   ← ["script.py", "arg1", ...]
        print(isinstance(sys.path, list))            # True   ← where imports are searched
        print(sys.maxsize == 2**63 - 1)              # True   ← on 64-bit builds
        print(sys.getrecursionlimit())               # 1000
    ''')
    yield table(
        ["Name", "What it is"],
        ["`sys.argv`", "Command-line arguments; `argv[0]` is the script name"],
        ["`sys.exit(code)`", "Exit by raising `SystemExit` — 0 means success"],
        ["`sys.stdin` / `stdout` / `stderr`", "The standard streams (file objects)"],
        ["`sys.path`", "Module search path"],
        ["`sys.modules`", "Cache of already-imported modules"],
        ["`sys.platform`", "`'linux'`, `'darwin'`, `'win32'`, …"],
        ["`sys.executable`", "Path of the running Python interpreter"],
        ["`sys.getsizeof(obj)`", "Shallow size of an object in bytes"],
    )
    yield section("os — environment, paths, processes", "settings")
    yield code('''
        import os

        os.environ["APP_MODE"] = "test"                     # visible to child processes too
        print(os.environ.get("APP_MODE"))                   # test
        print(os.environ.get("NOT_SET_ANYWHERE", "default"))  # default
        print(os.getenv("NOT_SET_ANYWHERE") is None)        # True
        print(os.path.join("data", "2026", "report.csv"))   # data/2026/report.csv
        print(os.path.splitext("photo.tar.gz"))             # ('photo.tar', '.gz')
        print(os.sep, os.cpu_count() > 0)                   # / True
        del os.environ["APP_MODE"]
    ''')
    yield warn("`os.environ[\"KEY\"]` raises `KeyError` when the variable is missing — use `os.environ.get(\"KEY\", default)` for optional settings, and never print secrets pulled from the environment.")
    yield section("Walking a directory tree", "folders")
    yield code('''
        import os, tempfile

        root = tempfile.mkdtemp()
        for rel in ["src/app.py", "src/util.py", "docs/index.md", "README.md"]:
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w").close()

        print(sorted(os.listdir(root)))                      # ['README.md', 'docs', 'src']
        with os.scandir(root) as entries:                    # faster: file type info included
            print(sorted(e.name for e in entries if e.is_dir()))   # ['docs', 'src']

        found = []
        for dirpath, dirnames, filenames in os.walk(root):
            found += [f for f in filenames if f.endswith(".py")]
        print(sorted(found))                                 # ['app.py', 'util.py']
    ''')
    yield note("For new code, `pathlib.Path` (see *Files, JSON & pathlib*) is usually nicer: `Path(root).rglob(\"*.py\")` replaces the `os.walk` loop.")
    yield section("shutil — high-level file operations", "copy")
    yield code('''
        import shutil, tempfile
        from pathlib import Path

        base = Path(tempfile.mkdtemp())
        (base / "src").mkdir()
        (base / "src" / "a.txt").write_text("hello")

        shutil.copy(base / "src" / "a.txt", base / "b.txt")        # copy one file
        shutil.copytree(base / "src", base / "backup")             # copy a whole tree
        shutil.move(base / "b.txt", base / "c.txt")                # move / rename
        shutil.rmtree(base / "src")                                # delete a tree — careful!
        print(sorted(p.name for p in base.iterdir()))              # ['backup', 'c.txt']
        print(shutil.which("definitely-not-a-real-cmd"))           # None
        archive = shutil.make_archive(str(base / "bundle"), "zip", base / "backup")
        print(Path(archive).name)                                  # bundle.zip
    ''')
    yield section("subprocess — running other programs", "player-play")
    yield code('''
        import subprocess, sys

        result = subprocess.run(
            [sys.executable, "-c", "print('hello from a child process')"],
            capture_output=True, text=True,
        )
        print(result.returncode, result.stdout.strip())   # 0 hello from a child process

        try:
            subprocess.run([sys.executable, "-c", "raise SystemExit(2)"], check=True)
        except subprocess.CalledProcessError as e:
            print("failed with", e.returncode)            # failed with 2

        out = subprocess.run([sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
                             input="piped text", capture_output=True, text=True, timeout=10)
        print(out.stdout.strip())                          # PIPED TEXT
    ''')
    yield table(
        ["Argument", "Effect"],
        ["`[\"cmd\", \"arg\"]` (a list)", "Runs the program directly — no shell, no quoting problems"],
        ["`capture_output=True`", "Collect stdout / stderr instead of printing them"],
        ["`text=True`", "Decode bytes to `str`"],
        ["`check=True`", "Raise `CalledProcessError` on a non-zero exit code"],
        ["`input=…`", "Send data to the child's stdin"],
        ["`timeout=…`", "Kill the child and raise `TimeoutExpired` if it takes too long"],
        ["`cwd=…`, `env=…`", "Working directory / environment for the child"],
    )
    yield warn("Never build a command string from user input with `shell=True` — `f\"ls {name}\"` with `name = \"x; rm -rf ~\"` runs both commands. Pass a list of arguments instead.", "Shell injection")
    yield qa("What is the difference between `os` and `sys`?",
             "`sys` is about the Python interpreter itself — arguments, import path, standard streams, exit, recursion limit. `os` is about the operating system — environment variables, files and directories, processes, permissions.")
    yield qa("How do you run a shell command from Python and get its output?",
             "`subprocess.run([\"git\", \"status\"], capture_output=True, text=True, check=True).stdout`. Use a list of arguments (no `shell=True`), `check=True` to fail loudly, and `timeout` for anything that might hang.")
    yield qa("How does `sys.exit()` work?",
             "It raises `SystemExit`. If nothing catches it, the interpreter exits with that code (0 = success, non-zero = error; a string is printed to stderr and gives exit code 1). `finally` blocks and `with` exits still run.")


@topic(G, "cli-argparse", "Command-Line Scripts & argparse", "prompt")
def _():
    yield lead("Turning a Python file into a proper command-line tool: a `main()` entry point, arguments parsed with `argparse`, clean exit codes and input from files or stdin.")
    yield section("The script skeleton", "template")
    yield code('''
        #!/usr/bin/env python3
        """wordcount — count words in text files."""
        import argparse
        import sys


        def parse_args(argv=None):
            parser = argparse.ArgumentParser(description="Count words in text files.")
            parser.add_argument("files", nargs="+", help="files to read")
            parser.add_argument("-n", "--top", type=int, default=5, help="how many words to show")
            return parser.parse_args(argv)


        def main(argv=None) -> int:
            args = parse_args(argv)
            ...                       # do the work
            return 0                  # exit code: 0 = success


        if __name__ == "__main__":
            raise SystemExit(main())
    ''', run=False)
    yield cards(
        ("Shebang", "`#!/usr/bin/env python3` + `chmod +x wordcount.py` lets you run `./wordcount.py` directly on macOS/Linux.", "hash"),
        ("`main(argv=None)`", "Taking `argv` as a parameter makes the CLI testable: `main([\"a.txt\", \"-n\", \"3\"])`.", "test-pipe"),
        ("Exit codes", "Return 0 on success and non-zero on failure — shells, CI and `&&` chains depend on it.", "logout"),
        ("Entry points", "Packaged tools declare `[project.scripts] wordcount = \"pkg.cli:main\"` in `pyproject.toml`.", "package"),
    )
    yield section("sys.argv — the raw arguments", "list")
    yield code('''
        import sys

        saved = sys.argv
        sys.argv = ["greet.py", "Asha", "--loud"]    # what the shell would pass for: python greet.py Asha --loud
        name = sys.argv[1]
        loud = "--loud" in sys.argv[2:]
        print(("HELLO " if loud else "hello ") + name)   # HELLO Asha
        sys.argv = saved
    ''')
    yield note("`sys.argv` is fine for one or two arguments. As soon as you have options, defaults, types or `--help`, switch to `argparse`.")
    yield section("argparse — positional, optional, flags", "adjustments")
    yield code('''
        import argparse

        parser = argparse.ArgumentParser(prog="resize")
        parser.add_argument("image")                                      # positional, required
        parser.add_argument("-w", "--width", type=int, required=True)     # option with a value
        parser.add_argument("--format", choices=["png", "jpg"], default="png")
        parser.add_argument("-q", "--quiet", action="store_true")         # flag: True if present
        parser.add_argument("-v", "--verbose", action="count", default=0) # -vv → 2
        parser.add_argument("--tag", action="append", default=[])         # repeatable
        parser.add_argument("extra", nargs="*")                           # zero or more

        args = parser.parse_args(["cat.png", "-w", "300", "-vv", "--tag", "a", "--tag", "b", "x", "y"])
        print(args.image, args.width, args.format, args.quiet)   # cat.png 300 png False
        print(args.verbose, args.tag, args.extra)                # 2 ['a', 'b'] ['x', 'y']
        print(vars(args)["width"] * 2)                           # 600
    ''')
    yield table(
        ["Option", "Meaning"],
        ["`type=int` / `float` / `Path` / any callable", "Convert (and validate) the string"],
        ["`default=…`", "Value when the option is absent"],
        ["`required=True`", "Make an option mandatory"],
        ["`choices=[…]`", "Restrict to allowed values"],
        ["`nargs=\"?\" / \"*\" / \"+\" / 2`", "Optional one / any number / at least one / exactly two"],
        ["`action=\"store_true\"`", "Boolean flag"],
        ["`action=\"count\"`", "Count repetitions (`-vvv`)"],
        ["`action=\"append\"`", "Collect repeated options into a list"],
        ["`dest=\"name\"`, `metavar=\"N\"`", "Attribute name / how the value is shown in help"],
    )
    yield section("Errors and --help for free", "help")
    yield code('''
        import argparse, io, contextlib

        parser = argparse.ArgumentParser(prog="resize")
        parser.add_argument("-w", "--width", type=int, required=True)

        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                parser.parse_args(["-w", "wide"])
        except SystemExit as e:
            print("exit code", e.code)                          # exit code 2
        print(err.getvalue().strip().splitlines()[-1])
        # resize: error: argument -w/--width: invalid int value: 'wide'
    ''', check=False)
    yield output('''
        exit code 2
        resize: error: argument -w/--width: invalid int value: 'wide'
    ''')
    yield output('''
        $ python resize.py --help
        usage: resize [-h] -w WIDTH [--format {png,jpg}] [-q] [-v] image

        positional arguments:
          image

        options:
          -h, --help            show this help message and exit
          -w, --width WIDTH
          --format {png,jpg}
          -q, --quiet
          -v, --verbose
    ''', caption="Terminal")
    yield section("Subcommands (git-style)", "git-branch")
    yield code('''
        import argparse

        parser = argparse.ArgumentParser(prog="todo")
        sub = parser.add_subparsers(dest="command", required=True)

        add = sub.add_parser("add", help="add a task")
        add.add_argument("text")
        add.add_argument("--priority", type=int, default=3)

        done = sub.add_parser("done", help="complete a task")
        done.add_argument("id", type=int)

        print(vars(parser.parse_args(["add", "buy milk", "--priority", "1"])))
        # {'command': 'add', 'text': 'buy milk', 'priority': 1}
        print(vars(parser.parse_args(["done", "7"])))    # {'command': 'done', 'id': 7}
    ''', check=False)
    yield output('''
        {'command': 'add', 'text': 'buy milk', 'priority': 1}
        {'command': 'done', 'id': 7}
    ''')
    yield section("Reading input: files or stdin", "file-import")
    yield code('''
        import io, sys

        def count_lines(stream) -> int:
            return sum(1 for line in stream if line.strip())

        saved = sys.stdin
        sys.stdin = io.StringIO("alpha\\n\\nbeta\\ngamma\\n")    # pretend: cat notes.txt | python count.py
        print(count_lines(sys.stdin))                              # 3
        sys.stdin = saved
    ''')
    yield shell('''
        $ python count.py notes.txt            # read a file named on the command line
        $ cat notes.txt | python count.py      # or read from a pipe
        $ python count.py < notes.txt          # or from a redirect
        $ python count.py notes.txt && echo ok # exit code 0 lets the chain continue
    ''')
    yield note("`fileinput.input()` iterates over the lines of every file named in `sys.argv[1:]`, or stdin if there are none — the classic Unix-filter behaviour in one line.")
    yield cards(
        ("`click` / `typer`", "Third-party libraries that build CLIs from decorators or type hints — nicer for big tools.", "sparkles"),
        ("`rich`", "Colour, tables and progress bars in the terminal.", "palette"),
    )
    yield qa("Why use `raise SystemExit(main())` instead of just calling `main()`?",
             "It turns `main`'s return value into the process exit code, so shells and CI can tell success (0) from failure. Keeping logic in `main(argv)` also makes it importable and testable.")
    yield qa("How does argparse report errors?",
             "It prints a usage line and an error message to stderr and exits with status 2 (by raising `SystemExit`). `--help` prints help and exits with 0.")


@topic(G, "logging-module", "Logging", "notes")
def _():
    yield lead("`logging` records what a program is doing — with severity levels, timestamps and destinations you can change without touching the code. It is how production code replaces `print`.")
    yield section("Why not print?", "scale")
    yield table(
        ["", "`print`", "`logging`"],
        ["Severity", "None", "`DEBUG` → `CRITICAL`, filterable"],
        ["Destination", "stdout only", "Console, files, syslog, HTTP… (handlers)"],
        ["Metadata", "Only what you type", "Time, module, line, thread, level (formatters)"],
        ["Turn off / on", "Edit the code", "Change the level or config"],
        ["Libraries", "Pollute the user's output", "Silent unless the app configures logging"],
    )
    yield section("Levels", "stairs")
    yield table(
        ["Level", "Value", "Use for"],
        ["`DEBUG`", "10", "Detailed diagnostics while developing"],
        ["`INFO`", "20", "Normal events: started, user logged in, job finished"],
        ["`WARNING`", "30", "Something unexpected but handled — *the default threshold*"],
        ["`ERROR`", "40", "An operation failed"],
        ["`CRITICAL`", "50", "The program may not be able to continue"],
    )
    yield section("Quick start", "player-play")
    yield code('''
        import logging

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
        log = logging.getLogger(__name__)      # one logger per module

        log.debug("not shown: below INFO")
        log.info("server started on port %d", 8000)
        log.warning("disk %s%% full", 91)
    ''', run=False)
    yield output('''
        2026-09-29 14:05:09,123 INFO __main__: server started on port 8000
        2026-09-29 14:05:09,124 WARNING __main__: disk 91% full
    ''')
    yield note("`basicConfig` configures the root logger **once**, at the application's entry point. Library modules only call `logging.getLogger(__name__)` and log — they never configure handlers.")
    yield section("Loggers, handlers, formatters", "hierarchy")
    yield flow("Logger `app.db`", "level filter", "Handler(s)", "Formatter", "Output")
    yield code('''
        import io, logging

        stream = io.StringIO()                                   # stands in for a console or file
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(levelname)-7s %(name)s | %(message)s"))

        log = logging.getLogger("shop.orders")
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)
        log.propagate = False                                    # don't also send to the root logger

        log.debug("cart has %d items", 3)
        log.info("order %s placed", "A-17")
        log.getChild("payments").error("card declined")          # child logger: shop.orders.payments

        for line in stream.getvalue().splitlines():
            print(line)
    ''', check=False)
    yield output('''
        DEBUG   shop.orders | cart has 3 items
        INFO    shop.orders | order A-17 placed
        ERROR   shop.orders.payments | card declined
    ''')
    yield cards(
        ("Logger", "What you call (`log.info`). Named hierarchically with dots; children pass records up to parents.", "user"),
        ("Handler", "Where records go: `StreamHandler`, `FileHandler`, `RotatingFileHandler`, `TimedRotatingFileHandler`, `SysLogHandler`…", "send"),
        ("Formatter", "How a record looks: `%(asctime)s`, `%(levelname)s`, `%(name)s`, `%(lineno)d`, `%(message)s`…", "text-caption"),
        ("Filter", "Extra rules to drop or enrich records (e.g. add a request id).", "filter"),
    )
    yield section("Logging exceptions", "alert-octagon")
    yield code('''
        import io, logging

        stream = io.StringIO()
        log = logging.getLogger("demo.exc")
        log.addHandler(logging.StreamHandler(stream))
        log.propagate = False

        try:
            1 / 0
        except ZeroDivisionError:
            log.exception("could not compute ratio")      # ERROR level + full traceback

        lines = stream.getvalue().splitlines()
        print(lines[0])            # could not compute ratio
        print(lines[1])            # Traceback (most recent call last):
        print(lines[-1])           # ZeroDivisionError: division by zero
    ''')
    yield section("Configuring a real application", "settings")
    yield code('''
        import logging.config

        logging.config.dictConfig({
            "version": 1,
            "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "plain", "level": "INFO"},
                "file": {"class": "logging.handlers.RotatingFileHandler", "formatter": "plain",
                         "filename": "app.log", "maxBytes": 1_000_000, "backupCount": 3},
            },
            "loggers": {"urllib3": {"level": "WARNING"}},          # quieten a chatty library
            "root": {"level": "DEBUG", "handlers": ["console", "file"]},
        })
    ''', run=False)
    yield section("Best practices", "checklist")
    yield dodont(
        "Pass arguments separately — `log.info(\"user %s\", uid)` — so the string is only built if the record is actually emitted.",
        "`log.info(f\"user {uid}\")` in hot paths (always formatted), logging passwords or tokens, or `except: log.error(e)` without the traceback.",
    )
    yield ul(
        "One logger per module: `log = logging.getLogger(__name__)`.",
        "Libraries add `logging.NullHandler()` to their top-level logger and never call `basicConfig`.",
        "Use `log.exception(...)` inside `except` blocks to keep the traceback.",
        "In services, log structured data (JSON lines) so log platforms can search fields — `python-json-logger` or `structlog`.",
    )
    yield qa("Why is `logging.getLogger(__name__)` the recommended pattern?",
             "It creates a logger named after the module (`shop.orders`), so logger names mirror the package hierarchy. Configuration can then target a whole package (`shop`) or one module, and every record shows where it came from.")
    yield qa("What is the default logging level?",
             "`WARNING`. `debug()` and `info()` messages are dropped until you lower the level (e.g. `basicConfig(level=logging.INFO)`).")
    yield qa("Why use `%s` arguments instead of f-strings in log calls?",
             "Logging formats the message lazily — only if the record passes the level check. An f-string is built on every call even when the message is discarded. `%`-style arguments also let log aggregators group identical message templates.")


@topic(G, "stdlib-tour", "Standard Library Tour", "books")
def _():
    yield lead("“Batteries included”: before installing a package, check the standard library. A map of the modules worth knowing, with a tiny example of each.")
    yield section("Where things live", "map")
    yield table(
        ["Need", "Module(s)", "Covered in"],
        ["Containers & algorithms", "`collections`, `heapq`, `bisect`, `array`", "*Data Structures*"],
        ["Iteration & functions", "`itertools`, `functools`, `operator`", "*Advanced Python*, *Functions*"],
        ["Text", "`string`, `re`, `textwrap`, `difflib`, `unicodedata`", "*Strings & Numbers*"],
        ["Numbers", "`math`, `decimal`, `fractions`, `statistics`, `random`", "*Numbers*, below"],
        ["Files & formats", "`pathlib`, `shutil`, `json`, `csv`, `tomllib`, `pickle`, `sqlite3`, `zipfile`", "*Errors, Modules & Files*"],
        ["Dates", "`datetime`, `zoneinfo`, `time`, `calendar`", "*Dates & Times*"],
        ["OS & processes", "`os`, `sys`, `subprocess`, `argparse`, `logging`", "this group"],
        ["Concurrency", "`threading`, `multiprocessing`, `concurrent.futures`, `asyncio`, `queue`", "*Concurrency*"],
        ["Testing & debugging", "`unittest`, `doctest`, `pdb`, `timeit`, `cProfile`, `tracemalloc`", "*Testing & Tooling*"],
        ["Security & ids", "`hashlib`, `hmac`, `secrets`, `uuid`, `base64`", "below"],
        ["Internet (no network needed to parse)", "`urllib.parse`, `http`, `email`, `html`, `ipaddress`", "below"],
    )
    yield section("random & statistics", "dice")
    yield code('''
        import random, statistics

        random.seed(42)                         # same seed → same sequence (reproducible experiments)
        first = [random.randint(1, 6) for _ in range(5)]
        random.seed(42)
        print(first == [random.randint(1, 6) for _ in range(5)])   # True

        rng = random.Random(7)                  # an independent generator with its own state
        deck = list("AKQJ")
        rng.shuffle(deck)                       # in place
        print(len(rng.sample(range(100), 3)), rng.choice(deck) in deck)   # 3 True

        data = [2, 4, 4, 4, 5, 5, 7, 9]
        print(statistics.mean(data), statistics.median(data), statistics.mode(data))   # 5 4.5 4
        print(statistics.pstdev(data), round(statistics.stdev(data), 3))             # 2.0 2.138
    ''')
    yield warn("`random` is predictable by design — never use it for passwords, tokens or anything security-related. Use `secrets`.")
    yield section("secrets, hashlib, uuid, base64", "lock")
    yield code('''
        import secrets, hashlib, hmac, uuid, base64

        token = secrets.token_urlsafe(16)                  # unpredictable, URL-safe
        print(len(token) >= 16)                            # True
        print(secrets.compare_digest("abc", "abc"))        # True   ← constant-time comparison

        print(hashlib.sha256(b"hello").hexdigest()[:16])   # 2cf24dba5fb0a30e
        sig = hmac.new(b"secret-key", b"payload", hashlib.sha256).hexdigest()
        print(len(sig))                                    # 64

        u = uuid.uuid4()                                   # random unique id
        print(u.version, len(str(u)))                      # 4 36

        encoded = base64.b64encode(b"hi there")
        print(encoded, base64.b64decode(encoded))          # b'aGkgdGhlcmU=' b'hi there'
    ''')
    yield note("Hash passwords with a slow, salted algorithm — `hashlib.scrypt` or `pbkdf2_hmac` (or the `argon2`/`bcrypt` packages) — never plain `sha256`.")
    yield section("Text helpers: string, textwrap, difflib, pprint", "text-wrap")
    yield code('''
        import string, textwrap, difflib, pprint

        print(string.ascii_lowercase[:5], string.digits, string.punctuation[:4])   # abcde 0123456789 !"#$
        print(textwrap.shorten("The quick brown fox jumps over the lazy dog", width=25))   # The quick brown fox [...]
        print(textwrap.wrap("one two three four five", width=9))   # ['one two', 'three', 'four five']
        print(difflib.get_close_matches("pyhton", ["python", "java", "ruby"]))   # ['python']
        print(round(difflib.SequenceMatcher(None, "kitten", "sitting").ratio(), 2))   # 0.62
        print(pprint.pformat({"b": [1, 2], "a": {"x": 1}}))        # {'a': {'x': 1}, 'b': [1, 2]}   ← keys sorted
    ''')
    yield section("urllib.parse, ipaddress, html", "world-www")
    yield code('''
        from urllib.parse import urlparse, parse_qs, urlencode, quote
        import ipaddress, html

        u = urlparse("https://shop.example.com:8443/search?q=red+shoes&page=2#top")
        print(u.scheme, u.hostname, u.port, u.path)        # https shop.example.com 8443 /search
        print(parse_qs(u.query))                           # {'q': ['red shoes'], 'page': ['2']}
        print(urlencode({"q": "café & co", "n": 3}))       # q=caf%C3%A9+%26+co&n=3
        print(quote("a b/c"))                              # a%20b/c

        net = ipaddress.ip_network("10.0.0.0/30")
        print([str(h) for h in net.hosts()])               # ['10.0.0.1', '10.0.0.2']
        print(ipaddress.ip_address("192.168.1.5").is_private)   # True
        print(html.escape("<b>Tom & Jerry</b>"))           # &lt;b&gt;Tom &amp; Jerry&lt;/b&gt;
    ''')
    yield section("Compression & archives in memory", "file-zip")
    yield code('''
        import gzip, io, zipfile

        raw = b"python " * 1000
        packed = gzip.compress(raw)
        print(len(raw), len(packed) < 100, gzip.decompress(packed) == raw)   # 7000 True True

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("notes/a.txt", "alpha")
            zf.writestr("notes/b.txt", "beta")
        with zipfile.ZipFile(buf) as zf:
            print(zf.namelist(), zf.read("notes/b.txt"))   # ['notes/a.txt', 'notes/b.txt'] b'beta'
    ''')
    yield section("weakref, contextvars, dis", "tools")
    yield code('''
        import weakref, dis

        class Big:
            pass

        obj = Big()
        ref = weakref.ref(obj)             # doesn't keep obj alive
        print(ref() is obj)                # True
        del obj
        print(ref())                       # None   ← freed as soon as the last strong reference went

        cache = weakref.WeakValueDictionary()   # entries vanish when values are garbage-collected

        def add(a, b):
            return a + b
        ops = [i.opname for i in dis.get_instructions(add)]
        print("BINARY_OP" in ops)          # True   ← dis shows the bytecode CPython runs
    ''')
    yield cards(
        ("`contextvars`", "Per-task “global” state (request id, user) that works correctly with asyncio, unlike thread-locals.", "variable"),
        ("`copy`", "`copy.copy` / `deepcopy` / `replace` (3.13).", "copy"),
        ("`enum`, `dataclasses`, `typing`", "Model data clearly — see *Object-Oriented Python*.", "box"),
        ("`sqlite3`", "A full SQL database in a file (or in memory), no server needed.", "database"),
        ("`http.server`", "`python -m http.server 8000` serves the current folder — handy for quick tests.", "server"),
        ("`venv`, `pip`, `ensurepip`", "Environments and installers ship with Python.", "box-multiple"),
    )
    yield shell('''
        $ python -m http.server 8000        # static file server
        $ python -m json.tool data.json     # pretty-print / validate JSON
        $ python -m timeit "sum(range(1000))"
        $ python -m venv .venv              # create a virtual environment
        $ python -m zipfile -l bundle.zip   # list an archive
        $ python -m calendar 2026 9         # print a month calendar
    ''', caption="Handy `python -m` one-liners")
    yield qa("When should you reach for a third-party package instead of the standard library?",
             "When the stdlib version is low-level or missing features you need: `requests`/`httpx` over `urllib.request`, `pandas` over `csv` for analysis, `pydantic` for validation, `rich`/`click` for CLIs, `dateutil` for fuzzy date parsing. Start with the stdlib — it has no install step and is stable.")
    yield qa("`random` vs `secrets`?",
             "`random` uses the Mersenne Twister — fast and reproducible with a seed, great for simulations and tests, but predictable. `secrets` uses the OS's cryptographically secure source — use it for tokens, passwords and keys.")
