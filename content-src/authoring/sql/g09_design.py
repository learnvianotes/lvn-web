from kit import *
from sample_db import sql, dialect

G = "Database Design"

UNNORMALISED = """
CREATE TABLE order_sheet (
    order_id      INTEGER,
    order_date    TEXT,
    customer_name TEXT,
    customer_city TEXT,
    products      TEXT      -- comma-separated list: a 1NF violation
);
INSERT INTO order_sheet VALUES
    (101, '2024-01-05', 'Ananya', 'Mumbai', 'Laptop, Headphones'),
    (102, '2024-01-12', 'Rahul',  'Delhi',  'Chair, Pen'),
    (103, '2024-02-03', 'Ananya', 'Mumbai', 'Notebook, Pen');
"""


@topic(G, "keys", "Keys: Super, Candidate, Primary, Foreign", "key")
def _():
    yield lead("Keys identify rows and link tables. Interviewers love the vocabulary — and the choice between natural and surrogate keys matters in every real schema.")
    yield table(
        ["Key", "Definition", "In `employees`"],
        ["**Super key**", "Any set of columns that uniquely identifies a row", "`{emp_id}`, `{email}`, `{emp_id, name}`, …"],
        ["**Candidate key**", "A *minimal* super key — remove any column and it is no longer unique", "`{emp_id}`, `{email}` (if always present)"],
        ["**Primary key**", "The candidate key chosen as the row's identity; unique and not null", "`emp_id`"],
        ["**Alternate key**", "A candidate key not chosen as primary (usually enforced with `UNIQUE`)", "`email`"],
        ["**Foreign key**", "Column(s) referencing a key of another (or the same) table", "`dept_id`, `manager_id`"],
        ["**Composite key**", "A key made of two or more columns", "`order_items (order_id, product_id)`"],
        ["**Surrogate key**", "A meaningless generated id (auto-increment, UUID)", "`emp_id`"],
        ["**Natural key**", "A key with business meaning", "email, PAN number, ISBN"],
    )
    yield flow("Super keys", "minimal → Candidate keys", "chosen → Primary key", "others → Alternate keys")
    yield section("Composite primary key", "columns")
    yield sql('''
        -- one row per (order, product): the pair is unique, neither column alone is
        SELECT order_id, product_id, quantity FROM order_items WHERE order_id = 101 ORDER BY product_id;
    ''', out='''
        order_id | product_id | quantity
        ---------+------------+---------
        101      | 1          | 1
        101      | 2          | 1
    ''')
    yield sql('''
        INSERT INTO order_items VALUES (101, 1, 3, 55000);    -- same pair again
    ''', fails=True, err='UNIQUE constraint failed: order_items.order_id, order_items.product_id')
    yield section("Natural vs surrogate keys", "scale")
    yield cards(
        ("Surrogate (`id`)", "Stable (never changes), compact integer joins, no business meaning to leak. Needs a separate `UNIQUE` on the natural key to stop duplicates.", "hash"),
        ("Natural (email, ISBN)", "Meaningful, no extra column, prevents duplicates by itself. But real-world “unique” values change (emails, phone numbers) or turn out not unique, and wide keys make every foreign key wide.", "id-badge"),
    )
    yield good("Common practice: a surrogate primary key **plus** `UNIQUE` constraints on the natural candidate keys. Composite natural keys are fine for pure junction tables (`order_items`).")
    yield dialect('''
        -- UUIDs: globally unique, generated anywhere (useful across services / offline clients)
        CREATE TABLE sessions (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id INT NOT NULL);
        -- prefer time-ordered UUIDv7 for B-tree friendliness (random v4 keys scatter inserts)
    ''', "PostgreSQL")
    yield qa("What is the difference between a primary key and a candidate key?",
             "A candidate key is any minimal set of columns that uniquely identifies rows; a table can have several. The primary key is the one candidate key you choose as the table's official identifier (not null, referenced by foreign keys). The others become alternate keys with `UNIQUE` constraints.")
    yield qa("Can a table have no primary key?",
             "Technically yes in most engines (a *heap*), but it is almost always a mistake: duplicates can't be prevented or targeted, replication and ORMs struggle, and InnoDB creates a hidden one anyway. Every table should have a primary key.")


@topic(G, "er-to-tables", "From ER Diagram to Tables", "schema")
def _():
    yield lead("An Entity–Relationship model describes *things* and *how they relate*; a few mechanical rules turn it into tables, keys and foreign keys.")
    yield section("ER vocabulary", "vocabulary")
    yield table(
        ["ER concept", "Becomes"],
        ["Entity (Customer, Product)", "A table"],
        ["Attribute (name, price)", "A column"],
        ["Identifier", "Primary key"],
        ["Multivalued attribute (phone numbers)", "A separate child table"],
        ["Relationship", "A foreign key, or a junction table"],
        ["Weak entity (Order line depends on Order)", "Table whose key includes the parent's key"],
    )
    yield section("Mapping relationships by cardinality", "arrows-split")
    yield table(
        ["Cardinality", "Example", "Implementation"],
        ["**One-to-one** (1:1)", "Employee — Laptop allocation, User — Profile", "FK with `UNIQUE` on one side (or share the same PK)"],
        ["**One-to-many** (1:N)", "Department — Employees, Customer — Orders", "FK on the **many** side (`employees.dept_id`)"],
        ["**Many-to-many** (M:N)", "Orders — Products, Students — Courses", "**Junction table** with two FKs (`order_items`)"],
        ["Recursive", "Employee — Manager", "FK to the same table (`manager_id`)"],
    )
    yield section("The sample database as an ER model", "sitemap")
    yield ul(
        "Department **1 : N** Employee → `employees.dept_id` (nullable: Dev has none).",
        "Employee **1 : N** Employee (manages) → `employees.manager_id`.",
        "Customer **1 : N** Order → `orders.customer_id` (`NOT NULL`: every order has a customer).",
        "Order **M : N** Product → junction table `order_items (order_id, product_id)` carrying relationship attributes `quantity` and `unit_price`.",
    )
    yield section("Worked example: a course platform", "school")
    yield sql('''
        CREATE TABLE students (
            student_id INTEGER PRIMARY KEY,
            name       TEXT NOT NULL
        );
        CREATE TABLE student_profiles (                        -- 1:1 with students
            student_id INTEGER PRIMARY KEY REFERENCES students(student_id),
            bio        TEXT
        );
        CREATE TABLE instructors (
            instructor_id INTEGER PRIMARY KEY,
            name          TEXT NOT NULL
        );
        CREATE TABLE courses (                                 -- 1:N instructor → courses
            course_id     INTEGER PRIMARY KEY,
            title         TEXT NOT NULL,
            instructor_id INTEGER NOT NULL REFERENCES instructors(instructor_id)
        );
        CREATE TABLE enrollments (                             -- M:N students ↔ courses
            student_id  INTEGER REFERENCES students(student_id),
            course_id   INTEGER REFERENCES courses(course_id),
            enrolled_on TEXT NOT NULL,
            PRIMARY KEY (student_id, course_id)
        );

        INSERT INTO students    VALUES (1, 'Asha'), (2, 'Ravi');
        INSERT INTO instructors VALUES (1, 'Dr. Rao');
        INSERT INTO courses     VALUES (10, 'SQL', 1), (11, 'Python', 1);
        INSERT INTO enrollments VALUES (1, 10, '2024-01-01'), (1, 11, '2024-01-02'), (2, 10, '2024-01-05');

        SELECT s.name AS student, c.title AS course, i.name AS instructor
        FROM enrollments e
        JOIN students s    ON s.student_id = e.student_id
        JOIN courses c     ON c.course_id = e.course_id
        JOIN instructors i ON i.instructor_id = c.instructor_id
        ORDER BY s.name, c.title;
    ''', out='''
        student | course | instructor
        --------+--------+-----------
        Asha    | Python | Dr. Rao
        Asha    | SQL    | Dr. Rao
        Ravi    | SQL    | Dr. Rao
    ''', setup="")
    yield warn("Never model many-to-many with a comma-separated list or with `course1`, `course2`, `course3` columns — you can't index, join, constrain or count them properly. Always use a junction table.")
    yield qa("How do you implement a many-to-many relationship?",
             "With a junction (bridge/associative) table holding a foreign key to each side, whose primary key is usually the pair of FKs (`PRIMARY KEY (student_id, course_id)`). Attributes of the relationship itself (grade, quantity, enrolled date) live in the junction table.")


@topic(G, "normalization", "Normalization (1NF → BCNF)", "layout-rows")
def _():
    yield lead("Normalization organises columns into tables so that **each fact is stored once**. It removes update, insert and delete anomalies caused by redundancy.")
    yield define("Functional dependency (A → B)", "the value of A determines the value of B: `emp_id → name`, `customer_name → customer_city`. Normal forms are rules about which dependencies may exist inside one table.")
    yield section("The problem: a spreadsheet as a table", "table")
    yield sql('''
        SELECT * FROM order_sheet ORDER BY order_id;
    ''', out='''
        order_id | order_date | customer_name | customer_city | products
        ---------+------------+---------------+---------------+-------------------
        101      | 2024-01-05 | Ananya        | Mumbai        | Laptop, Headphones
        102      | 2024-01-12 | Rahul         | Delhi         | Chair, Pen
        103      | 2024-02-03 | Ananya        | Mumbai        | Notebook, Pen
    ''', setup=UNNORMALISED)
    yield table(
        ["Anomaly", "In this sheet"],
        ["**Update**", "Ananya moves city → must update several rows; miss one and data disagrees"],
        ["**Insert**", "Can't record a new customer until they place an order"],
        ["**Delete**", "Delete Rahul's only order → we forget Rahul exists"],
        ["**Query pain**", "“How many orders include a Pen?” needs string matching on `products`"],
    )
    yield section("1NF — atomic values, no repeating groups", "number-1")
    yield p("Every cell holds one value; no lists, no `phone1`/`phone2`/`phone3` columns; each row is unique (has a key).")
    yield sql('''
        -- split the list into one row per product (key: order_id + product)
        WITH RECURSIVE split(order_id, order_date, customer_name, customer_city, product, rest) AS (
            SELECT order_id, order_date, customer_name, customer_city, '', products || ','
            FROM order_sheet
            UNION ALL
            SELECT order_id, order_date, customer_name, customer_city,
                   trim(substr(rest, 1, instr(rest, ',') - 1)),
                   substr(rest, instr(rest, ',') + 1)
            FROM split WHERE rest <> ''
        )
        SELECT order_id, order_date, customer_name, customer_city, product
        FROM split WHERE product <> ''
        ORDER BY order_id, product;
    ''', out='''
        order_id | order_date | customer_name | customer_city | product
        ---------+------------+---------------+---------------+-----------
        101      | 2024-01-05 | Ananya        | Mumbai        | Headphones
        101      | 2024-01-05 | Ananya        | Mumbai        | Laptop
        102      | 2024-01-12 | Rahul         | Delhi         | Chair
        102      | 2024-01-12 | Rahul         | Delhi         | Pen
        103      | 2024-02-03 | Ananya        | Mumbai        | Notebook
        103      | 2024-02-03 | Ananya        | Mumbai        | Pen
    ''', setup=UNNORMALISED)
    yield section("2NF — no partial dependencies", "number-2")
    yield p("Applies when the key is **composite**. Every non-key column must depend on the *whole* key. Here the key is `(order_id, product)`, but `order_date`, `customer_name`, `customer_city` depend on `order_id` alone → move them to an `orders` table. The line table keeps only `(order_id, product, quantity…)`.")
    yield section("3NF — no transitive dependencies", "number-3")
    yield p("Non-key columns must depend on **the key, the whole key, and nothing but the key**. In `orders(order_id, order_date, customer_name, customer_city)`, `order_id → customer_name → customer_city`: city depends on the customer, not the order → move customers to their own table and keep `customer_id` in `orders`.")
    yield flow("order_sheet", "1NF: one product per row", "2NF: orders + order_items", "3NF: customers + orders + order_items + products")
    yield p("That final shape is exactly the sample database: `customers`, `orders`, `order_items`, `products`.")
    yield section("BCNF — every determinant is a candidate key", "letter-b")
    yield p("A stricter 3NF. Classic case: `teaching(student, course, instructor)` where each instructor teaches exactly one course (`instructor → course`) and a student takes a course from one instructor. Key: `(student, course)`. `instructor → course` has a determinant that is not a candidate key → split into `instructor_course(instructor, course)` and `student_instructor(student, instructor)`.")
    yield sql('''
        CREATE TABLE teaching (student TEXT, course TEXT, instructor TEXT, PRIMARY KEY (student, course));
        INSERT INTO teaching VALUES
            ('Asha', 'SQL', 'Dr. Rao'), ('Ravi', 'SQL', 'Dr. Rao'),
            ('Asha', 'Python', 'Dr. Iyer'), ('Meera', 'SQL', 'Dr. Sen');

        -- the fact "Dr. Rao teaches SQL" is stored twice: redundancy BCNF removes
        SELECT instructor, course, COUNT(*) AS times_stored
        FROM teaching GROUP BY instructor, course ORDER BY instructor;
    ''', out='''
        instructor | course | times_stored
        -----------+--------+-------------
        Dr. Iyer   | Python | 1
        Dr. Rao    | SQL    | 2
        Dr. Sen    | SQL    | 1
    ''', setup="")
    yield section("Summary", "list-check")
    yield table(
        ["Form", "Rule", "Removes"],
        ["1NF", "Atomic values, no repeating groups, a key exists", "Lists in cells"],
        ["2NF", "1NF + no non-key column depends on part of a composite key", "Partial dependencies"],
        ["3NF", "2NF + no non-key column depends on another non-key column", "Transitive dependencies"],
        ["BCNF", "For every dependency X → Y, X is a super key", "Remaining anomalies from overlapping candidate keys"],
        ["4NF / 5NF", "No independent multi-valued / join dependencies", "Rare in practice"],
    )
    yield note("Most OLTP schemas aim for **3NF/BCNF**. Going further is rarely needed; going less far should be a deliberate choice (denormalization).")
    yield qa("What is normalization and why is it needed?",
             "The process of structuring tables so each fact is stored once, using normal forms (1NF, 2NF, 3NF, BCNF) based on functional dependencies. It prevents update/insert/delete anomalies, saves space and keeps data consistent; the cost is more tables and joins.")
    yield qa("What is the difference between 3NF and BCNF?",
             "3NF allows a dependency X → Y where Y is part of a candidate key (a *prime* attribute) even if X isn't a key. BCNF forbids it: the left side of every non-trivial dependency must be a super key. They differ only when a table has overlapping composite candidate keys.")


@topic(G, "denormalization", "Denormalization & OLTP vs OLAP", "layout-columns")
def _():
    yield lead("Denormalization deliberately re-introduces redundancy to make reads faster or simpler — trading write complexity and consistency risk for fewer joins.")
    yield section("Common techniques", "tools")
    yield table(
        ["Technique", "Example", "Kept in sync by"],
        ["Stored aggregate", "`customers.lifetime_value`, `posts.comment_count`", "Trigger, application code, batch job"],
        ["Duplicated column", "`orders.customer_city` copied from customers", "Trigger / app"],
        ["Snapshot of a value at a time", "`order_items.unit_price` (price *when bought*)", "Written once — not really redundancy"],
        ["Pre-joined reporting table", "One wide `sales_fact` row per order line", "ETL / materialised view"],
        ["Materialised view", "`monthly_revenue`", "`REFRESH`"],
    )
    yield note("`order_items.unit_price` looks redundant with `products.price` but isn't: it records a *different fact* (the price paid on that day). Order 106 paid 52000 while the list price is 55000.")
    yield sql('''
        SELECT oi.order_id, p.name, p.price AS list_price, oi.unit_price AS paid
        FROM order_items oi JOIN products p ON p.product_id = oi.product_id
        WHERE p.name = 'Laptop'
        ORDER BY oi.order_id;
    ''', out='''
        order_id | name   | list_price | paid
        ---------+--------+------------+------
        101      | Laptop | 55000      | 55000
        106      | Laptop | 55000      | 52000
    ''')
    yield section("OLTP vs OLAP", "chart-dots")
    yield table(
        ["", "OLTP (transactions)", "OLAP (analytics)"],
        ["Workload", "Many small reads/writes by key", "Few huge scans and aggregations"],
        ["Schema", "Normalised (3NF)", "Denormalised **star / snowflake** schema"],
        ["Examples", "PostgreSQL, MySQL, SQL Server for the app", "Snowflake, BigQuery, Redshift, ClickHouse, DuckDB"],
        ["Storage", "Row-oriented", "Column-oriented, compressed"],
        ["Freshness", "Real time", "Loaded by ETL/ELT (minutes–hours)"],
    )
    yield section("Star schema", "star")
    yield p("A central **fact table** of measurable events (`sales_fact`: quantity, amount) with foreign keys to **dimension tables** describing them (`dim_date`, `dim_customer`, `dim_product`). Dimensions are wide and denormalised, so queries need one join per dimension.")
    yield sql('''
        CREATE TABLE sales_fact AS
        SELECT o.order_date AS date_key, o.customer_id, oi.product_id,
               oi.quantity, oi.quantity * oi.unit_price AS amount
        FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.status <> 'cancelled';

        SELECT p.category, c.city, SUM(f.amount) AS revenue
        FROM sales_fact f
        JOIN products  p ON p.product_id  = f.product_id
        JOIN customers c ON c.customer_id = f.customer_id
        GROUP BY p.category, c.city
        ORDER BY revenue DESC;
    ''', out='''
        category    | city      | revenue
        ------------+-----------+--------
        Electronics | Mumbai    | 60000
        Electronics | Delhi     | 52000
        Furniture   | Bengaluru | 12500
        Furniture   | Delhi     | 9000
        Furniture   | Mumbai    | 8000
        Stationery  | Bengaluru | 1200
        Stationery  | Mumbai    | 400
        Stationery  | Delhi     | 200
    ''')
    yield dodont(
        "Normalise first; denormalise a specific hot path after measuring, with a clear owner of the sync logic (trigger, job, or materialised view).",
        "Denormalise “for speed” up front — you pay forever in inconsistent data and complex writes.",
    )
    yield qa("When would you denormalize?",
             "When a read path is hot and joins/aggregations are measurably too slow even with good indexes, for reporting/analytics (star schemas), or to cache expensive aggregates (counters). Accept the cost: extra storage, slower writes and code/triggers to keep copies consistent.")
    yield qa("What is a star schema?",
             "A data-warehouse design with one central fact table (numeric measures + foreign keys) surrounded by denormalised dimension tables (date, customer, product, store). Snowflake schema = the dimensions are further normalised into sub-dimensions.")
