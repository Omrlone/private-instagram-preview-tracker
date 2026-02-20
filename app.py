from sqlalchemy import func

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":
        file = request.files["photo"]
        category = request.form["category"]
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            new_photo = Photo(filename=file.filename, category=category)
            db.session.add(new_photo)
            db.session.commit()

    visitors = Visitor.query.order_by(Visitor.timestamp.desc()).all()
    total_views = Visitor.query.count()
    photos = Photo.query.all()

    # 📊 Views per day
    views_per_day = db.session.query(
        func.date(Visitor.timestamp),
        func.count(Visitor.id)
    ).group_by(func.date(Visitor.timestamp)).all()

    dates = [str(v[0]) for v in views_per_day]
    counts = [v[1] for v in views_per_day]

    return render_template(
        "admin_dashboard.html",
        visitors=visitors,
        total_views=total_views,
        photos=photos,
        dates=dates,
        counts=counts
    )