from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user

from website.models import db, Announcement, User

import os

def is_poster():
    return current_user.role in ["teacher", "admin", "cr"]

announcements_bp = Blueprint("announcements", __name__)

@announcements_bp.route("/announcements")
@login_required
def announcement_list():
    category = request.args.get("category")
    query = Announcement.query

    if category:
        query = query.filter_by(category=category)
    
    announcements = query.order_by(Announcement.is_pinned.desc(), Announcement.posted_at.desc()).all()
    return render_template("announcements/announcement_list.html", announcements=announcements)

@announcements_bp.route("/announcements/create", methods=["GET", "POST"])
@login_required
def announcement_create():
    if not is_poster():
        flash("You do not have permission to post announcements.", "error")
        return redirect(url_for("announcements.announcement_list"))
    
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category = request.form.get("category")
        is_pinned = bool(request.form.get("is_pinned"))
        tags_raw = request.form.get("tags", "")
        tag_names = [t.strip() for t in tags_raw.split(",") if t.strip()]
        from website.models import Tag
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        file = request.files.get("file")
        file_url = None
        if file and file.filename:
            upload_folder = os.path.join(current_app.root_path, "static", "announcement_files")
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, file.filename))
            file_url = f"/static/announcement_files/{file.filename}"
        announcement = Announcement(
            title=title,
            content=content,
            posted_by=current_user.id,
            category=category,
            is_pinned=is_pinned,
            file_url=file_url,
            tags=tags,
        )
        db.session.add(announcement)
        db.session.commit()
        flash("Announcement posted!", "success")
        return redirect(url_for("announcements.announcement_list"))
    return render_template("announcements/announcement_form.html")

@announcements_bp.route("/announcements/edit/<int:announcement_id>", methods=["GET", "POST"])
@login_required
def announcement_edit(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)

    if not is_poster() or announcement.posted_by != current_user.id:
        flash("You do not have permission to edit this announcement.", "error")
        return redirect(url_for("announcements.announcement_list"))
    
    if request.method == "POST":
        announcement.title = request.form["title"]
        announcement.content = request.form["content"]
        announcement.category = request.form.get("category")
        announcement.is_pinned = bool(request.form.get("is_pinned"))
        tags_raw = request.form.get("tags", "")
        tag_names = [t.strip() for t in tags_raw.split(",") if t.strip()]
        from website.models import Tag
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        announcement.tags = tags
        file = request.files.get("file")
        if file and file.filename:
            upload_folder = os.path.join(current_app.root_path, "static", "announcement_files")
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, file.filename))
            announcement.file_url = f"/static/announcement_files/{file.filename}"
        db.session.commit()
        flash("Announcement updated!", "success")
        return redirect(url_for("announcements.announcement_list"))
    tags_str = ", ".join([tag.name for tag in announcement.tags])
    return render_template("announcements/announcement_form.html", announcement=announcement, tags_str=tags_str)

@announcements_bp.route("/announcements/delete/<int:announcement_id>", methods=["POST"])
@login_required
def announcement_delete(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    if not is_poster() or announcement.posted_by != current_user.id:
        flash("You do not have permission to delete this announcement.", "error")
        return redirect(url_for("announcements.announcement_list"))
    
    db.session.delete(announcement)
    db.session.commit()
    
    flash("Announcement deleted!", "info")
    return redirect(url_for("announcements.announcement_list"))
