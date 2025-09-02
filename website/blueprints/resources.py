from flask_login import login_required, current_user
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app,
)
import os
from datetime import datetime
from werkzeug.utils import secure_filename

from website.models import db, Note

resources_bp = Blueprint("resources", __name__)


def is_faculty_or_admin():
    return current_user.role in ["teacher", "admin"]


@resources_bp.route("/notes", methods=["GET"])
@login_required
def notes_list():
    semester = request.args.get("semester")
    subject = request.args.get("subject")

    query = Note.query

    if semester:
        try:
            sem_int = int(semester)
            query = query.filter_by(semester=sem_int)
        except ValueError:
            flash("Invalid semester filter ignored.", "info")

    if subject:
        query = query.filter_by(subject=subject)

    notes = query.order_by(Note.uploaded_at.desc()).all()
    return render_template("resources/note_list.html", notes=notes)


@resources_bp.route("/notes/upload", methods=["GET", "POST"])
@login_required
def notes_upload():
    if not is_faculty_or_admin():
        flash("You do not have permission to upload notes.", "error")
        return redirect(url_for("resources.notes_list"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip() or None
        semester_raw = request.form.get("semester", "").strip()
        subject = request.form.get("subject", "").strip()
        file = request.files.get("file")

        # Basic validation
        if not title or not semester_raw or not subject:
            flash("Title, semester, and subject are required.", "error")
            return redirect(request.url)

        try:
            semester_val = int(semester_raw)
        except ValueError:
            flash("Semester must be a number.", "error")
            return redirect(request.url)

        if not file or not file.filename:
            flash("No file selected.", "error")
            return redirect(request.url)

        # Allowed file extensions
        allowed_ext = {"pdf", "doc", "docx", "ppt", "pptx", "txt", "jpg", "jpeg", "png"}
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in allowed_ext:
            flash("Unsupported file type.", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        # Avoid collisions: append timestamp if file exists
        base, extension = os.path.splitext(filename)
        candidate = filename
        dest_path = os.path.join(upload_folder, candidate)
        if os.path.exists(dest_path):
            stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            candidate = f"{base}_{stamp}{extension}"
            dest_path = os.path.join(upload_folder, candidate)

        file.save(dest_path)

        note = Note(
            title=title,
            description=description,
            file_url=f"/static/uploads/{candidate}",
            semester=semester_val,
            subject=subject,
            uploaded_by=current_user.id,
        )

        db.session.add(note)
        db.session.commit()

        flash("Note uploaded successfully!", "success")
        return redirect(url_for("resources.notes_list"))

    return render_template("resources/note_upload.html")


@resources_bp.route("/notes/<int:note_id>/download", methods=["GET"])
@login_required
def note_download(note_id):
    note = Note.query.get_or_404(note_id)
    file_path = note.file_url.replace("/static/uploads/", "")

    upload_folder = os.path.join(current_app.root_path, "static", "uploads")

    return send_from_directory(upload_folder, file_path, as_attachment=True)
