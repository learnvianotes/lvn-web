from kit import *
from sample_db import sql, dialect, SCHEMA

G = "Subqueries, CTEs & Windows"

SALES = """
CREATE TABLE daily_sales (day TEXT PRIMARY KEY, amount INTEGER);
INSERT INTO daily_sales VALUES
    ('2024-03-01', 120), ('2024-03-02', 80), ('2024-03-03', 150),
    ('2024-03-04', 90),  ('2024-03-05', 200), ('2024-03-06', 60);
"""


@topic(G, "subqueries", "Subqueries", "box-multiple")
def _():
    yield lead("A subquery is a `SELECT` nested inside another statement. Its result is used as a single value, a list, or a whole table, depending on where it sits.")
    yield table(
        ["Kind", "Returns", "Used in", "Example"],
        ["Scalar", "One row, one column", "`SELECT`, `WHERE`, `SET`", "`salary > (SELECT AVG(salary) FROM employees)`"],
        ["Row / list", "One column, many rows", "`IN`, `ANY`, `ALL`", "`dept_id IN (SELECT …)`"],
        ["Table (derived table)", "Many rows and columns", "`FROM`, `JOIN`", "`FROM (SELECT …) AS t`"],
        ["Correlated", "Re-evaluated per outer row", "`WHERE`, `SELECT`", "next topic"],
    )
    yield section("Scalar subquery", "number-1")
    yield sql('''
        -- employees paid above the company average (93700)
        SELECT name, salary
        FROM employees
        WHERE salary > (SELECT AVG(salary) FROM employees)
        ORDER BY salary DESC, emp_id;
    ''', out='''
        name  | salary
        ------+-------
        Asha  | 150000
        Ravi  | 120000
        Priya | 110000
        Meera | 95000
        Karan | 95000
    ''')
    yield sql('''
        -- scalar subquery in the SELECT list
        SELECT name, salary,
               salary - (SELECT AVG(salary) FROM employees) AS diff_from_avg
        FROM employees
        WHERE dept_id = 2
        ORDER BY emp_id;
    ''', out='''
        name  | salary | diff_from_avg
        ------+--------+--------------
        Priya | 110000 | 16300.0
        Arjun | 70000  | -23700.0
        Neha  | 72000  | -21700.0
    ''')
    yield warn("A scalar subquery must return at most one row. PostgreSQL, SQL Server and Oracle raise an error if it returns more; SQLite and MySQL (in some contexts) silently take the first. Zero rows give `NULL`.")
    yield section("List subquery: IN, ANY, ALL", "list")
    yield sql('''
        -- employees working in a department located in Mumbai or Hyderabad
        SELECT name FROM employees
        WHERE dept_id IN (SELECT dept_id FROM departments WHERE location IN ('Mumbai', 'Hyderabad'))
        ORDER BY emp_id;
    ''', out='''
        name
        ------
        Priya
        Arjun
        Neha
        Vikram
        Sara
    ''')
    yield dialect('''
        -- earn more than EVERY Sales employee / more than ANY Sales employee
        SELECT name FROM employees WHERE salary > ALL (SELECT salary FROM employees WHERE dept_id = 2);
        SELECT name FROM employees WHERE salary > ANY (SELECT salary FROM employees WHERE dept_id = 2);
    ''', "PostgreSQL / MySQL / SQL Server / Oracle")
    yield p("SQLite has no `ANY`/`ALL`; rewrite with aggregates — `> ALL (…)` is `> (SELECT MAX(…))` and `> ANY (…)` is `> (SELECT MIN(…))` (careful: they differ when the subquery is empty or contains `NULL`s).")
    yield sql('''
        SELECT name, salary FROM employees
        WHERE salary > (SELECT MAX(salary) FROM employees WHERE dept_id = 2)
        ORDER BY emp_id;
    ''', out='''
        name | salary
        -----+-------
        Asha | 150000
        Ravi | 120000
    ''')
    yield section("Derived table (subquery in FROM)", "table")
    yield sql('''
        -- average of per-department averages (not the same as the overall average!)
        SELECT ROUND(AVG(dept_avg)) AS avg_of_dept_avgs
        FROM (
            SELECT dept_id, AVG(salary) AS dept_avg
            FROM employees
            WHERE dept_id IS NOT NULL
            GROUP BY dept_id
        ) AS per_dept;
    ''', out='''
        avg_of_dept_avgs
        ----------------
        93833.0
    ''')
    yield sql('''
        -- join a table to an aggregated subquery: each employee vs their department average
        SELECT e.name, e.dept_id, e.salary, ROUND(d.avg_sal) AS dept_avg
        FROM employees e
        JOIN (SELECT dept_id, AVG(salary) AS avg_sal FROM employees GROUP BY dept_id) d
          ON d.dept_id = e.dept_id
        WHERE e.salary > d.avg_sal
        ORDER BY e.emp_id;
    ''', out='''
        name  | dept_id | salary | dept_avg
        ------+---------+--------+---------
        Asha  | 1       | 150000 | 115000.0
        Ravi  | 1       | 120000 | 115000.0
        Priya | 2       | 110000 | 84000.0
        Sara  | 3       | 85000  | 82500.0
    ''')
    yield note("A derived table needs an alias in most engines (`AS per_dept`). When a subquery grows or is used twice, promote it to a **CTE** for readability.")
    yield qa("What is the difference between a subquery and a join?",
             "A join combines columns from both tables into the result; a subquery computes a value/list/table used by the outer query. Many subqueries (`IN`, `EXISTS`) can be rewritten as joins and optimizers often do it automatically. Use a join when you need columns from both sides, a subquery for filtering or pre-aggregation.")


@topic(G, "correlated-subqueries", "Correlated Subqueries", "arrows-right-left")
def _():
    yield lead("A correlated subquery refers to a column of the **outer** query, so it is logically re-evaluated for every outer row — like a nested loop.")
    yield sql('''
        -- employees who earn more than the average of THEIR OWN department
        SELECT e.name, e.dept_id, e.salary
        FROM employees e
        WHERE e.salary > (
            SELECT AVG(i.salary)
            FROM employees i
            WHERE i.dept_id = e.dept_id          -- ← correlation: uses the outer row
        )
        ORDER BY e.emp_id;
    ''', out='''
        name  | dept_id | salary
        ------+---------+-------
        Asha  | 1       | 150000
        Ravi  | 1       | 120000
        Priya | 2       | 110000
        Sara  | 3       | 85000
    ''')
    yield steps(
        ("Take an outer row", "e = Asha, dept 1."),
        ("Run the inner query for it", "Average salary of dept 1 = 115000."),
        ("Test", "150000 > 115000 → keep Asha. Repeat for the next row."),
    )
    yield section("Correlated subquery in SELECT", "columns")
    yield sql('''
        SELECT c.name,
               (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) AS orders,
               (SELECT MAX(order_date) FROM orders o WHERE o.customer_id = c.customer_id) AS last_order
        FROM customers c
        ORDER BY c.customer_id;
    ''', out='''
        name   | orders | last_order
        -------+--------+-----------
        Ananya | 3      | 2024-03-15
        Rahul  | 2      | 2024-03-01
        Sneha  | 2      | 2024-03-08
        Imran  | 1      | 2024-02-20
        Kavya  | 0      | NULL
    ''')
    yield section("EXISTS is always correlated", "checkbox")
    yield sql('''
        -- customers who bought something from the Furniture category
        SELECT c.name
        FROM customers c
        WHERE EXISTS (
            SELECT 1
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.order_id
            JOIN products p     ON p.product_id = oi.product_id
            WHERE o.customer_id = c.customer_id AND p.category = 'Furniture'
        )
        ORDER BY c.name;
    ''', out='''
        name
        ------
        Ananya
        Rahul
        Sneha
    ''')
    yield section("Correlated UPDATE", "edit")
    yield sql('''
        ALTER TABLE customers ADD COLUMN lifetime_value INTEGER DEFAULT 0;

        UPDATE customers
        SET lifetime_value = COALESCE((
            SELECT SUM(oi.quantity * oi.unit_price)
            FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
            WHERE o.customer_id = customers.customer_id AND o.status <> 'cancelled'
        ), 0);

        SELECT name, lifetime_value FROM customers ORDER BY lifetime_value DESC, customer_id;
    ''', out='''
        name   | lifetime_value
        -------+---------------
        Ananya | 68400
        Rahul  | 61200
        Sneha  | 13700
        Imran  | 0
        Kavya  | 0
    ''')
    yield warn("Correlated subqueries can be O(n × m). Optimizers often decorrelate them into joins, but not always — for large tables compare against a join to a pre-aggregated derived table/CTE, or a window function (`AVG(salary) OVER (PARTITION BY dept_id)`).", "Performance")
    yield qa("What is a correlated subquery?",
             "A subquery that references columns of the outer query, so its result depends on the current outer row and is (logically) evaluated once per row. Example: `WHERE salary > (SELECT AVG(salary) FROM employees i WHERE i.dept_id = e.dept_id)`. A non-correlated subquery runs once, independently.")


@topic(G, "ctes", "Common Table Expressions (WITH)", "stack-push")
def _():
    yield lead("A CTE names a subquery at the top of a statement with `WITH name AS (…)`. Queries read top-down like a pipeline instead of inside-out.")
    yield section("Syntax", "code")
    yield sql('''
        WITH dept_stats AS (
            SELECT dept_id, COUNT(*) AS staff, AVG(salary) AS avg_sal
            FROM employees
            WHERE dept_id IS NOT NULL
            GROUP BY dept_id
        )
        SELECT d.name, s.staff, ROUND(s.avg_sal) AS avg_sal
        FROM dept_stats s
        JOIN departments d ON d.dept_id = s.dept_id
        ORDER BY s.avg_sal DESC;
    ''', out='''
        name        | staff | avg_sal
        ------------+-------+---------
        Engineering | 4     | 115000.0
        Sales       | 3     | 84000.0
        HR          | 2     | 82500.0
    ''')
    yield section("Chaining CTEs", "link")
    yield p("Each CTE can use the ones defined before it. A multi-step report becomes a list of named steps.")
    yield sql('''
        WITH order_totals AS (           -- step 1: value of each valid order
            SELECT o.order_id, o.customer_id, SUM(oi.quantity * oi.unit_price) AS total
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.order_id
            WHERE o.status <> 'cancelled'
            GROUP BY o.order_id, o.customer_id
        ),
        customer_totals AS (             -- step 2: per customer
            SELECT customer_id, COUNT(*) AS orders, SUM(total) AS spent
            FROM order_totals
            GROUP BY customer_id
        ),
        overall AS (                     -- step 3: one number to compare against
            SELECT AVG(spent) AS avg_spent FROM customer_totals
        )
        SELECT c.name, ct.orders, ct.spent,
               CASE WHEN ct.spent > o.avg_spent THEN 'above avg' ELSE 'below avg' END AS segment
        FROM customer_totals ct
        JOIN customers c ON c.customer_id = ct.customer_id
        CROSS JOIN overall o
        ORDER BY ct.spent DESC;
    ''', out='''
        name   | orders | spent | segment
        -------+--------+-------+----------
        Ananya | 3      | 68400 | above avg
        Rahul  | 2      | 61200 | above avg
        Sneha  | 2      | 13700 | below avg
    ''')
    yield section("CTE vs subquery vs view vs temp table", "arrows-diff")
    yield table(
        ["", "Scope", "Reusable in the statement", "Stored"],
        ["Derived table (subquery)", "One place in one query", "No — repeat it", "No"],
        ["CTE", "One statement", "Yes — reference by name, many times", "No"],
        ["View", "The database", "Across all queries", "Definition only"],
        ["Temporary table", "Session", "Across statements", "Yes (data, can be indexed)"],
    )
    yield note("Whether a CTE is computed once (**materialised**) or inlined like a subquery depends on the engine. PostgreSQL 12+ inlines by default and lets you force either with `AS MATERIALIZED` / `AS NOT MATERIALIZED`; SQLite accepts the same hints.")
    yield section("CTEs with DML", "edit")
    yield sql('''
        -- give a 5% raise to everyone below their department's average
        WITH below AS (
            SELECT e.emp_id
            FROM employees e
            WHERE e.salary < (SELECT AVG(salary) FROM employees i WHERE i.dept_id = e.dept_id)
        )
        UPDATE employees
        SET salary = salary * 105 / 100
        WHERE emp_id IN (SELECT emp_id FROM below);

        SELECT name, salary FROM employees WHERE emp_id IN (3, 4, 6, 7, 8) ORDER BY emp_id;
    ''', out='''
        name   | salary
        -------+-------
        Meera  | 99750
        Karan  | 99750
        Arjun  | 73500
        Neha   | 75600
        Vikram | 84000
    ''')
    yield qa("What is a CTE and why use it?",
             "A Common Table Expression is a named, temporary result defined with `WITH` and visible only to the statement that follows. It improves readability (step-by-step logic), lets you reference the same intermediate result several times, and is required for recursive queries.")
    yield qa("Is a CTE faster than a subquery?",
             "Usually neither — most optimizers treat a non-recursive CTE like an inline subquery. It can be faster if it is materialised once and referenced many times, or slower if materialisation blocks predicate push-down. Choose it for clarity and check the plan when performance matters.")


@topic(G, "recursive-ctes", "Recursive CTEs", "hierarchy-2")
def _():
    yield lead("`WITH RECURSIVE` lets a CTE refer to itself — the tool for hierarchies (org charts, categories, bills of materials), graphs and generated series.")
    yield section("How it works", "repeat")
    yield steps(
        ("Anchor member", "A normal `SELECT` that produces the starting rows."),
        ("`UNION ALL`", "Separates the anchor from the recursive part."),
        ("Recursive member", "A `SELECT` that joins the CTE's **previous** rows to produce the next rows."),
        ("Stop", "Recursion ends when the recursive member returns no new rows."),
    )
    yield section("Generating a series", "list-numbers")
    yield sql('''
        WITH RECURSIVE n(x) AS (
            SELECT 1                    -- anchor
            UNION ALL
            SELECT x + 1 FROM n         -- recursive step
            WHERE x < 5                 -- termination
        )
        SELECT x, x * x AS square FROM n;
    ''', out='''
        x | square
        --+-------
        1 | 1
        2 | 4
        3 | 9
        4 | 16
        5 | 25
    ''', setup="")
    yield sql('''
        -- a month calendar Jan–Apr 2024, then orders per month including empty months
        WITH RECURSIVE months(m) AS (
            SELECT '2024-01-01'
            UNION ALL
            SELECT date(m, '+1 month') FROM months WHERE m < '2024-04-01'
        )
        SELECT strftime('%Y-%m', m) AS month, COUNT(o.order_id) AS orders
        FROM months
        LEFT JOIN orders o ON strftime('%Y-%m', o.order_date) = strftime('%Y-%m', m)
        GROUP BY m
        ORDER BY m;
    ''', out='''
        month   | orders
        --------+-------
        2024-01 | 2
        2024-02 | 3
        2024-03 | 3
        2024-04 | 0
    ''')
    yield section("Walking a hierarchy: the org chart", "hierarchy")
    yield sql('''
        WITH RECURSIVE org(emp_id, name, manager_id, level, path) AS (
            SELECT emp_id, name, manager_id, 0, name
            FROM employees
            WHERE manager_id IS NULL                            -- start at the top (Asha)
            UNION ALL
            SELECT e.emp_id, e.name, e.manager_id, org.level + 1, org.path || ' > ' || e.name
            FROM employees e
            JOIN org ON e.manager_id = org.emp_id               -- children of the previous level
        )
        SELECT substr('            ', 1, level * 2) || name AS org_chart, level, path
        FROM org
        ORDER BY path;
    ''', out='''
        org_chart | level | path
        ----------+-------+---------------------
        Asha      | 0     | Asha
          Dev     | 1     | Asha > Dev
          Priya   | 1     | Asha > Priya
            Arjun | 2     | Asha > Priya > Arjun
            Neha  | 2     | Asha > Priya > Neha
          Ravi    | 1     | Asha > Ravi
            Karan | 2     | Asha > Ravi > Karan
            Meera | 2     | Asha > Ravi > Meera
          Vikram  | 1     | Asha > Vikram
            Sara  | 2     | Asha > Vikram > Sara
    ''')
    yield section("Walking up: all managers of one employee", "arrow-up")
    yield sql('''
        WITH RECURSIVE chain(emp_id, name, manager_id, hops) AS (
            SELECT emp_id, name, manager_id, 0 FROM employees WHERE name = 'Meera'
            UNION ALL
            SELECT m.emp_id, m.name, m.manager_id, c.hops + 1
            FROM employees m
            JOIN chain c ON m.emp_id = c.manager_id
        )
        SELECT hops, name FROM chain ORDER BY hops;
    ''', out='''
        hops | name
        -----+------
        0    | Meera
        1    | Ravi
        2    | Asha
    ''')
    yield sql('''
        -- total salary cost under each manager (all levels), a "subtree sum"
        WITH RECURSIVE reports(boss_id, emp_id) AS (
            SELECT manager_id, emp_id FROM employees WHERE manager_id IS NOT NULL
            UNION ALL
            SELECT r.boss_id, e.emp_id
            FROM reports r JOIN employees e ON e.manager_id = r.emp_id
        )
        SELECT b.name AS manager, COUNT(*) AS total_reports, SUM(e.salary) AS team_cost
        FROM reports r
        JOIN employees b ON b.emp_id = r.boss_id
        JOIN employees e ON e.emp_id = r.emp_id
        GROUP BY b.emp_id, b.name
        ORDER BY total_reports DESC, b.emp_id;
    ''', out='''
        manager | total_reports | team_cost
        --------+---------------+----------
        Asha    | 9             | 787000
        Ravi    | 2             | 190000
        Priya   | 2             | 142000
        Vikram  | 1             | 85000
    ''')
    yield warn("A cycle in the data (A manages B, B manages A) makes the recursion infinite. Guard with a depth limit (`WHERE level < 20`), track visited ids in a path string, or use `UNION` instead of `UNION ALL` (stops when no *new* rows appear). PostgreSQL 14+ has a `CYCLE` clause; SQL Server stops at `MAXRECURSION` (default 100).")
    yield note("Keyword differences: PostgreSQL, MySQL 8 and SQLite require `WITH RECURSIVE`; SQL Server and Oracle use plain `WITH` (Oracle also has the older `CONNECT BY PRIOR`).")
    yield qa("How do you query hierarchical data in SQL?",
             "Store a parent pointer (`manager_id`) and use a recursive CTE: the anchor selects the root(s), the recursive member joins the table to the CTE on `child.parent_id = cte.id`, carrying a `level` and `path`. Alternatives for read-heavy trees: materialised path, nested sets, closure tables, or PostgreSQL's `ltree`.")


@topic(G, "window-functions", "Window Functions: The Basics", "window")
def _():
    yield lead("A window function computes a value **across a set of related rows** — without collapsing them like `GROUP BY` does. Each row keeps its identity and gains an aggregate, a rank or a neighbour's value.")
    yield define("OVER clause", "`f(…) OVER (PARTITION BY … ORDER BY … frame)` — `PARTITION BY` splits rows into independent groups, `ORDER BY` orders rows inside each partition, the frame picks which rows around the current one are included.")
    yield section("GROUP BY vs window", "arrows-diff")
    yield sql('''
        -- GROUP BY: one row per department
        SELECT dept_id, AVG(salary) AS dept_avg
        FROM employees WHERE dept_id IN (2, 3)
        GROUP BY dept_id
        ORDER BY dept_id;

        -- window: every employee kept, department average attached
        SELECT name, dept_id, salary,
               AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg,
               salary - AVG(salary) OVER (PARTITION BY dept_id) AS diff
        FROM employees WHERE dept_id IN (2, 3)
        ORDER BY dept_id, emp_id;
    ''', out='''
        dept_id | dept_avg
        --------+---------
        2       | 84000.0
        3       | 82500.0

        name   | dept_id | salary | dept_avg | diff
        -------+---------+--------+----------+---------
        Priya  | 2       | 110000 | 84000.0  | 26000.0
        Arjun  | 2       | 70000  | 84000.0  | -14000.0
        Neha   | 2       | 72000  | 84000.0  | -12000.0
        Vikram | 3       | 80000  | 82500.0  | -2500.0
        Sara   | 3       | 85000  | 82500.0  | 2500.0
    ''')
    yield section("Aggregates as window functions", "sum")
    yield sql('''
        SELECT name, dept_id, salary,
               SUM(salary)   OVER ()                     AS company_payroll,
               ROUND(100.0 * salary / SUM(salary) OVER (), 1) AS pct_of_company,
               COUNT(*)      OVER (PARTITION BY dept_id) AS dept_size,
               MAX(salary)   OVER (PARTITION BY dept_id) AS dept_max
        FROM employees
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id, salary DESC, emp_id;
    ''', out='''
        name   | dept_id | salary | company_payroll | pct_of_company | dept_size | dept_max
        -------+---------+--------+-----------------+----------------+-----------+---------
        Asha   | 1       | 150000 | 877000          | 17.1           | 4         | 150000
        Ravi   | 1       | 120000 | 877000          | 13.7           | 4         | 150000
        Meera  | 1       | 95000  | 877000          | 10.8           | 4         | 150000
        Karan  | 1       | 95000  | 877000          | 10.8           | 4         | 150000
        Priya  | 2       | 110000 | 877000          | 12.5           | 3         | 110000
        Neha   | 2       | 72000  | 877000          | 8.2            | 3         | 110000
        Arjun  | 2       | 70000  | 877000          | 8.0            | 3         | 110000
        Sara   | 3       | 85000  | 877000          | 9.7            | 2         | 85000
        Vikram | 3       | 80000  | 877000          | 9.1            | 2         | 85000
    ''')
    yield p("`OVER ()` with nothing inside = one window containing all rows (of the result after `WHERE`).")
    yield section("Adding ORDER BY makes it cumulative", "trending-up")
    yield sql('''
        SELECT day, amount,
               SUM(amount) OVER (ORDER BY day)  AS running_total,
               COUNT(*)    OVER (ORDER BY day)  AS days_so_far
        FROM daily_sales
        ORDER BY day;
    ''', out='''
        day        | amount | running_total | days_so_far
        -----------+--------+---------------+------------
        2024-03-01 | 120    | 120           | 1
        2024-03-02 | 80     | 200           | 2
        2024-03-03 | 150    | 350           | 3
        2024-03-04 | 90     | 440           | 4
        2024-03-05 | 200    | 640           | 5
        2024-03-06 | 60     | 700           | 6
    ''', setup=SALES)
    yield note("With `ORDER BY` inside `OVER`, the default frame becomes “from the start of the partition up to the current row”, so `SUM` turns into a running total. Details in *Running Totals & Window Frames*.")
    yield section("The family", "category")
    yield table(
        ["Kind", "Functions"],
        ["Aggregate", "`SUM`, `AVG`, `COUNT`, `MIN`, `MAX` + `OVER (…)`"],
        ["Ranking", "`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `CUME_DIST`"],
        ["Offset / value", "`LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`"],
    )
    yield section("Where you can use them", "map-pin")
    yield p("Window functions are evaluated in the `SELECT` step, so they are allowed only in `SELECT` and `ORDER BY`. To filter on one, compute it in a CTE/subquery first:")
    yield sql('''
        SELECT name FROM employees
        WHERE salary > AVG(salary) OVER ();
    ''', fails=True, err='misuse of window function AVG()')
    yield sql('''
        WITH x AS (
            SELECT name, salary, AVG(salary) OVER () AS avg_all FROM employees
        )
        SELECT name, salary FROM x WHERE salary > avg_all ORDER BY salary DESC, name;
    ''', out='''
        name  | salary
        ------+-------
        Asha  | 150000
        Ravi  | 120000
        Priya | 110000
        Karan | 95000
        Meera | 95000
    ''')
    yield dialect('''
        -- Snowflake / BigQuery / DuckDB / Databricks: filter on a window directly
        SELECT name, dept_id, salary
        FROM employees
        QUALIFY ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) = 1;
    ''', "Snowflake / BigQuery / DuckDB (QUALIFY)")
    yield qa("What is the difference between GROUP BY and a window function?",
             "`GROUP BY` collapses each group into one output row, so you lose row detail. A window function computes over a group (the partition) but returns a value on **every** row — so you can show each employee next to their department average, rank or running total.")
    yield qa("What is PARTITION BY?",
             "The window equivalent of `GROUP BY`: it splits rows into independent partitions, and the window function restarts for each one. Without it, the whole result set is a single partition.")


@topic(G, "ranking-functions", "ROW_NUMBER, RANK, DENSE_RANK & NTILE", "trophy")
def _():
    yield lead("Ranking functions number rows in a defined order. They differ only in how they treat **ties** — the favourite interview detail.")
    yield sql('''
        SELECT name, salary,
               ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
               RANK()       OVER (ORDER BY salary DESC) AS rnk,
               DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rnk
        FROM employees
        WHERE dept_id IN (1, 2)
        ORDER BY salary DESC, name;
    ''', out='''
        name  | salary | row_num | rnk | dense_rnk
        ------+--------+---------+-----+----------
        Asha  | 150000 | 1       | 1   | 1
        Ravi  | 120000 | 2       | 2   | 2
        Priya | 110000 | 3       | 3   | 3
        Karan | 95000  | 5       | 4   | 4
        Meera | 95000  | 4       | 4   | 4
        Neha  | 72000  | 6       | 6   | 5
        Arjun | 70000  | 7       | 7   | 6
    ''')
    yield table(
        ["Function", "Ties", "Sequence for 150, 120, 110, 95, 95, 72"],
        ["`ROW_NUMBER()`", "Arbitrary but unique numbers", "1, 2, 3, 4, 5, 6"],
        ["`RANK()`", "Same rank, then a **gap**", "1, 2, 3, 4, 4, 6"],
        ["`DENSE_RANK()`", "Same rank, **no gap**", "1, 2, 3, 4, 4, 5"],
    )
    yield warn("`ROW_NUMBER` among ties is non-deterministic — Meera and Karan could swap between runs. Add a tie-breaker: `ORDER BY salary DESC, emp_id`.")
    yield section("Ranking within groups", "layout-grid")
    yield sql('''
        SELECT dept_id, name, salary,
               DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank_in_dept
        FROM employees
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id, rank_in_dept, name;
    ''', out='''
        dept_id | name   | salary | rank_in_dept
        --------+--------+--------+-------------
        1       | Asha   | 150000 | 1
        1       | Ravi   | 120000 | 2
        1       | Karan  | 95000  | 3
        1       | Meera  | 95000  | 3
        2       | Priya  | 110000 | 1
        2       | Neha   | 72000  | 2
        2       | Arjun  | 70000  | 3
        3       | Sara   | 85000  | 1
        3       | Vikram | 80000  | 2
    ''')
    yield section("Top-N per group", "list-numbers")
    yield sql('''
        -- the 2 best-paid employees of each department
        WITH ranked AS (
            SELECT dept_id, name, salary,
                   ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC, emp_id) AS rn
            FROM employees
            WHERE dept_id IS NOT NULL
        )
        SELECT dept_id, name, salary
        FROM ranked
        WHERE rn <= 2
        ORDER BY dept_id, rn;
    ''', out='''
        dept_id | name   | salary
        --------+--------+-------
        1       | Asha   | 150000
        1       | Ravi   | 120000
        2       | Priya  | 110000
        2       | Neha   | 72000
        3       | Sara   | 85000
        3       | Vikram | 80000
    ''')
    yield p("Choose the function by the business rule: `ROW_NUMBER` for *exactly N rows*, `DENSE_RANK` for *the top N salary levels, including ties*.")
    yield section("NTILE, PERCENT_RANK, CUME_DIST", "chart-pie")
    yield sql('''
        SELECT name, salary,
               NTILE(4)       OVER (ORDER BY salary DESC)          AS quartile,
               ROUND(PERCENT_RANK() OVER (ORDER BY salary), 2)     AS pct_rank,
               ROUND(CUME_DIST()    OVER (ORDER BY salary), 2)     AS cume_dist
        FROM employees
        ORDER BY salary DESC, emp_id;
    ''', out='''
        name   | salary | quartile | pct_rank | cume_dist
        -------+--------+----------+----------+----------
        Asha   | 150000 | 1        | 1.0      | 1.0
        Ravi   | 120000 | 1        | 0.89     | 0.9
        Priya  | 110000 | 1        | 0.78     | 0.8
        Meera  | 95000  | 2        | 0.56     | 0.7
        Karan  | 95000  | 2        | 0.56     | 0.7
        Sara   | 85000  | 2        | 0.44     | 0.5
        Vikram | 80000  | 3        | 0.33     | 0.4
        Neha   | 72000  | 3        | 0.22     | 0.3
        Arjun  | 70000  | 4        | 0.11     | 0.2
        Dev    | 60000  | 4        | 0.0      | 0.1
    ''')
    yield ul(
        "`NTILE(n)` splits the ordered rows into `n` buckets as evenly as possible (earlier buckets get the extra rows: 10 rows → 3, 3, 2, 2).",
        "`PERCENT_RANK()` = `(rank − 1) / (rows − 1)` — 0 for the lowest, 1 for the highest.",
        "`CUME_DIST()` = fraction of rows with a value ≤ the current one.",
    )
    yield section("Deduplicating with ROW_NUMBER", "copy-off")
    yield sql('''
        -- each customer's most recent order
        SELECT customer_id, order_id, order_date
        FROM (
            SELECT o.*, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
            FROM orders o
        )
        WHERE rn = 1
        ORDER BY customer_id;
    ''', out='''
        customer_id | order_id | order_date
        ------------+----------+-----------
        1           | 108      | 2024-03-15
        2           | 106      | 2024-03-01
        3           | 107      | 2024-03-08
        4           | 105      | 2024-02-20
    ''')
    yield qa("RANK vs DENSE_RANK vs ROW_NUMBER?",
             "All number rows in window order. `ROW_NUMBER` always gives unique consecutive numbers (ties broken arbitrarily). `RANK` gives ties the same number and then skips (1, 2, 2, 4). `DENSE_RANK` gives ties the same number without skipping (1, 2, 2, 3). For “Nth highest salary” use `DENSE_RANK`.")


@topic(G, "lag-lead", "LAG, LEAD & Value Functions", "arrows-left-right")
def _():
    yield lead("`LAG` and `LEAD` read a value from a previous or following row of the same window — day-over-day changes, gaps between events and “next step” analysis without a self join.")
    yield sql('''
        SELECT day, amount,
               LAG(amount)       OVER (ORDER BY day) AS prev_day,
               LEAD(amount)      OVER (ORDER BY day) AS next_day,
               amount - LAG(amount) OVER (ORDER BY day) AS change,
               LAG(amount, 2, 0) OVER (ORDER BY day) AS two_days_ago
        FROM daily_sales
        ORDER BY day;
    ''', out='''
        day        | amount | prev_day | next_day | change | two_days_ago
        -----------+--------+----------+----------+--------+-------------
        2024-03-01 | 120    | NULL     | 80       | NULL   | 0
        2024-03-02 | 80     | 120      | 150      | -40    | 0
        2024-03-03 | 150    | 80       | 90       | 70     | 120
        2024-03-04 | 90     | 150      | 200      | -60    | 80
        2024-03-05 | 200    | 90       | 60       | 110    | 150
        2024-03-06 | 60     | 200      | NULL     | -140   | 90
    ''', setup=SALES)
    yield p("Signature: `LAG(expr, offset = 1, default = NULL)`. The first row has no previous row, so it gets the default.")
    yield section("Growth in percent", "trending-up")
    yield sql('''
        WITH monthly AS (
            SELECT strftime('%Y-%m', o.order_date) AS month,
                   SUM(oi.quantity * oi.unit_price) AS revenue
            FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
            WHERE o.status <> 'cancelled'
            GROUP BY month
        )
        SELECT month, revenue,
               LAG(revenue) OVER (ORDER BY month) AS prev,
               ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
                     / LAG(revenue) OVER (ORDER BY month), 1) AS growth_pct
        FROM monthly
        ORDER BY month;
    ''', out='''
        month   | revenue | prev  | growth_pct
        --------+---------+-------+-----------
        2024-01 | 66700   | NULL  | NULL
        2024-02 | 12900   | 66700 | -80.7
        2024-03 | 63700   | 12900 | 393.8
    ''')
    yield section("Per group: time between a customer's orders", "clock")
    yield sql('''
        SELECT customer_id, order_id, order_date,
               LAG(order_date) OVER w AS previous_order,
               julianday(order_date) - julianday(LAG(order_date) OVER w) AS days_since
        FROM orders
        WINDOW w AS (PARTITION BY customer_id ORDER BY order_date)
        ORDER BY customer_id, order_date;
    ''', out='''
        customer_id | order_id | order_date | previous_order | days_since
        ------------+----------+------------+----------------+-----------
        1           | 101      | 2024-01-05 | NULL           | NULL
        1           | 103      | 2024-02-03 | 2024-01-05     | 29.0
        1           | 108      | 2024-03-15 | 2024-02-03     | 41.0
        2           | 102      | 2024-01-12 | NULL           | NULL
        2           | 106      | 2024-03-01 | 2024-01-12     | 49.0
        3           | 104      | 2024-02-14 | NULL           | NULL
        3           | 107      | 2024-03-08 | 2024-02-14     | 23.0
        4           | 105      | 2024-02-20 | NULL           | NULL
    ''')
    yield note("`WINDOW w AS (…)` names a window once and reuses it (standard SQL; PostgreSQL, MySQL 8, SQLite — not SQL Server before 2022).")
    yield section("FIRST_VALUE, LAST_VALUE, NTH_VALUE", "arrow-bar-to-left")
    yield sql('''
        SELECT name, dept_id, salary,
               FIRST_VALUE(name) OVER (PARTITION BY dept_id ORDER BY salary DESC) AS top_earner,
               LAST_VALUE(name)  OVER (PARTITION BY dept_id ORDER BY salary DESC) AS last_value_default,
               LAST_VALUE(name)  OVER (PARTITION BY dept_id ORDER BY salary DESC
                                       ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS lowest_earner
        FROM employees
        WHERE dept_id = 2
        ORDER BY salary DESC;
    ''', out='''
        name  | dept_id | salary | top_earner | last_value_default | lowest_earner
        ------+---------+--------+------------+--------------------+--------------
        Priya | 2       | 110000 | Priya      | Priya              | Arjun
        Neha  | 2       | 72000  | Priya      | Neha               | Arjun
        Arjun | 2       | 70000  | Priya      | Arjun              | Arjun
    ''')
    yield warn("`LAST_VALUE` with the default frame returns the **current** row (the frame ends at the current row), not the last row of the partition. Specify `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`, or use `FIRST_VALUE` with the opposite sort.")
    yield qa("How do you compute the difference between the current row and the previous row?",
             "`value - LAG(value) OVER (PARTITION BY group ORDER BY time)`. Before window functions this needed a self join on “the previous row”, which is slower and harder to write.")


@topic(G, "window-frames", "Running Totals & Window Frames", "chart-line")
def _():
    yield lead("The **frame** decides which rows around the current row a window aggregate sees: everything so far (running total), the last 3 rows (moving average), or the whole partition.")
    yield section("Frame syntax", "code")
    yield sql('''
        {ROWS | RANGE | GROUPS} BETWEEN <start> AND <end>

        -- <start>/<end>:  UNBOUNDED PRECEDING | n PRECEDING | CURRENT ROW | n FOLLOWING | UNBOUNDED FOLLOWING
    ''', run=False)
    yield table(
        ["`OVER (…)`", "Default frame"],
        ["No `ORDER BY`", "The whole partition"],
        ["With `ORDER BY`", "`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — start to current row *including peers (ties)*"],
    )
    yield section("Running total, moving average, centered window", "chart-arrows")
    yield sql('''
        SELECT day, amount,
               SUM(amount) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
               ROUND(AVG(amount) OVER (ORDER BY day ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS moving_avg_3,
               MAX(amount) OVER (ORDER BY day ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS max_neighbourhood
        FROM daily_sales
        ORDER BY day;
    ''', out='''
        day        | amount | running_total | moving_avg_3 | max_neighbourhood
        -----------+--------+---------------+--------------+------------------
        2024-03-01 | 120    | 120           | 120.0        | 120
        2024-03-02 | 80     | 200           | 100.0        | 150
        2024-03-03 | 150    | 350           | 116.7        | 150
        2024-03-04 | 90     | 440           | 106.7        | 200
        2024-03-05 | 200    | 640           | 146.7        | 200
        2024-03-06 | 60     | 700           | 116.7        | 200
    ''', setup=SALES)
    yield p("The first two moving averages use fewer than 3 rows (there is nothing before day 1). Filter them out or show them as incomplete if that matters.")
    yield section("ROWS vs RANGE: the ties trap", "alert-triangle")
    yield sql('''
        SELECT name, salary,
               SUM(salary) OVER (ORDER BY salary)                                         AS range_default,
               SUM(salary) OVER (ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rows_frame
        FROM employees
        WHERE dept_id = 1
        ORDER BY salary, emp_id;
    ''', out='''
        name  | salary | range_default | rows_frame
        ------+--------+---------------+-----------
        Meera | 95000  | 190000        | 95000
        Karan | 95000  | 190000        | 190000
        Ravi  | 120000 | 310000        | 310000
        Asha  | 150000 | 460000        | 460000
    ''')
    yield warn("Meera and Karan both earn 95000, so with the default `RANGE` frame they are *peers* and both see 190000. `ROWS` counts physical rows: 95000 then 190000. For running totals, specify `ROWS` (and a unique tie-breaker in `ORDER BY`).")
    yield section("Running total per group, and a reset", "layout-list")
    yield sql('''
        SELECT customer_id, order_id, order_date,
               COUNT(*) OVER (PARTITION BY customer_id ORDER BY order_date
                              ROWS UNBOUNDED PRECEDING) AS nth_order_of_customer
        FROM orders
        ORDER BY customer_id, order_date;
    ''', out='''
        customer_id | order_id | order_date | nth_order_of_customer
        ------------+----------+------------+----------------------
        1           | 101      | 2024-01-05 | 1
        1           | 103      | 2024-02-03 | 2
        1           | 108      | 2024-03-15 | 3
        2           | 102      | 2024-01-12 | 1
        2           | 106      | 2024-03-01 | 2
        3           | 104      | 2024-02-14 | 1
        3           | 107      | 2024-03-08 | 2
        4           | 105      | 2024-02-20 | 1
    ''')
    yield section("Cumulative share (Pareto)", "chart-pie-2")
    yield sql('''
        WITH product_rev AS (
            SELECT p.name, SUM(oi.quantity * oi.unit_price) AS revenue
            FROM order_items oi JOIN products p ON p.product_id = oi.product_id
            GROUP BY p.product_id, p.name
        )
        SELECT name, revenue,
               ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING)
                     / SUM(revenue) OVER (), 1) AS cumulative_pct
        FROM product_rev
        ORDER BY revenue DESC;
    ''', out='''
        name       | revenue | cumulative_pct
        -----------+---------+---------------
        Laptop     | 107000  | 72.2
        Desk       | 16000   | 82.9
        Chair      | 13500   | 92.0
        Headphones | 10000   | 98.8
        Notebook   | 1500    | 99.8
        Pen        | 300     | 100.0
    ''')
    yield qa("How do you calculate a running total in SQL?",
             "`SUM(amount) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`, adding `PARTITION BY` to restart per group. Without window functions: a correlated subquery `(SELECT SUM(amount) FROM t t2 WHERE t2.day <= t.day)` — O(n²).")
    yield qa("What is the difference between ROWS and RANGE?",
             "`ROWS` defines the frame by physical row count (2 PRECEDING = the two rows before). `RANGE` defines it by value of the `ORDER BY` key, so all rows with the same key (peers) are included together — which is why the default frame gives tied rows the same running total.")
