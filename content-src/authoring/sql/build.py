"""Build content-src/legacy-html/sql/index.html from the topic modules, verifying every snippet.

    python3 content-src/authoring/sql/build.py

Edit the g*_*.py topic modules (and sample_db.py, the shared sample database), not the generated HTML.
Every SQL sample runs on SQLite (in memory) against sample_db.SCHEMA unless it passes its own `setup`;
the build fails if any query errors or prints anything other than its `out` table. Syntax from other
engines (MySQL, PostgreSQL, SQL Server, Oracle) is shown with run=False and labelled with its dialect.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # shared kit.py

import kit
import g01_basics, g02_ddl_dml, g03_querying, g04_functions_aggregation, g05_joins  # noqa: F401,E402  (register topics,
import g06_advanced_queries, g07_objects_performance, g08_transactions_security  # noqa: F401,E402  in sidebar order)
import g09_design, g10_interview  # noqa: F401,E402

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "legacy-html" / "sql" / "index.html"
kit.build(out, "SQL")
