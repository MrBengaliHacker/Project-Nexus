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
        query = query.filter_by(semester=semester)

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
        title = request.form["title"]

        description = request.form.get("description")
        semester = request.form["semester"]

        subject = request.form["subject"]
        file = request.files["file"]

        if not file:
            flash("No file selected.", "error")
            return redirect(request.url)

        filename = file.filename
        upload_folder = os.path.join(current_app.root_path, "static", "uploads")

        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        note = Note(
            title=title,
            description=description,
            file_url=f"/static/uploads/{filename}",
            semester=semester,
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
