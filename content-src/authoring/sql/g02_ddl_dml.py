from kit import *
from sample_db import sql, dialect

G = "Defining & Changing Data"

ENROLL = '''
CREATE TABLE enrollments (
    student_id  INTEGER NOT NULL,
    course_id   INTEGER NOT NULL,
    grade       CHAR(1),
    enrolled_on TEXT    NOT NULL DEFAULT CURRENT_DATE,
    status      TEXT    NOT NULL DEFAULT 'active',
    CONSTRAINT pk_enrollment PRIMARY KEY (student_id, course_id),
    CONSTRAINT chk_grade CHECK (grade IN ('A', 'B', 'C', 'D', 'F'))
);
'''


@topic(G, "data-types", "Data Types", "abc")
def _():
    yield lead("Every column has a type that decides what it can hold, how much space it takes and how it compares and sorts. Choose the narrowest type that fits the data *forever*.")
    yield section("Standard SQL types", "list-details")
    yield table(
        ["Category", "Types", "Use for", "Notes"],
        ["Integer", "`SMALLINT`, `INT`, `BIGINT`", "Counts, ids, quantities", "2 / 4 / 8 bytes; `INT` max ≈ 2.1 billion"],
        ["Exact decimal", "`DECIMAL(p, s)` / `NUMERIC(p, s)`", "**Money**, rates", "`DECIMAL(10,2)` = 8 digits before the point, 2 after; no rounding errors"],
        ["Approximate", "`REAL`, `FLOAT`, `DOUBLE PRECISION`", "Measurements, science", "Binary floating point — `0.1 + 0.2 ≠ 0.3`"],
        ["Fixed text", "`CHAR(n)`", "Codes of fixed length (`'IN'`, `'USD'`)", "Padded with spaces to `n`"],
        ["Variable text", "`VARCHAR(n)`, `TEXT`", "Names, emails, descriptions", "Stores only what is used (+1–2 bytes length)"],
        ["Date & time", "`DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ`, `INTERVAL`", "Events, birthdays", "Store UTC; use `TIMESTAMP WITH TIME ZONE` where available"],
        ["Boolean", "`BOOLEAN`", "Flags", "MySQL: `TINYINT(1)`; SQL Server: `BIT`"],
        ["Binary", "`BLOB`, `BYTEA`, `VARBINARY`", "Files, hashes", "Large files usually belong in object storage, not the DB"],
        ["Other", "`UUID`, `JSON`/`JSONB`, `ENUM`, arrays", "Engine-specific", "PostgreSQL is richest here"],
    )
    yield section("CHAR vs VARCHAR", "letter-case")
    yield cards(
        ("`CHAR(10)`", "Always 10 characters — `'abc'` is stored as `'abc'` + 7 spaces. Slightly faster for truly fixed-length values (country codes, hashes).", "ruler"),
        ("`VARCHAR(10)`", "Up to 10 characters, stores only the actual length plus a small length prefix. The default choice for text.", "ruler-2"),
    )
    yield section("Money: DECIMAL, never FLOAT", "currency-rupee")
    yield sql('''
        SELECT 0.1 + 0.2        AS float_sum,
               0.1 + 0.2 = 0.3  AS is_equal;
    ''', out='''
        float_sum           | is_equal
        --------------------+---------
        0.30000000000000004 | 0
    ''', setup="")
    yield p("Floating-point numbers are binary fractions, so decimal values like 0.1 are approximated. `DECIMAL(p, s)` stores exact base-10 digits — use it (or integer paise/cents, as the sample database does) for money.")
    yield section("SQLite: types belong to values", "database")
    yield p("Most engines reject a value that doesn't fit the column type. SQLite uses **type affinity**: the column *prefers* a type and converts when it can, but otherwise stores what it is given. `typeof()` shows the stored type.")
    yield sql('''
        SELECT typeof(42), typeof(4.2), typeof('42'), typeof(NULL), typeof(x'CAFE');

        CREATE TABLE loose (n INTEGER);
        INSERT INTO loose VALUES (7), ('123'), ('abc');
        SELECT n, typeof(n) FROM loose ORDER BY rowid;
    ''', out='''
        typeof(42) | typeof(4.2) | typeof('42') | typeof(NULL) | typeof(x'CAFE')
        -----------+-------------+--------------+--------------+----------------
        integer    | real        | text         | null         | blob

        n   | typeof(n)
        ----+----------
        7   | integer
        123 | integer
        abc | text
    ''', setup="")
    yield p("`'123'` was converted to an integer, but `'abc'` was stored as text in an `INTEGER` column. A `STRICT` table (SQLite 3.37+) behaves like other databases:")
    yield sql('''
        CREATE TABLE strict_t (n INTEGER) STRICT;
        INSERT INTO strict_t VALUES ('abc');
    ''', fails=True, err='cannot store TEXT value in INTEGER column strict_t.n', setup="")
    yield warn("SQLite has no separate `DATE`/`BOOLEAN` storage: dates are stored as ISO-8601 text (`'2024-03-15'`) or numbers, booleans as `0`/`1`. That is why the sample database uses `TEXT` for dates — ISO strings sort and compare correctly.", "SQLite")
    yield section("Choosing types", "checklist")
    yield dodont(
        "Pick the smallest correct type (`INT` over `BIGINT` if it can never exceed 2 billion), `DECIMAL` for money, `DATE`/`TIMESTAMP` for time, and the same type on both sides of a foreign key.",
        "Store dates or numbers as free text in a real engine, use `FLOAT` for money, or give every text column `VARCHAR(255)` without thinking about the real limit.",
    )
    yield qa("What is the difference between DECIMAL and FLOAT?",
             "`DECIMAL(p,s)` is exact base-10 arithmetic with fixed precision — right for money. `FLOAT`/`DOUBLE` are approximate binary floating point: faster and with a huge range, but `0.1 + 0.2` is not exactly `0.3`, so sums of prices drift.")
    yield qa("What is the difference between VARCHAR and TEXT?",
             "In PostgreSQL they are the same storage; `VARCHAR(n)` just adds a length check. In MySQL, `TEXT` columns are stored off-page and have indexing restrictions (need a prefix length) and no default value, so `VARCHAR(n)` is preferred for short strings.")


@topic(G, "create-alter-drop", "CREATE, ALTER, DROP & TRUNCATE", "table-plus")
def _():
    yield lead("DDL commands create and reshape database objects. They change the *schema*, so they are usually run through versioned migration scripts, not by hand.")
    yield section("CREATE TABLE", "table-plus")
    yield sql('''
        CREATE TABLE projects (
            project_id  INTEGER PRIMARY KEY,
            title       VARCHAR(100) NOT NULL,
            budget      DECIMAL(12, 2) DEFAULT 0,
            dept_id     INTEGER REFERENCES departments(dept_id),
            started_on  DATE
        );

        CREATE TABLE IF NOT EXISTS projects (id INTEGER);   -- no error: already exists, skipped

        SELECT name, type, "notnull", dflt_value, pk
        FROM pragma_table_info('projects')
        ORDER BY cid;
    ''', out='''
        name       | type           | notnull | dflt_value | pk
        -----------+----------------+---------+------------+---
        project_id | INTEGER        | 0       | NULL       | 1
        title      | VARCHAR(100)   | 1       | NULL       | 0
        budget     | DECIMAL(12, 2) | 0       | 0          | 0
        dept_id    | INTEGER        | 0       | NULL       | 0
        started_on | DATE           | 0       | NULL       | 0
    ''')
    yield note("`pragma_table_info()` is SQLite's way to describe a table. Elsewhere: `DESCRIBE t` (MySQL), `\\d t` (psql), `sp_help 't'` (SQL Server), or the standard `information_schema.columns` view.")
    yield section("CREATE TABLE … AS SELECT", "copy")
    yield p("Creates a table *and* fills it from a query — handy for snapshots and backups. Constraints and indexes are **not** copied.")
    yield sql('''
        CREATE TABLE eng_staff AS
        SELECT emp_id, name, salary FROM employees WHERE dept_id = 1;

        SELECT * FROM eng_staff ORDER BY emp_id;
    ''', out='''
        emp_id | name  | salary
        -------+-------+-------
        1      | Asha  | 150000
        2      | Ravi  | 120000
        3      | Meera | 95000
        4      | Karan | 95000
    ''')
    yield dialect('''
        SELECT emp_id, name, salary
        INTO eng_staff
        FROM employees WHERE dept_id = 1;
    ''', "SQL Server (SELECT … INTO)")
    yield section("ALTER TABLE", "edit")
    yield sql('''
        CREATE TABLE projects (project_id INTEGER PRIMARY KEY, title TEXT NOT NULL);

        ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'planned';
        ALTER TABLE projects RENAME COLUMN title TO project_name;
        ALTER TABLE projects RENAME TO initiatives;
        INSERT INTO initiatives (project_name) VALUES ('Mobile app');
        ALTER TABLE initiatives DROP COLUMN status;

        SELECT * FROM initiatives;
    ''', out='''
        project_id | project_name
        -----------+-------------
        1          | Mobile app
    ''')
    yield table(
        ["Change", "SQLite", "MySQL", "PostgreSQL"],
        ["Add column", "`ADD COLUMN c T`", "`ADD COLUMN c T`", "`ADD COLUMN c T`"],
        ["Rename column", "`RENAME COLUMN a TO b`", "`RENAME COLUMN a TO b`", "`RENAME COLUMN a TO b`"],
        ["Change type", "not supported — rebuild the table", "`MODIFY COLUMN c NEWTYPE`", "`ALTER COLUMN c TYPE NEWTYPE`"],
        ["Drop column", "`DROP COLUMN c` (3.35+)", "`DROP COLUMN c`", "`DROP COLUMN c`"],
        ["Add constraint", "not supported — rebuild", "`ADD CONSTRAINT …`", "`ADD CONSTRAINT …`"],
    )
    yield dialect('''
        ALTER TABLE employees MODIFY COLUMN name VARCHAR(150) NOT NULL;   -- MySQL
        ALTER TABLE employees ALTER COLUMN name TYPE VARCHAR(150);        -- PostgreSQL
        ALTER TABLE employees ADD CONSTRAINT chk_sal CHECK (salary < 1000000);
    ''', "MySQL / PostgreSQL")
    yield section("DROP, TRUNCATE, DELETE", "trash")
    yield table(
        ["", "`DELETE FROM t`", "`TRUNCATE TABLE t`", "`DROP TABLE t`"],
        ["Removes", "Rows (all, or those matching `WHERE`)", "All rows", "Rows **and** the table definition"],
        ["Category", "DML", "DDL", "DDL"],
        ["`WHERE` allowed", "Yes", "No", "No"],
        ["Speed on big tables", "Slow — row by row, fully logged", "Fast — deallocates pages", "Fast"],
        ["Fires triggers", "Yes (`DELETE` triggers)", "No", "No"],
        ["Resets auto-increment", "No", "Yes (most engines)", "Table is gone"],
        ["Rollback", "Yes", "PostgreSQL/SQL Server: yes in a transaction; MySQL/Oracle: no (auto-commit)", "Same as `TRUNCATE`"],
    )
    yield sql('''
        CREATE TABLE temp_log (msg TEXT);
        INSERT INTO temp_log VALUES ('a'), ('b');

        DELETE FROM temp_log;                 -- SQLite has no TRUNCATE; an unqualified DELETE is optimised the same way
        SELECT COUNT(*) AS rows_left FROM temp_log;

        DROP TABLE temp_log;
        DROP TABLE IF EXISTS temp_log;        -- no error the second time
        SELECT COUNT(*) AS tables_named_temp_log FROM sqlite_schema WHERE name = 'temp_log';
    ''', out='''
        rows_left
        ---------
        0

        tables_named_temp_log
        ---------------------
        0
    ''', setup="")
    yield dialect('''
        TRUNCATE TABLE temp_log;
    ''', "MySQL / PostgreSQL / SQL Server / Oracle")
    yield warn("`DROP` and `TRUNCATE` cannot be undone in MySQL and Oracle (they auto-commit). Take a backup, and never run DDL on production without a reviewed migration.")
    yield qa("DELETE vs TRUNCATE vs DROP?",
             "`DELETE` removes chosen rows one by one (DML, logged, triggers fire, rollback-able). `TRUNCATE` empties the whole table quickly by deallocating storage (DDL, no `WHERE`, no triggers, resets identity). `DROP` removes the table itself — structure, data, indexes, constraints.")
    yield qa("Can TRUNCATE be used on a table referenced by a foreign key?",
             "Generally no — SQL Server and MySQL refuse to truncate a table referenced by a foreign key; PostgreSQL requires `TRUNCATE … CASCADE` to also empty the referencing tables. `DELETE` works if no child rows reference the deleted rows.")


@topic(G, "constraints", "Constraints", "shield-check")
def _():
    yield lead("Constraints are rules the database enforces on every insert and update. They keep bad data out no matter which application, script or person writes it.")
    yield table(
        ["Constraint", "Guarantees", "Sample database"],
        ["`PRIMARY KEY`", "Unique **and** not null; identifies each row", "`employees.emp_id`"],
        ["`FOREIGN KEY`", "Value must exist in the referenced table (or be `NULL`)", "`employees.dept_id → departments`"],
        ["`UNIQUE`", "No two rows share the value (`NULL`s allowed)", "`employees.email`"],
        ["`NOT NULL`", "A value must be supplied", "`employees.name`"],
        ["`CHECK`", "A boolean condition must not be false", "`salary > 0`"],
        ["`DEFAULT`", "Value used when the column is omitted", "`status DEFAULT 'pending'`"],
    )
    yield section("Each one rejecting bad data", "ban")
    yield sql('''
        INSERT INTO employees (emp_id, name, dept_id, salary, hire_date)
        VALUES (11, NULL, 1, 50000, '2024-06-01');
    ''', fails=True, err='NOT NULL constraint failed: employees.name', caption="SQL — NOT NULL")
    yield sql('''
        INSERT INTO employees (emp_id, name, email, dept_id, salary, hire_date)
        VALUES (11, 'Tara', 'asha@corp.in', 1, 50000, '2024-06-01');
    ''', fails=True, err='UNIQUE constraint failed: employees.email', caption="SQL — UNIQUE")
    yield sql('''
        UPDATE employees SET salary = -100 WHERE emp_id = 3;
    ''', fails=True, err='CHECK constraint failed: salary > 0', caption="SQL — CHECK")
    yield sql('''
        INSERT INTO employees (emp_id, name, dept_id, salary, hire_date)
        VALUES (11, 'Tara', 99, 50000, '2024-06-01');     -- there is no department 99
    ''', fails=True, err='FOREIGN KEY constraint failed', caption="SQL — FOREIGN KEY (child side)")
    yield sql('''
        DELETE FROM departments WHERE dept_id = 1;         -- Engineering still has employees
    ''', fails=True, err='FOREIGN KEY constraint failed', caption="SQL — FOREIGN KEY (parent side)")
    yield sql('''
        INSERT INTO employees (emp_id, name, dept_id, salary, hire_date)
        VALUES (1, 'Tara', 1, 50000, '2024-06-01');       -- emp_id 1 is Asha
    ''', fails=True, err='UNIQUE constraint failed: employees.emp_id', caption="SQL — PRIMARY KEY")
    yield note("`UNIQUE` still allows several `NULL`s — Neha and Dev both have a `NULL` email. `NULL` means *unknown*, and two unknowns are not considered equal. (SQL Server is the exception: it allows only one `NULL` in a unique column unless you use a filtered index.)")
    yield section("Named constraints, composite keys, defaults", "tag")
    yield sql('''
        CREATE TABLE enrollments (
            student_id  INTEGER NOT NULL,
            course_id   INTEGER NOT NULL,
            grade       CHAR(1),
            enrolled_on TEXT    NOT NULL DEFAULT CURRENT_DATE,
            status      TEXT    NOT NULL DEFAULT 'active',
            CONSTRAINT pk_enrollment PRIMARY KEY (student_id, course_id),
            CONSTRAINT chk_grade CHECK (grade IN ('A', 'B', 'C', 'D', 'F'))
        );
        INSERT INTO enrollments (student_id, course_id) VALUES (1, 10);
        SELECT student_id, course_id, grade, status,
               enrolled_on = CURRENT_DATE AS enrolled_today
        FROM enrollments;
    ''', out='''
        student_id | course_id | grade | status | enrolled_today
        -----------+-----------+-------+--------+---------------
        1          | 10        | NULL  | active | 1
    ''', setup="")
    yield sql('''
        INSERT INTO enrollments (student_id, course_id, grade) VALUES (1, 11, 'Z');
    ''', fails=True, err='CHECK constraint failed: chk_grade', setup=ENROLL)
    yield p("A **named** constraint shows up in the error (`chk_grade`), which makes failures much easier to diagnose — and you need the name to drop it later (`ALTER TABLE … DROP CONSTRAINT chk_grade`). Notice too that the first row's `NULL` grade passed the `CHECK`: a check only rejects a condition that is **false**, and `NULL IN (…)` is *unknown*. Add `NOT NULL` if the value is mandatory.")
    yield section("Referential actions: what happens to children?", "git-fork")
    yield table(
        ["`ON DELETE …`", "When the parent row is deleted"],
        ["`RESTRICT` / `NO ACTION` (default)", "Refuse the delete while children exist"],
        ["`CASCADE`", "Delete the children too"],
        ["`SET NULL`", "Set the child's foreign key to `NULL`"],
        ["`SET DEFAULT`", "Set it to the column default"],
    )
    yield sql('''
        PRAGMA foreign_keys = ON;
        CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE posts (
            id        INTEGER PRIMARY KEY,
            author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
            title     TEXT
        );
        CREATE TABLE comments (
            id        INTEGER PRIMARY KEY,
            author_id INTEGER REFERENCES authors(id) ON DELETE SET NULL,
            body      TEXT
        );
        INSERT INTO authors  VALUES (1, 'Asha'), (2, 'Ravi');
        INSERT INTO posts    VALUES (1, 1, 'Intro to SQL'), (2, 2, 'Joins'), (3, 1, 'Indexes');
        INSERT INTO comments VALUES (1, 1, 'Nice!'), (2, 2, 'Thanks');

        DELETE FROM authors WHERE id = 1;

        SELECT * FROM posts ORDER BY id;
        SELECT * FROM comments ORDER BY id;
    ''', out='''
        id | author_id | title
        ---+-----------+------
        2  | 2         | Joins

        id | author_id | body
        ---+-----------+-------
        1  | NULL      | Nice!
        2  | 2         | Thanks
    ''', setup="")
    yield warn("Use `CASCADE` deliberately: deleting one customer could silently remove years of orders. Many teams prefer `RESTRICT` plus soft deletes (`is_active = 0`).")
    yield qa("What is the difference between PRIMARY KEY and UNIQUE?",
             "Both enforce uniqueness and create an index. A table has **one** primary key and it can never be `NULL`; it is the row's identity and the target of foreign keys. A table can have **many** `UNIQUE` constraints and they allow `NULL`s (multiple, in most engines).")
    yield qa("Can a foreign key column be NULL?",
             "Yes, unless it is also `NOT NULL`. A `NULL` foreign key means “no related row” (e.g. Dev has no department). The constraint is only checked for non-null values.")
    yield qa("Why enforce constraints in the database if the application validates input?",
             "Several applications, scripts, admins and migrations write to the same database; bugs and race conditions happen (two requests inserting the same email at once). Only the database sees every write and can guarantee integrity atomically.")


@topic(G, "insert", "INSERT", "row-insert-bottom")
def _():
    yield lead("`INSERT` adds rows — one at a time, many at once, or straight from a query.")
    yield section("Basic forms", "plus")
    yield sql('''
        -- always name the columns: robust to column order and future new columns
        INSERT INTO customers (customer_id, name, city, signup_date)
        VALUES (6, 'Farhan', 'Pune', '2024-04-02');

        -- several rows in one statement (one round trip, one transaction)
        INSERT INTO customers (customer_id, name, city, signup_date) VALUES
            (7, 'Divya', 'Chennai', '2024-04-05'),
            (8, 'Gautam', NULL,     '2024-04-07');

        SELECT * FROM customers WHERE customer_id >= 6 ORDER BY customer_id;
    ''', out='''
        customer_id | name   | city    | signup_date
        ------------+--------+---------+------------
        6           | Farhan | Pune    | 2024-04-02
        7           | Divya  | Chennai | 2024-04-05
        8           | Gautam | NULL    | 2024-04-07
    ''')
    yield section("Auto-generated keys and DEFAULTs", "key")
    yield p("Omit the key column and the database generates it. In SQLite an `INTEGER PRIMARY KEY` auto-assigns *max + 1*; `RETURNING` hands back the generated values without a second query.")
    yield sql('''
        INSERT INTO products (name, category, price)
        VALUES ('Keyboard', 'Electronics', 1800)
        RETURNING product_id, name;
    ''', out='''
        product_id | name
        -----------+---------
        8          | Keyboard
    ''')
    yield table(
        ["Engine", "Get the new id"],
        ["PostgreSQL, SQLite 3.35+", "`INSERT … RETURNING id`"],
        ["SQL Server", "`INSERT … OUTPUT inserted.id VALUES …` or `SCOPE_IDENTITY()`"],
        ["MySQL", "`SELECT LAST_INSERT_ID()` after the insert"],
        ["Oracle", "`RETURNING id INTO :v` (PL/SQL)"],
    )
    yield section("INSERT … SELECT", "copy")
    yield p("Copy rows produced by any query — no `VALUES` keyword.")
    yield sql('''
        CREATE TABLE vip_customers (customer_id INTEGER PRIMARY KEY, name TEXT, total_spent INTEGER);

        INSERT INTO vip_customers (customer_id, name, total_spent)
        SELECT c.customer_id, c.name, SUM(oi.quantity * oi.unit_price)
        FROM customers c
        JOIN orders o       ON o.customer_id = c.customer_id
        JOIN order_items oi ON oi.order_id   = o.order_id
        WHERE o.status <> 'cancelled'
        GROUP BY c.customer_id, c.name
        HAVING SUM(oi.quantity * oi.unit_price) > 50000;

        SELECT * FROM vip_customers ORDER BY total_spent DESC;
    ''', out='''
        customer_id | name   | total_spent
        ------------+--------+------------
        1           | Ananya | 68400
        2           | Rahul  | 61200
    ''')
    yield section("Skipping rows that would violate a constraint", "filter-off")
    yield sql('''
        INSERT OR IGNORE INTO departments (dept_id, name, location)
        VALUES (1, 'Engineering', 'Bengaluru'), (5, 'Finance', 'Delhi');

        SELECT * FROM departments ORDER BY dept_id;
    ''', out='''
        dept_id | name        | location
        --------+-------------+----------
        1       | Engineering | Bengaluru
        2       | Sales       | Mumbai
        3       | HR          | Hyderabad
        4       | Marketing   | Pune
        5       | Finance     | Delhi
    ''', caption="SQLite")
    yield dialect('''
        INSERT IGNORE INTO departments (dept_id, name, location) VALUES (5, 'Finance', 'Delhi');          -- MySQL
        INSERT INTO departments (dept_id, name, location) VALUES (5, 'Finance', 'Delhi')
        ON CONFLICT DO NOTHING;                                                                     -- PostgreSQL
    ''', "MySQL / PostgreSQL")
    yield warn("`INSERT INTO t VALUES (…)` without a column list depends on the physical column order — it breaks (or silently puts values in the wrong columns) after an `ALTER TABLE`.")
    yield good("Batch inserts: one multi-row `INSERT` (or many inserts inside one transaction) is often 10–100× faster than autocommitting each row separately.")
    yield qa("How do you insert data from one table into another?",
             "`INSERT INTO target (cols…) SELECT cols… FROM source WHERE …;` — the column counts and types must line up. To create the target at the same time use `CREATE TABLE t AS SELECT …` (or `SELECT … INTO t` in SQL Server).")


@topic(G, "update-delete", "UPDATE & DELETE", "edit")
def _():
    yield lead("`UPDATE` changes column values in existing rows; `DELETE` removes rows. Both touch **every row the `WHERE` matches** — which is all of them if you forget it.")
    yield section("UPDATE", "pencil")
    yield sql('''
        -- 10% raise for Sales; several columns can change at once
        UPDATE employees
        SET salary = salary * 1.10,
            email  = COALESCE(email, lower(name) || '@corp.in')
        WHERE dept_id = 2;

        SELECT emp_id, name, email, salary FROM employees WHERE dept_id = 2 ORDER BY emp_id;
    ''', out='''
        emp_id | name  | email         | salary
        -------+-------+---------------+-------------------
        5      | Priya | priya@corp.in | 121000.00000000001
        6      | Arjun | arjun@corp.in | 77000
        7      | Neha  | neha@corp.in  | 79200
    ''')
    yield note("Every expression on the right of `SET` sees the row's **old** values, so `SET a = b, b = a` swaps two columns in standard SQL (MySQL is the odd one out — it applies assignments left to right).")
    yield warn("Priya's `121000.00000000001` is floating-point error from `* 1.10` (SQLite stored a `REAL`). In a real schema `salary` would be `DECIMAL(10,2)`; in SQLite wrap it: `CAST(round(salary * 1.10) AS INTEGER)`.")
    yield section("UPDATE using another table", "table-import")
    yield sql('''
        -- raise everyone located in Hyderabad by 5000: subquery form (works everywhere)
        UPDATE employees
        SET salary = salary + 5000
        WHERE dept_id IN (SELECT dept_id FROM departments WHERE location = 'Hyderabad');

        SELECT name, salary FROM employees WHERE dept_id = 3 ORDER BY emp_id;
    ''', out='''
        name   | salary
        -------+-------
        Vikram | 85000
        Sara   | 90000
    ''')
    yield sql('''
        -- UPDATE … FROM (PostgreSQL, SQLite 3.33+): join the table being updated
        CREATE TABLE raises (emp_id INTEGER PRIMARY KEY, pct INTEGER);
        INSERT INTO raises VALUES (3, 10), (4, 20);

        UPDATE employees
        SET salary = salary + salary * r.pct / 100
        FROM raises AS r
        WHERE r.emp_id = employees.emp_id;

        SELECT name, salary FROM employees WHERE emp_id IN (3, 4) ORDER BY emp_id;
    ''', out='''
        name  | salary
        ------+-------
        Meera | 104500
        Karan | 114000
    ''')
    yield dialect('''
        -- MySQL: multi-table UPDATE with JOIN
        UPDATE employees e
        JOIN raises r ON r.emp_id = e.emp_id
        SET e.salary = e.salary + e.salary * r.pct / 100;

        -- SQL Server: UPDATE … FROM with an alias
        UPDATE e SET e.salary = e.salary + e.salary * r.pct / 100
        FROM employees e JOIN raises r ON r.emp_id = e.emp_id;
    ''', "MySQL / SQL Server")
    yield section("DELETE", "trash")
    yield sql('''
        -- remove order lines of cancelled orders, then the orders themselves
        DELETE FROM order_items
        WHERE order_id IN (SELECT order_id FROM orders WHERE status = 'cancelled');

        DELETE FROM orders WHERE status = 'cancelled'
        RETURNING order_id, customer_id;

        SELECT COUNT(*) AS orders_left FROM orders;
    ''', out='''
        order_id | customer_id
        ---------+------------
        105      | 4

        orders_left
        -----------
        7
    ''')
    yield p("The child rows (`order_items`) had to go first — otherwise the foreign key would block deleting the order (unless it was declared `ON DELETE CASCADE`).")
    yield section("Safe habits", "shield")
    yield steps(
        ("Preview", "Run `SELECT … WHERE <same condition>` first and check the row count."),
        ("Wrap in a transaction", "`BEGIN; UPDATE …;` → check the result → `COMMIT` or `ROLLBACK`."),
        ("Limit the blast radius", "Key the `WHERE` on the primary key when you mean one row."),
        ("Prefer soft deletes for business data", "`UPDATE … SET deleted_at = CURRENT_TIMESTAMP` keeps history and is reversible."),
    )
    yield sql('''
        BEGIN;
        UPDATE employees SET salary = 1;          -- oops: no WHERE, all 10 rows changed
        SELECT COUNT(*) AS paid_one_rupee FROM employees WHERE salary = 1;
        ROLLBACK;                                 -- undo everything since BEGIN
        SELECT name, salary FROM employees WHERE emp_id = 1;
    ''', out='''
        paid_one_rupee
        --------------
        10

        name | salary
        -----+-------
        Asha | 150000
    ''')
    yield qa("How do you delete rows from one table based on another table?",
             "Use a subquery — `DELETE FROM a WHERE id IN (SELECT a_id FROM b WHERE …)` or `WHERE EXISTS (SELECT 1 FROM b WHERE b.a_id = a.id …)`. MySQL and SQL Server also allow a join form: `DELETE a FROM a JOIN b ON … WHERE …`; PostgreSQL has `DELETE FROM a USING b WHERE …`.")
    yield qa("What happens if you run UPDATE without WHERE?",
             "Every row in the table is updated. If you are inside an explicit transaction you can `ROLLBACK`; in autocommit mode the change is permanent and you need a backup or point-in-time recovery. MySQL's `--safe-updates` mode refuses `UPDATE`/`DELETE` without a key-based `WHERE` or `LIMIT`.")


@topic(G, "upsert", "UPSERT: Insert or Update", "arrows-diff")
def _():
    yield lead("An *upsert* inserts a row, or updates it if a row with the same key already exists — atomically, in one statement, without a race between “check” and “write”.")
    yield section("INSERT … ON CONFLICT (PostgreSQL, SQLite)", "git-merge")
    yield sql('''
        CREATE TABLE inventory (
            sku        TEXT PRIMARY KEY,
            qty        INTEGER NOT NULL,
            updated_on TEXT NOT NULL
        );
        INSERT INTO inventory VALUES ('PEN', 100, '2024-03-01'), ('DESK', 5, '2024-03-01');

        INSERT INTO inventory (sku, qty, updated_on) VALUES
            ('PEN',   50, '2024-03-10'),      -- exists  → add to stock
            ('CHAIR', 12, '2024-03-10')       -- new     → insert
        ON CONFLICT (sku) DO UPDATE
            SET qty        = inventory.qty + excluded.qty,
                updated_on = excluded.updated_on;

        SELECT * FROM inventory ORDER BY sku;
    ''', out='''
        sku   | qty | updated_on
        ------+-----+-----------
        CHAIR | 12  | 2024-03-10
        DESK  | 5   | 2024-03-01
        PEN   | 150 | 2024-03-10
    ''', setup="")
    yield p("`excluded` is the row that *would* have been inserted; `inventory.qty` is the existing row. `ON CONFLICT (sku) DO NOTHING` simply skips duplicates.")
    yield section("Other dialects", "language")
    yield dialect('''
        INSERT INTO inventory (sku, qty, updated_on) VALUES ('PEN', 50, '2024-03-10')
        ON DUPLICATE KEY UPDATE
            qty = qty + VALUES(qty),          -- MySQL 8.0.20+: prefer an alias, e.g. AS new … new.qty
            updated_on = VALUES(updated_on);
    ''', "MySQL")
    yield dialect('''
        MERGE INTO inventory AS t
        USING (VALUES ('PEN', 50, '2024-03-10')) AS s (sku, qty, updated_on)
            ON t.sku = s.sku
        WHEN MATCHED THEN
            UPDATE SET qty = t.qty + s.qty, updated_on = s.updated_on
        WHEN NOT MATCHED THEN
            INSERT (sku, qty, updated_on) VALUES (s.sku, s.qty, s.updated_on);
    ''', "SQL Server / Oracle / PostgreSQL 15+ (MERGE)")
    yield section("The REPLACE trap", "alert-triangle")
    yield p("SQLite's `INSERT OR REPLACE` (and MySQL's `REPLACE`) **deletes** the old row and inserts a new one — columns you did not supply fall back to defaults.")
    yield sql('''
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, plan TEXT DEFAULT 'free');
        INSERT INTO users VALUES (1, 'Asha', 'premium');

        INSERT OR REPLACE INTO users (id, name) VALUES (1, 'Asha R');   -- plan is lost!
        SELECT * FROM users;
    ''', out='''
        id | name   | plan
        ---+--------+-----
        1  | Asha R | free
    ''', setup="")
    yield warn("`REPLACE` also fires delete triggers and can cascade-delete child rows. Prefer `ON CONFLICT … DO UPDATE` / `ON DUPLICATE KEY UPDATE`, which update in place.")
    yield warn("“`SELECT` then `INSERT` or `UPDATE`” in application code is a race: two requests can both see “not found” and both insert. Upsert statements (or a unique constraint plus retry) make it atomic.", "Race condition")
    yield qa("How do you implement an upsert?",
             "Put a `UNIQUE`/`PRIMARY KEY` on the natural key, then use the engine's atomic form: `INSERT … ON CONFLICT (key) DO UPDATE SET … = excluded.…` (PostgreSQL/SQLite), `INSERT … ON DUPLICATE KEY UPDATE` (MySQL), or `MERGE` (SQL Server/Oracle/PostgreSQL 15+). The conflict target must be backed by a unique index.")
