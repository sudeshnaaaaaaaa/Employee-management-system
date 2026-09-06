"""
database.py
Handles SQLite database setup, schema creation, and seed data
for the Employee Management System.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ems.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed=True):
    """Create tables and optionally seed with sample data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            salary REAL NOT NULL,
            department_id INTEGER,
            hire_date TEXT DEFAULT (date('now')),
            FOREIGN KEY (department_id) REFERENCES departments(id)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER,
            deadline TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            hours_per_week INTEGER DEFAULT 10,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
                ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id)
                ON DELETE CASCADE,
            UNIQUE(employee_id, project_id)
        );
        """
    )
    conn.commit()

    if seed:
        cur.execute("SELECT COUNT(*) FROM departments")
        if cur.fetchone()[0] == 0:
            _seed_data(cur)
            conn.commit()

    conn.close()


def _seed_data(cur):
    departments = [
        ("Engineering", "Pune"),
        ("Quality Assurance", "Pune"),
        ("Human Resources", "Mumbai"),
        ("Sales", "Bengaluru"),
    ]
    cur.executemany("INSERT INTO departments (name, location) VALUES (?, ?)", departments)

    employees = [
        ("Aarav", "Sharma", "aarav.sharma@example.com", "Software Engineer", 650000, 1, "2024-03-11"),
        ("Isha", "Patil", "isha.patil@example.com", "SDET", 700000, 2, "2023-07-01"),
        ("Rohan", "Mehta", "rohan.mehta@example.com", "HR Executive", 500000, 3, "2022-11-20"),
        ("Sneha", "Kulkarni", "sneha.kulkarni@example.com", "Sales Associate", 480000, 4, "2024-01-15"),
        ("Karan", "Verma", "karan.verma@example.com", "Senior Software Engineer", 950000, 1, "2021-06-05"),
        ("Priya", "Nair", "priya.nair@example.com", "QA Lead", 900000, 2, "2020-09-09"),
    ]
    cur.executemany(
        """INSERT INTO employees
           (first_name, last_name, email, role, salary, department_id, hire_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        employees,
    )

    projects = [
        ("Backup Automation Suite", 1, "2026-12-01"),
        ("API Test Framework Revamp", 2, "2026-11-15"),
        ("Campus Hiring Drive", 3, "2026-10-30"),
        ("Q4 Sales Push", 4, "2026-12-31"),
    ]
    cur.executemany(
        "INSERT INTO projects (name, department_id, deadline) VALUES (?, ?, ?)", projects
    )

    assignments = [
        (1, 1, 20), (5, 1, 30), (2, 2, 25), (6, 2, 15), (3, 3, 10), (4, 4, 40),
    ]
    cur.executemany(
        """INSERT INTO assignments (employee_id, project_id, hours_per_week)
           VALUES (?, ?, ?)""",
        assignments,
    )


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
