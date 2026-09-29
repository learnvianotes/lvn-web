from kit import *
from sample_db import sql, dialect

G = "Transactions, Concurrency & Security"

BANK = """
CREATE TABLE accounts (
    id      INTEGER PRIMARY KEY,
    owner   TEXT    NOT NULL,
    balance INTEGER NOT NULL CHECK (balance >= 0)
);
INSERT INTO accounts VALUES (1, 'Asha', 1000), (2, 'Ravi', 500);
"""


@topic(G, "transactions-acid", "Transactions & ACID", "arrows-exchange")
def _():
    yield lead("A transaction groups several statements into one unit of work that either **fully happens or not at all**. It is what makes a money transfer safe.")
    yield section("ACID", "shield-check")
    yield table(
        ["Property", "Guarantee", "Mechanism"],
        ["**Atomicity**", "All statements succeed, or none take effect", "Undo/rollback log"],
        ["**Consistency**", "Each transaction moves the DB from one valid state to another (constraints hold)", "Constraints, triggers, your logic"],
        ["**Isolation**", "Concurrent transactions don't see each other's partial work (to a chosen degree)", "Locks and/or MVCC snapshots"],
        ["**Durability**", "Once committed, changes survive crashes and power loss", "Write-ahead log (WAL) flushed to disk"],
    )
    yield section("BEGIN, COMMIT, ROLLBACK", "player-play")
    yield sql('''
        BEGIN;
        UPDATE accounts SET balance = balance - 200 WHERE id = 1;
        UPDATE accounts SET balance = balance + 200 WHERE id = 2;
        COMMIT;

        SELECT * FROM accounts ORDER BY id;
    ''', out='''
        id | owner | balance
        ---+-------+--------
        1  | Asha  | 800
        2  | Ravi  | 700
    ''', setup=BANK)
    yield sql('''
        BEGIN;
        UPDATE accounts SET balance = balance - 200 WHERE id = 1;
        -- …the app detects a problem before crediting Ravi
        ROLLBACK;

        SELECT * FROM accounts ORDER BY id;
    ''', out='''
        id | owner | balance
        ---+-------+--------
        1  | Asha  | 1000
        2  | Ravi  | 500
    ''', setup=BANK)
    yield section("When a statement fails", "alert-triangle")
    yield p("A transfer of 1500 breaks the `CHECK (balance >= 0)` constraint on the debit:")
    yield sql('''
        BEGIN;
        UPDATE accounts SET balance = balance + 1500 WHERE id = 2;   -- credit first
        UPDATE accounts SET balance = balance - 1500 WHERE id = 1;   -- fails
        COMMIT;
    ''', fails=True, err='CHECK constraint failed: balance >= 0', setup=BANK)
    yield warn("In most engines, only the **failing statement** is undone automatically — the earlier credit is still pending inside the open transaction. The application must catch the error and issue `ROLLBACK` (PostgreSQL goes further: the whole transaction is marked aborted and only `ROLLBACK` is accepted). Drivers and ORMs usually wrap this in a `with transaction:` block.")
    yield section("Savepoints: partial rollback", "flag")
    yield sql('''
        BEGIN;
        INSERT INTO accounts VALUES (3, 'Meera', 300);
        SAVEPOINT before_bonus;
        UPDATE accounts SET balance = balance + 10000 WHERE id = 3;   -- mistake
        ROLLBACK TO before_bonus;                                     -- undo only the bonus
        COMMIT;

        SELECT * FROM accounts ORDER BY id;
    ''', out='''
        id | owner | balance
        ---+-------+--------
        1  | Asha  | 1000
        2  | Ravi  | 500
        3  | Meera | 300
    ''', setup=BANK)
    yield section("Autocommit", "player-skip-forward")
    yield p("Outside an explicit `BEGIN`, most engines run in **autocommit** mode: every statement is its own transaction. Oracle is the exception — a transaction starts implicitly and you must `COMMIT`. Python's DB-API and many drivers open transactions for you and require `conn.commit()`.")
    yield good("Keep transactions short: do the reads and computation first, then `BEGIN` → writes → `COMMIT`. Long transactions hold locks, block other users and bloat MVCC history.")
    yield qa("Explain ACID with a bank transfer.",
             "**Atomicity**: debit and credit both apply or neither does. **Consistency**: balances never go negative and total money is preserved (constraints). **Isolation**: a concurrent report never sees money “in flight” (debited but not yet credited). **Durability**: once the user sees “transfer complete”, a crash can't undo it.")
    yield qa("What is the difference between COMMIT and ROLLBACK?",
             "`COMMIT` makes all changes of the transaction permanent and visible to others. `ROLLBACK` discards them, restoring the state at `BEGIN` (or at a `SAVEPOINT` with `ROLLBACK TO`).")


@topic(G, "isolation-levels", "Isolation Levels & Anomalies", "layers-subtract")
def _():
    yield lead("Full isolation is expensive, so SQL defines four levels that trade correctness for concurrency. Each level forbids a different set of **anomalies**.")
    yield section("The anomalies", "bug")
    yield table(
        ["Anomaly", "What happens", "Example"],
        ["**Dirty read**", "T2 reads data T1 has written but not committed", "T1 debits 200, T2 reads 800, T1 rolls back — T2 used a value that never existed"],
        ["**Non-repeatable read**", "T1 reads a row twice and gets different values because T2 committed an update in between", "Balance 1000, then 800 in the same report"],
        ["**Phantom read**", "T1 re-runs a range query and sees new/removed rows committed by T2", "`COUNT(*) WHERE dept_id = 1` is 4, then 5"],
        ["**Lost update**", "T1 and T2 both read 1000, both write back their own result — one update disappears", "Two withdrawals of 100 leave 900 instead of 800"],
        ["**Write skew**", "Two transactions each check a condition, then write different rows, together breaking the rule", "Two on-call doctors each go off duty because “the other is on call”"],
    )
    yield section("The four standard levels", "stairs")
    yield table(
        ["Level", "Dirty read", "Non-repeatable read", "Phantom", "Notes"],
        ["`READ UNCOMMITTED`", "Possible", "Possible", "Possible", "Rarely used; PostgreSQL treats it as Read Committed"],
        ["`READ COMMITTED`", "No", "Possible", "Possible", "**Default** in PostgreSQL, SQL Server, Oracle"],
        ["`REPEATABLE READ`", "No", "No", "Possible (standard) — prevented by snapshots in PostgreSQL/MySQL", "**Default** in MySQL InnoDB"],
        ["`SERIALIZABLE`", "No", "No", "No", "As if transactions ran one at a time; may abort with serialization errors — retry"],
    )
    yield dialect('''
        SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;     -- SQL Server / MySQL (next transaction)
        BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;      -- PostgreSQL
    ''', "PostgreSQL / MySQL / SQL Server")
    yield section("Seeing it: two sessions on one SQLite file", "users")
    yield p("SQLite in WAL mode gives each reading transaction a **snapshot** (like Repeatable Read/Serializable) and allows one writer at a time. Two connections play two users:")
    yield code('''
        import os, sqlite3, tempfile

        path = os.path.join(tempfile.mkdtemp(), "bank.db")
        with sqlite3.connect(path) as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.executescript("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER);"
                             "INSERT INTO accounts VALUES (1, 1000);")

        a = sqlite3.connect(path, isolation_level=None, timeout=0)   # session A
        b = sqlite3.connect(path, isolation_level=None, timeout=0)   # session B
        read = lambda s: s.execute("SELECT balance FROM accounts WHERE id = 1").fetchone()[0]

        b.execute("BEGIN")                  # B starts a read transaction…
        print("B first read:", read(b))     # B first read: 1000

        a.execute("BEGIN IMMEDIATE")        # A takes the write lock
        a.execute("UPDATE accounts SET balance = balance - 200 WHERE id = 1")
        print("A sees its change:", read(a))       # A sees its change: 800
        print("B, A uncommitted:", read(b))        # B, A uncommitted: 1000   ← no dirty read
        a.execute("COMMIT")

        print("B, A committed:", read(b))          # B, A committed: 1000     ← same snapshot: repeatable read
        b.execute("COMMIT")
        print("B, new transaction:", read(b))      # B, new transaction: 800
    ''', caption="Python + SQLite — isolation")
    yield note("Under `READ COMMITTED` (PostgreSQL's default), B's third read would already return 800 — each *statement* sees the latest committed data. That's the non-repeatable read the level allows.")
    yield section("Preventing lost updates", "lock")
    yield cards(
        ("Atomic update", "`UPDATE accounts SET balance = balance - 100 WHERE id = 1` — read-modify-write happens inside one statement. Best when possible.", "bolt"),
        ("Pessimistic lock", "`SELECT … FOR UPDATE` locks the row until commit, so the second transaction waits.", "lock"),
        ("Optimistic check", "`UPDATE … SET balance = :new, version = version + 1 WHERE id = 1 AND version = :read_version` — 0 rows updated means someone else won; retry.", "refresh"),
        ("Serializable", "Let the database detect the conflict and abort one transaction; the app retries.", "shield"),
    )
    yield qa("What isolation level would you use?",
             "Usually the engine default (Read Committed in PostgreSQL/SQL Server/Oracle, Repeatable Read in MySQL) combined with atomic updates or `SELECT … FOR UPDATE` for read-modify-write. Use `SERIALIZABLE` for complex invariants spanning several rows (write skew) and be ready to retry on serialization failures.")
    yield qa("What is a phantom read?",
             "Re-running the same range query in one transaction returns a different *set* of rows because another transaction committed an insert or delete in that range. Non-repeatable reads are about changed values of existing rows; phantoms are about rows appearing or disappearing.")


@topic(G, "locking-concurrency", "Locking, MVCC & Deadlocks", "lock")
def _():
    yield lead("Databases coordinate concurrent transactions with **locks** and, in most modern engines, **MVCC** (multi-version concurrency control), so readers and writers rarely block each other.")
    yield section("Lock types", "lock-square")
    yield table(
        ["Lock", "Taken by", "Compatible with"],
        ["Shared (S)", "Reads that need stability (`FOR SHARE`, lock-based engines)", "Other shared locks"],
        ["Exclusive (X)", "`INSERT`/`UPDATE`/`DELETE`, `SELECT … FOR UPDATE`", "Nothing — others wait"],
        ["Intent (IS/IX)", "Table-level marker before row locks", "Lets the engine check table locks cheaply"],
    )
    yield p("Granularity: **row** locks (InnoDB, PostgreSQL, SQL Server, Oracle) allow high concurrency; **table/page** locks are cheaper but block more; SQLite locks the **whole database** for writing.")
    yield section("MVCC", "versions")
    yield p("Instead of overwriting a row in place, an update creates a **new version**. Each transaction reads the versions that were committed as of its snapshot. Result: *readers don't block writers and writers don't block readers*; only writer-vs-writer on the same row waits.")
    yield ul(
        "PostgreSQL keeps old versions in the table (cleaned up by `VACUUM`).",
        "MySQL InnoDB and Oracle rebuild old versions from undo logs.",
        "SQL Server uses locking by default; `READ_COMMITTED_SNAPSHOT` switches reads to row versions.",
    )
    yield section("Explicit row locks", "hand-stop")
    yield dialect('''
        BEGIN;
        SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;       -- lock the row; others' FOR UPDATE waits
        UPDATE accounts SET balance = balance - 100 WHERE id = 1;
        COMMIT;

        -- job queues: grab the next free job without waiting on rows others locked
        SELECT id FROM jobs WHERE status = 'new'
        ORDER BY id LIMIT 1
        FOR UPDATE SKIP LOCKED;
    ''', "PostgreSQL / MySQL 8 / Oracle")
    yield section("Deadlocks", "arrows-cross")
    yield steps(
        ("T1", "Locks account 1 (`UPDATE … WHERE id = 1`)."),
        ("T2", "Locks account 2 (`UPDATE … WHERE id = 2`)."),
        ("T1", "Wants account 2 → waits for T2."),
        ("T2", "Wants account 1 → waits for T1. Neither can proceed."),
        ("Database", "Detects the cycle and aborts one transaction (the *victim*) with a deadlock error; the other continues."),
    )
    yield dodont(
        "Access rows in a consistent order (e.g. always the lower account id first), keep transactions short, index the columns in `WHERE` so fewer rows are locked, and retry on deadlock errors.",
        "Hold a transaction open while waiting for user input or a slow API call.",
    )
    yield section("SQLite: one writer at a time", "database")
    yield code('''
        import os, sqlite3, tempfile

        path = os.path.join(tempfile.mkdtemp(), "shop.db")
        with sqlite3.connect(path) as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.execute("CREATE TABLE stock (sku TEXT PRIMARY KEY, qty INTEGER)")
            db.execute("INSERT INTO stock VALUES ('PEN', 10)")

        a = sqlite3.connect(path, isolation_level=None, timeout=0)
        b = sqlite3.connect(path, isolation_level=None, timeout=0)

        a.execute("BEGIN IMMEDIATE")                        # A holds the write lock
        a.execute("UPDATE stock SET qty = qty - 1 WHERE sku = 'PEN'")
        try:
            b.execute("UPDATE stock SET qty = qty - 1 WHERE sku = 'PEN'")
        except sqlite3.OperationalError as e:
            print("B:", e)                                  # B: database is locked
        print("B can still read:", b.execute("SELECT qty FROM stock").fetchone()[0])   # B can still read: 10
        a.execute("COMMIT")
        b.execute("UPDATE stock SET qty = qty - 1 WHERE sku = 'PEN'")   # now it succeeds
        print("final:", b.execute("SELECT qty FROM stock").fetchone()[0])              # final: 8
    ''', caption="Python + SQLite — write lock")
    yield p("Real apps set a `timeout` (busy timeout) so the second writer waits instead of failing immediately.")
    yield qa("What is a deadlock and how do databases handle it?",
             "Two (or more) transactions each hold a lock the other needs, so all wait forever. The engine's deadlock detector finds the cycle and rolls back one victim, returning an error (MySQL 1213, SQL Server 1205, PostgreSQL 40P01). Prevent with consistent lock ordering and short transactions; handle by retrying.")
    yield qa("Optimistic vs pessimistic locking?",
             "Pessimistic: lock the data before changing it (`SELECT … FOR UPDATE`), so conflicts wait — good for high contention. Optimistic: don't lock; detect a conflict at write time with a version/timestamp column (`WHERE version = :v`) and retry — good when conflicts are rare, e.g. web forms.")


@topic(G, "sql-injection", "SQL Injection & Parameterized Queries", "shield-lock")
def _():
    yield lead("SQL injection happens when user input is pasted into SQL text, letting an attacker change the query itself. It is still one of the most common and damaging web vulnerabilities — and it is completely preventable.")
    yield section("The vulnerable pattern", "bug")
    yield code('''
        import sqlite3
        db = sqlite3.connect(":memory:")
        db.executescript("""
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT, is_admin INTEGER);
            INSERT INTO users VALUES (1, 'asha', 'x1', 1), (2, 'ravi', 'x2', 0);
        """)

        def find_user_unsafe(name):
            query = f"SELECT id, username FROM users WHERE username = '{name}'"   # ✗ string building
            return db.execute(query).fetchall()

        print(find_user_unsafe("ravi"))              # [(2, 'ravi')]
        print(find_user_unsafe("x' OR '1'='1"))      # [(1, 'asha'), (2, 'ravi')]
    ''', caption="Python — vulnerable")
    yield p("The input `x' OR '1'='1` closes the string and adds a condition that is always true, so the query becomes:")
    yield sql('''
        SELECT id, username FROM users WHERE username = 'x' OR '1'='1'
    ''', run=False)
    yield p("With a login form that is an authentication bypass; with `UNION SELECT` an attacker can read other tables; with stacked queries (`'; DROP TABLE users; --`) in engines/drivers that allow them, destroy data.")
    yield section("The fix: bind parameters", "shield-check")
    yield code('''
        import sqlite3
        db = sqlite3.connect(":memory:")
        db.executescript("""
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT);
            INSERT INTO users VALUES (1, 'asha'), (2, 'ravi');
        """)

        def find_user(name):
            return db.execute("SELECT id, username FROM users WHERE username = ?", (name,)).fetchall()

        print(find_user("ravi"))             # [(2, 'ravi')]
        print(find_user("x' OR '1'='1"))     # []   ← treated as a plain (odd) username
    ''', caption="Python — parameterized")
    yield p("With a placeholder, the SQL text and the data travel **separately**; the database parses the query first and the value can never become code.")
    yield table(
        ["Language / driver", "Placeholder"],
        ["Python `sqlite3`", "`?` or `:name`"],
        ["Python `psycopg`", "`%s` or `%(name)s` (not Python `%` formatting!)"],
        ["Java JDBC", "`PreparedStatement` with `?`"],
        ["Node `pg`", "`$1, $2`"],
        ["PHP PDO", "`?` or `:name`"],
        ["C# ADO.NET", "`@name`"],
    )
    yield section("What parameters can't do", "alert-triangle")
    yield p("Placeholders stand for **values** only — not table names, column names, `ASC`/`DESC` or keywords. For those, map the user's choice through an allow-list:")
    yield code('''
        SORTABLE = {"name": "username", "newest": "id DESC"}

        def order_clause(user_choice):
            return "ORDER BY " + SORTABLE.get(user_choice, "id")    # never interpolate the raw input

        print(order_clause("newest"))                    # ORDER BY id DESC
        print(order_clause("id; DROP TABLE users"))      # ORDER BY id
    ''', caption="Python — allow-list")
    yield section("Defence in depth", "layers-linked")
    yield ul(
        "Parameterized queries or an ORM everywhere — including admin tools and scripts.",
        "Least privilege: the app's DB user can't `DROP`, can't read tables it doesn't need.",
        "Validate input types and lengths; escape output (injection's cousin is XSS).",
        "Don't show raw database errors to users; log them.",
        "Watch ORM escape hatches: raw SQL helpers, `.extra()`, string-built `WHERE` fragments.",
    )
    yield warn("Escaping quotes by hand (`name.replace(\"'\", \"''\")`) is fragile — character sets, numeric contexts and second-order injection (stored input reused later) break it. Use bind parameters.")
    yield qa("What is SQL injection and how do you prevent it?",
             "An attack where untrusted input is concatenated into a SQL string and changes the query's structure (`' OR '1'='1`, `UNION SELECT …`, `; DROP …`). Prevent it with parameterized queries/prepared statements (or an ORM using them), allow-lists for identifiers, least-privilege database accounts, and input validation.")
    yield qa("Do stored procedures prevent SQL injection?",
             "Only if they use parameters properly. A procedure that builds dynamic SQL by concatenating its arguments (`EXEC('SELECT … ' + @name)`) is just as injectable; use `sp_executesql` with parameters (SQL Server) or `EXECUTE … USING` (PostgreSQL).")


@topic(G, "access-control", "Users, Roles, GRANT & REVOKE", "user-shield")
def _():
    yield lead("DCL controls **who** may do **what** on **which** objects. Grant the minimum needed — the principle of least privilege.")
    yield section("Users and roles", "users")
    yield p("A **role** is a named bundle of privileges; users get privileges by being members of roles. Manage roles, not individual grants.")
    yield dialect('''
        CREATE ROLE analyst;                                    -- a group of privileges
        CREATE ROLE app_rw;
        CREATE USER priya WITH PASSWORD 's3cret';               -- PostgreSQL: a role that can log in
        GRANT analyst TO priya;
    ''', "PostgreSQL")
    yield section("GRANT and REVOKE", "key")
    yield dialect('''
        -- read-only reporting
        GRANT SELECT ON employees, departments TO analyst;

        -- the application: data changes, no schema changes
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_rw;

        -- column-level: hide salary from HR assistants
        GRANT SELECT (emp_id, name, dept_id) ON employees TO hr_assistant;

        -- let a user pass on the privilege
        GRANT SELECT ON orders TO team_lead WITH GRANT OPTION;

        REVOKE DELETE ON orders FROM app_rw;
        REVOKE analyst FROM priya;
    ''', "PostgreSQL (MySQL / SQL Server are similar)")
    yield table(
        ["Privilege", "Allows"],
        ["`SELECT`", "Read rows (optionally only some columns)"],
        ["`INSERT` / `UPDATE` / `DELETE`", "Change data"],
        ["`EXECUTE`", "Run a procedure/function"],
        ["`REFERENCES`", "Create a foreign key pointing at the table"],
        ["`CREATE` / `ALTER` / `DROP`", "Schema changes (usually only for migration users)"],
        ["`ALL PRIVILEGES`", "Everything on the object — avoid for applications"],
    )
    yield section("Row-level and view-based security", "eye-off")
    yield sql('''
        -- expose a safe subset through a view and grant access only to the view
        CREATE VIEW employee_public AS
        SELECT emp_id, name, dept_id, hire_date FROM employees;     -- no salary, no email

        SELECT * FROM employee_public WHERE dept_id = 3 ORDER BY emp_id;
    ''', out='''
        emp_id | name   | dept_id | hire_date
        -------+--------+---------+-----------
        8      | Vikram | 3       | 2018-09-05
        9      | Sara   | 3       | 2023-01-09
    ''')
    yield dialect('''
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
        CREATE POLICY own_orders ON orders
            USING (customer_id = current_setting('app.customer_id')::int);
    ''', "PostgreSQL (row-level security)")
    yield note("SQLite has no users or `GRANT`: access control is the file system's permissions plus whatever the application enforces.", "SQLite")
    yield section("Checklist", "list-check")
    yield ul(
        "Separate accounts for the app, migrations, analysts and admins.",
        "No application connects as `root`/`postgres`/`sa`.",
        "Revoke defaults you don't need (e.g. PostgreSQL's `CREATE` on `public` for everyone before v15).",
        "Store credentials in a secret manager; rotate them; require TLS.",
        "Audit privileged actions and review grants periodically.",
    )
    yield qa("What is the difference between GRANT and REVOKE?",
             "`GRANT` gives privileges (or role membership) to a user/role: `GRANT SELECT ON t TO analyst`. `REVOKE` removes them: `REVOKE SELECT ON t FROM analyst`. `WITH GRANT OPTION` lets the grantee pass the privilege on; revoking can then cascade.")
