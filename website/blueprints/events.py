from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from website.models import db, Event, event_rsvps, User
import os
from datetime import datetime

def is_event_poster():
    return current_user.role in ["teacher", "admin", "cr"]

events_bp = Blueprint("events", __name__)

@events_bp.route("/events")
@login_required
def event_list():
    # Filtering and search logic will be added later
    now = datetime.now()
    upcoming_events = Event.query.filter(Event.start_time >= now).order_by(Event.start_time).all()
    past_events = Event.query.filter(Event.start_time < now).order_by(Event.start_time.desc()).all()
    return render_template("events/events.html", upcoming_events=upcoming_events, past_events=past_events)

@events_bp.route("/events/create", methods=["GET", "POST"])
@login_required
def event_create():
    if not is_event_poster():
        flash("You do not have permission to create events.", "error")
        return redirect(url_for("events.event_list"))
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        location = request.form.get("location")
        registration_link = request.form.get("registration_link")
        category = request.form.get("category")
        file = request.files.get("file")
        file_url = None
        if file and file.filename:
            upload_folder = os.path.join(current_app.root_path, "static", "event_files")
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, file.filename))
            file_url = f"/static/event_files/{file.filename}"
        event = Event(
            title=title,
            description=description,
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time),
            location=location,
            registration_link=registration_link,
            category=category,
            file_url=file_url,
            posted_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created!", "success")
        return redirect(url_for("events.event_list"))
    return render_template("events/event_form.html")

@events_bp.route("/events/<int:event_id>")
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    poster = User.query.get(event.posted_by)
    is_registered = False
    if current_user.is_authenticated:
        is_registered = event in current_user.events_rsvped
    return render_template("events/event_details.html", event=event, poster=poster, is_registered=is_registered)

@events_bp.route("/events/<int:event_id>/rsvp", methods=["POST"])
@login_required
def event_rsvp(event_id):
    event = Event.query.get_or_404(event_id)
    if event in current_user.events_rsvped:
        flash("You have already registered for this event.", "info")
    else:
        current_user.events_rsvped.append(event)
        db.session.commit()
        flash("RSVP successful!", "success")
    return redirect(url_for("events.event_details", event_id=event_id))
