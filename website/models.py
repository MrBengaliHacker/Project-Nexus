from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)
    feedbacks = db.relationship("Feedback", backref="user", lazy=True)

    results = db.relationship("Result", backref="student", lazy=True)

    notes_uploaded = db.relationship("Note", backref="uploader", lazy=True)
    announcements = db.relationship("Announcement", backref="poster", lazy=True)

    events = db.relationship("Event", backref="poster", lazy=True)
    attendance = db.relationship(
        "Attendance",
        backref="student",
        lazy=True,
        foreign_keys="[Attendance.student_id]",
    )
    attendance_marked = db.relationship(
        "Attendance", backref="marker", lazy=True, foreign_keys="[Attendance.marked_by]"
    )
    timetable_entries = db.relationship("TimetableEntry", backref="student", lazy=True)

    def get_id(self):
        return str(self.id)


class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    semester = db.Column(db.Integer, nullable=False)

    sgpa = db.Column(db.Float, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)

    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    file_url = db.Column(db.String(255), nullable=False)

    semester = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(120), nullable=False)

    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    location = db.Column(db.String(255), nullable=True)

    registration_link = db.Column(db.String(255), nullable=True)

    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    is_anonymous = db.Column(db.Boolean, default=True)

    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    likes = db.Column(db.Integer, default=0)
    comments = db.relationship("Comment", backref="post", lazy=True)


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    marked_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)


class TimetableEntry(db.Model):
    __tablename__ = "timetable_entries"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    period = db.Column(db.String(20), nullable=False)

    subject = db.Column(db.String(120), nullable=False)
    start_time = db.Column(db.Time, nullable=False)

    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(120), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
