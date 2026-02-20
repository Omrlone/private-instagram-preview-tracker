from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random

# ==============================
# APP CONFIG
# ==============================

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# ==============================
# DATABASE MODELS
# ==============================

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    page = db.Column(db.String(50))  # portfolio or memories
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    bio = db.Column(db.Text)
    college = db.Column(db.String(200))
    college_desc = db.Column(db.Text)

# ==============================
# INIT
# ==============================

with app.app_context():
    db.create_all()
    if not Profile.query.first():
        profile = Profile(
            name="Omar Bashir Lone",
            bio="Entropy at its peak.",
            college="National Institute Of Technology Srinagar",
            college_desc="Premier engineering institute located in Srinagar, known for academic excellence and innovation"
        )
        db.session.add(profile)
        db.session.commit()

# ==============================
# CAPTCHA
# ==============================

def generate_captcha():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    session['captcha'] = str(a + b)
    return f"{a} + {b} = ?"

# ==============================
# ROUTES
# ==============================

@app.route("/", methods=["GET", "POST"])
def entry():
    if request.method == "POST":
        answer = request.form.get("captcha")
        if answer == session.get("captcha"):
            return redirect(url_for("portfolio"))
        else:
            flash("Wrong CAPTCHA. Try again.")

    question = generate_captcha()
    return render_template("entry.html", question=question)


@app.route("/portfolio")
def portfolio():
    ip = request.remote_addr
    visitor = Visitor(ip=ip)
    db.session.add(visitor)
    db.session.commit()

    profile = Profile.query.first()
    images = Image.query.filter_by(page="portfolio").all()
    total_views = Visitor.query.count()

    return render_template("portfolio.html",
                           profile=profile,
                           images=images,
                           views=total_views)


@app.route("/memories")
def memories():
    images = Image.query.filter_by(page="memories").all()
    return render_template("memories.html", images=images)


# ==============================
# ADMIN DASHBOARD
# ==============================

ADMIN_USERNAME = "omarlone"
ADMIN_PASSWORD = "sogamlolabkupwara"


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")

    return render_template("admin_login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    profile = Profile.query.first()
    images = Image.query.all()
    visitors = Visitor.query.order_by(Visitor.timestamp.desc()).all()
    total_views = Visitor.query.count()

    if request.method == "POST":

        # Update profile
        profile.name = request.form.get("name")
        profile.bio = request.form.get("bio")
        profile.college = request.form.get("college")
        profile.college_desc = request.form.get("college_desc")
        db.session.commit()

        # Upload image
        file = request.files.get("image")
        page = request.form.get("page")

        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_image = Image(filename=filename, page=page)
            db.session.add(new_image)
            db.session.commit()

        flash("Updated successfully")
        return redirect(url_for("dashboard"))

    return render_template("dashboard.html",
                           profile=profile,
                           images=images,
                           visitors=visitors,
                           total_views=total_views)


@app.route("/delete_image/<int:image_id>")
def delete_image(image_id):
    if not session.get("admin"):
        return redirect(url_for("admin"))

    image = Image.query.get_or_404(image_id)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(image)
    db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)