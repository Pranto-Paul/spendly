from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # Required for flash messages

# Ensure the database and seed data are ready before routes are used
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        error = None

        if not name:
            error = "Name is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."

        if error is None:
            db = get_db()
            try:
                from werkzeug.security import generate_password_hash
                db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password)),
                )
                db.commit()
                flash("Registration successful! Please sign in.", "success")
                return redirect(url_for("login"))
            except db.IntegrityError:
                error = f"User {email} is already registered."

        flash(error, "error")
        # Preserve form input
        return render_template("register.html", name=name, email=email)

    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/terms")
def terms():
    return render_template("terms.html", now=datetime.now())

@app.route("/privacy")
def privacy():
    return render_template("privacy.html", now=datetime.now())


if __name__ == "__main__":
    app.run(debug=True, port=5001)
