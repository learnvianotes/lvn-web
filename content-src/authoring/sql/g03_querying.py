from kit import *
from sample_db import sql, dialect

G = "Querying Basics"


@topic(G, "select-basics", "SELECT Basics", "table")
def _():
    yield lead("`SELECT` reads data: pick columns, compute expressions, and shape the result set. Every other query feature builds on this.")
    yield section("Anatomy of a SELECT", "list-tree")
    yield sql('''
        SELECT   column_list        -- what to return   (required)
        FROM     table_name         -- where from
        WHERE    row_filter         -- which rows
        GROUP BY grouping_columns   -- collapse rows into groups
        HAVING   group_filter       -- which groups
        ORDER BY sort_keys          -- in what order
        LIMIT    n;                 -- how many
    ''', run=False)
    yield p("Only `SELECT` is mandatory — but the clauses must appear in exactly this order.")
    yield section("Choosing columns", "columns")
    yield sql('''
        SELECT name, salary, hire_date
        FROM employees
        ORDER BY emp_id
        LIMIT 4;
    ''', out='''
        name  | salary | hire_date
        ------+--------+-----------
        Asha  | 150000 | 2015-03-01
        Ravi  | 120000 | 2017-06-15
        Meera | 95000  | 2019-01-10
        Karan | 95000  | 2020-08-01
    ''')
    yield section("Computed columns and literals", "calculator")
    yield p("The select list can contain any expression: arithmetic, function calls, string concatenation (`||`), constants.")
    yield sql('''
        SELECT name,
               salary,
               salary / 12            AS monthly,
               salary * 12 / 100      AS pf_12_pct,
               'INR'                  AS currency,
               upper(name) || ' #' || emp_id AS badge
        FROM employees
        WHERE dept_id = 1
        ORDER BY emp_id;
    ''', out='''
        name  | salary | monthly | pf_12_pct | currency | badge
        ------+--------+---------+-----------+----------+---------
        Asha  | 150000 | 12500   | 18000     | INR      | ASHA #1
        Ravi  | 120000 | 10000   | 14400     | INR      | RAVI #2
        Meera | 95000  | 7916    | 11400     | INR      | MEERA #3
        Karan | 95000  | 7916    | 11400     | INR      | KARAN #4
    ''')
    yield warn("Integer ÷ integer is **integer division** in SQLite, PostgreSQL and SQL Server: `7 / 2` is `3`. Use `7 / 2.0` or `CAST(x AS REAL)` for a fractional result. (MySQL and Oracle return `3.5`.)")
    yield section("SELECT without FROM", "math")
    yield sql('''
        SELECT 2 + 3 * 4 AS result, 7 / 2 AS int_div, 7 / 2.0 AS real_div, 'hi' || '!' AS greeting;
    ''', out='''
        result | int_div | real_div | greeting
        -------+---------+----------+---------
        14     | 3       | 3.5      | hi!
    ''', setup="")
    yield note("Oracle requires a `FROM`, so it provides a one-row dummy table: `SELECT 2 + 3 FROM DUAL;`.", "Oracle")
    yield section("SELECT *", "asterisk")
    yield dodont(
        "Name the columns you need: less data over the network, can use covering indexes, stable when columns are added.",
        "`SELECT *` in production code or in views — it returns columns you don't need and changes shape silently when the table changes.",
    )
    yield qa("Is SQL case-sensitive?",
             "Keywords and (unquoted) identifiers are case-insensitive in all major engines. **String comparison** depends on the collation: `'a' = 'A'` is false in PostgreSQL and SQLite (binary), true in MySQL and SQL Server with their default case-insensitive collations. Quoted identifiers (`\"Name\"`) are case-sensitive in PostgreSQL and Oracle.")


@topic(G, "where-operators", "Filtering with WHERE", "filter")
def _():
    yield lead("`WHERE` keeps only the rows for which a condition is **true** — rows where it is false *or unknown* (`NULL`) are dropped.")
    yield section("Operators", "math-symbols")
    yield table(
        ["Kind", "Operators", "Example"],
        ["Comparison", "`=  <>  !=  <  <=  >  >=`", "`salary >= 100000`"],
        ["Logical", "`AND`, `OR`, `NOT`", "`dept_id = 1 AND salary > 100000`"],
        ["Range", "`BETWEEN a AND b` (inclusive)", "`hire_date BETWEEN '2018-01-01' AND '2020-12-31'`"],
        ["List", "`IN (…)`, `NOT IN (…)`", "`dept_id IN (2, 3)`"],
        ["Pattern", "`LIKE`, `NOT LIKE`", "`name LIKE 'A%'`"],
        ["Null test", "`IS NULL`, `IS NOT NULL`", "`email IS NULL`"],
    )
    yield section("Comparison and logic", "adjustments")
    yield sql('''
        SELECT name, dept_id, salary
        FROM employees
        WHERE dept_id = 1 AND salary < 100000
        ORDER BY emp_id;
    ''', out='''
        name  | dept_id | salary
        ------+---------+-------
        Meera | 1       | 95000
        Karan | 1       | 95000
    ''')
    yield sql('''
        SELECT name, hire_date
        FROM employees
        WHERE hire_date BETWEEN '2018-01-01' AND '2020-12-31'
        ORDER BY hire_date;
    ''', out='''
        name   | hire_date
        -------+-----------
        Vikram | 2018-09-05
        Meera  | 2019-01-10
        Karan  | 2020-08-01
    ''')
    yield sql('''
        SELECT name, dept_id
        FROM employees
        WHERE dept_id IN (2, 3) AND NOT name = 'Sara'
        ORDER BY emp_id;
    ''', out='''
        name   | dept_id
        -------+--------
        Priya  | 2
        Arjun  | 2
        Neha   | 2
        Vikram | 3
    ''')
    yield section("Operator precedence: AND before OR", "brackets")
    yield p("`AND` binds tighter than `OR`, exactly like `×` before `+`. Mixing them without parentheses is a classic bug.")
    yield sql('''
        -- intended: Sales or HR employees earning over 75000
        SELECT name, dept_id, salary FROM employees
        WHERE dept_id = 2 OR dept_id = 3 AND salary > 75000     -- means 2 OR (3 AND > 75000)
        ORDER BY emp_id;

        SELECT name, dept_id, salary FROM employees
        WHERE (dept_id = 2 OR dept_id = 3) AND salary > 75000
        ORDER BY emp_id;
    ''', out='''
        name   | dept_id | salary
        -------+---------+-------
        Priya  | 2       | 110000
        Arjun  | 2       | 70000
        Neha   | 2       | 72000
        Vikram | 3       | 80000
        Sara   | 3       | 85000

        name   | dept_id | salary
        -------+---------+-------
        Priya  | 2       | 110000
        Vikram | 3       | 80000
        Sara   | 3       | 85000
    ''')
    yield warn("The first query returned Arjun and Neha (Sales, below 75000) because the salary test only applied to HR. When `AND` and `OR` meet, always add parentheses.")
    yield section("BETWEEN with dates and times", "calendar")
    yield warn("`BETWEEN '2024-03-01' AND '2024-03-31'` misses `'2024-03-31 14:00'` when the column stores timestamps — the string/timestamp is greater than the upper bound. Prefer a half-open range: `ts >= '2024-03-01' AND ts < '2024-04-01'`.")
    yield sql('''
        SELECT order_id, order_date FROM orders
        WHERE order_date >= '2024-02-01' AND order_date < '2024-03-01'
        ORDER BY order_id;
    ''', out='''
        order_id | order_date
        ---------+-----------
        103      | 2024-02-03
        104      | 2024-02-14
        105      | 2024-02-20
    ''')
    yield qa("What is the difference between != and <>?",
             "None in practice — `<>` is the ISO standard “not equal”, `!=` is accepted by every major engine. Both yield unknown (not true) when either side is `NULL`.")
    yield qa("Is BETWEEN inclusive?",
             "Yes, both ends: `x BETWEEN a AND b` means `x >= a AND x <= b`. If `a > b` it matches nothing (SQL Server/MySQL) — `BETWEEN SYMMETRIC` in PostgreSQL swaps them for you.")


@topic(G, "like-patterns", "LIKE & Pattern Matching", "search")
def _():
    yield lead("`LIKE` matches text against a simple pattern with two wildcards; regular expressions are available as dialect extensions.")
    yield table(
        ["Wildcard", "Matches", "Example", "Matches…"],
        ["`%`", "Any sequence of 0+ characters", "`'A%'`", "Asha, Arjun"],
        ["`_`", "Exactly one character", "`'_a%'`", "Ravi, Karan, Sara (second letter a)"],
    )
    yield sql('''
        SELECT name FROM employees WHERE name LIKE 'A%'   ORDER BY name;
        SELECT name FROM employees WHERE name LIKE '_a%'  ORDER BY name;
        SELECT name FROM employees WHERE name LIKE '%an%' ORDER BY name;
    ''', out='''
        name
        -----
        Arjun
        Asha

        name
        -----
        Karan
        Ravi
        Sara

        name
        -----
        Karan
    ''')
    yield section("Case sensitivity", "letter-case")
    yield p("SQLite's `LIKE` is case-insensitive for ASCII letters; PostgreSQL's `LIKE` is case-sensitive (use `ILIKE`); MySQL/SQL Server follow the column collation (usually insensitive). Portable trick: compare lowercased values.")
    yield sql('''
        SELECT name FROM employees WHERE name LIKE 'a%' ORDER BY name;              -- SQLite: matches A
        SELECT name FROM employees WHERE name GLOB 'a*' ORDER BY name;              -- GLOB: case-sensitive
        SELECT name FROM employees WHERE lower(name) LIKE 'a%' ORDER BY name;       -- portable
    ''', out='''
        name
        -----
        Arjun
        Asha

        name
        ----

        name
        -----
        Arjun
        Asha
    ''')
    yield section("Matching a literal % or _", "percentage")
    yield sql('''
        CREATE TABLE promos (code TEXT);
        INSERT INTO promos VALUES ('SAVE10%'), ('SAVE10'), ('FLAT_50'), ('FLATX50');

        SELECT code FROM promos WHERE code LIKE '%\\%' ESCAPE '\\' ORDER BY code;
        SELECT code FROM promos WHERE code LIKE 'FLAT\\_%' ESCAPE '\\' ORDER BY code;
        SELECT code FROM promos WHERE code LIKE 'FLAT_%' ORDER BY code;          -- _ is a wildcard!
    ''', out='''
        code
        -------
        SAVE10%

        code
        -------
        FLAT_50

        code
        -------
        FLATX50
        FLAT_50
    ''', setup="")
    yield section("Regular expressions (dialects)", "regex")
    yield dialect('''
        SELECT name FROM employees WHERE name ~ '^[AEIOU]';          -- PostgreSQL (~* = case-insensitive)
        SELECT name FROM employees WHERE name REGEXP '^[AEIOU]';     -- MySQL
        SELECT name FROM employees WHERE REGEXP_LIKE(name, '^[AEIOU]');  -- Oracle / MySQL 8
    ''', "PostgreSQL / MySQL / Oracle")
    yield warn("A leading wildcard (`LIKE '%son'`) cannot use a normal B-tree index — the engine must scan every row. `LIKE 'son%'` (prefix) can. For real text search use full-text indexes (`FULLTEXT`, PostgreSQL `tsvector`, SQLite FTS5).", "Performance")
    yield qa("Find names that start and end with a vowel.",
             "Portable: `WHERE lower(substr(name,1,1)) IN ('a','e','i','o','u') AND lower(substr(name,-1)) IN ('a','e','i','o','u')` (SQL Server/MySQL: `LEFT`/`RIGHT`). With regex: `name ~* '^[aeiou].*[aeiou]$'` (PostgreSQL) or `REGEXP '^[aeiou].*[aeiou]$'` (MySQL).")


@topic(G, "order-by", "Sorting with ORDER BY", "sort-ascending")
def _():
    yield lead("Without `ORDER BY`, row order is **undefined** — it may look sorted today and change after an index or a version upgrade. If order matters, say so.")
    yield section("One or more sort keys", "sort-descending")
    yield sql('''
        SELECT name, dept_id, salary
        FROM employees
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id ASC, salary DESC, name;    -- ASC is the default
    ''', out='''
        name   | dept_id | salary
        -------+---------+-------
        Asha   | 1       | 150000
        Ravi   | 1       | 120000
        Karan  | 1       | 95000
        Meera  | 1       | 95000
        Priya  | 2       | 110000
        Neha   | 2       | 72000
        Arjun  | 2       | 70000
        Sara   | 3       | 85000
        Vikram | 3       | 80000
    ''')
    yield p("Rows are sorted by the first key; ties are broken by the second, and so on. Meera and Karan tie on salary, so `name` decides.")
    yield section("Sort by expression, alias or position", "arrows-sort")
    yield sql('''
        SELECT name, salary / 12 AS monthly
        FROM employees
        WHERE dept_id = 2
        ORDER BY monthly DESC;                      -- alias from the SELECT list

        SELECT name, length(name) AS len
        FROM employees
        ORDER BY length(name) DESC, 1               -- expression, then column position 1
        LIMIT 3;
    ''', out='''
        name  | monthly
        ------+--------
        Priya | 9166
        Neha  | 6000
        Arjun | 5833

        name   | len
        -------+----
        Vikram | 6
        Arjun  | 5
        Karan  | 5
    ''')
    yield warn("`ORDER BY 1` (column position) is handy interactively but fragile in code — reordering the select list changes the sort silently.")
    yield section("Where do NULLs go?", "question-mark")
    yield p("SQLite, MySQL and SQL Server treat `NULL` as **smallest** (first in `ASC`); PostgreSQL and Oracle treat it as **largest** (last in `ASC`). Be explicit with `NULLS FIRST`/`NULLS LAST` (PostgreSQL, Oracle, SQLite 3.30+).")
    yield sql('''
        SELECT name, email FROM employees WHERE emp_id >= 6 ORDER BY email;
        SELECT name, email FROM employees WHERE emp_id >= 6 ORDER BY email NULLS LAST;
    ''', out='''
        name   | email
        -------+---------------
        Neha   | NULL
        Dev    | NULL
        Arjun  | arjun@corp.in
        Sara   | sara@corp.in
        Vikram | vikram@corp.in

        name   | email
        -------+---------------
        Arjun  | arjun@corp.in
        Sara   | sara@corp.in
        Vikram | vikram@corp.in
        Neha   | NULL
        Dev    | NULL
    ''')
    yield sql('''
        -- engines without NULLS LAST (MySQL, SQL Server): sort on "is null" first
        SELECT name, email FROM employees WHERE emp_id >= 6
        ORDER BY email IS NULL, email;
    ''', out='''
        name   | email
        -------+---------------
        Arjun  | arjun@corp.in
        Sara   | sara@corp.in
        Vikram | vikram@corp.in
        Neha   | NULL
        Dev    | NULL
    ''')
    yield section("Custom order with CASE", "list-numbers")
    yield sql('''
        SELECT order_id, status FROM orders
        ORDER BY CASE status
                     WHEN 'pending'   THEN 1
                     WHEN 'shipped'   THEN 2
                     WHEN 'delivered' THEN 3
                     ELSE 4
                 END,
                 order_id;
    ''', out='''
        order_id | status
        ---------+----------
        107      | pending
        104      | shipped
        108      | shipped
        101      | delivered
        102      | delivered
        103      | delivered
        106      | delivered
        105      | cancelled
    ''')
    yield qa("Can you ORDER BY a column that is not in the SELECT list?",
             "Yes, in a plain query (`SELECT name FROM employees ORDER BY salary`). Not with `SELECT DISTINCT` or in some `UNION` cases, because the sort key must then be part of the output rows.")


@topic(G, "limit-pagination", "LIMIT, OFFSET & Pagination", "list-numbers")
def _():
    yield lead("`LIMIT` caps the number of rows returned; `OFFSET` skips rows first. Together they page through results — but deep offsets get slow.")
    yield section("Top-N", "trophy")
    yield sql('''
        SELECT name, salary FROM employees
        ORDER BY salary DESC, emp_id
        LIMIT 3;
    ''', out='''
        name  | salary
        ------+-------
        Asha  | 150000
        Ravi  | 120000
        Priya | 110000
    ''')
    yield warn("`LIMIT` without `ORDER BY` returns an *arbitrary* 3 rows. And when the sort key has ties (Meera and Karan both 95000), add a unique tie-breaker (`emp_id`) so pages are stable.")
    yield section("Offset pagination", "file-stack")
    yield sql('''
        -- page 2, page size 3 → OFFSET = (page - 1) * size
        SELECT emp_id, name FROM employees
        ORDER BY emp_id
        LIMIT 3 OFFSET 3;
    ''', out='''
        emp_id | name
        -------+------
        4      | Karan
        5      | Priya
        6      | Arjun
    ''')
    yield table(
        ["Engine", "Page 2 of size 3"],
        ["SQLite, PostgreSQL, MySQL", "`LIMIT 3 OFFSET 3`  (MySQL also `LIMIT 3, 3` — offset first!)"],
        ["SQL Server 2012+", "`ORDER BY emp_id OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY`"],
        ["Oracle 12c+ / standard", "`OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY`"],
        ["Old Oracle", "`WHERE ROWNUM <= n` in a nested query"],
    )
    yield section("Keyset (seek) pagination", "key")
    yield p("`OFFSET 100000` still reads and throws away 100 000 rows, and rows inserted between requests shift pages (duplicates / gaps). **Keyset pagination** remembers the last key seen and seeks past it using the index.")
    yield sql('''
        -- the client got page 1 ending at emp_id = 3; next page:
        SELECT emp_id, name FROM employees
        WHERE emp_id > 3
        ORDER BY emp_id
        LIMIT 3;
    ''', out='''
        emp_id | name
        -------+------
        4      | Karan
        5      | Priya
        6      | Arjun
    ''')
    yield sql('''
        -- sorted by a non-unique column: seek on (salary, emp_id) together; last row seen was Meera (95000, 3)
        SELECT emp_id, name, salary FROM employees
        WHERE (salary, emp_id) < (95000, 3)
        ORDER BY salary DESC, emp_id DESC
        LIMIT 3;
    ''', out='''
        emp_id | name   | salary
        -------+--------+-------
        9      | Sara   | 85000
        8      | Vikram | 80000
        7      | Neha   | 72000
    ''')
    yield cards(
        ("Offset pagination", "Simple, allows jumping to page N. Cost grows with the offset; unstable when data changes.", "file-stack"),
        ("Keyset pagination", "Constant speed on any page, stable under inserts. No random page jumps — ideal for infinite scroll and APIs (`?after=…`).", "key"),
    )
    yield qa("Why is OFFSET pagination slow for large page numbers?",
             "The database must produce and discard every row before the offset — `OFFSET 1000000` reads a million rows to return 20. Keyset pagination (`WHERE key > :last ORDER BY key LIMIT 20`) jumps straight to the starting point through the index.")


@topic(G, "distinct-aliases", "DISTINCT & Aliases", "copy")
def _():
    yield lead("`DISTINCT` removes duplicate result rows; aliases give columns and tables short, readable names.")
    yield section("DISTINCT", "filter")
    yield sql('''
        SELECT DISTINCT category FROM products ORDER BY category;

        SELECT DISTINCT city FROM customers ORDER BY city;       -- NULL counts as one value here
    ''', out='''
        category
        -----------
        Electronics
        Furniture
        Stationery

        city
        ---------
        NULL
        Bengaluru
        Delhi
        Mumbai
    ''')
    yield p("`DISTINCT` applies to the **whole row**, not to one column:")
    yield sql('''
        SELECT DISTINCT customer_id, status FROM orders ORDER BY customer_id, status;
    ''', out='''
        customer_id | status
        ------------+----------
        1           | delivered
        1           | shipped
        2           | delivered
        3           | pending
        3           | shipped
        4           | cancelled
    ''')
    yield sql('''
        SELECT COUNT(DISTINCT customer_id) AS customers_who_ordered,
               COUNT(DISTINCT status)      AS statuses
        FROM orders;
    ''', out='''
        customers_who_ordered | statuses
        ----------------------+---------
        4                     | 4
    ''')
    yield warn("Reaching for `DISTINCT` to hide duplicates caused by a join usually hides a bug (a missing join condition or a one-to-many join). Fix the join — or use `EXISTS` — instead.")
    yield dialect('''
        -- PostgreSQL only: first row per group (by the ORDER BY)
        SELECT DISTINCT ON (dept_id) dept_id, name, salary
        FROM employees
        ORDER BY dept_id, salary DESC;
    ''', "PostgreSQL (DISTINCT ON)")
    yield section("Column aliases", "tag")
    yield sql('''
        SELECT name AS employee,
               salary * 12 AS "annual pay",       -- double quotes: spaces or reserved words
               hire_date joined                    -- AS is optional
        FROM employees
        WHERE emp_id <= 2
        ORDER BY emp_id;
    ''', out='''
        employee | annual pay | joined
        ---------+------------+-----------
        Asha     | 1800000    | 2015-03-01
        Ravi     | 1440000    | 2017-06-15
    ''')
    yield section("Table aliases", "table-alias")
    yield sql('''
        SELECT e.name, d.name AS department
        FROM employees AS e
        JOIN departments d ON d.dept_id = e.dept_id
        WHERE e.salary > 100000
        ORDER BY e.emp_id;
    ''', out='''
        name  | department
        ------+------------
        Asha  | Engineering
        Ravi  | Engineering
        Priya | Sales
    ''')
    yield note("A table alias is required when the same table appears twice (self-join) and makes every multi-table query readable. Oracle does not accept `AS` before a *table* alias.")
    yield warn("A column alias cannot be used in `WHERE` of the same query (the `SELECT` list is evaluated *after* `WHERE`) — see the next topic. SQLite and MySQL relax this in places, which is not portable.")
    yield qa("What is the difference between DISTINCT and GROUP BY?",
             "`SELECT DISTINCT a, b` and `SELECT a, b … GROUP BY a, b` return the same rows and usually get the same plan. Use `DISTINCT` to de-duplicate; use `GROUP BY` when you also compute aggregates per group.")


@topic(G, "logical-order", "Logical Order of Query Execution", "arrows-down")
def _():
    yield lead("You *write* `SELECT` first, but the database *evaluates* it almost last. This single fact explains most “why can't I use that here?” errors.")
    yield flow("FROM / JOIN", "WHERE", "GROUP BY", "HAVING", "SELECT", "DISTINCT", "ORDER BY", "LIMIT")
    yield steps(
        ("FROM + JOINs", "Build the working set of rows from the tables."),
        ("WHERE", "Keep rows whose condition is true. Aggregates don't exist yet."),
        ("GROUP BY", "Collapse rows into one row per group."),
        ("HAVING", "Keep groups whose condition is true — aggregates are available now."),
        ("SELECT", "Compute output expressions, window functions and aliases."),
        ("DISTINCT", "Remove duplicate output rows."),
        ("ORDER BY", "Sort — can use aliases, since `SELECT` already ran."),
        ("LIMIT / OFFSET", "Cut the sorted result."),
    )
    yield section("Consequences", "bulb")
    yield table(
        ["You try", "Result", "Why"],
        ["`WHERE monthly > 9000` (alias)", "Error in standard SQL", "`WHERE` runs before `SELECT` creates the alias"],
        ["`WHERE COUNT(*) > 2`", "Error everywhere", "Aggregates don't exist before `GROUP BY` — use `HAVING`"],
        ["`ORDER BY monthly`", "Works", "`ORDER BY` runs after `SELECT`"],
        ["`WHERE ROW_NUMBER() OVER (…) = 1`", "Error", "Window functions are computed in `SELECT` — filter in an outer query / CTE"],
    )
    yield sql('''
        SELECT dept_id, COUNT(*) AS headcount
        FROM employees
        WHERE COUNT(*) > 2
        GROUP BY dept_id;
    ''', fails=True, err='misuse of aggregate: COUNT()')
    yield sql('''
        SELECT dept_id, COUNT(*) AS headcount
        FROM employees
        WHERE dept_id IS NOT NULL           -- row filter: before grouping
        GROUP BY dept_id
        HAVING COUNT(*) > 2                 -- group filter: after grouping
        ORDER BY headcount DESC;            -- alias is fine here
    ''', out='''
        dept_id | headcount
        --------+----------
        1       | 4
        2       | 3
    ''')
    yield sql('''
        -- to filter on a computed column, compute it in a subquery / CTE first
        SELECT name, monthly
        FROM (SELECT name, salary / 12 AS monthly FROM employees) AS t
        WHERE monthly > 9000
        ORDER BY monthly DESC;
    ''', out='''
        name  | monthly
        ------+--------
        Asha  | 12500
        Ravi  | 10000
        Priya | 9166
    ''')
    yield note("This is the **logical** order — it defines what a query means. The optimizer is free to execute it physically in any order that gives the same result (for example, pushing a filter into an index lookup).")
    yield qa("What is the order of execution of a SQL query?",
             "`FROM`/`JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` (incl. window functions) → `DISTINCT` → `ORDER BY` → `LIMIT`/`OFFSET`. That is why `WHERE` can't see aggregates or select-list aliases, and `ORDER BY` can.")


@topic(G, "null-handling", "NULL & Three-Valued Logic", "question-mark")
def _():
    yield lead("`NULL` means *unknown / missing*. It is not zero, not an empty string, and not equal to anything — not even another `NULL`.")
    yield define("Three-valued logic", "SQL conditions evaluate to `TRUE`, `FALSE` or `UNKNOWN`. Any comparison with `NULL` (`=`, `<>`, `<`…) is `UNKNOWN`, and `WHERE` keeps only `TRUE` rows.")
    yield section("Comparisons with NULL", "equal-not")
    yield sql('''
        SELECT NULL = NULL      AS eq,
               NULL <> 1        AS ne,
               NULL IS NULL     AS is_null,
               1 IS NOT NULL    AS is_not_null,
               NULL + 5         AS arithmetic,
               'a' || NULL      AS concat;
    ''', out='''
        eq   | ne   | is_null | is_not_null | arithmetic | concat
        -----+------+---------+-------------+------------+-------
        NULL | NULL | 1       | 1           | NULL       | NULL
    ''', setup="")
    yield p("(SQLite shows `TRUE`/`FALSE` as `1`/`0` and `UNKNOWN` as `NULL`.) `NULL` propagates through arithmetic and concatenation — one missing value makes the whole expression `NULL`.")
    yield sql('''
        SELECT name FROM employees WHERE email = NULL;        -- always empty!
        SELECT name FROM employees WHERE email IS NULL ORDER BY name;
    ''', out='''
        name
        ----

        name
        ----
        Dev
        Neha
    ''')
    yield section("Truth tables", "table")
    yield table(
        ["`AND`", "TRUE", "FALSE", "UNKNOWN"],
        ["**TRUE**", "TRUE", "FALSE", "UNKNOWN"],
        ["**FALSE**", "FALSE", "FALSE", "FALSE"],
        ["**UNKNOWN**", "UNKNOWN", "FALSE", "UNKNOWN"],
    )
    yield table(
        ["`OR`", "TRUE", "FALSE", "UNKNOWN"],
        ["**TRUE**", "TRUE", "TRUE", "TRUE"],
        ["**FALSE**", "TRUE", "FALSE", "UNKNOWN"],
        ["**UNKNOWN**", "TRUE", "UNKNOWN", "UNKNOWN"],
    )
    yield p("`NOT UNKNOWN` is still `UNKNOWN`. So a row with a `NULL` column fails *both* `x = 5` and `NOT (x = 5)`:")
    yield sql('''
        SELECT COUNT(*) AS total,
               SUM(dept_id = 1)                   AS in_eng,
               SUM(NOT (dept_id = 1))             AS not_in_eng,
               SUM(dept_id IS NULL)               AS no_dept
        FROM employees;
    ''', out='''
        total | in_eng | not_in_eng | no_dept
        ------+--------+------------+--------
        10    | 4      | 5          | 1
    ''')
    yield section("The NOT IN trap", "alert-triangle")
    yield sql('''
        -- customers outside Mumbai and Delhi (Kavya's city is NULL)
        SELECT name FROM customers WHERE city NOT IN ('Mumbai', 'Delhi') ORDER BY name;
        SELECT 'x' AS found WHERE 3 NOT IN (1, 2, NULL);
    ''', out='''
        name
        -----
        Sneha

        found
        -----
    ''')
    yield warn("`x NOT IN (1, 2, NULL)` is never true: it means `x <> 1 AND x <> 2 AND x <> NULL`, and the last part is unknown. If a `NOT IN (subquery)` can return a `NULL`, the whole query returns nothing. Use `NOT EXISTS` instead (see Semi & Anti Joins). Also note Kavya (city `NULL`) is missing from the first result.")
    yield section("NULL-handling functions", "tool")
    yield table(
        ["Function", "Returns", "Portability"],
        ["`COALESCE(a, b, c…)`", "First non-`NULL` argument", "Standard — everywhere"],
        ["`NULLIF(a, b)`", "`NULL` if `a = b`, else `a`", "Standard — everywhere"],
        ["`IFNULL(a, b)`", "`b` if `a` is `NULL`", "MySQL, SQLite"],
        ["`ISNULL(a, b)` / `NVL(a, b)`", "Same idea", "SQL Server / Oracle"],
        ["`a IS DISTINCT FROM b`", "Null-safe `<>` (`NULL` vs `NULL` → false)", "Standard; PostgreSQL, SQL Server 2022, SQLite (`IS NOT`)"],
    )
    yield sql('''
        SELECT name,
               COALESCE(email, 'no email')          AS contact,
               COALESCE(dept_id, 0)                 AS dept
        FROM employees
        WHERE emp_id IN (6, 7, 10)
        ORDER BY emp_id;

        -- NULLIF avoids division by zero: x / 0 → x / NULL → NULL
        SELECT 100 / NULLIF(0, 0) AS safe_div;

        -- null-safe equality (SQLite: IS / IS NOT; standard: IS [NOT] DISTINCT FROM)
        SELECT NULL IS NULL AS both_null, 1 IS NOT NULL AS differ, NULL IS 1 AS null_vs_1;
    ''', out='''
        name  | contact       | dept
        ------+---------------+-----
        Arjun | arjun@corp.in | 2
        Neha  | no email      | 2
        Dev   | no email      | 0

        safe_div
        --------
        NULL

        both_null | differ | null_vs_1
        ----------+--------+----------
        1         | 1      | 0
    ''')
    yield section("NULL in aggregates, sorting and grouping", "list-check")
    yield ul(
        "Aggregates **ignore** `NULL`s: `COUNT(email)` counts non-null emails; `AVG` divides by the non-null count.",
        "`COUNT(*)` counts rows, whatever they contain.",
        "`GROUP BY` and `DISTINCT` put all `NULL`s into **one** group.",
        "`ORDER BY` puts `NULL`s first or last depending on the engine.",
        "`UNIQUE` allows multiple `NULL`s (except SQL Server).",
    )
    yield sql('''
        SELECT COUNT(*) AS all_rows, COUNT(email) AS with_email, COUNT(dept_id) AS with_dept
        FROM employees;
    ''', out='''
        all_rows | with_email | with_dept
        ---------+------------+----------
        10       | 8          | 9
    ''')
    yield qa("What is the difference between NULL, 0 and an empty string?",
             "`0` and `''` are known values that compare and sort normally. `NULL` is the absence of a value: comparisons with it yield `UNKNOWN`, it is skipped by aggregates and needs `IS NULL`. (Oracle is odd: it treats `''` as `NULL`.)")
    yield qa("Why does WHERE col <> 'x' not return rows where col is NULL?",
             "`NULL <> 'x'` is `UNKNOWN`, and `WHERE` keeps only `TRUE`. Write `WHERE col <> 'x' OR col IS NULL`, or `WHERE col IS DISTINCT FROM 'x'`.")


@topic(G, "case-expression", "CASE Expressions", "git-branch")
def _():
    yield lead("`CASE` is SQL's if/else. It is an **expression** — it returns a value and can be used anywhere a value can: `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY`, inside aggregates.")
    yield section("Searched CASE", "list-search")
    yield sql('''
        SELECT name, salary,
               CASE
                   WHEN salary >= 120000 THEN 'Senior'
                   WHEN salary >= 90000  THEN 'Mid'
                   ELSE 'Junior'
               END AS band
        FROM employees
        ORDER BY salary DESC, emp_id;
    ''', out='''
        name   | salary | band
        -------+--------+-------
        Asha   | 150000 | Senior
        Ravi   | 120000 | Senior
        Priya  | 110000 | Mid
        Meera  | 95000  | Mid
        Karan  | 95000  | Mid
        Sara   | 85000  | Junior
        Vikram | 80000  | Junior
        Neha   | 72000  | Junior
        Arjun  | 70000  | Junior
        Dev    | 60000  | Junior
    ''')
    yield p("Conditions are tested top to bottom and the **first** true branch wins — so order the `WHEN`s from most to least specific. Without `ELSE`, unmatched rows get `NULL`.")
    yield section("Simple CASE", "switch")
    yield sql('''
        SELECT order_id,
               CASE status
                   WHEN 'delivered' THEN 'Done'
                   WHEN 'shipped'   THEN 'On the way'
                   WHEN 'pending'   THEN 'Processing'
               END AS label
        FROM orders
        ORDER BY order_id;
    ''', out='''
        order_id | label
        ---------+-----------
        101      | Done
        102      | Done
        103      | Done
        104      | On the way
        105      | NULL
        106      | Done
        107      | Processing
        108      | On the way
    ''')
    yield warn("A simple `CASE x WHEN NULL THEN …` never matches — it tests `x = NULL`. Use the searched form: `CASE WHEN x IS NULL THEN …`.")
    yield section("CASE inside aggregates: conditional counts", "sum")
    yield sql('''
        SELECT COUNT(*)                                           AS orders,
               SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
               SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
               COUNT(CASE WHEN order_date >= '2024-03-01' THEN 1 END) AS in_march
        FROM orders;
    ''', out='''
        orders | delivered | cancelled | in_march
        -------+-----------+-----------+---------
        8      | 4         | 1         | 3
    ''')
    yield p("This pattern — an aggregate over a `CASE` — is the basis of **pivot** queries (see Interview Prep). `COUNT(CASE … THEN 1 END)` works because unmatched rows produce `NULL`, which `COUNT` skips. PostgreSQL also offers `COUNT(*) FILTER (WHERE status = 'delivered')`.")
    yield section("CASE in ORDER BY and UPDATE", "arrows-sort")
    yield sql('''
        -- different raise per band, in one statement
        UPDATE employees
        SET salary = salary + CASE WHEN salary < 80000 THEN 5000
                                   WHEN salary < 100000 THEN 3000
                                   ELSE 0 END;

        SELECT name, salary FROM employees WHERE salary < 110000 ORDER BY salary, emp_id;
    ''', out='''
        name   | salary
        -------+-------
        Dev    | 65000
        Arjun  | 75000
        Neha   | 77000
        Vikram | 83000
        Sara   | 88000
        Meera  | 98000
        Karan  | 98000
    ''')
    yield note("Short forms: `IIF(cond, a, b)` (SQL Server, SQLite), `IF(cond, a, b)` (MySQL), `DECODE(x, v1, r1, …, default)` (Oracle). `CASE` works everywhere.")
    yield qa("Can you use CASE in a WHERE clause?",
             "Yes — it is just an expression: `WHERE CASE WHEN :role = 'admin' THEN 1 WHEN owner_id = :me THEN 1 ELSE 0 END = 1`. But plain `AND`/`OR` logic is usually clearer and friendlier to indexes.")
