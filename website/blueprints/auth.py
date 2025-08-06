from website.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login Successful!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.admin_home"))
            elif user.role == "teacher":
                return redirect(url_for("teacher.teacher_home"))
            elif user.role == "faculty":
                return redirect(url_for("faculty.faculty_home"))
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
        name = request.form.get(
            "name", username
        )  # Optionally add a name field to the form
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username Already Exists", "error")
            return render_template("auth/register.html")
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email Already Exists", "error")
            return render_template("auth/register.html")
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            name=name,
            email=email,
            password_hash=hashed_password,
            role=role,
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful! Please Login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out", "info")
    return redirect(url_for("auth.login"))
