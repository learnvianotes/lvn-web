from kit import *
from sample_db import sql, dialect, SCHEMA

G = "Joins & Set Operations"

GRADES = """
CREATE TABLE salary_grades (grade TEXT PRIMARY KEY, min_salary INTEGER, max_salary INTEGER);
INSERT INTO salary_grades VALUES
    ('G1', 0, 74999), ('G2', 75000, 99999), ('G3', 100000, 139999), ('G4', 140000, 999999);
"""


@topic(G, "inner-join", "Joins & INNER JOIN", "arrows-join")
def _():
    yield lead("A join combines rows from two tables by matching a condition — usually a foreign key equal to a primary key. `INNER JOIN` keeps only the rows that match on both sides.")
    yield section("Why joins exist", "sitemap")
    yield p("Normalised tables store each fact once: an employee row holds `dept_id = 1`, not the text *Engineering, Bengaluru*. A join puts the pieces back together at query time.")
    yield table(
        ["Join", "Returns"],
        ["`INNER JOIN`", "Only matching pairs"],
        ["`LEFT [OUTER] JOIN`", "All left rows + matches (`NULL`s where none)"],
        ["`RIGHT [OUTER] JOIN`", "All right rows + matches"],
        ["`FULL [OUTER] JOIN`", "All rows from both sides"],
        ["`CROSS JOIN`", "Every combination (Cartesian product)"],
        ["Self join", "A table joined to itself (hierarchies, comparisons)"],
    )
    yield section("INNER JOIN", "arrows-join")
    yield sql('''
        SELECT e.name, d.name AS department, d.location
        FROM employees e
        INNER JOIN departments d ON d.dept_id = e.dept_id
        ORDER BY e.emp_id;
    ''', out='''
        name   | department  | location
        -------+-------------+----------
        Asha   | Engineering | Bengaluru
        Ravi   | Engineering | Bengaluru
        Meera  | Engineering | Bengaluru
        Karan  | Engineering | Bengaluru
        Priya  | Sales       | Mumbai
        Arjun  | Sales       | Mumbai
        Neha   | Sales       | Mumbai
        Vikram | HR          | Hyderabad
        Sara   | HR          | Hyderabad
    ''')
    yield p("10 employees, but only 9 rows: **Dev** (`dept_id` `NULL`) matches no department, and **Marketing** matches no employee — an inner join drops both. `JOIN` alone means `INNER JOIN`.")
    yield section("How a join is evaluated (conceptually)", "cpu")
    yield steps(
        ("Pair up", "Take every combination of a row from the left table with a row from the right table."),
        ("Keep matches", "Keep only pairs for which the `ON` condition is true."),
        ("Continue", "Further joins, `WHERE`, `GROUP BY`… work on this combined row set."),
    )
    yield note("That is only the *meaning*. Physically the optimizer uses a **nested-loop** join (with an index on the inner side), a **hash join** (build a hash table on the smaller side) or a **merge join** (both inputs sorted on the key).")
    yield section("Joining several tables", "stack-2")
    yield sql('''
        -- what did each customer buy? (customers → orders → order_items → products)
        SELECT c.name AS customer, o.order_id, p.name AS product, oi.quantity
        FROM customers c
        JOIN orders o       ON o.customer_id = c.customer_id
        JOIN order_items oi ON oi.order_id   = o.order_id
        JOIN products p     ON p.product_id  = oi.product_id
        WHERE o.status = 'delivered'
        ORDER BY o.order_id, p.name;
    ''', out='''
        customer | order_id | product    | quantity
        ---------+----------+------------+---------
        Ananya   | 101      | Headphones | 1
        Ananya   | 101      | Laptop     | 1
        Rahul    | 102      | Chair      | 2
        Rahul    | 102      | Pen        | 10
        Ananya   | 103      | Notebook   | 5
        Ananya   | 103      | Pen        | 5
        Rahul    | 106      | Laptop     | 1
    ''')
    yield section("ON vs USING vs NATURAL", "link")
    yield sql('''
        -- USING: the column has the same name on both sides; it appears once in the output
        SELECT order_id, customer_id, name, status
        FROM orders JOIN customers USING (customer_id)
        WHERE order_id <= 102
        ORDER BY order_id;
    ''', out='''
        order_id | customer_id | name   | status
        ---------+-------------+--------+----------
        101      | 1           | Ananya | delivered
        102      | 2           | Rahul  | delivered
    ''')
    yield warn("`NATURAL JOIN` joins on *every* column with the same name. `employees NATURAL JOIN departments` would match on both `dept_id` **and** `name` (employee name = department name) and return nothing. Avoid it — spell out the condition.")
    yield section("Join condition vs filter", "filter")
    yield p("For an inner join, a condition in `ON` or in `WHERE` gives the same result. Convention: relationships in `ON`, row filters in `WHERE`. For **outer** joins the placement changes the result — see the next topic.")
    yield warn("Forgetting the join condition (old comma syntax `FROM a, b` with no `WHERE`) creates a Cartesian product — 10 employees × 4 departments = 40 rows of nonsense. Explicit `JOIN … ON` makes the omission obvious.")
    yield qa("What is the difference between JOIN and INNER JOIN?",
             "None — `INNER` is optional. `JOIN … ON …` is an inner join.")
    yield qa("Can you join on columns that are not keys?",
             "Yes; any boolean condition works (`ON a.city = b.city`, ranges, inequalities). Joins on unindexed or non-unique columns can be slow or multiply rows, so know the cardinality of both sides.")


@topic(G, "outer-joins", "LEFT, RIGHT & FULL OUTER JOIN", "arrows-join-2")
def _():
    yield lead("Outer joins keep rows that have **no match**, filling the missing side with `NULL`s. Use them whenever “no related rows” is a valid answer.")
    yield section("LEFT JOIN", "arrow-bar-left")
    yield sql('''
        SELECT d.name AS department, e.name AS employee
        FROM departments d
        LEFT JOIN employees e ON e.dept_id = d.dept_id
        ORDER BY d.dept_id, e.name;
    ''', out='''
        department  | employee
        ------------+---------
        Engineering | Asha
        Engineering | Karan
        Engineering | Meera
        Engineering | Ravi
        Sales       | Arjun
        Sales       | Neha
        Sales       | Priya
        HR          | Sara
        HR          | Vikram
        Marketing   | NULL
    ''')
    yield p("Marketing appears with a `NULL` employee: every left row survives. Counting per department must count a *column from the right side*:")
    yield sql('''
        SELECT d.name, COUNT(e.emp_id) AS headcount, COUNT(*) AS wrong_count
        FROM departments d
        LEFT JOIN employees e ON e.dept_id = d.dept_id
        GROUP BY d.dept_id, d.name
        ORDER BY d.dept_id;
    ''', out='''
        name        | headcount | wrong_count
        ------------+-----------+------------
        Engineering | 4         | 4
        Sales       | 3         | 3
        HR          | 2         | 2
        Marketing   | 0         | 1
    ''')
    yield warn("`COUNT(*)` counts the padded row, so Marketing shows 1. `COUNT(e.emp_id)` skips the `NULL` and correctly shows 0.")
    yield section("RIGHT and FULL OUTER JOIN", "arrows-horizontal")
    yield p("`A RIGHT JOIN B` is `B LEFT JOIN A`. `FULL OUTER JOIN` keeps unmatched rows from **both** sides. SQLite supports both since 3.39 (2022); MySQL has **no** `FULL OUTER JOIN`.")
    yield sql('''
        SELECT e.name AS employee, d.name AS department
        FROM employees e
        FULL OUTER JOIN departments d ON d.dept_id = e.dept_id
        ORDER BY d.dept_id NULLS LAST, e.emp_id;
    ''', out='''
        employee | department
        ---------+------------
        Asha     | Engineering
        Ravi     | Engineering
        Meera    | Engineering
        Karan    | Engineering
        Priya    | Sales
        Arjun    | Sales
        Neha     | Sales
        Vikram   | HR
        Sara     | HR
        NULL     | Marketing
        Dev      | NULL
    ''')
    yield sql('''
        -- MySQL workaround for FULL OUTER JOIN: LEFT JOIN ∪ the right-only rows
        SELECT e.name AS employee, d.name AS department
        FROM employees e LEFT JOIN departments d ON d.dept_id = e.dept_id
        UNION ALL
        SELECT NULL, d.name
        FROM departments d
        WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.dept_id = d.dept_id)
        ORDER BY department, employee;
    ''', out='''
        employee | department
        ---------+------------
        Dev      | NULL
        Asha     | Engineering
        Karan    | Engineering
        Meera    | Engineering
        Ravi     | Engineering
        Sara     | HR
        Vikram   | HR
        NULL     | Marketing
        Arjun    | Sales
        Neha     | Sales
        Priya    | Sales
    ''')
    yield section("ON vs WHERE in an outer join", "alert-triangle")
    yield p("*List every customer with their delivered orders.* The filter on the right table must go in `ON` — in `WHERE` it removes the `NULL` rows and silently turns the query into an inner join.")
    yield sql('''
        -- filter in ON: all 5 customers kept
        SELECT c.name, o.order_id
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id AND o.status = 'delivered'
        ORDER BY c.customer_id, o.order_id;
    ''', out='''
        name   | order_id
        -------+---------
        Ananya | 101
        Ananya | 103
        Rahul  | 102
        Rahul  | 106
        Sneha  | NULL
        Imran  | NULL
        Kavya  | NULL
    ''')
    yield sql('''
        -- filter in WHERE: Sneha, Imran and Kavya disappear
        SELECT c.name, o.order_id
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.status = 'delivered'
        ORDER BY c.customer_id, o.order_id;
    ''', out='''
        name   | order_id
        -------+---------
        Ananya | 101
        Ananya | 103
        Rahul  | 102
        Rahul  | 106
    ''')
    yield note("Rule: conditions on the **optional** (right) side of a `LEFT JOIN` go in `ON`; conditions on the **preserved** (left) side go in `WHERE`. The exception is deliberately testing for `NULL` (`WHERE o.order_id IS NULL`), which finds non-matching rows — an anti-join.")
    yield qa("What is the difference between LEFT JOIN and INNER JOIN?",
             "`INNER JOIN` returns only rows with a match on both sides. `LEFT JOIN` returns every row of the left table, with the right table's columns `NULL` where there is no match. The row count of a left join is always ≥ the left table's count (more if one left row matches several right rows).")
    yield qa("How do you emulate FULL OUTER JOIN in MySQL?",
             "`LEFT JOIN` the two tables, then `UNION ALL` the rows of the right table that have no match (`RIGHT JOIN … WHERE left.key IS NULL` or `NOT EXISTS`). Plain `UNION` of a `LEFT` and a `RIGHT` join also works but de-duplicates, which can drop genuine duplicate rows.")


@topic(G, "cross-self-join", "CROSS JOIN & SELF JOIN", "arrows-cross")
def _():
    yield lead("A cross join pairs every row with every row; a self join matches a table with itself. Both are ordinary joins used in less ordinary ways.")
    yield section("CROSS JOIN: every combination", "grid-dots")
    yield sql('''
        CREATE TABLE sizes  (size TEXT);
        CREATE TABLE colors (color TEXT);
        INSERT INTO sizes  VALUES ('S'), ('M'), ('L');
        INSERT INTO colors VALUES ('Black'), ('White');

        SELECT s.size, c.color
        FROM sizes s CROSS JOIN colors c
        ORDER BY c.color, s.size;
    ''', out='''
        size | color
        -----+------
        L    | Black
        M    | Black
        S    | Black
        L    | White
        M    | White
        S    | White
    ''', setup="")
    yield p("3 × 2 = 6 rows. Real uses: generating all product variants, a calendar × store grid to report zero-sales days, or combining a single-row settings table with every row.")
    yield sql('''
        -- every department × every month of Q1, so empty months still appear
        WITH months(m) AS (VALUES ('2024-01'), ('2024-02'), ('2024-03'))
        SELECT d.name, m.m AS month
        FROM departments d CROSS JOIN months m
        WHERE d.dept_id <= 2
        ORDER BY d.name, month;
    ''', out='''
        name        | month
        ------------+--------
        Engineering | 2024-01
        Engineering | 2024-02
        Engineering | 2024-03
        Sales       | 2024-01
        Sales       | 2024-02
        Sales       | 2024-03
    ''')
    yield warn("Cross joins grow multiplicatively: 10 000 × 10 000 rows = 100 million. An accidental one (missing join condition) is a classic cause of runaway queries.")
    yield section("SELF JOIN: employees and their managers", "hierarchy")
    yield p("`employees.manager_id` points at another row of `employees`. Join the table to itself under two aliases — one playing *employee*, one playing *manager*.")
    yield sql('''
        SELECT e.name AS employee, m.name AS manager
        FROM employees e
        LEFT JOIN employees m ON m.emp_id = e.manager_id
        ORDER BY e.emp_id;
    ''', out='''
        employee | manager
        ---------+--------
        Asha     | NULL
        Ravi     | Asha
        Meera    | Ravi
        Karan    | Ravi
        Priya    | Asha
        Arjun    | Priya
        Neha     | Priya
        Vikram   | Asha
        Sara     | Vikram
        Dev      | Asha
    ''')
    yield p("`LEFT JOIN` keeps Asha, who has no manager. With an inner join she would vanish.")
    yield sql('''
        -- employees who earn more than their manager (a top interview question)
        SELECT e.name AS employee, e.salary, m.name AS manager, m.salary AS manager_salary
        FROM employees e
        JOIN employees m ON m.emp_id = e.manager_id
        WHERE e.salary > m.salary;
    ''', out='''
        employee | salary | manager | manager_salary
        ---------+--------+---------+---------------
        Sara     | 85000  | Vikram  | 80000
    ''')
    yield section("Self join to compare rows: pairs", "arrows-exchange")
    yield sql('''
        -- pairs of employees in the same department (each pair once)
        SELECT a.name AS first, b.name AS second, a.dept_id
        FROM employees a
        JOIN employees b ON b.dept_id = a.dept_id AND a.emp_id < b.emp_id
        WHERE a.dept_id IN (2, 3)
        ORDER BY a.dept_id, a.emp_id, b.emp_id;
    ''', out='''
        first  | second | dept_id
        -------+--------+--------
        Priya  | Arjun  | 2
        Priya  | Neha   | 2
        Arjun  | Neha   | 2
        Vikram | Sara   | 3
    ''')
    yield note("`a.emp_id < b.emp_id` removes self-pairs (Priya–Priya) and mirrored duplicates (Priya–Arjun and Arjun–Priya). `<>` would keep both mirrors.")
    yield qa("What is a self join and when is it used?",
             "A join of a table with itself using two aliases. Used for hierarchical data stored as a parent pointer (employee → manager, category → parent category), for comparing rows within the same table (pairs, duplicates, consecutive events), and for “earns more than manager”-style questions.")


@topic(G, "non-equi-joins", "Non-Equi Joins", "math-greater")
def _():
    yield lead("A join condition doesn't have to be `=`. Ranges, inequalities and `BETWEEN` joins match rows by *intervals* — salary bands, price tiers, date validity periods.")
    yield sql(GRADES.strip() + '''

        SELECT * FROM salary_grades ORDER BY grade;
    ''', out='''
        grade | min_salary | max_salary
        ------+------------+-----------
        G1    | 0          | 74999
        G2    | 75000      | 99999
        G3    | 100000     | 139999
        G4    | 140000     | 999999
    ''', setup="")
    yield section("Joining on a range", "arrows-horizontal")
    yield sql('''
        SELECT e.name, e.salary, g.grade
        FROM employees e
        JOIN salary_grades g ON e.salary BETWEEN g.min_salary AND g.max_salary
        ORDER BY e.salary DESC, e.emp_id;
    ''', out='''
        name   | salary | grade
        -------+--------+------
        Asha   | 150000 | G4
        Ravi   | 120000 | G3
        Priya  | 110000 | G3
        Meera  | 95000  | G2
        Karan  | 95000  | G2
        Sara   | 85000  | G2
        Vikram | 80000  | G2
        Neha   | 72000  | G1
        Arjun  | 70000  | G1
        Dev    | 60000  | G1
    ''', setup=SCHEMA + GRADES)
    yield section("Inequality joins: running comparisons", "chart-line")
    yield sql('''
        -- for each employee, how many colleagues earn strictly more (their 0-based rank)
        SELECT e.name, e.salary, COUNT(h.emp_id) AS earn_more
        FROM employees e
        LEFT JOIN employees h ON h.salary > e.salary
        GROUP BY e.emp_id, e.name, e.salary
        ORDER BY earn_more, e.emp_id
        LIMIT 5;
    ''', out='''
        name  | salary | earn_more
        ------+--------+----------
        Asha  | 150000 | 0
        Ravi  | 120000 | 1
        Priya | 110000 | 2
        Meera | 95000  | 3
        Karan | 95000  | 3
    ''')
    yield sql('''
        -- repeat orders: placed within 30 days after an earlier order by the same customer
        SELECT a.customer_id, a.order_id AS earlier, b.order_id AS later,
               julianday(b.order_date) - julianday(a.order_date) AS gap_days
        FROM orders a
        JOIN orders b ON b.customer_id = a.customer_id
                     AND b.order_date >  a.order_date
                     AND b.order_date <= date(a.order_date, '+30 days')
        ORDER BY a.customer_id, a.order_id;
    ''', out='''
        customer_id | earlier | later | gap_days
        ------------+---------+-------+---------
        1           | 101     | 103   | 29.0
        3           | 104     | 107   | 23.0
    ''')
    yield warn("Range and inequality joins can explode in size (O(n²) pairs) and can't use hash joins. Make sure ranges don't overlap (or you get duplicates), index the range columns, and prefer window functions for ranking/running questions.")
    yield qa("What is a non-equi join?",
             "A join whose condition uses an operator other than `=` — `BETWEEN`, `<`, `>=`, `<>`. Typical: mapping a value to a band (`salary BETWEEN min AND max`), finding overlapping date ranges, or pairing events that occurred within some interval.")


@topic(G, "semi-anti-joins", "Semi & Anti Joins (EXISTS, IN, NOT EXISTS)", "filter-check")
def _():
    yield lead("A **semi join** keeps rows that *have* a match; an **anti join** keeps rows that have *no* match. Neither returns columns from the other table, and neither duplicates rows.")
    yield section("Semi join: customers who ordered", "user-check")
    yield sql('''
        SELECT c.name FROM customers c
        WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
        ORDER BY c.name;

        SELECT c.name FROM customers c
        WHERE c.customer_id IN (SELECT customer_id FROM orders)
        ORDER BY c.name;
    ''', out='''
        name
        ------
        Ananya
        Imran
        Rahul
        Sneha

        name
        ------
        Ananya
        Imran
        Rahul
        Sneha
    ''')
    yield p("Compare with a plain join, which returns a customer once **per order**:")
    yield sql('''
        SELECT c.name FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        ORDER BY c.name;
    ''', out='''
        name
        ------
        Ananya
        Ananya
        Ananya
        Imran
        Rahul
        Rahul
        Sneha
        Sneha
    ''')
    yield note("`EXISTS` stops at the first match and never multiplies rows. Using `JOIN` + `DISTINCT` to get the same list does more work and is a code smell.")
    yield section("Anti join: customers who never ordered", "user-x")
    yield sql('''
        -- 1. NOT EXISTS (recommended)
        SELECT c.name FROM customers c
        WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

        -- 2. LEFT JOIN … IS NULL
        SELECT c.name FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.order_id IS NULL;

        -- 3. NOT IN (only safe if the subquery can never return NULL)
        SELECT name FROM customers
        WHERE customer_id NOT IN (SELECT customer_id FROM orders);
    ''', out='''
        name
        -----
        Kavya

        name
        -----
        Kavya

        name
        -----
        Kavya
    ''')
    yield sql('''
        -- products never sold
        SELECT p.name FROM products p
        WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id);
    ''', out='''
        name
        -------
        Monitor
    ''')
    yield section("The NOT IN + NULL trap, for real", "alert-triangle")
    yield sql('''
        -- departments that no employee belongs to…
        SELECT name FROM departments
        WHERE dept_id NOT IN (SELECT dept_id FROM employees);          -- Dev's NULL dept_id → empty!

        SELECT name FROM departments d
        WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.dept_id = d.dept_id);
    ''', out='''
        name
        ----

        name
        ---------
        Marketing
    ''')
    yield warn("Marketing should be returned, but `NOT IN` returned nothing because the subquery contains a `NULL`. `NOT EXISTS` is immune. If you must use `NOT IN`, add `WHERE dept_id IS NOT NULL` inside the subquery.")
    yield table(
        ["Form", "Handles NULL", "Duplicates", "Notes"],
        ["`EXISTS` / `NOT EXISTS`", "Yes", "Never", "Clearest intent; optimizers turn it into a semi/anti join"],
        ["`IN (subquery)`", "Yes", "Never", "Fine for semi joins"],
        ["`NOT IN (subquery)`", "**No**", "Never", "Returns nothing if the subquery has a `NULL`"],
        ["`LEFT JOIN … IS NULL`", "Yes", "Never (anti)", "Common, portable; test a non-nullable column"],
        ["`JOIN` + `DISTINCT`", "Yes", "Removed afterwards", "Extra work; avoid for existence checks"],
    )
    yield qa("EXISTS vs IN — which is faster?",
             "Modern optimizers (PostgreSQL, SQL Server, Oracle, MySQL 8) usually rewrite both into the same semi join, so pick the clearest. The real difference is `NOT IN` vs `NOT EXISTS`: `NOT IN` gives wrong (empty) results when the subquery returns a `NULL`, so prefer `NOT EXISTS` for anti joins.")
    yield qa("Find customers who have never placed an order.",
             "`SELECT c.* FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);` — or `LEFT JOIN orders o ON … WHERE o.order_id IS NULL`.")


@topic(G, "set-operations", "UNION, INTERSECT & EXCEPT", "layers-intersect")
def _():
    yield lead("Set operators combine the **results of two queries** vertically (more rows), unlike joins which combine tables horizontally (more columns).")
    yield table(
        ["Operator", "Returns", "Duplicates"],
        ["`UNION`", "Rows in either query", "Removed"],
        ["`UNION ALL`", "Rows in either query", "Kept (faster — no de-dup step)"],
        ["`INTERSECT`", "Rows in both queries", "Removed"],
        ["`EXCEPT` (`MINUS` in Oracle)", "Rows in the first but not the second", "Removed"],
    )
    yield p("Rules: both queries must return the **same number of columns** with compatible types; column names come from the first query; one `ORDER BY` at the very end sorts the combined result.")
    yield section("UNION vs UNION ALL", "layers-union")
    yield sql('''
        -- cities we have customers or offices in
        SELECT city FROM customers WHERE city IS NOT NULL
        UNION
        SELECT location FROM departments
        ORDER BY 1;
    ''', out='''
        city
        ---------
        Bengaluru
        Delhi
        Hyderabad
        Mumbai
        Pune
    ''')
    yield sql('''
        SELECT city FROM customers WHERE city IS NOT NULL
        UNION ALL
        SELECT location FROM departments
        ORDER BY 1;
    ''', out='''
        city
        ---------
        Bengaluru
        Bengaluru
        Delhi
        Delhi
        Hyderabad
        Mumbai
        Mumbai
        Pune
    ''')
    yield good("Use `UNION ALL` unless you actually need duplicates removed — `UNION` has to sort or hash the whole result to de-duplicate.")
    yield section("INTERSECT and EXCEPT", "layers-intersect-2")
    yield sql('''
        -- cities with both a customer and an office
        SELECT city FROM customers
        INTERSECT
        SELECT location FROM departments
        ORDER BY 1;

        -- office cities with no customers
        SELECT location FROM departments
        EXCEPT
        SELECT city FROM customers
        ORDER BY 1;
    ''', out='''
        city
        ---------
        Bengaluru
        Mumbai

        location
        ---------
        Hyderabad
        Pune
    ''')
    yield note("Set operators compare `NULL`s as equal (unlike `=`), so `EXCEPT` and `INTERSECT` are also a null-safe way to diff two result sets. MySQL supports `INTERSECT`/`EXCEPT` only since 8.0.31; Oracle calls `EXCEPT` `MINUS`.")
    yield section("Labelled union: combining different sources", "tags")
    yield sql('''
        SELECT 'employee' AS kind, name, dept_id AS ref FROM employees WHERE salary >= 110000
        UNION ALL
        SELECT 'customer', name, customer_id FROM customers WHERE city = 'Delhi'
        ORDER BY kind, name;
    ''', out='''
        kind     | name  | ref
        ---------+-------+----
        customer | Imran | 4
        customer | Rahul | 2
        employee | Asha  | 1
        employee | Priya | 2
        employee | Ravi  | 1
    ''')
    yield section("Comparing two tables", "git-compare")
    yield sql('''
        CREATE TABLE prices_old (sku TEXT, price INTEGER);
        CREATE TABLE prices_new (sku TEXT, price INTEGER);
        INSERT INTO prices_old VALUES ('A', 10), ('B', 20), ('C', 30);
        INSERT INTO prices_new VALUES ('A', 10), ('B', 25), ('D', 40);

        SELECT 'removed/changed' AS diff, * FROM (SELECT * FROM prices_old EXCEPT SELECT * FROM prices_new)
        UNION ALL
        SELECT 'added/changed', * FROM (SELECT * FROM prices_new EXCEPT SELECT * FROM prices_old)
        ORDER BY sku, diff;
    ''', out='''
        diff            | sku | price
        ----------------+-----+------
        added/changed   | B   | 25
        removed/changed | B   | 20
        removed/changed | C   | 30
        added/changed   | D   | 40
    ''', setup="")
    yield qa("What is the difference between UNION and UNION ALL?",
             "`UNION` removes duplicate rows from the combined result (extra sort/hash work); `UNION ALL` keeps every row and is faster. Use `UNION ALL` when the inputs can't overlap or duplicates are wanted.")
    yield qa("What is the difference between UNION and JOIN?",
             "`UNION` stacks the rows of two compatible queries (same columns) — the result has more rows. `JOIN` matches rows of two tables on a condition — the result has more columns.")
