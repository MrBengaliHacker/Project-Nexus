from flask import Blueprint, render_template

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route('/')
def faculty_home():
    return render_template('faculty/faculty.html')
