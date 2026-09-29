from kit import *
from sample_db import sql, dialect, SCHEMA

G = "Views, Indexes & Programmability"

BIG = SCHEMA + """
CREATE TABLE events (
    event_id   INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    kind       TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 5000)
INSERT INTO events (user_id, kind, created_at)
SELECT i % 500, CASE i % 3 WHEN 0 THEN 'click' WHEN 1 THEN 'view' ELSE 'buy' END,
       date('2024-01-01', '+' || (i % 90) || ' days')
FROM n;

CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
WITH RECURSIVE n(i) AS (SELECT 0 UNION ALL SELECT i + 1 FROM n WHERE i < 499)
INSERT INTO users SELECT i, 'user' || i FROM n;
"""


@topic(G, "views", "Views", "eye")
def _():
    yield lead("A view is a **saved query** that behaves like a table. It stores no data (unless materialised) — every time you select from it, its query runs.")
    yield section("Creating and using a view", "eye-plus")
    yield sql('''
        CREATE VIEW employee_directory AS
        SELECT e.emp_id, e.name, d.name AS department, d.location, m.name AS manager
        FROM employees e
        LEFT JOIN departments d ON d.dept_id = e.dept_id
        LEFT JOIN employees  m ON m.emp_id  = e.manager_id;

        SELECT name, department, manager
        FROM employee_directory
        WHERE location = 'Mumbai'
        ORDER BY emp_id;
    ''', out='''
        name  | department | manager
        ------+------------+--------
        Priya | Sales      | Asha
        Arjun | Sales      | Priya
        Neha  | Sales      | Priya
    ''')
    yield cards(
        ("Simplicity", "Hide complex joins behind a simple name; analysts query `employee_directory`, not four joins.", "wand"),
        ("Security", "Grant access to a view that exposes some columns/rows (no `salary`) instead of the base table.", "lock"),
        ("Stable interface", "Refactor the underlying tables while the view keeps the old shape for existing reports.", "plug"),
        ("Consistency", "One definition of “active customer” or “net revenue” instead of ten copies.", "equal"),
    )
    yield section("A view for business logic", "report-money")
    yield sql('''
        CREATE VIEW order_summary AS
        SELECT o.order_id, o.customer_id, o.order_date, o.status,
               SUM(oi.quantity * oi.unit_price) AS order_total,
               COUNT(*) AS line_count
        FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY o.order_id, o.customer_id, o.order_date, o.status;

        SELECT status, COUNT(*) AS orders, SUM(order_total) AS value
        FROM order_summary
        GROUP BY status
        ORDER BY value DESC;
    ''', out='''
        status    | orders | value
        ----------+--------+-------
        delivered | 4      | 119100
        shipped   | 2      | 23000
        cancelled | 1      | 5000
        pending   | 1      | 1200
    ''')
    yield section("Updatable views", "edit")
    yield p("A simple view over **one** table without aggregates, `DISTINCT` or `GROUP BY` is usually updatable in PostgreSQL, MySQL, SQL Server and Oracle. `WITH CHECK OPTION` rejects writes that would fall outside the view's `WHERE`.")
    yield dialect('''
        CREATE VIEW sales_team AS
        SELECT emp_id, name, salary, dept_id FROM employees WHERE dept_id = 2
        WITH CHECK OPTION;

        UPDATE sales_team SET salary = salary + 1000 WHERE emp_id = 6;   -- OK: updates employees
        UPDATE sales_team SET dept_id = 3 WHERE emp_id = 6;              -- ERROR: row would leave the view
    ''', "PostgreSQL / MySQL / SQL Server / Oracle")
    yield note("SQLite views are read-only; you make them writable with `INSTEAD OF` triggers (see Triggers).", "SQLite")
    yield section("Materialised views", "database")
    yield p("A **materialised view** stores the query result physically, so reads are fast but data is only as fresh as the last refresh. Great for heavy dashboards.")
    yield dialect('''
        CREATE MATERIALIZED VIEW monthly_revenue AS
        SELECT date_trunc('month', order_date) AS month, SUM(total) AS revenue
        FROM order_summary GROUP BY 1;

        REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;   -- needs a unique index
    ''', "PostgreSQL (Oracle: MATERIALIZED VIEW; SQL Server: indexed views)")
    yield table(
        ["", "View", "Materialised view"],
        ["Stores data", "No — query runs on every read", "Yes — a snapshot"],
        ["Freshness", "Always current", "Stale until refreshed"],
        ["Read speed", "Same as the underlying query", "Fast (can be indexed)"],
        ["Write cost", "None", "Refresh cost"],
    )
    yield qa("What is the difference between a view and a table?",
             "A table stores rows. A (regular) view stores only a query; reading it runs the query against the base tables, so it is always up to date and uses no extra storage. Views give abstraction and security; they don't make queries faster by themselves.")
    yield qa("Can you insert into a view?",
             "If the view is *updatable* — typically a single base table, no aggregates/`DISTINCT`/`GROUP BY`/set operators, and it includes all `NOT NULL` columns without defaults. Otherwise, use `INSTEAD OF` triggers (SQL Server, Oracle, PostgreSQL, SQLite).")


@topic(G, "indexes", "Indexes", "list-search")
def _():
    yield lead("An index is a separate, sorted structure that lets the database find rows without scanning the whole table — like the index at the back of a book. It speeds reads and slows writes.")
    yield section("B-tree: the default index", "binary-tree")
    yield p("A B-tree (B+tree) keeps keys sorted in a shallow, balanced tree: a lookup touches ~3–4 pages even for millions of rows (O(log n)), and because keys are sorted it also serves ranges, prefixes and `ORDER BY`.")
    yield table(
        ["Query shape", "Can a B-tree on `col` help?"],
        ["`col = 5`, `col IN (…)`", "Yes — seek"],
        ["`col > 5`, `BETWEEN`, `LIKE 'abc%'`", "Yes — range scan"],
        ["`ORDER BY col`, `MIN/MAX(col)`", "Yes — already sorted"],
        ["`LIKE '%abc'`, `lower(col) = …`, `col + 1 = 6`", "No — needs a full scan (or an expression index)"],
    )
    yield section("Reading a query plan", "route")
    yield p("`EXPLAIN QUERY PLAN` (SQLite) shows how a query will run; read the `detail` column. **SCAN** = read every row; **SEARCH … USING INDEX** = jump straight to matching rows.")
    yield sql('''
        EXPLAIN QUERY PLAN
        SELECT * FROM events WHERE user_id = 42;
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+------------
        2  | 0      | 216     | SCAN events
    ''', setup=BIG)
    yield sql('''
        CREATE INDEX idx_events_user ON events (user_id);

        EXPLAIN QUERY PLAN
        SELECT * FROM events WHERE user_id = 42;
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+------------------------------------------------------
        3  | 0      | 61      | SEARCH events USING INDEX idx_events_user (user_id=?)
    ''', setup=BIG)
    yield table(
        ["Engine", "Show the plan", "Run and measure"],
        ["SQLite", "`EXPLAIN QUERY PLAN …`", "`.timer on` in the shell"],
        ["PostgreSQL", "`EXPLAIN …`", "`EXPLAIN (ANALYZE, BUFFERS) …`"],
        ["MySQL", "`EXPLAIN …` / `EXPLAIN FORMAT=TREE`", "`EXPLAIN ANALYZE …`"],
        ["SQL Server", "Estimated plan (Ctrl+L)", "Actual plan, `SET STATISTICS IO ON`"],
    )
    yield section("Composite indexes and the leftmost-prefix rule", "columns")
    yield p("An index on `(user_id, created_at)` is sorted by `user_id`, then by `created_at` within each user — like a phone book sorted by surname, then first name. It helps queries that constrain a **leftmost prefix** of its columns.")
    yield sql('''
        CREATE INDEX idx_events_user_time ON events (user_id, created_at);

        EXPLAIN QUERY PLAN SELECT * FROM events WHERE user_id = 42 AND created_at >= '2024-03-01';
        EXPLAIN QUERY PLAN SELECT * FROM events WHERE user_id = 42;
        EXPLAIN QUERY PLAN SELECT * FROM events WHERE created_at >= '2024-03-01';
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+----------------------------------------------------------------------------
        3  | 0      | 51      | SEARCH events USING INDEX idx_events_user_time (user_id=? AND created_at>?)

        id | parent | notused | detail
        ---+--------+---------+-----------------------------------------------------------
        3  | 0      | 62      | SEARCH events USING INDEX idx_events_user_time (user_id=?)

        id | parent | notused | detail
        ---+--------+---------+------------
        2  | 0      | 216     | SCAN events
    ''', setup=BIG)
    yield p("The third query cannot use the index: without `user_id`, the `created_at` values are scattered across the whole index. Column order rule of thumb: **equality columns first, then the range/sort column**.")
    yield section("Covering indexes", "shield-check")
    yield p("If the index contains every column the query needs, the engine answers from the index alone and never touches the table.")
    yield sql('''
        CREATE INDEX idx_events_user_kind ON events (user_id, kind);

        EXPLAIN QUERY PLAN
        SELECT kind, COUNT(*) FROM events WHERE user_id = 42 GROUP BY kind;
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+--------------------------------------------------------------------
        6  | 0      | 55      | SEARCH events USING COVERING INDEX idx_events_user_kind (user_id=?)
    ''', setup=BIG)
    yield dialect('''
        -- PostgreSQL 11+ / SQL Server: extra payload columns stored in the leaf, not part of the key
        CREATE INDEX idx_orders_cust ON orders (customer_id) INCLUDE (order_date, status);
    ''', "PostgreSQL / SQL Server (INCLUDE)")
    yield section("Other kinds of index", "category")
    yield sql('''
        CREATE UNIQUE INDEX ux_users_name ON users (name);                          -- also a constraint
        CREATE INDEX idx_events_buy ON events (created_at) WHERE kind = 'buy';      -- partial
        CREATE INDEX idx_emp_lower_name ON employees (lower(name));                 -- expression

        EXPLAIN QUERY PLAN SELECT event_id FROM events WHERE kind = 'buy' AND created_at >= '2024-03-25';
        EXPLAIN QUERY PLAN SELECT * FROM employees WHERE lower(name) = 'sara';
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+-----------------------------------------------------------------
        2  | 0      | 183     | SEARCH events USING COVERING INDEX idx_events_buy (created_at>?)

        id | parent | notused | detail
        ---+--------+---------+-----------------------------------------------------------
        3  | 0      | 61      | SEARCH employees USING INDEX idx_emp_lower_name (<expr>=?)
    ''', setup=BIG)
    yield table(
        ["Index type", "Good for", "Where"],
        ["B-tree", "Equality, ranges, sorting — the default", "All"],
        ["Hash", "Equality only", "PostgreSQL, MySQL MEMORY"],
        ["GIN / full-text", "Arrays, JSONB, text search", "PostgreSQL, MySQL `FULLTEXT`, SQLite FTS5"],
        ["GiST / R-tree / spatial", "Geometry, ranges, nearest neighbour", "PostgreSQL, MySQL, SQLite R*Tree"],
        ["BRIN", "Huge, naturally ordered tables (time series)", "PostgreSQL"],
        ["Bitmap", "Low-cardinality columns in warehouses", "Oracle"],
    )
    yield section("Clustered vs non-clustered", "stack")
    yield cards(
        ("Clustered index", "The table rows themselves are stored in index order — one per table. InnoDB and SQL Server cluster on the primary key; SQLite tables are clustered on `rowid`.", "stack-2"),
        ("Non-clustered (secondary)", "A separate structure of key + pointer (row id or primary key) back to the table. Many per table; a lookup may need an extra hop to fetch the row.", "list-details"),
    )
    yield section("The cost side", "scale")
    yield ul(
        "Every `INSERT`, `DELETE` and indexed-column `UPDATE` must update every index — write-heavy tables should have few.",
        "Indexes take disk and memory (buffer cache).",
        "Low-selectivity columns (`status` with 4 values, booleans) rarely benefit alone — the planner prefers a scan when a large fraction of rows match.",
        "Unused and duplicate indexes (`(a)` next to `(a, b)`) are pure cost; drop them.",
    )
    yield qa("How does an index speed up a query?",
             "It keeps column values sorted in a B-tree with pointers to rows, so the engine can binary-search to the matching keys in O(log n) page reads instead of scanning all rows, and can return rows already sorted for `ORDER BY`. The price is extra storage and slower writes.")
    yield qa("Why might a query not use an index?",
             "The predicate doesn't match the index (function on the column, leading wildcard, implicit type conversion, not the leftmost column of a composite index), `OR` across different columns, low selectivity so a scan is cheaper, stale statistics, or a tiny table.")
    yield qa("Clustered vs non-clustered index?",
             "A clustered index defines the physical order of the table's rows (only one per table, usually the primary key). A non-clustered index is a separate structure with keys and row locators; a table can have many.")


@topic(G, "query-optimization", "Query Optimization", "rocket")
def _():
    yield lead("Most slow queries are fixed by the same handful of habits: read the plan, give the optimizer usable indexes and *sargable* predicates, and fetch less data.")
    yield define("Sargable", "“Search ARGument ABLE” — a predicate the engine can answer with an index seek: the indexed column stands alone on one side of the comparison (`col >= X`), not wrapped in a function or expression.")
    yield section("1. Keep indexed columns bare", "wand")
    yield sql('''
        CREATE INDEX idx_events_created ON events (created_at);

        EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE strftime('%m', created_at) = '03';
        EXPLAIN QUERY PLAN SELECT COUNT(*) FROM events WHERE created_at >= '2024-03-01' AND created_at < '2024-04-01';
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+----------------------------------------------------
        3  | 0      | 213     | SCAN events USING COVERING INDEX idx_events_created

        id | parent | notused | detail
        ---+--------+---------+--------------------------------------------------------------------------------------
        3  | 0      | 153     | SEARCH events USING COVERING INDEX idx_events_created (created_at>? AND created_at<?)
    ''', setup=BIG)
    yield p("Wrapped in `strftime`, every one of the 5 000 index entries has to be read and tested (**SCAN**). The bare-column range **SEARCH**es straight to March and reads only those entries.")
    yield table(
        ["Non-sargable", "Sargable rewrite"],
        ["`WHERE YEAR(order_date) = 2024`", "`WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`"],
        ["`WHERE salary * 12 > 1200000`", "`WHERE salary > 100000`"],
        ["`WHERE lower(email) = 'x@y.in'`", "Store normalised, or index `lower(email)`"],
        ["`WHERE name LIKE '%son'`", "Full-text / trigram index, or reverse-string column"],
        ["`WHERE phone = 9876543210` (text column)", "`WHERE phone = '9876543210'` — avoid implicit casts"],
    )
    yield section("2. Fetch less", "filter")
    yield ul(
        "Select only needed columns — enables covering indexes and reduces I/O and network.",
        "Filter early in `WHERE` (not `HAVING`) and paginate with keyset pagination instead of big `OFFSET`s.",
        "Use `EXISTS` for existence checks instead of `COUNT(*) > 0` or `JOIN … DISTINCT`.",
        "Use `UNION ALL` instead of `UNION` when duplicates are impossible.",
    )
    yield section("3. Avoid row-by-row work", "repeat-off")
    yield dodont(
        "One set-based statement: `UPDATE … WHERE id IN (…)`, `INSERT … SELECT`, window functions instead of correlated subqueries.",
        "The **N+1 query** pattern: fetch 100 orders, then run one query per order for its items (101 round trips). Fetch with a join or `WHERE order_id IN (…)`.",
    )
    yield section("4. Help the planner", "brain")
    yield ul(
        "Keep statistics fresh: `ANALYZE` (PostgreSQL, SQLite), `ANALYZE TABLE` (MySQL), `UPDATE STATISTICS` (SQL Server).",
        "Index foreign-key columns used in joins (`order_items.product_id`) — the PK side is indexed automatically, the FK side usually is not.",
        "Match data types on join columns (`INT` = `INT`, not `INT` = `VARCHAR`).",
        "Break monster queries into CTEs/temp tables when the planner mis-estimates.",
    )
    yield section("A tuning workflow", "list-check")
    yield steps(
        ("Measure", "Find the slow query (slow query log, `pg_stat_statements`, APM). Optimise what is actually slow and frequent."),
        ("Read the plan", "Look for full scans on big tables, huge row estimates vs actuals, temp B-trees for sorts, nested loops over large inputs."),
        ("Fix the cause", "Add/adjust an index, make predicates sargable, rewrite the query, reduce columns/rows."),
        ("Verify", "Re-run `EXPLAIN ANALYZE`, and check write overhead of any new index."),
    )
    yield p("Example: *events of the user named user42*. `events` (5 000 rows) is the “many” side of the join, and its `user_id` column has no index yet:")
    yield sql('''
        EXPLAIN QUERY PLAN
        SELECT u.name, e.kind, e.created_at
        FROM users u JOIN events e ON e.user_id = u.user_id
        WHERE u.name = 'user42';
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+---------------------------------------------
        3  | 0      | 216     | SCAN e
        5  | 0      | 45      | SEARCH u USING INTEGER PRIMARY KEY (rowid=?)
    ''', setup=BIG)
    yield p("The only way in is to scan all 5 000 events and look up each one's user. Index the foreign-key column and the plan flips: scan the small `users` table and seek into `events`.")
    yield sql('''
        CREATE INDEX idx_events_user ON events (user_id);

        EXPLAIN QUERY PLAN
        SELECT u.name, e.kind, e.created_at
        FROM users u JOIN events e ON e.user_id = u.user_id
        WHERE u.name = 'user42';
    ''', out='''
        id | parent | notused | detail
        ---+--------+---------+-------------------------------------------------
        4  | 0      | 216     | SCAN u
        8  | 0      | 61      | SEARCH e USING INDEX idx_events_user (user_id=?)
    ''', setup=BIG)
    yield qa("How would you optimise a slow SQL query?",
             "Reproduce and measure it; read `EXPLAIN (ANALYZE)`; look for full scans, bad row estimates and expensive sorts; add or fix indexes (composite in the right order, covering), make predicates sargable, remove `SELECT *`, replace correlated subqueries/N+1 patterns with joins or window functions, paginate with keysets, refresh statistics — then verify the plan and the write cost.")


@topic(G, "stored-procedures", "Stored Procedures & Functions", "function")
def _():
    yield lead("Stored procedures and user-defined functions are named programs stored **inside** the database — SQL plus variables, conditions, loops and error handling. Syntax is completely dialect-specific.")
    yield table(
        ["", "Stored procedure", "Function (UDF)"],
        ["Called with", "`CALL p(…)` / `EXEC p …`", "Inside a query: `SELECT f(x)`"],
        ["Returns", "Zero or more result sets, `OUT` parameters", "A value (scalar) or a table"],
        ["Side effects (`INSERT`/`UPDATE`)", "Yes", "Usually not allowed (SQL Server, MySQL) / discouraged"],
        ["Transaction control", "Can `COMMIT`/`ROLLBACK` (PostgreSQL 11+ procedures, MySQL, SQL Server)", "No"],
    )
    yield section("MySQL", "code")
    yield dialect('''
        DELIMITER //
        CREATE PROCEDURE give_raise(IN p_dept INT, IN p_pct DECIMAL(5,2), OUT p_rows INT)
        BEGIN
            UPDATE employees
            SET salary = salary * (1 + p_pct / 100)
            WHERE dept_id = p_dept;
            SET p_rows = ROW_COUNT();
        END //
        DELIMITER ;

        CALL give_raise(2, 10, @n);
        SELECT @n;
    ''', "MySQL")
    yield section("PostgreSQL (PL/pgSQL)", "code")
    yield dialect('''
        CREATE OR REPLACE FUNCTION dept_payroll(p_dept INT)
        RETURNS NUMERIC
        LANGUAGE plpgsql STABLE AS $$
        DECLARE total NUMERIC;
        BEGIN
            SELECT COALESCE(SUM(salary), 0) INTO total FROM employees WHERE dept_id = p_dept;
            RETURN total;
        END $$;

        SELECT name, dept_payroll(dept_id) FROM departments;

        CREATE PROCEDURE archive_orders(p_before DATE)
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO orders_archive SELECT * FROM orders WHERE order_date < p_before;
            DELETE FROM orders WHERE order_date < p_before;
            COMMIT;
        END $$;

        CALL archive_orders('2024-01-01');
    ''', "PostgreSQL")
    yield section("SQL Server (T-SQL)", "code")
    yield dialect('''
        CREATE PROCEDURE dbo.GetDeptEmployees
            @DeptId INT,
            @MinSalary INT = 0              -- default parameter
        AS
        BEGIN
            SET NOCOUNT ON;
            BEGIN TRY
                SELECT name, salary FROM employees
                WHERE dept_id = @DeptId AND salary >= @MinSalary
                ORDER BY salary DESC;
            END TRY
            BEGIN CATCH
                THROW;
            END CATCH
        END;

        EXEC dbo.GetDeptEmployees @DeptId = 1, @MinSalary = 100000;
    ''', "SQL Server")
    yield note("SQLite has no stored procedures: it is embedded, so the host program (Python, Java, …) *is* the procedure language. It does let the host register functions — e.g. Python's `sqlite3.Connection.create_function`.", "SQLite")
    yield section("Pros and cons", "scale")
    yield cards(
        ("Pros", "Fewer network round trips for multi-step logic; logic close to the data; can be granted `EXECUTE` without table access; plan reuse.", "thumb-up"),
        ("Cons", "Vendor lock-in; harder to version, test, debug and scale than application code; business logic split across two places.", "thumb-down"),
    )
    yield qa("What is the difference between a stored procedure and a function?",
             "A function returns a value (or table) and is used inside SQL expressions; it generally must not modify data. A procedure is invoked with `CALL`/`EXEC`, can return several result sets and `OUT` parameters, can modify data and (in most engines) control transactions, but cannot be used inside a `SELECT`.")


@topic(G, "triggers", "Triggers", "bolt")
def _():
    yield lead("A trigger is code the database runs **automatically** before or after an `INSERT`, `UPDATE` or `DELETE` on a table — for audit logs, derived columns and integrity rules.")
    yield table(
        ["Part", "Options"],
        ["Timing", "`BEFORE`, `AFTER`, `INSTEAD OF` (views)"],
        ["Event", "`INSERT`, `UPDATE [OF col]`, `DELETE`"],
        ["Granularity", "`FOR EACH ROW` (row-level) or per statement (PostgreSQL, SQL Server)"],
        ["Row values", "`NEW.col` (insert/update), `OLD.col` (update/delete); SQL Server uses `inserted`/`deleted` tables"],
    )
    yield section("Audit log with AFTER UPDATE", "history")
    yield sql('''
        CREATE TABLE salary_audit (
            emp_id     INTEGER,
            old_salary INTEGER,
            new_salary INTEGER,
            changed_at TEXT DEFAULT '2024-06-01'
        );

        CREATE TRIGGER trg_salary_audit
        AFTER UPDATE OF salary ON employees
        FOR EACH ROW
        WHEN NEW.salary <> OLD.salary
        BEGIN
            INSERT INTO salary_audit (emp_id, old_salary, new_salary)
            VALUES (OLD.emp_id, OLD.salary, NEW.salary);
        END;

        UPDATE employees SET salary = salary + 5000 WHERE dept_id = 3;
        UPDATE employees SET name = 'Sara K' WHERE emp_id = 9;       -- salary not touched: no audit row

        SELECT * FROM salary_audit ORDER BY emp_id;
    ''', out='''
        emp_id | old_salary | new_salary | changed_at
        -------+------------+------------+-----------
        8      | 80000      | 85000      | 2024-06-01
        9      | 85000      | 90000      | 2024-06-01
    ''')
    yield section("Validation with BEFORE + RAISE", "shield-x")
    yield sql('''
        CREATE TRIGGER trg_no_big_cut
        BEFORE UPDATE OF salary ON employees
        FOR EACH ROW
        WHEN NEW.salary < OLD.salary * 0.8
        BEGIN
            SELECT RAISE(ABORT, 'salary cut above 20% not allowed');
        END;

        UPDATE employees SET salary = 50000 WHERE emp_id = 2;
    ''', fails=True, err='salary cut above 20% not allowed')
    yield section("Maintaining a derived value", "calculator")
    yield sql('''
        ALTER TABLE products ADD COLUMN units_sold INTEGER NOT NULL DEFAULT 0;
        UPDATE products SET units_sold = (SELECT COALESCE(SUM(quantity), 0) FROM order_items oi
                                          WHERE oi.product_id = products.product_id);

        CREATE TRIGGER trg_units_sold
        AFTER INSERT ON order_items
        FOR EACH ROW
        BEGIN
            UPDATE products SET units_sold = units_sold + NEW.quantity
            WHERE product_id = NEW.product_id;
        END;

        INSERT INTO orders VALUES (109, 5, '2024-03-20', 'pending');
        INSERT INTO order_items VALUES (109, 7, 2, 12000), (109, 6, 3, 20);

        SELECT name, units_sold FROM products WHERE product_id IN (6, 7) ORDER BY product_id;
    ''', out='''
        name    | units_sold
        --------+-----------
        Pen     | 18
        Monitor | 2
    ''')
    yield section("INSTEAD OF: making a view writable", "eye-edit")
    yield sql('''
        CREATE VIEW emp_public AS SELECT emp_id, name, dept_id FROM employees;

        CREATE TRIGGER trg_emp_public_insert
        INSTEAD OF INSERT ON emp_public
        BEGIN
            INSERT INTO employees (emp_id, name, dept_id, salary, hire_date)
            VALUES (NEW.emp_id, NEW.name, NEW.dept_id, 50000, '2024-06-01');
        END;

        INSERT INTO emp_public VALUES (11, 'Tara', 4);
        SELECT emp_id, name, dept_id, salary FROM employees WHERE emp_id = 11;
    ''', out='''
        emp_id | name | dept_id | salary
        -------+------+---------+-------
        11     | Tara | 4       | 50000
    ''')
    yield dialect('''
        -- PostgreSQL: the trigger body is a function
        CREATE FUNCTION set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            NEW.updated_at := now();
            RETURN NEW;
        END $$;

        CREATE TRIGGER trg_touch BEFORE UPDATE ON customers
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    ''', "PostgreSQL")
    yield warn("Triggers are invisible side effects: a simple `UPDATE` can fan out into cascades of hidden writes, slow bulk loads and surprise developers. Keep them small, document them, and prefer constraints for pure integrity rules.")
    yield qa("What are triggers used for, and what are their drawbacks?",
             "Audit trails, keeping denormalised/derived columns in sync, enforcing complex rules constraints can't express, and making views writable. Drawbacks: hidden logic, harder debugging, performance cost on every write (especially row-level triggers on bulk operations), and possible trigger chains.")
    yield qa("BEFORE vs AFTER trigger?",
             "`BEFORE` runs before the row is written — use it to validate or modify `NEW` values (or reject the change). `AFTER` runs once the change is applied — use it for side effects like audit rows or updating other tables, when the final values are known.")


@topic(G, "json-in-sql", "JSON in SQL", "braces")
def _():
    yield lead("Modern engines store and query JSON documents inside relational tables — useful for flexible attributes, event payloads and API data, alongside normal columns.")
    yield section("Extracting values", "arrow-down-right")
    yield sql('''
        CREATE TABLE app_events (
            id      INTEGER PRIMARY KEY,
            payload TEXT CHECK (json_valid(payload))
        );
        INSERT INTO app_events (payload) VALUES
            ('{"user": {"id": 7, "name": "Asha"}, "action": "login",    "tags": ["web", "mobile"]}'),
            ('{"user": {"id": 9, "name": "Ravi"}, "action": "purchase", "amount": 2500, "tags": ["web"]}'),
            ('{"user": {"id": 7, "name": "Asha"}, "action": "purchase", "amount": 800}');

        SELECT id,
               payload ->> '$.user.name'           AS user_name,
               json_extract(payload, '$.action')   AS action,
               payload ->> '$.amount'              AS amount,
               json_array_length(payload, '$.tags') AS tag_count
        FROM app_events
        ORDER BY id;
    ''', out='''
        id | user_name | action   | amount | tag_count
        ---+-----------+----------+--------+----------
        1  | Asha      | login    | NULL   | 2
        2  | Ravi      | purchase | 2500   | 1
        3  | Asha      | purchase | 800    | NULL
    ''', setup="")
    yield p("`->>` returns a plain SQL value (text/number); `->` returns JSON. Missing keys give `NULL`.")
    yield section("Filtering and aggregating JSON", "filter")
    yield sql('''
        CREATE TABLE app_events (id INTEGER PRIMARY KEY, payload TEXT);
        INSERT INTO app_events (payload) VALUES
            ('{"user": {"id": 7, "name": "Asha"}, "action": "login",    "tags": ["web", "mobile"]}'),
            ('{"user": {"id": 9, "name": "Ravi"}, "action": "purchase", "amount": 2500, "tags": ["web"]}'),
            ('{"user": {"id": 7, "name": "Asha"}, "action": "purchase", "amount": 800}');

        SELECT payload ->> '$.user.name' AS user_name, SUM(payload ->> '$.amount') AS spent
        FROM app_events
        WHERE payload ->> '$.action' = 'purchase'
        GROUP BY user_name
        ORDER BY spent DESC;

        -- expand an array into rows
        SELECT e.id, t.value AS tag
        FROM app_events e, json_each(e.payload, '$.tags') AS t
        ORDER BY e.id, tag;
    ''', out='''
        user_name | spent
        ----------+------
        Ravi      | 2500
        Asha      | 800

        id | tag
        ---+-------
        1  | mobile
        1  | web
        2  | web
    ''', setup="")
    yield section("Building JSON from rows", "code-plus")
    yield sql('''
        SELECT d.name AS department,
               json_group_array(json_object('name', e.name, 'salary', e.salary)) AS staff
        FROM departments d
        JOIN employees e ON e.dept_id = d.dept_id
        WHERE d.dept_id = 3
        GROUP BY d.name;
    ''', out='''
        department | staff
        -----------+------------------------------------------------------------------
        HR         | [{"name":"Vikram","salary":80000},{"name":"Sara","salary":85000}]
    ''')
    yield section("Other engines", "language")
    yield table(
        ["Operation", "PostgreSQL (`jsonb`)", "MySQL (`JSON`)", "SQL Server (text)"],
        ["Get text", "`payload ->> 'action'`, `payload #>> '{user,name}'`", "`payload ->> '$.action'`", "`JSON_VALUE(payload, '$.action')`"],
        ["Get JSON", "`payload -> 'user'`", "`payload -> '$.user'`", "`JSON_QUERY(payload, '$.user')`"],
        ["Contains", "`payload @> '{\"action\":\"login\"}'`", "`JSON_CONTAINS(…)`", "—"],
        ["Array → rows", "`jsonb_array_elements`", "`JSON_TABLE`", "`OPENJSON`"],
        ["Index", "GIN index on `jsonb`", "Index a generated column", "Index a computed column"],
    )
    yield dialect('''
        CREATE TABLE app_events (id BIGSERIAL PRIMARY KEY, payload JSONB NOT NULL);
        CREATE INDEX idx_events_payload ON app_events USING GIN (payload);

        SELECT id FROM app_events WHERE payload @> '{"action": "purchase"}';   -- uses the GIN index
        SELECT payload -> 'user' ->> 'name' FROM app_events;
    ''', "PostgreSQL")
    yield dodont(
        "Use JSON for genuinely variable or rarely-queried attributes and raw payloads; promote fields you filter/join on to real columns (or generated columns) with indexes.",
        "Store everything as one JSON blob — you lose types, constraints, foreign keys, efficient joins and readable queries.",
    )
    yield qa("When should you store JSON in a relational database?",
             "When the structure is truly variable (per-product attributes, third-party webhook payloads, user settings) or the data is read/written as a whole. Keep core, frequently-filtered fields as typed columns; in PostgreSQL prefer `jsonb` (binary, indexable with GIN) over `json`.")
