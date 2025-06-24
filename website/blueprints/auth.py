from website.models import db, User

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash("Login Successfull!", "success")

            if user.role == "admin":
                return redirect(url_for("admin.admin_home"))
            elif user.role == "teacher":
                return redirect(url_for("teacher.teacher_home"))
            else:
                return redirect(url_for("student.student_home"))
        else:
            flash("Invalid Username Or Password", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username Already Exsists", "error")
            return render_template("auth/register.html")

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email Already Exsists", "error")
            return render_template("auth/register.html")

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username, email=email, password=hashed_password, role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You Have Been Logged Out", "info")
    return redirect(url_for("auth.login"))
