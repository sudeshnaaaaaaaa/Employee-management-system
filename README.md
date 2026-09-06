# Employee Management System

A full-stack employee/project management tool built with **Python (Flask)** and **SQLite**, designed to demonstrate core backend fundamentals: relational schema design, CRUD operations, JOIN queries, and aggregate reporting.

## Features

- **Employee CRUD** — add, edit, remove employees, with department assignment
- **Search/filter** — search employees by name, role, or department (parameterized SQL query)
- **Department dashboard** — headcount and average salary per department, computed with `GROUP BY` + `AVG()`
- **Project staffing view** — shows which employees are assigned to which projects and their weekly hours, using a 3-table JOIN (`projects` → `assignments` → `employees`)
- **Foreign key relationships** — employees belong to departments; projects belong to departments; assignments link employees to projects (many-to-many)

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQLite (file-based, zero setup)
- **Frontend:** Server-rendered HTML (Jinja2 templates) + plain CSS, no JS framework

## Database schema

```
departments (id, name, location)
employees   (id, first_name, last_name, email, role, salary, department_id → departments, hire_date)
projects    (id, name, department_id → departments, deadline)
assignments (id, employee_id → employees, project_id → projects, hours_per_week)
```

`assignments` is a join table implementing a many-to-many relationship: one employee can work on multiple projects, and one project can have multiple employees.

## Running it locally

```bash
pip install flask
python database.py   # creates ems.db and seeds sample data (safe to re-run)
python app.py         # starts the server at http://localhost:5000
```

## Talking points for interviews

- **Why SQLite over a full RDBMS?** Zero-config, file-based — appropriate for a demo/prototype scope; the schema (foreign keys, joins) is standard SQL and would port to PostgreSQL/MySQL with no changes to the queries.
- **Where are the JOINs?** `list_employees()` does a `LEFT JOIN` to show department name instead of just an ID; `list_projects()` does a `LEFT JOIN` to departments and a separate `JOIN` through `assignments` to show staffed employees per project; the dashboard does an aggregate `GROUP BY` with `AVG()` and `COUNT()`.
- **Why `LEFT JOIN` instead of `JOIN` in places?** So employees/projects with no department assigned still show up (e.g. `department_id IS NULL`), rather than silently disappearing from the list — a common bug in naive INNER JOIN usage.
- **SQL injection safety** — all queries use parameterized placeholders (`?`), never raw string formatting of user input.
- **What would you add with more time?** Pagination for large employee lists, role-based auth (e.g. manager vs. admin views), and an audit log table for salary changes.
