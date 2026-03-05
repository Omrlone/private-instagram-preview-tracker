from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import random

app = Flask(__name__)

# -------------------------
# Basic Config
# -------------------------
app.config['SECRET_KEY'] = 'super-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# Upload Folder
# -------------------------
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Database Model
# -------------------------
class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.Text)

# -------------------------
# Fake View Counter
# -------------------------
view_count = 0

# -------------------------
# Math CAPTCHA
# -------------------------
def generate_question():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    session['answer'] = a + b
    return f"{a} + {b} = ?"

# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    global view_count
    view_count += 1
    return render_template("portfolio.html", views=view_count)

# -------------------------

@app.route("/captcha", methods=["GET", "POST"])
def captcha():

    if request.method == "POST":

        user_answer = request.form.get("answer")

        if user_answer and int(user_answer) == session.get("answer"):

            name = request.form.get("name")
            message = request.form.get("message")

            visitor = Visitor(name=name, message=message)
            db.session.add(visitor)
            db.session.commit()

            return redirect(url_for("memories"))

    question = generate_question()
    return render_template("captcha.html", question=question)

# -------------------------

@app.route("/memories")
def memories():
    visitors = Visitor.query.all()
    return render_template("memories.html", visitors=visitors)

# -------------------------
# ADMIN LOGIN
# -------------------------

ADMIN_USER = "admin"
ADMIN_PASS = "password123"

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")

# -------------------------

@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    visitors = Visitor.query.all()
    return render_template("admin_dashboard.html", visitors=visitors)

# -------------------------

@app.route("/admin/delete/<int:id>")
def delete_visitor(id):

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    visitor = Visitor.query.get(id)

    if visitor:
        db.session.delete(visitor)
        db.session.commit()

    return redirect(url_for("admin_dashboard"))

# -------------------------

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

# -------------------------
# Create DB
# -------------------------

with app.app_context():
    db.create_all()

# -------------------------

if __name__ == "__main__":
    app.run(debug=True)