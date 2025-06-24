from flask import Blueprint, render_template

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/')
def teacher_home():
    return render_template('teacher/teacher.html')
