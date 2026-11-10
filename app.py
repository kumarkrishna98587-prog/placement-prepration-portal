import os, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-for-deployment")
DB = os.path.join(os.path.dirname(__file__), "portal.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS quiz_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            score INTEGER, total INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter all details. Password must be at least 6 characters.")
            return redirect(url_for("register"))
        try:
            with db() as con:
                con.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                            (name, email, generate_password_hash(password)))
            flash("Registration successful. Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("This email is already registered.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        results = con.execute(
            "SELECT score,total,created_at FROM quiz_results WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (session["user_id"],)).fetchall()
    return render_template("dashboard.html", results=results)

QUESTIONS = [
    ("Which data structure follows FIFO?", ["Stack", "Queue", "Tree", "Graph"], 1),
    ("Which language runs in a web browser?", ["Python", "C", "JavaScript", "SQL"], 2),
    ("Which SQL command retrieves data?", ["GET", "FETCH", "SELECT", "OPEN"], 2),
    ("What does CPU stand for?", ["Central Processing Unit", "Computer Personal Unit", "Core Program Utility", "Central Print Unit"], 0),
    ("Which HTML tag creates a hyperlink?", ["<link>", "<a>", "<href>", "<url>"], 1),
]

@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "POST":
        score = sum(1 for i, q in enumerate(QUESTIONS)
                    if request.form.get(f"q{i}") == str(q[2]))
        with db() as con:
            con.execute("INSERT INTO quiz_results(user_id,score,total) VALUES(?,?,?)",
                        (session["user_id"], score, len(QUESTIONS)))
        return render_template("quiz_result.html", score=score, total=len(QUESTIONS))
    return render_template("quiz.html", questions=QUESTIONS)

@app.route("/interview")
@login_required
def interview():
    questions = [
        "Tell me about yourself.",
        "What are your strengths as a Computer Science student?",
        "Explain the difference between a list and a tuple in Python.",
        "What is a primary key in DBMS?",
        "Why should we select you for this role?"
    ]
    return render_template("interview.html", questions=questions)

@app.route("/resume", methods=["GET", "POST"])
@login_required
def resume():
    data = None
    if request.method == "POST":
        data = {k: request.form.get(k, "").strip()
                for k in ["name", "email", "phone", "education", "skills", "objective"]}
    return render_template("resume.html", data=data)

@app.route("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
