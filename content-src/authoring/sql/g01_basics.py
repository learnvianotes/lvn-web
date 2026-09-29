from kit import *
from sample_db import sql, dialect, DDL, DATA

G = "Getting Started"


@topic(G, "sql-intro", "What is SQL?", "database")
def _():
    yield lead("SQL (Structured Query Language) is the standard language for defining, querying and changing data in relational databases — you describe *what* you want, the database works out *how*.")
    yield define("Relational database", "data stored in **tables** (relations) of **rows** (records/tuples) and **columns** (attributes/fields). Tables are linked by shared key values, not by pointers.")
    yield define("SQL", "a *declarative* language (pronounced “S-Q-L” or “sequel”), standardised by ANSI/ISO since 1986. Every relational database speaks it, each with its own dialect.")
    yield section("Tables, rows and columns", "table")
    yield p("A table has a fixed set of named, typed columns and any number of rows. Every row should be identifiable by a **primary key**.")
    yield sql('''
        SELECT emp_id, name, salary
        FROM employees
        WHERE salary > 100000
        ORDER BY salary DESC;
    ''', out='''
        emp_id | name  | salary
        -------+-------+-------
        1      | Asha  | 150000
        2      | Ravi  | 120000
        5      | Priya | 110000
    ''')
    yield p("Read it as English: *give me the id, name and salary of employees earning over 1,00,000, highest first*. There is no loop, no index handling, no file access — the **query optimizer** decides how to fetch the rows.")
    yield section("Declarative vs procedural", "arrows-exchange")
    yield cards(
        ("Declarative (SQL)", "You state the *result*: which rows, which columns, what order. The engine picks indexes, join algorithms and order of work.", "target"),
        ("Procedural (Python, Java)", "You state the *steps*: open, loop, compare, append, sort. You own the algorithm and its performance.", "list-numbers"),
    )
    yield section("Relational vocabulary", "vocabulary")
    yield table(
        ["Formal term", "Everyday term", "Meaning"],
        ["Relation", "Table", "A set of tuples with the same attributes"],
        ["Tuple", "Row / record", "One entity, e.g. one employee"],
        ["Attribute", "Column / field", "One property, e.g. `salary`"],
        ["Domain", "Data type (+ constraints)", "The allowed values of an attribute"],
        ["Degree", "Number of columns", "`employees` has degree 7"],
        ["Cardinality", "Number of rows", "`employees` has cardinality 10"],
        ["Schema", "Structure", "Table definitions, types, constraints (not the data)"],
    )
    yield section("Why relational databases?", "bulb")
    yield cards(
        ("Integrity", "Types, keys and constraints reject bad data before it is stored.", "shield-check"),
        ("Transactions (ACID)", "Multi-step changes happen completely or not at all, even across crashes.", "lock"),
        ("Ad-hoc queries", "Any question answerable from the data can be asked later — no new code paths needed.", "search"),
        ("Concurrency", "Hundreds of users read and write safely at the same time.", "users"),
    )
    yield note("SQL is case-insensitive for keywords (`select` = `SELECT`). Convention: keywords in UPPER CASE, table and column names in `snake_case`. String literals use **single** quotes: `'Mumbai'`.", "Convention")
    yield qa("What is the difference between SQL and MySQL?",
             "SQL is the *language* (an ISO standard). MySQL is one *database product* (an RDBMS) that implements SQL with its own extensions — like PostgreSQL, SQL Server, Oracle and SQLite.")
    yield qa("What does “declarative” mean for SQL?",
             "You describe the result set you want, not the algorithm. The optimizer chooses the execution plan (index vs full scan, join order, hash vs nested-loop join), so the same query can get faster when indexes are added without changing a line of SQL.")


@topic(G, "rdbms-dialects", "RDBMS Landscape & Dialects", "server")
def _():
    yield lead("All major databases share core SQL, but each adds its own types, functions and syntax. Knowing the differences saves hours when you switch engines.")
    yield define("RDBMS", "Relational Database Management System — the software that stores tables, enforces constraints, runs queries and manages transactions and users.")
    yield section("The major engines", "server-2")
    yield table(
        ["Engine", "Typical use", "Notable traits"],
        ["**MySQL / MariaDB**", "Web apps (LAMP), SaaS back ends", "Open source, InnoDB engine, very popular, replication-friendly"],
        ["**PostgreSQL**", "General purpose, analytics, GIS", "Most standards-compliant open-source engine; rich types (`JSONB`, arrays), extensions"],
        ["**SQL Server**", "Microsoft / enterprise stacks", "T-SQL dialect, strong tooling, `TOP`, `IDENTITY`"],
        ["**Oracle**", "Large enterprises, banking", "PL/SQL, `ROWNUM`, `DUAL`, powerful but commercial"],
        ["**SQLite**", "Mobile apps, browsers, embedded, tests", "A library, not a server — the whole DB is one file; dynamic typing"],
    )
    yield note("Every runnable example in these notes executes on **SQLite 3.53**, which supports modern SQL: CTEs, window functions, `RIGHT`/`FULL` joins, `UPSERT`, `RETURNING` and JSON. Where another engine differs, the variant is shown and labelled.", "About these notes")
    yield section("Dialect differences you will meet", "language")
    yield table(
        ["Task", "MySQL", "PostgreSQL", "SQL Server", "Oracle", "SQLite"],
        ["First N rows", "`LIMIT n`", "`LIMIT n` / `FETCH FIRST n ROWS ONLY`", "`TOP (n)` / `OFFSET … FETCH`", "`FETCH FIRST n ROWS ONLY` (12c+)", "`LIMIT n`"],
        ["Auto-increment id", "`AUTO_INCREMENT`", "`GENERATED … AS IDENTITY` / `SERIAL`", "`IDENTITY(1,1)`", "`GENERATED AS IDENTITY`", "`INTEGER PRIMARY KEY`"],
        ["String concat", "`CONCAT(a, b)`", "`a || b`", "`a + b` / `CONCAT`", "`a || b`", "`a || b`"],
        ["Current timestamp", "`NOW()`", "`NOW()`", "`GETDATE()`", "`SYSDATE`", "`CURRENT_TIMESTAMP`"],
        ["NULL replacement", "`IFNULL` / `COALESCE`", "`COALESCE`", "`ISNULL` / `COALESCE`", "`NVL` / `COALESCE`", "`IFNULL` / `COALESCE`"],
        ["Boolean type", "`TINYINT(1)`", "`BOOLEAN`", "`BIT`", "`NUMBER(1)` (`BOOLEAN` in 23ai)", "integer `0`/`1`"],
        ["Identifier quoting", "`` `name` ``", "`\"name\"`", "`[name]`", "`\"name\"`", "`\"name\"` (also accepts the others)"],
    )
    yield section("The same query in four dialects", "code")
    yield p("*Top 3 highest-paid employees:*")
    yield sql('''
        SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;
    ''', out='''
        name  | salary
        ------+-------
        Asha  | 150000
        Ravi  | 120000
        Priya | 110000
    ''', caption="SQLite / MySQL / PostgreSQL")
    yield dialect('''
        SELECT TOP (3) name, salary FROM employees ORDER BY salary DESC;
    ''', "SQL Server")
    yield dialect('''
        SELECT name, salary FROM employees ORDER BY salary DESC
        FETCH FIRST 3 ROWS ONLY;
    ''', "Oracle 12c+ / PostgreSQL / SQL standard")
    yield good("Prefer standard features (`COALESCE`, `CASE`, `FETCH FIRST`, `||` or `CONCAT`) when they exist — the code ports more easily between engines.")
    yield qa("Which SQL database should you choose for a new project?",
             "Default to **PostgreSQL** for a general server-side app (standards, JSONB, extensions). **MySQL** is equally fine and widely hosted. **SQLite** for embedded/mobile/local tools and tests. SQL Server or Oracle usually when the organisation already runs them.")
    yield qa("Is SQLite a “real” database?",
             "Yes — it is fully transactional (ACID) and is the most deployed database in the world (every phone and browser). What it lacks is a server: no network access, no user accounts/`GRANT`, and one writer at a time. It is ideal for local data, not for many concurrent writers.")


@topic(G, "sql-sublanguages", "SQL Sublanguages: DDL, DML, DQL, DCL, TCL", "category")
def _():
    yield lead("SQL commands are grouped by what they act on — the structure, the data, permissions, or transactions. A classic first interview question.")
    yield table(
        ["Group", "Stands for", "Commands", "Acts on"],
        ["**DDL**", "Data Definition Language", "`CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`", "Schema objects (tables, indexes, views)"],
        ["**DML**", "Data Manipulation Language", "`INSERT`, `UPDATE`, `DELETE`, `MERGE`", "Rows inside tables"],
        ["**DQL**", "Data Query Language", "`SELECT`", "Reading rows (often counted as part of DML)"],
        ["**DCL**", "Data Control Language", "`GRANT`, `REVOKE`", "Permissions of users and roles"],
        ["**TCL**", "Transaction Control Language", "`COMMIT`, `ROLLBACK`, `SAVEPOINT`, `BEGIN`", "Grouping DML into atomic units"],
    )
    yield section("One of each", "code")
    yield sql('''
        -- DDL: define structure
        CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL);

        -- TCL + DML: change data inside a transaction
        BEGIN;
        INSERT INTO notes (body) VALUES ('learn SQL'), ('practice joins');
        UPDATE notes SET body = 'practice window functions' WHERE id = 2;
        COMMIT;

        -- DQL: read it back
        SELECT id, body FROM notes ORDER BY id;
    ''', out='''
        id | body
        ---+--------------------------
        1  | learn SQL
        2  | practice window functions
    ''', setup="")
    yield dialect('''
        -- DCL: permissions (server databases only; SQLite has no users)
        GRANT SELECT, INSERT ON notes TO analyst;
        REVOKE INSERT ON notes FROM analyst;
    ''', "PostgreSQL / MySQL / SQL Server")
    yield section("Why the grouping matters", "bulb")
    yield cards(
        ("Auto-commit of DDL", "In MySQL and Oracle every DDL statement *implicitly commits* the open transaction and cannot be rolled back. PostgreSQL and SQLite allow DDL inside a transaction.", "alert-triangle"),
        ("Permissions", "DBAs grant DDL rights to few people (schema owners), DML to applications, and read-only DQL to analysts.", "shield-lock"),
    )
    yield qa("Is TRUNCATE DDL or DML?",
             "**DDL** in most engines. It removes all rows by deallocating data pages instead of deleting row by row, does not fire `DELETE` triggers, resets identity counters, and (in MySQL/Oracle) auto-commits. `DELETE` is DML: row by row, logged, can have a `WHERE`, can be rolled back.")
    yield qa("Is SELECT part of DML?",
             "Formally the SQL standard puts `SELECT` under data manipulation; many courses split it out as **DQL**. Either answer is accepted if you explain that `SELECT` only reads data.")


@topic(G, "sample-database", "The Sample Database", "table-options")
def _():
    yield lead("Every example in these notes runs against this small company-and-shop database. Skim it once — then every query result is easy to verify by eye.")
    yield section("The tables", "sitemap")
    yield table(
        ["Table", "Rows", "What it holds", "Links"],
        ["`departments`", "4", "Departments and their city", "—"],
        ["`employees`", "10", "Staff with salary, hire date and manager", "`dept_id` → departments, `manager_id` → employees (self)"],
        ["`customers`", "5", "Shop customers", "—"],
        ["`products`", "7", "Catalogue with category and list price", "—"],
        ["`orders`", "8", "One row per order, with status", "`customer_id` → customers"],
        ["`order_items`", "13", "Lines of each order (quantity × price paid)", "`order_id` → orders, `product_id` → products"],
    )
    yield flow("customers", "orders", "order_items", "products")
    yield section("Schema (DDL)", "code")
    yield sql(DDL, caption="SQL — schema", setup="")
    yield note("`PRAGMA foreign_keys = ON` is SQLite-specific: SQLite enforces foreign keys only when this is switched on for the connection. Other engines always enforce them.", "SQLite")
    yield section("The data", "database")
    yield sql('''
        SELECT * FROM departments ORDER BY dept_id;
        SELECT * FROM employees ORDER BY emp_id;
    ''', out='''
        dept_id | name        | location
        --------+-------------+----------
        1       | Engineering | Bengaluru
        2       | Sales       | Mumbai
        3       | HR          | Hyderabad
        4       | Marketing   | Pune

        emp_id | name   | email          | dept_id | manager_id | salary | hire_date
        -------+--------+----------------+---------+------------+--------+-----------
        1      | Asha   | asha@corp.in   | 1       | NULL       | 150000 | 2015-03-01
        2      | Ravi   | ravi@corp.in   | 1       | 1          | 120000 | 2017-06-15
        3      | Meera  | meera@corp.in  | 1       | 2          | 95000  | 2019-01-10
        4      | Karan  | karan@corp.in  | 1       | 2          | 95000  | 2020-08-01
        5      | Priya  | priya@corp.in  | 2       | 1          | 110000 | 2016-11-20
        6      | Arjun  | arjun@corp.in  | 2       | 5          | 70000  | 2021-02-14
        7      | Neha   | NULL           | 2       | 5          | 72000  | 2022-05-30
        8      | Vikram | vikram@corp.in | 3       | 1          | 80000  | 2018-09-05
        9      | Sara   | sara@corp.in   | 3       | 8          | 85000  | 2023-01-09
        10     | Dev    | NULL           | NULL    | 1          | 60000  | 2024-04-01
    ''')
    yield p("Built-in quirks worth noticing — later topics rely on them:")
    yield ul(
        "**Asha** has no manager (`manager_id` is `NULL`) — she is the root of the hierarchy.",
        "**Dev** has no department (`dept_id` is `NULL`) and **Marketing** has no employees — perfect for outer joins.",
        "**Meera** and **Karan** earn the same (95000) — ties for ranking functions.",
        "**Neha** and **Dev** have no email — `NULL` handling.",
        "**Sara** (85000) earns more than her manager **Vikram** (80000).",
    )
    yield sql('''
        SELECT * FROM customers ORDER BY customer_id;
        SELECT * FROM products ORDER BY product_id;
    ''', out='''
        customer_id | name   | city      | signup_date
        ------------+--------+-----------+------------
        1           | Ananya | Mumbai    | 2023-11-02
        2           | Rahul  | Delhi     | 2023-12-15
        3           | Sneha  | Bengaluru | 2024-01-20
        4           | Imran  | Delhi     | 2024-02-01
        5           | Kavya  | NULL      | 2024-03-10

        product_id | name       | category    | price
        -----------+------------+-------------+------
        1          | Laptop     | Electronics | 55000
        2          | Headphones | Electronics | 2500
        3          | Desk       | Furniture   | 8000
        4          | Chair      | Furniture   | 4500
        5          | Notebook   | Stationery  | 60
        6          | Pen        | Stationery  | 20
        7          | Monitor    | Electronics | 12000
    ''')
    yield sql('''
        SELECT * FROM orders ORDER BY order_id;
        SELECT * FROM order_items ORDER BY order_id, product_id;
    ''', out='''
        order_id | customer_id | order_date | status
        ---------+-------------+------------+----------
        101      | 1           | 2024-01-05 | delivered
        102      | 2           | 2024-01-12 | delivered
        103      | 1           | 2024-02-03 | delivered
        104      | 3           | 2024-02-14 | shipped
        105      | 4           | 2024-02-20 | cancelled
        106      | 2           | 2024-03-01 | delivered
        107      | 3           | 2024-03-08 | pending
        108      | 1           | 2024-03-15 | shipped

        order_id | product_id | quantity | unit_price
        ---------+------------+----------+-----------
        101      | 1          | 1        | 55000
        101      | 2          | 1        | 2500
        102      | 4          | 2        | 4500
        102      | 6          | 10       | 20
        103      | 5          | 5        | 60
        103      | 6          | 5        | 20
        104      | 3          | 1        | 8000
        104      | 4          | 1        | 4500
        105      | 2          | 2        | 2500
        106      | 1          | 1        | 52000
        107      | 5          | 20       | 60
        108      | 2          | 1        | 2500
        108      | 3          | 1        | 8000
    ''')
    yield ul(
        "**Kavya** has never ordered and has no city; the **Monitor** has never been sold.",
        "Order **106** sold a Laptop at 52000 — `unit_price` records the price *actually paid*, which can differ from the list price in `products`.",
        "Order **105** was cancelled — most revenue queries must exclude it.",
    )
    yield section("Data insert script", "file-database")
    yield sql(DATA, caption="SQL — data", setup=DDL)
    yield warn("`SELECT *` is fine for exploring. In application code, list the columns you need: it is faster, and the query does not break (or silently change) when someone adds a column.")
