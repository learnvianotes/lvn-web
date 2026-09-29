from kit import *
from sample_db import sql, dialect

G = "Functions & Aggregation"


@topic(G, "string-functions", "String Functions", "letter-case")
def _():
    yield lead("Built-in functions clean, slice, combine and format text. Names differ between engines more than anywhere else — learn the ideas, then look up the local spelling.")
    yield section("The essentials", "list")
    yield table(
        ["Task", "SQLite / standard", "MySQL", "SQL Server", "PostgreSQL"],
        ["Length", "`length(s)`", "`CHAR_LENGTH(s)` (`LENGTH` = bytes)", "`LEN(s)`", "`length(s)`"],
        ["Upper / lower", "`upper(s)`, `lower(s)`", "same", "same", "same"],
        ["Substring", "`substr(s, start, len)`", "`SUBSTRING(s, start, len)`", "`SUBSTRING(s, start, len)`", "`substring(s from 2 for 3)`"],
        ["First / last n", "`substr(s, 1, n)`, `substr(s, -n)`", "`LEFT(s, n)`, `RIGHT(s, n)`", "`LEFT`, `RIGHT`", "`left`, `right`"],
        ["Trim", "`trim(s)`, `ltrim`, `rtrim`", "same", "`TRIM` (2017+), `LTRIM`, `RTRIM`", "same"],
        ["Find position", "`instr(s, sub)`", "`INSTR(s, sub)` / `LOCATE`", "`CHARINDEX(sub, s)`", "`position(sub in s)`"],
        ["Replace", "`replace(s, from, to)`", "same", "same", "same"],
        ["Concatenate", "`a || b`, `concat(a, b)`", "`CONCAT(a, b)`", "`a + b`, `CONCAT`", "`a || b`, `concat`"],
        ["Pad", "`printf('%5s', s)`", "`LPAD(s, 5, ' ')`", "`RIGHT(SPACE(5) + s, 5)`", "`lpad(s, 5)`"],
    )
    yield note("SQL strings are **1-indexed**: the first character is position 1, and `instr`/`CHARINDEX` return `0` when not found.")
    yield section("Slicing and searching", "cut")
    yield sql('''
        SELECT email,
               length(email)                              AS len,
               instr(email, '@')                          AS at_pos,
               substr(email, 1, instr(email, '@') - 1)    AS username,
               substr(email, instr(email, '@') + 1)       AS domain,
               substr(email, -2)                          AS last_two
        FROM employees
        WHERE emp_id IN (1, 8)
        ORDER BY emp_id;
    ''', out='''
        email          | len | at_pos | username | domain  | last_two
        ---------------+-----+--------+----------+---------+---------
        asha@corp.in   | 12  | 5      | asha     | corp.in | in
        vikram@corp.in | 14  | 7      | vikram   | corp.in | in
    ''')
    yield section("Cleaning text", "wash")
    yield sql('''
        SELECT '[' || trim('   padded   ') || ']'        AS trimmed,
               ltrim('000742', '0')                      AS no_zeros,
               replace('2024/03/15', '/', '-')           AS iso_date,
               lower('MiXeD CaSe')                       AS lowered;
    ''', out='''
        trimmed  | no_zeros | iso_date   | lowered
        ---------+----------+------------+-----------
        [padded] | 742      | 2024-03-15 | mixed case
    ''', setup="")
    yield section("Building strings", "writing")
    yield sql('''
        SELECT name || ' (' || COALESCE(email, 'n/a') || ')'   AS with_pipe,
               concat(name, ' - ', dept_id)                    AS with_concat,
               concat_ws(', ', name, email, dept_id)           AS with_separator,
               printf('%-6s|%8d', name, salary)                AS formatted
        FROM employees
        WHERE emp_id IN (7, 10)
        ORDER BY emp_id;
    ''', out='''
        with_pipe  | with_concat | with_separator | formatted
        -----------+-------------+----------------+----------------
        Neha (n/a) | Neha - 2    | Neha, 2        | Neha  |   72000
        Dev (n/a)  | Dev -       | Dev            | Dev   |   60000
    ''')
    yield warn("`||` with a `NULL` operand gives `NULL` (see Neha's email handled with `COALESCE`). `concat()` treats `NULL` as an empty string in SQLite, PostgreSQL and SQL Server — but in **MySQL** `CONCAT()` returns `NULL` if any argument is `NULL`. `concat_ws` skips `NULL`s everywhere (Dev's missing email and department vanish).")
    yield section("Aggregating strings", "list-details")
    yield sql('''
        SELECT dept_id,
               group_concat(name, ', ' ORDER BY name) AS team
        FROM employees
        WHERE dept_id IS NOT NULL
        GROUP BY dept_id
        ORDER BY dept_id;
    ''', out='''
        dept_id | team
        --------+-------------------------
        1       | Asha, Karan, Meera, Ravi
        2       | Arjun, Neha, Priya
        3       | Sara, Vikram
    ''')
    yield p("Spellings: `STRING_AGG(name, ', ' ORDER BY name)` (PostgreSQL, SQLite 3.44+), `STRING_AGG(name, ', ') WITHIN GROUP (ORDER BY name)` (SQL Server), `GROUP_CONCAT(name ORDER BY name SEPARATOR ', ')` (MySQL), `LISTAGG(name, ', ') WITHIN GROUP (ORDER BY name)` (Oracle).")
    yield qa("How do you extract the domain from an email in SQL?",
             "Find the `@` and take everything after it: `substr(email, instr(email, '@') + 1)` (SQLite/MySQL), `SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email))` (SQL Server), `split_part(email, '@', 2)` (PostgreSQL), `SUBSTRING_INDEX(email, '@', -1)` (MySQL).")


@topic(G, "numeric-functions", "Numeric Functions & Type Casting", "calculator")
def _():
    yield lead("Rounding, absolute values, modulo and explicit casts — plus the integer-division and rounding rules that trip people up.")
    yield table(
        ["Function", "Does", "Example → result"],
        ["`ROUND(x, d)`", "Round to `d` decimals (half away from zero in most engines)", "`ROUND(2.567, 1)` → `2.6`"],
        ["`CEIL(x)` / `FLOOR(x)`", "Round up / down to an integer", "`CEIL(2.1)` → `3`"],
        ["`ABS(x)`", "Absolute value", "`ABS(-7)` → `7`"],
        ["`x % y` / `MOD(x, y)`", "Remainder", "`17 % 5` → `2`"],
        ["`POWER(x, y)`, `SQRT(x)`", "Powers and roots", "`POWER(2, 10)` → `1024`"],
        ["`SIGN(x)`", "−1, 0 or 1", "`SIGN(-3)` → `-1`"],
        ["`CAST(x AS type)`", "Convert type", "`CAST('42' AS INTEGER)` → `42`"],
    )
    yield sql('''
        SELECT ROUND(2.567, 1)  AS r1,
               ROUND(2.5)       AS half_up,
               ROUND(-2.5)      AS half_neg,
               CEIL(2.1)        AS ceil_,
               FLOOR(-2.1)      AS floor_,
               ABS(-7)          AS abs_,
               17 % 5           AS mod_,
               POWER(2, 10)     AS pow_,
               SQRT(144)        AS sqrt_,
               SIGN(-3)         AS sign_;
    ''', out='''
        r1  | half_up | half_neg | ceil_ | floor_ | abs_ | mod_ | pow_   | sqrt_ | sign_
        ----+---------+----------+-------+--------+------+------+--------+-------+------
        2.6 | 3.0     | -3.0     | 3.0   | -3.0   | 7    | 2    | 1024.0 | 12.0  | -1
    ''', setup="")
    yield section("Integer division and averages", "divide")
    yield sql('''
        SELECT 7 / 2                    AS int_div,
               7 / 2.0                  AS real_div,
               CAST(7 AS REAL) / 2      AS cast_div,
               7 * 1.0 / 2              AS times_one;

        -- percentage of employees in Engineering: the classic integer-division bug
        SELECT SUM(dept_id = 1) * 100 / COUNT(*)                  AS wrong_looking,
               ROUND(SUM(dept_id = 1) * 100.0 / COUNT(*), 1)      AS pct
        FROM employees;
    ''', out='''
        int_div | real_div | cast_div | times_one
        --------+----------+----------+----------
        3       | 3.5      | 3.5      | 3.5

        wrong_looking | pct
        --------------+-----
        40            | 40.0
    ''')
    yield p("Both answers are 40 here only because 4/10 divides evenly; with 4/9 the first would print `44` instead of `44.4`. Multiply by `100.0` (or cast) **before** dividing.")
    yield section("CAST and conversions", "transform")
    yield sql('''
        SELECT CAST('42' AS INTEGER) + 1     AS to_int,
               CAST(3.99 AS INTEGER)         AS truncates,
               CAST(150000 AS TEXT) || ' INR' AS to_text,
               CAST('12abc' AS INTEGER)      AS lenient,
               '10' + 5                      AS implicit;
    ''', out='''
        to_int | truncates | to_text    | lenient | implicit
        -------+-----------+------------+---------+---------
        43     | 3         | 150000 INR | 12      | 15
    ''', setup="")
    yield warn("SQLite converts leniently (`'12abc'` → `12`). PostgreSQL and SQL Server raise an error on a bad cast; use `TRY_CAST` (SQL Server), `SAFE_CAST` (BigQuery) or validate first. Relying on implicit conversion (`'10' + 5`) also hides bugs and can disable index use.")
    yield dialect('''
        SELECT CAST(salary AS DECIMAL(10, 2)) FROM employees;     -- standard
        SELECT salary::numeric(10, 2) FROM employees;              -- PostgreSQL shorthand
        SELECT CONVERT(VARCHAR(20), salary) FROM employees;        -- SQL Server
        SELECT TRY_CAST('12abc' AS INT);                           -- SQL Server → NULL instead of error
    ''', "Standard / PostgreSQL / SQL Server")
    yield section("Bucketing numbers", "chart-bar")
    yield sql('''
        SELECT (salary / 25000) * 25000       AS bucket_from,
               COUNT(*)                        AS employees
        FROM employees
        GROUP BY bucket_from
        ORDER BY bucket_from;
    ''', out='''
        bucket_from | employees
        ------------+----------
        50000       | 3
        75000       | 4
        100000      | 2
        150000      | 1
    ''')
    yield qa("What does ROUND(2.5) return?",
             "`3` in SQLite, MySQL, PostgreSQL (numeric), SQL Server and Oracle — they round half *away from zero*. But PostgreSQL's `round()` on `double precision` and many programming languages use banker's rounding (half to even, `2`). Know your types when cents matter.")


@topic(G, "date-time-functions", "Date & Time Functions", "calendar")
def _():
    yield lead("Dates are the least portable part of SQL. The concepts — extract a part, add an interval, difference two dates, truncate to a period — exist everywhere under different names.")
    yield section("Dialect map", "language")
    yield table(
        ["Task", "SQLite", "PostgreSQL", "MySQL", "SQL Server"],
        ["Now", "`datetime('now')`", "`now()`", "`NOW()`", "`GETDATE()` / `SYSDATETIME()`"],
        ["Today", "`date('now')`", "`CURRENT_DATE`", "`CURDATE()`", "`CAST(GETDATE() AS date)`"],
        ["Year of d", "`strftime('%Y', d)`", "`EXTRACT(YEAR FROM d)`", "`YEAR(d)`", "`YEAR(d)` / `DATEPART(year, d)`"],
        ["Add 1 month", "`date(d, '+1 month')`", "`d + INTERVAL '1 month'`", "`DATE_ADD(d, INTERVAL 1 MONTH)`", "`DATEADD(month, 1, d)`"],
        ["Days between", "`julianday(b) - julianday(a)`", "`b - a` (dates)", "`DATEDIFF(b, a)`", "`DATEDIFF(day, a, b)`"],
        ["Start of month", "`date(d, 'start of month')`", "`date_trunc('month', d)`", "`DATE_FORMAT(d, '%Y-%m-01')`", "`DATETRUNC(month, d)` (2022)"],
        ["Format", "`strftime('%d/%m/%Y', d)`", "`to_char(d, 'DD/MM/YYYY')`", "`DATE_FORMAT(d, '%d/%m/%Y')`", "`FORMAT(d, 'dd/MM/yyyy')`"],
    )
    yield note("SQLite stores dates as ISO-8601 text (`'2024-03-15'`, `'2024-03-15 09:30:00'`), which sorts and compares correctly as strings. Its date functions take such a string plus *modifiers*.", "SQLite")
    yield section("Extracting parts", "calendar-event")
    yield sql('''
        SELECT hire_date,
               strftime('%Y', hire_date)           AS year,
               CAST(strftime('%m', hire_date) AS INTEGER) AS month,
               strftime('%w', hire_date)           AS weekday_0_sun,
               strftime('%d/%m/%Y', hire_date)     AS indian_format
        FROM employees
        WHERE emp_id IN (1, 2, 3)
        ORDER BY emp_id;
    ''', out='''
        hire_date  | year | month | weekday_0_sun | indian_format
        -----------+------+-------+---------------+--------------
        2015-03-01 | 2015 | 3     | 0             | 01/03/2015
        2017-06-15 | 2017 | 6     | 4             | 15/06/2017
        2019-01-10 | 2019 | 1     | 4             | 10/01/2019
    ''')
    yield section("Date arithmetic", "calendar-plus")
    yield sql('''
        SELECT date('2024-01-31', '+1 month')             AS plus_month,
               date('2024-03-15', '-10 days')             AS minus_days,
               date('2024-03-15', 'start of month')       AS month_start,
               date('2024-03-15', 'start of month', '+1 month', '-1 day') AS month_end,
               julianday('2024-03-01') - julianday('2024-02-01')          AS days_in_feb;
    ''', out='''
        plus_month | minus_days | month_start | month_end  | days_in_feb
        -----------+------------+-------------+------------+------------
        2024-03-02 | 2024-03-05 | 2024-03-01  | 2024-03-31 | 29.0
    ''', setup="")
    yield warn("Month arithmetic has edge cases: SQLite turns `2024-01-31 + 1 month` into `2024-03-02` (Feb 31 overflows). PostgreSQL and MySQL clamp to the last day (`2024-02-29`). Test month-end logic explicitly.")
    yield section("Tenure and age", "hourglass")
    yield sql('''
        -- as of a fixed reporting date, so the output never changes
        SELECT name, hire_date,
               CAST((julianday('2024-12-31') - julianday(hire_date)) / 365.25 AS INTEGER) AS years_service
        FROM employees
        ORDER BY hire_date
        LIMIT 4;
    ''', out='''
        name   | hire_date  | years_service
        -------+------------+--------------
        Asha   | 2015-03-01 | 9
        Priya  | 2016-11-20 | 8
        Ravi   | 2017-06-15 | 7
        Vikram | 2018-09-05 | 6
    ''')
    yield section("Grouping by period", "calendar-stats")
    yield sql('''
        SELECT strftime('%Y-%m', o.order_date)          AS month,
               COUNT(DISTINCT o.order_id)                AS orders,
               SUM(oi.quantity * oi.unit_price)          AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status <> 'cancelled'
        GROUP BY month
        ORDER BY month;
    ''', out='''
        month   | orders | revenue
        --------+--------+--------
        2024-01 | 2      | 66700
        2024-02 | 2      | 12900
        2024-03 | 3      | 63700
    ''')
    yield good("Store timestamps in **UTC** (`TIMESTAMPTZ` in PostgreSQL, `DATETIME2`/`DATETIMEOFFSET` in SQL Server) and convert to local time only for display.")
    yield warn("Wrapping an indexed column in a function (`WHERE strftime('%Y', order_date) = '2024'`) usually prevents index use. Rewrite as a range: `WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`.", "Performance")
    yield qa("How do you find orders placed in the last 30 days?",
             "`WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'` (PostgreSQL), `>= DATE_SUB(CURDATE(), INTERVAL 30 DAY)` (MySQL), `>= DATEADD(day, -30, CAST(GETDATE() AS date))` (SQL Server), `>= date('now', '-30 days')` (SQLite). Keep the column bare so an index on it can be used.")


@topic(G, "aggregate-functions", "Aggregate Functions", "sum")
def _():
    yield lead("Aggregate functions collapse many rows into one value: how many, how much, the average, the extremes.")
    yield table(
        ["Function", "Returns", "NULLs"],
        ["`COUNT(*)`", "Number of rows", "Counted"],
        ["`COUNT(col)`", "Number of non-null values", "Ignored"],
        ["`COUNT(DISTINCT col)`", "Number of different non-null values", "Ignored"],
        ["`SUM(col)`", "Total", "Ignored (all `NULL` → `NULL`)"],
        ["`AVG(col)`", "Mean = `SUM / COUNT(col)`", "Ignored"],
        ["`MIN(col)` / `MAX(col)`", "Smallest / largest (also for text and dates)", "Ignored"],
    )
    yield sql('''
        SELECT COUNT(*)                 AS employees,
               COUNT(email)             AS with_email,
               COUNT(DISTINCT dept_id)  AS departments,
               SUM(salary)              AS payroll,
               AVG(salary)              AS avg_salary,
               MIN(hire_date)           AS first_hire,
               MAX(name)                AS last_name_alpha
        FROM employees;
    ''', out='''
        employees | with_email | departments | payroll | avg_salary | first_hire | last_name_alpha
        ----------+------------+-------------+---------+------------+------------+----------------
        10        | 8          | 3           | 937000  | 93700.0    | 2015-03-01 | Vikram
    ''')
    yield section("NULLs change averages", "question-mark")
    yield sql('''
        CREATE TABLE ratings (product TEXT, stars INTEGER);
        INSERT INTO ratings VALUES ('A', 5), ('A', 3), ('A', NULL), ('B', NULL);

        SELECT product,
               COUNT(*)              AS rows_,
               COUNT(stars)          AS rated,
               AVG(stars)            AS avg_ignoring_null,
               AVG(COALESCE(stars, 0)) AS avg_null_as_zero,
               SUM(stars)            AS total
        FROM ratings
        GROUP BY product
        ORDER BY product;
    ''', out='''
        product | rows_ | rated | avg_ignoring_null | avg_null_as_zero   | total
        --------+-------+-------+-------------------+--------------------+------
        A       | 3     | 2     | 4.0               | 2.6666666666666665 | 8
        B       | 1     | 0     | NULL              | 0.0                | NULL
    ''', setup="")
    yield p("Decide what `NULL` means for your metric. Product B shows the other surprise: `SUM` over only `NULL`s is `NULL`, not `0` — wrap it: `COALESCE(SUM(x), 0)`.")
    yield section("Aggregates over an empty set", "circle-dashed")
    yield sql('''
        SELECT COUNT(*) AS n, SUM(salary) AS total, MAX(salary) AS top
        FROM employees
        WHERE dept_id = 4;             -- Marketing has nobody
    ''', out='''
        n | total | top
        --+-------+-----
        0 | NULL  | NULL
    ''')
    yield note("Without `GROUP BY`, an aggregate query always returns **exactly one row** — even when no rows matched. With `GROUP BY`, no matching rows means no groups and zero result rows.")
    yield section("Conditional aggregation", "filter")
    yield sql('''
        SELECT SUM(CASE WHEN category = 'Electronics' THEN price END) AS electronics_value,
               AVG(CASE WHEN category = 'Furniture'   THEN price END) AS avg_furniture,
               COUNT(CASE WHEN price < 100 THEN 1 END)                 AS cheap_items
        FROM products;
    ''', out='''
        electronics_value | avg_furniture | cheap_items
        ------------------+---------------+------------
        69500             | 6250.0        | 2
    ''')
    yield warn("You cannot nest aggregates (`MAX(AVG(salary))`) in one level in most engines. Aggregate in a subquery or CTE first, then aggregate the result.")
    yield qa("What is the difference between COUNT(*), COUNT(1) and COUNT(column)?",
             "`COUNT(*)` and `COUNT(1)` both count rows and perform the same in modern engines. `COUNT(column)` counts rows where that column is **not** `NULL`. `COUNT(DISTINCT column)` counts distinct non-null values.")
    yield qa("Does AVG include NULL values?",
             "No. `AVG(x)` = `SUM(x) / COUNT(x)` over non-null values only. To treat missing as zero, use `AVG(COALESCE(x, 0))`.")


@topic(G, "group-by", "GROUP BY", "layout-grid")
def _():
    yield lead("`GROUP BY` splits rows into groups that share the same values, then aggregates each group into a single output row.")
    yield section("One row per group", "stack-2")
    yield sql('''
        SELECT dept_id,
               COUNT(*)            AS headcount,
               SUM(salary)         AS payroll,
               ROUND(AVG(salary))  AS avg_salary,
               MAX(salary)         AS top_salary
        FROM employees
        GROUP BY dept_id
        ORDER BY dept_id;
    ''', out='''
        dept_id | headcount | payroll | avg_salary | top_salary
        --------+-----------+---------+------------+-----------
        NULL    | 1         | 60000   | 60000.0    | 60000
        1       | 4         | 460000  | 115000.0   | 150000
        2       | 3         | 252000  | 84000.0    | 110000
        3       | 2         | 165000  | 82500.0    | 85000
    ''')
    yield p("Dev, with no department, forms his own `NULL` group — all `NULL`s are grouped together.")
    yield section("The golden rule", "rule")
    yield p("Every column in `SELECT` must either be in `GROUP BY` or be inside an aggregate. Otherwise the query asks for “the name” of a group that contains four names.")
    yield sql('''
        SELECT dept_id, name, MAX(salary) AS top_salary      -- name is not grouped or aggregated
        FROM employees
        WHERE dept_id IS NOT NULL
        GROUP BY dept_id
        ORDER BY dept_id;
    ''', out='''
        dept_id | name  | top_salary
        --------+-------+-----------
        1       | Asha  | 150000
        2       | Priya | 110000
        3       | Sara  | 85000
    ''', caption="SQLite — allowed, but not portable")
    yield warn("PostgreSQL, SQL Server and Oracle reject that query (*column must appear in the GROUP BY clause or be used in an aggregate function*); MySQL rejects it under the default `ONLY_FULL_GROUP_BY`. SQLite accepts it and, as a special case with a single `MAX`/`MIN`, returns the name from the max row. Don't rely on it — use a window function or a join (see *Top-N per group*).")
    yield section("Grouping by several columns or expressions", "columns")
    yield sql('''
        SELECT p.category,
               o.status,
               SUM(oi.quantity) AS units
        FROM order_items oi
        JOIN orders o   ON o.order_id = oi.order_id
        JOIN products p ON p.product_id = oi.product_id
        GROUP BY p.category, o.status
        ORDER BY p.category, o.status;
    ''', out='''
        category    | status    | units
        ------------+-----------+------
        Electronics | cancelled | 2
        Electronics | delivered | 3
        Electronics | shipped   | 1
        Furniture   | delivered | 2
        Furniture   | shipped   | 3
        Stationery  | delivered | 20
        Stationery  | pending   | 20
    ''')
    yield sql('''
        SELECT strftime('%Y', hire_date) AS hire_year, COUNT(*) AS hires
        FROM employees
        WHERE hire_date >= '2020-01-01'
        GROUP BY hire_year
        ORDER BY hire_year;
    ''', out='''
        hire_year | hires
        ----------+------
        2020      | 1
        2021      | 1
        2022      | 1
        2023      | 1
        2024      | 1
    ''')
    yield section("Subtotals: ROLLUP, CUBE, GROUPING SETS", "sum")
    yield dialect('''
        SELECT dept_id, EXTRACT(YEAR FROM hire_date) AS yr, SUM(salary)
        FROM employees
        GROUP BY ROLLUP (dept_id, yr);          -- per (dept, year), per dept, grand total

        -- MySQL: GROUP BY dept_id, yr WITH ROLLUP
        -- GROUPING SETS ((dept_id), (yr), ())  -- exactly the groupings you list
        -- CUBE (dept_id, yr)                   -- every combination
    ''', "PostgreSQL / SQL Server / Oracle / MySQL")
    yield p("SQLite has no `ROLLUP`; the same result is a `UNION ALL` of the groupings:")
    yield sql('''
        SELECT d.name AS department, SUM(e.salary) AS payroll
        FROM employees e JOIN departments d ON d.dept_id = e.dept_id
        GROUP BY d.name
        UNION ALL
        SELECT 'ALL DEPARTMENTS', SUM(e.salary)
        FROM employees e JOIN departments d ON d.dept_id = e.dept_id
        ORDER BY payroll;
    ''', out='''
        department      | payroll
        ----------------+--------
        HR              | 165000
        Sales           | 252000
        Engineering     | 460000
        ALL DEPARTMENTS | 877000
    ''')
    yield qa("Can you GROUP BY a column that is not in the SELECT list?",
             "Yes — `SELECT COUNT(*) FROM employees GROUP BY dept_id` returns one count per department without showing which is which. It is legal, just rarely useful. The reverse (selecting a non-grouped, non-aggregated column) is the error.")
    yield qa("What does GROUP BY do with NULL values?",
             "It treats all `NULL`s in the grouping column as one group (even though `NULL = NULL` is not true). The group shows up with `NULL` as its key.")


@topic(G, "having", "HAVING vs WHERE", "filter-cog")
def _():
    yield lead("`WHERE` filters **rows** before grouping; `HAVING` filters **groups** after aggregation. Same idea, different stage.")
    yield table(
        ["", "`WHERE`", "`HAVING`"],
        ["Filters", "Individual rows", "Groups (aggregated rows)"],
        ["Runs", "Before `GROUP BY`", "After `GROUP BY`"],
        ["Can use aggregates", "No", "Yes"],
        ["Can use indexes", "Yes", "Rarely — groups are computed first"],
        ["Needs `GROUP BY`", "No", "Usually (without it, the whole table is one group)"],
    )
    yield sql('''
        -- departments whose average salary exceeds 90000, counting only people hired before 2023
        SELECT dept_id,
               COUNT(*)            AS staff,
               ROUND(AVG(salary))  AS avg_salary
        FROM employees
        WHERE hire_date < '2023-01-01'          -- rows
        GROUP BY dept_id
        HAVING AVG(salary) > 90000              -- groups
        ORDER BY avg_salary DESC;
    ''', out='''
        dept_id | staff | avg_salary
        --------+-------+-----------
        1       | 4     | 115000.0
    ''')
    yield section("Customers with more than one order", "users")
    yield sql('''
        SELECT customer_id, COUNT(*) AS orders
        FROM orders
        GROUP BY customer_id
        HAVING COUNT(*) > 1
        ORDER BY customer_id;
    ''', out='''
        customer_id | orders
        ------------+-------
        1           | 3
        2           | 2
        3           | 2
    ''')
    yield section("Put row filters in WHERE", "bolt")
    yield dodont(
        "`WHERE status <> 'cancelled' … GROUP BY customer_id` — discards rows early, can use an index, groups less data.",
        "`… GROUP BY customer_id, status HAVING status <> 'cancelled'` — works, but groups everything first and changes the grouping.",
    )
    yield sql('''
        -- HAVING without GROUP BY: the whole table is one group
        SELECT COUNT(*) AS products FROM products HAVING MIN(price) < 100;
        SELECT COUNT(*) AS products FROM products HAVING MIN(price) < 10;
    ''', out='''
        products
        --------
        7

        products
        --------
    ''')
    yield qa("What is the difference between WHERE and HAVING?",
             "`WHERE` filters rows before grouping and cannot reference aggregates. `HAVING` filters groups after `GROUP BY` and can reference aggregates like `COUNT(*) > 1`. Use `WHERE` for anything that doesn't need an aggregate — it's cheaper.")
    yield qa("Find duplicate emails in a users table.",
             "`SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;` — group by the value that should be unique and keep groups with more than one row.")
