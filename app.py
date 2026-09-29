"""
app.py
Employee Management System — Flask + SQLite

Demonstrates: CRUD operations, foreign-key relationships,
multi-table JOINs, and basic aggregate queries (COUNT, AVG, SUM).
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

init_db(seed=True)


@app.route("/")
def dashboard():
    conn = get_connection()

    # Aggregate query: headcount + average salary per department
    dept_stats = conn.execute(
        """
        SELECT d.name AS department,
               COUNT(e.id) AS headcount,
               ROUND(AVG(e.salary), 2) AS avg_salary
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id
        GROUP BY d.id
        ORDER BY headcount DESC
        """
    ).fetchall()

    totals = conn.execute(
        "SELECT COUNT(*) AS total_employees, SUM(salary) AS total_payroll FROM employees"
    ).fetchone()

    project_count = conn.execute("SELECT COUNT(*) AS c FROM projects").fetchone()["c"]

    conn.close()
    return render_template(
        "dashboard.html",
        dept_stats=dept_stats,
        totals=totals,
        project_count=project_count,
    )


@app.route("/employees")
def list_employees():
    conn = get_connection()
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "id")
    direction = request.args.get("direction", "desc")

    # Only allow these exact column names, to keep the query safe
    allowed_sorts = {
        "name": "e.first_name",
        "salary": "e.salary",
        "hire_date": "e.hire_date",
    }
    sort_column = allowed_sorts.get(sort, "e.id")
    direction = "ASC" if direction == "asc" else "DESC"

    query = """
        SELECT e.id, e.first_name, e.last_name, e.email, e.role,
               e.salary, e.hire_date, d.name AS department
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
    """
    params = []
    if search:
        query += """ WHERE e.first_name LIKE ? OR e.last_name LIKE ?
                     OR e.role LIKE ? OR d.name LIKE ?"""
        like = f"%{search}%"
        params = [like, like, like, like]
    query += f" ORDER BY {sort_column} {direction}"

    employees = conn.execute(query, params).fetchall()
    conn.close()
    return render_template(
        "employees.html", employees=employees, search=search,
        sort=sort, direction=direction.lower(),
    )


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    conn = get_connection()
    departments = conn.execute("SELECT * FROM departments ORDER BY name").fetchall()

    if request.method == "POST":
        try:
            conn.execute(
                """INSERT INTO employees
                   (first_name, last_name, email, role, salary, department_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    request.form["first_name"].strip(),
                    request.form["last_name"].strip(),
                    request.form["email"].strip(),
                    request.form["role"].strip(),
                    float(request.form["salary"]),
                    request.form.get("department_id") or None,
                ),
            )
            conn.commit()
            flash("Employee added successfully.", "success")
            conn.close()
            return redirect(url_for("list_employees"))
        except Exception as exc:
            flash(f"Could not add employee: {exc}", "error")

    conn.close()
    return render_template("employee_form.html", departments=departments, employee=None)


@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
def edit_employee(emp_id):
    conn = get_connection()
    departments = conn.execute("SELECT * FROM departments ORDER BY name").fetchall()

    if request.method == "POST":
        conn.execute(
            """UPDATE employees
               SET first_name=?, last_name=?, email=?, role=?, salary=?, department_id=?
               WHERE id=?""",
            (
                request.form["first_name"].strip(),
                request.form["last_name"].strip(),
                request.form["email"].strip(),
                request.form["role"].strip(),
                float(request.form["salary"]),
                request.form.get("department_id") or None,
                emp_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Employee updated.", "success")
        return redirect(url_for("list_employees"))

    employee = conn.execute("SELECT * FROM employees WHERE id=?", (emp_id,)).fetchone()
    conn.close()
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("list_employees"))
    return render_template("employee_form.html", departments=departments, employee=employee)


@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
def delete_employee(emp_id):
    conn = get_connection()
    conn.execute("DELETE FROM employees WHERE id=?", (emp_id,))
    conn.commit()
    conn.close()
    flash("Employee removed.", "success")
    return redirect(url_for("list_employees"))


@app.route("/projects")
def list_projects():
    conn = get_connection()

    # Multi-table JOIN: projects -> departments, and projects -> assignments -> employees
    projects = conn.execute(
        """
        SELECT p.id, p.name, p.deadline, d.name AS department
        FROM projects p
        LEFT JOIN departments d ON p.department_id = d.id
        ORDER BY p.deadline
        """
    ).fetchall()

    team_rows = conn.execute(
        """
        SELECT a.project_id, e.first_name, e.last_name, a.hours_per_week
        FROM assignments a
        JOIN employees e ON a.employee_id = e.id
        """
    ).fetchall()

    teams_by_project = {}
    for row in team_rows:
        teams_by_project.setdefault(row["project_id"], []).append(row)

    conn.close()
    return render_template("projects.html", projects=projects, teams_by_project=teams_by_project)


@app.route("/departments")
def list_departments():
    conn = get_connection()
    departments = conn.execute("SELECT * FROM departments ORDER BY name").fetchall()
    conn.close()
    return render_template("departments.html", departments=departments)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
