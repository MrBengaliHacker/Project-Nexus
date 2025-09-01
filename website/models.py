from typing import Any, Dict
from datetime import datetime
from enum import Enum as PyEnum

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import event

db = SQLAlchemy()


# ---------- Mixins / Helpers ----------
class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)


class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, nullable=True, default=None, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()


class RoleEnum(PyEnum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"
    CR = "cr"


# ---------- Association Tables ----------
announcement_tags = db.Table(
    "announcement_tags",
    db.Column("announcement_id", db.Integer, db.ForeignKey("announcements.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)

event_rsvps = db.Table(
    "event_rsvps",
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)

post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


# ---------- Models ----------
class User(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.Enum(RoleEnum, values_callable=lambda x: [e.value for e in RoleEnum]), nullable=False, default=RoleEnum.STUDENT.value, index=True)
    semester = db.Column(db.Integer, nullable=True, index=True)
    bio = db.Column(db.Text, nullable=True)

    avatar_url = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Relationships
    posts = db.relationship("Post", back_populates="author", lazy="dynamic", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", lazy="dynamic", cascade="all, delete-orphan")
    feedbacks = db.relationship("Feedback", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    
    results = db.relationship("Result", back_populates="student", lazy="dynamic", cascade="all, delete-orphan")
    
    notes_uploaded = db.relationship("Resource", back_populates="uploader", lazy="dynamic", cascade="all, delete-orphan")
    
    announcements_posted = db.relationship("Announcement", back_populates="poster", lazy="dynamic", cascade="all, delete-orphan")
    events_posted = db.relationship("Event", back_populates="poster", lazy="dynamic", cascade="all, delete-orphan")

    attendance_records = db.relationship("Attendance", back_populates="student", lazy="dynamic", foreign_keys="Attendance.student_id", cascade="all, delete-orphan")
    attendance_marked = db.relationship("Attendance", back_populates="marker", lazy="dynamic", foreign_keys="Attendance.marked_by")

    events_rsvped = db.relationship("Event", secondary=event_rsvps, back_populates="rsvps", lazy="dynamic")

    likes = db.relationship("Like", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    reports = db.relationship("Report", back_populates="reporter", lazy="dynamic", cascade="all, delete-orphan")

    # Sessions / Tokens
    sessions = db.relationship("SessionToken", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"

    def get_id(self) -> str:
        return str(self.id)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "role": self.role,
            "semester": self.semester,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if include_email:
            data["email"] = self.email
        return data


class SessionToken(db.Model, TimestampMixin):
    __tablename__ = "session_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    user = db.relationship("User", back_populates="sessions", lazy="joined")
    expires_at = db.Column(db.DateTime, nullable=True, index=True)


# ---------- Courses / Enrollment / Assessment ----------
class Course(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    semester = db.Column(db.Integer, nullable=True, index=True)
    credits = db.Column(db.Integer, nullable=True)

    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    instructor = db.relationship("User", backref=db.backref("courses_instructing", lazy="dynamic"), foreign_keys=[instructor_id], lazy="joined")

    enrollments = db.relationship("Enrollment", back_populates="course", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Course {self.code} - {self.title}>"


class Enrollment(db.Model, TimestampMixin):
    __tablename__ = "enrollments"
    
    id = db.Column(db.Integer, primary_key=True)
    
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = db.Column(db.String(20), nullable=False, default="student")  # student / ta / auditor
    
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True, nullable=False)

    course = db.relationship("Course", back_populates="enrollments", lazy="joined")
    user = db.relationship("User", backref=db.backref("enrollments", lazy="dynamic"), lazy="joined")

    __table_args__ = (db.UniqueConstraint("course_id", "user_id", name="_course_user_uc"),)


class Assessment(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # test/quiz/assignment/exam
    
    max_marks = db.Column(db.Float, nullable=False)
    
    weight = db.Column(db.Float, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)

    course = db.relationship("Course", backref=db.backref("assessments", lazy="dynamic"), lazy="joined")


class Assignment(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    due_date = db.Column(db.DateTime, nullable=True)
    max_marks = db.Column(db.Float, nullable=True)

    course = db.relationship("Course", backref=db.backref("assignments", lazy="dynamic"), lazy="joined")


class Submission(db.Model, TimestampMixin):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(512), nullable=True)
    
    content = db.Column(db.Text, nullable=True)
    
    marks = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    graded = db.Column(db.Boolean, default=False, nullable=False)

    assignment = db.relationship("Assignment", backref=db.backref("submissions", lazy="dynamic"), lazy="joined")
    student = db.relationship("User", backref=db.backref("submissions", lazy="dynamic"), lazy="joined")

    __table_args__ = (db.UniqueConstraint("assignment_id", "student_id", name="_assignment_student_uc"),)


# ---------- Results & Academic Records ----------
class Result(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, index=True)

    sgpa = db.Column(db.Float, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    details = db.Column(db.JSON, nullable=True)  # Subject -> {marks, credits, grade}

    student = db.relationship("User", back_populates="results", lazy="joined")

    __table_args__ = (db.UniqueConstraint("student_id", "semester", name="_student_semester_uc"),)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "semester": self.semester,
            "sgpa": self.sgpa,
            "cgpa": self.cgpa,
            "details": self.details,
        }


# ---------- Resources / Files ----------
class Resource(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    file_url = db.Column(db.String(512), nullable=False)
    
    provider = db.Column(db.String(50), nullable=True)  # Synology
    visibility = db.Column(db.String(50), nullable=False, default="public")  # Public / Course / Semester / Role
    
    semester = db.Column(db.Integer, nullable=True, index=True)
    subject = db.Column(db.String(120), nullable=True, index=True)

    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    uploader = db.relationship("User", back_populates="notes_uploaded", lazy="joined")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_url": self.file_url,
            "provider": self.provider,
            "visibility": self.visibility,
            "semester": self.semester,
            "subject": self.subject,
            "uploader_id": self.uploader_id,
        }


# ---------- Announcements ----------
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)


class Announcement(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    category = db.Column(db.String(100), nullable=True, index=True)
    
    file_url = db.Column(db.String(512), nullable=True)
    
    is_pinned = db.Column(db.Boolean, default=False, nullable=False, index=True)
    audience = db.Column(db.JSON, nullable=True)  # {"roles":["student"], "semester":[3]}

    poster = db.relationship("User", back_populates="announcements_posted", lazy="joined")
    tags = db.relationship("Tag", secondary=announcement_tags, backref=db.backref("announcements", lazy="dynamic"), lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "posted_by": self.posted_by,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "category": self.category,
            "file_url": self.file_url,
            "is_pinned": self.is_pinned,
            "audience": self.audience,
        }


# ---------- Events ----------
class Event(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    
    location = db.Column(db.String(255), nullable=True)
    registration_link = db.Column(db.String(512), nullable=True)
    
    file_url = db.Column(db.String(512), nullable=True)
    category = db.Column(db.String(100), nullable=True, index=True)
    
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    capacity = db.Column(db.Integer, nullable=True)

    poster = db.relationship("User", back_populates="events_posted", lazy="joined")
    rsvps = db.relationship("User", secondary=event_rsvps, back_populates="events_rsvped", lazy="dynamic")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location,
            "registration_link": self.registration_link,
            "file_url": self.file_url,
            "category": self.category,
            "posted_by": self.posted_by,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "capacity": self.capacity,
        }


# ---------- Feedback / Complaints ----------
class Feedback(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_anonymous = db.Column(db.Boolean, default=True, nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    status = db.Column(db.String(50), nullable=False, default="open", index=True)
    internal_notes = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="feedbacks", lazy="joined")


# ---------- Feed / Social ----------
class Post(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    
    file_url = db.Column(db.String(512), nullable=True)
    
    is_reported = db.Column(db.Boolean, default=False, nullable=False, index=True)

    author = db.relationship("User", back_populates="posts", lazy="joined")
    tags = db.relationship("Tag", secondary=post_tags, backref=db.backref("posts", lazy="dynamic"), lazy="dynamic")
    
    comments = db.relationship("Comment", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")
    
    likes = db.relationship("Like", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")
    reports = db.relationship("Report", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")


class Comment(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = db.Column(db.Text, nullable=False)

    is_reported = db.Column(db.Boolean, default=False, nullable=False, index=True)

    post = db.relationship("Post", back_populates="comments", lazy="joined")
    author = db.relationship("User", back_populates="comments", lazy="joined")
    reports = db.relationship("Report", back_populates="comment", lazy="dynamic", cascade="all, delete-orphan")


class Like(db.Model, TimestampMixin):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint("user_id", "post_id", name="_user_post_uc"),)

    user = db.relationship("User", back_populates="likes", lazy="joined")
    post = db.relationship("Post", back_populates="likes", lazy="joined")


class Report(db.Model, TimestampMixin):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=True, index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)

    reason = db.Column(db.String(255), nullable=True)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False, index=True)

    reporter = db.relationship("User", back_populates="reports", lazy="joined")

    post = db.relationship("Post", back_populates="reports", lazy="joined")
    comment = db.relationship("Comment", back_populates="reports", lazy="joined")


# ---------- Attendance & Timetable ----------
class Attendance(db.Model, TimestampMixin):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, index=True) # Present / Absent / Excused

    marked_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("User", back_populates="attendance_records", foreign_keys=[student_id], lazy="joined")
    marker = db.relationship("User", back_populates="attendance_marked", foreign_keys=[marked_by], lazy="joined")

    __table_args__ = (db.UniqueConstraint("student_id", "date", name="_student_date_uc"),)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "date": self.date.isoformat() if self.date else None,
            "status": self.status,
            "marked_by": self.marked_by,
            "marked_at": self.marked_at.isoformat() if self.marked_at else None,
        }


class TimetableEntry(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "timetable_entries"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)

    day = db.Column(db.String(20), nullable=False, index=True)
    period = db.Column(db.String(20), nullable=True)

    subject = db.Column(db.String(120), nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    location = db.Column(db.String(120), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "course_id": self.course_id,
            "day": self.day,
            "period": self.period,
            "subject": self.subject,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location,
        }


# ---------- Admin / Jobs / Audit ----------
class Job(db.Model, TimestampMixin):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default="pending", index=True)

    params = db.Column(db.JSON, nullable=True)
    result = db.Column(db.JSON, nullable=True)

    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    action = db.Column(db.String(255), nullable=False, index=True)

    target_type = db.Column(db.String(100), nullable=True)
    target_id = db.Column(db.String(100), nullable=True)

    meta = db.Column(db.JSON, nullable=True)

    actor = db.relationship("User", lazy="joined")


class Setting(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False, index=True)

    value = db.Column(db.JSON, nullable=True)
    description = db.Column(db.String(512), nullable=True)


# ---------- Utilities ----------
@event.listens_for(User, "before_insert")
def _ensure_password_hash(mapper, connection, target: User):
    if target.password_hash and not target.password_hash.startswith("pbkdf2:"):
        target.password_hash = generate_password_hash(target.password_hash)
