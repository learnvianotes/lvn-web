"""The shared sample database every SQL topic queries, plus a small `sql()` helper.

SCHEMA is run (hidden) before each query snippet, so every result the reader sees comes from exactly
these rows. The "sample-database" topic shows these statements to the reader — keep them readable.
"""
import textwrap

import kit
from kit import snippet, output

DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    dept_id   INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    location  TEXT NOT NULL
);

CREATE TABLE employees (
    emp_id      INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    email       TEXT    UNIQUE,
    dept_id     INTEGER REFERENCES departments(dept_id),
    manager_id  INTEGER REFERENCES employees(emp_id),
    salary      INTEGER NOT NULL CHECK (salary > 0),
    hire_date   TEXT    NOT NULL
);

CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    city         TEXT,
    signup_date  TEXT NOT NULL
);

CREATE TABLE products (
    product_id  INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       INTEGER NOT NULL CHECK (price >= 0)
);

CREATE TABLE orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date   TEXT    NOT NULL,
    status       TEXT    NOT NULL
                 CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled'))
);

CREATE TABLE order_items (
    order_id    INTEGER NOT NULL REFERENCES orders(order_id),
    product_id  INTEGER NOT NULL REFERENCES products(product_id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
"""

DATA = """
INSERT INTO departments VALUES
    (1, 'Engineering', 'Bengaluru'),
    (2, 'Sales',       'Mumbai'),
    (3, 'HR',          'Hyderabad'),
    (4, 'Marketing',   'Pune');

INSERT INTO employees VALUES
    (1,  'Asha',   'asha@corp.in',   1,    NULL, 150000, '2015-03-01'),
    (2,  'Ravi',   'ravi@corp.in',   1,    1,    120000, '2017-06-15'),
    (3,  'Meera',  'meera@corp.in',  1,    2,     95000, '2019-01-10'),
    (4,  'Karan',  'karan@corp.in',  1,    2,     95000, '2020-08-01'),
    (5,  'Priya',  'priya@corp.in',  2,    1,    110000, '2016-11-20'),
    (6,  'Arjun',  'arjun@corp.in',  2,    5,     70000, '2021-02-14'),
    (7,  'Neha',   NULL,             2,    5,     72000, '2022-05-30'),
    (8,  'Vikram', 'vikram@corp.in', 3,    1,     80000, '2018-09-05'),
    (9,  'Sara',   'sara@corp.in',   3,    8,     85000, '2023-01-09'),
    (10, 'Dev',    NULL,             NULL, 1,     60000, '2024-04-01');

INSERT INTO customers VALUES
    (1, 'Ananya', 'Mumbai',    '2023-11-02'),
    (2, 'Rahul',  'Delhi',     '2023-12-15'),
    (3, 'Sneha',  'Bengaluru', '2024-01-20'),
    (4, 'Imran',  'Delhi',     '2024-02-01'),
    (5, 'Kavya',  NULL,        '2024-03-10');

INSERT INTO products VALUES
    (1, 'Laptop',     'Electronics', 55000),
    (2, 'Headphones', 'Electronics',  2500),
    (3, 'Desk',       'Furniture',    8000),
    (4, 'Chair',      'Furniture',    4500),
    (5, 'Notebook',   'Stationery',     60),
    (6, 'Pen',        'Stationery',     20),
    (7, 'Monitor',    'Electronics', 12000);

INSERT INTO orders VALUES
    (101, 1, '2024-01-05', 'delivered'),
    (102, 2, '2024-01-12', 'delivered'),
    (103, 1, '2024-02-03', 'delivered'),
    (104, 3, '2024-02-14', 'shipped'),
    (105, 4, '2024-02-20', 'cancelled'),
    (106, 2, '2024-03-01', 'delivered'),
    (107, 3, '2024-03-08', 'pending'),
    (108, 1, '2024-03-15', 'shipped');

INSERT INTO order_items VALUES
    (101, 1, 1, 55000), (101, 2, 1, 2500),
    (102, 4, 2, 4500),  (102, 6, 10, 20),
    (103, 5, 5, 60),    (103, 6, 5, 20),
    (104, 3, 1, 8000),  (104, 4, 1, 4500),
    (105, 2, 2, 2500),
    (106, 1, 1, 52000),
    (107, 5, 20, 60),
    (108, 2, 1, 2500),  (108, 3, 1, 8000);
"""

SCHEMA = DDL + DATA


def sql(src, out=None, caption=None, *, setup=SCHEMA, err=None, **kw):
    """A SQL snippet run against the sample database (or a custom `setup`).

    err  — for fails=True examples: the exact SQLite error. It is checked here (the kit only checks that the
           sample fails) and shown to the reader as an "Error" block.
    """
    html = snippet("sql", src, out, caption, setup=setup, **kw)
    if err is not None:
        rc, _, se = kit._sql(textwrap.dedent(src).strip("\n"), textwrap.dedent(setup))
        actual = se.split(": ", 1)[1] if ": " in se else se
        assert rc != 0 and actual == err, f"error mismatch:\n  expected {err!r}\n  actual   {actual!r}\n{src}"
        html += output(err, "Error")
    return html


def dialect(src, caption):
    """Syntax from another engine (MySQL, PostgreSQL, SQL Server, Oracle) — shown, not executed."""
    return snippet("sql", src, caption=caption, run=False)
