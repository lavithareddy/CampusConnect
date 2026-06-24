import csv
from flask import make_response
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "campusconnect123"

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("campusconnect.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("campusconnect.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"

        conn.close()

        return redirect("/dashboard")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


@app.route("/form", methods=["GET", "POST"])
def form():

    if request.method == "POST":

        request_type = request.form["request_type"]
        description = request.form["description"]

        conn = sqlite3.connect("campusconnect.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO forms(request_type,description,status) VALUES(?,?,?)",
            (request_type, description, "Pending")
        )

        conn.commit()
        conn.close()

        return "Form Submitted Successfully!"

    return render_template("form.html")


@app.route("/applications")
def applications():

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM forms")
    forms = cursor.fetchall()

    conn.close()

    return render_template("applications.html", forms=forms)


@app.route("/notifications")
def notifications():

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT
    )
    """)

    cursor.execute("SELECT * FROM notifications")
    notifications = cursor.fetchall()

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
    )


@app.route("/profile")
def profile():

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name,email FROM students ORDER BY id DESC LIMIT 1"
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        student=student
    )

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            conn = sqlite3.connect("campusconnect.db")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM forms")
            total_forms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM forms WHERE status='Pending'")
            pending_forms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM forms WHERE status='Approved'")
            approved_forms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM forms WHERE status='Rejected'")
            rejected_forms = cursor.fetchone()[0]

            conn.close()

            return render_template(
                "admin_dashboard.html",
                total_students=total_students,
                total_forms=total_forms,
                pending_forms=pending_forms,
                approved_forms=approved_forms,
                rejected_forms=rejected_forms
            )

        return "Invalid Admin Login"

    return render_template("admin_login.html")

@app.route("/admin_notifications", methods=["GET", "POST"])
def admin_notifications():

    if request.method == "POST":

        message = request.form["message"]

        conn = sqlite3.connect("campusconnect.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
        """)

        cursor.execute(
            "INSERT INTO notifications(message) VALUES(?)",
            (message,)
        )

        conn.commit()
        conn.close()

        return "Notification Sent Successfully!"

    return render_template("admin_notifications.html")


@app.route("/allforms")
def allforms():

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM forms")
    forms = cursor.fetchall()

    conn.close()

    return render_template(
        "allforms.html",
        forms=forms
    )


@app.route("/students")
def students():

    search = request.args.get("search", "")

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,name,email FROM students WHERE name LIKE ?",
        ('%' + search + '%',)
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )

@app.route("/approve/<int:id>")
def approve(id):

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE forms SET status='Approved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/allforms")


@app.route("/reject/<int:id>")
def reject(id):

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE forms SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/allforms")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/delete_student/<int:id>")
def delete_student(id):

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/students")

@app.route("/delete_form/<int:id>")
def delete_form(id):

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM forms WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/allforms")

from flask import Response
import csv
import io

@app.route("/download_report")
def download_report():

    conn = sqlite3.connect("campusconnect.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM forms")
    data = cursor.fetchall()

    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Request Type",
        "Description",
        "Status"
    ])

    for row in data:
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=forms_report.csv"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)