from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote
from pathlib import Path
from html import escape
import json
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "students.db"
HOST, PORT = "127.0.0.1", 8000
SUBJECTS = ["Python", "Database", "Cloud", "Web", "Security"]
GRADE_RULES = [(90, "A+", "Outstanding"), (80, "A", "Excellent"), (70, "B+", "Very Good"), (60, "B", "Good"), (50, "C", "Average"), (40, "D", "Pass"), (0, "F", "Needs Improvement")]


def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
        email TEXT NOT NULL, course TEXT NOT NULL, semester TEXT NOT NULL, marks_json TEXT NOT NULL,
        total INTEGER NOT NULL, percentage REAL NOT NULL, grade TEXT NOT NULL, remark TEXT NOT NULL)""")
    if c.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        demo = [
            ("VTA101", "Ananya Rao", "ananya@example.com", "Computer Science", "6", {"Python":92,"Database":86,"Cloud":81,"Web":95,"Security":88}),
            ("VTA102", "Rahul Kumar", "rahul@example.com", "Information Science", "6", {"Python":76,"Database":82,"Cloud":71,"Web":79,"Security":74}),
            ("VTA103", "Meera Shah", "meera@example.com", "Computer Science", "5", {"Python":64,"Database":69,"Cloud":72,"Web":61,"Security":66}),
        ]
        for record in demo:
            save_student(c, *record)
    c.commit(); c.close()


def calculate(marks):
    values = list(marks.values())
    total = sum(values)
    percentage = round(total / len(values), 2) if values else 0
    for minimum, grade, remark in GRADE_RULES:
        if percentage >= minimum:
            return total, percentage, grade, remark
    return total, percentage, "F", "Needs Improvement"


def save_student(c, roll, name, email, course, sem, marks):
    total, pct, grade, remark = calculate(marks)
    c.execute("INSERT INTO students(roll_no,name,email,course,semester,marks_json,total,percentage,grade,remark) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (roll,name,email,course,sem,json.dumps(marks),total,pct,grade,remark))


def rows(query=""):
    c = db()
    if query:
        q = f"%{query}%"
        data = c.execute("SELECT * FROM students WHERE roll_no LIKE ? OR name LIKE ? OR course LIKE ? ORDER BY id DESC", (q,q,q)).fetchall()
    else:
        data = c.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    c.close()
    return [dict(r, marks=json.loads(r["marks_json"])) for r in data]


def student(student_id):
    c = db(); r = c.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone(); c.close()
    return dict(r, marks=json.loads(r["marks_json"])) if r else None


def css():
    return (BASE_DIR / "static" / "style.css").read_text(encoding="utf-8")


def layout(title, body, message=""):
    alert = f'<div class="alert {message[0]}">{escape(message[1])}</div>' if message else ""
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · GradeFlow</title><style>{css()}</style></head><body><div class="ambient a1"></div><div class="ambient a2"></div>
<header><a class="brand" href="/"><b>GF</b><span>Grade<span>Flow</span></span></a><nav><a href="/">Dashboard</a><a class="navbtn" href="/add">+ Add Result</a></nav></header><main class="shell">{alert}{body}</main><footer>VEDA Technology · Task 15 · Student Result &amp; Grade Management System</footer></body></html>'''


def dashboard(query="", message=None):
    data = rows(query)
    all_data = rows()
    count = len(all_data)
    avg = round(sum(x["percentage"] for x in all_data)/count,1) if count else 0
    pass_rate = round(sum(x["percentage"] >= 40 for x in all_data)/count*100,1) if count else 0
    top = max(all_data, key=lambda x:x["percentage"], default=None)
    table = "".join(f'''<tr><td><a class="student" href="/student/{s['id']}">{escape(s['name'])}</a><small>{escape(s['roll_no'])} · {escape(s['email'])}</small></td><td>{escape(s['course'])}</td><td>Sem {escape(s['semester'])}</td><td>{s['total']}/500</td><td><strong>{s['percentage']}%</strong></td><td><span class="grade">{escape(s['grade'])}</span></td><td><a class="link" href="/edit/{s['id']}">Edit</a></td></tr>''' for s in data)
    body = f'''<section class="hero"><div><div class="eyebrow">STUDENT PERFORMANCE CONSOLE</div><h1>Results that read<br><em>at a glance.</em></h1><p>Manage student records, calculate grades automatically, search results and review academic performance from one clean workspace.</p></div><div class="taskmark"><strong>15</strong><small>VEDA TASK</small></div></section>
<section class="stats"><article><small>STUDENTS</small><b>{count}</b><span>records managed</span></article><article class="dark"><small>CLASS AVERAGE</small><b>{avg}%</b><span>across all subjects</span></article><article><small>PASS RATE</small><b>{pass_rate}%</b><span>40%+ threshold</span></article><article><small>TOP RESULT</small><b>{top['percentage'] if top else '—'}%</b><span>{escape(top['name']) if top else 'No records'}</span></article></section>
<section class="toolbar"><form method="get" class="search"><span>⌕</span><input name="q" value="{escape(query)}" placeholder="Search by name, roll number or course"><button>Search</button>{f'<a href="/">Clear</a>' if query else ''}</form><a class="button primary" href="/add">+ New student</a></section>
<section class="panel"><div class="panelhead"><div><div class="eyebrow">RECORDS</div><h2>Student results</h2></div><span class="pill">{len(data)} shown</span></div>{f'<div class="tablewrap"><table><thead><tr><th>Student</th><th>Course</th><th>Semester</th><th>Total</th><th>Percentage</th><th>Grade</th><th>Action</th></tr></thead><tbody>{table}</tbody></table></div>' if data else '<div class="empty">◎<h3>No matching records</h3><p>Try a different search or add a new student.</p></div>'}</section>
<section class="tips"><div>↗<p><b>Automatic grade calculation</b><br><span>Marks are validated from 0–100 and grades are derived automatically.</span></p></div><div>⌕<p><b>Fast student search</b><br><span>Search name, roll number or course from the dashboard.</span></p></div><div>▦<p><b>Performance summary</b><br><span>Class average, pass rate and top result update automatically.</span></p></div></section>'''
    return layout("Dashboard", body, message)


def form_page(s=None, error=""):
    val = lambda k: escape(str(s.get(k,""))) if s else ""
    marks = s.get("marks",{}) if s else {}
    subject_fields = "".join(f'<label>{sub}<div class="mark"><input type="number" name="{sub}" min="0" max="100" required value="{marks.get(sub,"")}"><b>/100</b></div></label>' for sub in SUBJECTS)
    options = "".join(f'<option value="{i}" {"selected" if val("semester")==str(i) else ""}>Semester {i}</option>' for i in range(1,9))
    body = f'''<section class="formhead"><div class="eyebrow">{'UPDATE RECORD' if s else 'NEW RECORD'}</div><h1>{'Edit student result' if s else 'Add a student result'}</h1><p>Enter student details and five subject marks. The result is calculated automatically.</p></section>
<form method="post" class="formcard"><section><div class="sectiontitle"><i>01</i><h2>Student details</h2></div><div class="grid"><label>Roll number<input name="roll_no" required value="{val('roll_no')}" placeholder="VTA104"></label><label>Full name<input name="name" required value="{val('name')}" placeholder="Student name"></label><label>Email<input type="email" name="email" required value="{val('email')}" placeholder="student@example.com"></label><label>Course<input name="course" required value="{val('course')}" placeholder="Computer Science"></label><label>Semester<select name="semester" required>{options}</select></label></div></section><section><div class="sectiontitle"><i>02</i><h2>Subject marks</h2><p>Enter values from 0 to 100.</p></div><div class="marks">{subject_fields}</div></section><div class="actions"><a class="button ghost" href="/">Cancel</a><button class="button primary">{'Save changes' if s else 'Calculate & Save'} →</button></div></form>'''
    return layout("Edit Result" if s else "Add Result", body, ("error",error) if error else None)


def detail_page(s):
    subjects = "".join(f'<div class="subject"><span>{escape(k)}</span><div class="bar"><i style="width:{v}%"></i></div><b>{v}</b></div>' for k,v in s["marks"].items())
    body = f'''<section class="detailtop"><div><a class="back" href="/">← Back to dashboard</a><div class="eyebrow">RESULT PROFILE · {escape(s['roll_no'])}</div><h1>{escape(s['name'])}</h1><p>{escape(s['course'])} · Semester {escape(s['semester'])} · {escape(s['email'])}</p></div><div class="orb"><b>{escape(s['grade'])}</b><small>{s['percentage']}%</small></div></section><section class="detailgrid"><div class="panel"><div class="panelhead"><div><div class="eyebrow">MARKS BREAKDOWN</div><h2>Subject performance</h2></div></div><div class="subjects">{subjects}</div></div><div class="panel summary"><div class="eyebrow">RESULT SUMMARY</div><div class="big">{s['total']}<small>/500</small></div><p>{s['percentage']}% overall percentage</p><div class="remark">{escape(s['remark'])}</div><a class="button primary full" href="/edit/{s['id']}">Edit result</a><form method="post" action="/delete/{s['id']}" onsubmit="return confirm('Delete this student record?')"><button class="button danger full">Delete record</button></form></div></section>'''
    return layout(s["name"], body)


def parse_form(body):
    data = parse_qs(body, keep_blank_values=True)
    get = lambda k: data.get(k,[""])[0].strip()
    fields = [get(k) for k in ["roll_no","name","email","course","semester"]]
    if not all(fields): raise ValueError("Please complete all student details.")
    marks = {}
    for sub in SUBJECTS:
        raw = get(sub)
        try: value = int(raw)
        except ValueError: raise ValueError(f"Enter valid marks for {sub}.")
        if not 0 <= value <= 100: raise ValueError(f"{sub} marks must be between 0 and 100.")
        marks[sub] = value
    return fields, marks


class Handler(BaseHTTPRequestHandler):
    def send_html(self, content, status=200):
        raw = content.encode("utf-8")
        self.send_response(status); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def redirect(self, location):
        self.send_response(303); self.send_header("Location",location); self.end_headers()
    def do_GET(self):
        p = urlparse(self.path); path = p.path
        if path == "/style.css":
            raw=css().encode(); self.send_response(200); self.send_header("Content-Type","text/css"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path == "/": self.send_html(dashboard(parse_qs(p.query).get("q",[""])[0])); return
        if path == "/add": self.send_html(form_page()); return
        if path.startswith("/edit/"):
            s=student(path.split("/")[-1]); self.send_html(form_page(s) if s else dashboard(message=("error","Student record not found.")), 200); return
        if path.startswith("/student/"):
            s=student(path.split("/")[-1]); self.send_html(detail_page(s) if s else dashboard(message=("error","Student record not found.")), 200); return
        if path == "/api/summary":
            data=rows(); payload={"students":len(data),"average_percentage":round(sum(x["percentage"] for x in data)/len(data),2) if data else 0,"grade_distribution":{g:sum(x["grade"]==g for x in data) for g in sorted(set(x["grade"] for x in data))}}
            raw=json.dumps(payload).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        self.send_html(dashboard(message=("error","Page not found.")),404)
    def do_POST(self):
        p=urlparse(self.path); length=int(self.headers.get("Content-Length",0)); body=self.rfile.read(length).decode()
        if p.path in ("/add",) or p.path.startswith("/edit/"):
            try:
                fields, marks=parse_form(body); roll,name,email,course,sem=fields; total,pct,grade,remark=calculate(marks); c=db()
                if p.path == "/add": c.execute("INSERT INTO students(roll_no,name,email,course,semester,marks_json,total,percentage,grade,remark) VALUES(?,?,?,?,?,?,?,?,?,?)",(roll,name,email,course,sem,json.dumps(marks),total,pct,grade,remark))
                else: c.execute("UPDATE students SET roll_no=?,name=?,email=?,course=?,semester=?,marks_json=?,total=?,percentage=?,grade=?,remark=? WHERE id=?",(roll,name,email,course,sem,json.dumps(marks),total,pct,grade,remark,p.path.split("/")[-1]))
                c.commit(); c.close(); self.redirect("/")
            except sqlite3.IntegrityError: self.send_html(form_page(student(p.path.split("/")[-1]) if p.path.startswith("/edit/") else None,"Roll number already exists."),400)
            except ValueError as e: self.send_html(form_page(student(p.path.split("/")[-1]) if p.path.startswith("/edit/") else None,str(e)),400)
            return
        if p.path.startswith("/delete/"):
            c=db(); c.execute("DELETE FROM students WHERE id=?",(p.path.split("/")[-1],)); c.commit(); c.close(); self.redirect("/"); return
        self.send_html(dashboard(message=("error","Invalid action.")),400)
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format%args}")


if __name__ == "__main__":
    init_db()
    print(f"GradeFlow running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    ThreadingHTTPServer((HOST,PORT), Handler).serve_forever()
