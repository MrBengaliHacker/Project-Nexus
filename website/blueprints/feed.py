from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_required, current_user
from website.models import db, Post, Tag, Comment, Like, Report
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from website.socketio_events import socketio

feed_bp = Blueprint('feed', __name__, template_folder='../templates/feed')

UPLOAD_FOLDER = 'static/uploads/'

# Helper: allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

# Feed main page: list & filter posts
@feed_bp.route('/feed', methods=['GET'])
@login_required
def feed():
    tag = request.args.get('tag')
    search = request.args.get('search')
    query = Post.query.filter_by(is_deleted=False)
    if tag:
        query = query.join(Post.tags).filter(Tag.name == tag)
    if search:
        query = query.filter((Post.title.ilike(f'%{search}%')) | (Post.content.ilike(f'%{search}%')))
    posts = query.order_by(Post.created_at.desc()).all()
    tags = Tag.query.all()
    return render_template('feed/feed.html', posts=posts, tags=tags)

# New post form
@feed_bp.route('/feed/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_ids = request.form.getlist('tags')
        file = request.files.get('file')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        post = Post(title=title, content=content, author_id=current_user.id, file_url=filename)
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        # Emit real-time event
        socketio.emit('broadcast_new_post', {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': current_user.name,
            'created_at': post.created_at.strftime('%d %b %Y %H:%M'),
        })
        flash('Post created!', 'success')
        return redirect(url_for('feed.feed'))
    tags = Tag.query.all()
    return render_template('feed/new_post.html', tags=tags)

# Post detail & comments
@feed_bp.route('/feed/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if post.is_deleted:
        abort(404)
    if request.method == 'POST':
        content = request.form['content']
        comment = Comment(post_id=post.id, author_id=current_user.id, content=content)
        db.session.add(comment)
        db.session.commit()
        # Emit real-time event
        socketio.emit('broadcast_new_comment', {
            'post_id': post.id,
            'comment_id': comment.id,
            'author': current_user.name,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%d %b %Y %H:%M'),
        })
        flash('Comment added!', 'success')
        return redirect(url_for('feed.post_detail', post_id=post.id))
    comments = Comment.query.filter_by(post_id=post.id, is_deleted=False).order_by(Comment.created_at.asc()).all()
    return render_template('feed/post_details.html', post=post, comments=comments)

# Like a post
@feed_bp.route('/feed/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if not existing:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        # Emit real-time event
        socketio.emit('broadcast_like_post', {
            'post_id': post.id,
            'count': len(post.likes),
        })
        return jsonify({'status': 'liked', 'count': len(post.likes)})
    else:
        db.session.delete(existing)
        db.session.commit()
        # Emit real-time event
        socketio.emit('broadcast_like_post', {
            'post_id': post.id,
            'count': len(post.likes),
        })
        return jsonify({'status': 'unliked', 'count': len(post.likes)})

# Report post or comment
@feed_bp.route('/feed/report', methods=['POST'])
@login_required
def report():
    post_id = request.form.get('post_id')
    comment_id = request.form.get('comment_id')
    reason = request.form.get('reason')
    report = Report(reporter_id=current_user.id, post_id=post_id, comment_id=comment_id, reason=reason)
    db.session.add(report)
    db.session.commit()
    # Emit real-time event
    socketio.emit('broadcast_report_content', {
        'report_id': report.id,
        'post_id': report.post_id,
        'comment_id': report.comment_id,
        'reason': report.reason,
        'reporter': current_user.name,
    })
    flash('Reported for review.', 'info')
    return redirect(request.referrer or url_for('feed.feed'))

# Admin: view reported content
@feed_bp.route('/feed/reports')
@login_required
def reports():
    if not current_user.role == 'admin':
        abort(403)
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('feed/reports.html', reports=reports)

# Admin: delete post/comment
@feed_bp.route('/feed/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.role == 'admin' or post.author_id == current_user.id:
        post.is_deleted = True
        db.session.commit()
        flash('Post deleted.', 'info')
    else:
        abort(403)
    return redirect(url_for('feed.feed'))

@feed_bp.route('/feed/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.role == 'admin' or comment.author_id == current_user.id:
        comment.is_deleted = True
        db.session.commit()
        flash('Comment deleted.', 'info')
    else:
        abort(403)
    return redirect(request.referrer or url_for('feed.feed'))
