from flask import Blueprint, render_template, request, jsonify
from ..models import db, User, Result, Resource, Announcement, Event, TimetableEntry, Attendance, Feedback

student_bp = Blueprint('student', __name__)

# Helper to get current user - placeholder, replace with actual auth
def get_current_user():
    # In real app, get from JWT or session
    return User.query.filter_by(id=1).first()  # Example

@student_bp.route('/')
def student_home():
    return render_template('student/student.html')

@student_bp.route('/profile', methods=['GET'])
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@student_bp.route('/profile', methods=['PUT'])
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'bio' in data:
        user.bio = data['bio']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    db.session.commit()
    return jsonify({"message": "Profile updated"}), 200

@student_bp.route('/change-password', methods=['POST'])
def change_password():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not user.check_password(old_password):
        return jsonify({"error": "Invalid old password"}), 400
    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password changed"}), 200

@student_bp.route('/results', methods=['GET'])
def get_results():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    results = Result.query.filter_by(student_id=user.id).all()
    return jsonify({"results": [r.to_dict() for r in results]}), 200

@student_bp.route('/results/<int:semester>', methods=['GET'])
def get_semester_result(semester):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    result = Result.query.filter_by(student_id=user.id, semester=semester).first()
    if not result:
        return jsonify({"error": "Result not found"}), 404
    return jsonify(result.to_dict()), 200

@student_bp.route('/export/transcript', methods=['POST'])
def export_transcript():
    # Placeholder: Create a background job for export
    return jsonify({"job_id": "123"}), 202

@student_bp.route('/resources', methods=['GET'])
def get_resources():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Filter by visibility: public or matching semester/role
    resources = Resource.query.filter(
        (Resource.visibility == 'public') |
        (Resource.semester == user.semester) |
        (Resource.visibility == user.role.value)
    ).all()
    return jsonify({"resources": [r.to_dict() for r in resources]}), 200

@student_bp.route('/resources/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    # Placeholder: Assuming a favorites table, toggle
    return jsonify({"message": "Favorite toggled"}), 200

@student_bp.route('/announcements', methods=['GET'])
def get_announcements():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Filter by audience
    announcements = Announcement.query.filter(
        (Announcement.audience.is_(None)) |
        (Announcement.audience.contains({"roles": [user.role.value]})) |
        (Announcement.audience.contains({"semester": [user.semester]}))
    ).all()
    return jsonify({"announcements": [a.to_dict() for a in announcements]}), 200

@student_bp.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify({"events": [e.to_dict() for e in events]}), 200

@student_bp.route('/events/<int:id>/register', methods=['POST'])
def register_event(id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    event = Event.query.get(id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    if user in event.rsvps:
        event.rsvps.remove(user)
        message = "Unregistered"
    else:
        event.rsvps.append(user)
        message = "Registered"
    db.session.commit()
    return jsonify({"message": message}), 200

@student_bp.route('/timetable', methods=['GET'])
def get_timetable():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Assuming timetable is per course, but simplified
    timetable = TimetableEntry.query.all()  # Or filter by user's courses
    return jsonify({"timetable": [t.to_dict() for t in timetable]}), 200

@student_bp.route('/attendance/excuse', methods=['POST'])
def submit_excuse():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    date = data.get('date')
    # reason = data.get('reason')  # Removed unused
    # Create attendance record with excused
    attendance = Attendance(student_id=user.id, date=date, status='excused', marked_by=user.id)
    db.session.add(attendance)
    db.session.commit()
    return jsonify({"message": "Excuse submitted"}), 201

@student_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    content = data.get('content')
    is_anonymous = data.get('is_anonymous', True)
    feedback = Feedback(user_id=user.id if not is_anonymous else None, content=content, is_anonymous=is_anonymous)
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback submitted"}), 201
