from kit import *
from sample_db import sql, dialect, SCHEMA

G = "Interview Prep"

CONTACTS = """
CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, email TEXT);
INSERT INTO contacts VALUES
    (1, 'Asha',  'asha@mail.com'),
    (2, 'Ravi',  'ravi@mail.com'),
    (3, 'Asha',  'ASHA@mail.com'),
    (4, 'Meera', 'meera@mail.com'),
    (5, 'Ravi',  'ravi@mail.com'),
    (6, 'Ravi',  'ravi@mail.com');
"""

LOGINS = """
CREATE TABLE logins (user_id INTEGER, login_date TEXT, PRIMARY KEY (user_id, login_date));
INSERT INTO logins VALUES
    (1, '2024-03-01'), (1, '2024-03-02'), (1, '2024-03-03'), (1, '2024-03-05'), (1, '2024-03-06'),
    (2, '2024-03-01'), (2, '2024-03-03'),
    (3, '2024-03-02'), (3, '2024-03-03'), (3, '2024-03-04'), (3, '2024-03-05');
"""

SCORES = """
CREATE TABLE exam_scores (student TEXT, subject TEXT, score INTEGER);
INSERT INTO exam_scores VALUES
    ('Asha', 'Math', 91), ('Asha', 'Science', 84), ('Asha', 'English', 78),
    ('Ravi', 'Math', 67), ('Ravi', 'Science', 88),
    ('Meera', 'Math', 75), ('Meera', 'English', 95);
"""


@topic(G, "nth-highest-salary", "Nth Highest Salary", "trophy")
def _():
    yield lead("The most-asked SQL interview question. Know three solutions, and be precise about **ties** and **what to return when there is no Nth value**.")
    yield p("Salaries (distinct, highest first): 150000, 120000, 110000, **95000** (Meera and Karan), 85000, 80000, … — so the 4th highest *distinct* salary is 95000.")
    yield section("1. DENSE_RANK (best general answer)", "number-1")
    yield sql('''
        WITH ranked AS (
            SELECT name, salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
            FROM employees
        )
        SELECT name, salary FROM ranked WHERE rnk = 4 ORDER BY name;
    ''', out='''
        name  | salary
        ------+-------
        Karan | 95000
        Meera | 95000
    ''')
    yield p("Returns *every* employee with that salary. `RANK` would skip numbers after ties, and `ROW_NUMBER` would arbitrarily return only one of Meera/Karan and shift everyone below.")
    yield section("2. LIMIT / OFFSET on distinct salaries", "number-2")
    yield sql('''
        SELECT DISTINCT salary
        FROM employees
        ORDER BY salary DESC
        LIMIT 1 OFFSET 3;          -- N - 1

        -- return NULL (not zero rows) when N is too large: wrap it in a scalar subquery
        SELECT (SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 99) AS nth_salary;
    ''', out='''
        salary
        ------
        95000

        nth_salary
        ----------
        NULL
    ''')
    yield section("3. Correlated subquery (no window functions)", "number-3")
    yield sql('''
        -- the salary that has exactly N-1 distinct salaries above it
        SELECT DISTINCT e.salary
        FROM employees e
        WHERE 3 = (SELECT COUNT(DISTINCT i.salary) FROM employees i WHERE i.salary > e.salary);
    ''', out='''
        salary
        ------
        95000
    ''')
    yield sql('''
        -- 2nd highest, the classic MAX-below-MAX trick
        SELECT MAX(salary) AS second_highest
        FROM employees
        WHERE salary < (SELECT MAX(salary) FROM employees);
    ''', out='''
        second_highest
        --------------
        120000
    ''')
    yield section("Nth highest per department", "layout-grid")
    yield sql('''
        WITH ranked AS (
            SELECT d.name AS department, e.name, e.salary,
                   DENSE_RANK() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) AS rnk
            FROM employees e JOIN departments d ON d.dept_id = e.dept_id
        )
        SELECT department, name, salary FROM ranked WHERE rnk = 2 ORDER BY department;
    ''', out='''
        department  | name   | salary
        ------------+--------+-------
        Engineering | Ravi   | 120000
        HR          | Vikram | 80000
        Sales       | Neha   | 72000
    ''')
    yield dialect('''
        SELECT DISTINCT salary FROM employees ORDER BY salary DESC
        OFFSET 3 ROWS FETCH NEXT 1 ROWS ONLY;                  -- SQL Server 2012+ / Oracle 12c+

        SELECT TOP 1 salary FROM (
            SELECT DISTINCT TOP 4 salary FROM employees ORDER BY salary DESC
        ) t ORDER BY salary ASC;                               -- older SQL Server
    ''', "SQL Server / Oracle")
    yield qa("Which approach would you give in an interview?",
             "`DENSE_RANK()` in a CTE: it handles ties correctly, generalises to “per department” with `PARTITION BY`, and reads clearly. Mention `LIMIT/OFFSET` on `DISTINCT` salaries as the short alternative, and wrap it in a scalar subquery if the spec says “return NULL if there is no Nth salary”.")


@topic(G, "duplicates", "Finding & Deleting Duplicates", "copy")
def _():
    yield lead("Find rows that repeat a value that should be unique, show all copies, and delete all but one — three variations of the same `GROUP BY`/`ROW_NUMBER` idea.")
    yield sql('''
        SELECT * FROM contacts ORDER BY id;
    ''', out='''
        id | name  | email
        ---+-------+---------------
        1  | Asha  | asha@mail.com
        2  | Ravi  | ravi@mail.com
        3  | Asha  | ASHA@mail.com
        4  | Meera | meera@mail.com
        5  | Ravi  | ravi@mail.com
        6  | Ravi  | ravi@mail.com
    ''', setup=CONTACTS)
    yield section("Which values are duplicated?", "search")
    yield sql('''
        SELECT email, COUNT(*) AS copies
        FROM contacts
        GROUP BY email
        HAVING COUNT(*) > 1;

        -- case-insensitive duplicates
        SELECT lower(email) AS email, COUNT(*) AS copies, group_concat(id) AS ids
        FROM contacts
        GROUP BY lower(email)
        HAVING COUNT(*) > 1
        ORDER BY email;
    ''', out='''
        email         | copies
        --------------+-------
        ravi@mail.com | 3

        email         | copies | ids
        --------------+--------+------
        asha@mail.com | 2      | 1,3
        ravi@mail.com | 3      | 2,5,6
    ''', setup=CONTACTS)
    yield section("Show every duplicate row", "list-details")
    yield sql('''
        SELECT id, name, email,
               COUNT(*) OVER (PARTITION BY email) AS copies
        FROM contacts
        ORDER BY email, id;
    ''', out='''
        id | name  | email          | copies
        ---+-------+----------------+-------
        3  | Asha  | ASHA@mail.com  | 1
        1  | Asha  | asha@mail.com  | 1
        4  | Meera | meera@mail.com | 1
        2  | Ravi  | ravi@mail.com  | 3
        5  | Ravi  | ravi@mail.com  | 3
        6  | Ravi  | ravi@mail.com  | 3
    ''', setup=CONTACTS)
    yield sql('''
        -- rows whose (name, email) combination appears more than once
        SELECT c.*
        FROM contacts c
        JOIN (SELECT name, email FROM contacts GROUP BY name, email HAVING COUNT(*) > 1) d
          ON d.name = c.name AND d.email = c.email
        ORDER BY c.id;
    ''', out='''
        id | name | email
        ---+------+--------------
        2  | Ravi | ravi@mail.com
        5  | Ravi | ravi@mail.com
        6  | Ravi | ravi@mail.com
    ''', setup=CONTACTS)
    yield section("Delete duplicates, keep the lowest id", "trash")
    yield sql('''
        DELETE FROM contacts
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
                FROM contacts
            ) WHERE rn > 1
        );

        SELECT * FROM contacts ORDER BY id;
    ''', out='''
        id | name  | email
        ---+-------+---------------
        1  | Asha  | asha@mail.com
        2  | Ravi  | ravi@mail.com
        3  | Asha  | ASHA@mail.com
        4  | Meera | meera@mail.com
    ''', setup=CONTACTS)
    yield sql('''
        -- without window functions: keep MIN(id) of each group
        DELETE FROM contacts
        WHERE id NOT IN (SELECT MIN(id) FROM contacts GROUP BY email);

        SELECT * FROM contacts ORDER BY id;
    ''', out='''
        id | name  | email
        ---+-------+---------------
        1  | Asha  | asha@mail.com
        2  | Ravi  | ravi@mail.com
        3  | Asha  | ASHA@mail.com
        4  | Meera | meera@mail.com
    ''', setup=CONTACTS)
    yield p("Contact 3 (`ASHA@mail.com`) survived both deletes: the comparison is case-sensitive. Partition/group by `lower(email)` when duplicates should be detected case-insensitively.")
    yield dialect('''
        -- MySQL: self-join delete
        DELETE c1 FROM contacts c1
        JOIN contacts c2 ON c2.email = c1.email AND c2.id < c1.id;

        -- SQL Server: delete through a CTE
        WITH d AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn FROM contacts)
        DELETE FROM d WHERE rn > 1;
    ''', "MySQL / SQL Server")
    yield good("After cleaning, add the constraint that should have been there: `CREATE UNIQUE INDEX ux_contacts_email ON contacts (lower(email));`")
    yield qa("How do you delete duplicate rows but keep one?",
             "Number the rows within each duplicate group with `ROW_NUMBER() OVER (PARTITION BY <dup columns> ORDER BY id)` and delete those with `rn > 1`; or delete where `id NOT IN (SELECT MIN(id) … GROUP BY <dup columns>)`. If the table has no unique id at all, copy distinct rows to a new table (or use the engine's physical row id: `rowid` in SQLite, `ctid` in PostgreSQL).")


@topic(G, "top-n-per-group", "Top-N per Group & Department Max", "list-numbers")
def _():
    yield lead("“Highest-paid employee in each department”, “latest order per customer”, “top 2 products per category” — one pattern with a few variants.")
    yield section("Department max: three ways", "crown")
    yield sql('''
        -- 1. window function
        SELECT department, name, salary FROM (
            SELECT d.name AS department, e.name, e.salary,
                   RANK() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) AS rnk
            FROM employees e JOIN departments d ON d.dept_id = e.dept_id
        ) WHERE rnk = 1
        ORDER BY department;
    ''', out='''
        department  | name  | salary
        ------------+-------+-------
        Engineering | Asha  | 150000
        HR          | Sara  | 85000
        Sales       | Priya | 110000
    ''')
    yield sql('''
        -- 2. join to the per-group max
        SELECT d.name AS department, e.name, e.salary
        FROM employees e
        JOIN (SELECT dept_id, MAX(salary) AS max_sal FROM employees GROUP BY dept_id) m
          ON m.dept_id = e.dept_id AND m.max_sal = e.salary
        JOIN departments d ON d.dept_id = e.dept_id
        ORDER BY department;

        -- 3. correlated subquery
        SELECT e.dept_id, e.name, e.salary
        FROM employees e
        WHERE e.salary = (SELECT MAX(salary) FROM employees i WHERE i.dept_id = e.dept_id)
        ORDER BY e.dept_id;
    ''', out='''
        department  | name  | salary
        ------------+-------+-------
        Engineering | Asha  | 150000
        HR          | Sara  | 85000
        Sales       | Priya | 110000

        dept_id | name  | salary
        --------+-------+-------
        1       | Asha  | 150000
        2       | Priya | 110000
        3       | Sara  | 85000
    ''')
    yield note("All three return **ties** (both rows if two people share the max). Use `ROW_NUMBER` instead of `RANK` when exactly one row per group is required, with a deterministic tie-breaker.")
    yield section("Top 2 products by revenue per category", "chart-bar")
    yield sql('''
        WITH product_revenue AS (
            SELECT p.category, p.name, COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
            FROM products p
            LEFT JOIN order_items oi ON oi.product_id = p.product_id
            GROUP BY p.product_id, p.category, p.name
        ),
        ranked AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC, name) AS rn
            FROM product_revenue
        )
        SELECT category, name, revenue FROM ranked WHERE rn <= 2 ORDER BY category, rn;
    ''', out='''
        category    | name       | revenue
        ------------+------------+--------
        Electronics | Laptop     | 107000
        Electronics | Headphones | 10000
        Furniture   | Desk       | 16000
        Furniture   | Chair      | 13500
        Stationery  | Notebook   | 1500
        Stationery  | Pen        | 300
    ''')
    yield section("Latest order per customer (with details)", "clock")
    yield sql('''
        SELECT c.name, o.order_id, o.order_date, o.status
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.order_date = (SELECT MAX(order_date) FROM orders o2 WHERE o2.customer_id = c.customer_id)
        ORDER BY c.customer_id;
    ''', out='''
        name   | order_id | order_date | status
        -------+----------+------------+----------
        Ananya | 108      | 2024-03-15 | shipped
        Rahul  | 106      | 2024-03-01 | delivered
        Sneha  | 107      | 2024-03-08 | pending
        Imran  | 105      | 2024-02-20 | cancelled
    ''')
    yield qa("How do you get the top 3 rows per group?",
             "`ROW_NUMBER()` (exactly 3) or `DENSE_RANK()` (top 3 values incl. ties) `OVER (PARTITION BY group ORDER BY metric DESC)` in a CTE/subquery, then `WHERE rn <= 3`. Alternatives: `LATERAL`/`CROSS APPLY` with `LIMIT 3` per group (PostgreSQL/SQL Server) — efficient with an index on (group, metric).")


@topic(G, "employee-manager-queries", "Employee–Manager Queries", "hierarchy")
def _():
    yield lead("The self-referencing `employees` table powers a whole family of interview questions. All of them are a self join, an aggregate, or a recursive CTE.")
    yield section("Employees earning more than their manager", "arrow-up-right")
    yield sql('''
        SELECT e.name AS employee, e.salary, m.name AS manager, m.salary AS manager_salary
        FROM employees e
        JOIN employees m ON m.emp_id = e.manager_id
        WHERE e.salary > m.salary;
    ''', out='''
        employee | salary | manager | manager_salary
        ---------+--------+---------+---------------
        Sara     | 85000  | Vikram  | 80000
    ''')
    yield section("Managers with at least N direct reports", "users-group")
    yield sql('''
        SELECT m.name AS manager, COUNT(*) AS direct_reports
        FROM employees e
        JOIN employees m ON m.emp_id = e.manager_id
        GROUP BY m.emp_id, m.name
        HAVING COUNT(*) >= 2
        ORDER BY direct_reports DESC, manager;
    ''', out='''
        manager | direct_reports
        --------+---------------
        Asha    | 4
        Priya   | 2
        Ravi    | 2
    ''')
    yield section("Employees who are not managers (leaf nodes)", "leaf")
    yield sql('''
        SELECT e.name
        FROM employees e
        WHERE NOT EXISTS (SELECT 1 FROM employees r WHERE r.manager_id = e.emp_id)
        ORDER BY e.emp_id;
    ''', out='''
        name
        -----
        Meera
        Karan
        Arjun
        Neha
        Sara
        Dev
    ''')
    yield section("Employee, manager and department in one row", "id-badge-2")
    yield sql('''
        SELECT e.name AS employee,
               COALESCE(m.name, '—')      AS manager,
               COALESCE(d.name, 'Unassigned') AS department,
               CASE WHEN e.dept_id = m.dept_id THEN 'same' ELSE 'different' END AS manager_dept
        FROM employees e
        LEFT JOIN employees m   ON m.emp_id = e.manager_id
        LEFT JOIN departments d ON d.dept_id = e.dept_id
        ORDER BY e.emp_id;
    ''', out='''
        employee | manager | department  | manager_dept
        ---------+---------+-------------+-------------
        Asha     | —       | Engineering | different
        Ravi     | Asha    | Engineering | same
        Meera    | Ravi    | Engineering | same
        Karan    | Ravi    | Engineering | same
        Priya    | Asha    | Sales       | different
        Arjun    | Priya   | Sales       | same
        Neha     | Priya   | Sales       | same
        Vikram   | Asha    | HR          | different
        Sara     | Vikram  | HR          | same
        Dev      | Asha    | Unassigned  | different
    ''')
    yield section("Salary as a percentage of the manager's", "percentage")
    yield sql('''
        SELECT e.name, e.salary, m.name AS manager,
               ROUND(100.0 * e.salary / m.salary, 1) AS pct_of_manager
        FROM employees e JOIN employees m ON m.emp_id = e.manager_id
        ORDER BY pct_of_manager DESC, e.emp_id
        LIMIT 4;
    ''', out='''
        name  | salary | manager | pct_of_manager
        ------+--------+---------+---------------
        Sara  | 85000  | Vikram  | 106.3
        Ravi  | 120000 | Asha    | 80.0
        Meera | 95000  | Ravi    | 79.2
        Karan | 95000  | Ravi    | 79.2
    ''')
    yield section("Department salary above company average", "chart-bar")
    yield sql('''
        SELECT d.name, ROUND(AVG(e.salary)) AS dept_avg
        FROM employees e JOIN departments d ON d.dept_id = e.dept_id
        GROUP BY d.dept_id, d.name
        HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees)
        ORDER BY dept_avg DESC;
    ''', out='''
        name        | dept_avg
        ------------+---------
        Engineering | 115000.0
    ''')
    yield qa("How do you find the full reporting chain of an employee?",
             "A recursive CTE: anchor on the employee, then repeatedly join `employees m ON m.emp_id = chain.manager_id` until `manager_id` is `NULL` — see *Recursive CTEs*. For a fixed depth, chain self joins (`e → m1 → m2`).")


@topic(G, "gaps-and-islands", "Consecutive Days, Gaps & Islands", "timeline")
def _():
    yield lead("“Users who logged in 3 days in a row”, “longest streak”, “missing ids” — the **gaps-and-islands** family, solved elegantly with `ROW_NUMBER` or `LAG`.")
    yield sql('''
        SELECT user_id, group_concat(substr(login_date, 9), ', ') AS march_days
        FROM (SELECT * FROM logins ORDER BY user_id, login_date)
        GROUP BY user_id
        ORDER BY user_id;
    ''', out='''
        user_id | march_days
        --------+-------------------
        1       | 01, 02, 03, 05, 06
        2       | 01, 03
        3       | 02, 03, 04, 05
    ''', setup=LOGINS)
    yield section("The islands trick", "bulb")
    yield p("Within one user, subtract the row number (in days) from the date. Consecutive dates produce the **same** anchor value; a gap changes it. Group by that anchor and each group is one streak (“island”).")
    yield sql('''
        SELECT user_id, login_date,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn,
               date(login_date, '-' || ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) || ' days') AS grp
        FROM logins
        WHERE user_id = 1
        ORDER BY login_date;
    ''', out='''
        user_id | login_date | rn | grp
        --------+------------+----+-----------
        1       | 2024-03-01 | 1  | 2024-02-29
        1       | 2024-03-02 | 2  | 2024-02-29
        1       | 2024-03-03 | 3  | 2024-02-29
        1       | 2024-03-05 | 4  | 2024-03-01
        1       | 2024-03-06 | 5  | 2024-03-01
    ''', setup=LOGINS)
    yield sql('''
        WITH marked AS (
            SELECT user_id, login_date,
                   date(login_date, '-' || ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) || ' days') AS grp
            FROM logins
        )
        SELECT user_id, MIN(login_date) AS streak_start, MAX(login_date) AS streak_end, COUNT(*) AS days
        FROM marked
        GROUP BY user_id, grp
        ORDER BY user_id, streak_start;
    ''', out='''
        user_id | streak_start | streak_end | days
        --------+--------------+------------+-----
        1       | 2024-03-01   | 2024-03-03 | 3
        1       | 2024-03-05   | 2024-03-06 | 2
        2       | 2024-03-01   | 2024-03-01 | 1
        2       | 2024-03-03   | 2024-03-03 | 1
        3       | 2024-03-02   | 2024-03-05 | 4
    ''', setup=LOGINS)
    yield section("Users with 3+ consecutive days, and longest streak", "flame")
    yield sql('''
        WITH marked AS (
            SELECT user_id,
                   date(login_date, '-' || ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) || ' days') AS grp
            FROM logins
        ),
        streaks AS (
            SELECT user_id, COUNT(*) AS days FROM marked GROUP BY user_id, grp
        )
        SELECT user_id, MAX(days) AS longest_streak
        FROM streaks
        GROUP BY user_id
        HAVING MAX(days) >= 3
        ORDER BY user_id;
    ''', out='''
        user_id | longest_streak
        --------+---------------
        1       | 3
        3       | 4
    ''', setup=LOGINS)
    yield section("The LAG alternative: detect breaks", "arrows-left-right")
    yield sql('''
        -- 3 consecutive days = today, yesterday and the day before are all present
        SELECT DISTINCT user_id
        FROM (
            SELECT user_id, login_date,
                   LAG(login_date, 2) OVER (PARTITION BY user_id ORDER BY login_date) AS two_back
            FROM logins
        )
        WHERE julianday(login_date) - julianday(two_back) = 2
        ORDER BY user_id;
    ''', out='''
        user_id
        -------
        1
        3
    ''', setup=LOGINS)
    yield section("Gaps: missing values in a sequence", "separator")
    yield sql('''
        -- gaps in order ids (orders 101..108 exist; pretend 103 and 104 were deleted)
        DELETE FROM order_items WHERE order_id IN (103, 104);
        DELETE FROM orders WHERE order_id IN (103, 104);

        SELECT order_id + 1 AS gap_start, next_id - 1 AS gap_end
        FROM (SELECT order_id, LEAD(order_id) OVER (ORDER BY order_id) AS next_id FROM orders)
        WHERE next_id - order_id > 1;
    ''', out='''
        gap_start | gap_end
        ----------+--------
        103       | 104
    ''')
    yield qa("Find users who logged in on 3 consecutive days.",
             "Either `LAG(login_date, 2) OVER (PARTITION BY user_id ORDER BY login_date)` and keep rows where the date difference is exactly 2 days (deduplicate dates first), or the islands trick: `login_date − ROW_NUMBER()` days is constant across a streak, so `GROUP BY user_id, that_value HAVING COUNT(*) >= 3`.")


@topic(G, "pivoting", "Pivoting Rows into Columns", "table-column")
def _():
    yield lead("A pivot turns row values (subjects, months, statuses) into columns. The portable way is **conditional aggregation**: `GROUP BY` the row key and one `CASE` per output column.")
    yield sql('''
        SELECT * FROM exam_scores ORDER BY student, subject;
    ''', out='''
        student | subject | score
        --------+---------+------
        Asha    | English | 78
        Asha    | Math    | 91
        Asha    | Science | 84
        Meera   | English | 95
        Meera   | Math    | 75
        Ravi    | Math    | 67
        Ravi    | Science | 88
    ''', setup=SCORES)
    yield section("Pivot with CASE", "table-column")
    yield sql('''
        SELECT student,
               MAX(CASE WHEN subject = 'Math'    THEN score END) AS math,
               MAX(CASE WHEN subject = 'Science' THEN score END) AS science,
               MAX(CASE WHEN subject = 'English' THEN score END) AS english,
               SUM(score) AS total
        FROM exam_scores
        GROUP BY student
        ORDER BY student;
    ''', out='''
        student | math | science | english | total
        --------+------+---------+---------+------
        Asha    | 91   | 84      | 78      | 253
        Meera   | 75   | NULL    | 95      | 170
        Ravi    | 67   | 88      | NULL    | 155
    ''', setup=SCORES)
    yield p("`MAX` just picks the single value in each cell (any aggregate works when there is one row per cell; use `SUM` when several rows should add up). Missing combinations become `NULL`.")
    yield section("Business pivot: order counts per month and status", "calendar-stats")
    yield sql('''
        SELECT strftime('%Y-%m', order_date) AS month,
               SUM(status = 'delivered') AS delivered,
               SUM(status = 'shipped')   AS shipped,
               SUM(status = 'pending')   AS pending,
               SUM(status = 'cancelled') AS cancelled,
               COUNT(*)                  AS total
        FROM orders
        GROUP BY month
        ORDER BY month;
    ''', out='''
        month   | delivered | shipped | pending | cancelled | total
        --------+-----------+---------+---------+-----------+------
        2024-01 | 2         | 0       | 0       | 0         | 2
        2024-02 | 1         | 1       | 0       | 1         | 3
        2024-03 | 1         | 1       | 1       | 0         | 3
    ''')
    yield p("In SQLite and MySQL a comparison is `1`/`0`, so `SUM(status = 'x')` counts matches. Portable form: `SUM(CASE WHEN status = 'x' THEN 1 ELSE 0 END)`; PostgreSQL: `COUNT(*) FILTER (WHERE status = 'x')`.")
    yield section("Unpivot: columns back into rows", "table-row")
    yield sql('''
        CREATE TABLE quarterly (region TEXT, q1 INTEGER, q2 INTEGER, q3 INTEGER);
        INSERT INTO quarterly VALUES ('North', 100, 120, 90), ('South', 80, 95, 110);

        SELECT region, 'Q1' AS quarter, q1 AS sales FROM quarterly
        UNION ALL SELECT region, 'Q2', q2 FROM quarterly
        UNION ALL SELECT region, 'Q3', q3 FROM quarterly
        ORDER BY region, quarter;
    ''', out='''
        region | quarter | sales
        -------+---------+------
        North  | Q1      | 100
        North  | Q2      | 120
        North  | Q3      | 90
        South  | Q1      | 80
        South  | Q2      | 95
        South  | Q3      | 110
    ''', setup="")
    yield dialect('''
        SELECT *
        FROM (SELECT student, subject, score FROM exam_scores) src
        PIVOT (MAX(score) FOR subject IN ([Math], [Science], [English])) p;

        SELECT region, quarter, sales
        FROM quarterly
        UNPIVOT (sales FOR quarter IN (q1, q2, q3)) u;
    ''', "SQL Server / Oracle (PIVOT / UNPIVOT)")
    yield warn("SQL needs the output columns known when the query is written. For a *dynamic* list of pivot columns you must generate the SQL text in application code (or dynamic SQL) — or pivot in the reporting tool.")
    yield qa("How do you convert rows to columns in SQL?",
             "Conditional aggregation: `SELECT key, MAX(CASE WHEN attr = 'A' THEN value END) AS a, … FROM t GROUP BY key`. It works in every engine; SQL Server/Oracle also have `PIVOT`, PostgreSQL has `crosstab()` in the `tablefunc` extension.")


@topic(G, "median-running-difference", "Median, Percentiles & Running Differences", "chart-histogram")
def _():
    yield lead("There is no universal `MEDIAN()` in SQL. Interviewers ask you to build it from window functions — and to compute running totals and row-to-row differences.")
    yield section("Median with ROW_NUMBER and COUNT", "math-function")
    yield sql('''
        -- works for odd and even counts: average the middle one or two rows
        WITH ordered AS (
            SELECT salary,
                   ROW_NUMBER() OVER (ORDER BY salary) AS rn,
                   COUNT(*)     OVER ()                AS n
            FROM employees
        )
        SELECT AVG(salary) AS median_salary
        FROM ordered
        WHERE rn IN ((n + 1) / 2, (n + 2) / 2);
    ''', out='''
        median_salary
        -------------
        90000.0
    ''')
    yield p("With 10 salaries, integer division gives rows 5 and 6 (85000 and 95000) → 90000. With 9 rows both expressions give 5, the single middle row.")
    yield sql('''
        -- median per department
        WITH ordered AS (
            SELECT dept_id, salary,
                   ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary) AS rn,
                   COUNT(*)     OVER (PARTITION BY dept_id)                AS n
            FROM employees
            WHERE dept_id IS NOT NULL
        )
        SELECT dept_id, AVG(salary) AS median_salary
        FROM ordered
        WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
        GROUP BY dept_id
        ORDER BY dept_id;
    ''', out='''
        dept_id | median_salary
        --------+--------------
        1       | 107500.0
        2       | 72000.0
        3       | 82500.0
    ''')
    yield sql('''
        -- recent SQLite builds (3.53 here) include median() and percentile()
        SELECT median(salary) AS median, ROUND(percentile(salary, 90)) AS p90 FROM employees;
    ''', out='''
        median  | p90
        --------+---------
        90000.0 | 123000.0
    ''', caption="SQLite (recent)")
    yield dialect('''
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median,     -- interpolated
               PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY salary) AS median_disc -- an actual value
        FROM employees;                                         -- PostgreSQL / Oracle (SQL Server: OVER ())
        SELECT MEDIAN(salary) FROM employees;                   -- Oracle, Snowflake
    ''', "PostgreSQL / Oracle / SQL Server / Snowflake")
    yield section("Running total and running difference", "trending-up")
    yield sql('''
        WITH monthly AS (
            SELECT strftime('%Y-%m', o.order_date) AS month, SUM(oi.quantity * oi.unit_price) AS revenue
            FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
            WHERE o.status <> 'cancelled'
            GROUP BY month
        )
        SELECT month, revenue,
               SUM(revenue) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS running_total,
               revenue - LAG(revenue, 1, 0) OVER (ORDER BY month)            AS diff_from_prev
        FROM monthly
        ORDER BY month;
    ''', out='''
        month   | revenue | running_total | diff_from_prev
        --------+---------+---------------+---------------
        2024-01 | 66700   | 66700         | 66700
        2024-02 | 12900   | 79600         | -53800
        2024-03 | 63700   | 143300        | 50800
    ''')
    yield section("Difference from the group's first / previous value", "arrows-diff")
    yield sql('''
        SELECT name, hire_date, salary,
               salary - FIRST_VALUE(salary) OVER (ORDER BY hire_date) AS vs_first_hire,
               julianday(hire_date) - julianday(LAG(hire_date) OVER (ORDER BY hire_date)) AS days_since_prev_hire
        FROM employees
        WHERE dept_id = 1
        ORDER BY hire_date;
    ''', out='''
        name  | hire_date  | salary | vs_first_hire | days_since_prev_hire
        ------+------------+--------+---------------+---------------------
        Asha  | 2015-03-01 | 150000 | 0             | NULL
        Ravi  | 2017-06-15 | 120000 | -30000        | 837.0
        Meera | 2019-01-10 | 95000  | -55000        | 574.0
        Karan | 2020-08-01 | 95000  | -55000        | 569.0
    ''')
    yield qa("How do you calculate a median in SQL?",
             "Portable: number rows with `ROW_NUMBER() OVER (ORDER BY x)` and count them with `COUNT(*) OVER ()`, then average the rows at positions `(n+1)/2` and `(n+2)/2` (integer division). Engine functions: `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x)` (PostgreSQL, Oracle, SQL Server), `MEDIAN(x)` (Oracle, Snowflake, recent SQLite builds).")


@topic(G, "classic-puzzles", "More Classic SQL Puzzles", "puzzle")
def _():
    yield lead("A grab-bag of questions that test whether you think in sets: relational division, conditional counts, comparisons against aggregates, and self-referencing updates.")
    yield section("Customers who bought every product in a category (relational division)", "divide")
    yield sql('''
        -- customers who bought ALL Furniture products (Desk and Chair)
        SELECT c.name
        FROM customers c
        JOIN orders o       ON o.customer_id = c.customer_id
        JOIN order_items oi ON oi.order_id   = o.order_id
        JOIN products p     ON p.product_id  = oi.product_id
        WHERE p.category = 'Furniture'
        GROUP BY c.customer_id, c.name
        HAVING COUNT(DISTINCT p.product_id) = (SELECT COUNT(*) FROM products WHERE category = 'Furniture')
        ORDER BY c.name;
    ''', out='''
        name
        -----
        Sneha
    ''')
    yield section("Customers who ordered in every month of Q1", "calendar-check")
    yield sql('''
        SELECT c.name
        FROM customers c JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.order_date >= '2024-01-01' AND o.order_date < '2024-04-01'
        GROUP BY c.customer_id, c.name
        HAVING COUNT(DISTINCT strftime('%m', o.order_date)) = 3;
    ''', out='''
        name
        ------
        Ananya
    ''')
    yield section("Products never ordered together with a Laptop", "link-off")
    yield sql('''
        SELECT p.name FROM products p
        WHERE p.name <> 'Laptop'
          AND NOT EXISTS (
              SELECT 1
              FROM order_items a
              JOIN order_items b ON b.order_id = a.order_id
              JOIN products l    ON l.product_id = b.product_id AND l.name = 'Laptop'
              WHERE a.product_id = p.product_id
          )
        ORDER BY p.name;
    ''', out='''
        name
        --------
        Chair
        Desk
        Monitor
        Notebook
        Pen
    ''')
    yield section("Share of total per row", "percentage")
    yield sql('''
        SELECT category,
               SUM(price) AS catalogue_value,
               ROUND(100.0 * SUM(price) / (SELECT SUM(price) FROM products), 1) AS pct
        FROM products
        GROUP BY category
        ORDER BY pct DESC;
    ''', out='''
        category    | catalogue_value | pct
        ------------+-----------------+-----
        Electronics | 69500           | 84.7
        Furniture   | 12500           | 15.2
        Stationery  | 80              | 0.1
    ''')
    yield section("Swap two values in one UPDATE", "switch-horizontal")
    yield sql('''
        CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, gender TEXT);
        INSERT INTO people VALUES (1, 'A', 'm'), (2, 'B', 'f'), (3, 'C', 'm');

        UPDATE people SET gender = CASE gender WHEN 'm' THEN 'f' ELSE 'm' END;
        SELECT * FROM people ORDER BY id;
    ''', out='''
        id | name | gender
        ---+------+-------
        1  | A    | f
        2  | B    | m
        3  | C    | f
    ''', setup="")
    yield section("Year-over-year style comparison with a self join", "arrows-left-right")
    yield sql('''
        WITH monthly AS (
            SELECT CAST(strftime('%m', o.order_date) AS INTEGER) AS m, COUNT(*) AS orders
            FROM orders o GROUP BY m
        )
        SELECT cur.m AS month, cur.orders, prev.orders AS prev_month_orders
        FROM monthly cur
        LEFT JOIN monthly prev ON prev.m = cur.m - 1
        ORDER BY cur.m;
    ''', out='''
        month | orders | prev_month_orders
        ------+--------+------------------
        1     | 2      | NULL
        2     | 3      | 2
        3     | 3      | 3
    ''')
    yield section("Second most recent order of each customer", "history")
    yield sql('''
        SELECT customer_id, order_id, order_date
        FROM (
            SELECT o.*, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
            FROM orders o
        )
        WHERE rn = 2
        ORDER BY customer_id;
    ''', out='''
        customer_id | order_id | order_date
        ------------+----------+-----------
        1           | 103      | 2024-02-03
        2           | 102      | 2024-01-12
        3           | 104      | 2024-02-14
    ''')
    yield qa("How do you find customers who bought all products (relational division)?",
             "Group the customer's distinct purchased products and compare the count with the total number of products: `GROUP BY customer HAVING COUNT(DISTINCT product_id) = (SELECT COUNT(*) FROM products)`. The double-`NOT EXISTS` formulation (“there is no product the customer has not bought”) is the textbook alternative.")


@topic(G, "sql-interview-questions", "SQL Interview Q&A", "message-question")
def _():
    yield lead("Rapid-fire theory questions with crisp answers. Each links to the topic where it is explained with runnable examples.")
    yield section("Fundamentals", "school")
    yield qa("What is the difference between DELETE, TRUNCATE and DROP?",
             "`DELETE` removes selected rows (DML, `WHERE`, triggers fire, rollback-able). `TRUNCATE` removes all rows fast by deallocating pages (DDL, no `WHERE`, resets identity). `DROP` removes the table itself.")
    yield qa("What is the difference between WHERE and HAVING?",
             "`WHERE` filters rows before grouping and can't use aggregates; `HAVING` filters groups after `GROUP BY` and can.")
    yield qa("What is the logical order of execution of a SELECT?",
             "`FROM`/`JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT`.")
    yield qa("What is NULL? How do you test for it?",
             "The marker for a missing/unknown value. Comparisons with it are `UNKNOWN`, so use `IS NULL` / `IS NOT NULL`; replace it with `COALESCE`. Aggregates ignore it; `COUNT(*)` doesn't.")
    yield qa("UNION vs UNION ALL?",
             "Both stack results; `UNION` removes duplicates (extra sort/hash), `UNION ALL` keeps them and is faster.")
    yield qa("What are the types of joins?",
             "`INNER` (matches only), `LEFT`/`RIGHT` `OUTER` (all rows of one side), `FULL OUTER` (all rows of both), `CROSS` (Cartesian product), plus self joins, non-equi joins, and semi/anti joins via `EXISTS`/`NOT EXISTS`.")
    yield qa("CHAR vs VARCHAR?",
             "`CHAR(n)` is fixed length and space-padded; `VARCHAR(n)` stores only the actual characters plus a length. Use `CHAR` only for truly fixed-length codes.")
    yield section("Design", "schema")
    yield qa("Primary key vs unique key?",
             "One primary key per table, never `NULL`, the row identity and FK target. Many unique keys allowed, `NULL`s permitted.")
    yield qa("What is a foreign key?",
             "A column (set) whose values must exist in the referenced key of another table, enforcing referential integrity, with `ON DELETE`/`ON UPDATE` actions (`RESTRICT`, `CASCADE`, `SET NULL`).")
    yield qa("What is normalization? Name the normal forms.",
             "Organising data so each fact is stored once: 1NF (atomic values), 2NF (no partial dependency on a composite key), 3NF (no transitive dependency), BCNF (every determinant is a candidate key). Prevents update/insert/delete anomalies.")
    yield qa("When would you denormalize?",
             "For measured read-performance needs or analytics (star schemas), accepting redundancy and sync logic.")
    yield section("Advanced querying", "code")
    yield qa("What is a CTE? A recursive CTE?",
             "A named subquery defined with `WITH` for one statement. A recursive CTE references itself (anchor `UNION ALL` recursive member) to walk hierarchies or generate series.")
    yield qa("What are window functions?",
             "Functions computed over a set of rows related to the current row via `OVER (PARTITION BY … ORDER BY … frame)`, without collapsing rows: ranks, running totals, `LAG`/`LEAD`.")
    yield qa("RANK vs DENSE_RANK vs ROW_NUMBER?",
             "`ROW_NUMBER`: 1,2,3,4 always unique. `RANK`: ties share, then a gap (1,2,2,4). `DENSE_RANK`: ties share, no gap (1,2,2,3).")
    yield qa("Correlated vs non-correlated subquery?",
             "A correlated subquery references the outer query and is evaluated per outer row; a non-correlated one runs once independently.")
    yield qa("EXISTS vs IN vs JOIN?",
             "`EXISTS`/`IN` test membership without duplicating rows (semi join); a `JOIN` returns combined rows and can multiply them. Prefer `NOT EXISTS` over `NOT IN` because of `NULL`s.")
    yield section("Performance & internals", "rocket")
    yield qa("What is an index? What are its downsides?",
             "A sorted auxiliary structure (usually a B+tree) for fast lookups, ranges and sorts. It costs storage and slows `INSERT`/`UPDATE`/`DELETE`.")
    yield qa("Clustered vs non-clustered index?",
             "Clustered: table rows are physically stored in index order (one per table, usually the PK). Non-clustered: separate structure pointing back to rows (many per table).")
    yield qa("What is a covering index?",
             "An index that contains all columns a query needs, so the query is answered from the index without reading the table.")
    yield qa("What makes a query non-sargable?",
             "Functions or arithmetic on the indexed column, leading-wildcard `LIKE`, implicit type conversion, or `OR` across columns — the index can't be used for a seek.")
    yield qa("How do you find why a query is slow?",
             "`EXPLAIN` / `EXPLAIN ANALYZE`: look for full scans, bad estimates, sorts and nested loops over big inputs; then index, rewrite, or reduce data.")
    yield section("Transactions & security", "lock")
    yield qa("What is ACID?",
             "Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions don't interfere, per isolation level), Durability (committed data survives crashes).")
    yield qa("Name the isolation levels and the anomalies they prevent.",
             "Read Uncommitted (none), Read Committed (dirty reads), Repeatable Read (+ non-repeatable reads), Serializable (+ phantoms and all others).")
    yield qa("What is a deadlock?",
             "Transactions waiting on each other's locks in a cycle; the database kills one. Avoid with consistent lock order and short transactions; retry on error.")
    yield qa("What is SQL injection and how do you prevent it?",
             "Untrusted input concatenated into SQL changes the query. Prevent with parameterized queries, allow-lists for identifiers and least-privilege accounts.")
    yield qa("View vs materialized view?",
             "A view is a stored query run on each access (always fresh, no storage). A materialized view stores the result (fast, but stale until refreshed).")
    yield qa("Stored procedure vs function?",
             "Procedures are called with `CALL`/`EXEC`, may modify data, return result sets/`OUT` params and control transactions; functions return a value/table and are used inside queries.")
    yield qa("What is a trigger?",
             "Code run automatically `BEFORE`/`AFTER`/`INSTEAD OF` an `INSERT`/`UPDATE`/`DELETE` — for audit logs, derived values and complex rules; use sparingly because it hides logic.")
