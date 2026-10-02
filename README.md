# VEDA Technology Task 15 — Student Result & Grade Management System

A unique Python web application for managing student details, marks, grades, search, and performance summaries.

## Features
- Add, edit, view and delete student records
- Five-subject marks entry with 0–100 validation
- Automatic total, percentage, grade and remark calculation
- Search by student name, roll number or course
- Dashboard with student count, class average, pass rate and top result
- Student result profile with subject performance bars
- SQLite database created automatically
- JSON summary endpoint at `/api/summary`
- Responsive, non-template visual style named **GradeFlow**

## Grade rules
| Percentage | Grade | Remark |
|---:|:---:|---|
| 90–100 | A+ | Outstanding |
| 80–89 | A | Excellent |
| 70–79 | B+ | Very Good |
| 60–69 | B | Good |
| 50–59 | C | Average |
| 40–49 | D | Pass |
| 0–39 | F | Needs Improvement |

## Run in terminal (Windows)
No external Python package is required. Run: 
```powershell
py -3.12 app.py
```

Open: http://127.0.0.1:8000

The first run automatically creates `students.db` and three sample records.

## GitHub
Suggested repository name:
`veda-task-15-student-result-grade-management-system`

Suggested description:
`VEDA Technology Task 15 - Student Result & Grade Management System built with Python Python standard library and SQLite.`

### Push commands
```powershell
git init
git add .
git commit -m "Complete VEDA Task 15 student result management system"
git branch -M main
git remote add origin https://github.com/manasams081-tech/veda-task-15-student-result-grade-management-system.git
git push -u origin main
```

If Git says `remote origin already exists`, use:
```powershell
git remote set-url origin https://github.com/manasams081-tech/veda-task-15-student-result-grade-management-system.git
git push -u origin main
```

## Important
Do not commit `.venv/`, Python cache files or the local SQLite database if your internship portal only expects source code. A `.gitignore` is included.
